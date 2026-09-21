"""
Tela de Seleção de Personagens (Character Select Screen).
Permite escolher entre Kenshin, Musashi, Ninja Hanzo, American Ninja (Joe & Dog) e Ninja Cinza (Kemuri).
"""
import math
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_RED_AURA,
    COLOR_BLUE_AURA, COLOR_YELLOW_AURA, COLOR_BG, COLOR_STEEL,
    COLOR_AMERICAN_NINJA, COLOR_AMERICAN_VEST, COLOR_AMERICAN_BANDANA,
    COLOR_DOBERMAN_BLACK, COLOR_DOBERMAN_RUST, COLOR_DOBERMAN_COLLAR,
    COLOR_GRAY_NINJA, COLOR_GRAY_DARK, COLOR_SMOKE, COLOR_BOMB_FUSE,
    COLOR_PURPLE_NINJA, COLOR_PURPLE_DARK, COLOR_PURPLE_AURA, COLOR_CHAIN,
    COLOR_SAITOU_LIGHT_BLUE, CHAR_SAITOU,
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE,
    CHAR_RIFLE, CHAR_KABUKI, CHAR_ARCHER, CHAR_PIRATE, CHAR_MUSKETEER,
    COLOR_PIRATE_AURA, COLOR_MUSKETEER_AURA
)

from src.isometric.iso_math import world_to_iso
from src.entities.voxel_models import render_voxel_humanoid, render_voxel_doberman
from src.ui.game_help import GameHelpModal
from src.i18n import t, get_lang, toggle_lang, LANG_PT, LANG_EN

class PreviewCamera:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
    def apply(self, wx, wy, wz=0.0):
        ix, iy = world_to_iso(wx, wy, wz)
        return int(self.cx + ix), int(self.cy + iy)

class CharacterSelectScreen:
    def __init__(self):
        self.p1_choice_idx = 0  # Kenshin
        self.p2_choice_idx = 1  # Musashi
        self.p1_ready = False
        self.p2_ready = False
        self.vs_ai = True
        self.anim_timer = 0.0

        # Modal de Ajuda Completa do Jogo e Guia dos 12 Guerreiros
        self.help_modal = GameHelpModal()
        self.help_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.lang_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.info_btn_rects: list[pygame.Rect] = []


        self.characters = [
            {
                "id": CHAR_KENSHIN,
                "name": "KENSHIN",
                "title": "Retalhador",
                "style": "Iai & Shukuchi",
                "color": COLOR_RED_AURA,
                "speed_stars": "[5/5] MAX",
                "damage_desc": "1-Hit Kill Instantâneo",
                "special_desc": "Shukuchi (Relâmpago)",
                "keys_p1": "[E] Iai | [R] Dash",
                "keys_p2": "[U] Iai | [I] Dash",
            },
            {
                "id": CHAR_MUSASHI,
                "name": "MUSASHI",
                "title": "Duas Lâminas",
                "style": "Niten Ichi-ryū",
                "color": COLOR_BLUE_AURA,
                "speed_stars": "[2/5] Firme",
                "damage_desc": "Combo 3-Cortes",
                "special_desc": "Defesa (Parry)",
                "keys_p1": "[E] Golpe | [R] Parry",
                "keys_p2": "[U] Golpe | [I] Parry",
            },
            {
                "id": CHAR_NINJA,
                "name": "HANZO",
                "title": "Ninja Mestre",
                "style": "Ninjutsu & Kunai",
                "color": COLOR_YELLOW_AURA,
                "speed_stars": "[5/5] MAX",
                "damage_desc": "Estocada (2 Hits)",
                "special_desc": "Arremesso Kunai",
                "keys_p1": "[E] Kunai | [R] Lançar",
                "keys_p2": "[U] Kunai | [I] Lançar",
            },
            {
                "id": CHAR_AMERICAN,
                "name": "JOE",
                "title": "American Ninja",
                "style": "Tático & Cão",
                "color": (255, 130, 45),
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Shuriken (Stun)",
                "special_desc": "Doberman (1-Hit Kill)",
                "keys_p1": "[E] Shuriken | [R] Cão",
                "keys_p2": "[U] Shuriken | [I] Cão",
            },
            {
                "id": CHAR_SAITOU,
                "name": "SAITOU",
                "title": "Lobo de Mibu",
                "style": "Gatotsu Shinsen",
                "color": COLOR_SAITOU_LIGHT_BLUE,
                "speed_stars": "[5/5] Impulso",
                "damage_desc": "1-Hit Acelerado",
                "special_desc": "Zeroshiki (Curto)",
                "keys_p1": "[E] Gatotsu | [R] Zero",
                "keys_p2": "[U] Gatotsu | [I] Zero",
            },
            {
                "id": CHAR_RIFLE,
                "name": "TEPPO",
                "title": "Marksman",
                "style": "Arcabuz Feudal",
                "color": (225, 170, 100),
                "speed_stars": "[3/5] Cadência",
                "damage_desc": "Tiro Fatal (1-Hit)",
                "special_desc": "Carregar Pólvora",
                "keys_p1": "[E] Tiro | [R] Recarga",
                "keys_p2": "[U] Tiro | [I] Recarga",
            },
            {
                "id": CHAR_PURPLE,
                "name": "MURASAKI",
                "title": "Kunoichi Foice",
                "style": "Kusarigama",
                "color": COLOR_PURPLE_AURA,
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Precedência Absoluta",
                "special_desc": "Puxão de Corrente",
                "keys_p1": "[E] Foice | [R] Puxar",
                "keys_p2": "[U] Foice | [I] Puxar",
            },
            {
                "id": CHAR_GRAY,
                "name": "KASUMI",
                "title": "Kunoichi Névoa",
                "style": "Pólvora & Fumaça",
                "color": (165, 180, 190),
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Bomba Arco (Auto-Dano)",
                "special_desc": "Fumaça (Slow + Fuga)",
                "keys_p1": "[E] Bomba | [R] Fumaça",
                "keys_p2": "[U] Bomba | [I] Fumaça",
            },
            {
                "id": CHAR_KABUKI,
                "name": "OKUNI",
                "title": "Mestra Kabuki",
                "style": "Sopro Tóxico",
                "color": (240, 115, 30),
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Veneno (10s Morte)",
                "special_desc": "Pirueta Evasiva",
                "keys_p1": "[E] Sopro | [R] Esquiva",
                "keys_p2": "[U] Sopro | [I] Esquiva",
            },
            {
                "id": CHAR_ARCHER,
                "name": "TOMOE",
                "title": "Arqueira Miko",
                "style": "Arco Yumi",
                "color": (110, 195, 135),
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Flecha Letal (Windup)",
                "special_desc": "Flecha de Corda",
                "keys_p1": "[E] Yumi | [R] Corda",
                "keys_p2": "[U] Yumi | [I] Corda",
            },
            {
                "id": CHAR_PIRATE,
                "name": "ANNE",
                "title": "Espadachim",
                "style": "Alfanje & Pólvora",
                "color": COLOR_PIRATE_AURA,
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Corte Amplo 180°",
                "special_desc": "Pólvora nos Olhos",
                "keys_p1": "[E] Alfanje | [R] Cegar",
                "keys_p2": "[U] Alfanje | [I] Cegar",
            },
            {
                "id": CHAR_MUSKETEER,
                "name": "JULIE",
                "title": "Mosqueteira",
                "style": "Florete Nobre",
                "color": COLOR_MUSKETEER_AURA,
                "speed_stars": "[5/5] Rápida",
                "damage_desc": "Fleche Longo",
                "special_desc": "Capa Riposte & Tiro",
                "keys_p1": "[E] Florete | [R] Riposte",
                "keys_p2": "[U] Florete | [I] Riposte",
            }
        ]

        self.card_rects: list[pygame.Rect] = []

    def handle_event(self, event: pygame.event.Event) -> bool:
        # Se o modal de ajuda estiver aberto, repassar eventos exclusivamente para ele
        if self.help_modal.is_open:
            self.help_modal.handle_event(event)
            return False

        num_c = len(self.characters)
        cols = 6

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.vs_ai = not self.vs_ai
                return False
            elif event.key == pygame.K_h:
                self.help_modal.open(GameHelpModal.TAB_RULES)
                return False
            elif event.key == pygame.K_f:
                self.help_modal.open(GameHelpModal.TAB_FIGHTERS, fighter_idx=self.p1_choice_idx)
                return False
            elif event.key == pygame.K_l:
                toggle_lang()
                return False

            # P1 (Você): Controles WASD navegam na grade
            if event.key == pygame.K_a:
                self.p1_choice_idx = (self.p1_choice_idx - 1) % num_c
            elif event.key == pygame.K_d:
                self.p1_choice_idx = (self.p1_choice_idx + 1) % num_c
            elif event.key == pygame.K_w:
                self.p1_choice_idx = (self.p1_choice_idx - cols) % num_c
            elif event.key == pygame.K_s:
                self.p1_choice_idx = (self.p1_choice_idx + cols) % num_c

            # P2 / IA (Oponente): Controles SETAS navegam na grade
            elif event.key == pygame.K_LEFT:
                self.p2_choice_idx = (self.p2_choice_idx - 1) % num_c
            elif event.key == pygame.K_RIGHT:
                self.p2_choice_idx = (self.p2_choice_idx + 1) % num_c
            elif event.key == pygame.K_UP:
                self.p2_choice_idx = (self.p2_choice_idx - cols) % num_c
            elif event.key == pygame.K_DOWN:
                self.p2_choice_idx = (self.p2_choice_idx + cols) % num_c

            # Iniciar partida
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Botão esquerdo: Seleciona P1 (Você) ou Botões de Ajuda / Idioma
            if event.button == 1:
                # Botão seletor de idioma [ PT | EN ]
                if self.lang_btn_rect.collidepoint(mx, my):
                    toggle_lang()
                    return False

                # Botão superior do Guia Completo
                if self.help_btn_rect.collidepoint(mx, my):
                    self.help_modal.open(GameHelpModal.TAB_RULES)
                    return False


                # Botões [ ? ] de cada card de personagem
                for idx, irect in enumerate(self.info_btn_rects):
                    if irect.collidepoint(mx, my):
                        self.help_modal.open(GameHelpModal.TAB_FIGHTERS, fighter_idx=idx)
                        return False

                for idx, rect in enumerate(self.card_rects):
                    if rect.collidepoint(mx, my):
                        self.p1_choice_idx = idx

                start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 64, 320, 44)
                if start_btn.collidepoint(mx, my):
                    return True

                ai_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 66, 280, 32)
                if ai_btn.collidepoint(mx, my):
                    self.vs_ai = not self.vs_ai
            # Botão direito: Seleciona IA (Oponente) / P2
            elif event.button == 3:
                for idx, rect in enumerate(self.card_rects):
                    if rect.collidepoint(mx, my):
                        self.p2_choice_idx = idx

        return False

    def update(self, dt: float):
        self.anim_timer += dt
        self.help_modal.update(dt)


    def get_selected_characters(self) -> tuple[str, str, bool]:
        p1_char = self.characters[self.p1_choice_idx]["id"]
        p2_char = self.characters[self.p2_choice_idx]["id"]
        return p1_char, p2_char, self.vs_ai

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        surface.fill(COLOR_BG)

        # 1. Título
        title_surf = font_large.render(t("select_title"), True, COLOR_GOLD)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 18))

        # Botão Seletor Flutuante de Idioma [ PT | EN ] (Padrão Boardbots)
        lang = get_lang()
        self.lang_btn_rect = pygame.Rect(SCREEN_WIDTH - 365, 18, 100, 36)
        pygame.draw.rect(surface, (30, 40, 35), self.lang_btn_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.lang_btn_rect, 1, border_radius=6)

        pt_col = COLOR_GOLD if lang == LANG_PT else (140, 155, 148)
        en_col = COLOR_GOLD if lang == LANG_EN else (140, 155, 148)
        pt_bg = (48, 64, 54) if lang == LANG_PT else (25, 34, 29)
        en_bg = (48, 64, 54) if lang == LANG_EN else (25, 34, 29)

        r_pt = pygame.Rect(self.lang_btn_rect.x + 3, self.lang_btn_rect.y + 3, 44, 30)
        r_en = pygame.Rect(self.lang_btn_rect.x + 53, self.lang_btn_rect.y + 3, 44, 30)
        pygame.draw.rect(surface, pt_bg, r_pt, border_radius=4)
        pygame.draw.rect(surface, en_bg, r_en, border_radius=4)

        s_pt = font_small.render("PT", True, pt_col)
        s_en = font_small.render("EN", True, en_col)
        surface.blit(s_pt, (r_pt.centerx - s_pt.get_width() // 2, r_pt.centery - s_pt.get_height() // 2))
        surface.blit(s_en, (r_en.centerx - s_en.get_width() // 2, r_en.centery - s_en.get_height() // 2))

        # Botão Superior Guia do Jogo & Ajuda
        self.help_btn_rect = pygame.Rect(SCREEN_WIDTH - 250, 18, 226, 36)
        pygame.draw.rect(surface, (28, 38, 33), self.help_btn_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.help_btn_rect, 1, border_radius=6)
        h_txt = font_small.render(t("btn_help"), True, COLOR_GOLD)
        surface.blit(h_txt, (self.help_btn_rect.centerx - h_txt.get_width() // 2, self.help_btn_rect.centery - h_txt.get_height() // 2))

        # 2. Botão Modo de Jogo
        ai_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 66, 280, 32)
        pygame.draw.rect(surface, (30, 40, 35), ai_btn, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, ai_btn, 1, border_radius=6)
        mode_text = t("mode_1p") if self.vs_ai else t("mode_2p")
        mode_surf = font_small.render(mode_text, True, COLOR_GOLD)
        surface.blit(mode_surf, (ai_btn.centerx - mode_surf.get_width() // 2, ai_btn.y + 7))



        # 3. Grade Simétrica 5x2 (5 cards na Linha 1, 5 cards na Linha 2)
        card_w = 230
        card_h = 236
        spacing_x = 16
        spacing_y = 14

        # 3. Grade Simétrica 6x2 (6 cards na Linha 1, 6 cards na Linha 2)
        card_w = 194
        card_h = 236
        spacing_x = 12
        spacing_y = 14

        total_w = 6 * card_w + 5 * spacing_x
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = 114

        self.card_rects.clear()
        self.info_btn_rects.clear()

        for idx, char_info in enumerate(self.characters):
            row = idx // 6
            col = idx % 6
            cx = start_x + col * (card_w + spacing_x)
            cy = start_y + row * (card_h + spacing_y)

            rect = pygame.Rect(cx, cy, card_w, card_h)
            self.card_rects.append(rect)

            is_p1 = (self.p1_choice_idx == idx)
            is_p2 = (self.p2_choice_idx == idx)

            bg_color = (25, 32, 28)
            border_color = (60, 75, 68)
            border_width = 1

            if is_p1 and is_p2:
                border_color = COLOR_GOLD
                border_width = 3
                bg_color = (35, 42, 38)
            elif is_p1:
                border_color = COLOR_RED_AURA
                border_width = 3
                bg_color = (40, 30, 32)
            elif is_p2:
                border_color = COLOR_BLUE_AURA
                border_width = 3
                bg_color = (30, 35, 45)

            pygame.draw.rect(surface, bg_color, rect, border_radius=12)
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=12)

            # Badges P1 / P2 no topo direito
            badge_y = rect.y + 8
            if is_p1 and is_p2:
                p1_label = t("badge_p1")
                p2_label = t("badge_ia") if self.vs_ai else t("badge_p2")
                p1_badge = font_small.render(p1_label, True, COLOR_RED_AURA)
                p2_badge = font_small.render(p2_label, True, COLOR_BLUE_AURA)
                surface.blit(p2_badge, (rect.right - p2_badge.get_width() - 8, badge_y))
                surface.blit(p1_badge, (rect.right - p2_badge.get_width() - p1_badge.get_width() - 12, badge_y))
            elif is_p1:
                p1_label = t("badge_p1")
                p1_badge = font_small.render(p1_label, True, COLOR_RED_AURA)
                surface.blit(p1_badge, (rect.right - p1_badge.get_width() - 8, badge_y))
            elif is_p2:
                p2_label = t("badge_ia") if self.vs_ai else t("badge_p2")
                p2_badge = font_small.render(p2_label, True, COLOR_BLUE_AURA)
                surface.blit(p2_badge, (rect.right - p2_badge.get_width() - 8, badge_y))


            # Retrato Voxel 3D do Personagem (no topo esquerdo da carta)
            portrait_cx = rect.x + 28
            portrait_cy = rect.y + 36
            pygame.draw.circle(surface, (18, 22, 20), (portrait_cx, portrait_cy), 22)
            pygame.draw.circle(surface, char_info["color"], (portrait_cx, portrait_cy), 22, 2)

            cam = PreviewCamera(portrait_cx, portrait_cy + 15)
            char_id = char_info["id"]

            if char_id == CHAR_KENSHIN:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="kenshin")
            elif char_id == CHAR_MUSASHI:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="musashi")
            elif char_id == CHAR_NINJA:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="yellow_ninja", extra_props={"has_kunai": True})
            elif char_id == CHAR_AMERICAN:
                render_voxel_humanoid(surface, cam, -0.20, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="american_ninja")
                render_voxel_doberman(surface, cam, 0.35, -0.10, 0, 1.0, 0.0, "IDLE", 0.0, True)
            elif char_id == CHAR_GRAY:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="kasumi")
            elif char_id == CHAR_PURPLE:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="murasaki")
            elif char_id == CHAR_SAITOU:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="saitou")
            elif char_id == CHAR_RIFLE:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="rifleman")
            elif char_id == CHAR_KABUKI:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="okuni")
            elif char_id == CHAR_ARCHER:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="tomoe")
            elif char_id == CHAR_PIRATE:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="pirate")
            elif char_id == CHAR_MUSKETEER:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="musketeer")

            # Nome, Título e Estilo ao lado do Retrato
            text_left = rect.x + 55
            name_surf = font_mid.render(char_info["name"], True, char_info["color"])
            surface.blit(name_surf, (text_left, rect.y + 6))

            title_s = font_small.render(char_info["title"], True, (185, 195, 190))
            surface.blit(title_s, (text_left, rect.y + 28))

            style_s = font_small.render(char_info["style"], True, COLOR_WHITE)
            surface.blit(style_s, (text_left, rect.y + 46))

            # Linha divisória sutil
            sep_y = rect.y + 70
            pygame.draw.line(surface, (45, 55, 50), (rect.x + 8, sep_y), (rect.right - 8, sep_y), 1)

            # Atributos e Estatísticas em largura total (sem truncar texto)
            stats_y = rect.y + 76
            line_vel = font_small.render(f"Vel: {char_info['speed_stars']}", True, COLOR_GOLD)
            line_dmg = font_small.render(f"Dano: {char_info['damage_desc']}", True, (240, 200, 200))
            line_esp = font_small.render(f"Esp: {char_info['special_desc']}", True, (200, 225, 240))

            surface.blit(line_vel, (rect.x + 8, stats_y))
            surface.blit(line_dmg, (rect.x + 8, stats_y + 19))
            surface.blit(line_esp, (rect.x + 8, stats_y + 38))

            # Caixa de Comandos / Teclas com espaço para o botão [ ? ] de Estratégia
            ctrl_w = card_w - 40
            ctrl_box = pygame.Rect(rect.x + 6, rect.bottom - 46, ctrl_w, 38)
            pygame.draw.rect(surface, (18, 24, 21), ctrl_box, border_radius=6)
            pygame.draw.rect(surface, (40, 50, 45), ctrl_box, 1, border_radius=6)
            p1_key_label = font_small.render(f"P1: {char_info['keys_p1']}", True, (255, 200, 180))
            p2_key_label = font_small.render(f"P2: {char_info['keys_p2']}", True, (180, 220, 255))
            surface.blit(p1_key_label, (ctrl_box.x + 4, ctrl_box.y + 3))
            surface.blit(p2_key_label, (ctrl_box.x + 4, ctrl_box.y + 19))

            # Botão [ ? ] para abrir estratégia individual deste guerreiro
            info_btn = pygame.Rect(rect.right - 30, rect.bottom - 46, 24, 38)
            self.info_btn_rects.append(info_btn)
            pygame.draw.rect(surface, (26, 36, 31), info_btn, border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD, info_btn, 1, border_radius=6)
            q_surf = font_mid.render("?", True, COLOR_GOLD)
            surface.blit(q_surf, (info_btn.centerx - q_surf.get_width() // 2, info_btn.centery - q_surf.get_height() // 2))

        # Guia de Navegação e Controles
        guide_text = t("guide_nav")
        guide_surf = font_small.render(guide_text, True, (210, 225, 220))
        surface.blit(guide_surf, (SCREEN_WIDTH // 2 - guide_surf.get_width() // 2, SCREEN_HEIGHT - 94))

        # 4. Botão INICIAR DUELO
        start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 64, 320, 44)
        pulse = (math.sin(self.anim_timer * 4.0) + 1.0) * 0.5
        btn_bg = (50 + int(pulse * 15), 75 + int(pulse * 20), 60 + int(pulse * 15))
        pygame.draw.rect(surface, btn_bg, start_btn, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, start_btn, 2, border_radius=8)

        st_text = font_mid.render(t("btn_start"), True, COLOR_GOLD)
        surface.blit(st_text, (start_btn.centerx - st_text.get_width() // 2, start_btn.y + 11))


        # 5. Renderizar Modal de Ajuda se aberto (sobreposto a toda a tela)
        if self.help_modal.is_open:
            self.help_modal.render(surface, font_large, font_mid, font_small)

