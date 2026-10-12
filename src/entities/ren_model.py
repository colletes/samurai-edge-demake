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
    Postura Shaolin de combate e poses cerimoniais (Intro/Victory):
    - 'shaolin_salute': Saudação Baoquan (punho direito encostado na palma esquerda aberta diante do peito).
    - 'kiai_roar': Postura de canalização de Kiai com punhos cerrados nas laterais do tronco.
    - 'shaolin_bow': Reverência Gassho com palmas unidas em prece no centro do peito.
    - Padrão: Mão esquerda à frente em guarda de palma (Ping Zhang) e punho direito engatilhado na cintura.
    """
    breathe = math.sin(c.walk_timer * 2.8) * 0.015
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    pose = c.extra_props.get("pose") if c.extra_props else None

    h_phase = c.extra_props.get("hyakuretsu_phase") if c.extra_props else None
    if h_phase == "FLURRY":
        h_clock = c.extra_props.get("hyakuretsu_clock", 0.0) if c.extra_props else 0.0
        s1 = math.sin(h_clock * 68.0)
        s2 = -s1
        left = (bx + fx * (0.28 + max(0.0, s1) * 0.30) + px * 0.11, by + fy * (0.28 + max(0.0, s1) * 0.30) + py * 0.11, tz + 0.14 + s1 * 0.04)
        right = (bx + fx * (0.28 + max(0.0, s2) * 0.30) - px * 0.11, by + fy * (0.28 + max(0.0, s2) * 0.30) - py * 0.11, tz + 0.14 + s2 * 0.04)
        return left, right
    if h_phase == "PAUSE":
        # Pausa dramática pós-Hyakuretsu Ken ("Omae wa mou shindeiru"): mão esquerda em prece vertical no peito, punho direito recolhido
        left = (bx + fx * 0.18 + px * 0.03, by + fy * 0.18 + py * 0.03, tz + 0.16)
        right = (bx - fx * 0.06 - px * 0.16, by - fy * 0.06 - py * 0.16, tz + 0.05)
        return left, right

    if pose == "shaolin_salute":
        left = (bx + fx * 0.20 + px * 0.03, by + fy * 0.20 + py * 0.03, tz + 0.14)
        right = (bx + fx * 0.19 - px * 0.02, by + fy * 0.19 - py * 0.02, tz + 0.13)
        return left, right
    if pose == "kiai_roar":
        left = (bx + fx * 0.10 + px * 0.22, by + fy * 0.10 + py * 0.22, tz + 0.08)
        right = (bx + fx * 0.10 - px * 0.22, by + fy * 0.10 - py * 0.22, tz + 0.08)
        return left, right
    if pose == "shaolin_bow":
        # Prece Dan Zhang de uma mão no peito + Palma do Lótus Dourado erguida ao céu
        left = (bx + fx * 0.18 + px * 0.04, by + fy * 0.18 + py * 0.04, tz + 0.15)
        right = (bx + fx * 0.06 - px * 0.14, by + fy * 0.06 - py * 0.14, tz + 0.38)
        return left, right

    # Palma esquerda à frente
    left = (
        bx + fx * 0.22 + px * 0.08,
        by + fy * 0.22 + py * 0.08,
        tz + 0.14
    )
    # Punho direito engatilhado na cintura
    right = (
        bx - fx * 0.04 - px * 0.14,
        by - fy * 0.04 - py * 0.14,
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
    Sequência de golpes Shaolin (Combo 3-Hit) ou Rajada dos Cem Punhos (Hyakuretsu Ken):
    - Passo 1: Soco direto rápido de direita (Straight Punch).
    - Passo 2: Palma de ferro ascendente de esquerda (Iron Palm Strike).
    - Passo 3: Chute Alto do Dragão Shaolin (braços em postura de contrabalanço marcial).
    """
    h_phase = c.extra_props.get("hyakuretsu_phase") if c.extra_props else None
    if h_phase in ("FLURRY", "PAUSE"):
        return idle_arms(c)

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
            bx + fx * (0.12 + reach * 0.44) + px * 0.03,
            by + fy * (0.12 + reach * 0.44) + py * 0.03,
            tz + 0.06 + reach * 0.16
        )
        right = (
            bx - px * 0.14 - fx * 0.06,
            by - py * 0.14 - fy * 0.06,
            tz + 0.08
        )
    else:
        # Passo 3: Chute Alto Shaolin — guarda de palma esquerda à frente e braço direito em contrabalanço
        kick_arc = max(0.35, math.sin(p * math.pi))
        left = (
            bx + fx * (0.20 + kick_arc * 0.12) + px * 0.14,
            by + fy * (0.20 + kick_arc * 0.12) + py * 0.14,
            tz + 0.18
        )
        right = (
            bx - fx * (0.12 + kick_arc * 0.14) - px * 0.20,
            by - fy * (0.12 + kick_arc * 0.14) - py * 0.20,
            tz + 0.12 + kick_arc * 0.06
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


def _draw_kicking_leg(c, hip_r, knee_r, foot_r):
    """Desenha a perna direita articulada desferindo o Chute Alto Shaolin."""
    P = pal()
    # Coxa (calça cinza) e canela (perneira branca Shaolin) articuladas no chute alto
    mk.limb(c, hip_r, knee_r, 0.125, P["pants"])
    mk.limb(c, knee_r, foot_r, 0.095, P["gaiter"], outline=True)
    # Pé com sandália Waraji na ponta do chute alto
    mk.obox(c, foot_r, (c.fx, c.fy, 0.65), 0.14, 0.08, 0.055, P["sandal"])
    mk.obox(c, (foot_r[0] - c.fx * 0.02, foot_r[1] - c.fy * 0.02, foot_r[2] + 0.01), (c.fx, c.fy, 0.65), 0.10, 0.075, 0.04, P["strap"], outline=False)


def draw_legs(c):
    """
    Pernas com calça cinza-ardósia e perneiras brancas amarradas (Gaiters Shaolin).
    No 3º golpe do combo (step == 3, fora da rajada de socos Hyakuretsu), executa um Chute Alto Shaolin.
    """
    P = pal()
    h_phase = c.extra_props.get("hyakuretsu_phase") if c.extra_props else None
    if c.is_melee and _step(c) == 3 and not h_phase:
        # Perna esquerda ("L") plantada como base firme de apoio
        ld_l = c.legs_data["L"]
        th_l, sh_l, ft_l = ld_l["thigh"], ld_l["shin"], ld_l["foot"]
        mk.obox(c, (ft_l[0] - c.fx * 0.05, ft_l[1] - c.fy * 0.05, ft_l[2]), (c.fx, c.fy, 0.0), 0.13, 0.075, 0.022, P["sandal"])
        mk.obox(c, (ft_l[0] - c.fx * 0.03, ft_l[1] - c.fy * 0.03, ft_l[2] + 0.02), (c.fx, c.fy, 0.0), 0.11, 0.063, 0.045, P["gaiter_dark"])
        mk.cbox(c, th_l[0], th_l[1], th_l[2], 0.14, 0.14, 0.22, P["pants"], texture="canvas")
        mk.cbox(c, sh_l[0], sh_l[1], sh_l[2] + 0.08, 0.13, 0.13, 0.13, P["pants"], texture="canvas")
        mk.cbox(c, sh_l[0], sh_l[1], sh_l[2] + 0.005, 0.10, 0.10, 0.16, P["gaiter"])
        for dz in (0.04, 0.08, 0.12):
            mk.cbox(c, sh_l[0], sh_l[1], sh_l[2] + dz, 0.106, 0.106, 0.014, P["strap"], outline=False)

        # Perna direita ("R") erguida em Chute Alto Shaolin (Dragon Kick)
        kick_arc = max(0.55, math.sin(c.atk_progress * math.pi))
        hip_r = (c.base_x - c.px * 0.06, c.base_y - c.py * 0.06, c.pelvis_z + 0.05)
        knee_r = (
            hip_r[0] + c.fx * (0.28 * kick_arc) - c.px * 0.04,
            hip_r[1] + c.fy * (0.28 * kick_arc) - c.py * 0.04,
            c.pelvis_z + 0.18 * kick_arc
        )
        foot_r = (
            hip_r[0] + c.fx * (0.66 * kick_arc) - c.px * (0.06 * kick_arc),
            hip_r[1] + c.fy * (0.66 * kick_arc) - c.py * (0.06 * kick_arc),
            c.torso_z + 0.34 * kick_arc
        )
        c.kick_foot = foot_r
        if mk.behind(c, foot_r):
            _draw_kicking_leg(c, hip_r, knee_r, foot_r)
            c.kick_leg_front = None
        else:
            c.kick_leg_front = (hip_r, knee_r, foot_r)
        return

    c.kick_leg_front = None
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

    if getattr(c, "kick_leg_front", None) is not None:
        _draw_kicking_leg(c, *c.kick_leg_front)

    # Faixas nos punhos (Wrist wraps)
    for hand, side_name in ((left_hand, "left"), (right_hand, "right")):
        mk.cbox(c, hand[0], hand[1], hand[2] - 0.01, 0.065, 0.065, 0.05, P["wrist_wrap"], outline=True)

    # Pulseira Mala de contas no pulso direito
    mk.cbox(c, right_hand[0], right_hand[1], right_hand[2] + 0.02, 0.075, 0.075, 0.022, P["bead"], outline=False)

    h_phase = c.extra_props.get("hyakuretsu_phase") if c.extra_props else None
    if h_phase == "FLURRY":
        # Rajada dos Cem Punhos (Estilo Fist of the North Star / Hokuto Hyakuretsu Ken):
        # Múltiplos punhos fantasmas e jatos dourados de Chi disparando em cone de alta frequência
        h_clock = c.extra_props.get("hyakuretsu_clock", 0.0) if c.extra_props else 0.0
        bx, by, tz = c.base_x, c.base_y, c.torso_z
        offsets = (
            (-0.22, 0.16, 0.0),
            (0.22, 0.18, 0.9),
            (-0.14, 0.04, 1.8),
            (0.14, 0.06, 2.7),
            (-0.26, 0.09, 3.6),
            (0.26, 0.11, 4.5),
            (-0.07, 0.22, 5.2),
            (0.07, -0.02, 6.0),
        )
        for lat, dz, ph in offsets:
            cyc = 0.5 + 0.5 * math.sin(h_clock * 58.0 + ph)
            reach = 0.34 + cyc * 0.42
            fx_pt = bx + fx * reach + px * lat
            fy_pt = by + fy * reach + py * lat
            fz_pt = tz + 0.08 + dz
            # Punho fantasma com faixa branca e impacto de Chi dourado
            mk.cbox(c, fx_pt, fy_pt, fz_pt, 0.058, 0.058, 0.052, P["skin"], outline=False)
            mk.cbox(c, fx_pt - fx * 0.03, fy_pt - fy * 0.03, fz_pt, 0.062, 0.062, 0.045, P["wrist_wrap"], outline=False)
            # Rastro de jato de Chi dourado
            tail_x = bx + fx * 0.16 + px * (lat * 0.5)
            tail_y = by + fy * 0.16 + py * (lat * 0.5)
            tail_z = tz + 0.10 + dz * 0.6
            r = 0.038
            pts = (
                (fx_pt + px * r, fy_pt + py * r, fz_pt + r),
                (fx_pt - px * r, fy_pt - py * r, fz_pt - r),
                (tail_x - px * r * 0.4, tail_y - py * r * 0.4, tail_z - r * 0.4),
                (tail_x + px * r * 0.4, tail_y + py * r * 0.4, tail_z + r * 0.4),
            )
            mk.band(c, pts, P["chi_gold"] + (185,))
            if cyc > 0.65:
                mk.cbox(c, fx_pt + fx * 0.04, fy_pt + fy * 0.04, fz_pt, 0.075, 0.075, 0.075, P["chi_core"], outline=False)
        return
    elif h_phase == "PAUSE":
        # Pausa dramática ("Omae wa mou shindeiru"): aura serena de Chi dourado na mão em prece
        r = 0.11
        pts = [
            (left_hand[0] + px * r, left_hand[1] + py * r, left_hand[2]),
            (left_hand[0], left_hand[1], left_hand[2] + r * 1.15),
            (left_hand[0] - px * r, left_hand[1] - py * r, left_hand[2]),
            (left_hand[0], left_hand[1], left_hand[2] - r * 0.9),
        ]
        mk.band(c, pts, P["chi_gold"] + (210,))
        return

    pose = c.extra_props.get("pose") if c.extra_props else None
    if pose == "shaolin_salute":
        # Halo de energia Chi dourada entre as mãos unidas em saudação
        mid = mk.lerp(left_hand, right_hand, 0.5)
        r = 0.085
        pts = [
            (mid[0] + px * r, mid[1] + py * r, mid[2]),
            (mid[0], mid[1], mid[2] + r),
            (mid[0] - px * r, mid[1] - py * r, mid[2]),
            (mid[0], mid[1], mid[2] - r * 0.8),
        ]
        mk.band(c, pts, P["chi_gold"] + (165,))
    elif pose == "shaolin_bow":
        # Orbe de Lótus de Chi Dourado sobre a palma direita erguida ao céu
        orb_c = (right_hand[0], right_hand[1], right_hand[2] + 0.08)
        for r, col, alpha in ((0.11, P["chi_gold"], 180), (0.065, P["chi_core"], 235)):
            pts = [
                (orb_c[0] + px * r, orb_c[1] + py * r, orb_c[2]),
                (orb_c[0], orb_c[1], orb_c[2] + r * 1.15),
                (orb_c[0] - px * r, orb_c[1] - py * r, orb_c[2]),
                (orb_c[0], orb_c[1], orb_c[2] - r * 0.95),
            ]
            mk.band(c, pts, col + (alpha,))
    elif pose == "kiai_roar":
        # Onda de choque de Kiai irradiando dos punhos e do Dantian
        wc = (c.base_x + fx * 0.12, c.base_y + fy * 0.12, c.torso_z + 0.10)
        for wave_r, alpha in ((0.28, 170), (0.18, 225)):
            w_pts = [
                (wc[0] + px * wave_r, wc[1] + py * wave_r, wc[2]),
                (wc[0], wc[1], wc[2] + wave_r * 0.78),
                (wc[0] - px * wave_r, wc[1] - py * wave_r, wc[2]),
                (wc[0], wc[1], wc[2] - wave_r * 0.78),
            ]
            mk.band(c, w_pts, (P["chi_core"] if wave_r < 0.22 else P["chi_gold"]) + (alpha,))

    # Efeito visual de Ataque Melee (Chi / Kiai)
    if c.is_melee:
        step = _step(c)
        strike_pt = getattr(c, "kick_foot", right_hand) if step == 3 else (right_hand if step == 1 else left_hand)
        p = c.atk_progress

        # Rastro de impacto marcial com energia Chi (mk.band translúcido)
        if 0.10 < p < 0.92:
            r = (0.12 if step == 3 else 0.09) * math.sin(p * math.pi)
            pt_center = (strike_pt[0] + fx * 0.10, strike_pt[1] + fy * 0.10, strike_pt[2])
            prev_z = strike_pt[2] - 0.18 if step == 3 else strike_pt[2]
            prev_center = (strike_pt[0] - fx * 0.18, strike_pt[1] - fy * 0.18, prev_z)
            a0 = (pt_center[0] + px * r, pt_center[1] + py * r, pt_center[2] + r)
            a1 = (pt_center[0] - px * r, pt_center[1] - py * r, pt_center[2] - r)
            b0 = (prev_center[0] + px * r * 0.5, prev_center[1] + py * r * 0.5, prev_center[2] + r * 0.5)
            b1 = (prev_center[0] - px * r * 0.5, prev_center[1] - py * r * 0.5, prev_center[2] - r * 0.5)
            mk.band(c, (a0, a1, b1, b0), P["chi_gold"] + (210,))
            mk.band(c, (mk.lerp(a0, a1, 0.3), mk.lerp(a0, a1, 0.7), mk.lerp(b0, b1, 0.7), mk.lerp(b0, b1, 0.3)), P["chi_core"] + (250,))

        # Se for o golpe 3 (Chute Alto) ou estado de Kiai, onda de choque esférica de Chi
        if step == 3 or getattr(c, "state", "") == "KIAI":
            wave_r = 0.28 * math.sin(p * math.pi)
            if wave_r > 0.05:
                wc = (strike_pt[0] + fx * 0.06, strike_pt[1] + fy * 0.06, strike_pt[2])
                w_pts = [
                    (wc[0] + px * wave_r, wc[1] + py * wave_r, wc[2]),
                    (wc[0] + fx * wave_r * 0.85, wc[1] + fy * wave_r * 0.85, wc[2] + wave_r * 0.7),
                    (wc[0] - px * wave_r, wc[1] - py * wave_r, wc[2]),
                    (wc[0] - fx * wave_r * 0.6, wc[1] - fy * wave_r * 0.6, wc[2] - wave_r * 0.7),
                ]
                mk.band(c, w_pts, P["chi_gold"] + (195,))
