"""
Gera capturas das novas arenas do Ciclo 3 (Arrozais e Moinho na Chuva) com os guerreiros Goro e Ichi,
mais os revamps de Ganryu e Iga para a pasta docs/screenshots/.
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1280, 720))

from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ARENA_RICE_PADDIES, ARENA_RAIN_MILL, ARENA_GANRYU, ARENA_IGA,
    CHAR_GORO, CHAR_ICHI, CHAR_SAITOU, CHAR_MUSASHI, CHAR_NINJA,
)
from src.isometric.camera import Camera
from src.world.arenas import create_arena
from main import create_fighter
from src.ui.fonts import get_title_font, get_text_font

OUT_DIR = os.path.join(ROOT, "docs", "screenshots")


def _build_render_queue(arena):
    queue = []
    for bamboo in getattr(arena, "bamboos", []):
        queue.append((bamboo.wx + bamboo.wy, "bamboo", bamboo))
    for rock in getattr(arena, "rocks", []):
        queue.append((rock.wx + rock.wy, "rock", rock))
    if getattr(arena, "well", None):
        queue.append((arena.well.wx + arena.well.wy, "well", arena.well))
    for tree in getattr(arena, "trees", []):
        queue.append((tree.wx + tree.wy, "tree", tree))
    for tg in getattr(arena, "torii_gates", []):
        queue.append((tg.wx + tg.wy, "torii", tg))
    for b in getattr(arena, "buildings", []):
        queue.append((b.wx + b.wy + getattr(b, "depth", 0.5) * 0.5, "building", b))
    for l in getattr(arena, "lanterns", []):
        queue.append((l.wx + l.wy, "lantern", l))
    return queue


def _render_arena_scene(arena_id: str, f1=None, f2=None, title: str = "", subtitle: str = "") -> pygame.Surface:
    arena = create_arena(arena_id)
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill(arena.bg_color)
    cam = Camera(11.0, 11.0)
    arena.attach_camera(cam)

    arena.render_terrain(surf, cam, 2.5)

    fighters = [f for f in (f1, f2) if f is not None]
    queue = []
    for _, kind, obj in _build_render_queue(arena):
        wx = getattr(obj, "wx", 11.0)
        wy = getattr(obj, "wy", 11.0)
        queue.append((cam.depth(wx, wy), kind, obj))

    for f in fighters:
        queue.append((cam.depth(f.wx, f.wy), "fighter", f))

    queue.sort(key=lambda item: item[0])
    for _, kind, obj in queue:
        if kind == "fighter":
            obj.render(surf, cam)
        elif kind in ("bamboo", "building", "lantern") or getattr(obj, "animated", False):
            try:
                obj.render(surf, cam, 2.5)
            except TypeError:
                obj.render(surf, cam)
        else:
            try:
                obj.render(surf, cam)
            except TypeError:
                obj.render(surf, cam, 2.5)

    arena.render_overhead(surf, cam, 2.5)

    # Banner superior estilizado
    banner = pygame.Surface((SCREEN_WIDTH, 70), pygame.SRCALPHA)
    banner.fill((10, 12, 16, 210))
    surf.blit(banner, (0, 0))
    pygame.draw.line(surf, (212, 175, 55), (0, 70), (SCREEN_WIDTH, 70), 2)

    title_font = get_title_font(28)
    sub_font = get_text_font(18)
    t_surf = title_font.render(title, True, (255, 235, 180))
    s_surf = sub_font.render(subtitle, True, (180, 195, 210))
    surf.blit(t_surf, (28, 12))
    surf.blit(s_surf, (28, 42))

    return surf


def generate_previews():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1. Rice Paddies: Goro vs Saitou
    goro = create_fighter(CHAR_GORO, 9.5, 10.5)
    goro.facing_x = 1.0
    goro.facing_y = 0.0
    saitou = create_fighter(CHAR_SAITOU, 12.5, 10.5)
    saitou.facing_x = -1.0
    saitou.facing_y = 0.0
    surf_paddies = _render_arena_scene(
        ARENA_RICE_PADDIES, goro, saitou,
        "TERRAÇOS DE ARROZ (RICE PADDIES) — GORO",
        "Pântanos de lama, fardos de feno, espantalhos e iluminação crepuscular terrosa"
    )
    p_path = os.path.join(OUT_DIR, "arena_rice_paddies_preview.png")
    pygame.image.save(surf_paddies, p_path)
    print("Salvo:", p_path)

    # 2. Rain Mill: Ichi vs Musashi
    ichi = create_fighter(CHAR_ICHI, 8.5, 11.0)
    ichi.facing_x = 1.0
    ichi.facing_y = 0.0
    musashi = create_fighter(CHAR_MUSASHI, 12.5, 11.0)
    musashi.facing_x = -1.0
    musashi.facing_y = 0.0
    surf_mill = _render_arena_scene(
        ARENA_RAIN_MILL, ichi, musashi,
        "MOINHO NA CHUVA (RAIN MILL) — ICHI",
        "Ponte de madeira sobre riacho caudaloso, roda d'água monumental e chuva torrencial"
    )
    m_path = os.path.join(OUT_DIR, "arena_rain_mill_preview.png")
    pygame.image.save(surf_mill, m_path)
    print("Salvo:", m_path)

    # 3. Gojo Bridge: Benkei vs Kenshin
    from src.config import ARENA_GOJO_BRIDGE, CHAR_BENKEI, CHAR_KENSHIN
    benkei = create_fighter(CHAR_BENKEI, 8.5, 10.5)
    benkei.facing_x = 1.0
    benkei.facing_y = 0.0
    kenshin = create_fighter(CHAR_KENSHIN, 12.5, 10.5)
    kenshin.facing_x = -1.0
    kenshin.facing_y = 0.0
    surf_gojo = _render_arena_scene(
        ARENA_GOJO_BRIDGE, benkei, kenshin,
        "PONTE GOJO (REVAMP HISTÓRICO) — BENKEI",
        "Balustrada com corrimão clássico e giboshi, kagaribis crepitantes e as 999 lâminas cravadas"
    )
    g_path = os.path.join(OUT_DIR, "arena_gojo_bridge_preview.png")
    pygame.image.save(surf_gojo, g_path)
    print("Salvo:", g_path)

    # 4. Showcase 2x2 com Rice Paddies, Rain Mill, Gojo Bridge e Ganryu
    showcase = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    half_w = SCREEN_WIDTH // 2
    half_h = SCREEN_HEIGHT // 2

    ganryu_surf = _render_arena_scene(
        ARENA_GANRYU, create_fighter(CHAR_MUSASHI, 10.0, 11.0), create_fighter(CHAR_SAITOU, 13.0, 11.0),
        "ILHA DE GANRYŪ (REVAMP)", "Dunas com capim costeiro e bruma densa oceânica"
    )
    iga_surf = _render_arena_scene(
        ARENA_IGA, create_fighter(CHAR_NINJA, 9.0, 11.0), create_fighter(CHAR_ICHI, 13.0, 11.0),
        "TELHADOS DE IGA (REVAMP)", "Névoa noturna volumétrica e cumeeiras de alto contraste"
    )

    showcase.blit(pygame.transform.smoothscale(surf_paddies, (half_w, half_h)), (0, 0))
    showcase.blit(pygame.transform.smoothscale(surf_mill, (half_w, half_h)), (half_w, 0))
    showcase.blit(pygame.transform.smoothscale(ganryu_surf, (half_w, half_h)), (0, half_h))
    showcase.blit(pygame.transform.smoothscale(iga_surf, (half_w, half_h)), (half_w, half_h))

    # Divisórias douradas
    pygame.draw.line(showcase, (212, 175, 55), (half_w, 0), (half_w, SCREEN_HEIGHT), 3)
    pygame.draw.line(showcase, (212, 175, 55), (0, half_h), (SCREEN_WIDTH, half_h), 3)

    s_path = os.path.join(OUT_DIR, "cycle3_arenas_showcase.png")
    pygame.image.save(showcase, s_path)
    print("Salvo:", s_path)


if __name__ == "__main__":
    generate_previews()
