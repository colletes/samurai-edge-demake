"""
Capturas de cada arena em 0°, 45° e 135° (36 imagens) para docs/screenshots/arenas.
Uso: SDL_VIDEODRIVER=dummy ./venv/bin/python tools/capture_arena_gallery.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src.config import SCREEN_HEIGHT, SCREEN_WIDTH
from src.isometric.camera import Camera
from src.world.arenas import arena_ids, create_arena

OUT = os.path.join(ROOT, "docs", "screenshots", "arenas")
AZIMUTHS = (0, 45, 135)


def _build_static_render_queue(current_map):
    queue = []
    for bamboo in getattr(current_map, "bamboos", []):
        queue.append((bamboo.wx + bamboo.wy, "bamboo", bamboo))
    for rock in getattr(current_map, "rocks", []):
        queue.append((rock.wx + rock.wy, "rock", rock))
    if getattr(current_map, "well", None):
        queue.append((current_map.well.wx + current_map.well.wy, "well", current_map.well))
    for tree in getattr(current_map, "trees", []):
        queue.append((tree.wx + tree.wy, "tree", tree))
    for tg in getattr(current_map, "torii_gates", []):
        queue.append((tg.wx + tg.wy, "torii", tg))
    for b in getattr(current_map, "buildings", []):
        queue.append((b.wx + b.wy + getattr(b, "depth", 0.5) * 0.5, "building", b))
    for l in getattr(current_map, "lanterns", []):
        queue.append((l.wx + l.wy, "lantern", l))
    return queue


def _static_item_center(item_type: str, obj) -> tuple[float, float]:
    if item_type == "building":
        return obj.wx + getattr(obj, "width", 0.5) * 0.5, obj.wy + getattr(obj, "depth", 0.5) * 0.5
    return obj.wx, obj.wy


def capture(arena_id: str, azimuth: float) -> pygame.Surface:
    random.seed(7)
    arena = create_arena(arena_id)
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill(arena.bg_color)
    cam = arena.attach_camera(Camera(11.0, 11.0)) or Camera(11.0, 11.0)
    cam.set_azimuth(math.radians(azimuth))
    arena.render_terrain(surf, cam, 1.0)
    queue = [(cam.depth(*_static_item_center(t, o)), t, o) for _, t, o in _build_static_render_queue(arena)]
    queue.sort(key=lambda item: item[0])
    for _, kind, obj in queue:
        if kind in ("bamboo", "building", "lantern") or getattr(obj, "animated", False):
            obj.render(surf, cam, 1.0)
        else:
            obj.render(surf, cam)
    arena.render_overhead(surf, cam, 1.0)
    return surf


def main_capture():
    os.makedirs(OUT, exist_ok=True)
    for arena_id in arena_ids():
        for az in AZIMUTHS:
            path = os.path.join(OUT, f"{arena_id}_az{az}.png")
            pygame.image.save(capture(arena_id, az), path)
            print("gravado", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main_capture()
