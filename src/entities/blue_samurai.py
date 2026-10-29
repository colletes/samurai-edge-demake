"""
Samurai Azul (Musashi): Mestre do Hyoho Niten Ichi-ryū (Duas Lâminas).
Ataque de alto windup preparatório seguido por um combo rápido e devastador
de 3 cortes consecutivos, postura de bloqueio (Cross Guard Parry) com contra-ataque
Cross Shockwave, rolamento tático de ombro e finalizações cinemáticas brutais.

Diretrizes Críticas:
- Musashi NUNCA embainha suas lâminas durante o combate ou vitória (permanece com espadas sacadas).
- Rolamento Tático: Estritamente sem sombras Zanzou e sem duplicação de personagem, com LERP fluida.
- Cancelamento Ofensivo aos 40% finais da esquiva em golpe corrido instantâneo.
- Finalização A: Empalamento sequencial duplo (Katana depois Wakizashi) e leque rasgando torso em 3 partes.
- Finalização B: Cross Vacuum Slicer em 4 quadrantes simétricos.
"""
import math
import pygame
from src.config import (
    COLOR_BLUE_KIMONO, COLOR_BLUE_HAIR, COLOR_BLUE_HAKAMA,
    COLOR_BLUE_AURA, COLOR_STEEL, COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_WINDUP, STATE_DASH,
    STATE_ATTACK, STATE_RECOVERY, STATE_PARRY, STATE_STUNNED, STATE_DEAD, STATE_ROLL,
    slide_movement_against_obstacles
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import MusashiWaveProjectile


class BlueSamurai(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Musashi")
        self.char_type = "musashi"
        self.speed = 4.0

        # Musashi com 3 HP (Resistência de espadachim veterano)
        self.max_hp = 3
        self.hp = 3

        # Parâmetros do Combo Manual Niten de 3 Cortes
        self.windup_duration = 0.35
        self.hit_duration = 0.10
        self.combo_step = 0               # 0, 1, 2 ou 3
        self.combo_buffered = False
        self.combo_window_timer = 0.0
        self.recovery_duration = 0.15     # Recuperação sem embainhar (swords drawn)
        self.noto_walk_speed_mult = 0.50  # Pode caminhar a 50% durante a recuperação

        # Defesa / Cross Guard Parry & Contra-ataque
        self.parry_timer = 0.0
        self.parry_duration = 0.45
        self.parry_reflect_active_timer = 0.0  # Janela de reflexão ativa: 0.28s
        self.counter_shockwave_ready = False
        self.cross_shockwave_timer = 0.0
        self.cross_shockwave_duration = 0.24

        # Soft Stun (quando atingido por golpe de 2 de dano)
        self.soft_stun_timer = 0.0

        # Terceira Ação: Rolamento Tático de Ombro (Sem Zanzou, Sem Duplicação)
        self.is_agile_dodge = False
        self.roll_speed = 8.5
        self.roll_duration = 0.20
        self.roll_recovery_duration = 0.16
        self.roll_cooldown_duration = 0.35
        self.is_roll_cancel = False

        # Qualidade Visual & Fluidez (SSAA 2x + Pose LERP 0.08s)
        self.ssaa_enabled = True
        self._pose_lerp_tracker = {
            "lerp_duration": 0.08,
            "blend_timer": 0.0,
            "pose_key": None,
            "prev_snap": None,
            "last_snap": None,
            "transitions_count": 0,
        }

        # Estado da pose ativa para rendering
        self.current_pose = ""

    def can_act(self) -> bool:
        """Musashi pode agir se vivo, em IDLE/WALK/RECOVERY e sem bloqueios de timer."""
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
            and self.soft_stun_timer <= 0
        )

    def can_move(self) -> bool:
        """Musashi pode se movimentar em RECOVERY mantendo as espadas sacadas em guarda alta."""
        if self.roll_recovery_timer > 0:
            return False
        if self.state == STATE_RECOVERY:
            return self.is_alive
        return super().can_move()

    def apply_movement(self, move_x: float, move_y: float, dt: float, game_map):
        """Aplica movimentação mantendo o estado de RECOVERY (guarda alta móvel) a 50% de velocidade."""
        if self.state == STATE_RECOVERY:
            saved_speed = self.speed
            self.speed = saved_speed * self.noto_walk_speed_mult
            try:
                super().apply_movement(move_x, move_y, dt, game_map)
            finally:
                self.speed = saved_speed
        else:
            super().apply_movement(move_x, move_y, dt, game_map)

    def can_cancel_roll(self) -> bool:
        """
        Janela de Cancelamento Ofensivo (Entregável 2.2.3):
        Permite cancelar os últimos 40% do rolamento diretamente em um corte de avanço (Lunge Slash).
        """
        roll_dur = getattr(self, "roll_duration", 0.20)
        return (
            self.is_alive
            and self.state == STATE_ROLL
            and self.state_timer <= roll_dur * 0.40 + 1e-5
        )

    def take_hit(self, slash_dir: tuple[float, float], damage: int = 2) -> tuple[bool, bool]:
        """Aplica dano, parry frontal ou soft stun."""
        if not self.is_alive:
            return False, False

        # Se estiver em esquiva / roll com i-frames ativos
        if self.state in (STATE_ROLL, STATE_DASH, "DODGE") and (self.is_invulnerable_dodge or getattr(self, "is_invulnerable_dodge", False)):
            return False, False

        # Se estiver em postura de parry e de frente para o ataque
        if self.state == STATE_PARRY:
            dot = self.facing_x * slash_dir[0] + self.facing_y * slash_dir[1]
            if dot < -0.2:  # O ataque veio de frente!
                self.on_parry_successful(None)
                return False, False  # Defendido com sucesso!

        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            self.state = STATE_DEAD
            self.state_timer = 0.0
            return True, True
        else:
            self.soft_stun_timer = 0.40
            self.hitbox_active = False
            self.is_invulnerable_dodge = False
            return True, False

    def trigger_combo_attack(self, target_wx: float, target_wy: float, instant: bool = False):
        """
        Dispara ou encadeia os 3 ataques em sequência manual e ritmada (Entregável 2.2.1).
        Permite cancelamento ofensivo direto dos 40% finais do rolamento tático.
        """
        is_cancel = self.can_cancel_roll()
        if not self.can_act() and not is_cancel:
            if self.state == STATE_ATTACK and self.combo_step < 3:
                self.combo_buffered = True
                self.set_facing(target_wx, target_wy)
            return False

        if is_cancel:
            self.set_facing(target_wx, target_wy)
            self.is_roll_cancel = True
            self.is_invulnerable_dodge = False
            self.combo_step = 1
            self.combo_buffered = False
            self.state = STATE_ATTACK
            self.state_timer = 0.18
            self.hitbox_active = True
            self.hitbox_radius = 1.60
            self.slash_dir = (self.facing_x, self.facing_y)
            self.hitbox_center = (self.wx + self.facing_x * 0.95, self.wy + self.facing_y * 0.95)
            try:
                from src.audio import play_sfx, SoundEvent
                play_sfx(SoundEvent.SLASH_KATANA, volume_scale=0.98)
            except Exception:
                pass
            return True

        if self.state in (STATE_IDLE, STATE_WALK):
            if self.dash_recovery_timer > 0:
                return False
            self.set_facing(target_wx, target_wy)
            self.combo_step = 1
            self.combo_buffered = False
            self.state = STATE_ATTACK
            self.state_timer = 0.18
            self.hitbox_active = True
            self.hitbox_radius = 1.45
            self.slash_dir = (self.facing_x, self.facing_y)
            self.hitbox_center = (self.wx + self.facing_x * 0.9, self.wy + self.facing_y * 0.9)
            try:
                from src.audio import play_sfx, SoundEvent
                play_sfx(SoundEvent.SLASH_KATANA, volume_scale=0.92)
            except Exception:
                pass
            return True

        elif self.state == STATE_RECOVERY and self.combo_step < 3 and self.combo_window_timer > 0:
            self.set_facing(target_wx, target_wy)
            self.combo_step += 1
            self.combo_buffered = False
            self.state = STATE_ATTACK
            self.state_timer = 0.18
            self.hitbox_active = True
            self.hitbox_radius = 1.62 if self.combo_step == 2 else 2.06
            self.slash_dir = (self.facing_x, self.facing_y)
            self.hitbox_center = (self.wx + self.facing_x * 1.0, self.wy + self.facing_y * 1.0)
            try:
                from src.audio import play_sfx, SoundEvent
                play_sfx(SoundEvent.SLASH_KATANA, volume_scale=0.95)
            except Exception:
                pass
            return True
        return False

    def trigger_parry(self, particles=None, banners=None, opponent=None, projectiles=None) -> bool:
        """
        Ação Secundária (Entregável 2.2.2): Cross Guard Parry (Lâminas Cruzadas em X).
        Janela de reflexão de 0.28s; se o contra-ataque estiver pronto, desfere o Cross Shockwave.
        """
        if not self.is_alive:
            return False

        if self.counter_shockwave_ready:
            aim_x = opponent.wx if opponent else (self.wx + self.facing_x * 2.0)
            aim_y = opponent.wy if opponent else (self.wy + self.facing_y * 2.0)
            self.trigger_cross_shockwave(aim_x, aim_y, projectiles=projectiles, particles=particles, banners=banners)
            return True

        if not self.can_move() or self.dash_recovery_timer > 0:
            return False

        self.state = STATE_PARRY
        self.state_timer = self.parry_duration
        self.parry_reflect_active_timer = 0.28
        self.current_pose = "cross_guard"
        return True

    def trigger_cross_shockwave(self, target_wx: float = None, target_wy: float = None, projectiles=None, particles=None, banners=None):
        """
        Contra-Ataque Punitivo Cross Shockwave (Entregável 2.2.2).
        Corte explosivo em 'X' que libera uma onda de vácuo devastadora (2 de dano).
        """
        if target_wx is not None and target_wy is not None:
            self.set_facing(target_wx, target_wy)

        self.state = "CROSS_SHOCKWAVE"
        self.state_timer = self.cross_shockwave_duration
        self.hitbox_active = True
        self.hitbox_radius = 2.20
        self.slash_dir = (self.facing_x, self.facing_y)
        self.hitbox_center = (self.wx + self.facing_x * 1.1, self.wy + self.facing_y * 1.1)
        self.counter_shockwave_ready = False
        self.current_pose = "cross_shockwave"

        if projectiles is not None:
            wave = MusashiWaveProjectile(
                wx=self.wx + self.facing_x * 0.5,
                wy=self.wy + self.facing_y * 0.5,
                wz=0.45,
                dir_x=self.facing_x,
                dir_y=self.facing_y,
                owner=self
            )
            projectiles.append(wave)

        if particles is not None:
            from src.effects.particles import SparkParticle
            for _ in range(12):
                particles.append(SparkParticle(self.wx + self.facing_x * 0.6, self.wy + self.facing_y * 0.6, 0.55))

        if banners is not None:
            from src.effects.particles import FloatingBanner
            banners.append(FloatingBanner("CROSS SHOCKWAVE!", self.wx, self.wy, wz=1.75, color=(110, 180, 255)))

        try:
            from src.audio import play_sfx, SoundEvent
            play_sfx(SoundEvent.SWORD_SLASH, volume_scale=1.0)
            play_sfx(SoundEvent.SWORD_CLASH, volume_scale=0.85)
        except Exception:
            pass

    def on_parry_successful(self, opponent=None, particles=None, banners=None):
        """Reação defensiva triunfante de Musashi ao aparar ataque frontal."""
        self.counter_shockwave_ready = True
        try:
            from src.audio import play_sfx, SoundEvent
            play_sfx(SoundEvent.SWORD_CLASH, volume_scale=1.0)
        except Exception:
            pass

        if particles is not None:
            from src.effects.particles import SparkParticle
            for _ in range(16):
                particles.append(SparkParticle(self.wx + self.facing_x * 0.5, self.wy + self.facing_y * 0.5, 0.65))

        if banners is not None:
            from src.effects.particles import FloatingBanner
            banners.append(FloatingBanner("CROSS GUARD DEFLECT!", self.wx, self.wy, wz=1.8, color=(110, 200, 255)))

    def on_parried(self, opponent, game_map=None, banners: list = None, particles: list = None):
        """
        Reação ao ter seu golpe aparado pelo adversário (Entregável 2.2.3):
        - Terrestre: Recuo firme mantendo as duas espadas erguidas em guarda alta frontal (sem embainhar).
        - Aéreo / Salto: Giro acrobático absorvendo o impacto e pousando em base firme.
        """
        self.hitbox_active = False
        self.combo_step = 0
        self.combo_buffered = False

        if opponent is not None:
            dx = self.wx - opponent.wx
            dy = self.wy - opponent.wy
            dist = math.hypot(dx, dy)
            if dist > 1e-4:
                nx, ny = dx / dist, dy / dist
            else:
                nx, ny = -self.facing_x, -self.facing_y
            self.facing_x, self.facing_y = -nx, -ny

            if getattr(self, "wz", 0.0) > 0.3:
                # Recuo aéreo com salto acrobático
                self.state = STATE_STUNNED
                self.state_timer = 0.55
                self.wz = 0.8
            else:
                # Recuo terrestre firme em guarda alta
                self.state = STATE_PARRY
                self.state_timer = 0.40
                self.parry_reflect_active_timer = 0.0

        if banners is not None:
            from src.effects.particles import FloatingBanner
            banners.append(FloatingBanner("CLASH RECOIL!", self.wx, self.wy, wz=1.7, color=(210, 180, 120)))

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None):
        """
        Terceira Ação: Rolamento Tático de Ombro (Entregável 2.2.3).
        CUIDADO CRÍTICO: Estritamente sem sombras Zanzou e sem duplicação de personagem.
        """
        if (
            not self.is_alive
            or self.state in (STATE_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK, "CROSS_SHOCKWAVE")
            or getattr(self, "wz", 0.0) > 0.45
            or self.roll_recovery_timer > 0
            or self.roll_cooldown_timer > 0
            or self.dash_recovery_timer > 0
        ):
            return False

        self.wz = 0.0
        if dir_x == 0 and dir_y == 0:
            dir_x, dir_y = self.facing_x, self.facing_y
        else:
            mag = math.hypot(dir_x, dir_y)
            if mag > 0.001:
                dir_x /= mag
                dir_y /= mag

        self.state = STATE_ROLL
        self.state_timer = self.roll_duration
        self.facing_x = dir_x
        self.facing_y = dir_y
        self.is_invulnerable_dodge = True
        self.hitbox_active = False
        self.is_roll_cancel = False
        self.current_pose = "tactical_roll"

        try:
            from src.audio import play_sfx, SoundEvent
            play_sfx(SoundEvent.DASH_ROLL, volume_scale=0.88)
        except Exception:
            pass
        return True

    def update_roll(self, dt: float, game_map, particles: list = None):
        """Atualiza a translação física e cronômetro do rolamento tático."""
        if self.state != STATE_ROLL:
            return

        self.state_timer -= dt
        step = self.roll_speed * dt
        dx = self.facing_x * step
        dy = self.facing_y * step
        new_wx, new_wy = slide_movement_against_obstacles(self.wx, self.wy, dx, dy, self.radius, game_map)
        self.wx, self.wy = new_wx, new_wy

        if self.state_timer <= 0:
            self.state = STATE_IDLE
            self.is_invulnerable_dodge = False
            self.roll_recovery_timer = self.roll_recovery_duration
            self.roll_cooldown_timer = self.roll_cooldown_duration
            self.dash_recovery_timer = self.roll_recovery_duration
            self.current_pose = ""

    def trigger_finisher_a(self, opponent, cinematic_director, game_map=None):
        """Dispara o Finisher 1: Empalamento Duplo em Leque (DUAL_IMPALE_X_SPREAD — 二天一流)."""
        if cinematic_director:
            cinematic_director.trigger_fatal_strike(self, opponent, "DUAL_IMPALE_X_SPREAD", (self.facing_x, self.facing_y))

    def trigger_finisher_b(self, opponent, cinematic_director, game_map=None):
        """Dispara o Finisher 2: Cross Vacuum Slicer em 4 Quadrantes (CROSS_VACUUM_SLICER — 十字真空波)."""
        if cinematic_director:
            cinematic_director.trigger_fatal_strike(self, opponent, "CROSS_VACUUM_SLICER", (self.facing_x, self.facing_y))

    def update(self, dt: float, game_map, particles=None, projectiles=None):
        """Atualiza a lógica, poses e golpes do Musashi."""
        if not self.is_alive:
            return

        self.update_stealth(game_map)
        self.update_dodge_timers(dt)

        # Atualizar cronômetro do Pose LERP (Entregável 2.2.9)
        if hasattr(self, "_pose_lerp_tracker") and self._pose_lerp_tracker["blend_timer"] > 0.0:
            self._pose_lerp_tracker["blend_timer"] = max(0.0, self._pose_lerp_tracker["blend_timer"] - dt)

        if self.combo_window_timer > 0:
            self.combo_window_timer -= dt
        if self.soft_stun_timer > 0:
            self.soft_stun_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Avanço de pressão do combo: 3º golpe projeta Musashi com lunge frontal vigoroso
            step_speed = 3.2 if self.combo_step == 1 else (4.0 if self.combo_step == 2 else 6.2)
            if self.is_roll_cancel:
                step_speed *= 1.20
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt

            # Colisão com obstáculos
            hit_obstacle = False
            for r in getattr(game_map, "rocks", []):
                c, _, _ = r.check_collision(new_wx, new_wy, self.radius)
                if c:
                    hit_obstacle = True
                    break
            if getattr(game_map, "well", None):
                c, _, _ = game_map.well.check_collision(new_wx, new_wy, self.radius)
                if c:
                    hit_obstacle = True

            if hit_obstacle:
                self.stun(0.8)
                self.combo_step = 0
                self.combo_buffered = False
                self.is_roll_cancel = False
                return

            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            self.hitbox_center = (self.wx + self.facing_x * 0.95, self.wy + self.facing_y * 0.95)

            if self.state_timer <= 0:
                self.is_roll_cancel = False
                if self.combo_buffered and self.combo_step < 3:
                    self.combo_step += 1
                    self.combo_buffered = False
                    self.state_timer = 0.18
                    self.hitbox_active = True
                    self.hitbox_radius = 1.62 if self.combo_step == 2 else 2.06
                    try:
                        from src.audio import play_sfx, SoundEvent
                        play_sfx(SoundEvent.SLASH_KATANA, volume_scale=0.95)
                    except Exception:
                        pass

                    if self.combo_step == 3 and projectiles is not None:
                        wave = MusashiWaveProjectile(
                            wx=self.wx + self.facing_x * 0.5,
                            wy=self.wy + self.facing_y * 0.5,
                            wz=0.45,
                            dir_x=self.facing_x,
                            dir_y=self.facing_y,
                            owner=self
                        )
                        projectiles.append(wave)
                else:
                    self.state = STATE_RECOVERY
                    self.state_timer = self.recovery_duration
                    self.combo_window_timer = 0.14
                    self.hitbox_active = False

        elif self.state == "CROSS_SHOCKWAVE":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.hitbox_active = False
                self.current_pose = ""

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.combo_step = 0
                self.combo_buffered = False

        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            self.parry_reflect_active_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.current_pose = ""

        elif self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Samurai Azul no autêntico estilo Voxel 3D Isométrico com SSAA 2x e Pose LERP."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        roll_prog = max(0.0, min(1.0, 1.0 - (self.state_timer / max(0.001, self.roll_duration)))) if self.state == STATE_ROLL else 0.0
        # Rolamento frontal de arte marcial (Mae Ukemi): gira para frente (-360°) rente ao solo
        somersault_angle = (-360.0 * roll_prog) if self.state == STATE_ROLL else 0.0
        somersault_pivot_z = (self.wz + 0.22) if self.state == STATE_ROLL else (self.wz + 0.52)
        render_wz = self.wz
        if self.state == STATE_ROLL:
            # Centro de massa abaixa no início, rola rente ao solo e ergue suavemente com inércia
            if roll_prog < 0.25:
                dip = (roll_prog / 0.25) * 0.12
            elif roll_prog < 0.75:
                dip = 0.12
            else:
                dip = (1.0 - (roll_prog - 0.75) / 0.25) * 0.12
            render_wz = max(0.0, self.wz - dip)

        extra = {
            "combo_step": self.combo_step,
            "ssaa_2x": getattr(self, "ssaa_enabled", True),
            "pose_lerp_tracker": getattr(self, "_pose_lerp_tracker", None),
            "pose": getattr(self, "current_pose", ""),
            "cross_shockwave": (self.state == "CROSS_SHOCKWAVE"),
            "is_roll": (self.state == STATE_ROLL),
            "somersault_angle": somersault_angle,
            "somersault_pivot_z": somersault_pivot_z,
            "roll_prog": roll_prog,
        }

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, render_wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="musashi",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props=extra
        )
