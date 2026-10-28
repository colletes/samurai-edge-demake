"""
Cache de Superfícies Estáticas de Arena e Props Voxel (Fase M-1 / Pilar 1).

Elimina o gargalo de CPU de recalcular projeções 3D e texturas procedurais de milhares
de faces de voxels estáticos a cada frame quando `camera.azimuth == 0.0`.
- `PropSurfaceCache`: pré-renderiza rochas, árvores, poços, torii, construções sólidas
  e bambus em superfícies recortadas (`SRCALPHA`) indexadas por `(prop_id, zoom_bucket, quality, state)`.
  Como a projeção isométrica com `azimuth == 0` é linear, o blit usa `camera.apply(obj.wx, obj.wy, 0.0)`
  como âncora exata, funcionando perfeitamente mesmo durante pan e screen shake.
- `TerrainSurfaceCache`: cacheia a camada de tiles estáticos (`flat` e `slab`) da arena
  quando o zoom está estabilizado e `azimuth == 0.0`.
"""
from __future__ import annotations

import math
from collections import OrderedDict
import pygame
from src.effects import quality
from src.isometric.iso_math import world_to_iso


class _BakingCamera:
    """Câmera virtual centrada na origem local do prop/terreno para pré-renderização."""

    def __init__(self, ref_wx: float, ref_wy: float, screen_x: int, screen_y: int, zoom: float):
        self.wx = ref_wx
        self.wy = ref_wy
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.zoom = zoom
        self.azimuth = 0.0
        self.ground_z = 0.0
        self.height_fn = None
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
        self.min_x = screen_x
        self.max_x = screen_x
        self.min_y = screen_y
        self.max_y = screen_y

    def apply(self, wx: float, wy: float, wz: float = 0.0) -> tuple[int, int]:
        iso_x, iso_y = world_to_iso(wx - self.wx, wy - self.wy, wz, 0.0)
        fx = int(iso_x * self.zoom + self.screen_x)
        fy = int(iso_y * self.zoom + self.screen_y)
        if fx < self.min_x:
            self.min_x = fx
        if fx > self.max_x:
            self.max_x = fx
        if fy < self.min_y:
            self.min_y = fy
        if fy > self.max_y:
            self.max_y = fy
        return fx, fy


class PropSurfaceCache:
    """Cache LRU de superfícies pré-renderizadas para props voxel do cenário."""

    MAX_ENTRIES = 1000
    # Durante transições de zoom os props são assados em buckets grossos e escalados no blit,
    # evitando um re-bake por frame (causa do travamento ao dar zoom).
    ZOOM_BUCKET_MOVING = 0.1
    SCRATCH_W = 1024
    SCRATCH_H = 1024
    ANCHOR_X = 512
    ANCHOR_Y = 740

    def __init__(self):
        self._cache: OrderedDict[tuple, tuple[pygame.Surface, int, int]] = OrderedDict()
        self._scratch: pygame.Surface | None = None
        self._last_dirty_rect: pygame.Rect | None = None
        self.hits = 0
        self.misses = 0

    def clear(self):
        self._cache.clear()
        self.hits = 0
        self.misses = 0

    def _get_scratch(self) -> pygame.Surface:
        if self._scratch is None:
            self._scratch = pygame.Surface((self.SCRATCH_W, self.SCRATCH_H), pygame.SRCALPHA)
            self._scratch.fill((0, 0, 0, 0))
        elif self._last_dirty_rect is not None:
            # Limpa só a região usada no último bake em vez de 1024x1024 px inteiros
            self._scratch.fill((0, 0, 0, 0), self._last_dirty_rect.inflate(160, 120))
            self._last_dirty_rect = None
        else:
            self._scratch.fill((0, 0, 0, 0))
        return self._scratch

    @staticmethod
    def can_cache_prop(item_type: str, obj, camera) -> bool:
        """Verifica se o objeto pode usar o cache estático no frame atual."""
        if abs(getattr(camera, "azimuth", 0.0)) > 1e-6:
            return False
        if getattr(camera, "height_fn", None) is not None:
            return False
        if getattr(obj, "animated", False):
            return False
        if item_type in ("rock", "well", "tree", "torii"):
            return True
        if item_type == "bamboo":
            # Bambus com impulso de vento de combate ativo são desenhados ao vivo
            if abs(getattr(obj, "combat_bend_x", 0.0)) > 0.005 or abs(getattr(obj, "combat_bend_y", 0.0)) > 0.005:
                return False
            return True
        if item_type == "building":
            cls_name = type(obj).__name__
            # SolidProp puro é 100% estático; Cannon, PowderBarrel, ShrineBell e MachiyaFacade em chamas animam
            if cls_name == "SolidProp":
                return True
        return False

    @staticmethod
    def _prop_state_key(item_type: str, obj, time_val: float):
        if item_type == "bamboo":
            if getattr(obj, "is_cut", False):
                return ("cut", round(getattr(obj, "stump_height", 0.5), 2))
            # Quantizar a fase de oscilação do vento em 16 estados suaves
            sway = math.sin(time_val * 2.0 + getattr(obj, "wind_offset", 0.0))
            return ("stand", int(round(sway * 7.0)))
        if hasattr(obj, "is_broken"):
            return ("broken" if obj.is_broken else "intact",)
        return ("static",)

    def render_prop(self, surface: pygame.Surface, camera, item_type: str, obj, time_val: float = 0.0) -> bool:
        """
        Tenta desenhar o prop a partir do cache. Retorna True se desenhou via cache,
        ou False se o chamador deve renderizar normalmente.
        """
        if not self.can_cache_prop(item_type, obj, camera):
            return False

        zoom_now = camera.zoom
        zooming = abs(getattr(camera, "target_zoom", zoom_now) - zoom_now) > 1e-6
        if zooming:
            zoom_q = round(zoom_now / self.ZOOM_BUCKET_MOVING) * self.ZOOM_BUCKET_MOVING
            scale = zoom_now / zoom_q if zoom_q > 0 else 1.0
            # Sem balanço de vento durante o zoom: um único estado por bucket mantém o cache pequeno
            state_key = ("cut", round(getattr(obj, "stump_height", 0.5), 2)) if (
                item_type == "bamboo" and getattr(obj, "is_cut", False)) else (
                ("stand", 0) if item_type == "bamboo" else self._prop_state_key(item_type, obj, time_val))
        else:
            zoom_q = round(zoom_now * 40.0) / 40.0
            scale = 1.0
            state_key = self._prop_state_key(item_type, obj, time_val)
        qual = quality.get_effects_quality()
        key = (id(obj), round(zoom_q, 4), qual, state_key)

        entry = self._cache.get(key)
        if entry is not None:
            self._cache.move_to_end(key)
            self.hits += 1
            baked_surf, off_x, off_y = entry
            bx, by = camera.apply(obj.wx, obj.wy, 0.0)
            if zooming and abs(scale - 1.0) > 1e-3:
                sw = max(1, int(baked_surf.get_width() * scale))
                sh = max(1, int(baked_surf.get_height() * scale))
                surface.blit(pygame.transform.scale(baked_surf, (sw, sh)), (bx + int(off_x * scale), by + int(off_y * scale)))
            else:
                surface.blit(baked_surf, (bx + off_x, by + off_y))
            return True

        self.misses += 1
        scratch = self._get_scratch()
        bake_cam = _BakingCamera(obj.wx, obj.wy, self.ANCHOR_X, self.ANCHOR_Y, zoom_q)

        if item_type in ("bamboo", "building", "lantern"):
            obj.render(scratch, bake_cam, time_val)
        else:
            obj.render(scratch, bake_cam)

        # Margem para sombras de base (elipses) e contornos
        pad_x = int(72 * zoom_q) + 8
        pad_y = int(42 * zoom_q) + 8
        x0 = max(0, bake_cam.min_x - pad_x)
        y0 = max(0, bake_cam.min_y - pad_y)
        x1 = min(self.SCRATCH_W, bake_cam.max_x + pad_x)
        y1 = min(self.SCRATCH_H, bake_cam.max_y + pad_y)

        if x1 <= x0 or y1 <= y0:
            self._scratch = None
            self._last_dirty_rect = None
            return False

        dirty_rect = pygame.Rect(x0, y0, x1 - x0, y1 - y0)
        self._last_dirty_rect = dirty_rect

        baked_surf = pygame.Surface(dirty_rect.size, pygame.SRCALPHA)
        baked_surf.fill((0, 0, 0, 0))
        baked_surf.blit(scratch, (0, 0), dirty_rect)
        off_x = x0 - self.ANCHOR_X
        off_y = y0 - self.ANCHOR_Y

        if len(self._cache) >= self.MAX_ENTRIES:
            self._cache.popitem(last=False)
        self._cache[key] = (baked_surf, off_x, off_y)

        bx, by = camera.apply(obj.wx, obj.wy, 0.0)
        if zooming and abs(scale - 1.0) > 1e-3:
            sw = max(1, int(baked_surf.get_width() * scale))
            sh = max(1, int(baked_surf.get_height() * scale))
            surface.blit(pygame.transform.scale(baked_surf, (sw, sh)), (bx + int(off_x * scale), by + int(off_y * scale)))
        else:
            surface.blit(baked_surf, (bx + off_x, by + off_y))
        return True


class TerrainSurfaceCache:
    """
    Cacheia a camada estática de terreno (`flat`, `slab` e buracos secos) de uma `ArenaMap`
    quando `azimuth == 0.0` e `height_fn is None`.
    """

    MAX_ZOOM_BUCKETS = 12
    ZOOM_BUCKET_MOVING = 0.1

    def __init__(self):
        self._cache: OrderedDict[tuple, tuple[pygame.Surface, int, int]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def clear(self):
        self._cache.clear()
        self.hits = 0
        self.misses = 0

    def render_static_terrain(self, arena_map, surface: pygame.Surface, camera) -> tuple[bool, set[int]]:
        """
        Desenha todos os tiles `flat`, `slab` e `pits` sem água a partir de uma única superfície cacheada.
        Retorna `( True, visible_anchors )` se usou o cache, ou `( False, set() )` caso contrário.
        """
        if abs(getattr(camera, "azimuth", 0.0)) > 1e-6 or getattr(camera, "height_fn", None) is not None:
            return False, set()

        zoom_exact = round(camera.zoom, 3)
        qual = quality.get_effects_quality()
        zooming = abs(getattr(camera, "target_zoom", camera.zoom) - camera.zoom) > 1e-6
        if zooming and (arena_map.arena_id, id(arena_map), zoom_exact, qual) not in self._cache:
            return self._render_zooming(arena_map, surface, camera, qual)
        key = (arena_map.arena_id, id(arena_map), zoom_exact, qual)

        entry = self._cache.get(key)
        if entry is None:
            self.misses += 1
            entry = self._bake_terrain(arena_map, zoom_exact)
            if len(self._cache) >= self.MAX_ZOOM_BUCKETS:
                self._cache.popitem(last=False)
            self._cache[key] = entry
        else:
            self._cache.move_to_end(key)
            self.hits += 1

        baked_surf, ref_x, ref_y, all_anchors = entry
        ox, oy = camera.apply(0.0, 0.0, 0.0)
        surface.blit(baked_surf, (ox - ref_x, oy - ref_y))
        return True, all_anchors

    def _render_zooming(self, arena_map, surface: pygame.Surface, camera, qual) -> tuple[bool, set[int]]:
        """Durante o zoom reaproveita um bake de bucket grosso e escala só a parte visível (sem re-bake por frame)."""
        zb = round(camera.zoom / self.ZOOM_BUCKET_MOVING) * self.ZOOM_BUCKET_MOVING
        zb = round(max(zb, self.ZOOM_BUCKET_MOVING), 3)
        key = (arena_map.arena_id, id(arena_map), zb, qual)
        entry = self._cache.get(key)
        if entry is None:
            self.misses += 1
            entry = self._bake_terrain(arena_map, zb)
            if len(self._cache) >= self.MAX_ZOOM_BUCKETS:
                self._cache.popitem(last=False)
            self._cache[key] = entry
        else:
            self._cache.move_to_end(key)
            self.hits += 1
        baked_surf, ref_x, ref_y, all_anchors = entry
        s = camera.zoom / zb
        ox, oy = camera.apply(0.0, 0.0, 0.0)
        sw, sh = surface.get_size()
        # Retângulo de origem (em px do bake) que cobre a tela inteira
        src = pygame.Rect(int(ref_x - ox / s) - 1, int(ref_y - oy / s) - 1, int(sw / s) + 3, int(sh / s) + 3)
        src = src.clip(baked_surf.get_rect())
        if src.w > 0 and src.h > 0:
            dx = ox + (src.x - ref_x) * s
            dy = oy + (src.y - ref_y) * s
            dw, dh = max(1, round(src.w * s)), max(1, round(src.h * s))
            surface.blit(pygame.transform.scale(baked_surf.subsurface(src), (dw, dh)), (round(dx), round(dy)))
        return True, all_anchors

    @staticmethod
    def _bake_terrain(arena_map, zoom: float):
        cols, rows = arena_map.cols, arena_map.rows
        # Calcular bounding box em pixels para todos os cantos do mapa
        corners = [
            world_to_iso(0, 0, 0.0, 0.0),
            world_to_iso(cols, 0, 0.0, 0.0),
            world_to_iso(cols, rows, -2.0, 0.0),
            world_to_iso(0, rows, 0.0, 0.0),
        ]
        xs = [int(c[0] * zoom) for c in corners]
        ys = [int(c[1] * zoom) for c in corners]
        pad = int(96 * zoom) + 24
        min_x, max_x = min(xs) - pad, max(xs) + pad
        min_y, max_y = min(ys) - pad, max(ys) + pad

        w = max(64, max_x - min_x)
        h = max(64, max_y - min_y)
        ref_x = -min_x
        ref_y = -min_y

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        bake_cam = _BakingCamera(0.0, 0.0, ref_x, ref_y, zoom)
        anchors: set[int] = set()

        for x in range(cols):
            for y in range(rows):
                tile = arena_map.tiles[x][y]
                style = arena_map.styles[tile]
                if style.kind == "flat":
                    quad = [
                        bake_cam.apply(x, y, 0.0),
                        bake_cam.apply(x + 1, y, 0.0),
                        bake_cam.apply(x + 1, y + 1, 0.0),
                        bake_cam.apply(x, y + 1, 0.0),
                    ]
                    arena_map._draw_flat(surf, bake_cam, style, x, y, quad)
                elif style.kind == "slab":
                    arena_map._draw_slab(surf, bake_cam, style, x, y)
                elif style.kind == "anchor":
                    anchors.add(tile)

        for pit in arena_map.pits:
            if pit.water is None:
                arena_map._draw_pit(surf, bake_cam, pit, 0.0)

        return surf, ref_x, ref_y, anchors


# Instâncias singleton globais reutilizadas pelo jogo
_PROP_CACHE = PropSurfaceCache()
_TERRAIN_CACHE = TerrainSurfaceCache()


def get_prop_cache() -> PropSurfaceCache:
    return _PROP_CACHE


def get_terrain_cache() -> TerrainSurfaceCache:
    return _TERRAIN_CACHE


def clear_arena_caches():
    _PROP_CACHE.clear()
    _TERRAIN_CACHE.clear()
