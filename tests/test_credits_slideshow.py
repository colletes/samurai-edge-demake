#!/usr/bin/env python3
"""
Testes automatizados do Slideshow e Tela de Créditos de Samurai Edge: Bakumatsu.
Verifica resolução de arquivos, durações, transições e ciclo de vida completo.
"""

import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.arcade.arcade_credits import (
    ArcadeCreditsScreen,
    SLIDE_CONFIG,
    _get_scaled_slide_image,
    _resolve_slide_image_path,
)


def test_credits_slideshow():
    pygame.init()
    screen = pygame.Surface((1280, 720))

    # 1. Total de slides e duração
    assert len(SLIDE_CONFIG) == 13, f"Esperado 13 slides, encontrado {len(SLIDE_CONFIG)}"
    total_dur = sum(s["duration"] for s in SLIDE_CONFIG)
    assert abs(total_dur - 291.0) < 0.1, f"Duração total deve ser 291s, obtido {total_dur}"

    # 2. Resolução de imagens e carregamento
    for idx, cfg in enumerate(SLIDE_CONFIG):
        path = _resolve_slide_image_path(cfg)
        assert os.path.exists(path), f"Arquivo do Slide {idx} não existe: {path}"
        surf = _get_scaled_slide_image(path)
        assert surf is not None, f"Falha ao carregar e escalar imagem do Slide {idx}"
        assert surf.get_size() == (1280, 720), f"Dimensão incorreta para Slide {idx}"

    # 3. Ciclo de vida da tela
    credits = ArcadeCreditsScreen()
    credits.open(None, white_fade_in=True, return_to_gallery=True, show_skip_prompt=True)
    assert credits.active
    assert credits.return_to_gallery

    # Renderizar primeiro frame (white-in)
    credits.render(screen)

    # Avançar até o fim
    for _ in range(int(295)):
        res = credits.update(1.0)
        credits.render(screen)
        if res == "DONE":
            break

    assert not credits.active, "Tela de créditos deveria estar inativa após conclusão"
    print("test_credits_slideshow OK")


if __name__ == "__main__":
    test_credits_slideshow()
