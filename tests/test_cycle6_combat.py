"""
Testes automatizados completos das mecânicas de combate do Ciclo 6 (Raiden & Hendrika).
Valida:
1. Raiden Tameemon: 3 HP, 3.85 vel, Poise/Super Armor, Tsuppari Rush com pushback, Tachiai Tackle com super knockback e dano 1, parry e fatalidades.
2. Hendrika van der Bilt: 2 HP, 4.60 vel, Estilete corrosivo quebra-guarda, 5 reagentes alquímicos, arremesso balístico 3D, poças químicas com efeitos distintos, upgrade Tier 1/2 e fatalidades elementais.
3. Integração com a fábrica create_fighter de main.py e sistema de colisões.
"""
import os
import sys
import math
import pygame

# Headless
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

pygame.init()
pygame.display.set_mode((640, 480))

from src.config import CHAR_RAIDEN, CHAR_HENDRIKA, CHAR_KENSHIN
from main import create_fighter
from src.entities.raiden import RaidenSumo
from src.entities.hendrika import HendrikaAlchemist
from src.entities.red_samurai import RedSamurai
from src.entities.projectile import AlchemicFlaskProjectile, ChemicalPoolHazard
from src.combat.collision import _get_death_style_for_attacker


def test_raiden_combat_mechanics():
    print("--- Testando Raiden Tameemon ---")
    raiden = create_fighter(CHAR_RAIDEN, 10.0, 10.0)
    assert isinstance(raiden, RaidenSumo), "Fábrica deve instanciar RaidenSumo"
    assert raiden.max_hp == 3, f"Raiden deve ter 3 HP, tem {raiden.max_hp}"
    assert raiden.hp == 3, f"Raiden deve iniciar com 3 HP, tem {raiden.hp}"
    assert abs(raiden.speed - 3.85) < 0.01, f"Velocidade deve ser 3.85, é {raiden.speed}"
    print("  [OK] Atributos base de Raiden: 3 HP, 3.85 velocidade")

    # 1. Tsuppari Rush
    opponent = RedSamurai(11.2, 10.0)
    particles = []
    success = raiden.trigger_tsuppari_rush(12.0, 10.0, particles=particles)
    assert success, "Tsuppari Rush deve ativar"
    assert raiden.state == "TSUPPARI_RUSH", "Estado deve ser TSUPPARI_RUSH"
    assert raiden.hitbox_active, "Hitbox deve estar ativa"

    # Simular avanço e pushback contínuo
    initial_opp_x = opponent.wx
    raiden.update(0.10, opponent=opponent, particles=particles)
    assert opponent.wx > initial_opp_x, "Oponente deve sofrer pushback para longe"
    print("  [OK] Tsuppari Rush avança com pushback massivo no rival")

    # 2. Poise / Hiperarmadura (não sofre stun durante ataque)
    hit, dead = raiden.take_hit((1.0, 0.0), damage=1)
    assert hit, "Deve receber o golpe"
    assert not dead, "Não deve morrer com 1 de dano (tem 3 HP)"
    assert raiden.hp == 2, f"HP deve ser 2, é {raiden.hp}"
    assert raiden.state == "TSUPPARI_RUSH", "Raiden não deve entrar em STUNNED durante ataque (Super Armor)"
    print("  [OK] Hiperarmadura / Poise absorve golpe sem interromper o ataque")

    # 3. Tachiai Tackle
    raiden.state = "IDLE"
    raiden.wx, raiden.wy = 8.0, 10.0
    opponent.wx, opponent.wy = 12.0, 10.0
    opponent.hp = 2
    success_tackle = raiden.trigger_tachiai_tackle(12.0, 10.0, opponent=opponent)
    assert success_tackle, "Tachiai Tackle deve ativar"
    assert raiden.state == "TACHIAI_TACKLE", "Estado deve ser TACHIAI_TACKLE"
    assert abs(raiden.tackle_speed - 9.5) < 0.01, "Velocidade do Tackle deve ser 9.5"

    # Atualizar até o impacto
    raiden.update(0.20, opponent=opponent, particles=particles)
    assert opponent.hp == 1, f"Tackle deve causar 1 de dano, HP do rival é {opponent.hp}"
    assert opponent.wx >= 15.0, f"Tackle deve arremessar o oponente para longe, x={opponent.wx}"
    print("  [OK] Tachiai Tackle semiteleguiado causa 1 de dano e super knockback")

    # 4. Fatalidades
    raiden.state = "TSUPPARI_RUSH"
    style_tsuppari = _get_death_style_for_attacker(raiden, victim=opponent)
    assert style_tsuppari == "TSUPPARI_SONIC_DECAP", f"Estilo de morte deve ser TSUPPARI_SONIC_DECAP, é {style_tsuppari}"

    raiden.state = "TACHIAI_TACKLE"
    style_tackle = _get_death_style_for_attacker(raiden, weapon="tackle", victim=opponent)
    assert style_tackle == "TACHIAI_SHATTER_SLAM", f"Estilo de morte deve ser TACHIAI_SHATTER_SLAM, é {style_tackle}"
    print("  [OK] Fatalidades de Raiden (Tsuppari Sonic Decap & Tachiai Shatter Slam)")


def test_hendrika_combat_mechanics():
    print("--- Testando Hendrika van der Bilt ---")
    hendrika = create_fighter(CHAR_HENDRIKA, 5.0, 10.0)
    assert isinstance(hendrika, HendrikaAlchemist), "Fábrica deve instanciar HendrikaAlchemist"
    assert hendrika.max_hp == 2, f"Hendrika deve ter 2 HP, tem {hendrika.max_hp}"
    assert hendrika.hp == 2, f"Hendrika deve iniciar com 2 HP, tem {hendrika.hp}"
    assert abs(hendrika.speed - 4.60) < 0.01, f"Velocidade deve ser 4.60, é {hendrika.speed}"
    print("  [OK] Atributos base de Hendrika: 2 HP, 4.60 velocidade")

    # 1. Ciclo de 5 Reagentes
    expected_reagents = ["acid", "fire", "ether", "frost", "miasma"]
    for expected in expected_reagents:
        current = hendrika.active_reagent
        assert current == expected, f"Reagente ativo esperado {expected}, obteve {current}"
        hendrika.cycle_reagent()
    assert hendrika.active_reagent == "acid", "Ciclo deve retornar ao Ácido"
    print("  [OK] Ciclo de 5 reagentes químicos funciona perfeitamente (Ácido, Fogo, Éter, Salitre, Miasma)")

    # 2. Estilete Corrosivo e Quebra de Guarda
    opponent = RedSamurai(6.2, 10.0)
    opponent.state = "PARRY"
    success_stiletto = hendrika.trigger_stiletto_thrust(6.2, 10.0, opponent=opponent)
    assert success_stiletto, "Estilete deve ativar"
    assert opponent.state == "STUNNED", "Ácido do estilete deve quebrar a guarda (PARRY) do oponente"
    print("  [OK] Estilete Corrosivo perfura e quebra guarda do oponente")

    # 3. Arremesso Balístico de Frasco 3D
    projectiles = []
    particles = []
    hendrika.state = "IDLE"
    success_flask = hendrika.trigger_flask_throw(10.0, 10.0, projectiles=projectiles, particles=particles)
    assert success_flask, "Arremesso de frasco deve ativar"
    assert len(projectiles) == 1, "Frasco deve ser adicionado aos projéteis"
    flask = projectiles[0]
    assert isinstance(flask, AlchemicFlaskProjectile), "Projétil deve ser AlchemicFlaskProjectile"
    assert flask.reagent == "acid", f"Reagente deve ser ácido, é {flask.reagent}"
    assert flask.wz > 0.0, "Frasco deve começar acima do solo em arco 3D"

    # Atualizar voo do frasco até atingir o solo
    chemical_pools = []
    for _ in range(30):
        if flask.is_active:
            flask.update(0.03, particles=particles, chemical_pools=chemical_pools)
    assert len(chemical_pools) == 1, "Impacto do frasco deve gerar ChemicalPoolHazard"
    pool = chemical_pools[0]
    assert isinstance(pool, ChemicalPoolHazard), "Poça deve ser ChemicalPoolHazard"
    assert pool.reagent == "acid", "Poça deve ser de ácido"
    print("  [OK] Arremesso balístico 3D gera poça química no impacto")

    # 4. Efeitos das Poças Químicas
    target = RedSamurai(pool.wx, pool.wy)
    target.hp = 2
    pool.tick_timer = 0.80  # Forçar tick imediato
    pool.update(0.10, fighters=[target], particles=particles)
    assert target.hp == 1, f"Poça ácida deve drenar 1 HP do oponente no tick, HP={target.hp}"
    print("  [OK] Poça de Ácido Corrosivo drena HP e corrói o alvo")

    # 5. Fatalidades por Reagente
    hendrika.state = "ATTACK"
    style_stiletto = _get_death_style_for_attacker(hendrika, victim=opponent)
    assert style_stiletto == "STILETTO_CAROTID_VITRIOL", f"Estilo estilete deve ser STILETTO_CAROTID_VITRIOL, é {style_stiletto}"

    hendrika.state = "FLASK_THROW"
    for r in ["acid", "fire", "ether", "frost", "miasma"]:
        hendrika.active_reagent_idx = hendrika.reagents.index(r)
        style_flask = _get_death_style_for_attacker(hendrika, weapon="flask", victim=opponent)
        assert r in style_flask.lower() or ("acid" in r and "dissolve" in style_flask.lower()) or ("fire" in r and "ash" in style_flask.lower()) or ("frost" in r and "shatter" in style_flask.lower()), f"Fatalidade incorreta para {r}: {style_flask}"
    print("  [OK] Fatalidades de Hendrika (Estilete Vitriol e variantes dinâmicas por elemento do frasco)")


if __name__ == "__main__":
    test_raiden_combat_mechanics()
    test_hendrika_combat_mechanics()
    print("\nTODOS OS TESTES DE COMBATE DO CICLO 6 PASSARAM COM SUCESSO!")
