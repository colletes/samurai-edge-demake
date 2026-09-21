"""
American Ninja: Guerreiro tático acompanhado pelo seu leal cão Doberman.
Ataca com Shurikens atordoantes (não matam) e comanda o Doberman para botes letais.
"""
import math
import pygame
from src.config import (
    COLOR_AMERICAN_NINJA, COLOR_AMERICAN_VEST, COLOR_AMERICAN_BANDANA,
    COLOR_STEEL, COLOR_WHITE, COLOR_BLACK, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.doberman import DobermanDog
from src.entities.projectile import ShurikenProjectile
from src.entities.voxel_models import render_voxel_humanoid

class AmericanNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Joe (American Ninja)")
        self.speed = 4.8

        # O Cão Doberman companheiro
        self.dog = DobermanDog(self)

        # Timings de Shuriken e Comando
        self.shuriken_cooldown = 0.35
        self.shuriken_timer = 0.0

    def trigger_shuriken(self, target_wx: float, target_wy: float, projectiles: list):
        """Arremessa uma shuriken atordoante (não mata, mas dá stun de 0.48s)."""
        if not self.can_move() or self.shuriken_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.shuriken_timer = self.shuriken_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.12

        shuriken = ShurikenProjectile(
            wx=self.wx + self.facing_x * 0.4,
            wy=self.wy + self.facing_y * 0.4,
            wz=0.6,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self
        )
        projectiles.append(shuriken)

    def trigger_dog_attack(self, target_wx: float, target_wy: float):
        """Ordena o Doberman a disparar em um dash de mordida letal (1-hit kill)."""
        if not self.can_move():
            return
        if self.dog and self.dog.can_attack():
            self.set_facing(target_wx, target_wy)
            self.state = STATE_RECOVERY
            self.state_timer = 0.15
            self.dog.charge(target_wx, target_wy)

    def update(self, dt: float, game_map):
        """Atualiza o Ninja e seu Doberman."""
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.shuriken_timer > 0:
            self.shuriken_timer -= dt

        if self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        # Atualiza a IA e movimentação do Doberman
        if self.dog:
            self.dog.update(dt, game_map)

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o American Ninja no autêntico estilo Voxel 3D Isométrico."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="american",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving
        )
