"""
Renderizador e Gerenciador de Ícones SVG de Botões de Controle (PlayStation, etc.)
Carrega e rasteriza os arquivos SVG de assets/icons/playstation/ com cache dinâmico.
Inclui fallback vetorial paramétrico ultra-nítido em caso de ausência de backend libsvg no SDL_image.
"""
import os
import math
import pygame
import pygame.gfxdraw

# Cores Oficiais PlayStation
COLOR_PS_CROSS = (0, 132, 255)       # Azul Cobalto Vibrante
COLOR_PS_CIRCLE = (255, 59, 48)      # Vermelho Carmim
COLOR_PS_SQUARE = (233, 84, 165)     # Magenta / Rosa Choque
COLOR_PS_TRIANGLE = (0, 224, 100)    # Verde Esmeralda
COLOR_PS_BG = (28, 34, 40)           # Base grafite escuro
COLOR_PS_BORDER = (80, 92, 105)      # Borda chanfrada
COLOR_PS_TEXT = (230, 235, 242)

# Diretório base dos SVGs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SVG_DIR = os.path.join(BASE_DIR, "assets", "icons", "playstation")

# Cache em memória: (icon_name, width, height) -> pygame.Surface
_ICON_CACHE: dict[tuple[str, int, int], pygame.Surface] = {}

ICON_FILENAME_MAP = {
    "cross": "ps_cross.svg",
    "circle": "ps_circle.svg",
    "square": "ps_square.svg",
    "triangle": "ps_triangle.svg",
    "l1": "ps_l1.svg",
    "r1": "ps_r1.svg",
    "dpad": "ps_dpad.svg",
    "options": "ps_options.svg",
}

def _draw_vector_fallback(icon_name: str, width: int, height: int) -> pygame.Surface:
    """Gera o ícone vetorial paramétrico idêntico ao SVG com anti-aliasing."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    cx, cy = width // 2, height // 2
    radius = min(width, height) // 2 - 2

    if icon_name in ("cross", "circle", "square", "triangle"):
        # Base Circular do Botão
        pygame.gfxdraw.filled_circle(surf, cx, cy, radius, COLOR_PS_BG)
        pygame.gfxdraw.aacircle(surf, cx, cy, radius, COLOR_PS_BORDER)

        inner_r = max(2, int(radius * 0.58))
        lw = max(2, int(radius * 0.22))

        if icon_name == "cross":
            # ✕ Cruz Azul
            d = int(inner_r * 0.72)
            pygame.draw.line(surf, COLOR_PS_CROSS, (cx - d, cy - d), (cx + d, cy + d), lw)
            pygame.draw.line(surf, COLOR_PS_CROSS, (cx + d, cy - d), (cx - d, cy + d), lw)

        elif icon_name == "circle":
            # ○ Círculo Vermelho
            pygame.gfxdraw.aacircle(surf, cx, cy, inner_r, COLOR_PS_CIRCLE)
            pygame.gfxdraw.aacircle(surf, cx, cy, inner_r - 1, COLOR_PS_CIRCLE)
            if inner_r > 3:
                pygame.gfxdraw.aacircle(surf, cx, cy, inner_r - 2, COLOR_PS_CIRCLE)

        elif icon_name == "square":
            # ▢ Quadrado Magenta
            s = int(inner_r * 0.85)
            r = pygame.Rect(cx - s, cy - s, s * 2, s * 2)
            pygame.draw.rect(surf, COLOR_PS_SQUARE, r, max(1, lw - 1), border_radius=max(1, s // 4))

        elif icon_name == "triangle":
            # △ Triângulo Verde
            h_tri = inner_r
            pts = [
                (cx, cy - h_tri),
                (cx + int(inner_r * 0.86), cy + int(h_tri * 0.58)),
                (cx - int(inner_r * 0.86), cy + int(h_tri * 0.58)),
            ]
            pygame.draw.polygon(surf, COLOR_PS_TRIANGLE, pts, max(1, lw - 1))

    elif icon_name in ("l1", "r1"):
        # Botões de Ombro Retangulares Arredondados
        rect = pygame.Rect(1, 1, width - 2, height - 2)
        pygame.draw.rect(surf, (40, 48, 56), rect, border_radius=5)
        pygame.draw.rect(surf, (90, 105, 120), rect, 1, border_radius=5)
        font = pygame.font.Font(None, max(12, int(height * 0.85)))
        txt = font.render(icon_name.upper(), True, COLOR_PS_TEXT)
        surf.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))

    elif icon_name == "dpad":
        # Cruz do D-Pad
        pw = max(3, width // 3)
        ph = max(3, height // 3)
        cross_h = pygame.Rect(2, cy - ph // 2, width - 4, ph)
        cross_v = pygame.Rect(cx - pw // 2, 2, pw, height - 4)
        pygame.draw.rect(surf, (45, 52, 60), cross_h, border_radius=2)
        pygame.draw.rect(surf, (45, 52, 60), cross_v, border_radius=2)
        pygame.draw.rect(surf, (80, 95, 110), cross_h, 1, border_radius=2)
        pygame.draw.rect(surf, (80, 95, 110), cross_v, 1, border_radius=2)

    elif icon_name in ("xbox_x", "xbox_a", "xbox_b", "xbox_y", "nintendo_y", "nintendo_b", "x", "a", "b", "y"):
        # Botões estilo Xbox e Nintendo
        pygame.gfxdraw.filled_circle(surf, cx, cy, radius, COLOR_PS_BG)
        colors = {
            "xbox_x": (0, 127, 255),    # Azul
            "x": (0, 127, 255),
            "xbox_a": (16, 185, 129),   # Verde
            "a": (16, 185, 129),
            "xbox_b": (239, 68, 68),    # Vermelho
            "b": (239, 68, 68),
            "xbox_y": (245, 158, 11),   # Amarelo
            "y": (245, 158, 11),
            "nintendo_y": (225, 230, 238),
            "nintendo_b": (225, 230, 238),
        }
        col = colors.get(icon_name, COLOR_PS_BORDER)
        pygame.gfxdraw.aacircle(surf, cx, cy, radius, col)
        letter = icon_name.split("_")[-1].upper()
        font = pygame.font.Font(None, max(12, int(height * 0.76)))
        txt = font.render(letter, True, col)
        surf.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))

    elif icon_name == "options":
        # Botão Options
        rect = pygame.Rect(1, 1, width - 2, height - 2)
        pygame.draw.rect(surf, (36, 42, 50), rect, border_radius=4)
        pygame.draw.rect(surf, (75, 88, 102), rect, 1, border_radius=4)
        font = pygame.font.Font(None, max(10, int(height * 0.70)))
        txt = font.render("OPT", True, COLOR_PS_TEXT)
        surf.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))

    return surf

def get_button_icon_surface(icon_name: str, width: int = 24, height: int = 24) -> pygame.Surface:
    """
    Retorna a Surface correspondente ao ícone SVG no tamanho desejado.
    Utiliza o arquivo SVG em assets/icons/playstation/ se disponível com suporte SDL_image,
    ou fallback vetorial idêntico em alta precisão.
    """
    icon_name = icon_name.lower().strip()
    cache_key = (icon_name, width, height)
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    filename = ICON_FILENAME_MAP.get(icon_name)
    svg_path = os.path.join(SVG_DIR, filename) if filename else None

    surf = None
    if svg_path and os.path.exists(svg_path):
        try:
            raw_img = pygame.image.load(svg_path)
            if raw_img.get_width() != width or raw_img.get_height() != height:
                surf = pygame.transform.smoothscale(raw_img, (width, height))
            else:
                surf = raw_img
        except Exception:
            surf = None

    if surf is None:
        surf = _draw_vector_fallback(icon_name, width, height)

    _ICON_CACHE[cache_key] = surf
    return surf

def render_button_icon(surface: pygame.Surface, icon_name: str, x: int, y: int, size: int = 24):
    """Desenha o ícone na superfície de destino nas coordenadas x, y (canto superior esquerdo)."""
    icon_surf = get_button_icon_surface(icon_name, size, size)
    surface.blit(icon_surf, (x, y))

def get_playstation_icon_name_for_button(button_index: int) -> str | None:
    """Mapeia o índice do botão físico do joystick PlayStation para o nome do ícone SVG."""
    mapping = {
        0: "cross",       # ✕ Cruz (Cross)
        1: "circle",      # ○ Círculo (Circle)
        2: "square",      # ▢ Quadrado (Square)
        3: "triangle",    # △ Triângulo (Triangle)
        9: "l1",          # L1
        10: "r1",         # R1
        6: "options",     # Options
        11: "dpad",       # D-Pad Cima
        12: "dpad",       # D-Pad Baixo
        13: "dpad",       # D-Pad Esquerda
        14: "dpad",       # D-Pad Direita
    }
    return mapping.get(button_index)

def resolve_icon_name(token: str) -> str:
    """
    Resolve identificadores genéricos como 'attack', 'confirm', 'dash', 'square', 'cancel'
    para o nome do ícone correspondente ao controle ativo ou PlayStation por padrão.
    """
    tok = token.lower().strip()
    dev = None
    try:
        from src.input import get_controller_manager
        mgr = get_controller_manager()
        dev = mgr.get_controller_for_player(0)
    except Exception:
        pass

    if tok in ("attack", "atk", "square"):
        if dev:
            if dev.is_xbox:
                return "xbox_x"
            elif dev.is_nintendo:
                return "nintendo_y"
        return "square"
    elif tok in ("confirm", "ok", "cross"):
        if dev:
            if dev.is_xbox:
                return "xbox_a"
            elif dev.is_nintendo:
                return "nintendo_b"
        return "cross"
    elif tok in ("cancel", "back", "circle", "dash", "roll"):
        if dev:
            if dev.is_xbox:
                return "xbox_b"
            elif dev.is_nintendo:
                return "nintendo_a"
        return "circle"
    return tok

import re
_ICON_TAG_RE = re.compile(r'\{icon:([^}]+)\}')

def render_text_with_icons(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    center_x: int,
    center_y: int,
    text_color: tuple[int, int, int] = (255, 255, 255),
    icon_size: int = 20,
    alpha: int = 255,
    shadow: bool = True,
    shadow_color: tuple[int, int, int] = (10, 10, 10),
    shadow_offset: tuple[int, int] = (1, 1),
) -> pygame.Rect:
    """
    Renderiza um texto contendo tokens como '{icon:attack}', '{icon:square}', '{icon:cross}',
    substituindo-os perfeitamente por ícones vetoriais com alinhamento visual, suporte a
    sombra e transparência alpha. Centralizado em (center_x, center_y).
    """
    if not text:
        return pygame.Rect(center_x, center_y, 0, 0)

    parts = _ICON_TAG_RE.split(text)
    font_h = font.get_height()
    line_h = max(font_h, icon_size)

    items = []
    total_w = 0

    for i, piece in enumerate(parts):
        if not piece:
            continue
        if i % 2 == 1:
            icon_name = resolve_icon_name(piece)
            icon_surf = get_button_icon_surface(icon_name, icon_size, icon_size)
            item_w = icon_size + 4
            items.append(("icon", icon_surf, item_w))
            total_w += item_w
        else:
            t_w, _ = font.size(piece)
            items.append(("text", piece, t_w))
            total_w += t_w

    if total_w == 0:
        return pygame.Rect(center_x, center_y, 0, 0)

    pad = 4
    comp_surf = pygame.Surface((total_w + pad * 2, line_h + pad * 2), pygame.SRCALPHA)

    if shadow:
        cur_x = pad + shadow_offset[0]
        cur_y_base = pad + shadow_offset[1]
        for itype, obj, iw in items:
            if itype == "text":
                sh_surf = font.render(obj, True, shadow_color)
                ty = cur_y_base + (line_h - font_h) // 2
                comp_surf.blit(sh_surf, (cur_x, ty))
            elif itype == "icon":
                sh_rect = pygame.Rect(cur_x + 2, cur_y_base + (line_h - icon_size) // 2, icon_size, icon_size)
                pygame.draw.circle(comp_surf, (shadow_color[0], shadow_color[1], shadow_color[2], 180), sh_rect.center, icon_size // 2)
            cur_x += iw

    cur_x = pad
    cur_y_base = pad
    for itype, obj, iw in items:
        if itype == "text":
            t_surf = font.render(obj, True, text_color)
            ty = cur_y_base + (line_h - font_h) // 2
            comp_surf.blit(t_surf, (cur_x, ty))
        elif itype == "icon":
            iy = cur_y_base + (line_h - icon_size) // 2
            comp_surf.blit(obj, (cur_x + 2, iy))
        cur_x += iw

    if alpha < 255:
        comp_surf.set_alpha(max(0, min(255, alpha)))

    dest_x = center_x - comp_surf.get_width() // 2
    dest_y = center_y - comp_surf.get_height() // 2
    surface.blit(comp_surf, (dest_x, dest_y))
    return pygame.Rect(dest_x, dest_y, comp_surf.get_width(), comp_surf.get_height())

