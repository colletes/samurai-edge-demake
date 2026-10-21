"""
Simulador de Balanceamento para 3 Arenas Selecionadas:
1. Sem Perigos (Zero Hazards): Floresta de Bambu (bamboo)
2. Perigo Médio (Medium Hazards): Gruta das Sombras (shadow_cave)
3. Kyoto Bakumatsu (2 Hazards - Carruagens e Destroços): Kyoto (kyoto)

Executa simulações de torneio completas em todas as 3 dificuldades (Easy, Normal, Hard)
com foco especial no rebalanceamento de evasão de projéteis e bombas da Kasumi.
Gera relatório detalhado em `docs/BALANCE_REPORT_3_ARENAS.md`.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import time
import json
from collections import defaultdict
import pygame

pygame.init()

from tools.simulate_tournament import (
    ROSTER, CHAR_IDS, CHAR_NAMES,
    run_full_tournament_simulation,
    run_merge_sort_tournament
)

ARENAS_3 = [
    ("Floresta de Bambu (Zero Hazards)", "bamboo"),
    ("Gruta das Sombras (Medium Hazard)", "shadow_cave"),
    ("Kyoto: Bakumatsu (High Hazards)", "kyoto")
]

def generate_3_arenas_report(all_results, output_path: str):
    """Gera relatório markdown detalhado da análise de balanceamento nas 3 arenas."""
    lines = []
    lines.append("# Relatório de Auditoria de Balanceamento — 3 Arenas Selecionadas")
    lines.append("")
    lines.append("> **Configuração da Auditoria**:")
    lines.append(f"> - **Arena 1 (Sem Perigos / Zero Hazards)**: Floresta de Bambu (`bamboo`)")
    lines.append(f"> - **Arena 2 (Perigo Médio / Medium Hazards)**: Gruta das Sombras (`shadow_cave`)")
    lines.append(f"> - **Arena 3 (Perigo Alto / Carruagens & Fogo)**: Kyoto Bakumatsu (`kyoto`)")
    lines.append(f"> - **Roster Testado**: {len(ROSTER)} Guerreiros (incluindo Daiki e Aoi)")
    lines.append(f"> - **Dificuldades da IA Auditadas**: Easy, Normal, Hard")
    lines.append(f"> - **Melhorias Aplicadas**: Evasão ativa de bombas da Kasumi, repulsão de minas/armadilhas, correção de sidestep perpendicular e janelas de esquiva calibradas.")
    lines.append("")

    # Seção 1: Desempenho Global (Normal)
    normal_data = all_results.get("normal")
    if normal_data:
        lines.append("## 1. Classificação Geral de Balanceamento (Dificuldade Normal)")
        lines.append("")
        lines.append("| Rank | Guerreiro | Winrate Geral | Vitórias | Derrotas | Empates | Bambu (0 Haz) | Gruta (Médio) | Kyoto (Carruagens) | Tier |")
        lines.append("|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")

        sorted_standings = sorted(normal_data["standings"], key=lambda s: s["winrate"], reverse=True)
        for rank, s in enumerate(sorted_standings, 1):
            wr = s["winrate"]
            b_wr = s["arena_stats"].get("Floresta de Bambu (Zero Hazards)", {}).get("winrate", 0.0)
            g_wr = s["arena_stats"].get("Gruta das Sombras (Medium Hazard)", {}).get("winrate", 0.0)
            k_wr = s["arena_stats"].get("Kyoto: Bakumatsu (High Hazards)", {}).get("winrate", 0.0)

            if wr >= 60.0:
                tier = "🔥 **Tier S**"
            elif wr >= 53.0:
                tier = "⚔️ **Tier A**"
            elif wr >= 47.0:
                tier = "⚖️ **Tier B (Equilibrado)**"
            elif wr >= 40.0:
                tier = "🛡️ **Tier C**"
            else:
                tier = "⚠️ **Tier D**"

            lines.append(f"| {rank} | **{s['name']}** | **{wr:.1f}%** | {s['wins']} | {s['losses']} | {s['draws']} | {b_wr:.1f}% | {g_wr:.1f}% | {k_wr:.1f}% | {tier} |")
        lines.append("")

    # Seção 2: Comparativo por Dificuldade (Easy vs Normal vs Hard)
    lines.append("## 2. Comparativo de Winrates entre Dificuldades (Easy vs Normal vs Hard)")
    lines.append("")
    lines.append("| Guerreiro | Winrate Easy | Winrate Normal | Winrate Hard | Variação (Hard - Easy) | Análise com Reações Avançadas |")
    lines.append("|:---|:---:|:---:|:---:|:---:|:---|")

    data_by_char = defaultdict(dict)
    for d in ["easy", "normal", "hard"]:
        if d in all_results:
            for s in all_results[d]["standings"]:
                data_by_char[s["id"]][d] = s["winrate"]

    avg_list = []
    for c_id in CHAR_IDS:
        wr_e = data_by_char[c_id].get("easy", 50.0)
        wr_n = data_by_char[c_id].get("normal", 50.0)
        wr_h = data_by_char[c_id].get("hard", 50.0)
        avg = (wr_e + wr_n + wr_h) / 3.0
        avg_list.append((avg, c_id, wr_e, wr_n, wr_h))

    avg_list.sort(reverse=True)
    for _, c_id, wr_e, wr_n, wr_h in avg_list:
        name = CHAR_NAMES[c_id]
        diff = wr_h - wr_e
        diff_str = f"+{diff:.1f}%" if diff > 0 else f"{diff:.1f}%"
        if diff > 4.0:
            analysis = "📈 Melhora expressiva com defesas e parries precisos"
        elif diff < -4.0:
            analysis = "📉 Mais punível contra oponentes com reflexos afiados"
        else:
            analysis = "⚖️ Desempenho estável em qualquer nível de habilidade"
        lines.append(f"| **{name}** | {wr_e:.1f}% | {wr_n:.1f}% | {wr_h:.1f}% | {diff_str} | {analysis} |")
    lines.append("")

    # Seção 3: Auditoria Específica de Kasumi e Evasão de Projéteis
    lines.append("## 3. Auditoria Específica: Bombas da Kasumi e Evasão de Projéteis")
    lines.append("")
    lines.append("Com as melhorias de IA:")
    lines.append("- **Não há mais saltos suicidas sobre bombas**: Golpes com deslocamento vertical e horizontal (`Ryuu Tsui Sen`, `Pole Vault`, `Gatotsu`, `Iai`, investidas melee) verificam se há bombas no trajeto antes de executar.")
    lines.append("- **Repulsão inteligente de solo**: A IA desvia seu caminho em 3.6m ao redor de bombas ticking, minas terrestres e armadilhas de urso.")
    lines.append("- **Esquiva de emergência (< 2.2m)**: Se uma bomba aterrissar colada ao lutador, ele executa rolamento ou dash imediato para longe ou em 90° perpendicular, nunca rolando na direção da explosão.")
    lines.append("- **Tratamento de projéteis não-bloqueáveis**: Bombas da Kasumi e balas de canhão da Anne nunca são alvo de tentativas ineficazes de parry; a IA prioriza exclusivamente rolamentos e dashes.")
    lines.append("")

    # Desempenho de Kasumi nos confrontos diretos
    if normal_data:
        h2h = normal_data["h2h_matrix"]
        kasumi_id = "gray_ninja"
        if kasumi_id in h2h:
            lines.append("### Desempenho Direto da Kasumi vs Guerreiros Notáveis (Normal):")
            lines.append("")
            lines.append("| Oponente | Vitórias Kasumi | Vitórias Oponente | Empates | Avaliação |")
            lines.append("|:---|:---:|:---:|:---:|:---|")
            for opp_id in ["kenshin", "musashi", "saitou", "daiki", "aoi", "rifleman", "kyudo_archer"]:
                if opp_id in h2h[kasumi_id]:
                    stat = h2h[kasumi_id][opp_id]
                    w_k = stat["wins"]
                    w_o = stat["losses"]
                    d = stat["draws"]
                    opp_name = CHAR_NAMES.get(opp_id, opp_id)
                    if w_k > w_o:
                        eval_str = "Vantagem tática de Kasumi (zoneamento efetivo)"
                    elif w_k < w_o:
                        eval_str = f"Vantagem de {opp_name} (esquiva e punição consistente)"
                    else:
                        eval_str = "Confronto equilibrado"
                    lines.append(f"| **{opp_name}** | {w_k} | {w_o} | {d} | {eval_str} |")
            lines.append("")

    # Seção 4: Impacto dos Perigos das 3 Arenas
    lines.append("## 4. Análise Comparativa de Impacto das 3 Arenas")
    lines.append("")
    lines.append("1. **Floresta de Bambu (Zero Hazards)**:")
    lines.append("   - Arena plana e pura de combate marcial. Zoners e duelistas de espada dependem estritamente de controle de distância e footsies.")
    lines.append("2. **Gruta das Sombras (Medium Hazard - Estalagmites)**:")
    lines.append("   - Perigos pontuais forçam reposicionamento. Lutadores de longo alcance se beneficiam do afunilamento de espaço.")
    lines.append("3. **Kyoto Bakumatsu (High Hazards - Carruagens em Chamas)**:")
    lines.append("   - A passagem contínua de carruagens em alta velocidade exige evasão perpendicular frequente. Combatentes ágeis (Kenshi, Okuni, Kasumi) tiram proveito de sua mobilidade superior.")
    lines.append("")

    content = "\n".join(lines)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n[OK] Relatório gravado com sucesso em '{output_path}'!")
    return content

def main():
    print("=" * 78)
    print(" INICIANDO AUDITORIA DE BALANCEAMENTO NAS 3 ARENAS")
    print(" Arenas: Floresta de Bambu (0 Haz), Gruta das Sombras (Médio), Kyoto (Alto)")
    print("=" * 78)

    difficulties = ["easy", "normal", "hard"]
    all_results = {}

    for diff in difficulties:
        print(f"\n>>>> Executando Torneio Headless [{diff.upper()}] <<<<")
        t_data = run_full_tournament_simulation(arena_list=ARENAS_3, difficulty=diff, battles_per_arena=2)
        m_roster, m_logs = run_merge_sort_tournament(t_data)
        t_data["merge_sorted_roster"] = m_roster
        t_data["merge_logs"] = m_logs
        all_results[diff] = t_data

    # Gerar relatório
    rep_path = "docs/BALANCE_REPORT_3_ARENAS.md"
    generate_3_arenas_report(all_results, rep_path)
    print("\nAuditoria concluída com sucesso em todas as 3 arenas e 3 dificuldades!")

if __name__ == "__main__":
    main()
