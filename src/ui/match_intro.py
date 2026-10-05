"""
Introdução cinematográfica do início de uma batalha (usa o azimute real da câmera, Entregável 6.1).

Roteiro:
  1. TÍTULO  - "DUELO MORTAL" (死闘) caligrafado sobre a arena vazia.
  2. P1      - lutador no centro da arena, câmera orbitando ~45°; nome e retrato no alto.
  3. P2      - o mesmo para o oponente, orbitando no sentido contrário.
  4. SAÍDA   - câmera volta à vista clássica e o jogo segue para o "READY" habitual.

A classe só guarda tempo e fornece o estado de câmera/overlay; quem posiciona os lutadores
e desenha o mundo é o laço principal.
"""
import math

import numpy as np
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD
from src.effects import parchment as pm
from src.i18n import t
from src.ui.camera_moves import smooth, lerp
from src.entities.pose_scripts import INTRO_DURATION
from src.ui.character_select import draw_enso_circle, COLOR_HANKO_RED, COLOR_HANKO_BLUE
from src.ui.font_manager import render_text_fx
from src.ui.fonts import get_title_font, get_text_font
from src.ui.portraits import get_portrait

T_TITLE = 4.6
T_FIGHTER = 2.4
T_OUTRO = 0.8
SWEEP_DEG = 22.5          # ±22.5° => ~45° de giro por lutador
FIGHTER_ZOOM = 2.3
FIGHTER_SHIFT_Y = 90      # desloca o foco para baixo, centralizando o corpo do lutador
LETTERBOX_H = 64
KANJI = "死闘"

PHASE_TITLE, PHASE_P1, PHASE_P2, PHASE_OUTRO = "title", "p1", "p2", "outro"


def _smooth(x: float) -> float:
    return smooth(x)


def _lerp(a: float, b: float, x: float) -> float:
    return lerp(a, b, x)


def ink_reveal(base: pygame.Surface, progress: float, diagonal: bool = False, edge: int = 50) -> pygame.Surface:
    """Revela a superfície com uma varredura de pincel (borda suave); progress 0..1."""
    w, h = base.get_size()
    out = base.copy()
    xs = np.arange(w, dtype=np.float32)[:, None]
    if diagonal:
        ys = np.arange(h, dtype=np.float32)[None, :]
        coord = xs + ys * 0.6
        span = w + h * 0.6
    else:
        coord = xs
        span = w
    pos = progress * (span + edge)
    mask = np.clip((pos - coord) / edge, 0.0, 1.0)
    alpha = pygame.surfarray.pixels_alpha(out)
    alpha[:] = (alpha * mask).astype(np.uint8)
    del alpha
    return out


def build_banner_shade() -> pygame.Surface:
    h = 190
    shade = pygame.Surface((SCREEN_WIDTH, h), pygame.SRCALPHA)
    for y in range(h):
        pygame.draw.line(shade, (6, 6, 8, int(170 * (1 - y / h) ** 1.3)), (0, y), (SCREEN_WIDTH, y))
    return shade


def draw_fighter_banner(surface: pygame.Surface, cache: dict, name: str, color, char_id: str, ring, label: str,
                        time: float, enter: float, leave: float = 1.0):
    """Faixa com retrato circular (anel ensō), rótulo e nome do lutador; usada na introdução e na vitória.
    `enter` (0..1) desliza o banner para dentro e `leave` (0..1) o apaga; `cache` guarda as superfícies de texto."""
    def cached(key, builder):
        if key not in cache:
            cache[key] = builder()
        return cache[key]

    name_font = get_title_font(46)
    label_font = get_text_font(22)
    fx = dict(outline=True, outline_color=(8, 6, 6), outline_width=2, shadow=True, shadow_offset=(2, 2))
    light = tuple(min(255, int(c * 0.55 + 140)) for c in color)
    name_surf = cached(("name", name), lambda: render_text_fx(name_font, name, light, **fx))
    label_surf = cached(("label", label), lambda: render_text_fx(label_font, label, (235, 225, 205), **fx))

    radius = 58
    gap = 22
    text_w = max(name_surf.get_width(), label_surf.get_width())
    total_w = radius * 2 + gap + text_w
    alpha = int(255 * enter * leave)
    left = (SCREEN_WIDTH - total_w) // 2 - int((1.0 - enter) * 60)
    cy = LETTERBOX_H + 18 + radius

    shade = cached(("shade",), build_banner_shade)
    shade.set_alpha(alpha)
    surface.blit(shade, (0, LETTERBOX_H))

    layer = pygame.Surface((total_w + 20, radius * 2 + 20), pygame.SRCALPHA)
    pcx, pcy = radius + 10, radius + 10
    draw_enso_circle(layer, pcx, pcy, radius, ring, time)
    portrait = get_portrait(char_id, size=(radius * 2 - 6, radius * 2 - 6), circular=True)
    if portrait is not None:
        layer.blit(portrait, (pcx - portrait.get_width() // 2, pcy - portrait.get_height() // 2))
    tx = radius * 2 + 10 + gap
    layer.blit(label_surf, (tx, pcy - radius + 10))
    layer.blit(name_surf, (tx, pcy - 6))
    layer.set_alpha(alpha)
    surface.blit(layer, (left - 10, cy - radius - 10))


class MatchIntro:
    def __init__(self):
        self.active = False
        self.time = 0.0
        self._cache: dict = {}
        self.stage = (0.0, 0.0)
        self.stage_z = 0.0
        self.spawns = ((0.0, 0.0), (0.0, 0.0))
        self.mid = (0.0, 0.0)
        self.names = ("", "")
        self.char_ids = ("", "")
        self.colors = ((255, 255, 255), (255, 255, 255))
        self.vs_ai = True

    # ------------------------------------------------------------------ controle
    def start(self, stage: tuple[float, ...], spawns, names, char_ids, colors, vs_ai: bool):
        self.active = True
        self.time = 0.0
        self.stage = (stage[0], stage[1])
        self.stage_z = stage[2] if len(stage) > 2 else 0.0
        self.spawns = tuple(spawns)
        self.mid = ((spawns[0][0] + spawns[1][0]) / 2.0, (spawns[0][1] + spawns[1][1]) / 2.0)
        self.names = (names[0].upper(), names[1].upper())
        self.char_ids = tuple(char_ids)
        self.colors = tuple(colors)
        self.vs_ai = vs_ai
        self._cache.clear()

    def update(self, dt: float):
        if not self.active:
            return
        self.time += dt
        if self.time >= T_TITLE + 2 * T_FIGHTER + T_OUTRO:
            self.active = False

    def skip(self):
        """Pula direto para o retorno à vista clássica."""
        if self.active and self.time < T_TITLE + 2 * T_FIGHTER:
            self.time = T_TITLE + 2 * T_FIGHTER

    def phase(self) -> tuple[str, float]:
        """(fase, tempo decorrido dentro da fase)."""
        t0 = self.time
        p1_start = T_TITLE
        p2_start = T_TITLE + T_FIGHTER
        outro_start = T_TITLE + 2 * T_FIGHTER
        if t0 < p1_start:
            return PHASE_TITLE, t0
        if t0 < p2_start:
            return PHASE_P1, t0 - p1_start
        if t0 < outro_start:
            return PHASE_P2, t0 - p2_start
        return PHASE_OUTRO, t0 - outro_start

    def visible_fighters(self) -> tuple[bool, bool]:
        phase, _ = self.phase()
        return {PHASE_TITLE: (False, False), PHASE_P1: (True, False),
                PHASE_P2: (False, True), PHASE_OUTRO: (True, True)}[phase]

    def acting_fighter(self) -> int | None:
        """Índice (0 = P1, 1 = P2) do lutador que faz a animação de apresentação neste ato; None fora dos atos."""
        phase, _ = self.phase()
        return {PHASE_P1: 0, PHASE_P2: 1}.get(phase)

    def fighter_progress(self) -> float:
        """Progresso 0..1 da animação de apresentação do ato atual (sobra uma pose final parada até o fim do ato)."""
        phase, lt = self.phase()
        if phase not in (PHASE_P1, PHASE_P2):
            return 0.0
        return max(0.0, min(1.0, lt / INTRO_DURATION))

    # ------------------------------------------------------------------ câmera
    def camera_state(self) -> dict:
        """Foco (wx, wy), azimute (rad), zoom e deslocamento vertical da câmera no instante atual."""
        phase, lt = self.phase()
        sweep = math.radians(SWEEP_DEG)
        title_zoom_end = 1.12
        if phase == PHASE_TITLE:
            k = _smooth(lt / T_TITLE)
            return dict(focus=self.stage, azimuth=-sweep * k, zoom=_lerp(1.0, title_zoom_end, k), shift_y=0.0)
        if phase in (PHASE_P1, PHASE_P2):
            k = _smooth(lt / T_FIGHTER)
            az = _lerp(-sweep, sweep, k) if phase == PHASE_P1 else _lerp(sweep, -sweep, k)
            zin = _smooth(lt / 0.6) if phase == PHASE_P1 else 1.0
            return dict(focus=self.stage, azimuth=az,
                        zoom=_lerp(title_zoom_end, FIGHTER_ZOOM, zin), shift_y=FIGHTER_SHIFT_Y * zin)
        k = _smooth(lt / T_OUTRO)
        return dict(focus=(_lerp(self.stage[0], self.mid[0], k), _lerp(self.stage[1], self.mid[1], k)),
                    azimuth=_lerp(-sweep, 0.0, k), zoom=_lerp(FIGHTER_ZOOM, 1.0, k),
                    shift_y=FIGHTER_SHIFT_Y * (1.0 - k))

    def apply_camera(self, camera):
        st = self.camera_state()
        camera.wx, camera.wy = st["focus"]
        camera.set_azimuth(st["azimuth"])
        camera.zoom = st["zoom"]
        camera.screen_y = SCREEN_HEIGHT // 2 + int(st["shift_y"])
        on_stage = self.phase()[0] in (PHASE_P1, PHASE_P2)
        camera.ground_z = self.stage_z if on_stage else 0.0

    # ------------------------------------------------------------------ overlay
    def _letterbox_amount(self) -> float:
        phase, lt = self.phase()
        if phase == PHASE_TITLE:
            return _smooth(lt / 0.5)
        if phase == PHASE_OUTRO:
            return 1.0 - _smooth(lt / T_OUTRO)
        return 1.0

    def _fade_from_black(self) -> float:
        """0..1 de opacidade do preto: abertura lenta e cortes rápidos entre os atos."""
        phase, lt = self.phase()
        if phase == PHASE_TITLE:
            return 1.0 - _smooth(lt / 0.8)
        if phase in (PHASE_P1, PHASE_P2):
            return 1.0 - _smooth(lt / 0.3)
        return 0.0

    def render_overlay(self, surface: pygame.Surface):
        phase, lt = self.phase()

        bar = int(LETTERBOX_H * self._letterbox_amount())
        if bar > 0:
            pygame.draw.rect(surface, (4, 4, 6), (0, 0, SCREEN_WIDTH, bar))
            pygame.draw.rect(surface, (4, 4, 6), (0, SCREEN_HEIGHT - bar, SCREEN_WIDTH, bar))

        if phase == PHASE_TITLE:
            self._render_title(surface, lt)
        elif phase in (PHASE_P1, PHASE_P2):
            self._render_fighter_banner(surface, 0 if phase == PHASE_P1 else 1, lt)

        fade = self._fade_from_black()
        if fade > 0.01:
            black = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            black.set_alpha(int(255 * fade))
            surface.blit(black, (0, 0))

    def _cached(self, key, builder):
        if key not in self._cache:
            self._cache[key] = builder()
        return self._cache[key]

    def _render_title(self, surface: pygame.Surface, lt: float):
        fx = dict(outline=True, outline_color=(8, 6, 6), outline_width=3, shadow=True, shadow_offset=(3, 3))
        kanji_font = get_text_font(200)
        text = t("match_intro_title")
        title_font = get_title_font(60)

        layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        cx = SCREEN_WIDTH // 2

        # Kanji 死 e 闘, um após o outro, com varredura diagonal de pincel
        for i, ch in enumerate(KANJI):
            base = self._cached(("kanji", i), lambda ch=ch: render_text_fx(
                kanji_font, ch, (240, 232, 214), glow=True, glow_color=(190, 30, 30), glow_width=6, **fx))
            start = 0.35 + i * 0.75
            p = _smooth((lt - start) / 0.8)
            if p > 0:
                img = ink_reveal(base, p, diagonal=True, edge=90)
                x = cx - base.get_width() - 10 if i == 0 else cx + 10
                layer.blit(img, (x, 120))

        # Pincelada vermelha e texto em Shojumaru, revelados da esquerda para a direita
        title_base = self._cached(("title", text), lambda: render_text_fx(title_font, text, COLOR_GOLD, **fx))
        stroke = self._cached(("stroke",), lambda: pm.make_brush_stroke(620, 40, pm.SEAL_RED, seed=17))
        p_stroke = _smooth((lt - 1.75) / 0.6)
        if p_stroke > 0:
            layer.blit(ink_reveal(stroke, p_stroke, edge=80), (cx - 310, 470))
        p_text = _smooth((lt - 1.95) / 1.0)
        if p_text > 0:
            layer.blit(ink_reveal(title_base, p_text, edge=70), (cx - title_base.get_width() // 2, 410))

        fade_out = 1.0 - _smooth((lt - (T_TITLE - 0.5)) / 0.5)
        layer.set_alpha(int(255 * fade_out))
        surface.blit(layer, (0, 0))

    def _render_fighter_banner(self, surface: pygame.Surface, idx: int, lt: float):
        label = t("match_intro_p1") if idx == 0 else t("match_intro_ai" if self.vs_ai else "match_intro_p2")
        enter = _smooth(lt / 0.5)
        leave = 1.0 - _smooth((lt - (T_FIGHTER - 0.35)) / 0.35)
        draw_fighter_banner(surface, self._cache, self.names[idx], self.colors[idx], self.char_ids[idx],
                            COLOR_HANKO_RED if idx == 0 else COLOR_HANKO_BLUE, label, self.time, enter, leave)

    @staticmethod
    def _build_shade() -> pygame.Surface:
        return build_banner_shade()
