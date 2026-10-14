"""
Benkei, o Guardião da Naginata / Walking Tank Colossal (Ciclo 2):
- Guerreiro sōhei imponente blindado em armadura pesada de placas de ferro laqueadas a preto (dō-maru/ō-yoroi).
- Capuz monástico de linho cru cobrindo o topo da cabeça e ombros, emoldurando uma face severa e calejada.
- Colar de contas budistas pesadas de cedro escuro com contas douradas de intervalo.
- Ombreiras monumentais de ferro (ō-sode) articuladas em camadas com cordões vermelhos (odoshi).
- Naginata colossal:
  - Haste maciça de carvalho negro com anéis de latão e ponteira inferior de ferro (ishizuki).
  - Lâmina curva pesada de aço brilhante forjado com colarinho de ouro (habaki) e tsuba circular.
  - Se desarmado (após arremesso), adota postura de investida pesada de atropelamento com as manoplas de ferro.
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth

SKIN = (218, 172, 138)
SKIN_SHADOW = (180, 134, 104)

PALETTE = {
    # Armadura de Ferro Negro e Bronze
    "iron": (24, 22, 26),
    "torso": (24, 22, 26),
    "iron_dark": (14, 12, 16),
    "iron_light": (45, 42, 48),
    "bronze": (175, 125, 45),
    "bronze_bright": (215, 165, 60),
    "odoshi": (165, 30, 36),       # Cordões vermelhos de amarração
    "odoshi_dark": (110, 18, 24),

    # Capuz e Vestes Monásticas
    "cowl": (220, 215, 205),
    "cowl_shadow": (170, 165, 155),
    "cowl_dark": (130, 125, 115),
    "hakama": (30, 28, 32),
    "pants": (30, 28, 32),
    "belt": (165, 30, 36),

    # Anatomia e Rosto
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "hair": (32, 28, 26),
    "beard": (35, 30, 28),
    "scar": (195, 115, 105),
    "eye": (30, 26, 24),
    "brow": (25, 20, 18),

    # Adornos Sagrados
    "bead": (65, 35, 20),
    "bead_dark": (45, 24, 14),
    "bead_gold": (220, 175, 50),

    # Perneiras e Calçados
    "suneate": (20, 18, 22),       # Grevas de ferro nas canelas
    "waraji": (175, 145, 100),
    "strap": (32, 28, 26),

    # Naginata (Arma Pesada)
    "wood_shaft": (36, 26, 20),
    "wood_shaft_dark": (24, 16, 12),
    "brass_ring": (195, 145, 55),
    "habaki": (225, 185, 65),
    "tsuba": (160, 115, 40),
    "steel": (228, 236, 248),
    "steel_edge": (255, 255, 255),
    "ishizuki": (30, 28, 32),
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
    """
    Guarda imponente de Benkei com duas mãos na Naginata (ou postura de investida se desarmado).
    """
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
    """
    Animações de Ataque:
    1. Estocada Frontal Colossal (Alcance 3.0 tiles - perfuração profunda em linha reta).
    2. Arremesso da Naginata (Recuo com torção de tronco e arremesso em arco potente).
    3. Investida de Recuperação (Desarmado - carga com ombro blindado).
    """
    p = c.atk_progress
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    is_throw = c.extra_props.get("is_throwing", False) if c.extra_props else False
    is_charge = c.extra_props.get("is_charging", False) if c.extra_props else False

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
    # Impulso maciço dos dois braços em linha reta para a frente
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


# ---------------------------------------------------------------------------------------------------------------------
# Detalhamento Voxel do Guerreiro
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Trás de Benkei:
    - O rack de armas coletadas nas costas (troféus das 999 lutas na Ponte Gojō).
    - Bainhas de katanas presas em cruz e o cabo de um machado de batalha pesado nas costas.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    # Bainhas de katanas troféu cruzadas nas costas
    back_origin = (bx - fx * 0.14, by - fy * 0.14, tz + 0.05)
    mk.obox(c, back_origin, mk.norm((fx * 0.3 + px * 0.6, fy * 0.3 + py * 0.6, 0.85)), 0.65, 0.034, 0.026, P["iron_dark"])
    mk.obox(c, back_origin, mk.norm((fx * 0.3 - px * 0.6, fy * 0.3 - py * 0.6, 0.85)), 0.65, 0.034, 0.026, P["iron_dark"])
    # Empunhaduras das armas troféu que sobressaem sobre os ombros
    mk.obox(c, (bx - fx * 0.16 + px * 0.12, by - fy * 0.16 + py * 0.12, tz + 0.28), mk.norm((px * 0.4, py * 0.4, 0.9)), 0.16, 0.032, 0.032, P["bronze"])
    mk.obox(c, (bx - fx * 0.16 - px * 0.12, by - fy * 0.16 - py * 0.12, tz + 0.28), mk.norm((-px * 0.4, -py * 0.4, 0.9)), 0.16, 0.032, 0.032, P["bronze"])


def draw_legs(c):
    """
    Pernas monumentais com grevas de ferro negro (Suneate) sobre hakama escuro.
    """
    P = pal()
    # Perna esquerda ("L") e direita ("R")
    for leg_key, side_sign in (("L", 1.0), ("R", -1.0)):
        ld = c.legs_data.get(leg_key)
        if not ld:
            continue
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]
        # Coxa com hakama volumoso
        mk.cbox(c, th[0], th[1], th[2], 0.16, 0.16, 0.24, P["hakama"], texture="canvas")
        # Greva de ferro na canela (Suneate) com bordas de bronze
        mk.cbox(c, sh[0], sh[1], sh[2] + 0.05, 0.13, 0.13, 0.20, P["suneate"], outline=True, texture="metal")
        mk.cbox(c, sh[0] + c.fx * 0.065, sh[1] + c.fy * 0.065, sh[2] + 0.05, 0.035, 0.08, 0.18, P["bronze"], outline=False)
        # Sandália Waraji com tiras pretas
        mk.obox(c, (ft[0] - c.fx * 0.05, ft[1] - c.fy * 0.05, ft[2]), (c.fx, c.fy, 0.0), 0.16, 0.09, 0.035, P["waraji"])
        mk.obox(c, (ft[0] - c.fx * 0.02, ft[1] - c.fy * 0.02, ft[2] + 0.03), (c.fx, c.fy, 0.0), 0.13, 0.075, 0.04, P["strap"], outline=False)


def draw_belt(c):
    """
    Cinturão de batalha de placas articuladas (kusazuri) e faixa vermelha odoshi.
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07

    # Placas de saia de armadura (kusazuri) que protegem coxas e virilha
    mk.cbox(c, bx, by, z, c.pelvis_w + 0.02, c.pelvis_w * 0.76, 0.09, P["iron"], outline=True, texture="metal")
    # Fileira de odoshi vermelho na borda inferior do cinturão
    mk.cbox(c, bx, by, z - 0.02, c.pelvis_w + 0.015, c.pelvis_w * 0.74, 0.03, P["odoshi"], outline=False)
    # Fivela central de bronze
    mk.cbox(c, bx + fx * (c.pelvis_w * 0.38 + 0.01), by + fy * (c.pelvis_w * 0.38 + 0.01), z + 0.02, 0.06, 0.04, 0.07, P["bronze"], outline=False)


def draw_torso(c):
    """
    Tronco imponente do Walking Tank:
    - Couraça de ferro negro laqueado (Dō-maru).
    - Ombreiras monumentais (Ō-sode) em camadas com bordas douradas.
    - Colar de contas Mala budistas gigantes pendurado no peito.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    # 1. Peitoral de ferro maciço (Dō-maru)
    mk.cbox(c, bx, by, tz + 0.04, 0.26, 0.19, 0.26, P["iron"], outline=True, texture="metal")
    # Placas horizontais de sobreposição do peitoral
    for dz in (0.08, 0.15, 0.22):
        mk.cbox(c, bx + fx * 0.096, by + fy * 0.096, tz + dz, 0.21, 0.03, 0.025, P["iron_light"], outline=False)
        mk.cbox(c, bx + fx * 0.098, by + fy * 0.098, tz + dz - 0.015, 0.19, 0.025, 0.012, P["odoshi"], outline=False)

    # 2. Ombreiras monumentais pesadas (Ō-sode)
    sode_w, sode_d, sode_h = 0.14, 0.14, 0.24
    for side_sign in (-1.0, 1.0):
        sx = bx + px * (0.19 * side_sign)
        sy = by + py * (0.19 * side_sign)
        sz = tz + 0.16
        # Bloco da ombreira
        mk.cbox(c, sx, sy, sz, sode_w, sode_d, sode_h, P["iron"], outline=True, texture="metal")
        # Rebordos de bronze e cordões vermelhos
        mk.cbox(c, sx, sy, sz + sode_h - 0.03, sode_w + 0.01, sode_d + 0.01, 0.03, P["bronze"], outline=False)
        mk.cbox(c, sx, sy, sz + 0.04, sode_w + 0.005, sode_d + 0.005, 0.02, P["odoshi"], outline=False)

    # 3. Grande colar Mala de contas de oração budistas
    bead_coords = [
        (bx + fx * 0.10 + px * 0.08, by + fy * 0.10 + py * 0.08, tz + 0.24),
        (bx + fx * 0.11 + px * 0.05, by + fy * 0.11 + py * 0.05, tz + 0.18),
        (bx + fx * 0.12 + px * 0.02, by + fy * 0.12 + py * 0.02, tz + 0.12),
        (bx + fx * 0.125, by + fy * 0.125, tz + 0.07),  # Centro / Guru bead
        (bx + fx * 0.12 - px * 0.02, by + fy * 0.12 - py * 0.02, tz + 0.12),
        (bx + fx * 0.11 - px * 0.05, by + fy * 0.11 - py * 0.05, tz + 0.18),
        (bx + fx * 0.10 - px * 0.08, by + fy * 0.10 - py * 0.08, tz + 0.24),
    ]
    for i, pt in enumerate(bead_coords):
        color = P["bead_gold"] if i == 3 else P["bead"]
        mk.cbox(c, pt[0], pt[1], pt[2], 0.038, 0.038, 0.038, color, outline=False)


def draw_arm(c, shoulder, hand, side):
    """
    Braço de ferro: manga interior escura com braçadeiras de placas articuladas (Kote).
    """
    P = pal()
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["hakama"],
        sleeve_to=0.35,
        bracer=P["iron"],
        bracer_span=(0.50, 0.94),
        w=0.078,
        bend=0.04
    )


def draw_head(c):
    """
    Cabeça de Benkei:
    - Capuz monástico de linho cru (Cowl) que cobre topo e laterais.
    - Rosto severo e barbado com cicatriz de batalha transversal.
    - Olhos penetrantes de determinação inabalável.
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    hz = c.head_z
    hw = c.head_w + 0.02  # Porte mais largo

    # 1. Capuz monástico (Cowl) envolvente
    mk.cbox(c, bx, by, hz + 0.04, hw + 0.03, hw + 0.03, 0.18, P["cowl"], outline=True, texture="canvas")
    mk.cbox(c, bx - fx * 0.02, by - fy * 0.02, hz + 0.17, hw + 0.01, hw + 0.01, 0.04, P["cowl_shadow"], outline=False)

    # 2. Rosto esculpido na abertura do capuz
    face_z = hz + 0.02
    mk.cbox(c, bx + fx * 0.02, by + fy * 0.02, face_z, hw - 0.03, hw - 0.03, 0.14, P["skin"], outline=False)

    if mk.facing_camera(c):
        front_d = hw / 2 + 0.005
        # Barba cerrada no queixo e maxilar
        mk.cbox(c, bx + fx * front_d, by + fy * front_d, face_z + 0.02, hw - 0.05, 0.03, 0.06, P["beard"], outline=False)
        # Cicatriz de lâmina transversal no olho/bochecha esquerda
        mk.cbox(c, bx + fx * front_d + px * 0.03, by + fy * front_d + py * 0.03, face_z + 0.09, 0.012, 0.02, 0.05, P["scar"], outline=False)
        # Olhos sombrios de guerreiro
        for side in (-1.0, 1.0):
            ex = bx + fx * front_d + px * (0.032 * side)
            ey = by + fy * front_d + py * (0.032 * side)
            mk.cbox(c, ex, ey, face_z + 0.09, 0.020, 0.014, 0.014, P["eye"], outline=False)
            mk.cbox(c, ex, ey, face_z + 0.11, 0.026, 0.015, 0.012, P["brow"], outline=False)


def _draw_naginata_prop(c, hand_pt, direction, length=1.75, blade_len=0.65):
    """
    Desenha a Naginata monumental empunhada:
    - Mastro negro de carvalho reforçado com anéis de latão.
    - Ponteira afiada de ferro na base (Ishizuki).
    - Tsuba circular de bronze e Habaki dourado.
    - Lâmina curva reluzente de aço com fio afiado.
    """
    P = pal()
    d = mk.norm(direction)
    shaft_len = length - blade_len
    grip_offset = shaft_len * 0.40  # Mão empunha próximo do terço superior da haste

    # Ponto base da haste (trás da mão) e ponto do colarinho da lâmina (frente)
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
    mk.obox(c, collar_pt, d, 0.022, 0.09, 0.09, P["tsuba"])
    mk.obox(c, mk.add(collar_pt, d, 0.022), d, 0.035, 0.055, 0.045, P["habaki"], outline=False)

    # 4. Lâmina Curva Colossal de Naginata
    blade_start = mk.add(collar_pt, d, 0.057)
    mk.obox(c, blade_start, d, blade_len, 0.058, 0.030, P["steel"])
    # Fio de corte polido (Ha)
    mk.obox(c, mk.add(blade_start, d, 0.015), d, blade_len - 0.02, 0.024, 0.034, P["steel_edge"], outline=False)

    # Retorna ponta da lâmina (Kissaki)
    return mk.add(blade_start, d, blade_len)


def draw_front(c, left_hand, right_hand):
    """
    Manoplas de ferro e empunhadura da Naginata, ou efeitos visuais de estocada colossal.
    """
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    has_weapon = c.extra_props.get("has_naginata", True) if c.extra_props else True

    # Manoplas de ferro pesado nos punhos
    for hand in (left_hand, right_hand):
        mk.cbox(c, hand[0], hand[1], hand[2], 0.082, 0.082, 0.075, P["iron"], outline=True)

    if not has_weapon:
        # Desarmado: investida de blindado (efeito de impacto de choque no ar ao correr)
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

        if is_throw:
            # Posição de arremesso
            dir_throw = mk.norm((fx * 0.85, fy * 0.85, 0.20 - p * 0.10))
            tip = _draw_naginata_prop(c, right_hand, dir_throw, length=1.75)
        else:
            # Estocada Frontal Colossal (Walking Tank Spear Thrust)
            dir_thrust = mk.norm((fx * 0.96 + px * 0.04, fy * 0.96 + py * 0.04, 0.05))
            tip = _draw_naginata_prop(c, right_hand, dir_thrust, length=1.80)

            # Rastro reluzente de estocada supersônica perfurante
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
        # Guarda Neutra (Diagonal à frente do corpo com ambas as mãos)
        weapon_dir = mk.norm((fx * 0.65 + px * 0.28, fy * 0.65 + py * 0.28, 0.72))
        _draw_naginata_prop(c, right_hand, weapon_dir, length=1.75)
