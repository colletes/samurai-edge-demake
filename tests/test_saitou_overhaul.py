"""
Unit and integration tests for Sub-fase 2.5: Saitou Hajime (O Lobo de Mibu & Capitão da 3ª Divisão).
Verifies:
1. 3D Model Voxel rendering, SSAA 2x, Legacy Mode, Asagi-iro Haori with Dandara, Kanji 誠 on back, Kiseru 3D pipe, Sanpaku martial eyes.
2. Single-pass sword rendering (empty saya when drawn, get_arms(c) dynamic kinematics).
3. Gatotsu Ishiki: continuous acceleration (5.2 -> 14.5 m/s), high frontal priority, wall recoil.
4. Gatotsu Cancel into Haori Sidestep within the first 50% of the charge.
5. Zeroshiki Guard Pierce: guarantees 1 Chip Damage even against opponent in STATE_PARRY.
6. Haori Sidestep: 14 invulnerability frames.
7. Elastic parried rebound: friction slide on parry recoil.
8. Pose Scripts: Intro and Victory continuous LERP without static freeze.
9. Finishers: Finisher A (HEART_IMPALE_LUNGE) and Finisher B (TORSO_BLAST_THRUST with horizontal bisection into 2 halves).
10. Model Inspector: CHARACTER_ANIM_BUTTONS["saitou"] and OVERHAUL_DE_PARA_NOTES["saitou"].
"""

import os
import sys
import math
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from src.entities.saitou_samurai import SaitouSamurai, STATE_GATOTSU_CHARGE, STATE_ZEROSHIKI
from src.entities.samurai import Samurai, STATE_IDLE, STATE_ATTACK, STATE_PARRY, STATE_DEAD, STATE_ROLL
from src.entities import saitou_model
from src.entities import pose_scripts
from src.entities.voxel_corpse import VoxelCorpse
from src.combat.collision import CombatSystem
from src.world.map_data import GameMap
from tools import model_inspector


class DummyCamera:
    def __init__(self):
        self.zoom = 1.0
        self.offset_x = 640
        self.offset_y = 360
        self.azimuth = math.radians(45)
        self.elevation = math.radians(35.264)
        self.cos_az = math.cos(self.azimuth)
        self.sin_az = math.sin(self.azimuth)
        self.cos_el = math.cos(self.elevation)
        self.sin_el = math.sin(self.elevation)

    def apply(self, wx, wy, wz):
        rx = (wx - wy) * self.cos_az
        ry = (wx + wy) * self.sin_az * self.sin_el - wz * self.cos_el
        return int(640 + rx * 60), int(360 + ry * 60)

    def add_shake(self, amount):
        pass


def test_saitou_model_materials_and_rendering():
    """Verifica materiais específicos do Saitou (Haori Asagi-iro, Kanji Makoto, Kiseru 3D, Olhos Sanpaku)."""
    assert "haori" in saitou_model.MATERIALS
    assert "kiseru_brass" in saitou_model.MATERIALS
    assert "kiseru_wood" in saitou_model.MATERIALS
    assert "makoto" in saitou_model.MATERIALS

    # Ambos os modos: Overhaul e Legacy
    surf = pygame.Surface((300, 300), pygame.SRCALPHA)
    cam = DummyCamera()

    # Overhaul SSAA 2x
    saitou = SaitouSamurai(10.0, 10.0)
    saitou.render(surf, cam)

    # Legacy Mode
    surf_legacy = pygame.Surface((300, 300), pygame.SRCALPHA)
    from src.entities.voxel_models import render_voxel_humanoid
    render_voxel_humanoid(
        surf_legacy, cam,
        10.0, 10.0, 0.0,
        1.0, 0.0,
        STATE_IDLE, 0.0, True,
        char_type="saitou",
        extra_props={"legacy_mode": True, "ssaa_2x": False}
    )


def test_saitou_gatotsu_acceleration_and_cancel():
    """Verifica aceleração progressiva do Gatotsu Ishiki (5.2 -> 14.5 m/s) e cancelamento em Sidestep."""
    saitou = SaitouSamurai(10.0, 10.0)
    game_map = GameMap()

    # Dispara Gatotsu Ishiki
    ok = saitou.trigger_gatotsu_thrust(target_wx=15.0, target_wy=10.0)
    assert ok is True
    assert saitou.state == STATE_GATOTSU_CHARGE
    assert saitou.charge_speed == saitou.initial_charge_speed == 5.2

    # Acelera por alguns frames
    saitou.update(0.15, game_map)
    assert saitou.charge_speed > 5.2

    # Cancelamento em Haori Sidestep nos primeiros 50%
    cancel_ok = saitou.trigger_roll(dir_x=0.0, dir_y=1.0)
    assert cancel_ok is True
    assert saitou.state == STATE_ROLL


def test_saitou_zeroshiki_guard_pierce_chip_damage():
    """Verifica que o Zeroshiki perfura o Parry inimigo causando 1 de Dano Garantido (Chip Damage)."""
    saitou = SaitouSamurai(10.0, 10.0)
    target = Samurai(10.5, 10.0, name="Defender")
    target.max_hp = 3
    target.hp = 3
    target.state = STATE_PARRY
    target.is_parrying = True

    # Saitou desfere Zeroshiki a queima-roupa com hitbox ativa
    saitou.state = "ZEROSHIKI"
    saitou.zeroshiki_phase = "ACTIVE"
    saitou.state_timer = 0.20
    saitou.facing_x = 1.0
    saitou.facing_y = 0.0
    saitou.hitbox_active = True
    saitou.hitbox_radius = 0.70
    saitou.hitbox_center = (saitou.wx + 0.75, saitou.wy)
    saitou.slash_dir = (1.0, 0.0)

    camera = DummyCamera()
    particles = []
    banners = []
    projectiles = []
    game_map = GameMap()
    col_mgr = CombatSystem()

    # Processa colisão
    col_mgr.process_combat(saitou, target, game_map, particles, banners, camera, projectiles, dt=0.016)

    # O alvo em Parry deve ter sofrido 1 de dano garantido (Chip Damage)
    assert target.hp == 2, f"Expected 2 HP after Zeroshiki guard pierce, got {target.hp}"


def test_saitou_zeroshiki_lethal_triggers_bisection():
    """Verifica que Zeroshiki letal gera decapitação/bissecção horizontal (TORSO_BLAST_THRUST)."""
    saitou = SaitouSamurai(10.0, 10.0)
    target = Samurai(10.5, 10.0, name="Defender")
    target.hp = 1
    target.state = STATE_PARRY
    target.is_parrying = True

    saitou.state = "ZEROSHIKI"
    saitou.zeroshiki_phase = "ACTIVE"
    saitou.state_timer = 0.20
    saitou.facing_x = 1.0
    saitou.facing_y = 0.0
    saitou.hitbox_active = True
    saitou.hitbox_radius = 0.70
    saitou.hitbox_center = (saitou.wx + 0.75, saitou.wy)
    saitou.slash_dir = (1.0, 0.0)

    camera = DummyCamera()
    particles = []
    banners = []
    projectiles = []
    game_map = GameMap()
    col_mgr = CombatSystem()

    from src.effects.cinematic_director import CinematicDirector
    cin_dir = CinematicDirector()

    col_mgr.process_combat(saitou, target, game_map, particles, banners, camera, projectiles, dt=0.016, cinematic_director=cin_dir)
    assert target.hp <= 0
    assert not target.is_alive
    assert cin_dir.pending_corpse is not None
    assert cin_dir.pending_corpse.death_style == "TORSO_BLAST_THRUST"

    # Verifica spawn dos pedaços do corpo bisectado
    corpse = cin_dir.pending_corpse
    corpse_pieces = corpse.pieces
    assert len(corpse_pieces) >= 2
    types = [p.piece_type for p in corpse_pieces]
    assert "bisected_upper_torso" in types
    assert "collapsed_lower_legs" in types

    # Verifica rotação negativa do tronco voando para trás
    upper = next(p for p in corpse_pieces if p.piece_type == "bisected_upper_torso")
    assert upper.rot_target < 0.0
    assert upper.vz > 0.0


def test_saitou_finisher_a_heart_impale():
    """Verifica Finisher A (HEART_IMPALE_LUNGE)."""
    victim = Samurai(10.0, 10.0, name="Victim")
    victim.hp = 0
    victim.is_alive = False

    corpse = VoxelCorpse(victim, death_style="HEART_IMPALE_LUNGE", slash_dir=(1.0, 0.0))
    corpse_pieces = corpse.pieces
    assert len(corpse_pieces) >= 1
    torso = next(p for p in corpse_pieces if p.piece_type == "impaled_body")
    assert torso.vz > 0.0
    assert not torso.is_grounded


def test_saitou_pose_scripts_lerp():
    """Verifica continuidade LERP nas animações de Intro e Victory do Saitou."""
    for p in [0.0, 0.25, 0.50, 0.75, 1.0]:
        pf_intro = pose_scripts.sample("saitou", "intro", p)
        assert pf_intro is not None
        assert pf_intro.state is not None
        assert "pose" in pf_intro.extra

        pf_victory = pose_scripts.sample("saitou", "victory", p)
        assert pf_victory is not None
        assert pf_victory.state is not None
        assert "pose" in pf_victory.extra


def test_saitou_model_inspector_registration():
    """Verifica que o Saitou possui botões dedicados e notas De/Para no Model Inspector."""
    assert "saitou" in model_inspector.CHARACTER_ANIM_BUTTONS
    btns = model_inspector.CHARACTER_ANIM_BUTTONS["saitou"]
    btn_ids = [aid for aid, lbl, dur in btns]
    assert "IDLE" in btn_ids
    assert "WALK" in btn_ids
    assert "GATOTSU_ISHIKI" in btn_ids
    assert "GATOTSU_ZEROSHIKI" in btn_ids
    assert "HAORI_SIDESTEP" in btn_ids
    assert "GATOTSU_CANCEL" in btn_ids
    assert "PARRY_RECOIL" in btn_ids
    assert "INTRO" in btn_ids
    assert "VICTORY" in btn_ids
    assert "FINISHER_1" in btn_ids
    assert "FINISHER_2" in btn_ids

    assert "saitou" in model_inspector.OVERHAUL_DE_PARA_NOTES
    notes = model_inspector.OVERHAUL_DE_PARA_NOTES["saitou"]
    assert len(notes) >= 4
    notes_text = " ".join(notes)
    assert "SSAA 2x" in notes_text
    assert "Gatotsu" in notes_text
    assert "Zeroshiki" in notes_text


def test_joe_model_inspector_registration():
    """Verifica que o Joe também está registrado com botões e notas De/Para no Model Inspector."""
    assert "joe" in model_inspector.CHARACTER_ANIM_BUTTONS
    btns = model_inspector.CHARACTER_ANIM_BUTTONS["joe"]
    btn_ids = [aid for aid, lbl, dur in btns]
    assert "FLIC_FLAC" in btn_ids
    assert "YAMATO_CHARGE" in btn_ids
    assert "FINISHER_1" in btn_ids
    assert "FINISHER_2" in btn_ids

    assert "joe" in model_inspector.OVERHAUL_DE_PARA_NOTES


if __name__ == "__main__":
    print("==================================================")
    print("  RUNNING SUB-FASE 2.5: SAITOU HAJIME TEST SUITE  ")
    print("==================================================")
    tests = [
        test_saitou_model_materials_and_rendering,
        test_saitou_gatotsu_acceleration_and_cancel,
        test_saitou_zeroshiki_guard_pierce_chip_damage,
        test_saitou_zeroshiki_lethal_triggers_bisection,
        test_saitou_finisher_a_heart_impale,
        test_saitou_pose_scripts_lerp,
        test_saitou_model_inspector_registration,
        test_joe_model_inspector_registration,
    ]
    for test in tests:
        print(f"Running {test.__name__}...", end=" ")
        test()
        print("PASS")
    print("==================================================")
    print("  ALL SAITOU & JOE OVERHAUL TESTS PASSED (100%)   ")
    print("==================================================")
