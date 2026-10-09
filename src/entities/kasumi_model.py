"""
Kasumi, a kunoichi da Névoa (6.5.5): cabelo prateado com coque e franja, cachecol cinza que esvoaça, armadura cromada
(perneiras com joelheiras, ombreiras e manoplas), colete-espartilho preto com fivelas, cinto de utilidades com bombas de
fumaça, coldres nas coxas, adaga curta na mão direita.
Só o visual muda: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk

PALETTE = {
    "torso": (34, 38, 44), "pants": (176, 186, 206), "hair": (214, 220, 232), "belt": (30, 32, 38),
    "skin": (240, 218, 204), "skin_shadow": (208, 184, 172),
    "chrome": (188, 196, 210), "chrome_dark": (112, 120, 136), "chrome_light": (236, 242, 250), "black": (32, 34, 40), "leather": (52, 44, 40),
    "scarf": (150, 156, 168), "scarf_dark": (112, 118, 130), "buckle": (214, 218, 226), "bomb": (30, 30, 35), "fuse": (255, 150, 60),
    "eye": (120, 150, 196), "brow": (128, 134, 148), "lip": (196, 130, 130), "blade": (222, 232, 244), "edge": (252, 254, 255), "tie": (44, 48, 56),
}


MATERIALS = {"pants": "latex", "chrome": "chrome", "chrome_dark": "metal", "chrome_light": "chrome", "torso": "leather", "black": "leather", "leather": "leather", "belt": "leather", "scarf": "knit", "scarf_dark": "knit", "bomb": "lacquer", "buckle": "chrome", "blade": "steel", "edge": "steel"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return PALETTE


def draw_behind(c):
    if mk.facing_camera(c):
        mk.hair_volume(c, pal()["hair"], size=0.14, height=0.12)


def draw_legs(c):
    """Perneiras cromadas justas com joelheira de placa, botas de aço e coldres nas coxas."""
    P = pal()
    mk.legs(c, P["pants"], boot=P["chrome_dark"], boot_h=0.13, tight_w=(0.11, 0.094), foot_color=P["chrome"], foot_len=0.14, foot_w=0.07, sole=P["black"], cuff=P["chrome_light"])
    for side in mk.sorted_sides(c):
        sh, th = c.legs_data[side]["shin"], c.legs_data[side]["thigh"]
        mk.cbox(c, sh[0] + c.fx * 0.04, sh[1] + c.fy * 0.04, sh[2] + 0.17, 0.1, 0.1, 0.075, P["chrome_light"])
        mk.cbox(c, sh[0] + c.fx * 0.045, sh[1] + c.fy * 0.045, sh[2] + 0.08, 0.075, 0.075, 0.09, P["chrome"], outline=False)
    th = c.legs_data["L"]["thigh"]
    mk.cbox(c, th[0] + c.px * 0.055, th[1] + c.py * 0.055, th[2] + 0.04, 0.05, 0.07, 0.14, P["leather"])  # coldre


def draw_obi(c):
    """Cinto de utilidades com fivela, bomba de fumaça, bolsas e a corda da adaga."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z
    mk.cbox(c, bx, by, z + 0.065, c.pelvis_w - 0.01, c.pelvis_w * 0.8, 0.065, P["belt"])
    mk.cbox(c, bx + fx * 0.088, by + fy * 0.088, z + 0.07, 0.05, 0.02, 0.05, P["buckle"], outline=False)
    mk.cbox(c, bx + px * 0.12 + fx * 0.06, by + py * 0.12 + fy * 0.06, z + 0.0, 0.06, 0.05, 0.075, P["leather"])
    mk.cbox(c, bx - px * 0.12 + fx * 0.06, by - py * 0.12 + fy * 0.06, z + 0.0, 0.06, 0.05, 0.075, P["leather"])
    bomb = (bx - px * 0.15, by - py * 0.15)
    mk.cbox(c, bomb[0], bomb[1], z - 0.02, 0.085, 0.085, 0.085, P["bomb"])
    mk.cbox(c, bomb[0], bomb[1], z + 0.065, 0.026, 0.026, 0.045, P["fuse"], outline=False)
    mk.cbox(c, bx - fx * 0.11, by - fy * 0.11, z + 0.02, 0.1, 0.05, 0.08, P["leather"])


def draw_torso(c):
    """Colete-espartilho preto com cadarço e fivelas prateadas sobre o traje cromado."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    mk.cbox(c, bx, by, tz - 0.005, 0.218, 0.17, 0.2, P["torso"])
    front = 0.085 + 0.006
    for i in range(4):
        mk.cbox(c, bx + fx * front, by + fy * front, tz + 0.015 + i * 0.045, 0.07, 0.012, 0.012, P["buckle"], outline=False)
    for s in (-1.0, 1.0):
        mk.limb(c, (bx + px * 0.07 * s + fx * front, by + py * 0.07 * s + fy * front, tz + 0.2), (bx + px * 0.1 * s + fx * front, by + py * 0.1 * s + fy * front, tz + 0.01), 0.024, P["leather"], outline=False, height=0.014)
    mk.cbox(c, bx, by, tz + 0.2, 0.17, 0.14, 0.05, P["chrome"])  # gola cromada
    mk.cbox(c, bx + fx * 0.05, by + fy * 0.05, tz + 0.215, 0.07, 0.04, 0.04, P["skin"], outline=False)


def draw_arm(c, shoulder, hand, side):
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["chrome"], glove=P["black"], bracer=P["chrome_dark"], bracer_span=(0.35, 0.95), w=0.056)


def draw_sleeves(c, arms):
    """Ombreiras cromadas com borda clara."""
    P = pal()
    for s, e, side in arms:
        z = s[2] + 0.02
        ox, oy = c.px * side * 0.03, c.py * side * 0.03
        mk.cbox(c, s[0] + ox, s[1] + oy, z - 0.035, 0.115, 0.105, 0.045, P["chrome"])
        mk.cbox(c, s[0] + ox * 1.3, s[1] + oy * 1.3, z + 0.005, 0.1, 0.09, 0.025, P["chrome_light"], outline=False)


def draw_head(c):
    """Cabelo prateado com franja e coque preso por um laço, mechas laterais, cachecol cinza e a ponta longa ao vento."""
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    mk.face(c, P["eye"], P["brow"], P["lip"], P["skin_shadow"], brow_tilt=0.004, spacing=0.034)
    mk.cbox(c, bx, by, hz + 0.118, 0.158, 0.158, 0.078, P["hair"])
    if not mk.facing_camera(c):
        mk.hair_volume(c, P["hair"], size=0.15, height=0.12)
    for s in (-1.0, 0.0, 1.0):
        mk.limb(c, (bx + fx * 0.07 - px * 0.01 * s, by + fy * 0.07 - py * 0.01 * s, hz + 0.18), (bx + fx * 0.075 + px * 0.06 * s, by + fy * 0.075 + py * 0.06 * s, hz + 0.115), 0.03, P["hair"], outline=False)
    trail, amp, freq = mk.motion(c, 0.06)
    for s in (-1.0, 1.0):
        o = mk.cloth_offsets(c, 1, 0.8 * s, trail, amp, freq, (bx, by))[0]
        mk.cbox(c, bx + px * 0.075 * s + o[0], by + py * 0.075 * s + o[1], hz + 0.0, 0.03, 0.036, 0.16, P["hair"], outline=False)
    mk.cbox(c, bx - fx * 0.01, by - fy * 0.01, hz + 0.19, 0.08, 0.08, 0.07, P["hair"])  # coque
    mk.cbox(c, bx - fx * 0.01, by - fy * 0.01, hz + 0.186, 0.088, 0.088, 0.016, P["tie"], outline=False)
    nz = c.neck_z
    mk.cbox(c, bx, by, nz - 0.02, 0.125, 0.125, 0.06, P["scarf"])
    root = (bx - fx * 0.05, by - fy * 0.05, nz + 0.02)
    last = root
    t2, a2, f2 = mk.motion(c, 0.12)
    offs = mk.cloth_offsets(c, 4, 0.3, t2, a2 * 2.2, f2, root, wind_gain=0.08)
    for i, o in enumerate(offs):
        origin = (root[0] - fx * 0.06 * (i + 1) + px * 0.05 + o[0], root[1] - fy * 0.06 * (i + 1) + py * 0.05 + o[1], root[2] - 0.03 * (i + 1) + o[2])
        mk.limb(c, last, origin, 0.05 - 0.005 * i, P["scarf"] if i % 2 == 0 else P["scarf_dark"], outline=(i == 0), height=0.02)
        last = origin


def draw_front(c, arm_l, arm_r):
    """Adaga na direita, em guarda baixa e rápida; no golpe deixa um corte prateado."""
    P = pal()
    hand = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    d = mk.norm((c.fx * 0.7 - c.px * 0.3, c.fy * 0.7 - c.py * 0.3, -0.15 if not c.is_moving else -0.7))
    mk.sword(c, hand, d, 0.26, P["blade"], P["edge"], P["black"], P["chrome_dark"], P["chrome_light"], guard_w=0.07, grip_len=0.1, blade_w=0.046)
    if c.is_melee and c.atk_progress >= 0.3:
        for j in range(1, 4):
            g = mk.add(hand, (c.px * 0.04, c.py * 0.04, 0.0), -j * 2.0)
            mk.band(c, (mk.add(g, d, 0.1), mk.add(g, d, 0.32), mk.add(hand, d, 0.32), mk.add(hand, d, 0.1)), (220, 236, 255, int(170 / j)))
