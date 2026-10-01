"""
Suíte de testes automatizados para o Entregável 3.2 da Fase 3:
Kanjis Kurosawa no Flash Cinematográfico (CinematicDirector).
Valida:
1. Geração e cache da superfície Sumi-E ao disparar o golpe fatal (zero garbage collection).
2. Seleção de ideogramas clássicos de cinema samurai (一刀両断, 決闘終焉, 神速必殺, 生死一瞬).
3. Renderização com alpha e vinheta monocromática em modo headless.
4. Limpeza completa dos recursos no reset do round.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"

import unittest
import pygame
pygame.init()
pygame.font.init()

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.effects.cinematic_director import CinematicDirector
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai

class TestCinematicKanji(unittest.TestCase):
    def setUp(self):
        self.director = CinematicDirector()
        self.attacker = RedSamurai(10.0, 10.0)
        self.victim = BlueSamurai(11.0, 10.0)
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def test_kanji_overlay_generation(self):
        """Teste 1: Geração e cache da textura de Kanji Sumi-E no golpe fatal."""
        self.assertIsNone(self.director.cached_kanji_surf)
        self.assertEqual(self.director.current_kanji_text, "")

        self.director.trigger_fatal_strike(
            self.attacker, self.victim, "KENSHIN_SPLIT", (1.0, 0.0)
        )

        self.assertIsNotNone(self.director.cached_kanji_surf)
        self.assertGreater(self.director.cached_kanji_surf.get_width(), 100)
        self.assertGreater(self.director.cached_kanji_surf.get_height(), 50)
        
        valid_kanjis = ["一刀両断", "決闘終焉", "神速必殺", "生死一瞬"]
        self.assertIn(self.director.current_kanji_text, valid_kanjis)
        self.assertTrue(len(self.director.current_kanji_subtitle) > 0)

    def test_kanji_rendering_headless_and_alpha_fade(self):
        """Teste 2: Renderização visual headless e transição de transparência (alpha fade)."""
        self.director.trigger_fatal_strike(
            self.attacker, self.victim, "KENSHIN_SPLIT", (1.0, 0.0)
        )

        # Frame inicial do flash (alpha máximo)
        self.director.apply_cinematic_filter(self.surface)
        self.assertGreaterEqual(self.director.cached_kanji_surf.get_alpha(), 200)

        # Simular passagem de tempo (meio do flash)
        self.director.update(0.30, None)
        self.director.apply_cinematic_filter(self.surface)
        self.assertLess(self.director.cached_kanji_surf.get_alpha(), 255)

        # Fim do flash
        self.director.update(0.30, None)
        self.assertEqual(self.director.bw_flash_timer, 0.0)
        # Quando flash zerado, não desenha mais
        self.director.apply_cinematic_filter(self.surface)

    def test_reset_round_cleans_kanji_resources(self):
        """Teste 3: Reset de round limpa completamente o cache de kanji."""
        self.director.trigger_fatal_strike(
            self.attacker, self.victim, "KENSHIN_SPLIT", (1.0, 0.0)
        )
        self.assertIsNotNone(self.director.cached_kanji_surf)

        self.director.reset_round()
        self.assertIsNone(self.director.cached_kanji_surf)
        self.assertEqual(self.director.current_kanji_text, "")
        self.assertEqual(self.director.current_kanji_subtitle, "")
        self.assertFalse(self.director.is_active)

if __name__ == "__main__":
    unittest.main()
