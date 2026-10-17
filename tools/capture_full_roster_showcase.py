import os
import sys
import math
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ["SDL_VIDEODRIVER"] = "dummy"

from src.entities.voxel_models import render_voxel_humanoid
from tools.model_inspector import InspectorCamera
from src.roster import PLAYABLE_FIGHTERS

CHARACTER_NAMES = {
    "kenshin": "Kenshi",
    "musashi": "Musashi",
    "ninja": "Hanzo",
    "american": "Joe",
    "saitou": "Saitou",
    "rifle": "Teppo",
    "purple": "Murasaki",
    "gray": "Kasumi",
    "kabuki": "Okuni",
    "archer": "Tomoe",
    "pirate": "Anne",
    "musketeer": "Julie",
    "ren": "Ren",
    "chiyo": "Chiyo",
    "benkei": "Benkei",
    "orin": "O-Rin",
    "goro": "Goro",
    "ichi": "Ichi",
}

def render_showcase():
    pygame.init()
    pygame.font.init()

    cols = 6
    rows = 3
    card_w = 220
    card_h = 280
    pad = 16
    total_w = cols * card_w + (cols + 1) * pad
    total_h = rows * card_h + (rows + 1) * pad + 60

    canvas = pygame.Surface((total_w, total_h))
    canvas.fill((20, 22, 26))

    font_title = pygame.font.Font(None, 42)
    font_name = pygame.font.Font(None, 24)
    font_sub = pygame.font.Font(None, 18)

    title_surf = font_title.render("SAMURAI EDGE: 18-FIGHTER ROSTER (3D ANIME VOXEL)", True, (240, 220, 180))
    canvas.blit(title_surf, ((total_w - title_surf.get_width()) // 2, 18))

    cam = InspectorCamera(card_w, card_h)
    cam.azimuth = math.radians(40.0)
    cam.elevation = math.radians(28.0)
    cam.zoom = 3.6
    cam.target_z = 0.48
    cam.screen_x = card_w // 2
    cam.screen_y = card_h // 2 + 30

    card_surf = pygame.Surface((card_w, card_h))

    for idx, char_id in enumerate(PLAYABLE_FIGHTERS):
        r = idx // cols
        c = idx % cols
        x = pad + c * (card_w + pad)
        y = 60 + pad + r * (card_h + pad)

        card_surf.fill((28, 30, 36))
        # Draw border
        pygame.draw.rect(card_surf, (50, 55, 65), (0, 0, card_w, card_h), 2)
        pygame.draw.rect(card_surf, (200, 180, 130), (0, 0, card_w, 28))

        display_name = CHARACTER_NAMES.get(char_id, char_id.capitalize())
        name_txt = font_name.render(display_name, True, (20, 20, 25))
        card_surf.blit(name_txt, ((card_w - name_txt.get_width()) // 2, 6))

        # Render 3D model
        render_voxel_humanoid(card_surf, cam, 0.0, 0.0, 0.0, 1.0, 1.0, "IDLE", 0.0, True, char_id, 0.0, 255, False)

        # Bottom label
        tag_txt = font_sub.render(f"#{idx+1:02d} • {char_id.upper()}", True, (140, 145, 160))
        card_surf.blit(tag_txt, ((card_w - tag_txt.get_width()) // 2, card_h - 22))

        canvas.blit(card_surf, (x, y))

    out_dir = "/Users/thiagocarvalho/.gemini/antigravity/brain/7fa4fe0a-114d-479a-99df-981bd66d67b6"
    out_file = os.path.join(out_dir, "roster_18_showcase.png")
    pygame.image.save(canvas, out_file)
    print("Full roster showcase saved to:", out_file)

if __name__ == "__main__":
    render_showcase()
