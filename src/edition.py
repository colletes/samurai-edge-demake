"""
Edição do jogo: completa ou demo. O workflow da demo troca `IS_DEMO` para True antes de empacotar; para testar sem
empacotar, defina SAMURAI_EDGE_DEMO=1. A demo libera só Ren e Chiyo (1P ou 2P), só as arenas deles (Templo Shaolin e
Jardim Higanbana; a arena segue o lutador do P1) e sem Arcade.
"""
import os

from src.config import CHAR_REN, CHAR_CHIYO, ARENA_SHAOLIN, ARENA_HIGANBANA

IS_DEMO = False
VERSION = "2.0.0"

DEMO_FIGHTERS = (CHAR_REN, CHAR_CHIYO)
DEMO_ARENAS = (ARENA_SHAOLIN, ARENA_HIGANBANA)
DEMO_ARENA = ARENA_SHAOLIN  # fallback


def is_demo() -> bool:
    return IS_DEMO or os.environ.get("SAMURAI_EDGE_DEMO") == "1"
