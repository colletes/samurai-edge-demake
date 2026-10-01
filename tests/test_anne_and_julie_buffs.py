import math
import sys
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()

from src.entities.pirate import PirateSwordswoman
from src.entities.musketeer import Musketeer
from src.entities.red_samurai import RedSamurai
from src.world.map_data import GameMap
from src.combat.collision import CombatSystem
from src.isometric.camera import Camera
from src.entities.projectile import MusketBulletProjectile, KyudoArrowProjectile

def test_anne_cleave_and_cannon():
    anne = PirateSwordswoman(10.0, 10.0)
    init_x = anne.wx

    # 1. Teste do avanço vigoroso do alfanje
    anne.trigger_cutlass_cleave(15.0, 10.0)
    assert anne.state == "ATTACK"
    assert anne.hitbox_radius == 1.55
    assert anne.wx > init_x + 0.60, f"Anne devia ter avançado >= 0.60m, avançou {anne.wx - init_x}"
    print("[PASS] Teste 1: Alfanje de Anne possui avanço frontal de 0.65m e hitbox 1.55m")

    # 2. Teste do disparo rápido do canhão (Tap / Quick Cannon)
    projectiles = []
    assert anne.cannon_cooldown_timer == 4.5  # Começa com cooldown no início do round
    anne.cannon_cooldown_timer = 0.0
    anne.trigger_quick_cannon(14.0, 10.0, projectiles)
    assert len(projectiles) == 1
    assert anne.cannon_cooldown_timer == 4.5
    assert projectiles[0].owner == anne
    print("[PASS] Teste 2: Quick Cannon de Anne dispara projétil naval com cooldown de 4.5s")

def test_anne_dash_and_deflection():
    anne = PirateSwordswoman(10.0, 10.0)
    opp = RedSamurai(10.8, 10.0)
    g_map = GameMap()
    particles = []

    # 1. Teste do Black Powder Dash causando stun e lentidão
    anne.trigger_roll(1.0, 0.0, particles)
    assert anne.state == "ROLL"
    assert anne.is_invulnerable_dodge == True

    anne.update(0.10, g_map, particles, opponent=opp)
    assert opp.state == "STUNNED"
    assert anne.dash_has_hit == True
    print("[PASS] Teste 3: Black Powder Dash de Anne aplica stun e repulsão no oponente")

    # 2. Teste de Cutlass Deflection com margem ampliada
    combat = CombatSystem()
    cam = Camera(10.0, 10.0)
    anne.state = "ATTACK"
    anne.hitbox_active = True
    anne.hitbox_center = (10.9, 10.0)
    anne.hitbox_radius = 1.55

    arrow = KyudoArrowProjectile(11.5, 10.0, 0.5, -1.0, 0.0, owner=opp)
    projs = [arrow]
    combat.process_combat(anne, opp, g_map, particles, [], cam, projs, 0.016)
    assert arrow.is_active == False
    print("[PASS] Teste 4: Corte de Alfanje de Anne deflete flechas e projéteis inimigos")

def test_julie_fleche_and_recovery():
    julie = Musketeer(10.0, 10.0)
    julie.trigger_fleche_thrust(15.0, 10.0)
    assert julie.state == "ATTACK"
    assert julie.hitbox_radius == 0.70

    g_map = GameMap()
    julie.update(0.21, g_map)
    assert julie.state == "RECOVERY"
    assert math.isclose(julie.state_timer, 0.18, abs_tol=0.03)
    print("[PASS] Teste 5: Fleche Thrust de Julie possui hitbox 0.70m e recovery reduzido para 0.18s")

def test_julie_cape_deflection_and_coup_de_pied():
    julie = Musketeer(10.0, 10.0)
    opp = RedSamurai(11.2, 10.0)
    particles = []
    banners = []
    g_map = GameMap()
    combat = CombatSystem()
    cam = Camera(10.0, 10.0)

    # 1. Teste do Coup de Pied / Stagger
    julie.trigger_cape_flourish(12.0, 10.0, opponent=opp, particles=particles, banners=banners)
    assert julie.state == "CAPE_FLOURISH"
    assert opp.state == "STUNNED"
    print("[PASS] Teste 6: Cape Flourish a curta distância aplica Coup de Pied com stagger")

    # 2. Teste de Cape Deflection de projéteis frontais
    bullet = MusketBulletProjectile(11.4, 10.0, 0.45, -1.0, 0.0, owner=opp)
    projs = [bullet]
    combat.process_combat(julie, opp, g_map, particles, banners, cam, projs, 0.016)
    assert bullet.is_active == False
    print("[PASS] Teste 7: Cape Deflection anula balas e projéteis inimigos")

def test_julie_pocket_flintlock():
    julie = Musketeer(10.0, 10.0)
    julie.flintlock_timer = 0.0  # Pronto para disparo
    projs = []
    particles = []

    julie.trigger_flintlock_shot(15.0, 10.0, projs, particles)
    assert len(projs) == 1
    assert isinstance(projs[0], MusketBulletProjectile)
    assert projs[0].owner == julie
    assert julie.flintlock_timer == 4.5
    print("[PASS] Teste 8: Pocket Flintlock de Julie dispara projétil de chumbo à distância")

def test_julie_cape_deflects_frontal_but_not_rear():
    """Julie: Cape deflecte projéteis frontais mas NÃO projéteis pelas costas (cone frontal)."""
    g_map = GameMap()
    pygame.display.set_mode((800, 600), pygame.NOFRAME)
    from src.isometric.camera import Camera as IsoCamera
    cam = IsoCamera(800, 600)
    combat = CombatSystem()

    # --- Projétil frontal (deve ser defletido) ---
    julie_front = Musketeer(10.0, 10.0)
    julie_front.facing_x, julie_front.facing_y = 1.0, 0.0  # Olhando para +X
    julie_front.state = "CAPE_FLOURISH"
    julie_front.is_invulnerable_dodge = True

    opponent = RedSamurai(15.0, 10.0)
    bullet_front = MusketBulletProjectile(
        wx=10.8, wy=10.0, wz=0.5,
        dir_x=-1.0, dir_y=0.0,  # Vindo de +X (frontal)
        owner=opponent
    )
    projs_front = [bullet_front]
    particles, banners = [], []
    combat.process_combat(julie_front, opponent, g_map, particles, banners, cam, projs_front, 0.016)
    assert not bullet_front.is_active, "Projétil FRONTAL deve ser defletido pela capa!"

    # --- Projétil pelas costas (NÃO deve ser defletido) ---
    julie_rear = Musketeer(10.0, 10.0)
    julie_rear.facing_x, julie_rear.facing_y = 1.0, 0.0  # Olhando para +X
    julie_rear.state = "CAPE_FLOURISH"
    julie_rear.is_invulnerable_dodge = True

    opponent2 = RedSamurai(5.0, 10.0)
    bullet_rear = MusketBulletProjectile(
        wx=9.2, wy=10.0, wz=0.5,
        dir_x=1.0, dir_y=0.0,  # Vindo de -X (costas)
        owner=opponent2
    )
    projs_rear = [bullet_rear]
    particles2, banners2 = [], []
    combat.process_combat(julie_rear, opponent2, g_map, particles2, banners2, cam, projs_rear, 0.016)
    assert bullet_rear.is_active, "Projétil pelas COSTAS NÃO deve ser defletido pela capa!"

    print("[PASS] Teste 9: Deflexão frontal de capa: frente defletida, costas passa através")


if __name__ == "__main__":
    test_anne_cleave_and_cannon()
    test_anne_dash_and_deflection()
    test_julie_fleche_and_recovery()
    test_julie_cape_deflection_and_coup_de_pied()
    test_julie_pocket_flintlock()
    test_julie_cape_deflects_frontal_but_not_rear()
    print("\nTODOS OS 9 TESTES DE ANNE E JULIE PASSARAM COM SUCESSO!")

