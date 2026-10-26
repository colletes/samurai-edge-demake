"""
Testes automatizados para os 5 ajustes de gameplay do Ciclo 6:
1. Finishers customizados de Raiden e Hendrika em VoxelCorpse (decapitação sônica, cratera/slam, stiletto vitriol, dissolução ácida, etc.).
2. Síntese de reagentes de Hendrika em qualquer arena baseada no solo/ambiente e potencialização para Tier 2.
3. Rondel de Seimei no rodapé do lado correspondente (P1 em X=220, P2 em X=1060) com instâncias independentes.
4. Finisher elemental de Seimei sem corpo residual após desintegração em cinzas.
5. Combo de 2 golpes pesados de Raiden (Harite -> Morote-Tsuppari) com janela de encadeamento e frenagem anti-spam.
"""
import os
import sys
import unittest
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

pygame.init()
pygame.display.set_mode((1280, 720))

from src.entities.raiden import RaidenSumo
from src.entities.hendrika import HendrikaAlchemist
from src.entities.seimei import SeimeiOnmyoji
from src.entities.red_samurai import RedSamurai
from src.entities.voxel_corpse import VoxelCorpse
from src.ui.hud_rondel import RondelHUD


class TestGameplayAdjustmentsCycle6(unittest.TestCase):

    def test_item1_finishers_raiden_and_hendrika(self):
        """Item 1: Finishers customizados para Raiden e Hendrika."""
        victim = RedSamurai(5.0, 5.0)

        # Raiden: TSUPPARI_SONIC_DECAP
        corpse_decap = VoxelCorpse(victim, death_style="TSUPPARI_SONIC_DECAP", slash_dir=(1.0, 0.0))
        self.assertFalse(corpse_decap.is_ash_mound)
        self.assertTrue(len(corpse_decap.pieces) >= 2, "Decapitação deve ter cabeça e tronco separados")
        self.assertTrue(any(p.piece_type == "head" for p in corpse_decap.pieces))

        # Raiden: TACHIAI_SHATTER_SLAM
        corpse_slam = VoxelCorpse(victim, death_style="TACHIAI_SHATTER_SLAM", slash_dir=(1.0, 0.0))
        self.assertTrue(corpse_slam.has_impact_crater, "Shatter slam deve gerar cratera de impacto")
        self.assertTrue(any(p.squash == "crush" for p in corpse_slam.pieces), "Corpo deve estar achatado")

        # Hendrika: STILETTO_CAROTID_VITRIOL
        corpse_vitriol = VoxelCorpse(victim, death_style="STILETTO_CAROTID_VITRIOL", slash_dir=(1.0, 0.0))
        self.assertTrue(len(corpse_vitriol.blood_droplets) > 0)

        # Hendrika: ALCHEMIC_ACID_DISSOLVE
        corpse_acid = VoxelCorpse(victim, death_style="ALCHEMIC_ACID_DISSOLVE", slash_dir=(1.0, 0.0))
        self.assertTrue(corpse_acid.is_acid_pool, "Deve formar poça ácida efervescente")

        # Hendrika: ALCHEMIC_FROST_SHATTER
        corpse_frost = VoxelCorpse(victim, death_style="ALCHEMIC_FROST_SHATTER", slash_dir=(1.0, 0.0))
        self.assertTrue(corpse_frost.is_frozen_statue, "Deve transformar o corpo em cristais de gelo quebradiços")
        self.assertTrue(len(corpse_frost.pieces) >= 16, "Deve quebrar em dezenas de fragmentos gélidos")

    def test_item2_hendrika_environmental_synthesis(self):
        """Item 2: Síntese de reagentes em qualquer arena e potencialização."""
        class MockMap:
            def __init__(self, surface="water"):
                self.curr_surface = surface
                self.rocks = []
                self.buildings = []
                self.props = []
            def surface_at(self, x, y):
                return self.curr_surface

        hendrika = HendrikaAlchemist(5.0, 5.0)

        # Gelo / Água -> Frost
        m_water = MockMap(surface="water")
        hendrika.active_reagent_idx = 0  # acid
        hendrika.surface_sample_reagent = "acid"
        hendrika.reagent_surface_timer = 0.0
        for _ in range(50):
            hendrika.check_reagent_pickup(m_water, dt=0.02)
        self.assertEqual(hendrika.active_reagent, "frost")

        # Pedra -> Ether
        m_stone = MockMap(surface="stone")
        for _ in range(50):
            hendrika.check_reagent_pickup(m_stone, dt=0.02)
        self.assertEqual(hendrika.active_reagent, "ether")

        # Permanência prolongada (>= 2.0s) -> Tier 2
        hendrika.reagent_tier = 1
        for _ in range(120):
            hendrika.check_reagent_pickup(m_stone, dt=0.02)
        self.assertEqual(hendrika.reagent_tier, 2)

    def test_item3_seimei_rondel_lateral_positioning(self):
        """Item 3: Rondel nos cantos inferiores P1 (X=220) e P2 (X=1060)."""
        screen = pygame.Surface((1280, 720))
        p1 = SeimeiOnmyoji(4.0, 4.0)
        p2 = SeimeiOnmyoji(8.0, 4.0)

        rondel_p1 = RondelHUD.get("p1")
        rondel_p2 = RondelHUD.get("p2")

        self.assertIsNot(rondel_p1, rondel_p2, "Instâncias de Rondel devem ser isoladas entre P1 e P2")

        # Renderizar P1 na esquerda e P2 na direita sem erros
        rondel_p1.render(screen, p1, 220, 720 - 65, dt=0.016)
        rondel_p2.render(screen, p2, 1280 - 220, 720 - 65, dt=0.016)

    def test_item4_seimei_finisher_no_residual_body(self):
        """Item 4: Finisher de Seimei não deixa corpo após cinzas."""
        victim = RedSamurai(5.0, 5.0)
        for st in ("SEIMEI_FATAL_FIRE", "SEIMEI_FATAL_WATER", "SEIMEI_FATAL_WOOD", "SEAL_STASIS_COLLAPSE", "OFUDA_PURIFICATION_PILLAR"):
            corpse = VoxelCorpse(victim, death_style=st, slash_dir=(1.0, 0.0))
            self.assertTrue(corpse.is_ash_mound, f"Estilo {st} deve ser monte de cinzas")
            self.assertEqual(len(corpse.pieces), 0, f"Estilo {st} não deve deixar pedaços de corpo no solo")

    def test_item5_raiden_two_hit_combo(self):
        """Item 5: Raiden combo de 2 golpes com Harite -> Morote-Tsuppari, alcance físico e anti-spam."""
        raiden = RaidenSumo(10.0, 10.0)
        opp = RedSamurai(10.75, 10.0)

        # 1. Primeiro ataque -> Golpe 1 (Harite)
        raiden.trigger_tsuppari_rush(12.0, 10.0)
        self.assertEqual(raiden.state, "TSUPPARI_STRIKE_1")
        self.assertEqual(raiden.hitbox_damage, 1)
        # Wind-up: no frame 0 a hitbox inicia desligada preparando o golpe
        self.assertFalse(raiden.hitbox_active, "Frame 0 deve ser wind-up (braço se armando)")
        self.assertLessEqual(raiden.hitbox_radius, 0.60, "Raio da palma deve ser físico (<= 0.60m)")

        # Não permite teclar spam instantâneo durante a animação do Golpe 1
        spam_denied = raiden.trigger_tsuppari_rush(12.0, 10.0)
        self.assertFalse(spam_denied, "Não deve permitir spam durante a execução do Golpe 1")

        # Fase de impacto ativo do Golpe 1
        raiden.update(0.10, opponent=opp)
        self.assertTrue(raiden.hitbox_active, "Hitbox deve ativar na fase de impacto (0.05s a 0.18s)")

        # Atualizar até o fim do Golpe 1 (entra em RECOVERY com janela aberta)
        raiden.update(0.14, opponent=opp)
        self.assertEqual(raiden.state, "RECOVERY")
        self.assertEqual(raiden.combo_step, 1)
        self.assertGreater(raiden.combo_window_timer, 0.0)

        # 2. Pressionar ataque na janela -> Golpe 2 (Morote-Tsuppari)
        combo_encadeado = raiden.trigger_tsuppari_rush(12.0, 10.0)
        self.assertTrue(combo_encadeado, "Deve encadear Golpe 2 dentro da janela")
        self.assertEqual(raiden.state, "TSUPPARI_STRIKE_2")
        self.assertEqual(raiden.hitbox_damage, 2)
        self.assertFalse(raiden.hitbox_active, "Frame 0 do Golpe 2 deve ser wind-up (braços abrindo)")
        self.assertLessEqual(raiden.hitbox_radius, 0.65, "Raio do Morote-Tsuppari deve ser calibrado (<= 0.65m)")

        # Impacto do Golpe 2 ativa e atordoa o rival
        raiden.update(0.10, opponent=opp)
        self.assertTrue(raiden.hitbox_active)
        self.assertEqual(opp.state, "STUNNED")

        # Ao terminar Golpe 2 -> recuperação pesada (0.44s)
        raiden.update(0.20, opponent=opp)
        self.assertEqual(raiden.state, "RECOVERY")
        self.assertGreater(raiden.state_timer, 0.35, "Deve aplicar recuperação pesada anti-spam pós-combo")
        self.assertEqual(raiden.combo_step, 0, "Combo deve resetar para neutro")

    def test_item6_hendrika_potions_effective_in_combat(self):
        """Item 6: Frascos de Hendrika detonam, criam poças e aplicam efeitos reais em combate."""
        from src.combat.collision import CombatSystem
        from src.isometric.camera import Camera
        from main import create_arena
        from src.config import ARENA_KYOTO
        game_map = create_arena(ARENA_KYOTO)
        camera = Camera()
        combat_system = CombatSystem()

        hendrika = HendrikaAlchemist(5.0, 5.0)
        opp = RedSamurai(6.0, 5.0)
        opp.hp = 2

        projectiles = []
        particles = []
        banners = []

        # Hendrika arremessa frasco de ácido na direção do rival
        hendrika.active_reagent_idx = 0  # acid
        success = hendrika.trigger_flask_throw(6.0, 5.0, projectiles=projectiles, particles=particles, banners=banners)
        self.assertTrue(success)
        self.assertEqual(len(projectiles), 1)

        # Processar combate até o frasco aterrissar e detonar
        for _ in range(40):
            combat_system.process_combat(hendrika, opp, game_map, particles, banners, camera, projectiles, dt=0.02)

        # A poça deve ter sido criada no solo em hendrika.active_pools
        self.assertTrue(len(hendrika.active_pools) >= 1, "Poça química deve ser criada em active_pools de Hendrika")
        pool = hendrika.active_pools[0]
        self.assertEqual(pool.reagent, "acid")

        # O oponente na área da explosão deve ter sofrido dano da poça
        self.assertLess(opp.hp, 2, "Oponente deve sofrer dano real com a poção de ácido de Hendrika")


if __name__ == "__main__":
    unittest.main()
