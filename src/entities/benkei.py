"""
Benkei (O Guardião da Naginata / Walking Tank Colossal):
Monge guerreiro sōhei colossal e inabalável.
- Velocidade pesada (4.0).
- Sem parry técnico (can_parry = False); foco em alcance colossal e solidez de tanque.
- Ataque Primário: Estocada frontal colossal de Naginata (alcance 3.0 tiles, alto knockback).
- Ataque Secundário: Arremesso de Naginata a longa distância; crava no solo sem jamais cair em buracos ou água.
- Desarmado: Ataque vira Investida com Guarda Alta (Tackle) de alta velocidade que causa 0 dano mas aplica STUN garantido (1.2s) e recupera a arma.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_BENKEI_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, resolve_playable_bounds
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import NaginataProjectile
from src.effects.particles import SparkParticle, FloatingBanner

STATE_NAGINATA_THROW = "NAGINATA_THROW"
STATE_TACKLE_CHARGE = "TACKLE_CHARGE"


class BenkeiSamurai(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Benkei")
        self.char_type = "benkei"
        self.speed = 4.0  # Walking Tank (movimentação pesada e sólida)
        self.max_hp = 2
        self.hp = 2
        self.can_parry = False  # Sem parry técnico por design

        # Estado da Naginata
        self.has_naginata = True
        self.active_naginata_projectile = None

        # Parâmetros da Estocada Primária (Colossal Thrust)
        self.thrust_duration = 0.22  # Duração acelerada (era 0.28s) para maior responsividade
        self.thrust_reach = 3.2
        self.thrust_radius = 1.45
        self.thrust_recovery = 0.28  # Recovery calibrado (era 0.38s)
        self.thrust_timer = 0.0

        # Parâmetros do Arremesso Secundário
        self.throw_duration = 0.22
        self.throw_cooldown = 1.8
        self.throw_timer = 0.0

        # Parâmetros do Atropelamento / Tackle Desarmado
        self.tackle_speed = 10.5
        self.tackle_duration = 0.38
        self.tackle_timer = 0.0
        self.tackle_dir_x = 1.0
        self.tackle_dir_y = 0.0
        self.tackle_hit_target = False

        # Esquiva pesada de blindado
        self.is_agile_dodge = False
        self.roll_speed = 8.0
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.20
        self.roll_cooldown_duration = 0.42
        self.recovery_duration = self.thrust_recovery

    def take_hit(self, slash_dir: tuple[float, float], damage: int = 2) -> tuple[bool, bool]:
        """Aplica dano ao Benkei com Hyper Armor durante o Tackle Charge contra ataques leves."""
        if not self.is_alive:
            return False, False
        # Hyper Armor no Tackle Charge: ataques de 1 de dano não interrompem a investida
        if self.state == STATE_TACKLE_CHARGE and damage < 2 and self.hp > 1:
            self.hp -= damage
            return True, False
        return super().take_hit(slash_dir, damage)

    @property
    def is_unarmed(self) -> bool:
        """Indica se Benkei arremessou a Naginata e está lutando desarmado."""
        return not self.has_naginata

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_naginata_thrust(self, aim_x: float, aim_y: float):
        """Ataque Primário com Naginata ou Investida Desarmada."""
        if not self.can_act():
            return False

        if not self.has_naginata:
            # Desarmado: Tackle de atropelamento com stun
            return self.trigger_tackle_charge(aim_x, aim_y)

        # Estocada colossal armada
        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.thrust_duration
        self.hitbox_active = True
        self.hitbox_damage = 2

        # Centro da hitbox a 1.90 tiles à frente com raio 1.45 tiles (alcance total ~3.35 tiles)
        self.hitbox_center = (
            self.wx + self.facing_x * 1.90,
            self.wy + self.facing_y * 1.90
        )
        self.hitbox_radius = self.thrust_radius
        self.slash_dir = (self.facing_x, self.facing_y)
        return True

    def trigger_naginata_throw(self, aim_x: float, aim_y: float, projectiles: list, particles: list = None):
        """Ação Secundária: Arremesso da Naginata em voo supersônico."""
        if not self.can_act():
            return False

        if not self.has_naginata:
            # Já está desarmado: executar tackle de recuperação
            return self.trigger_tackle_charge(aim_x, aim_y)

        self.set_facing(aim_x, aim_y)
        self.state = STATE_NAGINATA_THROW
        self.state_timer = self.throw_duration
        self.hitbox_active = False

        # Instanciar projétil da naginata
        proj = NaginataProjectile(
            wx=self.wx + self.facing_x * 0.45,
            wy=self.wy + self.facing_y * 0.45,
            wz=0.35,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self,
            max_range=7.5
        )
        projectiles.append(proj)
        self.active_naginata_projectile = proj
        self.has_naginata = False
        self.throw_timer = self.throw_cooldown

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.3))
        return True

    def trigger_tackle_charge(self, aim_x: float, aim_y: float):
        """Investida de alta velocidade desarmada: deal 0 lethal damage + STUN garantido (1.2s)."""
        if not self.is_alive or self.state in (STATE_ROLL, STATE_STUNNED, STATE_DEAD):
            return False

        # Se houver naginata fincada no solo, guiar na direção dela se o jogador mirar próximo
        target_x, target_y = aim_x, aim_y
        if self.active_naginata_projectile and getattr(self.active_naginata_projectile, "is_active", False):
            if getattr(self.active_naginata_projectile, "state", "") == "ON_GROUND":
                target_x = self.active_naginata_projectile.wx
                target_y = self.active_naginata_projectile.wy

        dx = target_x - self.wx
        dy = target_y - self.wy
        dist = math.hypot(dx, dy)
        if dist > 0.01:
            self.tackle_dir_x = dx / dist
            self.tackle_dir_y = dy / dist
        else:
            self.tackle_dir_x = self.facing_x
            self.tackle_dir_y = self.facing_y

        self.set_facing(self.wx + self.tackle_dir_x, self.wy + self.tackle_dir_y)
        self.state = STATE_TACKLE_CHARGE
        self.state_timer = self.tackle_duration
        self.tackle_timer = self.tackle_duration
        self.tackle_hit_target = False

        # Hitbox de impacto contundente (atordoante, sem letalidade direta)
        self.hitbox_active = True
        self.hitbox_damage = 0
        self.hitbox_radius = 1.05
        self.hitbox_center = (self.wx + self.facing_x * 0.70, self.wy + self.facing_y * 0.70)
        self.slash_dir = (self.facing_x, self.facing_y)
        return True

    def recover_naginata(self):
        """Recupera a Naginata empunhada com sucesso."""
        self.has_naginata = True
        self.active_naginata_projectile = None

    def set_facing(self, target_wx: float, target_wy: float):
        """Define o vetor de orientação (facing) em direção ao alvo."""
        dx = target_wx - self.wx
        dy = target_wy - self.wy
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            self.facing_x = dx / dist
            self.facing_y = dy / dist

    def update(self, dt: float, game_map, particles: list = None, opponent = None, banners: list = None):
        """Atualização de ciclo de combate do Benkei."""
        super().update_dodge_timers(dt)

        if self.throw_timer > 0:
            self.throw_timer = max(0.0, self.throw_timer - dt)

        # Atualizar rolamento se em estado ROLL
        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            return

        # 1. Investida Desarmada (TACKLE_CHARGE)
        if self.state == STATE_TACKLE_CHARGE:
            self.state_timer -= dt
            self.tackle_timer -= dt

            # Deslocamento em alta velocidade
            step = self.tackle_speed * dt
            new_wx = self.wx + self.tackle_dir_x * step
            new_wy = self.wy + self.tackle_dir_y * step

            # Limites de arena
            min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
            new_wx = max(min_x, min(max_x, new_wx))
            new_wy = max(min_y, min(max_y, new_wy))

            # Colisão com rochas e construções
            hit_solid = False
            for rock in getattr(game_map, "rocks", []):
                c, px, py = rock.check_collision(new_wx, new_wy, self.radius)
                if c:
                    new_wx += px; new_wy += py
                    hit_solid = True
            for bldg in getattr(game_map, "buildings", []):
                c, px, py = bldg.check_collision(new_wx, new_wy, self.radius)
                if c:
                    new_wx += px; new_wy += py
                    hit_solid = True

            self.wx, self.wy = new_wx, new_wy
            self.hitbox_center = (self.wx + self.facing_x * 0.70, self.wy + self.facing_y * 0.70)

            # Partículas de atrito no solo
            if particles is not None and random.random() < 0.6:
                particles.append(SparkParticle(self.wx, self.wy, 0.2))

            # Checar acerto no oponente durante a carga
            if opponent and getattr(opponent, "is_alive", True) and not self.tackle_hit_target:
                d_opp = math.hypot(opponent.wx - self.wx, opponent.wy - self.wy)
                if d_opp < (self.hitbox_radius + getattr(opponent, "radius", 0.35)):
                    self.tackle_hit_target = True
                    # STUN absoluto de 1.2s no oponente
                    opponent.stun(1.20)
                    opponent.apply_forced_displacement(self.tackle_dir_x * 1.8, self.tackle_dir_y * 1.8, game_map)
                    if banners is not None:
                        banners.append(FloatingBanner("STUNNED! (1.2s)", opponent.wx, opponent.wy, wz=1.7, color=(240, 180, 50)))
                    if particles is not None:
                        for _ in range(12):
                            particles.append(SparkParticle(opponent.wx, opponent.wy, 0.4))

            # Checar se alcançou a naginata cravada no chão
            if self.active_naginata_projectile and getattr(self.active_naginata_projectile, "is_active", False):
                if getattr(self.active_naginata_projectile, "state", "") == "ON_GROUND":
                    d_nag = math.hypot(self.active_naginata_projectile.wx - self.wx, self.active_naginata_projectile.wy - self.wy)
                    if d_nag < 0.75:
                        proj = self.active_naginata_projectile
                        self.recover_naginata()
                        if proj:
                            proj.is_active = False
                        if particles is not None:
                            for _ in range(8):
                                particles.append(SparkParticle(self.wx, self.wy, 0.3))

            if self.state_timer <= 0 or hit_solid:
                self.state = STATE_IDLE
                self.hitbox_active = False
                self.roll_recovery_timer = 0.16
            return

        # 2. Estocada Armada (ATTACK)
        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            self.hitbox_center = (self.wx + self.facing_x * 1.80, self.wy + self.facing_y * 1.80)
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.thrust_recovery
                self.hitbox_active = False
            return

        # 3. Arremesso (NAGINATA_THROW)
        if self.state == STATE_NAGINATA_THROW:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # 4. Recuperação (RECOVERY)
        if self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # 5. Atordoado (STUNNED)
        if self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # Checagem passiva de recolher a naginata andando sobre ela
        if not self.has_naginata and self.active_naginata_projectile and getattr(self.active_naginata_projectile, "is_active", False):
            if getattr(self.active_naginata_projectile, "state", "") == "ON_GROUND":
                d_nag = math.hypot(self.active_naginata_projectile.wx - self.wx, self.active_naginata_projectile.wy - self.wy)
                if d_nag < 0.65:
                    proj = self.active_naginata_projectile
                    self.recover_naginata()
                    if proj:
                        proj.is_active = False
                    if particles is not None:
                        for _ in range(6):
                            particles.append(SparkParticle(self.wx, self.wy, 0.25))

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o modelo voxel 3D do Benkei com armadura de ferro e naginata."""
        extra = {
            "has_naginata": self.has_naginata,
            "is_throwing": (self.state == STATE_NAGINATA_THROW),
            "is_charging": (self.state == STATE_TACKLE_CHARGE),
            "hoist_slam_phase": getattr(self, "hoist_slam_phase", None),
            "hoist_slam_prog": getattr(self, "hoist_slam_prog", 0.0),
        }
        render_voxel_humanoid(
            surface=surface,
            camera=camera,
            wx=self.wx, wy=self.wy, wz=self.wz,
            facing_x=self.facing_x, facing_y=self.facing_y,
            state=self.state,
            state_timer=self.state_timer,
            is_alive=self.is_alive,
            char_type="benkei",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=(self.is_moving or self.state == STATE_TACKLE_CHARGE),
            extra_props=extra
        )
