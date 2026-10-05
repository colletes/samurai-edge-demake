"""Entregável 7.2: câmera dramática de nocaute (replay orbital em câmera lenta)."""
import math
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()

from src.config import SCREEN_HEIGHT
from src.isometric.camera import Camera
from src.ui.knockout_cam import KnockoutCam, T_ORBIT, T_RETURN, SLOWMO_SCALE


def test_replay_orbits_the_loser_in_slow_motion_and_returns():
    cam = KnockoutCam()
    camera = Camera()
    cam.arm((5.0, 7.0))
    assert cam.pending and not cam.active and cam.time_scale() == 1.0

    cam.begin()
    assert cam.active and not cam.pending
    assert cam.time_scale() == SLOWMO_SCALE

    mid = (11.0, 11.0)
    for _ in range(int(T_ORBIT / 0.016) - 2):
        cam.update(0.016, mid)
        cam.apply_camera(camera, 0.016)
    assert cam.active
    assert camera.azimuth > math.radians(40), "a câmera deve orbitar o derrotado"
    assert camera.zoom > 1.4
    assert math.hypot(camera.wx - 5.0, camera.wy - 7.0) < math.hypot(11.0 - 5.0, 11.0 - 7.0), "foco migra para o derrotado"

    while cam.active:
        cam.update(0.016, mid)
        cam.apply_camera(camera, 0.016)
    KnockoutCam.restore_classic(camera)
    assert camera.azimuth == 0.0 and camera.zoom == 1.0 and camera.screen_y == SCREEN_HEIGHT // 2
    assert cam.time_scale() == 1.0


def test_slow_motion_eases_back_to_normal_speed():
    cam = KnockoutCam()
    cam.arm((0.0, 0.0))
    cam.begin()
    scales = []
    while cam.active:
        cam.update(0.05, (0.0, 0.0))
        scales.append(cam.time_scale())
    assert min(scales) == SLOWMO_SCALE
    assert scales[-1] > 0.9
    peak = scales.index(min(scales))
    assert all(a <= b + 1e-9 for a, b in zip(scales[peak:], scales[peak + 1:])), "a velocidade só aumenta depois do auge"


def test_one_replay_per_round_and_skip_and_reset():
    cam = KnockoutCam()
    cam.arm((1.0, 1.0))
    cam.begin()
    cam.skip()
    assert not cam.active and not cam.pending
    cam.arm((2.0, 2.0))
    assert not cam.pending, "só um replay por round"
    cam.reset()
    cam.arm((2.0, 2.0))
    assert cam.pending


def test_total_duration_covers_orbit_and_return():
    cam = KnockoutCam()
    cam.arm((0.0, 0.0))
    cam.begin()
    elapsed = 0.0
    while cam.active:
        cam.update(0.01, (0.0, 0.0))
        elapsed += 0.01
    assert abs(elapsed - (T_ORBIT + T_RETURN)) < 0.05
    assert 2.0 <= T_ORBIT <= 3.0


if __name__ == "__main__":
    test_replay_orbits_the_loser_in_slow_motion_and_returns()
    test_slow_motion_eases_back_to_normal_speed()
    test_one_replay_per_round_and_skip_and_reset()
    test_total_duration_covers_orbit_and_return()
    print("TODOS OS TESTES DA CÂMERA DE NOCAUTE PASSARAM!")
