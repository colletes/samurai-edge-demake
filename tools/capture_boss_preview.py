"""
tools/capture_boss_preview.py - Captura prévias visuais 3D do Final Boss Oni Gashadokuro.
Gera:
1. docs/screenshots/model_gashadokuro_snapshot.png (Visão completa no Model Inspector)
2. docs/screenshots/gashadokuro_5phases_preview.png (As 5 fases transmórficas em exibição 3D)
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import math
import pygame
from src.config import COLOR_GOLD, COLOR_WHITE
from src.entities.boss_oni import BossOni
from tools.model_inspector import ModelInspector, InspectorCamera


def capture_inspector_snapshot():
    pygame.init()
    inspector = ModelInspector(1280, 720, headless=True)
    idx = inspector.char_keys.index("gashadokuro")
    inspector.select_character(idx)
    inspector.set_pose_by_name("IDLE")

    # Renderizar alguns frames para estabilizar animação e partículas
    for _ in range(12):
        inspector.anim_time += 0.05
        inspector.screen.fill((18, 17, 24))
        inspector.draw_pedestal(inspector.screen)
        inspector.draw_character(inspector.screen)
        inspector.draw_hud(inspector.screen)

    out_path = os.path.join(ROOT, "docs", "screenshots", "model_gashadokuro_snapshot.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(inspector.screen, out_path)
    print(f"Snapshot do Model Inspector salvo em: {out_path}")

    # Captura em close-up focando o elmo e o rosto
    inspector.macro_focus = "head"
    inspector.camera.set_focus_target("head", is_colossal=True)
    inspector.camera.zoom = 2.6
    inspector.camera.target_z = 2.30
    for _ in range(6):
        inspector.anim_time += 0.05
        inspector.screen.fill((18, 17, 24))
        inspector.draw_pedestal(inspector.screen)
        inspector.draw_character(inspector.screen)
        inspector.draw_hud(inspector.screen)
    closeup_path = os.path.join(ROOT, "docs", "screenshots", "model_gashadokuro_closeup.png")
    pygame.image.save(inspector.screen, closeup_path)
    print(f"Snapshot Close-up do Elmo/Rosto salvo em: {closeup_path}")



def capture_five_phases():
    pygame.init()
    pygame.font.init()

    font_title = pygame.font.Font(None, 34)
    font_sub = pygame.font.Font(None, 20)
    font_phase = pygame.font.Font(None, 19)
    font_desc = pygame.font.Font(None, 15)

    width = 1200
    height = 540
    screen = pygame.Surface((width, height))
    screen.fill((15, 14, 22))

    # Grid sutil de fundo
    for x in range(0, width, 40):
        pygame.draw.line(screen, (24, 22, 34), (x, 0), (x, height), 1)
    for y in range(0, height, 40):
        pygame.draw.line(screen, (24, 22, 34), (0, y), (width, y), 1)

    # Header
    title_s = font_title.render("FINAL BOSS: ONI GASHADOKURO — 5 TRANSMORPHIC PHASES", True, (215, 125, 255))
    screen.blit(title_s, (width // 2 - title_s.get_width() // 2, 16))

    sub_s = font_sub.render("Colossal Skeletal Deity — Ancient Ivory Geometry, Curved Oni Horns & Spectral Miasma", True, (190, 185, 210))
    screen.blit(sub_s, (width // 2 - sub_s.get_width() // 2, 50))

    phases_info = [
        (0, "PHASE 1: BIPED", "Colossal Standing Titan", "Giant Dark Cleaver & Stomp"),
        (1, "PHASE 2: SERPENT", "Crawling Vertebrae Wyrm", "Low Slithering Ram & Charge"),
        (2, "PHASE 3: TORSO", "Ribcage & Forearms", "Violent Vaulting & Shockwave"),
        (3, "PHASE 4: CLUB", "Living Spiked Club", "Crushing Slam & Earth Ring"),
        (4, "PHASE 5: SKULL", "Colossal Flying Skull", "3-Stage Aerial Leaps & Flames"),
    ]

    boss = BossOni(0.0, 0.0)

    col_w = width // 5
    for idx, (p_num, title, sub, mechanics) in enumerate(phases_info):
        cx = col_w * idx + col_w // 2
        cy = 280

        # Card de fundo de cada fase
        card_rect = pygame.Rect(col_w * idx + 10, 85, col_w - 20, 435)
        pygame.draw.rect(screen, (22, 20, 32), card_rect, border_radius=8)
        pygame.draw.rect(screen, (75, 45, 110), card_rect, 1, border_radius=8)

        # Câmera específica para o slot
        cam = InspectorCamera(col_w - 20, 270)
        cam.height_fn = lambda wx, wy: 0.0
        cam.screen_x = (col_w - 20) // 2
        cam.screen_y = 210

        if p_num == 0:
            cam.target_z = 1.45
            cam.zoom = 1.15
        elif p_num == 1:
            cam.target_z = 0.50
            cam.zoom = 1.40
        elif p_num == 2:
            cam.target_z = 0.90
            cam.zoom = 1.30
        elif p_num == 3:
            cam.target_z = 1.00
            cam.zoom = 1.25
        elif p_num == 4:
            cam.target_z = 0.65
            cam.zoom = 1.55

        slot_surf = pygame.Surface((col_w - 20, 270), pygame.SRCALPHA)

        # Pedestal do slot
        sx0, sy0 = cam.apply(0.0, 0.0, 0.0)
        ped_r = int(60 * cam.zoom)
        pygame.draw.ellipse(slot_surf, (8, 6, 12, 190), (sx0 - ped_r, sy0 - ped_r // 3, ped_r * 2, ped_r * 2 // 3))

        # Renderizar boss na fase
        boss.set_phase(p_num)
        boss.time = 1.2
        if p_num == 0:
            boss.pose["stomp"] = 0.25
            boss.pose["head_up"] = 1.05
        elif p_num == 4:
            boss.pose["jaw"] = 0.25

        boss.render(slot_surf, cam, game_time=1.2)
        screen.blit(slot_surf, (card_rect.x, card_rect.y + 15))

        # Textos informativos
        p_surf = font_phase.render(title, True, (230, 150, 255))
        s_surf = font_desc.render(sub, True, COLOR_WHITE)
        m_surf = font_desc.render(mechanics, True, (160, 165, 185))

        screen.blit(p_surf, (cx - p_surf.get_width() // 2, card_rect.y + 310))
        screen.blit(s_surf, (cx - s_surf.get_width() // 2, card_rect.y + 338))
        screen.blit(m_surf, (cx - m_surf.get_width() // 2, card_rect.y + 360))

        # Badge indicador
        badge_rect = pygame.Rect(cx - 36, card_rect.y + 395, 72, 22)
        pygame.draw.rect(screen, (45, 25, 70), badge_rect, border_radius=4)
        pygame.draw.rect(screen, (160, 80, 240), badge_rect, 1, border_radius=4)
        b_txt = font_desc.render(f"2 HP • P{p_num+1}", True, (240, 220, 255))
        screen.blit(b_txt, (cx - b_txt.get_width() // 2, card_rect.y + 399))

    out_path = os.path.join(ROOT, "docs", "screenshots", "gashadokuro_5phases_preview.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(screen, out_path)
    print(f"Preview das 5 Fases salvo em: {out_path}")


if __name__ == "__main__":
    capture_inspector_snapshot()
    capture_five_phases()
