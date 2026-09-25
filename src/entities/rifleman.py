"""
Rifleman (Tanegashima): Mestre atirador armado com arcabuz feudal de mecha.
Tiro fatal de longo alcance (1-Hit Kill). Requer dosar a pólvora e socar a munição
segurando a ação secundária, com salto evasivo de fumaça para reposicionamento.
"""
import math
import random
import pygame
from src.config import (
    COLOR_RIFLE_COAT, COLOR_RIFLE_HAT, COLOR_RIFLE_AURA, COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import MusketBulletProjectile
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle

STATE_BACKSTEP = "BACKSTEP"

class Rifleman(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Teppo")
        self.char_type = "teppo"
        self.speed = 4.3  # Velocidade ágil para caçar pólvora na arena

        # Mecânica de Munição e Pólvora
        self.has_ammo = True           # Inicia CARREGADO com munição
        self.cocking_timer = 0.0
        self.reload_time = 0.0
        self.is_reloading = False
        self.reload_progress = 0.0

        # Subterfúgio Evasivo
        self.backstep_cooldown = 0.60   # Calibrado: reposicionamento ágil
        self.backstep_timer = 0.0
        self.backstep_duration = 0.20

    def check_powder_pickup(self, pouches: list, particles: list = None) -> bool:
        """Verifica se Teppo passou por cima de um saquinho de pólvora para carregar o arcabuz."""
        if self.has_ammo or not self.is_alive:
            return False
        for pouch in pouches:
            if getattr(pouch, "is_active", False):
                if math.hypot(self.wx - pouch.wx, self.wy - pouch.wy) < (pouch.radius + self.radius + 0.25):
                    pouch.is_active = False
                    pouch.respawn_timer = 4.0
                    self.has_ammo = True
                    self.cocking_timer = 0.40
                    if particles is not None:
                        for _ in range(14):
                            particles.append(SparkParticle(self.wx, self.wy, 0.6))
                    return True
        return False

    def can_act(self) -> bool:
        return self.is_alive and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD)

    def trigger_shoot(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None):
        """Ataque Primário: Disparo fatal de arcabuz se tiver munição e engatilhado, ou coronhada defensiva se descarregado."""
        if not self.can_act():
            return

        if not self.has_ammo or self.cocking_timer > 0:
            # Se descarregado, desfere coronhada tática; se ainda engatilhando, aguarda
            if not self.has_ammo:
                self.trigger_rifle_butt(target_wx, target_wy, particles)
            return

        self.set_facing(target_wx, target_wy)
        self.has_ammo = False
        self.is_reloading = False
        self.reload_progress = 0.0

        self.state = STATE_RECOVERY
        self.state_timer = 0.38

        # Recuo da pólvora
        self.wx -= self.facing_x * 0.4
        self.wy -= self.facing_y * 0.4

        # Criar projétil
        bx = self.wx + self.facing_x * 0.65
        by = self.wy + self.facing_y * 0.65
        bullet = MusketBulletProjectile(bx, by, wz=0.55, dir_x=self.facing_x, dir_y=self.facing_y, owner=self)
        projectiles.append(bullet)

        if particles is not None:
            for _ in range(14):
                particles.append(SparkParticle(bx, by, 0.55))

    def trigger_rifle_butt(self, target_wx: float, target_wy: float, particles: list = None):
        """Coronhada Defensiva: Golpe de madeira de curto alcance que atordoa e afasta o adversário."""
        if not self.can_act():
            return
        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.20
        self.hitbox_active = True
        self.hitbox_radius = 1.15
        self.is_rifle_butt = True
        self.hitbox_center = (self.wx + self.facing_x * 0.75, self.wy + self.facing_y * 0.75)
        self.slash_dir = (self.facing_x, self.facing_y)
        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.3))

    def trigger_reload_hold(self):
        """Ativado enquanto o jogador mantém pressionado o botão de ação secundária."""
        if not self.can_act() or self.has_ammo:
            return
        self.is_reloading = True

    def trigger_evasive_backstep(self, particles: list = None):
        """Subterfúgio: Salto tático para trás com fumaça sem cancelar a recarga."""
        if not self.is_alive or self.backstep_timer > 0:
            return

        self.backstep_timer = self.backstep_cooldown
        self.state = STATE_BACKSTEP
        self.state_timer = self.backstep_duration

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.3))

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.backstep_timer > 0:
            self.backstep_timer -= dt

        if self.cocking_timer > 0:
            self.cocking_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.hitbox_active = False
                self.is_rifle_butt = False

        elif self.state == STATE_BACKSTEP:
            self.state_timer -= dt
            # Recuo evasivo na direção oposta ao olhar
            step = 7.5 * dt
            new_wx = self.wx - self.facing_x * step
            new_wy = self.wy - self.facing_y * step

            hit_col = False
            for r in game_map.rocks:
                if r.check_collision(new_wx, new_wy, self.radius)[0]:
                    hit_col = True; break
            if game_map.well and game_map.well.check_collision(new_wx, new_wy, self.radius)[0]:
                hit_col = True

            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Rifleman e indicador de munição/pólvora."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="rifleman",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props={"has_ammo": self.has_ammo, "is_reloading": False}
        )

        # Indicador de Munição na cabeça do Teppo
        bx, by = camera.apply(self.wx, self.wy, 1.45)
        if self.has_ammo:
            # Bala de chumbo dourada carregada
            pygame.draw.circle(surface, COLOR_GOLD, (bx, by), 5)
            pygame.draw.circle(surface, (255, 255, 200), (bx - 1, by - 1), 2)
        else:
            # Silhueta vazia cinza/vermelha indicando necessidade de coletar pólvora
            pygame.draw.circle(surface, (140, 50, 50), (bx, by), 4, 1)
