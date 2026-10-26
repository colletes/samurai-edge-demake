"""
Testes automatizados do novo sistema de combate e HUD:
Overhaul de Seimei (Rondel Onmyōdō de 6 Elementos).
"""
import os
import sys
import pygame
pygame.init()

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.entities.seimei import SeimeiOnmyoji, ELEMENTS, ELEMENT_SPELL_NAMES
from src.entities.projectile import OfudaProjectile, TalismanWard
from src.ui.hud_rondel import RondelHUD, ELEMENT_DATA
from src.effects.cinematic_director import CinematicDirector
from src.entities.red_samurai import RedSamurai
from src.world.arenas import create_arena


def test_rondel_cycle_progression():
    print("Testando progressão e rotação do Rondel Onmyōdō de Seimei...")
    s = SeimeiOnmyoji(10.0, 10.0)
    projectiles = []

    expected_sequence = ["wood", "fire", "earth", "metal", "water", "yinyang"]

    # 1. Testar ciclo de 6 passos disparando Primário
    for expected_el in expected_sequence:
        assert s.current_element == expected_el, f"Esperado {expected_el}, obteve {s.current_element}"
        s.state = "IDLE"
        res = s.trigger_ofuda_toss(15.0, 10.0, projectiles)
        assert res is True
        proj = projectiles[-1]
        assert isinstance(proj, OfudaProjectile)
        assert proj.element == expected_el
        s.ofuda_timer = 0.0  # Reset para o teste

    # Após 6 passos, deve ter voltado para "wood"
    assert s.current_element == "wood"

    # 2. Testar ciclo de 6 passos acionando Secundário
    for expected_el in expected_sequence:
        assert s.current_element == expected_el
        s.state = "IDLE"
        res = s.trigger_sacred_ward(12.0, 10.0, projectiles=projectiles)
        assert res is True
        ward = projectiles[-1]
        assert isinstance(ward, TalismanWard)
        assert ward.element == expected_el
        s.ward_timer = 0.0

    assert s.current_element == "wood"
    print("  -> Progressão do Ciclo Onmyōdō: 100% OK!")


def test_rondel_hud_rendering():
    print("Testando renderização do RondelHUD...")
    s = SeimeiOnmyoji(10.0, 10.0)
    screen = pygame.Surface((1280, 720))

    hud = RondelHUD.get()
    # Renderiza para cada elemento
    for i in range(len(ELEMENTS)):
        s.rondel_index = i
        hud.render(screen, s, 640, 650, dt=0.016)

    print("  -> Renderização do RondelHUD no rodapé: 100% OK!")


def test_elemental_fatalities():
    print("Testando Fatalidades Elementais Adaptativas...")
    from src.isometric.camera import Camera
    cd = CinematicDirector()
    arena = create_arena("heian_shrine")
    cam = arena.attach_camera(Camera())
    surface = pygame.Surface((1280, 720))

    atk = SeimeiOnmyoji(10.0, 10.0)
    vic = RedSamurai(11.5, 10.0)

    for el in ("fire", "water", "wood", "metal", "earth", "yinyang"):
        cd = CinematicDirector()
        style = f"SEIMEI_FATAL_{el.upper()}"
        cd.trigger_fatal_strike(atk, vic, style, (1.0, 0.0))
        assert cd.is_active is True
        cd.update(0.05, arena, [])
        cd.render_letterbox(surface)
        cd.render_world_effects(surface, cam)

    print("  -> Fatalidades Elementais Adaptativas: 100% OK!")


if __name__ == "__main__":
    test_rondel_cycle_progression()
    test_rondel_hud_rendering()
    test_elemental_fatalities()
    print("TODOS OS TESTES DO OVERHAUL DO RONDEL PASSARAM COM SUCESSO!")
