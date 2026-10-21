"""
Aoi (A Caçadora Ainu de Hokkaido - Ciclo 5):
Jovem guerreira e rastreadora indígena Ainu das florestas boreais de Ezo (Hokkaido).
- Arquétipo: Caçadora ágil de controle de terreno, armadilhas e estocadas precisas (velocidade 5.15, 2 HP).
- Guarda de Caça (Parry técnico desviando lâminas com a haste da lança Op e a faca Makiri).
- Ataque Primário: Estocada de Lança Op / Makiri-Spear (SPEAR_THRUST) - bote perfurante veloz (alcance 2.15m, raio 1.05m, execução 0.15s).
- Ação Secundária: Armadilha de Urso (PLANT_BEAR_TRAP) - planta no solo uma armadilha de ferro dentada (máx. 2 ativas) enquanto dá um passo tático para trás; o rival que pisar sofre 1 de dano, fica imobilizado na posição e vulnerável à execução. Cooldown 3.4s.
- Esquiva: Deslize na Neve (SNOW_SLIDE) - rolamento rasteiro de caçadora com partículas de gelo/neve e i-frames.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_AOI_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, STATE_PARRY, resolve_playable_bounds
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import BearTrapProjectile
from src.effects.particles import SparkParticle, SmokeParticle, FloatingBanner


class AoiHuntress(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Aoi")
        self.char_type = "aoi"
        self.speed = 5.15
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Ataque Primário: Estocada Veloz de Lança Op
        self.spear_duration = 0.15
        self.spear_recovery = 0.17
        self.spear_reach = 2.15
        self.spear_radius = 1.05

        # Ação Secundária: Armadilha de Urso (Bear Trap)
        self.trap_cooldown = 3.4
        self.trap_timer = 0.0
        self.active_traps: list[BearTrapProjectile] = []

        # Esquiva: Deslize Ágil na Neve
        self.is_agile_dodge = True
        self.roll_speed = 9.4
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.15
        self.roll_cooldown_duration = 0.34
        self.recovery_duration = self.spear_recovery

    def trigger_parry(self) -> bool:
        """Guarda Ainu: desvia golpes com a haste da lança Op e a faca Makiri."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.38
        return True

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_spear_thrust(self, aim_x: float, aim_y: float, particles: list = None) -> bool:
        """Ataque Primário: Estocada rápida e letal com a lança de caça Op."""
        if not self.can_act():
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.spear_duration
        self.hitbox_active = True
        self.hitbox_damage = 2

        self.hitbox_center = (
            self.wx + self.facing_x * 1.25,
            self.wy + self.facing_y * 1.25
        )
        self.hitbox_radius = self.spear_radius
        self.slash_dir = (self.facing_x, self.facing_y)
        return True

    def trigger_bear_trap(self, aim_x: float = None, aim_y: float = None, projectiles: list = None, particles: list = None, banners: list = None, game_map=None) -> bool:
        """
        Ação Secundária: Planta uma Armadilha de Urso de ferro dentado à frente de Aoi
        e recua em passo ágil de caçadora.
        """
        if not self.can_act() or self.trap_timer > 0 or projectiles is None:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        trap_x = self.wx + self.facing_x * 1.15
        trap_y = self.wy + self.facing_y * 1.15

        if game_map is not None:
            min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
            trap_x = max(min_x + 0.35, min(max_x - 0.35, trap_x))
            trap_y = max(min_y + 0.35, min(max_y - 0.35, trap_y))

        # Limitar a 2 armadilhas ativas simultaneamente
        self.active_traps = [t for t in self.active_traps if getattr(t, "is_active", False)]
        if len(self.active_traps) >= 2:
            oldest = self.active_traps.pop(0)
            oldest.detonate()

        trap = BearTrapProjectile(trap_x, trap_y, owner=self, duration=9.0)
        self.active_traps.append(trap)
        projectiles.append(trap)

        # Passo ágil de recuo ao armar a armadilha no solo
        back_x = self.wx - self.facing_x * 0.65
        back_y = self.wy - self.facing_y * 0.65
        if game_map is not None:
            min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
            self.wx = max(min_x, min(max_x, back_x))
            self.wy = max(min_y, min(max_y, back_y))
        else:
            self.wx, self.wy = back_x, back_y

        self.trap_timer = self.trap_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.14

        if banners is not None:
            banners.append(FloatingBanner("TRAP SET!", trap_x, trap_y, wz=1.4, color=COLOR_AOI_AURA, duration=0.75))

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(trap_x, trap_y, 0.12, color=(205, 225, 245)))

        return True

    def trigger_snow_slide(self, dwx: float, dwy: float, particles: list = None):
        """Esquiva especial: Deslize rasteiro na neve com partículas boreais e i-frames."""
        if not self.can_act() or self.roll_cooldown_timer > 0:
            return
        super().trigger_roll(dwx, dwy, particles)
        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(
                    self.wx + random.uniform(-0.20, 0.20),
                    self.wy + random.uniform(-0.20, 0.20),
                    random.uniform(0.05, 0.30),
                    color=random.choice([(230, 242, 255), (150, 210, 245)])
                ))

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None, **kwargs):
        self.update_dodge_timers(dt)

        if self.trap_timer > 0:
            self.trap_timer = max(0.0, self.trap_timer - dt)

        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            return

        if self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            step_speed = 3.2
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map is not None:
                min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                self.wx = max(min_x, min(max_x, new_wx))
                self.wy = max(min_y, min(max_y, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.25,
                self.wy + self.facing_y * 1.25
            )
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.spear_recovery
                self.hitbox_active = False
            return

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        self.active_traps = [t for t in self.active_traps if getattr(t, "is_active", False)]

    def render(self, surface: pygame.Surface, camera):
        extra = {}
        if self.state in ("DEFEND", "PARRY") or getattr(self, "is_parrying", False):
            extra = {"pose": "hunter_guard"}

        render_voxel_humanoid(
            surface=surface,
            camera=camera,
            wx=self.wx,
            wy=self.wy,
            wz=getattr(self, "wz", 0.0),
            facing_x=self.facing_x,
            facing_y=self.facing_y,
            state=self.state,
            state_timer=self.state_timer,
            is_alive=self.is_alive,
            char_type="aoi",
            walk_timer=getattr(self, "walk_cycle", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
