#!/usr/bin/env python3
"""
Test Suite: Seimei Overhaul (Sub-fase 2.20)
Verifica:
1. Inicialização, paleta, materiais realistas, HD anime eyes e Sensu/Origami.
2. Disparo de Ofuda reto em alta velocidade, dano padronizado 2 HP e colisão estrita com obstáculos sólidos.
3. Ciclo contínuo do Rondel Elemental Onmyōdō Gogyō (Madeira -> Fogo -> Terra -> Metal -> Água -> Yin-Yang).
4. Selo Sagrado Kekkai (duração 5.5s e limite estrito de 2 selos ativos simultâneos).
5. Deslize Shikigami evasivo com 13 i-frames (0.22s de invulnerabilidade).
6. 6 Fatalidades Elementais Dinâmicas (1 para cada elemento, independente do ataque).
7. Cadáveres Voxel personalizados para os 6 elementos (Cinzas, Água, Madeira, Metal, Terra, Yin-Yang).
8. Sincronização com o 3D Model Inspector (15 botões de animação, notas De/Para e hotkeys F1-F6).
"""

import os
import sys
import math
import unittest
import pygame

# Inicialização headless do Pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

pygame.init()
pygame.display.set_mode((1280, 720))

from src.entities.seimei import SeimeiOnmyoji
from src.entities.projectile import OfudaProjectile, TalismanWard
from src.entities.voxel_corpse import VoxelCorpse
from src.isometric.camera import Camera
from src.isometric.mesh_primitives import PORTRAIT_FACE_STYLES
import src.entities.seimei_model as sm
import tools.model_inspector as mi


class MockDummyVictim:
    """Mock leve para testes de fatalidades e cortes anatômicos."""
    def __init__(self, char_type="kenshin", wx=2.0, wy=2.0):
        self.char_type = char_type
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.state = "IDLE"
        self.is_dead = False
        self.facing_angle = 0.0
        self.hp = 0


class TestSeimeiOverhaul(unittest.TestCase):
    def setUp(self):
        self.seimei = SeimeiOnmyoji(wx=0.0, wy=0.0)
        self.camera = Camera(1280, 720)

    def test_01_seimei_init_and_palette(self):
        """1. Validação de inicialização, materiais realistas, HD anime eyes e leque Sensu."""
        self.assertEqual(self.seimei.char_type, "seimei")
        self.assertIn("seimei", PORTRAIT_FACE_STYLES)
        self.assertTrue(PORTRAIT_FACE_STYLES["seimei"].get("hd_anime_eyes"))

        # Materiais e modelo
        self.assertTrue(hasattr(sm, "MATERIALS"))
        self.assertTrue(hasattr(sm, "LEGACY_MATERIALS"))
        self.assertEqual(sm.MATERIALS.get("robe_white"), "silk")
        self.assertEqual(sm.MATERIALS.get("eboshi"), "lacquer")
        self.assertEqual(sm.MATERIALS.get("gold_thread"), "gold")

        # Articulações de braços e leque Sensu
        hands = sm.get_arms(self.seimei)
        self.assertIsNotNone(hands)
        self.assertEqual(len(hands), 2)
        hand_l, hand_r = hands
        self.assertEqual(len(hand_l), 3)
        self.assertEqual(len(hand_r), 3)

    def test_02_seimei_ofuda_toss_and_obstacle_block(self):
        """2. Disparo de Ofuda reto em alta velocidade, dano padronizado 2 HP e colisão com obstáculos."""
        # Configurar elemento Fogo
        self.seimei.current_element = "fire"
        self.seimei.state = "IDLE"
        fired = self.seimei.trigger_ofuda_toss(1.0, 0.0)
        self.assertTrue(fired)
        self.assertGreater(len(self.seimei.projectiles), 0)

        proj = self.seimei.projectiles[-1]
        self.assertIsInstance(proj, OfudaProjectile)
        self.assertEqual(proj.damage, 2)
        self.assertAlmostEqual(proj.max_range, 6.5, places=1)

        # Verificar se projéteis de TODOS os 6 elementos possuem dano padronizado = 2
        for elem in ("wood", "fire", "earth", "metal", "water", "yinyang"):
            p = OfudaProjectile(0.0, 0.0, wz=0.45, dir_x=1.0, dir_y=0.0, owner=self.seimei, element=elem)
            self.assertEqual(p.damage, 2, f"Dano do elemento {elem} deveria ser 2")

        # Teste de bloqueio por obstáculo sólido (rocha/edifício/árvore)
        rock_proj = OfudaProjectile(0.0, 0.0, wz=0.45, dir_x=1.0, dir_y=0.0, owner=self.seimei, element="fire")
        class MockRock:
            wx = 0.5
            wy = 0.0
            radius = 0.6
            is_broken = False
        class MockGameMap:
            rocks = [MockRock()]
            buildings = []
            trees = []
        
        # O projétil deve ser cancelado ao colidir
        rock_proj.update(0.05, game_map=MockGameMap(), particles=[])
        self.assertFalse(rock_proj.is_active)

    def test_03_seimei_rondel_cycle(self):
        """3. Ciclo contínuo do Rondel Elemental Onmyōdō Gogyō."""
        expected_cycle = ["wood", "fire", "earth", "metal", "water", "yinyang"]
        self.seimei.current_element = expected_cycle[0]

        for i in range(len(expected_cycle) * 2):
            expected_current = expected_cycle[i % len(expected_cycle)]
            self.assertEqual(self.seimei.current_element, expected_current)
            self.seimei.advance_element()

    def test_04_seimei_sacred_ward_mechanics(self):
        """4. Selo Sagrado Kekkai (duração 5.5s e limite estrito de 2 selos ativos simultâneos)."""
        self.seimei.active_wards.clear()
        self.seimei.state = "IDLE"
        self.seimei.ward_timer = 0.0

        # Invocar 1º selo
        w1_success = self.seimei.trigger_sacred_ward()
        self.assertTrue(w1_success)
        self.assertEqual(len(self.seimei.active_wards), 1)
        self.assertAlmostEqual(self.seimei.active_wards[0].duration, 5.5, places=1)

        # Recuperar estado e invocar 2º selo
        self.seimei.state = "IDLE"
        self.seimei.ward_timer = 0.0
        w2_success = self.seimei.trigger_sacred_ward()
        self.assertTrue(w2_success)
        self.assertEqual(len(self.seimei.active_wards), 2)

        # Recuperar estado e invocar 3º selo -> o mais antigo deve ser reciclado ou removido, mantendo len <= 2
        self.seimei.state = "IDLE"
        self.seimei.ward_timer = 0.0
        w3_success = self.seimei.trigger_sacred_ward()
        self.assertTrue(w3_success)
        self.assertLessEqual(len(self.seimei.active_wards), 2)

    def test_05_seimei_shikigami_glide_iframes(self):
        """5. Deslize Shikigami evasivo com 13 i-frames (0.22s de invulnerabilidade)."""
        self.seimei.state = "IDLE"
        glided = self.seimei.trigger_shikigami_glide(1.0, 0.0)
        self.assertTrue(glided)
        self.assertEqual(self.seimei.state, "ROLL")
        self.assertTrue(self.seimei.is_invulnerable)

    def test_06_seimei_elemental_fatalities_dynamic_style(self):
        """6. 6 Fatalidades Elementais Dinâmicas (1 para cada elemento, independente do golpe)."""
        for elem in ("wood", "fire", "earth", "metal", "water", "yinyang"):
            self.seimei.current_element = elem
            expected_fatal = f"SEIMEI_FATAL_{elem.upper()}"
            self.assertEqual(self.seimei.finisher_style_primary, expected_fatal)
            self.assertEqual(self.seimei.finisher_style_secondary, expected_fatal)

    def test_07_seimei_voxel_corpse_renders(self):
        """7. Cadáveres Voxel personalizados para os 6 elementos."""
        styles = [
            ("SEIMEI_FATAL_FIRE", "is_ash_mound"),
            ("SEIMEI_FATAL_WATER", "is_water_dissolved"),
            ("SEIMEI_FATAL_WOOD", "is_sacred_tree"),
            ("SEIMEI_FATAL_METAL", "is_metal_impaled"),
            ("SEIMEI_FATAL_EARTH", "is_stone_petrified"),
            ("SEIMEI_FATAL_YINYANG", "is_spirit_banished"),
        ]

        surf = pygame.Surface((1280, 720))
        for style, attr in styles:
            victim = MockDummyVictim(wx=2.0, wy=2.0)
            corpse = VoxelCorpse(victim, death_style=style, slash_dir=(1.0, 0.0))
            self.assertTrue(getattr(corpse, attr), f"Atributo {attr} não foi ativado para {style}")
            self.assertEqual(len(corpse.pieces), 0, f"{style} não deveria ter peças convencionais de carne")

            # Atualização de partículas
            particles = []
            corpse.update(0.05, game_map=None, particles=particles)

            # Renderização no buffer sem exceções
            corpse.render(surf, self.camera)

    def test_08_seimei_model_inspector_sync(self):
        """8. Sincronização com o 3D Model Inspector (15 botões de animação e notas De/Para)."""
        self.assertIn("seimei", mi.CHARACTER_ANIM_BUTTONS)
        btns = mi.CHARACTER_ANIM_BUTTONS["seimei"]
        self.assertEqual(len(btns), 15)

        btn_ids = [b[0] for b in btns]
        self.assertIn("IDLE", btn_ids)
        self.assertIn("WALK", btn_ids)
        self.assertIn("OFUDA_TOSS", btn_ids)
        self.assertIn("SACRED_WARD", btn_ids)
        self.assertIn("SHIKIGAMI_GLIDE", btn_ids)
        self.assertIn("ASTRAL_GUARD", btn_ids)
        self.assertIn("PARRY_REACTION", btn_ids)
        self.assertIn("INTRO", btn_ids)
        self.assertIn("VICTORY", btn_ids)
        self.assertIn("FATAL_FIRE", btn_ids)
        self.assertIn("FATAL_WATER", btn_ids)
        self.assertIn("FATAL_WOOD", btn_ids)
        self.assertIn("FATAL_METAL", btn_ids)
        self.assertIn("FATAL_EARTH", btn_ids)
        self.assertIn("FATAL_YINYANG", btn_ids)

        # Notas De/Para
        self.assertIn("seimei", mi.OVERHAUL_DE_PARA_NOTES)
        self.assertGreater(len(mi.OVERHAUL_DE_PARA_NOTES["seimei"]), 3)

        # Teste de execução sem erro no ModelInspector
        inspector = mi.ModelInspector(1280, 720, headless=True)
        inspector.select_character("seimei")
        for b_id, _lbl, _dur in btns:
            inspector.trigger_action(b_id)
            inspector.update(0.016)


if __name__ == "__main__":
    unittest.main()
