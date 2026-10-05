"""
Gera src/arcade/arcade_tables.py a partir de tournament_results.json (saída de simulate_tournament.py).

  ARCADE_TIER_ORDER   lutadores do mais fraco ao mais forte (taxa de vitória geral)
  ARCADE_MATCHUP_TABLE[a][b]   taxa de vitória (0..100) de `a` contra `b`

Uso: python3 tools/generate_arcade_tables.py [tournament_results.json]
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "src", "arcade", "arcade_tables.py")


def build(results: dict) -> tuple[list[str], dict[str, dict[str, float]]]:
    ids = [s["id"] for s in results["standings"]]
    rate = {s["id"]: s["winrate"] for s in results["standings"]}
    tier = sorted(ids, key=lambda i: (rate[i], ids.index(i)))
    table: dict[str, dict[str, float]] = {i: {} for i in ids}
    for m in results["matchups"].values():
        a, b, total = m["c1"], m["c2"], m["total_battles"]
        if not total:
            continue
        table[a][b] = round(100.0 * m["wins_c1"] / total, 2)
        table[b][a] = round(100.0 * m["wins_c2"] / total, 2)
    return tier, table


def render(tier: list[str], table: dict[str, dict[str, float]], source: str) -> str:
    lines = [f'"""Gerado por tools/generate_arcade_tables.py a partir de {source}. Não editar à mão."""', "",
             "ARCADE_TIER_ORDER = (" + ", ".join(repr(i) for i in tier) + ",)", "", "ARCADE_MATCHUP_TABLE = {"]
    for a in sorted(table):
        row = ", ".join(f"{b!r}: {v}" for b, v in sorted(table[a].items()))
        lines.append(f"    {a!r}: {{{row}}},")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "tournament_results.json")
    with open(src, encoding="utf-8") as f:
        results = json.load(f)
    tier, table = build(results)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(tier, table, os.path.basename(src)))
    print(f"{OUT}: {len(tier)} lutadores, {sum(len(r) for r in table.values())} confrontos")


if __name__ == "__main__":
    main()
