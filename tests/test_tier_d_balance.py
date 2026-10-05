"""
Testes unitários e de integração para o Balanceamento de Lutadores Tier D (Fase 4 - Itens 4.1 a 4.4).
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import math
import pygame
from src.entities.samurai import Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED
from src.entities.red_samurai import RedSamurai
from src.entities.purple_ninja import PurpleNinja
from src.entities.gray_ninja import GrayNinja
from src.entities.yellow_ninja import YellowNinja
from src.entities.american_ninja import AmericanNinja
from src.entities.doberman import DobermanDog, STATE_DOG_BARK
from src.entities.projectile import KunaiProjectile, ShurikenProjectile, TimedBombEntity, RemoteMineEntity, KusarigamaChainEntity
from src.combat.collision import CombatSystem
from src.isometric.camera import Camera
from src.world.map_data import GameMap


def test_kenshin_tier_d_buffs():
    """Entregável 4.1: i-frame pós-Shukuchi do Kenshin."""
    game_map = GameMap()
    kenshin = RedSamurai(5.0, 5.0)

    kenshin.state = STATE_IDLE
    kenshin.roll_recovery_timer = 0.0
    kenshin.roll_cooldown_timer = 0.0
    kenshin.dash_recovery_timer = 0.0

    kenshin.trigger_dash(1.0, 0.0)
    assert kenshin.state == "SHUKUCHI"
    assert kenshin.is_invulnerable_dodge is True

    # Atualizar até o fim do dash
    kenshin.update(0.16, game_map)
    assert kenshin.state == STATE_IDLE
    assert kenshin.post_shukuchi_iframe_timer == 0.12
    assert kenshin.is_invulnerable_dodge is True

    # Após decorrido o iframe, perde invulnerabilidade
    kenshin.update(0.13, game_map)
    assert kenshin.post_shukuchi_iframe_timer == 0.0
    assert kenshin.is_invulnerable_dodge is False


def test_murasaki_tier_d_buffs():
    """Entregável 4.2: Murasaki Kama active window e Kusarigama hook com 1 HP de dano."""
    game_map = GameMap()
    camera = Camera(10.0, 10.0)
    murasaki = PurpleNinja(5.0, 5.0)
    assert murasaki.active_time == 0.22

    # Testar dano de Kusarigama Hook
    combat_sys = CombatSystem()
    target = RedSamurai(7.0, 5.0)
    target.hp = 2

    hook = KusarigamaChainEntity(target.wx, target.wy, 0.5, 1.0, 0.0, owner=murasaki)
    particles = []
    banners = []

    combat_sys.process_combat(murasaki, target, game_map, particles, banners, camera, [hook], 0.016)

    assert hook.state == "HOOKED_PULLING"
    assert target.hp == 1  # Sofreu 1 de dano!
    assert target.state == STATE_STUNNED


def test_kasumi_tier_d_buffs():
    """Entregável 4.3: Kasumi RemoteMine arming delay acelerado e imunidade a auto-suicídio (<= 1 HP)."""
    game_map = GameMap()
    camera = Camera(10.0, 10.0)
    combat_sys = CombatSystem()

    kasumi = GrayNinja(5.0, 5.0)
    opponent = RedSamurai(9.0, 5.0)

    # 1. Mina de Kasumi
    mine = RemoteMineEntity(kasumi.wx, kasumi.wy, owner=kasumi)
    assert mine.arm_delay == 0.28
    assert not mine.is_ready_to_detonate()

    # Passou o arm_delay
    mine.update(0.29, game_map)
    assert mine.is_ready_to_detonate()

    # Detonação com Kasumi com 2 HP: sofre 1 de auto-dano
    kasumi.hp = 2
    mine.detonate([kasumi, opponent])
    assert kasumi.hp == 1
    assert kasumi.is_alive

    # Detonação com Kasumi com 1 HP: NÃO morre por auto-dano (imunidade a auto-suicídio)
    mine2 = RemoteMineEntity(kasumi.wx, kasumi.wy, owner=kasumi)
    mine2.age = 0.35
    mine2.is_armed = True
    mine2.detonate([kasumi, opponent])
    assert kasumi.hp == 1
    assert kasumi.is_alive

    # 2. Bomba Temporizada (TimedBombEntity)
    bomb = TimedBombEntity(kasumi.wx, kasumi.wy, wz=0.0, dir_x=0.0, dir_y=0.0, owner=kasumi)
    bomb.is_airborne = False
    bomb.fuse_timer = 0.0  # Detonação imediata

    particles = []
    banners = []
    combat_sys.process_combat(kasumi, opponent, game_map, particles, banners, camera, [bomb], 0.016)

    # Kasumi não morre pelo blast de sua própria bomba quando tem 1 HP
    assert kasumi.hp == 1
    assert kasumi.is_alive


def test_hanzo_tier_d_buffs():
    """Entregável 4.4: Hanzo Kunai pickup distance de 0.85m fluido."""
    game_map = GameMap()
    hanzo = YellowNinja(5.0, 5.0)
    hanzo.has_kunai = False

    kunai = KunaiProjectile(5.7, 5.0, 0.05, 1.0, 0.0, owner=hanzo)
    kunai.state = "ON_GROUND"
    kunai.pickup_delay = 0.0

    # Distância = 0.70m (< 0.85m) -> deve ser recolhida!
    kunai.update(0.016, game_map, [])
    assert hanzo.has_kunai is True
    assert kunai.is_active is False


def test_joe_tier_d_buffs():
    """Entregável 4.4: Joe Doberman charge reaction delay (0.15s), speed (17.5) e Shuriken dano em alvos móveis."""
    game_map = GameMap()
    camera = Camera(10.0, 10.0)
    combat_sys = CombatSystem()

    joe = AmericanNinja(5.0, 5.0)
    dog = joe.dog
    assert dog.charge_speed == 17.5

    # Cão charge windup
    dog.charge(8.0, 5.0)
    assert dog.state == STATE_DOG_BARK
    assert dog.state_timer == 0.15

    # Shuriken contra alvo parado -> 0 dano, apenas stun
    target_still = RedSamurai(5.4, 5.0)
    target_still.is_moving = False
    target_still.state = STATE_IDLE
    target_still.hp = 2

    shuriken1 = ShurikenProjectile(5.4, 5.0, 0.5, 1.0, 0.0, owner=joe)
    combat_sys.process_combat(joe, target_still, game_map, [], [], camera, [shuriken1], 0.016)
    assert target_still.hp == 2  # Não levou dano
    assert target_still.state == STATE_STUNNED

    # Shuriken contra alvo em movimento -> 1 HP de dano + stun
    target_moving = RedSamurai(5.4, 5.0)
    target_moving.is_moving = True
    target_moving.state = STATE_WALK
    target_moving.hp = 2

    shuriken2 = ShurikenProjectile(5.4, 5.0, 0.5, 1.0, 0.0, owner=joe)
    combat_sys.process_combat(joe, target_moving, game_map, [], [], camera, [shuriken2], 0.016)
    assert target_moving.hp == 1  # Levou 1 de dano!
    assert target_moving.state == STATE_STUNNED


if __name__ == "__main__":
    pygame.init()
    test_kenshin_tier_d_buffs()
    print("✓ test_kenshin_tier_d_buffs passed!")
    test_murasaki_tier_d_buffs()
    print("✓ test_murasaki_tier_d_buffs passed!")
    test_kasumi_tier_d_buffs()
    print("✓ test_kasumi_tier_d_buffs passed!")
    test_hanzo_tier_d_buffs()
    print("✓ test_hanzo_tier_d_buffs passed!")
    test_joe_tier_d_buffs()
    print("✓ test_joe_tier_d_buffs passed!")
    print("\nALL TIER D BALANCE TESTS PASSED SUCCESSFULLY!")
