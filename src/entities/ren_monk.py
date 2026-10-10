"""
Ren (O Monge Shaolin de Punhos de Ferro e Kiai):
Guerreiro budista de agilidade máxima. Ataca desarmado com sequências rápidas
de socos, palmas e chutes marciais, além do devastador grito místico KIAI
que cria uma barreira esférica repelente de projéteis e com alto knockback.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_ROLL
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle, FloatingBanner

COLOR_REN_AURA = (245, 140, 35)

class RenMonk(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Ren")
        self.char_type = "ren"
        self.speed = 5.4  # Máxima agilidade de monge Shaolin
        self.max_hp = 2
        self.hp = 2

        # Combo de Artes Marciais (3 Golpes: Jab rápido, Chute Circular, Palma do Dragão)
        self.combo_step = 0
        self.combo_window_timer = 0.0
        self.attack_cooldown_timer = 0.0

        # Ação Secundária: Grito Místico Kiai (Aura Esférica Repelente)
        self.kiai_cooldown = 3.5
        self.kiai_timer = 0.0
        self.kiai_aura_active = False
        self.kiai_aura_timer = 0.0
        self.kiai_aura_radius = 0.0
        self.kiai_max_radius = 2.4

        # Esquiva ágil
        self.is_agile_dodge = True
        self.roll_speed = 9.8
        self.roll_duration = 0.20
        self.roll_recovery_duration = 0.12
        self.roll_cooldown_duration = 0.32
        self.recovery_duration = 0.20

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_punch_combo(self, target_wx: float, target_wy: float):
        """Ataque Primário: Combo Shaolin ritmado de 3 acertos."""
        if not self.is_alive or self.state in (STATE_STUNNED, STATE_DEAD):
            return

        # Avançar o passo de combo
        if self.combo_window_timer > 0 and self.combo_step < 3:
            self.combo_step += 1
        else:
            if not self.can_act():
                return
            self.combo_step = 1

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK

        if self.combo_step == 1:
            # Passo 1: Jab frontal veloz
            self.state_timer = 0.12
            self.combo_window_timer = 0.38
            self.hitbox_radius = 1.05
            self.hitbox_active = True
            self.hitbox_damage = 1
            # Impulso frontal ágil
            self.wx += self.facing_x * 0.40
            self.wy += self.facing_y * 0.40
        elif self.combo_step == 2:
            # Passo 2: Chute circular alto
            self.state_timer = 0.14
            self.combo_window_timer = 0.40
            self.hitbox_radius = 1.20
            self.hitbox_active = True
            self.hitbox_damage = 1
            self.wx += self.facing_x * 0.50
            self.wy += self.facing_y * 0.50
        else:
            # Passo 3: Palma do Dragão Chi (Golpe Letal)
            self.state_timer = 0.20
            self.combo_window_timer = 0.0
            self.hitbox_radius = 1.40
            self.hitbox_active = True
            self.hitbox_damage = 2
            self.wx += self.facing_x * 0.70
            self.wy += self.facing_y * 0.70

        self.slash_dir = (self.facing_x, self.facing_y)
        self.hitbox_center = (self.wx + self.facing_x * 0.75, self.wy + self.facing_y * 0.75)

    def trigger_primary_attack(self, target_wx: float, target_wy: float):
        self.trigger_punch_combo(target_wx, target_wy)

    def trigger_kiai_shout(self, target_wx: float = None, target_wy: float = None, opponent=None, projectiles: list = None, particles: list = None, banners: list = None, game_map=None):
        """
        Ação Secundária: Grito de Kiai da Montanha.
        Gera uma aura esférica de energia que repele projéteis e aplica alto knockback no oponente.
        """
        if not self.can_act() or self.kiai_timer > 0:
            return

        if target_wx is not None and target_wy is not None:
            self.set_facing(target_wx, target_wy)
        self.kiai_timer = self.kiai_cooldown
        self.kiai_aura_active = True
        self.kiai_aura_timer = 0.40
        self.kiai_aura_radius = 0.5
        self.state = "KIAI_SHOUT"
        self.state_timer = 0.35

        # Disparar partículas de Chi dourado
        if particles is not None:
            for _ in range(24):
                ang = random.uniform(0, math.pi * 2)
                sp = random.uniform(2.5, 6.0)
                particles.append(SparkParticle(self.wx + math.cos(ang) * 0.3, self.wy + math.sin(ang) * 0.3, 0.4, color=COLOR_GOLD))

        if banners is not None:
            banners.append(FloatingBanner(self.wx, self.wy - 0.6, "KIAI!", COLOR_GOLD))

        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent.SWORD_CLASH)
        except Exception:
            pass

        # Repelir projéteis imediatamente
        if projectiles is not None:
            for proj in projectiles:
                if getattr(proj, "owner", None) != self and getattr(proj, "active", True):
                    dx = proj.wx - self.wx
                    dy = proj.wy - self.wy
                    dist = math.hypot(dx, dy)
                    if dist <= self.kiai_max_radius:
                        # Refletir / repelir na direção oposta com maior velocidade
                        norm = dist or 1.0
                        proj.vx = (dx / norm) * 16.0
                        proj.vy = (dy / norm) * 16.0
                        proj.owner = self  # Agora pertence ao Ren!

        # Se o oponente estiver dentro do raio, repelir com alto knockback
        if opponent is not None and getattr(opponent, "is_alive", True):
            dx = opponent.wx - self.wx
            dy = opponent.wy - self.wy
            dist = math.hypot(dx, dy)
            if dist <= self.kiai_max_radius:
                norm = dist or 1.0
                nx, ny = dx / norm, dy / norm
                travel = 3.8
                if hasattr(opponent, "apply_forced_displacement") and game_map is not None:
                    opponent.apply_forced_displacement(nx * travel, ny * travel, game_map)
                else:
                    opponent.wx += nx * travel
                    opponent.wy += ny * travel
                # Atordoamento leve (soft stun)
                if hasattr(opponent, "stun"):
                    opponent.stun(0.40)

    def trigger_secondary_action(self, target_wx: float, target_wy: float, opponent=None, projectiles: list = None, particles: list = None, banners: list = None):
        self.trigger_kiai_shout(target_wx, target_wy, opponent=opponent, projectiles=projectiles, particles=particles, banners=banners)

    def update(self, dt: float, game_map, particles: list = None, banners: list = None, opponent=None, **kwargs):
        if not self.is_alive:
            return

        self.update_stealth(game_map)
        self.update_dodge_timers(dt)
        self.update_pit(dt, game_map, particles, banners)

        if self.kiai_timer > 0:
            self.kiai_timer = max(0.0, self.kiai_timer - dt)

        if self.combo_window_timer > 0:
            self.combo_window_timer = max(0.0, self.combo_window_timer - dt)
            if self.combo_window_timer <= 0:
                self.combo_step = 0

        # Atualizar expansão da onda de Kiai
        if self.kiai_aura_active:
            self.kiai_aura_timer -= dt
            progress = 1.0 - (self.kiai_aura_timer / 0.40)
            self.kiai_aura_radius = self.kiai_max_radius * min(1.0, progress * 1.4)
            if self.kiai_aura_timer <= 0:
                self.kiai_aura_active = False

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            step = 6.5 * dt
            new_wx = self.wx + self.facing_x * step
            new_wy = self.wy + self.facing_y * step
            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            self.hitbox_center = (self.wx + self.facing_x * 0.75, self.wy + self.facing_y * 0.75)
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
                self.hitbox_active = False

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.combo_step = 0

        # Transição de KIAI_SHOUT para IDLE
        elif self.state == "KIAI_SHOUT":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_ROLL:
            self.update_roll(dt, game_map)

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render_voxel(self, surface: pygame.Surface, camera, shadow: bool = True):
        # Renderizar aura de Kiai translúcida expandindo no solo
        if self.kiai_aura_active and self.kiai_aura_radius > 0.1:
            cx, cy = camera.apply(self.wx, self.wy, 0.05)
            # Converter raio do mundo para raio em pixels da tela
            rx, ry = camera.apply(self.wx + self.kiai_aura_radius, self.wy, 0.05)
            r_px = int(math.hypot(rx - cx, ry - cy))
            if r_px > 4:
                kiai_surf = pygame.Surface((r_px * 2 + 10, r_px * 2 + 10), pygame.SRCALPHA)
                alpha = int(max(0, min(180, (self.kiai_aura_timer / 0.40) * 180)))
                pygame.draw.circle(kiai_surf, (255, 215, 60, alpha), (r_px + 5, r_px + 5), r_px, 3)
                pygame.draw.circle(kiai_surf, (255, 160, 40, alpha // 2), (r_px + 5, r_px + 5), max(1, r_px - 4), 2)
                surface.blit(kiai_surf, (cx - r_px - 5, cy - r_px - 5))

        render_voxel_humanoid(
            surface, camera, self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y, self.state, self.state_timer,
            self.is_alive, char_type="ren", walk_timer=self.walk_cycle,
            alpha=self.alpha, is_moving=self.is_moving
        )
