"""Varredura de finishers: para cada (atacante, estilo de morte) alcancavel, roda a sequencia completa (update+render) em N vitimas.
Uso: t_finisher.py [VICTIMS=n]"""
import os, sys, re, math, time, traceback, random, itertools
os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
PROJECT = "/Users/thiagocarvalho/Public/SamuraiEdge"
sys.path.insert(0, PROJECT)
os.chdir("/tmp")
import pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
import main as gm
from src.roster import PLAYABLE_FIGHTERS
from src.combat import collision
from src.effects.cinematic_director import CinematicDirector
from src.isometric.camera import Camera
from src.world.arenas import create_arena

src_col = open(os.path.join(PROJECT, "src/combat/collision.py"), encoding="utf-8").read()
fn_src = src_col[src_col.index("def _get_death_style_for_attacker"):src_col.index("\ndef ", src_col.index("def _get_death_style_for_attacker") + 10)]
states = sorted(set(re.findall(r'"([A-Z_]{3,})"', fn_src)))
weapons = ["kunai", "shuriken", "arrow", "wave", "shockwave", "cross_wave", "stomp", "counter", None]
literal_styles = set()
pat = re.compile(r'trigger_fatal_strike\([^,]+,[^,]+,\s*"([A-Z_]+)"')
for f in ("src", "main.py"):
    p = os.path.join(PROJECT, f)
    files = [p] if os.path.isfile(p) else [os.path.join(r, fn) for r, _, fs in os.walk(p) for fn in fs if fn.endswith(".py")]
    for fp in files:
        try:
            literal_styles |= set(pat.findall(open(fp, encoding="utf-8").read()))
        except Exception:
            pass
print("estados varridos:", len(states), "estilos literais:", len(literal_styles))

pairs = {}   # style -> set(attacker char ids)
victims_pool = list(PLAYABLE_FIGHTERS)
for cid in PLAYABLE_FIGHTERS:
    a = gm.create_fighter(cid, 10.0, 10.0)
    v = gm.create_fighter(PLAYABLE_FIGHTERS[0], 11.0, 10.0)
    for st in states + [""]:
        for w in weapons:
            a.state = st
            try:
                style = collision._get_death_style_for_attacker(a, w, v)
            except Exception as e:
                print("ERRO _get_death_style", cid, st, w, e)
                continue
            if style:
                pairs.setdefault(style, set()).add(cid)
for s in literal_styles:
    pairs.setdefault(s, set())
for s, atks in list(pairs.items()):
    if not atks:
        pairs[s] = {"kenshin", "rifleman", "valerius"}
print("estilos totais:", len(pairs), "pares (atacante, estilo):", sum(len(v) for v in pairs.values()), flush=True)

NV = int(next((a.split("=")[1] for a in sys.argv[1:] if a.startswith("VICTIMS=")), "3"))
rnd = random.Random(5)
game_map = create_arena("bamboo")
fails = []
total = 0
t0 = time.time()
for style in sorted(pairs):
    for atk_id in sorted(pairs[style]):
        for vic_id in rnd.sample(victims_pool, NV):
            total += 1
            random.seed(total)
            try:
                atk = gm.create_fighter(atk_id, 10.0, 10.0)
                vic = gm.create_fighter(vic_id, 11.0, 10.0)
                atk.set_facing(vic.wx, vic.wy); vic.set_facing(atk.wx, atk.wy)
                cam = Camera(target_wx=10.5, target_wy=10.0)
                cd = CinematicDirector()
                particles = []
                vic.hp = 0; vic.is_alive = False; vic.state = "DEAD"
                cd.trigger_fatal_strike(atk, vic, style, (1.0, 0.0))
                dt = 1 / 30
                for fr in range(450):
                    cd.update(dt, game_map, particles)
                    if cd.is_frozen() or cd.is_active or cd.letterbox_prog > 0.01:
                        cd.apply_camera(cam, dt)
                    particles = [p for p in particles if p.update(dt)]
                    if fr % 6 == 0:
                        screen.fill((10, 12, 14))
                        game_map.render_terrain(screen, cam, 0.0)
                        for obj in (atk, vic):
                            obj.render(screen, cam)
                        for c in cd.corpses:
                            c.render(screen, cam)
                        for p in particles[:150]:
                            if hasattr(p, "render"):
                                p.render(screen, cam)
                        cd.render_world_effects(screen, cam)
                        cd.apply_cinematic_filter(screen)
                        if cd.letterbox_prog > 0.005:
                            cd.render_letterbox(screen)
                    if not (cd.is_active or cd.is_frozen() or cd.letterbox_prog > 0.01 or getattr(cd, "pending_corpse", None) or getattr(cd, "delayed_death_timer", 0) > 0) and fr > 20:
                        break
            except Exception as e:
                tb = traceback.format_exc().strip().splitlines()
                key = (style, atk_id, vic_id, tb[-1])
                fails.append((key, "\n".join(tb[-6:])))
                print(f"FAIL {style} atk={atk_id} vic={vic_id}: {tb[-1]}", flush=True)
print(f"\nTOTAL sims={total} falhas={len(fails)} t={time.time()-t0:.0f}s")
seen = {}
for key, tb in fails:
    seen.setdefault((key[0], key[3]), []).append(key[1:3])
for (style, msg), who in seen.items():
    print(f"- {style}: {msg}  ({len(who)} combos, ex.: {who[:3]})")
if fails:
    print("\nEXEMPLO DE TRACEBACK:\n" + fails[0][1])
