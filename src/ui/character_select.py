"""
Tela de Seleção de Personagens (Character Select Screen).
Permite escolher entre os 12 guerreiros do Bakumatsu.
Oferece suporte sequencial de seleção para 1P vs IA (P1 escolhe seu lutador -> P1 escolhe a IA),
bloqueio de teclado P2 no modo IA, suporte a 2 controles no modo 2P,
navegação até o botão de alternar modo e comandos padronizados de confirmação e volta.
"""
import os
import math
import random
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
from src.ui.fonts import get_title_font, get_text_font

# Paleta Sumi-E inspirada no conceito artístico do título
COLOR_SUMI_INK = (18, 18, 20)
COLOR_SUMI_CHARCOAL = (32, 32, 36)
COLOR_WASH_PAPER = (42, 40, 38)
COLOR_PARCHMENT_LIGHT = (218, 210, 195)
COLOR_HANKO_RED = (205, 42, 35)
COLOR_HANKO_BLUE = (35, 95, 175)
COLOR_HANKO_GOLD = (212, 175, 55)
COLOR_LACQUER_DARK = (24, 20, 22)


def draw_hanko_stamp(surface, font, text: str, x: int, y: int, size: int = 34, color = COLOR_HANKO_RED, border_w: int = 2):
    """Desenha um selo tradicional japonês (Hanko / Inkan) com borda dupla e aspecto entalhado."""
    rect = pygame.Rect(x, y, size, size)
    s_bg = pygame.Surface((size, size), pygame.SRCALPHA)
    s_bg.fill((color[0], color[1], color[2], 55))
    surface.blit(s_bg, (x, y))

    pygame.draw.rect(surface, color, rect, border_w)
    inner_rect = pygame.Rect(x + 3, y + 3, size - 6, size - 6)
    pygame.draw.rect(surface, color, inner_rect, 1)

    if text:
        s_txt = font.render(text, True, color)
        surface.blit(s_txt, (rect.centerx - s_txt.get_width() // 2, rect.centery - s_txt.get_height() // 2))


def draw_kanban_arrow(surface, x: int, y: int, size: int, color, direction: str = "right"):
    """Desenha setas indicadoras nítidas e estilizadas sem depender de fontes de sistema."""
    half = size // 2
    if direction == "right":
        pts = [(x, y - half), (x + size, y), (x, y + half)]
    elif direction == "left":
        pts = [(x + size, y - half), (x, y), (x + size, y + half)]
    elif direction == "up":
        pts = [(x - half, y + size), (x, y), (x + half, y + size)]
    elif direction == "down":
        pts = [(x - half, y), (x, y + size), (x + half, y)]
    pygame.draw.polygon(surface, color, pts)


def draw_brush_divider(surface, x1: int, y: int, x2: int, color = (90, 85, 80)):
    """Desenha uma linha divisória orgânica como se feita por pincel de caligrafia."""
    length = max(1, x2 - x1)
    for x in range(x1, x2, 2):
        t = (x - x1) / length
        thickness = 1 + int(2.5 * math.sin(t * math.pi))
        pygame.draw.line(surface, color, (x, y - thickness // 2), (x, y + thickness // 2))


def draw_sumie_card(surface, rect: pygame.Rect, is_p1: bool, is_p2: bool, vs_ai: bool, sel_step: str, anim_time: float):
    """Desenha a moldura de um card de guerreiro no estilo pergaminho e nanquim Sumi-E."""
    card_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    card_surf.fill((22, 20, 22, 245))
    surface.blit(card_surf, rect.topleft)

    pulse = 0.5 + 0.5 * math.sin(anim_time * 6.0)
    if is_p1 and is_p2:
        border_col = (int(255 * pulse + 180 * (1 - pulse)), int(215 * pulse + 140 * (1 - pulse)), 50)
        border_w = 3
    elif is_p1:
        border_col = (int(240 * pulse + 180 * (1 - pulse)), 45, 45)
        border_w = 3 if (not vs_ai or sel_step == "P1") else 2
    elif is_p2:
        border_col = (45, int(150 * pulse + 100 * (1 - pulse)), int(240 * pulse + 180 * (1 - pulse)))
        border_w = 3 if (not vs_ai or sel_step == "AI") else 2
    else:
        border_col = (65, 60, 56)
        border_w = 1

    pygame.draw.rect(surface, border_col, rect, border_w, border_radius=6)
    corner_sz = 8
    c_col = (border_col[0] // 2, border_col[1] // 2, border_col[2] // 2)
    for ox, oy in [(rect.x, rect.y), (rect.right - corner_sz, rect.y),
                   (rect.x, rect.bottom - corner_sz), (rect.right - corner_sz, rect.bottom - corner_sz)]:
        pygame.draw.rect(surface, c_col, (ox, oy, corner_sz, corner_sz), 1)


def draw_enso_circle(surface, cx: int, cy: int, radius: int, color, anim_time: float):
    """Desenha o círculo Ensō (símbolo zen de caligrafia em nanquim) ao redor do retrato."""
    pygame.draw.circle(surface, (14, 14, 16), (cx, cy), radius)
    num_points = 28
    points = []
    for i in range(num_points):
        angle = (i / num_points) * math.pi * 2
        r_offset = math.sin(angle * 3.0 + 1.2) * 1.5
        px = cx + int((radius + r_offset) * math.cos(angle))
        py = cy + int((radius + r_offset) * math.sin(angle))
        points.append((px, py))
    pygame.draw.polygon(surface, color, points, 2)
    pygame.draw.circle(surface, color, (cx + radius - 2, cy - 4), 2)


def draw_kanban_menu_button(surface, font, text: str, sub: str, rect: pygame.Rect, is_selected: bool, is_enabled: bool, anim_time: float):
    """Desenha um botão de menu no formato tradicional de tabuleta de madeira laqueada (Kanban)."""
    if not is_enabled:
        bg_col = (20, 20, 22)
        border_col = (65, 60, 60)
        txt_col = (115, 110, 110)
    elif is_selected:
        pulse = 0.5 + 0.5 * math.sin(anim_time * 6.0)
        bg_col = (52, 42, 24)
        border_col = (int(255 * pulse + 190 * (1 - pulse)), int(210 * pulse + 140 * (1 - pulse)), 50)
        txt_col = COLOR_GOLD
    else:
        bg_col = (30, 28, 28)
        border_col = (85, 78, 70)
        txt_col = (210, 205, 200)

    pygame.draw.rect(surface, bg_col, rect, border_radius=4)
    pygame.draw.rect(surface, border_col, rect, 2 if is_selected else 1, border_radius=4)
    pygame.draw.line(surface, border_col, (rect.x + 8, rect.y), (rect.x + 8, rect.bottom), 1)
    pygame.draw.line(surface, border_col, (rect.right - 8, rect.y), (rect.right - 8, rect.bottom), 1)

    if is_selected and is_enabled:
        draw_kanban_arrow(surface, rect.x + 14, rect.centery, 8, border_col, "right")

    text_x = rect.x + 28 if (is_selected and is_enabled) else rect.x + 14
    s_txt = font.render(text, True, txt_col)
    surface.blit(s_txt, (text_x, rect.centery - s_txt.get_height() // 2))

    if sub:
        s_sub = font.render(sub, True, (160, 150, 140) if is_enabled else (100, 95, 95))
        surface.blit(s_sub, (rect.right - s_sub.get_width() - 14, rect.centery - s_sub.get_height() // 2))


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
        self.help_btn_rect = pygame.Rect(SCREEN_WIDTH - 250, 14, 226, 32)
        self.lang_btn_rect = pygame.Rect(SCREEN_WIDTH - 365, 14, 96, 32)
        self.mode_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 190, 52, 380, 32)
        self.start_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT - 64, 420, 44)
        self.card_rects: list[pygame.Rect] = []
        self.info_btn_rects: list[pygame.Rect] = []

        # Carregar imagem conceitual Sumi-E do título com vinheta escurecida
        self.bg_surf = None
        bg_path = os.path.join("assets", "concepts", "sumie_title_logo_concept.jpg")
        if os.path.exists(bg_path):
            try:
                try:
                    raw_img = pygame.image.load(bg_path).convert()
                except Exception:
                    raw_img = pygame.image.load(bg_path)
                self.bg_surf = pygame.transform.smoothscale(raw_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                vignette.fill((14, 14, 18, 195))  # 75% escurecido para legibilidade
                self.bg_surf.blit(vignette, (0, 0))
                self.bg_surf.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MAX)
            except Exception:
                self.bg_surf = None

        # Partículas de tinta / cinzas atmosféricas em suspensão
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
                "style": "Niten Ichi-ryu",
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
                "damage_desc": "Tanto / Kunai Aérea",
                "special_desc": "Salto Parabólico",
                "keys_p1": "[E] Tanto/Kunai | [R] Salto",
                "keys_p2": "[U] Tanto/Kunai | [I] Salto",
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
                "damage_desc": "Bomba Arco (Auto)",
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
                "damage_desc": "Flecha Letal (1-Hit)",
                "special_desc": "Flecha de Corda",
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

    def reset(self):
        """Reinicia o fluxo de seleção para o início (P1)."""
        self.selection_step = "P1"
        self.p1_ready = False
        self.p2_ready = False
        self.focus_zone = "GRID"
        self._axis_x_held_p1 = False
        self._axis_y_held_p1 = False
        self._axis_x_held_p2 = False
        self._axis_y_held_p2 = False
        if hasattr(self, "help_modal"):
            self.help_modal.close()

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
                    if dy != 0:
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
            is_p2 = (not self.vs_ai and len(ctrl_mgr.controllers) > 1 and ctrl2 is not None and getattr(event, "instance_id", None) == ctrl2.instance_id)

            target_player = "P2" if is_p2 else "P1"
            player_idx = 1 if is_p2 else 0

            # D-Pad botões virtuais (11=Up, 12=Down, 13=Left, 14=Right)
            from src.input.controller_manager import get_dpad_motion_from_event
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                move_cursor(target_player, d_dir[0], d_dir[1])
                return False

            # Confirmação: Apenas Botão 0 (✕ Cruz / A)
            if ctrl_mgr.is_event_menu_confirm(event, player_idx) or event.button == 0:
                res = handle_confirm(target_player)
                if res:
                    return res
                return False
            # Cancelar / Voltar: Apenas Botão 1 (○ Círculo / B)
            elif ctrl_mgr.is_event_menu_cancel(event, player_idx) or event.button == 1:
                res = handle_cancel(target_player)
                if res:
                    return res
                return False
            # Alternar modo 1P vs IA / 2P Versus: Botão 2 (▢ Quadrado / X)
            elif event.button == 2:
                self.vs_ai = not self.vs_ai
                self.selection_step = "P1"
                self.p1_ready = False
                self.p2_ready = False
                return False
            # Abrir Guia / Ajuda: Botão 3 (△ Triângulo / Y)
            elif event.button == 3:
                active_idx = self.p1_choice_idx if (not self.vs_ai or self.selection_step == "P1") else self.p2_choice_idx
                self.help_modal.open(GameHelpModal.TAB_FIGHTERS, fighter_idx=active_idx)
                return False

        elif event.type == pygame.JOYHATMOTION:
            ctrl2 = ctrl_mgr.get_controller_for_player(1)
            is_p2 = (not self.vs_ai and len(ctrl_mgr.controllers) > 1 and ctrl2 is not None and getattr(event, "instance_id", None) == ctrl2.instance_id)

            target_player = "P2" if is_p2 else "P1"
            from src.input.controller_manager import get_dpad_motion_from_event
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                move_cursor(target_player, d_dir[0], d_dir[1])

        elif event.type == pygame.JOYAXISMOTION:
            ctrl2 = ctrl_mgr.get_controller_for_player(1)
            is_p2 = (not self.vs_ai and len(ctrl_mgr.controllers) > 1 and ctrl2 is not None and getattr(event, "instance_id", None) == ctrl2.instance_id)

            target_player = "P2" if is_p2 else "P1"

            if target_player == "P1":
                if event.axis == 0:
                    if event.value > 0.60 and not self._axis_x_held_p1:
                        move_cursor("P1", 1, 0)
                        self._axis_x_held_p1 = True
                    elif event.value < -0.60 and not self._axis_x_held_p1:
                        move_cursor("P1", -1, 0)
                        self._axis_x_held_p1 = True
                    elif abs(event.value) < 0.30:
                        self._axis_x_held_p1 = False

                elif event.axis == 1:
                    if event.value > 0.60 and not self._axis_y_held_p1:
                        move_cursor("P1", 0, 1)
                        self._axis_y_held_p1 = True
                    elif event.value < -0.60 and not self._axis_y_held_p1:
                        move_cursor("P1", 0, -1)
                        self._axis_y_held_p1 = True
                    elif abs(event.value) < 0.30:
                        self._axis_y_held_p1 = False

            elif target_player == "P2":
                if event.axis == 0:
                    if event.value > 0.60 and not self._axis_x_held_p2:
                        move_cursor("P2", 1, 0)
                        self._axis_x_held_p2 = True
                    elif event.value < -0.60 and not self._axis_x_held_p2:
                        move_cursor("P2", -1, 0)
                        self._axis_x_held_p2 = True
                    elif abs(event.value) < 0.30:
                        self._axis_x_held_p2 = False

                elif event.axis == 1:
                    if event.value > 0.60 and not self._axis_y_held_p2:
                        move_cursor("P2", 0, 1)
                        self._axis_y_held_p2 = True
                    elif event.value < -0.60 and not self._axis_y_held_p2:
                        move_cursor("P2", 0, -1)
                        self._axis_y_held_p2 = True
                    elif abs(event.value) < 0.30:
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
            if self.mode_btn_rect.collidepoint(vx, vy):
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
            if self.start_btn_rect.collidepoint(vx, vy):
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
                if self.mode_btn_rect.collidepoint(mx, my):
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
                if self.start_btn_rect.collidepoint(mx, my):
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
        for p in self.particles:
            p["x"] += p["speed_x"] + 0.3 * math.sin(self.anim_timer + p["y"] * 0.05)
            p["y"] += p["speed_y"]
            if p["y"] < -10:
                p["y"] = SCREEN_HEIGHT + 10
                p["x"] = random.uniform(0, SCREEN_WIDTH)

    def get_selected_characters(self) -> tuple[str, str, bool]:
        p1_char = self.characters[self.p1_choice_idx]["id"]
        p2_char = self.characters[self.p2_choice_idx]["id"]
        return p1_char, p2_char, self.vs_ai

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        # 1. Carregar tipografia oriental autêntica
        font_oriental_title = get_title_font(28)
        font_oriental_name = get_title_font(17)
        font_oriental_action = get_title_font(19)
        font_zen_mid = get_text_font(18)
        font_zen_small = get_text_font(14)
        font_zen_tiny = get_text_font(12)
        font_zen_stamp = get_text_font(13)

        # 2. Fundo Sumi-E com Vinheta e Partículas Atmosféricas
        if self.bg_surf:
            surface.blit(self.bg_surf, (0, 0))
        else:
            surface.fill(COLOR_BG)
        surface.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MAX)

        for p in self.particles:
            pygame.draw.circle(surface, (175, 170, 165), (int(p["x"]), int(p["y"])), int(p["size"]))

        # 3. TOPO: Título Sumi-E Nobre Centralizado
        header_y = 12
        title_text = t("select_title")
        s_shadow = font_oriental_title.render(title_text, True, (8, 8, 10))
        s_title = font_oriental_title.render(title_text, True, COLOR_GOLD)
        title_x = SCREEN_WIDTH // 2 - s_title.get_width() // 2
        surface.blit(s_shadow, (title_x + 1, header_y + 7))
        surface.blit(s_title, (title_x, header_y + 6))

        # Botão Seletor Flutuante de Idioma [ PT | EN ] (Hanko / Kanban)
        lang = get_lang()
        self.lang_btn_rect = pygame.Rect(SCREEN_WIDTH - 365, header_y + 4, 96, 32)
        r_pt = pygame.Rect(self.lang_btn_rect.x, self.lang_btn_rect.y, 46, 32)
        r_en = pygame.Rect(self.lang_btn_rect.x + 50, self.lang_btn_rect.y, 46, 32)

        pt_bg = (52, 42, 24) if lang == LANG_PT else (24, 22, 24)
        pt_border = COLOR_GOLD if lang == LANG_PT else (75, 70, 68)
        pt_text_col = COLOR_GOLD if lang == LANG_PT else (145, 140, 135)
        pygame.draw.rect(surface, pt_bg, r_pt, border_radius=4)
        pygame.draw.rect(surface, pt_border, r_pt, 2 if lang == LANG_PT else 1, border_radius=4)
        t_pt = font_zen_small.render("PT", True, pt_text_col)
        surface.blit(t_pt, (r_pt.centerx - t_pt.get_width() // 2, r_pt.centery - t_pt.get_height() // 2))

        en_bg = (52, 42, 24) if lang == LANG_EN else (24, 22, 24)
        en_border = COLOR_GOLD if lang == LANG_EN else (75, 70, 68)
        en_text_col = COLOR_GOLD if lang == LANG_EN else (145, 140, 135)
        pygame.draw.rect(surface, en_bg, r_en, border_radius=4)
        pygame.draw.rect(surface, en_border, r_en, 2 if lang == LANG_EN else 1, border_radius=4)
        t_en = font_zen_small.render("EN", True, en_text_col)
        surface.blit(t_en, (r_en.centerx - t_en.get_width() // 2, r_en.centery - t_en.get_height() // 2))

        # Botão Superior Guia do Jogo & Ajuda
        self.help_btn_rect = pygame.Rect(SCREEN_WIDTH - 250, header_y + 4, 226, 32)
        help_label = "GUIA DO JOGO" if lang == LANG_PT else "GAME GUIDE"
        draw_kanban_menu_button(surface, font_zen_small, help_label, "[ H / ? ]", self.help_btn_rect, False, True, self.anim_timer)

        # 4. Botão Modo de Jogo (Kanban laqueado com encaixes de ferro)
        is_mode_focused = (self.focus_zone == "MODE_BTN")
        self.mode_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 190, 52, 380, 32)
        mode_text = ("MODO: 1P vs IA (TREINO)" if self.vs_ai else "MODO: 1P vs 2P (VERSUS)")
        draw_kanban_menu_button(surface, font_zen_small, mode_text, "[ CIMA / BAIXO ]", self.mode_btn_rect, is_mode_focused, True, self.anim_timer)

        # 5. Banner Indicador de Etapa / Instrução
        step_y = 90
        lang = get_lang()
        if self.vs_ai:
            if self.selection_step == "P1":
                step_title = "PASSO 1: ESCOLHA SEU COMBATENTE (P1)" if lang == LANG_PT else "STEP 1: CHOOSE YOUR FIGHTER (P1)"
                step_color = COLOR_HANKO_RED
                div_color = (160, 50, 45)
            else:
                step_title = "PASSO 2: ESCOLHA SEU OPONENTE (IA)" if lang == LANG_PT else "STEP 2: CHOOSE YOUR OPPONENT (AI)"
                step_color = COLOR_HANKO_BLUE
                div_color = (45, 100, 180)
        else:
            step_title = "MODO 2 JOGADORES (VERSUS LOCAL)" if lang == LANG_PT else "2 PLAYERS MODE (LOCAL VERSUS)"
            step_color = COLOR_GOLD
            div_color = (160, 130, 50)

        step_s = font_zen_mid.render(step_title, True, step_color)
        step_x = SCREEN_WIDTH // 2 - step_s.get_width() // 2
        surface.blit(step_s, (step_x, step_y))

        # Divisórias de pincel nas laterais do texto (sem riscar as letras)
        draw_brush_divider(surface, step_x - 140, step_y + 11, step_x - 16, color=div_color)
        draw_brush_divider(surface, step_x + step_s.get_width() + 16, step_y + 11, step_x + step_s.get_width() + 140, color=div_color)

        # 6. Grade Simétrica 6x2 (6 cards na Linha 1, 6 cards na Linha 2)
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

            draw_sumie_card(surface, rect, is_p1, is_p2, self.vs_ai, self.selection_step, self.anim_timer)

            # Badges Hanko P1 / IA no topo direito
            if is_p1 and is_p2:
                p2_label = "IA" if self.vs_ai else "P2"
                draw_hanko_stamp(surface, font_zen_stamp, p2_label, rect.right - 30, rect.y + 6, size=24, color=COLOR_HANKO_BLUE, border_w=1)
                draw_hanko_stamp(surface, font_zen_stamp, "P1", rect.right - 58, rect.y + 6, size=24, color=COLOR_HANKO_RED, border_w=1)
            elif is_p1:
                draw_hanko_stamp(surface, font_zen_stamp, "P1", rect.right - 30, rect.y + 6, size=24, color=COLOR_HANKO_RED, border_w=1)
            elif is_p2:
                p2_label = "IA" if self.vs_ai else "P2"
                draw_hanko_stamp(surface, font_zen_stamp, p2_label, rect.right - 30, rect.y + 6, size=24, color=COLOR_HANKO_BLUE, border_w=1)

            # Retrato Circular com Anel Ensō
            char_id = char_info["id"]
            portrait_cx = rect.x + 36
            portrait_cy = rect.y + 36
            ring_color = COLOR_HANKO_RED if is_p1 else (COLOR_HANKO_BLUE if is_p2 else char_info["color"])
            draw_enso_circle(surface, portrait_cx, portrait_cy, 26, ring_color, self.anim_timer)

            portrait_surf = get_portrait(char_id, size=(50, 50), circular=True)
            if portrait_surf is not None:
                surface.blit(portrait_surf, (portrait_cx - 25, portrait_cy - 25))
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
            name_surf = font_oriental_name.render(char_info["name"], True, char_info["color"])
            surface.blit(name_surf, (text_left, rect.y + 8))

            title_s = font_zen_small.render(char_info["title"], True, (185, 180, 175))
            surface.blit(title_s, (text_left, rect.y + 30))

            style_s = font_zen_tiny.render(char_info["style"], True, (220, 215, 210))
            surface.blit(style_s, (text_left, rect.y + 49))

            # Pincelada divisória
            draw_brush_divider(surface, rect.x + 8, rect.y + 70, rect.right - 8, color=(75, 70, 65))

            # Atributos e Estatísticas
            stats_y = rect.y + 76
            line_vel = font_zen_tiny.render(f"Vel: {char_info['speed_stars']}", True, COLOR_GOLD)
            line_dmg = font_zen_tiny.render(f"Dano: {char_info['damage_desc']}", True, (240, 205, 195))
            line_esp = font_zen_tiny.render(f"Esp: {char_info['special_desc']}", True, (200, 220, 240))

            surface.blit(line_vel, (rect.x + 8, stats_y))
            surface.blit(line_dmg, (rect.x + 8, stats_y + 18))
            surface.blit(line_esp, (rect.x + 8, stats_y + 36))

            # Caixa de Comandos / Teclas em Laca Negra
            ctrl_box = pygame.Rect(rect.x + 6, rect.bottom - 46, card_w - 38, 38)
            pygame.draw.rect(surface, COLOR_LACQUER_DARK, ctrl_box, border_radius=4)
            pygame.draw.rect(surface, (55, 50, 48), ctrl_box, 1, border_radius=4)
            p1_key_label = font_zen_tiny.render(f"P1: {char_info['keys_p1']}", True, (255, 200, 180))
            p2_key_label = font_zen_tiny.render(f"P2: {char_info['keys_p2']}", True, (180, 220, 255))
            surface.blit(p1_key_label, (ctrl_box.x + 4, ctrl_box.y + 3))
            surface.blit(p2_key_label, (ctrl_box.x + 4, ctrl_box.y + 19))

            # Botão [ ? ] como Selo Hanko pequeno
            info_btn = pygame.Rect(rect.right - 28, rect.bottom - 46, 22, 38)
            self.info_btn_rects.append(info_btn)
            draw_hanko_stamp(surface, font_zen_mid, "?", info_btn.x, info_btn.y + 7, size=24, color=COLOR_GOLD, border_w=1)

        # 7. Botão Grande de Ação em Laca Escarlate
        start_w = 420
        self.start_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - start_w // 2, SCREEN_HEIGHT - 64, start_w, 44)
        pulse = 0.5 + 0.5 * math.sin(self.anim_timer * 4.0)
        btn_bg = (140 + int(pulse * 25), 28 + int(pulse * 10), 24)
        pygame.draw.rect(surface, btn_bg, self.start_btn_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.start_btn_rect, 2, border_radius=6)

        st_label = ("INICIAR DUELO" if lang == LANG_PT else "START DUEL") if (not self.vs_ai or self.selection_step == "AI") else ("CONFIRMAR P1" if lang == LANG_PT else "CONFIRM P1")
        s_title_sh = font_oriental_action.render(st_label, True, (20, 10, 10))
        s_title_tx = font_oriental_action.render(st_label, True, COLOR_GOLD)
        hint_label = "[ ENTER / ESPAÇO ]" if lang == LANG_PT else "[ ENTER / SPACE ]"
        s_hint_tx = font_zen_small.render(hint_label, True, (245, 225, 185))

        total_content_w = s_title_tx.get_width() + 14 + s_hint_tx.get_width()
        content_x = self.start_btn_rect.centerx - total_content_w // 2

        surface.blit(s_title_sh, (content_x + 1, self.start_btn_rect.centery - s_title_tx.get_height() // 2 + 1))
        surface.blit(s_title_tx, (content_x, self.start_btn_rect.centery - s_title_tx.get_height() // 2))

        hint_x = content_x + s_title_tx.get_width() + 14
        surface.blit(s_hint_tx, (hint_x, self.start_btn_rect.centery - s_hint_tx.get_height() // 2))

        # 8. Rodapé com Instruções de Controle em Zen Antique
        from src.input.controller_manager import get_controller_manager
        ctrl_mgr = get_controller_manager()
        ctrl = ctrl_mgr.get_controller_for_player(0) if ctrl_mgr else None
        badge = ctrl_mgr.get_badge_text(0) if ctrl_mgr else ""

        guide_text = t("guide_nav")
        if badge and ctrl:
            btn_ok = ctrl.get_button_glyph("confirm")
            btn_back = ctrl.get_button_glyph("cancel")
            btn_mode = ctrl.get_button_glyph("attack")
            btn_guide = ctrl.get_button_glyph("special")
            guide_text = f"{badge}: D-Pad/Analógico = Navegar | [{btn_ok}] = Confirma | [{btn_back}] = Volta | [{btn_mode}] = Alternar Modo | [{btn_guide}] = Guia"

        guide_surf = font_zen_small.render(guide_text, True, (185, 180, 175))
        surface.blit(guide_surf, (SCREEN_WIDTH // 2 - guide_surf.get_width() // 2, SCREEN_HEIGHT - 18))

        # 9. Modal de Ajuda se aberto (sobreposto)
        if self.help_modal.is_open:
            self.help_modal.render(surface, font_large, font_mid, font_small)
