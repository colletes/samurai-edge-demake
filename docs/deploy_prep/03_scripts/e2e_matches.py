"""
Lote de partidas ponta a ponta via main.run_game(): pares (P1,P2,arena) com render real.
Uso: python e2e_matches.py ARENA_ID START_IDX [FRAMES_PER_JOB] [MODE]
MODE: watch (IA x IA) | human (P1 teclado aleatorio vs IA) | mix (alterna)
"""
import os, sys, time, math, random, traceback, json
sys.path.insert(0, "/tmp/se")
import drv

ARENA = sys.argv[1]   # id da arena ou "ALL"
START = int(sys.argv[2]) if len(sys.argv) > 2 else 0
END = int(os.environ.get("END", "100000"))
P2_FIXED = os.environ.get("P2_FIXED")   # ex.: gashadokuro (so para o chefe)
FPJ = int(sys.argv[3]) if len(sys.argv) > 3 else 700
MODE = sys.argv[4] if len(sys.argv) > 4 else "mix"
DT_MS = int(os.environ.get("DT_MS", "40"))
OVERLAP = os.environ.get("OVERLAP") == "1"
FORCE_SEC = os.environ.get("FORCE_SEC") == "1"
OVERLAP_EVERY = int(os.environ.get("OVERLAP_EVERY", "3"))
SANDBOX = os.environ.get("SANDBOX", f"/tmp/se/play_m_{ARENA}")

import pygame
sys.path.insert(0, drv.PROJECT)
from src.roster import PLAYABLE_FIGHTERS
CHARS = list(PLAYABLE_FIGHTERS)


class JobBox:
    job = None


def patch_screens():
    sys.path.insert(0, SANDBOX)
    import src.ui.versus_config as vc
    import src.ui.character_select as cs
    import src.ui.arena_select as asl
    orig_vc = vc.VersusConfigScreen.handle_event
    def vc_he(self, event, ctrl_mgr=None):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return "PROCEED"
        return None
    vc.VersusConfigScreen.handle_event = vc_he
    def cs_he(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return True
        return False
    cs.CharacterSelectScreen.handle_event = cs_he
    def cs_sel(self):
        j = JobBox.job
        return j["p1"], j["p2"], True
    cs.CharacterSelectScreen.get_selected_characters = cs_sel
    def as_he(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return JobBox.job["arena"]
        return None
    asl.ArenaSelectScreen.handle_event = as_he


def finite(v):
    return isinstance(v, (int, float)) and math.isfinite(v)


STYLES = {}

def script(ctx):
    patch_screens()
    from src.effects.cinematic_director import CinematicDirector as _CD
    _orig_tfs = _CD.trigger_fatal_strike
    def _tfs(self, attacker, victim, death_style, slash_dir):
        STYLES[death_style] = STYLES.get(death_style, 0) + 1
        return _orig_tfs(self, attacker, victim, death_style, slash_dir)
    _CD.trigger_fatal_strike = _tfs
    import main as gm
    rnd = random.Random(1234 + START)
    jobs = []
    n = len(CHARS)
    from src.world.arenas import arena_ids
    arenas = arena_ids() if ARENA == "ALL" else [ARENA]
    for ar in arenas:
        a_i = arena_ids().index(ar) if ar in arena_ids() else 0
        for i in range(n):
            if os.environ.get("P1_FIXED"):
                jobs.append({"p1": os.environ["P1_FIXED"], "p2": CHARS[i], "arena": ar})
            else:
                jobs.append({"p1": CHARS[i], "p2": (P2_FIXED or CHARS[(i + a_i + 1) % n]), "arena": ar})
    stats = {"jobs_done": 0, "ko": 0, "no_ko": 0, "softlocks": [], "nan": [], "maxfr": 0.0, "fr_ms": []}
    results = []
    for ji in range(START, min(END, len(jobs))):
        job = jobs[ji]
        JobBox.job = job
        mode = MODE if MODE != "mix" else ("watch" if ji % 2 == 0 else "human")
        random.seed(ji * 7919 + 13)
        t_job = time.perf_counter()
        ctx.log(f"[job {ji}] {job['p1']} vs {job['p2']} @ {job['arena']} mode={mode}")
        # espera chegar ao duelo
        waited = 0
        while True:
            L = ctx.L()
            st = L.get("game_state")
            if st == "title":
                ctx.key(pygame.K_RETURN)
            elif st in ("versus_config", "character_select", "arena_select"):
                ctx.key(pygame.K_RETURN)
            elif st == "duel_playing":
                break
            waited += 1
            if waited > 600:
                ctx.log(f"  SOFTLOCK: nao chegou ao duelo; state={st}")
                stats["softlocks"].append((ji, "never_reached_duel", st))
                raise drv.Done()
            yield
        # pula intro orbital
        for _ in range(900):
            L = ctx.L()
            mi = L.get("match_intro")
            if mi is not None and mi.active:
                ctx.key(pygame.K_RETURN)
            elif L.get("round_started"):
                break
            yield
        L = ctx.L()
        if not L.get("round_started"):
            ctx.log("  SOFTLOCK: round nao iniciou em 900 frames")
            stats["softlocks"].append((ji, "round_never_started", L.get("game_state")))
        if mode == "watch":
            ctx.key(pygame.K_TAB)
        # luta
        keys_pool_p1 = {"move": [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d], "act": None}
        from src.config import DEFAULT_CONTROLS as DC
        mv = [DC["P1_UP"], DC["P1_DOWN"], DC["P1_LEFT"], DC["P1_RIGHT"]]
        acts = [DC["P1_ATTACK"], DC.get("P1_SECONDARY", pygame.K_r), DC.get("P1_DASH", pygame.K_t)]
        held = set()
        winner_frame = None
        forced = False
        peak_particles = 0
        for fr in range(FPJ):
            L = ctx.L()
            p1, p2 = L.get("p1"), L.get("p2")
            if p1 is None or p2 is None:
                yield
                continue
            if OVERLAP and L.get("round_winner") is None and L.get("round_started") and fr % OVERLAP_EVERY == 0:
                p2.wx, p2.wy = p1.wx + (1e-9 if fr % 2 else 0.0), p1.wy
            for f in (p1, p2):
                for attr in ("wx", "wy", "wz", "hp"):
                    v = getattr(f, attr, 0.0)
                    if not finite(v):
                        stats["nan"].append((ji, f.name, attr, v))
                        ctx.log(f"  NaN/inf {f.name}.{attr}={v}")
            for lst in ("particles", "projectiles", "banners"):
                peak_particles = max(peak_particles, len(L.get(lst) or []))
            if L.get("round_winner") is not None:
                if winner_frame is None:
                    winner_frame = fr
                    stats["ko"] += 1
                    ctx.log(f"  KO/round_winner={L.get('round_winner')} em frame {fr} (f.state p1={p1.state} p2={p2.state})")
                # tenta avancar
                if fr % 15 == 0:
                    ctx.key(pygame.K_SPACE)
                if fr - winner_frame > 700:
                    break
            else:
                if FORCE_SEC and L.get("round_started"):
                    if fr % 30 == 0:
                        p2.hp = 1
                        p1.wx, p1.wy = p2.wx - 1.0, p2.wy
                    p1.set_facing(p2.wx, p2.wy)
                    if hasattr(p2, "stun") and fr % 4 == 0:
                        p2.stun(0.3)
                    if fr % 5 == 0:
                        ctx.key(acts[1])
                if mode == "human" and fr % 6 == 0 and not FORCE_SEC:
                    for k in list(held):
                        ctx.keyup(k)
                        held.discard(k)
                    for k in rnd.sample(mv, rnd.choice([0, 1, 1, 2])):
                        ctx.keydown(k)
                        held.add(k)
                    if rnd.random() < 0.7:
                        ctx.key(rnd.choice(acts))
                # forcar KO se ninguem morreu na metade do tempo
                if fr == FPJ // 2 and not forced:
                    forced = True
                    tgt = p2 if mode == "human" else rnd.choice([p1, p2])
                    tgt.hp = 1
                    ctx.log("  (forcando hp=1 em %s)" % tgt.name)
            yield
        for k in list(held):
            ctx.keyup(k)
        if winner_frame is None:
            stats["no_ko"] += 1
            ctx.log("  sem KO no limite de frames")
        ctx.log(f"  peak(particles/proj/banners)={peak_particles} t={time.perf_counter()-t_job:.1f}s rss={drv.rss_mb():.0f}MB")
        stats["jobs_done"] += 1
        # volta ao menu: ESC -> Fighter (3x DOWN, ENTER)
        for _ in range(3):
            L = ctx.L()
            if L.get("pause_menu") is not None and L["pause_menu"].is_open:
                break
            ctx.key(pygame.K_ESCAPE)
            yield
            yield
        for _ in range(3):
            ctx.key(pygame.K_DOWN)
            yield
        ctx.key(pygame.K_RETURN)
        yield
        yield
    ctx.log("DEATH_STYLES", json.dumps(STYLES, sort_keys=True))
    ctx.log("STATS", json.dumps({k: v for k, v in stats.items() if k != "fr_ms"}, default=str))
    ctx.log(f"max_frame_ms (wall) = {ctx.max_frame_ms:.0f}")
    raise drv.Done()


if __name__ == "__main__":
    import warnings
    ctx, res = drv.run(script, sandbox=SANDBOX, dt_ms=DT_MS)
    sys.exit(0 if res["ok"] else 3)
