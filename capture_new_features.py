"""
Script de captura para documentar visualmente o novo asset de pólvora e o sistema de ajuda.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_GOLD
from src.isometric.camera import Camera
from src.world.map_data import GameMap
from src.entities.rifleman import Rifleman
from src.entities.blue_samurai import BlueSamurai
from src.entities.pickups import PowderPouch
from src.ui.character_select import CharacterSelectScreen
from src.ui.game_help import GameHelpModal

ARTIFACT_DIR = "/Users/thiagocarvalho/.gemini/antigravity/brain/e10d4a82-e079-4f09-8902-2500640f6ed3"

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    font_large = pygame.font.Font(None, 48)
    font_mid = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    # 1. Tela de Seleção de Personagens com botão [ H ] e [ ? ] em cada card e botão [ PT | EN ]
    from src.i18n import set_lang, LANG_PT, LANG_EN, t
    set_lang(LANG_PT)
    char_select = CharacterSelectScreen()
    char_select.p1_choice_idx = 5  # Teppo
    char_select.p2_choice_idx = 1  # Musashi
    char_select.render(screen, font_large, font_mid, font_small)
    p1_path = os.path.join(ARTIFACT_DIR, "char_select_with_help_btn.png")
    pygame.image.save(screen, p1_path)
    print("Salvo:", p1_path)

    # 2. Modal de Ajuda - Aba 1: Regras & Mecânicas Gerais
    char_select.help_modal.open(GameHelpModal.TAB_RULES)
    char_select.render(screen, font_large, font_mid, font_small)
    p2_path = os.path.join(ARTIFACT_DIR, "help_modal_rules.png")
    pygame.image.save(screen, p2_path)
    print("Salvo:", p2_path)

    # 3. Modal de Ajuda - Aba 3: Ficha Estratégica do Guerreiro (Teppo) em Português
    char_select.help_modal.open(GameHelpModal.TAB_FIGHTERS, fighter_idx=5)
    char_select.render(screen, font_large, font_mid, font_small)
    p3_path = os.path.join(ARTIFACT_DIR, "help_modal_fighter_strategy.png")
    pygame.image.save(screen, p3_path)
    print("Salvo:", p3_path)

    # 3b. Modal de Ajuda - Aba 3 em Inglês (demonstrando i18n padrão Boardbots)
    set_lang(LANG_EN)
    char_select.render(screen, font_large, font_mid, font_small)
    p3b_path = os.path.join(ARTIFACT_DIR, "help_modal_fighter_strategy_en.png")
    pygame.image.save(screen, p3b_path)
    print("Salvo:", p3b_path)
    set_lang(LANG_PT)

    # 4. Cena de Gameplay: Teppo sem munição avistando o novo Barril Voxel de Pólvora com Seta
    screen.fill(COLOR_BG)
    game_map = GameMap()
    camera = Camera(target_wx=10.5, target_wy=11.0)
    game_map.render_terrain(screen, camera, 1.0)

    teppo = Rifleman(wx=8.5, wy=11.0)
    teppo.has_ammo = False
    teppo.set_facing(12.5, 11.0)

    musashi = BlueSamurai(wx=14.0, wy=11.0)
    musashi.set_facing(8.5, 11.0)

    pouch = PowderPouch(wx=12.2, wy=11.0)
    pouch.is_active = True
    pouch.glow_timer = 2.0

    # Renderizar objetos com Y-sorting
    render_queue = [
        (teppo.wx + teppo.wy, 'fighter', teppo),
        (musashi.wx + musashi.wy, 'fighter', musashi),
        (pouch.wx + pouch.wy, 'pouch', pouch),
    ]
    for b in game_map.bamboos:
        if 6 <= b.wx <= 16 and 7 <= b.wy <= 15:
            render_queue.append((b.wx + b.wy, 'bamboo', b))
    render_queue.sort(key=lambda item: item[0])

    for _, itype, obj in render_queue:
        if itype == 'bamboo':
            obj.render(screen, camera, 1.0)
        elif itype == 'fighter':
            obj.render(screen, camera)
        elif itype == 'pouch':
            obj.render(screen, camera, font_small)

    # Renderizar bússola tática do Teppo (como em main.py)
    dist = math.hypot(pouch.wx - teppo.wx, pouch.wy - teppo.wy)
    fsx, fsy = camera.apply(teppo.wx, teppo.wy, 1.4)
    psx, psy = camera.apply(pouch.wx, pouch.wy, 0.4)
    sdx = psx - fsx
    sdy = psy - fsy
    s_dist = math.hypot(sdx, sdy)
    if s_dist > 0.001:
        nx = sdx / s_dist
        ny = sdy / s_dist
        ptr_dist = 42
        ptr_x = fsx + nx * ptr_dist
        ptr_y = fsy + ny * ptr_dist
        perp_x = -ny * 7
        perp_y = nx * 7
        p_tip = (ptr_x + nx * 8, ptr_y + ny * 8)
        p_left = (ptr_x - nx * 6 + perp_x, ptr_y - ny * 6 + perp_y)
        p_right = (ptr_x - nx * 6 - perp_x, ptr_y - ny * 6 - perp_y)
        pygame.draw.polygon(screen, (15, 18, 16), [p_tip, p_left, p_right])
        pygame.draw.polygon(screen, (255, 215, 40), [p_tip, p_left, p_right])
        pygame.draw.polygon(screen, (160, 110, 20), [p_tip, p_left, p_right], 1)
        dist_lbl = font_small.render(t("powder_tracker", dist=dist), True, (255, 240, 160))
        d_bg = pygame.Rect(ptr_x - dist_lbl.get_width() // 2 - 4, ptr_y - 24, dist_lbl.get_width() + 8, 16)
        pygame.draw.rect(screen, (18, 24, 21), d_bg, border_radius=4)
        pygame.draw.rect(screen, (255, 210, 50), d_bg, 1, border_radius=4)
        screen.blit(dist_lbl, (d_bg.x + 4, d_bg.y + 1))

    # Painel de HUD
    panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 14, 480, 54)
    pygame.draw.rect(screen, (20, 24, 22, 210), panel_rect, border_radius=8)
    pygame.draw.rect(screen, (60, 75, 68), panel_rect, 2, border_radius=8)
    t1 = font_mid.render("TEPPO  0", True, (225, 170, 100))
    t2 = font_mid.render("0  MUSASHI", True, (95, 170, 255))
    screen.blit(t1, (panel_rect.x + 20, panel_rect.y + 16))
    screen.blit(t2, (panel_rect.right - t2.get_width() - 20, panel_rect.y + 16))
    m_surf = font_small.render("[1P vs IA]", True, COLOR_GOLD)
    screen.blit(m_surf, (panel_rect.centerx - m_surf.get_width() // 2, panel_rect.y + 18))

    p4_path = os.path.join(ARTIFACT_DIR, "teppo_gunpowder_preview.png")
    pygame.image.save(screen, p4_path)
    print("Salvo:", p4_path)

    pygame.quit()

if __name__ == "__main__":
    main()
