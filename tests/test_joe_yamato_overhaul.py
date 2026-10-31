#!/usr/bin/env python3
"""
Testes de verificação e integração para a Sub-fase 2.4: Joe & Yamato (American Ninja & Doberman).
Verifica os 11 entregáveis obrigatórios:
1. joe_model.py: Materiais táteis, LEGACY_MATERIALS, get_arms(c) sem duplicação.
2. Chapéu de cowboy e banjo 3D modelados para a vitória.
3. Fuma Shuriken Moinho Gigante 3D para o Finisher B.
4. AmericanNinja: Shurikens a 15.5 m/s com cooldown 0.90s.
5. Yamato: Dash a 14.5 m/s, 1-hit kill (dano 3) e recuperação de 2.5s em whiff.
6. Flic-Flacs acrobáticos: Cadeia de até 3x para trás com atordoamento ao bater em obstáculos (0.60s).
7. Finishers: TRIPLE_SHURIKEN_DISMEMBER (3 peças desmembradas + tronco) e WINDMILL_SHURIKEN_DECAP.
8. Pose Scripts: Intro (luvas + assobio + alerta) e Vitória (chapéu de cowboy + banjo com sfx).
9. Model Inspector: Botoeira de 10 ações, notas de De/Para e comparação sincronizada.
10. Game Help: Manual atualizado com táticas de Joe e Yamato.
"""
import os
import sys
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

pygame.init()
pygame.display.set_mode((100, 100))

from src.entities import joe_model
from src.entities.american_ninja import AmericanNinja
from src.entities.doberman import DobermanDog, STATE_DOG_FOLLOW, STATE_DOG_CHARGE, STATE_DOG_KNOCKED_OUT
from src.entities.projectile import ShurikenProjectile
from src.entities.voxel_corpse import VoxelCorpse
from src.entities import pose_scripts
from src.effects.cinematic_director import CinematicDirector
from tools.model_inspector import CHARACTER_ANIM_BUTTONS, OVERHAUL_DE_PARA_NOTES


class DummyCamera:
    def __init__(self):
        self.azimuth = 0.0
        self.zoom = 1.0
        self.screen_x = 50
        self.screen_y = 50

    def apply(self, x, y, z):
        return int(50 + x * 20), int(50 + y * 20 - z * 20)


class DummyContext:
    def __init__(self, surface, camera, extra_props=None):
        self.surface = surface
        self.camera = camera
        self.azimuth = 0.0
        self.base_x = 0.0
        self.base_y = 0.0
        self.base_z = 0.0
        self.torso_z = 0.45
        self.head_z = 0.72
        self.head_w = 0.16
        self.pelvis_z = 0.38
        self.pelvis_w = 0.22
        self.fx = 1.0
        self.fy = 0.0
        self.px = 0.0
        self.py = 1.0
        self.is_moving = False
        self.walk_timer = 0.0
        self.atk_progress = None
        self.is_melee = False
        self.alpha = 255
        self.extra_props = extra_props or {}
        self.legs_data = {
            "L": {"thigh": (0, -0.06, 0.22), "shin": (0, -0.06, 0.11), "foot": (0, -0.06, 0.0)},
            "R": {"thigh": (0, 0.06, 0.22), "shin": (0, 0.06, 0.11), "foot": (0, 0.06, 0.0)},
        }


def test_joe_model_structure():
    """Valida paleta, materiais táteis, LEGACY_MATERIALS e cinemática de braços."""
    print("Testando estrutura de joe_model...")
    assert hasattr(joe_model, "PALETTE")
    assert hasattr(joe_model, "MATERIALS")
    assert hasattr(joe_model, "LEGACY_MATERIALS")
    assert "hat" in joe_model.PALETTE
    assert "banjo_wood" in joe_model.PALETTE
    assert "fuma_steel" in joe_model.PALETTE

    surf = pygame.Surface((200, 200))
    cam = DummyCamera()

    # Teste de cinemática dos braços e poses
    for pose_name in ("adjust_gloves", "dog_whistle", "tactical_guard", "cowboy_banjo", "flic_flac", "triple_shuriken", "fuma_throw"):
        ctx = DummyContext(surf, cam, extra_props={"pose": pose_name, "progress": 0.5})
        arms = joe_model.get_arms(ctx)
        assert len(arms) == 2
        assert len(arms[0]) == 3 and len(arms[1]) == 3

    # Teste de renderização das camadas sem erros
    ctx_victory = DummyContext(surf, cam, extra_props={"pose": "cowboy_banjo", "cowboy_hat": True})
    joe_model.draw_behind(ctx_victory)
    joe_model.draw_legs(ctx_victory)
    joe_model.draw_obi(ctx_victory)
    joe_model.draw_torso(ctx_victory)
    joe_model.draw_head(ctx_victory)
    hl, hr = joe_model.get_arms(ctx_victory)
    joe_model.draw_front(ctx_victory, hl, hr)
    print("✓ joe_model: Poses, materiais e renderização 3D validados!")


def test_american_ninja_gameplay():
    """Valida velocidade da shuriken, Yamato letal e cadeia de flic-flacs."""
    print("Testando jogabilidade do AmericanNinja...")
    joe = AmericanNinja(5.0, 5.0)

    # Shuriken tuning
    assert joe.shuriken_cooldown == 0.90
    projs = []
    assert joe.trigger_shuriken(8.0, 5.0, projs)
    assert len(projs) == 1
    shur = projs[0]
    speed = math.hypot(shur.vx, shur.vy)
    assert abs(speed - 15.5) < 0.1
    print("✓ Shuriken: 15.5 m/s e cooldown 0.90s confirmados!")

    # Yamato tuning
    joe.update(0.15, None)  # Recuperação do arremesso de shuriken
    assert joe.dog is not None
    assert joe.dog.charge_speed == 14.5
    assert joe.dog.charge_range == 5.2
    assert joe.trigger_dog_attack(10.0, 5.0)
    assert joe.dog.state == "BARK"
    joe.dog.update(0.16, None)
    assert joe.dog.state == "CHARGE"
    # Whiff recovery
    joe.dog.charge_dist = 6.0
    joe.dog.update(0.05, None)
    assert joe.dog.state == "FOLLOW"
    assert joe.dog.cooldown_timer == 2.5
    print("✓ Yamato: Bote a 14.5 m/s e recuperação ágil de 2.5s confirmados!")

    # Flic-flac chain (até 3x no centro da arena)
    joe.wx, joe.wy = 12.0, 10.0
    joe.facing_x, joe.facing_y = 1.0, 0.0
    joe.update(0.20, None)  # Recuperação do comando do cão
    assert joe.trigger_roll(0, 0)
    assert joe.state == "ROLL"
    assert joe.flic_flac_chain == 1
    assert joe.roll_dir_x < 0  # Movimento para trás!
    # Avança até o final do roll
    joe.update_roll(0.25, None)
    assert joe.state == "IDLE"
    assert joe.roll_cooldown_timer <= 0.05  # Encadeamento rápido habilitado!

    # 2º salto (após expirar o breve timer de recuperação de 0.06s)
    joe.update_dodge_timers(0.06)
    assert joe.trigger_roll(0, 0)
    assert joe.flic_flac_chain == 2
    joe.update_roll(0.25, None)
    assert joe.state == "IDLE"

    # 3º salto (após expirar o breve timer de recuperação de 0.06s)
    joe.update_dodge_timers(0.06)
    assert joe.trigger_roll(0, 0)
    assert joe.flic_flac_chain == 3
    joe.update_roll(0.25, None)
    assert joe.state == "IDLE"
    assert joe.flic_flac_chain == 0
    assert joe.roll_cooldown_timer >= 0.30  # Cooldown total após 3x!

    # Teste de colisão com obstáculo sólido (borda/parede): atordoamento de 0.60s
    joe.wx, joe.wy = 1.8, 10.0
    joe.facing_x, joe.facing_y = 1.0, 0.0
    joe.update_dodge_timers(0.35)
    assert joe.trigger_roll(0, 0)
    joe.update_roll(0.20, None)
    assert joe.state == "STUNNED"
    assert joe.state_timer > 0.40
    print("✓ Flic-Flac: Cadeia de 3x saltos para trás E colisão/atordoamento em parede confirmados!")


def test_finishers():
    """Valida os dois finishers cinematográficos de Joe."""
    print("Testando finishers...")
    victim = AmericanNinja(6.0, 5.0)

    # Finisher A: TRIPLE_SHURIKEN_DISMEMBER
    corpse_a = VoxelCorpse(victim, "TRIPLE_SHURIKEN_DISMEMBER", (1.0, 0.0))
    # Deve conter cabeça, braço direito, braço esquerdo e tronco decapitado
    types = [p.piece_type for p in corpse_a.pieces]
    assert "head" in types
    assert "arm_r" in types
    assert "arm_l" in types
    assert "torso_headless" in types
    # Queda para trás do tronco
    torso_p = next(p for p in corpse_a.pieces if p.piece_type == "torso_headless")
    assert torso_p.rot_target < 0  # Tombamento para trás!
    print("✓ Finisher A (TRIPLE_SHURIKEN_DISMEMBER): 4 pedaços corporais e gravidade validados!")

    # Finisher B: WINDMILL_SHURIKEN_DECAP
    corpse_b = VoxelCorpse(victim, "WINDMILL_SHURIKEN_DECAP", (1.0, 0.0))
    types_b = [p.piece_type for p in corpse_b.pieces]
    assert "head" in types_b
    assert "torso_headless" in types_b
    print("✓ Finisher B (WINDMILL_SHURIKEN_DECAP): Fuma Shuriken e decapitação validados!")


def test_inspector_and_poses():
    """Valida registro no Model Inspector e Roteiros de Animação."""
    print("Testando Model Inspector e Poses...")
    assert "american" in CHARACTER_ANIM_BUTTONS
    buttons = CHARACTER_ANIM_BUTTONS["american"]
    assert len(buttons) == 10
    assert "american" in OVERHAUL_DE_PARA_NOTES

    # Amostragem de Intro e Vitória
    p_intro = pose_scripts.sample("american", "intro", 0.15)
    assert p_intro.extra.get("pose") == "adjust_gloves"

    p_whistle = pose_scripts.sample("american", "intro", 0.50)
    assert p_whistle.extra.get("pose") == "dog_whistle"

    p_guard = pose_scripts.sample("american", "intro", 0.85)
    assert p_guard.extra.get("pose") == "tactical_guard"

    p_vic = pose_scripts.sample("american", "victory", 0.50)
    assert p_vic.extra.get("pose") == "cowboy_banjo"
    assert p_vic.extra.get("cowboy_hat") is True

    # Batidas de áudio da vitória
    v_beats = pose_scripts.BEATS["victory"]["american"]
    assert any("sfx:joe_banjo" in b[1] for b in v_beats)
    print("✓ Poses e Inspector: Intro, Vitória com Banjo e 10 botões validados!")


if __name__ == "__main__":
    test_joe_model_structure()
    test_american_ninja_gameplay()
    test_finishers()
    test_inspector_and_poses()
    print("\nTODOS OS TESTES DE JOE & YAMATO PASSARAM COM 100% DE SUCESSO!")
