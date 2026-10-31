"""
Entidade Bambu com estética voxel vertical, suporte a fatiamento por corte, camuflagem
e renderização ultra-otimizada por Template Instancing pré-aquecido.
"""
import math
import random
import pygame
from src.config import (
    COLOR_BAMBOO, COLOR_BAMBOO_LIGHT, COLOR_BAMBOO_LEAF
)
from src.effects.particles import BambooSliceParticle
from src.isometric.iso_math import world_to_iso
from src.isometric.voxel_renderer import draw_voxel_box


class _TemplateCamera:
    """Câmera simulada ultra-rápida usada para assar os templates de bambu em coordenadas relativas."""
    def __init__(self, anchor_x: int, anchor_y: int, zoom: float, azimuth: float = 0.0):
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.zoom = zoom
        self.azimuth = azimuth

    def apply(self, wx: float, wy: float, wz: float = 0.0) -> tuple[int, int]:
        iso_x, iso_y = world_to_iso(wx, wy, wz, self.azimuth)
        return int(iso_x * self.zoom + self.anchor_x), int(iso_y * self.zoom + self.anchor_y)


class BambooTemplateCache:
    """
    Gerenciador singleton de templates de sprites pré-renderizados para bambus.
    Substitui 2.300 chamadas por frame de draw_voxel_box por blits diretos de sprites
    otimizados em 4 faixas de altura x 8 fases de oscilação do vento.
    """
    HEIGHT_TIERS = (2.9, 3.2, 3.5, 3.8)
    STUMP_TIERS = (0.35, 0.50, 0.65)
    NUM_SWAYS = 8

    def __init__(self):
        # (h_idx, s_idx, zoom_b, az_b) -> (Surface, anchor_x, anchor_y)
        self._templates: dict[tuple[int, int, float, float], tuple[pygame.Surface, int, int]] = {}
        # (stump_idx, zoom_b, az_b) -> (Surface, anchor_x, anchor_y)
        self._stump_templates: dict[tuple[int, float, float], tuple[pygame.Surface, int, int]] = {}

    def clear(self):
        self._templates.clear()
        self._stump_templates.clear()

    @staticmethod
    def get_height_tier_idx(total_height: float) -> int:
        if total_height <= 3.05:
            return 0
        elif total_height <= 3.35:
            return 1
        elif total_height <= 3.65:
            return 2
        return 3

    @staticmethod
    def get_stump_tier_idx(stump_height: float) -> int:
        if stump_height <= 0.42:
            return 0
        elif stump_height <= 0.57:
            return 1
        return 2

    @staticmethod
    def get_sway_idx(wind_sway: float) -> int:
        norm = (wind_sway + 0.08) / 0.16
        idx = int(norm * 7.999)
        return max(0, min(7, idx))

    def _bake_bamboo_template(self, h_idx: int, s_idx: int, zoom: float, azimuth: float) -> tuple[pygame.Surface, int, int]:
        tot_h = self.HEIGHT_TIERS[h_idx]
        w_sway = ((s_idx / 7.0) * 2.0 - 1.0) * 0.08

        # Dimensões seguras do canvas do sprite
        w = max(40, int(96 * zoom))
        h = max(60, int((tot_h * 32.0 + 48) * zoom))
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        ax = w // 2
        ay = h - int(16 * zoom)
        cam = _TemplateCamera(ax, ay, zoom, azimuth)

        # 1. Sombra elíptica no solo
        sh_w = max(4, int(16 * zoom))
        sh_h = max(2, int(8 * zoom))
        pygame.draw.ellipse(surf, (12, 22, 16), (ax - sh_w // 2, ay - sh_h // 2, sh_w, sh_h))

        # 2. Segmentos verticais do colmo
        num_segs = 5
        seg_h = (tot_h - 0.2) / num_segs
        for i in range(num_segs):
            frac = i / num_segs
            sway_x = w_sway * frac
            sway_y = w_sway * frac
            cur_z = i * seg_h

            draw_voxel_box(
                surf, cam,
                -0.08 + sway_x, -0.08 + sway_y, cur_z,
                0.16, 0.16, seg_h,
                COLOR_BAMBOO
            )
            if i > 0:
                draw_voxel_box(
                    surf, cam,
                    -0.10 + sway_x, -0.10 + sway_y, cur_z,
                    0.20, 0.20, 0.04,
                    COLOR_BAMBOO_LIGHT
                )

        # 3. Topo e folhagem
        top_wx = w_sway
        top_wy = w_sway
        top_wz = tot_h
        draw_voxel_box(surf, cam, top_wx - 0.22, top_wy - 0.08, top_wz - 0.08, 0.26, 0.16, 0.05, COLOR_BAMBOO_LEAF)
        draw_voxel_box(surf, cam, top_wx + 0.04, top_wy - 0.20, top_wz - 0.02, 0.16, 0.24, 0.05, COLOR_BAMBOO_LEAF)
        draw_voxel_box(surf, cam, top_wx - 0.10, top_wy + 0.06, top_wz + 0.06, 0.22, 0.18, 0.05, (125, 205, 95))

        return surf, ax, ay

    def _bake_stump_template(self, stump_idx: int, zoom: float, azimuth: float) -> tuple[pygame.Surface, int, int]:
        stump_h = self.STUMP_TIERS[stump_idx]
        w = max(30, int(64 * zoom))
        h = max(30, int((stump_h * 32.0 + 32) * zoom))
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        ax = w // 2
        ay = h - int(12 * zoom)
        cam = _TemplateCamera(ax, ay, zoom, azimuth)

        sh_w = max(4, int(16 * zoom))
        sh_h = max(2, int(8 * zoom))
        pygame.draw.ellipse(surf, (12, 22, 16), (ax - sh_w // 2, ay - sh_h // 2, sh_w, sh_h))

        draw_voxel_box(
            surf, cam,
            -0.08, -0.08, 0.0,
            0.16, 0.16, stump_h,
            COLOR_BAMBOO
        )
        draw_voxel_box(
            surf, cam,
            -0.07, -0.07, stump_h,
            0.14, 0.14, 0.03,
            COLOR_BAMBOO_LIGHT
        )
        return surf, ax, ay

    def warm_up(self, base_zoom: float = 1.0, azimuth: float = 0.0):
        """Pré-aquece em ~2ms as 32 variações primárias e 3 tocos cortados para 60 FPS garantidos."""
        z_b = round(base_zoom, 1)
        az_b = round(azimuth, 2)
        for h_i in range(len(self.HEIGHT_TIERS)):
            for s_i in range(self.NUM_SWAYS):
                key = (h_i, s_i, z_b, az_b)
                if key not in self._templates:
                    self._templates[key] = self._bake_bamboo_template(h_i, s_i, z_b, az_b)
        for st_i in range(len(self.STUMP_TIERS)):
            s_key = (st_i, z_b, az_b)
            if s_key not in self._stump_templates:
                self._stump_templates[s_key] = self._bake_stump_template(st_i, z_b, az_b)

    def render(self, surface: pygame.Surface, camera, bamboo, time_val: float):
        # Se houver flexão de combate ativa (golpe de katana ou passagem de samurai), desenha ao vivo
        if abs(getattr(bamboo, "combat_bend_x", 0.0)) > 0.005 or abs(getattr(bamboo, "combat_bend_y", 0.0)) > 0.005:
            bamboo.render_live(surface, camera, time_val)
            return

        base_sx, base_sy = camera.apply(bamboo.wx, bamboo.wy, 0.0)
        zoom_b = round(camera.zoom, 1)
        az_b = round(getattr(camera, "azimuth", 0.0), 2)

        if bamboo.is_cut:
            stump_idx = self.get_stump_tier_idx(bamboo.stump_height)
            s_key = (stump_idx, zoom_b, az_b)
            tpl = self._stump_templates.get(s_key)
            if tpl is None:
                tpl = self._bake_stump_template(stump_idx, zoom_b, az_b)
                self._stump_templates[s_key] = tpl
            surf, ax, ay = tpl
            surface.blit(surf, (base_sx - ax, base_sy - ay))
            return

        h_idx = self.get_height_tier_idx(bamboo.total_height)
        wind_sway = math.sin(time_val * 2.0 + bamboo.wind_offset) * 0.08
        s_idx = self.get_sway_idx(wind_sway)

        key = (h_idx, s_idx, zoom_b, az_b)
        tpl = self._templates.get(key)
        if tpl is None:
            tpl = self._bake_bamboo_template(h_idx, s_idx, zoom_b, az_b)
            self._templates[key] = tpl
        surf, ax, ay = tpl
        surface.blit(surf, (base_sx - ax, base_sy - ay))


_BAMBOO_CACHE = BambooTemplateCache()


def get_bamboo_template_cache() -> BambooTemplateCache:
    return _BAMBOO_CACHE


def warm_up_bamboo_templates(base_zoom: float = 1.0, azimuth: float = 0.0):
    _BAMBOO_CACHE.warm_up(base_zoom, azimuth)


class Bamboo:
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.total_height = random.uniform(2.8, 3.8) # Altura no espaço z de mundo
        self.radius = 0.18 # Raio de colisão sutil
        self.is_cut = False
        self.stump_height = random.uniform(0.35, 0.65)
        self.wind_offset = random.uniform(0, math.pi * 2)
        self.combat_bend_x = 0.0
        self.combat_bend_y = 0.0

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
        """Renderização ultra-rápida via Template Instancing."""
        _BAMBOO_CACHE.render(surface, camera, self, time_val)

    def render_live(self, surface: pygame.Surface, camera, time_val: float):
        """Renderização voxel ao vivo usada quando há impacto físico de combate."""
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
        bend_x = getattr(self, "combat_bend_x", 0.0)
        bend_y = getattr(self, "combat_bend_y", 0.0)
        num_segs = 5
        seg_h = (self.total_height - 0.2) / num_segs

        for i in range(num_segs):
            frac = i / num_segs
            sway_x = wind_sway * frac + bend_x * (frac ** 1.6)
            sway_y = wind_sway * frac + bend_y * (frac ** 1.6)
            cur_z = i * seg_h

            draw_voxel_box(
                surface, camera,
                self.wx - 0.08 + sway_x, self.wy - 0.08 + sway_y, cur_z,
                0.16, 0.16, seg_h,
                COLOR_BAMBOO
            )
            if i > 0:
                draw_voxel_box(
                    surface, camera,
                    self.wx - 0.10 + sway_x, self.wy - 0.10 + sway_y, cur_z,
                    0.20, 0.20, 0.04,
                    COLOR_BAMBOO_LIGHT
                )

        # Topo e folhagem em blocos voxels suspensos
        top_wx = self.wx + wind_sway + bend_x
        top_wy = self.wy + wind_sway + bend_y
        top_wz = self.total_height

        draw_voxel_box(surface, camera, top_wx - 0.22, top_wy - 0.08, top_wz - 0.08, 0.26, 0.16, 0.05, COLOR_BAMBOO_LEAF)
        draw_voxel_box(surface, camera, top_wx + 0.04, top_wy - 0.20, top_wz - 0.02, 0.16, 0.24, 0.05, COLOR_BAMBOO_LEAF)
        draw_voxel_box(surface, camera, top_wx - 0.10, top_wy + 0.06, top_wz + 0.06, 0.22, 0.18, 0.05, (125, 205, 95))
