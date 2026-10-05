"""
Tomoe, a miko arqueira (6.5.5): cabelo preto longo e liso com franja reta e fita vermelha, kosode branco de mangas largas
com cordões vermelhos, hakama vermelha larga e pregueada, tabi branco com zori, omamori vermelho no quadril e o yumi, o arco
japonês alto, na mão esquerda.
Só o visual muda: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk

PALETTE = {
    "torso": (248, 246, 244), "pants": (206, 40, 38), "hair": (22, 20, 26), "belt": (206, 40, 38),
    "skin": (248, 224, 206), "skin_shadow": (218, 186, 168),
    "white": (248, 246, 244), "white_dark": (214, 212, 216), "red": (206, 40, 38), "red_dark": (146, 24, 28), "gold": (232, 190, 70),
    "hair_light": (84, 78, 98), "eye": (44, 28, 24), "brow": (28, 22, 24), "lip": (214, 110, 118),
    "tabi": (248, 246, 244), "zori": (200, 160, 110), "wood": (112, 70, 38), "wood_light": (166, 114, 62), "string": (244, 240, 230), "arrow": (180, 140, 80),
}


MATERIALS = {"white": "silk", "white_dark": "silk", "red": "silk", "red_dark": "silk", "zori": "canvas"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return PALETTE


def draw_behind(c):
    P = pal()
    if mk.facing_camera(c):
        mk.hair_volume(c, P["hair"], size=0.14, height=0.12)
        _long_hair(c)


def _long_hair(c):
    """Cabelo longo e liso até o quadril, balançando com o vento."""
    P = pal()
    anchor = (c.base_x - c.fx * 0.075, c.base_y - c.fy * 0.075, c.head_z + 0.13)
    mk.panels(c, anchor, 6, 0.115, 0.14, 0.05, (P["hair"], P["hair"], P["hair"], P["hair"], P["hair"], P["hair_light"]), phase=0.5, up=(c.fx, c.fy, 0.0), drag=(-c.fx * 0.03, -c.fy * 0.03), flare=-0.004)


def draw_legs(c):
    """Hakama vermelha larga e pregueada até o tornozelo, tabi branco e zori."""
    P = pal()
    mk.legs(c, P["pants"], baggy=(0.165, 0.18), foot_color=P["tabi"], foot_len=0.13, sole=P["zori"], texture="pleats")


def draw_obi(c):
    """Cós da hakama com os cordões brancos amarrados na frente e o omamori vermelho no quadril."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.01, c.pelvis_w * 0.78, 0.05, P["red_dark"])
    mk.cbox(c, bx + fx * 0.088, by + fy * 0.088, z + 0.005, 0.07, 0.025, 0.045, P["white"], outline=False)
    trail, amp, freq = mk.motion(c, 0.05)
    offs = mk.cloth_offsets(c, 2, 0.9, trail, amp * 1.4, freq, (bx, by))
    for i, o in enumerate(offs):
        mk.cbox(c, bx + fx * 0.098 + px * 0.02 + o[0], by + fy * 0.098 + py * 0.02 + o[1], z - 0.055 * (i + 1) + o[2], 0.026, 0.02, 0.06, P["white"], outline=False)
    bag = (bx - px * 0.13 - fx * 0.02, by - py * 0.13 - fy * 0.02)
    offs = mk.cloth_offsets(c, 1, 1.4, trail, amp, freq, bag)
    mk.cbox(c, bag[0] + offs[0][0], bag[1] + offs[0][1], z - 0.1, 0.05, 0.03, 0.08, P["red"])
    mk.cbox(c, bag[0] + offs[0][0], bag[1] + offs[0][1], z - 0.03, 0.012, 0.012, 0.03, P["gold"], outline=False)


def draw_torso(c):
    """Colarinho em V com o forro vermelho aparecendo e a gola alta do kosode."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.085 + 0.006
    apex = (bx + fx * front, by + fy * front, tz + 0.1)
    for s in (-1.0, 1.0):
        top = (bx + fx * (front - 0.004) + px * 0.06 * s, by + fy * (front - 0.004) + py * 0.06 * s, tz + 0.25)
        mk.limb(c, top, apex, 0.03, P["red"], outline=False, height=0.016)
        mk.limb(c, mk.add(top, (px * -0.012 * s, py * -0.012 * s, 0.0)), mk.add(apex, (0, 0, 0.01)), 0.016, P["white_dark"], outline=False, height=0.018)
    mk.cbox(c, bx + fx * (front - 0.004), by + fy * (front - 0.004), tz + 0.195, 0.045, 0.018, 0.06, P["skin"], outline=False)


def draw_arm(c, shoulder, hand, side):
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], w=0.052)


def draw_sleeves(c, arms):
    """Mangas largas e soltas do kosode, com um cordão vermelho no meio."""
    P = pal()
    atk = math.sin(c.atk_progress * math.pi) if c.is_melee else 0.0
    for k, (s, e, side) in enumerate(arms):
        anchor = (s[0] + c.px * side * 0.05, s[1] + c.py * side * 0.05, s[2] - 0.01)
        last = mk.panels(c, anchor, 3, 0.115, 0.065, 0.19, (P["white"], P["white"], P["white_dark"]), phase=1.7 * k, side=side, spread=0.016, flare=0.012,
                         drag=(-c.fx * 0.1 * atk, -c.fy * 0.1 * atk))
        mid = (anchor[0] + c.px * side * 0.03, anchor[1] + c.py * side * 0.03, anchor[2] - 0.2)
        mk.obox(c, (mid[0], mid[1], mid[2] + 0.014), (0.0, 0.0, -1.0), 0.014, 0.07, 0.2, P["red"], up=(c.fx, c.fy, 0.0), outline=False)


def draw_head(c):
    """Rosto de traços suaves, franja reta, mechas laterais longas e a fita vermelha amarrada em laço."""
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    mk.face(c, P["eye"], P["brow"], P["lip"], P["skin_shadow"], brow_tilt=0.0, spacing=0.032, mouth_w=0.022)
    mk.cbox(c, bx, by, hz + 0.118, 0.158, 0.158, 0.08, P["hair"])
    if not mk.facing_camera(c):
        mk.hair_volume(c, P["hair"], size=0.15, height=0.12)
        _long_hair(c)
    mk.obox(c, (bx + fx * (hw / 2 - 0.016), by + fy * (hw / 2 - 0.016), hz + 0.14), (fx, fy, 0.0), 0.03, hw + 0.01, 0.045, P["hair"], outline=False)  # franja reta
    trail, amp, freq = mk.motion(c, 0.06)
    for s in (-1.0, 1.0):
        anchor = (bx + px * 0.078 * s + fx * 0.02, by + py * 0.078 * s + fy * 0.02, hz + 0.1)
        mk.panels(c, anchor, 4, 0.1, 0.034, 0.045, (P["hair"],) * 4, phase=0.8 * s, up=(fx, fy, 0.0), trail=trail, amp=amp, freq=freq)
    root = (bx - fx * 0.085, by - fy * 0.085, hz + 0.1)
    mk.cbox(c, root[0], root[1], root[2], 0.045, 0.045, 0.04, P["red"])
    for s in (-1.0, 1.0):
        mk.obox(c, root, (px * s * 0.9, py * s * 0.9, 0.3), 0.075, 0.03, 0.04, P["red"])
    offs = mk.cloth_offsets(c, 2, 2.1, trail, amp * 1.6, freq * 1.2, root)
    for i, o in enumerate(offs):
        mk.cbox(c, root[0] - fx * 0.02 + o[0], root[1] - fy * 0.02 + o[1], root[2] - 0.06 - 0.05 * i + o[2], 0.026, 0.02, 0.055, P["red"], outline=False)


def draw_front(c, arm_l, arm_r):
    """Yumi vertical ao lado na neutra; levantado e à frente no ataque, com a flecha e a corda."""
    P = pal()
    hand = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    idle = not c.is_moving and not c.is_melee
    if idle:
        bx, by, bz = hand[0] + c.fx * 0.04, hand[1] + c.fy * 0.04, c.base_z + 0.02
        d, length = (0.0, 0.0, 1.0), 1.0
        base = (bx, by, bz)
        mk.obox(c, base, d, 0.35, 0.05, 0.05, P["wood"])
        mk.obox(c, mk.add(base, d, 0.35), d, 0.28, 0.05, 0.05, P["wood_light"])
        mk.obox(c, mk.add(base, d, 0.63), d, 0.38, 0.045, 0.045, P["wood"])
        top, bottom = mk.add(base, d, 1.0), base
    else:
        base = (hand[0] + c.fx * 0.12, hand[1] + c.fy * 0.12, c.torso_z - 0.2)
        d = mk.norm((c.fx * 0.2, c.fy * 0.2, 0.95))
        mk.obox(c, base, d, 0.34, 0.055, 0.055, P["wood"])
        mk.obox(c, mk.add(base, d, 0.34), d, 0.3, 0.055, 0.055, P["wood_light"])
        mk.obox(c, mk.add(base, d, 0.64), d, 0.3, 0.05, 0.05, P["wood"])
        top, bottom = mk.add(base, d, 0.94), base
    grip = mk.lerp(bottom, top, 0.5)
    mk.cbox(c, grip[0], grip[1], grip[2] - 0.04, 0.062, 0.062, 0.08, P["red"], outline=False)
    drawing = (c.extra_props or {}).get("is_drawing", False)
    pull = mk.add(grip, (-c.fx, -c.fy, 0.0), 0.25) if drawing else mk.add(grip, (-c.fx, -c.fy, 0.0), 0.05)
    mk.limb(c, top, pull, 0.01, P["string"], outline=False)
    mk.limb(c, pull, bottom, 0.01, P["string"], outline=False)
    if drawing:
        d2 = mk.norm((c.fx, c.fy, 0.0))
        mk.obox(c, mk.add(pull, d2, -0.02), d2, 0.55, 0.014, 0.014, P["arrow"])
        mk.obox(c, mk.add(pull, d2, 0.53), d2, 0.05, 0.03, 0.012, (200, 200, 210))
