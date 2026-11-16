"""
Avaliação Completa de Desempenho e Balanceamento por Personagem nas 24 Arenas.
Executa matriz de confrontos entre os 24 guerreiros distribuídos nas 24 arenas temáticas.
Gera estatísticas consolidadas por lutador, classificação por Tier e análise por categoria de arena.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import time
import math
from collections import defaultdict
import pygame

pygame.init()

from src.config import (
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_SAITOU,
    CHAR_RIFLE, CHAR_PURPLE, CHAR_GRAY, CHAR_KABUKI, CHAR_ARCHER,
    CHAR_PIRATE, CHAR_MUSKETEER, CHAR_REN, CHAR_CHIYO,
    CHAR_BENKEI, CHAR_ORIN, CHAR_GORO, CHAR_ICHI,
    CHAR_VALERIUS, CHAR_SEIMEI, CHAR_DAIKI, CHAR_AOI,
    CHAR_RAIDEN, CHAR_HENDRIKA,
)
from src.world.arenas import ARENA_SPECS, arena_ids, create_arena
from tools.simulate_tournament import simulate_single_battle, ROSTER, CHAR_NAMES, CHAR_IDS

ARENA_CATEGORIES = {
    "Zen": ["bamboo", "mountain_shrine", "mist_temple", "shaolin_temple", "higanbana_garden", "heian_shrine"],
    "Urban": ["kyoto", "yoshiwara_alley", "kabuki_stage", "baroque_court", "dejima_warehouse", "sacred_dohyo"],
    "Rural": ["nagashino_field", "forest_camp", "sacred_pines", "ezo_tundra", "rice_paddies", "rain_mill"],
    "Extreme": ["shadow_cave", "iga_rooftops", "pirate_deck", "ganryu_island", "gojo_bridge", "gothic_cemetery"],
}

# Inverso: arena_id -> categoria
ARENA_TO_CAT = {}
for cat, aids in ARENA_CATEGORIES.items():
    for aid in aids:
        ARENA_TO_CAT[aid] = cat

def run_character_balance_evaluation():
    all_arenas = arena_ids()
    n_chars = len(CHAR_IDS)
    pairs = []
    for i in range(n_chars):
        for j in range(i + 1, n_chars):
            pairs.append((CHAR_IDS[i], CHAR_IDS[j]))

    # Total de pares: 276. Com 2 lutas por par (P1/P2 alternados) = 552 lutas
    # Distribuídas uniformemente pelas 24 arenas (552 / 24 = 23 lutas por arena)
    print(f"================================================================================")
    print(f"  AVALIAÇÃO DE BALANCEAMENTO POR PERSONAGEM — SAMURAI EDGE")
    print(f"  24 Combatentes | 276 Pares x 2 Lutas = 552 Batalhas nas 24 Arenas")
    print(f"================================================================================\n")

    char_stats = defaultdict(lambda: {
        "wins": 0, "losses": 0, "draws": 0, "total": 0,
        "durations": [],
        "vs_opp": defaultdict(lambda: {"w": 0, "l": 0, "d": 0}),
        "cat_stats": defaultdict(lambda: {"w": 0, "l": 0, "d": 0, "total": 0})
    })

    t0 = time.perf_counter()

    for idx, (c1, c2) in enumerate(pairs):
        # Arena cíclica
        arena_id_1 = all_arenas[(idx * 2) % len(all_arenas)]
        arena_id_2 = all_arenas[(idx * 2 + 1) % len(all_arenas)]

        cat1 = ARENA_TO_CAT[arena_id_1]
        cat2 = ARENA_TO_CAT[arena_id_2]

        # Luta 1: C1 como P1
        m1 = create_arena(arena_id_1)
        w1, dur1, r1 = simulate_single_battle(c1, c2, m1, max_time=25.0)

        # Luta 2: C2 como P1
        m2 = create_arena(arena_id_2)
        w2, dur2, r2 = simulate_single_battle(c2, c1, m2, max_time=25.0)

        for w, dur, c_a, c_b, cat in ((w1, dur1, c1, c2, cat1), (w2, dur2, c1, c2, cat2)):
            char_stats[c_a]["total"] += 1
            char_stats[c_b]["total"] += 1
            char_stats[c_a]["durations"].append(dur)
            char_stats[c_b]["durations"].append(dur)
            char_stats[c_a]["cat_stats"][cat]["total"] += 1
            char_stats[c_b]["cat_stats"][cat]["total"] += 1

            if w == c_a:
                char_stats[c_a]["wins"] += 1
                char_stats[c_b]["losses"] += 1
                char_stats[c_a]["vs_opp"][c_b]["w"] += 1
                char_stats[c_b]["vs_opp"][c_a]["l"] += 1
                char_stats[c_a]["cat_stats"][cat]["w"] += 1
                char_stats[c_b]["cat_stats"][cat]["l"] += 1
            elif w == c_b:
                char_stats[c_b]["wins"] += 1
                char_stats[c_a]["losses"] += 1
                char_stats[c_b]["vs_opp"][c_a]["w"] += 1
                char_stats[c_a]["vs_opp"][c_b]["l"] += 1
                char_stats[c_b]["cat_stats"][cat]["w"] += 1
                char_stats[c_a]["cat_stats"][cat]["l"] += 1
            else:
                char_stats[c_a]["draws"] += 1
                char_stats[c_b]["draws"] += 1
                char_stats[c_a]["vs_opp"][c_b]["d"] += 1
                char_stats[c_b]["vs_opp"][c_a]["d"] += 1
                char_stats[c_a]["cat_stats"][cat]["d"] += 1
                char_stats[c_b]["cat_stats"][cat]["d"] += 1

    elapsed = time.perf_counter() - t0
    print(f">> 552 Batalhas simuladas com sucesso em {elapsed:.2f}s (~{552/elapsed:.1f} lutas/s) <<\n")

    # Ranking consolidado
    ranking = []
    for c_id in CHAR_IDS:
        st = char_stats[c_id]
        wr = (st["wins"] / st["total"]) * 100.0 if st["total"] > 0 else 0.0
        avg_dur = sum(st["durations"]) / len(st["durations"]) if st["durations"] else 0.0

        # Tier
        if wr >= 60.0:
            tier = "S (Dominante)"
        elif wr >= 53.0:
            tier = "A (Forte)"
        elif wr >= 47.0:
            tier = "B (Balanceado)"
        elif wr >= 40.0:
            tier = "C (Técnico)"
        else:
            tier = "D (Desafiador)"

        ranking.append({
            "id": c_id,
            "name": CHAR_NAMES[c_id],
            "wins": st["wins"],
            "losses": st["losses"],
            "draws": st["draws"],
            "total": st["total"],
            "winrate": wr,
            "tier": tier,
            "avg_dur": avg_dur,
            "cat_stats": st["cat_stats"],
            "vs_opp": st["vs_opp"]
        })

    ranking.sort(key=lambda x: x["winrate"], reverse=True)

    print("=" * 80)
    print(f"{'Pos':<4} {'Lutador':<14} {'Tier':<16} {'Winrate':<10} {'V - D - E':<14} {'Duração Média':<14}")
    print("=" * 80)

    for i, r in enumerate(ranking, 1):
        print(f"{i:02d}º  {r['name']:<14} {r['tier']:<16} {r['winrate']:5.1f}%     "
              f"{r['wins']:2d}V-{r['losses']:2d}D-{r['draws']:1d}E      {r['avg_dur']:4.1f}s")

    print("=" * 80)
    return ranking

if __name__ == "__main__":
    run_character_balance_evaluation()
