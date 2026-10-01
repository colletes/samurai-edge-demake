"""
Testes automatizados para validação do fluxo de confirmação do Jogador 2
na tela de Seleção de Personagens quando o Jogador 1 está com o controle conectado.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"
import unittest
import pygame
from src.ui.character_select import CharacterSelectScreen
from src.input.controller_manager import get_controller_manager

class TestP2CharacterConfirmation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    def setUp(self):
        self.state = CharacterSelectScreen()
        self.state.vs_ai = False  # Modo 2 Jogadores (Versus local)
        self.state.p1_ready = False
        self.state.p2_ready = False

    def test_p1_confirms_with_keyboard_and_p2_confirms_with_enter(self):
        # 1. P1 confirma com [E]
        ev_p1 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        self.state.handle_event(ev_p1)
        self.assertTrue(self.state.p1_ready, "P1 should be ready after pressing [E]")
        self.assertFalse(self.state.p2_ready, "P2 should NOT be ready yet")

        # 2. P2 aperta RETURN (Enter)
        ev_p2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        res = self.state.handle_event(ev_p2)
        self.assertTrue(self.state.p2_ready, "P2 should be ready after pressing RETURN")
        self.assertTrue(res, "Should trigger match start when both are ready")

    def test_p1_ready_and_p2_confirms_with_u_key(self):
        # P1 já está pronto (ex: confirmou via controle)
        self.state.p1_ready = True
        self.assertFalse(self.state.p2_ready)

        # P2 aperta sua tecla de ação primária [U]
        ev_u = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_u)
        res = self.state.handle_event(ev_u)
        self.assertTrue(self.state.p2_ready, "P2 should be ready after pressing [U]")
        self.assertTrue(res, "Should trigger match start")

    def test_p1_ready_and_p2_confirms_with_space(self):
        # P1 pronto via controle
        self.state.p1_ready = True
        self.assertFalse(self.state.p2_ready)

        # P2 aperta SPACE
        ev_space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        res = self.state.handle_event(ev_space)
        self.assertTrue(self.state.p2_ready, "P2 should be ready after pressing SPACE when P1 is already ready")
        self.assertTrue(res, "Should trigger match start")

    def test_single_controller_does_not_control_p2(self):
        # Simula 1 controle conectado
        ctrl_mgr = get_controller_manager()
        # Mock de 1 controle: button 0 (confirm) pertencente a P1
        ev_btn0 = pygame.event.Event(pygame.JOYBUTTONDOWN, button=0, instance_id=999)

        # Primeiro clique no controle confirma P1
        self.state.handle_event(ev_btn0)
        self.assertTrue(self.state.p1_ready, "P1 confirmed with controller")
        self.assertFalse(self.state.p2_ready, "P2 not yet confirmed")

        # Segundo clique no MESMO controle NÃO deve confirmar P2 (sem compartilhamento de controle)
        res = self.state.handle_event(ev_btn0)
        self.assertFalse(self.state.p2_ready, "P2 should NOT be confirmed with P1's single controller")
        self.assertFalse(res, "Match start must not be triggered")

        # P2 deve confirmar através do seu próprio dispositivo (ex: teclado P2 [U] ou [ENTER])
        ev_u = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_u)
        res_p2 = self.state.handle_event(ev_u)
        self.assertTrue(self.state.p2_ready, "P2 confirmed via keyboard")
        self.assertTrue(res_p2, "Match start triggered when both ready")

    def test_p2_cancellation_with_backspace(self):
        self.state.p1_ready = True
        self.state.p2_ready = True
        ev_bk = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE)
        self.state.handle_event(ev_bk)
        self.assertFalse(self.state.p2_ready, "P2 should be unconfirmed")
        self.assertTrue(self.state.p1_ready, "P1 should still be ready")

    def test_render_all_states(self):
        screen = pygame.Surface((1280, 720))
        f_large = pygame.font.Font(None, 40)
        f_mid = pygame.font.Font(None, 28)
        f_small = pygame.font.Font(None, 20)

        for vs_ai in [True, False]:
            self.state.vs_ai = vs_ai
            for p1_ready in [False, True]:
                self.state.p1_ready = p1_ready
                for p2_ready in [False, True]:
                    self.state.p2_ready = p2_ready
                    self.state.update(0.016)
                    self.state.render(screen, f_large, f_mid, f_small)

if __name__ == "__main__":
    unittest.main()
