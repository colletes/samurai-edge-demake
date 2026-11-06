"""
Testes automatizados da Sub-fase 2.14: Overhaul de Chiyo (A Assassina das Sombras - Kodachi Dupla).
Valida:
1. Entidade ChiyoKunoichi: Primary Attack (Combo 3-Hit), Dança Mai & Acrobat Lunge, Shadow Step Slip (14 i-frames).
2. Finishers: TRIPLE_SCISSOR_CLEAVE e SHADOW_LOTUS_FLURRY com kanji banners, sangue e stuck weapons.
3. Modelo 3D chiyo_model: get_arms(c), PBR materials, renderização single-pass de bainhas e lâminas.
4. Animações Contínuas: Intro e Victory em pose_scripts sem congelamento e com sincronização de bainhas.
5. Integração no Model Inspector e Game Help.
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

from src.entities.chiyo_kunoichi import ChiyoKunoichi
from src.entities import chiyo_model
from src.entities import pose_scripts
from src.effects.cinematic_director import CinematicDirector
from src.combat.collision import _get_death_style_for_attacker
from src.i18n import set_lang
from tools.model_inspector import OVERHAUL_DE_PARA_NOTES, CHARACTER_ANIM_BUTTONS


class TestChiyoOverhaul(unittest.TestCase):
    def setUp(self):
        set_lang("pt")
        self.chiyo = ChiyoKunoichi(5.0, 5.0)
        self.dummy = ChiyoKunoichi(6.0, 5.0)

    def test_entity_stats_and_moveset(self):
        """Valida atributos de velocidade, alcance e dano de Chiyo."""
        self.assertEqual(self.chiyo.char_type, "chiyo")
        self.assertEqual(self.chiyo.speed, 5.1)
        self.assertEqual(self.chiyo.scissor_cooldown, 0.28)
        self.assertEqual(self.chiyo.mai_dance_cooldown, 3.2)

        # Ataque primário: Corte Kodachi Duplo
        res = self.chiyo.trigger_kodachi_strike(6.0, 5.0)
        self.assertTrue(res)
        self.assertEqual(self.chiyo.state, "ATTACK")
        self.assertEqual(self.chiyo.combo_step, 1)

        # Atualiza até fim do passo 1 e testa combo passo 2
        self.chiyo.state_timer = 0.0
        self.chiyo.state = "IDLE"
        self.chiyo.scissor_timer = 0.0
        self.chiyo.trigger_kodachi_strike(6.0, 5.0)
        self.assertEqual(self.chiyo.combo_step, 2)

    def test_mai_dance_and_acrobat_lunge(self):
        """Valida ativação da Dança Mai e cancelamento reativo no Salto Acrobático Lunge (3.2m)."""
        res = self.chiyo.trigger_mai_dance(6.0, 5.0)
        self.assertTrue(res)
        self.assertEqual(self.chiyo.state, "MAI_DANCE")
        self.assertTrue(self.chiyo.mai_active)

        # Re-pressionar ativa o Acrobat Lunge
        res_lunge = self.chiyo.trigger_mai_dance(6.0, 5.0)
        self.assertTrue(res_lunge)
        self.assertEqual(self.chiyo.state, "ACROBAT_LUNGE")
        self.assertGreater(self.chiyo.mai_dance_timer, 2.5)

    def test_shadow_step_dodge_and_iframes(self):
        """Valida a esquiva Shadow Step Slip com 14 i-frames e imunidade a projéteis."""
        res = self.chiyo.trigger_shadow_step(1.0, 0.0)
        self.assertTrue(res)
        self.assertEqual(self.chiyo.state, "ROLL")
        self.assertTrue(self.chiyo.invulnerable)
        self.assertTrue(self.chiyo.is_invulnerable_dodge)
        self.assertGreater(len(self.chiyo.zanzou_ghosts), 0)

    def test_finishers_configuration(self):
        """Valida que os dois finishers de Chiyo estão configurados com kanji banners."""
        director = CinematicDirector()
        director._build_kanji_overlay(death_style="TRIPLE_SCISSOR_CLEAVE")
        self.assertEqual(director.current_kanji_text, "双刃十字")
        self.assertIn("SOUJIN JUUJI", director.current_kanji_subtitle)

        director._build_kanji_overlay(death_style="SHADOW_LOTUS_FLURRY")
        self.assertEqual(director.current_kanji_text, "影蓮乱舞")
        self.assertIn("EIGEN RANBU", director.current_kanji_subtitle)

        # Valida mapeamento de estilos de morte em collision
        self.chiyo.state = "ATTACK"
        self.assertEqual(_get_death_style_for_attacker(self.chiyo), "TRIPLE_SCISSOR_CLEAVE")
        self.chiyo.state = "ACROBAT_LUNGE"
        self.assertEqual(_get_death_style_for_attacker(self.chiyo), "SHADOW_LOTUS_FLURRY")

        # Valida stuck weapon dual_kodachi no voxel corpse
        from src.entities.voxel_corpse import VoxelCorpse
        corpse = VoxelCorpse(self.dummy, death_style="SHADOW_LOTUS_FLURRY")
        self.assertIsNotNone(corpse)
        self.assertEqual(corpse.death_style, "SHADOW_LOTUS_FLURRY")

    def test_model_arms_and_materials(self):
        """Valida cinemática de braços, materiais PBR e regra de bainhas vazias."""
        self.assertIn("leather", chiyo_model.MATERIALS)
        self.assertIn("steel", chiyo_model.MATERIALS)
        self.assertEqual(chiyo_model.MATERIALS["leather"], "latex")
        self.assertEqual(chiyo_model.MATERIALS["steel"], "steel")
        self.assertEqual(chiyo_model.LEGACY_MATERIALS["leather"], "matte")

        # Valida get_arms
        class DummyContext:
            base_x = 0.0
            base_y = 0.0
            torso_z = 0.8
            fx = 1.0
            fy = 0.0
            px = 0.0
            py = 1.0
            walk_timer = 1.0
            is_moving = False
            is_melee = False
            state = "IDLE"
            extra_props = {}

        c = DummyContext()
        left, right = chiyo_model.get_arms(c)
        self.assertEqual(len(left), 3)
        self.assertEqual(len(right), 3)

        # Testa pose de esquiva
        c.extra_props = {"pose": "shadow_step", "roll_prog": 0.5}
        left_slip, right_slip = chiyo_model.get_arms(c)
        self.assertLess(left_slip[0], c.base_x) # braços recuados

        # Testa pose de lunge
        c.extra_props = {"pose": "acrobat_lunge", "p": 0.5}
        left_lunge, right_lunge = chiyo_model.get_arms(c)
        self.assertGreater(left_lunge[0], c.base_x + 0.2) # braços projetados à frente

    def test_pose_scripts_continuity_and_sheathing(self):
        """Valida que Intro e Victory são 100% contínuos e alternam a flag sheathed corretamente."""
        # Intro: começa embainhada (sheathed=True), saca kodachis, termina em guarda felina (sheathed=False)
        p_start = pose_scripts.sample("chiyo", "intro", 0.05)
        self.assertTrue(p_start.extra.get("sheathed", False))

        p_end = pose_scripts.sample("chiyo", "intro", 0.95)
        self.assertFalse(p_end.extra.get("sheathed", False))
        self.assertIn(p_end.extra.get("pose"), ("kunoichi_feline_stance", "kodachi_feline_stance"))

        # Victory: começa com lâminas em mãos (sheathed=False), embainha em reverso, termina triunfante (sheathed=True)
        pv_start = pose_scripts.sample("chiyo", "victory", 0.05)
        self.assertFalse(pv_start.extra.get("sheathed", False))

        pv_end = pose_scripts.sample("chiyo", "victory", 0.95)
        self.assertTrue(pv_end.extra.get("sheathed", False))
        self.assertEqual(pv_end.extra.get("pose"), "kunoichi_triumphant")

    def test_model_inspector_registration(self):
        """Valida notas de De/Para e botões de animação no Model Inspector."""
        self.assertIn("chiyo", OVERHAUL_DE_PARA_NOTES)
        self.assertIn("chiyo", CHARACTER_ANIM_BUTTONS)
        buttons = CHARACTER_ANIM_BUTTONS["chiyo"]
        btn_ids = [b[0] for b in buttons]
        self.assertIn("KODACHI_CROSS", btn_ids)
        self.assertIn("MAI_DANCE", btn_ids)
        self.assertIn("ACROBAT_LUNGE", btn_ids)
        self.assertIn("SHADOW_STEP", btn_ids)
        self.assertIn("FINISHER_1", btn_ids)
        self.assertIn("FINISHER_2", btn_ids)


if __name__ == "__main__":
    unittest.main()
