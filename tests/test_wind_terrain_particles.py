"""
Teste da 6.5.1: vento compartilhado e partículas de terreno com física (src/effects/terrain_particles.py).
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_wind_terrain_particles.py
"""
import dataclasses
import math
import os
import random
import sys
import time
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src.effects import particles as particles_module
from src.effects import terrain_particles as tp
from src.effects.particles import AmbientLeafParticle, SmokeParticle
from src.isometric.camera import Camera
from src.world.arena_generator import ArenaMap, WindSpec
from src.world.arenas import ARENA_SPECS, create_arena

DT = 1 / 60


def _find(arena, surface):
    """Centro de um tile do material pedido, longe de buracos e sólidos."""
    solids = list(arena.rocks) + list(arena.buildings)
    for y in range(2, arena.rows - 2):
        for x in range(2, arena.cols - 2):
            cx, cy = x + 0.5, y + 0.5
            if arena.surface_at(cx, cy) == surface and arena.pit_at(cx, cy) is None \
                    and not any(r.check_collision(cx, cy, 0.8)[0] for r in solids):
                return cx, cy
    raise AssertionError(f"{arena.spec.id}: sem tile {surface}")


def _fighter(x, y):
    return SimpleNamespace(wx=x, wy=y, wz=0.0, is_alive=True, state="WALK")


def _run_speed(arena, surface, speed, seconds=0.5):
    """Move um lutador falso em linha reta na velocidade dada e devolve (partículas emitidas, velocidade média de saída)."""
    random.seed(3)
    fx = tp.TerrainFX()
    x, y = _find(arena, surface)
    f = _fighter(x - 1.0, y)
    fx.step(f, arena, DT)
    first = len(fx.particles)
    speeds = []
    for _ in range(int(seconds / DT)):
        f.wx += speed * DT
        before = len(fx.particles)
        fx.step(f, arena, DT)
        speeds.extend(math.hypot(p.vx, p.vy) for p in fx.particles[before:] if p.kind not in ("ring", "puff"))
    return fx.spawned - first, (sum(speeds) / len(speeds) if speeds else 0.0)


def test_wind_is_shared_and_gusty():
    pirate, kabuki = create_arena("pirate_deck"), create_arena("kabuki_stage")
    spec = pirate.spec.wind
    mags = []
    for k in range(200):
        vx, vy = pirate.wind_at(11, 11, k * 0.1)
        assert vx * spec.dir_x + vy * spec.dir_y >= 0.0, "o vento sopra a favor da direção do spec"
        mags.append(math.hypot(vx, vy))
    assert max(mags) - min(mags) > 0.5, "rajadas variam no tempo"
    assert abs(pirate.wind_at(3, 3, 2.0)[0] - pirate.wind_at(18, 18, 2.0)[0]) > 1e-6, "rajadas variam no espaço"
    calm = ArenaMap(dataclasses.replace(kabuki.spec, wind=WindSpec(1.0, 0.0, 0.5, 0.0)))
    assert len({round(calm.wind_at(5, 5, t / 3.0)[0], 6) for t in range(30)}) == 1, "gust 0 = vento constante"
    assert max(math.hypot(*kabuki.wind_at(11, 11, t * 0.3)) for t in range(40)) < 0.2, "palco fechado quase sem vento"
    assert max(math.hypot(*pirate.wind_at(11, 11, t * 0.3)) for t in range(40)) > 1.5, "convés na tempestade com vento forte"
    print("  [OK] Vento por arena: direção e força do spec, rajadas no tempo e no espaço, constante com gust 0.", flush=True)


def test_every_tile_has_a_known_surface():
    seen = set()
    for arena_id, spec in ARENA_SPECS.items():
        for tile, style in spec.tile_styles.items():
            if style.kind in ("anchor", "void"):
                continue
            kind = "water" if style.kind == "water" else style.surface
            assert kind in tp.SURFACES, f"{arena_id}: tile {tile} com material {kind}"
            seen.add(kind)
    assert {"grass", "sand", "gravel", "mud", "water", "wood", "stone", "marble", "dirt", "wet_sand", "roof"} <= seen, seen
    assert create_arena("bamboo").surface_at(11.5, 3.5) in ("grass", "dirt", "water", "gravel"), "consulta por coordenada"
    assert create_arena("bamboo").surface_at(-3, 4) is None, "fora da grade"
    print(f"  [OK] Todos os tiles das 12 arenas têm material conhecido ({len(seen)} materiais).", flush=True)


def test_particle_physics_per_material():
    random.seed(5)
    wind = (0.0, 0.0)
    bounce = {}
    for name in ("gravel", "mud"):
        preset = tp.SURFACES[name]
        p = tp.TerrainParticle(preset.kind, preset, 5, 5, 0.04, 0.8, 0.0, 3.0, (120, 110, 100), 2, 0.9)
        peaks, last_vz, alive, t = [], p.vz, True, 0.0
        while alive and t < 3.0:
            alive = p.update(DT, wind)
            t += DT
            if last_vz > 0 >= p.vz:
                peaks.append(p.wz)
            last_vz = p.vz
        assert not alive and t < 2.0, f"{name}: precisa assentar e sumir (levou {t:.2f}s)"
        bounce[name] = peaks
    assert len(bounce["gravel"]) >= 2, "pedrinha quica mais de uma vez"
    assert len(bounce["mud"]) <= 1, "lama não quica"
    # arrasto do vento: lâmina leve anda a favor do vento; sem vento quase não anda
    blade = tp.SURFACES["grass"]
    drift = []
    for w in ((0.0, 0.0), (2.0, 0.0)):
        p = tp.TerrainParticle("blade", blade, 5, 5, 0.04, 0.0, 0.0, 1.5, (90, 160, 70), 3, 1.0)
        for _ in range(30):
            p.update(DT, w)
        drift.append(p.wx - 5)
    assert drift[1] > drift[0] + 0.15, drift
    print("  [OK] Física: gravidade, quique por material, atrito, vento e sumiço depois de assentar.", flush=True)


def test_particles_react_to_speed_and_surface():
    expected = {"bamboo": ("grass", "blade"), "ganryu_island": ("gravel", "pebble"), "nagashino_field": ("mud", "clump"),
                "shrine": ("sand", "grain"), "pirate_deck": ("wood", "puff")}
    arenas = {"bamboo": create_arena("bamboo"), "ganryu_island": create_arena("ganryu_island"),
              "nagashino_field": create_arena("nagashino_field"), "shrine": create_arena("mountain_shrine"),
              "pirate_deck": create_arena("pirate_deck")}
    for key, (surface, kind) in expected.items():
        arena = arenas[key]
        counts = {s: _run_speed(arena, surface, s, 0.15 if kind == "puff" else 0.5) for s in (4.0, 10.0, 22.0)}
        if surface == "wood":  # só poeira, e só em eventos rápidos
            assert counts[4.0][0] == 0, "andar na madeira não levanta nada"
            assert counts[22.0][0] > counts[10.0][0] > 0, counts
            continue
        assert counts[4.0][0] > 0, f"{surface}: andar levanta partículas"
        assert counts[10.0][0] > counts[4.0][0] and counts[22.0][0] > counts[10.0][0], (surface, counts)
        assert counts[22.0][1] > counts[4.0][1], f"{surface}: velocidade de saída cresce com a do evento"
    water = create_arena("ganryu_island")
    assert _run_speed(water, "water", 4.0)[0] > 0, "andar na água espirra"
    fx = tp.TerrainFX()
    x, y = _find(arenas["bamboo"], "grass")
    f = _fighter(x - 0.5, y)
    fx.step(f, arenas["bamboo"], DT)
    f.wx += 12.0 * DT
    fx.step(f, arenas["bamboo"], DT)
    assert all(p.kind == "blade" for p in fx.particles if p.kind != "ring"), "grama solta lâminas"
    print("  [OK] As partículas escolhem o tipo pelo material e crescem em quantidade e velocidade com a do evento.", flush=True)


def test_events_pouso_freada_teleporte():
    random.seed(9)
    arena = create_arena("bamboo")
    x, y = _find(arena, "grass")
    fx = tp.TerrainFX()
    f = _fighter(x, y)
    fx.step(f, arena, DT)
    f.wx += 6.0  # spawn ou introdução: salto de posição não emite
    fx.step(f, arena, DT)
    assert fx.spawned == 0, "teleporte não emite"
    f.wz = 1.2
    fx.step(f, arena, DT)
    assert fx.spawned == 0, "no ar não emite"
    f.wz = 0.0
    fx.step(f, arena, DT)
    assert fx.spawned > 0, "pouso levanta poeira"
    dead = tp.TerrainFX()
    corpse = _fighter(x, y)
    corpse.is_alive = False
    dead.step(corpse, arena, DT)
    corpse.wx += 0.2
    dead.step(corpse, arena, DT)
    assert dead.spawned == 0
    skid = tp.TerrainFX()
    g = _fighter(x - 3.0, y)
    skid.step(g, arena, DT)
    for _ in range(10):
        g.wx += 10.0 * DT
        skid.step(g, arena, DT)
    before = skid.spawned
    skid.step(g, arena, DT)  # parou de repente
    assert skid.spawned > before, "freada levanta partículas"
    print("  [OK] Pouso e freada emitem; teleporte, no ar e morto não.", flush=True)


def test_nothing_stays_and_caps_hold():
    random.seed(11)
    arena = create_arena("shrine" if "shrine" in ARENA_SPECS else "mountain_shrine")
    x, y = _find(arena, "sand")
    fx = tp.TerrainFX()
    f = _fighter(x - 2.0, y)
    fx.step(f, arena, DT)
    peak = 0
    for _ in range(300):  # dash contínuo: tenta estourar o pool
        f.wx += 22.0 * DT
        if f.wx > x + 2.0:
            f.wx = x - 2.0
        fx.step(f, arena, DT)
        fx.update(DT, arena, 0.0)
        peak = max(peak, len(fx.particles))
        assert sum(1 for p in fx.particles if p.kind == "puff") <= tp.MAX_PUFFS
    assert 0 < peak <= tp.MAX_PARTICLES, peak
    for k in range(240):  # sem lutador: tudo some sozinho
        fx.update(DT, arena, 5.0 + k * DT)
    assert not fx.particles, f"ficaram {len(fx.particles)} partículas paradas"
    print(f"  [OK] Pool limitado (pico {peak}) e nada fica no cenário depois que assenta.", flush=True)


def test_smoke_and_leaves_follow_wind():
    random.seed(2)
    try:
        particles_module.set_wind_source(None)
        calm = SmokeParticle(5, 5, lifetime=1.0)
        calm.vx = calm.vy = 0.0
        particles_module.set_wind_source(lambda x, y: (2.0, 0.0))
        windy = SmokeParticle(5, 5, lifetime=1.0)
        windy.vx = windy.vy = 0.0
        particles_module.set_wind_source(None)
        for _ in range(30):
            calm.update(DT)
        particles_module.set_wind_source(lambda x, y: (2.0, 0.0))
        for _ in range(30):
            windy.update(DT)
        assert windy.wx - 5 > calm.wx - 5 + 0.2, "a fumaça anda com o vento"
    finally:
        particles_module.set_wind_source(None)
    leaf = AmbientLeafParticle(22, 22, 0.25)
    leaf.wx, leaf.wy, leaf.wz = 0.2, 5.0, 4.0
    for _ in range(60):
        leaf.update(DT, (-6.0, 0.0))
    assert 0 <= leaf.wx <= 22, "folha empurrada para fora da arena recomeça do alto"
    print("  [OK] Fumaça e folhas seguem o vento da arena; folha fora do mapa recomeça.", flush=True)


def test_render_and_budget():
    random.seed(4)
    arenas = {s: create_arena(a) for s, a in (("grass", "bamboo"), ("gravel", "ganryu_island"), ("mud", "nagashino_field"),
                                              ("sand", "mountain_shrine"), ("water", "ganryu_island"), ("wood", "pirate_deck"))}
    surf = pygame.Surface((1280, 720))
    for az in (0, 45, 135):
        cam = Camera(11.0, 11.0)
        cam.set_azimuth(math.radians(az))
        fx = tp.TerrainFX()
        for surface, arena in arenas.items():
            x, y = _find(arena, surface)
            f = _fighter(x - 1.0, y)
            fx.step(f, arena, DT)
            for _ in range(40):
                f.wx += 10.0 * DT
                fx.step(f, arena, DT)
                fx.update(DT, arena, 1.0)
            for p in fx.particles:
                p.render(surf, cam)
    arena = arenas["grass"]
    fx = tp.TerrainFX()
    x, y = _find(arena, "grass")
    cam = Camera(x, y)
    f = _fighter(x - 1.5, y)
    fx.step(f, arena, DT)
    total, frames = 0.0, 0
    for k in range(240):
        f.wx += 10.0 * DT
        if f.wx > x + 1.5:
            f.wx = x - 1.5
        start = time.perf_counter()
        fx.step(f, arena, DT)
        fx.update(DT, arena, k * DT)
        for p in fx.particles:
            p.render(surf, cam)
        if k >= 60:
            total += time.perf_counter() - start
            frames += 1
    ms = total * 1000.0 / frames
    assert ms < 2.5, f"{ms:.2f} ms por quadro"
    print(f"  [OK] Render nos três azimutes; custo médio {ms:.2f} ms por quadro com esquiva contínua.", flush=True)


def test_wind_and_terrain_particles():
    test_wind_is_shared_and_gusty()
    test_every_tile_has_a_known_surface()
    test_particle_physics_per_material()
    test_particles_react_to_speed_and_surface()
    test_events_pouso_freada_teleporte()
    test_nothing_stays_and_caps_hold()
    test_smoke_and_leaves_follow_wind()
    test_render_and_budget()


if __name__ == "__main__":
    test_wind_and_terrain_particles()
    print("=== TESTE 6.5.1 CONCLUÍDO ===", flush=True)
