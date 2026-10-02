"""
Tela e menu interativo de Configuração de Controles (Settings).
Permite visualizar e remapear teclas para o Samurai Vermelho e Azul tanto por teclado quanto por mouse.
"""
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_RED_AURA, COLOR_BLUE_AURA,
    DEFAULT_CONTROLS
)
from src.i18n import t
from src.ui.character_select import draw_scroll_frame, draw_brush_divider

def format_key_name(key_code: int) -> str:
    """Retorna uma representação amigável e legível para a tecla."""
    name_map = {
        pygame.K_UP: t("key_arrow_up"),
        pygame.K_DOWN: t("key_arrow_down"),
        pygame.K_LEFT: t("key_arrow_left"),
        pygame.K_RIGHT: t("key_arrow_right"),
        pygame.K_SPACE: t("key_space"),
        pygame.K_RETURN: t("key_enter"),
        pygame.K_LSHIFT: t("key_lshift"),
        pygame.K_RSHIFT: t("key_rshift"),
        pygame.K_LCTRL: t("key_lctrl"),
        pygame.K_RCTRL: t("key_rctrl"),
        pygame.K_TAB: "TAB",
        pygame.K_ESCAPE: "ESC",
    }
    if key_code in name_map:
        return name_map[key_code]
    key_str = pygame.key.name(key_code)
    return key_str.upper()

class SettingsMenu:
    def __init__(self, controls: dict, touch_controls=None, ai_difficulty: str = "normal"):
        self.controls = controls
        self.touch_controls = touch_controls
        self.ai_difficulty = ai_difficulty if ai_difficulty in ("easy", "normal", "hard") else "normal"
        self.is_open = False
        self.waiting_for_key_action = None  # Nome da ação sendo remapeada (ex: "P1_ATTACK")
        self.selected_index = 0
        self.blink_timer = 0.0
        self._axis_y_held = False
        self._axis_x_held = False

        # Definição dos itens remapeáveis (7 ações por jogador)
        self.items = [
            # Jogador 1 (Player 1)
            ("P1_UP", "Mover Cima", "red"),
            ("P1_DOWN", "Mover Baixo", "red"),
            ("P1_LEFT", "Mover Esquerda", "red"),
            ("P1_RIGHT", "Mover Direita", "red"),
            ("P1_ATTACK", "Ataque Principal", "red"),
            ("P1_SECONDARY", "Ação Secundária / Especial", "red"),
            ("P1_DASH", "Esquiva (Roll / Dash)", "red"),

            # Jogador 2 (Player 2)
            ("P2_UP", "Mover Cima", "blue"),
            ("P2_DOWN", "Mover Baixo", "blue"),
            ("P2_LEFT", "Mover Esquerda", "blue"),
            ("P2_RIGHT", "Mover Direita", "blue"),
            ("P2_ATTACK", "Ataque Principal", "blue"),
            ("P2_SECONDARY", "Ação Secundária / Especial", "blue"),
            ("P2_DASH", "Esquiva (Roll / Dash)", "blue"),
        ]

        # Áreas clicáveis na tela (atualizadas durante o render)
        self.button_rects: list[tuple[pygame.Rect, int]] = []
        self.touch_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.difficulty_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.sfx_minus_rect = pygame.Rect(0, 0, 0, 0)
        self.sfx_plus_rect = pygame.Rect(0, 0, 0, 0)
        self.sfx_bar_rect = pygame.Rect(0, 0, 0, 0)
        self.bgm_minus_rect = pygame.Rect(0, 0, 0, 0)
        self.bgm_plus_rect = pygame.Rect(0, 0, 0, 0)
        self.bgm_bar_rect = pygame.Rect(0, 0, 0, 0)

    def adjust_sfx_volume(self, delta: float):
        """Ajusta o volume dos efeitos sonoros em passos discretos."""
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent
        mgr = SoundManager.get_instance()
        new_vol = round(max(0.0, min(1.0, mgr.sfx_volume + delta)), 2)
        mgr.set_sfx_volume(new_vol)
        mgr.play(SoundEvent.MENU_SELECT)
        self.save_settings()

    def adjust_bgm_volume(self, delta: float):
        """Ajusta o volume da trilha musical de fundo em passos discretos."""
        from src.audio.sound_manager import SoundManager
        mgr = SoundManager.get_instance()
        new_vol = round(max(0.0, min(1.0, mgr.bgm_volume + delta)), 2)
        mgr.set_bgm_volume(new_vol)
        self.save_settings()

    def cycle_ai_difficulty(self):
        """Alterna a dificuldade da IA entre Fácil, Normal e Difícil."""
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent
        order = ["easy", "normal", "hard"]
        cur_idx = order.index(self.ai_difficulty) if self.ai_difficulty in order else 1
        self.ai_difficulty = order[(cur_idx + 1) % len(order)]
        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
        self.save_settings()

    def save_settings(self):
        """Salva as configurações atuais no arquivo controls_config.json."""
        from src.input.controller_manager import get_controller_manager
        from src.input.controls_storage import save_controls_config
        from src.audio.sound_manager import SoundManager
        ctrl_mgr = get_controller_manager()
        t_mode = getattr(self.touch_controls, "mode", "auto") if self.touch_controls else "auto"
        mgr = SoundManager.get_instance()
        self.controls["audio"] = {
            "master": mgr.master_volume,
            "sfx": mgr.sfx_volume,
            "bgm": mgr.bgm_volume
        }
        save_controls_config(self.controls, ctrl_mgr, t_mode, ai_difficulty=self.ai_difficulty)

    def open(self):
        self.is_open = True
        self.waiting_for_key_action = None

    @staticmethod
    def _fit_text(font, text: str, color, max_w: int) -> pygame.Surface:
        """Renderiza o texto, encurtando com '...' se exceder a largura máxima."""
        surf = font.render(text, True, color)
        if surf.get_width() <= max_w:
            return surf
        while len(text) > 1 and font.size(text + "...")[0] > max_w:
            text = text[:-1]
        return font.render(text.rstrip() + "...", True, color)

    def close(self):
        self.is_open = False
        self.waiting_for_key_action = None
        self.save_settings()

    def reset_to_defaults(self):
        """Restaura os controles para o padrão de fábrica e salva."""
        for k, v in DEFAULT_CONTROLS.items():
            self.controls[k] = v
        from src.input.controller_manager import get_controller_manager
        ctrl_mgr = get_controller_manager()
        for p_idx in (0, 1):
            ctrl = ctrl_mgr.get_controller_for_player(p_idx)
            if ctrl:
                ctrl.custom_mappings.clear()
        self.save_settings()

    def cycle_touch_mode(self):
        if self.touch_controls:
            from src.input.touch_controls import TOUCH_MODE_AUTO, TOUCH_MODE_ALWAYS, TOUCH_MODE_OFF
            order = [TOUCH_MODE_AUTO, TOUCH_MODE_ALWAYS, TOUCH_MODE_OFF]
            cur_idx = order.index(self.touch_controls.mode) if self.touch_controls.mode in order else 0
            self.touch_controls.mode = order[(cur_idx + 1) % len(order)]
            self.save_settings()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Processa eventos enquanto o menu de configurações está aberto.
        Retorna True se o evento foi consumido pelo menu.
        """
        if not self.is_open:
            return False

        from src.input.controller_manager import get_controller_manager, get_dpad_motion_from_event
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
                    self.save_settings()
                return True
            elif event.type == pygame.JOYBUTTONDOWN:
                # Se for Círculo (botão 1) e estiver esperando para cancelar
                if event.button == 1 and not ("DASH" in self.waiting_for_key_action or "CANCEL" in self.waiting_for_key_action):
                    self.waiting_for_key_action = None
                    return True
                # Remapear ação no controle correspondente (P1 ou P2)
                act_name = "attack" if "ATTACK" in self.waiting_for_key_action else (
                    "dash" if "DASH" in self.waiting_for_key_action else (
                        "secondary" if ("SECONDARY" in self.waiting_for_key_action or "PARRY" in self.waiting_for_key_action) else None
                    )
                )
                p_idx = 1 if "P2" in self.waiting_for_key_action else 0
                if act_name:
                    ctrl_mgr.remap_action(p_idx, act_name, event.button)
                    self.save_settings()
                self.waiting_for_key_action = None
                return True
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                # Cancelar espera ao clicar fora
                self.waiting_for_key_action = None
                return True
            return True

        # Suporte a Gamepad no menu de configurações
        if event.type == pygame.JOYBUTTONDOWN:
            # D-Pad botões virtuais (11=Up, 12=Down, 13=Left, 14=Right)
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                dx, dy = d_dir
                if dy != 0:
                    self.selected_index = (self.selected_index + dy) % len(self.items)
                elif dx != 0:
                    # Alternar entre coluna da esquerda (P1) e da direita (P2)
                    self.selected_index = (self.selected_index + 7) % len(self.items)
                return True

            if ctrl_mgr.is_event_menu_confirm(event) or event.button == 0:
                action_key, _, _ = self.items[self.selected_index]
                self.waiting_for_key_action = action_key
                return True
            elif ctrl_mgr.is_event_menu_cancel(event) or ctrl_mgr.is_event_menu_pause(event) or event.button in (1, 6):
                self.close()
                return True
            elif event.button == 4:
                self.reset_to_defaults()
                return True
            elif event.button == 3:
                self.cycle_touch_mode()
                return True

        elif event.type == pygame.JOYHATMOTION:
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                dx, dy = d_dir
                if dy != 0:
                    self.selected_index = (self.selected_index + dy) % len(self.items)
                elif dx != 0:
                    self.selected_index = (self.selected_index + 6) % len(self.items)

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
            elif event.axis == 0:
                if event.value > 0.65 and not self._axis_x_held:
                    self.selected_index = (self.selected_index + 7) % len(self.items)
                    self._axis_x_held = True
                elif event.value < -0.65 and not self._axis_x_held:
                    self.selected_index = (self.selected_index + 7) % len(self.items)
                    self._axis_x_held = True
                elif abs(event.value) < 0.25:
                    self._axis_x_held = False

        # Suporte a Touchscreen
        elif event.type == pygame.FINGERDOWN:
            vx = event.x * SCREEN_WIDTH
            vy = event.y * SCREEN_HEIGHT
            if self.sfx_minus_rect.collidepoint(vx, vy):
                self.adjust_sfx_volume(-0.1)
                return True
            elif self.sfx_plus_rect.collidepoint(vx, vy):
                self.adjust_sfx_volume(+0.1)
                return True
            elif self.sfx_bar_rect.collidepoint(vx, vy):
                pct = max(0.0, min(1.0, (vx - self.sfx_bar_rect.x) / max(1, self.sfx_bar_rect.width)))
                from src.audio.sound_manager import SoundManager
                from src.audio.sound_events import SoundEvent
                mgr = SoundManager.get_instance()
                mgr.set_sfx_volume(round(pct, 2))
                mgr.play(SoundEvent.MENU_SELECT)
                self.save_settings()
                return True
            elif self.bgm_minus_rect.collidepoint(vx, vy):
                self.adjust_bgm_volume(-0.1)
                return True
            elif self.bgm_plus_rect.collidepoint(vx, vy):
                self.adjust_bgm_volume(+0.1)
                return True
            elif self.bgm_bar_rect.collidepoint(vx, vy):
                pct = max(0.0, min(1.0, (vx - self.bgm_bar_rect.x) / max(1, self.bgm_bar_rect.width)))
                from src.audio.sound_manager import SoundManager
                mgr = SoundManager.get_instance()
                mgr.set_bgm_volume(round(pct, 2))
                self.save_settings()
                return True
            elif self.touch_toggle_rect.collidepoint(vx, vy):
                self.cycle_touch_mode()
                return True
            elif self.difficulty_toggle_rect.collidepoint(vx, vy):
                self.cycle_ai_difficulty()
                return True
            for rect, idx in self.button_rects:
                if rect.collidepoint(vx, vy):
                    self.selected_index = idx
                    action_key, _, _ = self.items[idx]
                    self.waiting_for_key_action = action_key
                    return True
            close_btn = pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 65, 260, 36)
            if close_btn.collidepoint(vx, vy):
                self.close()
                return True
            reset_btn = pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 105, 260, 32)
            if reset_btn.collidepoint(vx, vy):
                self.reset_to_defaults()
                return True

        # Navegação no menu por teclado
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_c):
                self.close()
                return True
            elif event.key == pygame.K_g:
                self.cycle_ai_difficulty()
                return True
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                self.adjust_sfx_volume(-0.1)
                return True
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                self.adjust_sfx_volume(+0.1)
                return True
            elif event.key == pygame.K_LEFTBRACKET:
                self.adjust_bgm_volume(-0.1)
                return True
            elif event.key == pygame.K_RIGHTBRACKET:
                self.adjust_bgm_volume(+0.1)
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
            elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                self.reset_to_defaults()
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.sfx_minus_rect.collidepoint(mx, my):
                self.adjust_sfx_volume(-0.1)
                return True
            elif self.sfx_plus_rect.collidepoint(mx, my):
                self.adjust_sfx_volume(+0.1)
                return True
            elif self.sfx_bar_rect.collidepoint(mx, my):
                pct = max(0.0, min(1.0, (mx - self.sfx_bar_rect.x) / max(1, self.sfx_bar_rect.width)))
                from src.audio.sound_manager import SoundManager
                from src.audio.sound_events import SoundEvent
                mgr = SoundManager.get_instance()
                mgr.set_sfx_volume(round(pct, 2))
                mgr.play(SoundEvent.MENU_SELECT)
                self.save_settings()
                return True
            elif self.bgm_minus_rect.collidepoint(mx, my):
                self.adjust_bgm_volume(-0.1)
                return True
            elif self.bgm_plus_rect.collidepoint(mx, my):
                self.adjust_bgm_volume(+0.1)
                return True
            elif self.bgm_bar_rect.collidepoint(mx, my):
                pct = max(0.0, min(1.0, (mx - self.bgm_bar_rect.x) / max(1, self.bgm_bar_rect.width)))
                from src.audio.sound_manager import SoundManager
                mgr = SoundManager.get_instance()
                mgr.set_bgm_volume(round(pct, 2))
                self.save_settings()
                return True
            elif self.touch_toggle_rect.collidepoint(mx, my):
                self.cycle_touch_mode()
                return True
            elif self.difficulty_toggle_rect.collidepoint(mx, my):
                self.cycle_ai_difficulty()
                return True
            for rect, idx in self.button_rects:
                if rect.collidepoint(mx, my):
                    self.selected_index = idx
                    action_key, _, _ = self.items[idx]
                    self.waiting_for_key_action = action_key
                    return True

            # Botão Fechar / Voltar
            close_btn = pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 65, 260, 36)
            if close_btn.collidepoint(mx, my):
                self.close()
                return True

            # Botão Restaurar Padrões
            reset_btn = pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 105, 260, 32)
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

        # 1. Overlay escuro de fundo com desfoque/transparência (suave, tipo nanquim diluído)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 14, 12, 200))  # Softer dark tone
        surface.blit(overlay, (0, 0))

        # 2. Painel Central Estilizado (Pergaminho com moldura dourada elegante)
        panel_w, panel_h = 960, 650
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 10
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # Use parchment color for background
        pygame.draw.rect(surface, (45, 43, 40), panel_rect, border_radius=12)  # Parchment/tan
        pygame.draw.rect(surface, (212, 175, 55), panel_rect, 2, border_radius=12)  # Soft gold border
        pygame.draw.rect(surface, (65, 60, 52), panel_rect.inflate(-8, -8), 1, border_radius=8)  # Inner line

        # 3. Título do Menu
        title_surf = font_large.render(t("settings_title"), True, (212, 175, 55))  # Soft gold
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2, panel_y + 14))

        sub_surf = font_small.render(t("settings_subtitle"), True, (180, 175, 165))
        surface.blit(sub_surf, (panel_rect.centerx - sub_surf.get_width() // 2, panel_y + 62))

        # 4. Duas Colunas: Vermelho à Esquerda e Azul à Direita
        col_w = 430
        col_left_x = panel_x + 30
        col_right_x = panel_x + panel_w - col_w - 30
        start_y = panel_y + 118
        row_h = 40  # Increased row height for better spacing

        # Cabeçalhos das Colunas
        h1 = font_mid.render(t("player_1_label"), True, COLOR_RED_AURA)
        h2 = font_mid.render(t("player_2_label"), True, COLOR_BLUE_AURA)
        surface.blit(h1, (col_left_x + 10, start_y - 28))
        surface.blit(h2, (col_right_x + 10, start_y - 28))

        self.button_rects.clear()

        from src.input.controller_manager import get_controller_manager
        from src.ui.svg_icon_renderer import get_button_icon_surface
        ctrl_mgr = get_controller_manager()

        for idx, (action_key, label, faction) in enumerate(self.items):
            is_red = (faction == "red")

            item_col_x = col_left_x if is_red else col_right_x
            row_index = idx if is_red else (idx - 7)
            cur_y = start_y + row_index * row_h

            btn_rect = pygame.Rect(item_col_x, cur_y, col_w, 32)
            self.button_rects.append((btn_rect, idx))

            is_selected = (self.selected_index == idx)
            is_waiting = (self.waiting_for_key_action == action_key)

            # Fundo do Botão (parchment palette)
            if is_waiting:
                bg_color = (80, 72, 55) if (int(self.blink_timer * 4) % 2 == 0) else (55, 50, 38)  # Tan/parchment
                border_color = (212, 175, 55)  # Gold
            elif is_selected:
                bg_color = (55, 50, 42)  # Parchment
                border_color = (220, 200, 180)  # Light parchment highlight
            else:
                bg_color = (40, 37, 33)  # Darker parchment
                border_color = (70, 63, 55)  # Subtle border

            pygame.draw.rect(surface, bg_color, btn_rect, border_radius=6)
            pygame.draw.rect(surface, border_color, btn_rect, 1 if not is_selected else 2, border_radius=6)

            # Texto da Ação (traduzido; truncado para não invadir a área da tecla)
            txt_color = (225, 220, 210) if not is_waiting else (212, 175, 55)
            label = t("settings_action_" + action_key[3:].lower())
            left_max_w = 150
            action_surf = self._fit_text(font_small, label, txt_color, left_max_w)
            surface.blit(action_surf, (btn_rect.x + 10, btn_rect.y + 8))

            # Tecla e Botão Atual
            if is_waiting:
                val_surf = self._fit_text(font_small, t("settings_press_key"), COLOR_GOLD, col_w - left_max_w - 30)
                surface.blit(val_surf, (btn_rect.right - val_surf.get_width() - 10, btn_rect.y + 7))
            else:
                key_code = self.controls.get(action_key, pygame.K_UNKNOWN)
                key_str = format_key_name(key_code)

                p_idx = 0 if is_red else 1
                ctrl = ctrl_mgr.get_controller_for_player(p_idx)
                act_suffix = "attack" if "ATTACK" in action_key else (
                    "dash" if "DASH" in action_key else (
                        "secondary" if ("SECONDARY" in action_key or "PARRY" in action_key) else None
                    )
                )

                svg_icon_name = None
                btn_label = ""

                # Botões de gamepad só aparecem com um controle realmente conectado
                if ctrl:
                    if action_key.endswith(("_UP", "_DOWN", "_LEFT", "_RIGHT")):
                        svg_icon_name = "dpad"
                        btn_label = t("settings_dpad_" + action_key.rsplit("_", 1)[1].lower())
                    elif act_suffix:
                        if ctrl.is_playstation:
                            svg_icon_name = ctrl.get_button_svg_icon(act_suffix)
                        btn_label = ctrl.get_mapped_button_name(act_suffix)

                key_color = (212, 175, 55) if is_selected else (140, 130, 120)  # Gold or muted tan

                cur_right_x = btn_rect.right - 10
                if svg_icon_name:
                    icon_surf = get_button_icon_surface(svg_icon_name, 18, 18)
                    cur_right_x -= 20
                    surface.blit(icon_surf, (cur_right_x, btn_rect.y + 7))

                key_surf = self._fit_text(font_small, f"[{key_str}]", key_color, 130)
                if btn_label:
                    room = col_w - left_max_w - 30 - key_surf.get_width() - (20 if svg_icon_name else 0)
                    label_surf = self._fit_text(font_small, f"[{btn_label}]", (160, 205, 185), max(room, 40))
                    cur_right_x -= (label_surf.get_width() + 5)
                    surface.blit(label_surf, (cur_right_x, btn_rect.y + 7))

                cur_right_x -= (key_surf.get_width() + 5)
                surface.blit(key_surf, (cur_right_x, btn_rect.y + 7))

        # 5. Painel de Volumes (SFX e BGM)
        from src.audio.sound_manager import SoundManager
        sound_mgr = SoundManager.get_instance()
        audio_y = start_y + 7 * row_h + 10

        # Divisor sutil
        pygame.draw.line(surface, (45, 60, 52), (col_left_x, audio_y - 6), (col_right_x + col_w, audio_y - 6), 1)

        # Coluna SFX
        sfx_pct = int(sound_mgr.sfx_volume * 100)
        sfx_lbl = self._fit_text(font_small, t("sfx_volume_label").format(sfx_pct=sfx_pct), (210, 230, 220), 190)
        surface.blit(sfx_lbl, (col_left_x + 5, audio_y))

        self.sfx_minus_rect = pygame.Rect(col_left_x + 200, audio_y - 2, 28, 24)
        self.sfx_bar_rect = pygame.Rect(col_left_x + 235, audio_y + 3, 140, 14)
        self.sfx_plus_rect = pygame.Rect(col_left_x + 382, audio_y - 2, 28, 24)

        for btn_r, symb in ((self.sfx_minus_rect, "-"), (self.sfx_plus_rect, "+")):
            pygame.draw.rect(surface, (35, 45, 40), btn_r, border_radius=4)
            pygame.draw.rect(surface, COLOR_GOLD, btn_r, 1, border_radius=4)
            t_s = font_small.render(symb, True, COLOR_GOLD)
            surface.blit(t_s, (btn_r.centerx - t_s.get_width() // 2, btn_r.centery - t_s.get_height() // 2))

        pygame.draw.rect(surface, (20, 26, 24), self.sfx_bar_rect, border_radius=3)
        fill_w = int(self.sfx_bar_rect.width * sound_mgr.sfx_volume)
        if fill_w > 0:
            fill_r = pygame.Rect(self.sfx_bar_rect.x, self.sfx_bar_rect.y, fill_w, self.sfx_bar_rect.height)
            pygame.draw.rect(surface, (180, 140, 60), fill_r, border_radius=3)
        pygame.draw.rect(surface, (60, 75, 68), self.sfx_bar_rect, 1, border_radius=3)

        # Coluna BGM
        bgm_pct = int(sound_mgr.bgm_volume * 100)
        bgm_lbl = self._fit_text(font_small, t("bgm_volume_label").format(bgm_pct=bgm_pct), (210, 230, 220), 190)
        surface.blit(bgm_lbl, (col_right_x + 5, audio_y))

        self.bgm_minus_rect = pygame.Rect(col_right_x + 200, audio_y - 2, 28, 24)
        self.bgm_bar_rect = pygame.Rect(col_right_x + 235, audio_y + 3, 140, 14)
        self.bgm_plus_rect = pygame.Rect(col_right_x + 382, audio_y - 2, 28, 24)

        for btn_r, symb in ((self.bgm_minus_rect, "-"), (self.bgm_plus_rect, "+")):
            pygame.draw.rect(surface, (35, 45, 40), btn_r, border_radius=4)
            pygame.draw.rect(surface, COLOR_GOLD, btn_r, 1, border_radius=4)
            t_s = font_small.render(symb, True, COLOR_GOLD)
            surface.blit(t_s, (btn_r.centerx - t_s.get_width() // 2, btn_r.centery - t_s.get_height() // 2))

        pygame.draw.rect(surface, (20, 26, 24), self.bgm_bar_rect, border_radius=3)
        fill_w = int(self.bgm_bar_rect.width * sound_mgr.bgm_volume)
        if fill_w > 0:
            fill_r = pygame.Rect(self.bgm_bar_rect.x, self.bgm_bar_rect.y, fill_w, self.bgm_bar_rect.height)
            pygame.draw.rect(surface, (90, 140, 110), fill_r, border_radius=3)
        pygame.draw.rect(surface, (60, 75, 68), self.bgm_bar_rect, 1, border_radius=3)

        # 6. Status de Gamepads e Controles Touch
        badge_p1 = ctrl_mgr.get_badge_text(0) or t("gamepad_not_detected_p1")
        badge_p2 = ctrl_mgr.get_badge_text(1) or t("gamepad_not_detected_p2")

        status_text = f"P1: {badge_p1}   |   P2: {badge_p2}"
        status_surf = self._fit_text(font_small, status_text, (170, 200, 190), 860)
        surface.blit(status_surf, (panel_rect.centerx - status_surf.get_width() // 2, audio_y + 36))

        # Botão Alternador de Controles Touch
        touch_mode_str = t("touch_mode_auto")
        if self.touch_controls:
            mode = getattr(self.touch_controls, "mode", "auto")
            if mode == "always":
                touch_mode_str = t("touch_mode_always_on")
            elif mode == "off":
                touch_mode_str = t("touch_mode_disabled")

        self.touch_toggle_rect = pygame.Rect(panel_rect.centerx - 175, audio_y + 60, 350, 26)
        pygame.draw.rect(surface, (28, 36, 32), self.touch_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.touch_toggle_rect, 1, border_radius=6)
        touch_lbl = self._fit_text(font_small, t("touch_controls_label").format(touch_mode_str=touch_mode_str), COLOR_GOLD, 336)
        surface.blit(touch_lbl, (self.touch_toggle_rect.centerx - touch_lbl.get_width() // 2, self.touch_toggle_rect.y + 5))

        # Botão Alternador de Dificuldade da IA
        diff_names = {
            "easy": t("difficulty_easy"),
            "normal": t("difficulty_normal"),
            "hard": t("difficulty_hard")
        }
        diff_colors = {"easy": (110, 225, 140), "normal": COLOR_GOLD, "hard": (245, 95, 85)}
        d_name = diff_names.get(self.ai_difficulty, t("difficulty_normal"))
        d_col = diff_colors.get(self.ai_difficulty, COLOR_GOLD)

        self.difficulty_toggle_rect = pygame.Rect(panel_rect.centerx - 195, audio_y + 90, 390, 26)
        pygame.draw.rect(surface, (28, 36, 32), self.difficulty_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, d_col, self.difficulty_toggle_rect, 1, border_radius=6)
        diff_lbl = self._fit_text(font_small, t("ai_difficulty_label").format(d_name=d_name), d_col, 376)
        surface.blit(diff_lbl, (self.difficulty_toggle_rect.centerx - diff_lbl.get_width() // 2, self.difficulty_toggle_rect.y + 5))

        # 7. Botões de Ação no Rodapé do Painel
        # Botão Restaurar Padrões
        reset_rect = pygame.Rect(panel_rect.centerx - 130, panel_y + panel_h - 78, 260, 28)
        pygame.draw.rect(surface, (32, 38, 34), reset_rect, border_radius=6)
        pygame.draw.rect(surface, (70, 85, 75), reset_rect, 1, border_radius=6)
        rst_surf = self._fit_text(font_small, t("reset_defaults_hint"), (220, 210, 160), 246)
        surface.blit(rst_surf, (reset_rect.centerx - rst_surf.get_width() // 2, reset_rect.y + 5))

        # Botão Fechar / Voltar
        close_rect = pygame.Rect(panel_rect.centerx - 140, panel_y + panel_h - 44, 280, 34)
        pygame.draw.rect(surface, (45, 62, 52), close_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, close_rect, 2, border_radius=6)
        cls_surf = self._fit_text(font_mid, t("settings_return_button"), COLOR_GOLD, 266)
        surface.blit(cls_surf, (close_rect.centerx - cls_surf.get_width() // 2, close_rect.y + 7))
