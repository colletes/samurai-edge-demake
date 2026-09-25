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
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_BG
)
from src.i18n import t

MODE_ARCADE = 0
MODE_VERSUS = 1
MODE_OPTIONS = 2

class SumieTitleScreen:
    def __init__(self):
        self.selected_mode = MODE_VERSUS
        self.anim_time = 0.0
        self.notice_timer = 0.0
        self.notice_text = ""

        # Carregar imagem conceitual Sumi-E se disponível
        self.bg_surf = None
        bg_path = os.path.join("assets", "concepts", "sumie_title_logo_concept.jpg")
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
            except Exception:
                self.bg_surf = None

        # Partículas de tinta / cinzas atmosféricas
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
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._activate_current_mode()

        elif event.type == pygame.JOYBUTTONDOWN:
            if ctrl_mgr.is_event_menu_confirm(event) or event.button in (0, 1, 7):
                return self._activate_current_mode()
            elif ctrl_mgr.is_event_menu_cancel(event) or event.button in (2, 1):
                return "QUIT"

        elif event.type == pygame.JOYHATMOTION:
            _, hy = event.value
            if hy > 0:
                self.selected_mode = (self.selected_mode - 1) % 3
            elif hy < 0:
                self.selected_mode = (self.selected_mode + 1) % 3

        elif event.type == pygame.JOYAXISMOTION:
            # Analógico esquerdo para navegação vertical nas opções
            if event.axis == 1:
                if event.value > 0.65 and not self._axis_y_held:
                    self.selected_mode = (self.selected_mode + 1) % 3
                    self._axis_y_held = True
                elif event.value < -0.65 and not self._axis_y_held:
                    self.selected_mode = (self.selected_mode - 1) % 3
                    self._axis_y_held = True
                elif abs(event.value) < 0.25:
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
            self.notice_timer = 2.0
            self.notice_text = "MODO ARCADE EM DESENVOLVIMENTO (EM BREVE!)"
            return None
        elif self.selected_mode == MODE_VERSUS:
            return "VERSUS"
        elif self.selected_mode == MODE_OPTIONS:
            return "OPTIONS"
        return None

    def update(self, dt: float):
        self.anim_time += dt
        if self.notice_timer > 0:
            self.notice_timer -= dt

        # Atualizar partículas de cinzas
        for p in self.particles:
            p["x"] += p["speed_x"] + 0.3 * math.sin(self.anim_time + p["y"] * 0.05)
            p["y"] += p["speed_y"]
            if p["y"] < -10:
                p["y"] = SCREEN_HEIGHT + 10
                p["x"] = random.uniform(0, SCREEN_WIDTH)

    def render(self, surface: pygame.Surface, font_large, font_mid, font_small):
        # 1. Desenhar Fundo Sumi-E
        if self.bg_surf:
            surface.blit(self.bg_surf, (0, 0))
        else:
            # Fallback procedural em nanquim
            surface.fill((22, 22, 24))
            pygame.draw.circle(surface, (230, 230, 230), (SCREEN_WIDTH - 200, 160), 65) # Lua crescente

        # 2. Partículas atmosféricas de cinzas
        for p in self.particles:
            alpha_col = (180, 175, 170)
            pygame.draw.circle(surface, alpha_col, (int(p["x"]), int(p["y"])), int(p["size"]))

        # 3. Painel do Menu de Modos de Jogo (Design minimalista de pergaminho escuro no rodapé)
        menu_w = 400
        menu_h = 145
        menu_x = (SCREEN_WIDTH - menu_w) // 2
        menu_y = SCREEN_HEIGHT - 165

        # Fundo do menu com borda de nanquim
        panel_surf = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
        panel_surf.fill((14, 14, 16, 235))
        surface.blit(panel_surf, (menu_x, menu_y))
        pygame.draw.rect(surface, (70, 65, 60), (menu_x, menu_y, menu_w, menu_h), 2, border_radius=8)

        # Itens do Menu
        modes = [
            {"id": MODE_ARCADE, "name": "ARCADE", "sub": "[EM BREVE]", "enabled": False},
            {"id": MODE_VERSUS, "name": "VERSUS (1P / 2P)", "sub": "DUELO IMEDIATO", "enabled": True},
            {"id": MODE_OPTIONS, "name": "OPTIONS", "sub": "CONFIGURAR CONTROLES", "enabled": True},
        ]

        self.btn_rects = []
        item_y = menu_y + 12
        for m in modes:
            is_sel = (self.selected_mode == m["id"])
            item_rect = pygame.Rect(menu_x + 16, item_y, menu_w - 32, 36)
            self.btn_rects.append(item_rect)

            if is_sel:
                # Efeito pincelada dourada na seleção
                pulse = 0.5 + 0.5 * math.sin(self.anim_time * 6.0)
                bg_col = (55, 45, 20) if m["enabled"] else (35, 35, 38)
                border_col = (COLOR_GOLD[0], int(COLOR_GOLD[1] * pulse + 80 * (1 - pulse)), COLOR_GOLD[2]) if m["enabled"] else (90, 90, 95)
                pygame.draw.rect(surface, bg_col, item_rect, border_radius=5)
                pygame.draw.rect(surface, border_col, item_rect, 2, border_radius=5)

                # Indicador de pincel à esquerda
                brush_ind = font_mid.render("►", True, border_col)
                surface.blit(brush_ind, (item_rect.x - 20, item_rect.y + 6))

            # Texto Principal
            if not m["enabled"]:
                text_col = (110, 110, 115)
                badge_col = (140, 90, 90)
            elif is_sel:
                text_col = COLOR_GOLD
                badge_col = (220, 200, 140)
            else:
                text_col = (200, 200, 205)
                badge_col = (150, 150, 155)

            name_s = font_mid.render(m["name"], True, text_col)
            surface.blit(name_s, (item_rect.x + 16, item_rect.y + 6))

            sub_s = font_small.render(m["sub"], True, badge_col)
            surface.blit(sub_s, (item_rect.right - sub_s.get_width() - 16, item_rect.y + 10))

            item_y += 42

        # 4. Mensagem de aviso se tentar escolher modo desabilitado
        if self.notice_timer > 0:
            notice_surf = font_small.render(self.notice_text, True, (255, 120, 120))
            notice_rect = pygame.Rect(SCREEN_WIDTH // 2 - notice_surf.get_width() // 2 - 12, menu_y - 32, notice_surf.get_width() + 24, 26)
            pygame.draw.rect(surface, (24, 16, 16), notice_rect, border_radius=4)
            pygame.draw.rect(surface, (200, 60, 60), notice_rect, 1, border_radius=4)
            surface.blit(notice_surf, (notice_rect.centerx - notice_surf.get_width() // 2, notice_rect.centery - notice_surf.get_height() // 2))

        # 5. Rodapé com instruções
        tip_text = font_small.render("[W/S ou Setas] Mover  |  [ENTER / ESPAÇO] Confirmar  |  [ESC] Sair", True, (160, 155, 150))
        surface.blit(tip_text, (SCREEN_WIDTH // 2 - tip_text.get_width() // 2, SCREEN_HEIGHT - 16))
