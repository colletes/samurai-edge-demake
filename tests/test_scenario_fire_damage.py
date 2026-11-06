"""
Testes unitários e de integração para dano por colisão em fogos do cenário (Campfire, KagaribiBrazier, DohyoBrazier).
Regra: Ao colidir com eles, os lutadores devem tomar 1 de dano.
"""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

from src.world.decor import Campfire, KagaribiBrazier, DohyoBrazier
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.world.arenas import create_arena
from src.config import ARENA_FOREST_CAMP, ARENA_GOJO_BRIDGE, ARENA_DOHYO
from src.effects.particles import FlameVoxelParticle, SparkParticle


class TestScenarioFireDamage(unittest.TestCase):

    def test_campfire_collision_and_damage(self):
        """Testa colisão física e dano de 1 ponto ao tocar a fogueira."""
        fire = Campfire(5.0, 5.0)
        fighter = RedSamurai(5.0, 5.5)
        self.assertEqual(fighter.hp, 2)
        self.assertTrue(fighter.is_alive)

        # Colisão física detectada
        col, px, py = fire.check_collision(fighter.wx, fighter.wy, fighter.radius)
        self.assertTrue(col)

        # Tick com combatente em contato com as chamas
        particles = []
        fire.tick(None, 0.016, [fighter], None, particles, [])

        self.assertEqual(fighter.hp, 1)
        self.assertTrue(fighter.is_alive)
        self.assertTrue(any(isinstance(p, FlameVoxelParticle) for p in particles))
        self.assertTrue(any(isinstance(p, SparkParticle) for p in particles))

        # Próximo frame imediato: cooldown ativo impede dano consecutivo
        fire.tick(None, 0.016, [fighter], None, particles, [])
        self.assertEqual(fighter.hp, 1)

        # Avança tempo para além do cooldown
        for _ in range(60):
            fire.tick(None, 0.016, [fighter], None, particles, [])

        # Segundo hit causa morte
        self.assertEqual(fighter.hp, 0)
        self.assertFalse(fighter.is_alive)

    def test_kagaribi_brazier_collision_and_damage(self):
        """Testa dano de fogo no braseiro de ferro Kagaribi de Kyoto."""
        brazier = KagaribiBrazier(10.0, 10.0)
        self.assertTrue(getattr(brazier, "animated", False))
        fighter = BlueSamurai(10.0, 10.4)
        initial_hp = fighter.hp

        particles = []
        brazier.tick(None, 0.016, [fighter], None, particles, [])

        self.assertEqual(fighter.hp, initial_hp - 1)
        self.assertTrue(fighter.is_alive)
        self.assertTrue(any(isinstance(p, FlameVoxelParticle) for p in particles))

    def test_dohyo_brazier_collision_and_damage(self):
        """Testa dano de fogo no braseiro ritual do Dohyo."""
        brazier = DohyoBrazier(7.0, 7.0)
        self.assertTrue(getattr(brazier, "animated", False))
        fighter = RedSamurai(7.0, 7.4)
        self.assertEqual(fighter.hp, 2)

        particles = []
        brazier.tick(None, 0.016, [fighter], None, particles, [])

        self.assertEqual(fighter.hp, 1)
        self.assertTrue(fighter.is_alive)

    def test_aerial_fighter_avoids_campfire(self):
        """Lutadores no ar muito acima da fogueira não tomam dano de chão."""
        fire = Campfire(5.0, 5.0)
        fighter = RedSamurai(5.0, 5.2)
        fighter.wz = 1.2  # Alto no ar

        fire.tick(None, 0.016, [fighter], None, [], [])
        self.assertEqual(fighter.hp, 2)

    def test_arena_emitters_registration(self):
        """Verifica se os braseiros e fogueiras são registrados em emitters nas arenas."""
        from src.isometric.camera import Camera

        camera = Camera()

        # Arena 6: Ninja Forest (possui campfire)
        arena6 = create_arena(ARENA_FOREST_CAMP)
        campfires = [e for e in arena6.emitters if isinstance(e, Campfire)]
        self.assertGreater(len(campfires), 0)

        # Arena 11: Gojo Bridge (possui kagaribi)
        arena11 = create_arena(ARENA_GOJO_BRIDGE)
        kagaribi = [e for e in arena11.emitters if isinstance(e, KagaribiBrazier)]
        self.assertGreater(len(kagaribi), 0)

        # Arena 23: Sacred Dohyo (possui dohyo_brazier)
        arena23 = create_arena(ARENA_DOHYO)
        dohyo_braziers = [e for e in arena23.emitters if isinstance(e, DohyoBrazier)]
        self.assertGreater(len(dohyo_braziers), 0)

        # Arena update roda sem erros com lutadores
        p1 = RedSamurai(10.0, 10.0)
        p2 = BlueSamurai(12.0, 10.0)
        arena11.update(0.016, [p1, p2], camera, [], [])


if __name__ == "__main__":
    unittest.main()
