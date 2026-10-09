"""
Okuni, dançarina kabuki (6.5.5): rosto de maquiagem branca (sem nariz de bola), cabelo shimada com kanzashi, quimono
longo em camadas que balança, laço do obi nas costas, mangas furisode e leques que abrem no ataque.
O desenho entra no `render_voxel_humanoid` por ganchos (`draw_head`, `draw_skirt`, `draw_bow`, `draw_sleeves`, `draw_fans`)
e as posições dos braços vêm de `idle_arms` e `attack_arms`.
"""
import math

from src.config import COLOR_GOLD, COLOR_KABUKI_WHITE
from src.isometric import cloth
from src.isometric.voxel_renderer import draw_oriented_voxel_box, draw_voxel_box

CRIMSON = (165, 24, 35)
CRIMSON_DARK = (112, 16, 30)
CRIMSON_DEEP = (84, 12, 26)
BLACK = (24, 22, 28)
EYE_RED = (196, 34, 58)
LIP_RED = (200, 30, 52)
FAN_RED = (190, 32, 44)
GOLD_DEEP = (176, 136, 44)
WHITE = COLOR_KABUKI_WHITE


def _box(c, x, y, z, w, d, h, color, outline=True, texture=None):
    draw_voxel_box(c.surface, c.camera, x, y, z, w, d, h, color, outline=outline, alpha=c.alpha, texture=texture)


def _obox(c, ox, oy, oz, direction, length, width, height, color, up=(0.0, 0.0, 1.0), outline=True):
    draw_oriented_voxel_box(c.surface, c.camera, ox, oy, oz, direction[0], direction[1], direction[2], length, width, height, color,
                            up_x=up[0], up_y=up[1], up_z=up[2], outline=outline, alpha=c.alpha)


def _norm(v):
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) or 1.0
    return (v[0] / n, v[1] / n, v[2] / n)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _motion(c):
    """(arrasto, amplitude do balanço, frequência) conforme ande ou fique parada."""
    if c.is_moving:
        return (-c.fx * 0.07, -c.fy * 0.07), 0.04, 7.0
    return (0.0, 0.0), 0.014, 1.7


def draw_head(c):
    """Rosto kabuki limpo com pó branco tradicional oshiroi, sem olhos ou boca saltados; shimada com kanzashi e pente."""
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    _box(c, bx - 0.04, by - 0.04, c.neck_z - 0.005, 0.08, 0.08, 0.07, WHITE, outline=False)  # nuca branca
    _box(c, bx - hw / 2 - 0.006, by - hw / 2 - 0.006, hz + 0.03, hw + 0.012, hw + 0.012, 0.14, WHITE)
    # Sombra sutil de queixo
    _box(c, bx + fx * (hw / 2) - 0.035, by + fy * (hw / 2) - 0.035, hz + 0.01, 0.07, 0.07, 0.04, (230, 226, 220), outline=False)

    # cabelo laqueado: calota, laterais (tabo), coque shimada atrás e coque no topo
    _box(c, bx - 0.082, by - 0.082, hz + 0.14, 0.164, 0.164, 0.075, BLACK)
    _box(c, bx + fx * 0.05 - 0.05, by + fy * 0.05 - 0.05, hz + 0.15, 0.10, 0.10, 0.04, BLACK, outline=False)  # franja
    for s in (-1.0, 1.0):
        _box(c, bx + px * 0.088 * s - 0.022, by + py * 0.088 * s - 0.022, hz + 0.06, 0.044, 0.044, 0.12, BLACK, outline=False)
    _box(c, bx - fx * 0.10 - 0.055, by - fy * 0.10 - 0.055, hz + 0.08, 0.11, 0.11, 0.13, BLACK)
    _box(c, bx - 0.04, by - 0.04, hz + 0.215, 0.08, 0.08, 0.06, BLACK)

    # kanzashi dourados em leque dos dois lados, pente na testa e borlas que balançam
    for s in (-1.0, 1.0):
        for j in range(3):
            d = _norm((px * s * (0.55 + 0.32 * j), py * s * (0.55 + 0.32 * j), 0.85 - 0.22 * j))
            _obox(c, bx + px * 0.075 * s, by + py * 0.075 * s, hz + 0.17, d, 0.15 + 0.02 * j, 0.011, 0.011, COLOR_GOLD, outline=False)
        offs = cloth.chain_offsets(2, c.walk_timer, 0.9 * s, (-fx * (0.03 if c.is_moving else 0.0), -fy * (0.03 if c.is_moving else 0.0)),
                                   (px, py), amp=0.014, freq=5.5 if c.is_moving else 2.0)
        for i, (ox, oy, oz) in enumerate(offs):
            _box(c, bx + px * 0.20 * s + ox - 0.008, by + py * 0.20 * s + oy - 0.008, hz + 0.14 - 0.05 * i + oz, 0.016, 0.016, 0.04, COLOR_GOLD, outline=False)
    _obox(c, bx + fx * 0.075 - px * 0.05, by + fy * 0.075 - py * 0.05, hz + 0.19, (px, py, 0.0), 0.10, 0.018, 0.04, COLOR_GOLD, outline=False)


def draw_skirt(c):
    """Quimono comprido em três camadas que alargam pouco, com barra dourada, faixa bordada, cauda e tabi nos pés."""
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    trail, amp, freq = _motion(c)
    offs = cloth.chain_offsets(3, c.walk_timer, 0.0, trail, (px, py), amp=amp, freq=freq, wind=cloth.wind_at(bx, by))
    flare = 0.10 * c.lunge_curve
    top, bottom = c.pelvis_z + 0.03, c.base_z + 0.04
    h = (top - bottom) / 3.0
    widths = (c.pelvis_w + 0.05, c.pelvis_w + 0.09, c.pelvis_w + 0.13)
    colors = (CRIMSON, CRIMSON_DARK, CRIMSON_DEEP)
    hem_w = widths[2] + 0.05 + flare
    ox, oy, _ = offs[2]
    _box(c, bx - hem_w / 2 + ox, by - hem_w * 0.45 + oy, c.base_z + 0.015, hem_w, hem_w * 0.9, 0.03, COLOR_GOLD, outline=False)  # barra primeiro, para as camadas a cobrirem
    for i in (2, 1, 0):  # de baixo para cima: a camada de cima cobre a face superior da faixa de baixo
        w = widths[i] + flare * (i + 1) / 3.0
        ox, oy, _ = offs[i]
        _box(c, bx - w / 2 + ox, by - w * 0.45 + oy, top - h * (i + 1), w, w * 0.9, h, colors[i], texture="silk")
        if i > 0:  # faixa bordada de ouro na borda de cima da camada
            wb = w + 0.012
            _box(c, bx - wb / 2 + ox, by - wb * 0.45 + oy, top - h * i - 0.02, wb, wb * 0.9, 0.022, COLOR_GOLD, outline=False)
    ox, oy, _ = offs[2]
    _box(c, bx - fx * 0.21 + ox * 1.3 - 0.09, by - fy * 0.21 + oy * 1.3 - 0.09, c.base_z + 0.012, 0.18, 0.18, 0.03, CRIMSON_DEEP, outline=False)  # cauda
    for side in ("L", "R"):  # tabi branco e geta aparecendo na frente da barra
        fxp, fyp, fzp = c.legs_data[side]["foot"]
        _box(c, fxp - 0.04 + fx * 0.06, fyp - 0.04 + fy * 0.06, fzp, 0.08, 0.08, 0.04, (236, 232, 226), outline=True)
        _box(c, fxp - 0.04 + fx * 0.06, fyp - 0.04 + fy * 0.06, fzp, 0.08, 0.08, 0.012, BLACK, outline=False)


def draw_bow(c):
    """Laço grande do obi (musubi) nas costas: nó dourado, duas asas e duas pontas que balançam."""
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    cx, cy, z = bx - fx * 0.14, by - fy * 0.14, c.torso_z + 0.01
    flap = math.sin(c.walk_timer * (7.0 if c.is_moving else 1.7)) * 0.025
    _box(c, cx - 0.05, cy - 0.05, z, 0.10, 0.10, 0.15, COLOR_GOLD)
    for s in (-1.0, 1.0):
        _obox(c, cx + px * 0.04 * s, cy + py * 0.04 * s, z + 0.06, _norm((px * s, py * s, 0.18 + flap * 4.0)), 0.15, 0.13, 0.05, GOLD_DEEP)
    trail, amp, freq = _motion(c)
    offs = cloth.chain_offsets(2, c.walk_timer, 0.4, trail, (px, py), amp=amp * 1.2, freq=freq, wind=cloth.wind_at(bx, by))
    for i, (ox, oy, oz) in enumerate(offs):
        _box(c, cx - fx * 0.04 + ox - 0.035, cy - fy * 0.04 + oy - 0.035, z - 0.08 - 0.09 * i + oz, 0.07, 0.07, 0.10, COLOR_GOLD if i == 0 else BLACK, outline=False)


def draw_sleeves(c, arms):
    """Mangas furisode longas penduradas dos braços; arrastam no movimento e abrem no ataque."""
    trail, amp, freq = _motion(c)
    atk = math.sin(c.atk_progress * math.pi) if c.is_melee else 0.0
    for k, (ax, ay, az) in enumerate(arms):
        phase = 1.7 * k
        offs = cloth.chain_offsets(3, c.walk_timer, phase, (trail[0] - c.fx * 0.10 * atk, trail[1] - c.fy * 0.10 * atk), (c.px, c.py),
                                   amp=amp * 1.5, freq=freq, wind=cloth.wind_at(ax, ay))
        for i, (ox, oy, oz) in enumerate(offs):
            w = 0.07 + 0.014 * i
            color = CRIMSON if i < 2 else CRIMSON_DARK
            _box(c, ax + ox - w / 2, ay + oy - w / 2, az - 0.06 - 0.10 * (i + 1) + oz, w, w, 0.10, color, texture="silk")
        ox, oy, oz = offs[-1]
        _box(c, ax + ox - 0.05, ay + oy - 0.05, az - 0.06 - 0.40 + oz, 0.10, 0.10, 0.025, COLOR_GOLD, outline=False)


def _open_fan(c, hand, spine, normal, spread=1.15, length=0.24, ribs=7):
    """Leque aberto: costelas douradas saindo da mão em leque e painéis vermelhos entre elas."""
    spine, normal = _norm(spine), _norm(normal)
    tangent = _norm(_cross(normal, spine))
    hx, hy, hz = hand
    dirs = []
    for i in range(ribs):
        a = -spread + 2.0 * spread * i / (ribs - 1)
        dirs.append((spine[0] * math.cos(a) + tangent[0] * math.sin(a), spine[1] * math.cos(a) + tangent[1] * math.sin(a),
                     spine[2] * math.cos(a) + tangent[2] * math.sin(a)))
    panel_w = 2.0 * length * math.sin(spread / (ribs - 1)) * 0.95
    for i in range(ribs - 1):
        mid = _norm((dirs[i][0] + dirs[i + 1][0], dirs[i][1] + dirs[i + 1][1], dirs[i][2] + dirs[i + 1][2]))
        _obox(c, hx + mid[0] * 0.03, hy + mid[1] * 0.03, hz + mid[2] * 0.03, mid, length * 0.95, panel_w, 0.008, FAN_RED, up=normal, outline=False)
    for i, d in enumerate(dirs):
        _obox(c, hx, hy, hz, d, length, 0.012 if 0 < i < ribs - 1 else 0.018, 0.014, COLOR_GOLD, up=normal, outline=False)


def _closed_fan(c, hand, direction):
    _obox(c, hand[0], hand[1], hand[2], direction, 0.22, 0.045, 0.03, FAN_RED, outline=True)
    _obox(c, hand[0] + direction[0] * 0.17, hand[1] + direction[1] * 0.17, hand[2] + direction[2] * 0.17, direction, 0.05, 0.048, 0.034, COLOR_GOLD, outline=False)


def draw_fans(c, arm_l, arm_r):
    """Direita: leque aberto erguido ao lado do rosto (como no conceito). Esquerda: leque fechado na cintura.
    No ataque os dois abrem e varrem para fora."""
    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    if c.is_melee:
        p = c.atk_progress
        sweep = max(0.0, min(1.0, (p - 0.25) / 0.5))
        for hand, side in ((arm_l, 1.0), (arm_r, -1.0)):
            spine = (px * side * (0.3 + 0.9 * sweep) + fx * 0.3, py * side * (0.3 + 0.9 * sweep) + fy * 0.3, 0.9 - 0.7 * sweep)
            normal = (0.0, 0.0, 1.0) if sweep > 0.5 else (-fy, fx, 0.0)
            _open_fan(c, hand, spine, normal, spread=1.0 + 0.3 * sweep)
    else:
        _open_fan(c, arm_r, (px * -0.25 + fx * 0.15, py * -0.25 + fy * 0.15, 1.0), (-fy, fx, 0.0))
        _closed_fan(c, arm_l, _norm((fx * 0.35 + px * 0.65, fy * 0.35 + py * 0.65, -0.12)))


def idle_arms(base_x, base_y, tz, fx, fy, px, py):
    """Postura neutra: direita ergue o leque aberto junto ao rosto, esquerda segura o leque fechado baixo e cruzado."""
    arm_r = (base_x + fx * 0.07 - px * 0.14, base_y + fy * 0.07 - py * 0.14, tz + 0.30)
    arm_l = (base_x + fx * 0.11 + px * 0.07, base_y + fy * 0.11 + py * 0.07, tz - 0.03)
    return arm_l, arm_r


def attack_arms(c):
    """Antecipação (braços cruzados no peito), varredura (os dois leques abrem para fora) e acompanhamento (braços abertos)."""
    bx, by, tz, fx, fy, px, py, p = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py, c.atk_progress
    cross = 1.0 - max(0.0, min(1.0, p / 0.25))
    sweep = max(0.0, min(1.0, (p - 0.25) / 0.5))
    reach = 0.12 + 0.20 * sweep
    lateral = (-0.05 * cross) + 0.36 * sweep
    z = tz + 0.22 - 0.05 * sweep
    arm_l = (bx + fx * reach + px * lateral, by + fy * reach + py * lateral, z)
    arm_r = (bx + fx * reach - px * lateral, by + fy * reach - py * lateral, z + 0.02)
    return arm_l, arm_r
