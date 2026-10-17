"""
Suíte de Testes Automatizados - Fase M-4: Piloto Vertical Slice
- Validação dos 4 Lutadores Piloto Esculpidos: Kenshi, Musashi, Saitou, Okuni
- Validação da Arena Sagrada de Bambu: Vento de combate, flexão elástica e corte de colmo
- Validação da Arena Kyoto Bakumatsu: Fachadas machiya, labaredas e lanternas
- Validação do Deslizamento Tangencial em Obstáculos (Rochas, Fachadas, Árvores)
"""
import os
import sys
import math
import unittest
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((960, 540))

from src.isometric.camera import Camera
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.saitou_samurai import SaitouSamurai
from src.entities.kabuki import Kabuki
from src.entities.samurai import (
    slide_movement_against_obstacles, resolve_playable_bounds,
    STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_DEAD, STATE_ROLL
)
from src.world.arenas import create_arena
from src.world.obstacles import Rock
from src.world.kyoto_map import MachiyaFacade, KyotoLantern, DynamicFlameSpot


class TestMasterPhase4(unittest.TestCase):
    def setUp(self):
        self.camera = Camera(960, 540)
        self.surface = pygame.Surface((960, 540), pygame.SRCALPHA)

    def test_01_pilot_fighters_rendering(self):
        """Valida que Kenshi, Musashi, Saitou e Okuni renderizam sem erros em múltiplos estados."""
        kenshi = RedSamurai(5.0, 5.0)
        musashi = BlueSamurai(5.0, 5.0)
        saitou = SaitouSamurai(5.0, 5.0)
        okuni = Kabuki(5.0, 5.0)

        fighters = [("Kenshi", kenshi), ("Musashi", musashi), ("Saitou", saitou), ("Okuni", okuni)]
        states = [STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_DEAD]

        for name, fighter in fighters:
            for st in states:
                fighter.state = st
                fighter.state_timer = 0.25
                fighter.render(self.surface, self.camera)
            # Rotação de câmera
            self.camera.azimuth = 0.45
            fighter.render(self.surface, self.camera)
            self.camera.azimuth = 0.0

    def test_02_bamboo_arena_and_wind_impulses(self):
        """Valida a arena de Bambu, física de choque de vento e flexão elástica."""
        arena = create_arena("bamboo")
        self.assertIsNotNone(arena)
        self.assertTrue(len(arena.bamboos) > 0)

        bamboo = arena.bamboos[0]
        self.assertEqual(getattr(bamboo, "combat_bend_x", 0.0), 0.0)
        self.assertEqual(getattr(bamboo, "combat_bend_y", 0.0), 0.0)

        # Aplicar choque de ar no local do bambu
        arena.add_wind_impulse(bamboo.wx, bamboo.wy, strength=1.5, radius=3.0, duration=0.6, dir_x=1.0, dir_y=0.0)
        self.assertGreater(bamboo.combat_bend_x, 0.01)

        # Simular amortecimento temporal (decay elástico)
        prev_bend = bamboo.combat_bend_x
        arena.update(0.1, [], self.camera, [], [])
        self.assertLess(bamboo.combat_bend_x, prev_bend)

        # Renderizar bambu curvado ao vivo
        bamboo.render(self.surface, self.camera, time_val=1.2)

        # Cortar bambu
        slice_p = bamboo.cut(slash_dir=(1.0, 0.0))
        self.assertIsNotNone(slice_p)
        self.assertTrue(bamboo.is_cut)
        bamboo.render(self.surface, self.camera, time_val=1.5)

    def test_03_kyoto_bakumatsu_arena_features(self):
        """Valida fachadas de Machiya, labaredas dinâmicas e lanternas de Kyoto."""
        arena = create_arena("kyoto")
        self.assertIsNotNone(arena)
        self.assertTrue(len(arena.buildings) > 0)

        # Fachada Machiya e colisão
        machiya = arena.buildings[0]
        self.assertIsInstance(machiya, MachiyaFacade)
        collided, px, py = machiya.check_collision(machiya.wx + 0.1, machiya.wy + 0.1, p_radius=0.3)
        self.assertTrue(collided)

        # Labaredas dinâmicas
        spot = DynamicFlameSpot(0.5, 0.5, period=5.0, burn_time=3.0, max_h=1.0, phase_shift=0.0)
        h1 = spot.get_height(1.5)
        h2 = spot.get_height(4.0)
        self.assertGreater(h1, 0.0)
        self.assertEqual(h2, 0.0)

        # Lanterna de Kyoto
        lantern = KyotoLantern(6.0, 6.0)
        collided, px, py = lantern.check_collision(6.1, 6.0, p_radius=0.3)
        self.assertTrue(collided)
        lantern.render(self.surface, self.camera, time_val=0.5)

    def test_04_tangential_obstacle_sliding(self):
        """Valida que personagens deslizam suavemente tangencialmente ao colidir com obstáculos."""
        arena = create_arena("bamboo")
        arena.buildings = []
        arena.trees = []
        arena.lanterns = []
        rock = Rock(5.0, 5.0, radius=0.6)
        arena.rocks = [rock]

        # 1. Movimento direto contra a rocha: deve empurrar para fora
        start_x, start_y = 5.0, 4.0
        dx, dy = 0.0, 0.8  # Movendo para dentro da rocha
        new_x, new_y = slide_movement_against_obstacles(start_x, start_y, dx, dy, radius=0.3, game_map=arena)
        dist_to_rock = math.hypot(new_x - rock.wx, new_y - rock.wy)
        self.assertGreaterEqual(dist_to_rock, rock.radius + 0.3 - 1e-4)

        # 2. Movimento oblíquo contra obstáculo (deslizamento tangencial):
        # Move em diagonal (+X, +Y), colidindo no lado esquerdo da rocha
        start_x, start_y = 4.2, 5.0
        dx, dy = 0.5, 0.5
        new_x, new_y = slide_movement_against_obstacles(start_x, start_y, dx, dy, radius=0.3, game_map=arena)
        # O deslocamento em Y (tangencial) deve ser preservado e avançar
        self.assertGreater(new_y, start_y)
        self.assertGreaterEqual(math.hypot(new_x - rock.wx, new_y - rock.wy), rock.radius + 0.3 - 1e-4)

    def test_05_roll_with_tangential_sliding_and_wind(self):
        """Valida a esquiva/rolamento com deslizamento e disparo de vento."""
        arena = create_arena("bamboo")
        kenshi = RedSamurai(5.0, 5.0)
        kenshi.trigger_roll(1.0, 0.0)
        self.assertEqual(kenshi.state, STATE_ROLL)

        # Ao atualizar roll, deve ter gerado impulso de vento
        kenshi.update_roll(0.016, arena)
        self.assertTrue(len(getattr(arena, "wind_impulses", [])) > 0)


if __name__ == "__main__":
    unittest.main()
