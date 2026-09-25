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
        super().__init__(wx, wy, name="Tomoe")
        self.char_type = "tomoe"
        self.speed = 4.2

        # Mecânica de Disparo com Yumi (Mira Manual - Sem Windup)
        self.draw_duration = 0.0
        self.draw_timer = 0.0
        self.target_aim_x = 0.0
        self.target_aim_y = 0.0

        # Mecânica de Flecha com Corda (Hold & Release)
        self.is_charging_rope = False
        self.rope_charge_time = 0.0
        self.rope_charge_duration = 0.45  # 0.45s para atingir alcance máximo
        self.rope_min_range = 3.0
        self.rope_max_range = 10.5
        self.target_rope_x = self.wx
        self.target_rope_y = self.wy
        self.rope_cooldown = 0.0
        self.rope_timer = 0.0

    def can_act(self) -> bool:
        return self.is_alive and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD)

    def can_move(self) -> bool:
        if self.is_charging_rope:
            return self.is_alive
        return super().can_move()

    def apply_movement(self, move_x: float, move_y: float, dt: float, game_map):
        if self.is_charging_rope:
            orig_speed = self.speed
            self.speed = orig_speed * 0.45  # Movimentação tática cuidadosa enquanto mira a corda
            super().apply_movement(move_x, move_y, dt, game_map)
            self.speed = orig_speed
        else:
            super().apply_movement(move_x, move_y, dt, game_map)

    def trigger_bow_draw(self, target_wx: float, target_wy: float, projectiles: list = None, particles: list = None):
        """Ataque Primário: Disparo imediato da flecha Yumi sem windup (mira manual)."""
        if not self.can_act():
            return

        self.set_facing(target_wx, target_wy)
        self.target_aim_x = target_wx
        self.target_aim_y = target_wy
        self.state = STATE_RECOVERY
        self.state_timer = 0.20

        proj_list = projectiles if projectiles is not None else getattr(self, "projectiles_ref", None)
        if proj_list is not None:
            bx = self.wx + self.facing_x * 0.65
            by = self.wy + self.facing_y * 0.65
            arrow = KyudoArrowProjectile(bx, by, wz=0.55, dir_x=self.facing_x, dir_y=self.facing_y, owner=self)
            proj_list.append(arrow)

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx + self.facing_x * 0.6, self.wy + self.facing_y * 0.6, 0.4))

    def start_rope_arrow_charge(self, target_wx: float, target_wy: float, game_map=None):
        """Inicia o tensionamento da corda (Hold)."""
        if not self.can_act():
            return
        self.is_charging_rope = True
        self.rope_charge_time = 0.0
        self.set_facing(target_wx, target_wy)
        self._calculate_rope_target(game_map)

    def update_rope_charge(self, dt: float, target_wx: float, target_wy: float, game_map=None):
        """Atualiza a mira e alcance contínuo enquanto o botão é mantido pressionado."""
        if not self.is_alive or not self.is_charging_rope:
            self.is_charging_rope = False
            return
        if self.state in (STATE_STUNNED, STATE_DEAD):
            self.is_charging_rope = False
            return
        self.rope_charge_time += dt
        self.set_facing(target_wx, target_wy)
        self._calculate_rope_target(game_map)

    def _calculate_rope_target(self, game_map=None):
        """Calcula o ponto exato de impacto respeitando os limites da arena e obstáculos."""
        charge_ratio = min(1.0, self.rope_charge_time / self.rope_charge_duration)
        cur_range = self.rope_min_range + (self.rope_max_range - self.rope_min_range) * charge_ratio

        min_x = 1.0
        max_x = (game_map.cols - 1.0) if game_map else 20.0
        min_y = 1.0
        max_y = (game_map.rows - 1.0) if game_map else 20.0

        step_sz = 0.25
        steps = max(1, int(cur_range / step_sz))
        cx, cy = self.wx, self.wy

        for i in range(1, steps + 1):
            nx = self.wx + self.facing_x * (i * step_sz)
            ny = self.wy + self.facing_y * (i * step_sz)

            # Limite estrito do mapa: para exatamente na borda
            if nx <= min_x or nx >= max_x or ny <= min_y or ny >= max_y:
                cx = max(min_x, min(max_x, nx))
                cy = max(min_y, min(max_y, ny))
                break

            # Trava em obstáculos sólidos da arena
            hit = False
            if game_map:
                for r in game_map.rocks:
                    if math.hypot(nx - r.wx, ny - r.wy) < (r.radius + 0.2):
                        hit = True; break
                if not hit and game_map.well and math.hypot(nx - game_map.well.wx, ny - game_map.well.wy) < (game_map.well.radius + 0.2):
                    hit = True
                if not hit:
                    for b in game_map.bamboos:
                        if not b.is_cut and math.hypot(nx - b.wx, ny - b.wy) < 0.5:
                            hit = True; break
            if hit:
                cx, cy = nx, ny
                break
            cx, cy = nx, ny

        self.target_rope_x = max(min_x, min(max_x, cx))
        self.target_rope_y = max(min_y, min(max_y, cy))

    def release_rope_arrow(self, projectiles: list, particles: list = None, game_map=None):
        """Ao soltar o botão, crava a flecha na posição mirada e puxa Tomoe para lá."""
        if not self.is_alive or not self.is_charging_rope:
            self.is_charging_rope = False
            return
        self.is_charging_rope = False

        min_x = 1.0
        max_x = (game_map.cols - 1.0) if game_map else 20.0
        min_y = 1.0
        max_y = (game_map.rows - 1.0) if game_map else 20.0

        tx = max(min_x, min(max_x, self.target_rope_x))
        ty = max(min_y, min(max_y, self.target_rope_y))

        rope = RopeArrowProjectile(tx, ty, wz=0.25, dir_x=self.facing_x, dir_y=self.facing_y, owner=self, start_latched=True)
        projectiles.append(rope)

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(tx, ty, 0.35))
            for _ in range(4):
                particles.append(SparkParticle(self.wx, self.wy, 0.25))

        self.state = STATE_RECOVERY
        self.state_timer = 0.08

    def trigger_rope_arrow(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None, game_map=None):
        """
        Ação Secundária: Flecha de Corda direta (compatibilidade com IA e testes).
        """
        if not self.is_alive:
            return

        self.set_facing(target_wx, target_wy)
        self.rope_timer = 0.0
        self.is_charging_rope = True
        self.rope_charge_time = self.rope_charge_duration
        self._calculate_rope_target(game_map)
        self.release_rope_arrow(projectiles, particles, game_map)

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
            self.is_charging_rope = False
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Arqueiro Kyudo e seu arco Yumi em Voxel 3D."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        # 1. Guia Visual Tática de Mira (Hold & Release)
        if self.is_charging_rope and self.is_alive:
            ox, oy = self.wx, self.wy
            tx, ty = self.target_rope_x, self.target_rope_y
            sx_from, sy_from = camera.apply(ox, oy, 0.4)
            sx_to, sy_to = camera.apply(tx, ty, 0.1)

            # Linha pontilhada de corda de cânhamo
            dist_pts = max(4, int(math.hypot(sx_to - sx_from, sy_to - sy_from) / 10))
            for i in range(dist_pts):
                t = i / float(dist_pts)
                px = int(sx_from + (sx_to - sx_from) * t)
                py = int(sy_from + (sy_to - sy_from) * t)
                if i % 2 == 0:
                    pygame.draw.circle(surface, (225, 205, 140), (px, py), 2)

            # Retículo de impacto na posição exata onde a flecha cravará
            pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.012)
            tgt_radius = int(8 + pulse * 3)
            pygame.draw.circle(surface, (235, 195, 50), (int(sx_to), int(sy_to)), tgt_radius, 2)
            pygame.draw.circle(surface, (255, 60, 50), (int(sx_to), int(sy_to)), 3)
            pygame.draw.line(surface, (235, 195, 50), (int(sx_to) - tgt_radius - 2, int(sy_to)), (int(sx_to) + tgt_radius + 2, int(sy_to)), 1)
            pygame.draw.line(surface, (235, 195, 50), (int(sx_to), int(sy_to) - tgt_radius - 2), (int(sx_to), int(sy_to) + tgt_radius + 2), 1)

            # Barra de carregamento de alcance sobre Tomoe
            bx, by = camera.apply(self.wx, self.wy, 1.45)
            charge_ratio = min(1.0, self.rope_charge_time / self.rope_charge_duration)
            bar_w = 34
            bar_h = 5
            pygame.draw.rect(surface, (24, 20, 22), (bx - bar_w // 2 - 1, by - 1, bar_w + 2, bar_h + 2), border_radius=2)
            charge_col = (int(255 * charge_ratio + 140 * (1 - charge_ratio)), int(210 * charge_ratio + 120 * (1 - charge_ratio)), 50)
            pygame.draw.rect(surface, charge_col, (bx - bar_w // 2, by, int(bar_w * charge_ratio), bar_h), border_radius=2)
            pygame.draw.rect(surface, COLOR_GOLD, (bx - bar_w // 2 - 1, by - 1, bar_w + 2, bar_h + 2), 1, border_radius=2)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="archer",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props={"is_drawing": (self.state == STATE_BOW_DRAW or self.is_charging_rope)}
        )

        # Indicador de retesamento do arco Yumi (mira precisa)
        if self.state == STATE_BOW_DRAW:
            bx, by = camera.apply(self.wx, self.wy, 1.35)
            progress = max(0.0, min(1.0, 1.0 - (self.draw_timer / self.draw_duration)))
            bar_w = 32
            bar_h = 5
            pygame.draw.rect(surface, (20, 30, 25), (bx - bar_w // 2 - 1, by - 1, bar_w + 2, bar_h + 2), border_radius=2)
            pygame.draw.rect(surface, (100, 220, 140), (bx - bar_w // 2, by, int(bar_w * progress), bar_h), border_radius=2)
