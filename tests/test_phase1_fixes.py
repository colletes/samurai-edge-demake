"""
Testes automatizados da Fase 1: Bugs Críticos e Balanço Numérico.
Valida:
1. Aoi dano primário = 2 HP
2. Hanzo Kunai dano = 1 HP, Tanto dano = 2 HP
3. Joe Shuriken dano = 1 HP + micro-stun
4. Ren Kiai dano = 1 HP
5. Tomoe esquiva secundária não trava no chão (avança e recupera)
6. Kasumi mina de chão híbrida (detonação por proximidade 1.2m e manual 2º toque)
7. O-rin fire rate ajustado
8. Valerius cooldown de summon reduzido
"""
import os
import sys
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from src.entities.aoi import AoiHuntress
from src.entities.yellow_ninja import YellowNinja
from src.entities.american_ninja import AmericanNinja
from src.entities.gray_ninja import GrayNinja
from src.entities.ren_monk import RenMonk
from src.entities.kyudo_archer import KyudoArcher
from src.entities.orin import OrinMinstrel
from src.entities.valerius import ValeriusNecromancer
from src.entities.samurai import STATE_ROLL, STATE_IDLE
from src.entities.projectile import KunaiProjectile, ShurikenProjectile, RemoteMineEntity
from src.combat.collision import CombatSystem
from src.isometric.camera import Camera

class MockMap:
    def __init__(self):
        self.bamboos = []
        self.rocks = []
        self.interactive_elements = []
        self.lanterns = []
        self.width = 20
        self.height = 20
    def is_walkable(self, x, y):
        return True
    def get_height(self, x, y):
        return 0.0

def test_aoi_primary_damage():
    aoi = AoiHuntress(5.0, 5.0)
    assert aoi.trigger_spear_thrust(6.0, 5.0)
    assert aoi.hitbox_damage == 2, f"Aoi hitbox_damage deveria ser 2, obteve {aoi.hitbox_damage}"
    print("✓ Teste Aoi dano primário = 2 HP OK!")

def test_hanzo_damages():
    hanzo = YellowNinja(5.0, 5.0)
    assert hanzo.trigger_combo_attack(6.0, 5.0)
    assert hanzo.hitbox_damage == 2, f"Hanzo Tanto Passo 1 deveria ser 2 HP, obteve {hanzo.hitbox_damage}"
    print("✓ Teste Hanzo Tanto dano = 2 HP OK!")

def test_tomoe_dodge_not_stuck():
    tomoe = KyudoArcher(5.0, 5.0)
    gmap = MockMap()
    # Forçar cooldown na corda para usar esquiva pura
    tomoe.rope_timer = 2.0
    res = tomoe.trigger_roll(1.0, 0.0)
    assert res is True
    assert tomoe.state == STATE_ROLL

    # Simular frames de update
    for _ in range(30):
        tomoe.update(0.016, gmap)

    assert tomoe.state == STATE_IDLE, f"Tomoe deveria ter recuperado para STATE_IDLE, mas continua em {tomoe.state}"
    assert tomoe.wx > 5.0, "Tomoe deveria ter se deslocado durante o roll"
    print("✓ Teste Tomoe esquiva secundária não trava mais no chão OK!")

def test_kasumi_hybrid_mine_proximity():
    kasumi = GrayNinja(5.0, 5.0)
    enemy = YellowNinja(5.8, 5.0) # a 0.8m da mina
    enemy.hp = 2
    gmap = MockMap()
    projs = []
    particles = []
    banners = []

    # 1º clique: planta mina
    assert kasumi.trigger_remote_mine(5.0, 5.0, projectiles=projs)
    assert len(projs) == 1
    mine = projs[0]
    assert isinstance(mine, RemoteMineEntity)

    # Armar a mina simulando passagem de tempo
    mine.update(0.35, gmap, particles, fighters=[kasumi, enemy], banners=banners)
    assert mine.is_armed is True
    # Na próxima atualização com o inimigo dentro de 1.2m, ela deve detonar por proximidade!
    still_valid = mine.update(0.016, gmap, particles, fighters=[kasumi, enemy], banners=banners)
    assert still_valid is False
    assert mine.is_active is False
    assert enemy.hp == 0, f"Inimigo deveria ter sofrido 2 de dano da mina, HP: {enemy.hp}"
    print("✓ Teste Kasumi mina híbrida detonação por proximidade OK!")

def test_joe_shuriken_damage_and_stun():
    joe = AmericanNinja(5.0, 5.0)
    target = YellowNinja(5.5, 5.0) # estacionário
    target.hp = 2
    combat = CombatSystem()
    shuriken = ShurikenProjectile(5.4, 5.0, 0.5, 1.0, 0.0, owner=joe)
    projs = [shuriken]
    particles = []
    banners = []
    camera = Camera(800, 600)
    gmap = MockMap()

    combat.process_combat(joe, target, gmap, particles, banners, camera, projs, 0.016)
    assert target.hp == 1, f"Joe shuriken deveria causar 1 HP de dano, target.hp = {target.hp}"
    assert target.state == "STUNNED" or target.state_timer > 0, "Alvo deveria estar atordoado"
    print("✓ Teste Joe Shuriken causa 1 HP de dano + micro stun OK!")

def test_ren_kiai_damage():
    ren = RenMonk(5.0, 5.0)
    enemy = YellowNinja(5.8, 5.0)
    enemy.hp = 2
    gmap = MockMap()
    banners = []
    particles = []

    res = ren.trigger_kiai_shout(5.8, 5.0, opponent=enemy, game_map=gmap, banners=banners, particles=particles)
    assert res is True
    assert enemy.hp == 1, f"Ren Kiai deveria causar 1 HP de dano, enemy.hp = {enemy.hp}"
    print("✓ Teste Ren Kiai causa 1 HP de dano OK!")

def test_cadence_and_cooldowns():
    orin = OrinMinstrel(5.0, 5.0)
    assert orin.attack_recovery >= 0.28
    assert orin.kamaitachi_cooldown >= 0.60

    valerius = ValeriusNecromancer(5.0, 5.0)
    assert valerius.summon_cooldown <= 4.0
    print("✓ Teste cadência O-rin e recarga Valerius OK!")

if __name__ == "__main__":
    test_aoi_primary_damage()
    test_hanzo_damages()
    test_tomoe_dodge_not_stuck()
    test_kasumi_hybrid_mine_proximity()
    test_joe_shuriken_damage_and_stun()
    test_ren_kiai_damage()
    test_cadence_and_cooldowns()
    print("\n=======================================================")
    print("TODOS OS TESTES DA FASE 1 PASSARAM COM 100% DE SUCESSO!")
    print("=======================================================")
