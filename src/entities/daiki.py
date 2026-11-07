"""
Daiki (O Peregrino do Bastão Bō - Ciclo 5):
Monge andarilho Yamabushi / Komusō das montanhas de pinheiros sagrados.
- Arquétipo: Especialista de longo alcance, espaçamento e mobilidade aérea acrobática.
- Guarda Giratória (Parry técnico girando o bastão de carvalho de 6 shaku / 1.82m).
- Ataque Primário: Varredura Helicoidal de 180° com Bastão Bō (Six-Shaku Bo Staff Sweep) - alcance longo 2.40m, raio 1.35m com cadência anti-spam.
- Ação Secundária: Salto com Vara / Impacto Meteoro (POLE_VAULT) - impulsiona-se no bastão sobre ataques baixos e obstáculos (wz até 2.2m) e desce com rotação mortal do bastão quebrando a guarda frontal (2 HP de dano). Cooldown 4.2s.
- Terceira Ação: Salto com Apoio de Bastão (Staff Vault Hop) - salto ágil acrobático com 13 i-frames completos, cruzando buracos estreitos.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_DAIKI_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, STATE_PARRY, resolve_playable_bounds,
    slide_movement_against_obstacles
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle, SmokeParticle, FloatingBanner

STATE_POLE_VAULT = "POLE_VAULT"
STATE_STAFF_HOP = "STAFF_HOP"


class DaikiPilgrim(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Daiki")
        self.char_type = "daiki"
        self.speed = 4.65  # Velocidade ágil de peregrino montanhês
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Ataque Primário: Varredura Helicoidal de 180° & Estocada (Longo Alcance, Anti-Spam)
        self.bo_duration = 0.22
        self.bo_recovery = 0.26        # Recovery balanceado eliminando vulnerabilidade prolongada
        self.bo_cooldown = 0.42        # Anti-spam estrito entre ataques consecutivos
        self.bo_cooldown_timer = 0.0
        self.bo_reach = 2.40           # Alcance longo condizente com os 1.82m do bastão
        self.bo_radius = 1.35
        self.flourish_spin_active = False
        self.recovery_max_time = self.bo_recovery

        # Ação Secundária: Salto com Vara / Impacto Meteoro (Pole Vault - 2 HP)
        self.vault_cooldown = 4.2      # Cooldown calibrado
        self.vault_timer = 0.0
        self.vault_duration = 0.42
        self.vault_speed = 9.2
        self.vault_dir_x = 1.0
        self.vault_dir_y = 0.0
        self.vault_slammed = False
        self.pole_vault_deflect_active = False

        # Terceira Ação: Salto Acrobático com Apoio no Bastão (Staff Vault Hop)
        self.is_agile_dodge = True
        self.staff_hop_duration = 0.24
        self.roll_speed = 8.8
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.16
        self.roll_cooldown_duration = 0.36
        self.recovery_duration = self.bo_recovery

        self.extra_props = {}
        self.action_name = "Bastão Bō"

    def trigger_parry(self) -> bool:
        """Guarda Giratória com o Bastão Bō de carvalho e anéis de ferro."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.38
        self.action_name = "Guarda Giratória"
        return True

    def on_parried(self, opponent=None, game_map=None, banners: list = None, particles: list = None):
        """Mitigação e aterrissagem física imediata ao ser aparado em salto ou golpe corpo a corpo."""
        self.hitbox_active = False
        self.wz = 0.0
        self.state = STATE_RECOVERY
        self.state_timer = self.bo_recovery * 1.25
        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.35, color=(235, 195, 95)))

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK)
            and self.bo_cooldown_timer <= 0
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_bo_strike(self, aim_x: float, aim_y: float, particles: list = None) -> bool:
        """Ataque Primário: Varredura helicoidal de 180° e estocada longa com o Bastão Bō de 1.82m."""
        if not self.can_act() or self.bo_cooldown_timer > 0:
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.bo_duration
        self.bo_cooldown_timer = self.bo_cooldown
        self.hitbox_active = True
        self.hitbox_damage = 2

        self.hitbox_center = (
            self.wx + self.facing_x * 1.35,
            self.wy + self.facing_y * 1.35
        )
        self.hitbox_radius = self.bo_radius
        self.slash_dir = (self.facing_x, self.facing_y)
        self.action_name = "Varredura de Bō"

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(
                    self.wx + self.facing_x * 0.8,
                    self.wy + self.facing_y * 0.8,
                    0.25,
                    color=(215, 185, 125)
                ))
        return True

    def trigger_attack(self, aim_x: float = None, aim_y: float = None, **kwargs) -> bool:
        """Compatibilidade com interface universal Samurai."""
        if aim_x is None or aim_y is None:
            aim_x = self.wx + self.facing_x * 2.0
            aim_y = self.wy + self.facing_y * 2.0
        return self.trigger_bo_strike(aim_x, aim_y, particles=kwargs.get("particles"))

    def trigger_pole_vault(self, aim_x: float = None, aim_y: float = None, particles: list = None, banners: list = None, opponent=None, game_map=None) -> bool:
        """
        Ação Secundária: Salto com Vara / Impacto Meteoro (Pole Vault).
        Impulsiona-se no bastão Bō sobre ataques rasteiros e desce com rotação vertical quebra-guarda (2 HP).
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
        self.pole_vault_deflect_active = True
        self.hitbox_active = False
        self.pit_cross_timer = self.vault_duration + 0.12
        self.action_name = "Salto com Vara"

        if particles is not None:
            for _ in range(12):
                particles.append(SparkParticle(self.wx, self.wy, 0.25, color=(235, 195, 95)))

        if banners is not None:
            banners.append(FloatingBanner("POLE VAULT!", self.wx, self.wy, wz=1.75, color=COLOR_DAIKI_AURA, duration=0.85))

        return True

    def trigger_staff_hop(self, dwx: float, dwy: float, particles: list = None, game_map=None) -> bool:
        """Terceira Ação: Salto Acrobático com apoio no Bastão Bō (13 i-frames, cruza buracos estreitos)."""
        if not self.is_alive or self.state in (STATE_ROLL, STATE_STAFF_HOP, STATE_STUNNED, STATE_DEAD, STATE_ATTACK, STATE_POLE_VAULT):
            return False
        if self.roll_cooldown_timer > 0 or self.roll_recovery_timer > 0:
            return False

        dist = math.hypot(dwx, dwy)
        if dist > 0.05:
            self.facing_x = dwx / dist
            self.facing_y = dwy / dist
        else:
            self.facing_x = -self.facing_x
            self.facing_y = -self.facing_y

        self.state = STATE_STAFF_HOP
        self.state_timer = self.staff_hop_duration
        self.is_invulnerable_dodge = True
        self.invulnerable = True
        self.hitbox_active = False
        self.pit_cross_timer = 0.28
        self.action_name = "Salto de Peregrino"

        if particles is not None:
            for _ in range(10):
                particles.append(SparkParticle(self.wx, self.wy, 0.30, color=(235, 195, 110)))
        return True

    def trigger_roll(self, dwx: float, dwy: float, particles: list = None, **kwargs) -> bool:
        """Compatibilidade com interface universal Samurai."""
        return self.trigger_staff_hop(dwx, dwy, particles=particles, game_map=kwargs.get("game_map"))

    def update_roll(self, dt: float, game_map=None, particles: list = None):
        """Atualiza a translação física e cronômetro do salto acrobático com bastão."""
        if self.state not in (STATE_ROLL, STATE_STAFF_HOP):
            return

        self.state_timer -= dt
        prog = 1.0 - max(0.0, self.state_timer / max(0.001, self.staff_hop_duration))
        # Arco sutil de salto acrobático
        self.wz = max(0.0, math.sin(prog * math.pi) * 0.45)

        step = self.roll_speed * dt
        dx = self.facing_x * step
        dy = self.facing_y * step
        new_wx, new_wy = slide_movement_against_obstacles(self.wx, self.wy, dx, dy, self.radius, game_map)
        self.wx, self.wy = new_wx, new_wy

        if self.state_timer <= 0:
            self.state = STATE_IDLE
            self.wz = 0.0
            self.is_invulnerable_dodge = False
            self.invulnerable = False
            self.roll_recovery_timer = self.roll_recovery_duration
            self.roll_cooldown_timer = self.roll_cooldown_duration
            self.dash_recovery_timer = self.roll_recovery_duration

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None, **kwargs):
        self.update_dodge_timers(dt)

        if self.bo_cooldown_timer > 0:
            self.bo_cooldown_timer = max(0.0, self.bo_cooldown_timer - dt)

        if self.vault_timer > 0:
            self.vault_timer = max(0.0, self.vault_timer - dt)

        if self.state not in (STATE_POLE_VAULT, "JUMP", STATE_STAFF_HOP) and self.wz > 0.0:
            self.wz = max(0.0, self.wz - 16.0 * dt)

        if self.state in (STATE_ROLL, STATE_STAFF_HOP):
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            self.wz = 0.0
            self.pole_vault_deflect_active = False
            return

        if self.state == STATE_STUNNED:
            self.wz = 0.0
            self.pole_vault_deflect_active = False
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            step_speed = 2.4
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
                self.recovery_max_time = self.bo_recovery
                self.flourish_spin_active = True
                self.hitbox_active = False
            return

        if self.state == STATE_POLE_VAULT:
            self.state_timer -= dt
            prog = 1.0 - max(0.0, self.state_timer / max(0.001, self.vault_duration))

            # Trajetória parabólica no eixo Z (atinge 2.2m no ápice, saltando sobre ataques baixos e armadilhas)
            self.wz = max(0.0, math.sin(prog * math.pi) * 2.20)

            # Avanço horizontal impulsionado pela alavanca do bastão
            new_wx = self.wx + self.vault_dir_x * self.vault_speed * dt
            new_wy = self.wy + self.vault_dir_y * self.vault_speed * dt
            if game_map is not None:
                min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                self.wx = max(min_x, min(max_x, new_wx))
                self.wy = max(min_y, min(max_y, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            # No impulso inicial (prog < 0.40), o giro veloz do bastão deflete projéteis frontais
            if prog < 0.40:
                self.pole_vault_deflect_active = True
            else:
                self.pole_vault_deflect_active = False

            # Na descida final com rotação do bastão (prog >= 0.65), desfere o Impacto Meteoro (2 HP) quebrando guarda
            if prog >= 0.65 and not self.vault_slammed:
                self.vault_slammed = True
                self.hitbox_active = True
                self.hitbox_damage = 2
                self.hitbox_center = (
                    self.wx + self.facing_x * 1.25,
                    self.wy + self.facing_y * 1.25
                )
                self.hitbox_radius = 1.45
                self.slash_dir = (self.facing_x, self.facing_y)

                # Quebra a guarda frontal (STATE_PARRY) do oponente se estiver na área de impacto
                if opponent and getattr(opponent, "is_alive", False) and getattr(opponent, "state", "") == STATE_PARRY:
                    dist_opp = math.hypot(opponent.wx - self.hitbox_center[0], opponent.wy - self.hitbox_center[1])
                    if dist_opp <= self.hitbox_radius + getattr(opponent, "radius", 0.35):
                        opponent.stun(0.65)
                        if banners is not None:
                            banners.append(FloatingBanner("GUARD CRUSH! (2 HP)", opponent.wx, opponent.wy, wz=1.8, color=(255, 175, 60)))

                if particles is not None:
                    for _ in range(16):
                        particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.25, color=(235, 185, 90)))
            elif prog >= 0.65:
                self.hitbox_center = (
                    self.wx + self.facing_x * 1.25,
                    self.wy + self.facing_y * 1.25
                )

            if self.state_timer <= 0:
                self.wz = 0.0
                self.pole_vault_deflect_active = False
                self.hitbox_active = False
                self.state = STATE_RECOVERY
                self.state_timer = 0.24
            return

        elif self.state == STATE_RECOVERY:
            self.wz = 0.0
            self.pole_vault_deflect_active = False
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.flourish_spin_active = False
            return

        elif self.state == STATE_PARRY:
            self.wz = 0.0
            self.pole_vault_deflect_active = False
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

    def get_extra_props(self) -> dict:
        extra = {}
        if self.state == STATE_POLE_VAULT:
            prog = 1.0 - max(0.0, self.state_timer / max(0.001, self.vault_duration))
            extra = {"pose": "pole_vault", "is_vaulting": True, "vault_prog": prog}
        elif self.state == STATE_STAFF_HOP:
            prog = 1.0 - max(0.0, self.state_timer / max(0.001, self.staff_hop_duration))
            extra = {"pose": "staff_vault_hop", "hop_prog": prog}
        elif self.state == STATE_RECOVERY and getattr(self, "flourish_spin_active", False):
            prog = 1.0 - max(0.0, min(1.0, self.state_timer / max(0.001, getattr(self, "recovery_max_time", 0.45))))
            extra = {"pose": "bo_twirl", "twirl_progress": prog}
        elif self.state in ("DEFEND", "PARRY") or getattr(self, "is_parrying", False):
            extra = {"pose": "bo_spin_guard"}

        if hasattr(self, "extra_props") and self.extra_props:
            extra.update(self.extra_props)
        return extra

    def render(self, surface: pygame.Surface, camera):
        extra = self.get_extra_props()

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
