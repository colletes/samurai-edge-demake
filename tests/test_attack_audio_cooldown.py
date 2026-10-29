import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((320, 240))

from main import execute_fighter_attack, execute_fighter_secondary, execute_fighter_roll
from src.audio.sound_manager import SoundManager
from src.audio.sound_events import SoundEvent
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.raiden import RaidenSumo
from src.entities.rifleman import Rifleman
from src.entities.saitou_samurai import SaitouSamurai
from src.entities.ren_monk import RenMonk
from src.entities.samurai import STATE_IDLE, STATE_ATTACK


class TestAttackAudioCooldown(unittest.TestCase):
    def setUp(self):
        self.sound_mgr = SoundManager.get_instance()
        self.played_events = []
        # Hook into sound manager play
        self.orig_play = self.sound_mgr.play
        self.sound_mgr.play = lambda ev, **kwargs: self.played_events.append(ev)

    def tearDown(self):
        self.sound_mgr.play = self.orig_play

    def test_red_samurai_no_audio_on_mash_during_attack(self):
        p = RedSamurai(5.0, 5.0)
        projectiles = []
        particles = []

        # First attack while idle should succeed
        self.played_events.clear()
        res1 = execute_fighter_attack(p, 7.0, 5.0, projectiles, particles)
        self.assertTrue(res1)
        self.assertEqual(p.state, STATE_ATTACK)

        # Record count of sounds from first attack initiation
        initial_sound_count = len(self.played_events)

        # Mashing attack while in mid-animation (STATE_ATTACK)
        for _ in range(5):
            res_mash = execute_fighter_attack(p, 7.0, 5.0, projectiles, particles)
            self.assertFalse(res_mash)

        # No new sounds should have been triggered while mashing
        self.assertEqual(len(self.played_events), initial_sound_count)

    def test_blue_samurai_combo_and_no_audio_on_excess_mash(self):
        p = BlueSamurai(5.0, 5.0)
        projectiles = []
        particles = []

        self.played_events.clear()
        res1 = execute_fighter_attack(p, 7.0, 5.0, projectiles, particles)
        self.assertTrue(res1)
        self.assertEqual(p.state, STATE_ATTACK)

        # Buffer a single combo step
        res2 = execute_fighter_attack(p, 7.0, 5.0, projectiles, particles)
        self.assertFalse(res2)  # Buffered into next strike, not immediate execution

        count_after_buffer = len(self.played_events)
        # Mashing further while already buffered
        for _ in range(5):
            res_mash = execute_fighter_attack(p, 7.0, 5.0, projectiles, particles)
            self.assertFalse(res_mash)

        self.assertEqual(len(self.played_events), count_after_buffer)

    def test_raiden_no_audio_on_mash_during_strike(self):
        p = RaidenSumo(5.0, 5.0)
        projectiles = []
        particles = []

        self.played_events.clear()
        res1 = execute_fighter_attack(p, 7.0, 5.0, projectiles, particles)
        self.assertTrue(res1)
        self.assertEqual(p.state, "TSUPPARI_STRIKE_1")
        self.assertIn(SoundEvent.SWING_BLUNT, self.played_events)

        count_after_first = len(self.played_events)

        # Mashing while Raiden is executing TSUPPARI_STRIKE_1
        for _ in range(5):
            res_mash = execute_fighter_attack(p, 7.0, 5.0, projectiles, particles)
            self.assertFalse(res_mash)

        # No sounds should play while mid-animation
        self.assertEqual(len(self.played_events), count_after_first)

    def test_saitou_no_audio_on_mash_during_gatotsu(self):
        p = SaitouSamurai(5.0, 5.0)
        projectiles = []
        particles = []

        self.played_events.clear()
        res1 = execute_fighter_attack(p, 7.0, 5.0, projectiles, particles)
        self.assertTrue(res1)
        self.assertIn(SoundEvent.SLASH_KATANA, self.played_events)

        count_after_first = len(self.played_events)

        # Mashing while charging Gatotsu
        for _ in range(5):
            res_mash = execute_fighter_attack(p, 7.0, 5.0, projectiles, particles)
            self.assertFalse(res_mash)

        self.assertEqual(len(self.played_events), count_after_first)

    def test_roll_no_audio_on_mash_during_roll_or_attack(self):
        p = RaidenSumo(5.0, 5.0)
        particles = []

        self.played_events.clear()
        # Roll while idle should succeed
        res_roll1 = execute_fighter_roll(p, 1.0, 0.0, 7.0, 5.0, particles)
        self.assertTrue(res_roll1)
        self.assertIn(SoundEvent.DASH_ROLL, self.played_events)

        count_after_first_roll = len(self.played_events)

        # Mashing roll while rolling
        for _ in range(5):
            res_mash = execute_fighter_roll(p, 1.0, 0.0, 7.0, 5.0, particles)
            self.assertFalse(res_mash)

        self.assertEqual(len(self.played_events), count_after_first_roll)

    def test_secondary_no_audio_on_mash_during_cooldown(self):
        p = RaidenSumo(5.0, 5.0)
        particles = []
        projectiles = []
        banners = []

        self.played_events.clear()
        res_sec1 = execute_fighter_secondary(p, 7.0, 5.0, 1.0, 0.0, projectiles, particles, [], [], [], banners=banners)
        self.assertTrue(res_sec1)
        self.assertIn(SoundEvent.DASH_ROLL, self.played_events)

        count_after_first_sec = len(self.played_events)

        # Mashing secondary while in tackle
        for _ in range(5):
            res_mash = execute_fighter_secondary(p, 7.0, 5.0, 1.0, 0.0, projectiles, particles, [], [], [], banners=banners)
            self.assertFalse(res_mash)

        self.assertEqual(len(self.played_events), count_after_first_sec)


if __name__ == "__main__":
    unittest.main()
