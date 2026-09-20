"""
Obstáculos rígidos do cenário: Rochas, Poço de Pedra e Árvores.
Bloqueiam movimentação e fazem lâminas ricochetearem com faíscas.
"""
import math
import pygame
from src.config import (
    COLOR_STONE, COLOR_STONE_DARK, COLOR_BRIDGE, COLOR_BRIDGE_DARK,
    COLOR_SAKURA_PINK
)

class Rock:
    """Rocha maciça de cantaria que bloqueia movimento e reflete golpes."""
    def __init__(self, wx: float, wy: float, radius: float = 0.65, height: float = 0.9):
        self.wx = wx
        self.wy = wy
        self.radius = radius
        self.height = height

    def check_collision(self, px: float, py: float, p_radius: float = 0.3) -> tuple[bool, float, float]:
        """Retorna se colidiu e o vetor de repulsão normalizado."""
        dist = math.hypot(px - self.wx, py - self.wy)
        min_dist = self.radius + p_radius
        if dist < min_dist:
            overlap = min_dist - dist
            if dist > 0.0001:
                nx = (px - self.wx) / dist
                ny = (py - self.wy) / dist
            else:
                nx, ny = 1.0, 0.0
            return True, nx * overlap, ny * overlap
        return False, 0.0, 0.0

    def render(self, surface: pygame.Surface, camera):
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)
        top_sx, top_sy = camera.apply(self.wx, self.wy, self.height)

        # Sombra na base
        pygame.draw.ellipse(surface, (15, 22, 18), (base_sx - 24, base_sy - 12, 48, 24))

        # Corpo da rocha (Voxel estilizado)
        poly_points = [
            (base_sx - 20, base_sy - 4),
            (base_sx + 20, base_sy - 4),
            (top_sx + 15, top_sy + 2),
            (top_sx - 14, top_sy - 6),
            (top_sx - 22, top_sy + 4)
        ]
        pygame.draw.polygon(surface, COLOR_STONE_DARK, poly_points)

        # Face iluminada superior
        top_poly = [
            (top_sx - 14, top_sy - 6),
            (top_sx + 15, top_sy + 2),
            (top_sx + 6, top_sy - 12),
            (top_sx - 12, top_sy - 15)
        ]
        pygame.draw.polygon(surface, COLOR_STONE, top_poly)
        # Detalhes de musgo
        pygame.draw.circle(surface, (50, 75, 45), (top_sx - 3, top_sy - 2), 4)
        pygame.draw.circle(surface, (50, 75, 45), (base_sx + 5, base_sy - 6), 5)


class Well:
    """Poço japonês tradicional de pedra com cobertura de telhas de madeira."""
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.radius = 0.85
        self.height = 1.2

    def check_collision(self, px: float, py: float, p_radius: float = 0.3) -> tuple[bool, float, float]:
        dist = math.hypot(px - self.wx, py - self.wy)
        min_dist = self.radius + p_radius
        if dist < min_dist:
            overlap = min_dist - dist
            if dist > 0.0001:
                nx = (px - self.wx) / dist
                ny = (py - self.wy) / dist
            else:
                nx, ny = 1.0, 0.0
            return True, nx * overlap, ny * overlap
        return False, 0.0, 0.0

    def render(self, surface: pygame.Surface, camera):
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)
        wall_sx, wall_sy = camera.apply(self.wx, self.wy, 0.5)
        roof_sx, roof_sy = camera.apply(self.wx, self.wy, 1.4)

        # Sombra no chão
        pygame.draw.ellipse(surface, (12, 18, 14), (base_sx - 28, base_sy - 14, 56, 28))

        # Base de pedra cilíndrica
        pygame.draw.ellipse(surface, COLOR_STONE_DARK, (base_sx - 24, base_sy - 10, 48, 20))
        # Paredes de pedra do poço
        pygame.draw.rect(surface, COLOR_STONE, (base_sx - 24, wall_sy, 48, base_sy - wall_sy))
        pygame.draw.ellipse(surface, (20, 24, 28), (wall_sx - 22, wall_sy - 9, 44, 18)) # Abertura escura da água

        # Vigas de suporte de madeira
        post_l_x, post_l_y = base_sx - 18, wall_sy
        post_r_x, post_r_y = base_sx + 18, wall_sy
        roof_l_x, roof_l_y = roof_sx - 20, roof_sy + 8
        roof_r_x, roof_r_y = roof_sx + 20, roof_sy + 8

        pygame.draw.line(surface, COLOR_BRIDGE_DARK, (post_l_x, post_l_y), (roof_l_x, roof_l_y), 4)
        pygame.draw.line(surface, COLOR_BRIDGE_DARK, (post_r_x, post_r_y), (roof_r_x, roof_r_y), 4)

        # Telhadinho de madeira (roof)
        roof_poly = [
            (roof_sx - 26, roof_sy + 10),
            (roof_sx + 26, roof_sy + 10),
            (roof_sx + 18, roof_sy - 10),
            (roof_sx - 18, roof_sy - 10),
        ]
        pygame.draw.polygon(surface, COLOR_BRIDGE, roof_poly)
        pygame.draw.polygon(surface, COLOR_BRIDGE_DARK, roof_poly, 2)


class AncientTree:
    """Árvore ancestral com tronco grosso e copa de sakura florida."""
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.radius = 0.8
        self.height = 2.4

    def check_collision(self, px: float, py: float, p_radius: float = 0.3) -> tuple[bool, float, float]:
        dist = math.hypot(px - self.wx, py - self.wy)
        min_dist = self.radius + p_radius
        if dist < min_dist:
            overlap = min_dist - dist
            if dist > 0.0001:
                nx = (px - self.wx) / dist
                ny = (py - self.wy) / dist
            else:
                nx, ny = 1.0, 0.0
            return True, nx * overlap, ny * overlap
        return False, 0.0, 0.0

    def render(self, surface: pygame.Surface, camera):
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)
        trunk_sx, trunk_sy = camera.apply(self.wx, self.wy, 1.2)
        crown_sx, crown_sy = camera.apply(self.wx, self.wy, self.height)

        # Sombra
        pygame.draw.ellipse(surface, (12, 18, 14), (base_sx - 36, base_sy - 18, 72, 36))

        # Tronco retorcido de madeira escura
        pygame.draw.line(surface, (55, 35, 22), (base_sx, base_sy), (trunk_sx - 6, trunk_sy), 14)
        pygame.draw.line(surface, (75, 48, 28), (trunk_sx - 6, trunk_sy), (crown_sx, crown_sy), 10)

        # Copa da árvore em camadas de sakura
        pygame.draw.circle(surface, (200, 110, 145), (crown_sx - 20, crown_sy), 26)
        pygame.draw.circle(surface, (215, 125, 160), (crown_sx + 20, crown_sy - 6), 28)
        pygame.draw.circle(surface, COLOR_SAKURA_PINK, (crown_sx, crown_sy - 16), 32)
        pygame.draw.circle(surface, (255, 185, 210), (crown_sx + 4, crown_sy - 22), 20)
