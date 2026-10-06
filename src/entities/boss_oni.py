"""
Entregável 8.2: Oni Gashadokuro, o chefe final do Arcade.

Ocupa o slot `p2` do duelo (D5). Tem 10 pontos de vida (D6), muda de fase a cada 2 perdidos e só sofre dano nos pontos
fracos/janelas de cada fase. Os ataques são `BossHazard` telegrafados (nenhum dano antes do aviso); o dano no jogador
é 1 (2 no impacto direto da fase 5), com 1.2 s de invulnerabilidade (D7). `wx`/`wy` são sempre o ponto fraco da fase.
"""
import math
import random
from types import SimpleNamespace

import pygame

from src.combat.collision import CombatSystem
from src.effects.particles import SparkParticle, SmokeParticle, FloatingBanner
from src.entities.boss_model import BossModel, Frame, TRANSFORM_TIME, DEBRIS_BY_PHASE
from src.entities.boss_model import layout_stand, layout_serpent, layout_torso, layout_club, layout_skull
from src.entities.samurai import Samurai, STATE_IDLE, resolve_playable_bounds
from src.i18n import t

# Valores de balanceamento (8.2.7): tempos em segundos, distâncias em unidades do mundo
BOSS_TUNING = {
    "hp_total": 10, "points_per_phase": 2,
    "player_iframes": 1.2, "hit_cooldown": 0.7,
    "p1_walk_speed": 2.2, "p1_gap": (0.2, 0.5), "p1_stomp_warn": 0.7, "p1_stomp_radius": 2.0, "p1_ring_speed": 5.5,
    "p1_ring_max": 4.6, "p1_sweep_warn": 0.7, "p1_sweep_active": 0.3, "p1_sweep_radius": 3.6, "p1_recover": 0.45,
    "p2_speed": 5.6, "p2_telegraph": 0.9, "p2_slow": 0.8, "p2_stun": 0.9, "p2_contact": 0.6,
    "p3_speed": 4.8, "p3_speed_gain": 0.6, "p3_speed_max": 8.5, "p3_aim": 0.55, "p3_stun": 0.9, "p3_tired_after": 5.0,
    "p4_idle": 0.25, "p4_warn": 0.8, "p4_radius": 2.2, "p4_aim_error": 0.8, "p4_jump": 0.4, "p4_stuck": 1.0,
    "p5_warns": (0.55, 0.45, 0.4), "p5_radius": 1.6, "p5_direct": 0.6, "p5_jump": 0.4, "p5_rest": 0.9,
    # Perigos do palco (a partir da fase 2): intervalo em segundos por fase (None = ainda não aparece)
    "env_grace": 2.0,
    "env_fire_every": (None, 5.0, 3.6, 2.8, 2.0), "env_fire_count": (0, 1, 1, 2, 3), "env_fire_warn": 1.0, "env_fire_radius": 1.3,
    "env_lava_every": (None, None, 9.0, 6.5, 4.5), "env_lava_warn": 1.4, "env_lava_speed": 9.0, "env_lava_width": 1.6, "env_lava_slab": 3.5,
    "env_trap_every": (None, None, None, 6.0, 4.0), "env_trap_count": (0, 0, 0, 3, 5), "env_trap_warn": 1.1, "env_trap_active": 0.7,
    "env_trap_radius": 0.95,
}
TUNE = BOSS_TUNING
PHASE_RADIUS = (1.1, 0.9, 1.1, 1.0, 0.8)
PHASE_KEYS = ("boss_phase_1", "boss_phase_2", "boss_phase_3", "boss_phase_4", "boss_phase_5")
DIFFICULTY_SCALE = {"easy": 1.2, "normal": 1.0, "hard": 0.8}  # só o tempo de aviso, nunca o dano


class BossHazard:
    """Área de dano telegrafada: `warn` s de aviso (sem dano) e depois `active` s de perigo. `kind` define a forma."""

    def __init__(self, kind: str, x: float, y: float, warn: float, active: float = 0.2, damage: int = 1, **shape):
        self.kind, self.x, self.y = kind, x, y
        self.warn, self.active, self.damage = warn, active, damage
        self.shape = shape
        self.t = 0.0
        self.hit_done = False
        self.announced = False  # o impacto já gerou o evento de som/tremor
        self.extra_life = shape.get("life", 0.0)  # `path`: continua desenhado depois do aviso

    @property
    def is_active(self) -> bool:
        return self.warn <= self.t < self.warn + self.active and self.kind != "path" and self.kind != "arrow"

    @property
    def done(self) -> bool:
        return self.t >= self.warn + max(self.active, self.extra_life)

    def update(self, dt: float):
        self.t += dt

    def radius_now(self) -> float:
        return self.shape["r0"] + self.shape["speed"] * max(0.0, self.t - self.warn) if self.kind == "ring" else self.shape.get("r", 0.0)

    def contains(self, px: float, py: float) -> bool:
        d = math.hypot(px - self.x, py - self.y)
        if self.kind in ("circle", "fireball", "spikes"):
            return d <= self.shape["r"]
        if self.kind == "lava":
            ux, uy = self.shape["dx"], self.shape["dy"]
            along = (px - self.x) * ux + (py - self.y) * uy
            perp = abs(-(px - self.x) * uy + (py - self.y) * ux)
            front = self.shape["speed"] * max(0.0, self.t - self.warn)
            return perp <= self.shape["width"] / 2.0 and front - self.shape["slab"] <= along <= front
        if self.kind == "ring":
            r = self.radius_now()
            return r - self.shape["width"] <= d <= r
        if self.kind == "sector":
            if d > self.shape["r"]:
                return False
            ang = math.atan2(py - self.y, px - self.x)
            diff = (ang - self.shape["dir"] + math.pi) % math.tau - math.pi
            return abs(diff) <= self.shape["half"]
        return False

    # ------------------------------------------------------------------ desenho
    def _lava_quad(self, a0: float, a1: float):
        ux, uy, half = self.shape["dx"], self.shape["dy"], self.shape["width"] / 2.0
        px, py = -uy * half, ux * half
        x0, y0, x1, y1 = self.x + ux * a0, self.y + uy * a0, self.x + ux * a1, self.y + uy * a1
        return [(x0 + px, y0 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (x0 - px, y0 - py)]

    def _outline(self):
        n = 40
        if self.kind == "lava":
            if self.t < self.warn:
                return self._lava_quad(0.0, self.shape["len"])
            front = self.shape["speed"] * (self.t - self.warn)
            return self._lava_quad(max(0.0, front - self.shape["slab"]), min(self.shape["len"] + self.shape["slab"], front))
        if self.kind in ("circle", "ring", "fireball", "spikes"):
            r = self.radius_now() if self.kind == "ring" else self.shape["r"]
            return [(self.x + math.cos(i / n * math.tau) * r, self.y + math.sin(i / n * math.tau) * r) for i in range(n)]
        if self.kind == "sector":
            r, a0, half = self.shape["r"], self.shape["dir"], self.shape["half"]
            pts = [(self.x, self.y)]
            pts += [(self.x + math.cos(a0 - half + 2 * half * i / 24) * r, self.y + math.sin(a0 - half + 2 * half * i / 24) * r) for i in range(25)]
            return pts
        if self.kind == "arrow":
            dx, dy, length = self.shape["dx"], self.shape["dy"], self.shape["len"]
            px, py = -dy, dx
            return [(self.x + px * 0.5, self.y + py * 0.5), (self.x + dx * length + px * 0.5, self.y + dy * length + py * 0.5),
                    (self.x + dx * length - px * 0.5, self.y + dy * length - py * 0.5), (self.x - px * 0.5, self.y - py * 0.5)]
        if self.kind == "path":
            return list(self.shape["points"])
        return []

    def render(self, surface: pygame.Surface, camera, game_time: float = 0.0):
        pts = self._outline()
        if len(pts) < 2:
            return
        screen_pts = [camera.apply(px, py, 0.02) for px, py in pts]
        xs, ys = [p[0] for p in screen_pts], [p[1] for p in screen_pts]
        x0, y0 = int(min(xs)) - 4, int(min(ys)) - 4
        w, h = int(max(xs)) - x0 + 8, int(max(ys)) - y0 + 8
        if w <= 0 or h <= 0 or w > 4000 or h > 4000:
            return
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        local = [(p[0] - x0, p[1] - y0) for p in screen_pts]
        active = self.is_active
        if self.kind == "path":
            pygame.draw.lines(overlay, (255, 150, 60, 190), True, local, 5)
        elif self.kind == "lava":
            if active:
                pygame.draw.polygon(overlay, (255, 96, 18, 235), local)
                pygame.draw.polygon(overlay, (255, 214, 90, 255), local, 3)
            else:
                progress = min(1.0, self.t / max(0.01, self.warn))
                pygame.draw.polygon(overlay, (255, 90, 30, int(30 + 70 * progress)), local)
                pygame.draw.polygon(overlay, (255, 150, 60, 200), local, 2)
        else:
            progress = min(1.0, self.t / max(0.01, self.warn))
            fill = (255, 40, 30, 150) if active else (255, 120, 50, int(40 + 70 * progress))
            if self.kind == "spikes" and not active:
                fill = (150, 20, 20, int(40 + 70 * progress))
            pygame.draw.polygon(overlay, fill, local)
            pygame.draw.polygon(overlay, (255, 220, 120, 230), local, 2)
        surface.blit(overlay, (x0, y0))
        if self.kind == "spikes":
            self._render_spikes(surface, camera)

    def _render_spikes(self, surface, camera):
        """Espinhos de osso que sobem do chão: tocos durante o aviso e lanças inteiras durante o perigo."""
        k = min(1.0, self.t / max(0.01, self.warn))
        height = 0.15 + 0.2 * k if self.t < self.warn else 1.1
        r = self.shape["r"]
        for i in range(7):
            ox, oy = (0.0, 0.0) if i == 0 else (math.cos(i / 6 * math.tau) * r * 0.62, math.sin(i / 6 * math.tau) * r * 0.62)
            bx, by = camera.apply(self.x + ox, self.y + oy, 0.0)
            tx, ty = camera.apply(self.x + ox, self.y + oy, height * (1.0 if i else 1.3))
            pygame.draw.polygon(surface, (236, 228, 204), [(bx - 5, by), (bx + 5, by), (tx, ty)])
            pygame.draw.polygon(surface, (120, 100, 80), [(bx - 5, by), (bx + 5, by), (tx, ty)], 1)

    def render_air(self, surface, camera):
        """Bola de fogo caindo do céu durante o aviso (desenhada acima dos lutadores)."""
        if self.kind != "fireball" or self.t >= self.warn:
            return
        k = self.t / max(0.01, self.warn)
        fall = 1.0 - k
        for n in range(6, -1, -1):  # rastro de chamas atrás da bola
            f = min(1.0, fall + n * 0.05)
            x, y, z = self.x - 2.2 * f, self.y - 2.2 * f, 0.5 + 9.0 * f ** 1.4
            px, py = camera.apply(x, y, z)
            zoom = getattr(camera, "zoom", 1.0)
            color = (255, 120 + n * 15, 30) if n else (255, 235, 140)
            pygame.draw.circle(surface, color, (px, py), max(2, int((9 - n) * zoom)))

    @property
    def air_view(self):
        return _AirView(self)


class _AirView:
    """Adaptador para a fila de desenho do mundo: `render(surface, camera)` desenha a parte aérea do perigo."""

    def __init__(self, hazard):
        self.hazard = hazard

    def render(self, surface, camera, game_time: float = 0.0):
        self.hazard.render_air(surface, camera)


class BossOni(Samurai):
    is_boss = True
    char_type = "gashadokuro"

    def __init__(self, wx: float, wy: float, seed: int = 8):
        super().__init__(wx, wy, t("boss_name"))
        self.max_hp = self.hp = TUNE["hp_total"]
        self.radius = PHASE_RADIUS[0]
        self.speed = TUNE["p1_walk_speed"]
        self.phase = 0
        self.model = BossModel(seed)
        self.rng = random.Random(seed)
        self.time = 0.0
        self.hazards: list[BossHazard] = []
        self.difficulty_scale = 1.0
        self.invuln_timer = 0.0
        self.vulnerable = True
        self.player_iframes = 0.0
        self.sub = "idle"
        self.sub_t = 0.0
        self.sub_data: dict = {}
        self.trail = [(wx - i * 0.2, wy) for i in range(40)]
        self.pose = {"stomp": 0.0, "sweep": None, "head_up": 1.0, "raise": 0.0}
        self.velocity = (0.0, 0.0)
        self.bounce_phase = 0.0
        self.last_attacks: list[str] = []
        self.env_rng = random.Random(seed + 101)  # sorteio separado: os perigos do palco não alteram os padrões do chefe
        self.env_timers: dict[str, float] = {}
        self._reset_env()
        self._clank = False
        self.dying = False
        self.events: list[str] = []
        self.model.prime(0, self.frame())

    # ------------------------------------------------------------------ utilidades
    def set_difficulty(self, name: str):
        self.difficulty_scale = DIFFICULTY_SCALE.get(name, 1.0)

    def frame(self) -> Frame:
        return Frame(self.wx, self.wy, self.wz, self.facing_x, self.facing_y)

    @property
    def phase_title(self) -> str:
        return t(PHASE_KEYS[self.phase])

    @property
    def transforming(self) -> bool:
        return self.model.transforming

    def set_phase(self, phase: int):
        """Começa direto na fase `phase` (checkpoint do Arcade) com os 2 pontos dela cheios."""
        self.phase = max(0, min(4, phase))
        self.hp = TUNE["hp_total"] - TUNE["points_per_phase"] * self.phase
        self.radius = PHASE_RADIUS[self.phase]
        self.model.prime(self.phase, self.frame())
        self._reset_brain()

    def _reset_brain(self):
        self.sub, self.sub_t, self.sub_data = "idle", 0.0, {}
        self.hazards.clear()
        self._reset_env()
        self.pose = {"stomp": 0.0, "sweep": None, "head_up": 1.0, "raise": 0.0}
        self.wz = 0.0
        self.velocity = (0.0, 0.0)
        if self.phase == 1:
            self._init_trail()

    def _reset_env(self):
        g = TUNE["env_grace"]
        self.env_timers = {"fire": g, "lava": g + 1.5, "trap": g + 3.0}

    def _init_trail(self):
        self.trail = [(self.wx - self.facing_x * i * 0.2, self.wy - self.facing_y * i * 0.2) for i in range(60)]

    def trail_point(self, d: float) -> tuple[float, float]:
        """Ponto do corpo da serpente a `d` unidades da cabeça, ao longo do histórico de posições."""
        pts = self.trail
        acc = 0.0
        for i in range(len(pts) - 1):
            seg = math.dist(pts[i], pts[i + 1])
            if acc + seg >= d and seg > 1e-6:
                k = (d - acc) / seg
                return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k)
            acc += seg
        return pts[-1]

    def current_layout(self) -> dict:
        fr = self.frame()
        pose = dict(self.pose, t=self.time)
        return [layout_stand(fr, pose), layout_serpent(self.trail_point, pose), layout_torso(fr, pose),
                layout_club(fr, pose), layout_skull(fr, pose)][self.phase]

    def _scaled(self, seconds: float) -> float:
        return seconds * self.difficulty_scale

    # ------------------------------------------------------------------ dano recebido
    def take_hit(self, slash_dir, damage: int = 2):
        """Só conta quando vulnerável (ponto fraco/janela); cada golpe válido tira 1 ponto, sem knockback nem stun."""
        if not self.is_alive or self.dying:
            return False, False
        if not self.vulnerable or self.transforming or self.invuln_timer > 0:
            self._clank = True
            return False, False
        self.hp -= 1
        self.invuln_timer = TUNE["hit_cooldown"]
        self.events.append("hit")
        if self.hp <= 0:
            self.hp = 0
            self.dying = True
            self.is_alive = False
            self.state = "DYING_FREEZE"
            return True, True
        new_phase = (TUNE["hp_total"] - self.hp) // TUNE["points_per_phase"]
        if new_phase != self.phase:
            self._begin_transform(new_phase)
        return True, False

    def stun(self, duration: float = 0.8):
        pass

    def apply_slow(self, duration: float = 2.5, banners: list = None):
        pass

    def apply_forced_displacement(self, dx, dy, game_map):
        pass

    def update_pit(self, dt, game_map, particles=None, banners=None) -> bool:
        return False

    def is_crossing_pit(self) -> bool:
        return True

    def can_act(self) -> bool:
        return False

    def _begin_transform(self, new_phase: int):
        self.poses()  # garante as poses da fase que termina, mesmo sem ter sido desenhada
        self.phase = new_phase
        if new_phase == 1:
            self._init_trail()
        self.model.begin_transform(new_phase, self.frame())
        self.hazards.clear()
        self.vulnerable = False
        self.radius = PHASE_RADIUS[new_phase]
        self.sub, self.sub_t, self.sub_data = "idle", 0.0, {}
        self.events.append(f"phase_{new_phase}")

    def begin_collapse(self):
        """Chamado pelo diretor cinematográfico depois do congelamento fatal: os ossos desabam."""
        self.state = "BONE_COLLAPSE"
        self.hazards.clear()
        self.model.begin_collapse(self.model.last_poses or self.model.poses(self.current_layout()))

    def pop_events(self) -> list[str]:
        ev, self.events = self.events, []
        return ev

    # ------------------------------------------------------------------ dano no jogador
    def _hurt_player(self, player, source, game_map, particles, banners, camera, damage: int = 1) -> bool:
        if not player.is_alive or self.player_iframes > 0 or player.is_invulnerable_dodge:
            return False
        dx, dy = player.wx - source[0], player.wy - source[1]
        n = math.hypot(dx, dy) or 1.0
        hit, dead = player.take_hit((dx / n, dy / n), damage=damage)
        if not hit:
            return False
        self.player_iframes = TUNE["player_iframes"]
        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(player.wx, player.wy, 0.8))
        if camera is not None:
            camera.add_shake(9.0)
        if not dead:
            stub = SimpleNamespace(wx=source[0], wy=source[1], facing_x=dx / n, facing_y=dy / n)
            CombatSystem._apply_hit_knockback(stub, player, game_map)
        self.events.append("player_hit")
        return True

    # ------------------------------------------------------------------ laço principal
    def update(self, dt: float, game_map=None, target=None, particles=None, banners=None, projectiles=None, camera=None):
        self.time += dt
        was_transforming = self.model.transforming
        self.model.update(dt)
        if was_transforming and not self.model.transforming and self.is_alive:
            self._finish_transform(target, banners)
        if self.invuln_timer > 0:
            self.invuln_timer = max(0.0, self.invuln_timer - dt)
        if self.player_iframes > 0:
            self.player_iframes = max(0.0, self.player_iframes - dt)
        if self._clank:
            self._clank = False
            if particles is not None:
                for _ in range(6):
                    particles.append(SparkParticle(self.wx, self.wy, 0.9, color=(210, 210, 220)))
        if not self.is_alive or self.dying:
            return
        if self.transforming:
            self.vulnerable = False
            if camera is not None:
                camera.add_shake(1.5)
            return
        if target is None or game_map is None or not target.is_alive:
            return
        self.vulnerable = True
        brain = (self._brain_stand, self._brain_serpent, self._brain_torso, self._brain_club, self._brain_skull)[self.phase]
        brain(dt, game_map, target, particles, banners, camera)
        self._update_env(dt, game_map, target)
        for h in self.hazards:
            h.update(dt)
            if h.is_active and not h.announced:
                h.announced = True
                if h.kind in ("fireball", "spikes", "lava"):
                    self.events.append(f"env_{h.kind}")
                    if camera is not None and h.kind != "lava":
                        camera.add_shake(6.0)
                    if h.kind == "fireball":
                        self._dust(particles, h.x, h.y, 8)
            if h.is_active and not h.hit_done and h.contains(target.wx, target.wy):
                if h.kind in ("circle", "ring", "sector", "fireball", "spikes", "lava"):
                    if self._hurt_player(target, (h.x, h.y), game_map, particles, banners, camera, h.damage):
                        h.hit_done = True
        self.hazards = [h for h in self.hazards if not h.done]

    # ------------------------------------------------------------------ perigos do palco
    def _update_env(self, dt, game_map, target):
        """Bolas de fogo, rios de lava e armadilhas aparecem em ritmo crescente a cada fase."""
        for key in ("fire", "lava", "trap"):
            every = TUNE[f"env_{key}_every"][self.phase]
            if every is None:
                continue
            self.env_timers[key] -= dt
            if self.env_timers[key] <= 0.0:
                self.env_timers[key] = every * self.env_rng.uniform(0.8, 1.2)
                getattr(self, f"_spawn_{key}")(game_map, target)

    def _random_spot(self, game_map, near=None, spread: float = 0.0):
        min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
        if near is None:
            x, y = self.env_rng.uniform(min_x, max_x), self.env_rng.uniform(min_y, max_y)
        else:
            x, y = near[0] + self.env_rng.uniform(-spread, spread), near[1] + self.env_rng.uniform(-spread, spread)
        return max(min_x, min(max_x, x)), max(min_y, min(max_y, y))

    def _spawn_fire(self, game_map, target):
        for i in range(TUNE["env_fire_count"][self.phase]):
            x, y = self._random_spot(game_map, (target.wx, target.wy), 1.8) if i == 0 else self._random_spot(game_map)
            self.hazards.append(BossHazard("fireball", x, y, self._scaled(TUNE["env_fire_warn"]) + 0.3 * i, 0.25, r=TUNE["env_fire_radius"]))

    def _spawn_trap(self, game_map, target):
        for i in range(TUNE["env_trap_count"][self.phase]):
            x, y = self._random_spot(game_map, (target.wx, target.wy), 0.6) if i == 0 else self._random_spot(game_map)
            self.hazards.append(BossHazard("spikes", x, y, self._scaled(TUNE["env_trap_warn"]) + 0.2 * i, TUNE["env_trap_active"],
                                           r=TUNE["env_trap_radius"]))

    def _spawn_lava(self, game_map, target):
        """Rio de lava que nasce num canto e atravessa a arena rumo ao canto oposto (puxado para o jogador)."""
        min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
        corners = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        first = self.env_rng.randrange(4)
        for n in range(2 if self.phase == 4 else 1):
            sx, sy = corners[(first + 2 * n) % 4]
            ox, oy = corners[(first + 2 * n + 2) % 4]
            ex, ey = ox + (target.wx - ox) * 0.4, oy + (target.wy - oy) * 0.4
            length = math.hypot(ex - sx, ey - sy) or 1.0
            dx, dy = (ex - sx) / length, (ey - sy) / length
            length += 3.0  # sai da arena
            active = (length + TUNE["env_lava_slab"]) / TUNE["env_lava_speed"]
            self.hazards.append(BossHazard("lava", sx, sy, self._scaled(TUNE["env_lava_warn"]) + 0.8 * n, active, dx=dx, dy=dy, len=length,
                                           width=TUNE["env_lava_width"], speed=TUNE["env_lava_speed"], slab=TUNE["env_lava_slab"]))

    def _finish_transform(self, target, banners):
        self._reset_brain()
        if self.phase in (2, 4) and target is not None and target.is_alive and target.hp < target.max_hp:
            target.hp += 1
            self.events.append("heal")

    def tick_transform(self, dt: float, target=None, banners=None):
        """Chamada pelo laço depois de `model.update`: avisa quando a transformação termina."""

    # ------------------------------------------------------------------ cérebros
    def _face(self, target):
        self.set_facing(target.wx, target.wy)

    def _brain_stand(self, dt, game_map, target, particles, banners, camera):
        """Fase 1: pisada e varredura do facão; só tornozelos e canelas são vulneráveis."""
        self.sub_t += dt
        sub = self.sub
        dist = math.hypot(target.wx - self.wx, target.wy - self.wy)
        if sub == "idle":
            self._face(target)
            if dist > 3.0:
                self._walk_toward(target, TUNE["p1_walk_speed"], dt, game_map)
            if self.sub_t >= self.sub_data.setdefault("gap", self.rng.uniform(*TUNE["p1_gap"])):
                choice = self.rng.choice(("stomp", "sweep"))
                if len(self.last_attacks) >= 2 and self.last_attacks[-1] == self.last_attacks[-2] == choice:
                    choice = "sweep" if choice == "stomp" else "stomp"
                self.last_attacks.append(choice)
                self.sub, self.sub_t, self.sub_data = f"{choice}_warn", 0.0, {"lock": (target.wx, target.wy)}
                if choice == "stomp":
                    x, y = self.sub_data["lock"]
                    self.hazards.append(BossHazard("circle", x, y, self._scaled(TUNE["p1_stomp_warn"]), 0.15, r=TUNE["p1_stomp_radius"]))
                else:
                    ang = math.atan2(self.facing_y, self.facing_x)
                    self.sub_data["dir"] = ang
                    self.hazards.append(BossHazard("sector", self.wx, self.wy, self._scaled(TUNE["p1_sweep_warn"]), TUNE["p1_sweep_active"],
                                                   r=TUNE["p1_sweep_radius"], dir=ang, half=math.pi / 2))
        elif sub == "stomp_warn":
            warn = self._scaled(TUNE["p1_stomp_warn"])
            self.pose["stomp"] = min(1.0, self.sub_t / (warn * 0.85))
            if self.sub_t >= warn:
                x, y = self.sub_data["lock"]
                self.pose["stomp"] = 0.0
                self.hazards.append(BossHazard("ring", x, y, 0.0, TUNE["p1_ring_max"] / TUNE["p1_ring_speed"], r0=TUNE["p1_stomp_radius"],
                                               speed=TUNE["p1_ring_speed"], width=0.6))
                if camera is not None:
                    camera.add_shake(14.0)
                self._dust(particles, x, y)
                self.sub, self.sub_t = "recover", 0.0
        elif sub == "sweep_warn":
            warn = self._scaled(TUNE["p1_sweep_warn"])
            self.pose["sweep"] = -math.pi / 2 - 0.35 * min(1.0, self.sub_t / warn)
            if self.sub_t >= warn:
                self.sub, self.sub_t = "sweep_active", 0.0
        elif sub == "sweep_active":
            k = min(1.0, self.sub_t / TUNE["p1_sweep_active"])
            self.pose["sweep"] = -math.pi / 2 + math.pi * k
            if k >= 1.0:
                self.pose["sweep"] = None
                self.sub, self.sub_t = "recover", 0.0
        elif sub == "recover":
            self.pose["sweep"] = None
            if self.sub_t >= TUNE["p1_recover"]:
                self.sub, self.sub_t, self.sub_data = "idle", 0.0, {}
        self.vulnerable = self.sub != "sweep_active"

    def _walk_toward(self, target, speed, dt, game_map):
        dx, dy = target.wx - self.wx, target.wy - self.wy
        n = math.hypot(dx, dy) or 1.0
        self._move(self.wx + dx / n * speed * dt, self.wy + dy / n * speed * dt, game_map)

    def _move(self, x, y, game_map) -> bool:
        """Move respeitando os limites e as rochas (sólidos); devolve True se bateu em uma rocha."""
        min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
        x, y = max(min_x, min(max_x, x)), max(min_y, min(max_y, y))
        hit_rock = False
        for rock in game_map.rocks:
            c, px, py = rock.check_collision(x, y, 0.6)
            if c:
                x += px
                y += py
                hit_rock = True
        self.wx, self.wy = x, y
        return hit_rock

    def _dust(self, particles, x, y, n: int = 14):
        if particles is None:
            return
        for _ in range(n):
            particles.append(SmokeParticle(x + self.rng.uniform(-1.2, 1.2), y + self.rng.uniform(-1.2, 1.2), wz=self.rng.uniform(0.05, 0.5),
                                           color=(140, 130, 112), radius=self.rng.uniform(0.2, 0.4), lifetime=self.rng.uniform(0.5, 0.9)))

    # --- Fase 2: serpente -------------------------------------------------
    def _new_ellipse(self, target, game_map):
        """Elipse com o eixo maior ligando a cabeça ao jogador, para a volta cruzar a posição dele."""
        hx, hy = self.wx, self.wy
        dx, dy = target.wx - hx, target.wy - hy
        d = math.hypot(dx, dy)
        ux, uy = (dx / d, dy / d) if d > 0.5 else (self.facing_x, self.facing_y)
        a = max(3.6, d / 2.0 + self.rng.uniform(0.0, 1.0))
        b = self.rng.uniform(2.4, 3.6)
        cx, cy = hx + ux * a, hy + uy * a
        min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
        cx, cy = max(min_x + b, min(max_x - b, cx)), max(min_y + b, min(max_y - b, cy))
        th = math.atan2(hy - cy, hx - cx)
        direction = self.rng.choice((-1, 1))
        a = max(2.5, min(a, math.hypot(hx - cx, hy - cy)))
        return {"cx": cx, "cy": cy, "a": a, "b": b, "th": th, "dir": direction, "s": 0.0, "s0": 0.0}

    @staticmethod
    def _ellipse_point(e, s):
        ex, ey = e["a"] * math.cos(s), e["b"] * math.sin(s)
        c, sn = math.cos(e["th"]), math.sin(e["th"])
        return (e["cx"] + ex * c - ey * sn, e["cy"] + ex * sn + ey * c)

    def _brain_serpent(self, dt, game_map, target, particles, banners, camera):
        """Fase 2: telegrafa a elipse, percorre uma volta atropelando e desacelera com a cabeça baixa (janela de dano)."""
        self.sub_t += dt
        sub = self.sub
        self.pose["head_up"] = 1.0
        if sub == "idle":
            e = self._new_ellipse(target, game_map)
            pts = [self._ellipse_point(e, i / 48 * math.tau) for i in range(48)]
            self.sub_data = {"e": e}
            warn = self._scaled(TUNE["p2_telegraph"])
            lap = math.tau * (e["a"] + e["b"]) / 2.0 / TUNE["p2_speed"]
            self.hazards.append(BossHazard("path", 0, 0, warn, 0.0, points=pts, life=lap))
            self.sub, self.sub_t = "telegraph", 0.0
        elif sub == "telegraph":
            if self.sub_t >= self._scaled(TUNE["p2_telegraph"]):
                self.sub, self.sub_t = "run", 0.0
        elif sub == "run":
            e = self.sub_data["e"]
            omega = TUNE["p2_speed"] / ((e["a"] + e["b"]) / 2.0)
            e["s"] += e["dir"] * omega * dt
            x, y = self._ellipse_point(e, e["s"])
            old = (self.wx, self.wy)
            hit_rock = self._move(x, y, game_map)
            if math.dist(old, (self.wx, self.wy)) > 1e-4:
                self.set_facing(self.wx + (self.wx - old[0]), self.wy + (self.wy - old[1]))
            self._push_trail()
            self._serpent_contact(target, game_map, particles, banners, camera)
            if hit_rock:
                self.sub, self.sub_t = "stun", 0.0
                if camera is not None:
                    camera.add_shake(10.0)
                self._dust(particles, self.wx, self.wy, 10)
            elif abs(e["s"]) >= math.tau - 0.05:
                self.sub, self.sub_t = "slow", 0.0
        elif sub in ("slow", "stun"):
            span = TUNE["p2_slow"] if sub == "slow" else TUNE["p2_stun"]
            self.pose["head_up"] = -0.6
            if sub == "slow" and self.sub_t < 0.4:
                e = self.sub_data["e"]
                e["s"] += e["dir"] * (TUNE["p2_speed"] * 0.25 / ((e["a"] + e["b"]) / 2.0)) * dt
                x, y = self._ellipse_point(e, e["s"])
                self._move(x, y, game_map)
                self._push_trail()
                self._serpent_contact(target, game_map, particles, banners, camera)
            if self.sub_t >= span:
                self.sub, self.sub_t, self.sub_data = "idle", 0.0, {}
        self.vulnerable = self.sub in ("slow", "stun")
        if self.vulnerable:
            self.pose["head_up"] = -0.6

    def _push_trail(self):
        if math.dist(self.trail[0], (self.wx, self.wy)) >= 0.2:
            self.trail.insert(0, (self.wx, self.wy))
            del self.trail[80:]
        else:
            self.trail[0] = (self.wx, self.wy)

    def _serpent_contact(self, target, game_map, particles, banners, camera):
        for d in (0.0, 0.8, 1.6, 2.4, 3.2, 4.0, 4.8):
            px, py = self.trail_point(d)
            if math.hypot(target.wx - px, target.wy - py) < TUNE["p2_contact"] + target.radius:
                self._hurt_player(target, (px, py), game_map, particles, banners, camera, 1)
                return

    # --- Fase 3: torso quicando ------------------------------------------
    def _brain_torso(self, dt, game_map, target, particles, banners, camera):
        self.sub_t += dt
        sub = self.sub
        if sub == "idle":
            dx, dy = target.wx - self.wx, target.wy - self.wy
            n = math.hypot(dx, dy) or 1.0
            ang = math.atan2(dy, dx) + self.rng.uniform(-0.35, 0.35)
            self.sub_data = {"dir": (math.cos(ang), math.sin(ang)), "speed": TUNE["p3_speed"], "flight": 0.0}
            self.set_facing(self.wx + self.sub_data["dir"][0], self.wy + self.sub_data["dir"][1])
            self.hazards.append(BossHazard("arrow", self.wx, self.wy, self._scaled(TUNE["p3_aim"]), 0.0, dx=self.sub_data["dir"][0],
                                           dy=self.sub_data["dir"][1], len=7.0))
            self.sub, self.sub_t = "aim", 0.0
        elif sub == "aim":
            if self.sub_t >= self._scaled(TUNE["p3_aim"]):
                self.sub, self.sub_t = "bounce", 0.0
        elif sub == "bounce":
            d = self.sub_data
            d["flight"] += dt
            self.bounce_phase += dt * (2.0 + d["speed"] * 0.5)
            self.wz = 0.9 * abs(math.sin(self.bounce_phase * 2.0))
            vx, vy = d["dir"][0] * d["speed"], d["dir"][1] * d["speed"]
            nx, ny = self.wx + vx * dt, self.wy + vy * dt
            min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
            bounced = False
            if nx < min_x or nx > max_x:
                d["dir"] = (-d["dir"][0], d["dir"][1])
                bounced = True
            if ny < min_y or ny > max_y:
                d["dir"] = (d["dir"][0], -d["dir"][1])
                bounced = True
            hit_rock = self._move(nx, ny, game_map)
            if bounced:
                d["speed"] = min(TUNE["p3_speed_max"], d["speed"] + TUNE["p3_speed_gain"])
                self._dust(particles, self.wx, self.wy, 5)
            if self.wz < 0.55 and math.hypot(target.wx - self.wx, target.wy - self.wy) < 0.95 + target.radius:
                self._hurt_player(target, (self.wx, self.wy), game_map, particles, banners, camera, 1)
            if hit_rock or d["flight"] > TUNE["p3_tired_after"]:
                if camera is not None and hit_rock:
                    camera.add_shake(12.0)
                self.sub, self.sub_t = "stun", 0.0
                self.wz = 0.0
        elif sub == "stun":
            self.wz = 0.0
            if self.sub_t >= TUNE["p3_stun"]:
                self.sub, self.sub_t, self.sub_data = "idle", 0.0, {}
        self.vulnerable = self.sub == "stun"

    # --- Fase 4: clava ---------------------------------------------------
    def _brain_club(self, dt, game_map, target, particles, banners, camera):
        self.sub_t += dt
        sub = self.sub
        if sub == "idle":
            self._face(target)
            self.pose["raise"] = max(0.0, self.pose["raise"] - dt * 2.0)
            if self.sub_t >= TUNE["p4_idle"]:
                err = TUNE["p4_aim_error"]
                lx, ly = target.wx + self.rng.uniform(-err, err), target.wy + self.rng.uniform(-err, err)
                min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                lx, ly = max(min_x, min(max_x, lx)), max(min_y, min(max_y, ly))
                warn = self._scaled(TUNE["p4_warn"])
                self.sub_data = {"land": (lx, ly)}
                self.hazards.append(BossHazard("circle", lx, ly, warn + TUNE["p4_jump"], 0.2, r=TUNE["p4_radius"]))
                self.sub, self.sub_t = "warn", 0.0
        elif sub == "warn":
            warn = self._scaled(TUNE["p4_warn"])
            self.pose["raise"] = min(1.0, self.sub_t / warn)
            self._face(target)
            if self.sub_t >= warn:
                self.sub_data["from"] = (self.wx, self.wy)
                self.sub, self.sub_t = "jump", 0.0
        elif sub == "jump":
            k = min(1.0, self.sub_t / TUNE["p4_jump"])
            fx, fy = self.sub_data["from"]
            lx, ly = self.sub_data["land"]
            self.wx, self.wy = fx + (lx - fx) * k, fy + (ly - fy) * k
            self.wz = 2.4 * math.sin(math.pi * k)
            if k >= 1.0:
                self.wz = 0.0
                self.pose["raise"] = 0.0
                if camera is not None:
                    camera.add_shake(16.0)
                self._dust(particles, lx, ly)
                self.hazards.append(BossHazard("ring", lx, ly, 0.0, 0.35, r0=TUNE["p4_radius"] - 0.3, speed=4.0, width=0.5))
                self.sub, self.sub_t = "stuck", 0.0
        elif sub == "stuck":
            if self.sub_t >= TUNE["p4_stuck"]:
                self.sub, self.sub_t, self.sub_data = "idle", 0.0, {}
        self.vulnerable = self.sub == "stuck"

    # --- Fase 5: crânio ---------------------------------------------------
    def _brain_skull(self, dt, game_map, target, particles, banners, camera):
        self.sub_t += dt
        sub = self.sub
        warns = TUNE["p5_warns"]
        if sub == "idle":
            self._face(target)
            self.sub_data = {"i": 0}
            self.sub = "aim"
            self.sub_t = 0.0
            self._skull_aim(target, warns[0], game_map)
        elif sub == "aim":
            self.pose["jaw"] = 0.25 * math.sin(self.time * 18.0)
            if self.sub_t >= self._scaled(warns[self.sub_data["i"]]):
                self.sub_data["from"] = (self.wx, self.wy)
                self.sub, self.sub_t = "jump", 0.0
        elif sub == "jump":
            k = min(1.0, self.sub_t / TUNE["p5_jump"])
            fx, fy = self.sub_data["from"]
            lx, ly = self.sub_data["land"]
            self.wx, self.wy = fx + (lx - fx) * k, fy + (ly - fy) * k
            self.wz = 2.2 * math.sin(math.pi * k)
            if k >= 1.0:
                self.wz = 0.0
                if camera is not None:
                    camera.add_shake(12.0)
                self._dust(particles, lx, ly, 10)
                dist = math.hypot(target.wx - lx, target.wy - ly)
                if dist < TUNE["p5_direct"] + target.radius:
                    self._hurt_player(target, (lx, ly), game_map, particles, banners, camera, 2)
                elif dist < TUNE["p5_radius"]:
                    self._hurt_player(target, (lx, ly), game_map, particles, banners, camera, 1)
                self.sub_data["i"] += 1
                if self.sub_data["i"] >= len(warns):
                    self.sub, self.sub_t = "rest", 0.0
                else:
                    self.sub, self.sub_t = "aim", 0.0
                    self._skull_aim(target, warns[self.sub_data["i"]], game_map)
        elif sub == "rest":
            self.pose["jaw"] = 0.2
            if self.sub_t >= TUNE["p5_rest"]:
                self.sub, self.sub_t, self.sub_data = "idle", 0.0, {}
        self.vulnerable = self.sub == "rest"

    def _skull_aim(self, target, warn, game_map):
        lx, ly = target.wx + self.rng.uniform(-0.5, 0.5), target.wy + self.rng.uniform(-0.5, 0.5)
        min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
        lx, ly = max(min_x, min(max_x, lx)), max(min_y, min(max_y, ly))
        self.sub_data["land"] = (lx, ly)
        self.hazards.append(BossHazard("circle", lx, ly, self._scaled(warn) + TUNE["p5_jump"], 0.2, r=TUNE["p5_radius"]))

    # ------------------------------------------------------------------ desenho
    def poses(self) -> dict:
        return self.model.poses(self.current_layout())

    def render_ground(self, surface, camera, game_time: float = 0.0):
        """Sombra no chão sob o chefe."""
        cx, cy = camera.apply(self.wx, self.wy, 0.0)
        zoom = getattr(camera, "zoom", 1.0)
        w = int((2.4 if self.phase != 1 else 1.4) * 64 * zoom)
        shadow = pygame.Surface((w, w // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 90), shadow.get_rect())
        surface.blit(shadow, (cx - w // 2, cy - w // 4))

    def render(self, surface, camera, game_time: float = 0.0):
        self.render_ground(surface, camera)
        self.model.draw(surface, camera, self.poses(), self.alpha)
