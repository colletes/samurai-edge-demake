"""Perigos telegrafados das arenas temáticas: aviso, fase ativa e recarga (Entregável 6.3.1)."""
import math
import random

import pygame

from src.effects.particles import FloatingBanner, SmokeParticle

PHASE_IDLE = "idle"
PHASE_WARN = "warn"
PHASE_ACTIVE = "active"


class TelegraphedHazard:
    """
    Máquina de estados comum: recarga (idle) -> aviso (warn) -> ativo (active) -> recarga. O aviso dá tempo de
    reagir; só a fase ativa afeta lutadores. Subclasses implementam `on_phase`, `tick_active` e `render_ground`.
    """

    def __init__(self, warn_time: float = 2.0, active_time: float = 1.5, interval: tuple[float, float] = (5.0, 8.0),
                 initial_delay: float = 3.0):
        self.warn_time = warn_time
        self.active_time = active_time
        self.interval = interval
        self.phase = PHASE_IDLE
        self.timer = initial_delay
        self.elapsed = 0.0  # tempo dentro da fase atual

    def _set_phase(self, phase: str, arena, particles, banners):
        self.phase = phase
        self.elapsed = 0.0
        if phase == PHASE_IDLE:
            self.timer = random.uniform(*self.interval)
        elif phase == PHASE_WARN:
            self.timer = self.warn_time
        else:
            self.timer = self.active_time
        self.on_phase(phase, arena, particles, banners)

    def update(self, arena, dt: float, fighters: list, camera, particles: list, banners: list, cinematic_director=None):
        self.elapsed += dt
        self.timer -= dt
        if self.phase == PHASE_ACTIVE:
            self.tick_active(arena, dt, fighters, particles, banners)
        if self.timer <= 0.0:
            nxt = {PHASE_IDLE: PHASE_WARN, PHASE_WARN: PHASE_ACTIVE, PHASE_ACTIVE: PHASE_IDLE}[self.phase]
            self._set_phase(nxt, arena, particles, banners)

    def on_phase(self, phase: str, arena, particles: list, banners: list):
        """Chamado ao entrar em uma fase (som, banner, partículas)."""

    def tick_active(self, arena, dt: float, fighters: list, particles: list, banners: list):
        """Efeito sobre os lutadores enquanto a fase ativa durar."""


class TideSurge(TelegraphedHazard):
    """
    Maré que sobe: uma faixa de espuma varre a arena ao longo do eixo X (do mar até o penhasco) e empurra
    quem estiver dentro dela. O aviso mostra a espuma crescendo na margem do mar e um banner.
    A queda em fendas e no penhasco decorre do empurrão (ver `Samurai.update_pit`).
    """

    def __init__(self, x_from: float = 0.0, x_to: float = 22.0, band_width: float = 3.2, sweep_speed: float = 6.5,
                 push_speed: float = 6.0, y_range: tuple[float, float] | None = None, warn_time: float = 2.4,
                 interval: tuple[float, float] = (6.0, 9.0), initial_delay: float = 4.0):
        super().__init__(warn_time=warn_time, active_time=(x_to - x_from + band_width) / sweep_speed,
                         interval=interval, initial_delay=initial_delay)
        self.x_from = x_from
        self.x_to = x_to
        self.band_width = band_width
        self.sweep_speed = sweep_speed
        self.push_speed = push_speed
        self.y_range = y_range

    @property
    def front(self) -> float:
        """Borda dianteira da faixa de espuma (só significativa na fase ativa)."""
        return self.x_from + self.sweep_speed * self.elapsed

    def band(self) -> tuple[float, float]:
        return self.front - self.band_width, self.front

    def on_phase(self, phase: str, arena, particles: list, banners: list):
        if phase == PHASE_WARN and banners is not None:
            from src.i18n import t
            cx = (self.x_from + self.x_to) / 2.0
            banners.append(FloatingBanner(t("banner_tide"), cx, arena.rows / 2.0, wz=2.0, color=(150, 215, 240), duration=1.8))
        if phase == PHASE_ACTIVE:
            try:
                from src.audio.sound_events import SoundEvent
                from src.audio.sound_manager import SoundManager
                SoundManager.get_instance().play(SoundEvent.DODGE_WHOOSH)
            except Exception:
                pass

    def tick_active(self, arena, dt: float, fighters: list, particles: list, banners: list):
        lo, hi = self.band()
        y_lo, y_hi = self.y_range if self.y_range else (0.0, float(arena.rows))
        for f in fighters:
            if f is not None and lo <= f.wx <= hi and y_lo <= f.wy <= y_hi:
                f.apply_forced_displacement(self.push_speed * dt, 0.0, arena)
        if particles is not None and random.random() < 0.6:
            particles.append(SmokeParticle(
                max(self.x_from, min(self.x_to, hi - random.uniform(0.0, self.band_width))),
                random.uniform(y_lo, y_hi), wz=random.uniform(0.0, 0.2), color=(205, 228, 238),
                radius=random.uniform(0.14, 0.26), lifetime=random.uniform(0.35, 0.6)))

    def render_ground(self, arena, surface, camera, time_val: float):
        y_lo, y_hi = self.y_range if self.y_range else (0.0, float(arena.rows))
        if self.phase == PHASE_WARN:
            # Espuma crescendo na margem do mar, pulsando mais rápido perto do fim do aviso
            grow = 1.0 - max(0.0, self.timer) / self.warn_time
            lo, hi = self.x_from, self.x_from + 0.6 + 1.6 * grow
            bright = (int(time_val * (4.0 + 6.0 * grow)) % 2 == 0)
        elif self.phase == PHASE_ACTIVE:
            lo, hi = max(self.x_from, self.front - self.band_width), min(self.x_to, self.front)
            bright = True
        else:
            return
        if hi <= lo:
            return
        stripes = 7
        step = (y_hi - y_lo) / stripes
        for i in range(stripes):
            ya, yb = y_lo + i * step, y_lo + (i + 1) * step
            color = (214, 236, 244) if (i % 2 == 0) == bright else (150, 196, 214)
            quad = [camera.apply(lo, ya, 0.03), camera.apply(hi, ya, 0.03), camera.apply(hi, yb, 0.03), camera.apply(lo, yb, 0.03)]
            pygame.draw.polygon(surface, color, quad)
        edge = [camera.apply(hi, y_lo, 0.04), camera.apply(hi, y_hi, 0.04)]
        pygame.draw.line(surface, (245, 252, 255), edge[0], edge[1], 3)


class ShipRoll(TelegraphedHazard):
    """
    Balanço do navio: o convés adorna para um dos bordos (sorteado no aviso) e empurra todos os lutadores nessa
    direção, ao longo do eixo Y. O aviso mostra tremor de tela crescente, ranger de madeira, banner e setas no
    convés apontando o bordo; quem fica perto da amurada ou de uma tábua quebrada pode cair.
    """

    def __init__(self, push_speed: float = 3.4, warn_time: float = 2.2, active_time: float = 1.3,
                 interval: tuple[float, float] = (7.0, 10.0), initial_delay: float = 5.0,
                 x_range: tuple[float, float] = (0.0, 22.0), y_center: float = 11.0):
        super().__init__(warn_time=warn_time, active_time=active_time, interval=interval, initial_delay=initial_delay)
        self.push_speed = push_speed
        self.x_range = x_range
        self.y_center = y_center
        self.direction = 1.0  # +1 = bordo de y maior, -1 = bordo de y menor

    def update(self, arena, dt: float, fighters: list, camera, particles: list, banners: list, cinematic_director=None):
        super().update(arena, dt, fighters, camera, particles, banners, cinematic_director)
        if camera is not None and hasattr(camera, "add_shake"):
            if self.phase == PHASE_WARN:
                camera.add_shake(1.5 + 4.0 * (1.0 - max(0.0, self.timer) / self.warn_time))
            elif self.phase == PHASE_ACTIVE:
                camera.add_shake(6.0)

    def on_phase(self, phase: str, arena, particles: list, banners: list):
        if phase == PHASE_WARN:
            self.direction = random.choice((-1.0, 1.0))
            if banners is not None:
                from src.i18n import t
                cx = (self.x_range[0] + self.x_range[1]) / 2.0
                banners.append(FloatingBanner(t("banner_ship_roll"), cx, self.y_center, wz=2.0, color=(240, 200, 90), duration=1.8))
            self._play("ship_creak")
        elif phase == PHASE_ACTIVE:
            self._play("dodge_whoosh")

    @staticmethod
    def _play(name: str):
        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent(name))
        except Exception:
            pass

    def push_ramp(self) -> float:
        """Empurrão suave: sobe nos primeiros 0.35 s e some nos últimos 0.4 s."""
        ramp_in = min(1.0, self.elapsed / 0.35)
        ramp_out = min(1.0, max(0.0, (self.active_time - self.elapsed) / 0.4))
        return ramp_in * ramp_out

    def tick_active(self, arena, dt: float, fighters: list, particles: list, banners: list):
        push = self.push_speed * dt * self.push_ramp() * self.direction
        for f in fighters:
            if f is not None:
                f.apply_forced_displacement(0.0, push, arena)
        if particles is not None and random.random() < 0.5:
            edge_y = arena.rows - 0.5 if self.direction > 0 else 0.5
            particles.append(SmokeParticle(random.uniform(*self.x_range), edge_y, wz=random.uniform(0.0, 0.3),
                                           color=(205, 228, 238), radius=random.uniform(0.15, 0.3), lifetime=random.uniform(0.35, 0.6)))

    def render_ground(self, arena, surface, camera, time_val: float):
        """Setas no convés apontando o bordo para onde o navio vai adernar."""
        if self.phase not in (PHASE_WARN, PHASE_ACTIVE):
            return
        urgency = 1.0 - max(0.0, self.timer) / self.timer_total() if self.phase == PHASE_WARN else 1.0
        on = int(time_val * (3.0 + 8.0 * urgency)) % 2 == 0
        color = (244, 208, 96) if on else (176, 140, 56)
        d = self.direction
        x_lo, x_hi = self.x_range
        count = max(3, int((x_hi - x_lo) / 3.5))
        for i in range(count):
            cx = x_lo + (i + 0.5) * (x_hi - x_lo) / count
            for y in (self.y_center - d * 1.8, self.y_center + d * 0.2):
                shaft = [(cx - 0.14, y - d * 0.5), (cx + 0.14, y - d * 0.5), (cx + 0.14, y + d * 0.35), (cx - 0.14, y + d * 0.35)]
                head = [(cx - 0.55, y + d * 0.35), (cx + 0.55, y + d * 0.35), (cx, y + d * 1.05)]
                for part in (shaft, head):
                    pygame.draw.polygon(surface, color, [camera.apply(px, py, 0.03) for px, py in part])

    def timer_total(self) -> float:
        return self.warn_time


class ChainPendulum(TelegraphedHazard):
    """
    Pêndulo de corrente da Gruta das Sombras: um peso de ferro preso ao teto por uma corrente varre uma faixa do
    chão de ponta a ponta. O aviso risca a faixa e a zona de perigo no chão e o peso aparece parado no alto; na fase
    ativa ele desce, varre a faixa (baixo só no meio do percurso) e atinge quem estiver nela. Pular por cima ou
    esquivar com i-frames evita o golpe; cada lutador leva no máximo um golpe por varredura.
    """

    def __init__(self, lanes: tuple = ((11.0, 8.5, 1.0, 0.0), (11.0, 13.5, 1.0, 0.0), (8.5, 11.0, 0.0, 1.0), (13.5, 11.0, 0.0, 1.0)),
                 amplitude: float = 5.5, chain_length: float = 5.8, pivot_height: float = 6.0, hit_radius: float = 0.85,
                 damage: int = 2, warn_time: float = 2.0, active_time: float = 1.7,
                 interval: tuple[float, float] = (4.5, 7.0), initial_delay: float = 4.0):
        super().__init__(warn_time=warn_time, active_time=active_time, interval=interval, initial_delay=initial_delay)
        self.lanes = lanes
        self.amplitude = amplitude
        self.chain_length = chain_length
        self.pivot_height = pivot_height
        self.hit_radius = hit_radius
        self.damage = damage
        self.lane = 0
        self._hit_ids: set[int] = set()

    # -- geometria ----------------------------------------------------------
    def weight_z(self, u: float) -> float:
        """Altura do peso quando está a `u` do centro da faixa (arco de um pêndulo de comprimento fixo)."""
        return self.pivot_height - math.sqrt(max(0.0, self.chain_length ** 2 - min(abs(u), self.chain_length) ** 2))

    @property
    def danger_half_length(self) -> float:
        """Meio comprimento da zona em que o peso está baixo o bastante para acertar (z < 1.6)."""
        return math.sqrt(max(0.0, self.chain_length ** 2 - (self.pivot_height - 1.6) ** 2))

    def u_now(self) -> float | None:
        if self.phase == PHASE_WARN:
            return -self.amplitude
        if self.phase == PHASE_ACTIVE:
            return -self.amplitude * math.cos(math.pi * min(1.0, self.elapsed / self.active_time))
        return None

    def point(self, u: float) -> tuple[float, float, float]:
        cx, cy, dx, dy = self.lanes[self.lane]
        return cx + dx * u, cy + dy * u, self.weight_z(u)

    # -- ciclo --------------------------------------------------------------
    def on_phase(self, phase: str, arena, particles: list, banners: list):
        if phase == PHASE_WARN:
            options = [i for i in range(len(self.lanes)) if i != self.lane] or [0]
            self.lane = random.choice(options)
            if banners is not None:
                from src.i18n import t
                cx, cy, _, _ = self.lanes[self.lane]
                banners.append(FloatingBanner(t("banner_chain_swing"), cx, cy, wz=2.2, color=(190, 140, 255), duration=1.7))
            self._play("chain_rattle")
        elif phase == PHASE_ACTIVE:
            self._hit_ids = set()
            self._play("chain_whip")

    @staticmethod
    def _play(name: str):
        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent(name))
        except Exception:
            pass

    def tick_active(self, arena, dt: float, fighters: list, particles: list, banners: list):
        u = self.u_now()
        wx, wy, wz = self.point(u)
        if wz >= 1.6:
            return
        cx, cy, dx, dy = self.lanes[self.lane]
        direction = 1.0  # a varredura vai sempre do início ao fim da faixa
        for f in fighters:
            if f is None or not getattr(f, "is_alive", False) or id(f) in self._hit_ids:
                continue
            if math.hypot(f.wx - wx, f.wy - wy) < self.hit_radius + getattr(f, "radius", 0.35) * 0.5 \
                    and getattr(f, "wz", 0.0) < wz + 0.5:
                self._hit_ids.add(id(f))
                hit, _ = f.take_hit((dx * direction, dy * direction), damage=self.damage)
                if hit and f.is_alive:
                    f.apply_forced_displacement(dx * 1.4, dy * 1.4, arena)
                if hit and particles is not None:
                    from src.effects.particles import SparkParticle
                    for _ in range(10):
                        particles.append(SparkParticle(wx, wy, 0.6, color=(190, 150, 255)))

    # -- desenho ------------------------------------------------------------
    def render_ground(self, arena, surface, camera, time_val: float):
        """Faixa da varredura, zona de perigo pulsando e a sombra do peso que se aproxima do chão."""
        if self.phase not in (PHASE_WARN, PHASE_ACTIVE):
            return
        cx, cy, dx, dy = self.lanes[self.lane]
        px, py = -dy, dx
        half_w = 0.95
        reach = self.amplitude + 0.8

        def quad(a: float, b: float, w: float, z: float = 0.03):
            return [camera.apply(cx + dx * a + px * w, cy + dy * a + py * w, z), camera.apply(cx + dx * b + px * w, cy + dy * b + py * w, z),
                    camera.apply(cx + dx * b - px * w, cy + dy * b - py * w, z), camera.apply(cx + dx * a - px * w, cy + dy * a - py * w, z)]

        pygame.draw.polygon(surface, (30, 20, 44), quad(-reach, reach, half_w))
        urgency = 1.0 - max(0.0, self.timer) / self.warn_time if self.phase == PHASE_WARN else 1.0
        on = int(time_val * (3.0 + 9.0 * urgency)) % 2 == 0
        zone = self.danger_half_length
        pygame.draw.polygon(surface, (168, 40, 84) if on else (104, 26, 64), quad(-zone, zone, half_w - 0.12, 0.04))
        for k in range(-int(zone), int(zone) + 1):
            pygame.draw.polygon(surface, (222, 120, 160) if on else (150, 70, 110), quad(k - 0.04, k + 0.04, half_w - 0.12, 0.05))
        u = self.u_now()
        wx, wy, wz = self.point(u)
        gx, gy = camera.apply(wx, wy, 0.04)
        size = int((9 + 16 * (1.0 - min(1.0, wz / 4.5))) * camera.zoom)
        pygame.draw.ellipse(surface, (10, 6, 16), (gx - size, gy - size // 2, size * 2, size))

    def render_overhead(self, arena, surface, camera, time_val: float):
        """Corrente do teto e peso de ferro com espigões, por cima de tudo."""
        if self.phase not in (PHASE_WARN, PHASE_ACTIVE):
            return
        cx, cy, _, _ = self.lanes[self.lane]
        wx, wy, wz = self.point(self.u_now())
        top = camera.apply(cx, cy, self.pivot_height)
        bottom = camera.apply(wx, wy, wz + 0.38)
        pygame.draw.line(surface, (58, 54, 70), top, bottom, 5)
        links = max(4, int(math.hypot(bottom[0] - top[0], bottom[1] - top[1]) / 12))
        for i in range(links + 1):
            f = i / links
            pos = (int(top[0] + (bottom[0] - top[0]) * f), int(top[1] + (bottom[1] - top[1]) * f))
            pygame.draw.circle(surface, (150, 146, 168) if i % 2 == 0 else (96, 92, 112), pos, 4, 2)
        center = camera.apply(wx, wy, wz)
        r = max(6, int(abs(camera.apply(wx, wy, wz + 0.38)[1] - center[1])))
        for k in range(8):
            ang = k * math.pi / 4.0
            tip = (center[0] + int(math.cos(ang) * (r + 6)), center[1] + int(math.sin(ang) * (r + 6)))
            pygame.draw.line(surface, (120, 116, 136), center, tip, 3)
        pygame.draw.circle(surface, (36, 34, 46), center, r)
        pygame.draw.circle(surface, (84, 80, 100), (center[0] - r // 3, center[1] - r // 3), max(2, r // 2))
        pygame.draw.circle(surface, (190, 186, 210), (center[0] - r // 3, center[1] - r // 3), max(1, r // 4))


class FireworkMortars(TelegraphedHazard):
    """
    Morteiros de fogos do Templo na Névoa: a cada volta, círculos avisados no chão (alguns mirando onde os lutadores
    estão) esperam o tiro; no fim do aviso um projétil luminoso desce sobre cada círculo e explode, atingindo quem
    ficou dentro (dano 2, empurrão para fora). Sair do círculo durante o aviso evita tudo.
    """

    COLORS = ((255, 120, 80), (255, 220, 100), (120, 220, 255), (200, 140, 255), (140, 255, 170))

    def __init__(self, circles: int = 3, radius: float = 1.5, bounds: tuple[float, float, float, float] = (3.0, 3.0, 19.0, 19.0),
                 damage: int = 2, warn_time: float = 1.9, active_time: float = 0.6, interval: tuple[float, float] = (3.5, 5.5),
                 initial_delay: float = 4.0):
        super().__init__(warn_time=warn_time, active_time=active_time, interval=interval, initial_delay=initial_delay)
        self.count = circles
        self.radius = radius
        self.bounds = bounds
        self.damage = damage
        self.circles: list[tuple[float, float, float]] = []
        self._fighters: list = []

    def update(self, arena, dt: float, fighters: list, camera, particles: list, banners: list, cinematic_director=None):
        self._fighters = fighters
        super().update(arena, dt, fighters, camera, particles, banners, cinematic_director)

    def _free(self, arena, x: float, y: float) -> bool:
        return not any(o.check_collision(x, y, self.radius * 0.7)[0] for o in arena.buildings + arena.trees)

    def _pick_circles(self, arena) -> list[tuple[float, float, float]]:
        x0, y0, x1, y1 = self.bounds
        chosen: list[tuple[float, float, float]] = []
        targets = [f for f in self._fighters if f is not None and getattr(f, "is_alive", False)]
        random.shuffle(targets)
        for _ in range(self.count * 40):
            if len(chosen) >= self.count:
                break
            if len(chosen) < len(targets):  # os primeiros círculos miram os lutadores (com folga para o erro do tiro)
                f = targets[len(chosen)]
                x, y = f.wx + random.uniform(-0.8, 0.8), f.wy + random.uniform(-0.8, 0.8)
            else:
                x, y = random.uniform(x0, x1), random.uniform(y0, y1)
            x, y = max(x0, min(x1, x)), max(y0, min(y1, y))
            if self._free(arena, x, y) and all(math.hypot(x - cx, y - cy) > self.radius * 1.6 for cx, cy, _ in chosen):
                chosen.append((x, y, self.radius))
        return chosen

    @staticmethod
    def _play(name: str):
        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent(name))
        except Exception:
            pass

    def on_phase(self, phase: str, arena, particles: list, banners: list):
        if phase == PHASE_WARN:
            self.circles = self._pick_circles(arena)
            if banners is not None and self.circles:
                from src.i18n import t
                x, y, _ = self.circles[0]
                banners.append(FloatingBanner(t("banner_mortars"), x, y, wz=2.4, color=(255, 190, 90), duration=1.6))
            self._play("dodge_whoosh")
        elif phase == PHASE_ACTIVE:
            self._play("bomb_explode")
            from src.effects.particles import SparkParticle
            for cx, cy, r in self.circles:
                if particles is not None:
                    for _ in range(26):
                        particles.append(SparkParticle(cx, cy, 0.6, color=random.choice(self.COLORS)))
                    for _ in range(6):
                        particles.append(SmokeParticle(cx, cy, wz=0.5, color=(190, 184, 200), radius=0.4, lifetime=0.9))
                for f in self._fighters:
                    if f is None or not getattr(f, "is_alive", False):
                        continue
                    d = math.hypot(f.wx - cx, f.wy - cy)
                    if d < r + getattr(f, "radius", 0.35) * 0.5:
                        hit, _ = f.take_hit((f.wx - cx, f.wy - cy), damage=self.damage)
                        if hit and f.is_alive and d > 0.01:
                            f.apply_forced_displacement((f.wx - cx) / d * 1.5, (f.wy - cy) / d * 1.5, arena)
        elif phase == PHASE_IDLE:
            self.circles = []

    def _ring(self, camera, cx: float, cy: float, r: float, z: float = 0.03, steps: int = 28):
        return [camera.apply(cx + math.cos(a) * r, cy + math.sin(a) * r, z) for a in (2.0 * math.pi * i / steps for i in range(steps))]

    def render_ground(self, arena, surface, camera, time_val: float):
        if self.phase == PHASE_WARN:
            urgency = 1.0 - max(0.0, self.timer) / self.warn_time
            on = int(time_val * (3.0 + 10.0 * urgency)) % 2 == 0
            color = (255, 150, 60) if on else (170, 80, 40)
            for cx, cy, r in self.circles:
                pygame.draw.polygon(surface, color, self._ring(camera, cx, cy, r), 3)
                pygame.draw.polygon(surface, color, self._ring(camera, cx, cy, r * (0.35 + 0.65 * urgency)), 2)
                for k in range(8):
                    a = k * math.pi / 4.0 + time_val
                    pygame.draw.line(surface, color, camera.apply(cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9, 0.03),
                                     camera.apply(cx + math.cos(a) * r, cy + math.sin(a) * r, 0.03), 3)
        elif self.phase == PHASE_ACTIVE:
            f = max(0.0, 1.0 - self.elapsed / self.active_time)
            for cx, cy, r in self.circles:
                pygame.draw.polygon(surface, (min(255, int(255 * f) + 40), min(255, int(200 * f) + 30), int(110 * f)), self._ring(camera, cx, cy, r * (1.0 - 0.2 * f)))
                pygame.draw.polygon(surface, (255, 250, 220), self._ring(camera, cx, cy, r * (1.05 - 0.4 * f)), 3)

    def render_overhead(self, arena, surface, camera, time_val: float):
        """Projétil luminoso que desce sobre cada círculo no fim do aviso."""
        if self.phase != PHASE_WARN or self.timer > 0.55:
            return
        f = 1.0 - self.timer / 0.55
        z = 7.0 * (1.0 - f) + 0.3
        for cx, cy, _ in self.circles:
            head = camera.apply(cx, cy, z)
            tail = camera.apply(cx, cy, z + 1.4)
            pygame.draw.line(surface, (255, 190, 90), tail, head, 4)
            pygame.draw.circle(surface, (255, 246, 210), head, 6)
            pygame.draw.circle(surface, (255, 150, 60), head, 10, 2)


class RotatingStage(TelegraphedHazard):
    """
    Palco giratório do kabuki: o disco central gira e arrasta consigo quem está em cima, sem ferir. O aviso mostra
    o disco piscando com setas no sentido do giro e o ranger da madeira; na fase ativa o disco acelera, gira e
    desacelera, e a posição de cada lutador sobre ele acompanha a rotação (pode jogá-lo contra biombos e bordas).
    """

    def __init__(self, cx: float = 11.0, cy: float = 11.0, radius: float = 4.3, omega: float = 0.8, warn_time: float = 1.6,
                 active_time: float = 3.2, interval: tuple[float, float] = (4.0, 7.0), initial_delay: float = 4.0):
        super().__init__(warn_time=warn_time, active_time=active_time, interval=interval, initial_delay=initial_delay)
        self.cx, self.cy, self.radius, self.omega = cx, cy, radius, omega
        self.direction = 1.0
        self.angle = 0.0  # ângulo acumulado do disco (só visual)

    def _speed(self) -> float:
        """Velocidade angular com subida e descida suaves (0.5 s cada)."""
        ramp_in = min(1.0, self.elapsed / 0.5)
        ramp_out = min(1.0, max(0.0, (self.active_time - self.elapsed) / 0.5))
        return self.omega * self.direction * ramp_in * ramp_out

    @staticmethod
    def _play(name: str):
        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent(name))
        except Exception:
            pass

    def on_phase(self, phase: str, arena, particles: list, banners: list):
        if phase == PHASE_WARN:
            self.direction = random.choice((-1.0, 1.0))
            if banners is not None:
                from src.i18n import t
                banners.append(FloatingBanner(t("banner_stage_turns"), self.cx, self.cy, wz=2.2, color=(255, 190, 90), duration=1.6))
            self._play("ship_creak")

    def tick_active(self, arena, dt: float, fighters: list, particles: list, banners: list):
        w = self._speed()
        self.angle += w * dt
        da = w * dt
        cos_a, sin_a = math.cos(da), math.sin(da)
        for f in fighters:
            if f is None or not getattr(f, "is_alive", False) or getattr(f, "wz", 0.0) > 0.3:
                continue
            rx, ry = f.wx - self.cx, f.wy - self.cy
            if math.hypot(rx, ry) < self.radius:
                f.apply_forced_displacement(rx * cos_a - ry * sin_a - rx, rx * sin_a + ry * cos_a - ry, arena)

    def render_ground(self, arena, surface, camera, time_val: float):
        """Disco com raios que giram e, no aviso, anel e setas piscando no sentido do giro."""
        cx, cy, r = self.cx, self.cy, self.radius
        base = self.angle
        active = self.phase in (PHASE_WARN, PHASE_ACTIVE)
        on = int(time_val * 8.0) % 2 == 0
        color = (255, 196, 90) if (active and on) else (170, 120, 60)
        for k in range(8):
            a = base + k * math.pi / 4.0
            pygame.draw.line(surface, color, camera.apply(cx + math.cos(a) * 0.4, cy + math.sin(a) * 0.4, 0.03),
                             camera.apply(cx + math.cos(a) * r, cy + math.sin(a) * r, 0.03), 3 if active else 2)
        ring = [camera.apply(cx + math.cos(a) * r, cy + math.sin(a) * r, 0.03) for a in (2.0 * math.pi * i / 36 for i in range(36))]
        pygame.draw.polygon(surface, color, ring, 4 if active else 2)
        if self.phase == PHASE_WARN:
            for k in range(4):  # setas tangenciais no sentido do giro
                a = k * math.pi / 2.0 + time_val * 0.6 * self.direction
                px, py = cx + math.cos(a) * r * 0.72, cy + math.sin(a) * r * 0.72
                tx, ty = -math.sin(a) * self.direction, math.cos(a) * self.direction
                nx, ny = math.cos(a), math.sin(a)
                head = [(px + tx * 0.6, py + ty * 0.6), (px - tx * 0.1 + nx * 0.35, py - ty * 0.1 + ny * 0.35), (px - tx * 0.1 - nx * 0.35, py - ty * 0.1 - ny * 0.35)]
                pygame.draw.polygon(surface, color, [camera.apply(x, y, 0.04) for x, y in head])
