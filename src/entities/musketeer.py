"""
Julie (A Mosqueteira de Florete):
Duelista de esgrima clássica capa e espada. Rápida e elegante com a lâmina
fina do florete (Fleche Thrust) e riposte defensivo de capa com tiro de pederneira (Flintlock).
"""
import math
import random
import pygame
from src.config import (
    COLOR_MUSKETEER_BLUE, COLOR_MUSKETEER_HAT, COLOR_MUSKETEER_AURA, COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_PARRY, STATE_ROLL
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import MusketBulletProjectile
from src.effects.particles import SparkParticle

class Musketeer(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Julie")
        self.char_type = "musketeer"
        self.speed = 4.4

        # Ataque Primário: Fleche Thrust (+25% alcance, bote linear cirúrgico de esgrima)
        self.thrust_cooldown = 0.48
        self.thrust_timer = 0.0

        # Ação Secundária: Floreio de Capa com Chute de Repulsão (Cape Flourish & Deflection)
        self.cape_cooldown = 2.4
        self.cape_timer = 0.0

        # Arma Secundária de Bolso: Pistola Pederneira (Pocket Flintlock)
        self.flintlock_cooldown = 4.5
        self.flintlock_timer = 1.0  # Inicia com 1.0s no round para evitar tiro instantâneo no spawn

    def can_act(self) -> bool:
        return self.is_alive and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, "CAPE_FLOURISH") and self.dash_recovery_timer <= 0

    def trigger_fleche_thrust(self, target_wx: float, target_wy: float):
        """
        Ataque Primário: Fleche Thrust.
        Estocada de florete linear com +25% de alcance e hitbox refinada (0.70m).
        """
        if not self.can_act() or self.thrust_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.20
        self.hitbox_active = True
        self.hitbox_radius = 0.70  # Calibrada para evitar errar esquivas diagonais
        self.slash_dir = (self.facing_x, self.facing_y)
        # Alcance estendido à frente
        self.hitbox_center = (self.wx + self.facing_x * 1.30, self.wy + self.facing_y * 1.30)
        self.thrust_timer = self.thrust_cooldown

    def trigger_flintlock_shot(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None):
        """
        Disparo de Pederneira de Bolso (Pocket Flintlock):
        Disparo veloz à média/longa distância para conter zhoners e punir aproximações descuidadas.
        """
        if not self.can_act() or self.flintlock_timer > 0 or projectiles is None:
            return

        self.set_facing(target_wx, target_wy)
        self.flintlock_timer = self.flintlock_cooldown

        dx = target_wx - self.wx
        dy = target_wy - self.wy
        length = math.hypot(dx, dy)
        if length > 0.001:
            dir_x = dx / length
            dir_y = dy / length
        else:
            dir_x, dir_y = self.facing_x, self.facing_y

        # Cria projétil supersônico de pederneira
        projectiles.append(MusketBulletProjectile(self.wx, self.wy, 0.45, dir_x, dir_y, owner=self))

        # Recuo sutil do tiro de pederneira
        self.wx -= dir_x * 0.25
        self.wy -= dir_y * 0.25

        if particles is not None:
            for _ in range(16):
                particles.append(SparkParticle(self.wx + dir_x * 0.5, self.wy + dir_y * 0.5, 0.45, color=(255, 210, 100)))

    def trigger_cape_flourish(self, target_wx: float = None, target_wy: float = None, opponent = None, particles: list = None, banners: list = None, projectiles: list = None):
        """
        Ação Secundária: Cape Flourish & Coup de Pied.
        Giro teatral da capa de veludo azul que repele rivais a curta distância e deflete projéteis frontais.
        Se o oponente estiver à média/longa distância (> 2.8m), utiliza a pistola pederneira caso disponível.
        """
        if not self.can_act():
            return

        # Se houver mira à distância e pederneira pronta: atira de pederneira!
        if target_wx is not None and target_wy is not None and projectiles is not None:
            dist_aim = math.hypot(target_wx - self.wx, target_wy - self.wy)
            if dist_aim >= 2.8 and self.flintlock_timer <= 0:
                self.trigger_flintlock_shot(target_wx, target_wy, projectiles, particles)
                return

        if self.cape_timer > 0:
            return

        if target_wx is not None and target_wy is not None:
            self.set_facing(target_wx, target_wy)

        self.cape_timer = self.cape_cooldown
        self.state = "CAPE_FLOURISH"
        self.state_timer = 0.25
        self.hitbox_active = False

        # Partículas de tecido azul da capa esvoaçante
        if particles is not None:
            for i in range(14):
                angle = (i / 14.0) * math.pi * 2
                px = self.wx + math.cos(angle) * 0.70
                py = self.wy + math.sin(angle) * 0.70
                particles.append(SparkParticle(px, py, 0.4, color=(100, 175, 255)))

        # Efeito de repulsão física e stagger no oponente a curta distância (< 1.85m)
        if opponent is not None and getattr(opponent, "is_alive", False):
            dist = math.hypot(self.wx - opponent.wx, self.wy - opponent.wy)
            if dist < 1.85:
                if hasattr(opponent, "stun"):
                    opponent.stun(0.40)  # Stagger de 0.40s
                # Knockback de ~2 metros na direção frontal
                opponent.wx += self.facing_x * 1.85
                opponent.wy += self.facing_y * 1.85
                if banners is not None:
                    from src.effects.particles import FloatingBanner
                    banners.append(FloatingBanner("COUP DE PIED! REPEL!", opponent.wx, opponent.wy, wz=1.75, color=(100, 175, 255)))

    def trigger_cloak_riposte(self, target_wx: float = None, target_wy: float = None, projectiles: list = None, particles: list = None, opponent = None, banners: list = None):
        """Compatibilidade para chamadas legadas: redireciona para o floreio de capa ou tiro de pederneira."""
        self.trigger_cape_flourish(target_wx, target_wy, opponent=opponent, particles=particles, banners=banners, projectiles=projectiles)

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.thrust_timer > 0:
            self.thrust_timer -= dt
        if self.cape_timer > 0:
            self.cape_timer -= dt
        if self.flintlock_timer > 0:
            self.flintlock_timer -= dt
        if self.dash_recovery_timer > 0:
            self.dash_recovery_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Bote linear veloz de fleche
            step = 7.5 * dt
            self.wx = max(1.0, min(game_map.cols - 1.0, self.wx + self.facing_x * step))
            self.wy = max(1.0, min(game_map.rows - 1.0, self.wy + self.facing_y * step))
            self.hitbox_center = (self.wx + self.facing_x * 1.30, self.wy + self.facing_y * 1.30)

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.18  # Recovery reduzido (era 0.28s) para punição justa sem paralisia letal
                self.hitbox_active = False

        elif self.state == "CAPE_FLOURISH":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_ROLL:
            self.update_roll(dt, game_map)

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
            char_type="musketeer",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving
        )
