"""
Editor Visual Interativo de Controles Touchscreen (HUD Editor).
Permite ao jogador reposicionar os botões de ação na tela arrastando com o dedo,
ajustar a escala dos botões e restaurar os padrões ergonômicos de fábrica.
"""
import math
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_RED_AURA
from src.ui.fonts import get_title_font, get_text_font
from src.ui.font_manager import render_text_fx
from src.input.controls_storage import load_controls_config, save_controls_config


class TouchControlsEditorScreen:
    """Tela interativa de personalização do layout dos controles de toque."""

    def __init__(self, touch_controls):
        self.touch_controls = touch_controls
        self.is_open = False
        self.dragging_button = None  # "attack", "secondary", "dash"
        self.drag_offset = (0, 0)
        self.active_finger_id = None

        # Botões de interface do editor
        self.btn_save = pygame.Rect(SCREEN_WIDTH - 220, 24, 190, 48)
        self.btn_reset = pygame.Rect(SCREEN_WIDTH - 440, 24, 200, 48)
        self.btn_scale_small = pygame.Rect(40, 24, 100, 48)
        self.btn_scale_normal = pygame.Rect(150, 24, 110, 48)
        self.btn_scale_large = pygame.Rect(270, 24, 100, 48)

    def open(self):
        self.is_open = True
        self.dragging_button = None
        self.active_finger_id = None

    def close(self):
        self.is_open = False
        self.dragging_button = None

    def handle_event(self, event: pygame.event.Event, scaler=None) -> bool:
        if not self.is_open:
            return False

        # Obter coordenadas virtuais (1280x720)
        vx, vy = 0, 0
        is_down = False
        is_up = False
        is_motion = False
        fid = None

        if event.type == pygame.FINGERDOWN:
            fx, fy = event.x, event.y
            fid = event.finger_id
            if scaler:
                vx, vy = scaler.normalized_finger_to_virtual(fx, fy)
            else:
                vx, vy = fx * SCREEN_WIDTH, fy * SCREEN_HEIGHT
            is_down = True

        elif event.type == pygame.FINGERMOTION:
            fx, fy = event.x, event.y
            fid = event.finger_id
            if scaler:
                vx, vy = scaler.normalized_finger_to_virtual(fx, fy)
            else:
                vx, vy = fx * SCREEN_WIDTH, fy * SCREEN_HEIGHT
            is_motion = True

        elif event.type == pygame.FINGERUP:
            fid = event.finger_id
            is_up = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            vx, vy = scaler.screen_to_virtual(mx, my) if scaler else (mx, my)
            is_down = True
            fid = -999

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            vx, vy = scaler.screen_to_virtual(mx, my) if scaler else (mx, my)
            is_motion = True
            fid = -999

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            is_up = True
            fid = -999

        # Processar interação
        if is_down:
            # 1. Botões do topo
            if self.btn_save.collidepoint(vx, vy):
                # Salvar e fechar
                layout = self.touch_controls.get_layout_config()
                cfg = load_controls_config()
                save_controls_config(
                    cfg.get("keyboard", {}),
                    touch_mode=cfg.get("touch_mode", "auto"),
                    audio_cfg=cfg.get("audio", {}),
                    ai_difficulty=cfg.get("ai_difficulty", "normal"),
                    ui_mode=cfg.get("ui_mode", "auto"),
                    touch_controls_cfg=layout
                )
                self.close()
                return True

            if self.btn_reset.collidepoint(vx, vy):
                self.touch_controls.reset_to_default_layout()
                return True

            if self.btn_scale_small.collidepoint(vx, vy):
                cfg = self.touch_controls.get_layout_config()
                cfg["scale"] = 0.75
                self.touch_controls.apply_layout(cfg)
                return True

            if self.btn_scale_normal.collidepoint(vx, vy):
                cfg = self.touch_controls.get_layout_config()
                cfg["scale"] = 1.0
                self.touch_controls.apply_layout(cfg)
                return True

            if self.btn_scale_large.collidepoint(vx, vy):
                cfg = self.touch_controls.get_layout_config()
                cfg["scale"] = 1.30
                self.touch_controls.apply_layout(cfg)
                return True

            # 2. Arrastar botões de combate
            btns = [
                ("attack", self.touch_controls.btn_attack),
                ("secondary", self.touch_controls.btn_secondary),
                ("dash", self.touch_controls.btn_dash),
            ]
            for name, btn in btns:
                dist = math.hypot(vx - btn.cx, vy - btn.cy)
                if dist <= btn.radius * 1.3:
                    self.dragging_button = name
                    self.active_finger_id = fid
                    self.drag_offset = (btn.cx - vx, btn.cy - vy)
                    return True

        elif is_motion and self.dragging_button:
            if self.active_finger_id == fid:
                btn_obj = getattr(self.touch_controls, f"btn_{self.dragging_button}")
                new_x = vx + self.drag_offset[0]
                new_y = vy + self.drag_offset[1]
                # Limitar aos limites da tela (lado direito preferencial, evitando topo)
                pad = btn_obj.radius + 10
                btn_obj.cx = max(SCREEN_WIDTH * 0.40, min(SCREEN_WIDTH - pad, new_x))
                btn_obj.cy = max(90 + pad, min(SCREEN_HEIGHT - pad, new_y))
                return True

        elif is_up:
            if self.dragging_button and (self.active_finger_id == fid or fid == -999):
                self.dragging_button = None
                self.active_finger_id = None
                return True

        return True  # Modal consome todos os eventos enquanto aberto

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_small: pygame.font.Font):
        if not self.is_open:
            return

        # Fundo escurecido semi-translúcido
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 14, 215))
        surface.blit(overlay, (0, 0))

        # Faixa indicadora do analógico flutuante à esquerda
        left_zone = pygame.Rect(0, 0, int(SCREEN_WIDTH * 0.50), SCREEN_HEIGHT)
        pygame.draw.rect(surface, (40, 55, 50, 45), left_zone)
        pygame.draw.line(surface, (120, 150, 140, 80), (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 1)

        font_title = get_title_font(26)
        font_sub = get_text_font(18)

        # Instrução da zona esquerda
        hint_left = font_sub.render("ÁREA DO ANALÓGICO FLUTUANTE (Toque em qualquer lugar)", True, (150, 180, 170))
        surface.blit(hint_left, (40, SCREEN_HEIGHT - 60))

        # Título central
        title_surf = render_text_fx(font_title, "PERSONALIZAR CONTROLES TOUCH", COLOR_GOLD, outline=True, outline_width=1)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 88))

        sub_desc = font_sub.render("Arraste os botões de ação para posicioná-los como preferir", True, (220, 215, 200))
        surface.blit(sub_desc, (SCREEN_WIDTH // 2 - sub_desc.get_width() // 2, 124))

        # Barra de ferramentas no topo
        cur_scale = self.touch_controls.button_scale

        # Botões de escala
        for rect, label, sc_val in [
            (self.btn_scale_small, "Pequeno", 0.75),
            (self.btn_scale_normal, "Médio", 1.0),
            (self.btn_scale_large, "Grande", 1.30)
        ]:
            active = abs(cur_scale - sc_val) < 0.1
            bg_col = (195, 32, 42, 220) if active else (28, 34, 30, 200)
            b_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(b_surf, bg_col, (0, 0, rect.w, rect.h), border_radius=8)
            pygame.draw.rect(b_surf, COLOR_GOLD if active else (120, 100, 60), (0, 0, rect.w, rect.h), 1, border_radius=8)
            surface.blit(b_surf, rect.topleft)
            txt = font_small.render(label, True, COLOR_WHITE if active else (200, 195, 180))
            surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # Botão Restaurar
        rst_surf = pygame.Surface((self.btn_reset.w, self.btn_reset.h), pygame.SRCALPHA)
        pygame.draw.rect(rst_surf, (45, 38, 42, 210), (0, 0, self.btn_reset.w, self.btn_reset.h), border_radius=8)
        pygame.draw.rect(rst_surf, (180, 140, 70), (0, 0, self.btn_reset.w, self.btn_reset.h), 1, border_radius=8)
        surface.blit(rst_surf, self.btn_reset.topleft)
        rst_txt = font_small.render("Restaurar Padrão", True, (240, 225, 200))
        surface.blit(rst_txt, (self.btn_reset.centerx - rst_txt.get_width() // 2, self.btn_reset.centery - rst_txt.get_height() // 2))

        # Botão Salvar
        sav_surf = pygame.Surface((self.btn_save.w, self.btn_save.h), pygame.SRCALPHA)
        pygame.draw.rect(sav_surf, (35, 80, 50, 230), (0, 0, self.btn_save.w, self.btn_save.h), border_radius=8)
        pygame.draw.rect(sav_surf, (110, 225, 140), (0, 0, self.btn_save.w, self.btn_save.h), 2, border_radius=8)
        surface.blit(sav_surf, self.btn_save.topleft)
        sav_txt = font_small.render("Salvar e Fechar", True, COLOR_WHITE)
        surface.blit(sav_txt, (self.btn_save.centerx - sav_txt.get_width() // 2, self.btn_save.centery - sav_txt.get_height() // 2))

        # Renderizar botões arrastáveis
        self.touch_controls.btn_attack.render(surface, font_large, font_small)
        self.touch_controls.btn_secondary.render(surface, font_large, font_small)
        self.touch_controls.btn_dash.render(surface, font_large, font_small)

        # Destacar botão selecionado sendo arrastado
        if self.dragging_button:
            btn_obj = getattr(self.touch_controls, f"btn_{self.dragging_button}")
            pygame.draw.circle(surface, (255, 235, 100), (int(btn_obj.cx), int(btn_obj.cy)), int(btn_obj.radius + 8), width=3)
