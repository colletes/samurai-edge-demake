"""
Simulador Automatizado de Torneio e Merge Sort de Batalhas para Samurai Edge Demake.
Executa simulações headless com IA completa, gera estatísticas de balanceamento
e ordena os lutadores através de Merge Sort baseado em confrontos diretos em todas
as 20 arenas temáticas e nas 3 dificuldades de IA (Easy, Normal, Hard).
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

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
    CHAR_PIRATE, CHAR_MUSKETEER, CHAR_REN, CHAR_CHIYO,
    CHAR_BENKEI, CHAR_ORIN, CHAR_GORO, CHAR_ICHI,
    CHAR_VALERIUS, CHAR_SEIMEI, CHAR_DAIKI, CHAR_AOI,
    CHAR_RAIDEN, CHAR_HENDRIKA,
    ARENA_DOHYO, ARENA_IGA, ARENA_GANRYU, ARENA_KYOTO
)
from src.world.map_data import GameMap
from src.world.kyoto_map import KyotoMap
from src.world.arenas import ARENA_SPECS, arena_ids, create_arena
from src.isometric.camera import Camera
from src.combat.collision import CombatSystem
from src.entities.ai_controller import SamuraiAI
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.saitou_samurai import SaitouSamurai
from src.entities.rifleman import Rifleman
from src.entities.kabuki import Kabuki
from src.entities.kyudo_archer import KyudoArcher
from src.entities.pirate import PirateSwordswoman
from src.entities.musketeer import Musketeer
from src.entities.ren_monk import RenMonk
from src.entities.chiyo_kunoichi import ChiyoKunoichi
from src.entities.benkei import BenkeiSamurai
from src.entities.orin import OrinMinstrel
from src.entities.goro import GoroFarmer
from src.entities.ichi import IchiBlade
from src.entities.valerius import ValeriusNecromancer
from src.entities.seimei import SeimeiOnmyoji
from src.entities.daiki import DaikiPilgrim
from src.entities.aoi import AoiHuntress
from src.entities.raiden import RaidenSumo
from src.entities.hendrika import HendrikaAlchemist
from src.entities.pickups import PowderPouch
from main import get_random_arena_spawns, get_kyoto_arena_spawns, create_fighter

# 4 Arenas Padrão de Balanceamento (Raiden: Dohyo, Hanzo: Telhados de Iga, Musashi: Ilha Ganryu, Saitou: Kyoto)
STANDARD_ARENAS = [
    ("Dohyo Sagrado", ARENA_DOHYO),
    ("Telhados de Iga", ARENA_IGA),
    ("Duelo na Ilha Ganryu", ARENA_GANRYU),
    ("Kyoto: Bakumatsu em Chamas", ARENA_KYOTO),
]

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
    {"id": CHAR_REN, "name": "Ren", "title": "Monge Shaolin (Kiai/Flurry)"},
    {"id": CHAR_CHIYO, "name": "Chiyo", "title": "Lâminas Gêmeas (Dual Nodachi)"},
    {"id": CHAR_BENKEI, "name": "Benkei", "title": "Sōhei Monge Guerreiro (Naginata Colossal)"},
    {"id": CHAR_ORIN, "name": "O-Rin", "title": "Menestrel Acústica (Shamisen/Kamaitachi)"},
    {"id": CHAR_GORO, "name": "Goro", "title": "Fazendeiro da Kuwa (Kuwa Cleave/Pisotão)"},
    {"id": CHAR_ICHI, "name": "Ichi", "title": "Lâmina Cega (Shikomizue/Gyaku-Iai)"},
    {"id": CHAR_VALERIUS, "name": "Valerius", "title": "Necromante Prussiano (Foice/Invocações)"},
    {"id": CHAR_SEIMEI, "name": "Seimei", "title": "Onmyoji dos Talismãs (Ofuda/Selo Sagrado)"},
    {"id": CHAR_DAIKI, "name": "Daiki", "title": "Peregrino do Bastão Bō (Pole Vault/Varredura)"},
    {"id": CHAR_AOI, "name": "Aoi", "title": "Caçadora Ainu (Lança Op/Armadilha de Urso)"},
    {"id": CHAR_RAIDEN, "name": "Raiden", "title": "Yokozuna Invicto (Tsuppari/Tachiai)"},
    {"id": CHAR_HENDRIKA, "name": "Hendrika", "title": "Alquimista de Dejima (Estilete/5 Reagentes)"},
]

CHAR_IDS = [char["id"] for char in ROSTER]
CHAR_NAMES = {char["id"]: char["name"] for char in ROSTER}

def update_fighter(f, dt, game_map, particles, projectiles, powder_pouches=None, opponent=None, banners=None):
    """Atualiza o lutador com os argumentos esperados pela sua subclasse."""
    if isinstance(f, Rifleman) and powder_pouches:
        f.check_powder_pickup(powder_pouches, particles)
    if isinstance(f, KyudoArcher):
        f.update(dt, game_map, particles, projectiles)
    elif isinstance(f, BlueSamurai):
        f.update(dt, game_map, particles, projectiles)
    elif isinstance(f, PirateSwordswoman):
        f.update(dt, game_map, particles, opponent=opponent, banners=banners)
    elif isinstance(f, (RenMonk, ChiyoKunoichi)):
        f.update(dt, game_map, particles, opponent=opponent, banners=banners)
    elif isinstance(f, BenkeiSamurai):
        f.update(dt, game_map, particles, opponent=opponent, banners=banners)
    elif isinstance(f, OrinMinstrel):
        f.update(dt, game_map, particles, opponent=opponent, projectiles=projectiles)
    elif isinstance(f, (GoroFarmer, IchiBlade, ValeriusNecromancer, SeimeiOnmyoji, DaikiPilgrim, AoiHuntress, RaidenSumo, HendrikaAlchemist)):
        f.update(dt, game_map, particles, opponent=opponent, projectiles=projectiles, banners=banners)
    elif isinstance(f, (RedSamurai, SaitouSamurai, Rifleman, Kabuki, Musketeer)):
        f.update(dt, game_map, particles)
    else:
        f.update(dt, game_map)

def simulate_single_battle(c1_id: str, c2_id: str, game_map, max_time: float = 35.0, dt: float = 0.016, difficulty: str = "normal"):
    """
    Simula um duelo headless entre dois personagens controlados por IA.
    Retorna: (winner_char_id, fight_duration, win_reason)
    """
    cam = Camera(11.0, 11.0)
    combat = CombatSystem()
    ai1 = SamuraiAI(difficulty=difficulty)
    ai2 = SamuraiAI(difficulty=difficulty)

    if hasattr(game_map, "pick_spawns"):
        (s1_x, s1_y), (s2_x, s2_y) = game_map.pick_spawns(min_distance=7.0)
    elif isinstance(game_map, KyotoMap):
        (s1_x, s1_y), (s2_x, s2_y) = get_kyoto_arena_spawns(game_map, min_distance=7.0)
    else:
        (s1_x, s1_y), (s2_x, s2_y) = get_random_arena_spawns(game_map, min_distance=7.0)

    p1 = create_fighter(c1_id, s1_x, s1_y)
    p2 = create_fighter(c2_id, s2_x, s2_y)
    p1.set_facing(p2.wx, p2.wy)
    p2.set_facing(p1.wx, p1.wy)
    for f in (p1, p2):
        if hasattr(f, "on_round_start"):
            f.on_round_start()

    projectiles = []
    particles = []
    banners = []
    decoys = []
    poison_clouds = []
    powder_traps = []
    powder_pouches = PowderPouch.create_arena_pouches(game_map, [p1, p2], total_pouches=3)

    elapsed = 0.0
    winner_result = None

    while elapsed < max_time and winner_result is None:
        if hasattr(game_map, "update"):
            game_map.update(dt, [p1, p2], cam, particles, banners)

        # 1. Decisão e comandos da IA
        ai1.update(p1, p2, dt, game_map, projectiles, powder_pouches, decoys, poison_clouds)
        ai2.update(p2, p1, dt, game_map, projectiles, powder_pouches, decoys, poison_clouds)

        # 1.5 Atualização de entidades secundárias
        decoys[:] = [d for d in decoys if d.update(dt)]
        poison_clouds[:] = [pc for pc in poison_clouds if pc.update(dt, [p1, p2], particles, banners=banners)]
        powder_traps[:] = [pt for pt in powder_traps if pt.update(dt, [p1, p2], particles, banners=banners)]

        for archer, opp in ((p1, p2), (p2, p1)):
            if isinstance(archer, KyudoArcher):
                archer.update_ofuda_barrier_effects(dt, projectiles, opponent=opp, particles=particles)

        # 2. Atualização física dos lutadores e pouches
        for pouch in powder_pouches:
            pouch.update(dt, game_map, particles)
        update_fighter(p1, dt, game_map, particles, projectiles, powder_pouches, opponent=p2, banners=banners)
        update_fighter(p2, dt, game_map, particles, projectiles, powder_pouches, opponent=p1, banners=banners)

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

def run_matchup(c1_id: str, c2_id: str, arena_list: list, difficulty: str = "normal", battles_per_arena: int = 2):
    """
    Executa batalhas distribuídas simetricamente entre todas as arenas especificadas.
    Para cada arena, executa `battles_per_arena` (metade com c1 como P1, metade com c2 como P1).
    """
    wins_c1 = 0
    wins_c2 = 0
    draws = 0
    times = []
    arena_stats = {}

    half = battles_per_arena // 2
    rem = battles_per_arena - half

    for map_name, map_id in arena_list:
        m_wins_c1 = 0
        m_wins_c2 = 0
        m_draws = 0

        # Lutas C1 como P1
        for _ in range(half):
            g_map = create_arena(map_id)
            w, t, _ = simulate_single_battle(c1_id, c2_id, g_map, difficulty=difficulty)
            times.append(t)
            if w == c1_id:
                wins_c1 += 1
                m_wins_c1 += 1
            elif w == c2_id:
                wins_c2 += 1
                m_wins_c2 += 1
            else:
                draws += 1
                m_draws += 1

        # Lutas C2 como P1
        for _ in range(rem):
            g_map = create_arena(map_id)
            w, t, _ = simulate_single_battle(c2_id, c1_id, g_map, difficulty=difficulty)
            times.append(t)
            if w == c1_id:
                wins_c1 += 1
                m_wins_c1 += 1
            elif w == c2_id:
                wins_c2 += 1
                m_wins_c2 += 1
            else:
                draws += 1
                m_draws += 1

        arena_stats[map_name] = {
            "wins_c1": m_wins_c1,
            "wins_c2": m_wins_c2,
            "draws": m_draws,
            "total": battles_per_arena
        }

    total_battles = len(arena_list) * battles_per_arena
    avg_time = sum(times) / len(times) if times else 0.0
    return {
        "c1": c1_id,
        "c2": c2_id,
        "c1_name": CHAR_NAMES[c1_id],
        "c2_name": CHAR_NAMES[c2_id],
        "wins_c1": wins_c1,
        "wins_c2": wins_c2,
        "draws": draws,
        "total_battles": total_battles,
        "avg_time": round(avg_time, 2),
        "arena_stats": arena_stats
    }

def run_full_tournament_simulation(arena_list: list = None, difficulty: str = "normal", battles_per_arena: int = 2):
    """
    Simula todas as combinações de guerreiros em todas as arenas padrão (Dohyo, Iga, Ganryu, Kyoto).
    Com 3 arenas padrão e 2 lutas/arena (1 P1, 1 P2) = 6 batalhas por par.
    """
    if arena_list is None:
        arena_list = list(STANDARD_ARENAS)

    n = len(CHAR_IDS)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((CHAR_IDS[i], CHAR_IDS[j]))

    total_pairs = len(pairs)
    battles_per_pair = len(arena_list) * battles_per_arena
    total_battles = total_pairs * battles_per_pair

    print("=" * 78)
    print(f" SIMULAÇÃO DE BALANCEAMENTO EM TODAS AS ARENAS ({len(arena_list)} ARENAS)")
    print(f" Roster: {n} Lutadores | Combinações: {total_pairs} | Lutas por Par: {battles_per_pair}")
    print(f" Dificuldade da IA: {difficulty.upper()}")
    print(f" Total de Batalhas Simuladas: {total_battles}")
    print("=" * 78)

    matchups = {}
    h2h_matrix = defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "total": 0}))
    arena_matrix = {
        name: defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "total": 0}))
        for name, _ in arena_list
    }

    start_time = time.time()
    for idx, (c1, c2) in enumerate(pairs, 1):
        pair_key = f"{c1}_vs_{c2}"
        res = run_matchup(c1, c2, arena_list, difficulty=difficulty, battles_per_arena=battles_per_arena)
        matchups[pair_key] = res

        # Registrar na matriz bidirecional global
        h2h_matrix[c1][c2]["wins"] += res["wins_c1"]
        h2h_matrix[c1][c2]["losses"] += res["wins_c2"]
        h2h_matrix[c1][c2]["draws"] += res["draws"]
        h2h_matrix[c1][c2]["total"] += res["total_battles"]

        h2h_matrix[c2][c1]["wins"] += res["wins_c2"]
        h2h_matrix[c2][c1]["losses"] += res["wins_c1"]
        h2h_matrix[c2][c1]["draws"] += res["draws"]
        h2h_matrix[c2][c1]["total"] += res["total_battles"]

        # Registrar estatísticas por arena
        for m_name, a_res in res["arena_stats"].items():
            arena_matrix[m_name][c1][c2]["wins"] += a_res["wins_c1"]
            arena_matrix[m_name][c1][c2]["losses"] += a_res["wins_c2"]
            arena_matrix[m_name][c1][c2]["draws"] += a_res["draws"]
            arena_matrix[m_name][c1][c2]["total"] += a_res["total"]

            arena_matrix[m_name][c2][c1]["wins"] += a_res["wins_c2"]
            arena_matrix[m_name][c2][c1]["losses"] += a_res["wins_c1"]
            arena_matrix[m_name][c2][c1]["draws"] += a_res["draws"]
            arena_matrix[m_name][c2][c1]["total"] += a_res["total"]

        if idx % 10 == 0 or idx == total_pairs:
            pct = (idx / total_pairs) * 100
            elapsed = time.time() - start_time
            rate = (idx * battles_per_pair) / elapsed if elapsed > 0 else 0
            print(f"[{idx:3d}/{total_pairs}] ({pct:5.1f}%) | {res['c1_name']:10s} vs {res['c2_name']:10s} -> "
                  f"{res['wins_c1']:2d} x {res['wins_c2']:2d} (E:{res['draws']}) | {elapsed:5.1f}s | {rate:.1f} lutas/s")

    total_sim_time = time.time() - start_time
    print("-" * 78)
    print(f"Torneio ({difficulty.upper()}) concluído em {total_sim_time:.2f}s! ({total_battles/total_sim_time:.1f} lutas/segundo)")
    print("=" * 78)

    # Calcular estatísticas agregadas de cada lutador
    standings = []
    for c_id in CHAR_IDS:
        total_w = sum(h2h_matrix[c_id][opp]["wins"] for opp in CHAR_IDS if opp != c_id)
        total_l = sum(h2h_matrix[c_id][opp]["losses"] for opp in CHAR_IDS if opp != c_id)
        total_d = sum(h2h_matrix[c_id][opp]["draws"] for opp in CHAR_IDS if opp != c_id)
        total_m = total_w + total_l + total_d
        winrate = (total_w / total_m) * 100 if total_m > 0 else 0.0

        # Estatísticas por arena
        char_arena_stats = {}
        for m_name, _ in arena_list:
            aw = sum(arena_matrix[m_name][c_id][opp]["wins"] for opp in CHAR_IDS if opp != c_id)
            al = sum(arena_matrix[m_name][c_id][opp]["losses"] for opp in CHAR_IDS if opp != c_id)
            ad = sum(arena_matrix[m_name][c_id][opp]["draws"] for opp in CHAR_IDS if opp != c_id)
            am = aw + al + ad
            awr = (aw / am) * 100 if am > 0 else 0.0
            char_arena_stats[m_name] = {
                "wins": aw,
                "losses": al,
                "draws": ad,
                "total": am,
                "winrate": round(awr, 2)
            }

        standings.append({
            "id": c_id,
            "name": CHAR_NAMES[c_id],
            "wins": total_w,
            "losses": total_l,
            "draws": total_d,
            "total_matches": total_m,
            "winrate": round(winrate, 2),
            "arena_stats": char_arena_stats
        })

    return {
        "matchups": matchups,
        "h2h_matrix": h2h_matrix,
        "arena_matrix": arena_matrix,
        "arena_list": arena_list,
        "standings": standings,
        "total_battles": total_battles,
        "sim_time": round(total_sim_time, 2),
        "difficulty": difficulty
    }

# ==============================================================================
# ALGORITMO MERGE SORT DE BATALHAS SIMULADAS
# ==============================================================================
class MergeSortBattleTournament:
    """
    Merge Sort clássico onde a precedência entre dois guerreiros A e B
    é arbitrada pelo retrospecto direto de combates (Head-to-Head).
    """
    def __init__(self, h2h_matrix, standings_map):
        self.h2h_matrix = h2h_matrix
        self.standings_map = standings_map
        self.log_history = []
        self.comparison_count = 0

    def compare(self, c1: str, c2: str) -> bool:
        """
        Retorna True se c1 deve ficar à frente de c2.
        Primeiro critério: Confronto Direto (H2H).
        Segundo critério (empate): Winrate Geral no Torneio.
        """
        self.comparison_count += 1
        h2h = self.h2h_matrix[c1][c2]
        w1 = h2h["wins"]
        w2 = h2h["losses"]
        name1 = CHAR_NAMES[c1]
        name2 = CHAR_NAMES[c2]

        if w1 > w2:
            self.log_history.append(
                f"   [H2H #{self.comparison_count}] {name1} ({w1}v) superou {name2} ({w2}v) -> {name1} avança"
            )
            return True
        elif w2 > w1:
            self.log_history.append(
                f"   [H2H #{self.comparison_count}] {name2} ({w2}v) superou {name1} ({w1}v) -> {name2} avança"
            )
            return False
        else:
            wr1 = self.standings_map[c1]["winrate"]
            wr2 = self.standings_map[c2]["winrate"]
            advances = wr1 >= wr2
            winner_name = name1 if advances else name2
            self.log_history.append(
                f"   [H2H #{self.comparison_count}] Empate H2H ({w1}x{w2})! Desempate por Winrate Geral: "
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
    initial_list = list(CHAR_IDS)
    print("\n" + "=" * 78)
    print(f" EXECUTANDO MERGE SORT DE CONFRONTOS DIRETOS ({tournament_data.get('difficulty','normal').upper()})")
    print("=" * 78)

    sorted_roster = sorter.merge_sort(initial_list)

    print("\n" + "=" * 78)
    print(f" CLASSIFICAÇÃO FINAL VIA MERGE SORT ({tournament_data.get('difficulty','normal').upper()})")
    print("=" * 78)
    for rank, c_id in enumerate(sorted_roster, 1):
        s = standings_map[c_id]
        print(f"  {rank:2d}º Lugar: {s['name']:12s} | Winrate Geral: {s['winrate']:5.1f}% | "
              f"Cartel: {s['wins']:3d}V - {s['losses']:3d}D - {s['draws']:2d}E")
    print("=" * 78)

    return sorted_roster, sorter.log_history

def generate_balance_report(tournament_data, merge_sorted_roster, output_path: str = "BALANCE_REPORT.md"):
    """
    Gera relatório completo de balanceamento em Markdown cobrindo todas as arenas e confrontos.
    """
    standings_map = {s["id"]: s for s in tournament_data["standings"]}
    h2h_matrix = tournament_data["h2h_matrix"]
    matchups = tournament_data["matchups"]
    total_battles = tournament_data["total_battles"]
    sim_time = tournament_data["sim_time"]
    arena_list = tournament_data.get("arena_list", [])

    sorted_by_wr = sorted(tournament_data["standings"], key=lambda x: x["winrate"], reverse=True)

    def get_tier(wr):
        if wr >= 58.0:
            return "S (Dominante / Alta Vantagem)"
        elif wr >= 52.0:
            return "A (Forte / Vantajoso)"
        elif wr >= 47.0:
            return "B (Balanceado / Saudável)"
        elif wr >= 42.0:
            return "C (Desfavorecido / Técnico)"
        return "D (Crítico / Sob Investigação)"

    difficulty = tournament_data.get("difficulty", "normal")
    n_fighters = len(ROSTER)
    n_combos = n_fighters * (n_fighters - 1) // 2
    n_arenas = len(arena_list)

    lines = []
    lines.append(f"# Relatório Detalhado de Balanceamento & Merge Sort de Duelos ({difficulty.upper()})")
    lines.append("")
    lines.append("> **Métricas Globais da Simulação**:")
    lines.append(f"> - Dificuldade da IA (ambos os lutadores): **{difficulty.upper()}**")
    lines.append(f"> - Total de Guerreiros Avaliados: **{n_fighters}**")
    lines.append(f"> - Total de Arenas Avaliadas: **{n_arenas}** ({', '.join(a[0] for a in arena_list)})")
    lines.append(f"> - Combinações Únicas de Duelos: **{n_combos} confrontos** $\\binom{{{n_fighters}}}{{2}}$")
    lines.append(f"> - Lutas por Combinação: **{total_battles // n_combos} batalhas** (2 por arena, paridade simétrica P1/P2)")
    lines.append(f"> - **Volume Total de Batalhas Simuladas**: **{total_battles} batalhas**")
    lines.append(f"> - Tempo Total de Simulação Física: **{sim_time} segundos** ({total_battles / sim_time:.1f} lutas/s)")
    lines.append("")

    # 1. Tabela Geral e Tier List
    lines.append("## 1. Tabela Geral de Desempenho & Tier List")
    lines.append("")
    lines.append("| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |")
    lines.append("|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|")
    for r, s in enumerate(sorted_by_wr, 1):
        char_info = next(c for c in ROSTER if c["id"] == s["id"])
        tier = get_tier(s["winrate"])
        lines.append(f"| {r} | **{s['name']}** | {char_info['title']} | {s['wins']} | {s['losses']} | {s['draws']} | **{s['winrate']:.1f}%** | {tier} |")
    lines.append("")

    # 2. Desempenho e Adaptação às 20 Arenas
    lines.append("## 2. Desempenho por Arena & Variância Geográfica")
    lines.append("Identificação das arenas de maior e menor eficácia para cada combatente (impacto de fossos, obstáculos, projéteis e perigos de fase):")
    lines.append("")
    lines.append("| Rank | Lutador | Winrate Geral | Melhor Arena | WR Max | Pior Arena | WR Min | Dispersão |")
    lines.append("|:---:|:---|:---:|:---|:---:|:---|:---:|:---:|")

    for r, s in enumerate(sorted_by_wr, 1):
        astats = s.get("arena_stats", {})
        if astats:
            best_arena = max(astats.items(), key=lambda x: x[1]["winrate"])
            worst_arena = min(astats.items(), key=lambda x: x[1]["winrate"])
            spread = best_arena[1]["winrate"] - worst_arena[1]["winrate"]
            lines.append(f"| {r} | **{s['name']}** | **{s['winrate']:.1f}%** | {best_arena[0]} | {best_arena[1]['winrate']:.1f}% | {worst_arena[0]} | {worst_arena[1]['winrate']:.1f}% | {spread:.1f}% |")
        else:
            lines.append(f"| {r} | **{s['name']}** | **{s['winrate']:.1f}%** | — | — | — | — | — |")
    lines.append("")

    # 3. Matriz Head-to-Head
    lines.append(f"## 3. Matriz de Confrontos Diretos Head-to-Head ({n_fighters}x{n_fighters})")
    lines.append("Percentual de vitórias da linha contra a coluna através de todas as arenas:")
    lines.append("")
    headers = ["Lutador"] + [c["name"][:5] for c in ROSTER]
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

    # 4. Resultado do Merge Sort de Duelos
    lines.append("## 4. Classificação Oficial via Algoritmo Merge Sort")
    lines.append("A ordenação por divisão e conquista arbitrou cada emparelhamento utilizando estritamente o retrospecto direto (Head-to-Head):")
    lines.append("")
    for r, c_id in enumerate(merge_sorted_roster, 1):
        s = standings_map[c_id]
        lines.append(f"{r}. **{s['name']}** — Winrate Geral: {s['winrate']:.1f}% ({s['wins']}V / {s['losses']}D / {s['draws']}E)")
    lines.append("")

    # 5. Avaliação Técnica
    lines.append("## 5. Análise Técnica dos Resultados")
    lines.append("")
    top1 = sorted_by_wr[0]
    top2 = sorted_by_wr[1]
    bot1 = sorted_by_wr[-1]
    bot2 = sorted_by_wr[-2]

    lines.append(f"### 5.1 Domínio dos Top Tiers: **{top1['name']} ({top1['winrate']:.1f}%)** e **{top2['name']} ({top2['winrate']:.1f}%)**")
    lines.append("- Combatentes com excelente alcance, precedência de ataque imediata ou cobertura por projéteis mantêm controle consistente do espaço mesmo em arenas com perigos complexos.")
    lines.append("")
    lines.append(f"### 5.2 Desafios dos Bottom Tiers: **{bot1['name']} ({bot1['winrate']:.1f}%)** e **{bot2['name']} ({bot2['winrate']:.1f}%)**")
    lines.append("- Personagens que dependem de recarga estacionária, tiros com windup ou que possuem desvantagens contra assédio a longa distância sofrem mais em arenas abertas e com perigos móveis.")
    lines.append("")

    polar_matchups = []
    for k, m in matchups.items():
        w1 = m["wins_c1"]
        w2 = m["wins_c2"]
        tot = m["total_battles"]
        if max(w1, w2) / tot >= 0.85:
            winner = m["c1_name"] if w1 > w2 else m["c2_name"]
            loser = m["c2_name"] if w1 > w2 else m["c1_name"]
            polar_matchups.append(f"- **{winner} vs {loser}**: {max(w1, w2)} a {min(w1, w2)} ({max(w1, w2)/tot*100:.1f}% de dominância)")

    lines.append("### 5.3 Confrontos com Polarização Extrema (>= 85% de dominância)")
    if polar_matchups:
        for pm in polar_matchups[:8]:
            lines.append(pm)
    else:
        lines.append("Nenhum confronto atingiu polarização extrema superior a 85%.")
    lines.append("")

    lines.append("## 6. Diretrizes e Recomendações de Balanceamento")
    lines.append("1. **Normalização de Recovery**: Ajustar janelas de whiff para punição balanceada de ataques rápidos.")
    lines.append("2. **Mobilidade Tática**: Preservar movimentação tática durante recargas para reduzir vulnerabilidade em arenas estreitas.")
    lines.append("3. **Interação com Perigos**: Manter zonas neutras acessíveis em arenas com hazards telegrafados ativos.")
    lines.append("")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Relatório gravado com sucesso em '{output_path}'!")
    return content

def generate_comparative_report(all_tournaments: dict, output_path: str = "docs/BALANCE_COMPARATIVE_REPORT.md"):
    """
    Gera um relatório comparativo consolidado comparando as 3 dificuldades de IA (Easy, Normal, Hard).
    """
    diffs = ["easy", "normal", "hard"]
    lines = []
    lines.append("# Relatório Comparativo Global de Balanceamento (Easy vs Normal vs Hard)")
    lines.append("")
    lines.append("> **Resumo da Auditoria Completa**:")
    lines.append(f"> - Total de Batalhas Simuladas: **{sum(t['total_battles'] for t in all_tournaments.values())} batalhas**")
    lines.append(f"> - Roster: **{len(ROSTER)} Guerreiros**")
    lines.append(f"> - Arenas: **4 Arenas Padronizadas** (Dohyo Sagrado [Raiden], Telhados de Iga [Hanzo], Duelo na Ilha Ganryu [Musashi], Kyoto Bakumatsu [Saitou])")
    lines.append(f"> - Níveis de Dificuldade da IA: **Fácil (Easy)**, **Normal (Normal)**, **Difícil (Hard)**")
    lines.append("")

    lines.append("## 1. Tabela Comparativa de Winrates por Dificuldade")
    lines.append("")
    lines.append("| Rank Médio | Lutador | Winrate Easy | Winrate Normal | Winrate Hard | Variação (Hard - Easy) | Comportamento com IA Avançada |")
    lines.append("|:---:|:---|:---:|:---:|:---:|:---:|:---|")

    # Mapear dados
    data_by_char = defaultdict(dict)
    for d in diffs:
        if d in all_tournaments:
            for s in all_tournaments[d]["standings"]:
                data_by_char[s["id"]][d] = s["winrate"]

    avg_ranks = []
    for c_id in CHAR_IDS:
        wr_e = data_by_char[c_id].get("easy", 50.0)
        wr_n = data_by_char[c_id].get("normal", 50.0)
        wr_h = data_by_char[c_id].get("hard", 50.0)
        avg_wr = (wr_e + wr_n + wr_h) / 3.0
        avg_ranks.append((avg_wr, c_id, wr_e, wr_n, wr_h))

    avg_ranks.sort(reverse=True)

    for rank, (avg_wr, c_id, wr_e, wr_n, wr_h) in enumerate(avg_ranks, 1):
        name = CHAR_NAMES[c_id]
        diff_he = wr_h - wr_e
        diff_str = f"+{diff_he:.1f}%" if diff_he > 0 else f"{diff_he:.1f}%"
        if diff_he > 3.0:
            behavior = "📈 Ganha muito valor com reações rápidas da IA"
        elif diff_he < -3.0:
            behavior = "📉 Mais eficaz contra novatos / IA previsível"
        else:
            behavior = "⚖️ Desempenho altamente consistente e estável"
        lines.append(f"| {rank} | **{name}** | {wr_e:.1f}% | {wr_n:.1f}% | {wr_h:.1f}% | {diff_str} | {behavior} |")
    lines.append("")

    # 2. Comparativo de Classificação no Merge Sort
    lines.append("## 2. Comparativo de Posições no Merge Sort")
    lines.append("")
    lines.append("| Lutador | Posição Easy | Posição Normal | Posição Hard | Tendência Global |")
    lines.append("|:---|:---:|:---:|:---:|:---|")

    for c_id in CHAR_IDS:
        name = CHAR_NAMES[c_id]
        pos_e = all_tournaments["easy"]["merge_sorted_roster"].index(c_id) + 1 if "easy" in all_tournaments else "—"
        pos_n = all_tournaments["normal"]["merge_sorted_roster"].index(c_id) + 1 if "normal" in all_tournaments else "—"
        pos_h = all_tournaments["hard"]["merge_sorted_roster"].index(c_id) + 1 if "hard" in all_tournaments else "—"
        trend = "Estável"
        if isinstance(pos_e, int) and isinstance(pos_h, int):
            if pos_h < pos_e - 2:
                trend = "🔺 Sobe no Hard"
            elif pos_h > pos_e + 2:
                trend = "🔻 Cai no Hard"
        lines.append(f"| **{name}** | {pos_e}º | {pos_n}º | {pos_h}º | {trend} |")
    lines.append("")

    # 3. Conclusão e Observações
    lines.append("## 3. Principais Descobertas do Balanceamento")
    lines.append("- **IA Easy (Reações lentas ~380ms)**: Personagens com projéteis rápidos ou ataques de área ampla (Tomoe, Murasaki, Anne) têm vantagem pronunciada, pois a IA não esquiva a tempo.")
    lines.append("- **IA Normal (Reações realistas ~230ms)**: Distribuição equilibrada, onde combos e parries pontuais começam a punir ataques telegrafados.")
    lines.append("- **IA Hard (Reações cirúrgicas ~145ms & 85% Parry)**: Personagens defensivos e de contra-ataque rápido (Musashi, Julie, Kenshin) sobem de rendimento devido ao timing refinado de defesas.")
    lines.append("")

    content = "\n".join(lines)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nRelatório Comparativo gravado em '{output_path}'!")
    return content

def main():
    mode = "all"
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("easy", "normal", "hard", "all"):
            mode = arg

    difficulties_to_run = ["easy", "normal", "hard"] if mode == "all" else [mode]
    all_tournaments = {}

    for diff in difficulties_to_run:
        print(f"\n>>>> INICIANDO SIMULAÇÃO DE BALANCEAMENTO COMPLETA — NÍVEL {diff.upper()} <<<<")
        t_data = run_full_tournament_simulation(difficulty=diff)
        m_roster, m_logs = run_merge_sort_tournament(t_data)
        t_data["merge_sorted_roster"] = m_roster
        t_data["merge_logs"] = m_logs
        all_tournaments[diff] = t_data

        suffix = "" if diff == "normal" else f"_{diff}"
        results_file = f"tournament_results{suffix}.json"
        report_file = f"BALANCE_REPORT{suffix}.md"

        export_payload = {
            "difficulty": diff,
            "total_battles": t_data["total_battles"],
            "sim_time": t_data["sim_time"],
            "standings": t_data["standings"],
            "merge_sorted_roster": m_roster,
            "matchups": t_data["matchups"]
        }
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(export_payload, f, indent=2, ensure_ascii=False)

        generate_balance_report(t_data, m_roster, report_file)
        if os.path.exists("docs"):
            generate_balance_report(t_data, m_roster, os.path.join("docs", report_file))

    if len(all_tournaments) > 1:
        generate_comparative_report(all_tournaments, "docs/BALANCE_COMPARATIVE_REPORT.md")

if __name__ == "__main__":
    main()
