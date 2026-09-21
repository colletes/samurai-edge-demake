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
        super().__init__(wx, wy, name="Kasumi")
        self.char_type = "kasumi"
        self.speed = 4.8
        self.bomb_cooldown = 0.65
        self.bomb_timer = 0.0
        self.smoke_cooldown = 2.8
        self.smoke_timer = 0.0

    def trigger_throw_bomb(self, target_wx: float, target_wy: float, projectiles: list):
        """Ataque Primário: Arremessa bomba em arco 3D (até 2 ativas). Detona por contato ou tempo."""
        if not self.can_move():
            return

        # Limitar a no máximo 2 bombas ativas no mapa simultaneamente
        active_bombs = sum(1 for p in projectiles if isinstance(p, TimedBombEntity) and p.owner == self and p.is_active)
        if active_bombs >= 2:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_RECOVERY
        self.state_timer = 0.12

        dx = target_wx - self.wx
        dy = target_wy - self.wy
        dist = math.hypot(dx, dy)
        dir_x = dx / dist if dist > 0.001 else self.facing_x
        dir_y = dy / dist if dist > 0.001 else self.facing_y

        # Arremessada a partir das mãos em arco tridimensional (wz=0.75) com avanço seguro
        bomb = TimedBombEntity(wx=self.wx + dir_x * 0.40, wy=self.wy + dir_y * 0.40, wz=0.75, dir_x=dir_x, dir_y=dir_y, owner=self)
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
