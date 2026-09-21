"""
Simulador Automatizado de Torneio e Merge Sort de Batalhas para Samurai Edge Demake.
Executa simulações headless com IA completa, gera estatísticas de balanceamento
e ordena os lutadores através de Merge Sort baseado em confrontos diretos.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
import time
import math
import random
import json
from collections import defaultdict
import pygame

pygame.init()
pygame.font.init()

from src.config import (
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_SAITOU,
    CHAR_RIFLE, CHAR_PURPLE, CHAR_GRAY, CHAR_KABUKI, CHAR_ARCHER,
    CHAR_PIRATE, CHAR_MUSKETEER
)
from src.world.map_data import GameMap
from src.isometric.camera import Camera
from src.combat.collision import CombatSystem
from src.entities.ai_controller import SamuraiAI
from src.entities.red_samurai import RedSamurai
from src.entities.saitou_samurai import SaitouSamurai
from src.entities.rifleman import Rifleman
from src.entities.kabuki import Kabuki
from src.entities.kyudo_archer import KyudoArcher
from src.entities.pirate import PirateSwordswoman
from src.entities.musketeer import Musketeer
from src.entities.pickups import PowderPouch
from main import get_random_arena_spawns, create_fighter

ROSTER = [
    {"id": CHAR_KENSHIN, "name": "Kenshin", "title": "Retalhador (Iai/Shukuchi)"},
    {"id": CHAR_MUSASHI, "name": "Musashi", "title": "Duas Lâminas (Combo/Parry)"},
    {"id": CHAR_NINJA, "name": "Hanzo", "title": "Ninja Mestre (Kunai)"},
    {"id": CHAR_AMERICAN, "name": "Joe", "title": "American Ninja (Shuriken/Cão)"},
    {"id": CHAR_SAITOU, "name": "Saitou", "title": "Lobo de Mibu (Gatotsu)"},
    {"id": CHAR_RIFLE, "name": "Teppo", "title": "Marksman (Tanegashima/Pólvora)"},
    {"id": CHAR_PURPLE, "name": "Murasaki", "title": "Kunoichi Foice (Kusarigama)"},
    {"id": CHAR_GRAY, "name": "Kasumi", "title": "Kunoichi Névoa (Bombas/Fumaça)"},
    {"id": CHAR_KABUKI, "name": "Okuni", "title": "Mestra dos Leques (Tessen/Kawarimi)"},
    {"id": CHAR_ARCHER, "name": "Tomoe", "title": "Arqueira Miko (Arco Yumi)"},
    {"id": CHAR_PIRATE, "name": "Anne", "title": "Espadachim (Alfanje 180°)"},
    {"id": CHAR_MUSKETEER, "name": "Julie", "title": "Mosqueteira (Florete/Riposte)"},
]

CHAR_IDS = [char["id"] for char in ROSTER]
CHAR_NAMES = {char["id"]: char["name"] for char in ROSTER}

def update_fighter(f, dt, game_map, particles, projectiles, powder_pouches=None):
    """Atualiza o lutador com os argumentos esperados pela sua subclasse."""
    if isinstance(f, Rifleman) and powder_pouches:
        f.check_powder_pickup(powder_pouches, particles)
    if isinstance(f, KyudoArcher):
        f.update(dt, game_map, particles, projectiles)
    elif isinstance(f, (RedSamurai, SaitouSamurai, Rifleman, Kabuki, PirateSwordswoman, Musketeer)):
        f.update(dt, game_map, particles)
    else:
        f.update(dt, game_map)

def simulate_single_battle(c1_id: str, c2_id: str, game_map: GameMap, max_time: float = 35.0, dt: float = 0.016):
    """
    Simula um duelo headless entre dois personagens controlados por IA.
    Retorna: (winner_char_id, fight_duration, win_reason)
    """
    cam = Camera(11.0, 11.0)
    combat = CombatSystem()
    ai1 = SamuraiAI()
    ai2 = SamuraiAI()

    (s1_x, s1_y), (s2_x, s2_y) = get_random_arena_spawns(game_map, min_distance=7.0)
    p1 = create_fighter(c1_id, s1_x, s1_y)
    p2 = create_fighter(c2_id, s2_x, s2_y)

    projectiles = []
    particles = []
    banners = []
    decoys = []
    powder_pouches = PowderPouch.create_arena_pouches(game_map, [p1, p2], total_pouches=3)

    elapsed = 0.0
    winner_result = None

    while elapsed < max_time and winner_result is None:
        # 1. Decisão e comandos da IA
        ai1.update(p1, p2, dt, game_map, projectiles, powder_pouches, decoys)
        ai2.update(p2, p1, dt, game_map, projectiles, powder_pouches, decoys)

        # 2. Atualização física dos lutadores e pouches
        for pouch in powder_pouches:
            pouch.update(dt, game_map, particles)
        update_fighter(p1, dt, game_map, particles, projectiles, powder_pouches)
        update_fighter(p2, dt, game_map, particles, projectiles, powder_pouches)

        # 3. Processamento de regras de combate e projéteis
        winner_result = combat.process_combat(p1, p2, game_map, particles, banners, cam, projectiles, dt, decoys=decoys)

        # 4. Limpeza periódica para manter pegada de memória mínima
        if len(particles) > 60:
            particles.clear()
        if len(banners) > 30:
            banners.clear()

        elapsed += dt

    if winner_result == "P1_WINS":
        return c1_id, elapsed, "FATAL_HIT"
    elif winner_result == "P2_WINS":
        return c2_id, elapsed, "FATAL_HIT"
    elif winner_result == "DRAW":
        return "DRAW", elapsed, "MUTUAL_DEATH"
    else:
        # Timeout: verifica HP restante se aplicável
        hp1 = getattr(p1, "hp", 0)
        hp2 = getattr(p2, "hp", 0)
        if hp1 > hp2:
            return c1_id, elapsed, "TIMEOUT_HP"
        elif hp2 > hp1:
            return c2_id, elapsed, "TIMEOUT_HP"
        return "DRAW", elapsed, "TIMEOUT_DRAW"

def run_matchup(c1_id: str, c2_id: str, game_map: GameMap, battles_per_match: int = 24):
    """
    Executa uma série de batalhas com simetria estrita (metade C1 como P1, metade C2 como P1).
    """
    wins_c1 = 0
    wins_c2 = 0
    draws = 0
    times = []

    half = battles_per_match // 2
    rem = battles_per_match - half

    # Rodada 1: c1 como P1, c2 como P2
    for _ in range(half):
        w, t, _ = simulate_single_battle(c1_id, c2_id, game_map)
        times.append(t)
        if w == c1_id:
            wins_c1 += 1
        elif w == c2_id:
            wins_c2 += 1
        else:
            draws += 1

    # Rodada 2: c2 como P1, c1 como P2
    for _ in range(rem):
        w, t, _ = simulate_single_battle(c2_id, c1_id, game_map)
        times.append(t)
        if w == c1_id:
            wins_c1 += 1
        elif w == c2_id:
            wins_c2 += 1
        else:
            draws += 1

    avg_time = sum(times) / len(times) if times else 0.0
    return {
        "c1": c1_id,
        "c2": c2_id,
        "c1_name": CHAR_NAMES[c1_id],
        "c2_name": CHAR_NAMES[c2_id],
        "wins_c1": wins_c1,
        "wins_c2": wins_c2,
        "draws": draws,
        "total_battles": battles_per_match,
        "avg_time": round(avg_time, 2)
    }

def run_full_tournament_simulation(battles_per_pair: int = 24):
    """
    Simula todas as combinações (C(12, 2) = 66 pares) com battles_per_pair batalhas cada.
    Total = 66 * 24 = 1.584 batalhas.
    """
    game_map = GameMap()
    n = len(CHAR_IDS)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((CHAR_IDS[i], CHAR_IDS[j]))

    total_pairs = len(pairs)
    total_battles = total_pairs * battles_per_pair

    print("=" * 78)
    print(f" INICIANDO SIMULAÇÃO DE TORNEIO HEADLESS AUTOMATIZADO")
    print(f" Roster: {n} Lutadores | Combinações: {total_pairs} | Lutas por Par: {battles_per_pair}")
    print(f" Total de Batalhas Simuladas: {total_battles}")
    print("=" * 78)

    matchups = {}
    h2h_matrix = defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "total": 0}))

    start_time = time.time()
    for idx, (c1, c2) in enumerate(pairs, 1):
        pair_key = f"{c1}_vs_{c2}"
        res = run_matchup(c1, c2, game_map, battles_per_match=battles_per_pair)
        matchups[pair_key] = res

        # Registrar na matriz bidirecional
        h2h_matrix[c1][c2]["wins"] += res["wins_c1"]
        h2h_matrix[c1][c2]["losses"] += res["wins_c2"]
        h2h_matrix[c1][c2]["draws"] += res["draws"]
        h2h_matrix[c1][c2]["total"] += res["total_battles"]

        h2h_matrix[c2][c1]["wins"] += res["wins_c2"]
        h2h_matrix[c2][c1]["losses"] += res["wins_c1"]
        h2h_matrix[c2][c1]["draws"] += res["draws"]
        h2h_matrix[c2][c1]["total"] += res["total_battles"]

        # Log de progresso a cada 6 pares ou no final
        if idx % 6 == 0 or idx == total_pairs:
            pct = (idx / total_pairs) * 100
            elapsed = time.time() - start_time
            print(f"[{idx:2d}/{total_pairs}] ({pct:5.1f}%) | {res['c1_name']:10s} vs {res['c2_name']:10s} -> "
                  f"{res['wins_c1']:2d} x {res['wins_c2']:2d} (Empates: {res['draws']}) | {elapsed:.1f}s decorridos")

    total_sim_time = time.time() - start_time
    print("-" * 78)
    print(f"Simulação concluída com sucesso em {total_sim_time:.2f} segundos!")
    print(f"Média por batalha: {(total_sim_time / total_battles)*1000:.2f} ms")
    print("=" * 78)

    # Calcular estatísticas agregadas de cada lutador
    standings = []
    for c_id in CHAR_IDS:
        total_w = sum(h2h_matrix[c_id][opp]["wins"] for opp in CHAR_IDS if opp != c_id)
        total_l = sum(h2h_matrix[c_id][opp]["losses"] for opp in CHAR_IDS if opp != c_id)
        total_d = sum(h2h_matrix[c_id][opp]["draws"] for opp in CHAR_IDS if opp != c_id)
        total_m = total_w + total_l + total_d
        winrate = (total_w / total_m) * 100 if total_m > 0 else 0.0

        standings.append({
            "id": c_id,
            "name": CHAR_NAMES[c_id],
            "wins": total_w,
            "losses": total_l,
            "draws": total_d,
            "total_matches": total_m,
            "winrate": round(winrate, 2)
        })

    return {
        "matchups": matchups,
        "h2h_matrix": h2h_matrix,
        "standings": standings,
        "total_battles": total_battles,
        "sim_time": round(total_sim_time, 2)
    }

# ==============================================================================
# ALGORITMO MERGE SORT DE BATALHAS SIMULADAS
# ==============================================================================
class MergeSortBattleTournament:
    """
    Implementa o Merge Sort clássico de ordenação, onde o operador de comparação
    entre dois lutadores A e B é baseado diretamente no resultado de confrontos diretos.
    """
    def __init__(self, h2h_matrix, standings_map):
        self.h2h_matrix = h2h_matrix
        self.standings_map = standings_map
        self.log_history = []
        self.comparison_count = 0

    def compare(self, c1: str, c2: str) -> bool:
        """
        Retorna True se c1 deve ficar à frente de c2 (c1 é mais forte que c2).
        Utiliza o confronto direto de 24 lutas entre c1 e c2.
        Em caso de empate no confronto direto, desempata pelo Winrate Geral no Torneio.
        """
        self.comparison_count += 1
        h2h = self.h2h_matrix[c1][c2]
        w1 = h2h["wins"]
        w2 = h2h["losses"]
        name1 = CHAR_NAMES[c1]
        name2 = CHAR_NAMES[c2]

        if w1 > w2:
            self.log_history.append(
                f"   [Duelo H2H #{self.comparison_count}] {name1} ({w1}v) venceu {name2} ({w2}v) -> {name1} avança"
            )
            return True
        elif w2 > w1:
            self.log_history.append(
                f"   [Duelo H2H #{self.comparison_count}] {name2} ({w2}v) venceu {name1} ({w1}v) -> {name2} avança"
            )
            return False
        else:
            # Desempate por Winrate Geral
            wr1 = self.standings_map[c1]["winrate"]
            wr2 = self.standings_map[c2]["winrate"]
            advances = wr1 >= wr2
            winner_name = name1 if advances else name2
            self.log_history.append(
                f"   [Duelo H2H #{self.comparison_count}] Empate H2H ({w1}x{w2})! Desempate por Winrate Geral: "
                f"{name1} ({wr1:.1f}%) vs {name2} ({wr2:.1f}%) -> {winner_name} avança"
            )
            return advances

    def merge_sort(self, items: list[str], depth: int = 0) -> list[str]:
        indent = "  " * depth
        if len(items) <= 1:
            return items

        mid = len(items) // 2
        left_items = items[:mid]
        right_items = items[mid:]

        self.log_history.append(
            f"{indent}[DIVISÃO Nível {depth}] Subdividindo {len(items)} lutadores: "
            f"{[CHAR_NAMES[x] for x in left_items]} | {[CHAR_NAMES[x] for x in right_items]}"
        )

        left_sorted = self.merge_sort(left_items, depth + 1)
        right_sorted = self.merge_sort(right_items, depth + 1)

        merged = self._merge(left_sorted, right_sorted, depth)
        self.log_history.append(
            f"{indent}[MERGE Nível {depth}] Resultado Intercalado: {[CHAR_NAMES[x] for x in merged]}"
        )
        return merged

    def _merge(self, left: list[str], right: list[str], depth: int) -> list[str]:
        result = []
        i = 0
        j = 0
        indent = "  " * depth

        while i < len(left) and j < len(right):
            c1 = left[i]
            c2 = right[j]
            if self.compare(c1, c2):
                result.append(c1)
                i += 1
            else:
                result.append(c2)
                j += 1

        while i < len(left):
            result.append(left[i])
            i += 1
        while j < len(right):
            result.append(right[j])
            j += 1

        return result

def run_merge_sort_tournament(tournament_data):
    """Executa o algoritmo Merge Sort sobre o roster de lutadores."""
    h2h_matrix = tournament_data["h2h_matrix"]
    standings_map = {s["id"]: s for s in tournament_data["standings"]}

    sorter = MergeSortBattleTournament(h2h_matrix, standings_map)
    # Embaralhar inicialmente ou usar a ordem inicial do roster
    initial_list = list(CHAR_IDS)
    print("\n" + "=" * 78)
    print(" EXECUTANDO ALGORITMO MERGE SORT DE BATALHAS SIMULADAS")
    print("=" * 78)
    print(f"Lista Inicial: {[CHAR_NAMES[x] for x in initial_list]}\n")

    sorted_roster = sorter.merge_sort(initial_list)

    for line in sorter.log_history:
        print(line)

    print("\n" + "=" * 78)
    print(" CLASSIFICAÇÃO FINAL VIA MERGE SORT DE BATALHAS")
    print("=" * 78)
    for rank, c_id in enumerate(sorted_roster, 1):
        s = standings_map[c_id]
        print(f"  {rank:2d}º Lugar: {s['name']:12s} | Winrate Geral: {s['winrate']:5.1f}% | "
              f"Cartel: {s['wins']:3d}V - {s['losses']:3d}D - {s['draws']:2d}E")
    print("=" * 78)

    return sorted_roster, sorter.log_history

def generate_balance_report(tournament_data, merge_sorted_roster, output_path: str = "BALANCE_REPORT.md"):
    """
    Gera um relatório completo e minucioso de balanceamento em Markdown.
    """
    standings_map = {s["id"]: s for s in tournament_data["standings"]}
    h2h_matrix = tournament_data["h2h_matrix"]
    matchups = tournament_data["matchups"]
    total_battles = tournament_data["total_battles"]
    sim_time = tournament_data["sim_time"]

    # Ordenar por winrate geral para exibição da Tier List
    sorted_by_wr = sorted(tournament_data["standings"], key=lambda x: x["winrate"], reverse=True)

    # Classificação em Tiers
    def get_tier(wr):
        if wr >= 70.0:
            return "S (Top Tier - Opressivo)"
        elif wr >= 55.0:
            return "A (Forte / Vantajoso)"
        elif wr >= 45.0:
            return "B (Balanceado / Saudável)"
        elif wr >= 30.0:
            return "C (Desfavorecido / Técnico)"
        return "D (Underpowered / Crítico)"

    lines = []
    lines.append("# Relatório Detalhado de Balanceamento & Merge Sort de Duelos Simulados")
    lines.append(f"\n> **Métricas Globais da Simulação**:")
    lines.append(f"> - Total de Guerreiros Avaliados: 12")
    lines.append(f"> - Combinações Únicas de Duelos: 66 confrontos $\\binom{{12}}{{2}}$")
    lines.append(f"> - Volume de Lutas por Combinação: 24 batalhas simétricas (12 com P1/P2 alternados)")
    lines.append(f"> - **Volume Total de Batalhas Simuladas**: **{total_battles} batalhas**")
    lines.append(f"> - Tempo Total de Simulação Física: {sim_time} segundos ({total_battles / sim_time:.1f} lutas/segundo)")
    lines.append("")

    lines.append("## 1. Tabela Geral de Desempenho & Tier List")
    lines.append("")
    lines.append("| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |")
    lines.append("|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|")
    for r, s in enumerate(sorted_by_wr, 1):
        char_info = next(c for c in ROSTER if c["id"] == s["id"])
        tier = get_tier(s["winrate"])
        lines.append(f"| {r} | **{s['name']}** | {char_info['title']} | {s['wins']} | {s['losses']} | {s['draws']} | **{s['winrate']:.1f}%** | {tier} |")
    lines.append("")

    lines.append("## 2. Matriz de Confrontos Head-to-Head (H2H 12x12)")
    lines.append("A tabela exibe a taxa percentual de vitórias da linha contra a coluna nas 24 lutas disputadas:")
    lines.append("")

    # Cabeçalho da matriz
    headers = ["Lutador"] + [c["name"][:6] for c in ROSTER]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join([":---"] + [":---:" for _ in ROSTER]) + "|")

    for c1 in ROSTER:
        row = [f"**{c1['name']}**"]
        for c2 in ROSTER:
            if c1["id"] == c2["id"]:
                row.append("—")
            else:
                rec = h2h_matrix[c1["id"]][c2["id"]]
                wr = (rec["wins"] / rec["total"]) * 100 if rec["total"] > 0 else 0
                row.append(f"{wr:.0f}%")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## 3. Resultado do Algoritmo Merge Sort de Duelos")
    lines.append("O Merge Sort executou uma ordenação por divisão e conquista onde cada decisão de precedência foi arbitrada pelo retrospecto direto de combates:")
    lines.append("")
    for r, c_id in enumerate(merge_sorted_roster, 1):
        s = standings_map[c_id]
        lines.append(f"{r}. **{s['name']}** — Winrate Geral: {s['winrate']:.1f}% ({s['wins']}V / {s['losses']}D / {s['draws']}E)")
    lines.append("")

    lines.append("## 4. Avaliação Técnica Aprofundada do Balanceamento")
    lines.append("")
    lines.append("### 4.1 Opressão e Dominância (Top Tiers)")
    top1 = sorted_by_wr[0]
    top2 = sorted_by_wr[1]
    lines.append(f"- **{top1['name']} ({top1['winrate']:.1f}%) & {top2['name']} ({top2['winrate']:.1f}%)**:")
    lines.append("  - As mecânicas de ataque com prioridade/precedência absoluta, alcance de projéteis instantâneos (snipers) ou frames defensivos de Parry/Riposte garantem uma taxa de vitória esmagadora contra lutadores de aproximação pura.")
    lines.append("")

    lines.append("### 4.2 Vulnerabilidades Críticas (Bottom Tiers)")
    bot1 = sorted_by_wr[-1]
    bot2 = sorted_by_wr[-2]
    lines.append(f"- **{bot1['name']} ({bot1['winrate']:.1f}%) & {bot2['name']} ({bot2['winrate']:.1f}%)**:")
    lines.append("  - Lutadores que dependem de tempos longos de recarga parada (ex: recarga do arcabuz sem cobertura móvel), auto-dano/suicídio por fogo amigo de explosivos, ou windup de retesamento de arco sofrem punições instantâneas contra oponentes rápidos.")
    lines.append("")

    lines.append("### 4.3 Dinâmica de Pedra-Papel-Tesoura e Polarização Extrema")
    polar_matchups = []
    for k, m in matchups.items():
        w1 = m["wins_c1"]
        w2 = m["wins_c2"]
        if w1 >= 21 or w2 >= 21: # >= 87.5% de vitórias
            winner = m["c1_name"] if w1 > w2 else m["c2_name"]
            loser = m["c2_name"] if w1 > w2 else m["c1_name"]
            polar_matchups.append(f"- **{winner} vs {loser}**: Placar esmagador de {max(w1, w2)} a {min(w1, w2)} ({max(w1, w2)/24*100:.1f}% de dominância)")

    if polar_matchups:
        lines.append("Foram detectados confrontos com polarização extrema (>= 87% de vitória para um lado):")
        for pm in polar_matchups[:8]:
            lines.append(pm)
    else:
        lines.append("Não foram detectados confrontos com polarização extrema superior a 87%.")
    lines.append("")

    lines.append("## 5. Propostas Concretas de Balance Patch (Recomendações de Design)")
    lines.append("Para equalizar o elenco e aproximar todos os combatentes da faixa saudável de 45% a 55% de winrate:")
    lines.append("1. **Ajuste de Precedência e Cooldowns de Projéteis**: Aumentar ligeiramente o recovery de golpes com prioridade e projéteis rápidos.")
    lines.append("2. **Mobilidade durante a Recarga**: Permitir que classes que recarregam mantenham movimentação a 50% da velocidade, evitando vulnerabilidade estática total.")
    lines.append("3. **Redução de Fogo Amigo**: Diminuir o raio de explosão auto-infligido para armas de área (como bombas).")
    lines.append("4. **Janela de Defesa (Parry/Riposte)**: Ajustar a janela de parry para exigir timing mais preciso contra sequências rápidas.")
    lines.append("")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nRelatório de balanceamento gravado com sucesso em '{output_path}'!")
    return content

def main():
    battles_per_pair = 24  # Garante >= 20 batalhas e simetria de spawns (12 P1, 12 P2)
    if len(sys.argv) > 1:
        try:
            battles_per_pair = int(sys.argv[1])
        except ValueError:
            pass

    tournament_data = run_full_tournament_simulation(battles_per_pair)
    merge_sorted_roster, merge_logs = run_merge_sort_tournament(tournament_data)

    # Exportar JSON bruto para persistência e auditoria
    export_payload = {
        "total_battles": tournament_data["total_battles"],
        "sim_time": tournament_data["sim_time"],
        "standings": tournament_data["standings"],
        "merge_sorted_roster": merge_sorted_roster,
        "matchups": tournament_data["matchups"]
    }
    with open("tournament_results.json", "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2, ensure_ascii=False)
    print("Dados brutos exportados para 'tournament_results.json'!")

    # Gerar Relatório Markdown
    generate_balance_report(tournament_data, merge_sorted_roster, "BALANCE_REPORT.md")

if __name__ == "__main__":
    main()
