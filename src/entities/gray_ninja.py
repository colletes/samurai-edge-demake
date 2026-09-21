"""
Ninja Cinza (Kemuri): Mestre em explosivos com delay e bombas de fumaça com slow para fuga.
"""
import math
import pygame
from src.config import (
    COLOR_GRAY_NINJA, COLOR_GRAY_DARK, COLOR_SMOKE, COLOR_WHITE, COLOR_BLACK, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import TimedBombEntity, SmokeCloudEntity
from src.entities.voxel_models import render_voxel_humanoid

class GrayNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Kemuri (Gray Ninja)")
        self.speed = 4.8
        self.bomb_cooldown = 1.2
        self.bomb_timer = 0.0
        self.smoke_cooldown = 3.5
        self.smoke_timer = 0.0

    def trigger_throw_bomb(self, target_wx: float, target_wy: float, projectiles: list):
        """Ataque Primário: Arremessa bomba com pavio de 1.5s que explode em área (1-hit fatal)."""
        if not self.can_move() or self.bomb_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.bomb_timer = self.bomb_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.14

        # Lança a bomba na direção do alvo a ~2.5 tiles
        throw_dist = min(3.5, math.hypot(target_wx - self.wx, target_wy - self.wy))
        bx = self.wx + self.facing_x * throw_dist
        by = self.wy + self.facing_y * throw_dist

        bomb = TimedBombEntity(wx=bx, wy=by, owner=self)
        projectiles.append(bomb)

    def trigger_smoke_bomb(self, target_wx: float, target_wy: float, projectiles: list):
        """Ataque Secundário: Bomba de fumaça instantânea que dá slow ao oponente e permite fuga."""
        if not self.can_move() or self.smoke_timer > 0:
            return

        self.smoke_timer = self.smoke_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.16

        # Cortina de fumaça instantânea no chão
        smoke = SmokeCloudEntity(wx=self.wx, wy=self.wy, owner=self)
        projectiles.append(smoke)

        # Recuo evasivo do Ninja Cinza para escapar
        self.wx -= self.facing_x * 0.9
        self.wy -= self.facing_y * 0.9
        self.alpha = 90  # Camuflagem de fuga na fumaça

    def update(self, dt: float, game_map):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.bomb_timer > 0:
            self.bomb_timer -= dt
        if self.smoke_timer > 0:
            self.smoke_timer -= dt

        if self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Ninja Cinza no autêntico estilo Voxel 3D Isométrico."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="gray",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving
        )
