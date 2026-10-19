"""
Script para capturar e validar visualmente os novos Finishers primários do Ciclo 4:
1. Valerius: Decapitação por foice, cabeça presa na ponta, recolhida na mão e reanimação do esqueleto.
2. Seimei: Ofuda sagrado, chamas verdes espirituais rugindo e consumo até restarem apenas cinzas.
"""
import os
import sys
import math
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.entities.valerius import ValeriusNecromancer
from src.entities.seimei import SeimeiOnmyoji
from src.entities.red_samurai import RedSamurai
from src.effects.cinematic_director import CinematicDirector
from src.world.arenas import create_arena
from src.isometric.camera import Camera

def capture_finishers():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.font.init()

    screen = pygame.Surface((1280, 720))
    cd = CinematicDirector()
    particles = []

    # -------------------------------------------------------------
    # 1. VALERIUS FINISHER CAPTURE (Cemetery Arena)
    # -------------------------------------------------------------
    arena_cemetery = create_arena("gothic_cemetery")
    cam_cemetery = arena_cemetery.attach_camera(Camera())

    v_atk = ValeriusNecromancer(10.0, 10.0)
    v_vic = RedSamurai(11.2, 10.0)

    cd.trigger_fatal_strike(v_atk, v_vic, "SOUL_REAP", (1.0, 0.0))

    # Avança até a decapitação e cabeça na ponta da foice
    while cd.camera_setup_timer > 0 or cd.valerius_decap_timer > 0:
        cd.update(0.04, arena_cemetery, particles)

    # Avança no recolhimento
    for _ in range(6):
        cd.update(0.04, arena_cemetery, particles)

    # Renderiza o momento do recolhimento da cabeça decepada
    screen.fill((18, 16, 24))
    arena_cemetery.render_terrain(screen, cam_cemetery, 1.0)
    v_vic.render(screen, cam_cemetery)
    v_atk.render(screen, cam_cemetery)
    cd.render_world_effects(screen, cam_cemetery)
    cd.apply_cinematic_filter(screen)

    os.makedirs("docs/screenshots/finishers", exist_ok=True)
    shot_valerius_decap = "docs/screenshots/finishers/valerius_decap_hook.png"
    pygame.image.save(screen, shot_valerius_decap)
    print(f"Capturado: {shot_valerius_decap}")

    # Avança até a reanimação do esqueleto e conclusão
    while cd.is_frozen() or cd.delayed_death_timer > 0:
        cd.update(0.04, arena_cemetery, particles)

    # Renderiza o esqueleto decapitado reanimado em pé no campo
    screen.fill((18, 16, 24))
    arena_cemetery.render_terrain(screen, cam_cemetery, 1.0)
    for c in cd.corpses:
        c.render(screen, cam_cemetery)
    v_atk.render(screen, cam_cemetery)
    cd.apply_cinematic_filter(screen)

    shot_valerius_skeleton = "docs/screenshots/finishers/valerius_skeleton_reanimated.png"
    pygame.image.save(screen, shot_valerius_skeleton)
    print(f"Capturado: {shot_valerius_skeleton}")

    # -------------------------------------------------------------
    # 2. SEIMEI FINISHER CAPTURE (Heian Shrine Arena)
    # -------------------------------------------------------------
    cd.reset_round()
    particles.clear()
    arena_heian = create_arena("heian_shrine")
    cam_heian = arena_heian.attach_camera(Camera())

    s_atk = SeimeiOnmyoji(10.0, 10.0)
    s_vic = RedSamurai(11.4, 10.0)

    cd.trigger_fatal_strike(s_atk, s_vic, "SEAL_STASIS_COLLAPSE", (1.0, 0.0))

    # Avança até as chamas verdes espirituais
    while cd.camera_setup_timer > 0 or cd.seimei_talisman_timer > 0:
        cd.update(0.04, arena_heian, particles)
    for _ in range(8):
        cd.update(0.04, arena_heian, particles)

    # Renderiza as chamas verdes espirituais rugindo sobre a vítima
    screen.fill((20, 22, 28))
    arena_heian.render_terrain(screen, cam_heian, 1.0)
    s_vic.render(screen, cam_heian)
    s_atk.render(screen, cam_heian)
    cd.render_world_effects(screen, cam_heian)
    cd.apply_cinematic_filter(screen)

    shot_seimei_flames = "docs/screenshots/finishers/seimei_green_flames.png"
    pygame.image.save(screen, shot_seimei_flames)
    print(f"Capturado: {shot_seimei_flames}")

    # Avança até o corpo ser consumido em cinzas
    while cd.is_frozen() or cd.delayed_death_timer > 0:
        cd.update(0.04, arena_heian, particles)

    # Renderiza o montículo de cinzas sagradas com brasas e talismã
    screen.fill((20, 22, 28))
    arena_heian.render_terrain(screen, cam_heian, 1.0)
    for c in cd.corpses:
        c.render(screen, cam_heian)
    s_atk.render(screen, cam_heian)
    cd.apply_cinematic_filter(screen)

    shot_seimei_ashes = "docs/screenshots/finishers/seimei_smoldering_ashes.png"
    pygame.image.save(screen, shot_seimei_ashes)
    print(f"Capturado: {shot_seimei_ashes}")

    print("\nTodos os frames dos novos finishers foram capturados com sucesso!")

if __name__ == "__main__":
    capture_finishers()
