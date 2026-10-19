#!/usr/bin/env python3
"""
Samurai Edge Demake - iOS App Icon Generator
Gera todos os tamanhos oficiais de ícone do iOS a partir do retrato de alta resolução da Kenshi
e instala diretamente no catálogo Images.xcassets/AppIcon.appiconset do projeto Xcode.
"""
import os
import json
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
CONCEPT_PATH = os.path.join(PROJECT_ROOT, "assets/concepts/kenshi_concept.jpg")
IOS_PROJECT_DIR = os.path.join(PROJECT_ROOT, "build/samuraiedge-ios")
APPICONSET_DIR = os.path.join(IOS_PROJECT_DIR, "samuraiedge/Images.xcassets/AppIcon.appiconset")

ICON_SPECS = [
    # iPhone
    {"name": "icon-20@2x.png", "idiom": "iphone", "size": "20x20", "scale": "2x", "px": 40},
    {"name": "icon-20@3x.png", "idiom": "iphone", "size": "20x20", "scale": "3x", "px": 60},
    {"name": "icon-29@2x.png", "idiom": "iphone", "size": "29x29", "scale": "2x", "px": 58},
    {"name": "icon-29@3x.png", "idiom": "iphone", "size": "29x29", "scale": "3x", "px": 87},
    {"name": "icon-40@2x.png", "idiom": "iphone", "size": "40x40", "scale": "2x", "px": 80},
    {"name": "icon-40@3x.png", "idiom": "iphone", "size": "40x40", "scale": "3x", "px": 120},
    {"name": "icon-60@2x.png", "idiom": "iphone", "size": "60x60", "scale": "2x", "px": 120},
    {"name": "icon-60@3x.png", "idiom": "iphone", "size": "60x60", "scale": "3x", "px": 180},
    # iPad
    {"name": "icon-20@1x.png", "idiom": "ipad", "size": "20x20", "scale": "1x", "px": 20},
    {"name": "icon-20@2x-ipad.png", "idiom": "ipad", "size": "20x20", "scale": "2x", "px": 40},
    {"name": "icon-29@1x.png", "idiom": "ipad", "size": "29x29", "scale": "1x", "px": 29},
    {"name": "icon-29@2x-ipad.png", "idiom": "ipad", "size": "29x29", "scale": "2x", "px": 58},
    {"name": "icon-40@1x.png", "idiom": "ipad", "size": "40x40", "scale": "1x", "px": 40},
    {"name": "icon-40@2x-ipad.png", "idiom": "ipad", "size": "40x40", "scale": "2x", "px": 80},
    {"name": "icon-76@1x.png", "idiom": "ipad", "size": "76x76", "scale": "1x", "px": 76},
    {"name": "icon-76@2x.png", "idiom": "ipad", "size": "76x76", "scale": "2x", "px": 152},
    {"name": "icon-83.5@2x.png", "idiom": "ipad", "size": "83.5x83.5", "scale": "2x", "px": 167},
    # App Store / Universal (iOS 16+)
    {"name": "icon-1024.png", "idiom": "ios-marketing", "size": "1024x1024", "scale": "1x", "px": 1024},
    {"name": "icon-1024.png", "idiom": "universal", "platform": "ios", "size": "1024x1024", "px": 1024},
]

def generate():
    if not os.path.exists(CONCEPT_PATH):
        print(f"Erro: Imagem da Kenshi não encontrada em {CONCEPT_PATH}")
        return False

    os.makedirs(APPICONSET_DIR, exist_ok=True)

    print("-> Carregando arte conceitual de alta resolução da Kenshi...")
    concept = Image.open(CONCEPT_PATH).convert("RGB")

    # Enquadramento exato da Kenshi (retrato oficial)
    crop = concept.crop((157, 16, 157 + 586, 16 + 586))

    # Salva imagem base em 1024x1024
    master_icon = crop.resize((1024, 1024), Image.Resampling.LANCZOS)
    master_path = os.path.join(APPICONSET_DIR, "icon-1024.png")
    master_icon.save(master_path, "PNG")

    # Também atualiza icon.png legado do kivy-ios
    kivy_icon_path = os.path.join(IOS_PROJECT_DIR, "icon.png")
    if os.path.exists(IOS_PROJECT_DIR):
        crop.resize((512, 512), Image.Resampling.LANCZOS).save(kivy_icon_path, "PNG")

    images_metadata = []
    generated_names = set()

    for spec in ICON_SPECS:
        fname = spec["name"]
        px = spec["px"]

        if fname not in generated_names:
            resized = master_icon.resize((px, px), Image.Resampling.LANCZOS)
            resized.save(os.path.join(APPICONSET_DIR, fname), "PNG")
            generated_names.add(fname)

        entry = {
            "filename": fname,
            "idiom": spec["idiom"],
            "size": spec["size"],
        }
        if "scale" in spec:
            entry["scale"] = spec["scale"]
        if "platform" in spec:
            entry["platform"] = spec["platform"]

        images_metadata.append(entry)

    contents = {
        "images": images_metadata,
        "info": {
            "author": "xcode",
            "version": 1
        }
    }

    contents_json_path = os.path.join(APPICONSET_DIR, "Contents.json")
    with open(contents_json_path, "w", encoding="utf-8") as f:
        json.dump(contents, f, indent=2)

    print(f"✓ Ícones da Kenshi instalados com sucesso em:\n  {APPICONSET_DIR}")
    return True

if __name__ == "__main__":
    generate()
