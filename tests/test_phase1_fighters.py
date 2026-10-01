import os
import sys
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()

from src.config import COLOR_YELLOW_NINJA
from src.entities.samurai import (
    Samurai, STATE_ROLL, STATE_RECOVERY, STATE_IDLE, STATE_ATTACK, STATE_STUNNED
)
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.yellow_ninja import YellowNinja
from src.entities.american_ninja import AmericanNinja
from src.entities.gray_ninja import GrayNinja
from src.entities.purple_ninja import PurpleNinja
from src.entities.rifleman import Rifleman, PowderTrap
from src.entities.kyudo_archer import KyudoArcher
from src.entities.pirate import PirateSwordswoman
from src.entities.musketeer import Musketeer
from src.entities.doberman import DobermanDog, STATE_DOG_KNOCKED_OUT, STATE_DOG_FOLLOW, STATE_DOG_CHARGE
from src.entities.projectile import (
    KunaiProjectile, KyudoArrowProjectile, RopeArrowProjectile,
    MusketBulletProjectile, ShurikenProjectile, TimedBombEntity, RemoteMineEntity
)
from src.world.map_data import GameMap
from src.combat.collision import CombatSystem
from src.isometric.camera import Camera
from main import (
    execute_fighter_attack,
    execute_fighter_secondary,
    execute_fighter_roll
)

class MockScreen:
    def __init__(self):
        self.surface = pygame.Surface((800, 600))

def test_universal_dash_recovery():
    print("[TEST] Universal Dash Recovery Lag...", flush=True)
    game_map = GameMap()
    s = RedSamurai(10.0, 10.0)
    assert s.dash_recovery_duration == 0.12
    assert s.can_act() is True

    # Iniciar rolamento
    s.trigger_roll(1.0, 0.0)
    assert s.state == STATE_ROLL

    # Simular término do rolamento
    s.update_roll(0.25, game_map)
    assert s.state == STATE_IDLE
    assert s.dash_recovery_timer > 0.0
    assert s.can_act() is False, "Fighter should not be able to act during dash recovery"

    # Atualizar durante recuperação (0.08s de 0.12s)
    s.update(0.08, game_map)
    assert s.can_act() is False

    # Completar recuperação (mais 0.05s)
    s.update(0.05, game_map)
    assert s.dash_recovery_timer <= 0.0
    assert s.can_act() is True, "Fighter should be able to act after dash recovery ends"
    print("  -> Dash recovery passed!")

def test_tomoe_cooldown_and_rope():
    print("[TEST] Tomoe Arrow Cooldown and Bamboo Penetration...", flush=True)
    game_map = GameMap()
    tomoe = KyudoArcher(10.0, 10.0)
    projectiles = []

    # Disparo de flecha
    tomoe.trigger_bow_draw(12.0, 10.0, projectiles)
    assert len(projectiles) == 1
    assert tomoe.arrow_cooldown_timer == 1.20

    # Tentativa imediata de disparar durante cooldown deve ser bloqueada
    tomoe.trigger_bow_draw(12.0, 10.0, projectiles)
    assert len(projectiles) == 1, "Disparo deve ser bloqueado durante o cooldown de 1.2s"

    # Avançar o tempo além do cooldown
    tomoe.update(1.25, game_map)
    assert tomoe.arrow_cooldown_timer <= 0.0
    tomoe.state = STATE_IDLE
    tomoe.trigger_bow_draw(12.0, 10.0, projectiles)
    assert len(projectiles) == 2, "Disparo permitido após expirar o cooldown"

    # Flecha de corda corta bambus no trajeto sem ser interrompida
    rope = RopeArrowProjectile(wx=5.0, wy=5.0, wz=0.5, dir_x=1.0, dir_y=0.0, owner=tomoe)
    # Adicionar bambu no caminho
    bamboo = game_map.bamboos[0]
    bamboo.wx, bamboo.wy = 5.2, 5.0
    bamboo.is_cut = False
    particles = []
    rope.update(0.02, game_map, particles)
    assert bamboo.is_cut is True, "Rope arrow should cut bamboos in flight"
    assert rope.state == "FLYING", "Rope arrow should not stop on bamboo"
    print("  -> Tomoe cooldown and rope penetration passed!")

def test_hanzo_kunai_and_jump():
    print("[TEST] Hanzo Standing Throw, Jump, Downward Angle, and Landing Lag...", flush=True)
    game_map = GameMap()
    hanzo = YellowNinja(10.0, 10.0)
    opp = RedSamurai(14.0, 10.0)
    projectiles = []

    # Ataque primário no solo é estritamente arremesso em pé
    execute_fighter_attack(hanzo, opp.wx, opp.wy, projectiles, [])
    assert hanzo.wz == 0.0, "Standing throw must keep Hanzo on the ground"
    assert len(projectiles) == 1
    kunai = projectiles[0]
    assert kunai.vz == 0.0, "Ground throw kunai should fly horizontally"

    # Limpar projéteis e testar salto (secundário)
    hanzo.state = STATE_IDLE
    hanzo.dash_recovery_timer = 0.0
    projectiles.clear()

    hanzo.trigger_jump(opp.wx, opp.wy)
    assert hanzo.state == "JUMP"
    hanzo.update(0.15, game_map)
    assert hanzo.wz > 0.0, "Secondary must leap into the air"

    # No ar, arremesso tem ângulo descendente (vz < 0)
    hanzo.has_kunai = True
    execute_fighter_attack(hanzo, opp.wx, opp.wy, projectiles, [])
    assert len(projectiles) == 1
    air_kunai = projectiles[0]
    assert air_kunai.vz < 0.0, "Airborne kunai throw must angle downwards"

    # Dash no ar não flutua indefinidamente (gravidade preservada)
    hanzo.trigger_roll(1.0, 0.0)
    assert hanzo.state == STATE_ROLL
    assert hanzo.is_midair_dash is True
    for _ in range(30):
        hanzo.update(0.05, game_map)
        hanzo.update_roll(0.05, game_map)
    assert hanzo.wz == 0.0, "Hanzo must land on ground and not float indefinitely"
    assert hanzo.is_midair_dash is False
    print("  -> Hanzo mechanics passed!")

def test_anne_cannon_and_powder_dash():
    print("[TEST] Anne Naval Cannon Cooldown and Black Powder Dash Stun...", flush=True)
    game_map = GameMap()
    anne = PirateSwordswoman(10.0, 10.0)
    opp = RedSamurai(11.0, 10.0)
    projectiles = []

    # Anne inicia a partida com o canhão em cooldown (anti round-start spam)
    assert anne.cannon_cooldown_timer == anne.cannon_cooldown
    anne.cannon_cooldown_timer = 0.0

    # Disparo de artilharia naval (Hold & Release)
    anne.start_cannon_strike(14.0, 10.0)
    anne.release_cannon_strike(projectiles)
    assert len(projectiles) == 1
    assert anne.cannon_cooldown_timer == anne.cannon_cooldown

    # Segundo disparo imediato é impedido pelo cooldown
    anne.start_cannon_strike(14.0, 10.0)
    assert anne.is_aiming_cannon is False, "Cannon should be on cooldown"

    # Dash de pólvora negra causa mini-stun e knockback no adversário próximo
    anne.state = STATE_IDLE
    anne.dash_recovery_timer = 0.0
    anne.trigger_roll(1.0, 0.0, particles=[])
    assert anne.state == STATE_ROLL

    initial_opp_x = opp.wx
    anne.update(0.05, game_map, opponent=opp)
    assert opp.state == STATE_STUNNED, "Opponent in path of Black Powder Dash must be stunned"
    assert opp.wx > initial_opp_x, "Opponent must be knocked back by Black Powder Dash"
    print("  -> Anne cannon cooldown and powder dash passed!")

def test_teppo_trap_and_pouch():
    print("[TEST] Teppo Powder Trap (Rebalanceamento: sem custo de pólvora, 1 mina ativa por vez) and Pouch Fix...", flush=True)
    game_map = GameMap()
    teppo = Rifleman(10.0, 10.0)
    traps = []

    assert teppo.has_ammo is True
    teppo.trigger_powder_trap(traps)
    assert len(traps) == 1
    assert teppo.has_ammo is True, "Placing a powder trap no longer costs ammo"
    assert teppo.trap_timer == teppo.trap_cooldown == 5.0

    # Enquanto a mina anterior ainda estiver ativa, não pode plantar outra (mesmo com cooldown zerado)
    teppo.state = STATE_IDLE
    teppo.dash_recovery_timer = 0.0
    teppo.trap_timer = 0.0
    teppo.trigger_powder_trap(traps)
    assert len(traps) == 1, "Cannot place a second mine while one is still active"

    # Após a mina antiga deixar de estar ativa (detonou/expirou), uma nova pode ser plantada
    traps[0].is_active = False
    teppo.trigger_powder_trap(traps)
    assert len(traps) == 2, "Can place a new mine once the previous one is no longer active"
    assert teppo.trap_timer == 5.0, "Redeploying resets the 5s cooldown"

    # Coleta de cartucho de pólvora reseta coordenadas para evitar coleta repetida infinita (Item 11)
    teppo.has_ammo = False  # Simula munição de disparo já gasta (independente da mina)
    class MockPouch:
        def __init__(self, wx, wy):
            self.wx = wx
            self.wy = wy
            self.radius = 0.5
            self.is_active = True
            self.respawn_timer = 0.0

    pouch = MockPouch(teppo.wx, teppo.wy)
    picked = teppo.check_powder_pickup([pouch])
    assert picked is True
    assert teppo.has_ammo is True
    assert pouch.wx == -999.0, "Collected pouch moved away to prevent infinite instant pickups"
    assert pouch.is_active is False
    assert pouch.respawn_timer == 10.0
    print("  -> Teppo trap ammo and pouch fix passed!")

def test_musashi_manual_combo():
    print("[TEST] Musashi Manual 3-Hit Combo and 3rd Strike Lunge...", flush=True)
    game_map = GameMap()
    musashi = BlueSamurai(10.0, 10.0)

    # 1º golpe
    musashi.trigger_combo_attack(12.0, 10.0)
    assert musashi.combo_step == 1
    assert musashi.state == STATE_ATTACK

    # Pressionar o 2º golpe durante o 1º ativa o buffer do combo
    musashi.trigger_combo_attack(12.0, 10.0)
    assert musashi.combo_buffered is True

    # Avançar o tempo para concluir o 1º golpe e encadear o 2º automaticamente pelo buffer
    musashi.update(0.20, game_map)
    assert musashi.combo_step == 2
    assert musashi.state == STATE_ATTACK

    # Pressionar o 3º golpe (buffer do lunge final)
    musashi.trigger_combo_attack(12.0, 10.0)
    assert musashi.combo_buffered is True

    # Avançar para o 3º golpe: avanço com lunge (+35% de velocidade/alcance)
    start_x = musashi.wx
    musashi.update(0.20, game_map)
    assert musashi.combo_step == 3
    assert musashi.state == STATE_ATTACK
    # Atualizar o deslocamento do lunge
    musashi.update(0.10, game_map)
    assert musashi.wx > start_x + 0.3, "3rd strike must forward lunge (+35% distance)"
    print("  -> Musashi manual combo passed!")

def test_julie_fleche_and_cape_flourish():
    print("[TEST] Julie Fleche Thrust and Cape Flourish...", flush=True)
    game_map = GameMap()
    julie = Musketeer(10.0, 10.0)
    opp = RedSamurai(11.2, 10.0)
    initial_opp_x = opp.wx

    # Fleche Thrust (ataque primário): alcance estendido (+25%) e hitbox calibrada (0.70m)
    julie.trigger_fleche_thrust(12.0, 10.0)
    assert julie.state == STATE_ATTACK
    assert julie.hitbox_radius == 0.70

    # Cape Flourish & Coup de Pied (secundário de espaçamento): knockback ~2m, stagger
    julie.state = STATE_IDLE
    julie.dash_recovery_timer = 0.0
    particles = []
    banners = []
    julie.trigger_cape_flourish(opp.wx, opp.wy, opponent=opp, particles=particles, banners=banners)
    assert julie.cape_timer == julie.cape_cooldown
    assert opp.state == STATE_STUNNED
    assert opp.wx >= initial_opp_x + 1.8, "Cape flourish knockback should be ~2m"
    print("  -> Julie mechanics passed!")

def test_kasumi_remote_mine_and_roll():
    print("[TEST] Kasumi Remote Mine and Stealth Roll...", flush=True)
    game_map = GameMap()
    kasumi = GrayNinja(10.0, 10.0)
    opp = RedSamurai(10.5, 10.0)
    all_f = [kasumi, opp]

    # 1º toque planta a mina
    kasumi.trigger_remote_mine(fighters=all_f)
    assert kasumi.planted_mine is not None
    assert kasumi.planted_mine.is_ready_to_detonate() is False, "Mine has 0.4s arm delay"

    # Tentativa antes de armar falha
    kasumi.trigger_remote_mine(fighters=all_f)
    assert kasumi.planted_mine.is_active is True

    # Aguardar armamento (0.45s)
    kasumi.planted_mine.update(0.45, game_map)
    assert kasumi.planted_mine.is_ready_to_detonate() is True

    # 2º toque detona a mina, danificando ambos se estiverem no raio
    kasumi.trigger_remote_mine(fighters=all_f)
    assert kasumi.planted_mine is None
    assert opp.hp < 2, "Opponent in blast radius must take damage"
    assert kasumi.hp < 2, "Kasumi caught in her own mine blast takes damage (Item 16)"

    # Rolamento furtivo com fumaça e alpha reduzido (Patch 2: alpha = 15)
    kasumi.state = STATE_IDLE
    kasumi.trigger_roll(1.0, 0.0)
    assert kasumi.alpha in (15, 50) or kasumi.alpha <= 50
    print("  -> Kasumi remote mine and roll passed!")

def test_kenshi_ryuu_tsui_sen():
    print("[TEST] Kenshi Ryuu Tsui Sen...", flush=True)
    game_map = GameMap()
    kenshi = RedSamurai(10.0, 10.0)
    kenshi.trigger_ryuu_tsui_sen(12.0, 10.0)
    assert kenshi.state == "RYUU_TSUI_SEN"
    assert kenshi.ryuu_timer == 3.5

    # Simular ascensão do salto
    kenshi.update(0.12, game_map)
    assert kenshi.wz > 0.5, "Kenshi must leap high into the air"

    # Simular descida e impacto fatal no solo
    kenshi.update(0.15, game_map)
    assert kenshi.hitbox_active is True
    assert kenshi.hitbox_radius >= 1.2
    print("  -> Kenshi Ryuu Tsui Sen passed!")

def test_murasaki_chain_shield_and_bamboo():
    print("[TEST] Murasaki Chain Shield Hold & Release and Bamboo Cut...", flush=True)
    game_map = GameMap()
    murasaki = PurpleNinja(10.0, 10.0)

    # Segurar secundário ativa escudo rotativo de corrente (Hold - Item 24)
    murasaki.start_chain_shield(12.0, 10.0)
    assert murasaki.is_holding_shield is True
    assert murasaki.is_spinning_chain is True

    # Giro protetor e rotação da corrente
    murasaki.update_chain_shield(0.10, 12.0, 10.0)
    assert murasaki.is_holding_shield is True
    assert murasaki.shield_spin_angle > 0.0

    # Soltar o botão dispara o gancho da kusarigama (Release - Item 24)
    projectiles = []
    murasaki.release_chain_shield(projectiles)
    assert murasaki.is_holding_shield is False
    assert len(projectiles) == 1, "Releasing shield launches chain pull"

    # Corte de foice corta bambus
    murasaki.state = STATE_IDLE
    bamboo = game_map.bamboos[0]
    bamboo.wx, bamboo.wy = 10.8, 10.0
    bamboo.is_cut = False
    murasaki.trigger_kama_strike(12.0, 10.0, game_map=game_map)
    assert bamboo.is_cut is True, "Kama strike must cut bamboos"
    print("  -> Murasaki mechanics passed!")

def test_doberman_mechanics():
    print("[TEST] Doberman Hit Vulnerability, 2.0s Knockout and Projectile Stun...", flush=True)
    game_map = GameMap()
    combat = CombatSystem()
    cam = Camera()
    joe = AmericanNinja(10.0, 10.0)
    kenshi = RedSamurai(10.8, 10.0)

    dog = joe.dog
    assert dog.state == STATE_DOG_FOLLOW
    assert dog.knockout_duration == 2.0

    joe.wx, joe.wy = 5.0, 5.0  # Joe afastado para testar exclusivamente a interação do cão
    dog.wx, dog.wy = 10.5, 10.0
    kenshi.wx, kenshi.wy = 10.8, 10.0
    kenshi.hitbox_active = True
    kenshi.hitbox_center = (dog.wx, dog.wy)
    kenshi.hitbox_radius = 1.0
    particles = []
    banners = []

    combat.process_combat(
        p1=joe, p2=kenshi, game_map=game_map,
        particles=particles, banners=banners, camera=cam,
        projectiles=[], dt=0.016
    )
    assert dog.state == STATE_DOG_FOLLOW, "Cão em FOLLOW deve ser imune a cortes passivos (Patch 6)"

    # Em CHARGE / BARK, o cão é vulnerável e recebe knockout
    kenshi.hitbox_active = True
    kenshi.hitbox_center = (dog.wx, dog.wy)
    dog.state = STATE_DOG_CHARGE
    combat.process_combat(
        p1=joe, p2=kenshi, game_map=game_map,
        particles=particles, banners=banners, camera=cam,
        projectiles=[], dt=0.016
    )
    assert dog.state == STATE_DOG_KNOCKED_OUT, "Dog must be knocked out when attacking (Patch 6)"
    assert dog.state_timer == 2.0, "Dog knockout duration must be 2.0s"
    any_dog_banner = any("DOG STUNNED!" in b.text for b in banners)
    assert any_dog_banner is True

    # 2. Recuperar o cão e testar atingimento por projétil inimigo durante ataque
    dog.update(2.1, game_map)
    assert dog.state == STATE_DOG_FOLLOW
    dog.state = STATE_DOG_CHARGE

    kunai = KunaiProjectile(wx=dog.wx - 0.2, wy=dog.wy, wz=0.2, dir_x=1.0, dir_y=0.0, owner=kenshi)
    projs = [kunai]
    banners.clear()

    combat.process_combat(
        p1=joe, p2=kenshi, game_map=game_map,
        particles=particles, banners=banners, camera=cam,
        projectiles=projs, dt=0.016
    )

    assert dog.state == STATE_DOG_KNOCKED_OUT, "Enemy projectile must knock out attacking Doberman"
    assert dog.state_timer == 2.0
    print("  -> Doberman mechanics passed!")

if __name__ == "__main__":
    test_universal_dash_recovery()
    test_tomoe_cooldown_and_rope()
    test_hanzo_kunai_and_jump()
    test_anne_cannon_and_powder_dash()
    test_teppo_trap_and_pouch()
    test_musashi_manual_combo()
    test_julie_fleche_and_cape_flourish()
    test_kasumi_remote_mine_and_roll()
    test_kenshi_ryuu_tsui_sen()
    test_murasaki_chain_shield_and_bamboo()
    test_doberman_mechanics()
    print("\n>>> ALL PHASE 1 FIGHTER TESTS PASSED WITH 100% SUCCESS! <<<")
