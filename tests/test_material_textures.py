"""
Teste da 6.5.8 (texturas de material nas roupas): padrões novos, caixas orientadas com textura, materiais por lutador
e o comportamento na qualidade baixa.
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_material_textures.py
"""
import math
import os
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import numpy as np
import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src.effects import quality
from src.entities import model_kit, voxel_models
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric import voxel_renderer, voxel_textures
from src.isometric.camera import Camera
from src.isometric.voxel_renderer import draw_oriented_voxel_box, draw_voxel_box

NEW = ("silk", "latex", "leather", "velvet", "brocade", "canvas", "knit", "brushed_metal", "lacquer")
FIGHTERS = ("kenshin", "murasaki", "musashi", "ninja", "american", "saitou", "rifleman", "kasumi", "tomoe", "pirate", "musketeer", "okuni")


def _cam(zoom=3.0):
    cam = Camera(0.0, 0.0)
    cam.zoom = zoom
    return cam


def _canvas():
    surf = pygame.Surface((1280, 720))
    surf.fill((30, 30, 36))
    return surf


def _arr(surf):
    return pygame.surfarray.array3d(surf).astype(int)


def test_new_patterns_exist_and_draw():
    for name in NEW:
        assert name in voxel_textures.PATTERNS, name
        plain, textured = _canvas(), _canvas()
        draw_voxel_box(plain, _cam(), 0.0, 0.0, 0.0, 1.2, 1.2, 1.4, (150, 110, 70))
        draw_voxel_box(textured, _cam(), 0.0, 0.0, 0.0, 1.2, 1.2, 1.4, (150, 110, 70), texture=name)
        assert np.abs(_arr(plain) - _arr(textured)).sum() > 0, f"{name}: não desenhou nada numa face grande"
        again = _canvas()
        draw_voxel_box(again, _cam(), 0.0, 0.0, 0.0, 1.2, 1.2, 1.4, (150, 110, 70), texture=name)
        assert (_arr(again) == _arr(textured)).all(), f"{name}: o desenho não é determinístico"
        small_plain, small_tex = _canvas(), _canvas()
        draw_voxel_box(small_plain, _cam(1.0), 0.0, 0.0, 0.0, 0.1, 0.1, 0.1, (150, 110, 70))
        draw_voxel_box(small_tex, _cam(1.0), 0.0, 0.0, 0.0, 0.1, 0.1, 0.1, (150, 110, 70), texture=name)
        assert (_arr(small_plain) == _arr(small_tex)).all(), f"{name}: faces minúsculas ficam lisas"
    print(f"  [OK] {len(NEW)} padrões novos (seda, látex, couro, veludo, brocado, lona, malha, metal escovado, laca): desenham, são determinísticos e somem em faces pequenas.", flush=True)


def test_oriented_boxes_take_textures():
    def draw(texture, alpha=255):
        surf = _canvas()
        draw_oriented_voxel_box(surf, _cam(), 0.0, 0.0, 0.2, 0.7, 0.5, 0.3, 1.1, 0.5, 0.5, (90, 30, 150), texture=texture, alpha=alpha)
        return _arr(surf)

    plain = draw(None)
    for name in NEW:
        assert np.abs(draw(name) - plain).sum() > 0, f"{name}: a caixa orientada não ganhou textura"
    assert (draw("latex", alpha=120) != draw(None, alpha=120)).sum() == 0, "translúcido não leva textura"
    quality.set_effects_quality("low")
    try:
        assert (draw("latex") == plain).all(), "qualidade baixa: sem textura"
    finally:
        quality.set_effects_quality("high")
    print("  [OK] Caixas orientadas (mangas, capas, braços) aceitam textura; translúcidas e a qualidade baixa ficam lisas.", flush=True)


def test_every_fighter_declares_materials():
    from src.entities import (anne_model, hanzo_model, joe_model, julie_model, kasumi_model, kenshi_model, murasaki_model, musashi_model,
                              saitou_model, teppo_model, tomoe_model)
    modules = {"kenshin": kenshi_model, "murasaki": murasaki_model, "musashi": musashi_model, "ninja": hanzo_model, "american": joe_model, "saitou": saitou_model,
               "rifleman": teppo_model, "kasumi": kasumi_model, "tomoe": tomoe_model, "pirate": anne_model, "musketeer": julie_model}
    for name, module in modules.items():
        mats = model_kit.material_map(module.pal(), module.MATERIALS)
        assert len(mats) >= 4, f"{name}: poucos materiais ({len(mats)})"
        assert set(mats.values()) <= set(voxel_textures.PATTERNS) | {"planks"}, f"{name}: textura desconhecida"
    assert model_kit.material_map(murasaki_model.pal(), murasaki_model.MATERIALS)[tuple(murasaki_model.pal()["suit"])] == "latex"
    assert model_kit.material_map(kasumi_model.pal(), kasumi_model.MATERIALS)[tuple(kasumi_model.pal()["pants"])] == "latex"
    assert model_kit.material_map(kenshi_model.pal(), kenshi_model.MATERIALS)[tuple(kenshi_model.pal()["kimono"])] == "silk"
    assert model_kit.material_map(julie_model.pal(), julie_model.MATERIALS)[tuple(julie_model.pal()["cape"])] == "velvet"
    print("  [OK] Os 11 lutadores com modelo declaram materiais (látex em Murasaki e Kasumi, seda em Kenshi, veludo na capa da Julie...).", flush=True)


def _fighter(char, zoom=3.6, state="IDLE", timer=0.0, az=0.0):
    surf = _canvas()
    cam = _cam(zoom)
    cam.set_azimuth(math.radians(az))
    render_voxel_humanoid(surf, cam, 0.0, 0.0, 0.0, 1.0, 1.0, state, timer, True, char, walk_timer=0.3)
    return _arr(surf)


def test_fighters_change_with_quality_and_budget():
    changed = []
    for char in FIGHTERS:
        high = _fighter(char)
        quality.set_effects_quality("low")
        try:
            low = _fighter(char)
        finally:
            quality.set_effects_quality("high")
        diff = int((np.abs(high - low).sum(axis=2) > 0).sum())
        assert diff > 30, f"{char}: as texturas de material não aparecem ({diff} pixels)"
        changed.append(diff)
    results = {}
    for level in ("high", "low"):
        quality.set_effects_quality(level)
        try:
            start = time.perf_counter()
            count = 0
            for char in FIGHTERS:
                for k in range(6):
                    _fighter(char, zoom=3.0, state="ATTACK" if k % 2 else "WALK", timer=0.1)
                    count += 1
            results[level] = (time.perf_counter() - start) * 1000.0 / count
        finally:
            quality.set_effects_quality("high")
    assert results["high"] < 25.0, f"{results['high']:.1f} ms por quadro com texturas a zoom 3 (inclui limpar a tela)"
    print(f"  [OK] 12 lutadores mudam com a qualidade ({min(changed)} a {max(changed)} px); custo a zoom 3: {results['high']:.1f} ms (alta) e {results['low']:.1f} ms (baixa).", flush=True)


def test_material_textures():
    test_new_patterns_exist_and_draw()
    test_oriented_boxes_take_textures()
    test_every_fighter_declares_materials()
    test_fighters_change_with_quality_and_budget()


if __name__ == "__main__":
    test_material_textures()
    print("=== TESTE 6.5.8 CONCLUÍDO ===", flush=True)
