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
    screen = pygame.Surface((400, 400))
    cam = InspectorCamera(400, 400)
    cam.screen_x = 200
    cam.screen_y = 200
    cam.azimuth = 0.0
    cam.elevation = math.radians(20.0)
    cam.zoom = 16.0
    cam.target_z = 0.72

    out_dir = "/Users/thiagocarvalho/.gemini/antigravity/brain/7fa4fe0a-114d-479a-99df-981bd66d67b6"
    screen.fill((30, 32, 36))
    render_voxel_humanoid(screen, cam, 0.0, 0.0, 0.0, 1.0, 1.0, "IDLE", 0.0, True, "kasumi", 0.0, 255, False)
    pygame.image.save(screen, os.path.join(out_dir, "kasumi_zoom16.png"))
    print("Saved kasumi_zoom16.png")

if __name__ == "__main__":
    run()
