"""
Anne, a capitã pirata (6.5.5): tricórnio preto com pluma, cabelo ruivo revolto, camisa cinza aberta com colete escuro, cintos
cruzados com chifre de pólvora e fivela dourada, casaco longo marrom-escuro com forro azul e galões dourados que balança, calça
larga em botas altas de cano dobrado, faixa na cintura, alfanje na direita e uma bomba de pavio aceso na esquerda.
Só o visual muda: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk
from src.isometric.voxel_rig import calc_blade_slash_3d

PALETTE = {
    "torso": (96, 98, 104), "pants": (84, 62, 44), "hair": (200, 84, 40), "belt": (118, 36, 40),
    "skin": (226, 178, 140), "skin_shadow": (190, 140, 106),
    "coat": (70, 48, 34), "coat_dark": (46, 32, 24), "lining": (40, 66, 120), "trim": (214, 172, 66), "vest": (38, 34, 36), "shirt": (150, 152, 158),
    "boot": (66, 44, 28), "boot_cuff": (96, 68, 42), "leather": (96, 62, 36), "horn": (206, 178, 110), "hat": (30, 28, 32),
    "feather": (210, 70, 54), "feather_white": (238, 232, 220), "eye": (40, 90, 70), "brow": (140, 56, 32), "lip": (184, 84, 80),
    "steel": (200, 210, 222), "edge": (250, 252, 255), "guard": (214, 172, 66), "grip": (60, 40, 28), "bomb": (30, 30, 34), "fuse": (255, 160, 60),
    "aura": (255, 170, 90), "aura_core": (255, 236, 190),
}


MATERIALS = {"coat": "velvet", "coat_dark": "velvet", "vest": "leather", "leather": "leather", "boot": "leather", "boot_cuff": "leather", "pants": "canvas", "torso": "canvas", "belt": "silk", "lining": "silk", "hat": "velvet", "steel": "steel", "guard": "gold", "trim": "gold"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return PALETTE


def _coat_back(c, P):
    anchor = (c.base_x - c.fx * 0.125, c.base_y - c.fy * 0.125, c.torso_z + 0.23)
    mk.panels(c, anchor, 5, 0.14, 0.3, 0.025, (P["coat"], P["coat"], P["coat"], P["coat_dark"], P["coat_dark"]), phase=0.5, up=(c.fx, c.fy, 0.0),
              drag=(-c.fx * 0.04, -c.fy * 0.04), flare=0.014)


def draw_behind(c):
    P = pal()
    if mk.facing_camera(c):
        mk.hair_volume(c, P["hair"], size=0.15, height=0.13)
        _coat_back(c, P)


def draw_legs(c):
    """Calça larga marrom presa em botas altas de couro com o cano dobrado."""
    P = pal()
    mk.legs(c, P["pants"], boot=P["boot"], boot_h=0.2, baggy=(0.14, 0.135), foot_color=P["boot"], foot_len=0.14, sole=(26, 20, 16), cuff=P["boot_cuff"])


def draw_obi(c):
    """Faixa vermelha larga na cintura, fivela dourada, chifre de pólvora e bolsa."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.06
    mk.cbox(c, bx, by, z, c.pelvis_w, c.pelvis_w * 0.8, 0.085, P["belt"])
    mk.cbox(c, bx + fx * 0.098, by + fy * 0.098, z + 0.015, 0.055, 0.025, 0.05, P["trim"], outline=False)
    trail, amp, freq = mk.motion(c, 0.05)
    offs = mk.cloth_offsets(c, 2, 0.8, trail, amp * 1.4, freq, (bx, by))
    for i, o in enumerate(offs):
        mk.cbox(c, bx + px * 0.12 + fx * 0.07 + o[0], by + py * 0.12 + fy * 0.07 + o[1], z - 0.06 * (i + 1) + o[2], 0.04, 0.026, 0.065, P["belt"], outline=False)
    horn = (bx - px * 0.15, by - py * 0.15, z - 0.02)
    d = mk.norm((-px * 0.3, -py * 0.3, -0.9))
    mk.obox(c, horn, d, 0.13, 0.05, 0.05, P["horn"])
    mk.obox(c, mk.add(horn, d, 0.13), mk.norm((-px * 0.4 + fx * 0.4, -py * 0.4 + fy * 0.4, -0.7)), 0.06, 0.04, 0.04, P["horn"])
    sheath_k = (bx + px * 0.14, by + py * 0.14, z + 0.01)
    mk.obox(c, sheath_k, mk.norm((-fx * 0.7 + px * 0.3, -fy * 0.7 + py * 0.3, -0.5)), 0.3, 0.04, 0.04, P["leather"])  # bainha vazia


def draw_torso(c):
    """Camisa aberta com colete escuro, cintos cruzados, fivela dourada e dragonas."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.085 + 0.006
    for s in (-1.0, 1.0):
        mk.cbox(c, bx + fx * (front - 0.004) + px * 0.07 * s, by + fy * (front - 0.004) + py * 0.07 * s, tz + 0.02, 0.07, 0.022, 0.2, P["vest"])
    mk.cbox(c, bx + fx * (front - 0.002), by + fy * (front - 0.002), tz + 0.15, 0.045, 0.018, 0.1, P["skin"], outline=False)  # peito aberto
    a = (bx - px * 0.1 + fx * (front + 0.004), by - py * 0.1 + fy * (front + 0.004), tz + 0.26)
    b = (bx + px * 0.1 + fx * (front + 0.004), by + py * 0.1 + fy * (front + 0.004), tz + 0.0)
    mk.limb(c, a, b, 0.032, P["leather"], outline=False, height=0.018)
    mk.limb(c, (a[0] + px * 0.2, a[1] + py * 0.2, a[2]), (b[0] - px * 0.2, b[1] - py * 0.2, b[2]), 0.03, P["leather"], outline=False, height=0.018)
    mk.cbox(c, bx + fx * (front + 0.006), by + fy * (front + 0.006), tz + 0.115, 0.04, 0.014, 0.04, P["trim"], outline=False)
    for s in (-1.0, 1.0):  # dragonas douradas
        mk.cbox(c, bx + px * 0.14 * s, by + py * 0.14 * s, tz + 0.28, 0.08, 0.07, 0.03, P["trim"], outline=False)
    if not mk.facing_camera(c):
        _coat_back(c, P)


def draw_arm(c, shoulder, hand, side):
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], sleeve=P["coat"], sleeve_to=0.6, bracer=P["leather"], bracer_span=(0.55, 0.95), w=0.058)


def draw_sleeves(c, arms):
    """Abas do casaco que caem à frente dos dois lados (forro azul aparecendo) e punhos com galão dourado."""
    P = pal()
    for s, e, side in arms:
        anchor = (c.base_x + c.fx * 0.09 + c.px * 0.125 * side, c.base_y + c.fy * 0.09 + c.py * 0.125 * side, c.torso_z + 0.2)
        last = mk.panels(c, anchor, 4, 0.115, 0.07, 0.024, (P["coat"], P["coat"], P["coat_dark"], P["coat_dark"]), phase=0.9 * side, up=(c.fx, c.fy, 0.0), flare=0.01)
        mk.cbox(c, anchor[0] + c.px * side * 0.03, anchor[1] + c.py * side * 0.03 + c.fy * 0.012, anchor[2] - 0.45, 0.014, 0.03, 0.45, P["lining"], outline=False)
        mk.cbox(c, e[0], e[1], e[2] + 0.02, 0.07, 0.07, 0.02, P["trim"], outline=False)


def draw_head(c):
    """Rosto de olhos verdes, cabelo ruivo revolto com mechas ao vento e o tricórnio com pluma."""
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    mk.face(c, P["eye"], P["brow"], P["lip"], P["skin_shadow"], brow_tilt=0.005, spacing=0.032, mouth_w=0.03)
    mk.cbox(c, bx, by, hz + 0.115, 0.16, 0.16, 0.075, P["hair"])
    if not mk.facing_camera(c):
        mk.hair_volume(c, P["hair"], size=0.15, height=0.13)
    trail, amp, freq = mk.motion(c, 0.1)
    for i, (a, b) in enumerate(((1.0, 0.0), (-1.0, 0.0), (0.7, -0.9), (-0.7, -0.9), (0.0, -1.0))):
        o = mk.cloth_offsets(c, 1, 0.9 * i, trail, amp * 2.0, freq, (bx, by), wind_gain=0.1)[0]
        root = (bx + px * 0.075 * a - fx * 0.04 * (-b), by + py * 0.075 * a - fy * 0.04 * (-b), hz + 0.1)
        tip = (root[0] + px * a * 0.04 - fx * 0.06 * (-b) + o[0], root[1] + py * a * 0.04 - fy * 0.06 * (-b) + o[1], root[2] - 0.17 + o[2])
        mk.limb(c, root, tip, 0.04, P["hair"], outline=False)
    mk.cbox(c, bx, by, hz + 0.18, 0.196, 0.196, 0.03, P["trim"], outline=False)
    mk.cbox(c, bx, by, hz + 0.18, 0.18, 0.18, 0.07, P["hat"])
    mk.cbox(c, bx, by, hz + 0.166, 0.31, 0.31, 0.022, P["hat"])
    for s in (-1.0, 0.0, 1.0):  # abas viradas para cima nos três lados
        mk.cbox(c, bx + fx * 0.145 * (1.0 if s == 0 else 0.0) + px * 0.145 * s * (1.0 if s != 0 else 0.0), by + fy * 0.145 * (1.0 if s == 0 else 0.0) + py * 0.145 * s * (1.0 if s != 0 else 0.0),
                hz + 0.18, 0.09, 0.09, 0.05, P["hat"], outline=False)
    root = (bx + px * 0.1, by + py * 0.1, hz + 0.24)
    offs = mk.cloth_offsets(c, 3, 0.4, trail, amp * 1.8, freq, root, wind_gain=0.07)
    prev = root
    for i, o in enumerate(offs):
        tip = (root[0] + px * 0.03 * (i + 1) - fx * 0.04 * (i + 1) + o[0], root[1] + py * 0.03 * (i + 1) - fy * 0.04 * (i + 1) + o[1], root[2] + 0.06 - 0.025 * i + o[2])
        mk.limb(c, prev, tip, 0.036 - 0.007 * i, P["feather"] if i < 2 else P["feather_white"], outline=False, height=0.012)
        prev = tip


def _cutlass(c, hand, d, up):
    """Alfanje de lâmina curva em três segmentos, guarda dourada e punho de couro."""
    P = pal()
    mk.obox(c, mk.add(hand, d, -0.1), d, 0.11, 0.042, 0.042, P["grip"])
    mk.obox(c, mk.add(hand, d, 0.0), d, 0.02, 0.09, 0.075, P["guard"])
    prev, dd = mk.add(hand, d, 0.02), d
    for i, (length, bend) in enumerate(((0.22, 0.0), (0.2, 0.16), (0.16, 0.2))):
        dd = mk.norm(mk.add(dd, up, bend))
        mk.obox(c, prev, dd, length, 0.066 - 0.01 * i, 0.028, P["steel"])
        mk.obox(c, mk.add(prev, dd, 0.01), dd, length - 0.01, 0.018, 0.03, P["edge"], outline=False)
        prev = mk.add(prev, dd, length)
    return prev


def draw_front(c, arm_l, arm_r):
    """Alfanje na mão direita (no ombro na neutra, baixo na caminhada, em arco no corte) e a bomba na esquerda."""
    P = pal()
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    if c.is_melee:
        info = calc_blade_slash_3d("pirate", "ATTACK", c.atk_progress, c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py)
        d = mk.norm(tuple(info["dir"]))
        up = (c.px * 0.0, c.py * 0.0, -0.6)
    elif c.is_moving:
        d, up = mk.norm((c.fx * 0.4, c.fy * 0.4, -0.7)), (c.fx * 0.3, c.fy * 0.3, 0.2)
    else:
        d, up = mk.norm((-c.fx * 0.65 - c.px * 0.3, -c.fy * 0.65 - c.py * 0.3, 0.6)), (c.fx * 0.4, c.fy * 0.4, 0.2)
    _cutlass(c, hand_r, d, up)
    if c.is_melee and c.atk_progress >= 0.25:
        ghosts = []
        for j in range(5):
            pj = c.atk_progress - 0.07 * j
            if pj < 0.1:
                break
            ang = -1.60 + pj * 3.20
            h = (c.base_x + c.fx * math.cos(ang) * 0.30 - c.px * math.sin(ang) * 0.30, c.base_y + c.fy * math.cos(ang) * 0.30 - c.py * math.sin(ang) * 0.30, c.torso_z + 0.16)
            dj = mk.norm(tuple(calc_blade_slash_3d("pirate", "ATTACK", pj, c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py)["dir"]))
            ghosts.append((mk.add(h, dj, 0.42), mk.add(h, dj, 0.62)))
        for j in range(len(ghosts) - 1):
            fade = 1.0 - j / 5.0
            (a0, a1), (b0, b1) = ghosts[j], ghosts[j + 1]
            mk.band(c, (a0, a1, b1, b0), P["aura"] + (int(215 * fade),))
            mk.band(c, (mk.lerp(a0, a1, 0.5), a1, b1, mk.lerp(b0, b1, 0.5)), P["aura_core"] + (int(240 * fade),))
    if not c.is_melee:
        bomb = (hand_l[0], hand_l[1], hand_l[2] - 0.03)
        for w, dd, h in ((0.1, 0.075, 0.075), (0.075, 0.1, 0.075), (0.075, 0.075, 0.1)):
            mk.cbox(c, bomb[0], bomb[1], bomb[2] - h / 2, w, dd, h, P["bomb"])
        mk.cbox(c, bomb[0], bomb[1], bomb[2] + 0.045, 0.02, 0.02, 0.05, P["fuse"], outline=False)
        mk.cbox(c, bomb[0] + 0.01, bomb[1], bomb[2] + 0.095, 0.03, 0.03, 0.03, (255, 220, 120), outline=False)
