"""
Testes automatizados das arenas do Ciclo 6: Dohyo Sagrado (Raiden) e Armazém de Dejima (Hendrika).
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
pygame.init()

from src.config import ARENA_DOHYO, ARENA_DEJIMA, CHAR_RAIDEN, CHAR_HENDRIKA
from src.world.arenas import create_arena, ARENA_SPECS
from src.roster import ARENA_BY_FIGHTER, FIGHTER_BY_ARENA, PLAYABLE_FIGHTERS


def test_cycle6_arenas_spec_and_loading():
    print("--- Testando Arenas do Ciclo 6 (Dohyo Sagrado & Armazém de Dejima) ---")
    assert ARENA_DOHYO in ARENA_SPECS, "ARENA_DOHYO deve estar em ARENA_SPECS"
    assert ARENA_DEJIMA in ARENA_SPECS, "ARENA_DEJIMA deve estar em ARENA_SPECS"

    dohyo = create_arena(ARENA_DOHYO)
    assert dohyo is not None, "create_arena deve instanciar Dohyo Sagrado"
    assert dohyo.arena_id == ARENA_DOHYO
    assert ARENA_SPECS[ARENA_DOHYO].name == "Dohyo Sagrado"
    assert dohyo.music == "bgm_sacred_dohyo"
    assert dohyo.cols == 22 and dohyo.rows == 22
    print("  [OK] Dohyo Sagrado instanciado com sucesso com BGM bgm_sacred_dohyo")

    dejima = create_arena(ARENA_DEJIMA)
    assert dejima is not None, "create_arena deve instanciar Armazém de Dejima"
    assert dejima.arena_id == ARENA_DEJIMA
    assert ARENA_SPECS[ARENA_DEJIMA].name == "Armazém de Dejima"
    assert dejima.music in ("bgm_dejima_dock", "bgm_dejima_warehouse")
    assert dejima.cols == 22 and dejima.rows == 22
    print("  [OK] Armazém de Dejima instanciado com sucesso com BGM bgm_dejima_dock")


def test_cycle6_arena_roster_mapping():
    print("--- Testando Mapeamento no Roster ---")
    assert ARENA_BY_FIGHTER[CHAR_RAIDEN] == ARENA_DOHYO
    assert ARENA_BY_FIGHTER[CHAR_HENDRIKA] == ARENA_DEJIMA
    assert FIGHTER_BY_ARENA[ARENA_DOHYO] == CHAR_RAIDEN
    assert FIGHTER_BY_ARENA[ARENA_DEJIMA] == CHAR_HENDRIKA
    assert CHAR_RAIDEN in PLAYABLE_FIGHTERS
    assert CHAR_HENDRIKA in PLAYABLE_FIGHTERS
    print("  [OK] Mapeamento bidirecional lutador <-> arena do Ciclo 6 validado")


if __name__ == "__main__":
    test_cycle6_arenas_spec_and_loading()
    test_cycle6_arena_roster_mapping()
    print("\nTODOS OS TESTES DE ARENAS DO CICLO 6 PASSARAM COM SUCESSO!")
