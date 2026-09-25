"""
Script para capturar screenshots de alta fidelidade das novas telas e do novo cenário:
1. Tela de Título com estilo Sumi-E e Seletor de Modos.
2. Tela de Seleção de Arena com os cards explicativos e miniaturas.
3. Gameplay na Arena Kyoto Bakumatsu com carruagem desgovernada, escombros flamejantes e samurais voxel.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_KYOTO_BG
)
from src.isometric.camera import Camera
from src.world.kyoto_map import KyotoMap, RunawayCarriage, FallingDebris
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.ui.title_screen import SumieTitleScreen
from src.ui.arena_select import ArenaSelectScreen
from src.effects.particles import FloatingBanner

def capture_previews():
    pygame.init()
    pygame.font.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    font_large = pygame.font.Font(None, 48)
    font_mid = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    # 1. Capturar Tela de Título Sumi-E
    title_screen = SumieTitleScreen()
    title_screen.update(0.1)
    title_screen.render(screen, font_large, font_mid, font_small)
    out_dir = "/Users/thiagocarvalho/.gemini/antigravity/brain/4f5a8a73-16ee-4044-841d-555e45713a63"
    p1_path = os.path.join(out_dir, "title_screen_preview.png")
    pygame.image.save(screen, p1_path)
    print("Salvo:", p1_path)

    # 2. Capturar Tela de Seleção de Arena
    arena_select = ArenaSelectScreen()
    arena_select.selected_idx = 1 # Kyoto selecionado
    arena_select.update(0.1)
    arena_select.render(screen, font_large, font_mid, font_small)
    p2_path = os.path.join(out_dir, "arena_select_preview.png")
    pygame.image.save(screen, p2_path)
    print("Salvo:", p2_path)

    # 3. Capturar Gameplay na Arena de Kyoto Bakumatsu
    screen.fill(COLOR_KYOTO_BG)
    kyoto = KyotoMap()
    camera = Camera(target_wx=11.0, target_wy=11.0)
    camera.update(11.0, 11.0, 0.016)

    red = RedSamurai(wx=8.5, wy=9.0)
    blue = BlueSamurai(wx=13.0, wy=13.5)
    red.set_facing(blue.wx, blue.wy)
    blue.set_facing(red.wx, red.wy)

    # Carruagem em alta velocidade cruzando a avenida central
    carriage = RunawayCarriage(start_pos=(10.5, 7.5), end_pos=(18.0, 15.0), speed=14.0)
    carriage.warning_timer = 0.0

    # Escombro flamejante caindo na calçada
    debris = FallingDebris(target_x=6.5, target_y=14.0)
    debris.timer = 1.05
    debris.wz = 1.5

    particles = []
    banners = [
        FloatingBanner("KYOTO: BAKUMATSU", 11.0, 11.0, wz=2.6, color=(255, 200, 60), duration=5.0),
        FloatingBanner("[!] CARRUAGEM!", carriage.wx, carriage.wy, wz=2.2, color=(255, 80, 40), duration=5.0)
    ]

    # Renderizar Terreno
    kyoto.render_terrain(screen, camera, 1.5)

    # Y-sorting dos objetos
    render_queue = []
    for b in kyoto.buildings:
        render_queue.append((b.wx + b.wy + b.depth * 0.5, 'building', b))
    for l in kyoto.lanterns:
        render_queue.append((l.wx + l.wy, 'lantern', l))
    render_queue.append((carriage.wx + carriage.wy, 'carriage', carriage))
    render_queue.append((debris.target_x + debris.target_y, 'debris', debris))
    render_queue.append((red.wx + red.wy, 'fighter', red))
    render_queue.append((blue.wx + blue.wy, 'fighter', blue))

    render_queue.sort(key=lambda item: item[0])

    for _, item_type, obj in render_queue:
        if item_type == 'building':
            obj.render(screen, camera, 1.5)
        elif item_type == 'lantern':
            obj.render(screen, camera, 1.5)
        elif item_type == 'carriage':
            obj.render(screen, camera)
        elif item_type == 'debris':
            obj.render(screen, camera)
        elif item_type == 'fighter':
            obj.render(screen, camera)

    for banner in banners:
        banner.render(screen, camera, font_mid)

    # HUD Superior
    panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 14, 480, 54)
    pygame.draw.rect(screen, (24, 20, 22, 220), panel_rect, border_radius=8)
    pygame.draw.rect(screen, (85, 60, 55), panel_rect, 2, border_radius=8)
    t_red = font_mid.render("KENSHI  0", True, (255, 90, 90))
    t_blue = font_mid.render("0  MUSASHI", True, (90, 160, 255))
    screen.blit(t_red, (panel_rect.x + 20, panel_rect.y + 16))
    screen.blit(t_blue, (panel_rect.right - t_blue.get_width() - 20, panel_rect.y + 16))
    arena_t = font_small.render("ARENA: KYOTO (BAKUMATSU)", True, COLOR_GOLD)
    screen.blit(arena_t, (panel_rect.centerx - arena_t.get_width() // 2, panel_rect.y + 18))

    p3_path = os.path.join(out_dir, "kyoto_gameplay_preview.png")
    pygame.image.save(screen, p3_path)
    print("Salvo:", p3_path)
    pygame.quit()

if __name__ == "__main__":
    capture_previews()
