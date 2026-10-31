"""
Teste da edição demo: só Kenshi, Valerius, Hendrika e Hanzo, suas arenas, e sem Arcade/Galeria.
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_demo_edition.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src import edition
from src.config import (
    CHAR_KENSHIN, CHAR_VALERIUS, CHAR_HENDRIKA, CHAR_HANZO,
    ARENA_BAMBOO, ARENA_GOTHIC_CEMETERY, ARENA_DEJIMA, ARENA_IGA
)
from src.i18n import set_lang
from src.roster import ROSTER_ORDER, ARENA_BY_FIGHTER
from src.ui.character_select import CharacterSelectScreen
from src.ui.fonts import get_title_font, get_text_font
from src.ui.pause_menu import PauseMenu, ACTION_ARENA
from src.ui.title_screen import SumieTitleScreen
from src.ui.settings_menu import SettingsMenu


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="", scancode=0)


def with_demo(value):
    if value:
        os.environ["SAMURAI_EDGE_DEMO"] = "1"
    else:
        os.environ.pop("SAMURAI_EDGE_DEMO", None)


def test_edition_constants():
    assert edition.DEMO_FIGHTERS == (CHAR_KENSHIN, CHAR_VALERIUS, CHAR_HENDRIKA, CHAR_HANZO)
    assert edition.DEMO_ARENAS == (ARENA_BAMBOO, ARENA_GOTHIC_CEMETERY, ARENA_DEJIMA, ARENA_IGA)
    assert ARENA_BY_FIGHTER[CHAR_KENSHIN] == ARENA_BAMBOO
    assert ARENA_BY_FIGHTER[CHAR_VALERIUS] == ARENA_GOTHIC_CEMETERY
    assert ARENA_BY_FIGHTER[CHAR_HENDRIKA] == ARENA_DEJIMA
    assert ARENA_BY_FIGHTER[CHAR_HANZO] == ARENA_IGA
    with_demo(False)
    assert not edition.is_demo() or edition.IS_DEMO
    with_demo(True)
    assert edition.is_demo()
    print("  [OK] Constantes da demo: Kenshi, Valerius, Hendrika, Hanzo e suas 4 arenas.", flush=True)


def test_title_blocks_arcade():
    with_demo(True)
    title = SumieTitleScreen()
    title.selected_mode = 0
    assert title.handle_event(key(pygame.K_RETURN)) is None and title.notice_timer > 0
    surf = pygame.Surface((1280, 720))
    for lang in ("pt", "en"):
        set_lang(lang)
        title.render(surf, get_title_font(40), get_title_font(24), get_text_font(16))
    set_lang("pt")
    with_demo(False)
    assert SumieTitleScreen().handle_event(key(pygame.K_UP)) is None
    full = SumieTitleScreen()
    full.selected_mode = 0
    assert full.handle_event(key(pygame.K_RETURN)) == "ARCADE", "a versão completa mantém o Arcade"
    print("  [OK] Demo: o Arcade fica bloqueado com aviso; a versão completa o mantém.", flush=True)


def test_character_select_demo_four():
    with_demo(True)
    cs = CharacterSelectScreen()
    assert cs.characters[cs.p1_choice_idx]["id"] == CHAR_KENSHIN
    assert cs.characters[cs.p2_choice_idx]["id"] == CHAR_VALERIUS
    allowed = {i for i in range(len(cs.characters)) if not cs.is_locked(i)}
    expected = {
        ROSTER_ORDER.index(CHAR_KENSHIN),
        ROSTER_ORDER.index(CHAR_VALERIUS),
        ROSTER_ORDER.index(CHAR_HENDRIKA),
        ROSTER_ORDER.index(CHAR_HANZO)
    }
    assert allowed == expected, f"Esperado {expected}, obteve {allowed}"
    for start in allowed:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            assert cs._grid_step(start, dx, dy) in allowed, (start, dx, dy)
    surf = pygame.Surface((1280, 720))
    for lang in ("pt", "en"):
        set_lang(lang)
        cs.render(surf, get_title_font(40), get_title_font(24), get_text_font(16))
        locked_rects = [r for i, r in enumerate(cs.card_rects) if i not in allowed]
        assert all(r.w == 0 for r in locked_rects), "cartas bloqueadas não recebem clique"
        assert all(cs.card_rects[i].w > 0 for i in allowed)
    set_lang("pt")
    cs.vs_ai = False
    cs.p1_choice_idx = ROSTER_ORDER.index(CHAR_KENSHIN)
    cs.p2_choice_idx = ROSTER_ORDER.index(CHAR_VALERIUS)
    assert cs.get_selected_characters() == (CHAR_KENSHIN, CHAR_VALERIUS, False), "2P com Kenshi e Valerius"
    with_demo(False)
    full = CharacterSelectScreen()
    assert not any(full.is_locked(i) for i, c in enumerate(full.characters) if c.get("ready", True))
    print("  [OK] Demo: só Kenshi, Valerius, Hendrika e Hanzo são selecionáveis.", flush=True)


def test_pause_menu_has_no_arena_item():
    with_demo(True)
    pm = PauseMenu()
    snap = pygame.Surface((1280, 720))
    pm.open(snap, demo=True)
    assert ACTION_ARENA not in [a for _, a in pm.items]
    pm.open(snap)
    assert ACTION_ARENA in [a for _, a in pm.items]
    with_demo(False)
    print("  [OK] A pausa da demo não oferece troca de cenário.", flush=True)


def test_settings_hub_blocks_gallery_in_demo():
    with_demo(True)
    sm = SettingsMenu({"master": 1.0, "sfx": 1.0, "bgm": 1.0}, "normal", {})
    sm.open()
    # Pressiona para selecionar o card da Galeria (índice 3)
    sm.hub_selected_index = 3
    sm._activate_hub_index(3)
    assert not sm.request_gallery, "A galeria deve permanecer bloqueada na demo"
    with_demo(False)
    print("  [OK] O Hub de Opções bloqueia a Galeria na edição demo.", flush=True)


def test_main_routes_demo_without_arena_screen():
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    block = src.split("if game_state == STATE_ARENA_SELECT:")[1].split("arena_select_screen.update")[0]
    assert "is_demo()" in block and "DEMO_ARENA" in block and "STATE_CHAR_SELECT" in block
    print("  [OK] No fluxo da demo a tela de cenário é pulada e entra direto na arena do P1.", flush=True)


if __name__ == "__main__":
    test_edition_constants()
    test_title_blocks_arcade()
    test_character_select_demo_four()
    test_pause_menu_has_no_arena_item()
    test_settings_hub_blocks_gallery_in_demo()
    test_main_routes_demo_without_arena_screen()
    print("Todos os testes da edição demo passaram com 100%!", flush=True)
