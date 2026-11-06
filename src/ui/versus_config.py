import os
import json
import math
import random
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD
from src.i18n import t, get_lang, LANG_PT
from src.audio.sound_events import SoundEvent
from src.audio.sound_manager import SoundManager
from src.effects import parchment as pm
from src.ui.character_select import draw_scroll_frame, draw_brush_divider, draw_hanko_stamp
from src.ui.svg_icon_renderer import render_text_with_icons
from src.ui.fonts import get_title_font, get_text_font

COLOR_BG = (14, 16, 18)
COLOR_TEXT_MAIN = (252, 244, 226)
COLOR_TEXT_MUTED = (160, 155, 150)
COLOR_HANKO_RED = (200, 40, 35)
COLOR_HANKO_BLUE = (40, 110, 200)

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "settings.json")


def load_versus_settings() -> dict:
    defaults = {
        "mode": "pve",       # "pvp", "pve", "watch"
        "rounds_to_win": 2,  # 1 a 10
        "ai_difficulty": "normal"  # "easy", "normal", "hard"
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                vs = data.get("versus", {})
                if isinstance(vs, dict):
                    if vs.get("mode") in ("pvp", "pve", "watch"):
                        defaults["mode"] = vs["mode"]
                    if isinstance(vs.get("rounds_to_win"), int) and 1 <= vs["rounds_to_win"] <= 10:
                        defaults["rounds_to_win"] = vs["rounds_to_win"]
                    if vs.get("ai_difficulty") in ("easy", "normal", "hard"):
                        defaults["ai_difficulty"] = vs["ai_difficulty"]
        except Exception:
            pass
    return defaults


def save_versus_settings(mode: str, rounds_to_win: int, ai_difficulty: str) -> bool:
    data = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    if not isinstance(data, dict):
        data = {}
    data["versus"] = {
        "mode": mode,
        "rounds_to_win": max(1, min(10, rounds_to_win)),
        "ai_difficulty": ai_difficulty if ai_difficulty in ("easy", "normal", "hard") else "normal"
    }
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


class VersusConfigScreen:
    """Submenu Sumi-e cerimonial para configuração do Modo Versus (Modo, Rounds, Dificuldade)."""

    OPT_MODE = 0
    OPT_ROUNDS = 1
    OPT_DIFFICULTY = 2
    OPT_PROCEED = 3
    OPT_BACK = 4

    MODES = ["pve", "pvp", "watch"]
    DIFFICULTIES = ["easy", "normal", "hard"]

    def __init__(self):
        saved = load_versus_settings()
        self.mode: str = saved.get("mode", "pve")
        self.rounds_to_win: int = saved.get("rounds_to_win", 2)
        self.ai_difficulty: str = saved.get("ai_difficulty", "normal")

        self.selected: int = self.OPT_MODE
        self.anim_timer: float = 0.0

        # Debounce de controle
        self._axis_x_held: bool = False
        self._axis_y_held: bool = False

        # Hitboxes interativas para mouse
        self.row_rects: dict[int, pygame.Rect] = {}
        self.arrow_left_rects: dict[int, pygame.Rect] = {}
        self.arrow_right_rects: dict[int, pygame.Rect] = {}
        self.btn_proceed_rect = pygame.Rect(0, 0, 0, 0)
        self.btn_back_rect = pygame.Rect(0, 0, 0, 0)

        # Partículas de nanquim e cinzas
        self.particles = []
        for _ in range(25):
            self.particles.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(0, SCREEN_HEIGHT),
                "speed_x": random.uniform(-0.3, 0.3),
                "speed_y": random.uniform(-0.6, -0.2),
                "size": random.uniform(1.5, 3.0),
                "alpha": random.randint(60, 160)
            })

    def open(self):
        """Abre a tela recarregando as últimas configurações salvas."""
        saved = load_versus_settings()
        self.mode = saved.get("mode", "pve")
        self.rounds_to_win = saved.get("rounds_to_win", 2)
        self.ai_difficulty = saved.get("ai_difficulty", "normal")
        self.selected = self.OPT_MODE
        self._axis_x_held = False
        self._axis_y_held = False

    def update(self, dt: float):
        self.anim_timer += dt
        for p in self.particles:
            p["x"] += p["speed_x"]
            p["y"] += p["speed_y"]
            if p["y"] < -10:
                p["y"] = SCREEN_HEIGHT + 10
                p["x"] = random.uniform(0, SCREEN_WIDTH)

    def _play_sfx(self):
        try:
            SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
        except Exception:
            pass

    def _change_option_value(self, opt_idx: int, direction: int):
        if opt_idx == self.OPT_MODE:
            cur_idx = self.MODES.index(self.mode) if self.mode in self.MODES else 0
            self.mode = self.MODES[(cur_idx + direction) % len(self.MODES)]
            self._play_sfx()
            save_versus_settings(self.mode, self.rounds_to_win, self.ai_difficulty)
        elif opt_idx == self.OPT_ROUNDS:
            new_r = max(1, min(10, self.rounds_to_win + direction))
            if new_r != self.rounds_to_win:
                self.rounds_to_win = new_r
                self._play_sfx()
                save_versus_settings(self.mode, self.rounds_to_win, self.ai_difficulty)
        elif opt_idx == self.OPT_DIFFICULTY:
            if self.mode == "pvp":
                return
            cur_idx = self.DIFFICULTIES.index(self.ai_difficulty) if self.ai_difficulty in self.DIFFICULTIES else 1
            self.ai_difficulty = self.DIFFICULTIES[(cur_idx + direction) % len(self.DIFFICULTIES)]
            self._play_sfx()
            save_versus_settings(self.mode, self.rounds_to_win, self.ai_difficulty)

    def _nav_step(self, step: int):
        nav_options = [self.OPT_MODE, self.OPT_ROUNDS]
        if self.mode != "pvp":
            nav_options.append(self.OPT_DIFFICULTY)
        nav_options.extend([self.OPT_PROCEED, self.OPT_BACK])

        if self.selected not in nav_options:
            self.selected = nav_options[0]
        else:
            cur_i = nav_options.index(self.selected)
            self.selected = nav_options[(cur_i + step) % len(nav_options)]
        self._play_sfx()

    def handle_event(self, event: pygame.event.Event, ctrl_mgr=None) -> str | None:
        """
        Processa eventos do submenu.
        Retorna:
          - "PROCEED": avança para a seleção de lutadores
          - "BACK": volta para o menu principal
          - None: permanece no submenu
        """
        # 1. Mouse
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for opt, rect in self.row_rects.items():
                if rect.collidepoint(mx, my):
                    if opt == self.OPT_DIFFICULTY and self.mode == "pvp":
                        continue
                    self.selected = opt
            if self.btn_proceed_rect.collidepoint(mx, my):
                self.selected = self.OPT_PROCEED
            elif self.btn_back_rect.collidepoint(mx, my):
                self.selected = self.OPT_BACK

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Clique nas setas esquerda/direita
            for opt, r_left in self.arrow_left_rects.items():
                if r_left.collidepoint(mx, my):
                    self.selected = opt
                    self._change_option_value(opt, -1)
                    return None
            for opt, r_right in self.arrow_right_rects.items():
                if r_right.collidepoint(mx, my):
                    self.selected = opt
                    self._change_option_value(opt, 1)
                    return None

            # Clique direto nos botões de ação
            if self.btn_proceed_rect.collidepoint(mx, my):
                self._play_sfx()
                save_versus_settings(self.mode, self.rounds_to_win, self.ai_difficulty)
                return "PROCEED"
            if self.btn_back_rect.collidepoint(mx, my):
                self._play_sfx()
                return "BACK"

            # Clique na própria linha alterna o valor
            for opt, rect in self.row_rects.items():
                if rect.collidepoint(mx, my):
                    if opt == self.OPT_DIFFICULTY and self.mode == "pvp":
                        continue
                    self.selected = opt
                    self._change_option_value(opt, 1)
                    return None

        # 2. Teclado
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,):
                self._play_sfx()
                return "BACK"
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._nav_step(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._nav_step(1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                if self.selected in (self.OPT_MODE, self.OPT_ROUNDS, self.OPT_DIFFICULTY):
                    self._change_option_value(self.selected, -1)
                elif self.selected == self.OPT_BACK:
                    self.selected = self.OPT_PROCEED
                    self._play_sfx()
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if self.selected in (self.OPT_MODE, self.OPT_ROUNDS, self.OPT_DIFFICULTY):
                    self._change_option_value(self.selected, 1)
                elif self.selected == self.OPT_PROCEED:
                    self.selected = self.OPT_BACK
                    self._play_sfx()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if self.selected == self.OPT_BACK:
                    self._play_sfx()
                    return "BACK"
                elif self.selected == self.OPT_PROCEED:
                    self._play_sfx()
                    save_versus_settings(self.mode, self.rounds_to_win, self.ai_difficulty)
                    return "PROCEED"
                elif self.selected in (self.OPT_MODE, self.OPT_ROUNDS, self.OPT_DIFFICULTY):
                    self._change_option_value(self.selected, 1)

        # 3. Gamepad D-Pad & Botões
        elif event.type in (pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION):
            from src.input.controller_manager import get_dpad_motion_from_event
            motion = get_dpad_motion_from_event(event)
            if motion:
                dx, dy = motion
                if dy < 0:
                    self._nav_step(-1)
                elif dy > 0:
                    self._nav_step(1)
                elif dx < 0:
                    if self.selected in (self.OPT_MODE, self.OPT_ROUNDS, self.OPT_DIFFICULTY):
                        self._change_option_value(self.selected, -1)
                    elif self.selected == self.OPT_BACK:
                        self.selected = self.OPT_PROCEED
                        self._play_sfx()
                elif dx > 0:
                    if self.selected in (self.OPT_MODE, self.OPT_ROUNDS, self.OPT_DIFFICULTY):
                        self._change_option_value(self.selected, 1)
                    elif self.selected == self.OPT_PROCEED:
                        self.selected = self.OPT_BACK
                        self._play_sfx()

            if event.type == pygame.JOYBUTTONDOWN:
                is_confirm = (ctrl_mgr is not None and ctrl_mgr.is_event_menu_confirm(event)) or event.button in (0, 2)
                is_cancel = (ctrl_mgr is not None and ctrl_mgr.is_event_menu_cancel(event)) or event.button == 1

                if is_cancel:
                    self._play_sfx()
                    return "BACK"
                elif is_confirm:
                    if self.selected == self.OPT_BACK:
                        self._play_sfx()
                        return "BACK"
                    elif self.selected == self.OPT_PROCEED:
                        self._play_sfx()
                        save_versus_settings(self.mode, self.rounds_to_win, self.ai_difficulty)
                        return "PROCEED"
                    elif self.selected in (self.OPT_MODE, self.OPT_ROUNDS, self.OPT_DIFFICULTY):
                        self._change_option_value(self.selected, 1)

        # 4. Gamepad Analógico Esquerdo
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
                val = -event.value if getattr(ctrl_mgr, "invert_y", False) else event.value
                if val > 0.65 and not self._axis_y_held:
                    self._axis_y_held = True
                    self._nav_step(1)
                elif val < -0.65 and not self._axis_y_held:
                    self._axis_y_held = True
                    self._nav_step(-1)
                elif abs(val) < 0.35:
                    self._axis_y_held = False
            elif event.axis == 0:
                val = event.value
                if val > 0.65 and not self._axis_x_held:
                    self._axis_x_held = True
                    if self.selected in (self.OPT_MODE, self.OPT_ROUNDS, self.OPT_DIFFICULTY):
                        self._change_option_value(self.selected, 1)
                    elif self.selected == self.OPT_PROCEED:
                        self.selected = self.OPT_BACK
                        self._play_sfx()
                elif val < -0.65 and not self._axis_x_held:
                    self._axis_x_held = True
                    if self.selected in (self.OPT_MODE, self.OPT_ROUNDS, self.OPT_DIFFICULTY):
                        self._change_option_value(self.selected, -1)
                    elif self.selected == self.OPT_BACK:
                        self.selected = self.OPT_PROCEED
                        self._play_sfx()
                elif abs(val) < 0.35:
                    self._axis_x_held = False

        return None

    def render(self, surface: pygame.Surface):
        parch = pm.get_backdrop() is not None
        if parch:
            pm.draw_backdrop(surface)
        else:
            surface.fill(COLOR_BG)
            for p in self.particles:
                pygame.draw.circle(surface, (175, 170, 165), (int(p["x"]), int(p["y"])), int(p["size"]))

        draw_scroll_frame(surface, margin_top=50, margin_bottom=45, margin_sides=24)

        font_title = get_title_font(34)
        font_sub = get_title_font(18)
        font_label = get_text_font(18)
        font_val = get_title_font(20)
        font_btn = get_title_font(18)
        font_hint = get_text_font(13)

        # Painel central cerimonial em pergaminho
        panel_w = 780
        panel_h = 490
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 10
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        if parch:
            pm.draw_paper_card(surface, panel_rect, seed=42)
            pm.draw_crest(surface, panel_rect.right - 65, panel_rect.y + 45, scale=0.7)
        else:
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel_surf.fill((20, 22, 26, 240))
            surface.blit(panel_surf, panel_rect.topleft)
            pygame.draw.rect(surface, (140, 115, 60), panel_rect, 2, border_radius=8)

        # Cabeçalho do Painel
        title_txt = t("versus_config_title")
        sub_txt = t("versus_config_subtitle")

        if parch:
            s_title = pm.render_ink(font_title, title_txt, pm.INK)
            s_sub = pm.render_ink(font_sub, sub_txt, pm.INK_SOFT)
        else:
            s_title = font_title.render(title_txt, True, COLOR_GOLD)
            s_sub = font_sub.render(sub_txt, True, (190, 180, 160))

        surface.blit(s_title, (panel_rect.centerx - s_title.get_width() // 2, panel_rect.y + 24))
        surface.blit(s_sub, (panel_rect.centerx - s_sub.get_width() // 2, panel_rect.y + 64))

        draw_brush_divider(surface, panel_rect.x + 36, panel_rect.y + 92, panel_rect.right - 36, color=(140, 105, 38) if parch else (90, 80, 60))

        # -------------------------------------------------------------
        # Linhas de Opções Interativas
        # -------------------------------------------------------------
        row_y_start = panel_rect.y + 115
        row_h = 68
        self.row_rects.clear()
        self.arrow_left_rects.clear()
        self.arrow_right_rects.clear()

        pulse = 0.5 + 0.5 * math.sin(self.anim_timer * 6.0)

        # Opção 0: Modo
        mode_names = {
            "pve": t("versus_mode_pve"),
            "pvp": t("versus_mode_pvp"),
            "watch": t("versus_mode_watch")
        }
        mode_val_txt = mode_names.get(self.mode, self.mode)

        # Opção 1: Rounds
        if self.rounds_to_win == 1:
            rounds_val_txt = t("versus_rounds_desc_single")
        elif self.rounds_to_win == 2:
            rounds_val_txt = t("versus_rounds_desc_default")
        else:
            total_b = 2 * self.rounds_to_win - 1
            rounds_val_txt = t("versus_rounds_desc", n=self.rounds_to_win, total=total_b)

        # Opção 2: Dificuldade da IA
        diff_names = {
            "easy": t("versus_diff_easy"),
            "normal": t("versus_diff_normal"),
            "hard": t("versus_diff_hard")
        }
        diff_disabled = (self.mode == "pvp")
        diff_val_txt = t("versus_diff_disabled") if diff_disabled else diff_names.get(self.ai_difficulty, self.ai_difficulty)

        options_data = [
            (self.OPT_MODE, t("versus_mode_label"), mode_val_txt, False),
            (self.OPT_ROUNDS, t("versus_rounds_label"), rounds_val_txt, False),
            (self.OPT_DIFFICULTY, t("versus_difficulty_label"), diff_val_txt, diff_disabled)
        ]

        for i, (opt_idx, label, val_text, is_disabled) in enumerate(options_data):
            ry = row_y_start + i * row_h
            r_box = pygame.Rect(panel_rect.x + 36, ry, panel_rect.width - 72, 54)
            self.row_rects[opt_idx] = r_box

            is_sel = (self.selected == opt_idx) and not is_disabled

            # Fundo da linha
            if is_disabled:
                bg_col = (20, 20, 22, 120) if not parch else (225, 220, 210)
                border_col = (70, 68, 65) if not parch else (190, 185, 175)
            elif is_sel:
                bg_col = (45, 34, 22) if not parch else (245, 238, 220)
                border_col = COLOR_GOLD if not parch else pm.SEAL_RED
            else:
                bg_col = (24, 26, 30) if not parch else (235, 230, 218)
                border_col = (80, 75, 70) if not parch else (180, 175, 160)

            pygame.draw.rect(surface, bg_col, r_box, border_radius=8)
            border_w = 2 if is_sel else 1
            pygame.draw.rect(surface, border_col, r_box, border_w, border_radius=8)

            if is_sel:
                if parch:
                    pm.draw_ink_border(surface, r_box, pm.SEAL_RED, width=2, seed=opt_idx + 12, alpha=int(140 + 115 * pulse))
                else:
                    glow_rect = r_box.inflate(4, 4)
                    pygame.draw.rect(surface, (180, 140, 50), glow_rect, 1, border_radius=10)

            # Rótulo à esquerda
            lbl_col = (110, 105, 100) if is_disabled else ((240, 230, 210) if not parch else pm.INK)
            s_lbl = font_label.render(label, True, lbl_col)
            surface.blit(s_lbl, (r_box.x + 20, r_box.centery - s_lbl.get_height() // 2))

            # Seletor interativo com setas à direita
            val_box_w = 340
            val_box = pygame.Rect(r_box.right - val_box_w - 14, r_box.y + 7, val_box_w, 40)
            btn_arrow_w = 34
            r_arrow_left = pygame.Rect(val_box.x, val_box.y, btn_arrow_w, val_box.height)
            r_arrow_right = pygame.Rect(val_box.right - btn_arrow_w, val_box.y, btn_arrow_w, val_box.height)

            if not is_disabled:
                self.arrow_left_rects[opt_idx] = r_arrow_left
                self.arrow_right_rects[opt_idx] = r_arrow_right

            # Fundo do seletor
            val_bg = (16, 18, 22) if not parch else (220, 214, 202)
            pygame.draw.rect(surface, val_bg, val_box, border_radius=6)
            pygame.draw.rect(surface, border_col, val_box, 1, border_radius=6)

            # Setas < e >
            arrow_col = (80, 75, 70) if is_disabled else (COLOR_GOLD if is_sel else (190, 180, 160))
            if parch and not is_disabled:
                arrow_col = pm.SEAL_RED if is_sel else pm.INK_SOFT

            s_al = font_val.render("◄", True, arrow_col)
            s_ar = font_val.render("►", True, arrow_col)
            surface.blit(s_al, s_al.get_rect(center=r_arrow_left.center))
            surface.blit(s_ar, s_ar.get_rect(center=r_arrow_right.center))

            # Texto do valor centralizado (sem necessidade de trim)
            val_text_col = (110, 105, 100) if is_disabled else ((COLOR_GOLD if is_sel else (245, 235, 220)) if not parch else (pm.SEAL_RED if is_sel else pm.INK))
            s_val = font_val.render(val_text, True, val_text_col)
            surface.blit(s_val, s_val.get_rect(center=(val_box.centerx, val_box.centery)))

        # Divisória antes dos botões de ação
        draw_brush_divider(surface, panel_rect.x + 36, panel_rect.y + 340, panel_rect.right - 36, color=(140, 105, 38) if parch else (90, 80, 60))

        # -------------------------------------------------------------
        # Botões de Ação (Avançar e Voltar)
        # -------------------------------------------------------------
        btn_w = 320
        btn_h = 50
        btn_y = panel_rect.y + 365

        self.btn_proceed_rect = pygame.Rect(panel_rect.centerx - btn_w - 18, btn_y, btn_w, btn_h)
        self.btn_back_rect = pygame.Rect(panel_rect.centerx + 18, btn_y, btn_w, btn_h)

        # 1. Botão Avançar / Selecionar Guerreiros
        is_sel_proceed = (self.selected == self.OPT_PROCEED)
        btn_bg_proceed = (165 + int(pulse * 30), 38 + int(pulse * 15), 32) if is_sel_proceed else ((120, 30, 26) if not parch else (235, 228, 215))
        pygame.draw.rect(surface, btn_bg_proceed, self.btn_proceed_rect, border_radius=8)
        border_col_proceed = COLOR_GOLD if is_sel_proceed else (140, 115, 60)
        pygame.draw.rect(surface, border_col_proceed, self.btn_proceed_rect, 2 if is_sel_proceed else 1, border_radius=8)

        if is_sel_proceed and parch:
            pm.draw_brush_highlight(surface, self.btn_proceed_rect, pm.SEAL_RED, seed=5, alpha=230)

        proceed_text = f"{t('versus_btn_proceed')}  [ENTER / {{icon:confirm}}]"
        render_text_with_icons(surface, font_btn, proceed_text, self.btn_proceed_rect.centerx, self.btn_proceed_rect.centery,
                               text_color=(255, 245, 220) if is_sel_proceed else COLOR_GOLD, icon_size=20, shadow=True)

        # 2. Botão Voltar
        is_sel_back = (self.selected == self.OPT_BACK)
        btn_bg_back = (45, 34, 22) if is_sel_back else ((24, 26, 30) if not parch else (235, 228, 215))
        pygame.draw.rect(surface, btn_bg_back, self.btn_back_rect, border_radius=8)
        border_col_back = COLOR_GOLD if is_sel_back else (90, 85, 80)
        pygame.draw.rect(surface, border_col_back, self.btn_back_rect, 2 if is_sel_back else 1, border_radius=8)

        if is_sel_back and parch:
            pm.draw_brush_highlight(surface, self.btn_back_rect, (85, 75, 68), seed=7, alpha=220)

        back_text = f"{t('versus_btn_back')}  [ESC / {{icon:cancel}}]"
        render_text_with_icons(surface, font_btn, back_text, self.btn_back_rect.centerx, self.btn_back_rect.centery,
                               text_color=(255, 245, 220) if is_sel_back else (190, 180, 160), icon_size=20, shadow=True)

        # -------------------------------------------------------------
        # Rodapé: Guia de Navegação
        # -------------------------------------------------------------
        hint_text = t("versus_nav_hint")
        render_text_with_icons(surface, font_hint, hint_text, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 24,
                               text_color=(210, 195, 160) if not parch else pm.INK_SOFT, icon_size=16, shadow=True)
