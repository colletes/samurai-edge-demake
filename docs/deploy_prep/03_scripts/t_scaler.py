import os, sys, traceback
os.environ["SDL_VIDEODRIVER"]="dummy"
sys.path.insert(0, "/Users/thiagocarvalho/Public/SamuraiEdge")
import pygame; pygame.init(); screen = pygame.display.set_mode((1280,720))
from src.input import DisplayScaler
for size in [(1280,720),(1280,800),(1920,1080),(800,600),(320,200),(1,1),(0,0),(2,2),(3,1),(1,500),(500,1),(7680,4320),(1366,768),(2560,1600)]:
    sc = DisplayScaler(1280,720)
    try:
        sc.update_window_size(*size)
        tgt = pygame.Surface((max(1,size[0]), max(1,size[1])))
        sc.render_to_screen(tgt)
        v = sc.screen_to_virtual(size[0]/2, size[1]/2)
        print("OK  ", size, "scale=%.4f" % sc.scale, "rect", tuple(sc.scaled_rect), "center->", tuple(round(x) for x in v))
    except Exception as e:
        print("FAIL", size, type(e).__name__, e)
