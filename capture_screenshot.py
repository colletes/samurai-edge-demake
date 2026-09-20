"""
Script para renderizar um frame de alta fidelidade e salvar uma screenshot do duelo.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_GOLD, COLOR_RED_AURA, COLOR_BLUE_AURA, COLOR_WHITE
)
from src.isometric.camera import Camera
from src.world.map_data import GameMap
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.combat.collision import CombatSystem
from src.effects.particles import AmbientLeafParticle, FloatingBanner

def generate_preview():
    pygame.init()
    pygame.font.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    font_large = pygame.font.Font(None, 44)
    font_mid = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    game_map = GameMap()
    red = RedSamurai(wx=8.5, wy=11.0)
    blue = BlueSamurai(wx=13.5, wy=11.0)
    camera = Camera(target_wx=11.0, target_wy=11.0)
    combat = CombatSystem()

    particles = []
    banners = [
        FloatingBanner("DUELO DE SAMURAIS", 11.0, 11.0, wz=2.2, color=(255, 230, 100), duration=5.0)
    ]
    leaves = [AmbientLeafParticle(game_map.cols, game_map.rows) for _ in range(50)]

    # Cortar alguns bambus próximos para demonstrar a física de corte
    for b in game_map.bamboos:
        if 9.0 <= b.wx <= 10.0 and 8.0 <= b.wy <= 12.0:
            part = b.cut((1.0, 0.2))
            if part:
                particles.append(part)

    # Simular 40 frames para espalhar folhas e posicionar a câmera
    for frame in range(40):
        dt = 1.0 / 60.0
        camera.update(11.0, 11.0, dt)
        red.update(dt, game_map)
        blue.update(dt, game_map)
        particles = [p for p in particles if p.update(dt)]
        banners = [bn for bn in banners if bn.update(dt)]
        for leaf in leaves:
            leaf.update(dt)

    # Renderização
    screen.fill(COLOR_BG)
    game_map.render_terrain(screen, camera, 1.2)

    # Y-Sort
    render_queue = []
    for b in game_map.bamboos:
        render_queue.append((b.wy, 'bamboo', b))
    for r in game_map.rocks:
        render_queue.append((r.wy, 'rock', r))
    if game_map.well:
        render_queue.append((game_map.well.wy, 'well', game_map.well))
    for t in game_map.trees:
        render_queue.append((t.wy, 'tree', t))
    render_queue.append((red.wy, 'red', red))
    render_queue.append((blue.wy, 'blue', blue))
    for p in particles:
        if hasattr(p, 'wy'):
            render_queue.append((p.wy, 'particle', p))

    render_queue.sort(key=lambda item: item[0])
    for _, itype, obj in render_queue:
        if itype == 'bamboo':
            obj.render(screen, camera, 1.2)
        elif itype == 'particle':
            obj.render(screen, camera)
        else:
            obj.render(screen, camera)

    for leaf in leaves:
        leaf.render(screen, camera)

    for banner in banners:
        banner.render(screen, camera, font_mid)

    # HUD
    panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, 14, 440, 52)
    pygame.draw.rect(screen, (20, 24, 22, 210), panel_rect, border_radius=8)
    pygame.draw.rect(screen, (60, 75, 68), panel_rect, 2, border_radius=8)

    p1_title = font_mid.render("KENSHIN  0", True, COLOR_RED_AURA)
    p2_title = font_mid.render("0  MUSASHI", True, COLOR_BLUE_AURA)
    screen.blit(p1_title, (panel_rect.x + 20, panel_rect.y + 14))
    screen.blit(p2_title, (panel_rect.right - p2_title.get_width() - 20, panel_rect.y + 14))

    mode_surf = font_small.render("[1P vs IA] - TAB para 2P", True, COLOR_GOLD)
    screen.blit(mode_surf, (panel_rect.centerx - mode_surf.get_width() // 2, panel_rect.y + 16))

    footer_rect = pygame.Rect(20, SCREEN_HEIGHT - 48, SCREEN_WIDTH - 40, 36)
    pygame.draw.rect(screen, (16, 20, 18, 200), footer_rect, border_radius=6)
    c1 = font_small.render("VERMELHO: W/A/S/D = Mover | J = Iai Flash | K = Dash", True, (240, 180, 180))
    c2 = font_small.render("AZUL: Setas = Mover | U = Combo 3-Cortes | I = Parry", True, (180, 210, 240))
    c3 = font_small.render("[TAB] Alternar IA / 2P  |  [ESPAÇO] Reiniciar", True, COLOR_GOLD)
    screen.blit(c1, (35, SCREEN_HEIGHT - 40))
    screen.blit(c2, (SCREEN_WIDTH // 2 - c2.get_width() // 2, SCREEN_HEIGHT - 40))
    screen.blit(c3, (SCREEN_WIDTH - c3.get_width() - 35, SCREEN_HEIGHT - 40))

    artifact_img = "/Users/thiagocarvalho/.gemini/antigravity/brain/80cd5ff5-eb4f-4d2c-baf8-9e4a729ecc96/gameplay_preview.png"
    pygame.image.save(screen, artifact_img)
    print("Screenshot salva com sucesso em:", artifact_img)
    pygame.quit()

if __name__ == "__main__":
    generate_preview()
