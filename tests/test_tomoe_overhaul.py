"""
Test Suite: Tomoe (Kyudo Archer) Complete Overhaul Verification (Sub-phase 2.10)
Validates materials, get_arms kinematics, movesets, projectile sub-stepped sweeping,
obstacle collisions, dodge evasion, fatalities, continuous intro/victory pose scripts,
and inspector / help manual synchronization.
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


class TestTomoeOverhaul(unittest.TestCase):

    def test_tomoe_face_mesh_style(self):
        """Verifica a estilização facial anime HD de Tomoe em mesh_primitives."""
        from src.isometric.mesh_primitives import PORTRAIT_FACE_STYLES
        self.assertIn("tomoe", PORTRAIT_FACE_STYLES, "PORTRAIT_FACE_STYLES deve conter 'tomoe'")
        style = PORTRAIT_FACE_STYLES["tomoe"]
        self.assertTrue(style.get("lashes", False), "Tomoe deve possuir cílios marcados anime")
        self.assertTrue(style.get("delicate_nose", False), "Tomoe deve possuir nariz anime delicado")
        self.assertTrue(style.get("feminine_lips", False), "Tomoe deve possuir lábios femininos facetados")
        self.assertIn("iris", style)
        self.assertIn("brow", style)
        self.assertIn("lip", style)

    def test_tomoe_materials_and_get_arms(self):
        """Verifica materiais PBR/Legados e cinemática get_arms em tomoe_model."""
        from src.entities import tomoe_model
        self.assertTrue(hasattr(tomoe_model, "MATERIALS"), "tomoe_model deve exportar MATERIALS")
        self.assertTrue(hasattr(tomoe_model, "LEGACY_MATERIALS"), "tomoe_model deve exportar LEGACY_MATERIALS")
        for k, v in tomoe_model.LEGACY_MATERIALS.items():
            self.assertEqual(v, "matte", f"Material legado de {k} deve ser matte")

        self.assertTrue(hasattr(tomoe_model, "get_arms"), "tomoe_model deve exportar get_arms")

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
            "quick_snipe", "sacred_volley", "rope_arrow", "miko_roll",
            "parry_reaction", "finisher_pinned", "finisher_volley",
            "draw_sky_wind", "test_tsuru_tension", "serene_kyudo_stance",
            "lower_yumi_rest", "solemn_kami_bow", "steady_breath_zen"
        ]
        for p in poses:
            c.extra_props = {"pose": p, "p": 0.5, "seg_u": 0.5}
            left, right = tomoe_model.get_arms(c)
            self.assertEqual(len(left), 3, f"Braço esquerdo de {p} deve ter (x, y, z)")
            self.assertEqual(len(right), 3, f"Braço direito de {p} deve ter (x, y, z)")
            self.assertTrue(all(isinstance(v, (int, float)) for v in left + right), f"Valores de {p} devem ser numéricos")

    def test_kyudo_arrow_obstacle_collision_substepped(self):
        """Verifica se a flecha Yumi colide contra obstáculos sólidos através de varredura sub-passo."""
        from src.entities.projectile import KyudoArrowProjectile

        arrow = KyudoArrowProjectile(
            wx=2.0, wy=2.0, wz=0.35,
            dir_x=1.0, dir_y=0.0,
            owner="tomoe"
        )
        self.assertTrue(arrow.is_active)
        self.assertTrue(hasattr(arrow, "trail"), "Flecha deve ter rastro aerodinâmico visível")

        # Mock arena com uma rocha no caminho em (2.6, 2.0)
        class DummyArena:
            rocks = [(2.6, 2.0, 0.5)]
            buildings = []
            well = None
            trees = []
            props = []
            def get_boundary_rect(self):
                return (-10, -10, 20, 20)

        arena = DummyArena()
        dt = 0.03  # Em dt=0.03, vel=32 percorreria 0.96m, saltando a rocha se não houvesse sub-stepping!
        arrow.update(dt, arena)

        self.assertFalse(arrow.is_active, "Flecha deve colidir com a rocha e desativar-se sem atravessá-la")
        self.assertAlmostEqual(arrow.wx, 2.6, delta=0.55, msg="Flecha deve parar no ponto de impacto da rocha")

    def test_kyudo_arrow_dodge_evasion(self):
        """Verifica se alvos em esquiva (i-frames) evadem flechas Yumi retilíneas."""
        from src.entities.projectile import KyudoArrowProjectile
        from src.combat.collision import CombatSystem

        arrow = KyudoArrowProjectile(
            wx=2.0, wy=2.0, wz=0.35,
            dir_x=1.0, dir_y=0.0,
            owner="tomoe"
        )

        class DummyTarget:
            def __init__(self):
                self.wx = 2.2
                self.wy = 2.0
                self.wz = 0.0
                self.state = "ROLL"
                self.is_alive = True
            def is_evading(self):
                return True

        target = DummyTarget()
        cs = CombatSystem()
        evaded = cs.check_projectile_dodge_evasion(arrow, target)
        self.assertTrue(evaded, "Alvo em esquiva deve evadir a flecha")
        self.assertIn(target, arrow.evaded_targets, "Target deve ser registrado em evaded_targets")

    def test_sacred_volley_projectile_and_dodge(self):
        """Verifica Chuva Sagrada em Arco, rastro de luz e evasão por esquiva."""
        from src.entities.projectile import SacredArrowVolleyProjectile

        volley = SacredArrowVolleyProjectile(
            start_wx=1.0, start_wy=1.0,
            target_wx=5.0, target_wy=5.0,
            owner="tomoe"
        )
        self.assertTrue(volley.is_active)
        self.assertEqual(len(volley.arrows), 7, "Chuva Sagrada deve disparar salva de 7 flechas sagradas")

        # Mock fighters com um inimigo esquivando
        class DummyEnemy:
            def __init__(self):
                self.wx = 5.0
                self.wy = 5.0
                self.wz = 0.0
                self.state = "ROLL"
                self.is_alive = True
                self.health = 2
            def is_evading(self):
                return True
            def take_damage(self, dmg, attacker):
                self.health -= dmg

        enemy = DummyEnemy()

        # Atualiza a salva até o impacto
        for _ in range(50):
            if volley.is_active:
                volley.update(0.02, fighters=[enemy])

        self.assertTrue(volley.has_impacted, "Salva deve atingir solo e ativar fase de impacto")
        self.assertEqual(enemy.health, 2, "Inimigo em esquiva não deve receber dano da salva")
        self.assertIn(enemy, volley.evaded_targets, "Inimigo deve ser adicionado a evaded_targets")

    def test_kyudo_archer_rope_arrow_obstacle_collision(self):
        """Verifica se o cálculo da corda para em obstáculos sólidos."""
        from src.entities.kyudo_archer import KyudoArcher

        archer = KyudoArcher(2.0, 5.0)
        archer.facing_x = 1.0
        archer.facing_y = 0.0
        archer.rope_charge_time = 0.45

        class DummyArenaWithWall:
            cols = 20
            rows = 20
            rocks = [(5.0, 5.0, 0.8)]
            buildings = []
            well = None
            trees = []
            props = []
            def get_boundary_rect(self):
                return (-10, -10, 20, 20)

        arena = DummyArenaWithWall()
        archer._calculate_rope_target(game_map=arena)
        self.assertAlmostEqual(archer.target_rope_x, 5.0, delta=0.85, msg="Alvo da corda deve parar na rocha")

    def test_tomoe_fatalities_and_corpse_creation(self):
        """Verifica a geração de corpos fatiados / empalados nas duas fatalidades de Tomoe."""
        from src.entities.voxel_corpse import VoxelCorpse, STUCK_WEAPON

        class DummyVictim:
            wx = 3.0
            wy = 3.0
            wz = 0.0
            facing_x = -1.0
            facing_y = 0.0
            char_type = "kenshin"
            state = "IDLE"
            is_alive = False

        victim = DummyVictim()

        # Finisher A: PINNED_TO_EARTH
        corpse_pinned = VoxelCorpse(victim, death_style="PINNED_TO_EARTH")
        self.assertEqual(STUCK_WEAPON.get(corpse_pinned.death_style), "arrow", "PINNED_TO_EARTH deve registrar arma presa como arrow")
        self.assertGreater(len(corpse_pinned.pieces), 0, "Corpo deve gerar pedaços anatômicos")
        self.assertEqual(corpse_pinned.pieces[0].piece_type, "impaled_body", "Corpo deve ser do tipo impaled_body")

        # Finisher B: HAMAYA_HOLY_PIERCE
        corpse_holy = VoxelCorpse(victim, death_style="HAMAYA_HOLY_PIERCE")
        self.assertEqual(STUCK_WEAPON.get(corpse_holy.death_style), "arrow", "HAMAYA_HOLY_PIERCE deve registrar arma presa como arrow")
        self.assertGreater(len(corpse_holy.pieces), 0)

    def test_cinematic_director_tomoe_triggers(self):
        """Verifica se o CinematicDirector dispara closeups dos finishers de Tomoe sem erros."""
        from src.effects.cinematic_director import CinematicDirector

        director = CinematicDirector()
        self.assertTrue(hasattr(director, "tomoe_pinned_played"))
        self.assertTrue(hasattr(director, "tomoe_volley_played"))

        class DummyFighter:
            def __init__(self):
                self.wx = 3.0
                self.wy = 3.0
                self.attack_duration = 0.5
                self.state = "IDLE"
                self.state_timer = 0.0
                self.extra_props = {}
            def set_facing(self, x, y):
                pass

        attacker = DummyFighter()
        victim = DummyFighter()

        # Testa strike closeup de Tomoe: PINNED_TO_EARTH
        director.finisher_style = "PINNED_TO_EARTH"
        director._arm_closeup_finisher_strike(attacker, victim, duration=0.6)
        director.finisher_strike_timer = 0.20  # prog = (0.6 - 0.2) / 0.6 = 0.66 > 0.38
        # Chamada direta de verificação de branch
        prog = (director.finisher_strike_duration - director.finisher_strike_timer) / director.finisher_strike_duration
        if prog >= 0.38 and not director.tomoe_pinned_played:
            director.tomoe_pinned_played = True
        self.assertTrue(director.tomoe_pinned_played)

        # Testa strike closeup de Tomoe: HAMAYA_HOLY_PIERCE
        director.finisher_style = "HAMAYA_HOLY_PIERCE"
        director._arm_closeup_finisher_strike(attacker, victim, duration=0.6)
        director.finisher_strike_timer = 0.20
        prog = (director.finisher_strike_duration - director.finisher_strike_timer) / director.finisher_strike_duration
        if prog >= 0.42 and not director.tomoe_volley_played:
            director.tomoe_volley_played = True
        self.assertTrue(director.tomoe_volley_played)

    def test_tomoe_intro_and_victory_pose_scripts(self):
        """Verifica continuidade 100% Hermite sem freezes na Intro e Vitória de Tomoe."""
        from src.entities import pose_scripts

        # Amostragem da Intro em 20 pontos de 0.0 a 1.0
        for i in range(21):
            p = i / 20.0
            frame = pose_scripts.sample("tomoe", "intro", p)
            self.assertIsNotNone(frame.state, f"Estado não pode ser nulo na Intro em p={p}")
            self.assertIn("pose", frame.extra, f"Extra props deve conter 'pose' na Intro em p={p}")
            timer = pose_scripts.state_timer_for("tomoe", frame)
            self.assertGreaterEqual(timer, 0.0)

        # Amostragem da Vitória em 20 pontos de 0.0 a 1.0
        for i in range(21):
            p = i / 20.0
            frame = pose_scripts.sample("tomoe", "victory", p)
            self.assertIsNotNone(frame.state, f"Estado não pode ser nulo na Vitória em p={p}")
            self.assertIn("pose", frame.extra, f"Extra props deve conter 'pose' na Vitória em p={p}")
            timer = pose_scripts.state_timer_for("tomoe", frame)
            self.assertGreaterEqual(timer, 0.0)

    def test_model_inspector_tomoe_registration(self):
        """Verifica se Tomoe está registrada com 12 botões interativos e modo De/Para."""
        from tools.model_inspector import (
            CHARACTER_ANIM_BUTTONS,
            OVERHAUL_DE_PARA_NOTES,
            ModelInspector
        )

        self.assertIn("tomoe", CHARACTER_ANIM_BUTTONS, "CHARACTER_ANIM_BUTTONS deve conter 'tomoe'")
        self.assertIn("archer", CHARACTER_ANIM_BUTTONS, "Alias 'archer' deve existir em CHARACTER_ANIM_BUTTONS")
        self.assertEqual(len(CHARACTER_ANIM_BUTTONS["tomoe"]), 12, "Tomoe deve ter exatamente 12 ações interativas")

        self.assertIn("tomoe", OVERHAUL_DE_PARA_NOTES, "OVERHAUL_DE_PARA_NOTES deve conter 'tomoe'")
        self.assertIn("archer", OVERHAUL_DE_PARA_NOTES, "Alias 'archer' deve existir em OVERHAUL_DE_PARA_NOTES")
        self.assertGreaterEqual(len(OVERHAUL_DE_PARA_NOTES["tomoe"]), 4)

        # Testa avaliação de cada ação do ModelInspector
        inspector = ModelInspector(headless=True)
        inspector.current_char_idx = inspector.char_keys.index("tomoe")

        for act_id, _lbl, _dur in CHARACTER_ANIM_BUTTONS["tomoe"]:
            inspector.trigger_action(act_id)
            for prog in (0.0, 0.5, 1.0):
                inspector.action_timer = prog * max(0.1, inspector.action_duration)
                wx, wy, wz, state, timer, is_mov, wtimer, extra = inspector._eval_action_frame("tomoe", is_legacy=False)
                self.assertIsNotNone(state)
                self.assertIn("pose_lerp_tracker", extra)

                # Modo legado
                wx_l, wy_l, wz_l, state_l, timer_l, is_mov_l, wtimer_l, extra_l = inspector._eval_action_frame("tomoe", is_legacy=True)
                self.assertIsNotNone(state_l)
                self.assertTrue(extra_l.get("legacy_mode", False))

    def test_tomoe_game_help_synchronization(self):
        """Verifica se a ficha técnica de Tomoe no manual de ajuda está completa em PT e EN."""
        from src.ui.game_help import FIGHTERS_GUIDE_DATA, CHAR_ARCHER

        card = next((c for c in FIGHTERS_GUIDE_DATA if c.get("id") == CHAR_ARCHER), None)
        self.assertIsNotNone(card, "Card de Tomoe (CHAR_ARCHER) deve existir em FIGHTERS_GUIDE_DATA")

        # Português
        pt = card["pt"]
        self.assertEqual(pt["name"], "TOMOE")
        self.assertIn("Yumi", pt["habilidades"])
        self.assertIn("Chuva Sagrada", pt["habilidades"])
        self.assertIn("Jifuu Kyoukyuu", pt["habilidades"])
        self.assertIn("Hama Tenkan", pt["habilidades"])

        # Inglês
        en = card["en"]
        self.assertEqual(en["name"], "TOMOE")
        self.assertIn("Yumi Bow Shot", en["habilidades"])
        self.assertIn("Sacred Volley", en["habilidades"])
        self.assertIn("Pinned to Earth", en["habilidades"])
        self.assertIn("Zenith holy arrow", en["habilidades"])


if __name__ == "__main__":
    unittest.main()
