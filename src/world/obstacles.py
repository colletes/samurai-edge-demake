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
    """Árvore ancestral com tronco grosso, raízes expostas e copa de sakura em camadas floridas."""
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.radius = 0.8
        self.height = 3.6

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

        # Sombra ampla no solo
        pygame.draw.ellipse(surface, (12, 18, 14), (base_sx - 48, base_sy - 24, 96, 48))

        # 1. Raízes expostas retorcidas sobre o solo musgoso
        draw_voxel_box(surface, camera, self.wx - 0.55, self.wy - 0.45, 0.0, 0.35, 0.30, 0.25, (45, 28, 16), outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.20, self.wy - 0.40, 0.0, 0.30, 0.35, 0.22, (45, 28, 16), outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.35, self.wy + 0.25, 0.0, 0.30, 0.30, 0.20, (50, 32, 18), outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.15, self.wy + 0.20, 0.0, 0.35, 0.30, 0.22, (45, 28, 16), outline=True)

        # Base central do tronco ancestral
        draw_voxel_box(surface, camera, self.wx - 0.42, self.wy - 0.42, 0.0, 0.84, 0.84, 0.70, (52, 34, 20), outline=True)

        # Tronco intermediário com nó de casca
        draw_voxel_box(surface, camera, self.wx - 0.35, self.wy - 0.32, 0.65, 0.70, 0.64, 0.75, (66, 42, 26), outline=True)
        # Detalhe de musgo na casca
        draw_voxel_box(surface, camera, self.wx - 0.38, self.wy - 0.10, 0.80, 0.10, 0.35, 0.40, (48, 75, 42), outline=False)

        # Bifurcação dos galhos principais
        # Galho Oeste/Norte
        draw_voxel_box(surface, camera, self.wx - 0.75, self.wy - 0.28, 1.35, 0.55, 0.45, 0.40, (58, 38, 24), outline=True)
        draw_voxel_box(surface, camera, self.wx - 1.10, self.wy - 0.25, 1.65, 0.50, 0.38, 0.35, (54, 34, 22), outline=True)

        # Galho Leste/Sul
        draw_voxel_box(surface, camera, self.wx + 0.20, self.wy - 0.30, 1.35, 0.60, 0.45, 0.40, (58, 38, 24), outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.65, self.wy - 0.15, 1.65, 0.55, 0.38, 0.35, (54, 34, 22), outline=True)

        # Galho Central erguido
        draw_voxel_box(surface, camera, self.wx - 0.25, self.wy - 0.22, 1.35, 0.50, 0.44, 0.65, (68, 44, 28), outline=True)

        # 2. Nuvens volumétricas de flores de Sakura (Camadas orgânicas)
        c_deep = (195, 95, 138)
        c_mid = (225, 125, 168)
        c_light = (248, 165, 202)
        c_blush = (255, 195, 220)
        c_white = (255, 230, 242)

        # Nuvem Oeste (baixa e expansiva)
        draw_voxel_box(surface, camera, self.wx - 1.60, self.wy - 0.75, 1.80, 1.10, 1.00, 0.65, c_deep, outline=True)
        draw_voxel_box(surface, camera, self.wx - 1.45, self.wy - 0.60, 2.35, 0.85, 0.80, 0.50, c_light, outline=True)

        # Nuvem Leste (baixa e expansiva)
        draw_voxel_box(surface, camera, self.wx + 0.55, self.wy - 0.80, 1.80, 1.20, 1.05, 0.65, c_deep, outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.65, self.wy - 0.65, 2.35, 0.90, 0.85, 0.50, c_light, outline=True)

        # Nuvem Sul / Frente
        draw_voxel_box(surface, camera, self.wx - 0.65, self.wy + 0.35, 1.85, 1.05, 0.95, 0.60, c_mid, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.45, self.wy + 0.45, 2.35, 0.75, 0.70, 0.45, c_blush, outline=True)

        # Copa Central Principal (Maciça e alta)
        draw_voxel_box(surface, camera, self.wx - 1.05, self.wy - 1.05, 2.10, 2.10, 2.10, 0.85, c_mid, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.85, self.wy - 0.85, 2.85, 1.70, 1.70, 0.70, c_light, outline=True)

        # Domo superior florido
        draw_voxel_box(surface, camera, self.wx - 0.60, self.wy - 0.60, 3.45, 1.20, 1.20, 0.55, c_blush, outline=True)
        # Pico em flores brancas
        draw_voxel_box(surface, camera, self.wx - 0.35, self.wy - 0.35, 3.90, 0.70, 0.70, 0.35, c_white, outline=True)


class Tsukubai(Well):
    """
    Lavatório ritual tradicional japonês de pedra esculpida (Tsukubai).
    Herda de Well para preservar 100% da compatibilidade de colisão e atributos.
    """
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy)
        self.radius = 0.85

    def render(self, surface: pygame.Surface, camera):
        from src.isometric.voxel_renderer import draw_voxel_box

        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)
        # Sombra no solo
        pygame.draw.ellipse(surface, (12, 18, 14), (base_sx - 28, base_sy - 14, 56, 28))

        c_stone = (78, 85, 80)
        c_moss = (45, 75, 42)
        c_bamboo = (65, 140, 55)

        # 1. Base e Bacia de pedra esculpida com musgo
        draw_voxel_box(surface, camera, self.wx - 0.55, self.wy - 0.55, 0.0, 1.10, 1.10, 0.65, c_stone, outline=True)
        # Musgo viçoso nas laterais
        draw_voxel_box(surface, camera, self.wx - 0.58, self.wy - 0.30, 0.10, 0.12, 0.60, 0.45, c_moss, outline=False)
        draw_voxel_box(surface, camera, self.wx + 0.20, self.wy + 0.50, 0.05, 0.35, 0.12, 0.50, c_moss, outline=False)

        # 2. Espelho d'água dentro da bacia
        draw_voxel_box(surface, camera, self.wx - 0.35, self.wy - 0.35, 0.45, 0.70, 0.70, 0.15, (25, 75, 110), outline=False)
        draw_voxel_box(surface, camera, self.wx - 0.25, self.wy - 0.25, 0.58, 0.50, 0.50, 0.04, (65, 175, 215), outline=False)

        # 3. Bica de bambu (Kakehi)
        draw_voxel_box(surface, camera, self.wx + 0.65, self.wy - 0.45, 0.0, 0.16, 0.16, 0.95, c_bamboo, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.15, self.wy - 0.42, 0.80, 0.85, 0.12, 0.12, c_bamboo, outline=True)

        # 4. Concha de madeira cerimonial (Hishaku) atravessada sobre a bacia
        draw_voxel_box(surface, camera, self.wx - 0.45, self.wy - 0.05, 0.68, 0.90, 0.05, 0.05, (160, 120, 75), outline=False)
        draw_voxel_box(surface, camera, self.wx - 0.48, self.wy - 0.10, 0.65, 0.16, 0.16, 0.12, (140, 100, 60), outline=True)


class ToriiGate:
    """
    Portal sagrado xintoísta em madeira nobre (Torii).
    As duas colunas possuem colisão individual para permitir passagem desimpedida pelo centro da via.
    """
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.radius = 1.6
        self.height = 3.8
        self.col_radius = 0.26

    def check_collision(self, px: float, py: float, p_radius: float = 0.3) -> tuple[bool, float, float]:
        """Verifica colisão com as duas colunas laterais (permitindo cruzar o centro livremente)."""
        left_col_x = self.wx - 1.05
        right_col_x = self.wx + 1.05
        col_y = self.wy

        min_dist = self.col_radius + p_radius
        for cx in (left_col_x, right_col_x):
            dist = math.hypot(px - cx, py - col_y)
            if dist < min_dist:
                overlap = min_dist - dist
                nx = (px - cx) / dist if dist > 0.0001 else 1.0
                ny = (py - col_y) / dist if dist > 0.0001 else 0.0
                return True, nx * overlap, ny * overlap
        return False, 0.0, 0.0

    def render(self, surface: pygame.Surface, camera):
        from src.isometric.voxel_renderer import draw_voxel_box

        c_wood = (72, 42, 28)
        c_dark = (48, 28, 20)

        # Pedras de base
        draw_voxel_box(surface, camera, self.wx - 1.35, self.wy - 0.25, 0.0, 0.50, 0.50, 0.15, (60, 65, 68), outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.85, self.wy - 0.25, 0.0, 0.50, 0.50, 0.15, (60, 65, 68), outline=True)

        # Colunas principais (Hashira)
        col_h = 3.2
        draw_voxel_box(surface, camera, self.wx - 1.28, self.wy - 0.18, 0.15, 0.36, 0.36, col_h, c_wood, outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.92, self.wy - 0.18, 0.15, 0.36, 0.36, col_h, c_wood, outline=True)

        # Travessa inferior (Nuki)
        draw_voxel_box(surface, camera, self.wx - 1.55, self.wy - 0.12, 2.30, 3.10, 0.24, 0.20, c_wood, outline=True)

        # Travessa superior principal (Kasagi & Shimagi)
        draw_voxel_box(surface, camera, self.wx - 1.75, self.wy - 0.16, col_h + 0.15, 3.50, 0.32, 0.26, c_wood, outline=True)
        draw_voxel_box(surface, camera, self.wx - 1.90, self.wy - 0.20, col_h + 0.38, 3.80, 0.40, 0.22, c_dark, outline=True)

        # Tábua central cerimonial (Gakuzuka)
        draw_voxel_box(surface, camera, self.wx - 0.15, self.wy - 0.10, 2.50, 0.30, 0.20, 0.80, (40, 24, 16), outline=False)


class StoneLantern:
    """
    Lanterna tradicional japonesa esculpida em granito (Ishi-doro) com câmara de luz âmbar acolhedora.
    """
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.radius = 0.35
        self.height = 1.05

    def check_collision(self, px: float, py: float, p_radius: float = 0.3) -> tuple[bool, float, float]:
        dist = math.hypot(px - self.wx, py - self.wy)
        min_dist = self.radius + p_radius
        if dist < min_dist:
            overlap = min_dist - dist
            nx = (px - self.wx) / dist if dist > 0.0001 else 1.0
            ny = (py - self.wy) / dist if dist > 0.0001 else 0.0
            return True, nx * overlap, ny * overlap
        return False, 0.0, 0.0

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        from src.isometric.voxel_renderer import draw_voxel_box

        # Base de pedra
        draw_voxel_box(surface, camera, self.wx - 0.22, self.wy - 0.22, 0.0, 0.44, 0.44, 0.15, (65, 70, 72), outline=True)
        # Pilar
        draw_voxel_box(surface, camera, self.wx - 0.10, self.wy - 0.10, 0.15, 0.20, 0.20, 0.40, (75, 80, 84), outline=True)

        # Brilho dinâmico acolhedor
        glow_pulse = math.sin(time_val * 4.0 + self.wx * 3.0) * 15
        r_glow = min(255, max(220, int(250 + glow_pulse)))
        g_glow = min(220, max(180, int(195 + glow_pulse * 0.8)))
        b_glow = min(90, max(50, int(70 + glow_pulse * 0.5)))
        glow_color = (r_glow, g_glow, b_glow)

        # Câmara de luz (Hibukuro)
        draw_voxel_box(surface, camera, self.wx - 0.16, self.wy - 0.16, 0.55, 0.32, 0.32, 0.22, glow_color, outline=False)

        # Telhado de pedra (Kasa)
        draw_voxel_box(surface, camera, self.wx - 0.28, self.wy - 0.28, 0.77, 0.56, 0.56, 0.14, (50, 54, 58), outline=True)
        # Ornamento de topo (Hoju)
        draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, 0.91, 0.16, 0.16, 0.10, (65, 70, 72), outline=False)

