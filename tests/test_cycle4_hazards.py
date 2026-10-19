"""
Testes unitários e de integração para Perigos e Detalhes das Arenas do Ciclo 4:
- Cemitério Gótico (Valerius): Morcegos, Fogos-fátuos (Slow), Mãos de Zumbi (Stun), Zumbis Andarilhos (Dano 1 / Destrutíveis)
- Pavilhão Astral Heian (Seimei): Feixes Mágicos, Animais Espirituais (Kitsune/Usagi), Talismã de Cura (+1 HP), Descarga do Pentagrama (Confusão/Controles Invertidos)
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

from src.entities.valerius import ValeriusNecromancer
from src.entities.seimei import SeimeiOnmyoji
from src.world.arenas import create_arena, ARENA_GOTHIC_CEMETERY, ARENA_HEIAN_SHRINE
from src.world.hazards import (
    GothicCemeteryHazard, HeianShrineHazard, CemeteryBat, WillOWisp,
    ZombieHandTrap, ZombieWalker, SpiritualBeast, HealingTalisman, PentagramDischarge
)
from src.isometric.camera import Camera
from src.combat.collision import CombatSystem


def test_gothic_cemetery_hazards():
    print("Testando perigos e detalhes do Cemitério Gótico...")
    arena = create_arena(ARENA_GOTHIC_CEMETERY)
    assert len(arena.hazards) > 0, "Cemitério Gótico deve possuir hazards configurados"
    cem_hazard = arena.hazards[0]
    assert isinstance(cem_hazard, GothicCemeteryHazard), "Hazard deve ser GothicCemeteryHazard"

    # 1. Morcegos
    assert len(cem_hazard.bats) > 0, "Devem existir morcegos sobrevoando o cemitério"
    bat = cem_hazard.bats[0]
    orig_x, orig_y = bat.wx, bat.wy
    bat.update(0.1)
    assert (bat.wx != orig_x or bat.wy != orig_y), "Morcegos devem se mover"

    # 2. Will-o'-the-Wisp e Slow
    p1 = ValeriusNecromancer(10.5, 10.5)
    wisp = WillOWisp(10.5, 10.5)
    particles = []
    banners = []
    wisp.update(0.1, [p1], particles, banners, 21, 21)
    assert p1.slow_timer > 0.0, "Will-o'-the-wisp deve aplicar slow no lutador atingido"

    # 3. Mãos de Zumbi e Stun
    p2 = SeimeiOnmyoji(10.5, 10.5)
    trap = ZombieHandTrap(10.5, 10.5)
    trap.state = ZombieHandTrap.STATE_ACTIVE
    trap.active_timer = 1.0
    trap.update(0.1, [p2], particles, banners, [])
    assert p2.state == "STUNNED", "Mãos de zumbi ao agarrar devem atordoar o lutador"

    # 4. Zumbi Walker dá 1 de dano ao alcançar lutador
    p2.state = "IDLE"
    p2.hp = 2
    walker = ZombieWalker(10.5, 10.5)
    walker.update(0.1, [p2], arena, particles, banners)
    assert p2.hp == 1, "Zumbi deve causar 1 de dano ao alcançar o personagem"
    assert not walker.is_alive, "Zumbi deve se desintegrar após causar dano"

    # 5. Destruição de zumbi e mãos por ataque do jogador
    p1.state = "ATTACK"
    p1.hitbox_active = True
    p1.hitbox_center = (10.5, 10.5)
    p1.hitbox_radius = 1.0
    fresh_walker = ZombieWalker(10.5, 10.5)
    fresh_trap = ZombieHandTrap(10.5, 10.5)
    cem_hazard.zombies = [fresh_walker]
    cem_hazard.traps = [fresh_trap]
    cem_hazard.check_combat_interactions(p1, p2, [], particles, banners, None)
    assert not fresh_walker.is_alive, "Golpe do jogador deve destruir o zumbi"
    assert fresh_trap.is_destroyed, "Golpe do jogador deve destruir as mãos"

    print("  -> Cemitério Gótico: 100% OK!")


def test_heian_shrine_hazards():
    print("Testando perigos e detalhes do Pavilhão Astral Heian...")
    arena = create_arena(ARENA_HEIAN_SHRINE)
    assert len(arena.hazards) > 0, "Pavilhão Astral Heian deve possuir hazards configurados"
    heian_hazard = arena.hazards[0]
    assert isinstance(heian_hazard, HeianShrineHazard), "Hazard deve ser HeianShrineHazard"

    # 1. Feixes de magia
    assert len(heian_hazard.streams) >= 4, "Devem existir pelo menos 4 feixes mágicos"
    for s in heian_hazard.streams:
        s.update(0.1)

    # 2. Animais mágicos
    beast = SpiritualBeast(kind="kitsune", start_edge="west")
    orig_x = beast.wx
    beast.update(0.1)
    assert beast.wx > orig_x, "Kitsune deve caminhar pelo cenário"

    # 3. Talismã de cura (+1 vida)
    p1 = ValeriusNecromancer(10.5, 10.5)
    p1.hp = 1
    talisman = HealingTalisman(10.5, 10.5)
    talisman.is_warn = False
    particles = []
    banners = []
    talisman.update(0.1, [p1], particles, banners)
    assert p1.hp == 2, "Talismã de cura deve recuperar 1 de HP do personagem"
    assert not talisman.is_active, "Talismã deve ser consumido após curar"

    # 4. Descarga do Pentagrama Central (Inversão de controles / Confusão)
    p2 = SeimeiOnmyoji(10.5, 10.5)
    pentagram = PentagramDischarge(cx=10.5, cy=10.5, radius=4.0)
    pentagram.state = PentagramDischarge.STATE_ACTIVE
    pentagram.update(0.1, [p2], particles, banners)
    assert getattr(p2, "confused_timer", 0.0) > 0.0, "Descarga do pentagrama deve aplicar temporizador de confusão"

    # 5. Decremento do temporizador no ciclo de dodge
    p2.update_dodge_timers(1.0)
    assert p2.confused_timer < 2.4, "O temporizador de confusão deve diminuir com dt"

    print("  -> Pavilhão Astral Heian: 100% OK!")


if __name__ == "__main__":
    test_gothic_cemetery_hazards()
    test_heian_shrine_hazards()
    print("\nTodos os testes de perigos e detalhes do Ciclo 4 passaram com sucesso!")
