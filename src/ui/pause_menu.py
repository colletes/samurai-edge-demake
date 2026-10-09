"""
Menu de pausa do duelo (ESC): retomar, configurações, trocar cenário/lutador, menu principal e sair.
Desenhado sobre o último quadro do duelo, no estilo pergaminho Sumi-E.
"""
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD
from src.effects import parchment as pm
from src.i18n import t
from src.ui.fonts import get_title_font, get_text_font

ACTION_RESUME = "RESUME"
ACTION_SETTINGS = "SETTINGS"
ACTION_ARENA = "ARENA"
ACTION_FIGHTER = "FIGHTER"
ACTION_MAIN_MENU = "MAIN_MENU"
ACTION_QUIT = "QUIT"
ACTION_ABANDON = "ABANDON"

_ITEMS = [
    ("pause_resume", ACTION_RESUME),
    ("pause_settings", ACTION_SETTINGS),
    ("pause_arena", ACTION_ARENA),
    ("pause_fighter", ACTION_FIGHTER),
    ("pause_main_menu", ACTION_MAIN_MENU),
    ("pause_quit", ACTION_QUIT),
]

_ARCADE_ITEMS = [
    ("pause_resume", ACTION_RESUME),
    ("pause_settings", ACTION_SETTINGS),
    ("arcade_abandon", ACTION_ABANDON),
    ("pause_quit", ACTION_QUIT),
]

PANEL_W, ROW_H, HEADER_H, PAD_BOTTOM = 460, 52, 86, 34


class PauseMenu:
    def __init__(self):
        self.is_open = False
        self.selected = 0
        self.items = _ITEMS
        self.confirm_abandon = False
        self.item_rects: list[pygame.Rect] = []
        self._snapshot: pygame.Surface | None = None
        self._axis_held = False

    def open(self, snapshot: pygame.Surface, arcade: bool = False, demo: bool = False):
        """Abre o menu congelando o quadro atual como fundo (Arcade: sem cenário/lutador; demo: sem escolha de cenário)."""
        self.is_open = True
        self.items = _ARCADE_ITEMS if arcade else [i for i in _ITEMS if not (demo and i[1] == ACTION_ARENA)]
        self.confirm_abandon = False
        self.selected = 0
        self._snapshot = snapshot.copy()
        self._axis_held = False

    def close(self):
        self.is_open = False
        self._snapshot = None

    def _choose(self, index: int) -> str | None:
        """Abandonar a jornada pede uma segunda confirmação."""
        action = self.items[index][1]
        if action == ACTION_ABANDON and not self.confirm_abandon:
            self.confirm_abandon = True
            return None
        return action

    def _move(self, step: int):
        self.confirm_abandon = False
        self.selected = (self.selected + step) % len(self.items)

    def handle_event(self, event, ctrl_mgr=None) -> str | None:
        """Devolve a ação escolhida (ACTION_*) ou None."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return ACTION_RESUME
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._move(1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_e, pygame.K_j):
                return self._choose(self.selected)

        elif event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.item_rects):
                if r.collidepoint(event.pos):
                    self.selected = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.item_rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    return self._choose(i)

        elif event.type in (pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION):
            from src.input.controller_manager import get_dpad_motion_from_event
            motion = get_dpad_motion_from_event(event)
            if motion:
                if motion[1] != 0:
                    self._move(motion[1])
                return None
            if event.type == pygame.JOYBUTTONDOWN and ctrl_mgr is not None:
                if ctrl_mgr.is_event_menu_confirm(event) or event.button in (0, 2):
                    return self._choose(self.selected)
                if ctrl_mgr.is_event_menu_cancel(event) or ctrl_mgr.is_event_menu_pause(event) or event.button in (1, 6, 7):
                    return ACTION_RESUME

        elif event.type == pygame.JOYAXISMOTION and event.axis == 1:
            if event.value > 0.65 and not self._axis_held:
                self._move(1)
                self._axis_held = True
            elif event.value < -0.65 and not self._axis_held:
                self._move(-1)
                self._axis_held = True
            elif abs(event.value) < 0.25:
                self._axis_held = False

        return None

    def render(self, surface: pygame.Surface):
        if self._snapshot is not None:
            surface.blit(self._snapshot, (0, 0))
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((6, 6, 10, 170))
        surface.blit(shade, (0, 0))

        panel_h = HEADER_H + ROW_H * len(self.items) + PAD_BOTTOM
        panel = pygame.Rect((SCREEN_WIDTH - PANEL_W) // 2, (SCREEN_HEIGHT - panel_h) // 2, PANEL_W, panel_h)
        pm.draw_paper_card(surface, panel, seed=57)

        title_font = get_title_font(30)
        title = pm.render_ink(title_font, t("pause_title"), pm.INK)
        surface.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 24))
        pygame.draw.line(surface, pm.INK_SOFT, (panel.x + 60, panel.y + HEADER_H - 10), (panel.right - 60, panel.y + HEADER_H - 10), 1)

        item_font = get_title_font(19)
        self.item_rects = []
        for i, (key, _action) in enumerate(self.items):
            row = pygame.Rect(panel.x + 36, panel.y + HEADER_H + i * ROW_H, PANEL_W - 72, ROW_H - 6)
            self.item_rects.append(row)
            selected = i == self.selected
            text = t("arcade_abandon_confirm") if (self.confirm_abandon and _action == ACTION_ABANDON) else t(key)
            if selected:
                pm.draw_brush_highlight(surface, row.inflate(10, 4), pm.SEAL_RED, seed=i + 3)
                label = item_font.render(text, True, (252, 244, 226))
            else:
                label = pm.render_ink(item_font, text, pm.INK)
            max_w = row.width - 24
            if label.get_width() > max_w:
                label = pygame.transform.smoothscale(label, (max_w, label.get_height()))
            surface.blit(label, (row.centerx - label.get_width() // 2, row.centery - label.get_height() // 2))
