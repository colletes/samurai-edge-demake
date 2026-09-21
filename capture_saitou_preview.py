"""
Gera preview da tela de seleção com 7 lutadores e do duelo na ponte com Saitou executando Gatotsu.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_GOLD, COLOR_WHITE,
    COLOR_SAITOU_LIGHT_BLUE, COLOR_RED_AURA
)
from src.isometric.camera import Camera
from src.world.map_data import GameMap
from src.entities.saitou_samurai import SaitouSamurai
from src.entities.red_samurai import RedSamurai
from src.effects.particles import AmbientLeafParticle, FloatingBanner, SparkParticle
from src.ui.character_select import CharacterSelectScreen

def generate_previews():
    pygame.init()
    pygame.font.init()

    font_large = pygame.font.Font(None, 48)
    font_mid = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    # 1. Preview da Seleção de Personagens (7 Guerreiros)
    screen_select = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    char_select = CharacterSelectScreen()
    char_select.p1_choice_idx = 6  # Hajime Saitou
    char_select.p2_choice_idx = 0  # Kenshin Himura
    char_select.render(screen_select, font_large, font_mid, font_small)

    out_select = "/Users/thiagocarvalho/.gemini/antigravity/brain/80cd5ff5-eb4f-4d2c-baf8-9e4a729ecc96/char_select_7p_preview.png"
    out_select_ws = "/Users/thiagocarvalho/Documents/Sample Game/char_select_7p_preview.png"
    pygame.image.save(screen_select, out_select)
    pygame.image.save(screen_select, out_select_ws)
    print("Preview da seleção 7P salvo!")

    # 2. Preview do Duelo na Ponte: Saitou vs Kenshin
    screen_game = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    game_map = GameMap()
    camera = Camera(target_wx=10.5, target_wy=11.0)

    # Spawns nas extremidades da ponte
    saitou = SaitouSamurai(wx=10.5, wy=8.8)
    kenshin = RedSamurai(wx=10.5, wy=14.8)
    saitou.set_facing(kenshin.wx, kenshin.wy)
    kenshin.set_facing(saitou.wx, saitou.wy)

    # Simular Gatotsu em alta velocidade pelo centro da ponte de madeira
    saitou.trigger_gatotsu_thrust(kenshin.wx, kenshin.wy)
    saitou.charge_speed = 14.5
    saitou.trail_points = [
        (10.5, 7.2), (10.5, 7.6), (10.5, 8.0), (10.5, 8.4), (10.5, 8.8)
    ]

    particles = []
    for pt in saitou.trail_points:
        for _ in range(3):
            particles.append(SparkParticle(pt[0], pt[1], 0.3))

    banners = [
        FloatingBanner("GATOTSU - ESTOCADA SHINSENGUMI!", 10.5, 8.8, wz=2.0, color=(140, 220, 255), duration=5.0),
        FloatingBanner("WOODEN BRIDGE DUEL", 10.5, 11.0, wz=2.2, color=COLOR_GOLD, duration=5.0)
    ]
    leaves = [AmbientLeafParticle(game_map.cols, game_map.rows) for _ in range(45)]

    # Renderizar Terreno
    screen_game.fill(COLOR_BG)
    game_map.render_terrain(screen_game, camera, 2.0)

    # Fila de renderização isométrica
    render_queue = []
    for b in game_map.bamboos:
        render_queue.append((b.wy, 'bamboo', b))
    for r in game_map.rocks:
        render_queue.append((r.wy, 'rock', r))
    if game_map.well:
        render_queue.append((game_map.well.wy, 'well', game_map.well))

    render_queue.append((saitou.wy, 'fighter', saitou))
    render_queue.append((kenshin.wy, 'fighter', kenshin))

    for p in particles:
        render_queue.append((p.wy, 'particle', p))

    render_queue.sort(key=lambda item: item[0])

    for item in render_queue:
        obj_type = item[1]
        obj = item[2]
        if obj_type == 'bamboo':
            obj.render(screen_game, camera, 1.0)
        elif obj_type == 'rock':
            obj.render(screen_game, camera)
        elif obj_type == 'well':
            obj.render(screen_game, camera)
        elif obj_type == 'fighter':
            obj.render(screen_game, camera)
        elif obj_type == 'particle':
            obj.render(screen_game, camera)

    for b in banners:
        b.render(screen_game, camera, font_large)

    # HUD
    p1_tag = font_mid.render("P1: HAJIME SAITOU (Shinsengumi) [VOXEL]", True, COLOR_SAITOU_LIGHT_BLUE)
    p2_tag = font_mid.render("P2: KENSHIN HIMURA (Battousai) [VOXEL]", True, COLOR_RED_AURA)
    screen_game.blit(p1_tag, (30, 25))
    screen_game.blit(p2_tag, (SCREEN_WIDTH - p2_tag.get_width() - 30, 25))

    out_game = "/Users/thiagocarvalho/.gemini/antigravity/brain/80cd5ff5-eb4f-4d2c-baf8-9e4a729ecc96/saitou_bridge_gameplay.png"
    out_game_ws = "/Users/thiagocarvalho/Documents/Sample Game/saitou_bridge_gameplay.png"
    pygame.image.save(screen_game, out_game)
    pygame.image.save(screen_game, out_game_ws)
    print("Preview do gameplay de Saitou na ponte salvo!")
    pygame.quit()

if __name__ == "__main__":
    generate_previews()
