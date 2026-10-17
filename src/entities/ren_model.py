"""
Ren, o Monge Shaolin de Punhos de Ferro e Kiai (Ciclo 1):
- Cabeça raspada esculpida em 3D com as 6 marcas sagradas Jieba de queima de incenso no topo da testa.
- Olhar marcial focado e determinado com sobrancelhas expressivas e lábios firmes.
- Túnica Kasaya cor de açafrão/laranja transpassada diagonalmente no peito com colarinho branco interno.
- Grande colar budista Mala de contas esféricas de madeira de cedro com borla sagrada.
- Calças cinza-ardósia em malha 3D contínua entrando em perneiras brancas Shaolin (gaiters) com tiras pretas.
- Sandálias Waraji com solado escuro.
- Braços fortes com faixas brancas nos punhos (wrist wraps) e pulseira de contas na mão direita.
- Ataques melee ultrarrápidos com socos, palmas de ferro, rajada Hyakuretsu Ken e chutes altos com aura dourada de Chi/Kiai.
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.mesh_primitives import (
    draw_ribbon_mesh_3d,
    draw_tapered_frustum_3d,
    draw_portrait_face_3d,
)

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
    "eye": (82, 54, 38),
    "brow": (38, 30, 26),
    "lip": (186, 134, 118),
    "bead": (110, 58, 32),
    "bead_dark": (75, 38, 20),
    "bead_light": (155, 88, 48),
    "bead_cord": (185, 45, 35),
    "wrist_wrap": (232, 228, 218),
    "sandal": (182, 152, 102),
    "sole": (38, 30, 24),
    "strap": (40, 34, 30),
    "chi_gold": (255, 210, 48),
    "chi_core": (255, 250, 195),
}

MATERIALS = {
    "robe": "canvas", "robe_dark": "canvas", "robe_light": "canvas",
    "collar": "canvas", "sash": "silk", "pants": "canvas",
    "pants_dark": "canvas", "gaiter": "canvas", "bead": "leather",
    "sandal": "canvas"
}


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def _step(c):
    return c.extra_props.get("combo_step", 1) if c.extra_props else 1


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
        # Pausa dramática pós-Hyakuretsu Ken: mão esquerda em prece vertical no peito, punho direito recolhido
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
        left = (bx + fx * 0.18 + px * 0.04, by + fy * 0.18 + py * 0.04, tz + 0.15)
        right = (bx + fx * 0.06 - px * 0.14, by + fy * 0.06 - py * 0.14, tz + 0.38)
        return left, right

    # Palma esquerda à frente
    left = (bx + fx * 0.22 + px * 0.08, by + fy * 0.22 + py * 0.08, tz + 0.14)
    # Punho direito engatilhado na cintura
    right = (bx - fx * 0.04 - px * 0.14, by - fy * 0.04 - py * 0.14, tz + 0.04)
    return left, right


def walk_arms(c):
    """Passada marcial com balanço fluído dos punhos."""
    sw = math.sin(c.walk_timer * 9.0)
    tz = c.torso_z
    left = (c.base_x + c.fx * (0.12 - sw * 0.14) + c.px * 0.12, c.base_y + c.fy * (0.12 - sw * 0.14) + c.py * 0.12, tz + 0.08 + abs(sw) * 0.02)
    right = (c.base_x + c.fx * (0.12 + sw * 0.14) - c.px * 0.12, c.base_y + c.fy * (0.12 + sw * 0.14) - c.py * 0.12, tz + 0.08 + abs(sw) * 0.02)
    return left, right


def attack_arms(c):
    """3 golpes de artes marciais Shaolin: 1) Soco Direto, 2) Palma de Ferro, 3) Chute Alto Dragon Kick."""
    step = _step(c)
    p = c.atk_progress if c.atk_progress is not None else 0.0
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    if step == 1:
        # Soco direto com o punho direito
        reach = math.sin(p * math.pi) * 0.44
        right = (bx + fx * (0.24 + reach) - px * 0.04, by + fy * (0.24 + reach) - py * 0.04, tz + 0.14)
        left = (bx - fx * (0.04 + reach * 0.2) + px * 0.14, by - fy * (0.04 + reach * 0.2) + py * 0.14, tz + 0.12)
        return left, right
    elif step == 2:
        # Palma de ferro com a mão esquerda
        reach = math.sin(p * math.pi) * 0.46
        left = (bx + fx * (0.26 + reach) + px * 0.04, by + fy * (0.26 + reach) + py * 0.04, tz + 0.15)
        right = (bx - fx * (0.08 + reach * 0.2) - px * 0.14, by - fy * (0.08 + reach * 0.2) - py * 0.14, tz + 0.06)
        return left, right
    else:
        # Chute alto Shaolin: braços abertos em equilíbrio
        kick_arc = math.sin(p * math.pi)
        left = (bx - fx * (0.06 + kick_arc * 0.12) + px * 0.22, by - fy * (0.06 + kick_arc * 0.12) + py * 0.22, tz + 0.18)
        right = (bx - fx * (0.12 + kick_arc * 0.14) - px * 0.20, by - fy * (0.12 + kick_arc * 0.14) - py * 0.20, tz + 0.12 + kick_arc * 0.06)
        return left, right


# ---------------------------------------------------------------------------------------------------------------------
# Camadas do Modelo: Trás, Pernas, Faixa, Tronco, Cabeça e Frente
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """Detalhes desenhados atrás do personagem."""
    P = pal()
    if mk.facing_camera(c):
        # Contas traseiras do colar Mala de madeira em volta do pescoço
        bead_r = 0.022
        for side in (-0.05, 0.0, 0.05):
            mk.cbox(c, c.base_x - c.fx * 0.08 + c.px * side, c.base_y - c.fy * 0.08 + c.py * side,
                    c.neck_z + 0.02, bead_r * 2, bead_r * 2, bead_r * 2, P["bead_dark"], outline=False)


def _draw_kicking_leg(c, hip_r, knee_r, foot_r):
    """Desenha a perna direita articulada desferindo o Chute Alto Shaolin."""
    P = pal()
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[hip_r, knee_r],
        widths=[0.120, 0.105],
        depth_thick=0.088,
        colors=[P["pants"], P["pants_dark"]],
        side_vec=(c.px, c.py, 0.0),
        normal_vec=(c.fx, c.fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[knee_r, foot_r],
        widths=[0.095, 0.080],
        depth_thick=0.080,
        colors=[P["gaiter"], P["gaiter_dark"]],
        side_vec=(c.px, c.py, 0.0),
        normal_vec=(c.fx, c.fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )
    # Pé com sandália Waraji na ponta do chute alto
    mk.obox(c, foot_r, (c.fx, c.fy, 0.65), 0.14, 0.075, 0.050, P["sandal"])


def draw_legs(c):
    """
    Pernas com calça cinza-ardósia e perneiras brancas amarradas (Gaiters Shaolin).
    No 3º golpe do combo (step == 3), executa um Chute Alto Shaolin (Dragon Kick).
    """
    P = pal()
    h_phase = c.extra_props.get("hyakuretsu_phase") if c.extra_props else None

    if c.is_melee and _step(c) == 3 and not h_phase and c.atk_progress is not None:
        # Perna esquerda ("L") plantada como base firme de apoio
        ld_l = c.legs_data["L"]
        th_l, sh_l, ft_l = ld_l["thigh"], ld_l["shin"], ld_l["foot"]
        top_l = (th_l[0], th_l[1], th_l[2] + 0.22)
        knee_l = (sh_l[0], sh_l[1], sh_l[2] + 0.15)
        cuff_l = (sh_l[0], sh_l[1], sh_l[2] + 0.08)
        ankle_l = (ft_l[0], ft_l[1], ft_l[2] + 0.05)

        draw_ribbon_mesh_3d(c.surface, c.camera, spine_points=[top_l, knee_l, cuff_l], widths=[0.120, 0.108, 0.090], depth_thick=0.088, colors=[P["pants"], P["pants_dark"]], side_vec=(c.px, c.py, 0.0), normal_vec=(c.fx, c.fy, 0.0), outline=True, alpha=c.alpha)
        draw_ribbon_mesh_3d(c.surface, c.camera, spine_points=[cuff_l, ankle_l], widths=[0.088, 0.076], depth_thick=0.078, colors=[P["gaiter"], P["gaiter_dark"]], side_vec=(c.px, c.py, 0.0), normal_vec=(c.fx, c.fy, 0.0), outline=True, alpha=c.alpha)
        mk.cbox(c, ft_l[0] + c.fx * 0.03, ft_l[1] + c.fy * 0.03, ft_l[2] + 0.015, 0.13, 0.065, 0.034, P["gaiter_dark"], outline=True)
        mk.cbox(c, ft_l[0] + c.fx * 0.03, ft_l[1] + c.fy * 0.03, ft_l[2] + 0.003, 0.134, 0.069, 0.010, P["sandal"], outline=False)

        # Perna direita ("R") erguida em Chute Alto Shaolin
        kick_arc = max(0.55, math.sin(c.atk_progress * math.pi))
        hip_r = (c.base_x - c.px * 0.06, c.base_y - c.py * 0.06, c.pelvis_z + 0.05)
        knee_r = (hip_r[0] + c.fx * (0.28 * kick_arc) - c.px * 0.04, hip_r[1] + c.fy * (0.28 * kick_arc) - c.py * 0.04, c.pelvis_z + 0.18 * kick_arc)
        foot_r = (hip_r[0] + c.fx * (0.66 * kick_arc) - c.px * (0.06 * kick_arc), hip_r[1] + c.fy * (0.66 * kick_arc) - c.py * (0.06 * kick_arc), c.torso_z + 0.34 * kick_arc)
        c.kick_foot = foot_r

        if mk.behind(c, foot_r):
            _draw_kicking_leg(c, hip_r, knee_r, foot_r)
            c.kick_leg_front = None
        else:
            c.kick_leg_front = (hip_r, knee_r, foot_r)
        return

    c.kick_leg_front = None
    trail, amp, freq = mk.motion(c, 0.04)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.8 * sign, trail, (c.px, c.py), amp=amp * 0.5, freq=freq)

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.4, sh[1] + o1[1] * 0.4, sh[2] + 0.15)
        cuff_pos = (sh[0] + o1[0] * 0.2, sh[1] + o1[1] * 0.2, sh[2] + 0.08)
        ankle = (foot[0] + o2[0] * 0.3, foot[1] + o2[1] * 0.3, foot[2] + 0.05)

        # Calça cinza-ardósia em malha contínua 3D
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos],
            widths=[0.125, 0.110, 0.092],
            depth_thick=0.088,
            colors=[P["pants"], P["pants_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Perneiras brancas Shaolin (Gaiters) enrolando a canela
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[cuff_pos, ankle],
            widths=[0.088, 0.076],
            depth_thick=0.078,
            colors=[P["gaiter"], P["gaiter_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Tiras pretas de amarração cruzadas nas perneiras
        for dz in (0.03, 0.07):
            mk.cbox(c, sh[0], sh[1], sh[2] + dz, 0.098, 0.098, 0.012, P["strap"], outline=False)

        # Pé com sandália Waraji e sola
        flen, fwidth = 0.13, 0.066
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.016, flen, fwidth, 0.034, P["gaiter_dark"], outline=True)
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.003, flen + 0.004, fwidth + 0.004, 0.010, P["sandal"], outline=False)
        mk.cbox(c, foot[0] + c.fx * (flen * 0.35), foot[1] + c.fy * (flen * 0.35), foot[2] + 0.018, 0.024, 0.024, 0.012, P["strap"], outline=False)


def draw_obi(c):
    """Faixa marcial vermelha com pontas caídas na lateral."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.005, c.pelvis_w * 0.72, 0.080, P["sash"])
    knot_x = bx + fx * 0.08 - px * 0.07
    knot_y = by + fy * 0.08 - py * 0.07
    mk.cbox(c, knot_x, knot_y, z + 0.010, 0.060, 0.050, 0.060, P["sash_dark"])

    trail, amp, freq = mk.motion(c, 0.05)
    offs = mk.cloth_offsets(c, 2, 0.8, trail, amp * 1.3, freq, (knot_x, knot_y))
    for i, o in enumerate(offs):
        mk.cbox(c, knot_x + o[0], knot_y + o[1], z - 0.060 * (i + 1) + o[2], 0.035, 0.024, 0.065, P["sash"], outline=False)


def draw_torso(c):
    """
    Túnica Kasaya alaranjada transpassada no peito com colarinho interno branco
    e o grande colar Mala de contas de madeira caindo sobre o peito.
    """
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.095

    if mk.depth(c, fx, fy) > -0.05:
        # Sub-gola interna branca visível no decote
        mk.obox(c, (bx + fx * (front - 0.008), by + fy * (front - 0.008), tz + 0.08), (0.0, 0.0, 1.0), 0.180, 0.090, 0.016, P["collar"], up=(fx, fy, 0.0), outline=False)

        # Faixa diagonal da túnica Kasaya cor de açafrão
        top_k = (bx + fx * front - px * 0.08, by + fy * front - py * 0.08, tz + 0.25)
        bot_k = (bx + fx * front + px * 0.06, by + fy * front + py * 0.06, tz + 0.03)
        draw_tapered_frustum_3d(c.surface, c.camera, top_k, bot_k, w_start=0.110, h_start=0.022, w_end=0.140, h_end=0.022, color=P["robe"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)

        # Orla dourada da túnica Kasaya
        mk.obox(c, (bx + fx * (front + 0.002) - px * 0.02, by + fy * (front + 0.002) - py * 0.02, tz + 0.08), (fx * 0.15 - px * 0.15, fy * 0.15 - py * 0.15, 0.90), 0.160, 0.022, 0.010, P["robe_light"], up=(fx, fy, 0.0), outline=False)

        # Grande Colar Mala de contas budistas na frente do peito
        bead_size = 0.032
        bead_coords = [
            (bx + fx * 0.090 + px * 0.060, by + fy * 0.090 + py * 0.060, tz + 0.20),
            (bx + fx * 0.100 + px * 0.040, by + fy * 0.100 + py * 0.040, tz + 0.15),
            (bx + fx * 0.105 + px * 0.020, by + fy * 0.105 + py * 0.020, tz + 0.10),
            (bx + fx * 0.110, by + fy * 0.110, tz + 0.06),
            (bx + fx * 0.105 - px * 0.020, by + fy * 0.105 - py * 0.020, tz + 0.10),
            (bx + fx * 0.100 - px * 0.040, by + fy * 0.100 - py * 0.040, tz + 0.15),
            (bx + fx * 0.090 - px * 0.060, by + fy * 0.090 - py * 0.060, tz + 0.20),
        ]
        for pt in bead_coords:
            mk.cbox(c, pt[0], pt[1], pt[2], bead_size, bead_size, bead_size, P["bead"], outline=False)
        # Borla vermelha da conta Guru central
        mk.cbox(c, bx + fx * 0.112, by + fy * 0.112, tz + 0.020, 0.024, 0.024, 0.045, P["bead_cord"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """
    Braço marcial articulado e musculoso de monge Shaolin:
    - Ombro direito coberto pela túnica Kasaya; ombro esquerdo musculoso.
    - Antebraços fortes articulados com cotovelo flexionado e faixas brancas nos punhos.
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


def draw_head(c):
    """
    Cabeça raspada com as 6 marcas sagradas Jieba de queima de incenso
    e sobrancelhas marcantes de monge determinado.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    hw = c.head_w

    # Cranial dome cap para cabeça raspada Shaolin arredondada (evita topo quadrado)
    cap_bot = (bx, by, hz + 0.158)
    cap_top = (bx, by, hz + 0.188)
    draw_tapered_frustum_3d(
        c.surface, c.camera, cap_bot, cap_top,
        w_start=hw * 0.88, h_start=hw * 0.88,
        w_end=hw * 0.62, h_end=hw * 0.62,
        color=P["skin"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha
    )

    if mk.facing_camera(c):
        # 6 Marcas Sagradas Jieba (2 colunas de 3 pequenos pontos no alto da testa)
        front_d = hw * 0.50 + 0.006
        for col_sign in (-1.0, 1.0):
            for row_idx, row_z in enumerate((hz + 0.115, hz + 0.135, hz + 0.155)):
                mx = bx + fx * front_d + px * (0.018 * col_sign)
                my = by + fy * front_d + py * (0.018 * col_sign)
                mk.cbox(c, mx, my, row_z, 0.014, 0.014, 0.014, P["jieba"], outline=False)


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
        mk.cbox(c, hand[0], hand[1], hand[2] - 0.010, 0.065, 0.065, 0.050, P["wrist_wrap"], outline=True)

    # Pulseira Mala de contas no pulso direito
    mk.cbox(c, right_hand[0], right_hand[1], right_hand[2] + 0.020, 0.075, 0.075, 0.022, P["bead"], outline=False)

    h_phase = c.extra_props.get("hyakuretsu_phase") if c.extra_props else None
    if h_phase == "FLURRY":
        # Rajada dos Cem Punhos (Hokuto Hyakuretsu Ken)
        h_clock = c.extra_props.get("hyakuretsu_clock", 0.0) if c.extra_props else 0.0
        bx, by, tz = c.base_x, c.base_y, c.torso_z
        offsets = (
            (-0.22, 0.16, 0.0), (0.22, 0.18, 0.9), (-0.14, 0.04, 1.8), (0.14, 0.06, 2.7),
            (-0.26, 0.09, 3.6), (0.26, 0.11, 4.5), (-0.07, 0.22, 5.2), (0.07, -0.02, 6.0),
        )
        for lat, dz, ph in offsets:
            cyc = 0.5 + 0.5 * math.sin(h_clock * 58.0 + ph)
            reach = 0.34 + cyc * 0.42
            fx_pt = bx + fx * reach + px * lat
            fy_pt = by + fy * reach + py * lat
            fz_pt = tz + 0.08 + dz
            mk.cbox(c, fx_pt, fy_pt, fz_pt, 0.058, 0.058, 0.052, P["skin"], outline=False)
            mk.cbox(c, fx_pt - fx * 0.03, fy_pt - fy * 0.03, fz_pt, 0.062, 0.062, 0.045, P["wrist_wrap"], outline=False)
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
        r = 0.11
        pts = [
            (left_hand[0] + px * r, left_hand[1] + py * r, left_hand[2]),
            (left_hand[0], left_hand[1], left_hand[2] + r * 1.15),
            (left_hand[0] - px * r, left_hand[1] - py * r, left_hand[2]),
            (left_hand[0], left_hand[1], left_hand[2] - r * 0.90),
        ]
        mk.band(c, pts, P["chi_gold"] + (210,))
        return

    # Efeito visual de Ataque Melee (Chi / Kiai)
    if c.is_melee and c.atk_progress is not None:
        step = _step(c)
        strike_pt = getattr(c, "kick_foot", right_hand) if step == 3 else (right_hand if step == 1 else left_hand)
        p = c.atk_progress

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
