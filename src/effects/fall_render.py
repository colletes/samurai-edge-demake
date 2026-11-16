"""Desenho da queda em buracos: o lutador afunda, gira, encolhe e escurece, recortado ao contorno do buraco."""
import pygame

from src.entities.samurai import FALL_DURATION

_layers: dict[tuple[int, int], tuple[pygame.Surface, pygame.Surface, pygame.Surface]] = {}


def _surfaces(size: tuple[int, int]):
    """Camadas reutilizadas (corpo, corpo girado, máscara) para não alocar telas inteiras a cada quadro."""
    if size not in _layers:
        _layers[size] = tuple(pygame.Surface(size, pygame.SRCALPHA) for _ in range(3))
    return _layers[size]


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def render_falling_fighter(surface: pygame.Surface, fighter, camera):
    """Desenha o lutador em queda abissal (state FALL): tomba, despenca verticalmente no vazio com aceleração gravitacional e fade out sombrio."""
    pit = fighter.fall_pit
    if pit is None:
        return
    progress = max(0.0, min(1.0, fighter.fall_timer / FALL_DURATION))
    body, spun, mask = _surfaces(surface.get_size())

    body.fill((0, 0, 0, 0))
    fighter.render(body, camera)

    # Queda vertical real no abismo: wz acelera para o fundo do abismo
    wz_fall = max(-4.0, getattr(fighter, "wz", -0.5 * 24.0 * fighter.fall_timer * fighter.fall_timer))
    cx, cy = camera.apply(fighter.wx, fighter.wy, wz_fall + 0.4)
    half_w, up, down = 130, 190, 130
    crop = pygame.Rect(int(cx) - half_w, int(cy) - up, half_w * 2, up + down).clip(body.get_rect())
    spun.fill((0, 0, 0, 0))
    if crop.width > 0 and crop.height > 0:
        piece = body.subsurface(crop).copy()
        # Rotação dramática de desespero e encolhimento de profundidade
        zoom_factor = max(0.15, 1.0 - 0.75 * progress)
        piece = pygame.transform.rotozoom(piece, progress * 320.0, zoom_factor)
        pivot = (crop.centerx, crop.centery)
        spun.blit(piece, piece.get_rect(center=pivot))

    # Região visível = abertura do buraco estendida para cima (o que passou da borda da frente é encoberto)
    corners = [(pit.x0, pit.y0), (pit.x1, pit.y0), (pit.x1, pit.y1), (pit.x0, pit.y1)]
    outline = [camera.apply(x, y, 0.0) for x, y in corners] + [camera.apply(x, y, 3.0) for x, y in corners]
    mask.fill((0, 0, 0, 0))
    pygame.draw.polygon(mask, (255, 255, 255, 255), convex_hull(outline))
    spun.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Escurecimento sombrio do abismo com fade suave até o sumiço
    shade = int(255 * max(0.0, (1.0 - 0.90 * progress)))
    fade = int(255 * max(0.0, (1.0 - progress * progress)))
    spun.fill((shade, shade, shade, fade), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(spun, (0, 0))
