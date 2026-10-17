"""
Gera preview visual dos modelos voxel de Goro e Ichi (Ciclo 3):
- Goro: Idle com Kuwa no ombro, Ataque vertical descendente Kuwa Cleave e Guarda de Ferro transversal.
- Ichi: Idle serena com Shikomizue à frente, Saque relâmpago Gyaku-Iai e Postura de Escuta sensorial.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE
from src.isometric.camera import Camera
from src.entities.voxel_models import render_voxel_humanoid

def generate_preview():
    pygame.init()
    pygame.font.init()

    font_title = pygame.font.Font(None, 36)
    font_sub = pygame.font.Font(None, 22)
    font_badge = pygame.font.Font(None, 18)

    width = 960
    height = 540
    screen = pygame.Surface((width, height))
    screen.fill((16, 16, 22))

    # Grid de fundo sutil
    for x in range(0, width, 40):
        pygame.draw.line(screen, (24, 24, 32), (x, 0), (x, height), 1)
    for y in range(0, height, 40):
        pygame.draw.line(screen, (24, 24, 32), (0, y), (width, y), 1)

    # Título do Header
    title_surf = font_title.render("CYCLE 3 VOXEL RIGS: GORO & ICHI", True, COLOR_GOLD)
    screen.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 20))

    sub_surf = font_sub.render("High-Fidelity Feudal Models: Kuwa Peasant Rebel & Blind Cane-Sword Master", True, (190, 195, 205))
    screen.blit(sub_surf, (width // 2 - sub_surf.get_width() // 2, 60))

    # Slots de exibição
    slots = [
        # (x_center, y_center, char, state, state_timer, extra_props, label, sublabel)
        (130, 260, "goro", "IDLE", 0.0, {}, "GORO", "Shoulder Rest (Steel Kuwa)"),
        (290, 260, "goro", "ATTACK", 0.16, {}, "GORO", "Kuwa Cleave Chop"),
        (450, 260, "goro", "DEFEND", 0.10, {"pose": "iron_guard"}, "GORO", "Iron Guard Stance"),

        (570, 260, "ichi", "IDLE", 0.0, {}, "ICHI", "Serene Cane Stance"),
        (720, 260, "ichi", "ATTACK", 0.12, {}, "ICHI", "Gyaku-Iai Reverse Flash"),
        (870, 260, "ichi", "DODGE", 0.15, {"pose": "listen_stance"}, "ICHI", "Sharp Hearing Evasion"),
    ]

    for (cx, cy, char, state, st_timer, extra, label, sublabel) in slots:
        char_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        cam = Camera(target_wx=5.0, target_wy=5.0)
        cam.screen_x = 100
        cam.screen_y = 135

        render_voxel_humanoid(
            surface=char_surf,
            camera=cam,
            wx=5.0, wy=5.0, wz=0.0,
            facing_x=1.0, facing_y=0.0,
            state=state,
            state_timer=st_timer,
            is_alive=True,
            char_type=char,
            walk_timer=0.5,
            alpha=255,
            is_moving=(state == "DODGE"),
            extra_props=extra
        )

        scaled_w = int(200 * 2.2)
        scaled_h = int(200 * 2.2)
        scaled_surf = pygame.transform.scale(char_surf, (scaled_w, scaled_h))

        # Pedestal circular posicionado exatamente na base dos pés
        ped_y = cy + 100
        pedestal = pygame.Surface((130, 40), pygame.SRCALPHA)
        ped_col = (52, 38, 54, 180) if char == "ichi" else (36, 44, 56, 180)
        pygame.draw.ellipse(pedestal, ped_col, (0, 0, 130, 40))
        ped_border = (160, 120, 170, 230) if char == "ichi" else (100, 130, 160, 230)
        pygame.draw.ellipse(pedestal, ped_border, (0, 0, 130, 40), 2)
        screen.blit(pedestal, (cx - 65, ped_y - 15))

        # Personagem com pés repousando sobre o pedestal
        char_top_y = ped_y - int(135 * 2.2)
        screen.blit(scaled_surf, (cx - scaled_w // 2, char_top_y))

        # Rótulos posicionados abaixo do pedestal
        lbl_col = (130, 180, 240) if char == "goro" else (225, 155, 240)
        lbl_surf = font_sub.render(label, True, lbl_col)
        screen.blit(lbl_surf, (cx - lbl_surf.get_width() // 2, ped_y + 35))

        sub_surf = font_badge.render(sublabel, True, (180, 185, 195))
        screen.blit(sub_surf, (cx - sub_surf.get_width() // 2, ped_y + 62))

    # Linha divisória
    pygame.draw.line(screen, (50, 52, 65), (510, 100), (510, 480), 2)

    out_path = os.path.join(ROOT, "docs", "screenshots", "goro_ichi_voxel_preview.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(screen, out_path)
    print(f"Preview salvo com sucesso em: {out_path}")

if __name__ == "__main__":
    generate_preview()
