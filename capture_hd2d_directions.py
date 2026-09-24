"""
capture_hd2d_directions.py
Gera uma captura detalhada demonstrando as 4 direções isométricas (Frente-Direita, Frente-Esquerda,
Costas-Direita, Costas-Esquerda) e ciclos de caminhada e ataque para Kenshi e Murasaki.
Salva em 'hd2d_directions_preview.png'.
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

def generate_directions_preview():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    font_large = pygame.font.Font(None, 40)
    font_mid = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 18)

    game_map = GameMap()
    camera = Camera(target_wx=11.0, target_wy=11.0)

    # 4 pares de combatentes demonstrando os 4 quadrantes isométricos:
    # 1. Frente-Direita (SE): wx=9.5, wy=9.5  (facing_x=1.0, facing_y=0.0)
    # 2. Frente-Esquerda (SW): wx=9.5, wy=12.5 (facing_x=0.0, facing_y=1.0)
    # 3. Costas-Direita (NE): wx=12.5, wy=9.5  (facing_x=0.0, facing_y=-1.0)
    # 4. Costas-Esquerda (NW): wx=12.5, wy=12.5 (facing_x=-1.0, facing_y=0.0)

    fighters = [
        # Quadrante 1: Frente-Direita (Sul/Leste)
        {"f": RedSamurai(9.5, 9.5), "dir": (1.0, 0.0), "label": "1. Frente-Direita (SE)", "walk": 1.5},
        {"f": PurpleNinja(10.5, 9.5), "dir": (1.0, 0.0), "label": "1. Frente-Direita (SE)", "walk": 2.6},

        # Quadrante 2: Frente-Esquerda (Sul/Oeste)
        {"f": RedSamurai(9.5, 12.5), "dir": (0.0, 1.0), "label": "2. Frente-Esquerda (SW)", "walk": 3.8},
        {"f": PurpleNinja(10.5, 12.5), "dir": (0.0, 1.0), "label": "2. Frente-Esquerda (SW)", "walk": 0.2},

        # Quadrante 3: Costas-Direita (Norte/Leste)
        {"f": RedSamurai(12.0, 9.5), "dir": (0.0, -1.0), "label": "3. Costas-Direita (NE)", "walk": 1.5},
        {"f": PurpleNinja(13.0, 9.5), "dir": (0.0, -1.0), "label": "3. Costas-Direita (NE)", "walk": 2.6},

        # Quadrante 4: Costas-Esquerda (Norte/Oeste)
        {"f": RedSamurai(12.0, 12.5), "dir": (-1.0, 0.0), "label": "4. Costas-Esquerda (NW)", "walk": 3.8},
        {"f": PurpleNinja(13.0, 12.5), "dir": (-1.0, 0.0), "label": "4. Costas-Esquerda (NW)", "walk": 0.2},
    ]

    for item in fighters:
        f = item["f"]
        dx, dy = item["dir"]
        f.facing_x = dx
        f.facing_y = dy
        f.walk_cycle = item["walk"]
        f.is_moving = True

    screen.fill(COLOR_BG)
    game_map.render_terrain(screen, camera, 0.0)

    # Y-sorting
    render_queue = []
    for b in game_map.bamboos:
        render_queue.append((b.wx + b.wy, 'bamboo', b))
    for r in game_map.rocks:
        render_queue.append((r.wx + r.wy, 'rock', r))
    if game_map.well:
        render_queue.append((game_map.well.wx + game_map.well.wy, 'well', game_map.well))

    for item in fighters:
        f = item["f"]
        render_queue.append((f.wx + f.wy, 'fighter', f))

    render_queue.sort(key=lambda x: x[0])

    for _, item_type, obj in render_queue:
        if item_type == 'bamboo':
            obj.render(screen, camera, 0.0)
        elif item_type in ('rock', 'well'):
            obj.render(screen, camera)
        elif item_type == 'fighter':
            obj.render(screen, camera)

    # Rótulos para cada quadrante na tela
    quadrant_labels = [
        (9.5, 9.0, "FRENTE-DIR (SE)", (255, 120, 120)),
        (9.5, 13.0, "FRENTE-ESQ (SW)", (255, 200, 120)),
        (12.5, 9.0, "COSTAS-DIR (NE)", (120, 200, 255)),
        (12.5, 13.0, "COSTAS-ESQ (NW)", (200, 140, 255)),
    ]
    for qx, qy, txt, col in quadrant_labels:
        sx, sy = camera.apply(qx, qy, 0.0)
        lbl_surf = font_small.render(txt, True, col)
        lbl_bg = pygame.Rect(sx - lbl_surf.get_width() // 2 - 4, sy + 14, lbl_surf.get_width() + 8, 18)
        pygame.draw.rect(screen, (15, 22, 20), lbl_bg, border_radius=4)
        pygame.draw.rect(screen, col, lbl_bg, 1, border_radius=4)
        screen.blit(lbl_surf, (lbl_bg.x + 4, lbl_bg.y + 2))

    # Título do painel superior
    header_rect = pygame.Rect(SCREEN_WIDTH // 2 - 320, 16, 640, 46)
    pygame.draw.rect(screen, (20, 26, 24), header_rect, border_radius=8)
    pygame.draw.rect(screen, COLOR_GOLD, header_rect, 1, border_radius=8)
    title = font_large.render("ANIMAÇÕES MULTIDIRECIONAIS HD-2D (4 QUADRANTES)", True, COLOR_GOLD)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 26))

    out_file = "hd2d_directions_preview.png"
    pygame.image.save(screen, out_file)
    print(f"[OK] Preview salvo em: {out_file}")

if __name__ == "__main__":
    generate_directions_preview()
