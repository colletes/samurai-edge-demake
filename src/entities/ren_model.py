"""
Ren, o Monge Shaolin de Punhos de Ferro e Kiai (Ciclo 1):
- Cabeça raspada com marcas sagradas Jieba (6 pontos de incenso no topo/testa).
- Túnica Kasaya cor de açafrão/laranja cruzada no peito sobre faixa branca.
- Grande colar budista Mala de contas esféricas pesadas de madeira de cedro.
- Calças cinza-ardósia com faixas de tecido brancas enrolando as canelas (perneiras de monge).
- Sandálias Waraji com tiras pretas.
- Ataques melee ultrarrápidos com socos, palmas de ferro e chutes com energia Chi/Kiai dourada.
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth

SKIN = (238, 195, 160)
SKIN_SHADOW = (200, 155, 120)

PALETTE = {
    "robe": (228, 122, 34),
    "torso": (228, 122, 34),
    "robe_dark": (168, 80, 20),
    "robe_light": (248, 152, 58),
    "collar": (238, 234, 224),
    "sash": (205, 55, 25),
    "belt": (205, 55, 25),
    "sash_dark": (150, 35, 18),
    "pants": (84, 88, 94),
    "pants_dark": (54, 58, 64),
    "gaiter": (228, 222, 210),
    "gaiter_dark": (180, 174, 162),
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "hair": SKIN,
    "jieba": (255, 248, 225),
    "eye": (45, 34, 28),
    "brow": (40, 32, 28),
    "bead": (110, 58, 32),
    "bead_dark": (75, 38, 20),
    "bead_light": (155, 88, 48),
    "bead_cord": (185, 45, 35),
    "wrist_wrap": (232, 228, 218),
    "sandal": (182, 152, 102),
    "strap": (40, 34, 30),
    "chi_gold": (255, 210, 48),
    "chi_core": (255, 250, 195),
}

MATERIALS = {
    "robe": "canvas",
    "robe_dark": "canvas",
    "robe_light": "canvas",
    "collar": "canvas",
    "sash": "silk",
    "pants": "canvas",
    "pants_dark": "canvas",
    "gaiter": "canvas",
    "bead": "leather",
    "sandal": "canvas",
}


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


# ---------------------------------------------------------------------------------------------------------------------
# Poses de Braços e Artes Marciais
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Postura Shaolin de combate:
    - Mão esquerda aberta à frente na altura do peito em guarda protetora de palma (Bei Shou / Ping Zhang).
    - Mão direita recuada fechada em punho junto ao quadril/costelas, pronta para o disparo.
    """
    breathe = math.sin(c.walk_timer * 2.8) * 0.015
    tz = c.torso_z + breathe

    # Palma esquerda à frente
    left = (
        c.base_x + c.fx * 0.22 + c.px * 0.08,
        c.base_y + c.fy * 0.22 + c.py * 0.08,
        tz + 0.14
    )
    # Punho direito engatilhado na cintura
    right = (
        c.base_x - c.fx * 0.04 - c.px * 0.14,
        c.base_y - c.fy * 0.04 - c.py * 0.14,
        tz + 0.04
    )
    return left, right


def walk_arms(c):
    """Passada marcial com balanço fluído dos punhos."""
    sw = math.sin(c.walk_timer * 9.0)
    tz = c.torso_z
    left = (
        c.base_x + c.fx * (0.12 - sw * 0.14) + c.px * 0.12,
        c.base_y + c.fy * (0.12 - sw * 0.14) + c.py * 0.12,
        tz + 0.08 + abs(sw) * 0.02
    )
    right = (
        c.base_x + c.fx * (0.12 + sw * 0.14) - c.px * 0.12,
        c.base_y + c.fy * (0.12 + sw * 0.14) - c.py * 0.12,
        tz + 0.08 + abs(sw) * 0.02
    )
    return left, right


def _step(c):
    return c.extra_props.get("combo_step", 1) if c.extra_props else 1


def attack_arms(c):
    """
    Sequência de golpes Shaolin (Combo 3-Hit):
    - Passo 1: Soco direto rápido de direita (Straight Punch).
    - Passo 2: Palma de ferro ascendente de esquerda (Iron Palm Strike).
    - Passo 3: Ataque duplo de palmas com projeção de Chi e Kiai.
    """
    p = c.atk_progress
    step = _step(c)
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    if step == 1:
        # Soco direto com a direita
        reach = _smooth(p / 0.5) if p < 0.5 else _smooth((1.0 - p) / 0.5)
        right = (
            bx + fx * (0.10 + reach * 0.44) - px * 0.04,
            by + fy * (0.10 + reach * 0.44) - py * 0.04,
            tz + 0.14
        )
        left = (
            bx + px * 0.14 - fx * 0.04,
            by + py * 0.14 - fy * 0.04,
            tz + 0.10
        )
    elif step == 2:
        # Palma de ferro de esquerda
        reach = _smooth(p / 0.5) if p < 0.5 else _smooth((1.0 - p) / 0.5)
        left = (
            bx + fx * (0.12 + reach * 0.42) + px * 0.03,
            by + fy * (0.12 + reach * 0.42) + py * 0.03,
            tz + 0.06 + reach * 0.16
        )
        right = (
            bx - px * 0.14 - fx * 0.06,
            by - py * 0.14 - fy * 0.06,
            tz + 0.08
        )
    else:
        # Golpe duplo ou Kiai
        reach = math.sin(p * math.pi) * 0.42
        left = (
            bx + fx * (0.16 + reach) + px * 0.08,
            by + fy * (0.16 + reach) + py * 0.08,
            tz + 0.15
        )
        right = (
            bx + fx * (0.16 + reach) - px * 0.08,
            by + fy * (0.16 + reach) - py * 0.08,
            tz + 0.15
        )
    return left, right


# ---------------------------------------------------------------------------------------------------------------------
# Camadas do Modelo: Trás, Pernas, Faixa, Tronco, Cabeça e Frente
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """Detalhes desenhados atrás do personagem."""
    # Nuca e contas traseiras do colar Mala
    P = pal()
    if mk.facing_camera(c):
        # Trás do colar Mala de madeira em volta do pescoço
        bead_r = 0.022
        for side in (-0.05, 0.0, 0.05):
            mk.cbox(c, c.base_x - c.fx * 0.08 + c.px * side, c.base_y - c.fy * 0.08 + c.py * side,
                    c.neck_z + 0.02, bead_r * 2, bead_r * 2, bead_r * 2, P["bead_dark"], outline=False)


def draw_legs(c):
    """
    Pernas com calça cinza-ardósia e perneiras brancas amarradas (Gaiters Shaolin).
    """
    P = pal()
    mk.legs(
        c,
        pants=P["pants"],
        boot=P["gaiter"],
        boot_h=0.16,
        baggy=(0.14, 0.13),
        foot_color=P["gaiter_dark"],
        foot_len=0.13,
        sole=P["sandal"],
        cuff=P["strap"],
        texture="canvas"
    )
    # Tiras pretas cruzadas na perneira branca
    for side in ("L", "R"):
        ld = c.legs_data[side]
        sh = ld["shin"]
        for dz in (0.04, 0.08, 0.12):
            mk.cbox(c, sh[0], sh[1], sh[2] + dz, 0.106, 0.106, 0.014, P["strap"], outline=False)


def draw_obi(c):
    """Faixa marcial vermelha com pontas caídas na lateral."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    # Faixa ao redor da cintura
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.005, c.pelvis_w * 0.72, 0.08, P["sash"])
    # Nó lateral
    knot_x = bx + fx * 0.08 - px * 0.07
    knot_y = by + fy * 0.08 - py * 0.07
    mk.cbox(c, knot_x, knot_y, z + 0.01, 0.06, 0.05, 0.06, P["sash_dark"])

    # Pontas penduradas da faixa
    trail, amp, freq = mk.motion(c, 0.05)
    offs = mk.cloth_offsets(c, 2, 0.8, trail, amp * 1.3, freq, (knot_x, knot_y))
    for i, o in enumerate(offs):
        mk.cbox(c, knot_x + o[0], knot_y + o[1], z - 0.06 * (i + 1) + o[2], 0.035, 0.024, 0.065, P["sash"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """
    Braço marcial articulado e musculoso de monge Shaolin:
    - Ombro direito coberto pela túnica Kasaya drapeada; ombro esquerdo musculoso.
    - Antebraços fortes articulados com cotovelo flexionado e faixas brancas nos punhos (wrist wraps).
    """
    P = pal()
    sleeve_color = P["robe"] if side < 0 else None
    sleeve_reach = 0.35 if side < 0 else 0.0
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=sleeve_color,
        sleeve_to=sleeve_reach,
        bracer=P["wrist_wrap"],
        bracer_span=(0.58, 0.94),
        w=0.062,
        bend=0.035
    )


def draw_torso(c):
    """
    Túnica Kasaya alaranjada transpassada no peito com colarinho interno branco
    e o grande colar Mala de contas de madeira caindo sobre o peito.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    # Sub-gola interna branca/creme visível no decote
    mk.cbox(c, bx + fx * 0.09, by + fy * 0.09, tz + 0.12, 0.12, 0.04, 0.14, P["collar"], outline=False)

    # Faixa diagonal da túnica Kasaya de ombro a cintura
    mk.cbox(c, bx + fx * 0.095, by + fy * 0.095, tz + 0.06, 0.18, 0.05, 0.18, P["robe"], outline=True, texture="canvas")
    # Borda/orla dourada da túnica
    mk.cbox(c, bx + fx * 0.105 - px * 0.03, by + fy * 0.105 - py * 0.03, tz + 0.12, 0.03, 0.04, 0.16, P["robe_light"], outline=False)

    # Grande Colar Mala de contas budistas na frente do peito
    # Laço de contas caindo em arco:
    bead_size = 0.032
    bead_coords = [
        # Lado esquerdo descendo
        (bx + fx * 0.09 + px * 0.06, by + fy * 0.09 + py * 0.06, tz + 0.20),
        (bx + fx * 0.10 + px * 0.04, by + fy * 0.10 + py * 0.04, tz + 0.15),
        (bx + fx * 0.105 + px * 0.02, by + fy * 0.105 + py * 0.02, tz + 0.10),
        # Ponto mais baixo central (Conta guru com borla)
        (bx + fx * 0.11, by + fy * 0.11, tz + 0.06),
        # Lado direito subindo
        (bx + fx * 0.105 - px * 0.02, by + fy * 0.105 - py * 0.02, tz + 0.10),
        (bx + fx * 0.10 - px * 0.04, by + fy * 0.10 - py * 0.04, tz + 0.15),
        (bx + fx * 0.09 - px * 0.06, by + fy * 0.09 - py * 0.06, tz + 0.20),
    ]
    for pt in bead_coords:
        mk.cbox(c, pt[0], pt[1], pt[2], bead_size, bead_size, bead_size, P["bead"], outline=False)
    # Borla vermelha abaixo da conta central
    mk.cbox(c, bx + fx * 0.112, by + fy * 0.112, tz + 0.02, 0.024, 0.024, 0.045, P["bead_cord"], outline=False)


def draw_head(c):
    """
    Cabeça raspada com as 6 marcas sagradas Jieba de queima de incenso
    e sobrancelhas marcantes de monge determinado.
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    hz = c.head_z
    hw = c.head_w

    # Crânio esculpido liso
    mk.cbox(c, bx, by, hz + 0.02, hw, hw, 0.16, P["skin"], outline=True)
    # Curvatura superior da cabeça raspada
    mk.cbox(c, bx, by, hz + 0.16, hw - 0.03, hw - 0.03, 0.03, P["skin_shadow"], outline=False)

    if mk.facing_camera(c):
        # 6 Marcas Sagradas Jieba (2 colunas de 3 pequenos pontos no alto da testa)
        front_d = hw / 2 + 0.006
        for col_sign in (-1.0, 1.0):
            for row_idx, row_z in enumerate((hz + 0.11, hz + 0.13, hz + 0.15)):
                mx = bx + fx * front_d + px * (0.016 * col_sign)
                my = by + fy * front_d + py * (0.016 * col_sign)
                mk.cbox(c, mx, my, row_z, 0.014, 0.014, 0.014, P["jieba"], outline=False)

        # Sobrancelhas retas e firmes
        for side in (-1.0, 1.0):
            bx_brow = bx + fx * front_d + px * (0.034 * side)
            by_brow = by + fy * front_d + py * (0.034 * side)
            mk.cbox(c, bx_brow, by_brow, hz + 0.08, 0.026, 0.012, 0.014, P["brow"], outline=False)


def draw_front(c, left_hand, right_hand):
    """
    Mãos com faixas brancas nos punhos, pulseira de oração na direita,
    e auras flamejantes douradas de Chi/Kiai ao atacar.
    """
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # Faixas nos punhos (Wrist wraps)
    for hand, side_name in ((left_hand, "left"), (right_hand, "right")):
        mk.cbox(c, hand[0], hand[1], hand[2] - 0.01, 0.065, 0.065, 0.05, P["wrist_wrap"], outline=True)

    # Pulseira Mala de contas no pulso direito
    mk.cbox(c, right_hand[0], right_hand[1], right_hand[2] + 0.02, 0.075, 0.075, 0.022, P["bead"], outline=False)

    # Efeito visual de Ataque Melee (Chi / Kiai)
    if c.is_melee:
        step = _step(c)
        strike_hand = right_hand if step == 1 else (left_hand if step == 2 else right_hand)
        p = c.atk_progress

        # Rastro de impacto marcial com energia Chi (mk.band translúcido)
        if 0.15 < p < 0.88:
            r = 0.09 * math.sin(p * math.pi)
            pt_center = (strike_hand[0] + fx * 0.08, strike_hand[1] + fy * 0.08, strike_hand[2])
            prev_center = (strike_hand[0] - fx * 0.16, strike_hand[1] - fy * 0.16, strike_hand[2])
            a0 = (pt_center[0] + px * r, pt_center[1] + py * r, pt_center[2] + r)
            a1 = (pt_center[0] - px * r, pt_center[1] - py * r, pt_center[2] - r)
            b0 = (prev_center[0] + px * r * 0.5, prev_center[1] + py * r * 0.5, prev_center[2] + r * 0.5)
            b1 = (prev_center[0] - px * r * 0.5, prev_center[1] - py * r * 0.5, prev_center[2] - r * 0.5)
            mk.band(c, (a0, a1, b1, b0), P["chi_gold"] + (200,))
            mk.band(c, (mk.lerp(a0, a1, 0.3), mk.lerp(a0, a1, 0.7), mk.lerp(b0, b1, 0.7), mk.lerp(b0, b1, 0.3)), P["chi_core"] + (245,))

        # Se for o golpe 3 ou estado de Kiai, onda de choque esférica de Chi
        if step == 3 or getattr(c, "state", "") == "KIAI":
            wave_r = 0.26 * math.sin(p * math.pi)
            if wave_r > 0.05:
                wc = (c.base_x + fx * 0.22, c.base_y + fy * 0.22, c.torso_z + 0.10)
                w_pts = [
                    (wc[0] + px * wave_r, wc[1] + py * wave_r, wc[2]),
                    (wc[0] + fx * wave_r * 0.8, wc[1] + fy * wave_r * 0.8, wc[2] + wave_r * 0.6),
                    (wc[0] - px * wave_r, wc[1] - py * wave_r, wc[2]),
                    (wc[0] - fx * wave_r * 0.8, wc[1] - fy * wave_r * 0.8, wc[2] - wave_r * 0.6),
                ]
                mk.band(c, w_pts, P["chi_gold"] + (180,))
