import os, sys, traceback
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
sys.path.insert(0, "/Users/thiagocarvalho/Public/SamuraiEdge")
import pygame; pygame.init(); pygame.display.set_mode((1280,720))
from src.world.arenas import create_arena
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
arena = create_arena("mist_temple")
(a,b),(c,d) = arena.pick_spawns(min_distance=7.0)
p1, p2 = RedSamurai(a,b), BlueSamurai(c,d)
particles, banners = [], []
try:
    for i in range(60*30):   # 30 s a 60 FPS, sem lutadores atacando
        arena.update(1/60, [p1, p2], None, particles, banners, None)
    print("OK sem crash em 30s")
except Exception:
    traceback.print_exc()
