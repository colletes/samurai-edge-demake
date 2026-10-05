"""Barras de dano do HUD (2 seções; Musashi com 3) e ausência de mensagens de dano sobre os lutadores."""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()

from src.combat.collision import CombatSystem
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.blue_samurai import BlueSamurai
from src.entities.red_samurai import RedSamurai
from src.isometric.camera import Camera
from src.ui.round_result import render_damage_bars
from src.world.map_data import GameMap

RED, BLUE = (230, 60, 60), (70, 140, 255)
PANEL = pygame.Rect(SCREEN_WIDTH // 2 - 270, 10, 540, 66)
BG = (5, 5, 5)


def _segments_lit(p1, p2):
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.fill(BG)
    render_damage_bars(surface, p1, p2, RED, BLUE, PANEL)
    y = PANEL.bottom + 6 + 4
    left = [surface.get_at((PANEL.x + 20 + i * 38 + 17, y))[:3] == RED for i in range(3)]
    total_w = 2 * 34 + 4
    right = [surface.get_at((PANEL.right - 20 - total_w + i * 38 + 17, y))[:3] == BLUE for i in range(2)]
    return left, right


def test_segment_count_follows_max_hp():
    left, right = _segments_lit(BlueSamurai(0, 0), RedSamurai(0, 0))
    assert left == [True, True, True], "Musashi tem 3 seções"
    assert right == [True, True], "os demais têm 2 seções"


def test_segments_empty_as_hp_drops():
    musashi, kenshi = BlueSamurai(0, 0), RedSamurai(0, 0)
    musashi.hp = 1
    kenshi.hp = 0
    left, right = _segments_lit(musashi, kenshi)
    assert left == [True, False, False]
    assert right == [False, False]


def test_no_damage_text_banners_on_hit():
    game_map = GameMap()
    attacker = RedSamurai(wx=10.0, wy=10.0)
    victim = BlueSamurai(wx=11.0, wy=10.0)
    attacker.set_facing(victim.wx, victim.wy)
    attacker.slash_dir = (attacker.facing_x, attacker.facing_y)
    attacker.hitbox_active = True
    attacker.hitbox_radius = 1.4
    attacker.hitbox_center = (attacker.wx + attacker.facing_x * 0.9, attacker.wy + attacker.facing_y * 0.9)
    banners = []
    CombatSystem().process_combat(attacker, victim, game_map, [], banners, Camera(), [])
    assert victim.hp == 1
    assert not [b for b in banners if "DMG" in b.text or "/2" in b.text], [b.text for b in banners]


if __name__ == "__main__":
    test_segment_count_follows_max_hp()
    test_segments_empty_as_hp_drops()
    test_no_damage_text_banners_on_hit()
    print("TODOS OS TESTES DA BARRA DE DANO PASSARAM!")
