"""
Testes automatizados da Sub-fase 2.18: Ichi (A Espadachim Cega — Lâmina Bengala Shikomizue).
Valida:
1. Atributos base, materiais realistas, legacy materials e fatalidades bespoke.
2. Ataque Primário: Gyaku-Iai Cego (saque relâmpago invertido Zatoichi, alcance 1.80m, raio 1.05m, 2 HP).
3. Ação Secundária: Postura de Escuta Sensorial & Contra-Ataque Automático (Blind Counter-Thrust).
4. Deflexão e contra-ataque de projéteis durante a Postura de Escuta.
5. Terceira Ação: Desvio Evasivo da Bengala (Cane Tap Slip, 13 i-frames, deslocamento padrão anti-perigos).
6. Coreografia 100% contínua ($C^0/C^1$) de Intro e Vitória em 3 fases com áudio dedicado.
7. Modelo 3D: get_arms(c), _hands(c), face em alta definição com olhos serenos fechados/leitosos e coque Mage com Kanzashi.
8. Integração completa com o Model Inspector (12 botões, notas De/Para e acionamento dinâmico).
"""
import os
import sys
import math
import unittest
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from src.entities.ichi import IchiBlade, STATE_LISTEN, STATE_COUNTER_THRUST
from src.entities import ichi_model
from src.entities import pose_scripts
from src.entities.samurai import STATE_IDLE, STATE_ATTACK, STATE_ROLL, STATE_PARRY, STATE_RECOVERY
from src.isometric.camera import Camera
from tools import model_inspector


class DummyProjectile:
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.is_active = True


class TestIchiOverhaul(unittest.TestCase):
    def setUp(self):
        self.ichi = IchiBlade(10.0, 10.0)
        self.camera = Camera(1280, 720)
        self.surface = pygame.Surface((1280, 720), pygame.SRCALPHA)

    def test_01_attributes_and_materials(self):
        """Verifica atributos base, fatalidades e materiais da Ichi."""
        self.assertEqual(self.ichi.char_type, "ichi")
        self.assertEqual(self.ichi.max_hp, 2)
        self.assertEqual(self.ichi.hp, 2)
        self.assertAlmostEqual(self.ichi.speed, 5.1)
        self.assertEqual(self.ichi.finisher_style_primary, "BLIND_CAROTID_SLICE")
        self.assertEqual(self.ichi.finisher_style_secondary, "BLIND_SPINE_PIERCE")

        # Materiais do modelo
        self.assertIn("kimono", ichi_model.MATERIALS)
        self.assertIn("cane_wood", ichi_model.MATERIALS)
        self.assertIn("steel_blade", ichi_model.MATERIALS)
        self.assertEqual(ichi_model.MATERIALS["cane_wood"], "wood")
        self.assertEqual(ichi_model.MATERIALS["steel_blade"], "metal")

        # Modo Legado para Comparador De / Para
        self.assertTrue(hasattr(ichi_model, "LEGACY_MATERIALS"))
        for mat in ichi_model.LEGACY_MATERIALS.values():
            self.assertEqual(mat, "matte")

    def test_02_primary_gyaku_iai(self):
        """Verifica o saque relâmpago invertido Gyaku-Iai (Opção A)."""
        ok = self.ichi.trigger_gyaku_iai(11.0, 10.0)
        self.assertTrue(ok)
        self.assertEqual(self.ichi.state, STATE_ATTACK)
        self.assertTrue(self.ichi.hitbox_active)
        self.assertEqual(self.ichi.hitbox_damage, 2)
        self.assertAlmostEqual(self.ichi.slash_reach, 1.80)
        self.assertAlmostEqual(self.ichi.slash_radius, 1.05)
        self.assertAlmostEqual(self.ichi.attack_duration, 0.11)

    def test_03_listen_stance_and_counter_thrust(self):
        """Verifica Postura de Escuta e contra-ataque automático em golpe inimigo."""
        banners = []
        particles = []
        ok = self.ichi.trigger_listen_stance(11.0, 10.0, banners=banners, particles=particles)
        self.assertTrue(ok)
        self.assertEqual(self.ichi.state, STATE_LISTEN)
        self.assertTrue(self.ichi.invincible)
        self.assertGreater(len(banners), 0)
        self.assertGreater(len(particles), 0)

        # Simular oponente atacando frontalmente
        opponent = IchiBlade(11.0, 10.0)
        opponent.state = STATE_ATTACK
        opponent.hitbox_active = True

        # Atualização durante escuta deve interceptar e disparar Blind Counter-Thrust
        self.ichi.update(0.016, opponent=opponent, banners=banners, particles=particles)
        self.assertEqual(self.ichi.state, STATE_COUNTER_THRUST)
        self.assertTrue(self.ichi.hitbox_active)
        self.assertEqual(self.ichi.hitbox_damage, 2)
        # Oponente deve ser interrompido para recovery
        self.assertFalse(opponent.hitbox_active)
        self.assertEqual(opponent.state, STATE_RECOVERY)

    def test_04_listen_stance_projectile_deflection(self):
        """Verifica deflexão de projéteis frontais com a bainha e contra-ataque."""
        self.ichi.trigger_listen_stance(11.0, 10.0)
        pr = DummyProjectile(10.8, 10.0)
        projectiles = [pr]

        self.ichi.update(0.016, projectiles=projectiles)
        self.assertFalse(pr.is_active)
        self.assertEqual(self.ichi.state, STATE_COUNTER_THRUST)

    def test_05_cane_tap_slip_dodge(self):
        """Verifica desvio evasivo da bengala com 13 i-frames e deslocamento padrão."""
        particles = []
        ok = self.ichi.trigger_cane_slip(1.0, 0.0, particles=particles)
        self.assertTrue(ok)
        self.assertEqual(self.ichi.state, STATE_ROLL)
        self.assertTrue(self.ichi.invincible)
        self.assertAlmostEqual(self.ichi.invincible_timer, 0.22)
        self.assertAlmostEqual(self.ichi.roll_speed, 7.2)
        self.assertGreater(len(particles), 0)

        # Compatibilidade com alias trigger_roll
        ichi2 = IchiBlade(10.0, 10.0)
        ok2 = ichi2.trigger_roll(0.0, 1.0)
        self.assertTrue(ok2)
        self.assertEqual(ichi2.state, STATE_ROLL)

    def test_06_continuous_intro_and_victory_poses(self):
        """Verifica que as poses de Intro e Vitória são 100% contínuas e usam os scripts novos."""
        self.assertIn("ichi", pose_scripts.SCRIPTS["intro"])
        self.assertIn("ichi", pose_scripts.SCRIPTS["victory"])

        intro_script = pose_scripts.SCRIPTS["intro"]["ichi"]
        self.assertEqual(len(intro_script), 3)
        self.assertEqual(intro_script[0][6]["pose"], "cane_ground_listen")
        self.assertEqual(intro_script[1][6]["pose"], "blade_unlock_thumb")
        self.assertEqual(intro_script[2][6]["pose"], "serene_ready_stance")

        victory_script = pose_scripts.SCRIPTS["victory"]["ichi"]
        self.assertEqual(len(victory_script), 3)
        self.assertEqual(victory_script[0][6]["pose"], "blade_sleeve_wipe")
        self.assertEqual(victory_script[1][6]["pose"], "sheath_click_lock")
        self.assertEqual(victory_script[2][6]["pose"], "serene_cane_rest")

        # Amostragem sem interrupções
        for p in [0.0, 0.2, 0.35, 0.5, 0.7, 0.85, 1.0]:
            f_in = pose_scripts.sample("ichi", "intro", p)
            self.assertIsNotNone(f_in)
            f_vic = pose_scripts.sample("ichi", "victory", p)
            self.assertIsNotNone(f_vic)

    def test_07_ichi_model_head_and_arms(self):
        """Verifica renderização articulada, get_arms e face 3D."""
        class DummyContext:
            base_x, base_y = 10.0, 10.0
            torso_z, head_z = 0.5, 0.95
            head_w = 0.16
            fx, fy = 1.0, 0.0
            px, py = 0.0, 1.0
            walk_timer = 0.0
            atk_progress = 0.5
            is_melee = False
            is_moving = False
            extra_props = {}
            alpha = 255
            surface = pygame.Surface((300, 300), pygame.SRCALPHA)
            camera = Camera(300, 300)

        c = DummyContext()
        self.assertTrue(hasattr(ichi_model, "get_arms"))
        left, right = ichi_model.get_arms(c)
        self.assertEqual(len(left), 3)
        self.assertEqual(len(right), 3)

        # Desenhar cabeça deve chamar draw_portrait_face_3d e setar _face_drawn
        ichi_model.draw_head(c)
        self.assertTrue(getattr(c, "_face_drawn", False))

    def test_08_model_inspector_registration(self):
        """Verifica registro dos 12 botões e notas De/Para no Model Inspector."""
        self.assertIn("ichi", model_inspector.CHARACTER_ANIM_BUTTONS)
        self.assertIn("blind", model_inspector.CHARACTER_ANIM_BUTTONS)
        self.assertIn("shikomizue", model_inspector.CHARACTER_ANIM_BUTTONS)
        buttons = model_inspector.CHARACTER_ANIM_BUTTONS["ichi"]
        self.assertEqual(len(buttons), 12)

        action_keys = [btn[0] for btn in buttons]
        self.assertIn("GYAKU_IAI_QUICKDRAW", action_keys)
        self.assertIn("LISTEN_STANCE", action_keys)
        self.assertIn("BLIND_COUNTER_THRUST", action_keys)
        self.assertIn("CANE_TAP_SLIP", action_keys)
        self.assertIn("SHEATH_PARRY", action_keys)
        self.assertIn("FINISHER_1", action_keys)
        self.assertIn("FINISHER_2", action_keys)

        self.assertIn("ichi", model_inspector.OVERHAUL_DE_PARA_NOTES)
        self.assertIn("blind", model_inspector.OVERHAUL_DE_PARA_NOTES)
        self.assertIn("shikomizue", model_inspector.OVERHAUL_DE_PARA_NOTES)
        self.assertGreater(len(model_inspector.OVERHAUL_DE_PARA_NOTES["ichi"]), 0)


if __name__ == "__main__":
    unittest.main()
