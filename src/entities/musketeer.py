"""
Julie (A Mosqueteira de Florete):
Duelista de esgrima clássica capa e espada. Rápida e elegante com a lâmina
fina do florete (Fleche Thrust) e riposte defensivo de capa com tiro de pederneira (Flintlock).
"""
import math
import random
import pygame
from src.config import (
    COLOR_MUSKETEER_BLUE, COLOR_MUSKETEER_HAT, COLOR_MUSKETEER_AURA, COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_PARRY, STATE_ROLL
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import MusketBulletProjectile
from src.effects.particles import SparkParticle

class Musketeer(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Julie")
        self.char_type = "musketeer"
        self.speed = 4.4

        # Ataque Primário: Fleche Thrust (+25% alcance, bote linear cirúrgico de esgrima)
        self.thrust_cooldown = 0.48
        self.thrust_timer = 0.0

        # Ação Secundária: Floreio de Capa com Chute de Repulsão (Cape Flourish & Deflection)
        self.cape_cooldown = 2.4
        self.cape_timer = 0.0

        # Arma Secundária de Bolso: Pistola Pederneira (Pocket Flintlock)
        self.flintlock_cooldown = 4.5
        self.flintlock_timer = 1.0  # Inicia com 1.0s no round para evitar tiro instantâneo no spawn

        # Terceira Ação: Rolamento de Mosqueteira (grande: cobre buracos largos e desvia projéteis)
        self.is_agile_dodge = False
        self.roll_speed = 9.5
        self.roll_duration = 0.34
        self.roll_recovery_duration = 0.20
        self.roll_cooldown_duration = 0.60

    def on_round_start(self):
        """Inicia o cooldown inicial da pederneira no momento exato em que o round começa."""
        self.flintlock_timer = 1.0

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, "CAPE_FLOURISH")
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_fleche_thrust(self, target_wx: float, target_wy: float):
        """
        Ataque Primário: Fleche Thrust.
        Estocada de florete linear com +25% de alcance e hitbox refinada (0.70m).
        """
        if not self.can_act() or self.thrust_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.20
        self.hitbox_active = True
        self.hitbox_radius = 0.70  # Calibrada para evitar errar esquivas diagonais
        self.slash_dir = (self.facing_x, self.facing_y)
        # Alcance estendido à frente
        self.hitbox_center = (self.wx + self.facing_x * 1.30, self.wy + self.facing_y * 1.30)
        self.thrust_timer = self.thrust_cooldown

    def trigger_flintlock_shot(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None):
        """
        Disparo de Pederneira de Bolso (Pocket Flintlock):
        Disparo veloz à média/longa distância para conter zhoners e punir aproximações descuidadas.
        """
        if not self.can_act() or self.flintlock_timer > 0 or projectiles is None:
            return

        self.set_facing(target_wx, target_wy)
        self.flintlock_timer = self.flintlock_cooldown

        dx = target_wx - self.wx
        dy = target_wy - self.wy
        length = math.hypot(dx, dy)
        if length > 0.001:
            dir_x = dx / length
            dir_y = dy / length
        else:
            dir_x, dir_y = self.facing_x, self.facing_y

        # Cria projétil veloz de pederneira de curto/médio alcance (Item 20: max_range=5.8)
        projectiles.append(MusketBulletProjectile(self.wx, self.wy, 0.45, dir_x, dir_y, owner=self, max_range=5.8))

        # Recuo sutil do tiro de pederneira
        self.wx -= dir_x * 0.25
        self.wy -= dir_y * 0.25

        if particles is not None:
            for _ in range(16):
                particles.append(SparkParticle(self.wx + dir_x * 0.5, self.wy + dir_y * 0.5, 0.45, color=(255, 210, 100)))

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None):
        """Terceira Ação: rolamento grande com i-frames; a capa desvia projéteis durante o giro (ver CombatSystem)."""
        if self.state == "CAPE_FLOURISH":
            return
        super().trigger_roll(dir_x, dir_y, particles)

    def trigger_cape_flip(self, dir_x: float, dir_y: float, particles: list = None, opponent=None):
        """
        Floreio de Capa & Coup de Pied: salto curto com giro da capa que desvia projéteis
        e repele oponentes a curta distância.
        """
        if (not self.is_alive or self.cape_timer > 0 or self.dash_recovery_timer > 0
                or self.state in (STATE_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK, "CAPE_FLOURISH")):
            return

        if dir_x == 0 and dir_y == 0:
            dir_x, dir_y = -self.facing_x, -self.facing_y
        else:
            mag = math.hypot(dir_x, dir_y)
            if mag > 0.001:
                dir_x /= mag
                dir_y /= mag

        self.facing_x = dir_x
        self.facing_y = dir_y
        self.state = "CAPE_FLOURISH"
        self.state_timer = 0.16
        self.cape_timer = self.cape_cooldown
        self.is_invulnerable_dodge = True
        self.hitbox_active = False

        self.wx += dir_x * 0.45
        self.wy += dir_y * 0.45

        if particles is not None:
            for i in range(12):
                angle = (i / 12.0) * math.pi * 2
                px = self.wx + math.cos(angle) * 0.65
                py = self.wy + math.sin(angle) * 0.65
                particles.append(SparkParticle(px, py, 0.4, color=(100, 175, 255)))

        if opponent is not None and getattr(opponent, "is_alive", False):
            dist = math.hypot(self.wx - opponent.wx, self.wy - opponent.wy)
            if dist < 1.65:
                if hasattr(opponent, "stun"):
                    opponent.stun(0.35)
                opponent.wx += self.facing_x * 2.0
                opponent.wy += self.facing_y * 2.0

    def trigger_secondary(self, aim_x: float, aim_y: float, projectiles: list, particles: list = None, opponent=None) -> str | None:
        """Ação Secundária contextual: tiro de pederneira quando pronto; com a pistola recarregando, o floreio de capa."""
        if self.flintlock_timer <= 0 and projectiles is not None and self.can_act():
            self.trigger_flintlock_shot(aim_x, aim_y, projectiles, particles)
            return "shot"
        self.trigger_cape_flourish(aim_x, aim_y, opponent=opponent, particles=particles)
        return "flip" if self.state == "CAPE_FLOURISH" else None

    def trigger_cape_flourish(self, target_wx: float = None, target_wy: float = None, opponent = None, particles: list = None, banners: list = None, projectiles: list = None):
        """Floreio de capa na direção do alvo (IA e chamadas legadas)."""
        dir_x, dir_y = self.facing_x, self.facing_y
        if target_wx is not None and target_wy is not None:
            dx = target_wx - self.wx
            dy = target_wy - self.wy
            mag = math.hypot(dx, dy)
            if mag > 0.001:
                dir_x, dir_y = dx / mag, dy / mag
        self.trigger_cape_flip(dir_x, dir_y, particles=particles, opponent=opponent)

    def trigger_cloak_riposte(self, target_wx: float = None, target_wy: float = None, projectiles: list = None, particles: list = None, opponent = None, banners: list = None):
        """Compatibilidade para chamadas legadas: redireciona para o floreio de capa/esquiva."""
        self.trigger_cape_flourish(target_wx, target_wy, opponent=opponent, particles=particles, banners=banners, projectiles=projectiles)

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.thrust_timer > 0:
            self.thrust_timer -= dt
        if self.cape_timer > 0:
            self.cape_timer -= dt
        if self.flintlock_timer > 0:
            self.flintlock_timer -= dt
        self.update_dodge_timers(dt)

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Bote linear veloz de fleche
            step = 7.5 * dt
            self.wx = max(1.0, min(game_map.cols - 1.0, self.wx + self.facing_x * step))
            self.wy = max(1.0, min(game_map.rows - 1.0, self.wy + self.facing_y * step))
            self.hitbox_center = (self.wx + self.facing_x * 1.30, self.wy + self.facing_y * 1.30)

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.18  # Recovery reduzido (era 0.28s) para punição justa sem paralisia letal
                self.hitbox_active = False

        elif self.state == "CAPE_FLOURISH":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.is_invulnerable_dodge = False
                self.dash_recovery_timer = self.dash_recovery_duration

        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_ROLL:
            self.update_roll(dt, game_map)

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="musketeer",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving
        )
