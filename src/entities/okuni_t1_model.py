"""
src/entities/okuni_t1_model.py - Okuni (Técnica 1: Micro-voxels e Texturas Procedurais Ricas)

Evolução de alta fidelidade visual da Dançarina Kabuki baseada diretamente
na arte conceitual original (okuni_concept.jpg):
  - Rosto kabuki refinado: maquiagem branca oshiroi, kumadori vermelho ao redor dos olhos,
    delineado afiado com reflexo nos olhos, lábios carmesim laqueados e rubor nas têmporas.
  - Penteado Taka-shimada laqueado: pente dourado kushi, fita de seda vermelha kanoko,
    três agulhas kanzashi douradas em leque e pingentes bira-bira com borlas dinâmicas.
  - Tronco e Quimono sólido: volume contínuo sem lacunas anatômicas da cintura ao pescoço,
    decote em V com colarinho branco duplo e gola dourada, kamon floral no peito e ombros.
  - Faixa Obi cerimonial: obi largo ouro/preto com cordão trançado obijime e broche obidome,
    laço musubi volumoso nas costas com profundidade dinâmica ordenada.
  - Saia e Cauda Uchikake: drapeado em camadas com bainha fuki acolchoada pesada no solo.
  - Leques de Aço Tessen: varetas reforçadas com lâminas afiadas, borlas nos rebites e emblema solar.
  - Ordenação correta por Profundidade da Câmera (Painter's Algorithm 360°):
    mangas e braços atrás do tronco são desenhados ANTES do tronco, e mangas à frente
    são desenhadas DEPOIS do tronco, garantindo oclusão perfeita em qualquer ângulo de rotação!
"""
import math
import pygame

from src.config import COLOR_GOLD, COLOR_KABUKI_WHITE, COLOR_WHITE, COLOR_BLACK
from src.isometric import cloth
from src.isometric.iso_math import rotate_xy
from src.isometric.voxel_renderer import draw_oriented_voxel_box, draw_voxel_box

# =============================================================================
# PALETA REFINADA DO CONCEPT ART (OKUNI T1)
# =============================================================================
CRIMSON_ROYAL = (184, 26, 42)      # Carmesim nobre do quimono principal
CRIMSON_DARK  = (128, 16, 32)      # Sombra e camadas inferiores do quimono
CRIMSON_DEEP  = (88, 12, 24)       # Forro interno e cauda acolchoada do quimono
CRIMSON_ACCENT= (220, 38, 58)      # Realces vibrantes de dobras e laços

GOLD_BRIGHT   = (242, 202, 72)     # Ouro polido dos kanzashi e brocados
GOLD_DEEP     = (182, 142, 48)     # Ouro sombreado de relevo e cordões
GOLD_EMBROID  = (214, 172, 60)     # Fio de bordado dourado nas barras

KABUKI_WHITE  = (252, 250, 246)    # Maquiagem branca pura de pó de arroz (oshiroi)
BLUSH_RED     = (224, 76, 92)      # Rubor suave das têmporas / maçãs do rosto
EYE_BENI      = (204, 32, 54)      # Vermelho teatral kumadori ao redor dos olhos
EYE_PUPIL     = (20, 18, 24)       # Delineador e pupila preta carvão
EYE_SPECULAR  = (255, 255, 255)    # Ponto de luz / brilho no olhar
LIP_CARMINE   = (212, 28, 52)      # Carmesim brilhante dos lábios
LIP_GLOSS     = (255, 120, 140)    # Ponto de reflexo do lábio

HAIR_LACQUER  = (18, 18, 22)       # Cabelo negro laqueado profundo
HAIR_SHEEN    = (42, 42, 54)       # Brilho sutil do penteado shimada

FAN_STEEL     = (220, 228, 240)    # Aço polido das varetas externas cortantes
FAN_RED       = (198, 30, 48)      # Papel laqueado carmesim do leque
FAN_GOLD      = (238, 196, 68)     # Sol nascente / arabescos no centro do leque

OBI_BLACK     = (28, 26, 32)       # Tecido negro de base do obi
OBI_GOLD      = (228, 188, 64)     # Padrão brocado do obi
OBI_CORD      = (195, 34, 46)      # Cordão trançado obijime
OBI_JEWEL     = (72, 184, 156)     # Broche de jade verde no fecho do obi


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
        return (-c.fx * 0.08, -c.fy * 0.08), 0.045, 7.2
    return (0.0, 0.0), 0.016, 1.8


def depth(c, x: float, y: float) -> float:
    """Profundidade na tela relativa à câmera orbital (maior = mais perto do observador)."""
    rx, ry = rotate_xy(x, y, getattr(c, "azimuth", 0.0))
    return rx + ry


# =============================================================================
# 1. CABEÇA, ROSTO KABUKI & JOIAS KANZASHI (MICRO-VOXELS T1)
# =============================================================================
def draw_head_t1(c):
    """
    Rosto kabuki refinado em micro-voxels:
    - Base de pó branco oshiroi com nuca esculpida em 'komata'.
    - Olhos com kumadori vermelho ao redor, delineado pontiagudo preto e ponto de luz especular.
    - Rubor suave nas maçãs do rosto.
    - Lábios com arco de cupido e ponto de brilho laqueado.
    - Pente dourado frontal kushi, três agulhas kanzashi em leque e pingentes bira-bira.
    - Fita kanoko vermelha na base do coque traseiro.
    """
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # Nuca elegante com recorte duplo tradicional japonês
    _box(c, bx - 0.038, by - 0.038, c.neck_z - 0.005, 0.076, 0.076, 0.075, KABUKI_WHITE, outline=False)
    # Recortes de pele natural na base da nuca (Komata)
    _box(c, bx - fx * 0.036 - 0.015, by - fy * 0.036 - 0.015, c.neck_z + 0.01, 0.03, 0.03, 0.04, (244, 218, 202), outline=False)

    # Volume crânio-facial base branco
    _box(c, bx - hw / 2 - 0.006, by - hw / 2 - 0.006, hz + 0.025, hw + 0.012, hw + 0.012, 0.145, KABUKI_WHITE)

    front = hw / 2 + 0.012

    # Rubor suave nas bochechas e têmporas (Sanbon-zome)
    for s in (-1.0, 1.0):
        cx = bx + fx * (front - 0.002) + px * 0.052 * s
        cy = by + fy * (front - 0.002) + py * 0.052 * s
        _box(c, cx - 0.016, cy - 0.016, hz + 0.065, 0.032, 0.032, 0.022, BLUSH_RED, outline=False)

    # Rosto teatral puro Kabuki Oshiroi com rubor suave nas têmporas
    # (Sem cubos saltados de olhos ou lábios para manter superfície facial limpa em 360°)

    # Penteado laqueado Taka-shimada
    _box(c, bx - 0.084, by - 0.084, hz + 0.138, 0.168, 0.168, 0.080, HAIR_LACQUER)
    _box(c, bx - 0.075, by - 0.075, hz + 0.165, 0.150, 0.150, 0.020, HAIR_SHEEN, outline=False)

    # Franja laqueada arredondada na testa
    _box(c, bx + fx * 0.052 - 0.052, by + fy * 0.052 - 0.052, hz + 0.148, 0.104, 0.104, 0.042, HAIR_LACQUER, outline=False)

    # Mechas laterais infladas (Bin)
    for s in (-1.0, 1.0):
        _box(c, bx + px * 0.090 * s - 0.024, by + py * 0.090 * s - 0.024, hz + 0.055, 0.048, 0.048, 0.130, HAIR_LACQUER, outline=False)

    # Coque volumoso traseiro arqueado (Tabo)
    _box(c, bx - fx * 0.105 - 0.060, by - fy * 0.105 - 0.060, hz + 0.075, 0.120, 0.120, 0.135, HAIR_LACQUER)
    # Coque superior em nó (Mage)
    _box(c, bx - 0.042, by - 0.042, hz + 0.218, 0.084, 0.084, 0.068, HAIR_LACQUER)

    # Fita vermelha de seda Kanoko na base do coque superior
    _box(c, bx - 0.048, by - 0.048, hz + 0.208, 0.096, 0.096, 0.018, CRIMSON_ACCENT, outline=False)

    # Pente dourado frontal ornamentado (Kushi)
    _obox(c, (bx + fx * 0.078 - px * 0.060, by + fy * 0.078 - py * 0.060, hz + 0.192),
          (px, py, 0.0), length=0.12, width=0.020, height=0.045, color=GOLD_BRIGHT, outline=False)
    for j in range(4):
        _box(c, bx + fx * 0.082 - px * (0.045 - j * 0.030), by + fy * 0.082 - py * (0.045 - j * 0.030),
             hz + 0.230, 0.012, 0.012, 0.012, GOLD_DEEP, outline=False)

    # Três agulhas Kanzashi douradas em leque de cada lado + pingentes Bira-Bira
    for s in (-1.0, 1.0):
        for j in range(3):
            d = _norm((px * s * (0.50 + 0.35 * j), py * s * (0.50 + 0.35 * j), 0.85 - 0.20 * j))
            _obox(c, (bx + px * 0.076 * s, by + py * 0.076 * s, hz + 0.170), d,
                  length=0.16 + 0.025 * j, width=0.013, height=0.013, color=GOLD_BRIGHT, outline=False)
            tip_x = bx + px * 0.076 * s + d[0] * (0.16 + 0.025 * j)
            tip_y = by + py * 0.076 * s + d[1] * (0.16 + 0.025 * j)
            tip_z = hz + 0.170 + d[2] * (0.16 + 0.025 * j)
            _box(c, tip_x - 0.010, tip_y - 0.010, tip_z - 0.010, 0.020, 0.020, 0.020, CRIMSON_ACCENT, outline=False)

        offs = cloth.chain_offsets(3, c.walk_timer, 0.8 * s,
                                   (-fx * (0.035 if c.is_moving else 0.0), -fy * (0.035 if c.is_moving else 0.0)),
                                   (px, py), amp=0.016, freq=5.8 if c.is_moving else 2.2)
        for i, (ox, oy, oz) in enumerate(offs):
            col = GOLD_BRIGHT if i % 2 == 0 else CRIMSON_ACCENT
            _box(c, bx + px * 0.21 * s + ox - 0.009, by + py * 0.21 * s + oy - 0.009,
                 hz + 0.135 - 0.045 * i + oz, 0.018, 0.018, 0.038, col, outline=False)


# =============================================================================
# 2. TRONCO SÓLIDO, QUIMONO BROCADO, GOLAS E OBI (SEM LACUNAS)
# =============================================================================
def draw_torso_t1(c):
    """
    Tronco anatômico e contínuo completo do quimono:
    - Bloco principal sólido do tronco cobrindo da cintura até a base do pescoço (sem buracos).
    - Peitoral e ombros de brocado carmesim estruturado.
    - Decote V duplo com gola interna branca (Haneri) e gola dourada brocada.
    - Kamon floral de crisântemo dourado no peito.
    - Faixa Obi larga na cintura com cordão trançado Obijime e broche de jade Obidome.
    """
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    tz = c.torso_z
    pz = c.pelvis_z

    # 1. Bloco volumétrico contínuo do quimono (conecta do quadril até a base do pescoço)
    torso_bottom = pz + 0.04
    torso_top = tz + 0.26
    torso_h = torso_top - torso_bottom
    _box(c, bx - 0.120, by - 0.090, torso_bottom, 0.240, 0.180, torso_h, CRIMSON_ROYAL, texture="silk")

    # 2. Busto e peitoral de brocado carmesim estruturado
    _box(c, bx - 0.125, by - 0.095, tz + 0.060, 0.250, 0.190, 0.180, CRIMSON_ROYAL, texture="brocade")

    # 3. Gola interna branca pura Haneri em V
    _box(c, bx - 0.045 + fx * 0.065, by - 0.045 + fy * 0.065, tz + 0.140, 0.090, 0.090, 0.120, (248, 246, 242), outline=False)
    # 4. Gola intermediária dourada brocada
    _box(c, bx - 0.052 + fx * 0.075, by - 0.052 + fy * 0.075, tz + 0.120, 0.104, 0.104, 0.105, GOLD_EMBROID, outline=False)

    # 5. Kamon floral dourado no peito
    _box(c, bx + fx * 0.095 - 0.025, by + fy * 0.095 - 0.025, tz + 0.145, 0.050, 0.050, 0.050, GOLD_BRIGHT, outline=False)
    _box(c, bx + fx * 0.100 - 0.012, by + fy * 0.100 - 0.012, tz + 0.158, 0.024, 0.024, 0.024, CRIMSON_ACCENT, outline=False)

    # 6. Faixa Obi cerimonial larga na cintura (envolve perfeitamente a junção quadril/tronco)
    _box(c, bx - 0.125, by - 0.095, pz + 0.040, 0.250, 0.190, 0.090, OBI_BLACK, texture="brocade")
    _box(c, bx - 0.120, by - 0.090, pz + 0.055, 0.240, 0.180, 0.060, OBI_GOLD, outline=False)

    # 7. Cordão trançado Obijime vermelho no centro do obi
    _box(c, bx + fx * 0.096 - 0.080, by + fy * 0.096 - 0.080, pz + 0.075, 0.160, 0.160, 0.020, OBI_CORD, outline=False)
    # Broche / fivela Obidome de jade no nó central
    _box(c, bx + fx * 0.104 - 0.022, by + fy * 0.104 - 0.022, pz + 0.070, 0.044, 0.044, 0.030, OBI_JEWEL, outline=True)
    _box(c, bx + fx * 0.108 - 0.010, by + fy * 0.108 - 0.010, pz + 0.076, 0.020, 0.020, 0.018, GOLD_BRIGHT, outline=False)


# =============================================================================
# 3. LAÇO DO OBI (MUSUBI NAS COSTAS)
# =============================================================================
def draw_bow_t1(c):
    """Laço cerimonial Tateya-musubi grande nas costas com asas diagonais e pontas balançantes."""
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    cx, cy, z = bx - fx * 0.145, by - fy * 0.145, c.torso_z + 0.015
    flap = math.sin(c.walk_timer * (7.2 if c.is_moving else 1.8)) * 0.030

    # Nó central do laço em ouro e seda negra
    _box(c, cx - 0.055, cy - 0.055, z, 0.110, 0.110, 0.155, GOLD_BRIGHT)
    _box(c, cx - 0.045, cy - 0.045, z + 0.020, 0.090, 0.090, 0.115, OBI_BLACK, outline=False)

    # Asas superiores diagonais do laço
    for s in (-1.0, 1.0):
        wing_dir = _norm((px * s, py * s, 0.22 + flap * 4.0))
        _obox(c, (cx + px * 0.045 * s, cy + py * 0.045 * s, z + 0.065), wing_dir,
              length=0.170, width=0.140, height=0.055, color=GOLD_DEEP, texture="brocade")
        _obox(c, (cx + px * (0.045 + wing_dir[0] * 0.15) * s, cy + py * (0.045 + wing_dir[1] * 0.15) * s,
                  z + 0.065 + wing_dir[2] * 0.15), wing_dir, length=0.030, width=0.145, height=0.058, color=CRIMSON_ACCENT, outline=False)

    # Duas caudas pendentes que balançam com a física de tecido
    trail, amp, freq = _motion(c)
    offs = cloth.chain_offsets(3, c.walk_timer, 0.45, trail, (px, py), amp=amp * 1.3, freq=freq, wind=cloth.wind_at(bx, by))
    for i, (ox, oy, oz) in enumerate(offs):
        col = GOLD_BRIGHT if i == 0 else (CRIMSON_DARK if i == 1 else OBI_BLACK)
        _box(c, cx - fx * 0.045 + ox - 0.038, cy - fy * 0.045 + oy - 0.038,
             z - 0.075 - 0.085 * i + oz, 0.076, 0.076, 0.095, col, outline=False)


# =============================================================================
# 4. SAIA E CAUDA UCHIKAKE EM CAMADAS
# =============================================================================
def draw_skirt_t1(c):
    """
    Saia comprida em 4 camadas de drapeado:
    - Camada 0: Cintura/quadril carmesim brocado.
    - Camada 1: Transição intermediária carmesim profundo.
    - Camada 2: Barra ampla drapeada com arrasto.
    - Bainha Fuki acolchoada pesada no solo com aro de ouro.
    - Cauda traseira estendida no chão.
    - Tabi branco e geta laqueada nos pés.
    """
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    trail, amp, freq = _motion(c)
    offs = cloth.chain_offsets(4, c.walk_timer, 0.0, trail, (px, py), amp=amp, freq=freq, wind=cloth.wind_at(bx, by))
    flare = 0.12 * c.lunge_curve
    top, bottom = c.pelvis_z + 0.04, c.base_z + 0.035
    h = (top - bottom) / 4.0

    widths = (c.pelvis_w + 0.04, c.pelvis_w + 0.08, c.pelvis_w + 0.12, c.pelvis_w + 0.16)
    colors = (CRIMSON_ROYAL, CRIMSON_ROYAL, CRIMSON_DARK, CRIMSON_DEEP)

    # 1. Bainha pesada acolchoada Fuki no solo com acabamento dourado
    hem_w = widths[3] + 0.06 + flare
    ox, oy, _ = offs[3]
    _box(c, bx - hem_w / 2 + ox, by - hem_w * 0.45 + oy, c.base_z + 0.010, hem_w, hem_w * 0.90, 0.035, GOLD_BRIGHT, outline=False)
    _box(c, bx - hem_w / 2 + ox - 0.010, by - hem_w * 0.45 + oy - 0.010, c.base_z + 0.005, hem_w + 0.020, (hem_w + 0.020) * 0.90, 0.015, CRIMSON_DEEP, outline=False)

    # 2. Camadas da saia (de baixo para cima)
    for i in (3, 2, 1, 0):
        w = widths[i] + flare * (i + 1) / 4.0
        ox, oy, _ = offs[i]
        _box(c, bx - w / 2 + ox, by - w * 0.45 + oy, top - h * (i + 1), w, w * 0.90, h, colors[i], texture="silk")
        if i > 0:
            wb = w + 0.014
            _box(c, bx - wb / 2 + ox, by - wb * 0.45 + oy, top - h * i - 0.020, wb, wb * 0.90, 0.024, GOLD_EMBROID, outline=False)

    # 3. Cauda traseira estendida no tablado (Uchikake)
    ox, oy, _ = offs[3]
    _box(c, bx - fx * 0.22 + ox * 1.3 - 0.10, by - fy * 0.22 + oy * 1.3 - 0.10, c.base_z + 0.010, 0.20, 0.20, 0.035, CRIMSON_DEEP, outline=False)
    _box(c, bx - fx * 0.26 + ox * 1.4 - 0.08, by - fy * 0.26 + oy * 1.4 - 0.08, c.base_z + 0.006, 0.16, 0.16, 0.025, GOLD_BRIGHT, outline=False)

    # 4. Tabi branco e geta com tira vermelha
    for side in ("L", "R"):
        fxp, fyp, fzp = c.legs_data[side]["foot"]
        _box(c, fxp - 0.042 + fx * 0.065, fyp - 0.042 + fy * 0.065, fzp, 0.084, 0.084, 0.042, (246, 244, 240), outline=True)
        _box(c, fxp - 0.042 + fx * 0.065, fyp - 0.042 + fy * 0.065, fzp, 0.084, 0.084, 0.014, (35, 30, 36), outline=False)
        _box(c, fxp - 0.016 + fx * 0.095, fyp - 0.016 + fy * 0.095, fzp + 0.028, 0.032, 0.032, 0.018, CRIMSON_ACCENT, outline=False)


# =============================================================================
# 5. LEQUES DE COMBATE TESSEN
# =============================================================================
def _open_fan_t1(c, hand, spine, normal, spread=1.22, length=0.27, ribs=9):
    """Leque Tessen de duelo de alta fidelidade com 9 costelas de aço e lâminas afiadas."""
    spine, normal = _norm(spine), _norm(normal)
    tangent = _norm(_cross(normal, spine))
    hx, hy, hz = hand

    dirs = []
    for i in range(ribs):
        a = -spread + 2.0 * spread * i / (ribs - 1)
        dirs.append((spine[0] * math.cos(a) + tangent[0] * math.sin(a),
                     spine[1] * math.cos(a) + tangent[1] * math.sin(a),
                     spine[2] * math.cos(a) + tangent[2] * math.sin(a)))

    panel_w = 2.0 * length * math.sin(spread / (ribs - 1)) * 0.98

    # Painéis de tecido/papel vermelho
    for i in range(ribs - 1):
        mid = _norm((dirs[i][0] + dirs[i + 1][0], dirs[i][1] + dirs[i + 1][1], dirs[i][2] + dirs[i + 1][2]))
        _obox(c, (hx + mid[0] * 0.035, hy + mid[1] * 0.035, hz + mid[2] * 0.035),
              mid, length=length * 0.95, width=panel_w, height=0.009, color=FAN_RED, up=normal, outline=False)

    # Emblema solar dourado
    mid_spine = dirs[ribs // 2]
    _obox(c, (hx + mid_spine[0] * 0.12, hy + mid_spine[1] * 0.12, hz + mid_spine[2] * 0.12),
          mid_spine, length=0.075, width=0.075, height=0.012, color=FAN_GOLD, up=normal, outline=False)

    # Varetas de aço com pontas afiadas
    for i, d in enumerate(dirs):
        is_outer = (i == 0 or i == ribs - 1)
        w = 0.020 if is_outer else 0.012
        col = FAN_STEEL if is_outer else GOLD_BRIGHT
        _obox(c, (hx, hy, hz), d, length=length, width=w, height=0.015, color=col, up=normal, outline=False)
        _obox(c, (hx + d[0] * length, hy + d[1] * length, hz + d[2] * length), d,
              length=0.035, width=0.016, height=0.006, color=(250, 252, 255), up=normal, outline=False)

    # Borla de seda carmesim e ouro pendurada no rebite (Kaname)
    _box(c, hx - 0.015, hy - 0.015, hz - 0.015, 0.030, 0.030, 0.030, GOLD_BRIGHT, outline=False)
    _obox(c, (hx, hy, hz), (0.0, 0.0, -1.0), length=0.090, width=0.018, height=0.018, color=CRIMSON_ACCENT, outline=False)


def _closed_fan_t1(c, hand, direction):
    """Leque fechado compacto pronto na cintura."""
    direction = _norm(direction)
    hx, hy, hz = hand
    _obox(c, (hx, hy, hz), direction, length=0.250, width=0.048, height=0.036, color=FAN_RED, outline=True)
    _obox(c, (hx + direction[0] * 0.20, hy + direction[1] * 0.20, hz + direction[2] * 0.20),
          direction, length=0.055, width=0.052, height=0.040, color=GOLD_BRIGHT, outline=False)
    _obox(c, (hx, hy, hz), (0.0, 0.0, -1.0), length=0.075, width=0.016, height=0.016, color=CRIMSON_ACCENT, outline=False)


# =============================================================================
# 6. DESENHO INDIVIDUAL DE BRAÇO, MANGA E LEQUE (COM ORDENAÇÃO DE PROFUNDIDADE)
# =============================================================================
def draw_single_arm_and_sleeve_t1(c, arm_pos, side, is_open):
    """
    Desenha uma manga furisode individual, o braço e o leque empunhado.
    Permite ordenação Painter's Algorithm perfeita de 360° em relação ao tronco!
    """
    ax, ay, az = arm_pos
    trail, amp, freq = _motion(c)
    atk = math.sin(c.atk_progress * math.pi) if c.is_melee else 0.0
    phase = 1.75 if side > 0 else 0.0

    # Ombreira e braço anatômico conectando o ombro à mão
    sh_x = c.base_x + c.px * side * c.sh_span
    sh_y = c.base_y + c.py * side * c.sh_span
    sh_z = c.torso_z + 0.19
    arm_dir = (ax - sh_x, ay - sh_y, az - sh_z)
    arm_len = math.hypot(arm_dir[0], arm_dir[1], arm_dir[2])
    _obox(c, (sh_x, sh_y, sh_z), arm_dir, length=arm_len, width=0.065, height=0.065, color=CRIMSON_ROYAL, texture="silk")

    # Mão branca esculpida
    _box(c, ax - 0.025, ay - 0.025, az - 0.025, 0.050, 0.050, 0.050, KABUKI_WHITE, outline=False)

    # Manga furisode esvoaçante pendurada no braço
    offs = cloth.chain_offsets(4, c.walk_timer, phase,
                               (trail[0] - c.fx * 0.12 * atk, trail[1] - c.fy * 0.12 * atk),
                               (c.px, c.py), amp=amp * 1.6, freq=freq, wind=cloth.wind_at(ax, ay))
    for i, (ox, oy, oz) in enumerate(offs):
        w = 0.075 + 0.016 * i
        color = CRIMSON_ROYAL if i < 2 else CRIMSON_DARK
        _box(c, ax + ox - w / 2, ay + oy - w / 2, az - 0.055 - 0.095 * (i + 1) + oz,
             w, w, 0.095, color, texture="silk")
        # Forro interno escuro
        _box(c, ax + ox - (w - 0.020) / 2, ay + oy - (w - 0.020) / 2, az - 0.055 - 0.095 * (i + 1) + oz + 0.010,
             w - 0.020, w - 0.020, 0.075, CRIMSON_DEEP, outline=False)

    # Franja e brocado dourado na barra da manga
    ox, oy, oz = offs[-1]
    _box(c, ax + ox - 0.060, ay + oy - 0.060, az - 0.055 - 0.420 + oz, 0.120, 0.120, 0.030, GOLD_BRIGHT, outline=False)
    _box(c, ax + ox - 0.055, ay + oy - 0.055, az - 0.055 - 0.435 + oz, 0.110, 0.110, 0.015, GOLD_DEEP, outline=False)

    # Leque nesta mão
    if is_open:
        # Leque aberto erguido com orgulho junto ao rosto
        spine = (c.px * (-0.22 if side > 0 else 0.22) + c.fx * 0.16,
                 c.py * (-0.22 if side > 0 else 0.22) + c.fy * 0.16, 1.0)
        _open_fan_t1(c, arm_pos, spine, (-c.fy, c.fx, 0.0))
    else:
        # Leque fechado compacto na cintura
        d_fan = _norm((c.fx * 0.36 + c.px * 0.62 * side, c.fy * 0.36 + c.py * 0.62 * side, -0.10))
        _closed_fan_t1(c, arm_pos, d_fan)


# =============================================================================
# 7. POSES DE BRAÇOS (IDLE, CONCEPT, ATTACK)
# =============================================================================
def idle_arms_t1(base_x, base_y, tz, fx, fy, px, py):
    arm_r = (base_x + fx * 0.08 - px * 0.15, base_y + fy * 0.08 - py * 0.15, tz + 0.31)
    arm_l = (base_x + fx * 0.12 + px * 0.08, base_y + fy * 0.12 + py * 0.08, tz - 0.02)
    return arm_l, arm_r


def concept_pose_arms_t1(base_x, base_y, tz, fx, fy, px, py):
    arm_r = (base_x + fx * 0.05 - px * 0.18, base_y + fx * 0.05 - py * 0.18, tz + 0.34)
    arm_l = (base_x + fx * 0.14 + px * 0.10, base_y + fy * 0.14 + py * 0.10, tz + 0.02)
    return arm_l, arm_r


def attack_arms_t1(c):
    bx, by, tz, fx, fy, px, py, p = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py, c.atk_progress
    cross = 1.0 - max(0.0, min(1.0, p / 0.22))
    sweep = max(0.0, min(1.0, (p - 0.22) / 0.55))
    reach = 0.14 + 0.22 * sweep
    lateral = (-0.06 * cross) + 0.38 * sweep
    z = tz + 0.23 - 0.06 * sweep
    arm_l = (bx + fx * reach + px * lateral, by + fy * reach + py * lateral, z)
    arm_r = (bx + fx * reach - px * lateral, by + fy * reach - py * lateral, z + 0.025)
    return arm_l, arm_r


# =============================================================================
# 8. RENDERIZADOR COMPLETO COM ORDENAÇÃO DE PROFUNDIDADE 360° (PAINTER'S ALGORITHM)
# =============================================================================
def render_okuni_t1(c):
    """
    Desenha Okuni T1 com ordenação perfeita de profundidade por azimute da câmera:
    - O tronco é esculpido sem lacunas anatômicas da cintura ao pescoço.
    - As mangas e braços que estão atrás do tronco na perspectiva da câmera são
      desenhados ANTES do tronco, ficando devidamente ocluídos na rotação de 360°!
    """
    # 1. Poses dos braços e leques
    if c.state == "ATTACK":
        arm_l, arm_r = attack_arms_t1(c)
        l_open, r_open = True, True
    elif c.state == "INTRO":  # Concept Iconic Pose
        arm_l, arm_r = concept_pose_arms_t1(c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py)
        l_open, r_open = False, True
    else:  # IDLE
        arm_l, arm_r = idle_arms_t1(c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py)
        l_open, r_open = False, True

    # 2. Profundidades calculadas para ordenação na câmera
    d_torso = depth(c, c.base_x, c.base_y)
    d_arm_l = depth(c, arm_l[0], arm_l[1])
    d_arm_r = depth(c, arm_r[0], arm_r[1])
    bow_pos = (c.base_x - c.fx * 0.145, c.base_y - c.fy * 0.145)
    d_bow = depth(c, bow_pos[0], bow_pos[1])

    # Elementos atrás do tronco (depth < d_torso) e à frente (depth >= d_torso)
    back_elements = []
    front_elements = []

    # Braço e manga esquerda (side = 1.0)
    elem_l = (d_arm_l, lambda: draw_single_arm_and_sleeve_t1(c, arm_l, side=1.0, is_open=l_open))
    (back_elements if d_arm_l < d_torso else front_elements).append(elem_l)

    # Braço e manga direita (side = -1.0)
    elem_r = (d_arm_r, lambda: draw_single_arm_and_sleeve_t1(c, arm_r, side=-1.0, is_open=r_open))
    (back_elements if d_arm_r < d_torso else front_elements).append(elem_r)

    # Laço Musubi nas costas
    elem_bow = (d_bow, lambda: draw_bow_t1(c))
    (back_elements if d_bow < d_torso else front_elements).append(elem_bow)

    # 3. Desenha elementos que estão ATRÁS do tronco (menor profundidade primeiro)
    back_elements.sort(key=lambda item: item[0])
    for _, draw_fn in back_elements:
        draw_fn()

    # 4. Saia longa em camadas e cauda no tablado
    draw_skirt_t1(c)

    # 5. Tronco sólido do quimono, busto e faixa Obi (cobre o que estiver atrás)
    draw_torso_t1(c)

    # 6. Desenha elementos que estão À FRENTE do tronco (menor para maior profundidade)
    front_elements.sort(key=lambda item: item[0])
    for _, draw_fn in front_elements:
        draw_fn()

    # 7. Cabeça, maquiagem teatral e penteado shimada
    draw_head_t1(c)
