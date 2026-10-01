"""
Main Menu — Elegant, centered vertical menu with ornate frame, hover effects, and animations.

Features:
  - Centered menu with ornate lacquer panel frame
  - Menu options: Play, Settings, Manual, Quit
  - Hover highlights with glow + scale-up animation
  - Watercolor ink-wash background with subtle parallax
  - Decorative corner ornaments
  - Smooth transitions between menu items
"""

import pygame
import json
import os
from typing import Optional, List, Callable
from enum import Enum
from src.ui.animations import UIAnimator, Tween, Easing, AnimationSequence
from src.ui.panel_renderer import PanelRenderer, PanelStyle
from src.ui.font_manager import FontManager, FontSize, FontFamily, TextAlign
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_BG
from src.i18n import t


class MenuAction(Enum):
    """Menu actions that can be triggered."""
    PLAY = "play"
    SETTINGS = "settings"
    MANUAL = "manual"
    ABOUT = "about"
    QUIT = "quit"
    NONE = "none"


class MenuItem:
    """Single menu item with hover state and animations."""
    
    def __init__(
        self,
        label: str,
        action: MenuAction,
        y_pos: int,
        width: int = 300,
        height: int = 60
    ):
        self.label = label
        self.action = action
        self.y_pos = y_pos
        self.width = width
        self.height = height
        
        # Center horizontally
        self.x_pos = (SCREEN_WIDTH - width) // 2
        self.rect = pygame.Rect(self.x_pos, y_pos, width, height)
        
        # Hover state
        self.is_hovered = False
        self.hover_tween = Tween(0.0, 1.0, 0.2, Easing.EASE_OUT_QUAD)
        self.hover_tween.finished = True  # Start as not hovered
        
        # Scale animation
        self.scale = 1.0
        self.scale_tween = Tween(1.0, 1.05, 0.2, Easing.EASE_OUT_BOUNCE)
        self.scale_tween.finished = True
    
    def set_hover(self, hovered: bool):
        """Set hover state and trigger animation."""
        if hovered and not self.is_hovered:
            self.is_hovered = True
            self.hover_tween = Tween(0.0, 1.0, 0.2, Easing.EASE_OUT_QUAD)
            self.scale_tween = Tween(1.0, 1.05, 0.2, Easing.EASE_OUT_BOUNCE)
        elif not hovered and self.is_hovered:
            self.is_hovered = False
            self.hover_tween = Tween(1.0, 0.0, 0.2, Easing.EASE_IN_QUAD)
            self.scale_tween = Tween(1.05, 1.0, 0.2, Easing.EASE_IN_QUAD)
    
    def update(self, dt: float):
        """Update hover animations."""
        if not self.hover_tween.finished:
            self.hover_tween.update(dt)
        
        if not self.scale_tween.finished:
            self.scale = self.scale_tween.update(dt)
    
    def get_hover_alpha(self) -> float:
        """Get hover animation progress (0.0 to 1.0)."""
        return self.hover_tween.current if not self.hover_tween.finished else (1.0 if self.is_hovered else 0.0)
    
    def check_collision(self, x: int, y: int) -> bool:
        """Check if point (x, y) is over this menu item."""
        return self.rect.collidepoint(x, y)


class MainMenu:
    """
    Main menu with elegant layout, animations, and options.
    
    Usage:
        menu = MainMenu()
        
        while game_running:
            events = pygame.event.get()
            action = menu.update(dt, events)
            
            if action == MenuAction.PLAY:
                # Start game
                pass
            elif action == MenuAction.SETTINGS:
                # Open settings
                pass
            
            menu.render(screen)
            pygame.display.flip()
    """
    
    def __init__(self):
        self.fm = FontManager()
        self.fm.load_fonts()
        
        self.pr = PanelRenderer()
        
        # Load color palette
        palette_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "assets", "design", "color_palettes.json"
        )
        self.palette = self._load_palette(palette_path)
        
        # Menu items
        self.items: List[MenuItem] = []
        self._create_menu_items()
        
        # Selection index
        self.selected_index = 0
        
        # Background animation
        self.bg_offset = 0.0
        self.bg_wave_offset = 0.0
        
        # Background panel (pre-rendered)
        self.bg_panel: Optional[pygame.Surface] = None
        self._prepare_background()
        
        # Entrance animation
        self.entrance_tween = Tween(0.0, 1.0, 0.8, Easing.EASE_OUT_CUBIC)
        self.menu_fade_in = False
    
    def _load_palette(self, path: str) -> dict:
        """Load color palette from JSON."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            # Fallback palette if file not found
            return {
                "palettes": {
                    "generic_ui": {
                        "primary": "#2a2a2a",
                        "accent": "#c9a876",
                        "highlight": "#ffffff",
                        "ui_frame": "#f5f1ed",
                        "ui_frame_dark": "#3a3a3a",
                        "ui_text": "#1a1a1a"
                    }
                }
            }
    
    def _create_menu_items(self):
        """Create menu items."""
        items_data = [
            (t("menu_play"), MenuAction.PLAY),
            (t("menu_settings"), MenuAction.SETTINGS),
            (t("menu_manual"), MenuAction.MANUAL),
            (t("menu_about"), MenuAction.ABOUT),
            (t("menu_quit"), MenuAction.QUIT),
        ]
        
        # Calculate spacing
        total_items = len(items_data)
        item_height = 60
        item_spacing = 20
        total_height = total_items * item_height + (total_items - 1) * item_spacing
        
        start_y = (SCREEN_HEIGHT - total_height) // 2
        
        for i, (label, action) in enumerate(items_data):
            y = start_y + i * (item_height + item_spacing)
            item = MenuItem(label, action, y, width=300, height=item_height)
            self.items.append(item)
    
    def _prepare_background(self):
        """Pre-render ornate background panel."""
        self.bg_panel = self.pr.render_panel(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            style=PanelStyle.INK_WASH,
            bg_color=(42, 42, 42),
            border_color=(201, 168, 118),
            accent_color=(230, 154, 60),
            shadow=False
        )
    
    # ========================================================================
    # Update & Input
    # ========================================================================
    
    def update(self, dt: float, events: list) -> MenuAction:
        """
        Update menu state and handle input.
        
        Args:
            dt: Delta time in seconds
            events: pygame.event list
        
        Returns:
            MenuAction if an action was triggered, else MenuAction.NONE
        """
        
        # Update entrance animation
        if not self.entrance_tween.finished:
            self.entrance_tween.update(dt)
            self.menu_fade_in = True
        
        # Update background animation
        self.bg_offset += dt * 5
        if self.bg_offset > 100:
            self.bg_offset = 0
        
        self.bg_wave_offset += dt * 2
        
        # Update all menu items
        for item in self.items:
            item.update(dt)
        
        # Handle input
        action = self._handle_input(events)
        
        return action
    
    def _handle_input(self, events: list) -> MenuAction:
        """Handle keyboard, gamepad, and mouse input."""
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected_index = (self.selected_index - 1) % len(self.items)
                    self._update_selection()
                
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected_index = (self.selected_index + 1) % len(self.items)
                    self._update_selection()
                
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    return self.items[self.selected_index].action
                
                elif event.key == pygame.K_ESCAPE:
                    return MenuAction.QUIT
            
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button in [0, 7]:  # A button or Start
                    return self.items[self.selected_index].action
                elif event.button in [1, 6]:  # B button or Back
                    return MenuAction.QUIT
            
            elif event.type == pygame.JOYHATMOTION:
                if event.value[1] == -1:  # Up
                    self.selected_index = (self.selected_index - 1) % len(self.items)
                    self._update_selection()
                elif event.value[1] == 1:  # Down
                    self.selected_index = (self.selected_index + 1) % len(self.items)
                    self._update_selection()
            
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i, item in enumerate(self.items):
                    if item.check_collision(mx, my):
                        if i != self.selected_index:
                            self.selected_index = i
                            self._update_selection()
                        break
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, item in enumerate(self.items):
                    if item.check_collision(mx, my):
                        self.selected_index = i
                        return item.action
        
        return MenuAction.NONE
    
    def _update_selection(self):
        """Update hover states based on selection."""
        for i, item in enumerate(self.items):
            item.set_hover(i == self.selected_index)
    
    # ========================================================================
    # Rendering
    # ========================================================================
    
    def render(self, surface: pygame.Surface):
        """Render menu to target surface."""
        
        # Background with ink-wash effect
        if self.bg_panel:
            surface.blit(self.bg_panel, (0, 0))
        else:
            surface.fill((42, 42, 42))
        
        # Subtle scrolling background pattern
        self._draw_background_texture(surface)
        
        # Render menu items
        fade_progress = self.entrance_tween.current if self.menu_fade_in else 1.0
        
        for item in self.items:
            self._render_menu_item(surface, item, fade_progress)
        
        # Render title above menu
        self._render_title(surface, fade_progress)
        
        # Render footer with instructions
        self._render_footer(surface)
    
    def _render_menu_item(self, surface: pygame.Surface, item: MenuItem, fade_progress: float):
        """Render a single menu item with hover effects."""
        
        hover_alpha = item.get_hover_alpha()
        scale = item.scale
        
        # Calculate scaled position (scale from center)
        scaled_width = int(item.width * scale)
        scaled_height = int(item.height * scale)
        scaled_x = item.x_pos + (item.width - scaled_width) // 2
        scaled_y = item.y_pos + (item.height - scaled_height) // 2
        
        # Draw background panel
        if item.is_hovered or hover_alpha > 0.1:
            # Highlighted state
            panel_color = (80, 60, 40)
            border_color = (230, 154, 60)
            border_width = 2
        else:
            # Normal state
            panel_color = (50, 50, 50)
            border_color = (100, 100, 100)
            border_width = 1
        
        pygame.draw.rect(surface, panel_color, (scaled_x, scaled_y, scaled_width, scaled_height), border_radius=6)
        pygame.draw.rect(surface, border_color, (scaled_x, scaled_y, scaled_width, scaled_height), border_width, border_radius=6)
        
        # Draw glow effect for hovered item
        if hover_alpha > 0.05:
            glow_surface = pygame.Surface((scaled_width + 4, scaled_height + 4), pygame.SRCALPHA)
            glow_color = (230, 154, 60, int(100 * hover_alpha))
            pygame.draw.rect(glow_surface, glow_color, (0, 0, scaled_width + 4, scaled_height + 4), border_radius=8)
            surface.blit(glow_surface, (scaled_x - 2, scaled_y - 2))
        
        # Draw text
        text_alpha = int(255 * fade_progress)
        text_surface = self.fm.render(
            item.label,
            size=FontSize.HEADING,
            family=FontFamily.HEADING,
            color=(230, 154, 60) if item.is_hovered else (245, 241, 237),
            shadow=True,
            shadow_color=(26, 26, 26),
            shadow_offset=(2, 2)
        )
        
        text_surface.set_alpha(text_alpha)
        text_x = scaled_x + (scaled_width - text_surface.get_width()) // 2
        text_y = scaled_y + (scaled_height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))
        
        # Draw selection indicator
        if item.is_hovered:
            indicator_x = scaled_x - 30
            indicator_y = scaled_y + scaled_height // 2 - 8
            indicator_pts = [
                (indicator_x, indicator_y),
                (indicator_x + 16, indicator_y + 8),
                (indicator_x, indicator_y + 16)
            ]
            pygame.draw.polygon(surface, (230, 154, 60), indicator_pts)
    
    def _render_title(self, surface: pygame.Surface, fade_progress: float):
        """Render menu title above items."""
        title_text = "SAMURAI EDGE"
        
        title_surface = self.fm.render(
            title_text,
            size=FontSize.EPIC,
            family=FontFamily.HEADING,
            color=(230, 154, 60),
            glow=True,
            glow_color=(255, 200, 100),
            glow_width=4,
            shadow=True,
            shadow_color=(26, 26, 26),
            shadow_offset=(3, 3)
        )
        
        title_surface.set_alpha(int(255 * fade_progress))
        title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        title_y = 80
        surface.blit(title_surface, (title_x, title_y))
        
        # Decorative line
        line_y = title_y + title_surface.get_height() + 20
        pygame.draw.line(surface, (230, 154, 60), (200, line_y), (SCREEN_WIDTH - 200, line_y), 2)
    
    def _render_footer(self, surface: pygame.Surface):
        """Render footer with instructions."""
        footer_text = "[↑/↓] Navigate  |  [Enter] Select  |  [Esc] Quit"
        
        footer_surface = self.fm.render(
            footer_text,
            size=FontSize.SMALL,
            family=FontFamily.BODY,
            color=(150, 150, 150),
            shadow=True,
            shadow_color=(26, 26, 26),
            shadow_offset=(1, 1)
        )
        
        footer_x = SCREEN_WIDTH // 2 - footer_surface.get_width() // 2
        footer_y = SCREEN_HEIGHT - 40
        surface.blit(footer_surface, (footer_x, footer_y))
    
    def _draw_background_texture(self, surface: pygame.Surface):
        """Draw subtle scrolling background texture."""
        # Horizontal stripes for subtle movement
        stripe_height = 8
        stripe_color = (50, 50, 50)
        
        for y in range(int(-self.bg_offset), SCREEN_HEIGHT, stripe_height * 2):
            pygame.draw.line(surface, stripe_color, (0, y), (SCREEN_WIDTH, y), 1)


# ============================================================================
# Test / Example
# ============================================================================

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Main Menu Test")
    
    menu = MainMenu()
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        action = menu.update(dt, events)
        
        if action != MenuAction.NONE:
            print(f"Menu action: {action.value}")
        
        menu.render(screen)
        pygame.display.flip()
    
    pygame.quit()
