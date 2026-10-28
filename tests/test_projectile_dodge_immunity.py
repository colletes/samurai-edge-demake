"""
Testes de balanceamento: Imunidade a projéteis cinéticos durante a esquiva (Dodge Evasion).
Valida que combatentes em esquiva ativa (i-frames) não são atingidos por kunais,
balas de mosquete, flechas de kyudo, shurikens, ofudas e ondas de vento, mantendo o projétil ativo
e impedindo re-acertos fantasma pós-recuperação (Graze Protection).
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.combat.collision import CombatSystem, is_fighter_evading
from src.entities.samurai import Samurai, STATE_ROLL, STATE_IDLE, STATE_PARRY
from src.entities.projectile import (
    KunaiProjectile, MusketBulletProjectile, KyudoArrowProjectile,
    ShurikenProjectile, MusashiWaveProjectile, CannonballProjectile
)
from src.world.map_data import GameMap

class DummyCamera:
    def add_shake(self, amount: float):
        pass

def setup_dummy_map():
    return GameMap()

def test_is_fighter_evading_helper():
    f = Samurai(5.0, 5.0, "red")
    f.state = STATE_IDLE
    f.is_invulnerable_dodge = False
    assert not is_fighter_evading(f)

    # Ativa esquiva com i-frames
    f.state = STATE_ROLL
    f.is_invulnerable_dodge = True
    assert is_fighter_evading(f)

    # Esquiva em recuperação (i-frames encerrados)
    f.is_invulnerable_dodge = False
    assert not is_fighter_evading(f)

    # Morto
    f.is_alive = False
    f.is_invulnerable_dodge = True
    assert not is_fighter_evading(f)

def test_kunai_dodge_graze_and_multi_frame_protection():
    cs = CombatSystem()
    game_map = setup_dummy_map()

    p1 = Samurai(2.0, 5.0, "red") # Lançador
    p2 = Samurai(5.0, 5.0, "blue") # Alvo

    # P2 em esquiva com i-frames
    p2.state = STATE_ROLL
    p2.is_invulnerable_dodge = True
    p2_initial_hp = p2.hp

    # Kunai atinge a posição de P2
    kunai = KunaiProjectile(5.0, 5.0, 0.6, dir_x=1.0, dir_y=0.0, owner=p1)
    projectiles = [kunai]

    # Frame 1: Colisão durante a esquiva
    winner = cs.process_combat(p1, p2, game_map, particles=[], banners=[], camera=DummyCamera(), projectiles=projectiles)
    
    assert winner is None
    assert p2.hp == p2_initial_hp
    assert p2.is_alive
    assert kunai.is_active, "A kunai deve continuar ativa voando reto, sem detonar ou cair"
    assert p2 in getattr(kunai, "evaded_targets", set()), "P2 deve ser registrado no set de evaded_targets"

    # Frame 2: A esquiva de P2 termina (recuperação, sem i-frames), mas a kunai ainda sobrepõe
    p2.state = STATE_IDLE
    p2.is_invulnerable_dodge = False

    winner_f2 = cs.process_combat(p1, p2, game_map, particles=[], banners=[], camera=DummyCamera(), projectiles=projectiles)

    assert winner_f2 is None
    assert p2.hp == p2_initial_hp
    assert p2.is_alive, "P2 não deve sofrer dano fantasma na recuperação graças ao Graze Protection"
    assert kunai.is_active

def test_musket_bullet_dodge_immunity():
    cs = CombatSystem()
    game_map = setup_dummy_map()

    p1 = Samurai(2.0, 5.0, "red")
    p2 = Samurai(5.0, 5.0, "blue")

    p2.state = STATE_ROLL
    p2.is_invulnerable_dodge = True

    bullet = MusketBulletProjectile(5.0, 5.0, 0.6, dir_x=1.0, dir_y=0.0, owner=p1)
    projectiles = [bullet]

    winner = cs.process_combat(p1, p2, game_map, particles=[], banners=[], camera=DummyCamera(), projectiles=projectiles)

    assert winner is None
    assert p2.is_alive
    assert bullet.is_active, "A bala de mosquete deve voar direto através do alvo em esquiva"
    assert p2 in bullet.evaded_targets

def test_kyudo_arrow_dodge_immunity():
    cs = CombatSystem()
    game_map = setup_dummy_map()

    p1 = Samurai(2.0, 5.0, "red")
    p2 = Samurai(5.0, 5.0, "blue")

    p2.state = STATE_ROLL
    p2.is_invulnerable_dodge = True

    arrow = KyudoArrowProjectile(5.0, 5.0, 0.6, dir_x=1.0, dir_y=0.0, owner=p1)
    projectiles = [arrow]

    winner = cs.process_combat(p1, p2, game_map, particles=[], banners=[], camera=DummyCamera(), projectiles=projectiles)

    assert winner is None
    assert p2.is_alive
    assert arrow.is_active, "A flecha deve atravessar sem atingir o guerreiro em esquiva"

def test_cannonball_explosion_is_not_evaded():
    """Explosões em área permanecem perigosas/letais mesmo em esquiva."""
    cs = CombatSystem()
    game_map = setup_dummy_map()

    p1 = Samurai(2.0, 5.0, "red")
    p2 = Samurai(5.0, 5.0, "blue")

    p2.state = STATE_IDLE
    p2.is_invulnerable_dodge = False

    cannonball = CannonballProjectile(5.0, 5.0, owner=p1)
    cannonball.has_exploded = True
    projectiles = [cannonball]

    winner = cs.process_combat(p1, p2, game_map, particles=[], banners=[], camera=DummyCamera(), projectiles=projectiles)

    assert winner == "P1_WINS", "A bala de canhão explodida deve atingir letalmente alvos no solo"

def test_reflection_clears_evaded_targets():
    """Se um projétil é refletido por Parry / Stance, seu histórico de esquiva é resetado para atingir o adversário."""
    from src.entities.blue_samurai import BlueSamurai
    cs = CombatSystem()
    game_map = setup_dummy_map()

    p1 = Samurai(2.0, 5.0, "red")
    p2 = BlueSamurai(5.0, 5.0)

    # P2 em postura de Parry com refletor ativo
    p2.state = STATE_PARRY
    p2.parry_reflect_active_timer = 0.25

    bullet = MusketBulletProjectile(5.0, 5.0, 0.6, dir_x=1.0, dir_y=0.0, owner=p1)
    bullet.evaded_targets = {p1} # Simula que P1 estava no set

    projectiles = [bullet]
    cs.process_combat(p1, p2, game_map, particles=[], banners=[], camera=DummyCamera(), projectiles=projectiles)

    assert bullet.has_been_reflected
    assert bullet.owner == p2
    assert len(bullet.evaded_targets) == 0, "Reflexão deve limpar evaded_targets para permitir contra-ataque a P1"

if __name__ == "__main__":
    test_is_fighter_evading_helper()
    test_kunai_dodge_graze_and_multi_frame_protection()
    test_musket_bullet_dodge_immunity()
    test_kyudo_arrow_dodge_immunity()
    test_cannonball_explosion_is_not_evaded()
    test_reflection_clears_evaded_targets()
    print("Todos os testes de imunidade e graze de projéteis passaram com sucesso!")
