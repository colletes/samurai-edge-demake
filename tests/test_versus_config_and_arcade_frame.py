import os
import sys
import unittest
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui.versus_config import VersusConfigScreen, load_versus_settings, save_versus_settings
from src.ui.character_select import CharacterSelectScreen
from src.i18n import t, set_lang, LANG_PT, LANG_EN


class TestVersusConfigAndArcadeFrame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        pygame.init()
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def setUp(self):
        set_lang(LANG_PT)

    def test_versus_settings_persistence(self):
        """Testa o salvamento e carregamento das configurações de versus no settings.json."""
        save_versus_settings(mode="watch", rounds_to_win=5, ai_difficulty="hard")
        loaded = load_versus_settings()
        self.assertEqual(loaded["mode"], "watch")
        self.assertEqual(loaded["rounds_to_win"], 5)
        self.assertEqual(loaded["ai_difficulty"], "hard")

        # Teste de limites (clamp entre 1 e 10)
        save_versus_settings(mode="pve", rounds_to_win=15, ai_difficulty="normal")
        loaded = load_versus_settings()
        self.assertEqual(loaded["rounds_to_win"], 10)

        save_versus_settings(mode="pve", rounds_to_win=0, ai_difficulty="normal")
        loaded = load_versus_settings()
        self.assertEqual(loaded["rounds_to_win"], 1)

        # Restaurar padrão
        save_versus_settings(mode="pve", rounds_to_win=2, ai_difficulty="normal")

    def test_versus_config_screen_navigation_and_logic(self):
        """Testa o submenu do Versus: navegação, alternância de valores e desativação da IA em 1P vs 2P."""
        screen = VersusConfigScreen()
        screen.open()
        screen.mode = "pve"
        screen.rounds_to_win = 2
        screen.ai_difficulty = "normal"
        screen.selected = VersusConfigScreen.OPT_MODE

        # 1. Teclado: Mudar Modo com Seta Direita
        ev_right = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT})
        screen.handle_event(ev_right)
        self.assertEqual(screen.mode, "pvp")

        # 2. Quando o modo for 'pvp', a opção de Dificuldade da IA deve ser pulada na navegação
        screen.selected = VersusConfigScreen.OPT_ROUNDS
        ev_down = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_DOWN})
        screen.handle_event(ev_down)
        # Deve ter pulado OPT_DIFFICULTY e ido direto para OPT_PROCEED!
        self.assertEqual(screen.selected, VersusConfigScreen.OPT_PROCEED)

        # 3. Navegação para cima volta para OPT_ROUNDS (pulando OPT_DIFFICULTY)
        ev_up = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP})
        screen.handle_event(ev_up)
        self.assertEqual(screen.selected, VersusConfigScreen.OPT_ROUNDS)

        # 4. Ajustar Rounds com Setas Esquerda/Direita
        screen.handle_event(ev_right)
        self.assertEqual(screen.rounds_to_win, 3)
        screen.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT}))
        self.assertEqual(screen.rounds_to_win, 2)

        # 5. Voltar Modo para 'pve'
        screen.selected = VersusConfigScreen.OPT_MODE
        screen.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT}))
        self.assertEqual(screen.mode, "pve")

        # Agora OPT_DIFFICULTY está ativo e navegável
        screen.selected = VersusConfigScreen.OPT_ROUNDS
        screen.handle_event(ev_down)
        self.assertEqual(screen.selected, VersusConfigScreen.OPT_DIFFICULTY)

        # Mudar dificuldade para 'hard'
        screen.handle_event(ev_right)
        self.assertEqual(screen.ai_difficulty, "hard")

        # 6. Pressionar Enter em OPT_PROCEED retorna 'PROCEED'
        screen.selected = VersusConfigScreen.OPT_PROCEED
        ev_enter = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
        res = screen.handle_event(ev_enter)
        self.assertEqual(res, "PROCEED")

        # 7. Pressionar ESC retorna 'BACK'
        ev_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        res = screen.handle_event(ev_esc)
        self.assertEqual(res, "BACK")

    def test_versus_config_screen_mouse_interaction(self):
        """Testa a interação por mouse no submenu do Versus (cliques nas setas e botões)."""
        screen = VersusConfigScreen()
        screen.open()
        surface = pygame.display.get_surface()
        screen.render(surface)

        # Testar clique na seta direita de Rounds
        r_right_rounds = screen.arrow_right_rects[VersusConfigScreen.OPT_ROUNDS]
        init_rounds = screen.rounds_to_win
        ev_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": r_right_rounds.center})
        screen.handle_event(ev_click)
        self.assertEqual(screen.rounds_to_win, min(10, init_rounds + 1))

        # Testar clique no botão Avançar
        ev_click_proceed = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": screen.btn_proceed_rect.center})
        res = screen.handle_event(ev_click_proceed)
        self.assertEqual(res, "PROCEED")

        # Testar clique no botão Voltar
        ev_click_back = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": screen.btn_back_rect.center})
        res = screen.handle_event(ev_click_back)
        self.assertEqual(res, "BACK")

    def test_character_select_arcade_single_frame(self):
        """Testa que no modo Arcade apenas a moldura do P1 é ativa na tela de seleção."""
        char_screen = CharacterSelectScreen(ai_difficulty="normal", rounds_to_win=2)
        char_screen.arcade_mode = True
        char_screen.reset()

        surface = pygame.display.get_surface()
        font_large = pygame.font.Font(None, 36)
        font_mid = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)

        # Renderizar tela em modo arcade
        char_screen.render(surface, font_large, font_mid, font_small)

        # No modo arcade, os botões antigos de modo e dificuldade são vazios
        self.assertEqual(char_screen.mode_btn_rect.width, 0)
        self.assertEqual(char_screen.difficulty_btn_rect.width, 0)

        # No modo arcade, confirmar P1 avança direto para início (retorna True)
        char_screen.p1_choice_idx = 0
        ev_confirm = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
        res = char_screen.handle_event(ev_confirm)
        self.assertTrue(res)

    def test_character_select_versus_mode_and_back(self):
        """Testa que no Versus o botão BACK devolve 'BACK' (para voltar ao submenu Versus)."""
        char_screen = CharacterSelectScreen(ai_difficulty="normal", rounds_to_win=3)
        char_screen.arcade_mode = False
        char_screen.match_mode = "pve"
        char_screen.reset()

        surface = pygame.display.get_surface()
        font_large = pygame.font.Font(None, 36)
        font_mid = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)
        char_screen.render(surface, font_large, font_mid, font_small)

        ev_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        res = char_screen.handle_event(ev_esc)
        self.assertEqual(res, "BACK")


if __name__ == "__main__":
    unittest.main()
