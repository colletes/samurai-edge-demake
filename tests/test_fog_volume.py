"""
Teste da 6.5.2: névoa volumétrica do Templo na Névoa e rastro de névoa da Kasumi (src/effects/fog.py).
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_fog_volume.py
"""
import math
import os
import random
import statistics
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

from src.config import CHAR_GRAY, CHAR_KENSHIN
from src.effects import fog as fog_module
from src.effects.fog import FogVolume
from src.entities.ai_controller import SamuraiAI
from src.isometric.camera import Camera
from src.world.arenas import arena_ids, create_arena
import tests.test_arena_engine as eng

DT = 1 / 60


def _volume(arena_id="mist_temple"):
    arena = create_arena(arena_id)
    fog = arena.fog = FogVolume(arena)
    return arena, fog


def _run(fog, seconds, t0=0.0):
    t = t0
    for _ in range(int(seconds / DT)):
        t += DT
        fog.update(DT, t)
    return t


def test_bank_only_in_the_temple_and_density_is_bounded():
    for arena_id in arena_ids():
        arena, fog = _volume(arena_id)
        assert fog.has_bank == (arena_id == "mist_temple"), arena_id
        assert fog.trail == [] and arena.fog is fog
    arena, fog = _volume()
    assert len(fog.bank) >= 25
    assert {round(p.z, 2) for p in fog.bank} == {0.15, 0.8, 1.7}, "três camadas de altura"
    values = [fog.bank_density_at(x, y) for x in range(0, 22, 2) for y in range(0, 22, 2)]
    assert all(0.0 <= v <= 1.0 for v in values)
    assert max(values) > 0.3 and min(values) < max(values) - 0.2, "o banco tem manchas densas e vãos"
    print("  [OK] Só o Templo na Névoa tem banco de névoa, em 3 camadas, com densidade limitada e desigual.", flush=True)


def test_fog_moves_with_the_wind():
    arena, fog = _volume()
    spec = arena.spec.wind
    before = [(p.x, p.y) for p in fog.bank]
    t = _run(fog, 8.0)
    moved_x = statistics.mean(p.x - b[0] for p, b in zip(fog.bank, before) if abs(p.x - b[0]) < 10)
    assert moved_x > 1.5 * 0.9 * spec.strength * 0.4, f"o banco anda a favor do vento ({moved_x:.2f})"
    t = _run(fog, 60.0, t)
    margin = 8.0
    assert all(-margin < p.x < arena.cols + margin and -margin < p.y < arena.rows + margin for p in fog.bank), "puffs voltam pelo outro lado"
    print("  [OK] O banco anda com o vento da arena e os puffs que saem do mapa voltam pelo lado oposto.", flush=True)


def test_visibility_follows_density_with_a_floor():
    arena, fog = _volume()
    fog.time = 5.0
    dens = sorted(((fog.bank_density_at(x + 0.5, y + 0.5), x + 0.5, y + 0.5) for x in range(2, 20) for y in range(2, 20)))
    low, high = dens[0], dens[-1]
    assert fog.visibility_at(low[1], low[2]) > fog.visibility_at(high[1], high[2]) + 0.1, "mais névoa, menos visível"
    assert fog.visibility_at(high[1], high[2]) >= 0.45 - 1e-9, "só o banco nunca esconde por completo (a IA não muda)"
    fog.add_trail(10.0, 10.0)
    fog.update(0.2, 5.2)
    assert fog.visibility_at(10.0, 10.0) < 0.3
    for _ in range(10):
        fog.add_trail(10.0, 10.0)
    fog.update(0.2, 5.4)
    assert fog.visibility_at(10.0, 10.0) >= fog_module.VISIBILITY_FLOOR - 1e-9
    print("  [OK] A visibilidade cai com a densidade, com piso de 0.45 no banco e 0.20 no rastro.", flush=True)


def test_trail_lifecycle_and_dispel():
    arena, fog = _volume("ganryu_island")  # sem banco: só o rastro
    fog.add_trail(8.0, 11.0, 1.2)
    fog.update(0.2, 0.2)
    assert fog.trail_density_at(8.0, 11.0) > 0.6 and fog.trail_density_at(15.0, 11.0) == 0.0
    r0 = fog.trail[0].r
    _run(fog, 2.0, 0.2)
    assert fog.trail[0].r > r0, "o rastro se expande"
    assert fog.trail_density_at(fog.trail[0].x, fog.trail[0].y) > 0.2, "ainda esconde depois de 2 s"
    _run(fog, 2.0, 2.2)
    assert not fog.trail and fog.visibility_at(8.0, 11.0) == 1.0, "some depois de ~3,5 s"
    for k in range(60):
        fog.add_trail(k * 0.3 % 20, 11.0)
    assert len(fog.trail) <= fog_module.TRAIL_MAX, "teto de puffs de rastro"
    # sino do santuário
    arena, fog = _volume()
    fog.time = 3.0
    peak = max(fog.bank_density_at(x + 0.5, y + 0.5) for x in range(2, 20) for y in range(2, 20))
    fog.add_trail(10.0, 10.0)
    fog.dispel()
    assert not fog.trail, "o sino apaga o rastro"
    after = max(fog.bank_density_at(x + 0.5, y + 0.5) for x in range(2, 20) for y in range(2, 20))
    assert after < peak * 0.25, "e afina o banco"
    _run(fog, fog_module.CALM_RECOVERY + 1.0, 3.0)
    assert fog.calm == 1.0, "que volta ao normal"
    print("  [OK] Rastro cresce, esconde e some em ~3,5 s, respeita o teto; o sino o apaga e afina o banco por alguns segundos.", flush=True)


def test_kasumi_dash_leaves_a_trail_that_hides_her():
    random.seed(8)
    arena, fog = _volume("ganryu_island")
    kasumi = eng._fighter_at(CHAR_GRAY, 6.0, 11.0)
    assert not kasumi.fog_nodes
    kasumi.trigger_roll(1.0, 0.0, [])
    assert kasumi.stealth_timer == 1.0, "camuflagem pessoal mais curta: o resto vem do rastro"
    assert kasumi.fog_nodes and kasumi.fog_nodes[0][2] > 1.2, "nó grande na partida"
    for _ in range(40):
        kasumi.update(DT, arena, [])
        for node in kasumi.drain_fog_nodes():
            fog.add_trail(*node)
        fog.update(DT, 0.0)
        assert kasumi.fog_nodes == [], "o main esvazia os nós"
    assert kasumi.wx > 7.5, "esquiva andou"
    xs = sorted({round(p.x, 1) for p in fog.trail})
    assert len(xs) >= 4 and xs[-1] - xs[0] > 1.5, f"nós espalhados pelo caminho {xs}"
    assert fog.visibility_at(7.0, 11.0) < 0.35, "quem está no caminho fica quase invisível"
    t = _run(fog, 4.0)
    kasumi.stealth_timer = 0.0
    for _ in range(30):
        kasumi.update(DT, arena, [])
    assert kasumi.alpha == 255 and fog.visibility_at(7.0, 11.0) == 1.0
    print("  [OK] A esquiva da Kasumi pede nós ao longo do caminho; quem fica no rastro some, e depois tudo volta ao normal.", flush=True)


def test_ai_loses_aim_inside_the_trail():
    random.seed(12)
    arena, fog = _volume("ganryu_island")
    shooter = eng._fighter_at(CHAR_KENSHIN, 4.0, 11.0)
    target = eng._fighter_at(CHAR_GRAY, 14.0, 11.0)
    ai = SamuraiAI("hard")
    ai._map = arena

    def spread():
        errs = []
        for _ in range(400):
            ax, ay = ai._get_aim_target(shooter, target, target.wx, target.wy)
            errs.append(abs(math.atan2(ay - shooter.wy, ax - shooter.wx)))
        return statistics.mean(errs)

    clear = spread()
    fog.add_trail(14.0, 11.0)
    fog.update(0.2, 0.2)
    foggy = spread()
    assert foggy > clear * 3 and foggy > 0.08, (clear, foggy)
    ai._map = SimpleNamespace(fog=None)
    assert spread() < foggy / 2, "sem névoa a mira volta ao normal"
    arena2, fog2 = _volume()  # só o banco do cenário: a IA não muda
    ai._map = arena2
    assert abs(spread() - clear) < 0.03
    print(f"  [OK] A IA erra a mira dentro do rastro (erro {clear:.3f} -> {foggy:.3f} rad) e não é afetada pelo banco do cenário.", flush=True)


def test_queue_render_and_budget():
    random.seed(2)
    arena, fog = _volume()
    for k in range(10):
        fog.add_trail(6.0 + k * 0.5, 11.0)
    t = _run(fog, 1.0)
    surf = pygame.Surface((1280, 720))
    for az in (0, 45, 135):
        cam = Camera(11.0, 11.0)
        cam.set_azimuth(math.radians(az))
        items = fog.queue_items(cam)
        assert len(items) == fog.count and all(kind == "fog" for _, kind, _ in items)
        for _, _, puff in sorted(items, key=lambda i: i[0]):
            puff.render(surf, cam)
    assert surf.get_at((640, 360))[:3] != (0, 0, 0)
    cam = Camera(11.0, 11.0)
    cam.zoom = 1.4
    for _, _, puff in fog.queue_items(cam):
        puff.render(surf, cam)
    for k in range(30):
        fog.add_trail(5.0 + k * 0.4, 9.0 + (k % 3))
    cam = Camera(11.0, 11.0)
    total, frames = 0.0, 90
    for _ in range(10):
        for _, _, puff in fog.queue_items(cam):
            puff.render(surf, cam)
    start = time.perf_counter()
    for k in range(frames):
        t += DT
        fog.update(DT, t)
        for _, _, puff in fog.queue_items(cam):
            puff.render(surf, cam)
    ms = (time.perf_counter() - start) * 1000.0 / frames
    assert ms < 9.0, f"{ms:.1f} ms por quadro"
    print(f"  [OK] Fila de profundidade e render nos três azimutes e com zoom; custo {ms:.1f} ms por quadro com banco e rastro cheios.", flush=True)


def test_fog_volume():
    test_bank_only_in_the_temple_and_density_is_bounded()
    test_fog_moves_with_the_wind()
    test_visibility_follows_density_with_a_floor()
    test_trail_lifecycle_and_dispel()
    test_kasumi_dash_leaves_a_trail_that_hides_her()
    test_ai_loses_aim_inside_the_trail()
    test_queue_render_and_budget()


if __name__ == "__main__":
    test_fog_volume()
    print("=== TESTE 6.5.2 CONCLUÍDO ===", flush=True)
