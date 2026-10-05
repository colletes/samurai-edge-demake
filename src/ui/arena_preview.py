"""Prévia de arena gerada pelo próprio gerador (vista clássica recortada), usada nas cartas da seleção de arena."""
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.isometric.camera import Camera
from src.world.arenas import create_arena

_cache: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}


def _static_items(arena):
    items = [(o, True) for o in arena.bamboos] + [(o, True) for o in arena.buildings] + [(o, True) for o in arena.lanterns]
    items += [(o, False) for o in arena.rocks + arena.trees + arena.torii_gates]
    if arena.well:
        items.append((arena.well, False))
    return items


def render_arena_preview(arena_id: str, size: tuple[int, int]) -> pygame.Surface:
    key = (arena_id, size)
    if key in _cache:
        return _cache[key]
    arena = create_arena(arena_id)
    frame = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    frame.fill(arena.bg_color)
    camera = arena.attach_camera(Camera(arena.cols / 2.0, arena.rows / 2.0))
    arena.render_terrain(frame, camera, 0.0)

    def center(obj):
        if hasattr(obj, "width") and hasattr(obj, "depth"):
            return obj.wx + obj.width * 0.5, obj.wy + obj.depth * 0.5
        return obj.wx, obj.wy

    for obj, timed in sorted(_static_items(arena), key=lambda it: camera.depth(*center(it[0]))):
        obj.render(frame, camera, 0.0) if timed else obj.render(frame, camera)

    crop_w = 1000
    crop_h = int(crop_w * size[1] / size[0])
    rect = pygame.Rect(0, 0, crop_w, crop_h)
    rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    preview = pygame.transform.smoothscale(frame.subsurface(rect.clip(frame.get_rect())), size)
    _cache[key] = preview
    return preview
