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
        save_controls_config(self.controls, ctrl_mgr, t_mode)

    def open(self):
        self.is_open = True
        self.waiting_for_key_action = None

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

        # 1. Overlay escuro de fundo com desfoque/transparência
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 12, 10, 220))
        surface.blit(overlay, (0, 0))

        # 2. Painel Central Estilizado
        panel_w, panel_h = 940, 630
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 5
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        pygame.draw.rect(surface, (22, 28, 25), panel_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_GOLD, panel_rect, 2, border_radius=12)
        pygame.draw.rect(surface, (50, 65, 58), panel_rect.inflate(-8, -8), 1, border_radius=8)

        # 3. Título do Menu
        title_surf = font_large.render("CONFIGURAÇÃO DE CONTROLES & ÁUDIO", True, COLOR_GOLD)
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2, panel_y + 18))

        sub_surf = font_small.render("Clique em uma ação para remapear teclas | Ajuste os volumes com [ - / + ] e [ [ / ] ]", True, (180, 190, 185))
        surface.blit(sub_surf, (panel_rect.centerx - sub_surf.get_width() // 2, panel_y + 54))

        # 4. Duas Colunas: Vermelho à Esquerda e Azul à Direita
        col_w = 420
        col_left_x = panel_x + 35
        col_right_x = panel_x + panel_w - col_w - 35
        start_y = panel_y + 88
        row_h = 38

        # Cabeçalhos das Colunas
        h1 = font_mid.render("PLAYER 1 (VERMELHO)", True, COLOR_RED_AURA)
        h2 = font_mid.render("PLAYER 2 (AZUL)", True, COLOR_BLUE_AURA)
        surface.blit(h1, (col_left_x + 10, start_y - 24))
        surface.blit(h2, (col_right_x + 10, start_y - 24))

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

            # Fundo do Botão
            if is_waiting:
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
            surface.blit(action_surf, (btn_rect.x + 10, btn_rect.y + 7))

            # Tecla e Botão Atual
            if is_waiting:
                key_text = "<PRESSIONE TECLA OU BOTÃO>"
                val_surf = font_small.render(key_text, True, COLOR_GOLD)
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

                dpad_names = {
                    "P1_UP": "D-PAD CIMA",
                    "P1_DOWN": "D-PAD BAIXO",
                    "P1_LEFT": "D-PAD ESQ",
                    "P1_RIGHT": "D-PAD DIR",
                    "P2_UP": "D-PAD CIMA",
                    "P2_DOWN": "D-PAD BAIXO",
                    "P2_LEFT": "D-PAD ESQ",
                    "P2_RIGHT": "D-PAD DIR",
                }

                svg_icon_name = None
                btn_label = ""

                if action_key in dpad_names:
                    svg_icon_name = "dpad"
                    btn_label = dpad_names[action_key]
                elif ctrl:
                    if act_suffix:
                        svg_icon_name = ctrl.get_button_svg_icon(act_suffix) if ctrl.is_playstation else None
                        btn_label = ctrl.get_mapped_button_name(act_suffix)
                else:
                    if act_suffix == "attack":
                        svg_icon_name = "square"
                        btn_label = "▢ / R1"
                    elif act_suffix == "secondary":
                        svg_icon_name = "triangle"
                        btn_label = "✕ / △"
                    elif act_suffix == "dash":
                        svg_icon_name = "circle"
                        btn_label = "○ / L1"

                key_color = (255, 215, 120) if is_selected else (200, 210, 205)

                cur_right_x = btn_rect.right - 10
                if svg_icon_name:
                    icon_surf = get_button_icon_surface(svg_icon_name, 18, 18)
                    cur_right_x -= 20
                    surface.blit(icon_surf, (cur_right_x, btn_rect.y + 7))

                if btn_label:
                    label_surf = font_small.render(f"[{btn_label}]", True, (160, 205, 185))
                    cur_right_x -= (label_surf.get_width() + 5)
                    surface.blit(label_surf, (cur_right_x, btn_rect.y + 7))

                key_surf = font_small.render(f"[{key_str}]", True, key_color)
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
        sfx_lbl = font_small.render(f"Efeitos Sonoros (SFX): {sfx_pct}%", True, (210, 230, 220))
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
        bgm_lbl = font_small.render(f"Música & Ambiência (BGM): {bgm_pct}%", True, (210, 230, 220))
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
        badge_p1 = ctrl_mgr.get_badge_text(0) or "Nenhum detectado (Teclado)"
        badge_p2 = ctrl_mgr.get_badge_text(1) or "Nenhum detectado"

        status_text = f"P1: {badge_p1}   |   P2: {badge_p2}"
        status_surf = font_small.render(status_text, True, (170, 200, 190))
        surface.blit(status_surf, (panel_rect.centerx - status_surf.get_width() // 2, audio_y + 36))

        # Botão Alternador de Controles Touch
        touch_mode_str = "AUTOMÁTICO"
        if self.touch_controls:
            mode = getattr(self.touch_controls, "mode", "auto")
            if mode == "always":
                touch_mode_str = "SEMPRE ATIVO"
            elif mode == "off":
                touch_mode_str = "DESATIVADO"

        self.touch_toggle_rect = pygame.Rect(panel_rect.centerx - 175, audio_y + 60, 350, 26)
        pygame.draw.rect(surface, (28, 36, 32), self.touch_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.touch_toggle_rect, 1, border_radius=6)
        touch_lbl = font_small.render(f"Controles Touch: [ {touch_mode_str} ] (Clique para alternar)", True, COLOR_GOLD)
        surface.blit(touch_lbl, (self.touch_toggle_rect.centerx - touch_lbl.get_width() // 2, self.touch_toggle_rect.y + 5))

        # 7. Botões de Ação no Rodapé do Painel
        # Botão Restaurar Padrões
        reset_rect = pygame.Rect(panel_rect.centerx - 130, panel_y + panel_h - 78, 260, 28)
        pygame.draw.rect(surface, (32, 38, 34), reset_rect, border_radius=6)
        pygame.draw.rect(surface, (70, 85, 75), reset_rect, 1, border_radius=6)
        rst_surf = font_small.render("[BACKSPACE] Restaurar Padrões", True, (220, 210, 160))
        surface.blit(rst_surf, (reset_rect.centerx - rst_surf.get_width() // 2, reset_rect.y + 5))

        # Botão Fechar / Voltar
        close_rect = pygame.Rect(panel_rect.centerx - 140, panel_y + panel_h - 44, 280, 34)
        pygame.draw.rect(surface, (45, 62, 52), close_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, close_rect, 2, border_radius=6)
        cls_surf = font_mid.render("VOLTAR AO JOGO (ESC / ○ / Options)", True, COLOR_GOLD)
        surface.blit(cls_surf, (close_rect.centerx - cls_surf.get_width() // 2, close_rect.y + 7))
