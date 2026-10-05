"""Ordem única do elenco e arena de cada lutador; as telas de seleção de personagem e de arena seguem esta lista."""
from src.config import (
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_SAITOU, CHAR_RIFLE, CHAR_PURPLE, CHAR_GRAY,
    CHAR_KABUKI, CHAR_ARCHER, CHAR_PIRATE, CHAR_MUSKETEER,
    ARENA_BAMBOO, ARENA_KYOTO, ARENA_GANRYU, ARENA_IGA, ARENA_FOREST_CAMP, ARENA_NAGASHINO, ARENA_SHADOW_CAVE,
    ARENA_MIST_TEMPLE, ARENA_KABUKI_STAGE, ARENA_MOUNTAIN_SHRINE, ARENA_PIRATE_DECK, ARENA_BAROQUE_COURT,
)

# (id do lutador, id da arena dele, nome do lutador em i18n sem o prefixo "char_" e sem o sufixo "_name")
ROSTER = (
    (CHAR_KENSHIN, ARENA_BAMBOO, "kenshi"),
    (CHAR_MUSASHI, ARENA_GANRYU, "musashi"),
    (CHAR_NINJA, ARENA_IGA, "hanzo"),
    (CHAR_AMERICAN, ARENA_FOREST_CAMP, "joe"),
    (CHAR_SAITOU, ARENA_KYOTO, "saitou"),
    (CHAR_RIFLE, ARENA_NAGASHINO, "teppo"),
    (CHAR_PURPLE, ARENA_SHADOW_CAVE, "murasaki"),
    (CHAR_GRAY, ARENA_MIST_TEMPLE, "kasumi"),
    (CHAR_KABUKI, ARENA_KABUKI_STAGE, "okuni"),
    (CHAR_ARCHER, ARENA_MOUNTAIN_SHRINE, "tomoe"),
    (CHAR_PIRATE, ARENA_PIRATE_DECK, "anne"),
    (CHAR_MUSKETEER, ARENA_BAROQUE_COURT, "julie"),
)

ROSTER_ORDER = tuple(fighter for fighter, _, _ in ROSTER)
ARENA_ORDER = tuple(arena for _, arena, _ in ROSTER)
ARENA_BY_FIGHTER = {fighter: arena for fighter, arena, _ in ROSTER}
FIGHTER_BY_ARENA = {arena: fighter for fighter, arena, _ in ROSTER}
FIGHTER_NAME_KEY = {fighter: f"char_{key}_name" for fighter, _, key in ROSTER}
