"""
Gera screenshots do American Ninja, Doberman e da nova tela com 4 cards de seleção.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_GOLD
)
from src.isometric.camera import Camera
from src.world.map_data import GameMap
from src.entities.american_ninja import AmericanNinja
from src.entities.yellow_ninja import YellowNinja
from src.entities.projectile import ShurikenProjectile
from src.effects.particles import AmbientLeafParticle, FloatingBanner
from src.ui.character_select import CharacterSelectScreen

def generate_previews():
    pygame.init()
    pygame.font.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    font_large = pygame.font.Font(None, 48)
    font_mid = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    # 1. Preview da Seleção com 4 Cards
    char_select = CharacterSelectScreen()
    char_select.p1_choice_idx = 3  # Joe (American Ninja)
    char_select.p2_choice_idx = 0  # Kenshin
    char_select.render(screen, font_large, font_mid, font_small)

    out_select = "/Users/thiagocarvalho/.gemini/antigravity/brain/80cd5ff5-eb4f-4d2c-baf8-9e4a729ecc96/char_select_4p_preview.png"
    pygame.image.save(screen, out_select)
    print("Preview de 4 personagens salvo em:", out_select)

    # 2. Preview do Gameplay do American Ninja & Doberman
    game_map = GameMap()
    joe = AmericanNinja(wx=8.5, wy=11.0)
    enemy = YellowNinja(wx=13.5, wy=11.0)
    joe.set_facing(enemy.wx, enemy.wy)
    enemy.set_facing(joe.wx, joe.wy)

    # Comandar o Doberman para investir contra o inimigo!
    joe.dog.charge(enemy.wx, enemy.wy)
    joe.dog.wx = 10.8
    joe.dog.wy = 11.0

    camera = Camera(11.0, 11.0)

    # Shuriken no ar
    shuriken = ShurikenProjectile(wx=12.0, wy=11.0, wz=0.6, dir_x=1.0, dir_y=0.0, owner=joe)
    projectiles = [shuriken]

    banners = [
        FloatingBanner("DOBERMAN ATTACK!", 10.8, 11.0, wz=1.6, color=(255, 60, 60), duration=5.0)
    ]
    leaves = [AmbientLeafParticle(game_map.cols, game_map.rows) for _ in range(40)]

    screen.fill(COLOR_BG)
    game_map.render_terrain(screen, camera, 2.0)

    render_queue = []
    for b in game_map.bamboos:
        render_queue.append((b.wy, 'bamboo', b))
    for r in game_map.rocks:
        render_queue.append((r.wy, 'rock', r))
    if game_map.well:
        render_queue.append((game_map.well.wy, 'well', game_map.well))
    for t in game_map.trees:
        render_queue.append((t.wy, 'tree', t))

    render_queue.append((joe.wy, 'fighter', joe))
    render_queue.append((enemy.wy, 'fighter', enemy))
    render_queue.append((joe.dog.wy, 'dog', joe.dog))

    for proj in projectiles:
        render_queue.append((proj.wy, 'projectile', proj))

    render_queue.sort(key=lambda item: item[0])

    for _, itype, obj in render_queue:
        if itype == 'bamboo':
            obj.render(screen, camera, 2.0)
        elif itype in ('rock', 'well', 'tree', 'fighter', 'dog', 'projectile'):
            obj.render(screen, camera)

    for leaf in leaves:
        leaf.render(screen, camera)

    for banner in banners:
        banner.render(screen, camera, font_mid)

    # HUD
    panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 14, 480, 54)
    pygame.draw.rect(screen, (20, 24, 22, 210), panel_rect, border_radius=8)
    pygame.draw.rect(screen, (60, 75, 68), panel_rect, 2, border_radius=8)

    p1_title = font_mid.render("JOE  0", True, (255, 130, 45))
    p2_title = font_mid.render("0  HANZO", True, (255, 220, 60))
    screen.blit(p1_title, (panel_rect.x + 20, panel_rect.y + 16))
    screen.blit(p2_title, (panel_rect.right - p2_title.get_width() - 20, panel_rect.y + 16))

    mode_surf = font_small.render("[1P vs IA]", True, COLOR_GOLD)
    screen.blit(mode_surf, (panel_rect.centerx - mode_surf.get_width() // 2, panel_rect.y + 18))

    select_btn = pygame.Rect(25, 20, 180, 32)
    pygame.draw.rect(screen, (26, 34, 30, 210), select_btn, border_radius=6)
    pygame.draw.rect(screen, COLOR_GOLD, select_btn, 1, border_radius=6)
    sel_txt = font_small.render("<< MUDAR GUERREIROS", True, COLOR_GOLD)
    screen.blit(sel_txt, (select_btn.centerx - sel_txt.get_width() // 2, select_btn.y + 7))

    footer_rect = pygame.Rect(20, SCREEN_HEIGHT - 48, SCREEN_WIDTH - 40, 36)
    pygame.draw.rect(screen, (16, 20, 18, 200), footer_rect, border_radius=6)
    c1 = font_small.render("P1 (JOE): W/A/S/D | E = Shuriken (Stun) | R = Cão Dash (Fatal)", True, (255, 205, 170))
    c2 = font_small.render("P2 (HANZO): Setas | U = Estocada | I = Arremessar Kunai", True, (255, 240, 180))
    screen.blit(c1, (30, SCREEN_HEIGHT - 40))
    screen.blit(c2, (SCREEN_WIDTH // 2 - c2.get_width() // 2 + 10, SCREEN_HEIGHT - 40))

    settings_btn_rect = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 44, 180, 28)
    pygame.draw.rect(screen, (40, 52, 45), settings_btn_rect, border_radius=4)
    pygame.draw.rect(screen, COLOR_GOLD, settings_btn_rect, 1, border_radius=4)
    c3 = font_small.render("[C] Controles / Settings", True, COLOR_GOLD)
    screen.blit(c3, (settings_btn_rect.centerx - c3.get_width() // 2, settings_btn_rect.y + 5))

    out_gameplay = "/Users/thiagocarvalho/.gemini/antigravity/brain/80cd5ff5-eb4f-4d2c-baf8-9e4a729ecc96/american_ninja_preview.png"
    pygame.image.save(screen, out_gameplay)
    print("Preview do gameplay do American Ninja salvo em:", out_gameplay)
    pygame.quit()

if __name__ == "__main__":
    generate_previews()
