"""
Font Manager — Centralized text rendering with caching, layering, and styling.

Handles:
  - Font loading (custom fonts + fallbacks)
  - Cached text rendering (avoid per-frame re-renders)
  - Text effects: outline, shadow, glow
  - Multi-line text alignment
  - Color palette integration
"""

import os
import pygame
from typing import Optional, Tuple, Dict, Any
from enum import Enum

# ============================================================================
# Font Configuration
# ============================================================================

class FontSize(Enum):
    """Standard font sizes for UI hierarchy."""
    TINY = 12
    SMALL = 16
    BODY = 20
    HEADING = 28
    TITLE = 36
    EPIC = 48


class FontFamily(Enum):
    """Font families available."""
    HEADING = "heading"  # Serif, traditional
    BODY = "body"        # Clean, readable
    MONO = "mono"        # Monospace (stats, debug)


class TextAlign(Enum):
    """Text alignment modes."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


# ============================================================================
# Text effects (shadow / outline / glow)
# ============================================================================

def _blur(surf: pygame.Surface, factor: int = 3) -> pygame.Surface:
    """Cheap blur: shrink then enlarge with smooth scaling."""
    w, h = surf.get_size()
    small = pygame.transform.smoothscale(surf, (max(1, w // factor), max(1, h // factor)))
    return pygame.transform.smoothscale(small, (w, h))


def render_text_fx(
    font: pygame.font.Font,
    text: str,
    color: Tuple[int, int, int] = (255, 255, 255),
    outline: bool = False,
    outline_color: Tuple[int, int, int] = (0, 0, 0),
    outline_width: int = 1,
    shadow: bool = False,
    shadow_color: Tuple[int, int, int] = (0, 0, 0),
    shadow_offset: Tuple[int, int] = (2, 2),
    glow: bool = False,
    glow_color: Optional[Tuple[int, int, int]] = None,
    glow_width: int = 3,
) -> pygame.Surface:
    """
    Render one line of text with consistent effects on a transparent surface.

    Layers (back to front): glow, shadow (of text + outline silhouette), outline, text.
    The text is rendered once per color; the surface is padded equally on all sides so
    centering it keeps the glyphs centered.
    """
    body = font.render(text, True, color)
    w, h = body.get_size()

    ow = outline_width if outline else 0
    sx, sy = shadow_offset if shadow else (0, 0)
    pad = max(ow + max(abs(sx), abs(sy)), glow_width * 2 if glow else 0, ow) + 1
    surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)

    # Silhouette of text + outline (shared by shadow and outline layers)
    ring = []
    if ow:
        for dx in range(-ow, ow + 1):
            for dy in range(-ow, ow + 1):
                if (dx or dy) and dx * dx + dy * dy <= ow * ow + ow:
                    ring.append((dx, dy))

    if glow:
        halo = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        halo.blit(font.render(text, True, glow_color or color), (pad, pad))
        halo = _blur(halo, max(2, glow_width))
        for _ in range(2):
            surf.blit(halo, (0, 0))

    if shadow:
        mask = font.render(text, True, shadow_color)
        shade = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        for dx, dy in ring + [(0, 0)]:
            shade.blit(mask, (pad + dx + sx, pad + dy + sy))
        shade.set_alpha(170)
        surf.blit(shade, (0, 0))

    if ring:
        edge = font.render(text, True, outline_color)
        for dx, dy in ring:
            surf.blit(edge, (pad + dx, pad + dy))

    surf.blit(body, (pad, pad))
    return surf


# ============================================================================
# Font Manager (Singleton)
# ============================================================================

class FontManager:
    """
    Singleton font manager. Handles loading, caching, and rendering text with effects.
    
    Usage:
        fm = FontManager()
        fm.load_fonts()
        
        # Simple render
        surf = fm.render("Hello", FontSize.BODY, FontFamily.BODY, color=(255, 255, 255))
        
        # With shadow & outline
        surf = fm.render(
            "Epic Title",
            FontSize.EPIC,
            FontFamily.HEADING,
            color=(200, 150, 50),
            shadow=True,
            shadow_color=(0, 0, 0),
            shadow_offset=(3, 3),
            outline=True,
            outline_color=(0, 0, 0),
            outline_width=2
        )
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.fonts: Dict[Tuple[FontFamily, FontSize], pygame.font.Font] = {}
        self.cache: Dict[str, pygame.Surface] = {}
        self.font_paths: Dict[FontFamily, str] = {}
        
    # ========================================================================
    # Font Loading
    # ========================================================================
    
    def load_fonts(self):
        """Load font files from assets/fonts/."""
        assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "fonts")
        
        # Attempt to load custom fonts; fall back to system fonts
        heading_path = os.path.join(assets_path, "Cinzel-Regular.ttf")
        body_path = os.path.join(assets_path, "ZenAntique-Regular.ttf")
        mono_path = os.path.join(assets_path, "DejaVuSansMono.ttf")
        
        self.font_paths[FontFamily.HEADING] = heading_path if os.path.exists(heading_path) else None
        self.font_paths[FontFamily.BODY] = body_path if os.path.exists(body_path) else None
        self.font_paths[FontFamily.MONO] = mono_path if os.path.exists(mono_path) else None
        
        # Pre-load common sizes
        for family in FontFamily:
            for size in FontSize:
                self._get_font(family, size)
    
    def _get_font(self, family: FontFamily, size: FontSize) -> pygame.font.Font:
        """Get or create font object (internal cache)."""
        key = (family, size)
        
        if key in self.fonts:
            return self.fonts[key]
        
        if not self.font_paths:
            self.load_fonts()
            if key in self.fonts:
                return self.fonts[key]
        
        font_path = self.font_paths.get(family)
        pixel_size = size.value
        
        if font_path and os.path.exists(font_path):
            font = pygame.font.Font(font_path, pixel_size)
        else:
            # Fallback to system font (use lowercase for pygame.font.SysFont)
            fallback_name = {
                FontFamily.HEADING: "times",       # Serif fallback (times new roman)
                FontFamily.BODY: "helvetica",      # Sans-serif fallback (verified available on macOS)
                FontFamily.MONO: "courier"         # Monospace fallback
            }.get(family, None)
            font = pygame.font.SysFont(fallback_name, pixel_size)
        
        self.fonts[key] = font
        return font
    
    # ========================================================================
    # Text Rendering
        # ========================================================================
    
    def render(
        self,
        text: str,
        size: FontSize = FontSize.BODY,
        family: FontFamily = FontFamily.BODY,
        color: Tuple[int, int, int] = (255, 255, 255),
        shadow: bool = False,
        shadow_color: Tuple[int, int, int] = (0, 0, 0),
        shadow_offset: Tuple[int, int] = (2, 2),
        outline: bool = False,
        outline_color: Tuple[int, int, int] = (0, 0, 0),
        outline_width: int = 1,
        glow: bool = False,
        glow_color: Optional[Tuple[int, int, int]] = None,
        glow_width: int = 3,
        alignment: TextAlign = TextAlign.LEFT,
        max_width: Optional[int] = None,
        use_cache: bool = True
    ) -> pygame.Surface:
        """
        Render text with optional effects.
        
        Args:
            text: Text to render
            size: Font size enum
            family: Font family enum
            color: RGB text color
            shadow: Whether to add shadow
            shadow_color: Shadow RGB
            shadow_offset: (x, y) shadow offset
            outline: Whether to add outline
            outline_color: Outline RGB
            outline_width: Outline thickness in pixels
            glow: Whether to add glow effect
            glow_color: Glow RGB (defaults to color)
            glow_width: Glow radius in pixels
            alignment: Text alignment
            max_width: Wrap text to this width (or None for no wrapping)
            use_cache: Whether to cache result
        
        Returns:
            pygame.Surface with rendered text
        """
        
        # Check cache
        cache_key = (
            text, size, family, tuple(color), shadow, tuple(shadow_color), tuple(shadow_offset),
            outline, tuple(outline_color), outline_width, glow,
            tuple(glow_color) if glow_color else None, glow_width, max_width,
        )
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key].copy()
        
        font = self._get_font(family, size)
        
        # Handle multi-line text
        if max_width:
            lines = self._wrap_text(text, font, max_width)
        else:
            lines = text.split("\n")
        
        # Render each line
        line_surfaces = []
        for line in lines:
            surf = self._render_line(
                line, font, color, outline, outline_color, outline_width,
                shadow, shadow_color, shadow_offset, glow, glow_color, glow_width
            )
            line_surfaces.append(surf)
        
        # Combine lines
        if len(line_surfaces) == 1:
            result = line_surfaces[0]
        else:
            total_height = sum(s.get_height() for s in line_surfaces)
            total_width = max(s.get_width() for s in line_surfaces)
            result = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
            y = 0
            for surf in line_surfaces:
                result.blit(surf, (0, y))
                y += surf.get_height()
        
        # Cache result
        if use_cache:
            self.cache[cache_key] = result.copy()
        
        return result
    
    def _render_line(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int],
        outline: bool,
        outline_color: Tuple[int, int, int],
        outline_width: int,
        shadow: bool,
        shadow_color: Tuple[int, int, int],
        shadow_offset: Tuple[int, int],
        glow: bool,
        glow_color: Optional[Tuple[int, int, int]],
        glow_width: int
    ) -> pygame.Surface:
        """Render a single line with effects."""
        return render_text_fx(
            font, text, color, outline, outline_color, outline_width,
            shadow, shadow_color, shadow_offset, glow, glow_color, glow_width
        )
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list:
        """Wrap text to fit within max_width."""
        words = text.split(" ")
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def clear_cache(self):
        """Clear the render cache (call if memory pressure)."""
        self.cache.clear()
    
    def get_text_size(
        self,
        text: str,
        size: FontSize = FontSize.BODY,
        family: FontFamily = FontFamily.BODY
    ) -> Tuple[int, int]:
        """Get width and height of text without rendering."""
        font = self._get_font(family, size)
        return font.size(text)


# ============================================================================
# Global Convenience Function
# ============================================================================

def get_font_manager() -> FontManager:
    """Get the singleton FontManager instance."""
    return FontManager()


# ============================================================================
# Test / Example
# ============================================================================

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Font Manager Test")
    
    fm = FontManager()
    fm.load_fonts()
    
    # Test renders
    text1 = fm.render("Simple Text", FontSize.BODY, FontFamily.BODY, color=(255, 255, 255))
    text2 = fm.render(
        "With Shadow & Outline",
        FontSize.HEADING,
        FontFamily.HEADING,
        color=(200, 150, 50),
        shadow=True,
        outline=True,
        outline_width=2
    )
    text3 = fm.render(
        "With Glow!",
        FontSize.EPIC,
        FontFamily.HEADING,
        color=(255, 200, 100),
        glow=True,
        glow_color=(255, 150, 0)
    )
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((30, 30, 30))
        screen.blit(text1, (100, 100))
        screen.blit(text2, (100, 200))
        screen.blit(text3, (100, 350))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
