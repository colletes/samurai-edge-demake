"""
Desenho em lote de milhares de cubos pequenos (esqueleto do chefe): cada combinação de cor e tamanho vira um sprite
pré-renderizado para o azimute/zoom atuais, e cada cubo custa só uma projeção do centro e um blit.
"""
import math

import pygame

from src.config import HALF_TILE_W, HALF_TILE_H
from src.isometric.iso_math import PIXELS_PER_Z, world_to_iso
from src.isometric.voxel_renderer import draw_voxel_box

_OUTLINE_MIN_SIZE = 0.2  # abaixo disso o contorno de 1 px engoliria as faces


class _SpriteCamera:
    """Câmera mínima para desenhar um cubo centrado na origem dentro de uma superfície pequena."""

    def __init__(self, azimuth: float, zoom: float, ox: float, oy: float):
        self.azimuth, self.zoom, self.ox, self.oy = azimuth, zoom, ox, oy

    def apply(self, wx, wy, wz=0.0):
        sx, sy = world_to_iso(wx, wy, wz, self.azimuth)
        return sx * self.zoom + self.ox, sy * self.zoom + self.oy


_cache_key = None
_sprites: dict = {}


def _sprite(color, size: float, azimuth: float, zoom: float, alpha: int):
    h = size / 2.0
    pts = [world_to_iso(x, y, z, azimuth) for x in (-h, h) for y in (-h, h) for z in (-h, h)]
    min_x, max_x = min(p[0] for p in pts) * zoom, max(p[0] for p in pts) * zoom
    min_y, max_y = min(p[1] for p in pts) * zoom, max(p[1] for p in pts) * zoom
    ox, oy = 1.0 - min_x, 1.0 - min_y
    surf = pygame.Surface((int(max_x - min_x) + 3, int(max_y - min_y) + 3), pygame.SRCALPHA)
    draw_voxel_box(surf, _SpriteCamera(azimuth, zoom, ox, oy), -h, -h, -h, size, size, size, color,
                   outline=size >= _OUTLINE_MIN_SIZE)
    if alpha < 255:
        surf.set_alpha(alpha)
    return surf, int(ox), int(oy)


def draw_cubes(surface: pygame.Surface, camera, cubes, alpha: int = 255):
    """`cubes`: iterável de (x, y, z, tamanho, cor) com (x, y, z) no centro do cubo. Ordena por profundidade e desenha."""
    global _cache_key
    azimuth, zoom = getattr(camera, "azimuth", 0.0), getattr(camera, "zoom", 1.0)
    if _cache_key != (azimuth, zoom, alpha):
        _sprites.clear()
        _cache_key = (azimuth, zoom, alpha)
    cos_a, sin_a = math.cos(azimuth), math.sin(azimuth)
    k1, k2 = cos_a + sin_a, cos_a - sin_a  # profundidade = rx + ry
    ordered = sorted([(x * k1 + y * k2, z, x, y, size, color) for x, y, z, size, color in cubes])
    blit, sprites = surface.blit, _sprites
    if camera.height_fn is not None:
        apply = camera.apply
        for _, z, x, y, size, color in ordered:
            spr = sprites.get((color, size)) or sprites.setdefault((color, size), _sprite(color, size, azimuth, zoom, alpha))
            px, py = apply(x, y, z)
            blit(spr[0], (px - spr[1], py - spr[2]))
        return
    cam_x, cam_y = camera.wx, camera.wy
    off_x = camera.screen_x + camera.shake_offset_x
    off_y = camera.screen_y + camera.shake_offset_y
    sx_k, sy_k, z_k = HALF_TILE_W * zoom, HALF_TILE_H * zoom, PIXELS_PER_Z * zoom
    for _, z, x, y, size, color in ordered:
        spr = sprites.get((color, size))
        if spr is None:
            spr = sprites[(color, size)] = _sprite(color, size, azimuth, zoom, alpha)
        dx, dy = x - cam_x, y - cam_y
        rx, ry = dx * cos_a - dy * sin_a, dx * sin_a + dy * cos_a
        blit(spr[0], (int((rx - ry) * sx_k + off_x) - spr[1], int((rx + ry) * sy_k - z * z_k + off_y) - spr[2]))
