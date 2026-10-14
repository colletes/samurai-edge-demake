"""
Gera preview visual dos modelos voxel de Benkei e O-Rin (Ciclo 2):
- Benkei: Idle com Naginata imponente, Estocada frontal colossal e Investida desarmado.
- O-Rin: Idle dedilhando Shamisen, Arco cortante Kamaitachi e Onda de Choque Ressonante 360°.
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
    screen.fill((16, 15, 20))

    # Grid de fundo sutil
    for x in range(0, width, 40):
        pygame.draw.line(screen, (24, 22, 30), (x, 0), (x, height), 1)
    for y in range(0, height, 40):
        pygame.draw.line(screen, (24, 22, 30), (0, y), (width, y), 1)

    # Título do Header
    title_surf = font_title.render("CYCLE 2 VOXEL RIGS: BENKEI & O-RIN", True, COLOR_GOLD)
    screen.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 20))

    sub_surf = font_sub.render("High-Fidelity Feudal Models: Walking Tank Sōhei & Acoustic Courtesan Minstrel", True, (190, 185, 195))
    screen.blit(sub_surf, (width // 2 - sub_surf.get_width() // 2, 60))

    # Definir posições e câmeras para cada modelo em exibição
    slots = [
        # (x_center, y_center, char, state, state_timer, extra_props, label, sublabel)
        (130, 260, "benkei", "IDLE", 0.0, {"has_naginata": True}, "BENKEI", "Guard Posture (Naginata)"),
        (290, 260, "benkei", "ATTACK", 0.14, {"has_naginata": True}, "BENKEI", "Colossal Spear Thrust"),
        (450, 260, "benkei", "TACKLE_CHARGE", 0.20, {"has_naginata": False, "is_charging": True}, "BENKEI", "Unarmed Stun Tackle"),

        (570, 260, "orin", "IDLE", 0.0, {}, "O-RIN", "Shamisen Melodic Idle"),
        (720, 260, "orin", "ATTACK", 0.08, {}, "O-RIN", "Kamaitachi Vacuum Pluck"),
        (870, 260, "orin", "RESONANCE", 0.15, {"is_resonance": True}, "O-RIN", "360° Acoustic Resonance"),
    ]

    for (cx, cy, char, state, st_timer, extra, label, sublabel) in slots:
        # Superfície individual para renderizar o personagem e depois dar zoom
        char_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        cam = Camera(target_wx=5.0, target_wy=5.0)
        cam.screen_x = 100
        cam.screen_y = 135

        # Renderizar modelo voxel
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
            is_moving=(state == "TACKLE_CHARGE"),
            extra_props=extra
        )

        # Upscale 2.2x com pixel-art crisp
        scaled_w = int(200 * 2.2)
        scaled_h = int(200 * 2.2)
        scaled_surf = pygame.transform.scale(char_surf, (scaled_w, scaled_h))

        # Pedestal circular sob o personagem
        pedestal = pygame.Surface((130, 48), pygame.SRCALPHA)
        ped_col = (45, 38, 52, 170) if char == "orin" else (48, 42, 38, 170)
        pygame.draw.ellipse(pedestal, ped_col, (0, 0, 130, 48))
        pygame.draw.ellipse(pedestal, (90, 80, 75, 220), (0, 0, 130, 48), 2)
        screen.blit(pedestal, (cx - 65, cy + 55))

        # Desenhar personagem ampliado
        screen.blit(scaled_surf, (cx - scaled_w // 2, cy - 165))

        # Rótulos
        lbl_col = (235, 180, 80) if char == "benkei" else (225, 90, 120)
        lbl_surf = font_sub.render(label, True, lbl_col)
        screen.blit(lbl_surf, (cx - lbl_surf.get_width() // 2, cy + 120))

        sub_surf = font_badge.render(sublabel, True, (170, 170, 180))
        screen.blit(sub_surf, (cx - sub_surf.get_width() // 2, cy + 148))

    # Linha divisória entre Benkei e O-Rin
    pygame.draw.line(screen, (50, 45, 60), (510, 100), (510, 480), 2)

    out_path = "docs/screenshots/benkei_orin_voxel_preview.png"
    pygame.image.save(screen, out_path)
    print(f"Preview salvo com sucesso em: {out_path}")

if __name__ == "__main__":
    generate_preview()
