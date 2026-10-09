"""
src/entities/kasumi_t4_model.py - Kasumi (Técnica 4: Modelo 3D Low-Poly Cel-Shaded via Software)

Implementação poligonal tridimensional estilizada da Kunoichi da Névoa:
- Geometria Low-Poly atlética e aerodinâmica: ombreiras cromadas facetadas,
  colete chanfrado, pernas esguias e máscara ninja poligonal.
- Cachecol da névoa em fita poligonal dinâmica que ondula ao vento.
- Adagas duplas shinobi em malha 3D chanfrada com gume afiado.
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

# Paleta Cel Shading de Kasumi
CHROME_LGT  = (225, 238, 252)
CHROME_SHD  = (140, 160, 185)
LEATHER_LGT = (52, 56, 66)
LEATHER_SHD = (28, 30, 36)
SCARF_LGT   = (145, 185, 225)
SCARF_SHD   = (90, 130, 175)
MASK_BLACK  = (22, 24, 28)
SKIN_PALE   = (248, 225, 212)
EYE_BLUE    = (75, 180, 245)


def depth(c, x: float, y: float) -> float:
    rx, ry = rotate_xy(x, y, getattr(c, "azimuth", 0.0))
    return rx + ry


_KASUMI_MESHES: dict[str, Mesh] = {}


def _get_kasumi_meshes():
    if not _KASUMI_MESHES:
        # 1. Pernas esguias com botas chanfradas
        _KASUMI_MESHES["leg"] = create_frustum_mesh(
            w_bottom=0.08, d_bottom=0.08,
            w_top=0.09, d_top=0.09,
            height=0.38,
            color=LEATHER_SHD,
            color_top=LEATHER_LGT
        )

        # 2. Joelheira/caneleira cromada
        _KASUMI_MESHES["knee_guard"] = create_frustum_mesh(
            w_bottom=0.09, d_bottom=0.07,
            w_top=0.10, d_top=0.08,
            height=0.12,
            color=CHROME_LGT
        )

        # 3. Tronco e colete tático facetado
        _KASUMI_MESHES["torso"] = create_frustum_mesh(
            w_bottom=0.20, d_bottom=0.16,
            w_top=0.22, d_top=0.18,
            height=0.26,
            color=LEATHER_LGT,
            color_top=CHROME_SHD
        )

        # 4. Ombreira cromada chanfrada
        _KASUMI_MESHES["pauldron"] = create_frustum_mesh(
            w_bottom=0.06, d_bottom=0.08,
            w_top=0.08, d_top=0.10,
            height=0.07,
            color=CHROME_LGT
        )

        # 5. Pescoço com colarinho de cachecol
        _KASUMI_MESHES["neck_scarf"] = create_octagonal_cylinder_mesh(
            radius=0.055, height=0.07, color=SCARF_LGT
        )

        # 6. Cabeça e máscara ninja poligonal
        _KASUMI_MESHES["head"] = create_frustum_mesh(
            w_bottom=0.14, d_bottom=0.14,
            w_top=0.16, d_top=0.16,
            height=0.18,
            color=MASK_BLACK,
            color_top=CHROME_SHD
        )

        # 7. Braço e bracelete
        _KASUMI_MESHES["arm"] = create_frustum_mesh(
            w_bottom=0.08, d_bottom=0.08,
            w_top=0.09, d_top=0.09,
            height=0.22,
            color=CHROME_LGT,
            color_top=LEATHER_SHD
        )

        # 8. Adaga Shinobi em lâmina afiada
        _KASUMI_MESHES["dagger"] = create_blade_mesh(
            length=0.22, width=0.05, thickness=0.02, color=CHROME_LGT
        )

    return _KASUMI_MESHES


def render_kasumi_t4(c):
    """Renderiza Kasumi na Técnica 4: Modelo 3D Low-Poly Cel-Shaded."""
    meshes = _get_kasumi_meshes()

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

    # Braço direito (guarda baixa)
    ra_x = bx + 0.18 * math.cos(yaw + 0.8)
    ra_y = by + 0.18 * math.sin(yaw + 0.8)
    ra_depth = depth(c, ra_x, ra_y)

    # Braço esquerdo (adaga invertida)
    la_x = bx + 0.18 * math.cos(yaw - 0.8)
    la_y = by + 0.18 * math.sin(yaw - 0.8)
    la_depth = depth(c, la_x, la_y)

    # Cauda do cachecol para trás
    sc_x = bx - 0.20 * cos_y
    sc_y = by - 0.20 * sin_y
    sc_depth = depth(c, sc_x, sc_y)

    # 1. Elementos traseiros
    if sc_depth < torso_depth:
        _draw_scarf_ribbon(c, bx, by, nz, yaw)
    if ra_depth < torso_depth:
        _draw_arm_t4(c, meshes, ra_x, ra_y, tz + 0.04, yaw, invert_blade=False)
    if la_depth < torso_depth:
        _draw_arm_t4(c, meshes, la_x, la_y, tz + 0.08, yaw, invert_blade=True)

    # 2. Pernas e Botas
    lx = bx - perp_x * 0.065
    ly = by - perp_y * 0.065
    rx = bx + perp_x * 0.065
    ry = by + perp_y * 0.065
    render_cel_mesh(c.surface, c.camera, meshes["leg"], lx, ly, 0.0, yaw=yaw, alpha=c.alpha)
    render_cel_mesh(c.surface, c.camera, meshes["leg"], rx, ry, 0.0, yaw=yaw, alpha=c.alpha)
    render_cel_mesh(c.surface, c.camera, meshes["knee_guard"], lx, ly, 0.14, yaw=yaw, alpha=c.alpha)
    render_cel_mesh(c.surface, c.camera, meshes["knee_guard"], rx, ry, 0.14, yaw=yaw, alpha=c.alpha)

    # 3. Tronco e Ombreiras cromadas
    render_cel_mesh(c.surface, c.camera, meshes["torso"], bx, by, tz, yaw=yaw, alpha=c.alpha)
    for sign in [-1, 1]:
        ox = bx + perp_x * sign * 0.13
        oy = by + perp_y * sign * 0.13
        render_cel_mesh(c.surface, c.camera, meshes["pauldron"], ox, oy, tz + 0.18, yaw=yaw, alpha=c.alpha)

    # 4. Pescoço e Cabeça
    render_cel_mesh(c.surface, c.camera, meshes["neck_scarf"], bx, by, nz, yaw=yaw, alpha=c.alpha)
    render_cel_mesh(c.surface, c.camera, meshes["head"], bx, by, hz, yaw=yaw, alpha=c.alpha)

    # Olhos azuis-gelo sutis no rosto poligonal
    p_head = c.camera.apply(bx + 0.07 * cos_y, by + 0.07 * sin_y, hz + 0.09)
    pygame.draw.circle(c.surface, EYE_BLUE, p_head, 2)

    # 5. Elementos frontais
    if sc_depth >= torso_depth:
        _draw_scarf_ribbon(c, bx, by, nz, yaw)
    if ra_depth >= torso_depth:
        _draw_arm_t4(c, meshes, ra_x, ra_y, tz + 0.04, yaw, invert_blade=False)
    if la_depth >= torso_depth:
        _draw_arm_t4(c, meshes, la_x, la_y, tz + 0.08, yaw, invert_blade=True)


def _draw_arm_t4(c, meshes, ax: float, ay: float, az: float, yaw: float, invert_blade: bool):
    """Braço com bracelete cromado e adaga afiada cel-shaded."""
    render_cel_mesh(c.surface, c.camera, meshes["arm"], ax, ay, az, yaw=yaw, alpha=c.alpha)

    # Adaga empunhada
    hx = ax + 0.06 * math.cos(yaw)
    hy = ay + 0.06 * math.sin(yaw)
    blade_z = az + (0.16 if invert_blade else -0.04)
    blade_yaw = yaw + (math.pi if invert_blade else 0.0)
    render_cel_mesh(c.surface, c.camera, meshes["dagger"], hx, hy, blade_z, yaw=blade_yaw, alpha=c.alpha)


def _draw_scarf_ribbon(c, bx: float, by: float, nz: float, yaw: float):
    """Fita poligonal do cachecol esvoaçando para trás com o vento."""
    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)
    wave = math.sin(c.walk_timer * 4.0) * 0.04

    p0 = c.camera.apply(bx - 0.06 * cos_y, by - 0.06 * sin_y, nz + 0.02)
    p1 = c.camera.apply(bx - 0.16 * cos_y + wave, by - 0.16 * sin_y, nz - 0.03)
    p2 = c.camera.apply(bx - 0.28 * cos_y + wave * 1.6, by - 0.28 * sin_y, nz - 0.12)
    p3 = c.camera.apply(bx - 0.32 * cos_y + wave * 2.0, by - 0.32 * sin_y, nz - 0.22)

    poly = [p0, p1, p2, p3]
    pygame.draw.lines(c.surface, (20, 24, 30), False, poly, 5)
    pygame.draw.lines(c.surface, SCARF_LGT, False, poly, 3)
