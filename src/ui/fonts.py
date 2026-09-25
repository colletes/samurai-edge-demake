"""
Módulo centralizado de carregamento e cache de fontes do jogo:
- Fonte Oriental Principal (Pincel Shojumaru): Títulos, Nomes de Guerreiros e Botões de Destaque
- Fonte Oriental Secundária (Serifa Histórica Zen Antique): Subtítulos, Atributos, Comandos e Textos Auxiliares
"""
import os
import pygame
from src.config import get_asset_path

_font_cache: dict[tuple[str, int], pygame.font.Font] = {}

FONT_ORIENTAL_TITLE = "assets/fonts/Shojumaru-Regular.ttf"
FONT_ORIENTAL_TEXT = "assets/fonts/ZenAntique-Regular.ttf"

def get_font(font_path: str, size: int) -> pygame.font.Font:
    """Retorna uma fonte em cache ou carrega com fallback seguro para a fonte padrão."""
    resolved_path = get_asset_path(font_path)
    key = (resolved_path, size)
    if key in _font_cache:
        return _font_cache[key]

    font = None
    if os.path.exists(resolved_path):
        try:
            font = pygame.font.Font(resolved_path, size)
        except Exception:
            font = None

    if font is None:
        font = pygame.font.Font(None, size)

    _font_cache[key] = font
    return font

def get_title_font(size: int = 28) -> pygame.font.Font:
    """Fonte oriental de pincel Shojumaru para títulos, nomes e botões de ação."""
    return get_font(FONT_ORIENTAL_TITLE, size)

def get_text_font(size: int = 16) -> pygame.font.Font:
    """Fonte histórica japonesa Zen Antique para textos secundários, atributos e menus."""
    return get_font(FONT_ORIENTAL_TEXT, size)
