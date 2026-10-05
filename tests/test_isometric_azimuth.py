"""
Teste da Fase 6 - Entregável 6.1: Azimute Real no Motor Isométrico.

Valida que:
1. Com azimute 0 a projeção é idêntica à isométrica 2:1 clássica.
2. O azimute gira o mundo em torno do alvo da câmera (alvo permanece no centro, 360° volta ao início)
   e iso_to_world desfaz a projeção para qualquer ângulo.
3. A entrada direcional continua relativa à tela (W = cima, D = direita) em qualquer azimute.
4. A chave de profundidade acompanha a posição vertical na tela (Y-sorting correto girado).
5. Os voxels mostram apenas as faces voltadas para a câmera (1-2 laterais + topo).
6. Terrenos, edifícios e lutadores renderizam em todos os azimutes sem erros.
"""
import math
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()
pygame.font.init()

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, HALF_TILE_W, HALF_TILE_H
from src.isometric.camera import Camera
from src.isometric.iso_math import world_to_iso, iso_to_world, input_to_world_direction, PIXELS_PER_Z
from src.isometric.voxel_renderer import draw_voxel_box, _visible_faces
from src.world.map_data import GameMap
from src.world.kyoto_map import KyotoMap
from src.entities.red_samurai import RedSamurai

AZIMUTHS = [math.radians(a) for a in range(0, 360, 15)]


def test_azimuth_zero_matches_classic_projection():
    camera = Camera(10.0, 12.0)
    for wx, wy, wz in [(3.0, 4.0, 0.0), (10.0, 12.0, 0.0), (15.5, 2.25, 1.4), (0.0, 21.0, 0.3)]:
        sx, sy = camera.apply(wx, wy, wz)
        exp_x = (wx - wy) * HALF_TILE_W - (10.0 - 12.0) * HALF_TILE_W + SCREEN_WIDTH // 2
        exp_y = (wx + wy) * HALF_TILE_H - wz * PIXELS_PER_Z - (10.0 + 12.0) * HALF_TILE_H + SCREEN_HEIGHT // 2
        assert abs(sx - exp_x) <= 1 and abs(sy - exp_y) <= 1, (wx, wy, wz, sx, sy, exp_x, exp_y)
    assert world_to_iso(3.0, 4.0, 0.5) == world_to_iso(3.0, 4.0, 0.5, 0.0)
    print("  [OK] Azimute 0 reproduz a projeção isométrica clássica.", flush=True)


def test_camera_orbit_and_roundtrip():
    camera = Camera(10.0, 12.0)
    for az in AZIMUTHS:
        camera.set_azimuth(az)
        # O alvo da câmera permanece no centro da tela em qualquer ângulo
        cx, cy = camera.apply(10.0, 12.0, 0.0)
        assert (cx, cy) == (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (az, cx, cy)
        # Projeção inversa recupera o ponto de mundo (relativo à câmera)
        sx, sy = world_to_iso(13.0 - 10.0, 7.0 - 12.0, 0.0, az)
        wx, wy = iso_to_world(sx, sy, az)
        assert abs(wx - 3.0) < 1e-6 and abs(wy + 5.0) < 1e-6, (az, wx, wy)

    camera.set_azimuth(0.0)
    before = camera.apply(14.0, 9.0, 0.5)
    for _ in range(24):
        camera.rotate(math.radians(15))
    assert camera.apply(14.0, 9.0, 0.5) == before
    assert -math.pi < camera.azimuth <= math.pi
    print("  [OK] Órbita em torno do alvo, volta completa e projeção inversa corretas.", flush=True)


def test_input_stays_screen_relative():
    camera = Camera(10.0, 10.0)
    for az in AZIMUTHS:
        camera.set_azimuth(az)
        base = camera.apply(10.0, 10.0, 0.0)
        for (dx, dy), check in [((0, -1), lambda ox, oy: oy < -3 and abs(ox) < 1.5),
                                ((1, 0), lambda ox, oy: ox > 3 and abs(oy) < 1.5),
                                ((0, 1), lambda ox, oy: oy > 3 and abs(ox) < 1.5),
                                ((-1, 0), lambda ox, oy: ox < -3 and abs(oy) < 1.5)]:
            dwx, dwy = input_to_world_direction(dx, dy, az)
            assert abs(math.hypot(dwx, dwy) - 1.0) < 1e-6
            moved = camera.apply(10.0 + dwx * 3.0, 10.0 + dwy * 3.0, 0.0)
            ox, oy = moved[0] - base[0], moved[1] - base[1]
            # Em tela o deslocamento correspondente a W/D/S/A deve apontar para cima/direita/baixo/esquerda
            assert check(ox / 3.0, oy / 3.0), (math.degrees(az), (dx, dy), ox, oy)
    print("  [OK] W/A/S/D seguem a tela em qualquer azimute.", flush=True)


def test_depth_matches_screen_order():
    camera = Camera(10.0, 10.0)
    points = [(4.0, 6.0), (12.0, 3.0), (9.0, 15.0), (16.0, 16.0), (2.0, 2.0)]
    for az in AZIMUTHS:
        camera.set_azimuth(az)
        for a in points:
            for b in points:
                if camera.depth(*a) - camera.depth(*b) > 0.5:
                    assert camera.apply(a[0], a[1], 0.0)[1] > camera.apply(b[0], b[1], 0.0)[1], (math.degrees(az), a, b)
    print("  [OK] Profundidade (Y-sorting) coerente com a posição vertical na tela.", flush=True)


def test_voxel_faces_visibility():
    shade = ((200, 0, 0), (100, 0, 0), (50, 0, 0))
    pts = [(0, 0)] * 8
    for az in AZIMUTHS:
        faces = _visible_faces(az, shade[1], shade[2], shade[0], *pts)
        sides = len(faces) - 1
        assert faces[-1][1] == shade[0], "a face do topo deve ser sempre desenhada por último"
        assert 1 <= sides <= 2, (math.degrees(az), sides)
        if abs(math.degrees(az) % 90 - 45) < 1e-6:
            assert sides == 1, "em múltiplos de 45° ímpares só uma lateral está de frente"
    classic = _visible_faces(0.0, shade[1], shade[2], shade[0], *pts)
    assert [f[1] for f in classic] == [shade[2], shade[1], shade[0]]  # +X direita, +Y esquerda, topo
    print("  [OK] Apenas faces voltadas para a câmera são desenhadas (1-2 laterais + topo).", flush=True)


def _changed_pixels(surface, reference_color):
    arr = pygame.surfarray.array3d(surface)
    return int((arr != reference_color).any(axis=2).sum())


def test_voxel_box_renders_at_all_azimuths():
    camera = Camera(5.0, 5.0)
    for az in AZIMUTHS:
        camera.set_azimuth(az)
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill((0, 0, 0))
        draw_voxel_box(surf, camera, 4.5, 4.5, 0.0, 1.0, 1.0, 1.0, (180, 120, 60))
        assert _changed_pixels(surf, (0, 0, 0)) > 300, math.degrees(az)

        surf.fill((0, 0, 0))
        draw_voxel_box(surf, camera, 4.5, 4.5, 0.0, 1.0, 1.0, 1.0, (180, 120, 60), alpha=120)
        assert _changed_pixels(surf, (0, 0, 0)) > 300, math.degrees(az)
    print("  [OK] Caixas voxel (opacas e translúcidas) renderizam em todos os azimutes.", flush=True)


def test_maps_and_fighters_render_at_all_azimuths():
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for game_map in (GameMap(), KyotoMap()):
        camera = Camera(11.0, 11.0)
        for az in AZIMUTHS:
            camera.set_azimuth(az)
            surf.fill((0, 0, 0))
            game_map.render_terrain(surf, camera, 1.0)
            assert _changed_pixels(surf, (0, 0, 0)) > 20000, (type(game_map).__name__, math.degrees(az))
            for obj in list(game_map.rocks) + list(game_map.trees) + list(game_map.bamboos[:20]):
                if hasattr(obj, "render"):
                    try:
                        obj.render(surf, camera)
                    except TypeError:
                        obj.render(surf, camera, 1.0)
            for b in getattr(game_map, "buildings", []):
                b.render(surf, camera, 1.0)

    fighter = RedSamurai(11.0, 11.0)
    camera = Camera(11.0, 11.0)
    for az in AZIMUTHS:
        camera.set_azimuth(az)
        surf.fill((0, 0, 0))
        fighter.render(surf, camera)
        assert _changed_pixels(surf, (0, 0, 0)) > 100, math.degrees(az)
    print("  [OK] Mapas, obstáculos, edifícios e lutadores renderizam em todos os azimutes.", flush=True)


def test_camera_azimuth_rotation_and_voxel_reprojection():
    print("=== TESTE 6.1: Azimute Real no Motor Isométrico ===", flush=True)
    test_azimuth_zero_matches_classic_projection()
    test_camera_orbit_and_roundtrip()
    test_input_stays_screen_relative()
    test_depth_matches_screen_order()
    test_voxel_faces_visibility()
    test_voxel_box_renders_at_all_azimuths()
    test_maps_and_fighters_render_at_all_azimuths()
    print("=== TESTE 6.1 CONCLUÍDO COM SUCESSO ===", flush=True)


if __name__ == "__main__":
    test_camera_azimuth_rotation_and_voxel_reprojection()
