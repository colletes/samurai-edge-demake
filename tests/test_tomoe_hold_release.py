import os
import sys
import math
import pygame

# Set dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
pygame.init()

from src.entities.kyudo_archer import KyudoArcher
from src.entities.projectile import RopeArrowProjectile
from src.world.map_data import GameMap, Rock
from src.world.kyoto_map import KyotoMap

def test_tomoe_hold_and_release():
    print("Iniciando teste de Tomoe Hold and Release...")
    game_map = GameMap()
    game_map.bamboos.clear()
    game_map.rocks.clear()
    tomoe = KyudoArcher(wx=10.0, wy=10.0)
    projectiles = []
    particles = []

    # 1. Início de carga
    tomoe.start_rope_arrow_charge(14.0, 10.0, game_map)
    assert tomoe.is_charging_rope, "Tomoe deveria estar carregando a flecha de corda"
    assert tomoe.rope_charge_time == 0.0, "Tempo de carga inicial deve ser 0"
    assert tomoe.facing_x > 0.9, "Direção de Tomoe deve estar voltada para o alvo"
    # Alcance mínimo inicial
    initial_target_dist = tomoe.target_rope_x - tomoe.wx
    assert abs(initial_target_dist - tomoe.rope_min_range) < 0.35, f"Alcance inicial ({initial_target_dist}) deve ser ~rope_min_range (3.0)"

    # 2. Atualização de carga contínua (Hold)
    dt = 0.25
    tomoe.update_rope_charge(dt, 20.0, 10.0, game_map)
    assert tomoe.rope_charge_time == 0.25
    assert tomoe.target_rope_x > 10.0 + tomoe.rope_min_range, "Alcance deve aumentar com o tempo de carga"

    # Carrega até o tempo máximo
    tomoe.update_rope_charge(1.0, 20.0, 10.0, game_map)
    assert tomoe.rope_charge_time >= tomoe.rope_charge_duration
    # Deve alcançar o limite ou rope_max_range
    expected_x = min(game_map.cols - 1.0, 10.0 + tomoe.rope_max_range)
    assert abs(tomoe.target_rope_x - expected_x) < 0.35, f"Alvo carregado {tomoe.target_rope_x} deve ser próximo a {expected_x}"

    # 3. Soltar (Release)
    target_x = tomoe.target_rope_x
    target_y = tomoe.target_rope_y
    tomoe.release_rope_arrow(projectiles, particles, game_map)
    assert not tomoe.is_charging_rope, "Não deve mais estar carregando após o release"
    assert len(projectiles) == 1, "Deveria ter gerado 1 RopeArrowProjectile"
    rope = projectiles[0]
    assert isinstance(rope, RopeArrowProjectile)
    assert rope.state == "LATCHED_PULLING", "A flecha deve nascer cravada (start_latched)"
    assert abs(rope.wx - target_x) < 0.01 and abs(rope.wy - target_y) < 0.01, "Flecha deve cravar na posição mirada"

    # 4. Deslocamento de Tomoe sendo puxada até o destino
    for _ in range(60):
        if not rope.is_active:
            break
        rope.update(0.016, game_map, particles)

    assert abs(tomoe.wx - target_x) < 0.86, f"Tomoe ({tomoe.wx}, {tomoe.wy}) deve ter sido puxada até o destino ({target_x}, {target_y})"
    print("  -> Hold and Release com zip mobility OK!")


def test_tomoe_boundary_clamping():
    print("Iniciando teste de contenção estrita aos limites do mapa...")
    game_map = GameMap()
    min_x, max_x = 1.0, game_map.cols - 1.0
    min_y, max_y = 1.0, game_map.rows - 1.0

    # Teste 1: Mirar para além do canto Noroeste (-100, -100)
    tomoe = KyudoArcher(wx=2.5, wy=2.5)
    projectiles = []
    tomoe.start_rope_arrow_charge(-50.0, -50.0, game_map)
    tomoe.update_rope_charge(1.0, -50.0, -50.0, game_map)

    assert tomoe.target_rope_x >= min_x, f"Target X ({tomoe.target_rope_x}) deve ser >= {min_x}"
    assert tomoe.target_rope_y >= min_y, f"Target Y ({tomoe.target_rope_y}) deve ser >= {min_y}"
    assert tomoe.target_rope_x <= max_x and tomoe.target_rope_y <= max_y

    tomoe.release_rope_arrow(projectiles, [], game_map)
    rope = projectiles[0]
    for _ in range(60):
        if not rope.is_active:
            break
        rope.update(0.016, game_map)

    assert min_x <= tomoe.wx <= max_x, f"Tomoe X ({tomoe.wx}) ultrapassou limites [{min_x}, {max_x}]"
    assert min_y <= tomoe.wy <= max_y, f"Tomoe Y ({tomoe.wy}) ultrapassou limites [{min_y}, {max_y}]"

    # Teste 2: Mirar para além do canto Sudeste (+999, +999)
    tomoe2 = KyudoArcher(wx=18.0, wy=18.0)
    projectiles2 = []
    tomoe2.start_rope_arrow_charge(999.0, 999.0, game_map)
    tomoe2.update_rope_charge(1.0, 999.0, 999.0, game_map)

    assert tomoe2.target_rope_x <= max_x, f"Target X ({tomoe2.target_rope_x}) deve ser <= {max_x}"
    assert tomoe2.target_rope_y <= max_y, f"Target Y ({tomoe2.target_rope_y}) deve ser <= {max_y}"

    tomoe2.release_rope_arrow(projectiles2, [], game_map)
    rope2 = projectiles2[0]
    for _ in range(60):
        if not rope2.is_active:
            break
        rope2.update(0.016, game_map)

    assert min_x <= tomoe2.wx <= max_x, f"Tomoe2 X ({tomoe2.wx}) ultrapassou limites [{min_x}, {max_x}]"
    assert min_y <= tomoe2.wy <= max_y, f"Tomoe2 Y ({tomoe2.wy}) ultrapassou limites [{min_y}, {max_y}]"

    # Teste 3: Na Arena KyotoMap
    kyoto_map = KyotoMap()
    k_min_x, k_max_x = 1.0, kyoto_map.cols - 1.0
    k_min_y, k_max_y = 1.0, kyoto_map.rows - 1.0
    tomoe3 = KyudoArcher(wx=20.0, wy=20.0)
    projectiles3 = []
    tomoe3.start_rope_arrow_charge(100.0, 100.0, kyoto_map)
    tomoe3.update_rope_charge(1.0, 100.0, 100.0, kyoto_map)

    assert tomoe3.target_rope_x <= k_max_x and tomoe3.target_rope_y <= k_max_y
    tomoe3.release_rope_arrow(projectiles3, [], kyoto_map)
    rope3 = projectiles3[0]
    for _ in range(60):
        if not rope3.is_active:
            break
        rope3.update(0.016, kyoto_map)

    assert k_min_x <= tomoe3.wx <= k_max_x
    assert k_min_y <= tomoe3.wy <= k_max_y

    print("  -> Contenção absoluta de arena em [min, max] OK!")


def test_tomoe_obstacle_lock():
    print("Iniciando teste de colisão da mira com obstáculos sólidos...")
    game_map = GameMap()
    # Adiciona uma rocha em (14.0, 10.0)
    test_rock = Rock(wx=14.0, wy=10.0, radius=0.8)
    game_map.rocks.append(test_rock)

    tomoe = KyudoArcher(wx=10.0, wy=10.0)
    # Mira na direção da rocha e segura carga completa
    tomoe.start_rope_arrow_charge(20.0, 10.0, game_map)
    tomoe.update_rope_charge(1.0, 20.0, 10.0, game_map)

    # O alvo da flecha deve travar na rocha e não passar dela
    assert tomoe.target_rope_x <= 14.0 + test_rock.radius, f"A mira ({tomoe.target_rope_x}) deve travar no obstáculo (14.0)"
    assert tomoe.target_rope_x >= 13.0
    print("  -> Detecção e fixação em rocha/obstáculo OK!")


if __name__ == "__main__":
    test_tomoe_hold_and_release()
    test_tomoe_boundary_clamping()
    test_tomoe_obstacle_lock()
    print("\n=======================================================")
    print("TODOS OS TESTES DE TOMOE HOLD & RELEASE PASSARAM COM 100%!")
    print("=======================================================\n")
