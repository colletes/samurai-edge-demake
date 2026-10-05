"""
Suíte de testes automatizados para a Fase 3:
- Exibição Clara do D-Pad (Item 8)
- Suporte a Múltiplos Botões por Ação (Item 8)
- Prevenção de Comandos Aleatórios ao Conectar Gamepads
- Persistência em JSON (controls_config.json)
"""
import unittest
import os
import sys
import json
import pygame

# Set dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
pygame.init()

from src.input.controller_manager import (
    ControllerDevice,
    ControllerManager,
    ACTION_ATTACK,
    ACTION_SECONDARY,
    ACTION_DASH,
    ACTION_MENU,
    CONTROLLER_TYPE_DUALSENSE,
    CONTROLLER_TYPE_XBOX,
    CONTROLLER_TYPE_NINTENDO,
    CONTROLLER_TYPE_GENERIC,
)
from src.input.controls_storage import (
    load_controls_config,
    save_controls_config,
    get_default_config,
    CONFIG_PATH,
)


class MockJoystick:
    def __init__(self, name="DualSense Wireless Controller", guid="030000004c050000", num_buttons=16):
        self._name = name
        self._guid = guid
        self._buttons = [False] * num_buttons

    def get_instance_id(self): return 1
    def get_name(self): return self._name
    def get_guid(self): return self._guid
    def get_numbuttons(self): return len(self._buttons)
    def get_button(self, idx): return self._buttons[idx] if 0 <= idx < len(self._buttons) else False
    def get_numaxes(self): return 2
    def get_axis(self, idx): return 0.0
    def get_numhats(self): return 1
    def get_hat(self, idx): return (0, 0)
    def press_button(self, idx): self._buttons[idx] = True
    def release_button(self, idx): self._buttons[idx] = False


class TestPhase3ControlsAndPersistence(unittest.TestCase):
    def setUp(self):
        from src.i18n import set_lang
        set_lang("pt")
        # Backup do arquivo original de config se existir
        self.backup_config = None
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                self.backup_config = f.read()

    def tearDown(self):
        # Restaura ou remove config temporária de teste
        if self.backup_config is not None:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                f.write(self.backup_config)
        elif os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)

    def test_dpad_display_names(self):
        """Verifica se as 4 direções do D-Pad são nomeadas de forma clara e por extenso."""
        mock_joy = MockJoystick()
        dev = ControllerDevice(mock_joy)
        
        self.assertEqual(dev.get_button_name(11), "D-PAD CIMA")
        self.assertEqual(dev.get_button_name(12), "D-PAD BAIXO")
        self.assertEqual(dev.get_button_name(13), "D-PAD ESQ")
        self.assertEqual(dev.get_button_name(14), "D-PAD DIR")

        # Verifica retorno de ícone SVG para direções
        self.assertEqual(dev.get_button_svg_icon("P1_UP"), "dpad")
        self.assertEqual(dev.get_button_svg_icon(11), "dpad")

    def test_multiple_buttons_per_action(self):
        """Verifica se múltiplos botões podem ser mapeados e acionados para a mesma ação (ex: R1 e X)."""
        mock_joy = MockJoystick()
        dev = ControllerDevice(mock_joy)

        # Mapeia múltiplos botões para ação secundária: botão 0 (Cruz) e botão 10 (R1)
        dev.set_action_buttons(ACTION_SECONDARY, [0, 10])
        mapped_buttons = dev.get_action_buttons(ACTION_SECONDARY)
        self.assertIn(0, mapped_buttons)
        self.assertIn(10, mapped_buttons)

        # Ambos os botões devem ser reconhecidos como ACTION_SECONDARY
        self.assertTrue(dev.is_action_pressed(0, ACTION_SECONDARY))
        self.assertTrue(dev.is_action_pressed(10, ACTION_SECONDARY))
        self.assertFalse(dev.is_action_pressed(2, ACTION_SECONDARY))

        # Teste de is_action_down com múltiplos botões
        self.assertFalse(dev.is_action_down(ACTION_SECONDARY))
        mock_joy.press_button(10) # Pressiona R1
        self.assertTrue(dev.is_action_down(ACTION_SECONDARY))
        mock_joy.release_button(10)
        self.assertFalse(dev.is_action_down(ACTION_SECONDARY))
        mock_joy.press_button(0)  # Pressiona Cruz
        self.assertTrue(dev.is_action_down(ACTION_SECONDARY))

        # Nome exibido deve conter ambos os botões
        mapped_name = dev.get_mapped_button_name(ACTION_SECONDARY)
        self.assertIn("Cruz", mapped_name)
        self.assertIn("R1", mapped_name)

    def test_no_random_mappings_on_connect(self):
        """Verifica se controles recém-conectados usam estritamente o padrão canônico sem aleatoriedade."""
        mock_joy = MockJoystick()
        dev = ControllerDevice(mock_joy)
        
        # Padrão PlayStation deve conter exatamente [2, 10] para ataque, [0, 3] para secundária e [1, 9] para esquiva
        self.assertEqual(dev.get_action_buttons(ACTION_ATTACK), [2, 10])
        self.assertEqual(dev.get_action_buttons(ACTION_SECONDARY), [0, 3])
        self.assertEqual(dev.get_action_buttons(ACTION_DASH), [1, 9])

    def test_persistence_save_and_load_json(self):
        """Verifica se as configurações são persistidas e recarregadas corretamente em controls_config.json."""
        custom_keyboard = {
            "P1_ATTACK": pygame.K_z,
            "P1_SECONDARY": pygame.K_x,
            "P1_DASH": pygame.K_c,
        }

        # Cria ControllerManager com mapeamento customizado
        mgr = ControllerManager()
        mock_joy = MockJoystick()
        dev = ControllerDevice(mock_joy)
        dev.set_action_buttons(ACTION_SECONDARY, [0, 10])
        mgr.controllers[1] = dev
        mgr.player_map[0] = 1

        # Salva em JSON
        ok = save_controls_config(custom_keyboard, mgr, touch_mode="always")
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(CONFIG_PATH))

        # Lê do JSON
        loaded = load_controls_config()
        self.assertEqual(loaded["touch_mode"], "always")
        self.assertEqual(loaded["keyboard"]["P1_ATTACK"], pygame.K_z)
        self.assertEqual(loaded["keyboard"]["P1_SECONDARY"], pygame.K_x)
        self.assertEqual(loaded["keyboard"]["P1_DASH"], pygame.K_c)
        self.assertIn("P1", loaded["controllers"])
        self.assertEqual(loaded["controllers"]["P1"][ACTION_SECONDARY], [0, 10])


if __name__ == "__main__":
    unittest.main()
