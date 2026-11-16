"""Soak de perigos por arena: cada arena (incluindo a do chefe) por N segundos simulados com 2 lutadores andando aleatoriamente,
render de terreno/props/perigos/overhead a cada K frames. Uso: t_hazards.py [SECONDS=120] [ARENA=id]"""
import os, sys, math, time, random, traceback
os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
PROJECT = "/Users/thiagocarvalho/Public/SamuraiEdge"
sys.path.insert(0, PROJECT)
os.chdir("/tmp")
import pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
import main as gm
from src.world.arenas import ARENA_SPECS, HIDDEN_ARENA_SPECS, create_arena
from src.isometric.camera import Camera
from src.effects.cinematic_director import CinematicDirector
from src.effects.lighting import ArenaLighting
from src.effects.fog import FogVolume
from src.effects.terrain_particles import TerrainFX
from src.world.arena_cache import get_prop_cache, clear_arena_caches
from src.roster import PLAYABLE_FIGHTERS
from src.entities.samurai import STATE_FALL

SECONDS = float(next((a.split("=")[1] for a in sys.argv[1:] if a.startswith("SECONDS=")), "120"))
ONLY = next((a.split("=")[1] for a in sys.argv[1:] if a.startswith("ARENA=")), None)
arenas = list(ARENA_SPECS) + list(HIDDEN_ARENA_SPECS)
if ONLY:
    arenas = [ONLY]
fails = []
t0 = time.time()
for ai, aid in enumerate(arenas):
    rnd = random.Random(100 + ai)
    random.seed(100 + ai)
    try:
        arena = create_arena(aid)
        (x1, y1), (x2, y2) = arena.pick_spawns(min_distance=7.0)
        c1 = PLAYABLE_FIGHTERS[(ai * 5) % 24]; c2 = PLAYABLE_FIGHTERS[(ai * 5 + 7) % 24]
        p1 = gm.create_fighter(c1, x1, y1); p2 = gm.create_fighter(c2, x2, y2)
        cam = arena.attach_camera(Camera(target_wx=(x1 + x2) / 2, target_wy=(y1 + y2) / 2))
        particles, banners, projectiles = [], [], []
        cd = CinematicDirector()
        light = ArenaLighting(arena)
        fog = arena.fog = FogVolume(arena)
        tfx = TerrainFX()
        clear_arena_caches()
        queue = gm.build_static_render_queue(arena)
        pc = get_prop_cache()
        dt = 1 / 30
        gt = 0.0
        dirs = [(0, 0)]
        fell = 0
        n = int(SECONDS / dt)
        for fr in range(n):
            gt += dt
            if fr % 20 == 0:
                dirs = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(2)]
                if rnd.random() < 0.3:
                    dirs = [(0.0, 0.0), (0.0, 0.0)]
            for f, d in ((p1, dirs[0]), (p2, dirs[1])):
                if not f.is_alive:
                    continue
                if f.state != STATE_FALL:
                    f.apply_movement(d[0], d[1], dt, arena)
            if arena.has_updates:
                arena.update(dt, [p1, p2], cam, particles, banners, cd)
            if arena.dispel_requested:
                arena.dispel_requested = False
                fog.dispel()
            for f in (p1, p2):
                opp = p2 if f is p1 else p1
                if f.state == STATE_FALL:
                    f.update_pit(dt, arena, particles, banners)
                    continue
                gm_update = None
                # mesma cadeia de despacho de main.py (ver run_game)
                from src.entities.pirate import PirateSwordswoman
                from src.entities.saitou_samurai import SaitouSamurai
                from src.entities.rifleman import Rifleman
                from src.entities.kabuki import Kabuki
                from src.entities.musketeer import Musketeer
                from src.entities.gray_ninja import GrayNinja
                from src.entities.blue_samurai import BlueSamurai
                from src.entities.kyudo_archer import KyudoArcher
                from src.entities.ren_monk import RenMonk
                from src.entities.chiyo_kunoichi import ChiyoKunoichi
                from src.entities.benkei import BenkeiSamurai
                from src.entities.orin import OrinMinstrel
                if isinstance(f, PirateSwordswoman): f.update(dt, arena, particles, opponent=opp, banners=banners)
                elif isinstance(f, (SaitouSamurai, Rifleman, Kabuki, Musketeer, GrayNinja)): f.update(dt, arena, particles)
                elif isinstance(f, (BlueSamurai, KyudoArcher)): f.update(dt, arena, particles, projectiles)
                elif isinstance(f, (RenMonk, ChiyoKunoichi)): f.update(dt, arena, particles, opponent=opp)
                elif isinstance(f, BenkeiSamurai): f.update(dt, arena, particles, opponent=opp, banners=banners, projectiles=projectiles)
                elif isinstance(f, OrinMinstrel): f.update(dt, arena, particles, opponent=opp, projectiles=projectiles, banners=banners)
                elif hasattr(f, "summon") or f.__class__.__name__ in ("GoroFarmer", "IchiBlade", "ValeriusNecromancer", "SeimeiOnmyoji", "DaikiPilgrim", "AoiHuntress", "RaidenSumo", "HendrikaAlchemist"):
                    f.update(dt, arena, particles, opponent=opp, projectiles=projectiles, banners=banners, cinematic_director=cd)
                else:
                    f.update(dt, arena)
                if f.update_pit(dt, arena, particles, banners):
                    fell += 1
                tfx.step(f, arena, dt)
            # reviver quem morreu/caiu para manter o soak (teleporta de volta)
            for f, (sx, sy) in ((p1, (x1, y1)), (p2, (x2, y2))):
                if (not f.is_alive) or getattr(f, "fell_into_pit", False):
                    new = gm.create_fighter(c1 if f is p1 else c2, sx, sy)
                    if f is p1: p1 = new
                    else: p2 = new
            cd.update(dt, arena, particles)
            particles = [p for p in particles if p.update(dt)][:150]
            banners = [b for b in banners if b.update(dt)]
            tfx.update(dt, arena, gt); fog.update(dt, gt)
            mid_x, mid_y = (p1.wx + p2.wx) / 2, (p1.wy + p2.wy) / 2
            cam.update_combat_framing(p1, p2, arena, dt, is_boss=False, projectiles=projectiles)
            if fr % 12 == 0:
                screen.fill(arena.bg_color)
                arena.render_terrain(screen, cam, gt)
                items = [(cam.depth(*gm.static_item_center(t_, o_)), t_, o_) for _, t_, o_ in queue]
                for h in getattr(arena, "hazards", []):
                    if hasattr(h, "get_render_items"):
                        items.extend(h.get_render_items(cam))
                items.append((cam.depth(p1.wx, p1.wy), "fighter", p1)); items.append((cam.depth(p2.wx, p2.wy), "fighter", p2))
                for p in particles:
                    if hasattr(p, "wx"): items.append((cam.depth(p.wx, p.wy), "particle", p))
                items.extend(fog.queue_items(cam))
                items.sort(key=lambda it: it[0])
                for _, t_, o_ in items:
                    if t_ in ("rock", "well", "tree", "torii", "bamboo", "building") and pc.render_prop(screen, cam, t_, o_, gt):
                        continue
                    if t_ == "fighter" and (getattr(o_, "fell_into_pit", False)):
                        continue
                    if t_ in ("bamboo", "building", "lantern") or getattr(o_, "animated", False):
                        o_.render(screen, cam, gt)
                    else:
                        o_.render(screen, cam)
                for b in banners:
                    b.render(screen, cam, pygame.font.Font(None, 26))
                arena.render_overhead(screen, cam, gt)
                light.render(screen, cam, gt)
        print(f"OK   {aid:22s} {SECONDS:.0f}s sim; quedas={fell}; hazards={[type(h).__name__ for h in getattr(arena, 'hazards', [])]}", flush=True)
    except Exception:
        tb = traceback.format_exc().strip().splitlines()
        fails.append((aid, tb[-1], "\n".join(tb[-8:])))
        print(f"FAIL {aid}: {tb[-1]}\n      " + "\n      ".join(tb[-8:]), flush=True)
print(f"\nTOTAL arenas={len(arenas)} falhas={len(fails)} t={time.time()-t0:.0f}s")
