"""
Gera preview visual dos modelos voxel de Valerius e Seimei (Ciclo 4):
- Valerius: Idle cerimonial com Foice Fúnebre no ombro, Ceifada Ampla (Soul Reap) e Visão Traseira (180° oclusão do sobretudo).
- Seimei: Idle serena com Talismã Ofuda, Lançamento Místico de Selo e Visão Traseira (Cabelos longos e laço Agemaki).
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame
from src.config import COLOR_GOLD, COLOR_WHITE
from src.isometric.camera import Camera
from src.entities.voxel_models import render_voxel_humanoid

def generate_preview():
    pygame.init()
    pygame.font.init()

    font_title = pygame.font.Font(None, 34)
    font_sub = pygame.font.Font(None, 20)
    font_badge = pygame.font.Font(None, 16)

    width = 1000
    height = 560
    screen = pygame.Surface((width, height))
    screen.fill((14, 15, 20))

    # Grid de fundo sutil
    for x in range(0, width, 40):
        pygame.draw.line(screen, (22, 24, 30), (x, 0), (x, height), 1)
    for y in range(0, height, 40):
        pygame.draw.line(screen, (22, 24, 30), (0, y), (width, y), 1)

    # Título do Header
    title_surf = font_title.render("CYCLE 4 VOXEL RIGS: VALERIUS & SEIMEI", True, COLOR_GOLD)
    screen.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 18))

    sub_surf = font_sub.render("High-Fidelity 3D Anime Models: Prussian Necromancer & Heian Onmyoji Master", True, (190, 195, 205))
    screen.blit(sub_surf, (width // 2 - sub_surf.get_width() // 2, 54))

    # Slots de exibição
    slots = [
        # (x_center, y_center, char, state, state_timer, extra_props, facing, label, sublabel)
        (100, 240, "valerius", "IDLE", 0.0, {}, (1.0, 0.0), "VALERIUS", "Ceremonial Scythe Rest"),
        (260, 240, "valerius", "ATTACK", 0.45, {}, (1.0, 0.0), "VALERIUS", "Soul Reap Scythe Slash"),
        (420, 240, "valerius", "IDLE", 0.0, {}, (-1.0, 0.0), "VALERIUS", "Back Coat Tails (180°)"),

        (580, 240, "seimei", "IDLE", 0.0, {}, (1.0, 0.0), "SEIMEI", "Ofuda Talisman Stance"),
        (740, 240, "seimei", "ATTACK", 0.50, {}, (1.0, 0.0), "SEIMEI", "Spiritual Seal Release"),
        (900, 240, "seimei", "IDLE", 0.0, {}, (-1.0, 0.0), "SEIMEI", "Flowing Hair & Eboshi (180°)"),
    ]

    for (cx, cy, char, state, st_timer, extra, facing, label, sublabel) in slots:
        char_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        cam = Camera(target_wx=5.0, target_wy=5.0)
        cam.screen_x = 100
        cam.screen_y = 135

        render_voxel_humanoid(
            surface=char_surf,
            camera=cam,
            wx=5.0, wy=5.0, wz=0.0,
            facing_x=facing[0], facing_y=facing[1],
            state=state,
            state_timer=st_timer,
            is_alive=True,
            char_type=char,
            walk_timer=0.5,
            alpha=255,
            is_moving=False,
            extra_props=extra
        )

        scaled_w = int(200 * 2.2)
        scaled_h = int(200 * 2.2)
        scaled_surf = pygame.transform.scale(char_surf, (scaled_w, scaled_h))

        # Pedestal circular posicionado na base dos pés
        ped_y = cy + 130
        pedestal = pygame.Surface((130, 40), pygame.SRCALPHA)
        ped_col = (45, 55, 75, 180) if char == "valerius" else (65, 45, 80, 180)
        ped_border = (120, 150, 190, 230) if char == "valerius" else (170, 130, 205, 230)
        pygame.draw.ellipse(pedestal, ped_col, (0, 0, 130, 40))
        pygame.draw.ellipse(pedestal, ped_border, (0, 0, 130, 40), 2)
        screen.blit(pedestal, (cx - 65, ped_y - 15))

        # Personagem sobre o pedestal
        char_top_y = ped_y - int(135 * 2.2)
        screen.blit(scaled_surf, (cx - scaled_w // 2, char_top_y))

        # Badge do Nome
        b_col = (45, 55, 75) if char == "valerius" else (65, 45, 80)
        t_col = (215, 230, 255) if char == "valerius" else (245, 220, 255)
        badge = font_badge.render(label, True, t_col)
        bw, bh = badge.get_width() + 14, badge.get_height() + 4
        bx, by = cx - bw // 2, ped_y + 30
        pygame.draw.rect(screen, b_col, (bx, by, bw, bh), border_radius=4)
        screen.blit(badge, (bx + 7, by + 2))

        # Subtítulo descritivo
        sub_t = font_sub.render(sublabel, True, (170, 175, 185))
        screen.blit(sub_t, (cx - sub_t.get_width() // 2, ped_y + 52))

    # Divisória central
    pygame.draw.line(screen, (38, 40, 52), (500, 90), (500, 520), 2)

    os.makedirs("docs/screenshots", exist_ok=True)
    out_path = "docs/screenshots/valerius_seimei_preview.png"
    pygame.image.save(screen, out_path)
    print(f"[OK] Preview salvo em: {out_path}")

if __name__ == "__main__":
    generate_preview()
