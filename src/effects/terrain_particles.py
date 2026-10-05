"""
Partículas de terreno com física (6.5.1): lâminas de grama, grãos de areia, pedrinhas, torrões de lama,
gotas de água e poeira saltam sob os pés dos lutadores conforme o material do piso e a velocidade do evento.

`TerrainFX.step(fighter, arena, dt)` deduz a velocidade pelo deslocamento por quadro, então andar, esquiva,
dash, knockback e pouso funcionam igual para os 12 lutadores sem tocar nas subclasses. As partículas têm
gravidade, quique, atrito e vento, e somem logo depois de assentar (nunca ficam no cenário).
"""
import math
import random
from dataclasses import dataclass

import pygame

from src.effects import quality
from src.effects.particles import get_pooled_smoke_surface

STRIDE = 0.5            # distância entre dois passos (u)
FAST_SPEED = 6.5        # a partir daqui é esquiva ou dash: rastro contínuo
REF_SPEED = 10.0        # velocidade de referência (esquiva ágil)
TELEPORT = 1.5          # deslocamento por quadro que indica teleporte (spawn, introdução), sem emissão
WIND_GAIN = 2.0         # vento (u/s) -> velocidade-alvo de uma partícula leve
MAX_PARTICLES = 200
MAX_PUFFS = 24
SETTLE_SPEED = 0.35
SETTLE_FADE = 0.14


@dataclass(frozen=True)
class Preset:
    kind: str            # blade | grain | pebble | clump | drop | puff
    mult: float          # brilho aplicado à cor do tile
    mix: tuple           # (r, g, b, peso) misturado à cor do tile
    step: float          # partículas por passo ao caminhar
    burst: float         # intensidade em esquiva, dash, pouso e freada
    gravity: float
    bounce: float
    friction: float
    drag: float
    wind: float          # 0..1: quanto o vento arrasta
    life: tuple
    size: tuple
    lift: float
    puff: float = 0.0    # poeira extra (fração do total) nos eventos rápidos
    ring: bool = False   # marolas na água


_NONE = (0, 0, 0, 0.0)
SURFACES: dict[str, Preset] = {
    "grass": Preset("blade", 1.6, (140, 215, 90, 0.45), 6.0, 2.4, 7.0, 0.10, 5.0, 0.6, 0.55, (0.6, 1.1), (3, 5), 1.8),
    "moss": Preset("blade", 1.4, (110, 180, 90, 0.4), 4.5, 1.8, 7.0, 0.10, 5.0, 0.6, 0.55, (0.6, 1.0), (2, 4), 1.1),
    "sand": Preset("grain", 1.3, (240, 225, 180, 0.3), 8.0, 3.0, 14.0, 0.30, 9.0, 0.25, 0.15, (0.5, 0.9), (1, 3), 1.8, puff=0.25),
    "wet_sand": Preset("clump", 0.95, _NONE, 5.0, 2.2, 15.0, 0.05, 11.0, 0.2, 0.0, (0.45, 0.8), (2, 3), 1.5),
    "gravel": Preset("pebble", 1.15, _NONE, 5.0, 2.2, 17.0, 0.45, 6.0, 0.2, 0.0, (0.5, 0.9), (2, 3), 2.0, puff=0.15),
    "mud": Preset("clump", 0.85, _NONE, 5.0, 2.2, 15.0, 0.03, 12.0, 0.2, 0.0, (0.5, 0.9), (2, 4), 1.6),
    "dirt": Preset("grain", 1.25, _NONE, 6.0, 2.4, 14.0, 0.20, 9.0, 0.3, 0.2, (0.4, 0.7), (1, 3), 1.5, puff=0.3),
    "water": Preset("drop", 1.0, (170, 210, 232, 0.8), 6.0, 2.5, 12.0, 0.0, 6.0, 0.1, 0.0, (0.4, 0.8), (1, 2), 2.2, ring=True),
    "stone": Preset("puff", 1.1, (200, 200, 200, 0.5), 0.0, 0.3, 0.0, 0.0, 0.0, 1.5, 0.5, (0.35, 0.6), (3, 5), 0.5),
    "marble": Preset("puff", 1.1, (230, 230, 230, 0.6), 0.0, 0.3, 0.0, 0.0, 0.0, 1.5, 0.5, (0.35, 0.6), (3, 5), 0.5),
    "wood": Preset("puff", 1.2, (190, 170, 140, 0.5), 0.0, 0.3, 0.0, 0.0, 0.0, 1.5, 0.5, (0.35, 0.6), (3, 5), 0.5),
    "roof": Preset("puff", 1.1, (190, 190, 190, 0.5), 0.0, 0.3, 0.0, 0.0, 0.0, 1.5, 0.5, (0.35, 0.6), (3, 5), 0.5),
    "tatami": Preset("puff", 1.2, (210, 200, 160, 0.5), 0.0, 0.18, 0.0, 0.0, 0.0, 1.5, 0.5, (0.35, 0.6), (3, 5), 0.5),
}
DEFAULT_PRESET = SURFACES["stone"]


def _rand_round(x: float) -> int:
    n = int(x)
    return n + (1 if random.random() < x - n else 0)


def _clamp(v: float) -> int:
    return max(0, min(255, int(v)))


class TerrainParticle:
    __slots__ = ("wx", "wy", "wz", "vx", "vy", "vz", "kind", "color", "size", "preset", "age", "life", "settled",
                 "fade", "grounded", "angle", "radius")

    def __init__(self, kind, preset, wx, wy, wz, vx, vy, vz, color, size, life):
        self.kind, self.preset = kind, preset
        self.wx, self.wy, self.wz = wx, wy, wz
        self.vx, self.vy, self.vz = vx, vy, vz
        self.color, self.size, self.life = color, size, life
        self.age = 0.0
        self.settled = False
        self.fade = SETTLE_FADE
        self.grounded = False
        self.angle = random.uniform(0, math.tau)
        self.radius = 0.1

    def update(self, dt: float, wind: tuple[float, float]) -> bool:
        self.age += dt
        p = self.preset
        if self.kind == "ring":
            self.radius += 0.9 * dt
            return self.age < self.life
        if self.settled:
            self.fade -= dt
            return self.fade > 0.0
        if self.kind == "puff":
            k = p.wind * dt
            self.vx += (wind[0] * WIND_GAIN - self.vx) * k
            self.vy += (wind[1] * WIND_GAIN - self.vy) * k
            self.vz *= 1.0 / (1.0 + 1.5 * dt)
            self.wx += self.vx * dt
            self.wy += self.vy * dt
            self.wz += self.vz * dt
            return self.age < self.life
        drag = 1.0 / (1.0 + p.drag * dt)
        if p.wind > 0.0 and not self.grounded:
            k = min(1.0, p.wind * dt)
            self.vx += (wind[0] * WIND_GAIN - self.vx) * k
            self.vy += (wind[1] * WIND_GAIN - self.vy) * k
        self.vx *= drag
        self.vy *= drag
        self.vz -= p.gravity * dt
        self.wx += self.vx * dt
        self.wy += self.vy * dt
        self.wz += self.vz * dt
        if self.wz <= 0.0:
            self.wz = 0.0
            if self.vz < 0.0:
                if -self.vz * p.bounce < 0.5:
                    self.vz = 0.0
                    self.grounded = True
                else:
                    self.vz = -self.vz * p.bounce
            if self.grounded:
                f = math.exp(-p.friction * dt)
                self.vx *= f
                self.vy *= f
                if self.kind == "drop" or math.hypot(self.vx, self.vy) < SETTLE_SPEED:
                    self.settled = True
        if self.age >= self.life:
            self.settled = True
        return True

    def render(self, surface: pygame.Surface, camera):
        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        kind = self.kind
        if kind == "puff":
            f = self.age / self.life
            r = max(2, int(self.size * (1.0 + f * 1.4)))
            surf = get_pooled_smoke_surface(r)
            pygame.draw.circle(surf, (*self.color, int(110 * (1.0 - f))), (r, r), r)
            surface.blit(surf, (sx - r, sy - r))
            return
        if kind == "ring":
            gx, gy = camera.apply(self.wx, self.wy, 0.0)
            f = self.age / self.life
            w = max(2, int(self.radius * 64.0))
            shade = tuple(_clamp(c * (1.0 - 0.5 * f)) for c in self.color)
            pygame.draw.ellipse(surface, shade, (gx - w // 2, gy - w // 4, w, w // 2), 1)
            return
        scale = max(0.0, self.fade / SETTLE_FADE) if self.settled else 1.0
        size = self.size * scale
        if size < 0.6:
            return
        if self.wz > 0.12:  # sombra no chão para dar altura
            gx, gy = camera.apply(self.wx, self.wy, 0.0)
            pygame.draw.rect(surface, (24, 22, 24), (gx - 1, gy, 3, 1))
        if kind == "blade":
            length = 2.0 + size
            dx, dy = math.cos(self.angle + self.age * 9.0) * length, math.sin(self.angle + self.age * 9.0) * length * 0.6
            pygame.draw.line(surface, self.color, (sx, sy), (sx + dx, sy + dy), 2)
        elif kind == "drop":
            pygame.draw.circle(surface, self.color, (sx, sy), max(1, int(size)))
            if not self.grounded and self.vz > 0.0:
                pygame.draw.line(surface, self.color, (sx, sy + 1), (sx, sy + 3), 1)
        elif kind == "clump":
            r = max(1, int(size))
            pygame.draw.circle(surface, tuple(_clamp(c * 0.55) for c in self.color), (sx, sy), r + 1)
            pygame.draw.circle(surface, self.color, (sx, sy), r)
        elif kind == "pebble":
            s = max(2, int(size) + 1)
            pygame.draw.rect(surface, tuple(_clamp(c * 0.5) for c in self.color), (sx - s // 2 - 1, sy - s // 2 - 1, s + 2, s + 2))
            pygame.draw.rect(surface, self.color, (sx - s // 2, sy - s // 2, s, s))
        else:  # grain
            s = max(1, int(size))
            pygame.draw.rect(surface, self.color, (sx, sy, s + 1, s + 1))


class TerrainFX:
    """Emissor e dono das partículas de terreno de uma arena."""

    def __init__(self):
        self.particles: list[TerrainParticle] = []
        self.spawned = 0
        self._track: dict[int, dict] = {}

    def _color(self, arena, wx, wy, preset: Preset):
        style = arena.style_at(int(math.floor(wx)), int(math.floor(wy)))
        base = style.colors[random.randrange(len(style.colors))] if style.colors else (128, 128, 128)
        shade = preset.mult * random.uniform(0.85, 1.15)
        r, g, b = (c * shade for c in base[:3])
        mr, mg, mb, w = preset.mix
        if w > 0.0:
            r, g, b = r * (1 - w) + mr * w, g * (1 - w) + mg * w, b * (1 - w) + mb * w
        return _clamp(r), _clamp(g), _clamp(b)

    def _emit(self, arena, preset, x, y, dir_x, dir_y, speed, n, kick, scale=1.0):
        """Solta `n` partículas em (x, y), jogadas para trás da direção (dir_x, dir_y) com a velocidade do evento."""
        puffs = sum(1 for p in self.particles if p.kind == "puff")
        max_particles, max_puffs = quality.scaled(MAX_PARTICLES, 40), quality.scaled(MAX_PUFFS, 6)
        for _ in range(quality.scaled(n) if n else 0):
            if len(self.particles) >= max_particles:
                self.particles.pop(0)
            is_puff = preset.kind == "puff" or (preset.puff > 0.0 and random.random() < preset.puff)
            if is_puff and puffs >= max_puffs:
                continue
            kind = "puff" if is_puff else preset.kind
            back = (kick * random.uniform(0.2, 1.0) + 0.15 * speed) * scale
            side = random.uniform(-1.0, 1.0) * (0.6 + 0.08 * speed)
            vx = -dir_x * back - dir_y * side
            vy = -dir_y * back + dir_x * side
            if is_puff:
                color = self._color(arena, x, y, SURFACES.get("stone") if preset.kind != "puff" else preset)
                size = random.randint(3, 5)
                p = TerrainParticle("puff", preset, x, y, 0.08, vx * 0.5, vy * 0.5, random.uniform(0.3, 0.8), color, size, random.uniform(0.35, 0.6))
                puffs += 1
            else:
                vz = (preset.lift * random.uniform(0.6, 1.3) + 0.10 * speed) * scale
                size = random.randint(*preset.size)
                p = TerrainParticle(kind, preset, x + random.uniform(-0.08, 0.08), y + random.uniform(-0.08, 0.08), 0.04,
                                    vx, vy, vz, self._color(arena, x, y, preset), size, random.uniform(*preset.life))
            self.particles.append(p)
            self.spawned += 1
        if preset.ring and n:
            self.particles.append(TerrainParticle("ring", preset, x, y, 0.0, 0, 0, 0, (190, 225, 240), 1, 0.55))

    def step(self, fighter, arena, dt: float):
        """Observa o lutador neste quadro e emite o que o movimento pede."""
        if dt <= 0.0 or not getattr(fighter, "is_alive", True):
            return
        key = id(fighter)
        x, y, z = fighter.wx, fighter.wy, getattr(fighter, "wz", 0.0)
        tr = self._track.get(key)
        if tr is None:
            self._track[key] = {"x": x, "y": y, "z": z, "speed": 0.0, "acc": 0.0, "dir": (1.0, 0.0), "side": 1.0}
            return
        dx, dy = x - tr["x"], y - tr["y"]
        dist = math.hypot(dx, dy)
        prev_speed, prev_z, prev_dir = tr["speed"], tr["z"], tr["dir"]
        tr["x"], tr["y"], tr["z"] = x, y, z
        if dist > TELEPORT or getattr(fighter, "state", "") == "FALL":
            tr["speed"], tr["acc"] = 0.0, 0.0
            return
        speed = dist / dt
        tr["speed"] = speed
        if dist > 1e-4:
            tr["dir"] = (dx / dist, dy / dist)
        dir_x, dir_y = tr["dir"]

        surface = arena.surface_at(x, y)
        if surface is None or arena.pit_at(x, y) is not None:
            return
        preset = SURFACES.get(surface, DEFAULT_PRESET)
        airborne = z > 0.05

        if prev_z > 0.2 and not airborne:  # pouso: poeira em anel
            impact = min(3.0, (prev_z - z) / dt / 6.0)
            self._emit(arena, preset, x, y, dir_x, dir_y, 4.0 + 6.0 * impact, _rand_round(6 + 8 * preset.burst * impact), 1.5, 0.6 + 0.5 * impact)
            tr["acc"] = 0.0
            return
        if airborne:
            return
        if prev_speed >= FAST_SPEED and speed < prev_speed * 0.4:  # freada
            n = _rand_round(4 + 8 * preset.burst * min(2.0, prev_speed / REF_SPEED))
            self._emit(arena, preset, x, y, -prev_dir[0], -prev_dir[1], prev_speed * 0.5, n, 2.5, 1.0)
            tr["acc"] = 0.0
            return
        if speed >= FAST_SPEED:  # esquiva, dash, empurrão: rastro contínuo
            n = _rand_round(preset.burst * speed * 6.0 * dt * (1.0 if preset.kind != "puff" else 3.0))
            if n:
                self._emit(arena, preset, x, y, dir_x, dir_y, speed, n, 1.2 + 0.18 * speed)
            tr["acc"] = 0.0
            return
        if speed > 0.6 and preset.step > 0.0:  # passos
            tr["acc"] += dist
            while tr["acc"] >= STRIDE:
                tr["acc"] -= STRIDE
                tr["side"] = -tr["side"]
                fx = x - dir_y * 0.12 * tr["side"] - dir_x * 0.05
                fy = y + dir_x * 0.12 * tr["side"] - dir_y * 0.05
                self._emit(arena, preset, fx, fy, dir_x, dir_y, speed, _rand_round(preset.step * (0.5 + speed / 6.0)), 0.5)
        else:
            tr["acc"] = 0.0

    def update(self, dt: float, arena, t: float):
        alive = []
        for p in self.particles:
            if p.update(dt, arena.wind_at(p.wx, p.wy, t)):
                alive.append(p)
        self.particles = alive

    def reset(self):
        self.particles.clear()
        self._track.clear()
