"""
Ninja Roxo (Murasaki): Especialista em Kusarigama (foice curta com corrente e peso de ferro).
Possui ataque especial que puxa o adversário para perto com a corrente, e golpe padrão de foice
de alcance bem curto mas com PRECEDÊNCIA ABSOLUTA sobre qualquer outro ataque.
"""
import math
import pygame
from src.config import (
    COLOR_PURPLE_NINJA, COLOR_PURPLE_DARK, COLOR_PURPLE_AURA, COLOR_CHAIN,
    COLOR_WHITE, COLOR_BLACK, COLOR_GOLD, COLOR_STEEL
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import KusarigamaChainEntity
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric.hd2d_renderer import HD2DSpriteRenderer

class PurpleNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Murasaki")
        self.char_type = "murasaki"
        self.speed = 4.6

        # Ataque Curto de Foice (Kama Strike) com Precedência Absoluta
        self.is_priority_strike = False
        self.kama_cooldown = 0.45
        self.kama_timer = 0.0

        # Ataque Especial: Kusarigama Chain Grapple / Pull
        self.chain_cooldown = 2.0
        self.chain_timer = 0.0

        # Timers da animação de ataque
        self.windup_time = 0.07
        self.active_time = 0.14
        self.recovery_time = 0.28

    def trigger_kama_strike(self, target_wx: float, target_wy: float):
        """
        Ataque Primário: Golpe rápido de foice de alcance bem curto (0.7m),
        mas com PRECEDÊNCIA ABSOLUTA sobre qualquer outro ataque.
        """
        if not self.can_move() or self.kama_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.0
        self.kama_timer = self.kama_cooldown
        self.is_priority_strike = True

        # Avanço súbito à queima-roupa
        self.vx = self.facing_x * 4.5
        self.vy = self.facing_y * 4.5

        # Hitbox curta calibrada
        self.hitbox_active = False
        self.hitbox_center = (self.wx + self.facing_x * 0.70, self.wy + self.facing_y * 0.70)
        self.hitbox_radius = 0.90  # Alcance ampliado para 0.90 para consistência tática

    def trigger_kusarigama_pull(self, target_wx: float, target_wy: float, projectiles: list):
        """
        Ataque Secundário / Especial: Arremessa a corrente com peso de ferro para engatar
        e puxar o adversário para perto. O adversário permanece livre para agir/atacar.
        """
        if not self.can_move() or self.chain_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.chain_timer = self.chain_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.18

        # Spawn da corrente saindo das mãos
        chain = KusarigamaChainEntity(
            wx=self.wx + self.facing_x * 0.35,
            wy=self.wy + self.facing_y * 0.35,
            wz=0.4,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self
        )
        projectiles.append(chain)

    def update(self, dt: float, game_map):
        if not self.is_alive:
            self.hitbox_active = False
            self.is_priority_strike = False
            return

        self.update_stealth(game_map)

        if self.kama_timer > 0:
            self.kama_timer -= dt
        if self.chain_timer > 0:
            self.chain_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer += dt
            # Fase 1: Windup curto
            if self.state_timer < self.windup_time:
                self.hitbox_active = False
            # Fase 2: Lâmina ativa com precedência
            elif self.state_timer < (self.windup_time + self.active_time):
                self.hitbox_active = True
                self.is_priority_strike = True
                self.hitbox_center = (self.wx + self.facing_x * 0.65, self.wy + self.facing_y * 0.65)
            # Fase 3: Recovery
            elif self.state_timer < (self.windup_time + self.active_time + self.recovery_time):
                self.hitbox_active = False
                self.is_priority_strike = False
            else:
                self.state = STATE_IDLE
                self.hitbox_active = False
                self.is_priority_strike = False

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.hitbox_active = False
            self.is_priority_strike = False
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza Murasaki em Sprite HD-2D ou no estilo Voxel 3D fallback."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        hd2d_rendered = HD2DSpriteRenderer.render_fighter(
            surface, camera, self, "murasaki", alpha=self.alpha
        )
        if not hd2d_rendered:
            render_voxel_humanoid(
                surface, camera,
                self.wx, self.wy, self.wz,
                self.facing_x, self.facing_y,
                self.state, self.state_timer, self.is_alive,
                char_type="purple",
                walk_timer=self.walk_cycle,
                alpha=self.alpha,
                is_moving=self.is_moving
            )
