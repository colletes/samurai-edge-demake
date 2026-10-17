"""
Anne, a Capitã Pirata dos Sete Mares:
- Rosto anime expressivo com penetrantes olhos verde-esmeralda, brilho duplo e cílios alados; nariz feminino delicado e lábios rosa-coral.
- Cabelo ruivo-acobreado revolto com franja ondulada acima das sobrancelhas e mechas ao vento ordenadas por profundidade.
- Autêntico Tricórnio Pirata de veludo preto com abas triangulares dobradas para cima, debrum dourado e pluma escarlate arqueada.
- Camisa pirata branca com decote aberto e gola desdobrada expondo a clavícula delicada, sob colete de couro e cintos cruzados com fivelas de latão.
- Casaco longo de capitã em azul-marinho profundo com forro de seda, abas que esvoaçam e dragonas douradas nos ombros.
- Calça de montaria justa em malha 3D contínua entrando em botas altas de couro com cano dobrado (sem degraus de joelho).
- Faixa vermelha de seda na cintura com nó pendurado e chifre de pólvora entalhado.
- Alfanje (Cutlass) de lâmina curva com guarda em concha dourada na mão direita e bomba redonda com pavio aceso na esquerda.
- Ordenação dinâmica de profundidade 3D (Painter's Algorithm) garantindo oclusão perfeita de costas (180°).
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
from src.isometric.voxel_rig import calc_blade_slash_3d

PALETTE = {
    "coat": (36, 44, 62),
    "coat_dark": (22, 28, 40),
    "lining": (165, 36, 45),
    "vest": (34, 30, 36),
    "shirt": (248, 246, 242),
    "shirt_dark": (212, 210, 206),
    "skin": (248, 224, 206),
    "skin_shadow": (218, 186, 168),
    "hair": (195, 75, 36),
    "hair_light": (235, 115, 65),
    "hair_dark": (145, 48, 24),
    "pants": (44, 40, 48),
    "boot": (64, 42, 28),
    "boot_cuff": (108, 74, 48),
    "belt": (185, 34, 42),
    "leather": (88, 56, 36),
    "gold": (235, 195, 65),
    "hat": (26, 24, 28),
    "feather": (215, 38, 48),
    "feather_white": (245, 242, 238),
    "horn": (215, 185, 120),
    "bomb": (32, 32, 36),
    "fuse": (255, 175, 70),
    "steel": (215, 225, 238),
    "edge": (252, 254, 255),
    "guard": (235, 195, 65),
    "grip": (68, 45, 30),
    "aura": (255, 170, 90),
    "aura_core": (255, 236, 190),
}

MATERIALS = {
    "coat": "velvet", "coat_dark": "velvet", "vest": "leather",
    "leather": "leather", "boot": "leather", "boot_cuff": "leather",
    "pants": "canvas", "belt": "silk", "lining": "silk",
    "hat": "velvet", "steel": "steel", "gold": "gold"
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Armas Piratas
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """Postura confiante de capitã: alfanje erguido em guarda diagonal no ombro direito, bomba na mão esquerda."""
    tz = c.torso_z + math.sin(c.walk_timer * 2.8) * 0.010
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    right = (bx + fx * 0.12 - px * 0.14, by + fy * 0.12 - py * 0.14, tz + 0.12)
    left = (bx + fx * 0.10 + px * 0.15, by + fy * 0.10 + py * 0.15, tz - 0.02)
    return left, right


def attack_arms(c):
    """Golpe rodopiante com o alfanje e recuo da mão da bomba."""
    p = c.atk_progress if c.atk_progress is not None else 0.0
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    sw_a = -1.60 + p * 3.20
    right = (bx + fx * math.cos(sw_a) * 0.30 - px * math.sin(sw_a) * 0.30,
             by + fy * math.cos(sw_a) * 0.30 - py * math.sin(sw_a) * 0.30,
             tz + 0.16)
    left = (bx - fx * math.cos(sw_a) * 0.16 + px * math.sin(sw_a) * 0.16,
            by - fy * math.cos(sw_a) * 0.16 + py * math.sin(sw_a) * 0.16,
            tz + 0.08)
    return left, right


def _current_hands(c):
    if c.is_melee and c.atk_progress is not None:
        return attack_arms(c)
    if c.is_moving and hasattr(c, "walk_timer"):
        tz = c.torso_z
        bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
        sw = math.sin(c.walk_timer * 7.5) * 0.035
        right = (bx + fx * 0.08 - px * 0.12 - fx * sw, by + fy * 0.08 - py * 0.12 - fy * sw, tz + 0.02)
        left = (bx + fx * 0.06 + px * 0.14 + fx * sw, by + fy * 0.06 + py * 0.14 + fy * sw, tz - 0.04)
        return left, right
    return idle_arms(c)


# ---------------------------------------------------------------------------------------------------------------------
# Alfanje Curvo & Bomba Pirata 3D
# ---------------------------------------------------------------------------------------------------------------------

def _draw_cutlass(c, hand, d, up):
    """Alfanje de capitã pirata: empunhadura de couro, guarda em concha dourada e lâmina curva afiada."""
    P = pal()
    mk.obox(c, mk.add(hand, d, -0.09), d, 0.10, 0.036, 0.036, P["grip"])
    mk.obox(c, mk.add(hand, d, 0.0), d, 0.022, 0.085, 0.070, P["guard"])
    prev, dd = mk.add(hand, d, 0.02), d
    # Lâmina curva segmentada em arco com gume afiado
    for i, (length, bend) in enumerate(((0.22, 0.0), (0.20, 0.16), (0.16, 0.22))):
        dd = mk.norm(mk.add(dd, up, bend))
        mk.obox(c, prev, dd, length, 0.062 - 0.010 * i, 0.026, P["steel"])
        mk.obox(c, mk.add(prev, dd, 0.01), dd, length - 0.01, 0.016, 0.028, P["edge"], outline=False)
        prev = mk.add(prev, dd, length)
    return prev


def _draw_weapons(c, hand_l, hand_r):
    P = pal()
    if c.is_melee:
        info = calc_blade_slash_3d("pirate", "ATTACK", c.atk_progress, c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py)
        d = mk.norm(tuple(info["dir"]))
        up = (0.0, 0.0, -0.6)
    elif c.is_moving:
        d, up = mk.norm((c.fx * 0.4, c.fy * 0.4, -0.75)), (c.fx * 0.3, c.fy * 0.3, 0.2)
    else:
        d, up = mk.norm((-c.fx * 0.65 - c.px * 0.3, -c.fy * 0.65 - c.py * 0.3, 0.60)), (c.fx * 0.4, c.fy * 0.4, 0.2)

    _draw_cutlass(c, hand_r, d, up)

    # Rastro incandescente durante o ataque
    if c.is_melee and c.atk_progress >= 0.25:
        ghosts = []
        for j in range(5):
            pj = c.atk_progress - 0.07 * j
            if pj < 0.1:
                break
            ang = -1.60 + pj * 3.20
            h = (c.base_x + c.fx * math.cos(ang) * 0.30 - c.px * math.sin(ang) * 0.30,
                 c.base_y + c.fy * math.cos(ang) * 0.30 - c.py * math.sin(ang) * 0.30,
                 c.torso_z + 0.16)
            dj = mk.norm(tuple(calc_blade_slash_3d("pirate", "ATTACK", pj, c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py)["dir"]))
            ghosts.append((mk.add(h, dj, 0.42), mk.add(h, dj, 0.62)))
        for j in range(len(ghosts) - 1):
            fade = 1.0 - j / 5.0
            (a0, a1), (b0, b1) = ghosts[j], ghosts[j + 1]
            mk.band(c, (a0, a1, b1, b0), P["aura"] + (int(215 * fade),))
            mk.band(c, (mk.lerp(a0, a1, 0.5), a1, b1, mk.lerp(b0, b1, 0.5)), P["aura_core"] + (int(240 * fade),))

    # Bomba redonda na mão esquerda
    if not c.is_melee:
        bomb = (hand_l[0], hand_l[1], hand_l[2] - 0.03)
        mk.cbox(c, bomb[0], bomb[1], bomb[2], 0.075, 0.075, 0.075, P["bomb"])
        mk.cbox(c, bomb[0], bomb[1], bomb[2] + 0.045, 0.018, 0.018, 0.045, P["fuse"], outline=False)
        # Faísca incandescente no pavio
        mk.cbox(c, bomb[0] + 0.01, bomb[1], bomb[2] + 0.085, 0.026, 0.026, 0.026, (255, 220, 110), outline=False)


# ---------------------------------------------------------------------------------------------------------------------
# Cabelo Ruivo Ondulado, Mechas e Tricórnio Pirata
# ---------------------------------------------------------------------------------------------------------------------

def _lock_is_behind(c, side_sign):
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    lx = bx + fx * 0.02 + px * 0.065 * side_sign
    ly = by + fy * 0.02 + py * 0.065 * side_sign
    return mk.depth(c, lx, ly) < mk.depth(c, bx, by) - 0.008


def _side_lock(c, side_sign):
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.07)
    o = mk.cloth_offsets(c, 1, 0.8 * side_sign, trail, amp * 1.4, freq * 1.2, (bx, by))[0]

    p0 = (bx + fx * 0.040 + px * 0.048 * side_sign, by + fy * 0.040 + py * 0.048 * side_sign, hz + 0.135)
    p1 = (bx + fx * 0.044 + px * 0.054 * side_sign + o[0] * 0.5, by + fy * 0.044 + py * 0.054 * side_sign + o[1] * 0.5, hz + 0.065)
    p2 = (bx + fx * 0.046 + px * 0.048 * side_sign + o[0], by + fy * 0.046 + py * 0.048 * side_sign + o[1], hz - 0.005 + o[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1, p2],
        widths=[0.024, 0.020, 0.012],
        depth_thick=0.012,
        colors=[P["hair"], P["hair_light"]],
        side_vec=(px * side_sign, py * side_sign, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )


def _draw_flowing_hair(c):
    """Cabelo ruivo volumoso ondulando pelas costas e ombros."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.08)

    p0 = (bx - fx * 0.065, by - fy * 0.065, hz + 0.110)
    offs = cloth.chain_offsets(2, c.walk_timer, 0.0, trail, (px, py), amp=amp * 1.6, freq=freq * 1.2, wind=cloth.wind_at(bx, by))
    p1 = (bx - fx * 0.085 + offs[0][0], by - fy * 0.085 + offs[0][1], hz + 0.030 + offs[0][2])
    p2 = (bx - fx * 0.095 + offs[1][0], by - fy * 0.095 + offs[1][1], c.torso_z + 0.100 + offs[1][2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1, p2],
        widths=[0.115, 0.135, 0.100],
        depth_thick=0.040,
        colors=[P["hair"], P["hair_light"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )


def _draw_tricorne_hat(c):
    """
    Tricórnio Pirata 3D esculpido:
    - Copa cilíndrica de veludo preto assente acima da testa (hz + 0.145).
    - Três abas dobradas para cima (frente, lateral esquerda, lateral direita) com debrum dourado.
    - Majestosa pluma escarlate arqueada para trás.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    crown_z = hz + 0.145

    # 1. Copa do chapéu (crown)
    mk.cbox(c, bx - fx * 0.015, by - fy * 0.015, crown_z + 0.025, 0.135, 0.135, 0.050, P["hat"])
    # Faixa dourada na base da copa
    mk.cbox(c, bx - fx * 0.015, by - fy * 0.015, crown_z + 0.010, 0.142, 0.142, 0.018, P["gold"], outline=False)

    # 2. As três abas viradas para cima (Tricorne: frontal, lateral esquerda, lateral direita)
    # Aba Frontal virada para cima (up=(fx, fy, 0) para que a largura seja lateral)
    dir_f = mk.norm((fx * 0.18, fy * 0.18, 0.95))
    mk.obox(c, (bx + fx * 0.065, by + fy * 0.065, crown_z + 0.010), dir_f, 0.080, 0.135, 0.020, P["hat"], up=(fx, fy, 0.0))
    # Debrum dourado na aba frontal
    mk.obox(c, (bx + fx * 0.065, by + fy * 0.065, crown_z + 0.082), (px, py, 0.0), 0.135, 0.014, 0.014, P["gold"], outline=False)

    # Abas laterais viradas para cima
    for s in (-1.0, 1.0):
        dir_lat = mk.norm((px * s * 0.18 - fx * 0.05, py * s * 0.18 - fy * 0.05, 0.95))
        pos_lat = (bx + px * s * 0.065 - fx * 0.025, by + py * s * 0.065 - fy * 0.025, crown_z + 0.010)
        mk.obox(c, pos_lat, dir_lat, 0.085, 0.130, 0.020, P["hat"], up=(px * s, py * s, 0.0))
        # Debrum dourado
        mk.obox(c, (pos_lat[0], pos_lat[1], crown_z + 0.088), (fx, fy, 0.0), 0.130, 0.014, 0.014, P["gold"], outline=False)

    # 3. Pluma escarlate arqueada que se projeta do lado esquerdo do chapéu para trás
    trail, amp, freq = mk.motion(c, 0.07)
    plume_root = (bx + px * 0.060 - fx * 0.010, by + py * 0.060 - fy * 0.010, crown_z + 0.050)
    o1 = mk.cloth_offsets(c, 1, 0.5, trail, amp * 1.5, freq, plume_root)[0]
    p_mid = (plume_root[0] - fx * 0.060 + px * 0.020 + o1[0] * 0.5,
             plume_root[1] - fy * 0.060 + py * 0.020 + o1[1] * 0.5,
             crown_z + 0.110 + o1[2] * 0.5)
    p_tip = (plume_root[0] - fx * 0.130 + px * 0.030 + o1[0],
             plume_root[1] - fy * 0.130 + py * 0.030 + o1[1],
             crown_z + 0.080 + o1[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[plume_root, p_mid, p_tip],
        widths=[0.028, 0.034, 0.018],
        depth_thick=0.012,
        colors=[P["feather"], P["feather_white"]],
        side_vec=(px, py, 0.0),
        normal_vec=(0.0, 0.0, 1.0),
        outline=False,
        alpha=c.alpha,
    )


# ---------------------------------------------------------------------------------------------------------------------
# Casaco de Capitã (Costas)
# ---------------------------------------------------------------------------------------------------------------------

def _draw_coat_back(c):
    """Aba traseira do casaco de capitã em malha 3D contínua drapeada."""
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.06)

    anchor = (bx - fx * 0.115, by - fy * 0.115, tz + 0.22)
    offs = cloth.chain_offsets(2, c.walk_timer, 0.0, trail, (px, py), amp=amp * 1.5, freq=freq, wind=cloth.wind_at(bx, by))

    p1 = (anchor[0] + offs[0][0], anchor[1] + offs[0][1], tz + 0.06 + offs[0][2])
    p2 = (anchor[0] - fx * 0.02 + offs[1][0], anchor[1] - fy * 0.02 + offs[1][1], c.pelvis_z - 0.08 + offs[1][2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[anchor, p1, p2],
        widths=[0.24, 0.28, 0.32],
        depth_thick=0.035,
        colors=[P["coat"], P["coat_dark"], P["lining"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )


# ---------------------------------------------------------------------------------------------------------------------
# Ganchos de Renderização (Painter's Algorithm)
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Mechas distantes do cabelo ruivo.
    - Casaco de capitã nas costas.
    - Armas se as mãos estiverem atrás do tronco ao encarar de costas.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)

    for s in (-1.0, 1.0):
        if _lock_is_behind(c, s):
            _side_lock(c, s)

    # Cabelo traseiro e casaco nas costas
    d_back = mk.depth(c, c.base_x - c.fx * 0.08, c.base_y - c.fy * 0.08)
    if d_back <= d_torso + 0.02:
        _draw_flowing_hair(c)
        _draw_coat_back(c)

    # Armas se estiverem atrás do tronco
    hand_l, hand_r = _current_hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _draw_weapons(c, hand_l, hand_r)


def draw_legs(c):
    """Calça justa de montaria em malha 3D contínua e botas altas de couro com cano dobrado (sem degraus de joelho)."""
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

        # Calça de montaria justa em malha 3D contínua até o cano da bota
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos],
            widths=[0.110, 0.096, 0.086],
            depth_thick=0.084,
            colors=[P["pants"], P["pants"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Cano dobrado da bota de couro (cuff) ajustado à perna
        mk.obox(c, cuff_pos, (c.fx, c.fy, 0.0), 0.065, 0.105, 0.098, P["boot_cuff"], up=(0.0, 0.0, 1.0))

        # Bota de couro contínua até o tornozelo
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[cuff_pos, ankle],
            widths=[0.086, 0.076],
            depth_thick=0.078,
            colors=[P["boot"], P["boot"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Pé da bota de couro com sola
        flen, fwidth = 0.13, 0.066
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.016, flen, fwidth, 0.034, P["boot"], outline=True)
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.003, flen + 0.004, fwidth + 0.004, 0.010, (35, 25, 18), outline=False)


def draw_obi(c):
    """Faixa vermelha larga na cintura, fivela dourada, chifre de pólvora entalhado e bainha de couro."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    # Faixa escarlate na cintura
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.005, c.pelvis_w * 0.78, 0.075, P["belt"])
    # Fivela de latão dourado
    mk.cbox(c, bx + fx * 0.092, by + fy * 0.092, z + 0.010, 0.055, 0.024, 0.048, P["gold"], outline=False)

    # Pontas caídas da faixa escarlate
    trail, amp, freq = mk.motion(c, 0.05)
    offs = cloth.chain_offsets(2, c.walk_timer, 0.8, trail, (px, py), amp=amp * 1.3, freq=freq)
    for i, o in enumerate(offs):
        mk.cbox(c, bx + px * 0.10 + fx * 0.07 + o[0],
                by + py * 0.10 + fy * 0.07 + o[1],
                z - 0.050 * (i + 1) + o[2],
                0.035, 0.022, 0.055, P["belt"], outline=False)

    # Chifre de pólvora entalhado no quadril esquerdo
    horn_pos = (bx - px * 0.14, by - py * 0.14, z - 0.02)
    mk.obox(c, horn_pos, mk.norm((-px * 0.3 - fx * 0.1, -py * 0.3 - fy * 0.1, -0.90)), 0.12, 0.045, 0.045, P["horn"])

    # Bainha vazia do alfanje no quadril direito
    sheath_pos = (bx + px * 0.14, by + py * 0.14, z + 0.02)
    mk.obox(c, sheath_pos, mk.norm((-fx * 0.70 + px * 0.25, -fy * 0.70 + py * 0.25, -0.50)), 0.32, 0.038, 0.038, P["leather"])


def draw_torso(c):
    """
    Camisa pirata branca aberta orientada, colete escuro, cintos cruzados com fivelas douradas e dragonas.
    """
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.092

    # Decote frontal com camisa branca e clavícula exposta
    if mk.depth(c, fx, fy) > -0.05:
        # Camisa branca interna aberta e rente ao tronco (orientada em fx, fy)
        mk.obox(c, (bx + fx * (front - 0.008), by + fy * (front - 0.008), tz + 0.07), (0.0, 0.0, 1.0), 0.180, 0.085, 0.016, P["shirt"], up=(fx, fy, 0.0), outline=False)
        # Pele delicada da clavícula
        mk.obox(c, (bx + fx * (front - 0.006), by + fy * (front - 0.006), tz + 0.14), (0.0, 0.0, 1.0), 0.100, 0.050, 0.016, P["skin"], up=(fx, fy, 0.0), outline=False)

        # Lapelas abertas da camisa
        for s in (-1.0, 1.0):
            l_pos = (bx + fx * (front - 0.002) + px * 0.035 * s, by + fy * (front - 0.002) + py * 0.035 * s, tz + 0.170)
            l_dir = mk.norm((fx * 0.15 + px * 0.15 * s, fy * 0.15 + py * 0.15 * s, 0.90))
            mk.obox(c, l_pos, l_dir, 0.070, 0.026, 0.010, P["shirt"], up=(fx, fy, 0.0), outline=False)

        # Colete escuro aberto em ambos os lados
        for s in (-1.0, 1.0):
            top = (bx + fx * front + px * 0.065 * s, by + fy * front + py * 0.065 * s, tz + 0.245)
            apex = (bx + fx * front + px * 0.040 * s, by + fy * front + py * 0.040 * s, tz + 0.030)
            draw_tapered_frustum_3d(c.surface, c.camera, top, apex, w_start=0.030, h_start=0.018, w_end=0.034, h_end=0.018, color=P["vest"], up=(0.0, 0.0, 1.0), outline=False, alpha=c.alpha)

        # Cintos cruzados de couro (baldrics)
        a = (bx - px * 0.10 + fx * (front + 0.004), by - py * 0.10 + fy * (front + 0.004), tz + 0.25)
        b = (bx + px * 0.10 + fx * (front + 0.004), by + py * 0.10 + fy * (front + 0.004), tz + 0.01)
        mk.limb(c, a, b, 0.030, P["leather"], outline=False, height=0.016)
        mk.limb(c, (a[0] + px * 0.20, a[1] + py * 0.20, a[2]), (b[0] - px * 0.20, b[1] - py * 0.20, b[2]), 0.028, P["leather"], outline=False, height=0.016)
        # Fivela central dourada
        mk.cbox(c, bx + fx * (front + 0.006), by + fy * (front + 0.006), tz + 0.125, 0.038, 0.014, 0.038, P["gold"], outline=False)

        # Dragonas douradas nos ombros
        for s in (-1.0, 1.0):
            mk.obox(c, (bx + px * 0.135 * s, by + py * 0.135 * s, tz + 0.270), (fx, fy, 0.0), 0.075, 0.065, 0.024, P["gold"], up=(0.0, 0.0, 1.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço feminino esguio com manga do casaco e braçadeira de couro."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.20)
    h = (hand[0], hand[1], hand[2] - 0.060)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.025), (0.0, 0.0, -0.025))

    # Manga do casaco até o antebraço
    mk.limb(c, s, e, 0.052, P["coat"], w_end=0.046)
    # Braçadeira de couro no punho
    mk.limb(c, e, h, 0.044, P["leather"], w_end=0.038)
    # Mão delicada
    mk.cbox(c, h[0], h[1], h[2] - 0.020, 0.040, 0.040, 0.040, P["skin"])
    return s, e


def draw_sleeves(c, arms):
    """Abas frontais do casaco de capitã com forro vermelho aparente."""
    P = pal()
    for s, e, side in arms:
        anchor = (c.base_x + c.fx * 0.08 + c.px * 0.120 * side, c.base_y + c.fy * 0.08 + c.py * 0.120 * side, c.torso_z + 0.20)
        mid = (anchor[0] + c.px * side * 0.015, anchor[1] + c.py * side * 0.015, c.torso_z + 0.08)
        hem = (anchor[0] + c.px * side * 0.030, anchor[1] + c.py * side * 0.030, c.torso_z - 0.04)

        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[anchor, mid, hem],
            widths=[0.080, 0.095, 0.110],
            depth_thick=0.030,
            colors=[P["coat"], P["lining"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )


def draw_head(c):
    """
    Cabeça de Anne:
    - Crânio esculpido 3D com olhos verde-esmeralda expressivos, nariz delicado e lábios rosa-coral via draw_portrait_face_3d.
    - Franja ondulada ruiva acima das sobrancelhas (z >= hz + 0.108).
    - Mechas laterais onduladas emoldurando a face se visíveis da câmera.
    - Autêntico Tricórnio Pirata 3D com abas dobradas e pluma escarlate.
    - Cabelo ruivo longo traseiro se visível.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    d_torso = mk.depth(c, bx, by)

    # Franja ondulada ruiva acima das sobrancelhas (z >= hz + 0.108)
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.005
        p0 = (bx + fx * front_d, by + fy * front_d, hz + 0.138)
        p1 = (bx + fx * (front_d + 0.002), by + fy * (front_d + 0.002), hz + 0.116)
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            p0, p1,
            w_start=0.084, h_start=0.014,
            w_end=0.078, h_end=0.010,
            color=P["hair"],
            up=(0.0, 0.0, 1.0),
            outline=False,
            alpha=c.alpha,
        )

    # Mechas laterais do lado visível da câmera
    for s in (-1.0, 1.0):
        if not _lock_is_behind(c, s):
            _side_lock(c, s)

    # Cabelo traseiro se visível
    d_back = mk.depth(c, bx - fx * 0.08, by - fy * 0.08)
    if d_back > d_torso + 0.02:
        _draw_flowing_hair(c)
        _draw_coat_back(c)

    # Tricórnio Pirata 3D
    _draw_tricorne_hat(c)


def draw_front(c, arm_l, arm_r):
    """
    Camada frontal (Painter's Algorithm):
    - Alfanje e bomba são renderizados aqui APENAS se estiverem à frente do tronco.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.060)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.060)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)

    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _draw_weapons(c, hand_l, hand_r)
