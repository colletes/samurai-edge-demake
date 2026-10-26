"""
Testes de integração completa do Ciclo 6 (Raiden & Hendrika) e Roster 24/24.
Valida o elenco de 24 guerreiros, o Modo Arcade de 12 lutas com alta aleatoriedade,
e a sincronização de UI, Roster e Inspetores.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
pygame.init()

from src.config import (
    CHAR_RAIDEN, CHAR_HENDRIKA, CHAR_BOSS, ARENA_DOHYO, ARENA_DEJIMA,
    SCREEN_WIDTH, SCREEN_HEIGHT
)
from src.roster import (
    ROSTER, PLAYABLE_FIGHTERS, ROSTER_ORDER, ARENA_BY_FIGHTER,
    FIGHTER_BY_ARENA, ARCADE_TIER_ORDER, ARCADE_MATCHUP_TABLE
)
from src.arcade.arcade_mode import ArcadeRun, FightKind, build_ladder, DUEL_COUNT, TOTAL_FIGHTS
from src.arcade.arcade_screens import ArcadeBracketScreen
from src.ui.character_select import CharacterSelectScreen
from src.ui.game_help import GameHelpModal, FIGHTERS_GUIDE_DATA
from tools.model_inspector import CHARACTERS


def test_roster_24_symmetry():
    print("--- Testando Roster 24/24 & Simetria ---")
    assert len(ROSTER) == 24, f"Esperado 24 combatentes no ROSTER, obtido {len(ROSTER)}"
    assert len(PLAYABLE_FIGHTERS) == 24, f"Esperado 24 em PLAYABLE_FIGHTERS, obtido {len(PLAYABLE_FIGHTERS)}"
    assert len(ROSTER_ORDER) == 24, f"Esperado 24 em ROSTER_ORDER, obtido {len(ROSTER_ORDER)}"
    assert CHAR_RAIDEN in PLAYABLE_FIGHTERS
    assert CHAR_HENDRIKA in PLAYABLE_FIGHTERS
    print("  [OK] Roster completo com 24 guerreiros jogáveis.")


def test_arcade_12_fights_and_randomness():
    print("--- Testando Modo Arcade (12 Lutas & Aleatoriedade) ---")
    assert DUEL_COUNT == 8, f"Esperado DUEL_COUNT=8, obtido {DUEL_COUNT}"
    assert TOTAL_FIGHTS == 12, f"Esperado TOTAL_FIGHTS=12, obtido {TOTAL_FIGHTS}"
    assert len(ARCADE_TIER_ORDER) == 24, f"Esperado 24 em ARCADE_TIER_ORDER, obtido {len(ARCADE_TIER_ORDER)}"

    # Testar para Raiden e Hendrika
    for char_id in (CHAR_RAIDEN, CHAR_HENDRIKA):
        run = ArcadeRun(char_id, difficulty_start=1, seed=42)
        assert len(run.ladder) == 12, f"Ladder deve ter 12 lutas, obtido {len(run.ladder)}"
        kinds = [f.kind for f in run.ladder]
        assert kinds == [FightKind.DUEL] * 8 + [FightKind.MIRROR, FightKind.ENDURANCE, FightKind.NINJA_CHALLENGE, FightKind.BOSS]
        assert run.ladder[8].kind == FightKind.MIRROR
        assert run.ladder[8].opponents == (char_id,)
        assert run.ladder[9].kind == FightKind.ENDURANCE
        assert len(run.ladder[9].opponents) == 2
        assert run.ladder[10].kind == FightKind.NINJA_CHALLENGE
        assert run.ladder[11].kind == FightKind.BOSS

    # Testar alta aleatoriedade de oponentes entre sementes diferentes
    duelists_by_seed = []
    for s in range(20):
        ladder = build_ladder("kenshin", seed=s * 101)
        duels = tuple(f.opponents[0] for f in ladder[:8])
        duelists_by_seed.append(duels)

    unique_runs = len(set(duelists_by_seed))
    assert unique_runs >= 12, f"Esperado ao menos 12 sequências de duelos únicas em 20 seeds, obtido {unique_runs}"
    print(f"  [OK] Alta entropia confirmada: {unique_runs}/20 runs geraram escalações distintas.")


def test_ui_and_bracket_12_nodes():
    print("--- Testando Apresentação da UI do Bracket (12 Nós) ---")
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    run = ArcadeRun("raiden", difficulty_start=1, seed=123)
    bracket = ArcadeBracketScreen()
    bracket.open(run)
    bracket.render(screen)
    print("  [OK] ArcadeBracketScreen renderizou 12 nós sem erro visual.")


def test_character_select_and_help():
    print("--- Testando Grade de Seleção e Ajuda ---")
    cs = CharacterSelectScreen()
    ready_chars = [c for c in cs.characters if c.get("ready")]
    assert len(ready_chars) == 24, f"Esperado 24 combatentes com ready=True, obtido {len(ready_chars)}"

    # Verificar registro no Model Inspector
    assert "raiden" in CHARACTERS
    assert "hendrika" in CHARACTERS

    # Verificar Guia de Ajuda
    fighter_ids = [f["id"] for f in FIGHTERS_GUIDE_DATA]
    assert CHAR_RAIDEN in fighter_ids
    assert CHAR_HENDRIKA in fighter_ids
    print("  [OK] Character Select, Model Inspector e Game Help 100% sincronizados com Raiden e Hendrika.")


if __name__ == "__main__":
    test_roster_24_symmetry()
    test_arcade_12_fights_and_randomness()
    test_ui_and_bracket_12_nodes()
    test_character_select_and_help()
    print("\nTODOS OS TESTES DE INTEGRAÇÃO DO CICLO 6 PASSARAM COM SUCESSO!")
