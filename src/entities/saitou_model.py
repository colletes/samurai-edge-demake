"""
Saitou Hajime, Capitão da 3ª Divisão do Shinsengumi:
- Rosto severo e impassível com olhar marcial focado, sobrancelhas cerradas, ponte nasal forte e lábios firmes.
- Cabelo negro com topete samurai, costeletas marcadas e rabo-de-cavalo (chonmage) amarrado com laço branco.
- Haori azul-piscina/turquesa clássico com barra em zigue-zague branco (Dandara) sobre quimono azul-marinho com colarinho branco.
- Hakama escura ampla com pregas em malha 3D contínua entrando em caneleiras pretas (kyahan), meias tabi brancas e sandálias waraji.
- Mangas amplas de haori em fita 3D fluida drapeando para baixo com padrão Dandara.
- Katana longa em guarda mortal de Gatotsu (estocada horizontal na altura dos olhos) e bainha laqueada preta no quadril.
- Ordenação dinâmica de profundidade 3D (Painter's Algorithm) com oclusão limpa de costas (180°).
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

PALETTE = {
    "haori": (134, 202, 226),
    "haori_dark": (92, 154, 186),
    "torso": (134, 202, 226),
    "zig": (244, 248, 252),
    "navy": (30, 38, 66),
    "navy_dark": (20, 26, 48),
    "pants": (36, 42, 74),
    "hakama_dark": (24, 28, 52),
    "belt": (238, 238, 244),
    "kyahan": (26, 26, 32),
    "tabi": (238, 238, 242),
    "sandal": (46, 40, 36),
    "strap": (210, 210, 220),
    "skin": (238, 204, 176),
    "skin_shadow": (206, 168, 140),
    "hair": (24, 24, 30),
    "hair_light": (44, 46, 56),
    "saya": (28, 30, 40),
    "gold": (214, 184, 96),
    "steel": (224, 234, 246),
    "edge": (252, 254, 255),
    "ito": (24, 26, 36),
    "aura": (150, 214, 255),
    "aura_core": (236, 250, 255),
}

MATERIALS = {
    "haori": "silk", "haori_dark": "silk", "navy": "silk",
    "belt": "silk", "kyahan": "leather", "saya": "lacquer",
    "strap": "canvas", "steel": "steel", "gold": "gold"
}


def pal() -> dict:
    return PALETTE


def _sheath(c):
    k = (c.base_x + c.px * 0.14 + c.fx * 0.03, c.base_y + c.py * 0.14 + c.fy * 0.03, c.pelvis_z + 0.07)
    b = mk.norm((-c.fx * 0.82 + c.px * 0.30, -c.fy * 0.82 + c.py * 0.30, -0.30))
    return k, b


def _draw_sheath(c):
    P = pal()
    k, b = _sheath(c)
    # Bainha laqueada escura (Saya)
    mk.obox(c, k, b, 0.50, 0.044, 0.044, P["saya"])
    # Boca da bainha (Koiguchi) dourada
    mk.obox(c, k, b, 0.030, 0.052, 0.052, P["gold"], outline=False)
    # Ponteira dourada (Kojiri)
    mk.obox(c, mk.add(k, b, 0.47), b, 0.030, 0.050, 0.050, P["gold"], outline=False)
    # Se estiver caminhando e sem golpear, a katana está embainhada
    if c.is_moving and not c.is_melee:
        h = (-b[0], -b[1], -b[2])
        mk.obox(c, k, h, 0.17, 0.040, 0.040, P["ito"])
        mk.obox(c, mk.add(k, b, -0.008), b, 0.016, 0.075, 0.075, P["gold"])


def _gatotsu_blade_dir(c):
    return mk.norm((c.fx * 0.95, c.fy * 0.95, -0.14 if not c.is_melee else -0.08))



def _draw_gatotsu_blade(c, hand):
    P = pal()
    d = _gatotsu_blade_dir(c)
    length = 0.76 if c.is_melee else 0.70
    mk.sword(c, mk.add(hand, d, -0.02), d, length, P["steel"], P["edge"], P["ito"], P["gold"], P["gold"], guard_w=0.070)
    if c.is_melee and c.atk_progress is not None and c.atk_progress >= 0.28:
        for j in range(1, 5):
            p = c.atk_progress - 0.06 * j
            if p < 0.15:
                break
            ghost = mk.add(hand, d, -0.06 * j)
            fade = 1.0 - j / 5.0
            tip, mid = mk.add(ghost, d, length), mk.add(ghost, d, length * 0.45)
            side = (c.px * 0.030, c.py * 0.030, 0.0)
            mk.band(c, (mid, tip, mk.add(tip, side, 1.0), mk.add(mid, side, 1.0)), P["aura"] + (int(200 * fade),))


def _back_panel(c, P):
    anchor = (c.base_x - c.fx * 0.12, c.base_y - c.fy * 0.12, c.torso_z + 0.22)
    trail, amp, freq = mk.motion(c, 0.06)
    offs = mk.cloth_offsets(c, 3, 0.6, trail, amp * 1.5, freq, anchor)
    p1 = (anchor[0] + offs[0][0], anchor[1] + offs[0][1], anchor[2] - 0.12 + offs[0][2])
    p2 = (anchor[0] + offs[1][0], anchor[1] + offs[1][1], anchor[2] - 0.24 + offs[1][2])
    p3 = (anchor[0] + offs[2][0], anchor[1] + offs[2][1], anchor[2] - 0.36 + offs[2][2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[anchor, p1, p2, p3],
        widths=(0.26, 0.28, 0.30, 0.32),
        depth_thick=0.032,
        colors=(P["haori"], P["haori"], P["haori_dark"]),
        side_vec=(c.px, c.py, 0.0),
        normal_vec=(-c.fx, -c.fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )
    # Zigue-zague branco tradicional do Shinsengumi (Dandara) na barra inferior
    for i in range(5):
        lat = (i - 2) * 0.055
        mk.cbox(c, p3[0] + c.px * lat, p3[1] + c.py * lat, p3[2] - 0.015, 0.034, 0.028, 0.040, P["zig"], outline=False)


def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Bainha se estiver atrás do corpo.
    - Aba traseira do haori se de costas.
    - Katana Gatotsu e braços se estiver de costas (180°), garantindo oclusão perfeita.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    k, b = _sheath(c)
    if mk.depth(c, k[0] + b[0] * 0.25, k[1] + b[1] * 0.25) < d_torso:
        _draw_sheath(c)

    d_back = mk.depth(c, c.base_x - c.fx * 0.10, c.base_y - c.fy * 0.10)
    if d_back <= d_torso + 0.02:
        _back_panel(c, pal())

    # Se estiver de costas, desenhar a katana Gatotsu em draw_behind para que o torso a oclua
    if not (c.is_moving and not c.is_melee):
        if c.is_melee:
            reach = math.sin(c.atk_progress * math.pi) * 0.35 if c.state == "ZEROSHIKI" else 0.24
            hand_l_x = c.base_x + c.fx * (0.34 + reach)
            hand_l_y = c.base_y + c.fy * (0.34 + reach)
            hand_l_z = c.torso_z + 0.18
        else:
            hand_l_x = c.base_x + c.fx * 0.28 + c.px * 0.12
            hand_l_y = c.base_y + c.fy * 0.28 + c.py * 0.12
            hand_l_z = c.torso_z + 0.15
        hand_l = (hand_l_x, hand_l_y, hand_l_z - 0.05)
        if mk.depth(c, hand_l[0], hand_l[1]) < d_torso:
            _draw_gatotsu_blade(c, hand_l)


def draw_legs(c):
    """Hakama larga e escura em malha 3D contínua, caneleira preta, tabi branco e sandália waraji."""
    P = pal()
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

        # Hakama azul-escura com pregas volumosas em malha contínua 3D
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos],
            widths=[0.130, 0.118, 0.095],
            depth_thick=0.092,
            colors=[P["pants"], P["hakama_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Caneleira preta protetora (Kyahan)
        mk.obox(c, cuff_pos, (c.fx, c.fy, 0.0), 0.065, 0.102, 0.095, P["kyahan"], up=(0.0, 0.0, 1.0))

        # Meias Tabi brancas até o tornozelo
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[cuff_pos, ankle],
            widths=[0.085, 0.075],
            depth_thick=0.078,
            colors=[P["tabi"], P["tabi"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Pé com sandália Waraji e sola
        flen, fwidth = 0.13, 0.066
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.016, flen, fwidth, 0.034, P["tabi"], outline=True)
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.003, flen + 0.004, fwidth + 0.004, 0.010, P["sandal"], outline=False)
        mk.cbox(c, foot[0] + c.fx * (flen * 0.35), foot[1] + c.fy * (flen * 0.35), foot[2] + 0.018, 0.024, 0.024, 0.012, P["strap"], outline=False)


def draw_obi(c):
    """Faixa branca de seda com nó lateral esvoaçante."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.008, c.pelvis_w * 0.74, 0.080, P["belt"])
    kx, ky = bx + fx * 0.10 - px * 0.04, by + fy * 0.10 - py * 0.04
    mk.cbox(c, kx, ky, z + 0.010, 0.070, 0.040, 0.060, P["belt"])
    trail, amp, freq = mk.motion(c, 0.05)
    offs = mk.cloth_offsets(c, 2, 0.9, trail, amp * 1.4, freq, (kx, ky))
    for i, o in enumerate(offs):
        mk.cbox(c, kx + o[0], ky + o[1], z - 0.060 * (i + 1) + o[2], 0.034, 0.024, 0.066, P["belt"], outline=False)


def draw_torso(c):
    """Quimono azul-marinho com colarinho branco aparecendo entre as abas do haori com padrão Dandara."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.110

    if mk.depth(c, fx, fy) > -0.05:
        # Quimono azul-marinho interno
        mk.obox(c, (bx + fx * (front - 0.008), by + fy * (front - 0.008), tz + 0.02), (0.0, 0.0, 1.0), 0.240, 0.110, 0.020, P["navy"], up=(fx, fy, 0.0), outline=False)
        # Colarinho branco (Juban)
        apex = (bx + fx * (front + 0.004), by + fy * (front + 0.004), tz + 0.10)
        for s in (-1.0, 1.0):
            top = (bx + fx * front + px * 0.065 * s, by + fy * front + py * 0.065 * s, tz + 0.265)
            mk.limb(c, top, apex, 0.034, P["strap"], outline=False, height=0.018)
        mk.cbox(c, bx + fx * front, by + fy * front, tz + 0.20, 0.040, 0.018, 0.060, P["skin"], outline=False)

        # Abas frontais do haori azul-turquesa
        for s in (-1.0, 1.0):
            anchor = (bx + fx * 0.120 + px * 0.130 * s, by + fy * 0.120 + py * 0.130 * s, tz + 0.20)
            last = mk.panels(c, anchor, 3, 0.10, 0.075, 0.022, (P["haori"], P["haori"], P["haori_dark"]), phase=0.9 * s, up=(fx, fy, 0.0), flare=0.006)
            for i in range(2):
                lat = (i - 0.5) * 0.040
                mk.cbox(c, last[0] + px * lat, last[1] + py * lat, last[2] - 0.015, 0.030, 0.026, 0.035, P["zig"], outline=False)

    if mk.depth(c, -fx, -fy) > -0.05:
        _back_panel(c, P)


def draw_arm(c, shoulder, hand, side):
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], bracer=P["kyahan"], bracer_span=(0.35, 0.95), w=0.058)


def draw_sleeves(c, arms):
    """Mangas amplas do haori em fita contínua 3D drapeando para baixo com padrão Dandara."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.07)
    atk = math.sin(c.atk_progress * math.pi) if c.is_melee and c.atk_progress is not None else 0.0
    for k, (s, e, side) in enumerate(arms):
        anchor = (s[0] + c.px * side * 0.040, s[1] + c.py * side * 0.040, s[2] - 0.010)
        drag = (-c.fx * 0.10 * atk, -c.fy * 0.10 * atk)
        offs = cloth.chain_offsets(2, c.walk_timer, 1.7 * k, drag, (c.px, c.py), amp=amp * 1.5, freq=freq, wind=cloth.wind_at(anchor[0], anchor[1]))

        mid = (anchor[0] + offs[0][0] + c.px * side * 0.015, anchor[1] + offs[0][1] + c.py * side * 0.015, anchor[2] - 0.100 + offs[0][2])
        hem = (anchor[0] + offs[1][0] + c.px * side * 0.025, anchor[1] + offs[1][1] + c.py * side * 0.025, anchor[2] - 0.200 + offs[1][2])

        spine_pts = [anchor, mid, hem]
        widths = (0.10, 0.13, 0.16)
        colors = (P["haori"], P["haori_dark"])
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=spine_pts,
            widths=widths,
            depth_thick=0.046,
            colors=colors,
            side_vec=(c.fx, c.fy, 0.0),
            normal_vec=(c.px * side, c.py * side, 0.0),
            outline=True,
            alpha=c.alpha,
        )
        # Pontas brancas em zigue-zague na barra da manga (Dandara)
        for i in range(3):
            lat = (i - 1) * 0.045
            mk.obox(c, (hem[0] + c.fx * lat, hem[1] + c.fy * lat, hem[2] - 0.005), (0.0, 0.0, -1.0), 0.025, 0.030, 0.035, P["zig"], up=(c.fx, c.fy, 0.0), outline=False)


def draw_head(c):
    """
    Cabeça de Saitou:
    - O crânio esculpido 3D e feições marciais resolutas são projetados pelo pipeline.
    - Topete samurai clássico esculpido ajustado ao crânio.
    - Costeletas marcadas descendo pelas têmporas.
    - Rabo de cavalo samurai (Chonmage) com laço branco.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    hw = c.head_w
    d_torso = mk.depth(c, bx, by)

    # Costeletas e mechas laterais rente às têmporas
    for s in (-1.0, 1.0):
        lx = bx + fx * 0.015 + px * 0.065 * s
        ly = by + fy * 0.015 + py * 0.065 * s
        if mk.depth(c, lx, ly) >= d_torso - 0.01:
            p0 = (lx, ly, hz + 0.125)
            p1 = (lx + fx * 0.010, ly + fy * 0.010, hz + 0.065)
            p2 = (lx + fx * 0.012, ly + fy * 0.012, hz + 0.020)
            draw_ribbon_mesh_3d(
                c.surface, c.camera,
                spine_points=[p0, p1, p2],
                widths=[0.024, 0.020, 0.012],
                depth_thick=0.012,
                colors=[P["hair"], P["hair"]],
                side_vec=(px * s, py * s, 0.0),
                normal_vec=(fx, fy, 0.0),
                outline=False,
                alpha=c.alpha,
            )

    # Topete samurai clássico no topo da cabeça (ajustado e cônico)
    cran_top = (bx - fx * 0.005, by - fy * 0.005, hz + 0.165)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, hz + 0.140), cran_top,
        w_start=hw * 0.95, h_start=hw * 0.95,
        w_end=hw * 0.72, h_end=hw * 0.72,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Rabo de cavalo samurai (Chonmage) amarrado com laço branco atrás
    knot_pos = (bx - fx * 0.040, by - fy * 0.040, hz + 0.165)
    mk.obox(c, knot_pos, (0.0, 0.0, 1.0), 0.015, 0.024, 0.024, P["belt"], up=(fx, fy, 0.0), outline=False)



    trail, amp, freq = mk.motion(c, 0.06)
    o = mk.cloth_offsets(c, 1, 0.8, trail, amp * 1.5, freq, knot_pos)[0]
    p_tail1 = (knot_pos[0] - fx * 0.040 + o[0] * 0.5, knot_pos[1] - fy * 0.040 + o[1] * 0.5, hz + 0.170 + o[2] * 0.5)
    p_tail2 = (knot_pos[0] - fx * 0.090 + o[0], knot_pos[1] - fy * 0.090 + o[1], hz + 0.120 + o[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[knot_pos, p_tail1, p_tail2],
        widths=[0.026, 0.028, 0.018],
        depth_thick=0.018,
        colors=[P["hair"], P["hair"]],
        side_vec=(px, py, 0.0),
        normal_vec=(0.0, 0.0, 1.0),
        outline=False,
        alpha=c.alpha,
    )


def draw_front(c, arm_l, arm_r):
    """
    Camada frontal:
    - Bainha se estiver voltada para a câmera.
    - Katana longa em guarda Gatotsu se estiver à frente do tronco.
    """
    P = pal()
    d_torso = mk.depth(c, c.base_x, c.base_y)
    k, b = _sheath(c)
    if mk.depth(c, k[0] + b[0] * 0.25, k[1] + b[1] * 0.25) >= d_torso:
        _draw_sheath(c)

    if c.is_moving and not c.is_melee:
        return

    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.05)
    if mk.depth(c, hand_l[0], hand_l[1]) >= d_torso:
        _draw_gatotsu_blade(c, hand_l)

