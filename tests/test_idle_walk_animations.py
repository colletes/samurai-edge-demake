import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import unittest
import pygame
from src.isometric.camera import Camera
from src.isometric.voxel_rig import calc_leg_joints, calc_character_idle_pose
from src.entities.voxel_models import render_voxel_humanoid

class TestIdleWalkAnimations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.surface = pygame.Surface((800, 600))
        cls.camera = Camera(10.0, 10.0)

    def test_calc_character_idle_poses(self):
        chars = [
            "kenshin", "musashi", "ninja", "american", "kasumi", "murasaki",
            "saitou", "teppo", "okuni", "tomoe", "anne", "julie"
        ]
        for c in chars:
            arm_l, arm_r, meta = calc_character_idle_pose(
                c, 0.0, 0.0, 0.8, 1.0, 0.0, 0.0, 1.0, 0.5
            )
            self.assertEqual(len(arm_l), 3, f"Arm L should have 3 coordinates for {c}")
            self.assertEqual(len(arm_r), 3, f"Arm R should have 3 coordinates for {c}")
            self.assertIn("pose", meta, f"Metadata should have pose key for {c}")

    def test_calc_leg_joints_idle_and_walk(self):
        chars = [
            "kenshin", "musashi", "ninja", "american", "kasumi", "murasaki",
            "saitou", "teppo", "okuni", "tomoe", "anne", "julie"
        ]
        for c in chars:
            legs_idle = calc_leg_joints(
                0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
                is_moving=False, walk_timer=0.2,
                is_attack=False, atk_progress=0.0,
                char_type=c
            )
            legs_walk = calc_leg_joints(
                0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
                is_moving=True, walk_timer=0.2,
                is_attack=False, atk_progress=0.0,
                char_type=c
            )
            self.assertIn("L", legs_idle)
            self.assertIn("R", legs_idle)
            self.assertIn("L", legs_walk)
            self.assertIn("R", legs_walk)
            # Lift or swing should be active during walk
            self.assertTrue(
                legs_walk["L"]["lift"] > 0.0 or legs_walk["R"]["lift"] > 0.0 or legs_walk["L"]["foot"][0] != legs_walk["R"]["foot"][0]
            )

    def test_render_voxel_character_all_12_idle_and_walk(self):
        chars = [
            "kenshin", "musashi", "ninja", "american", "kasumi", "murasaki",
            "saitou", "rifleman", "okuni", "archer", "pirate", "musketeer"
        ]
        for char_type in chars:
            # 1. Test Idle rendering
            render_voxel_humanoid(
                self.surface, self.camera,
                wx=10.0, wy=10.0, wz=0.0,
                facing_x=1.0, facing_y=0.0,
                state="IDLE", state_timer=0.0,
                is_alive=True,
                char_type=char_type,
                walk_timer=1.2,
                is_moving=False
            )

            # 2. Test Walk rendering
            render_voxel_humanoid(
                self.surface, self.camera,
                wx=10.0, wy=10.0, wz=0.0,
                facing_x=1.0, facing_y=0.0,
                state="WALK", state_timer=0.0,
                is_alive=True,
                char_type=char_type,
                walk_timer=0.45,
                is_moving=True
            )

if __name__ == "__main__":
    unittest.main()
