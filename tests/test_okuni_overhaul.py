"""
Automated Integration and Unit Test Suite for Okuni Overhaul (Sub-fase 2.9).
Verifies:
1. Okuni Kumadori Face in mesh_primitives (PORTRAIT_FACE_STYLES).
2. Okuni Model Realistic Materials & Legacy fallback.
3. Dynamic Articulated Arms & Fan Open/Close states in okuni_model.
4. Tessen Fan Strike combat mechanics (1.45m range, damage 2).
5. Dokukiri Poison Cloud (3.0m cone, 14 3D microvoxel wisps, 1.6m push, 0.8s whiff stun).
6. Kawarimi Decoy silk mannequin & whiff punish absorption (0.45s stun).
7. Finisher A: Tessen Zanshu decapitation & sakura burst.
8. Finisher B: Dokukiri Youkai caustic dissolution & collapsing skeleton bone disassembly.
9. Cinematic Director fatal strike phrases and closeup triggers.
10. Dynamic Intro & Victory scripts with 3-phase smoothstep interpolation and audio beats.
11. Model Inspector buttons, De/Para notes, and action evaluation.
12. Game Help manual card synchronization in PT & EN.
"""
import os
import sys
import math
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((800, 600))


def test_okuni_kumadori_face():
    from src.isometric.mesh_primitives import PORTRAIT_FACE_STYLES
    assert "okuni" in PORTRAIT_FACE_STYLES, "okuni style missing from PORTRAIT_FACE_STYLES"
    st = PORTRAIT_FACE_STYLES["okuni"]
    assert st.get("kumadori") is True, "Okuni must have kumadori makeup"
    assert st.get("lashes") is True, "Okuni must have anime lashes"
    assert st.get("delicate_nose") is True, "Okuni must have delicate nose"
    assert st.get("feminine_lips") is True, "Okuni must have feminine lips"
    assert st.get("iris") == (185, 36, 52), "Okuni iris must be crimson"
    print("[PASS] test_okuni_kumadori_face")


def test_okuni_model_materials_and_legacy():
    from src.entities.okuni_model import MATERIALS, LEGACY_MATERIALS, _smooth
    assert "kimono" in MATERIALS, "kimono missing from okuni MATERIALS"
    assert "tessen_blade" in MATERIALS, "tessen_blade missing from okuni MATERIALS"
    assert "kimono" in LEGACY_MATERIALS, "kimono missing from LEGACY_MATERIALS"
    assert "tessen_blade" in LEGACY_MATERIALS, "tessen_blade missing from LEGACY_MATERIALS"
    assert _smooth(0.0) == 0.0
    assert _smooth(1.0) == 1.0
    assert 0.0 < _smooth(0.5) < 1.0
    print("[PASS] test_okuni_model_materials_and_legacy")


def test_okuni_arms_and_dynamic_fans():
    from src.entities.okuni_model import get_arms, _hands
    class DummyContext:
        def __init__(self, pose_name="fan_strike", extra=None):
            self.facing_x = 1.0
            self.facing_y = 0.0
            self.state = "ATTACK" if pose_name == "fan_strike" else "IDLE"
            self.state_timer = 0.07
            self.walk_timer = 0.0
            self.is_moving = False
            self.pose_name = pose_name
            self.extra = extra or {}
            self.extra_props = self.extra
            self.torso_z = 0.40
            self.base_x = 0.0
            self.base_y = 0.0
            self.fx = 1.0
            self.fy = 0.0
            self.px = 0.0
            self.py = 1.0

    ctx_strike = DummyContext("fan_strike", {"pose": "fan_strike", "p": 0.5})
    left_strike, right_strike = get_arms(ctx_strike)
    assert len(left_strike) == 3, "Left hand must be (x, y, z)"
    assert len(right_strike) == 3, "Right hand must be (x, y, z)"

    ctx_mie = DummyContext("mie_pose", {"pose": "mie_pose", "p": 0.5})
    left_mie, right_mie = _hands(ctx_mie)
    # Mie pose brings right fan to chin and extends left fan
    assert right_mie != right_strike, "Right hand position must differ in mie pose"
    assert left_mie != left_strike, "Left hand position must differ in mie pose"

    ctx_dokukiri = DummyContext("dokukiri_breath", {"pose": "dokukiri_breath", "p": 0.6})
    left_doku, right_doku = _hands(ctx_dokukiri)
    assert right_doku != right_mie, "Dokukiri breath must use specialized fan breath posture"
    print("[PASS] test_okuni_arms_and_dynamic_fans")


def test_okuni_fan_strike_combat():
    from src.entities.kabuki import Kabuki
    okuni = Kabuki(10.0, 10.0)
    assert okuni.char_type == "okuni"
    assert okuni.speed == 4.6
    assert okuni.hitbox_radius == 1.45

    res = okuni.trigger_fan_strike(12.0, 10.0)
    assert res is True
    assert okuni.state == "ATTACK"
    assert okuni.hitbox_active is True
    assert okuni.hitbox_damage == 2
    assert okuni.hitbox_radius == 1.45
    print("[PASS] test_okuni_fan_strike_combat")


def test_okuni_dokukiri_cloud():
    from src.entities.kabuki import Kabuki, PoisonCloud
    from src.entities.samurai import Samurai
    okuni = Kabuki(10.0, 10.0)
    okuni.facing_x = 1.0
    okuni.facing_y = 0.0

    cloud = PoisonCloud(10.0, 10.0, 1.0, 0.0, owner=okuni)
    assert cloud.cone_length == 3.0
    assert cloud.radius == 1.35
    assert len(cloud.wisps) == 14

    dummy_target = Samurai(11.2, 10.0, name="Target")
    dummy_target.is_alive = True
    fighters = [okuni, dummy_target]
    banners = []

    cloud.update(0.016, fighters=fighters, banners=banners)
    assert dummy_target.wx > 11.2, "Dokukiri must push the target back"
    assert dummy_target.state == "STUNNED", "Dokukiri must apply stun"
    assert dummy_target.state_timer >= 0.70, "Dokukiri stun duration must be ~0.8s"
    assert getattr(dummy_target, "is_poisoned", False) is True, "Target must be poisoned"
    assert any("DOKUKIRI STUN!" in b.text for b in banners)
    print("[PASS] test_okuni_dokukiri_cloud")


def test_okuni_kawarimi_decoy():
    from src.entities.kabuki import Kabuki, OkuniDecoy
    from src.entities.samurai import Samurai
    from src.isometric.camera import Camera

    okuni = Kabuki(8.0, 8.0)
    decoys = []
    res = okuni.trigger_roll(1.0, 0.0, decoys=decoys)
    assert res is True
    assert len(decoys) == 1
    assert isinstance(decoys[0], OkuniDecoy)
    decoy = decoys[0]

    cam = Camera(800, 600)
    attacker = Samurai(8.1, 8.0, name="Attacker")
    attacker.is_alive = True
    decoy.on_hit(attacker, particles=[], banners=[], camera=cam)
    assert decoy.is_active is False
    assert attacker.state == "STUNNED"
    assert attacker.state_timer >= 0.40
    print("[PASS] test_okuni_kawarimi_decoy")


def test_okuni_corpse_tessen_decap():
    from src.entities.kabuki import Kabuki
    from src.entities.voxel_corpse import VoxelCorpse
    victim = Kabuki(10.0, 10.0)
    corpse = VoxelCorpse(victim, "TESSEN_DECAP", (1.0, 0.0))
    assert hasattr(corpse, "severed_head")
    assert hasattr(corpse, "headless_body")
    assert len(corpse.pieces) >= 2
    print("[PASS] test_okuni_corpse_tessen_decap")


def test_okuni_corpse_dokukiri_melt():
    from src.entities.kabuki import Kabuki
    from src.entities.voxel_corpse import VoxelCorpse
    victim = Kabuki(10.0, 10.0)
    corpse = VoxelCorpse(victim, "DOKUKIRI_MELT", (1.0, 0.0))
    assert getattr(corpse, "is_acid_pool", False) is True
    assert hasattr(corpse, "acid_radius")

    types = [p.piece_type for p in corpse.pieces]
    assert "melting_body" in types, "Must contain melting body piece"
    assert "bone_skull" in types, "Must contain ivory bone skull"
    assert "bone_ribs" in types, "Must contain rib cage segment"
    assert "bone_gib" in types, "Must contain bone fragments"
    print("[PASS] test_okuni_corpse_dokukiri_melt")


def test_okuni_cinematic_director_phrases():
    from src.effects.cinematic_director import CinematicDirector
    from src.combat.collision import _get_death_style_for_attacker
    from src.entities.kabuki import Kabuki
    from src.entities.samurai import Samurai

    okuni = Kabuki(0.0, 0.0)
    style_melee = _get_death_style_for_attacker(okuni, weapon="tessen")
    assert style_melee == "TESSEN_DECAP"

    style_poison = _get_death_style_for_attacker(okuni, weapon="poison")
    assert style_poison == "DOKUKIRI_MELT"

    cd = CinematicDirector()
    cd._build_kanji_overlay(death_style="TESSEN_DECAP")
    assert cd.current_kanji_text == "鉄扇斬首"
    assert "TESSEN" in cd.current_kanji_subtitle
    assert isinstance(cd.cached_kanji_surf, pygame.Surface)

    cd._build_kanji_overlay(death_style="DOKUKIRI_MELT")
    assert cd.current_kanji_text == "毒霧融骸"
    assert "DOKUKIRI" in cd.current_kanji_subtitle
    assert isinstance(cd.cached_kanji_surf, pygame.Surface)

    cd._build_kanji_overlay(death_style="OKUNI_MELT")
    assert cd.current_kanji_text == "毒霧融骸"
    assert isinstance(cd.cached_kanji_surf, pygame.Surface)

    victim = Samurai(1.0, 0.0, name="Victim")
    cd.trigger_fatal_strike(okuni, victim, "TESSEN_DECAP", (1.0, 0.0))
    assert cd.is_active is True
    print("[PASS] test_okuni_cinematic_director_phrases")


def test_okuni_pose_scripts_intro_victory():
    from src.entities.pose_scripts import sample, canonical, BEATS
    assert canonical("okuni") == "okuni"
    assert canonical("kabuki") == "okuni"

    p0 = sample("okuni", "intro", 0.15)
    assert p0.extra.get("pose") == "kumadori_steps"

    p1 = sample("okuni", "intro", 0.50)
    assert p1.extra.get("pose") == "kimono_spin"

    p2 = sample("okuni", "intro", 0.85)
    assert p2.extra.get("pose") == "tessen_cross_guard"

    v0 = sample("okuni", "victory", 0.15)
    assert v0.extra.get("pose") == "theatrical_flourish"

    v1 = sample("okuni", "victory", 0.50)
    assert v1.extra.get("pose") == "mie_pose"

    v2 = sample("okuni", "victory", 0.85)
    assert v2.extra.get("pose") == "fan_hide_smile"

    assert len(BEATS["intro"]["okuni"]) == 3
    assert len(BEATS["victory"]["okuni"]) == 3
    print("[PASS] test_okuni_pose_scripts_intro_victory")


def test_okuni_model_inspector_buttons_and_notes():
    from tools.model_inspector import CHARACTER_ANIM_BUTTONS, OVERHAUL_DE_PARA_NOTES, ModelInspector
    assert "okuni" in CHARACTER_ANIM_BUTTONS
    assert "kabuki" in CHARACTER_ANIM_BUTTONS
    assert len(CHARACTER_ANIM_BUTTONS["okuni"]) >= 10

    assert "okuni" in OVERHAUL_DE_PARA_NOTES
    assert "kabuki" in OVERHAUL_DE_PARA_NOTES
    assert len(OVERHAUL_DE_PARA_NOTES["okuni"]) >= 8

    inspector = ModelInspector(800, 600, headless=True)
    target_key = "okuni" if "okuni" in inspector.char_keys else "kabuki"
    inspector.current_char_idx = inspector.char_keys.index(target_key)
    inspector.trigger_action("FAN_STRIKE")
    frame = inspector._eval_action_frame("okuni")
    assert frame[3] == "ATTACK"
    assert frame[7].get("pose") == "fan_strike"

    inspector.trigger_action("DOKUKIRI")
    frame_d = inspector._eval_action_frame("okuni")
    assert frame_d[3] == "DOKUKIRI"
    assert frame_d[7].get("pose") == "dokukiri_breath"

    inspector.trigger_action("FINISHER_1")
    frame_f1 = inspector._eval_action_frame("okuni")
    assert frame_f1[7].get("pose") == "finisher_decap"

    inspector.trigger_action("FINISHER_2")
    frame_f2 = inspector._eval_action_frame("okuni")
    assert frame_f2[7].get("pose") == "finisher_melt"
    print("[PASS] test_okuni_model_inspector_buttons_and_notes")


def test_okuni_game_help_card():
    from src.ui.game_help import FIGHTERS_GUIDE_DATA, CHAR_KABUKI
    card = next(c for c in FIGHTERS_GUIDE_DATA if c.get("id") == CHAR_KABUKI)
    assert card["char_type"] == "okuni"
    assert "Tessen-jutsu" in card["pt"]["style"]
    assert "Dokukiri" in card["pt"]["style"]
    assert "Tessen" in card["en"]["style"]
    assert "Dokukiri" in card["en"]["style"]
    assert "Leques Tessen" in card["pt"]["keys_p1"]
    assert "Tessen Fans" in card["en"]["keys_p1"]
    print("[PASS] test_okuni_game_help_card")


if __name__ == "__main__":
    test_okuni_kumadori_face()
    test_okuni_model_materials_and_legacy()
    test_okuni_arms_and_dynamic_fans()
    test_okuni_fan_strike_combat()
    test_okuni_dokukiri_cloud()
    test_okuni_kawarimi_decoy()
    test_okuni_corpse_tessen_decap()
    test_okuni_corpse_dokukiri_melt()
    test_okuni_cinematic_director_phrases()
    test_okuni_pose_scripts_intro_victory()
    test_okuni_model_inspector_buttons_and_notes()
    test_okuni_game_help_card()
    print("\n>>> ALL 12 OKUNI OVERHAUL TESTS PASSED SUCCESSFULLY! <<<")
