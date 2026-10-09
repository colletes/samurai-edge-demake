"""
src/entities/musashi_t1_model.py - Musashi (Técnica 1: Micro-voxels e Texturas Procedurais Ricas)

Evolução de alta fidelidade visual do Mestre das Duas Espadas Niten Ichi-ryu
baseada diretamente na arte conceitual original (musashi_concept.jpg):
  - Rosto determinado com Hachimaki branco amarrado na testa e cicatriz de duelo marcante.
  - Cabelo negro rebelde espetado amarrado em coque samurai selvagem.
  - Quimono azul-cobalto de batalha com decote em V aberto exibindo porte atlético.
  - Hakama largo tradicional azul-marinho pregueado articulado nas coxas e canelas (legs_data).
  - Estilo Duas Espadas (Niten Ichi-ryu): Katana longa na mão direita e Wakizashi na esquerda.
  - Lâminas de aço polido reluzente e empunhaduras tradicionais de madeira e cordão.
  - Ordenação correta por Profundidade da Câmera (Painter's Algorithm 360°).
"""
import math
import pygame

from src.config import COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
from src.isometric import cloth
from src.isometric.iso_math import rotate_xy
from src.isometric.voxel_renderer import draw_oriented_voxel_box, draw_voxel_box

# Paleta Musashi T1
SKIN_WARRIOR   = (242, 208, 178)
SKIN_SHADOW    = (210, 168, 138)
HAIR_WILD      = (24, 22, 28)
HAIR_DARK      = (16, 14, 20)
HACHIMAKI      = (245, 245, 250)
SCAR_RED       = (175, 48, 42)
KIMONO_BLUE    = (45, 78, 142)
KIMONO_DARK    = (28, 50, 95)
KIMONO_LIGHT   = (65, 105, 180)
HAKAMA_BLUE    = (35, 45, 62)
HAKAMA_FOLD    = (50, 62, 85)
STEEL_BLADE    = (225, 235, 248)
STEEL_EDGE     = (255, 255, 255)
BRONZE_TSUBA   = (165, 120, 50)
WARAJI_SOLE    = (150, 130, 105)
TABI_BLUE      = (30, 38, 52)


def _box(c, x, y, z, w, d, h, color, outline=True, texture=None):
    draw_voxel_box(c.surface, c.camera, x, y, z, w, d, h, color, outline=outline, alpha=c.alpha, texture=texture)


def _obox(c, *args, **kwargs):
    if len(args) >= 2 and isinstance(args[0], (tuple, list)):
        ox, oy, oz = args[0]
        direction = args[1]
        length = args[2] if len(args) > 2 else kwargs.get("length")
        width = args[3] if len(args) > 3 else kwargs.get("width")
        height = args[4] if len(args) > 4 else kwargs.get("height")
        color = args[5] if len(args) > 5 else kwargs.get("color")
    else:
        ox, oy, oz = args[0], args[1], args[2]
        direction = args[3]
        length = args[4] if len(args) > 4 else kwargs.get("length")
        width = args[5] if len(args) > 5 else kwargs.get("width")
        height = args[6] if len(args) > 6 else kwargs.get("height")
        color = args[7] if len(args) > 7 else kwargs.get("color")

    up = kwargs.get("up", (0.0, 0.0, 1.0))
    outline = kwargs.get("outline", True)
    texture = kwargs.get("texture", None)
    draw_oriented_voxel_box(c.surface, c.camera, ox, oy, oz, direction[0], direction[1], direction[2],
                            length, width, height, color, up_x=up[0], up_y=up[1], up_z=up[2],
                            outline=outline, alpha=c.alpha, texture=texture)


def _norm(v):
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) or 1.0
    return (v[0] / n, v[1] / n, v[2] / n)


def draw_musashi_legs_t1(c):
    """Pernas articuladas com Hakama pregueada azul-marinho e sandálias Waraji."""
    for side in ("L", "R"):
        ld = c.legs_data[side]
        th_pos = ld["thigh"]
        sh_pos = ld["shin"]
        ft_pos = ld["foot"]

        # Coxa com Hakama pregueada
        _box(c, th_pos[0] - 0.075, th_pos[1] - 0.075, th_pos[2], 0.150, 0.150, 0.220, HAKAMA_BLUE, texture="pleats")
        _box(c, th_pos[0] - 0.065, th_pos[1] - 0.065, th_pos[2] + 0.050, 0.130, 0.130, 0.120, HAKAMA_FOLD, outline=False)

        # Canela
        _box(c, sh_pos[0] - 0.055, sh_pos[1] - 0.055, sh_pos[2], 0.110, 0.110, 0.190, HAKAMA_BLUE, texture="silk")

        # Tiras de amarração
        for i in range(2):
            _box(c, sh_pos[0] - 0.058, sh_pos[1] - 0.058, sh_pos[2] + 0.050 + i * 0.060, 0.116, 0.116, 0.014, (60, 75, 100), outline=False)

        # Pé com Tabi e Waraji
        _box(c, ft_pos[0] - 0.042 + c.fx * 0.030, ft_pos[1] - 0.042 + c.fy * 0.030, ft_pos[2], 0.084, 0.084, 0.048, TABI_BLUE, outline=True)
        _box(c, ft_pos[0] - 0.042 + c.fx * 0.030, ft_pos[1] - 0.042 + c.fy * 0.030, ft_pos[2], 0.084, 0.084, 0.014, WARAJI_SOLE, outline=False)


def draw_musashi_torso_t1(c):
    """Tronco de Musashi: Quimono azul cobalto contínuo e peitoral atlético."""
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    pz = c.pelvis_z
    front = 0.115

    torso_bottom = pz + 0.04
    torso_top = tz + 0.26
    _box(c, bx - 0.125, by - 0.095, torso_bottom, 0.250, 0.190, torso_top - torso_bottom, KIMONO_BLUE, texture="silk")

    # Decote amplo revelando peito e pescoço
    _box(c, bx + fx * (front - 0.005) - 0.040, by + fy * (front - 0.005) - 0.040, tz + 0.100, 0.080, 0.080, 0.140, SKIN_WARRIOR, outline=False)
    # Colarinho azul dobrado
    _box(c, bx + fx * front - 0.050, by + fy * front - 0.050, tz + 0.160, 0.100, 0.100, 0.050, KIMONO_LIGHT, outline=False)

    # Faixa Obi na cintura
    _box(c, bx - 0.120, by - 0.090, pz + 0.060, 0.240, 0.180, 0.075, (25, 28, 38), texture="silk")


def draw_musashi_head_t1(c):
    """Rosto severo de Musashi com Hachimaki branco e cicatriz de batalha."""
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    _box(c, bx - hw / 2, by - hw / 2, hz - 0.015, hw, hw, 0.165, SKIN_WARRIOR)

    rx, ry = rotate_xy(c.fx, c.fy, getattr(c, "azimuth", 0.0))
    is_facing = (rx + ry > -0.15)

    if is_facing:
        front = hw / 2 + 0.006
        # Cicatriz de combate diagonal marcante
        scar_x = bx + fx * front + px * 0.035
        scar_y = by + fy * front + py * 0.035
        _box(c, scar_x - 0.006, scar_y - 0.006, hz + 0.075, 0.012, 0.012, 0.050, SCAR_RED, outline=False)

        # Faixa Hachimaki branca na testa
        _box(c, bx - hw / 2 - 0.005, by - hw / 2 - 0.005, hz + 0.118, hw + 0.010, hw + 0.010, 0.030, HACHIMAKI, outline=True)
    else:
        _box(c, bx - fx * 0.035 - 0.085, by - fy * 0.035 - 0.085, hz + 0.010, 0.170, 0.170, 0.150, HAIR_DARK, outline=False)

    _box(c, bx - 0.084, by - 0.084, hz + 0.145, 0.168, 0.168, 0.065, HAIR_WILD)
    root = (bx - fx * 0.030, by - fy * 0.030, hz + 0.190)
    _obox(c, root, (-fx * 0.4 + px * 0.2, -fy * 0.4 + py * 0.2, 0.7),
          length=0.120, width=0.060, height=0.060, color=HAIR_DARK, outline=True)


def draw_musashi_arms_and_swords_t1(c, arm_l, arm_r):
    """Duas espadas Niten Ichi-ryu: Katana na direita e Wakizashi na esquerda."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    # Mangas azuis
    _box(c, arm_r[0] - 0.055, arm_r[1] - 0.055, arm_r[2] - 0.050, 0.110, 0.110, 0.140, KIMONO_BLUE, texture="silk")
    _box(c, arm_l[0] - 0.055, arm_l[1] - 0.055, arm_l[2] - 0.050, 0.110, 0.110, 0.140, KIMONO_BLUE, texture="silk")

    # Katana Longa na mão direita
    hand_r = (arm_r[0] + fx * 0.06, arm_r[1] + fy * 0.06, arm_r[2])
    d_kat = _norm((fx * 0.85 + px * 0.25, fy * 0.85 + py * 0.25, 0.15))
    _obox(c, (hand_r[0] - d_kat[0] * 0.10, hand_r[1] - d_kat[1] * 0.10, hand_r[2] - d_kat[2] * 0.10), d_kat,
          length=0.100, width=0.036, height=0.036, color=(24, 24, 28), outline=False)
    _obox(c, hand_r, d_kat, length=0.022, width=0.080, height=0.080, color=BRONZE_TSUBA, outline=True)
    _obox(c, (hand_r[0] + d_kat[0] * 0.022, hand_r[1] + d_kat[1] * 0.022, hand_r[2] + d_kat[2] * 0.022), d_kat,
          length=0.640, width=0.036, height=0.016, color=STEEL_BLADE, outline=False)
    _obox(c, (hand_r[0] + d_kat[0] * 0.022, hand_r[1] + d_kat[1] * 0.022, hand_r[2] + d_kat[2] * 0.022), d_kat,
          length=0.640, width=0.012, height=0.020, color=STEEL_EDGE, outline=False)

    # Wakizashi Curta na mão esquerda
    hand_l = (arm_l[0] + fx * 0.04, arm_l[1] + fy * 0.04, arm_l[2] - 0.020)
    d_wak = _norm((fx * 0.60 - px * 0.40, fy * 0.60 - py * 0.40, -0.25))
    _obox(c, (hand_l[0] - d_wak[0] * 0.08, hand_l[1] - d_wak[1] * 0.08, hand_l[2] - d_wak[2] * 0.08), d_wak,
          length=0.080, width=0.034, height=0.034, color=(24, 24, 28), outline=False)
    _obox(c, hand_l, d_wak, length=0.020, width=0.070, height=0.070, color=BRONZE_TSUBA, outline=True)
    _obox(c, (hand_l[0] + d_wak[0] * 0.020, hand_l[1] + d_wak[1] * 0.020, hand_l[2] + d_wak[2] * 0.020), d_wak,
          length=0.400, width=0.032, height=0.015, color=STEEL_BLADE, outline=False)
    _obox(c, (hand_l[0] + d_wak[0] * 0.020, hand_l[1] + d_wak[1] * 0.020, hand_l[2] + d_wak[2] * 0.020), d_wak,
          length=0.400, width=0.010, height=0.018, color=STEEL_EDGE, outline=False)


def render_musashi_t1(c):
    """Ponto de entrada: Renderiza Musashi no padrão Micro-voxels T1 com ordenação 360°."""
    sx0, sy0 = c.camera.apply(c.base_x, c.base_y, 0.0)
    shadow_w = int(25 * c.camera.zoom)
    shadow_h = int(13 * c.camera.zoom)
    shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (15, 12, 18, 120), (0, 0, shadow_w * 2, shadow_h * 2))
    c.surface.blit(shadow_surf, (sx0 - shadow_w, sy0 - shadow_h // 2))

    draw_musashi_legs_t1(c)

    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    if c.state == "ATTACK":
        reach = 0.30 + 0.25 * c.atk_progress
        arm_r = (bx + fx * reach + px * 0.12, by + fy * reach + py * 0.12, tz + 0.18)
        arm_l = (bx + fx * 0.15 - px * 0.12, by + fy * 0.15 - py * 0.12, tz + 0.14)
    else:
        arm_r = (bx + fx * 0.12 + px * 0.10, by + fy * 0.12 + py * 0.10, tz + 0.16)
        arm_l = (bx + fx * 0.06 - px * 0.10, by + fy * 0.06 - py * 0.10, tz + 0.14)

    def depth(x, y):
        rx, ry = rotate_xy(x, y, getattr(c, "azimuth", 0.0))
        return rx + ry

    d_torso = depth(bx, by)
    d_arms = depth((arm_r[0] + arm_l[0]) / 2, (arm_r[1] + arm_l[1]) / 2)

    back_elems = []
    front_elems = []

    elem_swords = (d_arms, lambda: draw_musashi_arms_and_swords_t1(c, arm_l, arm_r))
    (back_elems if d_arms < d_torso else front_elems).append(elem_swords)

    for _, fn in back_elems:
        fn()

    draw_musashi_torso_t1(c)

    for _, fn in front_elems:
        fn()

    draw_musashi_head_t1(c)
