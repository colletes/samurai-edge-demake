"""
Testes automatizados dos kits de combate e arenas do Ciclo 5: Daiki (Yamabushi) e Aoi (Caçadora Ainu).
"""
import os
import sys
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
pygame.init()

from src.config import CHAR_DAIKI, CHAR_AOI, ARENA_SACRED_PINES, ARENA_EZO_TUNDRA
from src.entities.daiki import DaikiPilgrim
from src.entities.aoi import AoiHuntress
from src.entities.projectile import BearTrapProjectile, ShurikenProjectile
from src.combat.collision import CombatSystem
from src.world.arenas import create_arena, ARENA_SPECS
from src.roster import PLAYABLE_FIGHTERS, ARCADE_TIER_ORDER


def test_daiki_combat_kit():
    print("Iniciando testes do kit de combate de Daiki...")
    d = DaikiPilgrim(10.0, 10.0)
    assert d.name == "Daiki"
    assert d.char_type == "daiki"
    assert d.hp == 2
    assert d.can_parry is True

    # 1. Ataque Primário: Bastão Bō
    res = d.trigger_bo_strike(12.0, 10.0)
    assert res is True
    assert d.state == "ATTACK"
    assert d.hitbox_active is True
    assert d.hitbox_damage == 2
    assert d.hitbox_radius == 1.25
    assert d.hitbox_center[0] > 10.0

    # 2. Ação Secundária: Salto com Vara (Pole Vault)
    d.state = "IDLE"
    d.hitbox_active = False
    particles = []
    banners = []
    dummy_opponent = AoiHuntress(13.0, 10.0)
    res_leap = d.trigger_pole_vault(12.0, 10.0, particles=particles, banners=banners, opponent=dummy_opponent)
    assert res_leap is True
    assert d.state == "POLE_VAULT"
    assert d.vault_timer > 0

    # Testar deflexão de projétil durante subida
    incoming_shuriken = ShurikenProjectile(d.wx + 0.3, d.wy, 0.4, -1.0, 0.0, dummy_opponent)
    projectiles = [incoming_shuriken]
    d.update(0.05, projectiles=projectiles, banners=banners)
    assert incoming_shuriken.dir_x > 0.0  # Defletido na direção contrária!
    assert incoming_shuriken.owner == d
    print("  -> Daiki Bōjutsu & Salto com Vara: 100% OK!")


def test_aoi_combat_kit():
    print("Iniciando testes do kit de combate de Aoi...")
    a = AoiHuntress(10.0, 10.0)
    assert a.name == "Aoi"
    assert a.char_type == "aoi"
    assert a.hp == 2
    assert a.can_parry is True

    # 1. Ataque Primário: Estocada de Lança Op
    res = a.trigger_spear_thrust(12.0, 10.0)
    assert res is True
    assert a.state == "ATTACK"
    assert a.hitbox_active is True
    assert a.hitbox_damage == 2
    assert a.hitbox_radius == 1.05
    assert a.hitbox_center[0] > 10.0

    # 2. Ação Secundária: Armadilha de Urso
    a.state = "IDLE"
    a.hitbox_active = False
    projectiles = []
    particles = []
    banners = []
    res_trap = a.trigger_bear_trap(11.5, 10.0, projectiles=projectiles, particles=particles, banners=banners)
    assert res_trap is True
    assert len(projectiles) == 1
    trap = projectiles[0]
    assert isinstance(trap, BearTrapProjectile)
    assert trap.is_active is True
    assert trap.owner == a

    # Testar ativação da armadilha por pisão do oponente
    opp = DaikiPilgrim(trap.wx, trap.wy)
    opp.hp = 1  # Deixa com 1 HP para verificar dano letal ao pisar
    cs = CombatSystem()
    game_map = create_arena("ezo_tundra")
    cs.process_combat(opp, a, game_map, particles, banners, camera=None, projectiles=[trap], dt=0.016)
    assert opp.is_alive is False  # Dano letal por contato!
    assert any("BEAR TRAP" in str(b.text) for b in banners)
    print("  -> Aoi Lança Op & Armadilha de Urso: 100% OK!")


def test_cycle5_arenas():
    print("Testando arenas do Ciclo 5 (Clareira dos Pinheiros & Taiga de Ezo)...")
    assert ARENA_SACRED_PINES in ARENA_SPECS
    assert ARENA_EZO_TUNDRA in ARENA_SPECS

    pines = create_arena(ARENA_SACRED_PINES)
    assert pines is not None
    assert pines.music == "bgm_pine_forest"
    assert len(pines.hazards) > 0

    ezo = create_arena(ARENA_EZO_TUNDRA)
    assert ezo is not None
    assert ezo.music == "bgm_ezo_taiga"
    assert len(ezo.hazards) > 0
    print("  -> Arenas Clareira dos Pinheiros & Taiga de Ezo: 100% OK!")


def test_cycle5_roster_integration():
    print("Testando integração do Ciclo 5 no Roster e Arcade...")
    assert CHAR_DAIKI in PLAYABLE_FIGHTERS
    assert CHAR_AOI in PLAYABLE_FIGHTERS
    assert CHAR_DAIKI in ARCADE_TIER_ORDER
    assert CHAR_AOI in ARCADE_TIER_ORDER
    print("  -> Roster & Arcade Integration: 100% OK!")


if __name__ == "__main__":
    test_daiki_combat_kit()
    test_aoi_combat_kit()
    test_cycle5_arenas()
    test_cycle5_roster_integration()
    print("\nTodos os testes unitários do Ciclo 5 passaram com sucesso!")
