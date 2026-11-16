"""
Ajustes de balanceamento pré-deploy SEM aumento de HP:
Teppo (bala mais lenta), Benkei (naginata boomerang), Hanzo (esquiva + kunai), Goro (armor/terra instantânea/torrões)
e IA (esquiva perpendicular do Gatotsu, Hanzo não persegue a kunai com o rival em cima).
"""
import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src.entities.ai_controller import SamuraiAI
from src.entities.benkei import BenkeiSamurai
from src.entities.goro import GoroFarmer
from src.entities.projectile import EarthClod, KunaiProjectile, MusketBulletProjectile, NaginataProjectile
from src.entities.rifleman import Rifleman
from src.entities.saitou_samurai import SaitouSamurai
from src.entities.yellow_ninja import YellowNinja
from src.world.arenas import create_arena


class _Foe:
    wx = 30.0
    wy = 8.0


class TestMaxHpUnchanged(unittest.TestCase):
    def test_nobody_gains_hp(self):
        for cls in (Rifleman, BenkeiSamurai, YellowNinja, GoroFarmer, SaitouSamurai):
            f = cls(5.0, 5.0)
            self.assertEqual((f.max_hp, f.hp), (2, 2), cls.__name__)


class TestTeppoBullet(unittest.TestCase):
    def test_bullet_slower_and_shorter_but_julie_unchanged(self):
        teppo = Rifleman(5.0, 5.0)
        projs = []
        teppo._fire_musket(10.0, 5.0, projs)
        bullet = projs[0]
        self.assertAlmostEqual(bullet.speed, 18.0)
        self.assertAlmostEqual(bullet.max_range, 12.0)
        # a classe segue com os defaults antigos para quem não passa parâmetros (Mosqueteira usa max_range próprio)
        default = MusketBulletProjectile(0, 0, 0.5, 1, 0, owner=_Foe())
        self.assertAlmostEqual(default.speed, 31.2)
        self.assertAlmostEqual(default.max_range, 18.0)


class TestBenkeiBoomerang(unittest.TestCase):
    def test_embeds_at_max_range_and_recall_rearms(self):
        gm = create_arena("bamboo")
        b = BenkeiSamurai(8.0, 8.0)
        projs = []
        self.assertTrue(b.trigger_naginata_throw(15.0, 8.0, projs))
        nag = projs[0]
        self.assertFalse(b.has_naginata)
        for _ in range(200):
            nag.update(0.016, gm, [])
        self.assertEqual(nag.state, "ON_GROUND")
        self.assertFalse(nag.returning)
        self.assertTrue(b.trigger_naginata_recall())
        for _ in range(600):
            if not nag.update(0.016, gm, []):
                break
        self.assertTrue(b.has_naginata)

    def test_can_hit_again_on_the_way_back(self):
        gm = create_arena("bamboo")
        b = BenkeiSamurai(8.0, 8.0)
        projs = []
        b.trigger_naginata_throw(15.0, 8.0, projs)
        nag = projs[0]
        nag.wx, nag.wy = 14.0, 8.0           # longe do dono
        nag.has_hit_fighter = True          # acertou (sem matar) na ida
        nag._embed_into_ground(gm, [])      # fim da ida -> cravada, aguardando recall
        self.assertEqual(nag.state, "ON_GROUND")
        self.assertTrue(nag.recall())       # 2º toque no secundário -> começa a voltar
        self.assertTrue(nag.returning)
        self.assertTrue(nag.has_hit_fighter)  # trava curta evita acerto duplo imediato
        for _ in range(20):
            nag.update(0.016, gm, [])
        self.assertFalse(nag.has_hit_fighter)  # liberado: a volta pode acertar

    def test_no_tackle_anymore(self):
        b = BenkeiSamurai(8.0, 8.0)
        self.assertFalse(hasattr(b, "trigger_tackle_charge"))
        b.has_naginata = False
        self.assertFalse(b.trigger_naginata_thrust(10.0, 8.0))


class TestHanzoDodge(unittest.TestCase):
    def test_dodge_is_faster_and_longer(self):
        h = YellowNinja(8.0, 8.0)
        self.assertAlmostEqual(h.jump_speed, 9.0)
        self.assertGreater(h.jump_speed * h.jump_duration, 4.0)
        self.assertGreater(SamuraiAI._roll_reach(h), 4.0)  # a IA considera o alcance real do salto

    def test_kunai_thrown_during_dodge_is_horizontal_full_range(self):
        h = YellowNinja(8.0, 8.0)
        projs = []
        self.assertTrue(h.trigger_jump(1.0, 0.0))
        self.assertEqual(h.state, "JUMP")
        self.assertTrue(h.trigger_kunai_snipe(14.0, 8.0, projs))
        self.assertEqual(h.state, "JUMP")  # continua esquivando
        k = projs[0]
        self.assertIsInstance(k, KunaiProjectile)
        self.assertEqual(k.vz, 0.0)
        self.assertAlmostEqual(k.max_range, 6.8)
        self.assertFalse(h.trigger_kunai_snipe(14.0, 8.0, projs))  # 1 por salto


class TestGoroStomp(unittest.TestCase):
    def test_armor_reduces_damage_by_one_without_stagger(self):
        g = GoroFarmer(8.0, 8.0)
        g.state = "EARTH_STOMP"
        took, dead = g.take_hit((1.0, 0.0), damage=2)
        self.assertTrue(took)
        self.assertFalse(dead)
        self.assertEqual((g.hp, g.max_hp, g.state), (1, 2, "EARTH_STOMP"))
        g2 = GoroFarmer(8.0, 8.0)
        g2.state = "EARTH_STOMP"
        g2.take_hit((1.0, 0.0), damage=1)
        self.assertEqual(g2.hp, 2)  # dano 1 absorvido
        _, dead = g.take_hit((1.0, 0.0), damage=2)  # segundo golpe de dano 2 mata
        self.assertTrue(dead)

    def test_no_armor_outside_stomp(self):
        g = GoroFarmer(8.0, 8.0)
        _, dead = g.take_hit((1.0, 0.0), damage=2)
        self.assertTrue(dead)

    def test_wave_is_near_instant_and_clods_block_projectiles(self):
        gm = create_arena("bamboo")
        g = GoroFarmer(8.0, 8.0)
        g.set_facing(12.0, 8.0)
        projs, parts = [], []
        self.assertTrue(g.trigger_earth_stomp(12.0, 8.0, shockwaves=projs, particles=parts, game_map=gm))
        wave = next(p for p in projs if type(p).__name__ == "EarthStompShockwave")
        self.assertLessEqual(wave.duration, 0.1)
        foe = _Foe()
        bullet = MusketBulletProjectile(14.0, 8.0, 0.55, -1.0, 0.0, owner=foe)
        kunai = KunaiProjectile(14.0, 8.4, 0.45, -1.0, 0.0, owner=foe)
        projs += [bullet, kunai]
        for _ in range(40):
            for p in list(projs):
                n = type(p).__name__
                if n in ("EarthClod", "EarthStompShockwave"):
                    p.update(0.016, gm, parts, projectiles=projs)
                elif n == "KunaiProjectile":
                    p.update(0.016, gm, parts, opponent=g)
                else:
                    p.update(0.016, gm, parts)
        self.assertFalse(bullet.is_active)
        self.assertEqual(kunai.state, "ON_GROUND")

    def test_clods_expire_and_are_not_threats_to_ai(self):
        gm = create_arena("bamboo")
        clod = EarthClod(9.0, 8.0, owner=GoroFarmer(8.0, 8.0), lifetime=0.5)
        self.assertTrue(clod.is_obstacle)
        alive = True
        for _ in range(60):
            alive = clod.update(0.016, gm, [], projectiles=[])
        self.assertFalse(alive)


class TestAiVsGatotsu(unittest.TestCase):
    def _setup(self, difficulty="hard"):
        ai = SamuraiAI(difficulty=difficulty)
        ai._charge_dodge_chance = lambda: 1.0
        ai._get_reaction_delay = lambda *a, **k: 0.0
        gm = create_arena("bamboo")
        saitou = SaitouSamurai(8.0, 8.0)
        defender = GoroFarmer(13.0, 8.0)
        saitou.state = "GATOTSU_CHARGE"
        saitou.charge_dir_x, saitou.charge_dir_y = 1.0, 0.0
        saitou.charge_speed = 8.0
        return ai, gm, saitou, defender

    def test_ai_sidesteps_perpendicular_to_charge(self):
        ai, gm, saitou, defender = self._setup()
        rolled = []
        defender.trigger_roll = lambda dx, dy, *a, **k: rolled.append((dx, dy)) or True
        for _ in range(30):
            if ai._dodge_linear_charge(defender, saitou, 0.016, gm):
                break
            saitou.wx += 8.0 * 0.016
        self.assertEqual(len(rolled), 1)
        dx, dy = rolled[0]
        self.assertAlmostEqual(dx, 0.0, places=3)   # perpendicular ao eixo X da investida
        self.assertAlmostEqual(abs(dy), 1.0, places=3)

    def test_ai_ignores_charge_when_out_of_corridor(self):
        ai, gm, saitou, defender = self._setup()
        defender.wy = 11.0
        defender.trigger_roll = lambda *a, **k: self.fail("não devia esquivar fora do corredor")
        for _ in range(20):
            self.assertFalse(ai._dodge_linear_charge(defender, saitou, 0.016, gm))

    def test_hanzo_does_not_chase_ground_kunai_with_foe_close(self):
        self.assertGreaterEqual(SamuraiAI.KUNAI_CHASE_MIN_DIST, 3.0)


if __name__ == "__main__":
    unittest.main()
