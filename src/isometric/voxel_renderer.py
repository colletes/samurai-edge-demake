"""
Módulo de Renderização de Voxels Isométricos 3D.
Projeta cubos e paralelepípedos volumétricos com iluminação direcional (faces superior, esquerda e direita)
e chanfro estético característico de jogos voxel (como Crossy Road, 3D Dot Game Heroes e Voxatron).
"""
import math
import pygame
from src.config import HALF_TILE_W, HALF_TILE_H
from src.isometric.iso_math import world_to_iso, PIXELS_PER_Z

# Cache de cores sombreadas para performance máxima
_COLOR_CACHE: dict[tuple, tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]] = {}

def get_voxel_shades(color: tuple[int, int, int]):
    """Retorna as 4 variações de sombreamento da cor: (top, left, right, outline)."""
    if color in _COLOR_CACHE:
        return _COLOR_CACHE[color]

    r, g, b = color[:3]
    top = (min(255, int(r * 1.15)), min(255, int(g * 1.15)), min(255, int(b * 1.15)))
    left = (max(0, int(r * 0.78)), max(0, int(g * 0.78)), max(0, int(b * 0.78)))
    right = (max(0, int(r * 0.62)), max(0, int(g * 0.62)), max(0, int(b * 0.62)))
    outline = (max(0, int(r * 0.40)), max(0, int(g * 0.40)), max(0, int(b * 0.40)))

    shades = (top, left, right, outline)
    _COLOR_CACHE[color] = shades
    return shades


def draw_voxel_box(
    surface: pygame.Surface,
    camera,
    wx: float, wy: float, wz: float,
    dx: float, dy: float, dz: float,
    color: tuple,
    outline: bool = True,
    alpha: int = 255
):
    """
    Desenha um bloco de voxel 3D posicionado em (wx, wy, wz) com dimensões (dx, dy, dz).
    As 3 faces visíveis na projeção isométrica 2:1 são:
      - Face Superior (+Z): Iluminada pelo sol zenital.
      - Face Esquerda (+Y): Iluminação intermediária difusa.
      - Face Direita (+X): Face sombreada.
    """
    # 8 vértices projetados para a tela relativa à câmera
    def to_screen(x, y, z):
        return camera.apply(x, y, z)

    p000 = to_screen(wx, wy, wz)
    p100 = to_screen(wx + dx, wy, wz)
    p110 = to_screen(wx + dx, wy + dy, wz)
    p010 = to_screen(wx, wy + dy, wz)

    p001 = to_screen(wx, wy, wz + dz)
    p101 = to_screen(wx + dx, wy, wz + dz)
    p111 = to_screen(wx + dx, wy + dy, wz + dz)
    p011 = to_screen(wx, wy + dy, wz + dz)

    top_shade, left_shade, right_shade, outline_shade = get_voxel_shades(color)

    target_surf = surface
    if alpha < 255:
        # Para transparência (fumaça, camuflagem)
        # Calcula bounding box local
        all_pts = [p000, p100, p110, p010, p001, p101, p111, p011]
        min_x = min(p[0] for p in all_pts)
        max_x = max(p[0] for p in all_pts)
        min_y = min(p[1] for p in all_pts)
        max_y = max(p[1] for p in all_pts)
        bw = max(2, int(max_x - min_x + 2))
        bh = max(2, int(max_y - min_y + 2))

        voxel_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        ox, oy = min_x, min_y

        p000_l = (p000[0] - ox, p000[1] - oy)
        p100_l = (p100[0] - ox, p100[1] - oy)
        p110_l = (p110[0] - ox, p110[1] - oy)
        p010_l = (p010[0] - ox, p010[1] - oy)
        p001_l = (p001[0] - ox, p001[1] - oy)
        p101_l = (p101[0] - ox, p101[1] - oy)
        p111_l = (p111[0] - ox, p111[1] - oy)
        p011_l = (p011[0] - ox, p011[1] - oy)

        left_poly = [p011_l, p111_l, p110_l, p010_l]
        right_poly = [p101_l, p111_l, p110_l, p100_l]
        top_poly = [p001_l, p101_l, p111_l, p011_l]

        pygame.draw.polygon(voxel_surf, (*left_shade, alpha), left_poly)
        pygame.draw.polygon(voxel_surf, (*right_shade, alpha), right_poly)
        pygame.draw.polygon(voxel_surf, (*top_shade, alpha), top_poly)

        if outline:
            pygame.draw.polygon(voxel_surf, (*outline_shade, alpha), top_poly, 1)
            pygame.draw.polygon(voxel_surf, (*outline_shade, alpha), left_poly, 1)
            pygame.draw.polygon(voxel_surf, (*outline_shade, alpha), right_poly, 1)

        surface.blit(voxel_surf, (ox, oy))
        return

    # Desenho direto ultra-rápido quando alpha == 255
    left_poly = [p011, p111, p110, p010]
    right_poly = [p101, p111, p110, p100]
    top_poly = [p001, p101, p111, p011]

    pygame.draw.polygon(target_surf, left_shade, left_poly)
    pygame.draw.polygon(target_surf, right_shade, right_poly)
    pygame.draw.polygon(target_surf, top_shade, top_poly)

    if outline:
        pygame.draw.polygon(target_surf, outline_shade, top_poly, 1)
        pygame.draw.polygon(target_surf, outline_shade, left_poly, 1)
        pygame.draw.polygon(target_surf, outline_shade, right_poly, 1)


def draw_voxel_model(surface: pygame.Surface, camera, base_wx: float, base_wy: float, base_wz: float, parts: list[dict], alpha: int = 255):
    """
    Renderiza um conjunto articulado de blocos de voxels ordenados para compor um modelo complexo
    (ex: personagem, animal, arma ou elemento cenográfico).
    Cada parte é um dict:
      {
        'rel_pos': (rx, ry, rz),
        'size': (dx, dy, dz),
        'color': (r, g, b),
        'outline': True/False
      }
    """
    for part in parts:
        rx, ry, rz = part['rel_pos']
        dx, dy, dz = part['size']
        color = part['color']
        outline = part.get('outline', True)

        draw_voxel_box(
            surface, camera,
            base_wx + rx, base_wy + ry, base_wz + rz,
            dx, dy, dz,
            color, outline, alpha
        )
