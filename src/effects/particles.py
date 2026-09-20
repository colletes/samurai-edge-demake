"""
Sistema completo de partículas e efeitos visuais para combate e atmosfera feudal.
"""
import math
import random
import pygame
from src.config import (
    COLOR_BAMBOO_LEAF, COLOR_SAKURA_PINK, COLOR_STEEL, COLOR_GOLD,
    COLOR_WHITE, COLOR_BLOOD, COLOR_RED_AURA, COLOR_BLUE_AURA
)
from src.isometric.iso_math import world_to_iso

class SparkParticle:
    """Faíscas geradas quando uma espada atinge pedras ou em choque de lâminas (clash/parry)."""
    def __init__(self, wx: float, wy: float, wz: float = 0.5):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2.5, 6.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.vz = random.uniform(2.0, 5.5)
        self.lifetime = random.uniform(0.25, 0.45)
        self.age = 0.0
        self.color = random.choice([COLOR_GOLD, COLOR_WHITE, (255, 240, 150), (255, 140, 40)])
        self.size = random.choice([2, 3])

    def update(self, dt: float) -> bool:
        self.age += dt
        self.wx += self.vx * dt
        self.wy += self.vy * dt
        self.wz += self.vz * dt
        self.vz -= 12.0 * dt  # gravidade
        return self.age < self.lifetime

    def render(self, surface: pygame.Surface, camera):
        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        alpha_ratio = max(0.0, 1.0 - (self.age / self.lifetime))
        if alpha_ratio > 0:
            pygame.draw.circle(surface, self.color, (sx, sy), self.size)


class BloodParticle:
    """Partículas de impacto sangrento no golpe fatal."""
    def __init__(self, wx: float, wy: float, wz: float = 0.8):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.5, 4.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.vz = random.uniform(1.0, 4.0)
        self.lifetime = random.uniform(0.4, 0.7)
        self.age = 0.0
        self.size = random.randint(2, 4)

    def update(self, dt: float) -> bool:
        self.age += dt
        self.wx += self.vx * dt
        self.wy += self.vy * dt
        self.wz += self.vz * dt
        self.vz -= 14.0 * dt
        if self.wz < 0:
            self.wz = 0
            self.vx *= 0.5
            self.vy *= 0.5
        return self.age < self.lifetime

    def render(self, surface: pygame.Surface, camera):
        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        pygame.draw.circle(surface, COLOR_BLOOD, (sx, sy), self.size)


class BambooSliceParticle:
    """A porção superior de um bambu cortado que tomba rodando no ar e cai no chão."""
    def __init__(self, wx: float, wy: float, cut_height: float, total_height: float, slash_dir: tuple[float, float]):
        self.wx = wx
        self.wy = wy
        self.wz = cut_height
        self.piece_length = total_height - cut_height
        self.vx = slash_dir[0] * random.uniform(2.0, 4.0) + random.uniform(-0.5, 0.5)
        self.vy = slash_dir[1] * random.uniform(2.0, 4.0) + random.uniform(-0.5, 0.5)
        self.vz = random.uniform(2.0, 4.5)
        self.rot_angle = 0.0
        self.rot_speed = random.uniform(200.0, 450.0) * (1 if random.random() > 0.5 else -1)
        self.lifetime = 1.2
        self.age = 0.0

    def update(self, dt: float) -> bool:
        self.age += dt
        self.wx += self.vx * dt
        self.wy += self.vy * dt
        self.wz += self.vz * dt
        self.vz -= 16.0 * dt
        self.rot_angle += self.rot_speed * dt
        if self.wz <= 0:
            self.wz = 0
            self.vx *= 0.6
            self.vy *= 0.6
            self.rot_speed *= 0.5
        return self.age < self.lifetime

    def render(self, surface: pygame.Surface, camera):
        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        rad = math.radians(self.rot_angle)
        pixel_len = int(self.piece_length * 28)
        end_x = int(sx + math.sin(rad) * pixel_len)
        end_y = int(sy - math.cos(rad) * pixel_len)
        pygame.draw.line(surface, (55, 125, 45), (sx, sy), (end_x, end_y), 5)
        pygame.draw.line(surface, (95, 185, 75), (sx, sy), (end_x, end_y), 2)


class AmbientLeafParticle:
    """Folhas de bambu e pétalas de sakura que caem suavemente com o vento."""
    def __init__(self, map_cols: int, map_rows: int):
        self.map_cols = map_cols
        self.map_rows = map_rows
        self.reset(random_z=True)

    def reset(self, random_z: bool = False):
        self.wx = random.uniform(0, self.map_cols)
        self.wy = random.uniform(0, self.map_rows)
        self.wz = random.uniform(1.0, 6.0) if random_z else random.uniform(5.0, 7.0)
        self.vx = random.uniform(0.4, 1.2)
        self.vy = random.uniform(0.2, 0.8)
        self.vz = random.uniform(-0.6, -1.2)
        self.is_sakura = random.random() < 0.25
        self.color = COLOR_SAKURA_PINK if self.is_sakura else COLOR_BAMBOO_LEAF
        self.size = 3 if self.is_sakura else 4
        self.flutter_time = random.uniform(0, math.pi * 2)

    def update(self, dt: float):
        self.flutter_time += dt * 3.0
        self.wx += (self.vx + math.sin(self.flutter_time) * 0.4) * dt
        self.wy += (self.vy + math.cos(self.flutter_time) * 0.3) * dt
        self.wz += self.vz * dt
        if self.wz <= 0 or self.wx > self.map_cols or self.wy > self.map_rows:
            self.reset(random_z=False)

    def render(self, surface: pygame.Surface, camera):
        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        pygame.draw.circle(surface, self.color, (sx, sy), self.size)


class FloatingBanner:
    """Textos estilizados de combate (CLASH, PARRY, IAI FLASH, VICTORY)."""
    def __init__(self, text: str, wx: float, wy: float, wz: float = 1.6, color=COLOR_WHITE, duration: float = 1.0):
        self.text = text
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.color = color
        self.duration = duration
        self.age = 0.0

    def update(self, dt: float) -> bool:
        self.age += dt
        self.wz += 0.4 * dt
        return self.age < self.duration

    def render(self, surface: pygame.Surface, camera, font: pygame.font.Font):
        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        alpha = max(0, min(255, int((1.0 - self.age / self.duration) * 255)))
        txt_surf = font.render(self.text, True, self.color)
        txt_surf.set_alpha(alpha)
        # Sombra
        shadow_surf = font.render(self.text, True, (0, 0, 0))
        shadow_surf.set_alpha(alpha)
        rect = txt_surf.get_rect(center=(sx, sy))
        surface.blit(shadow_surf, (rect.x + 2, rect.y + 2))
        surface.blit(txt_surf, rect)
