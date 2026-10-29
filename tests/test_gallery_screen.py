"""Testes da Tela da Galeria de Honra (Artes, Vídeos e Músicas) e integração nas Opções."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_CONTROLS
from src.ui.gallery_screen import GalleryScreen, TAB_IMAGES, TAB_VIDEOS, TAB_MUSIC, KARAOKE_TRACKS
from src.ui.settings_menu import SettingsMenu
from src.arcade import arcade_save


def test_gallery_screen_initialization_and_assets():
    pygame.init()
    g = GalleryScreen()
    assert len(g.concept_images) >= 50, f"Deveria ter carregado artes conceituais: {len(g.concept_images)}"
    assert len(g.music_tracks) >= 25, f"Deveria ter carregado faixas de música: {len(g.music_tracks)}"
    assert "Samurai Edge- Opening Theme" in g.music_tracks
    assert "Samurai Edge - Closing Theme" in g.music_tracks


def test_gallery_tab_navigation():
    pygame.init()
    g = GalleryScreen()
    g.open()
    assert g.current_tab == TAB_IMAGES

    # Avançar aba com E
    ev_e = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
    g.handle_event(ev_e)
    assert g.current_tab == TAB_VIDEOS

    g.handle_event(ev_e)
    assert g.current_tab == TAB_MUSIC

    # Voltar aba com Q
    ev_q = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q)
    g.handle_event(ev_q)
    assert g.current_tab == TAB_VIDEOS


def test_gallery_images_navigation():
    pygame.init()
    g = GalleryScreen()
    g.open()
    g.current_tab = TAB_IMAGES
    assert g.image_index == 0

    ev_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    g.handle_event(ev_right)
    assert g.image_index == 1

    ev_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
    g.handle_event(ev_left)
    assert g.image_index == 0


def test_gallery_video_selection():
    pygame.init()
    g = GalleryScreen()
    g.open()
    g.current_tab = TAB_VIDEOS
    g.video_index = 0

    ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    res = g.handle_event(ev_enter)
    assert res == "OPEN_OPENING_VIDEO"

    ev_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    g.handle_event(ev_down)
    assert g.video_index == 1
    res2 = g.handle_event(ev_enter)
    assert res2 == "OPEN_CREDITS_SLIDESHOW"


def test_gallery_music_player_and_karaoke_badge():
    pygame.init()
    g = GalleryScreen()
    g.open()
    g.current_tab = TAB_MUSIC

    # Encontra faixa com letra e verifica suporte
    opening_idx = g.music_tracks.index("Samurai Edge- Opening Theme")
    assert "Samurai Edge- Opening Theme" in KARAOKE_TRACKS
    g.music_index = opening_idx

    scr = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    g.render(scr)
    # Renderizou sem erros

    # Verifica botões de transporte presentes e com dimensões
    assert g.prev_track_btn_rect.width > 0, "Botão Prev deve existir"
    assert g.play_btn_rect.width > 0, "Botão Play deve existir"
    assert g.stop_btn_rect.width > 0, "Botão Stop deve existir"
    assert g.next_track_btn_rect.width > 0, "Botão Next deve existir"
    assert g.loop_btn_rect.width > 0, "Botão Loop deve existir"
    assert g.time_bar_rect.width > 0, "Barra de busca / tempo deve existir e ser clicável"
    assert g.lyrics_display_rect.width > 0, "Área de letras/informações deve existir"
    assert len(g.music_item_rects) == 7, "Deve renderizar 7 faixas na lista"

    # Testa clique na barra de tempo (seek)
    seek_x = g.time_bar_rect.x + int(g.time_bar_rect.width * 0.5)
    seek_y = g.time_bar_rect.centery
    ev_seek = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(seek_x, seek_y))
    g.handle_event(ev_seek)
    assert g.music_playback_time > 10.0, f"Clique no meio da barra deve avançar para posição > 10s: {g.music_playback_time}"
    assert g.is_playing_music is True, "Seek deve iniciar a música na nova posição"

    # Testa Play / Pause toggle
    ev_pause = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=g.play_btn_rect.center)
    g.handle_event(ev_pause)
    assert g.is_playing_music is False, "Botão Play/Pause deve pausar quando estava tocando"
    assert g.is_paused is True, "Estado deve ser pausado"

    ev_unpause = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=g.play_btn_rect.center)
    g.handle_event(ev_unpause)
    assert g.is_playing_music is True, "Botão Play/Pause deve retomar reprodução"
    assert g.is_paused is False

    # Testa avanço de faixa via Next e retorno via Prev
    cur_idx = g.music_index
    ev_next_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=g.next_track_btn_rect.center)
    g.handle_event(ev_next_click)
    assert g.music_index == (cur_idx + 1) % len(g.music_tracks), "Botão Next deve avançar faixa!"

    ev_prev_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=g.prev_track_btn_rect.center)
    g.handle_event(ev_prev_click)
    assert g.music_index == cur_idx, "Botão Prev deve retornar faixa!"

    # Testa Stop
    ev_stop_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=g.stop_btn_rect.center)
    g.handle_event(ev_stop_click)
    assert g.is_playing_music is False, "Botão Stop deve parar reprodução!"
    assert g.music_playback_time == 0.0, "Botão Stop deve resetar o tempo para 0"

    # Testa Loop toggle
    init_loop = g.is_looping
    ev_loop_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=g.loop_btn_rect.center)
    g.handle_event(ev_loop_click)
    assert g.is_looping == (not init_loop), "Botão Loop deve alternar repetição!"


def test_settings_menu_gallery_button_integration():
    pygame.init()
    menu = SettingsMenu(DEFAULT_CONTROLS.copy())
    scr = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    from src.ui.fonts import get_title_font, get_text_font
    menu.open()
    menu.render(scr, get_title_font(32), get_title_font(20), get_text_font(14))
    assert menu.gallery_btn_rect.width > 0, "Botão da galeria deveria ter dimensões no render"

    # Se a galeria estiver desbloqueada, clicar no botão ativa request_gallery
    save_data = arcade_save.empty_data()
    arcade_save.unlock_gallery(save_data)
    arcade_save.save(save_data)

    ev_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=menu.gallery_btn_rect.center)
    menu.handle_event(ev_click)
    assert menu.request_gallery is True, "Deveria solicitar abertura da galeria ao clicar"


def test_gallery_screen_render():
    pygame.init()
    scr = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    g = GalleryScreen()
    g.open()

    from src.ui.fonts import get_title_font, get_text_font
    f_l = get_title_font(32)
    f_m = get_title_font(20)
    f_s = get_text_font(14)

    # Render with just surface
    g.render(scr)

    # Render with fonts (main.py style)
    g.render(scr, f_l, f_m, f_s)

    # Render other tabs
    g.current_tab = TAB_VIDEOS
    g.render(scr, f_l, f_m, f_s)

    g.current_tab = TAB_MUSIC
    g.render(scr, f_l, f_m, f_s)


if __name__ == "__main__":
    test_gallery_screen_initialization_and_assets()
    test_gallery_tab_navigation()
    test_gallery_images_navigation()
    test_gallery_video_selection()
    test_gallery_music_player_and_karaoke_badge()
    test_settings_menu_gallery_button_integration()
    test_gallery_screen_render()
    print("test_gallery_screen OK")
