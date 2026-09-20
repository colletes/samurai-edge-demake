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
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE
)

class CharacterSelectScreen:
    def __init__(self):
        self.p1_choice_idx = 0  # 0: Kenshin, 1: Musashi, 2: Ninja, 3: American Ninja, 4: Ninja Cinza
        self.p2_choice_idx = 4  # Padrão: Ninja Cinza
        self.p1_ready = False
        self.p2_ready = False
        self.vs_ai = True
        self.anim_timer = 0.0

        self.characters = [
            {
                "id": CHAR_KENSHIN,
                "name": "KENSHIN",
                "title": "Retalhador Carmim",
                "style": "Iai-jutsu (Saque)",
                "color": COLOR_RED_AURA,
                "speed_stars": "[ 5 / 5 ] MAX",
                "damage_desc": "1-Hit Kill Instantâneo",
                "special_desc": "Dash Evasivo | Cooldown",
                "keys_p1": "[E] Iai | [R] Dash",
                "keys_p2": "[U] Iai | [I] Dash",
            },
            {
                "id": CHAR_MUSASHI,
                "name": "MUSASHI",
                "title": "Duas Lâminas",
                "style": "Niten Ichi-ryū",
                "color": COLOR_BLUE_AURA,
                "speed_stars": "[ 2 / 5 ] Firme",
                "damage_desc": "Combo 3-Cortes",
                "special_desc": "Defesa (Parry)",
                "keys_p1": "[E] 3-Cortes | [R] Parry",
                "keys_p2": "[U] 3-Cortes | [I] Parry",
            },
            {
                "id": CHAR_NINJA,
                "name": "HANZO",
                "title": "Ninja Amarelo",
                "style": "Ninjutsu & Kunai",
                "color": COLOR_YELLOW_AURA,
                "speed_stars": "[ 5 / 5 ] MAX",
                "damage_desc": "Estocada (2 Hits)",
                "special_desc": "Arremesso Mortal",
                "keys_p1": "[E] Kunai | [R] Lançar",
                "keys_p2": "[U] Kunai | [I] Lançar",
            },
            {
                "id": CHAR_AMERICAN,
                "name": "JOE",
                "title": "American Ninja",
                "style": "Tático & Cão",
                "color": (255, 130, 45),
                "speed_stars": "[ 4 / 5 ] Ágil",
                "damage_desc": "Shuriken (Stun)",
                "special_desc": "Doberman (1-Hit Kill)",
                "keys_p1": "[E] Shuriken | [R] Cão",
                "keys_p2": "[U] Shuriken | [I] Cão",
            },
            {
                "id": CHAR_GRAY,
                "name": "KEMURI",
                "title": "Ninja Cinza",
                "style": "Pólvora & Fumaça",
                "color": (165, 180, 190),
                "speed_stars": "[ 4 / 5 ] Ágil",
                "damage_desc": "Bomba c/ Delay (AOE)",
                "special_desc": "Fumaça (Slow + Fuga)",
                "keys_p1": "[E] Bomba | [R] Fumaça",
                "keys_p2": "[U] Bomba | [I] Fumaça",
            },
            {
                "id": CHAR_PURPLE,
                "name": "MURASAKI",
                "title": "Ninja Roxo",
                "style": "Kusarigama & Foice",
                "color": COLOR_PURPLE_AURA,
                "speed_stars": "[ 4 / 5 ] Ágil",
                "damage_desc": "Foice de Precedência",
                "special_desc": "Puxão de Corrente",
                "keys_p1": "[E] Foice | [R] Puxar",
                "keys_p2": "[U] Foice | [I] Puxar",
            }
        ]

        self.card_rects: list[pygame.Rect] = []

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.vs_ai = not self.vs_ai

            if event.key in (pygame.K_a, pygame.K_LEFT):
                self.p1_choice_idx = (self.p1_choice_idx - 1) % len(self.characters)
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self.p1_choice_idx = (self.p1_choice_idx + 1) % len(self.characters)
            elif event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                return True

            if not self.vs_ai:
                if event.key == pygame.K_q:
                    self.p2_choice_idx = (self.p2_choice_idx - 1) % len(self.characters)
                elif event.key == pygame.K_p:
                    self.p2_choice_idx = (self.p2_choice_idx + 1) % len(self.characters)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for idx, rect in enumerate(self.card_rects):
                if rect.collidepoint(mx, my):
                    self.p1_choice_idx = idx

            start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 95, 300, 48)
            if start_btn.collidepoint(mx, my):
                return True

            ai_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 78, 280, 32)
            if ai_btn.collidepoint(mx, my):
                self.vs_ai = not self.vs_ai

        return False

    def update(self, dt: float):
        self.anim_timer += dt

    def get_selected_characters(self) -> tuple[str, str, bool]:
        p1_char = self.characters[self.p1_choice_idx]["id"]
        p2_char = self.characters[self.p2_choice_idx]["id"]
        return p1_char, p2_char, self.vs_ai

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        surface.fill(COLOR_BG)

        # 1. Título
        title_surf = font_large.render("ESCOLHA SEU GUERREIRO", True, COLOR_GOLD)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 25))

        # 2. Botão Modo de Jogo
        ai_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 78, 280, 32)
        pygame.draw.rect(surface, (30, 40, 35), ai_btn, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, ai_btn, 1, border_radius=6)
        mode_text = "[1P vs IA] (TAB para 2P)" if self.vs_ai else "[2 JOGADORES] (TAB para IA)"
        mode_surf = font_small.render(mode_text, True, COLOR_GOLD)
        surface.blit(mode_surf, (ai_btn.centerx - mode_surf.get_width() // 2, ai_btn.y + 7))

        # 3. Seis Cards de Personagens
        card_w = 186
        card_h = 445
        spacing = 14
        num_cards = len(self.characters)
        start_x = (SCREEN_WIDTH - (card_w * num_cards + spacing * (num_cards - 1))) // 2
        start_y = 130

        self.card_rects.clear()

        for idx, char_info in enumerate(self.characters):
            cx = start_x + idx * (card_w + spacing)
            rect = pygame.Rect(cx, start_y, card_w, card_h)
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

            # Badges P1 / P2
            badge_y = rect.y + 14
            if is_p1:
                p1_badge = font_small.render("[ P1 ]", True, COLOR_RED_AURA)
                surface.blit(p1_badge, (rect.centerx - p1_badge.get_width() // 2 - (24 if is_p2 else 0), badge_y))
            if is_p2:
                label_p2 = "[ IA ]" if self.vs_ai else "[ P2 ]"
                p2_badge = font_small.render(label_p2, True, COLOR_BLUE_AURA)
                surface.blit(p2_badge, (rect.centerx - p2_badge.get_width() // 2 + (24 if is_p1 else 0), badge_y))

            # Nome e Título
            name_surf = font_large.render(char_info["name"], True, char_info["color"])
            surface.blit(name_surf, (rect.centerx - name_surf.get_width() // 2, rect.y + 40))

            title_s = font_small.render(char_info["title"], True, (180, 190, 185))
            surface.blit(title_s, (rect.centerx - title_s.get_width() // 2, rect.y + 82))

            # Retrato do Personagem
            portrait_center_x = rect.centerx
            portrait_center_y = rect.y + 150

            pygame.draw.circle(surface, (18, 22, 20), (portrait_center_x, portrait_center_y), 40)
            pygame.draw.circle(surface, char_info["color"], (portrait_center_x, portrait_center_y), 40, 2)

            # Mini-ilustrações
            if char_info["id"] == CHAR_KENSHIN:
                pygame.draw.circle(surface, (210, 85, 45), (portrait_center_x, portrait_center_y - 12), 15)
                pygame.draw.circle(surface, (245, 215, 190), (portrait_center_x, portrait_center_y - 8), 11)
                pygame.draw.polygon(surface, (195, 32, 42), [
                    (portrait_center_x - 16, portrait_center_y + 24),
                    (portrait_center_x + 16, portrait_center_y + 24),
                    (portrait_center_x + 10, portrait_center_y),
                    (portrait_center_x - 10, portrait_center_y)
                ])
                pygame.draw.line(surface, COLOR_STEEL, (portrait_center_x - 14, portrait_center_y + 8), (portrait_center_x + 22, portrait_center_y - 8), 3)

            elif char_info["id"] == CHAR_MUSASHI:
                pygame.draw.circle(surface, (24, 24, 30), (portrait_center_x, portrait_center_y - 12), 15)
                pygame.draw.circle(surface, (240, 210, 185), (portrait_center_x, portrait_center_y - 8), 11)
                pygame.draw.polygon(surface, (28, 56, 138), [
                    (portrait_center_x - 16, portrait_center_y + 24),
                    (portrait_center_x + 16, portrait_center_y + 24),
                    (portrait_center_x + 10, portrait_center_y),
                    (portrait_center_x - 10, portrait_center_y)
                ])
                pygame.draw.line(surface, COLOR_STEEL, (portrait_center_x - 18, portrait_center_y - 8), (portrait_center_x - 6, portrait_center_y + 18), 3)
                pygame.draw.line(surface, COLOR_STEEL, (portrait_center_x + 18, portrait_center_y - 8), (portrait_center_x + 6, portrait_center_y + 18), 3)

            elif char_info["id"] == CHAR_NINJA:
                pygame.draw.circle(surface, (240, 205, 30), (portrait_center_x, portrait_center_y - 12), 15)
                pygame.draw.rect(surface, (26, 26, 30), (portrait_center_x - 9, portrait_center_y - 7, 18, 11), border_radius=3)
                pygame.draw.polygon(surface, (240, 205, 30), [
                    (portrait_center_x - 15, portrait_center_y + 24),
                    (portrait_center_x + 15, portrait_center_y + 24),
                    (portrait_center_x + 10, portrait_center_y),
                    (portrait_center_x - 10, portrait_center_y)
                ])
                pygame.draw.line(surface, COLOR_STEEL, (portrait_center_x + 6, portrait_center_y + 10), (portrait_center_x + 22, portrait_center_y - 4), 3)
                pygame.draw.circle(surface, COLOR_GOLD, (portrait_center_x + 6, portrait_center_y + 10), 3, 1)

            elif char_info["id"] == CHAR_AMERICAN:
                pygame.draw.circle(surface, (30, 25, 25), (portrait_center_x - 8, portrait_center_y - 12), 12)
                pygame.draw.circle(surface, (240, 205, 180), (portrait_center_x - 8, portrait_center_y - 8), 9)
                pygame.draw.line(surface, COLOR_AMERICAN_BANDANA, (portrait_center_x - 16, portrait_center_y - 10), (portrait_center_x, portrait_center_y - 10), 3)
                pygame.draw.polygon(surface, COLOR_AMERICAN_NINJA, [
                    (portrait_center_x - 18, portrait_center_y + 24),
                    (portrait_center_x + 2, portrait_center_y + 24),
                    (portrait_center_x, portrait_center_y),
                    (portrait_center_x - 16, portrait_center_y)
                ])
                # Cão
                dog_x = portrait_center_x + 14
                dog_y = portrait_center_y + 6
                pygame.draw.circle(surface, COLOR_DOBERMAN_BLACK, (dog_x, dog_y - 6), 6)
                pygame.draw.line(surface, COLOR_DOBERMAN_BLACK, (dog_x - 2, dog_y - 10), (dog_x - 2, dog_y - 15), 2)
                pygame.draw.line(surface, COLOR_DOBERMAN_BLACK, (dog_x + 2, dog_y - 10), (dog_x + 2, dog_y - 15), 2)

            elif char_info["id"] == CHAR_GRAY:
                # Ninja Kemuri
                pygame.draw.circle(surface, COLOR_GRAY_NINJA, (portrait_center_x, portrait_center_y - 12), 15)
                pygame.draw.rect(surface, COLOR_GRAY_DARK, (portrait_center_x - 9, portrait_center_y - 7, 18, 11), border_radius=3)
                pygame.draw.polygon(surface, COLOR_GRAY_NINJA, [
                    (portrait_center_x - 15, portrait_center_y + 24),
                    (portrait_center_x + 15, portrait_center_y + 24),
                    (portrait_center_x + 10, portrait_center_y),
                    (portrait_center_x - 10, portrait_center_y)
                ])
                # Bomba ao lado
                pygame.draw.circle(surface, (20, 20, 25), (portrait_center_x + 18, portrait_center_y + 12), 6)
                pygame.draw.circle(surface, COLOR_BOMB_FUSE, (portrait_center_x + 20, portrait_center_y + 5), 2)

            elif char_info["id"] == CHAR_PURPLE:
                # Ninja Murasaki (Kusarigama)
                pygame.draw.circle(surface, COLOR_PURPLE_NINJA, (portrait_center_x, portrait_center_y - 12), 15)
                pygame.draw.rect(surface, COLOR_PURPLE_DARK, (portrait_center_x - 9, portrait_center_y - 7, 18, 11), border_radius=3)
                pygame.draw.polygon(surface, COLOR_PURPLE_NINJA, [
                    (portrait_center_x - 15, portrait_center_y + 24),
                    (portrait_center_x + 15, portrait_center_y + 24),
                    (portrait_center_x + 10, portrait_center_y),
                    (portrait_center_x - 10, portrait_center_y)
                ])
                # Foice curta
                pygame.draw.line(surface, (80, 50, 30), (portrait_center_x + 8, portrait_center_y + 12), (portrait_center_x + 18, portrait_center_y), 3)
                pygame.draw.line(surface, COLOR_STEEL, (portrait_center_x + 18, portrait_center_y), (portrait_center_x + 22, portrait_center_y - 8), 3)
                # Corrente pendurada com peso de ferro
                pygame.draw.line(surface, COLOR_CHAIN, (portrait_center_x - 10, portrait_center_y + 10), (portrait_center_x - 14, portrait_center_y + 18), 2)
                pygame.draw.circle(surface, (25, 25, 30), (portrait_center_x - 14, portrait_center_y + 20), 4)

            # Atributos
            stats_y = rect.y + 215
            line1 = font_small.render(f"Estilo: {char_info['style']}", True, COLOR_WHITE)
            line2 = font_small.render(f"Vel: {char_info['speed_stars']}", True, COLOR_GOLD)
            line3 = font_small.render(f"Dano: {char_info['damage_desc']}", True, (240, 200, 200))
            line4 = font_small.render(f"Esp: {char_info['special_desc']}", True, (200, 225, 240))

            surface.blit(line1, (rect.x + 10, stats_y))
            surface.blit(line2, (rect.x + 10, stats_y + 26))
            surface.blit(line3, (rect.x + 10, stats_y + 52))
            surface.blit(line4, (rect.x + 10, stats_y + 78))

            # Controles
            ctrl_box = pygame.Rect(rect.x + 8, rect.bottom - 74, card_w - 16, 58)
            pygame.draw.rect(surface, (20, 25, 22), ctrl_box, border_radius=6)
            p1_key_label = font_small.render(f"P1: {char_info['keys_p1']}", True, (255, 200, 180))
            p2_key_label = font_small.render(f"P2: {char_info['keys_p2']}", True, (180, 220, 255))
            surface.blit(p1_key_label, (ctrl_box.x + 6, ctrl_box.y + 8))
            surface.blit(p2_key_label, (ctrl_box.x + 6, ctrl_box.y + 32))

        # 4. Botão INICIAR DUELO
        start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 86, 320, 48)
        pulse = (math.sin(self.anim_timer * 4.0) + 1.0) * 0.5
        btn_bg = (50 + int(pulse * 15), 75 + int(pulse * 20), 60 + int(pulse * 15))
        pygame.draw.rect(surface, btn_bg, start_btn, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, start_btn, 2, border_radius=8)

        st_text = font_mid.render("INICIAR DUELO (ENTER)", True, COLOR_GOLD)
        surface.blit(st_text, (start_btn.centerx - st_text.get_width() // 2, start_btn.y + 13))
