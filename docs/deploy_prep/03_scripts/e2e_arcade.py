"""
Arcade ponta a ponta via main.run_game(). Uso:
  e2e_arcade.py PLAYER_CHAR SANDBOX [lose_idx,lose_idx,..] [stop_after_fight_idx]
Joga as 12 lutas (forcando vitoria, e derrota nos indices dados), passa pelos creditos e resultado.
"""
import os, sys, time, math, random, json, traceback
sys.path.insert(0, "/tmp/se")
import drv
import pygame

PLAYER = sys.argv[1]
SANDBOX = sys.argv[2]
LOSE = {int(x) for x in sys.argv[3].split(",")} if len(sys.argv) > 3 and sys.argv[3] not in ("", "-") else set()
STOP_AFTER = int(sys.argv[4]) if len(sys.argv) > 4 else 99
DT_MS = int(os.environ.get("DT_MS", "40"))
START_MODE = os.environ.get("ARC_START", "new")  # new | resume
sys.path.insert(0, drv.PROJECT)


def patch():
    sys.path.insert(0, SANDBOX)
    import src.ui.character_select as cs
    def cs_he(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return True
        return False
    cs.CharacterSelectScreen.handle_event = cs_he
    def cs_sel(self):
        return PLAYER, PLAYER, True
    cs.CharacterSelectScreen.get_selected_characters = cs_sel


def finite(v):
    return isinstance(v, (int, float)) and math.isfinite(v)


def script(ctx):
    patch()
    from src.config import DEFAULT_CONTROLS as DC
    rnd = random.Random(7)
    mv = [DC["P1_UP"], DC["P1_DOWN"], DC["P1_LEFT"], DC["P1_RIGHT"]]
    atk = DC["P1_ATTACK"]
    sec = DC.get("P1_SECONDARY", pygame.K_r)
    dash = DC.get("P1_DASH", pygame.K_t)
    last_sig = None
    sig_frames = 0
    transitions = []
    prev_state = None
    fights_done = 0
    seen_states = set()
    duel_frames = 0
    fight_key = None
    forced = {}
    lost_once = set()
    decision = {}
    total = 0
    started = False
    title_pressed = 0
    saw_credits = False
    stats = {"fights": [], "softlocks": [], "nan": []}
    while True:
        total += 1
        L = ctx.L()
        st = L.get("game_state")
        run = L.get("arcade_run")
        if st != prev_state:
            idx = run.index if run is not None else None
            ctx.log(f"[f{total}] state {prev_state} -> {st} (arcade idx={idx}) rw={L.get('round_winner')} over={L.get('arcade_fight_over')} p1hp={getattr(L.get('p1'),'hp',None)} p2hp={getattr(L.get('p2'),'hp',None)} p1alive={getattr(L.get('p1'),'is_alive',None)}")
            prev_state = st
        seen_states.add(st)
        # --- deteccao de soft-lock
        p1, p2 = L.get("p1"), L.get("p2")
        sig = (st, L.get("round_winner"), L.get("score_p1"), L.get("score_p2"), L.get("round_number"),
               round(getattr(p1, "hp", 0)) if p1 else 0, round(getattr(p2, "hp", 0)) if p2 else 0,
               run.index if run else None, L.get("arcade_fight_over"), L.get("arcade_round_status"),
               L.get("match_winner"))
        if sig == last_sig:
            sig_frames += 1
        else:
            sig_frames = 0
            last_sig = sig
        if sig_frames == 1200:
            cd = L.get("cinematic_director")
            os_ = L.get("outcome_seq")
            info = {
                "state": st, "round_winner": L.get("round_winner"), "match_winner": L.get("match_winner"),
                "arcade_fight_over": L.get("arcade_fight_over"), "round_status": L.get("arcade_round_status"),
                "cd_active": getattr(cd, "is_active", None), "cd_frozen": cd.is_frozen() if cd else None,
                "cd_timers": {k: getattr(cd, k) for k in ("camera_setup_timer", "freeze_timer", "delayed_death_timer", "bw_flash_timer") if cd and hasattr(cd, k)},
                "outcome_active": getattr(os_, "active", None), "outcome_pending": getattr(os_, "pending", None),
                "pause_open": L["pause_menu"].is_open if L.get("pause_menu") else None,
                "hitstop": getattr(L.get("combat_system"), "hitstop_timer", None),
                "p1_state": getattr(p1, "state", None), "p2_state": getattr(p2, "state", None),
            }
            ctx.log("  SOFTLOCK suspeito (1200 frames sem mudanca): " + json.dumps(info, default=str))
            stats["softlocks"].append(info)
        if sig_frames == 2400:
            ctx.log("  SOFTLOCK confirmado (2400 frames); abortando")
            break
        # --- NaN
        if p1 is not None and p2 is not None and st == "duel_playing":
            for f in (p1, p2):
                for attr in ("wx", "wy", "wz", "hp"):
                    v = getattr(f, attr, 0.0)
                    if not finite(v):
                        stats["nan"].append((total, f.name, attr, v))
                        ctx.log(f"  NaN/inf {f.name}.{attr}={v}")
        # --- acao por estado
        if st == "title":
            if title_pressed == 0:
                ctx.key(pygame.K_UP)
            elif title_pressed == 3:
                ctx.key(pygame.K_RETURN)
            title_pressed += 1
            if title_pressed > 20:
                title_pressed = 0
        elif st == "arcade_difficulty":
            scr = L.get("arcade_difficulty_screen")
            if os.environ.get("ARC_RESUME") == "1" and total % 10 == 2 and scr is not None and scr.options and scr.options[scr.selected] != "resume":
                ctx.key(pygame.K_LEFT)
            elif total % 10 == 0 and not (os.environ.get("ARC_RESUME") == "1" and scr is not None and scr.options and scr.options[scr.selected] != "resume"):
                ctx.key(pygame.K_RETURN)
        elif st == "arcade_char_select":
            if total % 5 == 0:
                ctx.key(pygame.K_RETURN)
        elif st == "arcade_bracket":
            if START_MODE == "boss" and not globals().get('_konami_done'):
                seq = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a]
                ks = globals().get('_ks', 0)
                if ks < len(seq):
                    ctx.key(seq[ks]); globals()['_ks'] = ks + 1
                else:
                    globals()['_konami_done'] = True
            elif total % 10 == 0:
                ctx.key(pygame.K_RETURN)
        elif st == "arcade_credits":
            saw_credits = True
            cred_frames = globals().get('_cf', 0) + 1
            globals()['_cf'] = cred_frames
            if cred_frames == 200:   # 5s+ de creditos a 40ms/frame
                ctx.keydown(pygame.K_RETURN)
            if cred_frames == 200 + 60:
                ctx.keyup(pygame.K_RETURN)
        elif st == "arcade_result":
            if total % 20 == 0:
                ctx.key(pygame.K_RETURN)
        elif st == "duel_playing":
            mi = L.get("match_intro")
            if mi is not None and mi.active:
                if total % 20 == 0:
                    ctx.key(pygame.K_RETURN)
            elif L.get("pause_menu") is not None and L["pause_menu"].is_open:
                ctx.key(pygame.K_ESCAPE)
            elif p1 is not None and p2 is not None and run is not None:
                fk = (run.index, run.opponent_index, L.get("round_number"), L.get("p2_char_id"))
                if fk != fight_key:
                    fight_key = fk
                    duel_frames = 0
                    ctx.log(f"  fight idx={run.index} opp#{run.opponent_index} round={L.get('round_number')} p2={L.get('p2_char_id')} arena={L.get('selected_arena_id')} diff={run.difficulty_name}")
                duel_frames += 1
                rw = L.get("round_winner")
                if rw is None and L.get("round_started") and getattr(p2, "is_boss", False):
                    for k in mv:
                        if k in ctx.keys.held:
                            ctx.keyup(k)
                    if os.environ.get("BOSS_LOSE") == "1":
                        p1.hp = min(p1.hp, 1)
                        if duel_frames == 1200:
                            p1.hp = 0; p1.is_alive = False
                    else:
                        p1.max_hp = max(p1.max_hp, 99); p1.hp = p1.max_hp
                        if duel_frames % 4 == 0:
                            ctx.key(rnd.choice([atk, atk, atk, sec, dash]))
                        if duel_frames % 10 == 0 and math.hypot(p2.wx - p1.wx, p2.wy - p1.wy) > 2.2:
                            p1.wx, p1.wy = p2.wx - 1.2, p2.wy
                        if duel_frames == int(os.environ.get('BOSS_T1','1500')):
                            p2.hp = 1
                        if duel_frames == int(os.environ.get('BOSS_T2','3000')):
                            ctx.log("  fallback boss: matando direto"); p2.hp = 0; p2.is_alive = False
                    if duel_frames % 200 == 0:
                        ctx.log(f"  boss f={duel_frames} hp={p2.hp} phase={getattr(p2,'phase',None)} p1hp={p1.hp}")
                elif rw is None and L.get("round_started"):
                    if fk not in decision:
                        decision[fk] = (run.index in LOSE and run.index not in lost_once)
                        if decision[fk]:
                            lost_once.add(run.index)
                    lose_this = decision[fk]
                    target = p1 if lose_this else p2
                    killer = p2 if lose_this else p1
                    # movimento de P1: aproxima do oponente e ataca
                    for k in mv:
                        if k in ctx.keys.held:
                            ctx.keyup(k)
                    if not lose_this:
                        dx, dy = p2.wx - p1.wx, p2.wy - p1.wy
                        # aproximacao em coordenadas de mundo: usa aleatorio + teleporte quando longe
                        if duel_frames % 4 == 0:
                            ctx.key(rnd.choice([atk, atk, atk, sec]))
                        if duel_frames > 40 and duel_frames % 8 == 0 and hasattr(p2, "stun") and not getattr(p2, "is_boss", False):
                            try:
                                p2.stun(0.5)
                            except Exception:
                                pass
                        if duel_frames > 50 and math.hypot(dx, dy) > 2.0 and duel_frames % 20 == 0:
                            p1.wx, p1.wy = p2.wx - 0.9, p2.wy
                    if duel_frames == 40 and not forced.get(fk):
                        forced[fk] = True
                        if not getattr(target, "is_boss", False) or True:
                            target.hp = 1
                        ctx.log(f"  (forcando hp=1 em {target.name})")
                    # fallback depois de muito tempo
                    if duel_frames == 700:
                        ctx.log("  fallback: matando alvo direto")
                        target.hp = 0
                        target.is_alive = False
                elif rw is not None:
                    if duel_frames % 12 == 0:
                        ctx.key(pygame.K_SPACE)
        # --- fim
        if saw_credits and st == "title":
            ctx.log("Arcade concluido; voltou ao titulo.")
            break
        if run is not None and run.index > STOP_AFTER and st == "arcade_bracket":
            ctx.log(f"Parando apos fight {STOP_AFTER} (para teste de resume)")
            break
        if total > 60000:
            ctx.log("TIMEOUT total frames")
            stats["softlocks"].append("total_timeout")
            break
        yield
    # salva resumo
    try:
        data = open(os.path.join(SANDBOX, "arcade_save.json")).read()
        ctx.log("arcade_save.json:", data[:600].replace("\n", " "))
    except Exception as e:
        ctx.log("sem arcade_save.json:", e)
    ctx.log("STATS", json.dumps(stats, default=str))
    ctx.log("states vistos:", sorted(str(s) for s in seen_states))
    ctx.log(f"frames={total} max_frame_ms={ctx.max_frame_ms:.0f}")
    raise drv.Done()


if __name__ == "__main__":
    ctx, res = drv.run(script, sandbox=SANDBOX, dt_ms=DT_MS)
    sys.exit(0 if res["ok"] else 3)
