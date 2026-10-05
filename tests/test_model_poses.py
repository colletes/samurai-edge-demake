"""
Teste da 6.5.5 (infraestrutura e piloto Okuni): movimento secundário de tecido, rosto de maquiagem, leques e poses.
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_model_poses.py
"""
import math
import os
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import numpy as np
import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src.config import COLOR_KABUKI_RED, COLOR_KABUKI_WHITE
from src.effects import particles
from src.entities import okuni_model
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric import cloth
from src.isometric.camera import Camera
import capture_sprite_sheet as css

DT = 1 / 60


def _render(state="IDLE", timer=0.0, facing=(1.0, 1.0), walk=0.3, moving=False, az=0.0, zoom=3.0, char="okuni"):
    surf = pygame.Surface((1280, 720))
    surf.fill((34, 36, 44))
    cam = Camera(0.0, 0.0)
    cam.set_azimuth(math.radians(az))
    cam.zoom = zoom
    render_voxel_humanoid(surf, cam, 0.0, 0.0, 0.0, facing[0], facing[1], state, timer, True, char, walk_timer=walk, is_moving=moving)
    return surf


def _diff(a, b):
    return int((np.abs(pygame.surfarray.array3d(a).astype(int) - pygame.surfarray.array3d(b).astype(int)).sum(axis=2) > 0).sum())


def test_cloth_chain():
    still = cloth.chain_offsets(3, 1.0, 0.0, (0.0, 0.0), (1.0, 0.0))
    assert len(still) == 3
    running = cloth.chain_offsets(3, 1.0, 0.0, (-0.07, 0.0), (0.0, 1.0), freq=7.0)
    assert running[2][0] < running[0][0] < 0, "a ponta é arrastada para trás do movimento, mais que a raiz"
    windy = cloth.chain_offsets(3, 1.0, 0.0, (0.0, 0.0), (0.0, 1.0), wind=(3.0, 0.0))
    calm = cloth.chain_offsets(3, 1.0, 0.0, (0.0, 0.0), (0.0, 1.0))
    assert windy[2][0] > calm[2][0] + 0.05, "o vento empurra o tecido"
    xs = {round(cloth.chain_offsets(3, t / 10.0, 0.0, (0.0, 0.0), (1.0, 0.0))[2][0], 4) for t in range(30)}
    assert len(xs) > 10, "em repouso o tecido balança no tempo"
    lagged = cloth.chain_offsets(3, 2.0, 0.0, (0.0, 0.0), (1.0, 0.0))
    assert lagged[0] != lagged[1] != lagged[2], "cada segmento tem a sua fase"
    particles.set_wind_source(lambda x, y: (1.5, -0.5))
    try:
        assert cloth.wind_at(3.0, 4.0) == (1.5, -0.5)
    finally:
        particles.set_wind_source(None)
    assert cloth.wind_at(3.0, 4.0) == (0.0, 0.0)
    print("  [OK] Tecido: a ponta é arrastada e balança com fase própria, em repouso oscila e o vento da arena o empurra.", flush=True)


def test_okuni_face_has_makeup_and_no_clown_nose():
    calls = []
    real = okuni_model._box

    def spy(c, x, y, z, w, d, h, color, outline=True, texture=None):
        calls.append((z, w, d, h, tuple(color)))
        return real(c, x, y, z, w, d, h, color, outline, texture)

    okuni_model._box = spy
    try:
        _render(facing=(1.0, 1.0))
    finally:
        okuni_model._box = real
    reds = [(w, d, h) for z, w, d, h, color in calls if color in (okuni_model.EYE_RED, okuni_model.LIP_RED)]
    assert len(reds) == 3, f"duas sombras de olho e os lábios, sem bolinha vermelha central ({len(reds)})"
    assert all(max(w, d) <= 0.04 for w, d, h in reds), "marcas vermelhas pequenas, nada de nariz de bola"
    assert not any(tuple(color) == tuple(COLOR_KABUKI_RED) and max(w, d) < 0.1 for _, w, d, _, color in calls), "o vermelho antigo do nariz sumiu"
    assert any(tuple(color) == tuple(COLOR_KABUKI_WHITE) and w >= 0.13 for _, w, d, h, color in calls), "rosto branco"
    print("  [OK] O rosto da Okuni tem maquiagem (olhos e lábios pequenos em rosto branco) e o nariz de bola vermelho sumiu.", flush=True)


def test_poses_idle_fans_and_attack_arc():
    opened, closed = [], []
    real_open, real_closed = okuni_model._open_fan, okuni_model._closed_fan
    okuni_model._open_fan = lambda *a, **k: (opened.append(1), real_open(*a, **k))[1]
    okuni_model._closed_fan = lambda *a, **k: (closed.append(1), real_closed(*a, **k))[1]
    try:
        _render()
        assert len(opened) == 1 and len(closed) == 1, "neutra: leque aberto erguido e leque fechado baixo"
        opened.clear()
        closed.clear()
        _render("ATTACK", 0.1)
        assert len(opened) == 2 and not closed, "no ataque os dois leques abrem"
    finally:
        okuni_model._open_fan, okuni_model._closed_fan = real_open, real_closed
    ns = type("C", (), {})()
    ns.base_x = ns.base_y = 0.0
    ns.torso_z, ns.fx, ns.fy, ns.px, ns.py = 0.6, 1.0, 0.0, 0.0, 1.0
    spreads = []
    for p in (0.05, 0.2, 0.45, 0.7, 0.9):
        ns.atk_progress = p
        arm_l, arm_r = okuni_model.attack_arms(ns)
        spreads.append(abs(arm_l[1] - arm_r[1]))
    assert spreads[0] < 0.2 and spreads[-1] > 0.6, f"cruzados na antecipação e abertos no fim ({spreads})"
    assert spreads[1:] == sorted(spreads[1:]) and spreads[1] < spreads[0], "os braços se cruzam na antecipação e depois só abrem"
    print(f"  [OK] Postura neutra (leque aberto + fechado) e ataque com antecipação cruzada e varredura aberta ({spreads[0]:.2f} -> {spreads[-1]:.2f}).", flush=True)


def test_every_state_renders_at_all_azimuths_and_cloth_moves():
    for az in (0, 45, 135):
        for state, timer, moving in (("IDLE", 0.0, False), ("WALK", 0.0, True), ("ATTACK", 0.08, False), ("ROLL", 0.1, True),
                                     ("PARRY", 0.1, False), ("STUNNED", 0.3, False), ("DEAD", 0.0, False)):
            surf = _render(state, timer, moving=moving, az=az)
            assert surf.get_at((640, 300)) is not None
        assert _diff(_render(az=az, walk=0.1), _render(az=az, walk=0.9)) > 20, f"azimute {az}: o tecido e a respiração mudam no tempo"
    particles.set_wind_source(lambda x, y: (4.0, 0.0))
    try:
        windy = _render(walk=0.5)
    finally:
        particles.set_wind_source(None)
    assert _diff(windy, _render(walk=0.5)) > 30, "o vento mexe nas mangas e na saia"
    print("  [OK] Todos os estados renderizam em 0/45/135; o tecido muda com o tempo e com o vento.", flush=True)


def test_sheet_frames_and_budget():
    renderer = css.CellRenderer(2.4)
    sections = dict(css._cells_for("okuni", renderer))
    for title, cells in sections.items():
        if title.startswith(("CAMINHADA", "ATAQUE")):
            distinct = len({pygame.surfarray.array3d(img).tobytes() for _, img in cells})
            assert distinct >= 6, f"{title}: {distinct} quadros distintos"
    start = time.perf_counter()
    for k in range(120):
        _render("ATTACK" if k % 2 else "WALK", 0.1, moving=k % 2 == 0, walk=k * DT, zoom=1.0)
    ms = (time.perf_counter() - start) * 1000.0 / 120
    assert ms < 8.0, f"{ms:.1f} ms por quadro"
    print(f"  [OK] Quadros do ataque e da caminhada diferentes na folha; custo {ms:.1f} ms por quadro (render inclui limpar a tela).", flush=True)


def test_model_poses():
    test_cloth_chain()
    test_okuni_face_has_makeup_and_no_clown_nose()
    test_poses_idle_fans_and_attack_arc()
    test_every_state_renders_at_all_azimuths_and_cloth_moves()
    test_sheet_frames_and_budget()
    test_kenshi_and_murasaki_render_in_both_styles()
    test_cel_outline_and_style_scope()
    test_kenshi_murasaki_attack_and_sheet()
    test_cel_budget_and_setting()
    test_musashi_two_blades_and_combo()
    test_all_fighters_have_models()


def test_musashi_two_blades_and_combo():
    from src.entities import musashi_model
    from src.entities.voxel_models import render_voxel_humanoid
    from src.isometric import voxel_renderer
    blades, trails = [], []
    real_blade, real_trail = musashi_model._blade, musashi_model._slash_trail
    musashi_model._blade = lambda *a, **k: (blades.append(k.get("short", False)), real_blade(*a, **k))[1]
    musashi_model._slash_trail = lambda *a, **k: (trails.append(a[-1]), real_trail(*a, **k))[1]

    def draw(state, timer, moving=False, step=None, az=0):
        surf = pygame.Surface((1280, 720))
        surf.fill((34, 36, 44))
        cam = Camera(0.0, 0.0)
        cam.set_azimuth(math.radians(az))
        cam.zoom = 3.0
        props = {"combo_step": step} if step else None
        render_voxel_humanoid(surf, cam, 0.0, 0.0, 0.0, 1.0, 1.0, state, timer, True, "musashi", walk_timer=0.3, is_moving=moving, extra_props=props)
        return surf

    try:
        draw("IDLE", 0.0)
        assert sorted(blades) == [False, True], "neutra: katana e wakizashi desembainhadas"
        blades.clear()
        draw("WALK", 0.0, moving=True)
        assert not blades, "na caminhada as lâminas voltam para as bainhas"
        draw("PARRY", 0.1)
        assert sorted(blades) == [False, True], "defesa: duas lâminas cruzadas"
        for step in (1, 2, 3):
            blades.clear()
            frames = [draw("ATTACK", 0.18 * (1.0 - p), step=step, az=az) for p in (0.15, 0.5, 0.85) for az in (0, 90)]
            assert len(blades) == 12, f"golpe {step}: as duas lâminas em cada quadro"
            assert len({pygame.surfarray.array3d(f).tobytes() for f in frames}) >= 5, f"golpe {step}: quadros distintos"
        assert trails == [1] * 6 + [2] * 6 + [3] * 6, "o rastro segue o passo do combo"
    finally:
        musashi_model._blade, musashi_model._slash_trail = real_blade, real_trail
    renderer = css.CellRenderer(2.4)
    for title, cells in css._cells_for("musashi", renderer):
        if title.startswith("CAMINHADA"):
            distinct = len({pygame.surfarray.array3d(img).tobytes() for _, img in cells})
            assert distinct >= 7, f"Musashi {title}: {distinct} quadros distintos (antes eram só 5)"
    assert voxel_renderer.get_render_style() == "detailed"
    print("  [OK] Musashi: duas lâminas na neutra e na defesa, bainhas na caminhada, 3 golpes do combo com rastro e caminhada com 7+ quadros distintos.", flush=True)
def test_all_fighters_have_models():
    from src.entities import voxel_models
    from src.entities.voxel_models import render_voxel_humanoid
    from src.isometric import voxel_renderer
    expected = {"kenshin", "murasaki", "musashi", "ninja", "american", "saitou", "rifleman", "kasumi", "tomoe", "pirate", "musketeer"}
    assert set(voxel_models.MODEL_FIGHTERS) == expected, "11 lutadores com modelo próprio (a Okuni tem o dela por ganchos)"
    assert set(voxel_models.CEL_FIGHTERS) == {"kenshin", "murasaki"}
    voxel_renderer.set_render_style("cel")
    try:
        _render(char="musashi", zoom=3.2)
        assert _count_ink(_render(char="musashi", zoom=3.2)) < 60, "o cel-shading continua só em Kenshi e Murasaki"
    finally:
        voxel_renderer.set_render_style("detailed")
    states = (("IDLE", 0.0, False), ("WALK", 0.0, True), ("ATTACK", 0.02, False), ("ATTACK", 0.1, False), ("ATTACK", 0.17, False), ("ROLL", 0.1, True),
              ("PARRY", 0.1, False), ("STUNNED", 0.3, False), ("DEAD", 0.0, False), ("CAPE_FLOURISH", 0.08, False), ("FLECHE", 0.1, False),
              ("CUTLASS_CLEAVE", 0.1, False), ("ZEROSHIKI", 0.1, False), ("GATOTSU_CHARGE", 0.1, False))
    for char in sorted(expected):
        for az in (0, 70, 135, 250):
            for state, timer, moving in states:
                _render(state, timer, moving=moving, az=az, char=char)
        assert _diff(_render(walk=0.1, char=char), _render(walk=0.9, char=char)) > 20, f"{char}: o tecido e a respiração mudam no tempo"
        assert _diff(_render("IDLE", char=char), _render("ATTACK", 0.08, char=char)) > 80, f"{char}: o ataque muda a pose"
    props = {"has_kunai": False}
    surf = pygame.Surface((1280, 720))
    surf.fill((34, 36, 44))
    cam = Camera(0.0, 0.0)
    cam.zoom = 3.0
    render_voxel_humanoid(surf, cam, 0.0, 0.0, 0.0, 1.0, 1.0, "IDLE", 0.0, True, "yellow_ninja", extra_props=props)
    assert _diff(surf, _render(char="ninja", zoom=3.0)) > 20, "sem kunai a mão direita fica vazia"
    ghost = pygame.Surface((1280, 720))
    ghost.fill((34, 36, 44))
    render_voxel_humanoid(ghost, cam, 0.0, 0.0, 0.0, 1.0, 1.0, "IDLE", 0.0, True, "kasumi", alpha=90)
    assert _diff(ghost, _render(char="kasumi", zoom=3.0)) > 50, "o alfa de furtividade (Kasumi) é respeitado"
    start = time.perf_counter()
    count = 0
    for char in sorted(expected):
        for k in range(20):
            _render("ATTACK" if k % 2 else "WALK", 0.1, moving=k % 2 == 0, walk=k * DT, zoom=1.0, char=char)
            count += 1
    ms = (time.perf_counter() - start) * 1000.0 / count
    assert ms < 12.0, f"{ms:.1f} ms por quadro"
    print(f"  [OK] 11 lutadores com modelo próprio: todos os estados em 4 azimutes (incluindo CAPE_FLOURISH, FLECHE, GATOTSU), kunai e furtividade; {ms:.1f} ms por quadro.", flush=True)


INK = (18, 16, 22)


def _count_ink(surf):
    arr = pygame.surfarray.array3d(surf)
    return int(((arr[:, :, 0] == INK[0]) & (arr[:, :, 1] == INK[1]) & (arr[:, :, 2] == INK[2])).sum())


def test_kenshi_and_murasaki_render_in_both_styles():
    from src.isometric import voxel_renderer
    try:
        for style in ("detailed", "cel"):
            voxel_renderer.set_render_style(style)
            for char in ("kenshin", "murasaki"):
                for az in (0, 45, 135, 200):
                    for state, timer, moving in (("IDLE", 0.0, False), ("WALK", 0.0, True), ("ATTACK", 0.02, False), ("ATTACK", 0.08, False),
                                                 ("ATTACK", 0.14, False), ("ROLL", 0.1, True), ("PARRY", 0.1, False), ("STUNNED", 0.3, False),
                                                 ("DEAD", 0.0, False)):
                        _render(state, timer, moving=moving, az=az, char=char)
                assert _diff(_render(walk=0.1, char=char), _render(walk=0.9, char=char)) > 20, f"{char}/{style}: o tecido muda no tempo"
    finally:
        voxel_renderer.set_render_style("detailed")
    print("  [OK] Kenshi e Murasaki renderizam todos os estados em 4 azimutes nos estilos detalhado e cel, e o tecido balança.", flush=True)


def test_cel_outline_and_style_scope():
    from src.isometric import voxel_renderer
    voxel_renderer.set_render_style("cel")
    try:
        cel = _render(char="kenshin", zoom=3.2)
        assert voxel_renderer.get_render_style() == "cel"
        assert _count_ink(cel) > 400, "silhueta com tinta dos sprites"
        other = _render(char="okuni", zoom=3.2)
        assert _count_ink(other) < 60, "quem não tem modelo cel continua no estilo detalhado, sem contorno de tinta"
        light, mid, shadow = voxel_renderer.cel_ramp((129, 30, 50))
        assert mid == (129, 30, 50) and light == (187, 53, 69) and shadow == (69, 13, 33), "rampa amostrada do sprite"
        l2, m2, s2 = voxel_renderer.cel_ramp((10, 200, 10))
        assert sum(l2) > sum(m2) > sum(s2), "rampa calculada: luz > médio > sombra"
    finally:
        voxel_renderer.set_render_style("detailed")
    assert _count_ink(_render(char="kenshin", zoom=3.2)) < 60, "no estilo detalhado não há contorno de tinta"
    assert voxel_renderer.get_render_style() == "detailed"
    with voxel_renderer.render_style("cel"):
        assert voxel_renderer.get_render_style() == "cel"
    assert voxel_renderer.get_render_style() == "detailed"
    print("  [OK] Cel-shading: silhueta de tinta, rampas dos sprites, só nos lutadores com modelo e o estilo volta ao detalhado.", flush=True)


def test_kenshi_murasaki_attack_and_sheet():
    from src.entities import kenshi_model, murasaki_model
    spy_kenshi, spy_murasaki = [], []
    real_k, real_m = kenshi_model._slash_trail, murasaki_model._ball_trail
    kenshi_model._slash_trail = lambda *a, **k: (spy_kenshi.append(1), real_k(*a, **k))[1]
    murasaki_model._ball_trail = lambda *a, **k: (spy_murasaki.append(1), real_m(*a, **k))[1]
    try:
        _render("IDLE", char="kenshin")
        _render("IDLE", char="murasaki")
        assert not spy_kenshi and not spy_murasaki, "sem rastro fora do ataque"
        _render("ATTACK", 0.152, char="kenshin")
        assert not spy_kenshi, "a lâmina ainda está sendo sacada"
        _render("ATTACK", 0.08, char="kenshin")
        _render("ATTACK", 0.08, char="murasaki")
        assert spy_kenshi and spy_murasaki, "rastro do corte e da bola no ataque"
    finally:
        kenshi_model._slash_trail, murasaki_model._ball_trail = real_k, real_m
    ns = type("C", (), {})()
    ns.base_x = ns.base_y = 0.0
    ns.torso_z, ns.fx, ns.fy, ns.px, ns.py = 0.6, 1.0, 0.0, 0.0, 1.0
    ns.pelvis_z, ns.base_z = 0.48, 0.0
    sides = []
    for p in (0.05, 0.3, 0.5, 0.7, 0.95):
        ns.atk_progress = p
        sides.append(murasaki_model.attack_arms(ns)[1][1])
    assert sides[0] < 0 < sides[-1], f"a foice cruza da direita para a esquerda ({sides})"
    ns.atk_progress = 0.05
    grip = kenshi_model.attack_arms(ns)[1]
    ns.atk_progress = 0.6
    swing = kenshi_model.attack_arms(ns)[1]
    assert abs(grip[0] - swing[0]) + abs(grip[1] - swing[1]) > 0.1, "a mão sai do cabo para o arco do corte"
    renderer = css.CellRenderer(2.4)
    for name in ("kenshi", "murasaki"):
        for title, cells in css._cells_for(name, renderer):
            if title.startswith("ATAQUE"):
                distinct = len({pygame.surfarray.array3d(img).tobytes() for _, img in cells})
                assert distinct >= 7, f"{name} {title}: {distinct} quadros distintos"
    print("  [OK] Ataques: Kenshi saca antes de cortar e a foice cruza o corpo; rastros só no golpe; 8 quadros de ataque distintos.", flush=True)


def test_cel_budget_and_setting():
    import json
    import tempfile
    from src.isometric import voxel_renderer
    voxel_renderer.set_render_style("cel")
    try:
        start = time.perf_counter()
        for k in range(120):
            _render("ATTACK" if k % 2 else "WALK", 0.1, moving=k % 2 == 0, walk=k * DT, zoom=1.0, char="murasaki" if k % 4 < 2 else "kenshin")
        ms = (time.perf_counter() - start) * 1000.0 / 120
    finally:
        voxel_renderer.set_render_style("detailed")
    assert ms < 12.0, f"{ms:.1f} ms por quadro em cel"
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "settings.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"video": {"character_style": "cel"}}, f)
        voxel_renderer.load_render_style(path)
        assert voxel_renderer.get_render_style() == "cel"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"video": {"character_style": "qualquer"}}, f)
        voxel_renderer.load_render_style(path)
        assert voxel_renderer.get_render_style() == "detailed", "valor inválido cai no detalhado"
        voxel_renderer.load_render_style(os.path.join(tmp, "nao_existe.json"))
        assert voxel_renderer.get_render_style() == "detailed"
    with open(os.path.join(ROOT, "settings.json"), encoding="utf-8") as f:
        assert json.load(f)["video"]["character_style"] in ("detailed", "cel")
    print(f"  [OK] Cel-shading custa {ms:.1f} ms por quadro (zoom 1) e `video.character_style` do settings.json é lido com segurança.", flush=True)


if __name__ == "__main__":
    test_model_poses()
    print("=== TESTE 6.5.5 (INFRA, OKUNI E OS 11 LUTADORES COM MODELO) CONCLUÍDO ===", flush=True)
