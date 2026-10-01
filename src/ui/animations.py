"""
Animation & Transition Library — Tweening, easing, and pre-built sequences.

Provides:
  - Tweening engine (value interpolation with easing)
  - Pre-built easing curves (linear, ease-in/out, bounce, etc.)
  - Animation sequences (chains of tweens)
  - Screen transition effects (fade, slide, zoom-blur, etc.)
  - Helper classes for common UI animations
"""

import pygame
from enum import Enum
from typing import Callable, Optional, Any, List, Tuple
from dataclasses import dataclass
import math


# ============================================================================
# Easing Functions
# ============================================================================

class Easing(Enum):
    """Standard easing curve types."""
    LINEAR = "linear"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    EASE_OUT_BOUNCE = "ease_out_bounce"
    EASE_OUT_ELASTIC = "ease_out_elastic"


def get_easing_function(easing: Easing) -> Callable[[float], float]:
    """
    Get easing function by type.
    
    Args:
        easing: Easing type
    
    Returns:
        Function that takes t (0.0 to 1.0) and returns eased value (0.0 to 1.0)
    """
    
    functions = {
        Easing.LINEAR: lambda t: t,
        
        Easing.EASE_IN_QUAD: lambda t: t * t,
        Easing.EASE_OUT_QUAD: lambda t: 1 - (1 - t) ** 2,
        Easing.EASE_IN_OUT_QUAD: lambda t: 2 * t ** 2 if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2,
        
        Easing.EASE_IN_CUBIC: lambda t: t ** 3,
        Easing.EASE_OUT_CUBIC: lambda t: 1 - (1 - t) ** 3,
        Easing.EASE_IN_OUT_CUBIC: lambda t: 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2,
        
        Easing.EASE_OUT_BOUNCE: _ease_out_bounce,
        Easing.EASE_OUT_ELASTIC: _ease_out_elastic,
    }
    
    return functions.get(easing, lambda t: t)


def _ease_out_bounce(t: float) -> float:
    """Bounce easing out."""
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


def _ease_out_elastic(t: float) -> float:
    """Elastic easing out."""
    c4 = (2 * math.pi) / 3
    return 0 if t == 0 else (1 if t == 1 else (2 ** (-10 * t)) * math.sin((t * 10 - 0.75) * c4) + 1)


# ============================================================================
# Tween — Single Value Animation
# ============================================================================

@dataclass
class Tween:
    """
    Single tweening animation from start_value to end_value over duration.
    
    Args:
        start_value: Initial value
        end_value: Target value
        duration: Duration in seconds
        easing: Easing curve type
        delay: Delay before tween starts (in seconds)
    """
    start_value: float
    end_value: float
    duration: float
    easing: Easing = Easing.LINEAR
    delay: float = 0.0
    
    # Runtime state
    elapsed: float = 0.0
    finished: bool = False
    current: float = 0.0
    
    def update(self, dt: float) -> float:
        """
        Update tween by dt seconds. Returns current value.
        
        Args:
            dt: Delta time in seconds
        
        Returns:
            Current interpolated value
        """
        if self.finished:
            self.current = self.end_value
            return self.end_value
        
        self.elapsed += dt
        
        # Handle delay
        if self.elapsed < self.delay:
            self.current = self.start_value
            return self.start_value
        
        # Adjust elapsed for delay
        t = (self.elapsed - self.delay) / self.duration
        
        if t >= 1.0:
            self.finished = True
            self.current = self.end_value
            return self.end_value
        
        # Apply easing
        easing_func = get_easing_function(self.easing)
        eased_t = easing_func(t)
        
        # Interpolate
        self.current = self.start_value + (self.end_value - self.start_value) * eased_t
        return self.current


# ============================================================================
# Animation Sequence — Chained Tweens
# ============================================================================

class AnimationSequence:
    """
    Chain of tweens that play sequentially.
    
    Example:
        seq = AnimationSequence()
        seq.add_tween(Tween(0, 1, 0.5, Easing.EASE_OUT_QUAD))  # Fade in
        seq.add_tween(Tween(1, 0, 0.5, Easing.EASE_IN_QUAD))   # Fade out
        
        while not seq.finished:
            value = seq.update(dt)
            alpha = int(255 * value)
    """
    
    def __init__(self):
        self.tweens: List[Tween] = []
        self.current_index: int = 0
        self.finished: bool = False
    
    def add_tween(self, tween: Tween) -> "AnimationSequence":
        """Add a tween to the sequence (returns self for chaining)."""
        self.tweens.append(tween)
        return self
    
    def update(self, dt: float) -> float:
        """
        Update sequence. Returns current value from active tween.
        
        Args:
            dt: Delta time in seconds
        
        Returns:
            Current value
        """
        if self.finished or not self.tweens:
            return 0.0
        
        current_tween = self.tweens[self.current_index]
        value = current_tween.update(dt)
        
        # Move to next tween if current is finished
        if current_tween.finished and self.current_index < len(self.tweens) - 1:
            self.current_index += 1
        elif current_tween.finished:
            self.finished = True
        
        return value
    
    def reset(self):
        """Reset sequence to beginning."""
        self.current_index = 0
        self.finished = False
        for tween in self.tweens:
            tween.elapsed = 0.0
            tween.finished = False


# ============================================================================
# Pre-Built Transition Effects
# ============================================================================

class TransitionEffect(Enum):
    """Pre-built screen transition types."""
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    ZOOM_BLUR = "zoom_blur"


class ScreenTransition:
    """
    Manage screen-to-screen transitions.
    
    Usage:
        trans = ScreenTransition(TransitionEffect.FADE, duration=0.3)
        
        while not trans.finished:
            alpha = trans.get_fade_alpha()  # for fade
            offset_x, offset_y = trans.get_slide_offset()  # for slide
            scale, blur = trans.get_zoom_blur()  # for zoom+blur
            trans.update(dt)
    """
    
    def __init__(self, effect: TransitionEffect, duration: float = 0.3, easing: Easing = Easing.EASE_IN_OUT_QUAD):
        self.effect = effect
        self.duration = duration
        self.easing = easing
        self.tween = Tween(0.0, 1.0, duration, easing)
        self.finished = False
    
    def update(self, dt: float):
        """Update transition by dt seconds."""
        value = self.tween.update(dt)
        self.finished = self.tween.finished
        return value
    
    def get_progress(self) -> float:
        """Get transition progress (0.0 to 1.0)."""
        return min(1.0, self.tween.elapsed / self.duration)
    
    def get_fade_alpha(self) -> int:
        """For FADE: get alpha (0-255)."""
        return int(255 * self.get_progress())
    
    def get_slide_offset(self) -> Tuple[int, int]:
        """For SLIDE: get (offset_x, offset_y) in pixels."""
        progress = self.get_progress()
        offset_pixels = 1280  # Adjust to screen width if needed
        
        if self.effect == TransitionEffect.SLIDE_LEFT:
            return (-int(offset_pixels * progress), 0)
        elif self.effect == TransitionEffect.SLIDE_RIGHT:
            return (int(offset_pixels * progress), 0)
        elif self.effect == TransitionEffect.SLIDE_UP:
            return (0, -int(offset_pixels * progress))
        elif self.effect == TransitionEffect.SLIDE_DOWN:
            return (0, int(offset_pixels * progress))
        return (0, 0)
    
    def get_scale_factor(self) -> float:
        """For ZOOM: get scale factor (1.0 + progress)."""
        progress = self.get_progress()
        if self.effect == TransitionEffect.ZOOM_IN:
            return 1.0 + progress * 0.3
        elif self.effect == TransitionEffect.ZOOM_OUT:
            return 1.0 - progress * 0.3
        elif self.effect == TransitionEffect.ZOOM_BLUR:
            return 1.0 + progress * 0.5
        return 1.0
    
    def get_blur_amount(self) -> int:
        """For ZOOM_BLUR: get blur radius in pixels."""
        if self.effect == TransitionEffect.ZOOM_BLUR:
            return int(self.get_progress() * 20)
        return 0


# ============================================================================
# UI Animation Helpers
# ============================================================================

class UIAnimator:
    """Helper for common UI animation patterns."""
    
    @staticmethod
    def fade_in(duration: float = 0.3) -> Tween:
        """Create fade-in tween (0 -> 1)."""
        return Tween(0.0, 1.0, duration, Easing.EASE_OUT_QUAD)
    
    @staticmethod
    def fade_out(duration: float = 0.3) -> Tween:
        """Create fade-out tween (1 -> 0)."""
        return Tween(1.0, 0.0, duration, Easing.EASE_IN_QUAD)
    
    @staticmethod
    def scale_up(duration: float = 0.3) -> Tween:
        """Create scale-up tween (0.8 -> 1.0)."""
        return Tween(0.8, 1.0, duration, Easing.EASE_OUT_BOUNCE)
    
    @staticmethod
    def scale_down(duration: float = 0.3) -> Tween:
        """Create scale-down tween (1.0 -> 0.8)."""
        return Tween(1.0, 0.8, duration, Easing.EASE_IN_QUAD)
    
    @staticmethod
    def pulse(duration: float = 0.5, min_alpha: float = 0.5, max_alpha: float = 1.0) -> AnimationSequence:
        """Create pulsing animation."""
        seq = AnimationSequence()
        seq.add_tween(Tween(min_alpha, max_alpha, duration / 2, Easing.EASE_IN_OUT_QUAD))
        seq.add_tween(Tween(max_alpha, min_alpha, duration / 2, Easing.EASE_IN_OUT_QUAD))
        return seq
    
    @staticmethod
    def slide_from_left(distance: int = 100, duration: float = 0.4) -> Tween:
        """Create slide-from-left tween."""
        return Tween(-distance, 0, duration, Easing.EASE_OUT_CUBIC)
    
    @staticmethod
    def slide_from_right(distance: int = 100, duration: float = 0.4) -> Tween:
        """Create slide-from-right tween."""
        return Tween(distance, 0, duration, Easing.EASE_OUT_CUBIC)
    
    @staticmethod
    def bounce_scale(duration: float = 0.3) -> Tween:
        """Create bounce scale tween (0.9 -> 1.0 with bounce)."""
        return Tween(0.9, 1.0, duration, Easing.EASE_OUT_BOUNCE)


# ============================================================================
# Test / Example
# ============================================================================

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Animation Test")
    
    # Create test animations
    fade_tween = Tween(0, 255, 1.0, Easing.EASE_IN_OUT_QUAD)
    slide_tween = UIAnimator.slide_from_left(200, 0.5)
    scale_tween = UIAnimator.bounce_scale(0.4)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        fade_value = fade_tween.update(dt)
        slide_value = slide_tween.update(dt)
        scale_value = scale_tween.update(dt)
        
        screen.fill((30, 30, 30))
        
        # Draw test rects with animations
        rect1 = pygame.Rect(640 - 50, 100, 100, 100)
        rect1.topleft = (int(rect1.topleft[0] + slide_value), rect1.topleft[1])
        pygame.draw.rect(screen, (255, 0, 0), rect1)
        
        rect2 = pygame.Rect(640 - 50, 250, 100, 100)
        scaled_size = int(100 * scale_value)
        rect2 = pygame.Rect(640 - scaled_size // 2, 250, scaled_size, scaled_size)
        pygame.draw.rect(screen, (0, 255, 0), rect2)
        
        rect3 = pygame.Rect(640 - 50, 400, 100, 100)
        rect3_surf = pygame.Surface((100, 100))
        rect3_surf.fill((0, 0, 255))
        rect3_surf.set_alpha(int(fade_value))
        screen.blit(rect3_surf, rect3.topleft)
        
        pygame.display.flip()
    
    pygame.quit()
