"""
Testes automatizados unitários e de integração para os guerreiros do Ciclo 3:
- Goro (O Camponês / The Kuwa Farmer)
- Ichi (A Lâmina Cega / The Blind Blade)
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import unittest
from src.config import (
    CHAR_GORO, CHAR_ICHI, COLOR_GORO_AURA, COLOR_ICHI_AURA
)
from src.roster import PLAYABLE_FIGHTERS, ROSTER
from src.entities.samurai import (
    STATE_IDLE, STATE_ATTACK, STATE_RECOVERY
)
from src.entities.goro import GoroFarmer, STATE_EARTH_STOMP
from src.entities.ichi import IchiBlade, STATE_LISTEN, STATE_COUNTER_THRUST
from src.entities.projectile import EarthStompShockwave
from src.ui.game_help import FIGHTERS_GUIDE_DATA
from src.ui.portraits import get_portrait


class TestCycle3GoroIchi(unittest.TestCase):

    def test_roster_and_portraits_registered(self):
        """Verifica se Goro e Ichi estão devidamente cadastrados no Roster e no sistema de Portraits."""
        self.assertIn(CHAR_GORO, PLAYABLE_FIGHTERS)
        self.assertIn(CHAR_ICHI, PLAYABLE_FIGHTERS)

        roster_dict = {f: (arena, key) for f, arena, key in ROSTER}
        self.assertIn(CHAR_GORO, roster_dict)
        self.assertEqual(roster_dict[CHAR_GORO][1], "goro")

        self.assertIn(CHAR_ICHI, roster_dict)
        self.assertEqual(roster_dict[CHAR_ICHI][1], "ichi")

        # Portraits
        bust_goro = get_portrait("goro", circular=False)
        self.assertIsNotNone(bust_goro)
        circle_goro = get_portrait("goro", circular=True)
        self.assertIsNotNone(circle_goro)

        bust_ichi = get_portrait("ichi", circular=False)
        self.assertIsNotNone(bust_ichi)
        circle_ichi = get_portrait("ichi", circular=True)
        self.assertIsNotNone(circle_ichi)

    def test_help_manual_entries(self):
        """Garante que Goro e Ichi possuem fichas completas no manual F1."""
        guide_ids = [item["id"] for item in FIGHTERS_GUIDE_DATA]
        self.assertIn(CHAR_GORO, guide_ids)
        self.assertIn(CHAR_ICHI, guide_ids)

        goro_data = next(item for item in FIGHTERS_GUIDE_DATA if item["id"] == CHAR_GORO)
        self.assertIn("pt", goro_data)
        self.assertIn("en", goro_data)
        self.assertEqual(goro_data["pt"]["name"], "GORO")

        ichi_data = next(item for item in FIGHTERS_GUIDE_DATA if item["id"] == CHAR_ICHI)
        self.assertIn("pt", ichi_data)
        self.assertIn("en", ichi_data)
        self.assertEqual(ichi_data["pt"]["name"], "ICHI")

    def test_goro_mechanics(self):
        """Valida o guerreiro Goro: Kuwa Cleave, Pisotão Sísmico e Shockwave."""
        goro = GoroFarmer(10.0, 10.0)
        self.assertEqual(goro.char_type, "goro")
        self.assertEqual(goro.hp, 2)
        self.assertEqual(goro.state, STATE_IDLE)

        # 1. Ataque Kuwa Cleave
        attacked = goro.trigger_kuwa_cleave(11.0, 10.0)
        self.assertTrue(attacked)
        self.assertEqual(goro.state, STATE_ATTACK)

        # Simula tempo de ataque até finalizar
        for _ in range(30):
            goro.update(0.016)
        self.assertIn(goro.state, (STATE_IDLE, STATE_RECOVERY))

        # 2. Pisotão Sísmico (Earth Stomp)
        goro.stomp_timer = 0.0
        goro.state = STATE_IDLE

        stomped = goro.trigger_earth_stomp(11.0, 10.0)
        self.assertTrue(stomped)
        self.assertEqual(goro.state, STATE_EARTH_STOMP)
        self.assertGreater(len(goro.active_shockwaves), 0)
        wave = goro.active_shockwaves[0]
        self.assertIsInstance(wave, EarthStompShockwave)
        self.assertGreater(wave.radius, 0.0)

    def test_ichi_mechanics(self):
        """Valida a guerreira Ichi: Gyaku-Iai rápido e Postura de Escuta sensorial."""
        ichi = IchiBlade(15.0, 15.0)
        self.assertEqual(ichi.char_type, "ichi")
        self.assertEqual(ichi.hp, 2)
        self.assertEqual(ichi.state, STATE_IDLE)

        # 1. Saque Gyaku-Iai (ultra rápido 0.14s)
        attacked = ichi.trigger_gyaku_iai(16.0, 15.0)
        self.assertTrue(attacked)
        self.assertEqual(ichi.state, STATE_ATTACK)
        self.assertAlmostEqual(ichi.attack_duration, 0.14, places=2)

        for _ in range(20):
            ichi.update(0.016)
        self.assertIn(ichi.state, (STATE_IDLE, STATE_RECOVERY))

        # 2. Postura de Escuta (Listen Stance)
        ichi.listen_timer = 0.0
        ichi.state = STATE_IDLE

        listened = ichi.trigger_listen_stance(16.0, 15.0)
        self.assertTrue(listened)
        self.assertEqual(ichi.state, STATE_LISTEN)
        self.assertTrue(ichi.counter_active)

        # 3. Teste direcional do parry sensorial: frente vs costas
        ichi.set_facing(16.0, 15.0)  # Olhando para a direita (+X)
        self.assertTrue(ichi.is_facing_target(17.0, 15.0), "Alvo à frente deve ser detectado")
        self.assertFalse(ichi.is_facing_target(13.0, 15.0), "Alvo pelas costas deve quebrar a guarda")

        # 4. Esquiva focada em parry (mais lenta que a média)
        self.assertFalse(ichi.is_agile_dodge)
        self.assertEqual(ichi.roll_speed, 7.0)
        self.assertGreaterEqual(ichi.roll_recovery_duration, 0.20)

        # 5. Teste do contra-ataque perfurante
        ichi.trigger_counter_thrust(16.0, 15.0)
        self.assertEqual(ichi.state, STATE_COUNTER_THRUST)
        self.assertFalse(ichi.counter_active)


if __name__ == "__main__":
    unittest.main()
