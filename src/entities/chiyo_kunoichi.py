"""
Chiyo (A Kunoichi das Duas Nodachi):
Guerreira shinobi graciosa e letal armada com duas lâminas gigantes Nodachi de 1,60m.
Possui estilo de luta defensivo e evasivo, utilizando a lendária Dança Mai com as
duas nodachi para confundir, defletir projéteis e desferir cortes em tesoura com alcance estendido.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_ROLL, STATE_PARRY
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle, FloatingBanner

COLOR_CHIYO_AURA = (210, 36, 48)

class ChiyoKunoichi(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Chiyo")
        self.char_type = "chiyo"
        self.speed = 4.8  # Movimentação fluida e evasiva
        self.max_hp = 2
        self.hp = 2

        # Ataque Primário: Corte Duplo Tesoura das Nodachi
        self.scissor_cooldown = 0.40
        self.scissor_timer = 0.0

        # Ação Secundária: Dança Mai com as 2 Nodachi (Defesa, Distração e Contra-Ataque)
        self.mai_dance_cooldown = 3.0
        self.mai_dance_timer = 0.0
        self.mai_cooldown = 3.0
        self.mai_timer = 0.0
        self.mai_active = False
        self.mai_counter_ready = False

        # Esquiva ágil
        self.is_agile_dodge = True
        self.roll_speed = 9.2
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.14
        self.roll_cooldown_duration = 0.35
        self.recovery_duration = 0.26

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_scissor_strike(self, target_wx: float, target_wy: float):
        """Ataque Primário: Tesoura Dupla com as 2 Nodachi (Alcance 2.3m)."""
        if not self.can_act() or self.scissor_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.20
        self.hitbox_active = True
        self.hitbox_radius = 1.65  # Amplo raio do arco das espadas gigantes
        self.hitbox_damage = 2     # Golpe letal
        self.slash_dir = (self.facing_x, self.facing_y)
        # Avanço gracioso com as lâminas
        self.wx += self.facing_x * 0.50
        self.wy += self.facing_y * 0.50
        self.hitbox_center = (self.wx + self.facing_x * 1.10, self.wy + self.facing_y * 1.10)
        self.scissor_timer = self.scissor_cooldown

    def trigger_primary_attack(self, target_wx: float, target_wy: float):
        self.trigger_scissor_strike(target_wx, target_wy)

    trigger_scissor_slash = trigger_scissor_strike

    def trigger_mai_dance(self, target_wx: float = None, target_wy: float = None, opponent=None, projectiles: list = None, particles: list = None, banners: list = None):
        """
        Ação Secundária: Dança Mai com as 2 Nodachi.
        Chiyo inicia um vórtice giratório de lâminas que deflete projéteis e a protege de ataques corpo a corpo.
        """
        if not self.can_act() or self.mai_dance_timer > 0:
            return

        if target_wx is not None and target_wy is not None:
            self.set_facing(target_wx, target_wy)
        self.mai_dance_timer = self.mai_dance_cooldown
        self.state = "MAI_DANCE"
        self.state_timer = 0.38
        self.is_invulnerable_dodge = True  # I-frames durante a dança
        self.mai_active = True
        self.hitbox_active = True
        self.hitbox_radius = 1.40
        self.hitbox_damage = 1
        self.hitbox_center = (self.wx, self.wy)

        if banners is not None:
            banners.append(FloatingBanner(self.wx, self.wy - 0.6, "MAI!", COLOR_CHIYO_AURA))

        # Partículas de pétalas e faíscas escarlates
        if particles is not None:
            for _ in range(18):
                ang = random.uniform(0, math.pi * 2)
                particles.append(SparkParticle(self.wx + math.cos(ang) * 0.4, self.wy + math.sin(ang) * 0.4, 0.35, color=(210, 40, 50)))

        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent.SWORD_CLASH)
        except Exception:
            pass

        # Defletir projéteis próximos
        if projectiles is not None:
            for proj in projectiles:
                if getattr(proj, "owner", None) != self and getattr(proj, "active", True):
                    dx = proj.wx - self.wx
                    dy = proj.wy - self.wy
                    if math.hypot(dx, dy) <= 1.8:
                        proj.vx = -proj.vx * 1.2
                        proj.vy = -proj.vy * 1.2
                        proj.owner = self

    def trigger_secondary_action(self, target_wx: float = None, target_wy: float = None, opponent=None, projectiles: list = None, particles: list = None, banners: list = None):
        self.trigger_mai_dance(target_wx, target_wy, opponent=opponent, projectiles=projectiles, particles=particles, banners=banners)

    trigger_nodachi_mai = trigger_mai_dance

    def update(self, dt: float, game_map, particles: list = None, banners: list = None, opponent=None, **kwargs):
        if not self.is_alive:
            return

        self.update_stealth(game_map)
        self.update_dodge_timers(dt)
        self.update_pit(dt, game_map, particles, banners)

        if self.scissor_timer > 0:
            self.scissor_timer = max(0.0, self.scissor_timer - dt)

        if self.mai_dance_timer > 0:
            self.mai_dance_timer = max(0.0, self.mai_dance_timer - dt)
        self.mai_timer = self.mai_dance_timer

        if self.state in (STATE_ATTACK, "SCISSOR_SLASH"):
            self.state_timer -= dt
            step = 5.8 * dt
            new_wx = self.wx + self.facing_x * step
            new_wy = self.wy + self.facing_y * step
            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            self.hitbox_center = (self.wx + self.facing_x * 1.15, self.wy + self.facing_y * 1.15)
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
                self.hitbox_active = False

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        # Fim da Dança Mai
        elif self.state == "MAI_DANCE":
            self.state_timer -= dt
            if particles is not None and random.random() < 0.35:
                particles.append(SparkParticle(self.wx, self.wy, 0.25, color=(190, 30, 45)))
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.is_invulnerable_dodge = False
                self.mai_active = False

        elif self.state == STATE_ROLL:
            self.update_roll(dt, game_map)

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render_voxel(self, surface: pygame.Surface, camera, shadow: bool = True):
        # Efeito visual de vórtice escarlate durante a Dança Mai
        if self.state == "MAI_DANCE":
            cx, cy = camera.apply(self.wx, self.wy, 0.3)
            r_px = int(32 * camera.zoom)
            vortex_surf = pygame.Surface((r_px * 2 + 10, r_px * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(vortex_surf, (215, 38, 50, 110), (r_px + 5, r_px + 5), r_px, 2)
            pygame.draw.circle(vortex_surf, (245, 120, 130, 90), (r_px + 5, r_px + 5), max(1, r_px - 6), 1)
            surface.blit(vortex_surf, (cx - r_px - 5, cy - r_px - 5))

        render_voxel_humanoid(
            surface, camera, self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y, self.state, self.state_timer,
            self.is_alive, char_type="chiyo", walk_timer=self.walk_cycle,
            alpha=self.alpha, is_moving=self.is_moving
        )
