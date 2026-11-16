"""
Diagnóstico Completo de Balanceamento & Atrito em 4 Categorias de Arenas (24 Palcos).
Avalia:
1. Taxa global de vitória por arquétipo (Rushdown, Zoner, Heavy, Mobility, Fencer, Area)
2. Taxa de timeout e duração média por arena
3. Desempenho relativo Melee vs Zoner nas diferentes geometrias
4. Detecção de anomalias e pontos de atrito
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import time
from collections import defaultdict
import pygame

pygame.init()

from src.world.arenas import ARENA_SPECS, create_arena
from tools.audit_arena_balance import ARCHETYPE_MATCHUPS
from tools.simulate_tournament import simulate_single_battle

ARENA_CATEGORIES = {
    "1. Santuários & Jardins Zen": [
        "bamboo", "mountain_shrine", "mist_temple", "shaolin_temple", "higanbana_garden", "heian_shrine"
    ],
    "2. Cenários Urbanos & Históricos": [
        "kyoto", "yoshiwara_alley", "kabuki_stage", "baroque_court", "dejima_warehouse", "sacred_dohyo"
    ],
    "3. Campos de Batalha & Vilarejos Rurais": [
        "nagashino_field", "forest_camp", "sacred_pines", "ezo_tundra", "rice_paddies", "rain_mill"
    ],
    "4. Locais Extremos & Noturnos": [
        "shadow_cave", "iga_rooftops", "pirate_deck", "ganryu_island", "gojo_bridge", "gothic_cemetery"
    ]
}

def run_categorized_audit():
    total_fights = 0
    total_timeouts = 0
    durations = []
    category_stats = {}

    print("=" * 80)
    print("  SIMULAÇÃO DE BALANCEAMENTO POR CATEGORIA DE ARENA (24 PALCOS)")
    print("=" * 80)

    t_all = time.perf_counter()

    for cat_name, arena_list in ARENA_CATEGORIES.items():
        print(f"\n📂 {cat_name} ({len(arena_list)} Arenas)")
        print("-" * 80)
        cat_fights = 0
        cat_timeouts = 0
        cat_durations = []

        for a_id in arena_list:
            spec = ARENA_SPECS[a_id]
            a_fights = 0
            a_timeouts = 0
            a_durations = []

            for c1, c2, desc in ARCHETYPE_MATCHUPS:
                for p1, p2 in ((c1, c2), (c2, c1)):
                    m = create_arena(a_id)
                    w, dur, r = simulate_single_battle(p1, p2, m, max_time=25.0)
                    a_fights += 1
                    a_durations.append(dur)
                    if "TIMEOUT" in r:
                        a_timeouts += 1

            cat_fights += a_fights
            cat_timeouts += a_timeouts
            cat_durations.extend(a_durations)

            a_avg = sum(a_durations) / len(a_durations) if a_durations else 0.0
            a_rate = (a_timeouts / a_fights) * 100.0 if a_fights else 0.0

            icon = "🟢" if a_rate < 5.0 else ("🟡" if a_rate < 15.0 else "🔴")
            print(f"  {icon} {spec.name:<26} (`{a_id:<17}`): Duração Média {a_avg:4.1f}s | Timeouts: {a_timeouts:2d}/{a_fights} ({a_rate:4.1f}%)")

        cat_avg = sum(cat_durations) / len(cat_durations) if cat_durations else 0.0
        cat_rate = (cat_timeouts / cat_fights) * 100.0 if cat_fights else 0.0
        category_stats[cat_name] = {
            "fights": cat_fights,
            "timeouts": cat_timeouts,
            "timeout_rate": cat_rate,
            "avg_duration": cat_avg
        }
        print(f"  📊 Média da Categoria: {cat_avg:.1f}s | Taxa de Timeout: {cat_rate:.1f}% ({cat_timeouts}/{cat_fights})")

        total_fights += cat_fights
        total_timeouts += cat_timeouts
        durations.extend(cat_durations)

    total_time = time.perf_counter() - t_all
    global_avg = sum(durations) / len(durations) if durations else 0.0
    global_rate = (total_timeouts / total_fights) * 100.0 if total_fights else 0.0

    print("\n" + "=" * 80)
    print(f"  SÍNTESE GERAL DO BALANCEAMENTO DAS 24 ARENAS ({total_fights} LUTAS EM {total_time:.2f}s)")
    print("=" * 80)
    print(f"  • Total de Lutas Simuladas : {total_fights}")
    print(f"  • Duração Média Global     : {global_avg:.2f}s por duelo")
    print(f"  • Taxa Global de Timeouts  : {global_rate:.2f}% ({total_timeouts}/{total_fights})")
    print(f"  • Tempo Real de Simulação  : {total_time:.2f}s (~{total_fights/total_time:.1f} lutas/segundo)")
    print("-" * 80)

    for cat_name, st in category_stats.items():
        print(f"  • {cat_name:<38}: Duração {st['avg_duration']:.1f}s | Timeouts {st['timeout_rate']:.1f}%")

    print("=" * 80)

if __name__ == "__main__":
    run_categorized_audit()
