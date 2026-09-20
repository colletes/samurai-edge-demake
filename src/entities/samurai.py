"""
Classe base Samurai com física isométrica, máquina de estados,
colisões, mecânica de stealth e renderização procedural em pixel art.
"""
import math
import pygame
from src.config import (
    COLOR_WHITE, COLOR_BLACK, COLOR_STEEL, COLOR_GOLD
)

# Estados da Máquina de Estados Finita (FSM)
STATE_IDLE = "IDLE"
STATE_WALK = "WALK"
STATE_DASH = "DASH"
STATE_WINDUP = "WINDUP"
STATE_ATTACK = "ATTACK"
STATE_RECOVERY = "RECOVERY"
STATE_PARRY = "PARRY"
STATE_STUNNED = "STUNNED"
STATE_DEAD = "DEAD"

class Samurai:
    def __init__(self, wx: float, wy: float, name: str):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.name = name

        # Direção para onde está olhando (vetor no mundo)
        self.facing_x = 1.0
        self.facing_y = 0.0

        # Atributos de Movimentação
        self.speed = 3.8
        self.radius = 0.35 # Raio de colisão física

        # Estado atual e cronômetros
        self.state = STATE_IDLE
        self.state_timer = 0.0

        # Camuflagem / Furtividade
        self.is_hidden = False
        self.alpha = 255

        # Animação
        self.walk_cycle = 0.0
        self.is_moving = False

        # Combate e Vida
        self.max_hp = 2
        self.hp = 2
        self.is_alive = True
        self.hitbox_active = False
        self.hitbox_radius = 0.0
        self.hitbox_center: tuple[float, float] = (0.0, 0.0)
        self.slash_dir: tuple[float, float] = (0.0, 0.0)
        self.slow_timer = 0.0

    def apply_slow(self, duration: float = 2.5):
        """Aplica desaceleração de 65% na velocidade de movimentação."""
        self.slow_timer = max(self.slow_timer, duration)

    def set_facing(self, target_wx: float, target_wy: float):
        """Vira o samurai para encarar o alvo."""
        dx = target_wx - self.wx
        dy = target_wy - self.wy
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            self.facing_x = dx / dist
            self.facing_y = dy / dist

    def can_move(self) -> bool:
        """Determina se o guerreiro pode andar no estado atual."""
        return self.state in (STATE_IDLE, STATE_WALK)

    def take_hit(self, slash_dir: tuple[float, float], damage: int = 2) -> tuple[bool, bool]:
        """
        Aplica dano ao guerreiro.
        Retorna (acertou, causou_morte).
        """
        if not self.is_alive:
            return False, False

        # Se estiver em postura de parry e de frente para o ataque
        if self.state == STATE_PARRY:
            dot = self.facing_x * slash_dir[0] + self.facing_y * slash_dir[1]
            if dot < -0.2: # O ataque veio de frente!
                return False, False # Defendido com sucesso!

        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            self.state = STATE_DEAD
            self.state_timer = 0.0
            return True, True
        else:
            # Dano parcial (ex: 1 golpe de kunai)
            self.stun(0.35)
            return True, False

    def stun(self, duration: float = 0.8):
        """Atordoa o guerreiro temporariamente (ex: ao bater na rocha ou sofrer parry)."""
        if self.is_alive:
            self.state = STATE_STUNNED
            self.state_timer = duration
            self.hitbox_active = False

    def apply_movement(self, move_x: float, move_y: float, dt: float, game_map):
        """Aplica a movimentação com detecção de obstáculos e desaceleração na água."""
        if not self.can_move():
            return

        self.is_moving = (move_x != 0 or move_y != 0)
        if not self.is_moving:
            if self.state == STATE_WALK:
                self.state = STATE_IDLE
            return

        self.state = STATE_WALK
        self.walk_cycle += dt * 10.0

        # Velocidade base reduzida se estiver pisando em água ou sob efeito de fumaça (slow)
        current_speed = self.speed
        if self.slow_timer > 0:
            current_speed *= 0.35
            self.slow_timer -= dt

        if game_map.is_water(self.wx, self.wy):
            current_speed *= 0.55

        # Nova posição proposta
        new_wx = self.wx + move_x * current_speed * dt
        new_wy = self.wy + move_y * current_speed * dt

        # Vira na direção do movimento
        self.facing_x = move_x
        self.facing_y = move_y

        # Colisão com limites do mapa
        new_wx = max(1.0, min(game_map.cols - 1.0, new_wx))
        new_wy = max(1.0, min(game_map.rows - 1.0, new_wy))

        # Colisão com rochas
        for rock in game_map.rocks:
            collided, push_x, push_y = rock.check_collision(new_wx, new_wy, self.radius)
            if collided:
                new_wx += push_x
                new_wy += push_y

        # Colisão com o poço
        if game_map.well:
            collided, push_x, push_y = game_map.well.check_collision(new_wx, new_wy, self.radius)
            if collided:
                new_wx += push_x
                new_wy += push_y

        # Colisão com árvores
        for tree in game_map.trees:
            collided, push_x, push_y = tree.check_collision(new_wx, new_wy, self.radius)
            if collided:
                new_wx += push_x
                new_wy += push_y

        self.wx = new_wx
        self.wy = new_wy

    def update_stealth(self, game_map):
        """Atualiza estado de camuflagem na vegetação de bambu."""
        self.is_hidden = game_map.is_hidden_in_bamboo(self.wx, self.wy)
        target_alpha = 110 if self.is_hidden else 255
        self.alpha += int((target_alpha - self.alpha) * 0.15)
