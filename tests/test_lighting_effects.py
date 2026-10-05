"""
Teste do Entregável 6.4: iluminação 2.5D dinâmica e atmosfera (src/effects/lighting.py).
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_lighting_effects.py
"""
import dataclasses
import math
import os
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import numpy as np
import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src.config import SCREEN_HEIGHT, SCREEN_WIDTH
from src.effects import lighting
from src.effects.lighting import ArenaLighting
from src.isometric.camera import Camera
from src.world.arenas import ARENA_SPECS, arena_ids, create_arena

SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
KNOWN_KINDS = {"fogbank", "fireflies", "dust", "embers", "smoke", "incense", "steam", "fog", "mist", "sunbeams", "spotlight",
               "fireworks", "rain"}


def _setup(arena_id, azimuth=45.0):
    arena = create_arena(arena_id)
    camera = arena.attach_camera(Camera(11.0, 11.0))
    camera.set_azimuth(math.radians(azimuth))
    return arena, ArenaLighting(arena), camera


def _flat(value=128):
    surf = pygame.Surface(SIZE)
    surf.fill((value, value, value))
    return surf


def _lum(surface, center, half=30):
    x, y = center
    rect = pygame.Rect(x - half, y - half, half * 2, half * 2).clip(surface.get_rect())
    arr = pygame.surfarray.array3d(surface.subsurface(rect)).astype(float)
    return float(arr.mean())


def _warm_up(lf, camera, seconds=1.0, start=0.0):
    t = start
    surf = _flat(0)
    for _ in range(int(seconds * 60)):
        t += 1 / 60
        lf.render(surf, camera, t)
    return t


def test_every_arena_builds_and_renders():
    for arena_id in arena_ids():
        for az in (0, 45, 135):
            arena, lf, camera = _setup(arena_id, az)
            kinds = {e.kind for e in arena.lighting.atmosphere}
            assert kinds <= KNOWN_KINDS, f"{arena_id}: efeito sem renderizador {kinds - KNOWN_KINDS}"
            assert len(lf.effects) == sum(1 for e in arena.lighting.atmosphere if e.kind != "fogbank"), arena_id
            surf = _flat()
            lf.render(surf, camera, 1.0)
        camera.zoom = 1.35  # zoom dramático do choque de espadas
        lf.render(_flat(), camera, 1.1)
    print("  [OK] As 12 arenas montam e renderizam a iluminação em 0/45/135 e com zoom.", flush=True)


def test_lights_glow_and_flicker():
    arena, lf, camera = _setup("kyoto")
    light = arena.lighting.lights[0]
    center = camera.apply(light.x, light.y, 0.0)
    far = camera.apply(light.x + 9.0, light.y, 0.0)

    lit = _flat()
    lf.render(lit, camera, 1.0)
    bare = ArenaLighting(arena)
    bare.env = dataclasses.replace(arena.lighting, lights=())
    dark = _flat()
    bare.render(dark, camera, 1.0)
    assert _lum(lit, center) > _lum(dark, center) + 8, "a luz acende a poça no chão"
    assert _lum(lit, center) > _lum(lit, far), "o brilho cai com a distância"

    samples = []
    for k in range(10):
        s = _flat()
        lf.render(s, camera, 1.0 + k * 0.037)
        samples.append(_lum(s, center, 12))
    assert max(samples) - min(samples) > 1.0, "a chama cintila"

    print("  [OK] Luzes acendem o chão, o brilho cai com a distância e a chama cintila.", flush=True)


def test_ambient_grade_and_vignette():
    for arena_id in arena_ids():
        arena, lf, camera = _setup(arena_id)
        env = arena.lighting
        surf = _flat()
        lf.effects, lf.env = [], dataclasses.replace(env, lights=())
        lf.render(surf, camera, 1.0)
        center = _lum(surf, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 40)
        corner = _lum(surf, (40, 40), 30)
        if env.vignette >= 0.2:
            assert corner < center * 0.9, f"{arena_id}: vinheta escurece os cantos"
        if env.ambient_strength >= 0.9:
            assert center > 128 * 0.9, f"{arena_id}: cena de dia quase sem gradação"
        if env.ambient_strength <= 0.45:
            assert center < 128 * 0.95, f"{arena_id}: cena noturna mais escura no centro"
    print("  [OK] Gradação ambiente e vinheta: dia quase neutro, noite mais escura, cantos escurecidos.", flush=True)


def test_atmosphere_effects_draw_and_stay_bounded():
    seen = set()
    for arena_id in arena_ids():
        arena = create_arena(arena_id)
        camera = arena.attach_camera(Camera(11.0, 11.0))
        for effect_spec in arena.lighting.atmosphere:
            if effect_spec.kind == "fogbank":  # desenhado pelo FogVolume (test_fog_volume.py)
                continue
            lf = ArenaLighting(arena)
            lf.env = dataclasses.replace(arena.lighting, lights=(), vignette=0.0, ambient_strength=1.0)
            lf.effects = [e for e in lf.effects if type(e) is type(ArenaLighting._make_effect(arena, effect_spec))][:1]
            assert lf.effects, (arena_id, effect_spec.kind)
            t, painted = 0.0, 0
            for _ in range(240):
                t += 1 / 60
                surf = _flat(0)
                lf.render(surf, camera, t)
                painted = max(painted, int((pygame.surfarray.array3d(surf).sum(axis=2) > 0).sum()))
            assert painted > 0, f"{arena_id}: {effect_spec.kind} não desenhou nada"
            seen.add(effect_spec.kind)
        # sem estourar memória em partida longa
        lf = ArenaLighting(arena)
        t = 0.0
        surf = _flat(0)
        for _ in range(60 * 30):
            t += 1 / 60
            lf.render(surf, camera, t)
        assert lf.particle_count() < 260, f"{arena_id}: {lf.particle_count()} partículas"
    assert seen == KNOWN_KINDS - {"fogbank"}, KNOWN_KINDS - seen
    print(f"  [OK] Todos os {len(seen)} tipos de atmosfera desenham e o total de partículas fica limitado.", flush=True)


def test_lightning_and_dynamic_lights():
    arena, lf, camera = _setup("pirate_deck")
    rain = lf.rain
    assert rain is not None
    base = _flat(40)
    lf_off = ArenaLighting(arena)
    lf_off.env = dataclasses.replace(arena.lighting, lights=(), vignette=0.0, ambient_strength=1.0)
    lf_off.effects = [e for e in lf_off.effects if isinstance(e, lighting._Rain)]
    quiet = base.copy()
    lf_off.render(quiet, camera, 1.0)
    lf_off.rain.force_lightning()
    flash = base.copy()
    lf_off.render(flash, camera, 1.0)
    assert _lum(flash, (640, 360), 200) > _lum(quiet, (640, 360), 200) + 20, "o relâmpago clareia a cena"
    assert lf_off.rain.flash_level() > 0.5
    lf_off.rain.flash_age = 5.0
    assert lf_off.rain.flash_level() == 0.0

    # os relâmpagos acontecem sozinhos em intervalo de poucos segundos
    t, flashes, was = 0.0, 0, False
    for _ in range(60 * 25):
        t += 1 / 60
        rain.update(1 / 60, t)
        now = rain.flash_level() > 0.5
        flashes += int(now and not was)
        was = now
    assert flashes >= 2, flashes

    # morteiros avisam e explodem com luz colorida
    arena, lf, camera = _setup("mist_temple")
    hazard = arena.hazards[0]
    lf.effects = []
    lf.env = dataclasses.replace(arena.lighting, lights=(), vignette=0.0, ambient_strength=1.0)
    idle = _flat(30)
    lf.render(idle, camera, 1.0)
    hazard.circles = [(11.0, 11.0, 1.5)]
    hazard.phase = "active"
    lit = _flat(30)
    lf.render(lit, camera, 1.0)
    spot = camera.apply(11.0, 11.0, 0.0)
    assert _lum(lit, spot, 20) > _lum(idle, spot, 20) + 10, "a explosão do morteiro ilumina o círculo"

    # barril aceso
    arena, lf, camera = _setup("nagashino_field")
    lf.effects = []
    lf.env = dataclasses.replace(arena.lighting, lights=(), vignette=0.0, ambient_strength=1.0)
    barrel = arena.interactives[0]
    cx, cy = barrel.center
    before = _flat(30)
    lf.render(before, camera, 1.0)
    barrel.state = "lit"
    after = _flat(30)
    lf.render(after, camera, 1.0)
    spot = camera.apply(cx, cy, 0.0)
    assert _lum(after, spot, 20) > _lum(before, spot, 20) + 8, "o barril aceso brilha"
    print("  [OK] Relâmpagos clareiam a cena em intervalos, morteiros e barris acesos iluminam o chão.", flush=True)


def test_performance_budget():
    worst = ("", 0.0)
    for arena_id in arena_ids():
        arena, lf, camera = _setup(arena_id)
        surf = _flat(90)
        t = _warm_up(lf, camera, 2.0)
        start = time.perf_counter()
        frames = 120
        for _ in range(frames):
            t += 1 / 60
            lf.render(surf, camera, t)
        ms = (time.perf_counter() - start) * 1000.0 / frames
        if ms > worst[1]:
            worst = (arena_id, ms)
        assert ms < 9.0, f"{arena_id}: {ms:.1f} ms por quadro"
    print(f"  [OK] Custo por quadro a 1280x720: pior caso {worst[1]:.1f} ms ({worst[0]}).", flush=True)


def test_dynamic_lighting_and_particles():
    test_every_arena_builds_and_renders()
    test_lights_glow_and_flicker()
    test_ambient_grade_and_vignette()
    test_atmosphere_effects_draw_and_stay_bounded()
    test_lightning_and_dynamic_lights()
    test_performance_budget()


if __name__ == "__main__":
    test_dynamic_lighting_and_particles()
    print("=== TESTE 6.4 CONCLUÍDO ===", flush=True)
