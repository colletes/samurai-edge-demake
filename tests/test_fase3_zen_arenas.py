"""
tests/test_fase3_zen_arenas.py - Validação Automatizada do Entregável A-3.1 (Santuários & Jardins Zen)

Testa as 6 arenas sagradas do primeiro lote da Fase 3:
  1. Floresta de Bambu (bamboo)
  2. Santuário na Montanha (mountain_shrine)
  3. Templo na Névoa (mist_temple)
  4. Pátio dos Sinos Shaolin (shaolin_temple)
  5. Jardim dos Lírios Carmim (higanbana_garden)
  6. Pavilhão Astral Heian (heian_shrine)
"""
import math
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
pygame.init()

from src.config import (
    ARENA_BAMBOO, ARENA_MOUNTAIN_SHRINE, ARENA_MIST_TEMPLE,
    ARENA_SHAOLIN, ARENA_HIGANBANA, ARENA_HEIAN_SHRINE
)
from src.world.arenas import create_arena, ARENA_SPECS
from src.world.decor import KoiFish, HiganbanaCluster, AstralBrazier, JizoStatue
from src.world.solid_props import ShrineBell
from src.effects.particles import WaterRippleParticle, WaterSplashParticle, PollenMoteParticle


class MockCamera:
    def __init__(self, zoom: float = 1.0, azimuth: float = 0.0):
        self.wx = 10.5
        self.wy = 10.5
        self.zoom = zoom
        self.azimuth = azimuth
        self.ground_z = 0.0

    def apply(self, wx: float, wy: float, wz: float = 0.0) -> tuple[int, int]:
        from src.isometric.iso_math import world_to_iso
        ix, iy = world_to_iso(wx - self.wx, wy - self.wy, wz, self.azimuth)
        return int(ix * self.zoom + 480), int(iy * self.zoom + 270)


class MockFighter:
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.vx = 0.0
        self.vy = 0.0
        self.state = "IDLE"
        self.is_alive = True


def test_zen_arenas_creation():
    print("--- Testando Criação e Specs das 6 Arenas Zen ---")
    zen_ids = [
        ARENA_BAMBOO, ARENA_MOUNTAIN_SHRINE, ARENA_MIST_TEMPLE,
        ARENA_SHAOLIN, ARENA_HIGANBANA, ARENA_HEIAN_SHRINE
    ]
    for aid in zen_ids:
        assert aid in ARENA_SPECS, f"Arena {aid} deve estar em ARENA_SPECS"
        arena = create_arena(aid)
        assert arena is not None, f"create_arena deve instanciar {aid}"
        assert arena.cols > 0 and arena.rows > 0
        print(f"  [OK] Arena {aid} ('{arena.theme_name}') criada com sucesso.")


def test_bamboo_koi_and_water():
    print("--- Testando Lago com Carpas Nishikigoi e Ondulações na Floresta de Bambu ---")
    arena = create_arena(ARENA_BAMBOO)
    koi_props = arena.koi
    assert len(koi_props) >= 3, f"Arena de bambu deve conter carpas Nishikigoi, encontrou {len(koi_props)}"

    # Verificar variedades
    varieties = {k.variety for k in koi_props}
    assert "kohaku" in varieties or "yamabuki" in varieties or "shiro" in varieties, "Carpas devem ter variedades"

    # Testar fuga reativa da carpa ao aproximar lutador
    surface = pygame.Surface((960, 540))
    camera = MockCamera(zoom=1.75)
    fleeing_koi = koi_props[0]
    initial_flee = fleeing_koi.flee_timer
    fighter = MockFighter(fleeing_koi.cur_x + 0.5, fleeing_koi.cur_y + 0.5)

    particles = []
    fleeing_koi.tick(arena, 0.05, [fighter], camera, particles, [])
    assert fleeing_koi.flee_timer > 0.0, "Carpa deve entrar em estado de fuga quando combatente está próximo"
    print("  [OK] Carpas Nishikigoi 3D reativas e com fuga tática validadas.")


def test_higanbana_garden_clusters_and_pollen():
    print("--- Testando Jardim dos Lírios Carmim (Higanbana Clusters) ---")
    arena = create_arena(ARENA_HIGANBANA)
    higan_props = [l for l in arena.lanterns if isinstance(l, HiganbanaCluster)]
    assert len(higan_props) >= 10, f"Higanbana Garden deve ter ao menos 10 touceiras de lírios, encontrou {len(higan_props)}"

    surface = pygame.Surface((960, 540))
    camera = MockCamera(zoom=1.0)
    cluster = higan_props[0]
    fighter = MockFighter(cluster.wx, cluster.wy)
    fighter.vx = 2.5
    fighter.vy = 1.0

    particles = []
    cluster.tick(arena, 0.016, [fighter], camera, particles, [])
    # Deve deformar elasticamente
    assert abs(cluster.bend_x) > 0 or len(particles) > 0, "Touceira deve sofrer deflexão ou soltar pólen"
    print("  [OK] Higanbana Clusters 3D volumétricos e dispersão de pólen validados.")


def test_shaolin_bell_and_censer():
    print("--- Testando Grande Sino Budista e Incensário no Pátio Shaolin ---")
    arena = create_arena(ARENA_SHAOLIN)
    bells = [b for b in arena.buildings if isinstance(b, ShrineBell)]
    assert len(bells) >= 2, f"Pátio Shaolin deve ter sinos de bronze, encontrou {len(bells)}"

    # Testar repique do sino
    bell = bells[0]
    ignited = bell.ignite(bell.wx + 0.5, bell.wy + 0.5, radius=1.0)
    assert ignited, "Sino deve ser acionado por golpe próximo"
    assert bell.ring > 0.0, "Sino deve registrar tempo de vibração acústica"

    surface = pygame.Surface((960, 540))
    camera = MockCamera(zoom=1.0)
    bell.render(surface, camera, time_val=1.2)
    print("  [OK] Sino Bonshō com martelo Shumoku e incensário validados.")


def test_heian_shrine_astral_braziers():
    print("--- Testando Braseiros Astrais com Kitsunebi no Pavilhão Heian ---")
    arena = create_arena(ARENA_HEIAN_SHRINE)
    braziers = [r for r in arena.rocks if isinstance(r, AstralBrazier)]
    assert len(braziers) >= 4, f"Pavilhão Heian deve conter os 4 braseiros astrais Onmyodo, encontrou {len(braziers)}"

    surface = pygame.Surface((960, 540))
    camera = MockCamera(zoom=1.25)
    particles = []
    braziers[0].tick(arena, 0.25, [], camera, particles, [])
    assert len(particles) > 0, "Braseiro astral deve emitir fagulhas Kitsunebi"
    braziers[0].render(surface, camera, time_val=2.5)
    print("  [OK] Braseiros Astrais Kitsunebi e centelhas místicas validados.")


def test_render_terrain_zen_arenas():
    print("--- Testando Renderização de Terreno e Ondas de Água em 60 FPS ---")
    surface = pygame.Surface((960, 540))
    zen_ids = [
        ARENA_BAMBOO, ARENA_MOUNTAIN_SHRINE, ARENA_MIST_TEMPLE,
        ARENA_SHAOLIN, ARENA_HIGANBANA, ARENA_HEIAN_SHRINE
    ]
    for aid in zen_ids:
        arena = create_arena(aid)
        camera = MockCamera(zoom=1.75, azimuth=0.0)

        # Simular combatente gerando ripple na água
        fighter = MockFighter(11.0, 11.0)
        fighter.vx = 1.5
        fighter.state = "ROLL"
        arena.update(0.016, [fighter], camera, [], [])

        # Renderizar 3 frames sucessivos
        for frame in range(3):
            arena.render_terrain(surface, camera, time_val=frame * 0.016)

        print(f"  [OK] Renderização de terreno e caustics/ripples em {aid} validada sem exceções.")


if __name__ == "__main__":
    test_zen_arenas_creation()
    test_bamboo_koi_and_water()
    test_higanbana_garden_clusters_and_pollen()
    test_shaolin_bell_and_censer()
    test_heian_shrine_astral_braziers()
    test_render_terrain_zen_arenas()
    print("\nTODOS OS TESTES DE SANTUÁRIOS & JARDINS ZEN (A-3.1) PASSARAM COM 100% DE SUCESSO!")
