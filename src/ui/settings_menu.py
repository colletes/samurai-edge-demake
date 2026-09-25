"""
Tela e menu interativo de Configuração de Controles (Settings).
Permite visualizar e remapear teclas para o Samurai Vermelho e Azul tanto por teclado quanto por mouse.
"""
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_RED_AURA, COLOR_BLUE_AURA,
    DEFAULT_CONTROLS
)

def format_key_name(key_code: int) -> str:
    """Retorna uma representação amigável e legível para a tecla."""
    name_map = {
        pygame.K_UP: "SETA CIMA",
        pygame.K_DOWN: "SETA BAIXO",
        pygame.K_LEFT: "SETA ESQUERDA",
        pygame.K_RIGHT: "SETA DIREITA",
        pygame.K_SPACE: "ESPAÇO",
        pygame.K_RETURN: "ENTER",
        pygame.K_LSHIFT: "SHIFT ESQ",
        pygame.K_RSHIFT: "SHIFT DIR",
        pygame.K_LCTRL: "CTRL ESQ",
        pygame.K_RCTRL: "CTRL DIR",
        pygame.K_TAB: "TAB",
        pygame.K_ESCAPE: "ESC",
    }
    if key_code in name_map:
        return name_map[key_code]
    key_str = pygame.key.name(key_code)
    return key_str.upper()

class SettingsMenu:
    def __init__(self, controls: dict, touch_controls=None):
        self.controls = controls
        self.touch_controls = touch_controls
        self.is_open = False
        self.waiting_for_key_action = None  # Nome da ação sendo remapeada (ex: "P1_ATTACK")
        self.selected_index = 0
        self.blink_timer = 0.0
        self._axis_y_held = False

        # Definição dos itens remapeáveis
        self.items = [
            # Jogador 1 (Kenshi)
            ("P1_UP", "Kenshi Mover Cima", "red"),
            ("P1_DOWN", "Kenshi Mover Baixo", "red"),
            ("P1_LEFT", "Kenshi Mover Esquerda", "red"),
            ("P1_RIGHT", "Kenshi Mover Direita", "red"),
            ("P1_ATTACK", "Kenshi Iai Flash Slash", "red"),
            ("P1_DASH", "Kenshi Dash / Esquiva", "red"),

            # Jogador 2 (Musashi)
            ("P2_UP", "Musashi Mover Cima", "blue"),
            ("P2_DOWN", "Musashi Mover Baixo", "blue"),
            ("P2_LEFT", "Musashi Mover Esquerda", "blue"),
            ("P2_RIGHT", "Musashi Mover Direita", "blue"),
            ("P2_ATTACK", "Musashi Combo 3-Cortes", "blue"),
            ("P2_PARRY", "Musashi Defesa / Parry", "blue"),
        ]

        # Áreas clicáveis na tela (atualizadas durante o render)
        self.button_rects: list[tuple[pygame.Rect, int]] = []
        self.touch_toggle_rect = pygame.Rect(0, 0, 0, 0)

    def open(self):
        self.is_open = True
        self.waiting_for_key_action = None

    def close(self):
        self.is_open = False
        self.waiting_for_key_action = None

    def reset_to_defaults(self):
        """Restaura os controles para o padrão de fábrica."""
        for k, v in DEFAULT_CONTROLS.items():
            self.controls[k] = v

    def cycle_touch_mode(self):
        if self.touch_controls:
            from src.input.touch_controls import TOUCH_MODE_AUTO, TOUCH_MODE_ALWAYS, TOUCH_MODE_OFF
            order = [TOUCH_MODE_AUTO, TOUCH_MODE_ALWAYS, TOUCH_MODE_OFF]
            cur_idx = order.index(self.touch_controls.mode) if self.touch_controls.mode in order else 0
            self.touch_controls.mode = order[(cur_idx + 1) % len(order)]

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Processa eventos enquanto o menu de configurações está aberto.
        Retorna True se o evento foi consumido pelo menu.
        """
        if not self.is_open:
            return False

        from src.input.controller_manager import get_controller_manager
        ctrl_mgr = get_controller_manager()

        # Se estiver esperando uma nova tecla/botão para remapear
        if self.waiting_for_key_action is not None:
            if event.type == pygame.KEYDOWN:
                # Cancelar remapeamento se for ESC
                if event.key == pygame.K_ESCAPE:
                    self.waiting_for_key_action = None
                else:
                    self.controls[self.waiting_for_key_action] = event.key
                    self.waiting_for_key_action = None
                return True
            elif event.type == pygame.JOYBUTTONDOWN:
                # Remapear ação no controle correspondente (P1 ou P2)
                act_name = "attack" if "ATTACK" in self.waiting_for_key_action else ("dash" if ("DASH" in self.waiting_for_key_action or "PARRY" in self.waiting_for_key_action) else "attack")
                p_idx = 1 if "P2" in self.waiting_for_key_action else 0
                ctrl_mgr.remap_action(p_idx, act_name, event.button)
                self.waiting_for_key_action = None
                return True
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                # Cancelar espera ao clicar fora
                self.waiting_for_key_action = None
                return True
            return True

        # Suporte a Gamepad no menu de configurações
        if event.type == pygame.JOYBUTTONDOWN:
            if ctrl_mgr.is_event_menu_confirm(event) or event.button in (0, 1):
                action_key, _, _ = self.items[self.selected_index]
                self.waiting_for_key_action = action_key
                return True
            elif ctrl_mgr.is_event_menu_cancel(event) or ctrl_mgr.is_event_menu_pause(event) or event.button in (2, 6, 9):
                self.close()
                return True
            elif event.button in (3, 4):
                self.cycle_touch_mode()
                return True

        elif event.type == pygame.JOYHATMOTION:
            _, hy = event.value
            if hy > 0:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif hy < 0:
                self.selected_index = (self.selected_index + 1) % len(self.items)

        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
                if event.value > 0.65 and not self._axis_y_held:
                    self.selected_index = (self.selected_index + 1) % len(self.items)
                    self._axis_y_held = True
                elif event.value < -0.65 and not self._axis_y_held:
                    self.selected_index = (self.selected_index - 1) % len(self.items)
                    self._axis_y_held = True
                elif abs(event.value) < 0.25:
                    self._axis_y_held = False

        # Suporte a Touchscreen
        elif event.type == pygame.FINGERDOWN:
            vx = event.x * SCREEN_WIDTH
            vy = event.y * SCREEN_HEIGHT
            if self.touch_toggle_rect.collidepoint(vx, vy):
                self.cycle_touch_mode()
                return True
            for rect, idx in self.button_rects:
                if rect.collidepoint(vx, vy):
                    self.selected_index = idx
                    action_key, _, _ = self.items[idx]
                    self.waiting_for_key_action = action_key
                    return True
            close_btn = pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 90, 260, 36)
            if close_btn.collidepoint(vx, vy):
                self.close()
                return True
            reset_btn = pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 135, 260, 32)
            if reset_btn.collidepoint(vx, vy):
                self.reset_to_defaults()
                return True

        # Navegação no menu por teclado
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_c):
                self.close()
                return True
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
                return True
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                action_key, _, _ = self.items[self.selected_index]
                self.waiting_for_key_action = action_key
                return True
            elif event.key == pygame.K_r:
                self.reset_to_defaults()
                return True
            elif event.key == pygame.K_t:
                self.cycle_touch_mode()
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.touch_toggle_rect.collidepoint(mx, my):
                self.cycle_touch_mode()
                return True
            for rect, idx in self.button_rects:
                if rect.collidepoint(mx, my):
                    self.selected_index = idx
                    action_key, _, _ = self.items[idx]
                    self.waiting_for_key_action = action_key
                    return True

            # Botão Fechar / Voltar
            close_btn = pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 90, 260, 36)
            if close_btn.collidepoint(mx, my):
                self.close()
                return True

            # Botão Restaurar Padrões
            reset_btn = pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 135, 260, 32)
            if reset_btn.collidepoint(mx, my):
                self.reset_to_defaults()
                return True

        return True

    def update(self, dt: float):
        if self.is_open:
            self.blink_timer += dt

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        if not self.is_open:
            return

        # 1. Overlay escuro de fundo com desfoque/transparência
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 12, 10, 220))
        surface.blit(overlay, (0, 0))

        # 2. Painel Central Estilizado
        panel_w, panel_h = 920, 580
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 10
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        pygame.draw.rect(surface, (22, 28, 25), panel_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_GOLD, panel_rect, 2, border_radius=12)
        pygame.draw.rect(surface, (50, 65, 58), panel_rect.inflate(-8, -8), 1, border_radius=8)

        # 3. Título do Menu
        title_surf = font_large.render("CONFIGURAÇÃO DE CONTROLES", True, COLOR_GOLD)
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2, panel_y + 24))

        sub_surf = font_small.render("Clique em uma ação ou use as setas + ENTER para remapear a tecla", True, (180, 190, 185))
        surface.blit(sub_surf, (panel_rect.centerx - sub_surf.get_width() // 2, panel_y + 68))

        # 4. Duas Colunas: Vermelho à Esquerda e Azul à Direita
        col_w = 410
        col_left_x = panel_x + 35
        col_right_x = panel_x + panel_w - col_w - 35
        start_y = panel_y + 110
        row_h = 44

        # Cabeçalhos das Colunas
        h1 = font_mid.render("KENSHIN (VERMELHO)", True, COLOR_RED_AURA)
        h2 = font_mid.render("MUSASHI (AZUL)", True, COLOR_BLUE_AURA)
        surface.blit(h1, (col_left_x + 10, start_y - 28))
        surface.blit(h2, (col_right_x + 10, start_y - 28))

        self.button_rects.clear()

        for idx, (action_key, label, faction) in enumerate(self.items):
            is_red = (faction == "red")
            item_col_x = col_left_x if is_red else col_right_x
            row_index = idx if is_red else (idx - 6)
            cur_y = start_y + row_index * row_h

            btn_rect = pygame.Rect(item_col_x, cur_y, col_w, 36)
            self.button_rects.append((btn_rect, idx))

            is_selected = (self.selected_index == idx)
            is_waiting = (self.waiting_for_key_action == action_key)

            # Fundo do Botão
            if is_waiting:
                # Efeito piscante dourado quando está aguardando nova tecla
                bg_color = (70, 60, 20) if (int(self.blink_timer * 4) % 2 == 0) else (45, 40, 15)
                border_color = COLOR_GOLD
            elif is_selected:
                bg_color = (38, 48, 42)
                border_color = COLOR_WHITE
            else:
                bg_color = (28, 34, 30)
                border_color = (48, 60, 52)

            pygame.draw.rect(surface, bg_color, btn_rect, border_radius=6)
            pygame.draw.rect(surface, border_color, btn_rect, 1 if not is_selected else 2, border_radius=6)

            # Texto da Ação
            txt_color = COLOR_WHITE if not is_waiting else COLOR_GOLD
            action_surf = font_small.render(label, True, txt_color)
            surface.blit(action_surf, (btn_rect.x + 12, btn_rect.y + 9))

            # Tecla Atual
            if is_waiting:
                key_text = "<PRESSIONE UMA TECLA>"
                key_color = COLOR_GOLD
            else:
                key_code = self.controls.get(action_key, pygame.K_UNKNOWN)
                key_text = f"[ {format_key_name(key_code)} ]"
                key_color = (255, 215, 120) if is_selected else (200, 210, 205)

            val_surf = font_small.render(key_text, True, key_color)
            surface.blit(val_surf, (btn_rect.right - val_surf.get_width() - 12, btn_rect.y + 9))

        # 5. Status de Gamepads e Controles Touch
        from src.input.controller_manager import get_controller_manager
        ctrl_mgr = get_controller_manager()
        badge_p1 = ctrl_mgr.get_badge_text(0) or "Nenhum detectado (Teclado)"
        badge_p2 = ctrl_mgr.get_badge_text(1) or "Nenhum detectado"

        status_text = f"P1: {badge_p1}   |   P2: {badge_p2}"
        status_surf = font_small.render(status_text, True, (190, 220, 210))
        surface.blit(status_surf, (panel_rect.centerx - status_surf.get_width() // 2, panel_y + panel_h - 165))

        # Botão Alternador de Controles Touch
        touch_mode_str = "AUTOMÁTICO"
        if self.touch_controls:
            mode = getattr(self.touch_controls, "mode", "auto")
            if mode == "always":
                touch_mode_str = "SEMPRE ATIVO"
            elif mode == "off":
                touch_mode_str = "DESATIVADO"

        self.touch_toggle_rect = pygame.Rect(panel_rect.centerx - 175, panel_y + panel_h - 138, 350, 28)
        pygame.draw.rect(surface, (28, 36, 32), self.touch_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.touch_toggle_rect, 1, border_radius=6)
        touch_lbl = font_small.render(f"Controles Touch: [ {touch_mode_str} ] (Clique ou T)", True, COLOR_GOLD)
        surface.blit(touch_lbl, (self.touch_toggle_rect.centerx - touch_lbl.get_width() // 2, self.touch_toggle_rect.y + 6))

        # 6. Botões de Ação no Rodapé do Painel
        # Botão Restaurar Padrões
        reset_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, panel_y + panel_h - 100, 260, 30)
        pygame.draw.rect(surface, (32, 38, 34), reset_rect, border_radius=6)
        pygame.draw.rect(surface, (70, 85, 75), reset_rect, 1, border_radius=6)
        rst_surf = font_small.render("[R] Restaurar Padrões", True, (220, 210, 160))
        surface.blit(rst_surf, (reset_rect.centerx - rst_surf.get_width() // 2, reset_rect.y + 6))

        # Botão Fechar / Voltar
        close_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, panel_y + panel_h - 60, 260, 36)
        pygame.draw.rect(surface, (45, 62, 52), close_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, close_rect, 2, border_radius=6)
        cls_surf = font_mid.render("VOLTAR AO JOGO (ESC / ○ / Options)", True, COLOR_GOLD)
        surface.blit(cls_surf, (close_rect.centerx - cls_surf.get_width() // 2, close_rect.y + 8))
