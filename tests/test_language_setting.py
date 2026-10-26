"""
Testes automatizados para o Entregável 5.5.7: Idioma Padrão da Máquina com Escolha Salva.
Verifica:
1. Preferência 'auto' segue detecção de sistema / SAMURAI_EDGE_LANG.
2. Persistência de 'pt', 'en' e 'auto' em settings.json mantendo demais chaves intactas.
3. Tratamento defensivo contra arquivo inexistente, corrompido ou chaves com valores inválidos.
4. toggle_lang() persiste a nova escolha no arquivo de configurações.
5. SettingsMenu.cycle_language() alterna corretamente e atualiza o botão na interface.
"""
import os
import sys
import json
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.font.init()

from src.i18n import (
    LANG_AUTO, LANG_PT, LANG_EN,
    load_language_setting, save_language_setting,
    get_saved_language_preference, apply_saved_language,
    detect_system_lang, get_lang, set_lang, toggle_lang, t
)
from src.ui.settings_menu import SettingsMenu
from src.config import DEFAULT_CONTROLS


class TestLanguageSetting(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_settings = os.path.join(self.temp_dir.name, "settings.json")
        self.orig_env_lang = os.environ.get("SAMURAI_EDGE_LANG")

    def tearDown(self):
        if self.orig_env_lang is not None:
            os.environ["SAMURAI_EDGE_LANG"] = self.orig_env_lang
        elif "SAMURAI_EDGE_LANG" in os.environ:
            del os.environ["SAMURAI_EDGE_LANG"]
        self.temp_dir.cleanup()

    def test_missing_file_defaults_to_auto(self):
        """Arquivo inexistente deve retornar 'auto' sem lançar exceções."""
        pref = load_language_setting(self.temp_settings)
        self.assertEqual(pref, LANG_AUTO)

    def test_corrupted_file_defaults_to_auto(self):
        """Arquivo com JSON corrompido deve retornar 'auto' de forma resiliente."""
        with open(self.temp_settings, "w", encoding="utf-8") as f:
            f.write("{ INVALID JSON DATA --- broken !!!")
        pref = load_language_setting(self.temp_settings)
        self.assertEqual(pref, LANG_AUTO)

    def test_invalid_value_defaults_to_auto(self):
        """Valores não suportados (ex: 'es', 999, None) devem cair com segurança em 'auto'."""
        for invalid_val in ["es", "fr", "de", 123, None, {}]:
            with open(self.temp_settings, "w", encoding="utf-8") as f:
                json.dump({"gameplay": {"language": invalid_val}}, f)
            pref = load_language_setting(self.temp_settings)
            self.assertEqual(pref, LANG_AUTO)

    def test_save_and_load_persistence(self):
        """Gravação de 'pt', 'en' e 'auto' deve persistir e preservar outras seções."""
        initial_data = {
            "video": {"fullscreen": False, "effects_quality": "high"},
            "audio": {"master_volume": 0.8}
        }
        with open(self.temp_settings, "w", encoding="utf-8") as f:
            json.dump(initial_data, f)

        # Salva PT
        res = save_language_setting(LANG_PT, self.temp_settings)
        self.assertTrue(res)
        self.assertEqual(load_language_setting(self.temp_settings), LANG_PT)

        # Verifica preservação de seções existentes
        with open(self.temp_settings, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["video"]["effects_quality"], "high")
        self.assertEqual(data["gameplay"]["language"], LANG_PT)

        # Salva EN
        res = save_language_setting(LANG_EN, self.temp_settings)
        self.assertTrue(res)
        self.assertEqual(load_language_setting(self.temp_settings), LANG_EN)

        # Salva AUTO
        res = save_language_setting(LANG_AUTO, self.temp_settings)
        self.assertTrue(res)
        self.assertEqual(load_language_setting(self.temp_settings), LANG_AUTO)

    def test_env_var_override_has_highest_priority(self):
        """SAMURAI_EDGE_LANG sempre se sobrepõe ao arquivo settings.json."""
        save_language_setting(LANG_PT, self.temp_settings)

        # Força EN via variável de ambiente
        os.environ["SAMURAI_EDGE_LANG"] = "en"
        active = apply_saved_language(self.temp_settings)
        self.assertEqual(active, LANG_EN)

        # Força PT via variável de ambiente
        save_language_setting(LANG_EN, self.temp_settings)
        os.environ["SAMURAI_EDGE_LANG"] = "pt"
        active = apply_saved_language(self.temp_settings)
        self.assertEqual(active, LANG_PT)

    def test_apply_saved_language_auto_uses_system_lang(self):
        """Quando a preferência for 'auto' e sem env var, usa detecção da máquina."""
        if "SAMURAI_EDGE_LANG" in os.environ:
            del os.environ["SAMURAI_EDGE_LANG"]
        save_language_setting(LANG_AUTO, self.temp_settings)

        detected = detect_system_lang()
        active = apply_saved_language(self.temp_settings)
        self.assertEqual(active, detected)

    def test_toggle_lang_persists_new_language(self):
        """toggle_lang(persist=True) deve alternar o idioma ativo e gravar em settings.json."""
        if "SAMURAI_EDGE_LANG" in os.environ:
            del os.environ["SAMURAI_EDGE_LANG"]

        set_lang(LANG_PT, persist=True, path=self.temp_settings)
        self.assertEqual(get_lang(), LANG_PT)
        self.assertEqual(load_language_setting(self.temp_settings), LANG_PT)

        # Alterna para EN
        new_lang = toggle_lang(persist=True, path=self.temp_settings)
        self.assertEqual(new_lang, LANG_EN)
        self.assertEqual(get_lang(), LANG_EN)
        self.assertEqual(load_language_setting(self.temp_settings), LANG_EN)

        # Alterna de volta para PT
        new_lang = toggle_lang(persist=True, path=self.temp_settings)
        self.assertEqual(new_lang, LANG_PT)
        self.assertEqual(get_lang(), LANG_PT)
        self.assertEqual(load_language_setting(self.temp_settings), LANG_PT)

    def test_settings_menu_cycle_language_and_interaction(self):
        """SettingsMenu.cycle_language() deve ciclar auto -> pt -> en -> auto."""
        if "SAMURAI_EDGE_LANG" in os.environ:
            del os.environ["SAMURAI_EDGE_LANG"]

        menu = SettingsMenu(dict(DEFAULT_CONTROLS))

        # Define estado inicial como 'auto'
        save_language_setting(LANG_AUTO)
        self.assertEqual(get_saved_language_preference(), LANG_AUTO)

        # Ciclo 1: auto -> pt
        menu.cycle_language()
        self.assertEqual(get_saved_language_preference(), LANG_PT)
        self.assertEqual(get_lang(), LANG_PT)

        # Ciclo 2: pt -> en
        menu.cycle_language()
        self.assertEqual(get_saved_language_preference(), LANG_EN)
        self.assertEqual(get_lang(), LANG_EN)

        # Ciclo 3: en -> auto
        menu.cycle_language()
        self.assertEqual(get_saved_language_preference(), LANG_AUTO)

    def test_settings_menu_render_and_click_language_button(self):
        """Verifica se o botão de idioma renderiza com bounding box válida e aceita clique/tecla L."""
        menu = SettingsMenu(dict(DEFAULT_CONTROLS))
        menu.open()

        surf = pygame.Surface((1280, 720))
        font_large = pygame.font.SysFont("sans-serif", 32)
        font_mid = pygame.font.SysFont("sans-serif", 20)
        font_small = pygame.font.SysFont("sans-serif", 14)

        # Render em modo normal (pergaminho)
        menu.render(surf, font_large, font_mid, font_small)
        self.assertGreater(menu.language_toggle_rect.width, 50)
        self.assertGreater(menu.language_toggle_rect.height, 15)

        # Simular clique do mouse no botão de idioma
        mx = menu.language_toggle_rect.centerx
        my = menu.language_toggle_rect.centery
        click_ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(mx, my))

        save_language_setting(LANG_AUTO)
        consumed = menu.handle_event(click_ev)
        self.assertTrue(consumed)
        self.assertEqual(get_saved_language_preference(), LANG_PT)

        # Simular pressionamento da tecla L
        key_l_ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_l)
        consumed_key = menu.handle_event(key_l_ev)
        self.assertTrue(consumed_key)
        self.assertEqual(get_saved_language_preference(), LANG_EN)


if __name__ == "__main__":
    unittest.main()
