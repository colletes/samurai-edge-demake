"""
Testes automatizados de validação da Fase 4: Grandes Revamps
1. Rework Ainu de Aoi (Combo Adaptativo + Lança 2HP + Makiri 1HP + Harponete Hold & Release + Bear Trap Crawl)
2. Deslize Espectral Alucard de Ichi (Velocidade 10.8, Desaceleração Contínua & Zanzou Afterimages)
3. Revamp Agressivo de Gashadokuro (+25% velocidade, 1.6s transição, chifres obsidian & olhos espectrais)
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
pygame.display.set_mode((800, 600), pygame.NOFRAME)

from src.entities.aoi import AoiHuntress
from src.entities.ichi import IchiBlade
from src.entities.projectile import AoiHarpoonProjectile, BearTrapProjectile
from src.entities.voxel_corpse import VoxelCorpse
from src.combat.collision import CombatSystem
from src.isometric.camera import Camera
from src.effects.cinematic_director import CinematicDirector
from src.entities.boss_oni import BOSS_TUNING
from src.entities import boss_model, boss_head


def test_aoi_spear_damage_and_combo():
    """Valida o combo adaptativo de Aoi: 1º golpe Lança (2HP), 2º golpe Makiri (1HP)."""
    aoi = AoiHuntress(5.0, 5.0)
    particles = []
    
    # 1º golpe: Lança Op
    success1 = aoi.trigger_spear_thrust(particles=particles)
    assert success1 is True
    assert aoi.hitbox_active is True
    assert aoi.hitbox_damage == 2
    assert aoi.attack_type == "spear"
    assert aoi.combo_step == 1
    assert aoi.combo_window > 0.0

    # Atualiza o fim da execução da estocada
    aoi.update(0.20)
    assert aoi.state == "RECOVERY"
    assert aoi.combo_step == 1
    assert aoi.combo_window > 0.0

    # 2º golpe dentro da janela de combo: aciona a faca Makiri
    success2 = aoi.trigger_attack(particles=particles)
    assert success2 is True
    assert aoi.hitbox_active is True
    assert aoi.hitbox_damage == 1
    assert aoi.attack_type == "makiri"
    assert abs(aoi.state_timer - 0.14) < 0.02
    
    props = aoi.get_extra_props()
    assert props.get("pose") == "makiri_slash"
    assert props.get("is_makiri") is True
    assert aoi.combo_step == 0
    print("✓ test_aoi_spear_damage_and_combo passou com sucesso!")


def test_aoi_hold_release_harpoon_and_trap():
    """Valida a mecânica de Hold & Release de Aoi: Tap -> Trap, Hold -> Harpoon."""
    aoi = AoiHuntress(5.0, 5.0)
    projectiles = []
    particles = []
    banners = []

    # 1. Tap rápido (< 0.24s) -> Planta Bear Trap
    aoi.start_harpoon_charge(6.0, 5.0)
    assert aoi.is_charging_harpoon is True
    aoi.update_harpoon_charge(0.08, 6.0, 5.0)
    aoi.release_harpoon_or_trap(projectiles=projectiles, particles=particles, banners=banners)
    assert aoi.is_charging_harpoon is False
    assert len(projectiles) == 1
    assert isinstance(projectiles[0], BearTrapProjectile)

    # 2. Hold prolongado (>= 0.24s) -> Arremessa Harponete
    aoi.update(0.25)
    aoi.state = "IDLE"
    aoi.trap_timer = 0.0
    projectiles.clear()
    success_charge = aoi.start_harpoon_charge(7.0, 5.0)
    assert success_charge is True
    aoi.update_harpoon_charge(0.28, 7.0, 5.0)
    aoi.release_harpoon_or_trap(projectiles=projectiles, particles=particles, banners=banners)
    assert aoi.is_charging_harpoon is False
    assert len(projectiles) == 1
    assert isinstance(projectiles[0], AoiHarpoonProjectile)
    harpoon = projectiles[0]
    assert harpoon.damage == 2
    assert harpoon.speed == 16.5
    assert harpoon.is_active is True
    print("✓ test_aoi_hold_release_harpoon_and_trap passou com sucesso!")


def test_aoi_harpoon_combat_collision_and_parry():
    """Valida a colisão do Harponete de Aoi no sistema de combate (Dano 2, Parry, Fatalidade)."""
    combat = CombatSystem()
    camera = Camera(800, 600)
    director = CinematicDirector()
    particles = []
    banners = []

    aoi = AoiHuntress(3.0, 5.0)
    rival = AoiHuntress(4.5, 5.0)
    rival.hp = 2

    harpoon = AoiHarpoonProjectile(4.2, 5.0, 0.65, 1.0, 0.0, owner=aoi)
    projectiles = [harpoon]

    # Rival em parry -> bloqueia sem sofrer dano
    rival.state = "PARRY"
    combat.process_combat(aoi, rival, None, particles, banners, camera, projectiles, dt=0.016, cinematic_director=director)
    assert harpoon.is_active is False
    assert rival.hp == 2
    assert rival.is_alive is True

    # Rival desprotegido -> sofre 2 de dano e morre
    rival.state = "IDLE"
    harpoon2 = AoiHarpoonProjectile(4.3, 5.0, 0.65, 1.0, 0.0, owner=aoi)
    projectiles = [harpoon2]
    winner = combat.process_combat(aoi, rival, None, particles, banners, camera, projectiles, dt=0.016, cinematic_director=director)
    assert winner == "P1_WINS"
    assert rival.is_alive is False
    assert rival.hp <= 0
    print("✓ test_aoi_harpoon_combat_collision_and_parry passou com sucesso!")


def test_aoi_bear_trap_fatal_crawl():
    """Valida o rastejo desesperado com amputação na armadilha de urso (TRAP_AND_EXECUTE)."""
    victim = AoiHuntress(6.0, 6.0)
    corpse = VoxelCorpse(victim, "TRAP_AND_EXECUTE", (1.0, 0.0))
    
    assert getattr(corpse, "has_bear_trap_clamped", False) is True
    assert getattr(corpse, "is_bear_trap_crawl", False) is True
    assert hasattr(corpse, "severed_legs")
    assert hasattr(corpse, "crawling_upper")
    assert corpse.trap_x == 6.0
    assert corpse.trap_y == 6.0

    initial_x = corpse.wx
    # Atualiza o rastejo por 1.0s
    for _ in range(60):
        corpse.update(1.0 / 60.0)

    # O tronco rastejou para a frente puxado pelos braços
    assert corpse.wx > initial_x
    assert len(corpse.crawl_trail) > 1

    # Após término da duração (2.8s), o tronco colapsa
    for _ in range(120):
        corpse.update(1.0 / 60.0)

    assert corpse.crawl_time >= corpse.crawl_duration
    assert abs(corpse.crawling_upper.rot_angle - 88.0) < 1.0
    print("✓ test_aoi_bear_trap_fatal_crawl passou com sucesso!")


def test_ichi_alucard_dash_and_zanzou():
    """Valida o deslize fluido Alucard de Ichi (10.8 velocidade, zanzou afterimages)."""
    ichi = IchiBlade(4.0, 4.0)
    particles = []
    
    success = ichi.trigger_cane_slip(1.0, 0.0, particles=particles)
    assert success is True
    assert ichi.state == "ROLL"
    assert ichi.roll_speed == 10.8
    assert ichi.roll_duration == 0.32
    assert len(ichi.zanzou_ghosts) >= 1

    # Atualiza meio segundo de esquiva gerando afterimages
    for _ in range(10):
        ichi.update(0.02, particles=particles)
    
    assert len(ichi.zanzou_ghosts) >= 3
    for g in ichi.zanzou_ghosts:
        assert "wx" in g and "wy" in g and "alpha" in g

    # Renderiza sem exceções
    surf = pygame.Surface((400, 300))
    cam = Camera(400, 300)
    ichi.render(surf, cam)

    # Esmaecimento das afterimages com o tempo
    for _ in range(60):
        ichi.update(0.016)
    
    assert len(ichi.zanzou_ghosts) == 0
    print("✓ test_ichi_alucard_dash_and_zanzou passou com sucesso!")


def test_boss_oni_aggressive_revamp():
    """Valida o revamp agressivo de Oni Gashadokuro (+25% velocidade, 1.6s transformação, cores)."""
    # 1. Tuning de combate 25% mais rápido
    assert BOSS_TUNING["p1_walk_speed"] == 2.75
    assert BOSS_TUNING["p1_stomp_warn"] == 0.52
    assert BOSS_TUNING["p2_speed"] == 9.6
    assert BOSS_TUNING["p2_telegraph"] == 0.48
    assert BOSS_TUNING["p3_speed"] == 8.5
    assert BOSS_TUNING["p4_warn"] == 0.60
    assert BOSS_TUNING["p5_warns"] == (0.42, 0.34, 0.30)

    # 2. Transição acelerada para 1.6s
    assert boss_model.TRANSFORM_TIME == 1.6

    # 3. Chifres obsidian com estrias carmesim e olhos espectrais
    assert boss_head.HORN == (28, 22, 26)
    assert boss_head.HORN_RIDGE == (165, 30, 36)
    assert boss_head.EYE_CORE == (255, 32, 24)
    assert boss_head.EYE_SPARK == (255, 230, 90)
    print("✓ test_boss_oni_aggressive_revamp passou com sucesso!")


if __name__ == "__main__":
    test_aoi_spear_damage_and_combo()
    test_aoi_hold_release_harpoon_and_trap()
    test_aoi_harpoon_combat_collision_and_parry()
    test_aoi_bear_trap_fatal_crawl()
    test_ichi_alucard_dash_and_zanzou()
    test_boss_oni_aggressive_revamp()
    print("\n🎉 TODOS OS TESTES DA FASE 4 FORAM APROVADOS COM 100% DE SUCESSO!")
