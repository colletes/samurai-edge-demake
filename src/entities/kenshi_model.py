"""
Kenshi, a espadachim do Iaijutsu (6.5.5): cabelo castanho-ruivo em rabo de cavalo alto com laço vermelho, quimono
carmim sem mangas com colarinho branco, mangas soltas largas com punho dourado, hakama larga e pregueada, obi com nó
na frente e a katana na cintura (saya à esquerda, mão direita no cabo).
Dois estilos saem do mesmo modelo: "detailed" (cores do conceito) e "cel" (cores e rampas de tom amostradas dos sprites
HD-2D, com contorno de tinta feito por `cel_outline`). Os ganchos são chamados por `render_voxel_humanoid`.
Mudanças só visuais: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk
from src.isometric import cloth, voxel_renderer
from src.isometric.voxel_rig import calc_blade_slash_3d

SKIN = (248, 218, 192)
SKIN_SHADOW = (220, 180, 150)

DETAILED = {
    "hair": (152, 84, 50), "hair_light": (200, 122, 70), "hair_dark": (96, 50, 36), "ribbon": (206, 36, 54),
    "skin": SKIN, "skin_shadow": SKIN_SHADOW, "eye": (58, 34, 30), "lip": (206, 98, 104),
    "kimono": (180, 32, 54), "kimono_dark": (122, 20, 42), "collar": (244, 240, 236),
    "cuff": (214, 162, 52), "cuff_dark": (150, 104, 30),
    "hakama": (78, 66, 120), "hakama_dark": (50, 42, 84), "obi": (112, 94, 170),
    "sandal": (180, 146, 100), "strap": (40, 32, 36),
    "saya": (34, 28, 38), "ito": (52, 38, 40), "ito_light": (226, 216, 196), "gold": (232, 190, 66),
    "steel": (228, 236, 248), "edge": (252, 254, 255),
    "trail": (222, 38, 56), "trail_core": (255, 214, 196),
}

# Sprites HD-2D (kenshi/front_idle_0): (sombra, tom médio, luz) amostrados por região do corpo.
_CEL_RAMPS = {
    "hair": ((78, 44, 38), (122, 70, 54), (160, 98, 70)),
    "kimono": ((69, 13, 33), (129, 30, 50), (187, 53, 69)),
    "skin": ((186, 126, 106), (235, 178, 143), (250, 207, 168)),
    "hakama": ((23, 19, 24), (35, 29, 35), (66, 57, 63)),
    "gold": ((128, 86, 34), (190, 140, 48), (240, 192, 88)),
    "sandal": ((115, 83, 70), (144, 104, 81), (180, 138, 104)),
    "collar": ((190, 186, 200), (238, 236, 242), (255, 255, 255)),
    "saya": ((16, 14, 20), (30, 26, 32), (66, 58, 70)),
    "steel": ((122, 130, 150), (200, 208, 222), (246, 250, 255)),
}
CEL = {
    "hair": _CEL_RAMPS["hair"][1], "hair_light": (156, 94, 67), "hair_dark": (65, 31, 31), "ribbon": (200, 36, 52),
    "skin": _CEL_RAMPS["skin"][1], "skin_shadow": _CEL_RAMPS["skin"][0], "eye": (51, 29, 28), "lip": (190, 92, 98),
    "kimono": _CEL_RAMPS["kimono"][1], "kimono_dark": _CEL_RAMPS["kimono"][0], "collar": _CEL_RAMPS["collar"][1],
    "cuff": _CEL_RAMPS["gold"][1], "cuff_dark": _CEL_RAMPS["gold"][0],
    "hakama": _CEL_RAMPS["hakama"][1], "hakama_dark": _CEL_RAMPS["hakama"][0], "obi": (48, 40, 56),
    "sandal": _CEL_RAMPS["sandal"][1], "strap": (30, 26, 32),
    "saya": _CEL_RAMPS["saya"][1], "ito": (44, 36, 40), "ito_light": (200, 190, 170), "gold": _CEL_RAMPS["gold"][1],
    "steel": _CEL_RAMPS["steel"][1], "edge": (250, 252, 255),
    "trail": (222, 40, 62), "trail_core": (255, 226, 200),
}
for _name, (_shadow, _mid, _light) in _CEL_RAMPS.items():
    voxel_renderer.register_cel_ramp(_mid, _light, _shadow)


MATERIALS = {"kimono": "silk", "kimono_dark": "silk", "obi": "silk", "collar": "silk", "ribbon": "silk", "saya": "lacquer"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return CEL if voxel_renderer.get_render_style() == "cel" else DETAILED


def _outward(c, side):
    return (c.px * side, c.py * side, 0.0)


def _sword_frame(c):
    """Ponto da boca da bainha (K), direção da bainha/lâmina (B) e do cabo (-B), na cintura esquerda."""
    k = (c.base_x + c.px * 0.11 + c.fx * 0.075, c.base_y + c.py * 0.11 + c.fy * 0.075, c.pelvis_z + 0.07)
    b = mk.norm((-c.fx * 0.80 + c.px * 0.40, -c.fy * 0.80 + c.py * 0.40, -0.32))
    return k, b


def idle_arms(c):
    """Neutra: mão direita cruza a barriga e empunha o cabo, esquerda segura a boca da bainha."""
    k, b = _sword_frame(c)
    grip = mk.add(k, b, -0.08)
    left = mk.add(k, b, 0.09)
    return (left[0], left[1], left[2] + 0.07), (grip[0], grip[1], grip[2] + 0.07)


def _arc_hand(c, p):
    a = -0.75 + p * 2.15
    return (c.base_x + c.fx * math.cos(a) * 0.24 - c.px * math.sin(a) * 0.24,
            c.base_y + c.fy * math.cos(a) * 0.24 - c.py * math.sin(a) * 0.24,
            c.torso_z + 0.18 - p * 0.10)


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def attack_arms(c):
    """Antecipação (mão no cabo, bainha presa), saque e corte em arco da esquerda para a direita, acompanhamento aberto."""
    p = c.atk_progress
    k, b = _sword_frame(c)
    grip = mk.add(mk.add(k, b, -0.08), (0.0, 0.0, 0.07))
    hand_r = mk.lerp(grip, _arc_hand(c, 0.22), _smooth((p - 0.08) / 0.14)) if p < 0.22 else _arc_hand(c, p)
    pull = _smooth((p - 0.1) / 0.3)
    left = mk.add(k, b, 0.09 + 0.10 * pull)
    return (left[0], left[1], left[2] + 0.07 - 0.04 * pull), hand_r


def _blade_dir(c, p):
    """Direção da lâmina: sai pela linha da bainha e gira rápido até a tangente do arco do corte."""
    _, b = _sword_frame(c)
    arc = calc_blade_slash_3d("kenshin", "ATTACK", p, c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py)["dir"]
    return mk.norm(mk.lerp(b, arc, _smooth((p - 0.2) / 0.1)))


# ---------------------------------------------------------------------------------------------------------------------
# Peças desenhadas por trás do corpo quando estão do lado oposto à câmera (rabo de cavalo, bainha) ou à frente dele
# ---------------------------------------------------------------------------------------------------------------------

def _behind(c, point) -> bool:
    return mk.depth(c, point[0], point[1]) < mk.depth(c, c.base_x, c.base_y) - 0.02


def draw_behind(c):
    """Camada de trás: o que está do lado oposto à câmera e deve ficar sob o corpo."""
    if mk.facing_camera(c):
        _hair_volume(c)  # o volume de trás fica atrás do rosto; de costas ele cobre a cabeça
    if _behind(c, _tail_root(c)):
        _ponytail(c)
    k, b = _sword_frame(c)
    if _behind(c, mk.add(k, b, 0.22)):
        _saya(c)


def _hair_volume(c):
    P = pal()
    mk.cbox(c, c.base_x - c.fx * 0.036, c.base_y - c.fy * 0.036, c.head_z + 0.03, 0.15, 0.15, 0.12, P["hair"], outline=False)


def _tail_root(c):
    return (c.base_x - c.fx * 0.075, c.base_y - c.fy * 0.075, c.head_z + 0.19)


def _ponytail(c):
    P = pal()
    root = _tail_root(c)
    trail, amp, freq = mk.motion(c, 0.09)
    offs = cloth.chain_offsets(4, c.walk_timer, 0.4, trail, (c.px, c.py), amp=amp * 1.6, freq=freq * 0.9, wind=cloth.wind_at(root[0], root[1]),
                               wind_gain=0.05)
    f = (c.fx, c.fy)
    base_pts = [root, (root[0] - f[0] * 0.05, root[1] - f[1] * 0.05, root[2] + 0.035), (root[0] - f[0] * 0.11, root[1] - f[1] * 0.11, root[2] - 0.02),
                (root[0] - f[0] * 0.14, root[1] - f[1] * 0.14, root[2] - 0.12), (root[0] - f[0] * 0.15, root[1] - f[1] * 0.15, root[2] - 0.23)]
    pts = [base_pts[0]] + [mk.add(base_pts[i + 1], offs[i]) for i in range(4)]
    widths = (0.078, 0.074, 0.064, 0.052)
    colors = (P["hair"], P["hair"], P["hair_light"], P["hair_dark"] if voxel_renderer.get_render_style() == "cel" else P["hair"])
    for i in range(4):
        mk.limb(c, pts[i], pts[i + 1], widths[i], colors[i])
    mk.limb(c, pts[3], pts[4], 0.03, P["hair_light"], outline=False)  # mecha clara da ponta


def _saya(c):
    P = pal()
    k, b = _sword_frame(c)
    mk.obox(c, k, b, 0.46, 0.044, 0.044, P["saya"])
    mk.obox(c, k, b, 0.03, 0.054, 0.054, P["gold"], outline=False)  # koiguchi
    mk.obox(c, mk.add(k, b, 0.43), b, 0.035, 0.048, 0.048, P["gold"], outline=False)  # kojiri
    offs = cloth.chain_offsets(2, c.walk_timer, 1.3, mk.motion(c, 0.05)[0], (c.px, c.py), amp=0.02, freq=2.2)  # sageo
    for i, o in enumerate(offs):
        a = mk.add(k, b, 0.05 + 0.035 * i)
        mk.cbox(c, a[0] + o[0], a[1] + o[1], a[2] - 0.05 - 0.04 * i, 0.016, 0.016, 0.05, P["ribbon"], outline=False)


def _tsuka(c, tsuba, blade_dir):
    P = pal()
    hilt = (-blade_dir[0], -blade_dir[1], -blade_dir[2])
    mk.obox(c, tsuba, hilt, 0.16, 0.036, 0.036, P["ito"])
    for t in (0.04, 0.085, 0.13):
        mk.obox(c, mk.add(tsuba, hilt, t), hilt, 0.02, 0.041, 0.041, P["ito_light"], outline=False)
    mk.obox(c, mk.add(tsuba, hilt, 0.155), hilt, 0.022, 0.042, 0.042, P["gold"], outline=False)  # kashira
    mk.obox(c, mk.add(tsuba, blade_dir, -0.008), blade_dir, 0.016, 0.082, 0.082, P["gold"], outline=False)  # tsuba


def draw_legs(c):
    """Hakama larga e pregueada que alarga até a barra, com a ponta do pé de waraji aparecendo."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.05)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]
        sign = 1.0 if side == "L" else -1.0
        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.9 * sign, trail, (c.px, c.py), amp=amp * 0.7, freq=freq, wind=cloth.wind_at(ft[0], ft[1]))
        # pé primeiro: a barra da hakama o cobre quase todo
        mk.obox(c, (ft[0] - c.fx * 0.045, ft[1] - c.fy * 0.045, ft[2]), (c.fx, c.fy, 0.0), 0.13, 0.07, 0.03, P["sandal"])
        mk.obox(c, (ft[0] - c.fx * 0.02, ft[1] - c.fy * 0.02, ft[2] + 0.03), (c.fx, c.fy, 0.0), 0.095, 0.055, 0.03, P["skin"], outline=False)
        mk.obox(c, (ft[0] + c.fx * 0.02, ft[1] + c.fy * 0.02, ft[2] + 0.03), (c.fx, c.fy, 0.0), 0.02, 0.058, 0.032, P["strap"], outline=False)
        top = (th[0], th[1], th[2] + 0.225)
        knee = (sh[0] + o1[0], sh[1] + o1[1], sh[2] + 0.2)
        hem = (sh[0] + o2[0], sh[1] + o2[1], sh[2] + 0.005)
        mk.limb(c, top, knee, 0.152, P["hakama"])
        mk.limb(c, knee, hem, 0.176, P["hakama"])
        mk.limb(c, mk.add(hem, (0, 0, 0.022)), hem, 0.184, P["hakama_dark"], outline=False)  # barra


def draw_obi(c):
    """Obi largo com o nó na frente e duas pontas penduradas que balançam; placa lombar da hakama nas costas."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07
    mk.cbox(c, bx, by, z - 0.012, c.pelvis_w, c.pelvis_w * 0.78, 0.018, P["hakama_dark"], outline=False)
    mk.cbox(c, bx - fx * 0.108, by - fy * 0.108, c.pelvis_z + 0.04, 0.10, 0.07, 0.15, P["hakama_dark"])  # koshi-ita
    kx, ky = bx + fx * 0.098 + px * 0.012, by + fy * 0.098 + py * 0.012
    mk.cbox(c, kx, ky, z + 0.005, 0.085, 0.05, 0.075, P["obi"])
    for s in (-1.0, 1.0):  # laços do nó
        mk.obox(c, (kx + px * 0.03 * s, ky + py * 0.03 * s, z + 0.045), (px * s, py * s, 0.25), 0.065, 0.032, 0.05, P["obi"])
    trail, amp, freq = mk.motion(c, 0.05)
    for k, (s, length) in enumerate(((-1.0, 3), (1.0, 2))):
        offs = cloth.chain_offsets(length, c.walk_timer, 1.1 * k, trail, (px, py), amp=amp * 1.4, freq=freq, wind=cloth.wind_at(kx, ky))
        for i, o in enumerate(offs):
            mk.cbox(c, kx + px * 0.03 * s + o[0], ky + fy * 0.012 + py * 0.03 * s + o[1], z - 0.012 - 0.07 * (i + 1) + o[2], 0.04, 0.026, 0.075, P["obi"])


def draw_torso(c):
    """Colarinho branco em V sobre o peito, no lugar da gola lisa."""
    P = pal()
    chest_d = 0.17
    front = chest_d / 2 + 0.006
    tz = c.torso_z
    apex = (c.base_x + c.fx * front, c.base_y + c.fy * front, tz + 0.11)
    for s in (-1.0, 1.0):
        top = (c.base_x + c.fx * (front - 0.004) + c.px * 0.062 * s, c.base_y + c.fy * (front - 0.004) + c.py * 0.062 * s, tz + 0.255)
        mk.limb(c, top, apex, 0.026, P["collar"], outline=False, height=0.016)
    mk.cbox(c, c.base_x + c.fx * (front - 0.004), c.base_y + c.fy * (front - 0.004), tz + 0.205, 0.05, 0.02, 0.05, P["skin"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço nu em duas partes (ombro-cotovelo, cotovelo-mão) que acompanha a mão; as mangas vêm separadas."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.205)
    h = (hand[0], hand[1], hand[2] - 0.065)
    out = _outward(c, side)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.03), (0.0, 0.0, -0.035))
    mk.cbox(c, s[0], s[1], s[2] - 0.035, 0.075, 0.075, 0.07, P["skin"], outline=False)
    mk.limb(c, s, e, 0.062, P["skin"])
    mk.limb(c, e, h, 0.054, P["skin"])
    mk.cbox(c, h[0], h[1], h[2] - 0.028, 0.056, 0.056, 0.056, P["skin"])
    return s, e


def draw_sleeves(c, arms):
    """Mangas soltas largas e curtas do quimono, presas no braço, penduradas; arrastam e abrem no ataque."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.07)
    atk = math.sin(c.atk_progress * math.pi) if c.is_melee else 0.0
    for k, (s, e, side) in enumerate(arms):
        anchor = (s[0] + c.px * side * 0.055, s[1] + c.py * side * 0.055, s[2] - 0.03)
        drag = (trail[0] - c.fx * 0.13 * atk + c.px * side * 0.07 * atk, trail[1] - c.fy * 0.13 * atk + c.py * side * 0.07 * atk)
        offs = cloth.chain_offsets(3, c.walk_timer, 1.7 * k, drag, (c.px, c.py), amp=amp * 1.5, freq=freq, wind=cloth.wind_at(anchor[0], anchor[1]))
        up = (c.fx, c.fy, 0.0)
        for i, o in enumerate(offs):
            origin = (anchor[0] + o[0] + c.px * side * 0.018 * i, anchor[1] + o[1] + c.py * side * 0.018 * i, anchor[2] - 0.115 * i + o[2])
            color = P["kimono"] if i < 2 else P["kimono_dark"]
            mk.obox(c, origin, (0.0, 0.0, -1.0), 0.118 if i < 2 else 0.095, 0.06 + 0.014 * i, 0.15 + 0.045 * i, color, up=up)
        o = offs[-1]
        bottom = (anchor[0] + o[0] + c.px * side * 0.054, anchor[1] + o[1] + c.py * side * 0.054, anchor[2] - 0.115 * 2 - 0.095 + o[2])
        mk.obox(c, (bottom[0], bottom[1], bottom[2] + 0.052), (0.0, 0.0, -1.0), 0.052, 0.088, 0.24, P["cuff"], up=up)  # punho dourado
        for t in (0.012, 0.03):
            mk.obox(c, (bottom[0], bottom[1], bottom[2] + 0.052 - t), (0.0, 0.0, -1.0), 0.008, 0.092, 0.244, P["cuff_dark"], up=up, outline=False)


def draw_head(c):
    """Rosto, cabelo castanho-ruivo com franja de lado, mechas laterais e laço vermelho; o rabo vem de `draw_behind`/`draw_front`."""
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    if mk.facing_camera(c):
        front = hw / 2 + 0.004
        for s in (-1.0, 1.0):
            ex, ey = bx + fx * front + px * 0.034 * s, by + fy * front + py * 0.034 * s
            mk.cbox(c, ex, ey, hz + 0.083, 0.024, 0.02, 0.032, P["eye"], outline=False)
            mk.cbox(c, ex + fx * 0.004 + px * 0.004 * s, ey + fy * 0.004 + py * 0.004 * s, hz + 0.105, 0.009, 0.009, 0.009, (255, 255, 255), outline=False)
            mk.limb(c, (ex - px * 0.019 * s, ey - py * 0.019 * s, hz + 0.128 - 0.004 * s), (ex + px * 0.019 * s, ey + py * 0.019 * s, hz + 0.128 + 0.004 * s),
                    0.009, P["hair_dark"], outline=False)
        mk.cbox(c, bx + fx * front, by + fy * front, hz + 0.062, 0.012, 0.012, 0.012, P["skin_shadow"], outline=False)
        mk.cbox(c, bx + fx * front, by + fy * front, hz + 0.043, 0.026, 0.012, 0.011, P["lip"], outline=False)
    # calota, volume de trás e franja
    mk.cbox(c, bx, by, hz + 0.115, 0.168, 0.168, 0.08, P["hair"])
    if not mk.facing_camera(c):
        _hair_volume(c)
    mk.limb(c, (bx + fx * 0.07 - px * 0.05, by + fy * 0.07 - py * 0.05, hz + 0.18), (bx + fx * 0.072 + px * 0.075, by + fy * 0.072 + py * 0.075, hz + 0.125), 0.04,
            P["hair"], outline=False)
    mk.limb(c, (bx + fx * 0.07 - px * 0.01, by + fy * 0.07 - py * 0.01, hz + 0.18), (bx + fx * 0.068 + px * 0.05, by + fy * 0.068 + py * 0.05, hz + 0.105), 0.03,
            P["hair_light"], outline=False)
    trail, amp, freq = mk.motion(c, 0.05)
    for s in (-1.0, 1.0):  # mechas laterais que emolduram o rosto
        o = cloth.chain_offsets(1, c.walk_timer, 0.8 * s, trail, (px, py), amp=amp * 0.8, freq=freq)[0]
        mk.cbox(c, bx + px * 0.077 * s + o[0], by + py * 0.077 * s + o[1], hz - 0.035, 0.038, 0.04, 0.17, P["hair"], outline=False)
    if not _behind(c, _tail_root(c)):
        _ponytail(c)
    root = _tail_root(c)  # laço vermelho e as pontas da fita
    mk.cbox(c, root[0], root[1], root[2] - 0.02, 0.05, 0.05, 0.05, P["ribbon"])
    for s in (-1.0, 1.0):
        mk.obox(c, (root[0], root[1], root[2] + 0.002), (px * s * 0.9, py * s * 0.9, 0.35), 0.075, 0.03, 0.045, P["ribbon"])
    offs = cloth.chain_offsets(2, c.walk_timer, 2.1, trail, (px, py), amp=amp * 1.6, freq=freq * 1.2, wind=cloth.wind_at(root[0], root[1]))
    for i, o in enumerate(offs):
        mk.cbox(c, root[0] - fx * 0.03 + o[0], root[1] - fy * 0.03 + o[1], root[2] - 0.06 - 0.05 * i + o[2], 0.026, 0.02, 0.055, P["ribbon"], outline=False)


def draw_front(c, arm_l, arm_r):
    """Bainha (se estiver do lado da câmera), cabo e lâmina; no ataque a lâmina sai da bainha e deixa o rastro vermelho."""
    P = pal()
    k, b = _sword_frame(c)
    if not _behind(c, mk.add(k, b, 0.22)):
        _saya(c)
    if not c.is_melee:
        _tsuka(c, k, b)
        return
    p = c.atk_progress
    if p < 0.1:  # ainda embainhada, mão no cabo
        _tsuka(c, k, b)
        return
    hand = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    d = _blade_dir(c, p)
    s_draw = _smooth((p - 0.1) / 0.1)  # saque: a lâmina aparece conforme o cabo vem da cintura para a mão
    tsuba = mk.lerp(k, hand, s_draw)
    length = 0.72 * s_draw
    _tsuka(c, tsuba, d)
    mk.obox(c, tsuba, d, length, 0.05, 0.034, P["steel"])
    mk.obox(c, mk.add(tsuba, d, 0.02), d, max(0.0, length - 0.02), 0.018, 0.036, P["edge"], outline=False)  # fio
    if p >= 0.34:
        _slash_trail(c, p, length)


def _slash_trail(c, p, length):
    """Meia-lua do corte: faixas translúcidas entre as posições recentes da ponta, de vermelho a branco quente no centro."""
    P = pal()
    steps = []
    for j in range(10):
        pj = p - 0.017 * j
        if pj < 0.3:
            break
        h = _arc_hand(c, pj)
        h = (h[0], h[1], h[2] - 0.065)
        d = _blade_dir(c, pj)
        steps.append((mk.add(h, d, length * 0.72), mk.add(h, d, length * 1.06)))
    for j in range(len(steps) - 1):
        a0, a1 = steps[j]
        b0, b1 = steps[j + 1]
        fade = (1.0 - j / 10.0) ** 1.3
        mk.band(c, (a0, a1, b1, b0), P["trail"] + (int(240 * fade),))
        mk.band(c, (mk.lerp(a0, a1, 0.55), a1, b1, mk.lerp(b0, b1, 0.55)), P["trail_core"] + (int(255 * fade),))
