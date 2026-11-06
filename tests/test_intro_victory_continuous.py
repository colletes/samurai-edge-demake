import os
import sys
import math
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()

from src.entities.pose_scripts import sample
from src.entities import okuni_model, kasumi_model, murasaki_model, teppo_model, saitou_model, hanzo_model, kenshi_model, musashi_model, raiden_model, joe_model


class DummyContext:
    def __init__(self, char_type: str):
        self.char_type = char_type
        self.base_x = 5.0
        self.base_y = 5.0
        self.base_z = 0.0
        self.torso_z = 0.60
        self.pelvis_z = 0.45
        self.head_z = 1.10
        self.fx = 1.0
        self.fy = 0.0
        self.px = 0.0
        self.py = 1.0
        self.is_melee = False
        self.atk_progress = 0.0
        self.walk_timer = 0.5
        self.state_timer = 0.5
        self.state = "IDLE"
        self.is_moving = False
        self.extra_props = {}
        self.legs_data = {
            "L": {"thigh": (5.0, 5.1, 0.45), "shin": (5.0, 5.1, 0.25), "foot": (5.0, 5.1, 0.0)},
            "R": {"thigh": (5.0, 4.9, 0.45), "shin": (5.0, 4.9, 0.25), "foot": (5.0, 4.9, 0.0)},
        }


def get_arms_for_char(char_type: str, c: DummyContext):
    if char_type == "okuni":
        return okuni_model.get_arms(c)
    elif char_type == "kasumi":
        return kasumi_model.get_arms(c)
    elif char_type == "murasaki":
        return murasaki_model.get_arms(c)
    elif char_type == "rifleman":
        return teppo_model.get_arms(c)
    elif char_type == "saitou":
        return saitou_model.get_arms(c)
    elif char_type == "ninja":
        return hanzo_model.get_arms(c)
    elif char_type == "kenshin":
        return kenshi_model.idle_arms(c)
    elif char_type == "musashi":
        return musashi_model.get_arms(c)
    elif char_type == "raiden":
        return raiden_model.get_arms(c)
    elif char_type == "american":
        return joe_model.get_arms(c)
    raise ValueError(f"Unknown char_type {char_type}")


class TestIntroVictoryContinuous(unittest.TestCase):
    def _test_character_animation_stream(self, char_type: str, kind: str):
        c = DummyContext(char_type)
        c.state = kind.upper()
        
        positions = []
        steps = 25
        for i in range(steps + 1):
            p = i / float(steps)
            frame = sample(char_type, kind, p)
            c.extra_props = {**frame.extra, "p": p, "intro_victory_state": kind.upper()}
            c.state_timer = p
            l, r = get_arms_for_char(char_type, c)
            self.assertIsNotNone(l)
            self.assertIsNotNone(r)
            positions.append((p, l, r))

        # 1. Verifica continuidade suave entre frames adjacentes (sem teleportes)
        for i in range(len(positions) - 1):
            p0, l0, r0 = positions[i]
            p1, l1, r1 = positions[i + 1]
            dl = math.sqrt((l1[0] - l0[0])**2 + (l1[1] - l0[1])**2 + (l1[2] - l0[2])**2)
            dr = math.sqrt((r1[0] - r0[0])**2 + (r1[1] - r0[1])**2 + (r1[2] - r0[2])**2)
            # Entre passos consecutivos (4% do tempo), os braços não devem saltar mais que 0.35m
            self.assertLess(dl, 0.35, f"{char_type} {kind} arm_l jumped {dl:.3f}m between p={p0:.2f} and p={p1:.2f}")
            self.assertLess(dr, 0.35, f"{char_type} {kind} arm_r jumped {dr:.3f}m between p={p0:.2f} and p={p1:.2f}")

        # 2. Zero Static Freeze Policy: a fase final (80% a 100%) deve apresentar movimento
        late_positions = positions[int(steps * 0.8):]
        total_delta = 0.0
        for i in range(len(late_positions) - 1):
            _, l0, r0 = late_positions[i]
            _, l1, r1 = late_positions[i + 1]
            total_delta += math.sqrt((l1[0] - l0[0])**2 + (l1[1] - l0[1])**2 + (l1[2] - l0[2])**2)
            total_delta += math.sqrt((r1[0] - r0[0])**2 + (r1[1] - r0[1])**2 + (r1[2] - r0[2])**2)

        self.assertGreater(total_delta, 0.005, f"{char_type} {kind} was static/frozen during the final phase (delta={total_delta})")

    def test_okuni_continuous(self):
        self._test_character_animation_stream("okuni", "intro")
        self._test_character_animation_stream("okuni", "victory")

    def test_kasumi_continuous(self):
        self._test_character_animation_stream("kasumi", "intro")
        self._test_character_animation_stream("kasumi", "victory")

    def test_murasaki_continuous(self):
        self._test_character_animation_stream("murasaki", "intro")
        self._test_character_animation_stream("murasaki", "victory")

    def test_teppo_continuous(self):
        self._test_character_animation_stream("rifleman", "intro")
        self._test_character_animation_stream("rifleman", "victory")

    def test_saitou_continuous(self):
        self._test_character_animation_stream("saitou", "intro")
        self._test_character_animation_stream("saitou", "victory")

    def test_hanzo_continuous(self):
        self._test_character_animation_stream("ninja", "intro")
        self._test_character_animation_stream("ninja", "victory")

    def test_kenshi_continuous(self):
        self._test_character_animation_stream("kenshin", "intro")
        self._test_character_animation_stream("kenshin", "victory")

    def test_musashi_continuous(self):
        self._test_character_animation_stream("musashi", "intro")
        self._test_character_animation_stream("musashi", "victory")

    def test_raiden_continuous(self):
        self._test_character_animation_stream("raiden", "intro")
        self._test_character_animation_stream("raiden", "victory")

    def test_joe_continuous(self):
        self._test_character_animation_stream("american", "intro")
        self._test_character_animation_stream("american", "victory")


if __name__ == "__main__":
    unittest.main()
