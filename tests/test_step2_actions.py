import os
import sys
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()

from src.config import DEFAULT_CONTROLS
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.yellow_ninja import YellowNinja
from src.entities.american_ninja import AmericanNinja
from src.entities.gray_ninja import GrayNinja
from src.entities.purple_ninja import PurpleNinja
from src.entities.saitou_samurai import SaitouSamurai
from src.entities.rifleman import Rifleman, PowderTrap
from src.entities.kabuki import Kabuki, PoisonCloud
from src.entities.kyudo_archer import KyudoArcher
from src.entities.pirate import PirateSwordswoman
from src.entities.musketeer import Musketeer
from src.entities.projectile import CannonballProjectile
from src.world.map_data import GameMap
from src.combat.collision import CombatSystem
from src.input.controller_manager import (
    ControllerManager, ACTION_ATTACK, ACTION_SECONDARY, ACTION_DASH
)
from main import (
    execute_fighter_attack,
    execute_fighter_secondary,
    execute_fighter_roll
)

def test_step2_roster_actions():
    print("--- Testando Roster Completo (12 lutadores) com 3 Ações ---", flush=True)
    game_map = GameMap()
    combat_system = CombatSystem()

    fighters = [
        RedSamurai(10.0, 10.0),
        BlueSamurai(10.0, 10.0),
        YellowNinja(10.0, 10.0),
        AmericanNinja(10.0, 10.0),
        GrayNinja(10.0, 10.0),
        PurpleNinja(10.0, 10.0),
        SaitouSamurai(10.0, 10.0),
        Rifleman(10.0, 10.0),
        Kabuki(10.0, 10.0),
        KyudoArcher(10.0, 10.0),
        PirateSwordswoman(10.0, 10.0),
        Musketeer(10.0, 10.0),
    ]

    for f in fighters:
        dummy_opp = RedSamurai(12.0, 10.0)
        projectiles = []
        particles = []
        decoys = []
        poison_clouds = []
        powder_traps = []

        # 1. Testar Ataque Primário
        execute_fighter_attack(f, 12.0, 10.0, projectiles, particles)

        # 2. Testar Ação Secundária
        execute_fighter_secondary(f, 12.0, 10.0, 1.0, 0.0, projectiles, particles, decoys, poison_clouds, powder_traps, opponent=dummy_opp, game_map=game_map)

        # 3. Testar Terceira Ação (Roll / Dash dedicado)
        execute_fighter_roll(f, 1.0, 0.0, 12.0, 10.0, particles, decoys=decoys, game_map=game_map)

        # 4. Atualizar o lutador
        f.update(0.016, game_map)
        print(f"  [OK] {f.__class__.__name__} respondeu com sucesso às 3 ações.", flush=True)

    print("--- Testando Especialidades Específicas da Etapa 2 ---", flush=True)

    # A. Kenshi: Ryuu Tsui Sen (Salto vertical e golpe descendente - Item 17)
    kenshi = RedSamurai(10.0, 10.0)
    opp = BlueSamurai(10.8, 10.0)
    kenshi.trigger_ryuu_tsui_sen(opp.wx, opp.wy, opponent=opp)
    assert kenshi.state == "RYUU_TSUI_SEN", f"Estado esperado RYUU_TSUI_SEN, obtido {kenshi.state}"
    print("  [OK] Kenshi Ryuu Tsui Sen (Item 17) verificado!", flush=True)

    # B. Okuni: Dokukiri (veneno com leques) e Roll dedicado
    okuni = Kabuki(10.0, 10.0)
    clouds = []
    okuni.trigger_dokukiri(12.0, 10.0, clouds)
    assert len(clouds) == 1, "Dokukiri deveria gerar 1 PoisonCloud"
    okuni.state = "IDLE"
    okuni.trigger_kabuki_roll(1.0, 0.0, [], [])
    assert okuni.state == "KABUKI_ROLL", f"Estado esperado KABUKI_ROLL, obtido {okuni.state}"
    assert okuni.is_invulnerable_dodge, "Okuni deve possuir i-frames no roll"
    print("  [OK] Okuni Dokukiri e Kabuki Roll verificados!", flush=True)

    # C. Teppo: Black Powder Ground Trap (Rebalanceamento: sem custo de pólvora) e Tumble Roll com recarga
    teppo = Rifleman(10.0, 10.0)
    traps = []
    teppo.has_ammo = True
    teppo.trigger_powder_trap(traps)
    assert len(traps) == 1, "Deveria criar 1 PowderTrap"
    assert isinstance(traps[0], PowderTrap)
    assert teppo.has_ammo is True, "Armadilha de pólvora não gasta mais munição (Rebalanceamento)"
    teppo.has_ammo = False  # Simula munição de disparo já gasta, independente da mina
    teppo.trigger_tumble_roll(1.0, 0.0, [])
    assert teppo.state == "RIFLE_ROLL"
    assert teppo.is_invulnerable_dodge, "Teppo deve possuir i-frames no tumble roll"
    teppo.update(teppo.roll_duration + 0.01, game_map)
    assert teppo.has_ammo, "Tumble roll deve recarregar munição de Teppo ao concluir o rolamento"
    print("  [OK] Teppo Powder Trap e Tumble Roll com recarga verificados!", flush=True)

    # D. Anne Bonny: Naval Artillery Strike (Hold & release de bala de canhão orbital)
    anne = PirateSwordswoman(10.0, 10.0)
    anne.cannon_cooldown_timer = 0.0
    anne.start_cannon_strike(14.0, 10.0)
    assert anne.is_aiming_cannon
    anne.update_cannon_strike(0.1, 15.0, 10.0)
    proj_anne = []
    anne.release_cannon_strike(proj_anne, [])
    assert not anne.is_aiming_cannon
    assert len(proj_anne) == 1
    assert isinstance(proj_anne[0], CannonballProjectile)
    # Anne pode dar roll com cutlass
    anne.trigger_roll(1.0, 0.0, [])
    assert anne.state == "ROLL"
    assert anne.is_invulnerable_dodge
    print("  [OK] Anne Bonny Naval Artillery Strike e Deck Roll verificados!", flush=True)

    # E. Tomoe: Ofuda Barrier (Secundária) e Flecha de Corda na 3ª ação
    tomoe = KyudoArcher(10.0, 10.0)
    tomoe.trigger_ofuda_barrier()
    assert tomoe.is_ofuda_active(), "Barreira Kami de Tomoe deve estar ativa"
    # Projétil inimigo repelido pelo Ofuda
    enemy_arrow = CannonballProjectile(10.5, 10.0, owner=anne)
    hostile_projs = [enemy_arrow]
    tomoe.update_ofuda_barrier_effects(0.016, hostile_projs)
    assert not enemy_arrow.is_active, "Projétil hostil deve ser desativado pelo Ofuda Ward"
    # Flecha de corda agora na 3ª ação (Dash/Roll)
    tomoe.start_rope_arrow_charge(14.0, 10.0, game_map)
    assert tomoe.is_charging_rope, "Tomoe deve carregar flecha de corda na 3ª ação"
    print("  [OK] Tomoe Ofuda Barrier e Flecha de Corda na 3ª ação verificados!", flush=True)

    print("\n=======================================================", flush=True)
    print("TODOS OS TESTES DA ETAPA 2 PASSARAM COM 100% DE SUCESSO!", flush=True)
    print("=======================================================\n", flush=True)

if __name__ == "__main__":
    test_step2_roster_actions()
