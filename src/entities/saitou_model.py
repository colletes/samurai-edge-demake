"""
Saitou, o capitão do Shinsengumi (6.5.5): haori azul-piscina com a barra em zigue-zague branco (dandara) sobre o quimono
azul-marinho, faixa branca, hakama larga e escura presa nas caneleiras pretas, tabi branco, topknot e rosto severo.
Gatotsu: a katana longa aponta na altura dos olhos, a mão direita junto ao colarinho; a bainha vazia fica no quadril esquerdo.
Só o visual muda: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk

PALETTE = {
    "torso": (134, 202, 226), "pants": (36, 42, 74), "hair": (24, 24, 30), "belt": (238, 238, 244),
    "skin": (238, 204, 176), "skin_shadow": (206, 168, 140),
    "haori": (134, 202, 226), "haori_dark": (92, 154, 186), "zig": (244, 248, 252), "navy": (30, 38, 66), "hakama_dark": (24, 28, 52),
    "kyahan": (26, 26, 32), "tabi": (238, 238, 242), "sandal": (46, 40, 36), "strap": (210, 210, 220),
    "eye": (30, 24, 24), "brow": (22, 20, 22), "lip": (190, 120, 110),
    "saya": (28, 30, 40), "gold": (214, 184, 96), "steel": (224, 234, 246), "edge": (252, 254, 255), "ito": (24, 26, 36),
    "aura": (150, 214, 255), "aura_core": (236, 250, 255),
}


MATERIALS = {"haori": "silk", "haori_dark": "silk", "navy": "silk", "belt": "silk", "kyahan": "leather", "saya": "lacquer", "strap": "canvas"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return PALETTE


def _sheath(c):
    k = (c.base_x + c.px * 0.14 + c.fx * 0.03, c.base_y + c.py * 0.14 + c.fy * 0.03, c.pelvis_z + 0.07)
    b = mk.norm((-c.fx * 0.82 + c.px * 0.3, -c.fy * 0.82 + c.py * 0.3, -0.3))
    return k, b


def _draw_sheath(c):
    P = pal()
    k, b = _sheath(c)
    mk.obox(c, k, b, 0.5, 0.044, 0.044, P["saya"])
    mk.obox(c, k, b, 0.03, 0.052, 0.052, P["gold"], outline=False)
    mk.obox(c, mk.add(k, b, 0.47), b, 0.03, 0.05, 0.05, P["gold"], outline=False)
    if c.is_moving and not c.is_melee:  # na caminhada a katana volta à bainha: só o cabo aparece
        h = (-b[0], -b[1], -b[2])
        mk.obox(c, k, h, 0.17, 0.04, 0.04, P["ito"])
        mk.obox(c, mk.add(k, b, -0.008), b, 0.016, 0.08, 0.08, P["gold"])


def draw_behind(c):
    k, b = _sheath(c)
    if mk.behind(c, mk.add(k, b, 0.25)):
        _draw_sheath(c)
    if mk.facing_camera(c):
        mk.hair_volume(c, pal()["hair"], size=0.16, height=0.13)
    if mk.facing_camera(c):
        _back_panel(c, pal())  # aba de trás do haori, atrás do corpo


def _back_panel(c, P):
    anchor = (c.base_x - c.fx * 0.12, c.base_y - c.fy * 0.12, c.torso_z + 0.22)
    last = mk.panels(c, anchor, 4, 0.1, 0.27, 0.024, (P["haori"], P["haori"], P["haori"], P["haori_dark"]), phase=0.6, up=(c.fx, c.fy, 0.0), flare=0.012)
    for i in range(5):  # zigue-zague branco na barra
        lat = (i - 2) * 0.055
        mk.cbox(c, last[0] + c.px * lat, last[1] + c.py * lat, last[2] - 0.02, 0.034, 0.028, 0.04, P["zig"], outline=False)


def draw_legs(c):
    """Hakama larga e escura que se estreita na caneleira preta, com tabi branco e sandália."""
    P = pal()
    mk.legs(c, P["pants"], boot=P["kyahan"], boot_h=0.15, baggy=(0.165, 0.155), foot_color=P["tabi"], foot_len=0.13, sole=P["sandal"], cuff=P["strap"], texture="pleats")


def draw_obi(c):
    """Faixa branca com nó de lado."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.008, c.pelvis_w * 0.74, 0.08, P["belt"])
    kx, ky = bx + fx * 0.1 - px * 0.04, by + fy * 0.1 - py * 0.04
    mk.cbox(c, kx, ky, z + 0.01, 0.07, 0.04, 0.06, P["belt"])
    trail, amp, freq = mk.motion(c, 0.05)
    offs = mk.cloth_offsets(c, 2, 0.9, trail, amp * 1.4, freq, (kx, ky))
    for i, o in enumerate(offs):
        mk.cbox(c, kx + o[0], ky + o[1], z - 0.06 * (i + 1) + o[2], 0.034, 0.024, 0.066, P["belt"], outline=False)


def draw_torso(c):
    """Quimono azul-marinho com colarinho branco aparecendo entre as abas do haori, que caem à frente e atrás."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.11 + 0.006
    mk.cbox(c, bx + fx * (front - 0.004), by + fy * (front - 0.004), tz + 0.0, 0.11, 0.024, 0.26, P["navy"], outline=False)
    apex = (bx + fx * (front + 0.004), by + fy * (front + 0.004), tz + 0.1)
    for s in (-1.0, 1.0):
        top = (bx + fx * front + px * 0.065 * s, by + fy * front + py * 0.065 * s, tz + 0.265)
        mk.limb(c, top, apex, 0.034, P["strap"], outline=False, height=0.018)
    mk.cbox(c, bx + fx * front, by + fy * front, tz + 0.2, 0.04, 0.018, 0.06, P["skin"], outline=False)
    for s in (-1.0, 1.0):  # abas da frente do haori
        anchor = (bx + fx * 0.122 + px * 0.135 * s, by + fy * 0.122 + py * 0.135 * s, tz + 0.2)
        last = mk.panels(c, anchor, 3, 0.1, 0.075, 0.022, (P["haori"], P["haori"], P["haori_dark"]), phase=0.9 * s, up=(fx, fy, 0.0), flare=0.006)
        for i in range(2):
            lat = (i - 0.5) * 0.04
            mk.cbox(c, last[0] + px * lat, last[1] + py * lat, last[2] - 0.015, 0.03, 0.026, 0.035, P["zig"], outline=False)
    if not mk.facing_camera(c):
        _back_panel(c, P)


def draw_arm(c, shoulder, hand, side):
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], bracer=P["kyahan"], bracer_span=(0.35, 0.95), w=0.058)


def draw_sleeves(c, arms):
    """Mangas largas do haori com a barra em zigue-zague branco."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.07)
    atk = math.sin(c.atk_progress * math.pi) if c.is_melee else 0.0
    for k, (s, e, side) in enumerate(arms):
        anchor = (s[0] + c.px * side * 0.05, s[1] + c.py * side * 0.05, s[2] - 0.01)
        last = mk.panels(c, anchor, 3, 0.1, 0.07, 0.17, (P["haori"], P["haori"], P["haori_dark"]), phase=1.7 * k, side=side, spread=0.014, flare=0.01,
                         drag=(-c.fx * 0.1 * atk, -c.fy * 0.1 * atk))
        for i in range(3):
            lat = (i - 1) * 0.06
            mk.cbox(c, last[0] + c.fx * lat, last[1] + c.fy * lat, last[2] - 0.01, 0.03, 0.03, 0.035, P["zig"], outline=False)


def draw_head(c):
    """Rosto severo, cabelo preto repuxado com topknot e costeletas."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    mk.face(c, P["eye"], P["brow"], P["lip"], P["skin_shadow"], brow_tilt=0.008, spacing=0.04)
    mk.cbox(c, bx, by, hz + 0.125, 0.166, 0.166, 0.07, P["hair"])
    if not mk.facing_camera(c):
        mk.hair_volume(c, P["hair"], size=0.16, height=0.13)
    for s in (-1.0, 1.0):
        mk.cbox(c, bx + px * 0.081 * s, by + py * 0.081 * s, hz + 0.07, 0.02, 0.05, 0.1, P["hair"], outline=False)
    trail, amp, freq = mk.motion(c, 0.06)
    root = (bx - fx * 0.02, by - fy * 0.02, hz + 0.19)
    o = mk.cloth_offsets(c, 1, 0.8, trail, amp * 1.6, freq, root)[0]
    mk.limb(c, root, (root[0] - fx * 0.04 + o[0], root[1] - fy * 0.04 + o[1], root[2] + 0.08), 0.06, P["hair"])
    mk.cbox(c, root[0] - 0.015, root[1] - 0.015, root[2] - 0.01, 0.03, 0.03, 0.02, P["strap"], outline=False)


def draw_front(c, arm_l, arm_r):
    """Katana no gatotsu: apontada à frente pela mão esquerda; no golpe a lâmina estende e deixa o rastro azul."""
    P = pal()
    k, b = _sheath(c)
    if not mk.behind(c, mk.add(k, b, 0.25)):
        _draw_sheath(c)
    if c.is_moving and not c.is_melee:
        return
    hand = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    d = mk.norm((c.fx * 0.95, c.fy * 0.95, -0.04 if not c.is_melee else -0.08))
    length = 0.74
    mk.sword(c, mk.add(hand, d, -0.02), d, length, P["steel"], P["edge"], P["ito"], P["gold"], P["gold"], guard_w=0.07)
    if c.is_melee and c.atk_progress >= 0.3:
        for j in range(1, 5):
            p = c.atk_progress - 0.06 * j
            if p < 0.2:
                break
            ghost = mk.add(hand, d, -0.06 * j)
            fade = 1.0 - j / 5.0
            tip, mid = mk.add(ghost, d, length), mk.add(ghost, d, length * 0.45)
            side = (c.px * 0.03, c.py * 0.03, 0.0)
            mk.band(c, (mid, tip, mk.add(tip, side, 1.0), mk.add(mid, side, 1.0)), P["aura"] + (int(200 * fade),))
