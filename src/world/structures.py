"""Estruturas voxel reutilizáveis das arenas (desenhadas por cima do terreno)."""
import math

from src.config import COLOR_BRIDGE, COLOR_BRIDGE_DARK, COLOR_GOLD
from src.isometric.voxel_renderer import draw_voxel_box

import pygame


class ArchedBridge:
    """
    Ponte arqueada Taiko-bashi ao longo do eixo Y: `x0` é a borda oeste, `width` a largura do tabuleiro
    e [y_start, y_end) o intervalo de seções de 1 tile. O tabuleiro sobe em degraus de 1/3 de tile.
    """

    def __init__(self, x0: float = 10.0, width: float = 2.0, y_start: int = 7, y_end: int = 16):
        self.x0 = x0
        self.width = width
        self.y_start = y_start
        self.y_end = y_end

    def _arch(self, wy: float) -> float:
        prog = (wy - self.y_start) / (self.y_end - self.y_start)
        return 0.10 + math.sin(prog * math.pi) * 0.38

    def deck_height(self, wx: float, wy: float) -> float:
        """Altura do topo do tabuleiro no degrau que contém wy."""
        step_y = self.y_start + math.floor((wy - self.y_start) * 3.0) / 3.0
        return self._arch(step_y) + 0.08

    def draw(self, surface: pygame.Surface, camera, time_val: float):
        x0, x1 = self.x0, self.x0 + self.width
        for y_idx in range(self.y_start, self.y_end):
            arch_z = self._arch(y_idx + 0.5)

            # Sombra da seção no leito do lago
            shadow = [camera.apply(x0, y_idx, -0.15), camera.apply(x1, y_idx, -0.15),
                      camera.apply(x1, y_idx + 1.0, -0.15), camera.apply(x0, y_idx + 1.0, -0.15)]
            pygame.draw.polygon(surface, (12, 22, 28), shadow)

            # Pilares de sustentação descendo até a água a cada 2 tiles, com viga transversal
            if (y_idx - self.y_start) % 2 == 1:
                draw_voxel_box(surface, camera, x0 - 0.08, y_idx + 0.4, -0.15, 0.15, 0.15, arch_z + 0.15, COLOR_BRIDGE_DARK, outline=True)
                draw_voxel_box(surface, camera, x1 - 0.07, y_idx + 0.4, -0.15, 0.15, 0.15, arch_z + 0.15, COLOR_BRIDGE_DARK, outline=True)
                draw_voxel_box(surface, camera, x0 - 0.05, y_idx + 0.4, arch_z - 0.08, self.width + 0.10, 0.14, 0.08, (52, 32, 20), outline=True)

            # Tabuleiro de tábuas de cedro em 3 degraus por tile
            for step_i in range(3):
                sy = y_idx + step_i * (1.0 / 3.0)
                draw_voxel_box(surface, camera, x0, sy, self._arch(sy), self.width, 0.31, 0.08, COLOR_BRIDGE, outline=True, texture="planks")

            # Corrimãos oeste e leste
            for rail_x, post_x, cap_x in ((x0 - 0.06, x0 - 0.08, x0 - 0.05), (x1 - 0.06, x1 - 0.08, x1 - 0.05)):
                draw_voxel_box(surface, camera, rail_x, y_idx + 0.1, arch_z + 0.08, 0.12, 0.12, 0.32, COLOR_BRIDGE_DARK, outline=True)
                draw_voxel_box(surface, camera, rail_x, y_idx + 0.8, arch_z + 0.08, 0.12, 0.12, 0.32, COLOR_BRIDGE_DARK, outline=True)
                draw_voxel_box(surface, camera, cap_x, y_idx, arch_z + 0.38, 0.10, 1.0, 0.07, (120, 68, 42), outline=True)
                if y_idx in (self.y_start, self.y_end - 1):
                    draw_voxel_box(surface, camera, post_x, y_idx + 0.1, arch_z + 0.40, 0.16, 0.16, 0.12, COLOR_GOLD, outline=False)


class PlankBridge:
    """Ponte plana de tábuas sobre um canal, ao longo do eixo Y: [y_start, y_end) em seções de 1 tile e corrimão baixo."""

    DECK_Z = 0.10

    def __init__(self, x0: float = 10.0, width: float = 2.0, y_start: int = 7, y_end: int = 15):
        self.x0 = x0
        self.width = width
        self.y_start = y_start
        self.y_end = y_end

    def deck_height(self, wx: float, wy: float) -> float:
        return self.DECK_Z + 0.08

    def draw(self, surface: pygame.Surface, camera, time_val: float):
        x0, x1 = self.x0, self.x0 + self.width
        for y_idx in range(self.y_start, self.y_end):
            shadow = [camera.apply(x0, y_idx, -0.10), camera.apply(x1, y_idx, -0.10),
                      camera.apply(x1, y_idx + 1.0, -0.10), camera.apply(x0, y_idx + 1.0, -0.10)]
            pygame.draw.polygon(surface, (16, 22, 26), shadow)
            if (y_idx - self.y_start) % 2 == 0:
                for px in (x0 - 0.05, x1 - 0.07):
                    draw_voxel_box(surface, camera, px, y_idx + 0.4, -0.10, 0.12, 0.12, self.DECK_Z + 0.32, COLOR_BRIDGE_DARK, outline=True)
            for step_i in range(3):
                sy = y_idx + step_i * (1.0 / 3.0)
                draw_voxel_box(surface, camera, x0, sy, self.DECK_Z, self.width, 0.31, 0.08, COLOR_BRIDGE, outline=True, texture="planks")
            for rail_x in (x0 - 0.05, x1 - 0.07):
                draw_voxel_box(surface, camera, rail_x, y_idx, self.DECK_Z + 0.08, 0.12, 1.0, 0.05, COLOR_BRIDGE_DARK, outline=True)


class RoofBeam:
    """
    Viga de madeira sobre um vão entre telhados, ao longo do eixo X: o convés vai de `x0` a `x1` (já com o
    apoio nos dois telhados) e ocupa [y0, y1]. É a rota sem salto sobre os becos (Telhados de Iga).
    """

    DECK_Z = 0.06

    def __init__(self, x0: float, y0: float, x1: float, y1: float):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1

    def deck_height(self, wx: float, wy: float) -> float:
        return self.DECK_Z + 0.22

    def draw(self, surface: pygame.Surface, camera, time_val: float):
        x0, y0, x1, y1 = self.x0, self.y0, self.x1, self.y1
        pygame.draw.polygon(surface, (10, 12, 18), [camera.apply(x0 + 0.2, y0, 0.0), camera.apply(x1 - 0.2, y0, 0.0),
                                                      camera.apply(x1 - 0.2, y1, 0.0), camera.apply(x0 + 0.2, y1, 0.0)])
        # Duas vigas mestras sob as tábuas, apoiadas nos telhados
        for sy in (y0 + 0.12, y1 - 0.40):
            draw_voxel_box(surface, camera, x0, sy, 0.0, x1 - x0, 0.28, 0.12, (86, 58, 38), outline=True, texture="planks")
        slat = 0.46
        steps = int((x1 - x0) / 0.5)
        for i in range(steps):
            sx = x0 + 0.04 + i * (x1 - x0 - 0.08) / steps
            color = (146, 108, 72) if i % 2 == 0 else (132, 96, 64)
            draw_voxel_box(surface, camera, sx, y0, 0.12, min(slat, x1 - sx), y1 - y0, 0.06, color, outline=True)
        # Cordas de amarração nas pontas (referência visual de que a viga está presa)
        for ex in (x0 + 0.35, x1 - 0.55):
            draw_voxel_box(surface, camera, ex, y0 - 0.02, 0.17, 0.10, y1 - y0 + 0.04, 0.05, (176, 146, 98), outline=False)
