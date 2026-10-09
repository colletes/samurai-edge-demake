"""
Tela de Seleção de Arena de Batalha (Arena Select Screen).
As cartas seguem a ordem do elenco (src/roster.py): cada arena mostra o retrato circular do lutador dono dela,
com a carta Aleatória ao final. Arenas ainda não construídas aparecem bloqueadas ("em breve") e liberam sozinhas
quando o spec é registrado em src/world/arenas.py. A arena escolhida aparece em detalhe no painel inferior.
"""
import math
import os
import random
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_BG,
    ARENA_BAMBOO, ARENA_KYOTO, ARENA_RANDOM, ARENA_GANRYU, ARENA_IGA, ARENA_PIRATE_DECK, ARENA_SHADOW_CAVE, ARENA_MIST_TEMPLE, ARENA_FOREST_CAMP, ARENA_NAGASHINO, ARENA_KABUKI_STAGE, ARENA_MOUNTAIN_SHRINE, ARENA_BAROQUE_COURT,
    get_asset_path
)
from src.i18n import t, get_lang
from src.effects import parchment as pm
from src.roster import ARENA_ORDER, FIGHTER_BY_ARENA, FIGHTER_NAME_KEY
from src.world.arenas import arena_ids
from src.ui.arena_preview import render_arena_preview
from src.ui.portraits import get_portrait
from src.ui.fonts import get_title_font, get_text_font
from src.ui.font_manager import render_text_fx
from src.ui.character_select import draw_scroll_frame, draw_enso_circle

# Sufixo das chaves de texto das três primeiras arenas; as demais usam o próprio id (arena_<id>_subtitle etc.)
_DETAIL_KEYS = {ARENA_BAMBOO: "bamboo", ARENA_KYOTO: "kyoto", ARENA_GANRYU: "ganryu", ARENA_RANDOM: "random"}
_THEME_COLORS = {
    ARENA_BAMBOO: (60, 140, 70), ARENA_KYOTO: (205, 75, 30), ARENA_GANRYU: (96, 150, 176), ARENA_RANDOM: (140, 120, 210),
    ARENA_IGA: (112, 124, 176), ARENA_PIRATE_DECK: (74, 140, 160), ARENA_SHADOW_CAVE: (140, 100, 196), ARENA_MIST_TEMPLE: (110, 150, 200), ARENA_FOREST_CAMP: (96, 160, 80), ARENA_NAGASHINO: (190, 120, 70), ARENA_KABUKI_STAGE: (200, 70, 80), ARENA_MOUNTAIN_SHRINE: (120, 160, 200), ARENA_BAROQUE_COURT: (80, 110, 190),
}
_HAZARD_COLORS = {
    ARENA_BAMBOO: (120, 220, 100), ARENA_KYOTO: (255, 75, 45), ARENA_GANRYU: (150, 215, 240), ARENA_RANDOM: COLOR_GOLD,
    ARENA_IGA: (240, 170, 80), ARENA_PIRATE_DECK: (120, 205, 235), ARENA_SHADOW_CAVE: (214, 130, 220), ARENA_MIST_TEMPLE: (255, 170, 90), ARENA_FOREST_CAMP: (240, 200, 110), ARENA_NAGASHINO: (255, 120, 60), ARENA_KABUKI_STAGE: (255, 196, 90), ARENA_MOUNTAIN_SHRINE: (255, 226, 150), ARENA_BAROQUE_COURT: (150, 210, 240),
}
_LOCKED_COLOR = (92, 92, 100)

GRID_COLS = 7
MARGIN_X = 40
GAP = 12
CARD_H = 128
GRID_Y = 108
PANEL_RECT = pygame.Rect(MARGIN_X, 392, SCREEN_WIDTH - 2 * MARGIN_X, 198)
PREVIEW_SIZE = (328, 160)


class ArenaSelectScreen:
    def __init__(self):
        self.selected_idx = 0
        self.anim_time = 0.0
        self.card_rects: list[pygame.Rect] = []
        self.locked_flash = 0.0
        self._axis_held = False
        self._card_preview_cache: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}

        # Artes de conceito disponíveis (as demais arenas usam a prévia gerada pelo próprio gerador)
        self.preview_surfs = {}
        preview_files = {
            ARENA_BAMBOO: get_asset_path("assets/concepts/bamboo_forest_concept.jpg"),
            ARENA_KYOTO: get_asset_path("assets/concepts/kyoto_bakumatsu_concept.jpg"),
            ARENA_RANDOM: get_asset_path("assets/concepts/random_arena_concept.jpg"),
        }
        # As demais arenas seguem a convenção assets/concepts/<id>_concept.jpg (sem a imagem, usa a prévia gerada)
        for arena_id in ARENA_ORDER:
            preview_files.setdefault(arena_id, get_asset_path(f"assets/concepts/{arena_id}_concept.jpg"))
        for arena_id, path in preview_files.items():
            if os.path.exists(path):
                try:
                    try:
                        raw = pygame.image.load(path).convert()
                    except Exception:
                        raw = pygame.image.load(path)
                    # Escala para cobrir o quadro sem distorcer e recorta o centro (artes com proporções diferentes)
                    factor = max(PREVIEW_SIZE[0] / raw.get_width(), PREVIEW_SIZE[1] / raw.get_height())
                    cover = pygame.transform.smoothscale(
                        raw, (math.ceil(raw.get_width() * factor), math.ceil(raw.get_height() * factor)))
                    crop = pygame.Rect(0, 0, *PREVIEW_SIZE)
                    crop.center = cover.get_rect().center
                    self.preview_surfs[arena_id] = cover.subsurface(crop).copy()
                except Exception:
                    self.preview_surfs[arena_id] = None

        self._arenas_lang = None
        self._arenas_cache: list[dict] = []

    # ------------------------------------------------------------------ dados
    @property
    def arenas(self) -> list[dict]:
        # Reconstrói os textos quando o idioma muda
        lang = get_lang()
        if self._arenas_lang != lang:
            self._arenas_cache = self._build_arenas()
            self._arenas_lang = lang
        return self._arenas_cache

    @property
    def random_idx(self) -> int:
        return len(self.arenas) - 1

    @staticmethod
    def _name_key(arena_id: str) -> str:
        return f"arena_{_DETAIL_KEYS.get(arena_id, arena_id)}_name"

    def _build_arenas(self) -> list[dict]:
        unlocked = set(arena_ids())
        cards = []
        for arena_id in ARENA_ORDER:
            fighter_id = FIGHTER_BY_ARENA[arena_id]
            detail = _DETAIL_KEYS.get(arena_id, arena_id)
            locked = arena_id not in unlocked
            card = {
                "id": arena_id,
                "fighter_id": fighter_id,
                "fighter_name": t(FIGHTER_NAME_KEY[fighter_id]),
                "locked": locked,
                "name": t(self._name_key(arena_id)),
                "theme_color": _LOCKED_COLOR if locked else _THEME_COLORS.get(arena_id, (96, 150, 176)),
                "hazard_color": _HAZARD_COLORS.get(arena_id, COLOR_GOLD),
            }
            if not locked:
                card.update(subtitle=t(f"arena_{detail}_subtitle"), hazard_level=t(f"arena_{detail}_hazard"),
                            features=t(f"arena_{detail}_features"), tactics=t(f"arena_{detail}_tactics"))
            cards.append(card)
        cards.append({
            "id": ARENA_RANDOM, "fighter_id": None, "fighter_name": "", "locked": False,
            "name": t("arena_random_name"), "theme_color": _THEME_COLORS[ARENA_RANDOM], "hazard_color": COLOR_GOLD,
            "subtitle": t("arena_random_subtitle"), "hazard_level": t("arena_random_hazard"),
            "features": t("arena_random_features"), "tactics": t("arena_random_tactics"),
        })
        return cards

    # -------------------------------------------------------------- navegação
    def _vertical_step(self, idx: int) -> int:
        """Cima/baixo na grade: 7 cartas na linha 1; na linha 2, 5 arenas e o Aleatório ocupando as duas últimas colunas."""
        rnd = self.random_idx
        if idx == rnd:
            return 5  # sobe para a coluna do meio do Aleatório
        if idx < GRID_COLS:
            return idx + GRID_COLS if idx + GRID_COLS < rnd else rnd
        return idx - GRID_COLS

    def _move(self, dx: int, dy: int):
        n = len(self.arenas)
        if dx:
            self.selected_idx = (self.selected_idx + dx) % n
        if dy:
            self.selected_idx = self._vertical_step(self.selected_idx)

    def is_locked(self, idx: int | None = None) -> bool:
        return self.arenas[self.selected_idx if idx is None else idx]["locked"]

    def _confirm(self) -> str | None:
        """Devolve a arena escolhida; bloqueada não confirma (pisca o aviso)."""
        if self.is_locked():
            self.locked_flash = 0.7
            try:
                from src.audio.sound_events import SoundEvent
                from src.audio.sound_manager import SoundManager
                SoundManager.get_instance().play(SoundEvent.MENU_CANCEL)
            except Exception:
                pass
            return None
        return self.get_resolved_arena_id()

    def handle_event(self, event) -> str | None:
        """
        Retorna:
          - ID da arena escolhida (nunca de uma arena bloqueada)
          - "BACK": se pressionar ESC ou botão de voltar
          - None: se ainda na tela
        """
        from src.input.controller_manager import get_controller_manager, get_dpad_motion_from_event
        ctrl_mgr = get_controller_manager()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._move(-1, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._move(1, 0)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._move(0, -1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._move(0, 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e, pygame.K_j):
                return self._confirm()
            elif event.key == pygame.K_ESCAPE:
                return "BACK"

        elif event.type == pygame.JOYBUTTONDOWN:
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                self._move(d_dir[0], d_dir[1])
                return None
            if ctrl_mgr.is_event_menu_confirm(event) or event.button in (0, 2):
                return self._confirm()
            elif ctrl_mgr.is_event_menu_cancel(event) or event.button == 1:
                return "BACK"

        elif event.type == pygame.JOYHATMOTION:
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                self._move(d_dir[0], d_dir[1])

        elif event.type == pygame.JOYAXISMOTION:
            if event.axis in (0, 1):
                if abs(event.value) < 0.25:
                    self._axis_held = False
                elif abs(event.value) > 0.65 and not self._axis_held:
                    step = 1 if event.value > 0 else -1
                    self._move(step if event.axis == 0 else 0, step if event.axis == 1 else 0)
                    self._axis_held = True

        elif event.type == pygame.MOUSEMOTION:
            for idx, r in enumerate(self.card_rects):
                if r.collidepoint(event.pos):
                    self.selected_idx = idx

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for idx, r in enumerate(self.card_rects):
                if r.collidepoint(mx, my):
                    self.selected_idx = idx
                    return self._confirm()
            start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 65, 320, 42)
            if start_btn.collidepoint(mx, my):
                return self._confirm()

        return None

    def get_resolved_arena_id(self) -> str:
        chosen = self.arenas[self.selected_idx]["id"]
        if chosen == ARENA_RANDOM:
            return random.choice(arena_ids())  # só arenas já liberadas
        return chosen

    def update(self, dt: float):
        self.anim_time += dt
        self.locked_flash = max(0.0, self.locked_flash - dt)

    # ----------------------------------------------------------------- desenho
    def _get_header_shade(self) -> pygame.Surface:
        shade = getattr(self, "_header_shade", None)
        if shade is None:
            h = 104
            shade = pygame.Surface((SCREEN_WIDTH, h), pygame.SRCALPHA)
            for y in range(h):
                pygame.draw.line(shade, (6, 8, 8, int(190 * (1 - y / h) ** 1.2)), (0, y), (SCREEN_WIDTH, y))
            self._header_shade = shade
        return shade

    def _fit_text(self, text: str, color, max_w: int, size: int) -> pygame.Surface:
        """Renderiza o texto reduzindo a fonte até caber em max_w (mínimo 10px)."""
        while True:
            surf = get_text_font(size).render(text, True, color)
            if surf.get_width() <= max_w or size <= 10:
                return surf
            size -= 1

    def _arena_image(self, arena_id: str, size: tuple[int, int]) -> pygame.Surface | None:
        """Arte da arena no tamanho pedido (conceito ou prévia gerada), com cache; None se não houver."""
        key = (arena_id, size)
        if key in self._card_preview_cache:
            return self._card_preview_cache[key]
        image = None
        art = self.preview_surfs.get(arena_id)
        if art is not None:
            factor = max(size[0] / art.get_width(), size[1] / art.get_height())
            cover = pygame.transform.smoothscale(art, (math.ceil(art.get_width() * factor), math.ceil(art.get_height() * factor)))
            crop = pygame.Rect(0, 0, *size)
            crop.center = cover.get_rect().center
            image = cover.subsurface(crop).copy()
        elif arena_id in arena_ids():
            image = render_arena_preview(arena_id, size)
        if image is not None:
            self._card_preview_cache[key] = image
        return image

    def _draw_art(self, surface, arena: dict, rect: pygame.Rect, big: bool):
        """Arte (ou silhueta bloqueada) dentro de `rect`; o Aleatório ganha brilho e interrogação."""
        image = None if arena["locked"] else self._arena_image(arena["id"], rect.size)
        if image is None:
            pygame.draw.rect(surface, (18, 20, 24), rect, border_radius=6)
            for i in range(0, rect.width + rect.height, 14):
                pygame.draw.line(surface, (28, 30, 36), (rect.x + min(i, rect.width), rect.y + max(0, i - rect.width)),
                                 (rect.x + max(0, i - rect.height), rect.y + min(i, rect.height)), 1)
            label = get_title_font(18 if big else 12).render(t("arena_locked"), True, (150, 150, 160))
            surface.blit(label, label.get_rect(center=rect.center))
        else:
            surface.blit(image, rect.topleft)
            if arena["id"] == ARENA_RANDOM:
                pulse = 0.5 + 0.5 * math.sin(self.anim_time * 4.0)
                glow = pygame.Surface(rect.size, pygame.SRCALPHA)
                glow.fill((120, 80, 200, int(35 + 25 * pulse)))
                surface.blit(glow, rect.topleft)
                q = get_title_font(54 if big else 28).render("?", True, COLOR_GOLD)
                surface.blit(q, q.get_rect(center=rect.center))
        pygame.draw.rect(surface, (80, 90, 85), rect, 1, border_radius=6)

    def _draw_portrait(self, surface, arena: dict, cx: int, cy: int, radius: int, selected: bool):
        """Retrato circular do lutador dono da arena, com anel ensō; o Aleatório mostra uma interrogação."""
        ring = COLOR_GOLD if selected else arena["theme_color"]
        draw_enso_circle(surface, cx, cy, radius + 3, ring, self.anim_time)
        if arena["fighter_id"] is None:
            pygame.draw.circle(surface, (22, 20, 30), (cx, cy), radius)
            q = get_title_font(int(radius * 1.3)).render("?", True, COLOR_GOLD)
            surface.blit(q, q.get_rect(center=(cx, cy + 1)))
            return
        portrait = get_portrait(arena["fighter_id"], size=(radius * 2, radius * 2), circular=True)
        if portrait is not None:
            surface.blit(portrait, (cx - radius, cy - radius))
        if arena["locked"]:
            shade = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shade, (10, 10, 14, 120), (radius, radius), radius)
            surface.blit(shade, (cx - radius, cy - radius))

    def _card_rect(self, idx: int) -> pygame.Rect:
        card_w = (SCREEN_WIDTH - 2 * MARGIN_X - (GRID_COLS - 1) * GAP) // GRID_COLS
        if idx == self.random_idx:
            return pygame.Rect(MARGIN_X + 5 * (card_w + GAP), GRID_Y + CARD_H + GAP, 2 * card_w + GAP, CARD_H)
        row, col = divmod(idx, GRID_COLS)
        return pygame.Rect(MARGIN_X + col * (card_w + GAP), GRID_Y + row * (CARD_H + GAP), card_w, CARD_H)

    def _draw_card(self, surface, idx: int, arena: dict):
        rect = self._card_rect(idx)
        self.card_rects.append(rect)
        is_sel = (idx == self.selected_idx)
        draw_rect = rect.move(0, -4 if is_sel else 0)
        locked = arena["locked"]

        pygame.draw.rect(surface, (34, 42, 38) if is_sel else (24, 28, 28), draw_rect, border_radius=9)
        border = arena["theme_color"] if is_sel else (55, 62, 60)
        pygame.draw.rect(surface, border, draw_rect, 3 if is_sel else 1, border_radius=9)
        if is_sel:
            pulse = 0.5 + 0.5 * math.sin(self.anim_time * 6.0)
            glow = tuple(int(c * pulse) for c in COLOR_GOLD)
            pygame.draw.rect(surface, glow, draw_rect.inflate(6, 6), 2, border_radius=11)

        art_rect = pygame.Rect(draw_rect.x + 6, draw_rect.y + 6, draw_rect.width - 12, 62)
        self._draw_art(surface, arena, art_rect, big=False)

        # Retrato do dono da arena sobre o canto inferior da prévia
        self._draw_portrait(surface, arena, draw_rect.x + 32, art_rect.bottom - 2, 22, is_sel)

        sub = arena["fighter_name"] if arena["fighter_id"] else ""
        text_x = draw_rect.x + 62
        sub_s = self._fit_text(sub, (130, 140, 135) if locked else (COLOR_GOLD if is_sel else (185, 195, 190)),
                               draw_rect.right - text_x - 6, 13)
        surface.blit(sub_s, (text_x, art_rect.bottom + 8))
        name_col = (150, 150, 158) if locked else (COLOR_GOLD if is_sel else COLOR_WHITE)
        name_s = self._fit_text(arena["name"], name_col, draw_rect.width - 14, 13)
        surface.blit(name_s, (draw_rect.x + 8, draw_rect.bottom - 8 - name_s.get_height()))

    def _draw_panel(self, surface, arena: dict, fonts: dict):
        """Detalhe da arena selecionada: arte grande, retrato do lutador, perigo, cenário e dica."""
        panel = PANEL_RECT
        flash = self.locked_flash > 0.0
        border = (220, 70, 60) if flash and int(self.anim_time * 14) % 2 == 0 else arena["theme_color"]
        pygame.draw.rect(surface, (22, 28, 26), panel, border_radius=10)
        pygame.draw.rect(surface, border, panel, 2, border_radius=10)

        art_rect = pygame.Rect(panel.x + 16, panel.y + 18, *PREVIEW_SIZE)
        self._draw_art(surface, arena, art_rect, big=True)

        x0 = art_rect.right + 26
        self._draw_portrait(surface, arena, x0 + 34, panel.y + 52, 32, True)
        tx = x0 + 84
        max_w = panel.right - tx - 20
        surface.blit(fonts["title"].render(arena["name"], True, COLOR_GOLD), (tx, panel.y + 18))
        if arena["fighter_id"] is not None:
            owner = self._fit_text(t("arena_of_fighter", name=arena["fighter_name"].upper()), (170, 190, 200), max_w, 14)
            surface.blit(owner, (tx, panel.y + 52))
        if arena["locked"]:
            surface.blit(fonts["title"].render(t("arena_locked"), True, (200, 200, 210)), (tx, panel.y + 86))
            surface.blit(self._fit_text(t("arena_locked_hint"), (150, 155, 160), max_w, 15), (tx, panel.y + 120))
            return
        surface.blit(self._fit_text(arena["subtitle"], (180, 190, 185), max_w, 14), (tx, panel.y + 74))

        y = panel.y + 104
        hz_label = fonts["body"].render(t("arena_hazard_label"), True, (160, 160, 165))
        surface.blit(hz_label, (x0, y))
        hz = self._fit_text(arena["hazard_level"], arena["hazard_color"], panel.right - x0 - hz_label.get_width() - 36, 14)
        surface.blit(hz, (x0 + hz_label.get_width() + 8, y))
        y += 26
        ft_label = fonts["body"].render(t("arena_features_label"), True, COLOR_GOLD)
        surface.blit(ft_label, (x0, y))
        self._draw_multiline_text(surface, arena["features"], x0 + ft_label.get_width() + 8, y,
                                  panel.right - x0 - ft_label.get_width() - 36, fonts["body"], (200, 205, 200), 1)
        y += 26
        tc_label = fonts["body"].render(t("arena_tactics_label"), True, (130, 210, 240))
        surface.blit(tc_label, (x0, y))
        self._draw_multiline_text(surface, arena["tactics"], x0 + tc_label.get_width() + 8, y,
                                  panel.right - x0 - tc_label.get_width() - 36, fonts["body"], (175, 185, 180), 2)

    def render(self, surface: pygame.Surface, font_large, font_mid, font_small):
        fonts = {"title": get_title_font(22), "body": get_text_font(14)}
        font_oriental_title = get_title_font(28)
        font_oriental_btn = get_title_font(17)
        font_zen_sub = get_text_font(14)

        scene = pm.get_scene_background(dim=150)
        if scene is not None:
            surface.blit(scene, (0, 0))
        else:
            surface.fill(COLOR_BG)
            draw_scroll_frame(surface, margin_top=100, margin_bottom=90, margin_sides=20)

        # Título sobre faixa escura em gradiente (legibilidade sobre a cena)
        surface.blit(self._get_header_shade(), (0, 0))
        fx = dict(outline=True, outline_color=(10, 8, 6), outline_width=1, shadow=True, shadow_offset=(2, 2))
        header_surf = render_text_fx(font_oriental_title, t("select_arena_title"), COLOR_GOLD, **fx)
        surface.blit(header_surf, header_surf.get_rect(midtop=(SCREEN_WIDTH // 2, 18)))
        sub_surf = render_text_fx(font_zen_sub, t("select_arena_subtitle"), (225, 228, 222), **fx)
        surface.blit(sub_surf, sub_surf.get_rect(midtop=(SCREEN_WIDTH // 2, 62)))

        arenas = self.arenas
        self.card_rects = []
        for idx, arena in enumerate(arenas):
            self._draw_card(surface, idx, arena)
        self._draw_panel(surface, arenas[self.selected_idx], fonts)

        # Rodapé de confirmação (esmaecido para arena bloqueada)
        locked = self.is_locked()
        start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 65, 320, 42)
        pygame.draw.rect(surface, (40, 40, 44) if locked else (30, 45, 35), start_btn, border_radius=8)
        pygame.draw.rect(surface, (110, 110, 118) if locked else COLOR_GOLD, start_btn, 2, border_radius=8)
        label = t("arena_locked") if locked else t("arena_start_button")
        btn_text = font_oriental_btn.render(label, True, (140, 140, 150) if locked else COLOR_GOLD)
        surface.blit(btn_text, btn_text.get_rect(center=start_btn.center))

    def _draw_multiline_text(self, surface, text, x, y, max_w, font, color, max_lines: int = 3):
        words = text.split()
        lines = []
        cur_line = ""
        for w in words:
            test = cur_line + (" " if cur_line else "") + w
            if font.size(test)[0] <= max_w:
                cur_line = test
            else:
                lines.append(cur_line)
                cur_line = w
        if cur_line:
            lines.append(cur_line)

        for l_idx, line in enumerate(lines[:max_lines]):
            surface.blit(font.render(line, True, color), (x, y + l_idx * 17))
