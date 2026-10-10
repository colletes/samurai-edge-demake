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
    CHAR_RIFLE, CHAR_KABUKI, CHAR_ARCHER, CHAR_PIRATE, CHAR_MUSKETEER, CHAR_RANDOM,
    CHAR_REN, CHAR_CHIYO, CHAR_BENKEI, CHAR_ORIN, CHAR_GORO, CHAR_ICHI,
    CHAR_VALERIUS, CHAR_SEIMEI, CHAR_DAIKI, CHAR_AOI, CHAR_RAIDEN, CHAR_HENDRIKA,
    COLOR_PIRATE_AURA, COLOR_MUSKETEER_AURA, get_asset_path
)

from src.isometric.iso_math import world_to_iso
from src.entities.voxel_models import render_voxel_humanoid, render_voxel_doberman
from src.ui.game_help import GameHelpModal
from src.i18n import t, get_lang, toggle_lang, LANG_PT, LANG_EN
from src.ui.portraits import get_portrait
from src.ui.fonts import get_title_font, get_text_font
from src.effects import parchment as pm
from src.roster import ROSTER_ORDER
from src.edition import is_demo, DEMO_FIGHTERS

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


def _draw_landscape_left(surface, base_x: int, base_y: int, color: tuple):
    """Desenha árvore estilizada Sumi-E no lado esquerdo da moldura."""
    # Tronco principal (linhas verticais paralelas)
    pygame.draw.line(surface, color, (base_x + 2, base_y), (base_x + 2, base_y + 80), 2)
    pygame.draw.line(surface, (color[0] - 30, color[1] - 30, color[2] - 30), (base_x + 5, base_y + 2), (base_x + 5, base_y + 78), 1)
    
    # Ramos principais (pinceladas angulares)
    pygame.draw.line(surface, color, (base_x + 2, base_y + 20), (base_x - 8, base_y + 10), 1)
    pygame.draw.line(surface, color, (base_x + 2, base_y + 35), (base_x - 6, base_y + 28), 1)
    pygame.draw.line(surface, color, (base_x + 2, base_y + 50), (base_x - 10, base_y + 45), 1)
    pygame.draw.line(surface, color, (base_x + 2, base_y + 25), (base_x + 12, base_y + 15), 1)
    pygame.draw.line(surface, color, (base_x + 2, base_y + 45), (base_x + 14, base_y + 38), 1)
    pygame.draw.line(surface, color, (base_x + 2, base_y + 60), (base_x + 10, base_y + 55), 1)
    
    # Folhagem (pinceladas circulares aglomeradas)
    for ox, oy, r in [(-10, 8, 8), (-8, 22, 7), (-12, 38, 9), (12, 12, 8), (14, 35, 7), (10, 52, 8)]:
        pygame.draw.circle(surface, (color[0] + 20, color[1] + 20, color[2] + 20), (base_x + ox, base_y + oy), r, 1)


def _draw_landscape_right(surface, base_x: int, base_y: int, color: tuple):
    """Desenha árvore estilizada Sumi-E no lado direito da moldura."""
    # Tronco principal (linhas verticais paralelas)
    pygame.draw.line(surface, color, (base_x - 2, base_y), (base_x - 2, base_y + 80), 2)
    pygame.draw.line(surface, (color[0] - 30, color[1] - 30, color[2] - 30), (base_x - 5, base_y + 2), (base_x - 5, base_y + 78), 1)
    
    # Ramos principais (pinceladas angulares, espelhados)
    pygame.draw.line(surface, color, (base_x - 2, base_y + 20), (base_x + 8, base_y + 10), 1)
    pygame.draw.line(surface, color, (base_x - 2, base_y + 35), (base_x + 6, base_y + 28), 1)
    pygame.draw.line(surface, color, (base_x - 2, base_y + 50), (base_x + 10, base_y + 45), 1)
    pygame.draw.line(surface, color, (base_x - 2, base_y + 25), (base_x - 12, base_y + 15), 1)
    pygame.draw.line(surface, color, (base_x - 2, base_y + 45), (base_x - 14, base_y + 38), 1)
    pygame.draw.line(surface, color, (base_x - 2, base_y + 60), (base_x - 10, base_y + 55), 1)
    
    # Folhagem (pinceladas circulares aglomeradas)
    for ox, oy, r in [(10, 8, 8), (8, 22, 7), (12, 38, 9), (-12, 12, 8), (-14, 35, 7), (-10, 52, 8)]:
        pygame.draw.circle(surface, (color[0] + 20, color[1] + 20, color[2] + 20), (base_x + ox, base_y + oy), r, 1)


def format_command_text(command_str: str, max_width: int = 155, font = None) -> str:
    """
    Formata texto de comando para caber na caixa de controles.
    Se necessário, trunca com reticências.
    Exemplo: "[E] Iai Flash (Ataque)" -> "[E] Iai Flash"
    """
    if not command_str or not font:
        return command_str
    
    # Tentar remover a descrição entre parênteses para economizar espaço
    import re
    # Remove " (palavra)" no final, e.g., " (Ataque)" ou " (Attack)"
    simplified = re.sub(r'\s*\([^)]+\)\s*$', '', command_str)
    
    # Se ainda for muito longo, truncar com "..."
    while font.size(simplified)[0] > max_width and len(simplified) > 5:
        simplified = simplified[:-1]
    
    if font.size(simplified)[0] > max_width:
        simplified = simplified[:20] + "..."
    
    return simplified


def draw_scroll_frame(surface, margin_top: int = 100, margin_bottom: int = 90, margin_sides: int = 20):
    """
    Desenha uma moldura decorativa tipo pergaminho nos lados da tela,
    com paisagem Sumi-E (árvores) inspirada na imagem de referência.
    """
    # Cores inspiradas em pergaminho antigo e ornamentos de madeira
    scroll_color = (245, 235, 215)
    scroll_dark = (210, 195, 170)
    ornament_color = (160, 140, 110)
    shadow_color = (100, 95, 90)
    highlight_color = (255, 255, 245)
    landscape_color = (140, 130, 120)
    
    # Função local para desenhar rolete com mais detalhes
    def draw_rolete_detailed(x, y):
        pygame.draw.circle(surface, ornament_color, (x, y), 8)
        pygame.draw.circle(surface, shadow_color, (x, y), 8, 2)
        pygame.draw.circle(surface, highlight_color, (x - 2, y - 3), 2)  # Realce
        pygame.draw.circle(surface, (180, 160, 140), (x, y), 5, 1)  # Padrão concêntrico
    
    # === COLUNA ESQUERDA ===
    left_x = margin_sides - 8
    left_rect = pygame.Rect(left_x, margin_top, 16, SCREEN_HEIGHT - margin_top - margin_bottom)
    
    # Fundo principal
    pygame.draw.rect(surface, scroll_color, left_rect)
    
    # Padrão de madeira: linhas verticais paralelas
    for x_off in [1, 5, 9, 13]:
        pygame.draw.line(surface, (230, 220, 200), (left_x + x_off, margin_top), (left_x + x_off, SCREEN_HEIGHT - margin_bottom), 1)
    
    # Pequenas linhas decorativas (padrão grid sutil)
    for y in range(margin_top, SCREEN_HEIGHT - margin_bottom, 12):
        pygame.draw.line(surface, ornament_color, (left_x + 2, y), (left_x + 14, y), 1)
    
    # Sombra interna (borda esquerda)
    pygame.draw.line(surface, shadow_color, (left_x, margin_top), (left_x, SCREEN_HEIGHT - margin_bottom), 2)
    # Borda direita (highlight)
    pygame.draw.line(surface, highlight_color, (left_x + 15, margin_top), (left_x + 15, SCREEN_HEIGHT - margin_bottom), 1)
    
    # Rolete de madeira no topo e base
    draw_rolete_detailed(left_x + 8, margin_top - 8)
    draw_rolete_detailed(left_x + 8, SCREEN_HEIGHT - margin_bottom + 8)
    
    # Paisagem Sumi-E (árvore) no lado esquerdo
    _draw_landscape_left(surface, left_x - 12, margin_top + 50, landscape_color)
    
    # === COLUNA DIREITA ===
    right_x = SCREEN_WIDTH - margin_sides - 8
    right_rect = pygame.Rect(right_x, margin_top, 16, SCREEN_HEIGHT - margin_top - margin_bottom)
    
    # Fundo principal
    pygame.draw.rect(surface, scroll_color, right_rect)
    
    # Padrão de madeira: linhas verticais paralelas
    for x_off in [1, 5, 9, 13]:
        pygame.draw.line(surface, (230, 220, 200), (right_x + x_off, margin_top), (right_x + x_off, SCREEN_HEIGHT - margin_bottom), 1)
    
    # Pequenas linhas decorativas (padrão grid sutil)
    for y in range(margin_top, SCREEN_HEIGHT - margin_bottom, 12):
        pygame.draw.line(surface, ornament_color, (right_x + 2, y), (right_x + 14, y), 1)
    
    # Sombra interna (borda direita)
    pygame.draw.line(surface, shadow_color, (right_x + 16, margin_top), (right_x + 16, SCREEN_HEIGHT - margin_bottom), 2)
    # Borda esquerda (highlight)
    pygame.draw.line(surface, highlight_color, (right_x, margin_top), (right_x, SCREEN_HEIGHT - margin_bottom), 1)
    
    # Rolete de madeira no topo e base
    draw_rolete_detailed(right_x + 8, margin_top - 8)
    draw_rolete_detailed(right_x + 8, SCREEN_HEIGHT - margin_bottom + 8)
    
    # Paisagem Sumi-E (árvore) no lado direito
    _draw_landscape_right(surface, right_x + 24, margin_top + 50, landscape_color)
    
    # === LINHAS DECORATIVAS HORIZONTAIS ===
    # Linha no topo (abaixo do título)
    draw_brush_divider(surface, margin_sides + 16, margin_top + 35, SCREEN_WIDTH - margin_sides - 16, color=ornament_color)
    # Linha na base (acima do botão)
    draw_brush_divider(surface, margin_sides + 16, SCREEN_HEIGHT - margin_bottom - 8, SCREEN_WIDTH - margin_sides - 16, color=ornament_color)


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


def draw_mystery_silhouette(surface: pygame.Surface, cx: int, cy: int, radius: int = 20):
    """Desenha uma silhueta de sombra indefinida no estilo Sumi-E para personagens em produção."""
    orb = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(orb, (16, 15, 18, 235), (radius, radius), radius)
    # Ombros e vestes em nanquim escuro
    pygame.draw.ellipse(orb, (36, 34, 40, 240), (2, radius + 2, (radius - 2) * 2, radius))
    # Cabeça / capuz encobrindo o rosto
    pygame.draw.circle(orb, (44, 42, 48, 240), (radius, radius - 3), int(radius * 0.52))
    surface.blit(orb, (cx - radius, cy - radius))


def draw_round_help_button(surface, font, rect: pygame.Rect, anim_time: float):
    """Ícone de ajuda circular: disco claro, aro dourado e '?' dourado, com brilho ao passar o mouse."""
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    center = rect.center
    radius = rect.width // 2
    if hovered:
        glow = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 215, 90, 90), (glow.get_width() // 2, glow.get_height() // 2), radius + 7)
        surface.blit(glow, (rect.x - 8, rect.y - 8))
    pygame.draw.circle(surface, (244, 238, 222) if hovered else (226, 218, 198), center, radius)
    pygame.draw.circle(surface, COLOR_GOLD, center, radius, 3)
    pygame.draw.circle(surface, (150, 112, 30), center, radius - 5, 1)
    q = font.render("?", True, (150, 104, 18))
    surface.blit(q, (center[0] - q.get_width() // 2, center[1] - q.get_height() // 2))


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
    arcade_mode = False  # Arcade: só o P1 escolhe, sem modo 2P nem etapa do oponente

    @property
    def vs_ai(self) -> bool:
        return self._vs_ai

    @vs_ai.setter
    def vs_ai(self, value: bool):
        self._vs_ai = True if self.arcade_mode else value

    def __init__(self, ai_difficulty: str = "normal"):
        self.p1_choice_idx = 0  # Kenshin
        self.p2_choice_idx = ROSTER_ORDER.index(CHAR_ARCHER) if is_demo() else 1  # Musashi (na demo, Tomoe)
        self.p1_ready = False
        self.p2_ready = False
        self.vs_ai = True
        self.ai_difficulty = ai_difficulty if ai_difficulty in ("easy", "normal", "hard") else "normal"
        self.selection_step = "P1"  # "P1" -> "AI" (no modo 1P vs IA)
        self.focus_zone = "GRID"    # "GRID" ou "MODE_BTN"
        self._axis_x_held_p1 = False
        self._axis_y_held_p1 = False
        self._axis_x_held_p2 = False
        self._axis_y_held_p2 = False
        self.anim_timer = 0.0
        self._last_col = 2          # coluna lembrada ao subir da carta Aleatório para a grade
        self.reveal: dict | None = None  # sorteio em andamento (roleta de lutadores antes de iniciar)

        # Modal de Ajuda Completa do Jogo e Guia dos 12 Guerreiros
        self.help_modal = GameHelpModal()
        self.help_btn_rect = pygame.Rect(SCREEN_WIDTH - 64, 14, 36, 36)
        self.lang_btn_rect = pygame.Rect(SCREEN_WIDTH - 170, 14, 96, 32)
        self.mode_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 190, 52, 380, 32)
        self.difficulty_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.start_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT - 64, 420, 44)
        self.card_rects: list[pygame.Rect] = []
        self.info_btn_rects: list[pygame.Rect] = []

        # Carregar imagem conceitual Sumi-E do título com vinheta escurecida
        self.bg_surf = None
        bg_path = get_asset_path("assets/concepts/sumie_title_logo_concept.jpg")
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
        self._characters_lang = None
        self._characters_cache = []
        self.petals = pm.PetalField()
        pm.prewarm([(190, 104, i * 7 + 3) for i in range(24)])

    @property
    def characters(self):
        # Reconstrói os textos quando o idioma muda
        lang = get_lang()
        if self._characters_lang != lang:
            self._characters_cache = self._build_characters()
            self._characters_lang = lang
        return self._characters_cache

    def _build_characters(self):
        """12 guerreiros na ordem do elenco (src/roster.py) e, por último, a carta Aleatório."""
        by_id = {c["id"]: c for c in self._build_fighters()}
        cards = [by_id[char_id] for char_id in ROSTER_ORDER]
        cards.append({
            "id": CHAR_RANDOM,
            "name": t("char_random_name"),
            "title": t("char_random_title"),
            "style": t("char_random_style"),
            "color": (200, 170, 90),
            "speed_stars": "", "damage_desc": "", "special_desc": "", "keys_p1": "", "keys_p2": "",
        })
        return cards

    @property
    def random_idx(self) -> int:
        return len(self.characters) - 1

    def _grid_step(self, idx: int, dx: int, dy: int) -> int:
        """Move o cursor; na demo pula as cartas bloqueadas."""
        new = self._raw_grid_step(idx, dx, dy)
        if not is_demo():
            return new
        for _ in range(40):
            if not self.is_locked(new):
                return new
            new = self._raw_grid_step(new, dx, dy)
        return idx

    def is_locked(self, idx: int) -> bool:
        """Indica se a carta está bloqueada (na demo ou se o personagem ainda está em desenvolvimento)."""
        if idx == self.random_idx or idx >= len(self.characters):
            return False
        char_info = self.characters[idx]
        if not char_info.get("ready", True):
            return True
        return is_demo() and char_info["id"] not in DEMO_FIGHTERS

    def _raw_grid_step(self, idx: int, dx: int, dy: int) -> int:
        """Move o cursor na grade 6x4 de guerreiros mais a carta Aleatório numa quinta linha."""
        cols, rnd = 6, self.random_idx
        if idx == rnd:
            row, col = 4, self._last_col
        else:
            row, col = divmod(idx, cols)
            self._last_col = col
        if dy:
            row = (row + dy) % 5
        if dx and row != 4:
            col = (col + dx) % cols
        return rnd if row == 4 else row * cols + col

    def _build_fighters(self):
        return [
            # 12 Veteranos (Prontos)
            {
                "id": CHAR_KENSHIN,
                "name": t("char_kenshi_name"),
                "title": t("char_kenshi_title"),
                "style": t("char_kenshi_style"),
                "color": COLOR_RED_AURA,
                "speed_stars": t("char_kenshi_speed"),
                "damage_desc": t("char_kenshi_damage"),
                "special_desc": t("char_kenshi_special"),
                "keys_p1": t("char_kenshi_keys_p1"),
                "keys_p2": t("char_kenshi_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_MUSASHI,
                "name": t("char_musashi_name"),
                "title": t("char_musashi_title"),
                "style": t("char_musashi_style"),
                "color": COLOR_BLUE_AURA,
                "speed_stars": t("char_musashi_speed"),
                "damage_desc": t("char_musashi_damage"),
                "special_desc": t("char_musashi_special"),
                "keys_p1": t("char_musashi_keys_p1"),
                "keys_p2": t("char_musashi_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_NINJA,
                "name": t("char_hanzo_name"),
                "title": t("char_hanzo_title"),
                "style": t("char_hanzo_style"),
                "color": COLOR_YELLOW_AURA,
                "speed_stars": t("char_hanzo_speed"),
                "damage_desc": t("char_hanzo_damage"),
                "special_desc": t("char_hanzo_special"),
                "keys_p1": t("char_hanzo_keys_p1"),
                "keys_p2": t("char_hanzo_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_AMERICAN,
                "name": t("char_joe_name"),
                "title": t("char_joe_title"),
                "style": t("char_joe_style"),
                "color": (255, 130, 45),
                "speed_stars": t("char_joe_speed"),
                "damage_desc": t("char_joe_damage"),
                "special_desc": t("char_joe_special"),
                "keys_p1": t("char_joe_keys_p1"),
                "keys_p2": t("char_joe_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_SAITOU,
                "name": t("char_saitou_name"),
                "title": t("char_saitou_title"),
                "style": t("char_saitou_style"),
                "color": COLOR_SAITOU_LIGHT_BLUE,
                "speed_stars": t("char_saitou_speed"),
                "damage_desc": t("char_saitou_damage"),
                "special_desc": t("char_saitou_special"),
                "keys_p1": t("char_saitou_keys_p1"),
                "keys_p2": t("char_saitou_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_RIFLE,
                "name": t("char_teppo_name"),
                "title": t("char_teppo_title"),
                "style": t("char_teppo_style"),
                "color": (225, 170, 100),
                "speed_stars": t("char_teppo_speed"),
                "damage_desc": t("char_teppo_damage"),
                "special_desc": t("char_teppo_special"),
                "keys_p1": t("char_teppo_keys_p1"),
                "keys_p2": t("char_teppo_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_PURPLE,
                "name": t("char_murasaki_name"),
                "title": t("char_murasaki_title"),
                "style": t("char_murasaki_style"),
                "color": COLOR_PURPLE_AURA,
                "speed_stars": t("char_murasaki_speed"),
                "damage_desc": t("char_murasaki_damage"),
                "special_desc": t("char_murasaki_special"),
                "keys_p1": t("char_murasaki_keys_p1"),
                "keys_p2": t("char_murasaki_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_GRAY,
                "name": t("char_kasumi_name"),
                "title": t("char_kasumi_title"),
                "style": t("char_kasumi_style"),
                "color": (165, 180, 190),
                "speed_stars": t("char_kasumi_speed"),
                "damage_desc": t("char_kasumi_damage"),
                "special_desc": t("char_kasumi_special"),
                "keys_p1": t("char_kasumi_keys_p1"),
                "keys_p2": t("char_kasumi_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_KABUKI,
                "name": t("char_okuni_name"),
                "title": t("char_okuni_title"),
                "style": t("char_okuni_style"),
                "color": (240, 115, 30),
                "speed_stars": t("char_okuni_speed"),
                "damage_desc": t("char_okuni_damage"),
                "special_desc": t("char_okuni_special"),
                "keys_p1": t("char_okuni_keys_p1"),
                "keys_p2": t("char_okuni_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_ARCHER,
                "name": t("char_tomoe_name"),
                "title": t("char_tomoe_title"),
                "style": t("char_tomoe_style"),
                "color": (110, 195, 135),
                "speed_stars": t("char_tomoe_speed"),
                "damage_desc": t("char_tomoe_damage"),
                "special_desc": t("char_tomoe_special"),
                "keys_p1": t("char_tomoe_keys_p1"),
                "keys_p2": t("char_tomoe_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_PIRATE,
                "name": t("char_anne_name"),
                "title": t("char_anne_title"),
                "style": t("char_anne_style"),
                "color": COLOR_PIRATE_AURA,
                "speed_stars": t("char_anne_speed"),
                "damage_desc": t("char_anne_damage"),
                "special_desc": t("char_anne_special"),
                "keys_p1": t("char_anne_keys_p1"),
                "keys_p2": t("char_anne_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_MUSKETEER,
                "name": t("char_julie_name"),
                "title": t("char_julie_title"),
                "style": t("char_julie_style"),
                "color": COLOR_MUSKETEER_AURA,
                "speed_stars": t("char_julie_speed"),
                "damage_desc": t("char_julie_damage"),
                "special_desc": t("char_julie_special"),
                "keys_p1": t("char_julie_keys_p1"),
                "keys_p2": t("char_julie_keys_p2"),
                "ready": True,
            },
            # Ciclo 1 (Prontos)
            {
                "id": CHAR_REN,
                "name": t("char_ren_name"),
                "title": t("char_ren_title"),
                "style": t("char_ren_style"),
                "color": (235, 175, 50),
                "speed_stars": t("char_ren_speed"),
                "damage_desc": t("char_ren_damage"),
                "special_desc": t("char_ren_special"),
                "keys_p1": t("char_ren_keys_p1"),
                "keys_p2": t("char_ren_keys_p2"),
                "ready": True,
            },
            {
                "id": CHAR_CHIYO,
                "name": t("char_chiyo_name"),
                "title": t("char_chiyo_title"),
                "style": t("char_chiyo_style"),
                "color": (210, 45, 60),
                "speed_stars": t("char_chiyo_speed"),
                "damage_desc": t("char_chiyo_damage"),
                "special_desc": t("char_chiyo_special"),
                "keys_p1": t("char_chiyo_keys_p1"),
                "keys_p2": t("char_chiyo_keys_p2"),
                "ready": True,
            },
            # Ciclos 2 a 6 (Em desenvolvimento)
            {
                "id": CHAR_BENKEI,
                "name": "???",
                "title": "",
                "style": "",
                "color": (170, 90, 60),
                "speed_stars": "",
                "damage_desc": "",
                "special_desc": "",
                "keys_p1": "",
                "keys_p2": "",
                "ready": False,
            },
            {
                "id": CHAR_ORIN,
                "name": "???",
                "title": "",
                "style": "",
                "color": (220, 110, 160),
                "speed_stars": "",
                "damage_desc": "",
                "special_desc": "",
                "keys_p1": "",
                "keys_p2": "",
                "ready": False,
            },
            {
                "id": CHAR_GORO,
                "name": "???",
                "title": "",
                "style": "",
                "color": (120, 150, 80),
                "speed_stars": "",
                "damage_desc": "",
                "special_desc": "",
                "keys_p1": "",
                "keys_p2": "",
                "ready": False,
            },
            {
                "id": CHAR_ICHI,
                "name": "???",
                "title": "",
                "style": "",
                "color": (180, 175, 170),
                "speed_stars": "",
                "damage_desc": "",
                "special_desc": "",
                "keys_p1": "",
                "keys_p2": "",
                "ready": False,
            },
            {
                "id": CHAR_VALERIUS,
                "name": "???",
                "title": "",
                "style": "",
                "color": (140, 70, 180),
                "speed_stars": "",
                "damage_desc": "",
                "special_desc": "",
                "keys_p1": "",
                "keys_p2": "",
                "ready": False,
            },
            {
                "id": CHAR_SEIMEI,
                "name": "???",
                "title": "",
                "style": "",
                "color": (80, 160, 210),
                "speed_stars": "",
                "damage_desc": "",
                "special_desc": "",
                "keys_p1": "",
                "keys_p2": "",
                "ready": False,
            },
            {
                "id": CHAR_DAIKI,
                "name": "???",
                "title": "",
                "style": "",
                "color": (190, 150, 90),
                "speed_stars": "",
                "damage_desc": "",
                "special_desc": "",
                "keys_p1": "",
                "keys_p2": "",
                "ready": False,
            },
            {
                "id": CHAR_AOI,
                "name": "???",
                "title": "",
                "style": "",
                "color": (60, 170, 150),
                "speed_stars": "",
                "damage_desc": "",
                "special_desc": "",
                "keys_p1": "",
                "keys_p2": "",
                "ready": False,
            },
            {
                "id": CHAR_RAIDEN,
                "name": "???",
                "title": "",
                "style": "",
                "color": (220, 140, 50),
                "speed_stars": "",
                "damage_desc": "",
                "special_desc": "",
                "keys_p1": "",
                "keys_p2": "",
                "ready": False,
            },
            {
                "id": CHAR_HENDRIKA,
                "name": "???",
                "title": "",
                "style": "",
                "color": (90, 180, 120),
                "speed_stars": "",
                "damage_desc": "",
                "special_desc": "",
                "keys_p1": "",
                "keys_p2": "",
                "ready": False,
            },
        ]

    def cycle_ai_difficulty(self):
        """Alterna o nível de dificuldade da IA (Fácil -> Normal -> Difícil)."""
        if self.arcade_mode:
            return  # no Arcade a dificuldade vem do menu próprio e muda durante a jornada
        from src.audio.sound_manager import SoundManager
        from src.audio.sound_events import SoundEvent
        from src.input.controls_storage import load_controls_config, save_controls_config
        from src.input.controller_manager import get_controller_manager
        order = ["easy", "normal", "hard"]
        cur_idx = order.index(self.ai_difficulty) if self.ai_difficulty in order else 1
        self.ai_difficulty = order[(cur_idx + 1) % len(order)]
        SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
        cfg = load_controls_config()
        save_controls_config(cfg.get("keyboard", {}), get_controller_manager(), cfg.get("touch_mode", "auto"), audio_cfg=cfg.get("audio", {}), ai_difficulty=self.ai_difficulty)

    def reset(self):
        """Reinicia o fluxo de seleção para o início (P1)."""
        self.selection_step = "P1"
        self.p1_ready = False
        self.p2_ready = False
        self.reveal = None
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
          - False: continuar na tela de seleção (inclusive durante o sorteio; ao terminar, `update` devolve True)
        """
        if self.reveal is not None:
            return False
        result = self._handle_event_inner(event)
        if result is True and self.random_idx in ((self.p1_choice_idx,) if self.arcade_mode else (self.p1_choice_idx, self.p2_choice_idx)):
            self._start_reveal()
            return False
        return result

    def _start_reveal(self):
        """Inicia a roleta que revela quem o Aleatório sorteou (P1 e/ou oponente)."""
        playable_indices = [i for i, c in enumerate(self.characters) if c.get("ready", True) and c["id"] != CHAR_RANDOM]
        targets = {}
        for player, idx in (("P1", self.p1_choice_idx), ("P2", self.p2_choice_idx)):
            if idx == self.random_idx and (player == "P1" or not self.arcade_mode):
                targets[player] = random.choice(playable_indices) if playable_indices else 0
        self.reveal = {"t": 0.0, "roulette": 1.1, "hold": 0.55, "targets": targets, "last_step": {}}

    def _update_reveal(self, dt: float) -> bool:
        """Avança a roleta; devolve True quando o sorteio terminou e a partida deve começar."""
        rv = self.reveal
        rv["t"] += dt
        playable_indices = [i for i, c in enumerate(self.characters) if c.get("ready", True) and c["id"] != CHAR_RANDOM]
        n = len(playable_indices) if playable_indices else 1
        progress = min(1.0, rv["t"] / rv["roulette"])
        for player, target in rv["targets"].items():
            total_steps = 2 * n + target
            step_idx = int(total_steps * (1.0 - (1.0 - progress) ** 2.4)) % n
            idx = playable_indices[step_idx] if playable_indices else 0
            if progress >= 1.0:
                idx = target
            if rv["last_step"].get(player) != idx:
                rv["last_step"][player] = idx
                try:
                    from src.audio.sound_events import SoundEvent
                    from src.audio.sound_manager import SoundManager
                    SoundManager.get_instance().play(SoundEvent.MENU_SELECT)
                except Exception:
                    pass
            if player == "P1":
                self.p1_choice_idx = idx
            else:
                self.p2_choice_idx = idx
        if rv["t"] >= rv["roulette"] + rv["hold"]:
            self.reveal = None
            return True
        return False

    def _handle_event_inner(self, event: pygame.event.Event) -> str | bool:
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
                if dy < 0 and active_idx < cols and not self.arcade_mode:
                    self.focus_zone = "MODE_BTN"
                    return

                new_idx = self._grid_step(active_idx, dx, dy)

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
                    self.p2_choice_idx = self._grid_step(self.p2_choice_idx, dx, dy)

        def handle_confirm(player: str) -> str | bool:
            if self.focus_zone == "MODE_BTN":
                self.vs_ai = not self.vs_ai
                self.selection_step = "P1"
                self.p1_ready = False
                self.p2_ready = False
                return False

            target_idx = self.p1_choice_idx if (self.vs_ai and self.selection_step == "P1") or (not self.vs_ai and player == "P1") else self.p2_choice_idx
            if self.is_locked(target_idx):
                try:
                    from src.audio.sound_events import SoundEvent
                    from src.audio.sound_manager import SoundManager
                    SoundManager.get_instance().play(SoundEvent.SWORD_CLASH)
                except Exception:
                    pass
                return False

            if self.vs_ai:
                if self.selection_step == "P1":
                    if self.arcade_mode:
                        return True
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
            num_controllers = ctrl_mgr.get_controller_count()

            # P2 só controla pelo controle se houver um segundo controle dedicado conectado
            is_p2 = (
                not self.vs_ai and
                num_controllers > 1 and
                ctrl2 is not None and
                getattr(event, "instance_id", None) == ctrl2.instance_id
            )

            target_player = "P2" if is_p2 else "P1"
            player_idx = 1 if is_p2 else 0

            # D-Pad botões virtuais (11=Up, 12=Down, 13=Left, 14=Right)
            from src.input.controller_manager import get_dpad_motion_from_event
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                move_cursor(target_player, d_dir[0], d_dir[1])
                return False

            # Confirmação: Botão 0 (✕ Cruz / A) OU Botão 2 (▢ Quadrado / X)
            if ctrl_mgr.is_event_menu_confirm(event, player_idx) or event.button in (0, 2):
                res = handle_confirm(target_player)
                if res:
                    return res
                return False
            # Cancelar / Voltar: Botão 1 (○ Círculo / B)
            elif ctrl_mgr.is_event_menu_cancel(event, player_idx) or event.button == 1:
                res = handle_cancel(target_player)
                if res:
                    return res
                return False
            # Alternar modo 1P vs IA / 2P Versus: Select / Touchpad / L1 / R1
            elif event.button in (4, 9, 10):
                self.vs_ai = not self.vs_ai
                self.selection_step = "P1"
                self.p1_ready = False
                self.p2_ready = False
                return False
            # Abrir Guia / Ajuda: Botão 3 (△ Triângulo / Y)
            elif event.button == 3:
                active_idx = self.p1_choice_idx if (not self.vs_ai or self.selection_step == "P1") else self.p2_choice_idx
                if active_idx < len(self.characters) and self.characters[active_idx].get("ready", True):
                    self.help_modal.open(GameHelpModal.TAB_FIGHTERS, fighter_idx=min(active_idx, 11))
                return False

        elif event.type == pygame.JOYHATMOTION:
            ctrl2 = ctrl_mgr.get_controller_for_player(1)
            num_controllers = ctrl_mgr.get_controller_count()
            is_p2 = (
                not self.vs_ai and
                num_controllers > 1 and
                ctrl2 is not None and
                getattr(event, "instance_id", None) == ctrl2.instance_id
            )
            target_player = "P2" if is_p2 else "P1"
            from src.input.controller_manager import get_dpad_motion_from_event
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                move_cursor(target_player, d_dir[0], d_dir[1])

        elif event.type == pygame.JOYAXISMOTION:
            ctrl2 = ctrl_mgr.get_controller_for_player(1)
            num_controllers = ctrl_mgr.get_controller_count()
            is_p2 = (
                not self.vs_ai and
                num_controllers > 1 and
                ctrl2 is not None and
                getattr(event, "instance_id", None) == ctrl2.instance_id
            )
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
                if active_idx < len(self.characters) and self.characters[active_idx].get("ready", True):
                    self.help_modal.open(GameHelpModal.TAB_FIGHTERS, fighter_idx=min(active_idx, 11))
                return False
            elif event.key == pygame.K_l:
                toggle_lang()
                return False
            elif event.key == pygame.K_g:
                self.cycle_ai_difficulty()
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
            elif event.key == pygame.K_e:
                # Tecla de ação/ataque de P1 confirma P1
                res = handle_confirm("P1")
                if res:
                    return res
                return False

            # Teclado P2 (SETAS)
            if event.key == pygame.K_LEFT:
                move_cursor("P2", -1, 0)
            elif event.key == pygame.K_RIGHT:
                move_cursor("P2", 1, 0)
            elif event.key == pygame.K_UP:
                move_cursor("P2", 0, -1)
            elif event.key == pygame.K_DOWN:
                move_cursor("P2", 0, 1)
            elif not self.vs_ai and event.key in (
                pygame.K_u, pygame.K_o,
                pygame.K_KP_ENTER, pygame.K_RCTRL, pygame.K_RSHIFT, pygame.K_BACKSLASH
            ):
                # Ação primária [U], [O] ou teclas direitas confirmam P2 diretamente!
                res = handle_confirm("P2")
                if res:
                    return res
                return False

            elif not self.vs_ai and event.key == pygame.K_i:
                # Item 5: Tecla [I] é a tecla de Cancelar/Voltar para P2 (como Círculo no gamepad)
                res = handle_cancel("P2")
                if res:
                    return res
                return False

            # Teclas de Confirmação Universais de Teclado (SPACE, RETURN / ENTER e Ataque)
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e, pygame.K_j):
                if self.vs_ai:
                    res = handle_confirm("P1")
                else:
                    # Se P1 já está confirmado (seja pelo gamepad ou teclado),
                    # qualquer SPACE ou RETURN confirma o Jogador 2!
                    if self.p1_ready and not self.p2_ready:
                        res = handle_confirm("P2")
                    elif not self.p1_ready:
                        res = handle_confirm("P1")
                    else:
                        # Ambos confirmados: iniciar partida
                        return True
                if res:
                    return res
                return False

            elif event.key == pygame.K_ESCAPE:
                # Item 5: ESC é o botão Cancelar/Voltar exclusivo de P1 / Menu; não cancela ações de P2
                res = handle_cancel("P1")
                if res:
                    return res
                return False

            elif event.key == pygame.K_BACKSPACE:
                # BACKSPACE cancela P2 no modo 2P, ou P1 se vs AI
                target = "P2" if not self.vs_ai else "P1"
                res = handle_cancel(target)
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
            if self.vs_ai and self.difficulty_btn_rect.collidepoint(vx, vy):
                self.cycle_ai_difficulty()
                return False
            for idx, rect in enumerate(self.card_rects):
                if rect.collidepoint(vx, vy):
                    if self.vs_ai:
                        if self.selection_step == "P1":
                            self.p1_choice_idx = idx
                        else:
                            self.p2_choice_idx = idx
                    else:
                        if self.p1_ready and not self.p2_ready:
                            self.p2_choice_idx = idx
                        else:
                            self.p1_choice_idx = idx
            if self.start_btn_rect.collidepoint(vx, vy):
                if self.vs_ai:
                    res = handle_confirm("P1")
                else:
                    if not self.p1_ready:
                        res = handle_confirm("P1")
                    elif not self.p2_ready:
                        res = handle_confirm("P2")
                    else:
                        return True
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
                if self.vs_ai and self.difficulty_btn_rect.collidepoint(mx, my):
                    self.cycle_ai_difficulty()
                    return False
                for idx, rect in enumerate(self.card_rects):
                    if rect.collidepoint(mx, my):
                        if self.vs_ai:
                            if self.selection_step == "P1":
                                self.p1_choice_idx = idx
                            else:
                                self.p2_choice_idx = idx
                        else:
                            if self.p1_ready and not self.p2_ready:
                                self.p2_choice_idx = idx
                            else:
                                self.p1_choice_idx = idx
                if self.start_btn_rect.collidepoint(mx, my):
                    if self.vs_ai:
                        res = handle_confirm("P1")
                    else:
                        if not self.p1_ready:
                            res = handle_confirm("P1")
                        elif not self.p2_ready:
                            res = handle_confirm("P2")
                        else:
                            return True
                    if res:
                        return res
                    return False
            elif event.button == 3:
                for idx, rect in enumerate(self.card_rects):
                    if rect.collidepoint(mx, my):
                        self.p2_choice_idx = idx

        return False

    def update(self, dt: float) -> bool:
        """Anima a tela; devolve True quando o sorteio do Aleatório termina e a partida pode começar."""
        self.anim_timer += dt
        self.help_modal.update(dt)
        self.petals.update(dt)
        for p in self.particles:
            p["x"] += p["speed_x"] + 0.3 * math.sin(self.anim_timer + p["y"] * 0.05)
            p["y"] += p["speed_y"]
            if p["y"] < -10:
                p["y"] = SCREEN_HEIGHT + 10
                p["x"] = random.uniform(0, SCREEN_WIDTH)
        if self.reveal is not None:
            return self._update_reveal(dt)
        return False

    def get_selected_characters(self) -> tuple[str, str, bool]:
        playable_ids = [c["id"] for c in self.characters if c.get("ready", True) and c["id"] != CHAR_RANDOM]
        def pick(idx: int) -> str:
            if idx == self.random_idx:
                return random.choice(playable_ids) if playable_ids else CHAR_KENSHIN
            char_id = self.characters[idx]["id"]
            if not self.characters[idx].get("ready", True):
                return random.choice(playable_ids) if playable_ids else CHAR_KENSHIN
            return char_id
        return pick(self.p1_choice_idx), pick(self.p2_choice_idx), self.vs_ai

    def _render_locked_overlay(self, surface, rect, font, is_demo_lock: bool = False):
        """Escurece a carta bloqueada e exibe aviso de bloqueio/desenvolvimento."""
        shade = pygame.Surface(rect.size, pygame.SRCALPHA)
        shade.fill((10, 10, 14, 175 if is_demo_lock else 150))
        surface.blit(shade, rect.topleft)
        text = t("demo_locked_card") if is_demo_lock else t("char_locked_badge")
        label = font.render(text, True, (225, 205, 160))
        surface.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    def _render_random_card(self, surface, rect, idx, char_info, parch, font_name, font_small, font_tiny, font_stamp):
        """Faixa do sorteio: círculo com interrogação, nome e dica; durante a roleta pulsa em dourado."""
        is_p1 = (self.p1_choice_idx == idx)
        is_p2 = (self.p2_choice_idx == idx)
        spinning = self.reveal is not None
        if parch:
            pm.draw_paper_card(surface, rect, seed=97)
            if is_p1 or is_p2 or spinning:
                pulse = 0.5 + 0.5 * math.sin(self.anim_timer * 6.0)
                border = pm.make_ink_border(rect, COLOR_HANKO_RED if is_p1 else COLOR_HANKO_BLUE, width=2, seed=99)
                border.set_alpha(int(150 + 105 * pulse))
                surface.blit(border, rect.topleft)
        else:
            draw_sumie_card(surface, rect, is_p1, is_p2, self.vs_ai, self.selection_step, self.anim_timer)

        cx, cy = rect.x + 24, rect.centery
        ring = COLOR_HANKO_RED if is_p1 else (COLOR_HANKO_BLUE if is_p2 else char_info["color"])
        draw_enso_circle(surface, cx, cy, 14, ring, self.anim_timer)
        q_font = get_title_font(18)
        q = q_font.render("?", True, pm.darken(char_info["color"], 0.55) if parch else char_info["color"])
        surface.blit(q, q.get_rect(center=(cx, cy)))

        text_left = rect.x + 46
        name_col = pm.darken(char_info["color"], 0.55) if parch else char_info["color"]
        name_s = font_name.render(char_info["name"], True, name_col)
        surface.blit(name_s, (text_left, rect.centery - name_s.get_height() // 2))

        title_col = pm.INK_SOFT if parch else (185, 180, 175)
        title_s = pm.fit_text(font_small, char_info["title"], title_col, rect.right - text_left - name_s.get_width() - 80)
        surface.blit(title_s, (text_left + name_s.get_width() + 14, rect.centery - title_s.get_height() // 2))

        p2_label = "IA" if self.vs_ai else "P2"
        if is_p1:
            draw_hanko_stamp(surface, font_stamp, "P1", rect.right - 54, rect.y + 6, size=24, color=COLOR_HANKO_RED, border_w=1)
        if is_p2:
            draw_hanko_stamp(surface, font_stamp, p2_label, rect.right - 28, rect.y + 6, size=24, color=COLOR_HANKO_BLUE, border_w=1)

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        # 1. Carregar tipografia oriental autêntica
        font_oriental_title = get_title_font(28)
        font_oriental_name = get_title_font(17)
        font_oriental_action = get_title_font(19)
        font_zen_mid = get_text_font(18)
        font_zen_small = get_text_font(14)
        font_zen_tiny = get_text_font(12)
        font_zen_stamp = get_text_font(13)

        # 2. Fundo: pergaminho sumi-e (arte de referência); fallback para o fundo escuro anterior
        parch = pm.get_backdrop() is not None
        if parch:
            pm.draw_backdrop(surface)
        else:
            if self.bg_surf:
                surface.blit(self.bg_surf, (0, 0))
            else:
                surface.fill(COLOR_BG)
            surface.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MAX)

            for p in self.particles:
                pygame.draw.circle(surface, (175, 170, 165), (int(p["x"]), int(p["y"])), int(p["size"]))

            # Desenhar moldura decorativa tipo pergaminho
            draw_scroll_frame(surface, margin_top=100, margin_bottom=90, margin_sides=20)

        # 3. TOPO: Título Sumi-E Nobre Centralizado
        header_y = 12
        title_text = t("select_title")
        if parch:
            s_title = pm.render_ink(font_oriental_title, title_text, pm.INK)
            surface.blit(s_title, (SCREEN_WIDTH // 2 - s_title.get_width() // 2, header_y + 5))
        else:
            s_shadow = font_oriental_title.render(title_text, True, (8, 8, 10))
            s_title = font_oriental_title.render(title_text, True, COLOR_GOLD)
            title_x = SCREEN_WIDTH // 2 - s_title.get_width() // 2
            surface.blit(s_shadow, (title_x + 1, header_y + 7))
            surface.blit(s_title, (title_x, header_y + 6))

        # Botão Seletor Flutuante de Idioma [ PT | EN ] (Hanko / Kanban)
        lang = get_lang()
        self.lang_btn_rect = pygame.Rect(SCREEN_WIDTH - 170, header_y + 4, 96, 32)
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

        # Botão de Ajuda redondo "?" (atalho H / ?)
        self.help_btn_rect = pygame.Rect(SCREEN_WIDTH - 64, header_y + 2, 36, 36)
        draw_round_help_button(surface, font_zen_mid, self.help_btn_rect, self.anim_timer)

        # 4. Botão Modo de Jogo & Dificuldade da IA (Kanban laqueado com encaixes de ferro)
        is_mode_focused = (self.focus_zone == "MODE_BTN")
        if self.arcade_mode:
            self.mode_btn_rect = pygame.Rect(0, 0, 0, 0)
            self.difficulty_btn_rect = pygame.Rect(0, 0, 0, 0)
            arcade_rect = pygame.Rect(SCREEN_WIDTH // 2 - 190, 52, 380, 32)
            draw_kanban_menu_button(surface, font_zen_small, t("arcade_title"), "", arcade_rect, False, True, self.anim_timer)
        elif self.vs_ai:
            self.mode_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 290, 52, 350, 32)
            self.difficulty_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 + 70, 52, 180, 32)
            mode_text = "MODO: 1P vs IA (TREINO)" if lang == LANG_PT else "MODE: 1P vs AI (TRAIN)"
            mode_hint = "[ CIMA/BAIXO ]" if lang == LANG_PT else "[ UP/DOWN ]"
            draw_kanban_menu_button(surface, font_zen_small, mode_text, mode_hint, self.mode_btn_rect, is_mode_focused, True, self.anim_timer)

            diff_names = {
                "easy": "FÁCIL" if lang == LANG_PT else "EASY",
                "normal": "NORMAL",
                "hard": "DIFÍCIL" if lang == LANG_PT else "HARD"
            }
            d_name = diff_names.get(self.ai_difficulty, "NORMAL")
            draw_kanban_menu_button(surface, font_zen_small, f"IA: {d_name}", "[ G ]", self.difficulty_btn_rect, False, True, self.anim_timer)
        else:
            self.mode_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 190, 52, 380, 32)
            self.difficulty_btn_rect = pygame.Rect(0, 0, 0, 0)
            mode_text = "MODO: 1P vs 2P (VERSUS)" if lang == LANG_PT else "MODE: 1P vs 2P (VERSUS)"
            mode_hint = "[ CIMA/BAIXO ]" if lang == LANG_PT else "[ UP/DOWN ]"
            draw_kanban_menu_button(surface, font_zen_small, mode_text, mode_hint, self.mode_btn_rect, is_mode_focused, True, self.anim_timer)

        # 5. Banner Indicador de Etapa / Instrução
        step_y = 80
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

        if self.reveal is not None:
            step_title = "SORTEANDO..." if lang == LANG_PT else "DRAWING..."
            step_color = COLOR_GOLD
        step_s = pm.render_ink(font_zen_mid, step_title, pm.darken(step_color, 0.8)) if parch else font_zen_mid.render(step_title, True, step_color)
        step_x = SCREEN_WIDTH // 2 - step_s.get_width() // 2
        surface.blit(step_s, (step_x, step_y))

        # Divisórias de pincel nas laterais do texto (sem riscar as letras)
        draw_brush_divider(surface, step_x - 140, step_y + 11, step_x - 16, color=div_color)
        draw_brush_divider(surface, step_x + step_s.get_width() + 16, step_y + 11, step_x + step_s.get_width() + 140, color=div_color)

        # 6. Grade 6x4 (24 combatentes: Linhas 0-1 veteranos, Linhas 2-3 novos) + Linha 4 (Aleatório)
        card_w = 190
        card_h = 102
        spacing_x = 10
        spacing_y = 6

        total_w = 6 * card_w + 5 * spacing_x
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = 108

        self.card_rects.clear()
        self.info_btn_rects.clear()

        for idx, char_info in enumerate(self.characters):
            if char_info["id"] == CHAR_RANDOM:
                # Carta Aleatório: faixa na quinta linha
                rand_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, start_y + 4 * (card_h + spacing_y), 500, 36)
                self.card_rects.append(rand_rect)
                self.info_btn_rects.append(pygame.Rect(0, 0, 0, 0))
                self._render_random_card(surface, rand_rect, idx, char_info, parch, font_oriental_name, font_zen_small, font_zen_tiny, font_zen_stamp)
                if self.is_locked(idx):
                    self._render_locked_overlay(surface, rand_rect, font_zen_small, is_demo_lock=is_demo() and char_info["id"] not in DEMO_FIGHTERS)
                continue

            row = idx // 6
            col = idx % 6
            cx = start_x + col * (card_w + spacing_x)
            cy = start_y + row * (card_h + spacing_y)

            rect = pygame.Rect(cx, cy, card_w, card_h)
            self.card_rects.append(rect)

            is_p1 = (self.p1_choice_idx == idx)
            is_p2 = (self.p2_choice_idx == idx)
            is_ready = char_info.get("ready", True)
            is_locked_card = self.is_locked(idx)
            is_demo_lock = is_demo() and char_info["id"] not in DEMO_FIGHTERS

            if parch:
                pm.draw_paper_card(surface, rect, seed=idx * 7 + 3)
                if is_p1 or is_p2:
                    sel_col = COLOR_HANKO_RED if is_p1 else COLOR_HANKO_BLUE
                    pm.draw_brush_highlight(surface, pygame.Rect(rect.x + 58, rect.y + 4, card_w - 74, 24),
                                            pm.SEAL_RED if is_p1 else pm.SEAL_BLUE, seed=idx + 2)
                    pulse = 0.5 + 0.5 * math.sin(self.anim_timer * 6.0)
                    border = pm.make_ink_border(rect, sel_col, width=2, seed=idx + 5)
                    border.set_alpha(int(150 + 105 * pulse))
                    surface.blit(border, rect.topleft)
            else:
                draw_sumie_card(surface, rect, is_p1, is_p2, self.vs_ai, self.selection_step, self.anim_timer)

            # Badges Hanko P1 / IA
            p2_label = "IA" if self.vs_ai else "P2"
            if parch:
                ssz = 18
                first_x, second_x, sy = rect.x - 4, rect.x + 16, rect.y - 6
            else:
                ssz = 18
                first_x, second_x, sy = rect.right - 44, rect.right - 22, rect.y + 4
            if is_p1 and is_p2:
                draw_hanko_stamp(surface, font_zen_stamp, "P1", first_x, sy, size=ssz, color=COLOR_HANKO_RED, border_w=1)
                draw_hanko_stamp(surface, font_zen_stamp, p2_label, second_x, sy, size=ssz, color=COLOR_HANKO_BLUE, border_w=1)
            elif is_p1:
                draw_hanko_stamp(surface, font_zen_stamp, "P1", second_x if not parch else first_x, sy, size=ssz, color=COLOR_HANKO_RED, border_w=1)
            elif is_p2:
                draw_hanko_stamp(surface, font_zen_stamp, p2_label, second_x if not parch else first_x, sy, size=ssz, color=COLOR_HANKO_BLUE, border_w=1)

            # Retrato Circular com Anel Ensō
            char_id = char_info["id"]
            portrait_cx = rect.x + 28
            portrait_cy = rect.y + 28
            ring_color = COLOR_HANKO_RED if is_p1 else (COLOR_HANKO_BLUE if is_p2 else char_info["color"])

            portrait_surf = get_portrait(char_id, size=(42, 42), circular=True) if is_ready else None
            if not is_ready:
                # Sombra indefinida com símbolo de interrogação para personagens em desenvolvimento
                draw_mystery_silhouette(surface, portrait_cx, portrait_cy, radius=20)
                draw_enso_circle(surface, portrait_cx, portrait_cy, 20, (75, 70, 68), self.anim_timer)
                q_font = get_title_font(18)
                q_surf = q_font.render("?", True, (190, 180, 160))
                surface.blit(q_surf, q_surf.get_rect(center=(portrait_cx, portrait_cy)))
            else:
                draw_enso_circle(surface, portrait_cx, portrait_cy, 21, ring_color, self.anim_timer)
                if portrait_surf is not None:
                    surface.blit(portrait_surf, (portrait_cx - 21, portrait_cy - 21))
                else:
                    draw_mystery_silhouette(surface, portrait_cx, portrait_cy, radius=20)

            # Nome, Título e Estilo ao lado do Retrato
            text_left = rect.x + 52
            if not is_ready:
                name_display = "???"
                name_col = (140, 135, 130) if parch else (120, 115, 110)
                name_surf = font_oriental_name.render(name_display, True, name_col)
                surface.blit(name_surf, (text_left, rect.y + 14))
            else:
                name_display = char_info["name"]
                if parch:
                    name_col = (252, 244, 226) if (is_p1 or is_p2) else pm.darken(char_info["color"], 0.55)
                else:
                    name_col = char_info["color"]
                name_surf = font_oriental_name.render(name_display, True, name_col)
                surface.blit(name_surf, (text_left, rect.y + 4))

                title_col = pm.INK_SOFT if parch else (185, 180, 175)
                title_s = pm.fit_text(font_zen_small, char_info["title"], title_col, rect.right - text_left - 6)
                surface.blit(title_s, (text_left, rect.y + 22))

            if is_ready:
                style_col = pm.INK if parch else (220, 215, 210)
                style_s = pm.fit_text(font_zen_tiny, char_info["style"], style_col, rect.right - text_left - 6)
                surface.blit(style_s, (text_left, rect.y + 38))

            # Pincelada divisória
            draw_brush_divider(surface, rect.x + 6, rect.y + 54, rect.right - 6, color=(120, 100, 78) if parch else (75, 70, 65))

            if is_ready:
                # Combatente pronto: estatísticas compactas e botão de ajuda
                stats_y = rect.y + 58
                vel_col = pm.GOLD_INK if parch else COLOR_GOLD
                dmg_col = (150, 40, 30) if parch else (240, 205, 195)
                esp_col = (30, 70, 125) if parch else (200, 220, 240)

                line_stats = pm.fit_text(font_zen_tiny, f"{t('char_stat_speed')}: {char_info['speed_stars']} | {char_info['damage_desc']}", vel_col, card_w - 12)
                line_esp = pm.fit_text(font_zen_tiny, f"{char_info['special_desc']}", esp_col, card_w - 32)
                surface.blit(line_stats, (rect.x + 6, stats_y))
                surface.blit(line_esp, (rect.x + 6, stats_y + 16))

                # Botão [ ? ] como Selo Hanko pequeno
                info_btn = pygame.Rect(rect.right - 22, stats_y + 12, 18, 22)
                self.info_btn_rects.append(info_btn)
                draw_hanko_stamp(surface, font_zen_small, "?", info_btn.x, info_btn.y, size=18,
                                 color=COLOR_HANKO_RED if parch else COLOR_GOLD, border_w=1)
                if is_locked_card:
                    self._render_locked_overlay(surface, rect, font_zen_small, is_demo_lock=is_demo_lock)
            else:
                self.info_btn_rects.append(pygame.Rect(0, 0, 0, 0))
                # Combatente bloqueado / em desenvolvimento: selo refinado "EM BREVE"
                badge_text = t("demo_locked_card") if is_demo_lock else t("char_locked_badge")
                badge_col = (165, 135, 80) if parch else (210, 190, 130)
                badge_s = font_zen_small.render(badge_text, True, badge_col)
                badge_rect = pygame.Rect(rect.centerx - badge_s.get_width() // 2 - 10, rect.y + 64, badge_s.get_width() + 20, 24)
                badge_bg = pygame.Surface((badge_rect.width, badge_rect.height), pygame.SRCALPHA)
                badge_bg.fill((30, 24, 18, 120) if parch else (15, 14, 18, 180))
                surface.blit(badge_bg, badge_rect.topleft)
                pygame.draw.rect(surface, (140, 115, 75) if parch else (90, 85, 78), badge_rect, 1, border_radius=4)
                surface.blit(badge_s, (badge_rect.centerx - badge_s.get_width() // 2, badge_rect.centery - badge_s.get_height() // 2))

        # 7. Botão Grande de Ação: pergaminho com vara + pincelada vermelha (ou laca escarlate no fallback)
        start_w = 420
        if parch:
            pm.draw_scroll(surface, pygame.Rect(SCREEN_WIDTH // 2 - 470, 604, 940, 116), seed=21)
            pm.draw_crest(surface, SCREEN_WIDTH - 126, 622, 0.8)
            self.start_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - start_w // 2, 629, start_w, 34)
            pm.draw_brush_highlight(surface, pygame.Rect(self.start_btn_rect.centerx - 260, self.start_btn_rect.y - 6, 520, 46), pm.SEAL_RED, seed=9)
        else:
            self.start_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - start_w // 2, SCREEN_HEIGHT - 64, start_w, 44)
            pulse = 0.5 + 0.5 * math.sin(self.anim_timer * 4.0)
            btn_bg = (140 + int(pulse * 25), 28 + int(pulse * 10), 24)
            pygame.draw.rect(surface, btn_bg, self.start_btn_rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD, self.start_btn_rect, 2, border_radius=6)

        from src.input.controller_manager import get_controller_manager
        ctrl_mgr = get_controller_manager()
        has_c1 = ctrl_mgr.has_controller(0) if ctrl_mgr else False
        has_c2 = ctrl_mgr.has_controller(1) if ctrl_mgr else False

        c1 = ctrl_mgr.get_controller_for_player(0) if ctrl_mgr else None
        c2 = ctrl_mgr.get_controller_for_player(1) if ctrl_mgr else None
        ok1 = c1.get_button_text("confirm").upper() if c1 else ""
        ok2 = c2.get_button_text("confirm").upper() if c2 else ""
        enter_space = "ENTER / ESPAÇO" if lang == LANG_PT else "ENTER / SPACE"
        space_only = "ESPAÇO" if lang == LANG_PT else "SPACE"

        if self.vs_ai:
            if self.selection_step == "P1":
                st_label = "CONFIRMAR P1" if lang == LANG_PT else "CONFIRM P1"
                hint_label = f"[ {ok1} / {space_only} ]" if has_c1 else f"[ {enter_space} ]"
            else:
                st_label = "INICIAR DUELO" if lang == LANG_PT else "START DUEL"
                hint_label = f"[ {ok1} / {space_only} ]" if has_c1 else f"[ {enter_space} ]"
        else:
            if not self.p1_ready:
                st_label = "CONFIRMAR P1" if lang == LANG_PT else "CONFIRM P1"
                hint_label = f"[ {ok1} / {space_only} / [E] ]" if has_c1 else f"[ {space_only} / [E] ]"
            elif not self.p2_ready:
                st_label = "CONFIRMAR P2" if lang == LANG_PT else "CONFIRM P2"
                hint_label = f"[ {ok2} / ENTER / [U] ]" if has_c2 else "[ ENTER / [U] ]"
            else:
                st_label = "INICIAR DUELO" if lang == LANG_PT else "START DUEL"
                hint_label = f"[ {enter_space} ]"

        s_title_sh = font_oriental_action.render(st_label, True, (20, 10, 10))
        s_title_tx = font_oriental_action.render(st_label, True, (252, 244, 226) if parch else COLOR_GOLD)
        s_hint_tx = font_zen_small.render(hint_label, True, (250, 232, 200) if parch else (245, 225, 185))

        total_content_w = s_title_tx.get_width() + 14 + s_hint_tx.get_width()
        content_x = self.start_btn_rect.centerx - total_content_w // 2

        surface.blit(s_title_sh, (content_x + 1, self.start_btn_rect.centery - s_title_tx.get_height() // 2 + 1))
        surface.blit(s_title_tx, (content_x, self.start_btn_rect.centery - s_title_tx.get_height() // 2))

        hint_x = content_x + s_title_tx.get_width() + 14
        surface.blit(s_hint_tx, (hint_x, self.start_btn_rect.centery - s_hint_tx.get_height() // 2))

        # 8. Pétalas decorativas (sem barra de instruções de teclado no rodapé)
        if parch:
            self.petals.draw(surface)

        # 9. Modal de Ajuda se aberto (sobreposto)
        if self.help_modal.is_open:
            self.help_modal.render(surface, font_large, font_mid, font_small)
