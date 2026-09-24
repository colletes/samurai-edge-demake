"""
Gera captura de preview do gameplay em alta definição com os sprites HD-2D de Kenshi e Murasaki (Kunoichi Roxa).
Salva em 'hd2d_gameplay_preview.png'.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_GOLD, COLOR_WHITE,
    COLOR_RED_AURA, COLOR_PURPLE_AURA
)
from src.isometric.camera import Camera
from src.world.map_data import GameMap
from src.entities.red_samurai import RedSamurai
from src.entities.purple_ninja import PurpleNinja
from src.effects.particles import AmbientLeafParticle, FloatingBanner

def generate_hd2d_preview():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    font_large = pygame.font.Font(None, 44)
    font_mid = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 18)

    game_map = GameMap()
    camera = Camera(target_wx=11.0, target_wy=11.0)

    # Posicionar Kenshi e Murasaki na ponte da arena
    kenshi = RedSamurai(wx=10.0, wy=11.0)
    murasaki = PurpleNinja(wx=12.2, wy=11.0)

    kenshi.set_facing(murasaki.wx, murasaki.wy) # Olha para a direita
    murasaki.set_facing(kenshi.wx, kenshi.wy)   # Olha para a esquerda

    # Efeitos visuais
    kenshi.state = "ATTACK"
    kenshi.slash_trail_points = [(9.2, 11.0), (10.0, 11.0)]

    particles = []
    banners = [
        FloatingBanner("HD-2D EDITION", 11.1, 11.0, wz=2.2, color=COLOR_GOLD, duration=10.0),
        FloatingBanner("KENSHI vs MURASAKI", 11.1, 11.0, wz=1.8, color=(140, 220, 255), duration=10.0)
    ]
    leaves = [AmbientLeafParticle(game_map.cols, game_map.rows) for _ in range(40)]

    # Renderizar terreno
    screen.fill(COLOR_BG)
    game_map.render_terrain(screen, camera, 2.0)

    # Fila de renderização com Y-sorting
    render_queue = []
    for b in game_map.bamboos:
        render_queue.append((b.wx + b.wy, 'bamboo', b))
    for r in game_map.rocks:
        render_queue.append((r.wx + r.wy, 'rock', r))
    if game_map.well:
        render_queue.append((game_map.well.wx + game_map.well.wy, 'well', game_map.well))

    render_queue.append((kenshi.wx + kenshi.wy, 'fighter', kenshi))
    render_queue.append((murasaki.wx + murasaki.wy, 'fighter', murasaki))

    render_queue.sort(key=lambda item: item[0])

    for _, item_type, obj in render_queue:
        if item_type == 'bamboo':
            obj.render(screen, camera, 2.0)
        elif item_type in ('rock', 'well'):
            obj.render(screen, camera)
        elif item_type == 'fighter':
            obj.render(screen, camera)

    for leaf in leaves:
        leaf.render(screen, camera)
    for banner in banners:
        banner.render(screen, camera, font_mid)

    # Moldura HUD Superior HD-2D
    hud_panel = pygame.Rect(SCREEN_WIDTH // 2 - 280, 16, 560, 48)
    pygame.draw.rect(screen, (20, 26, 24), hud_panel, border_radius=8)
    pygame.draw.rect(screen, COLOR_GOLD, hud_panel, 1, border_radius=8)

    title_s = font_large.render("SAMURAI EDGE: HD-2D PROTOTYPE", True, COLOR_GOLD)
    screen.blit(title_s, (SCREEN_WIDTH // 2 - title_s.get_width() // 2, 26))

    # Info dos Lutadores
    k_badge = font_mid.render("1P: KENSHI [Iai-Jutsu]", True, COLOR_RED_AURA)
    m_badge = font_mid.render("2P: MURASAKI [Kusarigama]", True, COLOR_PURPLE_AURA)
    screen.blit(k_badge, (30, 24))
    screen.blit(m_badge, (SCREEN_WIDTH - m_badge.get_width() - 30, 24))

    out_file = "hd2d_gameplay_preview.png"
    pygame.image.save(screen, out_file)
    print(f"[OK] Preview salvo em: {out_file}")

if __name__ == "__main__":
    generate_hd2d_preview()
