"""
Entidade Doberman: cão de combate leal do American Ninja.
Possui dash de mordida letal (1-hit kill fatal), mas fica fora de combate
por 4.5 segundos se for golpeado pelo oponente durante a luta.
"""
import math
import pygame
from src.config import (
    COLOR_DOBERMAN_BLACK, COLOR_DOBERMAN_RUST, COLOR_DOBERMAN_COLLAR,
    COLOR_WHITE, COLOR_GOLD, COLOR_RED_AURA
)
from src.isometric.iso_math import world_distance
from src.entities.voxel_models import render_voxel_doberman

STATE_DOG_FOLLOW = "FOLLOW"
STATE_DOG_CHARGE = "CHARGE"
STATE_DOG_KNOCKED_OUT = "KNOCKED_OUT"

class DobermanDog:
    def __init__(self, owner):
        self.owner = owner
        self.wx = owner.wx + 0.8
        self.wy = owner.wy + 0.8
        self.wz = 0.0

        self.facing_x = 1.0
        self.facing_y = 0.0

        self.state = STATE_DOG_FOLLOW
        self.state_timer = 0.0
        self.knockout_duration = 4.5

        # Atributos de corrida
        self.follow_speed = 4.8
        self.charge_speed = 15.0
        self.charge_range = 5.2
        self.charge_dist = 0.0

        # Hitbox e Colisão
        self.radius = 0.35
        self.hitbox_active = False
        self.hitbox_radius = 0.85
        self.hitbox_center = (self.wx, self.wy)

        self.run_cycle = 0.0

    def can_attack(self) -> bool:
        """Retorna True se o cão está apto a receber o comando de ataque."""
        return self.state == STATE_DOG_FOLLOW

    def charge(self, target_wx: float, target_wy: float):
        """Inicia o dash veloz de mordida letal."""
        if not self.can_attack():
            return

        dx = target_wx - self.wx
        dy = target_wy - self.wy
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            self.facing_x = dx / dist
            self.facing_y = dy / dist

        self.state = STATE_DOG_CHARGE
        self.charge_dist = 0.0
        self.hitbox_active = True

    def knock_out(self, duration: float = 4.5):
        """Nocauteia o cão temporariamente quando golpeado pelo adversário."""
        self.state = STATE_DOG_KNOCKED_OUT
        self.state_timer = duration
        self.knockout_duration = duration
        self.hitbox_active = False

    def update(self, dt: float, game_map):
        """Atualiza a movimentação, corrida ou recuperação do Doberman."""
        self.run_cycle += dt * 14.0

        if self.state == STATE_DOG_FOLLOW:
            self.hitbox_active = False
            # Seguir suavemente o dono (a ~0.8 tiles de distância)
            dx = self.owner.wx - self.wx
            dy = self.owner.wy - self.wy
            dist = math.hypot(dx, dy)

            if dist > 0.9:
                move_speed = self.follow_speed if dist < 2.5 else self.follow_speed * 1.5
                step_x = (dx / dist) * move_speed * dt
                step_y = (dy / dist) * move_speed * dt
                self.wx += step_x
                self.wy += step_y
                self.facing_x = dx / dist
                self.facing_y = dy / dist

        elif self.state == STATE_DOG_CHARGE:
            # Dash letal
            step = self.charge_speed * dt
            self.wx += self.facing_x * step
            self.wy += self.facing_y * step
            self.charge_dist += step
            self.hitbox_active = True
            self.hitbox_center = (self.wx + self.facing_x * 0.5, self.wy + self.facing_y * 0.5)

            # Colisão com rochas ou poço durante o dash
            for r in game_map.rocks:
                if world_distance(self.wx, self.wy, r.wx, r.wy) < r.radius:
                    self.state = STATE_DOG_FOLLOW
                    self.hitbox_active = False
                    return

            if self.charge_dist >= self.charge_range:
                # Terminou o dash sem acertar: retorna a seguir o dono
                self.state = STATE_DOG_FOLLOW
                self.hitbox_active = False

        elif self.state == STATE_DOG_KNOCKED_OUT:
            self.hitbox_active = False
            self.state_timer -= dt
            if self.state_timer <= 0:
                # Cão se recupera e volta à luta!
                self.state = STATE_DOG_FOLLOW

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Doberman no autêntico estilo Voxel 3D Isométrico."""
        # Se estiver nocauteado, renderiza barra de contagem regressiva
        if self.state == STATE_DOG_KNOCKED_OUT:
            sx, sy = camera.apply(self.wx, self.wy, 0.6)
            bar_w = 32
            progress = max(0.0, self.state_timer / self.knockout_duration)
            pygame.draw.rect(surface, (40, 40, 40, 200), (sx - 16, sy - 15, bar_w, 4))
            pygame.draw.rect(surface, (255, 60, 60, 220), (sx - 16, sy - 15, int(bar_w * progress), 4))
            pygame.draw.circle(surface, COLOR_GOLD, (sx - 8, sy - 22), 2)
            pygame.draw.circle(surface, COLOR_GOLD, (sx + 8, sy - 22), 2)

        render_voxel_doberman(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, is_alive=True
        )
