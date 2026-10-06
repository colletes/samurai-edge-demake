"""
Teste da Fase 6 - Entregável 6.3.1: motor de arenas temáticas.

Valida, com uma arena sintética de teste (não registrada), que:
1. Buracos (`PitZone`) são validados por classe de largura (S, M, L, J, VOID) e `derive_spec` valida variantes.
2. Andar é bloqueado na borda do buraco; esquiva, salto e avanço atravessam conforme o alcance REAL de cada
   lutador (simulado com as classes de verdade) e caem quando o pouso é dentro do buraco.
3. Empurrão e puxão derrubam; a queda (`STATE_FALL`) tira o lutador do round, é desenhada e termina sem corpo.
4. `speed_mult` por tile, prop sólido, perigo telegrafado (aviso, ativo, recarga), spawns e pickups fora de buracos.
5. A IA não pousa dentro de buracos e contorna os que cortam o caminho.
6. Música por nome de arquivo e o SFX de queda existem.
"""
import dataclasses
import math
import os
import random
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
from src.audio.sound_events import SoundEvent
from src.audio.procedural_sfx import _GENERATOR_MAP
from src.config import (
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE, CHAR_SAITOU, CHAR_RIFLE,
    CHAR_KABUKI, CHAR_PIRATE,
)
from src.effects.fall_render import render_falling_fighter
from src.entities.ai_controller import SamuraiAI
from src.entities.pickups import PowderPouch
from src.entities.samurai import STATE_FALL, STATE_DEAD, STATE_IDLE, STATE_STUNNED, FALL_DURATION, PIT_CROSSING_STATES
from src.isometric.camera import Camera
from src.world import arenas
from src.world.arena_generator import (
    ArenaMap, ArenaSpec, ArenaSpecError, FillLayer, HazardSpec, PIT_EDGE_MARGIN, GAP_WIDTHS, PitZone, PropSpec, RectLayer,
    SpawnRule, StageSpec, TileStyle, derive_spec, max_crossable_gap, validate_spec,
)
from src.world.hazards import PHASE_ACTIVE, PHASE_IDLE, PHASE_WARN
from src.world.solid_props import SolidProp

DT = 1.0 / 60.0
GROUND, SLOW = 1, 2


def _spec(pits=(), **overrides) -> ArenaSpec:
    """Arena sintética 22x22: chão e uma faixa lenta; buracos informados."""
    spec = ArenaSpec(
        id="engine_test", name="Teste do Motor", cols=22, rows=22, bg_color=(10, 10, 14), music="bgm_bamboo",
        tile_styles={GROUND: TileStyle("flat", ((90, 90, 80),)), SLOW: TileStyle("flat", ((70, 60, 40),), speed_mult=0.5)},
        layers=(FillLayer(GROUND), RectLayer(SLOW, 15, 20, 0, 21)),
        props=(), spawns=SpawnRule(margin=3.0, fallback=((3.0, 11.0), (20.5, 5.0))), stage=StageSpec(3.0, 5.0),
        pits=tuple(pits),
    )
    return derive_spec(spec, **overrides) if overrides else spec


def _crossing_arena() -> ArenaMap:
    """Quatro fendas N-S de classes S, M, L e J em x crescente, longas o bastante para só dar para atravessar."""
    pits = (
        PitZone(6.0, 1.5, 6.0 + GAP_WIDTHS["S"], 20.5, "S"),
        PitZone(9.0, 1.5, 9.0 + GAP_WIDTHS["M"], 20.5, "M"),
        PitZone(12.0, 1.5, 12.0 + GAP_WIDTHS["L"], 20.5, "L"),
        PitZone(16.0, 1.5, 16.0 + GAP_WIDTHS["J"], 20.5, "J"),
    )
    return ArenaMap(_spec(pits, layers=(FillLayer(GROUND),)))


def step_fighter(f, opp, dt, game_map, particles, projectiles, banners):
    """Mesma ordem do laço principal: atualização do lutador, depois a checagem de queda."""
    if f.state == STATE_FALL:
        f.update_pit(dt, game_map, particles, banners)
        return
    if isinstance(f, main.PirateSwordswoman):
        f.update(dt, game_map, particles, opponent=opp, banners=banners)
    elif isinstance(f, main.SaitouSamurai):
        f.update(dt, game_map, particles)
    elif isinstance(f, (main.Rifleman, main.Kabuki, main.Musketeer, main.GrayNinja)):
        f.update(dt, game_map, particles)
    elif isinstance(f, (main.BlueSamurai, main.KyudoArcher)):
        f.update(dt, game_map, particles, projectiles)
    else:
        f.update(dt, game_map)
    f.update_pit(dt, game_map, particles, banners)


def _fighter_at(char_id, x, y=11.0):
    f = main.create_fighter(char_id, x, y)
    f.facing_x, f.facing_y = 1.0, 0.0
    return f


def _run(f, game_map, seconds=3.0, dt=DT):
    opp = main.create_fighter(CHAR_MUSASHI, 1.5, 1.5)
    particles, projectiles, banners = [], [], []
    for _ in range(int(seconds / dt)):
        step_fighter(f, opp, dt, game_map, particles, projectiles, banners)
    return particles, banners


def _crossing_result(char_id, action, pit: PitZone, game_map, dt=DT) -> bool:
    """True se o lutador, partindo da borda do buraco, termina do outro lado (e vivo)."""
    f = _fighter_at(char_id, pit.x0 - PIT_EDGE_MARGIN)
    action(f)
    _run(f, game_map, 3.0, dt)
    return f.is_alive and f.state != STATE_FALL and f.wx > pit.x1


def _roll(f):
    main.execute_fighter_roll(f, 1.0, 0.0, f.wx + 5.0, f.wy, [], decoys=[], game_map=None)


def _jump(f):
    f.trigger_jump(f.wx + 5.0, f.wy)


def test_pit_spec_validation():
    good = PitZone(6.0, 3.0, 7.0, 9.0, "S")
    validate_spec(_spec((good,)))
    bad_cases = [
        (PitZone(6.0, 3.0, 7.5, 9.0, "S"), "pede largura"),
        (PitZone(6.0, 3.0, 8.0, 9.0, "VOID"), "VOID precisa"),
        (PitZone(6.0, 3.0, 7.0, 9.0, "Z"), "classe desconhecida"),
        (PitZone(8.0, 3.0, 7.0, 9.0, "S"), "inválido"),
        (PitZone(6.0, 3.0, 7.0, 40.0, "S"), "fora do mapa"),
    ]
    for pit, fragment in bad_cases:
        try:
            validate_spec(_spec((pit,)))
        except ArenaSpecError as exc:
            assert fragment in str(exc), (fragment, str(exc))
        else:
            raise AssertionError(f"buraco inválido aceito: {fragment}")
    try:
        validate_spec(_spec((good, PitZone(6.5, 4.0, 7.5, 8.0, "S"))))
    except ArenaSpecError as exc:
        assert "sobrepõe" in str(exc)
    else:
        raise AssertionError("buracos sobrepostos aceitos")
    try:
        ArenaMap(_spec((good,), stage=StageSpec(6.5, 5.0)))
    except ArenaSpecError as exc:
        assert "buraco" in str(exc)
    else:
        raise AssertionError("palco dentro de buraco aceito")
    try:
        _spec(tile_styles={GROUND: TileStyle("flat", ((1, 2, 3),), speed_mult=5.0), SLOW: TileStyle("flat", ((1, 2, 3),))})
    except ArenaSpecError as exc:
        assert "speed_mult" in str(exc)
    else:
        raise AssertionError("speed_mult inválido aceito")
    variant = derive_spec(_spec((good,)), id="engine_variant", name="Variante")
    assert variant.id == "engine_variant" and variant.pits == (good,)
    assert max_crossable_gap(1.70) > GAP_WIDTHS["M"] and max_crossable_gap(1.70) < GAP_WIDTHS["L"]
    assert max_crossable_gap(2.31) > GAP_WIDTHS["L"] and max_crossable_gap(2.31) < GAP_WIDTHS["J"]
    assert max_crossable_gap(3.07) > GAP_WIDTHS["J"]
    print("  [OK] Buracos validados por classe; variantes de spec validadas.", flush=True)


def _railed_arena() -> ArenaMap:
    """Mesmas fendas do arena de travessia, mas protegidas por cordas e estacas."""
    pits = tuple(dataclasses.replace(p, railed=True) for p in _crossing_arena().pits)
    return ArenaMap(_spec(pits, layers=(FillLayer(GROUND),)))


def test_walking_over_unprotected_pit_falls():
    arena = _crossing_arena()
    assert not arena.has_rails and arena.rail_edge_distance(7.0, 7.0) == math.inf
    assert not arena.lanterns, "buraco sem proteção não tem estacas"
    pit = arena.pits[1]
    f = _fighter_at(CHAR_MUSASHI, pit.x0 - 2.0)
    fell = False
    for _ in range(240):
        f.apply_movement(1.0, 0.0, DT, arena)
        fell = f.update_pit(DT, arena) or fell
        if fell:
            break
    assert fell and f.state == STATE_FALL and not f.is_alive, "quem anda por cima de um buraco sem proteção cai"
    print("  [OK] Buraco sem proteção: andar por cima derruba.", flush=True)


def test_walking_is_blocked_at_railed_pit_edge():
    arena = _railed_arena()
    assert arena.has_rails and arena.lanterns, "buraco protegido ganha estacas de corda"
    pit = arena.pits[1]
    f = _fighter_at(CHAR_MUSASHI, pit.x0 - 2.0)
    for _ in range(240):
        f.apply_movement(1.0, 0.0, DT, arena)
        f.update_pit(DT, arena)
    assert f.is_alive and f.state != STATE_FALL
    assert f.wx <= pit.x0 - PIT_EDGE_MARGIN + 1e-6, f.wx
    assert arena.pit_at(f.wx, f.wy) is None
    # Diagonal: desliza ao longo da borda em vez de parar
    y_before = f.wy
    for _ in range(60):
        f.apply_movement(0.7, 0.7, DT, arena)
    assert f.wy > y_before + 0.5 and f.wx <= pit.x0 - PIT_EDGE_MARGIN + 1e-6
    # Protegido só cai por esquiva curta, empurrão ou puxão
    rolled = _fighter_at(CHAR_MUSASHI, arena.pits[2].x0 - PIT_EDGE_MARGIN)
    _roll(rolled)
    _run(rolled, arena, 3.0)
    assert rolled.fell_into_pit, "esquiva curta demais cai mesmo com proteção"
    pushed = _fighter_at(CHAR_MUSASHI, pit.x0 - 0.3)
    pushed.apply_forced_displacement(1.0, 0.0, arena)
    assert pushed.update_pit(DT, arena) is True, "empurrão passa por cima da corda"
    print("  [OK] Buraco protegido: andar é bloqueado e desliza; esquiva curta e empurrão ainda derrubam.", flush=True)


def test_crossing_uses_real_fighter_reach():
    arena = _crossing_arena()
    s, m, l, j = arena.pits
    heavy = [(CHAR_MUSASHI, "Musashi"), (CHAR_AMERICAN, "Joe"), (CHAR_RIFLE, "Teppo"), (CHAR_PIRATE, "Anne"), (CHAR_SAITOU, "Saitou")]
    agile = [(CHAR_GRAY, "Kasumi"), (CHAR_KABUKI, "Okuni"), (CHAR_PURPLE, "Murasaki")]
    for dt in (1.0 / 60.0, 1.0 / 30.0):
        for cid, name in heavy:
            assert _crossing_result(cid, _roll, s, arena, dt), f"{name} deveria vencer S (dt={dt})"
            assert _crossing_result(cid, _roll, m, arena, dt), f"{name} deveria vencer M (dt={dt})"
            assert not _crossing_result(cid, _roll, l, arena, dt), f"{name} não deveria vencer L (dt={dt})"
        for cid, name in agile:
            assert _crossing_result(cid, _roll, m, arena, dt), f"{name} deveria vencer M (dt={dt})"
            assert _crossing_result(cid, _roll, l, arena, dt), f"{name} deveria vencer L (dt={dt})"
            assert not _crossing_result(cid, _roll, j, arena, dt), f"{name} não deveria vencer J (dt={dt})"
        assert _crossing_result(CHAR_NINJA, _jump, j, arena, dt), f"Hanzo deveria vencer J com o salto (dt={dt})"
        assert _crossing_result(CHAR_KENSHIN, _roll, j, arena, dt), f"Kenshi deveria vencer J com o Shukuchi (dt={dt})"
    print("  [OK] Esquivas, salto e Shukuchi cruzam as classes de buraco conforme o alcance real.", flush=True)


def test_failed_crossing_and_forced_displacement_fall():
    arena = _crossing_arena()
    m, l = arena.pits[1], arena.pits[2]
    f = _fighter_at(CHAR_MUSASHI, l.x0 - PIT_EDGE_MARGIN)
    _roll(f)
    particles, banners = _run(f, arena, 3.0)
    assert f.state == STATE_DEAD and f.fell_into_pit and not f.is_alive and f.hp == 0
    assert not banners, "a queda não mostra aviso flutuante"
    assert particles, "a queda levanta poeira"

    pushed = _fighter_at(CHAR_GRAY, m.x0 - 0.5)
    pushed.apply_forced_displacement(1.2, 0.0, arena)
    assert pushed.update_pit(DT, arena) is True
    assert pushed.state == STATE_FALL and not pushed.is_alive
    assert pushed.take_hit((1.0, 0.0)) == (False, False), "quem cai não recebe golpes"
    assert pushed.update_pit(DT, arena) is False, "a queda só dispara uma vez"

    pulled = _fighter_at(CHAR_PURPLE, m.x0 - 0.5)
    pulled.wx += 1.0  # puxão da corrente altera a posição direto
    assert pulled.update_pit(DT, arena) is True

    stunned = _fighter_at(CHAR_SAITOU, m.x0 + 0.4)
    stunned.stun(0.8)
    assert stunned.update_pit(DT, arena) is True, "atordoado dentro do buraco cai"

    rope = _fighter_at(CHAR_NINJA, m.x0 + 0.4)
    rope.pit_cross_timer = 0.10  # puxada pela flecha de corda
    assert rope.update_pit(DT, arena) is False and rope.state != STATE_FALL
    for _ in range(8):
        rope.update_pit(DT, arena)
    assert rope.state == STATE_FALL, "ao soltar a corda dentro do buraco, cai"

    attacker = _fighter_at(CHAR_KENSHIN, m.x0 - PIT_EDGE_MARGIN)
    attacker.state = "ATTACK"
    attacker.wx = m.x0 + 0.3
    assert attacker.update_pit(DT, arena) is False, "avanço de golpe não cai no meio do ataque"
    attacker.state = STATE_IDLE
    assert attacker.update_pit(DT, arena) is True, "mas cai se o golpe terminar dentro do buraco"
    assert {"ROLL", "SHUKUCHI", "JUMP", "ATTACK"} <= set(PIT_CROSSING_STATES)
    print("  [OK] Empurrão, puxão, atordoamento e pouso curto derrubam; avanços de golpe e corda não.", flush=True)


def test_gatotsu_brakes_at_railed_pit_and_falls_in_open_pit():
    arena = _railed_arena()
    m = arena.pits[1]
    f = _fighter_at(CHAR_SAITOU, m.x0 - 3.0)
    f.trigger_gatotsu_thrust(m.x1 + 3.0, f.wy)
    _run(f, arena, 3.0)
    assert f.is_alive and f.state != STATE_FALL
    assert f.wx <= m.x0 - PIT_EDGE_MARGIN + 0.05, f.wx
    open_arena = _crossing_arena()
    g = _fighter_at(CHAR_SAITOU, open_arena.pits[1].x0 - 3.0)
    g.trigger_gatotsu_thrust(open_arena.pits[1].x1 + 3.0, g.wy)
    _run(g, open_arena, 3.0)
    assert g.fell_into_pit or g.state == STATE_FALL, "a investida atravessa um buraco aberto e cai"
    print("  [OK] O Gatotsu freia na corda do buraco protegido e cai no buraco aberto.", flush=True)


def test_fall_animation_renders_and_fades():
    arena = _crossing_arena()
    m = arena.pits[1]
    camera = Camera(11.0, 11.0)
    f = _fighter_at(CHAR_MUSASHI, m.x0 + 0.5)
    f.update_pit(DT, arena)
    assert f.state == STATE_FALL
    counts = []
    for fraction in (0.05, 0.5, 0.97):
        f.fall_timer = FALL_DURATION * fraction
        f.wz = -0.5 * 14.0 * f.fall_timer ** 2
        surf = pygame.Surface((1280, 720))
        surf.fill((40, 40, 50))
        base = surf.copy()
        render_falling_fighter(surf, f, camera)
        diff = pygame.mask.from_threshold(surf, (40, 40, 50), (3, 3, 3, 255))
        counts.append(1280 * 720 - diff.count())
    assert counts[0] > 200, f"corpo visível no início da queda: {counts}"
    assert counts[2] < counts[0], f"corpo some ao final da queda: {counts}"
    print("  [OK] Animação de queda desenha o corpo e o faz sumir no buraco.", flush=True)


def test_speed_mult_and_solid_prop():
    arena = ArenaMap(_spec(props=(PropSpec("solid_block", 9.0, 9.0, {"width": 1.5, "depth": 1.5, "height": 0.8}),)))
    from src.world.arena_generator import PROP_KINDS
    assert PROP_KINDS["solid_block"].collection == "buildings"
    normal = _fighter_at(CHAR_MUSASHI, 5.0)
    slow = _fighter_at(CHAR_MUSASHI, 15.5)
    for _ in range(60):
        normal.apply_movement(1.0, 0.0, DT, arena)
        slow.apply_movement(1.0, 0.0, DT, arena)
    d_normal, d_slow = normal.wx - 5.0, slow.wx - 15.5
    assert abs(d_slow / d_normal - 0.5) < 0.03, (d_normal, d_slow)
    assert arena.speed_mult_at(16.0, 5.0) == 0.5 and arena.speed_mult_at(5.0, 5.0) == 1.0

    walker = _fighter_at(CHAR_MUSASHI, 6.0, 9.75)
    for _ in range(120):
        walker.apply_movement(1.0, 0.0, DT, arena)
    assert walker.wx < 9.0, "o prop sólido bloqueia quem anda"
    prop = SolidProp(0.0, 0.0, 2.0, 1.0)
    hit, push_x, push_y = prop.check_collision(1.0, 0.5, 0.3)
    assert hit and (abs(push_x) > 0 or abs(push_y) > 0)
    for _ in range(100):
        a, b = arena.pick_spawns()
        for p in (a, b):
            assert not arena.buildings[0].check_collision(p[0], p[1], 0.9)[0]
    print("  [OK] speed_mult por tile e prop sólido (colisão e spawns).", flush=True)


def test_telegraphed_hazard_cycle_and_push():
    from src.world.hazards import TideSurge
    random.seed(3)
    arena = ArenaMap(_spec())
    hazard = TideSurge(x_from=0.0, x_to=22.0, band_width=3.0, sweep_speed=6.0, push_speed=4.0,
                       warn_time=1.0, interval=(1.0, 1.0), initial_delay=0.5)
    arena.hazards.append(hazard)
    victim = _fighter_at(CHAR_MUSASHI, 8.0)
    bystander = _fighter_at(CHAR_MUSASHI, 3.0, 19.0)
    bystander.wx = 21.0  # já depois da faixa quando ela chegar lá
    banners, particles = [], []
    seen = []
    pushed_in_warn = False
    for _ in range(int(14.0 / DT)):
        x_before = victim.wx
        arena.update(DT, [victim, bystander], None, particles, banners)
        if not seen or seen[-1] != hazard.phase:
            seen.append(hazard.phase)
        if hazard.phase == PHASE_WARN and victim.wx != x_before:
            pushed_in_warn = True
    assert seen[:4] == [PHASE_IDLE, PHASE_WARN, PHASE_ACTIVE, PHASE_IDLE], seen
    assert not pushed_in_warn, "o aviso não empurra ninguém"
    assert victim.wx > 11.0, "a maré empurra quem está na faixa"
    assert banners, "o aviso mostra um banner"
    assert arena.has_hazards
    print("  [OK] Perigo telegrafado: recarga, aviso, fase ativa com empurrão.", flush=True)


def test_spawns_and_pickups_avoid_pits():
    arena = ArenaMap(_spec((PitZone(8.0, 2.0, 9.48, 20.0, "M"), PitZone(12.0, 2.0, 15.8, 20.0, "VOID"))))
    for _ in range(150):
        a, b = arena.pick_spawns(min_distance=5.0)
        assert arena.pit_edge_distance(*a) >= 1.0 and arena.pit_edge_distance(*b) >= 1.0
    pouches = PowderPouch.create_arena_pouches(arena, [main.create_fighter(CHAR_RIFLE, 4.0, 11.0)], total_pouches=3)
    for pouch in pouches:
        assert arena.pit_edge_distance(pouch.wx, pouch.wy) >= 1.0, (pouch.wx, pouch.wy)
    try:
        ArenaMap(_spec((PitZone(2.0, 2.0, 4.0, 8.0, "L"),), spawns=SpawnRule(fallback=((3.0, 11.0), (3.0, 5.0)))))
    except ArenaSpecError as exc:
        assert "buraco" in str(exc)
    else:
        raise AssertionError("spawn de reserva em buraco aceito")
    print("  [OK] Spawns e pickups ficam fora dos buracos.", flush=True)


def test_ai_avoids_and_routes_around_pits():
    arena = ArenaMap(_spec((PitZone(10.0, 3.0, 11.48, 14.0, "M"),)))
    ai = SamuraiAI("hard")
    random.seed(11)
    # Rolagem de fuga: pouso dentro do buraco é recusado, pouso em chão firme é aceito
    f = _fighter_at(CHAR_MUSASHI, 9.5, 8.0)
    opp = _fighter_at(CHAR_KENSHIN, 5.0, 8.0)
    assert ai._away_ok(f, opp, arena, 1.7) is False, "rolar para longe do rival cairia na fenda"
    assert ai._toward_ok(f, opp, arena, 1.7) is True
    # Rota: rival do outro lado da fenda -> a IA contorna e não cai
    ai_f = _fighter_at(CHAR_AMERICAN, 7.0, 8.0)
    target = _fighter_at(CHAR_MUSASHI, 14.0, 8.0)
    target.is_alive = True
    particles, projectiles, banners = [], [], []
    reached = False
    for _ in range(int(25.0 / DT)):
        ai.update(ai_f, target, DT, arena, projectiles, [], [])
        step_fighter(ai_f, target, DT, arena, particles, projectiles, banners)
        if ai_f.wx > 12.0:
            reached = True
            break
    assert ai_f.is_alive and ai_f.state != STATE_FALL, "a IA não pode cair sozinha"
    assert reached, f"a IA deveria contornar a fenda e chegar ao outro lado (x={ai_f.wx:.2f})"
    print("  [OK] IA recusa pouso em buraco e contorna fendas no caminho.", flush=True)


def test_music_files_and_fall_sfx():
    music_dir = os.path.join(ROOT, "assets", "sounds", "music")
    for arena_id in arenas.arena_ids():
        track = arenas.ARENA_SPECS[arena_id].music
        assert os.path.exists(os.path.join(music_dir, track + ".mp3")), f"música ausente: {track}"
    for arena_id in ("ganryu_island", "iga_rooftops", "forest_camp", "nagashino_field", "shadow_cave", "mist_temple",
                     "kabuki_stage", "mountain_shrine", "pirate_deck", "baroque_court"):
        assert os.path.exists(os.path.join(music_dir, f"bgm_{arena_id}.mp3")), arena_id
    assert SoundEvent.FALL in _GENERATOR_MAP and SoundEvent.FALL.value == "fall"
    assert os.path.exists(os.path.join(ROOT, "assets", "sounds", "sfx", "fall.wav"))
    with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as fh:
        src = fh.read()
    assert "play_music(game_map.music)" in src and "SoundEvent.FALL" in src
    print("  [OK] Música por nome de arquivo (12 faixas) e SFX de queda.", flush=True)


def test_arena_engine():
    print("=== TESTE 6.3.1: Motor de Arenas Temáticas ===", flush=True)
    test_pit_spec_validation()
    test_walking_over_unprotected_pit_falls()
    test_walking_is_blocked_at_railed_pit_edge()
    test_crossing_uses_real_fighter_reach()
    test_failed_crossing_and_forced_displacement_fall()
    test_gatotsu_brakes_at_railed_pit_and_falls_in_open_pit()
    test_fall_animation_renders_and_fades()
    test_speed_mult_and_solid_prop()
    test_telegraphed_hazard_cycle_and_push()
    test_spawns_and_pickups_avoid_pits()
    test_ai_avoids_and_routes_around_pits()
    test_music_files_and_fall_sfx()
    print("=== TESTE 6.3.1 CONCLUÍDO ===", flush=True)


if __name__ == "__main__":
    test_arena_engine()
