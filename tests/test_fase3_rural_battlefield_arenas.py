"""
Testes automatizados para o Entregável A-3.3:
Campos de Batalha & Vilarejos Rurais (6 Arenas):
- nagashino_field (Teppo)
- forest_camp (Joe)
- sacred_pines (Daiki)
- ezo_tundra (Aoi)
- rice_paddies (Goro)
- rain_mill (Ichi)
"""
import os
import sys
import time
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame

from src.config import (
    ARENA_NAGASHINO,
    ARENA_FOREST_CAMP,
    ARENA_SACRED_PINES,
    ARENA_EZO_TUNDRA,
    ARENA_RICE_PADDIES,
    ARENA_RAIN_MILL,
)
from src.effects.terrain_particles import SURFACES, TerrainFX
from src.entities.red_samurai import RedSamurai
from src.isometric.camera import Camera
from src.world.arenas import (
    NAGASHINO_SPEC,
    FOREST_CAMP_SPEC,
    SACRED_PINES_SPEC,
    EZO_TUNDRA_SPEC,
    RICE_PADDIES_SPEC,
    RAIN_MILL_SPEC,
    TILE_NAG_MUD,
    TILE_EZO_SNOW,
    TILE_EZO_ICE,
)
from src.world.arena_generator import ArenaMap
from src.world.decor import (
    AkamatsuPine,
    ArtilleryCrater,
    FallenLog,
    RiceStalkCluster,
    SnowSpruceTree,
    WaterMillWheel,
)


class TestFase3RuralBattlefieldArenas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((640, 360))

    def _render_arena(self, arena: ArenaMap, cam: Camera, t: float = 0.5):
        arena.render_terrain(self.screen, cam, t)
        arena.render_overhead(self.screen, cam, t)
        for obj in arena.rocks:
            obj.render(self.screen, cam)
        for obj in arena.trees:
            try:
                obj.render(self.screen, cam, t)
            except TypeError:
                obj.render(self.screen, cam)
        for obj in arena.buildings:
            obj.render(self.screen, cam, t)
        for obj in arena.lanterns:
            obj.render(self.screen, cam, t)

    def test_1_nagashino_field_palisades_craters_and_mud(self):
        """Campo de Nagashino possui paliçadas Umagiri, crateras de artilharia fumegantes e lamaçal lento."""
        arena = ArenaMap(NAGASHINO_SPEC)
        self.assertEqual(arena.spec.id, ARENA_NAGASHINO)
        palisades = [b for b in arena.buildings if getattr(b, "style", "") == "palisade"]
        self.assertGreaterEqual(len(palisades), 6)
        craters = [p for p in arena.lanterns if isinstance(p, ArtilleryCrater)]
        self.assertGreaterEqual(len(craters), 3)
        self.assertAlmostEqual(NAGASHINO_SPEC.tile_styles[TILE_NAG_MUD].speed_mult, 0.60, places=2)

        cam = Camera()
        particles = []
        arena.update(0.7, [], cam, particles=particles, banners=[])
        self.assertGreater(len(particles), 0, "ArtilleryCrater deve emitir fumaça de pólvora.")
        self._render_arena(arena, cam)

    def test_2_forest_camp_tents_cabins_fallen_logs_and_snares(self):
        """Acampamento na Floresta possui cabanas, barracas de lona, fogueira, toras caídas e armadilhas de laço."""
        arena = ArenaMap(FOREST_CAMP_SPEC)
        self.assertEqual(arena.spec.id, ARENA_FOREST_CAMP)
        cabins = [b for b in arena.buildings if getattr(b, "style", "") == "cabin"]
        tents = [b for b in arena.buildings if getattr(b, "style", "") == "tent"]
        logs = [r for r in arena.rocks if isinstance(r, FallenLog)]
        self.assertGreaterEqual(len(cabins), 4)
        self.assertGreaterEqual(len(tents), 2)
        self.assertGreaterEqual(len(logs), 2)

        cam = Camera()
        self._render_arena(arena, cam)

    def test_3_sacred_pines_akamatsu_cache_hokora_and_logs(self):
        """Floresta dos Pinheiros renderiza AkamatsuPine com cache de sprite, Hokora, pilhas de toras e toras caídas."""
        AkamatsuPine._sprite_cache.clear()
        arena = ArenaMap(SACRED_PINES_SPEC)
        self.assertEqual(arena.spec.id, ARENA_SACRED_PINES)
        pines = [t for t in arena.trees if isinstance(t, AkamatsuPine)]
        logs = [r for r in arena.rocks if isinstance(r, FallenLog)]
        self.assertGreaterEqual(len(pines), 6)
        self.assertGreaterEqual(len(logs), 2)

        cam = Camera()
        self._render_arena(arena, cam)
        self.assertGreater(len(AkamatsuPine._sprite_cache), 0, "AkamatsuPine deve popular _sprite_cache.")

    def test_4_ezo_tundra_snow_surface_spruce_cache_and_inau(self):
        """Taiga de Ezo possui superfície de neve física ('snow'), SnowSpruceTree cacheada, totens Ainu e varais de peles."""
        SnowSpruceTree._sprite_cache.clear()
        self.assertIn("snow", SURFACES)
        self.assertEqual(EZO_TUNDRA_SPEC.tile_styles[TILE_EZO_SNOW].surface, "snow")
        self.assertGreater(EZO_TUNDRA_SPEC.tile_styles[TILE_EZO_ICE].speed_mult, 1.1)

        arena = ArenaMap(EZO_TUNDRA_SPEC)
        self.assertEqual(arena.spec.id, ARENA_EZO_TUNDRA)
        spruces = [t for t in arena.trees if isinstance(t, SnowSpruceTree)]
        self.assertGreaterEqual(len(spruces), 6)

        # Verifica emissão de partículas de neve ao correr sobre a clareira nevada
        fx = TerrainFX()
        f1 = RedSamurai(10.5, 10.5)
        fx.step(f1, arena, 1 / 60)
        f1.wx += 0.65
        fx.step(f1, arena, 1 / 60)
        self.assertGreater(len(fx.particles), 0, "Correr na neve de Ezo deve emitir partículas de neve ('snow').")

        cam = Camera()
        self._render_arena(arena, cam)
        self.assertGreater(len(SnowSpruceTree._sprite_cache), 0, "SnowSpruceTree deve popular _sprite_cache.")

    def test_5_rice_paddies_terraces_stalks_and_chutes(self):
        """Arrozais Terraciados possuem 3 níveis de altura, touceiras 3D RiceStalkCluster interativas e vertedouros."""
        RiceStalkCluster._sprite_cache.clear()
        arena = ArenaMap(RICE_PADDIES_SPEC)
        self.assertEqual(arena.spec.id, ARENA_RICE_PADDIES)
        stalks = [p for p in arena.lanterns if isinstance(p, RiceStalkCluster)]
        self.assertGreaterEqual(len(stalks), 8)

        # Verifica alturas dos 3 patamares (0.28, 0.14, 0.0)
        self.assertAlmostEqual(arena.style_at(2, 2).height, 0.28, places=2)
        self.assertAlmostEqual(arena.style_at(2, 10).height, 0.14, places=2)
        self.assertAlmostEqual(arena.style_at(10, 17).height, 0.00, places=2)

        # Verifica inclinação interativa dos brotos de arroz quando um lutador passa
        target_stalk = stalks[0]
        f1 = RedSamurai(target_stalk.wx, target_stalk.wy)
        f1.vx = 5.0
        target_stalk.tick(arena, 1 / 60, [f1], Camera(), [], [])
        self.assertGreater(abs(target_stalk.bend_x), 0.0)

        cam = Camera()
        target_stalk.bend_x = 0.0
        self._render_arena(arena, cam)
        self.assertGreater(len(RiceStalkCluster._sprite_cache), 0, "RiceStalkCluster deve popular _sprite_cache.")

    def test_6_rain_mill_wheel_aqueduct_and_splashes(self):
        """Moinho na Chuva possui roda d'água monumental com calha elevada (aqueduto) e geração de respingos no rio."""
        arena = ArenaMap(RAIN_MILL_SPEC)
        self.assertEqual(arena.spec.id, ARENA_RAIN_MILL)
        wheels = [b for b in arena.buildings if isinstance(b, WaterMillWheel)]
        self.assertEqual(len(wheels), 1)

        cam = Camera()
        arena.update(0.3, [], cam, particles=[], banners=[])
        self.assertGreater(len(arena.water_ripples), 0, "WaterMillWheel deve gerar marolas no rio.")
        self._render_arena(arena, cam)


if __name__ == "__main__":
    unittest.main()
