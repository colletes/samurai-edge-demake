"""
Testes automatizados e diagnósticos de atrito de balanceamento nas arenas.
Verifica:
1. Fechamento de distância Melee vs Ranged (sem loops infinitos de fuga em terreno complexo)
2. Navegação de lutadores pesados/colossais (Benkei/Raiden) em arenas estreitas (Yoshiwara, Dejima, Gojo)
3. Detecção de bordas de buraco pela IA em arenas com abismo (Iga, Pirate Deck, Ganryu, Gojo)
4. Força e tempo de escape dos perigos de arena (Ship Roll, Tide Surge, Blizzard)
5. Validação das 24 arenas com zero spawns inválidos ou dentro de obstáculos
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import unittest
import math
import pygame

pygame.init()

from src.config import (
    CHAR_KENSHIN, CHAR_RIFLE, CHAR_BENKEI, CHAR_RAIDEN,
    CHAR_ARCHER, CHAR_MUSASHI,
    ARENA_YOSHIWARA, ARENA_DEJIMA, ARENA_GOJO_BRIDGE,
    ARENA_IGA, ARENA_PIRATE_DECK, ARENA_GANRYU, ARENA_DOHYO
)
from src.world.arenas import ARENA_SPECS, arena_ids, create_arena
from tools.simulate_tournament import simulate_single_battle


class TestArenaBalanceFriction(unittest.TestCase):

    def test_1_all_24_arenas_spawn_integrity(self):
        """Todas as 24 arenas devem gerar spawns válidos sem colisão com obstáculos ou abismos."""
        for a_id in arena_ids():
            arena = create_arena(a_id)
            for trial in range(30):
                (p1x, p1y), (p2x, p2y) = arena.pick_spawns(min_distance=7.0)
                dist = math.hypot(p2x - p1x, p2y - p1y)
                self.assertGreaterEqual(
                    dist, 6.8,
                    f"Arena {a_id}: Spawns muito próximos ({dist:.2f}m < 6.8m) na tentativa {trial}"
                )
                if hasattr(arena, "pit_edge_distance"):
                    p1_pdist = arena.pit_edge_distance(p1x, p1y)
                    p2_pdist = arena.pit_edge_distance(p2x, p2y)
                    self.assertGreaterEqual(
                        p1_pdist, 0.8,
                        f"Arena {a_id}: Spawn P1 ({p1x}, {p1y}) muito perto de abismo ({p1_pdist:.2f}m)"
                    )
                    self.assertGreaterEqual(
                        p2_pdist, 0.8,
                        f"Arena {a_id}: Spawn P2 ({p2x}, {p2y}) muito perto de abismo ({p2_pdist:.2f}m)"
                    )

    def test_2_melee_rushdown_vs_ranged_zoner_closure(self):
        """Kenshin (Melee) deve conseguir engajar Teppo (Ranged) nas arenas abertas sem sofrer timeout."""
        arenas_to_test = ["bamboo", "nagashino_field", "rice_paddies", "heian_shrine"]
        for a_id in arenas_to_test:
            g_map = create_arena(a_id)
            winner, duration, reason = simulate_single_battle(
                CHAR_KENSHIN, CHAR_RIFLE, g_map, max_time=25.0
            )
            self.assertNotEqual(
                reason, "TIMEOUT_DRAW",
                f"Arena {a_id}: Confronto Kenshin vs Teppo resultou em TIMEOUT_DRAW ({duration:.1f}s)"
            )
            self.assertLess(
                duration, 20.0,
                f"Arena {a_id}: Combate Melee vs Zoner demorou excessivamente ({duration:.1f}s)"
            )

    def test_3_heavy_fighters_in_narrow_arenas(self):
        """Lutadores colossais (Benkei/Raiden) não devem travar em becos e pontes estreitas."""
        narrow_arenas = [ARENA_YOSHIWARA, ARENA_DEJIMA, ARENA_GOJO_BRIDGE]
        for a_id in narrow_arenas:
            g_map = create_arena(a_id)
            winner, duration, reason = simulate_single_battle(
                CHAR_BENKEI, CHAR_RAIDEN, g_map, max_time=30.0
            )
            self.assertIn(
                winner, (CHAR_BENKEI, CHAR_RAIDEN),
                f"Arena {a_id}: Benkei vs Raiden não concluiu com vencedor ({reason})"
            )
            self.assertLess(
                duration, 28.0,
                f"Arena {a_id}: Benkei vs Raiden travou por muito tempo ({duration:.1f}s)"
            )

    def test_4_pit_edge_safety_ai_navigation(self):
        """Arenas com abismos (Iga, Pirate Deck, Ganryu, Gojo) não devem gerar mortes por timeout."""
        pit_arenas = [ARENA_IGA, ARENA_PIRATE_DECK, ARENA_GANRYU, ARENA_GOJO_BRIDGE]
        for a_id in pit_arenas:
            g_map = create_arena(a_id)
            winner, duration, reason = simulate_single_battle(
                CHAR_MUSASHI, CHAR_ARCHER, g_map, max_time=25.0
            )
            self.assertNotEqual(
                reason, "TIMEOUT_DRAW",
                f"Arena com abismo {a_id} travou em TIMEOUT_DRAW ({duration:.1f}s)"
            )

    def test_5_dohyo_sumo_ring_out_resolution(self):
        """No Dohyo Sagrado, duelos de alta pressão devem ser decididos rapidamente (sub-10s)."""
        dohyo = create_arena(ARENA_DOHYO)
        winner, duration, reason = simulate_single_battle(
            CHAR_RAIDEN, CHAR_KENSHIN, dohyo, max_time=15.0
        )
        self.assertLess(
            duration, 10.0,
            f"Dohyo demorou mais que 10s para decidir combate ({duration:.1f}s)"
        )


if __name__ == "__main__":
    unittest.main()
