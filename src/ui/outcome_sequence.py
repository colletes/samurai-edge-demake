"""
Entregáveis 7.2 e 7.4: sequência de fim de round (máquina de estados única).

  ARMED (espera o congelamento Kurosawa) -> KNOCKOUT (órbita lenta no derrotado, 7.2)
  -> VICTORY (pose do vencedor com órbita de ~45°, 7.4) -> DONE (banner do round ou tela da partida)

Empate não passa por aqui. Um round que não fecha a partida usa a vitória curta; o que fecha usa a completa.
A classe só guarda tempo e estado; o laço principal aplica câmera, pose e overlay.
"""
import math

import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.pose_scripts import VICTORY_FULL, VICTORY_SHORT, VICTORY_RETURN
from src.i18n import t
from src.ui.camera_moves import smooth, lerp
from src.ui.knockout_cam import KnockoutCam
from src.ui.match_intro import FIGHTER_ZOOM, FIGHTER_SHIFT_Y, LETTERBOX_H, draw_fighter_banner
from src.ui.character_select import COLOR_HANKO_RED, COLOR_HANKO_BLUE

PHASE_IDLE, PHASE_ARMED, PHASE_KNOCKOUT, PHASE_VICTORY, PHASE_DONE = "idle", "armed", "knockout", "victory", "done"
VICTORY_ORBIT_DEG = 45.0
SHORT_ZOOM = 1.6
SHORT_SHIFT_Y = 55


class OutcomeSequence:
    def __init__(self):
        self.knockout = KnockoutCam()
        self.deferred_result = None  # dados da tela de resultados, exibidos só depois da sequência
        self._banner_cache: dict = {}
        self.reset()

    def reset(self):
        self.knockout.reset()
        self.phase = PHASE_IDLE
        self.used = False
        self.winner_idx = None
        self.winner_pos = (0.0, 0.0)
        self.match_end = False
        self.victory_time = 0.0
        self.mid = (0.0, 0.0)
        self.deferred_result = None

    # ------------------------------------------------------------------ estado
    @property
    def pending(self) -> bool:
        return self.phase == PHASE_ARMED

    @property
    def active(self) -> bool:
        return self.phase in (PHASE_KNOCKOUT, PHASE_VICTORY)

    @property
    def pose_duration(self) -> float:
        return VICTORY_FULL if self.match_end else VICTORY_SHORT

    @property
    def victory_total(self) -> float:
        return self.pose_duration + VICTORY_RETURN

    def arm(self, loser_pos, winner_idx: int | None = None, winner_pos=None, match_end: bool = False):
        """Marca o fim do round (uma vez por round); `winner_idx` None = sem vitória (só o replay)."""
        if self.used:
            return
        self.used = True
        self.phase = PHASE_ARMED
        self.winner_idx = winner_idx
        self.winner_pos = tuple(winner_pos) if winner_pos is not None else (0.0, 0.0)
        self.match_end = match_end
        self.knockout.arm(loser_pos)

    def begin(self):
        if self.phase == PHASE_ARMED:
            self.knockout.begin()
            self.phase = PHASE_KNOCKOUT

    def skip(self):
        self.knockout.skip()
        self.phase = PHASE_DONE

    def update(self, dt: float, mid, winner_pos=None, winner_alive: bool = True):
        """`dt` em tempo real (sem a câmera lenta)."""
        self.mid = tuple(mid)
        if winner_pos is not None:
            self.winner_pos = tuple(winner_pos)
        if self.phase == PHASE_KNOCKOUT:
            self.knockout.update(dt, mid)
            if not self.knockout.active:
                self.phase = PHASE_VICTORY if (self.winner_idx is not None and winner_alive) else PHASE_DONE
                self.victory_time = 0.0
        elif self.phase == PHASE_VICTORY:
            self.victory_time += dt
            if not winner_alive or self.victory_time >= self.victory_total:
                self.phase = PHASE_DONE

    def time_scale(self) -> float:
        return self.knockout.time_scale() if self.phase == PHASE_KNOCKOUT else 1.0

    def victory_progress(self) -> float | None:
        """Progresso 0..1 da pose do vencedor; None fora da fase de vitória."""
        if self.phase != PHASE_VICTORY:
            return None
        return min(1.0, self.victory_time / self.pose_duration)

    # ------------------------------------------------------------------ câmera
    def victory_camera_state(self) -> dict:
        """Parte da vista clássica (onde o replay termina), gira ~45° em volta do vencedor e volta."""
        end_az = math.radians(VICTORY_ORBIT_DEG) * (1.0 if self.winner_idx == 1 else -1.0)
        zoom = FIGHTER_ZOOM if self.match_end else SHORT_ZOOM
        shift = FIGHTER_SHIFT_Y if self.match_end else SHORT_SHIFT_Y
        t_now, d = self.victory_time, self.pose_duration
        if t_now <= d:
            k = smooth(t_now / d)
            zin = smooth(t_now / 0.8)
            return dict(focus=(lerp(self.mid[0], self.winner_pos[0], zin), lerp(self.mid[1], self.winner_pos[1], zin)),
                        azimuth=end_az * k, zoom=lerp(1.0, zoom, zin), shift_y=shift * zin)
        k = smooth((t_now - d) / VICTORY_RETURN)
        return dict(focus=(lerp(self.winner_pos[0], self.mid[0], k), lerp(self.winner_pos[1], self.mid[1], k)),
                    azimuth=lerp(end_az, 0.0, k), zoom=lerp(zoom, 1.0, k), shift_y=shift * (1.0 - k))

    def apply_camera(self, camera, dt: float):
        if self.phase == PHASE_KNOCKOUT:
            self.knockout.apply_camera(camera, dt)
        elif self.phase == PHASE_VICTORY:
            st = self.victory_camera_state()
            camera.update(st["focus"][0], st["focus"][1], dt)
            camera.set_azimuth(st["azimuth"])
            camera.zoom = st["zoom"]
            camera.screen_y = SCREEN_HEIGHT // 2 + int(st["shift_y"])

    @staticmethod
    def restore_classic(camera):
        KnockoutCam.restore_classic(camera)

    # ------------------------------------------------------------------ overlay
    def letterbox_amount(self) -> float:
        if self.phase != PHASE_VICTORY:
            return 0.0
        t_now, d = self.victory_time, self.pose_duration
        if t_now <= d:
            return smooth(t_now / 0.4)
        return 1.0 - smooth((t_now - d) / VICTORY_RETURN)

    def render_overlay(self, surface: pygame.Surface, name: str, color, char_id: str):
        """Letterbox e banner do vencedor (nome e retrato com anel ensō) durante a pose de vitória."""
        if self.phase != PHASE_VICTORY:
            return
        bar = int(LETTERBOX_H * self.letterbox_amount())
        if bar > 0:
            pygame.draw.rect(surface, (4, 4, 6), (0, 0, SCREEN_WIDTH, bar))
            pygame.draw.rect(surface, (4, 4, 6), (0, SCREEN_HEIGHT - bar, SCREEN_WIDTH, bar))
        d = self.pose_duration
        enter = smooth(self.victory_time / 0.5)
        leave = 1.0 - smooth((self.victory_time - (d - 0.2)) / 0.5)
        label = t("match_winner_banner_label") if self.match_end else t("winner_banner_label")
        ring = COLOR_HANKO_RED if self.winner_idx == 0 else COLOR_HANKO_BLUE
        draw_fighter_banner(surface, self._banner_cache, name.upper(), color, char_id, ring, label, self.victory_time, enter, leave)
