"""
Suíte de testes automatizados para Controles (Gamepads) e Touchscreen:
1. Detecção precisa de marcas e modelos de controle (Xbox, DualShock 4, DualSense PS5, Switch, Genérico).
2. Geração correta de glifos/ícones para cada controle (ex: A/B vs ✕/○ vs 1/2).
3. Atribuição e mapeamento de P1 e P2.
4. Matemática e comportamento do Joystick Virtual (deadzone, clamping, normalização vetorial).
5. Funcionamento dos botões de toque (tap, hold para recarga contínua, reset por frame).
6. Multi-touch real (dois dedos simultâneos: movimentação + ataque).
7. Viewport responsivo e conversor de coordenadas (DisplayScaler) em resoluções mobile ultrawide.
8. Funções de execução de combate e mira direcional integrada.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame
from src.input.controller_manager import (
    detect_controller_type,
    CONTROLLER_TYPE_XBOX,
    CONTROLLER_TYPE_DUALSHOCK,
    CONTROLLER_TYPE_DUALSENSE,
    CONTROLLER_TYPE_NINTENDO,
    CONTROLLER_TYPE_GENERIC,
    ACTION_ATTACK,
    ACTION_DASH,
    ACTION_MENU,
    ACTION_CONFIRM,
    ACTION_CANCEL,
    ControllerManager,
    ControllerDevice
)
from src.input.touch_controls import VirtualJoystick, TouchButton, TouchControls, TOUCH_MODE_AUTO, TOUCH_MODE_ALWAYS, TOUCH_MODE_OFF
from src.input.display_scaler import DisplayScaler
from src.entities.red_samurai import RedSamurai
from src.entities.rifleman import Rifleman
from main import get_player_aim_target, execute_fighter_attack, execute_fighter_dash

def test_controller_detection():
    # 1. Xbox Controllers
    xbox_names = [
        "Xbox 360 Controller",
        "Xbox One Wireless Controller",
        "Xbox Series X Controller",
        "Microsoft X-Box 360 pad",
        "XInput Controller"
    ]
    for name in xbox_names:
        c_type = detect_controller_type(name)
        assert c_type == CONTROLLER_TYPE_XBOX, f"Falha na detecção Xbox para: {name} (detectado: {c_type})"

    # GUID da Microsoft (045e)
    assert detect_controller_type("Generic Controller", guid="030000005e040000") == CONTROLLER_TYPE_XBOX

    # 2. PlayStation Controllers (DualSense PS5 vs DualShock 4 PS4)
    ps5_names = [
        "PS5 Controller",
        "DualSense Wireless Controller",
        "Sony Interactive Entertainment Wireless Controller (PS5)"
    ]
    for name in ps5_names:
        c_type = detect_controller_type(name)
        assert c_type == CONTROLLER_TYPE_DUALSENSE, f"Falha na detecção DualSense para: {name} (detectado: {c_type})"

    ps4_names = [
        "PS4 Controller",
        "DualShock 4 Wireless Controller",
        "Sony DualShock 4"
    ]
    for name in ps4_names:
        c_type = detect_controller_type(name)
        assert c_type == CONTROLLER_TYPE_DUALSHOCK, f"Falha na detecção DualShock 4 para: {name} (detectado: {c_type})"

    # GUID da Sony (054c)
    assert detect_controller_type("Wireless Controller", guid="030000004c050000") in (CONTROLLER_TYPE_DUALSHOCK, CONTROLLER_TYPE_DUALSENSE)

    # 3. Nintendo Controllers
    switch_names = [
        "Nintendo Switch Pro Controller",
        "Joy-Con (L/R)"
    ]
    for name in switch_names:
        c_type = detect_controller_type(name)
        assert c_type == CONTROLLER_TYPE_NINTENDO, f"Falha na detecção Nintendo para: {name}"

    # 4. Controles Genéricos
    generic_names = [
        "USB Gamepad",
        "DragonRise Inc. Generic USB Joystick",
        "Twin USB Joystick",
        "Retro Arcade Stick"
    ]
    for name in generic_names:
        c_type = detect_controller_type(name)
        assert c_type == CONTROLLER_TYPE_GENERIC, f"Falha na detecção Genérico para: {name}"

    print("Teste 1: Detecção de Xbox, DualShock 4, DualSense PS5, Switch e Genéricos OK!")

def test_controller_glyphs():
    # Mocking joystick para testar ControllerDevice
    class MockJoystick:
        def get_instance_id(self): return 1
        def get_name(self): return "Xbox Wireless Controller"
        def get_guid(self): return "030000005e040000"

    dev_xbox = ControllerDevice(MockJoystick())
    assert dev_xbox.controller_type == CONTROLLER_TYPE_XBOX
    assert dev_xbox.get_button_glyph(ACTION_ATTACK) == "X"
    assert dev_xbox.get_button_glyph(ACTION_DASH) == "A"
    assert dev_xbox.get_button_glyph(ACTION_CONFIRM) == "A"
    assert dev_xbox.get_button_glyph(ACTION_CANCEL) == "B"

    # DualSense
    class MockPS5Joystick:
        def get_instance_id(self): return 2
        def get_name(self): return "DualSense Wireless Controller"
        def get_guid(self): return "030000004c050000"

    dev_ps5 = ControllerDevice(MockPS5Joystick())
    assert dev_ps5.controller_type == CONTROLLER_TYPE_DUALSENSE
    assert dev_ps5.get_button_glyph(ACTION_ATTACK) == "▢"
    assert dev_ps5.get_button_glyph(ACTION_DASH) == "✕"
    assert dev_ps5.get_button_glyph(ACTION_CONFIRM) == "✕"
    assert dev_ps5.get_button_glyph(ACTION_CANCEL) == "○"
    assert dev_ps5.get_button_glyph(ACTION_MENU) == "Options"

    # Verificação de Ações Pressionadas para PS5 (SDL GameController padrão macOS)
    assert dev_ps5.is_action_pressed(2, ACTION_ATTACK)  # ▢ Quadrado
    assert dev_ps5.is_action_pressed(10, ACTION_ATTACK) # R1
    assert dev_ps5.is_action_pressed(0, ACTION_DASH)    # ✕ Cruz
    assert dev_ps5.is_action_pressed(0, ACTION_CONFIRM) # ✕ Cruz
    assert dev_ps5.is_action_pressed(1, ACTION_CANCEL)  # ○ Círculo
    assert dev_ps5.is_action_pressed(6, ACTION_MENU)    # Options

    print("Teste 2: Mapeamento de Glifos Visuais contextuais e ações padronizadas OK!")

def test_virtual_joystick():
    joy = VirtualJoystick(base_x=160, base_y=570, radius=80, knob_radius=36)
    assert joy.dx == 0.0 and joy.dy == 0.0
    assert not joy.is_active

    # 1. Toque inicial na zona morta (deadzone = 14px)
    joy.on_touch_down(finger_id=1, vx=160, vy=570)
    assert joy.is_active
    joy.on_touch_motion(finger_id=1, vx=165, vy=575) # distância aprox 7px < deadzone
    assert joy.dx == 0.0 and joy.dy == 0.0

    # 2. Movimento para a direita além da deadzone
    joy.on_touch_motion(finger_id=1, vx=220, vy=570) # delta_x = 60px
    assert joy.dx > 0.5
    assert abs(joy.dy) < 0.001

    # 3. Movimento além do raio máximo (clamping)
    joy.on_touch_motion(finger_id=1, vx=300, vy=570) # delta_x = 140px > raio 80px
    assert joy.dx == 1.0 # Clamped em 1.0
    assert joy.knob_x == joy.center_x + joy.radius

    # 4. Soltar o toque
    joy.on_touch_up(finger_id=1)
    assert not joy.is_active
    assert joy.dx == 0.0 and joy.dy == 0.0

    print("Teste 3: Joystick Virtual (deadzone, clamping em raio máximo e retorno) OK!")

def test_touch_button_tap_and_hold():
    btn = TouchButton(cx=1000, cy=600, radius=50, label="ATK")
    assert not btn.is_down
    assert not btn.just_pressed

    # 1. Toque inicial
    btn.on_touch_down(finger_id=2, vx=1010, vy=605)
    assert btn.is_down
    assert btn.just_pressed

    # 2. Próximo frame: just_pressed limpo, mas continues is_down (hold)
    btn.reset_frame_state()
    assert not btn.just_pressed
    assert btn.is_down

    # 3. Soltar toque
    btn.on_touch_up(finger_id=2)
    assert not btn.is_down

    print("Teste 4: Botões Touch (disparo instantâneo e hold contínuo) OK!")

def test_multi_touch_tracking():
    tc = TouchControls()
    scaler = DisplayScaler(1280, 720)

    # Dedo 1 (Polegar Esquerdo no Joystick): FINGERDOWN
    ev_f1 = pygame.event.Event(pygame.FINGERDOWN, finger_id=1, x=160/1280, y=570/720)
    consumed_f1 = tc.handle_event(ev_f1, scaler)
    assert consumed_f1
    assert tc.joystick.is_active

    # Dedo 1 move para cima: FINGERMOTION
    ev_f1_move = pygame.event.Event(pygame.FINGERMOTION, finger_id=1, x=160/1280, y=500/720)
    tc.handle_event(ev_f1_move, scaler)
    assert tc.get_movement()[1] < -0.5 # Movendo para cima

    # Dedo 2 (Polegar Direito no Botão de Ataque): FINGERDOWN Simultâneo!
    atk_x, atk_y = tc.btn_attack.cx, tc.btn_attack.cy
    ev_f2 = pygame.event.Event(pygame.FINGERDOWN, finger_id=2, x=atk_x/1280, y=atk_y/720)
    consumed_f2 = tc.handle_event(ev_f2, scaler)
    assert consumed_f2
    assert tc.is_attack_just_pressed()

    # Dedo 1 continua ativo enquanto Dedo 2 dispara o ataque!
    assert tc.joystick.is_active
    assert tc.btn_attack.is_down

    # Soltar Dedo 2
    ev_f2_up = pygame.event.Event(pygame.FINGERUP, finger_id=2, x=atk_x/1280, y=atk_y/720)
    tc.handle_event(ev_f2_up, scaler)
    assert not tc.btn_attack.is_down
    assert tc.joystick.is_active # Joystick continua funcionando perfeitamente!

    # Soltar Dedo 1
    ev_f1_up = pygame.event.Event(pygame.FINGERUP, finger_id=1, x=160/1280, y=500/720)
    tc.handle_event(ev_f1_up, scaler)
    assert not tc.joystick.is_active

    print("Teste 5: Multi-Touch simultâneo real (Movimento + Ataque sem interferência) OK!")

def test_display_scaler_and_aspect_ratio():
    scaler = DisplayScaler(virtual_width=1280, virtual_height=720)

    # 1. Resolução padrão 1280x720 (escala 1.0, sem offset)
    scaler.update_window_size(1280, 720)
    assert scaler.scale == 1.0
    assert scaler.offset_x == 0 and scaler.offset_y == 0
    vx, vy = scaler.screen_to_virtual(640, 360)
    assert math.isclose(vx, 640, abs_tol=0.1) and math.isclose(vy, 360, abs_tol=0.1)

    # 2. Tela Ultrawide Mobile (ex: 2400 x 1080 - Proporção 20:9)
    scaler.update_window_size(2400, 1080)
    assert scaler.scale == 1080 / 720 # 1.5x
    assert scaler.offset_x > 0 # Barras pretas laterais (Pillarbox)
    assert scaler.offset_y == 0

    # Ponto no centro da tela física deve mapear para o centro virtual (640, 360)
    cvx, cvy = scaler.screen_to_virtual(1200, 540)
    assert math.isclose(cvx, 640, abs_tol=0.1)
    assert math.isclose(cvy, 360, abs_tol=0.1)

    print("Teste 6: DisplayScaler (Pillarbox/Letterbox para telas ultrawide mobile) OK!")

def test_combat_execution_helpers():
    kenshin = RedSamurai(10.0, 10.0)
    projectiles = []
    particles = []
    decoys = []

    # Ataque com mira direcional calculada
    aim_x, aim_y = get_player_aim_target(kenshin, {}, "P1", distance=4.0, move_dir=(1.0, 0.0))
    execute_fighter_attack(kenshin, aim_x, aim_y, projectiles, particles)
    assert kenshin.state == "ATTACK"

    # Dash (Shukuchi no Kenshin)
    kenshin2 = RedSamurai(10.0, 10.0)
    execute_fighter_dash(kenshin2, aim_x, aim_y, 1.0, 0.0, projectiles, particles, decoys)
    assert kenshin2.state == "SHUKUCHI"

    # Teste do Rifleman iniciando carregado
    teppo = Rifleman(10.0, 10.0)
    assert teppo.has_ammo is True
    teppo.has_ammo = False
    teppo.powder_level = 0.0
    teppo.trigger_reload_hold()
    assert teppo.is_reloading

    # Teste de Tomoe (disparo instantâneo sem windup e corda sem cooldown)
    from src.entities.kyudo_archer import KyudoArcher
    tomoe = KyudoArcher(10.0, 10.0)
    assert tomoe.draw_duration == 0.0
    assert tomoe.rope_cooldown == 0.0
    tomoe.trigger_bow_draw(15.0, 10.0, projectiles)
    assert len(projectiles) > 0 # Flecha disparada imediatamente

    print("Teste 7: Execução unificada de ataques, dash, mira manual e ajustes Tomoe/Teppo OK!")

def run_all_tests():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1280, 720))

    print("\n=======================================================")
    print("INICIANDO SUÍTE DE TESTES: CONTROLES, TOUCH & SCALER")
    print("=======================================================")
    test_controller_detection()
    test_controller_glyphs()
    test_virtual_joystick()
    test_touch_button_tap_and_hold()
    test_multi_touch_tracking()
    test_display_scaler_and_aspect_ratio()
    test_combat_execution_helpers()
    print("=======================================================")
    print("TODOS OS 7 TESTES DE CONTROLE E TOUCH PASSARAM COM 100%!")
    print("=======================================================\n")

if __name__ == "__main__":
    run_all_tests()
