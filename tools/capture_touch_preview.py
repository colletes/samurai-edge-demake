"""
Script para capturar e validar visualmente o design dos novos botões de arcade translúcidos.
Gera um preview PNG em docs/screenshots/arcade_touch_preview.png
"""
import os
import sys
import pygame

# Headless video driver
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

pygame.init()
pygame.font.init()

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui.fonts import get_text_font, get_title_font
from src.input.touch_controls import TouchControls

screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# Fundo escuro com sutil gradiente simulando o gabinete de arcade
screen.fill((14, 16, 20))

# Grade sutil de fundo
for x in range(0, SCREEN_WIDTH, 40):
    pygame.draw.line(screen, (22, 26, 32), (x, 0), (x, SCREEN_HEIGHT), 1)
for y in range(0, SCREEN_HEIGHT, 40):
    pygame.draw.line(screen, (22, 26, 32), (0, y), (SCREEN_WIDTH, y), 1)

touch = TouchControls()
touch.has_detected_touch = True

# Simular toque ativo no analógico (inclinado para cima-direita)
touch.joystick.is_active = True
touch.joystick.knob_x = touch.joystick.center_x + 42
touch.joystick.knob_y = touch.joystick.center_y - 38

# Simular botão ATK pressionado pelo jogador
touch.btn_attack.is_down = True

font_large = get_title_font(24)
font_small = get_text_font(13)

# Renderizar estado interativo
touch.render(screen, font_large, font_small)

out_dir = os.path.join(ROOT, "docs", "screenshots")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "arcade_touch_preview.png")
pygame.image.save(screen, out_path)
print(f"Preview salvo com sucesso em: {out_path}")
