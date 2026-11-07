"""
O-Rin (A Menestrel do Shamisen / Assassina Acústica de Yoshiwara):
Cortesã e musicista genial que nunca empunha uma lâmina física.
- Velocidade ágil (4.90 m/s).
- Golpe Primário: Combo Rítmico Kamaitachi (Lâminas cortantes de vácuo acústico em 2 passos):
  - Passo 1: Palhetada Rápida — Lâmina Sônica Simples (alcance 5.5m, startup 0.14s, rec 0.16s).
  - Passo 2: Palhetada Dupla com Bachi — Lâminas Gêmeas Cruzadas em V com micro-avanço de 0.20m (alcance 6.0m, startup 0.16s, rec 0.20s).
- Golpe Secundário: Ressonância Acústica 360°:
  - Onda de choque esférica imediata que dissipa projéteis em 2.0m e empurra oponentes adjacentes (stun 0.35s).
  - 3 ondas acústicas curvas em espiral a 120° (cooldown 4.5s).
- Terceira Ação / Esquiva: Silk Sleeve Glide (Deslize de Seda Evasivo com 13 i-frames e ondulação de mangas).
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
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, resolve_playable_bounds,
    slide_movement_against_obstacles
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
        self.speed = 4.90  # Zoner ágil e evasiva
        self.max_hp = 2
        self.hp = 2

        # Combo Rítmico de Palhetadas (Kamaitachi)
        self.combo_step = 0
        self.combo_target_step = 0
        self.combo_window_timer = 0.0
        self.combo_window = 0.50
        self.attack_duration = 0.14
        self.attack_recovery = 0.16
        self.kamaitachi_cooldown = 0.35
        self.kamaitachi_timer = 0.0

        # Ação Secundária: Acorde de Ressonância Mortal com Repulsão 360°
        self.resonance_cooldown = 4.5
        self.resonance_timer = 0.0
        self.resonance_duration = 0.35
        self.active_resonance_waves: list[AcousticResonanceWave] = []

        # Terceira Ação: Silk Sleeve Glide (Deslize de Seda com 13 i-frames)
        self.is_agile_dodge = True
        self.roll_speed = 9.8
        self.roll_duration = 0.20
        self.roll_recovery_duration = 0.12
        self.roll_cooldown_duration = 0.32
        self.recovery_duration = self.attack_recovery
        self.action_name = "Kamaitachi Sônico"

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def _start_combo_step(self, step: int, projectiles: list, particles: list = None, game_map = None):
        """Inicia o passo do combo de palhetada de Shamisen (1 ou 2)."""
        self.combo_step = step
        self.state = STATE_ATTACK
        self.hitbox_active = False

        if step == 1:
            # Passo 1: Lâmina Sônica Simples de Vácuo
            self.state_timer = 0.14
            self.recovery_duration = 0.16
            self.kamaitachi_timer = self.kamaitachi_cooldown
            self.action_name = "Kamaitachi Sônico"

            proj = KamaitachiProjectile(
                wx=self.wx + self.facing_x * 0.40,
                wy=self.wy + self.facing_y * 0.40,
                wz=0.35,
                dir_x=self.facing_x,
                dir_y=self.facing_y,
                owner=self,
                max_range=5.5
            )
            projectiles.append(proj)

            if particles is not None:
                for _ in range(6):
                    particles.append(SparkParticle(self.wx + self.facing_x * 0.3, self.wy + self.facing_y * 0.3, 0.2, color=(90, 215, 255)))
        else:
            # Passo 2: Dupla Lâmina Cruzada em V com micro-avanço de 0.20m
            self.state_timer = 0.16
            self.recovery_duration = 0.20
            self.kamaitachi_timer = self.kamaitachi_cooldown
            self.action_name = "Kamaitachi Duplo"

            # Micro-avanço de 0.20m
            lunge = 0.20
            if game_map:
                self.wx, self.wy = slide_movement_against_obstacles(self.wx, self.wy, self.facing_x * lunge, self.facing_y * lunge, self.radius, game_map)
            else:
                self.wx += self.facing_x * lunge
                self.wy += self.facing_y * lunge

            base_ang = math.atan2(self.facing_y, self.facing_x)
            ang1 = base_ang - 0.14
            ang2 = base_ang + 0.14

            proj1 = KamaitachiProjectile(
                wx=self.wx + math.cos(ang1) * 0.42,
                wy=self.wy + math.sin(ang1) * 0.42,
                wz=0.35,
                dir_x=math.cos(ang1),
                dir_y=math.sin(ang1),
                owner=self,
                max_range=6.0
            )
            proj2 = KamaitachiProjectile(
                wx=self.wx + math.cos(ang2) * 0.42,
                wy=self.wy + math.sin(ang2) * 0.42,
                wz=0.35,
                dir_x=math.cos(ang2),
                dir_y=math.sin(ang2),
                owner=self,
                max_range=6.0
            )
            projectiles.extend([proj1, proj2])

            if particles is not None:
                for _ in range(12):
                    particles.append(SparkParticle(self.wx + self.facing_x * 0.35, self.wy + self.facing_y * 0.35, 0.28, color=(255, 220, 85)))

    def trigger_kamaitachi_pluck(self, aim_x: float = None, aim_y: float = None, projectiles: list = None, particles: list = None, game_map = None):
        """Ataque Primário: Combo de Palhetadas Kamaitachi no Shamisen."""
        if not self.is_alive or self.state in (STATE_STUNNED, STATE_DEAD):
            return False

        if aim_x is None or aim_y is None:
            aim_x, aim_y = self.facing_x, self.facing_y

        if projectiles is None:
            projectiles = []

        # Input buffer durante ataque em andamento
        if self.state == STATE_ATTACK:
            if self.combo_step == 1:
                self.combo_target_step = 2
            return False

        # Encadeia para passo 2 se estiver na janela ativa pós-passo 1
        is_combo_chain = (self.combo_window_timer > 0 and self.combo_step == 1)
        if not is_combo_chain and self.kamaitachi_timer > 0:
            return False

        if not self.can_act():
            return False

        self.set_facing(aim_x, aim_y)

        next_step = 2 if is_combo_chain else 1
        self.combo_target_step = next_step
        self._start_combo_step(next_step, projectiles, particles=particles, game_map=game_map)
        return True

    def trigger_attack(self, aim_x: float = None, aim_y: float = None, projectiles: list = None, particles: list = None, game_map = None):
        """Interface universal de ataque primário para a O-Rin."""
        return self.trigger_kamaitachi_pluck(aim_x, aim_y, projectiles=projectiles, particles=particles, game_map=game_map)

    def trigger_deadly_resonance_chord(self, aim_x: float = None, aim_y: float = None, projectiles: list = None, particles: list = None, banners: list = None, opponent = None, game_map = None):
        """Ação Secundária: Acorde de Ressonância Mortal com Repulsão Acústica 360° imediata.
        - Pulso esférico dissipa projéteis em 2.0m e empurra oponentes adjacentes com stun leve (0.35s).
        - Dispara 3 ondas sônicas curvas separadas por 120° em espiral expansiva. Cooldown 4.5s."""
        if not self.can_act() or self.resonance_timer > 0:
            return False

        if aim_x is None or aim_y is None:
            aim_x, aim_y = self.facing_x, self.facing_y

        if projectiles is None:
            projectiles = []

        self.set_facing(aim_x, aim_y)
        self.state = STATE_RESONANCE
        self.state_timer = self.resonance_duration
        self.resonance_timer = self.resonance_cooldown
        self.hitbox_active = False
        self.action_name = "Ressonância 360°"

        # 1. Repulsão acústica imediata de projéteis hostis em 2.0m
        if projectiles is not None:
            for p in projectiles:
                if getattr(p, "is_active", False) and getattr(p, "owner", None) != self:
                    dp = math.hypot(p.wx - self.wx, p.wy - self.wy)
                    if dp <= 2.0:
                        p.is_active = False
                        if particles is not None:
                            for _ in range(8):
                                particles.append(SparkParticle(p.wx, p.wy, 0.3, color=(90, 215, 255)))

        # 2. Empurrão com choque sonoro no oponente adjacente
        opp_hit = False
        if opponent and getattr(opponent, "is_alive", True):
            dopp = math.hypot(opponent.wx - self.wx, opponent.wy - self.wy)
            if dopp <= 2.20:
                opp_hit = True
                dx = opponent.wx - self.wx
                dy = opponent.wy - self.wy
                dist = math.hypot(dx, dy) or 1.0
                nx, ny = dx / dist, dy / dist
                opponent.stun(0.35)
                opponent.apply_forced_displacement(nx * 1.6, ny * 1.6, game_map)
                if banners is not None:
                    banners.append(FloatingBanner("RESONANCE BLAST!", self.wx, self.wy, wz=1.75, color=(245, 80, 150)))
                if particles is not None:
                    for _ in range(12):
                        particles.append(SparkParticle(opponent.wx, opponent.wy, 0.35, color=(255, 120, 180)))

        # 3. Disparo das 3 ondas acústicas em espiral a 120°
        base_angle = math.atan2(self.facing_y, self.facing_x)
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

        if banners is not None and not opp_hit:
            banners.append(FloatingBanner(t("banner_resonant_chord"), self.wx, self.wy, wz=1.75, color=(245, 80, 150)))

        if particles is not None:
            for _ in range(16):
                particles.append(SparkParticle(self.wx, self.wy, 0.4, color=(90, 215, 255)))
        return True

    def trigger_resonance_shockwave(self, aim_x: float, aim_y: float, projectiles: list, particles: list = None, banners: list = None, opponent = None, game_map = None):
        """Alias retrocompatível para Acorde de Ressonância Mortal."""
        return self.trigger_deadly_resonance_chord(aim_x, aim_y, projectiles, particles=particles, banners=banners, opponent=opponent, game_map=game_map)

    def trigger_silk_glide(self, dwx: float, dwy: float, particles: list = None, banners: list = None, opponent = None, game_map = None, projectiles: list = None):
        """
        Terceira Ação (Esquiva / Deslize de Seda Evasivo):
        - 13 i-frames (invulnerabilidade a golpes e imunidade balística a projéteis diretos).
        - Deslize rente ao solo guiado pelo som com ondulação de mangas Furisode e flores de Higanbana.
        - Velocidade 9.8, duração 0.20s, recovery 0.12s, cooldown 0.32s.
        """
        if not self.is_alive or self.state in (STATE_ROLL, STATE_STUNNED, STATE_DEAD):
            return False
        if self.roll_cooldown_timer > 0:
            return False

        dist = math.hypot(dwx, dwy)
        if dist > 0.05:
            self.facing_x = dwx / dist
            self.facing_y = dwy / dist

        self.state = STATE_ROLL
        self.state_timer = self.roll_duration
        self.invincible_timer = 13.0 / 60.0
        self.is_invulnerable_dodge = True
        self.invulnerable = True
        self.is_projectile_immune = True
        self.is_projectile_invincible = True
        self.hitbox_active = False
        self.action_name = "Deslize de Seda"

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.22, color=(225, 45, 75)))
        return True

    def trigger_roll(self, dwx: float, dwy: float, particles: list = None, banners: list = None, opponent = None, game_map = None, projectiles: list = None):
        """Compatibilidade de esquiva com interface padrão Samurai."""
        return self.trigger_silk_glide(dwx, dwy, particles=particles, banners=banners, opponent=opponent, game_map=game_map, projectiles=projectiles)

    def update_roll(self, dt: float, game_map, particles: list = None):
        """Atualização do deslize de seda Silk Sleeve Glide."""
        if self.state != STATE_ROLL:
            return

        self.state_timer -= dt
        step = self.roll_speed * dt
        dx = self.facing_x * step
        dy = self.facing_y * step

        new_wx, new_wy = slide_movement_against_obstacles(self.wx, self.wy, dx, dy, self.radius, game_map)
        self.wx, self.wy = new_wx, new_wy

        if particles is not None and random.random() < 0.60:
            particles.append(SparkParticle(self.wx, self.wy, 0.20, color=(225, 45, 75)))

        if self.state_timer <= 0:
            self.state = STATE_IDLE
            self.is_invulnerable_dodge = False
            self.invulnerable = False
            self.is_projectile_immune = False
            self.roll_recovery_timer = self.roll_recovery_duration
            self.roll_cooldown_timer = self.roll_cooldown_duration
            self.dash_recovery_timer = self.roll_recovery_duration

    def set_facing(self, target_wx: float, target_wy: float):
        """Define o vetor de orientação (facing) em direção ao alvo."""
        dx = target_wx - self.wx
        dy = target_wy - self.wy
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            self.facing_x = dx / dist
            self.facing_y = dy / dist

    def update(self, dt: float, game_map, particles: list = None, opponent = None, projectiles: list = None, banners: list = None):
        """Atualização de ciclo de combate da O-Rin."""
        super().update_dodge_timers(dt)

        if self.resonance_timer > 0:
            self.resonance_timer = max(0.0, self.resonance_timer - dt)

        if self.kamaitachi_timer > 0:
            self.kamaitachi_timer = max(0.0, self.kamaitachi_timer - dt)

        # Decréscimo da janela de encadeamento do combo
        if self.state != STATE_ATTACK and self.combo_window_timer > 0:
            self.combo_window_timer = max(0.0, self.combo_window_timer - dt)
            if self.combo_window_timer <= 0:
                self.combo_step = 0
                self.combo_target_step = 0

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
                if self.combo_step < self.combo_target_step and projectiles is not None:
                    self._start_combo_step(self.combo_target_step, projectiles, particles=particles, game_map=game_map)
                else:
                    self.state = STATE_RECOVERY
                    self.state_timer = self.recovery_duration
                    if self.combo_step == 1:
                        self.combo_window_timer = self.combo_window
                    else:
                        self.combo_window_timer = 0.0
                        self.combo_step = 0
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
                if self.combo_window_timer <= 0:
                    self.combo_step = 0
            return

        # 4. Atordoada (STUNNED)
        if self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o modelo voxel 3D da O-Rin com shamisen, quimono escuro e kanzashi."""
        for w in self.active_resonance_waves:
            w.render(surface, camera)

        roll_p = 0.0
        if self.state == STATE_ROLL:
            roll_p = max(0.0, min(1.0, 1.0 - (self.state_timer / max(0.001, self.roll_duration))))

        extra = {
            "is_resonance": (self.state == STATE_RESONANCE),
            "is_roll": (self.state == STATE_ROLL),
            "roll_prog": roll_p,
            "combo_step": getattr(self, "combo_step", 1),
            "action_name": getattr(self, "action_name", ""),
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
            is_moving=(self.is_moving or self.state == STATE_ROLL),
            extra_props=extra
        )
