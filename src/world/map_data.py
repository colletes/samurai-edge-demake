"""
Definição do mapa isométrico, tiles de terreno (Grama, Terra, Lago, Ponte)
e posicionamento de bambus, pedras, poço e árvores.
"""
import math
import random
import pygame
from src.config import (
    MAP_COLS, MAP_ROWS, HALF_TILE_W, HALF_TILE_H,
    COLOR_GRASS, COLOR_GRASS_LIGHT, COLOR_EARTH,
    COLOR_WATER, COLOR_WATER_HIGHLIGHT, COLOR_BRIDGE, COLOR_BRIDGE_DARK
)
from src.world.bamboo import Bamboo
from src.world.obstacles import Rock, Well, AncientTree
from src.isometric.iso_math import world_to_iso

# Constantes de Tile de Terreno
TILE_GRASS = 0
TILE_EARTH = 1
TILE_WATER = 2
TILE_BRIDGE = 3

class GameMap:
    def __init__(self):
        self.cols = MAP_COLS
        self.rows = MAP_ROWS
        self.tiles = [[TILE_GRASS for _ in range(self.rows)] for _ in range(self.cols)]

        # Listas de objetos no mundo
        self.bamboos: list[Bamboo] = []
        self.rocks: list[Rock] = []
        self.well: Well | None = None
        self.trees: list[AncientTree] = []

        self._build_terrain()
        self._populate_scenery()

    def _build_terrain(self):
        """Constrói o traçado do caminho, o lago sereno e a ponte de madeira."""
        # 1. Caminho de terra central (cruzando a arena)
        for x in range(self.cols):
            for y in range(self.rows):
                if abs(x - y) <= 2:
                    self.tiles[x][y] = TILE_EARTH

        # 2. Laguinho orgânico (elipse inclinada)
        lake_center_x = 11.0
        lake_center_y = 11.0
        for x in range(self.cols):
            for y in range(self.rows):
                # Distância elíptica
                dx = x - lake_center_x
                dy = y - lake_center_y
                dist = math.hypot(dx * 1.1, dy * 0.9)
                if dist < 4.2:
                    self.tiles[x][y] = TILE_WATER

        # 3. Ponte de madeira cruzando o laguinho (ligando as duas margens)
        for y in range(int(lake_center_y - 4), int(lake_center_y + 5)):
            if 0 <= y < self.rows:
                # Ponte com 2 tiles de largura
                self.tiles[10][y] = TILE_BRIDGE
                self.tiles[11][y] = TILE_BRIDGE

    def _populate_scenery(self):
        """Posiciona bambus, pedras, o poço e árvores de sakura."""
        # 1. Poço de Pedra Tradicional (no canto do caminho)
        self.well = Well(wx=6.5, wy=6.5)

        # 2. Rochas sólidas estratégicas para bloqueio
        self.rocks.append(Rock(wx=6.0, wy=14.5, radius=0.7, height=0.9))
        self.rocks.append(Rock(wx=15.5, wy=7.0, radius=0.6, height=0.8))
        self.rocks.append(Rock(wx=16.0, wy=15.0, radius=0.75, height=1.0))
        self.rocks.append(Rock(wx=3.5, wy=10.0, radius=0.55, height=0.75))

        # 3. Árvores Ancestrais de Sakura
        self.trees.append(AncientTree(wx=4.0, wy=4.0))
        self.trees.append(AncientTree(wx=17.5, wy=17.5))

        # 4. Floresta de Bambus Cortáveis
        # Criar aglomerados densos para permitir emboscadas e cobertura
        random.seed(42) # Semente fixa para mapa consistente e belo
        for x in range(self.cols):
            for y in range(self.rows):
                # Não colocar bambu na água, na ponte ou no meio exato do caminho
                tile = self.tiles[x][y]
                if tile in (TILE_WATER, TILE_BRIDGE):
                    continue

                # Evitar sobrepor obstáculos rígidos
                too_close_obstacle = False
                for r in self.rocks:
                    if math.hypot(x - r.wx, y - r.wy) < 1.2:
                        too_close_obstacle = True
                        break
                if self.well and math.hypot(x - self.well.wx, y - self.well.wy) < 1.4:
                    too_close_obstacle = True
                for t in self.trees:
                    if math.hypot(x - t.wx, y - t.wy) < 1.5:
                        too_close_obstacle = True
                if too_close_obstacle:
                    continue

                # Probabilidade alta nas laterais, moderada perto do caminho
                dist_to_center = math.hypot(x - 11, y - 11)
                chance = 0.65 if dist_to_center > 5.5 else 0.15

                if random.random() < chance:
                    offset_x = random.uniform(-0.35, 0.35)
                    offset_y = random.uniform(-0.35, 0.35)
                    self.bamboos.append(Bamboo(x + 0.5 + offset_x, y + 0.5 + offset_y))

    def is_water(self, wx: float, wy: float) -> bool:
        """Verifica se uma coordenada de mundo está sobre água não coberta por ponte."""
        tx = int(math.floor(wx))
        ty = int(math.floor(wy))
        if 0 <= tx < self.cols and 0 <= ty < self.rows:
            return self.tiles[tx][ty] == TILE_WATER
        return False

    def is_hidden_in_bamboo(self, wx: float, wy: float) -> bool:
        """Verifica se um samurai está sob a camuflagem de qualquer bambu intacto."""
        for b in self.bamboos:
            if b.is_samurai_hidden(wx, wy):
                return True
        return False

    def render_terrain(self, surface: pygame.Surface, camera, time_val: float):
        """Renderiza os tiles de chão (Grama, Terra, Lago e Ponte)."""
        for x in range(self.cols):
            for y in range(self.rows):
                tile = self.tiles[x][y]

                # Coordenadas dos 4 vértices do diamante isométrico
                p_top = camera.apply(x, y, 0.0)
                p_right = camera.apply(x + 1, y, 0.0)
                p_bottom = camera.apply(x + 1, y + 1, 0.0)
                p_left = camera.apply(x, y + 1, 0.0)
                quad = [p_top, p_right, p_bottom, p_left]

                # Pular se estiver fora da tela para otimização
                if p_bottom[1] < -50 or p_top[1] > surface.get_height() + 50 or \
                   p_right[0] < -50 or p_left[0] > surface.get_width() + 50:
                    continue

                if tile == TILE_GRASS:
                    # Alternância sutil de tons de grama
                    c = COLOR_GRASS_LIGHT if (x + y) % 3 == 0 else COLOR_GRASS
                    pygame.draw.polygon(surface, c, quad)
                    pygame.draw.polygon(surface, (28, 44, 24), quad, 1)

                elif tile == TILE_EARTH:
                    pygame.draw.polygon(surface, COLOR_EARTH, quad)
                    pygame.draw.polygon(surface, (44, 34, 22), quad, 1)

                elif tile == TILE_WATER:
                    # Efeito de ondulação de água no lago
                    wave_c = COLOR_WATER_HIGHLIGHT if math.sin(time_val * 3.0 + x * 0.8 + y * 0.8) > 0.4 else COLOR_WATER
                    pygame.draw.polygon(surface, wave_c, quad)
                    pygame.draw.polygon(surface, (22, 55, 75), quad, 1)

                elif tile == TILE_BRIDGE:
                    # Ponte de madeira sobre a água
                    # Altura ligeiramente elevada (wz = 0.15)
                    bp_top = camera.apply(x, y, 0.15)
                    bp_right = camera.apply(x + 1, y, 0.15)
                    bp_bottom = camera.apply(x + 1, y + 1, 0.15)
                    bp_left = camera.apply(x, y + 1, 0.15)
                    b_quad = [bp_top, bp_right, bp_bottom, bp_left]

                    # Sombra da ponte na água
                    pygame.draw.polygon(surface, (18, 32, 42), quad)
                    # Tablado de madeira
                    pygame.draw.polygon(surface, COLOR_BRIDGE, b_quad)
                    pygame.draw.polygon(surface, COLOR_BRIDGE_DARK, b_quad, 2)
                    # Tábuas de madeira desenhadas
                    mid_l = ((bp_top[0] + bp_left[0]) // 2, (bp_top[1] + bp_left[1]) // 2)
                    mid_r = ((bp_right[0] + bp_bottom[0]) // 2, (bp_right[1] + bp_bottom[1]) // 2)
                    pygame.draw.line(surface, COLOR_BRIDGE_DARK, mid_l, mid_r, 1)
