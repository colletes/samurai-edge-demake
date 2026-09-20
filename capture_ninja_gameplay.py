"""
Gera preview do gameplay do Ninja Amarelo com a kunai em ação.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_GOLD, COLOR_YELLOW_AURA, COLOR_BLUE_AURA
)
from src.isometric.camera import Camera
from src.world.map_data import GameMap
from src.entities.yellow_ninja import YellowNinja
from src.entities.blue_samurai import BlueSamurai
from src.entities.projectile import KunaiProjectile
from src.effects.particles import AmbientLeafParticle, FloatingBanner

def generate_ninja_gameplay_preview():
    pygame.init()
    pygame.font.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    font_large = pygame.font.Font(None, 48)
    font_mid = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    game_map = GameMap()
    ninja = YellowNinja(wx=8.5, wy=11.0)
    musashi = BlueSamurai(wx=13.5, wy=11.0)
    ninja.set_facing(musashi.wx, musashi.wy)
    musashi.set_facing(ninja.wx, ninja.wy)

    camera = Camera(target_wx=11.0, target_wy=11.0)

    # Kunai arremessada no ar voando em direção ao Musashi
    kunai = KunaiProjectile(wx=11.0, wy=11.0, wz=0.6, dir_x=1.0, dir_y=0.0, owner=ninja)
    projectiles = [kunai]

    particles = []
    banners = [
        FloatingBanner("KUNAI THROW!", 11.0, 11.0, wz=1.8, color=(255, 220, 50), duration=5.0)
    ]
    leaves = [AmbientLeafParticle(game_map.cols, game_map.rows) for _ in range(45)]

    # Fatiar alguns bambus próximos
    for b in game_map.bamboos:
        if 9.0 <= b.wx <= 10.0 and 8.0 <= b.wy <= 12.0:
            part = b.cut((1.0, 0.2))
            if part:
                particles.append(part)

    # Renderização da Cena
    screen.fill(COLOR_BG)
    game_map.render_terrain(screen, camera, 1.5)

    render_queue = []
    for b in game_map.bamboos:
        render_queue.append((b.wy, 'bamboo', b))
    for r in game_map.rocks:
        render_queue.append((r.wy, 'rock', r))
    if game_map.well:
        render_queue.append((game_map.well.wy, 'well', game_map.well))
    for t in game_map.trees:
        render_queue.append((t.wy, 'tree', t))

    render_queue.append((ninja.wy, 'fighter', ninja))
    render_queue.append((musashi.wy, 'fighter', musashi))

    for proj in projectiles:
        render_queue.append((proj.wy, 'projectile', proj))

    for p in particles:
        if hasattr(p, 'wy'):
            render_queue.append((p.wy, 'particle', p))

    render_queue.sort(key=lambda item: item[0])

    for _, itype, obj in render_queue:
        if itype == 'bamboo':
            obj.render(screen, camera, 1.5)
        elif itype in ('rock', 'well', 'tree', 'fighter', 'projectile', 'particle'):
            obj.render(screen, camera)

    for leaf in leaves:
        leaf.render(screen, camera)

    for banner in banners:
        banner.render(screen, camera, font_mid)

    # HUD
    panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 14, 480, 54)
    pygame.draw.rect(screen, (20, 24, 22, 210), panel_rect, border_radius=8)
    pygame.draw.rect(screen, (60, 75, 68), panel_rect, 2, border_radius=8)

    p1_title = font_mid.render("HANZO  0", True, COLOR_YELLOW_AURA)
    p2_title = font_mid.render("0  MUSASHI", True, COLOR_BLUE_AURA)
    screen.blit(p1_title, (panel_rect.x + 20, panel_rect.y + 16))
    screen.blit(p2_title, (panel_rect.right - p2_title.get_width() - 20, panel_rect.y + 16))

    mode_surf = font_small.render("[1P vs IA]", True, COLOR_GOLD)
    screen.blit(mode_surf, (panel_rect.centerx - mode_surf.get_width() // 2, panel_rect.y + 18))

    # Botão voltar para a seleção
    select_btn = pygame.Rect(25, 20, 180, 32)
    pygame.draw.rect(screen, (26, 34, 30, 210), select_btn, border_radius=6)
    pygame.draw.rect(screen, COLOR_GOLD, select_btn, 1, border_radius=6)
    sel_txt = font_small.render("<< MUDAR GUERREIROS", True, COLOR_GOLD)
    screen.blit(sel_txt, (select_btn.centerx - sel_txt.get_width() // 2, select_btn.y + 7))

    footer_rect = pygame.Rect(20, SCREEN_HEIGHT - 48, SCREEN_WIDTH - 40, 36)
    pygame.draw.rect(screen, (16, 20, 18, 200), footer_rect, border_radius=6)
    c1 = font_small.render("P1 (HANZO): W/A/S/D | E = Estocada | R = Arremessar Kunai", True, (255, 235, 180))
    c2 = font_small.render("P2 (MUSASHI): Setas | U = 3-Cortes | I = Parry", True, (205, 225, 245))
    screen.blit(c1, (30, SCREEN_HEIGHT - 40))
    screen.blit(c2, (SCREEN_WIDTH // 2 - c2.get_width() // 2 - 30, SCREEN_HEIGHT - 40))

    settings_btn_rect = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 44, 180, 28)
    pygame.draw.rect(screen, (40, 52, 45), settings_btn_rect, border_radius=4)
    pygame.draw.rect(screen, COLOR_GOLD, settings_btn_rect, 1, border_radius=4)
    c3 = font_small.render("[C] Controles / Settings", True, COLOR_GOLD)
    screen.blit(c3, (settings_btn_rect.centerx - c3.get_width() // 2, settings_btn_rect.y + 5))

    out_path = "/Users/thiagocarvalho/.gemini/antigravity/brain/80cd5ff5-eb4f-4d2c-baf8-9e4a729ecc96/ninja_gameplay_preview.png"
    pygame.image.save(screen, out_path)
    print("Preview do gameplay do Ninja salvo em:", out_path)
    pygame.quit()

if __name__ == "__main__":
    generate_ninja_gameplay_preview()
