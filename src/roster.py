"""Ordem única do elenco e arena de cada lutador; as telas de seleção de personagem e de arena seguem esta lista."""
from src.config import (
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_SAITOU, CHAR_RIFLE, CHAR_PURPLE, CHAR_GRAY,
    CHAR_KABUKI, CHAR_ARCHER, CHAR_PIRATE, CHAR_MUSKETEER, CHAR_REN, CHAR_CHIYO,
    CHAR_BENKEI, CHAR_ORIN, CHAR_GORO, CHAR_ICHI, CHAR_VALERIUS, CHAR_SEIMEI,
    CHAR_DAIKI, CHAR_AOI, CHAR_RAIDEN, CHAR_HENDRIKA,
    ARENA_BAMBOO, ARENA_KYOTO, ARENA_GANRYU, ARENA_IGA, ARENA_FOREST_CAMP, ARENA_NAGASHINO, ARENA_SHADOW_CAVE,
    ARENA_MIST_TEMPLE, ARENA_KABUKI_STAGE, ARENA_MOUNTAIN_SHRINE, ARENA_PIRATE_DECK, ARENA_BAROQUE_COURT,
    ARENA_SHAOLIN, ARENA_HIGANBANA,
)

# (id do lutador, id da arena dele, nome do lutador em i18n sem o prefixo "char_" e sem o sufixo "_name")
ROSTER = (
    # Veteranos (12)
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
    # Ciclo 1 (2)
    (CHAR_REN, ARENA_SHAOLIN, "ren"),
    (CHAR_CHIYO, ARENA_HIGANBANA, "chiyo"),
    # Ciclo 2 (2)
    (CHAR_BENKEI, ARENA_BAMBOO, "benkei"),
    (CHAR_ORIN, ARENA_KYOTO, "orin"),
    # Ciclo 3 (2)
    (CHAR_GORO, ARENA_FOREST_CAMP, "goro"),
    (CHAR_ICHI, ARENA_MIST_TEMPLE, "ichi"),
    # Ciclo 4 (2)
    (CHAR_VALERIUS, ARENA_SHADOW_CAVE, "valerius"),
    (CHAR_SEIMEI, ARENA_MOUNTAIN_SHRINE, "seimei"),
    # Ciclo 5 (2)
    (CHAR_DAIKI, ARENA_BAMBOO, "daiki"),
    (CHAR_AOI, ARENA_FOREST_CAMP, "aoi"),
    # Ciclo 6 (2)
    (CHAR_RAIDEN, ARENA_GANRYU, "raiden"),
    (CHAR_HENDRIKA, ARENA_BAROQUE_COURT, "hendrika"),
)

PLAYABLE_FIGHTERS = (
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN,
    CHAR_SAITOU, CHAR_RIFLE, CHAR_PURPLE, CHAR_GRAY,
    CHAR_KABUKI, CHAR_ARCHER, CHAR_PIRATE, CHAR_MUSKETEER,
    CHAR_REN, CHAR_CHIYO,
)

ROSTER_ORDER = tuple(fighter for fighter, _, _ in ROSTER)
ARENA_ORDER = tuple(arena for fighter, arena, _ in ROSTER if fighter in PLAYABLE_FIGHTERS)
ARENA_BY_FIGHTER = {fighter: arena for fighter, arena, _ in ROSTER}
FIGHTER_BY_ARENA = {arena: fighter for fighter, arena, _ in ROSTER if fighter in PLAYABLE_FIGHTERS}
FIGHTER_NAME_KEY = {fighter: f"char_{key}_name" for fighter, _, key in ROSTER}

# Dados gerados do Arcade (tools/generate_arcade_tables.py): ordem de força geral e taxa de vitória por confronto
from src.arcade.arcade_tables import ARCADE_TIER_ORDER, ARCADE_MATCHUP_TABLE  # noqa: E402,F401
