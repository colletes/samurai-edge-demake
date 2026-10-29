#!/usr/bin/env python3
"""Gera o 'Character Atlas' composto com os 24 lutadores (6 colunas x 4 linhas).

Cada lutador tem sua arte conceitual de corpo inteiro com seu nome em destaque logo abaixo.
Serve como o arquivo de referência único (1 slot de anexo) para o Nano Banana na geração do slide final.

Arquivo gerado: assets/concepts/roster_24_characters_atlas.jpg
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONCEPTS_DIR = os.path.join(ROOT, "assets", "concepts")
OUT_PATH = os.path.join(CONCEPTS_DIR, "roster_24_characters_atlas.jpg")

ROSTER_DATA = [
    # Linha 1: Veteranos de Lâmina & Pólvora
    ("kenshi", "1. KENSHI (Ronin)"),
    ("musashi", "2. MUSASHI (Niten Dual Blade)"),
    ("hanzo", "3. HANZO (Iga Shinobi Leader)"),
    ("joe", "4. JOE (American Ninja)"),
    ("saitou", "5. SAITOU (Shinsengumi)"),
    ("teppo", "6. TEPPO (Rifle Marksman)"),
    # Linha 2: Veteranas & Kunoichi
    ("murasaki", "7. MURASAKI (Chain Kunoichi)"),
    ("kasumi", "8. KASUMI (Mist Kunoichi)"),
    ("okuni", "9. OKUNI (Kabuki Maiden)"),
    ("tomoe", "10. TOMOE (Kyudo Shrine Miko)"),
    ("anne", "11. ANNE (Corsair Pirate)"),
    ("julie", "12. JULIE (French Musketeer)"),
    # Linha 3: Ciclos 1 a 3
    ("ren", "13. REN (Shaolin Bare-Fist Monk)"),
    ("chiyo", "14. CHIYO (Dual Kodachi Kunoichi)"),
    ("benkei", "15. BENKEI (Heavy Armor Monk)"),
    ("orin", "16. O-RIN (Blind Shamisen Minstrel)"),
    ("goro", "17. GORO (Peasant Rebel Kuwa)"),
    ("ichi", "18. ICHI (Blind Cane Masseuse)"),
    # Linha 4: Ciclos 4 a 6
    ("valerius", "19. VALERIUS (Prussian Occultist)"),
    ("seimei", "20. SEIMEI (Imperial Onmyoji)"),
    ("daiki", "21. DAIKI (Ascetic Bo Monk)"),
    ("aoi", "22. AOI (Ainu Huntress)"),
    ("raiden", "23. RAIDEN (Sumo Yokozuna)"),
    ("hendrika", "24. HENDRIKA (Dutch Scholar)"),
]

COLS = 6
ROWS = 4
CELL_W = 420
IMG_H = 580
LABEL_H = 55
CELL_H = IMG_H + LABEL_H
MARGIN_X = 40
MARGIN_Y = 120  # Espaço para o cabeçalho superior
GAP_X = 20
GAP_Y = 24

TOTAL_W = MARGIN_X * 2 + COLS * CELL_W + (COLS - 1) * GAP_X
TOTAL_H = MARGIN_Y + ROWS * CELL_H + (ROWS - 1) * GAP_Y + 40


def build_atlas():
    atlas = Image.new("RGB", (TOTAL_W, TOTAL_H), color=(18, 16, 20))
    draw = ImageDraw.Draw(atlas)

    # Fontes
    font_title_path = os.path.join(ROOT, "assets", "fonts", "Cinzel-Regular.ttf")
    font_label_path = os.path.join(ROOT, "assets", "fonts", "Cinzel-Regular.ttf")

    try:
        font_header = ImageFont.truetype(font_title_path, 42)
        font_sub = ImageFont.truetype(font_title_path, 22)
        font_name = ImageFont.truetype(font_label_path, 20)
    except Exception:
        font_header = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_name = ImageFont.load_default()

    # Cabeçalho do Atlas
    title_text = "SAMURAI EDGE: BAKUMATSU  ―  24 FIGHTERS ROSTER REFERENCE ATLAS"
    sub_text = "ALL 24 CANONICAL FIGHTER DESIGNS FOR EPILOGUE & CREDITS COMPOSITION"
    draw.text((TOTAL_W // 2, 40), title_text, fill=(218, 175, 75), font=font_header, anchor="mm")
    draw.text((TOTAL_W // 2, 85), sub_text, fill=(185, 180, 170), font=font_sub, anchor="mm")

    # Linha divisória dourada
    draw.line([(MARGIN_X, 105), (TOTAL_W - MARGIN_X, 105)], fill=(140, 110, 45), width=2)

    for idx, (char_id, label) in enumerate(ROSTER_DATA):
        col = idx % COLS
        row = idx // COLS
        x = MARGIN_X + col * (CELL_W + GAP_X)
        y = MARGIN_Y + row * (CELL_H + GAP_Y)

        # Fundo da célula
        draw.rectangle([x, y, x + CELL_W, y + CELL_H], fill=(26, 24, 30), outline=(65, 55, 45), width=1)

        # Carregar imagem do lutador
        img_file = os.path.join(CONCEPTS_DIR, f"{char_id}_full_concept.jpg")
        if os.path.exists(img_file):
            im = Image.open(img_file)
            # Escalar mantendo proporção para caber em (CELL_W - 12, IMG_H - 12)
            max_w, max_h = CELL_W - 16, IMG_H - 16
            scale = min(max_w / im.width, max_h / im.height)
            nw = int(im.width * scale)
            nh = int(im.height * scale)
            scaled = im.resize((nw, nh), Image.Resampling.LANCZOS)
            ox = x + (CELL_W - nw) // 2
            oy = y + 8 + (IMG_H - nh) // 2
            atlas.paste(scaled, (ox, oy))
        else:
            draw.text((x + CELL_W // 2, y + IMG_H // 2), f"{char_id}\n(not found)", fill=(200, 80, 80), font=font_name, anchor="mm")

        # Tarja preta com borda dourada para o nome do personagem
        label_rect = [x + 4, y + IMG_H, x + CELL_W - 4, y + CELL_H - 4]
        draw.rectangle(label_rect, fill=(12, 10, 14), outline=(180, 140, 60), width=2)
        draw.text((x + CELL_W // 2, y + IMG_H + LABEL_H // 2 - 2), label, fill=(245, 235, 215), font=font_name, anchor="mm")

    atlas.save(OUT_PATH, "JPEG", quality=92, optimize=True)
    file_size_mb = os.path.getsize(OUT_PATH) / (1024 * 1024)
    print(f"Atlas gerado com sucesso: {OUT_PATH}")
    print(f"Dimensões: {TOTAL_W}x{TOTAL_H} | Tamanho: {file_size_mb:.2f} MB")


if __name__ == "__main__":
    build_atlas()
