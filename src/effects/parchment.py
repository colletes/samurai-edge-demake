"""
Fase 5.5.4 - Pergaminho Sumi-E de alta fidelidade.

Reúne os elementos visuais derivados das artes de referência (assets/concepts/concept1-3):
- backdrop: paisagem sumi-e em papel envelhecido com moldura de madeira (recortada da arte real)
- varas de pergaminho e brasão da garça (camadas de multiplicação recortadas da arte real)
- cartões/folhas de papel com bordas rasgadas, fibras e manchas (texturas calibradas pelo papel da arte)
- pincelada vermelha de destaque (pincel seco) e pétalas de cerejeira

Os PNGs são gerados por tools/build_parchment_assets.py.
"""
import math
import os
import random

import numpy as np
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, get_asset_path

ASSET_DIR = "assets/ui/parchment"

INK = (28, 22, 18)
INK_SOFT = (74, 62, 52)
SEAL_RED = (176, 38, 34)
SEAL_BLUE = (36, 78, 150)
GOLD_INK = (140, 98, 22)

_cache: dict = {}


def _load(name: str) -> pygame.Surface | None:
    key = ("img", name)
    if key in _cache:
        return _cache[key]
    path = get_asset_path(f"{ASSET_DIR}/{name}")
    surf = None
    if os.path.exists(path):
        try:
            surf = pygame.image.load(path)
            surf = surf.convert() if pygame.display.get_surface() else surf
        except Exception:
            surf = None
    _cache[key] = surf
    return surf


def get_backdrop() -> pygame.Surface | None:
    """Paisagem sumi-e em papel envelhecido, no tamanho da tela."""
    key = ("backdrop", SCREEN_WIDTH, SCREEN_HEIGHT)
    if key not in _cache:
        img = _load("backdrop.png")
        if img is not None and img.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
            img = pygame.transform.smoothscale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        _cache[key] = img
    return _cache[key]


SCENE_BG_PATH = "assets/concepts/bamboo_forest_concept.jpg"


def get_scene_background(dim: int = 110) -> pygame.Surface | None:
    """Floresta de bambu (arte conceitual) no tamanho da tela, com escurecimento e vinheta; None se ausente."""
    key = ("scene_bg", SCREEN_WIDTH, SCREEN_HEIGHT, dim)
    if key not in _cache:
        img = None
        path = get_asset_path(SCENE_BG_PATH)
        if os.path.exists(path):
            try:
                raw = pygame.image.load(path)
                raw = raw.convert() if pygame.display.get_surface() else raw
                scale = max(SCREEN_WIDTH / raw.get_width(), SCREEN_HEIGHT / raw.get_height())
                size = (math.ceil(raw.get_width() * scale), math.ceil(raw.get_height() * scale))
                scaled = pygame.transform.smoothscale(raw, size)
                img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                img.blit(scaled, ((SCREEN_WIDTH - size[0]) // 2, (SCREEN_HEIGHT - size[1]) // 2))

                shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                shade.fill((6, 10, 12, dim))
                img.blit(shade, (0, 0))
                # vinheta: escurece as bordas para conter o olhar no conteúdo
                vig = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                for i in range(60):
                    a = int(120 * (1 - i / 60) ** 2)
                    pygame.draw.rect(vig, (0, 0, 0, a), (i, i, SCREEN_WIDTH - 2 * i, SCREEN_HEIGHT - 2 * i), 1)
                img.blit(vig, (0, 0))
            except Exception:
                img = None
        _cache[key] = img
    return _cache[key]


def paper_tone() -> tuple[int, int, int]:
    """Tom do papel amostrado na própria arte (área clara do pergaminho)."""
    if "paper_tone" not in _cache:
        bg = get_backdrop()
        tone = (226, 208, 172)
        if bg is not None:
            try:
                r, g, b, _ = pygame.transform.average_color(bg, pygame.Rect(380, 600, 120, 60))
                tone = (min(255, int(r * 1.04)), min(255, int(g * 1.04)), min(255, int(b * 1.04)))
            except Exception:
                pass
        _cache["paper_tone"] = tone
    return _cache["paper_tone"]


def draw_backdrop(surface: pygame.Surface) -> bool:
    bg = get_backdrop()
    if bg is None:
        return False
    surface.blit(bg, (0, 0))
    return True


# ---------------------------------------------------------------------------
# Ruído e texturas
# ---------------------------------------------------------------------------
def _smooth_noise(rng: np.random.Generator, n: int, amp: float, period: int = 9) -> np.ndarray:
    raw = rng.normal(0, 1, n + period * 4)
    kernel = np.ones(period) / period
    sm = np.convolve(np.convolve(raw, kernel, "same"), kernel, "same")
    sm = sm[period * 2: period * 2 + n]
    return sm / (sm.std() + 1e-6) * amp


def _value_noise(rng: np.random.Generator, w: int, h: int, cell: int) -> np.ndarray:
    gw, gh = max(2, w // cell + 2), max(2, h // cell + 2)
    grid = rng.random((gw, gh)).astype(np.float32)
    small = pygame.Surface((gw, gh))
    g8 = (grid * 255).astype(np.uint8)
    pygame.surfarray.blit_array(small, np.stack([g8, g8, g8], axis=-1))
    big = pygame.transform.smoothscale(small, (gw * cell, gh * cell))
    arr = pygame.surfarray.array3d(big)[:w, :h, 0].astype(np.float32) / 255.0
    return arr - arr.mean()


def _paper_array(w: int, h: int, seed: int, ragged: tuple[bool, bool, bool, bool] = (True, True, True, True),
                 edge_amp: float = 2.4, burn: float = 0.30):
    """Devolve (rgb[w,h,3] uint8, alpha[w,h] uint8) de uma folha de papel envelhecido."""
    rng = np.random.default_rng(seed)
    base = np.array(paper_tone(), np.float32)

    tone = np.ones((w, h), np.float32)
    tone += _value_noise(rng, w, h, 46) * 0.20
    tone += _value_noise(rng, w, h, 14) * 0.10
    tone += rng.normal(0, 0.018, (w, h)).astype(np.float32)

    # fibras horizontais/verticais discretas
    for _ in range(max(4, (w * h) // 2600)):
        if rng.random() < 0.6:
            y = int(rng.integers(0, h)); x0 = int(rng.integers(0, w)); ln = int(rng.integers(8, 40))
            tone[x0:x0 + ln, y] -= rng.uniform(0.02, 0.06)
        else:
            x = int(rng.integers(0, w)); y0 = int(rng.integers(0, h)); ln = int(rng.integers(6, 28))
            tone[x, y0:y0 + ln] -= rng.uniform(0.02, 0.05)

    # manchas escuras suaves de envelhecimento
    for _ in range(max(1, (w * h) // 14000)):
        cx, cy = int(rng.integers(0, w)), int(rng.integers(0, h))
        r = int(rng.integers(10, 26))
        xs = np.arange(w)[:, None]; ys = np.arange(h)[None, :]
        d2 = ((xs - cx) ** 2 + (ys - cy) ** 2) / float(r * r)
        tone -= np.exp(-d2) * rng.uniform(0.03, 0.08)

    # contorno com bordas rasgadas (apenas nos lados pedidos)
    top = _smooth_noise(rng, w, edge_amp) + edge_amp * 1.2 if ragged[0] else np.zeros(w)
    bottom = _smooth_noise(rng, w, edge_amp) + edge_amp * 1.2 if ragged[1] else np.zeros(w)
    left = _smooth_noise(rng, h, edge_amp) + edge_amp * 1.2 if ragged[2] else np.zeros(h)
    right = _smooth_noise(rng, h, edge_amp) + edge_amp * 1.2 if ragged[3] else np.zeros(h)
    xs = np.arange(w)[:, None]; ys = np.arange(h)[None, :]
    dist = np.minimum.reduce([
        ys - top[:, None],
        (h - 1 - bottom[:, None]) - ys,
        xs - left[None, :],
        (w - 1 - right[None, :]) - xs,
    ])
    alpha = np.clip(dist + 0.5, 0.0, 1.0)

    # escurecimento nas bordas (papel queimado/oxidado)
    edge = np.clip(1.0 - dist / 11.0, 0.0, 1.0)
    tone *= 1.0 - burn * edge ** 1.5

    rgb = np.clip(tone[..., None] * base[None, None, :], 0, 255).astype(np.uint8)
    return rgb, (alpha * 255).astype(np.uint8)


def make_paper(w: int, h: int, seed: int = 1, **kw) -> pygame.Surface:
    """Folha de papel (SRCALPHA) com bordas rasgadas; em cache por (w, h, seed)."""
    key = ("paper", w, h, seed, tuple(sorted(kw.items())))
    if key in _cache:
        return _cache[key]
    rgb, alpha = _paper_array(w, h, seed, **kw)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.surfarray.blit_array(surf, rgb)
    pygame.surfarray.pixels_alpha(surf)[:] = alpha
    _cache[key] = surf
    return surf


def _soft_shadow(alpha_src: pygame.Surface, blur: int = 6, opacity: int = 90) -> pygame.Surface:
    key = ("shadow", id(alpha_src), blur, opacity)
    if key in _cache:
        return _cache[key]
    w, h = alpha_src.get_size()
    a = pygame.surfarray.array_alpha(alpha_src)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    sh.fill((20, 12, 6, 0))
    pygame.surfarray.pixels_alpha(sh)[:] = (a.astype(np.float32) * (opacity / 255.0)).astype(np.uint8)
    small = pygame.transform.smoothscale(sh, (max(1, w // blur), max(1, h // blur)))
    out = pygame.transform.smoothscale(small, (w, h))
    _cache[key] = out
    return out


def draw_paper_card(surface: pygame.Surface, rect: pygame.Rect, seed: int = 1, shadow: bool = True):
    paper = make_paper(rect.width, rect.height, seed)
    if shadow:
        surface.blit(_soft_shadow(paper), (rect.x + 3, rect.y + 5))
    surface.blit(paper, rect.topleft)


def make_ink_border(rect: pygame.Rect, color, width: int = 2, seed: int = 1) -> pygame.Surface:
    """Contorno de nanquim irregular para destacar o cartão selecionado."""
    key = ("inkborder", rect.w, rect.h, color, width, seed)
    if key in _cache:
        return _cache[key]
    rng = random.Random(seed)
    surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for i in range(width):
        j = lambda: rng.randint(-1, 1)
        pts = [(2 + j() + i, 2 + j() + i), (rect.w - 3 + j() - i, 2 + j() + i),
               (rect.w - 3 + j() - i, rect.h - 3 + j() - i), (2 + j() + i, rect.h - 3 + j() - i)]
        pygame.draw.lines(surf, (*color, 235 - i * 30), True, pts, 2)
    _cache[key] = surf
    return surf


# ---------------------------------------------------------------------------
# Pincelada vermelha (pincel seco)
# ---------------------------------------------------------------------------
def make_brush_stroke(w: int, h: int, color=SEAL_RED, seed: int = 3) -> pygame.Surface:
    key = ("brush", w, h, color, seed)
    if key in _cache:
        return _cache[key]
    rng = np.random.default_rng(seed)
    xn = np.linspace(0, 1, w, dtype=np.float32)[:, None]
    yn = np.linspace(0, 1, h, dtype=np.float32)[None, :]

    centre = 0.5 + 0.05 * np.sin(xn * 5.0 + seed) + _smooth_noise(rng, w, 0.015, 21)[:, None]
    half = 0.42 + _smooth_noise(rng, w, 0.05, 15)[:, None]
    taper = np.clip(xn / 0.03, 0, 1) * np.clip((1.0 - xn) / 0.30, 0.18, 1.0) ** 0.8
    half = half * (0.35 + 0.65 * taper)
    rag = _smooth_noise(rng, h, 0.04, 3)[None, :]
    inside = np.clip((half - np.abs(yn - centre) + rag * 0.5) * h * 0.7, 0, 1)

    # pincel seco: falhas horizontais crescem rumo à ponta
    rows = _smooth_noise(rng, h, 1.0, 2)[None, :]
    dry = np.clip((xn - 0.64) * 2.8, 0, 1)
    gaps = (rows > (1.2 - 1.6 * dry)).astype(np.float32)
    gaps = np.clip(1.0 - gaps * dry * 1.4, 0, 1)
    alpha = inside * gaps * (0.88 + 0.12 * np.clip(rng.normal(0, 1, (w, h)), -1, 1))

    base = np.array(color, np.float32)
    shade = 1.0 - 0.28 * np.clip((yn - 0.5) * 2, 0, 1) - 0.10 * np.abs(rng.normal(0, 1, (w, h)))
    rgb = np.clip(shade[..., None] * base[None, None, :], 0, 255).astype(np.uint8)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.surfarray.blit_array(surf, rgb)
    pygame.surfarray.pixels_alpha(surf)[:] = (np.clip(alpha, 0, 1) * 235).astype(np.uint8)
    _cache[key] = surf
    return surf


def draw_brush_highlight(surface: pygame.Surface, rect: pygame.Rect, color=SEAL_RED, seed: int = 3, alpha: int = 255):
    stroke = make_brush_stroke(rect.width, rect.height, color, seed)
    if alpha < 255:
        stroke = stroke.copy()
        stroke.set_alpha(alpha)
    surface.blit(stroke, rect.topleft)


# ---------------------------------------------------------------------------
# Varas de pergaminho (camadas de multiplicação da arte real)
# ---------------------------------------------------------------------------
def _rod(kind: str, width: int) -> pygame.Surface | None:
    key = ("rod", kind, width)
    if key in _cache:
        return _cache[key]
    src = _load(f"rod_{kind}.png")
    if src is None:
        _cache[key] = None
        return None
    sw, sh = src.get_size()
    cap = 46
    width = max(width, cap * 2 + 8)
    out = pygame.Surface((width, sh))
    out.fill((255, 255, 255))
    out.blit(src, (0, 0), pygame.Rect(0, 0, cap, sh))
    out.blit(src, (width - cap, 0), pygame.Rect(sw - cap, 0, cap, sh))
    mid = pygame.transform.smoothscale(src.subsurface(pygame.Rect(cap, 0, sw - cap * 2, sh)), (width - cap * 2, sh))
    out.blit(mid, (cap, 0))
    _cache[key] = out
    return out


def _rod_silhouette(kind: str, width: int) -> pygame.Surface | None:
    """Silhueta branca opaca da vara (do contorno escuro superior ao inferior, coluna a coluna), para ela não ficar translúcida."""
    key = ("rod_sil", kind, width)
    if key in _cache:
        return _cache[key]
    rod = _rod(kind, width)
    if rod is None:
        _cache[key] = None
        return None
    w, h = rod.get_size()
    dark = pygame.surfarray.array3d(rod).max(axis=2) < 110
    has_outline = dark.any(axis=1)
    top = np.where(has_outline, dark.argmax(axis=1), h)
    bottom = np.where(has_outline, h - 1 - dark[:, ::-1].argmax(axis=1), -1)
    # Colunas com contorno completo usam o próprio topo/base (acompanha os botões nas pontas);
    # as sem contorno (ou com só um risco) usam a envoltória de uma janela de colunas, evitando furos
    robust = has_outline & ((bottom - top) >= 12)
    top_env, bottom_env = top.copy(), bottom.copy()
    for shift in range(-14, 15):
        top_env = np.minimum(top_env, np.roll(top, shift))
        bottom_env = np.maximum(bottom_env, np.roll(bottom, shift))
    top_final = np.where(robust, top, top_env)
    bottom_final = np.where(robust, bottom, bottom_env)
    solid_cols = np.flatnonzero(robust)
    outside = (np.arange(w) < solid_cols[0]) | (np.arange(w) > solid_cols[-1])
    top_final = np.where(outside, h, top_final)
    bottom_final = np.where(outside, -1, bottom_final)
    rows = np.arange(h)[None, :]
    inside = (rows >= top_final[:, None]) & (rows <= bottom_final[:, None])
    sil = pygame.Surface((w, h), pygame.SRCALPHA)
    sil.fill((255, 255, 255, 0))
    pygame.surfarray.pixels_alpha(sil)[:] = np.where(inside, 255, 0).astype(np.uint8)
    _cache[key] = sil
    return sil


def draw_rod(surface: pygame.Surface, kind: str, center_x: int, y: int, width: int):
    rod = _rod(kind, width)
    if rod is None:
        pygame.draw.rect(surface, (92, 64, 38), (center_x - width // 2, y + 20, width, 18), border_radius=8)
        return
    pos = (center_x - rod.get_width() // 2, y)
    sil = _rod_silhouette(kind, width)
    if sil is not None:
        surface.blit(sil, pos)
    surface.blit(rod, pos, special_flags=pygame.BLEND_RGB_MULT)


def rod_height() -> int:
    r = _rod("bottom", 200)
    return r.get_height() if r else 40


def draw_scroll(surface: pygame.Surface, rect: pygame.Rect, seed: int = 11, rod_top: bool = False):
    """Pergaminho horizontal: folha rasgada acima e vara enrolada na base (como nas artes de referência)."""
    rh = rod_height()
    sheet = pygame.Rect(rect.x + 14, rect.y, rect.width - 28, rect.height - rh // 2)
    paper = make_paper(sheet.width, sheet.height, seed, ragged=(True, False, False, False))
    surface.blit(_soft_shadow(paper), (sheet.x + 3, sheet.y + 5))
    surface.blit(paper, sheet.topleft)
    draw_rod(surface, "bottom", rect.centerx, rect.bottom - rh, rect.width)
    if rod_top:
        draw_rod(surface, "top", rect.centerx, rect.y - rh // 2, rect.width)


def prewarm(card_sizes: list[tuple[int, int, int]]):
    """Gera as texturas pesadas durante o carregamento para evitar travadas na primeira renderização."""
    if get_backdrop() is None:
        return
    for w, h, seed in card_sizes:
        make_paper(w, h, seed)
    make_paper(912, 116 - rod_height() // 2, 21, ragged=(True, False, False, False))
    _rod("bottom", 940)
    make_brush_stroke(520, 46, SEAL_RED, 9)


def fit_text(font: pygame.font.Font, text: str, color, max_w: int) -> pygame.Surface:
    """Renderiza o texto encurtando com '...' se passar da largura máxima."""
    surf = font.render(text, True, color)
    if surf.get_width() <= max_w:
        return surf
    while len(text) > 1 and font.size(text + "...")[0] > max_w:
        text = text[:-1]
    return font.render(text.rstrip() + "...", True, color)


def draw_crest(surface: pygame.Surface, x: int, y: int, scale: float = 0.8):
    crest = _load("crane_crest.png")
    if crest is None:
        return
    key = ("crest", scale)
    if key not in _cache:
        w, h = crest.get_size()
        _cache[key] = pygame.transform.smoothscale(crest, (int(w * scale), int(h * scale)))
    surface.blit(_cache[key], (x, y), special_flags=pygame.BLEND_RGB_MULT)


# ---------------------------------------------------------------------------
# Texto em nanquim
# ---------------------------------------------------------------------------
def render_ink(font: pygame.font.Font, text: str, color=INK) -> pygame.Surface:
    """Texto com halo claro de papel para ler bem sobre a pintura."""
    core = font.render(text, True, color)
    halo = font.render(text, True, (*paper_tone(),))
    out = pygame.Surface((core.get_width() + 2, core.get_height() + 2), pygame.SRCALPHA)
    for dx, dy in ((0, 0), (2, 0), (0, 2), (2, 2), (1, 0), (1, 2), (0, 1), (2, 1)):
        h = halo.copy()
        h.set_alpha(150)
        out.blit(h, (dx, dy))
    out.blit(core, (1, 1))
    return out


def darken(color, factor: float = 0.55) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in color[:3])


# ---------------------------------------------------------------------------
# Pétalas de cerejeira
# ---------------------------------------------------------------------------
class PetalField:
    """Pétalas caindo com balanço e rotação."""

    def __init__(self, count: int = 26, seed: int = 5):
        self.rng = random.Random(seed)
        self.petals = [self._new(initial=True) for _ in range(count)]
        self._sprites: dict = {}

    def _new(self, initial: bool = False) -> dict:
        r = self.rng
        return {
            "x": r.uniform(0, SCREEN_WIDTH),
            "y": r.uniform(-20, SCREEN_HEIGHT) if initial else r.uniform(-40, -8),
            "vy": r.uniform(22, 48),
            "vx": r.uniform(-14, 10),
            "phase": r.uniform(0, 6.28),
            "sway": r.uniform(10, 26),
            "rot": r.uniform(0, 360),
            "spin": r.uniform(-90, 90),
            "size": r.choice((9, 11, 13)),
            "shade": r.choice((0, 1, 2)),
        }

    def _sprite(self, size: int, shade: int) -> pygame.Surface:
        key = (size, shade)
        if key not in self._sprites:
            fills = ((246, 202, 212), (238, 178, 196), (250, 222, 226))
            surf = pygame.Surface((size + 4, size + 4), pygame.SRCALPHA)
            c = (size + 4) / 2
            pts = []
            for i in range(14):
                a = i / 14 * 2 * math.pi
                rx, ry = size / 2, size / 3.0
                bump = 1.0 - 0.28 * max(0.0, math.cos(a)) ** 6  # entalhe na ponta da pétala
                pts.append((c + math.cos(a) * rx * bump, c + math.sin(a) * ry))
            pygame.draw.polygon(surf, (*fills[shade], 235), pts)
            pygame.draw.polygon(surf, (196, 118, 140, 200), pts, 1)
            self._sprites[key] = surf
        return self._sprites[key]

    def update(self, dt: float):
        for i, p in enumerate(self.petals):
            p["phase"] += dt * 1.8
            p["y"] += p["vy"] * dt
            p["x"] += (p["vx"] + math.sin(p["phase"]) * p["sway"]) * dt
            p["rot"] += p["spin"] * dt
            if p["y"] > SCREEN_HEIGHT + 20 or p["x"] < -30 or p["x"] > SCREEN_WIDTH + 30:
                self.petals[i] = self._new()

    def draw(self, surface: pygame.Surface):
        for p in self.petals:
            spr = pygame.transform.rotate(self._sprite(p["size"], p["shade"]), p["rot"])
            surface.blit(spr, (p["x"] - spr.get_width() / 2, p["y"] - spr.get_height() / 2))
