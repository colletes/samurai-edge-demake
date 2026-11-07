"""
Goro (O Fazendeiro da Kuwa - Ciclo 3):
Camponês e líder rebelde da era Bakumatsu.
- Arquétipo: Lutador pesado e telúrico (velocidade 4.85, 2 HP).
- Guarda de Ferro: Parry técnico com a haste de carvalho e lâmina de ferro forjado.
- Ataque Primário: Corte da Kuwa (KUWA_CLEAVE) - golpe vertical com hiper-inércia (alcance 2.40m, raio 1.30m) e quebra de guarda.
- Ação Secundária: Pisotão Sísmico (EARTH_STOMP) - onda de choque linear/cônica que racha o solo, empurra rivais e inflige STUN (0.80s).
- Terceira Ação / Mobilidade: Rolamento de Lavrador (MUD_ROLL) com 13 i-frames e cancelamento em Pocket Dirt (0.22s micro-stun).
- Fatalidades: KUWA_SKULL_CLEAVE e SEISMIC_RUPTURE.
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
STATE_POCKET_DIRT = "POCKET_DIRT"


class GoroFarmer(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Goro")
        self.char_type = "goro"
        self.speed = 4.85  # Movimentação ágil e impetuosa de camponês rebelde
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Fatalidades Cinematográficas
        self.finisher_style_primary = "KUWA_SKULL_CLEAVE"
        self.finisher_style_secondary = "EARTH_STOMP_CRUSH"

        # Ataque Primário: Descida da Kuwa (Hiper-Inércia & Quebra de Guarda)
        self.cleave_duration = 0.22
        self.cleave_recovery = 0.20
        self.cleave_reach = 2.40
        self.cleave_radius = 1.30
        self.cleave_timer = 0.0
        self.is_guard_break = False

        # Ação Secundária: Pisotão Sísmico
        self.stomp_cooldown = 2.2
        self.stomp_timer = 0.0
        self.stomp_duration = 0.20
        self.active_shockwaves: list[EarthStompShockwave] = []

        # Terceira Ação: Rolamento de Lavrador (Peasant Mud Roll)
        self.is_agile_dodge = False
        self.roll_speed = 8.6
        self.roll_duration = 0.216  # 13 frames a 60 FPS
        self.roll_recovery_duration = 0.16
        self.roll_cooldown_duration = 0.36
        self.recovery_duration = self.cleave_recovery
        self.action_name = "Corte da Kuwa"

        # Mecânica Especial: Pocket Dirt (Cancelamento do Rolamento)
        self.pocket_dirt_cooldown = 1.8
        self.pocket_dirt_timer = 0.0
        self.pocket_dirt_duration = 0.22

    def trigger_parry(self) -> bool:
        """Guarda de Ferro: ergue a Kuwa e o cabo reforçado para aparar golpes e flechas."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.40
        self.action_name = "Guarda de Ferro"
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

    def trigger_kuwa_cleave(self, aim_x: float = None, aim_y: float = None) -> bool:
        """Ataque Primário: Golpe descendente demolidor com a Kuwa de aço (alcance 2.40m e quebra de guarda)."""
        if not self.can_act():
            return False

        if aim_x is None or aim_y is None:
            aim_x, aim_y = self.facing_x, self.facing_y

        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.cleave_duration
        self.hitbox_active = True
        self.hitbox_damage = 2
        self.is_guard_break = True
        self.action_name = "Corte da Kuwa"

        # Centro da hitbox à frente
        self.hitbox_center = (
            self.wx + self.facing_x * 1.35,
            self.wy + self.facing_y * 1.35
        )
        self.hitbox_radius = self.cleave_radius
        self.slash_dir = (self.facing_x, self.facing_y)
        return True

    def trigger_attack(self, aim_x: float = None, aim_y: float = None, **kwargs) -> bool:
        """Interface universal de ataque primário."""
        return self.trigger_kuwa_cleave(aim_x, aim_y)

    def trigger_earth_stomp(self, aim_x: float = None, aim_y: float = None, shockwaves: list = None, particles: list = None, banners: list = None, opponent = None, game_map = None) -> bool:
        """Ação Secundária: Pisotão Sísmico. Racha o solo, gera onda expansiva e atordoa oponentes em 4.2m."""
        if not self.can_act() or self.stomp_timer > 0:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        self.state = STATE_EARTH_STOMP
        self.state_timer = self.stomp_duration
        self.stomp_timer = self.stomp_cooldown
        self.hitbox_active = False
        self.action_name = "Pisotão Sísmico"

        # Criar onda de choque sísmica frontal em 120 graus (alcance 4.2m, rápida, com 1 de dano e anula projéteis)
        wave = EarthStompShockwave(self.wx, self.wy, owner=self, facing=(self.facing_x, self.facing_y), max_radius=4.2, duration=0.30)
        if shockwaves is not None:
            shockwaves.append(wave)
        self.active_shockwaves.append(wave)

        # Repulsão e stun direto se o oponente estiver na área de impacto
        if opponent and getattr(opponent, "is_alive", True):
            dx = opponent.wx - self.wx
            dy = opponent.wy - self.wy
            dist = math.hypot(dx, dy)
            if dist <= 4.2:
                # Checa ângulo frontal
                ndx, ndy = (dx / dist, dy / dist) if dist > 0.001 else (self.facing_x, self.facing_y)
                dot = ndx * self.facing_x + ndy * self.facing_y
                if dot > 0.25:  # cone frontal
                    if hasattr(opponent, "stun"):
                        opponent.stun(0.80)
                    if hasattr(opponent, "apply_forced_displacement"):
                        opponent.apply_forced_displacement(ndx * 2.2, ndy * 2.2, game_map)
                    if banners is not None:
                        banners.append(FloatingBanner("EARTHQUAKE STUN!", opponent.wx, opponent.wy, wz=1.75, color=COLOR_GOLD))

        if particles is not None:
            for _ in range(16):
                particles.append(SparkParticle(self.wx, self.wy, 0.40, color=(165, 130, 85)))

        if banners is not None:
            banners.append(FloatingBanner("PISOTÃO SÍSMICO!", self.wx, self.wy, color=COLOR_GOLD, duration=0.85))

        return True

    def trigger_mud_roll(self, dwx: float, dwy: float, particles: list = None, game_map = None) -> bool:
        """Terceira Ação: Rolamento de Lavrador com 13 i-frames completos."""
        if not self.is_alive or self.state in (STATE_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK):
            return False
        if self.roll_cooldown_timer > 0:
            return False

        dist = math.hypot(dwx, dwy)
        if dist > 0.05:
            self.facing_x = dwx / dist
            self.facing_y = dwy / dist

        self.state = STATE_ROLL
        self.state_timer = self.roll_duration
        self.invincible_timer = 13.0 / 60.0
        self.is_invulnerable_dodge = True
        self.invulnerable = True
        self.hitbox_active = False
        self.action_name = "Rolamento de Lama"

        if particles is not None:
            for _ in range(10):
                particles.append(SparkParticle(self.wx, self.wy, 0.28, color=(110, 80, 50)))
        return True

    def trigger_roll(self, dwx: float, dwy: float, particles: list = None, **kwargs) -> bool:
        """Compatibilidade com interface padrão Samurai."""
        return self.trigger_mud_roll(dwx, dwy, particles=particles)

    def trigger_pocket_dirt(self, opponent = None, particles: list = None, banners: list = None, game_map = None) -> bool:
        """Cancelamento da Esquiva: Lança um punhado de terra/cascalho no rosto do rival (micro-stun 0.22s)."""
        if not self.is_alive or self.state not in (STATE_ROLL, STATE_WALK, STATE_IDLE):
            return False
        if self.pocket_dirt_timer > 0:
            return False

        self.state = STATE_POCKET_DIRT
        self.state_timer = self.pocket_dirt_duration
        self.pocket_dirt_timer = self.pocket_dirt_cooldown
        self.is_invulnerable_dodge = False
        self.invulnerable = False
        self.action_name = "Pocket Dirt"

        hit = False
        if opponent and getattr(opponent, "is_alive", True):
            dx = opponent.wx - self.wx
            dy = opponent.wy - self.wy
            dist = math.hypot(dx, dy)
            if dist <= 1.60:
                dot = (dx * self.facing_x + dy * self.facing_y) / (dist or 1.0)
                if dot > 0.20:
                    hit = True
                    if hasattr(opponent, "stun"):
                        opponent.stun(0.22)
                    if hasattr(opponent, "is_blinded"):
                        opponent.is_blinded = True
                    if banners is not None:
                        banners.append(FloatingBanner("POCKET DIRT!", opponent.wx, opponent.wy, wz=1.65, color=(185, 145, 95)))

        if particles is not None:
            for _ in range(14):
                particles.append(SparkParticle(self.wx + self.facing_x * 0.45, self.wy + self.facing_y * 0.45, 0.32, color=(145, 115, 80)))
        return True

    def update_roll(self, dt: float, game_map, particles: list = None):
        """Atualização da movimentação rente ao solo do rolamento."""
        if self.state != STATE_ROLL:
            return
        self.state_timer -= dt
        if hasattr(self, "invincible_timer") and self.invincible_timer > 0:
            self.invincible_timer = max(0.0, self.invincible_timer - dt)
            if self.invincible_timer <= 0:
                self.is_invulnerable_dodge = False
                self.invulnerable = False

        # Deslocamento do rolamento
        speed = self.roll_speed
        new_wx = self.wx + self.facing_x * speed * dt
        new_wy = self.wy + self.facing_y * speed * dt
        if game_map and hasattr(game_map, "cols"):
            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
        else:
            self.wx, self.wy = new_wx, new_wy

        if self.state_timer <= 0:
            self.state = STATE_RECOVERY
            self.state_timer = self.roll_recovery_duration
            self.roll_cooldown_timer = self.roll_cooldown_duration
            self.is_invulnerable_dodge = False
            self.invulnerable = False

    def update(self, dt: float, game_map = None, particles: list = None, opponent = None, projectiles: list = None, banners: list = None, **kwargs):
        # Timers universais de esquiva
        self.update_dodge_timers(dt)

        if self.stomp_timer > 0:
            self.stomp_timer = max(0.0, self.stomp_timer - dt)
        if self.pocket_dirt_timer > 0:
            self.pocket_dirt_timer = max(0.0, self.pocket_dirt_timer - dt)

        # Atualizar rolamento se em estado ROLL
        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            return

        # 1. Atordoamento
        if self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # 2. Cancelamento em Pocket Dirt
        if self.state == STATE_POCKET_DIRT:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.08
            return

        # 3. Ataque Primário (Kuwa Cleave)
        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            step_speed = 2.4
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map and hasattr(game_map, "cols"):
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.35,
                self.wy + self.facing_y * 1.35
            )
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.cleave_recovery
                self.hitbox_active = False
                self.is_guard_break = False
            return

        # 4. Pisotão Sísmico
        if self.state == STATE_EARTH_STOMP:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.12
            return

        # 5. Recuperação
        if self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # 6. Guarda / Parry
        if self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # 7. Ondas ativas de choque
        if self.active_shockwaves:
            fighters = [self]
            if opponent:
                fighters.append(opponent)
            self.active_shockwaves = [
                w for w in self.active_shockwaves
                if w.update(dt, game_map=game_map, particles=particles, fighters=fighters, projectiles=projectiles)
            ]

    def get_extra_props(self) -> dict:
        extra = super().get_extra_props()
        if self.state == STATE_EARTH_STOMP:
            extra.update({"is_stomp": True, "pose": "earth_stomp"})
        elif self.state == STATE_POCKET_DIRT:
            extra.update({"is_pocket_dirt": True, "pose": "pocket_dirt"})
        elif self.state == STATE_ROLL:
            dur = self.roll_duration or 0.22
            p = 1.0 - max(0.0, self.state_timer / dur)
            extra.update({"is_mud_roll": True, "pose": "mud_roll", "roll_prog": p})
        elif self.state in ("DEFEND", "PARRY") or getattr(self, "is_parrying", False):
            extra.update({"pose": "iron_guard"})
        extra["action_name"] = getattr(self, "action_name", "")
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
            char_type="goro",
            walk_timer=getattr(self, "walk_cycle", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
