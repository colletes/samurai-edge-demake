"""
O-Rin (A Menestrel do Shamisen / Assassina Acústica de Yoshiwara):
Cortesã e musicista genial que nunca empunha uma lâmina física.
- Velocidade ágil (4.9).
- Ataque Primário: Kamaitachi (Lâmina cortante de vácuo acústico em crescente disparada pelo dedilhado do shamisen, alcance 6.0 tiles).
- Ação Secundária: Ressonância Acústica 360° (Onda esférica concêntrica que desvia projéteis leves e empurra/atordoa rivais próximos).
- Olhos dourados/âmbar penetrantes com delineador kumadori vermelho e tatuagem de higanbana no pescoço.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_ORIN_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, resolve_playable_bounds
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import KamaitachiProjectile, AcousticResonanceWave, SpiralResonanceProjectile
from src.effects.particles import SparkParticle, FloatingBanner
from src.i18n import t

STATE_RESONANCE = "RESONANCE"


class OrinMinstrel(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="O-Rin")
        self.char_type = "orin"
        self.speed = 4.9  # Zoner ágil e evasiva
        self.max_hp = 2
        self.hp = 2

        # Ataque Primário: Kamaitachi (Lâmina Sônica de Vácuo)
        self.attack_duration = 0.18
        self.attack_recovery = 0.24
        self.kamaitachi_cooldown = 0.65  # Cadência controlada com intervalo entre dedilhados
        self.kamaitachi_timer = 0.0

        # Ação Secundária: Acorde de Ressonância Mortal (3 ondas em espiral a 120°)
        self.resonance_cooldown = 5.0
        self.resonance_timer = 0.0
        self.resonance_duration = 0.35
        self.active_resonance_waves: list[AcousticResonanceWave] = []

        # Esquiva ágil
        self.is_agile_dodge = True
        self.roll_speed = 9.8
        self.roll_duration = 0.20
        self.roll_recovery_duration = 0.12
        self.roll_cooldown_duration = 0.32
        self.recovery_duration = self.attack_recovery

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_kamaitachi_pluck(self, aim_x: float, aim_y: float, projectiles: list, particles: list = None):
        """Ataque Primário: Disparo de lâmina acústica de vácuo Kamaitachi com cooldown."""
        if not self.can_act() or self.kamaitachi_timer > 0:
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.attack_duration
        self.kamaitachi_timer = self.kamaitachi_cooldown
        self.hitbox_active = False  # O dano é conduzido pelo projétil acústico

        # Instanciar projétil Kamaitachi
        proj = KamaitachiProjectile(
            wx=self.wx + self.facing_x * 0.40,
            wy=self.wy + self.facing_y * 0.40,
            wz=0.35,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self,
            max_range=6.2
        )
        projectiles.append(proj)

        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(self.wx + self.facing_x * 0.3, self.wy + self.facing_y * 0.3, 0.2))
        return True

    def trigger_deadly_resonance_chord(self, aim_x: float, aim_y: float, projectiles: list, particles: list = None, banners: list = None):
        """Ação Secundária: Acorde de Ressonância Mortal.
        Dispara 3 ondas sônicas curvas separadas por 120° em espiral expansiva. Cooldown 5.0s."""
        if not self.can_act() or self.resonance_timer > 0:
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_RESONANCE
        self.state_timer = self.resonance_duration
        self.resonance_timer = self.resonance_cooldown
        self.hitbox_active = False

        base_angle = math.atan2(self.facing_y, self.facing_x)
        # 3 ondas acústicas em espiral a 120° (2π/3 radianos)
        for i in range(3):
            proj_angle = base_angle + i * (2.0 * math.pi / 3.0)
            spawn_x = self.wx + math.cos(proj_angle) * 0.45
            spawn_y = self.wy + math.sin(proj_angle) * 0.45
            proj = SpiralResonanceProjectile(
                wx=spawn_x,
                wy=spawn_y,
                wz=0.35,
                initial_angle=proj_angle,
                owner=self,
                curve_direction=1.0 if i % 2 == 0 else -1.0,
                speed=11.5,
                angular_speed=2.2,
                max_range=7.2
            )
            projectiles.append(proj)

        if banners is not None:
            banners.append(FloatingBanner(t("banner_resonant_chord"), self.wx, self.wy, wz=1.75, color=(245, 80, 150)))

        if particles is not None:
            for _ in range(14):
                particles.append(SparkParticle(self.wx, self.wy, 0.4, color=(255, 120, 180)))
        return True

    def trigger_resonance_shockwave(self, aim_x: float, aim_y: float, projectiles: list, particles: list = None, banners: list = None):
        """Alias retrocompatível para Acorde de Ressonância Mortal."""
        return self.trigger_deadly_resonance_chord(aim_x, aim_y, projectiles, particles=particles, banners=banners)

    def set_facing(self, target_wx: float, target_wy: float):
        """Define a direção que está olhando."""
        dx = target_wx - self.wx
        dy = target_wy - self.wy
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            self.facing_x = dx / dist
            self.facing_y = dy / dist

    def update(self, dt: float, game_map, particles: list = None, opponent = None, projectiles: list = None):
        """Atualização de ciclo de combate da O-Rin."""
        super().update_dodge_timers(dt)

        if self.resonance_timer > 0:
            self.resonance_timer = max(0.0, self.resonance_timer - dt)

        if self.kamaitachi_timer > 0:
            self.kamaitachi_timer = max(0.0, self.kamaitachi_timer - dt)

        # Atualizar ondas de choque ativas
        if self.active_resonance_waves:
            fighters = [self]
            if opponent:
                fighters.append(opponent)
            self.active_resonance_waves = [
                w for w in self.active_resonance_waves
                if w.update(dt, projectiles or [], fighters, game_map)
            ]

        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            return

        # 1. Ataque Primário Sônico (ATTACK)
        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.attack_recovery
            return

        # 2. Ressonância 360° (RESONANCE)
        if self.state == STATE_RESONANCE:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.12
            return

        # 3. Recuperação (RECOVERY)
        if self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # 4. Atordoada (STUNNED)
        if self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o modelo voxel 3D da O-Rin com shamisen, quimono escuro e kanzashi."""
        # Renderizar ondas de choque ativas
        for w in self.active_resonance_waves:
            w.render(surface, camera)

        extra = {
            "is_resonance": (self.state == STATE_RESONANCE)
        }
        render_voxel_humanoid(
            surface=surface,
            camera=camera,
            wx=self.wx, wy=self.wy, wz=self.wz,
            facing_x=self.facing_x, facing_y=self.facing_y,
            state=self.state,
            state_timer=self.state_timer,
            is_alive=self.is_alive,
            char_type="orin",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props=extra
        )
