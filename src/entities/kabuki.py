"""
Kabuki (Dançarino do Sopro Venenoso):
Cospe uma nuvem de veneno concentrada. Ao acertar, o oponente ganha um boost
de velocidade e cooldowns zerados, mas entra em contagem regressiva fatal de 10s.
O Kabuki não pode mais atacar e deve usar piruetas e esquivas acrobáticas para sobreviver!
"""
import math
import random
import pygame
from src.config import (
    COLOR_KABUKI_WHITE, COLOR_KABUKI_RED, COLOR_KABUKI_HAIR, COLOR_KABUKI_AURA,
    COLOR_POISON_GREEN, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import PoisonCloudProjectile
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle

STATE_KABUKI_ROLL = "KABUKI_ROLL"

class Kabuki(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Kabuki (Poison Dancer)")
        self.speed = 4.4

        # Mecânica do Veneno e Sobrevivência
        self.has_poisoned_target = False  # Ativa após o veneno acertar o rival
        self.poison_timer = 10.0          # Contagem regressiva fatal de 10s
        self.target_rival = None

        # Esquiva Acrobática / Pirueta (Kabuki Roll)
        self.dodge_cooldown = 0.65
        self.dodge_timer = 0.0
        self.roll_speed = 10.5
        self.roll_duration = 0.26
        self.roll_dir_x = 1.0
        self.roll_dir_y = 0.0

    def can_act(self) -> bool:
        if not self.is_alive or self.state in (STATE_KABUKI_ROLL, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD):
            return False
        # Se já envenenou o alvo, NÃO pode atacar, apenas esquivar!
        return True

    def trigger_poison_spit(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None):
        """Ataque Primário: Sopro de nuvem ácida venenosa. Bloqueado após acertar o veneno."""
        if not self.can_act() or self.has_poisoned_target:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_RECOVERY
        self.state_timer = 0.22

        # Lançar nuvem de veneno
        bx = self.wx + self.facing_x * 0.4
        by = self.wy + self.facing_y * 0.4
        cloud = PoisonCloudProjectile(bx, by, wz=0.5, dir_x=self.facing_x, dir_y=self.facing_y, owner=self)
        projectiles.append(cloud)

        if particles is not None:
            for _ in range(10):
                particles.append(SparkParticle(bx, by, 0.45))

    def trigger_acrobatic_dodge(self, dir_x: float, dir_y: float, particles: list = None):
        """Ação Secundária (e Primária pós-veneno): Pirueta acrobática evasiva."""
        if not self.is_alive or self.dodge_timer > 0 or self.state == STATE_KABUKI_ROLL:
            return

        if dir_x == 0 and dir_y == 0:
            dir_x, dir_y = -self.facing_x, -self.facing_y
        else:
            mag = math.hypot(dir_x, dir_y)
            if mag > 0.001:
                dir_x /= mag
                dir_y /= mag

        self.dodge_timer = self.dodge_cooldown
        self.state = STATE_KABUKI_ROLL
        self.state_timer = self.roll_duration
        self.roll_dir_x = dir_x
        self.roll_dir_y = dir_y
        self.facing_x = dir_x
        self.facing_y = dir_y

        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(self.wx, self.wy, 0.3))

    def on_poison_inflicted(self, rival):
        """Chamado pelo sistema de colisão quando o veneno atinge o oponente."""
        self.has_poisoned_target = True
        self.poison_timer = 10.0
        self.target_rival = rival

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.dodge_timer > 0:
            self.dodge_timer -= dt

        # Atualização do cronômetro de morte do oponente
        if self.has_poisoned_target and self.target_rival and self.target_rival.is_alive:
            self.poison_timer -= dt

        if self.state == STATE_KABUKI_ROLL:
            self.state_timer -= dt
            step = self.roll_speed * dt
            new_wx = self.wx + self.roll_dir_x * step
            new_wy = self.wy + self.roll_dir_y * step

            hit_col = False
            for r in game_map.rocks:
                if r.check_collision(new_wx, new_wy, self.radius)[0]:
                    hit_col = True; break
            if game_map.well and game_map.well.check_collision(new_wx, new_wy, self.radius)[0]:
                hit_col = True

            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            if particles is not None and random.random() < 0.3:
                particles.append(SparkParticle(self.wx, self.wy, 0.2))

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
        """Renderiza o Kabuki e o cronômetro dramático de veneno."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="kabuki",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props={"has_poisoned": self.has_poisoned_target}
        )

        # Se o oponente estiver envenenado, exibir aviso de contagem no Kabuki
        if self.has_poisoned_target and self.poison_timer > 0:
            kx, ky = camera.apply(self.wx, self.wy, 1.45)
            font_small = pygame.font.Font(None, 20)
            txt = font_small.render(f"SOBREVIVA: {self.poison_timer:.1f}s", True, COLOR_POISON_GREEN)
            surface.blit(txt, (kx - txt.get_width() // 2, ky))
