"""
Testes dedicados para:
1. Tela de Opções (SettingsMenu): PLAYER 1 / PLAYER 2, remapeamento de Gamepad e exibição de botões.
2. Navegação em Menus com D-Pad (11, 12, 13, 14) e botões DualSense (0=✕, 1=○, 2=▢, 3=△).
3. Suporte completo a Gamepad no Guia/Modal de Ajuda (fechar com ○, scroll, tabs).
4. Hanzo (YellowNinja): Pulo parabólico evasivo, arremesso aéreo de kunai e Tanto disponível apenas sem kunai.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame
from src.config import (
    DEFAULT_CONTROLS, CHAR_NINJA, CHAR_KENSHIN
)
from src.input.controller_manager import (
    ControllerManager, ControllerDevice, get_controller_manager,
    CONTROLLER_TYPE_DUALSENSE, ACTION_ATTACK, ACTION_DASH, ACTION_CONFIRM, ACTION_CANCEL, ACTION_MENU,
    BTN_DPAD_UP, BTN_DPAD_DOWN, BTN_DPAD_LEFT, BTN_DPAD_RIGHT
)
from src.ui.settings_menu import SettingsMenu
from src.ui.character_select import CharacterSelectScreen
from src.ui.game_help import GameHelpModal
from src.entities.yellow_ninja import YellowNinja
from src.entities.red_samurai import RedSamurai
from src.combat.collision import CombatSystem
from src.world.map_data import GameMap
from src.isometric.camera import Camera

class MockDualSenseJoystick:
    def __init__(self, inst_id=1):
        self.inst_id = inst_id
        self._buttons = [False] * 16
    def get_instance_id(self): return self.inst_id
    def get_name(self): return "DualSense Wireless Controller"
    def get_guid(self): return "030000004c050000e60c000011010000"
    def get_numbuttons(self): return 16
    def get_numaxes(self): return 4
    def get_numhats(self): return 0
    def get_axis(self, idx): return 0.0
    def get_button(self, idx): return self._buttons[idx] if idx < len(self._buttons) else False

def test_settings_menu_labels_and_remapping():
    controls = dict(DEFAULT_CONTROLS)
    menu = SettingsMenu(controls)

    # 1. Verificar labels generificados (Player 1 e Player 2, sem Kenshin/Musashi)
    labels = [lbl for _, lbl, _ in menu.items]
    assert any("Mover Cima" in l for l in labels)
    assert any("Ataque Principal" in l for l in labels)
    assert any("Ação Secundária (Dash)" in l for l in labels)
    for lbl in labels:
        assert "Kenshin" not in lbl and "Kenshi" not in lbl and "Musashi" not in lbl, f"Nome antigo encontrado: {lbl}"

    # 2. Configurar mock de controle no manager
    ctrl_mgr = get_controller_manager()
    joy = MockDualSenseJoystick(inst_id=0)
    dev = ControllerDevice(joy)
    ctrl_mgr.controllers[0] = dev
    ctrl_mgr.player_map[0] = 0

    menu.open()
    assert menu.is_open is True

    # 3. Navegação via D-Pad (botão 12 = D-Pad Baixo)
    e_dpad_down = pygame.event.Event(pygame.JOYBUTTONDOWN, {"button": BTN_DPAD_DOWN, "instance_id": 0})
    menu.handle_event(e_dpad_down)
    assert menu.selected_index == 1

    # 4. Iniciar remapeamento pressionando ✕ Cruz (botão 0)
    e_confirm = pygame.event.Event(pygame.JOYBUTTONDOWN, {"button": 0, "instance_id": 0})
    menu.handle_event(e_confirm)
    assert menu.waiting_for_key_action == menu.items[1][0]

    # 5. Pressionar ○ Círculo (botão 1) cancela a espera sem remapear
    e_cancel = pygame.event.Event(pygame.JOYBUTTONDOWN, {"button": 1, "instance_id": 0})
    menu.handle_event(e_cancel)
    assert menu.waiting_for_key_action is None

    # 6. Selecionar Ataque do P1 (índice 4) e remapear via controle para R1 (botão 10)
    menu.selected_index = 4
    action_key = menu.items[4][0]
    menu.handle_event(e_confirm)
    assert menu.waiting_for_key_action == action_key

    e_remap_r1 = pygame.event.Event(pygame.JOYBUTTONDOWN, {"button": 10, "instance_id": 0})
    menu.handle_event(e_remap_r1)
    assert menu.waiting_for_key_action is None
    assert dev.custom_mappings["attack"] == 10
    assert dev.get_mapped_button_name("attack") == "R1"

    print("Teste SettingsMenu: Nomes P1/P2, D-Pad e remapeamento de Gamepad OK!")

def test_character_select_dpad_and_buttons():
    screen = CharacterSelectScreen()
    ctrl_mgr = get_controller_manager()

    # D-Pad Direita (14) move para o próximo lutador
    old_idx = screen.p1_choice_idx
    e_dpad_right = pygame.event.Event(pygame.JOYBUTTONDOWN, {"button": BTN_DPAD_RIGHT, "instance_id": 0})
    screen.handle_event(e_dpad_right)
    assert screen.p1_choice_idx == (old_idx + 1) % 6

    # Botão 2 (Quadrado) alterna modo 1P vs IA / 2P Versus
    old_mode = screen.vs_ai
    e_mode = pygame.event.Event(pygame.JOYBUTTONDOWN, {"button": 2, "instance_id": 0})
    screen.handle_event(e_mode)
    assert screen.vs_ai != old_mode

    # Botão 3 (Triângulo) abre o modal de ajuda
    e_help = pygame.event.Event(pygame.JOYBUTTONDOWN, {"button": 3, "instance_id": 0})
    screen.handle_event(e_help)
    assert screen.help_modal.is_open is True

    # Fechar modal de ajuda com ○ Círculo (botão 1)
    e_circle = pygame.event.Event(pygame.JOYBUTTONDOWN, {"button": 1, "instance_id": 0})
    screen.handle_event(e_circle)
    assert screen.help_modal.is_open is False, "○ Círculo deve fechar o modal de ajuda!"

    print("Teste CharacterSelect & HelpModal: D-Pad, Modo (▢), Guia (△) e Fechar (○) OK!")

def test_hanzo_parabolic_jump_and_tanto_rules():
    hanzo = YellowNinja(10.0, 10.0)
    enemy = RedSamurai(18.0, 10.0)
    game_map = GameMap()
    camera = Camera(10.0, 10.0)
    combat = CombatSystem()

    # 1. Com Kunai: Tanto está BLOQUEADA
    assert hanzo.has_kunai is True
    hanzo.trigger_thrust_attack(11.0, 10.0)
    assert hanzo.state == "IDLE", "Tanto deve estar bloqueada enquanto Hanzo possui a Kunai!"

    # 2. Pulo Parabólico (Ação Secundária)
    hanzo.trigger_jump(13.0, 10.0)
    assert hanzo.state == "JUMP"
    hanzo.update(0.24, game_map)
    assert hanzo.wz > 0.6, "Hanzo deve atingir altura elevada (wz > 0.6) no pulo!"

    # 3. Evasão Aérea: Corte terrestre inimigo NÃO atinge Hanzo no ar
    enemy.wx = hanzo.wx
    enemy.wy = hanzo.wy
    enemy.hitbox_active = True
    enemy.hitbox_center = (hanzo.wx, hanzo.wy)
    enemy.hitbox_radius = 1.5
    winner = combat.process_combat(enemy, hanzo, game_map, [], [], camera, [], 0.016)
    assert winner is None, "Corte no chão deve errar Hanzo enquanto ele estiver no ar (wz > 0.65)!"
    assert hanzo.is_alive is True

    # 4. Arremesso de Kunai no ar
    projs = []
    hanzo.trigger_midair_throw(15.0, 10.0, projs)
    assert hanzo.has_kunai is False, "Kunai deve ser arremessada no ar!"
    assert len(projs) == 1
    assert projs[0].wz > 0.4, "Kunai deve partir da altura do ninja no ar!"

    # 5. Ao aterrissar desarmado: Tanto LIBERADA!
    hanzo.update(0.35, game_map)
    assert hanzo.state == "IDLE"
    assert hanzo.wz == 0.0

    hanzo.trigger_thrust_attack(11.0, 10.0)
    assert hanzo.state == "ATTACK", "Tanto deve estar LIBERADA com Hanzo sem kunai!"

    print("Teste Hanzo: Pulo Parabólico, Evasão Aérea e Tanto exclusiva desarmado OK!")

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1280, 720))
    test_settings_menu_labels_and_remapping()
    test_character_select_dpad_and_buttons()
    test_hanzo_parabolic_jump_and_tanto_rules()
    print("\nTODAS AS VERIFICAÇÕES DE OPÇÕES, CONTROLE E HANZO PASSARAM COM SUCESSO!\n")
