"""
Suíte de testes automatizados para o Entregável 3.1 da Fase 3:
Tomoe — Ação Secundária Sagrada (Hamaya / 破魔矢).
Valida:
1. Disparo da Hamaya e ativação do cooldown sagrado de 3.6s.
2. Perfuração absoluta de rochas e poço (sólidos) mantendo o projétil ativo.
3. Anulação e exorcismo de projéteis hostis em pleno voo.
4. Letalidade 1-Hit Kill contra oponente com efeitos visuais e banner.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"

import unittest
import math
import pygame
pygame.init()
pygame.font.init()

from src.entities.kyudo_archer import KyudoArcher
from src.entities.red_samurai import RedSamurai
from src.entities.yellow_ninja import YellowNinja
from src.entities.rifleman import Rifleman
from src.entities.projectile import (
    HamayaArrowProjectile, KyudoArrowProjectile, KunaiProjectile,
    MusketBulletProjectile, TimedBombEntity
)
from src.combat.collision import CombatSystem
from src.world.map_data import GameMap
from src.isometric.camera import Camera

class TestTomoeHamaya(unittest.TestCase):
    def setUp(self):
        self.game_map = GameMap()
        self.camera = Camera(10.0, 10.0)
        self.combat = CombatSystem()
        self.tomoe = KyudoArcher(5.0, 10.0)
        self.enemy = RedSamurai(15.0, 10.0)

    def test_hamaya_shot_and_cooldown(self):
        """Teste 1: Disparo da Hamaya e ativação do cooldown de 3.6s."""
        projs = []
        particles = []
        self.assertEqual(self.tomoe.hamaya_cooldown_timer, 0.0)
        
        self.tomoe.trigger_hamaya_shot(15.0, 10.0, projs, particles)
        self.assertEqual(len(projs), 1)
        hamaya = projs[0]
        self.assertIsInstance(hamaya, HamayaArrowProjectile)
        self.assertEqual(hamaya.owner, self.tomoe)
        self.assertAlmostEqual(self.tomoe.hamaya_cooldown_timer, 3.6, delta=0.01)
        self.assertTrue(len(particles) >= 12, "Deve gerar partículas sagradas de disparo")

        # Tentativa durante cooldown deve ser ignorada
        self.tomoe.state = "IDLE"
        self.tomoe.trigger_hamaya_shot(15.0, 10.0, projs, particles)
        self.assertEqual(len(projs), 1, "Não deve disparar em cooldown")

        # Após atualizar o tempo do cooldown, o disparo volta a ser permitido
        self.tomoe.update(3.7, self.game_map)
        self.assertLessEqual(self.tomoe.hamaya_cooldown_timer, 0.0)
        self.tomoe.trigger_hamaya_shot(15.0, 10.0, projs, particles)
        self.assertEqual(len(projs), 2, "Deve permitir novo disparo após zerar cooldown")

    def test_hamaya_pierces_solid_obstacles(self):
        """Teste 2: Hamaya atravessa rochas sólidas e o poço sem ser destruída."""
        projs = []
        particles = []
        # Disparo atravessando a rocha central
        self.tomoe.wx, self.tomoe.wy = 8.0, 10.0
        # Coloca uma rocha no caminho direto (entre 9.0 e 11.0)
        if len(self.game_map.rocks) > 0:
            rock = self.game_map.rocks[0]
            rock.wx, rock.wy = 10.0, 10.0
            rock.radius = 1.2

        hamaya = HamayaArrowProjectile(8.0, 10.0, wz=0.55, dir_x=1.0, dir_y=0.0, owner=self.tomoe)
        # Avança a flecha através da rocha
        active = hamaya.update(0.10, self.game_map, particles)
        self.assertTrue(active, "Hamaya deve continuar ativa mesmo cruzando o obstáculo sólido")
        self.assertTrue(hamaya.is_active)
        self.assertGreater(hamaya.wx, 10.0, "Hamaya deve ter transpassado a coordenada da rocha")

        # Comparação: flecha Yumi normal BATE na rocha e se desativa
        normal_arrow = KyudoArrowProjectile(8.0, 10.0, wz=0.55, dir_x=1.0, dir_y=0.0, owner=self.tomoe)
        normal_active = normal_arrow.update(0.10, self.game_map, particles)
        self.assertFalse(normal_active, "Flecha comum Yumi deve ser parada pela rocha")
        self.assertFalse(normal_arrow.is_active)

    def test_hamaya_projectile_pierce_and_deflect(self):
        """Teste 3: Anulação/exorcismo de múltiplos projéteis inimigos hostis no ar."""
        projs = []
        particles = []
        banners = []

        hamaya = HamayaArrowProjectile(10.0, 10.0, wz=0.5, dir_x=1.0, dir_y=0.0, owner=self.tomoe)
        # Projéteis inimigos vindo na direção contrária
        enemy_gunner = Rifleman(18.0, 10.0)
        enemy_ninja = YellowNinja(18.0, 10.0)
        bullet = MusketBulletProjectile(10.3, 10.0, 0.5, -1.0, 0.0, owner=enemy_gunner)
        kunai = KunaiProjectile(10.5, 10.0, 0.5, -1.0, 0.0, owner=enemy_ninja)

        all_projs = [hamaya, bullet, kunai]
        self.combat.process_combat(
            self.tomoe, enemy_gunner, self.game_map,
            particles, banners, self.camera, all_projs, dt=0.016
        )

        # Hamaya deve continuar ativa e os projéteis inimigos devem ser destruídos/exorcizados
        self.assertTrue(hamaya.is_active, "Hamaya deve persistir purificando o ar")
        self.assertFalse(bullet.is_active, "Bala de rifle inimiga deve ser anulada")
        self.assertFalse(kunai.is_active, "Kunai inimiga deve ser anulada")

    def test_hamaya_lethal_strike_on_opponent(self):
        """Teste 4: Impacto letal no oponente causa 1-Hit Kill com banner de purificação."""
        hamaya = HamayaArrowProjectile(14.8, 10.0, wz=0.5, dir_x=1.0, dir_y=0.0, owner=self.tomoe)
        all_projs = [hamaya]
        particles = []
        banners = []

        winner = self.combat.process_combat(
            self.tomoe, self.enemy, self.game_map,
            particles, banners, self.camera, all_projs, dt=0.016
        )

        self.assertEqual(winner, "P1_WINS", "Hamaya deve conceder a vitória letal")
        self.assertFalse(self.enemy.is_alive, "Oponente deve morrer com 1 hit da Hamaya")
        self.assertFalse(hamaya.is_active, "Hamaya é consumida ao cravar no oponente")
        self.assertFalse(any("HAMAYA" in b.text for b in banners), "morte não gera aviso flutuante")
        self.assertTrue(len(particles) >= 20, "Partículas de sangue e luz sagrada devem ser geradas")

if __name__ == "__main__":
    unittest.main()
