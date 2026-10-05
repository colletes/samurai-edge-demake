"""
Teste da Fase 6 - Entregável 6.2: Gerador de Arenas Parametrizado.

Valida que:
1. As duas arenas existentes (Bambu e Kyoto), agora geradas por `ArenaSpec`, mantêm o layout e a
   renderização da implementação anterior (tiles, props e imagens de referência em
   tests/fixtures/arena_parity/ nos azimutes 0/45/135).
2. O motor é genérico: uma arena sintética (apenas de teste, não registrada) é montada, renderizada
   em vários azimutes e gera spawns/palco válidos usando só tipos de prop registrados.
3. `validate_spec` rejeita especificações inválidas (prop desconhecido, tile sem estilo, estrutura sem
   âncora, palco ou spawn em água, cor/iluminação inválidas).
4. `pick_spawns` respeita a distância mínima e as regras de cada arena; perigos continuam por spec.
5. O registro (`arena_ids`/`create_arena`) e o `main.py` não dependem mais de ramificações por arena.
"""
import dataclasses
import hashlib
import math
import os
import random
import re
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
pygame.init()
pygame.font.init()
pygame.display.set_mode((1280, 720))

import main
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, ARENA_BAMBOO, ARENA_KYOTO, ARENA_GANRYU
from src.isometric.camera import Camera
from src.world import arena_generator as ag
from src.world.arena_generator import (
    ArenaMap, ArenaSpec, ArenaSpecError, AtmosphereEffect, FillLayer, LightingEnvironment, LightSource,
    PropSpec, RectLayer, ScatterSpec, SpawnRule, StageSpec, StructureSpec, TileStyle, validate_spec,
)
from src.world.arenas import BAMBOO_SPEC, KYOTO_SPEC, arena_ids, create_arena
from src.roster import ARENA_ORDER as ROSTER_ARENAS
from src.world.kyoto_map import KyotoMap
from src.world.map_data import GameMap, TILE_BRIDGE, TILE_WATER

FIXTURES = os.path.join(ROOT, "tests", "fixtures", "arena_parity")
PARITY_TOLERANCE = 1.0  # diferença média absoluta por canal (0..255) tolerada contra a imagem de referência

# Assinaturas do layout do Bambu com dojo e karesansui (6.3.6; antes eram 215 bambus)
BAMBOO_TILES_MD5 = "702d22962846f1b3270420817dc4dbc5"
BAMBOO_BAMBOO_COUNT = 192
BAMBOO_BAMBOO_CHECKSUM = 22156.0271


def _tiles_md5(game_map) -> str:
    return hashlib.md5(str(game_map.tiles).encode()).hexdigest()


def render_frame(game_map, azimuth_deg: float):
    """Mesma rotina usada para gerar as imagens de referência (semente fixa por causa dos sprites aleatórios)."""
    random.seed(7)
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill(game_map.bg_color)
    cam = Camera(11.0, 11.0)
    cam.set_azimuth(math.radians(azimuth_deg))
    game_map.render_terrain(surf, cam, 1.0)
    queue = [(cam.depth(*main.static_item_center(t, o)), t, o) for _, t, o in main.build_static_render_queue(game_map)]
    queue.sort(key=lambda i: i[0])
    for _, kind, obj in queue:
        if kind in ("bamboo", "building", "lantern"):
            obj.render(surf, cam, 1.0)
        else:
            obj.render(surf, cam)
    for fx, fy, fz in game_map.fireflies:
        pygame.draw.circle(surf, (180, 255, 80), cam.apply(fx, fy, fz), 3)
    return pygame.transform.smoothscale(surf, (640, 360))


def _mean_abs_diff(a: pygame.Surface, b: pygame.Surface) -> float:
    import numpy as np
    arr_a = pygame.surfarray.array3d(a).astype("int16")
    arr_b = pygame.surfarray.array3d(b).astype("int16")
    assert arr_a.shape == arr_b.shape
    return float(np.abs(arr_a - arr_b).mean())


def _synthetic_spec(**overrides) -> ArenaSpec:
    """Arena sintética 12x12 (apenas de teste): grama, um lago e uma trilha de terra, só com tipos registrados."""
    grass, earth, water = 1, 2, 3
    spec = ArenaSpec(
        id="synthetic_test",
        name="Arena Sintética",
        cols=12,
        rows=12,
        bg_color=(10, 12, 20),
        music="bgm_bamboo",
        tile_styles={
            grass: TileStyle("flat", ((40, 90, 40),)),
            earth: TileStyle("flat", ((110, 90, 60),), edge=(60, 50, 30)),
            water: TileStyle("water", ((30, 70, 120), (60, 110, 160))),
        },
        layers=(
            FillLayer(grass),
            RectLayer(earth, 5, 6, 0, 11),
            RectLayer(water, 8, 10, 8, 10),
        ),
        props=(
            PropSpec("rock", 3.0, 3.0, {"radius": 0.6, "height": 0.8}),
            PropSpec("rock", 3.5, 8.5, {"radius": 0.5, "height": 0.6}),
            PropSpec("stone_lantern", 6.0, 2.0),
        ),
        scatters=(ScatterSpec("bamboo", seed=3, blocked_tiles=(water, earth), center=(6.0, 6.0)),),
        spawns=SpawnRule(margin=2.0, fallback=((1.5, 6.0), (10.5, 2.5))),
        stage=StageSpec(6.0, 6.0),
        lighting=LightingEnvironment(
            ambient_color=(200, 210, 255), ambient_strength=0.8, vignette=0.3,
            lights=(LightSource(6.0, 2.0, 1.0, (255, 200, 120), 3.0, flicker=0.2),),
            atmosphere=(AtmosphereEffect("fireflies", 1.0, ((4.0, 4.0, 0.5),)),),
        ),
    )
    return dataclasses.replace(spec, **overrides) if overrides else spec


def test_registry_and_creation():
    ids = arena_ids()
    assert ids[:3] == [ARENA_BAMBOO, ARENA_KYOTO, ARENA_GANRYU], ids
    assert set(ids) <= set(ROSTER_ARENAS), ids
    assert "synthetic_test" not in ids, "a arena sintética é só de teste e não pode estar registrada"
    bamboo, kyoto = create_arena(ARENA_BAMBOO), create_arena(ARENA_KYOTO)
    assert isinstance(bamboo, ArenaMap) and isinstance(kyoto, ArenaMap)
    assert isinstance(GameMap(), ArenaMap) and isinstance(KyotoMap(), ArenaMap)
    assert (bamboo.cols, bamboo.rows) == (22, 22) or bamboo.cols == kyoto.cols
    assert bamboo.music == "bgm_bamboo" and kyoto.music == "bgm_kyoto"
    assert not bamboo.has_hazards and kyoto.has_hazards
    assert bamboo.bg_color != kyoto.bg_color
    for arena in (bamboo, kyoto):
        for attr in ("tiles", "rocks", "trees", "torii_gates", "lanterns", "buildings", "bamboos", "fireflies",
                     "carriages", "falling_debris", "intro_stage_point", "pick_spawns", "render_terrain", "update",
                     "is_water", "is_hidden_in_bamboo", "lighting"):
            assert hasattr(arena, attr), attr
    try:
        create_arena("nao_existe")
    except (KeyError, ArenaSpecError, ValueError):
        pass
    else:
        raise AssertionError("create_arena deveria rejeitar id desconhecido")
    print("  [OK] Registro lista Bambu e Kyoto e cria mapas com o protocolo completo.", flush=True)


def test_bamboo_layout_matches_legacy():
    g = GameMap()
    assert _tiles_md5(g) == BAMBOO_TILES_MD5, "grade de tiles do Bambu mudou"
    assert len(g.bamboos) == BAMBOO_BAMBOO_COUNT
    assert abs(sum(b.wx * 3 + b.wy * 7 for b in g.bamboos) - BAMBOO_BAMBOO_CHECKSUM) < 1e-3
    assert (len(g.rocks), len(g.trees), len(g.torii_gates), len(g.lanterns)) == (6, 1, 1, 5)
    assert g.well is not None and (g.well.wx, g.well.wy) == (6.5, 6.5)
    assert len(g.fireflies) == 7
    x, y, z = g.intro_stage_point()
    assert (x, y) == (11.0, 11.5) and abs(z - 0.559) < 1e-3
    assert g.tiles[int(x)][int(y)] == TILE_BRIDGE
    # Ponte: tiles y=7 e y=15 foram cobertos pela terra batida (comportamento herdado); ponte em y 8..14
    assert {y for y in range(g.rows) if g.tiles[10][y] == TILE_BRIDGE} == set(range(8, 15))
    assert g.is_water(8.5, 11.5) and not g.is_water(10.5, 11.5)
    print("  [OK] Layout do Bambu idêntico ao da implementação anterior.", flush=True)


def test_kyoto_layout():
    k = KyotoMap()
    assert len(k.buildings) == 13 and len(k.lanterns) == 23  # 12 fachadas + posto de guarda; 8 pedra + 6 papel + 3 faixas + 4 nobori + 2 incensários
    assert (len(k.carriages), len(k.falling_debris)) == (0, 0)
    assert len(k.hazards) == 2 and k.has_hazards
    x, y, z = k.intro_stage_point()
    assert (x, y, z) == (11.0, 11.0, 0.0)
    assert not k.is_water(x, y)
    # a rua fica no centro e as calçadas/prédios nas laterais
    assert k.tiles[10][11] != k.tiles[1][11]
    print("  [OK] Layout de Kyoto: 12 fachadas e posto de guarda, decoração do Shinsengumi, 2 perigos por spec.", flush=True)


def test_visual_parity_with_reference_images():
    for name, ctor in (("bamboo", GameMap), ("kyoto", KyotoMap)):
        for az in (0, 45, 135):
            path = os.path.join(FIXTURES, f"{name}_az{az}.png")
            assert os.path.exists(path), f"fixture ausente: {path}"
            reference = pygame.image.load(path).convert()
            random.seed(7)
            frame = render_frame(ctor(), az)
            diff = _mean_abs_diff(frame, reference)
            assert diff <= PARITY_TOLERANCE, f"{name} az{az}: diferença média {diff:.3f} > {PARITY_TOLERANCE}"
    print("  [OK] Renderização igual às imagens de referência (6 quadros, azimutes 0/45/135).", flush=True)


def test_synthetic_arena_is_generic():
    spec = _synthetic_spec()
    validate_spec(spec)
    arena = ArenaMap(spec)
    assert (arena.cols, arena.rows) == (12, 12) and arena.music == "bgm_bamboo"
    assert len(arena.rocks) == 2 and len(arena.lanterns) == 1
    assert len(arena.bamboos) > 0, "scatter deveria gerar bambus em tiles livres"
    assert all(arena.tiles[int(b.wx)][int(b.wy)] == 1 for b in arena.bamboos), "scatter respeita tiles bloqueados"
    assert arena.is_water(9.0, 9.0) and not arena.is_water(2.0, 2.0)
    assert arena.intro_stage_point() == (6.0, 6.0, 0.0)
    assert arena.fireflies == [(4.0, 4.0, 0.5)]
    assert arena.lighting.lights[0].flicker == 0.2
    for _ in range(25):
        a, b = arena.pick_spawns(min_distance=5.0)
        assert math.dist(a, b) >= 5.0 - 1e-9, (a, b)
        assert not arena.is_water(*a) and not arena.is_water(*b)
    camera = Camera(6.0, 6.0)
    for az in (0, 60, 135, 270):
        camera.set_azimuth(math.radians(az))
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(arena.bg_color)
        arena.render_terrain(surf, camera, 0.5)
        queue = main.build_static_render_queue(arena)
        assert queue, "fila estática deveria conter os props da arena sintética"
        assert pygame.transform.average_color(surf) != arena.bg_color, f"nada foi desenhado no azimute {az}"
    arena.update(0.016, [], camera, [], [])  # sem perigos: não deve falhar
    assert not arena.has_hazards
    print("  [OK] Arena sintética gerada, renderizada em 4 azimutes e com spawns válidos.", flush=True)


def _raises(spec: ArenaSpec, fragment: str, builder=validate_spec):
    try:
        builder(spec)
    except ArenaSpecError as exc:
        assert fragment in str(exc), f"mensagem '{exc}' não contém '{fragment}'"
        return
    raise AssertionError(f"spec inválido não foi rejeitado (esperado: {fragment})")


def test_validate_spec_rejects_invalid_specs():
    base = _synthetic_spec()
    validate_spec(base)
    _raises(dataclasses.replace(base, props=(PropSpec("dragao", 3.0, 3.0),)), "prop desconhecido")
    _raises(dataclasses.replace(base, layers=(FillLayer(1), RectLayer(9, 0, 3, 0, 3))), "sem estilo")
    _raises(dataclasses.replace(base, layers=(RectLayer(1, 0, 3, 0, 3),)), "primeira camada")
    _raises(dataclasses.replace(base, layers=(FillLayer(1), RectLayer(2, 0, 30, 0, 3))), "fora da grade")
    _raises(dataclasses.replace(base, structures=(StructureSpec("arched_bridge", 1, {}),)), "tile 'anchor'")
    _raises(dataclasses.replace(base, structures=(StructureSpec("torre_voadora", 1),)), "estrutura desconhecida")
    _raises(dataclasses.replace(base, stage=StageSpec(50.0, 3.0)), "fora do mapa")
    _raises(dataclasses.replace(base, stage=StageSpec(6.0, 6.0, structure=0)), "estrutura inexistente")
    _raises(dataclasses.replace(base, bg_color=(0, 0, 999)), "cor inválida")
    _raises(dataclasses.replace(base, cols=2), "tamanho mínimo")
    _raises(dataclasses.replace(base, spawns=SpawnRule(min_distance=0.0, fallback=((1.5, 6.0), (10.5, 2.5)))), "regra de spawn")
    _raises(dataclasses.replace(base, hazards=(ag.HazardSpec("meteoro"),)), "perigo desconhecido")
    _raises(dataclasses.replace(base, lighting=LightingEnvironment(ambient_strength=2.0)), "0..1")
    _raises(dataclasses.replace(base, lighting=LightingEnvironment(lights=(LightSource(1, 1, 1, (1, 2, 3), 0.0),))),
            "raio não positivo")
    _raises(dataclasses.replace(base, lighting=LightingEnvironment(lights=(LightSource(99, 1, 1, (1, 2, 3), 2.0),))),
            "fora do mapa")
    _raises(dataclasses.replace(
        base, scatters=(ScatterSpec("bamboo", 1, density_inner=1.5),)), "densidades")
    _raises(dataclasses.replace(
        base, tile_styles={**base.tile_styles, 4: TileStyle("flat", ((1, 2, 3),), pattern="parity")}),
        "parity")
    print("  [OK] validate_spec rejeita 17 tipos de especificação inválida.", flush=True)


def test_build_rejects_stage_or_spawn_in_water_or_obstacle():
    base = _synthetic_spec()
    _raises(dataclasses.replace(base, stage=StageSpec(9.0, 9.0)), "água ou obstáculo", builder=ArenaMap)
    _raises(dataclasses.replace(base, spawns=SpawnRule(fallback=((9.0, 9.0), (1.5, 6.0)))), "água ou obstáculo",
            builder=ArenaMap)
    _raises(dataclasses.replace(base, stage=StageSpec(3.0, 3.0)), "água ou obstáculo", builder=ArenaMap)
    print("  [OK] Palco/spawn de reserva em água ou obstáculo é recusado na construção.", flush=True)


def test_spawn_rules_per_arena():
    bamboo, kyoto = create_arena(ARENA_BAMBOO), create_arena(ARENA_KYOTO)
    for _ in range(60):
        a, b = bamboo.pick_spawns(min_distance=7.0)
        assert math.dist(a, b) >= 7.0 - 1e-9
        assert not bamboo.is_water(*a) and not bamboo.is_water(*b)
        a, b = kyoto.pick_spawns(min_distance=7.0)
        assert math.dist(a, b) >= 7.0 - 1e-9
        lo, hi = KYOTO_SPEC.spawns.x_range
        assert lo <= a[0] <= hi and lo <= b[0] <= hi, (a, b)
    # compatibilidade dos auxiliares de spawn do main
    for arena in (bamboo, kyoto):
        a, b = main.get_random_arena_spawns(arena, min_distance=7.0)
        assert math.dist(a, b) >= 7.0 - 1e-9
    print("  [OK] pick_spawns respeita distância mínima, água e faixa de cada arena.", flush=True)


def test_kyoto_hazards_driven_by_spec():
    kyoto = KyotoMap()
    kyoto.carriage_timer = 0.0  # compat com test_game.py
    cam = Camera(11.0, 11.0)
    particles, banners = [], []
    for _ in range(120):
        kyoto.update(0.05, [], cam, particles, banners)
    assert len(kyoto.carriages) > 0 or len(kyoto.falling_debris) > 0, "perigos do spec nunca dispararam"
    print("  [OK] Perigos de Kyoto são instanciados e atualizados a partir do spec.", flush=True)


def test_lighting_is_data_only():
    for spec in (BAMBOO_SPEC, KYOTO_SPEC):
        validate_spec(spec)
        assert isinstance(spec.lighting, LightingEnvironment)
        assert 0.0 <= spec.lighting.ambient_strength <= 1.0
        assert spec.lighting.lights or spec.lighting.atmosphere, f"{spec.id} sem dados de iluminação"
    assert BAMBOO_SPEC.lighting.atmosphere and BAMBOO_SPEC.lighting.atmosphere[0].kind == "fireflies"
    print("  [OK] Iluminação das arenas é dado validado (renderização fica para 6.4).", flush=True)


def test_main_has_no_per_arena_branches():
    with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as fh:
        src = fh.read()
    assert "isinstance(game_map, KyotoMap)" not in src
    assert "KyotoMap()" not in src and "GameMap()" not in src
    assert "create_arena(selected_arena_id)" in src
    assert "play_music(game_map.music)" in src
    with open(os.path.join(ROOT, "src", "ui", "arena_select.py"), encoding="utf-8") as fh:
        sel = fh.read()
    assert "random.choice(arena_ids())" in sel
    print("  [OK] main.py e seleção de arena usam o registro, sem ramificações por arena.", flush=True)


def _walkable_components(arena, step=0.5):
    """Componentes conexos de posições andando (fora de buracos, sólidos e limites); usado para provar que há rota sem salto."""
    from src.entities.samurai import resolve_playable_bounds
    from src.world.arena_generator import PIT_EDGE_MARGIN
    min_x, min_y, max_x, max_y = resolve_playable_bounds(arena)
    nx, ny = int((max_x - min_x) / step) + 1, int((max_y - min_y) / step) + 1

    def ok(i, j):
        x, y = min_x + i * step, min_y + j * step
        if arena.pit_edge_distance(x, y) < PIT_EDGE_MARGIN:
            return False
        return not any(b.check_collision(x, y, 0.35)[0] for b in arena.buildings + arena.rocks)

    def cell(x, y):
        return round((x - min_x) / step), round((y - min_y) / step)

    seen = {}
    comp_id = 0
    for i0 in range(nx):
        for j0 in range(ny):
            if (i0, j0) in seen or not ok(i0, j0):
                continue
            comp_id += 1
            stack = [(i0, j0)]
            seen[(i0, j0)] = comp_id
            while stack:
                i, j = stack.pop()
                for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (i + di, j + dj)
                    if 0 <= n[0] < nx and 0 <= n[1] < ny and n not in seen and ok(*n):
                        seen[n] = comp_id
                        stack.append(n)
    return seen, cell


def test_ganryu_island():
    from src.entities.samurai import STATE_FALL
    from src.world.arena_generator import GAP_WIDTHS, PIT_EDGE_MARGIN
    import tests.test_arena_engine as eng

    arena = create_arena(ARENA_GANRYU)
    assert arena.music == "bgm_ganryu_island" and arena.has_hazards
    classes = sorted(p.gap_class for p in arena.pits)
    assert classes == ["L", "M", "S", "VOID"], classes
    for pit in arena.pits:
        if pit.gap_class != "VOID":
            assert abs(pit.width - GAP_WIDTHS[pit.gap_class]) < 0.02

    # Chegar a pontos de spawn, à ponte e ao penhasco sem pular: todas as regiões de interesse estão conectadas
    seen, cell = _walkable_components(arena)
    (ax, ay), (bx, by) = arena.spec.spawns.fallback
    stage = arena.intro_stage_point()
    ids = {seen.get(cell(ax, ay)), seen.get(cell(bx, by)), seen.get(cell(stage[0], stage[1]))}
    assert None not in ids and len(ids) == 1, f"rota sem salto entre spawns e ponte: {ids}"
    for _ in range(80):
        a, b = arena.pick_spawns()
        assert math.dist(a, b) >= 7.0 - 1e-9
        assert arena.pit_edge_distance(*a) >= 1.0 and arena.pit_edge_distance(*b) >= 1.0
        assert not arena.is_water(*a) and not arena.is_water(*b)
        assert not any(bld.check_collision(p[0], p[1], 0.9)[0] for bld in arena.buildings for p in (a, b))

    # Terreno: areia molhada e rasos reduzem a velocidade; a ponte não
    assert arena.speed_mult_at(2.5, 5.0) == 0.8 and arena.speed_mult_at(0.5, 5.0) == 0.55
    assert arena.speed_mult_at(12.0, 11.0) == 1.0 and not arena.is_water(12.0, 11.0)
    assert arena.intro_stage_point()[2] > 0.1, "palco em cima da ponte"

    # Render em três azimutes: o mapa, os buracos e o barco aparecem
    for az in (0, 45, 135):
        random.seed(5)
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(arena.bg_color)
        camera = Camera(11.0, 11.0)
        camera.set_azimuth(math.radians(az))
        arena.render_terrain(surf, camera, 1.0)
        for _, kind, obj in sorted(main.build_static_render_queue(arena), key=lambda i: camera.depth(*main.static_item_center(i[1], i[2]))):
            obj.render(surf, camera, 1.0) if kind in ("bamboo", "building", "lantern") else obj.render(surf, camera)
        assert pygame.transform.average_color(surf) != arena.bg_color
        cliff = arena.pits[3]
        pit_px = camera.apply((cliff.x0 + cliff.x1) / 2.0, (cliff.y0 + cliff.y1) / 2.0, -1.1)
        assert surf.get_at((int(pit_px[0]), int(pit_px[1])))[:3][0] < 40, f"fundo escuro do penhasco no azimute {az}"

    # A maré empurra quem está parado rumo ao penhasco e ele cai
    random.seed(2)
    victim = eng._fighter_at(eng.CHAR_MUSASHI, 14.5, 15.0)
    opp = eng._fighter_at(eng.CHAR_KENSHIN, 3.0, 3.0)
    fell_at = None
    for i in range(int(16.0 / eng.DT)):
        arena.update(eng.DT, [victim, opp], None, [], [])
        eng.step_fighter(victim, opp, eng.DT, arena, [], [], [])
        if victim.state == STATE_FALL and fell_at is None:
            fell_at = i * eng.DT
    assert fell_at is not None and victim.wx > arena.pits[3].x0 - 1.0, "a maré derruba no penhasco"
    assert not victim.is_alive and victim.fell_into_pit
    print("  [OK] Ilha de Ganryū: classes de buraco, rota sem salto, terreno lento, azimutes e queda pela maré.", flush=True)


def test_iga_rooftops():
    from src.config import ARENA_IGA
    from src.entities.ai_controller import SamuraiAI
    from src.entities.samurai import STATE_FALL
    from src.world.arena_generator import GAP_WIDTHS
    import tests.test_arena_engine as eng

    arena = create_arena(ARENA_IGA)
    assert arena.music == "bgm_iga_rooftops" and not arena.has_hazards and not arena.has_rails
    assert sorted(p.gap_class for p in arena.pits) == ["J", "J", "L", "L", "M", "S", "S"]
    assert all(not p.railed for p in arena.pits), "vãos entre telhados não têm proteção"
    assert len(arena.structures) == 2 and all(type(st).__name__ == "RoofBeam" for st in arena.structures)
    for pit in arena.pits:
        assert abs(pit.width - GAP_WIDTHS[pit.gap_class]) < 0.02

    # Telhados ligados pelas vigas: o chão firme liga oeste, centro e leste sem salto; o beco corta em y = 11
    seen, cell = _walkable_components(arena)
    points = [arena.spec.spawns.fallback[0], (arena.spec.stage.x, arena.spec.stage.y), arena.spec.spawns.fallback[1]]
    ids = {seen.get(cell(*p)) for p in points}
    assert None not in ids and len(ids) == 1, f"as vigas ligam os três telhados: {ids}"
    assert arena.pit_at(7.0, 11.0) is not None and arena.pit_at(7.0, 15.0) is None, "viga atravessa o beco L"
    assert arena.pit_at(15.4, 11.0) is not None and arena.pit_at(15.4, 7.0) is None, "viga atravessa o beco J"

    # Andar pela viga é seguro; andar pelo beco derruba
    walker = eng._fighter_at(eng.CHAR_MUSASHI, 4.0, 15.0)
    for _ in range(int(2.5 / eng.DT)):
        walker.apply_movement(1.0, 0.0, eng.DT, arena)
        walker.update_pit(eng.DT, arena)
    assert walker.is_alive and walker.state != STATE_FALL and walker.wx > 9.0, f"atravessou a viga (x={walker.wx:.2f})"
    faller = eng._fighter_at(eng.CHAR_MUSASHI, 4.0, 11.0)
    fell = False
    for _ in range(int(2.5 / eng.DT)):
        faller.apply_movement(1.0, 0.0, eng.DT, arena)
        fell = faller.update_pit(eng.DT, arena) or fell
        if fell:
            break
    assert fell and faller.state == STATE_FALL and not faller.is_alive

    # Cada classe de vão com os lutadores certos (alcances reais)
    narrow, wide = arena.pits[0], arena.pits[3]
    assert narrow.gap_class == "L" and wide.gap_class == "J"
    assert not eng._crossing_result(eng.CHAR_MUSASHI, eng._roll, narrow, arena), "esquiva pesada não vence o L"
    assert eng._crossing_result(eng.CHAR_GRAY, eng._roll, narrow, arena), "esquiva ágil vence o L"
    assert not eng._crossing_result(eng.CHAR_GRAY, eng._roll, wide, arena), "esquiva ágil não vence o J"
    assert eng._crossing_result(eng.CHAR_NINJA, eng._jump, wide, arena), "salto do Hanzo vence o J"
    assert eng._crossing_result(eng.CHAR_KENSHIN, eng._roll, wide, arena), "Shukuchi do Kenshi vence o J"

    # Telhados de duas águas: sobem até a cumeeira, descem até a beirada e o beco fica no nível da beirada
    assert abs(arena.height_at(3.5, 10.0) - 1.1) < 1e-9 and abs(arena.height_at(10.5, 3.0) - 1.1) < 1e-9
    assert 0.0 < arena.height_at(0.5, 10.0) < 0.3 and arena.height_at(7.0, 10.0) == 0.0 and arena.height_at(6.0, 10.0) == 0.0
    flat_cam, sloped = Camera(11.0, 11.0), arena.attach_camera(Camera(11.0, 11.0))
    assert abs((flat_cam.apply(3.5, 10.0)[1] - sloped.apply(3.5, 10.0)[1]) - 1.1 * 32.0) <= 1, "tudo sobre o telhado sobe junto com ele"
    assert sloped.apply(7.0, 10.0) == flat_cam.apply(7.0, 10.0), "o beco e as vigas ficam no nível das beiradas"
    assert create_arena(ARENA_BAMBOO).attach_camera(Camera(11.0, 11.0)).height_fn is None
    for slope in arena.spec.slopes:
        assert not any(p.x0 < slope.ridge < p.x1 for p in arena.pits if p.gap_class in ("S", "M")), "rachadura não cruza a cumeeira"

    # Spawns em telhado firme, nunca em buraco nem colados nele
    for _ in range(120):
        a, b = arena.pick_spawns()
        assert math.dist(a, b) >= 7.0 - 1e-9
        for p in (a, b):
            assert arena.pit_edge_distance(*p) >= 1.1, "ninguém nasce em cima de uma viga estreita"
            assert not any(bld.check_collision(p[0], p[1], 0.9)[0] for bld in arena.buildings)

    # Renderiza nos três azimutes (vigas, becos e cumeeiras)
    for az in (0, 45, 135):
        random.seed(5)
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(arena.bg_color)
        camera = arena.attach_camera(Camera(11.0, 11.0))
        camera.set_azimuth(math.radians(az))
        arena.render_terrain(surf, camera, 1.0)
        for _, kind, obj in sorted(main.build_static_render_queue(arena), key=lambda i: camera.depth(*main.static_item_center(i[1], i[2]))):
            obj.render(surf, camera, 1.0) if kind in ("bamboo", "building", "lantern") else obj.render(surf, camera)
        assert pygame.transform.average_color(surf) != arena.bg_color

    # A IA atravessa pelas vigas até o rival do outro lado, sem cair
    random.seed(7)
    ai = SamuraiAI("hard")
    walker = eng._fighter_at(eng.CHAR_AMERICAN, 3.0, 11.0)
    target = eng._fighter_at(eng.CHAR_MUSASHI, 19.5, 12.0)
    particles, projectiles, banners = [], [], []
    reached = False
    for _ in range(int(60.0 / eng.DT)):
        ai.update(walker, target, eng.DT, arena, projectiles, [], [])
        eng.step_fighter(walker, target, eng.DT, arena, particles, projectiles, banners)
        projectiles.clear()
        if math.dist((walker.wx, walker.wy), (target.wx, target.wy)) < 3.0:
            reached = True
            break
    assert walker.is_alive and walker.state != STATE_FALL, "a IA não cai atravessando"
    assert reached, f"a IA deveria chegar ao outro telhado pelas vigas ({walker.wx:.1f}, {walker.wy:.1f})"

    # A IA não avança em golpe corrido sobre buraco aberto, mas aceita o protegido
    f = eng._fighter_at(eng.CHAR_SAITOU, 13.0, 11.0)
    assert SamuraiAI._lunge_clear(f, 18.0, 11.0, arena, 7.5) is False
    assert SamuraiAI._lunge_clear(f, 9.0, 11.0, arena, 3.8) is True
    print("  [OK] Telhados de Iga: becos L e J, vigas como rota sem salto, queda, alcances reais, spawns e IA.", flush=True)


def test_pirate_deck():
    from src.config import ARENA_PIRATE_DECK
    from src.combat.collision import CombatSystem
    from src.entities.ai_controller import SamuraiAI
    from src.entities.samurai import STATE_FALL
    from src.world.hazards import PHASE_ACTIVE, PHASE_WARN
    from src.world.solid_props import Cannon
    import tests.test_arena_engine as eng

    arena = create_arena(ARENA_PIRATE_DECK)
    assert arena.music == "bgm_pirate_deck" and arena.has_hazards and arena.has_rails
    assert sorted(p.gap_class for p in arena.pits) == ["L", "M", "S", "VOID", "VOID"]
    sea = [p for p in arena.pits if p.gap_class == "VOID"]
    assert len(sea) == 2 and all(p.railed for p in sea), "amurada: o mar é protegido por corda"
    assert all(p.water is not None for p in sea) and all(p.water is None for p in arena.pits if p.gap_class != "VOID")
    assert [type(h).__name__ for h in arena.hazards] == ["ShipRoll"]
    cannons = [c for c in arena.buildings if isinstance(c, Cannon)]
    assert len(cannons) == 2 and arena.interactives == cannons

    # Andar até a amurada é bloqueado; só o empurrão derruba no mar
    walker = eng._fighter_at(eng.CHAR_MUSASHI, 10.0, 12.0)
    for _ in range(int(4.0 / eng.DT)):
        walker.apply_movement(0.0, 1.0, eng.DT, arena)
        walker.update_pit(eng.DT, arena)
    assert walker.is_alive and walker.state != STATE_FALL and walker.wy < 18.0

    # Balanço do navio: aviso (tremor, banner, setas) sem empurrar, depois empurrão telegrafado até o mar
    for direction, y0 in ((1.0, 16.6), (-1.0, 5.4)):
        random.seed(4)
        arena = create_arena(ARENA_PIRATE_DECK)
        roll = arena.hazards[0]
        victim = eng._fighter_at(eng.CHAR_MUSASHI, 10.0, y0)
        camera = Camera(11.0, 11.0)
        banners, particles = [], []
        seen_warn, seen_active, pushed_in_warn, forced = False, False, False, False
        for _ in range(int(14.0 / eng.DT)):
            y_before = victim.wy
            arena.update(eng.DT, [victim], camera, particles, banners)
            if roll.phase == PHASE_WARN and not forced:
                roll.direction = direction  # sorteio do bordo fixado para o teste
                forced = True
            if roll.phase == PHASE_WARN:
                seen_warn = True
                pushed_in_warn = pushed_in_warn or abs(victim.wy - y_before) > 1e-9
                assert camera.shake_intensity > 0.0, "o aviso treme a tela"
            seen_active = seen_active or roll.phase == PHASE_ACTIVE
            eng.step_fighter(victim, None, eng.DT, arena, particles, [], banners)
            if victim.state == STATE_FALL:
                break
        assert seen_warn and seen_active and not pushed_in_warn and banners
        assert victim.state == STATE_FALL and not victim.is_alive, f"o balanço empurra para o mar (direção {direction})"
        assert arena.pit_at(victim.wx, victim.wy).gap_class == "VOID"
    arena = create_arena(ARENA_PIRATE_DECK)

    # Canhão: só um golpe ou projétil acende o pavio; dispara em linha, recarrega e só então acende de novo
    cannon = [c for c in arena.buildings if isinstance(c, Cannon)][0]
    far = eng._fighter_at(eng.CHAR_MUSASHI, 10.0, 12.0)
    assert cannon.ignite(10.0, 12.0, 0.5) is False and cannon.state == "idle"
    mx, my = cannon.muzzle
    in_line = eng._fighter_at(eng.CHAR_MUSASHI, mx + 4.0, my)
    off_line = eng._fighter_at(eng.CHAR_MUSASHI, mx + 4.0, my + 3.0)
    banners = []
    assert cannon.ignite(cannon.wx + cannon.width + 0.1, cannon.wy, 0.5) is True and cannon.state == "lit"
    assert cannon.ignite(cannon.wx, cannon.wy, 0.5) is False, "já aceso"
    shots = []
    for _ in range(int((cannon.FUSE_TIME + 0.2) / eng.DT)):
        cannon.tick(arena, eng.DT, [in_line, off_line], None, shots, banners)
        if cannon.state == "reload":
            break
    assert banners, "o pavio aceso mostra um banner"
    from src.effects.particles import CannonShotParticle
    ball = next((p for p in shots if isinstance(p, CannonShotParticle)), None)
    assert ball is not None, "o disparo cria uma bala visível"
    assert cannon.state == "reload" and cannon.recoil > 0.9 and in_line.is_alive, "a bala ainda está em voo"
    assert ball.update(0.0)
    start_x = cannon.wx
    for _ in range(int(1.0 / eng.DT)):
        cannon.tick(arena, eng.DT, [in_line, off_line], None, shots, [])
        ball.update(eng.DT)
        if not in_line.is_alive:
            break
    assert not in_line.is_alive and off_line.is_alive, "a bala mata quem cruza o corredor"
    for _ in range(int(1.0 / eng.DT)):
        cannon.tick(arena, eng.DT, [], None, [], [])
    assert cannon.recoil == 0.0 and cannon.shot_age is None
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    cam = Camera(11.0, 11.0)
    ball.age = 0.2
    ball.render(surf, cam)
    cannon.recoil = 1.0
    cannon.render(surf, cam, 0.0)
    assert cannon.wx == start_x, "o recuo é só visual"
    assert cannon.ignite(cannon.wx + cannon.width + 0.1, cannon.wy, 0.5) is False, "recarregando"
    for _ in range(int((cannon.RELOAD_TIME + 0.2) / eng.DT)):
        cannon.tick(arena, eng.DT, [], None, [], [])
    assert cannon.state == "idle" and cannon.ignite(cannon.wx + cannon.width + 0.1, cannon.wy, 0.5)

    # Golpes e projéteis em voo acendem o canhão pelo sistema de combate
    arena = create_arena(ARENA_PIRATE_DECK)
    cannon = [c for c in arena.buildings if isinstance(c, Cannon)][1]
    p1 = eng._fighter_at(eng.CHAR_MUSASHI, 10.0, 12.0)
    p2 = eng._fighter_at(eng.CHAR_KENSHIN, 12.0, 12.0)
    CombatSystem._check_interactives(p1, p2, arena, [])
    assert cannon.state == "idle", "sem golpe nada acende"
    p1.hitbox_active, p1.hitbox_center, p1.hitbox_radius = True, (cannon.wx - 0.2, cannon.wy + 0.4), 0.6
    CombatSystem._check_interactives(p1, p2, arena, [])
    assert cannon.state == "lit"
    cannon.state = "idle"
    p1.hitbox_active = False
    dart = type("Dart", (), {"wx": cannon.wx + 0.5, "wy": cannon.wy + 0.4, "dir_x": 1.0, "dir_y": 0.0, "is_active": True})()
    CombatSystem._check_interactives(p1, p2, arena, [dart])
    assert cannon.state == "lit"

    # Spawns longe das tábuas quebradas e do mar; renderiza nos três azimutes com o corredor de tiro aceso
    for _ in range(120):
        a, b = arena.pick_spawns()
        assert math.dist(a, b) >= 7.0 - 1e-9
        for p in (a, b):
            assert arena.pit_edge_distance(*p) >= 1.0
            assert not any(bld.check_collision(p[0], p[1], 0.9)[0] for bld in arena.buildings)
    for az in (0, 45, 135):
        random.seed(5)
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(arena.bg_color)
        camera = Camera(11.0, 11.0)
        camera.set_azimuth(math.radians(az))
        arena.hazards[0].phase = PHASE_WARN
        arena.render_terrain(surf, camera, 1.0)
        sea_px = camera.apply(11.0, 2.0, -sea[0].depth)  # fundo da lateral: água azulada, não vazio escuro
        block = pygame.transform.average_color(surf, pygame.Rect(sea_px[0] - 3, sea_px[1] - 3, 6, 6))
        if az == 0:  # nos outros azimutes a parede da frente esconde o fundo desse ponto
            assert block[2] > block[0] + 15 and block[2] > 50, f"água no fundo da lateral (azimute {az}): {block}"
        for _, kind, obj in sorted(main.build_static_render_queue(arena), key=lambda i: camera.depth(*main.static_item_center(i[1], i[2]))):
            obj.render(surf, camera, 1.0) if kind in ("bamboo", "building", "lantern") else obj.render(surf, camera)
        assert pygame.transform.average_color(surf) != arena.bg_color

    # IA: foge do bordo que vai adernar quando o empurrão levaria ao mar
    arena = create_arena(ARENA_PIRATE_DECK)
    roll = arena.hazards[0]
    roll.direction, roll.phase = 1.0, PHASE_WARN
    assert SamuraiAI._avoid_ship_roll(eng._fighter_at(eng.CHAR_MUSASHI, 10.0, 16.6), arena) is True
    assert SamuraiAI._avoid_ship_roll(eng._fighter_at(eng.CHAR_MUSASHI, 10.0, 11.0), arena) is False
    roll.phase = "idle"
    assert SamuraiAI._avoid_ship_roll(eng._fighter_at(eng.CHAR_MUSASHI, 10.0, 16.6), arena) is False

    # Som novo do ranger do navio
    from src.audio.procedural_sfx import _GENERATOR_MAP
    from src.audio.sound_events import SoundEvent
    assert SoundEvent.SHIP_CREAK in _GENERATOR_MAP and os.path.exists(os.path.join(ROOT, "assets", "sounds", "sfx", "ship_creak.wav"))
    print("  [OK] Convés na Tempestade: amurada, balanço telegrafado, canhão aceso por golpe ou projétil, spawns e IA.", flush=True)


def test_bamboo_kenshi_variant():
    """6.3.6: o Bambu ganha dojo sólido, karesansui e mais pétalas, com zonas liberadas de bambu."""
    from src.world.arenas import BAMBOO_SPEC, TILE_KARESANSUI
    from src.world.solid_props import SolidProp
    import tests.test_arena_engine as eng

    g = GameMap()
    dojo = next(b for b in g.buildings if isinstance(b, SolidProp) and b.style == "dojo")
    assert (dojo.wx, dojo.wy) == (0.6, 0.6) and dojo.height >= 1.5

    # Sem bambu dentro do dojo e do jardim (a floresta em volta continua densa)
    assert len(g.bamboos) > 150
    for sc in BAMBOO_SPEC.scatters:
        for x0, y0, x1, y1 in sc.cleared:
            assert not any(x0 <= b.wx <= x1 and y0 <= b.wy <= y1 for b in g.bamboos), "sem bambu no dojo e no jardim"

    # O dojo não pode ser atravessado nem usado para nascer; o jardim é cascalho rastelado com rochas
    assert dojo.check_collision(2.5, 2.5, 0.35)[0] and not dojo.check_collision(8.0, 8.0, 0.35)[0]
    walker = eng._fighter_at(eng.CHAR_MUSASHI, 3.0, 7.0)
    for _ in range(int(3.0 / eng.DT)):
        walker.apply_movement(0.0, -1.0, eng.DT, g)
    assert walker.wy >= dojo.wy + dojo.depth, f"o dojo bloqueia a passagem (y={walker.wy:.2f})"
    assert all(g.tiles[x][y] == TILE_KARESANSUI for x in range(1, 6) for y in range(5, 9))
    assert any(1.0 <= r.wx <= 6.0 and 5.0 <= r.wy <= 9.0 for r in g.rocks), "rochas zen no jardim"
    for _ in range(150):
        a, b = g.pick_spawns()
        assert not dojo.check_collision(a[0], a[1], 0.9)[0] and not dojo.check_collision(b[0], b[1], 0.9)[0]

    # Pétalas ao vento: a fração vem do spec; o convés não tem folhas
    from src.effects.particles import AmbientLeafParticle
    random.seed(1)
    share = sum(AmbientLeafParticle(22, 22, BAMBOO_SPEC.drift_petals).is_sakura for _ in range(2000)) / 2000.0
    assert 0.58 < share < 0.72 and BAMBOO_SPEC.drift_petals > 0.25
    assert create_arena("pirate_deck").spec.drift_count == 0 and BAMBOO_SPEC.drift_count == 45
    print("  [OK] Bambu de Kenshi: dojo sólido, karesansui, zonas sem bambu, pétalas.", flush=True)


def test_kyoto_saitou_variant():
    """6.3.6: Kyoto ganha o Shinsengumi (lanternas vermelhas, faixas do haori, banners, posto de guarda, incenso)."""
    from src.world.decor import Bunting, IncenseBurner, NoboriBanner, PaperLantern
    from src.world.kyoto_map import CarriageTraffic, DebrisRain
    from src.world.solid_props import SolidProp
    import tests.test_arena_engine as eng

    k = KyotoMap()
    kinds = lambda cls: [o for o in k.lanterns if isinstance(o, cls)]
    assert len(kinds(PaperLantern)) == 6 and len(kinds(Bunting)) == 3 and len(kinds(IncenseBurner)) == 2
    assert sorted(b.text for b in kinds(NoboriBanner)) == ["悪即斬", "悪即斬", "誠", "誠"]
    assert [type(h) for h in k.hazards] == [CarriageTraffic, DebrisRain], "carruagem e escombros seguem iguais"
    post = next(b for b in k.buildings if isinstance(b, SolidProp) and b.style == "guardpost")
    assert post.wx >= 13.0 and post.check_collision(post.wx + 0.5, post.wy + 0.5, 0.35)[0]
    assert not post.check_collision(10.5, post.wy + 0.7, 0.35)[0], "a rua continua livre"
    assert not any(isinstance(b, PaperLantern) and b.wx in (post.wx,) for b in kinds(PaperLantern))
    for _ in range(150):
        a, b = k.pick_spawns()
        assert not post.check_collision(a[0], a[1], 0.9)[0] and not post.check_collision(b[0], b[1], 0.9)[0]
    # Os postes não bloqueiam ninguém
    walker = eng._fighter_at(eng.CHAR_MUSASHI, 9.5, 5.75)
    for _ in range(int(1.0 / eng.DT)):
        walker.apply_movement(-1.0, 0.0, eng.DT, k)
    assert walker.wx < 8.0, "lanterna e faixa não têm colisão"

    # Incenso: os incensários soltam fumaça a cada frame de update, em vez de depender de um perigo
    assert len(k.emitters) == 2 and k.has_updates
    particles = []
    for _ in range(int(1.5 / eng.DT)):
        k.update(eng.DT, [], None, particles, [])
    assert len(particles) >= 8, "fumaça de incenso"
    assert not GameMap().has_updates

    # Os banners desenham o kanji de verdade (pixel claro sobre pano escuro) e ondulam com o tempo
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    cam = Camera(11.0, 11.0)
    banner = next(b for b in kinds(NoboriBanner) if b.text == "悪即斬")
    img = banner._image()
    assert img.get_height() > 3 * 30 and banner.cloth_length > 1.2 and pygame.mask.from_threshold(img, (244, 238, 224), (30, 30, 30)).count() > 300
    banner.render(surf, cam, 0.0)
    before = pygame.image.tobytes(surf, "RGB")
    surf.fill((0, 0, 0))
    banner.render(surf, cam, 1.3)
    assert pygame.image.tobytes(surf, "RGB") != before
    print("  [OK] Kyoto de Saitou: decoração do Shinsengumi, posto de guarda sólido, incenso, perigos intactos.", flush=True)


def test_shadow_cave():
    from src.config import ARENA_SHADOW_CAVE
    from src.entities.ai_controller import SamuraiAI
    from src.entities.projectile import KunaiProjectile
    from src.world.decor import JizoStatue
    from src.world.hazards import ChainPendulum, PHASE_ACTIVE, PHASE_WARN
    from src.world.solid_props import SolidProp
    import tests.test_arena_engine as eng

    arena = create_arena(ARENA_SHADOW_CAVE)
    assert arena.music == "bgm_shadow_cave" and arena.has_hazards and not arena.pits
    assert [type(h) for h in arena.hazards] == [ChainPendulum]
    jizos = [r for r in arena.rocks if isinstance(r, JizoStatue)]
    assert len(jizos) == 8 and len(arena.rocks) == 8, "as estátuas de Jizo são as únicas rochas"
    assert sum(1 for b in arena.buildings if isinstance(b, SolidProp) and b.style == "pillar") == 4

    # Jizo como cobertura: para projéteis e bloqueia quem anda
    jizo = min(jizos, key=lambda j: j.wx)  # a mais a oeste: nada entre ela e o ponto de tiro
    dart = KunaiProjectile(jizo.wx - 3.0, jizo.wy, 0.5, 1.0, 0.0, None)
    for _ in range(60):
        dart.update(eng.DT, arena, [])
        if dart.state != "FLYING":
            break
    assert dart.state == "ON_GROUND" and dart.wx < jizo.wx, f"a Jizo para o projétil (x={dart.wx:.2f})"
    walker = eng._fighter_at(eng.CHAR_MUSASHI, jizo.wx - 3.0, jizo.wy)
    for _ in range(int(2.0 / eng.DT)):
        walker.apply_movement(1.0, 0.0, eng.DT, arena)
    assert walker.wx < jizo.wx, "a Jizo bloqueia o caminho"
    for _ in range(100):
        a, b = arena.pick_spawns()
        assert math.dist(a, b) >= 7.0 - 1e-9
        assert not any(j.check_collision(p[0], p[1], 0.65)[0] for j in jizos for p in (a, b))

    # Pêndulo: aviso risca a faixa e não machuca; a varredura acerta uma vez quem está no meio, não quem pula ou está fora
    def run(placements, seed=3):
        random.seed(seed)
        arena = create_arena(ARENA_SHADOW_CAVE)
        pend = arena.hazards[0]
        fighters = [eng._fighter_at(eng.CHAR_MUSASHI, x, y) for x, y in placements]
        fighters[2].wz = 1.2  # em pleno salto (parado no ar só para o teste)
        banners, particles = [], []
        phases, forced, hp_in_warn = [], False, None
        for _ in range(int(16.0 / eng.DT)):
            arena.update(eng.DT, fighters, None, particles, banners)
            if pend.phase == PHASE_WARN and not forced:
                pend.lane, forced = 0, True  # faixa fixada no teste: y = 8.5, ao longo de x
            if pend.phase == PHASE_WARN:
                hp_in_warn = [f.hp for f in fighters]
            if not phases or phases[-1] != pend.phase:
                phases.append(pend.phase)
            if len(phases) >= 4:
                break
        return arena, pend, fighters, banners, phases, hp_in_warn

    arena, pend, fighters, banners, phases, hp_in_warn = run([(11.0, 8.5), (11.0, 12.0), (11.0, 8.5), (16.3, 8.5)])
    assert phases[:3] == ["idle", PHASE_WARN, PHASE_ACTIVE] and banners
    assert hp_in_warn == [3, 3, 3, 3], "o aviso não machuca ninguém"
    assert fighters[0].hp == 1, "quem fica no meio da faixa leva um golpe (e só um)"
    assert fighters[1].hp == 3, "fora da faixa fica a salvo"
    assert fighters[2].hp == 3, "pular por cima do peso evita o golpe"
    assert fighters[3].hp == 3, "a ponta da varredura, onde o peso está alto, não acerta"
    assert pend.danger_half_length < pend.amplitude and pend.weight_z(0.0) < 0.5 and pend.weight_z(pend.amplitude) > 3.0

    # Telégrafo no chão: a zona de perigo aparece em magenta e o peso desce pela corrente em ordem de render
    random.seed(1)
    arena = create_arena(ARENA_SHADOW_CAVE)
    pend = arena.hazards[0]
    pend.phase, pend.lane, pend.timer = PHASE_WARN, 0, 1.0
    for az in (0, 45, 135):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(arena.bg_color)
        camera = arena.attach_camera(Camera(11.0, 11.0))
        camera.set_azimuth(math.radians(az))
        arena.render_terrain(surf, camera, 0.0)
        px = camera.apply(11.0, 8.5, 0.04)
        r, g, b, _ = surf.get_at(px)
        assert r > g + 40, f"zona de perigo visível no azimute {az}: {(r, g, b)}"
        for _, kind, obj in sorted(main.build_static_render_queue(arena), key=lambda i: camera.depth(*main.static_item_center(i[1], i[2]))):
            obj.render(surf, camera, 1.0) if kind in ("bamboo", "building", "lantern") else obj.render(surf, camera)
        arena.render_overhead(surf, camera, 0.0)
        pend.phase, pend.elapsed = PHASE_ACTIVE, 0.85
        arena.render_overhead(surf, camera, 0.0)
        pend.phase = PHASE_WARN

    # A IA sai da faixa avisada pelo lado mais curto e ignora o pêndulo quando ele está parado
    pend.phase, pend.lane = PHASE_WARN, 0
    escape = SamuraiAI._avoid_pendulum(eng._fighter_at(eng.CHAR_MUSASHI, 11.0, 8.9), arena)
    assert escape is not None and escape[1] > 0.9 and abs(escape[0]) < 0.1
    escape = SamuraiAI._avoid_pendulum(eng._fighter_at(eng.CHAR_MUSASHI, 11.0, 8.1), arena)
    assert escape is not None and escape[1] < -0.9
    assert SamuraiAI._avoid_pendulum(eng._fighter_at(eng.CHAR_MUSASHI, 11.0, 12.5), arena) is None
    pend.phase = "idle"
    assert SamuraiAI._avoid_pendulum(eng._fighter_at(eng.CHAR_MUSASHI, 11.0, 8.5), arena) is None

    from src.audio.procedural_sfx import _GENERATOR_MAP
    from src.audio.sound_events import SoundEvent
    assert SoundEvent.CHAIN_RATTLE in _GENERATOR_MAP and os.path.exists(os.path.join(ROOT, "assets", "sounds", "sfx", "chain_rattle.wav"))
    print("  [OK] Gruta das Sombras: Jizo como cobertura, pêndulo telegrafado, golpe único, salto, IA e render.", flush=True)


def test_mist_temple():
    from src.config import ARENA_MIST_TEMPLE
    from src.entities.ai_controller import SamuraiAI
    from src.world.decor import PineTree
    from src.world.hazards import FireworkMortars, PHASE_ACTIVE, PHASE_WARN
    import tests.test_arena_engine as eng

    arena = create_arena(ARENA_MIST_TEMPLE)
    assert arena.music == "bgm_mist_temple" and arena.has_hazards and not arena.pits
    assert [type(h) for h in arena.hazards] == [FireworkMortars]
    assert len(arena.trees) == 4 and all(isinstance(t_, PineTree) for t_ in arena.trees)

    # Lagoa rasa: lenta e sem queda; spawns nunca nascem na água
    assert arena.is_water(6.5, 13.5) and arena.speed_mult_at(6.5, 13.5) == 0.6 and arena.speed_mult_at(11.0, 8.0) == 1.0
    for _ in range(100):
        a, b = arena.pick_spawns()
        assert not arena.is_water(*a) and not arena.is_water(*b) and math.dist(a, b) >= 7.0 - 1e-9

    # Morteiros: aviso com círculos (os primeiros miram os lutadores) sem dano; a explosão atinge quem ficou
    def run(stay_inside_second: bool, seed: int = 5):
        random.seed(seed)
        arena = create_arena(ARENA_MIST_TEMPLE)
        mortars = arena.hazards[0]
        p1 = eng._fighter_at(eng.CHAR_MUSASHI, 11.0, 8.0)
        p2 = eng._fighter_at(eng.CHAR_MUSASHI, 14.0, 15.0)
        banners, particles = [], []
        hp_warn, circles_seen, moved = None, None, False
        for _ in range(int(14.0 / eng.DT)):
            arena.update(eng.DT, [p1, p2], None, particles, banners)
            if mortars.phase == PHASE_WARN:
                circles_seen = list(mortars.circles)
                hp_warn = (p1.hp, p2.hp)
                if not stay_inside_second and not moved:
                    p2.wx, p2.wy, moved = 4.0, 18.0, True  # sai do alcance durante o aviso
            if mortars.phase == PHASE_ACTIVE and mortars.elapsed > 0.1:
                break
        return arena, mortars, p1, p2, banners, hp_warn, circles_seen, particles

    arena, mortars, p1, p2, banners, hp_warn, circles, particles = run(True)
    assert len(circles) == 3 and banners and hp_warn == (3, 3), "aviso sem dano"
    starts = ((11.0, 8.0), (14.0, 15.0))
    assert any(math.dist(circles[0][:2], st) < 1.3 for st in starts), "o primeiro círculo mira um lutador"
    assert all(math.dist(a[:2], b[:2]) > 1.5 * 1.5 for i, a in enumerate(circles) for b in circles[i + 1:]), "círculos separados"
    assert particles, "a explosão solta faíscas"
    assert min(p1.hp, p2.hp) == 1, "quem ficou no círculo leva o golpe (dano 2)"
    arena2, mortars2, q1, q2, _, _, circles2, _ = run(False)
    assert q2.hp == 3, "quem saiu do círculo no aviso não é atingido"

    # Render: anel laranja no aviso e projétil luminoso descendo; IA foge dos círculos
    random.seed(1)
    arena = create_arena(ARENA_MIST_TEMPLE)
    mortars = arena.hazards[0]
    mortars.phase, mortars.timer, mortars.circles = PHASE_WARN, 0.3, [(9.0, 9.0, 1.5)]
    for az in (0, 45, 135):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(arena.bg_color)
        camera = arena.attach_camera(Camera(11.0, 11.0))
        camera.set_azimuth(math.radians(az))
        arena.render_terrain(surf, camera, 0.0)
        ring = camera.apply(9.0 + 1.5, 9.0, 0.03)
        found = max(surf.get_at((ring[0] + dx, ring[1] + dy))[0] - surf.get_at((ring[0] + dx, ring[1] + dy))[2]
                    for dx in range(-3, 4) for dy in range(-3, 4))
        assert found > 40, f"anel de aviso visível no azimute {az}"
        for _, kind, obj in sorted(main.build_static_render_queue(arena), key=lambda i: camera.depth(*main.static_item_center(i[1], i[2]))):
            obj.render(surf, camera, 1.0) if kind in ("bamboo", "building", "lantern") else obj.render(surf, camera)
        arena.render_overhead(surf, camera, 0.0)
    mortars.phase = PHASE_ACTIVE  # no primeiro instante da explosão a cor do anel passava de 255 e o jogo caía
    for elapsed in (0.0, 0.2, 0.5):
        mortars.elapsed = elapsed
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        arena.render_terrain(surf, arena.attach_camera(Camera(11.0, 11.0)), 0.0)
    mortars.phase = PHASE_WARN
    escape = SamuraiAI._avoid_circles(eng._fighter_at(eng.CHAR_MUSASHI, 9.5, 9.0), arena)
    assert escape is not None and escape[0] > 0.9
    assert SamuraiAI._avoid_circles(eng._fighter_at(eng.CHAR_MUSASHI, 15.0, 15.0), arena) is None
    mortars.phase = "idle"
    assert SamuraiAI._avoid_circles(eng._fighter_at(eng.CHAR_MUSASHI, 9.5, 9.0), arena) is None
    print("  [OK] Templo na Névoa: lagoa lenta, círculos de morteiro avisados, explosão e fuga da IA.", flush=True)


def test_forest_camp():
    from src.config import ARENA_FOREST_CAMP
    from src.entities.ai_controller import SamuraiAI
    from src.entities.projectile import KunaiProjectile
    from src.entities.samurai import STATE_STUNNED
    from src.world.decor import SnareTrap, SupplyCrate
    import tests.test_arena_engine as eng

    arena = create_arena(ARENA_FOREST_CAMP)
    assert arena.music == "bgm_forest_camp" and not arena.pits and not arena.hazards
    assert sum(arena.bg_color) / 3 > 110, "única arena diurna: céu claro"
    traps = [e for e in arena.emitters if isinstance(e, SnareTrap)]
    crates = [r for r in arena.rocks if isinstance(r, SupplyCrate)]
    assert len(traps) == 6 and len(crates) == 6 and len(arena.rocks) == 6 and arena.has_updates

    # Caixote como cobertura: para projétil e bloqueia
    crate = min(crates, key=lambda c: c.wx)
    dart = KunaiProjectile(crate.wx - 3.0, crate.wy, 0.5, 1.0, 0.0, None)
    for _ in range(60):
        dart.update(eng.DT, arena, [])
        if dart.state != "FLYING":
            break
    assert dart.state == "ON_GROUND" and dart.wx < crate.wx

    # Armadilha: atordoa sem ferir, ignora quem salta, rearma; dispara uma vez por pisada
    trap = traps[0]
    walker = eng._fighter_at(eng.CHAR_MUSASHI, trap.wx - 0.1, trap.wy)
    jumper = eng._fighter_at(eng.CHAR_MUSASHI, trap.wx + 0.1, trap.wy)
    jumper.wz = 0.6
    banners, particles = [], []
    arena.update(eng.DT, [jumper], None, particles, banners)
    assert trap.armed and jumper.state != STATE_STUNNED, "quem está no ar não dispara"
    arena.update(eng.DT, [walker], None, particles, banners)
    assert not trap.armed and walker.state == STATE_STUNNED and walker.hp == 3 and walker.is_alive, "atordoa sem ferir"
    assert banners
    for _ in range(int((trap.REARM - 0.5) / eng.DT)):
        arena.update(eng.DT, [], None, [], [])
    assert not trap.armed, "ainda recarregando"
    for _ in range(int(1.0 / eng.DT)):
        arena.update(eng.DT, [], None, [], [])
    assert trap.armed, "rearmou"

    # Nascer: longe das armadilhas e das caixas; IA se afasta delas sem anular a perseguição
    for _ in range(150):
        a, b = arena.pick_spawns()
        assert math.dist(a, b) >= 7.0 - 1e-9
        for p in (a, b):
            assert all(math.dist(p, (t_.wx, t_.wy)) >= t_.spawn_clearance for t_ in traps)
            assert not any(c.check_collision(p[0], p[1], 0.65)[0] for c in crates)
    near = eng._fighter_at(eng.CHAR_MUSASHI, trap.wx - 0.9, trap.wy)
    repel = SamuraiAI._avoid_traps(near, arena)
    assert repel is not None and repel[0] < 0
    assert SamuraiAI._avoid_traps(eng._fighter_at(eng.CHAR_MUSASHI, 3.0, 12.0), arena) is None
    trap.armed = False
    assert SamuraiAI._avoid_traps(near, arena) is None

    # Fogueira solta fumaça; renderiza em três azimutes
    particles = []
    for _ in range(int(1.0 / eng.DT)):
        arena.update(eng.DT, [], None, particles, [])
    assert len(particles) >= 5
    for az in (0, 45, 135):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(arena.bg_color)
        camera = arena.attach_camera(Camera(11.0, 11.0))
        camera.set_azimuth(math.radians(az))
        arena.render_terrain(surf, camera, 0.0)
        for _, kind, obj in sorted(main.build_static_render_queue(arena), key=lambda i: camera.depth(*main.static_item_center(i[1], i[2]))):
            obj.render(surf, camera, 1.0) if kind in ("bamboo", "building", "lantern") else obj.render(surf, camera)
    print("  [OK] Acampamento na Floresta: dia, armadilhas que atordoam e rearmam, caixas como cobertura, spawns e IA.", flush=True)


def test_nagashino_field():
    from src.combat.collision import CombatSystem
    from src.config import ARENA_NAGASHINO
    from src.entities.ai_controller import SamuraiAI
    from src.world.solid_props import PowderBarrel, SolidProp
    import tests.test_arena_engine as eng

    arena = create_arena(ARENA_NAGASHINO)
    barrels = [b for b in arena.interactives if isinstance(b, PowderBarrel)]
    assert arena.music == "bgm_nagashino_field" and len(barrels) == 7 and arena.has_updates and not arena.pits
    palisades = [b for b in arena.buildings if isinstance(b, SolidProp) and b.style == "palisade"]
    assert len(palisades) == 6 and palisades[0].check_collision(palisades[0].wx + 1.0, palisades[0].wy + 0.2, 0.3)[0]
    assert arena.speed_mult_at(5.5, 11.0) == 0.6 and not arena.is_water(5.5, 11.0) and arena.speed_mult_at(11.0, 9.0) == 1.0

    # Acender com golpe, projétil ou bomba: pavio visível, círculo de perigo e explosão que mata só quem está no raio
    def fresh():
        random.seed(2)
        a = create_arena(ARENA_NAGASHINO)
        return a, [b for b in a.interactives if isinstance(b, PowderBarrel)]

    arena, barrels = fresh()
    first, second, far = barrels[0], barrels[1], barrels[3]
    fx, fy = first.center
    victim = eng._fighter_at(eng.CHAR_MUSASHI, fx - 1.5, fy)
    safe = eng._fighter_at(eng.CHAR_MUSASHI, fx + 5.0, fy + 5.0)
    p1 = eng._fighter_at(eng.CHAR_KENSHIN, fx, fy + 3.0)
    p1.hitbox_active, p1.hitbox_center, p1.hitbox_radius = True, (first.wx + 0.4, first.wy - 0.2), 0.6
    CombatSystem._check_interactives(p1, safe, arena, [])
    assert first.state == "lit" and first.danger_circle()[2] == first.BLAST_RADIUS and second.state == "idle"
    banners, particles = [], []
    for _ in range(int((first.FUSE_TIME - 0.2) / eng.DT)):
        arena.update(eng.DT, [victim, safe], None, particles, banners)
    assert victim.hp == 3 and first.state == "lit" and banners, "o pavio ainda queima: sem dano"
    assert SamuraiAI._avoid_circles(victim, arena) is not None, "a IA foge do círculo do barril aceso"
    for _ in range(int(0.4 / eng.DT)):
        arena.update(eng.DT, [victim, safe], None, particles, banners)
    assert first.state == "spent" and not victim.is_alive and safe.is_alive, "explosão mata só quem está no raio"
    assert not first.check_collision(fx, fy, 0.3)[0], "a cratera não bloqueia"
    for _ in range(int(0.8 / eng.DT)):
        arena.update(eng.DT, [safe], None, particles, banners)
    assert second.state == "spent", "o barril vizinho explode em cadeia"
    assert far.state == "idle", "o barril distante não é atingido"

    # Projétil em voo também acende; quem pula por cima da explosão sobrevive
    arena, barrels = fresh()
    dart = type("Dart", (), {"wx": barrels[4].center[0], "wy": barrels[4].center[1], "dir_x": 1.0, "dir_y": 0.0, "is_active": True})()
    p1.hitbox_active = False
    CombatSystem._check_interactives(p1, safe, arena, [dart])
    assert barrels[4].state == "lit"
    jumper = eng._fighter_at(eng.CHAR_NINJA, barrels[4].center[0] + 1.0, barrels[4].center[1])
    jumper.wz = 1.6
    for _ in range(int(2.0 / eng.DT)):
        arena.update(eng.DT, [jumper], None, [], [])
    assert jumper.is_alive and barrels[4].state == "spent"

    # Spawns longe de paliçadas e barris; renderiza (aceso e gasto) em três azimutes
    arena, barrels = fresh()
    for _ in range(120):
        a, b = arena.pick_spawns()
        assert math.dist(a, b) >= 7.0 - 1e-9
        assert not any(o.check_collision(p[0], p[1], 0.9)[0] for o in arena.buildings for p in (a, b))
    barrels[0].state, barrels[0].timer = "lit", 0.5
    barrels[1].state, barrels[1].flash = "spent", 0.3
    for az in (0, 45, 135):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(arena.bg_color)
        camera = arena.attach_camera(Camera(11.0, 11.0))
        camera.set_azimuth(math.radians(az))
        arena.render_terrain(surf, camera, 0.0)
        for _, kind, obj in sorted(main.build_static_render_queue(arena), key=lambda i: camera.depth(*main.static_item_center(i[1], i[2]))):
            obj.render(surf, camera, 1.0) if kind in ("bamboo", "building", "lantern") else obj.render(surf, camera)
    print("  [OK] Campo de Nagashino: barris de pólvora (golpe/projétil, pavio, explosão e cadeia), paliçadas, lama e IA.", flush=True)


def test_kabuki_stage():
    from src.config import ARENA_KABUKI_STAGE
    from src.entities.projectile import KunaiProjectile
    from src.world.decor import ScreenPanel, StripedCurtain
    from src.world.hazards import PHASE_ACTIVE, PHASE_WARN, RotatingStage
    import tests.test_arena_engine as eng

    arena = create_arena(ARENA_KABUKI_STAGE)
    assert arena.music == "bgm_kabuki_stage" and arena.has_hazards and not arena.pits
    assert [type(h) for h in arena.hazards] == [RotatingStage]
    panels = [r for r in arena.rocks if isinstance(r, ScreenPanel)]
    assert len(panels) == 9 and len(arena.rocks) == 9, "três biombos de três painéis"
    assert any(isinstance(o, StripedCurtain) for o in arena.lanterns)
    from src.world.arenas import TILE_HANAMICHI, TILE_KABUKI_DISC
    assert arena.tiles[3][10] == TILE_HANAMICHI and arena.tiles[10][10] == TILE_KABUKI_DISC, "passarela hanamichi e disco central"
    walker = eng._fighter_at(eng.CHAR_MUSASHI, 1.0, 10.9)
    for _ in range(int(2.0 / eng.DT)):
        walker.apply_movement(1.0, 0.0, eng.DT, arena)
    assert walker.wx > 5.0, "a hanamichi é passagem livre"

    # Biombo como cobertura: para projétil e bloqueia
    panel = panels[0]
    dart = KunaiProjectile(panel.wx, panel.wy - 3.0, 0.5, 0.0, 1.0, None)
    for _ in range(60):
        dart.update(eng.DT, arena, [])
        if dart.state != "FLYING":
            break
    assert dart.state == "ON_GROUND" and dart.wy < panel.wy

    # Giro: o aviso não move ninguém; na fase ativa quem está no disco gira junto, sem dano; fora e no ar não gira
    random.seed(6)
    arena = create_arena(ARENA_KABUKI_STAGE)
    stage = arena.hazards[0]
    on_disc = eng._fighter_at(eng.CHAR_MUSASHI, 14.0, 11.0)
    centre = eng._fighter_at(eng.CHAR_MUSASHI, 11.0, 11.0)
    outside = eng._fighter_at(eng.CHAR_MUSASHI, 17.0, 11.0)
    airborne = eng._fighter_at(eng.CHAR_MUSASHI, 12.5, 12.5)
    airborne.wz = 1.0
    fighters = [on_disc, centre, outside, airborne]
    start = [(f.wx, f.wy) for f in fighters]
    banners, particles = [], []
    in_warn, forced = None, False
    for _ in range(int(20.0 / eng.DT)):
        arena.update(eng.DT, fighters, None, particles, banners)
        if stage.phase == PHASE_WARN:
            in_warn = [(f.wx, f.wy) for f in fighters]
            if not forced:
                stage.direction, forced = 1.0, True
        if stage.phase == PHASE_ACTIVE and stage.elapsed > stage.active_time - 0.05:
            break
    assert in_warn == start and banners, "o aviso não move ninguém"
    ang0 = math.atan2(start[0][1] - 11.0, start[0][0] - 11.0)
    ang1 = math.atan2(on_disc.wy - 11.0, on_disc.wx - 11.0)
    turned = (ang1 - ang0 + math.pi) % (2 * math.pi) - math.pi
    assert abs(math.hypot(on_disc.wx - 11.0, on_disc.wy - 11.0) - 3.0) < 0.15, "gira em círculo, mantendo o raio"
    assert 1.2 < abs(turned) < 2.6 and on_disc.hp == 3 and on_disc.is_alive, f"o disco arrasta sem ferir (giro {turned:.2f} rad)"
    assert (centre.wx, centre.wy) == start[1] and (outside.wx, outside.wy) == start[2] and (airborne.wx, airborne.wy) == start[3]

    # Disco desenhado nos três azimutes, com os raios girando entre dois instantes
    stage.phase, stage.direction = PHASE_WARN, 1.0
    shots = []
    for az in (0, 45, 135):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(arena.bg_color)
        camera = arena.attach_camera(Camera(11.0, 11.0))
        camera.set_azimuth(math.radians(az))
        arena.render_terrain(surf, camera, 0.0)
        rim = camera.apply(11.0 + 4.3, 11.0, 0.03)
        found = max(surf.get_at((rim[0] + dx, rim[1] + dy))[0] - surf.get_at((rim[0] + dx, rim[1] + dy))[2] for dx in range(-3, 4) for dy in range(-3, 4))
        assert found > 40, f"aro do disco visível no azimute {az}"
        for _, kind, obj in sorted(main.build_static_render_queue(arena), key=lambda i: camera.depth(*main.static_item_center(i[1], i[2]))):
            obj.render(surf, camera, 1.0) if kind in ("bamboo", "building", "lantern") else obj.render(surf, camera)
        shots.append(pygame.image.tobytes(surf, "RGB"))
    stage.angle += 0.3
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill(arena.bg_color)
    camera = arena.attach_camera(Camera(11.0, 11.0))
    arena.render_terrain(surf, camera, 0.0)
    assert pygame.image.tobytes(surf, "RGB") != shots[0], "os raios acompanham o giro"
    # regressão: o palco tem `direction` mas não empurra; a IA não pode quebrar ao checar balanço de navio
    from src.entities.ai_controller import SamuraiAI
    stage.phase = PHASE_ACTIVE
    assert SamuraiAI._avoid_ship_roll(eng._fighter_at(eng.CHAR_MUSASHI, 11.0, 11.0), arena) is False
    print("  [OK] Palco Kabuki: disco giratório (aviso, giro sem dano), hanamichi, biombos como cobertura e render.", flush=True)


def test_mountain_shrine():
    from src.combat.collision import CombatSystem
    from src.config import ARENA_MOUNTAIN_SHRINE
    from src.entities.projectile import KunaiProjectile
    from src.world.decor import ArcheryTarget
    from src.world.solid_props import ShrineBell
    import tests.test_arena_engine as eng

    arena = create_arena(ARENA_MOUNTAIN_SHRINE)
    assert arena.music == "bgm_mountain_shrine" and arena.hazards == [] and not arena.pits, "sem perigos"
    assert len(arena.torii_gates) == 5, "torii em sequência"
    targets = [r for r in arena.rocks if isinstance(r, ArcheryTarget)]
    assert len(targets) == 3
    bells = [b for b in arena.interactives if isinstance(b, ShrineBell)]
    assert len(bells) == 1 and arena.has_updates
    bell = bells[0]

    # Sino: golpe ou projétil faz soar e pede a dissipação; pausa entre toques; main apaga fumaça e veneno
    p1 = eng._fighter_at(eng.CHAR_NINJA, 8.0, 6.2)
    p2 = eng._fighter_at(eng.CHAR_MUSASHI, 12.0, 14.0)
    CombatSystem._check_interactives(p1, p2, arena, [])
    assert bell.cooldown == 0.0 and not arena.dispel_requested, "sem golpe o sino fica calado"
    p1.hitbox_active, p1.hitbox_center, p1.hitbox_radius = True, (bell.wx - 0.2, bell.wy + 0.8), 0.6
    CombatSystem._check_interactives(p1, p2, arena, [])
    banners, particles = [], []
    arena.update(eng.DT, [p1, p2], None, particles, banners)
    assert arena.dispel_requested and banners and bell.ring > 0 and bell.cooldown > 1.5
    arena.dispel_requested = False
    CombatSystem._check_interactives(p1, p2, arena, [])
    arena.update(eng.DT, [p1, p2], None, [], [])
    assert not arena.dispel_requested, "o sino ainda está na pausa"
    for _ in range(int(2.2 / eng.DT)):
        arena.update(eng.DT, [], None, [], [])
    p1.hitbox_active = False
    dart = type("Dart", (), {"wx": bell.wx + 0.3, "wy": bell.wy + 0.4, "dir_x": 1.0, "dir_y": 0.0, "is_active": True})()
    CombatSystem._check_interactives(p1, p2, arena, [dart])
    arena.update(eng.DT, [], None, [], [])
    assert arena.dispel_requested, "projétil também toca o sino"
    with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as fh:
        src = fh.read()
    assert "game_map.dispel_requested" in src and "SmokeCloudEntity" in src and "poison_clouds.clear()" in src

    # Alvo como cobertura; passagem pelos torii; spawns; render
    target = targets[0]
    dart = KunaiProjectile(target.wx, target.wy + 3.0, 0.5, 0.0, -1.0, None)
    for _ in range(60):
        dart.update(eng.DT, arena, [])
        if dart.state != "FLYING":
            break
    assert dart.state == "ON_GROUND" and dart.wy > target.wy
    walker = eng._fighter_at(eng.CHAR_MUSASHI, 10.5, 20.0)
    for _ in range(int(4.0 / eng.DT)):
        walker.apply_movement(0.0, -1.0, eng.DT, arena)
    assert walker.wy < 8.0, f"o caminho dos torii é livre (y={walker.wy:.2f})"
    for _ in range(120):
        a, b = arena.pick_spawns()
        assert math.dist(a, b) >= 7.0 - 1e-9
        assert not any(o.check_collision(p[0], p[1], 0.9)[0] for o in arena.buildings for p in (a, b))
    for az in (0, 45, 135):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(arena.bg_color)
        camera = arena.attach_camera(Camera(11.0, 11.0))
        camera.set_azimuth(math.radians(az))
        arena.render_terrain(surf, camera, 0.0)
        bell.ring = 1.0
        for _, kind, obj in sorted(main.build_static_render_queue(arena), key=lambda i: camera.depth(*main.static_item_center(i[1], i[2]))):
            obj.render(surf, camera, 1.0) if kind in ("bamboo", "building", "lantern") else obj.render(surf, camera)
    print("  [OK] Santuário na Montanha: sem perigos, sino que dissipa fumaça e veneno, alvos como cobertura, torii livres.", flush=True)


def test_baroque_court():
    from src.config import ARENA_BAROQUE_COURT
    from src.entities.projectile import KunaiProjectile
    from src.world.arenas import TILE_MARBLE_DARK, TILE_MARBLE_LIGHT
    from src.world.decor import Fountain, HedgeBlock, MarbleStatue, NoboriBanner
    import tests.test_arena_engine as eng

    arena = create_arena(ARENA_BAROQUE_COURT)
    assert arena.music == "bgm_baroque_court" and arena.hazards == [] and not arena.pits and not arena.has_hazards, "sem perigos"
    hedges = [r for r in arena.rocks if isinstance(r, HedgeBlock)]
    statues = [r for r in arena.rocks if isinstance(r, MarbleStatue)]
    fountains = [r for r in arena.rocks if isinstance(r, Fountain)]
    assert len(hedges) == 16 and len(statues) == 6 and len(fountains) == 1 and len(arena.rocks) == 23
    assert {arena.tiles[x][y] for x in (2, 3) for y in (2, 3)} == {TILE_MARBLE_LIGHT, TILE_MARBLE_DARK}, "mármore xadrez"

    # Fonte: água lenta em volta e fonte sólida no centro
    assert arena.is_water(8.8, 11.0) and arena.speed_mult_at(8.8, 11.0) == 0.6 and arena.speed_mult_at(4.0, 11.0) == 1.0
    walker = eng._fighter_at(eng.CHAR_MUSASHI, 7.5, 11.0)
    for _ in range(int(3.0 / eng.DT)):
        walker.apply_movement(1.0, 0.0, eng.DT, arena)
    assert walker.wx < fountains[0].wx - 0.9, "a fonte bloqueia o centro"

    # Sebes e estátuas param projéteis e bloqueiam
    for cover in (min(hedges, key=lambda h: h.wx), statues[0]):
        dart = KunaiProjectile(cover.wx - 3.0, cover.wy, 0.5, 1.0, 0.0, None)
        for _ in range(60):
            dart.update(eng.DT, arena, [])
            if dart.state != "FLYING":
                break
        assert dart.state == "ON_GROUND" and dart.wx < cover.wx, type(cover).__name__
    for _ in range(120):
        a, b = arena.pick_spawns()
        assert math.dist(a, b) >= 7.0 - 1e-9
        assert not arena.is_water(*a) and not arena.is_water(*b)
        assert not any(r.check_collision(p[0], p[1], 0.65)[0] for r in arena.rocks for p in (a, b))

    # Estandartes com flor-de-lis desenhada (sem texto) e render em três azimutes (fonte animada)
    banner = next(o for o in arena.lanterns if isinstance(o, NoboriBanner))
    img = banner._image()
    assert banner.emblem == "fleur" and pygame.mask.from_threshold(img, (238, 204, 90), (20, 20, 20)).count() > 250
    frames = []
    for az in (0, 45, 135):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(arena.bg_color)
        camera = arena.attach_camera(Camera(11.0, 11.0))
        camera.set_azimuth(math.radians(az))
        arena.render_terrain(surf, camera, 0.0)
        for _, kind, obj in sorted(main.build_static_render_queue(arena), key=lambda i: camera.depth(*main.static_item_center(i[1], i[2]))):
            if getattr(obj, "animated", False):
                obj.render(surf, camera, 0.0)
            else:
                obj.render(surf, camera, 1.0) if kind in ("bamboo", "building", "lantern") else obj.render(surf, camera)
        frames.append(pygame.image.tobytes(surf, "RGB"))
    f1, f2 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)), pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    cam = Camera(11.0, 11.0)
    fountains[0].render(f1, cam, 0.0)
    fountains[0].render(f2, cam, 0.6)
    assert pygame.image.tobytes(f1, "RGB") != pygame.image.tobytes(f2, "RGB"), "a fonte anima"
    print("  [OK] Pátio Barroco: sem perigos, mármore xadrez, fonte e água lenta, sebes e estátuas como cobertura, estandartes.", flush=True)


def test_all_12_character_arenas_generate():
    """Fechamento do 6.3: as 12 arenas geram, renderizam em três azimutes e têm spawns, música e textos válidos."""
    from src.audio.sound_manager import MUSIC_DIR
    from src.roster import ARENA_ORDER, FIGHTER_BY_ARENA
    from src.world.arenas import ARENA_SPECS

    assert len(ARENA_ORDER) == 12 and set(arena_ids()) == set(ARENA_ORDER), "as 12 arenas do elenco estão registradas"
    assert len(FIGHTER_BY_ARENA) == 12
    for arena_id in ARENA_ORDER:
        arena = create_arena(arena_id)
        spec = ARENA_SPECS[arena_id]
        assert os.path.exists(os.path.join(MUSIC_DIR, f"{spec.music}.mp3")), f"{arena_id}: música {spec.music}"
        shots = []
        for az in (0, 45, 135):
            shots.append(render_frame(arena, az))
        assert _mean_abs_diff(shots[0], shots[1]) > 0.5 and _mean_abs_diff(shots[0], shots[2]) > 0.5, f"{arena_id}: azimutes iguais"
        solids = list(arena.rocks) + list(arena.buildings)
        for _ in range(60):
            a, b = arena.pick_spawns()
            assert math.dist(a, b) >= 6.99, arena_id
            for point in (a, b):
                assert arena.pit_at(*point) is None, f"{arena_id}: spawn em buraco"
                assert not any(r.check_collision(point[0], point[1], 0.5)[0] for r in solids), f"{arena_id}: spawn em sólido"
        assert arena.intro_stage_point() is not None
    print("  [OK] As 12 arenas geram, renderizam em 0/45/135, têm spawns válidos e música (textos PT/EN em test_selection_screens).", flush=True)


def test_parametrized_arena_creation():
    print("=== TESTE 6.2: Gerador de Arenas Parametrizado ===", flush=True)
    test_registry_and_creation()
    test_bamboo_layout_matches_legacy()
    test_kyoto_layout()
    test_visual_parity_with_reference_images()
    test_synthetic_arena_is_generic()
    test_validate_spec_rejects_invalid_specs()
    test_build_rejects_stage_or_spawn_in_water_or_obstacle()
    test_spawn_rules_per_arena()
    test_kyoto_hazards_driven_by_spec()
    test_lighting_is_data_only()
    test_main_has_no_per_arena_branches()
    test_ganryu_island()
    test_iga_rooftops()
    test_pirate_deck()
    test_bamboo_kenshi_variant()
    test_kyoto_saitou_variant()
    test_shadow_cave()
    test_mist_temple()
    test_forest_camp()
    test_nagashino_field()
    test_kabuki_stage()
    test_mountain_shrine()
    test_baroque_court()
    test_all_12_character_arenas_generate()
    print("=== TESTE 6.2 CONCLUÍDO ===", flush=True)


if __name__ == "__main__":
    test_parametrized_arena_creation()
