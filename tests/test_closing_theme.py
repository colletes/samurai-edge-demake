"""Tema de encerramento: faixa registrada, arquivo existente e sem duplicação de caminho."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.audio.sound_events import MusicTrack
from src.audio.sound_manager import MUSIC_DIR


def test_closing_theme_file_exists():
    assert os.path.isfile(os.path.join(MUSIC_DIR, MusicTrack.CLOSING_THEME.value + ".mp3"))


def test_opening_theme_file_exists():
    assert os.path.isfile(os.path.join(MUSIC_DIR, MusicTrack.OPENING_THEME.value + ".mp3"))


def test_credits_start_plays_closing_theme_once():
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    assert "MusicTrack.CLOSING_THEME, fade_ms=1200, loops=0" in src


if __name__ == "__main__":
    test_closing_theme_file_exists()
    test_opening_theme_file_exists()
    test_credits_start_plays_closing_theme_once()
    print("test_closing_theme OK")
