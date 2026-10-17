import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.world.decor import ScreenPanel
from src.world.bamboo import Bamboo
from src.world.obstacles import Rock, Well
from src.entities.american_ninja import AmericanNinja
from src.entities.projectile import (
    ShurikenProjectile, KunaiProjectile, MusketBulletProjectile,
    KyudoArrowProjectile, HamayaArrowProjectile, MusashiWaveProjectile,
    TimedBombEntity, RemoteMineEntity, CannonballProjectile,
    AcousticResonanceWave, EarthStompShockwave,
)
from src.world.solid_props import PowderBarrel
from src.combat.collision import CombatSystem


class FakeArenaMap:
    def __init__(self, rocks=None, bamboos=None, well=None, interactives=None):
        self.rocks = rocks or []
        self.bamboos = bamboos or []
        self.well = well
        self.interactives = interactives or []
        self.cols = 20
        self.rows = 20


class TestBreakableObjectsDamage(unittest.TestCase):
    def test_joe_shuriken_breaks_screen_panel(self):
        """Valida que o projétil Shuriken do Joe destrói biombos quebraveis (ScreenPanel)."""
        biombo = ScreenPanel(10.0, 10.0, axis="x")
        self.assertFalse(biombo.is_broken)
        self.assertGreater(biombo.radius, 0)

        game_map = FakeArenaMap(rocks=[biombo])
        particles = []

        joe = AmericanNinja(8.0, 10.0)
        shuriken = ShurikenProjectile(
            wx=8.0, wy=10.0, wz=0.6,
            dir_x=1.0, dir_y=0.0,
            owner=joe
        )

        # Atualiza a trajetória da shuriken até atingir o biombo
        broken = False
        for _ in range(30):
            if not shuriken.update(0.016, game_map, particles):
                break
            if biombo.is_broken:
                broken = True
                break

        self.assertTrue(biombo.is_broken, "O biombo deve ser quebrado pelo projétil do Joe")
        self.assertEqual(biombo.radius, 0.0, "O raio de colisão do biombo deve ser zerado após quebra")
        self.assertFalse(shuriken.is_active, "A primeira shuriken deve ser consumida ao quebrar o biombo")

        # Uma segunda shuriken agora passa direto pelo biombo já destruído
        shuriken2 = ShurikenProjectile(
            wx=8.0, wy=10.0, wz=0.6,
            dir_x=1.0, dir_y=0.0,
            owner=joe
        )
        passed = False
        for _ in range(30):
            still_active = shuriken2.update(0.016, game_map, particles)
            if shuriken2.wx > 10.5:
                passed = True
                break
            if not still_active:
                break

        self.assertTrue(passed, "Segunda shuriken deve atravessar o biombo já destruído sem colidir")

    def test_joe_shuriken_cuts_bamboo(self):
        """Valida que o projétil Shuriken do Joe também corta bambus."""
        bamboo = Bamboo(10.0, 10.0)
        self.assertFalse(bamboo.is_cut)

        game_map = FakeArenaMap(bamboos=[bamboo])
        particles = []

        joe = AmericanNinja(8.0, 10.0)
        shuriken = ShurikenProjectile(
            wx=8.0, wy=10.0, wz=0.6,
            dir_x=1.0, dir_y=0.0,
            owner=joe
        )

        for _ in range(30):
            if not shuriken.update(0.016, game_map, particles):
                break

        self.assertTrue(bamboo.is_cut, "A shuriken do Joe deve cortar bambus no caminho")

    def test_doberman_dog_breaks_screen_panel(self):
        """Valida que o ataque com o cão Doberman quebra biombos no caminho do dash."""
        biombo = ScreenPanel(10.0, 10.0, axis="x")
        game_map = FakeArenaMap(rocks=[biombo])

        joe = AmericanNinja(8.0, 10.0)
        dog = joe.dog
        dog.wx = 8.0
        dog.wy = 10.0
        dog.state = "CHARGE"
        dog.facing_x = 1.0
        dog.facing_y = 0.0

        for _ in range(20):
            dog.update(0.016, game_map)
            if biombo.is_broken:
                break

        self.assertTrue(biombo.is_broken, "O dash letal do Doberman deve estilhaçar biombos")

    def test_other_projectiles_break_screen_panel(self):
        """Valida que kunais, balas de mosquete e flechas quebram biombos."""
        # 1. Kunai
        biombo1 = ScreenPanel(10.0, 10.0)
        kunai = KunaiProjectile(8.0, 10.0, 0.5, 1.0, 0.0, owner=None)
        gmap1 = FakeArenaMap(rocks=[biombo1])
        parts1 = []
        for _ in range(30):
            if not kunai.update(0.016, gmap1, parts1):
                break
        self.assertTrue(biombo1.is_broken, "Kunai deve quebrar o biombo")

        # 2. Musket Bullet
        biombo2 = ScreenPanel(10.0, 10.0)
        bullet = MusketBulletProjectile(8.0, 10.0, 0.5, 1.0, 0.0, owner=None)
        gmap2 = FakeArenaMap(rocks=[biombo2])
        parts2 = []
        for _ in range(30):
            if not bullet.update(0.016, gmap2, parts2):
                break
        self.assertTrue(biombo2.is_broken, "Bala de mosquete deve quebrar o biombo")

        # 3. Kyudo Arrow
        biombo3 = ScreenPanel(10.0, 10.0)
        arrow = KyudoArrowProjectile(8.0, 10.0, 0.5, 1.0, 0.0, owner=None)
        gmap3 = FakeArenaMap(rocks=[biombo3])
        parts3 = []
        for _ in range(30):
            if not arrow.update(0.016, gmap3, parts3):
                break
        self.assertTrue(biombo3.is_broken, "Flecha de arco Kyudo deve quebrar o biombo")

        # 4. Musashi Wave
        biombo4 = ScreenPanel(10.0, 10.0)
        wave = MusashiWaveProjectile(8.0, 10.0, 0.5, 1.0, 0.0, owner=None)
        gmap4 = FakeArenaMap(rocks=[biombo4])
        parts4 = []
        for _ in range(30):
            if not wave.update(0.016, gmap4, parts4):
                break
        self.assertTrue(biombo4.is_broken, "Onda de corte Musashi deve quebrar o biombo")

    def test_explosions_break_screen_panel(self):
        """Valida que explosões de bombas, minas e barris quebram biombos ao redor."""
        # 1. TimedBombEntity via collision
        biombo_bomb = ScreenPanel(10.0, 10.0)
        bamboo_bomb = Bamboo(10.5, 10.0)
        gmap_bomb = FakeArenaMap(rocks=[biombo_bomb], bamboos=[bamboo_bomb])
        bomb = TimedBombEntity(10.0, 10.0, wz=0.0, dir_x=0.0, dir_y=0.0, owner=None)
        bomb.fuse_timer = 0.0
        col_sys = CombatSystem()
        p1 = AmericanNinja(5.0, 5.0)
        p2 = AmericanNinja(15.0, 15.0)
        parts = []
        banners = []
        col_sys.process_combat(p1, p2, gmap_bomb, parts, banners, camera=None, projectiles=[bomb])
        self.assertTrue(biombo_bomb.is_broken, "Explosão de bomba deve quebrar biombos na área")
        self.assertTrue(bamboo_bomb.is_cut, "Explosão de bomba deve cortar bambus na área")

        # 2. RemoteMineEntity
        biombo_mine = ScreenPanel(10.0, 10.0)
        gmap_mine = FakeArenaMap(rocks=[biombo_mine])
        mine = RemoteMineEntity(10.2, 10.0, owner=p1)
        mine.update(0.016, gmap_mine, parts)
        mine.detonate([p1, p2], parts, banners, game_map=gmap_mine)
        self.assertTrue(biombo_mine.is_broken, "Detonação de mina deve quebrar biombos na área")

        # 3. PowderBarrel
        biombo_barrel = ScreenPanel(10.0, 10.0)
        barrel = PowderBarrel(10.5, 10.0)
        gmap_barrel = FakeArenaMap(rocks=[biombo_barrel], interactives=[barrel])
        barrel.state = "lit"
        barrel.timer = 0.0
        barrel.tick(gmap_barrel, 0.016, [p1, p2], camera=None, particles=parts, banners=banners)
        self.assertTrue(biombo_barrel.is_broken, "Explosão de barril de pólvora deve quebrar biombos")

    def test_broken_screen_panel_allows_movement(self):
        """Valida que o biombo destruído não bloqueia movimento de lutadores."""
        biombo = ScreenPanel(10.0, 10.0)
        col, _, _ = biombo.check_collision(10.0, 10.0, p_radius=0.3)
        self.assertTrue(col, "Biombo inteiro deve colidir")

        biombo.break_panel((1.0, 0.0))
        col_after, _, _ = biombo.check_collision(10.0, 10.0, p_radius=0.3)
        self.assertFalse(col_after, "Biombo destruído NÃO deve bloquear movimento")


if __name__ == "__main__":
    unittest.main()
