import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import unittest
import pygame
pygame.init()

from src.combat.collision import CombatSystem
from src.entities.samurai import STATE_PARRY, STATE_STUNNED, STATE_ROLL
from src.entities.red_samurai import RedSamurai
from src.entities.rifleman import Rifleman
from src.entities.seimei import SeimeiOnmyoji
from src.entities.projectile import MusketBulletProjectile
from src.world.map_data import GameMap
from src.entities.ai_controller import SamuraiAI, DIFFICULTY_NORMAL, DIFFICULTY_HARD

class DummyCamera:
    def __init__(self):
        self.shake = 0.0
    def add_shake(self, val):
        self.shake += val

class TestBulletParryBalance(unittest.TestCase):
    def setUp(self):
        self.combat = CombatSystem()
        self.game_map = GameMap()
        self.camera = DummyCamera()

    def test_bullet_parry_kinetic_pushback_without_stun(self):
        """Testa se aparar uma bala pesada resulta em empurrão cinético de 1.0m SEM atordoar o defensor."""
        teppo = Rifleman(wx=5.0, wy=10.0)
        seimei = SeimeiOnmyoji(wx=7.0, wy=10.0)
        seimei.set_facing(5.0, 10.0) # Olhando para Teppo
        seimei.state = STATE_PARRY
        seimei.state_timer = 0.35

        # Cria a bala voando em direção a Seimei
        bullet = MusketBulletProjectile(wx=6.9, wy=10.0, wz=0.5, dir_x=1.0, dir_y=0.0, owner=teppo, speed=31.2)
        bullet.vx = 31.2
        bullet.vy = 0.0
        projectiles = [bullet]
        particles = []
        banners = []

        initial_seimei_x = seimei.wx

        winner = self.combat.process_combat(
            teppo, seimei, self.game_map, particles, banners, self.camera, projectiles, dt=0.016
        )

        # 1. Bala foi desativada no parry
        self.assertFalse(bullet.is_active)
        # 2. Ninguém morreu
        self.assertIsNone(winner)
        self.assertTrue(seimei.is_alive)
        # 3. Seimei NÃO sofreu STUN (recupera a postura/mantém estado de parry)
        self.assertNotEqual(seimei.state, STATE_STUNNED)
        # 4. Seimei foi empurrado para trás na direção do tiro (~1.0m de deslocamento)
        self.assertGreater(seimei.wx, initial_seimei_x + 0.8)
        # 5. Banner de deflexão pesada gerado
        banner_texts = [b.text for b in banners]
        self.assertTrue(any("DEFLECTION" in b for b in banner_texts))

    def test_ai_bullet_reaction_delay_under_threshold(self):
        """Testa se a IA não reage se o tempo de impacto for inferior ao limiar à queima-roupa (<0.05s)."""
        ai = SamuraiAI(difficulty=DIFFICULTY_NORMAL)
        seimei = SeimeiOnmyoji(wx=10.0, wy=10.0)
        teppo = Rifleman(wx=9.0, wy=10.0) # Distância 1.0m: a 31.2 m/s, impacto é ~0.032s (< 0.05s)

        bullet = MusketBulletProjectile(wx=9.0, wy=10.0, wz=0.5, dir_x=1.0, dir_y=0.0, owner=teppo, speed=31.2)
        bullet.vx = 31.2
        bullet.vy = 0.0

        ai.update(seimei, teppo, dt=0.016, game_map=self.game_map, projectiles=[bullet])

        # Como a bala está a 1m (<0.05s de impacto), a IA não deve ter armada uma reação de defesa
        self.assertFalse(ai.pending_defense_ready)
        self.assertNotEqual(seimei.state, STATE_PARRY)

    def test_ai_prefers_evasion_against_bullet(self):
        """Testa se a IA prefere evasão (roll/dash) em vez de parry estático contra tiros distantes."""
        import random
        random.seed(1234)
        ai = SamuraiAI(difficulty=DIFFICULTY_HARD)
        kenshin = RedSamurai(wx=15.0, wy=10.0)
        teppo = Rifleman(wx=5.0, wy=10.0)

        # Distância 8m: impacto é 8.0 / 31.2 = 0.256s (>0.25s e <= 8.5m dentro do radar de perigo)
        bullet = MusketBulletProjectile(wx=7.0, wy=10.0, wz=0.5, dir_x=1.0, dir_y=0.0, owner=teppo, speed=31.2)
        bullet.vx = 31.2
        bullet.vy = 0.0

        # Simula tempo suficiente para a defesa ficar pronta
        ai.pending_defense_threat = "PROJECTILE"
        ai.pending_defense_ready = True

        ai.update(kenshin, teppo, dt=0.016, game_map=self.game_map, projectiles=[bullet])

        # Kenshin deve ter esquivado (DASH / SHUKUCHI ou ROLL) e NÃO feito parry parado
        self.assertIn(kenshin.state, ("DASH", "SHUKUCHI", STATE_ROLL))

if __name__ == "__main__":
    unittest.main()
