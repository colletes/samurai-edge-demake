"""
Julie, a mosqueteira (6.5.5): chapéu azul de aba larga com pluma branca longa, cabelo ruivo com trança sobre o ombro, gola de
renda, túnica azul-real com botões dourados e mangas bufantes com punhos de renda, bandoleira de couro com flor-de-lis, luvas
brancas, calça cinza em botas marrons altas de cano dobrado, capa azul que esvoaça (e gira no CAPE_FLOURISH) e o florete de
guarda em concha.
Só o visual muda: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk
from src.isometric.voxel_rig import calc_blade_slash_3d

PALETTE = {
    "torso": (30, 70, 164), "pants": (150, 152, 162), "hair": (176, 62, 42), "belt": (112, 72, 42),
    "skin": (244, 214, 190), "skin_shadow": (212, 176, 152),
    "blue": (30, 70, 164), "blue_dark": (20, 48, 124), "cape": (34, 74, 172), "cape_dark": (22, 52, 130), "gold": (232, 190, 70), "lace": (246, 244, 238), "lace_dark": (214, 212, 208),
    "leather": (112, 72, 42), "boot": (96, 58, 30), "boot_cuff": (140, 92, 52), "glove": (246, 244, 238), "hat": (28, 66, 156), "plume": (248, 246, 240), "plume_dark": (214, 212, 214),
    "eye": (52, 96, 120), "brow": (130, 50, 36), "lip": (196, 84, 90), "steel": (196, 214, 250), "edge": (252, 254, 255), "grip": (60, 40, 28),
    "aura": (150, 190, 255), "aura_core": (240, 248, 255),
}


MATERIALS = {"cape": "velvet", "cape_dark": "velvet", "blue": "brocade", "blue_dark": "velvet", "leather": "leather", "boot": "leather", "boot_cuff": "leather", "lace": "knit", "lace_dark": "knit", "glove": "silk", "hat": "velvet", "pants": "silk"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return PALETTE


def _flourishing(c) -> bool:
    return c.state == "CAPE_FLOURISH"


def _cape(c):
    """Capa pendurada nas costas, com bordado dourado; balança e é empurrada pelo vento."""
    P = pal()
    anchor = (c.base_x - c.fx * 0.1, c.base_y - c.fy * 0.1, c.torso_z + 0.24)
    last = mk.panels(c, anchor, 5, 0.13, 0.26, 0.026, (P["cape"], P["cape"], P["cape"], P["cape_dark"], P["cape_dark"]), phase=0.4, up=(c.fx, c.fy, 0.0),
                     drag=(-c.fx * 0.05, -c.fy * 0.05), flare=0.016)
    for i in range(3):
        mk.cbox(c, last[0] + c.px * (i - 1) * 0.07, last[1] + c.py * (i - 1) * 0.07, last[2] - 0.01, 0.034, 0.03, 0.03, P["gold"], outline=False)


def draw_behind(c):
    if mk.facing_camera(c):
        mk.hair_volume(c, pal()["hair"], size=0.15, height=0.13)
        if not _flourishing(c):
            _cape(c)


def draw_legs(c):
    """Calça cinza justa em botas marrons altas com o cano dobrado."""
    P = pal()
    mk.legs(c, P["pants"], boot=P["boot"], boot_h=0.24, tight_w=(0.108, 0.092), foot_color=P["boot"], foot_len=0.15, foot_w=0.07, sole=(40, 26, 16), cuff=P["boot_cuff"])


def draw_obi(c):
    """Cinto de couro com fivela dourada e a bainha do florete no quadril esquerdo."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z
    mk.cbox(c, bx, by, z + 0.065, c.pelvis_w - 0.008, c.pelvis_w * 0.8, 0.06, P["leather"])
    mk.cbox(c, bx + fx * 0.088, by + fy * 0.088, z + 0.068, 0.05, 0.02, 0.05, P["gold"], outline=False)
    k = (bx + px * 0.13, by + py * 0.13, z + 0.06)
    d = mk.norm((-fx * 0.75 + px * 0.2, -fy * 0.75 + py * 0.2, -0.55))
    mk.obox(c, k, d, 0.5, 0.034, 0.034, P["leather"])
    mk.obox(c, mk.add(k, d, 0.47), d, 0.04, 0.04, 0.04, P["gold"], outline=False)


def draw_torso(c):
    """Gola de renda, botões dourados, bandoleira de couro com flor-de-lis e a capa quando está nas costas."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.085 + 0.006
    for i in range(3):
        mk.cbox(c, bx + fx * front, by + fy * front, tz + 0.02 + i * 0.055, 0.022, 0.012, 0.022, P["gold"], outline=False)
    a = (bx - px * 0.1 + fx * (front + 0.004), by - py * 0.1 + fy * (front + 0.004), tz + 0.26)
    b = (bx + px * 0.1 + fx * (front + 0.004), by + py * 0.1 + fy * (front + 0.004), tz + 0.0)
    mk.limb(c, a, b, 0.036, P["leather"], outline=False, height=0.018)
    mk.cbox(c, bx + fx * (front + 0.008), by + fy * (front + 0.008), tz + 0.115, 0.04, 0.014, 0.04, P["gold"], outline=False)
    nz = c.neck_z
    mk.cbox(c, bx, by, nz - 0.03, 0.15, 0.14, 0.04, P["lace"])
    for k in range(6):  # pontas da renda
        ang = k * math.pi / 3.0
        mk.cbox(c, bx + math.cos(ang) * 0.075 - 0.012, by + math.sin(ang) * 0.07 - 0.012, nz - 0.055, 0.024, 0.024, 0.03, P["lace"], outline=False)
    if not mk.facing_camera(c) and not _flourishing(c):
        _cape(c)


def draw_arm(c, shoulder, hand, side):
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], sleeve=P["blue"], sleeve_to=1.1, glove=P["glove"], bracer=P["lace"], bracer_span=(0.72, 0.97), w=0.052)


def draw_sleeves(c, arms):
    """Mangas bufantes: ombro volumoso com talhos dourados e punho de renda."""
    P = pal()
    for s, e, side in arms:
        ox, oy = c.px * side * 0.02, c.py * side * 0.02
        mk.cbox(c, s[0] + ox, s[1] + oy, s[2] - 0.075, 0.1, 0.1, 0.11, P["blue"])
        for k in (-1.0, 1.0):
            mk.limb(c, (s[0] + ox + c.fx * 0.05 * k, s[1] + oy + c.fy * 0.05 * k, s[2] + 0.03), (s[0] + ox + c.fx * 0.05 * k, s[1] + oy + c.fy * 0.05 * k, s[2] - 0.07), 0.01, P["gold"], outline=False)
        mk.cbox(c, e[0], e[1], e[2] - 0.02, 0.08, 0.08, 0.06, P["blue_dark"], outline=False)


def draw_head(c):
    """Rosto de olhos azul-acinzentados, cabelo ruivo com trança, chapéu azul de aba larga e a pluma branca que esvoaça."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    mk.face(c, P["eye"], P["brow"], P["lip"], P["skin_shadow"], brow_tilt=0.004, spacing=0.032, mouth_w=0.024)
    mk.cbox(c, bx, by, hz + 0.115, 0.16, 0.16, 0.075, P["hair"])
    if not mk.facing_camera(c):
        mk.hair_volume(c, P["hair"], size=0.15, height=0.13)
    trail, amp, freq = mk.motion(c, 0.08)
    for s in (-1.0, 1.0):
        mk.limb(c, (bx + fx * 0.07, by + fy * 0.07, hz + 0.17), (bx + fx * 0.075 + px * 0.065 * s, by + fy * 0.075 + py * 0.065 * s, hz + 0.115), 0.03, P["hair"], outline=False)
    anchor = (bx + px * 0.075 + fx * 0.02, by + py * 0.075 + fy * 0.02, hz + 0.06)  # trança sobre o ombro
    mk.panels(c, anchor, 5, 0.07, 0.05, 0.045, (P["hair"],) * 5, phase=1.1, up=(fx, fy, 0.0), trail=trail, amp=amp, freq=freq, flare=-0.004)
    mk.cbox(c, bx, by, hz + 0.18, 0.186, 0.186, 0.03, P["gold"], outline=False)
    mk.cbox(c, bx, by, hz + 0.18, 0.17, 0.17, 0.08, P["hat"])
    mk.cbox(c, bx, by, hz + 0.168, 0.35, 0.35, 0.022, P["hat"])
    mk.cbox(c, bx - px * 0.16, by - py * 0.16, hz + 0.178, 0.1, 0.1, 0.05, P["hat"], outline=False)  # aba dobrada para cima
    root = (bx - px * 0.09, by - py * 0.09, hz + 0.26)
    offs = mk.cloth_offsets(c, 4, 0.5, trail, amp * 2.0, freq, root, wind_gain=0.08)
    prev = root
    for i, o in enumerate(offs):
        tip = (root[0] - px * 0.03 * (i + 1) - fx * 0.05 * (i + 1) + o[0], root[1] - py * 0.03 * (i + 1) - fy * 0.05 * (i + 1) + o[1], root[2] + 0.05 - 0.035 * i + o[2])
        mk.limb(c, prev, tip, 0.05 - 0.008 * i, P["plume"] if i % 2 == 0 else P["plume_dark"], outline=(i == 0), height=0.014)
        prev = tip


def _rapier(c, hand, d, length):
    P = pal()
    mk.obox(c, mk.add(hand, d, -0.1), d, 0.12, 0.034, 0.034, P["grip"])
    mk.obox(c, mk.add(hand, d, -0.11), d, 0.02, 0.046, 0.046, P["gold"], outline=False)
    mk.cbox(c, hand[0] + d[0] * 0.04 - 0.045, hand[1] + d[1] * 0.04 - 0.045, hand[2] + d[2] * 0.04 - 0.03, 0.09, 0.09, 0.06, P["gold"])  # guarda em concha
    mk.obox(c, mk.add(hand, d, 0.04), d, length, 0.028, 0.026, P["steel"])
    mk.obox(c, mk.add(hand, d, 0.05), d, length - 0.02, 0.012, 0.028, P["edge"], outline=False)
    return mk.add(hand, d, 0.04 + length)


def draw_front(c, arm_l, arm_r):
    """Florete (en garde, baixo na caminhada, estocada no fleche) e a capa girando no CAPE_FLOURISH com o chute."""
    P = pal()
    hand = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    if _flourishing(c):
        t = max(0.0, min(1.0, 1.0 - c.state_timer / 0.16))
        a = t * math.pi * 2.2
        cf = (c.fx * math.cos(a) + c.px * math.sin(a), c.fy * math.cos(a) + c.py * math.sin(a))
        mk.obox(c, (c.base_x + cf[0] * 0.2, c.base_y + cf[1] * 0.2, c.torso_z + 0.06), (cf[0], cf[1], -0.15), 0.5, 0.22, 0.04, P["cape"], up=(0.0, 0.0, 1.0))
        mk.obox(c, (c.base_x + cf[0] * 0.2, c.base_y + cf[1] * 0.2, c.torso_z + 0.06), (cf[0], cf[1], -0.15), 0.5, 0.22, 0.012, P["gold"], up=(0.0, 0.0, 1.0), outline=False)
        kick = c.pelvis_z - 0.12
        mk.obox(c, (c.base_x + c.fx * 0.18, c.base_y + c.fy * 0.18, kick), (c.fx, c.fy, 0.1), 0.38, 0.08, 0.08, P["pants"])
        mk.obox(c, (c.base_x + c.fx * 0.36, c.base_y + c.fy * 0.36, kick + 0.02), (c.fx, c.fy, 0.1), 0.14, 0.09, 0.09, P["boot"])
    if c.is_melee:
        info = calc_blade_slash_3d("musketeer", "ATTACK", c.atk_progress, c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py)
        d, length = mk.norm(tuple(info["dir"])), 0.78
        tip = _rapier(c, hand, d, length)
        if c.atk_progress >= 0.25:
            for j in range(1, 4):
                back = mk.add(hand, d, -0.12 * j)
                fade = 1.0 - j / 4.0
                side = (c.px * 0.04, c.py * 0.04, 0.0)
                a0, a1 = mk.add(back, d, 0.35), mk.add(back, d, length + 0.1)
                mk.band(c, (a0, a1, mk.add(a1, side, 1.0), mk.add(a0, side, 1.0)), P["aura"] + (int(190 * fade),))
        return
    if c.is_moving:
        d = mk.norm((c.fx * 0.3, c.fy * 0.3, -0.75))
    else:
        d = mk.norm((c.fx * 0.82 + c.px * 0.1, c.fy * 0.82 + c.py * 0.1, 0.08))
    _rapier(c, hand, d, 0.72 if not c.is_moving else 0.68)
