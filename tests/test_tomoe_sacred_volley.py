"""
Suíte de testes automatizados para o novo ataque secundário de Tomoe:
Chuva de Flechas Sagradas em Arco (Salva Sagrada / Sacred Arrow Volley).

Validações obrigatórias da solicitação:
1. Mecanismo de mira idêntico ao da Anne (Hold, update suave do retículo e Release; quick fire para IA).
2. Cooldown idêntico ao da Anne (4.5s e timer inicial de 4.5s no início do round).
3. Disparo em arco de várias flechas sagradas em uma pequena área concentrada.
4. Dano letal (2 HP) ao oponente na área de impacto.
"""
import os
import sys
import unittest
import math
import pygame

# Set dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
pygame.init()
pygame.font.init()

from src.entities.kyudo_archer import KyudoArcher
from src.entities.pirate import PirateSwordswoman
from src.entities.red_samurai import RedSamurai
from src.entities.projectile import SacredArrowVolleyProjectile
from src.combat.collision import CombatSystem
from src.world.map_data import GameMap
from src.isometric.camera import Camera


class TestTomoeSacredVolley(unittest.TestCase):
    def setUp(self):
        self.game_map = GameMap()
        self.camera = Camera(10.0, 10.0)
        self.combat = CombatSystem()
        self.tomoe = KyudoArcher(5.0, 10.0)
        self.anne = PirateSwordswoman(5.0, 10.0)
        self.enemy = RedSamurai(10.0, 10.0)

    def test_cooldown_identical_to_anne(self):
        """Teste 1: Cooldown de Tomoe é idêntico ao de Anne (4.5s de cooldown e 4.5s no início do round)."""
        # 1. Ambos iniciam o round com 4.5s de cooldown para evitar spawn nuke
        self.assertEqual(self.tomoe.volley_cooldown, self.anne.cannon_cooldown)
        self.assertEqual(self.tomoe.volley_cooldown, 4.5)
        self.assertEqual(self.tomoe.volley_cooldown_timer, 4.5)
        self.assertEqual(self.anne.cannon_cooldown_timer, 4.5)

        # 2. Ao zerar o cooldown e disparar (quick ou release), ambos voltam para exatamente 4.5s
        self.tomoe.volley_cooldown_timer = 0.0
        self.anne.cannon_cooldown_timer = 0.0
        projectiles = []

        self.tomoe.trigger_quick_volley(10.0, 10.0, projectiles)
        self.assertEqual(self.tomoe.volley_cooldown_timer, 4.5)

        anne_projs = []
        self.anne.trigger_quick_cannon(10.0, 10.0, anne_projs)
        self.assertEqual(self.anne.cannon_cooldown_timer, 4.5)

    def test_aiming_mechanism_identical_to_anne(self):
        """Teste 2: Mecanismo de mira Hold, Update e Release idêntico ao de Anne."""
        self.tomoe.volley_cooldown_timer = 0.0
        projectiles = []
        particles = []

        # Inicia mira (Hold)
        self.tomoe.start_sacred_volley(12.0, 10.0)
        self.assertTrue(self.tomoe.is_aiming_volley)
        self.assertEqual(self.tomoe.volley_target_wx, 12.0)
        self.assertEqual(self.tomoe.volley_target_wy, 10.0)

        # Atualiza a mira continuamente com interpolação suave (Update)
        dt = 0.05
        prev_pulse = self.tomoe.volley_reticle_pulse
        self.tomoe.update_sacred_volley(dt, 14.0, 11.0)
        self.assertGreater(self.tomoe.volley_reticle_pulse, prev_pulse)
        self.assertGreater(self.tomoe.volley_target_wx, 12.0)

        # Solta o botão (Release): dispara a salva e reseta o estado de mira
        self.tomoe.release_sacred_volley(projectiles, particles)
        self.assertFalse(self.tomoe.is_aiming_volley)
        self.assertEqual(len(projectiles), 1)
        self.assertIsInstance(projectiles[0], SacredArrowVolleyProjectile)
        self.assertEqual(projectiles[0].owner, self.tomoe)
        self.assertEqual(self.tomoe.volley_cooldown_timer, 4.5)

    def test_volley_contains_multiple_sacred_arrows_in_small_area(self):
        """Teste 3: Disparo em arco contendo múltiplas flechas sagradas em pequena área."""
        self.tomoe.volley_cooldown_timer = 0.0
        projectiles = []
        self.tomoe.trigger_quick_volley(10.0, 10.0, projectiles)
        self.assertEqual(len(projectiles), 1)

        volley = projectiles[0]
        self.assertIsInstance(volley, SacredArrowVolleyProjectile)
        # Pequena área concentrada
        self.assertLessEqual(volley.radius, 1.5)
        self.assertGreaterEqual(volley.radius, 1.0)
        # Múltiplas flechas sagradas na salva (>= 5 flechas)
        self.assertGreaterEqual(len(volley.arrows), 5)

        # Cada flecha é direcionada para a pequena área em torno do alvo
        for a in volley.arrows:
            dist = math.hypot(a["dest_x"] - 10.0, a["dest_y"] - 10.0)
            self.assertLessEqual(dist, 1.0, f"Flecha dispersa além da pequena área: {dist}")
            self.assertGreaterEqual(a["apex"], 4.0, "Trajetória deve atingir altura parabólica em arco")

    def test_volley_lethal_damage_2_hp(self):
        """Teste 4: Dano letal (2 HP) ao oponente na área de impacto."""
        self.tomoe.volley_cooldown_timer = 0.0
        projectiles = []
        self.tomoe.trigger_quick_volley(10.0, 10.0, projectiles)
        volley = projectiles[0]

        # O inimigo começa com 2 HP
        self.assertEqual(self.enemy.hp, 2)
        self.assertTrue(self.enemy.is_alive)

        # Posiciona o inimigo no centro do impacto
        self.enemy.wx, self.enemy.wy = 10.0, 10.0

        # Simula o avanço do tempo até a aterrissagem das flechas
        particles = []
        banners = []
        total_time = 0.0
        while total_time < 0.50 and self.enemy.is_alive:
            dt = 0.02
            total_time += dt
            self.combat.process_combat(
                self.tomoe, self.enemy, self.game_map, particles, banners, self.camera, projectiles, dt=dt
            )

        # O inimigo deve ter levado 2 de dano e morrido (dano letal)
        self.assertEqual(self.enemy.hp, 0)
        self.assertFalse(self.enemy.is_alive)

    def test_render_reticle_without_errors(self):
        """Teste 5: Renderização do retículo de mira idêntico ao da Anne sem erros."""
        self.tomoe.volley_cooldown_timer = 0.0
        self.tomoe.start_sacred_volley(8.0, 10.0)
        surface = pygame.Surface((800, 600))
        # Deve renderizar com sucesso sem exceções
        self.tomoe.render(surface, self.camera)


if __name__ == "__main__":
    unittest.main()
