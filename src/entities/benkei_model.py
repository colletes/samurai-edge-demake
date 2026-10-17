"""
Benkei, o Guardião da Naginata / Walking Tank Colossal:
- Guerreiro sōhei imponente blindado em armadura pesada de placas de ferro laqueadas a preto (dō-maru/ō-yoroi).
- Capuz monástico de linho cru (zukin) cobrindo o topo da cabeça e ombros, emoldurando uma face severa e calejada.
- Colar de contas budistas pesadas de cedro escuro com contas douradas de intervalo (Mala).
- Ombreiras monumentais de ferro (ō-sode) articuladas em camadas com cordões vermelhos (odoshi) e bordas douradas.
- Naginata colossal:
  - Haste maciça de carvalho negro com anéis de latão e ponteira inferior de ferro (ishizuki).
  - Lâmina curva pesada de aço brilhante forjado com colarinho de ouro (habaki) e tsuba circular.
  - Ordenação dinâmica de profundidade (Painter's Algorithm) para renderizar a naginata e punhos atrás do tronco se estiver de costas.
- Feixe de armas troféu das 999 lutas na Ponte Gojō compacto e firme nas costas.
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.mesh_primitives import draw_tapered_frustum_3d, draw_ribbon_mesh_3d

SKIN = (218, 172, 138)
SKIN_SHADOW = (180, 134, 104)

PALETTE = {
    # Armadura de Ferro Negro e Bronze
    "iron": (28, 26, 30),
    "torso": (28, 26, 30),
    "iron_dark": (16, 14, 18),
    "iron_light": (48, 45, 52),
    "bronze": (175, 128, 48),
    "bronze_bright": (218, 168, 62),
    "bronze_dark": (118, 84, 30),
    "odoshi": (168, 32, 38),       # Cordões vermelhos de amarração
    "odoshi_dark": (108, 18, 24),

    # Capuz e Vestes Monásticas de Linho Cru
    "cowl": (218, 212, 202),
    "cowl_shadow": (168, 162, 152),
    "cowl_dark": (128, 122, 114),
    "cowl_light": (240, 235, 226),
    "hair": (218, 212, 202),       # Capuz de linho integrado no crânio
    "neck": (218, 212, 202),       # Gola do capuz envolvendo o pescoço
    "hakama": (32, 30, 36),
    "pants": (32, 30, 36),
    "belt": (168, 32, 38),

    # Anatomia e Rosto
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "beard": (32, 28, 26),
    "eye": (30, 26, 24),
    "brow": (24, 20, 20),

    # Adornos Sagrados
    "bead": (68, 38, 22),
    "bead_dark": (46, 24, 14),
    "bead_gold": (224, 178, 52),

    # Perneiras e Calçados
    "suneate": (22, 20, 24),       # Grevas de ferro nas canelas
    "waraji": (175, 145, 100),
    "strap": (32, 28, 26),

    # Naginata e Feixe de Armas da Ponte Gojō
    "wood_shaft": (38, 28, 22),
    "wood_shaft_dark": (24, 16, 12),
    "brass_ring": (198, 148, 56),
    "habaki": (228, 186, 64),
    "tsuba": (162, 116, 42),
    "steel": (230, 238, 248),
    "steel_edge": (255, 255, 255),
    "ishizuki": (32, 30, 34),
    "thrust_trail": (255, 215, 120),
    "trail_core": (255, 255, 230),
    "blood_gib": (180, 25, 30),
}

MATERIALS = {
    "iron": "metal",
    "iron_dark": "metal",
    "iron_light": "metal",
    "bronze": "metal",
    "suneate": "metal",
    "steel": "metal",
    "cowl": "canvas",
    "hakama": "canvas",
    "waraji": "canvas",
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses de Braços e Animação de Combate
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """Guarda imponente de Benkei com duas mãos na Naginata (ou postura de investida se desarmado)."""
    breathe = math.sin(c.walk_timer * 2.2) * 0.012
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    has_weapon = c.extra_props.get("has_naginata", True) if c.extra_props else True

    if not has_weapon:
        # Desarmado: postura de avanço bruto com manoplas prontas para agarrar/atropelar
        left = (bx + fx * 0.24 + px * 0.16, by + fy * 0.24 + py * 0.16, tz + 0.08)
        right = (bx + fx * 0.22 - px * 0.16, by + fy * 0.22 - py * 0.16, tz + 0.10)
        return left, right

    # Armado: Guarda pesada de Naginata (mão esquerda adiante no cabo, direita firme próxima à base)
    left = (bx + fx * 0.22 + px * 0.08, by + fy * 0.22 + py * 0.08, tz + 0.16)
    right = (bx - fx * 0.08 - px * 0.14, by - fy * 0.08 - py * 0.14, tz + 0.04)
    return left, right


def attack_arms(c):
    """Animações de Ataque Melee de Benkei."""
    p = c.atk_progress
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    is_throw = c.extra_props.get("is_throwing", False) if c.extra_props else False
    is_charge = c.extra_props.get("is_charging", False) if c.extra_props else False

    hoist_phase = c.extra_props.get("hoist_slam_phase") if c.extra_props else None
    hoist_prog = c.extra_props.get("hoist_slam_prog", 0.0) if c.extra_props else 0.0

    if hoist_phase == "HOIST":
        # Heave monumental para cima com as duas mãos erguendo a Naginata
        arm_z = tz + 0.16 + hoist_prog * 0.36
        left = (bx + fx * (0.28 - hoist_prog * 0.12) + px * 0.05, by + fy * (0.28 - hoist_prog * 0.12) + py * 0.05, arm_z)
        right = (bx + fx * (0.04 - hoist_prog * 0.08) - px * 0.07, by + fy * (0.04 - hoist_prog * 0.08) - py * 0.07, arm_z + 0.04)
        return left, right

    if hoist_phase == "SLAM":
        # Descida sísmica da Naginata cravando com força brutal no chão
        slam_curve = hoist_prog ** 1.8
        arm_z = tz + 0.52 - slam_curve * 0.58
        reach = 0.16 + slam_curve * 0.18
        left = (bx + fx * reach + px * 0.05, by + fy * reach + py * 0.05, arm_z)
        right = (bx + fx * (reach - 0.18) - px * 0.06, by + fy * (reach - 0.18) - py * 0.06, arm_z + 0.03)
        return left, right

    if is_charge:
        # Carga com ombro blindado: ombro direito projetado à frente em aríete
        left = (bx + fx * 0.18 + px * 0.20, by + fy * 0.18 + py * 0.20, tz + 0.06)
        right = (bx + fx * 0.32 - px * 0.10, by + fy * 0.32 - py * 0.10, tz + 0.14)
        return left, right

    if is_throw:
        # Arremesso de Naginata: recua a arma no início, arremessa com força total no clímax
        if p < 0.40:
            windup = p / 0.40
            left = (bx + fx * 0.12 + px * 0.10, by + fy * 0.12 + py * 0.10, tz + 0.20)
            right = (bx - fx * (0.15 + windup * 0.22) - px * 0.18, by - fy * (0.15 + windup * 0.22) - py * 0.18, tz + 0.25 + windup * 0.15)
        else:
            thrust = (p - 0.40) / 0.60
            left = (bx - fx * 0.10 + px * 0.14, by - fy * 0.10 + py * 0.14, tz + 0.05)
            right = (bx + fx * (0.35 + thrust * 0.25) - px * 0.06, by + fy * (0.35 + thrust * 0.25) - py * 0.06, tz + 0.20)
        return left, right

    # Estocada Frontal Colossal (Walking Tank Thrust)
    thrust_curve = math.sin(p * math.pi)
    left = (
        bx + fx * (0.24 + thrust_curve * 0.38) + px * 0.04,
        by + fy * (0.24 + thrust_curve * 0.38) + py * 0.04,
        tz + 0.16 + thrust_curve * 0.04
    )
    right = (
        bx + fx * (0.02 + thrust_curve * 0.46) - px * 0.06,
        by + fy * (0.02 + thrust_curve * 0.46) - py * 0.06,
        tz + 0.14 + thrust_curve * 0.04
    )
    return left, right


def _hands(c):
    """Calcula posição instantânea das mãos para ordenação de profundidade e renderização."""
    if c.is_melee and c.atk_progress is not None:
        return attack_arms(c)
    if c.is_moving and hasattr(c, "walk_timer"):
        # Marcha pesada de tanque com a Naginata segura
        sw = math.sin(c.walk_timer * 7.5) * 0.05
        tz = c.torso_z
        bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
        left = (bx + fx * 0.20 + px * 0.08 + fx * sw, by + fy * 0.20 + py * 0.08 + fy * sw, tz + 0.15)
        right = (bx - fx * 0.06 - px * 0.12 - fx * sw, by - fy * 0.06 - py * 0.12 - fy * sw, tz + 0.05)
        return left, right
    return idle_arms(c)


# ---------------------------------------------------------------------------------------------------------------------
# Detalhamento Voxel do Guerreiro
# ---------------------------------------------------------------------------------------------------------------------

def _draw_trophy_rack(c):
    """
    Feixe de armas troféu das 999 lutas na Ponte Gojō:
    - Compacto e firme contra as costas da armadura Dō-maru.
    - Duas bainhas cruzadas com empunhaduras de bronze e amarrações odoshi carmim.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    rack_base = (bx - fx * 0.14, by - fy * 0.14, tz + 0.08)

    # Suporte dorsal com cordões de amarração carmim
    mk.cbox(c, rack_base[0], rack_base[1], rack_base[2] + 0.04, 0.10, 0.05, 0.08, P["iron_dark"], outline=False)
    mk.cbox(c, rack_base[0], rack_base[1], rack_base[2] + 0.04, 0.11, 0.06, 0.018, P["odoshi"], outline=False)

    # Bainhas de katanas troféu cruzadas firmemente para trás (compactas junto à coluna)
    d1 = mk.norm((-fx * 0.18 + px * 0.24, -fy * 0.18 + py * 0.24, 0.92))
    d2 = mk.norm((-fx * 0.18 - px * 0.24, -fy * 0.18 - py * 0.24, 0.92))
    mk.obox(c, rack_base, d1, 0.36, 0.026, 0.022, P["iron_dark"])
    mk.obox(c, rack_base, d2, 0.36, 0.026, 0.022, P["iron_dark"])

    # Empunhaduras de bronze sobre o rack
    p_h1 = mk.add(rack_base, d1, 0.32)
    p_h2 = mk.add(rack_base, d2, 0.32)
    mk.obox(c, p_h1, d1, 0.10, 0.028, 0.028, P["bronze"], outline=False)
    mk.obox(c, p_h2, d2, 0.10, 0.028, 0.028, P["bronze"], outline=False)


def _draw_naginata_prop(c, hand_pt, direction, length=1.80, blade_len=0.65):
    """
    Desenha a Naginata monumental empunhada:
    - Mastro maciço de carvalho reforçado com anéis de latão.
    - Ponteira afiada de ferro na base (Ishizuki).
    - Tsuba circular de bronze e Habaki dourado.
    - Lâmina curva reluzente de aço com fio afiado.
    """
    P = pal()
    d = mk.norm(direction)
    shaft_len = length - blade_len
    grip_offset = shaft_len * 0.38

    base_pt = mk.add(hand_pt, d, -grip_offset)
    collar_pt = mk.add(hand_pt, d, shaft_len - grip_offset)

    # 1. Haste de carvalho negro
    mk.obox(c, base_pt, d, shaft_len, 0.040, 0.040, P["wood_shaft"])
    # Ponteira de ferro inferior (Ishizuki)
    mk.obox(c, mk.add(base_pt, d, -0.06), d, 0.065, 0.044, 0.044, P["ishizuki"])

    # 2. Anéis de reforço de latão ao longo do cabo
    for ring_frac in (0.25, 0.50, 0.75, 0.95):
        rp = mk.add(base_pt, d, shaft_len * ring_frac)
        mk.obox(c, rp, d, 0.024, 0.046, 0.046, P["brass_ring"], outline=False)

    # 3. Tsuba e Habaki
    mk.obox(c, collar_pt, d, 0.022, 0.088, 0.088, P["tsuba"])
    mk.obox(c, mk.add(collar_pt, d, 0.022), d, 0.035, 0.055, 0.045, P["habaki"], outline=False)

    # 4. Lâmina Curva Colossal de Naginata
    blade_start = mk.add(collar_pt, d, 0.057)
    mk.obox(c, blade_start, d, blade_len, 0.058, 0.030, P["steel"])
    # Fio de corte polido (Ha)
    mk.obox(c, mk.add(blade_start, d, 0.015), d, blade_len - 0.02, 0.024, 0.034, P["steel_edge"], outline=False)
    return mk.add(blade_start, d, blade_len)


def _render_weapon_and_hands(c, left_hand, right_hand):
    """Renderiza as manoplas Tekkō e a Naginata."""
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    has_weapon = c.extra_props.get("has_naginata", True) if c.extra_props else True

    # Manoplas de ferro Tekkō articuladas nos punhos
    for hand, s_sign in ((left_hand, 1.0), (right_hand, -1.0)):
        mk.obox(c, hand, (fx * 0.8 + px * s_sign * 0.2, fy * 0.8 + py * s_sign * 0.2, 0.0), 0.075, 0.068, 0.065, P["iron"])
        # Placa de proteção dos nós dos dedos
        mk.obox(c, mk.add(hand, (fx, fy, 0.0), 0.030), (fx, fy, 0.0), 0.035, 0.065, 0.030, P["iron_light"], outline=False)

    if not has_weapon:
        is_charge = c.extra_props.get("is_charging", False) if c.extra_props else False
        if is_charge:
            shock_c = (c.base_x + fx * 0.35, c.base_y + fy * 0.35, c.torso_z + 0.12)
            pts = [
                (shock_c[0] + px * 0.25, shock_c[1] + py * 0.25, shock_c[2]),
                (shock_c[0] + fx * 0.15, shock_c[1] + fy * 0.15, shock_c[2] + 0.22),
                (shock_c[0] - px * 0.25, shock_c[1] - py * 0.25, shock_c[2]),
                (shock_c[0] - fx * 0.15, shock_c[1] - fy * 0.15, shock_c[2] - 0.22),
            ]
            mk.band(c, pts, P["thrust_trail"] + (185,))
        return

    # Desenho da Naginata empunhada
    if c.is_melee:
        p = c.atk_progress
        is_throw = c.extra_props.get("is_throwing", False) if c.extra_props else False
        hoist_phase = c.extra_props.get("hoist_slam_phase") if c.extra_props else None
        hoist_prog = c.extra_props.get("hoist_slam_prog", 0.0) if c.extra_props else 0.0

        if hoist_phase == "HOIST":
            dir_hoist = mk.norm((fx * (0.95 - hoist_prog * 0.65) + px * 0.04, fy * (0.95 - hoist_prog * 0.65) + py * 0.04, 0.08 + hoist_prog * 0.88))
            tip = _draw_naginata_prop(c, right_hand, dir_hoist, length=1.85)
            if hoist_prog > 0.15:
                trail_c = mk.lerp(right_hand, tip, 0.70)
                pts = [
                    (tip[0] + px * 0.08, tip[1] + py * 0.08, tip[2] + 0.08),
                    (tip[0] - px * 0.08, tip[1] - py * 0.08, tip[2] - 0.08),
                    (trail_c[0] - px * 0.05, trail_c[1] - py * 0.05, trail_c[2] - 0.12),
                    (trail_c[0] + px * 0.05, trail_c[1] + py * 0.05, trail_c[2] - 0.12),
                ]
                mk.band(c, pts, (180, 25, 25, 190))

        elif hoist_phase == "SLAM":
            slam_curve = hoist_prog ** 1.8
            dir_slam = mk.norm((fx * (0.30 + slam_curve * 0.55) + px * 0.02, fy * (0.30 + slam_curve * 0.55) + py * 0.02, 0.95 - slam_curve * 1.55))
            tip = _draw_naginata_prop(c, right_hand, dir_slam, length=1.85)
            trail_c = mk.lerp(right_hand, tip, 0.60)
            pts = [
                (tip[0] + px * 0.12, tip[1] + py * 0.12, tip[2] + 0.10),
                (tip[0] - px * 0.12, tip[1] - py * 0.12, tip[2] - 0.10),
                (trail_c[0] - px * 0.06, trail_c[1] - py * 0.06, trail_c[2] + 0.20),
                (trail_c[0] + px * 0.06, trail_c[1] + py * 0.06, trail_c[2] + 0.20),
            ]
            mk.band(c, pts, P["thrust_trail"] + (210,))
            mk.band(c, (mk.lerp(pts[0], pts[1], 0.25), mk.lerp(pts[0], pts[1], 0.75), mk.lerp(pts[2], pts[3], 0.75), mk.lerp(pts[2], pts[3], 0.25)), (255, 240, 210, 230))

        elif is_throw:
            dir_throw = mk.norm((fx * 0.85, fy * 0.85, 0.20 - p * 0.10))
            tip = _draw_naginata_prop(c, right_hand, dir_throw, length=1.75)
        else:
            dir_thrust = mk.norm((fx * 0.96 + px * 0.04, fy * 0.96 + py * 0.04, 0.05))
            tip = _draw_naginata_prop(c, right_hand, dir_thrust, length=1.80)
            if 0.12 < p < 0.85:
                r_cone = 0.10 * math.sin(p * math.pi)
                c_mid = mk.lerp(right_hand, tip, 0.50)
                p0 = (tip[0] + px * r_cone, tip[1] + py * r_cone, tip[2] + r_cone)
                p1 = (tip[0] - px * r_cone, tip[1] - py * r_cone, tip[2] - r_cone)
                p2 = (c_mid[0] - px * r_cone * 0.5, c_mid[1] - py * r_cone * 0.5, c_mid[2] - r_cone * 0.5)
                p3 = (c_mid[0] + px * r_cone * 0.5, c_mid[1] + py * r_cone * 0.5, c_mid[2] + r_cone * 0.5)
                mk.band(c, (p0, p1, p2, p3), P["thrust_trail"] + (215,))
                mk.band(c, (mk.lerp(p0, p1, 0.25), mk.lerp(p0, p1, 0.75), mk.lerp(p2, p3, 0.75), mk.lerp(p2, p3, 0.25)), P["trail_core"] + (245,))
    else:
        # Guarda Neutra (Diagonal imponente à frente do corpo com ambas as mãos)
        weapon_dir = mk.norm((fx * 0.65 + px * 0.28, fy * 0.65 + py * 0.28, 0.72))
        _draw_naginata_prop(c, right_hand, weapon_dir, length=1.75)


def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Rack de armas troféu das 999 lutas na Ponte Gojō (se o rack estiver no lado oposto à câmera).
    - Se a Naginata estiver no lado oposto à câmera, desenha ela aqui ANTES do tronco para oclusão.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    d_rack = mk.depth(c, c.base_x - c.fx * 0.14, c.base_y - c.fy * 0.14)
    if d_rack < d_torso:
        _draw_trophy_rack(c)

    # Ordenação dinâmica: se o ponto médio da empunhadura estiver atrás do tronco, desenha aqui
    hand_l, hand_r = _hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_weapon_and_hands(c, hand_l, hand_r)


def draw_legs(c):
    """Pernas monumentais com grevas de ferro negro (Suneate) sobre hakama escuro."""
    P = pal()
    for leg_key, side_sign in (("L", 1.0), ("R", -1.0)):
        ld = c.legs_data.get(leg_key)
        if not ld:
            continue
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]

        # Coxa com hakama volumoso de monge guerreiro (tapered 3D)
        th_top = (th[0], th[1], th[2] + 0.20)
        th_bot = (sh[0], sh[1], sh[2] + 0.14)
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            th_top, th_bot,
            w_start=0.170, h_start=0.170,
            w_end=0.140, h_end=0.140,
            color=P["hakama"],
            up=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
            cap_end=False,
        )

        # Greva de ferro na canela (Suneate)
        sh_top = (sh[0], sh[1], sh[2] + 0.14)
        sh_bot = (ft[0], ft[1], ft[2] + 0.05)
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            sh_top, sh_bot,
            w_start=0.135, h_start=0.135,
            w_end=0.110, h_end=0.110,
            color=P["suneate"],
            up=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
            cap_end=False,
        )
        # Crista frontal de bronze reforçada na canela
        mk.obox(c, (sh[0] + c.fx * 0.060, sh[1] + c.fy * 0.060, sh[2] + 0.07),
                (c.fx, c.fy, 0.0), 0.032, 0.065, 0.14, P["bronze"], outline=False)

        # Sandália Waraji com tiras pretas
        flen, fwidth = 0.17, 0.09
        mk.cbox(c, ft[0] + c.fx * (flen * 0.22), ft[1] + c.fy * (flen * 0.22), ft[2] + 0.018,
                flen, fwidth, 0.036, P["waraji"], outline=True)
        # Tiras trançadas da sandália
        mk.cbox(c, ft[0] + c.fx * (flen * 0.22), ft[1] + c.fy * (flen * 0.22), ft[2] + 0.038,
                flen * 0.70, fwidth * 0.75, 0.015, P["strap"], outline=False)


def draw_belt(c):
    """Cinturão de batalha com placas articuladas (kusazuri) e faixa vermelha odoshi."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.075

    # Cinto principal de placas de ferro laqueado
    mk.cbox(c, bx, by, z, c.pelvis_w, c.pelvis_w * 0.75, 0.080, P["iron"], outline=True)
    # Fileira de odoshi vermelho
    mk.cbox(c, bx, by, z - 0.018, c.pelvis_w - 0.01, c.pelvis_w * 0.73, 0.024, P["odoshi"], outline=False)

    # 4 abas protetoras de quadril e coxas (kusazuri)
    # Aba frontal
    if mk.depth(c, fx, fy) > -0.05:
        f_pos = (bx + fx * 0.13, by + fy * 0.13, z - 0.08)
        mk.obox(c, f_pos, (fx * 0.2, fy * 0.2, -0.95), 0.12, 0.028, 0.15, P["iron"])
        mk.obox(c, mk.add(f_pos, (0, 0, -0.05)), (fx * 0.2, fy * 0.2, -0.95), 0.11, 0.032, 0.022, P["bronze"], outline=False)
        mk.obox(c, mk.add(f_pos, (0, 0, -0.02)), (fx * 0.2, fy * 0.2, -0.95), 0.10, 0.030, 0.015, P["odoshi"], outline=False)

    # Abas laterais
    for s_sign in (-1.0, 1.0):
        lat_pos = (bx + px * (0.16 * s_sign), by + py * (0.16 * s_sign), z - 0.08)
        mk.obox(c, lat_pos, (px * s_sign * 0.25, py * s_sign * 0.25, -0.95), 0.11, 0.028, 0.14, P["iron"])
        mk.obox(c, mk.add(lat_pos, (0, 0, -0.045)), (px * s_sign * 0.25, py * s_sign * 0.25, -0.95), 0.10, 0.030, 0.020, P["bronze"], outline=False)


def draw_torso(c):
    """
    Tronco monumental do Walking Tank:
    - Lamellae horizontais reforçadas no peitoral Dō-maru com rebites de bronze e odoshi.
    - Colar de contas Mala budistas gigantes pendurado no peito.
    - Manto inferior do capuz monástico de linho cru assentado sobre os ombros e clavículas.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    front_d = 0.128

    if mk.depth(c, fx, fy) > -0.05:
        # Placas horizontais de sobreposição do peitoral Dō-maru
        for dz in (0.06, 0.13, 0.20):
            mk.cbox(c, bx + fx * front_d, by + fy * front_d, tz + dz, 0.24, 0.024, 0.028, P["iron_light"], outline=False)
            mk.cbox(c, bx + fx * (front_d + 0.004), by + fy * (front_d + 0.004), tz + dz - 0.012, 0.22, 0.020, 0.014, P["odoshi"], outline=False)

        # Grande colar Mala de contas de oração budistas no peito
        bead_coords = [
            (bx + fx * 0.115 + px * 0.09, by + fy * 0.115 + py * 0.09, tz + 0.22),
            (bx + fx * 0.125 + px * 0.05, by + fy * 0.125 + py * 0.05, tz + 0.16),
            (bx + fx * 0.135 + px * 0.02, by + fy * 0.135 + py * 0.02, tz + 0.10),
            (bx + fx * 0.140, by + fy * 0.140, tz + 0.05),  # Centro / Guru bead
            (bx + fx * 0.135 - px * 0.02, by + fy * 0.135 - py * 0.02, tz + 0.10),
            (bx + fx * 0.125 - px * 0.05, by + fy * 0.125 - py * 0.05, tz + 0.16),
            (bx + fx * 0.115 - px * 0.09, by + fy * 0.115 - py * 0.09, tz + 0.22),
        ]
        for i, pt in enumerate(bead_coords):
            color = P["bead_gold"] if i == 3 else P["bead"]
            mk.cbox(c, pt[0], pt[1], pt[2], 0.040, 0.040, 0.040, color, outline=False)

    # Manto/gola do capuz monástico de linho cru assentado na base do pescoço
    nz = tz + 0.26
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, nz - 0.040),
        (bx, by, nz + 0.030),
        w_start=0.185, h_start=0.185,
        w_end=0.145, h_end=0.145,
        color=P["cowl"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
        cap_end=False,
    )
    # Detalhes dorsais: se o guerreiro estiver de costas para a câmera
    if mk.depth(c, -fx, -fy) > -0.05:
        back_d = 0.125
        # Lamellae horizontais dorsais laqueadas
        for dz in (0.07, 0.14, 0.20):
            mk.cbox(c, bx - fx * back_d, by - fy * back_d, tz + dz, 0.22, 0.022, 0.026, P["iron_light"], outline=False)
            mk.cbox(c, bx - fx * (back_d + 0.004), by - fy * (back_d + 0.004), tz + dz - 0.010, 0.20, 0.018, 0.012, P["odoshi"], outline=False)

        # Laço Agemaki carmim nas costas (nó tradicional de armadura sōhei/samurai)
        mk.cbox(c, bx - fx * (back_d + 0.012), by - fy * (back_d + 0.012), tz + 0.16, 0.045, 0.022, 0.045, P["odoshi"], outline=False)
        mk.cbox(c, bx - fx * (back_d + 0.016), by - fy * (back_d + 0.016), tz + 0.16, 0.024, 0.024, 0.024, P["bronze"], outline=False)
        for t_side in (-1.0, 1.0):
            mk.obox(c, (bx - fx * (back_d + 0.014) + px * 0.025 * t_side, by - fy * (back_d + 0.014) + py * 0.025 * t_side, tz + 0.14),
                    (px * t_side * 0.35, py * t_side * 0.35, -0.92), 0.08, 0.018, 0.018, P["odoshi"], outline=False)

    # Ombreiras monumentais pesadas articuladas (Ō-sode)
    # Assentadas perfeitamente no topo e laterais dos ombros (tz + 0.235)
    sh_x = 0.185
    order = sorted((-1.0, 1.0), key=lambda s: mk.depth(c, bx + px * (sh_x * s), by + py * (sh_x * s)))
    up_sode = (fx, fy, 0.0)
    for side in order:
        sx = bx + px * (sh_x * side)
        sy = by + py * (sh_x * side)
        sz = tz + 0.235
        sode_dir = mk.norm((px * side * 0.25, py * side * 0.25, -0.95))

        # 1. Placa superior monumental do Ō-sode (Kamuri-ita e 1ª lamelar)
        # Cobre o ombro desde a frente do peitoral até a escápula dorsal (span de 0.24m)
        p1 = (sx - fx * 0.015 + px * side * 0.012, sy - fy * 0.015 + py * side * 0.012, sz)
        mk.obox(c, p1, sode_dir, 0.160, 0.058, 0.240, P["iron"], up=up_sode, texture="metal")
        # Rebordos reforçados de bronze brilhante e odoshi carmim
        mk.obox(c, (p1[0], p1[1], p1[2] + 0.006), sode_dir, 0.035, 0.064, 0.246, P["bronze_bright"], up=up_sode, outline=False)
        mk.obox(c, mk.add(p1, sode_dir, 0.070), sode_dir, 0.020, 0.062, 0.242, P["odoshi"], up=up_sode, outline=False)

        # 2. Placa inferior sobreposta do Ō-sode
        p2 = mk.add(p1, sode_dir, 0.085)
        mk.obox(c, p2, sode_dir, 0.150, 0.052, 0.225, P["iron"], up=up_sode, texture="metal")
        mk.obox(c, mk.add(p2, sode_dir, 0.065), sode_dir, 0.020, 0.056, 0.228, P["odoshi"], up=up_sode, outline=False)
        mk.obox(c, mk.add(p2, sode_dir, 0.125), sode_dir, 0.022, 0.058, 0.230, P["bronze"], up=up_sode, outline=False)

        # Tiras watagami fixando o topo da ombreira à couraça sobre o ombro
        mk.obox(c, (sx - fx * 0.08, sy - fy * 0.08, sz + 0.008), (fx, fy, 0.0), 0.18, 0.055, 0.024, P["iron_light"], outline=False)
        mk.obox(c, (sx - fx * 0.06, sy - fy * 0.06, sz + 0.016), (fx, fy, 0.0), 0.14, 0.044, 0.016, P["bronze"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço maciço: manga monástica escura com braçadeiras de ferro negro (Kote) e manoplas Tekkō."""
    P = pal()
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["hakama"],
        sleeve_to=0.35,
        bracer=P["iron"],
        bracer_span=(0.48, 0.95),
        glove=P["iron"],
        w=0.082,
        bend=0.04
    )


def draw_head(c):
    """
    Cabeça do Monge Guerreiro Benkei:
    - Capuz monástico de linho cru (zukin) esculpido com facetas integradas.
    - O rosto marcial severo, olhos determinados, nariz forte e barba/mustache em 3D
      são esculpidos por draw_sculpted_head_3d e draw_portrait_face_3d.
    - Aqui são modeladas as dobras de tecido do capuz ao redor da fronte e têmporas,
      completamente livres de caixas fechadas ou artefatos de chaminé.
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    hz = c.head_z
    hw = c.head_w

    # 1. Dobra frontal de linho do capuz na testa (acima da linha das sobrancelhas)
    z_b0 = hz + 0.106
    z_b1 = hz + 0.148
    r0 = hw * 0.50 + 0.004
    r1 = hw * 0.48 + 0.003

    fl0 = (bx + fx * r0 - px * r0, by + fy * r0 - py * r0, z_b0)
    fr0 = (bx + fx * r0 + px * r0, by + fy * r0 + py * r0, z_b0)
    br0 = (bx - fx * r0 + px * r0, by - fy * r0 + py * r0, z_b0)
    bl0 = (bx - fx * r0 - px * r0, by - fy * r0 - py * r0, z_b0)

    fl1 = (bx + fx * r1 - px * r1, by + fy * r1 - py * r1, z_b1)
    fr1 = (bx + fx * r1 + px * r1, by + fy * r1 + py * r1, z_b1)
    br1 = (bx - fx * r1 + px * r1, by - fy * r1 + py * r1, z_b1)
    bl1 = (bx - fx * r1 - px * r1, by - fy * r1 - py * r1, z_b1)

    s_fl0 = c.camera.apply(fl0[0], fl0[1], fl0[2])
    s_fr0 = c.camera.apply(fr0[0], fr0[1], fr0[2])
    s_br0 = c.camera.apply(br0[0], br0[1], br0[2])
    s_bl0 = c.camera.apply(bl0[0], bl0[1], bl0[2])

    s_fl1 = c.camera.apply(fl1[0], fl1[1], fl1[2])
    s_fr1 = c.camera.apply(fr1[0], fr1[1], fr1[2])
    s_br1 = c.camera.apply(br1[0], br1[1], br1[2])
    s_bl1 = c.camera.apply(bl1[0], bl1[1], bl1[2])

    azimuth = getattr(c.camera, "azimuth", 0.0)
    fn_rx, fn_ry = mk.rotate_xy(fx, fy, azimuth)
    rn_rx, rn_ry = mk.rotate_xy(px, py, azimuth)

    hood_faces = [
        ((fn_rx + fn_ry) > -0.05, (fn_rx + fn_ry) * r0, [s_fl0, s_fr0, s_fr1, s_fl1], P["cowl"], True),
        ((rn_rx + rn_ry) > -0.05, (rn_rx + rn_ry) * r0, [s_fr0, s_br0, s_br1, s_fr1], P["cowl_shadow"], False),
        ((-fn_rx - fn_ry) > -0.05, (-fn_rx - fn_ry) * r0, [s_br0, s_bl0, s_bl1, s_br1], P["cowl_dark"], False),
        ((-rn_rx - rn_ry) > -0.05, (-rn_rx - rn_ry) * r0, [s_bl0, s_fl0, s_fl1, s_bl1], P["cowl_shadow"], False),
    ]
    hood_faces.sort(key=lambda item: item[1])
    for visible, _, poly, col, is_front in hood_faces:
        if visible:
            pygame.draw.polygon(c.surface, col, poly)
            if is_front:
                # Dobra de linho do capuz sobre a testa
                pygame.draw.line(c.surface, P["cowl_light"], poly[3], poly[2], 1)

    # 2. Dobra traseira do capuz na nuca
    d_torso = mk.depth(c, bx, by)
    d_nape = mk.depth(c, bx - fx * 0.08, by - fy * 0.08)
    if d_nape > d_torso - 0.02:
        nape_pt = (bx - fx * 0.075, by - fy * 0.075, hz + 0.035)
        mk.obox(c, nape_pt, (-fx * 0.2, -fy * 0.2, -0.95), 0.13, 0.040, 0.075, P["cowl_shadow"], outline=False)


def draw_front(c, left_hand, right_hand):
    """
    Camada frontal (Painter's Algorithm):
    - Rack de armas troféu das 999 lutas na Ponte Gojō (se o dorso estiver voltado para a câmera).
    - Naginata e manoplas são renderizadas aqui APENAS se as mãos estiverem à frente do tronco.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    d_rack = mk.depth(c, c.base_x - c.fx * 0.14, c.base_y - c.fy * 0.14)
    if d_rack >= d_torso:
        _draw_trophy_rack(c)

    w_mid = ((left_hand[0] + right_hand[0]) * 0.5, (left_hand[1] + right_hand[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_weapon_and_hands(c, left_hand, right_hand)
