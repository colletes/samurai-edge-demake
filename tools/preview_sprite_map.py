"""
tools/preview_sprite_map.py
Gera o Mapa Visual Completo de Sprites HD-2D (hd2d_sprite_map.png)
composta em alta definição com grade pixel-art, nomes de animação,
demonstração dos ciclos de Idle (Frente e Costas) e Caminhada em todas as 4 direções isométricas (SE, SW, NE, NW).
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

def create_sprite_map_preview():
    pygame.init()
    pygame.display.set_mode((1, 1))
    pygame.font.init()

    W = 1200
    H = 920
    screen = pygame.Surface((W, H))
    screen.fill((20, 22, 28))

    font_title = pygame.font.Font(None, 34)
    font_section = pygame.font.Font(None, 24)
    font_label = pygame.font.Font(None, 18)
    font_small = pygame.font.Font(None, 15)

    # Grade decorativa de fundo
    for x in range(0, W, 24):
        pygame.draw.line(screen, (28, 30, 38), (x, 0), (x, H), 1)
    for y in range(0, H, 24):
        pygame.draw.line(screen, (28, 30, 38), (0, y), (W, y), 1)

    # Top Header Banner
    header_rect = pygame.Rect(40, 20, W - 80, 54)
    pygame.draw.rect(screen, (16, 18, 24), header_rect, border_radius=8)
    pygame.draw.rect(screen, (240, 200, 80), header_rect, 2, border_radius=8)
    title_surf = font_title.render("MAPA COMPLETO DE SPRITES HD-2D — KENSHI & MURASAKI", True, (245, 215, 95))
    screen.blit(title_surf, (W // 2 - title_surf.get_width() // 2, 35))

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sprites_dir = os.path.join(base_dir, "assets", "sprites")

    CHARACTERS = [
        ("KENSHI — A Espadachim Lendária (Iaijutsu)", "kenshi", 50, (230, 70, 70)),
        ("MURASAKI — A Kunoichi da Foice (Kusarigama)", "murasaki", 620, (180, 90, 240))
    ]

    ROW_SPECS = [
        ("Idle Frente (SE)", "front_idle", False, 4, "Respiração / Guarda"),
        ("Idle Costas (NE)", "back_idle", False, 4, "Respiração / Costas"),
        ("Walk Frente-Dir (SE)", "front_walk", False, 4, "Passadas 1..4 Frente"),
        ("Walk Frente-Esq (SW)", "front_walk", True, 4, "Passadas 1..4 Espelhado"),
        ("Walk Costas-Dir (NE)", "back_walk", False, 4, "Passadas 1..4 Costas"),
        ("Walk Costas-Esq (NW)", "back_walk", True, 4, "Passadas 1..4 Costas Esp."),
        ("Ataque & Reações", "special", False, 5, "Attack, Back Atk, Recovery, Stun, Dead")
    ]

    for char_title, char_key, start_x, theme_color in CHARACTERS:
        # Coluna do Personagem
        col_w = 530
        panel_rect = pygame.Rect(start_x, 90, col_w, H - 120)
        pygame.draw.rect(screen, (15, 17, 22), panel_rect, border_radius=8)
        pygame.draw.rect(screen, theme_color, panel_rect, 1, border_radius=8)

        # Cabeçalho do Personagem
        ch_banner = pygame.Rect(start_x, 90, col_w, 36)
        pygame.draw.rect(screen, (24, 26, 34), ch_banner, border_top_left_radius=8, border_top_right_radius=8)
        ch_surf = font_section.render(char_title, True, theme_color)
        screen.blit(ch_surf, (start_x + 14, 98))

        char_dir = os.path.join(sprites_dir, char_key)
        start_y = 140
        row_height = 104

        for r_idx, (row_label, file_prefix, is_flip, num_frames, desc) in enumerate(ROW_SPECS):
            ry = start_y + r_idx * row_height

            # Etiqueta da Linha
            lbl_surf = font_label.render(row_label, True, (230, 230, 230))
            screen.blit(lbl_surf, (start_x + 14, ry + 12))
            desc_surf = font_small.render(desc, True, (120, 130, 145))
            screen.blit(desc_surf, (start_x + 14, ry + 32))

            # Baseline line
            baseline_y = ry + 92
            pygame.draw.line(screen, (38, 42, 54), (start_x + 165, baseline_y), (start_x + col_w - 15, baseline_y), 1)

            # Frames da linha
            if file_prefix == "special":
                frames_to_draw = ["front_attack", "back_attack", "recovery", "stunned", "dead"]
            else:
                frames_to_draw = [f"{file_prefix}_{i}" for i in range(num_frames)]

            for col_idx, fr_name in enumerate(frames_to_draw):
                fr_path = os.path.join(char_dir, f"{fr_name}.png")
                cell_cx = start_x + 200 + col_idx * 64
                cell_box = pygame.Rect(cell_cx - 28, ry + 4, 56, 88)
                pygame.draw.rect(screen, (22, 25, 32), cell_box, border_radius=4)
                pygame.draw.rect(screen, (34, 38, 48), cell_box, 1, border_radius=4)

                if os.path.exists(fr_path):
                    surf = pygame.image.load(fr_path).convert_alpha()
                    if is_flip:
                        surf = pygame.transform.flip(surf, True, False)
                    sw, sh = surf.get_size()
                    dest_x = cell_cx - sw // 2
                    dest_y = baseline_y - sh
                    screen.blit(surf, (dest_x, dest_y))

                idx_lbl = font_small.render(f"F{col_idx+1}", True, (100, 110, 125))
                screen.blit(idx_lbl, (cell_cx - idx_lbl.get_width() // 2, ry + 6))

    out_file = os.path.join(base_dir, "hd2d_sprite_map.png")
    pygame.image.save(screen, out_file)
    print(f"[OK] Mapa de Sprites Completo salvo com sucesso em: {out_file}")
    return out_file

if __name__ == "__main__":
    create_sprite_map_preview()
