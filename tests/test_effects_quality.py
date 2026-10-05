"""
Teste da 6.5.6 (qualidade dos efeitos) e da otimização do `set_alpha` da iluminação.
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_effects_quality.py
"""
import inspect
import json
import os
import random
import sys
import tempfile
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import numpy as np
import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src.effects import lighting, quality
from src.effects.terrain_particles import TerrainFX, SURFACES
from src.isometric.camera import Camera
from src.isometric.voxel_renderer import draw_voxel_box
from src.world.arenas import arena_ids
import test_lighting_effects as tl


def _restore():
    quality.set_effects_quality(quality.HIGH)


def test_quality_api_and_settings_file():
    try:
        assert quality.get_effects_quality() == "high" and quality.is_high()
        quality.set_effects_quality("low")
        assert not quality.is_high() and quality.scaled(30) == 10 and quality.scaled(2, 4) == 4
        quality.set_effects_quality("qualquer")
        assert quality.is_high() and quality.scaled(30) == 30, "valor inválido cai na alta"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "settings.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"audio": {"master_volume": 0.5}, "video": {"vsync": True}}, f)
            assert quality.save_video_setting(path, "effects_quality", "low")
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            assert data["audio"] == {"master_volume": 0.5} and data["video"] == {"vsync": True, "effects_quality": "low"}, "o resto do arquivo fica intacto"
            quality.load_effects_quality(path)
            assert quality.get_effects_quality() == "low"
            quality.load_effects_quality(os.path.join(tmp, "nao_existe.json"))
            assert quality.is_high()
            assert quality.save_video_setting(os.path.join(tmp, "novo.json"), "effects_quality", "high"), "cria o arquivo se faltar"
    finally:
        _restore()
    with open(os.path.join(ROOT, "settings.json"), encoding="utf-8") as f:
        assert "video" in json.load(f)
    print("  [OK] Qualidade: API, valor inválido, leitura e gravação no settings.json sem apagar o resto.", flush=True)


def _counts(arena_id, level, seconds=6.0):
    quality.set_effects_quality(level)
    random.seed(3)
    arena, lf, camera = tl._setup(arena_id)
    surf = tl._flat(90)
    t = 0.0
    for _ in range(int(seconds * 60)):
        t += 1 / 60
        lf.render(surf, camera, t)
    return lf.particle_count()


def test_low_quality_cuts_particles():
    try:
        fewer = 0
        for arena_id in arena_ids():
            high, low = _counts(arena_id, "high"), _counts(arena_id, "low")
            assert low <= high, f"{arena_id}: a baixa não pode ter mais partículas ({low} > {high})"
            fewer += low < high
        assert fewer >= 4, f"só {fewer} arenas ficaram com menos partículas na baixa"
        arena, lf, camera = tl._setup(arena_ids()[0])
        fx_counts = {}
        for level in ("high", "low"):
            quality.set_effects_quality(level)
            random.seed(5)
            fx = TerrainFX()
            fx._emit(arena, SURFACES["dust"] if "dust" in SURFACES else next(iter(SURFACES.values())), 5.0, 5.0, 1.0, 0.0, 6.0, 30, 1.0)
            fx_counts[level] = len(fx.particles)
        assert fx_counts["low"] < fx_counts["high"], f"partículas de terreno {fx_counts}"
    finally:
        _restore()
    print(f"  [OK] A qualidade baixa solta menos partículas de ar em {fewer} arenas e menos poeira de terreno ({fx_counts['high']} -> {fx_counts['low']}).", flush=True)


def test_textures_follow_quality():
    cam = Camera(0.0, 0.0)
    cam.zoom = 3.0

    def draw(texture):
        surf = pygame.Surface((1280, 720))
        surf.fill((30, 30, 36))
        draw_voxel_box(surf, cam, 0.0, 0.0, 0.0, 1.2, 1.2, 1.4, (150, 60, 70), texture=texture)
        return pygame.surfarray.array3d(surf).astype(int)

    plain = draw(None)
    try:
        assert np.abs(draw("silk") - plain).sum() > 0, "alta: a textura aparece"
        quality.set_effects_quality("low")
        assert np.abs(draw("silk") - plain).sum() == 0, "baixa: sem textura nos voxels"
    finally:
        _restore()
    print("  [OK] As texturas dos voxels só aparecem na qualidade alta.", flush=True)


def test_opacity_is_baked_not_set_alpha():
    source = inspect.getsource(lighting)
    assert "set_alpha" not in source.replace('"""', "").split("def puff_sprite")[1].split("class _Sunbeams")[0], "puffs e névoa não usam set_alpha"
    a = lighting.puff_sprite((200, 200, 210), 64, 41)
    b = lighting.puff_sprite((200, 200, 210), 64, 43)
    c = lighting.puff_sprite((200, 200, 210), 64, 90)
    assert a is b and a is not c, "opacidades próximas dividem o mesmo sprite assado"
    assert pygame.surfarray.array_alpha(c).max() > pygame.surfarray.array_alpha(a).max() > 20
    assert pygame.surfarray.array_alpha(c).max() <= 96
    assert lighting.quantize_opacity(-5) == 0 and lighting.quantize_opacity(999) <= 255
    print("  [OK] A opacidade das bolas de fumaça e névoa vem assada no sprite, em degraus, e não de `set_alpha` por quadro.", flush=True)


def test_lighting_budget_improved():
    worst = {"high": ("", 0.0), "low": ("", 0.0)}
    try:
        for level in ("high", "low"):
            quality.set_effects_quality(level)
            for arena_id in arena_ids():
                arena, lf, camera = tl._setup(arena_id)
                surf = tl._flat(90)
                t = tl._warm_up(lf, camera, 2.0)
                start = time.perf_counter()
                for _ in range(120):
                    t += 1 / 60
                    lf.render(surf, camera, t)
                ms = (time.perf_counter() - start) * 1000.0 / 120
                if ms > worst[level][1]:
                    worst[level] = (arena_id, ms)
    finally:
        _restore()
    assert worst["high"][1] < 3.5, f"alta: {worst['high']}"
    assert worst["low"][1] <= worst["high"][1] * 1.15 + 0.2, f"baixa: {worst['low']} contra {worst['high']}"
    print(f"  [OK] Iluminação a 1280x720: pior caso {worst['high'][1]:.1f} ms na alta ({worst['high'][0]}) e {worst['low'][1]:.1f} ms na baixa (antes 2.1 ms).", flush=True)


def test_settings_menu_toggles():
    from src.i18n import set_lang
    from src.input.controls_storage import load_controls_config
    from src.isometric import voxel_renderer
    from src.ui.settings_menu import SettingsMenu
    fonts = (pygame.font.Font(None, 48), pygame.font.Font(None, 26), pygame.font.Font(None, 20))
    real_path = quality.SETTINGS_PATH
    with tempfile.TemporaryDirectory() as tmp:
        quality.SETTINGS_PATH = os.path.join(tmp, "settings.json")
        try:
            menu = SettingsMenu(load_controls_config())
            menu.open()
            surf = pygame.Surface((1280, 720))
            for lang in ("pt", "en"):
                set_lang(lang)
                menu.render(surf, *fonts)
            assert menu.quality_toggle_rect.width > 0 and menu.style_toggle_rect.width > 0 and not menu.quality_toggle_rect.colliderect(menu.style_toggle_rect)
            menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
            assert quality.get_effects_quality() == "low"
            menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_v))
            assert voxel_renderer.get_render_style() == "cel"
            menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=menu.quality_toggle_rect.center))
            assert quality.get_effects_quality() == "high"
            with open(quality.SETTINGS_PATH, encoding="utf-8") as f:
                video = json.load(f)["video"]
            assert video == {"effects_quality": "high", "character_style": "cel"}, video
        finally:
            quality.SETTINGS_PATH = real_path
            _restore()
            voxel_renderer.set_render_style("detailed")
            set_lang("pt")
    print("  [OK] Menu de opções: botões de qualidade e de estilo (teclas E e V, clique), em PT e EN, gravando só a chave do vídeo.", flush=True)


def test_effects_quality():
    test_quality_api_and_settings_file()
    test_low_quality_cuts_particles()
    test_textures_follow_quality()
    test_opacity_is_baked_not_set_alpha()
    test_lighting_budget_improved()
    test_settings_menu_toggles()


if __name__ == "__main__":
    test_effects_quality()
    print("=== TESTE 6.5.6 CONCLUÍDO ===", flush=True)
