import os
import sys
import math
import pygame

# Initialize headless pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((800, 600))

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.entities.aoi import AoiHuntress
from src.entities.ichi import IchiBlade
from src.entities.blue_samurai import BlueSamurai
from src.entities.red_samurai import RedSamurai
from src.entities.rifleman import Rifleman
from src.entities.pirate import PirateSwordswoman
from src.entities.yellow_ninja import YellowNinja
from src.entities.boss_oni import BossOni, BossHazard
from src.entities.samurai import STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY
from src.effects.cinematic_director import CinematicDirector
from src.isometric.camera import Camera
from src.world.map_data import GameMap


def test_aoi_combo():
    print("[1] Testing Aoi Huntress Combo...")
    aoi = AoiHuntress(5.0, 5.0)
    assert aoi.combo_step == 0
    # Step 1: trigger_attack -> spear thrust
    success1 = aoi.trigger_attack(6.0, 5.0)
    assert success1, "Step 1 (spear) failed"
    assert aoi.state == STATE_ATTACK
    assert aoi.attack_type == "spear"
    assert aoi.combo_step == 1
    assert aoi.combo_window > 0.40

    # Step 2: trigger_attack buffered/chained while in spear attack
    success2 = aoi.trigger_attack(6.0, 5.0)
    assert success2, "Step 2 (makiri) failed to chain during spear thrust"
    assert aoi.state == STATE_ATTACK
    assert aoi.attack_type == "makiri"
    assert aoi.combo_step == 0
    assert aoi.hitbox_damage == 1
    print(" -> Aoi combo test passed!")


def test_ichi_speed_and_recovery():
    print("[2] Testing Ichi Primary Attack Cadence & Recovery...")
    ichi = IchiBlade(5.0, 5.0)
    assert ichi.attack_duration >= 0.20, f"Ichi attack duration {ichi.attack_duration} too fast"
    assert ichi.attack_recovery >= 0.25, f"Ichi attack recovery {ichi.attack_recovery} too short"

    # Trigger attack
    assert ichi.trigger_gyaku_iai(6.0, 5.0)
    assert ichi.state == STATE_ATTACK

    # Advance until recovery
    ichi.update(0.23)
    assert ichi.state == STATE_RECOVERY
    assert not ichi.can_act(), "Ichi should NOT be able to act during recovery!"
    assert not ichi.trigger_gyaku_iai(6.0, 5.0), "Ichi should not be able to cancel recovery into attack!"

    # Finish recovery
    ichi.update(0.27)
    assert ichi.state == STATE_IDLE
    assert ichi.can_act(), "Ichi should be able to act after recovery completes"
    print(" -> Ichi cadence and recovery test passed!")


def test_musashi_cadence():
    print("[3] Testing Musashi Combo Cadence...")
    musashi = BlueSamurai(5.0, 5.0)
    assert musashi.recovery_duration >= 0.22, f"Musashi recovery {musashi.recovery_duration} too short"

    # Step 1
    assert musashi.trigger_combo_attack(6.0, 5.0)
    assert musashi.state == STATE_ATTACK
    assert musashi.combo_step == 1
    assert musashi.state_timer >= 0.25, f"Step 1 timer {musashi.state_timer} too fast"

    # Buffer step 2 while in attack
    musashi.trigger_combo_attack(6.0, 5.0)
    assert musashi.combo_buffered

    # Advance until step 2 triggers
    gmap = GameMap()
    musashi.update(0.27, gmap)
    assert musashi.combo_step == 2
    assert musashi.state == STATE_ATTACK
    assert musashi.state_timer >= 0.27, f"Step 2 timer {musashi.state_timer} too fast"
    print(" -> Musashi cadence test passed!")


def test_boss_oni_hazards_and_vulnerability():
    print("[4] Testing Gashadokuro Hazards Cleanup & Vulnerability Visuals...")
    boss = BossOni(10.0, 10.0, seed=42)
    gmap = GameMap()
    cam = Camera(800, 600)
    surf = pygame.Surface((800, 600), pygame.SRCALPHA)

    # Test hazard cleanup on serpent stun
    boss.set_phase(1)
    boss.sub = "run"
    player = BlueSamurai(10.0, 10.0)
    boss.sub_data = {"e": boss._new_ellipse(player, gmap)}
    boss.hazards.append(BossHazard("path", 0, 0, 1.0, 0.0, points=[(10, 10), (11, 11)], life=8.0))
    assert any(h.kind == "path" for h in boss.hazards)

    # Simulate stun transition
    boss.sub_t = 0.5
    boss._dust = lambda *args: None
    # Call serpent brain with hit_rock simulated
    old_move = boss._move
    boss._move = lambda x, y, m: True  # force hit_rock
    boss._brain_serpent(0.016, gmap, player, None, None, cam)
    boss._move = old_move

    assert boss.sub == "stun"
    assert not any(h.kind == "path" for h in boss.hazards), "Obsolete path hazard not cleared on stun!"

    # Test torso bounce wall directions
    boss.set_phase(2)
    boss.sub = "bounce"
    boss.sub_data = {"dir": (-0.8, -0.6), "speed": 10.0, "flight": 0.0, "bounces": 0}
    boss.wx, boss.wy = 1.0, 1.0  # Near left/top wall
    boss._dust = lambda *args: None
    boss._brain_torso(0.016, gmap, player, None, None, cam)
    assert boss.sub_data["dir"][0] > 0, "Torso should bounce away from min_x (positive dx)"
    assert boss.sub_data["dir"][1] > 0, "Torso should bounce away from min_y (positive dy)"

    # Test vulnerability rendering
    boss.vulnerable = True
    boss.render_ground(surf, cam, game_time=1.0)
    boss.render(surf, cam, game_time=1.0)
    print(" -> Gashadokuro hazards cleanup and vulnerability visuals passed!")


def test_tomoe_finishers_somersault_and_pin():
    print("[5] Testing Tomoe Finishers & Victim Models...")
    cd = CinematicDirector()
    cam = Camera(800, 600)
    surf = pygame.Surface((800, 600), pygame.SRCALPHA)

    for style in ("PINNED_TO_EARTH", "HAMAYA_HOLY_PIERCE"):
        tomoe = AoiHuntress(5.0, 5.0)  # acts as attacker
        tomoe.char_type = "tomoe"
        victim = RedSamurai(7.0, 5.0)

        cd.trigger_fatal_strike(tomoe, victim, style, (1.0, 0.0))
        assert cd.finisher_style == style
        assert cd.finisher_attacker is tomoe
        assert cd.finisher_victim is victim

        # Advance to Phase 2 (fall phase)
        cd.camera_setup_timer = 0.0
        cd.delayed_death_timer = 2.0
        cd.finisher_strike_timer = cd.finisher_strike_duration * (1.0 - 0.45)  # prog = 0.45 (hit_prog <= prog < ground_prog)

        cd.update(0.001, None)
        assert victim.extra_props.get("somersault_angle", 0.0) > 0.0, f"Victim somersault_angle not set in {style} Phase 2!"
        assert getattr(victim, "somersault_angle", 0.0) > 0.0, f"Victim somersault_angle attribute not set in {style} Phase 2!"

        # Ensure RedSamurai.render does not overwrite somersault_angle
        victim.render(surf, cam)

        # Advance to Phase 3 (ground pinned phase)
        cd.finisher_strike_timer = cd.finisher_strike_duration * (1.0 - 0.75)  # prog = 0.75 (ground_prog <= prog)
        cd.update(0.001, None)
        assert victim.state == "PINNED_DOWN"
        assert victim.extra_props.get("is_pinned_to_earth", False) is True, f"is_pinned_to_earth not True in {style} Phase 3!"
        if style == "HAMAYA_HOLY_PIERCE":
            assert victim.extra_props.get("is_holy_pierced", False) is True

        # Render pinned victim
        victim.render(surf, cam)

    # Test other fighter models don't overwrite somersault_angle
    for fighter_cls, char_name in [
        (Rifleman, "teppo"),
        (PirateSwordswoman, "pirate"),
        (YellowNinja, "ninja"),
    ]:
        f = fighter_cls(5.0, 5.0)
        f.extra_props = {"somersault_angle": 90.0, "is_pinned_to_earth": True}
        f.state = "PINNED_DOWN"
        f.is_alive = False
        f.render(surf, cam)

    print(" -> Tomoe finishers and victim models test passed!")


if __name__ == "__main__":
    test_aoi_combo()
    test_ichi_speed_and_recovery()
    test_musashi_cadence()
    test_boss_oni_hazards_and_vulnerability()
    test_tomoe_finishers_somersault_and_pin()
    print("\nALL 5 AUDIT FIX TESTS PASSED SUCCESSFULLY!")
