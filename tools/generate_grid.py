#!/usr/bin/env python3
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from tools.model_inspector import CHARACTERS, ModelInspector

def main():
    inspector = ModelInspector(headless=True)
    cols = 4
    rows = 3
    cell_w, cell_h = 320, 240
    grid_surf = pygame.Surface((cols * cell_w, rows * cell_h))
    font = pygame.font.Font(None, 24)

    for i, (k, info) in enumerate(CHARACTERS.items()):
        inspector.select_character(i)
        inspector.render()
        cropped = pygame.Surface((cell_w, cell_h))
        cropped.blit(inspector.screen, (0, 0), (inspector.width//2 - cell_w//2, inspector.height//2 - cell_h//2 - 20, cell_w, cell_h))
        label = font.render(f"{i+1}. {info['name'].split()[0]}", True, (255, 230, 80))
        cropped.blit(label, (10, 10))
        c = i % cols
        r = i // cols
        grid_surf.blit(cropped, (c * cell_w, r * cell_h))

    out_file = "scratch/roster_12_updated_grid.png"
    pygame.image.save(grid_surf, out_file)
    print("Updated grid saved to", out_file, flush=True)

if __name__ == "__main__":
    main()
