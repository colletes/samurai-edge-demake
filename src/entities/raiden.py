"""
Guerreiro Ciclo 6 — Raiden Tameemon (O Yokozuna Invicto / Tanque Juggernaut de Sumô).

Características (Fase 2 Overhaul):
- Vida: 3 HP (pesado e inabalável).
- Velocidade: 3.85 m/s (passada cerimonial de ringue Suriashi).
- Poise / Super Armor: Hiperarmadura contínua no avanço contra shurikens e projéteis leves.
- Ataque Primário: Combo de 2 Golpes Pesados (Harite -> Morote-Tsuppari que quebra guardas).
- Ataque Secundário: Tachiai Tackle 3-Fases com Aceleração Realista (4.0 -> 12.5 m/s),
  causando 1 de dano no arranque e 2 de dano em velocidade máxima com super repulsão!
- Defesa: Gassho-hineri (parry de braços cruzados anulando 100% de recuo e refletindo projéteis).
- Esquiva: Shiko Slip-Step (deslize baixo no dohyo com pisada firme sem rolamentos corporais).
- SSAA 2x Offscreen Render nativo com antialiasing bilinear.
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
from src.i18n import t

COLOR_RAIDEN_AURA = (195, 45, 55)
COLOR_SALT_BURST = (255, 250, 235)


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
        self.tsuppari_strike2_duration = 0.30
        self.tsuppari_strike2_recovery = 0.42  # Frenagem pós-combo impedindo spam ininterrupto
        self.tsuppari_combo_window = 0.38
        self.strike2_hit_applied = False

        self.tsuppari_duration = self.tsuppari_strike1_duration
        self.tsuppari_recovery = self.tsuppari_strike1_recovery
        self.tsuppari_reach = 0.85
        self.tsuppari_radius = 0.60
        self.tsuppari_pulses = 3
        self.tsuppari_pulse_timer = 0.0

        # Ação Secundária: Tachiai Tackle 3-Fases com Aceleração Realista
        self.tackle_cooldown = 4.8
        self.tackle_timer = 0.0
        self.tackle_duration = 0.52
        self.tackle_speed = 9.5  # Velocidade nominal média
        self.tackle_initial_speed = 3.8
        self.tackle_max_speed = 12.5
        self.current_tackle_speed = self.tackle_initial_speed
        self.tackle_dir_x = 1.0
        self.tackle_dir_y = 0.0
        self.tackle_hit_applied = False
        self.tackle_phase = "IDLE"  # "CROUCH", "CHARGE", "IMPACT"

        # Esquiva: Shiko Slip-Step (Deslize baixo no dohyo com pisada firme)
        self.is_agile_dodge = False
        self.roll_speed = 7.8
        self.roll_duration = 0.20
        self.roll_recovery_duration = 0.16
        self.roll_cooldown_duration = 0.38
        self.recovery_duration = 0.38
        self.noto_walk_speed_mult = 0.50

        # Qualidade Visual & Fluidez Cinemática (Padrão Kenshi / Sub-fase 2.23)
        self.ssaa_enabled = True
        self._pose_lerp_tracker = {
            "lerp_duration": 0.08,
            "blend_timer": 0.0,
            "pose_key": None,
            "prev_snap": None,
            "last_snap": None,
            "transitions_count": 0,
        }
        self.opponent_launch_state = {"active": False}

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

    def can_move(self) -> bool:
        """Raiden pode se mover livremente em Kamae e durante recuperação (Suriashi a 50% de velocidade)."""
        if self.roll_recovery_timer > 0:
            return False
        if self.state == STATE_RECOVERY:
            return self.is_alive
        return super().can_move()

    def apply_movement(self, move_x: float, move_y: float, dt: float, game_map):
        """Aplica movimentação com passada Suriashi de Sumô (50% de velocidade durante recuperação)."""
        saved_speed = self.speed
        if self.state == STATE_RECOVERY:
            self.speed = saved_speed * getattr(self, "noto_walk_speed_mult", 0.50)
        super().apply_movement(move_x, move_y, dt, game_map)
        self.speed = saved_speed

    def trigger_parry(self) -> bool:
        """Guarda Cerimonial Gassho-hineri: braços cruzados anulando 100% de recuo de impacto."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.40
        return True

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None) -> bool:
        """Esquiva Shiko Slip-Step: deslizamento baixo e potente na argila com pisada sólida."""
        if not self.can_act() or self.roll_cooldown_timer > 0:
            return False

        length = math.hypot(dir_x, dir_y)
        if length > 0.001:
            self.roll_dir_x = dir_x / length
            self.roll_dir_y = dir_y / length
        else:
            self.roll_dir_x = self.facing_x
            self.roll_dir_y = self.facing_y

        self.set_facing(self.wx + self.roll_dir_x, self.wy + self.roll_dir_y)
        self.state = STATE_ROLL
        self.state_timer = self.roll_duration
        self.roll_cooldown_timer = self.roll_cooldown_duration
        self.is_invulnerable_dodge = True

        if particles is not None:
            # Poeira de argila e sal espalhando no arranque do Shiko
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.22, color=(222, 198, 165)))

        return True

    def trigger_tsuppari_rush(self, aim_x: float = None, aim_y: float = None, particles: list = None, banners: list = None) -> bool:
        """Ataque Primário: Combo de 2 Golpes Pesados (Harite -> Morote-Tsuppari)."""
        if not self.can_act():
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        # Se já desferiu o Golpe 1 e está dentro da janela de combo -> Golpe 2 (Morote-Tsuppari quebra guardas)
        if self.combo_step == 1 and self.combo_window_timer > 0:
            self.combo_step = 2
            self.combo_window_timer = 0.0
            self.state = "TSUPPARI_STRIKE_2"
            self.state_timer = self.tsuppari_strike2_duration
            self.tsuppari_pulse_timer = 0.0
            self.strike2_hit_applied = False
            self.hitbox_active = False
            self.hitbox_damage = 2
            self.hitbox_radius = 0.65
            self.hitbox_center = (
                self.wx + self.facing_x * 0.72,
                self.wy + self.facing_y * 0.72
            )
            self.slash_dir = (self.facing_x, self.facing_y)

            if banners is not None:
                banners.append(FloatingBanner("MOROTE-TSUPPARI!", self.wx, self.wy, wz=1.75, color=COLOR_RAIDEN_AURA, duration=0.75))

            if particles is not None:
                for _ in range(14):
                    particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.35, color=(255, 205, 110)))

            return True

        # Golpe 1: Harite (Palma Direita com rotação de quadril)
        self.combo_step = 1
        self.combo_window_timer = 0.0
        self.state = "TSUPPARI_STRIKE_1"
        self.state_timer = self.tsuppari_strike1_duration
        self.tsuppari_pulse_timer = 0.0
        self.hitbox_active = False
        self.hitbox_damage = 1
        self.hitbox_center = (
            self.wx + self.facing_x * 0.68,
            self.wy + self.facing_y * 0.68
        )
        self.hitbox_radius = 0.60
        self.slash_dir = (self.facing_x, self.facing_y)

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.25, color=(240, 210, 160)))

        return True

    def trigger_primary(self, aim_x: float = None, aim_y: float = None, particles: list = None, banners: list = None, **kwargs) -> bool:
        return self.trigger_tsuppari_rush(aim_x, aim_y, particles, banners)

    def trigger_attack(self, aim_x: float = None, aim_y: float = None, particles: list = None, banners: list = None, **kwargs) -> bool:
        return self.trigger_primary(aim_x, aim_y, particles, banners, **kwargs)

    def trigger_tachiai_tackle(self, aim_x: float = None, aim_y: float = None, particles: list = None, banners: list = None, opponent=None, game_map=None) -> bool:
        """
        Ação Secundária: Tachiai Tackle 3-Fases com Aceleração Realista:
        - Fase 1 (Kamae Crouch): Mãos na argila (0.0s a 0.14s) preparando a arremetida.
        - Fase 2 (Aceleração Contínua): Rampa de 4.0 m/s até 12.5 m/s com inclinação frontal de 35°.
        - Fase 3 (Impacto Devastador): Causa 1 de dano no arranque e 2 de dano em velocidade máxima!
        """
        if not self.can_act() or self.tackle_timer > 0:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        # Semiteleguiamento: interpola suavemente em direção ao adversário
        if opponent and getattr(opponent, "is_alive", False):
            opp_dx = opponent.wx - self.wx
            opp_dy = opponent.wy - self.wy
            opp_dist = math.hypot(opp_dx, opp_dy)
            if 0.5 < opp_dist <= 7.0:
                t_dx = opp_dx / opp_dist
                t_dy = opp_dy / opp_dist
                blend_x = self.facing_x * 0.65 + t_dx * 0.35
                blend_y = self.facing_y * 0.65 + t_dy * 0.35
                mag = math.hypot(blend_x, blend_y) or 1.0
                self.set_facing(self.wx + blend_x / mag, self.wy + blend_y / mag)

        self.tackle_dir_x = self.facing_x
        self.tackle_dir_y = self.facing_y
        self.state = "TACHIAI_TACKLE"
        self.state_timer = self.tackle_duration
        self.tackle_timer = self.tackle_cooldown
        self.tackle_hit_applied = False
        self.current_tackle_speed = self.tackle_initial_speed
        self.tackle_phase = "CROUCH"
        self.hitbox_active = False
        self.hitbox_damage = 1

        self.hitbox_center = (
            self.wx + self.facing_x * 0.90,
            self.wy + self.facing_y * 0.90
        )
        self.hitbox_radius = 1.20
        self.slash_dir = (self.facing_x, self.facing_y)

        if particles is not None:
            for _ in range(10):
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

        # Se estiver em Tsuppari ou Tackle acelerando, absorve com Poise inabalável sem stun
        if self.state in ("TSUPPARI_RUSH", "TSUPPARI_STRIKE_1", "TSUPPARI_STRIKE_2", "TACHIAI_TACKLE"):
            return True, False

        self.state = STATE_STUNNED
        self.state_timer = 0.35
        return True, False

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None, **kwargs):
        # Atualizar interpolador de pose (Pose LERP 0.08s — Entregável 2.23.9 / Padrão Kenshi; avança mesmo em INTRO/VICTORY)
        lerp_dt = dt if dt > 0.0 else (1.0 / 60.0)
        if hasattr(self, "_pose_lerp_tracker") and self._pose_lerp_tracker["blend_timer"] > 0.0:
            self._pose_lerp_tracker["blend_timer"] = max(0.0, self._pose_lerp_tracker["blend_timer"] - lerp_dt)

        # Atualização contínua da física parabólica de arremesso do adversário atingido pelo Tachiai
        if getattr(self, "opponent_launch_state", None) and self.opponent_launch_state.get("active", False):
            ls = self.opponent_launch_state
            opp = ls.get("opponent")
            if opp and getattr(opp, "is_alive", False) and ls["timer"] > 0:
                # 1. Fase de Hitstop no instante exato do impacto (peso e gravidade visual)
                if ls.get("hitstop_timer", 0.0) > 0.0:
                    ls["hitstop_timer"] = max(0.0, ls["hitstop_timer"] - dt)
                    if particles is not None and random.random() < 0.60:
                        particles.append(SparkParticle(opp.wx, opp.wy, getattr(opp, "wz", 0.0) + 0.35, color=(255, 180, 70)))
                else:
                    # 2. Voo parabólico com gravidade e arrasto de ar
                    ls["timer"] = max(0.0, ls["timer"] - dt)
                    opp.wz = max(0.0, getattr(opp, "wz", 0.0) + ls["vz"] * dt)
                    ls["vz"] -= ls["gravity"] * dt

                    drag = 0.94 ** (dt * 60.0)
                    ls["vx"] *= drag
                    ls["vy"] *= drag

                    next_wx = opp.wx + ls["vx"] * dt
                    next_wy = opp.wy + ls["vy"] * dt

                    collided_wall = False
                    if game_map is not None:
                        min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                        bounded_x = max(min_x, min(max_x, next_wx))
                        bounded_y = max(min_y, min(max_y, next_wy))
                        if bounded_x != next_wx or bounded_y != next_wy:
                            collided_wall = True
                            next_wx, next_wy = bounded_x, bounded_y

                        for obs in list(getattr(game_map, "rocks", [])) + list(getattr(game_map, "buildings", [])):
                            col, push_x, push_y = obs.check_collision(next_wx, next_wy, getattr(opp, "radius", 0.35))
                            if col:
                                collided_wall = True
                                next_wx += push_x
                                next_wy += push_y

                    opp.wx, opp.wy = next_wx, next_wy

                    # Impacto na parede/obstáculo durante o voo
                    if collided_wall and not ls.get("bounced", False) and (abs(ls["vx"]) + abs(ls["vy"]) > 2.5):
                        ls["bounced"] = True
                        ls["vx"] *= -0.20
                        ls["vy"] *= -0.20
                        if particles is not None:
                            for _ in range(8):
                                particles.append(SparkParticle(opp.wx, opp.wy, getattr(opp, "wz", 0.0) + 0.35, color=(235, 205, 160)))

                    # Pouso sísmico no solo do dohyo
                    if opp.wz <= 0.0 and ls["vz"] < 0:
                        opp.wz = 0.0
                        ls["active"] = False
                        if particles is not None:
                            count = 14 if ls.get("dmg", 1) == 2 else 7
                            for _ in range(count):
                                particles.append(SparkParticle(opp.wx, opp.wy, 0.12, color=(210, 195, 170)))
            else:
                self.opponent_launch_state["active"] = False

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

        # -------------------------------------------------------------------------------------------------
        # GOLPE 1: HARITE
        # -------------------------------------------------------------------------------------------------
        if self.state in ("TSUPPARI_STRIKE_1", "TSUPPARI_RUSH"):
            self.state_timer -= dt
            self.tsuppari_pulse_timer += dt
            elapsed = self.tsuppari_strike1_duration - self.state_timer

            # Wind-up de 0.05s -> Fase ativa de impacto (0.05s a 0.18s)
            if 0.05 <= elapsed <= 0.18:
                self.hitbox_active = True
            else:
                self.hitbox_active = False

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
                self.wx + self.facing_x * 0.68,
                self.wy + self.facing_y * 0.68
            )
            self.hitbox_radius = 0.60

            # Empurrão físico progressivo de sumô no impacto
            if self.hitbox_active and opponent and getattr(opponent, "is_alive", False):
                dist_opp = math.hypot(opponent.wx - self.hitbox_center[0], opponent.wy - self.hitbox_center[1])
                if dist_opp <= self.hitbox_radius + getattr(opponent, "radius", 0.35):
                    push_x = self.facing_x * 3.6 * dt
                    push_y = self.facing_y * 3.6 * dt
                    new_opp_x = opponent.wx + push_x
                    new_opp_y = opponent.wy + push_y
                    if game_map is not None:
                        min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                        new_opp_x = max(min_x, min(max_x, new_opp_x))
                        new_opp_y = max(min_y, min(max_y, new_opp_y))
                        for obs in list(getattr(game_map, "rocks", [])) + list(getattr(game_map, "buildings", [])):
                            col, px, py = obs.check_collision(new_opp_x, new_opp_y, getattr(opponent, "radius", 0.35))
                            if col:
                                new_opp_x += px
                                new_opp_y += py
                    opponent.wx, opponent.wy = new_opp_x, new_opp_y
                    if particles is not None and random.random() < 0.35:
                        particles.append(SparkParticle(opponent.wx, opponent.wy, 0.25, color=(240, 215, 175)))

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.tsuppari_strike1_recovery
                self.combo_window_timer = self.tsuppari_combo_window
                self.hitbox_active = False
            return

        # -------------------------------------------------------------------------------------------------
        # GOLPE 2: MOROTE-TSUPPARI (Quebra de Guarda)
        # -------------------------------------------------------------------------------------------------
        if self.state == "TSUPPARI_STRIKE_2":
            self.state_timer -= dt
            self.tsuppari_pulse_timer += dt
            elapsed = self.tsuppari_strike2_duration - self.state_timer

            # Wind-up de 0.07s (braços abrem) -> Fase ativa (0.07s a 0.24s)
            if 0.07 <= elapsed <= 0.24:
                self.hitbox_active = True
            else:
                self.hitbox_active = False

            step_speed = 1.4
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map is not None:
                min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                self.wx = max(min_x, min(max_x, new_wx))
                self.wy = max(min_y, min(max_y, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 0.72,
                self.wy + self.facing_y * 0.72
            )
            self.hitbox_radius = 0.70

            if self.hitbox_active and opponent and getattr(opponent, "is_alive", False):
                dist_opp = math.hypot(opponent.wx - self.hitbox_center[0], opponent.wy - self.hitbox_center[1])
                if dist_opp <= self.hitbox_radius + getattr(opponent, "radius", 0.35):
                    # Quebra de guarda: se oponente estiver em PARRY, estilhaça a defesa!
                    if getattr(opponent, "state", "") == STATE_PARRY:
                        opponent.state = STATE_STUNNED
                        opponent.state_timer = 0.65
                        if banners is not None:
                            banners.append(FloatingBanner(t("banner_guard_broken"), opponent.wx, opponent.wy, wz=1.8, color=(255, 60, 60)))
                        if particles is not None:
                            for _ in range(12):
                                particles.append(SparkParticle(opponent.wx, opponent.wy, 0.45, color=(255, 235, 140)))

                    push_x = self.facing_x * 7.0 * dt
                    push_y = self.facing_y * 7.0 * dt
                    new_opp_x = opponent.wx + push_x
                    new_opp_y = opponent.wy + push_y
                    if game_map is not None:
                        min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                        new_opp_x = max(min_x, min(max_x, new_opp_x))
                        new_opp_y = max(min_y, min(max_y, new_opp_y))
                        for obs in list(getattr(game_map, "rocks", [])) + list(getattr(game_map, "buildings", [])):
                            col, px, py = obs.check_collision(new_opp_x, new_opp_y, getattr(opponent, "radius", 0.35))
                            if col:
                                new_opp_x += px
                                new_opp_y += py
                    opponent.wx, opponent.wy = new_opp_x, new_opp_y

                    if not self.strike2_hit_applied:
                        self.strike2_hit_applied = True
                        if hasattr(opponent, "stun"):
                            opponent.stun(0.55)
                    if particles is not None and random.random() < 0.50:
                        particles.append(SparkParticle(opponent.wx, opponent.wy, 0.40, color=(255, 205, 120)))

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.tsuppari_strike2_recovery
                self.combo_step = 0
                self.combo_window_timer = 0.0
                self.hitbox_active = False
            return

        # -------------------------------------------------------------------------------------------------
        # INVESTIDA SECUNDÁRIA: TACHIAI TACKLE 3-FASES
        # -------------------------------------------------------------------------------------------------
        if self.state == "TACHIAI_TACKLE":
            self.state_timer -= dt
            elapsed = self.tackle_duration - self.state_timer

            # FASE 1: Kamae Crouch (mãos na argila nos primeiros 0.14s)
            if elapsed < 0.14:
                self.tackle_phase = "CROUCH"
                self.hitbox_active = False
                u = elapsed / 0.14
                self.current_tackle_speed = self.tackle_initial_speed * (0.4 + 0.6 * u)
                if particles is not None and random.random() < 0.40:
                    particles.append(SparkParticle(self.wx, self.wy, 0.20, color=(222, 198, 165)))

            # FASE 2: Aceleração Explosiva (0.14s até 0.44s) -> Rampa contínua até 12.5 m/s
            elif elapsed < 0.44:
                self.tackle_phase = "CHARGE"
                self.hitbox_active = True
                u = (elapsed - 0.14) / 0.30
                self.current_tackle_speed = self.tackle_initial_speed + (self.tackle_max_speed - self.tackle_initial_speed) * (u ** 1.3)

                # Dano escala para 2 se atingir velocidade máxima (>= 10.0 m/s)
                self.hitbox_damage = 2 if self.current_tackle_speed >= 10.0 else 1

                if particles is not None and random.random() < 0.70:
                    trail_x = self.wx - self.facing_x * 0.35
                    trail_y = self.wy - self.facing_y * 0.35
                    particles.append(SparkParticle(trail_x, trail_y, 0.28, color=(225, 200, 160)))

            # FASE 3: Frenagem de Desaceleração pós-carga
            else:
                self.tackle_phase = "IMPACT"
                self.hitbox_active = False
                self.current_tackle_speed = max(2.0, self.current_tackle_speed - 22.0 * dt)

            # Movimento com velocidade acelerada contínua
            new_wx = self.wx + self.tackle_dir_x * self.current_tackle_speed * dt
            new_wy = self.wy + self.tackle_dir_y * self.current_tackle_speed * dt
            if game_map is not None:
                min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                self.wx = max(min_x, min(max_x, new_wx))
                self.wy = max(min_y, min(max_y, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.05,
                self.wy + self.facing_y * 1.05
            )

            # Colisão corporal com o rival
            if self.hitbox_active and opponent and getattr(opponent, "is_alive", False) and not self.tackle_hit_applied:
                dist_opp = math.hypot(opponent.wx - self.hitbox_center[0], opponent.wy - self.hitbox_center[1])
                if dist_opp <= self.hitbox_radius + getattr(opponent, "radius", 0.35):
                    self.tackle_hit_applied = True
                    dmg = 2 if self.current_tackle_speed >= 10.0 else 1
                    hit, dead = opponent.take_hit((self.facing_x, self.facing_y), damage=dmg)

                    # Inicia lançamento físico com trajetória parabólica autêntica (sem teleport instantaneous)
                    launch_speed = 25.0 if dmg == 2 else 19.5
                    self.opponent_launch_state = {
                        "active": True,
                        "opponent": opponent,
                        "vx": self.facing_x * launch_speed,
                        "vy": self.facing_y * launch_speed,
                        "vz": 5.2 if dmg == 2 else 4.2,
                        "gravity": 12.5 if dmg == 2 else 12.0,
                        "timer": 0.90 if dmg == 2 else 0.75,
                        "hitstop_timer": 0.08 if dmg == 2 else 0.05,
                        "dmg": dmg,
                        "bounced": False,
                    }
                    opponent.stun(1.10 if dmg == 2 else 0.75)
                    opponent.wz = 0.08

                    # Frenagem por impacto físico
                    self.current_tackle_speed = min(self.current_tackle_speed, 3.0)

                    if particles is not None:
                        for _ in range(18 if dmg == 2 else 10):
                            particles.append(SparkParticle(opponent.wx, opponent.wy, 0.40, color=(255, 175, 60)))
                        for _ in range(10 if dmg == 2 else 5):
                            particles.append(BloodParticle(opponent.wx, opponent.wy, 0.35))

                    if banners is not None:
                        msg = "MAX TACHIAI SLAM! (2 DANO)" if dmg == 2 else "TACHIAI IMPACT!"
                        banners.append(FloatingBanner(msg, opponent.wx, opponent.wy, wz=1.75, color=COLOR_RAIDEN_AURA))

            if self.state_timer <= 0:
                self.hitbox_active = False
                self.state = STATE_RECOVERY
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
        extra = {
            "ssaa_2x": getattr(self, "ssaa_enabled", True),
            "pose_lerp_tracker": getattr(self, "_pose_lerp_tracker", None),
            "tachiai_phase": getattr(self, "tackle_phase", ""),
        }

        if self.state == "TSUPPARI_STRIKE_2":
            extra["pose"] = "tsuppari_2"
        elif self.state in ("TSUPPARI_RUSH", "TSUPPARI_STRIKE_1"):
            extra["pose"] = "tsuppari"
        elif self.state == "TACHIAI_TACKLE":
            if self.tackle_phase == "CROUCH":
                extra["pose"] = "tachiai_crouch"
            else:
                extra["pose"] = "tackle"
        elif self.state == STATE_ROLL:
            extra["pose"] = "shiko_slip"
        elif self.state in ("DEFEND", "PARRY") or getattr(self, "is_parrying", False):
            extra["pose"] = "sumo_guard"

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
