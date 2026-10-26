"""
Fase 5 - Entregável 5.2: Apresentação Cinematográfica de Round (Sumi-E).

Antes de cada round (exceto a introdução da batalha), a arena gira levemente
(azimute real da câmera, Entregável 6.1) e para na vista clássica enquanto um
pergaminho vertical (pintura Sumi-E) se desenrola no centro da tela,
revelando os nomes dos dois duelistas.

Esta classe é propositalmente "sem estado próprio de tempo": toda a animação
é derivada do cronômetro `round_intro_timer` já mantido pelo laço principal
do jogo, o que permite reutilizar `get_rotation_angle`/`render` como funções
puras a cada quadro sem duplicar contabilidade de tempo.
"""
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui.fonts import get_title_font, get_text_font
from src.effects import parchment as pm

INTRO_DURATION = 2.0   # Duração total da cinemática de abertura, em segundos
ROTATION_DEGREES = 24.0  # Giro inicial do azimute da câmera, que termina em 0° (vista clássica)


def _ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def _parse_name_and_badge(raw_name: str) -> tuple[str, str]:
    """Separa o nome base do lutador e sua etiqueta secundária (ex: '(ESPELHO)', '(MIRROR)', '(IA 2)')."""
    import re
    m = re.search(r"\(([^)]+)\)", raw_name)
    if m:
        badge = m.group(1).strip()
        base_name = raw_name[:m.start()].strip()
        return base_name, f"[ {badge} ]"
    return raw_name.strip(), ""


def _render_fitted_text(text: str, color, max_w: int, base_size: int = 24, min_size: int = 14) -> pygame.Surface:
    """Renderiza texto com escala tipográfica adaptativa para garantir que caiba no pergaminho."""
    for sz in range(base_size, min_size - 1, -2):
        font = get_title_font(sz)
        surf = font.render(text, True, color)
        if surf.get_width() <= max_w:
            return surf
    # Se ainda exceder, faz escala suave proporcional
    surf = get_title_font(min_size).render(text, True, color)
    if surf.get_width() > max_w:
        scale = max_w / surf.get_width()
        return pygame.transform.smoothscale(surf, (max_w, max(1, int(surf.get_height() * scale))))
    return surf


class RoundIntroScreen:
    """Controla a cinemática de abertura de cada round: rotação suave da
    câmera e pergaminho vertical Sumi-E revelando os nomes dos lutadores."""

    def __init__(self):
        self.p1_name = ""
        self.p2_name = ""
        self.p1_color = (255, 255, 255)
        self.p2_color = (255, 255, 255)
        self.round_label = ""
        if pm.get_backdrop() is not None:
            pm.make_paper(190, int(SCREEN_HEIGHT * 0.78), seed=33, ragged=(False, False, True, True))

    def start(self, p1_name: str, p2_name: str, p1_color=(255, 255, 255), p2_color=(255, 255, 255), round_label: str = ""):
        """Prepara os dados exibidos pela cinemática para o round que está começando."""
        self.p1_name = p1_name.upper()
        self.p2_name = p2_name.upper()
        self.p1_color = p1_color
        self.p2_color = p2_color
        self.round_label = round_label

    def is_active(self, round_intro_timer: float) -> bool:
        """A cinemática está em andamento enquanto o cronômetro dedicado for positivo."""
        return round_intro_timer > 0.0

    def _progress(self, round_intro_timer: float, duration: float = INTRO_DURATION) -> float:
        elapsed = duration - max(0.0, round_intro_timer)
        return max(0.0, min(1.0, elapsed / duration))

    def get_rotation_angle(self, round_intro_timer: float, duration: float = INTRO_DURATION) -> float:
        """Azimute (graus) da câmera: começa em ROTATION_DEGREES e se estabiliza em 0°."""
        if not self.is_active(round_intro_timer):
            return 0.0
        progress = min(1.0, self._progress(round_intro_timer, duration) / 0.7)
        return ROTATION_DEGREES * (1.0 - _ease_out_cubic(progress))

    def render(self, surface: pygame.Surface, round_intro_timer: float, duration: float = INTRO_DURATION):
        """Desenha o pergaminho vertical Sumi-E com os nomes dos dois duelistas."""
        if not self.is_active(round_intro_timer):
            return

        reveal = min(1.0, self._progress(round_intro_timer, duration) / 0.5)
        reveal = _ease_out_cubic(reveal)

        parch = pm.get_backdrop() is not None
        scroll_w = 190 if parch else 150
        scroll_h = int(SCREEN_HEIGHT * 0.78 * reveal)
        scroll_x = SCREEN_WIDTH // 2 - scroll_w // 2
        scroll_y = SCREEN_HEIGHT // 2 - scroll_h // 2

        if scroll_h <= 2:
            return

        if parch:
            # Papel envelhecido gerado uma vez; o desenrolar revela uma faixa central, com as varas reais nas pontas
            full_h = int(SCREEN_HEIGHT * 0.78)
            paper = pm.make_paper(scroll_w, full_h, seed=33, ragged=(False, False, True, True))
            sheet = paper.subsurface(pygame.Rect(0, (full_h - scroll_h) // 2, scroll_w, scroll_h))
            surface.blit(pm._soft_shadow(paper).subsurface(pygame.Rect(0, (full_h - scroll_h) // 2, scroll_w, scroll_h)),
                         (scroll_x + 4, scroll_y + 5))
            surface.blit(sheet, (scroll_x, scroll_y))
            rh = pm.rod_height()
            pm.draw_rod(surface, "top", SCREEN_WIDTH // 2, scroll_y - rh // 2, scroll_w + 40)
            pm.draw_rod(surface, "bottom", SCREEN_WIDTH // 2, scroll_y + scroll_h - rh // 2, scroll_w + 40)
        else:
            scroll_surf = pygame.Surface((scroll_w, scroll_h), pygame.SRCALPHA)
            pygame.draw.rect(scroll_surf, (235, 225, 200, 235), (0, 0, scroll_w, scroll_h), border_radius=10)
            pygame.draw.rect(scroll_surf, (90, 60, 30, 255), (0, 0, scroll_w, scroll_h), width=4, border_radius=10)
            pygame.draw.rect(scroll_surf, (40, 25, 15, 255), (0, 0, scroll_w, 14), border_radius=6)
            pygame.draw.rect(scroll_surf, (40, 25, 15, 255), (0, scroll_h - 14, scroll_w, 14), border_radius=6)
            surface.blit(scroll_surf, (scroll_x, scroll_y))

        if reveal > 0.55:
            text_alpha = int(255 * min(1.0, (reveal - 0.55) / 0.45))
            font_vs = get_text_font(20)
            font_badge = get_text_font(13)
            max_name_w = scroll_w - 24

            p1_base, p1_badge = _parse_name_and_badge(self.p1_name)
            p1_col = pm.darken(self.p1_color, 0.6) if parch else self.p1_color
            p1_surf = _render_fitted_text(p1_base, p1_col, max_name_w, base_size=24, min_size=14)

            p2_base, p2_badge = _parse_name_and_badge(self.p2_name)
            p2_col = pm.darken(self.p2_color, 0.6) if parch else self.p2_color
            p2_surf = _render_fitted_text(p2_base, p2_col, max_name_w, base_size=24, min_size=14)

            badge_col = pm.SEAL_RED if parch else (190, 50, 40)
            b1_surf = font_badge.render(p1_badge, True, badge_col) if p1_badge else None
            b2_surf = font_badge.render(p2_badge, True, badge_col) if p2_badge else None

            vs_surf = font_vs.render("対", True, pm.SEAL_RED if parch else (60, 40, 20))

            if text_alpha < 255:
                for s in (p1_surf, p2_surf, vs_surf, b1_surf, b2_surf):
                    if s is not None:
                        s.fill((255, 255, 255, text_alpha), special_flags=pygame.BLEND_RGBA_MULT)

            cy = scroll_y + scroll_h // 2
            mid_x = scroll_x + scroll_w // 2

            p1_y = cy - 90
            surface.blit(p1_surf, (mid_x - p1_surf.get_width() // 2, p1_y))
            if b1_surf is not None:
                surface.blit(b1_surf, (mid_x - b1_surf.get_width() // 2, p1_y + p1_surf.get_height() + 2))

            surface.blit(vs_surf, (mid_x - vs_surf.get_width() // 2, cy - 14))

            p2_y = cy + 40
            surface.blit(p2_surf, (mid_x - p2_surf.get_width() // 2, p2_y))
            if b2_surf is not None:
                surface.blit(b2_surf, (mid_x - b2_surf.get_width() // 2, p2_y + p2_surf.get_height() + 2))

            if self.round_label:
                font_round = get_text_font(16)
                r_surf = font_round.render(self.round_label, True, pm.SEAL_RED if parch else (70, 45, 20))
                if text_alpha < 255:
                    r_surf.fill((255, 255, 255, text_alpha), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(r_surf, (mid_x - r_surf.get_width() // 2, scroll_y + 46 if parch else scroll_y - 26))
