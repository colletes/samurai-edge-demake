"""
Testes automatizados de cobertura, simetria e formatação de i18n (P4 da v2.0.0).
Valida:
1. Simetria estrita entre dicionários de Português (pt) e Inglês (en).
2. Consistência de marcadores de interpolação {placeholder} entre ambos os idiomas.
3. Resiliência do método t() para todas as chaves e fallback seguro para chaves desconhecidas.
4. Renderização limpa de telas de interface nos dois idiomas.
"""
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SAMURAI_EDGE_LANG"] = "pt"

import pygame
pygame.init()
pygame.font.init()

from src.i18n import I18N, LANG_PT, LANG_EN, t, set_lang, get_lang, toggle_lang
from src.ui.settings_menu import SettingsMenu
from src.ui.pause_menu import PauseMenu
from src.ui.title_screen import SumieTitleScreen
from src.config import DEFAULT_CONTROLS


class TestTranslationAndUI(unittest.TestCase):
    def setUp(self):
        set_lang(LANG_PT, persist=False)

    def test_i18n_key_symmetry(self):
        """Todas as chaves presentes em PT devem estar em EN e vice-versa."""
        pt_keys = set(I18N[LANG_PT].keys())
        en_keys = set(I18N[LANG_EN].keys())

        missing_in_en = pt_keys - en_keys
        missing_in_pt = en_keys - pt_keys

        self.assertEqual(
            missing_in_en, set(),
            f"Chaves presentes em PT mas ausentes em EN: {missing_in_en}"
        )
        self.assertEqual(
            missing_in_pt, set(),
            f"Chaves presentes em EN mas ausentes em PT: {missing_in_pt}"
        )

    def test_i18n_placeholder_consistency(self):
        """Marcadores de interpolação {nome} devem coincidir entre PT e EN."""
        placeholder_pattern = re.compile(r"\{([a-zA-Z0-9_]+)\}")
        pt_dict = I18N[LANG_PT]
        en_dict = I18N[LANG_EN]

        mismatches = []
        for key in pt_dict:
            pt_text = str(pt_dict[key])
            en_text = str(en_dict[key])

            pt_placeholders = set(placeholder_pattern.findall(pt_text))
            en_placeholders = set(placeholder_pattern.findall(en_text))

            if pt_placeholders != en_placeholders:
                mismatches.append((key, pt_placeholders, en_placeholders))

        self.assertEqual(
            mismatches, [],
            f"Inconsistência de marcadores de formatação: {mismatches}"
        )

    def test_t_function_resilience(self):
        """t() deve retornar strings ou listas válidas para todas as chaves em ambos os idiomas."""
        for lang in (LANG_PT, LANG_EN):
            set_lang(lang, persist=False)
            for key in I18N[lang]:
                res = t(key)
                self.assertTrue(isinstance(res, (str, list)))
                self.assertGreater(len(res), 0)

        # Fallback de chave inexistente devolve a própria chave sem quebrar
        self.assertEqual(t("nonexistent_test_key_xyz"), "nonexistent_test_key_xyz")

    def test_ui_screens_render_bilingual(self):
        """Telas principais devem renderizar perfeitamente em PT e em EN."""
        surf = pygame.Surface((1280, 720))
        font_large = pygame.font.SysFont("sans-serif", 32)
        font_mid = pygame.font.SysFont("sans-serif", 20)
        font_small = pygame.font.SysFont("sans-serif", 14)

        for lang in (LANG_PT, LANG_EN):
            set_lang(lang, persist=False)
            self.assertEqual(get_lang(), lang)

            # 1. Title Screen
            title_screen = SumieTitleScreen()
            title_screen.render(surf, font_large, font_mid, font_small)

            # 2. Settings Menu
            settings_menu = SettingsMenu(dict(DEFAULT_CONTROLS))
            settings_menu.open()
            settings_menu.render(surf, font_large, font_mid, font_small)

            # 3. Pause Menu
            pause_menu = PauseMenu()
            pause_menu.open(surf.copy())
            pause_menu.render(surf)


if __name__ == "__main__":
    unittest.main()
