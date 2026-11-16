"""Testa abertura/creditos com video REAL (SDL_VIDEODRIVER trocado apos init) e dependencias opcionais bloqueadas.
Uso: t_video.py [BLOCK=mod1,mod2] [VIDEO=/caminho.mp4]"""
import os, sys, time, traceback
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"
block = [a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("BLOCK=")]
video = [a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("VIDEO=")]
for m in (block[0].split(",") if block else []):
    if m:
        sys.modules[m] = None
sys.path.insert(0, "/Users/thiagocarvalho/Public/SamuraiEdge")
os.chdir("/tmp")
import pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
os.environ["SDL_VIDEODRIVER"] = "cocoa"   # engana as guardas "headless dummy" para exercitar o caminho real de video
from src.ui.opening_video import OpeningVideoScreen
from src.arcade.arcade_credits import ArcadeCreditsScreen
from src.arcade.arcade_mode import ArcadeRun


def drive(name, screen_obj, frames=240, finished_attr="is_finished"):
    t0 = time.time()
    try:
        n = 0
        for i in range(frames):
            for ev in ([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0, unicode=" ", scancode=0)] if i == 60 else []):
                screen_obj.handle_event(ev)
            r = screen_obj.update(1 / 30)
            screen_obj.render(screen)
            n += 1
            if getattr(screen_obj, finished_attr, False) or r == "DONE":
                break
        print(f"OK   {name}: {n} frames, finished={getattr(screen_obj, finished_attr, None)}, video={getattr(screen_obj, 'video', None) is not None} ({time.time()-t0:.1f}s)")
    except Exception:
        print(f"FAIL {name}")
        traceback.print_exc()


try:
    s = OpeningVideoScreen(video[0]) if video else OpeningVideoScreen()
    print("opening: finished_at_init =", s.is_finished, "video_obj =", s.video is not None, "path =", s.video_path)
    drive("OpeningVideoScreen", s)
    s.stop()
except Exception:
    print("FAIL OpeningVideoScreen init"); traceback.print_exc()

try:
    c = ArcadeCreditsScreen()
    run = ArcadeRun(player_char="kenshin", difficulty_start=1, seed=3)
    c.open(run, 1, [])
    print("credits: video_path =", c.video_path, "video_obj =", c.video is not None)
    drive("ArcadeCreditsScreen", c, frames=400, finished_attr="active_done")
    c.stop()
except Exception:
    print("FAIL ArcadeCreditsScreen"); traceback.print_exc()
print("DONE")
