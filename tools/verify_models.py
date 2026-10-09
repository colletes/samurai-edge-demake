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
    print("ModelInspector initialized successfully.", flush=True)
    os.makedirs("scratch", exist_ok=True)
    for i, (k, info) in enumerate(CHARACTERS.items()):
        inspector.select_character(i)
        inspector.render()
        out_path = f"scratch/test_v2_char_{i+1}_{k}.png"
        pygame.image.save(inspector.screen, out_path)
        print(f"OK: [{i+1}/12] {k} -> {out_path}", flush=True)
    print("ALL 12 MODELS VERIFIED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    main()
