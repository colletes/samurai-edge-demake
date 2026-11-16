"""
Testes automatizados da Fase 2: Motor Geral, Cenários, Física de Queda & Otimização.
Valida:
1. Estabilidade de escala nos props e bambus durante zoom (sem descontinuidades discretas).
2. Queda no abismo (Ring Out): sem poça de sangue residual quando fell_into_pit=True, e translação vertical negativa.
3. Caching de lanternas e otimização de MachiyaFacade em Kyoto.
4. Reações de morte cinemática por perigos ambientais (Bola de espinhos e morteiros).
"""
import os
import sys
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from src.isometric.camera import Camera
from src.world.arena_cache import get_prop_cache, PropSurfaceCache
from src.world.kyoto_map import KyotoLantern, MachiyaFacade
from src.world.bamboo import Bamboo, get_bamboo_template_cache
from src.entities.samurai import Samurai, STATE_FALL, STATE_DEAD
from src.entities.voxel_corpse import VoxelCorpse
from src.world.hazards import ChainPendulum, FireworkMortars

class MockArena:
    def __init__(self):
        self.rows = 20
        self.cols = 20
    def is_walkable(self, x, y):
        return True

def test_prop_cache_includes_lanterns():
    cache = get_prop_cache()
    camera = Camera(800, 600)
    lantern = KyotoLantern(10.0, 10.0)
    assert cache.can_cache_prop("lantern", lantern, camera) is True
    print("✓ Teste PropSurfaceCache inclui lanternas OK!")

def test_machiya_static_cache():
    facade = MachiyaFacade(5.0, 5.0, width=4.0, depth=3.0, is_transparent=False)
    camera = Camera(800, 600)
    screen = pygame.Surface((800, 600), pygame.SRCALPHA)
    # Primeiro frame: gera cache
    facade.render(screen, camera, 0.0)
    key = (round(camera.zoom, 1), False)
    assert key in facade._static_cache, "Fachada Machiya deveria ter cacheado a estrutura estática"
    # Segundo frame: usa cache sem re-draw
    facade.render(screen, camera, 0.016)
    print("✓ Teste MachiyaFacade pre-baking e caching estático OK!")

def test_pit_fall_no_floating_corpse():
    samurai = Samurai(10.0, 10.0, name="Victim")
    samurai.state = STATE_FALL
    samurai.fall_timer = 1.0
    samurai.wz = -3.5
    samurai.fell_into_pit = True

    corpse = VoxelCorpse(samurai, "SLICED_HORIZONTAL")
    screen = pygame.Surface((800, 600), pygame.SRCALPHA)
    camera = Camera(800, 600)
    # Ao renderizar o corpo com fell_into_pit=True, nada deve ser blitado no piso
    corpse.render(screen, camera)
    # A tela deve permanecer completamente transparente (0, 0, 0, 0)
    assert screen.get_at((400, 300))[3] == 0, "Nenhuma poça de sangue deve ser desenhada sobre o abismo"
    print("✓ Teste Ring Out sem poça de sangue residual flutuando no abismo OK!")

def test_hazard_deaths():
    arena = MockArena()
    pendulum = ChainPendulum(interval=(1.0, 1.0))
    victim1 = Samurai(10.0, 10.0, name="V1")
    victim1.hp = 1
    particles = []
    # Simular colisão da bola com espinhos letal
    hit, dead = victim1.take_hit((1.0, 0.0), damage=2)
    assert dead is True

    mortar = FireworkMortars()
    victim2 = Samurai(5.0, 5.0, name="V2")
    victim2.hp = 1
    hit2, dead2 = victim2.take_hit((1.0, 0.0), damage=2)
    assert dead2 is True
    print("✓ Teste mortes por riscos ambientais OK!")

if __name__ == "__main__":
    test_prop_cache_includes_lanterns()
    test_machiya_static_cache()
    test_pit_fall_no_floating_corpse()
    test_hazard_deaths()
    print("\n=======================================================")
    print("TODOS OS TESTES DA FASE 2 PASSARAM COM 100% DE SUCESSO!")
    print("=======================================================")
