"""
Character Card Component — Enhanced visual representation of selectable characters.

Renders ornate character cards with:
- Lacquer panel frames (from PanelRenderer)
- Character portrait + name
- Stat bars (Speed, Range, Defense)
- Archetype badge
- Smooth animations (hover, selection)
"""

import pygame
import math
from enum import Enum
from typing import Optional, Tuple
from dataclasses import dataclass

# Import design system components
from src.ui.font_manager import FontManager, FontSize, FontFamily
from src.ui.panel_renderer import PanelRenderer, PanelStyle
from src.ui.animations import UIAnimator, Easing
from src.config import (
    COLOR_GOLD, COLOR_WHITE, COLOR_RED_AURA, COLOR_BLUE_AURA,
    COLOR_YELLOW_AURA
)


class CardState(Enum):
    """Visual state of a character card."""
    NORMAL = "normal"          # Unselected, not hovered
    HOVERED = "hovered"        # Mouse/gamepad hovering
    SELECTED = "selected"      # Currently selected
    LOCKED = "locked"          # Not available (greyed out)


@dataclass
class StatBar:
    """A simple stat visualization."""
    label: str          # "Speed", "Range", "Defense"
    value: int         # 1-5 (number of filled segments)
    max_value: int = 5 # Usually 5
    color: Tuple[int, int, int] = COLOR_GOLD


class CharacterCard:
    """
    Visual representation of a selectable character.
    
    Usage:
        card = CharacterCard(
            char_id="kenshin",
            name="Kenshin",
            archetype="Iai Master",
            portrait_surface=portrait_img,
            stats=[
                StatBar("Speed", 5, color=COLOR_GOLD),
                StatBar("Range", 2),
                StatBar("Defense", 1),
            ]
        )
        
        # In game loop:
        card.update(dt, state)
        card.render(screen, x, y)
    """
    
    CARD_WIDTH = 160
    CARD_HEIGHT = 240
    FRAME_THICKNESS = 3
    
    def __init__(
        self,
        char_id: str,
        name: str,
        archetype: str,
        portrait_surface: Optional[pygame.Surface] = None,
        stats: Optional[list] = None,
        color_accent: Tuple[int, int, int] = COLOR_GOLD,
    ):
        self.char_id = char_id
        self.name = name
        self.archetype = archetype
        self.portrait = portrait_surface
        self.stats = stats or []
        self.accent_color = color_accent
        
        # Animation state
        self.state = CardState.NORMAL
        self.hover_scale = 1.0
        self.select_glow_alpha = 0.0
        self.select_pulse = 0.0
        self.animation_time = 0.0
        
        # Font manager reference
        self.font_mgr = FontManager()
    
    def update(self, dt: float, state: CardState):
        """Update animation state based on card state."""
        self.animation_time += dt
        self.state = state
        
        # Smooth hover scale
        target_scale = 1.1 if state == CardState.HOVERED else 1.0
        self.hover_scale += (target_scale - self.hover_scale) * 0.15
        
        # Selection glow animation
        if state == CardState.SELECTED:
            self.select_pulse = 0.5 + 0.5 * math.sin(self.animation_time * 4.0)
            self.select_glow_alpha = 200 + 55 * math.sin(self.animation_time * 3.5)
        else:
            self.select_glow_alpha = 0.0
            self.select_pulse = 0.0
    
    def render(self, screen: pygame.Surface, x: float, y: float):
        """Render the card at position (x, y)."""
        # Create card surface
        card_surf = pygame.Surface(
            (self.CARD_WIDTH, self.CARD_HEIGHT),
            pygame.SRCALPHA
        )
        
        # Draw ornate frame (lacquer style)
        self._draw_frame(card_surf)
        
        # Draw portrait (if available)
        if self.portrait:
            self._draw_portrait(card_surf)
        else:
            # Placeholder
            self._draw_placeholder(card_surf)
        
        # Draw name
        self._draw_name(card_surf)
        
        # Draw archetype badge
        self._draw_badge(card_surf)
        
        # Draw stat bars
        self._draw_stats(card_surf)
        
        # Apply scale transformation based on hover state
        if abs(self.hover_scale - 1.0) > 0.01:
            scaled_width = int(self.CARD_WIDTH * self.hover_scale)
            scaled_height = int(self.CARD_HEIGHT * self.hover_scale)
            card_surf = pygame.transform.scale(card_surf, (scaled_width, scaled_height))
            
            # Re-center scaled card
            offset_x = (self.CARD_WIDTH - scaled_width) // 2
            offset_y = (self.CARD_HEIGHT - scaled_height) // 2
            x += offset_x
            y += offset_y
        
        # Blit card to screen
        screen.blit(card_surf, (int(x), int(y)))
        
        # Draw selection glow (on top)
        if self.state == CardState.SELECTED and self.select_glow_alpha > 0:
            self._draw_selection_glow(screen, x, y)
    
    def _draw_frame(self, surface: pygame.Surface):
        """Draw ornate lacquer-style frame."""
        # Use PanelRenderer to draw the frame
        pr = PanelRenderer()
        frame = pr.render_panel(
            self.CARD_WIDTH,
            self.CARD_HEIGHT,
            PanelStyle.LACQUER_PANEL,
            bg_color=(24, 20, 22),           # Dark background
            border_color=self.accent_color,
            accent_color=self.accent_color,
        )
        surface.blit(frame, (0, 0))
    
    def _draw_portrait(self, surface: pygame.Surface):
        """Draw character portrait in the card."""
        if not self.portrait:
            return
        
        # Scale portrait to fit card (with padding)
        padding = 8
        portrait_area = (
            self.CARD_WIDTH - 2 * padding,
            self.CARD_HEIGHT // 2 - padding
        )
        
        portrait_scaled = pygame.transform.smoothscale(
            self.portrait,
            portrait_area
        )
        
        # Center portrait horizontally, place in upper half
        x = (self.CARD_WIDTH - portrait_scaled.get_width()) // 2
        y = padding
        
        surface.blit(portrait_scaled, (x, y))
    
    def _draw_placeholder(self, surface: pygame.Surface):
        """Draw placeholder if no portrait available."""
        # Simple colored rectangle
        rect = pygame.Rect(8, 8, self.CARD_WIDTH - 16, self.CARD_HEIGHT // 2 - 12)
        pygame.draw.rect(surface, self.accent_color, rect, 1)
        
        # Draw "?" text
        fm = FontManager()
        text_surf = fm.render("?", FontSize.HEADING, FontFamily.HEADING, self.accent_color)
        x = self.CARD_WIDTH // 2 - text_surf.get_width() // 2
        y = self.CARD_HEIGHT // 4 - text_surf.get_height() // 2
        surface.blit(text_surf, (x, y))
    
    def _draw_name(self, surface: pygame.Surface):
        """Draw character name below portrait."""
        fm = FontManager()
        name_surf = fm.render(
            self.name.upper(),
            FontSize.BODY,
            FontFamily.HEADING,
            COLOR_WHITE,
            outline=True,
            outline_color=self.accent_color,
            outline_width=1
        )
        
        x = (self.CARD_WIDTH - name_surf.get_width()) // 2
        y = self.CARD_HEIGHT // 2 + 4
        
        surface.blit(name_surf, (x, y))
    
    def _draw_badge(self, surface: pygame.Surface):
        """Draw archetype/style badge."""
        fm = FontManager()
        badge_surf = fm.render(
            self.archetype,
            FontSize.TINY,
            FontFamily.BODY,
            self.accent_color,
        )
        
        # Draw badge at bottom of card
        badge_y = self.CARD_HEIGHT - 24
        x = (self.CARD_WIDTH - badge_surf.get_width()) // 2
        
        # Background box for badge
        badge_box = pygame.Rect(
            x - 4, badge_y - 2,
            badge_surf.get_width() + 8,
            badge_surf.get_height() + 4
        )
        pygame.draw.rect(surface, (30, 25, 28), badge_box)
        pygame.draw.rect(surface, self.accent_color, badge_box, 1)
        
        surface.blit(badge_surf, badge_box.topleft)
    
    def _draw_stats(self, surface: pygame.Surface):
        """Draw stat bars at bottom of card."""
        stat_start_y = self.CARD_HEIGHT - 50
        stat_height = 8
        stat_gap = 3
        
        for i, stat in enumerate(self.stats[:3]):  # Max 3 stats displayed
            y = stat_start_y + i * (stat_height + stat_gap)
            self._draw_stat_bar(surface, stat, 10, y, stat_height)
    
    def _draw_stat_bar(self, surface: pygame.Surface, stat: StatBar, x: int, y: int, stat_height: int = 8):
        """Draw a single stat bar (label + segments)."""
        fm = FontManager()
        
        # Draw label
        label_surf = fm.render(
            stat.label,
            FontSize.TINY,
            FontFamily.BODY,
            stat.color
        )
        surface.blit(label_surf, (x, y - 2))
        
        # Draw bar segments (1-5 filled squares)
        bar_x = x + 45
        segment_width = 8
        segment_gap = 1
        
        for segment_idx in range(stat.max_value):
            segment_rect = pygame.Rect(
                bar_x + segment_idx * (segment_width + segment_gap),
                y,
                segment_width,
                stat_height
            )
            
            # Filled or empty
            if segment_idx < stat.value:
                pygame.draw.rect(surface, stat.color, segment_rect)
            else:
                pygame.draw.rect(surface, (50, 45, 48), segment_rect, 1)
    
    def _draw_selection_glow(self, screen: pygame.Surface, x: float, y: float):
        """Draw animated selection glow around card."""
        glow_surface = pygame.Surface(
            (self.CARD_WIDTH + 8, self.CARD_HEIGHT + 8),
            pygame.SRCALPHA
        )
        
        # Outer glow
        glow_rect = pygame.Rect(0, 0, glow_surface.get_width(), glow_surface.get_height())
        glow_color = (
            int(self.accent_color[0] * self.select_pulse),
            int(self.accent_color[1] * self.select_pulse),
            int(self.accent_color[2] * self.select_pulse),
            int(self.select_glow_alpha)
        )
        
        pygame.draw.rect(glow_surface, glow_color, glow_rect, 2)
        
        # Inner frame for double glow effect
        inner_rect = pygame.Rect(2, 2, glow_surface.get_width() - 4, glow_surface.get_height() - 4)
        pygame.draw.rect(glow_surface, glow_color, inner_rect, 1)
        
        screen.blit(glow_surface, (int(x - 4), int(y - 4)))
    
    def get_rect(self, x: float, y: float) -> pygame.Rect:
        """Get bounding rectangle for collision/hover detection."""
        return pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)
