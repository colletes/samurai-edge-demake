"""
Testes automatizados para a Fase 3 (Entregável A-3.2):
Revamp Visual e Atmosférico Geral das Arenas — Cenários Urbanos & Históricos (6 Arenas):
1. `kyoto` (Murasaki)
2. `yoshiwara_alley` (O-Rin)
3. `kabuki_stage` (Okuni)
4. `baroque_court` (Julie)
5. `dejima_warehouse` (Hendrika)
6. `sacred_dohyo` (Raiden)
"""
import inspect
import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
from src.config import (
    ARENA_KYOTO,
    ARENA_YOSHIWARA,
    ARENA_KABUKI_STAGE,
    ARENA_BAROQUE_COURT,
    ARENA_DEJIMA,
    ARENA_DOHYO,
)
from src.isometric.camera import Camera
from src.world.arenas import create_arena, ARENA_SPECS
from src.world.arena_cache import clear_arena_caches, get_prop_cache
from src.world.decor import (
    SupplyCrate,
    ScreenPanel,
    StripedCurtain,
    MarbleStatue,
    Fountain,
    DohyoCornerPost,
    SacredSaltMound,
    KabukiFootlight,
    DutchCargoCrane,
)
from src.world.hazards import RotatingStage, DohyoHazard, DejimaHazard


URBAN_ARENAS = (
    ARENA_KYOTO,
    ARENA_YOSHIWARA,
    ARENA_KABUKI_STAGE,
    ARENA_BAROQUE_COURT,
    ARENA_DEJIMA,
    ARENA_DOHYO,
)


class _DummyFighter:
    def __init__(self, wx: float, wy: float, state: str = "ATTACK", hitbox_active: bool = True):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.vx = 1.8
        self.vy = 0.5
        self.is_alive = True
        self.is_moving = True
        self.facing_x = 1.0
        self.facing_y = 0.0
        self.state = state
        self.hitbox_active = hitbox_active
        self.hitbox_center = (wx, wy)
        self.hitbox_radius = 1.1

    def apply_forced_displacement(self, dx: float, dy: float, arena):
        self.wx += dx
        self.wy += dy


class TestFase3UrbanArenas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((640, 360))

    def test_01_all_six_urban_arenas_build_and_render(self):
        """Valida construção, cache, atualização e renderização das 6 arenas urbanas e históricas."""
        clear_arena_caches()
        cam = Camera(640, 360)
        prop_cache = get_prop_cache()

        for arena_id in URBAN_ARENAS:
            with self.subTest(arena_id=arena_id):
                self.assertIn(arena_id, ARENA_SPECS)
                arena = create_arena(arena_id)
                s1, s2 = arena.pick_spawns()
                self.assertNotEqual(s1, s2)

                f1 = _DummyFighter(s1[0], s1[1])
                f2 = _DummyFighter(s2[0], s2[1])
                particles = []
                banners = []

                arena.update(0.25, [f1, f2], cam, particles, banners)
                arena.render_terrain(self.screen, cam, 1.25)
                arena.render_overhead(self.screen, cam, 1.25)

                for obj in arena.rocks:
                    if not prop_cache.render_prop(self.screen, cam, "rock", obj, 1.25):
                        obj.render(self.screen, cam)
                for obj in arena.buildings:
                    obj.render(self.screen, cam, 1.25)
                for obj in arena.lanterns:
                    obj.render(self.screen, cam, 1.25)

    def test_02_destructible_urban_props_protocol(self):
        """Verifica que SupplyCrate, ScreenPanel e SacredSaltMound quebram com break_panel e desativam colisão."""
        cam = Camera(640, 360)
        for prop in (SupplyCrate(10.0, 10.0), ScreenPanel(10.0, 10.0, "x"), SacredSaltMound(10.0, 10.0)):
            self.assertFalse(prop.is_broken)
            self.assertGreater(prop.radius, 0.0)
            self.assertTrue(prop.check_collision(10.0, 10.0, 0.3)[0])
            prop.render(self.screen, cam)

            particles = []
            prop.break_panel((1.0, 0.0), particles)
            self.assertTrue(prop.is_broken)
            self.assertEqual(prop.radius, 0.0)
            self.assertFalse(prop.check_collision(10.0, 10.0, 0.3)[0])
            self.assertGreater(len(prop.splinters), 0)
            self.assertGreater(len(particles), 0)
            prop.render(self.screen, cam)

    def test_03_reactive_striped_curtain_tearing(self):
        """Verifica que StripedCurtain rasga faixas e aumenta oscilação quando atingida por golpes."""
        cam = Camera(640, 360)
        curtain = StripedCurtain(3.0, 0.8, length=8.0, axis="x")
        self.assertEqual(len(curtain.torn_strips), 0)
        curtain.render(self.screen, cam, 0.5)

        fighter = _DummyFighter(5.0, 0.8, state="ATTACK", hitbox_active=True)
        particles = []
        curtain.tick(None, 0.016, [fighter], cam, particles, [])
        self.assertGreater(len(curtain.torn_strips), 0)
        self.assertGreater(curtain.sway_boost, 0.0)
        curtain.render(self.screen, cam, 1.0)

    def test_04_baroque_fountain_ripples_and_zero_2d_circles(self):
        """Verifica que Fountain emite ondas/respingos na bacia e não usa pygame.draw.circle."""
        cam = Camera(640, 360)
        arena = create_arena(ARENA_BAROQUE_COURT)
        fountains = [r for r in arena.rocks if isinstance(r, Fountain)]
        self.assertEqual(len(fountains), 1)
        fountain = fountains[0]

        for _ in range(3):
            fountain.tick(arena, 0.15, [], cam, [], [])
        self.assertGreater(len(arena.water_ripples), 0)

        for cls in (Fountain, MarbleStatue, DohyoHazard, DejimaHazard):
            src = inspect.getsource(cls)
            self.assertNotIn("draw.circle", src, f"{cls.__name__} não deve usar pygame.draw.circle")

    def test_05_new_kabuki_and_dejima_props_registered(self):
        """Verifica presença de KabukiFootlight em kabuki_stage e DutchCargoCrane em dejima_warehouse."""
        kabuki = create_arena(ARENA_KABUKI_STAGE)
        footlights = [p for p in kabuki.lanterns if isinstance(p, KabukiFootlight)]
        self.assertGreaterEqual(len(footlights), 6)

        dejima = create_arena(ARENA_DEJIMA)
        cranes = [b for b in dejima.buildings if isinstance(b, DutchCargoCrane)]
        self.assertGreaterEqual(len(cranes), 2)

        dohyo = create_arena(ARENA_DOHYO)
        posts = [p for p in dohyo.lanterns if isinstance(p, DohyoCornerPost)]
        mounds = [r for r in dohyo.rocks if isinstance(r, SacredSaltMound)]
        self.assertEqual(len(posts), 4)
        self.assertEqual(len(mounds), 2)


if __name__ == "__main__":
    unittest.main()
