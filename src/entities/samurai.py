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
STATE_ROLL = "ROLL"
STATE_WINDUP = "WINDUP"
STATE_ATTACK = "ATTACK"
STATE_RECOVERY = "RECOVERY"
STATE_PARRY = "PARRY"
STATE_STUNNED = "STUNNED"
STATE_DEAD = "DEAD"


def resolve_playable_bounds(game_map) -> tuple[float, float, float, float]:
    """Retorna (min_x, min_y, max_x, max_y) jogável do mapa atual, respeitando
    game_map.playable_bounds quando definido (ex: faixa real da rua em Kyoto),
    ou o grid cheio como fallback para mapas sem essa restrição."""
    bounds = getattr(game_map, "playable_bounds", None)
    if bounds is not None:
        return bounds
    return 1.0, 1.0, game_map.cols - 1.0, game_map.rows - 1.0


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
        self.is_invulnerable_dodge = False
        self.is_agile_dodge = False  # False = Padrão/Pesada, True = Especial/Ágil
        self.roll_speed = 8.5        # Padrão pesada: 8.5 (ágil: 10.5)
        self.roll_duration = 0.20    # Padrão pesada: 0.20s (~1.7 tiles), ágil: 0.22s (~2.3 tiles)
        self.roll_recovery_duration = 0.18  # Pós-esquiva imóvel e vulnerável (pesada: 0.18s, ágil: 0.12s)
        self.roll_recovery_timer = 0.0
        self.roll_cooldown_duration = 0.38  # Cooldown total de re-esquiva (pesada: 0.38s, ágil: 0.35s)
        self.roll_cooldown_timer = 0.0
        self.dash_recovery_timer = 0.0

    @property
    def dash_recovery_duration(self) -> float:
        return self.roll_recovery_duration

    @dash_recovery_duration.setter
    def dash_recovery_duration(self, val: float):
        self.roll_recovery_duration = val

    def apply_slow(self, duration: float = 2.5, banners: list = None):
        """Aplica desaceleração de 65% na velocidade de movimentação."""
        if getattr(self, "is_poisoned", False):
            return  # Veneno agora concede adrenalina/frenzy e anula efeitos de lentidão
        was_slow = self.slow_timer > 0
        self.slow_timer = max(self.slow_timer, duration)
        if not was_slow and banners is not None:
            from src.effects.particles import FloatingBanner
            banners.append(FloatingBanner("SLOW!", self.wx, self.wy, wz=1.7, color=(190, 180, 170), duration=1.2))

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
        if self.roll_recovery_timer > 0:
            return False
        return self.state in (STATE_IDLE, STATE_WALK)

    def can_act(self) -> bool:
        """Determina se o guerreiro pode desferir ataques ou técnicas."""
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def update_dodge_timers(self, dt: float):
        """Atualiza cronômetros universais de recuperação pós-esquiva e cooldown de re-esquiva."""
        if self.roll_recovery_timer > 0:
            self.roll_recovery_timer = max(0.0, self.roll_recovery_timer - dt)
        if self.roll_cooldown_timer > 0:
            self.roll_cooldown_timer = max(0.0, self.roll_cooldown_timer - dt)
        if self.dash_recovery_timer > 0:
            self.dash_recovery_timer = max(0.0, self.dash_recovery_timer - dt)

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None):
        """Terceira Ação Universal: Rolamento / Esquiva com frames de invulnerabilidade (i-frames)."""
        if (
            not self.is_alive
            or self.state in (STATE_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK, STATE_RECOVERY)
            or self.roll_recovery_timer > 0
            or self.roll_cooldown_timer > 0
            or self.dash_recovery_timer > 0
        ):
            return

        if dir_x == 0 and dir_y == 0:
            dir_x, dir_y = -self.facing_x, -self.facing_y
        else:
            mag = math.hypot(dir_x, dir_y)
            if mag > 0.001:
                dir_x /= mag
                dir_y /= mag

        self.state = STATE_ROLL
        self.state_timer = self.roll_duration
        self.facing_x = dir_x
        self.facing_y = dir_y
        self.is_invulnerable_dodge = True
        self.hitbox_active = False

        if particles is not None:
            from src.effects.particles import SparkParticle
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.35))

    def update_roll(self, dt: float, game_map, particles: list = None):
        """Atualiza a translação física e cronômetro do rolamento/esquiva."""
        if self.state != STATE_ROLL:
            return
        self.state_timer -= dt
        step = self.roll_speed * dt
        new_wx = self.wx + self.facing_x * step
        new_wy = self.wy + self.facing_y * step

        min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
        new_wx = max(min_x, min(max_x, new_wx))
        new_wy = max(min_y, min(max_y, new_wy))

        # Testar colisão com rochas
        for rock in game_map.rocks:
            c, px, py = rock.check_collision(new_wx, new_wy, self.radius)
            if c:
                new_wx += px; new_wy += py

        # Testar colisão com fachadas de edifícios (ex: machiyas de Kyoto)
        for building in getattr(game_map, "buildings", []):
            c, px, py = building.check_collision(new_wx, new_wy, self.radius)
            if c:
                new_wx += px; new_wy += py

        self.wx, self.wy = new_wx, new_wy

        if self.state_timer <= 0:
            self.state = STATE_IDLE
            self.is_invulnerable_dodge = False
            self.roll_recovery_timer = self.roll_recovery_duration
            self.roll_cooldown_timer = self.roll_cooldown_duration
            self.dash_recovery_timer = self.roll_recovery_duration

    def take_hit(self, slash_dir: tuple[float, float], damage: int = 2) -> tuple[bool, bool]:
        """
        Aplica dano ao guerreiro.
        Retorna (acertou, causou_morte).
        """
        if not self.is_alive:
            return False, False

        # Se estiver em esquiva / roll com i-frames ativos
        if self.state in (STATE_ROLL, STATE_DASH, "SHUKUCHI", "KAWARIMI_ROLL", "DODGE") and (self.is_invulnerable_dodge or getattr(self, "is_invulnerable_dodge", False)):
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
            self.is_invulnerable_dodge = False

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

        # Velocidade base: veneno confere adrenalina (+25% velocidade); slow ou água reduzem
        current_speed = self.speed
        if getattr(self, "is_poisoned", False):
            current_speed *= 1.25
        elif self.slow_timer > 0:
            current_speed *= 0.35

        if game_map.is_water(self.wx, self.wy):
            current_speed *= 0.55

        # Nova posição proposta
        new_wx = self.wx + move_x * current_speed * dt
        new_wy = self.wy + move_y * current_speed * dt

        # Vira na direção do movimento
        self.facing_x = move_x
        self.facing_y = move_y

        # Colisão com limites do mapa
        min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
        new_wx = max(min_x, min(max_x, new_wx))
        new_wy = max(min_y, min(max_y, new_wy))

        # Colisão com rochas
        for rock in game_map.rocks:
            collided, push_x, push_y = rock.check_collision(new_wx, new_wy, self.radius)
            if collided:
                new_wx += push_x
                new_wy += push_y

        # Colisão com fachadas de edifícios (ex: machiyas de Kyoto)
        for building in getattr(game_map, "buildings", []):
            collided, push_x, push_y = building.check_collision(new_wx, new_wy, self.radius)
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
