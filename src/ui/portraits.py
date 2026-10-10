"""
Gerenciador e cache de retratos de busto HD-2D dos guerreiros.
Carrega as artes de assets/portraits/ com redimensionamento suave e cache automático.
"""
import os
import pygame
from src.config import get_asset_path

# Mapeamento universal de identificadores para o prefixo do arquivo em assets/portraits/
PORTRAIT_MAP = {
    # Por ID de configuração
    "kenshin": "kenshi",
    "kenshi": "kenshi",
    "musashi": "musashi",
    "ninja": "hanzo",
    "hanzo": "hanzo",
    "yellow_ninja": "hanzo",
    "american": "joe",
    "joe": "joe",
    "american_ninja": "joe",
    "saitou": "saitou",
    "rifle": "teppo",
    "rifleman": "teppo",
    "teppo": "teppo",
    "purple": "murasaki",
    "murasaki": "murasaki",
    "gray": "kasumi",
    "kasumi": "kasumi",
    "kabuki": "okuni",
    "okuni": "okuni",
    "archer": "tomoe",
    "tomoe": "tomoe",
    "pirate": "anne",
    "anne": "anne",
    "musketeer": "julie",
    "julie": "julie",
    "ren": "ren",
    "shaolin": "ren",
    "chiyo": "chiyo",
    "nodachi": "chiyo",
}

# Cache de superfícies carregadas: (char_key, size, circular) -> pygame.Surface
_PORTRAIT_CACHE: dict[tuple[str, tuple[int, int], bool], pygame.Surface] = {}
# Cache de imagens brutas em disco: path -> pygame.Surface
_RAW_CACHE: dict[str, pygame.Surface] = {}

def get_portrait(char_id: str, size: tuple[int, int] = (58, 58), circular: bool = True) -> pygame.Surface | None:
    """
    Retorna a superfície do busto do guerreiro no tamanho solicitado.
    Utiliza cache em memória para máxima performance a 60 FPS.
    """
    cache_key = (char_id.lower(), size, circular)
    if cache_key in _PORTRAIT_CACHE:
        return _PORTRAIT_CACHE[cache_key]

    prefix = PORTRAIT_MAP.get(char_id.lower(), char_id.lower())
    suffix = "_bust_circle.png" if circular else "_bust.png"
    filename = f"{prefix}{suffix}"

    path = get_asset_path(f"assets/portraits/{filename}")

    raw_surf = _RAW_CACHE.get(path)
    if raw_surf is None:
        if not os.path.exists(path):
            return None
        try:
            raw_surf = pygame.image.load(path)
            if pygame.display.get_surface() is not None:
                try:
                    raw_surf = raw_surf.convert_alpha()
                except Exception:
                    pass
            _RAW_CACHE[path] = raw_surf
        except Exception as e:
            print(f"[Portraits] Erro ao carregar {path}: {e}")
            return None

    try:
        if raw_surf.get_size() != size:
            scaled_surf = pygame.transform.smoothscale(raw_surf, size)
        else:
            scaled_surf = raw_surf
        _PORTRAIT_CACHE[cache_key] = scaled_surf
        return scaled_surf
    except Exception as e:
        print(f"[Portraits] Erro ao redimensionar {path}: {e}")
        return None


def preload_portraits(sizes=((50, 50), (58, 58), (35, 35), (33, 33), (66, 66), (84, 84), (110, 110))):
    """
    Pré-carrega todos os retratos dos 12 combatentes nos tamanhos mais comuns do jogo,
    eliminando qualquer micro-travamento (stutter) durante a seleção de personagens,
    transição de lutas do Arcade e introdução orbital.
    """
    unique_chars = (
        "kenshi", "musashi", "hanzo", "joe", "saitou", "teppo",
        "murasaki", "kasumi", "okuni", "tomoe", "anne", "julie",
        "ren", "chiyo"
    )
    for char in unique_chars:
        for circ in (True, False):
            for s in sizes:
                get_portrait(char, size=s, circular=circ)
