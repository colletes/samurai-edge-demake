"""
Goro (O Fazendeiro da Kuwa - Ciclo 3):
Camponês e líder rebelde da era Bakumatsu.
- Arquétipo: Lutador pesado e resistente (velocidade 4.2, 2 HP).
- Guarda de Ferro (Parry técnico com o cabo maciço e a lâmina de ferro forjado).
- Ataque Primário: Descida da Kuwa (KUWA_CLEAVE) - golpe vertical devastador no solo (alcance 1.85m, raio 1.05m).
- Ação Secundária: Pisotão Sísmico (EARTH_STOMP) - onda de choque circular que racha o solo, empurra rivais e inflige STUN (0.80s). Cooldown 4.5s.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_GORO_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, STATE_PARRY, resolve_playable_bounds
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import EarthStompShockwave
from src.effects.particles import SparkParticle, FloatingBanner

STATE_EARTH_STOMP = "EARTH_STOMP"


class GoroFarmer(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Goro")
        self.char_type = "goro"
        self.speed = 4.6  # Movimentação ágil e firme
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Ataque Primário: Descida da Kuwa (Corte Vertical de Enxada)
        self.cleave_duration = 0.18  # Execução rápida e impetuosa (era 0.24s)
        self.cleave_recovery = 0.18  # Recovery reduzido para punição justa sem travamento excessivo
        self.cleave_reach = 2.20
        self.cleave_radius = 1.35
        self.cleave_timer = 0.0

        # Ação Secundária: Pisotão Sísmico
        self.stomp_cooldown = 1.6    # Cooldown reduzido (era 2.4s) para controle de solo dinâmico
        self.stomp_timer = 0.0
        self.stomp_duration = 0.20
        self.active_shockwaves: list[EarthStompShockwave] = []

        # Esquiva firme de camponês
        self.is_agile_dodge = False
        self.roll_speed = 8.4
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.18
        self.roll_cooldown_duration = 0.38
        self.recovery_duration = self.cleave_recovery

    def trigger_parry(self) -> bool:
        """Guarda de Ferro: ergue a Kuwa e o cabo reforçado para aparar golpes e flechas."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.40
        return True

    def take_hit(self, slash_dir: tuple[float, float], damage: int = 2) -> tuple[bool, bool]:
        """Aplica dano ao Goro com Hyper Armor durante o cleave contra ataques leves."""
        if not self.is_alive:
            return False, False
        # Hyper Armor na execução do Cleave da Kuwa: golpes leves (dano 1) não cancelam o ataque se tiver HP > 1
        if self.state == STATE_ATTACK and damage < 2 and self.hp > 1:
            self.hp -= damage
            return True, False
        return super().take_hit(slash_dir, damage)

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_kuwa_cleave(self, aim_x: float, aim_y: float) -> bool:
        """Ataque Primário: Golpe descendente brutal com a Kuwa de aço."""
        if not self.can_act():
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.cleave_duration
        self.hitbox_active = True
        self.hitbox_damage = 2

        # Centro da hitbox à frente
        self.hitbox_center = (
            self.wx + self.facing_x * 1.15,
            self.wy + self.facing_y * 1.15
        )
        self.hitbox_radius = self.cleave_radius
        self.slash_dir = (self.facing_x, self.facing_y)
        return True

    def trigger_earth_stomp(self, aim_x: float = None, aim_y: float = None, shockwaves: list = None, particles: list = None, banners: list = None) -> bool:
        """Ação Secundária: Pisotão Sísmico. Racha o solo, gera onda expansiva e atordoa."""
        if not self.can_act() or self.stomp_timer > 0:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)
        self.state = STATE_EARTH_STOMP
        self.state_timer = self.stomp_duration
        self.stomp_timer = self.stomp_cooldown
        self.hitbox_active = False

        # Criar onda de choque sísmica frontal em 120 graus (alcance 4.2m, rápida, com 1 de dano e anula projéteis)
        wave = EarthStompShockwave(self.wx, self.wy, owner=self, facing=(self.facing_x, self.facing_y), max_radius=4.2, duration=0.30)
        if shockwaves is not None:
            shockwaves.append(wave)
        self.active_shockwaves.append(wave)

        if particles is not None:
            for _ in range(12):
                particles.append(SparkParticle(self.wx, self.wy, 0.35, color=(165, 130, 85)))

        if banners is not None:
            banners.append(FloatingBanner("EARTH STOMP!", self.wx, self.wy, color=COLOR_GOLD, duration=0.85))

        return True

    def update(self, dt: float, game_map = None, particles: list = None, opponent = None, projectiles: list = None, **kwargs):
        # Atualizar timers de esquiva e recuperação de roll
        self.update_dodge_timers(dt)

        # Atualizar cooldown do pisotão sísmico
        if self.stomp_timer > 0:
            self.stomp_timer = max(0.0, self.stomp_timer - dt)

        # Atualizar rolamento se em estado ROLL
        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            return

        # Atualizar estado de atordoamento (STUNNED)
        if self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # Atualizar ataque primário (Kuwa Cleave)
        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Avanço de peso corporal no golpe da enxada
            step_speed = 2.4
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map and hasattr(game_map, "cols"):
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.15,
                self.wy + self.facing_y * 1.15
            )
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.cleave_recovery
                self.hitbox_active = False
            return

        # Atualizar estado específico do pisotão sísmico
        if self.state == STATE_EARTH_STOMP:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.10
            return

        # Atualizar estado de recuperação
        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # Atualizar estado de guarda / parry
        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # Atualizar ondas ativas de Goro
        if self.active_shockwaves:
            fighters = [self]
            if opponent:
                fighters.append(opponent)
            self.active_shockwaves = [
                w for w in self.active_shockwaves
                if w.update(dt, game_map=game_map, particles=particles, fighters=fighters, projectiles=projectiles)
            ]

    def render(self, surface: pygame.Surface, camera):
        extra = {}
        if self.state == STATE_EARTH_STOMP:
            extra = {"is_stomp": True, "pose": "earth_stomp"}
        elif self.state in ("DEFEND", "PARRY") or getattr(self, "is_parrying", False):
            extra = {"pose": "iron_guard"}

        atk_prog = 0.0
        if self.state == STATE_ATTACK:
            dur = self.cleave_duration if self.cleave_duration > 0 else 0.26
            atk_prog = 1.0 - max(0.0, self.state_timer / dur)

        render_voxel_humanoid(
            surface=surface,
            camera=camera,
            wx=self.wx,
            wy=self.wy,
            wz=getattr(self, "wz", 0.0),
            facing_x=self.facing_x,
            facing_y=self.facing_y,
            state=self.state,
            state_timer=self.state_timer,
            is_alive=self.is_alive,
            char_type="goro",
            walk_timer=getattr(self, "walk_cycle", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
