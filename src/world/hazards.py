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


# =============================================================================
# CICLO 4: CEMITÉRIO GÓTICO (VALERIUS)
# =============================================================================

class CemeteryBat:
    """Morcego animado voando pelo céu noturno do cemitério."""
    def __init__(self, wx: float, wy: float, wz: float, angle: float, speed: float = 3.2):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.angle = angle
        self.speed = speed
        self.wing_cycle = random.uniform(0.0, 10.0)
        self.turn_rate = random.uniform(-0.6, 0.6)

    def update(self, dt: float, cols: int = 21, rows: int = 21):
        self.wing_cycle += dt * 14.0
        self.angle += self.turn_rate * dt
        if self.wx < 2.0 or self.wx > cols - 2.0 or self.wy < 2.0 or self.wy > rows - 2.0:
            cx, cy = cols * 0.5, rows * 0.5
            target_angle = math.atan2(cy - self.wy, cx - self.wx)
            self.angle += (target_angle - self.angle) * dt * 2.0
            self.turn_rate = random.uniform(-0.8, 0.8)
        self.wx += math.cos(self.angle) * self.speed * dt
        self.wy += math.sin(self.angle) * self.speed * dt
        self.wz = 2.2 + math.sin(self.wing_cycle * 0.4) * 0.4

    def render(self, surface: pygame.Surface, camera):
        from src.isometric.voxel_renderer import draw_voxel_box
        flap = math.sin(self.wing_cycle)
        body_col = (24, 22, 28)
        wing_col = (38, 34, 44)
        draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, self.wz, 0.16, 0.16, 0.12, body_col, outline=False)
        w_span = 0.22
        w_h = flap * 0.12
        draw_voxel_box(surface, camera, self.wx - w_span - 0.04, self.wy - 0.06, self.wz + max(0.0, w_h), w_span, 0.12, 0.04, wing_col, outline=False)
        draw_voxel_box(surface, camera, self.wx + 0.04, self.wy - 0.06, self.wz + max(0.0, -w_h if w_h < 0 else w_h), w_span, 0.12, 0.04, wing_col, outline=False)


class WillOWisp:
    """Fogo fátuo espectral flutuante: persegue suavemente e causa SLOW ao tocar."""
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.wz = 0.65
        self.vx = random.uniform(-0.6, 0.6)
        self.vy = random.uniform(-0.6, 0.6)
        self.timer = 0.0
        self.active = True
        self.respawn_timer = 0.0

    def update(self, dt: float, fighters: list, particles: list, banners: list, cols: int = 21, rows: int = 21):
        if not self.active:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.active = True
                self.wx = random.uniform(4.0, cols - 4.0)
                self.wy = random.uniform(4.0, rows - 4.0)
            return

        self.timer += dt
        self.wz = 0.60 + math.sin(self.timer * 3.5) * 0.15

        self.wx += self.vx * dt
        self.wy += self.vy * dt
        if self.wx < 3.0 or self.wx > cols - 3.0:
            self.vx = -self.vx
        if self.wy < 3.0 or self.wy > rows - 3.0:
            self.vy = -self.vy

        if random.random() < dt * 0.8:
            self.vx += random.uniform(-0.3, 0.3)
            self.vy += random.uniform(-0.3, 0.3)
            spd = math.hypot(self.vx, self.vy)
            if spd > 1.1:
                self.vx = (self.vx / spd) * 0.95
                self.vy = (self.vy / spd) * 0.95

        if particles is not None and random.random() < 0.22:
            from src.effects.particles import SparkParticle
            particles.append(SparkParticle(self.wx, self.wy, self.wz, color=(70, 240, 190)))

        for f in fighters:
            if f and getattr(f, "is_alive", False):
                if math.hypot(f.wx - self.wx, f.wy - self.wy) < 0.65:
                    if hasattr(f, "apply_slow"):
                        f.apply_slow(2.5, banners=banners)
                    else:
                        f.slow_timer = 2.5
                    self.active = False
                    self.respawn_timer = random.uniform(4.5, 7.5)
                    if particles is not None:
                        from src.effects.particles import SparkParticle
                        for _ in range(12):
                            particles.append(SparkParticle(self.wx, self.wy, self.wz, color=(90, 255, 210)))
                    try:
                        from src.audio.sound_events import SoundEvent
                        from src.audio.sound_manager import SoundManager
                        SoundManager.get_instance().play(SoundEvent.DODGE_WHOOSH, volume_scale=0.7)
                    except Exception:
                        pass
                    break

    def render(self, surface: pygame.Surface, camera):
        if not self.active:
            return
        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        pulse = 0.75 + 0.25 * math.sin(self.timer * 6.0)
        r_outer = max(6, int(12 * pulse * camera.zoom))
        r_inner = max(3, int(6 * pulse * camera.zoom))
        glow_surf = pygame.Surface((r_outer * 2 + 4, r_outer * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (50, 220, 170, 75), (r_outer + 2, r_outer + 2), r_outer)
        pygame.draw.circle(glow_surf, (140, 255, 220, 170), (r_outer + 2, r_outer + 2), r_inner)
        pygame.draw.circle(glow_surf, (240, 255, 250, 230), (r_outer + 2, r_outer + 2), max(2, r_inner // 2))
        surface.blit(glow_surf, (sx - r_outer - 2, sy - r_outer - 2), special_flags=pygame.BLEND_ADD)


class ZombieWalker:
    """Zumbi reanimado lento que caminha em direção aos lutadores, causando 1 de dano ao alcançar."""
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.facing_x = 1.0
        self.facing_y = 0.0
        self.speed = 1.30
        self.is_alive = True
        self.radius = 0.40
        self.lifetime = 12.0
        self.walk_timer = 0.0

    def update(self, dt: float, fighters: list, arena, particles: list, banners: list) -> bool:
        if not self.is_alive:
            return False
        self.lifetime -= dt
        if self.lifetime <= 0.0:
            self.is_alive = False
            return False

        self.walk_timer += dt * 6.0

        nearest_f = None
        min_d = 999.0
        for f in fighters:
            if f and getattr(f, "is_alive", False):
                d = math.hypot(f.wx - self.wx, f.wy - self.wy)
                if d < min_d:
                    min_d = d
                    nearest_f = f

        if nearest_f:
            dx = nearest_f.wx - self.wx
            dy = nearest_f.wy - self.wy
            if min_d > 0.01:
                self.facing_x = dx / min_d
                self.facing_y = dy / min_d
            self.wx += self.facing_x * self.speed * dt
            self.wy += self.facing_y * self.speed * dt

            if min_d < (self.radius + getattr(nearest_f, "radius", 0.35)):
                nearest_f.take_hit((self.facing_x, self.facing_y), damage=1)
                self.is_alive = False
                if particles is not None:
                    from src.effects.particles import SparkParticle, SmokeParticle
                    for _ in range(14):
                        particles.append(SparkParticle(self.wx, self.wy, 0.5, color=(140, 200, 160)))
                    for _ in range(5):
                        particles.append(SmokeParticle(self.wx, self.wy, wz=0.4, color=(60, 50, 60), radius=0.4))
                if banners is not None:
                    banners.append(FloatingBanner("ZUMBI MORDIDA! / ZOMBIE HIT!", nearest_f.wx, nearest_f.wy, wz=1.8, color=(220, 60, 60)))
                try:
                    from src.audio.sound_events import SoundEvent
                    from src.audio.sound_manager import SoundManager
                    SoundManager.get_instance().play(SoundEvent.FLESH_CLEAVE)
                except Exception:
                    pass
                return False

        return True

    def take_hit(self, damage: int = 1, particles: list = None, banners: list = None):
        self.is_alive = False
        if particles is not None:
            from src.effects.particles import BloodParticle, SparkParticle
            for _ in range(12):
                particles.append(BloodParticle(self.wx, self.wy, 0.45))
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.5, color=(200, 195, 180)))
        if banners is not None:
            banners.append(FloatingBanner("ZUMBI DESTRUÍDO! / SLAIN!", self.wx, self.wy, wz=1.6, color=(240, 230, 200)))
        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent.BONE_CRUSH)
        except Exception:
            pass

    def render(self, surface: pygame.Surface, camera):
        if not self.is_alive:
            return
        from src.isometric.voxel_renderer import draw_voxel_box
        bx, by = self.wx, self.wy
        fx, fy = self.facing_x, self.facing_y
        px, py = -fy, fx
        leg_anim = math.sin(self.walk_timer) * 0.08

        skin_col = (118, 142, 126)
        cloth_col = (48, 44, 52)
        eye_col = (80, 255, 170)

        # Pernas
        draw_voxel_box(surface, camera, bx + px * 0.1 - 0.07, by + py * 0.1 - 0.07 + leg_anim, 0.0, 0.14, 0.14, 0.40, cloth_col, outline=True)
        draw_voxel_box(surface, camera, bx - px * 0.1 - 0.07, by - py * 0.1 - 0.07 - leg_anim, 0.0, 0.14, 0.14, 0.40, cloth_col, outline=True)
        # Torso e trapos
        draw_voxel_box(surface, camera, bx - 0.16, by - 0.14, 0.40, 0.32, 0.28, 0.45, cloth_col, outline=True)
        # Cabeça caída
        draw_voxel_box(surface, camera, bx + fx * 0.05 - 0.12, by + fy * 0.05 - 0.12, 0.85, 0.24, 0.24, 0.24, skin_col, outline=True)
        # Olhos
        eye_sx, eye_sy = camera.apply(bx + fx * 0.18, by + fy * 0.18, 0.98)
        pygame.draw.circle(surface, eye_col, (eye_sx, eye_sy), 2)
        # Braços estendidos
        arm_swing = math.cos(self.walk_timer * 0.5) * 0.04
        draw_voxel_box(surface, camera, bx + fx * 0.20 + px * 0.15 - 0.06, by + fy * 0.20 + py * 0.15 - 0.06, 0.60 + arm_swing, 0.24, 0.12, 0.12, skin_col, outline=True)
        draw_voxel_box(surface, camera, bx + fx * 0.20 - px * 0.15 - 0.06, by + fy * 0.20 - py * 0.15 - 0.06, 0.60 - arm_swing, 0.24, 0.12, 0.12, skin_col, outline=True)


class ZombieHandTrap:
    """Mãos de zumbi que emergem de covas: aviso -> agarram com STUN -> erguem ZombieWalker se não atacadas."""
    STATE_WARN = "WARN"
    STATE_ACTIVE = "ACTIVE"
    STATE_DONE = "DONE"

    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.state = self.STATE_WARN
        self.timer = 1.6
        self.active_timer = 1.4
        self.is_destroyed = False
        self.radius = 0.55

    def update(self, dt: float, fighters: list, particles: list, banners: list, zombies_out: list) -> bool:
        if self.is_destroyed:
            return False

        if self.state == self.STATE_WARN:
            self.timer -= dt
            if particles is not None and random.random() < 0.20:
                from src.effects.particles import SmokeParticle
                particles.append(SmokeParticle(self.wx, self.wy, wz=0.1, color=(50, 42, 34), radius=0.25))
            if self.timer <= 0.0:
                self.state = self.STATE_ACTIVE
                try:
                    from src.audio.sound_events import SoundEvent
                    from src.audio.sound_manager import SoundManager
                    SoundManager.get_instance().play(SoundEvent.BONE_CRUSH, volume_scale=0.7)
                except Exception:
                    pass

        elif self.state == self.STATE_ACTIVE:
            self.active_timer -= dt
            for f in fighters:
                if f and getattr(f, "is_alive", False) and getattr(f, "wz", 0.0) < 0.3:
                    if math.hypot(f.wx - self.wx, f.wy - self.wy) < (self.radius + getattr(f, "radius", 0.35) * 0.5):
                        f.stun(1.15)
                        if banners is not None:
                            banners.append(FloatingBanner("AGARRADO! / HELD!", f.wx, f.wy, wz=1.6, color=(140, 220, 160), duration=1.2))
                        if particles is not None:
                            from src.effects.particles import SparkParticle
                            for _ in range(8):
                                particles.append(SparkParticle(self.wx, self.wy, 0.2, color=(160, 240, 190)))
                        break

            if self.active_timer <= 0.0:
                self.state = self.STATE_DONE
                zombies_out.append(ZombieWalker(self.wx, self.wy))
                if banners is not None:
                    banners.append(FloatingBanner("MORTO-VIVO SURGE! / RISEN!", self.wx, self.wy, wz=1.9, color=(180, 230, 180), duration=1.3))
                if particles is not None:
                    from src.effects.particles import SmokeParticle, SparkParticle
                    for _ in range(16):
                        particles.append(SmokeParticle(self.wx, self.wy, wz=0.2, color=(55, 48, 40), radius=0.35))
                    for _ in range(10):
                        particles.append(SparkParticle(self.wx, self.wy, 0.4, color=(120, 255, 180)))
                return False

        return True

    def take_hit(self, particles: list = None, banners: list = None):
        self.is_destroyed = True
        if particles is not None:
            from src.effects.particles import BloodParticle, SparkParticle
            for _ in range(10):
                particles.append(BloodParticle(self.wx, self.wy, 0.3))
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.4, color=(180, 175, 160)))
        if banners is not None:
            banners.append(FloatingBanner("COVA PURIFICADA! / PURIFIED!", self.wx, self.wy, wz=1.5, color=(255, 220, 140), duration=1.2))
        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent.BONE_CRUSH)
        except Exception:
            pass

    def render_ground(self, surface: pygame.Surface, camera, time_val: float):
        if self.is_destroyed:
            return
        sx, sy = camera.apply(self.wx, self.wy, 0.02)
        if self.state == self.STATE_WARN:
            pulse = 0.5 + 0.5 * math.sin(time_val * 12.0)
            r_px = int(self.radius * 28 * camera.zoom)
            pygame.draw.circle(surface, (45, 36, 30), (sx, sy), r_px)
            pygame.draw.circle(surface, (60, int(160 * pulse + 80), int(120 * pulse + 50)), (sx, sy), r_px, 2)
            for a in (0.3, 1.8, 3.5, 4.9):
                ex, ey = camera.apply(self.wx + math.cos(a) * self.radius * 0.9, self.wy + math.sin(a) * self.radius * 0.9, 0.03)
                pygame.draw.line(surface, (50, 180, 130), (sx, sy), (ex, ey), 2)
        elif self.state == self.STATE_ACTIVE:
            r_px = int(self.radius * 28 * camera.zoom)
            pygame.draw.circle(surface, (30, 24, 22), (sx, sy), r_px)
            from src.isometric.voxel_renderer import draw_voxel_box
            bone_col = (185, 180, 165)
            draw_voxel_box(surface, camera, self.wx - 0.18, self.wy - 0.05, 0.0, 0.10, 0.10, 0.35, bone_col, outline=True)
            draw_voxel_box(surface, camera, self.wx + 0.08, self.wy - 0.05, 0.0, 0.10, 0.10, 0.38, bone_col, outline=True)
            draw_voxel_box(surface, camera, self.wx - 0.20, self.wy - 0.02, 0.32, 0.14, 0.06, 0.08, bone_col, outline=False)
            draw_voxel_box(surface, camera, self.wx + 0.06, self.wy - 0.02, 0.35, 0.14, 0.06, 0.08, bone_col, outline=False)


class GothicCemeteryHazard:
    """Gerenciador completo de perigos e detalhes do Cemitério Gótico."""
    def __init__(self):
        # 1. Morcegos noturnos
        self.bats = [
            CemeteryBat(random.uniform(5.0, 15.0), random.uniform(5.0, 15.0), 2.4, random.uniform(0.0, math.pi * 2.0))
            for _ in range(4)
        ]
        # 2. Fogos fátuos
        self.wisps = [
            WillOWisp(5.0, 5.0),
            WillOWisp(15.0, 15.0),
        ]
        # 3. Covas ativas com mãos e zumbis
        self.traps: list[ZombieHandTrap] = []
        self.zombies: list[ZombieWalker] = []
        self.trap_spawn_timer = 4.0
        self.grave_plots = [
            (5.0, 5.0), (15.0, 5.0), (5.0, 15.0), (15.0, 15.0),
            (5.5, 9.5), (15.5, 9.5), (9.5, 15.5)
        ]

    def update(self, arena, dt: float, fighters: list, camera, particles: list, banners: list, cinematic_director=None):
        cols, rows = getattr(arena, "cols", 21), getattr(arena, "rows", 21)
        # Morcegos
        for bat in self.bats:
            bat.update(dt, cols, rows)
        # Wisps
        for wisp in self.wisps:
            wisp.update(dt, fighters, particles, banners, cols, rows)

        # Spawn periódico de mãos de zumbi
        self.trap_spawn_timer -= dt
        if self.trap_spawn_timer <= 0.0:
            self.trap_spawn_timer = random.uniform(7.5, 11.5)
            if len(self.traps) < 3 and len(self.zombies) < 4:
                base_x, base_y = random.choice(self.grave_plots)
                gx = base_x + random.uniform(-1.2, 1.2)
                gy = base_y + random.uniform(-1.2, 1.2)
                self.traps.append(ZombieHandTrap(gx, gy))

        # Atualiza armadilhas de mãos
        self.traps = [t for t in self.traps if t.update(dt, fighters, particles, banners, self.zombies)]
        # Atualiza zumbis erguidos
        self.zombies = [z for z in self.zombies if z.update(dt, fighters, arena, particles, banners)]

    def check_combat_interactions(self, p1, p2, projectiles: list, particles: list, banners: list, camera):
        """Permite que combatentes ataquem e destruam as mãos e os zumbis com armas ou projéteis."""
        for f in (p1, p2):
            if f and getattr(f, "is_alive", False) and getattr(f, "hitbox_active", False):
                hx, hy = f.hitbox_center
                hr = f.hitbox_radius
                # Ataque corpo a corpo contra zumbis
                for z in self.zombies:
                    if z.is_alive and math.hypot(hx - z.wx, hy - z.wy) < (hr + z.radius):
                        z.take_hit(particles=particles, banners=banners)
                        if camera: camera.add_shake(4.0)
                # Ataque corpo a corpo contra mãos emergentes
                for t in self.traps:
                    if not t.is_destroyed and math.hypot(hx - t.wx, hy - t.wy) < (hr + t.radius):
                        t.take_hit(particles=particles, banners=banners)
                        if camera: camera.add_shake(4.0)

        # Projéteis contra zumbis e mãos
        for proj in projectiles:
            if getattr(proj, "is_active", False):
                px, py = getattr(proj, "wx", 0.0), getattr(proj, "wy", 0.0)
                for z in self.zombies:
                    if z.is_alive and math.hypot(px - z.wx, py - z.wy) < (0.4 + z.radius):
                        z.take_hit(particles=particles, banners=banners)
                        proj.is_active = False
                        break
                for t in self.traps:
                    if not t.is_destroyed and math.hypot(px - t.wx, py - t.wy) < (0.4 + t.radius):
                        t.take_hit(particles=particles, banners=banners)
                        proj.is_active = False
                        break

    def get_render_items(self, camera):
        items = []
        for z in self.zombies:
            if z.is_alive:
                items.append((camera.depth(z.wx, z.wy), "zombie_walker", z))
        return items

    def render_ground(self, arena, surface: pygame.Surface, camera, time_val: float):
        for t in self.traps:
            t.render_ground(surface, camera, time_val)

    def render_overhead(self, arena, surface: pygame.Surface, camera, time_val: float):
        for bat in self.bats:
            bat.render(surface, camera)
        for wisp in self.wisps:
            wisp.render(surface, camera)


# =============================================================================
# CICLO 4: PAVILHÃO ASTRAL HEIAN (SEIMEI)
# =============================================================================

class AstralMagicStream:
    """Raios e feixes semitransparentes de magia que cruzam a arena em padrões retos e espirais."""
    def __init__(self, mode: str = "straight", cx: float = 10.5, cy: float = 10.5):
        self.mode = mode
        self.cx = cx
        self.cy = cy
        self.angle = random.uniform(0.0, math.pi * 2.0)
        self.radius = random.uniform(1.2, 5.0)
        self.speed = random.uniform(2.0, 3.8)
        self.color = random.choice([(100, 180, 255), (180, 130, 255), (255, 215, 110), (120, 240, 220)])
        self.alpha = random.randint(75, 155)
        self.progress = random.uniform(0.0, 5.0)

        self.x = random.uniform(3.0, 18.0)
        self.y = random.uniform(3.0, 18.0)
        self.dx = math.cos(self.angle)
        self.dy = math.sin(self.angle)

    def update(self, dt: float):
        self.progress += dt * self.speed
        if self.mode == "spiral":
            self.angle += dt * self.speed * 0.75
            self.radius = 1.2 + (self.progress % 4.2)
        else:
            self.x += self.dx * self.speed * dt
            self.y += self.dy * self.speed * dt
            if self.x < 1.0 or self.x > 20.0 or self.y < 1.0 or self.y > 20.0:
                self.x = random.uniform(3.0, 18.0)
                self.y = random.uniform(3.0, 18.0)
                self.angle = random.uniform(0.0, math.pi * 2.0)
                self.dx = math.cos(self.angle)
                self.dy = math.sin(self.angle)

    def render(self, surface: pygame.Surface, camera):
        pts = []
        if self.mode == "spiral":
            for step in range(5):
                t_step = step * 0.15
                a = self.angle - t_step
                r = max(0.4, self.radius - t_step * 0.4)
                wx = self.cx + math.cos(a) * r
                wy = self.cy + math.sin(a) * r
                wz = 0.2 + (step * 0.08)
                pts.append(camera.apply(wx, wy, wz))
        else:
            for step in range(5):
                t_step = step * 0.25
                wx = self.x - self.dx * t_step
                wy = self.y - self.dy * t_step
                wz = 0.15 + (step * 0.05)
                pts.append(camera.apply(wx, wy, wz))

        if len(pts) >= 2:
            r, g, b = self.color
            surf_line = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.lines(surf_line, (r, g, b, self.alpha), False, pts, 3)
            pygame.draw.circle(surf_line, (255, 255, 255, min(255, self.alpha + 80)), pts[0], 4)
            surface.blit(surf_line, (0, 0), special_flags=pygame.BLEND_ADD)


class SpiritualBeast:
    """Pequeno animal mágico (Kitsune ou Usagi) que atravessa o jardim zen pacificamente."""
    def __init__(self, kind: str = "kitsune", start_edge: str = "west"):
        self.kind = kind
        self.start_edge = start_edge
        if start_edge == "west":
            self.wx, self.wy = 2.5, random.uniform(4.0, 16.0)
            self.target_x, self.target_y = 18.5, random.uniform(4.0, 16.0)
        else:
            self.wx, self.wy = 18.5, random.uniform(4.0, 16.0)
            self.target_x, self.target_y = 2.5, random.uniform(4.0, 16.0)
        self.wz = 0.0
        self.speed = 2.6 if kind == "kitsune" else 2.1
        self.hop_timer = 0.0
        self.is_done = False

    def update(self, dt: float) -> bool:
        if self.is_done:
            return False
        self.hop_timer += dt * (8.0 if self.kind == "kitsune" else 5.5)
        dx = self.target_x - self.wx
        dy = self.target_y - self.wy
        dist = math.hypot(dx, dy)
        if dist < 0.4:
            self.is_done = True
            return False
        ux, uy = dx / dist, dy / dist
        self.wx += ux * self.speed * dt
        self.wy += uy * self.speed * dt
        self.wz = max(0.0, math.sin(self.hop_timer) * 0.16)
        return True

    def render(self, surface: pygame.Surface, camera):
        if self.is_done:
            return
        from src.isometric.voxel_renderer import draw_voxel_box
        if self.kind == "kitsune":
            body_col = (250, 248, 240)
            ear_tip = (215, 60, 60)
            tail_col = (140, 210, 255)
            draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.08, self.wz, 0.24, 0.16, 0.16, body_col, outline=False)
            draw_voxel_box(surface, camera, self.wx + 0.08, self.wy - 0.06, self.wz + 0.10, 0.12, 0.12, 0.12, body_col, outline=False)
            draw_voxel_box(surface, camera, self.wx + 0.12, self.wy - 0.05, self.wz + 0.20, 0.04, 0.04, 0.06, ear_tip, outline=False)
            draw_voxel_box(surface, camera, self.wx - 0.22, self.wy - 0.05, self.wz + 0.08, 0.14, 0.10, 0.12, tail_col, outline=False)
        else:
            body_col = (245, 245, 250)
            ear_col = (255, 200, 210)
            draw_voxel_box(surface, camera, self.wx - 0.09, self.wy - 0.07, self.wz, 0.18, 0.14, 0.15, body_col, outline=False)
            draw_voxel_box(surface, camera, self.wx + 0.04, self.wy - 0.05, self.wz + 0.12, 0.10, 0.10, 0.10, body_col, outline=False)
            draw_voxel_box(surface, camera, self.wx + 0.02, self.wy - 0.04, self.wz + 0.20, 0.04, 0.08, 0.12, ear_col, outline=False)


class HealingTalisman:
    """Talismã sagrado que surge com aviso verde e cura 1 ponto de vida de quem pegar."""
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.wz = 0.25
        self.is_active = True
        self.is_warn = True
        self.warn_timer = 1.5
        self.lifetime = 14.0
        self.rot_timer = 0.0

    def update(self, dt: float, fighters: list, particles: list, banners: list) -> bool:
        if not self.is_active:
            return False

        self.rot_timer += dt * 4.0

        if self.is_warn:
            self.warn_timer -= dt
            if particles is not None and random.random() < 0.25:
                from src.effects.particles import SparkParticle
                particles.append(SparkParticle(self.wx, self.wy, 0.1, color=(80, 255, 140)))
            if self.warn_timer <= 0.0:
                self.is_warn = False
                if banners is not None:
                    banners.append(FloatingBanner("TALISMÃ SAGRADO! / HEALING WARD!", self.wx, self.wy, wz=1.8, color=(80, 255, 140), duration=1.2))
            return True

        self.lifetime -= dt
        if self.lifetime <= 0.0:
            self.is_active = False
            return False

        self.wz = 0.25 + math.sin(self.rot_timer * 1.5) * 0.08

        if particles is not None and random.random() < 0.20:
            from src.effects.particles import SparkParticle
            particles.append(SparkParticle(self.wx, self.wy, self.wz, color=(100, 255, 160)))

        for f in fighters:
            if f and getattr(f, "is_alive", False):
                if math.hypot(f.wx - self.wx, f.wy - self.wy) < 0.70:
                    max_h = getattr(f, "max_hp", 2)
                    cur_h = getattr(f, "hp", 1)
                    if cur_h < max_h:
                        f.hp = min(max_h, cur_h + 1)
                    self.is_active = False
                    if banners is not None:
                        banners.append(FloatingBanner("+1 VIDA! / RECOVERED!", f.wx, f.wy, wz=1.9, color=(80, 255, 140), duration=1.4))
                    if particles is not None:
                        from src.effects.particles import SparkParticle
                        for _ in range(18):
                            particles.append(SparkParticle(f.wx, f.wy, 0.6, color=(120, 255, 180)))
                    try:
                        from src.audio.sound_events import SoundEvent
                        from src.audio.sound_manager import SoundManager
                        SoundManager.get_instance().play(SoundEvent.PARRY, volume_scale=0.7)
                    except Exception:
                        pass
                    return False

        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        if self.is_warn:
            pulse = 0.5 + 0.5 * math.sin(self.rot_timer * 8.0)
            r_px = int(18 * camera.zoom)
            glow_surf = pygame.Surface((r_px * 2 + 4, r_px * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (60, 240, 130, int(100 * pulse + 50)), (r_px + 2, r_px + 2), r_px)
            pygame.draw.circle(glow_surf, (200, 255, 210, 200), (r_px + 2, r_px + 2), max(2, int(r_px * 0.4)))
            surface.blit(glow_surf, (sx - r_px - 2, sy - r_px - 2), special_flags=pygame.BLEND_ADD)
        else:
            w_px = max(8, int(14 * camera.zoom))
            h_px = max(14, int(22 * camera.zoom))
            paper_surf = pygame.Surface((w_px, h_px), pygame.SRCALPHA)
            paper_surf.fill((250, 252, 245, 240))
            pygame.draw.rect(paper_surf, (60, 220, 120), (1, 1, w_px - 2, h_px - 2), 2)
            pygame.draw.line(paper_surf, (40, 190, 90), (w_px // 2, 4), (w_px // 2, h_px - 4), 2)
            pygame.draw.line(paper_surf, (40, 190, 90), (3, h_px // 3), (w_px - 3, h_px // 3), 2)
            pygame.draw.line(paper_surf, (40, 190, 90), (3, 2 * h_px // 3), (w_px - 3, 2 * h_px // 3), 2)
            surface.blit(paper_surf, (sx - w_px // 2, sy - h_px // 2))
            glow_r = max(12, int(22 * camera.zoom))
            glow_s = pygame.Surface((glow_r * 2 + 2, glow_r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_s, (60, 240, 130, 60), (glow_r + 1, glow_r + 1), glow_r)
            surface.blit(glow_s, (sx - glow_r - 1, sy - glow_r - 1), special_flags=pygame.BLEND_ADD)


class PentagramDischarge:
    """Descarga de energia roxa do pentagrama central: aviso pulsante -> arcos elétricos invertem controles."""
    STATE_IDLE = "IDLE"
    STATE_WARN = "WARN"
    STATE_ACTIVE = "ACTIVE"

    def __init__(self, cx: float = 10.5, cy: float = 10.5, radius: float = 4.2):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.state = self.STATE_IDLE
        self.timer = random.uniform(8.0, 12.0)
        self.warn_duration = 1.6
        self.active_duration = 0.85

    def update(self, dt: float, fighters: list, particles: list, banners: list):
        self.timer -= dt

        if self.state == self.STATE_IDLE:
            if self.timer <= 0.0:
                self.state = self.STATE_WARN
                self.timer = self.warn_duration
                if banners is not None:
                    banners.append(FloatingBanner("PENTAGRAMA RESSOA! / STAR PULSE!", self.cx, self.cy, wz=2.2, color=(210, 80, 255), duration=1.4))
                try:
                    from src.audio.sound_events import SoundEvent
                    from src.audio.sound_manager import SoundManager
                    SoundManager.get_instance().play(SoundEvent.CHAIN_SPIN, volume_scale=0.6)
                except Exception:
                    pass

        elif self.state == self.STATE_WARN:
            if particles is not None and random.random() < 0.35:
                from src.effects.particles import SparkParticle
                ang = random.uniform(0.0, math.pi * 2.0)
                r = random.uniform(0.5, self.radius)
                particles.append(SparkParticle(self.cx + math.cos(ang) * r, self.cy + math.sin(ang) * r, 0.2, color=(200, 70, 255)))
            if self.timer <= 0.0:
                self.state = self.STATE_ACTIVE
                self.timer = self.active_duration
                try:
                    from src.audio.sound_events import SoundEvent
                    from src.audio.sound_manager import SoundManager
                    SoundManager.get_instance().play(SoundEvent.SHUKUCHI, volume_scale=0.9)
                except Exception:
                    pass

        elif self.state == self.STATE_ACTIVE:
            for f in fighters:
                if f and getattr(f, "is_alive", False):
                    d = math.hypot(f.wx - self.cx, f.wy - self.cy)
                    if d < self.radius + getattr(f, "radius", 0.35):
                        if hasattr(f, "apply_confusion"):
                            f.apply_confusion(2.4, banners=banners)
                        else:
                            f.confused_timer = 2.4
                        if particles is not None:
                            from src.effects.particles import SparkParticle
                            for _ in range(8):
                                particles.append(SparkParticle(f.wx, f.wy, 1.2, color=(220, 100, 255)))

            if self.timer <= 0.0:
                self.state = self.STATE_IDLE
                self.timer = random.uniform(9.0, 13.0)

    def render_ground(self, surface: pygame.Surface, camera, time_val: float):
        if self.state == self.STATE_IDLE:
            return
        cx, cy = self.cx, self.cy
        if self.state == self.STATE_WARN:
            pulse = 0.5 + 0.5 * math.sin(time_val * 14.0)
            color = (int(160 + 80 * pulse), int(40 + 40 * pulse), 255)
            star_pts = []
            for k in range(5):
                a = -math.pi / 2.0 + k * (4.0 * math.pi / 5.0)
                star_pts.append(camera.apply(cx + math.cos(a) * self.radius * 0.95, cy + math.sin(a) * self.radius * 0.95, 0.03))
            if len(star_pts) == 5:
                pygame.draw.polygon(surface, color, star_pts, 3)
        elif self.state == self.STATE_ACTIVE:
            color = (230, 120, 255)
            core_col = (255, 230, 255)
            for k in range(5):
                base_a = -math.pi / 2.0 + k * (2.0 * math.pi / 5.0)
                cur_x, cur_y = cx, cy
                r_step = self.radius / 5.0
                pts = [camera.apply(cur_x, cur_y, 0.04)]
                for s in range(1, 6):
                    r_cur = s * r_step
                    jolt = random.uniform(-0.35, 0.35)
                    nx = cx + math.cos(base_a) * r_cur - math.sin(base_a) * jolt
                    ny = cy + math.sin(base_a) * r_cur + math.cos(base_a) * jolt
                    pts.append(camera.apply(nx, ny, 0.04))
                pygame.draw.lines(surface, color, False, pts, 4)
                pygame.draw.lines(surface, core_col, False, pts, 2)


class HeianShrineHazard:
    """Gerenciador completo de perigos e detalhes do Pavilhão Astral Heian."""
    def __init__(self):
        # 1. Feixes de magia celestiais
        self.streams = [
            AstralMagicStream(mode="straight"),
            AstralMagicStream(mode="straight"),
            AstralMagicStream(mode="spiral"),
            AstralMagicStream(mode="spiral"),
        ]
        # 2. Pequenos animais espirituais
        self.beasts: list[SpiritualBeast] = []
        self.beast_spawn_timer = 5.0

        # 3. Talismãs de cura
        self.talismans: list[HealingTalisman] = []
        self.talisman_spawn_timer = 6.0

        # 4. Descarga de energia do pentagrama
        self.pentagram = PentagramDischarge(cx=10.5, cy=10.5, radius=4.2)

    def update(self, arena, dt: float, fighters: list, camera, particles: list, banners: list, cinematic_director=None):
        for s in self.streams:
            s.update(dt)

        # Animais mágicos
        self.beast_spawn_timer -= dt
        if self.beast_spawn_timer <= 0.0:
            self.beast_spawn_timer = random.uniform(9.0, 15.0)
            if len(self.beasts) < 2:
                kind = random.choice(["kitsune", "usagi"])
                edge = random.choice(["west", "east"])
                self.beasts.append(SpiritualBeast(kind=kind, start_edge=edge))
        self.beasts = [b for b in self.beasts if b.update(dt)]

        # Talismãs de cura
        self.talisman_spawn_timer -= dt
        if self.talisman_spawn_timer <= 0.0:
            self.talisman_spawn_timer = random.uniform(14.0, 20.0)
            if len(self.talismans) < 2:
                tx = random.uniform(6.0, 15.0)
                ty = random.uniform(6.0, 15.0)
                self.talismans.append(HealingTalisman(tx, ty))
        self.talismans = [t for t in self.talismans if t.update(dt, fighters, particles, banners)]

        # Pentagrama
        self.pentagram.update(dt, fighters, particles, banners)

    def get_render_items(self, camera):
        items = []
        for t in self.talismans:
            if t.is_active and not t.is_warn:
                items.append((camera.depth(t.wx, t.wy), "healing_talisman", t))
        for b in self.beasts:
            if not b.is_done:
                items.append((camera.depth(b.wx, b.wy), "spiritual_beast", b))
        return items

    def render_ground(self, arena, surface: pygame.Surface, camera, time_val: float):
        for t in self.talismans:
            if t.is_active and t.is_warn:
                t.render(surface, camera)
        self.pentagram.render_ground(surface, camera, time_val)

    def render_overhead(self, arena, surface: pygame.Surface, camera, time_val: float):
        for s in self.streams:
            s.render(surface, camera)


# =============================================================================
# ETAPA 5.3: CAMPO DOS MORTOS DE FOME (GASHADOKURO — HAZARDS POR FASE 1 A 5)
# =============================================================================

class FloatingDarkSoul:
    """
    Espírito maligno / alma sombria 3D que emerge do chão rachado,
    flutua em espiral com rosto cadavérico facetado e se dissipa no ar.
    """
    def __init__(self, wx: float, wy: float, is_crimson: bool = False):
        self.wx = wx
        self.wy = wy
        self.wz = 0.05
        self.is_crimson = is_crimson
        self.vz = random.uniform(0.45, 0.85)
        self.angle = random.uniform(0.0, math.tau)
        self.sway_speed = random.uniform(2.5, 4.5)
        self.lifetime = random.uniform(2.4, 3.8)
        self.age = 0.0

    def update(self, dt: float, phase: int = 0) -> bool:
        speed_mult = 1.0 + phase * 0.18
        self.age += dt * speed_mult
        if self.age >= self.lifetime:
            return False
        self.wz += self.vz * dt * speed_mult
        self.angle += self.sway_speed * dt
        self.wx += math.cos(self.angle) * 0.25 * dt
        self.wy += math.sin(self.angle) * 0.25 * dt
        return True

    def render(self, surface: pygame.Surface, camera):
        from src.isometric.voxel_renderer import draw_voxel_box
        progress = self.age / max(0.01, self.lifetime)
        fade = math.sin(progress * math.pi)
        if fade <= 0.1:
            return

        shroud = (34, 16, 44) if not self.is_crimson else (46, 14, 24)
        core = (165, 55, 235) if not self.is_crimson else (230, 45, 85)
        eye_col = (195, 255, 255) if not self.is_crimson else (255, 225, 95)

        w = 0.20 * fade
        if w < 0.05:
            return

        # Cauda de miasma sombrio 3D
        for i in range(2):
            tw = w * (0.75 - i * 0.25)
            tz = max(0.02, self.wz - (i + 1) * 0.14)
            draw_voxel_box(surface, camera, self.wx - tw * 0.5, self.wy - tw * 0.5, tz, tw, tw, 0.12, shroud, outline=False)

        # Crânio/manto do espírito maligno 3D
        draw_voxel_box(surface, camera, self.wx - w * 0.5, self.wy - w * 0.5, self.wz, w, w, w * 1.15, core, outline=True)
        # Garras/braços laterais
        draw_voxel_box(surface, camera, self.wx - w * 0.95, self.wy - 0.03, self.wz - 0.02, w * 0.4, 0.06, 0.12, shroud, outline=False)
        draw_voxel_box(surface, camera, self.wx + w * 0.55, self.wy - 0.03, self.wz - 0.02, w * 0.4, 0.06, 0.12, shroud, outline=False)

        # Olhos poligonais brilhantes
        ex, ey = camera.apply(self.wx, self.wy + w * 0.45, self.wz + w * 0.55)
        pygame.draw.polygon(surface, eye_col, [(ex - 2, ey), (ex, ey - 2), (ex + 2, ey), (ex, ey + 2)])


class SoulMiasmaGeyser:
    """
    Hazard de Fase 1+: Gêiser de Miasma e Almas Sombrias que brota das fissuras.
    Telegrafa por `warn_time` segundos e depois entra em erupção aplicando SLOW.
    """
    def __init__(self, wx: float, wy: float, radius: float = 1.15, warn_time: float = 1.1, active_time: float = 1.4):
        self.wx = wx
        self.wy = wy
        self.radius = radius
        self.warn_time = warn_time
        self.active_time = active_time
        self.t = 0.0
        self.applied_to = set()

    @property
    def is_active(self) -> bool:
        return self.warn_time <= self.t < (self.warn_time + self.active_time)

    @property
    def done(self) -> bool:
        return self.t >= (self.warn_time + self.active_time)

    def update(self, dt: float, fighters: list, particles: list, banners: list) -> bool:
        self.t += dt
        if self.done:
            return False

        if self.is_active:
            if particles is not None and random.random() < 0.35:
                from src.effects.particles import SparkParticle
                ang = random.uniform(0.0, math.tau)
                r = random.uniform(0.1, self.radius * 0.8)
                particles.append(SparkParticle(self.wx + math.cos(ang) * r, self.wy + math.sin(ang) * r, 0.5, color=(185, 65, 255)))

            for f in fighters:
                if f and getattr(f, "is_alive", False) and not getattr(f, "is_boss", False):
                    if id(f) not in self.applied_to and math.hypot(f.wx - self.wx, f.wy - self.wy) <= self.radius:
                        self.applied_to.add(id(f))
                        if hasattr(f, "apply_slow"):
                            f.apply_slow(2.2, banners=banners)
                        else:
                            f.slow_timer = 2.2
        return True

    def render_ground(self, surface: pygame.Surface, camera, time_val: float):
        n = 24
        pts = [
            camera.apply(self.wx + math.cos(i / n * math.tau) * self.radius,
                         self.wy + math.sin(i / n * math.tau) * self.radius, 0.02)
            for i in range(n)
        ]
        if len(pts) < 3:
            return

        if not self.is_active:
            k = min(1.0, self.t / max(0.01, self.warn_time))
            pulse = 0.5 + 0.5 * math.sin(time_val * 14.0)
            pygame.draw.polygon(surface, (42, 16, 56), pts)
            rim_col = (int(140 + 80 * k), int(35 + 30 * pulse), int(195 + 55 * k))
            pygame.draw.polygon(surface, rim_col, pts, 2)
        else:
            from src.isometric.voxel_renderer import draw_voxel_box
            pygame.draw.polygon(surface, (68, 18, 92), pts)
            pygame.draw.polygon(surface, (220, 110, 255), pts, 3)

            # Coluna 3D de espíritos e miasma jorrando da fenda
            active_k = (self.t - self.warn_time) / max(0.01, self.active_time)
            col_h = math.sin(active_k * math.pi) * 1.65
            if col_h > 0.12:
                draw_voxel_box(surface, camera, self.wx - 0.28, self.wy - 0.28, 0.0, 0.56, 0.56, col_h * 0.65, (52, 18, 72), outline=False)
                draw_voxel_box(surface, camera, self.wx - 0.16, self.wy - 0.16, col_h * 0.35, 0.32, 0.32, col_h * 0.65, (165, 55, 235), outline=True)
                draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, col_h * 0.75, 0.16, 0.16, col_h * 0.35, (235, 175, 255), outline=False)


class AbyssalSoulVortex:
    """
    Hazard de Fase 5 (Crânio Voraz): Vórtice do Abismo de Almas no centro da arena.
    Gira continuamente puxando suavemente os combatentes em direção ao centro.
    """
    def __init__(self, cx: float = 10.5, cy: float = 10.5, radius: float = 4.2):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.angle = 0.0

    def update(self, dt: float, fighters: list, game_map):
        self.angle += dt * 3.8
        for f in fighters:
            if f and getattr(f, "is_alive", False) and not getattr(f, "is_boss", False):
                dx = self.cx - f.wx
                dy = self.cy - f.wy
                dist = math.hypot(dx, dy)
                if 0.6 < dist < self.radius * 1.35:
                    pull_strength = 0.85 * (1.0 - dist / (self.radius * 1.5))
                    if hasattr(f, "apply_forced_displacement") and game_map is not None:
                        f.apply_forced_displacement((dx / dist) * pull_strength * dt, (dy / dist) * pull_strength * dt, game_map)

    def render_ground(self, surface: pygame.Surface, camera, time_val: float):
        # Espirais de almas sombrias e relâmpagos púrpura/carmesim no solo
        for arm in range(4):
            base_a = self.angle + arm * (math.tau / 4.0)
            pts = []
            for step in range(10):
                u = step / 9.0
                r = 0.35 + u * self.radius
                a = base_a - u * 2.4
                pts.append(camera.apply(self.cx + math.cos(a) * r, self.cy + math.sin(a) * r, 0.03))
            if len(pts) >= 2:
                col = (195, 55, 245) if arm % 2 == 0 else (235, 45, 90)
                pygame.draw.lines(surface, col, False, pts, 3)


class GashadokuroArenaHazard:
    """
    Gerenciador da Arena Campo dos Mortos de Fome (`gashadokuro_graveyard`):
    - Almas sombrias e espíritos malignos 3D saindo continuamente das fissuras do chão.
    - Escalonamento automático pelas 5 Fases do BossOni (ou seleção manual 1-5 no Arena Viewer):
      • Fase 1 (phase 0): Gêiseres de Miasma & Almas nas fissuras (aplicam SLOW)
      • Fase 2 (phase 1): + Chuva de Crânios Espectrais Flamejantes
      • Fase 3 (phase 2): + Fissuras de Magma Espiritual
      • Fase 4 (phase 3): + Garras e Espinhos Ósseos brotando do solo
      • Fase 5 (phase 4): + Vórtice do Abismo de Almas central + frequência máxima
    """
    FISSURE_SPOTS = (
        (6.2, 6.5), (14.8, 6.5), (4.8, 11.0), (16.2, 11.0),
        (6.5, 15.2), (14.5, 15.2), (10.5, 10.5),
    )

    def __init__(self):
        self.current_phase = 0
        self.manual_phase: int | None = None
        self.souls: list[FloatingDarkSoul] = []
        self.geysers: list[SoulMiasmaGeyser] = []
        self.preview_hazards = []  # Usado quando não há BossOni em campo (ex.: Arena Viewer)
        self.vortex = AbyssalSoulVortex(cx=10.5, cy=10.5, radius=4.2)
        self.soul_timer = 0.15
        self.geyser_timer = 2.2
        self.preview_timers = {"fire": 2.0, "lava": 3.5, "spikes": 2.8}

    def set_phase(self, phase: int):
        """Permite fixar a fase (0 a 4) no Arena Viewer / Studio Inspector."""
        self.manual_phase = max(0, min(4, phase))
        self.current_phase = self.manual_phase

    def update(self, arena, dt: float, fighters: list, camera, particles: list, banners: list, cinematic_director=None):
        # 1. Sincroniza fase com o BossOni em luta, ou usa manual_phase no Inspector
        boss_present = False
        for f in fighters:
            if getattr(f, "is_boss", False) and hasattr(f, "phase"):
                self.current_phase = int(f.phase)
                boss_present = True
                break
        if not boss_present and self.manual_phase is not None:
            self.current_phase = self.manual_phase

        # 2. Almas sombrias e espíritos malignos emergindo continuamente das fissuras
        self.soul_timer -= dt
        spawn_interval = max(0.14, 0.42 - self.current_phase * 0.06)
        if self.soul_timer <= 0.0:
            self.soul_timer = spawn_interval
            if len(self.souls) < (10 + self.current_phase * 3):
                fx, fy = random.choice(self.FISSURE_SPOTS)
                sx = fx + random.uniform(-1.1, 1.1)
                sy = fy + random.uniform(-1.1, 1.1)
                self.souls.append(FloatingDarkSoul(sx, sy, is_crimson=(random.random() < 0.45)))

        self.souls = [s for s in self.souls if s.update(dt, self.current_phase)]

        # 3. Fase 1+ (todas as fases): Gêiseres de Miasma e Almas nas fissuras
        self.geyser_timer -= dt
        if self.geyser_timer <= 0.0:
            geyser_every = max(1.8, 4.4 - self.current_phase * 0.55)
            self.geyser_timer = geyser_every
            count = 1 if self.current_phase < 2 else (2 if self.current_phase < 4 else 3)
            for _ in range(count):
                gx, gy = random.choice(self.FISSURE_SPOTS)
                gx += random.uniform(-0.8, 0.8)
                gy += random.uniform(-0.8, 0.8)
                self.geysers.append(SoulMiasmaGeyser(gx, gy, radius=1.15))

        self.geysers = [g for g in self.geysers if g.update(dt, fighters, particles, banners)]

        # 4. Fase 5 (phase == 4): Vórtice do Abismo de Almas no centro
        if self.current_phase >= 4:
            self.vortex.update(dt, fighters, arena)

        # 5. Quando inspecionado sem BossOni (ex.: Arena Viewer), spawna os perigos das Fases 2, 3 e 4
        if not boss_present:
            from src.entities.boss_oni import BossHazard
            if self.current_phase >= 1:
                self.preview_timers["fire"] -= dt
                if self.preview_timers["fire"] <= 0.0:
                    self.preview_timers["fire"] = max(1.6, 3.8 - self.current_phase * 0.45)
                    rx, ry = random.uniform(5.0, 16.0), random.uniform(5.0, 16.0)
                    self.preview_hazards.append(BossHazard("fireball", rx, ry, 1.0, 0.3, r=1.3))
            if self.current_phase >= 2:
                self.preview_timers["lava"] -= dt
                if self.preview_timers["lava"] <= 0.0:
                    self.preview_timers["lava"] = max(3.2, 6.0 - self.current_phase * 0.6)
                    ang = random.uniform(0.0, math.tau)
                    dx, dy = math.cos(ang), math.sin(ang)
                    self.preview_hazards.append(
                        BossHazard("lava", 10.5 - dx * 6.0, 10.5 - dy * 6.0, 1.2, 1.6,
                                   dx=dx, dy=dy, len=12.0, speed=9.0, width=1.5, slab=3.5)
                    )
            if self.current_phase >= 3:
                self.preview_timers["spikes"] -= dt
                if self.preview_timers["spikes"] <= 0.0:
                    self.preview_timers["spikes"] = max(2.0, 4.2 - self.current_phase * 0.5)
                    for _ in range(2):
                        rx, ry = random.uniform(5.5, 15.5), random.uniform(5.5, 15.5)
                        self.preview_hazards.append(BossHazard("spikes", rx, ry, 1.0, 0.7, r=0.95))

            for ph in self.preview_hazards:
                ph.update(dt)
            self.preview_hazards = [ph for ph in self.preview_hazards if not ph.done]

    def get_render_items(self, camera):
        items = []
        for s in self.souls:
            items.append((camera.depth(s.wx, s.wy), "dark_soul", s))
        for ph in self.preview_hazards:
            if ph.kind == "fireball":
                items.append((camera.depth(ph.x, ph.y) + 10.0, "boss_hazard_air", ph.air_view))
        return items

    def render_ground(self, arena, surface: pygame.Surface, camera, time_val: float):
        if self.current_phase >= 4:
            self.vortex.render_ground(surface, camera, time_val)
        for g in self.geysers:
            g.render_ground(surface, camera, time_val)
        for ph in self.preview_hazards:
            ph.render(surface, camera, time_val)

    def render_overhead(self, arena, surface: pygame.Surface, camera, time_val: float):
        for ph in self.preview_hazards:
            ph.render_air(surface, camera)


# =============================================================================
# CICLO 5: FLORESTA DOS PINHEIROS (DAIKI) & TAIGA DE EZO (AOI)
# =============================================================================

class FallingPineBranch:
    """
    Pinha gigante / galho pesado de Akamatsu derrubado pelas rajadas de vento da montanha.
    Telegrafa com sombra crescente no solo (`warn_time`) antes de cair e causar atordoamento/lentidão.
    """
    def __init__(self, wx: float, wy: float, radius: float = 1.05):
        self.wx = wx
        self.wy = wy
        self.radius = radius
        self.warn_time = 1.25
        self.active_time = 0.55
        self.t = 0.0
        self.applied = False

    @property
    def done(self) -> bool:
        return self.t >= (self.warn_time + self.active_time)

    def update(self, dt: float, fighters: list, particles: list, banners: list) -> bool:
        self.t += dt
        if self.done:
            return False

        if self.t >= self.warn_time and not self.applied:
            self.applied = True
            if particles is not None:
                from src.effects.particles import SparkParticle
                for _ in range(8):
                    particles.append(SparkParticle(self.wx, self.wy, 0.25, color=(138, 92, 52)))
            for f in fighters:
                if f and getattr(f, "is_alive", False):
                    if math.hypot(f.wx - self.wx, f.wy - self.wy) <= self.radius:
                        if hasattr(f, "apply_slow"):
                            f.apply_slow(1.8, banners=banners)
                        else:
                            f.slow_timer = 1.8
        return True

    def render_ground(self, surface: pygame.Surface, camera, time_val: float):
        from src.isometric.voxel_renderer import draw_voxel_box
        n = 20
        if self.t < self.warn_time:
            k = min(1.0, self.t / self.warn_time)
            r = self.radius * (0.35 + 0.65 * k)
            pts = [
                camera.apply(self.wx + math.cos(i / n * math.tau) * r,
                             self.wy + math.sin(i / n * math.tau) * r, 0.02)
                for i in range(n)
            ]
            if len(pts) >= 3:
                pygame.draw.polygon(surface, (42, 34, 24), pts)
                pygame.draw.polygon(surface, (215, 165, 75), pts, 2)
            # Galho/pinha caindo do alto
            z_fall = max(0.1, (1.0 - k) * 3.2)
            draw_voxel_box(surface, camera, self.wx - 0.22, self.wy - 0.14, z_fall, 0.44, 0.28, 0.24, (112, 62, 36), outline=True)
            draw_voxel_box(surface, camera, self.wx - 0.16, self.wy - 0.22, z_fall + 0.14, 0.32, 0.44, 0.18, (46, 108, 58), outline=True)
        else:
            # Galho caído no chão antes de quebrar
            draw_voxel_box(surface, camera, self.wx - 0.32, self.wy - 0.16, 0.0, 0.64, 0.32, 0.22, (112, 62, 36), outline=True)
            draw_voxel_box(surface, camera, self.wx - 0.22, self.wy - 0.24, 0.14, 0.44, 0.48, 0.18, (46, 108, 58), outline=True)


class PineForestHazard:
    """
    Hazard da Floresta dos Pinheiros (`sacred_pines` / `pine_forest` — Daiki):
    1. Rajada da Montanha (`Mountain Wind Gust`): Corrente periódica de vento dourado-esmeralda que atravessa a clareira,
       impulsionando saltos/esquivas a favor do vento e deslocando levemente os combatentes.
    2. Queda de Pinhas e Galhos (`FallingPineBranch`): Derrubados pelas rajadas, exigindo atenção ao posicionamento.
    """
    def __init__(self):
        self.gust_timer = 5.5
        self.gust_active = 0.0
        self.gust_dir = (1.0, 0.0)
        self.branches: list[FallingPineBranch] = []
        self.branch_timer = 3.2
        self.wind_streaks = [
            {"x": random.uniform(3.0, 18.0), "y": random.uniform(3.0, 18.0), "z": random.uniform(0.3, 1.8), "spd": random.uniform(4.5, 7.5)}
            for _ in range(10)
        ]

    def update(self, arena, dt: float, fighters: list, camera, particles: list, banners: list, cinematic_director=None):
        # 1. Ciclo da Rajada da Montanha
        if self.gust_active > 0.0:
            self.gust_active -= dt
            gx, gy = self.gust_dir
            for f in fighters:
                if f and getattr(f, "is_alive", False) and hasattr(f, "apply_forced_displacement"):
                    # Impulso mais forte se estiver saltando ou esquivando
                    boost = 1.65 if getattr(f, "wz", 0.0) > 0.1 or getattr(f, "state", "") == "DODGE" else 0.72
                    f.apply_forced_displacement(gx * boost * dt, gy * boost * dt, arena)
        else:
            self.gust_timer -= dt
            if self.gust_timer <= 0.0:
                self.gust_timer = random.uniform(7.5, 11.0)
                self.gust_active = 2.6
                ang = random.choice((0.0, math.pi * 0.25, -math.pi * 0.25, math.pi))
                self.gust_dir = (math.cos(ang), math.sin(ang))

        # Atualiza feixes visuais de vento e agulhas de pinheiro
        gx, gy = self.gust_dir
        mult = 2.2 if self.gust_active > 0.0 else 0.75
        for st in self.wind_streaks:
            st["x"] = (st["x"] + gx * st["spd"] * mult * dt - 2.0) % 17.0 + 2.0
            st["y"] = (st["y"] + gy * st["spd"] * mult * dt - 2.0) % 17.0 + 2.0

        # 2. Queda periódica de pinhas e galhos
        self.branch_timer -= dt
        if self.branch_timer <= 0.0:
            self.branch_timer = random.uniform(4.0, 6.8)
            bx = random.uniform(5.5, 15.5)
            by = random.uniform(5.5, 15.5)
            self.branches.append(FallingPineBranch(bx, by))

        self.branches = [b for b in self.branches if b.update(dt, fighters, particles, banners)]

    def get_render_items(self, camera):
        return []

    def render_ground(self, arena, surface: pygame.Surface, camera, time_val: float):
        for b in self.branches:
            b.render_ground(surface, camera, time_val)

    def render_overhead(self, arena, surface: pygame.Surface, camera, time_val: float):
        gx, gy = self.gust_dir
        col = (225, 245, 190) if self.gust_active > 0.0 else (165, 205, 155)
        length = 1.35 if self.gust_active > 0.0 else 0.65
        for st in self.wind_streaks:
            p0 = camera.apply(st["x"], st["y"], st["z"])
            p1 = camera.apply(st["x"] + gx * length, st["y"] + gy * length, st["z"] + 0.06)
            pygame.draw.line(surface, col, p0, p1, 2 if self.gust_active > 0.0 else 1)


class EzoTaigaHazard:
    """
    Hazard da Taiga Nevada de Ezo (`ezo_tundra` / `ezo_taiga` — Aoi):
    1. Nevasca Periódica Whiteout (`Blizzard Squall`): Rajada polar que sopra neve densa pela clareira,
       empurrando e resfriando combatentes que estejam longe do calor das fogueiras de caça.
    2. Bordas de Gelo Escorregadio: Deslizamento extra quando os lutadores pisam no anel congelado externo.
    """
    CAMPFIRES = ((6.8, 6.8), (14.2, 14.2))

    def __init__(self):
        self.blizzard_timer = 6.5
        self.blizzard_active = 0.0
        self.wind_dir = (0.85, 0.52)
        self.snow_gusts = [
            {"x": random.uniform(2.5, 18.5), "y": random.uniform(2.5, 18.5), "z": random.uniform(0.2, 2.0), "spd": random.uniform(5.0, 8.5)}
            for _ in range(14)
        ]

    def update(self, arena, dt: float, fighters: list, camera, particles: list, banners: list, cinematic_director=None):
        if self.blizzard_active > 0.0:
            self.blizzard_active -= dt
            wx_d, wy_d = self.wind_dir
            for f in fighters:
                if f and getattr(f, "is_alive", False):
                    # Verifica se está protegido perto de uma fogueira de caça
                    near_fire = any(math.hypot(f.wx - fx, f.wy - fy) < 2.6 for fx, fy in self.CAMPFIRES)
                    if not near_fire and hasattr(f, "apply_forced_displacement"):
                        f.apply_forced_displacement(wx_d * 0.95 * dt, wy_d * 0.95 * dt, arena)
        else:
            self.blizzard_timer -= dt
            if self.blizzard_timer <= 0.0:
                self.blizzard_timer = random.uniform(8.0, 12.0)
                self.blizzard_active = 3.2
                ang = random.uniform(-0.6, 0.8)
                self.wind_dir = (math.cos(ang), math.sin(ang))

        # Gelo escorregadio nas bordas da clareira (distância ao centro > 5.4)
        for f in fighters:
            if f and getattr(f, "is_alive", False) and getattr(f, "is_moving", False):
                dist_c = math.hypot(f.wx - 10.5, f.wy - 10.5)
                if dist_c > 5.4 and hasattr(f, "apply_forced_displacement"):
                    fx_f = getattr(f, "facing_x", 0.0)
                    fy_f = getattr(f, "facing_y", 0.0)
                    f.apply_forced_displacement(fx_f * 0.85 * dt, fy_f * 0.85 * dt, arena)

        wx_d, wy_d = self.wind_dir
        mult = 2.4 if self.blizzard_active > 0.0 else 0.85
        for sg in self.snow_gusts:
            sg["x"] = (sg["x"] + wx_d * sg["spd"] * mult * dt - 2.0) % 17.0 + 2.0
            sg["y"] = (sg["y"] + wy_d * sg["spd"] * mult * dt - 2.0) % 17.0 + 2.0

    def get_render_items(self, camera):
        return []

    def render_ground(self, arena, surface: pygame.Surface, camera, time_val: float):
        # Halos de calor alaranjados ao redor das fogueiras de caça durante a nevasca
        if self.blizzard_active > 0.0:
            pulse = 0.5 + 0.5 * math.sin(time_val * 8.0)
            col = (255, int(155 + 40 * pulse), 75)
            for fx, fy in self.CAMPFIRES:
                pts = [
                    camera.apply(fx + math.cos(i / 18 * math.tau) * 2.4,
                                 fy + math.sin(i / 18 * math.tau) * 2.4, 0.02)
                    for i in range(18)
                ]
                if len(pts) >= 3:
                    pygame.draw.polygon(surface, col, pts, 2)

    def render_overhead(self, arena, surface: pygame.Surface, camera, time_val: float):
        wx_d, wy_d = self.wind_dir
        col = (235, 248, 255) if self.blizzard_active > 0.0 else (195, 220, 240)
        length = 1.45 if self.blizzard_active > 0.0 else 0.55
        for sg in self.snow_gusts:
            p0 = camera.apply(sg["x"], sg["y"], sg["z"])
            p1 = camera.apply(sg["x"] + wx_d * length, sg["y"] + wy_d * length, sg["z"] - 0.08)
            pygame.draw.line(surface, col, p0, p1, 2 if self.blizzard_active > 0.0 else 1)
