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
from src.ui.svg_icon_renderer import render_text_with_icons

MATCH_WINS_NEEDED = 2  # Melhor-de-3: primeiro a vencer 2 rounds fecha a partida


def check_match_winner(score_p1: int, score_p2: int, wins_needed: int = MATCH_WINS_NEEDED) -> str | None:
    """Retorna 'P1' ou 'P2' se algum lutador já fechou a partida (Melhor-de-3), senão None."""
    if score_p1 >= wins_needed:
        return "P1"
    if score_p2 >= wins_needed:
        return "P2"
    return None


def render_round_pips(surface: pygame.Surface, score_p1: int, score_p2: int, p1_color, p2_color, wins_needed: int = MATCH_WINS_NEEDED, panel_rect: pygame.Rect = None, p1_total: int | None = None):
    """Desenha os marcadores (pips) de rounds vencidos como medalhões de laca urushi com incrustação em folha de ouro."""
    pip_radius = 7
    spacing = 19
    if panel_rect is not None:
        y = panel_rect.y + 7
        start_x_p1 = panel_rect.x + 18
        start_x_p2 = panel_rect.right - 18
    else:
        y = 46
        start_x_p1 = 24
        start_x_p2 = SCREEN_WIDTH - 24

    for i in range(p1_total or wins_needed):
        cx = start_x_p1 + i * spacing
        won = i < score_p1
        # Base de laca escura
        pygame.draw.circle(surface, (14, 16, 18), (cx, y), pip_radius)
        if won:
            # Incrustação dourada com centro no tom do guerreiro
            pygame.draw.circle(surface, (218, 175, 75), (cx, y), pip_radius)
            pygame.draw.circle(surface, p1_color, (cx, y), pip_radius - 2)
            pygame.draw.circle(surface, (255, 235, 150), (cx - 1, y - 1), 2)
        else:
            pygame.draw.circle(surface, (55, 60, 65), (cx, y), pip_radius, width=1)
            pygame.draw.circle(surface, (28, 30, 32), (cx, y), pip_radius - 2)

    for i in range(wins_needed):
        cx = start_x_p2 - i * spacing
        won = i < score_p2
        pygame.draw.circle(surface, (14, 16, 18), (cx, y), pip_radius)
        if won:
            pygame.draw.circle(surface, (218, 175, 75), (cx, y), pip_radius)
            pygame.draw.circle(surface, p2_color, (cx, y), pip_radius - 2)
            pygame.draw.circle(surface, (255, 235, 150), (cx - 1, y - 1), 2)
        else:
            pygame.draw.circle(surface, (55, 60, 65), (cx, y), pip_radius, width=1)
            pygame.draw.circle(surface, (28, 30, 32), (cx, y), pip_radius - 2)


def render_damage_bars(surface: pygame.Surface, p1, p2, p1_color, p2_color, panel_rect: pygame.Rect):
    """
    Barras de dano segmentadas em paralelogramos chanfrados com moldura em folha de ouro
    e rastro animado de perda de vida (damage drain trail carmesim/branco).
    """
    seg_w, seg_h, gap = 34, 10, 4
    skew = 3  # Chanfro de paralelogramo elegante
    y = panel_rect.bottom + 6

    for fighter, color, from_left in ((p1, p1_color, True), (p2, p2_color, False)):
        if getattr(fighter, "is_boss", False):
            continue  # o chefe tem a própria barra (render_boss_bar)

        max_hp = max(1, getattr(fighter, "max_hp", 2))
        hp = max(0, min(max_hp, getattr(fighter, "hp", max_hp)))

        # Rastro de dano interpolado (drain trail)
        drain_hp = getattr(fighter, "_drain_hp", float(hp))
        if drain_hp > hp:
            fighter._drain_hp = max(float(hp), drain_hp - 0.02)
            drain_hp = fighter._drain_hp
        elif drain_hp < hp:
            fighter._drain_hp = float(hp)
            drain_hp = float(hp)

        total_w = max_hp * seg_w + (max_hp - 1) * gap + skew
        x0 = panel_rect.x + 20 if from_left else panel_rect.right - 20 - total_w

        # Placa traseira de laca escura com bisel dourado
        back_poly = [
            (x0 - 4 + (skew if not from_left else 0), y - 3),
            (x0 + total_w + 4 + (skew if not from_left else 0), y - 3),
            (x0 + total_w + 4 - (skew if from_left else 0), y + seg_h + 3),
            (x0 - 4 - (skew if from_left else 0), y + seg_h + 3),
        ]
        pygame.draw.polygon(surface, (14, 18, 16), back_poly)
        pygame.draw.polygon(surface, (180, 145, 60), back_poly, width=1)

        for i in range(max_hp):
            # P1 esvazia da direita para a esquerda; P2 da esquerda para a direita (espelhado)
            slot = i if from_left else max_hp - 1 - i
            sx = x0 + slot * (seg_w + gap)

            # Paralelogramo chanfrado do segmento de vida
            seg_pts = [
                (sx + skew, y),
                (sx + seg_w + skew, y),
                (sx + seg_w, y + seg_h),
                (sx, y + seg_h),
            ] if from_left else [
                (sx, y),
                (sx + seg_w, y),
                (sx + seg_w + skew, y + seg_h),
                (sx + skew, y + seg_h),
            ]

            if i < hp:
                # Segmento vivo com brilho de lâmina
                pygame.draw.polygon(surface, color, seg_pts)
                highlight_pts = [seg_pts[0], seg_pts[1], (seg_pts[1][0] - 1, seg_pts[1][1] + 2), (seg_pts[0][0] + 1, seg_pts[0][1] + 2)]
                pygame.draw.polygon(surface, tuple(min(255, c + 75) for c in color), highlight_pts)
                pygame.draw.polygon(surface, (218, 175, 75), seg_pts, width=1)
            elif i < int(math.ceil(drain_hp)):
                # Rastro animado de perda recente de vida (flash carmesim / branco)
                pygame.draw.polygon(surface, (240, 85, 75), seg_pts)
                pygame.draw.polygon(surface, (255, 230, 200), seg_pts, width=1)
            else:
                # Segmento de vida esvaziado
                pygame.draw.polygon(surface, (36, 24, 26), seg_pts)
                pygame.draw.polygon(surface, (95, 40, 45), seg_pts, width=1)


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
    pygame.draw.rect(surface, (180, 145, 60), backing, 1, border_radius=5)
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
    """Tela final de partida (Melhor-de-3) com painel sumi-e em laca e opção de revanche rápida."""

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
        """Desenha a tela final de partida com painel de laca escura e acabamento cerimonial."""
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = int(min(220, self.timer * 420))
        overlay.fill((8, 10, 12, alpha))
        surface.blit(overlay, (0, 0))

        # Painel central cerimonial em laca urushi com moldura dourada
        panel_w, panel_h = 680, 260
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 20
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (16, 18, 22, 235), (0, 0, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(panel_surf, (218, 175, 75, 220), (0, 0, panel_w, panel_h), width=2, border_radius=10)
        pygame.draw.rect(panel_surf, (140, 105, 38, 160), (4, 4, panel_w - 8, panel_h - 8), width=1, border_radius=8)
        surface.blit(panel_surf, (panel_x, panel_y))

        font_title = get_title_font(44)
        font_sub = get_title_font(28)
        font_prompt = get_text_font(18)

        # Selo Inkan de Vitória (勝)
        seal_size = 38
        seal_x = panel_x + 36
        seal_y = panel_y + 36
        pygame.draw.rect(surface, (185, 34, 38), (seal_x, seal_y, seal_size, seal_size), border_radius=4)
        pygame.draw.rect(surface, (255, 225, 110), (seal_x, seal_y, seal_size, seal_size), width=2, border_radius=4)
        kanji_font = get_title_font(24)
        k_surf = kanji_font.render("勝", True, (255, 245, 225))
        surface.blit(k_surf, (seal_x + (seal_size - k_surf.get_width()) // 2, seal_y + (seal_size - k_surf.get_height()) // 2))

        title_str = f"{self.winner_name} VENCE A PARTIDA!"
        max_title_w = panel_w - 116
        sz = 40
        while sz > 18:
            test_font = get_title_font(sz)
            if test_font.size(title_str)[0] <= max_title_w:
                font_title = test_font
                break
            sz -= 2
        else:
            font_title = get_title_font(18)

        title_surf = font_title.render(title_str, True, self.winner_color)
        title_shadow = font_title.render(title_str, True, (0, 0, 0))
        tx = panel_x + 88
        ty = panel_y + 36 + (38 - title_surf.get_height()) // 2
        surface.blit(title_shadow, (tx + 2, ty + 2))
        surface.blit(title_surf, (tx, ty))

        score_str = f"{self.score_p1}   —   {self.score_p2}"
        score_surf = font_sub.render(score_str, True, (240, 225, 175))
        surface.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, panel_y + 115))

        if self.can_accept_rematch():
            pulse = 0.65 + 0.35 * abs(math.sin(self.timer * 3.2))
            render_text_with_icons(
                surface, font_prompt, t("rematch_prompt"),
                SCREEN_WIDTH // 2, panel_y + 195,
                text_color=(255, 240, 200), icon_size=18, alpha=int(255 * pulse)
            )
