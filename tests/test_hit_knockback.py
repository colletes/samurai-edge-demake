"""Golpe melee que fere sem matar empurra o ferido para fora do alcance de contra-ataque."""
import math
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()
pygame.font.init()

from src.combat.collision import CombatSystem, HIT_KNOCKBACK_DISTANCE
from src.entities.blue_samurai import BlueSamurai
from src.entities.red_samurai import RedSamurai
from src.isometric.camera import Camera
from src.world.map_data import GameMap


def _strike(attacker, victim, game_map):
    attacker.set_facing(victim.wx, victim.wy)
    attacker.slash_dir = (attacker.facing_x, attacker.facing_y)
    attacker.hitbox_active = True
    attacker.hitbox_radius = 1.4
    attacker.hitbox_center = (attacker.wx + attacker.facing_x * 0.9, attacker.wy + attacker.facing_y * 0.9)
    return CombatSystem().process_combat(attacker, victim, game_map, [], [], Camera(), [])


def test_wounded_fighter_is_knocked_out_of_melee_reach():
    game_map = GameMap()
    attacker = RedSamurai(wx=10.0, wy=10.0)
    victim = BlueSamurai(wx=11.0, wy=10.0)
    assert _strike(attacker, victim, game_map) is None
    assert victim.is_alive and victim.hp == 1
    dist = math.hypot(victim.wx - attacker.wx, victim.wy - attacker.wy)
    musashi_max_reach = 0.9 + 2.06 + victim.radius
    assert dist > musashi_max_reach, f"ferido ainda alcança o agressor: {dist:.2f} <= {musashi_max_reach:.2f}"
    assert dist >= HIT_KNOCKBACK_DISTANCE


def test_knockback_applies_symmetrically_to_p1():
    game_map = GameMap()
    victim = BlueSamurai(wx=10.0, wy=10.0)
    attacker = RedSamurai(wx=11.0, wy=10.0)
    attacker.set_facing(victim.wx, victim.wy)
    attacker.slash_dir = (attacker.facing_x, attacker.facing_y)
    attacker.hitbox_active = True
    attacker.hitbox_radius = 1.4
    attacker.hitbox_center = (attacker.wx + attacker.facing_x * 0.9, attacker.wy + attacker.facing_y * 0.9)
    CombatSystem().process_combat(victim, attacker, game_map, [], [], Camera(), [])
    assert victim.hp == 1 and victim.wx < 10.0 - 2.0


def test_lethal_hit_does_not_knock_back():
    game_map = GameMap()
    attacker = BlueSamurai(wx=10.0, wy=10.0)
    victim = RedSamurai(wx=11.0, wy=10.0)
    assert _strike(attacker, victim, game_map) == "P1_WINS"
    assert victim.wx == 11.0


def test_knockback_can_throw_fighter_into_pit():
    from tests.test_arena_engine import _crossing_arena
    arena = _crossing_arena()
    pit = arena.pits[1]
    attacker = RedSamurai(wx=pit.x0 - 2.0, wy=11.0)
    victim = BlueSamurai(wx=pit.x0 - 1.0, wy=11.0)
    _strike(attacker, victim, arena)
    assert victim.update_pit(0.016, arena) is True, "ferido empurrado para o buraco deve cair"


if __name__ == "__main__":
    test_wounded_fighter_is_knocked_out_of_melee_reach()
    test_knockback_applies_symmetrically_to_p1()
    test_lethal_hit_does_not_knock_back()
    test_knockback_can_throw_fighter_into_pit()
    print("TODOS OS TESTES DE KNOCKBACK PASSARAM!")
