"""
Definição do mapa isométrico, tiles de terreno (Grama, Terra com lajes Tobi-ishi, Lago Zen com reflexo, Ponte Arqueada Taiko-bashi)
e posicionamento de bambus, pedras, lavatório ritual Tsukubai, portal Torii, lanternas Ishi-doro e árvores de sakura.
"""
import math
import random
import pygame
from src.config import (
    MAP_COLS, MAP_ROWS, HALF_TILE_W, HALF_TILE_H,
    COLOR_GRASS, COLOR_GRASS_LIGHT, COLOR_EARTH,
    COLOR_WATER, COLOR_WATER_HIGHLIGHT, COLOR_BRIDGE, COLOR_BRIDGE_DARK,
    COLOR_GOLD
)
from src.world.bamboo import Bamboo
from src.world.obstacles import Rock, Well, AncientTree, Tsukubai, ToriiGate, StoneLantern
from src.isometric.iso_math import world_to_iso
from src.isometric.voxel_renderer import draw_voxel_box

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
        self.torii_gates: list[ToriiGate] = []
        self.lanterns: list[StoneLantern] = []
        self.fireflies: list[tuple[float, float, float]] = []

        self._build_terrain()
        self._populate_scenery()

    def _build_terrain(self):
        """Constrói o traçado do caminho cerimonial conectado à ponte, o lago zen e a ponte Taiko-bashi."""
        lake_center_x = 11.0
        lake_center_y = 11.0

        # 1. Laguinho zen orgânico (elipse inclinada)
        for x in range(self.cols):
            for y in range(self.rows):
                dx = (x - lake_center_x) * 1.12
                dy = (y - lake_center_y) * 0.90
                dist = math.hypot(dx, dy)
                if dist < 4.2:
                    self.tiles[x][y] = TILE_WATER

        # 2. Ponte de madeira Taiko-bashi cruzando o lago (x=10 e x=11 de y=7 a y=15)
        for y in range(7, 16):
            if 0 <= y < self.rows:
                self.tiles[10][y] = TILE_BRIDGE
                self.tiles[11][y] = TILE_BRIDGE

        # 3. Estrada de terra batida e lajes conectada DIRETAMENTE às duas pontas da ponte
        # Entrada Norte (de y=0 até y=7 em x=10, 11) passando pelo Torii
        for y in range(0, 8):
            self.tiles[10][y] = TILE_EARTH
            self.tiles[11][y] = TILE_EARTH
            if y in (6, 7):
                self.tiles[9][y] = TILE_EARTH
                self.tiles[12][y] = TILE_EARTH

        # Entrada Sul (de y=15 até y=21 em x=10, 11)
        for y in range(15, 22):
            self.tiles[10][y] = TILE_EARTH
            self.tiles[11][y] = TILE_EARTH
            if y in (15, 16):
                self.tiles[9][y] = TILE_EARTH
                self.tiles[12][y] = TILE_EARTH

        # Caminho secundário contornando o lago até o lavatório Tsukubai (wx=6.5, wy=6.5)
        for x in range(6, 11):
            for y in range(6, 8):
                if self.tiles[x][y] not in (TILE_WATER, TILE_BRIDGE):
                    self.tiles[x][y] = TILE_EARTH
        for y in range(6, 10):
            self.tiles[6][y] = TILE_EARTH
            self.tiles[7][y] = TILE_EARTH

    def _populate_scenery(self):
        """Posiciona bambus densos, pedras, lavatório Tsukubai, portal Torii, lanternas e árvores de sakura."""
        # 1. Lavatório Ritual Tradicional Tsukubai (substitui o poço genérico preservando a colisão)
        self.well = Tsukubai(wx=6.5, wy=6.5)

        # 2. Rochas sólidas táticas para bloqueio
        self.rocks.append(Rock(wx=6.0, wy=14.5, radius=0.7, height=0.9))
        self.rocks.append(Rock(wx=15.5, wy=7.0, radius=0.6, height=0.8))
        self.rocks.append(Rock(wx=16.0, wy=15.0, radius=0.75, height=1.0))
        self.rocks.append(Rock(wx=3.5, wy=10.0, radius=0.55, height=0.75))

        # 3. Árvores Ancestrais de Sakura (modelo majestoso)
        self.trees.append(AncientTree(wx=4.0, wy=4.0))
        self.trees.append(AncientTree(wx=17.5, wy=17.5))

        # 4. Portal Torii xintoísta sobre a estrada de acesso norte
        self.torii_gates.append(ToriiGate(wx=10.5, wy=5.0))

        # 5. Lanternas de pedra Ishi-doro iluminando as cabeceiras da ponte e caminhos
        self.lanterns.append(StoneLantern(wx=8.8, wy=6.2))   # Cabeceira Norte Oeste
        self.lanterns.append(StoneLantern(wx=12.2, wy=6.2))  # Cabeceira Norte Leste
        self.lanterns.append(StoneLantern(wx=8.8, wy=15.8))  # Cabeceira Sul Oeste
        self.lanterns.append(StoneLantern(wx=12.2, wy=15.8)) # Cabeceira Sul Leste
        self.lanterns.append(StoneLantern(wx=5.8, wy=7.8))   # Próximo ao Tsukubai

        # 6. Vaga-lumes bioluminescentes (Hotaru)
        self.fireflies = [
            (10.2, 11.8, 0.7), (11.8, 12.5, 0.5), (8.5, 10.2, 0.3),
            (12.5, 9.5, 0.6), (7.8, 7.8, 0.8), (11.0, 6.2, 0.9), (6.2, 6.8, 0.6)
        ]

        # 7. Floresta Densa de Bambus Cortáveis (200+ bambus gerados)
        bamboo_rng = random.Random(42) # Semente fixa para mapa consistente e harmonioso
        for x in range(self.cols):
            for y in range(self.rows):
                # Não colocar bambu na água, na ponte ou na estrada
                tile = self.tiles[x][y]
                if tile in (TILE_WATER, TILE_BRIDGE, TILE_EARTH):
                    continue

                # Evitar sobrepor obstáculos rígidos
                too_close = False
                for r in self.rocks:
                    if math.hypot(x - r.wx, y - r.wy) < 1.3:
                        too_close = True
                        break
                if self.well and math.hypot(x - self.well.wx, y - self.well.wy) < 1.4:
                    too_close = True
                for t in self.trees:
                    if math.hypot(x - t.wx, y - t.wy) < 2.6:
                        too_close = True
                        break
                for tg in self.torii_gates:
                    if math.hypot(x - tg.wx, y - tg.wy) < 1.6:
                        too_close = True
                        break
                for l in self.lanterns:
                    if math.hypot(x - l.wx, y - l.wy) < 0.8:
                        too_close = True
                        break
                if too_close:
                    continue

                # Densidade alta nas laterais, moderada nas clareiras internas
                dist_to_center = math.hypot(x - 11, y - 11)
                chance = 0.72 if dist_to_center > 5.0 else 0.25

                if bamboo_rng.random() < chance:
                    offset_x = bamboo_rng.uniform(-0.35, 0.35)
                    offset_y = bamboo_rng.uniform(-0.35, 0.35)
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
        """Renderiza os tiles de chão com profundidade voxel 3D (Grama, Lajes Tobi-ishi, Lago Zen e Ponte Taiko-bashi)."""
        bridge_drawn = False

        for x in range(self.cols):
            for y in range(self.rows):
                tile = self.tiles[x][y]

                # Coordenadas base (z = 0.0)
                p_top = camera.apply(x, y, 0.0)
                p_right = camera.apply(x + 1, y, 0.0)
                p_bottom = camera.apply(x + 1, y + 1, 0.0)
                p_left = camera.apply(x, y + 1, 0.0)
                quad = [p_top, p_right, p_bottom, p_left]

                # Culling se estiver fora da tela
                if p_bottom[1] < -60 or p_top[1] > surface.get_height() + 60 or \
                   p_right[0] < -60 or p_left[0] > surface.get_width() + 60:
                    continue

                if tile == TILE_GRASS:
                    c = COLOR_GRASS_LIGHT if (x + y) % 3 == 0 else COLOR_GRASS
                    pygame.draw.polygon(surface, c, quad)
                    pygame.draw.polygon(surface, (28, 44, 24), quad, 1)

                elif tile == TILE_EARTH:
                    pygame.draw.polygon(surface, COLOR_EARTH, quad)
                    pygame.draw.polygon(surface, (44, 34, 22), quad, 1)
                    # Lajes de cantaria Tobi-ishi cravadas no caminho
                    if (x + y) % 2 == 0:
                        draw_voxel_box(surface, camera, x + 0.15, y + 0.15, 0.0, 0.70, 0.70, 0.04, (88, 92, 95), outline=True)

                elif tile == TILE_WATER:
                    # Margem rebaixada do lago zen (depressão voxel a z = -0.15)
                    w_top = camera.apply(x, y, -0.15)
                    w_right = camera.apply(x + 1, y, -0.15)
                    w_bottom = camera.apply(x + 1, y + 1, -0.15)
                    w_left = camera.apply(x, y + 1, -0.15)
                    w_quad = [w_top, w_right, w_bottom, w_left]

                    # Barrancos de terra verticais para vizinhos que não são água
                    if y > 0 and self.tiles[x][y - 1] not in (TILE_WATER, TILE_BRIDGE):
                        bank_n = [p_top, p_right, w_right, w_top]
                        pygame.draw.polygon(surface, (36, 26, 18), bank_n)
                        pygame.draw.polygon(surface, (22, 16, 12), bank_n, 1)

                    if x > 0 and self.tiles[x - 1][y] not in (TILE_WATER, TILE_BRIDGE):
                        bank_w = [p_left, p_top, w_top, w_left]
                        pygame.draw.polygon(surface, (46, 32, 22), bank_w)
                        pygame.draw.polygon(surface, (28, 20, 14), bank_w, 1)

                    # Superfície da água com ondulações
                    wave = math.sin(time_val * 3.0 + x * 0.9 + y * 0.9)
                    wave_c = COLOR_WATER_HIGHLIGHT if wave > 0.45 else COLOR_WATER
                    pygame.draw.polygon(surface, wave_c, w_quad)
                    pygame.draw.polygon(surface, (14, 48, 72), w_quad, 1)

                    # Reflexo sutil da lua no espelho d'água
                    if (x == 11 and y in (11, 12)) or (x == 10 and y == 12):
                        ref_sx, ref_sy = camera.apply(x + 0.5, y + 0.5, -0.14)
                        pygame.draw.circle(surface, (120, 205, 240, 180), (ref_sx, ref_sy), 8)

                elif tile == TILE_BRIDGE and not bridge_drawn:
                    # Desenhar a ponte Taiko-bashi em Voxel 3D arqueada por completo uma única vez
                    self._draw_taiko_bashi_bridge(surface, camera, time_val)
                    bridge_drawn = True

    def _draw_taiko_bashi_bridge(self, surface: pygame.Surface, camera, time_val: float):
        """Renderiza a ponte tradicional arqueada japonesa Taiko-bashi em Voxel 3D."""
        bridge_y_start = 7
        bridge_y_end = 16
        total_len = bridge_y_end - bridge_y_start

        for y_idx in range(bridge_y_start, bridge_y_end):
            prog = (y_idx - bridge_y_start + 0.5) / total_len
            arch_z = 0.10 + math.sin(prog * math.pi) * 0.38

            # Sombra da seção no leito do lago
            sh_top = camera.apply(10.0, y_idx, -0.15)
            sh_right = camera.apply(12.0, y_idx, -0.15)
            sh_bot = camera.apply(12.0, y_idx + 1.0, -0.15)
            sh_left = camera.apply(10.0, y_idx + 1.0, -0.15)
            pygame.draw.polygon(surface, (12, 22, 28), [sh_top, sh_right, sh_bot, sh_left])

            # Pilares de sustentação descendo até a água a cada 2 tiles
            if (y_idx - bridge_y_start) % 2 == 1:
                draw_voxel_box(surface, camera, 9.92, y_idx + 0.4, -0.15, 0.15, 0.15, arch_z + 0.15, COLOR_BRIDGE_DARK, outline=True)
                draw_voxel_box(surface, camera, 11.93, y_idx + 0.4, -0.15, 0.15, 0.15, arch_z + 0.15, COLOR_BRIDGE_DARK, outline=True)
                # Viga transversal sob a ponte
                draw_voxel_box(surface, camera, 9.95, y_idx + 0.4, arch_z - 0.08, 2.10, 0.14, 0.08, (52, 32, 20), outline=True)

            # Tabuleiro da ponte (Deck de tábuas de cedro em 3 degraus por tile)
            for step_i in range(3):
                sy = y_idx + step_i * (1.0 / 3.0)
                s_prog = (sy - bridge_y_start) / total_len
                sz = 0.10 + math.sin(s_prog * math.pi) * 0.38
                draw_voxel_box(surface, camera, 10.0, sy, sz, 2.0, 0.31, 0.08, COLOR_BRIDGE, outline=True)

            # Corrimão Oeste (x = 10)
            draw_voxel_box(surface, camera, 9.94, y_idx + 0.1, arch_z + 0.08, 0.12, 0.12, 0.32, COLOR_BRIDGE_DARK, outline=True)
            draw_voxel_box(surface, camera, 9.94, y_idx + 0.8, arch_z + 0.08, 0.12, 0.12, 0.32, COLOR_BRIDGE_DARK, outline=True)
            draw_voxel_box(surface, camera, 9.95, y_idx, arch_z + 0.38, 0.10, 1.0, 0.07, (120, 68, 42), outline=True)
            if y_idx in (bridge_y_start, bridge_y_end - 1):
                draw_voxel_box(surface, camera, 9.92, y_idx + 0.1, arch_z + 0.40, 0.16, 0.16, 0.12, COLOR_GOLD, outline=False)

            # Corrimão Leste (x = 11)
            draw_voxel_box(surface, camera, 11.94, y_idx + 0.1, arch_z + 0.08, 0.12, 0.12, 0.32, COLOR_BRIDGE_DARK, outline=True)
            draw_voxel_box(surface, camera, 11.94, y_idx + 0.8, arch_z + 0.08, 0.12, 0.12, 0.32, COLOR_BRIDGE_DARK, outline=True)
            draw_voxel_box(surface, camera, 11.95, y_idx, arch_z + 0.38, 0.10, 1.0, 0.07, (120, 68, 42), outline=True)
            if y_idx in (bridge_y_start, bridge_y_end - 1):
                draw_voxel_box(surface, camera, 11.92, y_idx + 0.1, arch_z + 0.40, 0.16, 0.16, 0.12, COLOR_GOLD, outline=False)
