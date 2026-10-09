"""
Hanzo, o shinobi amarelo (6.5.5): capuz dourado com máscara preta e faixa dos olhos, túnica amarela com debrum preto e
bordado dourado, faixa preta com nó, ombreira de aço no ombro esquerdo, braçadeiras pretas com rebites, calça larga que se
estreita na bota preta, katana nas costas na diagonal e um kunai em cada mão.
Só o visual muda: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk

PALETTE = {
    "torso": (224, 172, 36), "pants": (206, 154, 28), "hair": (28, 24, 28), "belt": (30, 26, 32),
    "skin": (226, 190, 156), "skin_shadow": (60, 46, 34),
    "gold": (244, 204, 84), "yellow_dark": (170, 124, 22), "black": (28, 24, 30), "stud": (236, 200, 90),
    "steel": (176, 178, 190), "steel_dark": (96, 98, 112), "boot": (34, 30, 36),
    "eye": (244, 232, 190), "pupil": (24, 18, 18), "ito": (30, 26, 28), "aura": (255, 214, 70), "aura_core": (255, 244, 190),
}


MATERIALS = {"torso": "knit", "pants": "knit", "yellow_dark": "knit", "black": "leather", "boot": "leather", "steel": "metal", "steel_dark": "metal", "belt": "leather", "gold": "gold", "stud": "gold"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def _hands(c, p):
    """(esquerda, direita) do golpe de kunais: antecipação recolhida, estocada da direita e corte cruzado da esquerda."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    r = _smooth((p - 0.2) / 0.4)
    reach_r = 0.08 + 0.36 * r
    right = (bx + fx * reach_r - px * 0.10, by + fy * reach_r - py * 0.10, tz + 0.14 + 0.02 * r)
    s = _smooth((p - 0.35) / 0.4)
    lat = 0.18 - 0.30 * s
    reach_l = 0.0 + 0.30 * s
    left = (bx + fx * reach_l + px * lat, by + fy * reach_l + py * lat, tz + 0.12 - 0.02 * s)
    return left, right


def attack_arms(c):
    return _hands(c, c.atk_progress)


def _kunai_dirs(c):
    return (mk.norm((c.fx * 0.9, c.fy * 0.9, -0.1)), mk.norm((c.fx * 0.5 + c.px * 0.3, c.fy * 0.5 + c.py * 0.3, -0.2)))


def _kunai(c, hand, d):
    P = pal()
    tip = mk.add(hand, d, 0.04)
    mk.obox(c, mk.add(hand, d, -0.10), d, 0.1, 0.036, 0.036, P["ito"])
    mk.obox(c, mk.add(hand, d, -0.125), d, 0.03, 0.06, 0.012, P["steel_dark"], outline=False)  # argola do pomo
    mk.obox(c, mk.add(tip, d, -0.005), d, 0.02, 0.07, 0.04, P["gold"], outline=False)
    mk.obox(c, tip, d, 0.12, 0.05, 0.016, P["steel"])
    mk.obox(c, mk.add(tip, d, 0.12), d, 0.08, 0.026, 0.014, P["steel"])
    return mk.add(tip, d, 0.2)


def _back_sword(c):
    P = pal()
    origin = (c.base_x - c.fx * 0.13 + c.px * 0.09, c.base_y - c.fy * 0.13 + c.py * 0.09, c.torso_z - 0.03)
    d = mk.norm((-c.px * 0.5, -c.py * 0.5, 0.9))
    mk.obox(c, origin, d, 0.5, 0.044, 0.044, P["black"])
    mk.obox(c, origin, d, 0.03, 0.052, 0.052, P["gold"], outline=False)
    top = mk.add(origin, d, 0.5)
    mk.obox(c, top, d, 0.14, 0.04, 0.04, P["ito"])
    mk.obox(c, mk.add(top, d, -0.006), d, 0.014, 0.08, 0.08, P["gold"])
    return mk.add(origin, d, 0.3)


def draw_behind(c):
    mid = (c.base_x - c.fx * 0.13, c.base_y - c.fy * 0.13, 0.0)
    if mk.behind(c, mid):
        _back_sword(c)
    if mk.facing_camera(c):
        mk.hair_volume(c, pal()["torso"], size=0.17, height=0.14)


def draw_legs(c):
    P = pal()
    mk.legs(c, P["pants"], boot=P["boot"], boot_h=0.15, baggy=(0.15, 0.14), foot_color=P["boot"], foot_len=0.14, sole=(20, 18, 22), cuff=P["steel_dark"], texture="cloth")


def draw_obi(c):
    """Faixa preta larga com bordado dourado e um nó no lado com duas pontas que balançam."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.008, c.pelvis_w * 0.74, 0.09, P["black"])
    mk.cbox(c, bx, by, z + 0.082, c.pelvis_w - 0.008, c.pelvis_w * 0.74, 0.01, P["gold"], outline=False)
    kx, ky = bx + fx * 0.098 + px * 0.05, by + fy * 0.098 + py * 0.05
    mk.cbox(c, kx, ky, z + 0.015, 0.07, 0.05, 0.065, P["black"])
    trail, amp, freq = mk.motion(c, 0.05)
    for k, s in enumerate((-1.0, 1.0)):
        offs = mk.cloth_offsets(c, 3, 0.8 * k, trail, amp * 1.4, freq, (kx, ky))
        for i, o in enumerate(offs):
            mk.cbox(c, kx + px * 0.02 * s + o[0], ky + o[1], z - 0.06 * (i + 1) + o[2], 0.034, 0.026, 0.066, P["black"], outline=False)


def draw_torso(c):
    """Debrum preto cruzado com bordado dourado e a katana nas costas quando está do lado da câmera."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.11 + 0.006
    apex = (bx + fx * front - px * 0.02, by + fy * front - py * 0.02, tz + 0.06)
    for s in (-1.0, 1.0):
        top = (bx + fx * (front - 0.004) + px * 0.075 * s, by + fy * (front - 0.004) + py * 0.075 * s, tz + 0.265)
        mk.limb(c, top, apex, 0.04, P["black"], outline=False, height=0.02)
        mk.limb(c, mk.add(top, (0, 0, -0.01)), mk.add(apex, (0, 0, 0.012)), 0.012, P["gold"], outline=False, height=0.022)
    mk.cbox(c, bx + fx * (front - 0.003), by + fy * (front - 0.003), tz + 0.2, 0.06, 0.02, 0.07, P["black"], outline=False)  # gola
    mid = (bx - fx * 0.13, by - fy * 0.13, 0.0)
    if not mk.behind(c, mid):
        _back_sword(c)


def draw_arm(c, shoulder, hand, side):
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], sleeve=P["torso"], sleeve_to=1.1, glove=P["black"], bracer=P["black"], bracer_span=(0.4, 0.95), w=0.064, bend=0.03)


def draw_sleeves(c, arms):
    """Ombreira de aço no ombro esquerdo."""
    P = pal()
    for s, e, side in arms:
        if side > 0:
            z = s[2] + 0.03
            mk.cbox(c, s[0] + c.px * 0.015, s[1] + c.py * 0.015, z - 0.04, 0.115, 0.105, 0.04, P["steel_dark"])
            mk.cbox(c, s[0] + c.px * 0.025, s[1] + c.py * 0.025, z - 0.005, 0.1, 0.09, 0.035, P["steel"])
            mk.cbox(c, s[0] + c.px * 0.03, s[1] + c.py * 0.03, z + 0.025, 0.08, 0.07, 0.025, P["steel_dark"])


def draw_head(c):
    """Capuz amarelo com máscara preta, faixa dos olhos e a ponta do capuz caindo pelas costas e balançando."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    mk.cbox(c, bx, by, hz + 0.015, 0.172, 0.172, 0.18, P["torso"])
    if not mk.facing_camera(c):
        mk.hair_volume(c, P["torso"], size=0.17, height=0.14)
    if mk.facing_camera(c):
        mk.plate(c, hz + 0.03, 0.075, P["black"])
        mk.plate(c, hz + 0.105, 0.04, P["skin_shadow"], inset=0.004)
        mk.plate(c, hz + 0.145, 0.05, P["yellow_dark"])
        # Faixa dos olhos e máscara shinobi limpas (sem cubos saltados de olhos em 360°)
        pass
    trail, amp, freq = mk.motion(c, 0.09)
    root = (bx - fx * 0.08, by - fy * 0.08, hz + 0.05)
    offs = mk.cloth_offsets(c, 3, 0.7, trail, amp * 1.8, freq, root, wind_gain=0.06)
    for i, o in enumerate(offs):
        mk.cbox(c, root[0] - fx * 0.03 * i + o[0], root[1] - fy * 0.03 * i + o[1], root[2] - 0.07 * (i + 1) + o[2], 0.06 - 0.01 * i, 0.04, 0.075, P["torso"], outline=(i == 0))
    mk.limb(c, (bx, by, hz + 0.19), (bx - fx * 0.02, by - fy * 0.02, hz + 0.215), 0.05, P["yellow_dark"], outline=False)  # nó do capuz


def draw_front(c, arm_l, arm_r):
    """Kunais nas mãos (o da direita some se `has_kunai` for falso) e, no golpe, o rastro dourado."""
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    dr, dl = _kunai_dirs(c)
    if c.is_melee:
        dr = mk.norm((c.fx * 0.95, c.fy * 0.95, 0.0))
        dl = mk.norm((c.fx * 0.4 - c.px * 0.55, c.fy * 0.4 - c.py * 0.55, -0.05))
    if c.is_moving and not c.is_melee:
        dr = mk.norm((c.fx * 0.3, c.fy * 0.3, -0.8))
        dl = mk.norm((c.fx * 0.3, c.fy * 0.3, -0.8))
    if (c.extra_props or {}).get("has_kunai", True):
        _kunai(c, hand_r, dr)
    _kunai(c, hand_l, dl)
    if c.is_melee and c.atk_progress >= 0.3:
        _trail(c, c.atk_progress)


def _trail(c, p):
    P = pal()
    ghosts = []
    for j in range(5):
        pj = p - 0.06 * j
        if pj < 0.25:
            break
        left, right = _hands(c, pj)
        h = (right[0], right[1], right[2] - 0.065)
        d = mk.norm((c.fx * 0.95, c.fy * 0.95, 0.0))
        h2 = (left[0], left[1], left[2] - 0.065)
        d2 = mk.norm((c.fx * 0.4 - c.px * 0.55, c.fy * 0.4 - c.py * 0.55, -0.05))
        ghosts.append((mk.add(h, d, 0.12), mk.add(h, d, 0.24), mk.add(h2, d2, 0.12), mk.add(h2, d2, 0.24)))
    for j in range(len(ghosts) - 1):
        fade = 1.0 - j / 5.0
        for a0, a1, b0, b1 in ((ghosts[j][0], ghosts[j][1], ghosts[j + 1][0], ghosts[j + 1][1]), (ghosts[j][2], ghosts[j][3], ghosts[j + 1][2], ghosts[j + 1][3])):
            mk.band(c, (a0, a1, b1, b0), P["aura"] + (int(215 * fade),))
            mk.band(c, (mk.lerp(a0, a1, 0.5), a1, b1, mk.lerp(b0, b1, 0.5)), P["aura_core"] + (int(245 * fade),))
