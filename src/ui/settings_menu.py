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
from src.input.touch_editor import TouchControlsEditorScreen
from src.input.device_info import is_mobile_device, get_saved_ui_mode, set_ui_mode

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
        self.p1_controller_box_rect = pygame.Rect(0, 0, 0, 0)
        self.p1_controller_prev_rect = pygame.Rect(0, 0, 0, 0)
        self.p1_controller_next_rect = pygame.Rect(0, 0, 0, 0)
        self.p2_controller_box_rect = pygame.Rect(0, 0, 0, 0)
        self.p2_controller_prev_rect = pygame.Rect(0, 0, 0, 0)
        self.p2_controller_next_rect = pygame.Rect(0, 0, 0, 0)
        self.touch_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.difficulty_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.language_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.quality_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.game_boost_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.sfx_minus_rect = pygame.Rect(0, 0, 0, 0)
        self.sfx_plus_rect = pygame.Rect(0, 0, 0, 0)
        self.sfx_bar_rect = pygame.Rect(0, 0, 0, 0)
        self.bgm_minus_rect = pygame.Rect(0, 0, 0, 0)
        self.bgm_plus_rect = pygame.Rect(0, 0, 0, 0)
        self.bgm_bar_rect = pygame.Rect(0, 0, 0, 0)
        self.touch_editor_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.ui_mode_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.close_rect = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 68, 320, 48)
        self.reset_rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 120, 280, 40)
        self.touch_editor = TouchControlsEditorScreen(self.touch_controls)

    def cycle_p1_controller(self, delta: int = 1):
        """Alterna o controle atribuído ao Jogador 1 entre os dispositivos conectados."""
        from src.input.controller_manager import get_controller_manager
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent
        ctrl_mgr = get_controller_manager()
        ctrl_mgr.cycle_player_controller(0, delta)
        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)

    def cycle_p2_controller(self, delta: int = 1):
        """Alterna o controle atribuído ao Jogador 2 entre os dispositivos conectados."""
        from src.input.controller_manager import get_controller_manager
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent
        ctrl_mgr = get_controller_manager()
        ctrl_mgr.cycle_player_controller(1, delta)
        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)

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

    def cycle_language(self):
        """Alterna a preferência de idioma entre Auto (Sistema), Português e Inglês e salva em settings.json."""
        from src.i18n import (
            get_saved_language_preference, save_language_setting,
            apply_saved_language, LANG_AUTO, LANG_PT, LANG_EN
        )
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent

        cur = get_saved_language_preference()
        order = [LANG_AUTO, LANG_PT, LANG_EN]
        idx = order.index(cur) if cur in order else 0
        next_pref = order[(idx + 1) % len(order)]
        save_language_setting(next_pref)
        apply_saved_language()
        try:
            SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
        except Exception:
            pass

    def cycle_effects_quality(self):
        """Alterna a qualidade dos efeitos (alta/baixa) e grava em settings.json."""
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent
        from src.effects import quality
        quality.set_effects_quality(quality.LOW if quality.is_high() else quality.HIGH)
        quality.save_video_setting(quality.SETTINGS_PATH, "effects_quality", quality.get_effects_quality())
        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)

    def toggle_game_boost(self):
        """Alterna o Modo Game Boost (alto desempenho e economia) e grava em settings.json."""
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent
        from src.effects import quality
        new_state = not quality.is_game_boost_enabled()
        quality.set_game_boost(new_state)
        quality.save_video_setting(quality.SETTINGS_PATH, "game_boost", new_state)
        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)

    def toggle_invert_y(self):
        """Alterna a inversão do eixo vertical Y no analógico."""
        from src.input.controller_manager import get_controller_manager
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent
        ctrl_mgr = get_controller_manager()
        ctrl_mgr.toggle_invert_y()
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
        if hasattr(self, "touch_editor"):
            self.touch_editor.close()

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

    def cycle_ui_mode(self):
        from src.input.device_info import get_saved_ui_mode, set_ui_mode
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent
        order = ["auto", "mobile", "classic"]
        cur = get_saved_ui_mode()
        cur_idx = order.index(cur) if cur in order else 0
        nxt = order[(cur_idx + 1) % len(order)]
        set_ui_mode(nxt)
        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Processa eventos enquanto o menu de configurações está aberto.
        Retorna True se o evento foi consumido pelo menu.
        """
        if not self.is_open:
            return False

        if hasattr(self, "touch_editor") and self.touch_editor.is_open:
            if self.touch_editor.handle_event(event):
                return True
            return True

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
                    ctrl = ctrl_mgr.get_controller_for_player(p_idx)
                    if ctrl:
                        ctrl.set_action_buttons(act_name, [event.button])
                    else:
                        ctrl_mgr.remap_action(p_idx, act_name, event.button, toggle=False)
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
                    try:
                        from src.audio.sound_manager import SoundManager
                        from src.audio.sound_events import SoundEvent
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass
                elif dx != 0:
                    # Alternar entre coluna da esquerda (P1) e da direita (P2)
                    self.selected_index = (self.selected_index + 7) % len(self.items)
                    try:
                        from src.audio.sound_manager import SoundManager
                        from src.audio.sound_events import SoundEvent
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass
                return True

            if event.button == 9: # L1 / LB
                self.cycle_p1_controller(+1)
                return True
            elif event.button == 10: # R1 / RB
                self.cycle_p2_controller(+1)
                return True

            if ctrl_mgr.is_event_menu_confirm(event) or event.button in (0, 2):
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
                self.toggle_invert_y()
                return True

        elif event.type == pygame.JOYHATMOTION:
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                dx, dy = d_dir
                if dy != 0:
                    self.selected_index = (self.selected_index + dy) % len(self.items)
                    try:
                        from src.audio.sound_manager import SoundManager
                        from src.audio.sound_events import SoundEvent
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass
                elif dx != 0:
                    self.selected_index = (self.selected_index + 7) % len(self.items)
                    try:
                        from src.audio.sound_manager import SoundManager
                        from src.audio.sound_events import SoundEvent
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass

        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
                val = -event.value if getattr(ctrl_mgr, "invert_y", False) else event.value
                if val > 0.65 and not self._axis_y_held:
                    self.selected_index = (self.selected_index + 1) % len(self.items)
                    self._axis_y_held = True
                    try:
                        from src.audio.sound_manager import SoundManager
                        from src.audio.sound_events import SoundEvent
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass
                elif val < -0.65 and not self._axis_y_held:
                    self.selected_index = (self.selected_index - 1) % len(self.items)
                    self._axis_y_held = True
                    try:
                        from src.audio.sound_manager import SoundManager
                        from src.audio.sound_events import SoundEvent
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass
                elif abs(val) < 0.25:
                    self._axis_y_held = False
            elif event.axis == 0:
                if event.value > 0.65 and not self._axis_x_held:
                    self.selected_index = (self.selected_index + 7) % len(self.items)
                    self._axis_x_held = True
                    try:
                        from src.audio.sound_manager import SoundManager
                        from src.audio.sound_events import SoundEvent
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass
                elif event.value < -0.65 and not self._axis_x_held:
                    self.selected_index = (self.selected_index + 7) % len(self.items)
                    self._axis_x_held = True
                    try:
                        from src.audio.sound_manager import SoundManager
                        from src.audio.sound_events import SoundEvent
                        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                    except Exception:
                        pass
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
            elif self.language_toggle_rect.collidepoint(vx, vy):
                self.cycle_language()
                return True
            elif self.quality_toggle_rect.collidepoint(vx, vy):
                self.cycle_effects_quality()
                return True
            elif self.game_boost_toggle_rect.collidepoint(vx, vy):
                self.toggle_game_boost()
                return True
            elif self.p1_controller_prev_rect.collidepoint(vx, vy):
                self.cycle_p1_controller(-1)
                return True
            elif self.p1_controller_next_rect.collidepoint(vx, vy) or self.p1_controller_box_rect.collidepoint(vx, vy):
                self.cycle_p1_controller(+1)
                return True
            elif self.p2_controller_prev_rect.collidepoint(vx, vy):
                self.cycle_p2_controller(-1)
                return True
            elif self.p2_controller_next_rect.collidepoint(vx, vy) or self.p2_controller_box_rect.collidepoint(vx, vy):
                self.cycle_p2_controller(+1)
                return True
            for rect, idx in self.button_rects:
                if rect.collidepoint(vx, vy):
                    self.selected_index = idx
                    action_key, _, _ = self.items[idx]
                    self.waiting_for_key_action = action_key
                    return True
            if self.touch_editor_btn_rect.collidepoint(vx, vy):
                self.touch_editor.open()
                return True
            elif self.ui_mode_toggle_rect.collidepoint(vx, vy):
                self.cycle_ui_mode()
                return True
            elif self.close_rect.collidepoint(vx, vy):
                self.close()
                return True
            elif self.reset_rect.collidepoint(vx, vy):
                self.reset_to_defaults()
                return True

        # Navegação no menu por teclado
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_c):
                self.close()
                return True
            elif event.key == pygame.K_1:
                self.cycle_p1_controller(+1)
                return True
            elif event.key == pygame.K_2:
                self.cycle_p2_controller(+1)
                return True
            elif event.key == pygame.K_g:
                self.cycle_ai_difficulty()
                return True
            elif event.key == pygame.K_l:
                self.cycle_language()
                return True
            elif event.key == pygame.K_e:
                self.cycle_effects_quality()
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
            if self.p1_controller_prev_rect.collidepoint(mx, my):
                self.cycle_p1_controller(-1)
                return True
            elif self.p1_controller_next_rect.collidepoint(mx, my) or self.p1_controller_box_rect.collidepoint(mx, my):
                self.cycle_p1_controller(+1)
                return True
            elif self.p2_controller_prev_rect.collidepoint(mx, my):
                self.cycle_p2_controller(-1)
                return True
            elif self.p2_controller_next_rect.collidepoint(mx, my) or self.p2_controller_box_rect.collidepoint(mx, my):
                self.cycle_p2_controller(+1)
                return True
            elif self.sfx_minus_rect.collidepoint(mx, my):
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
            elif self.language_toggle_rect.collidepoint(mx, my):
                self.cycle_language()
                return True
            elif self.quality_toggle_rect.collidepoint(mx, my):
                self.cycle_effects_quality()
                return True
            elif self.game_boost_toggle_rect.collidepoint(mx, my):
                self.toggle_game_boost()
                return True
            for rect, idx in self.button_rects:
                if rect.collidepoint(mx, my):
                    self.selected_index = idx
                    action_key, _, _ = self.items[idx]
                    self.waiting_for_key_action = action_key
                    return True

            if self.touch_editor_btn_rect.collidepoint(mx, my):
                self.touch_editor.open()
                return True
            elif self.ui_mode_toggle_rect.collidepoint(mx, my):
                self.cycle_ui_mode()
                return True
            elif self.close_rect.collidepoint(mx, my):
                self.close()
                return True
            elif self.reset_rect.collidepoint(mx, my):
                self.reset_to_defaults()
                return True

        return True

    def update(self, dt: float):
        if self.is_open:
            self.blink_timer += dt

    def _render_mobile_settings(self, surface: pygame.Surface, font_large, font_mid, font_small):
        """Layout exclusivo e simplificado de opções para smartphones sem controle físico conectado."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 14, 12, 220))
        surface.blit(overlay, (0, 0))

        from src.audio.sound_manager import SoundManager
        mgr = SoundManager.get_instance()
        from src.input.device_info import get_saved_ui_mode

        panel_w = 720
        panel_h = 580
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 10
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        pygame.draw.rect(surface, (38, 36, 34), panel_rect, border_radius=12)
        pygame.draw.rect(surface, (212, 175, 55), panel_rect, 2, border_radius=12)
        pygame.draw.rect(surface, (55, 50, 44), panel_rect.inflate(-8, -8), 1, border_radius=8)

        title_surf = font_large.render(t("settings_title"), True, (212, 175, 55))
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2, panel_y + 16))

        sub_surf = font_small.render(t("settings_subtitle"), True, (180, 175, 165))
        surface.blit(sub_surf, (panel_rect.centerx - sub_surf.get_width() // 2, panel_y + 54))

        # Indicador de detecção de controle físico MFi / Bluetooth
        from src.input.controller_manager import get_controller_manager
        c_mgr = get_controller_manager()
        c_mgr.poll_controllers()
        c1 = c_mgr.get_controller_for_player(0)
        if c1:
            badge_txt = font_small.render(f"🎮 {c1.friendly_name} CONECTADO", True, (110, 245, 150))
        else:
            badge_txt = font_small.render("📱 MODO TOUCH SCREEN (Nenhum controle físico conectado)", True, (150, 165, 175))
        surface.blit(badge_txt, (panel_rect.centerx - badge_txt.get_width() // 2, panel_y + 78))

        draw_brush_divider(surface, panel_x + 40, panel_y + 102, panel_x + panel_w - 40)

        cy = panel_y + 116

        # 1. Volume SFX
        sfx_lbl = font_mid.render(f"{t('sfx_volume_label')}: {int(mgr.sfx_volume * 100)}%", True, COLOR_WHITE)
        surface.blit(sfx_lbl, (panel_x + 60, cy + 8))

        btn_size = 44
        bar_w = 220
        controls_x = panel_rect.right - 60 - (btn_size * 2 + bar_w + 16)

        self.sfx_minus_rect = pygame.Rect(controls_x, cy, btn_size, btn_size)
        self.sfx_bar_rect = pygame.Rect(controls_x + btn_size + 8, cy, bar_w, btn_size)
        self.sfx_plus_rect = pygame.Rect(controls_x + btn_size + bar_w + 16, cy, btn_size, btn_size)

        pygame.draw.rect(surface, (28, 36, 32), self.sfx_minus_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.sfx_minus_rect, 1, border_radius=6)
        minus_s = font_mid.render("-", True, COLOR_GOLD)
        surface.blit(minus_s, minus_s.get_rect(center=self.sfx_minus_rect.center))

        pygame.draw.rect(surface, (24, 28, 26), (self.sfx_bar_rect.x, cy + 12, bar_w, 20), border_radius=4)
        fill_w = int(bar_w * mgr.sfx_volume)
        if fill_w > 0:
            pygame.draw.rect(surface, (110, 225, 140), (self.sfx_bar_rect.x, cy + 12, fill_w, 20), border_radius=4)
        pygame.draw.rect(surface, COLOR_GOLD, (self.sfx_bar_rect.x, cy + 12, bar_w, 20), 1, border_radius=4)

        pygame.draw.rect(surface, (28, 36, 32), self.sfx_plus_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.sfx_plus_rect, 1, border_radius=6)
        plus_s = font_mid.render("+", True, COLOR_GOLD)
        surface.blit(plus_s, plus_s.get_rect(center=self.sfx_plus_rect.center))

        cy += 56

        # 2. Volume BGM
        bgm_lbl = font_mid.render(f"{t('bgm_volume_label')}: {int(mgr.bgm_volume * 100)}%", True, COLOR_WHITE)
        surface.blit(bgm_lbl, (panel_x + 60, cy + 8))

        self.bgm_minus_rect = pygame.Rect(controls_x, cy, btn_size, btn_size)
        self.bgm_bar_rect = pygame.Rect(controls_x + btn_size + 8, cy, bar_w, btn_size)
        self.bgm_plus_rect = pygame.Rect(controls_x + btn_size + bar_w + 16, cy, btn_size, btn_size)

        pygame.draw.rect(surface, (28, 36, 32), self.bgm_minus_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.bgm_minus_rect, 1, border_radius=6)
        surface.blit(minus_s, minus_s.get_rect(center=self.bgm_minus_rect.center))

        pygame.draw.rect(surface, (24, 28, 26), (self.bgm_bar_rect.x, cy + 12, bar_w, 20), border_radius=4)
        fill_bgm = int(bar_w * mgr.bgm_volume)
        if fill_bgm > 0:
            pygame.draw.rect(surface, (110, 225, 140), (self.bgm_bar_rect.x, cy + 12, fill_bgm, 20), border_radius=4)
        pygame.draw.rect(surface, COLOR_GOLD, (self.bgm_bar_rect.x, cy + 12, bar_w, 20), 1, border_radius=4)

        pygame.draw.rect(surface, (28, 36, 32), self.bgm_plus_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.bgm_plus_rect, 1, border_radius=6)
        surface.blit(plus_s, plus_s.get_rect(center=self.bgm_plus_rect.center))

        cy += 64
        draw_brush_divider(surface, panel_x + 40, cy, panel_x + panel_w - 40)
        cy += 18

        # 3. Dificuldade da IA & Idioma
        diff_names = {"easy": t("difficulty_easy"), "normal": t("difficulty_normal"), "hard": t("difficulty_hard")}
        diff_colors = {"easy": (110, 225, 140), "normal": COLOR_GOLD, "hard": (245, 95, 85)}
        d_name = diff_names.get(self.ai_difficulty, t("difficulty_normal"))
        d_col = diff_colors.get(self.ai_difficulty, COLOR_GOLD)

        btn_w = 520
        half_w = (btn_w - 10) // 2

        self.difficulty_toggle_rect = pygame.Rect(panel_rect.centerx - btn_w // 2, cy, half_w, 42)
        pygame.draw.rect(surface, (28, 36, 32), self.difficulty_toggle_rect, border_radius=8)
        pygame.draw.rect(surface, d_col, self.difficulty_toggle_rect, 1, border_radius=8)
        d_lbl = self._fit_text(font_small, t("ai_difficulty_label").format(d_name=d_name), d_col, half_w - 12)
        surface.blit(d_lbl, d_lbl.get_rect(center=self.difficulty_toggle_rect.center))

        from src.i18n import get_saved_language_preference, LANG_AUTO, LANG_PT, LANG_EN
        pref = get_saved_language_preference()
        lang_str = t("lang_auto") if pref == LANG_AUTO else (t("lang_pt") if pref == LANG_PT else t("lang_en"))
        l_col = (110, 225, 140) if pref != LANG_AUTO else COLOR_GOLD
        self.language_toggle_rect = pygame.Rect(panel_rect.centerx - btn_w // 2 + half_w + 10, cy, half_w, 42)
        pygame.draw.rect(surface, (28, 36, 32), self.language_toggle_rect, border_radius=8)
        pygame.draw.rect(surface, l_col, self.language_toggle_rect, 1, border_radius=8)
        l_lbl = self._fit_text(font_small, t("language_toggle_label").format(lang_name=lang_str), l_col, half_w - 12)
        surface.blit(l_lbl, l_lbl.get_rect(center=self.language_toggle_rect.center))

        cy += 50

        # 4. Modo de Interface (UI Mode: Automático / Smartphone / Clássico)
        ui_mode = get_saved_ui_mode()
        ui_mode_names = {"auto": "AUTOMÁTICO", "mobile": "SMARTPHONE", "classic": "CLÁSSICO"}
        u_name = ui_mode_names.get(ui_mode, "AUTOMÁTICO")
        self.ui_mode_toggle_rect = pygame.Rect(panel_rect.centerx - btn_w // 2, cy, btn_w, 42)
        pygame.draw.rect(surface, (28, 36, 32), self.ui_mode_toggle_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, self.ui_mode_toggle_rect, 1, border_radius=8)
        u_lbl = font_mid.render(f"LAYOUT DA INTERFACE: [ {u_name} ]", True, COLOR_GOLD)
        surface.blit(u_lbl, u_lbl.get_rect(center=self.ui_mode_toggle_rect.center))

        cy += 50

        # 5. Qualidade dos Efeitos & Game Boost
        from src.effects import quality
        high = quality.is_high()
        q_col = (110, 225, 140) if high else (245, 190, 85)
        q_label = t("effects_quality_label").format(q_name=t("quality_high") if high else t("quality_low"))
        half_w = (btn_w - 10) // 2

        self.quality_toggle_rect = pygame.Rect(panel_rect.centerx - btn_w // 2, cy, half_w, 42)
        pygame.draw.rect(surface, (28, 36, 32), self.quality_toggle_rect, border_radius=8)
        pygame.draw.rect(surface, q_col, self.quality_toggle_rect, 1, border_radius=8)
        q_lbl = self._fit_text(font_small, q_label, q_col, half_w - 12)
        surface.blit(q_lbl, q_lbl.get_rect(center=self.quality_toggle_rect.center))

        boost_on = quality.is_game_boost_enabled()
        b_col = (110, 225, 140) if boost_on else (160, 175, 168)
        b_label = t("game_boost_label").format(status=t("status_on") if boost_on else t("status_off"))
        self.game_boost_toggle_rect = pygame.Rect(panel_rect.centerx - btn_w // 2 + half_w + 10, cy, half_w, 42)
        pygame.draw.rect(surface, (28, 36, 32), self.game_boost_toggle_rect, border_radius=8)
        pygame.draw.rect(surface, b_col, self.game_boost_toggle_rect, 1, border_radius=8)
        b_lbl = self._fit_text(font_small, b_label, b_col, half_w - 12)
        surface.blit(b_lbl, b_lbl.get_rect(center=self.game_boost_toggle_rect.center))

        cy += 54

        # 6. Botão "PERSONALIZAR BOTÕES TOUCH (HUD)"
        self.touch_editor_btn_rect = pygame.Rect(panel_rect.centerx - btn_w // 2, cy, btn_w, 46)
        pygame.draw.rect(surface, (36, 48, 40), self.touch_editor_btn_rect, border_radius=8)
        pygame.draw.rect(surface, (212, 175, 55), self.touch_editor_btn_rect, 2, border_radius=8)
        hud_lbl = font_mid.render("⚙ PERSONALIZAR BOTÕES TOUCH (HUD)", True, COLOR_GOLD)
        surface.blit(hud_lbl, hud_lbl.get_rect(center=self.touch_editor_btn_rect.center))

        # 7. Rodapé: Restaurar Padrões e Voltar
        self.reset_rect = pygame.Rect(panel_rect.centerx - 170, panel_y + panel_h - 78, 340, 34)
        pygame.draw.rect(surface, (32, 38, 34), self.reset_rect, border_radius=6)
        pygame.draw.rect(surface, (70, 85, 75), self.reset_rect, 1, border_radius=6)
        rst_surf = self._fit_text(font_small, t("reset_defaults_hint"), (220, 210, 160), 320)
        surface.blit(rst_surf, rst_surf.get_rect(center=self.reset_rect.center))

        self.close_rect = pygame.Rect(panel_rect.centerx - 170, SCREEN_HEIGHT - 68, 340, 48)
        pygame.draw.rect(surface, (45, 62, 52), self.close_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, self.close_rect, 2, border_radius=8)
        cls_surf = self._fit_text(font_mid, t("settings_return_button"), COLOR_GOLD, 320)
        surface.blit(cls_surf, cls_surf.get_rect(center=self.close_rect.center))

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        if not self.is_open:
            return

        if hasattr(self, "touch_editor") and self.touch_editor.is_open:
            self.touch_editor.render(surface)
            return

        from src.input.controller_manager import get_controller_manager
        ctrl_mgr = get_controller_manager()
        ctrl_mgr.poll_controllers()
        has_any_controller = ctrl_mgr.has_controller(0) or ctrl_mgr.has_controller(1) or pygame.joystick.get_count() > 0

        if is_mobile_device() and not has_any_controller:
            self._render_mobile_settings(surface, font_large, font_mid, font_small)
            return

        from src.effects import parchment as pm
        parch = pm.get_backdrop() is not None
        if parch:
            self._render_parchment(surface, font_large, font_mid, font_small, ctrl_mgr)
        else:
            self._render_fallback(surface, font_large, font_mid, font_small, ctrl_mgr)

    def _render_parchment(self, surface: pygame.Surface, font_large: pygame.font.Font, font_mid: pygame.font.Font, font_small: pygame.font.Font, ctrl_mgr):
        from src.effects import parchment as pm
        from src.ui.svg_icon_renderer import get_button_icon_surface
        from src.audio.sound_manager import SoundManager
        from src.effects import quality

        # 1. Overlay escuro suave de fundo
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 8, 6, 175))
        surface.blit(overlay, (0, 0))

        # 2. Pergaminho Central em Papel Envelhecido com Varas de Madeira
        panel_w, panel_h = 960, 650
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 10
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # Folha de papel Sumi-E
        paper = pm.make_paper(panel_w, panel_h, seed=61, ragged=(False, False, True, True), burn=0.25)
        surface.blit(pm._soft_shadow(paper, blur=8, opacity=130), (panel_x + 3, panel_y + 5))
        surface.blit(paper, (panel_x, panel_y))

        # Varas de madeira no topo e na base
        pm.draw_rod(surface, "top", panel_rect.centerx, panel_rect.y - 14, panel_w + 32)
        pm.draw_rod(surface, "bottom", panel_rect.centerx, panel_rect.bottom - 22, panel_w + 32)

        # Brasão da garça no canto superior direito
        pm.draw_crest(surface, panel_rect.right - 92, panel_rect.y + 14, scale=0.62)

        # 3. Título do Menu em Nanquim
        title_surf = pm.render_ink(font_large, t("settings_title"), pm.INK)
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2, panel_y + 14))

        sub_surf = font_small.render(t("settings_subtitle"), True, pm.INK_SOFT)
        surface.blit(sub_surf, (panel_rect.centerx - sub_surf.get_width() // 2, panel_y + 60))

        # 4. Duas Colunas: Vermelho à Esquerda e Azul à Direita
        col_w = 430
        col_left_x = panel_x + 30
        col_right_x = panel_x + panel_w - col_w - 30
        start_y = panel_y + 118
        row_h = 40

        box_w = 210
        box_h = 24
        header_max_w = col_w - box_w - 14

        pygame.draw.line(surface, pm.INK_SOFT, (col_left_x, start_y - 38), (col_right_x + col_w, start_y - 38), 1)

        h1 = self._fit_text(font_mid, t("player_1_label"), pm.SEAL_RED, header_max_w)
        h2 = self._fit_text(font_mid, t("player_2_label"), pm.SEAL_BLUE, header_max_w)
        surface.blit(h1, (col_left_x + 6, start_y - 28))
        surface.blit(h2, (col_right_x + 6, start_y - 28))

        # Seletor interativo de Controle P1
        p1_ctrl_name = ctrl_mgr.get_player_controller_name(0)
        p1_box_x = col_left_x + col_w - box_w
        p1_box_y = start_y - 28
        self.p1_controller_box_rect = pygame.Rect(p1_box_x, p1_box_y, box_w, box_h)
        self.p1_controller_prev_rect = pygame.Rect(p1_box_x, p1_box_y, 22, box_h)
        self.p1_controller_next_rect = pygame.Rect(p1_box_x + box_w - 22, p1_box_y, 22, box_h)

        pygame.draw.rect(surface, (226, 212, 185), self.p1_controller_box_rect, border_radius=4)
        pygame.draw.rect(surface, pm.SEAL_RED, self.p1_controller_box_rect, 1, border_radius=4)
        arrow_l = font_small.render("<", True, pm.SEAL_RED)
        arrow_r = font_small.render(">", True, pm.SEAL_RED)
        surface.blit(arrow_l, (p1_box_x + 6, p1_box_y + 3))
        surface.blit(arrow_r, (p1_box_x + box_w - 14, p1_box_y + 3))
        p1_lbl = self._fit_text(font_small, p1_ctrl_name, pm.INK, box_w - 38)
        surface.blit(p1_lbl, (p1_box_x + (box_w - p1_lbl.get_width()) // 2, p1_box_y + 3))

        # Seletor interativo de Controle P2
        p2_ctrl_name = ctrl_mgr.get_player_controller_name(1)
        p2_box_x = col_right_x + col_w - box_w
        p2_box_y = start_y - 28
        self.p2_controller_box_rect = pygame.Rect(p2_box_x, p2_box_y, box_w, box_h)
        self.p2_controller_prev_rect = pygame.Rect(p2_box_x, p2_box_y, 22, box_h)
        self.p2_controller_next_rect = pygame.Rect(p2_box_x + box_w - 22, p2_box_y, 22, box_h)

        pygame.draw.rect(surface, (226, 212, 185), self.p2_controller_box_rect, border_radius=4)
        pygame.draw.rect(surface, pm.SEAL_BLUE, self.p2_controller_box_rect, 1, border_radius=4)
        arrow_l_b = font_small.render("<", True, pm.SEAL_BLUE)
        arrow_r_b = font_small.render(">", True, pm.SEAL_BLUE)
        surface.blit(arrow_l_b, (p2_box_x + 6, p2_box_y + 3))
        surface.blit(arrow_r_b, (p2_box_x + box_w - 14, p2_box_y + 3))
        p2_lbl = self._fit_text(font_small, p2_ctrl_name, pm.INK, box_w - 38)
        surface.blit(p2_lbl, (p2_box_x + (box_w - p2_lbl.get_width()) // 2, p2_box_y + 3))

        self.button_rects.clear()

        for idx, (action_key, label, faction) in enumerate(self.items):
            is_red = (faction == "red")

            item_col_x = col_left_x if is_red else col_right_x
            row_index = idx if is_red else (idx - 7)
            cur_y = start_y + row_index * row_h

            btn_rect = pygame.Rect(item_col_x, cur_y, col_w, 32)
            self.button_rects.append((btn_rect, idx))

            is_selected = (self.selected_index == idx)
            is_waiting = (self.waiting_for_key_action == action_key)

            if is_waiting:
                stroke_c = pm.SEAL_RED if (int(self.blink_timer * 4) % 2 == 0) else (140, 40, 35)
                pm.draw_brush_highlight(surface, btn_rect.inflate(4, 2), color=stroke_c, seed=idx + 3)
                pm.draw_ink_border(surface, btn_rect, color=stroke_c, width=1, seed=idx + 1)
                action_surf = self._fit_text(font_small, t("settings_action_" + action_key[3:].lower()), (252, 248, 235), 150)
                surface.blit(action_surf, (btn_rect.x + 10, btn_rect.y + 8))
                val_surf = self._fit_text(font_small, t("settings_press_key"), (245, 225, 170), col_w - 180)
                surface.blit(val_surf, (btn_rect.right - val_surf.get_width() - 10, btn_rect.y + 7))
            elif is_selected:
                stroke_col = pm.SEAL_RED if is_red else pm.SEAL_BLUE
                pm.draw_brush_highlight(surface, btn_rect.inflate(4, 2), color=stroke_col, seed=idx + 3, alpha=215)
                pm.draw_ink_border(surface, btn_rect, color=stroke_col, width=1, seed=idx + 1)
                action_surf = self._fit_text(font_small, t("settings_action_" + action_key[3:].lower()), (252, 248, 235), 150)
                surface.blit(action_surf, (btn_rect.x + 10, btn_rect.y + 8))
            else:
                pygame.draw.rect(surface, (218, 202, 172), btn_rect, border_radius=4)
                pygame.draw.rect(surface, (168, 150, 128), btn_rect, 1, border_radius=4)
                action_surf = self._fit_text(font_small, t("settings_action_" + action_key[3:].lower()), pm.INK, 150)
                surface.blit(action_surf, (btn_rect.x + 10, btn_rect.y + 8))

            if not is_waiting:
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

                if ctrl:
                    if action_key.endswith(("_UP", "_DOWN", "_LEFT", "_RIGHT")):
                        svg_icon_name = "dpad"
                        btn_label = t("settings_dpad_" + action_key.rsplit("_", 1)[1].lower())
                    elif act_suffix:
                        if ctrl.is_playstation:
                            svg_icon_name = ctrl.get_button_svg_icon(act_suffix)
                        btn_label = ctrl.get_mapped_button_name(act_suffix)

                key_color = (245, 225, 170) if is_selected else pm.INK_SOFT

                cur_right_x = btn_rect.right - 10
                if svg_icon_name:
                    icon_surf = get_button_icon_surface(svg_icon_name, 18, 18)
                    cur_right_x -= 20
                    surface.blit(icon_surf, (cur_right_x, btn_rect.y + 7))

                key_surf = self._fit_text(font_small, f"[{key_str}]", key_color, 130)
                if btn_label:
                    room = col_w - 180 - key_surf.get_width() - (20 if svg_icon_name else 0)
                    label_color = (230, 240, 220) if is_selected else (60, 95, 75)
                    label_surf = self._fit_text(font_small, f"[{btn_label}]", label_color, max(room, 40))
                    cur_right_x -= (label_surf.get_width() + 5)
                    surface.blit(label_surf, (cur_right_x, btn_rect.y + 7))

                cur_right_x -= (key_surf.get_width() + 5)
                surface.blit(key_surf, (cur_right_x, btn_rect.y + 7))

        # 5. Painel de Volumes (SFX e BGM)
        sound_mgr = SoundManager.get_instance()
        audio_y = start_y + 7 * row_h + 10

        pygame.draw.line(surface, pm.INK_SOFT, (col_left_x, audio_y - 6), (col_right_x + col_w, audio_y - 6), 1)

        # Coluna SFX
        sfx_pct = int(sound_mgr.sfx_volume * 100)
        sfx_lbl = self._fit_text(font_small, t("sfx_volume_label").format(sfx_pct=sfx_pct), pm.INK, 190)
        surface.blit(sfx_lbl, (col_left_x + 5, audio_y))

        self.sfx_minus_rect = pygame.Rect(col_left_x + 200, audio_y - 2, 28, 24)
        self.sfx_bar_rect = pygame.Rect(col_left_x + 235, audio_y + 3, 140, 14)
        self.sfx_plus_rect = pygame.Rect(col_left_x + 382, audio_y - 2, 28, 24)

        for btn_r, symb in ((self.sfx_minus_rect, "-"), (self.sfx_plus_rect, "+")):
            pygame.draw.rect(surface, (226, 212, 185), btn_r, border_radius=4)
            pygame.draw.rect(surface, (140, 125, 105), btn_r, 1, border_radius=4)
            t_s = font_small.render(symb, True, pm.INK)
            surface.blit(t_s, (btn_r.centerx - t_s.get_width() // 2, btn_r.centery - t_s.get_height() // 2))

        pygame.draw.rect(surface, (195, 180, 152), self.sfx_bar_rect, border_radius=3)
        fill_w = int(self.sfx_bar_rect.width * sound_mgr.sfx_volume)
        if fill_w > 0:
            fill_r = pygame.Rect(self.sfx_bar_rect.x, self.sfx_bar_rect.y, fill_w, self.sfx_bar_rect.height)
            pygame.draw.rect(surface, (170, 125, 45), fill_r, border_radius=3)
        pygame.draw.rect(surface, (140, 125, 105), self.sfx_bar_rect, 1, border_radius=3)

        # Coluna BGM
        bgm_pct = int(sound_mgr.bgm_volume * 100)
        bgm_lbl = self._fit_text(font_small, t("bgm_volume_label").format(bgm_pct=bgm_pct), pm.INK, 190)
        surface.blit(bgm_lbl, (col_right_x + 5, audio_y))

        self.bgm_minus_rect = pygame.Rect(col_right_x + 200, audio_y - 2, 28, 24)
        self.bgm_bar_rect = pygame.Rect(col_right_x + 235, audio_y + 3, 140, 14)
        self.bgm_plus_rect = pygame.Rect(col_right_x + 382, audio_y - 2, 28, 24)

        for btn_r, symb in ((self.bgm_minus_rect, "-"), (self.bgm_plus_rect, "+")):
            pygame.draw.rect(surface, (226, 212, 185), btn_r, border_radius=4)
            pygame.draw.rect(surface, (140, 125, 105), btn_r, 1, border_radius=4)
            t_s = font_small.render(symb, True, pm.INK)
            surface.blit(t_s, (btn_r.centerx - t_s.get_width() // 2, btn_r.centery - t_s.get_height() // 2))

        pygame.draw.rect(surface, (195, 180, 152), self.bgm_bar_rect, border_radius=3)
        fill_w = int(self.bgm_bar_rect.width * sound_mgr.bgm_volume)
        if fill_w > 0:
            fill_r = pygame.Rect(self.bgm_bar_rect.x, self.bgm_bar_rect.y, fill_w, self.bgm_bar_rect.height)
            pygame.draw.rect(surface, (70, 125, 95), fill_r, border_radius=3)
        pygame.draw.rect(surface, (140, 125, 105), self.bgm_bar_rect, 1, border_radius=3)

        # 6. Status de Gamepads e Controles Touch
        badge_p1 = ctrl_mgr.get_badge_text(0) or t("gamepad_not_detected_p1")
        badge_p2 = ctrl_mgr.get_badge_text(1) or t("gamepad_not_detected_p2")

        status_text = f"P1: {badge_p1}   |   P2: {badge_p2}   [1 / L1: P1, 2 / R1: P2]"
        status_surf = self._fit_text(font_small, status_text, pm.INK_SOFT, 860)
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
        pygame.draw.rect(surface, (226, 212, 185), self.touch_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, (150, 135, 115), self.touch_toggle_rect, 1, border_radius=6)
        touch_lbl = self._fit_text(font_small, t("touch_controls_label").format(touch_mode_str=touch_mode_str), pm.INK, 336)
        surface.blit(touch_lbl, (self.touch_toggle_rect.centerx - touch_lbl.get_width() // 2, self.touch_toggle_rect.y + 5))

        # Botão Alternador de Dificuldade da IA e de Idioma
        diff_names = {
            "easy": t("difficulty_easy"),
            "normal": t("difficulty_normal"),
            "hard": t("difficulty_hard")
        }
        diff_colors = {"easy": (45, 140, 65), "normal": (170, 125, 45), "hard": pm.SEAL_RED}
        d_name = diff_names.get(self.ai_difficulty, t("difficulty_normal"))
        d_col = diff_colors.get(self.ai_difficulty, (170, 125, 45))

        self.difficulty_toggle_rect = pygame.Rect(panel_rect.centerx - 195, audio_y + 90, 190, 26)
        pygame.draw.rect(surface, (226, 212, 185), self.difficulty_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, d_col, self.difficulty_toggle_rect, 2, border_radius=6)
        diff_lbl = self._fit_text(font_small, t("ai_difficulty_label").format(d_name=d_name), d_col, 180)
        surface.blit(diff_lbl, (self.difficulty_toggle_rect.centerx - diff_lbl.get_width() // 2, self.difficulty_toggle_rect.y + 5))

        from src.i18n import get_saved_language_preference, LANG_AUTO, LANG_PT, LANG_EN
        pref = get_saved_language_preference()
        lang_str = t("lang_auto") if pref == LANG_AUTO else (t("lang_pt") if pref == LANG_PT else t("lang_en"))
        l_col = (70, 125, 95) if pref != LANG_AUTO else pm.INK
        self.language_toggle_rect = pygame.Rect(panel_rect.centerx + 5, audio_y + 90, 190, 26)
        pygame.draw.rect(surface, (226, 212, 185), self.language_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, l_col, self.language_toggle_rect, 1, border_radius=6)
        l_lbl = self._fit_text(font_small, t("language_toggle_label").format(lang_name=lang_str), l_col, 180)
        surface.blit(l_lbl, (self.language_toggle_rect.centerx - l_lbl.get_width() // 2, self.language_toggle_rect.y + 5))

        # Botão de qualidade dos efeitos e Game Boost
        high = quality.is_high()
        q_color = (45, 140, 65) if high else (170, 125, 45)
        q_label = t("effects_quality_label").format(q_name=t("quality_high") if high else t("quality_low"))
        self.quality_toggle_rect = pygame.Rect(panel_rect.centerx - 195, audio_y + 120, 190, 26)
        pygame.draw.rect(surface, (226, 212, 185), self.quality_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, q_color, self.quality_toggle_rect, 1, border_radius=6)
        lbl = self._fit_text(font_small, q_label, q_color, 180)
        surface.blit(lbl, (self.quality_toggle_rect.centerx - lbl.get_width() // 2, self.quality_toggle_rect.y + 5))

        boost_on = quality.is_game_boost_enabled()
        b_col = (45, 140, 65) if boost_on else pm.INK_SOFT
        b_label = t("game_boost_label").format(status=t("status_on") if boost_on else t("status_off"))
        self.game_boost_toggle_rect = pygame.Rect(panel_rect.centerx + 5, audio_y + 120, 190, 26)
        pygame.draw.rect(surface, (226, 212, 185), self.game_boost_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, b_col, self.game_boost_toggle_rect, 1, border_radius=6)
        b_lbl = self._fit_text(font_small, b_label, b_col, 180)
        surface.blit(b_lbl, (self.game_boost_toggle_rect.centerx - b_lbl.get_width() // 2, self.game_boost_toggle_rect.y + 5))

        # 7. Botões de Ação no Rodapé do Painel
        self.reset_rect = pygame.Rect(panel_rect.centerx - 140, panel_y + panel_h - 96, 280, 36)
        pygame.draw.rect(surface, (226, 212, 185), self.reset_rect, border_radius=6)
        pygame.draw.rect(surface, (150, 135, 115), self.reset_rect, 1, border_radius=6)
        rst_surf = self._fit_text(font_small, t("reset_defaults_hint"), pm.INK, 260)
        surface.blit(rst_surf, rst_surf.get_rect(center=self.reset_rect.center))

        self.close_rect = pygame.Rect(panel_rect.centerx - 160, SCREEN_HEIGHT - 68, 320, 48)
        pygame.draw.rect(surface, pm.SEAL_RED, self.close_rect, border_radius=8)
        pygame.draw.rect(surface, (212, 175, 55), self.close_rect, 2, border_radius=8)
        cls_surf = self._fit_text(font_mid, t("settings_return_button"), (252, 248, 235), 300)
        surface.blit(cls_surf, cls_surf.get_rect(center=self.close_rect.center))

    def _render_fallback(self, surface: pygame.Surface, font_large: pygame.font.Font, font_mid: pygame.font.Font, font_small: pygame.font.Font, ctrl_mgr):
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

        from src.input.controller_manager import get_controller_manager
        from src.ui.svg_icon_renderer import get_button_icon_surface
        ctrl_mgr = get_controller_manager()

        # Cabeçalhos das Colunas e Seletores de Controle sem sobreposição
        box_w = 210
        box_h = 24
        header_max_w = col_w - box_w - 14

        h1 = self._fit_text(font_mid, t("player_1_label"), COLOR_RED_AURA, header_max_w)
        h2 = self._fit_text(font_mid, t("player_2_label"), COLOR_BLUE_AURA, header_max_w)
        surface.blit(h1, (col_left_x + 6, start_y - 28))
        surface.blit(h2, (col_right_x + 6, start_y - 28))

        # Seletor interativo de Controle P1
        p1_ctrl_name = ctrl_mgr.get_player_controller_name(0)
        p1_box_x = col_left_x + col_w - box_w
        p1_box_y = start_y - 28
        self.p1_controller_box_rect = pygame.Rect(p1_box_x, p1_box_y, box_w, box_h)
        self.p1_controller_prev_rect = pygame.Rect(p1_box_x, p1_box_y, 22, box_h)
        self.p1_controller_next_rect = pygame.Rect(p1_box_x + box_w - 22, p1_box_y, 22, box_h)

        pygame.draw.rect(surface, (36, 32, 28), self.p1_controller_box_rect, border_radius=4)
        pygame.draw.rect(surface, (160, 75, 75), self.p1_controller_box_rect, 1, border_radius=4)
        arrow_l = font_small.render("<", True, (212, 175, 55))
        arrow_r = font_small.render(">", True, (212, 175, 55))
        surface.blit(arrow_l, (p1_box_x + 6, p1_box_y + 3))
        surface.blit(arrow_r, (p1_box_x + box_w - 14, p1_box_y + 3))
        p1_lbl = self._fit_text(font_small, p1_ctrl_name, (230, 225, 215), box_w - 38)
        surface.blit(p1_lbl, (p1_box_x + (box_w - p1_lbl.get_width()) // 2, p1_box_y + 3))

        # Seletor interativo de Controle P2
        p2_ctrl_name = ctrl_mgr.get_player_controller_name(1)
        p2_box_x = col_right_x + col_w - box_w
        p2_box_y = start_y - 28
        self.p2_controller_box_rect = pygame.Rect(p2_box_x, p2_box_y, box_w, box_h)
        self.p2_controller_prev_rect = pygame.Rect(p2_box_x, p2_box_y, 22, box_h)
        self.p2_controller_next_rect = pygame.Rect(p2_box_x + box_w - 22, p2_box_y, 22, box_h)

        pygame.draw.rect(surface, (36, 32, 28), self.p2_controller_box_rect, border_radius=4)
        pygame.draw.rect(surface, (75, 95, 160), self.p2_controller_box_rect, 1, border_radius=4)
        surface.blit(arrow_l, (p2_box_x + 6, p2_box_y + 3))
        surface.blit(arrow_r, (p2_box_x + box_w - 14, p2_box_y + 3))
        p2_lbl = self._fit_text(font_small, p2_ctrl_name, (230, 225, 215), box_w - 38)
        surface.blit(p2_lbl, (p2_box_x + (box_w - p2_lbl.get_width()) // 2, p2_box_y + 3))

        self.button_rects.clear()

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

        status_text = f"P1: {badge_p1}   |   P2: {badge_p2}   [1 / L1: P1, 2 / R1: P2]"
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

        # Botão Alternador de Dificuldade da IA e de Idioma
        diff_names = {
            "easy": t("difficulty_easy"),
            "normal": t("difficulty_normal"),
            "hard": t("difficulty_hard")
        }
        diff_colors = {"easy": (110, 225, 140), "normal": COLOR_GOLD, "hard": (245, 95, 85)}
        d_name = diff_names.get(self.ai_difficulty, t("difficulty_normal"))
        d_col = diff_colors.get(self.ai_difficulty, COLOR_GOLD)

        self.difficulty_toggle_rect = pygame.Rect(panel_rect.centerx - 195, audio_y + 90, 190, 26)
        pygame.draw.rect(surface, (28, 36, 32), self.difficulty_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, d_col, self.difficulty_toggle_rect, 1, border_radius=6)
        diff_lbl = self._fit_text(font_small, t("ai_difficulty_label").format(d_name=d_name), d_col, 180)
        surface.blit(diff_lbl, (self.difficulty_toggle_rect.centerx - diff_lbl.get_width() // 2, self.difficulty_toggle_rect.y + 5))

        from src.i18n import get_saved_language_preference, LANG_AUTO, LANG_PT, LANG_EN
        pref = get_saved_language_preference()
        lang_str = t("lang_auto") if pref == LANG_AUTO else (t("lang_pt") if pref == LANG_PT else t("lang_en"))
        l_col = (110, 225, 140) if pref != LANG_AUTO else COLOR_GOLD
        self.language_toggle_rect = pygame.Rect(panel_rect.centerx + 5, audio_y + 90, 190, 26)
        pygame.draw.rect(surface, (28, 36, 32), self.language_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, l_col, self.language_toggle_rect, 1, border_radius=6)
        l_label = t("language_toggle_label").format(lang_name=lang_str)
        l_lbl = self._fit_text(font_small, l_label, l_col, 180)
        surface.blit(l_lbl, (self.language_toggle_rect.centerx - l_lbl.get_width() // 2, self.language_toggle_rect.y + 5))

        # Botão de qualidade dos efeitos e Game Boost
        from src.effects import quality
        high = quality.is_high()
        color = (110, 225, 140) if high else (245, 190, 85)
        label = t("effects_quality_label").format(q_name=t("quality_high") if high else t("quality_low"))
        self.quality_toggle_rect = pygame.Rect(panel_rect.centerx - 195, audio_y + 120, 190, 26)
        pygame.draw.rect(surface, (28, 36, 32), self.quality_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, color, self.quality_toggle_rect, 1, border_radius=6)
        lbl = self._fit_text(font_small, label, color, 180)
        surface.blit(lbl, (self.quality_toggle_rect.centerx - lbl.get_width() // 2, self.quality_toggle_rect.y + 5))

        boost_on = quality.is_game_boost_enabled()
        b_col = (110, 225, 140) if boost_on else (160, 175, 168)
        b_label = t("game_boost_label").format(status=t("status_on") if boost_on else t("status_off"))
        self.game_boost_toggle_rect = pygame.Rect(panel_rect.centerx + 5, audio_y + 120, 190, 26)
        pygame.draw.rect(surface, (28, 36, 32), self.game_boost_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, b_col, self.game_boost_toggle_rect, 1, border_radius=6)
        b_lbl = self._fit_text(font_small, b_label, b_col, 180)
        surface.blit(b_lbl, (self.game_boost_toggle_rect.centerx - b_lbl.get_width() // 2, self.game_boost_toggle_rect.y + 5))

        # 7. Botões de Ação no Rodapé do Painel
        # Botão Restaurar Padrões
        self.reset_rect = pygame.Rect(panel_rect.centerx - 140, panel_y + panel_h - 96, 280, 36)
        pygame.draw.rect(surface, (32, 38, 34), self.reset_rect, border_radius=6)
        pygame.draw.rect(surface, (70, 85, 75), self.reset_rect, 1, border_radius=6)
        rst_surf = self._fit_text(font_small, t("reset_defaults_hint"), (220, 210, 160), 260)
        surface.blit(rst_surf, rst_surf.get_rect(center=self.reset_rect.center))

        # Botão Fechar / Voltar (Levantado acima da Home Bar)
        self.close_rect = pygame.Rect(panel_rect.centerx - 160, SCREEN_HEIGHT - 68, 320, 48)
        pygame.draw.rect(surface, (45, 62, 52), self.close_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, self.close_rect, 2, border_radius=8)
        cls_surf = self._fit_text(font_mid, t("settings_return_button"), COLOR_GOLD, 300)
        surface.blit(cls_surf, cls_surf.get_rect(center=self.close_rect.center))
