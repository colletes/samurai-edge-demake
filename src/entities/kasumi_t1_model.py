"""
src/entities/kasumi_t1_model.py - Kasumi (Técnica 1: Micro-voxels e Texturas Procedurais Ricas)

Evolução de alta fidelidade visual da Kunoichi da Névoa baseada diretamente
na arte conceitual original (kasumi_concept.jpg):
  - Rosto de assassina shinobi: máscara tática cinza-escura/preta, olhos azuis-gelo afiados
    com delineador kunoichi, pupila e ponto especular; cabelo prateado com coque alto,
    franja assimétrica e mechas laterais esvoaçantes.
  - Cachecol longo da névoa: enrolado no pescoço com cauda longa em 5 gomos que esvoaça
    para trás com física de vento em tecido knit/seda.
  - Colete-espartilho tático: couro negro com textura procedural, 4 fivelas cromadas
    horizontais com ilhoses, tiras de ajuste cruzadas e decote de malha tática.
  - Cinto e utilidades: cinto com fivela polida, bolsas de pó de fumaça, coldres duplos
    nas coxas e bomba cerâmica kemuridama com pavio laranja.
  - Membros e armadura: ombreiras cromadas em camadas, manoplas com braçadeiras de placas,
    perneiras justas cinza-azuladas com joelheiras cromadas chanfradas e botas reforçadas.
  - Adaga Shinobi: lâmina de aço polido com sulco fuller e gume reflexivo espelhado.
"""
import math
import pygame

from src.config import COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
from src.isometric import cloth
from src.isometric.voxel_renderer import draw_oriented_voxel_box, draw_voxel_box

# =============================================================================
# PALETA REFINADA DO CONCEPT ART (KASUMI T1)
# =============================================================================
HAIR_SILVER     = (222, 228, 238)   # Prateado luminoso do cabelo
HAIR_SHADE      = (164, 174, 192)   # Mechas de sombra do cabelo
HAIR_TIE        = (36, 40, 50)      # Fita escura prendendo o coque

MASK_DARK       = (28, 30, 36)      # Máscara tática de tecido respirável
MASK_SEAM       = (46, 50, 62)      # Borda e costura da máscara
SKIN_PALE       = (242, 222, 210)   # Pele clara exposta ao redor dos olhos e colo
SKIN_SHADOW     = (210, 186, 174)

EYE_ICE_BLUE    = (108, 168, 235)   # Azul-gelo penetrante da íris
EYE_PUPIL       = (18, 20, 26)      # Pupila e delineador preto afiado
EYE_SPECULAR    = (255, 255, 255)   # Ponto de reflexo no olho
BROW_SLATE      = (115, 125, 142)   # Sobrancelha fina cinza

SCARF_MIST      = (162, 170, 184)   # Cachecol cinza da névoa
SCARF_DARK      = (118, 126, 140)   # Sombra das dobras do cachecol
SCARF_HIGHLIGHT = (204, 212, 226)   # Realce de luz no tecido

CORSET_LEATHER  = (28, 30, 36)      # Couro preto do colete-espartilho
CORSET_SEAM     = (48, 52, 62)      # Costuras verticais
BUCKLE_CHROME   = (228, 234, 244)   # Fivelas metálicas cromadas brilhantes
BUCKLE_DARK     = (130, 138, 152)   # Sombra da fivela

PANTS_TACTICAL  = (168, 178, 198)   # Tecido cinza-azulado justo das pernas
PANTS_SHADOW    = (112, 122, 142)

ARMOR_CHROME    = (195, 205, 220)   # Placas metálicas de armadura
ARMOR_LIGHT     = (240, 246, 255)   # Chanfro reluzente de cromo
ARMOR_DARK      = (115, 125, 140)   # Sombra de oclusão das placas

BLADE_STEEL     = (228, 238, 250)   # Aço polido da adaga
BLADE_EDGE      = (255, 255, 255)   # Gume cortante de navalha
BLADE_FULLER    = (140, 150, 168)   # Sulco central de sangue

BOMB_SHELL      = (34, 34, 40)      # Cerâmica da bomba de fumaça
BOMB_FUSE       = (255, 145, 50)    # Pavio incandescente de pólvora
LEATHER_STRAP   = (48, 42, 38)      # Tiras e coldres de couro marrom-escuro


def _box(c, x, y, z, w, d, h, color, outline=True, texture=None):
    draw_voxel_box(c.surface, c.camera, x, y, z, w, d, h, color, outline=outline, alpha=c.alpha, texture=texture)


def _obox(c, ox, oy, oz, direction, length, width, height, color, up=(0.0, 0.0, 1.0), outline=True, texture=None):
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
        return (-c.fx * 0.09, -c.fy * 0.09), 0.05, 8.0
    return (0.0, 0.0), 0.018, 2.0


# =============================================================================
# 1. CABEÇA, MÁSCARA SHINOBI E CABELO PRATEADO (MICRO-VOXELS T1)
# =============================================================================
def draw_head_t1(c):
    """
    Rosto tático de Kunoichi em micro-voxels:
    - Máscara ninja preta cobrindo nariz, boca e queixo.
    - Olhos azuis-gelo nítidos com delineado afiado de gata e brilho especular.
    - Cabelo prateado luminoso com coque alto, franja assimétrica e mechas laterais.
    - Cachecol da névoa volumoso com ponta longa que drapeja ao vento.
    """
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # 1. Pescoço anatômico contínuo conectando o colarinho à cabeça (sem cabeça flutuando!)
    _box(c, bx - 0.038, by - 0.038, c.neck_z - 0.040, 0.076, 0.076, 0.090, SKIN_PALE, outline=False)

    # 2. Volume do crânio / rosto base contínuo
    _box(c, bx - hw / 2, by - hw / 2, hz - 0.010, hw, hw, 0.165, SKIN_PALE)

    from src.isometric.iso_math import rotate_xy
    rx, ry = rotate_xy(c.fx, c.fy, getattr(c, "azimuth", 0.0))
    is_facing = (rx + ry > -0.15)

    if is_facing:
        # Apenas desenha traços faciais se o rosto estiver voltado para a câmera!
        front = hw / 2 + 0.006

        # Máscara facial ninja preta cobrindo queixo, boca e nariz
        _box(c, bx + fx * 0.030 - 0.060, by + fy * 0.030 - 0.060, hz - 0.010, 0.120, 0.120, 0.082, MASK_DARK, texture="leather")
        _box(c, bx + fx * 0.035 - 0.055, by + fy * 0.035 - 0.055, hz + 0.066, 0.110, 0.110, 0.014, MASK_SEAM, outline=False)

        # Rosto tático com máscara shinobi e pele limpa (sem cubos saltados de olhos em 360°)
        pass
    else:
        # Quando de costas para a câmera, desenha o volume sólido do cabelo traseiro cobrindo a nuca
        _box(c, bx - fx * 0.035 - 0.080, by - fy * 0.035 - 0.080, hz + 0.015, 0.160, 0.160, 0.145, HAIR_SILVER, outline=False)

    # Cabelo prateado com mechas e reflexos
    # Calota principal
    _box(c, bx - 0.082, by - 0.082, hz + 0.130, 0.164, 0.164, 0.082, HAIR_SILVER)
    _box(c, bx - 0.072, by - 0.072, hz + 0.155, 0.144, 0.144, 0.024, HAIR_SHADE, outline=False)

    # Franja assimétrica caída sobre a testa e o olho esquerdo
    for s in (-1.0, 0.0, 1.0):
        fx_len = 0.040 + 0.015 * (s + 1.0)
        _box(c, bx + fx * 0.055 + px * 0.030 * s - 0.015,
             by + fy * 0.055 + py * 0.030 * s - 0.015,
             hz + 0.115 - 0.010 * s, 0.030, 0.030, fx_len, HAIR_SILVER, outline=False)

    # Mechas laterais esvoaçantes que emolduram a mandíbula
    trail, amp, freq = _motion(c)
    for s in (-1.0, 1.0):
        offs = cloth.chain_offsets(2, c.walk_timer, 0.7 * s, trail, (px, py), amp=0.018, freq=6.0 if c.is_moving else 2.2)
        for i, (ox, oy, oz) in enumerate(offs):
            _box(c, bx + px * 0.080 * s + ox - 0.015, by + py * 0.080 * s + oy - 0.015,
                 hz + 0.060 - 0.060 * i + oz, 0.030, 0.030, 0.070, HAIR_SILVER, outline=False)

    # Coque ninja traseiro alto preso por fita escura
    _box(c, bx - fx * 0.025 - 0.045, by - fy * 0.025 - 0.045, hz + 0.200, 0.090, 0.090, 0.080, HAIR_SILVER)
    _box(c, bx - fx * 0.025 - 0.048, by - fy * 0.025 - 0.048, hz + 0.194, 0.096, 0.096, 0.018, HAIR_TIE, outline=False)

    # Cachecol volumoso da névoa no pescoço
    nz = c.neck_z
    _box(c, bx - 0.070, by - 0.070, nz - 0.025, 0.140, 0.140, 0.075, SCARF_MIST, texture="knit")
    _box(c, bx - 0.062, by - 0.062, nz + 0.010, 0.124, 0.124, 0.025, SCARF_HIGHLIGHT, outline=False)

    # Ponta longa do cachecol esvoaçando para trás com física fluida
    root = (bx - fx * 0.07, by - fy * 0.07, nz + 0.01)
    offs_scarf = cloth.chain_offsets(5, c.walk_timer, 0.35,
                                      (-fx * (0.08 if c.is_moving else 0.02), -fy * (0.08 if c.is_moving else 0.02)),
                                      (px, py), amp=0.035, freq=5.5 if c.is_moving else 2.5, wind_gain=0.08)
    last = root
    for i, (ox, oy, oz) in enumerate(offs_scarf):
        target = (root[0] - fx * 0.075 * (i + 1) + px * 0.045 + ox,
                  root[1] - fy * 0.075 * (i + 1) + py * 0.045 + oy,
                  root[2] - 0.025 * (i + 1) + oz)
        col = SCARF_MIST if i % 2 == 0 else SCARF_DARK
        w = max(0.028, 0.055 - 0.006 * i)
        _obox(c, last[0], last[1], last[2], (target[0] - last[0], target[1] - last[1], target[2] - last[2]),
              length=math.hypot(target[0] - last[0], target[1] - last[1], target[2] - last[2]),
              width=w, height=0.022, color=col, outline=(i == 0))
        last = target


# =============================================================================
# 2. TRONCO, ESPARTILHO TÁTICO E FIVELAS CROMADAS (MICRO-VOXELS T1)
# =============================================================================
def draw_torso_t1(c):
    """
    Colete-espartilho tático ajustado:
    - Base de couro negro justa com costuras e dobras anatômicas.
    - 4 fivelas metálicas cromadas horizontais alinhadas na frente.
    - Tiras de couro cruzadas de aperto lateral.
    - Gola interna e proteção de malha acoplada.
    """
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    # Colete de couro negro principal
    _box(c, bx - 0.115, by - 0.090, tz - 0.008, 0.230, 0.180, 0.210, CORSET_LEATHER, texture="leather")

    # Decote/placa peitoral com acabamento cromado suave
    _box(c, bx - 0.085, by - 0.070, tz + 0.190, 0.170, 0.140, 0.045, ARMOR_CHROME, texture="brushed_metal")
    # Pequeno recorte de pele no colo
    _box(c, bx + fx * 0.055 - 0.035, by + fy * 0.055 - 0.035, tz + 0.210, 0.070, 0.050, 0.035, SKIN_PALE, outline=False)

    # 4 Fivelas cromadas brilhantes na frente do espartilho
    front = 0.092
    for i in range(4):
        fz = tz + 0.025 + i * 0.042
        # Barra de couro da tira
        _box(c, bx + fx * front - 0.050, by + fy * front - 0.050, fz - 0.003, 0.100, 0.100, 0.015, LEATHER_STRAP, outline=False)
        # Fivela cromada central retangular
        _box(c, bx + fx * (front + 0.005) - 0.025, by + fy * (front + 0.005) - 0.025, fz - 0.005, 0.050, 0.050, 0.020, BUCKLE_CHROME, outline=False)
        # Lingueta / pino escuro da fivela
        _box(c, bx + fx * (front + 0.008) - 0.006, by + fy * (front + 0.008) - 0.006, fz - 0.002, 0.012, 0.012, 0.014, BUCKLE_DARK, outline=False)

    # Tiras de couro diagonais de reforço lateral
    for s in (-1.0, 1.0):
        start = (bx + px * 0.070 * s + fx * front, by + py * 0.070 * s + fy * front, tz + 0.190)
        end = (bx + px * 0.105 * s + fx * front, by + py * 0.105 * s + fy * front, tz + 0.015)
        d = (end[0] - start[0], end[1] - start[1], end[2] - start[2])
        _obox(c, start[0], start[1], start[2], d, length=math.hypot(d[0], d[1], d[2]),
              width=0.024, height=0.014, color=LEATHER_STRAP, outline=False)


# =============================================================================
# 3. CINTO DE UTILIDADES, COLDRES E BOMBA DE FUMAÇA
# =============================================================================
def draw_belt_t1(c):
    """
    Cinto tático reforçado com coldres de adagas e bombas kemuridama:
    - Cinto largo de couro com fivela retangular cromada.
    - Bolsas de munição nas laterais.
    - Bomba cerâmica de fumaça preta com pavio laranja incandescente.
    - Coldres de couro nas duas coxas.
    """
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z

    # Cinto de couro
    _box(c, bx - 0.110, by - 0.085, z + 0.060, 0.220, 0.170, 0.070, LEATHER_STRAP, texture="leather")
    # Fivela central cromada grande
    _box(c, bx + fx * 0.092 - 0.030, by + fy * 0.092 - 0.030, z + 0.065, 0.060, 0.060, 0.055, BUCKLE_CHROME, outline=True)
    _box(c, bx + fx * 0.096 - 0.015, by + fy * 0.096 - 0.015, z + 0.075, 0.030, 0.030, 0.035, BUCKLE_DARK, outline=False)

    # Bolsas de pólvora e utilidades
    for s in (-1.0, 1.0):
        _box(c, bx + px * 0.125 * s + fx * 0.050 - 0.025, by + py * 0.125 * s + fy * 0.050 - 0.025,
             z + 0.010, 0.050, 0.050, 0.075, LEATHER_STRAP, outline=True)

    # Bomba de fumaça cerâmica (Kemuridama) no quadril esquerdo
    bomb_pos = (bx - px * 0.145, by - py * 0.145, z - 0.015)
    _box(c, bomb_pos[0] - 0.040, bomb_pos[1] - 0.040, bomb_pos[2], 0.080, 0.080, 0.080, BOMB_SHELL, outline=True, texture="lacquer")
    # Tampa e pavio incandescente laranja
    _box(c, bomb_pos[0] - 0.018, bomb_pos[1] - 0.018, bomb_pos[2] + 0.080, 0.036, 0.036, 0.024, (70, 70, 80), outline=False)
    _box(c, bomb_pos[0] - 0.010, bomb_pos[1] - 0.010, bomb_pos[2] + 0.104, 0.020, 0.020, 0.035, BOMB_FUSE, outline=False)

    # Coldres nas coxas presas por tiras
    for s in (-1.0, 1.0):
        thigh_data = c.legs_data["R" if s > 0 else "L"]["thigh"]
        _box(c, thigh_data[0] + px * 0.055 * s - 0.025, thigh_data[1] + py * 0.055 * s - 0.025,
             thigh_data[2] + 0.020, 0.050, 0.065, 0.130, LEATHER_STRAP, outline=True)
        # Fivelas do coldre
        _box(c, thigh_data[0] + px * 0.065 * s - 0.012, thigh_data[1] + py * 0.065 * s - 0.012,
             thigh_data[2] + 0.090, 0.024, 0.024, 0.024, BUCKLE_CHROME, outline=False)


# =============================================================================
# 4. PERNAS TÁTICAS, JOELHEIRAS CROMADAS E BOTAS
# =============================================================================
def draw_legs_t1(c):
    """Perneiras justas cinza-azuladas com joelheiras de placas cromadas e botas reforçadas."""
    for side in ("L", "R"):
        ld = c.legs_data[side]
        th_pos = ld["thigh"]
        sh_pos = ld["shin"]
        ft_pos = ld["foot"]

        # Coxa (calça tática justa cinza-azulada)
        _box(c, th_pos[0] - 0.055, th_pos[1] - 0.055, th_pos[2], 0.110, 0.110, 0.220, PANTS_TACTICAL, texture="latex")

        # Joelheira com placa cromada chanfrada
        _box(c, sh_pos[0] + c.fx * 0.045 - 0.045, sh_pos[1] + c.fy * 0.045 - 0.045,
             sh_pos[2] + 0.140, 0.090, 0.090, 0.080, ARMOR_CHROME, texture="chrome")
        _box(c, sh_pos[0] + c.fx * 0.055 - 0.035, sh_pos[1] + c.fy * 0.055 - 0.035,
             sh_pos[2] + 0.155, 0.070, 0.070, 0.050, ARMOR_LIGHT, outline=False)

        # Canela / Bota alta de aço
        _box(c, sh_pos[0] - 0.050, sh_pos[1] - 0.050, sh_pos[2], 0.100, 0.100, 0.150, ARMOR_DARK, texture="metal")
        # Aro cromado superior da bota
        _box(c, sh_pos[0] - 0.055, sh_pos[1] - 0.055, sh_pos[2] + 0.130, 0.110, 0.110, 0.025, ARMOR_LIGHT, outline=False)

        # Pé com bota tática reforçada
        _box(c, ft_pos[0] - 0.040 + c.fx * 0.025, ft_pos[1] - 0.040 + c.fy * 0.025,
             ft_pos[2], 0.080, 0.080, 0.050, ARMOR_CHROME, outline=True)
        # Sola de borracha preta
        _box(c, ft_pos[0] - 0.040 + c.fx * 0.025, ft_pos[1] - 0.040 + c.fy * 0.025,
             ft_pos[2], 0.080, 0.080, 0.015, COLOR_BLACK, outline=False)


# =============================================================================
# 5. OMBREIRAS E BRAÇOS DE COMBATE
# =============================================================================
def draw_arms_and_armor_t1(c, arms):
    """Ombreiras cromadas em camadas, manoplas táticas e luvas pretas."""
    for k, (s, e, side) in enumerate(arms):
        # Ombreira cromada chanfrada
        z = s[2] + 0.015
        ox, oy = c.px * side * 0.035, c.py * side * 0.035
        _box(c, s[0] + ox - 0.060, s[1] + oy - 0.055, z - 0.035, 0.120, 0.110, 0.050, ARMOR_CHROME, texture="chrome")
        _box(c, s[0] + ox * 1.3 - 0.050, s[1] + oy * 1.3 - 0.045, z + 0.005, 0.100, 0.090, 0.025, ARMOR_LIGHT, outline=False)

        # Braço e antebraço com manopla cromada
        arm_dir = (e[0] - s[0], e[1] - s[1], e[2] - s[2])
        arm_len = math.hypot(arm_dir[0], arm_dir[1], arm_dir[2])
        _obox(c, s[0], s[1], s[2], arm_dir, length=arm_len, width=0.060, height=0.060, color=PANTS_TACTICAL)
        # Manopla metálica no antebraço
        mid = (s[0] + arm_dir[0] * 0.45, s[1] + arm_dir[1] * 0.45, s[2] + arm_dir[2] * 0.45)
        _obox(c, mid[0], mid[1], mid[2], arm_dir, length=arm_len * 0.55, width=0.068, height=0.068,
              color=ARMOR_CHROME, texture="chrome")
        # Luva preta na mão
        _box(c, e[0] - 0.025, e[1] - 0.025, e[2] - 0.025, 0.050, 0.050, 0.050, COLOR_BLACK, outline=True)


# =============================================================================
# 6. ADAGA SHINOBI DE ALTA PRECISÃO (MICRO-VOXELS T1)
# =============================================================================
def draw_weapons_t1(c, arm_r):
    """
    Adaga Shinobi de alta precisão:
    - Lâmina afiada com gume branco reluzente e sulco central fuller.
    - Guarda metálica cromada e cabo de couro trançado.
    - No ataque especial: corte relâmpago prateado e rastro azul-névoa!
    """
    hand = (arm_r[0], arm_r[1], arm_r[2] - 0.060)

    if c.is_melee:
        d = _norm((c.fx * 0.85 + c.px * 0.20, c.fy * 0.85 + c.py * 0.20, -0.25))
    else:
        # Guarda baixa ágil de adaga invertida ou estocada rápida
        d = _norm((c.fx * 0.70 - c.px * 0.30, c.fy * 0.70 - c.py * 0.30, -0.18))

    # Cabo da adaga com couro trançado
    _obox(c, hand[0] - d[0] * 0.10, hand[1] - d[1] * 0.10, hand[2] - d[2] * 0.10,
          d, length=0.100, width=0.032, height=0.032, color=LEATHER_STRAP)
    # Pomo de aço
    _obox(c, hand[0] - d[0] * 0.12, hand[1] - d[1] * 0.12, hand[2] - d[2] * 0.12,
          d, length=0.025, width=0.040, height=0.040, color=ARMOR_LIGHT, outline=False)

    # Guarda cromada chanfrada
    _obox(c, hand[0], hand[1], hand[2], d, length=0.025, width=0.075, height=0.035, color=ARMOR_CHROME, outline=True)

    # Lâmina de aço afiada com sulco fuller e gume navalha
    blade_len = 0.300
    _obox(c, hand[0] + d[0] * 0.025, hand[1] + d[1] * 0.025, hand[2] + d[2] * 0.025,
          d, length=blade_len, width=0.044, height=0.016, color=BLADE_STEEL, outline=False)
    # Gume reflexivo branco
    _obox(c, hand[0] + d[0] * 0.025, hand[1] + d[1] * 0.025, hand[2] + d[2] * 0.025,
          d, length=blade_len, width=0.014, height=0.022, color=BLADE_EDGE, outline=False)
    # Ponta da adaga
    tip = (hand[0] + d[0] * (0.025 + blade_len), hand[1] + d[1] * (0.025 + blade_len), hand[2] + d[2] * (0.025 + blade_len))
    _obox(c, tip[0], tip[1], tip[2], d, length=0.045, width=0.020, height=0.010, color=BLADE_EDGE, outline=False)


# =============================================================================
# 7. RENDERIZADOR COMPLETO DE KASUMI T1
# =============================================================================
def render_kasumi_t1(c):
    """Renderiza Kasumi na Técnica 1 (Micro-voxels & Texturas Procedurais Ricas)."""
    # 1. Pernas, joelheiras e botas
    draw_legs_t1(c)

    # 2. Cinto, coldres e bombas de fumaça
    draw_belt_t1(c)

    # 3. Tronco e espartilho tático com fivelas
    draw_torso_t1(c)

    # 4. Braços e Poses
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    if c.state == "ATTACK":
        # Estocada/salto rápido com adaga
        p = c.atk_progress
        reach = 0.18 + 0.26 * p
        arm_l = (bx + fx * 0.12 - px * 0.14, by + fy * 0.12 - py * 0.14, tz + 0.15)
        arm_r = (bx + fx * reach + px * 0.06, by + fy * reach + py * 0.06, tz + 0.18)
    elif c.state == "INTRO":  # Concept Iconic Pose
        # Postura baixa agachada ninja pronta para saque
        arm_l = (bx + fx * 0.10 - px * 0.16, by + fy * 0.10 - py * 0.16, tz + 0.12)
        arm_r = (bx + fx * 0.16 + px * 0.12, by + fy * 0.16 + py * 0.12, tz + 0.08)
    else:  # IDLE
        arm_l = (bx + fx * 0.06 - px * 0.15, by + fy * 0.06 - py * 0.15, tz + 0.10)
        arm_r = (bx + fx * 0.14 + px * 0.10, by + fy * 0.14 + py * 0.10, tz + 0.12)

    # 4. Braços e Poses com ordenação Painter's Algorithm
    sh_l = (bx - px * 0.14, by - py * 0.14, tz + 0.20)
    sh_r = (bx + px * 0.14, by + py * 0.14, tz + 0.20)

    from src.isometric.iso_math import rotate_xy
    def depth(x, y):
        rx, ry = rotate_xy(x, y, getattr(c, "azimuth", 0.0))
        return rx + ry

    d_torso = depth(bx, by)
    d_arm_l = depth(arm_l[0], arm_l[1])
    d_arm_r = depth(arm_r[0], arm_r[1])

    back_elems = []
    front_elems = []

    elem_l = (d_arm_l, lambda: draw_arms_and_armor_t1(c, [(sh_l, arm_l, -1.0)]))
    (back_elems if d_arm_l < d_torso else front_elems).append(elem_l)

    def draw_right_arm_and_blade():
        draw_arms_and_armor_t1(c, [(sh_r, arm_r, 1.0)])
        draw_weapons_t1(c, arm_r)

    elem_r = (d_arm_r, draw_right_arm_and_blade)
    (back_elems if d_arm_r < d_torso else front_elems).append(elem_r)

    # Elementos atrás do tronco
    back_elems.sort(key=lambda item: item[0])
    for _, fn in back_elems:
        fn()

    # Tronco e espartilho tático com fivelas
    draw_torso_t1(c)

    # Elementos à frente do tronco
    front_elems.sort(key=lambda item: item[0])
    for _, fn in front_elems:
        fn()

    # Cabeça, máscara e cachecol
    draw_head_t1(c)
