"""
Entregável 8.1.2: telas do Arcade em estilo pergaminho Sumi-E: menu de dificuldade, chaves da jornada e resultado final.
Nenhuma regra mora aqui; os dados vêm de `ArcadeRun` (src/arcade/arcade_mode.py).
"""
import pygame

from src.arcade.arcade_mode import DIFFICULTIES, FightKind
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, CHAR_BOSS
from src.effects import parchment as pm
from src.i18n import t
from src.roster import FIGHTER_NAME_KEY
from src.ui.fonts import get_title_font, get_text_font
from src.ui.portraits import get_portrait

DIFF_KEYS = {0: "difficulty_easy", 1: "difficulty_normal", 2: "difficulty_hard"}
KIND_KEYS = {FightKind.DUEL: "arcade_kind_duel", FightKind.MIRROR: "arcade_kind_mirror",
             FightKind.ENDURANCE: "arcade_kind_endurance", FightKind.NINJA_CHALLENGE: "arcade_kind_ninja_challenge",
             FightKind.BOSS: "arcade_kind_boss"}
RED = pm.SEAL_RED


def fighter_name(char_id: str) -> str:
    return t("boss_name") if char_id == CHAR_BOSS else t(FIGHTER_NAME_KEY[char_id])


def arena_name(arena_id: str) -> str:
    for key in (f"arena_{arena_id}_name", f"arena_{arena_id.split('_')[0]}_name"):
        text = t(key)
        if text != key:
            return text
    return arena_id


def format_time(seconds: float) -> str:
    seconds = int(seconds)
    return t("arcade_time", m=seconds // 60, s=seconds % 60)


def navigation(event, ctrl_mgr=None):
    """Traduz teclado e controle em ("move", dx, dy), ("confirm",) ou ("cancel",)."""
    if event.type == pygame.KEYDOWN:
        moves = {pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
                 pygame.K_UP: (0, -1), pygame.K_w: (0, -1), pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1)}
        if event.key in moves:
            return ("move",) + moves[event.key]
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_e, pygame.K_j):
            return ("confirm",)
        if event.key == pygame.K_ESCAPE:
            return ("cancel",)
    elif event.type in (pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION):
        from src.input.controller_manager import get_dpad_motion_from_event
        motion = get_dpad_motion_from_event(event)
        if motion:
            return ("move", motion[0], motion[1])
        if event.type == pygame.JOYBUTTONDOWN:
            if (ctrl_mgr is not None and ctrl_mgr.is_event_menu_confirm(event)) or event.button in (0, 2):
                return ("confirm",)
            if (ctrl_mgr is not None and ctrl_mgr.is_event_menu_cancel(event)) or event.button == 1:
                return ("cancel",)
    return None


def _backdrop(surface: pygame.Surface):
    if not pm.draw_backdrop(surface):
        surface.fill((22, 20, 24))


def _centered(surface, font, text, color, cx, y, max_w=None):
    if "{icon:" in text:
        from src.ui.svg_icon_renderer import render_text_with_icons
        h = font.get_height()
        rect = render_text_with_icons(surface, font, text, cx, y + h // 2, text_color=color, icon_size=max(16, h - 2), shadow=False)
        return rect.height
    img = pm.fit_text(font, text, color, max_w) if max_w else pm.render_ink(font, text, color)
    surface.blit(img, (cx - img.get_width() // 2, y))
    return img.get_height()


def _draw_skull(surface, cx, cy, r, color=(235, 228, 210)):
    pygame.draw.circle(surface, color, (cx, cy - r // 6), r)
    pygame.draw.rect(surface, color, (cx - r // 2, cy + r // 3, r, r // 2), border_radius=3)
    for dx in (-r // 3, r // 3):
        pygame.draw.circle(surface, (30, 24, 24), (cx + dx, cy - r // 6), max(2, r // 4))
    pygame.draw.polygon(surface, (30, 24, 24), [(cx, cy + r // 8), (cx - r // 8, cy + r // 3), (cx + r // 8, cy + r // 3)])


class ArcadeDifficultyScreen:
    """Cartões Fácil/Normal/Difícil; com jornada salva aparece também o cartão "continuar"."""

    def __init__(self):
        self.options: list = []
        self.selected = 0
        self.saved_run: dict | None = None
        self.high_scores: list = []
        self.rects: list[pygame.Rect] = []

    def open(self, default_level: int = 1, saved_run: dict | None = None, high_scores: list | None = None):
        self.saved_run = saved_run
        self.high_scores = high_scores or []
        self.options = (["resume"] if saved_run else []) + [0, 1, 2]
        self.selected = self.options.index(max(0, min(2, default_level)))

    def handle_event(self, event, ctrl_mgr=None):
        """Devolve ("START", nível), "RESUME", "BACK" ou None."""
        if event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    return self._confirm()
        nav = navigation(event, ctrl_mgr)
        if nav is None:
            return None
        if nav[0] == "move":
            step = nav[1] or nav[2]
            if step:
                self.selected = (self.selected + step) % len(self.options)
        elif nav[0] == "confirm":
            return self._confirm()
        elif nav[0] == "cancel":
            return "BACK"
        return None

    def _confirm(self):
        choice = self.options[self.selected]
        return "RESUME" if choice == "resume" else ("START", choice)

    def render(self, surface: pygame.Surface):
        _backdrop(surface)
        cx = SCREEN_WIDTH // 2
        _centered(surface, get_title_font(40), t("arcade_title"), pm.INK, cx, 40)
        _centered(surface, get_text_font(20), t("arcade_subtitle"), pm.INK_SOFT, cx, 92)
        _centered(surface, get_title_font(24), t("arcade_difficulty_title"), pm.INK, cx, 150)

        n = len(self.options)
        card_w, card_h, gap = 280, 250, 36
        x0 = cx - (n * card_w + (n - 1) * gap) // 2
        self.rects = []
        for i, opt in enumerate(self.options):
            rect = pygame.Rect(x0 + i * (card_w + gap), 210, card_w, card_h)
            self.rects.append(rect)
            pm.draw_paper_card(surface, rect, seed=70 + i)
            band = pygame.Rect(rect.x + 18, rect.bottom - 56, rect.w - 36, 34)
            if i == self.selected:
                pm.draw_brush_highlight(surface, band, RED, seed=i + 5, alpha=235)
            band_color = (252, 244, 226) if i == self.selected else pm.INK
            if opt == "resume":
                run = self.saved_run
                _centered(surface, get_title_font(22), t("arcade_resume_run"), pm.INK, rect.centerx, rect.y + 28, card_w - 30)
                portrait = get_portrait(run.get("player_char", ""), size=(84, 84), circular=True)
                if portrait:
                    surface.blit(portrait, (rect.centerx - 42, rect.y + 70))
                name = fighter_name(run["player_char"]) if run.get("player_char") in FIGHTER_NAME_KEY else ""
                sub = t("arcade_resume_run_sub", name=name, n=min(11, run.get("index", 0) + 1), m=11, score=run.get("score", 0))
                _centered(surface, get_text_font(15), sub, pm.INK_SOFT, rect.centerx, rect.y + 168, card_w - 24)
                _centered(surface, get_title_font(20), "▶", band_color, rect.centerx, band.y + 6)
            else:
                for k in range(3):  # lâminas acesas = nível
                    col = RED if k <= opt else pm.INK_SOFT
                    bx = rect.centerx + (k - 1) * 60
                    pygame.draw.polygon(surface, col, [(bx, rect.y + 40), (bx - 14, rect.y + 150), (bx + 14, rect.y + 150)], 0 if k <= opt else 2)
                _centered(surface, get_title_font(24), t(DIFF_KEYS[opt]), band_color, rect.centerx, band.y + 4, band.w - 20)

        lower = pygame.Rect(cx - 430, 478, 860, 170)
        pm.draw_paper_card(surface, lower, seed=81)
        _centered(surface, get_text_font(17), t("arcade_difficulty_hint"), pm.INK, cx, lower.y + 24, lower.w - 60)
        if self.high_scores:
            _centered(surface, get_title_font(18), t("arcade_high_scores"), pm.INK, cx, lower.y + 64)
            for i, e in enumerate(self.high_scores[:3]):
                line = f"{i + 1}. {fighter_name(e['char']) if e.get('char') in FIGHTER_NAME_KEY else '?'}  {e['score']}"
                _centered(surface, get_text_font(16), line, pm.INK, cx, lower.y + 92 + i * 22)
        _centered(surface, get_text_font(16), t("arcade_difficulty_nav"), pm.INK, cx, SCREEN_HEIGHT - 44)


class ArcadeBracketScreen:
    """As 11 lutas em linha, a luta atual e o resumo da jornada; serve também de cartão antes de cada luta."""

    def __init__(self):
        self.run = None
        self.banner: str | None = None  # "cleared" | "defeat" | None
        self.gained = 0
        self.confirm_abandon = False
        self.time = 0.0

    def open(self, run, banner: str | None = None, gained: int = 0):
        self.run, self.banner, self.gained = run, banner, gained
        self.confirm_abandon = False
        self.time = 0.0

    def update(self, dt: float):
        self.time += dt

    def handle_event(self, event, ctrl_mgr=None):
        """Devolve "FIGHT" (iniciar ou continuar), "ABANDON" ou None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._confirm()
        nav = navigation(event, ctrl_mgr)
        if nav is None:
            return None
        if nav[0] == "confirm":
            return self._confirm()
        if nav[0] == "cancel":
            if self.confirm_abandon:
                return "ABANDON"
            self.confirm_abandon = True
        return None

    def _confirm(self):
        if self.confirm_abandon:
            self.confirm_abandon = False
            return None
        return "FIGHT"

    # ------------------------------------------------------------------ desenho
    def _marker(self, surface, rect: pygame.Rect, fight, state: str):
        """state: 'done' | 'current' | 'todo'."""
        pygame.draw.circle(surface, (236, 226, 200), rect.center, rect.w // 2)
        if fight.kind == FightKind.BOSS:
            _draw_skull(surface, rect.centerx, rect.centery, rect.w // 3, (60, 54, 50))
        else:
            opponents = fight.opponents if len(fight.opponents) > 1 else ((fight.opponents[0],) * (2 if fight.kind == FightKind.MIRROR else 1))
            count = len(opponents)
            sizes = {1: rect.w - 8, 2: rect.w // 2 - 2, 4: rect.w // 2 - 4}[count if count in (1, 2, 4) else 1]
            for k, char in enumerate(opponents):
                img = get_portrait(char, size=(sizes, sizes), circular=True)
                if img is None:
                    continue
                if count == 1:
                    pos = (rect.centerx - sizes // 2, rect.centery - sizes // 2)
                elif count == 2:
                    pos = (rect.x + 1 + k * (sizes), rect.centery - sizes // 2)
                else:
                    pos = (rect.x + 2 + (k % 2) * sizes, rect.y + 2 + (k // 2) * sizes)
                surface.blit(img, pos)
        if state == "done":
            pygame.draw.line(surface, RED, (rect.x + 4, rect.bottom - 6), (rect.right - 4, rect.y + 6), 6)
        ring = COLOR_GOLD if state == "current" else (70, 60, 50)
        pygame.draw.circle(surface, ring, rect.center, rect.w // 2, 4 if state == "current" else 2)

    def render(self, surface: pygame.Surface):
        run = self.run
        _backdrop(surface)
        cx = SCREEN_WIDTH // 2
        _centered(surface, get_title_font(34), t("arcade_title"), pm.INK, cx, 26)

        n = len(run.ladder)
        size, gap = 74, 24
        x0 = cx - (n * size + (n - 1) * gap) // 2
        for i, fight in enumerate(run.ladder):
            state = "done" if i < run.index else ("current" if i == run.index else "todo")
            rect = pygame.Rect(x0 + i * (size + gap), 100 + (6 if state == "current" else 0), size, size)
            self._marker(surface, rect, fight, state)
            _centered(surface, get_text_font(14), str(i + 1), pm.INK, rect.centerx, rect.bottom + 6)

        panel = pygame.Rect(cx - 470, 235, 940, 380)
        pm.draw_paper_card(surface, panel, seed=91)
        fight = run.current_fight()
        if self.banner == "defeat":
            _centered(surface, get_title_font(34), t("arcade_defeat"), RED, cx, panel.y + 22)
        elif self.banner == "cleared":
            _centered(surface, get_title_font(30), f"{t('arcade_fight_cleared')}  +{self.gained}", RED, cx, panel.y + 22)
        if fight is not None:
            head = f"{t('arcade_fight_n_of_m', n=run.index + 1, m=n)} — {t(KIND_KEYS[fight.kind])}"
            _centered(surface, get_title_font(26), head, pm.INK, cx, panel.y + 74, panel.w - 60)
            names = ", ".join(fighter_name(o) for o in fight.opponents)
            vs = t("arcade_vs", name=names)
            _centered(surface, get_text_font(22), vs, pm.INK, cx, panel.y + 116, panel.w - 60)
            _centered(surface, get_text_font(18), arena_name(fight.arena_id), pm.INK_SOFT, cx, panel.y + 148)
            if fight.is_challenge:
                _centered(surface, get_text_font(18), t("arcade_round_lives", n=fight.player_round_lives), pm.INK, cx, panel.y + 176)
            if fight.kind == FightKind.MIRROR or (fight.kind == FightKind.NINJA_CHALLENGE and run.player_char in fight.opponents):
                _centered(surface, get_text_font(16), t("arcade_mirror_tag"), RED, cx, panel.y + 200)

        diff = t(DIFF_KEYS[run.difficulty_level])
        arrow = {1: " ↑", -1: " ↓"}.get(run.last_difficulty_change, "")
        stats = [t("arcade_score", n=run.score), t("arcade_continues_used", n=run.continues),
                 t("arcade_points_lost", n=run.points_lost_to_continues), f"{diff}{arrow}", format_time(run.elapsed)]
        for i, line in enumerate(stats):
            _centered(surface, get_text_font(18), line, pm.INK, cx, panel.y + 218 + i * 26, panel.w - 60)
        if run.last_difficulty_change:
            key = "arcade_difficulty_up" if run.last_difficulty_change > 0 else "arcade_difficulty_down"
            _centered(surface, get_text_font(15), t(key), RED, cx + 250, panel.y + 304)

        if self.confirm_abandon:
            hint = t("arcade_abandon_confirm_prompt")
        else:
            hint = t("arcade_continue_prompt") if self.banner == "defeat" else t("arcade_start_fight")
        _centered(surface, get_text_font(18), hint, pm.INK, cx, SCREEN_HEIGHT - 62)


class ArcadeResultScreen:
    """Final da jornada: resumo, posição na tabela de recordes e créditos rolando."""

    def __init__(self):
        self.run = None
        self.rank: int | None = None
        self.high_scores: list = []
        self.time = 0.0

    def open(self, run, rank: int | None, high_scores: list):
        self.run, self.rank, self.high_scores, self.time = run, rank, high_scores, 0.0

    def update(self, dt: float):
        self.time += dt

    def handle_event(self, event, ctrl_mgr=None):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return "DONE"
        nav = navigation(event, ctrl_mgr)
        if nav and nav[0] in ("confirm", "cancel"):
            return "DONE"
        return None

    def render(self, surface: pygame.Surface):
        run = self.run
        _backdrop(surface)
        cx = SCREEN_WIDTH // 2
        _centered(surface, get_title_font(40), t("arcade_final_victory"), (235, 228, 210), cx, 30)

        left = pygame.Rect(60, 100, 560, 500)
        pm.draw_paper_card(surface, left, seed=92)
        lines = [fighter_name(run.player_char), t("arcade_score", n=run.score), format_time(run.elapsed),
                 t("arcade_continues_used", n=run.continues), t("arcade_points_lost", n=run.points_lost_to_continues),
                 t("arcade_difficulty_start_end", a=t(DIFF_KEYS[run.difficulty_start]), b=t(DIFF_KEYS[run.difficulty_level]))]
        portrait = get_portrait(run.player_char, size=(110, 110), circular=True)
        if portrait:
            surface.blit(portrait, (left.centerx - 55, left.y + 24))
        for i, line in enumerate(lines):
            _centered(surface, get_title_font(24) if i == 0 else get_text_font(21), line, pm.INK, left.centerx, left.y + 150 + i * 38, left.w - 40)
        if self.rank:
            _centered(surface, get_title_font(22), t("arcade_new_record", n=self.rank), RED, left.centerx, left.bottom - 60, left.w - 40)

        right = pygame.Rect(660, 100, 560, 500)
        pm.draw_paper_card(surface, right, seed=93)
        _centered(surface, get_title_font(22), t("arcade_high_scores"), pm.INK, right.centerx, right.y + 20)
        for i, e in enumerate(self.high_scores[:10]):
            name = fighter_name(e["char"]) if e.get("char") in FIGHTER_NAME_KEY else "?"
            col = RED if self.rank == i + 1 else pm.INK
            surface.blit(pm.render_ink(get_text_font(18), f"{i + 1:>2}. {name}", col), (right.x + 40, right.y + 64 + i * 30))
            score = pm.render_ink(get_text_font(18), str(e["score"]), col)
            surface.blit(score, (right.right - 40 - score.get_width(), right.y + 64 + i * 30))

        credits = [t("arcade_credits_1"), t("arcade_credits_2"), t("arcade_credits_3")]
        _centered(surface, get_title_font(20), credits[int(self.time / 2.5) % len(credits)], (235, 228, 210), cx, SCREEN_HEIGHT - 80)
        _centered(surface, get_text_font(16), t("arcade_result_hint"), (235, 228, 210), cx, SCREEN_HEIGHT - 28)
