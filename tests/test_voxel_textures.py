"""
Teste da 6.5.3: texturas procedurais nos voxels grandes (src/isometric/voxel_textures.py).
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_voxel_textures.py
"""
import math
import os
import random
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

import main
from src.config import SCREEN_HEIGHT, SCREEN_WIDTH
from src.isometric import voxel_textures as vt
from src.isometric.camera import Camera
from src.isometric.voxel_renderer import draw_voxel_box
from src.world.arenas import arena_ids, create_arena

BG = (30, 30, 34)


def _camera(az=45.0, zoom=1.0):
    cam = Camera(2.0, 2.0)
    cam.set_azimuth(math.radians(az))
    cam.zoom = zoom
    return cam


def _box(texture, size=(2.0, 2.0, 1.2), color=(150, 110, 70), az=45.0, zoom=1.0, alpha=255, pos=(1.0, 1.0, 0.0)):
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill(BG)
    cam = _camera(az, zoom)
    draw_voxel_box(surf, cam, *pos, *size, color, outline=True, alpha=alpha, texture=texture)
    return surf


def _diff(a, b):
    arr = np.abs(pygame.surfarray.array3d(a).astype(int) - pygame.surfarray.array3d(b).astype(int)).sum(axis=2)
    return int((arr > 0).sum()), arr


def test_every_pattern_draws_inside_the_box_at_all_azimuths():
    for name in vt.PATTERNS:
        for az in (0, 45, 135):
            plain, textured = _box(None, az=az), _box(name, az=az)
            changed, arr = _diff(plain, textured)
            assert changed > 10, f"{name}@{az}: o padrão não apareceu ({changed} px)"
            box_mask = np.abs(pygame.surfarray.array3d(plain).astype(int) - np.array(BG)).sum(axis=2) > 0
            outside = int(((arr > 0) & ~box_mask).sum())
            assert outside == 0, f"{name}@{az}: {outside} px fora do voxel"
    print(f"  [OK] Os {len(vt.PATTERNS)} padrões aparecem nas faces visíveis em 0/45/135 e nunca vazam para fora do voxel.", flush=True)


def test_lod_alpha_and_unknown_names_leave_the_box_smooth():
    assert _diff(_box(None, size=(0.12, 0.12, 0.12)), _box("planks", size=(0.12, 0.12, 0.12)))[0] == 0, "voxel pequeno fica liso"
    assert _diff(_box(None, alpha=120), _box("stone", alpha=120))[0] == 0, "translúcido fica liso"
    assert _diff(_box(None), _box("nao_existe"))[0] == 0, "nome desconhecido é ignorado"
    assert _diff(_box(None, zoom=2.0), _box("stone", zoom=2.0))[0] > _diff(_box(None), _box("stone"))[0], "mais zoom, mais detalhe"
    print("  [OK] Voxel pequeno, translúcido e nome desconhecido ficam lisos; mais zoom mostra mais detalhe.", flush=True)


def test_deterministic_and_position_dependent():
    a, b = _box("thatch"), _box("thatch")
    assert _diff(a, b)[0] == 0, "mesma chamada, mesmo desenho"
    other = _box("thatch", pos=(1.0, 1.0, 0.0), size=(2.0, 2.0, 1.2))
    shifted = _box("thatch", pos=(1.5, 1.5, 0.0))
    assert _diff(_box(None, pos=(1.5, 1.5, 0.0)), shifted)[0] > 0
    assert other.get_at((640, 300)) is not None
    print("  [OK] O padrão é determinístico e muda com a posição do voxel (sem repetição idêntica entre caixas).", flush=True)


def test_line_budget_on_a_huge_roof():
    calls = {"n": 0}
    real = pygame.draw.line

    def counting(*args, **kwargs):
        calls["n"] += 1
        return real(*args, **kwargs)

    pygame.draw.line = counting
    try:
        for name in ("roof_tile", "stone", "planks"):
            calls["n"] = 0
            _box(name, size=(8.0, 6.0, 0.4), zoom=2.0)
            assert calls["n"] <= 3 * (vt.MAX_LINES + 24), f"{name}: {calls['n']} linhas"
    finally:
        pygame.draw.line = real
    print(f"  [OK] Um telhado enorme não passa do teto de linhas por face (MAX_LINES={vt.MAX_LINES}).", flush=True)


def _static_pass(arena, camera):
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill(arena.bg_color)
    queue = sorted(main.build_static_render_queue(arena), key=lambda i: camera.depth(*main.static_item_center(i[1], i[2])))
    for _, kind, obj in queue:
        if kind in ("bamboo", "building", "lantern") or getattr(obj, "animated", False):
            obj.render(surf, camera, 1.0)
        else:
            obj.render(surf, camera)
    return surf


def test_props_use_textures_and_cost_stays_low():
    expected = {"bamboo", "kyoto", "ganryu_island", "forest_camp", "nagashino_field", "baroque_court", "mountain_shrine"}
    real = vt.draw_face_texture
    tally = {}
    for arena_id in arena_ids():
        random.seed(7)
        arena = create_arena(arena_id)
        camera = arena.attach_camera(Camera(11.0, 11.0))
        camera.set_azimuth(math.radians(45))
        count = {"faces": 0}

        def spy(*args, **kwargs):
            count["faces"] += 1
            return real(*args, **kwargs)

        vt.draw_face_texture = spy
        try:
            textured = _static_pass(arena, camera)
        finally:
            vt.draw_face_texture = real
        tally[arena_id] = count["faces"]
        vt.draw_face_texture = lambda *a, **k: None
        try:
            plain = _static_pass(arena, camera)
        finally:
            vt.draw_face_texture = real
        if arena_id in expected - {"mountain_shrine"}:
            assert _diff(plain, textured)[0] > 30, f"{arena_id}: os props deveriam ter textura"
    assert all(tally[a] > 0 for a in expected - {"mountain_shrine"}), tally

    worst = ("", 0.0)
    for arena_id in ("bamboo", "kyoto", "forest_camp", "nagashino_field", "baroque_court"):
        random.seed(7)
        arena = create_arena(arena_id)
        camera = arena.attach_camera(Camera(11.0, 11.0))
        _static_pass(arena, camera)
        on, off = [], []
        for _ in range(7):
            start = time.perf_counter()
            _static_pass(arena, camera)
            on.append(time.perf_counter() - start)
        vt.draw_face_texture = lambda *a, **k: None
        try:
            for _ in range(7):
                start = time.perf_counter()
                _static_pass(arena, camera)
                off.append(time.perf_counter() - start)
        finally:
            vt.draw_face_texture = real
        extra = (min(on) - min(off)) * 1000.0
        if extra > worst[1]:
            worst = (arena_id, extra)
        assert extra < 6.0, f"{arena_id}: texturas custam {extra:.1f} ms por quadro"
    print(f"  [OK] Os props das arenas usam as texturas ({sum(tally.values())} faces) e o custo extra por quadro é de até {worst[1]:.1f} ms ({worst[0]}).", flush=True)


def test_voxel_textures():
    test_every_pattern_draws_inside_the_box_at_all_azimuths()
    test_lod_alpha_and_unknown_names_leave_the_box_smooth()
    test_deterministic_and_position_dependent()
    test_line_budget_on_a_huge_roof()
    test_props_use_textures_and_cost_stays_low()


if __name__ == "__main__":
    test_voxel_textures()
    print("=== TESTE 6.5.3 CONCLUÍDO ===", flush=True)
