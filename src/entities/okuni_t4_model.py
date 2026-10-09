"""
src/entities/okuni_t4_model.py - Okuni (Técnica 4: Modelo 3D Low-Poly Cel-Shaded via Software)

Implementação poligonal tridimensional estilizada da Dançarina Kabuki:
- Geometria Low-Poly graciosa: saia cônica em trapézio facetada, mangas furisode
  em leque e penteado taka-shimada poligonal.
- Cel Shading de 2 bandas (luz brilhante vs sombra toon de recorte duro).
- Contornos de tinta estilo mangá (Ink Outline).
- Leques de aço Tessen poligonais afiados em postura elegante de dança.
- Ordenação rigorosa por profundidade em 360° (Painter's Algorithm).
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

# Paleta Cel Shading de Okuni
CRIMSON_MAIN = (195, 26, 42)
CRIMSON_DARK = (130, 16, 30)
GOLD_BRIGHT  = (246, 208, 68)
GOLD_SHADOW  = (180, 140, 40)
WHITE_OSHIROI= (252, 250, 246)
HAIR_BLACK   = (22, 20, 26)
OBI_BLACK    = (30, 28, 34)
STEEL_POLISH = (225, 235, 248)


def depth(c, x: float, y: float) -> float:
    """Profundidade relativa à câmera (maior = mais próximo do observador)."""
    rx, ry = rotate_xy(x, y, getattr(c, "azimuth", 0.0))
    return rx + ry


# Cache de primitivas estáticas de Okuni
_OKUNI_MESHES: dict[str, Mesh] = {}


def _get_okuni_meshes():
    if not _OKUNI_MESHES:
        # 1. Saia Superior (quadril e cintura)
        _OKUNI_MESHES["skirt_upper"] = create_frustum_mesh(
            w_bottom=0.34, d_bottom=0.28,
            w_top=0.24, d_top=0.18,
            height=0.22,
            color=CRIMSON_MAIN,
            color_top=OBI_BLACK
        )

        # 2. Saia Inferior Longa (alargada até o chão com barra fuki)
        _OKUNI_MESHES["skirt_lower"] = create_frustum_mesh(
            w_bottom=0.44, d_bottom=0.36,
            w_top=0.34, d_top=0.28,
            height=0.26,
            color=CRIMSON_DARK,
            color_top=CRIMSON_MAIN
        )

        # 3. Tronco e Obi (busto com decote elegante)
        _OKUNI_MESHES["torso"] = create_frustum_mesh(
            w_bottom=0.24, d_bottom=0.18,
            w_top=0.22, d_top=0.16,
            height=0.24,
            color=CRIMSON_MAIN,
            color_top=WHITE_OSHIROI
        )

        # 4. Pescoço gracioso de porcelana
        _OKUNI_MESHES["neck"] = create_octagonal_cylinder_mesh(
            radius=0.045, height=0.08, color=WHITE_OSHIROI
        )

        # 5. Cabeça e Rosto Kabuki poligonal
        _OKUNI_MESHES["head"] = create_frustum_mesh(
            w_bottom=0.15, d_bottom=0.15,
            w_top=0.17, d_top=0.17,
            height=0.19,
            color=WHITE_OSHIROI,
            color_top=HAIR_BLACK
        )

        # 6. Coque Shimada laqueado
        _OKUNI_MESHES["hair_bun"] = create_octagonal_cylinder_mesh(
            radius=0.075, height=0.11, color=HAIR_BLACK
        )

        # 7. Manga Furisode em trapézio (braço direito)
        _OKUNI_MESHES["sleeve"] = create_frustum_mesh(
            w_bottom=0.16, d_bottom=0.14,
            w_top=0.11, d_top=0.10,
            height=0.26,
            color=CRIMSON_MAIN,
            color_top=GOLD_BRIGHT
        )

        # 8. Leque Tessen de Aço Aberto
        mesh_fan = Mesh()
        # Vértices em leque aberto poligonal
        v_base = mesh_fan.add_vertex(0.0, 0.0, 0.0)
        v1 = mesh_fan.add_vertex(-0.08, 0.02, 0.16)
        v2 = mesh_fan.add_vertex(-0.03, 0.03, 0.19)
        v3 = mesh_fan.add_vertex( 0.03, 0.03, 0.19)
        v4 = mesh_fan.add_vertex( 0.08, 0.02, 0.16)
        mesh_fan.add_face([v_base, v1, v2], STEEL_POLISH)
        mesh_fan.add_face([v_base, v2, v3], GOLD_BRIGHT)
        mesh_fan.add_face([v_base, v3, v4], STEEL_POLISH)
        _OKUNI_MESHES["fan"] = mesh_fan

    return _OKUNI_MESHES


def render_okuni_t4(c):
    """Renderiza Okuni na Técnica 4: Modelo 3D Low-Poly com Cel Shading via Software."""
    meshes = _get_okuni_meshes()

    yaw = math.atan2(c.fy, c.fx) - math.pi * 0.25
    bx, by = c.base_x, c.base_y
    tz = c.torso_z
    hz = c.head_z
    nz = c.neck_z

    # Posições dos centros dos membros
    torso_depth = depth(c, bx, by)

    ra_x = bx + 0.22 * math.cos(yaw + 0.9)
    ra_y = by + 0.22 * math.sin(yaw + 0.9)
    ra_depth = depth(c, ra_x, ra_y)

    la_x = bx + 0.22 * math.cos(yaw - 0.9)
    la_y = by + 0.22 * math.sin(yaw - 0.9)
    la_depth = depth(c, la_x, la_y)

    # 1. Membros que estão atrás do tronco na perspectiva da câmera
    if ra_depth < torso_depth:
        _draw_arm_t4(c, meshes, ra_x, ra_y, tz + 0.02, yaw, has_fan=True, fan_up=False)
    if la_depth < torso_depth:
        _draw_arm_t4(c, meshes, la_x, la_y, tz + 0.06, yaw, has_fan=True, fan_up=True)

    # 2. Saia Inferior e Superior (Volume gracioso em camadas)
    render_cel_mesh(c.surface, c.camera, meshes["skirt_lower"], bx, by, 0.0, yaw=yaw, alpha=c.alpha)
    render_cel_mesh(c.surface, c.camera, meshes["skirt_upper"], bx, by, tz - 0.22, yaw=yaw, alpha=c.alpha)

    # 3. Tronco e Obi
    render_cel_mesh(c.surface, c.camera, meshes["torso"], bx, by, tz, yaw=yaw, alpha=c.alpha)

    # 4. Pescoço e Cabeça
    render_cel_mesh(c.surface, c.camera, meshes["neck"], bx, by, nz, yaw=yaw, alpha=c.alpha)
    render_cel_mesh(c.surface, c.camera, meshes["head"], bx, by, hz, yaw=yaw, alpha=c.alpha)
    render_cel_mesh(c.surface, c.camera, meshes["hair_bun"], bx, by - 0.03, hz + 0.17, yaw=yaw, alpha=c.alpha)

    # Detalhes de Kanzashi dourados 3D
    cos_y, sin_y = math.cos(yaw), math.sin(yaw)
    for sign in [-1, 1]:
        kx = bx + sign * 0.11 * cos_y
        ky = by + sign * 0.11 * sin_y
        k_pts = [
            c.camera.apply(kx, ky, hz + 0.12),
            c.camera.apply(kx + sign * 0.05 * cos_y, ky + sign * 0.05 * sin_y, hz + 0.22)
        ]
        pygame.draw.line(c.surface, GOLD_BRIGHT, k_pts[0], k_pts[1], 3)
        pygame.draw.circle(c.surface, GOLD_BRIGHT, k_pts[1], 3)

    # 5. Membros que estão à frente do tronco na perspectiva da câmera
    if ra_depth >= torso_depth:
        _draw_arm_t4(c, meshes, ra_x, ra_y, tz + 0.02, yaw, has_fan=True, fan_up=False)
    if la_depth >= torso_depth:
        _draw_arm_t4(c, meshes, la_x, la_y, tz + 0.06, yaw, has_fan=True, fan_up=True)


def _draw_arm_t4(c, meshes, ax: float, ay: float, az: float, yaw: float, has_fan: bool, fan_up: bool):
    """Manga furisode poligonal e leque de aço Tessen cel-shaded."""
    # Manga
    render_cel_mesh(c.surface, c.camera, meshes["sleeve"], ax, ay, az, yaw=yaw, alpha=c.alpha)

    # Mão graciosa
    hx = ax + 0.06 * math.cos(yaw)
    hy = ay + 0.06 * math.sin(yaw)
    hand_z = az + (0.12 if fan_up else 0.04)
    p_hand = c.camera.apply(hx, hy, hand_z)
    pygame.draw.circle(c.surface, WHITE_OSHIROI, p_hand, 4)

    # Leque Tessen de aço
    if has_fan:
        fx = hx + 0.03 * math.cos(yaw)
        fy = hy + 0.03 * math.sin(yaw)
        fz = hand_z + (0.02 if fan_up else -0.04)
        fan_yaw = yaw + (0.3 if fan_up else -0.4)
        render_cel_mesh(c.surface, c.camera, meshes["fan"], fx, fy, fz, yaw=fan_yaw, alpha=c.alpha)
