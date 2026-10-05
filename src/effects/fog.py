"""
Névoa volumétrica (6.5.2).

`FogVolume` guarda "puffs" de névoa em camadas de altura. Os puffs vão para a fila de profundidade do `main.py`, então
a névoa passa na frente de quem está atrás dela e vela o corpo parcialmente. Dois tipos:
  - banco de névoa do cenário (spec `AtmosphereEffect("fogbank")`, hoje o Templo na Névoa): puffs largos que andam com o
    vento da arena e deixam os lutadores dentro dele mais apagados (só visual, a IA não muda);
  - rastro de névoa da Kasumi (`add_trail`): nuvem densa de ~3,5 s deixada pela esquiva. Quem está dentro fica quase
    invisível e a IA erra a mira de projéteis contra ele (`trail_density_at`), sem dano.
O sino do santuário chama `dispel()`: apaga os rastros e afina o banco por alguns segundos.
"""
import math
import random

import numpy as np
import pygame

from src.effects.lighting import _ground_extent

BANK_VISIBILITY = 0.55      # quanto a densidade do banco apaga um lutador (1.0 = some)
TRAIL_VISIBILITY = 0.80
VISIBILITY_FLOOR = 0.2
TRAIL_LIFE = 3.5
TRAIL_MAX = 28
CALM_AFTER_DISPEL = 0.1
CALM_RECOVERY = 8.0         # s para o banco voltar ao normal depois do sino
SPRITE_W, SPRITE_H = 192, 112
VARIANTS = 6

_cache: dict = {}


def _fbm(w: int, h: int, seed: int):
    """Ruído de valor em 3 oitavas, em [0, 1], com shape (w, h)."""
    rng = np.random.default_rng(seed)
    acc = np.zeros((w, h))
    amp, total = 1.0, 0.0
    for cells in (4, 8, 16):
        grid = (rng.random((cells, cells)) * 255).astype(np.uint8)
        small = pygame.surfarray.make_surface(np.stack([grid] * 3, axis=-1))
        big = pygame.transform.smoothscale(small, (w, h))
        acc += pygame.surfarray.array3d(big)[..., 0].astype(float) / 255.0 * amp
        total += amp
        amp *= 0.5
    return acc / total


def fog_base(variant: int, color) -> pygame.Surface:
    key = ("base", variant, tuple(color))
    surf = _cache.get(key)
    if surf is None:
        w, h = SPRITE_W, SPRITE_H
        xs = np.linspace(-1.0, 1.0, w)[:, None]
        ys = np.linspace(-1.0, 1.0, h)[None, :]
        radial = np.clip(1.0 - np.sqrt(xs ** 2 + ys ** 2), 0.0, 1.0) ** 1.3
        alpha = np.clip(radial * (0.35 + 0.95 * _fbm(w, h, 100 + variant)), 0.0, 1.0)
        shade = 0.78 + 0.32 * (1.0 - (ys + 1.0) / 2.0)  # topo iluminado, base mais escura
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        rgb = np.clip(np.array(color, dtype=float)[None, None, :] * shade[..., None], 0, 255)
        pygame.surfarray.pixels3d(surf)[:] = rgb.astype(np.uint8)
        pygame.surfarray.pixels_alpha(surf)[:] = (alpha * 255).astype(np.uint8)
        _cache[key] = surf
    return surf


LEVELS = 8


def fog_sprite(variant: int, color, w: int, h: int, level: float = 1.0) -> pygame.Surface:
    """Sprite já com a opacidade assada (set_alpha em superfície com alfa por pixel deixa o blit ~6x mais lento)."""
    wq, hq = max(24, int(round(w / 24.0)) * 24), max(12, int(round(h / 12.0)) * 12)
    lv = max(1, min(LEVELS, int(round(level * LEVELS))))
    key = ("scaled", variant, tuple(color), wq, hq, lv)
    sprite = _cache.get(key)
    if sprite is None:
        if len(_cache) > 700:
            _cache.clear()
        base = _cache.get(("full", variant, tuple(color), wq, hq))
        if base is None:
            base = _cache[("full", variant, tuple(color), wq, hq)] = pygame.transform.smoothscale(fog_base(variant, color), (wq, hq))
        sprite = base.copy()
        alpha = pygame.surfarray.pixels_alpha(sprite)
        alpha[:] = (alpha * (lv / LEVELS)).astype(np.uint8)
        del alpha
        sprite = _cache[key] = sprite.convert_alpha()
    return sprite


class FogPuff:
    __slots__ = ("volume", "kind", "x", "y", "z", "r", "base", "age", "life", "phase", "variant", "color", "grow")

    def __init__(self, volume, kind, x, y, z, r, base, life=0.0, phase=0.0, variant=0, color=(200, 205, 215), grow=0.0):
        self.volume, self.kind = volume, kind
        self.x, self.y, self.z, self.r = x, y, z, r
        self.base, self.life, self.phase = base, life, phase
        self.variant, self.color, self.grow = variant, color, grow
        self.age = 0.0

    def strength(self, t: float = 0.0) -> float:
        if self.kind == "trail":
            fade_in = min(1.0, self.age / 0.15)
            fade_out = min(1.0, max(0.0, (self.life - self.age) / 1.2))
            return self.base * fade_in * fade_out
        return self.base * (0.8 + 0.2 * math.sin(t * 0.3 + self.phase)) * self.volume.calm

    def render(self, surface: pygame.Surface, camera):
        s = self.strength(self.volume.time)
        if s <= 0.02:
            return
        (cx, cy), hw, hh = _ground_extent(camera, self.x, self.y, self.z, self.r)
        hh = int(hh * 1.5)
        sw, sh = surface.get_size()
        if cx + hw < 0 or cx - hw > sw or cy + hh < 0 or cy - hh > sh:
            return
        sprite = fog_sprite(self.variant, self.color, hw * 2, hh * 2, min(1.0, s * self.volume.alpha_gain(self.kind)))
        surface.blit(sprite, (cx - sprite.get_width() // 2, cy - sprite.get_height() // 2))


class FogVolume:
    def __init__(self, arena):
        self.arena = arena
        self.time = 0.0
        self.calm = 1.0
        self.bank: list[FogPuff] = []
        self.trail: list[FogPuff] = []
        self.rng = random.Random(hash(("fog", arena.spec.id)) & 0xFFFF)
        spec = next((e for e in arena.lighting.atmosphere if e.kind == "fogbank"), None)
        self.has_bank = spec is not None
        if spec is not None:
            self._build_bank(spec.density)

    def _build_bank(self, density: float):
        ambient = self.arena.lighting.ambient_color
        color = tuple(int(c * 0.35 + 255 * 0.65) for c in ambient)
        rng = self.rng
        for z, count, radius, strength in ((0.15, 12, (3.4, 5.2), 0.8), (0.8, 10, (2.8, 4.2), 0.65), (1.7, 6, (2.4, 3.4), 0.4)):
            for _ in range(int(round(count * max(0.3, density)))):
                self.bank.append(FogPuff(self, "bank", rng.uniform(-1, self.arena.cols + 1), rng.uniform(2, self.arena.rows - 2),
                                         z, rng.uniform(*radius), strength, phase=rng.uniform(0, 6.28),
                                         variant=rng.randrange(VARIANTS), color=color))

    @staticmethod
    def alpha_gain(kind: str) -> float:
        return 0.95 if kind == "bank" else 0.75

    def add_trail(self, x: float, y: float, radius: float = 1.2, strength: float = 1.0):
        """Um nó do rastro: cresce um pouco e some em ~3,5 s."""
        for z in (0.35, 0.95):
            if len(self.trail) >= TRAIL_MAX:
                self.trail.pop(0)
            self.trail.append(FogPuff(self, "trail", x + self.rng.uniform(-0.15, 0.15), y + self.rng.uniform(-0.15, 0.15), z,
                                      radius * self.rng.uniform(0.9, 1.15), strength, life=TRAIL_LIFE,
                                      variant=self.rng.randrange(VARIANTS), color=(168, 176, 194), grow=0.12))

    def dispel(self):
        """Sino do santuário: apaga os rastros e afina o banco, que volta devagar."""
        self.trail.clear()
        self.calm = CALM_AFTER_DISPEL

    def update(self, dt: float, t: float):
        self.time = t
        if self.calm < 1.0:
            self.calm = min(1.0, self.calm + (1.0 - CALM_AFTER_DISPEL) / CALM_RECOVERY * dt)
        arena = self.arena
        for p in self.bank:
            wind_x, wind_y = arena.wind_at(p.x, p.y, t)
            p.x += wind_x * 0.9 * dt
            p.y += (wind_y * 0.9 + math.sin(t * 0.2 + p.phase) * 0.12) * dt
            margin = p.r + 1.0
            if p.x > arena.cols + margin:
                p.x = -margin
            elif p.x < -margin:
                p.x = arena.cols + margin
            if p.y > arena.rows + margin:
                p.y = -margin
            elif p.y < -margin:
                p.y = arena.rows + margin
        for p in self.trail:
            p.age += dt
            wind_x, wind_y = arena.wind_at(p.x, p.y, t)
            p.x += wind_x * 0.7 * dt
            p.y += wind_y * 0.7 * dt
            p.r += p.grow * dt
        self.trail = [p for p in self.trail if p.age < p.life]

    @staticmethod
    def _falloff(p: FogPuff, x: float, y: float, t: float) -> float:
        d2 = ((x - p.x) ** 2 + (y - p.y) ** 2) / (p.r * p.r)
        if d2 >= 1.0:
            return 0.0
        return p.strength(t) * (1.0 - d2) ** 2

    def bank_density_at(self, x: float, y: float) -> float:
        return min(1.0, sum(self._falloff(p, x, y, self.time) for p in self.bank if p.z < 1.5))

    def trail_density_at(self, x: float, y: float) -> float:
        return min(1.0, sum(self._falloff(p, x, y, self.time) for p in self.trail) * 0.7)

    def visibility_at(self, x: float, y: float) -> float:
        """Fração da opacidade com que um lutador em (x, y) aparece (1 = sem névoa)."""
        v = 1.0 - BANK_VISIBILITY * self.bank_density_at(x, y) - TRAIL_VISIBILITY * self.trail_density_at(x, y)
        return max(VISIBILITY_FLOOR, v)

    def queue_items(self, camera):
        """Itens (profundidade, 'fog', puff) para a fila de renderização com y-sorting."""
        depth = camera.depth
        return [(depth(p.x, p.y), "fog", p) for p in self.bank + self.trail]

    @property
    def count(self) -> int:
        return len(self.bank) + len(self.trail)
