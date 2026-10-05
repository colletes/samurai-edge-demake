"""
Teste do entregável 8.2: Oni Gashadokuro (vida e fases, janelas de dano, ossos reaproveitados, ataques telegrafados,
arena escondida, checkpoint no Arcade e integração com o motor de combate).
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_boss_oni.py
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

from src.arcade.arcade_mode import ArcadeRun, FightKind, FIGHT_LOST, FIGHT_WON
from src.config import ARENA_GASHADOKURO, CHAR_BOSS
from src.effects.cinematic_director import CinematicDirector
from src.entities.boss_model import BONE_COUNT, BONES, DEBRIS_BY_PHASE, TRANSFORM_TIME
from src.entities.boss_oni import BossOni, BOSS_TUNING, BossHazard
from src.entities.red_samurai import RedSamurai
from src.i18n import set_lang
from src.isometric.camera import Camera
from src.roster import ARENA_ORDER
from src.world.arenas import ARENA_SPECS, arena_ids, create_arena

DT = 1 / 60
set_lang("pt")


def arena():
    return create_arena(ARENA_GASHADOKURO)


def make(phase=0, seed=8):
    boss = BossOni(10.5, 7.5, seed)
    boss.set_phase(phase)
    boss.set_facing(10.5, 17.5)
    player = RedSamurai(10.5, 17.5)
    player.max_hp = player.hp = 60
    return boss, player


def step(boss, player, game_map, seconds, particles=None, banners=None):
    particles = [] if particles is None else particles
    banners = [] if banners is None else banners
    for _ in range(int(seconds / DT)):
        boss.update(DT, game_map, player, particles, banners, [], None)


def hit_ready(boss):
    boss.vulnerable = True
    boss.invuln_timer = 0.0
    return boss.take_hit((1.0, 0.0), 2)


def test_phase_transitions():
    boss, player = make()
    gm = arena()
    assert boss.hp == 10 and boss.phase == 0
    phases = []
    for point in range(1, 11):
        hit, dead = hit_ready(boss)
        assert hit and dead == (point == 10), point
        phases.append(boss.phase)
        if dead:
            break
        if boss.transforming:
            assert boss.take_hit((1, 0), 2) == (False, False), "invulnerável durante a transformação"
            step(boss, player, gm, TRANSFORM_TIME + 0.1)
    assert phases == [0, 1, 1, 2, 2, 3, 3, 4, 4, 4], phases
    assert boss.hp == 0 and not boss.is_alive
    print("  [OK] 10 pontos de vida: nova fase a cada 2, invulnerável ao se transformar, morte no 10º ponto.", flush=True)


def test_hit_gating_no_knockback_no_stun():
    boss, player = make()
    boss.vulnerable = False
    assert boss.take_hit((1, 0), 2) == (False, False) and boss.hp == 10 and boss._clank
    hit_ready(boss)
    assert boss.hp == 9
    assert boss.take_hit((1, 0), 2) == (False, False), "recarga entre golpes"
    before = (boss.wx, boss.wy)
    boss.apply_forced_displacement(3.0, 3.0, arena())
    boss.stun(2.0)
    boss.apply_slow(2.0)
    assert (boss.wx, boss.wy) == before and boss.state != "STUNNED"
    assert boss.update_pit(DT, arena()) is False and boss.is_crossing_pit()
    print("  [OK] Golpe fora da janela é bloqueado; sem knockback, stun, lentidão nem queda em buraco.", flush=True)


def test_boss_voxels_are_reused():
    boss, player = make()
    ids = {b.id for b in BONES}
    assert len(ids) == BONE_COUNT == 31
    for phase in range(5):
        boss.set_phase(phase)
        poses = boss.poses()
        assert set(poses) == ids and len(poses) == BONE_COUNT, phase
        for bone_id in DEBRIS_BY_PHASE[phase]:
            assert bone_id in boss.model.debris
            assert poses[bone_id][0][2] < 0.6, "o osso perdido está caído no chão"
    assert set(DEBRIS_BY_PHASE[1]) < set(DEBRIS_BY_PHASE[2]) < set(DEBRIS_BY_PHASE[3]) < set(DEBRIS_BY_PHASE[4])
    boss, player = make()
    boss.poses()
    hit_ready(boss), hit_ready(boss)
    assert boss.transforming and len(boss.poses()) == BONE_COUNT
    print("  [OK] Os mesmos 31 ossos em todas as fases; os perdidos viram entulho no chão.", flush=True)


def test_boss_attacks_are_telegraphed():
    gm = arena()
    for phase in range(5):
        boss, player = make(phase, seed=phase + 1)
        player.wx, player.wy = 10.5, 12.5
        log = []
        real = boss._hurt_player

        def spy(p, source, game_map, particles, banners, camera, damage=1, boss=boss, real=real, log=log):
            hazard_ok = any(h.is_active for h in boss.hazards)
            contact_ok = boss.sub in ("run", "slow", "stun", "bounce")
            log.append((boss.phase, boss.sub, hazard_ok or contact_ok))
            return real(p, source, game_map, particles, banners, camera, damage)

        boss._hurt_player = spy
        for _ in range(int(40 / DT)):
            boss.update(DT, gm, player, [], [], [], None)
            for h in boss.hazards:
                assert h.is_active == (h.kind not in ("path", "arrow") and h.warn <= h.t < h.warn + h.active)
            if player.hp < 55:
                player.hp = 60
                player.state = "IDLE"
        assert all(ok for *_, ok in log), (phase, log)
    print("  [OK] Nenhum dano antes do aviso: só áreas ativas ou contato dentro do padrão telegrafado.", flush=True)


def test_hazard_shapes():
    circle = BossHazard("circle", 5, 5, 1.0, 0.2, r=2.0)
    assert circle.contains(6.5, 5.0) and not circle.contains(8.0, 5.0)
    sector = BossHazard("sector", 5, 5, 1.0, 0.2, r=3.0, dir=0.0, half=math.pi / 2)
    assert sector.contains(7.0, 5.5) and not sector.contains(3.0, 5.0) and not sector.contains(9.0, 5.0)
    ring = BossHazard("ring", 5, 5, 0.0, 0.5, r0=2.0, speed=4.0, width=0.6)
    ring.t = 0.25
    assert ring.contains(5 + 2.0 + 4.0 * 0.25 - 0.3, 5) and not ring.contains(5, 5)
    print("  [OK] Formas das áreas: círculo, setor e anel que se expande.", flush=True)


def test_boss_serpent_path():
    gm = arena()
    rocks = list(gm.rocks)
    gm.rocks = []  # sem lápides no caminho: a volta completa termina na janela de desaceleração
    boss, player = make(1)
    player.wx, player.wy = 10.5, 14.5
    seen = []
    for _ in range(int(14 / DT)):
        boss.update(DT, gm, player, [], [], [], None)
        if not seen or seen[-1] != boss.sub:
            seen.append(boss.sub)
            if boss.sub == "telegraph":
                assert any(h.kind == "path" for h in boss.hazards), "a elipse aparece no chão antes da volta"
                assert not boss.vulnerable
            if boss.sub == "slow":
                assert boss.vulnerable and boss.pose["head_up"] < 0, "desacelera com a cabeça baixa"
    assert seen[:3] == ["telegraph", "run", "slow"], seen
    gm.rocks = rocks
    rock = gm.rocks[0]
    boss.sub, boss.sub_t = "run", 0.0
    boss.sub_data = {"e": {"cx": rock.wx, "cy": rock.wy, "a": 0.2, "b": 0.2, "th": 0.0, "dir": 1, "s": 0.0, "s0": 0.0}}
    boss.wx, boss.wy = rock.wx + 0.8, rock.wy
    boss.update(DT, gm, player, [], [], [], None)
    assert boss.sub == "stun" and boss.vulnerable, "bater em rocha atordoa a serpente"
    print("  [OK] Serpente: elipse telegrafada, desacelera com a cabeça baixa e atordoa ao bater numa rocha.", flush=True)


def test_boss_torso_bounces():
    gm = arena()
    boss, player = make(2)
    player.wx, player.wy = 3.0, 19.0
    bounds = (2.0, 2.0, 20.0, 20.0)
    states = set()
    for _ in range(int(40 / DT)):
        boss.update(DT, gm, player, [], [], [], None)
        states.add(boss.sub)
        assert bounds[0] - 0.7 <= boss.wx <= bounds[2] + 0.7 and bounds[1] - 0.7 <= boss.wy <= bounds[3] + 0.7
        assert gm.pit_at(boss.wx, boss.wy) is None if hasattr(gm, "pit_at") else True
        if player.hp < 55:
            player.hp = 60
        if boss.sub == "stun":
            assert boss.vulnerable and boss.wz == 0.0
    assert {"aim", "bounce", "stun"} <= states, states
    print("  [OK] Torso: telegrafa a direção, quica nos limites e sólidos, atordoa depois e é vulnerável só então.", flush=True)


def test_boss_club_slam():
    gm = arena()
    boss, player = make(3)
    player.wx, player.wy = 10.5, 13.0
    seen, land = [], None
    for _ in range(int(12 / DT)):
        boss.update(DT, gm, player, [], [], [], None)
        if boss.sub == "warn" and not land:
            land = boss.sub_data["land"]
            assert any(h.kind == "circle" and (h.x, h.y) == land for h in boss.hazards), "círculo de pouso marcado antes do salto"
        if not seen or seen[-1] != boss.sub:
            seen.append(boss.sub)
        if boss.sub == "stuck":
            assert boss.vulnerable and boss.pose["raise"] == 0.0
            assert math.dist((boss.wx, boss.wy), land) < 0.05, "a ponta cai onde foi marcado"
            break
    assert seen[:4] == ["idle", "warn", "jump", "stuck"], seen
    print("  [OK] Clava: círculo marcado antes do salto, pouso no ponto marcado e ponta vulnerável cravada.", flush=True)


def test_boss_skull_jumps():
    gm = arena()
    boss, player = make(4)
    player.wx, player.wy = 10.5, 13.0
    jumps, rest_after = 0, False
    prev = None
    for _ in range(int(14 / DT)):
        boss.update(DT, gm, player, [], [], [], None)
        if boss.sub == "aim":
            assert any(h.kind == "circle" for h in boss.hazards), "sombra de pouso antes do salto"
        if prev == "jump" and boss.sub != "jump":
            jumps += 1
        if boss.sub == "rest":
            rest_after = jumps >= 3
            assert boss.vulnerable
            break
        if player.hp < 55:
            player.hp = 60
        prev = boss.sub
    assert jumps == 3 and rest_after
    print("  [OK] Crânio: 3 saltos encadeados, sombra antes de cada pouso e descanso vulnerável no fim.", flush=True)


def test_director_collapse_and_kill():
    boss, player = make(4)
    for _ in range(2):
        hit_ready(boss)
    assert boss.hp == 0 and boss.dying
    director = CinematicDirector()
    director.trigger_fatal_strike(player, boss, "X", (1, 0))
    assert director.pending_corpse is None and director.pending_boss is boss and director.current_kanji_text == "餓者髑髏"
    gm = arena()
    for _ in range(60):
        director.update(DT, gm, [])
    assert boss.state == "BONE_COLLAPSE" and boss.model.collapse is not None
    for _ in range(int(4 / DT)):
        boss.update(DT, gm, player, [], [], [], None)
    poses = boss.poses()
    assert boss.model.collapse_done and all(max(a[2], b[2]) < 1.2 for a, b in poses.values()), "ossos no chão"
    print("  [OK] Morte: kanji, congelamento e ossos desabando no chão.", flush=True)


def test_silhouettes_and_budget():
    gm = arena()
    imgs = {}
    for az in (0.0, 22.5, 135.0, -22.5):
        for phase in range(5):
            boss, _ = make(phase)
            surf = pygame.Surface((900, 700))
            surf.fill((30, 24, 30))
            cam = Camera(10.5, 7.5)
            cam.set_azimuth(math.radians(az))
            boss.pose.update({"stomp": 0.0})
            boss.render(surf, cam)
            imgs[(az, phase)] = pygame.surfarray.array3d(surf).astype(int)
    for az in (0.0, 22.5, 135.0, -22.5):
        for a in range(5):
            assert (np.abs(imgs[(az, a)] - 30).sum(axis=2) > 0).sum() > 800, "o chefe aparece"
            for b in range(a + 1, 5):
                diff = (np.abs(imgs[(az, a)] - imgs[(az, b)]).sum(axis=2) > 0).sum()
                assert diff > 1500, (az, a, b, diff)
    surf = pygame.Surface((1280, 720))
    worst = 0.0
    for phase in range(5):
        boss, _ = make(phase)
        cam = Camera(10.5, 7.5)
        boss.render(surf, cam)
        t0 = time.perf_counter()
        for _ in range(20):
            boss.render(surf, cam)
        worst = max(worst, (time.perf_counter() - t0) / 20 * 1000)
    assert worst < 10.0, f"{worst:.1f} ms"
    print(f"  [OK] 5 fases com silhuetas distintas em 4 azimutes; pior quadro {worst:.1f} ms (< 10 ms).", flush=True)


def test_arena_hidden_from_selection():
    assert ARENA_GASHADOKURO not in arena_ids() and ARENA_GASHADOKURO not in ARENA_SPECS
    assert ARENA_GASHADOKURO not in ARENA_ORDER and len(arena_ids()) == 12
    gm = arena()
    assert len(gm.rocks) >= 6, "lápides para a elipse e o quique"
    print("  [OK] A arena do chefe existe, tem 6+ lápides e não aparece nas telas de seleção (12 arenas).", flush=True)


def test_arcade_integration_and_checkpoint():
    run = ArcadeRun("kenshin")
    boss_fight = run.ladder[10]
    assert boss_fight.kind == FightKind.BOSS and boss_fight.opponents == (CHAR_BOSS,) and boss_fight.arena_id == ARENA_GASHADOKURO
    run.index = 10
    run._reset_fight_state()
    assert run.on_round_end("P2") == FIGHT_LOST, "a primeira derrota no chefe pede Continue (D8)"
    run.boss_phase = 3
    run.score = 5000
    run.on_continue()
    assert run.boss_phase == 3 and run.index == 10 and run.continues == 1 and run.score == 3000
    boss = BossOni(10.5, 7.5)
    boss.set_phase(run.boss_phase)
    assert boss.phase == 3 and boss.hp == 4, "recomeça a fase atual com os 2 pontos dela"
    again = ArcadeRun.from_dict(run.to_dict())
    assert again.boss_phase == 3
    assert run.on_round_end("P1") == FIGHT_WON and run.is_finished and run.boss_phase == 0
    print("  [OK] Arcade: 11ª luta é o chefe, derrota usa Continue e recomeça na fase atingida, vitória fecha a jornada.", flush=True)


def test_heal_on_phases_three_and_five():
    gm = arena()
    for phase in (2, 4):
        boss, player = make(phase - 1)
        player.max_hp = 3
        player.hp = 1
        boss.model.xform_t = 1.0
        boss.hp = 11 - 2 * phase  # um ponto antes de entrar na fase
        boss.vulnerable = True
        boss.invuln_timer = 0.0
        boss.take_hit((1, 0), 2)
        assert boss.phase == phase and boss.transforming
        step(boss, player, gm, TRANSFORM_TIME + 0.2)
        assert player.hp == 2, (phase, player.hp)
    print("  [OK] O jogador recupera 1 HP ao entrar nas fases 3 e 5.", flush=True)


if __name__ == "__main__":
    test_phase_transitions()
    test_hit_gating_no_knockback_no_stun()
    test_boss_voxels_are_reused()
    test_hazard_shapes()
    test_boss_attacks_are_telegraphed()
    test_boss_serpent_path()
    test_boss_torso_bounces()
    test_boss_club_slam()
    test_boss_skull_jumps()
    test_director_collapse_and_kill()
    test_silhouettes_and_budget()
    test_arena_hidden_from_selection()
    test_arcade_integration_and_checkpoint()
    test_heal_on_phases_three_and_five()
    print("Todos os testes do chefe Oni Gashadokuro passaram.", flush=True)
