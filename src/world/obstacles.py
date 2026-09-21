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
        from src.isometric.voxel_renderer import draw_voxel_box

        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

        # Sombra suave na base
        pygame.draw.ellipse(surface, (14, 20, 16), (base_sx - 24, base_sy - 12, 48, 24))

        # Rocha composta por blocos orgânicos de voxel
        # 1. Base rochosa
        draw_voxel_box(
            surface, camera,
            self.wx - self.radius * 0.7, self.wy - self.radius * 0.7, 0.0,
            self.radius * 1.4, self.radius * 1.4, self.height * 0.42,
            COLOR_STONE_DARK
        )
        # 2. Projeção lateral
        draw_voxel_box(
            surface, camera,
            self.wx + self.radius * 0.15, self.wy - self.radius * 0.55, 0.04,
            self.radius * 0.65, self.radius * 0.65, self.height * 0.45,
            (68, 76, 80)
        )
        # 3. Bloco central maciço
        draw_voxel_box(
            surface, camera,
            self.wx - self.radius * 0.55, self.wy - self.radius * 0.55, self.height * 0.38,
            self.radius * 1.1, self.radius * 1.1, self.height * 0.48,
            COLOR_STONE
        )
        # 4. Topo chanfrado angulado
        draw_voxel_box(
            surface, camera,
            self.wx - self.radius * 0.32, self.wy - self.radius * 0.32, self.height * 0.82,
            self.radius * 0.64, self.radius * 0.64, self.height * 0.22,
            (145, 155, 160)
        )
        # 5. Detalhe de musgo feudal no topo da pedra
        draw_voxel_box(
            surface, camera,
            self.wx - self.radius * 0.4, self.wy - self.radius * 0.15, self.height * 0.85,
            self.radius * 0.35, self.radius * 0.35, 0.05,
            (52, 85, 48), outline=False
        )


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
        from src.isometric.voxel_renderer import draw_voxel_box

        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

        # Sombra no chão
        pygame.draw.ellipse(surface, (12, 18, 14), (base_sx - 28, base_sy - 14, 56, 28))

        # 1. Estrutura de cantaria do poço (4 paredes de pedra)
        # Parede Norte
        draw_voxel_box(surface, camera, self.wx - 0.55, self.wy - 0.55, 0.0, 1.10, 0.24, 0.55, COLOR_STONE)
        # Parede Sul
        draw_voxel_box(surface, camera, self.wx - 0.55, self.wy + 0.31, 0.0, 1.10, 0.24, 0.55, COLOR_STONE)
        # Parede Oeste
        draw_voxel_box(surface, camera, self.wx - 0.55, self.wy - 0.31, 0.0, 0.24, 0.62, 0.55, COLOR_STONE_DARK)
        # Parede Leste
        draw_voxel_box(surface, camera, self.wx + 0.31, self.wy - 0.31, 0.0, 0.24, 0.62, 0.55, COLOR_STONE_DARK)

        # Água escura e profunda dentro do poço
        draw_voxel_box(surface, camera, self.wx - 0.31, self.wy - 0.31, 0.15, 0.62, 0.62, 0.05, (16, 32, 45), outline=False)

        # 2. Pilares de sustentação de madeira
        draw_voxel_box(surface, camera, self.wx - 0.48, self.wy - 0.05, 0.55, 0.10, 0.10, 0.70, COLOR_BRIDGE_DARK)
        draw_voxel_box(surface, camera, self.wx + 0.38, self.wy - 0.05, 0.55, 0.10, 0.10, 0.70, COLOR_BRIDGE_DARK)

        # Viga mestra horizontal
        draw_voxel_box(surface, camera, self.wx - 0.54, self.wy - 0.05, 1.22, 1.08, 0.10, 0.08, COLOR_BRIDGE)

        # Carretilha / corda
        draw_voxel_box(surface, camera, self.wx - 0.06, self.wy - 0.05, 1.08, 0.12, 0.10, 0.14, (155, 125, 80))

        # 3. Telhadinho de madeira tradicional em voxel (camadas chanfradas)
        # Camada inferior do telhado
        draw_voxel_box(surface, camera, self.wx - 0.68, self.wy - 0.45, 1.28, 1.36, 0.90, 0.08, COLOR_BRIDGE)
        # Camada superior inclinada
        draw_voxel_box(surface, camera, self.wx - 0.58, self.wy - 0.32, 1.36, 1.16, 0.64, 0.08, COLOR_BRIDGE_DARK)
        # Cumeeira / viga de topo
        draw_voxel_box(surface, camera, self.wx - 0.72, self.wy - 0.08, 1.44, 1.44, 0.16, 0.08, (52, 34, 18))


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
        from src.isometric.voxel_renderer import draw_voxel_box

        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

        # Sombra volumosa no solo
        pygame.draw.ellipse(surface, (12, 18, 14), (base_sx - 38, base_sy - 19, 76, 38))

        # 1. Tronco retorcido de voxel
        # Raízes / Base
        draw_voxel_box(surface, camera, self.wx - 0.32, self.wy - 0.32, 0.0, 0.64, 0.64, 0.65, (52, 34, 20))
        # Tronco intermediário com ligeira inclinação
        draw_voxel_box(surface, camera, self.wx - 0.26, self.wy - 0.22, 0.62, 0.52, 0.52, 0.65, (66, 42, 26))
        # Tronco superior
        draw_voxel_box(surface, camera, self.wx - 0.20, self.wy - 0.16, 1.22, 0.42, 0.42, 0.55, (78, 50, 32))

        # Galhos laterais
        draw_voxel_box(surface, camera, self.wx - 0.58, self.wy - 0.16, 1.35, 0.40, 0.28, 0.24, (56, 36, 22))
        draw_voxel_box(surface, camera, self.wx + 0.18, self.wy - 0.24, 1.42, 0.44, 0.32, 0.24, (56, 36, 22))

        # 2. Copa de Sakura volumétrica em blocos de voxel
        # Folhagens de base mais escuras
        draw_voxel_box(surface, camera, self.wx - 0.85, self.wy - 0.38, 1.50, 0.52, 0.52, 0.45, (200, 110, 145))
        draw_voxel_box(surface, camera, self.wx + 0.35, self.wy - 0.55, 1.55, 0.55, 0.52, 0.45, (215, 125, 160))
        draw_voxel_box(surface, camera, self.wx - 0.38, self.wy + 0.35, 1.52, 0.52, 0.55, 0.45, (225, 135, 170))

        # Bloco central principal da copa
        draw_voxel_box(surface, camera, self.wx - 0.72, self.wy - 0.72, 1.68, 1.44, 1.44, 0.68, COLOR_SAKURA_PINK)

        # Camada superior de flores
        draw_voxel_box(surface, camera, self.wx - 0.52, self.wy - 0.52, 2.32, 1.04, 1.04, 0.55, (255, 185, 210))

        # Topo em flor branca/rosada
        draw_voxel_box(surface, camera, self.wx - 0.30, self.wy - 0.30, 2.84, 0.60, 0.60, 0.35, (255, 220, 235))
