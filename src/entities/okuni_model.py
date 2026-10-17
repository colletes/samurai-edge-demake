"""
Okuni, mestra do Kabuki e dos leques Tessen (Izumo no Okuni):
- Rosto Oshiroi de porcelana branca pura, maquiagem teatral Kumadori carmim com asas nas têmporas.
- Olhos anime rubi expressivos com brilho duplo e cílios alados; lábios facetados em 3 planos com brilho cereja.
- Penteado tradicional Shimada em laca preta, coque alto, franja acima das sobrancelhas e grampos Kanzashi dourados com borlas de seda.
- Quimono Furisode cerimonial carmim em camadas com barra preta bordada a ouro e mangas longas ondulantes.
- Grande laço borboleta no Obi dourado nas costas com pontas esvoaçantes.
- Leques de guerra de ferro Tessen (fechados em guarda/marcha, abrindo-se em semicírculos radiantes de carmim e ouro nos golpes).
- Ordenação dinâmica de profundidade 3D (Painter's Algorithm) para oclusão perfeita dos leques e braços de costas.
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.mesh_primitives import (
    draw_ribbon_mesh_3d,
    draw_tapered_frustum_3d,
    draw_sculpted_head_3d,
    draw_portrait_face_3d,
)

PALETTE = {
    "kimono": (175, 24, 38),
    "kimono_dark": (118, 16, 28),
    "kimono_light": (215, 48, 62),
    "skirt": (28, 24, 32),
    "skirt_dark": (18, 15, 20),
    "collar": (252, 250, 248),
    "collar_gold": (224, 182, 54),
    "obi": (224, 182, 54),
    "obi_knot": (32, 28, 36),
    "tassel": (195, 30, 45),
    "skin": (252, 250, 248),
    "skin_shadow": (230, 224, 218),
    "hair": (22, 20, 26),
    "hair_light": (48, 42, 54),
    "hair_dark": (14, 12, 16),
    "kanzashi": (245, 205, 75),
    "fan_rib": (48, 44, 52),
    "fan_cloth": (185, 28, 42),
    "fan_gold": (240, 198, 65),
    "steel": (215, 222, 235),
    "tabi": (252, 250, 248),
    "geta": (145, 95, 55),
    "poison": (80, 220, 120),
    "aura": (195, 45, 85),
    "aura_core": (255, 225, 235),
}

MATERIALS = {
    "kimono": "silk", "kimono_dark": "silk", "kimono_light": "silk",
    "skirt": "silk", "obi": "gold", "kanzashi": "gold",
    "fan_cloth": "silk", "fan_gold": "gold", "steel": "steel",
    "geta": "wood"
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Leques Tessen
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """Guarda graciosa de dançarina: leque direito em semicírculo diante do peito, leque esquerdo invertido ao lado."""
    tz = c.torso_z + math.sin(c.walk_timer * 2.8) * 0.012
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    right = (bx + fx * 0.16 - px * 0.06, by + fy * 0.16 - py * 0.06, tz + 0.12)
    left = (bx + fx * 0.06 + px * 0.14, by + fy * 0.06 + py * 0.14, tz + 0.02)
    return left, right


def attack_arms(c):
    """Ataque rodopiante de leques de ferro (Tessen-jutsu): leque direito cortando em leque e esquerdo bloqueando."""
    p = c.atk_progress if c.atk_progress is not None else 0.0
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    sw = math.sin(p * math.pi)
    right = (bx + fx * (0.18 + sw * 0.28) - px * (0.04 - p * 0.18),
             by + fy * (0.18 + sw * 0.28) - py * (0.04 - p * 0.18),
             tz + 0.15 + sw * 0.12)
    left = (bx + fx * (0.10 + p * 0.16) + px * (0.12 - p * 0.10),
            by + fy * (0.10 + p * 0.16) + py * (0.12 - p * 0.10),
            tz + 0.06 + sw * 0.08)
    return left, right


def _current_hands(c):
    if c.is_melee and c.atk_progress is not None:
        return attack_arms(c)
    if c.is_moving and hasattr(c, "walk_timer"):
        tz = c.torso_z
        bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
        sw = math.sin(c.walk_timer * 7.5) * 0.035
        right = (bx + fx * 0.12 - px * 0.08 + fx * sw, by + fy * 0.12 - py * 0.08 + fy * sw, tz + 0.08)
        left = (bx + fx * 0.04 + px * 0.12 - fx * sw, by + fy * 0.04 + py * 0.12 - fy * sw, tz + 0.04)
        return left, right
    return idle_arms(c)


# ---------------------------------------------------------------------------------------------------------------------
# Leque Tessen 3D (Fechado e Aberto)
# ---------------------------------------------------------------------------------------------------------------------

def _draw_tessen_fan(c, hand, fwd_dir, side_dir, open_frac=0.0):
    """
    Renderiza o leque de guerra de ferro Tessen:
    - Fechado: bastão sólido de ferro laqueado com anel de seda e borla.
    - Aberto: semicírculo de varetas de aço e seda carmim com sol dourado pintado.
    """
    P = pal()
    u = mk.norm(fwd_dir)
    v = mk.norm(side_dir)

    if open_frac < 0.15:
        # Leque Fechado (bastão Tessen)
        p_base = mk.add(hand, u, -0.04)
        mk.obox(c, p_base, u, 0.26, 0.032, 0.026, P["fan_rib"])
        mk.obox(c, mk.add(p_base, u, 0.02), u, 0.022, 0.036, 0.030, P["fan_gold"], outline=False)
        mk.obox(c, mk.add(p_base, u, 0.22), u, 0.035, 0.030, 0.024, P["steel"], outline=False)
    else:
        # Leque Aberto em Semicírculo Radiante
        p_rivet = mk.add(hand, u, 0.01)
        mk.cbox(c, p_rivet[0], p_rivet[1], p_rivet[2], 0.022, 0.022, 0.022, P["fan_gold"], outline=False)

        # 5 varetas radiais de ferro e leque de seda em leque
        fan_radius = 0.26 * (0.85 + 0.15 * open_frac)
        spread_angle = math.pi * 0.55 * open_frac
        num_ribs = 5

        fan_pts = []
        for i in range(num_ribs):
            frac = (i / (num_ribs - 1) - 0.5) * 2.0  # -1.0 a +1.0
            ang = frac * (spread_angle * 0.5)
            # Direção radial da vareta
            cos_a = math.cos(ang)
            sin_a = math.sin(ang)
            rib_dir = (u[0] * cos_a + v[0] * sin_a,
                       u[1] * cos_a + v[1] * sin_a,
                       u[2] * cos_a + v[2] * sin_a)
            tip = mk.add(p_rivet, rib_dir, fan_radius)
            fan_pts.append(tip)
            # Vareta de ferro
            mk.obox(c, p_rivet, rib_dir, fan_radius, 0.016, 0.016, P["fan_rib"], outline=False)
            # Ponteira de aço afiado na extremidade
            mk.obox(c, mk.add(tip, rib_dir, -0.03), rib_dir, 0.03, 0.018, 0.018, P["steel"], outline=False)

        # Seda carmim estendida entre as varetas
        for i in range(len(fan_pts) - 1):
            p0 = mk.lerp(p_rivet, fan_pts[i], 0.35)
            p1 = fan_pts[i]
            p2 = fan_pts[i + 1]
            p3 = mk.lerp(p_rivet, fan_pts[i + 1], 0.35)
            mk.band(c, (p0, p1, p2, p3), P["fan_cloth"] + (235,))
            # Arco dourado de sol kabuki no centro da seda
            g0 = mk.lerp(p0, p1, 0.40)
            g1 = mk.lerp(p0, p1, 0.65)
            g2 = mk.lerp(p3, p2, 0.65)
            g3 = mk.lerp(p3, p2, 0.40)
            mk.band(c, (g0, g1, g2, g3), P["fan_gold"] + (245,))


def _render_fans_and_hands(c, arm_l, arm_r):
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)

    is_atk = c.is_melee and c.atk_progress is not None
    open_frac = math.sin(c.atk_progress * math.pi) if is_atk else 0.0

    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    dir_r_fwd = (fx * 0.8 + px * 0.3, fy * 0.8 + py * 0.3, 0.2 if is_atk else 0.4)
    dir_r_side = (-px * 0.7 + fx * 0.2, -py * 0.7 + fy * 0.2, 0.1)
    _draw_tessen_fan(c, hand_r, dir_r_fwd, dir_r_side, open_frac=open_frac)

    dir_l_fwd = (fx * 0.5 - px * 0.5, fy * 0.5 - py * 0.5, -0.2 if is_atk else 0.1)
    dir_l_side = (px * 0.7 + fx * 0.1, py * 0.7 + fy * 0.1, 0.0)
    _draw_tessen_fan(c, hand_l, dir_l_fwd, dir_l_side, open_frac=open_frac * 0.7)

    # Rastro mágico/venenoso em arco durante o ataque
    if is_atk and c.atk_progress >= 0.25:
        P = pal()
        tip_r = mk.add(hand_r, mk.norm(dir_r_fwd), 0.28)
        c_mid = mk.add(c.base_x + fx * 0.35, c.base_y + fy * 0.35, c.torso_z + 0.18)
        pts = [
            (tip_r[0] + px * 0.12, tip_r[1] + py * 0.12, tip_r[2] + 0.06),
            (tip_r[0] - px * 0.12, tip_r[1] - py * 0.12, tip_r[2] - 0.06),
            (hand_r[0] - px * 0.06, hand_r[1] - py * 0.06, hand_r[2]),
            (hand_r[0] + px * 0.06, hand_r[1] + py * 0.06, hand_r[2]),
        ]
        mk.band(c, pts, P["aura"] + (180,))


# ---------------------------------------------------------------------------------------------------------------------
# Penteado Shimada & Kanzashi
# ---------------------------------------------------------------------------------------------------------------------

def _shimada_bun_root(c):
    return (c.base_x - c.fx * 0.045, c.base_y - c.fy * 0.045, c.head_z + 0.170)


def _draw_shimada_hair(c):
    """Coque Shimada alto com laço de cabelo laqueado, pente dourado e Kanzashis."""
    P = pal()
    root = _shimada_bun_root(c)
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # Coque volumoso em forma de laço duplo (chignon Shimada)
    bun_top = (root[0] - fx * 0.02, root[1] - fy * 0.02, root[2] + 0.08)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        root, bun_top,
        w_start=0.075, h_start=0.075,
        w_end=0.060, h_end=0.060,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Pente dourado tradicional (kushi) na base do coque
    mk.obox(c, (root[0] + fx * 0.025, root[1] + fy * 0.025, root[2] + 0.02),
            (px, py, 0.0), 0.10, 0.016, 0.038, P["kanzashi"], up=(0.0, 0.0, 1.0), outline=False)

    # Grampos Kanzashi dourados radiais dos dois lados
    for s in (-1.0, 1.0):
        for j in range(3):
            k_dir = mk.norm((px * s * (0.60 + 0.20 * j) - fx * 0.10,
                             py * s * (0.60 + 0.20 * j) - fy * 0.10,
                             0.80 - 0.25 * j))
            k_origin = (root[0] + px * s * 0.035, root[1] + py * s * 0.035, root[2] + 0.03)
            mk.obox(c, k_origin, k_dir, 0.14, 0.010, 0.010, P["kanzashi"], outline=False)

        # Borla dourada pendurada que balança com o movimento
        trail, amp, freq = mk.motion(c, 0.05)
        offs = cloth.chain_offsets(2, c.walk_timer, 0.9 * s, trail, (px, py), amp=amp * 1.4, freq=freq)
        p_tassel = (root[0] + px * s * 0.08 + offs[1][0], root[1] + py * s * 0.08 + offs[1][1], root[2] - 0.04 + offs[1][2])
        mk.obox(c, p_tassel, (0.0, 0.0, -1.0), 0.050, 0.014, 0.014, P["tassel"], outline=False)


# ---------------------------------------------------------------------------------------------------------------------
# Ganchos de Renderização (Painter's Algorithm)
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Laço borboleta monumental do Obi dourado nas costas.
    - Coque Shimada traseiro se estiver do lado oposto à câmera.
    - Leques e mãos se estiverem atrás do tronco ao encarar de costas.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    # Laço borboleta monumental do Obi nas costas
    d_back = mk.depth(c, bx - fx * 0.11, by - fy * 0.11)
    if d_back >= d_torso - 0.03:
        b_root = (bx - fx * 0.11, by - fy * 0.11, c.pelvis_z + 0.08)
        # Nó central
        mk.cbox(c, b_root[0], b_root[1], b_root[2], 0.065, 0.045, 0.065, P["obi_knot"])
        # Asas borboleta douradas arqueadas
        for s in (-1.0, 1.0):
            wing_dir = mk.norm((px * s * 0.70 - fx * 0.15, py * s * 0.70 - fy * 0.15, 0.45))
            mk.obox(c, (b_root[0] + px * s * 0.02, b_root[1] + py * s * 0.02, b_root[2] + 0.01),
                    wing_dir, 0.11, 0.030, 0.065, P["obi"], up=(fx, fy, 0.0), outline=True)

        # Fitas longas do obi penduradas com movimento
        trail, amp, freq = mk.motion(c, 0.06)
        for k, s in enumerate((-1.0, 1.0)):
            offs = cloth.chain_offsets(3, c.walk_timer, 0.8 * k, trail, (px, py), amp=amp * 1.5, freq=freq)
            for i, o in enumerate(offs):
                mk.cbox(c, b_root[0] - fx * 0.02 + px * 0.03 * s + o[0],
                        b_root[1] - fy * 0.02 + py * 0.03 * s + o[1],
                        b_root[2] - 0.03 - 0.06 * (i + 1) + o[2],
                        0.035, 0.022, 0.065, P["obi"], outline=False)

    # Coque Shimada se atrás da cabeça
    b_root_pos = _shimada_bun_root(c)
    if mk.depth(c, b_root_pos[0], b_root_pos[1]) < d_torso:
        _draw_shimada_hair(c)

    # Mãos e leques ordenados por profundidade
    hand_l, hand_r = _current_hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_fans_and_hands(c, hand_l, hand_r)


def draw_legs(c):
    """Saia Furisode cerimonial contínua em fita 3D com barra dourada e sandálias Geta."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.06)
    flare = 0.08 * c.lunge_curve
    top = c.pelvis_z + 0.02
    bottom = c.base_z + 0.04

    offs = cloth.chain_offsets(3, c.walk_timer, 0.0, trail, (px, py), amp=amp * 1.2, freq=freq, wind=cloth.wind_at(bx, by))

    p0 = (bx, by, top)
    p1 = (bx + offs[0][0] * 0.5, by + offs[0][1] * 0.5, top - 0.14)
    p2 = (bx + offs[1][0] * 0.8, by + offs[1][1] * 0.8, bottom + 0.06)
    p3 = (bx + offs[2][0], by + offs[2][1], bottom)

    # Saia de seda carmim contínua em malha 3D
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1, p2, p3],
        widths=[c.pelvis_w + 0.04, c.pelvis_w + 0.08, c.pelvis_w + 0.12 + flare, c.pelvis_w + 0.14 + flare],
        depth_thick=0.130,
        colors=[P["kimono"], P["kimono_dark"], P["skirt"]],
        side_vec=(px, py, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Barra inferior dourada ricamente bordada
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p2, p3],
        widths=[c.pelvis_w + 0.125 + flare, c.pelvis_w + 0.145 + flare],
        depth_thick=0.134,
        colors=[P["collar_gold"], P["obi"]],
        side_vec=(px, py, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Sandálias de madeira Geta sob a barra
    for side in (-1.0, 1.0):
        gx = bx + px * (0.065 * side)
        gy = by + py * (0.065 * side)
        gz = bottom - 0.015
        mk.obox(c, (gx - fx * 0.035, gy - fy * 0.035, gz), (fx, fy, 0.0), 0.12, 0.065, 0.025, P["geta"])
        mk.obox(c, (gx - fx * 0.015, gy - fy * 0.015, gz + 0.025), (fx, fy, 0.0), 0.09, 0.055, 0.022, P["tabi"])
        mk.obox(c, (gx + fx * 0.015, gy + fy * 0.015, gz + 0.025), (fx, fy, 0.0), 0.015, 0.058, 0.024, P["tassel"], outline=False)


def draw_obi(c):
    """Obi dourado largo na cintura com nó frontal estilizado."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07
    d_torso = mk.depth(c, bx, by)

    # Faixa principal dourada do obi
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.005, c.pelvis_w * 0.76, 0.075, P["obi"])
    # Faixa superior de contraste
    mk.cbox(c, bx, by, z + 0.065, c.pelvis_w - 0.008, c.pelvis_w * 0.74, 0.012, P["obi_knot"], outline=False)


def draw_torso(c):
    """
    Tronco de Okuni:
    - Quimono Furisode cerimonial carmim com decote em V sutil.
    - Colarinho branco de seda pura (collar) com debrum dourado de contraste.
    - Pele Oshiroi branca pura de porcelana.
    """
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.105

    # Detalhes frontais (colarinho branco e debrum dourado)
    if mk.depth(c, fx, fy) > -0.05:
        apex = (bx + fx * front, by + fy * front, tz + 0.095)
        for s in (-1.0, 1.0):
            top = (bx + fx * (front - 0.003) + px * 0.052 * s, by + fy * (front - 0.003) + py * 0.052 * s, tz + 0.245)
            # Colarinho branco
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                top, apex,
                w_start=0.024, h_start=0.014,
                w_end=0.016, h_end=0.010,
                color=P["collar"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )
            # Debrum dourado de seda
            top_g = (top[0] - px * 0.006 * s, top[1] - py * 0.006 * s, top[2] - 0.004)
            apex_g = (apex[0] - px * 0.004 * s, apex[1] - py * 0.004 * s, apex[2] + 0.006)
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                top_g, apex_g,
                w_start=0.010, h_start=0.010,
                w_end=0.007, h_end=0.007,
                color=P["collar_gold"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )

        # Pele Oshiroi no centro do decote
        mk.obox(c, (bx + fx * (front - 0.005), by + fy * (front - 0.005), tz + 0.145),
                (0.0, 0.0, 1.0), 0.080, 0.040, 0.014, P["skin"], up=(fx, fy, 0.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço feminino esguio de pele Oshiroi branca pura."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.20)
    h = (hand[0], hand[1], hand[2] - 0.065)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.025), (0.0, 0.0, -0.025))

    # Braço e antebraço esguios de porcelana
    mk.limb(c, s, e, 0.048, P["skin"], w_end=0.042)
    mk.limb(c, e, h, 0.042, P["skin"], w_end=0.036)
    # Mão delicada
    mk.cbox(c, h[0], h[1], h[2] - 0.022, 0.042, 0.042, 0.042, P["skin"])
    return s, e


def draw_sleeves(c, arms):
    """Mangas Furisode amplas e ondulantes com caimento vertical natural e debrum dourado."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.07)
    for k, (s, e, side) in enumerate(arms):
        anchor = (s[0] + c.px * side * 0.015, s[1] + c.py * side * 0.015, s[2] + 0.010)
        mid = mk.add(mk.lerp(s, e, 0.45), (c.px * side * 0.025, c.py * side * 0.025, -0.040))
        hem = mk.add(mk.lerp(s, e, 0.85), (c.px * side * 0.040, c.py * side * 0.040, -0.120))

        # Manga de seda carmim
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[anchor, mid, hem],
            widths=[0.110, 0.145, 0.165],
            depth_thick=0.082,
            colors=[P["kimono"], P["kimono_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Debrum dourado na borda inferior da manga
        mk.obox(c, (hem[0], hem[1], hem[2] + 0.010), (0.0, 0.0, -1.0),
                0.016, 0.165, 0.084, P["collar_gold"], up=(c.fx, c.fy, 0.0), outline=False)


def draw_head(c):
    """
    Cabeça de Okuni:
    - Crânio esculpido em 3D com pele Oshiroi branca pura.
    - Olhos anime rubi expressivos, Kumadori alado carmim nas têmporas, nariz delicado e lábios cereja via draw_portrait_face_3d.
    - Cabelo laqueado Shimada com franja arqueada acima das sobrancelhas.
    - Coque Shimada alto com Kanzashi dourados (se visível).
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    d_torso = mk.depth(c, bx, by)

    # Franja repartida clássica acima das sobrancelhas (z >= hz + 0.108)
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.005
        for s in (-1.0, 1.0):
            p0 = (bx + fx * front_d + px * 0.012 * s, by + fy * front_d + py * 0.012 * s, hz + 0.140)
            p1 = (bx + fx * (front_d + 0.002) + px * 0.038 * s, by + fy * (front_d + 0.002) + py * 0.038 * s, hz + 0.118)
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                p0, p1,
                w_start=0.020, h_start=0.012,
                w_end=0.012, h_end=0.008,
                color=P["hair"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )

    # Coque Shimada se do lado visível da câmera
    b_root_pos = _shimada_bun_root(c)
    if mk.depth(c, b_root_pos[0], b_root_pos[1]) >= d_torso:
        _draw_shimada_hair(c)


def draw_front(c, arm_l, arm_r):
    """
    Camada frontal (Painter's Algorithm):
    - Leques Tessen são renderizados aqui APENAS se as mãos estiverem à frente do tronco.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)

    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_fans_and_hands(c, hand_l, hand_r)
