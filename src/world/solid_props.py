"""Props sólidos genéricos (retângulo com colisão) para as arenas temáticas: barco, dojo, paliçadas, caixas."""
import math
import random

import pygame

from src.isometric.voxel_renderer import draw_voxel_box


def aabb_circle_collision(rect: tuple[float, float, float, float], px: float, py: float, radius: float) -> tuple[bool, float, float]:
    """Círculo (lutador) contra retângulo (min_x, min_y, max_x, max_y); devolve (colidiu, push_x, push_y)."""
    min_x, min_y, max_x, max_y = rect
    closest_x = max(min_x, min(px, max_x))
    closest_y = max(min_y, min(py, max_y))
    dx = px - closest_x
    dy = py - closest_y
    dist = math.hypot(dx, dy)
    if dist >= radius:
        return False, 0.0, 0.0
    if dist > 0.0001:
        overlap = radius - dist
        return True, dx / dist * overlap, dy / dist * overlap
    # Centro dentro do retângulo: empurra pelo eixo de menor penetração
    pens = ((px - min_x, -1.0, 0.0), (max_x - px, 1.0, 0.0), (py - min_y, 0.0, -1.0), (max_y - py, 0.0, 1.0))
    pen, nx, ny = min(pens, key=lambda p: p[0])
    return True, nx * (pen + radius), ny * (pen + radius)


class SolidProp:
    """
    Obstáculo retangular alinhado aos eixos (`wx`, `wy` = canto mínimo). Entra na coleção `buildings` do mapa,
    então já bloqueia lutadores (andar e esquiva) e é ordenado junto com os demais itens estáticos.
    `style`: "block" (caixa simples), "boat" (barco encalhado com remo), "mast" (mastro com vergas) ou
    "barrel" (barril com aros), "dojo" (dojo de telhado de telha), "guardpost" (posto de guarda do Shinsengumi) ou "pillar" (coluna de pedra), "cabin" (cabana de palha), "tent" (barraca de lona) ou "palisade" (paliçada de estacas) ou "bell" (pavilhão do sino).
    """

    def __init__(self, wx: float, wy: float, width: float, depth: float, height: float = 0.6,
                 color: tuple[int, int, int] = (96, 70, 48), style: str = "block"):
        self.wx = wx
        self.wy = wy
        self.width = width
        self.depth = depth
        self.height = height
        self.color = color
        self.style = style

    def check_collision(self, px: float, py: float, p_radius: float = 0.3) -> tuple[bool, float, float]:
        return aabb_circle_collision((self.wx, self.wy, self.wx + self.width, self.wy + self.depth), px, py, p_radius)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        if self.style == "boat":
            self._render_boat(surface, camera)
            return
        if self.style == "mast":
            self._render_mast(surface, camera)
            return
        if self.style == "barrel":
            self._render_barrel(surface, camera)
            return
        if self.style == "dojo":
            self._render_dojo(surface, camera)
            return
        if self.style == "guardpost":
            self._render_guardpost(surface, camera)
            return
        if self.style == "pillar":
            self._render_pillar(surface, camera)
            return
        if self.style == "cabin":
            self._render_cabin(surface, camera)
            return
        if self.style == "tent":
            self._render_tent(surface, camera)
            return
        if self.style == "palisade":
            self._render_palisade(surface, camera)
            return
        draw_voxel_box(surface, camera, self.wx, self.wy, 0.0, self.width, self.depth, self.height, self.color, outline=True, texture="planks")

    def _render_mast(self, surface: pygame.Surface, camera):
        """Mastro grosso com base reforçada e duas vergas cruzadas no alto."""
        x0, y0, w, d, h = self.wx, self.wy, self.width, self.depth, self.height
        dark = tuple(int(c * 0.7) for c in self.color)
        draw_voxel_box(surface, camera, x0 - 0.12, y0 - 0.12, 0.0, w + 0.24, d + 0.24, 0.30, dark, outline=True, texture="stone")
        draw_voxel_box(surface, camera, x0, y0, 0.0, w, d, h, self.color, outline=True, texture="planks")
        for z, span in ((h * 0.62, 2.4), (h * 0.88, 1.7)):
            draw_voxel_box(surface, camera, x0 + w / 2 - 0.05, y0 + d / 2 - span / 2, z, 0.10, span, 0.10, dark, outline=True)
        # Vela enrolada na verga baixa
        draw_voxel_box(surface, camera, x0 + w / 2 - 0.14, y0 + d / 2 - 0.95, h * 0.62 - 0.22, 0.28, 1.9, 0.22, (214, 204, 178), outline=True)

    @staticmethod
    def _hip_roof(surface, camera, x0, y0, w, d, z, color, layers=3, overhang=0.45, step=0.55, thick=0.17, texture=None):
        """Telhado de quatro águas feito de lajes empilhadas, cada uma mais recuada que a de baixo."""
        for i in range(layers):
            inset = i * step - overhang
            if w - 2 * inset <= 0.2 or d - 2 * inset <= 0.2:
                break
            shade = tuple(min(255, int(c * (1.0 + 0.07 * i))) for c in color)
            draw_voxel_box(surface, camera, x0 + inset, y0 + inset, z + i * thick, w - 2 * inset, d - 2 * inset, thick, shade, outline=True, texture=texture)

    def _render_dojo(self, surface: pygame.Surface, camera):
        """Dojo: fundação de pedra, paredes vermelho-madeira com shoji e telhado de telha escura."""
        x0, y0, w, d, h = self.wx, self.wy, self.width, self.depth, self.height
        wood, dark_wood, paper = (126, 54, 42), (70, 44, 30), (232, 222, 196)
        draw_voxel_box(surface, camera, x0, y0, 0.0, w, d, 0.25, (96, 94, 90), outline=True, texture="stone")
        draw_voxel_box(surface, camera, x0 + 0.3, y0 + 0.3, 0.25, w - 0.6, d - 0.6, h - 0.25, wood, outline=True, texture="planks")
        inner = 0.3
        for fx in (x0 + inner - 0.03, x0 + w - inner - 0.01):  # paredes de leste e oeste
            draw_voxel_box(surface, camera, fx, y0 + inner + 0.4, 0.55, 0.04, d - 2 * inner - 0.8, h - 0.9, paper, outline=False)
        for fy in (y0 + inner - 0.03, y0 + d - inner - 0.01):  # paredes de norte e sul
            draw_voxel_box(surface, camera, x0 + inner + 0.4, fy, 0.55, w - 2 * inner - 0.8, 0.04, h - 0.9, paper, outline=False)
        cols = max(2, int(w / 0.9))
        for i in range(cols + 1):
            px = x0 + inner + (w - 2 * inner - 0.14) * i / cols
            for py in (y0 + inner - 0.04, y0 + d - inner - 0.10):
                draw_voxel_box(surface, camera, px, py, 0.25, 0.14, 0.14, h - 0.25, dark_wood, outline=True)
        rows = max(2, int(d / 0.9))
        for i in range(rows + 1):
            py = y0 + inner + (d - 2 * inner - 0.14) * i / rows
            for px in (x0 + inner - 0.04, x0 + w - inner - 0.10):
                draw_voxel_box(surface, camera, px, py, 0.25, 0.14, 0.14, h - 0.25, dark_wood, outline=True)
        draw_voxel_box(surface, camera, x0 + 0.2, y0 + 0.2, h, w - 0.4, d - 0.4, 0.10, dark_wood, outline=True)
        self._hip_roof(surface, camera, x0, y0, w, d, h + 0.10, (60, 66, 82), layers=3, texture="roof_tile")
        draw_voxel_box(surface, camera, x0 + w * 0.5 - 0.9, y0 + d * 0.5 - 0.12, h + 0.10 + 3 * 0.17, 1.8, 0.24, 0.12, (96, 104, 124), outline=True)

    def _render_guardpost(self, surface: pygame.Surface, camera):
        """Posto de guarda do Shinsengumi: cabana de reboco com faixa azul-claro e branco e telhado baixo."""
        x0, y0, w, d, h = self.wx, self.wy, self.width, self.depth, self.height
        draw_voxel_box(surface, camera, x0, y0, 0.0, w, d, 0.16, (88, 86, 84), outline=True, texture="stone")
        draw_voxel_box(surface, camera, x0 + 0.1, y0 + 0.1, 0.16, w - 0.2, d - 0.2, h - 0.16, (216, 208, 190), outline=True, texture="plaster")
        stripes = 6
        for i in range(stripes):
            color = (132, 200, 224) if i % 2 == 0 else (240, 240, 246)
            sx = x0 + 0.1 + (w - 0.2) * i / stripes
            draw_voxel_box(surface, camera, sx, y0 + 0.07, h - 0.34, (w - 0.2) / stripes, 0.04, 0.22, color, outline=False)
            draw_voxel_box(surface, camera, sx, y0 + d - 0.11, h - 0.34, (w - 0.2) / stripes, 0.04, 0.22, color, outline=False)
        for i in range(max(2, int(d / 0.4))):
            color = (132, 200, 224) if i % 2 == 0 else (240, 240, 246)
            sy = y0 + 0.1 + (d - 0.2) * i / max(2, int(d / 0.4))
            draw_voxel_box(surface, camera, x0 + 0.07, sy, h - 0.34, 0.04, (d - 0.2) / max(2, int(d / 0.4)), 0.22, color, outline=False)
            draw_voxel_box(surface, camera, x0 + w - 0.11, sy, h - 0.34, 0.04, (d - 0.2) / max(2, int(d / 0.4)), 0.22, color, outline=False)
        draw_voxel_box(surface, camera, x0 + w * 0.5 - 0.2, y0 + 0.05, 0.16, 0.4, 0.04, 0.6, (60, 44, 32), outline=False)
        self._hip_roof(surface, camera, x0, y0, w, d, h, (56, 60, 74), layers=2, overhang=0.3, step=0.5, texture="roof_tile")

    def _render_cabin(self, surface: pygame.Surface, camera):
        """Cabana de aldeia: paredes de madeira, porta escura e telhado de palha."""
        x0, y0, w, d, h = self.wx, self.wy, self.width, self.depth, self.height
        gx, gy = camera.apply(x0 + w / 2, y0 + d / 2, 0.0)
        pygame.draw.ellipse(surface, (60, 96, 50), (gx - int(w * 18), gy - int(d * 8), int(w * 36), int(d * 16)))
        draw_voxel_box(surface, camera, x0, y0, 0.0, w, d, 0.2, (112, 108, 100), outline=True, texture="stone")
        draw_voxel_box(surface, camera, x0 + 0.1, y0 + 0.1, 0.2, w - 0.2, d - 0.2, h - 0.2, self.color, outline=True, texture="planks")
        draw_voxel_box(surface, camera, x0 + w * 0.5 - 0.25, y0 + d - 0.12, 0.2, 0.5, 0.05, h * 0.55, (54, 38, 28), outline=False)
        draw_voxel_box(surface, camera, x0 + w - 0.12, y0 + d * 0.5 - 0.25, 0.2, 0.05, 0.5, h * 0.55, (54, 38, 28), outline=False)
        self._hip_roof(surface, camera, x0, y0, w, d, h, (176, 144, 72), layers=3, overhang=0.35, step=0.45, thick=0.2, texture="thatch")

    def _render_tent(self, surface: pygame.Surface, camera):
        """Barraca de lona em degraus que se estreitam até a cumeeira, com a entrada escura."""
        x0, y0, w, d, h = self.wx, self.wy, self.width, self.depth, self.height
        gx, gy = camera.apply(x0 + w / 2, y0 + d / 2, 0.0)
        pygame.draw.ellipse(surface, (60, 96, 50), (gx - int(w * 18), gy - int(d * 8), int(w * 36), int(d * 16)))
        steps = 5
        for i in range(steps):
            inset = w * 0.5 * i / steps
            col = tuple(min(255, int(c * (0.9 + 0.05 * i))) for c in self.color)
            draw_voxel_box(surface, camera, x0 + inset, y0, h * i / steps, w - 2 * inset, d, h / steps + 0.02, col, outline=True, texture="cloth")
        draw_voxel_box(surface, camera, x0 + w * 0.5 - 0.3, y0 + d - 0.03, 0.0, 0.6, 0.04, h * 0.55, (50, 40, 34), outline=False)
        draw_voxel_box(surface, camera, x0 + w * 0.5 - 0.04, y0 - 0.04, h, 0.08, d + 0.08, 0.08, (98, 70, 44), outline=False)

    def _render_palisade(self, surface: pygame.Surface, camera):
        """Paliçada (mabori) de estacas pontudas lado a lado ao longo do maior lado, com travessas de corda."""
        x0, y0, w, d, h = self.wx, self.wy, self.width, self.depth, self.height
        along_x = w >= d
        length = w if along_x else d
        count = max(2, int(length / 0.42))
        step = length / count
        for i in range(count):
            a = i * step
            lean = 0.04 * ((i * 7) % 3 - 1)
            ph = h + 0.18 * (((i * 5) % 4) / 3.0)
            col = tuple(int(c * (0.9 + 0.1 * ((i * 3) % 3) / 2.0)) for c in self.color)
            if along_x:
                draw_voxel_box(surface, camera, x0 + a, y0, 0.0, step * 0.92, d, ph, col, outline=True, texture="bark")
                draw_voxel_box(surface, camera, x0 + a + step * 0.2 + lean, y0 + d * 0.2, ph, step * 0.5, d * 0.6, 0.16, col, outline=False)
            else:
                draw_voxel_box(surface, camera, x0, y0 + a, 0.0, w, step * 0.92, ph, col, outline=True, texture="bark")
                draw_voxel_box(surface, camera, x0 + w * 0.2, y0 + a + step * 0.2 + lean, ph, w * 0.6, step * 0.5, 0.16, col, outline=False)
        z = h * 0.45
        rope = (176, 146, 98)
        if along_x:
            draw_voxel_box(surface, camera, x0, y0 - 0.03, z, w, d + 0.06, 0.07, rope, outline=False)
        else:
            draw_voxel_box(surface, camera, x0 - 0.03, y0, z, w + 0.06, d, 0.07, rope, outline=False)

    def _render_pillar(self, surface: pygame.Surface, camera):
        """Coluna de pedra: pedestal largo, fuste e capitel, com um friso na cor do material."""
        x0, y0, w, d, h = self.wx, self.wy, self.width, self.depth, self.height
        dark = tuple(int(c * 0.72) for c in self.color)
        light = tuple(min(255, int(c * 1.18)) for c in self.color)
        gx, gy = camera.apply(x0 + w / 2, y0 + d / 2, 0.0)
        pygame.draw.ellipse(surface, (12, 8, 18), (gx - 26, gy - 12, 52, 24))
        draw_voxel_box(surface, camera, x0 - 0.12, y0 - 0.12, 0.0, w + 0.24, d + 0.24, 0.30, dark, outline=True)
        draw_voxel_box(surface, camera, x0, y0, 0.30, w, d, h - 0.60, self.color, outline=True, texture="stone")
        draw_voxel_box(surface, camera, x0 - 0.04, y0 - 0.04, h * 0.45, w + 0.08, d + 0.08, 0.10, light, outline=False)
        draw_voxel_box(surface, camera, x0 - 0.14, y0 - 0.14, h - 0.30, w + 0.28, d + 0.28, 0.30, dark, outline=True)

    def _render_barrel(self, surface: pygame.Surface, camera):
        x0, y0, w, d, h = self.wx, self.wy, self.width, self.depth, self.height
        draw_voxel_box(surface, camera, x0, y0, 0.0, w, d, h, self.color, outline=True, texture="planks")
        hoop = tuple(int(c * 0.55) for c in self.color)
        for z in (h * 0.2, h * 0.68):
            draw_voxel_box(surface, camera, x0 - 0.03, y0 - 0.03, z, w + 0.06, d + 0.06, 0.06, hoop, outline=False)

    def _render_boat(self, surface: pygame.Surface, camera):
        """Casco comprido ao longo do eixo X: quilha escura, bordas, proa elevada, banco e remo apoiado."""
        x0, y0, w, d = self.wx, self.wy, self.width, self.depth
        keel = (52, 38, 28)
        plank = self.color
        draw_voxel_box(surface, camera, x0 + 0.15, y0 + 0.10, 0.0, w - 0.30, d - 0.20, 0.18, keel, outline=True)
        draw_voxel_box(surface, camera, x0, y0, 0.12, w, 0.14, 0.34, plank, outline=True, texture="planks")
        draw_voxel_box(surface, camera, x0, y0 + d - 0.14, 0.12, w, 0.14, 0.34, plank, outline=True, texture="planks")
        draw_voxel_box(surface, camera, x0 + w - 0.16, y0 + 0.10, 0.12, 0.16, d - 0.20, 0.34, plank, outline=True, texture="planks")
        draw_voxel_box(surface, camera, x0, y0 + 0.14, 0.12, 0.16, d - 0.28, 0.58, plank, outline=True)
        draw_voxel_box(surface, camera, x0 + w * 0.45, y0 + 0.14, 0.30, 0.18, d - 0.28, 0.07, (74, 54, 38), outline=True)
        # Remo longo apoiado na amurada (a "espada" de madeira de Musashi)
        draw_voxel_box(surface, camera, x0 + w * 0.2, y0 + d + 0.05, 0.0, w * 0.55, 0.07, 0.07, (150, 112, 72), outline=True)
        draw_voxel_box(surface, camera, x0 + w * 0.2 + w * 0.55, y0 + d + 0.02, 0.0, 0.30, 0.14, 0.07, (170, 128, 84), outline=True)


class RailPost:
    """Estaca de madeira de um cercado de buraco; liga-se à próxima por duas cordas. Não bloqueia (o bloqueio é do PitZone)."""

    ROPE_COLOR = (176, 146, 98)

    def __init__(self, wx: float, wy: float, next_point: tuple[float, float] | None = None):
        self.wx = wx
        self.wy = wy
        self.next_point = next_point

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        if self.next_point is not None:
            nx, ny = self.next_point
            for z, sag in ((0.50, 0.05), (0.30, 0.04)):
                a = camera.apply(self.wx, self.wy, z)
                b = camera.apply(nx, ny, z)
                mid = camera.apply((self.wx + nx) / 2.0, (self.wy + ny) / 2.0, z - sag)
                pygame.draw.lines(surface, self.ROPE_COLOR, False, [a, mid, b], 2)
        draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05, 0.0, 0.10, 0.10, 0.60, (98, 68, 44), outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.065, self.wy - 0.065, 0.58, 0.13, 0.13, 0.05, (128, 92, 60), outline=False)


def _aabb_distance(rect: tuple[float, float, float, float], px: float, py: float) -> float:
    return math.hypot(px - max(rect[0], min(px, rect[2])), py - max(rect[1], min(py, rect[3])))


class Cannon(SolidProp):
    """
    Canhão naval sólido com pavio visível (Convés na Tempestade). Qualquer golpe ou projétil que o toque acende
    o pavio; depois de `FUSE_TIME` ele dispara em linha reta, matando quem estiver no corredor, e recarrega.
    O corredor de tiro aparece no chão enquanto o pavio queima, então é um perigo que ambos podem usar.
    """

    FUSE_TIME = 1.7
    RELOAD_TIME = 7.0
    RANGE = 11.0
    HALF_WIDTH = 0.55
    FLASH_TIME = 0.30
    BALL_SPEED = 18.0  # a bala atravessa o convés em cerca de 0.6 s: dá para ver e para esquivar
    RECOIL_DISTANCE = 0.45
    RECOIL_TIME = 0.55

    def __init__(self, wx: float, wy: float, facing: tuple[float, float] = (1.0, 0.0),
                 color: tuple[int, int, int] = (46, 44, 42)):
        fx, fy = facing
        self.facing = (1.0 if fx > 0 else -1.0, 0.0) if abs(fx) >= abs(fy) else (0.0, 1.0 if fy > 0 else -1.0)
        along_x = self.facing[0] != 0.0
        super().__init__(wx, wy, 1.8 if along_x else 1.1, 1.1 if along_x else 1.8, height=0.62, color=color, style="cannon")
        self.state = "idle"  # idle -> lit -> reload -> idle
        self.timer = 0.0
        self.flash = 0.0
        self.recoil = 0.0  # 1.0 no disparo, decai a 0: o canhão desliza para trás e volta
        self.shot_age: float | None = None  # idade da bala em voo (None = nenhuma)
        self._hit_ids: set[int] = set()
        self._just_lit = False

    @property
    def center(self) -> tuple[float, float]:
        return self.wx + self.width / 2.0, self.wy + self.depth / 2.0

    @property
    def muzzle(self) -> tuple[float, float]:
        cx, cy = self.center
        return cx + self.facing[0] * (self.width / 2.0 if self.facing[0] else 0.0), \
            cy + self.facing[1] * (self.depth / 2.0 if self.facing[1] else 0.0)

    def ignite(self, hx: float, hy: float, radius: float) -> bool:
        """Chamado por golpes e projéteis; só acende com o pavio apagado e fora da recarga."""
        if self.state != "idle":
            return False
        if _aabb_distance((self.wx, self.wy, self.wx + self.width, self.wy + self.depth), hx, hy) > radius + 0.1:
            return False
        self.state, self.timer, self._just_lit = "lit", self.FUSE_TIME, True
        return True

    def tick(self, arena, dt: float, fighters: list, camera, particles: list, banners: list):
        self.flash = max(0.0, self.flash - dt)
        self.recoil = max(0.0, self.recoil - dt / self.RECOIL_TIME)
        if self.shot_age is not None:
            self._advance_ball(dt, fighters, particles)
        if self._just_lit:
            self._just_lit = False
            self._play("smoke_puff")
            if banners is not None:
                from src.effects.particles import FloatingBanner
                from src.i18n import t
                cx, cy = self.center
                banners.append(FloatingBanner(t("banner_cannon_lit"), cx, cy, wz=1.5, color=(255, 170, 60), duration=1.3))
        if self.state == "lit":
            self.timer -= dt
            if particles is not None and random.random() < 0.7:
                from src.effects.particles import SparkParticle
                fx, fy, fz = self._fuse_point()
                particles.append(SparkParticle(fx, fy, fz, color=(255, 190, 80)))
            if self.timer <= 0.0:
                self._fire(fighters, camera, particles)
        elif self.state == "reload":
            self.timer -= dt
            if self.timer <= 0.0:
                self.state = "idle"

    def _advance_ball(self, dt: float, fighters: list, particles: list):
        """A bala em voo derruba quem cruza o seu caminho (varredura entre dois quadros); esquiva com i-frames atravessa."""
        prev = self.shot_age * self.BALL_SPEED
        self.shot_age += dt
        now = self.shot_age * self.BALL_SPEED
        mx, my = self.muzzle
        fx, fy = self.facing
        for f in fighters:
            if f is None or not getattr(f, "is_alive", False) or id(f) in self._hit_ids or getattr(f, "wz", 0.0) > 0.8:
                continue
            along = (f.wx - mx) * fx + (f.wy - my) * fy
            across = abs((f.wx - mx) * fy - (f.wy - my) * fx)
            if prev - 0.3 <= along <= now + 0.3 and across < self.HALF_WIDTH + getattr(f, "radius", 0.35) * 0.5:
                self._hit_ids.add(id(f))
                f.take_hit((fx, fy), damage=3)  # tiro de canhão é fatal para qualquer lutador
        if particles is not None:
            from src.effects.particles import SmokeParticle
            bx, by = mx + fx * min(now, self.RANGE), my + fy * min(now, self.RANGE)
            particles.append(SmokeParticle(bx, by, wz=0.5, color=(150, 150, 158), radius=0.2, lifetime=0.45))
        if now >= self.RANGE:
            self.shot_age = None

    def _fuse_point(self) -> tuple[float, float, float]:
        """Ponta do pavio: sobre a culatra, no lado oposto à boca."""
        cx, cy = self.center
        return cx - self.facing[0] * (self.width / 2.0 - 0.22), cy - self.facing[1] * (self.depth / 2.0 - 0.22), 0.80

    @staticmethod
    def _play(name: str):
        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent(name))
        except Exception:
            pass

    def _fire(self, fighters: list, camera, particles: list):
        self.state, self.timer, self.flash, self.recoil = "reload", self.RELOAD_TIME, self.FLASH_TIME, 1.0
        self.shot_age, self._hit_ids = 0.0, set()
        self._play("cannon_fire")
        if camera is not None and hasattr(camera, "add_shake"):
            camera.add_shake(11.0)
        mx, my = self.muzzle
        fx, fy = self.facing
        if particles is not None:
            from src.effects.particles import CannonShotParticle, FlameVoxelParticle, SmokeParticle, SparkParticle
            particles.append(CannonShotParticle(mx, my, fx, fy, self.BALL_SPEED, self.RANGE))
            for _ in range(16):
                particles.append(FlameVoxelParticle(mx + fx * 0.3, my + fy * 0.3, wz=0.45))
            for _ in range(14):
                particles.append(SmokeParticle(mx + fx * 0.7, my + fy * 0.7, wz=0.45, color=(170, 170, 176), radius=0.4, lifetime=1.0))
            for _ in range(10):
                particles.append(SparkParticle(mx, my, 0.45))
        self._advance_ball(0.0, fighters, None)  # quem está colado na boca é atingido no mesmo quadro

    def corridor(self) -> list[tuple[float, float]]:
        """Retângulo do corredor de tiro no chão (4 cantos)."""
        mx, my = self.muzzle
        fx, fy = self.facing
        hw = self.HALF_WIDTH
        px, py = -fy, fx
        end_x, end_y = mx + fx * self.RANGE, my + fy * self.RANGE
        return [(mx + px * hw, my + py * hw), (end_x + px * hw, end_y + py * hw),
                (end_x - px * hw, end_y - py * hw), (mx - px * hw, my - py * hw)]

    def render_ground(self, arena, surface, camera, time_val: float):
        """Corredor de tiro riscado no chão enquanto o pavio queima (mais rápido perto do fim) e clarão após o disparo."""
        if self.state == "lit":
            urgency = 1.0 - max(0.0, self.timer) / self.FUSE_TIME
            on = int(time_val * (4.0 + 10.0 * urgency)) % 2 == 0
            color = (232, 70, 48) if on else (150, 48, 40)
        elif self.flash > 0.0:
            color = (255, 214, 120)
        else:
            return
        corners = self.corridor()
        mx, my = self.muzzle
        fx, fy = self.facing
        px, py = -fy, fx
        hw = self.HALF_WIDTH
        for side in (-1.0, 1.0):
            a = camera.apply(mx + px * hw * side, my + py * hw * side, 0.03)
            b = camera.apply(corners[1][0] if side > 0 else corners[2][0], corners[1][1] if side > 0 else corners[2][1], 0.03)
            pygame.draw.line(surface, color, a, b, 2)
        for i in range(1, int(self.RANGE)):
            ax, ay = mx + fx * i, my + fy * i
            pygame.draw.line(surface, color, camera.apply(ax + px * hw, ay + py * hw, 0.03),
                             camera.apply(ax - px * hw, ay - py * hw, 0.03), 1)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        """Canhão deslizando para trás no recuo e tremendo enquanto o pavio queima."""
        shift = -self.RECOIL_DISTANCE * (self.recoil ** 2)
        px, py = -self.facing[1], self.facing[0]
        if self.state == "lit":
            urgency = 1.0 - max(0.0, self.timer) / self.FUSE_TIME
            shift += 0.045 * urgency * math.sin(time_val * 70.0)
            ox, oy = self.facing[0] * shift + px * 0.02 * urgency * math.sin(time_val * 53.0), self.facing[1] * shift + py * 0.02 * urgency * math.sin(time_val * 53.0)
        else:
            ox, oy = self.facing[0] * shift, self.facing[1] * shift
        base = (self.wx, self.wy)
        self.wx, self.wy = base[0] + ox, base[1] + oy
        try:
            self._render_body(surface, camera, time_val)
        finally:
            self.wx, self.wy = base

    def _render_body(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x0, y0, w, d = self.wx, self.wy, self.width, self.depth
        wood = (96, 66, 44)
        along_x = self.facing[0] != 0.0
        # Reparo de madeira e rodas
        draw_voxel_box(surface, camera, x0, y0, 0.0, w, d, 0.24, wood, outline=True)
        if along_x:
            for wy_ in (y0 - 0.07, y0 + d - 0.05):
                draw_voxel_box(surface, camera, x0 + 0.25, wy_, 0.0, w - 0.5, 0.12, 0.34, (60, 42, 30), outline=True)
        else:
            for wx_ in (x0 - 0.07, x0 + w - 0.05):
                draw_voxel_box(surface, camera, wx_, y0 + 0.25, 0.0, 0.12, d - 0.5, 0.34, (60, 42, 30), outline=True)
        # Cano de ferro: mais escuro enquanto recarrega
        barrel = (86, 58, 50) if self.state == "reload" else self.color
        cx, cy = self.center
        bw = 0.46
        if along_x:
            draw_voxel_box(surface, camera, x0 + 0.05, cy - bw / 2, 0.24, w - 0.10, bw, 0.36, barrel, outline=True)
            ring_x = x0 + w - 0.22 if self.facing[0] > 0 else x0 + 0.04
            draw_voxel_box(surface, camera, ring_x, cy - bw / 2 - 0.04, 0.24, 0.18, bw + 0.08, 0.44, (96, 94, 90), outline=True)
        else:
            draw_voxel_box(surface, camera, cx - bw / 2, y0 + 0.05, 0.24, bw, d - 0.10, 0.36, barrel, outline=True)
            ring_y = y0 + d - 0.22 if self.facing[1] > 0 else y0 + 0.04
            draw_voxel_box(surface, camera, cx - bw / 2 - 0.04, ring_y, 0.24, bw + 0.08, 0.18, 0.44, (96, 94, 90), outline=True)
        # Pavio: corda pálida até a ponta, que brilha enquanto queima
        fx_, fy_, fz_ = self._fuse_point()
        base = camera.apply(fx_, fy_, 0.60)
        tip = camera.apply(fx_, fy_, fz_)
        pygame.draw.line(surface, (206, 190, 150), base, tip, 2)
        if self.state == "lit":
            flick = 4 + int(2 * (0.5 + 0.5 * math.sin(time_val * 30.0)))
            pygame.draw.circle(surface, (255, 120, 40), tip, flick + 2)
            pygame.draw.circle(surface, (255, 230, 120), tip, flick - 1)
        else:
            pygame.draw.circle(surface, (120, 108, 90), tip, 2)
        if self.flash > 0.0:
            mx, my = self.muzzle
            blast = camera.apply(mx + self.facing[0] * 0.4, my + self.facing[1] * 0.4, 0.5)
            r = int(26 * self.flash / self.FLASH_TIME) + 6
            pygame.draw.circle(surface, (255, 150, 40), blast, r)
            pygame.draw.circle(surface, (255, 240, 170), blast, max(2, r // 2))


class PowderBarrel(SolidProp):
    """
    Barril de pólvora com pavio visível (Campo de Nagashino). Golpe, projétil ou a explosão de outro barril acende o
    pavio; a explosão mata quem estiver no raio e acende os barris vizinhos. Depois, fica só a cratera.
    """

    FUSE_TIME = 1.4
    CHAIN_FUSE = 0.35
    BLAST_RADIUS = 2.3

    def __init__(self, wx: float, wy: float, color: tuple[int, int, int] = (104, 72, 44)):
        super().__init__(wx - 0.4, wy - 0.4, 0.8, 0.8, height=0.95, color=color, style="powderbarrel")
        self.state = "idle"  # idle -> lit -> spent
        self.timer = 0.0
        self.flash = 0.0
        self._just_lit = False

    @property
    def center(self) -> tuple[float, float]:
        return self.wx + self.width / 2.0, self.wy + self.depth / 2.0

    def danger_circle(self) -> tuple[float, float, float] | None:
        cx, cy = self.center
        return (cx, cy, self.BLAST_RADIUS) if self.state == "lit" else None

    def check_collision(self, px: float, py: float, p_radius: float = 0.3):
        if self.state == "spent":
            return False, 0.0, 0.0
        return super().check_collision(px, py, p_radius)

    def ignite(self, hx: float, hy: float, radius: float) -> bool:
        if self.state != "idle":
            return False
        if _aabb_distance((self.wx, self.wy, self.wx + self.width, self.wy + self.depth), hx, hy) > radius + 0.1:
            return False
        self.state, self.timer, self._just_lit = "lit", self.FUSE_TIME, True
        return True

    def _chain(self, fuse: float):
        if self.state == "idle":
            self.state, self.timer, self._just_lit = "lit", min(fuse, self.FUSE_TIME), True

    def tick(self, arena, dt: float, fighters: list, camera, particles: list, banners: list):
        self.flash = max(0.0, self.flash - dt)
        if self._just_lit:
            self._just_lit = False
            Cannon._play("smoke_puff")
            if banners is not None:
                from src.effects.particles import FloatingBanner
                from src.i18n import t
                cx, cy = self.center
                banners.append(FloatingBanner(t("banner_powder_lit"), cx, cy, wz=1.5, color=(255, 170, 60), duration=1.2))
        if self.state != "lit":
            return
        self.timer -= dt
        if particles is not None and random.random() < 0.8:
            from src.effects.particles import SparkParticle
            cx, cy = self.center
            particles.append(SparkParticle(cx, cy, 1.1, color=(255, 190, 80)))
        if self.timer <= 0.0:
            self._explode(arena, fighters, camera, particles)

    def _explode(self, arena, fighters: list, camera, particles: list):
        self.state, self.flash = "spent", 0.4
        Cannon._play("bomb_explode")
        if camera is not None and hasattr(camera, "add_shake"):
            camera.add_shake(14.0)
        cx, cy = self.center
        if particles is not None:
            from src.effects.particles import FlameVoxelParticle, SmokeParticle, SparkParticle
            for _ in range(30):
                particles.append(FlameVoxelParticle(cx, cy, wz=0.3))
            for _ in range(14):
                particles.append(SmokeParticle(cx, cy, wz=0.5, color=(120, 116, 120), radius=0.5, lifetime=1.2))
            for _ in range(16):
                particles.append(SparkParticle(cx, cy, 0.5))
        for f in fighters:
            if f is not None and getattr(f, "is_alive", False) and math.hypot(f.wx - cx, f.wy - cy) < self.BLAST_RADIUS + getattr(f, "radius", 0.35) * 0.5 \
                    and getattr(f, "wz", 0.0) < 1.2:
                f.take_hit((f.wx - cx, f.wy - cy), damage=3)  # explosão de pólvora é fatal
        for other in getattr(arena, "interactives", ()):
            if isinstance(other, PowderBarrel) and other is not self:
                ox, oy = other.center
                if math.hypot(ox - cx, oy - cy) < self.BLAST_RADIUS + 0.5:
                    other._chain(self.CHAIN_FUSE)

    def render_ground(self, arena, surface, camera, time_val: float):
        cx, cy = self.center
        if self.state == "spent":
            pts = [camera.apply(cx + math.cos(a) * 0.9, cy + math.sin(a) * 0.9, 0.02) for a in (2.0 * math.pi * i / 16 for i in range(16))]
            pygame.draw.polygon(surface, (34, 28, 24), pts)
            if self.flash > 0.0:
                big = [camera.apply(cx + math.cos(a) * self.BLAST_RADIUS * (1.0 - 0.5 * self.flash / 0.4), cy + math.sin(a) * self.BLAST_RADIUS * (1.0 - 0.5 * self.flash / 0.4), 0.03)
                       for a in (2.0 * math.pi * i / 24 for i in range(24))]
                pygame.draw.polygon(surface, (255, 214, 130), big)
            return
        if self.state == "lit":
            urgency = 1.0 - max(0.0, self.timer) / self.FUSE_TIME
            on = int(time_val * (4.0 + 10.0 * urgency)) % 2 == 0
            color = (232, 70, 48) if on else (150, 48, 40)
            ring = [camera.apply(cx + math.cos(a) * self.BLAST_RADIUS, cy + math.sin(a) * self.BLAST_RADIUS, 0.03) for a in (2.0 * math.pi * i / 28 for i in range(28))]
            pygame.draw.polygon(surface, color, ring, 3)
            inner = [camera.apply(cx + math.cos(a) * self.BLAST_RADIUS * urgency, cy + math.sin(a) * self.BLAST_RADIUS * urgency, 0.03) for a in (2.0 * math.pi * i / 28 for i in range(28))]
            pygame.draw.polygon(surface, color, inner, 2)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        if self.state == "spent":
            return
        cx, cy = self.center
        shake = 0.03 * math.sin(time_val * 60.0) if self.state == "lit" else 0.0
        x, y = cx - 0.34 + shake, cy - 0.34
        draw_voxel_box(surface, camera, x, y, 0.0, 0.68, 0.68, 0.85, self.color, outline=True)
        hoop = tuple(int(c * 0.5) for c in self.color)
        for z in (0.14, 0.62):
            draw_voxel_box(surface, camera, x - 0.03, y - 0.03, z, 0.74, 0.74, 0.06, hoop, outline=False)
        draw_voxel_box(surface, camera, x + 0.1, y + 0.1, 0.85, 0.48, 0.48, 0.07, (60, 44, 32), outline=True)
        base = camera.apply(cx, cy, 0.92)
        tip = camera.apply(cx + 0.12, cy - 0.1, 1.28)
        pygame.draw.line(surface, (206, 190, 150), base, tip, 2)
        if self.state == "lit":
            flick = 4 + int(2 * (0.5 + 0.5 * math.sin(time_val * 30.0)))
            pygame.draw.circle(surface, (255, 120, 40), tip, flick + 2)
            pygame.draw.circle(surface, (255, 230, 120), tip, flick - 1)
        else:
            pygame.draw.circle(surface, (120, 108, 90), tip, 2)


class ShrineBell(SolidProp):
    """
    Sino de bronze do santuário (Tomoe). Golpe ou projétil que o toque faz soar o sino, e o som dissipa a fumaça da
    Kasumi e as nuvens de veneno da Okuni em toda a arena. Tem uma pausa entre toques.
    """

    COOLDOWN = 2.0
    RING_TIME = 1.4

    def __init__(self, wx: float, wy: float):
        super().__init__(wx - 0.8, wy - 0.8, 1.6, 1.6, height=2.1, color=(110, 78, 50), style="bell")
        self.cooldown = 0.0
        self.ring = 0.0
        self._pending = False

    def ignite(self, hx: float, hy: float, radius: float) -> bool:
        if self.cooldown > 0.0:
            return False
        if _aabb_distance((self.wx, self.wy, self.wx + self.width, self.wy + self.depth), hx, hy) > radius + 0.1:
            return False
        self.cooldown, self.ring, self._pending = self.COOLDOWN, self.RING_TIME, True
        return True

    def tick(self, arena, dt: float, fighters: list, camera, particles: list, banners: list):
        self.cooldown = max(0.0, self.cooldown - dt)
        self.ring = max(0.0, self.ring - dt)
        if not self._pending:
            return
        self._pending = False
        arena.dispel_requested = True
        Cannon._play("round_win")
        cx, cy = self.wx + self.width / 2.0, self.wy + self.depth / 2.0
        if banners is not None:
            from src.effects.particles import FloatingBanner
            from src.i18n import t
            banners.append(FloatingBanner(t("banner_bell"), cx, cy, wz=2.6, color=(255, 226, 150), duration=1.6))
        if particles is not None:
            from src.effects.particles import SparkParticle, SmokeParticle
            for _ in range(10):
                particles.append(SparkParticle(cx, cy, 1.3, color=(255, 230, 150)))
            for _ in range(8):
                particles.append(SmokeParticle(cx, cy, wz=1.2, color=(240, 236, 220), radius=0.5, lifetime=0.9))

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x0, y0, w, d, h = self.wx, self.wy, self.width, self.depth, self.height
        gx, gy = camera.apply(x0 + w / 2, y0 + d / 2, 0.0)
        pygame.draw.ellipse(surface, (88, 82, 74), (gx - 40, gy - 18, 80, 36))
        draw_voxel_box(surface, camera, x0, y0, 0.0, w, d, 0.18, (112, 108, 100), outline=True)
        for px, py in ((x0 + 0.08, y0 + 0.08), (x0 + w - 0.24, y0 + 0.08), (x0 + 0.08, y0 + d - 0.24), (x0 + w - 0.24, y0 + d - 0.24)):
            draw_voxel_box(surface, camera, px, py, 0.18, 0.16, 0.16, h - 0.5, (98, 56, 40), outline=True)
        draw_voxel_box(surface, camera, x0 + 0.05, y0 + 0.05, h - 0.32, w - 0.1, d - 0.1, 0.12, (70, 44, 34), outline=True)
        self._hip_roof(surface, camera, x0, y0, w, d, h - 0.2, (60, 66, 82), layers=2, overhang=0.3, step=0.5, thick=0.16)
        swing = 0.18 * math.sin(time_val * 9.0) * (self.ring / self.RING_TIME) ** 2
        bx, by = x0 + w / 2 - 0.26 + swing, y0 + d / 2 - 0.26
        draw_voxel_box(surface, camera, bx + 0.22, by + 0.22, h - 0.62, 0.08, 0.08, 0.3, (60, 50, 40), outline=False)
        glow = int(60 * (self.ring / self.RING_TIME))
        draw_voxel_box(surface, camera, bx, by, 0.7, 0.52, 0.52, h - 1.4, (150 + glow, 108 + glow // 2, 54), outline=True)
        draw_voxel_box(surface, camera, bx - 0.04, by - 0.04, 0.66, 0.60, 0.60, 0.1, (176, 132, 70), outline=False)
