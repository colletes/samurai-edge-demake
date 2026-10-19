"""Props decorativos sem colisão das arenas temáticas: lanternas de papel, faixas, nobori e incensário (6.3.6)."""
import math
import random

import pygame

from src.isometric.voxel_renderer import draw_voxel_box
from src.world.obstacles import AncientTree, Rock, ToriiGate

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
    para projéteis; destrutível por golpes melee ou projéteis pesados.
    """

    def __init__(self, wx: float, wy: float, axis: str = "x", tilt: float = 1.0):
        super().__init__(wx, wy, radius=0.5, height=1.7)
        self.axis = axis
        self.tilt = tilt
        self.is_broken = False
        self.splinters = []

    def check_collision(self, px: float, py: float, p_radius: float = 0.3) -> tuple[bool, float, float]:
        if self.is_broken:
            return False, 0.0, 0.0
        return super().check_collision(px, py, p_radius)

    def break_panel(self, slash_dir: tuple[float, float] = (1.0, 0.0), particles: list = None):
        """Destrói o painel de biombo, estilhaçando madeira e papel shoji."""
        if self.is_broken:
            return
        self.is_broken = True
        self.radius = 0.0  # desativa colisão física
        self.height = 0.12

        # Gerar estilhaços visuais no chão
        dx, dy = slash_dir
        for _ in range(8):
            ox = random.uniform(-0.35, 0.35) + dx * 0.15
            oy = random.uniform(-0.35, 0.35) + dy * 0.15
            self.splinters.append((ox, oy, random.choice([(214, 176, 72), (44, 30, 26), (230, 220, 195)])))

        if particles is not None:
            from src.effects.particles import SparkParticle
            for _ in range(12):
                particles.append(SparkParticle(self.wx, self.wy, 0.35, color=(240, 205, 120)))

        try:
            from src.audio.sound_manager import get_sound_manager
            from src.audio.sound_events import SoundEvent
            sm = get_sound_manager()
            if sm:
                sm.play(SoundEvent.OBSTACLE_HIT)
        except Exception:
            pass

    def render(self, surface: pygame.Surface, camera):
        x, y = self.wx, self.wy
        gx, gy = camera.apply(x, y, 0.0)

        if self.is_broken:
            # Painel destruído: armação de madeira partida e retalhos de papel dourado no solo
            pygame.draw.ellipse(surface, (45, 30, 22), (gx - 24, gy - 10, 48, 20))
            w, t = 0.75, 0.12
            if self.axis == "x":
                draw_voxel_box(surface, camera, x - w / 2, y - t / 2, 0.01, w, t, 0.05, (44, 30, 26), outline=False)
            else:
                draw_voxel_box(surface, camera, x - t / 2, y - w / 2, 0.01, t, w, 0.05, (44, 30, 26), outline=False)
            for ox, oy, col in self.splinters:
                draw_voxel_box(surface, camera, x + ox - 0.08, y + oy - 0.08, 0.02, 0.16, 0.16, 0.04, col, outline=False)
            return

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
    """Cortina do teatro kabuki / noren de Yoshiwara: faixas verticais translúcidas penduradas."""

    PALETTE = ((28, 26, 30), (230, 104, 42), (44, 124, 74))

    def __init__(self, wx: float, wy: float, length: float = 6.0, axis: str = "x", height: float = 3.2, drop: float = 3.0, alpha: int = 115):
        self.wx, self.wy, self.length, self.axis, self.height, self.drop = wx, wy, length, axis, height, drop
        self.alpha = alpha
        self.cx = wx + (length / 2 if axis == "x" else 0.0)
        self.cy = wy + (length / 2 if axis == "y" else 0.0)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        n = max(3, int(self.length / 0.8))
        top, bottom = self.height, self.height - self.drop
        draw = lambda a, z, sway=0.0: camera.apply(self.wx + (a if self.axis == "x" else sway), self.wy + (a if self.axis == "y" else sway), z)
        p_top_start = draw(0.0, top + 0.05)
        p_top_end = draw(self.length, top + 0.05)
        pygame.draw.line(surface, (70, 50, 34), p_top_start, p_top_end, 4)

        quads = []
        min_x, max_x = surface.get_width(), 0
        min_y, max_y = surface.get_height(), 0
        for i in range(n):
            a0, a1 = self.length * i / n, self.length * (i + 1) / n
            sway = 0.05 * math.sin(time_val * 1.4 + i * 0.7)
            q = [draw(a0, top), draw(a1, top), draw(a1, bottom + sway), draw(a0, bottom + sway)]
            quads.append((q, self.PALETTE[i % 3]))
            for pt in q:
                min_x = min(min_x, pt[0])
                max_x = max(max_x, pt[0])
                min_y = min(min_y, pt[1])
                max_y = max(max_y, pt[1])

        bw = int(max_x - min_x + 8)
        bh = int(max_y - min_y + 8)
        if bw > 0 and bh > 0:
            c_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            ox, oy = min_x - 4, min_y - 4
            for q, col in quads:
                local_q = [(pt[0] - ox, pt[1] - oy) for pt in q]
                pygame.draw.polygon(c_surf, (*col, self.alpha), local_q)
                pygame.draw.polygon(c_surf, (16, 14, 18, int(self.alpha * 0.7)), local_q, 1)
            surface.blit(c_surf, (ox, oy))


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


class VoxelCricket:
    """Grilo em arte voxel que habita o templo e jardins da floresta.
    Salta suavemente pelo piso e canta com sutis partículas sonoras."""

    def __init__(self, wx: float, wy: float, seed: int = 12):
        self.home_x = wx
        self.home_y = wy
        self.wx = wx
        self.wy = wy
        self.seed = seed
        self.color = random.Random(seed).choice([(52, 68, 38), (44, 58, 32), (64, 52, 36)])

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        t = time_val + self.seed * 3.7
        cycle = t % 4.0
        hop_phase = max(0.0, min(1.0, (cycle - 2.8) / 0.5)) if cycle >= 2.8 and cycle < 3.3 else 0.0

        angle = math.sin(self.seed * 7.1) * 3.14
        hop_dist = 0.55 * hop_phase
        x = self.home_x + math.cos(angle) * (math.sin(t * 0.3) * 0.8 + hop_dist)
        y = self.home_y + math.sin(angle) * (math.cos(t * 0.3) * 0.8 + hop_dist)
        z = math.sin(hop_phase * math.pi) * 0.28 if hop_phase > 0 else 0.0

        gx, gy = camera.apply(x, y, 0.0)
        pygame.draw.ellipse(surface, (20, 24, 20), (gx - 5, gy - 2, 10, 4))

        draw_voxel_box(surface, camera, x - 0.06, y - 0.06, z, 0.12, 0.12, 0.08, self.color, outline=False)
        draw_voxel_box(surface, camera, x - 0.03, y - 0.03, z + 0.06, 0.06, 0.06, 0.05, (70, 85, 45), outline=False)

        if cycle < 1.0 and int(t * 8) % 3 == 0:
            rx = int(camera.zoom * 8)
            ry = int(rx * 0.5)
            chirp_surf = pygame.Surface((rx * 2 + 4, ry * 2 + 4), pygame.SRCALPHA)
            pygame.draw.ellipse(chirp_surf, (200, 240, 140, 90), (2, 2, rx * 2, ry * 2), 1)
            surface.blit(chirp_surf, (gx - rx - 2, gy - ry - 2))


class VoxelSparrow:
    """Pássaro silvestre em voxel (Pardal dos templos montanhosos).
    Cisca no cascalho dos jardins zen e revoa graciosamente quando há aproximação."""

    def __init__(self, wx: float, wy: float, seed: int = 42):
        self.home_x = wx
        self.home_y = wy
        self.wx = wx
        self.wy = wy
        self.seed = seed
        self.feather_col = random.Random(seed).choice([(138, 92, 58), (120, 80, 52), (150, 106, 68)])
        self.chest_col = (225, 218, 204)
        self.beak_col = (235, 180, 45)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        t = time_val + self.seed * 5.3
        flight_cycle = (t * 0.25) % 1.0
        is_flying = flight_cycle > 0.65

        if is_flying:
            flight_prog = (flight_cycle - 0.65) / 0.35
            fly_angle = flight_prog * math.pi * 2.0
            x = self.home_x + math.cos(fly_angle) * 1.8
            y = self.home_y + math.sin(fly_angle) * 1.2
            z = 0.5 + math.sin(flight_prog * math.pi) * 1.2
            wing_flap = math.sin(t * 35.0) * 0.12
        else:
            hop = max(0.0, math.sin(t * 1.8) - 0.7) * 0.2
            x = self.home_x + math.sin(t * 0.5) * 0.25
            y = self.home_y + math.cos(t * 0.5) * 0.25
            z = hop
            wing_flap = 0.0

        gx, gy = camera.apply(x, y, 0.0)
        s_size = max(4, int(12 * (1.0 - min(1.0, z / 2.0))))
        pygame.draw.ellipse(surface, (25, 28, 25), (gx - s_size // 2, gy - s_size // 4, s_size, max(2, s_size // 2)))

        draw_voxel_box(surface, camera, x - 0.08, y - 0.08, z, 0.16, 0.16, 0.12, self.feather_col, outline=False)
        draw_voxel_box(surface, camera, x - 0.06, y - 0.06, z, 0.12, 0.12, 0.07, self.chest_col, outline=False)
        draw_voxel_box(surface, camera, x - 0.05, y - 0.05, z + 0.09, 0.10, 0.10, 0.09, self.feather_col, outline=False)
        draw_voxel_box(surface, camera, x + 0.05, y - 0.02, z + 0.11, 0.05, 0.04, 0.04, self.beak_col, outline=False)
        if is_flying:
            draw_voxel_box(surface, camera, x - 0.14, y - 0.05, z + 0.06 + wing_flap, 0.06, 0.14, 0.03, self.feather_col, outline=False)
            draw_voxel_box(surface, camera, x + 0.08, y - 0.05, z + 0.06 - wing_flap, 0.06, 0.14, 0.03, self.feather_col, outline=False)


# ---------------------------------------------------------------------------
# Props Temáticos do Ciclo 3 (Arrozais de Goro e Moinho na Chuva de Ichi)
# ---------------------------------------------------------------------------

class Scarecrow:
    """Espantalho rústico de palha dos arrozais (Kakashi tradicional japonês).
    Mastro cruciforme de bambu com túnica de cânhamo esfarrapada e chapéu de palha kedge."""

    def __init__(self, wx: float, wy: float, seed: int = 101):
        self.wx = wx
        self.wy = wy
        self.seed = seed
        self.tunic_col = (110, 85, 60) if seed % 2 == 0 else (75, 80, 105)
        self.straw_col = (210, 185, 120)
        self.hat_col = (185, 150, 95)
        self.wood_col = (90, 65, 42)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x, y = self.wx, self.wy
        wind_sway = math.sin(time_val * 2.0 + self.seed) * 0.04

        # Mastro vertical
        draw_voxel_box(surface, camera, x - 0.04, y - 0.04, 0.0, 0.08, 0.08, 1.8, self.wood_col, outline=True)
        # Travessa horizontal dos braços
        draw_voxel_box(surface, camera, x - 0.65, y - 0.04 + wind_sway, 1.25, 1.30, 0.08, 0.08, self.wood_col, outline=True)
        # Corpo / Túnica de palha e pano
        draw_voxel_box(surface, camera, x - 0.22, y - 0.12 + wind_sway, 0.60, 0.44, 0.24, 0.70, self.tunic_col, outline=True)
        # Manga esquerda e direita
        draw_voxel_box(surface, camera, x - 0.60, y - 0.08 + wind_sway * 1.5, 1.15, 0.38, 0.16, 0.20, self.tunic_col, outline=False)
        draw_voxel_box(surface, camera, x + 0.22, y - 0.08 - wind_sway * 1.5, 1.15, 0.38, 0.16, 0.20, self.tunic_col, outline=False)
        # Tufos de palha saindo das pontas dos braços
        draw_voxel_box(surface, camera, x - 0.72, y - 0.06 + wind_sway * 1.8, 1.18, 0.14, 0.12, 0.14, self.straw_col, outline=False)
        draw_voxel_box(surface, camera, x + 0.58, y - 0.06 - wind_sway * 1.8, 1.18, 0.14, 0.12, 0.14, self.straw_col, outline=False)
        # Cabeça redonda de palha
        draw_voxel_box(surface, camera, x - 0.14, y - 0.14 + wind_sway * 0.5, 1.35, 0.28, 0.28, 0.30, self.straw_col, outline=True)
        # Chapéu cônico de palha (Kasa)
        draw_voxel_box(surface, camera, x - 0.30, y - 0.30 + wind_sway * 0.5, 1.62, 0.60, 0.60, 0.08, self.hat_col, outline=True)
        draw_voxel_box(surface, camera, x - 0.18, y - 0.18 + wind_sway * 0.5, 1.70, 0.36, 0.36, 0.10, self.hat_col, outline=False)
        draw_voxel_box(surface, camera, x - 0.08, y - 0.08 + wind_sway * 0.5, 1.80, 0.16, 0.16, 0.08, self.hat_col, outline=False)


class HayBale:
    """Fardo rústico de feno/palha de arroz seco colhido."""

    def __init__(self, wx: float, wy: float, seed: int = 1):
        self.wx = wx
        self.wy = wy
        self.radius = 0.45
        self.straw_main = (205, 175, 105) if seed % 2 == 0 else (190, 160, 95)
        self.straw_shade = (165, 135, 75)
        self.rope_col = (90, 65, 40)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x, y = self.wx, self.wy
        # Bloco de palha
        draw_voxel_box(surface, camera, x - 0.40, y - 0.30, 0.0, 0.80, 0.60, 0.55, self.straw_main, outline=True)
        # Camada superior texturizada
        draw_voxel_box(surface, camera, x - 0.36, y - 0.26, 0.55, 0.72, 0.52, 0.08, self.straw_shade, outline=False)
        # Cordas de amarração
        draw_voxel_box(surface, camera, x - 0.18, y - 0.32, 0.0, 0.05, 0.64, 0.58, self.rope_col, outline=False)
        draw_voxel_box(surface, camera, x + 0.13, y - 0.32, 0.0, 0.05, 0.64, 0.58, self.rope_col, outline=False)

    def check_collision(self, px: float, py: float, p_radius: float = 0.3) -> tuple[bool, float, float]:
        dist = math.hypot(px - self.wx, py - self.wy)
        min_dist = self.radius + p_radius
        if dist < min_dist:
            overlap = min_dist - dist
            if dist > 0.0001:
                nx = (px - self.wx) / dist
                ny = (py - self.wy) / dist
            else:
                nx, ny = 1.0, 0.0
            return True, nx * overlap, ny * overlap
        return False, 0.0, 0.0


class WaterMillWheel:
    """Roda d'água monumental de madeira do moinho abandonado na chuva.
    Gira continuamente impulsionada pelo fluxo do riacho, com respingos e pás de madeira."""

    def __init__(self, wx: float, wy: float, radius: float = 1.6, speed: float = 1.2):
        self.wx = wx
        self.wy = wy
        self.wheel_radius = radius
        self.width = 1.0
        self.depth = 1.4
        self.height = radius * 2.0
        self.speed = speed
        self.wood_rim = (85, 60, 42)
        self.wood_spoke = (115, 85, 55)
        self.iron_hub = (45, 45, 50)
        self.water_splash = (180, 220, 255)

    def check_collision(self, px: float, py: float, p_radius: float = 0.3) -> tuple[bool, float, float]:
        half_w = 0.4
        half_d = 0.7
        min_x, max_x = self.wx - half_w, self.wx + half_w
        min_y, max_y = self.wy - half_d, self.wy + half_d
        closest_x = max(min_x, min(px, max_x))
        closest_y = max(min_y, min(py, max_y))
        dx = px - closest_x
        dy = py - closest_y
        dist = math.hypot(dx, dy)
        if dist >= p_radius:
            return False, 0.0, 0.0
        if dist > 0.0001:
            overlap = p_radius - dist
            return True, dx / dist * overlap, dy / dist * overlap
        return True, 0.0, p_radius

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        cx, cy = self.wx, self.wy
        hub_z = self.wheel_radius * 0.85
        rot_angle = time_val * self.speed

        # Eixo central de ferro/carvalho apoiado no solo
        draw_voxel_box(surface, camera, cx - 0.15, cy - 0.45, hub_z - 0.15, 0.30, 0.90, 0.30, self.iron_hub, outline=True)

        # Suportes angulares de madeira cravados na margem
        draw_voxel_box(surface, camera, cx - 0.12, cy - 0.40, 0.0, 0.24, 0.18, hub_z, self.wood_rim, outline=True)
        draw_voxel_box(surface, camera, cx - 0.12, cy + 0.22, 0.0, 0.24, 0.18, hub_z, self.wood_rim, outline=True)

        # 8 Raios e Pás de madeira giratórias
        for i in range(8):
            ang = rot_angle + i * (math.pi / 4.0)
            dx = math.cos(ang) * (self.wheel_radius * 0.85)
            dz = math.sin(ang) * (self.wheel_radius * 0.85)

            # Pá de madeira
            blade_x = cx + dx
            blade_z = hub_z + dz
            if blade_z >= 0.0:
                draw_voxel_box(surface, camera, blade_x - 0.12, cy - 0.35, blade_z - 0.06, 0.24, 0.70, 0.12, self.wood_spoke, outline=False)

                # Respingos de água na parte inferior da roda ao tocar a correnteza
                if blade_z < 0.35 and math.sin(time_val * 15.0 + i) > 0.0:
                    splash_size = 0.08
                    draw_voxel_box(surface, camera, blade_x - 0.06, cy - 0.25, 0.05, splash_size, 0.50, splash_size, self.water_splash, outline=False)

        # Aro exterior circular da roda (segmentos)
        for i in range(12):
            ang = rot_angle + i * (math.pi / 6.0)
            rx = cx + math.cos(ang) * self.wheel_radius
            rz = hub_z + math.sin(ang) * self.wheel_radius
            if rz >= 0.0:
                draw_voxel_box(surface, camera, rx - 0.08, cy - 0.32, rz - 0.08, 0.16, 0.64, 0.16, self.wood_rim, outline=False)


class DuneGrass:
    """Tufos de capim costeiro de duna que balançam com a brisa oceânica (Ilha Ganryū)."""

    def __init__(self, wx: float, wy: float, seed: int = 5):
        self.wx = wx
        self.wy = wy
        self.seed = seed
        self.grass_col = (118, 142, 86) if seed % 2 == 0 else (135, 155, 96)
        self.grass_tip = (175, 190, 125)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        x, y = self.wx, self.wy
        wind_sway = math.sin(time_val * 3.5 + self.seed * 1.7) * 0.06
        # Haste central e ramificações
        draw_voxel_box(surface, camera, x - 0.10, y - 0.10, 0.0, 0.20, 0.20, 0.25, self.grass_col, outline=False)
        draw_voxel_box(surface, camera, x - 0.08 + wind_sway, y - 0.08, 0.25, 0.16, 0.16, 0.30, self.grass_col, outline=False)
        draw_voxel_box(surface, camera, x - 0.05 + wind_sway * 1.8, y - 0.05, 0.55, 0.10, 0.10, 0.20, self.grass_tip, outline=False)


class GojoRailing:
    """Balustrada clássica da Ponte Gojo: traves de madeira de cedro e postes com pontas de bronze (giboshi)."""

    def __init__(self, x0: float, x1: float, wy: float, height: float = 0.85):
        self.x0 = min(x0, x1)
        self.x1 = max(x0, x1)
        self.wx = (self.x0 + self.x1) * 0.5
        self.wy = wy
        self.height = height
        self.width = max(0.1, self.x1 - self.x0)
        self.depth = 0.30
        self.wood_beam = (68, 48, 32)
        self.wood_post = (56, 38, 24)
        self.giboshi_bronze = (172, 142, 68)
        self.giboshi_glow = (215, 185, 95)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        length = self.x1 - self.x0
        if length <= 0.1:
            return

        # 1. Trave horizontal superior (corrimão principal)
        draw_voxel_box(surface, camera, self.x0, self.wy - 0.08, self.height - 0.12, length, 0.16, 0.12, self.wood_beam, outline=True)

        # 2. Trave horizontal intermediária
        draw_voxel_box(surface, camera, self.x0, self.wy - 0.06, self.height * 0.45, length, 0.12, 0.10, self.wood_beam, outline=False)

        # 3. Postes verticais espaçados com topo ornamental Giboshi de bronze
        post_spacing = 1.8
        num_posts = max(2, int(round(length / post_spacing)) + 1)
        actual_step = length / (num_posts - 1) if num_posts > 1 else length

        for i in range(num_posts):
            px = self.x0 + i * actual_step
            # Poste maciço de madeira
            draw_voxel_box(surface, camera, px - 0.12, self.wy - 0.12, 0.0, 0.24, 0.24, self.height, self.wood_post, outline=True)

            # Giboshi (ornamento cônico/abaulado de bronze feudal sobre o poste)
            draw_voxel_box(surface, camera, px - 0.14, self.wy - 0.14, self.height, 0.28, 0.28, 0.08, self.giboshi_bronze, outline=False)
            draw_voxel_box(surface, camera, px - 0.10, self.wy - 0.10, self.height + 0.08, 0.20, 0.20, 0.12, self.giboshi_glow, outline=False)
            draw_voxel_box(surface, camera, px - 0.05, self.wy - 0.05, self.height + 0.20, 0.10, 0.10, 0.08, self.giboshi_bronze, outline=False)

    def check_collision(self, px: float, py: float, radius: float) -> tuple[bool, float, float]:
        """Bloqueia passagem de personagens contra a balustrada nos trechos protegidos da ponte."""
        if (self.x0 - radius * 0.5) <= px <= (self.x1 + radius * 0.5):
            dy = py - self.wy
            min_dist = radius + 0.20
            if abs(dy) < min_dist:
                sign = 1.0 if dy >= 0 else -1.0
                push_y = sign * (min_dist - abs(dy))
                return True, 0.0, push_y
        return False, 0.0, 0.0


class KagaribiBrazier(Rock):
    """Braseiro de ferro suspenso com fogo crepitante e brasas na noite de Kyoto."""

    def __init__(self, wx: float, wy: float, radius: float = 0.35, height: float = 1.3):
        super().__init__(wx, wy, radius, height)
        self.iron_dark = (36, 36, 42)
        self.iron_rim = (52, 54, 62)
        self.embers = (210, 75, 20)
        self.fire_core = (255, 195, 55)
        self.fire_tip = (255, 110, 25)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        # 1. Haste/Tripé de sustentação de ferro forjado
        draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, 0.0, 0.16, 0.16, 0.85, self.iron_dark, outline=True)
        # 2. Cesto de ferro vazado
        draw_voxel_box(surface, camera, self.wx - 0.30, self.wy - 0.30, 0.85, 0.60, 0.60, 0.25, self.iron_rim, outline=True)
        # 3. Leito de brasas incandescentes
        draw_voxel_box(surface, camera, self.wx - 0.24, self.wy - 0.24, 0.95, 0.48, 0.48, 0.12, self.embers, outline=False)

        # 4. Fogo animado em múltiplos voxels dançantes
        flicker1 = math.sin(time_val * 14.0 + self.wx * 3.0) * 0.06
        flicker2 = math.cos(time_val * 18.0 + self.wy * 3.0) * 0.06
        flame_h1 = 0.35 + math.sin(time_val * 20.0) * 0.10
        flame_h2 = 0.25 + math.cos(time_val * 24.0) * 0.08

        # Núcleo amarelo de chama
        draw_voxel_box(surface, camera, self.wx - 0.16 + flicker1, self.wy - 0.16 + flicker2, 1.05, 0.32, 0.32, flame_h1, self.fire_core, outline=False)
        # Pontas alaranjadas
        draw_voxel_box(surface, camera, self.wx - 0.10 - flicker2, self.wy - 0.10 + flicker1, 1.05 + flame_h1 * 0.6, 0.20, 0.20, flame_h2, self.fire_tip, outline=False)


class BladeCluster(Rock):
    """Feixe de espadas e lanças fincadas nas margens de pedra (As 999 Lâminas de Benkei)."""

    def __init__(self, wx: float, wy: float, seed: int = 1):
        super().__init__(wx, wy, radius=0.30, height=0.90)
        self.seed = seed
        self.blade_steel = (195, 205, 220)
        self.blade_edge = (240, 245, 255)
        self.tsuka_cord = (42, 28, 24) if seed % 2 == 0 else (120, 24, 24)
        self.tsuba_brass = (165, 135, 60)
        self.spear_wood = (88, 62, 42)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        # Base de pedras onde as lâminas estão cravadas
        draw_voxel_box(surface, camera, self.wx - 0.25, self.wy - 0.25, 0.0, 0.50, 0.50, 0.14, (64, 58, 54), outline=True)

        # Katana 1: ligeiramente inclinada para leste
        draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - 0.08, 0.12, 0.08, 0.06, 0.70, self.blade_steel, outline=False)
        draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.12, 0.82, 0.16, 0.14, 0.04, self.tsuba_brass, outline=False)
        draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.09, 0.86, 0.10, 0.08, 0.26, self.tsuka_cord, outline=False)

        # Lança Yari / Naginata: mais alta com haste de madeira
        draw_voxel_box(surface, camera, self.wx + 0.08, self.wy + 0.04, 0.12, 0.08, 0.08, 1.15, self.spear_wood, outline=False)
        draw_voxel_box(surface, camera, self.wx + 0.06, self.wy + 0.02, 1.27, 0.12, 0.06, 0.38, self.blade_edge, outline=False)

        # Katana 2: lâmina mais curta ou quebrada
        draw_voxel_box(surface, camera, self.wx - 0.14, self.wy + 0.08, 0.12, 0.07, 0.07, 0.48, self.blade_steel, outline=False)
        draw_voxel_box(surface, camera, self.wx - 0.18, self.wy + 0.04, 0.60, 0.14, 0.14, 0.04, self.tsuba_brass, outline=False)
        draw_voxel_box(surface, camera, self.wx - 0.15, self.wy + 0.06, 0.64, 0.08, 0.08, 0.22, (28, 36, 48), outline=False)


class BridgeSupport:
    """Pilares maciços de sustentação da ponte descendo até o leito do rio."""

    def __init__(self, wx: float, wy: float, depth: float = 0.8):
        self.wx = wx
        self.wy = wy
        self.depth = depth
        self.wood_color = (48, 36, 26)
        self.wood_shadow = (32, 24, 18)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        # Pilar descendo de z=0 até o fundo do rio
        draw_voxel_box(surface, camera, self.wx - 0.22, self.wy - 0.22, -self.depth, 0.44, 0.44, self.depth, self.wood_color, outline=True)
        # Travessão transversal
        draw_voxel_box(surface, camera, self.wx - 0.30, self.wy - 0.30, -0.20, 0.60, 0.60, 0.15, self.wood_shadow, outline=False)


class WaterChute:
    """Vertedouro e calha de bambu com fluxo d'água animado entre os patamares dos arrozais."""

    def __init__(self, wx: float, wy: float, z_top: float = 0.28, z_bottom: float = 0.14, length: float = 1.0):
        self.wx = wx
        self.wy = wy
        self.z_top = z_top
        self.z_bottom = z_bottom
        self.length = length
        self.bamboo_col = (72, 115, 54)
        self.water_col = (130, 180, 225)
        self.water_foam = (215, 235, 255)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        # Calha de bambu cortada
        h_diff = self.z_top - self.z_bottom
        draw_voxel_box(surface, camera, self.wx - 0.18, self.wy - 0.10, self.z_bottom, 0.36, 0.20, h_diff + 0.05, self.bamboo_col, outline=True)

        # Lâmina d'água fluindo com oscilação procedural
        flow = math.sin(time_val * 16.0 + self.wx * 5.0) * 0.02
        draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.08, self.z_bottom + flow, 0.24, 0.16, h_diff, self.water_col, outline=False)

        # Espuma no ponto de queda inferior
        foam_size = 0.22 + math.sin(time_val * 22.0) * 0.04
        draw_voxel_box(surface, camera, self.wx - foam_size * 0.5, self.wy + 0.10, self.z_bottom, foam_size, 0.15, 0.04, self.water_foam, outline=False)


# =============================================================================
# PROPS DO CICLO 4: CEMITÉRIO GÓTICO (VALERIUS) & SANTUÁRIO HEIAN (SEIMEI)
# =============================================================================

class GothicHeadstone(Rock):
    """Lápide gótica esculpida em granito escuro com detalhes de cruz latina ou arco pontiagudo."""

    def __init__(self, wx: float, wy: float, style: str = "cross", seed: int = 1):
        super().__init__(wx, wy, radius=0.38, height=1.1)
        self.style = style
        self.seed = seed
        self.stone_dark = (48, 50, 56)
        self.stone_mid = (65, 68, 76)
        self.stone_hi = (92, 96, 108)
        self.moss = (42, 60, 48)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        # 1. Base / Plinto de cantaria no solo
        draw_voxel_box(surface, camera, self.wx - 0.32, self.wy - 0.22, 0.0, 0.64, 0.44, 0.14, self.stone_dark, outline=True)
        # 2. Degrau intermediário
        draw_voxel_box(surface, camera, self.wx - 0.24, self.wy - 0.16, 0.14, 0.48, 0.32, 0.10, self.stone_mid, outline=True)

        if self.style == "cross":
            # Haste vertical da cruz
            draw_voxel_box(surface, camera, self.wx - 0.07, self.wy - 0.07, 0.24, 0.14, 0.14, 0.82, self.stone_hi, outline=True)
            # Braço horizontal transversal
            draw_voxel_box(surface, camera, self.wx - 0.26, self.wy - 0.06, 0.68, 0.52, 0.12, 0.15, self.stone_hi, outline=True)
            # Detalhe de musgo gótico na junção
            draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, 0.22, 0.16, 0.16, 0.08, self.moss, outline=False)
        else:
            # Lápide retangular em arco barroco
            draw_voxel_box(surface, camera, self.wx - 0.20, self.wy - 0.10, 0.24, 0.40, 0.20, 0.60, self.stone_hi, outline=True)
            # Arco pontiagudo superior
            draw_voxel_box(surface, camera, self.wx - 0.14, self.wy - 0.08, 0.84, 0.28, 0.16, 0.18, self.stone_mid, outline=True)
            # Friso entalhado de cruz no relevo
            draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - 0.11, 0.40, 0.08, 0.04, 0.32, (120, 126, 140), outline=False)
            draw_voxel_box(surface, camera, self.wx - 0.10, self.wy - 0.11, 0.54, 0.20, 0.04, 0.08, (120, 126, 140), outline=False)


class MausoleumCrypt:
    """Mausoléu barroco/gótico monumental: colunas clássicas, frontão triangular e portão de ferro forjado."""

    def __init__(self, wx: float, wy: float, width: float = 2.4, depth: float = 1.8, height: float = 2.3):
        self.wx = wx
        self.wy = wy
        self.width = width
        self.depth = depth
        self.height = height
        self.stone_dark = (36, 38, 44)
        self.stone_wall = (54, 58, 66)
        self.stone_column = (75, 80, 92)
        self.roof_pediment = (44, 48, 56)
        self.iron_bars = (28, 30, 36)
        self.spectral_glow = (50, 190, 160)

    def check_collision(self, px: float, py: float, p_radius: float = 0.3) -> tuple[bool, float, float]:
        from src.world.solid_props import aabb_circle_collision
        return aabb_circle_collision((self.wx, self.wy, self.wx + self.width, self.wy + self.depth), px, py, p_radius)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        w, d = self.width, self.depth
        x, y = self.wx, self.wy

        # 1. Base monumental de pedra chanfrada
        draw_voxel_box(surface, camera, x - 0.10, y - 0.10, 0.0, w + 0.20, d + 0.20, 0.22, self.stone_dark, outline=True)

        # 2. Paredes sólidas da câmara sepulcral (traseira e laterais)
        draw_voxel_box(surface, camera, x, y, 0.22, w, d, 1.45, self.stone_wall, outline=True)

        # 3. Portal escuro em nicho frontal
        portal_w = 0.85
        portal_x = x + (w - portal_w) * 0.5
        draw_voxel_box(surface, camera, portal_x, y - 0.02, 0.22, portal_w, 0.20, 1.30, (14, 16, 20), outline=True)

        # Brilho espectral verde-esmeralda fúnebre no fundo do portal
        glow_pulse = 0.85 + 0.15 * math.sin(time_val * 4.0 + x)
        glow_col = tuple(int(c * glow_pulse) for c in self.spectral_glow)
        draw_voxel_box(surface, camera, portal_x + 0.15, y + 0.05, 0.40, portal_w - 0.30, 0.08, 0.70, glow_col, outline=False)

        # Grades verticais de ferro forjado no portal
        for i in range(4):
            bx = portal_x + 0.12 + i * 0.20
            draw_voxel_box(surface, camera, bx, y - 0.04, 0.22, 0.05, 0.05, 1.30, self.iron_bars, outline=False)

        # 4. Colunas toscanas frontais (esquerda e direita do portal)
        col_r = 0.18
        draw_voxel_box(surface, camera, x + 0.12, y - 0.05, 0.22, col_r * 2, col_r * 2, 1.50, self.stone_column, outline=True)
        draw_voxel_box(surface, camera, x + w - col_r * 2 - 0.12, y - 0.05, 0.22, col_r * 2, col_r * 2, 1.50, self.stone_column, outline=True)

        # 5. Entablamento e arquitrave sobre as colunas
        draw_voxel_box(surface, camera, x - 0.06, y - 0.08, 1.67, w + 0.12, d + 0.16, 0.20, self.stone_column, outline=True)

        # 6. Frontão triangular do telhado barroco (pediment)
        draw_voxel_box(surface, camera, x - 0.02, y - 0.04, 1.87, w + 0.04, d + 0.08, 0.26, self.roof_pediment, outline=True)
        draw_voxel_box(surface, camera, x + 0.30, y + 0.10, 2.13, w - 0.60, d - 0.20, 0.20, self.roof_pediment, outline=True)

        # 7. Cruz monumental de pedra no ápice
        cross_cx = x + w * 0.5
        draw_voxel_box(surface, camera, cross_cx - 0.06, y + 0.15, 2.33, 0.12, 0.12, 0.55, self.stone_column, outline=True)
        draw_voxel_box(surface, camera, cross_cx - 0.20, y + 0.16, 2.65, 0.40, 0.10, 0.12, self.stone_column, outline=True)


class WroughtIronFence(Rock):
    """Gradil de ferro forjado gótico com lanças pontiagudas para divisão dos túmulos."""

    def __init__(self, wx: float, wy: float, length: float = 1.2, orientation: str = "x"):
        super().__init__(wx, wy, radius=0.40, height=1.1)
        self.length = length
        self.orientation = orientation
        self.iron_col = (34, 36, 42)
        self.iron_post = (46, 48, 56)
        self.iron_tip = (82, 86, 98)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        half_l = self.length * 0.5
        if self.orientation == "x":
            # Dois postes robustos nas extremidades
            draw_voxel_box(surface, camera, self.wx - half_l, self.wy - 0.08, 0.0, 0.16, 0.16, 1.05, self.iron_post, outline=True)
            draw_voxel_box(surface, camera, self.wx + half_l - 0.16, self.wy - 0.08, 0.0, 0.16, 0.16, 1.05, self.iron_post, outline=True)
            # Trilhos horizontais
            draw_voxel_box(surface, camera, self.wx - half_l, self.wy - 0.04, 0.25, self.length, 0.08, 0.06, self.iron_col, outline=False)
            draw_voxel_box(surface, camera, self.wx - half_l, self.wy - 0.04, 0.85, self.length, 0.08, 0.06, self.iron_col, outline=False)
            # Lanças verticais finas com pontas afiadas
            n = 5
            step = (self.length - 0.3) / max(1, n - 1)
            for i in range(n):
                px = self.wx - half_l + 0.15 + i * step
                draw_voxel_box(surface, camera, px - 0.03, self.wy - 0.03, 0.0, 0.06, 0.06, 0.95, self.iron_col, outline=False)
                draw_voxel_box(surface, camera, px - 0.04, self.wy - 0.04, 0.95, 0.08, 0.08, 0.15, self.iron_tip, outline=False)
        else:
            # Orientação Y
            draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - half_l, 0.0, 0.16, 0.16, 1.05, self.iron_post, outline=True)
            draw_voxel_box(surface, camera, self.wx - 0.08, self.wy + half_l - 0.16, 0.0, 0.16, 0.16, 1.05, self.iron_post, outline=True)
            draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - half_l, 0.25, 0.08, self.length, 0.06, self.iron_col, outline=False)
            draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - half_l, 0.85, 0.08, self.length, 0.06, self.iron_col, outline=False)
            n = 5
            step = (self.length - 0.3) / max(1, n - 1)
            for i in range(n):
                py = self.wy - half_l + 0.15 + i * step
                draw_voxel_box(surface, camera, self.wx - 0.03, py - 0.03, 0.0, 0.06, 0.06, 0.95, self.iron_col, outline=False)
                draw_voxel_box(surface, camera, self.wx - 0.04, py - 0.04, 0.95, 0.08, 0.08, 0.15, self.iron_tip, outline=False)


class GothicDeadTree(AncientTree):
    """Árvore fúnebre gótica desfolhada: tronco retorcido, nós negros e galhos secos estendidos sob o luar."""

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy)
        self.radius = 0.55
        self.wood_dark = (32, 28, 30)
        self.wood_bark = (48, 42, 45)
        self.wood_branch = (62, 54, 58)

    def render(self, surface: pygame.Surface, camera):
        # 1. Raízes ossudas cravadas no solo do cemitério
        draw_voxel_box(surface, camera, self.wx - 0.60, self.wy - 0.40, 0.0, 0.40, 0.30, 0.20, self.wood_dark, outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.25, self.wy - 0.35, 0.0, 0.35, 0.35, 0.18, self.wood_dark, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.30, self.wy + 0.28, 0.0, 0.35, 0.30, 0.18, self.wood_dark, outline=True)

        # 2. Tronco retorcido ascendente
        draw_voxel_box(surface, camera, self.wx - 0.40, self.wy - 0.40, 0.0, 0.80, 0.80, 0.75, self.wood_bark, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.30, self.wy - 0.28, 0.70, 0.60, 0.56, 0.80, self.wood_bark, outline=True)

        # 3. Bifurcações e galhos secos desfolhados angulados
        # Galho Noroeste
        draw_voxel_box(surface, camera, self.wx - 0.70, self.wy - 0.45, 1.45, 0.45, 0.35, 0.38, self.wood_branch, outline=True)
        draw_voxel_box(surface, camera, self.wx - 1.10, self.wy - 0.60, 1.80, 0.50, 0.30, 0.30, self.wood_branch, outline=True)
        draw_voxel_box(surface, camera, self.wx - 1.45, self.wy - 0.75, 2.05, 0.40, 0.22, 0.22, self.wood_dark, outline=False)

        # Galho Sudeste
        draw_voxel_box(surface, camera, self.wx + 0.25, self.wy - 0.20, 1.45, 0.50, 0.40, 0.38, self.wood_branch, outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.70, self.wy - 0.10, 1.80, 0.55, 0.30, 0.28, self.wood_branch, outline=True)
        draw_voxel_box(surface, camera, self.wx + 1.15, self.wy - 0.05, 2.05, 0.45, 0.20, 0.20, self.wood_dark, outline=False)

        # Haste central retorcida erguida
        draw_voxel_box(surface, camera, self.wx - 0.20, self.wy - 0.18, 1.50, 0.40, 0.36, 0.90, self.wood_bark, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.12, 2.35, 0.24, 0.24, 0.70, self.wood_branch, outline=True)


class HeianTorii(ToriiGate):
    """Portal Torii cerimonial da era Heian: laca vermelha vermilion brilhante, sapatas negras e bronzes dourados."""

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy)
        self.c_vermilion = (215, 38, 28)
        self.c_vermilion_hi = (240, 55, 42)
        self.c_black_shoe = (24, 22, 26)
        self.c_gold_bracket = (225, 180, 52)

    def render(self, surface: pygame.Surface, camera):
        col_h = 3.3

        # Sapatas negras de laca (Kamebara / Daiishi)
        draw_voxel_box(surface, camera, self.wx - 1.35, self.wy - 0.25, 0.0, 0.50, 0.50, 0.35, self.c_black_shoe, outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.85, self.wy - 0.25, 0.0, 0.50, 0.50, 0.35, self.c_black_shoe, outline=True)

        # Anéis de bronze dourado na transição
        draw_voxel_box(surface, camera, self.wx - 1.30, self.wy - 0.20, 0.35, 0.40, 0.40, 0.08, self.c_gold_bracket, outline=False)
        draw_voxel_box(surface, camera, self.wx + 0.90, self.wy - 0.20, 0.35, 0.40, 0.40, 0.08, self.c_gold_bracket, outline=False)

        # Colunas principais cilíndricas em vermilion nobre (Hashira)
        draw_voxel_box(surface, camera, self.wx - 1.28, self.wy - 0.18, 0.43, 0.36, 0.36, col_h - 0.43, self.c_vermilion, outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.92, self.wy - 0.18, 0.43, 0.36, 0.36, col_h - 0.43, self.c_vermilion, outline=True)

        # Travessa inferior (Nuki) com cunhas douradas
        draw_voxel_box(surface, camera, self.wx - 1.55, self.wy - 0.12, 2.35, 3.10, 0.24, 0.20, self.c_vermilion, outline=True)
        draw_voxel_box(surface, camera, self.wx - 1.58, self.wy - 0.13, 2.37, 0.08, 0.26, 0.16, self.c_gold_bracket, outline=False)
        draw_voxel_box(surface, camera, self.wx + 1.50, self.wy - 0.13, 2.37, 0.08, 0.26, 0.16, self.c_gold_bracket, outline=False)

        # Travessa superior principal (Kasagi & Shimagi) com curvatura imperial Heian
        draw_voxel_box(surface, camera, self.wx - 1.75, self.wy - 0.16, col_h + 0.10, 3.50, 0.32, 0.26, self.c_vermilion, outline=True)
        # Cumeeira preta de acabamento (Kasagi Top)
        draw_voxel_box(surface, camera, self.wx - 1.92, self.wy - 0.20, col_h + 0.34, 3.84, 0.40, 0.20, self.c_black_shoe, outline=True)
        # Encaixes dourados nas extremidades
        draw_voxel_box(surface, camera, self.wx - 1.95, self.wy - 0.21, col_h + 0.32, 0.15, 0.42, 0.22, self.c_gold_bracket, outline=False)
        draw_voxel_box(surface, camera, self.wx + 1.80, self.wy - 0.21, col_h + 0.32, 0.15, 0.42, 0.22, self.c_gold_bracket, outline=False)

        # Tábua central cerimonial com kanji de consagração (Gakuzuka)
        draw_voxel_box(surface, camera, self.wx - 0.16, self.wy - 0.10, 2.55, 0.32, 0.20, 0.78, self.c_black_shoe, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.11, 2.75, 0.16, 0.04, 0.40, self.c_gold_bracket, outline=False)


class GinkgoTree(AncientTree):
    """Árvore de Ginkgo Dourada de Heian: copa em camadas reluzentes de folhas âmbar e douradas."""

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy)
        self.radius = 0.85
        self.c_trunk = (68, 52, 38)
        self.c_gold_deep = (210, 160, 32)
        self.c_gold_mid = (245, 195, 42)
        self.c_gold_light = (255, 222, 70)
        self.c_gold_top = (255, 240, 120)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        # 1. Base sólida de tronco
        draw_voxel_box(surface, camera, self.wx - 0.45, self.wy - 0.45, 0.0, 0.90, 0.90, 0.80, self.c_trunk, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.36, self.wy - 0.34, 0.75, 0.72, 0.68, 0.85, self.c_trunk, outline=True)

        # 2. Camadas volumétricas de copa dourada de Ginkgo com oscilação sutil ao vento
        sway = math.sin(time_val * 2.0 + self.wx) * 0.04

        # Camada baixa ampla
        draw_voxel_box(surface, camera, self.wx - 1.40 + sway, self.wy - 1.30, 1.55, 2.80, 2.60, 0.75, self.c_gold_deep, outline=True, texture="foliage")
        # Camada média dourada
        draw_voxel_box(surface, camera, self.wx - 1.15 - sway, self.wy - 1.10, 2.25, 2.30, 2.20, 0.75, self.c_gold_mid, outline=True, texture="foliage")
        # Camada alta luminosa
        draw_voxel_box(surface, camera, self.wx - 0.85 + sway, self.wy - 0.80, 2.95, 1.70, 1.60, 0.65, self.c_gold_light, outline=True, texture="foliage")
        # Cúpula de topo reluzente
        draw_voxel_box(surface, camera, self.wx - 0.45, self.wy - 0.45, 3.55, 0.90, 0.90, 0.50, self.c_gold_top, outline=True)


class ShimenawaBanner:
    """Corda sagrada de palha de arroz trançada (Shimenawa) com papéis rituais em zigue-zague (Shide)."""

    def __init__(self, wx: float, wy: float, span: float = 4.0, z: float = 2.4, ribbons: int = 5,
                 x1: float | None = None, y1: float | None = None):
        if x1 is not None:
            self.x0 = wx
            self.y0 = wy
            self.x1 = x1
            self.y1 = wy if y1 is None else y1
            self.wx = (self.x0 + self.x1) * 0.5
            self.wy = (self.y0 + self.y1) * 0.5
        else:
            self.wx = wx
            self.wy = wy
            self.x0 = wx - span * 0.5
            self.x1 = wx + span * 0.5
            self.y0 = wy
            self.y1 = wy
        self.z = z
        self.ribbons = ribbons
        self.rope_col = (195, 175, 125)
        self.rope_core = (160, 140, 95)
        self.shide_col = (250, 250, 255)
        self.shide_shadow = (205, 210, 225)

    def _point(self, t: float, drop: float = 0.0, time_val: float = 0.0):
        sag = 0.28 * math.sin(math.pi * t)
        sway = 0.03 * math.sin(time_val * 2.5 + t * 4.0)
        return self.x0 + (self.x1 - self.x0) * t, self.y0 + (self.y1 - self.y0) * t, self.z - sag - drop + sway

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        n = 16
        pts = [camera.apply(*self._point(i / n, 0.0, time_val)) for i in range(n + 1)]
        # Corda trançada grossa
        pygame.draw.lines(surface, self.rope_core, False, pts, 4)
        pygame.draw.lines(surface, self.rope_col, False, pts, 2)

        # Shide (fitas rituais dobradas em zigue-zague)
        for i in range(1, self.ribbons + 1):
            t = i / (self.ribbons + 1)
            px, py, pz = self._point(t, 0.0, time_val)
            top = camera.apply(px, py, pz)
            p1 = camera.apply(px - 0.08, py, pz - 0.20)
            p2 = camera.apply(px + 0.08, py, pz - 0.38)
            p3 = camera.apply(px - 0.05, py, pz - 0.55)
            tip = camera.apply(px, py, pz - 0.68)
            pygame.draw.lines(surface, self.shide_shadow, False, [top, p1, p2, p3, tip], 3)
            pygame.draw.lines(surface, self.shide_col, False, [top, p1, p2, p3, tip], 2)


class HeianToro(Rock):
    """Lanterna de pedra nobre Heian (Tōrō) com câmara aberta de lareira ritualística em brilho âmbar."""

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.36, height=1.25)
        self.stone_col = (72, 75, 82)
        self.stone_light = (95, 100, 110)
        self.amber_glow = (255, 195, 65)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        # 1. Base de lótus de cantaria
        draw_voxel_box(surface, camera, self.wx - 0.28, self.wy - 0.28, 0.0, 0.56, 0.56, 0.16, self.stone_col, outline=True)
        # 2. Fuste estriado
        draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.12, 0.16, 0.24, 0.24, 0.45, self.stone_light, outline=True)
        # 3. Plataforma do meio (Chūdai)
        draw_voxel_box(surface, camera, self.wx - 0.25, self.wy - 0.25, 0.61, 0.50, 0.50, 0.12, self.stone_col, outline=True)

        # 4. Câmara da chama sagrada (Hibukuro) com oscilação suave
        flick = 0.90 + 0.10 * math.sin(time_val * 8.0 + self.wx * 3.0)
        glow = tuple(min(255, int(c * flick)) for c in self.amber_glow)
        draw_voxel_box(surface, camera, self.wx - 0.18, self.wy - 0.18, 0.73, 0.36, 0.36, 0.28, glow, outline=False)

        # Colunas de pedra da câmara
        draw_voxel_box(surface, camera, self.wx - 0.20, self.wy - 0.20, 0.73, 0.08, 0.08, 0.28, self.stone_col, outline=False)
        draw_voxel_box(surface, camera, self.wx + 0.12, self.wy - 0.20, 0.73, 0.08, 0.08, 0.28, self.stone_col, outline=False)
        draw_voxel_box(surface, camera, self.wx - 0.20, self.wy + 0.12, 0.73, 0.08, 0.08, 0.28, self.stone_col, outline=False)
        draw_voxel_box(surface, camera, self.wx + 0.12, self.wy + 0.12, 0.73, 0.08, 0.08, 0.28, self.stone_col, outline=False)

        # 5. Telhado hexagonal com abas curvadas (Kasa)
        draw_voxel_box(surface, camera, self.wx - 0.32, self.wy - 0.32, 1.01, 0.64, 0.64, 0.16, self.stone_col, outline=True)
        # 6. Ornamento de joia sagrada no ápice (Hōju)
        draw_voxel_box(surface, camera, self.wx - 0.10, self.wy - 0.10, 1.17, 0.20, 0.20, 0.15, self.stone_light, outline=False)


# =============================================================================
# ETAPA 5.3: CAMPO DOS MORTOS DE FOME (GASHADOKURO ARENA PROPS)
# =============================================================================

class SoulFissure:
    """
    Fenda espiritual profunda no solo rachado de onde emergem almas sombrias
    e espíritos malignos (Onryō / Yūrei) em 3D continuamente.
    """
    animated = True

    def __init__(self, wx: float, wy: float, length: float = 2.0, angle: float = 0.4, seed: int = 1):
        self.wx = wx
        self.wy = wy
        self.length = length
        self.angle = angle
        self.seed = seed
        self.rock_dark = (32, 22, 26)
        self.rock_rim = (54, 36, 42)
        self.void_purple = (145, 35, 195)
        self.void_crimson = (225, 45, 85)
        self.core_bright = (240, 165, 255)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        ca = math.cos(self.angle)
        sa = math.sin(self.angle)
        px, py = -sa, ca
        pulse = 0.65 + 0.35 * math.sin(time_val * 4.5 + self.seed * 1.7)

        # 1. Bordas rochosas irregulares da fissura e fenda brilhante no solo
        steps = 6
        half_l = self.length * 0.5
        crack_pts_l = []
        crack_pts_r = []
        core_pts = []
        for i in range(steps + 1):
            u = -half_l + (i / steps) * self.length
            jagged = math.sin(i * 2.1 + self.seed) * 0.14
            width_here = 0.26 * math.sin((i / steps) * math.pi) + 0.06
            cx = self.wx + ca * u + px * jagged
            cy = self.wy + sa * u + py * jagged
            crack_pts_l.append(camera.apply(cx + px * width_here, cy + py * width_here, 0.02))
            crack_pts_r.append(camera.apply(cx - px * width_here, cy - py * width_here, 0.02))
            core_pts.append(camera.apply(cx, cy, 0.03))

            # Blocos chanfrados 3D nas bordas da fenda
            if 0 < i < steps:
                rim_h = 0.08 + 0.05 * ((i + self.seed) % 2)
                draw_voxel_box(
                    surface, camera,
                    cx + px * (width_here + 0.08) - 0.10,
                    cy + py * (width_here + 0.08) - 0.10,
                    0.0, 0.20, 0.20, rim_h, self.rock_rim, outline=True
                )
                draw_voxel_box(
                    surface, camera,
                    cx - px * (width_here + 0.08) - 0.10,
                    cy - py * (width_here + 0.08) - 0.10,
                    0.0, 0.20, 0.20, rim_h * 0.85, self.rock_dark, outline=True
                )

        poly = crack_pts_l + list(reversed(crack_pts_r))
        if len(poly) >= 3:
            pygame.draw.polygon(surface, (22, 8, 28), poly)
            glow_col = (
                min(255, int(self.void_purple[0] * pulse + 40)),
                min(255, int(self.void_purple[1] * pulse + 10)),
                min(255, int(self.void_purple[2] * pulse + 50)),
            )
            pygame.draw.polygon(surface, glow_col, poly, 2)
        if len(core_pts) >= 2:
            pygame.draw.lines(surface, self.core_bright, False, core_pts, max(1, int(2 * camera.zoom)))

        # 2. Almas Sombrias e Espíritos Malignos 3D emergindo continuamente da fenda
        for s_idx in range(2):
            cycle = (time_val * (0.55 + 0.15 * s_idx) + self.seed * 0.37 + s_idx * 0.5) % 1.0
            along = (s_idx - 0.5) * (self.length * 0.45)
            sway_x = math.sin(time_val * 3.2 + s_idx * 2.5 + self.seed) * 0.18
            sway_y = math.cos(time_val * 2.7 + s_idx * 1.9 + self.seed) * 0.18
            sx_w = self.wx + ca * along + sway_x
            sy_w = self.wy + sa * along + sway_y
            sz_w = cycle * 1.85  # Sobe até 1.85m de altura antes de dissipar

            fade = math.sin(cycle * math.pi)
            if fade <= 0.08:
                continue

            # Cores sombrias / espectrais do espírito
            is_crimson = ((self.seed + s_idx) % 2 == 0)
            shroud_col = (38, 18, 48) if not is_crimson else (48, 16, 28)
            spirit_core = (155, 55, 220) if not is_crimson else (220, 45, 85)
            eye_glow = (255, 220, 90) if is_crimson else (190, 255, 255)

            # Cauda/Miasma inferior estreitando em direção à fenda (3 segmentos 3D)
            for tail_i in range(3):
                tz = max(0.02, sz_w - (tail_i + 1) * 0.16)
                tw = (0.18 - tail_i * 0.04) * fade
                tail_sway = math.sin(time_val * 5.0 + tail_i + s_idx) * 0.05
                draw_voxel_box(
                    surface, camera,
                    sx_w + tail_sway - tw * 0.5, sy_w - tail_sway - tw * 0.5,
                    tz, tw, tw, 0.14, shroud_col, outline=False
                )

            # Torso e Cabeça 3D de Espírito Maligno (Yūrei / Onryō)
            head_w = 0.22 * fade
            if head_w > 0.06:
                draw_voxel_box(
                    surface, camera,
                    sx_w - head_w * 0.5, sy_w - head_w * 0.5,
                    sz_w, head_w, head_w, head_w * 1.15, spirit_core, outline=True
                )
                # Chifres / Manto sombrio no topo do crânio espiritual
                draw_voxel_box(
                    surface, camera,
                    sx_w - head_w * 0.65, sy_w - head_w * 0.2,
                    sz_w + head_w * 0.9, head_w * 0.35, head_w * 0.35, head_w * 0.45, shroud_col, outline=False
                )
                draw_voxel_box(
                    surface, camera,
                    sx_w + head_w * 0.30, sy_w - head_w * 0.2,
                    sz_w + head_w * 0.9, head_w * 0.35, head_w * 0.35, head_w * 0.45, shroud_col, outline=False
                )
                # Braços fantasmagóricos erguidos em agonia
                arm_z = sz_w - 0.04 + math.sin(time_val * 6.0 + s_idx) * 0.06
                draw_voxel_box(
                    surface, camera,
                    sx_w - head_w * 1.1, sy_w - 0.04,
                    arm_z, head_w * 0.5, 0.08, 0.16, shroud_col, outline=False
                )
                draw_voxel_box(
                    surface, camera,
                    sx_w + head_w * 0.6, sy_w - 0.04,
                    arm_z, head_w * 0.5, 0.08, 0.16, shroud_col, outline=False
                )
                # Olhos espirituais poligonais (sem usar draw.circle)
                e1 = camera.apply(sx_w - 0.04, sy_w + head_w * 0.45, sz_w + head_w * 0.6)
                e2 = camera.apply(sx_w + 0.04, sy_w + head_w * 0.45, sz_w + head_w * 0.6)
                for ex, ey in (e1, e2):
                    pygame.draw.polygon(surface, eye_glow, [(ex - 2, ey), (ex, ey - 2), (ex + 2, ey), (ex, ey + 2)])


class BoneMound(Rock):
    """
    Monte funerário de ossos antigos, crânios de soldados famintos e armaduras de samurai despedaçadas.
    """
    def __init__(self, wx: float, wy: float, seed: int = 1):
        super().__init__(wx, wy, radius=0.65, height=0.85)
        self.seed = seed
        self.soil_col = (46, 34, 32)
        self.bone_col = (212, 202, 182)
        self.bone_dark = (158, 146, 128)
        self.armor_lacquer = (115, 24, 28)
        self.iron_rust = (62, 56, 58)

    def render(self, surface: pygame.Surface, camera):
        # 1. Base de terra revirada e cinzas
        draw_voxel_box(surface, camera, self.wx - 0.52, self.wy - 0.48, 0.0, 1.04, 0.96, 0.22, self.soil_col, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.36, self.wy - 0.34, 0.20, 0.72, 0.68, 0.18, self.soil_col, outline=True)

        # 2. Costelas e fêmures empilhados em 3D
        draw_voxel_box(surface, camera, self.wx - 0.32, self.wy - 0.18, 0.34, 0.42, 0.12, 0.10, self.bone_dark, outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.04, self.wy - 0.26, 0.32, 0.12, 0.40, 0.10, self.bone_col, outline=True)

        # 3. Ombreira de samurai quebrada (Ō-sode) enterrada na pilha
        draw_voxel_box(surface, camera, self.wx - 0.38, self.wy + 0.06, 0.22, 0.34, 0.26, 0.28, self.armor_lacquer, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.36, self.wy + 0.08, 0.42, 0.30, 0.22, 0.08, self.iron_rust, outline=False)

        # 4. Crânios facetados no topo do monte
        draw_voxel_box(surface, camera, self.wx - 0.14, self.wy - 0.14, 0.38, 0.26, 0.26, 0.26, self.bone_col, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.10, self.wy + 0.08, 0.40, 0.18, 0.08, 0.12, (28, 22, 24), outline=False)
        draw_voxel_box(surface, camera, self.wx + 0.14, self.wy + 0.04, 0.24, 0.22, 0.22, 0.22, self.bone_dark, outline=True)


class SpectralToro(Rock):
    """
    Lanterna de pedra ancestral rachada no Campo dos Mortos de Fome,
    queimando com fogo espectral violeta e carmesim 3D.
    """
    animated = True

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.38, height=1.30)
        self.stone_dark = (48, 42, 46)
        self.stone_mid = (68, 60, 66)
        self.flame_violet = (175, 50, 235)
        self.flame_crimson = (245, 55, 95)
        self.flame_core = (255, 210, 255)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        # 1. Base de pedra rachada
        draw_voxel_box(surface, camera, self.wx - 0.30, self.wy - 0.30, 0.0, 0.60, 0.60, 0.18, self.stone_dark, outline=True)
        # 2. Coluna central
        draw_voxel_box(surface, camera, self.wx - 0.13, self.wy - 0.13, 0.18, 0.26, 0.26, 0.46, self.stone_mid, outline=True)
        # 3. Plataforma da câmara
        draw_voxel_box(surface, camera, self.wx - 0.26, self.wy - 0.26, 0.64, 0.52, 0.52, 0.12, self.stone_dark, outline=True)

        # 4. Chama Espectral 3D oscilante no interior (Hibukuro)
        flick = math.sin(time_val * 9.0 + self.wx * 2.3) * 0.04
        draw_voxel_box(surface, camera, self.wx - 0.16, self.wy - 0.16, 0.76, 0.32, 0.32, 0.26, self.flame_violet, outline=False)
        draw_voxel_box(surface, camera, self.wx - 0.10 + flick, self.wy - 0.10, 0.80, 0.20, 0.20, 0.22, self.flame_crimson, outline=False)
        draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05 + flick, 0.84, 0.10, 0.10, 0.16, self.flame_core, outline=False)

        # Pilares de canto da lanterna
        for ox, oy in ((-0.20, -0.20), (0.12, -0.20), (-0.20, 0.12), (0.12, 0.12)):
            draw_voxel_box(surface, camera, self.wx + ox, self.wy + oy, 0.76, 0.08, 0.08, 0.28, self.stone_dark, outline=False)

        # 5. Telhado pesado (Kasa) e topo quebrado
        draw_voxel_box(surface, camera, self.wx - 0.34, self.wy - 0.34, 1.04, 0.68, 0.68, 0.16, self.stone_mid, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.11, self.wy - 0.11, 1.20, 0.22, 0.22, 0.14, self.stone_dark, outline=True)


# =============================================================================
# CICLO 5: FLORESTA DOS PINHEIROS (DAIKI) & TAIGA DE EZO (AOI)
# =============================================================================

class AkamatsuPine(Rock):
    """
    Pinheiro-vermelho japonês monumental (Akamatsu) da Floresta dos Pinheiros:
    - Tronco avermelhado retorcido com raízes musgosas.
    - Copas em patamares de agulhas verde-esmeralda que oscilam com o vento da montanha.
    """
    animated = True

    def __init__(self, wx: float, wy: float, scale: float = 1.0):
        super().__init__(wx, wy, radius=0.55 * scale, height=3.2 * scale)
        self.scale = scale
        self.bark_red = (118, 56, 38)
        self.bark_dark = (78, 36, 24)
        self.moss_col = (64, 112, 52)
        self.needle_dark = (28, 76, 44)
        self.needle_mid = (44, 108, 60)
        self.needle_light = (68, 138, 76)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        s = self.scale
        sway = math.sin(time_val * 2.2 + self.wx * 0.7 + self.wy * 0.5) * 0.06 * s

        # 1. Raízes musgosas e base do tronco
        draw_voxel_box(surface, camera, self.wx - 0.36 * s, self.wy - 0.36 * s, 0.0, 0.72 * s, 0.72 * s, 0.22 * s, self.bark_dark, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.32 * s, self.wy - 0.32 * s, 0.18 * s, 0.64 * s, 0.64 * s, 0.10 * s, self.moss_col, outline=False)

        # 2. Tronco avermelhado Akamatsu em segmentos levemente sinuosos
        draw_voxel_box(surface, camera, self.wx - 0.22 * s, self.wy - 0.22 * s, 0.22 * s, 0.44 * s, 0.44 * s, 0.95 * s, self.bark_red, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.18 * s + sway * 0.3, self.wy - 0.18 * s, 1.15 * s, 0.36 * s, 0.36 * s, 0.95 * s, self.bark_red, outline=True)

        # Galhos horizontais estruturais
        draw_voxel_box(surface, camera, self.wx - 0.65 * s + sway * 0.5, self.wy - 0.10 * s, 1.55 * s, 1.30 * s, 0.20 * s, 0.14 * s, self.bark_dark, outline=True)

        # 3. Patamares de copa de pinheiro (3 nuvens largas de agulhas 3D)
        draw_voxel_box(surface, camera, self.wx - 0.95 * s + sway * 0.6, self.wy - 0.85 * s, 1.65 * s, 1.90 * s, 1.70 * s, 0.36 * s, self.needle_dark, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.82 * s + sway * 0.8, self.wy - 0.72 * s, 1.98 * s, 1.64 * s, 1.44 * s, 0.34 * s, self.needle_mid, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.56 * s + sway, self.wy - 0.52 * s, 2.30 * s, 1.12 * s, 1.04 * s, 0.30 * s, self.needle_light, outline=True)


class MountainHokora(Rock):
    """
    Pequeno santuário de trilha montanhesa (Hokora) sobre pedestal de pedra musgosa,
    com corda sagrada shimenawa e vela acesa no interior.
    """
    animated = True

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.48, height=1.45)
        self.stone_base = (104, 108, 102)
        self.moss = (66, 114, 58)
        self.wood_col = (128, 82, 48)
        self.roof_col = (54, 48, 44)
        self.rope_col = (218, 192, 132)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        # Pedestal de pedra e musgo
        draw_voxel_box(surface, camera, self.wx - 0.42, self.wy - 0.42, 0.0, 0.84, 0.84, 0.28, self.stone_base, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.36, self.wy - 0.36, 0.28, 0.72, 0.72, 0.24, self.stone_base, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.38, self.wy - 0.38, 0.48, 0.76, 0.76, 0.06, self.moss, outline=False)

        # Câmara de madeira do Hokora e chama votiva
        draw_voxel_box(surface, camera, self.wx - 0.28, self.wy - 0.28, 0.52, 0.56, 0.56, 0.48, self.wood_col, outline=True)
        flick = math.sin(time_val * 8.0 + self.wx) * 0.02
        draw_voxel_box(surface, camera, self.wx - 0.08 + flick, self.wy + 0.16, 0.62, 0.16, 0.14, 0.20, (255, 195, 75), outline=False)

        # Corda Shimenawa frontal e telhado curvado
        draw_voxel_box(surface, camera, self.wx - 0.32, self.wy + 0.24, 0.92, 0.64, 0.08, 0.07, self.rope_col, outline=False)
        draw_voxel_box(surface, camera, self.wx - 0.44, self.wy - 0.44, 0.98, 0.88, 0.88, 0.22, self.roof_col, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.28, self.wy - 0.28, 1.20, 0.56, 0.56, 0.16, self.roof_col, outline=True)


class TimberLogPile(Rock):
    """Pilha de toras de pinheiro cortadas e amarradas com corda na borda da clareira."""
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.58, height=0.72)
        self.bark = (108, 62, 38)
        self.wood_end = (208, 168, 114)
        self.rope = (186, 158, 104)

    def render(self, surface: pygame.Surface, camera):
        # 3 toras na base
        for ox in (-0.28, 0.0, 0.28):
            draw_voxel_box(surface, camera, self.wx + ox - 0.13, self.wy - 0.48, 0.0, 0.26, 0.96, 0.26, self.bark, outline=True)
            draw_voxel_box(surface, camera, self.wx + ox - 0.10, self.wy + 0.46, 0.03, 0.20, 0.04, 0.20, self.wood_end, outline=False)
        # 2 toras no segundo nível
        for ox in (-0.14, 0.14):
            draw_voxel_box(surface, camera, self.wx + ox - 0.13, self.wy - 0.44, 0.25, 0.26, 0.88, 0.26, self.bark, outline=True)
            draw_voxel_box(surface, camera, self.wx + ox - 0.10, self.wy + 0.42, 0.28, 0.20, 0.04, 0.20, self.wood_end, outline=False)
        # 1 tora no topo e amarração de corda
        draw_voxel_box(surface, camera, self.wx - 0.13, self.wy - 0.40, 0.48, 0.26, 0.80, 0.24, self.bark, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.44, self.wy - 0.06, 0.0, 0.88, 0.12, 0.56, self.rope, outline=False)


class AinuInauTotem(Rock):
    """
    Bastão ritual sagrado Ainu (Inau / Chisei-Inau) cravado na neve de Ezo:
    - Haste de madeira clara entalhada com cachos de aparas de madeira (kikepar) que balançam ao vento.
    - Topo esculpido em honra aos espíritos Kamuy da floresta boreal.
    """
    animated = True

    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.32, height=1.55)
        self.wood_light = (232, 212, 168)
        self.wood_shaving = (246, 234, 198)
        self.wood_dark = (146, 108, 68)
        self.red_cord = (196, 44, 48)
        self.snow_col = (236, 244, 255)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        sway = math.sin(time_val * 3.8 + self.wx * 1.3) * 0.04
        # Monte de neve na base
        draw_voxel_box(surface, camera, self.wx - 0.28, self.wy - 0.28, 0.0, 0.56, 0.56, 0.14, self.snow_col, outline=True)
        # Haste central de madeira sagrada
        draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, 0.12, 0.16, 0.16, 1.32, self.wood_dark, outline=True)
        # Cachos de aparas de madeira (kikepar) em duas coroas volumosas
        for z_h in (0.58, 0.98):
            draw_voxel_box(surface, camera, self.wx - 0.24 + sway, self.wy - 0.24, z_h, 0.48, 0.48, 0.22, self.wood_light, outline=True)
            draw_voxel_box(surface, camera, self.wx - 0.28 - sway, self.wy - 0.18, z_h - 0.08, 0.56, 0.36, 0.14, self.wood_shaving, outline=False)
        # Fita vermelha Ainu e topo entalhado
        draw_voxel_box(surface, camera, self.wx - 0.11, self.wy - 0.11, 1.24, 0.22, 0.22, 0.08, self.red_cord, outline=False)
        draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.12, 1.32, 0.24, 0.24, 0.20, self.wood_light, outline=True)


class HideDryingRack(Rock):
    """Varal de madeira Ainu para curtir peles de inverno, coberto de neve no topo."""
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, radius=0.55, height=1.50)
        self.pole_col = (98, 66, 42)
        self.pelt_fur = (218, 222, 230)
        self.pelt_inner = (164, 132, 102)
        self.snow_col = (240, 246, 255)

    def render(self, surface: pygame.Surface, camera):
        # 2 postes laterais de madeira
        draw_voxel_box(surface, camera, self.wx - 0.52, self.wy - 0.10, 0.0, 0.16, 0.20, 1.42, self.pole_col, outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.36, self.wy - 0.10, 0.0, 0.16, 0.20, 1.42, self.pole_col, outline=True)
        # Trave superior com camada de neve
        draw_voxel_box(surface, camera, self.wx - 0.60, self.wy - 0.12, 1.32, 1.20, 0.24, 0.14, self.pole_col, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.58, self.wy - 0.10, 1.44, 1.16, 0.20, 0.08, self.snow_col, outline=False)
        # Pele de lobo/cervo esticada no centro
        draw_voxel_box(surface, camera, self.wx - 0.32, self.wy - 0.05, 0.28, 0.64, 0.10, 0.98, self.pelt_fur, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.22, self.wy + 0.04, 0.38, 0.44, 0.04, 0.78, self.pelt_inner, outline=False)


class SnowSpruceTree(Rock):
    """Abeto boreal de Hokkaido (Ezo-matsu) carregado de neve alva em camadas cônicas 3D."""
    animated = True

    def __init__(self, wx: float, wy: float, scale: float = 1.0):
        super().__init__(wx, wy, radius=0.52 * scale, height=3.0 * scale)
        self.scale = scale
        self.trunk_col = (68, 46, 32)
        self.pine_dark = (24, 58, 48)
        self.pine_mid = (36, 78, 64)
        self.snow_bright = (238, 246, 255)
        self.snow_shade = (195, 214, 236)

    def render(self, surface: pygame.Surface, camera, time_val: float = 0.0):
        s = self.scale
        sway = math.sin(time_val * 2.0 + self.wx * 0.9) * 0.04 * s
        # Tronco e base nevada
        draw_voxel_box(surface, camera, self.wx - 0.38 * s, self.wy - 0.38 * s, 0.0, 0.76 * s, 0.76 * s, 0.18 * s, self.snow_shade, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.18 * s, self.wy - 0.18 * s, 0.14 * s, 0.36 * s, 0.36 * s, 0.75 * s, self.trunk_col, outline=True)

        # 3 camadas cônicas de abeto cobertas de neve espessa
        tiers = (
            (0.75 * s, 1.56 * s, 0.52 * s, 0.3),
            (1.38 * s, 1.18 * s, 0.50 * s, 0.6),
            (1.96 * s, 0.78 * s, 0.52 * s, 1.0),
        )
        for z0, w, h, sw_mult in tiers:
            ox = sway * sw_mult
            draw_voxel_box(surface, camera, self.wx - w * 0.5 + ox, self.wy - w * 0.5, z0, w, w, h * 0.65, self.pine_dark, outline=True)
            draw_voxel_box(surface, camera, self.wx - w * 0.46 + ox, self.wy - w * 0.46, z0 + h * 0.55, w * 0.92, w * 0.92, h * 0.45, self.snow_bright, outline=True)




