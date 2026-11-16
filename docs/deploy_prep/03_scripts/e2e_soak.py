"""Soak 5000 frames em IA x IA (watch), monitorando RSS, listas e contagem de objetos.
Uso: e2e_soak.py P1 P2 ARENA FRAMES SANDBOX"""
import os, sys, time, gc, subprocess, collections, math
sys.path.insert(0, "/tmp/se")
import drv
import pygame

P1, P2, ARENA, FRAMES, SANDBOX = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
sys.path.insert(0, drv.PROJECT)


def rss_now():
    try:
        return int(subprocess.run(["ps", "-o", "rss=", "-p", str(os.getpid())], capture_output=True, text=True).stdout.strip()) / 1024
    except Exception:
        return -1


def patch():
    sys.path.insert(0, SANDBOX)
    import src.ui.versus_config as vc, src.ui.character_select as cs, src.ui.arena_select as asl
    vc.VersusConfigScreen.handle_event = lambda self, e, c=None: "PROCEED" if (e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN) else None
    cs.CharacterSelectScreen.handle_event = lambda self, e: bool(e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN)
    cs.CharacterSelectScreen.get_selected_characters = lambda self: (P1, P2, True)
    asl.ArenaSelectScreen.handle_event = lambda self, e: ARENA if (e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN) else None


def script(ctx):
    patch()
    waited = 0
    while True:
        L = ctx.L(); st = L.get("game_state")
        if st in ("title", "versus_config", "character_select", "arena_select"):
            ctx.key(pygame.K_RETURN)
        elif st == "duel_playing":
            break
        yield
    for _ in range(600):
        L = ctx.L()
        if L["match_intro"].active:
            ctx.key(pygame.K_RETURN)
        elif L.get("round_started"):
            break
        yield
    ctx.key(pygame.K_TAB)  # watch
    rows = []
    rounds_seen = 0
    last_rw = None
    t0 = time.time()
    gc.collect()
    TM = os.environ.get("TM") == "1"
    if TM:
        import tracemalloc
    snap1 = None
    for fr in range(FRAMES):
        L = ctx.L()
        if TM and fr == 1500:
            gc.collect(); tracemalloc.start(8); snap1 = tracemalloc.take_snapshot()
        rw = L.get("round_winner")
        if rw is not None and last_rw is None:
            rounds_seen += 1
        last_rw = rw
        if fr % 250 == 0:
            gc.collect()
            cnt = collections.Counter(type(o).__name__ for o in gc.get_objects())
            cd = L.get("cinematic_director")
            row = {
                "fr": fr, "rss": round(rss_now()), "rounds": rounds_seen,
                "particles": len(L.get("particles") or []), "proj": len(L.get("projectiles") or []), "banners": len(L.get("banners") or []),
                "leaves": len(L.get("ambient_leaves") or []), "decoys": len(L.get("decoys") or []),
                "poison": len(L.get("poison_clouds") or []), "traps": len(L.get("powder_traps") or []),
                "corpses": len(getattr(cd, "corpses", []) or []),
                "terrain_p": len(getattr(L.get("terrain_fx"), "particles", []) or []),
                "Surface": cnt.get("Surface", 0), "ndarray": cnt.get("ndarray", 0), "objs": sum(cnt.values()),
                "score": (L.get("score_p1"), L.get("score_p2")),
            }
            rows.append(row)
            if fr == 1000: cnt_a = cnt
            cnt_last = cnt
            ctx.log("SOAK", row)
        # reinicia sozinho (watch) ; ajuda: Espaco
        if rw is not None and fr % 40 == 0:
            ctx.key(pygame.K_SPACE)
        yield
    if TM and snap1 is not None:
        gc.collect()
        snap2 = tracemalloc.take_snapshot()
        top = snap2.compare_to(snap1, "lineno")[:15]
        ctx.log("TRACEMALLOC top crescimento (de fr=1500 ate o fim):")
        for st in top:
            ctx.log("   ", st)
    try:
        diff = {k: cnt_last.get(k, 0) - cnt_a.get(k, 0) for k in set(cnt_last) | set(cnt_a)}
        ctx.log("TIPOS que mais cresceram (fr=1000 -> fim):", sorted(diff.items(), key=lambda kv: -kv[1])[:12])
    except Exception as e:
        ctx.log("diff erro", e)
    ctx.log(f"SOAK_DONE frames={FRAMES} t={time.time()-t0:.0f}s rounds={rounds_seen}")
    first, last = rows[1], rows[-1]
    ctx.log("DELTA rss %+d MB ; objs %+d ; Surface %+d ; ndarray %+d" % (last["rss"] - first["rss"], last["objs"] - first["objs"], last["Surface"] - first["Surface"], last["ndarray"] - first["ndarray"]))
    raise drv.Done()


if __name__ == "__main__":
    ctx, res = drv.run(script, sandbox=SANDBOX, dt_ms=33)
    sys.exit(0 if res["ok"] else 3)
