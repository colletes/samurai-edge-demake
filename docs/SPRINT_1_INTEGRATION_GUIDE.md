"""
Sprint 1 Integration Guide — Quick reference for using new UI components in main.py

New UI Components (Sprint 1):
  - MainMenuEnhanced: Elegant centered menu with animations
  - EnhancedSettingsMenu: Visual settings with sliders, toggles, selects
  - Title Screen: Already integrated, now with animation support

Dependencies (Sprint 0 — already created):
  - FontManager: Centralized text rendering with effects
  - PanelRenderer: 5 reusable panel styles (Ornate, Scroll, Lacquer, Ink, Shrine)
  - Animations: Tweening engine with easing curves and transitions

---

## Quick Integration Example

```python
# In main.py or your game loop:

from src.ui.main_menu_enhanced import MainMenu, MenuAction
from src.ui.settings_menu_enhanced import EnhancedSettingsMenu
from src.ui.title_screen import SumieTitleScreen

class GameState(Enum):
    TITLE = "title"
    MAIN_MENU = "main_menu"
    SETTINGS = "settings"
    GAME = "game"
    QUIT = "quit"

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    state = GameState.TITLE
    title_screen = SumieTitleScreen()
    main_menu = None
    settings_menu = None
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # State machine
        if state == GameState.TITLE:
            title_screen.update(dt)
            title_screen.render(screen)
            
            # Check if title is finished (player can skip after 1 second)
            if title_screen.finished:
                state = GameState.MAIN_MENU
                main_menu = MainMenu()
        
        elif state == GameState.MAIN_MENU:
            action = main_menu.update(dt, events)
            main_menu.render(screen)
            
            if action == MenuAction.PLAY:
                state = GameState.GAME
                # Initialize game here
            elif action == MenuAction.SETTINGS:
                state = GameState.SETTINGS
                settings_menu = EnhancedSettingsMenu()
            elif action == MenuAction.MANUAL:
                # Open manual viewer
                pass
            elif action == MenuAction.ABOUT:
                # Open about/credits screen
                pass
            elif action == MenuAction.QUIT:
                running = False
        
        elif state == GameState.SETTINGS:
            if settings_menu.update(dt, events):
                state = GameState.MAIN_MENU
                # Settings saved automatically
            
            settings_menu.render(screen)
        
        elif state == GameState.GAME:
            # Your game loop here
            pass
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
```

---

## Component API Reference

### MainMenuEnhanced

```python
from src.ui.main_menu_enhanced import MainMenu, MenuAction

menu = MainMenu()

# In update loop:
action = menu.update(dt, events)

if action == MenuAction.PLAY:
    print("Start game")
elif action == MenuAction.SETTINGS:
    print("Open settings")
elif action == MenuAction.MANUAL:
    print("Open manual")
elif action == MenuAction.ABOUT:
    print("Show credits")
elif action == MenuAction.QUIT:
    print("Exit game")

# Render:
menu.render(screen_surface)
```

**Features:**
- Automatically handles keyboard (↑/↓, Enter, Esc), gamepad (D-pad, A/B), mouse
- 5 menu items with smooth hover animations
- Entrance fade-in animation (0.8s)
- Ornate background with subtle parallax
- Selection indicators (animated triangles)

### EnhancedSettingsMenu

```python
from src.ui.settings_menu_enhanced import EnhancedSettingsMenu

settings = EnhancedSettingsMenu()

# In update loop:
should_close = settings.update(dt, events)

if should_close:
    print("Settings closed, changes saved")

# Render (renders with semi-transparent overlay):
settings.render(screen_surface)
```

**Sections:**
- **Audio:** Master Volume, Music Volume, SFX Volume (sliders)
- **Video:** Fullscreen (toggle), V-Sync (toggle)
- **Gameplay:** Language (English/Português/日本語), Gamepad Rumble (toggle)

**Input:**
- Keyboard: ↑/↓ navigate, ←/→ adjust, Enter toggle, Esc close
- Gamepad: D-Pad ↑/↓ navigate, ← → adjust, B close
- Mouse: Click to focus, then ←/→ to adjust

**Auto-saves** to `settings.json` on close.

### FontManager (Sprint 0)

```python
from src.ui.font_manager import FontManager, FontSize, FontFamily, TextAlign

fm = FontManager()
fm.load_fonts()

# Render text with effects
surface = fm.render(
    text="Hello",
    size=FontSize.HEADING,  # or EPIC, BODY, SMALL
    family=FontFamily.HEADING,  # or BODY
    color=(255, 200, 100),
    shadow=True,
    shadow_color=(26, 26, 26),
    shadow_offset=(2, 2),
    glow=True,
    glow_color=(255, 220, 150),
    glow_width=3,
    outline=False
)

screen.blit(surface, (x, y))
```

### PanelRenderer (Sprint 0)

```python
from src.ui.panel_renderer import PanelRenderer, PanelStyle

pr = PanelRenderer()

# Render ornate panel
panel = pr.render_panel(
    width=400,
    height=300,
    style=PanelStyle.ORNATE_FRAME,  # or SCROLL, LACQUER, INK_WASH, SHRINE_GATE
    bg_color=(42, 42, 42),
    border_color=(201, 168, 118),
    accent_color=(230, 154, 60),
    shadow=False
)

screen.blit(panel, (x, y))
```

**Panel Styles:**
- `ORNATE_FRAME`: Gold/bronze decorative corners
- `PAPER_SCROLL`: Aged parchment with rolled edges
- `LACQUER_PANEL`: Glossy, layered 3D effect
- `INK_WASH`: Transparent, watercolor edges
- `SHRINE_GATE`: Torii architectural, grid pattern

### Animations (Sprint 0)

```python
from src.ui.animations import Tween, Easing, UIAnimator

# Basic tween
tween = Tween(start=0.0, end=1.0, duration=1.0, easing=Easing.EASE_OUT_QUAD)

while not tween.finished:
    value = tween.update(dt)
    print(f"Progress: {value}")  # 0.0 -> 1.0

# UIAnimator helpers
pulse = UIAnimator.pulse(duration=1.0, min_alpha=0.5, max_alpha=1.0)
while not pulse.finished:
    pulse.update(dt)
    alpha = pulse.get_progress()  # 0.5 -> 1.0 -> 0.5 -> ...

# Screen transitions
transition = ScreenTransition(TransitionEffect.FADE, duration=0.5)
transition.update(dt)
progress = transition.get_progress()  # 0.0 -> 1.0
```

**Easing Curves:**
- `LINEAR`
- `EASE_IN/OUT_QUAD/CUBIC`
- `EASE_IN/OUT_BOUNCE/ELASTIC`

---

## Integration Checklist

- [ ] Import MainMenuEnhanced and EnhancedSettingsMenu in main.py
- [ ] Add GameState enum with TITLE, MAIN_MENU, SETTINGS, GAME states
- [ ] Implement state machine loop (see example above)
- [ ] Test keyboard navigation (↑/↓, Enter, Esc)
- [ ] Test gamepad navigation (D-Pad, A/B buttons)
- [ ] Test mouse interactions (hover, click)
- [ ] Verify settings persist to settings.json
- [ ] Check frame rate at 60 FPS on target platform
- [ ] Test on different screen resolutions (1280x720, 1920x1080, mobile)

---

## File Locations (Sprint 1)

```
src/ui/
├── title_screen.py              (existing, Sumi-E styled)
├── main_menu_enhanced.py        (NEW)
├── settings_menu_enhanced.py    (NEW)
├── font_manager.py              (Sprint 0)
├── panel_renderer.py            (Sprint 0)
├── animations.py                (Sprint 0)
├── fonts.py                     (existing)
├── __init__.py
```

```
assets/design/
├── color_palettes.json          (Sprint 0)
```

---

## Notes

- All new UI modules are **standalone** — no changes to existing game code needed yet
- Color scheme uses `assets/design/color_palettes.json` (loaded automatically)
- Font rendering uses system fonts + custom Shojoru/Noto Sans JP if available
- Panel rendering is **procedural** — no external image assets required
- Animations use simple **Tween** system — math-based, very efficient
- All modules support **keyboard, gamepad, and mouse** input
- Ready for **mobile** scaling (responsive layout)

