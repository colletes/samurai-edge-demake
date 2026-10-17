"""
Suite de Testes Automatizados para a Fase M-3:
Efeitos Sonoros Realistas Multi-Camadas e Interface Nobre Samurai Cinema (Sumi-E / Laca Urushi).

Execução headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_master_phase3.py
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
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

from src.audio.sound_events import SoundEvent, get_weapon_swing_event, get_surface_footstep_event
from src.audio.sound_manager import SoundManager
from src.audio.procedural_sfx import _GENERATOR_MAP
from src.ui.combat_callouts import render_sumie_ribbon, draw_overhead_marker, draw_status_gauge
from src.effects.particles import FloatingBanner
from src.combat.clash_system import ClashSystem
from src.ui.round_result import render_round_pips, render_damage_bars, RoundResultScreen
from src.isometric.camera import Camera
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai


class TestMasterPhase3(unittest.TestCase):
    def setUp(self):
        self.screen = pygame.Surface((1280, 720))
        self.camera = Camera(1280, 720)
        self.sound_mgr = SoundManager.get_instance()

    def test_01_weapon_and_surface_events(self):
        """Verifica o mapeamento e consistência dos novos eventos de arma e terreno."""
        # Armas específicas por arquétipo
        self.assertEqual(get_weapon_swing_event("kenshin"), SoundEvent.SLASH_KATANA)
        self.assertEqual(get_weapon_swing_event("benkei"), SoundEvent.SLASH_HEAVY)
        self.assertEqual(get_weapon_swing_event("musketeer"), SoundEvent.SLASH_RAPIER)
        self.assertEqual(get_weapon_swing_event("ren_monk"), SoundEvent.SWING_BLUNT)
        self.assertEqual(get_weapon_swing_event("purple_ninja"), SoundEvent.SLASH_CHAIN)
        self.assertEqual(get_weapon_swing_event("orin"), SoundEvent.SWING_SHAMISEN)

        # Superfícies por tipo de terreno
        self.assertEqual(get_surface_footstep_event("grass_lawn"), SoundEvent.FOOTSTEP_GRASS)
        self.assertEqual(get_surface_footstep_event("wooden_bridge"), SoundEvent.FOOTSTEP_WOOD)
        self.assertEqual(get_surface_footstep_event("stone_pavement"), SoundEvent.FOOTSTEP_STONE)
        self.assertEqual(get_surface_footstep_event("gravel_path"), SoundEvent.FOOTSTEP_GRAVEL)
        self.assertEqual(get_surface_footstep_event("water_puddle"), SoundEvent.FOOTSTEP_WATER)
        self.assertEqual(get_surface_footstep_event("mud_swamp"), SoundEvent.FOOTSTEP_MUD)

    def test_02_sound_manager_pitch_variation_and_micro_jitter(self):
        """Verifica se o SoundManager constrói variações de pitch e aplica jitter de ganho."""
        base_sound = self.sound_mgr.get_sound(SoundEvent.SLASH_KATANA)
        self.assertIsNotNone(base_sound)

        variants = self.sound_mgr._build_pitch_variants(base_sound)
        self.assertGreaterEqual(len(variants), 1)

        # Solicitar com variação não deve lançar exceção
        snd_var = self.sound_mgr.get_sound_with_variation(SoundEvent.SLASH_KATANA)
        self.assertIsNotNone(snd_var)

        # Tocar som com variação
        ch = self.sound_mgr.play(SoundEvent.SLASH_KATANA, volume_scale=0.8, pitch_variance=True)

    def test_03_sound_manager_multi_layer(self):
        """Verifica se play_layered dispara camadas concomitantes de áudio visceral."""
        # Impacto letal: deve disparar golpe + carne visceral + jato arterial
        channels_fatal = self.sound_mgr.play_layered(SoundEvent.FATAL_STRIKE, weapon="benkei")
        self.assertIsInstance(channels_fatal, list)

        # Bloqueio perfeito: deve disparar parry + deflexão em armadura
        channels_parry = self.sound_mgr.play_layered(SoundEvent.PARRY)
        self.assertIsInstance(channels_parry, list)

        # Passo em superfície
        channels_step = self.sound_mgr.play_layered(SoundEvent.FOOTSTEP, surface="stone")
        self.assertIsInstance(channels_step, list)

    def test_04_realistic_wav_assets_exist_and_load(self):
        """Verifica se os arquivos WAV sintetizados fisicamente existem no disco e são válidos."""
        sfx_dir = os.path.join(ROOT, "assets", "sounds", "sfx")
        crucial_events = [
            "slash_katana", "slash_heavy", "slash_rapier", "swing_blunt",
            "slash_chain", "swing_shamisen", "flesh_cleave", "bone_crush",
            "arterial_spray", "armor_clang", "wood_shatter",
            "footstep_grass", "footstep_wood", "footstep_stone",
            "footstep_gravel", "footstep_water", "footstep_mud"
        ]
        for name in crucial_events:
            path = os.path.join(sfx_dir, f"{name}.wav")
            self.assertTrue(os.path.exists(path), f"Arquivo WAV ausente: {path}")
            snd = pygame.mixer.Sound(path)
            self.assertGreater(snd.get_length(), 0.0)

    def test_05_sumie_callout_and_floating_banner(self):
        """Verifica renderização da fita de aguada Sumi-E e do FloatingBanner cinematográfico."""
        # Teste direto da fita Sumi-E
        render_sumie_ribbon(self.screen, "GOLPE FATAL!", 640, 360, alpha=220, kanji_seal="斬")

        # Teste de FloatingBanner encapsulando a fita
        banner = FloatingBanner("CLASH MUTUAL!", 0.0, 0.0, wz=1.5, color=(255, 220, 80))
        dummy_font = pygame.font.Font(None, 24)
        banner.render(self.screen, self.camera, dummy_font)

    def test_06_clash_qte_crossed_blades_prompt(self):
        """Verifica o prompt renovado de Tsubazeriai (lâminas cruzadas, anel e selo 斬)."""
        clash = ClashSystem()
        p1 = RedSamurai(0, 0)
        p2 = BlueSamurai(1.5, 0)
        clash.trigger(p1, p2, 0.75, 0.0, camera=self.camera)
        clash.key_hints = ("J", "U")

        # Renderizar em diferentes momentos da janela de tensão
        clash.timer = 0.9
        clash.render(self.screen, self.camera)

        clash.timer = 0.2  # Tensão máxima (carmesim)
        clash.render(self.screen, self.camera)
        self.assertTrue(clash.is_active)

    def test_07_modern_hud_and_round_result(self):
        """Verifica barras de vida em paralelogramo com rastro de dano e painel de resultados."""
        p1 = RedSamurai(0, 0)
        p2 = BlueSamurai(2, 0)
        p1.hp = 1
        p1._drain_hp = 2.0  # Simula perda de vida recente para o rastro de dano (drain trail)

        panel = pygame.Rect(370, 10, 540, 66)
        render_round_pips(self.screen, 1, 0, (255, 80, 80), (80, 160, 255), panel_rect=panel)
        render_damage_bars(self.screen, p1, p2, (255, 80, 80), (80, 160, 255), panel)

        # Teste da tela de resultado de partida
        result_screen = RoundResultScreen()
        result_screen.show("KENSHI", (255, 80, 80), 2, 1)
        result_screen.update(0.5)
        result_screen.render(self.screen)


if __name__ == "__main__":
    unittest.main()
