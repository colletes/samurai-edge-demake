"""
Chiyo, a Kunoichi das Duas Nodachi (Ciclo 1):
- Cabelo negro como a noite em corte hime com franja reta, mechas laterais e presilha dourada Kanzashi.
- Olhos cor de âmbar com delineado carmim alado (estilo benibake) e sorriso sutil.
- Traje shinobi de couro preto-carvão ajustado com malha ninja (kusari) na gola e antebraços.
- Lenço carmim-vinho volumoso em volta do pescoço com pontas esvoaçantes ao vento.
- Ombreira laqueada negra no ombro direito com bordas douradas e brasão do lírio-aranha (higanbana).
- Duas espadas gigantes Nodachi:
  - Bainhas cruzadas em 'X' nas costas com os longos cabos sobressaindo sobre os ombros.
  - Empunhaduras longas com cordão ito preto e vermelho, tsuba dourada quadrada e lâminas longas de aço polido.
  - Postura de dança marcial defensiva e cortes amplos e fluidos com rastro carmim.
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.voxel_rig import calc_blade_slash_3d

SKIN = (244, 212, 186)
SKIN_SHADOW = (212, 172, 144)

PALETTE = {
    # Cabelo e Adornos
    "hair": (24, 22, 26),
    "hair_highlight": (48, 44, 52),
    "hair_dark": (14, 12, 16),
    "gold": (224, 182, 64),
    "gold_bright": (255, 218, 96),
    "kanzashi_red": (210, 38, 48),

    # Rosto e Olhos
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "eye_amber": (218, 142, 36),
    "liner_red": (188, 30, 42),
    "lip": (195, 75, 85),

    # Traje Shinobi
    "leather": (28, 26, 30),
    "torso": (28, 26, 30),
    "leather_dark": (18, 16, 20),
    "leather_light": (44, 40, 48),
    "mesh": (20, 18, 22),
    "scarf": (152, 28, 48),
    "scarf_dark": (102, 18, 32),
    "scarf_light": (192, 42, 64),
    "sode_black": (22, 20, 24),
    "crest_red": (220, 36, 48),

    # Faixa e Pernas
    "sash": (132, 24, 40),
    "belt": (132, 24, 40),
    "pants": (26, 24, 28),
    "boot": (20, 18, 22),
    "boot_wrap": (142, 26, 44),
    "sole": (14, 12, 16),

    # Nodachi (Armas)
    "saya": (24, 22, 26),
    "saya_gold": (214, 174, 56),
    "ito_black": (22, 20, 22),
    "ito_red": (175, 30, 42),
    "steel": (230, 238, 248),
    "edge": (254, 255, 255),
    "trail": (214, 32, 52),
    "trail_core": (255, 196, 208),
}

MATERIALS = {
    "leather": "latex",
    "leather_dark": "latex",
    "scarf": "silk",
    "scarf_dark": "silk",
    "sash": "silk",
    "pants": "latex",
    "boot": "leather",
    "sode_black": "lacquer",
    "saya": "lacquer",
    "steel": "steel",
    "edge": "steel",
    "gold": "gold",
    "gold_bright": "gold",
}


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


# ---------------------------------------------------------------------------------------------------------------------
# Poses de Braços e Combate com Duas Nodachi
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Postura marcial de guarda da Dança das Duas Nodachi:
    - Braço direito recuado baixo, segurando a 1ª Nodachi apontando para trás e para baixo (pronta para o corte ascendente).
    - Braço esquerdo erguido alto cruzando à frente, segurando a 2ª Nodachi em guarda defensiva angular (guarda de interceptação).
    """
    breathe = math.sin(c.walk_timer * 2.8) * 0.015
    tz = c.torso_z + breathe

    # Mão direita baixa e recuada
    right = (
        c.base_x - c.fx * 0.12 - c.px * 0.14,
        c.base_y - c.fy * 0.12 - c.py * 0.14,
        tz + 0.04
    )
    # Mão esquerda alta na frente do torso
    left = (
        c.base_x + c.fx * 0.16 + c.px * 0.10,
        c.base_y + c.fy * 0.16 + c.py * 0.10,
        tz + 0.20
    )
    return left, right


def walk_arms(c):
    """Caminhada ágil e furtiva com as Nodachi balanceadas nas laterais."""
    sw = math.sin(c.walk_timer * 9.0)
    tz = c.torso_z
    right = (
        c.base_x - c.fx * 0.08 - c.px * (0.16 + sw * 0.03),
        c.base_y - c.fy * 0.08 - py * (0.16 + sw * 0.03) if "py" in dir() else c.base_y - c.fy * 0.08 - c.py * (0.16 + sw * 0.03),
        tz + 0.06 + abs(sw) * 0.02
    )
    left = (
        c.base_x + c.fx * 0.10 + c.px * (0.12 - sw * 0.03),
        c.base_y + c.fy * 0.10 + c.py * (0.12 - sw * 0.03),
        tz + 0.14 + abs(sw) * 0.02
    )
    return left, right


def _step(c):
    return c.extra_props.get("combo_step", 1) if c.extra_props else 1


def attack_arms(c):
    """
    Dança das Duas Nodachi (Combo 3-Hit com arcos amplos):
    - Passo 1: Corte ascendente diagonal com a Nodachi direita.
    - Passo 2: Giro horizontal rasante com a Nodachi esquerda.
    - Passo 3: Corte em tesoura cruzada com ambas as Nodachis se encontrando.
    """
    p = c.atk_progress
    step = _step(c)
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    if step == 1:
        # Corte ascendente com a direita
        arc_a = -1.2 + p * 2.4
        right = (
            bx + fx * math.cos(arc_a) * 0.28 - px * math.sin(arc_a) * 0.22,
            by + fy * math.cos(arc_a) * 0.28 - py * math.sin(arc_a) * 0.22,
            tz + 0.02 + p * 0.36
        )
        left = (
            bx + px * 0.16 - fx * 0.06,
            by + py * 0.16 - fy * 0.06,
            tz + 0.18
        )
    elif step == 2:
        # Giro horizontal com a esquerda
        arc_l = 1.4 - p * 2.8
        left = (
            bx + fx * math.cos(arc_l) * 0.30 + px * math.sin(arc_l) * 0.26,
            by + fy * math.cos(arc_l) * 0.30 + py * math.sin(arc_l) * 0.26,
            tz + 0.16
        )
        right = (
            bx - px * 0.16 - fx * 0.08,
            by - py * 0.16 - fy * 0.08,
            tz + 0.08
        )
    else:
        # Tesoura cruzada dupla
        cross_t = math.sin(p * math.pi)
        right = (
            bx + fx * (0.18 + cross_t * 0.24) - px * (0.16 - p * 0.26),
            by + fy * (0.18 + cross_t * 0.24) - py * (0.16 - p * 0.26),
            tz + 0.22 - p * 0.10
        )
        left = (
            bx + fx * (0.18 + cross_t * 0.24) + px * (0.16 - p * 0.26),
            by + fy * (0.18 + cross_t * 0.24) + py * (0.16 - p * 0.26),
            tz + 0.12 + p * 0.10
        )
    return left, right


# ---------------------------------------------------------------------------------------------------------------------
# Bainhas das Duas Nodachi nas Costas
# ---------------------------------------------------------------------------------------------------------------------

def _sheath_frames(c):
    """
    Duas grandes bainhas de Nodachi cruzadas nas costas em formato de 'X':
    - Bainha 1: diagonal do ombro direito ao quadril esquerdo.
    - Bainha 2: diagonal do ombro esquerdo ao quadril direito.
    """
    bx, by, pz, fx, fy, px, py = c.base_x, c.base_y, c.pelvis_z, c.fx, c.fy, c.px, c.py
    # Pontos de ancoragem no meio das costas
    back_center = (bx - fx * 0.12, by - fy * 0.12, pz + 0.18)

    # Direção 1 (cai para o quadril esquerdo, cabo aponta para ombro direito alto)
    dir1 = mk.norm((-fx * 0.15 + px * 0.45, -fy * 0.15 + py * 0.45, -0.85))
    orig1 = (back_center[0] - px * 0.10, back_center[1] - py * 0.10, back_center[2] + 0.18)

    # Direção 2 (cai para o quadril direito, cabo aponta para ombro esquerdo alto)
    dir2 = mk.norm((-fx * 0.15 - px * 0.45, -fy * 0.15 - py * 0.45, -0.85))
    orig2 = (back_center[0] + px * 0.10, back_center[1] + py * 0.10, back_center[2] + 0.18)

    return (orig1, dir1), (orig2, dir2)


# ---------------------------------------------------------------------------------------------------------------------
# Camadas do Modelo: Trás, Pernas, Faixa, Tronco, Cabeça e Frente
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira:
    - Longo cabelo negro caindo pelas costas.
    - Pontas esvoaçantes do lenço carmim.
    - As duas grandes bainhas das Nodachi cruzadas nas costas (com detalhes dourados).
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    hz, tz = c.head_z, c.torso_z

    # Volume traseiro do cabelo negro liso
    if mk.facing_camera(c):
        mk.hair_volume(c, P["hair"], size=0.14, height=0.14, back=0.04)
        # Cascata de cabelo longo caindo até a altura do tórax
        mk.cbox(c, bx - fx * 0.08, by - fy * 0.08, hz - 0.12, 0.11, 0.06, 0.16, P["hair"], outline=False)

    # Pontas do lenço carmim esvoaçante atrás do pescoço
    trail, amp, freq = mk.motion(c, 0.06)
    scarf_anchor = (bx - fx * 0.10, by - fy * 0.10, tz + 0.22)
    mk.panels(c, scarf_anchor, 3, 0.08, 0.08, 0.024,
              (P["scarf"], P["scarf_dark"], P["scarf_dark"]),
              phase=0.4, side=-1.0, drag=(-fx * 0.05, -fy * 0.05))

    # As duas grandes bainhas de Nodachi cruzadas nas costas
    (orig1, dir1), (orig2, dir2) = _sheath_frames(c)
    nodachi_sheath_len = 0.72

    for orig, d in ((orig1, dir1), (orig2, dir2)):
        # Corpo da bainha laqueada negra
        mk.obox(c, orig, d, nodachi_sheath_len, 0.048, 0.048, P["saya"], outline=True)
        # Boca da bainha (Kojiri) e ponteira com acabamento dourado
        mk.obox(c, orig, d, 0.04, 0.054, 0.054, P["saya_gold"], outline=False)
        mk.obox(c, mk.add(orig, d, nodachi_sheath_len - 0.04), d, 0.04, 0.052, 0.052, P["saya_gold"], outline=False)


def draw_legs(c):
    """
    Pernas femininas ágeis com calça shinobi justa preta e bandagens carmim na canela.
    """
    P = pal()
    mk.legs(
        c,
        pants=P["pants"],
        boot=P["boot"],
        boot_h=0.14,
        tight_w=(0.09, 0.08),
        foot_color=P["boot"],
        foot_len=0.12,
        sole=P["sole"],
        cuff=P["boot_wrap"],
        texture="latex"
    )
    # Tiras decorativas de amarração carmim nas botas
    for side in ("L", "R"):
        ld = c.legs_data[side]
        sh = ld["shin"]
        for dz in (0.03, 0.07, 0.11):
            mk.cbox(c, sh[0], sh[1], sh[2] + dz, 0.092, 0.092, 0.012, P["boot_wrap"], outline=False)


def draw_obi(c):
    """Cinto shinobi fino de couro preto com faixa carmim e fivela dourada."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    # Faixa carmim
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.01, c.pelvis_w * 0.70, 0.07, P["sash"])
    # Cinto de couro preto central
    mk.cbox(c, bx, by, z + 0.015, c.pelvis_w - 0.005, c.pelvis_w * 0.72, 0.035, P["leather_dark"])
    # Fivela retangular dourada na frente
    mk.cbox(c, bx + fx * 0.09, by + fy * 0.09, z + 0.02, 0.045, 0.03, 0.04, P["gold"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """
    Braço ágil articulado de kunoichi:
    - Manga justa de couro preto com malha ninja até o antebraço.
    - Braçadeira protetora de couro escuro e mãos articuladas para empunhadura dupla de Nodachi.
    """
    P = pal()
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["leather"],
        sleeve_to=0.70,
        bracer=P["leather_dark"],
        bracer_span=(0.55, 0.92),
        w=0.052,
        bend=0.025
    )


def draw_torso(c):
    """
    Tronco:
    - Gola interna com malha ninja (kusari).
    - Lenço carmim volumoso ao redor do pescoço.
    - Corpete de couro ajustado preto com rebites dourados.
    - Ombreira laqueada negra (sode) no ombro direito com borda dourada e flor de lírio-aranha.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    # Malha ninja no decote / colo
    mk.cbox(c, bx + fx * 0.08, by + fy * 0.08, tz + 0.14, 0.10, 0.04, 0.10, P["mesh"], outline=False)

    # Lenço carmim envolto no pescoço/clavícula
    mk.cbox(c, bx, by, tz + 0.22, 0.15, 0.15, 0.06, P["scarf"], outline=False)
    mk.cbox(c, bx + fx * 0.05, by + fy * 0.05, tz + 0.21, 0.12, 0.06, 0.05, P["scarf_light"], outline=False)

    # Corpete de couro preto
    mk.cbox(c, bx, by, tz + 0.08, 0.19, 0.14, 0.14, P["leather"], outline=True, texture="latex")

    # Rebites dourados no corpete
    for side in (-0.05, 0.05):
        for rz in (tz + 0.04, tz + 0.09, tz + 0.14):
            mk.cbox(c, bx + fx * 0.085 + px * side, by + fy * 0.085 + py * side, rz,
                    0.012, 0.012, 0.012, P["gold"], outline=False)

    # Ombreira laqueada negra no ombro direito (Sode)
    sh_r_x = bx - px * 0.15
    sh_r_y = by - py * 0.15
    sh_r_z = tz + 0.18
    # Placa laqueada
    mk.cbox(c, sh_r_x, sh_r_y, sh_r_z, 0.10, 0.10, 0.09, P["sode_black"], outline=True)
    # Borda dourada da ombreira
    mk.cbox(c, sh_r_x - px * 0.03, sh_r_y - py * 0.03, sh_r_z + 0.03, 0.04, 0.04, 0.07, P["gold"], outline=False)
    # Brasão vermelho da flor lírio-aranha
    mk.cbox(c, sh_r_x - px * 0.045, sh_r_y - py * 0.045, sh_r_z, 0.02, 0.02, 0.04, P["crest_red"], outline=False)


def draw_head(c):
    """
    Cabeça estilizada:
    - Corte hime em cabelo preto: franja frontal reta e mechas laterais retas descendo pelas bochechas.
    - Presilha dourada Kanzashi no lado esquerdo do cabelo com pequeno pendente carmim.
    - Olhos amendoados âmbar com delineado carmim pontiagudo (benibake).
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    hz = c.head_z
    hw = c.head_w

    # Rosto com pele feminina esculpida
    mk.cbox(c, bx, by, hz + 0.02, hw, hw, 0.14, P["skin"], outline=True)

    # Topo do cabelo negro
    mk.cbox(c, bx, by, hz + 0.10, hw + 0.016, hw + 0.016, 0.08, P["hair"], outline=True)

    if mk.facing_camera(c):
        front_d = hw / 2 + 0.006

        # Franja frontal reta característica do corte Hime
        mk.cbox(c, bx + fx * front_d, by + fy * front_d, hz + 0.085, hw - 0.01, 0.03, 0.045, P["hair"], outline=False)

        # Mechas laterais do corte Hime descendo além do queixo
        for side in (-1.0, 1.0):
            mx = bx + fx * (front_d - 0.015) + px * (0.058 * side)
            my = by + fy * (front_d - 0.015) + py * (0.058 * side)
            mk.cbox(c, mx, my, hz + 0.01, 0.03, 0.025, 0.12, P["hair"], outline=False)

        # Presilha dourada Kanzashi no lado esquerdo da cabeça
        pin_x = bx + px * 0.075 + fx * 0.02
        pin_y = by + py * 0.075 + fy * 0.02
        pin_z = hz + 0.11
        mk.cbox(c, pin_x, pin_y, pin_z, 0.04, 0.04, 0.03, P["gold_bright"], outline=False)
        mk.cbox(c, pin_x + px * 0.01, pin_y + py * 0.01, pin_z - 0.03, 0.018, 0.018, 0.04, P["kanzashi_red"], outline=False)

        # Olhos amendoados âmbar com delineado carmim
        for side in (-1.0, 1.0):
            ex = bx + fx * front_d + px * (0.032 * side)
            ey = by + fy * front_d + py * (0.032 * side)
            # Delineado carmim alado
            mk.cbox(c, ex + px * (0.01 * side), ey + py * (0.01 * side), hz + 0.055, 0.026, 0.01, 0.015, P["liner_red"], outline=False)
            # Íris âmbar
            mk.cbox(c, ex, ey, hz + 0.052, 0.018, 0.008, 0.016, P["eye_amber"], outline=False)


# ---------------------------------------------------------------------------------------------------------------------
# Renderizador Especializado das Duas Nodachis
# ---------------------------------------------------------------------------------------------------------------------

def _draw_nodachi_blade(c, hand, direction, length=0.86):
    """
    Desenha uma espada Nodachi proporcional:
    - Longa empunhadura (tsuka) de ~0.24m atrás da mão com cordão preto e vermelho.
    - Pommel (kashira) dourado.
    - Guarda (tsuba) quadrada dourada.
    - Lâmina longa de ~0.86m de aço prateado brilhante com fio afiado.
    """
    P = pal()
    d = mk.norm(direction)
    grip_len = 0.24
    guard_w = 0.08

    # Localização da Tsuba (guarda) logo à frente da mão
    tsuba_pt = mk.add(hand, d, 0.05)

    # 1. Empunhadura longa (Tsuka)
    mk.obox(c, mk.add(tsuba_pt, d, -grip_len), d, grip_len, 0.038, 0.038, P["ito_black"])
    # Tranças carmim no cabo
    mk.obox(c, mk.add(tsuba_pt, d, -grip_len * 0.55), d, 0.06, 0.04, 0.04, P["ito_red"], outline=False)
    # Pomo de ouro (Kashira)
    mk.obox(c, mk.add(tsuba_pt, d, -grip_len - 0.012), d, 0.02, 0.044, 0.044, P["gold"], outline=False)

    # 2. Guarda quadrada dourada (Tsuba)
    mk.obox(c, mk.add(tsuba_pt, d, -0.008), d, 0.016, guard_w, guard_w, P["gold"])
    # Habaki (colar dourado na base da lâmina)
    mk.obox(c, mk.add(tsuba_pt, d, 0.008), d, 0.03, 0.045, 0.035, P["gold"], outline=False)

    # 3. Lâmina longa de Nodachi (Nagasa)
    mk.obox(c, mk.add(tsuba_pt, d, 0.038), d, length, 0.048, 0.026, P["steel"])
    # Fio de corte polido (Ha)
    mk.obox(c, mk.add(tsuba_pt, d, 0.048), d, length - 0.02, 0.016, 0.03, P["edge"], outline=False)

    # Retorna ponta da lâmina (Kissaki)
    return mk.add(tsuba_pt, d, 0.038 + length)


def draw_front(c, left_hand, right_hand):
    """
    Desenha as duas Nodachis em combate e os rastros carmim nos ataques.
    """
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # Antebraços com braçadeiras de couro e malha
    for hand, side_name in ((left_hand, "left"), (right_hand, "right")):
        mk.cbox(c, hand[0], hand[1], hand[2] - 0.02, 0.058, 0.058, 0.06, P["leather_dark"], outline=True)
        mk.cbox(c, hand[0], hand[1], hand[2] + 0.02, 0.062, 0.062, 0.02, P["mesh"], outline=False)

    # Determinação das orientações das lâminas conforme o estado
    if c.is_melee:
        step = _step(c)
        p = c.atk_progress

        if step == 1:
            # Nodachi direita corta para cima, esquerda mantém guarda
            slash_d1 = mk.norm((fx * 0.70 + px * 0.20, fy * 0.70 + py * 0.20, 0.75 - p * 0.30))
            guard_d2 = mk.norm((fx * 0.40 - px * 0.40, fy * 0.40 - py * 0.40, 0.80))
            tip1 = _draw_nodachi_blade(c, right_hand, slash_d1, length=0.90)
            _draw_nodachi_blade(c, left_hand, guard_d2, length=0.84)

            # Rastro carmim de corte usando faixa translúcida fluida (mk.band)
            if 0.15 < p < 0.88:
                mid = mk.lerp(right_hand, tip1, 0.55)
                prev_tip = (tip1[0] - fx * 0.16 - px * 0.08, tip1[1] - fy * 0.16 - py * 0.08, tip1[2] - 0.18)
                prev_mid = (mid[0] - fx * 0.10 - px * 0.04, mid[1] - fy * 0.10 - py * 0.04, mid[2] - 0.10)
                mk.band(c, (mid, tip1, prev_tip, prev_mid), P["trail"] + (180,))
                mk.band(c, (mk.lerp(mid, tip1, 0.6), tip1, prev_tip, mk.lerp(prev_mid, prev_tip, 0.6)), P["trail_core"] + (230,))

        elif step == 2:
            # Nodachi esquerda corta em giro horizontal, direita acompanha
            slash_d2 = mk.norm((fx * 0.85 - px * 0.35, fy * 0.85 - py * 0.35, -0.15))
            guard_d1 = mk.norm((-fx * 0.20 - px * 0.60, -fy * 0.20 - py * 0.60, -0.75))
            _draw_nodachi_blade(c, right_hand, guard_d1, length=0.84)
            tip2 = _draw_nodachi_blade(c, left_hand, slash_d2, length=0.90)

            # Rastro carmim de corte circular
            if 0.15 < p < 0.88:
                mid = mk.lerp(left_hand, tip2, 0.55)
                prev_tip = (tip2[0] - fx * 0.12 + px * 0.16, tip2[1] - fy * 0.12 + py * 0.16, tip2[2] + 0.06)
                prev_mid = (mid[0] - fx * 0.08 + px * 0.10, mid[1] - fy * 0.08 + py * 0.10, mid[2] + 0.04)
                mk.band(c, (mid, tip2, prev_tip, prev_mid), P["trail"] + (180,))
                mk.band(c, (mk.lerp(mid, tip2, 0.6), tip2, prev_tip, mk.lerp(prev_mid, prev_tip, 0.6)), P["trail_core"] + (230,))

        else:
            # Tesoura dupla: ambas as lâminas cruzando à frente
            cross_d1 = mk.norm((fx * 0.75 + px * 0.35, fy * 0.75 + py * 0.35, -0.25))
            cross_d2 = mk.norm((fx * 0.75 - px * 0.35, fy * 0.75 - py * 0.35, 0.25))
            tip1 = _draw_nodachi_blade(c, right_hand, cross_d1, length=0.88)
            tip2 = _draw_nodachi_blade(c, left_hand, cross_d2, length=0.88)

            # Rastro cruzado em 'X'
            if 0.15 < p < 0.88:
                mid1 = mk.lerp(right_hand, tip1, 0.5)
                mid2 = mk.lerp(left_hand, tip2, 0.5)
                mk.band(c, (mid1, tip1, tip2, mid2), P["trail"] + (190,))
                mk.band(c, (mk.lerp(mid1, tip1, 0.6), tip1, tip2, mk.lerp(mid2, tip2, 0.6)), P["trail_core"] + (240,))
    else:
        # Poses Neutras (Idle / Caminhada)
        # Nodachi direita apontando para trás e para baixo
        dir_r = mk.norm((-fx * 0.55 - px * 0.35, -fy * 0.55 - py * 0.35, -0.75))
        # Nodachi esquerda apontando para cima e para frente em guarda
        dir_l = mk.norm((fx * 0.45 + px * 0.25, fy * 0.45 + py * 0.25, 0.85))

        _draw_nodachi_blade(c, right_hand, dir_r, length=0.86)
        _draw_nodachi_blade(c, left_hand, dir_l, length=0.86)
