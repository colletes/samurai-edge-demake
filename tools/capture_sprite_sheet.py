"""
Folha de sprites quadro a quadro dos lutadores (6.5.4): idle, caminhada, ataque, esquiva, estados e especiais,
com o conceito e o portrait ao lado (e os sprites HD-2D de Kenshi e Murasaki, quando existem).

Uso: SDL_VIDEODRIVER=dummy ./venv/bin/python tools/capture_sprite_sheet.py [--tag before] [--only okuni,kenshi] [--zoom 2.6]
Saída: docs/screenshots/sprites/<lutador>_<tag>.png
"""
import argparse
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src.entities.voxel_models import render_voxel_humanoid
from src.isometric.camera import Camera

OUT = os.path.join(ROOT, "docs", "screenshots", "sprites")

# nome do lutador -> (char_type do renderizador, arquivo do conceito, retrato, ataque em s, especiais)
FIGHTERS = {
    "kenshi": ("kenshin", "kenshi_concept.jpg", "kenshi_bust.png", 0.16, ()),
    "musashi": ("musashi", "musashi_concept.jpg", "musashi_bust.png", 0.18, ()),
    "hanzo": ("ninja", "hanzo_concept.jpg", "hanzo_bust.png", 0.18, ()),
    "joe": ("american", "joe_concept.jpg", "joe_bust.png", 0.20, ()),
    "saitou": ("saitou", "saitou_concept.jpg", "saitou_bust.png", 0.25, ("GATOTSU_CHARGE", "ZEROSHIKI")),
    "teppo": ("rifleman", "teppo_concept.jpg", "teppo_bust.png", 0.20, ()),
    "murasaki": ("purple", "murasaki_concept.jpg", "murasaki_bust.png", 0.16, ()),
    "kasumi": ("kasumi", "kasumi_concept.jpg", "kasumi_bust.png", 0.20, ()),
    "okuni": ("okuni", "okuni_concept.jpg", "okuni_bust.png", 0.20, ()),
    "tomoe": ("tomoe", "tomoe_concept.jpg", "tomoe_bust.png", 0.20, ()),
    "anne": ("pirate", "anne_concept.jpg", "anne_bust.png", 0.22, ("CUTLASS_CLEAVE",)),
    "julie": ("musketeer", "julie_concept.jpg", "julie_bust.png", 0.24, ("FLECHE", "CAPE_FLOURISH")),
}
HD2D_SPRITES = {"kenshi": "kenshi", "murasaki": "murasaki"}

# direções de olhar no mundo; na projeção isométrica clássica (x - y vai para a direita, x + y para baixo)
FACINGS = {"frente": (1.0, 1.0), "costas": (-1.0, -1.0), "esquerda": (-1.0, 1.0), "direita": (1.0, -1.0)}

CELL_W, CELL_H = 180, 224
REF_W = 300
LABEL_H = 22
BG = (34, 36, 44)
PANEL = (44, 47, 58)
TEXT = (226, 230, 238)
DIM = (150, 156, 170)


def _font(size):
    return pygame.font.Font(None, size)


class CellRenderer:
    def __init__(self, zoom: float):
        self.zoom = zoom
        self.canvas = pygame.Surface((1280, 720))

    def cell(self, char_type, state, state_timer, facing, walk_timer=0.0, is_moving=False, alive=True) -> pygame.Surface:
        cam = Camera(0.0, 0.0)
        cam.zoom = self.zoom
        self.canvas.fill(PANEL)
        render_voxel_humanoid(self.canvas, cam, 0.0, 0.0, 0.0, facing[0], facing[1], state, state_timer, alive, char_type,
                              walk_timer=walk_timer, is_moving=is_moving)
        fx, fy = cam.apply(0.0, 0.0, 0.0)
        rect = pygame.Rect(fx - CELL_W // 2, fy - int(CELL_H * 0.80), CELL_W, CELL_H)
        out = pygame.Surface((CELL_W, CELL_H))
        out.blit(self.canvas, (0, 0), rect)
        return out


def _cells_for(name, renderer: CellRenderer):
    """Seções (título, [(rótulo, imagem)]) de um lutador."""
    char_type, _, _, atk_dur, specials = FIGHTERS[name]
    r = renderer.cell
    sections = []
    idle_t = (math.pi / (2 * 2.8), 3 * math.pi / (2 * 2.8))
    sections.append(("IDLE (2 fases de respiração por direção)", [
        (f"{face} {i + 1}", r(char_type, "IDLE", 0.0, vec, walk_timer=idle_t[i]))
        for face, vec in FACINGS.items() for i in range(2)]))
    stride = 2 * math.pi / 9.0
    for face in ("direita", "frente", "costas"):
        sections.append((f"CAMINHADA, {face} (8 quadros)", [
            (str(k + 1), r(char_type, "WALK", 0.0, FACINGS[face], walk_timer=stride * k / 8.0, is_moving=True)) for k in range(8)]))
    for face in ("direita", "frente"):
        sections.append((f"ATAQUE, {face} (8 quadros, 0% a 100%)", [
            (f"{int((k + 0.5) / 8 * 100)}%", r(char_type, "ATTACK", atk_dur * (1.0 - (k + 0.5) / 8.0), FACINGS[face])) for k in range(8)]))
    states = [("esquiva 1", "ROLL", 0.18), ("esquiva 2", "ROLL", 0.10), ("esquiva 3", "ROLL", 0.03),
              ("defesa", "PARRY", 0.2), ("recuperação", "RECOVERY", 0.2), ("atordoado", "STUNNED", 0.5), ("morto", "DEAD", 0.0)]
    cells = [(label, r(char_type, state, timer, FACINGS["direita"], walk_timer=0.05, is_moving=state == "ROLL", alive=state != "DEAD"))
             for label, state, timer in states]
    sections.append(("ESQUIVA E ESTADOS (direita)", cells))
    if specials:
        sp = []
        for state in specials:
            for k, p in enumerate((0.15, 0.5, 0.85)):
                sp.append((f"{state.lower()} {k + 1}", r(char_type, state, atk_dur * (1.0 - p), FACINGS["direita"], walk_timer=0.05)))
        sections.append(("ESPECIAIS (direita)", sp[:8]))
    return sections


def _load(path, size=None):
    if not os.path.exists(path):
        return None
    img = pygame.image.load(path).convert_alpha()
    if size:
        w, h = img.get_size()
        k = min(size[0] / w, size[1] / h)
        img = pygame.transform.smoothscale(img, (max(1, int(w * k)), max(1, int(h * k))))
    return img


def _reference_column(name, height) -> pygame.Surface:
    _, concept, bust, _, _ = FIGHTERS[name]
    col = pygame.Surface((REF_W, height))
    col.fill(BG)
    y = 8
    font = _font(20)
    concept_img = _load(os.path.join(ROOT, "assets", "concepts", concept), (REF_W - 16, 330))
    if concept_img:
        col.blit(font.render("CONCEITO", True, DIM), (8, y))
        col.blit(concept_img, (8, y + 18))
        y += 18 + concept_img.get_height() + 10
    bust_img = _load(os.path.join(ROOT, "assets", "portraits", bust), (REF_W - 16, 200))
    if bust_img:
        col.blit(font.render("PORTRAIT", True, DIM), (8, y))
        col.blit(bust_img, (8, y + 18))
        y += 18 + bust_img.get_height() + 10
    hd = HD2D_SPRITES.get(name)
    if hd:
        col.blit(font.render("SPRITES HD-2D (referência)", True, DIM), (8, y))
        x = 8
        for frame in ("idle", "walk_0", "walk_1", "attack"):
            img = _load(os.path.join(ROOT, "hd2d_edition", "assets", "sprites", hd, f"{frame}.png"))
            if img:
                img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
                col.blit(img, (x, y + 18))
                x += img.get_width() + 2
    return col


def build_sheet(name: str, tag: str, zoom: float) -> pygame.Surface:
    renderer = CellRenderer(zoom)
    sections = _cells_for(name, renderer)
    cols = max(len(cells) for _, cells in sections)
    width = REF_W + cols * CELL_W + 12
    title_h = 44
    section_h = LABEL_H + CELL_H + 18
    height = title_h + len(sections) * section_h + 10
    sheet = pygame.Surface((width, max(height, 760)))
    sheet.fill(BG)
    big, small = _font(34), _font(20)
    sheet.blit(big.render(f"{name.upper()}  -  {tag}", True, TEXT), (REF_W + 12, 10))
    sheet.blit(_reference_column(name, sheet.get_height()), (0, 0))
    y = title_h
    for title, cells in sections:
        sheet.blit(small.render(title, True, (240, 200, 110)), (REF_W + 12, y + 2))
        for i, (label, img) in enumerate(cells):
            x = REF_W + 6 + i * CELL_W
            sheet.blit(img, (x, y + LABEL_H))
            pygame.draw.rect(sheet, (70, 74, 90), (x, y + LABEL_H, CELL_W, CELL_H), 1)
            sheet.blit(small.render(label, True, DIM), (x + 6, y + LABEL_H + CELL_H + 1))
        y += section_h
    return sheet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="before")
    parser.add_argument("--only", default="")
    parser.add_argument("--zoom", type=float, default=3.2)
    opts = parser.parse_args()

    names = [n for n in FIGHTERS if not opts.only or n in opts.only.split(",")]
    os.makedirs(OUT, exist_ok=True)
    for name in names:
        path = os.path.join(OUT, f"{name}_{opts.tag}.png")
        pygame.image.save(build_sheet(name, opts.tag, opts.zoom), path)
        print("gravado", os.path.relpath(path, ROOT), flush=True)


if __name__ == "__main__":
    main()
