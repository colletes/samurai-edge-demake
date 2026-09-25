"""
Tela de Seleção de Personagens (Character Select Screen).
Permite escolher entre os 12 guerreiros do Bakumatsu.
Oferece suporte sequencial de seleção para 1P vs IA (P1 escolhe seu lutador -> P1 escolhe a IA),
bloqueio de teclado P2 no modo IA, suporte a 2 controles no modo 2P,
navegação até o botão de alternar modo e comandos padronizados de confirmação e volta.
"""
import math
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_RED_AURA,
    COLOR_BLUE_AURA, COLOR_YELLOW_AURA, COLOR_BG, COLOR_STEEL,
    COLOR_AMERICAN_NINJA, COLOR_AMERICAN_VEST, COLOR_AMERICAN_BANDANA,
    COLOR_DOBERMAN_BLACK, COLOR_DOBERMAN_RUST, COLOR_DOBERMAN_COLLAR,
    COLOR_GRAY_NINJA, COLOR_GRAY_DARK, COLOR_SMOKE, COLOR_BOMB_FUSE,
    COLOR_PURPLE_NINJA, COLOR_PURPLE_DARK, COLOR_PURPLE_AURA, COLOR_CHAIN,
    COLOR_SAITOU_LIGHT_BLUE, CHAR_SAITOU,
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE,
    CHAR_RIFLE, CHAR_KABUKI, CHAR_ARCHER, CHAR_PIRATE, CHAR_MUSKETEER,
    COLOR_PIRATE_AURA, COLOR_MUSKETEER_AURA
)

from src.isometric.iso_math import world_to_iso
from src.entities.voxel_models import render_voxel_humanoid, render_voxel_doberman
from src.ui.game_help import GameHelpModal
from src.i18n import t, get_lang, toggle_lang, LANG_PT, LANG_EN
from src.ui.portraits import get_portrait


class PreviewCamera:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
    def apply(self, wx, wy, wz=0.0):
        ix, iy = world_to_iso(wx, wy, wz)
        return int(self.cx + ix), int(self.cy + iy)


class CharacterSelectScreen:
    def __init__(self):
        self.p1_choice_idx = 0  # Kenshin
        self.p2_choice_idx = 1  # Musashi
        self.p1_ready = False
        self.p2_ready = False
        self.vs_ai = True
        self.selection_step = "P1"  # "P1" -> "AI" (no modo 1P vs IA)
        self.focus_zone = "GRID"    # "GRID" ou "MODE_BTN"
        self._axis_x_held_p1 = False
        self._axis_y_held_p1 = False
        self._axis_x_held_p2 = False
        self._axis_y_held_p2 = False
        self.anim_timer = 0.0

        # Modal de Ajuda Completa do Jogo e Guia dos 12 Guerreiros
        self.help_modal = GameHelpModal()
        self.help_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.lang_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.info_btn_rects: list[pygame.Rect] = []

        self.characters = [
            {
                "id": CHAR_KENSHIN,
                "name": "KENSHI",
                "title": "Retalhadora",
                "style": "Iai & Shukuchi",
                "color": COLOR_RED_AURA,
                "speed_stars": "[5/5] MAX",
                "damage_desc": "1-Hit Kill Instantâneo",
                "special_desc": "Shukuchi (Relâmpago)",
                "keys_p1": "[E] Iai | [R] Dash",
                "keys_p2": "[U] Iai | [I] Dash",
            },
            {
                "id": CHAR_MUSASHI,
                "name": "MUSASHI",
                "title": "Duas Lâminas",
                "style": "Niten Ichi-ryū",
                "color": COLOR_BLUE_AURA,
                "speed_stars": "[2/5] Firme",
                "damage_desc": "Combo 3-Cortes",
                "special_desc": "Defesa (Parry)",
                "keys_p1": "[E] Golpe | [R] Parry",
                "keys_p2": "[U] Golpe | [I] Parry",
            },
            {
                "id": CHAR_NINJA,
                "name": "HANZO",
                "title": "Ninja Mestre",
                "style": "Ninjutsu & Kunai",
                "color": COLOR_YELLOW_AURA,
                "speed_stars": "[5/5] MAX",
                "damage_desc": "Estocada (2 Hits)",
                "special_desc": "Arremesso Kunai",
                "keys_p1": "[E] Kunai | [R] Lançar",
                "keys_p2": "[U] Kunai | [I] Lançar",
            },
            {
                "id": CHAR_AMERICAN,
                "name": "JOE",
                "title": "American Ninja",
                "style": "Tático & Cão",
                "color": (255, 130, 45),
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Shuriken (Stun)",
                "special_desc": "Doberman (1-Hit Kill)",
                "keys_p1": "[E] Shuriken | [R] Cão",
                "keys_p2": "[U] Shuriken | [I] Cão",
            },
            {
                "id": CHAR_SAITOU,
                "name": "SAITOU",
                "title": "Lobo de Mibu",
                "style": "Gatotsu Shinsen",
                "color": COLOR_SAITOU_LIGHT_BLUE,
                "speed_stars": "[5/5] Impulso",
                "damage_desc": "1-Hit Acelerado",
                "special_desc": "Zeroshiki (Curto)",
                "keys_p1": "[E] Gatotsu | [R] Zero",
                "keys_p2": "[U] Gatotsu | [I] Zero",
            },
            {
                "id": CHAR_RIFLE,
                "name": "TEPPO",
                "title": "Marksman",
                "style": "Arcabuz Feudal",
                "color": (225, 170, 100),
                "speed_stars": "[3/5] Cadência",
                "damage_desc": "Tiro Fatal (1-Hit)",
                "special_desc": "Carregar Pólvora",
                "keys_p1": "[E] Tiro | [R] Recarga",
                "keys_p2": "[U] Tiro | [I] Recarga",
            },
            {
                "id": CHAR_PURPLE,
                "name": "MURASAKI",
                "title": "Kunoichi Foice",
                "style": "Kusarigama",
                "color": COLOR_PURPLE_AURA,
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Precedência Absoluta",
                "special_desc": "Puxão de Corrente",
                "keys_p1": "[E] Foice | [R] Puxar",
                "keys_p2": "[U] Foice | [I] Puxar",
            },
            {
                "id": CHAR_GRAY,
                "name": "KASUMI",
                "title": "Kunoichi Névoa",
                "style": "Pólvora & Fumaça",
                "color": (165, 180, 190),
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Bomba Arco (Auto-Dano)",
                "special_desc": "Fumaça (Slow + Fuga)",
                "keys_p1": "[E] Bomba | [R] Fumaça",
                "keys_p2": "[U] Bomba | [I] Fumaça",
            },
            {
                "id": CHAR_KABUKI,
                "name": "OKUNI",
                "title": "Mestra Kabuki",
                "style": "Sopro Tóxico",
                "color": (240, 115, 30),
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Veneno (10s Morte)",
                "special_desc": "Pirueta Evasiva",
                "keys_p1": "[E] Sopro | [R] Esquiva",
                "keys_p2": "[U] Sopro | [I] Esquiva",
            },
            {
                "id": CHAR_ARCHER,
                "name": "TOMOE",
                "title": "Arqueira Miko",
                "style": "Arco Yumi",
                "color": (110, 195, 135),
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Flecha Letal (Disparo Rápido)",
                "special_desc": "Flecha de Corda (Sem Cooldown)",
                "keys_p1": "[E] Yumi | [R] Corda",
                "keys_p2": "[U] Yumi | [I] Corda",
            },
            {
                "id": CHAR_PIRATE,
                "name": "ANNE",
                "title": "Espadachim",
                "style": "Alfanje & Pólvora",
                "color": COLOR_PIRATE_AURA,
                "speed_stars": "[4/5] Ágil",
                "damage_desc": "Corte Amplo 180°",
                "special_desc": "Pólvora nos Olhos",
                "keys_p1": "[E] Alfanje | [R] Cegar",
                "keys_p2": "[U] Alfanje | [I] Cegar",
            },
            {
                "id": CHAR_MUSKETEER,
                "name": "JULIE",
                "title": "Mosqueteira",
                "style": "Florete Nobre",
                "color": COLOR_MUSKETEER_AURA,
                "speed_stars": "[5/5] Rápida",
                "damage_desc": "Fleche Longo",
                "special_desc": "Capa Riposte & Tiro",
                "keys_p1": "[E] Florete | [R] Riposte",
                "keys_p2": "[U] Florete | [I] Riposte",
            }
        ]

        self.card_rects: list[pygame.Rect] = []

    def handle_event(self, event: pygame.event.Event) -> str | bool:
        """
        Processa eventos de seleção de personagens.
        Retorna:
          - True: iniciar partida
          - "BACK": voltar para a tela de título
          - False: continuar na tela de seleção
        """
        from src.input.controller_manager import get_controller_manager
        ctrl_mgr = get_controller_manager()

        if self.help_modal.is_open:
            self.help_modal.handle_event(event)
            return False

        num_c = len(self.characters)
        cols = 6

        def move_cursor(player: str, dx: int, dy: int):
            if player == "P1":
                if self.focus_zone == "MODE_BTN":
                    if dy > 0:
                        self.focus_zone = "GRID"
                    elif dx != 0:
                        self.vs_ai = not self.vs_ai
                        self.selection_step = "P1"
                        self.p1_ready = False
                        self.p2_ready = False
                    return

                active_idx = self.p1_choice_idx if (not self.vs_ai or self.selection_step == "P1") else self.p2_choice_idx
                row = active_idx // cols
                col = active_idx % cols

                if dy < 0 and row == 0:
                    self.focus_zone = "MODE_BTN"
                    return

                new_col = (col + dx) % cols
                new_row = (row + dy) % 2
                new_idx = new_row * cols + new_col

                if not self.vs_ai:
                    if not self.p1_ready:
                        self.p1_choice_idx = new_idx
                else:
                    if self.selection_step == "P1":
                        self.p1_choice_idx = new_idx
                    else:
                        self.p2_choice_idx = new_idx

            elif player == "P2":
                if not self.vs_ai and not self.p2_ready:
                    row = self.p2_choice_idx // cols
                    col = self.p2_choice_idx % cols
                    new_col = (col + dx) % cols
                    new_row = (row + dy) % 2
                    self.p2_choice_idx = new_row * cols + new_col

        def handle_confirm(player: str) -> str | bool:
            if self.focus_zone == "MODE_BTN":
                self.vs_ai = not self.vs_ai
                self.selection_step = "P1"
                self.p1_ready = False
                self.p2_ready = False
                return False

            if self.vs_ai:
                if self.selection_step == "P1":
                    self.selection_step = "AI"
                    return False
                elif self.selection_step == "AI":
                    return True
            else:
                if player == "P1":
                    self.p1_ready = True
                elif player == "P2":
                    self.p2_ready = True
                if self.p1_ready and self.p2_ready:
                    return True
            return False

        def handle_cancel(player: str) -> str | bool:
            if self.focus_zone == "MODE_BTN":
                self.focus_zone = "GRID"
                return False

            if self.vs_ai:
                if self.selection_step == "AI":
                    self.selection_step = "P1"
                    return False
                elif self.selection_step == "P1":
                    return "BACK"
            else:
                if player == "P2" and self.p2_ready:
                    self.p2_ready = False
                    return False
                elif player == "P1" and self.p1_ready:
                    self.p1_ready = False
                    return False
                else:
                    return "BACK"
            return False

        # --- 1. GAMEPAD EVENTS ---
        if event.type == pygame.JOYBUTTONDOWN:
            ctrl2 = ctrl_mgr.get_controller_for_player(1)
            is_p2 = (ctrl2 is not None and getattr(event, "instance_id", None) == ctrl2.instance_id)

            if self.vs_ai and is_p2:
                return False

            target_player = "P2" if (is_p2 and not self.vs_ai) else "P1"
            player_idx = 1 if is_p2 else 0

            if ctrl_mgr.is_event_menu_confirm(event, player_idx) or event.button in (0, 1, 7):
                res = handle_confirm(target_player)
                if res:
                    return res
                return False
            elif ctrl_mgr.is_event_menu_cancel(event, player_idx) or event.button in (2, 1):
                res = handle_cancel(target_player)
                if res:
                    return res
                return False
            elif event.button in (2, 3):
                active_idx = self.p1_choice_idx if (not self.vs_ai or self.selection_step == "P1") else self.p2_choice_idx
                self.help_modal.open(GameHelpModal.TAB_FIGHTERS, fighter_idx=active_idx)
                return False

        elif event.type == pygame.JOYHATMOTION:
            ctrl2 = ctrl_mgr.get_controller_for_player(1)
            is_p2 = (ctrl2 is not None and getattr(event, "instance_id", None) == ctrl2.instance_id)
            if self.vs_ai and is_p2:
                return False

            target_player = "P2" if (is_p2 and not self.vs_ai) else "P1"
            hx, hy = event.value
            dx = 1 if hx > 0 else (-1 if hx < 0 else 0)
            dy = -1 if hy > 0 else (1 if hy < 0 else 0)
            if dx != 0 or dy != 0:
                move_cursor(target_player, dx, dy)

        elif event.type == pygame.JOYAXISMOTION:
            ctrl2 = ctrl_mgr.get_controller_for_player(1)
            is_p2 = (ctrl2 is not None and getattr(event, "instance_id", None) == ctrl2.instance_id)
            if self.vs_ai and is_p2:
                return False

            target_player = "P2" if (is_p2 and not self.vs_ai) else "P1"

            if target_player == "P1":
                if event.axis == 0:
                    if event.value > 0.65 and not self._axis_x_held_p1:
                        move_cursor("P1", 1, 0)
                        self._axis_x_held_p1 = True
                    elif event.value < -0.65 and not self._axis_x_held_p1:
                        move_cursor("P1", -1, 0)
                        self._axis_x_held_p1 = True
                    elif abs(event.value) < 0.25:
                        self._axis_x_held_p1 = False

                elif event.axis == 1:
                    if event.value > 0.65 and not self._axis_y_held_p1:
                        move_cursor("P1", 0, 1)
                        self._axis_y_held_p1 = True
                    elif event.value < -0.65 and not self._axis_y_held_p1:
                        move_cursor("P1", 0, -1)
                        self._axis_y_held_p1 = True
                    elif abs(event.value) < 0.25:
                        self._axis_y_held_p1 = False

            elif target_player == "P2":
                if event.axis == 0:
                    if event.value > 0.65 and not self._axis_x_held_p2:
                        move_cursor("P2", 1, 0)
                        self._axis_x_held_p2 = True
                    elif event.value < -0.65 and not self._axis_x_held_p2:
                        move_cursor("P2", -1, 0)
                        self._axis_x_held_p2 = True
                    elif abs(event.value) < 0.25:
                        self._axis_x_held_p2 = False

                elif event.axis == 1:
                    if event.value > 0.65 and not self._axis_y_held_p2:
                        move_cursor("P2", 0, 1)
                        self._axis_y_held_p2 = True
                    elif event.value < -0.65 and not self._axis_y_held_p2:
                        move_cursor("P2", 0, -1)
                        self._axis_y_held_p2 = True
                    elif abs(event.value) < 0.25:
                        self._axis_y_held_p2 = False

        # --- 2. KEYBOARD EVENTS ---
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.vs_ai = not self.vs_ai
                self.selection_step = "P1"
                self.p1_ready = False
                self.p2_ready = False
                return False
            elif event.key == pygame.K_h:
                self.help_modal.open(GameHelpModal.TAB_RULES)
                return False
            elif event.key == pygame.K_f:
                active_idx = self.p1_choice_idx if (not self.vs_ai or self.selection_step == "P1") else self.p2_choice_idx
                self.help_modal.open(GameHelpModal.TAB_FIGHTERS, fighter_idx=active_idx)
                return False
            elif event.key == pygame.K_l:
                toggle_lang()
                return False

            # Teclado P1 (WASD)
            if event.key == pygame.K_a:
                move_cursor("P1", -1, 0)
            elif event.key == pygame.K_d:
                move_cursor("P1", 1, 0)
            elif event.key == pygame.K_w:
                move_cursor("P1", 0, -1)
            elif event.key == pygame.K_s:
                move_cursor("P1", 0, 1)
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                res = handle_confirm("P1")
                if res:
                    return res
                return False
            elif event.key == pygame.K_ESCAPE:
                res = handle_cancel("P1")
                if res:
                    return res
                return False

            # Teclado P2 (SETAS) - Navega P2 no modo 2P ou escolhe o oponente da IA no modo vs_ai
            if event.key == pygame.K_LEFT:
                move_cursor("P2", -1, 0)
            elif event.key == pygame.K_RIGHT:
                move_cursor("P2", 1, 0)
            elif event.key == pygame.K_UP:
                move_cursor("P2", 0, -1)
            elif event.key == pygame.K_DOWN:
                move_cursor("P2", 0, 1)
            elif not self.vs_ai and event.key in (pygame.K_KP_ENTER, pygame.K_RCTRL):
                res = handle_confirm("P2")
                if res:
                    return res
                return False

        # --- 3. TOQUE E MOUSE ---
        elif event.type == pygame.FINGERDOWN:
            vx = event.x * SCREEN_WIDTH
            vy = event.y * SCREEN_HEIGHT
            if self.lang_btn_rect.collidepoint(vx, vy):
                toggle_lang()
                return False
            if self.help_btn_rect.collidepoint(vx, vy):
                self.help_modal.open(GameHelpModal.TAB_RULES)
                return False
            for idx, irect in enumerate(self.info_btn_rects):
                if irect.collidepoint(vx, vy):
                    self.help_modal.open(GameHelpModal.TAB_FIGHTERS, fighter_idx=idx)
                    return False
            ai_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 52, 280, 28)
            if ai_btn.collidepoint(vx, vy):
                self.vs_ai = not self.vs_ai
                self.selection_step = "P1"
                self.p1_ready = False
                self.p2_ready = False
                return False
            for idx, rect in enumerate(self.card_rects):
                if rect.collidepoint(vx, vy):
                    if self.vs_ai:
                        if self.selection_step == "P1":
                            self.p1_choice_idx = idx
                        else:
                            self.p2_choice_idx = idx
                    else:
                        self.p1_choice_idx = idx
            start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 64, 320, 44)
            if start_btn.collidepoint(vx, vy):
                res = handle_confirm("P1")
                if res:
                    return res
                return False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if event.button == 1:
                if self.lang_btn_rect.collidepoint(mx, my):
                    toggle_lang()
                    return False
                if self.help_btn_rect.collidepoint(mx, my):
                    self.help_modal.open(GameHelpModal.TAB_RULES)
                    return False
                for idx, irect in enumerate(self.info_btn_rects):
                    if irect.collidepoint(mx, my):
                        self.help_modal.open(GameHelpModal.TAB_FIGHTERS, fighter_idx=idx)
                        return False
                ai_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 52, 280, 28)
                if ai_btn.collidepoint(mx, my):
                    self.vs_ai = not self.vs_ai
                    self.selection_step = "P1"
                    self.p1_ready = False
                    self.p2_ready = False
                    return False
                for idx, rect in enumerate(self.card_rects):
                    if rect.collidepoint(mx, my):
                        if self.vs_ai:
                            if self.selection_step == "P1":
                                self.p1_choice_idx = idx
                            else:
                                self.p2_choice_idx = idx
                        else:
                            self.p1_choice_idx = idx
                start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 64, 320, 44)
                if start_btn.collidepoint(mx, my):
                    res = handle_confirm("P1")
                    if res:
                        return res
                    return False
            elif event.button == 3:
                for idx, rect in enumerate(self.card_rects):
                    if rect.collidepoint(mx, my):
                        self.p2_choice_idx = idx

        return False

    def update(self, dt: float):
        self.anim_timer += dt
        self.help_modal.update(dt)

    def get_selected_characters(self) -> tuple[str, str, bool]:
        p1_char = self.characters[self.p1_choice_idx]["id"]
        p2_char = self.characters[self.p2_choice_idx]["id"]
        return p1_char, p2_char, self.vs_ai

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        surface.fill(COLOR_BG)

        # 1. Título
        title_surf = font_large.render(t("select_title"), True, COLOR_GOLD)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 14))

        # Botão Seletor Flutuante de Idioma [ PT | EN ]
        lang = get_lang()
        self.lang_btn_rect = pygame.Rect(SCREEN_WIDTH - 365, 14, 100, 34)
        pygame.draw.rect(surface, (30, 40, 35), self.lang_btn_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.lang_btn_rect, 1, border_radius=6)

        pt_col = COLOR_GOLD if lang == LANG_PT else (140, 155, 148)
        en_col = COLOR_GOLD if lang == LANG_EN else (140, 155, 148)
        pt_bg = (48, 64, 54) if lang == LANG_PT else (25, 34, 29)
        en_bg = (48, 64, 54) if lang == LANG_EN else (25, 34, 29)

        r_pt = pygame.Rect(self.lang_btn_rect.x + 3, self.lang_btn_rect.y + 3, 44, 28)
        r_en = pygame.Rect(self.lang_btn_rect.x + 53, self.lang_btn_rect.y + 3, 44, 28)
        pygame.draw.rect(surface, pt_bg, r_pt, border_radius=4)
        pygame.draw.rect(surface, en_bg, r_en, border_radius=4)

        s_pt = font_small.render("PT", True, pt_col)
        s_en = font_small.render("EN", True, en_col)
        surface.blit(s_pt, (r_pt.centerx - s_pt.get_width() // 2, r_pt.centery - s_pt.get_height() // 2))
        surface.blit(s_en, (r_en.centerx - s_en.get_width() // 2, r_en.centery - s_en.get_height() // 2))

        # Botão Superior Guia do Jogo & Ajuda
        self.help_btn_rect = pygame.Rect(SCREEN_WIDTH - 250, 14, 226, 34)
        pygame.draw.rect(surface, (28, 38, 33), self.help_btn_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.help_btn_rect, 1, border_radius=6)
        h_txt = font_small.render(t("btn_help"), True, COLOR_GOLD)
        surface.blit(h_txt, (self.help_btn_rect.centerx - h_txt.get_width() // 2, self.help_btn_rect.centery - h_txt.get_height() // 2))

        # 2. Botão Modo de Jogo (Navegável via Direcional Cima/Baixo)
        ai_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 52, 280, 28)
        is_mode_focused = (self.focus_zone == "MODE_BTN")
        mode_btn_bg = (45, 60, 50) if is_mode_focused else (30, 40, 35)
        pygame.draw.rect(surface, mode_btn_bg, ai_btn, border_radius=6)
        border_col = (255, 230, 120) if is_mode_focused else COLOR_GOLD
        border_w = 2 if is_mode_focused else 1
        pygame.draw.rect(surface, border_col, ai_btn, border_w, border_radius=6)

        mode_text = ("1P vs IA (Treino / Duelo)" if self.vs_ai else "1P vs 2P (Versus Local)")
        if is_mode_focused:
            mode_text = f"► {mode_text} ◄"
        mode_surf = font_small.render(mode_text, True, border_col)
        surface.blit(mode_surf, (ai_btn.centerx - mode_surf.get_width() // 2, ai_btn.y + 6))

        # Banner Indicador de Etapa / Instrução
        pulse = (math.sin(self.anim_timer * 5.0) + 1.0) * 0.5
        if self.vs_ai:
            if self.selection_step == "P1":
                step_title = "PASSO 1: ESCOLHA SEU GUERREIRO (P1)"
                step_color = COLOR_RED_AURA
                sub_step = "[ ✕ / Espaço ] Confirmar P1  |  [ ○ / ESC ] Voltar ao Menu  |  [ ↑ ] Alternar Modo"
            else:
                step_title = "PASSO 2: ESCOLHA SEU OPONENTE (IA)"
                step_color = COLOR_BLUE_AURA
                sub_step = "[ ✕ / Espaço ] Confirmar e Iniciar Duelo  |  [ ○ / ESC ] Voltar ao P1"
        else:
            step_title = "MODO 2 JOGADORES (VERSUS LOCAL)"
            step_color = COLOR_GOLD
            p1_st = "PRONTO!" if self.p1_ready else "ESCOLHENDO"
            p2_st = "PRONTO!" if self.p2_ready else "ESCOLHENDO"
            sub_step = f"P1: {p1_st}  |  P2: {p2_st}  |  [ ✕ / Espaço ] Confirmar  |  [ ○ / ESC ] Voltar"

        banner_surf = font_mid.render(step_title, True, step_color)
        surface.blit(banner_surf, (SCREEN_WIDTH // 2 - banner_surf.get_width() // 2, 84))

        sub_surf = font_small.render(sub_step, True, (200, 215, 210))
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 104))

        # 3. Grade Simétrica 6x2 (6 cards na Linha 1, 6 cards na Linha 2)
        card_w = 194
        card_h = 232
        spacing_x = 12
        spacing_y = 12

        total_w = 6 * card_w + 5 * spacing_x
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = 124

        self.card_rects.clear()
        self.info_btn_rects.clear()

        for idx, char_info in enumerate(self.characters):
            row = idx // 6
            col = idx % 6
            cx = start_x + col * (card_w + spacing_x)
            cy = start_y + row * (card_h + spacing_y)

            rect = pygame.Rect(cx, cy, card_w, card_h)
            self.card_rects.append(rect)

            is_p1 = (self.p1_choice_idx == idx)
            is_p2 = (self.p2_choice_idx == idx)

            bg_color = (25, 32, 28)
            border_color = (60, 75, 68)
            border_width = 1

            if self.vs_ai:
                if is_p1 and is_p2:
                    border_color = COLOR_GOLD
                    border_width = 3
                    bg_color = (35, 42, 38)
                elif is_p1:
                    border_color = COLOR_RED_AURA
                    border_width = 3 if self.selection_step == "P1" else 2
                    bg_color = (40, 30, 32)
                elif is_p2:
                    border_color = COLOR_BLUE_AURA
                    border_width = 3 if self.selection_step == "AI" else 2
                    bg_color = (30, 35, 45)
            else:
                if is_p1 and is_p2:
                    border_color = COLOR_GOLD
                    border_width = 3
                    bg_color = (35, 42, 38)
                elif is_p1:
                    border_color = COLOR_RED_AURA
                    border_width = 3
                    bg_color = (40, 30, 32)
                elif is_p2:
                    border_color = COLOR_BLUE_AURA
                    border_width = 3
                    bg_color = (30, 35, 45)

            pygame.draw.rect(surface, bg_color, rect, border_radius=12)
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=12)

            # Badges P1 / IA no topo direito do card
            badge_y = rect.y + 8
            if is_p1 and is_p2:
                p1_label = "P1"
                p2_label = "IA" if self.vs_ai else "P2"
                p1_badge = font_small.render(p1_label, True, COLOR_RED_AURA)
                p2_badge = font_small.render(p2_label, True, COLOR_BLUE_AURA)
                surface.blit(p2_badge, (rect.right - p2_badge.get_width() - 8, badge_y))
                surface.blit(p1_badge, (rect.right - p2_badge.get_width() - p1_badge.get_width() - 12, badge_y))
            elif is_p1:
                p1_label = "P1"
                if self.vs_ai and self.selection_step == "AI":
                    p1_label = "P1 ✓"
                p1_badge = font_small.render(p1_label, True, COLOR_RED_AURA)
                surface.blit(p1_badge, (rect.right - p1_badge.get_width() - 8, badge_y))
            elif is_p2:
                p2_label = "IA (Alvo)" if self.vs_ai else "P2"
                p2_badge = font_small.render(p2_label, True, COLOR_BLUE_AURA)
                surface.blit(p2_badge, (rect.right - p2_badge.get_width() - 8, badge_y))

            # Retrato de Busto HD-2D do Personagem (no topo esquerdo da carta)
            char_id = char_info["id"]
            portrait_size = (54, 54)
            portrait_x = rect.x + 8
            portrait_y = rect.y + 10
            portrait_cx = portrait_x + portrait_size[0] // 2
            portrait_cy = portrait_y + portrait_size[1] // 2

            ring_color = border_color if (is_p1 or is_p2) else char_info["color"]
            pygame.draw.circle(surface, (16, 22, 19), (portrait_cx, portrait_cy), 27)
            pygame.draw.circle(surface, ring_color, (portrait_cx, portrait_cy), 27, 2)

            portrait_surf = get_portrait(char_id, size=portrait_size, circular=True)
            if portrait_surf is not None:
                surface.blit(portrait_surf, (portrait_x, portrait_y))
            else:
                cam = PreviewCamera(portrait_cx, portrait_cy + 15)
                if char_id == CHAR_KENSHIN:
                    render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="kenshin")
                elif char_id == CHAR_MUSASHI:
                    render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="musashi")
                elif char_id == CHAR_NINJA:
                    render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="yellow_ninja", extra_props={"has_kunai": True})
                elif char_id == CHAR_AMERICAN:
                    render_voxel_humanoid(surface, cam, -0.20, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="american_ninja")
                    render_voxel_doberman(surface, cam, 0.35, -0.10, 0, 1.0, 0.0, "IDLE", 0.0, True)
                elif char_id == CHAR_GRAY:
                    render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="kasumi")
                elif char_id == CHAR_PURPLE:
                    render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="murasaki")
                elif char_id == CHAR_SAITOU:
                    render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="saitou")
                elif char_id == CHAR_RIFLE:
                    render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="rifleman")
                elif char_id == CHAR_KABUKI:
                    render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="okuni")
                elif char_id == CHAR_ARCHER:
                    render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="tomoe")
                elif char_id == CHAR_PIRATE:
                    render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="pirate")
                elif char_id == CHAR_MUSKETEER:
                    render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type="musketeer")

            # Nome, Título e Estilo ao lado do Retrato
            text_left = rect.x + 68
            name_surf = font_mid.render(char_info["name"], True, char_info["color"])
            surface.blit(name_surf, (text_left, rect.y + 8))

            title_s = font_small.render(char_info["title"], True, (185, 195, 190))
            surface.blit(title_s, (text_left, rect.y + 30))

            style_s = font_small.render(char_info["style"], True, COLOR_WHITE)
            surface.blit(style_s, (text_left, rect.y + 48))

            # Linha divisória
            sep_y = rect.y + 70
            pygame.draw.line(surface, (45, 55, 50), (rect.x + 8, sep_y), (rect.right - 8, sep_y), 1)

            # Atributos e Estatísticas
            stats_y = rect.y + 76
            line_vel = font_small.render(f"Vel: {char_info['speed_stars']}", True, COLOR_GOLD)
            line_dmg = font_small.render(f"Dano: {char_info['damage_desc']}", True, (240, 200, 200))
            line_esp = font_small.render(f"Esp: {char_info['special_desc']}", True, (200, 225, 240))

            surface.blit(line_vel, (rect.x + 8, stats_y))
            surface.blit(line_dmg, (rect.x + 8, stats_y + 19))
            surface.blit(line_esp, (rect.x + 8, stats_y + 38))

            # Caixa de Comandos / Teclas
            ctrl_w = card_w - 40
            ctrl_box = pygame.Rect(rect.x + 6, rect.bottom - 46, ctrl_w, 38)
            pygame.draw.rect(surface, (18, 24, 21), ctrl_box, border_radius=6)
            pygame.draw.rect(surface, (40, 50, 45), ctrl_box, 1, border_radius=6)
            p1_key_label = font_small.render(f"P1: {char_info['keys_p1']}", True, (255, 200, 180))
            p2_key_label = font_small.render(f"P2: {char_info['keys_p2']}", True, (180, 220, 255))
            surface.blit(p1_key_label, (ctrl_box.x + 4, ctrl_box.y + 3))
            surface.blit(p2_key_label, (ctrl_box.x + 4, ctrl_box.y + 19))

            # Botão [ ? ] para abrir estratégia individual deste guerreiro
            info_btn = pygame.Rect(rect.right - 30, rect.bottom - 46, 24, 38)
            self.info_btn_rects.append(info_btn)
            pygame.draw.rect(surface, (26, 36, 31), info_btn, border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD, info_btn, 1, border_radius=6)
            q_surf = font_mid.render("?", True, COLOR_GOLD)
            surface.blit(q_surf, (info_btn.centerx - q_surf.get_width() // 2, info_btn.centery - q_surf.get_height() // 2))

        # Guia de Navegação e Controles (Teclado, Gamepad e Touch)
        from src.input.controller_manager import get_controller_manager
        ctrl_mgr = get_controller_manager()
        badge = ctrl_mgr.get_badge_text(0)

        guide_text = t("guide_nav")
        if badge:
            ctrl = ctrl_mgr.get_controller_for_player(0)
            btn_ok = ctrl.get_button_glyph("confirm") if ctrl else "✕"
            btn_back = ctrl.get_button_glyph("cancel") if ctrl else "○"
            guide_text = f"{badge}: Analógico/D-Pad = Navegar | [{btn_ok}] = Confirma | [{btn_back}] = Volta | [Options] = Menu"

        guide_surf = font_small.render(guide_text, True, (210, 225, 220))
        surface.blit(guide_surf, (SCREEN_WIDTH // 2 - guide_surf.get_width() // 2, SCREEN_HEIGHT - 94))

        # 4. Botão INICIAR DUELO
        start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 64, 320, 44)
        pulse = (math.sin(self.anim_timer * 4.0) + 1.0) * 0.5
        btn_bg = (50 + int(pulse * 15), 75 + int(pulse * 20), 60 + int(pulse * 15))
        pygame.draw.rect(surface, btn_bg, start_btn, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, start_btn, 2, border_radius=8)

        st_label = "INICIAR DUELO" if (not self.vs_ai or self.selection_step == "AI") else "CONFIRMAR P1"
        st_text = font_mid.render(st_label, True, COLOR_GOLD)
        surface.blit(st_text, (start_btn.centerx - st_text.get_width() // 2, start_btn.y + 11))

        # 5. Renderizar Modal de Ajuda se aberto (sobreposto a toda a tela)
        if self.help_modal.is_open:
            self.help_modal.render(surface, font_large, font_mid, font_small)
