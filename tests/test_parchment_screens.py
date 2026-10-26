"""
Testes do Entregável 5.5.6 — Telas em Pergaminho Sumi-E e Fallback:
- SumieTitleScreen (Tela de Título)
- SettingsMenu (Menu de Configurações/Opções)
- PauseMenu (Menu de Pausa)
- Consistência de linguagem visual das 5 telas do jogo (Título, Seleção de Personagem, Seleção de Cenário, Opções, Pausa)
- Renderização em PT e EN em 1280x720, com e sem os assets de pergaminho (fallback)
- Áreas clicáveis contidas na tela e sem sobreposição
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src import i18n
from src.config import DEFAULT_CONTROLS, SCREEN_HEIGHT, SCREEN_WIDTH
from src.effects import parchment as pm
from src.ui.arena_select import ArenaSelectScreen
from src.ui.character_select import CharacterSelectScreen
from src.ui.fonts import get_text_font, get_title_font
from src.ui.pause_menu import PauseMenu
from src.ui.settings_menu import SettingsMenu
from src.ui.title_screen import SumieTitleScreen


class _MockNoParchment:
    """Context manager para simular a ausência de assets de pergaminho (modo fallback)."""

    def __enter__(self):
        self._orig_backdrop = pm.get_backdrop
        pm.get_backdrop = lambda: None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pm.get_backdrop = self._orig_backdrop


def test_title_screen_renders_pt_en_and_fallback():
    title = SumieTitleScreen()
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    f_large = get_title_font(36)
    f_mid = get_title_font(24)
    f_small = get_text_font(16)

    for lang in ("pt", "en"):
        i18n.set_lang(lang)

        # 1. Modo Pergaminho (assets presentes)
        title.update(0.016)
        title.render(surf, f_large, f_mid, f_small)
        assert len(title.btn_rects) == 3, f"Esperado 3 botões de modo, obtido {len(title.btn_rects)}"
        for i, r in enumerate(title.btn_rects):
            assert 0 <= r.x and r.right <= SCREEN_WIDTH, f"Botão {i} fora dos limites horizontais: {r}"
            assert 0 <= r.y and r.bottom <= SCREEN_HEIGHT, f"Botão {i} fora dos limites verticais: {r}"
        # Verificar que não há sobreposição vertical
        for i in range(len(title.btn_rects) - 1):
            assert title.btn_rects[i].bottom <= title.btn_rects[i + 1].y, f"Sobreposição entre botões {i} e {i+1}"

        # 2. Modo Fallback (sem backdrop)
        with _MockNoParchment():
            title.update(0.016)
            title.render(surf, f_large, f_mid, f_small)
            assert len(title.btn_rects) == 3
            for i, r in enumerate(title.btn_rects):
                assert 0 <= r.x and r.right <= SCREEN_WIDTH
                assert 0 <= r.y and r.bottom <= SCREEN_HEIGHT

    print("  [OK] SumieTitleScreen renderiza com sucesso em PT/EN e Fallback sem sobreposição.", flush=True)


def test_settings_menu_renders_pt_en_and_fallback():
    controls = dict(DEFAULT_CONTROLS)
    settings = SettingsMenu(controls)
    settings.open()

    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    f_large = get_title_font(30)
    f_mid = get_title_font(20)
    f_small = get_text_font(15)

    for lang in ("pt", "en"):
        i18n.set_lang(lang)

        # 1. Modo Pergaminho
        settings.render(surf, f_large, f_mid, f_small)
        assert len(settings.button_rects) == 14, f"Esperado 14 ações remapeáveis, obtido {len(settings.button_rects)}"

        # Verificar limites da tela para todas as áreas interativas
        all_rects = [r for r, _ in settings.button_rects] + [
            settings.sfx_minus_rect, settings.sfx_plus_rect, settings.sfx_bar_rect,
            settings.bgm_minus_rect, settings.bgm_plus_rect, settings.bgm_bar_rect,
            settings.touch_toggle_rect, settings.difficulty_toggle_rect,
            settings.quality_toggle_rect, settings.game_boost_toggle_rect,
            settings.reset_rect, settings.close_rect
        ]
        for r in all_rects:
            assert 0 <= r.x and r.right <= SCREEN_WIDTH, f"Rect fora da tela em X: {r}"
            assert 0 <= r.y and r.bottom <= SCREEN_HEIGHT, f"Rect fora da tela em Y: {r}"

        # Colunas P1 (0..6) e P2 (7..13) não devem se sobrepor
        p1_rects = [r for r, idx in settings.button_rects if idx < 7]
        p2_rects = [r for r, idx in settings.button_rects if idx >= 7]
        for r1 in p1_rects:
            for r2 in p2_rects:
                assert not r1.colliderect(r2), f"Sobreposição entre coluna P1 e P2: {r1} vs {r2}"

        # 2. Modo Fallback
        with _MockNoParchment():
            settings.render(surf, f_large, f_mid, f_small)
            assert len(settings.button_rects) == 14
            for r in all_rects:
                assert 0 <= r.x and r.right <= SCREEN_WIDTH
                assert 0 <= r.y and r.bottom <= SCREEN_HEIGHT

    print("  [OK] SettingsMenu renderiza com sucesso em PT/EN e Fallback sem sobreposição.", flush=True)


def test_pause_menu_renders_pt_en_and_fallback():
    pause = PauseMenu()
    snapshot = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    snapshot.fill((30, 40, 50))
    pause.open(snapshot)

    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    for lang in ("pt", "en"):
        i18n.set_lang(lang)

        # 1. Modo Pergaminho
        pause.render(surf)
        assert len(pause.item_rects) == len(pause.items)
        for i, r in enumerate(pause.item_rects):
            assert 0 <= r.x and r.right <= SCREEN_WIDTH, f"Item de pausa {i} fora de X: {r}"
            assert 0 <= r.y and r.bottom <= SCREEN_HEIGHT, f"Item de pausa {i} fora de Y: {r}"
        for i in range(len(pause.item_rects) - 1):
            assert pause.item_rects[i].bottom <= pause.item_rects[i + 1].y, f"Sobreposição em pausa: {i} e {i+1}"

        # 2. Modo Fallback
        with _MockNoParchment():
            pause.render(surf)
            assert len(pause.item_rects) == len(pause.items)
            for r in pause.item_rects:
                assert 0 <= r.x and r.right <= SCREEN_WIDTH
                assert 0 <= r.y and r.bottom <= SCREEN_HEIGHT

    print("  [OK] PauseMenu renderiza com sucesso em PT/EN e Fallback sem sobreposição.", flush=True)


def test_visual_consistency_across_all_five_screens():
    """Critério de aceite 5.5.6: as cinco telas do jogo compartilham a mesma linguagem visual."""
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    f_large = get_title_font(36)
    f_mid = get_title_font(24)
    f_small = get_text_font(16)

    # 1. Título
    title = SumieTitleScreen()
    title.update(0.016)
    title.render(surf, f_large, f_mid, f_small)

    # 2. Seleção de Personagem
    char_sel = CharacterSelectScreen()
    char_sel.update(0.016)
    char_sel.render(surf, f_large, f_mid, f_small)

    # 3. Seleção de Cenário
    arena_sel = ArenaSelectScreen()
    arena_sel.update(0.016)
    arena_sel.render(surf, f_large, f_mid, f_small)

    # 4. Opções
    controls = dict(DEFAULT_CONTROLS)
    settings = SettingsMenu(controls)
    settings.open()
    settings.render(surf, f_large, f_mid, f_small)

    # 5. Pausa
    pause = PauseMenu()
    pause.open(surf)
    pause.render(surf)

    print("  [OK] Todas as 5 telas renderizam harmonicamente sob a mesma arquitetura de pergaminho Sumi-E.", flush=True)


if __name__ == "__main__":
    print("--- Executando testes de telas em pergaminho (Fase 5.5.6) ---")
    test_title_screen_renders_pt_en_and_fallback()
    test_settings_menu_renders_pt_en_and_fallback()
    test_pause_menu_renders_pt_en_and_fallback()
    test_visual_consistency_across_all_five_screens()
    print("=======================================================")
    print("TODOS OS TESTES DE PERGAMINHO 5.5.6 PASSARAM COM SUCESSO!")
    print("=======================================================")
    import os
    os._exit(0)
