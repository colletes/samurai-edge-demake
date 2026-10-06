"""
Fase 5 - Entregável 5.3: Contador Best of 3 (BO3) e Tela de Resultados.

Introduz o conceito de "partida" acima do conceito já existente de "round":
o primeiro lutador a vencer 2 rounds fecha a partida (Melhor-de-3). O HUD
ganha marcadores (pips) de rounds vencidos ao lado do placar de cada
jogador, e ao final da partida uma tela dedicada exibe o vencedor com uma
opção de revanche rápida (tecla Espaço / botão de confirmação).
"""
import math
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.i18n import t
from src.ui.fonts import get_title_font, get_text_font

MATCH_WINS_NEEDED = 2  # Melhor-de-3: primeiro a vencer 2 rounds fecha a partida


def check_match_winner(score_p1: int, score_p2: int, wins_needed: int = MATCH_WINS_NEEDED) -> str | None:
    """Retorna 'P1' ou 'P2' se algum lutador já fechou a partida (Melhor-de-3), senão None."""
    if score_p1 >= wins_needed:
        return "P1"
    if score_p2 >= wins_needed:
        return "P2"
    return None


def render_round_pips(surface: pygame.Surface, score_p1: int, score_p2: int, p1_color, p2_color, wins_needed: int = MATCH_WINS_NEEDED, panel_rect: pygame.Rect = None, p1_total: int | None = None):
    """Desenha os marcadores (pips) de rounds vencidos por cada jogador na HUD (`p1_total` amplia só os do jogador 1)."""
    pip_radius = 6
    spacing = 18
    if panel_rect is not None:
        y = panel_rect.y + 6
        start_x_p1 = panel_rect.x + 16
        start_x_p2 = panel_rect.right - 16
    else:
        y = 46
        start_x_p1 = 24
        start_x_p2 = SCREEN_WIDTH - 24

    for i in range(p1_total or wins_needed):
        color = p1_color if i < score_p1 else (70, 70, 80)
        cx = start_x_p1 + i * spacing
        pygame.draw.circle(surface, color, (cx, y), pip_radius)
        pygame.draw.circle(surface, (20, 20, 25), (cx, y), pip_radius, width=2)

    for i in range(wins_needed):
        color = p2_color if i < score_p2 else (70, 70, 80)
        cx = start_x_p2 - i * spacing
        pygame.draw.circle(surface, color, (cx, y), pip_radius)
        pygame.draw.circle(surface, (20, 20, 25), (cx, y), pip_radius, width=2)


def render_damage_bars(surface: pygame.Surface, p1, p2, p1_color, p2_color, panel_rect: pygame.Rect):
    """Barras de dano segmentadas (uma seção por ponto de vida) logo abaixo do contador de rounds."""
    seg_w, seg_h, gap = 34, 9, 4
    y = panel_rect.bottom + 6
    for fighter, color, from_left in ((p1, p1_color, True), (p2, p2_color, False)):
        if getattr(fighter, "is_boss", False):
            continue  # o chefe tem a própria barra (render_boss_bar)
        max_hp = max(1, getattr(fighter, "max_hp", 2))
        hp = max(0, min(max_hp, getattr(fighter, "hp", max_hp)))
        total_w = max_hp * seg_w + (max_hp - 1) * gap
        x0 = panel_rect.x + 20 if from_left else panel_rect.right - 20 - total_w
        backing = pygame.Rect(x0 - 3, y - 3, total_w + 6, seg_h + 6)
        pygame.draw.rect(surface, (20, 24, 22), backing, border_radius=5)
        pygame.draw.rect(surface, (60, 75, 68), backing, 1, border_radius=5)
        for i in range(max_hp):
            # P1 esvazia da direita para a esquerda; P2 da esquerda para a direita (espelhado)
            slot = i if from_left else max_hp - 1 - i
            seg = pygame.Rect(x0 + slot * (seg_w + gap), y, seg_w, seg_h)
            if i < hp:
                pygame.draw.rect(surface, color, seg, border_radius=2)
                pygame.draw.line(surface, tuple(min(255, c + 70) for c in color), (seg.x + 2, seg.y + 1), (seg.right - 3, seg.y + 1))
            else:
                pygame.draw.rect(surface, (44, 30, 32), seg, border_radius=2)
                pygame.draw.rect(surface, (120, 50, 55), seg, 1, border_radius=2)


def render_boss_bar(surface: pygame.Surface, boss, panel_rect: pygame.Rect):
    """Barra do chefe: 10 pontos de vida em 5 grupos de 2 (um por fase), com o nome e o título da fase."""
    seg_w, seg_h, gap, group_gap = 22, 10, 3, 7
    max_hp = max(1, boss.max_hp)
    groups = max_hp // 2
    total_w = groups * (2 * seg_w + gap) + (groups - 1) * group_gap
    x0 = panel_rect.right - 20 - total_w
    y = panel_rect.bottom + 6
    backing = pygame.Rect(x0 - 3, y - 3, total_w + 6, seg_h + 6)
    pygame.draw.rect(surface, (20, 24, 22), backing, border_radius=5)
    pygame.draw.rect(surface, (60, 75, 68), backing, 1, border_radius=5)
    for i in range(max_hp):
        g, k = divmod(i, 2)
        # Esvazia da esquerda para a direita; a fase atual fica destacada
        seg = pygame.Rect(x0 + g * (2 * seg_w + gap + group_gap) + k * (seg_w + gap), y, seg_w, seg_h)
        if i < boss.hp:
            color = (240, 110, 70) if g == boss.phase else (200, 90, 62)
            pygame.draw.rect(surface, color, seg, border_radius=2)
            pygame.draw.line(surface, (255, 190, 150), (seg.x + 2, seg.y + 1), (seg.right - 3, seg.y + 1))
        else:
            pygame.draw.rect(surface, (44, 30, 32), seg, border_radius=2)
            pygame.draw.rect(surface, (120, 50, 55), seg, 1, border_radius=2)
    font = get_text_font(15)
    label = font.render(f"{boss.name.upper()} — {t('boss_phase_label', n=boss.phase + 1, title=boss.phase_title)}", True, (255, 200, 150))
    surface.blit(label, (panel_rect.right - 20 - label.get_width(), y + seg_h + 6))


class RoundResultScreen:
    """Tela final de partida (Melhor-de-3), com opção de revanche rápida."""

    def __init__(self):
        self.active = False
        self.winner_name = ""
        self.winner_color = (255, 255, 255)
        self.score_p1 = 0
        self.score_p2 = 0
        self.timer = 0.0

    def show(self, winner_name: str, winner_color, score_p1: int, score_p2: int):
        """Ativa a tela de resultados exibindo o vencedor da partida e o placar final."""
        self.active = True
        self.winner_name = winner_name
        self.winner_color = winner_color
        self.score_p1 = score_p1
        self.score_p2 = score_p2
        self.timer = 0.0

    def hide(self):
        """Oculta a tela de resultados (chamado ao iniciar uma revanche)."""
        self.active = False
        self.timer = 0.0

    def update(self, dt: float):
        if self.active:
            self.timer += dt

    def can_accept_rematch(self) -> bool:
        """Pequeno atraso antes de aceitar o pedido de revanche, evitando reinícios acidentais."""
        return self.active and self.timer > 0.35

    def render(self, surface: pygame.Surface):
        """Desenha a tela final de partida com o vencedor, placar e prompt de revanche."""
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = int(min(205, self.timer * 420))
        overlay.fill((10, 8, 12, alpha))
        surface.blit(overlay, (0, 0))

        font_title = get_title_font(50)
        font_sub = get_text_font(22)
        font_prompt = get_text_font(18)

        title_str = f"{self.winner_name} VENCE A PARTIDA!"
        title_surf = font_title.render(title_str, True, self.winner_color)
        title_shadow = font_title.render(title_str, True, (10, 10, 10))
        tx = SCREEN_WIDTH // 2 - title_surf.get_width() // 2
        ty = SCREEN_HEIGHT // 2 - 90
        surface.blit(title_shadow, (tx + 3, ty + 3))
        surface.blit(title_surf, (tx, ty))

        score_str = f"{self.score_p1}  -  {self.score_p2}"
        score_surf = font_sub.render(score_str, True, (235, 230, 220))
        surface.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, ty + 70))

        if self.can_accept_rematch():
            pulse = 0.65 + 0.35 * abs(math.sin(self.timer * 3.2))
            prompt_surf = font_prompt.render(t("rematch_prompt"), True, (255, 255, 255))
            prompt_surf.set_alpha(int(255 * pulse))
            surface.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, ty + 118))
