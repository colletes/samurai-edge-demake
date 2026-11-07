"""
Testes automatizados da Sub-fase 2.15: Overhaul de Benkei (O Monge Guardião — Naginata Pesada & Walking Tank).
Valida:
1. Atributos de Tanque e gameplay base (can_parry=False, velocidade 4.35, 2 HP).
2. Combo de Inércia da Naginata: Varredura 170° (2.4m) conectando em Estocada Colossal (2.8m).
3. Reset do combo após expiração da janela (0.55s).
4. Adamantine Guard Push (Avanço blindado com 12 i-frames, deflexão de projéteis e empurrão frontal).
5. Transição desarmada após arremesso da Naginata e Tackle com STUN de 1.2s.
6. Modelo 3D benkei_model: get_arms(c), materiais PBR e legacy, single-pass weapon rendering.
7. Animações Contínuas: Intro e Victory em pose_scripts sem travamentos ($C^0/C^1$).
8. Sincronização no Model Inspector: botões de animação interativos e notas De/Para.
"""
import os
import sys
import unittest
import math

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((800, 600))

from src.entities.benkei import BenkeiSamurai, STATE_ATTACK, STATE_ROLL, STATE_TACKLE_CHARGE
from src.entities.samurai import STATE_IDLE, STATE_RECOVERY
from src.entities.projectile import NaginataProjectile
from src.entities import benkei_model, pose_scripts
from tools import model_inspector


class DummyMap:
    def __init__(self, cols=20, rows=20):
        self.cols = cols
        self.rows = rows
        self.rocks = []
        self.buildings = []
        self.pits = []

    def pit_at(self, x, y):
        return None


class DummyOpponent:
    def __init__(self, wx=6.0, wy=5.0):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.radius = 0.35
        self.is_alive = True
        self.stun_timer = 0.0
        self.displaced = False

    def stun(self, duration: float):
        self.stun_timer = duration

    def apply_forced_displacement(self, dx: float, dy: float, game_map=None):
        self.wx += dx
        self.wy += dy
        self.displaced = True


class TestBenkeiOverhaul(unittest.TestCase):
    def test_benkei_initialization_and_traits(self):
        """Verifica atributos base de Benkei como Walking Tank."""
        benkei = BenkeiSamurai(5.0, 5.0)
        self.assertEqual(benkei.char_type, "benkei")
        self.assertEqual(benkei.speed, 4.35)
        self.assertEqual(benkei.max_hp, 2)
        self.assertEqual(benkei.hp, 2)
        self.assertFalse(benkei.can_parry)
        self.assertTrue(benkei.has_naginata)
        self.assertFalse(benkei.is_unarmed)
        self.assertEqual(benkei.combo_step, 0)

    def test_benkei_two_step_inertia_combo(self):
        """Verifica o combo de 2 passos da Naginata: Varredura 170° conectando em Estocada 2.8m."""
        benkei = BenkeiSamurai(5.0, 5.0)
        gmap = DummyMap()

        # Passo 1: Varredura Circular em Arco (170°, 2.40m, center offset 1.10)
        success = benkei.trigger_naginata_thrust(7.0, 5.0, game_map=gmap)
        self.assertTrue(success)
        self.assertEqual(benkei.state, STATE_ATTACK)
        self.assertEqual(benkei.combo_step, 1)
        self.assertEqual(benkei.action_name, "Varredura Naginata")
        self.assertEqual(benkei.hitbox_radius, 2.40)
        self.assertAlmostEqual(benkei.hitbox_center[0], 5.0 + 1.10, delta=0.05)

        # Avança tempo para recovery
        benkei.update(0.22, gmap)
        self.assertEqual(benkei.state, STATE_RECOVERY)
        self.assertGreater(benkei.combo_window_timer, 0)

        # Passo 2: Estocada Perfurante Monumental (2.8m, lunge 0.45m, center offset 1.85)
        success2 = benkei.trigger_naginata_thrust(8.0, 5.0, game_map=gmap)
        self.assertTrue(success2)
        self.assertEqual(benkei.state, STATE_ATTACK)
        self.assertEqual(benkei.combo_step, 2)
        self.assertEqual(benkei.action_name, "Estocada Colossal")
        self.assertEqual(benkei.hitbox_radius, benkei.thrust_radius)
        self.assertGreater(benkei.wx, 5.0)  # Avançou 0.45m à frente

        # Termina o combo e volta ao IDLE com combo_step resetado
        benkei.update(0.20, gmap)
        benkei.update(0.25, gmap)
        self.assertEqual(benkei.combo_step, 0)

    def test_benkei_combo_timeout_reset(self):
        """Verifica que o combo_step reseta caso a janela de 0.55s expire."""
        benkei = BenkeiSamurai(5.0, 5.0)
        gmap = DummyMap()

        benkei.trigger_naginata_thrust(7.0, 5.0, game_map=gmap)
        self.assertEqual(benkei.combo_step, 1)

        # Passa o ataque e espera expirar a janela do combo
        benkei.update(0.25, gmap)  # entra em RECOVERY
        benkei.update(0.20, gmap)  # entra em IDLE
        self.assertGreater(benkei.combo_window_timer, 0)

        benkei.update(0.60, gmap)  # expira combo_window_timer
        self.assertEqual(benkei.combo_step, 0)

    def test_benkei_adamantine_guard_push(self):
        """Verifica o Adamantine Guard Push com 12 i-frames, deflexão de projéteis e empurrão."""
        benkei = BenkeiSamurai(5.0, 5.0)
        gmap = DummyMap()
        opp = DummyOpponent(wx=5.8, wy=5.0)
        particles = []
        banners = []

        # Projétil inimigo a 1.2m
        enemy_proj = NaginataProjectile(wx=5.5, wy=5.0, wz=0.3, dir_x=-1.0, dir_y=0.0, owner=None)
        projectiles = [enemy_proj]

        success = benkei.trigger_adamantine_push(1.0, 0.0, particles=particles, banners=banners, opponent=opp, game_map=gmap, projectiles=projectiles)
        self.assertTrue(success)
        self.assertEqual(benkei.state, STATE_ROLL)
        self.assertTrue(benkei.is_invulnerable_dodge)
        self.assertTrue(benkei.invulnerable)
        self.assertTrue(benkei.is_projectile_immune)
        self.assertEqual(benkei.action_name, "Adamantine Push")

        # Projétil inimigo destruído/refletido
        self.assertFalse(enemy_proj.is_active)
        # Oponente adjacente empurrado com deslocamento forçado
        self.assertTrue(opp.displaced)
        self.assertGreater(opp.wx, 5.8)

    def test_benkei_unarmed_tackle_and_recovery(self):
        """Verifica transição desarmada após arremesso e tackle com stun de 1.2s."""
        benkei = BenkeiSamurai(5.0, 5.0)
        gmap = DummyMap()
        opp = DummyOpponent(wx=6.5, wy=5.0)
        projectiles = []

        # Arremesso da Naginata
        success = benkei.trigger_naginata_throw(7.0, 5.0, projectiles=projectiles)
        self.assertTrue(success)
        self.assertFalse(benkei.has_naginata)
        self.assertTrue(benkei.is_unarmed)
        self.assertEqual(len(projectiles), 1)

        benkei.update(0.25, gmap)  # sai de THROW

        # Ataque primário enquanto desarmado dispara Tackle Charge
        banners = []
        particles = []
        tackle_ok = benkei.trigger_naginata_thrust(7.0, 5.0, game_map=gmap)
        self.assertTrue(tackle_ok)
        self.assertEqual(benkei.state, STATE_TACKLE_CHARGE)
        self.assertEqual(benkei.action_name, "Tackle Atropelo")

        # Avança tackle e atinge o oponente aplicando 1.2s de STUN
        benkei.update(0.15, gmap, particles=particles, opponent=opp, banners=banners)
        self.assertEqual(opp.stun_timer, 1.20)
        self.assertTrue(opp.displaced)

        # Recupera a Naginata
        benkei.recover_naginata()
        self.assertTrue(benkei.has_naginata)
        self.assertFalse(benkei.is_unarmed)

    def test_benkei_model_and_materials(self):
        """Verifica interfaces modulares do modelo: get_arms, materiais PBR e legacy."""
        self.assertTrue(hasattr(benkei_model, "get_arms"))
        self.assertIn("iron", benkei_model.MATERIALS)
        self.assertIn("suneate", benkei_model.MATERIALS)
        self.assertIn("wood_shaft", benkei_model.PALETTE)
        self.assertEqual(benkei_model.LEGACY_MATERIALS["iron"], "matte")

    def test_benkei_continuous_intro_and_victory(self):
        """Verifica continuidade C0/C1 das animações de intro e vitória sem travamentos."""
        # Intro
        for p in [0.0, 0.20, 0.35, 0.50, 0.70, 0.85, 1.0]:
            frame = pose_scripts.sample("benkei", "intro", p)
            self.assertIsNotNone(frame)
            self.assertIn("seg_u", frame.extra)

        # Vitória
        for p in [0.0, 0.20, 0.38, 0.55, 0.75, 0.90, 1.0]:
            frame = pose_scripts.sample("benkei", "victory", p)
            self.assertIsNotNone(frame)
            self.assertIn("seg_u", frame.extra)

    def test_benkei_model_inspector_synchronization(self):
        """Verifica registro de Benkei no 3D Model Inspector com De/Para e botões de animação."""
        self.assertIn("benkei", model_inspector.OVERHAUL_DE_PARA_NOTES)
        notes = model_inspector.OVERHAUL_DE_PARA_NOTES["benkei"]
        self.assertGreaterEqual(len(notes), 5)
        self.assertTrue(any("Varredura 170°" in n for n in notes))
        self.assertTrue(any("Adamantine Guard Push" in n for n in notes))

        self.assertIn("benkei", model_inspector.CHARACTER_ANIM_BUTTONS)
        buttons = model_inspector.CHARACTER_ANIM_BUTTONS["benkei"]
        button_ids = [b[0] for b in buttons]
        self.assertIn("NAGINATA_CLEAVE", button_ids)
        self.assertIn("NAGINATA_THRUST", button_ids)
        self.assertIn("NAGINATA_THROW", button_ids)
        self.assertIn("TACKLE_CHARGE", button_ids)
        self.assertIn("ADAMANTINE_PUSH", button_ids)
        self.assertIn("FINISHER_1", button_ids)
        self.assertIn("FINISHER_2", button_ids)


if __name__ == "__main__":
    unittest.main()
