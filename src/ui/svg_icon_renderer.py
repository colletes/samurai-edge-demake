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
