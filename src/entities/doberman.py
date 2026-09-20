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
        """Renderiza o Doberman com estética pixel art e detalhes da raça."""
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

        dog_surf = pygame.Surface((60, 50), pygame.SRCALPHA)
        cx, cy = 30, 32

        # 1. Sombra no chão
        pygame.draw.ellipse(dog_surf, (10, 15, 12, 120), (cx - 14, cy - 5, 28, 10))

        if self.state == STATE_DOG_KNOCKED_OUT:
            # Pose deitado ferido
            pygame.draw.ellipse(dog_surf, COLOR_DOBERMAN_BLACK, (cx - 16, cy - 8, 32, 12))
            pygame.draw.circle(dog_surf, COLOR_DOBERMAN_RUST, (cx + 10, cy - 4), 5)
            # Barra de recuperação sobre o cão
            bar_w = 26
            progress = max(0.0, self.state_timer / self.knockout_duration)
            pygame.draw.rect(dog_surf, (40, 40, 40, 200), (cx - 13, cy - 22, bar_w, 4))
            pygame.draw.rect(dog_surf, (255, 60, 60, 220), (cx - 13, cy - 22, int(bar_w * progress), 4))
            # Estrelinhas de atordoamento
            pygame.draw.circle(dog_surf, COLOR_GOLD, (cx - 4, cy - 14), 2)
            pygame.draw.circle(dog_surf, COLOR_GOLD, (cx + 6, cy - 15), 2)

            surface.blit(dog_surf, (base_sx - 30, base_sy - 32))
            return

        # 2. Quatro Patas (Animação de corrida ou trote)
        leg_swing = math.sin(self.run_cycle) * 4.0 if (self.state == STATE_DOG_CHARGE or world_distance(self.wx, self.wy, self.owner.wx, self.owner.wy) > 0.9) else 0.0
        # Patas dianteiras e traseiras com manchas castanhas nas pontas
        pygame.draw.line(dog_surf, COLOR_DOBERMAN_BLACK, (cx - 8, cy - 8), (cx - 8 - leg_swing, cy), 3)
        pygame.draw.circle(dog_surf, COLOR_DOBERMAN_RUST, (int(cx - 8 - leg_swing), cy), 2)

        pygame.draw.line(dog_surf, COLOR_DOBERMAN_BLACK, (cx + 8, cy - 8), (cx + 8 + leg_swing, cy), 3)
        pygame.draw.circle(dog_surf, COLOR_DOBERMAN_RUST, (int(cx + 8 + leg_swing), cy), 2)

        # 3. Tronco Atlético do Doberman (Preto e Peito Castanho)
        body_rect = pygame.Rect(cx - 12, cy - 16, 24, 11)
        pygame.draw.ellipse(dog_surf, COLOR_DOBERMAN_BLACK, body_rect)
        # Mancha no peito castanha
        pygame.draw.ellipse(dog_surf, COLOR_DOBERMAN_RUST, (cx + 2, cy - 14, 8, 7))

        # 4. Rabo Curto Pontudo (típico da raça)
        tail_dir = -1 if self.facing_x >= 0 else 1
        pygame.draw.line(dog_surf, COLOR_DOBERMAN_BLACK, (cx - 10, cy - 14), (cx - 15, cy - 20), 2)

        # 5. Pescoço, Cabeça e Orelhas Pontudas em Alerta
        head_x = cx + int(self.facing_x * 12)
        head_y = cy - 18
        # Coleira Vermelha
        pygame.draw.line(dog_surf, COLOR_DOBERMAN_COLLAR, (cx + int(self.facing_x * 4), cy - 12), (head_x, head_y + 4), 3)

        # Cabeça
        pygame.draw.circle(dog_surf, COLOR_DOBERMAN_BLACK, (head_x, head_y), 6)
        # Focinho Castanho
        snout_x = head_x + int(self.facing_x * 6)
        pygame.draw.line(dog_surf, COLOR_DOBERMAN_RUST, (head_x, head_y), (snout_x, head_y + 1), 4)

        # Orelhas Pontudas em Pé (marca registrada do Doberman)
        pygame.draw.line(dog_surf, COLOR_DOBERMAN_BLACK, (head_x - 2, head_y - 4), (head_x - 2, head_y - 12), 2)
        pygame.draw.line(dog_surf, COLOR_DOBERMAN_BLACK, (head_x + 2, head_y - 4), (head_x + 2, head_y - 12), 2)

        # Se em CHARGE: Dentes brancos ferozes à mostra!
        if self.state == STATE_DOG_CHARGE:
            pygame.draw.circle(dog_surf, COLOR_WHITE, (snout_x, head_y + 1), 2)
            # Rastro de velocidade vermelho
            pygame.draw.line(dog_surf, COLOR_RED_AURA, (cx - 14, cy - 10), (cx - 24, cy - 10), 2)

        surface.blit(dog_surf, (base_sx - 30, base_sy - 32))
