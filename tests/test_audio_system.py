"""
Suíte de Testes Automatizados para a Fase 2: Arquitetura de Áudio & SFX Feudal.
Valida:
1. Geração procedural pura de ondas PCM 16-bit 44.1kHz sem dependência externa.
2. Síntese de todos os 24 eventos de SoundEvent.
3. SoundManager singleton, canais, volume clamping e fallback gracioso.
4. Persistência de volumes no controls_storage.py.
5. Execução segura em ambientes headless / sem dispositivo de som físico.
"""
import os
import sys
import unittest
import io
import wave
import tempfile
import json

# Forçar driver de áudio dummy para execução segura e headless em CI/CD
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Adicionar raiz do projeto ao path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pygame
pygame.init()
try:
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except Exception:
    pass

from src.audio.sound_events import SoundEvent, MusicTrack
from src.audio.procedural_sfx import generate_procedural_sound
from src.audio.sound_manager import SoundManager
from src.input.controls_storage import load_controls_config, save_controls_config


class TestProceduralSFX(unittest.TestCase):
    """Testa a geração procedural de áudio em memória (PCM 16-bit estéreo 44.1kHz)."""

    def test_all_sound_events_generate_valid_sound(self):
        """Todos os eventos de SoundEvent devem gerar um objeto pygame.mixer.Sound válido."""
        for event in SoundEvent:
            with self.subTest(event=event):
                snd = generate_procedural_sound(event)
                self.assertIsNotNone(snd, f"Falha ao gerar som procedural para o evento: {event}")
                self.assertIsInstance(snd, pygame.mixer.Sound)
                # Verifica se a duração do som é positiva e razoável (< 5 segundos para SFX)
                duration = snd.get_length()
                self.assertGreater(duration, 0.01, f"{event} gerou duração quase nula")
                self.assertLess(duration, 5.0, f"{event} gerou som longo demais para SFX")


class TestSoundManager(unittest.TestCase):
    """Testa o gerenciador de som, cache, controle de volume e canais."""

    def setUp(self):
        self.mgr = SoundManager.get_instance()

    def test_singleton_instance(self):
        mgr2 = SoundManager.get_instance()
        self.assertIs(self.mgr, mgr2, "SoundManager deve seguir padrão Singleton estrito")

    def test_volume_clamping(self):
        """Volumes devem ser confinados com segurança no intervalo [0.0, 1.0]."""
        self.mgr.set_master_volume(1.5)
        self.assertEqual(self.mgr.master_volume, 1.0)
        self.mgr.set_master_volume(-0.5)
        self.assertEqual(self.mgr.master_volume, 0.0)
        self.mgr.set_master_volume(0.8)
        self.assertEqual(self.mgr.master_volume, 0.8)

        self.mgr.set_sfx_volume(2.0)
        self.assertEqual(self.mgr.sfx_volume, 1.0)
        self.mgr.set_sfx_volume(-0.1)
        self.assertEqual(self.mgr.sfx_volume, 0.0)

        self.mgr.set_bgm_volume(1.2)
        self.assertEqual(self.mgr.bgm_volume, 1.0)
        self.mgr.set_bgm_volume(-0.2)
        self.assertEqual(self.mgr.bgm_volume, 0.0)

    def test_play_sound_event_does_not_crash(self):
        """O método play deve reproduzir sons conhecidos sem lançar exceções."""
        for event in (SoundEvent.SWORD_SLASH, SoundEvent.PARRY, SoundEvent.ROUND_START, SoundEvent.FATAL_STRIKE):
            try:
                self.mgr.play(event)
            except Exception as e:
                self.fail(f"play({event}) falhou com exceção: {e}")

    def test_play_music_does_not_crash(self):
        """O método play_music deve transicionar entre trilhas sem quebrar."""
        try:
            self.mgr.play_music(MusicTrack.TITLE_THEME)
            self.mgr.play_music(MusicTrack.CHAR_SELECT_THEME)
            self.mgr.play_music(MusicTrack.KYOTO_THEME)
            self.mgr.play_music(MusicTrack.BAMBOO_THEME)
            self.mgr.stop_music()
        except Exception as e:
            self.fail(f"play_music falhou com exceção: {e}")


class TestAudioPersistence(unittest.TestCase):
    """Testa salvar e carregar os volumes no controls_storage.py."""

    def test_audio_config_save_and_load(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tf:
            temp_path = tf.name

        try:
            import src.input.controls_storage as cs
            orig_file = cs.CONFIG_PATH
            cs.CONFIG_PATH = temp_path

            test_controls = {
                "audio": {
                    "master": 0.85,
                    "sfx": 0.65,
                    "bgm": 0.45
                }
            }

            save_controls_config(test_controls)
            loaded = load_controls_config()

            self.assertIn("audio", loaded)
            self.assertAlmostEqual(loaded["audio"]["master"], 0.85, places=2)
            self.assertAlmostEqual(loaded["audio"]["sfx"], 0.65, places=2)
            self.assertAlmostEqual(loaded["audio"]["bgm"], 0.45, places=2)

        finally:
            if 'orig_file' in locals():
                cs.CONFIG_PATH = orig_file
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
