"""
Módulo de Renderização de Voxels Isométricos 3D.
Projeta cubos e paralelepípedos volumétricos com iluminação direcional (faces superior, esquerda e direita)
e chanfro estético característico de jogos voxel (como Crossy Road, 3D Dot Game Heroes e Voxatron).
"""
import json
import math
from contextlib import contextmanager
import pygame
from src.config import HALF_TILE_W, HALF_TILE_H
from src.isometric.iso_math import world_to_iso, PIXELS_PER_Z

# Cache de cores sombreadas para performance máxima
_COLOR_CACHE: dict[tuple, tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]] = {}
_CEL_CACHE: dict[tuple, tuple] = {}
_CEL_RAMPS: dict[tuple, tuple] = {}

STYLES = ("detailed", "cel")
CEL_INK = (18, 16, 22)  # cor do contorno dos sprites HD-2D
CEL_TEXTURES = frozenset({"pleats", "weave", "gloss", "cloth"})  # no cel só as linhas largas; os materiais finos (seda, couro...) não entram
_STYLE = "detailed"


def set_render_style(style: str):
    """"detailed" (voxels com chanfro e texturas) ou "cel" (3 faixas de tom chapadas e tinta, a partir dos sprites HD-2D)."""
    global _STYLE
    _STYLE = style if style in STYLES else "detailed"


def get_render_style() -> str:
    return _STYLE


def load_render_style(settings_path: str):
    """Aplica `video.character_style` do settings.json; sem o arquivo ou a chave fica "detailed"."""
    try:
        with open(settings_path, encoding="utf-8") as f:
            set_render_style(json.load(f).get("video", {}).get("character_style", "detailed"))
    except (OSError, ValueError, AttributeError):
        set_render_style("detailed")


@contextmanager
def render_style(style: str):
    """Troca o estilo só dentro do bloco (o contorno em cel-shading desenha o lutador numa camada própria)."""
    global _STYLE
    previous = _STYLE
    _STYLE = style if style in STYLES else "detailed"
    try:
        yield
    finally:
        _STYLE = previous


def register_cel_ramp(mid: tuple, light: tuple, shadow: tuple):
    """Fixa a rampa (luz, sombra) de um tom médio, amostrada dos sprites; sem registro a rampa é calculada."""
    mid = tuple(mid[:3])
    _CEL_RAMPS[mid] = (tuple(light[:3]), tuple(shadow[:3]))
    _CEL_CACHE.pop(mid, None)


def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t), int(a[2] + (b[2] - a[2]) * t))


def cel_ramp(color: tuple) -> tuple:
    """(luz, tom médio, sombra) de uma cor: tons escuros clareiam saturando e sombreiam esfriando, como nos sprites."""
    mid = tuple(color[:3])
    if mid in _CEL_RAMPS:
        light, shadow = _CEL_RAMPS[mid]
        return light, mid, shadow
    r, g, b = mid
    lum = (0.30 * r + 0.59 * g + 0.11 * b) / 255.0
    lift = 1.50 - 0.44 * min(1.0, lum / 0.9)
    drop = 0.62 + 0.18 * min(1.0, lum / 0.9)
    light = (min(255, int(r * lift) + 4), min(255, int(g * lift) + 3), min(255, int(b * lift) + 6))
    cool = 1.0 - min(1.0, lum * 1.6)
    shadow = (int(r * drop), int(g * drop * 0.94), min(255, int(b * drop * 0.98 + 10 * cool)))
    return light, mid, shadow


def _cel_shades(color: tuple):
    shades = _CEL_CACHE.get(color)
    if shades is None:
        light, mid, shadow = cel_ramp(color)
        shades = (light, mid, shadow, _mix(shadow, CEL_INK, 0.55))
        _CEL_CACHE[color] = shades
    return shades


def get_voxel_shades(color: tuple[int, int, int]):
    """Retorna as 4 variações de sombreamento da cor: (top, left, right, outline)."""
    if _STYLE == "cel":
        return _cel_shades(tuple(color[:3]))
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
    alpha: int = 255,
    texture: str | None = None
):
    """
    Desenha um bloco de voxel 3D posicionado em (wx, wy, wz) com dimensões (dx, dy, dz).
    `texture` (opcional) desenha um padrão procedural nas faces visíveis grandes (ver voxel_textures.py).
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

    # Faces visíveis como (polígono, cor). Com azimute 0 são as 3 faces clássicas (+Y esquerda, +X direita, topo).
    azimuth = getattr(camera, "azimuth", 0.0)
    if abs(azimuth) < 1e-6:
        faces = [
            ([p010, p110, p111, p011], left_shade, "x", "side"),
            ([p100, p110, p111, p101], right_shade, "y", "side"),
            ([p001, p101, p111, p011], top_shade, "x", "top"),
        ]
    else:
        faces = _visible_faces_ex(
            azimuth, left_shade, right_shade, top_shade,
            p000, p100, p110, p010, p001, p101, p111, p011,
        )

    if alpha < 255:
        # Para transparência (fumaça, camuflagem): desenha numa superfície local com bounding box
        all_pts = [p000, p100, p110, p010, p001, p101, p111, p011]
        min_x = min(p[0] for p in all_pts)
        max_x = max(p[0] for p in all_pts)
        min_y = min(p[1] for p in all_pts)
        max_y = max(p[1] for p in all_pts)
        bw = max(2, int(max_x - min_x + 2))
        bh = max(2, int(max_y - min_y + 2))

        voxel_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        ox, oy = min_x, min_y
        local_faces = [([(px - ox, py - oy) for px, py in poly], shade) for poly, shade, _, _ in faces]

        for poly, shade in local_faces:
            pygame.draw.polygon(voxel_surf, (*shade, alpha), poly)
        if outline:
            for poly, _ in local_faces:
                pygame.draw.polygon(voxel_surf, (*outline_shade, alpha), poly, 1)

        surface.blit(voxel_surf, (ox, oy))
        return

    # Desenho direto ultra-rápido quando alpha == 255
    for poly, shade, _, _ in faces:
        pygame.draw.polygon(surface, shade, poly)
    if texture and (_STYLE != "cel" or texture in CEL_TEXTURES):
        from src.isometric.voxel_textures import draw_face_texture
        seed = int(wx * 37.0 + wy * 57.0 + wz * 91.0 + dx * 13.0)
        for poly, shade, axis, kind in faces:
            if kind == "top":
                ulen, vlen = dx, dy
            else:
                ulen, vlen = (dx if axis == "x" else dy), dz
            draw_face_texture(surface, texture, poly, kind, ulen, vlen, shade, seed)
    if outline:
        for poly, _, _, _ in faces:
            pygame.draw.polygon(surface, outline_shade, poly, 1)


def _visible_faces(azimuth, left_shade, right_shade, top_shade,
                   p000, p100, p110, p010, p001, p101, p111, p011):
    """Faces voltadas para a câmera como (polígono, cor)."""
    return [(poly, shade) for poly, shade, _, _ in _visible_faces_ex(
        azimuth, left_shade, right_shade, top_shade, p000, p100, p110, p010, p001, p101, p111, p011)]


def _visible_faces_ex(azimuth, left_shade, right_shade, top_shade,
                      p000, p100, p110, p010, p001, p101, p111, p011):
    """
    Faces voltadas para a câmera com o mundo girado pelo azimute.
    Uma face lateral é visível se a normal girada aponta para o observador (nx' + ny' > 0).
    O sombreamento interpola entre o tom esquerdo e o direito conforme a normal gira,
    de modo que a iluminação varia continuamente durante a órbita.
    """
    c, s = math.cos(azimuth), math.sin(azimuth)
    sides = (  # (normal, polígono a-b-c-d, eixo da aresta u: a face +X estende-se ao longo de y)
        ((1, 0), [p100, p110, p111, p101], "y"),   # +X
        ((-1, 0), [p000, p010, p011, p001], "y"),  # -X
        ((0, 1), [p010, p110, p111, p011], "x"),   # +Y
        ((0, -1), [p000, p100, p101, p001], "x"),  # -Y
    )
    faces = []
    for (nx, ny), poly, axis in sides:
        rx = nx * c - ny * s
        ry = nx * s + ny * c
        if rx + ry <= 1e-6:
            continue
        t = max(0.0, min(1.0, 0.5 + (rx - ry) * 0.5))  # 0 = tom esquerdo, 1 = tom direito
        shade = tuple(int(l + (r - l) * t) for l, r in zip(left_shade, right_shade))
        faces.append((poly, shade, axis, "side"))
    faces.append(([p001, p101, p111, p011], top_shade, "x", "top"))
    return faces


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
    alpha: int = 255,
    texture: str | None = None
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

    # As 6 faces: índices, normal e as arestas (u, v) em unidades de mundo para a textura
    faces = [
        ([4, 5, 7, 6], (dir_x, dir_y, dir_z), width, height, "side"),
        ([1, 0, 2, 3], (-dir_x, -dir_y, -dir_z), width, height, "side"),
        ([2, 3, 7, 6], (ux, uy, uz), width, length, "top"),
        ([0, 1, 5, 4], (-ux, -uy, -uz), width, length, "side"),
        ([1, 3, 7, 5], (rx, ry, rz), height, length, "side"),
        ([0, 2, 6, 4], (-rx, -ry, -rz), height, length, "side")
    ]
    use_texture = bool(texture) and alpha >= 255 and (_STYLE != "cel" or texture in CEL_TEXTURES)
    seed = int(ox * 37.0 + oy * 57.0 + oz * 91.0 + length * 13.0) if use_texture else 0

    top_shade, left_shade, right_shade, outline_shade = get_voxel_shades(color)

    # Iluminação direcional (Sol superior esquerdo)
    sun_x, sun_y, sun_z = 0.2, -0.4, 0.9
    s_norm = math.hypot(sun_x, sun_y, sun_z)
    sun_x /= s_norm; sun_y /= s_norm; sun_z /= s_norm

    for idxs, normal, ulen, vlen, kind in faces:
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
            if use_texture:
                from src.isometric.voxel_textures import draw_face_texture
                draw_face_texture(surface, texture, poly, kind, ulen, vlen, face_color, seed + idxs[0])
            if outline:
                pygame.draw.polygon(surface, outline_shade, poly, 1)

