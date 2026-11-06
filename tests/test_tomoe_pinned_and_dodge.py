"""
Test Suite: Tomoe Pinned to Earth Finisher, Blood Fountain, Rope Cooldown Dodge, and 3.0s Secondary Cooldown.
"""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

from src.entities.kyudo_archer import KyudoArcher
from src.entities.red_samurai import RedSamurai
from src.entities.voxel_corpse import VoxelCorpse, render_pinned_to_earth_model
from src.effects.cinematic_director import CinematicDirector
from src.isometric.camera import Camera


class TestTomoePinnedAndDodge(unittest.TestCase):

    def test_secondary_cooldown_is_3s(self):
        """Verifica se o cooldown do ataque secundário (Chuva Sagrada) foi reduzido para 3.0s."""
        archer = KyudoArcher(5.0, 5.0)
        self.assertEqual(archer.volley_cooldown, 3.0)
        self.assertEqual(archer.volley_cooldown_timer, 3.0)
        self.assertEqual(archer.sacred_volley_cooldown, 3.0)
        self.assertEqual(archer.hamaya_cooldown, 3.0)
        self.assertEqual(archer.ofuda_cooldown, 3.0)

    def test_rope_cooldown_dodge_fallback(self):
        """Verifica se quando a esquiva de corda está em cooldown, Tomoe executa a esquiva padrão (mergulho ao chão)."""
        from main import execute_fighter_roll

        archer = KyudoArcher(5.0, 5.0)
        archer.rope_timer = 1.5  # Em cooldown!
        particles = []

        # Executa o roll
        success = execute_fighter_roll(archer, dwx=-1.0, dwy=0.0, aim_x=4.0, aim_y=5.0, particles=particles)
        self.assertTrue(success, "Dodge deve ter sucesso mesmo com a corda em cooldown")
        self.assertEqual(archer.state, "ROLL", "Estado deve ser ROLL (mergulho ao chão padrão)")
        self.assertFalse(archer.is_charging_rope, "Não deve estar carregando corda")

        # Verifica props do somersault / miko_roll
        self.assertGreater(archer.state_timer, 0.0)

        # Testa também o método direto trigger_rope_arrow com fallback
        archer2 = KyudoArcher(6.0, 6.0)
        archer2.rope_timer = 1.2
        projectiles = []
        res = archer2.trigger_rope_arrow(8.0, 6.0, projectiles, particles)
        self.assertTrue(res)
        self.assertEqual(archer2.state, "ROLL", "trigger_rope_arrow deve cair no fallback trigger_roll em cooldown")

    def test_pinned_to_earth_corpse_3d_and_no_fall_twisting(self):
        """Verifica se PINNED_TO_EARTH cria um corpo com is_pinned_to_earth=True, region=None e sem rotação por fall_factor."""
        victim = RedSamurai(5.0, 5.0)
        corpse = VoxelCorpse(victim, death_style="PINNED_TO_EARTH", slash_dir=(1.0, 0.0))

        self.assertTrue(getattr(corpse, "is_pinned_to_earth", False))
        self.assertGreater(len(corpse.pieces), 0)
        self.assertIsNone(corpse.pieces[0].region, "region deve ser None para evitar recorte 2D por fall_factor")

        # Renderização não deve falhar em múltiplos azimutes de câmera orbitando 360 graus
        surf = pygame.Surface((800, 600))
        camera = Camera(5.0, 5.0)
        for az in [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]:
            camera.azimuth = az
            corpse.render(surf, camera)

    def test_pinned_to_earth_throat_blood_fountain(self):
        """Verifica se a fonte de sangue da garganta jorra ativamente em VoxelCorpse e CinematicDirector."""
        victim = RedSamurai(5.0, 5.0)
        corpse = VoxelCorpse(victim, death_style="PINNED_TO_EARTH", slash_dir=(1.0, 0.0))
        particles = []

        # Atualiza o corpo por alguns frames
        for _ in range(5):
            corpse.update(0.04, None, particles)

        self.assertGreater(len(particles), 0, "Partículas de sangue da garganta devem ser geradas continuamente")
        # Verifica velocidade vertical alta (fonte arterial para cima)
        upward_particles = [p for p in particles if getattr(p, "vz", 0.0) > 2.0]
        self.assertGreater(len(upward_particles), 0, "Sangue deve espirrar para cima (vz > 2.0)")

        # Testa também em CinematicDirector durante prog >= 0.38
        director = CinematicDirector()
        attacker = KyudoArcher(4.0, 5.0)
        victim2 = RedSamurai(5.0, 5.0)
        director.finisher_style = "PINNED_TO_EARTH"
        director._arm_closeup_finisher_strike(attacker, victim2, duration=0.8)

        # Simula progresso até prog >= 0.38
        director.finisher_strike_timer = 0.20  # prog = (0.8 - 0.2) / 0.8 = 0.75
        cd_particles = []
        director.update(0.03, None, cd_particles)

        self.assertTrue(director.tomoe_pinned_played)
        self.assertEqual(victim2.state, "PINNED_DOWN", "Vítima deve estar no estado PINNED_DOWN")
        self.assertTrue(victim2.extra_props.get("is_pinned_to_earth", False))
        self.assertGreater(len(cd_particles), 0, "CinematicDirector deve gerar partículas de sangue da garganta")


if __name__ == "__main__":
    unittest.main()
