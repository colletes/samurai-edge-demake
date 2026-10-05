"""
Teste do entregável 8.1: regras do Arcade (escada, desafios, Continues, dificuldade, pontuação, save).
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_arcade_mode.py
"""
import json
import os
import random
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src.arcade import arcade_save
from src.arcade.arcade_screens import ArcadeBracketScreen, ArcadeDifficultyScreen, ArcadeResultScreen
from src.i18n import set_lang, t
from src.ui.character_select import CharacterSelectScreen
from src.ui.pause_menu import PauseMenu, ACTION_ABANDON, ACTION_RESUME
from src.ui.title_screen import SumieTitleScreen
from src.arcade.arcade_mode import (
    ArcadeRun, FightKind, build_ladder, NINJA_ORDER, NINJAS, FIGHT_LOST, FIGHT_WON, NEXT_OPPONENT, NEXT_ROUND,
    ORDER_RANDOM, CONTINUE_PENALTY, SCORE_FIGHT,
)
from src.config import ARENA_SHADOW_CAVE
from src.roster import ROSTER_ORDER, ARENA_BY_FIGHTER, ARCADE_TIER_ORDER, ARCADE_MATCHUP_TABLE


def test_tables_are_complete():
    assert set(ARCADE_TIER_ORDER) == set(ROSTER_ORDER) and len(ARCADE_TIER_ORDER) == 12
    for a in ROSTER_ORDER:
        for b in ROSTER_ORDER:
            if a != b:
                assert 0.0 <= ARCADE_MATCHUP_TABLE[a][b] <= 100.0, (a, b)
    print("  [OK] Tabelas geradas: 12 lutadores e os 132 confrontos sem lacunas.", flush=True)


def test_ladder_for_all_fighters():
    for player in ROSTER_ORDER:
        ladder = build_ladder(player, seed=3)
        assert len(ladder) == 11, player
        kinds = [f.kind for f in ladder]
        assert kinds == [FightKind.DUEL] * 7 + [FightKind.MIRROR, FightKind.ENDURANCE, FightKind.NINJA_CHALLENGE, FightKind.BOSS]
        duels = [f.opponents[0] for f in ladder[:7]]
        assert len(set(duels)) == 7 and player not in duels and not (set(duels) & NINJAS), (player, duels)
        strength = [ARCADE_TIER_ORDER.index(c) for c in duels]
        assert strength == sorted(strength), "do mais fraco ao mais forte"
        assert [ARENA_BY_FIGHTER[o] for o in duels] == [f.arena_id for f in ladder[:7]]
        mirror = ladder[7]
        assert mirror.opponents == (player,) and mirror.arena_id == ARENA_BY_FIGHTER[player] and not mirror.is_challenge

        endurance = ladder[8]
        assert len(endurance.opponents) == 2 and len(set(endurance.opponents)) == 2
        assert player not in endurance.opponents and not (set(endurance.opponents) & NINJAS)
        assert endurance.player_round_lives == 2 and endurance.arena_id == ARENA_BY_FIGHTER[endurance.opponents[0]]
        candidates = [c for c in ROSTER_ORDER if c not in NINJAS and c != player]
        rate = {c: ARCADE_MATCHUP_TABLE[c][player] for c in candidates}
        others = [rate[c] for c in candidates if c not in endurance.opponents]
        assert min(rate[c] for c in endurance.opponents) >= max(others), (player, endurance.opponents)
        rates = [ARCADE_MATCHUP_TABLE[c][player] for c in endurance.opponents]
        assert rates == sorted(rates), "do mais fraco ao mais forte no confronto"

        ninja = ladder[9]
        assert ninja.opponents == NINJA_ORDER and len(ninja.opponents) == 4
        assert ninja.arena_id == ARENA_SHADOW_CAVE and ninja.player_round_lives == 2
        if player in NINJAS:
            assert player in ninja.opponents, "a vez do ninja vira espelho"
        assert ladder[10].kind == FightKind.BOSS
    print("  [OK] Escada de 11 lutas correta para os 12 lutadores (duelos, espelho, endurance, ninjas, chefe).", flush=True)


def test_ladder_order_and_seed():
    assert [f.opponents for f in build_ladder("kenshin", 5)] == [f.opponents for f in build_ladder("kenshin", 5)]
    a = [f.opponents[0] for f in build_ladder("kenshin", 1, ORDER_RANDOM)[:7]]
    b = [f.opponents[0] for f in build_ladder("kenshin", 1, ORDER_RANDOM)[:7]]
    c = [f.opponents[0] for f in build_ladder("kenshin", 2, ORDER_RANDOM)[:7]]
    assert a == b and sorted(a) == sorted(c)
    discarded = {tuple(sorted(f.opponents[0] for f in build_ladder("ninja", s)[:7])) for s in range(12)}
    assert len(discarded) > 1, "jogador ninja: o descartado muda com a semente"
    print("  [OK] A ordem por tier e por semente é reproduzível; ninja descarta um oponente por sorteio.", flush=True)


def play_fight(run, results):
    out = None
    for r in results:
        out = run.on_round_end(r, round_time=30.0, flawless=False)
    return out


def test_duel_bo3():
    run = ArcadeRun("kenshin", difficulty_start=1)
    assert run.on_round_end("P1", 20) == NEXT_ROUND
    assert run.on_round_end("DRAW", 20) == NEXT_ROUND
    assert run.on_round_end("P2", 20) == NEXT_ROUND
    assert run.on_round_end("P1", 20) == FIGHT_WON
    assert run.index == 1
    lost = ArcadeRun("kenshin")
    assert play_fight(lost, ["P2", "P1", "P2"]) == FIGHT_LOST and lost.index == 0
    print("  [OK] Duelo BO3: vence com 2 rounds, perde com 2, empate não conta.", flush=True)


def jump_to(run, kind):
    run.index = next(i for i, f in enumerate(run.ladder) if f.kind == kind)
    run._reset_fight_state()


def test_challenges():
    run = ArcadeRun("kenshin")
    jump_to(run, FightKind.NINJA_CHALLENGE)
    assert run.lives_left == 2
    seen = []
    assert run.on_round_end("P1") == NEXT_ROUND
    assert run.on_round_end("P1") == NEXT_OPPONENT
    seen.append(run.current_opponent())
    assert run.current_opponent() == NINJA_ORDER[1] and run.rounds_won_vs_current == 0
    assert run.on_round_end("P2") == NEXT_ROUND and run.lives_left == 1
    assert run.on_round_end("P2") == FIGHT_LOST, "o 2º round perdido encerra o desafio"

    run.on_continue()
    assert run.current_opponent() == NINJA_ORDER[0] and run.lives_left == 2, "o Continue refaz o desafio inteiro"

    for i in range(4):
        assert run.on_round_end("P1") == NEXT_ROUND
        r = run.on_round_end("P1")
        assert r == (NEXT_OPPONENT if i < 3 else FIGHT_WON), (i, r)
    assert run.index == 10

    end = ArcadeRun("musashi")
    jump_to(end, FightKind.ENDURANCE)
    first = end.current_opponent()
    end.on_round_end("P1"); end.on_round_end("P1")
    assert end.current_opponent() != first and end.ladder[8].arena_id == ARENA_BY_FIGHTER[first], "troca de oponente sem trocar de arena"
    end.on_round_end("P2")
    assert end.lives_left == 1
    print("  [OK] Desafios: 2 rounds por oponente, 2 vidas de round, 2ª derrota encerra, Continue refaz tudo.", flush=True)


def test_continues_score_and_difficulty():
    run = ArcadeRun("kenshin", difficulty_start=1)
    run.score = 500
    run.on_continue()
    assert run.score == 0 and run.points_lost_to_continues == 500 and run.continues == 1
    run.score = 5000
    run.on_continue()
    assert run.score == 3000 and run.points_lost_to_continues == 2500 and run.continues == 2
    assert run.difficulty_level == 0, "Continue baixa a dificuldade (mínimo fácil)"
    run.on_continue()
    assert run.difficulty_level == 0 and run.continues == 3, "Continues são infinitos"

    run = ArcadeRun("kenshin", difficulty_start=1)
    play_fight(run, ["P1", "P1"])
    assert run.difficulty_level == 1 and run.clean_streak == 1
    play_fight(run, ["P1", "P1"])
    assert run.difficulty_level == 2 and run.last_difficulty_change == 1 and run.clean_streak == 0
    play_fight(run, ["P1", "P1"]); play_fight(run, ["P1", "P1"])
    assert run.difficulty_level == 2, "máximo difícil"
    run.on_continue()
    assert run.difficulty_level == 1 and run.clean_streak == 0 and run.last_difficulty_change == -1
    print("  [OK] Continues contados (-2000, nunca negativo) e dificuldade sobe a cada 2 lutas e desce a cada Continue.", flush=True)


def test_scoring():
    run = ArcadeRun("kenshin")
    run.on_round_end("P1", round_time=20.0, flawless=True, kill_style=True)
    assert run.score == 400 + 500 + 100
    run.on_round_end("P1", round_time=99.0)
    assert run.score == 1000 + SCORE_FIGHT
    print("  [OK] Pontuação: 1000 por luta, +500 sem dano, bônus de tempo e estilo.", flush=True)


def test_full_simulated_journey():
    rng = random.Random(7)
    run = ArcadeRun("saitou", difficulty_start=0, seed=7)
    rounds = 0
    while not run.is_finished and rounds < 2000:
        rounds += 1
        win_p = 0.62 if run.current_fight().kind != FightKind.BOSS else 0.5
        r = run.on_round_end("P1" if rng.random() < win_p else "P2", round_time=rng.uniform(10, 50))
        if r == FIGHT_LOST:
            run.on_continue()
    assert run.is_finished and rounds < 2000
    assert run.score >= 0 and len(run.stats) == 11
    print(f"  [OK] Jornada simulada completa em {rounds} rounds, com {run.continues} Continue(s) e placar >= 0.", flush=True)


def test_run_roundtrip_and_save():
    run = ArcadeRun("kabuki", difficulty_start=2, seed=11)
    play_fight(run, ["P1", "P1"])
    run.on_continue()
    data = run.to_dict()
    again = ArcadeRun.from_dict(json.loads(json.dumps(data)))
    assert (again.index, again.score, again.continues, again.difficulty_level, again.player_char) == \
        (run.index, run.score, run.continues, run.difficulty_level, run.player_char)
    assert [f.opponents for f in again.ladder] == [f.opponents for f in run.ladder]

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "arcade_save.json")
        assert arcade_save.load(path) == arcade_save.empty_data(), "arquivo ausente"
        with open(path, "w") as f:
            f.write("{quebrado")
        assert arcade_save.load(path) == arcade_save.empty_data(), "JSON corrompido"
        with open(path, "w") as f:
            json.dump({"version": 99, "high_scores": [{"score": 1}]}, f)
        assert arcade_save.load(path) == arcade_save.empty_data(), "versão nova"

        data = arcade_save.empty_data()
        data["current_run"] = run.to_dict()
        assert arcade_save.save(data, path) and arcade_save.load(path)["current_run"]["player_char"] == "kabuki"
        assert not [n for n in os.listdir(tmp) if n.endswith(".tmp")], "sem temporários sobrando"

        for i in range(12):
            r = ArcadeRun("kenshin")
            r.score = 1000 * i
            r.continues = i % 3
            r.elapsed = 100.0 + i
            arcade_save.add_high_score(data, r, now=0)
        scores = data["high_scores"]
        assert len(scores) == 10 and scores[0]["score"] == 11000 and scores[-1]["score"] == 2000
        tie_a, tie_b = ArcadeRun("kenshin"), ArcadeRun("kenshin")
        tie_a.score = tie_b.score = 5000
        tie_a.continues, tie_b.continues = 2, 0
        d2 = arcade_save.empty_data()
        arcade_save.add_high_score(d2, tie_a)
        pos = arcade_save.add_high_score(d2, tie_b)
        assert pos == 1 and d2["clears"]["kenshin"] == 2, "empate: menos Continues primeiro"
        assert d2["best_clear_time"]["kenshin"] == 0.0
    print("  [OK] Jornada e arcade_save.json: ida e volta, tolerância a erros, top 10 e desempate.", flush=True)


def _key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="", scancode=0)


def test_screens_render_in_both_languages():
    surf = pygame.Surface((1280, 720))
    for lang in ("pt", "en"):
        set_lang(lang)
        diff = ArcadeDifficultyScreen()
        diff.open(1, saved_run=ArcadeRun("kenshin").to_dict(), high_scores=[{"score": 9000, "char": "kenshin"}])
        diff.render(surf)
        assert diff.options == ["resume", 0, 1, 2] and diff.options[diff.selected] == 1
        assert diff.handle_event(_key(pygame.K_RETURN)) == ("START", 1)
        diff.handle_event(_key(pygame.K_UP))
        assert diff.handle_event(_key(pygame.K_ESCAPE)) == "BACK"
        diff.open(2)
        assert diff.options == [0, 1, 2] and diff.handle_event(_key(pygame.K_RETURN)) == ("START", 2)

        run = ArcadeRun("kenshin")
        bracket = ArcadeBracketScreen()
        for banner in (None, "cleared", "defeat"):
            bracket.open(run, banner, 1234)
            bracket.render(surf)
        mirror = ArcadeRun("ninja")
        jump_to(mirror, FightKind.NINJA_CHALLENGE)
        bracket.open(mirror)
        bracket.render(surf)
        bracket.open(run)
        assert bracket.handle_event(_key(pygame.K_RETURN)) == "FIGHT"
        assert bracket.handle_event(_key(pygame.K_ESCAPE)) is None and bracket.confirm_abandon
        assert bracket.handle_event(_key(pygame.K_RETURN)) is None and not bracket.confirm_abandon
        bracket.handle_event(_key(pygame.K_ESCAPE))
        assert bracket.handle_event(_key(pygame.K_ESCAPE)) == "ABANDON"

        result = ArcadeResultScreen()
        result.open(run, 3, [{"score": 100 * i, "char": "kenshin"} for i in range(10)])
        result.update(1.0)
        result.render(surf)
        assert result.handle_event(_key(pygame.K_RETURN)) == "DONE"
        for key in ("arcade_title", "arcade_fight_n_of_m", "mode_arcade_sub", "arcade_final_victory"):
            assert t(key) != key
    set_lang("pt")
    print("  [OK] Menu de dificuldade, chaves e resultado renderizam em PT e EN e respondem ao teclado.", flush=True)


def test_title_card_enabled():
    title = SumieTitleScreen()
    title.selected_mode = 0
    assert title.handle_event(_key(pygame.K_RETURN)) == "ARCADE"
    print("  [OK] O cartão ARCADE do título está habilitado.", flush=True)


def test_pause_menu_arcade_items():
    pm = PauseMenu()
    snap = pygame.Surface((1280, 720))
    pm.open(snap, arcade=True)
    actions = [a for _, a in pm.items]
    assert ACTION_ABANDON in actions and "ARENA" not in actions and "FIGHTER" not in actions
    pm.selected = actions.index(ACTION_ABANDON)
    assert pm.handle_event(_key(pygame.K_RETURN)) is None and pm.confirm_abandon, "abandonar pede confirmação"
    assert pm.handle_event(_key(pygame.K_RETURN)) == ACTION_ABANDON
    pm.open(snap)
    assert ACTION_ABANDON not in [a for _, a in pm.items] and pm.handle_event(_key(pygame.K_ESCAPE)) == ACTION_RESUME
    print("  [OK] Pausa do Arcade: sem cenário/lutador, com abandono confirmado.", flush=True)


def test_character_select_arcade_mode():
    cs = CharacterSelectScreen()
    cs.arcade_mode = True
    cs.vs_ai = False
    assert cs.vs_ai is True, "o Arcade trava o modo 1P"
    cs.reset()
    cs.p1_choice_idx = 0
    assert cs.handle_event(_key(pygame.K_RETURN)) is True, "um confirmar do P1 inicia, sem etapa do oponente"
    before = cs.ai_difficulty
    cs.cycle_ai_difficulty()
    assert cs.ai_difficulty == before, "a dificuldade do Arcade não vem desta tela"
    surf = pygame.Surface((1280, 720))
    from src.ui.fonts import get_title_font, get_text_font
    cs.render(surf, get_title_font(40), get_title_font(24), get_text_font(16))
    cs.arcade_mode = False
    cs.vs_ai = False
    assert cs.vs_ai is False
    print("  [OK] Seleção de personagem no Arcade: 1P travado, confirma de uma vez, sem mudar a dificuldade.", flush=True)


if __name__ == "__main__":
    test_tables_are_complete()
    test_ladder_for_all_fighters()
    test_ladder_order_and_seed()
    test_duel_bo3()
    test_challenges()
    test_continues_score_and_difficulty()
    test_scoring()
    test_full_simulated_journey()
    test_run_roundtrip_and_save()
    test_screens_render_in_both_languages()
    test_title_card_enabled()
    test_pause_menu_arcade_items()
    test_character_select_arcade_mode()
    print("Todos os testes do modo Arcade passaram.", flush=True)
