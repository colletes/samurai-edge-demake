"""
Rifleman (Tanegashima): Mestre atirador armado com arcabuz feudal de mecha.
Tiro fatal de longo alcance (1-Hit Kill). Requer dosar a pólvora e socar a munição
segurando a ação secundária, com salto evasivo de fumaça para reposicionamento.
"""
import math
import random
import pygame
from src.config import (
    COLOR_RIFLE_COAT, COLOR_RIFLE_HAT, COLOR_RIFLE_AURA, COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import MusketBulletProjectile
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle

STATE_BACKSTEP = "BACKSTEP"

class Rifleman(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Tanegashima (Rifleman)")
        self.speed = 3.9

        # Mecânica de Munição e Pólvora
        self.has_ammo = True          # Inicia com 1 tiro pronto
        self.is_reloading = False
        self.reload_progress = 0.0
        self.reload_time = 1.75        # Tempo segurando secundário para carregar

        # Subterfúgio Evasivo durante recarga
        self.backstep_cooldown = 1.6
        self.backstep_timer = 0.0
        self.backstep_duration = 0.20

    def can_act(self) -> bool:
        return self.is_alive and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD)

    def trigger_shoot(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None):
        """Ataque Primário: Disparo fatal supersônico de arcabuz (1-Hit Kill)."""
        if not self.can_act() or not self.has_ammo:
            return

        self.set_facing(target_wx, target_wy)
        self.has_ammo = False
        self.is_reloading = False
        self.reload_progress = 0.0

        self.state = STATE_RECOVERY
        self.state_timer = 0.38

        # Recuo da pólvora
        self.wx -= self.facing_x * 0.4
        self.wy -= self.facing_y * 0.4

        # Criar projétil
        bx = self.wx + self.facing_x * 0.65
        by = self.wy + self.facing_y * 0.65
        bullet = MusketBulletProjectile(bx, by, wz=0.55, dir_x=self.facing_x, dir_y=self.facing_y, owner=self)
        projectiles.append(bullet)

        if particles is not None:
            for _ in range(14):
                particles.append(SparkParticle(bx, by, 0.55))

    def trigger_reload_hold(self):
        """Ativado enquanto o jogador mantém pressionado o botão de ação secundária."""
        if not self.can_act() or self.has_ammo:
            return
        self.is_reloading = True

    def trigger_evasive_backstep(self, particles: list = None):
        """Subterfúgio: Salto tático para trás com fumaça sem cancelar a recarga."""
        if not self.is_alive or self.backstep_timer > 0:
            return

        self.backstep_timer = self.backstep_cooldown
        self.state = STATE_BACKSTEP
        self.state_timer = self.backstep_duration

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.3))

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.backstep_timer > 0:
            self.backstep_timer -= dt

        # Progresso de recarga se estiver segurando o botão
        if self.is_reloading and not self.has_ammo:
            self.reload_progress += dt / self.reload_time
            if particles is not None and random.random() < 0.25:
                particles.append(SparkParticle(self.wx, self.wy, 0.4))

            if self.reload_progress >= 1.0:
                self.has_ammo = True
                self.is_reloading = False
                self.reload_progress = 0.0
                if particles is not None:
                    for _ in range(8):
                        particles.append(SparkParticle(self.wx, self.wy, 0.7))

        if self.state == STATE_BACKSTEP:
            self.state_timer -= dt
            # Recuo evasivo na direção oposta ao olhar
            step = 7.5 * dt
            new_wx = self.wx - self.facing_x * step
            new_wy = self.wy - self.facing_y * step

            hit_col = False
            for r in game_map.rocks:
                if r.check_collision(new_wx, new_wy, self.radius)[0]:
                    hit_col = True; break
            if game_map.well and game_map.well.check_collision(new_wx, new_wy, self.radius)[0]:
                hit_col = True

            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

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
        """Renderiza o Rifleman e sua barra de recarga."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="rifleman",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props={"has_ammo": self.has_ammo, "is_reloading": self.is_reloading}
        )

        # Barra visual de preparo de pólvora / recarga
        if self.is_reloading and not self.has_ammo:
            bx, by = camera.apply(self.wx, self.wy, 1.35)
            bar_w = 40
            bar_h = 6
            pygame.draw.rect(surface, (20, 20, 25), (bx - bar_w // 2 - 1, by - 1, bar_w + 2, bar_h + 2), border_radius=3)
            fill_w = int(bar_w * max(0.0, min(1.0, self.reload_progress)))
            pygame.draw.rect(surface, (230, 160, 40), (bx - bar_w // 2, by, fill_w, bar_h), border_radius=2)
            pygame.draw.rect(surface, COLOR_GOLD, (bx - bar_w // 2 - 1, by - 1, bar_w + 2, bar_h + 2), 1, border_radius=3)
