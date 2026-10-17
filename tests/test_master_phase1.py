"""Automated test suite for Master Roadmap Phase M-1:
- Static Terrain & Prop Surface Caching (`src/world/arena_cache.py`)
- Auto-Adaptive FPS Governor (`src/effects/quality.py`)
- Dynamic Gameplay Camera (`src/isometric/camera.py`)
- 3-Phase Finisher Camera (`src/effects/cinematic_director.py`)
"""

import math
import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1280, 720))

from src.world.arena_cache import PropSurfaceCache, get_terrain_cache, clear_arena_caches
from src.world.arenas import create_arena
from src.config import ARENA_BAMBOO
from src.entities.samurai import STATE_PARRY
from src.effects import quality
from src.isometric.camera import Camera
from src.effects.cinematic_director import CinematicDirector


class DummyFighter:
    def __init__(self, wx=5.0, wy=5.0):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.facing_x = 1.0
        self.facing_y = 0.0
        self.state = "IDLE"
        self.is_alive = True
        self.hp = 100


class TestMasterPhase1(unittest.TestCase):

    def setUp(self):
        clear_arena_caches()
        quality.set_effects_quality(quality.HIGH)
        quality.set_auto_adjust(True)
        quality.reset_fps_governor()

    def test_terrain_and_prop_surface_cache(self):
        surface = pygame.Surface((1280, 720))
        camera = Camera()
        camera.wx, camera.wy = 7.0, 7.0
        camera.azimuth = 0.0

        arena = create_arena(ARENA_BAMBOO)
        t_cache = get_terrain_cache()
        arena.render_terrain(surface, camera, 0.0)
        self.assertEqual(len(t_cache._cache), 1, "Terrain cache should be populated at azimuth == 0")
        self.assertEqual(t_cache.misses, 1)

        # Panning camera should reuse cached terrain surface without rebuilding
        camera.wx, camera.wy = 8.5, 6.2
        arena.render_terrain(surface, camera, 0.1)
        self.assertEqual(t_cache.hits, 1, "Terrain cache should register a hit on camera pan")

        # PropSurfaceCache test on rock and undisturbed bamboo from the arena
        prop_cache = PropSurfaceCache()
        rock = arena.rocks[0]
        bamboo = arena.bamboos[0]

        self.assertTrue(prop_cache.render_prop(surface, camera, "rock", rock))
        self.assertTrue(prop_cache.render_prop(surface, camera, "bamboo", bamboo))
        self.assertGreaterEqual(len(prop_cache._cache), 2)

        # When camera rotates (azimuth != 0), PropSurfaceCache should bypass and return False
        camera.azimuth = 0.35
        self.assertFalse(prop_cache.render_prop(surface, camera, "rock", rock))

        # When bamboo has active combat wind bend, PropSurfaceCache should bypass for live 3D physics
        camera.azimuth = 0.0
        bamboo.combat_bend_x = 0.25
        self.assertFalse(prop_cache.render_prop(surface, camera, "bamboo", bamboo))

    def test_auto_adaptive_fps_governor(self):
        quality.set_effects_quality(quality.HIGH)
        quality.set_auto_adjust(True)

        # Simulate 80 frames of low framerate (35 FPS -> dt = 1/35 ≈ 0.0286s)
        for _ in range(80):
            quality.update_fps_governor(1.0 / 35.0)
        self.assertEqual(quality.get_effects_quality(), quality.LOW, "Governor should step down after sustained < 48 FPS")
        self.assertTrue(quality.is_governor_stepped_down())

        # Simulate 250 frames of smooth 60 FPS (dt = 1/60s) to recover back to HIGH
        for _ in range(250):
            quality.update_fps_governor(1.0 / 60.0)
        self.assertEqual(quality.get_effects_quality(), quality.HIGH, "Governor should recover back toward user target after sustained >= 57 FPS")
        self.assertFalse(quality.is_governor_stepped_down())

    def test_dynamic_combat_camera_framing(self):
        cam = Camera()
        arena = create_arena(ARENA_BAMBOO)
        p1 = DummyFighter(6.0, 6.0)
        p2 = DummyFighter(7.2, 6.0)  # Close melee (< 3.0 tiles)

        for _ in range(60):
            cam.update_combat_framing(p1, p2, arena, 1.0 / 60.0)
        self.assertGreater(cam.zoom, 1.20, "Close melee should zoom in toward 1.28x")
        self.assertEqual(cam.azimuth, 0.0, "Gameplay camera must keep azimuth fixed at 0.0")

        # Long-range standoff (>= 9.0 tiles)
        p1.wx, p1.wy = 3.0, 3.0
        p2.wx, p2.wy = 11.0, 10.0
        for _ in range(90):
            cam.update_combat_framing(p1, p2, arena, 1.0 / 60.0)
        self.assertLess(cam.zoom, 0.95, "Long-range spacing should zoom out toward 0.88x")

        # Parry micro-zoom impulse
        p1.state = STATE_PARRY
        cam.update_combat_framing(p1, p2, arena, 1.0 / 60.0)
        self.assertGreater(cam.zoom_impulse, 0.04, "Parry state should trigger a micro-zoom impulse")

    def test_three_phase_finisher_camera(self):
        director = CinematicDirector()
        cam = Camera()
        p1 = DummyFighter(6.0, 6.0)
        p1.attack_duration = 0.25
        p1.set_facing = lambda tx, ty: None
        p2 = DummyFighter(6.9, 6.2)
        p2.set_facing = lambda tx, ty: None
        particles = []

        director.trigger_fatal_strike(p1, p2, "VERTICAL_BISECTION", (1.0, 0.2))
        self.assertTrue(director.is_frozen())

        # Step 1: IMPACT_FREEZE (first 0.18s) — Time is frozen, attacker coiled in windup
        director.update(0.05, None, particles)
        self.assertEqual(director.get_finisher_phase(), "IMPACT_FREEZE")
        director.apply_camera(cam, 0.05)
        self.assertAlmostEqual(p1.state_timer, 0.25 * 0.90, places=3,
                               msg="Attacker must be held in coiled windup while time is frozen")

        # Step 2: CAMERA_SWOOP (0.18s -> 0.60s) — Still frozen, camera zooms in & rolls to best angle
        for _ in range(10):
            director.update(0.05, None, particles)
            director.apply_camera(cam, 0.05)
            if director.camera_setup_timer <= 0.05:
                break
        self.assertEqual(director.get_finisher_phase(), "CAMERA_SWOOP")
        self.assertGreater(cam.zoom, 1.50, "Camera should zoom in close during frozen swoop")
        self.assertAlmostEqual(cam.azimuth, director.optimal_azimuth, delta=0.12,
                               msg="Camera should roll to optimal best angle before unfreezing")

        # Step 3 & 4: UNFREEZE -> EXECUTION — Time unfreezes and finisher strike happens from close angle
        director.update(0.10, None, particles)  # crosses setup threshold into EXECUTION
        self.assertEqual(director.get_finisher_phase(), "EXECUTION")
        self.assertEqual(director.camera_setup_timer, 0.0)
        director.update(0.30, None, particles)
        self.assertTrue(director.finisher_impact_played,
                        "Finisher strike impact must execute after time unfreezes at close-up angle")
        self.assertLess(p1.state_timer, 0.25 * 0.50,
                        "Attacker must swing through the finisher arc during close-up execution")


if __name__ == "__main__":
    unittest.main()
