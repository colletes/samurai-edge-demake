"""
Automated Test Suite: Valerius Overhaul (Sub-fase 2.19)
Verifica as 8 diretivas do overhaul de Valerius:
1. Inicialização, Paleta e Materiais (SSAA 2x, Monóculo 3D, Chamas Azuis, LEGACY_MATERIALS).
2. Ataque Primário: Cursed Scythe Reap (Alcance 1.95m, Raio 1.35m, Dano 2 HP).
3. Tríade dos Mortos: Ciclo Ritual dos 3 Servos (Rastejante -> Soldado -> Wight).
4. Variante Rastejante de Tornozelos (Grasper): Perseguição a 3.4 m/s e imobilização de 1.4s.
5. Variantes Soldado (Swordsman - 1 dano) e Wight (Explosão de chamas azuis em área 1.6m).
6. Detonação Cadavérica Manual: Estalo de dedos [R] detonando o lacaio ativo em chamas azuis.
7. Névoa Espectral (Mist Dash com 13 i-frames) e Guarda de Foice (Scythe Guard).
8. Finisher 1 Soul Reap (Decapitação com cabeça normal e corpo transformado em esqueleto) e Integração no Model Inspector.
"""
import os
import sys
import unittest
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.entities.valerius import ValeriusNecromancer, ValeriusUndeadSummon
from src.entities.samurai import Samurai, STATE_IDLE, STATE_ATTACK, STATE_RECOVERY, STATE_ROLL, STATE_PARRY
from src.entities.voxel_corpse import VoxelCorpse
from src.entities import valerius_model
from src.isometric.camera import Camera


class TestValeriusOverhaul(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        pygame.init()
        pygame.display.set_mode((800, 600))

    def setUp(self):
        self.valerius = ValeriusNecromancer(5.0, 5.0)
        self.dummy = Samurai(6.0, 5.0, name="Dummy")
        self.camera = Camera(800, 600)
        self.surface = pygame.Surface((800, 600), pygame.SRCALPHA)

    def test_01_valerius_initialization_and_palette(self):
        """Verifica atributos básicos, materiais e paleta espectral."""
        self.assertEqual(self.valerius.name, "Valerius")
        self.assertEqual(self.valerius.char_type, "valerius")
        self.assertEqual(self.valerius.hp, 2)
        self.assertEqual(self.valerius.max_hp, 2)
        self.assertEqual(self.valerius.speed, 3.80)
        self.assertTrue(self.valerius.can_parry)
        self.assertEqual(self.valerius.finisher_style_primary, "SOUL_REAP")
        self.assertEqual(self.valerius.finisher_style_secondary, "DRAGGED_TO_GRAVE")

        # Verifica paleta e materiais em valerius_model
        self.assertIn("spectral_aura", valerius_model.PALETTE)
        self.assertIn("flame_blue", valerius_model.PALETTE)
        self.assertIn("monocle_gold", valerius_model.PALETTE)
        self.assertTrue(hasattr(valerius_model, "LEGACY_MATERIALS"))
        self.assertTrue(hasattr(valerius_model, "get_arms"))

    def test_02_scythe_reap_attack(self):
        """Verifica mecânicas e calibragem do ataque primário Cursed Scythe Reap."""
        success = self.valerius.trigger_scythe_reap(6.0, 5.0)
        self.assertTrue(success)
        self.assertEqual(self.valerius.state, STATE_ATTACK)
        self.assertEqual(self.valerius.hitbox_damage, 2)
        self.assertEqual(self.valerius.scythe_reach, 1.95)
        self.assertEqual(self.valerius.scythe_radius, 1.35)
        self.assertEqual(self.valerius.hitbox_radius, 1.35)
        self.assertEqual(self.valerius.scythe_duration, 0.25)
        self.assertEqual(self.valerius.scythe_recovery, 0.48)

    def test_03_triad_of_the_dead_cycle(self):
        """Verifica a rotação ritual dos 3 servos (Grasper -> Swordsman -> Wight -> Grasper)."""
        particles = []
        banners = []

        # 1. Primeiro servo: Grasper
        self.assertEqual(self.valerius.summon_cycle, 0)
        self.assertEqual(self.valerius.get_next_summon_name(), "Evocar Rastejante")
        self.valerius.trigger_summon_undead(6.0, 5.0, particles=particles, opponent=self.dummy, banners=banners)
        self.assertIsNotNone(self.valerius.summon)
        self.assertEqual(self.valerius.summon.kind, "grasper")
        self.assertEqual(self.valerius.summon.speed, 3.4)
        self.assertEqual(self.valerius.summon_cycle, 1)

        # Simula morte do servo e reset de timer para próximo teste
        self.valerius.summon.is_alive = False
        self.valerius.summon = None
        self.valerius.summon_timer = 0.0
        self.valerius.state = STATE_IDLE

        # 2. Segundo servo: Swordsman
        self.assertEqual(self.valerius.get_next_summon_name(), "Evocar Soldado")
        self.valerius.trigger_summon_undead(6.0, 5.0, particles=particles, opponent=self.dummy, banners=banners)
        self.assertIsNotNone(self.valerius.summon)
        self.assertEqual(self.valerius.summon.kind, "swordsman")
        self.assertEqual(self.valerius.summon.speed, 3.6)
        self.assertEqual(self.valerius.summon_cycle, 2)

        self.valerius.summon.is_alive = False
        self.valerius.summon = None
        self.valerius.summon_timer = 0.0
        self.valerius.state = STATE_IDLE

        # 3. Terceiro servo: Wight
        self.assertEqual(self.valerius.get_next_summon_name(), "Evocar Wight")
        self.valerius.trigger_summon_undead(6.0, 5.0, particles=particles, opponent=self.dummy, banners=banners)
        self.assertIsNotNone(self.valerius.summon)
        self.assertEqual(self.valerius.summon.kind, "wight")
        self.assertEqual(self.valerius.summon.speed, 4.4)
        self.assertEqual(self.valerius.summon_cycle, 0)  # Ciclo fechado de volta ao início

    def test_04_grasper_ankle_grab_and_immobilization(self):
        """Verifica a variante Rastejante de Tornozelos agarrando o rival com 1.4s de imobilização."""
        grasper = ValeriusUndeadSummon(self.valerius, 5.0, 5.0, kind="grasper", opponent=self.dummy)
        grasper.state = "CHASING"

        # Coloca o dummy bem perto (< 0.85m)
        self.dummy.wx = 5.4
        self.dummy.wy = 5.0
        initial_hp = self.dummy.hp

        banners = []
        particles = []
        grasper.update(0.1, None, self.dummy, particles=particles, banners=banners)

        # Grasper causa 0 de dano direto, mas imobiliza/atordoa por 1.4s
        self.assertEqual(self.dummy.hp, initial_hp)
        self.assertGreaterEqual(self.dummy.state_timer, 1.3)
        self.assertFalse(grasper.is_alive)
        self.assertTrue(any("ANKLE GRAB" in b.text for b in banners))

    def test_05_swordsman_and_wight_behaviors(self):
        """Verifica as ações de golpe do Swordsman e explosão do Wight."""
        # 1. Swordsman cortando o oponente
        swordsman = ValeriusUndeadSummon(self.valerius, 5.0, 5.0, kind="swordsman", opponent=self.dummy)
        swordsman.state = "CHASING"
        self.dummy.wx = 5.8
        self.dummy.wy = 5.0
        self.dummy.hp = 2

        banners = []
        swordsman.update(0.1, None, self.dummy, banners=banners)
        self.assertEqual(self.dummy.hp, 1)  # Sofreu 1 de dano
        self.assertFalse(swordsman.is_alive)
        self.assertTrue(any("SABER SLASH" in b.text for b in banners))

        # 2. Wight explodindo por proximidade
        wight = ValeriusUndeadSummon(self.valerius, 5.0, 5.0, kind="wight", opponent=self.dummy)
        wight.state = "CHASING"
        self.dummy.wx = 5.6
        self.dummy.wy = 5.0
        self.dummy.hp = 2

        banners = []
        wight.update(0.1, None, self.dummy, banners=banners)
        self.assertEqual(self.dummy.hp, 1)  # Dano da explosão
        self.assertFalse(wight.is_alive)
        self.assertTrue(any("PYRE BLAST" in b.text for b in banners))

    def test_06_manual_corpse_detonation(self):
        """Verifica se pressionar o botão secundário com servo ativo detona-o prematuramente."""
        self.valerius.summon = ValeriusUndeadSummon(self.valerius, 5.5, 5.0, kind="swordsman", opponent=self.dummy)
        self.valerius.summon.state = "CHASING"
        self.dummy.wx = 5.8
        self.dummy.wy = 5.0
        self.dummy.hp = 2

        banners = []
        particles = []
        # Chama a ação secundária enquanto o lacaio está vivo -> detonação cadavérica!
        res = self.valerius.trigger_summon_undead(particles=particles, opponent=self.dummy, banners=banners)
        self.assertTrue(res)
        self.assertIsNone(self.valerius.summon)
        self.assertEqual(self.dummy.hp, 1)  # Explosão atingiu o dummy
        self.assertEqual(self.valerius.summon_timer, self.valerius.summon_cooldown)
        self.assertTrue(any("CORPSE DETONATION" in b.text for b in banners))

    def test_07_mist_dash_and_scythe_guard(self):
        """Verifica a esquiva névoa espectral e a guarda de foice."""
        # 1. Mist Dash
        particles = []
        res = self.valerius.trigger_mist_dash(1.0, 0.0, particles=particles)
        self.assertTrue(res)
        self.assertEqual(self.valerius.state, STATE_ROLL)
        self.assertEqual(self.valerius.roll_duration, 0.22)
        self.assertTrue(len(particles) > 0)

        # 2. Scythe Guard (Parry)
        self.valerius.state = STATE_IDLE
        self.valerius.roll_recovery_timer = 0.0
        parry_res = self.valerius.trigger_parry()
        self.assertTrue(parry_res)
        self.assertEqual(self.valerius.state, STATE_PARRY)

    def test_08_soul_reap_decapitation_and_skeleton_reanimation(self):
        """Verifica a criação do cadáver SOUL_REAP (cabeça preservada e corpo em esqueleto reanimado)."""
        victim = Samurai(5.0, 5.0, name="Victim")
        victim.col_hair = (40, 30, 20)
        corpse = VoxelCorpse(victim, death_style="SOUL_REAP", slash_dir=(1.0, 0.0))

        self.assertTrue(getattr(corpse, "reanimated_skeleton", False))
        self.assertIsNotNone(getattr(corpse, "severed_head", None))
        self.assertEqual(corpse.severed_head.piece_type, "head")

        # Atualização do esqueleto e emissão de partículas azuis
        particles = []
        corpse.update(0.1, game_map=None, particles=particles)
        self.assertGreater(corpse.skeleton_time, 0.0)

        # Renderização do esqueleto reanimado
        corpse._render_reanimated_skeleton(self.surface, self.camera)

        # Model inspector botões e notas
        from tools.model_inspector import CHARACTER_ANIM_BUTTONS, OVERHAUL_DE_PARA_NOTES
        self.assertIn("valerius", CHARACTER_ANIM_BUTTONS)
        self.assertIn("valerius", OVERHAUL_DE_PARA_NOTES)
        self.assertEqual(len(CHARACTER_ANIM_BUTTONS["valerius"]), 13)


if __name__ == "__main__":
    unittest.main()
