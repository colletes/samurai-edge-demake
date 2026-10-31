"""
Edição do jogo: completa ou demo. O workflow da demo troca `IS_DEMO` para True antes de empacotar; para testar sem
empacotar, defina SAMURAI_EDGE_DEMO=1. A demo libera Kenshi, Valerius, Hendrika e Hanzo (1P ou 2P), suas respectivas
arenas (Bambu, Cemitério Gótico, Armazém Dejima e Telhados de Iga; a arena segue o lutador do P1), modo Versus e Opções (sem Galeria e sem Arcade).
"""
import os

from src.config import (
    CHAR_KENSHIN, CHAR_VALERIUS, CHAR_HENDRIKA, CHAR_HANZO,
    ARENA_BAMBOO, ARENA_GOTHIC_CEMETERY, ARENA_DEJIMA, ARENA_IGA
)

IS_DEMO = False
VERSION = "3.0.1alpha"

DEMO_FIGHTERS = (CHAR_KENSHIN, CHAR_VALERIUS, CHAR_HENDRIKA, CHAR_HANZO)
DEMO_ARENAS = (ARENA_BAMBOO, ARENA_GOTHIC_CEMETERY, ARENA_DEJIMA, ARENA_IGA)
DEMO_ARENA = ARENA_BAMBOO  # fallback


def is_demo() -> bool:
    return IS_DEMO or os.environ.get("SAMURAI_EDGE_DEMO") == "1"
