"""
Unit tests for OpeningVideoScreen (Samurai Edge Opening Video).
"""
import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set dummy video/audio drivers for headless test runner
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from src.ui.opening_video import OpeningVideoScreen


class TestOpeningVideo(unittest.TestCase):
    def test_headless_auto_finish(self):
        """In headless mode (dummy driver), opening video should automatically finish without error."""
        screen = OpeningVideoScreen()
        self.assertTrue(screen.is_finished)
        # Calling update, render, handle_event should be safe
        screen.update(0.016)
        surf = pygame.Surface((1280, 720))
        screen.render(surf)
        self.assertTrue(screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)))

    def test_nonexistent_file_handling(self):
        """If a nonexistent video file path is given, it should mark finished and not crash."""
        screen = OpeningVideoScreen(video_path="nonexistent_video_path.mp4")
        self.assertTrue(screen.is_finished)

    def test_skip_keyboard_events(self):
        """Verify that Space, Enter, Escape trigger skip."""
        screen = OpeningVideoScreen()
        # Artificially set is_finished to False to test event routing
        screen.is_finished = False
        screen.prompt_timer = 1.0

        # Non-skip key (e.g. 'A')
        non_skip_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
        self.assertFalse(screen.handle_event(non_skip_event))
        self.assertFalse(screen.is_finished)

        # Space key
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        self.assertTrue(screen.handle_event(space_event))
        self.assertTrue(screen.is_finished)

        # Enter key
        screen.is_finished = False
        screen.prompt_timer = 1.0
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        self.assertTrue(screen.handle_event(enter_event))
        self.assertTrue(screen.is_finished)

        # Escape key
        screen.is_finished = False
        screen.prompt_timer = 1.0
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.assertTrue(screen.handle_event(esc_event))
        self.assertTrue(screen.is_finished)

    def test_skip_controller_buttons(self):
        """Verify Start (button 6/7) and Cross (button 0) trigger skip."""
        screen = OpeningVideoScreen()
        screen.is_finished = False
        screen.prompt_timer = 1.0

        # Start / Options (button 6)
        btn_start = pygame.event.Event(pygame.JOYBUTTONDOWN, button=6, instance_id=0)
        self.assertTrue(screen.handle_event(btn_start))
        self.assertTrue(screen.is_finished)

        # Cross / Confirm (button 0)
        screen.is_finished = False
        screen.prompt_timer = 1.0
        btn_cross = pygame.event.Event(pygame.JOYBUTTONDOWN, button=0, instance_id=0)
        self.assertTrue(screen.handle_event(btn_cross))
        self.assertTrue(screen.is_finished)

    def test_skip_mouse_touch(self):
        """Verify mouse click or touchscreen tap triggers skip."""
        screen = OpeningVideoScreen()
        screen.is_finished = False
        screen.prompt_timer = 1.0

        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(640, 360))
        self.assertTrue(screen.handle_event(click_event))
        self.assertTrue(screen.is_finished)

        screen.is_finished = False
        screen.prompt_timer = 1.0
        finger_event = pygame.event.Event(pygame.FINGERDOWN, x=0.5, y=0.5, finger_id=0)
        self.assertTrue(screen.handle_event(finger_event))
        self.assertTrue(screen.is_finished)

    def test_clean_stop_and_close(self):
        """Verify stop() and close() can be called multiple times without error."""
        screen = OpeningVideoScreen()
        screen.stop()
        self.assertTrue(screen.is_finished)
        self.assertIsNone(screen.video)
        screen.close()
        self.assertTrue(screen.is_finished)


if __name__ == "__main__":
    unittest.main()
