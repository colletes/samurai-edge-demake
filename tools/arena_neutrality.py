"""
Neutralidade das arenas: duelos de IA contra IA em cada uma das 12 arenas, com os 12 lutadores.

Para cada arena, cada lutador faz `--duels` duelos contra rivais sorteados (lados alternados).
O relatório compara a taxa de vitória de cada lutador na arena com a dele no conjunto de todas
as arenas, e mede a "vantagem de casa" (lutador dono da arena contra o resto do elenco nela).
Uma arena é marcada quando alguma diferença passa de `--limite` (padrão 0.30 em pontos de taxa).

Uso: SDL_VIDEODRIVER=dummy ./venv/bin/python tools/arena_neutrality.py [--duels 4] [--arena id] [--jobs 4]
Saída: tabela no terminal e JSON em scratch/arena_neutrality.json.
"""
import argparse
import collections
import json
import multiprocessing
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

DUEL_SECONDS = 45.0
DT = 1 / 60


def _setup():
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))


def duel(arena_id: str, char_a: str, char_b: str, seed: int, use_fog: bool = True):
    """Um duelo completo; devolve (vencedor, motivo, segundos). Vencedor: id do lutador, 'draw' ou 'timeout'."""
    import tests.test_arena_engine as eng
    from src.combat.collision import CombatSystem
    from src.effects.cinematic_director import CinematicDirector
    from src.effects.fog import FogVolume
    from src.entities.ai_controller import SamuraiAI
    from src.isometric.camera import Camera
    from src.world.arenas import create_arena

    random.seed(seed)
    arena = create_arena(arena_id)
    fog = FogVolume(arena) if use_fog else None
    arena.fog = fog
    (ax, ay), (bx, by) = arena.pick_spawns()
    a = eng._fighter_at(char_a, ax, ay)
    b = eng._fighter_at(char_b, bx, by)
    a.set_facing(b.wx, b.wy)
    b.set_facing(a.wx, a.wy)
    ai_a, ai_b = SamuraiAI("hard"), SamuraiAI("hard")
    combat, cam, director = CombatSystem(), Camera(11.0, 11.0), CinematicDirector()
    particles, projectiles, banners, decoys = [], [], [], []
    t = 0.0
    while t < DUEL_SECONDS and a.is_alive and b.is_alive:
        ai_a.update(a, b, DT, arena, projectiles, decoys, [])
        ai_b.update(b, a, DT, arena, projectiles, decoys, [])
        eng.step_fighter(a, b, DT, arena, particles, projectiles, banners)
        eng.step_fighter(b, a, DT, arena, particles, projectiles, banners)
        arena.update(DT, [a, b], cam, particles, banners, director)
        if fog is not None:
            for fighter in (a, b):
                if hasattr(fighter, "drain_fog_nodes"):
                    for node in fighter.drain_fog_nodes():
                        fog.add_trail(*node)
            fog.update(DT, t)
        combat.process_combat(a, b, arena, particles, banners, cam, projectiles, DT, director, decoys)
        particles[:] = particles[-200:]
        banners[:] = banners[-10:]
        t += DT
    if not a.is_alive and not b.is_alive:
        return "draw", "mutual", t
    if not a.is_alive:
        return char_b, "ko", t
    if not b.is_alive:
        return char_a, "ko", t
    ha, hb = getattr(a, "hp", 0), getattr(b, "hp", 0)
    if ha != hb:
        return (char_a if ha > hb else char_b), "timeout_hp", t
    return "timeout", "timeout", t


def run_arena(args):
    arena_id, duels, base_seed = args
    _setup()
    from src.roster import ROSTER_ORDER
    rng = random.Random(base_seed)
    wins, games = collections.Counter(), collections.Counter()
    reasons = collections.Counter()
    for fighter in ROSTER_ORDER:
        for k in range(duels):
            rival = rng.choice([c for c in ROSTER_ORDER if c != fighter])
            pair = (fighter, rival) if k % 2 == 0 else (rival, fighter)
            winner, reason, _ = duel(arena_id, pair[0], pair[1], rng.randrange(10 ** 6))
            reasons[reason] += 1
            games[fighter] += 1
            if winner == fighter:
                wins[fighter] += 1
            elif winner in ("draw", "timeout"):
                wins[fighter] += 0.5
    return arena_id, {f: wins[f] / games[f] for f in ROSTER_ORDER}, dict(reasons)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duels", type=int, default=4, help="duelos por lutador por arena")
    parser.add_argument("--arena", default=None, help="só esta arena")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--limite", type=float, default=0.30)
    opts = parser.parse_args()

    from src.roster import ARENA_BY_FIGHTER, ROSTER_ORDER
    from src.world.arenas import arena_ids
    ids = [opts.arena] if opts.arena else arena_ids()
    jobs = [(a, opts.duels, 1000 + i) for i, a in enumerate(ids)]
    with multiprocessing.get_context("spawn").Pool(min(opts.jobs, len(jobs))) as pool:
        results = {a: (rates, reasons) for a, rates, reasons in pool.map(run_arena, jobs)}

    overall = {f: sum(results[a][0][f] for a in ids) / len(ids) for f in ROSTER_ORDER}
    print(f"\nDuelos por lutador por arena: {opts.duels} (IA difícil). Desvio = taxa na arena - taxa geral do lutador.")
    flagged = []
    for a in ids:
        rates, reasons = results[a]
        devs = {f: rates[f] - overall[f] for f in ROSTER_ORDER}
        worst_f = max(devs, key=lambda f: abs(devs[f]))
        home = next((f for f, arena in ARENA_BY_FIGHTER.items() if arena == a), None)
        home_dev = devs[home] if home else 0.0
        mean_abs = sum(abs(v) for v in devs.values()) / len(devs)
        mark = "  <== CONFERIR" if abs(home_dev) > opts.limite else ""
        if mark:
            flagged.append(a)
        print(f"{a:18s} casa={home or '-':10s} desvio_casa={home_dev:+.2f}  maior_desvio={worst_f}:{devs[worst_f]:+.2f}  "
              f"desvio_médio={mean_abs:.2f}  fins={reasons}{mark}")
    print("\nTaxa de vitória geral por lutador:", {f: round(v, 2) for f, v in overall.items()})
    print("Arenas para conferir:", flagged or "nenhuma")
    os.makedirs(os.path.join(ROOT, "scratch"), exist_ok=True)
    with open(os.path.join(ROOT, "scratch", "arena_neutrality.json"), "w", encoding="utf-8") as fh:
        json.dump({"duels": opts.duels, "overall": overall, "arenas": {a: results[a][0] for a in ids}, "flagged": flagged}, fh, indent=2)


if __name__ == "__main__":
    main()
