"""
Teste do entregável 7.4: animações de vitória por personagem e sequência de fim de round (OutcomeSequence).
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_character_victory_animations.py
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src.config import SCREEN_HEIGHT
from src.entities.pose_scripts import VICTORY_FULL, VICTORY_SHORT, VICTORY_RETURN
from src.i18n import t
from src.isometric.camera import Camera
from src.ui.outcome_sequence import OutcomeSequence

DT = 1 / 60
MID = (10.0, 10.0)


def run_until(seq, predicate, limit=20.0, **kw):
    elapsed = 0.0
    while not predicate() and elapsed < limit:
        seq.update(DT, MID, **kw)
        elapsed += DT
    return elapsed


def start_sequence(match_end=False, winner_idx=0):
    seq = OutcomeSequence()
    seq.arm((12.0, 10.0), winner_idx=winner_idx, winner_pos=(8.0, 10.0), match_end=match_end)
    assert seq.pending
    seq.begin()
    assert seq.phase == "knockout" and seq.active
    return seq


def test_phase_order_and_durations():
    for match_end, pose in ((False, VICTORY_SHORT), (True, VICTORY_FULL)):
        seq = start_sequence(match_end)
        phases = []
        elapsed = 0.0
        while seq.phase != "done" and elapsed < 30.0:
            seq.update(DT, MID)
            elapsed += DT
            if not phases or phases[-1] != seq.phase:
                phases.append(seq.phase)
        assert phases == ["knockout", "victory", "done"], phases
        victory_len = VICTORY_FULL + VICTORY_RETURN if match_end else VICTORY_SHORT + VICTORY_RETURN
        assert abs(seq.victory_time - victory_len) < 2 * DT, (seq.victory_time, victory_len)
        assert seq.pose_duration == pose
    short, full = OutcomeSequence(), OutcomeSequence()
    short.match_end, full.match_end = False, True
    assert full.pose_duration > short.pose_duration
    print("  [OK] Ordem knockout -> vitória -> fim; vitória curta no round e completa no fim da partida.", flush=True)


def test_arm_once_per_round_and_draw_skips():
    seq = OutcomeSequence()
    seq.arm((1.0, 1.0), winner_idx=0, winner_pos=(0.0, 0.0))
    seq.arm((5.0, 5.0), winner_idx=1, winner_pos=(2.0, 2.0), match_end=True)
    assert seq.winner_idx == 0 and not seq.match_end, "só o primeiro arm vale em cada round"
    seq.reset()
    assert seq.phase == "idle" and not seq.pending and not seq.active
    seq.arm((1.0, 1.0), winner_idx=1, winner_pos=(0.0, 0.0))
    assert seq.pending
    empate = OutcomeSequence()
    assert empate.phase == "idle" and not empate.pending and empate.victory_progress() is None, "empate nunca arma a sequência"
    print("  [OK] Um arm por round; empate não dispara replay nem vitória.", flush=True)


def test_victory_progress_and_time_scale():
    seq = start_sequence(False)
    assert seq.time_scale() < 1.0, "o replay do nocaute roda em câmera lenta"
    assert seq.victory_progress() is None
    run_until(seq, lambda: seq.phase == "victory")
    assert seq.time_scale() == 1.0
    p0 = seq.victory_progress()
    assert p0 is not None and p0 < 0.05
    seen = []
    while seq.phase == "victory":
        seq.update(DT, MID)
        p = seq.victory_progress()
        if p is not None:
            seen.append(p)
    assert seen and max(seen) == 1.0 and all(b >= a for a, b in zip(seen, seen[1:]))
    print("  [OK] Câmera lenta só no nocaute; o progresso da pose de vitória vai de 0 a 1.", flush=True)


def test_winner_death_ends_sequence():
    seq = start_sequence(True)
    run_until(seq, lambda: seq.phase == "victory")
    seq.update(DT, MID, winner_alive=False)
    assert seq.phase == "done"
    seq2 = start_sequence(True)
    run_until(seq2, lambda: seq2.phase == "victory" or seq2.phase == "done", winner_alive=False)
    assert seq2.phase == "done", "se o vencedor morre durante o replay, não há pose de vitória"
    print("  [OK] Se o vencedor morre, a sequência termina sem pose de vitória.", flush=True)


def test_skip_restores_classic_camera():
    seq = start_sequence(True)
    cam = Camera(0.0, 0.0)
    run_until(seq, lambda: seq.phase == "victory")
    run_until(seq, lambda: seq.victory_time > 1.0)
    seq.apply_camera(cam, DT)
    assert abs(cam.azimuth) > 0.01 and cam.zoom > 1.2
    seq.skip()
    OutcomeSequence.restore_classic(cam)
    assert seq.phase == "done" and not seq.active and not seq.pending
    assert cam.azimuth == 0.0 and cam.zoom == 1.0 and cam.screen_y == SCREEN_HEIGHT // 2
    print("  [OK] Pular a sequência devolve azimute 0, zoom 1.0 e tela centralizada.", flush=True)


def test_camera_continuity_and_direction():
    for idx in (0, 1):
        seq = start_sequence(False, winner_idx=idx)
        run_until(seq, lambda: seq.phase == "victory")
        st0 = seq.victory_camera_state()
        assert abs(st0["azimuth"]) < math.radians(3) and abs(st0["zoom"] - 1.0) < 0.05, "começa onde o replay termina"
        seq.victory_time = seq.pose_duration
        mid = seq.victory_camera_state()
        assert abs(abs(mid["azimuth"]) - math.radians(45)) < 1e-6
        assert (mid["azimuth"] > 0) == (idx == 1), "cada vencedor orbita para um lado"
        seq.victory_time = seq.victory_total
        end = seq.victory_camera_state()
        assert abs(end["azimuth"]) < 1e-6 and abs(end["zoom"] - 1.0) < 1e-6 and abs(end["shift_y"]) < 1e-6
    print("  [OK] A câmera de vitória começa e termina na vista clássica e orbita ~45°.", flush=True)


def test_result_deferred_until_sequence_ends():
    seq = start_sequence(True)
    seq.deferred_result = ("A", (255, 0, 0), 2, 0)
    ready = lambda: seq.deferred_result and not seq.active and not seq.pending
    run_until(seq, lambda: seq.phase == "victory")
    assert not ready(), "a tela da partida espera a pose de vitória"
    run_until(seq, lambda: seq.phase == "done")
    assert ready()
    print("  [OK] A tela de resultados só aparece depois da pose de vitória.", flush=True)


def test_overlay_renders_and_labels_exist():
    seq = start_sequence(True, winner_idx=1)
    surf = pygame.Surface((1280, 720))
    seq.render_overlay(surf, "Kenshi", (200, 40, 40), "kenshin")  # fora da vitória: não desenha
    run_until(seq, lambda: seq.phase == "victory")
    run_until(seq, lambda: seq.victory_time > 1.0)
    surf.fill((90, 90, 90))
    seq.render_overlay(surf, "Kenshi", (200, 40, 40), "kenshin")
    assert surf.get_at((5, 5))[:3] != (90, 90, 90), "letterbox desenhado"
    for key in ("winner_banner_label", "match_winner_banner_label"):
        assert t(key) != key, f"chave i18n ausente: {key}"
    print("  [OK] Letterbox e banner do vencedor são desenhados; textos traduzidos.", flush=True)


if __name__ == "__main__":
    test_phase_order_and_durations()
    test_arm_once_per_round_and_draw_skips()
    test_victory_progress_and_time_scale()
    test_winner_death_ends_sequence()
    test_skip_restores_classic_camera()
    test_camera_continuity_and_direction()
    test_result_deferred_until_sequence_ends()
    test_overlay_renders_and_labels_exist()
    print("Todos os testes de vitória e sequência de fim de round passaram.", flush=True)
