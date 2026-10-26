"""
Guerreiro Ciclo 6 — Raiden Tameemon (O Yokozuna Invicto / Tanque Juggernaut de Sumô).

Características:
- Vida: 3 HP (pesado e inabalável).
- Velocidade: 3.85 m/s (passada cerimonial de ringue).
- Poise / Super Armor: Hiperarmadura contínua no avanço contra shurikens e projéteis leves.
- Ataque Primário: Tsuppari Rush (rajada rítmica de palmas com avanço, hiperarmadura e pushback massivo).
- Ataque Secundário: Tachiai Tackle (investida de ombro semiteleguiada com velocidade 9.5, dano 1 e repulsão que joga o rival longe).
- Defesa: Gassho-hineri (parry de braços cruzados anulando 100% de recuo).
- Fatalidades:
  - Primário (Tsuppari): Dupla palmada trovejante com onda de choque sônica que decapita o adversário.
  - Secundário (Tackle): Impacto sísmico devastador de corpo inteiro que despedaça o rival e o projeta voando.
"""
import math
import random
import pygame

from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_PARRY, STATE_STUNNED, STATE_ROLL, resolve_playable_bounds,
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle, BloodParticle, FloatingBanner

COLOR_RAIDEN_AURA = (195, 45, 55)


class RaidenSumo(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Raiden")
        self.char_type = "raiden"
        self.speed = 3.85
        self.max_hp = 3
        self.hp = 3
        self.can_parry = True

        # Ataque Primário: Combo de 2 Golpes Pesados de Sumô (Harite -> Morote-Tsuppari)
        self.combo_step = 0  # 0: neutro, 1: Golpe 1 desferido (janela aberta), 2: Golpe 2 executando
        self.combo_window_timer = 0.0
        self.tsuppari_strike1_duration = 0.22
        self.tsuppari_strike1_recovery = 0.22
        self.tsuppari_strike2_duration = 0.28
        self.tsuppari_strike2_recovery = 0.44  # Frenagem pesada pós-combo impedindo spam ininterrupto
        self.tsuppari_combo_window = 0.36
        self.strike2_hit_applied = False

        self.tsuppari_duration = self.tsuppari_strike1_duration
        self.tsuppari_recovery = self.tsuppari_strike1_recovery
        self.tsuppari_reach = 1.65
        self.tsuppari_radius = 1.15
        self.tsuppari_pulses = 3
        self.tsuppari_pulse_timer = 0.0

        # Ação Secundária: Tachiai Tackle (Investida Semiteleguiada com Dano 1 e Super Knockback)
        self.tackle_cooldown = 5.0  # Cooldown calibrado
        self.tackle_timer = 0.0
        self.tackle_duration = 0.30
        self.tackle_speed = 9.5
        self.tackle_dir_x = 1.0
        self.tackle_dir_y = 0.0
        self.tackle_hit_applied = False

        # Esquiva: Deslocamento Lateral Pesado de Sumô
        self.is_agile_dodge = False
        self.roll_speed = 7.5
        self.roll_duration = 0.20
        self.roll_recovery_duration = 0.18
        self.roll_cooldown_duration = 0.40
        self.recovery_duration = self.tsuppari_recovery

    def can_act(self) -> bool:
        if not self.is_alive:
            return False
        if self.roll_recovery_timer > 0 or self.dash_recovery_timer > 0:
            return False
        if self.state in (STATE_IDLE, STATE_WALK):
            return True
        # Permite encadear o Golpe 2 do combo se estiver na janela durante a recuperação do Golpe 1
        if self.combo_step == 1 and self.combo_window_timer > 0 and self.state == STATE_RECOVERY:
            return True
        return False

    def trigger_parry(self) -> bool:
        """Guarda Cerimonial Gassho-hineri: braços cruzados anulando 100% de recuo de impacto."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.40
        return True

    def trigger_tsuppari_rush(self, aim_x: float, aim_y: float, particles: list = None, banners: list = None) -> bool:
        """Ataque Primário: Combo de 2 Golpes Pesados (Harite -> Morote-Tsuppari)."""
        if not self.can_act():
            return False

        self.set_facing(aim_x, aim_y)

        # Se já desferiu o Golpe 1 e está dentro da janela de combo -> Golpe 2 (Morote-Tsuppari)
        if self.combo_step == 1 and self.combo_window_timer > 0:
            self.combo_step = 2
            self.combo_window_timer = 0.0
            self.state = "TSUPPARI_STRIKE_2"
            self.state_timer = self.tsuppari_strike2_duration
            self.tsuppari_pulse_timer = 0.0
            self.strike2_hit_applied = False
            self.hitbox_active = True
            self.hitbox_damage = 2
            self.hitbox_radius = 1.35
            self.hitbox_center = (
                self.wx + self.facing_x * 1.25,
                self.wy + self.facing_y * 1.25
            )
            self.slash_dir = (self.facing_x, self.facing_y)

            if banners is not None:
                banners.append(FloatingBanner("MOROTE-TSUPPARI!", self.wx, self.wy, wz=1.75, color=COLOR_RAIDEN_AURA, duration=0.75))

            if particles is not None:
                for _ in range(12):
                    particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.40, color=(255, 205, 110)))

            return True

        # Golpe 1: Harite (Palma Simples com Avanço Moderado)
        self.combo_step = 1
        self.combo_window_timer = 0.0
        self.state = "TSUPPARI_STRIKE_1"
        self.state_timer = self.tsuppari_strike1_duration
        self.tsuppari_pulse_timer = 0.0
        self.hitbox_active = True
        self.hitbox_damage = 1
        self.hitbox_center = (
            self.wx + self.facing_x * 1.20,
            self.wy + self.facing_y * 1.20
        )
        self.hitbox_radius = self.tsuppari_radius
        self.slash_dir = (self.facing_x, self.facing_y)

        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.30, color=(240, 210, 160)))

        return True

    def trigger_primary(self, aim_x: float, aim_y: float, particles: list = None) -> bool:
        return self.trigger_tsuppari_rush(aim_x, aim_y, particles)

    def trigger_tachiai_tackle(self, aim_x: float = None, aim_y: float = None, particles: list = None, banners: list = None, opponent=None, game_map=None) -> bool:
        """Ação Secundária: Investida Tachiai semiteleguiada com 1 de dano e super repulsão."""
        if not self.can_act() or self.tackle_timer > 0:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        # Semiteleguiamento: ajusta levemente a direção em direção ao oponente se estiver no campo visual
        if opponent and getattr(opponent, "is_alive", False):
            opp_dx = opponent.wx - self.wx
            opp_dy = opponent.wy - self.wy
            opp_dist = math.hypot(opp_dx, opp_dy)
            if 0.5 < opp_dist <= 6.5:
                # Interpola 40% em direção ao alvo
                t_dx = opp_dx / opp_dist
                t_dy = opp_dy / opp_dist
                blend_x = self.facing_x * 0.60 + t_dx * 0.40
                blend_y = self.facing_y * 0.60 + t_dy * 0.40
                mag = math.hypot(blend_x, blend_y) or 1.0
                self.set_facing(self.wx + blend_x / mag, self.wy + blend_y / mag)

        self.tackle_dir_x = self.facing_x
        self.tackle_dir_y = self.facing_y
        self.state = "TACHIAI_TACKLE"
        self.state_timer = self.tackle_duration
        self.tackle_timer = self.tackle_cooldown
        self.tackle_hit_applied = False
        self.hitbox_active = True
        self.hitbox_damage = 1

        self.hitbox_center = (
            self.wx + self.facing_x * 1.10,
            self.wy + self.facing_y * 1.10
        )
        self.hitbox_radius = 1.30
        self.slash_dir = (self.facing_x, self.facing_y)

        if particles is not None:
            for _ in range(12):
                particles.append(SparkParticle(self.wx, self.wy, 0.25, color=(255, 185, 95)))

        if banners is not None:
            banners.append(FloatingBanner("TACHIAI TACKLE!", self.wx, self.wy, wz=1.7, color=COLOR_RAIDEN_AURA, duration=0.85))

        return True

    def trigger_secondary(self, aim_x: float, aim_y: float, particles: list = None, banners: list = None, opponent=None, game_map=None, **kwargs) -> bool:
        return self.trigger_tachiai_tackle(aim_x, aim_y, particles, banners, opponent, game_map)

    def take_hit(self, slash_dir: tuple[float, float], damage: int = 1) -> tuple[bool, bool]:
        """Hiperarmadura / Poise: Raiden não sofre flinch/stun se estiver atacando ou investindo."""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            return True, True

        # Se estiver em Tsuppari ou Tackle, absorve o golpe com Poise inabalável sem stun
        if self.state in ("TSUPPARI_RUSH", "TSUPPARI_STRIKE_1", "TSUPPARI_STRIKE_2", "TACHIAI_TACKLE"):
            return True, False

        self.state = STATE_STUNNED
        self.state_timer = 0.35
        return True, False

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None, **kwargs):
        self.update_dodge_timers(dt)

        if self.combo_window_timer > 0:
            self.combo_window_timer = max(0.0, self.combo_window_timer - dt)
            if self.combo_window_timer <= 0 and self.combo_step == 1:
                self.combo_step = 0

        if self.tackle_timer > 0:
            self.tackle_timer = max(0.0, self.tackle_timer - dt)

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

        if self.state in ("TSUPPARI_STRIKE_1", "TSUPPARI_RUSH"):
            self.state_timer -= dt
            self.tsuppari_pulse_timer += dt

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
                self.wx + self.facing_x * 1.20,
                self.wy + self.facing_y * 1.20
            )

            # Empurrão moderado (1.8 metros)
            if opponent and getattr(opponent, "is_alive", False):
                dist_opp = math.hypot(opponent.wx - self.hitbox_center[0], opponent.wy - self.hitbox_center[1])
                if dist_opp <= self.hitbox_radius + getattr(opponent, "radius", 0.35):
                    push_x = self.facing_x * 3.5 * dt
                    push_y = self.facing_y * 3.5 * dt
                    opponent.wx += push_x
                    opponent.wy += push_y
                    if particles is not None and random.random() < 0.35:
                        particles.append(SparkParticle(opponent.wx, opponent.wy, 0.30, color=(240, 215, 175)))

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.tsuppari_strike1_recovery
                self.combo_window_timer = self.tsuppari_combo_window
                self.hitbox_active = False
            return

        if self.state == "TSUPPARI_STRIKE_2":
            self.state_timer -= dt
            self.tsuppari_pulse_timer += dt

            # Avanço de impacto curto e bofetada dupla estonteante nas têmporas
            step_speed = 1.2
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map is not None:
                min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                self.wx = max(min_x, min(max_x, new_wx))
                self.wy = max(min_y, min(max_y, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.25,
                self.wy + self.facing_y * 1.25
            )

            if opponent and getattr(opponent, "is_alive", False):
                dist_opp = math.hypot(opponent.wx - self.hitbox_center[0], opponent.wy - self.hitbox_center[1])
                if dist_opp <= self.hitbox_radius + getattr(opponent, "radius", 0.35):
                    # Pushback maciço e congelamento de guarda / stun
                    push_x = self.facing_x * 6.5 * dt
                    push_y = self.facing_y * 6.5 * dt
                    opponent.wx += push_x
                    opponent.wy += push_y
                    if not self.strike2_hit_applied:
                        self.strike2_hit_applied = True
                        if hasattr(opponent, "stun"):
                            opponent.stun(0.55)
                    if particles is not None and random.random() < 0.50:
                        particles.append(SparkParticle(opponent.wx, opponent.wy, 0.40, color=(255, 205, 120)))

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.tsuppari_strike2_recovery  # 0.44s de frenagem pesada impedindo spam!
                self.combo_step = 0
                self.combo_window_timer = 0.0
                self.hitbox_active = False
            return

        if self.state == "TACHIAI_TACKLE":
            self.state_timer -= dt

            # Avanço retilíneo impetuoso em velocidade 9.5
            new_wx = self.wx + self.tackle_dir_x * self.tackle_speed * dt
            new_wy = self.wy + self.tackle_dir_y * self.tackle_speed * dt
            if game_map is not None:
                min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                self.wx = max(min_x, min(max_x, new_wx))
                self.wy = max(min_y, min(max_y, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.10,
                self.wy + self.facing_y * 1.10
            )

            # Impacto devastador com o oponente: 1 de dano e super repulsão (4.5 metros)
            if opponent and getattr(opponent, "is_alive", False) and not self.tackle_hit_applied:
                dist_opp = math.hypot(opponent.wx - self.hitbox_center[0], opponent.wy - self.hitbox_center[1])
                if dist_opp <= self.hitbox_radius + getattr(opponent, "radius", 0.35):
                    self.tackle_hit_applied = True
                    hit, dead = opponent.take_hit((self.facing_x, self.facing_y), damage=1)
                    # Arremessa o rival longe
                    opponent.wx += self.facing_x * 4.2
                    opponent.wy += self.facing_y * 4.2
                    opponent.stun(0.85)

                    if particles is not None:
                        for _ in range(16):
                            particles.append(SparkParticle(opponent.wx, opponent.wy, 0.40, color=(255, 175, 60)))
                        for _ in range(8):
                            particles.append(BloodParticle(opponent.wx, opponent.wy, 0.30))

                    if banners is not None:
                        banners.append(FloatingBanner("SUMO SLAM!", opponent.wx, opponent.wy, wz=1.75, color=COLOR_RAIDEN_AURA))

            if self.state_timer <= 0:
                self.hitbox_active = False
                self.state = STATE_RECOVERY
                # Se errou a investida (whiff), sofre leve frenagem extra permitindo punição
                self.state_timer = 0.32 if not self.tackle_hit_applied else 0.20
            return

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

    def render(self, surface: pygame.Surface, camera):
        extra = {}
        if self.state == "TSUPPARI_STRIKE_2":
            extra = {"pose": "tsuppari_2"}
        elif self.state in ("TSUPPARI_RUSH", "TSUPPARI_STRIKE_1"):
            extra = {"pose": "tsuppari"}
        elif self.state == "TACHIAI_TACKLE":
            extra = {"pose": "tackle"}
        elif self.state in ("DEFEND", "PARRY") or getattr(self, "is_parrying", False):
            extra = {"pose": "sumo_guard"}

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
            char_type="raiden",
            walk_timer=getattr(self, "walk_cycle", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
