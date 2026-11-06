"""
Test Suite: Anne & Julie Complete Overhaul Verification (Sub-phases 2.11 & 2.12)
Validates materials, get_arms kinematics, movesets, projectile mechanics,
fatalities, 100% continuous intro/victory scripts, corpse physics, and inspector synchronization.
"""
import os
import sys
import math
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()


class TestAnneAndJulieOverhaul(unittest.TestCase):

    def test_anne_materials_and_get_arms(self):
        from src.entities import anne_model
        self.assertTrue(hasattr(anne_model, "MATERIALS"), "anne_model must define MATERIALS")
        self.assertTrue(hasattr(anne_model, "LEGACY_MATERIALS"), "anne_model must define LEGACY_MATERIALS")
        for k, v in anne_model.LEGACY_MATERIALS.items():
            self.assertEqual(v, "matte", f"Legacy material for {k} must be matte")

        self.assertTrue(hasattr(anne_model, "get_arms"), "anne_model must export get_arms")
        class DummyContext:
            torso_z = 0.40
            base_x = 0.0
            base_y = 0.0
            fx = 1.0
            fy = 0.0
            px = 0.0
            py = 1.0
            state = "IDLE"
            extra_props = {}
            atk_progress = 0.0

        c = DummyContext()
        left, right = anne_model.get_arms(c)
        self.assertEqual(len(left), 3)
        self.assertEqual(len(right), 3)
        self.assertTrue(all(isinstance(v, (int, float)) for v in left + right))

    def test_julie_materials_and_get_arms(self):
        from src.entities import julie_model
        self.assertTrue(hasattr(julie_model, "MATERIALS"), "julie_model must define MATERIALS")
        self.assertTrue(hasattr(julie_model, "LEGACY_MATERIALS"), "julie_model must define LEGACY_MATERIALS")
        for k, v in julie_model.LEGACY_MATERIALS.items():
            self.assertEqual(v, "matte", f"Legacy material for {k} must be matte")

        self.assertTrue(hasattr(julie_model, "get_arms"), "julie_model must export get_arms")
        class DummyContext:
            torso_z = 0.40
            base_x = 0.0
            base_y = 0.0
            fx = 1.0
            fy = 0.0
            px = 0.0
            py = 1.0
            state = "IDLE"
            extra_props = {}
            atk_progress = 0.0

        c = DummyContext()
        left, right = julie_model.get_arms(c)
        self.assertEqual(len(left), 3)
        self.assertEqual(len(right), 3)
        self.assertTrue(all(isinstance(v, (int, float)) for v in left + right))

    def test_anne_cutlass_cleave(self):
        from src.entities.pirate import PirateSwordswoman
        anne = PirateSwordswoman(5.0, 5.0)
        self.assertGreaterEqual(anne.speed, 4.8, "Anne speed should be agile (4.9)")

        initial_x = anne.wx
        res = anne.trigger_cutlass_cleave(7.0, 5.0)
        self.assertTrue(res)
        self.assertEqual(anne.state, "ATTACK")
        self.assertEqual(anne.hitbox_radius, 1.65, "Cutlass Cleave hitbox radius must be 1.65m")
        self.assertGreater(anne.wx, initial_x + 0.60, "Cutlass Cleave must provide a 0.65m forward lunge")

    def test_anne_cannon_strike(self):
        from src.entities.pirate import PirateSwordswoman
        anne = PirateSwordswoman(5.0, 5.0)
        anne.on_round_start()
        self.assertEqual(anne.cannon_cooldown_timer, 4.5, "Cannon starts on 4.5s cooldown at round start")

        # Reset cooldown for testing
        anne.cannon_cooldown_timer = 0.0
        res = anne.start_cannon_strike(8.0, 8.0)
        self.assertTrue(res)
        self.assertTrue(anne.is_aiming_cannon)

        projectiles = []
        particles = []
        anne.cannon_cooldown_timer = 0.0
        anne.trigger_quick_cannon(9.0, 9.0, projectiles, particles)
        self.assertEqual(len(projectiles), 1)
        self.assertEqual(anne.cannon_cooldown_timer, 4.5)
        self.assertEqual(projectiles[0].target_wx, 9.0)
        self.assertEqual(projectiles[0].target_wy, 9.0)

    def test_anne_swashbuckle_dash(self):
        from src.entities.pirate import PirateSwordswoman
        anne = PirateSwordswoman(5.0, 5.0)
        res = anne.trigger_roll(1.0, 0.0)
        self.assertTrue(res)
        self.assertEqual(anne.state, "ROLL")
        self.assertTrue(anne.is_invulnerable_dodge)

    def test_anne_fatalities_mapping(self):
        from src.combat.collision import _get_death_style_for_attacker
        class DummyFighter:
            char_type = "pirate"
            state = "ATTACK"
        atk = DummyFighter()

        style_cutlass = _get_death_style_for_attacker(atk, "cutlass")
        self.assertEqual(style_cutlass, "ARANAMI_CLEAVE")

        style_cannon = _get_death_style_for_attacker(atk, "cannon")
        self.assertEqual(style_cannon, "KANPOU_SENMETSU")

    def test_julie_fleche_thrust(self):
        from src.entities.musketeer import Musketeer
        julie = Musketeer(5.0, 5.0)
        res = julie.trigger_fleche_thrust(7.0, 5.0)
        self.assertTrue(res)
        self.assertEqual(julie.state, "ATTACK")
        self.assertEqual(julie.hitbox_radius, 0.70, "Fleche thrust hitbox radius must be 0.70m")
        self.assertAlmostEqual(julie.hitbox_center[0], julie.wx + 1.30, places=2)

    def test_julie_secondary_and_cape_flip(self):
        from src.entities.musketeer import Musketeer
        julie = Musketeer(5.0, 5.0)
        projectiles = []
        particles = []

        # Flintlock available when timer is 0
        julie.flintlock_timer = 0.0
        action = julie.trigger_secondary(8.0, 5.0, projectiles, particles)
        self.assertEqual(action, "shot")
        self.assertEqual(len(projectiles), 1)
        self.assertEqual(julie.flintlock_timer, 6.0, "Flintlock cooldown must be 6.0s")

        # Secondary with flintlock on cooldown -> Cape Flourish
        action2 = julie.trigger_secondary(8.0, 5.0, projectiles, particles)
        self.assertEqual(action2, "flip")
        self.assertEqual(julie.state, "CAPE_FLOURISH")
        self.assertTrue(julie.is_invulnerable_dodge)

    def test_julie_fatalities_mapping(self):
        from src.combat.collision import _get_death_style_for_attacker
        class DummyFighter:
            char_type = "musketeer"
            state = "ATTACK"
        atk = DummyFighter()

        style_rapier = _get_death_style_for_attacker(atk, "rapier")
        self.assertEqual(style_rapier, "RAPIER_BLOOD_FOUNTAIN")

        style_gun = _get_death_style_for_attacker(atk, "flintlock")
        self.assertEqual(style_gun, "FLINTLOCK_EXECUTION")

    def test_continuous_intro_victory_scripts(self):
        from src.entities import pose_scripts

        for char_key in ("pirate", "musketeer"):
            for anim in ("intro", "victory"):
                for step in range(21):
                    p = step / 20.0
                    pf = pose_scripts.sample(char_key, anim, p)
                    self.assertIsNotNone(pf, f"PoseFrame cannot be None for {char_key} {anim} at {p}")
                    self.assertNotEqual(pf.state, "", f"State cannot be empty for {char_key} {anim} at {p}")
                    seg_u = pf.extra.get("seg_u")
                    if seg_u is not None:
                        self.assertTrue(0.0 <= seg_u <= 1.0001, f"seg_u out of bounds ({seg_u}) for {char_key} {anim} at {p}")

                end_pf = pose_scripts.sample(char_key, anim, 1.0)
                self.assertIsNotNone(end_pf)
                self.assertIn("seg_u", end_pf.extra)

    def test_corpse_pieces_for_new_fatalities(self):
        from src.entities.voxel_corpse import VoxelCorpse

        class DummyVictim:
            wx = 10.0
            wy = 10.0
            wz = 0.0
            facing_x = 1.0
            facing_y = 0.0
            is_grounded = True
            char_type = "red"
            palette = {}

        victim = DummyVictim()

        for style in ("ARANAMI_CLEAVE", "KANPOU_SENMETSU", "RAPIER_BLOOD_FOUNTAIN", "FLINTLOCK_EXECUTION"):
            corpse = VoxelCorpse(victim, death_style=style)
            self.assertGreater(len(corpse.pieces), 0, f"Corpse must have pieces for {style}")
            corpse.update(0.016, None, [])
            self.assertGreater(corpse.timer, 0)

    def test_model_inspector_and_help_sync(self):
        from tools.model_inspector import CHARACTER_ANIM_BUTTONS, OVERHAUL_DE_PARA_NOTES
        from src.ui.game_help import FIGHTERS_GUIDE_DATA

        for key in ("anne", "julie"):
            self.assertIn(key, CHARACTER_ANIM_BUTTONS, f"{key} missing in CHARACTER_ANIM_BUTTONS")
            self.assertGreaterEqual(len(CHARACTER_ANIM_BUTTONS[key]), 10, f"{key} buttons should have all moves")
            self.assertIn(key, OVERHAUL_DE_PARA_NOTES, f"{key} missing in OVERHAUL_DE_PARA_NOTES")
            self.assertGreaterEqual(len(OVERHAUL_DE_PARA_NOTES[key]), 4, f"{key} notes should describe overhaul")

        # Also check aliases
        self.assertIn("pirate", CHARACTER_ANIM_BUTTONS)
        self.assertIn("musketeer", CHARACTER_ANIM_BUTTONS)
        self.assertIn("pirate", OVERHAUL_DE_PARA_NOTES)
        self.assertIn("musketeer", OVERHAUL_DE_PARA_NOTES)

        # Check help cards
        anne_help = [c for c in FIGHTERS_GUIDE_DATA if c.get("char_type") in ("pirate", "anne")]
        julie_help = [c for c in FIGHTERS_GUIDE_DATA if c.get("char_type") in ("musketeer", "julie")]
        self.assertGreater(len(anne_help), 0, "Anne help card must exist in FIGHTERS_GUIDE_DATA")
        self.assertGreater(len(julie_help), 0, "Julie help card must exist in FIGHTERS_GUIDE_DATA")
        self.assertIn("Aranami", anne_help[0]["pt"]["habilidades"])
        self.assertIn("Hyakka", julie_help[0]["pt"]["habilidades"])

    def test_dodge_somersault_extra_props(self):
        from src.entities.pirate import PirateSwordswoman
        from src.entities.musketeer import Musketeer
        from unittest.mock import MagicMock, patch

        # Anne dodge somersault props
        anne = PirateSwordswoman(5.0, 5.0)
        anne.trigger_roll(1.0, 0.0)
        anne.state_timer = anne.roll_duration * 0.5
        with patch("src.entities.pirate.render_voxel_humanoid") as mock_render:
            anne.render(MagicMock(), MagicMock())
            self.assertTrue(mock_render.called)
            kwargs = mock_render.call_args[1]
            extra = kwargs.get("extra_props", {})
            self.assertTrue(extra.get("is_roll"))
            self.assertAlmostEqual(extra.get("somersault_angle"), -180.0, delta=1.0)
            self.assertIn("somersault_pivot_z", extra)

        # Julie dodge somersault props
        julie = Musketeer(5.0, 5.0)
        julie.trigger_roll(-1.0, 0.0)
        julie.state_timer = julie.roll_duration * 0.5
        with patch("src.entities.musketeer.render_voxel_humanoid") as mock_render_j:
            julie.render(MagicMock(), MagicMock())
            self.assertTrue(mock_render_j.called)
            kwargs = mock_render_j.call_args[1]
            extra = kwargs.get("extra_props", {})
            self.assertTrue(extra.get("is_roll"))
            self.assertAlmostEqual(extra.get("somersault_angle"), 180.0, delta=1.0)
            self.assertIn("somersault_pivot_z", extra)

    def test_julie_and_anne_intro_victory_smooth_and_active(self):
        from src.entities import anne_model, julie_model, pose_scripts

        class DummyC:
            def __init__(self, char, state, p, seg_u, pose):
                self.torso_z = 0.40
                self.base_x = 0.0
                self.base_y = 0.0
                self.fx = 1.0
                self.fy = 0.0
                self.px = 0.0
                self.py = 1.0
                self.state = state
                self.is_melee = False
                self.atk_progress = 0.0
                self.extra_props = {"p": p, "seg_u": seg_u, "pose": pose}

        for char_name, model_mod in [("pirate", anne_model), ("musketeer", julie_model)]:
            for state in ["INTRO", "VICTORY"]:
                prev_left, prev_right = None, None
                static_count = 0
                max_step_dist = 0.0
                steps = 100
                for i in range(steps + 1):
                    p = i / float(steps)
                    pf = pose_scripts.sample(char_name, state.lower(), p)
                    seg_u = pf.extra.get("seg_u", p)
                    pose = pf.extra.get("pose")
                    c = DummyC(char_name, state, p, seg_u, pose)
                    l, r = model_mod.get_arms(c)
                    if prev_left is not None:
                        d_l = math.dist(l, prev_left)
                        d_r = math.dist(r, prev_right)
                        max_step_dist = max(max_step_dist, d_l, d_r)
                        if d_l < 1e-5 and d_r < 1e-5:
                            static_count += 1
                    prev_left, prev_right = l, r

                # Zero static freeze policy: must not stay completely frozen
                self.assertLess(static_count, 5, f"{char_name} {state} has {static_count} frozen steps!")
                # C0 continuity: step distance per 0.01 progress should be small (no jumps > 0.035m)
                self.assertLess(max_step_dist, 0.035, f"{char_name} {state} has jarring jump of {max_step_dist:.4f}m!")

    def test_julie_victory_render_no_crash(self):
        from src.entities.voxel_models import render_voxel_humanoid
        from src.isometric.camera import Camera
        surf = pygame.Surface((320, 240), pygame.SRCALPHA)
        cam = Camera()

        for step in range(11):
            p = step / 10.0
            # Test that rendering Julie during victory at any progress doesn't crash
            render_voxel_humanoid(
                surf, cam,
                0.0, 0.0, 0.0,
                1.0, 0.0,
                "VICTORY", p, True,
                char_type="musketeer"
            )
            render_voxel_humanoid(
                surf, cam,
                0.0, 0.0, 0.0,
                1.0, 0.0,
                "VICTORY", p, True,
                char_type="pirate"
            )

    def test_julie_primary_finisher_flurry_and_blood_direction(self):
        from src.effects.cinematic_director import CinematicDirector
        from src.entities.musketeer import Musketeer
        from src.entities import julie_model

        director = CinematicDirector()
        julie = Musketeer(5.0, 5.0)
        julie.set_facing(6.0, 5.0)

        class DummyVictim:
            wx = 6.0
            wy = 5.0
            wz = 0.0
            facing_x = -1.0
            facing_y = 0.0
            state = "IDLE"
            extra_props = {}
            char_type = "red"
            palette = {}

        victim = DummyVictim()
        director.trigger_fatal_strike(julie, victim, death_style="RAPIER_BLOOD_FOUNTAIN", slash_dir=(1.0, 0.0))

        self.assertGreater(director.julie_flurry_timer, 0.0, "Julie flurry timer must be active")
        self.assertTrue(director.is_active)

        # Fast-forward camera swoop (0.60s setup) to reach execution phase
        director.camera_setup_timer = 0.0

        particles = []
        hand_positions = []

        class DummyC:
            def __init__(self, props, fx=1.0, fy=0.0):
                self.torso_z = 0.40
                self.base_x = 5.0
                self.base_y = 5.0
                self.fx = fx
                self.fy = fy
                self.px = -fy
                self.py = fx
                self.state = "ATTACK"
                self.is_melee = True
                self.atk_progress = props.get("thrust_phase", 0.0)
                self.extra_props = props

        # Simulate several flurry frames
        for _ in range(15):
            director.update(0.025, None, particles)
            c = DummyC(julie.extra_props, julie.facing_x, julie.facing_y)
            l, r = julie_model.get_arms(c)
            hand_positions.append(r)

        # 1. Zero static check: Julie's right hand holding rapier must actively move
        unique_x = {round(pos[0], 3) for pos in hand_positions}
        self.assertGreater(len(unique_x), 4, f"Julie's rapier hand should actively move during flurry, got {unique_x}")

        # 2. Standing upright check: Victim must remain standing in DYING_FREEZE without falling
        self.assertEqual(victim.state, "DYING_FREEZE", "Victim must remain standing in DYING_FREEZE during flurry")
        self.assertEqual(victim.extra_props.get("kneel_prog", 0.0), 0.0, "Victim must not kneel during flurry")

        # 3. Blood volume check: 5x blood generated
        from src.effects.particles import BloodParticle
        blood_particles = [p for p in particles if isinstance(p, BloodParticle)]
        self.assertGreater(len(blood_particles), 150, f"Expected >150 blood particles in flurry bursts, got {len(blood_particles)}")

        # 4. Directional check: Blood must squirt in opposite direction, forward from rival (facing_x = -1.0)
        rival_front_blood = [p for p in blood_particles if p.vx < -1.5]
        self.assertGreater(len(rival_front_blood), len(blood_particles) * 0.65,
                           "Major portion of blood particles must shoot forward from rival's chest")

        # 5. Phase 2: Victim falls to knees after flurry
        director.julie_flurry_timer = 0.0
        director.update(0.15, None, [])
        self.assertGreater(victim.extra_props.get("kneel_prog", 0.0), 0.20,
                           "Victim must fall to knees after flurry completes")

    def test_julie_corpse_fountain_forward_blood(self):
        from src.entities.voxel_corpse import VoxelCorpse

        class DummyVictim:
            wx = 10.0
            wy = 10.0
            wz = 0.0
            facing_x = -1.0
            facing_y = 0.0
            is_grounded = True
            char_type = "red"
            palette = {}

        corpse = VoxelCorpse(DummyVictim(), death_style="RAPIER_BLOOD_FOUNTAIN", slash_dir=(1.0, 0.0))
        # Initial blood drops: 5x increased (120)
        self.assertGreaterEqual(len(corpse.blood_droplets), 100, "Corpse must spawn >= 100 initial blood drops")

        particles = []
        corpse.update(0.025, None, particles)
        self.assertGreater(len(particles), 35, f"Corpse geyser must burst with high count (>=35), got {len(particles)}")
        # Verify direction: squirts forward from rival (-slash_dir)
        forward_parts = [p for p in particles if p.vx < -1.5]
        self.assertGreater(len(forward_parts), len(particles) * 0.70, "Geyser must shoot forward in front of rival")


if __name__ == "__main__":
    unittest.main()
