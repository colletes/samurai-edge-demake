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
HORN, HORN_RIDGE = (45, 38, 32), (75, 62, 50)
CORD = (176, 72, 44)

EYE_CENTER = (0.30, 0.17, 0.05)  # f, |s|, h (antes de SCALE)
SCALE = 0.88  # Escala proporcional de titã esqueleto colossal (sem efeito chibi/cabeçudo)


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


# ---------------------------------------------------------------------------------------------- elmo Kabuto e crânio Oni
def _helmet_h_min(f: float) -> float:
    return 0.14 - 0.32 * max(0.0, min(1.0, (0.22 - f) / 0.6))


def _inside_helmet(f: float, s: float, h: float, grow: float = 0.0) -> bool:
    e = ((f + 0.05) / (0.50 + grow)) ** 2 + (s / (0.44 + grow)) ** 2 + ((h - 0.02) / (0.46 + grow)) ** 2
    return e <= 1.0 and h >= _helmet_h_min(f)


def _skull(f, s, h):
    if _inside_helmet(f, s, h, 0.02):
        return None
    sa = abs(s)
    # Órbitas oculares fundas
    sock = math.sqrt((f - 0.36) ** 2 + (sa - 0.17) ** 2 + (h - 0.05) ** 2)
    if sock < 0.14:
        return None
    # Cavidade nasal
    if f > 0.32 and abs(s) < 0.055 and -0.22 < h < -0.06:
        return None

    # Abóbada craniana completa e sólida sob o elmo
    solid = ((f + 0.02) / 0.50) ** 2 + (s / 0.42) ** 2 + ((h + 0.02) / 0.46) ** 2 <= 1.0

    # Maçãs do rosto (arcos zigomáticos)
    if not solid and math.sqrt((f - 0.26) ** 2 + (sa - 0.25) ** 2 + (h + 0.08) ** 2) <= 0.12:
        solid = True
    # Maxila e dentes superiores
    if not solid and 0.0 <= f <= 0.42 and -0.36 <= h <= 0.0 and sa <= 0.25 - 0.20 * max(0.0, f - 0.15):
        solid = True
    # Arcada supraciliar pesada e ameaçadora
    if not solid and 0.22 <= f <= 0.46 and sa <= 0.30 and 0.08 <= h <= 0.20 - 0.06 * (1.0 - sa / 0.30):
        return BONE_BROW

    if not solid:
        return None

    if sock < 0.22:
        return SOCKET

    # Dentes da maxila
    if f > 0.30 and h < -0.26:
        return TOOTH if round(s / 0.08) % 2 == 0 else GAP

    # Textura de osso antigo envelhecido
    n = _noise(int(f * 40), int(s * 40), int(h * 40))
    return BONE_BROW if n < 18 else BONE_TONES[n % 3]


def _bowl(f, s, h):
    """Cúpula de ferro forjado do elmo samurai Kabuto com anéis e rebites."""
    if not _inside_helmet(f, s, h):
        return None
    rim = _helmet_h_min(f)
    if h < rim + 0.08:
        return GOLD
    if h > 0.45 and f * f + s * s < 0.015:
        return GOLD_LIGHT
    band = int((math.atan2(s, f + 0.05) + math.pi) / (math.pi / 8.0))
    return (52, 48, 50) if (band + int((h - rim) / 0.10)) % 2 == 0 else (36, 33, 35)


def _brim(f, s, h):
    """Aba frontal (Mabizashi) laqueada em preto com friso dourado."""
    u = (f - 0.22) / 0.22
    if u < 0.0 or u > 1.0:
        return None
    s_max = 0.38 * math.sqrt(max(0.0, 1.0 - u * u))
    if abs(s) > s_max:
        return None
    hc = 0.18 + 0.16 * (f - 0.22) - 0.08 * (s / 0.42) ** 2
    if abs(h - hc) > 0.045:
        return None
    return (185, 145, 55) if abs(s) > s_max - 0.06 or u > 0.85 else (42, 38, 40)


def _shikoro(f, s, h):
    """Protetores de nuca (Shikoro) em lâminas escalonadas compactas."""
    if f > 0.04 or not -0.55 <= h <= 0.10:
        return None
    k = 1.0 + (0.10 - h) * 0.32
    a, b = 0.50 * k, 0.46 * k
    e = (f + 0.05) ** 2 / (a * a) + s * s / (b * b)
    if not 0.72 <= e <= 1.0:
        return None
    tier = int((0.10 - h) / 0.11)
    if (0.10 - h) % 0.11 < 0.04:
        return (165, 125, 55)
    return (58, 48, 46) if tier % 2 == 0 else (85, 68, 58)


def _wing(sign):
    """Abas laterais (Fukikaeshi) do elmo dobradas discretamente contra o crânio."""
    def fn(f, s, h):
        s_val = s * sign
        if not -0.05 <= f <= 0.28 or not -0.10 <= h <= 0.18 + 0.08 * f:
            return None
        if abs(s_val - (0.42 + 0.22 * (f + 0.05))) > 0.055:
            return None
        if abs(h - (0.16 + 0.08 * f)) < 0.05:
            return GOLD
        return (85, 68, 58)
    return fn


def _horn_cells(sign: int) -> dict:
    """Chifres demoníacos curvados de Oni que emergem da arcada e recurvam para trás."""
    sph = []
    for n in range(24):
        t = n / 23.0
        f = 0.12 - 0.34 * (t ** 1.1)
        s = sign * (0.36 + 0.34 * (t ** 0.85))
        h = 0.18 + 0.78 * (t ** 0.95)
        r = 0.10 * (1.0 - t * 0.75)
        sph.append((f, s, h, r))

    def color(f, s, h, n):
        t = n / 23.0
        if t > 0.82:
            return (28, 22, 20)
        return HORN_RIDGE if (int(t * 14) % 2 == 0) else HORN
    return _spheres(0.08, sph, color)


def _crest_cells() -> dict:
    """Maedate de ouro esculpido no elmo: medalhão e crescente dourado compacto na fronte."""
    sph = []

    def fc(h):
        return 0.38 - 0.28 * max(0.0, h - 0.32)

    def add(s, h, r):
        sph.append((fc(h), s, h, r))

    for a in range(16):
        ang = a / 16.0 * math.tau
        add(0.10 * math.cos(ang), 0.50 + 0.10 * math.sin(ang), 0.035)
    add(0.0, 0.50, 0.05)
    for a in range(12):
        ang = math.pi + a / 11.0 * math.pi
        add(0.26 * math.cos(ang), 0.46 + 0.26 * math.sin(ang), 0.045)
    for sign in (-1, 1):
        for n in range(10):
            u = n / 9.0
            add(sign * (0.24 + 0.16 * math.sin(u * 1.3)), 0.46 + 0.38 * u, 0.04 + 0.02 * u)
        add(sign * 0.38, 0.86, 0.06)

    def color(f, s, h, n):
        return GOLD_LIGHT if n % 4 == 0 else (GOLD_DARK if n % 3 == 0 else GOLD)
    return _spheres(0.08, sph, color)


def _jaw_cells() -> dict:
    """Mandíbula em U com dentes pontiagudos."""
    v = 0.07
    cells = {}
    for n in range(21):
        phi = math.radians(-95 + 190 * n / 20.0)
        f, s = (0.18 * math.cos(phi) - 0.04) * SCALE, 0.27 * math.sin(phi) * SCALE
        base = (round(f / v), round(s / v))
        for dk in (-1, 0):
            cells[(base[0], base[1], dk)] = BONE_TONES[(n + dk) % 3]
        if abs(phi) < math.radians(65) and n % 2 == 0:
            cells[(base[0], base[1], 1)] = TOOTH
    return cells


def _build():
    parts = []
    # Crânio esculpido de marfim e osso ancestral completo
    parts += _shell(_fill(0.08, (-0.52, 0.52), (-0.46, 0.46), (-0.48, 0.52), _skull), 0.08)
    # Cúpula de ferro do elmo Kabuto
    parts += _shell(_fill(0.09, (-0.60, 0.60), (-0.52, 0.52), (-0.20, 0.60), _bowl), 0.09)
    # Aba frontal com borda dourada
    parts += _shell(_fill(0.08, (0.15, 0.52), (-0.48, 0.48), (0.0, 0.38), _brim), 0.08)
    # Protetor de nuca (Shikoro)
    parts += _shell(_fill(0.09, (-0.75, 0.08), (-0.68, 0.68), (-0.58, 0.15), _shikoro), 0.09)
    # Abas laterais e Chifres demoníacos curvados de Oni
    for sign in (-1, 1):
        parts += _shell(_fill(0.08, (-0.08, 0.32), (-0.62, 0.62), (-0.15, 0.25), _wing(sign)), 0.08)
        parts += _shell(_horn_cells(sign), 0.08)
    # Maedate dourado: crescente na fronte
    parts += _shell(_crest_cells(), 0.08)
    # Órbitas oculares com núcleo espectral
    for sign in (-1, 1):
        ef, es, eh = (c * SCALE for c in EYE_CENTER)
        parts.append((ef, sign * es, eh, 0.14, EYE_CORE))
        parts.append((ef + 0.06, sign * es, eh + 0.02, 0.06, EYE_SPARK))
    jaw = _shell(_jaw_cells(), 0.07)
    return parts, jaw


HEAD_VOXELS, JAW_VOXELS = _build()
JAW_MID = (0.28 * SCALE, 0.0, -0.40 * SCALE)  # centro da mandíbula fechada, relativo ao centro do crânio
JAW_ENDS = tuple((-0.07 * SCALE, sg * 0.27 * SCALE, 0.0) for sg in (-1, 1))  # onde os ramos saem da mandíbula
HINGE = tuple((0.0, sg * 0.27 * SCALE, -0.08 * SCALE) for sg in (-1, 1))     # articulação no crânio
HEAD_MIN_H = min(h - size / 2.0 for _, _, h, size, _ in HEAD_VOXELS)


def head_yaw(skull, eye_l, eye_r, fallback=(1.0, 0.0)):
    """Direção horizontal do rosto (do centro do crânio para o ponto médio dos olhos)."""
    fx, fy = (eye_l[0] + eye_r[0]) / 2.0 - skull[0], (eye_l[1] + eye_r[1]) / 2.0 - skull[1]
    n = math.hypot(fx, fy)
    return (fx / n, fy / n) if n > 1e-4 else fallback


def head_cubes(skull, jaw_mid, yaw):
    """Cubos da cabeça no mundo, (x, y, z, tamanho, cor), e o centro do crânio já erguido."""
    fx, fy = yaw
    ox, oy, oz = skull
    lift = max(0.0, 0.02 - (oz + HEAD_MIN_H))
    oz += lift
    out = [(ox + f * fx - s * fy, oy + f * fy + s * fx, oz + h, size, color) for f, s, h, size, color in HEAD_VOXELS]
    jx, jy, jz = jaw_mid
    jz += lift
    out += [(jx + f * fx - s * fy, jy + f * fy + s * fx, jz + h, size, color) for f, s, h, size, color in JAW_VOXELS]
    for (jf, js, jh), (hf, hs, hh) in zip(JAW_ENDS, HINGE):
        a = (jx + jf * fx - js * fy, jy + jf * fy + js * fx, jz + jh)
        b = (ox + hf * fx - hs * fy, oy + hf * fy + hs * fx, oz + hh)
        n = max(2, int(math.dist(a, b) / 0.07))
        out += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n, a[2] + (b[2] - a[2]) * i / n, 0.08, BONE_TONES[i % 3])
                for i in range(n + 1)]
    return out, (ox, oy, oz)


_glow_cache: dict = {}


def draw_eye_glow(surface, camera, skull, yaw, t: float):
    """Brilho espectral roxo e carmesim aditivo com labaredas espirituais sobre os olhos."""
    zoom = getattr(camera, "zoom", 1.0)
    radius = max(5, int((9 + 2 * math.sin(t * 8.5)) * zoom))
    spr = _glow_cache.get(radius)
    if spr is None:
        spr = pygame.Surface((radius * 2, radius * 2))
        for r in range(radius, 0, -1):
            k = (1.0 - r / radius) ** 1.8
            # Gradiente de chamas espirituais: violeta cósmico na borda -> carmesim no meio -> branco no centro
            if r > radius * 0.55:
                u = (r - radius * 0.55) / (radius * 0.45)
                col = (int((140 + 60 * (1 - u)) * k), int(25 * k), int((210 + 45 * (1 - u)) * k))
            elif r > radius * 0.22:
                u = (r - radius * 0.22) / (radius * 0.33)
                col = (int((240 + 15 * (1 - u)) * k), int((40 + 30 * (1 - u)) * k), int((100 * u + 180 * (1 - u)) * k))
            else:
                col = (int(255 * k), int(220 * k), int(245 * k))
            pygame.draw.circle(spr, col, (radius, radius), r)
        _glow_cache[radius] = spr
    fx, fy = yaw
    for sign in (-1, 1):
        f, s, h = (EYE_CENTER[0] + 0.08) * SCALE, sign * EYE_CENTER[1] * SCALE, EYE_CENTER[2] * SCALE
        x, y, z = skull[0] + f * fx - s * fy, skull[1] + f * fy + s * fx, skull[2] + h
        px, py = camera.apply(x, y, z)
        surface.blit(spr, (px - radius, py - radius), special_flags=pygame.BLEND_RGB_ADD)

        # Labaredas ascendentes dinâmicas de alma (flickering wisps)
        for w_i in range(3):
            w_phase = t * 9.0 + sign * 1.5 + w_i * 2.1
            flicker_h = 0.05 + 0.05 * math.sin(w_phase)
            flicker_s = 0.02 * math.cos(w_phase * 1.3)
            fx_w, fy_w, fz_w = x - fx * 0.02 + (-fy) * flicker_s, y - fy * 0.02 + fx * flicker_s, z + flicker_h
            fl_px, fl_py = camera.apply(fx_w, fy_w, fz_w)
            fl_r = max(2, int((2.6 - w_i * 0.6) * zoom))
            fl_surf = pygame.Surface((fl_r * 2, fl_r * 2))
            fl_col = (190, 50, 240) if w_i % 2 == 0 else (255, 60, 90)
            pygame.draw.circle(fl_surf, fl_col, (fl_r, fl_r), fl_r)
            surface.blit(fl_surf, (fl_px - fl_r, fl_py - fl_r), special_flags=pygame.BLEND_RGB_ADD)
