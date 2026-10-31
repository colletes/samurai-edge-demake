"""
Tela e menu interativo de Configuração de Controles (Settings) com Hub Central e Submenus Dedicados.
Permite navegar entre Audiovisual, Jogabilidade, Controles e Galeria de Arte,
com suporte harmonioso aos temas Pergaminho Sumi-E e Tabuleta Kanban Laqueada.
"""
import math
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
    """Menu de Opções do Sistema com Hub de 4 Categorias e Submenus Estilizados."""

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

        # Subtelas do Hub: "HUB", "AUDIOVISUAL", "GAMEPLAY", "CONTROLS"
        self.current_subscreen = "HUB"
        self.hub_selected_index = 0
        self.sub_row_index = 0
        self.request_gallery = False

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

        # Áreas clicáveis inicializadas com dimensões seguras
        self.button_rects: list[tuple[pygame.Rect, int]] = []
        self.hub_cards_rects: list[tuple[pygame.Rect, str]] = []
        self.touch_editor = TouchControlsEditorScreen(self.touch_controls)

        self._init_geometry()

    def _init_geometry(self):
        """Inicializa e pré-computa bounding boxes válidas dentro da tela para todos os elementos."""
        panel_w, panel_h = 980, 650
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 10
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        cx = SCREEN_WIDTH // 2

        # 1. Hub Cards (Grade 2x2)
        card_w = 425
        card_h = 185
        card_x0 = panel_x + 45
        card_x1 = panel_x + panel_w - card_w - 45
        card_y0 = panel_y + 115
        card_y1 = panel_y + 325

        self.hub_audiovisual_rect = pygame.Rect(card_x0, card_y0, card_w, card_h)
        self.hub_gameplay_rect = pygame.Rect(card_x1, card_y0, card_w, card_h)
        self.hub_controls_rect = pygame.Rect(card_x0, card_y1, card_w, card_h)
        self.gallery_btn_rect = pygame.Rect(card_x1, card_y1, card_w, card_h)

        self.hub_cards_rects = [
            (self.hub_audiovisual_rect, "AUDIOVISUAL"),
            (self.hub_gameplay_rect, "GAMEPLAY"),
            (self.hub_controls_rect, "CONTROLS"),
            (self.gallery_btn_rect, "GALLERY"),
        ]

        # Rodapé do Hub: Restaurar Padrões à esquerda, Voltar ao Menu Principal à direita
        self.reset_rect = pygame.Rect(panel_x + 50, panel_rect.bottom - 58, 340, 44)
        self.close_rect = pygame.Rect(panel_x + panel_w - 390, panel_rect.bottom - 58, 340, 44)

        # 2. Subtela de Controles (Grid de remapeamento P1 e P2)
        col_w = 430
        col_left_x = panel_x + 30
        col_right_x = panel_x + panel_w - col_w - 30
        start_y = panel_y + 118
        row_h = 40
        box_w = 210
        box_h = 24

        p1_box_x = col_left_x + col_w - box_w
        p1_box_y = start_y - 28
        self.p1_controller_box_rect = pygame.Rect(p1_box_x, p1_box_y, box_w, box_h)
        self.p1_controller_prev_rect = pygame.Rect(p1_box_x, p1_box_y, 22, box_h)
        self.p1_controller_next_rect = pygame.Rect(p1_box_x + box_w - 22, p1_box_y, 22, box_h)

        p2_box_x = col_right_x + col_w - box_w
        p2_box_y = start_y - 28
        self.p2_controller_box_rect = pygame.Rect(p2_box_x, p2_box_y, box_w, box_h)
        self.p2_controller_prev_rect = pygame.Rect(p2_box_x, p2_box_y, 22, box_h)
        self.p2_controller_next_rect = pygame.Rect(p2_box_x + box_w - 22, p2_box_y, 22, box_h)

        self.button_rects = []
        for idx in range(14):
            is_red = (idx < 7)
            item_col_x = col_left_x if is_red else col_right_x
            row_index = idx if is_red else (idx - 7)
            cur_y = start_y + row_index * row_h
            self.button_rects.append((pygame.Rect(item_col_x, cur_y, col_w, 32), idx))

        self.controls_reset_rect = pygame.Rect(panel_x + 50, panel_rect.bottom - 58, 340, 44)
        self.sub_back_rect = pygame.Rect(panel_x + panel_w - 390, panel_rect.bottom - 58, 340, 44)
        self.touch_editor_btn_rect = pygame.Rect(cx - 200, start_y + 7 * row_h + 8, 400, 34)

        # 3. Subtela Audiovisual
        audio_center_w = 720
        audio_x = cx - audio_center_w // 2
        self.sfx_minus_rect = pygame.Rect(audio_x + 400, panel_y + 140, 36, 32)
        self.sfx_bar_rect = pygame.Rect(audio_x + 448, panel_y + 144, 210, 24)
        self.sfx_plus_rect = pygame.Rect(audio_x + 670, panel_y + 140, 36, 32)

        self.bgm_minus_rect = pygame.Rect(audio_x + 400, panel_y + 220, 36, 32)
        self.bgm_bar_rect = pygame.Rect(audio_x + 448, panel_y + 224, 210, 24)
        self.bgm_plus_rect = pygame.Rect(audio_x + 670, panel_y + 220, 36, 32)

        self.quality_toggle_rect = pygame.Rect(audio_x, panel_y + 300, audio_center_w, 50)
        self.ui_mode_toggle_rect = pygame.Rect(audio_x, panel_y + 375, audio_center_w, 50)

        # 4. Subtela Gameplay
        gp_w = 720
        gp_x = cx - gp_w // 2
        self.difficulty_toggle_rect = pygame.Rect(gp_x, panel_y + 130, gp_w, 56)
        self.language_toggle_rect = pygame.Rect(gp_x, panel_y + 210, gp_w, 50)
        self.game_boost_toggle_rect = pygame.Rect(gp_x, panel_y + 280, gp_w, 50)
        self.invert_y_toggle_rect = pygame.Rect(gp_x, panel_y + 350, gp_w, 50)
        self.touch_toggle_rect = pygame.Rect(gp_x, panel_y + 420, gp_w, 50)

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
        """Alterna o Modo Game Boost oficial do macOS e grava em settings.json."""
        import sys
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent
        from src.effects import quality
        new_state = not quality.is_game_boost_enabled()
        quality.set_game_boost(new_state)
        quality.save_video_setting(quality.SETTINGS_PATH, "game_boost", new_state)
        if sys.platform == "darwin" and new_state:
            surf = pygame.display.get_surface()
            if surf and not (surf.get_flags() & pygame.FULLSCREEN):
                try:
                    pygame.display.toggle_fullscreen()
                except Exception:
                    pass
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

    def open(self, subscreen: str = "HUB"):
        self.is_open = True
        self.current_subscreen = subscreen
        self.hub_selected_index = 0
        self.sub_row_index = 0
        self.waiting_for_key_action = None
        self._init_geometry()
        if hasattr(self, "touch_editor"):
            self.touch_editor.close()

    @staticmethod
    def _fit_text(font, text: str, color, max_w: int) -> pygame.Surface:
        """Renderiza o texto, substituindo tags {icon:...} ou encurtando com '...' se exceder a largura máxima."""
        if "{icon:" in text:
            from src.ui.svg_icon_renderer import create_text_with_icons_surface
            h = font.get_height()
            return create_text_with_icons_surface(font, text, color, icon_size=max(16, h - 2))
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
        """Restaura os controles e áudio para o padrão de fábrica e salva."""
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
        """Processa eventos enquanto o menu de configurações está aberto."""
        if not self.is_open:
            return False

        if hasattr(self, "touch_editor") and self.touch_editor.is_open:
            if self.touch_editor.handle_event(event):
                return True
            return True

        from src.input.controller_manager import get_controller_manager, get_dpad_motion_from_event
        ctrl_mgr = get_controller_manager()

        # 1. Se estiver aguardando remapeamento de tecla/botão
        if self.waiting_for_key_action is not None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.waiting_for_key_action = None
                else:
                    self.controls[self.waiting_for_key_action] = event.key
                    self.waiting_for_key_action = None
                    self.save_settings()
                return True
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 1 and not ("DASH" in self.waiting_for_key_action or "CANCEL" in self.waiting_for_key_action):
                    self.waiting_for_key_action = None
                    return True
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
                pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT) if event.type == pygame.FINGERDOWN else event.pos
                mx, my = pos
                # Se clicou em outro botão de remapeamento, muda o alvo diretamente
                clicked_other = False
                for rect, idx in self.button_rects:
                    if rect.collidepoint(mx, my):
                        self.selected_index = idx
                        self.waiting_for_key_action = self.items[idx][0]
                        clicked_other = True
                        break
                if not clicked_other:
                    self.waiting_for_key_action = None
                return True
            return True

        # Extração de movimento direcional universal (D-Pad, Analógico, Teclado)
        motion_x, motion_y = 0, 0
        is_confirm = False
        is_cancel = False

        if event.type == pygame.JOYHATMOTION:
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                motion_x, motion_y = d_dir
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
                val = -event.value if getattr(ctrl_mgr, "invert_y", False) else event.value
                if val > 0.55 and not self._axis_y_held:
                    motion_y = 1
                    self._axis_y_held = True
                elif val < -0.55 and not self._axis_y_held:
                    motion_y = -1
                    self._axis_y_held = True
                elif abs(val) < 0.25:
                    self._axis_y_held = False
            elif event.axis == 0:
                val = event.value
                if val > 0.55 and not self._axis_x_held:
                    motion_x = 1
                    self._axis_x_held = True
                elif val < -0.55 and not self._axis_x_held:
                    motion_x = -1
                    self._axis_x_held = True
                elif abs(val) < 0.25:
                    self._axis_x_held = False
        elif event.type == pygame.JOYBUTTONDOWN:
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                motion_x, motion_y = d_dir
            if ctrl_mgr.is_event_menu_confirm(event) or event.button in (0, 2):
                is_confirm = True
            elif ctrl_mgr.is_event_menu_cancel(event) or event.button == 1:
                is_cancel = True

        # 2. Navegação no HUB CENTRAL
        if self.current_subscreen == "HUB":
            if motion_y != 0:
                self.hub_selected_index ^= 2
                return True
            elif motion_x != 0:
                self.hub_selected_index ^= 1
                return True

            if is_confirm:
                self._activate_hub_index(self.hub_selected_index)
                return True
            elif is_cancel:
                self.close()
                return True

            # Teclado no HUB
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_c):
                    self.close()
                    return True
                elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    self.hub_selected_index ^= 2
                    return True
                elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                    self.hub_selected_index ^= 1
                    return True
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._activate_hub_index(self.hub_selected_index)
                    return True

            # Mouse / Toque no HUB
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT) if event.type == pygame.FINGERDOWN else event.pos
                mx, my = pos
                for idx, (card_r, cat_name) in enumerate(self.hub_cards_rects):
                    if card_r.collidepoint(mx, my):
                        self.hub_selected_index = idx
                        self._activate_hub_index(idx)
                        return True
                if self.reset_rect.collidepoint(mx, my):
                    self.reset_to_defaults()
                    return True
                elif self.close_rect.collidepoint(mx, my):
                    self.close()
                    return True
                # Compatibilidade com testes diretos headless
                elif self.language_toggle_rect.collidepoint(mx, my):
                    self.cycle_language()
                    return True

        # 3. Subtela AUDIOVISUAL
        elif self.current_subscreen == "AUDIOVISUAL":
            if is_cancel:
                self.current_subscreen = "HUB"
                return True

            # Navegação vertical por linhas: 0: SFX, 1: BGM, 2: Qualidade, 3: Modo UI
            if motion_y != 0:
                self.sub_row_index = (self.sub_row_index + motion_y) % 4
                return True

            if motion_x < 0:
                if self.sub_row_index == 0: self.adjust_sfx_volume(-0.1)
                elif self.sub_row_index == 1: self.adjust_bgm_volume(-0.1)
                elif self.sub_row_index == 2: self.cycle_effects_quality()
                elif self.sub_row_index == 3: self.cycle_ui_mode()
                return True
            elif motion_x > 0:
                if self.sub_row_index == 0: self.adjust_sfx_volume(+0.1)
                elif self.sub_row_index == 1: self.adjust_bgm_volume(+0.1)
                elif self.sub_row_index == 2: self.cycle_effects_quality()
                elif self.sub_row_index == 3: self.cycle_ui_mode()
                return True

            if is_confirm:
                if self.sub_row_index == 0: self.adjust_sfx_volume(+0.1)
                elif self.sub_row_index == 1: self.adjust_bgm_volume(+0.1)
                elif self.sub_row_index == 2: self.cycle_effects_quality()
                elif self.sub_row_index == 3: self.cycle_ui_mode()
                return True

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_c):
                    self.current_subscreen = "HUB"
                    return True
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.sub_row_index = (self.sub_row_index - 1) % 4; return True
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.sub_row_index = (self.sub_row_index + 1) % 4; return True
                elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_MINUS, pygame.K_KP_MINUS, pygame.K_LEFTBRACKET):
                    if self.sub_row_index == 0: self.adjust_sfx_volume(-0.1)
                    elif self.sub_row_index == 1: self.adjust_bgm_volume(-0.1)
                    elif self.sub_row_index == 2: self.cycle_effects_quality()
                    elif self.sub_row_index == 3: self.cycle_ui_mode()
                    return True
                elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_RIGHTBRACKET):
                    if self.sub_row_index == 0: self.adjust_sfx_volume(+0.1)
                    elif self.sub_row_index == 1: self.adjust_bgm_volume(+0.1)
                    elif self.sub_row_index == 2: self.cycle_effects_quality()
                    elif self.sub_row_index == 3: self.cycle_ui_mode()
                    return True
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.sub_row_index == 2: self.cycle_effects_quality()
                    elif self.sub_row_index == 3: self.cycle_ui_mode()
                    return True
                elif event.key == pygame.K_e:
                    self.cycle_effects_quality(); return True
                elif event.key == pygame.K_u:
                    self.cycle_ui_mode(); return True

            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT) if event.type == pygame.FINGERDOWN else event.pos
                mx, my = pos
                if self.sub_back_rect.collidepoint(mx, my):
                    self.current_subscreen = "HUB"
                    return True
                elif self.sfx_minus_rect.collidepoint(mx, my):
                    self.sub_row_index = 0
                    self.adjust_sfx_volume(-0.1)
                    return True
                elif self.sfx_plus_rect.collidepoint(mx, my):
                    self.sub_row_index = 0
                    self.adjust_sfx_volume(+0.1)
                    return True
                elif self.sfx_bar_rect.collidepoint(mx, my):
                    self.sub_row_index = 0
                    pct = max(0.0, min(1.0, (mx - self.sfx_bar_rect.x) / max(1, self.sfx_bar_rect.width)))
                    from src.audio.sound_manager import SoundManager
                    from src.audio.sound_events import SoundEvent
                    mgr = SoundManager.get_instance()
                    mgr.set_sfx_volume(round(pct, 2))
                    mgr.play(SoundEvent.MENU_SELECT)
                    self.save_settings()
                    return True
                elif self.bgm_minus_rect.collidepoint(mx, my):
                    self.sub_row_index = 1
                    self.adjust_bgm_volume(-0.1)
                    return True
                elif self.bgm_plus_rect.collidepoint(mx, my):
                    self.sub_row_index = 1
                    self.adjust_bgm_volume(+0.1)
                    return True
                elif self.bgm_bar_rect.collidepoint(mx, my):
                    self.sub_row_index = 1
                    pct = max(0.0, min(1.0, (mx - self.bgm_bar_rect.x) / max(1, self.bgm_bar_rect.width)))
                    from src.audio.sound_manager import SoundManager
                    mgr = SoundManager.get_instance()
                    mgr.set_bgm_volume(round(pct, 2))
                    self.save_settings()
                    return True
                elif self.quality_toggle_rect.collidepoint(mx, my):
                    self.sub_row_index = 2
                    self.cycle_effects_quality()
                    return True
                elif self.ui_mode_toggle_rect.collidepoint(mx, my):
                    self.sub_row_index = 3
                    self.cycle_ui_mode()
                    return True

            elif event.type == pygame.MOUSEMOTION and (event.buttons[0] == 1 if hasattr(event, "buttons") and len(event.buttons) > 0 else False):
                mx, my = event.pos
                if self.sfx_bar_rect.collidepoint(mx, my):
                    pct = max(0.0, min(1.0, (mx - self.sfx_bar_rect.x) / max(1, self.sfx_bar_rect.width)))
                    from src.audio.sound_manager import SoundManager
                    mgr = SoundManager.get_instance()
                    mgr.set_sfx_volume(round(pct, 2))
                    self.save_settings()
                    return True
                elif self.bgm_bar_rect.collidepoint(mx, my):
                    pct = max(0.0, min(1.0, (mx - self.bgm_bar_rect.x) / max(1, self.bgm_bar_rect.width)))
                    from src.audio.sound_manager import SoundManager
                    mgr = SoundManager.get_instance()
                    mgr.set_bgm_volume(round(pct, 2))
                    self.save_settings()
                    return True

        # 4. Subtela GAMEPLAY
        elif self.current_subscreen == "GAMEPLAY":
            if is_cancel:
                self.current_subscreen = "HUB"
                return True

            # 5 Linhas: 0: Dificuldade IA, 1: Idioma, 2: Boost 60 FPS, 3: Inverter Y, 4: Controles de Toque
            if motion_y != 0:
                self.sub_row_index = (self.sub_row_index + motion_y) % 5
                return True

            if motion_x != 0 or is_confirm:
                if self.sub_row_index == 0: self.cycle_ai_difficulty()
                elif self.sub_row_index == 1: self.cycle_language()
                elif self.sub_row_index == 2: self.toggle_game_boost()
                elif self.sub_row_index == 3: self.toggle_invert_y()
                elif self.sub_row_index == 4: self.cycle_touch_mode()
                return True

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_c):
                    self.current_subscreen = "HUB"
                    return True
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.sub_row_index = (self.sub_row_index - 1) % 5; return True
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.sub_row_index = (self.sub_row_index + 1) % 5; return True
                elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN, pygame.K_SPACE):
                    if self.sub_row_index == 0: self.cycle_ai_difficulty()
                    elif self.sub_row_index == 1: self.cycle_language()
                    elif self.sub_row_index == 2: self.toggle_game_boost()
                    elif self.sub_row_index == 3: self.toggle_invert_y()
                    elif self.sub_row_index == 4: self.cycle_touch_mode()
                    return True
                elif event.key == pygame.K_g:
                    self.cycle_ai_difficulty(); return True
                elif event.key == pygame.K_l:
                    self.cycle_language(); return True
                elif event.key == pygame.K_b:
                    self.toggle_game_boost(); return True

            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT) if event.type == pygame.FINGERDOWN else event.pos
                mx, my = pos
                if self.sub_back_rect.collidepoint(mx, my):
                    self.current_subscreen = "HUB"
                    return True
                elif self.difficulty_toggle_rect.collidepoint(mx, my):
                    self.sub_row_index = 0
                    self.cycle_ai_difficulty()
                    return True
                elif self.language_toggle_rect.collidepoint(mx, my):
                    self.sub_row_index = 1
                    self.cycle_language()
                    return True
                elif self.game_boost_toggle_rect.collidepoint(mx, my):
                    self.sub_row_index = 2
                    self.toggle_game_boost()
                    return True
                elif self.invert_y_toggle_rect.collidepoint(mx, my):
                    self.sub_row_index = 3
                    self.toggle_invert_y()
                    return True
                elif self.touch_toggle_rect.collidepoint(mx, my):
                    self.sub_row_index = 4
                    self.cycle_touch_mode()
                    return True

        # 5. Subtela CONTROLS
        elif self.current_subscreen == "CONTROLS":
            if is_cancel:
                self.current_subscreen = "HUB"
                return True

            if motion_y != 0:
                self.selected_index = (self.selected_index + motion_y) % len(self.items)
                return True
            elif motion_x < 0 and self.selected_index >= 7:
                self.selected_index -= 7
                return True
            elif motion_x > 0 and self.selected_index < 7:
                self.selected_index += 7
                return True

            if is_confirm:
                action_key, _, _ = self.items[self.selected_index]
                self.waiting_for_key_action = action_key
                return True

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_c):
                    self.current_subscreen = "HUB"
                    return True
                elif event.key == pygame.K_1:
                    self.cycle_p1_controller(+1); return True
                elif event.key == pygame.K_2:
                    self.cycle_p2_controller(+1); return True
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_index = (self.selected_index - 1) % len(self.items); return True
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_index = (self.selected_index + 1) % len(self.items); return True
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if self.selected_index >= 7: self.selected_index -= 7
                    return True
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if self.selected_index < 7: self.selected_index += 7
                    return True
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    action_key, _, _ = self.items[self.selected_index]
                    self.waiting_for_key_action = action_key; return True

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 4:
                    self.cycle_p1_controller(+1); return True
                elif event.button == 5:
                    self.cycle_p2_controller(+1); return True

            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT) if event.type == pygame.FINGERDOWN else event.pos
                mx, my = pos
                if self.sub_back_rect.collidepoint(mx, my):
                    self.current_subscreen = "HUB"
                    return True
                elif self.controls_reset_rect.collidepoint(mx, my):
                    self.reset_to_defaults()
                    return True
                elif self.p1_controller_prev_rect.collidepoint(mx, my):
                    self.cycle_p1_controller(-1); return True
                elif self.p1_controller_next_rect.collidepoint(mx, my) or self.p1_controller_box_rect.collidepoint(mx, my):
                    self.cycle_p1_controller(+1); return True
                elif self.p2_controller_prev_rect.collidepoint(mx, my):
                    self.cycle_p2_controller(-1); return True
                elif self.p2_controller_next_rect.collidepoint(mx, my) or self.p2_controller_box_rect.collidepoint(mx, my):
                    self.cycle_p2_controller(+1); return True
                elif self.touch_editor_btn_rect.collidepoint(mx, my):
                    self.touch_editor.open(); return True

                for rect, idx in self.button_rects:
                    if rect.collidepoint(mx, my):
                        self.selected_index = idx
                        action_key, _, _ = self.items[idx]
                        self.waiting_for_key_action = action_key
                        return True

        # Fallback universal para layout mobile puro
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT) if event.type == pygame.FINGERDOWN else event.pos
            mx, my = pos
            if self.close_rect.collidepoint(mx, my):
                self.close(); return True
            elif self.reset_rect.collidepoint(mx, my):
                self.reset_to_defaults(); return True

        # Tecla L de idioma em qualquer tela (compatibilidade de teste)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            self.cycle_language()
            return True

        return True

    def _activate_hub_index(self, idx: int):
        """Ativa a opção do Hub selecionada."""
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent
        if idx == 0:
            self.current_subscreen = "AUDIOVISUAL"
            SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
        elif idx == 1:
            self.current_subscreen = "GAMEPLAY"
            SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
        elif idx == 2:
            self.current_subscreen = "CONTROLS"
            SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
        elif idx == 3:
            from src.edition import is_demo
            if is_demo():
                SoundManager.get_instance().play(SoundEvent.UI_CANCEL)
                return
            from src.arcade import arcade_save
            if arcade_save.is_gallery_unlocked(arcade_save.load()):
                SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                self.request_gallery = True
                self.close()
            else:
                SoundManager.get_instance().play(SoundEvent.UI_CANCEL)

    def update(self, dt: float):
        if self.is_open:
            self.blink_timer += dt

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

    def _render_parchment(self, surface: pygame.Surface, font_large, font_mid, font_small, ctrl_mgr):
        from src.effects import parchment as pm

        # 1. Overlay escuro suave
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 8, 6, 185))
        surface.blit(overlay, (0, 0))

        # 2. Pergaminho Central em Papel Sumi-E Envelhecido
        panel_w, panel_h = 980, 650
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 10
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        paper = pm.make_paper(panel_w, panel_h, seed=61, ragged=(False, False, True, True), burn=0.25)
        surface.blit(pm._soft_shadow(paper, blur=8, opacity=130), (panel_x + 3, panel_y + 5))
        surface.blit(paper, (panel_x, panel_y))

        # Varas de madeira
        pm.draw_rod(surface, "top", panel_rect.centerx, panel_rect.y - 14, panel_w + 32)
        pm.draw_rod(surface, "bottom", panel_rect.centerx, panel_rect.bottom - 22, panel_w + 32)

        # Despacho por subtela
        if self.current_subscreen == "HUB":
            self._render_hub_content(surface, panel_rect, font_large, font_mid, font_small, ctrl_mgr, is_parchment=True)
        elif self.current_subscreen == "AUDIOVISUAL":
            self._render_audiovisual_content(surface, panel_rect, font_large, font_mid, font_small, is_parchment=True)
        elif self.current_subscreen == "GAMEPLAY":
            self._render_gameplay_content(surface, panel_rect, font_large, font_mid, font_small, is_parchment=True)
        elif self.current_subscreen == "CONTROLS":
            self._render_controls_content(surface, panel_rect, font_large, font_mid, font_small, ctrl_mgr, is_parchment=True)

    def _render_fallback(self, surface: pygame.Surface, font_large, font_mid, font_small, ctrl_mgr):
        # 1. Overlay escuro
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 14, 12, 210))
        surface.blit(overlay, (0, 0))

        # 2. Painel Central em Madeira Laqueada e Dourado
        panel_w, panel_h = 980, 650
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 10
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        pygame.draw.rect(surface, (45, 43, 40), panel_rect, border_radius=12)
        pygame.draw.rect(surface, (212, 175, 55), panel_rect, 2, border_radius=12)
        pygame.draw.rect(surface, (65, 60, 52), panel_rect.inflate(-8, -8), 1, border_radius=8)

        if self.current_subscreen == "HUB":
            self._render_hub_content(surface, panel_rect, font_large, font_mid, font_small, ctrl_mgr, is_parchment=False)
        elif self.current_subscreen == "AUDIOVISUAL":
            self._render_audiovisual_content(surface, panel_rect, font_large, font_mid, font_small, is_parchment=False)
        elif self.current_subscreen == "GAMEPLAY":
            self._render_gameplay_content(surface, panel_rect, font_large, font_mid, font_small, is_parchment=False)
        elif self.current_subscreen == "CONTROLS":
            self._render_controls_content(surface, panel_rect, font_large, font_mid, font_small, ctrl_mgr, is_parchment=False)

    def _render_hub_content(self, surface, panel_rect, font_large, font_mid, font_small, ctrl_mgr, is_parchment: bool):
        from src.effects import parchment as pm
        from src.audio.sound_manager import SoundManager
        from src.effects import quality
        from src.arcade import arcade_save
        from src.i18n import get_saved_language_preference, LANG_AUTO, LANG_PT

        mgr = SoundManager.get_instance()
        unlocked = arcade_save.is_gallery_unlocked(arcade_save.load())
        mouse_pos = pygame.mouse.get_pos()

        # Cabeçalho
        t_col = pm.INK if is_parchment else (212, 175, 55)
        title_surf = font_large.render(t("settings_hub_title"), True, t_col)
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2, panel_rect.y + 28))

        sub_col = pm.INK_SOFT if is_parchment else (180, 175, 165)
        sub_surf = font_small.render(t("settings_hub_subtitle"), True, sub_col)
        surface.blit(sub_surf, (panel_rect.centerx - sub_surf.get_width() // 2, panel_rect.y + 68))

        # Sumários de Status para as Tabuletas
        q_str = t("quality_high") if quality.is_high() else t("quality_low")
        diff_names = {"easy": t("difficulty_easy"), "normal": t("difficulty_normal"), "hard": t("difficulty_hard")}
        d_name = diff_names.get(self.ai_difficulty, t("difficulty_normal"))
        pref = get_saved_language_preference()
        lang_str = t("lang_auto") if pref == LANG_AUTO else (t("lang_pt") if pref == LANG_PT else t("lang_en"))
        boost_str = t("status_on") if quality.is_game_boost_enabled() else t("status_off")
        p1_name = ctrl_mgr.get_player_controller_name(0) if ctrl_mgr else "P1"
        p2_name = ctrl_mgr.get_player_controller_name(1) if ctrl_mgr else "P2"

        cards_data = [
            (
                self.hub_audiovisual_rect,
                t("settings_hub_audiovisual_title"),
                t("settings_hub_audiovisual_desc"),
                f"BGM: {int(mgr.bgm_volume * 100)}%   SFX: {int(mgr.sfx_volume * 100)}%   Qualidade: {q_str}",
                True,
            ),
            (
                self.hub_gameplay_rect,
                t("settings_hub_gameplay_title"),
                t("settings_hub_gameplay_desc"),
                f"IA: {d_name}   Idioma: {lang_str}   Boost: {boost_str}",
                True,
            ),
            (
                self.hub_controls_rect,
                t("settings_hub_controls_title"),
                t("settings_hub_controls_desc"),
                f"P1: {p1_name}   P2: {p2_name}",
                True,
            ),
            (
                self.gallery_btn_rect,
                t("settings_hub_gallery_title"),
                t("settings_hub_gallery_desc"),
                t("demo_locked_sub") if is_demo() else (t("gallery_btn_label") if unlocked else t("gallery_locked_label")),
                False if is_demo() else unlocked,
            ),
        ]

        # Renderização dos 4 Cards Kanban
        for idx, (cr, c_title, c_desc, c_status, is_avail) in enumerate(cards_data):
            is_hover = cr.collidepoint(mouse_pos)
            is_sel = (self.hub_selected_index == idx) or is_hover

            if is_parchment:
                bg_col = (238, 226, 202) if is_sel else (226, 212, 185)
                border_col = pm.SEAL_RED if is_sel else (160, 145, 125)
                head_col = pm.SEAL_RED if is_sel else pm.INK
                body_col = pm.INK_SOFT
                stat_col = (180, 130, 45) if is_avail else (140, 125, 115)
            else:
                bg_col = (52, 48, 44) if is_sel else (38, 36, 34)
                border_col = (212, 175, 55) if is_sel else (75, 70, 62)
                head_col = (212, 175, 55) if is_sel else COLOR_WHITE
                body_col = (180, 175, 165)
                stat_col = (110, 225, 140) if is_avail else (160, 140, 130)

            pygame.draw.rect(surface, bg_col, cr, border_radius=8)
            pygame.draw.rect(surface, border_col, cr, 2 if is_sel else 1, border_radius=8)

            # Filete decorativo superior do card
            pygame.draw.line(surface, border_col, (cr.x + 14, cr.y + 44), (cr.right - 14, cr.y + 44), 1)

            t_card = font_mid.render(c_title, True, head_col)
            surface.blit(t_card, (cr.x + 18, cr.y + 14))

            d_card = font_small.render(c_desc, True, body_col)
            surface.blit(d_card, (cr.x + 18, cr.y + 56))

            s_card = font_small.render(c_status, True, stat_col)
            surface.blit(s_card, (cr.x + 18, cr.bottom - 34))

        # Rodapé: Restaurar Padrões à esquerda, Voltar ao Menu Principal à direita
        pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (40, 36, 32), self.reset_rect, border_radius=6)
        pygame.draw.rect(surface, (150, 135, 115) if is_parchment else (80, 75, 65), self.reset_rect, 1, border_radius=6)
        rst_surf = self._fit_text(font_small, t("reset_defaults_hint"), pm.INK if is_parchment else (220, 210, 160), 320)
        surface.blit(rst_surf, rst_surf.get_rect(center=self.reset_rect.center))

        pygame.draw.rect(surface, pm.SEAL_RED if is_parchment else (50, 65, 55), self.close_rect, border_radius=8)
        pygame.draw.rect(surface, (212, 175, 55), self.close_rect, 2, border_radius=8)
        cls_surf = self._fit_text(font_mid, t("settings_return_button"), COLOR_WHITE if is_parchment else COLOR_GOLD, 320)
        surface.blit(cls_surf, cls_surf.get_rect(center=self.close_rect.center))

    def _render_audiovisual_content(self, surface, panel_rect, font_large, font_mid, font_small, is_parchment: bool):
        from src.effects import parchment as pm
        from src.audio.sound_manager import SoundManager
        from src.effects import quality
        mgr = SoundManager.get_instance()

        t_col = pm.INK if is_parchment else (212, 175, 55)
        title_surf = font_large.render(t("settings_sub_audiovisual_title"), True, t_col)
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2, panel_rect.y + 28))

        sub_col = pm.INK_SOFT if is_parchment else (180, 175, 165)
        sub_surf = font_small.render(t("settings_hub_audiovisual_desc"), True, sub_col)
        surface.blit(sub_surf, (panel_rect.centerx - sub_surf.get_width() // 2, panel_rect.y + 68))

        # 1. Slider SFX
        sfx_title = font_mid.render(t('sfx_volume_label'), True, pm.SEAL_RED if (self.sub_row_index == 0 and is_parchment) else ((255, 225, 90) if self.sub_row_index == 0 else t_col))
        surface.blit(sfx_title, (self.sfx_minus_rect.x - 290, self.sfx_minus_rect.y + 4))

        sfx_pct_surf = font_mid.render(f"{int(mgr.sfx_volume * 100)}%", True, pm.SEAL_RED if (self.sub_row_index == 0 and is_parchment) else (pm.INK if is_parchment else COLOR_WHITE))
        surface.blit(sfx_pct_surf, (self.sfx_plus_rect.right + 14, self.sfx_plus_rect.y + 4))

        if self.sub_row_index == 0:
            glow_r = self.sfx_bar_rect.inflate(8, 8)
            pygame.draw.rect(surface, pm.SEAL_RED if is_parchment else (255, 215, 60), glow_r, 2, border_radius=6)

        for btn_r, symb in ((self.sfx_minus_rect, "-"), (self.sfx_plus_rect, "+")):
            pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (36, 42, 38), btn_r, border_radius=6)
            pygame.draw.rect(surface, (140, 125, 105) if is_parchment else COLOR_GOLD, btn_r, 1, border_radius=6)
            t_s = font_mid.render(symb, True, pm.INK if is_parchment else COLOR_GOLD)
            surface.blit(t_s, t_s.get_rect(center=btn_r.center))

        pygame.draw.rect(surface, (195, 180, 152) if is_parchment else (24, 28, 26), self.sfx_bar_rect, border_radius=4)
        fill_sfx = int(self.sfx_bar_rect.width * mgr.sfx_volume)
        if fill_sfx > 0:
            pygame.draw.rect(surface, (170, 125, 45) if is_parchment else (110, 225, 140), (self.sfx_bar_rect.x, self.sfx_bar_rect.y, fill_sfx, self.sfx_bar_rect.height), border_radius=4)
        pygame.draw.rect(surface, (140, 125, 105) if is_parchment else COLOR_GOLD, self.sfx_bar_rect, 1, border_radius=4)

        # 2. Slider BGM
        bgm_title = font_mid.render(t('bgm_volume_label'), True, pm.SEAL_RED if (self.sub_row_index == 1 and is_parchment) else ((255, 225, 90) if self.sub_row_index == 1 else t_col))
        surface.blit(bgm_title, (self.bgm_minus_rect.x - 290, self.bgm_minus_rect.y + 4))

        bgm_pct_surf = font_mid.render(f"{int(mgr.bgm_volume * 100)}%", True, pm.SEAL_RED if (self.sub_row_index == 1 and is_parchment) else (pm.INK if is_parchment else COLOR_WHITE))
        surface.blit(bgm_pct_surf, (self.bgm_plus_rect.right + 14, self.bgm_plus_rect.y + 4))

        if self.sub_row_index == 1:
            glow_r = self.bgm_bar_rect.inflate(8, 8)
            pygame.draw.rect(surface, pm.SEAL_RED if is_parchment else (255, 215, 60), glow_r, 2, border_radius=6)

        for btn_r, symb in ((self.bgm_minus_rect, "-"), (self.bgm_plus_rect, "+")):
            pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (36, 42, 38), btn_r, border_radius=6)
            pygame.draw.rect(surface, (140, 125, 105) if is_parchment else COLOR_GOLD, btn_r, 1, border_radius=6)
            t_s = font_mid.render(symb, True, pm.INK if is_parchment else COLOR_GOLD)
            surface.blit(t_s, t_s.get_rect(center=btn_r.center))

        pygame.draw.rect(surface, (195, 180, 152) if is_parchment else (24, 28, 26), self.bgm_bar_rect, border_radius=4)
        fill_bgm = int(self.bgm_bar_rect.width * mgr.bgm_volume)
        if fill_bgm > 0:
            pygame.draw.rect(surface, (70, 125, 95) if is_parchment else (110, 225, 140), (self.bgm_bar_rect.x, self.bgm_bar_rect.y, fill_bgm, self.bgm_bar_rect.height), border_radius=4)
        pygame.draw.rect(surface, (140, 125, 105) if is_parchment else COLOR_GOLD, self.bgm_bar_rect, 1, border_radius=4)

        # 3. Qualidade Gráfica
        high = quality.is_high()
        q_label = t("effects_quality_label").format(q_name=t("quality_high") if high else t("quality_low"))
        q_sub = "Alta: SSAA 2x Voxel + Sombra Realista" if high else "Baixa: Renderização Otimizada 60 FPS"
        pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (38, 36, 34), self.quality_toggle_rect, border_radius=8)
        q_border = pm.SEAL_RED if (self.sub_row_index == 2 and is_parchment) else ((255, 215, 60) if self.sub_row_index == 2 else ((170, 125, 45) if is_parchment else COLOR_GOLD))
        pygame.draw.rect(surface, q_border, self.quality_toggle_rect, 3 if self.sub_row_index == 2 else (2 if high else 1), border_radius=8)
        ql = font_mid.render(q_label, True, pm.SEAL_RED if (self.sub_row_index == 2 and is_parchment) else (pm.INK if is_parchment else COLOR_GOLD))
        qs = font_small.render(q_sub, True, pm.INK_SOFT if is_parchment else (180, 175, 165))
        surface.blit(ql, (self.quality_toggle_rect.x + 24, self.quality_toggle_rect.y + 6))
        surface.blit(qs, (self.quality_toggle_rect.x + 24, self.quality_toggle_rect.y + 28))

        # 4. Modo da Interface
        ui_mode = get_saved_ui_mode()
        ui_mode_names = {"auto": "AUTOMÁTICO", "mobile": "SMARTPHONE", "classic": "CLÁSSICO"}
        u_name = ui_mode_names.get(ui_mode, "AUTOMÁTICO")
        pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (38, 36, 34), self.ui_mode_toggle_rect, border_radius=8)
        u_border = pm.SEAL_RED if (self.sub_row_index == 3 and is_parchment) else ((255, 215, 60) if self.sub_row_index == 3 else ((140, 125, 105) if is_parchment else (75, 70, 62)))
        pygame.draw.rect(surface, u_border, self.ui_mode_toggle_rect, 3 if self.sub_row_index == 3 else 1, border_radius=8)
        ul = font_mid.render(f"LAYOUT DA INTERFACE: [ {u_name} ]", True, pm.SEAL_RED if (self.sub_row_index == 3 and is_parchment) else (pm.INK if is_parchment else COLOR_WHITE))
        surface.blit(ul, ul.get_rect(center=self.ui_mode_toggle_rect.center))

        # Botão Voltar às Opções
        pygame.draw.rect(surface, pm.SEAL_RED if is_parchment else (50, 65, 55), self.sub_back_rect, border_radius=8)
        pygame.draw.rect(surface, (212, 175, 55), self.sub_back_rect, 2, border_radius=8)
        b_surf = self._fit_text(font_mid, t("settings_sub_back_btn"), COLOR_WHITE if is_parchment else COLOR_GOLD, 320)
        surface.blit(b_surf, b_surf.get_rect(center=self.sub_back_rect.center))

    def _render_gameplay_content(self, surface, panel_rect, font_large, font_mid, font_small, is_parchment: bool):
        from src.effects import parchment as pm
        from src.effects import quality
        from src.i18n import get_saved_language_preference, get_lang, LANG_AUTO, LANG_PT, LANG_EN

        t_col = pm.INK if is_parchment else (212, 175, 55)
        title_surf = font_large.render(t("settings_sub_gameplay_title"), True, t_col)
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2, panel_rect.y + 28))

        sub_col = pm.INK_SOFT if is_parchment else (180, 175, 165)
        sub_surf = font_small.render(t("settings_hub_gameplay_desc"), True, sub_col)
        surface.blit(sub_surf, (panel_rect.centerx - sub_surf.get_width() // 2, panel_rect.y + 68))

        # 1. Dificuldade da IA
        diff_names = {"easy": t("difficulty_easy"), "normal": t("difficulty_normal"), "hard": t("difficulty_hard")}
        diff_colors = {"easy": (45, 140, 65), "normal": (170, 125, 45), "hard": pm.SEAL_RED}
        d_name = diff_names.get(self.ai_difficulty, t("difficulty_normal"))
        d_col = diff_colors.get(self.ai_difficulty, (170, 125, 45))
        if get_lang() == LANG_EN:
            d_desc = "Easy: Cautious opponents" if self.ai_difficulty == "easy" else (
                "Normal: Balanced combat intensity" if self.ai_difficulty == "normal" else "Hard: Relentless AI and razor-sharp reflexes"
            )
        else:
            d_desc = "Fácil: Inimigos mais cautelosos" if self.ai_difficulty == "easy" else (
                "Normal: Equilíbrio padrão de combate" if self.ai_difficulty == "normal" else "Difícil: IA implacável e reflexos afiados"
            )

        pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (38, 36, 34), self.difficulty_toggle_rect, border_radius=8)
        d_border = pm.SEAL_RED if (self.sub_row_index == 0 and is_parchment) else ((255, 215, 60) if self.sub_row_index == 0 else d_col)
        pygame.draw.rect(surface, d_border, self.difficulty_toggle_rect, 3 if self.sub_row_index == 0 else 2, border_radius=8)
        dl = self._fit_text(font_mid, t("ai_difficulty_label").format(d_name=d_name), d_border if self.sub_row_index == 0 else d_col, self.difficulty_toggle_rect.width - 48)
        ds = self._fit_text(font_small, d_desc, pm.INK_SOFT if is_parchment else (180, 175, 165), self.difficulty_toggle_rect.width - 48)
        surface.blit(dl, (self.difficulty_toggle_rect.x + 24, self.difficulty_toggle_rect.y + 8))
        surface.blit(ds, (self.difficulty_toggle_rect.x + 24, self.difficulty_toggle_rect.y + 32))

        # 2. Idioma
        pref = get_saved_language_preference()
        lang_str = t("lang_auto") if pref == LANG_AUTO else (t("lang_pt") if pref == LANG_PT else t("lang_en"))
        pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (38, 36, 34), self.language_toggle_rect, border_radius=8)
        l_border = pm.SEAL_RED if (self.sub_row_index == 1 and is_parchment) else ((255, 215, 60) if self.sub_row_index == 1 else ((140, 125, 105) if is_parchment else (75, 70, 62)))
        pygame.draw.rect(surface, l_border, self.language_toggle_rect, 3 if self.sub_row_index == 1 else 1, border_radius=8)
        ll = self._fit_text(font_mid, t("language_toggle_label").format(lang_name=lang_str), pm.SEAL_RED if (self.sub_row_index == 1 and is_parchment) else (pm.INK if is_parchment else COLOR_WHITE), self.language_toggle_rect.width - 24)
        surface.blit(ll, ll.get_rect(center=self.language_toggle_rect.center))

        # 3. Game Boost
        boost_on = quality.is_game_boost_enabled()
        b_label = t("game_boost_label").format(status=t("status_on") if boost_on else t("status_off"))
        pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (38, 36, 34), self.game_boost_toggle_rect, border_radius=8)
        b_border = pm.SEAL_RED if (self.sub_row_index == 2 and is_parchment) else ((255, 215, 60) if self.sub_row_index == 2 else ((45, 140, 65) if boost_on else ((140, 125, 105) if is_parchment else (75, 70, 62))))
        pygame.draw.rect(surface, b_border, self.game_boost_toggle_rect, 3 if self.sub_row_index == 2 else (2 if boost_on else 1), border_radius=8)
        bl = self._fit_text(font_mid, b_label, pm.SEAL_RED if (self.sub_row_index == 2 and is_parchment) else ((45, 140, 65) if boost_on else (pm.INK if is_parchment else COLOR_WHITE)), self.game_boost_toggle_rect.width - 24)
        surface.blit(bl, bl.get_rect(center=self.game_boost_toggle_rect.center))

        # 4. Inverter Eixo Y
        from src.input.controller_manager import get_controller_manager
        inv_y = getattr(get_controller_manager(), "invert_y", False)
        inv_name = t("status_on") if inv_y else t("status_off")
        y_txt = f"{t('invert_y_label')}: [ {inv_name} ]" if t("invert_y_label") else (f"Invert Analog Y Axis: [ {inv_name} ]" if get_lang() == LANG_EN else f"Inverter Eixo Y do Analógico: [ {inv_name} ]")
        pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (38, 36, 34), self.invert_y_toggle_rect, border_radius=8)
        y_border = pm.SEAL_RED if (self.sub_row_index == 3 and is_parchment) else ((255, 215, 60) if self.sub_row_index == 3 else ((140, 125, 105) if is_parchment else (75, 70, 62)))
        pygame.draw.rect(surface, y_border, self.invert_y_toggle_rect, 3 if self.sub_row_index == 3 else 1, border_radius=8)
        yl = self._fit_text(font_mid, y_txt, pm.SEAL_RED if (self.sub_row_index == 3 and is_parchment) else (pm.INK if is_parchment else COLOR_WHITE), self.invert_y_toggle_rect.width - 24)
        surface.blit(yl, yl.get_rect(center=self.invert_y_toggle_rect.center))

        # 5. Modo de Toque
        touch_mode_str = t("touch_mode_auto")
        if self.touch_controls:
            mode = getattr(self.touch_controls, "mode", "auto")
            if mode == "always":
                touch_mode_str = t("touch_mode_always_on")
            elif mode == "off":
                touch_mode_str = t("touch_mode_disabled")
        pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (38, 36, 34), self.touch_toggle_rect, border_radius=8)
        t_border = pm.SEAL_RED if (self.sub_row_index == 4 and is_parchment) else ((255, 215, 60) if self.sub_row_index == 4 else ((140, 125, 105) if is_parchment else (75, 70, 62)))
        pygame.draw.rect(surface, t_border, self.touch_toggle_rect, 3 if self.sub_row_index == 4 else 1, border_radius=8)
        tl = self._fit_text(font_mid, t("touch_controls_label").format(touch_mode_str=touch_mode_str), pm.SEAL_RED if (self.sub_row_index == 4 and is_parchment) else (pm.INK if is_parchment else COLOR_WHITE), self.touch_toggle_rect.width - 24)
        surface.blit(tl, tl.get_rect(center=self.touch_toggle_rect.center))

        # Botão Voltar às Opções
        pygame.draw.rect(surface, pm.SEAL_RED if is_parchment else (50, 65, 55), self.sub_back_rect, border_radius=8)
        pygame.draw.rect(surface, (212, 175, 55), self.sub_back_rect, 2, border_radius=8)
        b_surf = self._fit_text(font_mid, t("settings_sub_back_btn"), COLOR_WHITE if is_parchment else COLOR_GOLD, 320)
        surface.blit(b_surf, b_surf.get_rect(center=self.sub_back_rect.center))

    def _render_controls_content(self, surface, panel_rect, font_large, font_mid, font_small, ctrl_mgr, is_parchment: bool):
        from src.effects import parchment as pm
        from src.ui.svg_icon_renderer import get_button_icon_surface

        t_col = pm.INK if is_parchment else (212, 175, 55)
        title_surf = font_large.render(t("settings_sub_controls_title"), True, t_col)
        surface.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2, panel_rect.y + 28))

        sub_col = pm.INK_SOFT if is_parchment else (180, 175, 165)
        sub_surf = font_small.render(t("settings_hub_controls_desc"), True, sub_col)
        surface.blit(sub_surf, (panel_rect.centerx - sub_surf.get_width() // 2, panel_rect.y + 68))

        # Colunas P1 (Vermelho) e P2 (Azul)
        col_w = 430
        col_left_x = panel_rect.x + 30
        col_right_x = panel_rect.x + panel_rect.width - col_w - 30
        start_y = panel_rect.y + 118
        row_h = 40
        box_w = 210

        # Cabeçalhos
        h1 = self._fit_text(font_mid, t("player_1_label"), pm.SEAL_RED if is_parchment else COLOR_RED_AURA, col_w - box_w - 14)
        h2 = self._fit_text(font_mid, t("player_2_label"), pm.SEAL_BLUE if is_parchment else COLOR_BLUE_AURA, col_w - box_w - 14)
        surface.blit(h1, (col_left_x + 6, start_y - 28))
        surface.blit(h2, (col_right_x + 6, start_y - 28))

        # Seletor P1
        p1_ctrl_name = ctrl_mgr.get_player_controller_name(0)
        pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (36, 32, 28), self.p1_controller_box_rect, border_radius=4)
        pygame.draw.rect(surface, pm.SEAL_RED if is_parchment else (160, 75, 75), self.p1_controller_box_rect, 1, border_radius=4)
        arrow_l = font_small.render("<", True, pm.SEAL_RED if is_parchment else (212, 175, 55))
        arrow_r = font_small.render(">", True, pm.SEAL_RED if is_parchment else (212, 175, 55))
        surface.blit(arrow_l, (self.p1_controller_box_rect.x + 6, self.p1_controller_box_rect.y + 3))
        surface.blit(arrow_r, (self.p1_controller_box_rect.right - 14, self.p1_controller_box_rect.y + 3))
        p1_lbl = self._fit_text(font_small, p1_ctrl_name, pm.INK if is_parchment else (230, 225, 215), box_w - 38)
        surface.blit(p1_lbl, (self.p1_controller_box_rect.x + (box_w - p1_lbl.get_width()) // 2, self.p1_controller_box_rect.y + 3))

        # Seletor P2
        p2_ctrl_name = ctrl_mgr.get_player_controller_name(1)
        pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (36, 32, 28), self.p2_controller_box_rect, border_radius=4)
        pygame.draw.rect(surface, pm.SEAL_BLUE if is_parchment else (75, 95, 160), self.p2_controller_box_rect, 1, border_radius=4)
        surface.blit(arrow_l, (self.p2_controller_box_rect.x + 6, self.p2_controller_box_rect.y + 3))
        surface.blit(arrow_r, (self.p2_controller_box_rect.right - 14, self.p2_controller_box_rect.y + 3))
        p2_lbl = self._fit_text(font_small, p2_ctrl_name, pm.INK if is_parchment else (230, 225, 215), box_w - 38)
        surface.blit(p2_lbl, (self.p2_controller_box_rect.x + (box_w - p2_lbl.get_width()) // 2, self.p2_controller_box_rect.y + 3))

        # Linhas de Remapeamento (7 de cada lado)
        for btn_rect, idx in self.button_rects:
            action_key, default_lbl, faction = self.items[idx]
            is_red = (faction == "red")
            is_sel = (self.selected_index == idx)
            is_waiting = (self.waiting_for_key_action == action_key)

            bg_c = (238, 226, 202) if (is_sel and is_parchment) else ((226, 212, 185) if is_parchment else ((50, 46, 42) if is_sel else (38, 36, 34)))
            bd_c = pm.SEAL_RED if (is_red and is_sel) else (pm.SEAL_BLUE if (not is_red and is_sel) else ((160, 145, 125) if is_parchment else (70, 65, 58)))

            pygame.draw.rect(surface, bg_c, btn_rect, border_radius=4)
            pygame.draw.rect(surface, bd_c, btn_rect, 2 if is_sel else 1, border_radius=4)

            # Rótulo da Ação
            lbl_key = f"settings_action_{action_key.split('_')[1].lower()}"
            lbl_text = t(lbl_key)
            l_surf = self._fit_text(font_small, lbl_text, pm.INK if is_parchment else COLOR_WHITE, 190)
            surface.blit(l_surf, (btn_rect.x + 10, btn_rect.y + 6))

            # Caixa da Tecla / Botão
            kbox_w = 205
            kbox_r = pygame.Rect(btn_rect.right - kbox_w - 6, btn_rect.y + 4, kbox_w, btn_rect.height - 8)
            pygame.draw.rect(surface, (216, 202, 175) if is_parchment else (28, 26, 24), kbox_r, border_radius=4)

            if is_waiting:
                pulse = abs(math.sin(self.blink_timer * 6))
                w_col = (int(200 + 55 * pulse), int(40 + 40 * pulse), 40)
                w_txt = font_small.render(t("settings_press_key"), True, w_col)
                surface.blit(w_txt, w_txt.get_rect(center=kbox_r.center))
            else:
                key_code = self.controls.get(action_key, 0)
                k_name = format_key_name(key_code)

                p_idx = 0 if is_red else 1
                ctrl = ctrl_mgr.get_controller_for_player(p_idx)
                act_suffix = "attack" if "ATTACK" in action_key else (
                    "dash" if "DASH" in action_key else (
                        "secondary" if ("SECONDARY" in action_key or "PARRY" in action_key) else None
                    )
                )

                svg_icon_name = None
                btn_name = ""
                if ctrl and ctrl.is_playstation:
                    if act_suffix:
                        svg_icon_name = ctrl.get_button_svg_icon(act_suffix)
                        btn_name = ctrl.get_mapped_button_name(act_suffix)
                    else:
                        svg_icon_name = "dpad"
                        btn_name = "D-Pad"
                elif ctrl:
                    if act_suffix:
                        svg_icon_name = ctrl.get_button_svg_icon(act_suffix)
                        btn_name = ctrl.get_mapped_button_name(act_suffix)
                    else:
                        svg_icon_name = "dpad"
                        btn_name = "D-Pad"
                else:
                    if act_suffix == "attack":
                        svg_icon_name = "square"
                    elif act_suffix == "secondary":
                        svg_icon_name = "triangle"
                    elif act_suffix == "dash":
                        svg_icon_name = "circle"
                    else:
                        svg_icon_name = "dpad"

                cur_right_x = kbox_r.right - 6
                if svg_icon_name:
                    icon_surf = get_button_icon_surface(svg_icon_name, 20, 20)
                    cur_right_x -= 22
                    surface.blit(icon_surf, (cur_right_x, kbox_r.y + (kbox_r.height - 20) // 2))

                if btn_name and not (ctrl and ctrl.is_playstation):
                    b_txt = self._fit_text(font_small, f"[{btn_name}]", pm.INK_SOFT if is_parchment else (160, 185, 175), 65)
                    cur_right_x -= (b_txt.get_width() + 4)
                    surface.blit(b_txt, (cur_right_x, kbox_r.y + (kbox_r.height - b_txt.get_height()) // 2))

                key_color = pm.SEAL_RED if (is_red and is_parchment) else (pm.SEAL_BLUE if is_parchment else (COLOR_GOLD if is_sel else (225, 220, 210)))
                kt = self._fit_text(font_small, f"[{k_name}]", key_color, max(50, cur_right_x - kbox_r.x - 4))
                surface.blit(kt, (kbox_r.x + 8, kbox_r.y + (kbox_r.height - kt.get_height()) // 2))

        # Botão Editor de Toque (se houver touch controls)
        if hasattr(self, "touch_controls") and self.touch_controls:
            pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (36, 48, 40), self.touch_editor_btn_rect, border_radius=6)
            pygame.draw.rect(surface, (140, 125, 105) if is_parchment else (212, 175, 55), self.touch_editor_btn_rect, 1, border_radius=6)
            hud_lbl = font_small.render("⚙ PERSONALIZAR BOTÕES TOUCH (HUD)", True, pm.INK if is_parchment else COLOR_GOLD)
            surface.blit(hud_lbl, hud_lbl.get_rect(center=self.touch_editor_btn_rect.center))

        # Rodapé: Restaurar Controles à esquerda, Voltar às Opções à direita
        pygame.draw.rect(surface, (226, 212, 185) if is_parchment else (40, 36, 32), self.controls_reset_rect, border_radius=6)
        pygame.draw.rect(surface, (150, 135, 115) if is_parchment else (80, 75, 65), self.controls_reset_rect, 1, border_radius=6)
        rst_surf = self._fit_text(font_small, t("reset_defaults_hint"), pm.INK if is_parchment else (220, 210, 160), 320)
        surface.blit(rst_surf, rst_surf.get_rect(center=self.controls_reset_rect.center))

        pygame.draw.rect(surface, pm.SEAL_RED if is_parchment else (50, 65, 55), self.sub_back_rect, border_radius=8)
        pygame.draw.rect(surface, (212, 175, 55), self.sub_back_rect, 2, border_radius=8)
        b_surf = self._fit_text(font_mid, t("settings_sub_back_btn"), COLOR_WHITE if is_parchment else COLOR_GOLD, 320)
        surface.blit(b_surf, b_surf.get_rect(center=self.sub_back_rect.center))

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

        # Indicador de detecção de controle físico
        from src.input.controller_manager import get_controller_manager
        c_mgr = get_controller_manager()
        c_mgr.poll_controllers()
        c1 = c_mgr.get_controller_for_player(0)
        if c1:
            badge_txt = font_small.render(f"[{c1.friendly_name.upper()}] CONECTADO", True, (110, 245, 150))
        else:
            badge_txt = font_small.render("[MODO TOUCH SCREEN] Nenhum controle físico conectado", True, (150, 165, 175))
        surface.blit(badge_txt, (panel_rect.centerx - badge_txt.get_width() // 2, panel_y + 78))

        draw_brush_divider(surface, panel_x + 40, panel_y + 102, panel_x + panel_w - 40)

        cy = panel_y + 116
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

        # Dificuldade e Idioma
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
        ui_mode = get_saved_ui_mode()
        ui_mode_names = {"auto": "AUTOMÁTICO", "mobile": "SMARTPHONE", "classic": "CLÁSSICO"}
        u_name = ui_mode_names.get(ui_mode, "AUTOMÁTICO")
        self.ui_mode_toggle_rect = pygame.Rect(panel_rect.centerx - btn_w // 2, cy, btn_w, 42)
        pygame.draw.rect(surface, (28, 36, 32), self.ui_mode_toggle_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, self.ui_mode_toggle_rect, 1, border_radius=8)
        u_lbl = font_mid.render(f"LAYOUT DA INTERFACE: [ {u_name} ]", True, COLOR_GOLD)
        surface.blit(u_lbl, u_lbl.get_rect(center=self.ui_mode_toggle_rect.center))

        cy += 50
        from src.effects import quality
        high = quality.is_high()
        q_col = (110, 225, 140) if high else (245, 190, 85)
        q_label = t("effects_quality_label").format(q_name=t("quality_high") if high else t("quality_low"))

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
        self.touch_editor_btn_rect = pygame.Rect(panel_rect.centerx - btn_w // 2, cy, btn_w, 46)
        pygame.draw.rect(surface, (36, 48, 40), self.touch_editor_btn_rect, border_radius=8)
        pygame.draw.rect(surface, (212, 175, 55), self.touch_editor_btn_rect, 2, border_radius=8)
        hud_lbl = font_mid.render("⚙ PERSONALIZAR BOTÕES TOUCH (HUD)", True, COLOR_GOLD)
        surface.blit(hud_lbl, hud_lbl.get_rect(center=self.touch_editor_btn_rect.center))

        # Rodapé Mobile
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
