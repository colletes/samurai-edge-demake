#!/usr/bin/env python3
"""
Testes automatizados do Hub de Opções e Submenus Dedicados (SettingsMenu).
Verifica navegação entre Hub e subscreens, separação física dos botões sem sobreposição,
e retorno ao Hub via tecla ESC e botão Voltar.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_CONTROLS
from src.ui.settings_menu import SettingsMenu
from src.ui.fonts import get_title_font, get_text_font
from src.arcade import arcade_save


def test_settings_hub_navigation():
    pygame.init()
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    f_large = get_title_font(30)
    f_mid = get_title_font(20)
    f_small = get_text_font(15)

    menu = SettingsMenu(dict(DEFAULT_CONTROLS))
    menu.open()
    menu.render(surf, f_large, f_mid, f_small)

    assert menu.current_subscreen == "HUB"
    assert len(menu.hub_cards_rects) == 4

    # 1. Verifica separação física entre botões inferiores do Hub (zero sobreposição)
    assert not menu.reset_rect.colliderect(menu.close_rect), "Botão Restaurar e Voltar não devem se sobrepor!"
    assert not menu.gallery_btn_rect.colliderect(menu.reset_rect), "Card da Galeria e Restaurar não devem se sobrepor!"
    assert not menu.gallery_btn_rect.colliderect(menu.close_rect), "Card da Galeria e Voltar não devem se sobrepor!"

    # 2. Navegação por Teclado no Hub (Up/Down/Left/Right)
    assert menu.hub_selected_index == 0  # Audiovisual
    ev_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    menu.handle_event(ev_right)
    assert menu.hub_selected_index == 1  # Gameplay

    ev_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    menu.handle_event(ev_down)
    assert menu.hub_selected_index == 3  # Galeria

    ev_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
    menu.handle_event(ev_left)
    assert menu.hub_selected_index == 2  # Controles

    # 3. Abrir Subtela CONTROLES ao pressionar Enter
    ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    menu.handle_event(ev_enter)
    assert menu.current_subscreen == "CONTROLS"

    # Renderiza subtela de controles
    menu.render(surf, f_large, f_mid, f_small)
    assert len(menu.button_rects) == 14

    # 4. Voltar ao Hub via ESC
    ev_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    menu.handle_event(ev_esc)
    assert menu.current_subscreen == "HUB", "ESC dentro de subtela deve retornar ao Hub!"

    # 5. Abrir Subtela AUDIOVISUAL via clique do mouse
    ev_click_audio = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=menu.hub_audiovisual_rect.center)
    menu.handle_event(ev_click_audio)
    assert menu.current_subscreen == "AUDIOVISUAL"

    # Voltar ao Hub via botão Voltar
    ev_click_back = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=menu.sub_back_rect.center)
    menu.handle_event(ev_click_back)
    assert menu.current_subscreen == "HUB"

    # 6. Abrir Subtela GAMEPLAY via clique do mouse
    ev_click_gameplay = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=menu.hub_gameplay_rect.center)
    menu.handle_event(ev_click_gameplay)
    assert menu.current_subscreen == "GAMEPLAY"

    # Voltar ao Hub
    menu.handle_event(ev_esc)
    assert menu.current_subscreen == "HUB"

    # 7. ESC no Hub fecha o menu
    menu.handle_event(ev_esc)
    assert not menu.is_open, "ESC no Hub Central deve fechar o menu de opções!"

    print("test_settings_hub_navigation OK")


def test_audiovisual_volume_clicks_do_not_change_language():
    """Garante que clicar nos botões de volume na subtela Audiovisual NÃO altera o idioma."""
    from src.i18n import get_saved_language_preference, save_language_setting, LANG_PT
    save_language_setting(LANG_PT)
    initial_lang = get_saved_language_preference()

    menu = SettingsMenu(dict(DEFAULT_CONTROLS))
    menu.open()
    menu.current_subscreen = "AUDIOVISUAL"

    from src.audio.sound_manager import SoundManager
    mgr = SoundManager.get_instance()
    initial_bgm = mgr.bgm_volume

    # Clicar no botão '+' do BGM
    ev_bgm_plus = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=menu.bgm_plus_rect.center)
    menu.handle_event(ev_bgm_plus)

    # Idioma DEVE permanecer inalterado
    assert get_saved_language_preference() == initial_lang, "Clicar em volume BGM não deve alterar o idioma!"
    assert mgr.bgm_volume == min(1.0, round(initial_bgm + 0.1, 2))

    # Clicar no botão '-' do BGM
    ev_bgm_minus = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=menu.bgm_minus_rect.center)
    menu.handle_event(ev_bgm_minus)
    assert get_saved_language_preference() == initial_lang
    assert mgr.bgm_volume == round(initial_bgm, 2)

    print("test_audiovisual_volume_clicks_do_not_change_language OK")


def test_controls_remapping_flow():
    """Garante que clicar numa ação ativa a espera e a tecla seguinte é atribuída corretamente."""
    menu = SettingsMenu(dict(DEFAULT_CONTROLS))
    menu.open()
    menu.current_subscreen = "CONTROLS"

    assert menu.waiting_for_key_action is None
    # Clica na primeira ação (P1_UP)
    first_rect, _ = menu.button_rects[0]
    ev_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=first_rect.center)
    menu.handle_event(ev_click)

    assert menu.waiting_for_key_action == "P1_UP", "Clicar na linha de controle deve aguardar entrada!"

    # Pressiona tecla K_w
    ev_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)
    menu.handle_event(ev_key)

    assert menu.waiting_for_key_action is None
    assert menu.controls["P1_UP"] == pygame.K_w, "P1_UP deve ter sido remapeado para K_w!"

    print("test_controls_remapping_flow OK")


if __name__ == "__main__":
    test_settings_hub_navigation()
    test_audiovisual_volume_clicks_do_not_change_language()
    test_controls_remapping_flow()
