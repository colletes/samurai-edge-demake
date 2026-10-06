"""
Edição do jogo: completa ou demo. O workflow da demo troca `IS_DEMO` para True antes de empacotar; para testar sem
empacotar, defina SAMURAI_EDGE_DEMO=1. A demo libera só Kenshi e Tomoe (1P ou 2P), só a arena da Kenshi e sem Arcade.
"""
import os

from src.config import CHAR_KENSHIN, CHAR_ARCHER, ARENA_BAMBOO

IS_DEMO = False
VERSION = "1.6.0"

DEMO_FIGHTERS = (CHAR_KENSHIN, CHAR_ARCHER)
DEMO_ARENA = ARENA_BAMBOO


def is_demo() -> bool:
    return IS_DEMO or os.environ.get("SAMURAI_EDGE_DEMO") == "1"
