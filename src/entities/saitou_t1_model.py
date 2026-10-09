"""
src/entities/saitou_t1_model.py - Saitou (Técnica 1: Micro-voxels e Texturas Procedurais Ricas)

Evolução de alta fidelidade visual do Capitão Shinsengumi baseada diretamente
na arte conceitual original (saitou_concept.jpg):
  - Rosto severo do Lobo de Mibu: sobrancelhas retas cerradas, olhar penetrante resoluto,
    costeletas longas e topknot chonmage samurai preso com fita branca.
  - Haori Shinsengumi clássico: azul-celeste vibrante (asagi-iro) sobre quimono navy,
    com padrão dente de serra branco dandara esculpido em micro-voxels triangulares nítidos
    nas barras das mangas e na aba traseira/dianteira.
  - Quimono e colarinho: azul-marinho profundo com gola dupla branca imaculada exposta no colo.
  - Faixa Obi cerimonial branca: faixa larga de seda com nó lateral e caudas caídas.
  - Hakama e perneiras: hakama escura pregueada, caneleiras pretas kyahan com amarrações
    cruzadas brancas, tabi branco e sandálias waraji.
  - Katana longa do Gatotsu: lâmina longa afiada (0.76m) apontada na horizontal à frente,
    cabo com ito preto e samegawa branca, bainha laqueada com koiguchi dourado e cordão sageo branco.
"""
import math
import pygame

from src.config import COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
from src.isometric import cloth
from src.isometric.voxel_renderer import draw_oriented_voxel_box, draw_voxel_box

# =============================================================================
# PALETA REFINADA DO CONCEPT ART (SAITOU T1)
# =============================================================================
HAORI_ASAGI     = (118, 196, 224)   # Azul-celeste característico do Shinsengumi
HAORI_DARK      = (82, 148, 178)    # Sombra das dobras do haori
HAORI_LINING    = (28, 36, 56)      # Forro interno escuro do haori
DANDARA_WHITE   = (250, 252, 255)   # Branco puro do padrão zigue-zague dente de serra

KIMONO_NAVY     = (28, 36, 62)      # Azul-marinho do quimono sob o haori
KIMONO_SHADOW   = (18, 24, 44)
COLLAR_WHITE    = (246, 248, 252)   # Colarinho branco interno duplo

HAKAMA_BLACK    = (24, 26, 36)      # Hakama escura tradicional
HAKAMA_FOLD     = (38, 42, 58)      # Pregas verticais de contraste da hakama

BELT_WHITE      = (242, 244, 248)   # Faixa obi branca cerimonial
BELT_SHADOW     = (185, 192, 205)

KYAHAN_BLACK    = (22, 22, 28)      # Caneleiras pretas de combate
KYAHAN_STRAP    = (220, 225, 235)   # Tiras brancas cruzadas de amarração
TABI_WHITE      = (248, 248, 252)   # Meias tabi brancas
WARAJI_SOLE     = (52, 44, 38)      # Sola de palha/madeira da sandália

SKIN_NOBLE      = (238, 206, 180)   # Tom de pele natural
SKIN_SHADOW     = (204, 168, 142)

HAIR_RAVEN      = (20, 20, 26)      # Cabelo preto carvão
HAIR_SHEEN      = (42, 42, 54)
TOPKNOT_TIE     = (240, 242, 246)   # Fita branca amarrando o chonmage

STEEL_BLADE     = (228, 238, 250)   # Aço polido da katana longa
STEEL_EDGE      = (255, 255, 255)   # Gume reflexivo de navalha
KATANA_GOLD     = (220, 188, 72)    # Tsuba e acabamentos de ouro
TSUKA_ITO       = (22, 24, 30)      # Trançado negro do cabo
TSUKA_SAME      = (240, 240, 244)   # Pele de arraia branca nos losangos do cabo
SAYA_LACQUER    = (24, 26, 34)      # Laca preta profunda da bainha
SAGEO_WHITE     = (235, 238, 245)   # Cordão de amarração da bainha


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


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _motion(c):
    if c.is_moving:
        return (-c.fx * 0.08, -c.fy * 0.08), 0.045, 7.5
    return (0.0, 0.0), 0.015, 1.9


# =============================================================================
# 1. CABEÇA, ROSTO SEVERO E TOPKNOT SAMURAI (MICRO-VOXELS T1)
# =============================================================================
def draw_head_t1(c):
    """
    Rosto severo de capitão samurai:
    - Olhos escuros cerrados com sobrancelhas grossas resolutas retas.
    - Costeletas longas descendo pelas têmporas.
    - Penteado samurai clássico com topo raspado sutil e topknot chonmage
      curvado para a frente, amarrado com fita branca tradicional.
    """
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # 1. Volume do crânio / cabeça base contínuo (inicia em hz - 0.015 para encaixar no pescoço)
    _box(c, bx - hw / 2, by - hw / 2, hz - 0.015, hw, hw, 0.165, SKIN_NOBLE)

    from src.isometric.iso_math import rotate_xy
    rx, ry = rotate_xy(c.fx, c.fy, getattr(c, "azimuth", 0.0))
    is_facing = (rx + ry > -0.15)

    if is_facing:
        front = hw / 2 + 0.006

        # Rosto severo samurai esculpido limpo (sem cubos saltados de olhos ou boca em 360°)
        pass
    else:
        # Quando de costas para a câmera, desenha o cabelo traseiro espesso cobrindo a nuca
        _box(c, bx - fx * 0.035 - 0.085, by - fy * 0.035 - 0.085, hz + 0.010, 0.170, 0.170, 0.150, HAIR_RAVEN, outline=False)

    # Cabelo preto com calota e costeletas
    _box(c, bx - 0.084, by - 0.084, hz + 0.125, 0.168, 0.168, 0.075, HAIR_RAVEN)
    for s in (-1.0, 1.0):
        _box(c, bx + px * 0.085 * s - 0.012, by + py * 0.085 * s - 0.012, hz + 0.055, 0.024, 0.045, 0.100, HAIR_RAVEN, outline=False)

    # Topknot tradicional samurai (Chonmage) amarrado com fita branca
    root = (bx - fx * 0.030, by - fy * 0.030, hz + 0.190)
    _box(c, root[0] - 0.024, root[1] - 0.024, root[2] - 0.005, 0.048, 0.048, 0.026, TOPKNOT_TIE, outline=False)
    _obox(c, (root[0], root[1], root[2] + 0.015), (-fx * 0.5 + 0.1, -fy * 0.5 + 0.1, 0.8),
          length=0.100, width=0.048, height=0.048, color=HAIR_RAVEN, outline=True)
    _obox(c, (root[0] - fx * 0.03, root[1] - fy * 0.03, root[2] + 0.080), (fx * 0.8, fy * 0.8, -0.2),
          length=0.085, width=0.042, height=0.042, color=HAIR_RAVEN, outline=False)


# =============================================================================
# 2. HAORI SHINSENGUMI COM ESTAMPA DANDARA (MICRO-VOXELS T1)
# =============================================================================
def draw_haori_and_torso_t1(c):
    """
    Haori Shinsengumi com gola branca e estampa Dandara (dente de serra):
    - Quimono azul-marinho interno com colarinho branco em decote V.
    - Haori azul-celeste asagi-iro com caimento largo.
    - Padrão dente de serra branco Dandara esculpido com dentes triangulares nítidos.
    - Faixa Obi branca na cintura com nó e pontas caídas.
    """
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.115

    # 1. Quimono azul-marinho contínuo conectando até a base do pescoço (sem gap!)
    _box(c, bx - 0.120, by - 0.090, tz - 0.005, 0.240, 0.180, 0.270, KIMONO_NAVY, texture="silk")

    # 2. Pescoço muscular contínuo conectando tronco à cabeça
    _box(c, bx - 0.045, by - 0.045, tz + 0.200, 0.090, 0.090, 0.115, SKIN_NOBLE, outline=False)

    # 3. Colarinho branco duplo Haneri envolvendo o pescoço
    _box(c, bx - 0.052, by - 0.052, tz + 0.205, 0.104, 0.104, 0.075, COLLAR_WHITE, outline=False)
    _box(c, bx + fx * 0.055 - 0.040, by + fy * 0.055 - 0.040, tz + 0.160, 0.080, 0.080, 0.110, COLLAR_WHITE, outline=False)

    # Colarinho branco duplo limpo aparecendo no decote (Haneri)
    _box(c, bx + fx * (front - 0.008) - 0.045, by + fy * (front - 0.008) - 0.045, tz + 0.110, 0.090, 0.090, 0.130, COLLAR_WHITE, outline=False)
    # Pele do pescoço / colo
    _box(c, bx + fx * front - 0.025, by + fy * front - 0.025, tz + 0.180, 0.050, 0.050, 0.050, SKIN_NOBLE, outline=False)

    # Abas frontais do Haori azul-celeste
    for s in (-1.0, 1.0):
        _box(c, bx + px * 0.095 * s - 0.040, by + py * 0.095 * s - 0.040, tz + 0.040, 0.080, 0.160, 0.170, HAORI_ASAGI, texture="silk")
        # Dente de serra Dandara na ponta da aba dianteira
        for j in range(2):
            dx_dandara = bx + px * (0.075 + j * 0.035) * s + fx * front
            dy_dandara = by + py * (0.075 + j * 0.035) * s + fy * front
            _box(c, dx_dandara - 0.015, dy_dandara - 0.015, tz + 0.040, 0.030, 0.030, 0.035, DANDARA_WHITE, outline=False)

    # Faixa Obi branca cerimonial na cintura
    pz = c.pelvis_z
    _box(c, bx - 0.115, by - 0.085, pz + 0.060, 0.230, 0.170, 0.075, BELT_WHITE, texture="silk")
    # Nó lateral e caudas pendentes
    kx, ky = bx + fx * 0.090 - px * 0.050, by + fy * 0.090 - py * 0.050
    _box(c, kx - 0.030, ky - 0.030, pz + 0.065, 0.060, 0.060, 0.060, BELT_WHITE, outline=True)
    # Caudas do obi que balançam
    trail, amp, freq = _motion(c)
    offs = cloth.chain_offsets(2, c.walk_timer, 0.8, trail, (px, py), amp=amp * 1.3, freq=freq)
    for i, (ox, oy, oz) in enumerate(offs):
        _box(c, kx + ox - 0.018, ky + oy - 0.018, pz - 0.055 * (i + 1) + oz, 0.036, 0.036, 0.065, BELT_WHITE, outline=False)


# =============================================================================
# 3. ABA TRASEIRA DO HAORI E DANDARA POSTERIOR
# =============================================================================
def draw_haori_back_t1(c):
    """Aba traseira do Haori com 5 dentes de serra brancos Dandara em micro-voxels."""
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    tz = c.torso_z

    trail, amp, freq = _motion(c)
    offs = cloth.chain_offsets(3, c.walk_timer, 0.5, trail, (px, py), amp=amp * 1.5, freq=freq)

    # Painel traseiro azul-celeste
    for i, (ox, oy, oz) in enumerate(offs):
        w = 0.270 + 0.020 * i
        _box(c, bx - fx * (0.110 + 0.035 * i) + ox - w / 2,
             by - fy * (0.110 + 0.035 * i) + oy - w / 2,
             tz + 0.140 - 0.075 * (i + 1) + oz, w, w * 0.70, 0.080, HAORI_ASAGI, texture="silk")

    # Barra inferior com 5 dentes triangulares Dandara brancos
    ox, oy, oz = offs[-1]
    back_z = tz + 0.140 - 0.075 * 3 + oz
    for i in range(5):
        lat = (i - 2.0) * 0.055
        dx_tri = bx - fx * 0.220 + px * lat + ox
        dy_tri = by - fy * 0.220 + py * lat + oy
        # Base e topo do triângulo dandara
        _box(c, dx_tri - 0.018, dy_tri - 0.018, back_z - 0.015, 0.036, 0.036, 0.040, DANDARA_WHITE, outline=False)
        _box(c, dx_tri - 0.010, dy_tri - 0.010, back_z + 0.020, 0.020, 0.020, 0.025, DANDARA_WHITE, outline=False)


# =============================================================================
# 4. MANGAS LARGAS DO HAORI COM DANDARA
# =============================================================================
def draw_sleeves_t1(c, arms):
    """Mangas amplas do haori com o padrão dente de serra branco Dandara nas barras."""
    trail, amp, freq = _motion(c)
    atk = math.sin(c.atk_progress * math.pi) if c.is_melee else 0.0

    for k, (s, e, side) in enumerate(arms):
        phase = 1.8 * k
        offs = cloth.chain_offsets(3, c.walk_timer, phase,
                                   (trail[0] - c.fx * 0.11 * atk, trail[1] - c.fy * 0.11 * atk),
                                   (c.px, c.py), amp=amp * 1.5, freq=freq)

        for i, (ox, oy, oz) in enumerate(offs):
            w = 0.090 + 0.020 * i
            _box(c, s[0] + ox - w / 2, s[1] + oy - w / 2, s[2] - 0.050 - 0.095 * (i + 1) + oz,
                 w, w, 0.095, HAORI_ASAGI, texture="silk")

        # Dentes de serra brancos Dandara na borda da manga
        ox, oy, oz = offs[-1]
        sleeve_bottom_z = s[2] - 0.050 - 0.095 * 3 + oz
        for j in range(3):
            lat = (j - 1.0) * 0.050
            dx_dand = s[0] + ox + c.fx * lat
            dy_dand = s[1] + oy + c.fy * lat
            _box(c, dx_dand - 0.018, dy_dand - 0.018, sleeve_bottom_z - 0.012, 0.036, 0.036, 0.038, DANDARA_WHITE, outline=False)


# =============================================================================
# 5. HAKAMA PREGUEADA, CANELEIRAS KYAHAN E TABI
# =============================================================================
def draw_legs_t1(c):
    """Hakama preta com pregas verticais, caneleiras kyahan com tiras brancas cruzadas e tabi."""
    for side in ("L", "R"):
        ld = c.legs_data[side]
        th_pos = ld["thigh"]
        sh_pos = ld["shin"]
        ft_pos = ld["foot"]

        # Coxa (Hakama larga e volumosa pregueada)
        _box(c, th_pos[0] - 0.075, th_pos[1] - 0.075, th_pos[2], 0.150, 0.150, 0.220, HAKAMA_BLACK, texture="pleats")
        _box(c, th_pos[0] - 0.065, th_pos[1] - 0.065, th_pos[2] + 0.050, 0.130, 0.130, 0.120, HAKAMA_FOLD, outline=False)

        # Joelho / Canela com Caneleira Kyahan preta
        _box(c, sh_pos[0] - 0.055, sh_pos[1] - 0.055, sh_pos[2], 0.110, 0.110, 0.190, KYAHAN_BLACK, texture="leather")
        # Tiras brancas cruzadas de amarração (Kyahan-himo)
        for i in range(3):
            _box(c, sh_pos[0] - 0.058, sh_pos[1] - 0.058, sh_pos[2] + 0.040 + i * 0.050, 0.116, 0.116, 0.014, KYAHAN_STRAP, outline=False)

        # Pé com Tabi branco e sandália Waraji
        _box(c, ft_pos[0] - 0.042 + c.fx * 0.030, ft_pos[1] - 0.042 + c.fy * 0.030,
             ft_pos[2], 0.084, 0.084, 0.050, TABI_WHITE, outline=True)
        # Sola de palha/madeira Waraji
        _box(c, ft_pos[0] - 0.042 + c.fx * 0.030, ft_pos[1] - 0.042 + c.fy * 0.030,
             ft_pos[2], 0.084, 0.084, 0.014, WARAJI_SOLE, outline=False)


# =============================================================================
# 6. KATANA DO GATOTSU E BAINHA SHINSENGUMI (MICRO-VOXELS T1)
# =============================================================================
def draw_katana_and_sheath_t1(c, arm_l, arm_r):
    """
    A Katana do Gatotsu:
    - Postura de estocada horizontal com lâmina apontada à frente pela mão esquerda.
    - Lâmina longa de aço (0.76m), tsuba dourada e cabo preto trançado.
    - Bainha laqueada negra no quadril esquerdo com acabamentos de ouro e sageo branco.
    """
    # 1. Bainha no quadril esquerdo
    k = (c.base_x + c.px * 0.145 + c.fx * 0.030, c.base_y + c.py * 0.145 + c.fy * 0.030, c.pelvis_z + 0.075)
    b = _norm((-c.fx * 0.84 + c.px * 0.28, -c.fy * 0.84 + c.py * 0.28, -0.28))

    # Corpo da bainha negra
    _obox(c, k, b, length=0.520, width=0.046, height=0.046, color=SAYA_LACQUER, texture="lacquer")
    # Bocal de ouro (Koiguchi)
    _obox(c, k, b, length=0.035, width=0.054, height=0.054, color=KATANA_GOLD, outline=False)
    # Ponteira de ouro (Kojiri)
    tip_sheath = (k[0] + b[0] * 0.490, k[1] + b[1] * 0.490, k[2] + b[2] * 0.490)
    _obox(c, tip_sheath, b, length=0.035, width=0.050, height=0.050, color=KATANA_GOLD, outline=False)
    # Cordão Sageo branco enrolado
    _obox(c, (k[0] + b[0] * 0.060, k[1] + b[1] * 0.060, k[2] + b[2] * 0.060), b,
          length=0.060, width=0.056, height=0.056, color=SAGEO_WHITE, outline=False)

    # 2. Katana longa empunhada no Gatotsu
    hand = (arm_l[0], arm_l[1], arm_l[2] - 0.060)

    # Direção de mira horizontal mortal do Gatotsu
    if c.is_melee:
        d = _norm((c.fx * 0.98, c.fy * 0.98, -0.06))
    else:
        d = _norm((c.fx * 0.96, c.fy * 0.96, -0.03))

    blade_len = 0.760

    # Cabo (Tsuka) empunhado pela mão esquerda junto ao peito
    _obox(c, hand[0] - d[0] * 0.180, hand[1] - d[1] * 0.180, hand[2] - d[2] * 0.180,
          d, length=0.180, width=0.038, height=0.038, color=TSUKA_ITO)
    # Pele de arraia branca nos losangos do cabo
    _obox(c, hand[0] - d[0] * 0.140, hand[1] - d[1] * 0.140, hand[2] - d[2] * 0.140,
          d, length=0.080, width=0.042, height=0.042, color=TSUKA_SAME, outline=False)

    # Guarda de disco circular de aço/ouro (Tsuba)
    _obox(c, hand[0], hand[1], hand[2], d, length=0.022, width=0.085, height=0.085, color=KATANA_GOLD, outline=True)

    # Lâmina longa reta de aço polido
    _obox(c, hand[0] + d[0] * 0.022, hand[1] + d[1] * 0.022, hand[2] + d[2] * 0.022,
          d, length=blade_len, width=0.038, height=0.016, color=STEEL_BLADE, outline=False)
    # Gume cortante reflexivo branco
    _obox(c, hand[0] + d[0] * 0.022, hand[1] + d[1] * 0.022, hand[2] + d[2] * 0.022,
          d, length=blade_len, width=0.012, height=0.020, color=STEEL_EDGE, outline=False)
    # Ponta da espada (Kissaki) afiada
    tip_k = (hand[0] + d[0] * (0.022 + blade_len), hand[1] + d[1] * (0.022 + blade_len), hand[2] + d[2] * (0.022 + blade_len))
    _obox(c, tip_k, d, length=0.050, width=0.018, height=0.012, color=STEEL_EDGE, outline=False)


# =============================================================================
# 7. RENDERIZADOR COMPLETO DE SAITOU T1
# =============================================================================
def render_saitou_t1(c):
    """Renderiza Saitou na Técnica 1 (Micro-voxels & Texturas Procedurais Ricas)."""
    # 1. Pernas, hakama e kyahan
    draw_legs_t1(c)

    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    if c.state == "ATTACK":
        p = c.atk_progress
        reach = 0.28 + 0.35 * p
        arm_l = (bx + fx * reach + px * 0.04, by + fy * reach + py * 0.04, tz + 0.18)
        arm_r = (bx - fx * 0.05 - px * 0.12, by - fy * 0.05 - py * 0.12, tz + 0.20)
    elif c.state == "INTRO":  # Concept Iconic Pose
        arm_l = (bx + fx * 0.26 + px * 0.05, by + fy * 0.26 + py * 0.05, tz + 0.19)
        arm_r = (bx + fx * 0.08 - px * 0.07, by + fy * 0.08 - py * 0.07, tz + 0.25)
    else:  # IDLE
        arm_l = (bx + fx * 0.22 + px * 0.06, by + fy * 0.22 + py * 0.06, tz + 0.17)
        arm_r = (bx + fx * 0.06 - px * 0.08, by + fy * 0.06 - py * 0.08, tz + 0.23)

    sh_l = (bx - px * 0.14, by - py * 0.14, tz + 0.20)
    sh_r = (bx + px * 0.14, by + py * 0.14, tz + 0.20)

    from src.isometric.iso_math import rotate_xy
    def depth(x, y):
        rx, ry = rotate_xy(x, y, getattr(c, "azimuth", 0.0))
        return rx + ry

    d_torso = depth(bx, by)
    d_arm_l = depth(arm_l[0], arm_l[1])
    d_arm_r = depth(arm_r[0], arm_r[1])
    d_back = depth(bx - fx * 0.15, by - fy * 0.15)

    back_elems = []
    front_elems = []

    # Aba traseira do haori com dandara
    elem_back = (d_back, lambda: draw_haori_back_t1(c))
    (back_elems if d_back < d_torso else front_elems).append(elem_back)

    # Braço esquerdo e manga (com a katana empunhada)
    def draw_left_arm_and_sword():
        draw_sleeves_t1(c, [(sh_l, arm_l, -1.0)])
        draw_katana_and_sheath_t1(c, arm_l, arm_r)

    elem_l = (d_arm_l, draw_left_arm_and_sword)
    (back_elems if d_arm_l < d_torso else front_elems).append(elem_l)

    # Braço direito e manga
    elem_r = (d_arm_r, lambda: draw_sleeves_t1(c, [(sh_r, arm_r, 1.0)]))
    (back_elems if d_arm_r < d_torso else front_elems).append(elem_r)

    # 1. Elementos atrás do tronco
    back_elems.sort(key=lambda item: item[0])
    for _, fn in back_elems:
        fn()

    # 2. Haori frontal e Quimono
    draw_haori_and_torso_t1(c)

    # 3. Elementos à frente do tronco
    front_elems.sort(key=lambda item: item[0])
    for _, fn in front_elems:
        fn()

    # 4. Cabeça e Chonmage
    draw_head_t1(c)
