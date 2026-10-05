"""
Auditoria do sistema de HP.

Regras:
- Elenco com 2 HP; Musashi com 3 HP.
- Ataques que causam 1 de dano continuam causando 1; todos os demais causam 2.
- Perigos instantâneos do cenário de Kyoto (carruagem e escombros, dano 99) seguem letais.
"""
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

import main
from src.combat.collision import CombatSystem
from src.effects.cinematic_director import CinematicDirector
from src.isometric.camera import Camera
from src.world.map_data import GameMap

CHARACTERS = {
    "KENSHIN": 2, "MUSASHI": 3, "NINJA": 2, "AMERICAN": 2, "GRAY": 2, "PURPLE": 2,
    "SAITOU": 2, "RIFLE": 2, "KABUKI": 2, "ARCHER": 2, "PIRATE": 2, "MUSKETEER": 2,
}
HAZARD_FILES = {os.path.join("src", "world", "kyoto_map.py")}


def test_starting_hp_per_character():
    for name, expected in CHARACTERS.items():
        fighter = main.create_fighter(getattr(main, f"CHAR_{name}"), 5.0, 5.0)
        assert fighter.hp == fighter.max_hp == expected, (name, fighter.hp, fighter.max_hp)
    print("  [OK] Musashi com 3 HP e os outros 11 lutadores com 2 HP.", flush=True)


def test_every_attack_deals_one_or_two():
    """Nenhum ataque de lutador pode causar um valor diferente de 1 ou 2 (exceto perigos de Kyoto)."""
    offenders = []
    for folder, _, files in os.walk(os.path.join(ROOT, "src")):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            path = os.path.join(folder, fname)
            rel = os.path.relpath(path, ROOT)
            if rel in HAZARD_FILES:
                continue
            with open(path, encoding="utf-8") as fh:
                for lineno, line in enumerate(fh, 1):
                    for value in re.findall(r"take_hit\([^)]*damage=(\d+)\)", line):
                        if int(value) not in (1, 2):
                            offenders.append((rel, lineno, value))
    assert not offenders, offenders
    print("  [OK] Todo take_hit literal causa 1 ou 2 de dano (fora os perigos de Kyoto).", flush=True)


def test_two_damage_hit_vs_hp_pools():
    for name, hp in CHARACTERS.items():
        fighter = main.create_fighter(getattr(main, f"CHAR_{name}"), 5.0, 5.0)
        _, dead = fighter.take_hit((1.0, 0.0), damage=2)
        assert dead == (hp == 2), (name, "um golpe de 2 mata quem tem 2 HP e deixa Musashi com 1")
        if hp == 3:
            fighter.state = "IDLE"
            fighter.soft_stun_timer = 0.0
            _, dead = fighter.take_hit((1.0, 0.0), damage=2)
            assert dead and fighter.hp == 0
        fighter = main.create_fighter(getattr(main, f"CHAR_{name}"), 5.0, 5.0)
        _, dead = fighter.take_hit((1.0, 0.0), damage=1)
        assert not dead and fighter.hp == hp - 1, name
    print("  [OK] Golpe de 1 tira 1 HP; golpe de 2 tira 2 (Musashi sobrevive ao primeiro).", flush=True)


def test_poison_deals_two_and_only_kills_when_hp_runs_out():
    for char, survives in (("MUSASHI", True), ("KENSHIN", False)):
        p1 = main.create_fighter(main.CHAR_KABUKI, 5.0, 5.0)
        p2 = main.create_fighter(getattr(main, f"CHAR_{char}"), 14.0, 14.0)
        p2.is_poisoned = True
        p2.poison_timer = 0.01
        winner = CombatSystem().process_combat(
            p1, p2, GameMap(), [], [], Camera(), [], 0.05, cinematic_director=CinematicDirector())
        assert p2.is_alive == survives, char
        assert p2.hp == (1 if survives else 0), (char, p2.hp)
        assert (winner is None) == survives, (char, winner)
    print("  [OK] Veneno causa 2 de dano: Musashi sobrevive com 1 HP, os demais morrem.", flush=True)


def test_hp_system():
    print("=== TESTE: Sistema de HP ===", flush=True)
    test_starting_hp_per_character()
    test_every_attack_deals_one_or_two()
    test_two_damage_hit_vs_hp_pools()
    test_poison_deals_two_and_only_kills_when_hp_runs_out()
    print("=== TESTE DE HP CONCLUÍDO COM SUCESSO ===", flush=True)


if __name__ == "__main__":
    test_hp_system()
