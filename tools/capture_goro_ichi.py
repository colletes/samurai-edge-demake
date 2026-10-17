import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ["SDL_VIDEODRIVER"] = "dummy"
import math
import pygame
from src.entities.voxel_models import render_voxel_humanoid
from tools.model_inspector import InspectorCamera

def run():
    pygame.init()
    screen = pygame.Surface((500, 500))
    cam = InspectorCamera(500, 500)
    cam.screen_x = 250
    cam.screen_y = 280

    out_dir = "/Users/thiagocarvalho/.gemini/antigravity/brain/7fa4fe0a-114d-479a-99df-981bd66d67b6"

    for char_id in ("goro", "ichi"):
        prefix = char_id
        # 1. Front view head macro
        cam.azimuth = 0.0
        cam.elevation = math.radians(25.0)
        cam.zoom = 8.5
        cam.target_z = 0.72
        screen.fill((30, 32, 36))
        render_voxel_humanoid(screen, cam, 0.0, 0.0, 0.0, 1.0, 1.0, "IDLE", 0.0, True, char_id, 0.0, 255, False)
        pygame.image.save(screen, os.path.join(out_dir, f"{prefix}_head_front.png"))

        # 2. 45 deg full body
        cam.azimuth = math.radians(45.0)
        cam.elevation = math.radians(30.0)
        cam.zoom = 4.0
        cam.target_z = 0.50
        screen.fill((30, 32, 36))
        render_voxel_humanoid(screen, cam, 0.0, 0.0, 0.0, 1.0, 1.0, "IDLE", 0.0, True, char_id, 0.0, 255, False)
        pygame.image.save(screen, os.path.join(out_dir, f"{prefix}_body_45.png"))

        # 3. 270 deg full body (left profile)
        cam.azimuth = math.radians(270.0)
        cam.elevation = math.radians(30.0)
        cam.zoom = 4.0
        cam.target_z = 0.50
        screen.fill((30, 32, 36))
        render_voxel_humanoid(screen, cam, 0.0, 0.0, 0.0, 1.0, 1.0, "IDLE", 0.0, True, char_id, 0.0, 255, False)
        pygame.image.save(screen, os.path.join(out_dir, f"{prefix}_body_270.png"))

        # 4. 180 deg full body (back)
        cam.azimuth = math.radians(180.0)
        cam.elevation = math.radians(30.0)
        cam.zoom = 4.0
        cam.target_z = 0.50
        screen.fill((30, 32, 36))
        render_voxel_humanoid(screen, cam, 0.0, 0.0, 0.0, 1.0, 1.0, "IDLE", 0.0, True, char_id, 0.0, 255, False)
        pygame.image.save(screen, os.path.join(out_dir, f"{prefix}_body_180.png"))

    print("Goro & Ichi captures complete!")

if __name__ == "__main__":
    run()
