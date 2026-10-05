"""
Teste da Fase 7 - Entregável 7.1: Introdução de batalha com câmera orbital.

Valida que:
1. A linha do tempo percorre título -> P1 -> P2 -> saída e só então termina.
2. Cada lutador aparece sozinho em seu ato e o título mostra a arena vazia.
3. A câmera varre ~45° por lutador, de forma contínua entre os atos, e volta ao azimute 0 no fim.
4. O ponto de palco fica em chão livre nas duas arenas.
5. A introdução só é disparada ao iniciar uma batalha (não entre rounds) e pode ser pulada.
"""
import math
import os
import re
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
pygame.init()
pygame.font.init()
pygame.display.set_mode((1280, 720))

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.isometric.camera import Camera
from src.ui.match_intro import (
    MatchIntro, ink_reveal, T_TITLE, T_FIGHTER, T_OUTRO, SWEEP_DEG,
    PHASE_TITLE, PHASE_P1, PHASE_P2, PHASE_OUTRO,
)
from src.world.map_data import GameMap, TILE_BRIDGE
from src.world.kyoto_map import KyotoMap


def _started_intro():
    intro = MatchIntro()
    intro.start((11.0, 11.0, 0.5), ((5.0, 6.0), (16.0, 15.0)), ("Kenshi", "Musashi"),
                ("kenshin", "musashi"), ((255, 80, 80), (80, 120, 255)), True)
    return intro


def test_timeline_and_visibility():
    intro = _started_intro()
    seen = []
    dt = 0.05
    while intro.active:
        phase, _ = intro.phase()
        if not seen or seen[-1] != phase:
            seen.append(phase)
        expected = {PHASE_TITLE: (False, False), PHASE_P1: (True, False),
                    PHASE_P2: (False, True), PHASE_OUTRO: (True, True)}[phase]
        assert intro.visible_fighters() == expected, (phase, intro.visible_fighters())
        intro.update(dt)
    assert seen == [PHASE_TITLE, PHASE_P1, PHASE_P2, PHASE_OUTRO], seen
    assert abs(intro.time - (T_TITLE + 2 * T_FIGHTER + T_OUTRO)) < 0.1
    print("  [OK] Linha do tempo título -> P1 -> P2 -> saída e visibilidade dos lutadores.", flush=True)


def test_camera_sweep_is_continuous_and_returns_to_classic():
    intro = _started_intro()
    sweep = math.radians(SWEEP_DEG)

    def state_at(t):
        intro.time = t
        return intro.camera_state()

    assert abs(state_at(0.0)["azimuth"]) < 1e-9
    assert abs(state_at(T_TITLE - 1e-6)["azimuth"] - state_at(T_TITLE + 1e-6)["azimuth"]) < 1e-3
    p1_start, p1_end = state_at(T_TITLE)["azimuth"], state_at(T_TITLE + T_FIGHTER - 1e-6)["azimuth"]
    assert abs(abs(p1_end - p1_start) - 2 * sweep) < 1e-3, "cada lutador cobre ~45°"
    t2 = T_TITLE + T_FIGHTER
    assert abs(state_at(t2 - 1e-6)["azimuth"] - state_at(t2 + 1e-6)["azimuth"]) < 1e-3
    p2_start, p2_end = state_at(t2)["azimuth"], state_at(t2 + T_FIGHTER - 1e-6)["azimuth"]
    assert (p1_end - p1_start) * (p2_end - p2_start) < 0, "P2 orbita no sentido contrário"

    final = state_at(T_TITLE + 2 * T_FIGHTER + T_OUTRO - 1e-6)
    assert abs(final["azimuth"]) < 1e-3 and abs(final["zoom"] - 1.0) < 1e-3 and abs(final["shift_y"]) < 1e-2
    assert abs(final["focus"][0] - intro.mid[0]) < 1e-2 and abs(final["focus"][1] - intro.mid[1]) < 1e-2

    camera = Camera()
    state_at(T_TITLE + 0.5)
    intro.apply_camera(camera)
    assert camera.zoom > 1.0 and camera.screen_y > SCREEN_HEIGHT // 2
    assert camera.ground_z == intro.stage_z == 0.5, "a sombra do lutador desce até o piso do palco (tabuleiro)"
    state_at(0.5)
    intro.apply_camera(camera)
    assert camera.ground_z == 0.0, "sem lutador em cena, o piso volta a z=0"
    print("  [OK] Giro de ~45° por lutador, contínuo entre os atos, com retorno à vista clássica.", flush=True)


def test_stage_point_is_free_ground():
    bamboo, kyoto = GameMap(), KyotoMap()
    x, y, z = bamboo.intro_stage_point()
    assert (x, y) == (11.0, 11.5), "arena de bambu: centro da ponte"
    assert bamboo.tiles[int(x)][int(y)] == TILE_BRIDGE and 0.5 < z < 0.6, "em cima do tabuleiro arqueado"
    assert not bamboo.is_water(x, y)

    x, y, z = kyoto.intro_stage_point()
    assert 9 <= int(x) <= 12 and z == 0.0, "Kyoto: no meio da rua"
    assert abs(y - kyoto.rows / 2.0) < 1e-9
    for building in kyoto.buildings:
        assert not building.check_collision(x, y, 0.9)[0]
    for game_map in (bamboo, kyoto):
        for rock in game_map.rocks:
            assert not rock.check_collision(*game_map.intro_stage_point()[:2], 0.9)[0]
    print("  [OK] Palco da introdução: ponte (bambu) e centro da rua (Kyoto).", flush=True)


def test_skip_jumps_to_outro_and_overlay_renders():
    intro = _started_intro()
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for t in (0.5, 2.0, 3.5, T_TITLE + 0.8, T_TITLE + T_FIGHTER + 1.0, T_TITLE + 2 * T_FIGHTER + 0.3):
        intro.time = t
        surf.fill((60, 90, 60))
        intro.render_overlay(surf)

    intro.time = 1.0
    intro.skip()
    assert intro.phase()[0] == PHASE_OUTRO
    src = pygame.Surface((200, 80), pygame.SRCALPHA)
    pygame.draw.rect(src, (255, 255, 255, 255), (0, 0, 200, 80))
    half = ink_reveal(src, 0.5)
    assert 0 < pygame.surfarray.array_alpha(half).mean() < 255
    print("  [OK] Overlay renderiza em todos os atos; skip() leva à saída; revelação de tinta parcial.", flush=True)


def test_intro_only_triggered_when_a_battle_starts():
    """Somente a escolha de cenário (início de batalha) pede a introdução; rounds seguintes e revanche não."""
    with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as fh:
        src = fh.read()
    assert re.search(r"def start_new_match\(play_intro: bool = False\)", src)
    assert len(re.findall(r"start_new_match\(play_intro=True\)", src)) == 3  # cenário (Versus), demo e início de luta (Arcade)
    arena_block = src.split("arena_choice in arena_ids()")[1].split("arena_select_screen.update")[0]
    assert "start_new_match(play_intro=True)" in arena_block
    arcade_block = src.split("def begin_arcade_fight")[1].split("def ")[0]
    assert "start_new_match(play_intro=True)" in arcade_block
    for helper in ("def request_rematch", "def request_next_round"):
        body = src.split(helper)[1].split("def ")[0]
        assert "play_intro" not in body
    print("  [OK] Introdução só é disparada ao iniciar uma batalha.", flush=True)


def test_round_start_rotates_arena_and_settles_on_classic_view():
    from src.ui.round_intro import RoundIntroScreen, INTRO_DURATION, ROTATION_DEGREES
    ri = RoundIntroScreen()
    assert not hasattr(ri, "apply_rotation"), "a rotação 2D da tela foi substituída pelo azimute da câmera"
    assert abs(ri.get_rotation_angle(INTRO_DURATION) - ROTATION_DEGREES) < 1e-6
    angles = [ri.get_rotation_angle(INTRO_DURATION * (1 - i / 20.0)) for i in range(21)]
    assert all(a >= b - 1e-9 for a, b in zip(angles, angles[1:])), "giro decrescente e suave"
    assert ri.get_rotation_angle(0.01) == 0.0 or ri.get_rotation_angle(0.01) < 1e-6
    assert ri.get_rotation_angle(0.0) == 0.0
    with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as fh:
        src = fh.read()
    assert "apply_rotation" not in src and "camera.set_azimuth(math.radians(round_intro.get_rotation_angle" in src
    print("  [OK] Início de round gira o azimute da arena e termina na vista clássica.", flush=True)


def test_battle_intro_orbital_camera():
    print("=== TESTE 7.1: Introdução de Batalha com Câmera Orbital ===", flush=True)
    test_timeline_and_visibility()
    test_camera_sweep_is_continuous_and_returns_to_classic()
    test_stage_point_is_free_ground()
    test_skip_jumps_to_outro_and_overlay_renders()
    test_intro_only_triggered_when_a_battle_starts()
    test_round_start_rotates_arena_and_settles_on_classic_view()
    print("=== TESTE 7.1 CONCLUÍDO COM SUCESSO ===", flush=True)


if __name__ == "__main__":
    test_battle_intro_orbital_camera()
