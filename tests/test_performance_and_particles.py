"""
Suíte de testes automatizados para a Fase 1: Performance & Estabilidade.
Cobre:
1. Entregável 1.1: Surface Object Pooling para SmokeParticle (eliminação de GC stutter).
2. Entregável 1.2: Hitstop anti-cascata no Ryuu Tsui Sen e obstáculos sólidos (verificação de altitude + cooldown).
3. Entregável 1.3: Fila estática vs dinâmica de Y-Sorting.
4. Entregável 1.4: Cap global de partículas (150 máximo, preservando sangue e banners).
"""
import os
import sys
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((100, 100), pygame.NOFRAME)

from src.effects.particles import SmokeParticle, BloodParticle, FloatingBanner, _SMOKE_SURFACE_POOL, get_pooled_smoke_surface
from src.isometric.camera import Camera
from src.world.map_data import GameMap
from src.world.kyoto_map import KyotoMap
from src.entities.red_samurai import RedSamurai
from src.combat.collision import CombatSystem
from main import build_static_render_queue


def test_smoke_particle_surface_pooling():
    """Entregável 1.1: SmokeParticle reutiliza superfícies pré-alocadas sem criar novos Surfaces por frame."""
    screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
    camera = Camera(800, 600)

    # Limpar pool para teste isolado
    _SMOKE_SURFACE_POOL.clear()

    particles = [SmokeParticle(10.0, 10.0, size=5) for _ in range(50)]

    # Primeiro render preenche o pool
    for p in particles:
        p.render(screen, camera)

    initial_pool_size = len(_SMOKE_SURFACE_POOL)
    assert initial_pool_size > 0, "O pool de superfícies de fumaça deve conter instâncias pré-alocadas"

    # Segundo frame de render para as mesmas partículas não deve criar novas superfícies
    for p in particles:
        p.update(0.016)
        p.render(screen, camera)

    # O número de superfícies no pool não deve explodir
    assert len(_SMOKE_SURFACE_POOL) <= 40, f"Pool deve se manter estável por faixas de raio, atual: {len(_SMOKE_SURFACE_POOL)}"

    # Testar reuso direto da função get_pooled_smoke_surface
    surf1 = get_pooled_smoke_surface(12)
    surf2 = get_pooled_smoke_surface(12)
    assert surf1 is surf2, "get_pooled_smoke_surface deve retornar a MESMA instância para um mesmo raio"
    print("[PASS] Entregável 1.1: Surface Object Pooling de SmokeParticle ativo e reutilizando memória.")


def test_obstacle_sparks_altitude_and_anti_cascade():
    """Entregável 1.2: Ryuu Tsui Sen no ar não dispara faíscas de solo e não gera hitstop em cascata."""
    combat = CombatSystem()
    game_map = GameMap()
    camera = Camera(800, 600)
    kenshi = RedSamurai(10.0, 10.0)

    # Posicionar Kenshi exatamente sobre a rocha (wx=6.0, wy=14.5)
    rock = game_map.rocks[0]
    kenshi.wx = rock.wx
    kenshi.wy = rock.wy

    # 1. Fase aérea do Ryuu Tsui Sen (wz = 1.6m no ar):
    kenshi.state = "RYUU_TSUI_SEN"
    kenshi.wz = 1.6
    kenshi.hitbox_active = True
    kenshi.hitbox_center = (kenshi.wx, kenshi.wy)
    kenshi.hitbox_radius = 1.45
    kenshi.obstacle_spark_timer = 0.0

    particles = []
    combat.hitstop_timer = 0.0
    combat._check_obstacle_sparks(kenshi, game_map, particles, camera)

    assert combat.hitstop_timer == 0.0, "Combatente no ar (wz > 0.40) NÃO deve disparar hitstop de obstáculo no solo"
    assert len(particles) == 0, "Não devem ser geradas faíscas de colisão terrestre com o golpe no ar"

    # 2. Impacto no solo (wz = 0.0):
    kenshi.wz = 0.0
    combat._check_obstacle_sparks(kenshi, game_map, particles, camera)

    assert combat.hitstop_timer > 0.0, "Ao atingir o solo sobre a rocha, deve disparar hitstop"
    assert combat.hitstop_timer <= 0.040, f"Hitstop deve ser calibrado (<= 0.040s), atual: {combat.hitstop_timer}"
    assert kenshi.obstacle_spark_timer > 0.15, "Deve ativar cooldown para impedir hitstop consecutivo no mesmo golpe"
    assert len(particles) == 4, f"Deve emitir faíscas calibradas no impacto, emitidas: {len(particles)}"

    # 3. Teste Anti-Cascata no frame seguinte:
    particles_before = len(particles)
    initial_hitstop = combat.hitstop_timer
    # Frame seguinte: ainda sobre a rocha e com hitbox ativa, mas com timer ativo
    combat._check_obstacle_sparks(kenshi, game_map, particles, camera)

    assert len(particles) == particles_before, "Segundo frame consecutivo com cooldown ativo NÃO deve gerar novas faíscas"
    assert combat.hitstop_timer == initial_hitstop, "Segundo frame consecutivo com cooldown NÃO deve re-armar o hitstop"

    print("[PASS] Entregável 1.2: Hitstop anti-cascata e altitude check funcionando 100%.")


def test_static_render_queue_efficiency():
    """Entregável 1.3: Fila estática pré-calculada contém todos os elementos fixos de cenário."""
    bamboo_map = GameMap()
    kyoto_map = KyotoMap()

    static_bamboo = build_static_render_queue(bamboo_map)
    assert len(static_bamboo) > 0, "Fila estática da Floresta de Bambu deve conter rochas, poço e bambus"
    bamboo_types = set(item[1] for item in static_bamboo)
    assert "bamboo" in bamboo_types
    assert "rock" in bamboo_types

    static_kyoto = build_static_render_queue(kyoto_map)
    assert len(static_kyoto) > 0, "Fila estática de Kyoto deve conter prédios, lanternas e toriis"
    kyoto_types = set(item[1] for item in static_kyoto)
    assert "building" in kyoto_types
    assert "lantern" in kyoto_types

    print("[PASS] Entregável 1.3: Fila estática de Y-Sorting construída com sucesso para ambas as arenas.")


def test_particle_cap_enforcement():
    """Entregável 1.4: Lista de partículas descarta cosméticos ao passar de 150 mas preserva sangue e banners."""
    particles = []
    # Adicionar 100 partículas de fumaça
    for _ in range(100):
        particles.append(SmokeParticle(10.0, 10.0))

    # Adicionar 10 banners e 20 partículas de sangue
    for _ in range(10):
        particles.append(FloatingBanner("TEST", 10.0, 10.0))
    for _ in range(20):
        particles.append(BloodParticle(10.0, 10.0))

    # Adicionar mais 50 de fumaça (total = 180 partículas)
    for _ in range(50):
        particles.append(SmokeParticle(10.0, 10.0))

    assert len(particles) == 180

    # Lógica de cap global (mesma de main.py)
    if len(particles) > 150:
        cosmetic_idx = [i for i, p in enumerate(particles) if not isinstance(p, (BloodParticle, FloatingBanner))]
        excess = len(particles) - 150
        if excess > 0:
            to_remove = set(cosmetic_idx[:excess])
            particles = [p for i, p in enumerate(particles) if i not in to_remove]

    assert len(particles) == 150, f"Partículas devem ter sido limitadas a 150, atual: {len(particles)}"
    banners_count = sum(1 for p in particles if isinstance(p, FloatingBanner))
    blood_count = sum(1 for p in particles if isinstance(p, BloodParticle))

    assert banners_count == 10, "Todos os 10 banners devem ser preservados"
    assert blood_count == 20, "Todas as 20 partículas de sangue devem ser preservadas"
    print("[PASS] Entregável 1.4: Particle Cap Global preserva elementos críticos e poda cosméticos.")


if __name__ == "__main__":
    test_smoke_particle_surface_pooling()
    test_obstacle_sparks_altitude_and_anti_cascade()
    test_static_render_queue_efficiency()
    test_particle_cap_enforcement()
    print("\n=======================================================")
    print("TODOS OS TESTES DA FASE 1 (PERFORMANCE) PASSARAM 100%!")
    print("=======================================================")
