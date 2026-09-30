"""
tools/generate_sprite_atlas.py
Gera as Spritesheets Mestras e os Metadados em JSON (Atlas) para Kenshi e Murasaki,
além de um Mapa Visual Consolidado com todas as animações (Idle, Walk em todas as 4 direções, Ataque e Reações).
"""
import os
import json
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

def build_character_atlas(char_name, sprite_dir, out_dir):
    pygame.init()
    pygame.display.set_mode((1, 1))

    # Definição das trilhas de animação
    animations = {
        "idle_front": {
            "fps": 4.5,
            "loop": True,
            "frames": [f"front_idle_{i}" for i in range(4)]
        },
        "idle_back": {
            "fps": 4.5,
            "loop": True,
            "frames": [f"back_idle_{i}" for i in range(4)]
        },
        "walk_se": {
            "fps": 8.0,
            "loop": True,
            "direction": "front_right",
            "frames": [f"front_walk_{i}" for i in range(4)]
        },
        "walk_sw": {
            "fps": 8.0,
            "loop": True,
            "direction": "front_left",
            "flip_x": True,
            "frames": [f"front_walk_{i}" for i in range(4)]
        },
        "walk_ne": {
            "fps": 8.0,
            "loop": True,
            "direction": "back_right",
            "frames": [f"back_walk_{i}" for i in range(4)]
        },
        "walk_nw": {
            "fps": 8.0,
            "loop": True,
            "direction": "back_left",
            "flip_x": True,
            "frames": [f"back_walk_{i}" for i in range(4)]
        },
        "combat": {
            "fps": 10.0,
            "loop": False,
            "frames": ["front_attack", "back_attack", "recovery", "stunned", "dead"]
        }
    }

    # Carregar todas as superfícies
    loaded_frames = {}
    for anim_id, anim_data in animations.items():
        is_flip = anim_data.get("flip_x", False)
        for fr_name in anim_data["frames"]:
            key = f"{fr_name}_flip" if is_flip else fr_name
            if key not in loaded_frames:
                path = os.path.join(sprite_dir, f"{fr_name}.png")
                if os.path.exists(path):
                    surf = pygame.image.load(path).convert_alpha()
                    if is_flip:
                        surf = pygame.transform.flip(surf, True, False)
                    loaded_frames[key] = surf
                else:
                    print(f"[Aviso] Frame ausente: {path}")

    # Layout da Spritesheet Mestra em Grade
    # Célula padrão: 64x80 (com margens para respirar)
    CELL_W = 64
    CELL_H = 84
    FOOT_BASELINE_Y = 76 # Linha de chão padrão dentro da célula

    ROWS = [
        ("idle_front", "Idle Frente (SE)", [f"front_idle_{i}" for i in range(4)]),
        ("idle_back", "Idle Costas (NE)", [f"back_idle_{i}" for i in range(4)]),
        ("walk_se", "Walk Frente-Dir (SE)", [f"front_walk_{i}" for i in range(4)]),
        ("walk_sw", "Walk Frente-Esq (SW)", [f"front_walk_{i}_flip" for i in range(4)]),
        ("walk_ne", "Walk Costas-Dir (NE)", [f"back_walk_{i}" for i in range(4)]),
        ("walk_nw", "Walk Costas-Esq (NW)", [f"back_walk_{i}_flip" for i in range(4)]),
        ("combat", "Ataque & Reações", ["front_attack", "back_attack", "recovery", "stunned", "dead"])
    ]

    max_cols = max(len(row[2]) for row in ROWS)
    sheet_w = max_cols * CELL_W
    sheet_h = len(ROWS) * CELL_H

    sheet_surf = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet_surf.fill((0, 0, 0, 0))

    atlas_data = {
        "character": char_name,
        "sheet_width": sheet_w,
        "sheet_height": sheet_h,
        "cell_width": CELL_W,
        "cell_height": CELL_H,
        "foot_baseline_y": FOOT_BASELINE_Y,
        "animations": {},
        "frames": {}
    }

    for row_idx, (anim_id, label, frame_keys) in enumerate(ROWS):
        anim_entry = {
            "label": label,
            "fps": animations[anim_id]["fps"],
            "loop": animations[anim_id]["loop"],
            "frames": []
        }

        for col_idx, fr_key in enumerate(frame_keys):
            if fr_key in loaded_frames:
                surf = loaded_frames[fr_key]
                sw, sh = surf.get_size()

                # Ancoragem pelos pés no baseline
                dest_x = col_idx * CELL_W + (CELL_W - sw) // 2
                dest_y = row_idx * CELL_H + (FOOT_BASELINE_Y - sh)

                sheet_surf.blit(surf, (dest_x, dest_y))

                rect = [dest_x, dest_y, sw, sh]
                atlas_data["frames"][fr_key] = {
                    "rect": rect,
                    "anchor_x": sw // 2,
                    "anchor_y": sh,
                    "row": row_idx,
                    "col": col_idx
                }
                anim_entry["frames"].append(fr_key)

        atlas_data["animations"][anim_id] = anim_entry

    # Salva a spritesheet PNG e o JSON
    sheet_path = os.path.join(out_dir, f"{char_name}_sprite_sheet.png")
    json_path = os.path.join(out_dir, f"{char_name}_atlas.json")

    pygame.image.save(sheet_surf, sheet_path)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(atlas_data, f, indent=2, ensure_ascii=False)

    print(f"[OK] {char_name.capitalize()} Atlas salvo:")
    print(f"     Spritesheet: {sheet_path} ({sheet_w}x{sheet_h})")
    print(f"     Metadados:   {json_path}")
    return sheet_path, json_path, atlas_data

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sprites_dir = os.path.join(base_dir, "assets", "sprites")

    for c in ["kenshi", "murasaki"]:
        c_dir = os.path.join(sprites_dir, c)
        build_character_atlas(c, c_dir, c_dir)
