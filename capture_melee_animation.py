"""
Captura uma screenshot demonstrando as novas animações procedurais dos ataques melee em pleno movimento.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_GOLD, COLOR_WHITE
from src.world.map_data import GameMap
from src.isometric.camera import Camera
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.effects.particles import AmbientLeafParticle, FloatingBanner

def capture():
    pygame.init()
    pygame.font.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    game_map = GameMap()
    camera = Camera(11.0, 11.0)

    kenshin = RedSamurai(wx=10.0, wy=11.0)
    musashi = BlueSamurai(wx=12.2, wy=11.0)

    # Iniciar ataques melee em ambos para congelar no ápice do arco de corte
    kenshin.trigger_iai_attack(musashi.wx, musashi.wy)
    kenshin.state_timer = 0.08  # Meio do arco (atk_progress ~ 0.5)

    musashi.combo_step = 1
    musashi.state = "ATTACK"
    musashi.state_timer = 0.09 # Meio do corte 1

    banners = [
        FloatingBanner("NOVA ANIMAÇÃO PROCEDURAL MELEE (VOXEL ARCS)", 11.0, 11.0, wz=2.2, color=(255, 230, 100), duration=5.0)
    ]
    leaves = [AmbientLeafParticle(game_map.cols, game_map.rows) for _ in range(40)]

    # Render
    screen.fill(COLOR_BG)
    game_map.render_terrain(screen, camera, 1.0)

    for b in game_map.bamboos:
        b.render(screen, camera, 1.0)
    for r in game_map.rocks:
        r.render(screen, camera)
    if game_map.well:
        game_map.well.render(screen, camera)
    for t in game_map.trees:
        t.render(screen, camera)

    kenshin.render(screen, camera)
    musashi.render(screen, camera)

    font = pygame.font.Font(None, 32)
    for bn in banners:
        bn.render(screen, camera, font)

    pygame.image.save(screen, "melee_animation_preview.png")
    print("Screenshot salva com sucesso em 'melee_animation_preview.png'!")

if __name__ == "__main__":
    capture()
