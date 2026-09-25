"""
Tela de Seleção de Arena de Batalha (Arena Select Screen).
Permite escolher entre a clássica Floresta de Bambu Sagrada,
o novo cenário de guerra urbana de Kyoto no Bakumatsu ou Seleção Aleatória.
Apresenta cards detalhados com indicadores de perigos, táticas e prévias visuais.
"""
import math
import os
import random
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_BG,
    ARENA_BAMBOO, ARENA_KYOTO, ARENA_RANDOM,
    COLOR_BAMBOO, COLOR_WATER, COLOR_BRIDGE,
    COLOR_KYOTO_STONE, COLOR_KYOTO_FIRE_MID, COLOR_KYOTO_CARRIAGE_WOOD,
    get_asset_path
)
from src.i18n import t

class ArenaSelectScreen:
    def __init__(self):
        self.selected_idx = 1  # Destaca Kyoto por padrão para a novidade
        self.anim_time = 0.0
        self.card_rects = []

        # Carregar imagens de conceito para portraits dos cards (com fallback procedural)
        self.preview_surfs = {}
        target_size = (328, 160)
        preview_files = {
            ARENA_BAMBOO: get_asset_path("assets/concepts/bamboo_forest_concept.jpg"),
            ARENA_KYOTO: get_asset_path("assets/concepts/kyoto_bakumatsu_concept.jpg"),
            ARENA_RANDOM: get_asset_path("assets/concepts/random_arena_concept.jpg"),
        }
        for arena_id, path in preview_files.items():
            if os.path.exists(path):
                try:
                    try:
                        raw = pygame.image.load(path).convert()
                    except Exception:
                        raw = pygame.image.load(path)
                    scaled = pygame.transform.smoothscale(raw, target_size)
                    self.preview_surfs[arena_id] = scaled
                except Exception:
                    self.preview_surfs[arena_id] = None

        self.arenas = [
            {
                "id": ARENA_BAMBOO,
                "name": "FLORESTA DE BAMBU",
                "tag": "[ ESTÁGIO 1 ]",
                "subtitle": "Santuário Sagrado - Duelo Tradicional",
                "hazard_level": "BAIXO (Terreno Estável)",
                "hazard_color": (120, 220, 100),
                "features": "Bambuzal cortável, lago com margens, ponte elevada e poço ancestral.",
                "tactics": "Emboscadas no bambuzal e controle tático dos gargalos da ponte.",
                "theme_color": (60, 140, 70),
            },
            {
                "id": ARENA_KYOTO,
                "name": "KYOTO: BAKUMATSU",
                "tag": "[ NOVO ]",
                "subtitle": "Avenida Imperial sob Cerco e Chamas",
                "hazard_level": "EXTREMO (Morte Ambiental)",
                "hazard_color": (255, 75, 45),
                "features": "Rua espaçosa de mobilidade total, carruagens assassinas e escombros em chamas.",
                "tactics": "Amplo espaço para dashes e kiting; esquive das carruagens nas calçadas!",
                "theme_color": (205, 75, 30),
            },
            {
                "id": ARENA_RANDOM,
                "name": "ARENA ALEATÓRIA",
                "tag": "[ SORTEIO ]",
                "subtitle": "O Destino Decide o Terreno",
                "hazard_level": "VARIÁVEL",
                "hazard_color": COLOR_GOLD,
                "features": "Sorteia imprevisivelmente qualquer arena do jogo para o combate.",
                "tactics": "Adapte sua estratégia instantaneamente ao cenário sorteado.",
                "theme_color": (140, 120, 210),
            }
        ]
        self._axis_x_held = False

    def handle_event(self, event) -> str | None:
        """
        Retorna:
          - ID da arena escolhida (ARENA_BAMBOO ou ARENA_KYOTO)
          - "BACK": se pressionar ESC ou botão de voltar
          - None: se ainda na tela
        """
        from src.input.controller_manager import get_controller_manager
        ctrl_mgr = get_controller_manager()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_idx = (self.selected_idx - 1) % len(self.arenas)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_idx = (self.selected_idx + 1) % len(self.arenas)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.get_resolved_arena_id()
            elif event.key == pygame.K_ESCAPE:
                return "BACK"

        elif event.type == pygame.JOYBUTTONDOWN:
            from src.input.controller_manager import get_dpad_motion_from_event
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                dx, _ = d_dir
                if dx != 0:
                    self.selected_idx = (self.selected_idx + dx) % len(self.arenas)
                return None

            if ctrl_mgr.is_event_menu_confirm(event) or event.button == 0:
                return self.get_resolved_arena_id()
            elif ctrl_mgr.is_event_menu_cancel(event) or event.button == 1:
                return "BACK"

        elif event.type == pygame.JOYHATMOTION:
            from src.input.controller_manager import get_dpad_motion_from_event
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                dx, _ = d_dir
                if dx != 0:
                    self.selected_idx = (self.selected_idx + dx) % len(self.arenas)

        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                if event.value > 0.65 and not self._axis_x_held:
                    self.selected_idx = (self.selected_idx + 1) % len(self.arenas)
                    self._axis_x_held = True
                elif event.value < -0.65 and not self._axis_x_held:
                    self.selected_idx = (self.selected_idx - 1) % len(self.arenas)
                    self._axis_x_held = True
                elif abs(event.value) < 0.25:
                    self._axis_x_held = False

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for idx, r in enumerate(self.card_rects):
                if r.collidepoint(mx, my):
                    self.selected_idx = idx

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for idx, r in enumerate(self.card_rects):
                if r.collidepoint(mx, my):
                    self.selected_idx = idx
                    return self.get_resolved_arena_id()

            # Botão Iniciar no rodapé
            start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 65, 280, 42)
            if start_btn.collidepoint(mx, my):
                return self.get_resolved_arena_id()

        return None

    def get_resolved_arena_id(self) -> str:
        chosen = self.arenas[self.selected_idx]["id"]
        if chosen == ARENA_RANDOM:
            return random.choice([ARENA_BAMBOO, ARENA_KYOTO])
        return chosen

    def update(self, dt: float):
        self.anim_time += dt

    def render(self, surface: pygame.Surface, font_large, font_mid, font_small):
        from src.ui.fonts import get_title_font, get_text_font
        font_oriental_title = get_title_font(28)
        font_oriental_name = get_title_font(18)
        font_oriental_btn = get_title_font(17)
        font_zen_sub = get_text_font(14)
        font_zen_body = get_text_font(13)
        font_zen_tip = get_text_font(14)

        surface.fill(COLOR_BG)

        # 1. Título Superior
        header_surf = font_oriental_title.render("SELEÇÃO DE ARENA", True, COLOR_GOLD)
        surface.blit(header_surf, (SCREEN_WIDTH // 2 - header_surf.get_width() // 2, 24))

        sub_surf = font_zen_sub.render("Escolha o campo de honra para o duelo mortal", True, (175, 180, 175))
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 68))

        # 2. Renderização dos 3 Cards
        card_w = 360
        card_h = 470
        spacing = 30
        total_w = len(self.arenas) * card_w + (len(self.arenas) - 1) * spacing
        start_x = (SCREEN_WIDTH - total_w) // 2
        card_y = 105

        self.card_rects = []
        for idx, arena in enumerate(self.arenas):
            cx = start_x + idx * (card_w + spacing)
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)
            self.card_rects.append(card_rect)

            is_sel = (self.selected_idx == idx)

            # Efeito de elevação suave e borda pulsante no selecionado
            y_offset = -8 if is_sel else 0
            draw_rect = pygame.Rect(cx, card_y + y_offset, card_w, card_h)

            bg_col = (26, 32, 30) if not is_sel else (34, 42, 38)
            pygame.draw.rect(surface, bg_col, draw_rect, border_radius=10)

            border_col = arena["theme_color"] if is_sel else (55, 65, 60)
            border_thick = 3 if is_sel else 1
            pygame.draw.rect(surface, border_col, draw_rect, border_thick, border_radius=10)

            # Efeito de brilho dourado se selecionado
            if is_sel:
                pulse = 0.5 + 0.5 * math.sin(self.anim_time * 6.0)
                glow_col = (int(COLOR_GOLD[0] * pulse), int(COLOR_GOLD[1] * pulse), int(COLOR_GOLD[2] * pulse))
                pygame.draw.rect(surface, glow_col, draw_rect.inflate(6, 6), 2, border_radius=12)

            # Área de Mini-Preview Visual do Cenário
            preview_rect = pygame.Rect(draw_rect.x + 16, draw_rect.y + 16, card_w - 32, 160)
            pygame.draw.rect(surface, (14, 16, 15), preview_rect, border_radius=6)
            self._render_arena_mini_preview(surface, arena["id"], preview_rect)

            # Badge da Tag flutuante sobre a foto no canto superior direito
            tag_s = font_zen_sub.render(arena["tag"], True, arena["theme_color"])
            tag_bg = pygame.Rect(preview_rect.right - tag_s.get_width() - 16, preview_rect.top + 8, tag_s.get_width() + 10, 22)
            pygame.draw.rect(surface, (16, 18, 18), tag_bg, border_radius=4)
            pygame.draw.rect(surface, arena["theme_color"], tag_bg, 1, border_radius=4)
            surface.blit(tag_s, (tag_bg.centerx - tag_s.get_width() // 2, tag_bg.centery - tag_s.get_height() // 2))

            # Título da Arena
            name_s = font_oriental_name.render(arena["name"], True, COLOR_WHITE if not is_sel else COLOR_GOLD)
            surface.blit(name_s, (draw_rect.x + 18, preview_rect.bottom + 14))

            sub_s = font_zen_body.render(arena["subtitle"], True, (180, 190, 185))
            surface.blit(sub_s, (draw_rect.x + 18, preview_rect.bottom + 42))

            # Linha divisória
            pygame.draw.line(surface, (50, 60, 55), (draw_rect.x + 18, preview_rect.bottom + 65), (draw_rect.right - 18, preview_rect.bottom + 65), 1)

            # Nível de Perigo
            hz_label = font_zen_body.render("Perigo:", True, (160, 160, 165))
            hz_val = font_zen_body.render(arena["hazard_level"], True, arena["hazard_color"])
            surface.blit(hz_label, (draw_rect.x + 18, preview_rect.bottom + 76))
            surface.blit(hz_val, (draw_rect.x + 75, preview_rect.bottom + 76))

            # Recursos e Táticas
            ft_label = font_zen_body.render("Cenário:", True, COLOR_GOLD)
            surface.blit(ft_label, (draw_rect.x + 18, preview_rect.bottom + 106))
            self._draw_multiline_text(surface, arena["features"], draw_rect.x + 18, preview_rect.bottom + 128, card_w - 36, font_zen_body, (200, 205, 200))

            tc_label = font_zen_body.render("Dica Tática:", True, (130, 210, 240))
            surface.blit(tc_label, (draw_rect.x + 18, preview_rect.bottom + 185))
            self._draw_multiline_text(surface, arena["tactics"], draw_rect.x + 18, preview_rect.bottom + 207, card_w - 36, font_zen_body, (175, 185, 180))

            # Badge [ SELECIONADO ]
            if is_sel:
                badge_surf = font_zen_sub.render("◄ SELECIONADO ►", True, COLOR_GOLD)
                badge_bg = pygame.Rect(draw_rect.centerx - badge_surf.get_width() // 2 - 10, draw_rect.bottom - 32, badge_surf.get_width() + 20, 22)
                pygame.draw.rect(surface, (20, 24, 22), badge_bg, border_radius=4)
                pygame.draw.rect(surface, COLOR_GOLD, badge_bg, 1, border_radius=4)
                surface.blit(badge_surf, (badge_bg.centerx - badge_surf.get_width() // 2, badge_bg.centery - badge_surf.get_height() // 2))

        # 3. Rodapé de Confirmação
        start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 65, 320, 42)
        pygame.draw.rect(surface, (30, 45, 35), start_btn, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, start_btn, 2, border_radius=8)
        btn_text = font_oriental_btn.render("INICIAR BATALHA [ENTER]", True, COLOR_GOLD)
        surface.blit(btn_text, (start_btn.centerx - btn_text.get_width() // 2, start_btn.centery - btn_text.get_height() // 2))

        tip_s = font_zen_tip.render("[A/D ou Setas] Mudar Arena  |  [ESC] Voltar aos Personagens", True, (160, 165, 160))
        surface.blit(tip_s, (SCREEN_WIDTH // 2 - tip_s.get_width() // 2, SCREEN_HEIGHT - 16))

    def _render_arena_mini_preview(self, surface: pygame.Surface, arena_id: str, rect: pygame.Rect):
        """Desenha a foto conceito ou vinheta gráfica representativa de cada arena."""
        cx = rect.centerx
        cy = rect.centery

        # Se houver portrait de arte conceitual carregado, exibe com recorte e acabamento
        img = self.preview_surfs.get(arena_id)
        if img:
            surface.blit(img, rect.topleft)
            # Se for ARENA_RANDOM, adiciona efeito especial de destino
            if arena_id == ARENA_RANDOM:
                pulse = 0.5 + 0.5 * math.sin(self.anim_time * 4.0)
                glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                glow.fill((120, 80, 200, int(35 + 25 * pulse)))
                surface.blit(glow, rect.topleft)

                q_font = pygame.font.Font(None, 56)
                q_surf = q_font.render("?", True, COLOR_GOLD)
                surface.blit(q_surf, (cx - q_surf.get_width() // 2, cy - q_surf.get_height() // 2))

            # Borda interna fina para acabamento de foto
            pygame.draw.rect(surface, (80, 90, 85), rect, 1, border_radius=6)
            return

        if arena_id == ARENA_BAMBOO:
            # Chão verde e laguinho azul
            pygame.draw.rect(surface, (28, 48, 26), rect, border_radius=6)
            pygame.draw.ellipse(surface, (32, 74, 98), (cx - 70, cy - 25, 140, 50))
            # Ponte de madeira cruzando
            pygame.draw.rect(surface, (112, 70, 42), (cx - 18, cy - 45, 36, 90), border_radius=2)
            pygame.draw.rect(surface, (78, 48, 28), (cx - 18, cy - 45, 36, 90), 2, border_radius=2)
            # Bambus verticais
            for bx in (-110, -85, -55, 60, 90, 115):
                by = cy + math.sin(bx * 0.1) * 20
                pygame.draw.line(surface, COLOR_BAMBOO, (cx + bx, rect.bottom - 8), (cx + bx, rect.top + 20), 4)
                pygame.draw.circle(surface, (102, 188, 78), (cx + bx, int(by)), 3)

        elif arena_id == ARENA_KYOTO:
            # Chão de pedra escuro e calçadas
            pygame.draw.rect(surface, (30, 24, 26), rect, border_radius=6)
            # Avenida de pedra central
            pygame.draw.polygon(surface, COLOR_KYOTO_STONE, [
                (rect.left + 50, rect.bottom), (rect.right - 50, rect.bottom),
                (rect.right - 90, rect.top), (rect.left + 90, rect.top)
            ])
            # Chamas no horizonte dos dois lados
            t = self.anim_time * 9.0
            for side, base_x in ((-1, rect.left + 35), (1, rect.right - 35)):
                for i in range(4):
                    fx = base_x + side * (i * 12)
                    fh = 24 + 12 * math.sin(t + i * 1.5)
                    pygame.draw.polygon(surface, (255, 60, 20), [(fx - 8, cy + 15), (fx + 8, cy + 15), (fx, cy + 15 - fh)])
                    pygame.draw.polygon(surface, (255, 210, 60), [(fx - 4, cy + 15), (fx + 4, cy + 15), (fx, cy + 15 - fh * 0.65)])

            # Silhueta da carruagem na rua
            c_pos = (math.sin(self.anim_time * 1.5) * 40)
            pygame.draw.rect(surface, COLOR_KYOTO_CARRIAGE_WOOD, (cx + c_pos - 24, cy - 8, 48, 28), border_radius=3)
            pygame.draw.circle(surface, (180, 140, 60), (int(cx + c_pos - 15), cy + 20), 8, 2)
            pygame.draw.circle(surface, (180, 140, 60), (int(cx + c_pos + 15), cy + 20), 8, 2)

        elif arena_id == ARENA_RANDOM:
            # Fundo místico com kanji de destino
            pygame.draw.rect(surface, (24, 20, 32), rect, border_radius=6)
            pulse = 0.5 + 0.5 * math.sin(self.anim_time * 4.0)
            rad = int(38 + 6 * pulse)
            pygame.draw.circle(surface, (50, 42, 70), (cx, cy), rad)
            pygame.draw.circle(surface, (140, 120, 210), (cx, cy), rad, 2)

            q_font = pygame.font.Font(None, 62)
            q_surf = q_font.render("?", True, COLOR_GOLD)
            surface.blit(q_surf, (cx - q_surf.get_width() // 2, cy - q_surf.get_height() // 2))

    def _draw_multiline_text(self, surface, text, x, y, max_w, font, color):
        words = text.split()
        lines = []
        cur_line = ""
        for w in words:
            test = cur_line + (" " if cur_line else "") + w
            if font.size(test)[0] <= max_w:
                cur_line = test
            else:
                lines.append(cur_line)
                cur_line = w
        if cur_line:
            lines.append(cur_line)

        for l_idx, line in enumerate(lines[:3]):
            rendered = font.render(line, True, color)
            surface.blit(rendered, (x, y + l_idx * 17))
