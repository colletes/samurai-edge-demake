"""
Okuni (Mestra dos Leques de Aço & Finta Teatral Kawarimi):
Abandona o veneno em favor de combate corpo a corpo técnico e gracioso
com Leques de Ferro (Tessen-jutsu) e manequim teatral de seda (Kawarimi Decoy)
que aplica whiff punish / stun no adversário ao ser golpeado.
"""
import math
import random
import pygame
from src.config import (
    COLOR_KABUKI_WHITE, COLOR_KABUKI_RED, COLOR_KABUKI_HAIR, COLOR_KABUKI_AURA,
    COLOR_SAKURA_PINK, COLOR_WHITE, COLOR_GOLD, COLOR_STEEL
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle, FloatingBanner

STATE_KABUKI_ROLL = "KABUKI_ROLL"

class OkuniDecoy:
    """Manequim teatral de seda deixado por Okuni durante a finta Kawarimi."""
    def __init__(self, wx: float, wy: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.owner = owner
        self.lifetime = 1.4   # Permanece ativa por 1.4s
        self.radius = 0.38
        self.is_active = True
        self.facing_x = getattr(owner, "facing_x", 1.0)
        self.facing_y = getattr(owner, "facing_y", 0.0)

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.is_active = False
        return self.is_active

    def on_hit(self, attacker, particles: list, banners: list, camera):
        """Absorve o golpe adversário, causa whiff stun e estoura em pétalas de cerejeira."""
        self.is_active = False
        camera.add_shake(7.0)
        banners.append(FloatingBanner("KAWARIMI WHIFF!", self.wx, self.wy, wz=1.7, color=COLOR_SAKURA_PINK))
        if attacker and attacker.is_alive:
            attacker.stun(0.45)  # Whiff punish fatal!
        if particles is not None:
            for _ in range(22):
                particles.append(SparkParticle(self.wx, self.wy, 0.45))

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        # Renderiza a ilusão em voxel com leve transparência teatral
        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            STATE_IDLE, 0.0, True,
            char_type="kabuki",
            alpha=210
        )
        sx, sy = camera.apply(self.wx, self.wy, 1.35)
        font = pygame.font.Font(None, 18)
        txt = font.render("KAWARIMI", True, COLOR_SAKURA_PINK)
        surface.blit(txt, (sx - txt.get_width() // 2, sy))


class Kabuki(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Okuni")
        self.char_type = "okuni"
        self.speed = 4.4

        # Ataque Melee: Dança dos Leques de Aço (Tessen-jutsu)
        self.attack_duration = 0.16
        self.recovery_duration = 0.12

        # Finta Teatral: Kawarimi Decoy
        self.decoy_cooldown = 2.8
        self.decoy_cooldown_timer = 0.0
        self.roll_speed = 12.0
        self.roll_duration = 0.20
        self.roll_dir_x = 1.0
        self.roll_dir_y = 0.0

    def can_act(self) -> bool:
        if not self.is_alive or self.state in (STATE_KABUKI_ROLL, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD):
            return False
        return True

    def trigger_fan_strike(self, target_wx: float, target_wy: float, particles: list = None):
        """Ataque Primário: Golpe veloz e duplo de leques de ferro afiados (Tessen)."""
        if not self.can_act():
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = self.attack_duration
        self.hitbox_active = True
        self.hitbox_radius = 1.25
        self.hitbox_center = (self.wx + self.facing_x * 0.75, self.wy + self.facing_y * 0.75)
        self.slash_dir = (self.facing_x, self.facing_y)

        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.35))

    def trigger_kawarimi_decoy(self, dir_x: float, dir_y: float, decoys: list, particles: list = None):
        """Ação Secundária: Substituição com boneco de seda Kawarimi e pirueta evasiva."""
        if not self.is_alive or self.decoy_cooldown_timer > 0 or self.state in (STATE_KABUKI_ROLL, STATE_STUNNED, STATE_DEAD):
            return

        if dir_x == 0 and dir_y == 0:
            dir_x, dir_y = -self.facing_x, -self.facing_y
        else:
            mag = math.hypot(dir_x, dir_y)
            if mag > 0.001:
                dir_x /= mag
                dir_y /= mag

        # Deixa o manequim na posição original
        if decoys is not None:
            decoy = OkuniDecoy(self.wx, self.wy, owner=self)
            decoys.append(decoy)

        self.decoy_cooldown_timer = self.decoy_cooldown
        self.state = STATE_KABUKI_ROLL
        self.state_timer = self.roll_duration
        self.roll_dir_x = dir_x
        self.roll_dir_y = dir_y
        self.facing_x = dir_x
        self.facing_y = dir_y
        self.hitbox_active = False

        if particles is not None:
            for _ in range(12):
                particles.append(SparkParticle(self.wx, self.wy, 0.4))

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.decoy_cooldown_timer > 0:
            self.decoy_cooldown_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Passo leve à frente durante o golpe dos leques
            step = 3.2 * dt
            new_wx = self.wx + self.facing_x * step
            new_wy = self.wy + self.facing_y * step

            hit_col = False
            for r in game_map.rocks:
                if r.check_collision(new_wx, new_wy, self.radius)[0]:
                    hit_col = True; break
            if game_map.well and game_map.well.check_collision(new_wx, new_wy, self.radius)[0]:
                hit_col = True

            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            self.hitbox_center = (self.wx + self.facing_x * 0.75, self.wy + self.facing_y * 0.75)

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
                self.hitbox_active = False

        elif self.state == STATE_KABUKI_ROLL:
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

            if particles is not None and random.random() < 0.4:
                particles.append(SparkParticle(self.wx, self.wy, 0.25))

            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza Okuni com leques de aço e efeito de camuflagem."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (235, 150, 180), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="kabuki",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving
        )
