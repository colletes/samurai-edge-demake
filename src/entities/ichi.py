"""
Ichi (A Lâmina Cega / Shikomizue - Ciclo 3 — Overhaul 2.18):
Mestra espadachim cega de audição extraordinária (homenagem à clássica lenda de Zatoichi).
- Arquétipo: Assassina ágil, precisa e sensorial (velocidade 5.1, 2 HP).
- Ataque Primário: Gyaku-Iai Cego (GYAKU_IAI_SLASH) - saque relâmpago em pegada invertida da espada-bengala oculta (alcance 1.80m, raio 1.05m, execução 0.11s, dano 2).
- Ação Secundária: Postura de Escuta Sensorial (LISTEN_STANCE) - postura sensorial de percepção auditiva que concede foco, desvia golpes/projéteis frontais com a bainha de madeira e engatilha contra-ataque perfurante automático letal (Blind Counter-Thrust). Cooldown 3.8s.
- Mobilidade / Terceira Ação: Desvio da Bengala (CANE_TAP_SLIP) - deslize evasivo ágil guiado pelo toque da bengala de cerejeira (13 i-frames) com deslocamento padrão para esquivar de perigos de arena e carruagens.
- Fatalidades: Blind Carotid Slice (盲刃頚断) e Blind Spine Pierce (盲背心貫).
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_ICHI_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, STATE_PARRY, resolve_playable_bounds
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle, FloatingBanner

STATE_LISTEN = "LISTEN"
STATE_COUNTER_THRUST = "COUNTER_THRUST"


class IchiBlade(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Ichi")
        self.char_type = "ichi"
        self.speed = 5.1  # Ágil e fluida
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Ataque Primário: Gyaku-Iai (Saque Relâmpago Invertido estilo Zatoichi puro)
        self.attack_duration = 0.11   # 7 frames de startup ultrarrápido
        self.attack_recovery = 0.20
        self.slash_reach = 1.80
        self.slash_radius = 1.05

        # Ação Secundária: Postura de Escuta & Contra-Ataque Cego
        self.listen_cooldown = 3.8
        self.listen_timer = 0.0
        self.listen_duration = 0.40
        self.counter_active = False

        # Terceira Ação: Desvio Evasivo da Bengala (Cane Tap Slip)
        # Deslocamento padrão com 13 i-frames para evadir carruagens de Kyoto e perigos de arena
        self.is_agile_dodge = True
        self.roll_speed = 7.2
        self.roll_duration = 0.28
        self.roll_recovery_duration = 0.22
        self.roll_cooldown_duration = 0.45
        self.recovery_duration = self.attack_recovery

        # Estilos de Fatalidade Bespoke
        self.finisher_style_primary = "BLIND_CAROTID_SLICE"
        self.finisher_style_secondary = "BLIND_SPINE_PIERCE"

    def trigger_parry(self) -> bool:
        """Parry técnico: bloqueia com a bainha de madeira de cerejeira (Shikomizue)."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.36
        return True

    def is_facing_target(self, target_x: float, target_y: float) -> bool:
        """Verifica se o alvo está no cone frontal de escuta (ângulo < 90°)."""
        dx = target_x - self.wx
        dy = target_y - self.wy
        return (dx * self.facing_x + dy * self.facing_y) > 0.0

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_gyaku_iai(self, aim_x: float, aim_y: float) -> bool:
        """Ataque Primário: Saque relâmpago em pegada invertida da Shikomizue (Opção A)."""
        if not self.can_act():
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.attack_duration
        self.hitbox_active = True
        self.hitbox_damage = 2

        self.hitbox_center = (
            self.wx + self.facing_x * 1.05,
            self.wy + self.facing_y * 1.05
        )
        self.hitbox_radius = self.slash_radius
        self.slash_dir = (self.facing_x, self.facing_y)
        return True

    def trigger_listen_stance(self, aim_x: float = None, aim_y: float = None, banners: list = None, particles: list = None) -> bool:
        """Ação Secundária: Postura de Escuta Sensorial. Foco auditivo que desvia e contra-ataca."""
        if not self.can_act() or self.listen_timer > 0:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)
        self.state = STATE_LISTEN
        self.state_timer = self.listen_duration
        self.listen_timer = self.listen_cooldown
        self.hitbox_active = False
        self.counter_active = True
        self.invincible = True
        self.invincible_timer = self.listen_duration

        if particles is not None:
            # Ondas concêntricas sutis simulando a ecolocalização da bengala
            for ang_deg in range(0, 360, 45):
                rad = math.radians(ang_deg)
                px = self.wx + math.cos(rad) * 0.4
                py = self.wy + math.sin(rad) * 0.4
                particles.append(SparkParticle(px, py, 0.15, color=(210, 225, 250)))

        if banners is not None:
            banners.append(FloatingBanner("LISTEN...", self.wx, self.wy, color=(215, 230, 255), duration=0.65))

        return True

    def trigger_counter_thrust(self, target_x: float, target_y: float, banners: list = None, particles: list = None, cinematic_director = None):
        """Contra-ataque automático perfurante ativado ao interceptar golpe ou projétil na Postura de Escuta."""
        self.set_facing(target_x, target_y)
        self.state = STATE_COUNTER_THRUST
        self.state_timer = 0.20
        self.hitbox_active = True
        self.hitbox_damage = 2

        self.hitbox_center = (
            self.wx + self.facing_x * 1.25,
            self.wy + self.facing_y * 1.25
        )
        self.hitbox_radius = 1.05
        self.slash_dir = (self.facing_x, self.facing_y)
        self.counter_active = False

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx + self.facing_x * 0.8, self.wy + self.facing_y * 0.8, 0.45, color=(255, 250, 220)))

        if banners is not None:
            banners.append(FloatingBanner("BLIND COUNTER!", self.wx, self.wy, color=COLOR_GOLD, duration=0.85))

        try:
            from src.audio.sound_manager import get_sound_manager
            from src.audio.sound_events import SoundEvent
            get_sound_manager().play(SoundEvent.SWORD_SLASH, volume_scale=1.0)
        except Exception:
            pass

    def trigger_cane_slip(self, dwx: float, dwy: float, particles: list = None, game_map = None) -> bool:
        """
        Terceira Ação: Desvio Evasivo da Bengala (Cane Tap Slip).
        Deslize ágil com 13 i-frames (0.22s de invulnerabilidade) em distância padrão
        permitindo escapar de ataques em área, escombros e carruagens de Kyoto.
        """
        if (
            not self.is_alive
            or self.state in (STATE_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK, STATE_RECOVERY, "RYUU_TSUI_SEN", "POLE_VAULT", "PARRY_BACKHOP")
            or getattr(self, "wz", 0.0) > 0.45
            or self.roll_recovery_timer > 0
            or self.roll_cooldown_timer > 0
            or self.dash_recovery_timer > 0
        ):
            return False

        self.wz = 0.0

        # Direção da esquiva
        if abs(dwx) > 0.01 or abs(dwy) > 0.01:
            mag = math.hypot(dwx, dwy)
            dir_x = dwx / mag
            dir_y = dwy / mag
        else:
            dir_x = self.facing_x
            dir_y = self.facing_y

        self.facing_x = dir_x
        self.facing_y = dir_y
        self.state = STATE_ROLL
        self.state_timer = self.roll_duration
        self.is_invulnerable_dodge = True
        self.invincible = True
        self.invincible_timer = 0.22  # 13 frames a 60 FPS
        self.hitbox_active = False

        if particles is not None:
            # Toque da ponta da bengala no chão levantando poeira e faíscas
            particles.append(SparkParticle(self.wx, self.wy, 0.12, color=(185, 175, 160)))
            particles.append(SparkParticle(self.wx + self.facing_x * 0.15, self.wy + self.facing_y * 0.15, 0.15, color=(220, 215, 200)))

        return True

    def trigger_roll(self, dwx: float, dwy: float, particles: list = None, **kwargs) -> bool:
        """Alias para garantir compatibilidade com roll genérico."""
        return self.trigger_cane_slip(dwx, dwy, particles=particles)

    def update(self, dt: float, game_map = None, particles: list = None, opponent = None, projectiles: list = None, banners: list = None, cinematic_director = None, **kwargs):
        # Atualizar timers de esquiva e recuperação de roll
        self.update_dodge_timers(dt)

        # Atualizar recarga da Postura de Escuta
        if self.listen_timer > 0:
            self.listen_timer = max(0.0, self.listen_timer - dt)

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

        # Atualizar ataque primário (Gyaku-Iai)
        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Lunge veloz do saque em pegada invertida
            step_speed = 3.8
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map and hasattr(game_map, "cols"):
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.05,
                self.wy + self.facing_y * 1.05
            )
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.attack_recovery
                self.hitbox_active = False
            return

        # Atualizar Postura de Escuta Sensorial
        if self.state == STATE_LISTEN:
            self.state_timer -= dt

            # 1. Interceptar e contra-atacar golpes inimigos
            if self.counter_active and opponent and getattr(opponent, "is_alive", False):
                opp_attacking = (
                    getattr(opponent, "hitbox_active", False)
                    or getattr(opponent, "state", "") in (
                        "ATTACK", "RYUU_TSUI_SEN", "GATOTSU_CHARGE", "ZEROSHIKI",
                        "CUTLASS_CLEAVE", "FLECHE", "KIAI", "MAI_DANCE", "POLE_VAULT",
                        "TACHIAI_TACKLE", "TSUPPARI_RUSH", "TSUPPARI_STRIKE_1", "TSUPPARI_STRIKE_2"
                    )
                )
                dist_opp = math.hypot(opponent.wx - self.wx, opponent.wy - self.wy)
                if opp_attacking and dist_opp <= 2.2 and self.is_facing_target(opponent.wx, opponent.wy):
                    # Aparar e interromper o oponente com a bainha de madeira
                    opponent.hitbox_active = False
                    opponent.state = STATE_RECOVERY
                    opponent.state_timer = 0.35
                    if particles is not None:
                        for _ in range(6):
                            particles.append(SparkParticle(self.wx + self.facing_x * 0.6, self.wy + self.facing_y * 0.6, 0.35, color=(240, 230, 200)))
                    self.trigger_counter_thrust(opponent.wx, opponent.wy, banners=banners, particles=particles, cinematic_director=cinematic_director)
                    return

            # 2. Interceptar e rebater projéteis frontais
            if self.counter_active and projectiles:
                for pr in projectiles:
                    if not getattr(pr, "is_active", True):
                        continue
                    p_dx = pr.wx - self.wx
                    p_dy = pr.wy - self.wy
                    p_dist = math.hypot(p_dx, p_dy)
                    if p_dist <= 1.8 and (p_dx * self.facing_x + p_dy * self.facing_y) > 0:
                        pr.is_active = False
                        if particles is not None:
                            particles.append(SparkParticle(pr.wx, pr.wy, 0.40, color=(255, 230, 180)))
                        tgt_x = opponent.wx if (opponent and opponent.is_alive) else (self.wx + self.facing_x * 2.0)
                        tgt_y = opponent.wy if (opponent and opponent.is_alive) else (self.wy + self.facing_y * 2.0)
                        self.trigger_counter_thrust(tgt_x, tgt_y, banners=banners, particles=particles, cinematic_director=cinematic_director)
                        return

            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.counter_active = False
                self.invincible = False
            return

        elif self.state == STATE_COUNTER_THRUST:
            self.state_timer -= dt
            # Estocada perfurante instantânea
            step_speed = 4.5
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map and hasattr(game_map, "cols"):
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.25,
                self.wy + self.facing_y * 1.25
            )
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.16
                self.hitbox_active = False
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
        if self.state == STATE_LISTEN:
            extra = {"pose": "listen_stance", "is_listen": True}
        elif self.state == STATE_COUNTER_THRUST:
            extra = {"pose": "counter_thrust", "is_pierce": True}
        elif self.state == STATE_ROLL:
            roll_p = 1.0 - (self.state_timer / max(0.001, self.roll_duration))
            extra = {"pose": "cane_slip", "is_roll": True, "roll_prog": roll_p}
        elif self.state == STATE_PARRY:
            extra = {"pose": "sheath_parry", "is_parry": True}

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
            char_type="ichi",
            walk_timer=getattr(self, "walk_cycle", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
