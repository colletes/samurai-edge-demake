"""
Captura uma vitrine de alta resolução demonstrando o novo elenco de micro-voxels,
silhuetas humanas anatômicas e lâminas fluidas em ação no Samurai Edge.
"""
import os
import sys
sys.path.insert(0, "/Users/thiagocarvalho/Documents/Sample Game")
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_GOLD, COLOR_WHITE
from src.isometric.camera import Camera
from src.entities.voxel_models import render_voxel_humanoid, render_voxel_doberman

class ZoomCamera:
    def __init__(self, target_wx: float = 0.0, target_wy: float = 0.0, zoom: float = 2.4, screen_x: int = 0, screen_y: int = 0):
        self.wx = target_wx
        self.wy = target_wy
        self.zoom = zoom
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

    def apply(self, wx: float, wy: float, wz: float = 0.0) -> tuple[int, int]:
        iso_x = (wx - wy) * 32.0 * self.zoom
        iso_y = (wx + wy) * 16.0 * self.zoom - (wz * 32.0 * self.zoom)

        cam_iso_x = (self.wx - self.wy) * 32.0 * self.zoom
        cam_iso_y = (self.wx + self.wy) * 16.0 * self.zoom

        final_x = int(iso_x - cam_iso_x + self.screen_x)
        final_y = int(iso_y - cam_iso_y + self.screen_y)
        return final_x, final_y

def main():
    pygame.init()
    pygame.font.init()

    W, H = 1440, 960
    surface = pygame.Surface((W, H))
    surface.fill(COLOR_BG)

    font_title = pygame.font.Font(None, 44)
    font_sub = pygame.font.Font(None, 24)
    font_name = pygame.font.Font(None, 24)
    font_role = pygame.font.Font(None, 18)

    title = font_title.render("NOVO SISTEMA DE ARTE VOXEL DETALHADA & ARTICULAÇÃO 3D", True, COLOR_GOLD)
    surface.blit(title, (W // 2 - title.get_width() // 2, 22))

    sub = font_sub.render("Proposta 2A: Proporções Humanas (~5.7 cabeças), Kenshi Feminina, Silhuetas Nítidas e Lâminas Fluidas", True, (215, 220, 225))
    surface.blit(sub, (W // 2 - sub.get_width() // 2, 65))

    # Grid 4 colunas x 3 linhas dos 12 Guerreiros
    roster = [
        {"id": "kenshin", "name": "Kenshi", "role": "Duelista de Battojutsu (Feminina)", "state": "ATTACK", "timer": 0.08, "fx": 1.0, "fy": 0.25},
        {"id": "musashi", "name": "Musashi", "role": "Samurai de Duas Espadas", "state": "ATTACK", "timer": 0.09, "fx": 1.0, "fy": 0.25},
        {"id": "saitou", "name": "Saitou", "role": "Capitão do Shinsengumi (Gatotsu)", "state": "ATTACK", "timer": 0.12, "fx": 1.0, "fy": 0.25},
        {"id": "julie", "name": "Julie", "role": "Mosqueteira de Duelo (Florete)", "state": "ATTACK", "timer": 0.10, "fx": 1.0, "fy": 0.25},

        {"id": "anne", "name": "Anne", "role": "Capitã Pirata (Cutlass 180°)", "state": "ATTACK", "timer": 0.11, "fx": 1.0, "fy": 0.25},
        {"id": "okuni", "name": "Okuni", "role": "Criadora do Kabuki (Leques Tessen)", "state": "WALK", "timer": 0.0, "fx": 1.0, "fy": 0.25},
        {"id": "tomoe", "name": "Tomoe", "role": "Miko Arqueira (Arco Yumi)", "state": "IDLE", "timer": 0.0, "fx": 1.0, "fy": 0.25},
        {"id": "rifleman", "name": "Tanegashima", "role": "Soldado Teppo (Arcabuz Voxel)", "state": "IDLE", "timer": 0.0, "fx": 1.0, "fy": 0.25},

        {"id": "ninja", "name": "Hanzo", "role": "Ninja Shinobi (Kunai)", "state": "ATTACK", "timer": 0.09, "fx": 1.0, "fy": 0.25},
        {"id": "kasumi", "name": "Kasumi", "role": "Kunoichi da Névoa (Trança & Bomba)", "state": "WALK", "timer": 0.0, "fx": 1.0, "fy": 0.25},
        {"id": "murasaki", "name": "Murasaki", "role": "Kunoichi de Kusarigama", "state": "ATTACK", "timer": 0.08, "fx": 1.0, "fy": 0.25},
        {"id": "american", "name": "Joe & Doberman", "role": "American Ninja & Cão de Combate", "state": "IDLE", "timer": 0.0, "fx": 1.0, "fy": 0.25},
    ]

    col_w = 340
    row_h = 265
    start_x = 70
    start_y = 115

    for idx, f in enumerate(roster):
        c = idx % 4
        r = idx // 4

        card_x = start_x + c * col_w
        card_y = start_y + r * row_h

        card_rect = pygame.Rect(card_x, card_y, col_w - 20, row_h - 15)
        pygame.draw.rect(surface, (20, 26, 25), card_rect, border_radius=10)
        pygame.draw.rect(surface, (50, 65, 60), card_rect, width=1, border_radius=10)

        # Header do lutador
        name_t = font_name.render(f["name"], True, COLOR_GOLD)
        surface.blit(name_t, (card_rect.centerx - name_t.get_width() // 2, card_y + 12))

        role_t = font_role.render(f["role"], True, (170, 185, 190))
        surface.blit(role_t, (card_rect.centerx - role_t.get_width() // 2, card_y + 34))

        # Câmera centrada no card
        cam = ZoomCamera(0.0, 0.0, zoom=2.35, screen_x=card_rect.centerx, screen_y=card_y + 185)

        char_id = f["id"]
        is_moving = (f["state"] == "WALK")
        walk_t = 1.4 if is_moving else 0.0

        render_voxel_humanoid(
            surface, cam,
            0.0, 0.0, 0.0,
            f["fx"], f["fy"],
            f["state"], f["timer"],
            True, char_id,
            walk_timer=walk_t, is_moving=is_moving
        )

        if char_id == "american":
            # Renderizar Doberman ao lado de Joe
            render_voxel_doberman(
                surface, cam,
                0.28, -0.22, 0.0,
                f["fx"], f["fy"],
                "IDLE", 0.0, True
            )

    out_file = "/Users/thiagocarvalho/.gemini/antigravity/brain/702c3513-d289-4263-9e2f-fb1dba471417/roster_voxel_overhaul.png"
    pygame.image.save(surface, out_file)
    print(f"Vitrine do elenco salva com sucesso em: {out_file}")

if __name__ == "__main__":
    main()
