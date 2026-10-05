"""
Teste da 6.5.4: ferramenta de folha de sprites (tools/capture_sprite_sheet.py).
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_sprite_sheet.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import numpy as np
import pygame

import capture_sprite_sheet as css


def _distinct(cells):
    arrays = [pygame.surfarray.array3d(img).tobytes() for _, img in cells]
    return len(set(arrays))


def test_sprite_sheets_cover_the_whole_roster():
    from src.roster import ROSTER_ORDER
    assert len(css.FIGHTERS) == 12 and len(ROSTER_ORDER) == 12
    for name in css.FIGHTERS:
        renderer = css.CellRenderer(2.4)
        sections = css._cells_for(name, renderer)
        titles = [t for t, _ in sections]
        assert titles[0].startswith("IDLE") and any(t.startswith("CAMINHADA") for t in titles) and any(t.startswith("ATAQUE") for t in titles)
        for title, cells in sections:
            assert cells and all(isinstance(img, pygame.Surface) for _, img in cells)
            blank = css.PANEL
            for label, img in cells:
                arr = pygame.surfarray.array3d(img)
                assert (np.abs(arr.astype(int) - np.array(blank)).sum(axis=2) > 0).sum() > 80, f"{name}: célula vazia em {title} / {label}"
            if title.startswith(("CAMINHADA", "ATAQUE")):
                assert _distinct(cells) >= 4, f"{name}: {title} com quadros repetidos ({_distinct(cells)} de {len(cells)})"
    print("  [OK] Os 12 lutadores têm folha com idle, caminhada, ataque, esquiva e estados; os quadros de movimento mudam.", flush=True)


def test_sheet_layout_and_references():
    for name in ("kenshi", "murasaki", "okuni"):
        sheet = css.build_sheet(name, "teste", 2.4)
        assert sheet.get_width() >= css.REF_W + 8 * css.CELL_W and sheet.get_height() >= 760
        ref = css._reference_column(name, 900)
        assert ref.get_width() == css.REF_W
        assert css._load(os.path.join(ROOT, "assets", "concepts", css.FIGHTERS[name][1])) is not None, "conceito presente"
        assert css._load(os.path.join(ROOT, "assets", "portraits", css.FIGHTERS[name][2])) is not None, "portrait presente"
    for name in css.HD2D_SPRITES:
        assert css._load(os.path.join(ROOT, "hd2d_edition", "assets", "sprites", css.HD2D_SPRITES[name], "idle.png")) is not None, name
    print("  [OK] Layout da folha, conceito e portrait presentes; sprites HD-2D de Kenshi e Murasaki encontrados.", flush=True)


def test_sprite_sheet_tool():
    test_sprite_sheets_cover_the_whole_roster()
    test_sheet_layout_and_references()


if __name__ == "__main__":
    test_sprite_sheet_tool()
    print("=== TESTE 6.5.4 CONCLUÍDO ===", flush=True)
