"""
Balanceamento exaustivo: TODOS os pares de lutadores x TODAS as arenas x ambos os lados (P1/P2).
24 lutadores -> 276 pares x 2 lados x 24 arenas = 13.248 duelos IA vs IA (headless).
Uso: python tools/balance_full_matrix.py [--difficulty normal] [--workers 6] [--out docs/deploy_prep/01_balance_raw.json]
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import argparse
import json
import random
import time
import zlib
from multiprocessing import Pool


def _wrap_super_armor(f, states):
    orig = f.take_hit

    def take_hit(slash_dir, damage=2, *a, **kw):
        if f.state in states and not getattr(f, "_armor_used", False) and damage >= f.hp:
            f._armor_used = True
            damage = f.hp - 1
        return orig(slash_dir, damage, *a, **kw)
    f.take_hit = take_hit


def _arena_job(args):
    arena_id, difficulty, max_time, patch, focus, salt = args
    import pygame
    pygame.init()
    pygame.font.init()
    from src.world.arenas import create_arena
    import tools.simulate_tournament as st
    from tools.simulate_tournament import simulate_single_battle, CHAR_IDS

    if patch:  # experimento "e se": sobrescreve atributos de instância após criar o lutador (não toca o código-fonte)
        _orig_create = st.create_fighter

        def _patched_create(char_id, x, y, *a, **kw):
            f = _orig_create(char_id, x, y, *a, **kw)
            for k, v in patch.get(char_id, {}).items():
                if k == "_super_armor":  # "e se": sobrevive a 1 golpe fatal enquanto estiver em estados de ataque
                    _wrap_super_armor(f, set(v))
                else:
                    setattr(f, k, v)
            return f
        st.create_fighter = _patched_create

    rows = []  # (a, b, winner, dur, reason) onde a=P1, b=P2
    errors = []
    t0 = time.perf_counter()
    for i, a in enumerate(CHAR_IDS):
        for b in CHAR_IDS[i + 1:]:
            if focus and a not in focus and b not in focus:
                continue
            for first, second in ((a, b), (b, a)):
                seed = zlib.crc32(f"{arena_id}|{first}|{second}{salt}".encode())
                random.seed(seed)
                try:
                    gm = create_arena(arena_id)
                    w, dur, reason = simulate_single_battle(first, second, gm, max_time=max_time, difficulty=difficulty)
                    rows.append((first, second, w, round(dur, 3), reason))
                except Exception as e:  # noqa: BLE001
                    errors.append((first, second, repr(e)))
    return arena_id, rows, errors, time.perf_counter() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--difficulty", default="normal")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--max-time", type=float, default=35.0)
    ap.add_argument("--arenas", nargs="*")
    ap.add_argument("--patch", default="", help='JSON {"char_id": {"attr": valor}} aplicado a instâncias (experimentos)')
    ap.add_argument("--salt", default="", help="sufixo da seed (replicação independente para medir ruído)")
    ap.add_argument("--focus", nargs="*", help="só pares que envolvam estes char_ids")
    ap.add_argument("--out", default=os.path.join(ROOT, "docs/deploy_prep/01_balance_raw.json"))
    args = ap.parse_args()

    import pygame
    pygame.init()
    from src.world.arenas import arena_ids
    arenas = args.arenas or arena_ids()
    patch = json.loads(args.patch) if args.patch else {}
    jobs = [(a, args.difficulty, args.max_time, patch, args.focus, args.salt) for a in arenas]
    out = {"patch": patch, "difficulty": args.difficulty, "max_time": args.max_time, "arenas": {}, "errors": {}}
    t0 = time.perf_counter()
    with Pool(args.workers) as pool:
        for aid, rows, errs, dt in pool.imap_unordered(_arena_job, jobs):
            out["arenas"][aid] = rows
            if errs:
                out["errors"][aid] = errs
            print(f"[{len(out['arenas']):2d}/{len(jobs)}] {aid:20s} {len(rows)} lutas, {len(errs)} erros, {dt:.0f}s", flush=True)
    out["elapsed"] = time.perf_counter() - t0
    with open(args.out, "w") as f:
        json.dump(out, f)
    print(f"Total {out['elapsed']:.0f}s -> {args.out}")


if __name__ == "__main__":
    main()
