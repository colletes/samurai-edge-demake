"""
Testes automatizados de esquiva contra projéteis e magias de Seimei (Ofuda e TalismanWard).
Garante que todos os projéteis e feitiços não explosivos sejam evitados com dodge por
qualquer combatente em i-frames (Samurai, Teppo, Okuni, Hanzo, etc.).
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.entities.samurai import Samurai, STATE_ROLL
from src.entities.aoi import AoiHuntress
from src.entities.rifleman import Rifleman
from src.entities.kabuki import Kabuki
from src.entities.yellow_ninja import YellowNinja
from src.entities.seimei import SeimeiOnmyoji, ELEMENTS
from src.entities.projectile import OfudaProjectile, TalismanWard
from src.combat.collision import CombatSystem, is_fighter_evading
from src.world.kyoto_map import KyotoMap
from src.isometric.camera import Camera


def test_is_fighter_evading_all_classes():
    """Valida se o estado de esquiva é detectado corretamente para todas as classes."""
    s = Samurai(10, 10, "musashi")
    assert not is_fighter_evading(s)
    s.trigger_roll(1, 0)
    assert is_fighter_evading(s)

    teppo = Rifleman(10, 10)
    assert not is_fighter_evading(teppo)
    teppo.trigger_roll(1, 0)
    assert is_fighter_evading(teppo)

    kabuki = Kabuki(10, 10)
    assert not is_fighter_evading(kabuki)
    kabuki.trigger_roll(1, 0)
    assert is_fighter_evading(kabuki)

    hanzo = YellowNinja(10, 10)
    assert not is_fighter_evading(hanzo)
    hanzo.trigger_roll(1, 0)
    assert is_fighter_evading(hanzo)


def test_ofuda_dodge_all_elements():
    """Valida que todos os elementos de Ofuda são evitados com dodge."""
    arena = KyotoMap()
    cam = Camera()
    cs = CombatSystem()
    seimei = SeimeiOnmyoji(13, 10)

    for el in ["wood", "fire", "water", "metal", "earth", "yinyang"]:
        # Samurai dodge
        s = Samurai(10, 10, "musashi")
        s.trigger_roll(1, 0)
        ofuda = OfudaProjectile(11, 10, 0.45, -1, 0, owner=seimei, element=el)
        cs.process_combat(s, seimei, arena, [], [], cam, [ofuda], dt=0.016)
        assert s.hp == 2, f"Samurai deve evitar Ofuda {el}"
        assert s.state == STATE_ROLL, f"Samurai deve permanecer em ROLL ao desviar de Ofuda {el}"

        # Teppo dodge
        teppo = Rifleman(10, 10)
        teppo.trigger_roll(1, 0)
        ofuda_teppo = OfudaProjectile(11, 10, 0.45, -1, 0, owner=seimei, element=el)
        cs.process_combat(teppo, seimei, arena, [], [], cam, [ofuda_teppo], dt=0.016)
        assert teppo.hp == 2, f"Teppo deve evitar Ofuda {el}"
        assert teppo.state == "RIFLE_ROLL", f"Teppo deve permanecer em RIFLE_ROLL ao desviar de Ofuda {el}"

        # Kabuki dodge
        kabuki = Kabuki(10, 10)
        kabuki.trigger_roll(1, 0)
        ofuda_kabuki = OfudaProjectile(11, 10, 0.45, -1, 0, owner=seimei, element=el)
        cs.process_combat(kabuki, seimei, arena, [], [], cam, [ofuda_kabuki], dt=0.016)
        assert kabuki.hp == 2, f"Kabuki deve evitar Ofuda {el}"
        assert kabuki.state == "KABUKI_ROLL", f"Kabuki deve permanecer em KABUKI_ROLL ao desviar de Ofuda {el}"

        # Hanzo jump dodge
        hanzo = YellowNinja(10, 10)
        hanzo.trigger_roll(1, 0)
        ofuda_hanzo = OfudaProjectile(11, 10, 0.45, -1, 0, owner=seimei, element=el)
        cs.process_combat(hanzo, seimei, arena, [], [], cam, [ofuda_hanzo], dt=0.016)
        assert hanzo.hp == 2, f"Hanzo deve evitar Ofuda {el}"
        assert hanzo.state == "JUMP", f"Hanzo deve permanecer em JUMP ao desviar de Ofuda {el}"


def test_talisman_ward_dodge():
    """Valida que barreiras e selos não-explosivos são evitados durante a esquiva."""
    arena = KyotoMap()
    cam = Camera()
    cs = CombatSystem()
    seimei = SeimeiOnmyoji(13, 10)

    for el in ["wood", "water", "metal", "earth", "yinyang"]:
        # Samurai evade ward
        s = Samurai(10, 10, "musashi")
        s.trigger_roll(1, 0)
        ward = TalismanWard(10.5, 10.0, owner=seimei, element=el)
        cs.process_combat(s, seimei, arena, [], [], cam, [ward], dt=0.016)
        assert s.hp == 2 and s.state == STATE_ROLL, f"Samurai deve ignorar ward armado {el} ao rolar"

        ward.state = "DETONATING"
        ward.detonate_timer = 0.05
        cs.process_combat(s, seimei, arena, [], [], cam, [ward], dt=0.016)
        assert s.hp == 2 and s.state == STATE_ROLL, f"Samurai deve evitar detonação de ward {el} ao rolar"


def test_non_dodging_target_gets_hit():
    """Valida que alvos sem esquiva continuam sendo atingidos normalmente."""
    arena = KyotoMap()
    cam = Camera()
    cs = CombatSystem()
    seimei = SeimeiOnmyoji(13, 10)

    s = Samurai(10, 10, "musashi")
    ofuda = OfudaProjectile(10, 10, 0.45, -1, 0, owner=seimei, element="wood")
    cs.process_combat(s, seimei, arena, [], [], cam, [ofuda], dt=0.016)
    assert s.hp < 2, "Alvo parado deve sofrer dano do Ofuda"

    s2 = Samurai(10, 10, "musashi")
    ward = TalismanWard(10.5, 10.0, owner=seimei, element="wood")
    ward.state = "DETONATING"
    ward.detonate_timer = 0.05
    cs.process_combat(s2, seimei, arena, [], [], cam, [ward], dt=0.016)
    assert s2.hp < 2 or s2.state == "STUNNED", "Alvo parado deve ser atingido/atordoado pelo ward"


def test_ofuda_stops_at_hedges_and_solid_obstacles():
    """Valida que todos os projéteis de Seimei colidem e param em objetos sólidos (e.g. cercas vivas da Julie)."""
    from src.world.arenas import create_arena, ARENA_BAROQUE_COURT
    from src.world.decor import HedgeBlock

    arena = create_arena(ARENA_BAROQUE_COURT)
    hedges = [r for r in arena.rocks if isinstance(r, HedgeBlock)]
    assert len(hedges) > 0, "A arena barroca deve conter cercas vivas (HedgeBlock)"
    hedge = hedges[0]

    seimei = SeimeiOnmyoji(hedge.wx - 2.0, hedge.wy)
    s = Samurai(hedge.wx + 1.5, hedge.wy, "musashi")
    cs = CombatSystem()
    cam = Camera()

    for el in ["wood", "fire", "water", "metal", "earth", "yinyang"]:
        s.hp = 2
        ofuda = OfudaProjectile(hedge.wx - 1.5, hedge.wy, 0.45, 1.0, 0.0, owner=seimei, element=el)
        projs = [ofuda]
        for _ in range(30):
            if not ofuda.is_active:
                break
            ofuda.update(0.016, arena, [])
            cs.process_combat(s, seimei, arena, [], [], cam, projs, dt=0.016)

        assert not ofuda.is_active, f"Ofuda {el} deveria ter sido bloqueado pela cerca viva!"
        assert s.hp == 2, f"Oponente atrás da cerca viva não deve sofrer dano do Ofuda {el}!"


def test_aoi_snow_slide_dodge_seimei_projectiles_and_wards():
    """
    Valida especificamente que Aoi desvia com 100% de confiabilidade de todos os feitiços
    de Ofuda e barreiras de TalismanWard de Seimei durante seu deslize de esquiva (Snow Slide)
    e recuperação imediata, mesmo contra dispersões triplas (Madeira) e teleguiados (Água).
    """
    arena = KyotoMap()
    cam = Camera()
    cs = CombatSystem()

    # 1. Esquiva contra OfudaProjectile de todos os elementos
    for el in ELEMENTS:
        for dist in [2.5, 4.0, 5.5]:
            for roll_dir in [(1, 0), (-1, 0), (0, 1), (0.7, 0.7), (-0.7, 0.7)]:
                seimei = SeimeiOnmyoji(10.0 + dist, 10.0)
                seimei.rondel_index = ELEMENTS.index(el)
                aoi = AoiHuntress(10.0, 10.0)
                projectiles = []
                particles = []
                banners = []

                seimei.trigger_ofuda_toss(10.0, 10.0, projectiles)
                dodged = False
                for _ in range(50):
                    dt = 0.016
                    p = projectiles[0] if projectiles else None
                    if p and not dodged:
                        d = ((p.wx - aoi.wx)**2 + (p.wy - aoi.wy)**2)**0.5
                        if d <= 2.2:
                            aoi.trigger_snow_slide(roll_dir[0], roll_dir[1])
                            dodged = True
                    aoi.update(dt, arena, particles, opponent=seimei, projectiles=projectiles, banners=banners)
                    seimei.update(dt, arena, particles, opponent=aoi, projectiles=projectiles, banners=banners)
                    cs.process_combat(aoi, seimei, arena, particles, banners, cam, projectiles, dt)

                assert aoi.hp == 2, f"Aoi deve sobreviver e desviar com sucesso de Ofuda {el} a dist {dist} na direção {roll_dir}!"

    # 2. Esquiva contra TalismanWard (pré-existente e armado)
    for el in ["wood", "water", "metal", "earth", "yinyang"]:
        seimei = SeimeiOnmyoji(14.0, 10.0)
        seimei.rondel_index = ELEMENTS.index(el)
        aoi = AoiHuntress(8.5, 10.0)
        projectiles = []
        particles = []
        banners = []

        ward = TalismanWard(10.5, 10.0, owner=seimei, element=el)
        projectiles.append(ward)

        for f in range(60):
            dt = 0.016
            if f == 10:
                aoi.trigger_snow_slide(1, 0)
            aoi.update(dt, arena, particles, opponent=seimei, projectiles=projectiles, banners=banners)
            seimei.update(dt, arena, particles, opponent=aoi, projectiles=projectiles, banners=banners)
            cs.process_combat(aoi, seimei, arena, particles, banners, cam, projectiles, dt)

        assert aoi.hp == 2, f"Aoi deve ignorar/desviar de TalismanWard {el} ao rolar através dele sem sofrer dano posterior!"


if __name__ == "__main__":
    test_is_fighter_evading_all_classes()
    test_ofuda_dodge_all_elements()
    test_talisman_ward_dodge()
    test_non_dodging_target_gets_hit()
    test_ofuda_stops_at_hedges_and_solid_obstacles()
    test_aoi_snow_slide_dodge_seimei_projectiles_and_wards()
    print("Todos os testes de esquiva contra Seimei e projéteis passaram com sucesso!")
