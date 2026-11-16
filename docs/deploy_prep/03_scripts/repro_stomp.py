import os, sys, traceback
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
sys.path.insert(0, "/Users/thiagocarvalho/Public/SamuraiEdge")
import pygame; pygame.init(); pygame.display.set_mode((1280,720))
from src.entities.goro import GoroFarmer
from src.entities.red_samurai import RedSamurai
from src.effects.cinematic_director import CinematicDirector
from src.world.arenas import create_arena
arena = create_arena("rice_paddies")
g = GoroFarmer(10.0, 10.0); v = RedSamurai(11.0, 10.0)
cd = CinematicDirector()
particles=[]
v.hp = 0; v.is_alive = False
cd.trigger_fatal_strike(g, v, "EARTH_STOMP_CRUSH", (1.0, 0.0))
try:
    for i in range(600):
        cd.update(1/60, arena, particles)
        if not (cd.is_active or cd.is_frozen()): break
    print("OK frames", i)
except Exception:
    print("CRASH frame", i); traceback.print_exc()
