"""
Daiki (O Peregrino do Bastão Bō - Ciclo 5):
Monge andarilho Yamabushi / Komusō das montanhas de pinheiros sagrados.
- Arquétipo: Especialista de longo alcance, espaçamento e mobilidade aérea (velocidade 4.75, 2 HP).
- Guarda Giratória (Parry técnico girando o bastão de carvalho de 6 shaku / 1.82m).
- Ataque Primário: Estocada & Giro de Bastão Bō (BO_STRIKE) - golpe longo de duas mãos com ponteiras de ferro (alcance 2.65m, raio 1.25m).
- Ação Secundária: Salto com Vara / Impacto Meteoro (POLE_VAULT) - apoia o bastão no solo para saltar sobre ataques rasteiros e armadilhas (wz até 1.35m) e desce esmagando a guarda frontal com impacto letal. Cooldown 3.6s.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_DAIKI_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, STATE_PARRY, resolve_playable_bounds
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle, SmokeParticle, FloatingBanner

STATE_POLE_VAULT = "POLE_VAULT"


class DaikiPilgrim(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Daiki")
        self.char_type = "daiki"
        self.speed = 4.75
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Ataque Primário: Estocada & Varredura de Bastão Bō (Longo Alcance)
        self.bo_duration = 0.17
        self.bo_recovery = 0.18
        self.bo_reach = 2.65
        self.bo_radius = 1.25

        # Ação Secundária: Salto com Vara / Impacto Meteoro (Pole Vault)
        self.vault_cooldown = 3.6
        self.vault_timer = 0.0
        self.vault_duration = 0.36
        self.vault_speed = 9.5
        self.vault_dir_x = 1.0
        self.vault_dir_y = 0.0
        self.vault_slammed = False

        # Esquiva firme de peregrino da montanha
        self.is_agile_dodge = True
        self.roll_speed = 8.8
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.16
        self.roll_cooldown_duration = 0.36
        self.recovery_duration = self.bo_recovery

    def trigger_parry(self) -> bool:
        """Guarda Giratória com o Bastão Bō de carvalho e anéis de ferro."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.38
        return True

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_bo_strike(self, aim_x: float, aim_y: float) -> bool:
        """Ataque Primário: Estocada e giro longo com o Bastão Bō de 1.82m."""
        if not self.can_act():
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.bo_duration
        self.hitbox_active = True
        self.hitbox_damage = 2

        self.hitbox_center = (
            self.wx + self.facing_x * 1.45,
            self.wy + self.facing_y * 1.45
        )
        self.hitbox_radius = self.bo_radius
        self.slash_dir = (self.facing_x, self.facing_y)
        return True

    def trigger_pole_vault(self, aim_x: float = None, aim_y: float = None, particles: list = None, banners: list = None, opponent=None, game_map=None) -> bool:
        """
        Ação Secundária: Salto com Vara / Impacto Meteoro (Pole Vault).
        Impulsiona-se no bastão Bō sobre ataques rasteiros e desce com golpe vertical quebra-guarda.
        """
        if not self.can_act() or self.vault_timer > 0:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        self.vault_dir_x = self.facing_x
        self.vault_dir_y = self.facing_y
        self.state = STATE_POLE_VAULT
        self.state_timer = self.vault_duration
        self.vault_timer = self.vault_cooldown
        self.vault_slammed = False
        self.hitbox_active = False
        self.pit_cross_timer = self.vault_duration + 0.08

        if particles is not None:
            for _ in range(10):
                particles.append(SparkParticle(self.wx, self.wy, 0.25, color=(235, 195, 95)))

        if banners is not None:
            banners.append(FloatingBanner("POLE VAULT!", self.wx, self.wy, wz=1.65, color=COLOR_DAIKI_AURA, duration=0.80))

        return True

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None, **kwargs):
        self.update_dodge_timers(dt)

        if self.vault_timer > 0:
            self.vault_timer = max(0.0, self.vault_timer - dt)

        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            self.wz = 0.0
            return

        if self.state == STATE_STUNNED:
            self.wz = 0.0
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            step_speed = 2.6
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map is not None:
                min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                self.wx = max(min_x, min(max_x, new_wx))
                self.wy = max(min_y, min(max_y, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.45,
                self.wy + self.facing_y * 1.45
            )
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.bo_recovery
                self.hitbox_active = False
            return

        if self.state == STATE_POLE_VAULT:
            self.state_timer -= dt
            prog = 1.0 - max(0.0, self.state_timer / max(0.001, self.vault_duration))

            # Trajetória parabólica no eixo Z (atinge 1.35m no ápice, saltando sobre ataques baixos e armadilhas)
            self.wz = max(0.0, math.sin(prog * math.pi) * 1.35)

            # Avanço horizontal impulsionado pela vara
            new_wx = self.wx + self.vault_dir_x * self.vault_speed * dt
            new_wy = self.wy + self.vault_dir_y * self.vault_speed * dt
            if game_map is not None:
                min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                self.wx = max(min_x, min(max_x, new_wx))
                self.wy = max(min_y, min(max_y, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            # No início do salto (prog < 0.35), o giro do bastão desvia projéteis frontais próximos
            if prog < 0.35 and projectiles:
                for p in projectiles:
                    if getattr(p, "is_active", False) and getattr(p, "owner", None) is not self:
                        px, py = getattr(p, "wx", -999.0), getattr(p, "wy", -999.0)
                        if math.hypot(px - self.wx, py - self.wy) < 1.35 and hasattr(p, "vx"):
                            p.vx = -p.vx
                            p.vy = -p.vy
                            if hasattr(p, "dir_x"):
                                p.dir_x = -p.dir_x
                                p.dir_y = -p.dir_y
                            p.owner = self

            # Na descida final (prog >= 0.72), ativa o Impacto Meteoro quebra-guarda
            if prog >= 0.72 and not self.vault_slammed:
                self.vault_slammed = True
                self.hitbox_active = True
                self.hitbox_damage = 2
                self.hitbox_center = (
                    self.wx + self.facing_x * 1.15,
                    self.wy + self.facing_y * 1.15
                )
                self.hitbox_radius = 1.35
                self.slash_dir = (self.facing_x, self.facing_y)
                # Quebra a guarda frontal (STATE_PARRY) do oponente se estiver na área de impacto
                if opponent and getattr(opponent, "is_alive", False) and getattr(opponent, "state", "") == STATE_PARRY:
                    dist_opp = math.hypot(opponent.wx - self.hitbox_center[0], opponent.wy - self.hitbox_center[1])
                    if dist_opp <= self.hitbox_radius + getattr(opponent, "radius", 0.35):
                        opponent.stun(0.55)
                        if banners is not None:
                            banners.append(FloatingBanner("GUARD CRUSH!", opponent.wx, opponent.wy, wz=1.7, color=(255, 160, 50)))

                if particles is not None:
                    for _ in range(14):
                        particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.20, color=(235, 185, 90)))
            elif prog >= 0.72:
                self.hitbox_center = (
                    self.wx + self.facing_x * 1.15,
                    self.wy + self.facing_y * 1.15
                )

            if self.state_timer <= 0:
                self.wz = 0.0
                self.hitbox_active = False
                self.state = STATE_RECOVERY
                self.state_timer = 0.18
            return

        elif self.state == STATE_RECOVERY:
            self.wz = 0.0
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        elif self.state == STATE_PARRY:
            self.wz = 0.0
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

    def render(self, surface: pygame.Surface, camera):
        extra = {}
        if self.state == STATE_POLE_VAULT:
            extra = {"pose": "pole_vault", "is_vaulting": True}
        elif self.state in ("DEFEND", "PARRY") or getattr(self, "is_parrying", False):
            extra = {"pose": "bo_spin_guard"}

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
            char_type="daiki",
            walk_timer=getattr(self, "walk_cycle", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
