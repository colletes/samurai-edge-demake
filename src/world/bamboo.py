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
        from src.isometric.voxel_renderer import draw_voxel_box

        # Y-sort usa a base do bambu
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

        # Sombra sutil no solo
        pygame.draw.ellipse(surface, (12, 22, 16), (base_sx - 8, base_sy - 4, 16, 8))

        if self.is_cut:
            # Toco cortado em voxel 3D
            draw_voxel_box(
                surface, camera,
                self.wx - 0.08, self.wy - 0.08, 0.0,
                0.16, 0.16, self.stump_height,
                COLOR_BAMBOO
            )
            # Tampa cortada diagonal em tom claro
            draw_voxel_box(
                surface, camera,
                self.wx - 0.07, self.wy - 0.07, self.stump_height,
                0.14, 0.14, 0.03,
                COLOR_BAMBOO_LIGHT
            )
            return

        # Bambu em pé: coluna vertical de voxels com anéis e nós volumétricos
        wind_sway = math.sin(time_val * 2.0 + self.wind_offset) * 0.08
        num_segs = 5
        seg_h = (self.total_height - 0.2) / num_segs

        for i in range(num_segs):
            frac = i / num_segs
            sway_x = wind_sway * frac
            sway_y = wind_sway * frac
            cur_z = i * seg_h

            # Segmento do colmo (coluna voxel)
            draw_voxel_box(
                surface, camera,
                self.wx - 0.08 + sway_x, self.wy - 0.08 + sway_y, cur_z,
                0.16, 0.16, seg_h,
                COLOR_BAMBOO
            )

            # Anel / nó entre os entrenós
            if i > 0:
                draw_voxel_box(
                    surface, camera,
                    self.wx - 0.10 + sway_x, self.wy - 0.10 + sway_y, cur_z,
                    0.20, 0.20, 0.04,
                    COLOR_BAMBOO_LIGHT
                )

        # Topo e folhagem em blocos voxels suspensos
        top_wx = self.wx + wind_sway
        top_wy = self.wy + wind_sway
        top_wz = self.total_height

        # Folhas em blocos voxel finos projetados
        draw_voxel_box(surface, camera, top_wx - 0.22, top_wy - 0.08, top_wz - 0.08, 0.26, 0.16, 0.05, COLOR_BAMBOO_LEAF)
        draw_voxel_box(surface, camera, top_wx + 0.04, top_wy - 0.20, top_wz - 0.02, 0.16, 0.24, 0.05, COLOR_BAMBOO_LEAF)
        draw_voxel_box(surface, camera, top_wx - 0.10, top_wy + 0.06, top_wz + 0.06, 0.22, 0.18, 0.05, (125, 205, 95))
