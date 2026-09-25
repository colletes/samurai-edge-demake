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
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle

class PirateSwordswoman(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Anne")
        self.char_type = "pirate"
        self.speed = 4.9  # Velocidade ágil e agressiva de bucaneira (era 4.3)

        # Mecânica do Alfanje (Corte Amplo em Meia-Lua)
        self.cleave_cooldown = 0.40
        self.cleave_timer = 0.0

        # Truque Sujo: Pólvora nos Olhos & Recuo
        self.powder_cooldown = 2.0
        self.powder_timer = 0.0

    def can_act(self) -> bool:
        return self.is_alive and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD)

    def trigger_cutlass_cleave(self, target_wx: float, target_wy: float):
        """Ataque Primário: Golpe horizontal em meia-lua de 180° com o alfanje e avanço frontal."""
        if not self.can_act() or self.cleave_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.24
        self.hitbox_active = True
        self.hitbox_radius = 1.40
        self.slash_dir = (self.facing_x, self.facing_y)
        # Avanço frontal inicial com o corte
        self.wx += self.facing_x * 0.40
        self.wy += self.facing_y * 0.40
        self.hitbox_center = (self.wx + self.facing_x * 0.75, self.wy + self.facing_y * 0.75)
        self.cleave_timer = self.cleave_cooldown

    def trigger_gunpowder_blind(self, target_wx: float = None, target_wy: float = None, opponent = None, particles: list = None):
        """Ação Secundária: Lança pó de pólvora abrasivo nos olhos do rival a curta distância (Stun + Slow 1.5s)."""
        if not self.can_act() or self.powder_timer > 0:
            return

        if target_wx is not None and target_wy is not None:
            self.set_facing(target_wx, target_wy)
        self.powder_timer = self.powder_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.16

        # Nuvem de pólvora à queima-roupa
        cloud_x = self.wx + self.facing_x * 0.9
        cloud_y = self.wy + self.facing_y * 0.9

        # Avanço frontal agressivo da pirata em direção ao alvo cego
        self.wx += self.facing_x * 0.60
        self.wy += self.facing_y * 0.60

        # Se o oponente estiver perto, fica atordoado e lento pela pólvora abrasiva nos olhos!
        if opponent is not None:
            from src.isometric.iso_math import world_distance
            if world_distance(self.wx, self.wy, opponent.wx, opponent.wy) < 3.0:
                if hasattr(opponent, "stun"):
                    opponent.stun(0.60)
                if hasattr(opponent, "apply_slow"):
                    opponent.apply_slow(1.5)

        if particles is not None:
            for _ in range(16):
                particles.append(SparkParticle(cloud_x, cloud_y, 0.45))

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.cleave_timer > 0:
            self.cleave_timer -= dt
        if self.powder_timer > 0:
            self.powder_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Avanço com o corte do alfanje
            step = 5.0 * dt
            self.wx = max(1.0, min(game_map.cols - 1.0, self.wx + self.facing_x * step))
            self.wy = max(1.0, min(game_map.rows - 1.0, self.wy + self.facing_y * step))
            self.hitbox_center = (self.wx + self.facing_x * 0.75, self.wy + self.facing_y * 0.75)

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.08  # Recuperação ultrarrápida do alfanje
                self.hitbox_active = False

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
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
