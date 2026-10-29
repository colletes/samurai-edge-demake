"""Logo oficial "Samurai Edge: Bakumatsu" com cache de escala (sem alocar Surface por frame)."""
import pygame

from src.config import get_asset_path

_LOGO_FILES = {
    "light": "assets/ui/logo_light_bg.png",  # tinta preta, para fundos claros (pergaminho)
    "dark": "assets/ui/logo_dark_bg.png",    # tinta clara, para fundos escuros
}
_RAW_CACHE: dict[str, pygame.Surface | None] = {}
_SCALED_CACHE: dict[tuple[str, int], pygame.Surface | None] = {}


def _load_raw(variant: str) -> pygame.Surface | None:
    if variant not in _RAW_CACHE:
        try:
            _RAW_CACHE[variant] = pygame.image.load(get_asset_path(_LOGO_FILES[variant])).convert_alpha()
        except (pygame.error, FileNotFoundError, KeyError):
            _RAW_CACHE[variant] = None
    return _RAW_CACHE[variant]


def get_logo(variant: str, width: int) -> pygame.Surface | None:
    """Retorna o logo escalado para a largura pedida (mantém proporção) ou None se o asset faltar."""
    key = (variant, width)
    if key not in _SCALED_CACHE:
        raw = _load_raw(variant)
        if raw is None:
            _SCALED_CACHE[key] = None
        else:
            height = max(1, round(raw.get_height() * width / raw.get_width()))
            _SCALED_CACHE[key] = pygame.transform.smoothscale(raw, (width, height))
    return _SCALED_CACHE[key]
