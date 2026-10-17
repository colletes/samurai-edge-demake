"""
Suíte de Testes Automatizados - Fase M-5: Rollout Completo do Roster e Arenas
- Validação de Todos os 18 Cenários (Terreno, Props Voxel, Vento e Colisões)
- Validação de Todos os Lutadores do Roster (Malhas Esculpidas, Rig 3D e Feições Faciais)
- Validação de Deslizamento Tangencial em Todas as Arenas
"""
import os
import sys
import unittest
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((960, 540))

from src.isometric.camera import Camera
from src.entities.samurai import (
    Samurai, slide_movement_against_obstacles, resolve_playable_bounds,
    STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_DEAD
)
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.saitou_samurai import SaitouSamurai
from src.entities.kabuki import Kabuki
from src.entities.yellow_ninja import YellowNinja
from src.entities.american_ninja import AmericanNinja
from src.entities.purple_ninja import PurpleNinja
from src.entities.rifleman import Rifleman
from src.entities.kyudo_archer import KyudoArcher
from src.entities.pirate import PirateSwordswoman
from src.entities.musketeer import Musketeer
from src.entities.ren_monk import RenMonk
from src.entities.chiyo_kunoichi import ChiyoKunoichi
from src.entities.benkei import BenkeiSamurai
from src.entities.orin import OrinMinstrel
from src.entities.goro import GoroFarmer
from src.entities.ichi import IchiBlade
from src.world.arenas import create_arena, arena_ids


class TestMasterPhase5(unittest.TestCase):
    def setUp(self):
        self.camera = Camera(960, 540)
        self.surface = pygame.Surface((960, 540), pygame.SRCALPHA)

    def test_01_all_18_arenas_initialization_and_rendering(self):
        """Valida a criação e renderização de todos os 18 cenários do jogo."""
        all_ids = arena_ids()
        self.assertGreaterEqual(len(all_ids), 18)

        for a_id in all_ids:
            with self.subTest(arena=a_id):
                arena = create_arena(a_id)
                self.assertIsNotNone(arena)

                # Renderizar terreno e camada aérea
                arena.render_terrain(self.surface, self.camera, time_val=1.0)
                arena.render_overhead(self.surface, self.camera, time_val=1.0)

                # Vento e choques de combate
                arena.add_wind_impulse(5.0, 5.0, strength=1.2, radius=3.5, duration=0.5)
                vx, vy = arena.wind_at(5.0, 5.0, t=1.0)
                self.assertIsInstance(vx, float)
                self.assertIsInstance(vy, float)

                # Simulação
                arena.update(0.016, [], self.camera, [], [])

    def test_02_all_17_fighters_sculpted_rendering(self):
        """Valida que todos os 17 lutadores do elenco renderizam em múltiplos estados e azimutes."""
        fighters = [
            ("Kenshi", RedSamurai(5.0, 5.0)),
            ("Musashi", BlueSamurai(5.0, 5.0)),
            ("Saitou", SaitouSamurai(5.0, 5.0)),
            ("Okuni", Kabuki(5.0, 5.0)),
            ("Hanzo", YellowNinja(5.0, 5.0)),
            ("Joe", AmericanNinja(5.0, 5.0)),
            ("Murasaki", PurpleNinja(5.0, 5.0)),
            ("Teppo", Rifleman(5.0, 5.0)),
            ("Tomoe", KyudoArcher(5.0, 5.0)),
            ("Anne", PirateSwordswoman(5.0, 5.0)),
            ("Julie", Musketeer(5.0, 5.0)),
            ("Ren", RenMonk(5.0, 5.0)),
            ("Chiyo", ChiyoKunoichi(5.0, 5.0)),
            ("Benkei", BenkeiSamurai(5.0, 5.0)),
            ("Orin", OrinMinstrel(5.0, 5.0)),
            ("Goro", GoroFarmer(5.0, 5.0)),
            ("Ichi", IchiBlade(5.0, 5.0)),
        ]

        states = [STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_DEAD]
        azimuths = [0.0, 0.45, -0.60]

        for name, fighter in fighters:
            with self.subTest(fighter=name):
                for az in azimuths:
                    self.camera.azimuth = az
                    for st in states:
                        fighter.state = st
                        fighter.state_timer = 0.2
                        fighter.render(self.surface, self.camera)
        self.camera.azimuth = 0.0

    def test_03_tangential_sliding_across_arenas(self):
        """Valida que o vetor tangencial desvia suavemente em obstáculos em diferentes cenários."""
        sample_arenas = ["bamboo", "kyoto", "nagashino_field", "shaolin_temple"]
        for a_id in sample_arenas:
            with self.subTest(arena=a_id):
                arena = create_arena(a_id)
                # Deslocar entidade no centro da arena
                start_x, start_y = 6.0, 6.0
                dx, dy = 0.35, 0.35
                nx, ny = slide_movement_against_obstacles(start_x, start_y, dx, dy, radius=0.3, game_map=arena)
                self.assertIsInstance(nx, float)
                self.assertIsInstance(ny, float)
                min_x, min_y, max_x, max_y = resolve_playable_bounds(arena)
                self.assertGreaterEqual(nx, min_x)
                self.assertLessEqual(nx, max_x)
                self.assertGreaterEqual(ny, min_y)
                self.assertLessEqual(ny, max_y)


if __name__ == "__main__":
    unittest.main()
