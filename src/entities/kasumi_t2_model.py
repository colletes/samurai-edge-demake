"""
src/entities/kasumi_t2_model.py - Kasumi (Técnica 2: Mapeamento UV / Pixel Art sobre Cubos)

Modelo shinobi ágil e estilizado com ricas texturas em Pixel Art
mapeadas diretamente nas faces dos blocos tridimensionais:
  - Cabeça: Mapeamento UV 360° com olhos azuis-gelo afiados, bandô protetor
    de testa cromado reluzente, máscara ninja anatômica e nó de bandana nas costas.
  - Colete-Espartilho Tático: 4 fivelas cromadas com realces especulares brilhantes,
    malha respirável sob o colarinho e costuras de couro reforçadas.
  - Costas: Arnês tático em X com bolsa de equipamentos e coldre dorsal.
  - Cachecol Shinobi Esvoaçante: Ondulando ao vento com dinâmica de profundidade.
  - Braços & Adaga: Protetores de braço cromados e adaga afiada com anel de arremesso.
  - Pernas & Botas: Calças escuras com ataduras cruzadas nas panturrilhas e coldre lateral.
  - Ordenação Dinâmica de Profundidade 360° (Painter's Algorithm): oclusão correta
    em qualquer ângulo de rotação da câmera orbital.
"""
import math
import pygame

from src.isometric.iso_math import rotate_xy
from src.isometric.uv_voxel_renderer import draw_uv_cube, draw_uv_quad

# Cores base de fallback
LEATHER_BASE = (36, 40, 48)
LEATHER_DARK = (22, 24, 30)
CHROME_BASE  = (210, 225, 240)
CHROME_DARK  = (130, 148, 170)
HAIR_BASE    = (18, 18, 22)
SCARF_BLUE   = (135, 175, 215)
SCARF_DARK   = (90, 130, 170)
SKIN_BASE    = (248, 226, 212)


def depth(c, x: float, y: float) -> float:
    """Calcula profundidade relativa à câmera (maior = mais próximo do observador)."""
    rx, ry = rotate_xy(x, y, getattr(c, "azimuth", 0.0))
    return rx + ry


def render_kasumi_t2(c):
    """Renderiza Kasumi com a Técnica 2: Cubos Voxel com Mapeamento UV Pixel Art."""
    yaw = math.atan2(c.fy, c.fx) - math.pi * 0.25

    bx, by = c.base_x, c.base_y
    torso_z = c.torso_z
    neck_z = c.neck_z
    head_z = c.head_z

    torso_depth = depth(c, bx, by)

    # Braço direito (empunhando adaga shinobi em guarda baixa)
    ra_x = bx + 0.18 * math.cos(yaw + 0.8)
    ra_y = by + 0.18 * math.sin(yaw + 0.8)
    ra_depth = depth(c, ra_x, ra_y)

    # Braço esquerdo (guarda defensiva com adaga invertida)
    la_x = bx + 0.18 * math.cos(yaw - 0.8)
    la_y = by + 0.18 * math.sin(yaw - 0.8)
    la_depth = depth(c, la_x, la_y)

    # Cachecol shinobi esvoaçando para trás (-Y no espaço local)
    scarf_tail_x = bx - 0.22 * math.cos(yaw)
    scarf_tail_y = by - 0.22 * math.sin(yaw)
    scarf_depth = depth(c, scarf_tail_x, scarf_tail_y)

    # 1. Componentes que estão atrás do tronco na perspectiva da câmera
    if scarf_depth < torso_depth:
        _draw_scarf_tail(c, bx, by, neck_z, yaw)
    if ra_depth < torso_depth:
        _draw_right_arm(c, ra_x, ra_y, torso_z, yaw)
    if la_depth < torso_depth:
        _draw_left_arm(c, la_x, la_y, torso_z, yaw)

    # 2. Pernas e Botas Táticas
    _draw_legs(c, bx, by, torso_z, yaw)

    # 3. Tronco e Colete com 4 fivelas UV
    _draw_torso(c, bx, by, torso_z, yaw)

    # 4. Pescoço, Cachecol gola e Cabeça com Máscara e Olhos UV
    _draw_head_and_mask(c, bx, by, head_z, neck_z, yaw)

    # 5. Componentes que estão à frente do tronco
    if scarf_depth >= torso_depth:
        _draw_scarf_tail(c, bx, by, neck_z, yaw)
    if ra_depth >= torso_depth:
        _draw_right_arm(c, ra_x, ra_y, torso_z, yaw)
    if la_depth >= torso_depth:
        _draw_left_arm(c, la_x, la_y, torso_z, yaw)


def _draw_legs(c, bx: float, by: float, torso_z: float, yaw: float):
    """Pernas com calças shinobi justas, ataduras nas panturrilhas e coldre."""
    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)
    perp_x = -sin_y
    perp_y = cos_y

    leg_len = torso_z
    leg_w = 0.08
    leg_d = 0.08

    # Perna direita
    rx = bx + perp_x * 0.065
    ry = by + perp_y * 0.065
    draw_uv_cube(
        c.surface, c.camera,
        wx=rx, wy=ry, wz=0.0,
        dx=leg_w, dy=leg_d, dz=leg_len,
        fallback_color=LEATHER_DARK,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    # Perna esquerda
    lx = bx - perp_x * 0.065
    ly = by - perp_y * 0.065
    draw_uv_cube(
        c.surface, c.camera,
        wx=lx, wy=ly, wz=0.0,
        dx=leg_w, dy=leg_d, dz=leg_len,
        fallback_color=LEATHER_DARK,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    # Coldre tático lateral na coxa direita
    draw_uv_cube(
        c.surface, c.camera,
        wx=rx + perp_x * 0.04, wy=ry + perp_y * 0.04, wz=torso_z * 0.5,
        dx=0.04, dy=0.06, dz=0.10,
        fallback_color=CHROME_DARK,
        yaw=yaw, outline=True, alpha=c.alpha
    )


def _draw_torso(c, bx: float, by: float, torso_z: float, yaw: float):
    """Colete-espartilho tático com 4 fivelas cromadas e arnês traseiro."""
    draw_uv_cube(
        c.surface, c.camera,
        wx=bx, wy=by, wz=torso_z,
        dx=0.22, dy=0.18, dz=0.26,
        tex_front="kasumi_torso_front",
        tex_back="kasumi_torso_back",
        tex_left="kasumi_torso_front",
        tex_right="kasumi_torso_front",
        fallback_color=LEATHER_BASE,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    # Placas cromadas nos ombros (ombreiras shinobi)
    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)
    perp_x = -sin_y
    perp_y = cos_y

    for sign in [-1, 1]:
        ox = bx + perp_x * sign * 0.13
        oy = by + perp_y * sign * 0.13
        draw_uv_cube(
            c.surface, c.camera,
            wx=ox, wy=oy, wz=torso_z + 0.18,
            dx=0.06, dy=0.08, dz=0.06,
            fallback_color=CHROME_BASE,
            yaw=yaw, outline=True, alpha=c.alpha
        )


def _draw_head_and_mask(c, bx: float, by: float, head_z: float, neck_z: float, yaw: float):
    """Cabeça com máscara ninja, olhos azuis-gelo afiados e protetor de testa cromado."""
    # Pescoço com gola de cachecol enrolado
    draw_uv_cube(
        c.surface, c.camera,
        wx=bx, wy=by, wz=neck_z,
        dx=0.12, dy=0.12, dz=0.06,
        fallback_color=SCARF_BLUE,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    # Cabeça principal com textura frontal da máscara e olhos
    draw_uv_cube(
        c.surface, c.camera,
        wx=bx, wy=by, wz=head_z,
        dx=0.19, dy=0.19, dz=0.19,
        tex_front="kasumi_face_front",
        tex_back="kasumi_face_back",
        fallback_color=HAIR_BASE,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    # Rabo de cavalo alto atrás da cabeça
    draw_uv_cube(
        c.surface, c.camera,
        wx=bx - 0.08 * math.cos(yaw), wy=by - 0.08 * math.sin(yaw), wz=head_z + 0.10,
        dx=0.08, dy=0.08, dz=0.14,
        fallback_color=HAIR_BASE,
        yaw=yaw, outline=True, alpha=c.alpha
    )


def _draw_scarf_tail(c, bx: float, by: float, neck_z: float, yaw: float):
    """Ponta do cachecol ninja esvoaçando em camadas para trás com o vento."""
    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)
    wave = math.sin(c.walk_timer * 4.0) * 0.03

    # Segmento 1 do cachecol
    s1_x = bx - 0.12 * cos_y + wave
    s1_y = by - 0.12 * sin_y
    draw_uv_cube(
        c.surface, c.camera,
        wx=s1_x, wy=s1_y, wz=neck_z + 0.01,
        dx=0.10, dy=0.10, dz=0.06,
        fallback_color=SCARF_BLUE,
        yaw=yaw, outline=False, alpha=c.alpha
    )

    # Segmento 2 (ponta esvoaçante descendo)
    s2_x = bx - 0.22 * cos_y + wave * 1.5
    s2_y = by - 0.22 * sin_y
    draw_uv_cube(
        c.surface, c.camera,
        wx=s2_x, wy=s2_y, wz=neck_z - 0.08,
        dx=0.08, dy=0.08, dz=0.12,
        fallback_color=SCARF_DARK,
        yaw=yaw, outline=False, alpha=c.alpha
    )


def _draw_right_arm(c, ra_x: float, ra_y: float, torso_z: float, yaw: float):
    """Braço direito com protetor cromado e adaga empunhada voltada para frente."""
    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)

    # Braço com protetor
    draw_uv_cube(
        c.surface, c.camera,
        wx=ra_x, wy=ra_y, wz=torso_z + 0.04,
        dx=0.11, dy=0.11, dz=0.20,
        tex_front="kasumi_arm_guard",
        tex_back="kasumi_arm_guard",
        fallback_color=LEATHER_BASE,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    # Mão com luva preta
    hand_z = torso_z + 0.04
    hx = ra_x + 0.06 * cos_y
    hy = ra_y + 0.06 * sin_y
    draw_uv_cube(
        c.surface, c.camera,
        wx=hx, wy=hy, wz=hand_z,
        dx=0.05, dy=0.05, dz=0.05,
        fallback_color=LEATHER_DARK,
        yaw=yaw, outline=False, alpha=c.alpha
    )

    # Adaga Shinobi em punho
    fx = hx + 0.05 * cos_y
    fy = hy + 0.05 * sin_y
    fz = hand_z - 0.02

    perp_x = -sin_y
    perp_y = cos_y
    w, h = 0.08, 0.16

    p0 = (fx - perp_x * w * 0.5, fy - perp_y * w * 0.5, fz)
    p1 = (fx + perp_x * w * 0.5, fy + perp_y * w * 0.5, fz)
    p2 = (fx + perp_x * w * 0.5, fy + perp_y * w * 0.5, fz + h)
    p3 = (fx - perp_x * w * 0.5, fy - perp_y * w * 0.5, fz + h)

    draw_uv_quad(
        c.surface, c.camera,
        p0, p1, p2, p3,
        texture_name="kasumi_dagger",
        fallback_color=CHROME_BASE,
        outline=True, alpha=c.alpha
    )


def _draw_left_arm(c, la_x: float, la_y: float, torso_z: float, yaw: float):
    """Braço esquerdo em guarda rápida com segunda adaga invertida."""
    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)

    draw_uv_cube(
        c.surface, c.camera,
        wx=la_x, wy=la_y, wz=torso_z + 0.08,
        dx=0.11, dy=0.11, dz=0.20,
        tex_front="kasumi_arm_guard",
        tex_back="kasumi_arm_guard",
        fallback_color=LEATHER_BASE,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    # Mão esquerda
    hand_z = torso_z + 0.12
    hx = la_x + 0.05 * cos_y
    hy = la_y + 0.05 * sin_y
    draw_uv_cube(
        c.surface, c.camera,
        wx=hx, wy=hy, wz=hand_z,
        dx=0.05, dy=0.05, dz=0.05,
        fallback_color=LEATHER_DARK,
        yaw=yaw, outline=False, alpha=c.alpha
    )

    # Segunda adaga em empunhadura invertida
    fx = hx + 0.04 * cos_y
    fy = hy + 0.04 * sin_y
    fz = hand_z + 0.08

    perp_x = -sin_y
    perp_y = cos_y
    w, h = 0.07, 0.15

    p0 = (fx - perp_x * w * 0.5, fy - perp_y * w * 0.5, fz)
    p1 = (fx + perp_x * w * 0.5, fy + perp_y * w * 0.5, fz)
    p2 = (fx + perp_x * w * 0.5, fy + perp_y * w * 0.5, fz - h)
    p3 = (fx - perp_x * w * 0.5, fy - perp_y * w * 0.5, fz - h)

    draw_uv_quad(
        c.surface, c.camera,
        p0, p1, p2, p3,
        texture_name="kasumi_dagger",
        fallback_color=CHROME_BASE,
        outline=True, alpha=c.alpha
    )
