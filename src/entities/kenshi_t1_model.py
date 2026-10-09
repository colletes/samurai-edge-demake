"""
src/entities/kenshi_t1_model.py - Kenshi (Técnica 1: Micro-voxels e Texturas Procedurais Ricas)

Evolução de alta fidelidade visual do Espadachim Errante / Mestre de Iaijutsu
baseada diretamente na arte conceitual original (kenshi_concept.jpg):
  - Rosto nobre com olhar focado, sobrancelhas expressivas e lábios definidos.
  - Cabelo castanho-ruivo detalhado com franja em mechas e rabo de cavalo volumoso amarrado com fita carmim (kanoko).
  - Quimono carmim nobre com camadas, decote V com colarinho branco duplo (haneri) e brocados dourados.
  - Hakama escuro tradicional pregueado articulado nas coxas e canelas (legs_data) com sandálias Waraji e Tabi.
  - Faixa Obi preta com bordas douradas e laço.
  - Bainha Saya preta laqueada no quadril esquerdo com Tsuba dourada e kurikata.
  - Katana afiada em aço polido com reflexo de luz e hamon no corte Iai.
  - Ordenação correta por Profundidade da Câmera (Painter's Algorithm 360°).
"""
import math
import pygame

from src.config import COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
from src.isometric import cloth
from src.isometric.iso_math import rotate_xy
from src.isometric.voxel_renderer import draw_oriented_voxel_box, draw_voxel_box

# Paleta Kenshi T1
SKIN_NOBLE     = (248, 214, 186)
SKIN_SHADOW    = (218, 175, 145)
HAIR_AUBURN    = (185, 70, 35)
HAIR_DARK      = (130, 42, 20)
HAIR_HIGHLIGHT = (225, 105, 55)
RIBBON_RED     = (210, 35, 45)
KIMONO_RED     = (195, 30, 45)
KIMONO_DARK    = (135, 18, 30)
KIMONO_LIGHT   = (230, 60, 75)
GOLD_ACCENT    = (235, 195, 60)
HAKAMA_DARK    = (34, 36, 44)
HAKAMA_FOLD    = (48, 52, 64)
COLLAR_WHITE   = (245, 245, 250)
STEEL_BLADE    = (225, 235, 245)
STEEL_EDGE     = (255, 255, 255)
WARAJI_SOLE    = (160, 140, 110)
TABI_WHITE     = (240, 240, 245)


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


def draw_kenshi_legs_t1(c):
    """Pernas anatômicas articuladas com Hakama pregueada e Waraji."""
    for side in ("L", "R"):
        ld = c.legs_data[side]
        th_pos = ld["thigh"]
        sh_pos = ld["shin"]
        ft_pos = ld["foot"]

        # Coxa com Hakama escura pregueada
        _box(c, th_pos[0] - 0.075, th_pos[1] - 0.075, th_pos[2], 0.150, 0.150, 0.220, HAKAMA_DARK, texture="pleats")
        _box(c, th_pos[0] - 0.065, th_pos[1] - 0.065, th_pos[2] + 0.050, 0.130, 0.130, 0.120, HAKAMA_FOLD, outline=False)

        # Joelho e Canela
        _box(c, sh_pos[0] - 0.055, sh_pos[1] - 0.055, sh_pos[2], 0.110, 0.110, 0.190, HAKAMA_DARK, texture="silk")

        # Tiras de amarração nos kyahan (sutis e rentes à perna)
        for i in range(2):
            _box(c, sh_pos[0] - 0.056, sh_pos[1] - 0.056, sh_pos[2] + 0.045 + i * 0.055, 0.112, 0.112, 0.008, (210, 205, 195), outline=False)

        # Pé com Tabi branco e sola Waraji
        _box(c, ft_pos[0] - 0.042 + c.fx * 0.030, ft_pos[1] - 0.042 + c.fy * 0.030, ft_pos[2], 0.084, 0.084, 0.048, TABI_WHITE, outline=True)
        _box(c, ft_pos[0] - 0.042 + c.fx * 0.030, ft_pos[1] - 0.042 + c.fy * 0.030, ft_pos[2], 0.084, 0.084, 0.014, WARAJI_SOLE, outline=False)


def draw_kenshi_torso_t1(c):
    """Tronco de Kenshi: Quimono carmim nobre da cintura ao pescoço com gola branca dupla e Obi."""
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    pz = c.pelvis_z
    front = 0.115

    # 1. Bloco contínuo do quimono conectando quadril ao tronco
    torso_bottom = pz + 0.04
    torso_top = tz + 0.26
    _box(c, bx - 0.120, by - 0.090, torso_bottom, 0.240, 0.180, torso_top - torso_bottom, KIMONO_RED, texture="silk")

    # 2. Pescoço nobre
    _box(c, bx - 0.045, by - 0.045, tz + 0.200, 0.090, 0.090, 0.115, SKIN_NOBLE, outline=False)

    # 3. Gola dupla branca Haneri
    _box(c, bx + fx * (front - 0.008) - 0.045, by + fy * (front - 0.008) - 0.045, tz + 0.110, 0.090, 0.090, 0.130, COLLAR_WHITE, outline=False)
    # Pele do pescoço
    _box(c, bx + fx * front - 0.025, by + fy * front - 0.025, tz + 0.180, 0.050, 0.050, 0.050, SKIN_NOBLE, outline=False)

    # 4. Faixa Obi cerimonial na cintura com cordão sutil obijime
    _box(c, bx - 0.122, by - 0.092, pz + 0.060, 0.244, 0.184, 0.075, (25, 26, 32), texture="silk")
    _box(c, bx - 0.124, by - 0.094, pz + 0.088, 0.248, 0.188, 0.010, (215, 210, 195), outline=False)


def draw_kenshi_head_t1(c):
    """Rosto severo e cabelo ruivo com rabo de cavalo de Kenshi em micro-voxels."""
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # Raiz e orientação do rabo de cavalo atrás da cabeça
    root = (bx - fx * 0.040, by - fy * 0.040, hz + 0.150)
    rx_back, ry_back = rotate_xy(-c.fx * 0.040, -c.fy * 0.040, getattr(c, "azimuth", 0.0))
    tail_is_in_front = (rx_back + ry_back > 0.0)

    def _draw_ponytail():
        _box(c, root[0] - 0.025, root[1] - 0.025, root[2] - 0.005, 0.050, 0.050, 0.030, RIBBON_RED, outline=True)
        _obox(c, (root[0], root[1], root[2] + 0.010), (-fx * 0.6 + px * 0.1, -fy * 0.6 + py * 0.1, -0.7),
              length=0.180, width=0.065, height=0.065, color=HAIR_DARK, outline=True)
        _box(c, root[0] - fx * 0.030 - 0.015, root[1] - fy * 0.030 - 0.015, root[2] - 0.060, 0.030, 0.030, 0.080, RIBBON_RED, outline=False)

    # Se estiver atrás na tela, desenha antes da cabeça para que a cabeça fique na frente
    if not tail_is_in_front:
        _draw_ponytail()

    _box(c, bx - hw / 2, by - hw / 2, hz - 0.015, hw, hw, 0.165, SKIN_NOBLE)

    rx, ry = rotate_xy(c.fx, c.fy, getattr(c, "azimuth", 0.0))
    is_facing = (rx + ry > -0.15)

    if is_facing:
        front = hw / 2 + 0.006
        # Rosto nobre limpo como pele (sem cubos de olhos ou boca saltados)
        _box(c, bx + fx * (front - 0.005) - 0.045, by + fy * (front - 0.005) - 0.045, hz + 0.125, 0.090, 0.090, 0.040, HAIR_AUBURN)
    else:
        _box(c, bx - fx * 0.035 - 0.085, by - fy * 0.035 - 0.085, hz + 0.010, 0.170, 0.170, 0.150, HAIR_DARK, outline=False)

    _box(c, bx - 0.084, by - 0.084, hz + 0.125, 0.168, 0.168, 0.075, HAIR_AUBURN)
    _box(c, bx - 0.060, by - 0.060, hz + 0.170, 0.120, 0.120, 0.030, HAIR_HIGHLIGHT, outline=False)

    # Se estiver na frente na tela (vista traseira), desenha depois da cabeça
    if tail_is_in_front:
        _draw_ponytail()


def draw_kenshi_arms_and_katana_t1(c, arm_l, arm_r):
    """Mangas, braços e Katana de corte rápido Iaijutsu."""
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    tz = c.torso_z

    # Mangas largas carmim
    sh_l = (bx - px * 0.14, by - py * 0.14, tz + 0.20)
    sh_r = (bx + px * 0.14, by + py * 0.14, tz + 0.20)
    _box(c, arm_l[0] - 0.055, arm_l[1] - 0.055, arm_l[2] - 0.050, 0.110, 0.110, 0.140, KIMONO_RED, texture="silk")
    _box(c, arm_r[0] - 0.055, arm_r[1] - 0.055, arm_r[2] - 0.050, 0.110, 0.110, 0.140, KIMONO_RED, texture="silk")

    # Bainha Saya laqueada preta no quadril esquerdo
    k = (bx + px * 0.145 + fx * 0.020, by + py * 0.145 + fy * 0.020, c.pelvis_z + 0.075)
    b = _norm((-fx * 0.84 + px * 0.28, -fy * 0.84 + py * 0.28, -0.28))
    _obox(c, k, b, length=0.480, width=0.044, height=0.044, color=(20, 20, 24), texture="lacquer")
    _obox(c, k, b, length=0.030, width=0.052, height=0.052, color=GOLD_ACCENT, outline=False)

    if c.is_melee:
        # Ataque de corte Iai estendido
        hand = (arm_r[0] + fx * 0.08, arm_r[1] + fy * 0.08, arm_r[2])
        d = _norm((fx * 0.90 + px * 0.20, fy * 0.90 + py * 0.20, 0.10))
        # Cabo da katana
        _obox(c, (hand[0] - d[0] * 0.10, hand[1] - d[1] * 0.10, hand[2] - d[2] * 0.10), d,
              length=0.100, width=0.036, height=0.036, color=(22, 22, 26), outline=False)
        # Tsuba dourada
        _obox(c, hand, d, length=0.022, width=0.080, height=0.080, color=GOLD_ACCENT, outline=True)
        # Lâmina afiada de aço polido
        _obox(c, (hand[0] + d[0] * 0.022, hand[1] + d[1] * 0.022, hand[2] + d[2] * 0.022), d,
              length=0.620, width=0.036, height=0.016, color=STEEL_BLADE, outline=False)
        _obox(c, (hand[0] + d[0] * 0.022, hand[1] + d[1] * 0.022, hand[2] + d[2] * 0.022), d,
              length=0.620, width=0.012, height=0.020, color=STEEL_EDGE, outline=False)
    else:
        # Postura de saque Iai: mão direita na tsuka
        tsuka_pos = (k[0] + fx * 0.06, k[1] + fy * 0.06, k[2] + 0.03)
        _obox(c, tsuka_pos, b, length=0.100, width=0.036, height=0.036, color=(22, 22, 26), outline=False)
        _obox(c, k, b, length=0.022, width=0.080, height=0.080, color=GOLD_ACCENT, outline=True)


def render_kenshi_t1(c):
    """Ponto de entrada: Renderiza Kenshi no padrão Micro-voxels T1 com ordenação 360°."""
    # Sombra de solo
    sx0, sy0 = c.camera.apply(c.base_x, c.base_y, 0.0)
    shadow_w = int(24 * c.camera.zoom)
    shadow_h = int(12 * c.camera.zoom)
    shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (15, 12, 18, 120), (0, 0, shadow_w * 2, shadow_h * 2))
    c.surface.blit(shadow_surf, (sx0 - shadow_w, sy0 - shadow_h // 2))

    # Pernas e Hakama
    draw_kenshi_legs_t1(c)

    # Posicionamento cinemático dos braços
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    if c.state == "ATTACK":
        reach = 0.30 + 0.25 * c.atk_progress
        arm_r = (bx + fx * reach + px * 0.08, by + fy * reach + py * 0.08, tz + 0.18)
        arm_l = (bx - fx * 0.04 - px * 0.10, by - fy * 0.04 - py * 0.10, tz + 0.16)
    else:
        arm_r = (bx + fx * 0.06 - px * 0.04, by + fy * 0.06 - py * 0.04, tz + 0.15)
        arm_l = (bx + fx * 0.04 + px * 0.10, by + fy * 0.04 + py * 0.10, tz + 0.14)

    # Ordenação 360° por profundidade
    def depth(x, y):
        rx, ry = rotate_xy(x, y, getattr(c, "azimuth", 0.0))
        return rx + ry

    d_torso = depth(bx, by)
    d_arm_r = depth(arm_r[0], arm_r[1])
    d_arm_l = depth(arm_l[0], arm_l[1])

    back_elems = []
    front_elems = []

    elem_r = (d_arm_r, lambda: draw_kenshi_arms_and_katana_t1(c, arm_l, arm_r))
    (back_elems if d_arm_r < d_torso else front_elems).append(elem_r)

    # 1. Elementos atrás do tronco
    for _, fn in back_elems:
        fn()

    # 2. Tronco e Quimono
    draw_kenshi_torso_t1(c)

    # 3. Elementos à frente do tronco
    for _, fn in front_elems:
        fn()

    # 4. Cabeça e Cabelo ruivo
    draw_kenshi_head_t1(c)
