"""
Captura preview de gameplay entre Valerius (Necromante) e Seimei (Onmyoji) na arena.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
pygame.init()
pygame.font.init()

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG
from src.isometric.camera import Camera
from src.world.arenas import create_arena
from src.entities.valerius import ValeriusNecromancer, SkeletonSummon
from src.entities.seimei import SeimeiOnmyoji
from src.entities.projectile import OfudaProjectile, TalismanWard
from src.effects.particles import SparkParticle, FloatingBanner


def capture_cycle4_gameplay():
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    font_large = pygame.font.Font(None, 40)
    font_mid = pygame.font.Font(None, 24)

    arena = create_arena("bamboo")
    camera = arena.attach_camera(Camera(target_wx=11.1, target_wy=11.1))
    camera.zoom = 2.5

    # Lutadores no tabuado da ponte
    p1 = ValeriusNecromancer(9.8, 11.0)
    p2 = SeimeiOnmyoji(12.2, 11.0)
    p1.set_facing(p2.wx, p2.wy)
    p2.set_facing(p1.wx, p1.wy)

    # Ações ativas: Valerius invocou um esqueleto e desfere Ceifada; Seimei lançou Ofuda e armou Selo Sagrado
    p1.state = "ATTACK"
    p1.state_timer = 0.10
    p1.hitbox_active = True
    p1.hitbox_center = (10.8, 11.0)
    p1.hitbox_radius = 1.35

    # Esqueleto invocado avançando na ponte
    p1.summon = SkeletonSummon(p1, 11.0, 11.0, opponent=p2)
    p1.summon.state = "CHASING"
    p1.summon.facing_x = 1.0

    # Ofuda cortante de Seimei no ar
    ofuda = OfudaProjectile(11.6, 11.0, 0.45, -1.0, 0.0, owner=p2)
    ward = TalismanWard(12.4, 11.3, owner=p2)

    projectiles = [ofuda, ward]
    particles = []
    banners = [
        FloatingBanner("SOUL REAP!", p1.wx, p1.wy, wz=1.9, color=(65, 230, 170), duration=5.0),
        FloatingBanner("OFUDA TOSS!", p2.wx, p2.wy, wz=1.9, color=(140, 200, 255), duration=5.0),
    ]

    # Render
    screen.fill(COLOR_BG)
    arena.render_terrain(screen, camera, 2.0)

    render_queue = []
    for b in getattr(arena, "bamboos", []):
        render_queue.append((camera.depth(b.wx, b.wy), 'bamboo', b))
    for r in getattr(arena, "rocks", []):
        render_queue.append((camera.depth(r.wx, r.wy), 'rock', r))

    render_queue.append((camera.depth(p1.wx, p1.wy), 'fighter', p1))
    render_queue.append((camera.depth(p2.wx, p2.wy), 'fighter', p2))

    if p1.summon and p1.summon.is_alive:
        render_queue.append((camera.depth(p1.summon.wx, p1.summon.wy), 'summon', p1.summon))

    for proj in projectiles:
        render_queue.append((camera.depth(proj.wx, proj.wy), 'projectile', proj))

    # Desenho ordenado
    render_queue.sort(key=lambda item: item[0])
    for _, itype, obj in render_queue:
        if itype == 'bamboo':
            obj.render(screen, camera, 2.0)
        elif hasattr(obj, "render"):
            obj.render(screen, camera)

    for banner in banners:
        banner.render(screen, camera, font_mid)

    # HUD Card Superior
    hud_surf = pygame.Surface((SCREEN_WIDTH, 44), pygame.SRCALPHA)
    hud_surf.fill((16, 16, 20, 220))
    pygame.draw.line(hud_surf, (212, 175, 55), (0, 42), (SCREEN_WIDTH, 42), 2)

    t1 = font_large.render("VALERIUS", True, (65, 230, 170))
    t2 = font_large.render("SEIMEI", True, (140, 200, 255))
    vs = font_mid.render("CYCLE 4 — BATTLE PREVIEW", True, (212, 175, 55))
    hud_surf.blit(t1, (24, 8))
    hud_surf.blit(t2, (SCREEN_WIDTH - t2.get_width() - 24, 8))
    hud_surf.blit(vs, (SCREEN_WIDTH // 2 - vs.get_width() // 2, 12))

    screen.blit(hud_surf, (0, 0))

    out_path = os.path.join(ROOT, "docs", "screenshots", "cycle4_combat_preview.png")
    pygame.image.save(screen, out_path)
    print(f"Salvo preview em: {out_path}")


if __name__ == "__main__":
    capture_cycle4_gameplay()
