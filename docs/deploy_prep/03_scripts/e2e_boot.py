"""Boot headless ate o titulo e percorre menus basicos. Uso: e2e_boot.py SANDBOX [frames]"""
import os, sys, time, random
sys.path.insert(0, "/tmp/se")
import drv
import pygame

SANDBOX = sys.argv[1]
FRAMES = int(sys.argv[2]) if len(sys.argv) > 2 else 120


def script(ctx):
    t0 = time.time()
    seen = []
    RESUME = os.environ.get("RESUME") == "1"
    for fr in range(FRAMES):
        L = ctx.L()
        st = L.get("game_state")
        if not seen or seen[-1] != st:
            seen.append(st)
        if RESUME:
            if st == "title" and fr % 8 == 0:
                ctx.key(pygame.K_UP) if fr % 16 == 0 else ctx.key(pygame.K_RETURN)
            elif st in ("arcade_difficulty", "arcade_bracket") and fr % 6 == 0:
                ctx.key(pygame.K_RETURN)
            elif st == "duel_playing":
                mi = L.get("match_intro")
                if mi is not None and mi.active and fr % 5 == 0:
                    ctx.key(pygame.K_RETURN)
            yield
            continue
        if fr == 10:
            ctx.key(pygame.K_DOWN); ctx.key(pygame.K_DOWN)      # OPTIONS
        if fr == 14:
            ctx.key(pygame.K_RETURN)
        if fr in (25, 28, 31, 34):
            ctx.key(pygame.K_DOWN)
        if fr == 40:
            ctx.key(pygame.K_RETURN)
        if fr == 50:
            ctx.key(pygame.K_ESCAPE)
        if fr == 60:
            ctx.key(pygame.K_ESCAPE)
        if fr == 70:
            ctx.key(pygame.K_UP)
        if fr == 74:
            ctx.key(pygame.K_RETURN)   # ARCADE
        if fr == 90:
            ctx.key(pygame.K_ESCAPE)
        yield
    ctx.log("BOOT_OK states:", seen, f"t={time.time()-t0:.1f}s")
    raise drv.Done()


if __name__ == "__main__":
    t = time.time()
    ctx, res = drv.run(script, sandbox=SANDBOX, dt_ms=33)
    print(f"total {time.time()-t:.1f}s ok={res['ok']}")
    sys.exit(0 if res["ok"] else 3)
