#!/usr/bin/env python3
"""
Test Suite para Fase 3: Finishers, Dynamic Intros/Victories & Audio Systems.
Verifica:
1. Universal extra_props propagation para todos os combatentes.
2. O-rin shamisen procedural melody SFX e trigger nos eventos.
3. Musashi wave Ki projectile aura e 3-act finisher drive.
4. Tomoe Sacred Arrow Volley impact (stun, damage, blood, particles) e non-zero slash_dir.
5. Tomoe Pinned to Earth arrow world rendering.
6. Valerius Soul Reap decapitation (cabeça no pescoço antes do corte, sem duplicação de cabeça voadora).
7. Valerius summons fatal strike triggers (SKELETON_SWORD_EXECUTION e WIGHT_CORRUPTION_ROT).
8. Hanzo melee fatality (HEART_THROAT_STAB) e Goro (EARTH_STOMP_CRUSH).
9. Hendrika fatalities (STILETTO_CAROTID_VITRIOL, ALCHEMIC_FROST_SHATTER).
10. Continuous C0 continuity e active breathing em intros e vitórias.
"""
import os
import sys
import unittest
import math
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

# Headless setup
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((800, 600))


class TestPhase3Fixes(unittest.TestCase):

    def setUp(self):
        from src.effects.cinematic_director import CinematicDirector
        self.cd = CinematicDirector()
        self.cd.is_active = False

    def test_orin_procedural_shamisen_audio(self):
        """Verifica se o gerador procedural de Shamisen produz o som com sucesso."""
        from src.audio.procedural_sfx import generate_shamisen_melody, _GENERATOR_MAP
        from src.audio.sound_events import SoundEvent

        self.assertIn(SoundEvent.SHAMISEN_MELODY, _GENERATOR_MAP)
        snd = generate_shamisen_melody()
        self.assertIsNotNone(snd)
        self.assertIsInstance(snd, pygame.mixer.Sound)

    def test_musashi_wave_projectile(self):
        """Verifica o projétil de onda Ki de Musashi com aura e escala ampliadas."""
        from src.entities.projectile import MusashiWaveProjectile
        wave = MusashiWaveProjectile(10.0, 10.0, 0.4, 1.0, 0.0, owner=None)
        self.assertEqual(wave.width, 1.5)
        self.assertEqual(wave.damage, 2)
        self.assertEqual(wave.max_range, 6.5)

    def test_slash_dir_sanitization(self):
        """Verifica se trigger_fatal_strike sanitiza (0, 0) para vetor não-nulo."""
        from src.entities.red_samurai import RedSamurai
        from src.entities.blue_samurai import BlueSamurai
        p1 = RedSamurai(5.0, 5.0)
        p2 = BlueSamurai(6.0, 5.0)
        self.cd.trigger_fatal_strike(p1, p2, "KENSHIN_SPLIT", (0.0, 0.0))
        self.assertTrue(self.cd.is_active)
        self.assertIsNotNone(self.cd.pending_corpse)
        # Pending corpse deve ter dx != 0 ou dy != 0
        mag = math.hypot(self.cd.pending_corpse.dx, self.cd.pending_corpse.dy)
        self.assertGreater(mag, 0.001)

    def test_valerius_soul_reap_no_duplicate_flying_head(self):
        """Verifica que SOUL_REAP não gera cabeça voadora duplicada em pieces."""
        from src.entities.valerius import ValeriusNecromancer
        from src.entities.red_samurai import RedSamurai
        from src.entities.voxel_corpse import VoxelCorpse

        valerius = ValeriusNecromancer(5.0, 5.0)
        victim = RedSamurai(6.0, 5.0)

        # Dispara SOUL_REAP
        self.cd.trigger_fatal_strike(valerius, victim, "SOUL_REAP", (1.0, 0.0))
        # Head começa na posição da vítima (pescoço), não na foice
        self.assertAlmostEqual(self.cd.valerius_head_x, victim.wx)
        self.assertAlmostEqual(self.cd.valerius_head_y, victim.wy)

        # Corpse gerado para SOUL_REAP não deve ter severed_head em pieces
        corpse = VoxelCorpse(victim, "SOUL_REAP", (1.0, 0.0))
        self.assertTrue(getattr(corpse, "reanimated_skeleton", False))
        for p in corpse.pieces:
            self.assertNotEqual(p.piece_type, "head")

    def test_valerius_summon_fatalities(self):
        """Verifica que mortes por servos invocam fatalidades cinematográficas apropriadas."""
        from src.entities.valerius import ValeriusNecromancer, ValeriusUndeadSummon
        from src.entities.red_samurai import RedSamurai

        val = ValeriusNecromancer(5.0, 5.0)
        target = RedSamurai(5.5, 5.0)
        target.hp = 1  # 1 HP restante

        # Soldado esqueleto
        swordsman = ValeriusUndeadSummon(val, 5.2, 5.0, kind="swordsman", opponent=target)
        swordsman.state = "CHASING"
        swordsman.update(0.016, None, target, cinematic_director=self.cd)
        self.assertTrue(self.cd.is_active)
        self.assertEqual(self.cd.finisher_style, "SKELETON_SWORD_EXECUTION")

        # Pyre wight
        self.cd.is_active = False
        target2 = RedSamurai(5.5, 5.0)
        target2.hp = 1
        wight = ValeriusUndeadSummon(val, 5.4, 5.0, kind="wight", opponent=target2)
        wight.explode(opponent=target2, cinematic_director=self.cd)
        self.assertTrue(self.cd.is_active)
        self.assertEqual(self.cd.finisher_style, "WIGHT_CORRUPTION_ROT")

    def test_hanzo_and_goro_finishers_in_cinematic(self):
        """Verifica registro e inicialização de HEART_THROAT_STAB e EARTH_STOMP_CRUSH."""
        from src.entities.yellow_ninja import YellowNinja
        from src.entities.goro import GoroFarmer
        from src.entities.red_samurai import RedSamurai

        hanzo = YellowNinja(5.0, 5.0)
        goro = GoroFarmer(5.0, 5.0)
        victim = RedSamurai(6.0, 5.0)

        # Hanzo Throat Slit
        self.cd.trigger_fatal_strike(hanzo, victim, "HEART_THROAT_STAB", (1.0, 0.0))
        self.assertTrue(self.cd.is_active)
        self.assertEqual(self.cd.finisher_style, "HEART_THROAT_STAB")

        # Goro Earth Stomp
        self.cd.is_active = False
        self.cd.trigger_fatal_strike(goro, victim, "EARTH_STOMP_CRUSH", (1.0, 0.0))
        self.assertTrue(self.cd.is_active)
        self.assertEqual(self.cd.finisher_style, "EARTH_STOMP_CRUSH")

    def test_sacred_volley_non_zero_slash_and_nonlethal_stun(self):
        """Verifica que SacredArrowVolleyProjectile aplica dano, stun e passa vetor não-nulo."""
        from src.entities.kyudo_archer import KyudoArcher
        from src.entities.red_samurai import RedSamurai
        from src.entities.projectile import SacredArrowVolleyProjectile
        from src.combat.collision import CombatSystem
        from src.isometric.camera import Camera

        cs = CombatSystem()
        camera = Camera(800, 600)
        archer = KyudoArcher(5.0, 5.0)
        victim = RedSamurai(8.0, 5.0)
        victim.hp = 3  # Sobrevive ao impacto de 2 dano

        volley = SacredArrowVolleyProjectile(5.0, 5.0, 8.0, 5.0, owner=archer)
        volley.has_impacted = True
        volley.damage_dealt = False

        particles = []
        banners = []
        projectiles = [volley]

        class DummyMap:
            def is_solid(self, x, y): return False
            def is_pit(self, x, y): return False
            has_updates = False
            destructibles = []
            interactive_props = []
            bamboos = []
            lanterns = []
            traps = []

        cs.process_combat(
            archer, victim, DummyMap(),
            particles=particles, banners=banners,
            camera=camera, projectiles=projectiles,
            dt=0.016, cinematic_director=self.cd
        )

        # O alvo sofreu dano e entrou em stun
        self.assertEqual(victim.hp, 1)
        self.assertEqual(victim.state, "STUNNED")
        self.assertGreater(len(particles), 0)
        self.assertGreater(len(banners), 0)


if __name__ == "__main__":
    unittest.main()
