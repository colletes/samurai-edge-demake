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


def draw_oriented_voxel_box(
    surface: pygame.Surface,
    camera,
    ox: float, oy: float, oz: float,
    dir_x: float, dir_y: float, dir_z: float,
    length: float, width: float, height: float,
    color: tuple,
    up_x: float = 0.0, up_y: float = 0.0, up_z: float = 1.0,
    outline: bool = True,
    alpha: int = 255
):
    """
    Desenha um paralelepípedo de voxel 3D orientado no espaço ao longo de (dir_x, dir_y, dir_z).
    Permite lâminas diagonais, membros flexionados em qualquer ângulo 3D com iluminação correta
    e back-face culling para máxima performance.
    """
    # Normalizar vetor forward (direção do comprimento)
    f_len = math.hypot(dir_x, dir_y, dir_z)
    if f_len < 0.0001:
        dir_x, dir_y, dir_z = 1.0, 0.0, 0.0
    else:
        dir_x /= f_len; dir_y /= f_len; dir_z /= f_len

    # Vetor Up ortogonalizado (Gram-Schmidt)
    dot = up_x * dir_x + up_y * dir_y + up_z * dir_z
    ux = up_x - dot * dir_x
    uy = up_y - dot * dir_y
    uz = up_z - dot * dir_z
    u_len = math.hypot(ux, uy, uz)
    if u_len < 0.0001:
        ux, uy, uz = (0.0, 1.0, 0.0) if abs(dir_z) > 0.9 else (0.0, 0.0, 1.0)
        dot = ux * dir_x + uy * dir_y + uz * dir_z
        ux -= dot * dir_x; uy -= dot * dir_y; uz -= dot * dir_z
        u_len = math.hypot(ux, uy, uz)
    ux /= u_len; uy /= u_len; uz /= u_len

    # Vetor Right (Dir x Up)
    rx = dir_y * uz - dir_z * uy
    ry = dir_z * ux - dir_x * uz
    rz = dir_x * uy - dir_y * ux

    hw = width * 0.5
    hh = height * 0.5

    # 8 vértices no espaço 3D (do início ao fim ao longo do vetor dir)
    verts = []
    for k in (0.0, length):
        for j in (-hh, hh):
            for i in (-hw, hw):
                vx = ox + dir_x * k + rx * i + ux * j
                vy = oy + dir_y * k + ry * i + uy * j
                vz = oz + dir_z * k + rz * i + uz * j
                verts.append((vx, vy, vz))

    # Projeção dos 8 vértices para tela
    screen_pts = [camera.apply(v[0], v[1], v[2]) for v in verts]

    # As 6 faces definidas pelos índices com orientação de enrolamento
    faces = [
        ([4, 5, 7, 6], (dir_x, dir_y, dir_z)),
        ([1, 0, 2, 3], (-dir_x, -dir_y, -dir_z)),
        ([2, 3, 7, 6], (ux, uy, uz)),
        ([0, 1, 5, 4], (-ux, -uy, -uz)),
        ([1, 3, 7, 5], (rx, ry, rz)),
        ([0, 2, 6, 4], (-rx, -ry, -rz))
    ]

    top_shade, left_shade, right_shade, outline_shade = get_voxel_shades(color)

    # Iluminação direcional (Sol superior esquerdo)
    sun_x, sun_y, sun_z = 0.2, -0.4, 0.9
    s_norm = math.hypot(sun_x, sun_y, sun_z)
    sun_x /= s_norm; sun_y /= s_norm; sun_z /= s_norm

    for idxs, normal in faces:
        p0 = screen_pts[idxs[0]]
        p1 = screen_pts[idxs[1]]
        p2 = screen_pts[idxs[2]]
        p3 = screen_pts[idxs[3]]

        # Back-face culling na tela 2D
        cross_2d = (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])
        if cross_2d <= 0:
            continue

        ndotl = normal[0] * sun_x + normal[1] * sun_y + normal[2] * sun_z
        if ndotl > 0.45:
            face_color = top_shade
        elif ndotl > -0.15:
            face_color = left_shade
        else:
            face_color = right_shade

        poly = [p0, p1, p2, p3]
        if alpha < 255:
            min_x = min(p[0] for p in poly)
            max_x = max(p[0] for p in poly)
            min_y = min(p[1] for p in poly)
            max_y = max(p[1] for p in poly)
            bw = max(2, max_x - min_x + 2)
            bh = max(2, max_y - min_y + 2)
            f_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            loc_poly = [(p[0] - min_x, p[1] - min_y) for p in poly]
            pygame.draw.polygon(f_surf, (*face_color, alpha), loc_poly)
            if outline:
                pygame.draw.polygon(f_surf, (*outline_shade, alpha), loc_poly, 1)
            surface.blit(f_surf, (min_x, min_y))
        else:
            pygame.draw.polygon(surface, face_color, poly)
            if outline:
                pygame.draw.polygon(surface, outline_shade, poly, 1)

