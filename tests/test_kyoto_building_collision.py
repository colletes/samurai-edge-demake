"""
Testes da Correção Urgente: Colisão de Fachadas (MachiyaFacade) e Limites Reais
da Via Jogável na arena de Kyoto Bakumatsu.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pygame
from src.entities.samurai import Samurai
from src.world.kyoto_map import KyotoMap, MachiyaFacade
from src.world.map_data import GameMap


def test_machiya_facade_has_check_collision():
    """A fachada deve ter o mesmo contrato check_collision() de Rock/Well/Tree."""
    facade = MachiyaFacade(wx=2.4, wy=0.4, width=4.4, depth=3.3)
    assert hasattr(facade, "check_collision")

    # Bem longe da fachada: sem colisão
    collided, px, py = facade.check_collision(50.0, 50.0, 0.3)
    assert collided is False

    # Centro do círculo dentro do retângulo da fachada: deve detectar colisão e empurrar para fora
    collided, px, py = facade.check_collision(4.0, 1.5, 0.3)
    assert collided is True
    assert (px != 0.0) or (py != 0.0)

    # Encostando bem na borda oeste por fora: também deve colidir (raio cobre a borda)
    collided, px, py = facade.check_collision(facade.wx - 0.1, facade.wy + 1.0, 0.3)
    assert collided is True
    assert px < 0  # Empurra para longe da fachada (oeste)


def test_fighters_cannot_enter_buildings_or_leave_street():
    """Lutador tentando andar continuamente em direção às machiyas do lado oeste não deve
    atravessar a fachada nem escapar da faixa real caminhável da rua de Kyoto."""
    game_map = KyotoMap()
    assert len(game_map.buildings) > 0
    assert hasattr(game_map, "playable_bounds")

    fighter = Samurai(10.0, 8.0, "TestFighter")

    # Anda para oeste (em direção às machiyas) por muitos frames
    for _ in range(400):
        fighter.apply_movement(-1.0, 0.0, 1 / 60.0, game_map)

    min_x, min_y, max_x, max_y = game_map.playable_bounds
    # Nunca deve ficar fora da faixa jogável...
    assert fighter.wx >= min_x - 0.001
    # ...e nunca deve penetrar de forma perceptível em nenhuma fachada do lado oeste (x em [2.4, 6.8]);
    # no equilíbrio exato (raio == distância até a borda) um epsilon de ponto flutuante pode acusar uma
    # "colisão" com empurrão insignificante (<1e-6) — isso não é um bug, é apenas a borda do raio.
    for b in game_map.buildings:
        collided, px, py = b.check_collision(fighter.wx, fighter.wy, fighter.radius)
        if collided:
            assert abs(px) < 0.01 and abs(py) < 0.01

    # Agora testa o lado leste (machiyas translúcidas, x >= 15.0)
    fighter2 = Samurai(10.0, 8.0, "TestFighter2")
    for _ in range(400):
        fighter2.apply_movement(1.0, 0.0, 1 / 60.0, game_map)

    assert fighter2.wx <= max_x + 0.001
    for b in game_map.buildings:
        collided, px, py = b.check_collision(fighter2.wx, fighter2.wy, fighter2.radius)
        if collided:
            assert abs(px) < 0.01 and abs(py) < 0.01


def test_roll_also_respects_building_collision():
    """O rolamento/esquiva (update_roll) usa o mesmo caminho de colisão da movimentação normal."""
    game_map = KyotoMap()
    fighter = Samurai(8.0, 2.0, "RollTester")
    fighter.trigger_roll(-1.0, 0.0)

    for _ in range(60):
        fighter.update_roll(1 / 60.0, game_map)
        if fighter.state != "ROLL":
            break

    min_x, _, _, _ = game_map.playable_bounds
    assert fighter.wx >= min_x - 0.001
    for building in game_map.buildings:
        collided, px, py = building.check_collision(fighter.wx, fighter.wy, fighter.radius)
        if collided:
            assert abs(px) < 0.01 and abs(py) < 0.01


def test_default_map_without_playable_bounds_still_uses_full_grid():
    """Mapas sem playable_bounds (ex: Bambu) continuam usando o clamp de grid cheio, sem regressão."""
    game_map = GameMap()
    fighter = Samurai(2.0, 10.0, "BambooTester")

    for _ in range(400):
        fighter.apply_movement(-1.0, 0.0, 1 / 60.0, game_map)

    assert fighter.wx >= 1.0 - 0.001
    assert fighter.wx <= game_map.cols - 1.0 + 0.001


if __name__ == "__main__":
    pygame.init()
    test_machiya_facade_has_check_collision()
    print("✓ test_machiya_facade_has_check_collision passed!")
    test_fighters_cannot_enter_buildings_or_leave_street()
    print("✓ test_fighters_cannot_enter_buildings_or_leave_street passed!")
    test_roll_also_respects_building_collision()
    print("✓ test_roll_also_respects_building_collision passed!")
    test_default_map_without_playable_bounds_still_uses_full_grid()
    print("✓ test_default_map_without_playable_bounds_still_uses_full_grid passed!")
    print("\nALL KYOTO BUILDING COLLISION TESTS PASSED SUCCESSFULLY!")
