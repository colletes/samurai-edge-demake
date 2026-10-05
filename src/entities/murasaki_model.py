"""
Murasaki, a kunoichi da Kusarigama (6.5.5): coque preto com laço roxo e fitas ao vento, máscara roxa, traje justo e brilhante com
faixa roxa cruzada, ombreiras e braçadeiras de aço escuro, botas tabi roxas; foice (kama) na direita e corrente com bola
de ferro presa à esquerda, que no ataque gira em arco largo deixando um rastro roxo.
Os ganchos são chamados por `render_voxel_humanoid`; só o visual muda, não a duração do ataque nem as hitboxes.
"""
import math

from src.entities import model_kit as mk
from src.isometric import cloth

DETAILED = {
    "suit": (34, 24, 46), "suit_dark": (20, 14, 30), "wrap": (118, 58, 176), "wrap_dark": (76, 36, 118), "wrap_light": (178, 112, 238),
    "skin": (236, 196, 166), "skin_shadow": (206, 160, 132), "hair": (30, 24, 38), "hair_light": (96, 78, 122),
    "mask": (112, 56, 168), "mask_light": (160, 100, 220), "eye": (206, 156, 255), "liner": (14, 10, 20),
    "steel_dark": (62, 58, 78), "steel": (116, 114, 138), "steel_light": (214, 214, 230),
    "boot": (76, 42, 112), "sole": (38, 30, 36), "strap": (28, 20, 38),
    "chain": (176, 180, 196), "ball": (62, 60, 76), "ball_light": (150, 148, 170),
    "wood": (88, 54, 32), "blade": (226, 232, 246), "edge": (252, 254, 255),
    "aura": (200, 120, 255), "aura_core": (250, 232, 255),
}


MATERIALS = {"suit": "latex", "suit_dark": "latex", "wrap": "latex", "wrap_dark": "latex", "wrap_light": "latex", "boot": "leather", "strap": "leather", "steel_dark": "brushed_metal", "steel": "brushed_metal", "mask": "latex", "ball": "brushed_metal"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return DETAILED


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def _hand_pose(c, p=None):
    """(mão direita da foice, mão esquerda da corrente) da pose atual, antes do respiro."""
    bx, by, fx, fy, px, py, tz = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py, c.torso_z
    if p is not None:  # ataque
        if p < 0.3:
            w = _smooth(p / 0.3)
            right = (bx + fx * (0.10 - 0.18 * w) - px * 0.16, by + fy * (0.10 - 0.18 * w) - py * 0.16, tz + 0.27 + 0.14 * w)
        elif p < 0.7:
            t = (p - 0.3) / 0.4
            reach = 0.06 + 0.30 * math.sin(math.pi * t)
            lat = -0.17 + 0.34 * _smooth(t)
            right = (bx + fx * reach + px * lat, by + fy * reach + py * lat, tz + 0.41 - 0.34 * _smooth(t))
        else:
            right = (bx + fx * 0.14 + px * 0.17, by + fy * 0.14 + py * 0.17, tz + 0.07)
        left = (bx + px * 0.19 - fx * 0.05, by + py * 0.19 - fy * 0.05, tz + 0.13 - 0.05 * math.sin(math.pi * p))
        return right, left
    bob = math.sin(c.walk_timer * 2.8) * 0.015
    if c.is_moving:
        sw = math.sin(c.walk_timer * 9.0)
        right = (bx + fx * 0.11 - px * 0.16, by + fy * 0.11 - py * 0.16, tz + 0.20 + abs(sw) * 0.02)
        left = (bx + px * 0.17 + fx * sw * -0.15, by + py * 0.17 + fy * sw * -0.15, tz + 0.05 + abs(sw) * 0.02)
        return right, left
    return ((bx + fx * 0.10 - px * 0.16, by + fy * 0.10 - py * 0.16, tz + 0.28 + bob),
            (bx + fx * 0.13 + px * 0.18, by + fy * 0.13 + py * 0.18, tz - 0.01 + bob))


def idle_arms(c):
    right, left = _hand_pose(c)
    return left, right


def attack_arms(c):
    right, left = _hand_pose(c, c.atk_progress)
    return left, right


walk_arms = idle_arms


def _kama_dirs(c, arm_r):
    """(direção do cabo, lado para onde a lâmina se curva) da foice conforme a pose."""
    f, p = (c.fx, c.fy, 0.0), (c.px, c.py, 0.0)
    if c.is_melee:
        q = c.atk_progress
        if q < 0.3:
            return mk.norm((-c.fx * 0.35, -c.fy * 0.35, 0.95)), mk.norm(f)
        t = _smooth((q - 0.3) / 0.45)
        kd = mk.norm((c.fx * (-0.35 + 1.25 * t), c.fy * (-0.35 + 1.25 * t), 0.95 - 1.75 * t))
        bs = mk.norm((c.fx * (1.0 - t) + c.px * 1.1 * t, c.fy * (1.0 - t) + c.py * 1.1 * t, 0.0))
        return kd, bs
    if c.is_moving:
        return mk.norm((c.fx * 0.45 - c.px * 0.1, c.fy * 0.45 - c.py * 0.1, 0.9)), mk.norm(f)
    return mk.norm((c.fx * 0.30 - c.px * 0.08, c.fy * 0.30 - c.py * 0.08, 0.95)), mk.norm(f)


def _orbit_radius(q):
    return 0.55 + 0.30 * math.sin(math.pi * min(1.0, q))


def _ball_state(c, arm_l):
    """Posição da bola, ponto de controle da curva da corrente e a fase do giro (None fora do ataque)."""
    if c.is_melee:
        q = c.atk_progress
        theta = -2.2 + 5.0 * q
        radius = _orbit_radius(q)
        pos = (c.base_x + (math.cos(theta) * c.fx + math.sin(theta) * c.px) * radius,
               c.base_y + (math.cos(theta) * c.fy + math.sin(theta) * c.py) * radius,
               c.base_z + 0.58 + 0.10 * math.sin(theta))
        lag = theta - 0.9
        ctrl = (c.base_x + (math.cos(lag) * c.fx + math.sin(lag) * c.px) * radius * 0.6,
                c.base_y + (math.cos(lag) * c.fy + math.sin(lag) * c.py) * radius * 0.6, c.base_z + 0.55)
        return pos, ctrl, theta
    t = c.walk_timer
    sway = math.sin(t * (7.0 if c.is_moving else 1.9)) * (0.07 if c.is_moving else 0.035)
    drop = 0.30 if not c.is_moving else 0.26
    pos = (arm_l[0] + c.px * sway + c.fx * 0.02, arm_l[1] + c.py * sway + c.fy * 0.02, arm_l[2] - 0.075 - drop)
    return pos, None, None


def _curve(a, ctrl, b, count):
    if ctrl is None:
        return mk.chain_points(a, b, count, sag=0.05)
    pts = []
    for i in range(count + 1):
        t = i / count
        u = 1.0 - t
        pts.append((u * u * a[0] + 2 * u * t * ctrl[0] + t * t * b[0], u * u * a[1] + 2 * u * t * ctrl[1] + t * t * b[1],
                    u * u * a[2] + 2 * u * t * ctrl[2] + t * t * b[2]))
    return pts


# ---------------------------------------------------------------------------------------------------------------------

def _behind(c, point) -> bool:
    return mk.depth(c, point[0], point[1]) < mk.depth(c, c.base_x, c.base_y) - 0.02


def _ribbon_root(c):
    return (c.base_x - c.fx * 0.025, c.base_y - c.fy * 0.025, c.head_z + 0.205)


def _hair_volume(c):
    mk.cbox(c, c.base_x - c.fx * 0.04, c.base_y - c.fy * 0.04, c.head_z + 0.03, 0.152, 0.152, 0.14, pal()["hair"], outline=False)


def draw_behind(c):
    """Volume do cabelo, fitas e trança, quando ficam do lado oposto à câmera."""
    if mk.facing_camera(c):
        _hair_volume(c)  # atrás do rosto; de costas ele cobre a cabeça
    if _behind(c, (c.base_x - c.fx * 0.1, c.base_y - c.fy * 0.1, c.head_z)):
        _streamers(c)
        _braid(c)


def _streamers(c):
    P = pal()
    root = _ribbon_root(c)
    trail, amp, freq = mk.motion(c, 0.10)
    for k, side in enumerate((0.55, -0.9)):
        offs = cloth.chain_offsets(4, c.walk_timer, 0.8 * k, trail, (c.px, c.py), amp=amp * 2.0, freq=freq * 1.1, wind=cloth.wind_at(root[0], root[1]),
                                   wind_gain=0.07)
        prev = root
        for i, o in enumerate(offs):
            k4 = (i + 1) / 4.0
            nxt = (root[0] - c.fx * 0.075 * (i + 1) + c.px * side * 0.05 * k4 + o[0], root[1] - c.fy * 0.075 * (i + 1) + c.py * side * 0.05 * k4 + o[1],
                   root[2] + 0.02 - 0.035 * (i + 1) + o[2])
            mk.limb(c, prev, nxt, 0.034 - 0.004 * i, P["wrap"], outline=(i == 0), height=0.012)
            prev = nxt


def _braid(c):
    P = pal()
    trail, amp, freq = mk.motion(c, 0.08)
    s = 1.0
    root = (c.base_x + c.px * 0.075 * s - c.fx * 0.02, c.base_y + c.py * 0.075 * s - c.fy * 0.02, c.head_z + 0.08)
    offs = cloth.chain_offsets(3, c.walk_timer, 1.4, trail, (c.px, c.py), amp=amp * 1.6, freq=freq, wind=cloth.wind_at(root[0], root[1]))
    prev = root
    for i, o in enumerate(offs):
        nxt = (root[0] + c.px * 0.02 * (i + 1) + o[0], root[1] + c.py * 0.02 * (i + 1) + o[1], root[2] - 0.06 * (i + 1) + o[2])
        mk.limb(c, prev, nxt, 0.036 - 0.005 * i, P["hair"], outline=False)
        prev = nxt
    mk.cbox(c, prev[0], prev[1], prev[2] - 0.045, 0.034, 0.034, 0.05, P["wrap"], outline=False)  # fita da ponta


def draw_legs(c):
    """Calça justa e brilhante, bota tabi roxa com tiras no tornozelo e geta."""
    P = pal()
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]
        top = (th[0], th[1], th[2] + 0.215)
        knee = (sh[0], sh[1], sh[2] + 0.205)
        ankle = (ft[0], ft[1], ft[2] + 0.10)
        mk.obox(c, (ft[0] - c.fx * 0.05, ft[1] - c.fy * 0.05, ft[2]), (c.fx, c.fy, 0.0), 0.13, 0.072, 0.02, P["sole"])
        mk.obox(c, (ft[0] - c.fx * 0.03, ft[1] - c.fy * 0.03, ft[2] + 0.02), (c.fx, c.fy, 0.0), 0.10, 0.062, 0.04, P["boot"])
        mk.limb(c, top, mk.add(knee, (0, 0, 0.02)), 0.116, P["suit"])
        mk.limb(c, mk.add(knee, (0, 0, 0.03)), mk.lerp(knee, ankle, 0.5), 0.1, P["suit"])
        mk.limb(c, mk.lerp(knee, ankle, 0.45), ankle, 0.1, P["boot"])  # cano da bota
        for t in (0.25, 0.7):
            q = mk.lerp(mk.lerp(knee, ankle, 0.45), ankle, t)
            mk.limb(c, q, mk.add(q, (0, 0, -0.016)), 0.108, P["strap"], outline=False)


def draw_obi(c):
    """Nó da faixa nas costas com duas pontas que balançam."""
    P = pal()
    kx, ky = c.base_x - c.fx * 0.115, c.base_y - c.fy * 0.115
    z = c.pelvis_z + 0.09
    mk.cbox(c, kx, ky, z, 0.07, 0.05, 0.075, P["wrap_dark"])
    for s in (-1.0, 1.0):
        mk.obox(c, (kx, ky, z + 0.035), (c.px * s, c.py * s, 0.3), 0.07, 0.03, 0.05, P["wrap"])
    trail, amp, freq = mk.motion(c, 0.06)
    for k, s in enumerate((-1.0, 1.0)):
        offs = cloth.chain_offsets(2, c.walk_timer, 0.9 * k, trail, (c.px, c.py), amp=amp * 1.3, freq=freq, wind=cloth.wind_at(kx, ky))
        for i, o in enumerate(offs):
            mk.cbox(c, kx - c.fx * 0.02 * (i + 1) + c.px * 0.025 * s + o[0], ky - c.fy * 0.02 * (i + 1) + c.py * 0.025 * s + o[1], z - 0.065 * (i + 1) + o[2],
                    0.034, 0.024, 0.07, P["wrap"] if i == 0 else P["wrap_dark"], outline=False)


def draw_torso(c):
    """Faixa roxa cruzada na barriga, gola em V com debrum roxo e brilho do traje."""
    P = pal()
    tz = c.torso_z
    front = 0.085
    mk.cbox(c, c.base_x, c.base_y, tz - 0.005, 0.215, 0.165, 0.125, P["wrap"], texture="gloss")
    for s in (-1.0, 1.0):  # faixas cruzando o abdômen
        a = (c.base_x + c.fx * (front + 0.006) + c.px * 0.085 * s, c.base_y + c.fy * (front + 0.006) + c.py * 0.085 * s, tz + 0.115)
        b = (c.base_x + c.fx * (front + 0.006) - c.px * 0.07 * s, c.base_y + c.fy * (front + 0.006) - c.py * 0.07 * s, tz + 0.01)
        mk.limb(c, a, b, 0.032, P["wrap_dark"], outline=False, height=0.018)
    apex = (c.base_x + c.fx * (front + 0.012), c.base_y + c.fy * (front + 0.012), tz + 0.14)
    for s in (-1.0, 1.0):
        top = (c.base_x + c.fx * (front + 0.006) + c.px * 0.06 * s, c.base_y + c.fy * (front + 0.006) + c.py * 0.06 * s, tz + 0.255)
        mk.limb(c, top, apex, 0.03, P["wrap"], outline=False, height=0.02)
    mk.cbox(c, c.base_x + c.fx * (front + 0.004), c.base_y + c.fy * (front + 0.004), tz + 0.175, 0.045, 0.016, 0.075, P["skin"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço nu com ombreira de aço escuro e braçadeira preta com aro de prata; o braço acompanha a mão."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.205)
    h = (hand[0], hand[1], hand[2] - 0.065)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.025), (0.0, 0.0, -0.03))
    mk.limb(c, s, e, 0.056, P["skin"])
    wrist = mk.lerp(e, h, 0.86)
    mk.limb(c, e, wrist, 0.07, P["suit_dark"])
    mk.limb(c, mk.lerp(e, h, 0.12), mk.lerp(e, h, 0.3), 0.078, P["steel"], outline=False)
    mk.limb(c, mk.lerp(e, h, 0.78), wrist, 0.08, P["steel"], outline=False)
    mk.cbox(c, h[0], h[1], h[2] - 0.026, 0.052, 0.052, 0.052, P["skin"])
    return s, e


def draw_sleeves(c, arms):
    """Ombreiras: base de aço escuro, placa superior com aro prateado e uma gema roxa."""
    P = pal()
    for s, e, side in arms:
        z = s[2] + 0.035
        ox, oy = s[0] + c.px * side * 0.018, s[1] + c.py * side * 0.018
        mk.cbox(c, ox, oy, z - 0.05, 0.11, 0.105, 0.05, P["steel_dark"])
        mk.cbox(c, ox, oy, z - 0.01, 0.096, 0.092, 0.036, P["steel_dark"])
        mk.cbox(c, ox, oy, z + 0.024, 0.108, 0.1, 0.012, P["steel"], outline=False)
        mk.cbox(c, ox + c.fx * 0.04, oy + c.fy * 0.04, z - 0.008, 0.026, 0.026, 0.026, P["wrap_light"], outline=False)


def draw_head(c):
    """Máscara roxa, olhos violeta com delineador, cabelo preto com coque, laço, fitas e trança."""
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    if mk.facing_camera(c):
        mk.obox(c, (bx - fx * 0.01, by - fy * 0.01, hz + 0.028), (fx, fy, 0.0), hw / 2 + 0.017, hw + 0.016, 0.078, P["mask"])
        mk.obox(c, (bx - fx * 0.01, by - fy * 0.01, hz + 0.092), (fx, fy, 0.0), hw / 2 + 0.017, hw + 0.016, 0.012, P["mask_light"], outline=False)
        front = hw / 2 + 0.004
        for s in (-1.0, 1.0):
            ex, ey = bx + fx * front + px * 0.034 * s, by + fy * front + py * 0.034 * s
            mk.cbox(c, ex, ey, hz + 0.104, 0.03, 0.02, 0.024, P["eye"], outline=False)
            mk.cbox(c, ex, ey, hz + 0.109, 0.012, 0.014, 0.014, P["liner"], outline=False)
            mk.limb(c, (ex - px * 0.02 * s, ey - py * 0.02 * s, hz + 0.13), (ex + px * 0.022 * s, ey + py * 0.022 * s, hz + 0.142), 0.01, P["liner"], outline=False, height=0.01)
    mk.cbox(c, bx, by, hz + 0.145, 0.15, 0.15, 0.06, P["hair"])
    if not mk.facing_camera(c):
        _hair_volume(c)
    for s in (-1.0, 1.0):  # franja repartida e mechas
        mk.limb(c, (bx + fx * 0.07, by + fy * 0.07, hz + 0.205), (bx + fx * 0.07 + px * 0.066 * s, by + fy * 0.07 + py * 0.066 * s, hz + 0.158), 0.03, P["hair"], outline=False, height=0.03)
        mk.cbox(c, bx + px * 0.082 * s, by + py * 0.082 * s, hz + 0.045, 0.03, 0.036, 0.12, P["hair"], outline=False)
    root = _ribbon_root(c)
    mk.cbox(c, bx - fx * 0.01, by - fy * 0.01, hz + 0.2, 0.076, 0.076, 0.062, P["hair"])  # coque
    mk.cbox(c, bx - fx * 0.01, by - fy * 0.01, hz + 0.24, 0.04, 0.04, 0.016, P["hair_light"], outline=False)
    mk.cbox(c, bx - fx * 0.01, by - fy * 0.01, hz + 0.196, 0.09, 0.09, 0.02, P["wrap"])  # laço na base do coque
    if not _behind(c, (bx - fx * 0.1, by - fy * 0.1, hz)):
        _braid(c)
        _streamers(c)
    mk.cbox(c, root[0], root[1], root[2] - 0.012, 0.04, 0.04, 0.034, P["wrap_dark"], outline=False)


def draw_front(c, arm_l, arm_r):
    """Foice, corrente e bola; no ataque a bola gira em arco largo com rastro roxo."""
    P = pal()
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    kd, bs = _kama_dirs(c, arm_r)
    pommel = mk.add(hand_r, kd, -0.075)
    ball, ctrl, theta = _ball_state(c, arm_l)
    if theta is not None:
        _ball_trail(c, theta)
    first = mk.chain_points(pommel, hand_l, 5, sag=0.07)
    second = _curve(hand_l, ctrl, ball, 6)
    for pts in (first, second):
        for i in range(len(pts) - 1):
            mk.limb(c, pts[i], pts[i + 1], 0.024, P["chain"] if i % 2 else P["steel"], outline=False)
    mk.limb(c, mk.add(hand_l, (0, 0, 1), 0.045), mk.add(hand_l, (0, 0, -1), 0.045), 0.034, P["steel_dark"])  # cabo da corrente na esquerda
    _ball(c, ball)
    _kama(c, hand_r, kd, bs)


def _kama(c, hand, kd, bs):
    P = pal()
    mk.limb(c, mk.add(hand, kd, -0.075), mk.add(hand, kd, 0.27), 0.046, P["wood"])
    mk.limb(c, mk.add(hand, kd, -0.085), mk.add(hand, kd, -0.06), 0.056, P["steel_dark"], outline=False)
    mk.limb(c, mk.add(hand, kd, 0.245), mk.add(hand, kd, 0.30), 0.058, P["steel_dark"])
    top = mk.add(hand, kd, 0.29)
    prev = top
    segments = ((mk.norm(mk.add(bs, kd, 0.25)), 0.17, 0.062), (mk.norm(mk.add(mk.add((0, 0, 0), bs, 0.65), kd, -0.65)), 0.13, 0.054),
                (mk.norm(mk.add(mk.add((0, 0, 0), bs, 0.2), kd, -1.0)), 0.095, 0.046))
    for d, length, height in segments:
        mk.obox(c, prev, d, length, 0.018, height, P["blade"], up=kd)
        mk.obox(c, prev, d, length, 0.02, 0.012, P["edge"], up=kd, outline=False)
        prev = mk.add(prev, d, length)


def _ball(c, pos):
    P = pal()
    for w, d, h in ((0.118, 0.085, 0.085), (0.085, 0.118, 0.085), (0.085, 0.085, 0.118)):
        mk.cbox(c, pos[0], pos[1], pos[2] - h / 2, w, d, h, P["ball"])
    mk.cbox(c, pos[0] - 0.012, pos[1] - 0.012, pos[2] + 0.02, 0.03, 0.03, 0.03, P["ball_light"], outline=False)


def _ball_trail(c, theta):
    P = pal()
    q = c.atk_progress
    pts = []
    for j in range(9):
        th = theta - 0.22 * j
        qj = q - 0.044 * j
        if qj < 0.0:
            break
        r = _orbit_radius(qj)
        pts.append((c.base_x + (math.cos(th) * c.fx + math.sin(th) * c.px) * r, c.base_y + (math.cos(th) * c.fy + math.sin(th) * c.py) * r,
                    c.base_z + 0.58 + 0.10 * math.sin(th)))
    for j in range(len(pts) - 1):
        fade = 1.0 - j / 9.0
        a, b = pts[j], pts[j + 1]
        mk.band(c, ((a[0], a[1], a[2] + 0.07), (b[0], b[1], b[2] + 0.07), (b[0], b[1], b[2] - 0.07), (a[0], a[1], a[2] - 0.07)), P["aura"] + (int(170 * fade),))
        mk.band(c, ((a[0], a[1], a[2] + 0.025), (b[0], b[1], b[2] + 0.025), (b[0], b[1], b[2] - 0.025), (a[0], a[1], a[2] - 0.025)), P["aura_core"] + (int(210 * fade),))
