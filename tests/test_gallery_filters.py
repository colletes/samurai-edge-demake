#!/usr/bin/env python3
"""
Testes automatizados da Galeria de Imagens com Filtros de Categoria e Arte Pura de Ending Slides.
Verifica carregamento dos 13 slides finais, filtros por categoria e desenho das setas poligonais.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui.gallery_screen import (
    GalleryScreen,
    CAT_ALL,
    CAT_CHARACTERS,
    CAT_ARENAS,
    CAT_ENDING,
    TAB_IMAGES,
)


def test_gallery_categories_and_ending_slides():
    pygame.init()
    g = GalleryScreen()
    g.open()

    # 1. Total de imagens escaneadas
    assert len(g.concept_entries) >= 60, f"Total de artes deve incluir concepts + ending slides, obtido {len(g.concept_entries)}"

    # 2. Verifica presença de artes em cada categoria
    chars = [e for e in g.concept_entries if e["category"] == CAT_CHARACTERS]
    arenas = [e for e in g.concept_entries if e["category"] == CAT_ARENAS]
    endings = [e for e in g.concept_entries if e["category"] == CAT_ENDING]

    assert len(chars) >= 20, f"Esperado ao menos 20 conceitos de personagens, obtido {len(chars)}"
    assert len(arenas) >= 20, f"Esperado ao menos 20 conceitos de arenas, obtido {len(arenas)}"
    assert len(endings) >= 13, f"Esperado ao menos 13 slides de encerramento em arte pura, obtido {len(endings)}"

    # 3. Verifica títulos limpos dos Ending Slides
    ending_titles = [e["title"] for e in endings]
    assert any("Slide 0" in t for t in ending_titles)
    assert any("Slide 1" in t for t in ending_titles)
    assert any("Monte Fuji" in t or "Slide Final" in t for t in ending_titles)

    # 4. Filtro de Categorias
    assert g.current_filter == CAT_ALL
    assert len(g.get_current_items()) == len(g.concept_entries)

    # Alternar para PERSONAGENS
    g.set_filter(CAT_CHARACTERS)
    assert g.current_filter == CAT_CHARACTERS
    assert len(g.get_current_items()) == len(chars)
    assert g.image_index == 0

    # Alternar para ARENAS
    g.set_filter(CAT_ARENAS)
    assert g.current_filter == CAT_ARENAS
    assert len(g.get_current_items()) == len(arenas)

    # Alternar para ENSAIOS DE FIM
    g.set_filter(CAT_ENDING)
    assert g.current_filter == CAT_ENDING
    assert len(g.get_current_items()) == len(endings)

    # 5. Renderização com setas poligonais
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    g.render(surf)

    assert g.prev_btn_rect.width == 48
    assert g.next_btn_rect.width == 48
    assert len(g.filter_rects) == 4

    # 6. Clique na pílula de filtro
    pill_rect_all, cat_key_all = g.filter_rects[0]
    ev_click_all = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pill_rect_all.center)
    g.handle_event(ev_click_all)
    assert g.current_filter == CAT_ALL

    print("test_gallery_categories_and_ending_slides OK")


if __name__ == "__main__":
    test_gallery_categories_and_ending_slides()
