"""
Teste de regressão para transparência de fontes e ausência de bounding boxes / caixas opacas
em overlays de texto, finishers (Kurosawa Sumi-E), callouts de combate e marcadores.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
pygame.init()

from src.effects.cinematic_director import CinematicDirector
from src.ui.fonts import get_text_font, get_title_font
from src.ui.font_manager import render_text_fx
from src.effects.parchment import render_ink

def test_kanji_overlay_transparency():
    cd = CinematicDirector()
    cd._build_kanji_overlay(death_style="DUAL_IMPALE_X_SPREAD")
    surf = cd.cached_kanji_surf
    assert surf is not None
    assert surf.get_flags() & pygame.SRCALPHA

    # O topo esquerdo do overlay (fora do selo) deve ser 100% transparente (alpha == 0)
    # e NÃO deve conter caixa branca ou preta opaca
    top_left_col = surf.get_at((0, 0))
    assert top_left_col.a == 0, f"Pixel em (0,0) deveria ser transparente, obtido {top_left_col}"

    # Simular fading com BLEND_RGBA_MULT
    for alpha in (255, 180, 80):
        scaled = surf.copy()
        if alpha < 255:
            fade_mask = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
            fade_mask.fill((255, 255, 255, alpha))
            scaled.blit(fade_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Blit sobre um fundo verde de arena
        bg = pygame.Surface((scaled.get_width() + 50, scaled.get_height() + 50))
        bg.fill((45, 120, 50))
        bg.blit(scaled, (10, 10))

        # O fundo ao redor do texto DEVE permanecer a cor original do terreno
        assert bg.get_at((10, 10)) == (45, 120, 50, 255)
        assert bg.get_at((10 + scaled.get_width() - 1, 10)) == (45, 120, 50, 255)

def test_all_fatality_phrases_transparency():
    cd = CinematicDirector()
    styles = [
        "DUAL_IMPALE_X_SPREAD", "HEADSHOT_EXPLODE", "VERTICAL_BISECTION",
        "WINDMILL_SHURIKEN_DECAP", "KUWA_SKULL_CLEAVE", "EARTH_STOMP_CRUSH",
        "BLIND_CAROTID_SLICE", "TESSEN_DECAP", "HAMAYA_HOLY_PIERCE"
    ]
    for st in styles:
        cd._build_kanji_overlay(death_style=st)
        surf = cd.cached_kanji_surf
        # Assegurar que cantos e áreas livres são transparentes
        assert surf.get_at((0, 0)).a == 0
        assert surf.get_at((surf.get_width() - 1, 0)).a == 0

def test_render_ink_transparency():
    font = get_title_font(18)
    ink_surf = render_ink(font, "二天一流")
    assert ink_surf.get_flags() & pygame.SRCALPHA
    # Cantos devem ser transparentes
    assert ink_surf.get_at((0, 0)).a == 0

def test_render_text_fx_transparency():
    font = get_title_font(20)
    txt_surf = render_text_fx(font, "TESTE TEXTO", (255, 255, 255), outline=True, shadow=True)
    assert txt_surf.get_flags() & pygame.SRCALPHA
    assert txt_surf.get_at((0, 0)).a == 0

if __name__ == "__main__":
    test_kanji_overlay_transparency()
    test_all_fatality_phrases_transparency()
    test_render_ink_transparency()
    test_render_text_fx_transparency()
    print("Todos os testes de transparência de fontes passaram com 100% de sucesso!")
