"""
Ninja Amarelo (Hanzo): Mestre furtivo de artes ninjas de Iga (Sub-fase 2.3 Overhaul).
- Botão 1: Combo Melee ágil de 2 tempos com Ninjato invertida (Reverse Slash + Solar Plexus Thrust).
- Botão 2: Kunai Snipe de alta velocidade (horizontal no solo; mergulho íngreme vz=-6.5 no ar).
- Botão 3: Salto Ninja Acrobático Parabólico (wz até 1.35m) sem zanzou e com cancelamento ofensivo (Landing Cancel).
- Anti-Floating: Queda imediata (wz = 0.0) se sofrer parry no ar.
- Finishers duplos: HEART_THROAT_STAB (Ninjato Melee) & FOREHEAD_PIN (Kunai Snipe).
- SSAA 2x Offscreen Buffer e Pose LERP 0.08s contínua.
"""
import math
import pygame
from src.config import (
    COLOR_YELLOW_NINJA, COLOR_YELLOW_DARK, COLOR_NINJA_MASK,
    COLOR_YELLOW_AURA, COLOR_STEEL, COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_ROLL
)
from src.entities.projectile import KunaiProjectile
from src.entities.voxel_models import render_voxel_humanoid
from src.audio.sound_manager import play_sfx, SoundEvent

class YellowNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Hanzo")
        self.char_type = "ninja"
        self.speed = 5.4  # Mobilidade de elite ninja

        # Atributos de Kunai Snipe (Botão 2)
        self.has_kunai = True
        self.kunai_cooldown = 1.5
        self.kunai_timer = 0.0

        # Combo Melee com Ninjato (Botão 1)
        self.combo_step = 0            # 0: Nenhum, 1: Reverse Slash, 2: Solar Plexus Thrust
        self.combo_buffered = False
        self.combo_window_timer = 0.0
        self.combo_window_duration = 0.40
        self.is_landing_cancel = False

        # Durações dos ataques
        self.slash_duration = 0.11
        self.thrust_duration = 0.13
        self.recovery_duration = 0.12
        self.thrust_step = 4.8

        # Salto Ninja Acrobático Parabólico (Botão 3)
        self.jump_duration = 0.48
        self.jump_max_height = 1.35
        self.jump_speed = 6.4
        self.jump_dir = (1.0, 0.0)
        self.jump_cooldown = 0.35
        self.jump_cooldown_timer = 0.0
        self.is_midair_dash = False
        self.has_thrown_in_jump = False
        self.auto_throw_in_jump = False
        self._throw_target = (0.0, 0.0)
        self._throw_projectiles = None
        self.is_landing_from_jump = False

        # Compatibilidade com esquiva/roll (sem zanzou)
        self.is_agile_dodge = True
        self.roll_speed = 9.6
        self.roll_duration = 0.20
        self.roll_recovery_duration = 0.12
        self.roll_cooldown_duration = 0.35

        # Qualidade Visual & Fluidez (SSAA 2x + Pose LERP 0.08s — Entregável 2.3.9)
        self.ssaa_enabled = True
        self._pose_lerp_tracker = {
            "lerp_duration": 0.08,
            "blend_timer": 0.0,
            "pose_key": None,
            "prev_snap": None,
            "last_snap": None,
            "transitions_count": 0,
        }

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def can_cancel_jump(self) -> bool:
        """Verifica se está nos 40% finais da aterrissagem do salto ninja (Landing Cancel)."""
        if self.state == "JUMP" and self.state_timer <= (self.jump_duration * 0.40):
            return True
        if self.state == STATE_RECOVERY and self.is_landing_from_jump:
            return True
        return False

    # -------------------------------------------------------------------------
    # Botão 1: Combo Melee Ninjato (Reverse Slash + Solar Plexus Thrust)
    # -------------------------------------------------------------------------
    def trigger_combo_attack(self, target_wx: float, target_wy: float):
        """
        Dispara ou encadeia o combo ágil de 2 tempos da Ninjato com empunhadura invertida:
        - Passo 1: Corte horizontal reverso (Reverse Slash, raio 1.30m, 1 de dano).
        - Passo 2: Estocada fulminante no plexo solar com avanço rápido (raio 1.45m, 2 de dano).
        - Landing Cancel: se acionado na aterrissagem do salto, cancela o lag em corte imediato!
        """
        if not self.is_alive or self.state in (STATE_DEAD, STATE_STUNNED, STATE_ROLL):
            return False

        # 1. Landing Cancel do Salto Ninja nos 40% finais
        if self.can_cancel_jump():
            self.wz = 0.0
            self.is_landing_from_jump = False
            self.is_landing_cancel = True
            self.state = STATE_ATTACK
            self.combo_step = 2  # Entra direto na estocada veloz com avanço
            self.combo_buffered = False
            self.combo_window_timer = 0.0
            self.set_facing(target_wx, target_wy)
            self.state_timer = self.thrust_duration
            self.hitbox_active = True
            self.hitbox_damage = 2
            self.hitbox_radius = 1.45
            self.slash_dir = (self.facing_x, self.facing_y)
            self.hitbox_center = (self.wx + self.facing_x * 1.15, self.wy + self.facing_y * 1.15)
            play_sfx(SoundEvent.SWORD_SLASH)
            return True

        # 2. Buffer durante o Passo 1 para transição imediata ao Passo 2
        if self.state == STATE_ATTACK and self.combo_step == 1:
            self.combo_buffered = True
            return True

        # 3. Execução a partir de Idle/Walk ou na janela de combo
        if self.can_act() or (self.state == STATE_RECOVERY and self.combo_window_timer > 0.0 and self.combo_step == 1):
            next_step = 2 if (self.combo_step == 1 and self.combo_window_timer > 0.0) else 1
            self.set_facing(target_wx, target_wy)
            self.state = STATE_ATTACK
            self.combo_step = next_step
            self.combo_buffered = False
            self.combo_window_timer = 0.0
            self.is_landing_cancel = False

            if next_step == 1:
                self.state_timer = self.slash_duration
                self.hitbox_active = True
                self.hitbox_damage = 1
                self.hitbox_radius = 1.30
                self.slash_dir = (self.facing_x, self.facing_y)
                self.hitbox_center = (self.wx + self.facing_x * 0.95, self.wy + self.facing_y * 0.95)
                play_sfx(SoundEvent.SWORD_SLASH)
            else:
                self.state_timer = self.thrust_duration
                self.hitbox_active = True
                self.hitbox_damage = 2
                self.hitbox_radius = 1.45
                self.slash_dir = (self.facing_x, self.facing_y)
                self.hitbox_center = (self.wx + self.facing_x * 1.15, self.wy + self.facing_y * 1.15)
                play_sfx(SoundEvent.SWORD_SLASH)
            return True

        return False

    def trigger_thrust_attack(self, target_wx: float, target_wy: float):
        """Compatibilidade: direciona para o combo melee."""
        return self.trigger_combo_attack(target_wx, target_wy)

    # -------------------------------------------------------------------------
    # Botão 2: Kunai Snipe (Solo e Mid-Air)
    # -------------------------------------------------------------------------
    def trigger_kunai_snipe(self, target_wx: float, target_wy: float, projectiles: list):
        """
        Ação Secundária: Kunai Snipe de alta precisão e velocidade (24 m/s).
        - No solo: tiro tenso horizontal (vz = 0.0).
        - No ar (durante JUMP): arremesso íngreme descendente (vz = -6.5).
        """
        if not self.is_alive or not self.has_kunai or self.state in (STATE_DEAD, STATE_STUNNED, STATE_ROLL):
            return False

        # Mid-air throw durante salto
        if self.state == "JUMP":
            if self.has_thrown_in_jump:
                return False
            self.set_facing(target_wx, target_wy)
            self.has_kunai = False
            self.has_thrown_in_jump = True
            self.kunai_timer = self.kunai_cooldown

            kunai = KunaiProjectile(
                wx=self.wx + self.facing_x * 0.35,
                wy=self.wy + self.facing_y * 0.35,
                wz=max(0.40, self.wz),
                dir_x=self.facing_x,
                dir_y=self.facing_y,
                owner=self,
                vz=-6.5,
                max_range=3.5
            )
            projectiles.append(kunai)
            play_sfx(SoundEvent.KUNAI_THROW)
            return True

        # Standing throw no solo
        if not self.can_act():
            return False

        self.set_facing(target_wx, target_wy)
        self.has_kunai = False
        self.kunai_timer = self.kunai_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.10

        kunai = KunaiProjectile(
            wx=self.wx + self.facing_x * 0.40,
            wy=self.wy + self.facing_y * 0.40,
            wz=0.45,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self,
            vz=0.0,
            max_range=6.8
        )
        projectiles.append(kunai)
        play_sfx(SoundEvent.KUNAI_THROW)
        return True

    def trigger_standing_throw(self, target_wx: float, target_wy: float, projectiles: list):
        """Compatibilidade: disparo em pé."""
        return self.trigger_kunai_snipe(target_wx, target_wy, projectiles)

    def trigger_midair_throw(self, target_wx: float, target_wy: float, projectiles: list):
        """Compatibilidade: disparo aéreo."""
        return self.trigger_kunai_snipe(target_wx, target_wy, projectiles)

    def trigger_throw_attack(self, target_wx: float, target_wy: float, projectiles: list):
        """Compatibilidade legada."""
        return self.trigger_kunai_snipe(target_wx, target_wy, projectiles)

    def trigger_jump_and_throw(self, target_wx: float, target_wy: float, projectiles: list):
        """Compatibilidade: salto seguido de arremesso."""
        if self.trigger_jump(target_wx, target_wy, projectiles):
            self.auto_throw_in_jump = True
            self._throw_target = (target_wx, target_wy)
            self._throw_projectiles = projectiles

    # -------------------------------------------------------------------------
    # Botão 3: Salto Ninja Acrobático Parabólico (Evasão Dedicada)
    # -------------------------------------------------------------------------
    def trigger_jump(self, dir_x: float, dir_y: float, projectiles: list | None = None):
        """
        Terceira Ação / Mobilidade: Salto acrobático parabólico no ar (wz até 1.35m).
        Desvia inteiramente de golpes no solo (wz < 0.40m).
        Permite disparar kunai descendente em pleno ar e cancelamento ofensivo na aterrissagem.
        """
        if not self.is_alive or self.jump_cooldown_timer > 0.0 or self.state in (STATE_DEAD, STATE_STUNNED, "JUMP"):
            return False

        # Se executado durante o combo ou recovery de combo, cancela para fuga ágil
        mag = math.hypot(dir_x, dir_y)
        if mag > 0.01:
            self.facing_x = dir_x / mag
            self.facing_y = dir_y / mag
        self.jump_dir = (self.facing_x, self.facing_y)

        self.state = "JUMP"
        self.state_timer = self.jump_duration
        self.has_thrown_in_jump = False
        self.auto_throw_in_jump = False
        self.hitbox_active = False
        self.is_landing_from_jump = False
        self.is_landing_cancel = False
        self.combo_step = 0
        self.combo_buffered = False
        play_sfx(SoundEvent.DASH_ROLL)
        return True

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None):
        """Mapeia rolamento / esquiva padrão para o Salto Ninja Acrobático."""
        return self.trigger_jump(dir_x, dir_y)

    # -------------------------------------------------------------------------
    # Resposta a Parry (Diretiva Crítica: Zero Flutuação no Ar)
    # -------------------------------------------------------------------------
    def on_parried(self, opponent=None, game_map=None, banners=None, particles=None):
        """
        Quando Hanzo sofre parry (seja no chão ou no ar), o ninja cai IMEDIATAMENTE no solo.
        Reseta wz = 0.0, cancela qualquer salto pendente e entra em recuo de atordoamento.
        """
        self.wz = 0.0
        self.is_midair_dash = False
        self.hitbox_active = False
        self.combo_step = 0
        self.combo_buffered = False
        self.is_landing_from_jump = False
        self.is_landing_cancel = False
        self.stun(0.85)

    # -------------------------------------------------------------------------
    # Fatalities Bespoke (Melee HEART_THROAT_STAB e Ranged FOREHEAD_PIN)
    # -------------------------------------------------------------------------
    def trigger_finisher_a(self, opponent, cd):
        """Finisher 1 (Melee Ninjato): Estocada invertida transpassando garganta/coração."""
        if cd:
            return cd.trigger_fatal_strike(self, opponent, "HEART_THROAT_STAB", (self.facing_x, self.facing_y))

    def trigger_finisher_b(self, opponent, cd):
        """Finisher 2 (Kunai Snipe): Salto ágil sobre a vítima com kunai cravada na testa."""
        if cd:
            return cd.trigger_fatal_strike(self, opponent, "FOREHEAD_PIN", (self.facing_x, self.facing_y))

    # -------------------------------------------------------------------------
    # Atualização da Lógica & Cinemática
    # -------------------------------------------------------------------------
    def update(self, dt: float, game_map, projectiles: list | None = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)
        self.update_dodge_timers(dt)

        # Atualizar cronômetro do Pose LERP (Entregável 2.3.9)
        if hasattr(self, "_pose_lerp_tracker") and self._pose_lerp_tracker["blend_timer"] > 0.0:
            self._pose_lerp_tracker["blend_timer"] = max(0.0, self._pose_lerp_tracker["blend_timer"] - dt)

        # Recarga da Kunai
        if not self.has_kunai:
            self.kunai_timer -= dt
            if self.kunai_timer <= 0.0:
                self.has_kunai = True

        # Cooldown do Salto Ninja
        if self.jump_cooldown_timer > 0.0:
            self.jump_cooldown_timer -= dt

        # Janela de combo
        if self.combo_window_timer > 0.0:
            self.combo_window_timer -= dt
            if self.combo_window_timer <= 0.0 and self.state != STATE_ATTACK:
                self.combo_step = 0

        # Física do Salto Ninja
        if self.state == "JUMP":
            self.state_timer -= dt
            progress = max(0.0, min(1.0, 1.0 - (self.state_timer / self.jump_duration)))
            self.wz = math.sin(progress * math.pi) * self.jump_max_height

            # Arremesso automático se configurado
            if self.auto_throw_in_jump and not self.has_thrown_in_jump and self.has_kunai and progress >= 0.28:
                if self._throw_projectiles is not None:
                    self.trigger_midair_throw(self._throw_target[0], self._throw_target[1], self._throw_projectiles)

            # Deslocamento no ar
            new_wx = self.wx + self.jump_dir[0] * self.jump_speed * dt
            new_wy = self.wy + self.jump_dir[1] * self.jump_speed * dt

            # Colisão apenas rente ao chão
            hit_obstacle = False
            if self.wz < 0.40:
                for r in game_map.rocks:
                    c, _, _ = r.check_collision(new_wx, new_wy, self.radius)
                    if c:
                        hit_obstacle = True
                        break
                if game_map.well:
                    c, _, _ = game_map.well.check_collision(new_wx, new_wy, self.radius)
                    if c:
                        hit_obstacle = True

            if not hit_obstacle:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            # Fim do salto
            if self.state_timer <= 0.0:
                self.wz = 0.0
                self.state = STATE_RECOVERY
                self.state_timer = 0.16  # Landing lag
                self.is_landing_from_jump = True
                self.jump_cooldown_timer = self.jump_cooldown
                self.has_thrown_in_jump = False
                self.auto_throw_in_jump = False

        # Estado de Ataque Melee
        elif self.state == STATE_ATTACK:
            self.state_timer -= dt

            # Deslocamento / impulso
            thrust_speed = self.thrust_step if (self.combo_step == 2 or self.is_landing_cancel) else 1.8
            new_wx = self.wx + self.facing_x * thrust_speed * dt
            new_wy = self.wy + self.facing_y * thrust_speed * dt

            # Colisão com rochas/poço
            hit_obstacle = False
            for r in game_map.rocks:
                c, _, _ = r.check_collision(new_wx, new_wy, self.radius)
                if c:
                    hit_obstacle = True
                    break
            if game_map.well:
                c, _, _ = game_map.well.check_collision(new_wx, new_wy, self.radius)
                if c:
                    hit_obstacle = True

            if hit_obstacle:
                self.stun(0.60)
                self.combo_step = 0
                self.combo_buffered = False
                return

            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            reach = 1.15 if (self.combo_step == 2 or self.is_landing_cancel) else 0.95
            self.hitbox_center = (self.wx + self.facing_x * reach, self.wy + self.facing_y * reach)

            # Transição ao expirar o tempo de ataque
            if self.state_timer <= 0.0:
                self.hitbox_active = False
                # Encadeia o passo 2 se estiver bufferizado
                if self.combo_step == 1 and self.combo_buffered:
                    self.state = STATE_ATTACK
                    self.combo_step = 2
                    self.combo_buffered = False
                    self.state_timer = self.thrust_duration
                    self.hitbox_active = True
                    self.hitbox_damage = 2
                    self.hitbox_radius = 1.45
                    self.slash_dir = (self.facing_x, self.facing_y)
                    self.hitbox_center = (self.wx + self.facing_x * 1.15, self.wy + self.facing_y * 1.15)
                    play_sfx(SoundEvent.SWORD_SLASH)
                else:
                    self.state = STATE_RECOVERY
                    self.state_timer = self.recovery_duration
                    if self.combo_step == 1:
                        self.combo_window_timer = self.combo_window_duration
                    else:
                        self.combo_step = 0
                        self.combo_buffered = False

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0.0:
                self.state = STATE_IDLE
                self.is_landing_from_jump = False
                self.is_landing_cancel = False

        elif self.state == STATE_ROLL:
            self.update_roll(dt, game_map)

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0.0:
                self.state = STATE_IDLE
                self.combo_step = 0
                self.combo_buffered = False

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Ninja Amarelo (Hanzo) no padrão Proposta 2A com SSAA 2x e Pose LERP."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        extra = {
            "has_kunai": self.has_kunai,
            "combo_step": self.combo_step,
            "is_landing_cancel": self.is_landing_cancel,
            "ssaa_2x": getattr(self, "ssaa_enabled", True),
            "pose_lerp_tracker": getattr(self, "_pose_lerp_tracker", None),
            "pose": getattr(self, "current_pose", ""),
            "is_jumping": (self.state == "JUMP"),
        }

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="ninja",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props=extra
        )
