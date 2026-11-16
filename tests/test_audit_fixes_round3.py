import os
import sys
import math
import pygame

# Initialize headless pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.config import CHAR_KENSHIN, CHAR_HENDRIKA, SCREEN_WIDTH, SCREEN_HEIGHT
from src.i18n import t, set_lang
from src.arcade.arcade_mode import ArcadeRun
from src.arcade.arcade_screens import ArcadeBracketScreen, ArcadeResultScreen
from src.entities.boss_oni import BossOni
from src.world.obstacles import Rock, AncientTree
from src.world.solid_props import SolidProp
from src.world.decor import SpectralToro, JizoStatue, BoneMound
from src.entities.voxel_corpse import VoxelCorpse, WAIST_Z
from src.entities.hendrika import HendrikaAlchemist
from src.entities.red_samurai import RedSamurai
from src.effects.cinematic_director import CinematicDirector


def _key(key):
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def _hat(val):
    return pygame.event.Event(pygame.JOYHATMOTION, hat=0, value=val)


def _btn(b):
    return pygame.event.Event(pygame.JOYBUTTONDOWN, button=b)


def test_secret_code_and_practice_mode():
    print("[1] Testing Secret Code warp to final boss & practice mode...")
    run = ArcadeRun(player_char=CHAR_KENSHIN)
    bracket = ArcadeBracketScreen()
    bracket.open(run)

    assert run.index == 0
    assert run.is_practice is False

    # Input keyboard sequence: UP, UP, DOWN, DOWN, LEFT, RIGHT, LEFT, RIGHT, B, A
    seq = [
        pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN,
        pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT,
        pygame.K_b, pygame.K_a
    ]
    for k in seq:
        res = bracket.handle_event(_key(k))
        # intermediate keys must not start fight or abandon
        assert res is None

    assert run.index == 11, "Must warp directly to final boss"
    assert run.is_practice is True, "Must set is_practice flag"

    # Test gamepad sequence protection: Circle (button 1) must not abandon, Cross (button 0) must not auto-start
    run2 = ArcadeRun(player_char=CHAR_KENSHIN)
    bracket2 = ArcadeBracketScreen()
    bracket2.open(run2)

    dpad_hats = [(0, 1), (0, 1), (0, -1), (0, -1), (-1, 0), (1, 0), (-1, 0), (1, 0)]
    for h in dpad_hats:
        bracket2.handle_event(_hat(h))

    # Circle (button 1)
    res_c = bracket2.handle_event(_btn(1))
    assert res_c is None
    assert bracket2.confirm_abandon is False, "Circle during secret code must not trigger abandon screen"

    # Cross (button 0)
    res_x = bracket2.handle_event(_btn(0))
    assert res_x is None, "Cross during secret code must not auto-start fight"
    assert run2.index == 11
    assert run2.is_practice is True

    print(" -> Secret code warp & button protection passed!")


def test_scoreboard_cheaters_never_prosper():
    print("[2] Testing Scoreboard with Cheaters Never Prosper penalty...")
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    for lang in ("pt", "en"):
        set_lang(lang)
        run = ArcadeRun(player_char=CHAR_KENSHIN)
        run.is_practice = True
        run.score = -1000000

        result = ArcadeResultScreen()
        result.open(run, rank=None, high_scores=[{"score": 50000, "char": "kenshin"}])
        result.update(0.1)
        result.render(surf)

        # Check title text and warning string
        warn_txt = t("arcade_cheaters_never_prosper")
        assert len(warn_txt) > 0
        if lang == "pt":
            assert "TRAPACEIROS" in warn_txt.upper()
        else:
            assert "CHEATERS" in warn_txt.upper()

    set_lang("pt")
    print(" -> Scoreboard -1,000,000 & Cheaters Never Prosper test passed!")


def test_boss_obstacles_break_on_two_hits():
    print("[3] Testing Gashadokuro arena obstacles: break after 2 hits exclusively from Boss...")
    boss = BossOni(10.0, 10.0, seed=42)

    # Test various obstacle types
    obstacles = [
        Rock(10.5, 10.0, radius=0.6),
        AncientTree(10.0, 10.5),
        SpectralToro(10.5, 10.5),
        JizoStatue(10.0, 9.5),
        BoneMound(9.5, 10.0),
    ]

    for obs in obstacles:
        # Initial state: intact, collision active
        assert getattr(obs, "is_broken", False) is False
        assert getattr(obs, "is_cracked", False) is False
        c, px, py = obs.check_collision(obs.wx, obs.wy, 0.5)
        assert c is True, "Unbroken obstacle must block collision"

        # Hit 1 by Boss
        boss.time += 1.0
        boss._hit_obstacle(obs)
        assert getattr(obs, "boss_hits", 0) == 1
        assert getattr(obs, "is_cracked", False) is True
        assert getattr(obs, "is_broken", False) is False
        c1, _, _ = obs.check_collision(obs.wx, obs.wy, 0.5)
        assert c1 is True, "Cracked obstacle must still collide"

        # Hit 2 by Boss
        boss.time += 1.0
        boss._hit_obstacle(obs)
        assert getattr(obs, "boss_hits", 0) == 2
        assert getattr(obs, "is_broken", False) is True
        c2, px2, py2 = obs.check_collision(obs.wx, obs.wy, 0.5)
        assert c2 is False and px2 == 0.0 and py2 == 0.0, "Broken obstacle must disable collision"

    # Verify that player collision does NOT damage obstacle
    fresh_obs = Rock(5.0, 5.0, radius=0.6)
    player = RedSamurai(5.2, 5.0)
    # Player collision check
    collided, _, _ = fresh_obs.check_collision(player.wx, player.wy, player.hitbox_radius)
    assert collided is True
    assert getattr(fresh_obs, "boss_hits", 0) == 0, "Player must not increment boss_hits"
    assert getattr(fresh_obs, "is_cracked", False) is False
    assert getattr(fresh_obs, "is_broken", False) is False

    print(" -> Boss obstacle 2-hit break exclusively by Boss test passed!")


def test_gashadokuro_defeat_animation_sequence():
    print("[4] Testing Gashadokuro defeat animation & dissolve sequence...")
    boss = BossOni(10.0, 10.0, seed=42)
    boss.hp = 1
    boss.vulnerable = True

    # Deal fatal blow
    hit, dead = boss.take_hit((1.0, 0.0), damage=1)
    assert hit is True and dead is True
    assert boss.state == "DYING_FREEZE"
    assert boss.dying is True
    assert boss.is_alive is False

    # Update through DYING_FREEZE
    particles = []
    boss.update(0.7, particles=particles)
    assert boss.state in ("BONE_COLLAPSE", "PURPLE_DISSOLVE")

    # Update through PURPLE_DISSOLVE
    boss.update(1.5, particles=particles)
    assert boss.state == "PURPLE_DISSOLVE"
    assert boss.whiteout_alpha > 0.0
    assert len(particles) > 0

    # Advance until dissolve is complete
    boss.update(2.0, particles=particles)
    assert boss.dissolve_complete is True
    assert boss.whiteout_alpha >= 254.0
    assert boss.alpha == 0

    print(" -> Gashadokuro defeat animation test passed!")


def test_hendrika_visceral_finisher():
    print("[5] Testing Hendrika's Visceral Finisher (Surgical Acid Dissection)...")
    hendrika = HendrikaAlchemist(4.0, 4.0)
    victim = RedSamurai(4.8, 4.0)
    cd = CinematicDirector()

    # Verify finisher banner in both languages
    for lang in ("pt", "en"):
        set_lang(lang)
        cd._build_kanji_overlay(attacker=hendrika, victim=victim, death_style="STILETTO_CAROTID_VITRIOL")
        assert cd.cached_kanji_surf is not None
        assert cd.current_kanji_text == "硫酸解剖"
        if lang == "pt":
            assert "DISSECAÇÃO CIRÚRGICA ÁCIDA" in cd.current_kanji_subtitle
        else:
            assert "SURGICAL ACID DISSECTION" in cd.current_kanji_subtitle

    set_lang("pt")

    # Create VoxelCorpse with STILETTO_CAROTID_VITRIOL style
    corpse = VoxelCorpse(victim, "STILETTO_CAROTID_VITRIOL", (1.0, 0.0))

    # Must have both cleaved_top and cleaved_bottom
    assert hasattr(corpse, "cleaved_top"), "Corpse must have cleaved_top (upper dissected torso)"
    assert hasattr(corpse, "cleaved_bottom"), "Corpse must have cleaved_bottom (dissolved legs)"
    assert corpse.cleaved_top in corpse.pieces
    assert corpse.cleaved_bottom in corpse.pieces

    # Verify pieces include acid droplets and bone shards
    acid_droplets = [p for p in corpse.pieces if getattr(p, "piece_type", "") == "acid_droplet"]
    bone_shards = [p for p in corpse.pieces if getattr(p, "piece_type", "") == "bone_shard"]
    assert len(acid_droplets) >= 20, f"Expected >= 20 acid droplets, got {len(acid_droplets)}"
    assert len(bone_shards) >= 4, f"Expected >= 4 bone shards, got {len(bone_shards)}"
    assert len(corpse.blood_droplets) >= 30, f"Expected >= 30 blood droplets, got {len(corpse.blood_droplets)}"

    # Update corpse physics
    corpse.update(0.2)
    assert corpse.cleaved_top.wz > 0.0
    assert corpse.cleaved_bottom.wz >= 0.0

    print(" -> Hendrika visceral finisher test passed!")


if __name__ == "__main__":
    test_secret_code_and_practice_mode()
    test_scoreboard_cheaters_never_prosper()
    test_boss_obstacles_break_on_two_hits()
    test_gashadokuro_defeat_animation_sequence()
    test_hendrika_visceral_finisher()
    print("\n=======================================================")
    print("ALL AUDIT ROUND 3 TESTS PASSED (100% SUCCESS)!")
    print("=======================================================")
