"""
Joe, o ninja americano (6.5.5): balaclava preta com faixa de pano e sol vermelho, óculos de visão noturna erguidos, colete
tático coiote com carregadores, granada e almofada de shuriken, remendo da bandeira na manga, luvas pretas, farda oliva com
joelheiras e botas, coldre na coxa, mochila e katana nas costas, kunai na direita e shuriken na esquerda.
Só o visual muda: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk

PALETTE = {
    "torso": (84, 90, 62), "pants": (84, 90, 62), "hair": (26, 27, 31), "belt": (112, 98, 64),
    "skin": (228, 186, 150), "skin_shadow": (196, 152, 120),
    "balaclava": (26, 27, 31), "glove": (28, 28, 30), "boot": (66, 58, 40), "knee": (54, 58, 50),
    "vest": (136, 120, 78), "pouch": (108, 96, 62), "pack": (60, 66, 44), "headband": (222, 206, 150), "sun": (200, 36, 40),
    "nvg": (38, 42, 46), "lens": (96, 214, 196), "grenade": (62, 92, 52), "flag_blue": (36, 62, 150), "holster": (30, 30, 34),
    "steel": (216, 226, 240), "steel_dark": (112, 116, 124), "wood": (92, 66, 40), "eye": (30, 30, 34),
}


MATERIALS = {"torso": "canvas", "vest": "canvas", "pouch": "canvas", "pack": "canvas", "boot": "leather", "glove": "leather", "knee": "leather", "holster": "leather", "belt": "canvas", "balaclava": "knit", "headband": "canvas"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def attack_arms(c):
    """Estocada de kunai: a direita recolhe no quadril, avança em linha reta e volta; a esquerda guarda o queixo."""
    bx, by, tz, fx, fy, px, py, p = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py, c.atk_progress
    t = _smooth((p - 0.2) / 0.45)
    back = 1.0 - _smooth(p / 0.2)
    reach = 0.02 + 0.40 * t - 0.12 * back
    right = (bx + fx * reach - px * 0.12, by + fy * reach - py * 0.12, tz + 0.10 + 0.08 * t)
    left = (bx + fx * (0.14 + 0.06 * t) + px * 0.10, by + fy * (0.14 + 0.06 * t) + py * 0.10, tz + 0.18)
    return left, right


def _back_point(c):
    return (c.base_x - c.fx * 0.15, c.base_y - c.fy * 0.15, 0.0)


def _back_gear(c):
    """Mochila tática e katana em diagonal nas costas."""
    P = pal()
    mk.cbox(c, c.base_x - c.fx * 0.15, c.base_y - c.fy * 0.15, c.torso_z + 0.02, 0.15, 0.15, 0.23, P["pack"])
    mk.cbox(c, c.base_x - c.fx * 0.15, c.base_y - c.fy * 0.15, c.torso_z + 0.215, 0.12, 0.12, 0.03, P["pouch"], outline=False)
    d = mk.norm((c.px * 0.35 - c.fx * 0.05, c.py * 0.35 - c.fy * 0.05, 0.9))
    origin = (c.base_x - c.fx * 0.23 - c.px * 0.07, c.base_y - c.fy * 0.23 - c.py * 0.07, c.torso_z - 0.06)
    mk.obox(c, origin, d, 0.36, 0.042, 0.042, P["balaclava"])
    mk.obox(c, mk.add(origin, d, 0.34), d, 0.12, 0.046, 0.046, P["wood"])


def draw_behind(c):
    if mk.behind(c, _back_point(c)):
        _back_gear(c)
    if mk.facing_camera(c):
        mk.hair_volume(c, pal()["balaclava"], size=0.166, height=0.15)


def draw_legs(c):
    """Calça oliva com joelheiras e botas de combate de cano alto."""
    P = pal()
    mk.legs(c, P["pants"], boot=P["boot"], boot_h=0.12, tight_w=(0.125, 0.115), foot_color=P["boot"], foot_len=0.15, foot_w=0.085, sole=(30, 26, 22), cuff=(54, 48, 34))
    for side in mk.sorted_sides(c):
        sh = c.legs_data[side]["shin"]
        mk.cbox(c, sh[0] + c.fx * 0.035, sh[1] + c.fy * 0.035, sh[2] + 0.13, 0.115, 0.115, 0.075, P["knee"])


def draw_obi(c):
    """Cinto de nylon com fivela, granada à esquerda e coldre preto na coxa direita."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z
    mk.cbox(c, bx, by, z + 0.065, c.pelvis_w, c.pelvis_w * 0.78, 0.07, P["belt"])
    mk.cbox(c, bx + fx * 0.098, by + fy * 0.098, z + 0.07, 0.05, 0.03, 0.05, P["steel_dark"], outline=False)
    mk.cbox(c, bx - px * 0.12 + fx * 0.10, by - py * 0.12 + fy * 0.10, z + 0.02, 0.045, 0.045, 0.07, P["grenade"])
    mk.cbox(c, bx + px * 0.16, by + py * 0.16, z - 0.12, 0.06, 0.07, 0.15, P["holster"])
    mk.cbox(c, bx + px * 0.16, by + py * 0.16, z - 0.115, 0.065, 0.075, 0.03, P["pouch"], outline=False)


def draw_torso(c):
    """Colete coiote com três carregadores, granada, almofada de shuriken e alças."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    mk.cbox(c, bx, by, tz + 0.08, 0.31, 0.25, 0.185, P["vest"])
    front = 0.125 + 0.02
    for side in (-0.085, 0.0, 0.085):
        mk.cbox(c, bx + fx * front + px * side, by + fy * front + py * side, tz + 0.02, 0.07, 0.05, 0.095, P["pouch"])
    mk.cbox(c, bx + fx * front + px * 0.11, by + fy * front + py * 0.11, tz + 0.15, 0.045, 0.04, 0.06, P["grenade"])
    mk.cbox(c, bx + fx * front - px * 0.09, by + fy * front - py * 0.09, tz + 0.16, 0.07, 0.03, 0.02, P["steel_dark"], outline=False)
    for s in (-1.0, 1.0):
        mk.limb(c, (bx + px * 0.09 * s, by + py * 0.09 * s, tz + 0.27), (bx + fx * front * 0.9 + px * 0.07 * s, by + fy * front * 0.9 + py * 0.07 * s, tz + 0.14), 0.035, P["pouch"], outline=False)
    mk.cbox(c, bx + fx * (front - 0.02), by + fy * (front - 0.02), tz + 0.205, 0.05, 0.02, 0.05, P["skin"], outline=False)
    if not mk.behind(c, _back_point(c)):
        _back_gear(c)


def draw_arm(c, shoulder, hand, side):
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], sleeve=P["torso"], sleeve_to=1.1, glove=P["glove"], w=0.064)


def draw_sleeves(c, arms):
    """Remendo da bandeira no lado de fora de cada ombro e almofada de cotovelo."""
    P = pal()
    for s, e, side in arms:
        px_, py_ = s[0] + c.px * side * 0.065, s[1] + c.py * side * 0.065
        mk.cbox(c, px_, py_, s[2] - 0.055, 0.044, 0.044, 0.04, P["sun"], outline=False)
        mk.cbox(c, px_ + c.px * side * 0.004, py_ + c.py * side * 0.004, s[2] - 0.03, 0.026, 0.026, 0.026, P["flag_blue"], outline=False)
        mk.cbox(c, e[0], e[1], e[2] - 0.03, 0.07, 0.07, 0.05, P["knee"], outline=False)


def draw_head(c):
    """Balaclava, faixa de pano com sol vermelho e pontas do nó balançando, visão noturna erguida."""
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    mk.cbox(c, bx, by, hz + 0.02, hw + 0.016, hw + 0.016, 0.16, P["balaclava"])
    if not mk.facing_camera(c):
        mk.hair_volume(c, P["balaclava"], size=0.166, height=0.15)
    mk.cbox(c, bx, by, hz + 0.095, hw + 0.026, hw + 0.026, 0.04, P["headband"])
    if mk.facing_camera(c):
        mk.plate(c, hz + 0.06, 0.036, P["skin"], outline=False)
        front = hw / 2 + 0.012
        for s in (-1.0, 1.0):
            mk.cbox(c, bx + fx * front + px * 0.026 * s, by + fy * front + py * 0.026 * s, hz + 0.066, 0.02, 0.016, 0.016, P["eye"], outline=False)
        mk.cbox(c, bx + fx * (hw / 2 + 0.02), by + fy * (hw / 2 + 0.02), hz + 0.1, 0.044, 0.02, 0.03, P["sun"], outline=False)
    trail, amp, freq = mk.motion(c, 0.08)
    offs = mk.cloth_offsets(c, 2, 0.6, trail, amp * 1.6, freq, (bx, by))
    for k, s in enumerate((-1.0, 1.0)):
        for i, o in enumerate(offs):
            mk.cbox(c, bx - fx * (hw / 2 + 0.03) + px * 0.03 * s + o[0] * (1 + 0.3 * k), by - fy * (hw / 2 + 0.03) + py * 0.03 * s + o[1], hz + 0.08 - 0.05 * i + o[2], 0.03, 0.02, 0.06, P["headband"], outline=False)
    mk.cbox(c, bx + fx * 0.02, by + fy * 0.02, hz + 0.175, 0.095, 0.09, 0.03, P["nvg"])
    for s in (-1.0, 1.0):
        tx, ty = bx + fx * 0.04 + px * 0.04 * s, by + fy * 0.04 + py * 0.04 * s
        mk.cbox(c, tx, ty, hz + 0.205, 0.05, 0.05, 0.07, P["nvg"])
        mk.cbox(c, tx + fx * 0.03, ty + fy * 0.03, hz + 0.23, 0.026, 0.026, 0.024, P["lens"], outline=False)


def _shuriken(c, hand):
    P = pal()
    for ang in (0.0, math.pi / 4):
        d = (math.cos(ang) * c.fx + math.sin(ang) * c.px, math.cos(ang) * c.fy + math.sin(ang) * c.py, 0.0)
        mk.obox(c, (hand[0] - d[0] * 0.07, hand[1] - d[1] * 0.07, hand[2] - 0.01), d, 0.14, 0.03, 0.014, P["steel_dark"])
    mk.cbox(c, hand[0], hand[1], hand[2] - 0.012, 0.03, 0.03, 0.02, P["steel"], outline=False)


def draw_front(c, arm_l, arm_r):
    """Kunai na direita (em linha com o antebraço) e shuriken na esquerda."""
    P = pal()
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.07)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    d = mk.norm((c.fx * 0.95, c.fy * 0.95, 0.12 if c.is_melee else 0.5))
    mk.obox(c, mk.add(hand_r, d, -0.1), d, 0.12, 0.04, 0.04, P["glove"])
    mk.obox(c, mk.add(hand_r, d, 0.02), d, 0.02, 0.07, 0.04, P["steel_dark"], outline=False)
    mk.obox(c, mk.add(hand_r, d, 0.04), d, 0.14, 0.05, 0.016, P["steel"])
    mk.obox(c, mk.add(hand_r, d, 0.18), d, 0.07, 0.026, 0.014, P["steel"])
    _shuriken(c, hand_l)
    if c.is_melee and c.atk_progress >= 0.35:
        for j in range(1, 4):
            ghost = attack_arms_at(c, c.atk_progress - 0.05 * j)
            g = (ghost[0], ghost[1], ghost[2] - 0.065)
            mk.band(c, (mk.add(g, d, 0.1), mk.add(g, d, 0.25), mk.add(hand_r, d, 0.25), mk.add(hand_r, d, 0.1)), (210, 230, 250, int(160 / j)))


def attack_arms_at(c, p):
    saved = c.atk_progress
    c.atk_progress = p
    try:
        return attack_arms(c)[1]
    finally:
        c.atk_progress = saved
