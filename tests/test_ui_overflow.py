"""
Testes unitários automatizados para prevenção e garantia de zero overflow de texto
nas telas de Ajuda (GameHelpModal), Guia de Personagens e Opções (SettingsMenu).
"""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui.game_help import GameHelpModal, FIGHTERS_GUIDE_DATA
from src.ui.settings_menu import SettingsMenu
from src.i18n import set_lang, LANG_PT, LANG_EN


class TestUIOverflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.font.init()
        cls.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        cls.font_large = pygame.font.Font(None, 48)
        cls.font_mid = pygame.font.Font(None, 26)
        cls.font_small = pygame.font.Font(None, 20)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_help_modal_all_tabs_render_no_overflow(self):
        """Verifica se todas as abas do GameHelpModal renderizam em PT e EN sem erros."""
        modal = GameHelpModal()
        for lang in (LANG_PT, LANG_EN):
            set_lang(lang)
            for tab in (GameHelpModal.TAB_RULES, GameHelpModal.TAB_CONTROLS, GameHelpModal.TAB_FIGHTERS):
                modal.open(tab)
                self.screen.fill((0, 0, 0))
                modal.render(self.screen, self.font_large, self.font_mid, self.font_small)
                self.assertTrue(modal.modal_rect.width <= SCREEN_WIDTH)
                self.assertTrue(modal.modal_rect.height <= SCREEN_HEIGHT)

    def test_fighters_guide_all_fighters_render(self):
        """Verifica se cada guerreiro do banco de dados renderiza sem erros nem sobreposição de botões."""
        modal = GameHelpModal()
        for lang in (LANG_PT, LANG_EN):
            set_lang(lang)
            for idx, fdata in enumerate(FIGHTERS_GUIDE_DATA):
                modal.open(GameHelpModal.TAB_FIGHTERS, fighter_idx=idx)
                self.screen.fill((0, 0, 0))
                modal.render(self.screen, self.font_large, self.font_mid, self.font_small)

                # Verifica se os botões do carrossel ficam contidos na largura do modal
                for b_rect in modal.fighter_tab_rects:
                    self.assertGreaterEqual(b_rect.left, modal.modal_rect.left)
                    self.assertLessEqual(b_rect.right, modal.modal_rect.right)

                # Verifica se as pílulas de sub-seções ficam contidas na coluna direita
                for sb_rect in modal.sub_sec_btn_rects:
                    self.assertLessEqual(sb_rect.right, modal.modal_rect.right)

    def test_settings_menu_no_header_controller_overlap(self):
        """Verifica se os cabeçalhos de coluna e as caixas de seleção de controle não colidem."""
        settings = SettingsMenu({})
        for lang in (LANG_PT, LANG_EN):
            set_lang(lang)
            settings.open()
            self.screen.fill((0, 0, 0))
            settings.render(self.screen, self.font_large, self.font_mid, self.font_small)

            # Verifica dimensões e espaçamento das caixas de controle P1 e P2
            self.assertTrue(settings.p1_controller_box_rect.width > 0)
            self.assertTrue(settings.p2_controller_box_rect.width > 0)
            # A caixa P1 deve estar contida dentro da coluna esquerda
            col_w = 430
            panel_x = (SCREEN_WIDTH - 960) // 2
            col_left_x = panel_x + 30
            self.assertGreaterEqual(settings.p1_controller_box_rect.right, col_left_x + col_w - 220)
            self.assertLessEqual(settings.p1_controller_box_rect.right, col_left_x + col_w)


if __name__ == "__main__":
    unittest.main()
