"""
Ninja Amarelo (Hanzo): Mestre furtivo de artes ninjas e kunai.
Possui velocidade máxima (5.4), salto acrobático parabólico evasivo com arremesso de kunai em pleno ar,
e combate corpo a corpo letal com adaga Tanto (disponível exclusivamente se estiver desarmado/sem kunai).
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
        super().__init__(wx, wy, name="Hanzo")
        self.char_type = "ninja"
        self.speed = 5.4  # Mesma velocidade máxima do Kenshi!

        # Atributos de Kunai
        self.has_kunai = True
        self.thrust_duration = 0.14
        self.recovery_duration = 0.15
        self.thrust_step = 0.0

        # Salto Parabólico Evasivo
        self.jump_duration = 0.48
        self.jump_max_height = 1.35
        self.jump_speed = 6.4
        self.jump_dir = (1.0, 0.0)
        self.has_thrown_in_jump = False
        self.auto_throw_in_jump = False
        self._throw_target = (0.0, 0.0)
        self._throw_projectiles = None

    def trigger_jump(self, target_wx: float, target_wy: float, projectiles: list | None = None):
        """
        Ação Secundária (Dash/Especial): Pulo Parabólico Evasivo.
        Hanzo salta alto no ar, desviando de ataques no solo.
        Durante o salto, se possuir a Kunai, pode arremessá-la.
        """
        if not self.can_move():
            return

        self.set_facing(target_wx, target_wy)
        self.state = "JUMP"
        self.state_timer = self.jump_duration
        self.jump_dir = (self.facing_x, self.facing_y)
        self.has_thrown_in_jump = False
        self.auto_throw_in_jump = False
        self.hitbox_active = False

    def trigger_jump_and_throw(self, target_wx: float, target_wy: float, projectiles: list):
        """Inicia o salto parabólico e arremessa a kunai em pleno ar."""
        if not self.can_move() or not self.has_kunai:
            return
        self.trigger_jump(target_wx, target_wy)
        self.has_kunai = False
        self.has_thrown_in_jump = True

        kunai = KunaiProjectile(
            wx=self.wx + self.facing_x * 0.35,
            wy=self.wy + self.facing_y * 0.35,
            wz=0.65,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self
        )
        projectiles.append(kunai)

    def trigger_midair_throw(self, target_wx: float, target_wy: float, projectiles: list):
        """Arremessa a kunai de cima para baixo em pleno ar."""
        if self.state != "JUMP" or not self.has_kunai or self.has_thrown_in_jump:
            return

        self.set_facing(target_wx, target_wy)
        self.has_kunai = False
        self.has_thrown_in_jump = True

        kunai = KunaiProjectile(
            wx=self.wx + self.facing_x * 0.35,
            wy=self.wy + self.facing_y * 0.35,
            wz=max(0.4, self.wz),
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self
        )
        projectiles.append(kunai)

    def trigger_thrust_attack(self, target_wx: float, target_wy: float):
        """
        Ataque Melee: Estocada com a adaga Tanto.
        Regra: Fica disponível EXCLUSIVAMENTE se Hanzo NÃO tiver mais a Kunai!
        """
        if self.has_kunai:
            # Tanto indisponível enquanto tiver a kunai!
            return

        if not self.can_move():
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = self.thrust_duration
        self.hitbox_active = True
        self.hitbox_radius = 1.05
        self.slash_dir = (self.facing_x, self.facing_y)
        self.hitbox_center = (self.wx + self.facing_x * 0.85, self.wy + self.facing_y * 0.85)

    def trigger_throw_attack(self, target_wx: float, target_wy: float, projectiles: list):
        """Atalho de compatibilidade para arremesso com salto."""
        if self.has_kunai:
            if self.state == "JUMP":
                self.trigger_midair_throw(target_wx, target_wy, projectiles)
            else:
                self.trigger_jump_and_throw(target_wx, target_wy, projectiles)

    def update(self, dt: float, game_map):
        """Atualiza a lógica e física do Ninja Amarelo."""
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.state == "JUMP":
            self.state_timer -= dt
            progress = max(0.0, min(1.0, 1.0 - (self.state_timer / self.jump_duration)))
            self.wz = math.sin(progress * math.pi) * self.jump_max_height

            # Arremesso automático na subida/ápice do salto se solicitado
            if self.auto_throw_in_jump and not self.has_thrown_in_jump and self.has_kunai and progress >= 0.28:
                if self._throw_projectiles is not None:
                    self.trigger_midair_throw(self._throw_target[0], self._throw_target[1], self._throw_projectiles)

            # Deslocamento no ar
            new_wx = self.wx + self.jump_dir[0] * self.jump_speed * dt
            new_wy = self.wy + self.jump_dir[1] * self.jump_speed * dt

            # Colisão apenas rente ao chão
            hit_obstacle = False
            if self.wz < 0.4:
                for r in game_map.rocks:
                    c, _, _ = r.check_collision(new_wx, new_wy, self.radius)
                    if c:
                        hit_obstacle = True
                        break
                if game_map.well:
                    c, _, _ = game_map.well.check_collision(new_wx, new_wy, self.radius)
                    if c:
                        hit_obstacle = True

            if not hit_obstacle:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            if self.state_timer <= 0:
                self.wz = 0.0
                self.state = STATE_IDLE
                self.has_thrown_in_jump = False
                self.auto_throw_in_jump = False

        elif self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Impulso na estocada da Tanto
            thrust_speed = 4.2
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

        # Indicador se está desarmado (sem kunai)
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
