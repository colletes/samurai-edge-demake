"""
Teste do entregável 7.3: animações de apresentação por personagem e integração com a introdução da batalha.
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_character_intro_animations.py
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import numpy as np
import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src.entities import pose_scripts as ps
from src.entities.samurai import STATE_INTRO, STATE_VICTORY, Samurai
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric.camera import Camera
from src.audio.sound_manager import SoundEvent
from src.ui.match_intro import MatchIntro

CHARS = ["kenshin", "musashi", "ninja", "american", "kasumi", "murasaki", "saitou", "rifleman", "okuni", "tomoe", "pirate", "musketeer"]
CHAR_IDS = ["kenshin", "musashi", "ninja", "american", "gray", "purple", "saitou", "rifleman", "kabuki", "archer", "pirate", "musketeer"]
BG = (34, 36, 44)


def render_pose(char, state, timer, az=0.0, zoom=2.0):
    surf = pygame.Surface((640, 480))
    surf.fill(BG)
    cam = Camera(0.0, 0.0)
    cam.set_azimuth(math.radians(az))
    cam.zoom = zoom
    render_voxel_humanoid(surf, cam, 0.0, 0.0, 0.0, 1.0, 1.0, state, timer, True, char, walk_timer=0.0, is_moving=False)
    return pygame.surfarray.array3d(surf).astype(int)


def diff(a, b):
    return int((np.abs(a - b).sum(axis=2) > 0).sum())


def test_scripts_registered_for_all_characters():
    for kind in ("intro", "victory"):
        for ch in CHARS:
            assert ch in ps.SCRIPTS[kind], f"roteiro {kind} ausente para {ch}"
            assert ch in ps.BEATS[kind], f"batidas {kind} ausentes para {ch}"
    for cid, ch in zip(CHAR_IDS, CHARS):
        assert ps.canonical(cid) == ch, (cid, ps.canonical(cid))
    print("  [OK] Os 12 personagens têm roteiro e batidas de apresentação e de vitória.", flush=True)


def test_script_ends_neutral_and_starts_neutral():
    for ch in CHARS:
        for kind in ("intro", "victory"):
            end = ps.sample(ch, kind, 1.0)
            assert end.state == "IDLE" and end.alpha == 1.0, (ch, kind, end)
            start = ps.sample(ch, kind, 0.0)
            assert start.state == "IDLE", (ch, kind, start)
    assert ps.sample("kasumi", "intro", 0.0).alpha == 0.0, "Kasumi surge da fumaça"
    print("  [OK] Todos os roteiros começam e terminam em pose neutra (Kasumi começa invisível).", flush=True)


def test_poses_render_without_errors_and_vary():
    for ch, cid in zip(CHARS, CHAR_IDS):
        idle = render_pose(cid, "IDLE", 0.0)
        frames = []
        for kind in ("intro", "victory"):
            for i in range(21):
                p = i / 20.0
                img = render_pose(cid, STATE_INTRO if kind == "intro" else STATE_VICTORY, p)
                frames.append((kind, p, img))
        for kind in ("intro", "victory"):
            imgs = [im for k, _, im in frames if k == kind]
            distinct = {im.tobytes() for im in imgs}
            assert len(distinct) >= 5, f"{ch} {kind}: só {len(distinct)} quadros distintos"
            end = imgs[-1]
            assert diff(end, idle) < 40, f"{ch} {kind}: pose final difere do idle ({diff(end, idle)} px)"
    print("  [OK] 12 personagens renderizam intro/vitória sem erro, com 5+ quadros distintos e terminando no idle.", flush=True)


def test_poses_render_in_several_azimuths():
    for az in (0.0, 22.5, -22.5, 135.0):
        for cid in CHAR_IDS:
            for kind, state in (("intro", STATE_INTRO), ("victory", STATE_VICTORY)):
                img = render_pose(cid, state, 0.5, az=az)
                assert diff(img, np.full_like(img, BG)) > 100, (cid, kind, az)
    print("  [OK] As poses aparecem nos azimutes 0, ±22.5° e 135°.", flush=True)


def test_beat_player_fires_once():
    for ch in CHARS:
        for kind in ("intro", "victory"):
            expected = len(ps.BEATS[kind][ch])
            player = ps.BeatPlayer(ch, kind)
            fired = []
            for i in range(0, 201):
                fired += player.advance(i / 200.0)
            fired += player.advance(1.0)
            assert len(fired) == expected, (ch, kind, fired)
            for name in fired:
                k, _, arg = name.partition(":")
                assert k in ("sfx", "fx")
                if k == "sfx":
                    assert getattr(SoundEvent, arg.upper(), None) is not None, f"SoundEvent inexistente: {arg}"
            jump = ps.BeatPlayer(ch, kind)
            assert len(jump.advance(1.0)) == expected, "um salto de progresso ainda dispara cada batida uma vez"
            assert jump.advance(1.0) == []
    print("  [OK] Cada batida de som/efeito dispara exatamente uma vez, e todos os SoundEvent existem.", flush=True)


def test_cinematic_states_are_inert():
    import inspect
    # can_move/can_act só aceitam IDLE/WALK: os estados cinematográficos nunca movem nem agem
    src = inspect.getsource(Samurai.can_move) + inspect.getsource(Samurai.can_act)
    assert "STATE_INTRO" not in src and "STATE_VICTORY" not in src
    assert STATE_INTRO != STATE_VICTORY
    print("  [OK] INTRO/VICTORY não habilitam movimento nem ações.", flush=True)


def test_match_intro_progress():
    mi = MatchIntro()
    mi.start((0.0, 0.0), ((-3.0, 0.0), (3.0, 0.0)), ("A", "B"), ("kenshin", "musashi"), ((200, 0, 0), (0, 0, 200)), False)
    seen = {}
    t = 0.0
    while mi.active and t < 30.0:
        mi.update(1 / 60)
        t += 1 / 60
        ph, _ = mi.phase()
        if ph in ("p1", "p2"):
            seen.setdefault(ph, []).append(mi.fighter_progress())
            assert mi.acting_fighter() == (0 if ph == "p1" else 1)
        else:
            assert mi.fighter_progress() == 0.0 and mi.acting_fighter() is None
    for ph in ("p1", "p2"):
        vals = seen[ph]
        assert vals[0] < 0.05 and vals[-1] == 1.0, (ph, vals[0], vals[-1])
        assert all(b >= a for a, b in zip(vals, vals[1:])), "o progresso nunca recua"
    print("  [OK] O progresso da apresentação vai de 0 a 1 em cada ato e não existe fora dos atos.", flush=True)


if __name__ == "__main__":
    test_scripts_registered_for_all_characters()
    test_script_ends_neutral_and_starts_neutral()
    test_poses_render_without_errors_and_vary()
    test_poses_render_in_several_azimuths()
    test_beat_player_fires_once()
    test_cinematic_states_are_inert()
    test_match_intro_progress()
    print("Todos os testes de animações de apresentação passaram.", flush=True)
