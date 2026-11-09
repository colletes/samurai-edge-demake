"""
Testes automatizados para o Entregável A-3.4:
Locais Extremos & Noturnos (6 Arenas):
- shadow_cave (Murasaki)
- iga_rooftops (Hanzo)
- pirate_deck (Anne)
- ganryu_island (Musashi)
- gojo_bridge (Benkei)
- gothic_cemetery (Valerius)
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
    ARENA_SHADOW_CAVE,
    ARENA_IGA,
    ARENA_PIRATE_DECK,
    ARENA_GANRYU,
    ARENA_GOJO_BRIDGE,
    ARENA_GOTHIC_CEMETERY,
)
from src.isometric.camera import Camera
from src.world.arenas import (
    SHADOW_CAVE_SPEC,
    IGA_SPEC,
    PIRATE_SPEC,
    GANRYU_SPEC,
    GOJO_BRIDGE_SPEC,
    GOTHIC_CEMETERY_SPEC,
)
from src.world.arena_generator import ArenaMap
from src.world.decor import (
    BladeCluster,
    BridgeSupport,
    CannonballPyramid,
    CaveStalagmite,
    GojoRailing,
    GraveyardGargoyle,
    HangingChain,
    OnigawaraTile,
    OpenGrave,
    RoofChimney,
    ShipRigging,
    ShoreDriftwood,
    ShurikenEmbedded,
    StalactiteCluster,
)


class TestFase3ExtremeArenas(unittest.TestCase):
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

    def test_1_shadow_cave_stalactites_stalagmites_and_chains(self):
        """Gruta das Sombras possui estalactites com gotejamento, estalagmites facetadas e correntes balançando."""
        arena = ArenaMap(SHADOW_CAVE_SPEC)
        self.assertEqual(arena.spec.id, ARENA_SHADOW_CAVE)
        stalactites = [p for p in arena.lanterns if isinstance(p, StalactiteCluster)]
        self.assertGreaterEqual(len(stalactites), 6)
        stalagmites = [r for r in arena.rocks if isinstance(r, CaveStalagmite)]
        self.assertGreaterEqual(len(stalagmites), 6)
        chains = [p for p in arena.lanterns if isinstance(p, HangingChain)]
        self.assertGreaterEqual(len(chains), 6)

        cam = Camera()
        arena.update(0.5, [], cam, particles=[], banners=[])
        self._render_arena(arena, cam)

    def test_2_iga_rooftops_chimneys_onigawara_and_shurikens(self):
        """Telhados de Iga possui chaminés fumegantes, telhas onigawara e shurikens cravados."""
        arena = ArenaMap(IGA_SPEC)
        self.assertEqual(arena.spec.id, ARENA_IGA)
        chimneys = [r for r in arena.rocks if isinstance(r, RoofChimney)]
        self.assertGreaterEqual(len(chimneys), 3)
        onigawara = [r for r in arena.rocks if isinstance(r, OnigawaraTile)]
        self.assertGreaterEqual(len(onigawara), 4)
        shurikens = [p for p in arena.lanterns if isinstance(p, ShurikenEmbedded)]
        self.assertGreaterEqual(len(shurikens), 3)

        cam = Camera()
        particles = []
        arena.update(0.8, [], cam, particles=particles, banners=[])
        self.assertGreater(len(particles), 0, "RoofChimney deve emitir fumaça noturna.")
        self._render_arena(arena, cam)

    def test_3_pirate_deck_masts_cannonballs_and_rigging(self):
        """Convés Pirata possui mastros detalhados com gávea, pirâmides de balas de canhão e enxárcias esticadas."""
        arena = ArenaMap(PIRATE_SPEC)
        self.assertEqual(arena.spec.id, ARENA_PIRATE_DECK)
        masts = [b for b in arena.buildings if getattr(b, "style", "") == "mast"]
        self.assertGreaterEqual(len(masts), 2)
        cannonballs = [r for r in arena.rocks if isinstance(r, CannonballPyramid)]
        self.assertGreaterEqual(len(cannonballs), 2)
        riggings = [p for p in arena.lanterns if isinstance(p, ShipRigging)]
        self.assertGreaterEqual(len(riggings), 4)

        cam = Camera()
        arena.update(0.5, [], cam, particles=[], banners=[])
        self._render_arena(arena, cam)

    def test_4_ganryu_island_boat_ribs_driftwood_and_oar(self):
        """Ilha de Ganryu possui barco quebrado com o remo de Musashi e troncos de cedro náufrago na areia."""
        arena = ArenaMap(GANRYU_SPEC)
        self.assertEqual(arena.spec.id, ARENA_GANRYU)
        boats = [b for b in arena.buildings if getattr(b, "style", "") == "boat"]
        self.assertGreaterEqual(len(boats), 1)
        driftwood = [r for r in arena.rocks if isinstance(r, ShoreDriftwood)]
        self.assertGreaterEqual(len(driftwood), 3)

        cam = Camera()
        arena.update(0.5, [], cam, particles=[], banners=[])
        self._render_arena(arena, cam)

    def test_5_gojo_bridge_blades_supports_and_railings(self):
        """Ponte Gojo possui feixes de lâminas de Benkei, balustradas e pilares estruturais com espuma de rio."""
        arena = ArenaMap(GOJO_BRIDGE_SPEC)
        self.assertEqual(arena.spec.id, ARENA_GOJO_BRIDGE)
        blades = [r for r in arena.rocks if isinstance(r, BladeCluster)]
        self.assertGreaterEqual(len(blades), 10)
        supports = [p for p in arena.lanterns if isinstance(p, BridgeSupport)]
        self.assertGreaterEqual(len(supports), 6)
        railings = [b for b in arena.buildings if isinstance(b, GojoRailing)]
        self.assertGreaterEqual(len(railings), 6)

        cam = Camera()
        arena.update(0.5, [], cam, particles=[], banners=[])
        self._render_arena(arena, cam)

    def test_6_gothic_cemetery_open_graves_gargoyles_and_crypt(self):
        """Cemitério Gótico possui sepulturas abertas com névoa, gárgulas nos muros e cripta de pedra."""
        arena = ArenaMap(GOTHIC_CEMETERY_SPEC)
        self.assertEqual(arena.spec.id, ARENA_GOTHIC_CEMETERY)
        graves = [r for r in arena.rocks if isinstance(r, OpenGrave)]
        self.assertGreaterEqual(len(graves), 2)
        gargoyles = [r for r in arena.rocks if isinstance(r, GraveyardGargoyle)]
        self.assertGreaterEqual(len(gargoyles), 2)

        cam = Camera()
        arena.update(0.5, [], cam, particles=[], banners=[])
        self._render_arena(arena, cam)

    def test_7_rendering_performance_all_extreme_arenas(self):
        """As 6 arenas extremas e noturnas devem renderizar com alta taxa de quadros (sub-16ms por quadro)."""
        specs = [
            SHADOW_CAVE_SPEC,
            IGA_SPEC,
            PIRATE_SPEC,
            GANRYU_SPEC,
            GOJO_BRIDGE_SPEC,
            GOTHIC_CEMETERY_SPEC,
        ]
        cam = Camera()
        for spec in specs:
            arena = ArenaMap(spec)
            # Warm-up
            self._render_arena(arena, cam, 0.0)

            t0 = time.perf_counter()
            frames = 20
            for i in range(frames):
                self._render_arena(arena, cam, i * 0.016)
            elapsed = time.perf_counter() - t0
            ms_per_frame = (elapsed / frames) * 1000.0
            self.assertLess(
                ms_per_frame,
                16.0,
                f"Arena {spec.id} demorou {ms_per_frame:.2f}ms/frame (limite 16ms para 60 FPS)",
            )


if __name__ == "__main__":
    unittest.main()
