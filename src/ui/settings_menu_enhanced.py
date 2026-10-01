"""
Enhanced Settings Menu — Visual toggles, sliders, and elegant layout using Sprint 0 design system.

Features:
  - Visual toggle switches
  - Volume sliders with speaker icons
  - Gamepad rumble visualization
  - Language select with visual indicators
  - Ornate panel frame with organized sections
  - Smooth animations and transitions
"""

import pygame
import json
import os
from typing import Optional, List, Dict
from enum import Enum
from src.ui.animations import Tween, Easing
from src.ui.panel_renderer import PanelRenderer, PanelStyle
from src.ui.font_manager import FontManager, FontSize, FontFamily
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.i18n import t


class SettingType(Enum):
    """Types of settings controls."""
    TOGGLE = "toggle"
    SLIDER = "slider"
    SELECT = "select"
    LABEL = "label"


class Setting:
    """Single setting with associated control."""
    
    def __init__(
        self,
        key: str,
        label: str,
        setting_type: SettingType,
        value: any,
        min_val: float = 0.0,
        max_val: float = 1.0,
        options: Optional[List[str]] = None,
        x: int = 0,
        y: int = 0,
        width: int = 500,
        height: int = 50
    ):
        self.key = key
        self.label = label
        self.setting_type = setting_type
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.options = options or []
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        
        # Hover and focus
        self.is_hovered = False
        self.is_focused = False
        self.hover_tween = Tween(0.0, 1.0, 0.2, Easing.EASE_OUT_QUAD)
        self.hover_tween.finished = True
    
    def set_hover(self, hovered: bool):
        """Set hover state."""
        if hovered and not self.is_hovered:
            self.is_hovered = True
            self.hover_tween = Tween(0.0, 1.0, 0.2, Easing.EASE_OUT_QUAD)
        elif not hovered and self.is_hovered:
            self.is_hovered = False
            self.hover_tween = Tween(1.0, 0.0, 0.2, Easing.EASE_IN_QUAD)
    
    def update(self, dt: float):
        """Update animations."""
        if not self.hover_tween.finished:
            self.hover_tween.update(dt)
    
    def get_hover_alpha(self) -> float:
        """Get hover animation progress."""
        return self.hover_tween.current if not self.hover_tween.finished else (1.0 if self.is_hovered else 0.0)
    
    def check_collision(self, x: int, y: int) -> bool:
        """Check if point is over this setting."""
        return self.rect.collidepoint(x, y)


class EnhancedSettingsMenu:
    """
    Enhanced settings menu with visual controls using design system.
    
    Usage:
        settings = EnhancedSettingsMenu()
        
        while settings_open:
            events = pygame.event.get()
            if settings.update(dt, events):
                settings_open = False
            
            settings.render(screen)
            pygame.display.flip()
    """
    
    def __init__(self):
        self.fm = FontManager()
        self.fm.load_fonts()
        
        self.pr = PanelRenderer()
        
        # Load settings from config
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "settings.json"
        )
        self.settings_data = self._load_settings()
        
        # Menu state
        self.settings: List[Setting] = []
        self._create_settings()
        
        self.selected_index = 0
        self.show_overlay = True
        
        # Background panel
        self.bg_panel: Optional[pygame.Surface] = None
        self._prepare_background()
    
    def _load_settings(self) -> Dict:
        """Load settings from JSON file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        # Default settings
        return {
            "audio": {
                "master_volume": 0.8,
                "music_volume": 0.7,
                "sfx_volume": 0.8
            },
            "video": {
                "fullscreen": False,
                "vsync": True,
                "resolution": "1280x720"
            },
            "gameplay": {
                "language": "en",
                "rumble": True,
                "difficulty": "normal"
            }
        }
    
    def _save_settings(self):
        """Save settings to JSON file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings_data, f, indent=2)
        except:
            pass
    
    def _create_settings(self):
        """Create settings controls."""
        start_y = 150
        padding_y = 70
        
        settings_config = [
            # Audio Section
            ("audio_label", "AUDIO", SettingType.LABEL, None),
            ("master_volume", "Master Volume", SettingType.SLIDER, 
             self.settings_data["audio"]["master_volume"], 0.0, 1.0),
            ("music_volume", "Music Volume", SettingType.SLIDER,
             self.settings_data["audio"]["music_volume"], 0.0, 1.0),
            ("sfx_volume", "SFX Volume", SettingType.SLIDER,
             self.settings_data["audio"]["sfx_volume"], 0.0, 1.0),
            
            # Video Section
            ("video_label", "VIDEO", SettingType.LABEL, None),
            ("fullscreen", "Fullscreen", SettingType.TOGGLE,
             self.settings_data["video"]["fullscreen"]),
            ("vsync", "V-Sync", SettingType.TOGGLE,
             self.settings_data["video"]["vsync"]),
            
            # Gameplay Section
            ("gameplay_label", "GAMEPLAY", SettingType.LABEL, None),
            ("language", "Language", SettingType.SELECT,
             self.settings_data["gameplay"]["language"], 0, 2, ["English", "Português", "日本語"]),
            ("rumble", "Gamepad Rumble", SettingType.TOGGLE,
             self.settings_data["gameplay"]["rumble"]),
        ]
        
        y = start_y
        for config in settings_config:
            key, label, setting_type, value, *extra = config + (None,) * 5
            
            min_val = extra[0] if extra and extra[0] is not None else 0.0
            max_val = extra[1] if extra and extra[1] is not None else 1.0
            options = extra[2] if extra and len(extra) > 2 and extra[2] else None
            
            setting = Setting(
                key=key,
                label=label,
                setting_type=setting_type,
                value=value,
                min_val=min_val,
                max_val=max_val,
                options=options,
                x=SCREEN_WIDTH // 2 - 250,
                y=y,
                width=500,
                height=50 if setting_type != SettingType.LABEL else 40
            )
            
            self.settings.append(setting)
            y += padding_y
    
    def _prepare_background(self):
        """Pre-render background panel."""
        self.bg_panel = self.pr.render_panel(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            style=PanelStyle.LACQUER_PANEL,
            bg_color=(42, 42, 42),
            border_color=(201, 168, 118),
            accent_color=(230, 154, 60),
            shadow=False
        )
    
    # ========================================================================
    # Update & Input
    # ========================================================================
    
    def update(self, dt: float, events: list) -> bool:
        """
        Update settings menu.
        
        Args:
            dt: Delta time
            events: pygame.event list
        
        Returns:
            True if settings should close, False otherwise
        """
        
        # Update all settings
        for setting in self.settings:
            setting.update(dt)
        
        # Handle input
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._save_settings()
                    return True
                
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected_index = (self.selected_index - 1) % len(self.settings)
                    self._update_focus()
                
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected_index = (self.selected_index + 1) % len(self.settings)
                    self._update_focus()
                
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    self._adjust_setting(-0.1)
                
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self._adjust_setting(0.1)
                
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self._toggle_focused_setting()
            
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 1:  # B button
                    self._save_settings()
                    return True
            
            elif event.type == pygame.JOYHATMOTION:
                if event.value[1] == -1:
                    self.selected_index = (self.selected_index - 1) % len(self.settings)
                    self._update_focus()
                elif event.value[1] == 1:
                    self.selected_index = (self.selected_index + 1) % len(self.settings)
                    self._update_focus()
                
                if event.value[0] == -1:
                    self._adjust_setting(-0.1)
                elif event.value[0] == 1:
                    self._adjust_setting(0.1)
            
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i, setting in enumerate(self.settings):
                    if setting.check_collision(mx, my) and setting.setting_type != SettingType.LABEL:
                        if i != self.selected_index:
                            self.selected_index = i
                            self._update_focus()
                        break
        
        return False
    
    def _update_focus(self):
        """Update focus states based on selection."""
        for i, setting in enumerate(self.settings):
            setting.set_hover(i == self.selected_index)
            setting.is_focused = (i == self.selected_index)
    
    def _adjust_setting(self, delta: float):
        """Adjust focused setting value."""
        setting = self.settings[self.selected_index]
        
        if setting.setting_type == SettingType.SLIDER:
            new_value = max(setting.min_val, min(setting.max_val, setting.value + delta))
            setting.value = new_value
            self.settings_data["audio"][setting.key] = new_value
        
        elif setting.setting_type == SettingType.SELECT and setting.options:
            current_idx = setting.options.index(setting.value) if setting.value in setting.options else 0
            new_idx = (current_idx + (1 if delta > 0 else -1)) % len(setting.options)
            setting.value = setting.options[new_idx]
            self.settings_data["gameplay"][setting.key] = setting.value
    
    def _toggle_focused_setting(self):
        """Toggle focused setting if it's a toggle type."""
        setting = self.settings[self.selected_index]
        
        if setting.setting_type == SettingType.TOGGLE:
            setting.value = not setting.value
            self.settings_data["video" if setting.key in ["fullscreen", "vsync"] 
                                else "gameplay"][setting.key] = setting.value
    
    # ========================================================================
    # Rendering
    # ========================================================================
    
    def render(self, surface: pygame.Surface):
        """Render settings menu."""
        
        # Draw semi-transparent overlay if showing as modal
        if self.show_overlay:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            surface.blit(overlay, (0, 0))
        
        # Background panel
        if self.bg_panel:
            surface.blit(self.bg_panel, (0, 0))
        else:
            surface.fill((42, 42, 42))
        
        # Title
        title_surface = self.fm.render(
            "SETTINGS",
            size=FontSize.EPIC,
            family=FontFamily.HEADING,
            color=(230, 154, 60),
            shadow=True,
            shadow_color=(26, 26, 26),
            shadow_offset=(3, 3)
        )
        title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        title_y = 60
        surface.blit(title_surface, (title_x, title_y))
        
        # Render each setting
        for i, setting in enumerate(self.settings):
            self._render_setting(surface, setting, i == self.selected_index)
        
        # Footer
        footer_text = t("settings_footer_instructions")
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
    
    def _render_setting(self, surface: pygame.Surface, setting: Setting, is_focused: bool):
        """Render a single setting control."""
        
        if setting.setting_type == SettingType.LABEL:
            # Section label
            label_surface = self.fm.render(
                setting.label,
                size=FontSize.HEADING,
                family=FontFamily.HEADING,
                color=(200, 160, 100),
                shadow=True,
                shadow_color=(26, 26, 26),
                shadow_offset=(1, 1)
            )
            surface.blit(label_surface, (setting.x, setting.y))
            return
        
        # Background
        hover_alpha = setting.get_hover_alpha()
        bg_color = (80, 60, 40) if is_focused else (50, 50, 50)
        border_color = (230, 154, 60) if is_focused else (100, 100, 100)
        border_width = 2 if is_focused else 1
        
        pygame.draw.rect(surface, bg_color, setting.rect, border_radius=6)
        pygame.draw.rect(surface, border_color, setting.rect, border_width, border_radius=6)
        
        # Draw label
        label_surface = self.fm.render(
            setting.label,
            size=FontSize.BODY,
            family=FontFamily.BODY,
            color=(245, 241, 237),
            shadow=True,
            shadow_color=(26, 26, 26),
            shadow_offset=(1, 1)
        )
        surface.blit(label_surface, (setting.x + 20, setting.y + 10))
        
        # Draw control based on type
        control_x = setting.x + setting.width - 150
        
        if setting.setting_type == SettingType.TOGGLE:
            self._draw_toggle(surface, control_x, setting.y + 15, setting.value, is_focused)
        
        elif setting.setting_type == SettingType.SLIDER:
            self._draw_slider(surface, control_x, setting.y + 15, setting.value, is_focused)
        
        elif setting.setting_type == SettingType.SELECT and setting.options:
            self._draw_select(surface, control_x, setting.y + 15, setting.value, setting.options, is_focused)
    
    def _draw_toggle(self, surface: pygame.Surface, x: int, y: int, is_on: bool, is_focused: bool):
        """Draw a toggle switch."""
        toggle_width = 60
        toggle_height = 30
        
        # Background
        bg_color = (60, 100, 60) if is_on else (100, 60, 60)
        pygame.draw.rect(surface, bg_color, (x, y, toggle_width, toggle_height), border_radius=15)
        
        # Border
        pygame.draw.rect(surface, (200, 200, 200) if is_focused else (150, 150, 150),
                        (x, y, toggle_width, toggle_height), 1, border_radius=15)
        
        # Circle (knob)
        knob_x = x + 27 if is_on else x + 5
        pygame.draw.circle(surface, (255, 255, 255), (int(knob_x + 10), y + 15), 10)
    
    def _draw_slider(self, surface: pygame.Surface, x: int, y: int, value: float, is_focused: bool):
        """Draw a slider control."""
        slider_width = 120
        slider_height = 8
        
        # Track
        pygame.draw.rect(surface, (70, 70, 70), (x, y, slider_width, slider_height), border_radius=4)
        
        # Fill (progress)
        fill_width = int(slider_width * max(0, min(1, value)))
        pygame.draw.rect(surface, (230, 154, 60), (x, y, fill_width, slider_height), border_radius=4)
        
        # Border
        pygame.draw.rect(surface, (150, 150, 150) if is_focused else (100, 100, 100),
                        (x, y, slider_width, slider_height), 1, border_radius=4)
        
        # Knob
        knob_x = x + fill_width
        pygame.draw.circle(surface, (255, 255, 255) if is_focused else (200, 200, 200),
                          (int(knob_x), y + slider_height // 2), 6)
    
    def _draw_select(self, surface: pygame.Surface, x: int, y: int, value: str,
                     options: List[str], is_focused: bool):
        """Draw a select dropdown."""
        option_text = value if isinstance(value, str) else str(value)
        
        option_surface = self.fm.render(
            option_text,
            size=FontSize.BODY,
            family=FontFamily.BODY,
            color=(230, 154, 60) if is_focused else (245, 241, 237),
            shadow=True,
            shadow_color=(26, 26, 26),
            shadow_offset=(1, 1)
        )
        
        # Background box
        box_width = max(120, option_surface.get_width() + 20)
        box_height = 30
        pygame.draw.rect(surface, (70, 70, 70), (x, y, box_width, box_height), border_radius=4)
        pygame.draw.rect(surface, (200, 200, 200) if is_focused else (150, 150, 150),
                        (x, y, box_width, box_height), 1, border_radius=4)
        
        # Text
        surface.blit(option_surface, (x + 10, y + 6))
