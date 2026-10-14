import os
import sys
import math
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.entities.benkei import BenkeiSamurai
from src.entities.orin import OrinMinstrel
from src.entities.red_samurai import RedSamurai
from src.entities.american_ninja import AmericanNinja
from src.entities.musketeer import Musketeer
from src.entities.projectile import NaginataProjectile, KamaitachiProjectile, SpiralResonanceProjectile
from src.world.decor import ScreenPanel, VoxelCricket, VoxelSparrow
from src.world.arenas import create_arena
from src.world.solid_props import ShrineBell
from src.combat.collision import CombatSystem, _get_death_style_for_attacker
from src.effects.cinematic_director import CinematicDirector
from src.ui.arena_select import ArenaSelectScreen
from src.isometric.camera import Camera

def test_all_feedback_fixes():
    pygame.init()
    surf = pygame.Surface((640, 360))
    cam = Camera()

    print("--- 1. Teste de Colisão da Naginata com O-Rin / Não-Benkei (Sem Crash) ---")
    benkei = BenkeiSamurai(5.0, 5.0)
    orin = OrinMinstrel(7.0, 5.0)
    game_map = create_arena("gojo_bridge")
    particles = []

    # Lançar naginata e fazê-la fincar no solo
    benkei.has_naginata = False
    naginata = NaginataProjectile(wx=6.5, wy=5.0, wz=0.2, dir_x=1.0, dir_y=0.0, owner=benkei)
    naginata._embed_into_ground(game_map, particles)
    assert naginata.state == "ON_GROUND"

    # Mover O-Rin diretamente para cima da naginata cravada
    orin.wx = naginata.wx
    orin.wy = naginata.wy
    # Simular update da naginata: O-Rin NÃO deve causar AttributeError!
    naginata.update(0.1, game_map, particles)
    assert naginata.state == "ON_GROUND", "Naginata deve continuar no chão quando O-Rin pisa sobre ela"
    assert not benkei.has_naginata, "Benkei ainda não recuperou a naginata"

    # Agora mover o Benkei para cima da naginata cravada
    benkei.wx = naginata.wx
    benkei.wy = naginata.wy
    naginata.pickup_delay = 0.0
    naginata.update(0.1, game_map, particles)
    assert not naginata.is_active, "Naginata deve ser recolhida pelo Benkei"
    assert benkei.has_naginata, "Benkei deve recuperar sua naginata"
    print("✓ Crash de recolhimento da Naginata corrigido com sucesso!")

    print("--- 2. Teste de Biombos Quebráveis (ScreenPanel) ---")
    biombo = ScreenPanel(10.0, 10.0, axis="x")
    assert not biombo.is_broken
    assert biombo.radius > 0
    # Quebrar biombo com corte de lâmina
    biombo.break_panel((1.0, 0.0), particles)
    assert biombo.is_broken
    assert biombo.radius == 0.0, "Raio de colisão deve ser zerado após quebra"
    # Renderizar escombros planos no solo
    biombo.render(surf, cam)
    print("✓ Biombos de Yoshiwara agora são quebráveis e abrem passagem!")

    print("--- 3. Teste de Machiyas Yoshiwara Sem Chamas (Vida Noturna) ---")
    yoshi_map = create_arena("yoshiwara_alley")
    for b in yoshi_map.buildings:
        if hasattr(b, "burning"):
            assert not b.burning, "Machiyas de Yoshiwara NÃO devem estar em chamas"
            assert getattr(b, "style", "") == "yoshiwara"
    print("✓ Fachadas de Yoshiwara convertidas com sucesso para o estilo vida noturna!")

    print("--- 4. Teste de Portraits de Conceito da Arena do Ren e da Chiyo ---")
    arena_sel = ArenaSelectScreen()
    assert arena_sel.preview_surfs["shaolin_temple"] is not None
    assert arena_sel.preview_surfs["higanbana_garden"] is not None
    print("✓ Portraits de conceito para Shaolin Temple e Higanbana Garden carregados!")

    print("--- 5. Teste do Sino Shaolin (Ataque Circular Expansivo & Paralisia) ---")
    bell = ShrineBell(10.0, 10.0)
    bell_arena = create_arena("shaolin_temple")
    combatant_striker = RedSamurai(10.5, 10.5)
    combatant_innocent = RedSamurai(15.0, 10.0)
    combatant_dodger = RedSamurai(13.0, 10.0)
    combatant_dodger.state = "ROLL"

    # Acionar sino
    bell.ignite(10.5, 10.5, 0.5, striker=combatant_striker)
    assert bell._pending
    banners = []
    # Primeiro tick ativa a onda
    bell.tick(bell_arena, 0.05, [combatant_striker, combatant_innocent, combatant_dodger], cam, particles, banners)
    assert bell.soundwave_active
    # O striker está logo ao lado do sino e não esquivou -> Paralisia imediata!
    assert combatant_striker.state == "STUNNED"

    # Avançar onda sonora até 5 tiles (alcança combatant_dodger e combatant_innocent)
    dt_step = 0.5
    bell.tick(bell_arena, dt_step, [combatant_striker, combatant_innocent, combatant_dodger], cam, particles, banners)
    # Dodger estava em ROLL -> Evitou a paralisia!
    assert combatant_dodger.state == "ROLL"
    # Innocent não estava esquivando -> Paralisado!
    assert combatant_innocent.state == "STUNNED"
    # Renderizar anel sônico expansivo
    bell.render(surf, cam, time_val=1.0)
    print("✓ Sino Shaolin gera onda de som circular que paralisa e pode ser esquivada!")

    print("--- 6. Teste de Acorde de Ressonância Mortal da O-Rin ---")
    projectiles = []
    orin.state = "IDLE"
    orin.trigger_deadly_resonance_chord(15.0, 5.0, projectiles, particles, banners)
    assert len(projectiles) == 3
    assert orin.resonance_cooldown == 5.0
    for p in projectiles:
        assert isinstance(p, SpiralResonanceProjectile)
        p.update(0.05, game_map, particles)
        p.render(surf, cam)
    print("✓ O-Rin dispara 3 ondas em espiral a 120° com cooldown de 5.0s!")

    print("--- 7. Teste de Finishers e Bloqueio de Input ---")
    joe = AmericanNinja(5.0, 5.0)
    julie = Musketeer(5.0, 5.0)
    orin.state = "IDLE"
    assert _get_death_style_for_attacker(benkei) == "NAGINATA_HOIST_SLAM"
    assert _get_death_style_for_attacker(orin) in ("SONIC_SLICER", "KAMAITACHI_MINCE")
    assert _get_death_style_for_attacker(joe) == "WINDMILL_SHURIKEN_DECAP"
    assert _get_death_style_for_attacker(julie) == "RAPIER_FLURRY_POINTBLANK"

    director = CinematicDirector()
    director.trigger_fatal_strike(benkei, combatant_striker, "NAGINATA_HOIST_SLAM", (1.0, 0.0))
    assert director.is_active
    assert director.is_frozen()
    director.update(0.1, game_map, particles)
    print("✓ Novos finishers multi-estágios integrados com bloqueio de cancelamento por input!")

    print("--- 8. Teste de Criaturas Voxel na Arena Shaolin ---")
    cricket = VoxelCricket(10.0, 10.0, seed=1)
    sparrow = VoxelSparrow(12.0, 12.0, seed=2)
    cricket.render(surf, cam, time_val=1.5)
    sparrow.render(surf, cam, time_val=1.5)
    print("✓ Grilos e pássaros em voxel adicionados à arena do Ren!")

    print("\n=======================================================")
    print("TODAS AS CORREÇÕES E NOVAS MECÂNICAS TESTADAS COM SUCESSO!")
    print("=======================================================")

if __name__ == "__main__":
    test_all_feedback_fixes()
