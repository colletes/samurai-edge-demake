"""
Test Suite: Ren (Shaolin Monk) Complete Overhaul Verification (Sub-phase 2.13)
Validates PBR materials, get_arms modular kinematics, 3-step martial combo with buffering,
dodge somersault with offensive cancel, 360° Kiai projectile reflection and knockback,
fatalities (Hyakuretsu Ken & Kiai Shougeki), continuous Intro/Victory pose scripts,
and Model Inspector / Help Manual synchronization.
"""
import os
import sys
import math
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()


class TestRenOverhaul(unittest.TestCase):

    def test_ren_face_mesh_and_jieba(self):
        """Verifica a estilização facial anime marcial e marcas sagradas Jieba de Ren."""
        from src.isometric.mesh_primitives import PORTRAIT_FACE_STYLES
        self.assertIn("ren", PORTRAIT_FACE_STYLES, "PORTRAIT_FACE_STYLES deve conter 'ren'")
        style = PORTRAIT_FACE_STYLES["ren"]
        self.assertFalse(style.get("lashes", False), "Monge marcial não deve ter cílios femininos alongados")
        self.assertFalse(style.get("delicate_nose", True), "Ren deve ter nariz masculino estruturado")
        self.assertIn("iris", style)
        self.assertIn("brow", style)
        self.assertIn("lip", style)
        self.assertGreater(style.get("brow_tilt", 0.0), 0.20, "Sobrancelhas devem ter inclinação marcial resoluta")

    def test_ren_materials_and_legacy(self):
        """Verifica materiais PBR/Legados em ren_model."""
        from src.entities import ren_model
        self.assertTrue(hasattr(ren_model, "MATERIALS"), "ren_model deve exportar MATERIALS")
        self.assertTrue(hasattr(ren_model, "LEGACY_MATERIALS"), "ren_model deve exportar LEGACY_MATERIALS")
        for k, v in ren_model.LEGACY_MATERIALS.items():
            self.assertEqual(v, "matte", f"Material legado de {k} deve ser matte")

    def test_ren_get_arms_and_all_poses(self):
        """Verifica se get_arms(c) exporta posições válidas para as 12 poses do monge."""
        from src.entities import ren_model
        self.assertTrue(hasattr(ren_model, "get_arms"), "ren_model deve exportar get_arms")

        class DummyContext:
            torso_z = 0.40
            base_x = 0.0
            base_y = 0.0
            fx = 1.0
            fy = 0.0
            px = 0.0
            py = 1.0
            state = "IDLE"
            extra_props = {}
            atk_progress = 0.0
            is_melee = False
            is_moving = False
            walk_timer = 0.0

        c = DummyContext()
        poses = [
            "combo_step_1_jab", "combo_step_2_palm", "combo_step_3_dragon_kick",
            "shaolin_roll", "kiai_roar", "iron_palm_parry",
            "shaolin_salute", "shaolin_opening_flurry", "three_dragons_stance",
            "dragon_kick_landing", "shaolin_bow", "finisher_hyakuretsu", "finisher_kiai"
        ]
        for p in poses:
            c.extra_props = {"pose": p, "p": 0.5, "seg_u": 0.5, "combo_step": 2}
            left, right = ren_model.get_arms(c)
            self.assertEqual(len(left), 3, f"Braço esquerdo de {p} deve ter (x, y, z)")
            self.assertEqual(len(right), 3, f"Braço direito de {p} deve ter (x, y, z)")
            self.assertTrue(all(isinstance(v, (int, float)) for v in left + right), f"Valores de {p} devem ser numéricos")

    def test_ren_combo_buffering_and_kinetic_lunge(self):
        """Verifica a execução do combo marcial de 3 passos com dano progressivo e buffering."""
        from src.entities.ren_monk import RenMonk

        ren = RenMonk(5.0, 5.0)
        self.assertEqual(ren.speed, 5.4, "Ren deve possuir velocidade máxima de 5.4")

        # Passo 1: Jab
        self.assertTrue(ren.trigger_punch_combo(6.0, 5.0))
        self.assertEqual(ren.combo_step, 1)
        self.assertEqual(ren.hitbox_damage, 1)
        self.assertEqual(ren.hitbox_radius, 1.30)

        # Buffering do próximo passo durante o ataque atual
        ren.trigger_punch_combo(6.0, 5.0)
        self.assertTrue(ren.combo_buffered)
        self.assertEqual(ren.combo_target_step, 2)

        # Passo 2 direto
        ren._start_combo_step(2)
        self.assertEqual(ren.combo_step, 2)
        self.assertEqual(ren.hitbox_damage, 1)
        self.assertEqual(ren.hitbox_radius, 1.45)

        # Passo 3: Chute Alto com Chi (Letal 2 HP)
        ren._start_combo_step(3)
        self.assertEqual(ren.combo_step, 3)
        self.assertEqual(ren.hitbox_damage, 2)
        self.assertEqual(ren.hitbox_radius, 1.65)

    def test_ren_dodge_roll_and_offensive_cancel(self):
        """Verifica o salto acrobático e o cancelamento ofensivo para o combo nos últimos 40%."""
        from src.entities.ren_monk import RenMonk
        from src.entities.samurai import STATE_ROLL, STATE_ATTACK

        ren = RenMonk(5.0, 5.0)

        # Inicia roll
        self.assertTrue(ren.trigger_roll(1.0, 0.0))
        self.assertEqual(ren.state, STATE_ROLL)

        # Tentativa de cancelamento no início do roll (state_timer alto) deve falhar
        ren.state_timer = 0.18
        self.assertFalse(ren.trigger_punch_combo(6.0, 5.0))
        self.assertEqual(ren.state, STATE_ROLL)

        # Cancelamento nos últimos 40% (state_timer <= 0.08s) deve converter para ataque
        ren.state_timer = 0.06
        self.assertTrue(ren.trigger_punch_combo(6.0, 5.0))
        self.assertEqual(ren.state, STATE_ATTACK)
        self.assertEqual(ren.combo_step, 1)

    def test_ren_kiai_360_projectile_reflection(self):
        """Verifica a reflexão balística de projéteis em 360° com a barreira de Kiai."""
        from src.entities.ren_monk import RenMonk

        ren = RenMonk(5.0, 5.0)

        class DummyProjectile:
            def __init__(self):
                self.wx = 5.8
                self.wy = 5.0
                self.vx = -12.0
                self.vy = 0.0
                self.active = True
                self.owner = "enemy"

        proj = DummyProjectile()
        self.assertTrue(ren.trigger_kiai_shout(projectiles=[proj]))
        self.assertTrue(ren.kiai_aura_active)
        self.assertEqual(proj.owner, ren, "Projétil refletido pelo Kiai deve pertencer a Ren")
        self.assertGreater(proj.vx, 0.0, "Velocidade deve ser invertida e refletida para fora")

    def test_ren_kiai_opponent_knockback_and_stun(self):
        """Verifica alto knockback e soft stun aplicados ao oponente no raio do Kiai."""
        from src.entities.ren_monk import RenMonk

        ren = RenMonk(5.0, 5.0)

        class DummyOpponent:
            def __init__(self):
                self.wx = 6.0
                self.wy = 5.0
                self.is_alive = True
                self.stun_timer = 0.0
            def stun(self, dur):
                self.stun_timer = dur

        opp = DummyOpponent()
        ren.trigger_kiai_shout(opponent=opp)
        self.assertGreater(opp.wx, 6.0, "Oponente deve sofrer deslocamento forçado para trás")
        self.assertEqual(opp.stun_timer, 0.40, "Oponente deve sofrer soft stun de 0.40s")

    def test_ren_fatalities_corpse_creation(self):
        """Verifica a criação anatômica das duas fatalidades de Ren em VoxelCorpse."""
        from src.entities.voxel_corpse import VoxelCorpse

        class DummyVictim:
            wx = 4.0
            wy = 4.0
            wz = 0.0
            facing_x = -1.0
            facing_y = 0.0
            char_type = "kenshin"
            state = "IDLE"
            is_alive = False

        victim = DummyVictim()

        # Finisher A: HYAKURETSU_BODY_EXPLOSION
        corpse_hyaku = VoxelCorpse(victim, death_style="HYAKURETSU_BODY_EXPLOSION")
        piece_types = [p.piece_type for p in corpse_hyaku.pieces]
        self.assertIn("head", piece_types)
        self.assertIn("shattered_torso", piece_types)
        self.assertGreaterEqual(len(corpse_hyaku.pieces), 3)

        # Finisher B: WALL_SMASH_FATAL
        corpse_smash = VoxelCorpse(victim, death_style="WALL_SMASH_FATAL")
        piece_types_smash = [p.piece_type for p in corpse_smash.pieces]
        self.assertIn("shattered_torso", piece_types_smash)
        self.assertIn("shattered_legs", piece_types_smash)

    def test_ren_cinematic_director_phrases(self):
        """Verifica frases Sumi-E e gatilhos de closeup de Ren no CinematicDirector."""
        from src.effects.cinematic_director import CinematicDirector
        from src.i18n import set_lang

        set_lang("pt")
        director = CinematicDirector()
        # Frases em PT
        director._build_kanji_overlay(death_style="HYAKURETSU_BODY_EXPLOSION")
        self.assertEqual(director.current_kanji_text, "百烈拳")
        self.assertIn("HYAKURETSU KEN", director.current_kanji_subtitle)

        director._build_kanji_overlay(death_style="WALL_SMASH_FATAL")
        self.assertEqual(director.current_kanji_text, "気合衝撃")
        self.assertIn("KIAI SHOUGEKI", director.current_kanji_subtitle)

    def test_ren_intro_and_victory_pose_scripts_continuity(self):
        """Verifica continuidade contínua sem freeze na Intro e Vitória de Ren."""
        from src.entities import pose_scripts

        # Amostragem da Intro em 20 pontos de 0.0 a 1.0
        for i in range(21):
            p = i / 20.0
            frame = pose_scripts.sample("ren", "intro", p)
            self.assertIsNotNone(frame.state)
            self.assertIn("pose", frame.extra)
            timer = pose_scripts.state_timer_for("ren", frame)
            self.assertGreaterEqual(timer, 0.0)

        # Amostragem da Vitória em 20 pontos de 0.0 a 1.0
        for i in range(21):
            p = i / 20.0
            frame = pose_scripts.sample("ren", "victory", p)
            self.assertIsNotNone(frame.state)
            self.assertIn("pose", frame.extra)
            timer = pose_scripts.state_timer_for("ren", frame)
            self.assertGreaterEqual(timer, 0.0)

    def test_ren_model_inspector_registration(self):
        """Verifica se Ren está registrado com 12 botões interativos e modo De/Para."""
        from tools.model_inspector import (
            CHARACTER_ANIM_BUTTONS,
            OVERHAUL_DE_PARA_NOTES,
            ModelInspector
        )

        self.assertIn("ren", CHARACTER_ANIM_BUTTONS, "CHARACTER_ANIM_BUTTONS deve conter 'ren'")
        self.assertIn("shaolin", CHARACTER_ANIM_BUTTONS, "Alias 'shaolin' deve existir em CHARACTER_ANIM_BUTTONS")
        self.assertEqual(len(CHARACTER_ANIM_BUTTONS["ren"]), 12, "Ren deve ter exatamente 12 ações interativas")

        self.assertIn("ren", OVERHAUL_DE_PARA_NOTES, "OVERHAUL_DE_PARA_NOTES deve conter 'ren'")
        self.assertIn("shaolin", OVERHAUL_DE_PARA_NOTES, "Alias 'shaolin' deve existir em OVERHAUL_DE_PARA_NOTES")

        inspector = ModelInspector(headless=True)
        inspector.current_char_idx = inspector.char_keys.index("ren")

        for act_id, _lbl, _dur in CHARACTER_ANIM_BUTTONS["ren"]:
            inspector.trigger_action(act_id)
            for prog in (0.0, 0.5, 1.0):
                inspector.action_timer = prog * max(0.1, inspector.action_duration)
                wx, wy, wz, state, timer, is_mov, wtimer, extra = inspector._eval_action_frame("ren", is_legacy=False)
                self.assertIsNotNone(state)
                self.assertIn("pose_lerp_tracker", extra)

                # Modo legado
                wx_l, wy_l, wz_l, state_l, timer_l, is_mov_l, wtimer_l, extra_l = inspector._eval_action_frame("ren", is_legacy=True)
                self.assertIsNotNone(state_l)
                self.assertTrue(extra_l.get("legacy_mode", False))

    def test_ren_game_help_card(self):
        """Verifica se a ficha técnica de Ren no manual de ajuda está completa em PT e EN."""
        from src.ui.game_help import FIGHTERS_GUIDE_DATA, CHAR_REN

        card = next((c for c in FIGHTERS_GUIDE_DATA if c.get("id") == CHAR_REN), None)
        self.assertIsNotNone(card, "Card de Ren (CHAR_REN) deve existir em FIGHTERS_GUIDE_DATA")

        # Português
        pt = card["pt"]
        self.assertEqual(pt["name"], "REN")
        self.assertIn("Combo Shaolin", pt["habilidades"])
        self.assertIn("Grito Místico Kiai", pt["habilidades"])
        self.assertIn("Salto Acrobático", pt["habilidades"])
        self.assertIn("Hyakuretsu Ken", pt["habilidades"])

        # Inglês
        en = card["en"]
        self.assertEqual(en["name"], "REN")
        self.assertIn("Shaolin Combo", en["habilidades"])
        self.assertIn("Kiai Shout", en["habilidades"])
        self.assertIn("Acrobatic Somersault", en["habilidades"])
        self.assertIn("Hyakuretsu Ken", en["habilidades"])


if __name__ == "__main__":
    unittest.main()
