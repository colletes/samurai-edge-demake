"""
Anne (A Espadachim Pirata):
Capitã bucaneira dos mares orientais. Despreza o código de honra com
cortes amplos de alfanje (Cutlass Cleave) em meia-lua e truques sujos como pó de pólvora nos olhos.
"""
import math
import random
import pygame
from src.config import (
    COLOR_PIRATE_COAT, COLOR_PIRATE_HAT, COLOR_PIRATE_AURA, COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_ROLL
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle

class PirateSwordswoman(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Anne")
        self.char_type = "pirate"
        self.speed = 4.9  # Velocidade ágil e agressiva de bucaneira (era 4.3)

        # Mecânica do Alfanje (Corte Amplo em Meia-Lua)
        self.cleave_cooldown = 0.35
        self.cleave_timer = 0.0

        # Ação Secundária: Tiro de Canhão Celestial (Tap Rápido ou Hold de Mira)
        self.cannon_cooldown = 4.5
        self.cannon_cooldown_timer = 0.0
        self.is_aiming_cannon = False
        self.cannon_target_wx = self.wx + 3.0
        self.cannon_target_wy = self.wy
        self.cannon_reticle_pulse = 0.0

        # Terceira Ação: Rolamento com Pólvora Negra (Black Powder Dash)
        self.roll_speed = 11.5
        self.roll_duration = 0.22
        self.roll_dir_x = 1.0
        self.roll_dir_y = 0.0
        self.dash_has_hit = False

    def can_act(self) -> bool:
        return self.is_alive and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD) and self.dash_recovery_timer <= 0

    def trigger_cutlass_cleave(self, target_wx: float, target_wy: float):
        """Ataque Primário: Golpe horizontal em meia-lua de 180° com o alfanje e avanço frontal vigoroso."""
        if not self.can_act() or self.cleave_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.22
        self.hitbox_active = True
        self.hitbox_radius = 1.55  # Raio ampliado para corte varredor
        self.slash_dir = (self.facing_x, self.facing_y)
        # Avanço frontal inicial com o corte (+62% de impulso frontal)
        self.wx += self.facing_x * 0.65
        self.wy += self.facing_y * 0.65
        self.hitbox_center = (self.wx + self.facing_x * 0.90, self.wy + self.facing_y * 0.90)
        self.cleave_timer = self.cleave_cooldown

    def trigger_quick_cannon(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None):
        """Disparo Imediato de Canhão (Tap rápido ou IA): dispara bola de canhão a distância efetiva."""
        if not self.is_alive or self.cannon_cooldown_timer > 0 or projectiles is None:
            return
        self.cannon_cooldown_timer = self.cannon_cooldown
        self.is_aiming_cannon = False

        from src.entities.projectile import CannonballProjectile
        projectiles.append(CannonballProjectile(target_wx, target_wy, owner=self))

        if particles is not None:
            for _ in range(12):
                particles.append(SparkParticle(self.wx, self.wy, 0.45))

    def start_cannon_strike(self, target_wx: float, target_wy: float):
        """Inicia o direcionamento do bombardeio naval orbital (Hold). Anne pode se mover e atacar livremente."""
        if not self.is_alive or self.cannon_cooldown_timer > 0:
            return
        self.is_aiming_cannon = True
        self.cannon_target_wx = target_wx
        self.cannon_target_wy = target_wy

    def update_cannon_strike(self, dt: float, target_wx: float, target_wy: float):
        """Atualiza o retículo de mira do canhão enquanto o botão de secundário for mantido pressionado."""
        if not self.is_alive or not self.is_aiming_cannon:
            self.is_aiming_cannon = False
            return
        self.cannon_reticle_pulse += dt * 8.0
        # O retículo de mira se move suavemente em direção à mira
        self.cannon_target_wx += (target_wx - self.cannon_target_wx) * min(1.0, dt * 10.0)
        self.cannon_target_wy += (target_wy - self.cannon_target_wy) * min(1.0, dt * 10.0)

    def release_cannon_strike(self, projectiles: list, particles: list = None):
        """Dispara o canhão ao soltar o botão de secundário (Release)."""
        if not self.is_aiming_cannon or not self.is_alive:
            self.is_aiming_cannon = False
            return
        self.is_aiming_cannon = False
        self.cannon_cooldown_timer = self.cannon_cooldown

        from src.entities.projectile import CannonballProjectile
        projectiles.append(CannonballProjectile(self.cannon_target_wx, self.cannon_target_wy, owner=self))

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.4))

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None):
        """Terceira Ação: Black Powder Dash — rolamento veloz com rastro de fumaça, mini-stun e lentidão."""
        if not self.is_alive or self.state in (STATE_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK) or self.dash_recovery_timer > 0:
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
        self.roll_dir_x = dir_x
        self.roll_dir_y = dir_y
        self.facing_x = dir_x
        self.facing_y = dir_y
        self.is_invulnerable_dodge = True
        self.hitbox_active = False
        self.dash_has_hit = False

        if particles is not None:
            for _ in range(10):
                particles.append(SparkParticle(self.wx, self.wy, 0.4))

    def trigger_deck_roll(self, dir_x: float, dir_y: float, particles: list = None):
        self.trigger_roll(dir_x, dir_y, particles)

    def trigger_gunpowder_blind(self, target_wx: float = None, target_wy: float = None, opponent = None, particles: list = None, projectiles: list = None):
        """Disparo tático compatível para IA e chamadas diretas."""
        if target_wx is not None and target_wy is not None:
            if projectiles is not None:
                self.trigger_quick_cannon(target_wx, target_wy, projectiles, particles)
            else:
                self.start_cannon_strike(target_wx, target_wy)

    def update(self, dt: float, game_map, particles: list = None, opponent = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.cleave_timer > 0:
            self.cleave_timer -= dt
        if self.cannon_cooldown_timer > 0:
            self.cannon_cooldown_timer -= dt
        if self.dash_recovery_timer > 0:
            self.dash_recovery_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Avanço com o corte do alfanje
            step = 6.0 * dt
            self.wx = max(1.0, min(game_map.cols - 1.0, self.wx + self.facing_x * step))
            self.wy = max(1.0, min(game_map.rows - 1.0, self.wy + self.facing_y * step))
            self.hitbox_center = (self.wx + self.facing_x * 0.90, self.wy + self.facing_y * 0.90)

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.06  # Recuperação ultrarrápida do alfanje
                self.hitbox_active = False

        elif self.state == STATE_ROLL:
            self.state_timer -= dt
            step = self.roll_speed * dt
            new_wx = self.wx + self.roll_dir_x * step
            new_wy = self.wy + self.roll_dir_y * step
            hit_col = False
            for r in game_map.rocks:
                if r.check_collision(new_wx, new_wy, self.radius)[0]:
                    hit_col = True; break
            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            # Rastro de pólvora e faíscas ao longo do trajeto (Item 4)
            if particles is not None and random.random() < 0.5:
                particles.append(SparkParticle(self.wx, self.wy, 0.3))

            # Impacto do Black Powder Dash no oponente: aplica mini-stun, desorientação e lentidão
            if opponent is not None and getattr(opponent, "is_alive", False) and not self.dash_has_hit:
                dist = math.hypot(self.wx - opponent.wx, self.wy - opponent.wy)
                if dist < (self.radius + getattr(opponent, "radius", 0.4) + 0.45):
                    self.dash_has_hit = True
                    if hasattr(opponent, "stun"):
                        opponent.stun(0.40)  # Mini-stun de 0.40s
                    if hasattr(opponent, "apply_slow"):
                        opponent.apply_slow(1.2)  # Lentidão de pólvora
                    # Leve repulsão física do impacto de pólvora
                    opponent.wx += self.roll_dir_x * 0.35
                    opponent.wy += self.roll_dir_y * 0.35
                    if particles is not None:
                        for _ in range(14):
                            particles.append(SparkParticle(opponent.wx, opponent.wy, 0.45))

            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.is_invulnerable_dodge = False
                self.dash_recovery_timer = self.dash_recovery_duration

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        # Retículo de mira náutica elegante do bombardeio de canhão (Astrolábio Isométrico)
        if self.is_aiming_cannon:
            cx, cy = camera.apply(self.cannon_target_wx, self.cannon_target_wy, 0.0)
            top_x, top_y = camera.apply(self.cannon_target_wx, self.cannon_target_wy, 4.5)

            # Trajetória balística zenital pontilhada vindo dos céus
            dash_steps = 7
            for i in range(dash_steps):
                if i % 2 == 0:
                    t1 = i / dash_steps
                    t2 = (i + 1) / dash_steps
                    p1 = (int(top_x + (cx - top_x) * t1), int(top_y + (cy - top_y) * t1))
                    p2 = (int(top_x + (cx - top_x) * t2), int(top_y + (cy - top_y) * t2))
                    pygame.draw.line(surface, (255, 200, 80), p1, p2, 1)

            rx = int(32 + 3 * math.sin(self.cannon_reticle_pulse * 2.0))
            ry = max(12, rx // 2)

            # Brilho suave translúcido no piso sob a mira
            glow_surf = pygame.Surface((rx * 2 + 16, ry * 2 + 16), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255, 80, 30, 40), (8, 8, rx * 2, ry * 2))
            surface.blit(glow_surf, (cx - rx - 8, cy - ry - 8))

            # Anel externo dourado de latão náutico
            pygame.draw.ellipse(surface, (218, 165, 32), (cx - rx, cy - ry, rx * 2, ry * 2), 2)

            # Anel interno carmim de perigo
            rx_in = rx - 8
            ry_in = max(8, rx_in // 2)
            pygame.draw.ellipse(surface, (220, 50, 40), (cx - rx_in, cy - ry_in, rx_in * 2, ry_in * 2), 1)

            # 4 Pontos cardeais do astrolábio girando suavemente
            rot = self.cannon_reticle_pulse * 0.9
            for k in range(4):
                angle = rot + k * (math.pi / 2)
                ox = int(rx * math.cos(angle))
                oy = int(ry * math.sin(angle))
                # Marcadores de bússola na borda
                pygame.draw.circle(surface, (255, 235, 120), (cx + ox, cy + oy), 2)
                # Hastes finas apontando para fora
                out_ox = int((rx + 6) * math.cos(angle))
                out_oy = int((ry + 3) * math.sin(angle))
                pygame.draw.line(surface, (218, 165, 32), (cx + ox, cy + oy), (cx + out_ox, cy + out_oy), 1)

            # Mira central de precisão e rubi central
            pygame.draw.line(surface, (255, 215, 80), (cx - 7, cy), (cx + 7, cy), 1)
            pygame.draw.line(surface, (255, 215, 80), (cx, cy - 4), (cx, cy + 4), 1)
            pygame.draw.circle(surface, (255, 245, 180), (cx, cy), 3)
            pygame.draw.circle(surface, (200, 30, 30), (cx, cy), 1)


        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="pirate",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving
        )
