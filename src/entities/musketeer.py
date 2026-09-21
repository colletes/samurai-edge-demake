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
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_PARRY
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import MusketBulletProjectile
from src.effects.particles import SparkParticle

class Musketeer(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Julie (Musketeer)")
        self.char_type = "musketeer"
        self.speed = 4.4

        # Mecânica do Florete (Fleche Lunge)
        self.thrust_cooldown = 0.45
        self.thrust_timer = 0.0

        # Riposte com Capa & Pistola Flintlock
        self.riposte_cooldown = 3.5
        self.riposte_timer = 0.0
        self.has_flintlock = True

    def can_act(self) -> bool:
        return self.is_alive and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD)

    def trigger_fleche_thrust(self, target_wx: float, target_wy: float):
        """Ataque Primário: Estocada relâmpago de esgrima clássica com o florete."""
        if not self.can_act() or self.thrust_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.22
        self.hitbox_active = True
        self.hitbox_radius = 1.30
        self.slash_dir = (self.facing_x, self.facing_y)
        self.hitbox_center = (self.wx + self.facing_x * 0.90, self.wy + self.facing_y * 0.90)
        self.thrust_timer = self.thrust_cooldown

    def trigger_cloak_riposte(self, target_wx: float = None, target_wy: float = None, projectiles: list = None, particles: list = None):
        """
        Ação Secundária: Riposte de Capa e Tiro de Pederneira (Flintlock).
        Entra em postura de defesa e dispara um tiro rápido.
        """
        if not self.can_act() or self.riposte_timer > 0:
            return

        if target_wx is not None and target_wy is not None:
            self.set_facing(target_wx, target_wy)
        self.riposte_timer = self.riposte_cooldown
        self.state = STATE_PARRY
        self.state_timer = 0.28
        self.is_riposte_ready = True

        # Disparo da pistola de pederneira (se projectiles fornecido)
        if projectiles is not None:
            bx = self.wx + self.facing_x * 0.55
            by = self.wy + self.facing_y * 0.55
            bullet = MusketBulletProjectile(bx, by, wz=0.55, dir_x=self.facing_x, dir_y=self.facing_y, owner=self)
            projectiles.append(bullet)

            if particles is not None:
                for _ in range(12):
                    particles.append(SparkParticle(bx, by, 0.5))

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.thrust_timer > 0:
            self.thrust_timer -= dt
        if self.riposte_timer > 0:
            self.riposte_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Bote linear veloz de esgrima
            step = 6.2 * dt
            self.wx = max(1.0, min(game_map.cols - 1.0, self.wx + self.facing_x * step))
            self.wy = max(1.0, min(game_map.rows - 1.0, self.wy + self.facing_y * step))
            self.hitbox_center = (self.wx + self.facing_x * 0.90, self.wy + self.facing_y * 0.90)

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.14
                self.hitbox_active = False

        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

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
