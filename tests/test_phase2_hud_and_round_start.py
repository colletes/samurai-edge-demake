"""
Testes automatizados para a Fase 2:
- Barras Universais de Cooldown (Item 6)
- Temporizador de Abertura de Round e Kanjis (Item 10)
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"
import unittest
import pygame
pygame.init()
pygame.font.init()

from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.yellow_ninja import YellowNinja
from src.entities.american_ninja import AmericanNinja
from src.entities.gray_ninja import GrayNinja
from src.entities.purple_ninja import PurpleNinja
from src.entities.saitou_samurai import SaitouSamurai
from src.entities.rifleman import Rifleman
from src.entities.kabuki import Kabuki
from src.entities.kyudo_archer import KyudoArcher
from src.entities.pirate import PirateSwordswoman
from src.entities.musketeer import Musketeer
from main import get_fighter_cooldown_data
from src.ui.fonts import get_text_font, get_title_font


class TestPhase2HudAndRoundStart(unittest.TestCase):
    def test_all_fighters_have_valid_cooldown_data(self):
        """Verifica se todos os 12 combatentes retornam dados estruturados válidos de cooldown."""
        fighters = [
            RedSamurai(0, 0), BlueSamurai(0, 0), YellowNinja(0, 0), AmericanNinja(0, 0),
            GrayNinja(0, 0), PurpleNinja(0, 0), SaitouSamurai(0, 0), Rifleman(0, 0),
            Kabuki(0, 0), KyudoArcher(0, 0), PirateSwordswoman(0, 0), Musketeer(0, 0)
        ]
        for f in fighters:
            data = get_fighter_cooldown_data(f)
            self.assertIsNotNone(data, f"Combatente {f.__class__.__name__} retornou None")
            self.assertIn("name", data)
            self.assertIn("timer", data)
            self.assertIn("max_cd", data)
            self.assertIn("color", data)
            self.assertGreaterEqual(data["max_cd"], 0.1)

    def test_cooldown_active_timers(self):
        """Verifica se habilidades em recarga reportam os timers e valores corretos."""
        # Kenshi
        kenshi = RedSamurai(0, 0)
        kenshi.ryuu_timer = 2.1
        data = get_fighter_cooldown_data(kenshi)
        self.assertEqual(data["name"], "Ryuu Tsui Sen")
        self.assertAlmostEqual(data["timer"], 2.1)

        # Anne Bonny
        anne = PirateSwordswoman(0, 0)
        anne.cannon_cooldown_timer = 3.5
        data = get_fighter_cooldown_data(anne)
        self.assertEqual(data["name"], "Canhão Naval")
        self.assertAlmostEqual(data["timer"], 3.5)

        # Julie Musketeer
        julie = Musketeer(0, 0)
        julie.flintlock_timer = 4.0
        data = get_fighter_cooldown_data(julie)
        self.assertEqual(data["name"], "Pederneira")
        self.assertAlmostEqual(data["timer"], 4.0)

        # Saitou
        saitou = SaitouSamurai(0, 0)
        saitou.zeroshiki_timer = 1.2
        data = get_fighter_cooldown_data(saitou)
        self.assertEqual(data["name"], "Zeroshiki")
        self.assertAlmostEqual(data["timer"], 1.2)

    def test_warning_states(self):
        """Verifica se estados críticos geram badges de aviso com warning=True."""
        # Hanzo sem kunai
        hanzo = YellowNinja(0, 0)
        hanzo.has_kunai = False
        data = get_fighter_cooldown_data(hanzo)
        self.assertTrue(data.get("warning"))
        self.assertEqual(data["name"], "Sem Kunai")

        # Teppo sem pólvora
        teppo = Rifleman(0, 0)
        teppo.has_ammo = False
        data = get_fighter_cooldown_data(teppo)
        self.assertTrue(data.get("warning"))
        self.assertEqual(data["name"], "Sem Pólvora")

        # American Ninja com Yamato KO
        joe = AmericanNinja(0, 0)
        joe.dog.state = "KNOCKED_OUT"
        joe.dog.knockout_timer = 1.8
        data = get_fighter_cooldown_data(joe)
        self.assertTrue(data.get("warning"))
        self.assertEqual(data["name"], "Cão Yamato KO")

    def test_kanji_fonts_rendering(self):
        """Verifica se os kanjis 準備 e 始め! são renderizados com sucesso pela fonte ZenAntique."""
        f_kanji = get_text_font(46)
        surf_junbi = f_kanji.render("準備", True, (255, 255, 255))
        surf_hajime = f_kanji.render("始め!", True, (255, 255, 255))
        self.assertGreater(surf_junbi.get_width(), 40)
        self.assertGreater(surf_hajime.get_width(), 40)

        f_sub = get_title_font(18)
        surf_ready = f_sub.render("READY...", True, (255, 255, 255))
        surf_start = f_sub.render("START!", True, (255, 255, 255))
        self.assertGreater(surf_ready.get_width(), 20)
        self.assertGreater(surf_start.get_width(), 20)

    def test_initial_cooldown_starts_at_round_start(self):
        """Verifica se os combatentes com cooldown inicial (Anne e Julie) iniciam no round_start."""
        anne = PirateSwordswoman(0, 0)
        julie = Musketeer(0, 0)

        # Na criação, possuem os timers iniciais
        self.assertEqual(anne.cannon_cooldown_timer, 4.5)
        self.assertEqual(julie.flintlock_timer, 1.0)

        # Simulação: antes do round começar (intro e contagem), updates ocorrem com dt=0.0
        from src.world.map_data import GameMap
        g_map = GameMap()
        anne.update(0.0, g_map)
        julie.update(0.0, g_map)
        self.assertEqual(anne.cannon_cooldown_timer, 4.5)
        self.assertEqual(julie.flintlock_timer, 1.0)

        # Simulação: no momento exato em que o round inicia (on_round_start é chamado)
        anne.on_round_start()
        julie.on_round_start()
        self.assertEqual(anne.cannon_cooldown_timer, 4.5)
        self.assertEqual(julie.flintlock_timer, 1.0)

        # Simulação: com a luta em andamento (dt normal), os timers começam a decrescer
        anne.update(0.5, g_map)
        julie.update(0.5, g_map)
        self.assertAlmostEqual(anne.cannon_cooldown_timer, 4.0)
        self.assertAlmostEqual(julie.flintlock_timer, 0.5)


if __name__ == "__main__":
    unittest.main()
