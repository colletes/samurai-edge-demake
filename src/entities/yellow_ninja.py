"""
Ninja Amarelo (Hanzo): Mestre furtivo de artes ninjas e kunai.
Possui velocidade máxima (igual ao Kenshin), estocada rápida corpo a corpo (requer 2 acertos)
e arremesso de kunai mortal à distância (1-hit kill, mas requer pegar a kunai do solo).
"""
import math
import pygame
from src.config import (
    COLOR_YELLOW_NINJA, COLOR_YELLOW_DARK, COLOR_NINJA_MASK,
    COLOR_YELLOW_AURA, COLOR_STEEL, COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import KunaiProjectile
from src.entities.voxel_models import render_voxel_humanoid

class YellowNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Hanzo (Ninja)")
        self.speed = 5.4  # Mesma velocidade máxima do Kenshin!

        # Atributos de Kunai
        self.has_kunai = True
        self.thrust_duration = 0.14
        self.recovery_duration = 0.15
        self.thrust_step = 0.0

    def trigger_thrust_attack(self, target_wx: float, target_wy: float):
        """Ataque Melee Padrão: Estocada rápida com a kunai (causa 1 de dano)."""
        if not self.can_move() or not self.has_kunai:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = self.thrust_duration
        self.hitbox_active = True
        self.hitbox_radius = 1.05
        self.slash_dir = (self.facing_x, self.facing_y)
        self.hitbox_center = (self.wx + self.facing_x * 0.85, self.wy + self.facing_y * 0.85)

    def trigger_throw_attack(self, target_wx: float, target_wy: float, projectiles: list):
        """Ataque Ranged: Arremessa a kunai em linha reta (1-hit kill mortal)."""
        if not self.can_move() or not self.has_kunai:
            return

        self.set_facing(target_wx, target_wy)
        self.has_kunai = False
        self.state = STATE_RECOVERY
        self.state_timer = 0.18

        # Cria a kunai em vôo
        kunai = KunaiProjectile(
            wx=self.wx + self.facing_x * 0.4,
            wy=self.wy + self.facing_y * 0.4,
            wz=0.6,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self
        )
        projectiles.append(kunai)

    def update(self, dt: float, game_map):
        """Atualiza a lógica do Ninja Amarelo."""
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Pequeno impulso na estocada
            thrust_speed = 4.0
            new_wx = self.wx + self.facing_x * thrust_speed * dt
            new_wy = self.wy + self.facing_y * thrust_speed * dt

            # Colisão com rochas/poço
            hit_obstacle = False
            for r in game_map.rocks:
                c, _, _ = r.check_collision(new_wx, new_wy, self.radius)
                if c:
                    hit_obstacle = True
                    break
            if game_map.well:
                c, _, _ = game_map.well.check_collision(new_wx, new_wy, self.radius)
                if c:
                    hit_obstacle = True

            if hit_obstacle:
                self.stun(0.6)
                return

            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            self.hitbox_center = (self.wx + self.facing_x * 0.85, self.wy + self.facing_y * 0.85)

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
                self.hitbox_active = False

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Ninja Amarelo no autêntico estilo Voxel 3D Isométrico."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        # Barra de Vida (se tomou dano mas ainda está vivo)
        if self.hp < self.max_hp and self.is_alive:
            sx, sy = camera.apply(self.wx, self.wy, 1.35)
            pygame.draw.rect(surface, (40, 40, 40, 200), (sx - 10, sy, 20, 4))
            pygame.draw.rect(surface, (255, 50, 50, 220), (sx - 10, sy, 10, 4))

        # Indicador se está desarmado
        if not self.has_kunai and self.is_alive:
            sx, sy = camera.apply(self.wx, self.wy, 1.5)
            pygame.draw.circle(surface, (255, 80, 80), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="ninja",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props={"has_kunai": self.has_kunai}
        )
