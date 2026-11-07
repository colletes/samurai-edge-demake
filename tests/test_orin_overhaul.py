"""
Testes de verificação e conformidade da Sub-fase 2.16:
Overhaul da O-Rin (A Menestrel de Yoshiwara — Tsugaru Shamisen Acústico & Lâminas de Vácuo Kamaitachi).
"""
import math
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame

# Inicialização headless do Pygame para testes
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from src.entities.orin import OrinMinstrel, KamaitachiProjectile
from src.entities import orin_model, pose_scripts
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric.camera import Camera
from src.ui.game_help import FIGHTERS_GUIDE_DATA
from tools.model_inspector import (
    OVERHAUL_DE_PARA_NOTES,
    CHARACTER_ANIM_BUTTONS,
    ModelInspector,
)


class DummyMockContext:
    """Mock leve de contexto do model_kit para testes de geometria e mãos."""
    def __init__(self, char_type="orin", state="IDLE", atk_progress=0.0, walk_timer=0.0, extra_props=None):
        self.char_type = char_type
        self.state = state
        self.atk_progress = atk_progress
        self.walk_timer = walk_timer
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_z = 0.0
        self.torso_z = 0.40
        self.head_z = 0.65
        self.pelvis_z = 0.32
        self.head_w = 0.18
        self.pelvis_w = 0.22
        self.fx = 1.0
        self.fy = 0.0
        self.px = 0.0
        self.py = 1.0
        self.alpha = 255
        self.is_melee = (state == "ATTACK")
        self.is_moving = (state == "WALK")
        self.extra_props = extra_props or {}
        self.camera = Camera(1280, 720)
        self.surface = pygame.Surface((300, 300), pygame.SRCALPHA)
        self.legs_data = {
            "L": {"thigh": (0, 0.08, 0.35), "shin": (0, 0.08, 0.18), "foot": (0, 0.08, 0.02)},
            "R": {"thigh": (0, -0.08, 0.35), "shin": (0, -0.08, 0.18), "foot": (0, -0.08, 0.02)},
        }


class DummyOpponent:
    """Mock de oponente para testar repulsão acústica da ressonância."""
    def __init__(self, wx=1.0, wy=0.0):
        self.wx = wx
        self.wy = wy
        self.is_alive = True
        self.state = "IDLE"
        self.stun_timer = 0.0
        self.knockback_vx = 0.0
        self.knockback_vy = 0.0
        self.knockback_timer = 0.0

    def stun(self, dur: float):
        self.stun_timer = dur

    def apply_forced_displacement(self, dx: float, dy: float, game_map=None):
        self.knockback_vx = dx
        self.knockback_vy = dy


class DummyProjectile:
    """Mock de projétil inimigo para testar deflexão da ressonância."""
    def __init__(self, wx=1.2, wy=0.0):
        self.wx = wx
        self.wy = wy
        self.owner = None
        self.is_active = True
        self.speed = 10.0
        self.dir_x = -1.0
        self.dir_y = 0.0


class TestOrinOverhaul(unittest.TestCase):
    """Bateria de testes de conformidade técnica e estética da O-Rin."""

    def test_01_palette_and_materials(self):
        """Valida paleta canônica, materiais PBR e materiais legados para comparação."""
        pal = orin_model.pal()
        self.assertIn("kimono", pal)
        self.assertIn("obi", pal)
        self.assertIn("eye_amber", pal)
        self.assertIn("tattoo_higan", pal)
        self.assertIn("shamisen_wood", pal)
        self.assertIn("silk_string", pal)

        # Materiais PBR
        self.assertEqual(orin_model.MATERIALS["kimono"], "silk")
        self.assertEqual(orin_model.MATERIALS["obi"], "silk")
        self.assertEqual(orin_model.MATERIALS["shamisen_wood"], "wood")

        # Modo Legado preservado
        self.assertTrue(hasattr(orin_model, "LEGACY_MATERIALS"))
        for k, mat in orin_model.LEGACY_MATERIALS.items():
            self.assertEqual(mat, "matte")

    def test_02_get_arms_interface_and_glide(self):
        """Valida interface get_arms(c) e pose do Deslize de Seda (Silk Sleeve Glide)."""
        c = DummyMockContext(extra_props={"pose": "silk_glide", "is_roll": True, "roll_prog": 0.5})
        left, right = orin_model.get_arms(c)
        self.assertIsInstance(left, tuple)
        self.assertIsInstance(right, tuple)
        self.assertEqual(len(left), 3)
        self.assertEqual(len(right), 3)

        # Braços devem estar em recuo aerodinâmico suave
        self.assertLess(right[0], c.base_x)

    def test_03_intro_and_victory_continuity(self):
        """Valida que todas as fases da intro e vitória são contínuas (C0 boundary matching e vivas)."""
        # Intro
        c_i1_end = DummyMockContext(extra_props={"pose": "shamisen_tuning_pluck", "seg_u": 1.0})
        l1, r1 = orin_model.get_arms(c_i1_end)

        c_i2_start = DummyMockContext(extra_props={"pose": "furisode_flourish", "seg_u": 0.0})
        l2_s, r2_s = orin_model.get_arms(c_i2_start)
        self.assertAlmostEqual(l1[0], l2_s[0], delta=0.01)
        self.assertAlmostEqual(l1[2], l2_s[2], delta=0.01)

        c_i2_end = DummyMockContext(extra_props={"pose": "furisode_flourish", "seg_u": 1.0})
        l2_e, r2_e = orin_model.get_arms(c_i2_end)

        c_i3_start = DummyMockContext(extra_props={"pose": "courtesan_stance", "seg_u": 0.0})
        l3_s, r3_s = orin_model.get_arms(c_i3_start)
        self.assertAlmostEqual(l2_e[0], l3_s[0], delta=0.01)
        self.assertAlmostEqual(l2_e[2], l3_s[2], delta=0.01)

        # Victory
        c_v1_end = DummyMockContext(extra_props={"pose": "triumphant_chord", "seg_u": 1.0})
        vl1, vr1 = orin_model.get_arms(c_v1_end)

        c_v2_start = DummyMockContext(extra_props={"pose": "turning_retune", "seg_u": 0.0})
        vl2_s, vr2_s = orin_model.get_arms(c_v2_start)
        self.assertAlmostEqual(vl1[0], vl2_s[0], delta=0.01)

        c_v2_end = DummyMockContext(extra_props={"pose": "turning_retune", "seg_u": 1.0})
        vl2_e, vr2_e = orin_model.get_arms(c_v2_end)

        c_v3_start = DummyMockContext(extra_props={"pose": "orin_backward_glance", "seg_u": 0.0})
        vl3_s, vr3_s = orin_model.get_arms(c_v3_start)
        self.assertAlmostEqual(vl2_e[0], vl3_s[0], delta=0.01)

    def test_04_primary_attack_two_step_combo(self):
        """Valida que o ataque primário dispara o combo rítmico em 2 etapas."""
        orin = OrinMinstrel(0.0, 0.0)
        projectiles = []

        # Estado inicial
        self.assertEqual(orin.combo_step, 0)

        # Etapa 1: 1 lâmina sônica linear 5.5m
        success1 = orin.trigger_attack(projectiles=projectiles)
        self.assertTrue(success1)
        self.assertEqual(orin.combo_step, 1)
        self.assertEqual(len(projectiles), 1)
        p1 = projectiles[0]
        self.assertEqual(p1.speed, 21.0)
        self.assertAlmostEqual(p1.max_range, 5.5, delta=0.1)

        # Simula recuperação do primeiro golpe e ativa janela do combo
        orin.state = "RECOVERY"
        orin.combo_window_timer = 0.40

        # Etapa 2: 2 lâminas em V cruzadas (±0.14 rad) com micro-avanço
        initial_wx = orin.wx
        success2 = orin.trigger_attack(projectiles=projectiles)
        self.assertTrue(success2)
        self.assertEqual(orin.combo_step, 2)
        self.assertEqual(len(projectiles), 3)  # 1 anterior + 2 novas
        self.assertGreater(orin.wx, initial_wx)  # micro-passo executado

    def test_05_secondary_resonance_chord_repulsion(self):
        """Valida que a Ressonância 360° repele oponentes, deflete projéteis e lança 3 ondas."""
        orin = OrinMinstrel(0.0, 0.0)
        opp = DummyOpponent(wx=1.2, wy=0.0)
        proj = DummyProjectile(wx=1.5, wy=0.0)
        proj.owner = opp
        projectiles = [proj]

        success = orin.trigger_deadly_resonance_chord(opponent=opp, projectiles=projectiles)
        self.assertTrue(success)

        # Projétil inimigo no raio de 2.0m deve ser dissipado pela onda de choque
        self.assertFalse(proj.is_active)

        # Oponente deve sofrer deslocamento forçado e stun
        self.assertGreater(opp.knockback_vx, 0.0)
        self.assertAlmostEqual(opp.stun_timer, 0.35, delta=0.05)

        # Deve ter gerado 3 projéteis acústicos em espiral (120°)
        self.assertEqual(len(projectiles), 4)

    def test_06_silk_sleeve_glide_dodge(self):
        """Valida que o Deslize de Seda concede 13 i-frames e imunidade a projéteis."""
        orin = OrinMinstrel(0.0, 0.0)
        success = orin.trigger_silk_glide(1.0, 0.0)
        self.assertTrue(success)
        self.assertEqual(orin.state, "ROLL")
        self.assertAlmostEqual(orin.invincible_timer, 13.0 / 60.0, delta=0.01)
        self.assertTrue(getattr(orin, "is_projectile_invincible", False))

    def test_07_model_inspector_and_help_integration(self):
        """Valida integração no Model Inspector (12 botões, notas De/Para) e Game Help."""
        # Notas De/Para
        self.assertIn("orin", OVERHAUL_DE_PARA_NOTES)
        self.assertIn("minstrel", OVERHAUL_DE_PARA_NOTES)
        notes = OVERHAUL_DE_PARA_NOTES["orin"]
        self.assertTrue(any("SSAA 2x" in n for n in notes))
        self.assertTrue(any("Kamaitachi" in n for n in notes))

        # Botões de animação
        self.assertIn("orin", CHARACTER_ANIM_BUTTONS)
        self.assertIn("minstrel", CHARACTER_ANIM_BUTTONS)
        buttons = CHARACTER_ANIM_BUTTONS["orin"]
        self.assertEqual(len(buttons), 12)
        btn_ids = [b[0] for b in buttons]
        self.assertIn("SONIC_CLEAVE_1", btn_ids)
        self.assertIn("SONIC_CLEAVE_2", btn_ids)
        self.assertIn("RESONANCE_360", btn_ids)
        self.assertIn("SILK_GLIDE", btn_ids)
        self.assertIn("FINISHER_1", btn_ids)
        self.assertIn("FINISHER_2", btn_ids)

        # Game Help
        orin_help = next((entry for entry in FIGHTERS_GUIDE_DATA if entry.get("char_type") == "orin"), None)
        self.assertIsNotNone(orin_help)
        self.assertIn("Kamaitachi", orin_help["pt"]["dano"])
        self.assertIn("Kamaitachi", orin_help["en"]["dano"])

    def test_08_ssaa_and_hd_rendering_without_crashes(self):
        """Valida renderização completa com SSAA 2x e face HD 3D sem exceções."""
        surf = pygame.Surface((300, 300), pygame.SRCALPHA)
        camera = Camera(1280, 720)

        # Renderização Nova (SSAA + HD)
        render_voxel_humanoid(
            surf, camera,
            wx=0.0, wy=0.0, wz=0.0,
            facing_x=1.0, facing_y=0.0,
            state="IDLE",
            state_timer=0.0,
            is_alive=True,
            char_type="orin",
            walk_timer=0.25,
            extra_props={"ssaa_2x": True, "legacy_mode": False}
        )

        # Renderização Legada (Pedestal Esquerdo De/Para)
        render_voxel_humanoid(
            surf, camera,
            wx=0.0, wy=0.0, wz=0.0,
            facing_x=1.0, facing_y=0.0,
            state="IDLE",
            state_timer=0.0,
            is_alive=True,
            char_type="orin",
            walk_timer=0.25,
            extra_props={"ssaa_2x": False, "legacy_mode": True}
        )


if __name__ == "__main__":
    unittest.main()
