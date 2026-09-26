"""
Ninja Cinza (Kemuri): Mestre em explosivos com delay e bombas de fumaça com slow para fuga.
"""
import math
import pygame
from src.config import (
    COLOR_GRAY_NINJA, COLOR_GRAY_DARK, COLOR_SMOKE, COLOR_WHITE, COLOR_BLACK, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_ROLL
)
from src.entities.projectile import TimedBombEntity, SmokeCloudEntity, RemoteMineEntity
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle

class GrayNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Kasumi")
        self.char_type = "kasumi"
        self.speed = 4.8
        self.bomb_cooldown = 0.50
        self.bomb_timer = 0.0
        self.smoke_cooldown = 2.0
        self.smoke_timer = 0.0
        self.mine_cooldown = 2.2
        self.mine_timer = 0.0
        self.planted_mine = None

    def can_act(self) -> bool:
        return self.is_alive and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD) and self.dash_recovery_timer <= 0

    def trigger_throw_bomb(self, target_wx: float, target_wy: float, projectiles: list):
        """Ataque Primário: Arremessa bomba em arco 3D (até 2 ativas). Detona por contato ou tempo."""
        if not self.can_act() or self.bomb_timer > 0:
            return

        active_bombs = sum(1 for p in projectiles if isinstance(p, TimedBombEntity) and p.owner == self and p.is_active)
        if active_bombs >= 2:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_RECOVERY
        self.state_timer = 0.12
        self.bomb_timer = self.bomb_cooldown

        dx = target_wx - self.wx
        dy = target_wy - self.wy
        dist = math.hypot(dx, dy)
        dir_x = dx / dist if dist > 0.001 else self.facing_x
        dir_y = dy / dist if dist > 0.001 else self.facing_y

        bomb = TimedBombEntity(wx=self.wx + dir_x * 0.40, wy=self.wy + dir_y * 0.40, wz=0.75, dir_x=dir_x, dir_y=dir_y, owner=self)
        projectiles.append(bomb)

    def trigger_remote_mine(self, target_wx: float = 0.0, target_wy: float = 0.0, projectiles: list = None, fighters: list = None, particles: list = None, banners: list = None, cinematic_director = None):
        """
        Ação Secundária: Mina de Detonação Remota (Item 16).
        1º toque: Planta a mina no solo.
        2º toque: Detona remotamente se armada (delay 0.4s). Dano atinge também Kasumi se estiver no raio.
        """
        # Se já existe mina plantada e ativa, tenta detonar!
        if self.planted_mine and getattr(self.planted_mine, "is_active", False):
            if self.planted_mine.is_ready_to_detonate():
                flist = fighters if fighters is not None else [self]
                self.planted_mine.detonate(flist, particles=particles, banners=banners, cinematic_director=cinematic_director)
                self.planted_mine = None
                self.mine_timer = self.mine_cooldown
            return

        # Senão, planta a mina no solo!
        if not self.can_act() or self.mine_timer > 0:
            return

        self.state = STATE_RECOVERY
        self.state_timer = 0.12
        proj_list = projectiles if projectiles is not None else getattr(self, "projectiles_ref", None)

        mine = RemoteMineEntity(self.wx, self.wy, owner=self)
        self.planted_mine = mine
        if proj_list is not None:
            proj_list.append(mine)

        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(self.wx, self.wy, 0.25))

    def trigger_smoke_bomb(self, target_wx: float, target_wy: float, projectiles: list, fighters: list = None, particles: list = None, banners: list = None, cinematic_director = None):
        """Compatibilidade: redireciona para a Mina Remota."""
        self.trigger_remote_mine(target_wx, target_wy, projectiles, fighters=fighters, particles=particles, banners=banners, cinematic_director=cinematic_director)

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None):
        """Dash Furtivo: Cortina de fumaça instantânea, transparência (alpha=50) e imunidade a projéteis (Item 16)."""
        if not self.is_alive or self.state in (STATE_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK) or self.dash_recovery_timer > 0:
            return

        super().trigger_roll(dir_x, dir_y, particles)
        self.alpha = 50  # Quase invisível durante o percurso!

        if particles is not None:
            for _ in range(12):
                particles.append(SparkParticle(self.wx, self.wy, 0.4))

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.bomb_timer > 0:
            self.bomb_timer -= dt
        if self.smoke_timer > 0:
            self.smoke_timer -= dt
        if self.mine_timer > 0:
            self.mine_timer -= dt
        if self.dash_recovery_timer > 0:
            self.dash_recovery_timer -= dt

        # Recuperação gradual de transparência quando fora do roll e de bambu
        if self.state != STATE_ROLL and not self.is_hidden and self.alpha < 255:
            self.alpha = min(255, self.alpha + int(400 * dt))

        if self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_ROLL:
            self.update_roll(dt, game_map)
            if self.state == STATE_IDLE:
                self.dash_recovery_timer = self.dash_recovery_duration

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Ninja Cinza no autêntico estilo Voxel 3D Isométrico."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="gray",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving
        )
