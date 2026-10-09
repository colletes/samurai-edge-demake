"""
Musashi, o espadachim de duas lâminas (6.5.5): topknot desgrenhado, rosto marcado com barba por fazer, quimono índigo desbotado
de mangas largas até o cotovelo, tasuki bege com laço no ombro, antebraços com bandagem, hakama larga, escura e pregueada, faixa
azul-arroxeada, tabi com sandália de palha e corda. Duas espadas: katana na direita (tsuba grande, ito preto) e wakizashi
na esquerda; as bainhas vazias ficam na cintura esquerda e, na caminhada, as lâminas voltam para elas.
Os ganchos são chamados por `render_voxel_humanoid`. Só o visual muda: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.voxel_rig import calc_blade_slash_3d

PALETTE = {
    "kimono": (64, 94, 144), "kimono_dark": (44, 66, 106), "kimono_light": (92, 124, 176), "collar": (224, 208, 172),
    "tasuki": (198, 160, 100), "wrap": (216, 202, 170),
    "hakama": (78, 68, 62), "hakama_dark": (46, 40, 38), "sash": (58, 56, 118), "knot": (36, 32, 36),
    "skin": (216, 168, 130), "skin_shadow": (176, 130, 98), "stubble": (120, 90, 72),
    "hair": (38, 32, 32), "hair_light": (88, 72, 64), "eye": (34, 24, 20), "brow": (28, 22, 22), "scar": (190, 120, 104),
    "tabi": (32, 30, 36), "straw": (182, 150, 94), "rope": (122, 92, 52),
    "saya": (116, 68, 36), "saya_tip": (176, 140, 70), "saya_short": (36, 44, 70),
    "ito": (30, 26, 28), "tsuba": (158, 156, 168), "gold": (210, 176, 84),
    "steel": (214, 224, 238), "edge": (250, 253, 255),
    "trail": (116, 172, 255), "trail_core": (232, 246, 255),
}


MATERIALS = {"kimono": "canvas", "kimono_dark": "canvas", "kimono_light": "canvas", "sash": "silk", "wrap": "canvas", "tabi": "canvas", "straw": "canvas", "tasuki": "canvas", "collar": "canvas", "saya": "lacquer", "saya_short": "lacquer", "steel": "steel", "edge": "steel", "tsuba": "metal", "gold": "gold"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


# ---------------------------------------------------------------------------------------------------------------------
# Poses
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """Neutra: katana adiante na direita (chūdan) e wakizashi baixa e invertida na esquerda."""
    tz = c.torso_z + math.sin(c.walk_timer * 2.8) * 0.015
    right = (c.base_x + c.fx * 0.20 - c.px * 0.08, c.base_y + c.fy * 0.20 - c.py * 0.08, tz + 0.12)
    left = (c.base_x + c.fx * 0.08 + c.px * 0.12, c.base_y + c.fy * 0.08 + c.py * 0.12, tz + 0.02)
    return left, right


def _step(c):
    return c.extra_props.get("combo_step", 1) if c.extra_props else 1


def _hands_at(c, p, step):
    """(esquerda, direita) no progresso `p` do golpe: corte 1 de cima na katana, corte 2 de baixo na wakizashi, corte 3 cruzado."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    if step == 1:
        right = (bx + fx * (0.16 + p * 0.30) - px * 0.06, by + fy * (0.16 + p * 0.30) - py * 0.06, tz + 0.40 - p * 0.36)
        left = (bx + px * 0.15 - fx * 0.05, by + py * 0.15 - fy * 0.05, tz + 0.10)
    elif step == 2:
        left = (bx + fx * (0.16 + p * 0.28) + px * 0.06, by + fy * (0.16 + p * 0.28) + py * 0.06, tz + 0.04 + p * 0.34)
        right = (bx - px * 0.15 - fx * 0.08, by - py * 0.15 - fy * 0.08, tz + 0.20)
    else:
        cross = math.sin(p * math.pi)
        lat = 0.20 - p * 0.35
        right = (bx + fx * (0.22 + cross * 0.22) - px * lat, by + fy * (0.22 + cross * 0.22) - py * lat, tz + 0.18)
        left = (bx + fx * (0.22 + cross * 0.22) + px * lat, by + fy * (0.22 + cross * 0.22) + py * lat, tz + 0.18)
    return left, right


def attack_arms(c):
    return _hands_at(c, c.atk_progress, _step(c))


def _blade_dirs(c, p, step):
    """(direção da katana, comprimento, direção da wakizashi, comprimento) no progresso `p`."""
    f, side = (c.fx, c.fy, 0.0), (c.px, c.py, 0.0)
    info = calc_blade_slash_3d("musashi", "ATTACK", p, c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py, {"combo_step": step})
    swing = tuple(info["dir"])
    guard_k = mk.norm((c.fx * 0.60 - c.px * 0.10, c.fy * 0.60 - c.py * 0.10, -0.30))
    guard_w = mk.norm((c.fx * 0.50 + c.px * 0.10, c.fy * 0.50 + c.py * 0.10, -0.20))
    if step == 1:
        return swing, info["length"], guard_w, 0.48
    if step == 2:
        return guard_k, 0.66, swing, info["length"]
    return (mk.norm((c.fx * 0.70 + c.px * 0.28, c.fy * 0.70 + c.py * 0.28, 0.12)), 0.66,
            mk.norm((c.fx * 0.70 - c.px * 0.28, c.fy * 0.70 - c.py * 0.28, 0.12)), 0.50)


def _drawn_dirs(c):
    return (mk.norm((c.fx * 0.80 - c.px * 0.25, c.fy * 0.80 - c.py * 0.25, 0.12)), 0.68,
            mk.norm((c.fx * 0.45 + c.px * 0.40, c.fy * 0.45 + c.py * 0.40, -0.28)), 0.48)


# ---------------------------------------------------------------------------------------------------------------------
# Camada de trás
# ---------------------------------------------------------------------------------------------------------------------

def _scabbards(c):
    """Katana (marrom, longa) e wakizashi (azul-escura, curta) na cintura esquerda: ponto da boca e direção."""
    k = (c.base_x + c.px * 0.15 + c.fx * 0.02, c.base_y + c.py * 0.15 + c.fy * 0.02, c.pelvis_z + 0.06)
    b1 = mk.norm((-c.fx * 0.78 + c.px * 0.40, -c.fy * 0.78 + c.py * 0.40, -0.34))
    k2 = (k[0] + c.fx * 0.025, k[1] + c.fy * 0.025, k[2] + 0.05)
    b2 = mk.norm((-c.fx * 0.60 + c.px * 0.62, -c.fy * 0.60 + c.py * 0.62, -0.26))
    return (k, b1), (k2, b2)


def _behind(c, point) -> bool:
    return mk.depth(c, point[0], point[1]) < mk.depth(c, c.base_x, c.base_y) - 0.02


def _sheaths(c):
    P = pal()
    (k, b1), (k2, b2) = _scabbards(c)
    mk.obox(c, k2, b2, 0.36, 0.04, 0.04, P["saya_short"])
    mk.obox(c, mk.add(k2, b2, 0.33), b2, 0.03, 0.044, 0.044, P["gold"], outline=False)
    mk.obox(c, k, b1, 0.52, 0.046, 0.046, P["saya"])
    mk.obox(c, k, b1, 0.03, 0.054, 0.054, P["gold"], outline=False)
    mk.obox(c, mk.add(k, b1, 0.49), b1, 0.035, 0.05, 0.05, P["saya_tip"], outline=False)
    offs = cloth.chain_offsets(2, c.walk_timer, 1.3, mk.motion(c, 0.05)[0], (c.px, c.py), amp=0.02, freq=2.2)
    for i, o in enumerate(offs):  # sageo azul
        a = mk.add(k, b1, 0.06 + 0.04 * i)
        mk.cbox(c, a[0] + o[0], a[1] + o[1], a[2] - 0.05 - 0.04 * i, 0.016, 0.016, 0.05, P["sash"], outline=False)


def _hair_volume(c):
    mk.cbox(c, c.base_x - c.fx * 0.04, c.base_y - c.fy * 0.04, c.head_z + 0.03, 0.162, 0.162, 0.13, pal()["hair"], outline=False)


def draw_behind(c):
    if mk.facing_camera(c):
        _hair_volume(c)
    (k, b1), _ = _scabbards(c)
    if _behind(c, mk.add(k, b1, 0.25)):
        _sheaths(c)


# ---------------------------------------------------------------------------------------------------------------------
# Corpo
# ---------------------------------------------------------------------------------------------------------------------

def draw_legs(c):
    """Hakama larga e pregueada com a barra puída, tabi preto e sandália de palha atada com corda."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.05)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]
        sign = 1.0 if side == "L" else -1.0
        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.9 * sign, trail, (c.px, c.py), amp=amp * 0.8, freq=freq, wind=cloth.wind_at(ft[0], ft[1]))
        mk.obox(c, (ft[0] - c.fx * 0.05, ft[1] - c.fy * 0.05, ft[2]), (c.fx, c.fy, 0.0), 0.15, 0.085, 0.028, P["straw"])
        mk.obox(c, (ft[0] - c.fx * 0.025, ft[1] - c.fy * 0.025, ft[2] + 0.028), (c.fx, c.fy, 0.0), 0.11, 0.07, 0.034, P["tabi"])
        mk.obox(c, (ft[0] + c.fx * 0.01, ft[1] + c.fy * 0.01, ft[2] + 0.03), (c.fx, c.fy, 0.0), 0.02, 0.074, 0.036, P["rope"], outline=False)
        mk.cbox(c, th[0], th[1], th[2], 0.15, 0.15, 0.22, P["hakama"], texture="pleats")
        mk.cbox(c, sh[0] + o1[0], sh[1] + o1[1], sh[2] + 0.1, 0.157, 0.157, 0.12, P["hakama"], texture="pleats")
        mk.cbox(c, sh[0] + o2[0], sh[1] + o2[1], sh[2] + 0.016, 0.17, 0.17, 0.086, P["hakama"], texture="pleats")
        mk.cbox(c, sh[0] + o2[0], sh[1] + o2[1], sh[2] + 0.002, 0.176, 0.176, 0.016, P["hakama_dark"], outline=False)


def draw_obi(c):
    """Faixa azul-arroxeada larga com nó escuro na frente e a ponta pendurada; placa lombar nas costas."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07
    mk.cbox(c, bx - fx * 0.12, by - fy * 0.12, c.pelvis_z + 0.03, 0.12, 0.07, 0.16, P["hakama_dark"])
    kx, ky = bx + fx * 0.115, by + fy * 0.115
    mk.cbox(c, kx, ky, z + 0.005, 0.07, 0.045, 0.07, P["knot"])
    trail, amp, freq = mk.motion(c, 0.05)
    offs = cloth.chain_offsets(3, c.walk_timer, 0.7, trail, (px, py), amp=amp * 1.4, freq=freq, wind=cloth.wind_at(kx, ky))
    for i, o in enumerate(offs):
        mk.cbox(c, kx - px * 0.02 + o[0], ky + o[1], z - 0.012 - 0.07 * (i + 1) + o[2], 0.034, 0.024, 0.075, P["sash"])


def _strap(c, a, b):
    mk.limb(c, a, b, 0.032, pal()["tasuki"], outline=False, height=0.018)


def draw_torso(c):
    """Colarinho bege em V, tasuki cruzando peito e costas com o laço no ombro direito."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    chest_d = 0.22
    front, back = chest_d / 2 + 0.006, -(chest_d / 2 + 0.006)
    apex = (bx + fx * front, by + fy * front, tz + 0.10)
    for s in (-1.0, 1.0):
        top = (bx + fx * (front - 0.004) + px * 0.07 * s, by + fy * (front - 0.004) + py * 0.07 * s, tz + 0.265)
        mk.limb(c, top, apex, 0.036, P["collar"], outline=False, height=0.018)
        _strap(c, (bx + fx * front + px * 0.10 * s, by + fy * front + py * 0.10 * s, tz + 0.26), (bx + fx * front + px * 0.12 * s, by + fy * front + py * 0.12 * s, tz + 0.02))
        _strap(c, (bx + fx * back + px * 0.10 * s, by + fy * back + py * 0.10 * s, tz + 0.26), (bx + fx * back - px * 0.10 * s, by + fy * back - py * 0.10 * s, tz + 0.04))
    mk.cbox(c, bx + fx * (front - 0.003), by + fy * (front - 0.003), tz + 0.19, 0.06, 0.02, 0.07, P["skin"], outline=False)
    bow = (bx + fx * (front - 0.01) - px * 0.105, by + fy * (front - 0.01) - py * 0.105, tz + 0.245)  # laço do tasuki no ombro direito
    mk.cbox(c, bow[0], bow[1], bow[2] - 0.015, 0.04, 0.03, 0.04, P["tasuki"])
    trail, amp, freq = mk.motion(c, 0.06)
    for k, s in enumerate((-1.0, 1.0)):
        offs = cloth.chain_offsets(2, c.walk_timer, 0.9 * k, trail, (px, py), amp=amp * 1.4, freq=freq, wind=cloth.wind_at(bow[0], bow[1]))
        for i, o in enumerate(offs):
            mk.cbox(c, bow[0] + px * 0.026 * s + o[0], bow[1] + py * 0.026 * s + o[1], bow[2] - 0.05 - 0.05 * i + o[2], 0.024, 0.02, 0.055, P["tasuki"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço musculoso com cicatriz e bandagem no pulso; as mangas largas cobrem a parte de cima."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.21)
    h = (hand[0], hand[1], hand[2] - 0.065)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.035), (0.0, 0.0, -0.035))
    mk.limb(c, s, e, 0.068, P["skin"])
    mk.limb(c, e, h, 0.06, P["skin"])
    mk.limb(c, mk.lerp(e, h, 0.3), mk.lerp(e, h, 0.52), 0.022, P["scar"], outline=False, height=0.075)
    mk.limb(c, mk.lerp(e, h, 0.66), mk.lerp(e, h, 0.96), 0.07, P["wrap"])
    mk.cbox(c, h[0], h[1], h[2] - 0.03, 0.066, 0.066, 0.062, P["skin"])
    return s, e


def draw_sleeves(c, arms):
    """Mangas largas e curtas do quimono, soltas até o cotovelo, com a barra dobrada."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.07)
    atk = math.sin(c.atk_progress * math.pi) if c.is_melee else 0.0
    up = (c.fx, c.fy, 0.0)
    for k, (s, e, side) in enumerate(arms):
        anchor = (s[0] + c.px * side * 0.03, s[1] + c.py * side * 0.03, s[2] + 0.005)
        drag = (trail[0] - c.fx * 0.10 * atk, trail[1] - c.fy * 0.10 * atk)
        offs = cloth.chain_offsets(2, c.walk_timer, 1.7 * k, drag, (c.px, c.py), amp=amp * 1.5, freq=freq, wind=cloth.wind_at(anchor[0], anchor[1]))
        for i, o in enumerate(offs):
            origin = (anchor[0] + o[0] + c.px * side * 0.02 * i, anchor[1] + o[1] + c.py * side * 0.02 * i, anchor[2] - 0.115 * i + o[2])
            mk.obox(c, origin, (0.0, 0.0, -1.0), 0.12 if i == 0 else 0.1, 0.085 + 0.02 * i, 0.17 + 0.04 * i, P["kimono"] if i == 0 else P["kimono_dark"], up=up)
        o = offs[-1]
        hem = (anchor[0] + o[0] + c.px * side * 0.04, anchor[1] + o[1] + c.py * side * 0.04, anchor[2] - 0.215 + o[2])
        mk.obox(c, hem, (0.0, 0.0, -1.0), 0.02, 0.108, 0.25, P["kimono_light"], up=up, outline=False)


def draw_head(c):
    """Rosto severo com sobrancelhas franzidas e barba por fazer; cabelo preto com topknot desgrenhado e mechas soltas."""
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    if mk.facing_camera(c):
        front = hw / 2 + 0.004
        mk.obox(c, (bx - fx * 0.01, by - fy * 0.01, hz + 0.03), (fx, fy, 0.0), hw / 2 + 0.012, hw + 0.008, 0.052, P["stubble"], outline=False)  # barba
        # Rosto severo como pele limpa (sem cubos saltados de olhos ou boca)
    mk.cbox(c, bx, by, hz + 0.125, 0.172, 0.172, 0.075, P["hair"])
    if not mk.facing_camera(c):
        _hair_volume(c)
    trail, amp, freq = mk.motion(c, 0.06)
    # franja desalinhada e costeletas
    for s, dz in ((-1.0, 0.0), (0.0, 0.01), (1.0, 0.0)):
        mk.limb(c, (bx + fx * 0.08 + px * 0.03 * s, by + fy * 0.08 + py * 0.03 * s, hz + 0.18), (bx + fx * 0.088 + px * 0.06 * s, by + fy * 0.088 + py * 0.06 * s, hz + 0.135 + dz), 0.022, P["hair"], outline=False)
    for s in (-1.0, 1.0):
        o = cloth.chain_offsets(1, c.walk_timer, 0.8 * s, trail, (px, py), amp=amp * 0.8, freq=freq)[0]
        mk.cbox(c, bx + px * 0.082 * s + o[0], by + py * 0.082 * s + o[1], hz + 0.02, 0.03, 0.036, 0.15, P["hair"], outline=False)
    # topknot: coque amarrado com mechas espetadas ao vento
    root = (bx - fx * 0.03, by - fy * 0.03, hz + 0.19)
    wind = cloth.wind_at(root[0], root[1])
    base_tip = (root[0] - fx * 0.05, root[1] - fy * 0.05, root[2] + 0.12)
    mk.limb(c, root, base_tip, 0.07, P["hair"])
    mk.limb(c, mk.lerp(root, base_tip, 0.12), mk.lerp(root, base_tip, 0.22), 0.082, P["tasuki"], outline=False)
    spikes = ((0.5, 0.2, 0.09), (-0.6, 0.15, 0.08), (0.1, 0.6, 0.1), (-0.2, -0.5, 0.09), (0.0, 0.0, 0.13))
    for i, (a, b, length) in enumerate(spikes):
        o = cloth.chain_offsets(1, c.walk_timer, 0.9 * i, trail, (px, py), amp=amp * 2.0, freq=freq * 1.1, wind=wind, wind_gain=0.06)[0]
        tip = (base_tip[0] + px * a * 0.07 - fx * b * 0.07 + o[0], base_tip[1] + py * a * 0.07 - fy * b * 0.07 + o[1], base_tip[2] + length + o[2])
        mk.limb(c, base_tip, tip, 0.034, P["hair"], outline=False)
    mk.limb(c, base_tip, (base_tip[0], base_tip[1], base_tip[2] + 0.1), 0.04, P["hair_light"], outline=False)


# ---------------------------------------------------------------------------------------------------------------------
# Espadas
# ---------------------------------------------------------------------------------------------------------------------

def _blade(c, hand, d, length, short=False):
    """Espada na mão: cabo com ito preto atrás da mão, tsuba, habaki e lâmina com fio claro."""
    P = pal()
    tsuba = mk.add(hand, d, 0.06)
    mk.obox(c, mk.add(tsuba, d, -0.16 if not short else -0.13), d, 0.16 if not short else 0.13, 0.04, 0.04, P["ito"])
    mk.obox(c, mk.add(tsuba, d, -0.172), d, 0.02, 0.046, 0.046, P["gold"], outline=False)
    mk.obox(c, mk.add(tsuba, d, -0.008), d, 0.016, 0.09 if not short else 0.07, 0.09 if not short else 0.07, P["tsuba"])
    mk.obox(c, mk.add(tsuba, d, 0.008), d, 0.03, 0.05, 0.036, P["gold"], outline=False)
    mk.obox(c, mk.add(tsuba, d, 0.03), d, length, 0.044, 0.03, P["steel"])
    mk.obox(c, mk.add(tsuba, d, 0.04), d, max(0.0, length - 0.02), 0.016, 0.034, P["edge"], outline=False)


def _sheathed_hilts(c):
    P = pal()
    (k, b1), (k2, b2) = _scabbards(c)
    for origin, b, length, w in ((k, b1, 0.17, 0.04), (k2, b2, 0.12, 0.036)):
        h = (-b[0], -b[1], -b[2])
        mk.obox(c, origin, h, length, w, w, P["ito"])
        mk.obox(c, mk.add(origin, h, length - 0.01), h, 0.02, w + 0.006, w + 0.006, P["gold"], outline=False)
        mk.obox(c, mk.add(origin, b, -0.008), b, 0.016, 0.08 if length > 0.15 else 0.065, 0.08 if length > 0.15 else 0.065, P["tsuba"])


def draw_front(c, arm_l, arm_r):
    """Bainhas (se do lado da câmera), lâminas conforme o estado e, no golpe, o rastro azul."""
    (k, b1), _ = _scabbards(c)
    if not _behind(c, mk.add(k, b1, 0.25)):
        _sheaths(c)
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    if c.state == "PARRY":
        _parry(c)
    elif c.is_melee:
        step, p = _step(c), c.atk_progress
        dk, lk, dw, lw = _blade_dirs(c, p, step)
        _blade(c, hand_r, dk, lk)
        _blade(c, hand_l, dw, lw, short=True)
        _slash_trail(c, p, step)
    elif c.is_moving:
        _sheathed_hilts(c)
    else:
        dk, lk, dw, lw = _drawn_dirs(c)
        _blade(c, hand_r, dk, lk)
        _blade(c, hand_l, dw, lw, short=True)


def _parry(c):
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.torso_z + 0.05
    left = (bx + fx * 0.15 + px * 0.12, by + fy * 0.15 + py * 0.12, z)
    right = (bx + fx * 0.15 - px * 0.12, by + fy * 0.15 - py * 0.12, z)
    _blade(c, right, mk.norm((fx * 0.3 + px * 0.6, fy * 0.3 + py * 0.6, 0.75)), 0.62)
    _blade(c, left, mk.norm((fx * 0.3 - px * 0.6, fy * 0.3 - py * 0.6, 0.75)), 0.46, short=True)


def _slash_trail(c, p, step):
    """Fantasmas da lâmina que golpeia nos quadros anteriores, formando a faixa azul do corte."""
    P = pal()
    ghosts = []
    for j in range(6):
        pj = p - 0.07 * j
        if pj < 0.05:
            break
        left, right = _hands_at(c, pj, step)
        dk, lk, dw, lw = _blade_dirs(c, pj, step)
        hand, d, length = ((left, dw, lw) if step == 2 else (right, dk, lk))
        h = (hand[0], hand[1], hand[2] - 0.065)
        ghosts.append((mk.add(h, d, length * 0.5), mk.add(h, d, length * 1.06)))
    for j in range(len(ghosts) - 1):
        a0, a1 = ghosts[j]
        b0, b1 = ghosts[j + 1]
        fade = 1.0 - j / 6.0
        mk.band(c, (a0, a1, b1, b0), P["trail"] + (int(225 * fade),))
        mk.band(c, (mk.lerp(a0, a1, 0.5), a1, b1, mk.lerp(b0, b1, 0.5)), P["trail_core"] + (int(250 * fade),))
