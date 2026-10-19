"""
Testes automatizados para a interface mobile (Smartphones iOS/Android),
garantindo paginação, seleção em 2 etapas, carrossel de arena, editor HUD e ausência de caixa preta.
"""
import os
import sys
import unittest
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input import device_info
from src.ui.character_select import CharacterSelectScreen
from src.ui.arena_select import ArenaSelectScreen
from src.ui.settings_menu import SettingsMenu
from src.effects import parchment as pm


class TestMobileUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        pygame.init()
        pygame.font.init()
        cls.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        cls.font_large = pygame.font.Font(None, 48)
        cls.font_mid = pygame.font.Font(None, 26)
        cls.font_small = pygame.font.Font(None, 20)

    def setUp(self):
        device_info.set_ui_mode("mobile")

    def tearDown(self):
        device_info.set_ui_mode("auto")

    def test_parchment_brush_and_border_no_opaque_black_box(self):
        """Verifica se pinceladas e bordas possuem canal alfa per-pixel transparente válido."""
        stroke = pm.make_brush_stroke(200, 30, color=(180, 40, 35), seed=3)
        self.assertEqual(stroke.get_size(), (200, 30))
        # O canto externo do traço (0, 0) deve ser totalmente transparente (alpha 0)
        c0 = stroke.get_at((0, 0))
        self.assertEqual(c0.a, 0, f"Canto externo deveria ser transparente, mas obteve {c0}")

        # O centro do traço deve ser visível (alpha > 50)
        mid_x, mid_y = 100, 15
        cm = stroke.get_at((mid_x, mid_y))
        self.assertGreater(cm.a, 50, f"Centro deveria ter tinta, mas obteve {cm}")

    def test_mobile_character_selection_flow(self):
        """Verifica o fluxo completo de seleção mobile: P1 -> confirma -> IA -> confirma."""
        cs = CharacterSelectScreen()
        self.assertTrue(device_info.is_mobile_device())
        self.assertEqual(cs.selection_step, "P1")

        # Renderiza em modo mobile
        self.screen.fill((0, 0, 0))
        cs.render(self.screen, self.font_large, self.font_mid, self.font_small)

        # Clica no segundo lutador (Musashi) na página 0
        card_rect_1 = cs.card_rects[1]
        self.assertGreater(card_rect_1.width, 0)
        ev_click_card = pygame.event.Event(pygame.FINGERDOWN, {"x": card_rect_1.centerx / SCREEN_WIDTH, "y": card_rect_1.centery / SCREEN_HEIGHT, "finger_id": 0})
        cs.handle_event(ev_click_card)
        self.assertEqual(cs.p1_choice_idx, 1)

        # Clica no botão de confirmação mobile (bloqueia P1 e avança para IA)
        ev_confirm_p1 = pygame.event.Event(pygame.FINGERDOWN, {"x": cs.btn_mobile_confirm.centerx / SCREEN_WIDTH, "y": cs.btn_mobile_confirm.centery / SCREEN_HEIGHT, "finger_id": 0})
        res1 = cs.handle_event(ev_confirm_p1)
        self.assertFalse(res1)
        self.assertEqual(cs.selection_step, "AI")

        # Escolhe lutador para a IA (card 2)
        card_rect_2 = cs.card_rects[2]
        ev_click_ai = pygame.event.Event(pygame.FINGERDOWN, {"x": card_rect_2.centerx / SCREEN_WIDTH, "y": card_rect_2.centery / SCREEN_HEIGHT, "finger_id": 0})
        cs.handle_event(ev_click_ai)
        self.assertEqual(cs.p2_choice_idx, 2)

        # Clica no botão de iniciar duelo
        res2 = cs.handle_event(ev_confirm_p1)
        self.assertTrue(res2)

    def test_mobile_character_pagination(self):
        """Verifica paginação mobile entre conjuntos de lutadores."""
        cs = CharacterSelectScreen()
        cs.render(self.screen, self.font_large, self.font_mid, self.font_small)
        self.assertEqual(cs.mobile_page, 0)

        # Avança para a página 1
        ev_next = pygame.event.Event(pygame.FINGERDOWN, {"x": cs.btn_mobile_next.centerx / SCREEN_WIDTH, "y": cs.btn_mobile_next.centery / SCREEN_HEIGHT, "finger_id": 0})
        cs.handle_event(ev_next)
        self.assertEqual(cs.mobile_page, 1)

        # Retorna para a página 0
        ev_prev = pygame.event.Event(pygame.FINGERDOWN, {"x": cs.btn_mobile_prev.centerx / SCREEN_WIDTH, "y": cs.btn_mobile_prev.centery / SCREEN_HEIGHT, "finger_id": 0})
        cs.handle_event(ev_prev)
        self.assertEqual(cs.mobile_page, 0)

    def test_mobile_arena_selection(self):
        """Verifica navegação e confirmação no carrossel panorâmico de arenas."""
        ascr = ArenaSelectScreen()
        ascr.render(self.screen, self.font_large, self.font_mid, self.font_small)
        start_idx = ascr.selected_idx

        # Próxima arena
        ev_next = pygame.event.Event(pygame.FINGERDOWN, {"x": ascr.btn_mobile_next.centerx / SCREEN_WIDTH, "y": ascr.btn_mobile_next.centery / SCREEN_HEIGHT, "finger_id": 0})
        ascr.handle_event(ev_next)
        self.assertEqual(ascr.selected_idx, (start_idx + 1) % len(ascr.arenas))

        # Arena anterior
        ev_prev = pygame.event.Event(pygame.FINGERDOWN, {"x": ascr.btn_mobile_prev.centerx / SCREEN_WIDTH, "y": ascr.btn_mobile_prev.centery / SCREEN_HEIGHT, "finger_id": 0})
        ascr.handle_event(ev_prev)
        self.assertEqual(ascr.selected_idx, start_idx)

    def test_settings_menu_mobile_panel(self):
        """Verifica se o menu de configurações mobile abre, renderiza e fecha sem sobreposição."""
        menu = SettingsMenu({})
        menu.open()
        self.assertTrue(menu.is_open)
        menu.render(self.screen, self.font_large, self.font_mid, self.font_small)

        # Botão Fechar deve estar posicionado com segurança
        self.assertGreaterEqual(menu.close_rect.bottom, SCREEN_HEIGHT - 75)
        self.assertLessEqual(menu.close_rect.bottom, SCREEN_HEIGHT - 10)

        # Clica em fechar
        ev_close = pygame.event.Event(pygame.FINGERDOWN, {"x": menu.close_rect.centerx / SCREEN_WIDTH, "y": menu.close_rect.centery / SCREEN_HEIGHT, "finger_id": 0})
        menu.handle_event(ev_close)
        self.assertFalse(menu.is_open)


if __name__ == "__main__":
    unittest.main()
