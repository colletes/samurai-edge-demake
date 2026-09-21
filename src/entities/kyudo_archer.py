"""
Kyudo Archer (Arqueiro Tradicional de Hakama):
Mestre da arte milenar do arco Yumi.
Possui windup preparatório para retesar a corda e disparar flecha fatal de longo alcance.
Pode cancelar o disparo e usar a Flecha de Corda para se puxar pelo mapa em fuga rápida,
tornando a partida um jogo de gato e rato.
"""
import math
import random
import pygame
from src.config import (
    COLOR_ARCHER_HAKAMA, COLOR_ARCHER_KIMONO, COLOR_ARCHER_AURA,
    COLOR_BOW_WOOD, COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import KyudoArrowProjectile, RopeArrowProjectile
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle

STATE_BOW_DRAW = "BOW_DRAW"

class KyudoArcher(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Kyudo (Archer)")
        self.speed = 4.2

        # Mecânica de Disparo com Yumi
        self.draw_duration = 0.42     # Windup para puxar a corda do arco
        self.draw_timer = 0.0
        self.target_aim_x = 0.0
        self.target_aim_y = 0.0

        # Cooldown da Flecha de Corda
        self.rope_cooldown = 2.4
        self.rope_timer = 0.0

    def can_act(self) -> bool:
        return self.is_alive and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD)

    def trigger_bow_draw(self, target_wx: float, target_wy: float, projectiles: list = None):
        """Ataque Primário: Inicia o retesamento do arco (windup)."""
        if not self.can_act():
            return

        self.set_facing(target_wx, target_wy)
        self.target_aim_x = target_wx
        self.target_aim_y = target_wy
        self.state = STATE_BOW_DRAW
        self.draw_timer = self.draw_duration
        if projectiles is not None:
            self.projectiles_ref = projectiles

    def trigger_rope_arrow(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None):
        """
        Ação Secundária: Flecha de Corda (Rope Arrow).
        Cancela o arco imediatamente se estiver em windup e se desloca até o ponto cravado.
        """
        if not self.is_alive or self.rope_timer > 0:
            return

        # Cancela windup do arco
        self.set_facing(target_wx, target_wy)
        self.rope_timer = self.rope_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.15

        bx = self.wx + self.facing_x * 0.5
        by = self.wy + self.facing_y * 0.5
        rope = RopeArrowProjectile(bx, by, wz=0.5, dir_x=self.facing_x, dir_y=self.facing_y, owner=self)
        projectiles.append(rope)

        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(bx, by, 0.3))

    def update(self, dt: float, game_map, particles: list = None, projectiles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.rope_timer > 0:
            self.rope_timer -= dt

        proj_list = projectiles if projectiles is not None else getattr(self, "projectiles_ref", None)
        if self.state == STATE_BOW_DRAW:
            self.draw_timer -= dt
            if self.draw_timer <= 0:
                # Fim do windup: dispara a flecha mortal (1-Hit Kill)
                self.state = STATE_RECOVERY
                self.state_timer = 0.24

                if proj_list is not None:
                    bx = self.wx + self.facing_x * 0.65
                    by = self.wy + self.facing_y * 0.65
                    arrow = KyudoArrowProjectile(bx, by, wz=0.55, dir_x=self.facing_x, dir_y=self.facing_y, owner=self)
                    proj_list.append(arrow)

                if particles is not None:
                    for _ in range(8):
                        particles.append(SparkParticle(self.wx + self.facing_x * 0.6, self.wy + self.facing_y * 0.6, 0.4))

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Arqueiro Kyudo e seu arco Yumi em Voxel 3D."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="archer",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props={"is_drawing": (self.state == STATE_BOW_DRAW)}
        )

        # Indicador de retesamento do arco (mira precisa)
        if self.state == STATE_BOW_DRAW:
            bx, by = camera.apply(self.wx, self.wy, 1.35)
            progress = max(0.0, min(1.0, 1.0 - (self.draw_timer / self.draw_duration)))
            bar_w = 32
            bar_h = 5
            pygame.draw.rect(surface, (20, 30, 25), (bx - bar_w // 2 - 1, by - 1, bar_w + 2, bar_h + 2), border_radius=2)
            pygame.draw.rect(surface, (100, 220, 140), (bx - bar_w // 2, by, int(bar_w * progress), bar_h), border_radius=2)
