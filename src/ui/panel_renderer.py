"""
Panel Renderer — Modular, reusable UI panel/frame styles.

Provides 5 panel design systems:
  1. Ornate Frame (decorative corners, gold/bronze accents)
  2. Paper Scroll (top/bottom curl, aged parchment texture)
  3. Lacquer Panel (glossy, layered, shadow depth)
  4. Ink Wash (semi-transparent, watercolor edges)
  5. Shrine Gate (architectural, grid pattern)
"""

import pygame
from enum import Enum
from typing import Tuple, Optional


class PanelStyle(Enum):
    """Panel style types."""
    ORNATE_FRAME = "ornate_frame"
    PAPER_SCROLL = "paper_scroll"
    LACQUER_PANEL = "lacquer_panel"
    INK_WASH = "ink_wash"
    SHRINE_GATE = "shrine_gate"


class PanelRenderer:
    """
    Render UI panels/frames with various aesthetic styles.
    
    Usage:
        pr = PanelRenderer()
        surface = pr.render_panel(
            width=400,
            height=300,
            style=PanelStyle.ORNATE_FRAME,
            bg_color=(245, 241, 237),
            border_color=(58, 58, 58),
            accent_color=(201, 168, 118)
        )
        screen.blit(surface, (100, 100))
    """
    
    def __init__(self):
        self.border_thickness = 4
        self.corner_size = 20
        self.accent_width = 3
    
    def render_panel(
        self,
        width: int,
        height: int,
        style: PanelStyle = PanelStyle.LACQUER_PANEL,
        bg_color: Tuple[int, int, int] = (245, 241, 237),
        border_color: Tuple[int, int, int] = (58, 58, 58),
        accent_color: Tuple[int, int, int] = (201, 168, 118),
        shadow: bool = True
    ) -> pygame.Surface:
        """
        Render a panel of given dimensions and style.
        
        Args:
            width: Panel width in pixels
            height: Panel height in pixels
            style: Panel style type
            bg_color: Background RGB
            border_color: Border RGB
            accent_color: Accent/highlight RGB
            shadow: Whether to add drop shadow
        
        Returns:
            pygame.Surface with rendered panel
        """
        
        # Create surface with extra space for effects
        shadow_offset = 8 if shadow else 0
        total_width = width + shadow_offset
        total_height = height + shadow_offset
        
        surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        
        # Draw shadow
        if shadow:
            shadow_rect = pygame.Rect(4, 4, width, height)
            pygame.draw.rect(surface, (0, 0, 0, 80), shadow_rect, border_radius=6)
        
        # Render based on style
        if style == PanelStyle.ORNATE_FRAME:
            self._render_ornate_frame(surface, width, height, bg_color, border_color, accent_color)
        elif style == PanelStyle.PAPER_SCROLL:
            self._render_paper_scroll(surface, width, height, bg_color, border_color, accent_color)
        elif style == PanelStyle.LACQUER_PANEL:
            self._render_lacquer_panel(surface, width, height, bg_color, border_color, accent_color)
        elif style == PanelStyle.INK_WASH:
            self._render_ink_wash(surface, width, height, bg_color, border_color, accent_color)
        elif style == PanelStyle.SHRINE_GATE:
            self._render_shrine_gate(surface, width, height, bg_color, border_color, accent_color)
        
        return surface
    
    # ========================================================================
    # Style Implementations
    # ========================================================================
    
    def _render_ornate_frame(
        self,
        surface: pygame.Surface,
        width: int,
        height: int,
        bg_color: Tuple[int, int, int],
        border_color: Tuple[int, int, int],
        accent_color: Tuple[int, int, int]
    ):
        """Ornate frame with decorative corners (gold/bronze accents)."""
        
        # Background
        pygame.draw.rect(surface, bg_color, (0, 0, width, height))
        
        # Outer border
        pygame.draw.rect(surface, border_color, (0, 0, width, height), self.border_thickness)
        
        # Inner accent line (thin gold line inside border)
        inner_rect = pygame.Rect(
            self.border_thickness + 2,
            self.border_thickness + 2,
            width - (self.border_thickness + 2) * 2,
            height - (self.border_thickness + 2) * 2
        )
        pygame.draw.rect(surface, accent_color, inner_rect, self.accent_width)
        
        # Decorative corners (small ornaments at each corner)
        corner_size = 15
        corners = [
            (self.border_thickness, self.border_thickness),  # TL
            (width - self.border_thickness - corner_size, self.border_thickness),  # TR
            (self.border_thickness, height - self.border_thickness - corner_size),  # BL
            (width - self.border_thickness - corner_size, height - self.border_thickness - corner_size),  # BR
        ]
        
        for cx, cy in corners:
            pygame.draw.rect(surface, accent_color, (cx, cy, corner_size, corner_size))
    
    def _render_paper_scroll(
        self,
        surface: pygame.Surface,
        width: int,
        height: int,
        bg_color: Tuple[int, int, int],
        border_color: Tuple[int, int, int],
        accent_color: Tuple[int, int, int]
    ):
        """Paper scroll with aged parchment look and rolled edges."""
        
        # Aged parchment background (slightly darker/yellowed)
        parchment_color = tuple(int(c * 0.95) for c in bg_color)
        pygame.draw.rect(surface, parchment_color, (0, 0, width, height))
        
        # Top curl effect (darker shading)
        pygame.draw.line(surface, tuple(int(c * 0.8) for c in bg_color), (0, 8), (width, 8), 4)
        
        # Bottom curl effect
        pygame.draw.line(surface, tuple(int(c * 0.8) for c in bg_color), (0, height - 8), (width, height - 8), 4)
        
        # Side borders (thin, subtle)
        pygame.draw.line(surface, border_color, (4, 10), (4, height - 10), 2)
        pygame.draw.line(surface, border_color, (width - 4, 10), (width - 4, height - 10), 2)
        
        # Accent ornament (top center, like a seal)
        seal_x = width // 2 - 8
        seal_y = 4
        pygame.draw.circle(surface, accent_color, (seal_x + 8, seal_y + 8), 6)
    
    def _render_lacquer_panel(
        self,
        surface: pygame.Surface,
        width: int,
        height: int,
        bg_color: Tuple[int, int, int],
        border_color: Tuple[int, int, int],
        accent_color: Tuple[int, int, int]
    ):
        """Lacquer panel with glossy, layered appearance and depth."""
        
        # Base background
        pygame.draw.rect(surface, bg_color, (0, 0, width, height))
        
        # Dark border (outer)
        pygame.draw.rect(surface, border_color, (0, 0, width, height), self.border_thickness)
        
        # Highlight edge (top-left, gives glossy 3D effect)
        pygame.draw.line(surface, accent_color, (self.border_thickness, self.border_thickness), 
                        (width - self.border_thickness, self.border_thickness), 2)
        pygame.draw.line(surface, accent_color, (self.border_thickness, self.border_thickness), 
                        (self.border_thickness, height - self.border_thickness), 2)
        
        # Shadow edge (bottom-right)
        shadow_color = tuple(int(c * 0.6) for c in bg_color)
        pygame.draw.line(surface, shadow_color, (width - self.border_thickness - 2, self.border_thickness), 
                        (width - self.border_thickness - 2, height - self.border_thickness), 2)
        pygame.draw.line(surface, shadow_color, (self.border_thickness, height - self.border_thickness - 2), 
                        (width - self.border_thickness, height - self.border_thickness - 2), 2)
        
        # Center reflection (subtle glossy shine)
        shine_height = 4
        shine_rect = pygame.Rect(0, 10, width, shine_height)
        shine_surf = pygame.Surface((width, shine_height), pygame.SRCALPHA)
        shine_surf.fill((255, 255, 255, 40))
        surface.blit(shine_surf, shine_rect.topleft)
    
    def _render_ink_wash(
        self,
        surface: pygame.Surface,
        width: int,
        height: int,
        bg_color: Tuple[int, int, int],
        border_color: Tuple[int, int, int],
        accent_color: Tuple[int, int, int]
    ):
        """Ink wash with semi-transparent, watercolor edges and organic feel."""
        
        # Semi-transparent background (like watercolor wash)
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_surface.fill(bg_color + (220,))  # 220 alpha = slightly transparent
        surface.blit(bg_surface, (0, 0))
        
        # Organic edge effect (faded border with varying alpha)
        edge_width = 12
        for i in range(edge_width):
            alpha = int(80 * (1 - i / edge_width))
            edge_color = border_color + (alpha,)
            
            # Top
            pygame.draw.line(surface, edge_color, (0, i), (width, i), 1)
            # Bottom
            pygame.draw.line(surface, edge_color, (0, height - i), (width, height - i), 1)
            # Left
            pygame.draw.line(surface, edge_color, (i, 0), (i, height), 1)
            # Right
            pygame.draw.line(surface, edge_color, (width - i, 0), (width - i, height), 1)
        
        # Accent wash (optional inner tint)
        accent_wash = pygame.Surface((width - 20, height - 20), pygame.SRCALPHA)
        accent_wash.fill(accent_color + (30,))
        surface.blit(accent_wash, (10, 10))
    
    def _render_shrine_gate(
        self,
        surface: pygame.Surface,
        width: int,
        height: int,
        bg_color: Tuple[int, int, int],
        border_color: Tuple[int, int, int],
        accent_color: Tuple[int, int, int]
    ):
        """Shrine gate (torii) architectural style with grid pattern."""
        
        # Background
        pygame.draw.rect(surface, bg_color, (0, 0, width, height))
        
        # Thick architectural frame (like torii gate)
        frame_thickness = 8
        pygame.draw.rect(surface, border_color, (0, 0, width, height), frame_thickness)
        
        # Inner frame (accent color)
        inner_margin = frame_thickness + 4
        inner_rect = pygame.Rect(inner_margin, inner_margin, width - inner_margin * 2, height - inner_margin * 2)
        pygame.draw.rect(surface, accent_color, inner_rect, self.accent_width)
        
        # Grid pattern (like shrine lattice) - vertical and horizontal lines
        grid_spacing = 40
        grid_color = tuple(int(c * 0.85) for c in border_color)
        
        # Vertical lines
        x = inner_margin + grid_spacing
        while x < width - inner_margin:
            pygame.draw.line(surface, grid_color, (x, inner_margin + 10), (x, height - inner_margin - 10), 1)
            x += grid_spacing
        
        # Horizontal lines
        y = inner_margin + grid_spacing
        while y < height - inner_margin:
            pygame.draw.line(surface, grid_color, (inner_margin + 10, y), (width - inner_margin - 10, y), 1)
            y += grid_spacing
        
        # Corner ornaments (small squares at cardinal points)
        ornament_size = 12
        ornaments = [
            (inner_margin - ornament_size // 2, inner_margin - ornament_size // 2),  # TL
            (width - inner_margin - ornament_size // 2, inner_margin - ornament_size // 2),  # TR
            (inner_margin - ornament_size // 2, height - inner_margin - ornament_size // 2),  # BL
            (width - inner_margin - ornament_size // 2, height - inner_margin - ornament_size // 2),  # BR
        ]
        
        for ox, oy in ornaments:
            pygame.draw.rect(surface, accent_color, (ox, oy, ornament_size, ornament_size))


# ============================================================================
# Convenience Functions
# ============================================================================

def create_panel_with_text(
    width: int,
    height: int,
    text: str,
    style: PanelStyle = PanelStyle.LACQUER_PANEL,
    bg_color: Tuple[int, int, int] = (245, 241, 237),
    border_color: Tuple[int, int, int] = (58, 58, 58),
    accent_color: Tuple[int, int, int] = (201, 168, 118),
    text_color: Tuple[int, int, int] = (26, 26, 26),
    font: Optional[pygame.font.Font] = None
) -> pygame.Surface:
    """
    Helper to create a panel with centered text.
    
    Args:
        width: Panel width
        height: Panel height
        text: Text to display
        style: Panel style
        bg_color: Background color
        border_color: Border color
        accent_color: Accent color
        text_color: Text color
        font: pygame.font.Font (uses default if None)
    
    Returns:
        pygame.Surface with panel and text
    """
    
    if font is None:
        font = pygame.font.SysFont("times", 20)
    
    pr = PanelRenderer()
    panel = pr.render_panel(width, height, style, bg_color, border_color, accent_color)
    
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(width // 2, height // 2))
    panel.blit(text_surf, text_rect.topleft)
    
    return panel


# ============================================================================
# Test / Example
# ============================================================================

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Panel Renderer Test")
    
    pr = PanelRenderer()
    
    # Create panels in different styles
    ornate = pr.render_panel(280, 150, PanelStyle.ORNATE_FRAME)
    scroll = pr.render_panel(280, 150, PanelStyle.PAPER_SCROLL)
    lacquer = pr.render_panel(280, 150, PanelStyle.LACQUER_PANEL)
    ink = pr.render_panel(280, 150, PanelStyle.INK_WASH)
    shrine = pr.render_panel(280, 150, PanelStyle.SHRINE_GATE)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((50, 50, 50))
        
        screen.blit(ornate, (20, 50))
        screen.blit(scroll, (320, 50))
        screen.blit(lacquer, (620, 50))
        screen.blit(ink, (20, 300))
        screen.blit(shrine, (320, 300))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
