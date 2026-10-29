"""Desbloqueio da Galeria: flag no save do Arcade, migração de saves antigos e persistência."""
import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.arcade import arcade_save


def _tmp_path():
    return os.path.join(tempfile.mkdtemp(), "arcade_save.json")


def test_new_save_is_locked():
    assert arcade_save.is_gallery_unlocked(arcade_save.empty_data()) is False


def test_unlock_persists_and_reports_first_time():
    path = _tmp_path()
    data = arcade_save.load(path)
    assert arcade_save.unlock_gallery(data) is True
    assert arcade_save.unlock_gallery(data) is False
    arcade_save.save(data, path)
    assert arcade_save.is_gallery_unlocked(arcade_save.load(path)) is True


def test_old_save_with_clears_migrates_to_unlocked():
    path = _tmp_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"version": arcade_save.SAVE_VERSION, "clears": {"1": {"normal": 1}}}, f)
    assert arcade_save.is_gallery_unlocked(arcade_save.load(path)) is True


def test_old_save_without_clears_stays_locked():
    path = _tmp_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"version": arcade_save.SAVE_VERSION, "high_scores": []}, f)
    assert arcade_save.is_gallery_unlocked(arcade_save.load(path)) is False


def test_main_unlocks_on_arcade_completion():
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    assert "arcade_save.unlock_gallery(data)" in src


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("test_gallery_unlock OK")
