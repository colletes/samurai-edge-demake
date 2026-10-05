"""Props decorativos sem colisão das arenas temáticas: lanternas de papel, faixas, nobori e incensário (6.3.6)."""
import math
import random

import pygame

from src.isometric.voxel_renderer import draw_voxel_box
from src.world.obstacles import AncientTree, Rock

ASAGI = (132, 200, 224)  # azul-claro do haori do Shinsengumi
HAORI_WHITE = (240, 240, 246)

_banner_cache: dict[tuple, pygame.Surface] = {}


def _draw_fleur_de_lis(surf: pygame.Surface, cx: int, cy: int, color: tuple[int, int, int]):
    """Flor-de-lis esquemática: pétala central, duas pétalas curvas, faixa e base."""
    pygame.draw.polygon(surf, color, [(cx, cy - 16), (cx + 5, cy - 4), (cx + 3, cy + 8), (cx - 3, cy + 8), (cx - 5, cy - 4)])
    for s in (-1, 1):
        pygame.draw.polygon(surf, color, [(cx + s * 4, cy + 2), (cx + s * 15, cy - 10), (cx + s * 17, cy - 1), (cx + s * 13, cy + 8), (cx + s * 6, cy + 9)])
    pygame.draw.rect(surf, color, (cx - 9, cy + 7, 18, 4))
    pygame.draw.polygon(surf, color, [(cx - 7, cy + 11), (cx + 7, cy + 11), (cx + 4, cy + 18), (cx - 4, cy + 18)])


class PaperLantern:
    """Poste de madeira com chōchin vermelho aceso; o topo serve de apoio para as faixas (`Bunting`)."""

    POST_TOP = 2.4

    def __init__(self, wx: float, wy: float, color: tuple[int, int, int] = (200, 34, 30)):
        self.wx = wx
        self.wy = wy
        self.color = color

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x, y = self.wx, self.wy
        draw_voxel_box(surface, camera, x - 0.2, y - 0.2, 0.0, 0.4, 0.4, 0.14, (78, 72, 68), outline=True)
        draw_voxel_box(surface, camera, x - 0.07, y - 0.07, 0.14, 0.14, 0.14, self.POST_TOP - 0.14, (86, 58, 38), outline=True)
        draw_voxel_box(surface, camera, x - 0.07, y - 0.07, self.POST_TOP - 0.55, 0.14, 0.14, 0.05, (60, 40, 28), outline=False)
        flick = 0.9 + 0.1 * math.sin(time_val * 9.0 + x * 2.0 + y)
        glow = tuple(min(255, int(c * flick)) for c in self.color)
        z = self.POST_TOP - 1.05
        draw_voxel_box(surface, camera, x - 0.2, y - 0.2, z - 0.04, 0.4, 0.4, 0.05, (30, 26, 26), outline=False)
        draw_voxel_box(surface, camera, x - 0.17, y - 0.17, z, 0.34, 0.34, 0.5, glow, outline=True)
        draw_voxel_box(surface, camera, x - 0.2, y - 0.2, z + 0.5, 0.4, 0.4, 0.05, (30, 26, 26), outline=False)
        draw_voxel_box(surface, camera, x - 0.03, y - 0.03, z + 0.12, 0.06, 0.06, 0.26, (255, 214, 120), outline=False)


class Bunting:
    """Corda com bandeirolas triangulares azul-claro e branco (padrão dandara do haori) entre dois postes."""

    def __init__(self, x0: float, y0: float, x1: float, y1: float, z: float = 2.35, flags: int = 11):
        self.x0, self.y0, self.x1, self.y1, self.z, self.flags = x0, y0, x1, y1, z, flags
        self.wx, self.wy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

    def _point(self, t: float, drop: float = 0.0, time_val: float = 0.0):
        sag = 0.22 * math.sin(math.pi * t)
        sway = 0.04 * math.sin(time_val * 2.2 + t * 6.0)
        return self.x0 + (self.x1 - self.x0) * t, self.y0 + (self.y1 - self.y0) * t, self.z - sag - drop + sway

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        n = self.flags
        rope = [camera.apply(*self._point(i / n, 0.0, time_val)) for i in range(n + 1)]
        pygame.draw.lines(surface, (70, 52, 40), False, rope, 2)
        for i in range(n):
            a = camera.apply(*self._point(i / n, 0.0, time_val))
            b = camera.apply(*self._point((i + 1) / n, 0.0, time_val))
            tip = camera.apply(*self._point((i + 0.5) / n, 0.5, time_val))
            color = ASAGI if i % 2 == 0 else HAORI_WHITE
            pygame.draw.polygon(surface, color, [a, b, tip])
            pygame.draw.polygon(surface, (86, 100, 118), [a, b, tip], 1)


class NoboriBanner:
    """Nobori: mastro com travessa e faixa vertical de tecido que ondula e traz kanji (誠 do Shinsengumi, 悪即斬 do Saitou)."""

    CLOTH_WIDTH = 0.55  # em unidades de mundo, para escalar com o zoom e o azimute

    def __init__(self, wx: float, wy: float, text: str = "誠", cloth: tuple[int, int, int] = (186, 32, 38),
                 ink: tuple[int, int, int] = (244, 238, 224), pole_height: float = 3.3, emblem: str = ""):
        self.wx = wx
        self.wy = wy
        self.emblem = emblem  # "fleur": flor-de-lis desenhada no lugar do kanji
        self.text = text
        self.cloth = cloth
        self.ink = ink
        self.pole_height = pole_height

    def _image(self) -> pygame.Surface:
        key = (self.text, self.cloth, self.ink, self.emblem)
        img = _banner_cache.get(key)
        if img is None and self.emblem == "fleur":
            img = pygame.Surface((46, 112), pygame.SRCALPHA)
            img.fill(self.cloth)
            pygame.draw.rect(img, tuple(int(c * 0.6) for c in self.cloth), img.get_rect(), 2)
            for oy in (30, 76):
                _draw_fleur_de_lis(img, 23, oy, self.ink)
            pygame.draw.polygon(img, self.cloth, [(0, 112), (23, 96), (46, 112)])  # ponta em V da flâmula
            _banner_cache[key] = img
        if img is None:
            from src.ui.fonts import get_text_font
            font = get_text_font(34)
            glyphs = [font.render(ch, True, self.ink) for ch in self.text]
            h = 14 + sum(g.get_height() - 8 for g in glyphs) + 10
            img = pygame.Surface((46, h), pygame.SRCALPHA)
            img.fill(self.cloth)
            pygame.draw.rect(img, tuple(int(c * 0.6) for c in self.cloth), img.get_rect(), 2)
            y = 10
            for g in glyphs:
                img.blit(g, g.get_rect(midtop=(img.get_width() // 2, y)))
                y += g.get_height() - 8
            _banner_cache[key] = img
        return img

    @property
    def cloth_length(self) -> float:
        img = self._image()
        return self.CLOTH_WIDTH * img.get_height() / img.get_width()

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x, y, h = self.wx, self.wy, self.pole_height
        draw_voxel_box(surface, camera, x - 0.2, y - 0.2, 0.0, 0.4, 0.4, 0.14, (78, 72, 68), outline=True)
        draw_voxel_box(surface, camera, x - 0.05, y - 0.05, 0.14, 0.10, 0.10, h - 0.14, (96, 66, 44), outline=True)
        draw_voxel_box(surface, camera, x - 0.05, y - 0.05, h - 0.02, 0.10, 0.10, 0.08, (150, 120, 70), outline=False)
        draw_voxel_box(surface, camera, x - 0.03, y - 0.03, h - 0.10, 0.06, self.CLOTH_WIDTH + 0.12, 0.06, (60, 44, 32), outline=False)
        # O pano é um plano vertical em mundo (paralelo ao eixo Y): fatias projetadas pela câmera, então
        # escala com o zoom e afina de lado conforme o azimute
        img = self._image()
        length = self.cloth_length
        strips = 8
        step = img.get_width() // strips
        ztop = h - 0.12
        for i in range(strips):
            t0, t1 = i / strips, (i + 1) / strips
            sway = 0.05 * math.sin(time_val * 2.4 + t0 * 3.0 + x) * t0
            ya, yb = y + 0.03 + self.CLOTH_WIDTH * t0, y + 0.03 + self.CLOTH_WIDTH * t1
            ax, ay = camera.apply(x + sway, ya, ztop)
            bx, _ = camera.apply(x + sway, yb, ztop)
            _, ly = camera.apply(x + sway, ya, ztop - length)
            w = abs(bx - ax) + 1
            hgt = max(1, ly - ay)
            col = img.subsurface(pygame.Rect(i * step, 0, step, img.get_height()))
            surface.blit(pygame.transform.scale(col, (int(w), int(hgt))), (min(ax, bx), ay))


class JizoStatue(Rock):
    """
    Estátua de Jizo de pedra com babador vermelho. Entra em `rocks`: bloqueia o movimento e para projéteis, então
    serve de cobertura (Gruta das Sombras).
    """

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.5, height=1.25)

    def render(self, surface: pygame.Surface, camera):
        x, y = self.wx, self.wy
        gx, gy = camera.apply(x, y, 0.0)
        pygame.draw.ellipse(surface, (12, 8, 18), (gx - 22, gy - 10, 44, 20))
        draw_voxel_box(surface, camera, x - 0.30, y - 0.30, 0.0, 0.60, 0.60, 0.22, (92, 88, 102), outline=True)
        draw_voxel_box(surface, camera, x - 0.21, y - 0.21, 0.22, 0.42, 0.42, 0.60, (132, 128, 142), outline=True)
        draw_voxel_box(surface, camera, x - 0.235, y - 0.235, 0.62, 0.47, 0.47, 0.09, (176, 40, 46), outline=True)  # babador
        draw_voxel_box(surface, camera, x - 0.17, y - 0.17, 0.82, 0.34, 0.34, 0.28, (150, 146, 160), outline=True)  # cabeça
        draw_voxel_box(surface, camera, x - 0.20, y - 0.20, 1.06, 0.40, 0.40, 0.10, (150, 146, 160), outline=True)  # gorro
        draw_voxel_box(surface, camera, x - 0.06, y - 0.06, 1.16, 0.12, 0.12, 0.07, (176, 40, 46), outline=False)
        draw_voxel_box(surface, camera, x - 0.10, y + 0.27, 0.0, 0.20, 0.14, 0.10, (70, 66, 80), outline=False)  # oferenda


class PineTree(AncientTree):
    """Pinheiro escuro de copa em camadas (Templo na Névoa); colide como as demais árvores."""

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy)
        self.radius = 0.6
        self.height = 3.8

    def render(self, surface: pygame.Surface, camera):
        x, y = self.wx, self.wy
        gx, gy = camera.apply(x, y, 0.0)
        pygame.draw.ellipse(surface, (14, 24, 24), (gx - 38, gy - 18, 76, 36))
        draw_voxel_box(surface, camera, x - 0.17, y - 0.17, 0.0, 0.34, 0.34, 1.3, (70, 48, 34), outline=True)
        for i, (w, z, h) in enumerate(((1.7, 0.85, 0.7), (1.35, 1.45, 0.7), (1.0, 2.05, 0.7), (0.6, 2.65, 0.7))):
            shade = (26 + 6 * i, 70 + 9 * i, 58 + 7 * i)
            draw_voxel_box(surface, camera, x - w / 2, y - w / 2, z, w, w, h, shade, outline=True)
        draw_voxel_box(surface, camera, x - 0.12, y - 0.12, 3.3, 0.24, 0.24, 0.4, (60, 120, 100), outline=False)


class KoiFish:
    """Carpa que nada em círculos na lagoa (só visual); `wx`/`wy` é o centro do passeio."""

    def __init__(self, wx: float, wy: float, radius: float = 1.6, speed: float = 0.5, phase: float = 0.0,
                 color: tuple[int, int, int] = (240, 120, 50)):
        self.wx, self.wy, self.radius, self.speed, self.phase, self.color = wx, wy, radius, speed, phase, color

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        a = time_val * self.speed + self.phase
        x, y = self.wx + math.cos(a) * self.radius, self.wy + math.sin(a * 1.3) * self.radius * 0.8
        hx, hy = -math.sin(a), math.cos(a * 1.3) * 1.3  # direção do nado (aproximada)
        n = math.hypot(hx, hy) or 1.0
        hx, hy = hx / n, hy / n
        wag = math.sin(time_val * 6.0 + self.phase) * 0.08
        for k, (back, size) in enumerate(((0.0, 7), (0.22, 6), (0.42, 4))):
            px = x - hx * back - hy * wag * k
            py = y - hy * back + hx * wag * k
            pygame.draw.circle(surface, self.color if k < 2 else tuple(min(255, c + 30) for c in self.color), camera.apply(px, py, -0.1), size)
        pygame.draw.circle(surface, (250, 240, 230), camera.apply(x + hx * 0.05, y + hy * 0.05, -0.09), 3)


class MistBank:
    """Banco de névoa baixa que deriva devagar sobre o chão (elipse translúcida)."""

    _cache: dict[tuple[int, int], pygame.Surface] = {}

    def __init__(self, wx: float, wy: float, radius: float = 3.0, alpha: int = 46, tint: tuple[int, int, int] = (190, 205, 225)):
        self.wx, self.wy, self.radius, self.alpha, self.tint = wx, wy, radius, alpha, tint

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x = self.wx + 0.6 * math.sin(time_val * 0.25 + self.wy)
        y = self.wy + 0.4 * math.cos(time_val * 0.21 + self.wx)
        cx, cy = camera.apply(x, y, 0.3)
        rx = abs(camera.apply(x + self.radius, y, 0.3)[0] - cx) + abs(camera.apply(x, y + self.radius, 0.3)[0] - cx)
        w, h = max(8, int(rx * 1.2)), max(4, int(rx * 0.6))
        key = (w, h, self.alpha, self.tint)
        surf = MistBank._cache.get(key)
        if surf is None:
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            for i in range(5):
                f = 1.0 - i / 5.0
                pygame.draw.ellipse(surf, (*self.tint, int(self.alpha * (1.0 - f) * 0.9) + 6), (int(w * (1 - f) / 2), int(h * (1 - f) / 2), int(w * f), int(h * f)))
            MistBank._cache[key] = surf
        surface.blit(surf, (cx - w // 2, cy - h // 2))


class ForestTree(AncientTree):
    """Árvore de copa redonda e folhagem clara de dia (Acampamento na Floresta)."""

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy)
        self.radius = 0.65
        self.height = 3.4

    def render(self, surface: pygame.Surface, camera):
        x, y = self.wx, self.wy
        gx, gy = camera.apply(x, y, 0.0)
        pygame.draw.ellipse(surface, (56, 92, 50), (gx - 44, gy - 20, 88, 40))
        draw_voxel_box(surface, camera, x - 0.2, y - 0.2, 0.0, 0.4, 0.4, 1.5, (104, 72, 44), outline=True, texture="bark")
        for i, (w, z, h, col) in enumerate(((1.9, 1.2, 0.8, (58, 132, 56)), (1.6, 1.9, 0.8, (74, 152, 62)), (1.1, 2.6, 0.7, (96, 172, 76)))):
            draw_voxel_box(surface, camera, x - w / 2, y - w / 2, z, w, w, h, col, outline=True, texture="foliage")


class SupplyCrate(Rock):
    """Caixote de suprimentos de madeira: bloqueia o movimento e para projéteis (cobertura)."""

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.55, height=0.95)

    def render(self, surface: pygame.Surface, camera):
        x, y = self.wx, self.wy
        gx, gy = camera.apply(x, y, 0.0)
        pygame.draw.ellipse(surface, (58, 90, 48), (gx - 24, gy - 11, 48, 22))
        draw_voxel_box(surface, camera, x - 0.46, y - 0.46, 0.0, 0.92, 0.92, 0.82, (176, 130, 80), outline=True, texture="planks")
        for z in (0.12, 0.62):
            draw_voxel_box(surface, camera, x - 0.49, y - 0.49, z, 0.98, 0.98, 0.09, (112, 78, 46), outline=False)
        draw_voxel_box(surface, camera, x - 0.50, y - 0.07, 0.0, 1.0, 0.14, 0.82, (120, 86, 52), outline=False)
        draw_voxel_box(surface, camera, x - 0.30, y - 0.30, 0.82, 0.6, 0.6, 0.12, (150, 108, 64), outline=True)


class Campfire:
    """Fogueira do acampamento: brasas, chamas e fumaça (só visual, sem colisão)."""

    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self._carry = random.random()

    def tick(self, arena, dt: float, fighters: list, camera, particles: list, banners: list):
        if particles is None:
            return
        self._carry += dt * 6.0
        while self._carry >= 1.0:
            self._carry -= 1.0
            from src.effects.particles import SmokeParticle
            particles.append(SmokeParticle(self.wx, self.wy, wz=0.7, color=(150, 150, 154), radius=0.28, lifetime=random.uniform(1.4, 2.2)))

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x, y = self.wx, self.wy
        for k in range(8):
            a = k * math.pi / 4.0
            draw_voxel_box(surface, camera, x + math.cos(a) * 0.5 - 0.1, y + math.sin(a) * 0.5 - 0.1, 0.0, 0.2, 0.2, 0.14, (110, 106, 100), outline=True)
        draw_voxel_box(surface, camera, x - 0.35, y - 0.07, 0.04, 0.7, 0.14, 0.12, (86, 56, 34), outline=True)
        draw_voxel_box(surface, camera, x - 0.07, y - 0.35, 0.04, 0.14, 0.7, 0.12, (96, 62, 38), outline=True)
        h = 0.45 + 0.12 * math.sin(time_val * 11.0 + x) + 0.06 * math.sin(time_val * 17.0)
        draw_voxel_box(surface, camera, x - 0.2, y - 0.2, 0.12, 0.4, 0.4, h, (255, 140, 40), outline=False)
        draw_voxel_box(surface, camera, x - 0.1, y - 0.1, 0.12, 0.2, 0.2, h + 0.2, (255, 220, 110), outline=False)


class SnareTrap:
    """
    Armadilha de laço escondida sob terra remexida: atordoa (sem ferir) quem pisa nela e rearma depois.
    O monte de terra e os gravetos são o sinal; ao disparar, o laço sobe e mostra a corda.
    """

    RADIUS = 0.6
    STUN = 1.2
    REARM = 6.0

    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.armed = True
        self.timer = 0.0
        self.spawn_clearance = 1.3

    def tick(self, arena, dt: float, fighters: list, camera, particles: list, banners: list):
        if not self.armed:
            self.timer -= dt
            if self.timer <= 0.0:
                self.armed = True
            return
        for f in fighters:
            if f is None or not getattr(f, "is_alive", False) or getattr(f, "wz", 0.0) > 0.3:
                continue
            if math.hypot(f.wx - self.wx, f.wy - self.wy) < self.RADIUS + getattr(f, "radius", 0.35) * 0.4:
                self.armed, self.timer = False, self.REARM
                f.stun(self.STUN)
                if particles is not None:
                    from src.effects.particles import SmokeParticle
                    for _ in range(8):
                        particles.append(SmokeParticle(self.wx, self.wy, wz=0.2, color=(150, 118, 80), radius=0.3, lifetime=0.6))
                if banners is not None:
                    from src.effects.particles import FloatingBanner
                    from src.i18n import t
                    banners.append(FloatingBanner(t("banner_snare"), self.wx, self.wy, wz=1.5, color=(240, 200, 120), duration=1.2))
                try:
                    from src.audio.sound_events import SoundEvent
                    from src.audio.sound_manager import SoundManager
                    SoundManager.get_instance().play(SoundEvent("obstacle_hit"))
                except Exception:
                    pass
                break

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x, y = self.wx, self.wy
        if self.armed:
            draw_voxel_box(surface, camera, x - 0.5, y - 0.45, 0.0, 1.0, 0.9, 0.05, (92, 64, 40), outline=False)
            for dx, dy, s in ((-0.3, -0.2, 0.22), (0.15, 0.1, 0.26), (-0.05, 0.3, 0.18), (0.32, -0.28, 0.16)):
                draw_voxel_box(surface, camera, x + dx - s / 2, y + dy - s / 2, 0.05, s, s, 0.09, (118, 84, 54), outline=False)
            for a, b in (((-0.45, -0.05), (0.2, 0.4)), ((-0.1, -0.5), (0.35, -0.1))):
                pygame.draw.line(surface, (60, 44, 28), camera.apply(x + a[0], y + a[1], 0.12), camera.apply(x + b[0], y + b[1], 0.12), 2)
        else:
            draw_voxel_box(surface, camera, x - 0.5, y - 0.45, 0.0, 1.0, 0.9, 0.04, (70, 50, 32), outline=False)
            top = camera.apply(x, y, 1.1)
            for k in range(3):
                ang = k * 2.1 + 0.4
                pygame.draw.line(surface, (216, 190, 130), camera.apply(x + math.cos(ang) * 0.35, y + math.sin(ang) * 0.35, 0.0), top, 3)
            pygame.draw.circle(surface, (216, 190, 130), top, 9, 3)


class ScreenPanel(Rock):
    """
    Um painel de biombo dourado (byōbu). Três painéis em zigue-zague formam um biombo que bloqueia o movimento e
    para projéteis; cada painel é uma rocha pequena, então a cobertura segue o desenho.
    """

    def __init__(self, wx: float, wy: float, axis: str = "x", tilt: float = 1.0):
        super().__init__(wx, wy, radius=0.5, height=1.7)
        self.axis = axis
        self.tilt = tilt

    def render(self, surface: pygame.Surface, camera):
        x, y = self.wx, self.wy
        gx, gy = camera.apply(x, y, 0.0)
        pygame.draw.ellipse(surface, (70, 46, 34), (gx - 22, gy - 8, 44, 16))
        w, t = 0.84, 0.10
        off = 0.16 * self.tilt
        if self.axis == "x":
            bx, by, bw, bd = x - w / 2, y - t / 2 + off, w, t
        else:
            bx, by, bw, bd = x - t / 2 + off, y - w / 2, t, w
        draw_voxel_box(surface, camera, bx - 0.02, by - 0.02, 0.0, bw + 0.04, bd + 0.04, 0.12, (44, 30, 26), outline=True)
        draw_voxel_box(surface, camera, bx, by, 0.12, bw, bd, 1.5, (214, 176, 72), outline=True)
        draw_voxel_box(surface, camera, bx - 0.01, by - 0.01, 1.62, bw + 0.02, bd + 0.02, 0.08, (44, 30, 26), outline=False)
        if self.axis == "x":
            draw_voxel_box(surface, camera, x - 0.14, by - 0.015, 0.7, 0.28, bd + 0.03, 0.4, (190, 40, 36), outline=False)
        else:
            draw_voxel_box(surface, camera, bx - 0.015, y - 0.14, 0.7, bw + 0.03, 0.28, 0.4, (190, 40, 36), outline=False)


class StripedCurtain:
    """Cortina do teatro kabuki (jōshiki-maku): faixas verticais preto, caqui e verde, pendurada em plano de mundo."""

    PALETTE = ((28, 26, 30), (230, 104, 42), (44, 124, 74))

    def __init__(self, wx: float, wy: float, length: float = 6.0, axis: str = "x", height: float = 3.2, drop: float = 3.0):
        self.wx, self.wy, self.length, self.axis, self.height, self.drop = wx, wy, length, axis, height, drop
        self.cx = wx + (length / 2 if axis == "x" else 0.0)
        self.cy = wy + (length / 2 if axis == "y" else 0.0)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        n = max(3, int(self.length / 0.8))
        top, bottom = self.height, self.height - self.drop
        draw = lambda a, z, sway=0.0: camera.apply(self.wx + (a if self.axis == "x" else sway), self.wy + (a if self.axis == "y" else sway), z)
        pygame.draw.line(surface, (70, 50, 34), draw(0.0, top + 0.05), draw(self.length, top + 0.05), 4)
        for i in range(n):
            a0, a1 = self.length * i / n, self.length * (i + 1) / n
            sway = 0.05 * math.sin(time_val * 1.4 + i * 0.7)
            quad = [draw(a0, top), draw(a1, top), draw(a1, bottom + sway), draw(a0, bottom + sway)]
            pygame.draw.polygon(surface, self.PALETTE[i % 3], quad)
            pygame.draw.polygon(surface, (16, 14, 18), quad, 1)


class ArcheryTarget(Rock):
    """Alvo de palha do kyudo-jo sobre um suporte de madeira; bloqueia e para projéteis como cobertura baixa."""

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.5, height=1.5)

    def render(self, surface: pygame.Surface, camera):
        x, y = self.wx, self.wy
        gx, gy = camera.apply(x, y, 0.0)
        pygame.draw.ellipse(surface, (186, 170, 132), (gx - 22, gy - 9, 44, 18))
        draw_voxel_box(surface, camera, x - 0.42, y - 0.06, 0.0, 0.08, 0.12, 1.1, (98, 70, 44), outline=True)
        draw_voxel_box(surface, camera, x + 0.34, y - 0.06, 0.0, 0.08, 0.12, 1.1, (98, 70, 44), outline=True)
        c = camera.apply(x, y, 1.0)
        r = max(10, int(abs(camera.apply(x, y, 1.45)[1] - c[1])))
        for k, col in enumerate(((60, 50, 40), (232, 226, 206), (50, 44, 40), (232, 226, 206), (190, 40, 36))):
            pygame.draw.circle(surface, col, c, max(2, r - k * (r // 5)))


class HedgeBlock(Rock):
    """Módulo de sebe aparada: bloqueia o movimento e para projéteis; vários em fila formam a cobertura."""

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.5, height=1.15)

    def render(self, surface: pygame.Surface, camera):
        x, y = self.wx, self.wy
        gx, gy = camera.apply(x, y, 0.0)
        pygame.draw.ellipse(surface, (66, 100, 64), (gx - 26, gy - 11, 52, 22))
        draw_voxel_box(surface, camera, x - 0.46, y - 0.46, 0.0, 0.92, 0.92, 0.95, (44, 112, 56), outline=True, texture="foliage")
        draw_voxel_box(surface, camera, x - 0.40, y - 0.40, 0.95, 0.80, 0.80, 0.2, (66, 140, 72), outline=True, texture="foliage")
        for dx, dy in ((-0.22, -0.2), (0.18, 0.12), (-0.05, 0.25)):
            draw_voxel_box(surface, camera, x + dx - 0.05, y + dy - 0.05, 1.15, 0.1, 0.1, 0.05, (96, 170, 96), outline=False)


class MarbleStatue(Rock):
    """Estátua de mármore sobre pedestal: cobertura decorativa do pátio."""

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.5, height=1.9)

    def render(self, surface: pygame.Surface, camera):
        x, y = self.wx, self.wy
        gx, gy = camera.apply(x, y, 0.0)
        pygame.draw.ellipse(surface, (120, 118, 112), (gx - 24, gy - 10, 48, 20))
        draw_voxel_box(surface, camera, x - 0.38, y - 0.38, 0.0, 0.76, 0.76, 0.18, (196, 192, 184), outline=True, texture="marble")
        draw_voxel_box(surface, camera, x - 0.30, y - 0.30, 0.18, 0.60, 0.60, 0.62, (222, 218, 208), outline=True, texture="marble")
        draw_voxel_box(surface, camera, x - 0.22, y - 0.22, 0.80, 0.44, 0.44, 0.56, (238, 234, 226), outline=True)  # corpo
        draw_voxel_box(surface, camera, x - 0.16, y - 0.16, 1.36, 0.32, 0.32, 0.28, (244, 240, 232), outline=True)  # cabeça
        draw_voxel_box(surface, camera, x + 0.18, y - 0.06, 1.0, 0.1, 0.12, 0.52, (230, 226, 216), outline=False)  # braço erguido


class Fountain(Rock):
    """Fonte barroca no centro do pátio: bacia, pedestal em dois níveis e jatos de água animados."""

    animated = True  # main passa o tempo ao desenhar

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.95, height=2.0)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x, y = self.wx, self.wy
        draw_voxel_box(surface, camera, x - 0.9, y - 0.9, 0.0, 1.8, 1.8, 0.35, (206, 202, 192), outline=True, texture="marble")
        draw_voxel_box(surface, camera, x - 0.75, y - 0.75, 0.35, 1.5, 1.5, 0.12, (60, 120, 156), outline=False)
        draw_voxel_box(surface, camera, x - 0.2, y - 0.2, 0.35, 0.4, 0.4, 0.9, (226, 222, 212), outline=True)
        draw_voxel_box(surface, camera, x - 0.55, y - 0.55, 1.2, 1.1, 1.1, 0.14, (214, 210, 200), outline=True)
        draw_voxel_box(surface, camera, x - 0.12, y - 0.12, 1.34, 0.24, 0.24, 0.5, (232, 228, 218), outline=True)
        top = camera.apply(x, y, 1.9)
        for k in range(6):
            a = k * math.pi / 3.0
            pts = []
            for s in range(0, 9):
                f = s / 8.0
                pts.append(camera.apply(x + math.cos(a) * f * 0.9, y + math.sin(a) * f * 0.9, 1.9 + 0.55 * math.sin(f * math.pi) - 1.6 * f * f))
            pygame.draw.lines(surface, (170, 214, 240), False, pts, 2)
        for k in range(6):
            a = k * math.pi / 3.0 + time_val * 1.5
            fx, fy = camera.apply(x + math.cos(a) * 0.45, y + math.sin(a) * 0.45, 0.4)
            pygame.draw.circle(surface, (214, 236, 250), (fx, fy), 3)
        pygame.draw.circle(surface, (210, 236, 250), top, 5)


class HangingChain:
    """Corrente que pende do teto da gruta (decoração sem colisão); balança de leve."""

    def __init__(self, wx: float, wy: float, length: float = 3.2, top: float = 6.0):
        self.wx = wx
        self.wy = wy
        self.length = length
        self.top = top

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        sway = 0.12 * math.sin(time_val * 1.1 + self.wx * 0.7 + self.wy)
        links = int(self.length / 0.28)
        prev = camera.apply(self.wx, self.wy, self.top)
        for i in range(1, links + 1):
            f = i / links
            pos = camera.apply(self.wx + sway * f, self.wy + sway * 0.6 * f, self.top - self.length * f)
            pygame.draw.line(surface, (62, 58, 76), prev, pos, 3)
            pygame.draw.circle(surface, (130, 124, 150) if i % 2 else (88, 84, 106), pos, 3, 1)
            prev = pos
        pygame.draw.circle(surface, (150, 120, 190), prev, 4)


class IncenseBurner:
    """Incensário de bronze sobre base de pedra que solta fumaça fina e perfumada (a névoa de incenso)."""

    RATE = 5.0  # partículas por segundo

    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self._carry = random.random()

    def tick(self, arena, dt: float, fighters: list, camera, particles: list, banners: list):
        if particles is None:
            return
        self._carry += dt * self.RATE
        while self._carry >= 1.0:
            self._carry -= 1.0
            from src.effects.particles import SmokeParticle
            particles.append(SmokeParticle(self.wx, self.wy, wz=0.75, color=(206, 198, 214), radius=0.32, lifetime=random.uniform(1.8, 2.6)))

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x, y = self.wx, self.wy
        draw_voxel_box(surface, camera, x - 0.24, y - 0.24, 0.0, 0.48, 0.48, 0.20, (96, 92, 88), outline=True)
        draw_voxel_box(surface, camera, x - 0.17, y - 0.17, 0.20, 0.34, 0.34, 0.26, (150, 112, 52), outline=True)
        draw_voxel_box(surface, camera, x - 0.21, y - 0.21, 0.44, 0.42, 0.42, 0.06, (178, 138, 66), outline=False)
        glow = 0.6 + 0.4 * math.sin(time_val * 3.0 + x)
        draw_voxel_box(surface, camera, x - 0.08, y - 0.08, 0.50, 0.16, 0.16, 0.05, (int(255 * glow), int(90 * glow), 40), outline=False)
