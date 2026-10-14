"""
Gera preview da tela de seleção de personagens.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui.character_select import CharacterSelectScreen

def generate_char_select_preview():
    pygame.init()
    pygame.font.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    font_large = pygame.font.Font(None, 48)
    font_mid = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    char_select = CharacterSelectScreen()
    char_select.p1_choice_idx = 0  # Kenshin
    char_select.p2_choice_idx = 2  # Ninja Hanzo

    char_select.render(screen, font_large, font_mid, font_small)

    out_path = "/Users/thiagocarvalho/.gemini/antigravity/brain/80cd5ff5-eb4f-4d2c-baf8-9e4a729ecc96/char_select_preview.png"
    pygame.image.save(screen, out_path)
    print("Preview da seleção de personagens salvo em:", out_path)
    pygame.quit()

if __name__ == "__main__":
    generate_char_select_preview()
