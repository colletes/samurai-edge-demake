"""
Renderiza e salva uma screenshot da nova Tela de Configurações de Controles.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, DEFAULT_CONTROLS
)
from src.isometric.camera import Camera
from src.world.map_data import GameMap
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.ui.settings_menu import SettingsMenu

def generate_settings_preview():
    pygame.init()
    pygame.font.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    font_large = pygame.font.Font(None, 48)
    font_mid = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    controls = dict(DEFAULT_CONTROLS)
    settings_menu = SettingsMenu(controls)
    settings_menu.open()

    game_map = GameMap()
    red = RedSamurai(wx=8.5, wy=11.0)
    blue = BlueSamurai(wx=13.5, wy=11.0)
    camera = Camera(target_wx=11.0, target_wy=11.0)

    # Renderiza o fundo do jogo
    screen.fill(COLOR_BG)
    game_map.render_terrain(screen, camera, 0.0)

    # Renderiza os samurais e bambus
    render_queue = []
    for b in game_map.bamboos:
        render_queue.append((b.wy, 'bamboo', b))
    render_queue.append((red.wy, 'red', red))
    render_queue.append((blue.wy, 'blue', blue))
    render_queue.sort(key=lambda item: item[0])
    for _, itype, obj in render_queue:
        if itype == 'bamboo':
            obj.render(screen, camera, 0.0)
        else:
            obj.render(screen, camera)

    # Renderiza o Menu de Configurações
    settings_menu.render(screen, font_large, font_mid, font_small)

    out_path = "/Users/thiagocarvalho/.gemini/antigravity/brain/80cd5ff5-eb4f-4d2c-baf8-9e4a729ecc96/settings_preview.png"
    pygame.image.save(screen, out_path)
    print("Settings preview salvo em:", out_path)
    pygame.quit()

if __name__ == "__main__":
    generate_settings_preview()
