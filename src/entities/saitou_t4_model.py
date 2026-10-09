"""
src/entities/saitou_t4_model.py - Saitou (Técnica 4: Modelo 3D Low-Poly Cel-Shaded via Software)

Implementação poligonal tridimensional estilizada do Capitão Shinsengumi:
- Geometria Low-Poly severa e imponente: haori azul-celeste asagi-iro em trapézio,
  hakama com pregas facetadas e nó chonmage samurai.
- Katana longa do Gatotsu em lâmina 3D chanfrada com tsuba poligonal.
- Cel Shading de 2 bandas e Ink Outlines em software puro.
"""
import math
import pygame

from src.isometric.iso_math import rotate_xy
from src.isometric.cel_mesh_renderer import (
    Mesh,
    create_frustum_mesh,
    create_octagonal_cylinder_mesh,
    create_blade_mesh,
    render_cel_mesh
)

# Paleta Cel Shading de Saitou
ASAGI_LGT   = (115, 205, 235)  # Haori azul-celeste Shinsengumi claro
ASAGI_SHD   = (65, 145, 175)   # Haori azul-celeste sombra
HAKAMA_LGT  = (38, 42, 52)     # Hakama escura
HAKAMA_SHD  = (20, 22, 28)
WHITE_DAND  = (250, 252, 255)  # Branco dandara
GOLD_TSUBA  = (238, 195, 62)
STEEL_BLADE = (230, 240, 252)
HAIR_BLACK  = (20, 18, 22)
SKIN_TAN    = (235, 195, 170)


def depth(c, x: float, y: float) -> float:
    rx, ry = rotate_xy(x, y, getattr(c, "azimuth", 0.0))
    return rx + ry


_SAITOU_MESHES: dict[str, Mesh] = {}


def _get_saitou_meshes():
    if not _SAITOU_MESHES:
        # 1. Hakama inferior (largura ampla nas pernas)
        _SAITOU_MESHES["hakama_lower"] = create_frustum_mesh(
            w_bottom=0.38, d_bottom=0.32,
            w_top=0.30, d_top=0.24,
            height=0.28,
            color=HAKAMA_SHD,
            color_top=HAKAMA_LGT
        )

        # 2. Hakama superior (cintura)
        _SAITOU_MESHES["hakama_upper"] = create_frustum_mesh(
            w_bottom=0.30, d_bottom=0.24,
            w_top=0.26, d_top=0.20,
            height=0.18,
            color=HAKAMA_LGT,
            color_top=WHITE_DAND
        )

        # 3. Haori Azul-Celeste (tronco samurai com peito haneri branco)
        _SAITOU_MESHES["haori_torso"] = create_frustum_mesh(
            w_bottom=0.28, d_bottom=0.22,
            w_top=0.26, d_top=0.20,
            height=0.26,
            color=ASAGI_LGT,
            color_top=WHITE_DAND
        )

        # 4. Pescoço samurai musculoso
        _SAITOU_MESHES["neck"] = create_octagonal_cylinder_mesh(
            radius=0.055, height=0.08, color=SKIN_TAN
        )

        # 5. Cabeça severa e queixo quadrado
        _SAITOU_MESHES["head"] = create_frustum_mesh(
            w_bottom=0.16, d_bottom=0.16,
            w_top=0.17, d_top=0.17,
            height=0.20,
            color=SKIN_TAN,
            color_top=HAIR_BLACK
        )

        # 6. Topknot Chonmage samurai
        _SAITOU_MESHES["chonmage"] = create_octagonal_cylinder_mesh(
            radius=0.040, height=0.12, color=HAIR_BLACK
        )

        # 7. Manga do Haori em trapézio
        _SAITOU_MESHES["sleeve"] = create_frustum_mesh(
            w_bottom=0.15, d_bottom=0.14,
            w_top=0.12, d_top=0.11,
            height=0.24,
            color=ASAGI_LGT,
            color_top=WHITE_DAND
        )

        # 8. Katana Longa do Gatotsu (lâmina afiada de 0.52m com bisel)
        _SAITOU_MESHES["katana"] = create_blade_mesh(
            length=0.52, width=0.045, thickness=0.018, color=STEEL_BLADE
        )

        # 9. Tsuba (guarda circular dourada)
        _SAITOU_MESHES["tsuba"] = create_octagonal_cylinder_mesh(
            radius=0.055, height=0.02, color=GOLD_TSUBA
        )

    return _SAITOU_MESHES


def render_saitou_t4(c):
    """Renderiza Saitou na Técnica 4: Modelo 3D Low-Poly Cel-Shaded."""
    meshes = _get_saitou_meshes()

    yaw = math.atan2(c.fy, c.fx) - math.pi * 0.25
    bx, by = c.base_x, c.base_y
    tz = c.torso_z
    hz = c.head_z
    nz = c.neck_z

    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)
    perp_x = -sin_y
    perp_y = cos_y

    torso_depth = depth(c, bx, by)

    # Braço esquerdo (apoiando a ponta/bainha da katana)
    la_x = bx + 0.16 * math.cos(yaw - 0.7)
    la_y = by + 0.16 * math.sin(yaw - 0.7)
    la_depth = depth(c, la_x, la_y)

    # Braço direito (empunhadura do Gatotsu para frente)
    ra_x = bx + 0.16 * math.cos(yaw + 0.7)
    ra_y = by + 0.16 * math.sin(yaw + 0.7)
    ra_depth = depth(c, ra_x, ra_y)

    # Katana projetada para frente horizontal
    blade_x = bx + 0.18 * cos_y
    blade_y = by + 0.18 * sin_y
    blade_z = tz + 0.12
    blade_depth = depth(c, blade_x, blade_y)

    # 1. Elementos traseiros
    if ra_depth < torso_depth:
        render_cel_mesh(c.surface, c.camera, meshes["sleeve"], ra_x, ra_y, tz + 0.04, yaw=yaw, alpha=c.alpha)
    if la_depth < torso_depth:
        render_cel_mesh(c.surface, c.camera, meshes["sleeve"], la_x, la_y, tz + 0.04, yaw=yaw, alpha=c.alpha)
    if blade_depth < torso_depth:
        _draw_gatotsu_blade(c, meshes, blade_x, blade_y, blade_z, yaw)

    # 2. Hakama inferior e superior
    render_cel_mesh(c.surface, c.camera, meshes["hakama_lower"], bx, by, 0.0, yaw=yaw, alpha=c.alpha)
    render_cel_mesh(c.surface, c.camera, meshes["hakama_upper"], bx, by, tz - 0.18, yaw=yaw, alpha=c.alpha)

    # 3. Haori Azul-Celeste (Tronco)
    render_cel_mesh(c.surface, c.camera, meshes["haori_torso"], bx, by, tz, yaw=yaw, alpha=c.alpha)

    # 4. Pescoço, Cabeça e Topknot Chonmage
    render_cel_mesh(c.surface, c.camera, meshes["neck"], bx, by, nz, yaw=yaw, alpha=c.alpha)
    render_cel_mesh(c.surface, c.camera, meshes["head"], bx, by, hz, yaw=yaw, alpha=c.alpha)
    render_cel_mesh(c.surface, c.camera, meshes["chonmage"], bx, by - 0.04, hz + 0.18, yaw=yaw, alpha=c.alpha)

    # 5. Elementos frontais
    if blade_depth >= torso_depth:
        _draw_gatotsu_blade(c, meshes, blade_x, blade_y, blade_z, yaw)
    if ra_depth >= torso_depth:
        render_cel_mesh(c.surface, c.camera, meshes["sleeve"], ra_x, ra_y, tz + 0.04, yaw=yaw, alpha=c.alpha)
    if la_depth >= torso_depth:
        render_cel_mesh(c.surface, c.camera, meshes["sleeve"], la_x, la_y, tz + 0.04, yaw=yaw, alpha=c.alpha)


def _draw_gatotsu_blade(c, meshes, bx: float, by: float, bz: float, yaw: float):
    """Katana longa estocada do Gatotsu com tsuba dourada."""
    # Tsuba
    render_cel_mesh(c.surface, c.camera, meshes["tsuba"], bx, by, bz, yaw=yaw, alpha=c.alpha)

    # Lâmina longa apontando para frente
    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)
    kx = bx + 0.04 * cos_y
    ky = by + 0.04 * sin_y
    # A lâmina é estocada horizontalmente para a frente
    render_cel_mesh(c.surface, c.camera, meshes["katana"], kx, ky, bz, yaw=yaw, alpha=c.alpha)
