"""
Testes de verificação e conformidade da Sub-fase 2.17:
Overhaul do Goro (O Fazendeiro Rebelde — Enxada Kuwa & Terremoto).
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

from src.entities.goro import GoroFarmer
from src.entities import goro_model, pose_scripts
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric.camera import Camera
from src.ui.game_help import FIGHTERS_GUIDE_DATA
from tools.model_inspector import (
    OVERHAUL_DE_PARA_NOTES,
    CHARACTER_ANIM_BUTTONS,
)


class DummyMockContext:
    """Mock leve de contexto do model_kit para testes de geometria e membros articulados."""
    def __init__(self, char_type="goro", state="IDLE", atk_progress=0.0, walk_timer=0.0, extra_props=None):
        self.char_type = char_type
        self.state = state
        self.atk_progress = atk_progress
        self.walk_timer = walk_timer
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_z = 0.0
        self.torso_z = 0.42
        self.head_z = 0.68
        self.pelvis_z = 0.33
        self.head_w = 0.19
        self.pelvis_w = 0.23
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
    """Mock de oponente para testar pisotão sísmico e pocket dirt."""
    def __init__(self, wx=1.0, wy=0.0):
        self.wx = wx
        self.wy = wy
        self.is_alive = True
        self.state = "IDLE"
        self.stun_timer = 0.0
        self.knockback_vx = 0.0
        self.knockback_vy = 0.0
        self.is_blinded = False

    def stun(self, dur: float):
        self.stun_timer = dur

    def apply_forced_displacement(self, dx: float, dy: float, game_map=None):
        self.knockback_vx = dx
        self.knockback_vy = dy


class TestGoroOverhaul(unittest.TestCase):
    """Bateria de testes de conformidade técnica e estética do Goro."""

    def test_01_palette_and_materials(self):
        """Valida paleta rústica, materiais PBR e materiais legados para comparação."""
        pal = goro_model.pal()
        self.assertIn("noragi", pal)
        self.assertIn("tenugui", pal)
        self.assertIn("rope_belt", pal)
        self.assertIn("iron_kuwa", pal)
        self.assertIn("wood_shaft", pal)

        # Materiais PBR
        self.assertEqual(goro_model.MATERIALS["noragi"], "canvas")
        self.assertEqual(goro_model.MATERIALS["iron_kuwa"], "metal")
        self.assertEqual(goro_model.MATERIALS["wood_shaft"], "wood")

        # Modo Legado preservado
        self.assertTrue(hasattr(goro_model, "LEGACY_MATERIALS"))
        for k, mat in goro_model.LEGACY_MATERIALS.items():
            self.assertEqual(mat, "matte")

    def test_02_get_arms_interface_and_mud_roll(self):
        """Valida interface get_arms(c), Rolamento de Lama e Pocket Dirt."""
        # Rolamento
        c_roll = DummyMockContext(extra_props={"pose": "mud_roll", "is_roll": True, "roll_prog": 0.5})
        left, right = goro_model.get_arms(c_roll)
        self.assertIsInstance(left, tuple)
        self.assertIsInstance(right, tuple)

        # Pocket Dirt (lançamento de terra)
        c_dirt = DummyMockContext(extra_props={"pose": "pocket_dirt", "is_pocket_dirt": True, "p": 0.5})
        dl, dr = goro_model.get_arms(c_dirt)
        self.assertGreater(dl[0], c_dirt.base_x)  # Mão esquerda arremessando à frente

    def test_03_intro_and_victory_continuity(self):
        """Valida que todas as fases da intro e vitória são 100% contínuas (C0 boundary matching e vivas)."""
        # Intro
        c_i1_end = DummyMockContext(extra_props={"pose": "kuwa_shoulder_carry", "seg_u": 1.0})
        l1, r1 = goro_model.get_arms(c_i1_end)

        c_i2_start = DummyMockContext(extra_props={"pose": "tenugui_tighten_plant", "seg_u": 0.0})
        l2_s, r2_s = goro_model.get_arms(c_i2_start)
        self.assertAlmostEqual(l1[0], l2_s[0], delta=0.01)
        self.assertAlmostEqual(l1[2], l2_s[2], delta=0.01)

        c_i2_end = DummyMockContext(extra_props={"pose": "tenugui_tighten_plant", "seg_u": 1.0})
        l2_e, r2_e = goro_model.get_arms(c_i2_end)

        c_i3_start = DummyMockContext(extra_props={"pose": "peasant_rebel_stance", "seg_u": 0.0})
        l3_s, r3_s = goro_model.get_arms(c_i3_start)
        self.assertAlmostEqual(l2_e[0], l3_s[0], delta=0.01)
        self.assertAlmostEqual(l2_e[2], l3_s[2], delta=0.01)

        # Victory
        c_v1_end = DummyMockContext(extra_props={"pose": "kuwa_earth_rest", "seg_u": 1.0})
        vl1, vr1 = goro_model.get_arms(c_v1_end)

        c_v2_start = DummyMockContext(extra_props={"pose": "sweat_wipe", "seg_u": 0.0})
        vl2_s, vr2_s = goro_model.get_arms(c_v2_start)
        self.assertAlmostEqual(vl1[0], vl2_s[0], delta=0.01)

        c_v2_end = DummyMockContext(extra_props={"pose": "sweat_wipe", "seg_u": 1.0})
        vl2_e, vr2_e = goro_model.get_arms(c_v2_end)

        c_v3_start = DummyMockContext(extra_props={"pose": "farmer_proud_laugh", "seg_u": 0.0})
        vl3_s, vr3_s = goro_model.get_arms(c_v3_start)
        self.assertAlmostEqual(vl2_e[0], vl3_s[0], delta=0.01)

    def test_04_kuwa_heavy_cleave_and_hyper_armor(self):
        """Valida que a descida da Kuwa possui alcance 2.40m, quebra de guarda e Hyper Armor."""
        goro = GoroFarmer(0.0, 0.0)
        self.assertEqual(goro.cleave_reach, 2.40)
        self.assertEqual(goro.cleave_duration, 0.22)

        # Disparo do cleave
        success = goro.trigger_kuwa_cleave(1.0, 0.0)
        self.assertTrue(success)
        self.assertEqual(goro.state, "ATTACK")
        self.assertTrue(goro.is_guard_break)

        # Teste de Hyper Armor durante ataque: golpe de 1 dano não interrompe se HP > 1
        goro.hp = 2
        took_dmg, killed = goro.take_hit((1.0, 0.0), damage=1)
        self.assertTrue(took_dmg)
        self.assertFalse(killed)
        self.assertEqual(goro.hp, 1)
        self.assertEqual(goro.state, "ATTACK")  # Não foi cancelado para STUNNED nem morto!

    def test_05_seismic_stomp_fissure(self):
        """Valida o Pisotão Sísmico causando stun (0.80s) e deslocamento forçado em oponente a até 4.2m."""
        goro = GoroFarmer(0.0, 0.0)
        opp = DummyOpponent(wx=2.5, wy=0.0)
        shockwaves = []

        success = goro.trigger_earth_stomp(1.0, 0.0, shockwaves=shockwaves, opponent=opp)
        self.assertTrue(success)
        self.assertEqual(goro.state, "EARTH_STOMP")
        self.assertEqual(len(shockwaves), 1)

        # Oponente deve sofrer stun de 0.80s e knockback
        self.assertAlmostEqual(opp.stun_timer, 0.80, delta=0.05)
        self.assertGreater(opp.knockback_vx, 0.0)

    def test_06_peasant_mud_roll_and_pocket_dirt(self):
        """Valida Rolamento de Lavrador (13 i-frames) e cancelamento com Pocket Dirt."""
        goro = GoroFarmer(0.0, 0.0)
        opp = DummyOpponent(wx=0.8, wy=0.0)

        # 1. Dispara rolamento
        success_roll = goro.trigger_mud_roll(1.0, 0.0)
        self.assertTrue(success_roll)
        self.assertEqual(goro.state, "ROLL")
        self.assertAlmostEqual(goro.invincible_timer, 13.0 / 60.0, delta=0.01)

        # 2. Cancela o rolamento em Pocket Dirt
        success_dirt = goro.trigger_pocket_dirt(opponent=opp)
        self.assertTrue(success_dirt)
        self.assertEqual(goro.state, "POCKET_DIRT")

        # Oponente adjacente deve ter sido atordoado (0.22s) e cegado
        self.assertAlmostEqual(opp.stun_timer, 0.22, delta=0.05)
        self.assertTrue(opp.is_blinded)

    def test_07_model_inspector_and_help_integration(self):
        """Valida registro no Model Inspector (12 botões, notas De/Para) e Game Help."""
        # Notas De/Para
        self.assertIn("goro", OVERHAUL_DE_PARA_NOTES)
        self.assertIn("farmer", OVERHAUL_DE_PARA_NOTES)
        notes = OVERHAUL_DE_PARA_NOTES["goro"]
        self.assertTrue(any("SSAA 2x" in n for n in notes))
        self.assertTrue(any("Pocket Dirt" in n for n in notes))

        # Botões de animação
        self.assertIn("goro", CHARACTER_ANIM_BUTTONS)
        self.assertIn("farmer", CHARACTER_ANIM_BUTTONS)
        buttons = CHARACTER_ANIM_BUTTONS["goro"]
        self.assertEqual(len(buttons), 12)
        btn_ids = [b[0] for b in buttons]
        self.assertIn("KUWA_HEAVY_CLEAVE", btn_ids)
        self.assertIn("EARTH_STOMP_ACTION", btn_ids)
        self.assertIn("MUD_ROLL", btn_ids)
        self.assertIn("POCKET_DIRT", btn_ids)
        self.assertIn("FINISHER_1", btn_ids)
        self.assertIn("FINISHER_2", btn_ids)

        # Game Help
        goro_help = next((entry for entry in FIGHTERS_GUIDE_DATA if entry.get("char_type") == "goro"), None)
        self.assertIsNotNone(goro_help)
        self.assertIn("Pocket Dirt", goro_help["pt"]["especial"])
        self.assertIn("Pocket Dirt", goro_help["en"]["especial"])

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
            char_type="goro",
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
            char_type="goro",
            walk_timer=0.25,
            extra_props={"ssaa_2x": False, "legacy_mode": True}
        )


if __name__ == "__main__":
    unittest.main()
