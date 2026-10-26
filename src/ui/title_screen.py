"""
Tela de Título estilizada em Sumi-E (Pintura tradicional em nanquim e papiro).
Apresenta o logo artístico de Samurai Edge: Bakumatsu, névoa fluida,
partículas de cinzas em suspensão e o seletor de modos de jogo:
  - ARCADE (Em Breve)
  - VERSUS (Habilitado por padrão)
  - OPTIONS (Abre menu de configurações de controles)
"""
import os
import math
import random
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_BG, get_asset_path
)
from src.i18n import t
from src.edition import is_demo
from src.effects import parchment as pm
from src.ui.font_manager import render_text_fx
from src.ui.fonts import get_title_font, get_text_font

MODE_ARCADE = 0
MODE_VERSUS = 1
MODE_OPTIONS = 2

class SumieTitleScreen:
    def __init__(self):
        self.selected_mode = MODE_VERSUS
        self.anim_time = 0.0
        self.notice_timer = 0.0
        self.notice_text = ""

        # Pétalas de cerejeira para a tela de título em pergaminho Sumi-E
        self.petals = pm.PetalField(count=26, seed=9)

        # Carregar imagem conceitual Sumi-E se disponível (para fallback)
        self.bg_surf = None
        bg_path = get_asset_path("assets/concepts/sumie_title_logo_concept.jpg")
        if os.path.exists(bg_path):
            try:
                try:
                    raw_img = pygame.image.load(bg_path).convert()
                except Exception:
                    raw_img = pygame.image.load(bg_path)
                self.bg_surf = pygame.transform.smoothscale(raw_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                # Aplicar vinheta escurecida para legibilidade do menu
                vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                for i in range(140):
                    alpha = int(195 * (i / 140.0) ** 1.4)
                    pygame.draw.rect(vignette, (10, 10, 12, alpha), (0, SCREEN_HEIGHT - 190 + i, SCREEN_WIDTH, 2))
                self.bg_surf.blit(vignette, (0, 0))
                self.bg_surf.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MAX)
            except Exception:
                self.bg_surf = None

        # Partículas de tinta / cinzas atmosféricas (para fallback)
        self.particles = []
        for _ in range(35):
            self.particles.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(0, SCREEN_HEIGHT),
                "speed_x": random.uniform(-0.5, 0.5),
                "speed_y": random.uniform(-0.8, -0.2),
                "size": random.uniform(1.5, 3.5),
                "alpha": random.randint(60, 180)
            })

        self.btn_rects = []
        self._axis_y_held = False

    def handle_event(self, event) -> str | None:
        """
        Retorna:
          - "VERSUS": se o jogador confirmar Versus
          - "ARCADE": se o jogador confirmar Arcade
          - "OPTIONS": se o jogador confirmar Opções
          - "QUIT": se o jogador cancelar/voltar na tela inicial
          - None: se ainda na tela
        """
        from src.input.controller_manager import get_controller_manager
        ctrl_mgr = get_controller_manager()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_mode = (self.selected_mode - 1) % 3
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_mode = (self.selected_mode + 1) % 3
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e, pygame.K_j):
                return self._activate_current_mode()
            elif event.key == pygame.K_ESCAPE:
                return "QUIT"

        elif event.type == pygame.JOYBUTTONDOWN:
            from src.input.controller_manager import get_dpad_motion_from_event
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                _, dy = d_dir
                if dy != 0:
                    self.selected_mode = (self.selected_mode + dy) % 3
                    try:
                        from src.audio.sound_events import SoundEvent
                        from src.audio.sound_manager import SoundManager
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass
                return None

            if ctrl_mgr.is_event_menu_confirm(event) or ctrl_mgr.is_event_menu_pause(event) or event.button in (0, 2, 3, 6, 7):
                return self._activate_current_mode()
            elif event.button in (4, 5): # Share / Guide para sair da tela inicial
                return "QUIT"

        elif event.type == pygame.JOYHATMOTION:
            from src.input.controller_manager import get_dpad_motion_from_event
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                _, dy = d_dir
                if dy != 0:
                    self.selected_mode = (self.selected_mode + dy) % 3
                    try:
                        from src.audio.sound_events import SoundEvent
                        from src.audio.sound_manager import SoundManager
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass

        elif event.type == pygame.JOYAXISMOTION:
            # Analógico esquerdo para navegação vertical nas opções
            if event.axis == 1:
                val = -event.value if getattr(ctrl_mgr, "invert_y", False) else event.value
                if val > 0.65 and not self._axis_y_held:
                    self.selected_mode = (self.selected_mode + 1) % 3
                    self._axis_y_held = True
                    try:
                        from src.audio.sound_events import SoundEvent
                        from src.audio.sound_manager import SoundManager
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass
                elif val < -0.65 and not self._axis_y_held:
                    self.selected_mode = (self.selected_mode - 1) % 3
                    self._axis_y_held = True
                    try:
                        from src.audio.sound_events import SoundEvent
                        from src.audio.sound_manager import SoundManager
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass
                elif abs(val) < 0.25:
                    self._axis_y_held = False

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for idx, r in enumerate(self.btn_rects):
                if r.collidepoint(mx, my):
                    self.selected_mode = idx

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for idx, r in enumerate(self.btn_rects):
                if r.collidepoint(mx, my):
                    self.selected_mode = idx
                    return self._activate_current_mode()

        return None

    def _activate_current_mode(self) -> str | None:
        if self.selected_mode == MODE_ARCADE:
            if is_demo():
                self.notice_timer = 2.0
                self.notice_text = t("demo_locked_notice")
                return None
            return "ARCADE"
        elif self.selected_mode == MODE_VERSUS:
            return "VERSUS"
        elif self.selected_mode == MODE_OPTIONS:
            return "OPTIONS"
        return None

    def update(self, dt: float):
        self.anim_time += dt
        if self.notice_timer > 0:
            self.notice_timer -= dt

        # Atualizar pétalas de cerejeira
        self.petals.update(dt)

        # Atualizar partículas de cinzas (para fallback)
        for p in self.particles:
            p["x"] += p["speed_x"] + 0.3 * math.sin(self.anim_time + p["y"] * 0.05)
            p["y"] += p["speed_y"]
            if p["y"] < -10:
                p["y"] = SCREEN_HEIGHT + 10
                p["x"] = random.uniform(0, SCREEN_WIDTH)

    def render(self, surface: pygame.Surface, font_large, font_mid, font_small):
        parch = pm.get_backdrop() is not None
        if parch:
            self._render_parchment(surface, font_large, font_mid, font_small)
        else:
            self._render_fallback(surface, font_large, font_mid, font_small)

    def _render_parchment(self, surface: pygame.Surface, font_large, font_mid, font_small):
        # 1. Paisagem Sumi-E em papel envelhecido e moldura de madeira
        pm.draw_backdrop(surface)

        # 2. Pétalas de cerejeira em suspensão
        self.petals.draw(surface)

        # 3. Logotipo Artístico Caligrafado (Shojumaru com glow dourado e nanquim profundo)
        font_title_big = get_title_font(46)
        font_title_sub = get_title_font(18)
        font_menu_title = get_title_font(18)
        font_menu_sub = get_text_font(13)
        font_menu_tip = get_text_font(14)

        title_text = t("game_title")
        sub_text = t("game_subtitle")

        title_surf = render_text_fx(
            font_title_big,
            title_text,
            color=(28, 22, 18),
            outline=True,
            outline_color=(58, 48, 38),
            outline_width=1,
            glow=True,
            glow_color=(212, 175, 55),
            glow_width=3,
            shadow=True,
            shadow_color=(20, 16, 12),
            shadow_offset=(2, 2)
        )
        title_y = 65
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, title_y))

        sub_surf = render_text_fx(
            font_title_sub,
            f"―  {sub_text}  ―",
            color=pm.SEAL_RED,
            glow=True,
            glow_color=(235, 205, 140),
            glow_width=2,
            shadow=True,
            shadow_color=(30, 20, 18),
            shadow_offset=(1, 1)
        )
        sub_y = title_y + title_surf.get_height() - 8
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, sub_y))

        # Brasão da garça no canto superior direito
        pm.draw_crest(surface, SCREEN_WIDTH - 120, 26, scale=0.68)

        # 4. Três Cartões de Modo de Jogo montados sobre a tabuleta no quadrante direito
        modes = [
            {"id": MODE_ARCADE, "name": t("mode_arcade"), "sub": t("demo_locked_sub") if is_demo() else t("mode_arcade_sub"), "enabled": not is_demo()},
            {"id": MODE_VERSUS, "name": t("mode_versus"), "sub": t("mode_immediate_duel"), "enabled": True},
            {"id": MODE_OPTIONS, "name": t("mode_options"), "sub": t("mode_configure_controls"), "enabled": True},
        ]

        card_w = 420
        card_h = 50
        gap = 16
        start_x = SCREEN_WIDTH - card_w - 75  # ~785, posicionado perfeitamente sobre o quadrante direito
        start_y = 355

        # Tabuleta de pergaminho de montagem com varas cilíndricas tradicionais
        scroll_rect = pygame.Rect(start_x - 16, start_y - 28, card_w + 32, 3 * (card_h + gap) + 32)
        pm.draw_scroll(surface, scroll_rect, seed=55, rod_top=True)

        self.btn_rects = []
        for idx, m in enumerate(modes):
            item_rect = pygame.Rect(start_x, start_y + idx * (card_h + gap), card_w, card_h)
            self.btn_rects.append(item_rect)

            is_sel = (self.selected_mode == m["id"])

            # Cartão de papel rasgado individual
            pm.draw_paper_card(surface, item_rect, seed=idx * 29 + 11)

            if is_sel:
                # Pincelada vermelha e borda de nanquim no item focado
                stroke_col = pm.SEAL_RED if m["enabled"] else (100, 95, 95)
                pm.draw_brush_highlight(surface, item_rect.inflate(12, 6), color=stroke_col, seed=idx + 3, alpha=225)
                pm.draw_ink_border(surface, item_rect, color=stroke_col, width=2, seed=idx + 1)

                # Indicador de seta de pincel
                arrow_pts = [
                    (item_rect.x + 12, item_rect.centery - 6),
                    (item_rect.x + 20, item_rect.centery),
                    (item_rect.x + 12, item_rect.centery + 6)
                ]
                pygame.draw.polygon(surface, (252, 246, 230), arrow_pts)

                name_s = font_menu_title.render(m["name"], True, (252, 246, 230))
                sub_max_w = card_w - name_s.get_width() - 56
                sub_s = pm.fit_text(font_menu_sub, m["sub"], (240, 225, 190), sub_max_w)
                surface.blit(name_s, (item_rect.x + 28, item_rect.centery - name_s.get_height() // 2))
                surface.blit(sub_s, (item_rect.right - sub_s.get_width() - 16, item_rect.centery - sub_s.get_height() // 2))
            else:
                pm.draw_ink_border(surface, item_rect, color=pm.INK_SOFT, width=1, seed=idx + 1, alpha=150)

                text_col = pm.INK if m["enabled"] else pm.INK_SOFT
                name_s = pm.render_ink(font_menu_title, m["name"], color=text_col)
                sub_col = pm.INK_SOFT if m["enabled"] else (135, 130, 125)
                sub_max_w = card_w - name_s.get_width() - 44
                sub_s = pm.fit_text(font_menu_sub, m["sub"], sub_col, sub_max_w)
                surface.blit(name_s, (item_rect.x + 18, item_rect.centery - name_s.get_height() // 2))
                surface.blit(sub_s, (item_rect.right - sub_s.get_width() - 16, item_rect.centery - sub_s.get_height() // 2))

        # 5. Mensagem de aviso se tentar escolher modo desabilitado
        if self.notice_timer > 0:
            notice_rect = pygame.Rect(start_x, start_y - 42, card_w, 28)
            pm.draw_paper_card(surface, notice_rect, seed=89)
            pm.draw_ink_border(surface, notice_rect, color=pm.SEAL_RED, width=1)
            notice_surf = pm.fit_text(font_menu_tip, self.notice_text, pm.SEAL_RED, card_w - 20)
            surface.blit(notice_surf, (notice_rect.centerx - notice_surf.get_width() // 2, notice_rect.centery - notice_surf.get_height() // 2))

        # 6. Rodapé com instruções em Zen Antique
        if is_demo():
            badge = font_menu_title.render(t("demo_badge"), True, pm.SEAL_RED)
            surface.blit(badge, (SCREEN_WIDTH - badge.get_width() - 24, 20))
        tip_text = pm.fit_text(font_menu_tip, t("title_menu_hint"), pm.INK_SOFT, SCREEN_WIDTH - 80)
        surface.blit(tip_text, (SCREEN_WIDTH // 2 - tip_text.get_width() // 2, SCREEN_HEIGHT - 20))

    def _render_fallback(self, surface: pygame.Surface, font_large, font_mid, font_small):
        # 1. Desenhar Fundo Sumi-E
        if self.bg_surf:
            surface.blit(self.bg_surf, (0, 0))
        else:
            # Fallback procedural em nanquim
            surface.fill((22, 22, 24))
            pygame.draw.circle(surface, (230, 230, 230), (SCREEN_WIDTH - 200, 160), 65) # Lua crescente
        surface.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MAX)

        # 2. Partículas atmosféricas de cinzas
        for p in self.particles:
            alpha_col = (180, 175, 170)
            pygame.draw.circle(surface, alpha_col, (int(p["x"]), int(p["y"])), int(p["size"]))

        # 3. Painel do Menu de Modos de Jogo em Tabuleta Kanban Laqueada
        font_menu_title = get_title_font(17)
        font_menu_sub = get_text_font(13)
        font_menu_tip = get_text_font(14)

        menu_w = 440
        menu_h = 152
        menu_x = (SCREEN_WIDTH - menu_w) // 2
        menu_y = SCREEN_HEIGHT - 172

        # Fundo do menu com borda de nanquim e encaixes de ferro
        panel_surf = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
        panel_surf.fill((16, 14, 16, 240))
        surface.blit(panel_surf, (menu_x, menu_y))
        pygame.draw.rect(surface, (80, 72, 65), (menu_x, menu_y, menu_w, menu_h), 2, border_radius=6)
        pygame.draw.rect(surface, (45, 40, 38), (menu_x + 4, menu_y + 4, menu_w - 8, menu_h - 8), 1, border_radius=4)

        # Itens do Menu
        modes = [
            {"id": MODE_ARCADE, "name": t("mode_arcade"), "sub": t("demo_locked_sub") if is_demo() else t("mode_arcade_sub"), "enabled": not is_demo()},
            {"id": MODE_VERSUS, "name": t("mode_versus"), "sub": t("mode_immediate_duel"), "enabled": True},
            {"id": MODE_OPTIONS, "name": t("mode_options"), "sub": t("mode_configure_controls"), "enabled": True},
        ]

        self.btn_rects = []
        item_y = menu_y + 12
        for m in modes:
            is_sel = (self.selected_mode == m["id"])
            item_rect = pygame.Rect(menu_x + 14, item_y, menu_w - 28, 38)
            self.btn_rects.append(item_rect)

            if is_sel:
                # Efeito tabuleta dourada na seleção
                pulse = 0.5 + 0.5 * math.sin(self.anim_time * 6.0)
                bg_col = (54, 44, 24) if m["enabled"] else (35, 35, 38)
                border_col = (int(255 * pulse + 190 * (1 - pulse)), int(210 * pulse + 140 * (1 - pulse)), 50) if m["enabled"] else (90, 90, 95)
                pygame.draw.rect(surface, bg_col, item_rect, border_radius=4)
                pygame.draw.rect(surface, border_col, item_rect, 2, border_radius=4)

                # Indicador de corte de katana / seta em polígono
                arrow_pts = [
                    (item_rect.x + 8, item_rect.centery - 6),
                    (item_rect.x + 16, item_rect.centery),
                    (item_rect.x + 8, item_rect.centery + 6)
                ]
                pygame.draw.polygon(surface, border_col, arrow_pts)
            else:
                pygame.draw.rect(surface, (26, 24, 26), item_rect, border_radius=4)
                pygame.draw.rect(surface, (58, 52, 48), item_rect, 1, border_radius=4)

            # Detalhes de encaixe de ferro nas laterais da tabuleta
            pygame.draw.line(surface, (70, 65, 60), (item_rect.x + 4, item_rect.y), (item_rect.x + 4, item_rect.bottom), 1)
            pygame.draw.line(surface, (70, 65, 60), (item_rect.right - 4, item_rect.y), (item_rect.right - 4, item_rect.bottom), 1)

            # Texto Principal (Shojumaru)
            if not m["enabled"]:
                text_col = (110, 110, 115)
                badge_col = (140, 90, 90)
            elif is_sel:
                text_col = COLOR_GOLD
                badge_col = (235, 215, 150)
            else:
                text_col = (210, 205, 200)
                badge_col = (165, 160, 155)

            name_x = item_rect.x + 24 if is_sel else item_rect.x + 14
            name_s = font_menu_title.render(m["name"], True, text_col)
            surface.blit(name_s, (name_x, item_rect.centery - name_s.get_height() // 2))

            sub_s = font_menu_sub.render(m["sub"], True, badge_col)
            surface.blit(sub_s, (item_rect.right - sub_s.get_width() - 14, item_rect.centery - sub_s.get_height() // 2))

            item_y += 44

        # 4. Mensagem de aviso se tentar escolher modo desabilitado
        if self.notice_timer > 0:
            notice_surf = font_menu_tip.render(self.notice_text, True, (255, 120, 120))
            notice_rect = pygame.Rect(SCREEN_WIDTH // 2 - notice_surf.get_width() // 2 - 12, menu_y - 32, notice_surf.get_width() + 24, 26)
            pygame.draw.rect(surface, (24, 16, 16), notice_rect, border_radius=4)
            pygame.draw.rect(surface, (200, 60, 60), notice_rect, 1, border_radius=4)
            surface.blit(notice_surf, (notice_rect.centerx - notice_surf.get_width() // 2, notice_rect.centery - notice_surf.get_height() // 2))

        # 5. Rodapé com instruções em Zen Antique
        if is_demo():
            badge = font_menu_title.render(t("demo_badge"), True, COLOR_GOLD)
            surface.blit(badge, (SCREEN_WIDTH - badge.get_width() - 24, 20))
        tip_text = font_menu_tip.render(t("title_menu_hint"), True, (175, 170, 165))
        surface.blit(tip_text, (SCREEN_WIDTH // 2 - tip_text.get_width() // 2, SCREEN_HEIGHT - 16))
