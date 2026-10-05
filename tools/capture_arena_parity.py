"""
Regrava as imagens de referência de paridade visual do Bambu e de Kyoto (tests/fixtures/arena_parity).
Uso (depois de mudar o visual de uma arena de propósito): SDL_VIDEODRIVER=dummy ./venv/bin/python tools/capture_arena_parity.py
"""
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame

from tests.test_arena_generator import FIXTURES, render_frame
from src.world.kyoto_map import KyotoMap
from src.world.map_data import GameMap


def main():
    os.makedirs(FIXTURES, exist_ok=True)
    for name, ctor in (("bamboo", GameMap), ("kyoto", KyotoMap)):
        for az in (0, 45, 135):
            random.seed(7)
            path = os.path.join(FIXTURES, f"{name}_az{az}.png")
            pygame.image.save(render_frame(ctor(), az), path)
            print("gravado", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
