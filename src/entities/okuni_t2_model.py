"""
src/entities/okuni_t2_model.py - Okuni (Técnica 2: Mapeamento UV / Pixel Art sobre Cubos)

Modelo estilizado com proporções refinadas e ricas texturas em Pixel Art
mapeadas diretamente nas faces dos blocos tridimensionais:
  - Cabeça: Mapeamento UV 360° com rosto kabuki pintado pixel-a-pixel (maquiagem oshiroi,
    kumadori teatral nos olhos com brilho de olhar, lábios carmesim com reflexo de laca),
    pente frontal kushi em ouro e nuca komata nas costas.
  - Quimono Carmesim Real: Painéis frontal, dorsal e saia texturizados com estampa
    floral de cerejeira (sakura) — pétalas suaves e brocados de ouro imperial.
  - Faixa Obi e Laço Musubi: Padrão geométrico ichimatsu xadrez ouro/preto e broche
    de jade esmeralda na frente, com laço borboleta fukura-suzume nas costas.
  - Mangas Furisode e Leques Tessen: Mangas texturizadas com barra de ouro e leque de aço
    com sol nascente radiante em pixel art.
  - Ordenação Dinâmica de Profundidade 360° (Painter's Algorithm): mangas e leques
    são ordenados de trás para frente perfeitamente em qualquer ângulo de rotação orbital.
"""
import math
import pygame

from src.isometric.iso_math import rotate_xy
from src.isometric.uv_voxel_renderer import draw_uv_cube, draw_uv_quad, shade_color

# Cores base de fallback e acabamentos
CRIMSON_BASE = (175, 22, 36)
CRIMSON_DARK = (120, 14, 25)
GOLD_BASE    = (235, 195, 60)
HAIR_BASE    = (18, 18, 22)
WHITE_BASE   = (250, 248, 242)
STEEL_BASE   = (215, 225, 240)


def depth(c, x: float, y: float) -> float:
    """Calcula profundidade relativa à câmera (maior = mais próximo do observador)."""
    rx, ry = rotate_xy(x, y, getattr(c, "azimuth", 0.0))
    return rx + ry


def render_okuni_t2(c):
    """Renderiza Okuni com a Técnica 2: Cubos Voxel com Mapeamento UV Pixel Art."""
    # Ângulo horizontal do guerreiro no mundo a partir de fx e fy
    yaw = math.atan2(c.fy, c.fx) - math.pi * 0.25

    bx, by = c.base_x, c.base_y
    torso_z = c.torso_z
    neck_z = c.neck_z
    head_z = c.head_z

    # Posições dos centros dos membros
    torso_depth = depth(c, bx, by)

    # Braço direito (empunhando leque principal aberto)
    ra_x = bx + 0.22 * math.cos(yaw + 0.9)
    ra_y = by + 0.22 * math.sin(yaw + 0.9)
    ra_depth = depth(c, ra_x, ra_y)

    # Braço esquerdo (postura elegante de dança kabuki)
    la_x = bx + 0.22 * math.cos(yaw - 0.9)
    la_y = by + 0.22 * math.sin(yaw - 0.9)
    la_depth = depth(c, la_x, la_y)

    # Lista de componentes ordenáveis por profundidade (Painter's Algorithm 360°)
    # Componentes com depth menor que torso_depth são desenhados ANTES do tronco/saia.
    # Componentes com depth maior são desenhados DEPOIS.

    # 1. Desenha membros que estão atrás do tronco
    if ra_depth < torso_depth:
        _draw_right_arm(c, ra_x, ra_y, torso_z, yaw)
    if la_depth < torso_depth:
        _draw_left_arm(c, la_x, la_y, torso_z, yaw)

    # 2. Saia e Cauda do Quimono (Volume inferior)
    _draw_skirt(c, bx, by, torso_z, yaw)

    # 3. Tronco e Obi (Volume central)
    _draw_torso(c, bx, by, torso_z, yaw)

    # 4. Pescoço e Cabeça (com texturas UV faciais 360°)
    _draw_head_and_hair(c, bx, by, head_z, neck_z, yaw)

    # 5. Desenha membros que estão à frente do tronco
    if ra_depth >= torso_depth:
        _draw_right_arm(c, ra_x, ra_y, torso_z, yaw)
    if la_depth >= torso_depth:
        _draw_left_arm(c, la_x, la_y, torso_z, yaw)


def _draw_skirt(c, bx: float, by: float, torso_z: float, yaw: float):
    """Saia longa do quimono com chuva de pétalas sakura e barra fuki acolchoada."""
    # Bloco superior da saia (quadril / transição do obi)
    draw_uv_cube(
        c.surface, c.camera,
        wx=bx, wy=by, wz=torso_z - 0.22,
        dx=0.28, dy=0.24, dz=0.22,
        tex_front="okuni_skirt_front",
        tex_back="okuni_skirt_back",
        tex_left="okuni_skirt_front",
        tex_right="okuni_skirt_front",
        fallback_color=CRIMSON_BASE,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    # Bloco inferior alargado da saia (até o chão, com barra fuki bordada)
    draw_uv_cube(
        c.surface, c.camera,
        wx=bx, wy=by, wz=0.0,
        dx=0.36, dy=0.32, dz=torso_z - 0.20,
        tex_front="okuni_skirt_front",
        tex_back="okuni_skirt_back",
        tex_left="okuni_skirt_front",
        tex_right="okuni_skirt_front",
        fallback_color=CRIMSON_DARK,
        yaw=yaw, outline=True, alpha=c.alpha
    )


def _draw_torso(c, bx: float, by: float, torso_z: float, yaw: float):
    """Tronco com quimono carmim, flores sakura e faixa obi com laço musubi nas costas."""
    # Bloco sólido do tronco
    draw_uv_cube(
        c.surface, c.camera,
        wx=bx, wy=by, wz=torso_z,
        dx=0.26, dy=0.20, dz=0.26,
        tex_front="okuni_torso_front",
        tex_back="okuni_torso_back",
        tex_left="okuni_torso_front",
        tex_right="okuni_torso_front",
        tex_top="okuni_hair_top",  # Ombro/gola
        fallback_color=CRIMSON_BASE,
        yaw=yaw, outline=True, alpha=c.alpha
    )


def _draw_head_and_hair(c, bx: float, by: float, head_z: float, neck_z: float, yaw: float):
    """
    Cabeça estilizada com maquiagem kabuki completa na frente,
    pente kushi dourado no topo, nuca komata atrás e adereços kanzashi.
    """
    # Pescoço delicado de porcelana
    draw_uv_cube(
        c.surface, c.camera,
        wx=bx, wy=by, wz=neck_z,
        dx=0.10, dy=0.10, dz=0.06,
        fallback_color=WHITE_BASE,
        yaw=yaw, outline=False, alpha=c.alpha
    )

    # Cubo principal da Cabeça / Rosto UV
    draw_uv_cube(
        c.surface, c.camera,
        wx=bx, wy=by, wz=head_z,
        dx=0.20, dy=0.20, dz=0.20,
        tex_front="okuni_face_front",
        tex_back="okuni_face_back",
        tex_top="okuni_hair_top",
        tex_left="okuni_hair_side",
        tex_right="okuni_hair_side",
        fallback_color=WHITE_BASE,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    # Coque volumoso Taka-Shimada acima da cabeça
    draw_uv_cube(
        c.surface, c.camera,
        wx=bx, wy=by - 0.03, wz=head_z + 0.17,
        dx=0.16, dy=0.16, dz=0.10,
        tex_top="okuni_hair_top",
        tex_back="okuni_face_back",
        fallback_color=HAIR_BASE,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    # Kanzashi dourados laterais (agulhas decorativas em 3D)
    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)
    for sign in [-1, 1]:
        kx = bx + sign * 0.13 * cos_y
        ky = by + sign * 0.13 * sin_y
        draw_uv_cube(
            c.surface, c.camera,
            wx=kx, wy=ky, wz=head_z + 0.12,
            dx=0.04, dy=0.04, dz=0.12,
            fallback_color=GOLD_BASE,
            yaw=yaw, outline=True, alpha=c.alpha
        )


def _draw_right_arm(c, ra_x: float, ra_y: float, torso_z: float, yaw: float):
    """Braço direito com manga furisode ampla e leque tessen aberto voltado para baixo/frente."""
    # Manga Furisode esvoaçante
    draw_uv_cube(
        c.surface, c.camera,
        wx=ra_x, wy=ra_y, wz=torso_z + 0.02,
        dx=0.14, dy=0.14, dz=0.24,
        tex_front="okuni_sleeve",
        tex_back="okuni_sleeve",
        tex_left="okuni_sleeve",
        tex_right="okuni_sleeve",
        fallback_color=CRIMSON_BASE,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)
    perp_x = -sin_y
    perp_y = cos_y

    # Mão delicada em tom de pele suave
    hand_z = torso_z + 0.06
    hx = ra_x + 0.07 * cos_y
    hy = ra_y + 0.07 * sin_y
    draw_uv_cube(
        c.surface, c.camera,
        wx=hx, wy=hy, wz=hand_z,
        dx=0.06, dy=0.06, dz=0.06,
        fallback_color=(252, 235, 226),
        yaw=yaw, outline=False, alpha=c.alpha
    )

    # Leque Tessen de Aço Aberto (orientado com o braço)
    fx = hx + 0.04 * cos_y
    fy = hy + 0.04 * sin_y
    fz = hand_z + 0.02
    w = 0.10
    h = 0.16

    p0 = (fx - perp_x * w * 0.5, fy - perp_y * w * 0.5, fz)
    p1 = (fx + perp_x * w * 0.5, fy + perp_y * w * 0.5, fz)
    p2 = (fx + perp_x * w * 0.8, fy + perp_y * w * 0.8, fz + h)
    p3 = (fx - perp_x * w * 0.8, fy - perp_y * w * 0.8, fz + h)

    draw_uv_quad(
        c.surface, c.camera,
        p0, p1, p2, p3,
        texture_name="okuni_fan",
        fallback_color=STEEL_BASE,
        outline=True, alpha=c.alpha
    )


def _draw_left_arm(c, la_x: float, la_y: float, torso_z: float, yaw: float):
    """Braço esquerdo em postura de dança graciosa erguendo o segundo leque tessen."""
    draw_uv_cube(
        c.surface, c.camera,
        wx=la_x, wy=la_y, wz=torso_z + 0.08,
        dx=0.13, dy=0.13, dz=0.22,
        tex_front="okuni_sleeve",
        tex_back="okuni_sleeve",
        tex_left="okuni_sleeve",
        tex_right="okuni_sleeve",
        fallback_color=CRIMSON_BASE,
        yaw=yaw, outline=True, alpha=c.alpha
    )

    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)
    perp_x = -sin_y
    perp_y = cos_y

    # Mão esquerda graciosa erguida
    hand_z = torso_z + 0.16
    hx = la_x + 0.06 * cos_y
    hy = la_y + 0.06 * sin_y
    draw_uv_cube(
        c.surface, c.camera,
        wx=hx, wy=hy, wz=hand_z,
        dx=0.06, dy=0.06, dz=0.06,
        fallback_color=(252, 235, 226),
        yaw=yaw, outline=False, alpha=c.alpha
    )

    # Segundo Leque Tessen Aberto ao alto (como no concept art original)
    fx = hx + 0.03 * cos_y
    fy = hy + 0.03 * sin_y
    fz = hand_z + 0.02
    w = 0.11
    h = 0.17

    p0 = (fx - perp_x * w * 0.5, fy - perp_y * w * 0.5, fz)
    p1 = (fx + perp_x * w * 0.5, fy + perp_y * w * 0.5, fz)
    p2 = (fx + perp_x * w * 0.9, fy + perp_y * w * 0.9, fz + h)
    p3 = (fx - perp_x * w * 0.9, fy - perp_y * w * 0.9, fz + h)

    draw_uv_quad(
        c.surface, c.camera,
        p0, p1, p2, p3,
        texture_name="okuni_fan",
        fallback_color=STEEL_BASE,
        outline=True, alpha=c.alpha
    )
