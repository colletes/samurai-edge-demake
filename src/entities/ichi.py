"""
Ichi (A Lâmina Cega / Shikomizue - Ciclo 3):
Mestra espadachim cega de audição extraordinária (homenagem a Zatoichi).
- Arquétipo: Assassina ágil, precisa e sensorial (velocidade 4.8, 2 HP).
- Ataque Primário: Gyaku-Iai Cego (GYAKU_IAI_SLASH) - saque relâmpago em pegada invertida da espada-bengala oculta (alcance 1.70m, raio 0.95m, execução 0.14s).
- Ação Secundária: Postura de Escuta (LISTEN_STANCE) - postura sensorial de percepção auditiva que concede i-frames e engatilha contra-ataque perfurante automático se atacada. Cooldown 4.2s.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_ICHI_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, STATE_PARRY, resolve_playable_bounds
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle, FloatingBanner

STATE_LISTEN = "LISTEN"
STATE_COUNTER_THRUST = "COUNTER_THRUST"


class IchiBlade(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Ichi")
        self.char_type = "ichi"
        self.speed = 5.1  # Ágil e fluida
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Ataque Primário: Gyaku-Iai (Saque Relâmpago Invertido)
        self.attack_duration = 0.14  # Altíssima velocidade de saque
        self.attack_recovery = 0.20
        self.slash_reach = 1.80
        self.slash_radius = 1.05

        # Ação Secundária: Postura de Escuta & Contra-Ataque Cego
        self.listen_cooldown = 3.8
        self.listen_timer = 0.0
        self.listen_duration = 0.40
        self.counter_active = False

        # Esquiva mais lenta e pesada (design intencional: priorizar parry/escuta)
        self.is_agile_dodge = False
        self.roll_speed = 7.0
        self.roll_duration = 0.28
        self.roll_recovery_duration = 0.24
        self.roll_cooldown_duration = 0.50
        self.recovery_duration = self.attack_recovery

    def trigger_parry(self) -> bool:
        """Parry técnico: bloqueia com a bainha de madeira (Shikomizue)."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.36
        return True

    def is_facing_target(self, target_x: float, target_y: float) -> bool:
        """Verifica se o alvo está no cone frontal de escuta (angulo < 90°)."""
        dx = target_x - self.wx
        dy = target_y - self.wy
        return (dx * self.facing_x + dy * self.facing_y) > 0.0

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_gyaku_iai(self, aim_x: float, aim_y: float) -> bool:
        """Ataque Primário: Saque rápido em pegada invertida da Shikomizue."""
        if not self.can_act():
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.attack_duration
        self.hitbox_active = True
        self.hitbox_damage = 2

        self.hitbox_center = (
            self.wx + self.facing_x * 1.05,
            self.wy + self.facing_y * 1.05
        )
        self.hitbox_radius = self.slash_radius
        self.slash_dir = (self.facing_x, self.facing_y)
        return True

    def trigger_listen_stance(self, aim_x: float = None, aim_y: float = None, banners: list = None, particles: list = None) -> bool:
        """Ação Secundária: Postura de Escuta Auditiva. Foco sensorial que contra-ataca."""
        if not self.can_act() or self.listen_timer > 0:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)
        self.state = STATE_LISTEN
        self.state_timer = self.listen_duration
        self.listen_timer = self.listen_cooldown
        self.hitbox_active = False
        self.counter_active = True

        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(self.wx, self.wy, 0.20, color=(210, 180, 235)))

        if banners is not None:
            banners.append(FloatingBanner("LISTEN...", self.wx, self.wy, color=(220, 170, 240), duration=0.75))

        return True

    def trigger_counter_thrust(self, target_x: float, target_y: float, banners: list = None, particles: list = None):
        """Contra-ataque automático perfurante ativado ao aparar ou desviar durante a Postura de Escuta."""
        self.set_facing(target_x, target_y)
        self.state = STATE_COUNTER_THRUST
        self.state_timer = 0.20
        self.hitbox_active = True
        self.hitbox_damage = 2

        self.hitbox_center = (
            self.wx + self.facing_x * 1.25,
            self.wy + self.facing_y * 1.25
        )
        self.hitbox_radius = 1.0
        self.slash_dir = (self.facing_x, self.facing_y)
        self.counter_active = False

        if banners is not None:
            banners.append(FloatingBanner("BLIND COUNTER!", self.wx, self.wy, color=COLOR_GOLD, duration=0.85))

    def update(self, dt: float, game_map = None, particles: list = None, opponent = None, projectiles: list = None, **kwargs):
        # Atualizar timers de esquiva e recuperação de roll
        self.update_dodge_timers(dt)

        # Atualizar recarga da Postura de Escuta
        if self.listen_timer > 0:
            self.listen_timer = max(0.0, self.listen_timer - dt)

        # Atualizar rolamento se em estado ROLL
        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            return

        # Atualizar estado de atordoamento (STUNNED)
        if self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # Atualizar ataque primário (Gyaku-Iai)
        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Lunge veloz do saque em pegada invertida
            step_speed = 3.6
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map and hasattr(game_map, "cols"):
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.05,
                self.wy + self.facing_y * 1.05
            )
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.attack_recovery
                self.hitbox_active = False
            return

        # Atualizar postura de escuta
        if self.state == STATE_LISTEN:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.counter_active = False
            return

        elif self.state == STATE_COUNTER_THRUST:
            self.state_timer -= dt
            # Estocada perfurante instantânea
            step_speed = 4.2
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map and hasattr(game_map, "cols"):
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.25,
                self.wy + self.facing_y * 1.25
            )
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.16
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

    def render(self, surface: pygame.Surface, camera):
        extra = {}
        if self.state == STATE_LISTEN:
            extra = {"pose": "listen_stance"}
        elif self.state == STATE_COUNTER_THRUST:
            extra = {"is_pierce": True}

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
            char_type="ichi",
            walk_timer=getattr(self, "walk_cycle", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
