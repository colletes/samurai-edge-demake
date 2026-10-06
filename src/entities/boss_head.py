"""
Cabeça do Oni Gashadokuro: caveira ameaçadora com kabuto (elmo samurai) de ferro escuro, mempo de olhos em brasa,
cristal dourado (maedate) e chifres curvos. Tudo é montado uma vez em voxels pequenos (coordenadas locais: f frente,
s esquerda, h cima, com a origem no centro do crânio) e depois só transformado para o mundo a cada quadro.
"""
import math

import pygame

BONE_TONES = ((228, 218, 190), (214, 203, 172), (196, 184, 154))
BONE_BROW = (150, 138, 112)
SOCKET = (34, 18, 16)
TOOTH = (238, 232, 208)
GAP = (44, 32, 30)
EYE_CORE = (255, 64, 36)
EYE_SPARK = (255, 200, 130)
BRONZE, BRONZE_DARK = (142, 110, 58), (104, 82, 46)
BRIM, BRIM_EDGE = (150, 132, 66), (196, 164, 64)
GOLD, GOLD_LIGHT, GOLD_DARK = (214, 170, 50), (244, 206, 84), (152, 112, 30)
GUARD_A, GUARD_B, GUARD_TRIM = (112, 76, 46), (176, 102, 52), (206, 130, 60)
HORN, HORN_RIDGE = (72, 62, 48), (100, 86, 62)
CORD = (176, 72, 44)

EYE_CENTER = (0.34, 0.2, 0.08)  # f, |s|, h (antes de SCALE)
SCALE = 1.3  # a cabeça é maior que um crânio comum, mas os voxels continuam pequenos (mais cubos, não cubos maiores)


def _noise(i: int, j: int, k: int) -> int:
    return ((i * 73856093) ^ (j * 19349663) ^ (k * 83492791)) & 0xFF


def _shell(cells: dict, v: float) -> list:
    out = []
    for (i, j, k), color in cells.items():
        if ((i + 1, j, k) not in cells or (i - 1, j, k) not in cells or (i, j + 1, k) not in cells
                or (i, j - 1, k) not in cells or (i, j, k + 1) not in cells or (i, j, k - 1) not in cells):
            out.append((i * v, j * v, k * v, v, color))
    return out


def _fill(v: float, f_rng, s_rng, h_rng, fn) -> dict:
    cells = {}
    inv = 1.0 / SCALE
    for i in range(int(f_rng[0] * SCALE / v), int(f_rng[1] * SCALE / v) + 1):
        for j in range(int(s_rng[0] * SCALE / v), int(s_rng[1] * SCALE / v) + 1):
            for k in range(int(h_rng[0] * SCALE / v), int(h_rng[1] * SCALE / v) + 1):
                c = fn(i * v * inv, j * v * inv, k * v * inv)
                if c is not None:
                    cells[(i, j, k)] = c
    return cells


def _spheres(v: float, spheres, color_fn) -> dict:
    """União de esferas (cx, cy, cz, r) no grid de passo `v`; `color_fn(f, s, h, índice)` escolhe a cor."""
    cells = {}
    for n, (cx, cy, cz, r) in enumerate(spheres):
        cx, cy, cz, r = cx * SCALE, cy * SCALE, cz * SCALE, r * SCALE
        cells[(round(cx / v), round(cy / v), round(cz / v))] = color_fn(cx, cy, cz, n)  # esferas finas sempre deixam 1 cubo
        for i in range(int((cx - r) / v) - 1, int((cx + r) / v) + 2):
            for j in range(int((cy - r) / v) - 1, int((cy + r) / v) + 2):
                for k in range(int((cz - r) / v) - 1, int((cz + r) / v) + 2):
                    if (i * v - cx) ** 2 + (j * v - cy) ** 2 + (k * v - cz) ** 2 <= r * r:
                        cells[(i, j, k)] = color_fn(i * v, j * v, k * v, n)
    return cells


# ---------------------------------------------------------------------------------------------- partes
def _helmet_h_min(f: float) -> float:
    return 0.22 - 0.43 * max(0.0, min(1.0, (0.25 - f) / 0.8))


def _inside_helmet(f: float, s: float, h: float, grow: float = 0.0) -> bool:
    e = ((f + 0.08) / (0.66 + grow)) ** 2 + (s / (0.62 + grow)) ** 2 + ((h - 0.06) / (0.62 + grow)) ** 2
    return e <= 1.0 and h >= _helmet_h_min(f)


def _skull(f, s, h):
    if _inside_helmet(f, s, h, 0.04):
        return None
    sa = abs(s)
    sock = math.sqrt((f - 0.42) ** 2 + (sa - 0.2) ** 2 + (h - 0.08) ** 2)
    if sock < 0.15:
        return None
    if f > 0.4 and abs(s) < 0.07 and -0.24 < h < -0.07:  # cavidade nasal
        return None
    solid = ((f + 0.05) / 0.58) ** 2 + (s / 0.5) ** 2 + ((h - 0.05) / 0.55) ** 2 <= 1.0
    if not solid and 0.0 <= f <= 0.52 and -0.42 <= h <= 0.02 and sa <= 0.3 - 0.3 * max(0.0, f - 0.2):
        solid = True
    if not solid and math.sqrt((f - 0.34) ** 2 + (sa - 0.3) ** 2 + (h + 0.12) ** 2) <= 0.12:  # maçã do rosto
        solid = True
    if not solid and 0.3 <= f <= 0.56 and sa <= 0.38 and 0.13 <= h <= 0.24 - 0.09 * (1.0 - sa / 0.38):  # sobrancelha pesada
        return BONE_BROW
    if not solid:
        return None
    if sock < 0.25:
        return SOCKET
    if f > 0.36 and h < -0.33:
        return TOOTH if round(s / 0.1) % 2 == 0 else GAP
    n = _noise(int(f * 40), int(s * 40), int(h * 40))
    return BONE_BROW if n < 14 else BONE_TONES[n % 3]


def _bowl(f, s, h):
    if not _inside_helmet(f, s, h):
        return None
    rim = _helmet_h_min(f)
    if h < rim + 0.12:
        return GOLD
    if h > 0.6 and f * f + s * s < 0.02:
        return GOLD_LIGHT
    band = int((math.atan2(s, f + 0.08) + math.pi) / (math.pi / 10.0))
    return BRONZE if (band + int((h - rim) / 0.14)) % 2 == 0 else BRONZE_DARK


def _brim(f, s, h):
    u = (f - 0.3) / 0.26
    if u < 0.0 or u > 1.0:
        return None
    s_max = 0.5 * math.sqrt(1.0 - u * u)
    if abs(s) > s_max:
        return None
    hc = 0.28 + 0.3 * (f - 0.3) - 0.1 * (s / 0.58) ** 2
    if abs(h - hc) > 0.05:
        return None
    return BRIM_EDGE if abs(s) > s_max - 0.1 or u > 0.88 else BRIM


def _shikoro(f, s, h):
    if f > 0.08 or not -0.78 <= h <= 0.1:
        return None
    k = 1.0 + (0.1 - h) * 0.55
    a, b = 0.66 * k, 0.66 * k
    e = (f + 0.08) ** 2 / (a * a) + s * s / (b * b)
    if not 0.65 <= e <= 1.0:
        return None
    tier = int((0.1 - h) / 0.15)
    if (0.1 - h) % 0.15 < 0.06:
        return GUARD_TRIM
    return GUARD_A if tier % 2 == 0 else GUARD_B


def _wing(sign):
    def fn(f, s, h):
        s = s * sign
        if not -0.1 <= f <= 0.42 or not -0.22 <= h <= 0.2 + 0.1 * f:
            return None
        if abs(s - (0.62 + 0.5 * (f + 0.1))) > 0.07:
            return None
        if abs(h - (0.2 + 0.1 * f)) < 0.08:
            return GOLD
        stud = (round(f / 0.14) + round(h / 0.14)) % 3 == 0 and abs(f / 0.14 - round(f / 0.14)) < 0.15
        return (200, 70, 40) if stud else GUARD_B
    return fn


def _horn_cells(sign: int) -> dict:
    sph = []
    for n in range(30):
        t = n / 29.0
        f = -0.12 - 0.3 * t
        s = sign * (0.5 + 0.8 * t ** 0.9)
        h = 0.1 + 1.25 * t ** 1.4
        sph.append((f, s, h, 0.2 * (1.0 - t) ** 0.8 + 0.08))

    def color(f, s, h, n):
        t = n / 29.0
        if t < 0.07:
            return GOLD
        return HORN_RIDGE if int(t * 15) % 2 == 0 else HORN
    return _spheres(0.15, sph, color)


def _crest_cells() -> dict:
    """Maedate dourado: medalhão, crescente e duas hastes curvas, inclinados para trás seguindo a testa do elmo."""
    sph = []

    def fc(h):
        return 0.5 - 0.4 * max(0.0, h - 0.5)

    def add(s, h, r):
        sph.append((fc(h), s, h, r))

    for a in range(0, 24):  # medalhão em anel
        ang = a / 24 * math.tau
        add(0.18 * math.cos(ang), 0.86 + 0.18 * math.sin(ang), 0.04)
    add(0.0, 0.86, 0.065)
    for a in range(0, 15):  # crescente sob o medalhão
        ang = math.pi + a / 14 * math.pi
        add(0.45 * math.cos(ang), 0.8 + 0.45 * math.sin(ang), 0.065)
    for sign in (-1, 1):  # hastes douradas que sobem e se curvam para fora
        for n in range(14):
            u = n / 13.0
            add(sign * (0.45 + 0.28 * math.sin(u * 1.4)), 0.8 + 0.6 * u, 0.06 + 0.03 * u)
        add(sign * 0.6, 1.42, 0.1)
        add(sign * 0.5, 1.37, 0.07)

    def color(f, s, h, n):
        return GOLD_LIGHT if (round(h / 0.09) + round(s / 0.09)) % 4 == 0 else (GOLD_DARK if n % 5 == 0 else GOLD)
    return _spheres(0.09, sph, color)


def _cord_cells() -> dict:
    sph = []
    for sign in (-1, 1):
        for n in range(10):
            u = n / 9.0
            sph.append((0.0 + 0.3 * u, sign * (0.56 - 0.36 * u), -0.22 - 0.55 * u, 0.05))
        sph.append((0.3, sign * 0.12, -0.95, 0.1))  # laço
        for n in range(8):
            u = n / 7.0
            sph.append((0.3, sign * (0.06 + 0.06 * u), -1.0 - 0.3 * u, 0.045))
    sph.append((0.3, 0.0, -0.95, 0.09))
    return _spheres(0.09, sph, lambda f, s, h, n: CORD)


def _jaw_cells() -> dict:
    """Mandíbula em U ao redor do centro do osso `jaw`; os ramos até a articulação são desenhados à parte."""
    v = 0.09
    cells = {}
    for n in range(23):
        phi = math.radians(-100 + 200 * n / 22.0)
        f, s = (0.2 * math.cos(phi) - 0.05) * SCALE, 0.34 * math.sin(phi) * SCALE
        base = (round(f / v), round(s / v))
        for dk in (-1, 0):
            cells[(base[0], base[1], dk)] = BONE_TONES[(n + dk) % 3]
        if abs(phi) < math.radians(62) and n % 2 == 0:
            cells[(base[0], base[1], 1)] = TOOTH
    return cells


def _build():
    parts = []
    parts += _shell(_fill(0.1, (-0.62, 0.62), (-0.62, 0.62), (-0.66, 0.66), _skull), 0.1)
    parts += _shell(_fill(0.12, (-0.8, 0.8), (-0.8, 0.8), (-0.3, 0.8), _bowl), 0.12)
    parts += _shell(_fill(0.1, (0.2, 0.7), (-0.65, 0.65), (0.0, 0.5), _brim), 0.1)
    parts += _shell(_fill(0.12, (-1.1, 0.1), (-1.1, 1.1), (-0.8, 0.2), _shikoro), 0.12)
    for sign in (-1, 1):
        parts += _shell(_fill(0.1, (-0.15, 0.45), (-1.1, 1.1), (-0.3, 0.35), _wing(sign)), 0.1)
        parts += _shell(_horn_cells(sign), 0.15)
    parts += _shell(_crest_cells(), 0.09)
    parts += _shell(_cord_cells(), 0.09)
    for sign in (-1, 1):
        ef, es, eh = (c * SCALE for c in EYE_CENTER)
        parts.append((ef, sign * es, eh, 0.19, EYE_CORE))
        parts.append((ef + 0.09, sign * es, eh + 0.03, 0.07, EYE_SPARK))
    jaw = _shell(_jaw_cells(), 0.09)
    return parts, jaw


HEAD_VOXELS, JAW_VOXELS = _build()
JAW_MID = (0.33 * SCALE, 0.0, -0.55 * SCALE)  # centro da mandíbula fechada, relativo ao centro do crânio
JAW_ENDS = tuple((-0.085 * SCALE, sg * 0.335 * SCALE, 0.0) for sg in (-1, 1))  # onde os ramos saem da mandíbula (f, s, h locais do jaw)
HINGE = tuple((0.0, sg * 0.36 * SCALE, -0.1 * SCALE) for sg in (-1, 1))         # articulação no crânio (f, s, h locais do crânio)
HEAD_MIN_H = min(h - size / 2.0 for _, _, h, size, _ in HEAD_VOXELS)


def head_yaw(skull, eye_l, eye_r, fallback=(1.0, 0.0)):
    """Direção horizontal do rosto (do centro do crânio para o ponto médio dos olhos)."""
    fx, fy = (eye_l[0] + eye_r[0]) / 2.0 - skull[0], (eye_l[1] + eye_r[1]) / 2.0 - skull[1]
    n = math.hypot(fx, fy)
    return (fx / n, fy / n) if n > 1e-4 else fallback


def head_cubes(skull, jaw_mid, yaw):
    """Cubos da cabeça no mundo, (x, y, z, tamanho, cor), e o centro do crânio já erguido. Cabeça no chão repousa no kabuto."""
    fx, fy = yaw
    ox, oy, oz = skull
    lift = max(0.0, 0.02 - (oz + HEAD_MIN_H))
    oz += lift
    out = [(ox + f * fx - s * fy, oy + f * fy + s * fx, oz + h, size, color) for f, s, h, size, color in HEAD_VOXELS]
    jx, jy, jz = jaw_mid
    jz += lift
    out += [(jx + f * fx - s * fy, jy + f * fy + s * fx, jz + h, size, color) for f, s, h, size, color in JAW_VOXELS]
    for (jf, js, jh), (hf, hs, hh) in zip(JAW_ENDS, HINGE):  # ramos da mandíbula esticam até a articulação
        a = (jx + jf * fx - js * fy, jy + jf * fy + js * fx, jz + jh)
        b = (ox + hf * fx - hs * fy, oy + hf * fy + hs * fx, oz + hh)
        n = max(2, int(math.dist(a, b) / 0.08))
        out += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n, a[2] + (b[2] - a[2]) * i / n, 0.09, BONE_TONES[i % 3])
                for i in range(n + 1)]
    return out, (ox, oy, oz)


_glow_cache: dict = {}


def draw_eye_glow(surface, camera, skull, yaw, t: float):
    """Brilho vermelho aditivo sobre os olhos (pulsa de leve)."""
    zoom = getattr(camera, "zoom", 1.0)
    radius = max(5, int((11 + 2 * math.sin(t * 7.0)) * zoom))
    spr = _glow_cache.get(radius)
    if spr is None:
        spr = pygame.Surface((radius * 2, radius * 2))
        for r in range(radius, 0, -2):
            k = (1.0 - r / radius) ** 2
            pygame.draw.circle(spr, (int(150 * k), int(26 * k), int(10 * k)), (radius, radius), r)
        _glow_cache[radius] = spr
    fx, fy = yaw
    for sign in (-1, 1):
        f, s, h = (EYE_CENTER[0] + 0.1) * SCALE, sign * EYE_CENTER[1] * SCALE, EYE_CENTER[2] * SCALE
        x, y, z = skull[0] + f * fx - s * fy, skull[1] + f * fy + s * fx, skull[2] + h
        px, py = camera.apply(x, y, z)
        surface.blit(spr, (px - radius, py - radius), special_flags=pygame.BLEND_RGB_ADD)
