"""
Entidade Bambu com estética voxel vertical, suporte a fatiamento por corte e camuflagem.
"""
import math
import random
import pygame
from src.config import (
    COLOR_BAMBOO, COLOR_BAMBOO_LIGHT, COLOR_BAMBOO_LEAF
)
from src.effects.particles import BambooSliceParticle

class Bamboo:
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.total_height = random.uniform(2.8, 3.8) # Altura no espaço z de mundo
        self.radius = 0.18 # Raio de colisão sutil
        self.is_cut = False
        self.stump_height = random.uniform(0.35, 0.65)
        self.wind_offset = random.uniform(0, math.pi * 2)

    def cut(self, slash_dir: tuple[float, float]) -> BambooSliceParticle | None:
        """Corta o bambu se ainda estiver inteiro, gerando o tronco superior que tomba."""
        if self.is_cut:
            return None
        self.is_cut = True
        return BambooSliceParticle(
            wx=self.wx,
            wy=self.wy,
            cut_height=self.stump_height,
            total_height=self.total_height,
            slash_dir=slash_dir
        )

    def is_samurai_hidden(self, sam_wx: float, sam_wy: float) -> bool:
        """Determina se um samurai está escondido sob a folhagem deste bambu em pé."""
        if self.is_cut:
            return False
        dist = math.hypot(self.wx - sam_wx, self.wy - sam_wy)
        return dist < 0.75

    def render(self, surface: pygame.Surface, camera, time_val: float):
        # Y-sort usa a base do bambu
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

        if self.is_cut:
            # Desenha apenas o toco cortado na base
            top_sx, top_sy = camera.apply(self.wx, self.wy, self.stump_height)
            pygame.draw.line(surface, (45, 95, 38), (base_sx, base_sy), (top_sx, top_sy), 6)
            pygame.draw.line(surface, (75, 145, 60), (base_sx, base_sy), (top_sx, top_sy), 3)
            # Ponta cortada diagonal
            pygame.draw.ellipse(surface, (130, 190, 90), (top_sx - 3, top_sy - 2, 7, 4))
            return

        # Bambu em pé (Voxel Stalk vertical com anéis e folhagem balançando)
        wind_sway = math.sin(time_val * 2.0 + self.wind_offset) * 0.08
        top_wx = self.wx + wind_sway
        top_wy = self.wy + wind_sway
        top_sx, top_sy = camera.apply(top_wx, top_wy, self.total_height)

        # Haste principal do bambu (camada de sombra e luz)
        pygame.draw.line(surface, (42, 90, 36), (base_sx, base_sy), (top_sx, top_sy), 6)
        pygame.draw.line(surface, COLOR_BAMBOO, (base_sx, base_sy), (top_sx, top_sy), 4)
        pygame.draw.line(surface, COLOR_BAMBOO_LIGHT, (base_sx, base_sy), (top_sx, top_sy), 2)

        # Anéis/Nós do bambu ao longo do tronco
        segments = int(self.total_height * 3)
        for i in range(1, segments):
            frac = i / segments
            seg_z = self.total_height * frac
            seg_wx = self.wx + wind_sway * frac
            seg_wy = self.wy + wind_sway * frac
            node_sx, node_sy = camera.apply(seg_wx, seg_wy, seg_z)
            pygame.draw.circle(surface, COLOR_BAMBOO_LIGHT, (node_sx, node_sy), 3)

        # Folhagem no topo (clusters de folhas pontudas de bambu)
        leaf_count = 5
        for j in range(leaf_count):
            ang = j * (math.pi * 2 / leaf_count) + wind_sway * 3
            leaf_len = 16
            leaf_end_x = int(top_sx + math.cos(ang) * leaf_len)
            leaf_end_y = int(top_sy + math.sin(ang) * leaf_len * 0.6)
            pygame.draw.line(surface, COLOR_BAMBOO_LEAF, (top_sx, top_sy), (leaf_end_x, leaf_end_y), 3)
            pygame.draw.circle(surface, (130, 210, 100), (leaf_end_x, leaf_end_y), 2)
