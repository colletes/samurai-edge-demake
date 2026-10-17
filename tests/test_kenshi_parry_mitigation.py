import os
import sys
import unittest
import math

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.combat.collision import CombatSystem
from src.world.map_data import GameMap
from src.isometric.camera import Camera
from src.entities.samurai import STATE_PARRY, STATE_RECOVERY, STATE_IDLE, STATE_STUNNED

class TestKenshiParryMitigation(unittest.TestCase):
    def setUp(self):
        self.arena = GameMap()
        self.combat = CombatSystem()
        self.camera = Camera(10.0, 10.0)
        self.particles = []
        self.banners = []

    def test_ryuu_tsui_sen_parry_no_floating(self):
        """Verifica que o Ryuu Tsui Sen aparado não deixa Kenshi flutuando no ar e traz de volta ao solo com i-frames."""
        p1 = RedSamurai(5.0, 5.0)
        p2 = BlueSamurai(5.8, 5.0)
        p2.state = STATE_PARRY
        p2.facing_x, p2.facing_y = -1.0, 0.0

        p1.trigger_ryuu_tsui_sen(5.8, 5.0)
        self.assertEqual(p1.state, "RYUU_TSUI_SEN")
        self.assertGreater(p1.wz, 1.5)

        # Desce até a altura onde a hitbox ativa (< 1.8)
        while not p1.hitbox_active and p1.state == "RYUU_TSUI_SEN":
            p1.update(0.016, self.arena, self.particles)

        self.assertTrue(p1.hitbox_active)
        self.assertGreater(p1.wz, 0.5)

        # Ocorre a colisão com o parry de P2
        self.combat.process_combat(p1, p2, self.arena, self.particles, self.banners, self.camera, [])

        # Deve ter entrado em PARRY_BACKHOP com deflexão aérea e i-frames
        self.assertEqual(p1.state, "PARRY_BACKHOP")
        self.assertTrue(p1.is_aerial_parry)
        self.assertTrue(p1.is_invulnerable_dodge)
        self.assertFalse(p1.hitbox_active)

        # Simular avanço de física até o pouso
        for _ in range(60):
            p1.update(0.016, self.arena, self.particles)
            if p1.state != "PARRY_BACKHOP":
                break

        # Ao pousar: deve estar em STATE_RECOVERY no solo (wz == 0.0)
        self.assertEqual(p1.state, STATE_RECOVERY)
        self.assertEqual(p1.wz, 0.0, "Kenshi não pode ficar flutuando no ar!")
        self.assertFalse(p1.is_invulnerable_dodge)

    def test_grounded_attack_parry_backhop_safe_distance(self):
        """Verifica que o ataque Iai aparado realiza salto de recuo (~2.0 tiles) com i-frames."""
        p1 = RedSamurai(5.0, 5.0)
        p2 = BlueSamurai(5.8, 5.0)
        p2.state = STATE_PARRY
        p2.facing_x, p2.facing_y = -1.0, 0.0

        init_dist = math.hypot(p1.wx - p2.wx, p1.wy - p2.wy)

        p1.trigger_iai_attack(5.8, 5.0)
        self.assertTrue(p1.hitbox_active)

        self.combat.process_combat(p1, p2, self.arena, self.particles, self.banners, self.camera, [])

        self.assertEqual(p1.state, "PARRY_BACKHOP")
        self.assertFalse(p1.is_aerial_parry)
        self.assertTrue(p1.is_invulnerable_dodge)

        # Simular o salto para trás
        for _ in range(30):
            p1.update(0.016, self.arena, self.particles)
            if p1.state != "PARRY_BACKHOP":
                break

        final_dist = math.hypot(p1.wx - p2.wx, p1.wy - p2.wy)
        # Deve ter recuado para longe de P2
        self.assertGreater(final_dist, init_dist + 1.0)
        self.assertEqual(p1.state, STATE_RECOVERY)
        self.assertEqual(p1.wz, 0.0)

    def test_general_stun_resets_wz(self):
        """Verifica que qualquer chamada de stun zera a altura wz, prevenindo flutuação acidental."""
        p1 = RedSamurai(5.0, 5.0)
        p1.wz = 2.4
        p1.stun(0.5)
        self.assertEqual(p1.wz, 0.0)
        self.assertEqual(p1.state, STATE_STUNNED)

    def test_kenshi_as_p2_parried(self):
        """Verifica que Kenshi como P2 também aciona on_parried quando P1 apara."""
        p1 = BlueSamurai(5.0, 5.0)
        p2 = RedSamurai(5.8, 5.0)
        p1.state = STATE_PARRY
        p1.facing_x, p1.facing_y = 1.0, 0.0

        p2.trigger_iai_attack(5.0, 5.0)
        self.combat.process_combat(p1, p2, self.arena, self.particles, self.banners, self.camera, [])

        self.assertEqual(p2.state, "PARRY_BACKHOP")
        self.assertTrue(p2.is_invulnerable_dodge)

if __name__ == "__main__":
    unittest.main()
