"""
Testes automatizados dos kits de combate do Ciclo 4: Valerius (Necromante) e Seimei (Onmyoji).
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

from src.config import CHAR_VALERIUS, CHAR_SEIMEI
from src.entities.valerius import ValeriusNecromancer, SkeletonSummon
from src.entities.seimei import SeimeiOnmyoji
from src.entities.projectile import OfudaProjectile, TalismanWard
from src.combat.collision import CombatSystem
from src.world.arenas import create_arena


def test_valerius_combat_kit():
    print("Iniciando testes do kit de combate de Valerius...")
    v = ValeriusNecromancer(10.0, 10.0)
    assert v.name == "Valerius"
    assert v.char_type == "valerius"
    assert v.hp == 2
    assert v.can_parry is True

    # 1. Ataque Primário: Foice Fúnebre
    res = v.trigger_scythe_reap(12.0, 10.0)
    assert res is True
    assert v.state == "ATTACK"
    assert v.hitbox_active is True
    assert v.hitbox_damage == 2
    assert v.hitbox_radius == 1.35
    assert v.hitbox_center[0] > 10.0

    # 2. Parry
    v.state = "IDLE"
    v.hitbox_active = False
    assert v.trigger_parry() is True
    assert v.state == "PARRY"

    # 3. Ação Secundária: Evocar Mortos
    v.state = "IDLE"
    particles = []
    banners = []
    dummy_opponent = SeimeiOnmyoji(14.0, 10.0)
    res_summon = v.trigger_summon_undead(12.0, 10.0, particles=particles, opponent=dummy_opponent, banners=banners)
    assert res_summon is True
    assert v.summon is not None
    assert isinstance(v.summon, SkeletonSummon)
    assert v.summon.is_alive is True
    assert len(banners) > 0
    assert v.summon_timer > 0

    # 4. Atualização e perseguição do lacaio esqueleto
    arena = create_arena("bamboo")
    v.summon.state = "CHASING"  # pula transição de surgimento
    v.summon.update(0.1, arena, dummy_opponent, particles=particles, banners=banners)
    assert v.summon.facing_x > 0.0  # perseguindo na direção +X do oponente

    # 5. Oponente atinge e destrói o esqueleto
    assert v.summon.take_hit(damage=1, particles=particles) is True
    assert v.summon.is_alive is False

    # 6. Esquiva Névoa Espectral
    v.state = "IDLE"
    v.trigger_mist_dash(1.0, 0.0, particles=particles)
    assert v.state == "ROLL"
    print("  -> Valerius Necromancer: 100% OK!")


def test_seimei_combat_kit():
    print("Iniciando testes do kit de combate de Seimei...")
    s = SeimeiOnmyoji(10.0, 10.0)
    assert s.name == "Seimei"
    assert s.char_type == "seimei"
    assert s.hp == 2
    assert s.can_parry is True

    # 1. Ataque Primário: Ofuda Cortante
    projectiles = []
    particles = []
    res = s.trigger_ofuda_toss(15.0, 10.0, projectiles, particles=particles)
    assert res is True
    assert len(projectiles) == 1
    ofuda = projectiles[0]
    assert isinstance(ofuda, OfudaProjectile)
    assert ofuda.owner is s
    assert ofuda.damage == 1
    assert ofuda.speed == 15.0
    assert ofuda.dir_x > 0.9

    # 2. Atualização e alcance do Ofuda
    arena = create_arena("bamboo")
    assert ofuda.update(0.05, arena, particles) is True

    # 3. Ação Secundária: Selo Sagrado (Posicionamento consistente à frente)
    s.state = "IDLE"
    banners = []
    # Aiming at (50.0, 10.0) should orient Seimei rightwards, but place ward at s.wx + 1.35, NEVER at 50.0
    res_ward = s.trigger_sacred_ward(50.0, 10.0, projectiles=projectiles, particles=particles, banners=banners, game_map=arena)
    assert res_ward is True
    assert len(projectiles) == 2
    ward = projectiles[1]
    assert isinstance(ward, TalismanWard)
    assert ward.owner is s
    assert ward.state == "ARMED"
    assert abs(ward.wx - (s.wx + 1.35)) < 1e-3
    assert abs(ward.wy - s.wy) < 1e-3
    assert len(banners) > 0

    # 4. Absorção de projéteis inimigos pelo Kekkai
    enemy_bullet = OfudaProjectile(ward.wx + 0.2, ward.wy, 0.5, 1.0, 0.0, ValeriusNecromancer(0, 0))
    projectiles.append(enemy_bullet)
    ward.update(0.016, arena, particles, fighters=[s], projectiles=projectiles)
    assert enemy_bullet.is_active is False  # Projétil inimigo purificado/bloqueado pela barreira

    # 5. Detonação do Selo Sagrado quando inimigo entra no raio
    dummy_opponent = ValeriusNecromancer(ward.wx + 0.1, ward.wy)
    ward.update(0.1, arena, particles, fighters=[s, dummy_opponent], projectiles=projectiles)
    assert ward.state == "DETONATING"

    # 6. Esquiva Deslize Shikigami
    s.state = "IDLE"
    s.trigger_shikigami_glide(1.0, 0.0, particles=particles)
    assert s.state == "ROLL"
    print("  -> Seimei Onmyoji: 100% OK!")


def test_valerius_vs_seimei_combat_system():
    print("Iniciando simulação de combate entre Valerius e Seimei via CombatSystem...")
    arena = create_arena("bamboo")
    cs = CombatSystem()
    particles = []
    banners = []
    from src.isometric.camera import Camera
    camera = arena.attach_camera(Camera())
    projectiles = []

    p1 = ValeriusNecromancer(10.0, 10.0)
    p2 = SeimeiOnmyoji(14.0, 10.0)

    # 1. Seimei dispara Ofuda contra Valerius
    p2.trigger_ofuda_toss(10.0, 10.0, projectiles, particles)
    assert len(projectiles) == 1

    # Valerius apara com Parry
    p1.trigger_parry()
    # Aproxima ofuda do Valerius para colisão
    projectiles[0].wx = 10.2
    projectiles[0].wy = 10.0

    winner = cs.process_combat(p1, p2, arena, particles, banners, camera, projectiles, 0.016)
    assert winner is None
    # Ofuda foi absorvido ou refletido pelo Parry
    assert len(banners) > 0
def test_valerius_finisher_decap_and_skeleton_reanimation():
    print("Iniciando testes do novo Finisher primário de Valerius (Decapitação + Reanimação do Esqueleto)...")
    from src.effects.cinematic_director import CinematicDirector
    from src.entities.red_samurai import RedSamurai
    from src.isometric.camera import Camera

    cd = CinematicDirector()
    arena = create_arena("gothic_cemetery")
    cam = arena.attach_camera(Camera())
    surface = pygame.Surface((1280, 720))

    atk = ValeriusNecromancer(10.0, 10.0)
    vic = RedSamurai(11.2, 10.0)
    particles = []

    # 1. Disparo do golpe fatal
    cd.trigger_fatal_strike(atk, vic, "SOUL_REAP", (1.0, 0.0))
    assert cd.valerius_attacker is atk
    assert cd.valerius_victim is vic
    assert cd.valerius_decap_timer == 0.35
    assert cd.is_frozen() is True
    assert cd.current_kanji_text == "首刈骸生"

    # 2. Fase 1: Avanço da foice até a decapitação
    while cd.camera_setup_timer > 0 or cd.valerius_decap_timer > 0:
        cd.update(0.05, arena, particles)
    assert vic.state == "DYING_HEADLESS"
    assert cd.valerius_hook_timer > 0.0

    # 3. Fase 2: Recolhimento da foice e captura da cabeça na mão
    cd.render_world_effects(surface, cam)
    while cd.valerius_hook_timer > 0:
        cd.update(0.05, arena, particles)
    assert cd.valerius_reanimate_timer > 0.0

    # 4. Fase 3: Reanimação do cadáver decapitado em esqueleto
    cd.render_world_effects(surface, cam)
    while cd.valerius_reanimate_timer > 0 or cd.delayed_death_timer > 0:
        cd.update(0.05, arena, particles)

    # 5. Conclusão e geração do VoxelCorpse permanente
    assert len(cd.corpses) == 1
    corpse = cd.corpses[0]
    assert getattr(corpse, "reanimated_skeleton", False) is True
    assert getattr(corpse, "severed_head", None) is not None

    # 6. Renderização do esqueleto reanimado e da cabeça decepada sem exceções
    corpse.update(0.016, arena, particles)
    corpse.render(surface, cam)
    print("  -> Finisher Valerius (Decapitação + Esqueleto Reanimado): 100% OK!")


def test_seimei_finisher_ofuda_green_flames_to_ashes():
    print("Iniciando testes do novo Finisher primário de Seimei (Ofuda + Chamas Verdes às Cinzas)...")
    from src.effects.cinematic_director import CinematicDirector
    from src.entities.red_samurai import RedSamurai
    from src.isometric.camera import Camera

    cd = CinematicDirector()
    arena = create_arena("heian_shrine")
    cam = arena.attach_camera(Camera())
    surface = pygame.Surface((1280, 720))

    atk = SeimeiOnmyoji(10.0, 10.0)
    vic = RedSamurai(11.5, 10.0)
    particles = []

    # 1. Disparo do golpe fatal por Ofuda
    cd.trigger_fatal_strike(atk, vic, "SEAL_STASIS_COLLAPSE", (1.0, 0.0))
    assert cd.seimei_attacker is atk
    assert cd.seimei_victim is vic
    assert cd.seimei_talisman_timer == 0.32
    assert cd.is_frozen() is True
    assert cd.current_kanji_text == "青炎灰燼"

    # 2. Fase 1: Talismã cravado no alvo
    cd.render_world_effects(surface, cam)
    while cd.camera_setup_timer > 0 or cd.seimei_talisman_timer > 0:
        cd.update(0.05, arena, particles)
    assert cd.seimei_fire_timer > 0.0

    # 3. Fase 2: Chamas verdes espirituais rugindo
    cd.render_world_effects(surface, cam)
    while cd.seimei_fire_timer > 0:
        cd.update(0.05, arena, particles)
    assert cd.seimei_ash_timer > 0.0

    # 4. Fase 3: Corpo consumido em cinzas
    cd.render_world_effects(surface, cam)
    while cd.seimei_ash_timer > 0 or cd.delayed_death_timer > 0:
        cd.update(0.05, arena, particles)
    assert vic.state == "CORPSE_SLICED"

    # 5. Conclusão e geração do VoxelCorpse (apenas montículo de cinzas, sem sangue)
    assert len(cd.corpses) == 1
    corpse = cd.corpses[0]
    assert getattr(corpse, "is_ash_mound", False) is True
    assert len(corpse.pieces) == 0
    assert len(corpse.blood_droplets) == 0

    # 6. Renderização das cinzas fumegantes com brasas sem exceções
    corpse.update(0.016, arena, particles)
    corpse.render(surface, cam)
    print("  -> Finisher Seimei (Ofuda + Chamas Verdes às Cinzas): 100% OK!")


if __name__ == "__main__":
    test_valerius_combat_kit()
    test_seimei_combat_kit()
    test_valerius_vs_seimei_combat_system()
    test_valerius_finisher_decap_and_skeleton_reanimation()
    test_seimei_finisher_ofuda_green_flames_to_ashes()
    print("\nTodos os testes unitários do Ciclo 4 passaram com sucesso!")
