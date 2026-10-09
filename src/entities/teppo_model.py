"""
Teppo, o arcabuzeiro (6.5.5): jingasa preta cônica com brasão dourado e jugular, armadura oliva-acinzentada com cordões,
ombreiras em camadas, kusazuri na cintura, calça oliva presa nas caneleiras de ferro, sandálias de palha, chifre de pólvora,
bandoleira e o arcabuz de cano longo com o pavio aceso e fumaça.
Só o visual muda: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk

PALETTE = {
    "torso": (74, 82, 60), "pants": (84, 90, 62), "hair": (28, 26, 24), "belt": (54, 44, 34),
    "skin": (222, 180, 142), "skin_shadow": (186, 142, 108),
    "armor": (66, 74, 62), "armor_dark": (44, 50, 44), "lace": (150, 140, 110), "iron": (82, 86, 94), "iron_light": (140, 144, 154),
    "hat": (30, 28, 26), "hat_light": (62, 58, 52), "gold": (214, 176, 70), "strap": (22, 20, 20),
    "sandal": (176, 146, 92), "tabi": (60, 56, 48), "horn": (206, 178, 118), "cord": (150, 120, 70),
    "wood": (124, 80, 44), "wood_dark": (84, 52, 30), "barrel": (78, 82, 92), "ember": (255, 150, 50), "smoke": (210, 210, 214),
    "eye": (30, 24, 20), "brow": (26, 22, 20), "lip": (170, 110, 96),
}


MATERIALS = {"armor": "metal", "armor_dark": "metal", "iron": "metal", "iron_light": "chrome", "pants": "canvas", "torso": "canvas", "hat": "metal", "belt": "leather", "wood": "planks", "wood_dark": "planks", "barrel": "metal", "horn": "lacquer", "gold": "gold"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return PALETTE


def draw_behind(c):
    if mk.facing_camera(c):
        mk.hair_volume(c, pal()["hair"], size=0.14, height=0.1)


def draw_legs(c):
    """Calça oliva larga presa em caneleiras de ferro, tabi escuro e sandália de palha."""
    P = pal()
    mk.legs(c, P["pants"], boot=P["iron"], boot_h=0.15, baggy=(0.15, 0.14), foot_color=P["tabi"], foot_len=0.13, sole=P["sandal"], cuff=P["iron_light"], texture="cloth")


def draw_obi(c):
    """Cinto de couro, kusazuri (placas da saia da armadura), chifre de pólvora e bolsa de balas."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z
    mk.cbox(c, bx, by, z + 0.065, c.pelvis_w, c.pelvis_w * 0.78, 0.07, P["belt"])
    trail, amp, freq = mk.motion(c, 0.05)
    for k, (fwd, lat) in enumerate(((0.105, -0.07), (0.105, 0.0), (0.105, 0.07), (0.0, -0.145), (0.0, 0.145))):
        anchor = (bx + fx * fwd + px * lat, by + fy * fwd + py * lat, z + 0.075)
        if abs(lat) > 0.1:
            anchor = (bx + px * lat, by + py * lat, z + 0.075)
        offs = mk.cloth_offsets(c, 2, 0.6 * k, trail, amp, freq, anchor)
        for i, o in enumerate(offs):
            mk.cbox(c, anchor[0] + o[0], anchor[1] + o[1], anchor[2] - 0.065 * (i + 1) + o[2], 0.06, 0.03, 0.068, P["armor_dark"] if i else P["armor"])
    horn = (bx - px * 0.15 - fx * 0.02, by - py * 0.15 - fy * 0.02, z + 0.02)
    mk.obox(c, horn, mk.norm((-px * 0.4, -py * 0.4, -0.9)), 0.12, 0.05, 0.05, P["horn"])
    mk.obox(c, mk.add(horn, mk.norm((-px * 0.4, -py * 0.4, -0.9)), 0.12), mk.norm((-px * 0.5 + fx * 0.3, -py * 0.5 + fy * 0.3, -0.8)), 0.06, 0.04, 0.04, P["horn"])
    mk.cbox(c, bx + px * 0.15 - fx * 0.03, by + py * 0.15 - fy * 0.03, z + 0.0, 0.07, 0.06, 0.08, P["belt"])


def draw_torso(c):
    """Peitoral de armadura com cordões, golas e a bandoleira cruzando o peito."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    mk.cbox(c, bx, by, tz + 0.04, 0.315, 0.245, 0.2, P["armor"])
    front = 0.125 + 0.02
    for i in range(3):
        mk.cbox(c, bx + fx * (front - 0.005), by + fy * (front - 0.005), tz + 0.06 + i * 0.055, 0.2, 0.012, 0.012, P["lace"], outline=False)
    mk.cbox(c, bx + fx * (front - 0.012), by + fy * (front - 0.012), tz + 0.205, 0.07, 0.016, 0.07, P["skin"], outline=False)
    mk.cbox(c, bx, by, tz + 0.235, 0.17, 0.15, 0.05, P["armor_dark"])  # gorjal
    a = (bx - px * 0.115 + fx * (front - 0.01), by - py * 0.115 + fy * (front - 0.01), tz + 0.27)
    b = (bx + px * 0.11 + fx * (front - 0.01), by + py * 0.11 + fy * (front - 0.01), tz + 0.02)
    mk.limb(c, a, b, 0.032, P["cord"], outline=False, height=0.018)
    a2 = (bx - px * 0.115 - fx * 0.12, by - py * 0.115 - fy * 0.12, tz + 0.27)
    b2 = (bx + px * 0.11 - fx * 0.12, by + py * 0.11 - fy * 0.12, tz + 0.02)
    mk.limb(c, a2, b2, 0.032, P["cord"], outline=False, height=0.018)


def draw_arm(c, shoulder, hand, side):
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], sleeve=P["torso"], sleeve_to=0.5, bracer=P["iron"], bracer_span=(0.35, 0.95), w=0.062)


def draw_sleeves(c, arms):
    """Ombreiras (sode) em três placas de ferro com cordões."""
    P = pal()
    for s, e, side in arms:
        z = s[2] + 0.02
        ox, oy = c.px * side * 0.03, c.py * side * 0.03
        for i, (w, h, col) in enumerate(((0.15, 0.04, P["armor"]), (0.135, 0.04, P["armor_dark"]), (0.12, 0.04, P["armor"]))):
            mk.cbox(c, s[0] + ox * (1 + 0.4 * i), s[1] + oy * (1 + 0.4 * i), z - 0.045 * i - 0.02, w, w - 0.02, h, col)
        mk.cbox(c, s[0] + ox * 1.6, s[1] + oy * 1.6, z - 0.115, 0.012, 0.012, 0.012, P["lace"], outline=False)


def draw_head(c):
    """Jingasa cônica com brasão e jugular; rosto marcado de sol com bigode."""
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    mk.face(c, P["eye"], P["brow"], P["lip"], P["skin_shadow"], brow_tilt=0.006, spacing=0.04)
    if mk.facing_camera(c):
        mk.obox(c, (bx + fx * (hw / 2 - 0.01), by + fy * (hw / 2 - 0.01), hz + 0.052), (fx, fy, 0.0), 0.02, 0.07, 0.014, P["hair"], outline=False)  # bigode
    mk.cbox(c, bx, by, hz + 0.145, 0.164, 0.164, 0.03, P["hair"])
    mk.cbox(c, bx, by, hz + 0.17, 0.34, 0.34, 0.025, P["hat"])
    mk.cbox(c, bx, by, hz + 0.195, 0.24, 0.24, 0.03, P["hat"])
    mk.cbox(c, bx, by, hz + 0.225, 0.15, 0.15, 0.035, P["hat"])
    mk.cbox(c, bx, by, hz + 0.26, 0.07, 0.07, 0.03, P["hat_light"], outline=False)
    mk.cbox(c, bx + fx * 0.075, by + fy * 0.075, hz + 0.2, 0.03, 0.03, 0.03, P["gold"], outline=False)
    for s in (-1.0, 1.0):
        mk.limb(c, (bx + px * 0.1 * s + fx * 0.02, by + py * 0.1 * s + fy * 0.02, hz + 0.17), (bx + px * 0.04 * s + fx * 0.06, by + py * 0.04 * s + fy * 0.06, hz + 0.02), 0.01, P["strap"], outline=False)


def _rifle_dir(c, hand_r, hand_l):
    d = (hand_l[0] - hand_r[0], hand_l[1] - hand_r[1], hand_l[2] - hand_r[2])
    if abs(d[0]) + abs(d[1]) + abs(d[2]) < 1e-3:
        return mk.norm((c.fx, c.fy, 0.2))
    return mk.norm(d)


def draw_front(c, arm_l, arm_r):
    """Arcabuz de coronha de madeira e cano longo, com o pavio aceso, a corda pendurada e a fumaça."""
    P = pal()
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    d = _rifle_dir(c, hand_r, hand_l)
    butt = mk.add(hand_r, d, -0.24)
    mk.obox(c, butt, d, 0.2, 0.055, 0.09, P["wood_dark"])
    mk.obox(c, mk.add(butt, d, 0.2), d, 0.3, 0.052, 0.062, P["wood"])
    mk.obox(c, mk.add(butt, d, 0.5), d, 0.22, 0.046, 0.05, P["wood"])
    barrel = mk.add(butt, d, 0.3)
    mk.obox(c, barrel, d, 0.5, 0.036, 0.036, P["barrel"])
    for t in (0.12, 0.3, 0.46):
        mk.obox(c, mk.add(barrel, d, t), d, 0.016, 0.046, 0.046, P["iron_light"], outline=False)
    lock = mk.add(hand_r, d, 0.0)
    mk.cbox(c, lock[0] - 0.02, lock[1] - 0.02, lock[2] + 0.04, 0.04, 0.04, 0.05, P["iron"])
    mk.cbox(c, lock[0] - 0.012, lock[1] - 0.012, lock[2] + 0.085, 0.024, 0.024, 0.024, P["ember"], outline=False)
    trail, amp, freq = mk.motion(c, 0.06)
    offs = mk.cloth_offsets(c, 3, 0.4, trail, amp * 1.5, freq, lock)
    for i, o in enumerate(offs):
        mk.cbox(c, lock[0] + o[0] - 0.008, lock[1] + o[1] - 0.008, lock[2] + 0.03 - 0.05 * (i + 1) + o[2], 0.016, 0.016, 0.05, P["cord"], outline=False)
    muzzle = mk.add(butt, d, 0.8)
    for i in range(3):  # fumaça do pavio e do cano, subindo e abrindo ao vento
        o = mk.cloth_offsets(c, 3, 0.9 * i, (0.0, 0.0), 0.02, 1.4, muzzle, wind_gain=0.12)[2]
        r = 0.03 + 0.015 * i
        mk.band(c, ((muzzle[0] - r + o[0], muzzle[1] + o[1], muzzle[2] + 0.06 * i), (muzzle[0] + r + o[0], muzzle[1] + o[1], muzzle[2] + 0.06 * i),
                    (muzzle[0] + r * 1.4 + o[0], muzzle[1] + o[1], muzzle[2] + 0.06 * i + 0.08), (muzzle[0] - r * 1.4 + o[0], muzzle[1] + o[1], muzzle[2] + 0.06 * i + 0.08)),
                P["smoke"] + (int(70 - 18 * i),))
    if c.is_melee and c.atk_progress >= 0.4:
        mk.band(c, (mk.add(muzzle, d, 0.02), mk.add(muzzle, d, 0.16), mk.add(muzzle, (0, 0, 0.1), 1.0), muzzle), P["ember"] + (200,))
