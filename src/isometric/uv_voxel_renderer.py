"""
src/isometric/uv_voxel_renderer.py - Renderizador de Voxels com Mapeamento UV Pixel Art (Técnica 2)

Projeta texturas desenhadas pixel-a-pixel diretamente sobre as faces das caixas de voxel 3D:
- Cada face visível (superior, frontal, traseira, esquerda, direita) mapeia a grade UV da textura.
- Utiliza Back-Face Culling 2D preciso via produto vetorial dos vértices projetados na tela,
  garantindo que detalhes faciais, estampas traseiras ou laterais NUNCA apareçam do lado oposto.
- Aplica iluminação direcional suave multiplicada sobre os pixels da textura original.
- Permite estampas detalhadas manuais (flores de cerejeira sakura, brasões Makoto, costuras de espartilho, etc.)
  com resolução nítida estilo retro 3D (Mega Man Legends / Vagrant Story / 3D Dot Game Heroes).
"""
import math
import pygame
from src.isometric.voxel_renderer import get_voxel_shades


# Cache global de texturas geradas em pixel art (matrizes de tuplas RGB)
_PIXEL_TEXTURES: dict[str, list[list[tuple[int, int, int]]]] = {}
_TEXTURES_INITIALIZED = False


def register_pixel_texture(name: str, grid: list[list[tuple[int, int, int]]]):
    """Registra uma textura em formato grade 2D de cores RGB."""
    _PIXEL_TEXTURES[name] = grid


def get_pixel_texture(name: str) -> list[list[tuple[int, int, int]]] | None:
    global _TEXTURES_INITIALIZED
    if not _TEXTURES_INITIALIZED:
        _TEXTURES_INITIALIZED = True
        try:
            from src.isometric.pixel_art_textures import init_pixel_art_textures
            init_pixel_art_textures()
        except ImportError:
            pass
    return _PIXEL_TEXTURES.get(name)


def shade_color(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    """Aplica fator de luminosidade direcional a uma cor RGB."""
    r, g, b = color[:3]
    return (
        max(0, min(255, int(r * factor))),
        max(0, min(255, int(g * factor))),
        max(0, min(255, int(b * factor)))
    )


def cross2d(p0: tuple[int, int], p1: tuple[int, int], p2: tuple[int, int]) -> int:
    """Calcula a área orientada 2D na tela (shoelace). Retorna > 0 se horário/voltado para a câmera."""
    return (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])


def draw_uv_cube(
    surface: pygame.Surface,
    camera,
    wx: float, wy: float, wz: float,
    dx: float, dy: float, dz: float,
    tex_top: str | None = None,
    tex_bottom: str | None = None,
    tex_front: str | None = None,
    tex_back: str | None = None,
    tex_left: str | None = None,
    tex_right: str | None = None,
    fallback_color: tuple[int, int, int] = (180, 40, 50),
    yaw: float = 0.0,
    outline: bool = True,
    alpha: int = 255
):
    """
    Renderiza um cubo voxel orientado no espaço 3D mapeando texturas UV em cada face visível.
    
    Convenção dos eixos locais do bloco:
    - +Z: Topo (tex_top)
    - -Z: Base (tex_bottom)
    - +Y: Frente / Peito / Rosto (tex_front)
    - -Y: Costas / Nuca (tex_back)
    - +X: Lado Direito do personagem (tex_right)
    - -X: Lado Esquerdo do personagem (tex_left)
    """
    # 8 vértices locais
    hx, hy = dx * 0.5, dy * 0.5
    local_verts = [
        (-hx, -hy, 0.0),   # 0: 000
        ( hx, -hy, 0.0),   # 1: 100
        ( hx,  hy, 0.0),   # 2: 110
        (-hx,  hy, 0.0),   # 3: 010
        (-hx, -hy, dz),    # 4: 001
        ( hx, -hy, dz),    # 5: 101
        ( hx,  hy, dz),    # 6: 111
        (-hx,  hy, dz),    # 7: 011
    ]

    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)

    # Transforma vértices para o mundo e projeta na tela
    proj_pts = []
    for lx, ly, lz in local_verts:
        # Rotação local por yaw
        rx = lx * cos_y - ly * sin_y
        ry = lx * sin_y + ly * cos_y
        px, py = camera.apply(wx + rx, wy + ry, wz + lz)
        proj_pts.append((px, py))

    top_shade, left_shade, right_shade, outline_shade = get_voxel_shades(fallback_color)

    # Definição das 6 faces com seus vértices em ordem horária na tela
    # Face Top (+Z): v4 -> v5 -> v6 -> v7
    # Face Front (+Y): v2 -> v3 -> v7 -> v6
    # Face Back (-Y): v0 -> v1 -> v5 -> v4
    # Face Right (+X): v1 -> v2 -> v6 -> v5
    # Face Left (-X): v3 -> v0 -> v4 -> v7
    # Face Bottom (-Z): v3 -> v2 -> v1 -> v0
    faces = [
        # (índices, nome_textura, base_shade, fator_luz)
        ("top", [proj_pts[4], proj_pts[5], proj_pts[6], proj_pts[7]], tex_top, top_shade, 1.15),
        ("front", [proj_pts[2], proj_pts[3], proj_pts[7], proj_pts[6]], tex_front, left_shade, 0.95),
        ("back", [proj_pts[0], proj_pts[1], proj_pts[5], proj_pts[4]], tex_back, right_shade, 0.65),
        ("right", [proj_pts[1], proj_pts[2], proj_pts[6], proj_pts[5]], tex_right, right_shade, 0.75),
        ("left", [proj_pts[3], proj_pts[0], proj_pts[4], proj_pts[7]], tex_left, left_shade, 0.85),
    ]

    # Renderiza apenas as faces voltadas para a câmera (cross2d > 0)
    for face_name, poly, tex_name, shade, factor in faces:
        if cross2d(poly[0], poly[1], poly[2]) > 0:
            _render_face_uv(surface, poly, tex_name, shade, factor, outline, outline_shade, alpha)


def draw_uv_quad(
    surface: pygame.Surface,
    camera,
    p0_3d: tuple[float, float, float],
    p1_3d: tuple[float, float, float],
    p2_3d: tuple[float, float, float],
    p3_3d: tuple[float, float, float],
    texture_name: str | None = None,
    fallback_color: tuple[int, int, int] = (200, 30, 40),
    outline: bool = True,
    alpha: int = 255
):
    """Renderiza um quadrilátero 3D plano texturizado com pixel art (ex: leques, faixas, lâminas)."""
    poly = [
        camera.apply(*p0_3d),
        camera.apply(*p1_3d),
        camera.apply(*p2_3d),
        camera.apply(*p3_3d),
    ]
    # Em faces de duas faces, renderiza independente do sinal
    top_shade, left_shade, right_shade, outline_shade = get_voxel_shades(fallback_color)
    is_front = cross2d(poly[0], poly[1], poly[2]) > 0
    light_factor = 1.05 if is_front else 0.75
    _render_face_uv(surface, poly if is_front else [poly[0], poly[3], poly[2], poly[1]],
                    texture_name, left_shade, light_factor, outline, outline_shade, alpha)


def _render_face_uv(
    surface: pygame.Surface,
    poly: list[tuple[int, int]],
    tex_name: str | None,
    fallback_shade: tuple[int, int, int],
    light_factor: float,
    outline: bool,
    outline_shade: tuple[int, int, int],
    alpha: int
):
    """Renderiza a face poligonal interpolando os texels da textura pixel art."""
    p0, p1, p2, p3 = poly
    tex = get_pixel_texture(tex_name) if tex_name else None

    if not tex:
        # Preenchimento sólido sombreado se não houver textura
        color = shade_color(fallback_shade, light_factor)
        pygame.draw.polygon(surface, color, poly)
        if outline:
            pygame.draw.polygon(surface, outline_shade, poly, 1)
        return

    # Rasterização dos texels na face poligonal
    h_tex = len(tex)
    w_tex = len(tex[0])

    # Interpolação bilinear de texels
    # u varia ao longo de p0 -> p1 (horizontal)
    # v varia ao longo de p0 -> p3 (vertical de cima para baixo)
    for v in range(h_tex):
        v0 = v / h_tex
        v1 = (v + 1) / h_tex

        left0_x = p0[0] + (p3[0] - p0[0]) * v0
        left0_y = p0[1] + (p3[1] - p0[1]) * v0
        left1_x = p0[0] + (p3[0] - p0[0]) * v1
        left1_y = p0[1] + (p3[1] - p0[1]) * v1

        right0_x = p1[0] + (p2[0] - p1[0]) * v0
        right0_y = p1[1] + (p2[1] - p1[1]) * v0
        right1_x = p1[0] + (p2[0] - p1[0]) * v1
        right1_y = p1[1] + (p2[1] - p1[1]) * v1

        row = tex[v]
        row_len = len(row)
        for u in range(row_len):
            u0 = u / row_len
            u1 = (u + 1) / row_len

            q0 = (int(left0_x + (right0_x - left0_x) * u0), int(left0_y + (right0_y - left0_y) * v0))
            q1 = (int(left0_x + (right0_x - left0_x) * u1), int(left0_y + (right0_y - left0_y) * v1))
            q2 = (int(left1_x + (right1_x - left1_x) * u1), int(left1_y + (right1_y - left1_y) * v1))
            q3 = (int(left1_x + (right1_x - left1_x) * u0), int(left1_y + (right1_y - left1_y) * v1))

            col_tex = row[u]
            col_shaded = shade_color(col_tex, light_factor)
            pygame.draw.polygon(surface, col_shaded, [q0, q1, q2, q3])

    if outline:
        pygame.draw.polygon(surface, outline_shade, poly, 1)
