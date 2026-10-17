"""
Combat Callouts & Samurai Cinema UI (Fase M-3.2).
Substitui faixas neon retrô por fitas de pincel Sumi-E com detalhes em folha de ouro,
selos Inkan (hanko carmesim) e marcadores de combate em laca japonesa (urushi).
"""
import math
import pygame
from src.ui.fonts import get_title_font, get_text_font

# Paleta Nobre Feudal
INK_BLACK = (16, 18, 20)
INK_CHARCOAL = (28, 30, 34)
GOLD_LEAF = (218, 175, 75)
GOLD_BRIGHT = (255, 228, 130)
GOLD_DARK = (140, 105, 38)
HANKO_RED = (185, 34, 38)
HANKO_BORDER = (220, 50, 54)
CREAM_PAPER = (245, 238, 222)


def render_sumie_ribbon(
    surface: pygame.Surface,
    text: str,
    cx: int,
    cy: int,
    color: tuple[int, int, int] = GOLD_BRIGHT,
    alpha: int = 255,
    font_size: int = 20,
    kanji_seal: str | None = None,
    scale: float = 1.0,
):
    """
    Renderiza uma fita horizontal de aguada de tinta Sumi-E com bordas em folha de ouro,
    chanfrada estilo pergaminho e tipografia nítida anti-serrilhada.
    """
    if alpha <= 0 or not text:
        return

    font = get_title_font(int(font_size * scale))
    txt_surf = font.render(text, True, color)
    txt_w, txt_h = txt_surf.get_width(), txt_surf.get_height()

    # Dimensões da fita com margem elegante
    pad_h = int(10 * scale)
    pad_w = int(28 * scale)
    ribbon_h = txt_h + pad_h * 2
    ribbon_w = txt_w + pad_w * 2 + (int(26 * scale) if kanji_seal else 0)

    half_w = ribbon_w // 2
    half_h = ribbon_h // 2
    skew = int(12 * scale)  # Chanfro dinâmico das pontas

    # Superfície de tinta com canal alpha
    ink_surf = pygame.Surface((ribbon_w + skew * 2, ribbon_h + 8), pygame.SRCALPHA)
    ox = skew
    oy = 2

    # Polígono chanfrado da fita de tinta
    poly_pts = [
        (ox - skew, oy),
        (ox + ribbon_w, oy),
        (ox + ribbon_w + skew, oy + ribbon_h),
        (ox, oy + ribbon_h),
    ]

    # Sombra difusa sob a fita
    shadow_alpha = int(alpha * 0.40)
    shadow_pts = [(x + 2, y + 4) for (x, y) in poly_pts]
    pygame.draw.polygon(ink_surf, (0, 0, 0, shadow_alpha), shadow_pts)

    # Corpo de tinta Sumi-E (camada escura profunda)
    body_alpha = int(alpha * 0.88)
    pygame.draw.polygon(ink_surf, (*INK_BLACK, body_alpha), poly_pts)

    # Textura interna de pincel (faixa central mais translúcida)
    inner_pts = [
        (ox - int(skew * 0.6), oy + 3),
        (ox + ribbon_w + int(skew * 0.3), oy + 3),
        (ox + ribbon_w + int(skew * 0.6), oy + ribbon_h - 3),
        (ox - int(skew * 0.1), oy + ribbon_h - 3),
    ]
    pygame.draw.polygon(ink_surf, (*INK_CHARCOAL, int(alpha * 0.55)), inner_pts)

    # Frisos superior e inferior em folha de ouro
    gold_alpha = int(alpha * 0.85)
    line_gold = (*GOLD_LEAF, gold_alpha)
    pygame.draw.line(ink_surf, line_gold, (ox - skew, oy), (ox + ribbon_w, oy), max(1, int(2 * scale)))
    pygame.draw.line(ink_surf, line_gold, (ox, oy + ribbon_h), (ox + ribbon_w + skew, oy + ribbon_h), max(1, int(2 * scale)))

    # Selo Inkan carmesim (carimbo tradicional japonês) à esquerda
    text_start_x = ox + pad_w
    if kanji_seal:
        seal_size = int(18 * scale)
        seal_x = ox + int(10 * scale)
        seal_y = oy + (ribbon_h - seal_size) // 2
        seal_rect = pygame.Rect(seal_x, seal_y, seal_size, seal_size)
        pygame.draw.rect(ink_surf, (*HANKO_RED, int(alpha * 0.92)), seal_rect, border_radius=max(1, int(2 * scale)))
        pygame.draw.rect(ink_surf, (*HANKO_BORDER, gold_alpha), seal_rect, width=1, border_radius=max(1, int(2 * scale)))

        kanji_font = get_title_font(max(10, int(11 * scale)))
        k_surf = kanji_font.render(kanji_seal, True, CREAM_PAPER)
        ink_surf.blit(k_surf, (seal_rect.centerx - k_surf.get_width() // 2, seal_rect.centery - k_surf.get_height() // 2))
        text_start_x += seal_size + int(6 * scale)

    # Sombra do texto
    shadow_font_surf = font.render(text, True, (0, 0, 0))
    shadow_font_surf.set_alpha(int(alpha * 0.8))
    txt_y = oy + pad_h
    ink_surf.blit(shadow_font_surf, (text_start_x + 2, txt_y + 2))

    # Texto frontal iluminado
    txt_surf.set_alpha(alpha)
    ink_surf.blit(txt_surf, (text_start_x, txt_y))

    # Blit centralizado na tela
    dest_x = cx - (ribbon_w + skew * 2) // 2
    dest_y = cy - (ribbon_h + 8) // 2
    surface.blit(ink_surf, (dest_x, dest_y))


def draw_overhead_marker(
    surface: pygame.Surface,
    sx: int,
    sy: int,
    label: str,
    color: tuple[int, int, int],
    alpha: int = 255,
):
    """
    Marcador minimalista de jogador em losango de laca (urushi) com ponta de flecha de precisão.
    Substitui caixas retangulares retrô com visual cinematográfico limpo.
    """
    if alpha <= 0:
        return

    font = get_title_font(14)
    txt = font.render(label, True, color)
    txt_w, txt_h = txt.get_width(), txt.get_height()

    box_w = txt_w + 16
    box_h = 22
    by = sy - 36
    bx = sx - box_w // 2

    # Superfície semi-transparente
    surf = pygame.Surface((box_w + 8, box_h + 16), pygame.SRCALPHA)
    ox = 4
    oy = 0

    # Losango de laca preta chanfrado
    lacquer_poly = [
        (ox + 4, oy),
        (ox + box_w - 4, oy),
        (ox + box_w, oy + box_h // 2),
        (ox + box_w - 4, oy + box_h),
        (ox + 4, oy + box_h),
        (ox, oy + box_h // 2),
    ]
    pygame.draw.polygon(surf, (12, 14, 16, int(alpha * 0.88)), lacquer_poly)
    pygame.draw.polygon(surf, (*color, int(alpha * 0.85)), lacquer_poly, width=1)

    # Texto centralizado
    txt.set_alpha(alpha)
    surf.blit(txt, (ox + (box_w - txt_w) // 2, oy + (box_h - txt_h) // 2))

    # Ponta em V / flecha minimalista apontando para a cabeça do guerreiro
    arrow_pts = [
        (ox + box_w // 2 - 5, oy + box_h + 1),
        (ox + box_w // 2 + 5, oy + box_h + 1),
        (ox + box_w // 2, oy + box_h + 7),
    ]
    pygame.draw.polygon(surf, (*color, int(alpha * 0.90)), arrow_pts)

    surface.blit(surf, (bx - 4, by))


def draw_status_gauge(
    surface: pygame.Surface,
    sx: int,
    sy: int,
    label: str,
    timer: float,
    max_timer: float,
    color: tuple[int, int, int] = GOLD_LEAF,
    warning: bool = False,
    blink: bool = False,
):
    """Medidor de cooldown/habilidade em laca escura com friso dourado e preenchimento suave."""
    bar_w = 48
    bar_h = 4
    bx = sx - bar_w // 2
    by = sy - 26

    # Moldura de laca
    pygame.draw.rect(surface, (14, 16, 18, 220), (bx - 2, by - 2, bar_w + 4, bar_h + 4), border_radius=2)

    if warning:
        fill_col = (245, 60, 60) if blink else (160, 40, 40)
        pygame.draw.rect(surface, fill_col, (bx, by, bar_w, bar_h), border_radius=1)
        font = get_text_font(12)
        txt = font.render(label, True, (255, 180, 180))
        surface.blit(txt, (sx - txt.get_width() // 2, by - 14))
    else:
        pct = max(0.0, min(1.0, 1.0 - (timer / max(0.01, max_timer))))
        fill_w = int(bar_w * pct)
        pygame.draw.rect(surface, (30, 34, 38), (bx, by, bar_w, bar_h), border_radius=1)
        if fill_w > 0:
            pygame.draw.rect(surface, color, (bx, by, fill_w, bar_h), border_radius=1)
        pygame.draw.rect(surface, GOLD_DARK, (bx - 1, by - 1, bar_w + 2, bar_h + 2), 1, border_radius=2)

        font = get_text_font(12)
        status_txt = f"{timer:.1f}s" if timer > 0.0 else "READY"
        txt = font.render(status_txt, True, (220, 230, 225) if timer > 0 else (130, 245, 165))
        surface.blit(txt, (sx - txt.get_width() // 2, by - 13))
