import os, sys, traceback
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
sys.path.insert(0, "/Users/thiagocarvalho/Public/SamuraiEdge")
import pygame; pygame.init(); screen = pygame.display.set_mode((1280,720))
from src.config import DEFAULT_CONTROLS
from src.input import TouchControls
from src.ui.settings_menu import SettingsMenu
f = [pygame.font.Font(None, s) for s in (48, 26, 20)]
m = SettingsMenu(dict(DEFAULT_CONTROLS), touch_controls=TouchControls(), ai_difficulty="normal")
m.open(subscreen="CONTROLS") if "subscreen" in SettingsMenu.open.__code__.co_varnames else m.open()
m.render(screen, *f)                      # render normal OK
print("botao touch editor rect:", m.touch_editor_btn_rect)
# clique do mouse no botao "PERSONALIZAR BOTOES TOUCH (HUD)"
r = m.touch_editor_btn_rect
for t in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
    ev = pygame.event.Event(t, pos=r.center, button=1, rel=(0,0), buttons=(0,0,0)) 
    m.handle_event(ev)
print("touch_editor.is_open =", m.touch_editor.is_open)
try:
    m.render(screen, *f)
    print("render OK")
except Exception:
    traceback.print_exc()
