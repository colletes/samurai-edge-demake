"""
Iluminação 2.5D e atmosfera das arenas (Entregável 6.4).

`ArenaLighting` lê o `LightingEnvironment` do spec da arena e desenha, depois do mundo e antes do HUD:
  1. camadas de ar em baixo da cor (névoa, bruma, fumaça, incenso, vapor);
  2. a gradação ambiente + vinheta, numa única multiplicação de tela;
  3. brilho aditivo das luzes (poça no chão e halo na altura da lanterna, com cintilação), luzes dinâmicas
     (círculos de morteiro, barris acesos, relâmpago) e partículas luminosas (vaga-lumes, brasas, poeira,
     feixes de sol, refletor, fogos distantes);
  4. chuva.

Convenção de `AtmosphereEffect.points`: (x, y, z) para vaga-lumes, incenso e vapor; (x, y, raio) para o refletor.
Tudo usa sprites pré-assados em cache e o tempo vem de `time_val`, então não há `update` separado para chamar.
"""
import math
import random

import numpy as np
import pygame

from src.effects import quality

GRADE_GAIN = 0.45       # quanto da cor ambiente entra na gradação (0 = nenhuma)
GLOW_GAIN = 0.55        # intensidade do brilho aditivo das luzes
LEVEL_STEPS = 4         # degraus de intensidade do brilho (cintilação) por sprite
MAX_PUFFS = 28
FIRE_FLICKER = 0.2      # luzes com cintilação a partir daqui soltam brasas

_sprite_cache: dict = {}
OPACITY_STEP = 8        # a opacidade das bolas é assada no sprite em degraus, no lugar de `set_alpha` por quadro


def _remember(key, make):
    sprite = _sprite_cache.get(key)
    if sprite is None:
        if len(_sprite_cache) > 900:
            _sprite_cache.clear()
        sprite = _sprite_cache[key] = make()
    return sprite


def glow_sprite(color, hw: int, hh: int, level: float) -> pygame.Surface:
    """Elipse de brilho com queda quadrática, já multiplicada pela cor: some ao ser somada na tela quando o valor é 0."""
    hw = max(8, int(round(hw / 8.0)) * 8)
    hh = max(4, int(round(hh / 4.0)) * 4)
    level = round(level * LEVEL_STEPS) / LEVEL_STEPS

    def make():
        w, h = hw * 2, hh * 2
        xs = np.linspace(-1.0, 1.0, w)[:, None]
        ys = np.linspace(-1.0, 1.0, h)[None, :]
        falloff = np.clip(1.0 - np.sqrt(xs ** 2 + ys ** 2), 0.0, 1.0) ** 2 * level
        arr = np.clip(falloff[..., None] * np.array(color, dtype=float), 0, 255).astype(np.uint8)
        return pygame.surfarray.make_surface(arr)

    return _remember(("glow", tuple(color), hw, hh, level), make)


def quantize_opacity(opacity: float) -> int:
    return max(0, min(255, int(round(opacity / OPACITY_STEP)) * OPACITY_STEP))


def puff_sprite(color, size: int, opacity: int = 255) -> pygame.Surface:
    """Bola macia com alfa por pixel (névoa, fumaça), com a opacidade geral já assada no sprite (em degraus de `OPACITY_STEP`)."""
    size = max(8, int(round(size / 8.0)) * 8)
    opacity = quantize_opacity(opacity)

    def make():
        axis = np.linspace(-1.0, 1.0, size)
        d = np.sqrt(axis[:, None] ** 2 + axis[None, :] ** 2)
        alpha = (np.clip(1.0 - d, 0.0, 1.0) ** 1.5 * opacity).astype(np.uint8)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.surfarray.pixels3d(surf)[:] = color
        pygame.surfarray.pixels_alpha(surf)[:] = alpha
        return surf

    return _remember(("puff", tuple(color), size, opacity), make)


def _take(items):
    """Itens a desenhar na qualidade atual: todos na alta, um terço (no mínimo 2) na baixa."""
    if quality.is_high():
        return items
    return items[:max(2, len(items) // 3)]


def _ground_extent(camera, x: float, y: float, z: float, r: float):
    """Centro na tela e meia-largura/meia-altura da elipse que um círculo de raio `r` desenha na projeção."""
    cx, cy = camera.apply(x, y, z)
    hw = hh = 1
    for k in range(8):
        a = k * math.pi / 4.0
        px, py = camera.apply(x + math.cos(a) * r, y + math.sin(a) * r, z)
        hw = max(hw, abs(px - cx))
        hh = max(hh, abs(py - cy))
    return (cx, cy), hw, hh


def _add_glow(surface, camera, x, y, z, color, radius, level, ground=True):
    (cx, cy), hw, hh = _ground_extent(camera, x, y, z, radius)
    if not ground:  # halo redondo à altura da lâmpada
        hh = hw
    sprite = glow_sprite(color, hw, hh, level)
    surface.blit(sprite, (cx - sprite.get_width() // 2, cy - sprite.get_height() // 2), special_flags=pygame.BLEND_RGB_ADD)


def _add_spark(surface, sx, sy, color, size=2):
    surface.fill(color, (int(sx) - size // 2, int(sy) - size // 2, size, size), special_flags=pygame.BLEND_RGB_ADD)


def _scaled(color, k: float):
    return tuple(max(0, min(255, int(c * k))) for c in color)


class _Effect:
    def __init__(self, arena, density: float, points=()):
        self.arena = arena
        self.cols, self.rows = arena.cols, arena.rows
        self.density = density
        self.points = points
        self.rng = random.Random(hash((type(self).__name__, arena.spec.id)) & 0xFFFF)

    def update(self, dt: float, time_val: float):
        pass

    def wind(self, x: float, y: float, time_val: float):
        return self.arena.wind_at(x, y, time_val)

    def render_air(self, surface, camera, time_val):
        """Antes da gradação (mistura normal)."""

    def render_glow(self, surface, camera, time_val):
        """Depois da gradação (soma aditiva)."""

    def render_front(self, surface, camera, time_val):
        """Por último, na frente de tudo."""

    def count(self) -> int:
        return 0


class _Fireflies(_Effect):
    def render_glow(self, surface, camera, time_val):
        for fx, fy, fz in _take(self.points):
            x = fx + math.sin(time_val * 2.0 + fy) * 0.12
            y = fy + math.cos(time_val * 1.8 + fx) * 0.12
            z = fz + math.sin(time_val * 2.5 + fx * 2.0) * 0.08
            blink = 0.65 + 0.35 * math.sin(time_val * 3.1 + fx * 1.7)
            sx, sy = camera.apply(x, y, z)
            _add_spark(surface, sx, sy, _scaled((180, 255, 80), blink), 4)
            _add_glow(surface, camera, x, y, z, (120, 200, 60), 0.5, blink, ground=False)

    def count(self):
        return len(_take(self.points))


class _Motes(_Effect):
    """Poeira flutuante ao sol: pontos que sobem e derivam devagar."""

    def __init__(self, arena, density, points=()):
        super().__init__(arena, density, points)
        n = int(10 + 30 * density)
        self.motes = [[self.rng.uniform(0, self.cols), self.rng.uniform(0, self.rows), self.rng.uniform(0.3, 4.0),
                       self.rng.uniform(-0.12, 0.12), self.rng.uniform(0.02, 0.12), self.rng.uniform(0.04, 0.16),
                       self.rng.uniform(0, 6.28)] for _ in range(n)]

    def update(self, dt, time_val):
        for m in self.motes:
            wind_x, wind_y = self.wind(m[0], m[1], time_val)
            m[0] += (m[3] + wind_x * 0.3) * dt
            m[1] += (m[4] + wind_y * 0.3) * dt
            m[2] += m[5] * dt
            if m[2] > 4.2 or m[0] < 0 or m[0] > self.cols or m[1] > self.rows:
                m[0], m[1], m[2] = self.rng.uniform(0, self.cols), self.rng.uniform(0, self.rows), 0.2

    def render_glow(self, surface, camera, time_val):
        for m in _take(self.motes):
            twinkle = 0.5 + 0.5 * math.sin(time_val * 1.6 + m[6])
            sx, sy = camera.apply(m[0], m[1], m[2])
            _add_spark(surface, sx, sy, _scaled((230, 215, 170), 0.25 + 0.55 * twinkle), 2)

    def count(self):
        return len(_take(self.motes))


class _Embers(_Effect):
    """Brasas que sobem das fontes de fogo e do cenário em chamas."""

    def __init__(self, arena, density, points=()):
        super().__init__(arena, density, points)
        self.fires = [(l.x, l.y, l.z) for l in arena.lighting.lights if l.flicker >= FIRE_FLICKER]
        self.cap = int(10 + 40 * density)
        self.embers: list[list[float]] = []

    def update(self, dt, time_val):
        spawn = 4.0 + 8.0 * self.density
        n = int(spawn * dt) + (1 if self.rng.random() < spawn * dt % 1.0 else 0)
        for _ in range(n):
            if len(self.embers) >= quality.scaled(self.cap, 4):
                break
            if self.fires and self.rng.random() < 0.6:
                fx, fy, fz = self.rng.choice(self.fires)
                x, y, z = fx + self.rng.uniform(-0.2, 0.2), fy + self.rng.uniform(-0.2, 0.2), fz
            else:
                x, y, z = self.rng.uniform(1, self.cols - 1), self.rng.uniform(1, self.rows - 1), 0.1
            self.embers.append([x, y, z, self.rng.uniform(-0.3, 0.3), self.rng.uniform(-0.3, 0.3),
                                self.rng.uniform(0.7, 1.6), 0.0, self.rng.uniform(1.2, 2.4)])
        for e in self.embers:
            wind_x, wind_y = self.wind(e[0], e[1], time_val)
            e[0] += (e[3] + wind_x * 0.6) * dt
            e[1] += (e[4] + wind_y * 0.6) * dt
            e[2] += e[5] * dt
            e[6] += dt
        self.embers = [e for e in self.embers if e[6] < e[7]]

    def render_glow(self, surface, camera, time_val):
        for e in self.embers:
            k = 1.0 - e[6] / e[7]
            sx, sy = camera.apply(e[0] + math.sin(e[6] * 5.0 + e[7]) * 0.08, e[1], e[2])
            _add_spark(surface, sx, sy, _scaled((255, 140, 50), 0.4 + 0.6 * k), 3 if k > 0.5 else 2)

    def count(self):
        return len(self.embers)


class _Puffs(_Effect):
    """Fumaça, incenso e vapor: bolas macias que sobem, crescem e somem. Só muda cor, tamanho e origem."""

    def __init__(self, arena, density, points=(), *, color=(120, 118, 120), alpha=70, size=(40, 120), life=(3.5, 6.0),
                 rise=(0.35, 0.7), rate=1.0, sway=0.2):
        super().__init__(arena, density, points)
        self.color, self.alpha, self.size, self.life, self.rise, self.sway = color, alpha, size, life, rise, sway
        self.rate = rate * max(density, 0.05) * max(1, len(points))
        self.puffs: list[list[float]] = []
        self._carry = 0.0

    def _origin(self):
        if self.points:
            x, y, z = self.rng.choice(self.points)
            return x + self.rng.uniform(-0.1, 0.1), y + self.rng.uniform(-0.1, 0.1), z
        return self.rng.uniform(1.0, self.cols - 1.0), self.rng.uniform(1.0, self.rows - 1.0), 0.3

    def update(self, dt, time_val):
        self._carry += self.rate * dt
        while self._carry >= 1.0:
            self._carry -= 1.0
            if len(self.puffs) < quality.scaled(MAX_PUFFS, 6):
                x, y, z = self._origin()
                self.puffs.append([x, y, z, self.rng.uniform(*self.rise), self.rng.uniform(*self.life), 0.0, self.rng.uniform(0, 6.28)])
        for p in self.puffs:
            p[5] += dt
            p[2] += p[3] * dt
            wind_x, wind_y = self.wind(p[0], p[1], time_val)
            p[0] += (math.sin(p[5] * 1.3 + p[6]) * self.sway + wind_x * 0.8) * dt
            p[1] += wind_y * 0.8 * dt
        self.puffs = [p for p in self.puffs if p[5] < p[4]]

    def render_air(self, surface, camera, time_val):
        for x, y, z, _, life, age, _ in self.puffs:
            f = age / life
            fade = min(1.0, f * 5.0) * (1.0 - f)
            world = self.size[0] + (self.size[1] - self.size[0]) * f
            sx, sy = camera.apply(x, y, z)
            opacity = quantize_opacity(self.alpha * fade)
            if opacity <= 0:
                continue
            sprite = puff_sprite(self.color, world * camera.zoom, opacity)
            surface.blit(sprite, (sx - sprite.get_width() // 2, sy - sprite.get_height() // 2))

    def count(self):
        return len(self.puffs)


class _Fog(_Effect):
    """Névoa ou bruma baixa: bolhas largas que andam pelo chão."""

    def __init__(self, arena, density, points=(), *, color=(190, 200, 215), alpha=60, speed=0.3):
        super().__init__(arena, density, points)
        self.color, self.alpha, self.speed = color, alpha, speed
        n = int(4 + 6 * density)
        self.blobs = [[self.rng.uniform(-2, self.cols + 2), self.rng.uniform(0, self.rows), self.rng.uniform(3.2, 5.5),
                       self.rng.uniform(0.6, 1.4), self.rng.uniform(0, 6.28)] for _ in range(n)]

    def update(self, dt, time_val):
        for b in self.blobs:
            wind_x, wind_y = self.wind(b[0], b[1], time_val)
            b[0] += (wind_x * 0.9 + self.speed * 0.3 * b[3]) * dt
            b[1] += wind_y * 0.9 * dt
            if b[0] > self.cols + 4 or b[0] < -4 or b[1] > self.rows + 3 or b[1] < -3:
                upwind_x = -1.0 if wind_x >= 0 else 1.0
                b[0] = -4.0 if upwind_x < 0 else self.cols + 4.0
                b[1] = self.rng.uniform(0, self.rows)

    def render_air(self, surface, camera, time_val):
        for x, y, radius, _, phase in _take(self.blobs):
            (cx, cy), hw, hh = _ground_extent(camera, x, y, 0.25, radius)
            opacity = quantize_opacity(self.alpha * (0.75 + 0.25 * math.sin(time_val * 0.4 + phase)))
            if opacity <= 0:
                continue
            base = puff_sprite(self.color, 128, opacity)
            sprite = _remember(("fog", tuple(self.color), int(hw // 8), int(hh // 8), opacity),
                               lambda: pygame.transform.smoothscale(base, (max(8, int(hw * 2)), max(4, int(hh * 2)))))
            surface.blit(sprite, (cx - sprite.get_width() // 2, cy - sprite.get_height() // 2))

    def count(self):
        return len(_take(self.blobs))


class _Sunbeams(_Effect):
    """Feixes de luz inclinados e translúcidos que respiram devagar."""

    def __init__(self, arena, density, points=()):
        super().__init__(arena, density, points)
        n = max(2, int(2 + 4 * density))
        self.beams = [(self.rng.uniform(0.1, 0.95), self.rng.uniform(70, 130), self.rng.uniform(0, 6.28)) for _ in range(n)]

    @staticmethod
    def _beam(width: int, height: int, level: float):
        level = round(level * 8) / 8.0

        def make():
            xs = np.arange(width * 3)[:, None]
            ys = np.arange(height)[None, :]
            center = width * 1.5 + ys * 0.45 - height * 0.22
            profile = np.exp(-(((xs - center) / (width * 0.55)) ** 2))
            fade = np.clip(1.0 - ys / height, 0.0, 1.0)
            arr = np.clip(profile * fade * 255 * level, 0, 255)[..., None] * np.array([1.0, 0.92, 0.7])
            return pygame.surfarray.make_surface(arr.astype(np.uint8))
        return _remember(("beam", width, height, level), make)

    def render_glow(self, surface, camera, time_val):
        sw, sh = surface.get_size()
        for pos, width, phase in self.beams:
            level = (0.10 + 0.07 * math.sin(time_val * 0.5 + phase)) * (0.5 + self.density) * 2.2
            beam = self._beam(int(width), int(sh * 0.8), level)
            surface.blit(beam, (int(sw * pos) - beam.get_width() // 2, 0), special_flags=pygame.BLEND_RGB_ADD)

    def count(self):
        return len(self.beams)


class _Spotlight(_Effect):
    """Refletor de palco: poça de luz quente no chão (x, y, raio)."""

    def render_glow(self, surface, camera, time_val):
        for x, y, radius in self.points:
            pulse = 0.85 + 0.15 * math.sin(time_val * 1.1)
            _add_glow(surface, camera, x, y, 0.0, (255, 230, 180), radius, 0.55 * self.density * 2.0 * pulse)

    def count(self):
        return len(self.points)


class _SkyFireworks(_Effect):
    """Fogos distantes no alto da tela, longe do chão para não lembrar os círculos de aviso dos morteiros."""

    PALETTE = ((255, 120, 80), (255, 220, 100), (120, 220, 255), (200, 140, 255), (140, 255, 170))

    def __init__(self, arena, density, points=()):
        super().__init__(arena, density, points)
        self.bursts: list[dict] = []
        self.timer = 1.5

    def update(self, dt, time_val):
        self.timer -= dt
        if self.timer <= 0 and len(self.bursts) < 3:
            self.timer = self.rng.uniform(2.0, 4.0) / max(self.density, 0.1)
            self.bursts.append({"x": self.rng.uniform(0.12, 0.88), "y": self.rng.uniform(0.04, 0.2), "age": 0.0,
                                "color": self.rng.choice(self.PALETTE), "n": 18})
        for b in self.bursts:
            b["age"] += dt
        self.bursts = [b for b in self.bursts if b["age"] < 1.3]

    def render_front(self, surface, camera, time_val):
        sw, sh = surface.get_size()
        for b in self.bursts:
            f = b["age"] / 1.3
            for k in range(b["n"]):
                a = k * math.tau / b["n"]
                r = 70.0 * (1.0 - (1.0 - f) ** 2)
                _add_spark(surface, sw * b["x"] + math.cos(a) * r, sh * b["y"] + math.sin(a) * r + 30 * f * f,
                           _scaled(b["color"], 0.8 * (1.0 - f)), 3)

    def count(self):
        return len(self.bursts)


class _Rain(_Effect):
    """Chuva em linhas na tela, com relâmpagos que clareiam tudo por um instante."""

    def __init__(self, arena, density, points=()):
        super().__init__(arena, density, points)
        n = int(90 + 110 * density)
        self.drops = [[self.rng.uniform(0, 1), self.rng.uniform(0, 1), self.rng.uniform(0.8, 1.3)] for _ in range(n)]
        self.next_flash = self.rng.uniform(3.0, 7.0)
        self.flash_age = 99.0
        self._time = 0.0

    def force_lightning(self):
        self.flash_age = 0.0

    def flash_level(self) -> float:
        a = self.flash_age
        if a > 0.6:
            return 0.0
        return max(0.0, 1.0 - a / 0.12) if a < 0.12 else (0.7 * max(0.0, 1.0 - (a - 0.2) / 0.3) if a > 0.2 else 0.0)

    def update(self, dt, time_val):
        self._time += dt
        self.flash_age += dt
        for d in self.drops:
            d[1] += d[2] * 1.6 * dt
            d[0] -= d[2] * 0.4 * dt
            if d[1] > 1.0 or d[0] < -0.05:
                d[0], d[1] = self.rng.uniform(0.0, 1.2), -0.05
        if self._time >= self.next_flash:
            self._time = 0.0
            self.next_flash = self.rng.uniform(5.0, 11.0)
            self.force_lightning()

    def render_glow(self, surface, camera, time_val):
        level = self.flash_level()
        if level > 0.0:
            surface.fill(_scaled((110, 130, 170), level), special_flags=pygame.BLEND_RGB_ADD)

    def render_front(self, surface, camera, time_val):
        sw, sh = surface.get_size()
        color = (150, 170, 205)
        for x, y, speed in _take(self.drops):
            sx, sy = int(x * sw), int(y * sh)
            pygame.draw.line(surface, color, (sx, sy), (sx - int(6 * speed), sy + int(16 * speed)), 1)

    def count(self):
        return len(_take(self.drops))


class ArenaLighting:
    """Desenha a iluminação e a atmosfera de uma arena. Um por arena carregada."""

    def __init__(self, arena):
        self.arena = arena
        self.env = arena.lighting
        self._grade = None
        self._grade_size = None
        self._last_time = None
        self.effects: list[_Effect] = [self._make_effect(arena, e) for e in self.env.atmosphere]
        self.effects = [e for e in self.effects if e is not None]
        self.rain = next((e for e in self.effects if isinstance(e, _Rain)), None)

    @staticmethod
    def _make_effect(arena, spec):
        d, pts = spec.density, spec.points
        tint = tuple(int(c * 0.5 + 255 * 0.5) for c in arena.lighting.ambient_color)
        kind = spec.kind
        if kind == "fireflies":
            return _Fireflies(arena, d, pts)
        if kind == "dust":
            return _Motes(arena, d, pts)
        if kind == "embers":
            return _Embers(arena, d, pts)
        if kind == "smoke":
            return _Puffs(arena, d, pts, color=(110, 105, 108), alpha=60, size=(60, 150), rate=0.9)
        if kind == "incense":
            return _Puffs(arena, d, pts, color=(200, 200, 210), alpha=46, size=(14, 44), life=(2.5, 4.0), rise=(0.3, 0.5), rate=2.0, sway=0.35)
        if kind == "steam":
            return _Puffs(arena, d, pts, color=(235, 240, 245), alpha=50, size=(24, 70), life=(1.6, 2.6), rise=(0.5, 0.9), rate=3.0, sway=0.25)
        if kind in ("fog", "mist"):
            return _Fog(arena, d, pts, color=tint, alpha=int(34 + 40 * d), speed=0.3 if kind == "fog" else 0.15)
        if kind == "sunbeams":
            return _Sunbeams(arena, d, pts)
        if kind == "spotlight":
            return _Spotlight(arena, d, pts)
        if kind == "fireworks":
            return _SkyFireworks(arena, d, pts)
        if kind == "rain":
            return _Rain(arena, d, pts)
        return None

    def _grade_surface(self, size):
        """Multiplicador de tela: tinta/escurecimento ambiente e vinheta, calculado uma vez por tamanho."""
        if self._grade is not None and self._grade_size == size:
            return self._grade
        w, h = size
        env = self.env
        gain = GRADE_GAIN * (1.0 - env.ambient_strength)
        base = 1.0 - gain * (1.0 - np.array(env.ambient_color, dtype=float) / 255.0)
        xs = (np.linspace(-1.0, 1.0, w)[:, None]) * 0.9
        ys = (np.linspace(-1.0, 1.0, h)[None, :]) * 1.0
        t = np.clip((np.sqrt(xs ** 2 + ys ** 2) - 0.45) / 0.8, 0.0, 1.0)
        vig = 1.0 - env.vignette * 0.85 * t ** 2
        arr = np.clip(vig[..., None] * base * 255.0, 0, 255).astype(np.uint8)
        self._grade, self._grade_size = pygame.surfarray.make_surface(arr), size
        return self._grade

    def _dynamic_lights(self):
        arena = self.arena
        for hazard in getattr(arena, "hazards", ()):
            circles = getattr(hazard, "circles", None)
            phase = getattr(hazard, "phase", "idle")
            if not circles or phase == "idle":
                continue
            palette = getattr(hazard, "COLORS", ((255, 190, 120),))
            for i, (cx, cy, r) in enumerate(circles):
                yield cx, cy, 0.3, palette[i % len(palette)], r * 1.1, (1.5 if phase == "active" else 0.6)
        for prop in getattr(arena, "interactives", ()):
            circle = prop.danger_circle() if hasattr(prop, "danger_circle") else None
            if circle:
                yield circle[0], circle[1], 0.4, (255, 150, 70), circle[2] * 0.8, 0.9

    def render(self, surface, camera, time_val):
        dt = 0.0 if self._last_time is None else min(max(time_val - self._last_time, 0.0), 0.05)
        self._last_time = time_val
        for effect in self.effects:
            effect.update(dt, time_val)

        for effect in self.effects:
            effect.render_air(surface, camera, time_val)

        surface.blit(self._grade_surface(surface.get_size()), (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        for i, light in enumerate(self.env.lights):
            wave = 0.5 * math.sin(time_val * 7.0 + i * 1.9) + 0.5 * math.sin(time_val * 13.0 + i * 0.7)
            level = GLOW_GAIN * max(0.3, 1.0 + light.flicker * wave)
            _add_glow(surface, camera, light.x, light.y, 0.0, light.color, light.radius, level)
            _add_glow(surface, camera, light.x, light.y, light.z, light.color, light.radius * 0.35, level * 1.2, ground=False)
        for x, y, z, color, radius, level in self._dynamic_lights():
            _add_glow(surface, camera, x, y, 0.0, color, radius, GLOW_GAIN * level)

        for effect in self.effects:
            effect.render_glow(surface, camera, time_val)
        for effect in self.effects:
            effect.render_front(surface, camera, time_val)

    def particle_count(self) -> int:
        return sum(effect.count() for effect in self.effects)
