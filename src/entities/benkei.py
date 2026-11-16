"""
Benkei (O Guardião da Naginata / Walking Tank Colossal):
Monge guerreiro sōhei colossal e inabalável da Ponte Gojō.
- Velocidade pesada (4.35).
- Sem parry técnico (can_parry = False); foco em alcance colossal e solidez de tanque.
- Ataque Primário: Combo de Inércia com Floreio:
  - Passo 1: Varredura Circular em Arco (170°, 2.40m, dano 2, rec 0.16s).
  - Passo 2: Estocada Perfurante Monumental (2.8m, avanço 0.45m, dano 2, rec 0.22s).
- Terceira Ação / Esquiva: Adamantine Guard Push (Avanço Blindado & Empurrão com o Cabo):
  - 12 i-frames, deslize com ombro encouraçado, faíscas no piso.
  - Repulsão e destruição de projéteis hostis (raio 1.8m) e empurrão frontal com deslocamento forçado.
- Ataque Secundário: Arremesso de Naginata: voa até 7.5m e crava-se no chão (acerta na ida). Novo toque no secundário a chama de volta
  (voa até as mãos de Benkei, acertando também na volta); caminhar sobre ela também a recupera.
- Enquanto a Naginata está fora ele fica sem ataque primário (só a esquiva Adamantine Guard Push e o recall).
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_BENKEI_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, resolve_playable_bounds,
    slide_movement_against_obstacles
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import NaginataProjectile
from src.effects.particles import SparkParticle, FloatingBanner

STATE_NAGINATA_THROW = "NAGINATA_THROW"


class BenkeiSamurai(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Benkei")
        self.char_type = "benkei"
        self.speed = 4.35  # Passo firme e vigoroso de monge guerreiro
        self.max_hp = 2
        self.hp = 2
        self.can_parry = False  # Sem parry técnico por design

        # Estado da Naginata
        self.has_naginata = True
        self.active_naginata_projectile = None

        # Combo de Inércia com Naginata (Passo 1: Varredura 170°, Passo 2: Estocada 2.8m)
        self.combo_step = 0
        self.combo_target_step = 0
        self.combo_window_timer = 0.0
        self.combo_window = 0.55
        self.cleave_duration = 0.21
        self.cleave_recovery = 0.16
        self.thrust_duration = 0.18
        self.thrust_recovery = 0.22
        self.thrust_reach = 2.80
        self.thrust_radius = 1.45
        self.recovery_duration = self.cleave_recovery

        # Parâmetros do Arremesso Secundário
        self.throw_duration = 0.22
        self.throw_cooldown = 1.8
        self.throw_timer = 0.0

        # Terceira Ação: Adamantine Guard Push (Avanço Blindado & Empurrão com o Cabo)
        self.is_agile_dodge = False
        self.roll_speed = 8.5
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.18
        self.roll_cooldown_duration = 0.40
        self.push_hit_target = False
        self.action_name = "Estocada Colossal"

    def take_hit(self, slash_dir: tuple[float, float], damage: int = 2) -> tuple[bool, bool]:
        """Aplica dano ao Benkei."""
        if not self.is_alive:
            return False, False
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

    def _start_combo_step(self, step: int, game_map=None):
        """Dispara o passo selecionado do combo de inércia da Naginata."""
        self.combo_step = step
        self.state = STATE_ATTACK
        self.hitbox_active = True
        self.hitbox_damage = 2

        if step == 1:
            # Passo 1: Varredura Circular em Arco (170°, 2.40m, recovery rápido 0.16s)
            self.state_timer = self.cleave_duration
            self.recovery_duration = self.cleave_recovery
            self.hitbox_radius = 2.40
            self.hitbox_center = (
                self.wx + self.facing_x * 1.10,
                self.wy + self.facing_y * 1.10
            )
            self.slash_dir = (self.facing_y, -self.facing_x)  # Corte transversal
            self.action_name = "Varredura Naginata"
        else:
            # Passo 2: Estocada Perfurante Monumental (2.8m, avanço impulsionado de 0.45m)
            self.state_timer = self.thrust_duration
            self.recovery_duration = self.thrust_recovery
            self.hitbox_radius = self.thrust_radius

            # Avanço de 0.45m à frente
            lunge = 0.45
            new_wx = self.wx + self.facing_x * lunge
            new_wy = self.wy + self.facing_y * lunge
            if game_map:
                new_wx, new_wy = slide_movement_against_obstacles(self.wx, self.wy, self.facing_x * lunge, self.facing_y * lunge, self.radius, game_map)
            self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.85,
                self.wy + self.facing_y * 1.85
            )
            self.slash_dir = (self.facing_x, self.facing_y)
            self.action_name = "Estocada Colossal"

    def trigger_naginata_thrust(self, aim_x: float, aim_y: float, game_map=None):
        """Ataque Primário com Naginata (Combo de Inércia) ou Investida Desarmada."""
        if not self.is_alive or self.state in (STATE_STUNNED, STATE_DEAD):
            return False

        if not self.has_naginata:
            # Desarmado (Naginata em voo): sem ataque até ela voltar
            return False

        # Buffer durante golpe atual
        if self.state == STATE_ATTACK:
            if self.combo_step == 1:
                self.combo_target_step = 2
            return False

        if not self.can_act():
            return False

        self.set_facing(aim_x, aim_y)

        # Se estiver na janela de encadeamento pós-golpe 1, avança para o golpe 2
        if self.combo_window_timer > 0 and self.combo_step == 1:
            next_step = 2
        else:
            next_step = 1

        self.combo_target_step = next_step
        self._start_combo_step(next_step, game_map=game_map)
        return True

    def trigger_adamantine_push(self, dwx: float, dwy: float, particles: list = None, banners: list = None, opponent = None, game_map = None, projectiles: list = None):
        """
        Terceira Ação (Esquiva / Avanço Blindado com Empurrão de Cabo):
        - 12 i-frames (invulnerabilidade a golpes e projéteis).
        - Deslocamento firme e pesado com ombro encouraçado (speed 8.5, dur 0.22s, rec 0.18s, cd 0.40s).
        - Reflete / destrói projéteis em raio de 1.8m.
        - Aplica empurrão com deslocamento forçado em oponentes em contato corpo a corpo.
        """
        if not self.is_alive or self.state in (STATE_ROLL, STATE_STUNNED, STATE_DEAD):
            return False
        if self.roll_cooldown_timer > 0:
            return False

        dist = math.hypot(dwx, dwy)
        if dist > 0.05:
            self.facing_x = dwx / dist
            self.facing_y = dwy / dist

        self.state = STATE_ROLL
        self.state_timer = self.roll_duration
        self.is_invulnerable_dodge = True
        self.invulnerable = True
        self.is_projectile_immune = True
        self.hitbox_active = False
        self.push_hit_target = False
        self.action_name = "Adamantine Push"

        # Limpeza imediata de projéteis hostis próximos
        if projectiles is not None:
            for p in projectiles:
                if getattr(p, "is_active", False) and getattr(p, "owner", None) != self:
                    dp = math.hypot(p.wx - self.wx, p.wy - self.wy)
                    if dp <= 1.80:
                        p.is_active = False
                        if particles is not None:
                            for _ in range(8):
                                particles.append(SparkParticle(p.wx, p.wy, 0.3, color=(255, 220, 100)))

        # Empurrão frontal imediato no oponente se em contato
        if opponent and getattr(opponent, "is_alive", True):
            dopp = math.hypot(opponent.wx - self.wx, opponent.wy - self.wy)
            if dopp <= (self.radius + getattr(opponent, "radius", 0.35) + 0.65):
                self.push_hit_target = True
                opponent.apply_forced_displacement(self.facing_x * 1.8, self.facing_y * 1.8, game_map)
                if banners is not None:
                    banners.append(FloatingBanner("ADAMANTINE PUSH!", self.wx, self.wy, wz=1.7, color=(255, 215, 80)))
                if particles is not None:
                    for _ in range(10):
                        particles.append(SparkParticle(opponent.wx, opponent.wy, 0.3, color=(255, 200, 100)))

        # Faíscas no piso
        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.25, color=(240, 205, 120)))
        return True

    def trigger_roll(self, dwx: float, dwy: float, particles: list = None, banners: list = None, opponent = None, game_map = None, projectiles: list = None):
        """Compatibilidade de esquiva com interface padrão Samurai."""
        return self.trigger_adamantine_push(dwx, dwy, particles=particles, banners=banners, opponent=opponent, game_map=game_map, projectiles=projectiles)

    def update_roll(self, dt: float, game_map, particles: list = None, opponent = None, banners: list = None, projectiles: list = None):
        """Atualização física e impacto do avanço blindado Adamantine Push."""
        if self.state != STATE_ROLL:
            return

        self.state_timer -= dt
        step = self.roll_speed * dt
        dx = self.facing_x * step
        dy = self.facing_y * step

        new_wx, new_wy = slide_movement_against_obstacles(self.wx, self.wy, dx, dy, self.radius, game_map)
        self.wx, self.wy = new_wx, new_wy

        # Faíscas de atrito com armadura de ferro e solo
        if particles is not None and random.random() < 0.65:
            particles.append(SparkParticle(self.wx, self.wy, 0.22, color=(240, 205, 120)))

        # Refletir / destruir projéteis durante o deslize
        if projectiles is not None:
            for p in projectiles:
                if getattr(p, "is_active", False) and getattr(p, "owner", None) != self:
                    dp = math.hypot(p.wx - self.wx, p.wy - self.wy)
                    if dp <= 1.80:
                        p.is_active = False
                        if particles is not None:
                            for _ in range(8):
                                particles.append(SparkParticle(p.wx, p.wy, 0.3, color=(255, 220, 100)))

        # Empurrão frontal com deslocamento forçado
        if opponent and getattr(opponent, "is_alive", True) and not self.push_hit_target:
            dopp = math.hypot(opponent.wx - self.wx, opponent.wy - self.wy)
            if dopp <= (self.radius + getattr(opponent, "radius", 0.35) + 0.65):
                self.push_hit_target = True
                opponent.apply_forced_displacement(self.facing_x * 1.8, self.facing_y * 1.8, game_map)
                if banners is not None:
                    banners.append(FloatingBanner("ADAMANTINE PUSH!", self.wx, self.wy, wz=1.7, color=(255, 215, 80)))
                if particles is not None:
                    for _ in range(10):
                        particles.append(SparkParticle(opponent.wx, opponent.wy, 0.3, color=(255, 200, 100)))

        if self.state_timer <= 0:
            self.state = STATE_IDLE
            self.is_invulnerable_dodge = False
            self.invulnerable = False
            self.is_projectile_immune = False
            self.roll_recovery_timer = self.roll_recovery_duration
            self.roll_cooldown_timer = self.roll_cooldown_duration
            self.dash_recovery_timer = self.roll_recovery_duration

    def trigger_naginata_throw(self, aim_x: float, aim_y: float, projectiles: list, particles: list = None):
        """Ação Secundária: Arremesso da Naginata em voo supersônico."""
        if not self.can_act():
            return False

        if not self.has_naginata:
            # A Naginata ainda está em voo (ida ou volta)
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_NAGINATA_THROW
        self.state_timer = self.throw_duration
        self.hitbox_active = False
        self.action_name = "Arremesso Naginata"

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

    def trigger_naginata_secondary(self, aim_x: float, aim_y: float, projectiles: list, particles: list = None):
        """Ataque Secundário: 1º toque arremessa a Naginata; novo toque enquanto ela está fora a chama de volta."""
        if self.has_naginata:
            return self.trigger_naginata_throw(aim_x, aim_y, projectiles, particles=particles)
        return self.trigger_naginata_recall(particles=particles)

    def trigger_naginata_recall(self, particles: list = None):
        """Chama a Naginata arremessada de volta (voa até as mãos de Benkei, acertando na volta)."""
        if not self.is_alive or self.state in (STATE_STUNNED, STATE_DEAD):
            return False
        proj = self.active_naginata_projectile
        if self.has_naginata or proj is None or not proj.is_active:
            return False
        return proj.recall(particles=particles)

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

    def update(self, dt: float, game_map, particles: list = None, opponent = None, banners: list = None, projectiles: list = None):
        """Atualização de ciclo de combate do Benkei."""
        super().update_dodge_timers(dt)

        if self.throw_timer > 0:
            self.throw_timer = max(0.0, self.throw_timer - dt)

        # Decréscimo da janela de encadeamento de combo
        if self.state != STATE_ATTACK and self.combo_window_timer > 0:
            self.combo_window_timer = max(0.0, self.combo_window_timer - dt)
            if self.combo_window_timer <= 0:
                self.combo_step = 0
                self.combo_target_step = 0

        # Atualizar rolamento se em estado ROLL
        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles=particles, opponent=opponent, banners=banners, projectiles=projectiles)
            return

        if not self.is_alive:
            return

        # 2. Ataque Armado (ATTACK)
        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            if self.combo_step == 1:
                self.hitbox_center = (self.wx + self.facing_x * 1.10, self.wy + self.facing_y * 1.10)
            else:
                self.hitbox_center = (self.wx + self.facing_x * 1.85, self.wy + self.facing_y * 1.85)

            if self.state_timer <= 0:
                # Se o próximo passo foi engatilhado durante o golpe 1, avança de imediato
                if self.combo_step < self.combo_target_step:
                    self._start_combo_step(self.combo_target_step, game_map=game_map)
                else:
                    self.state = STATE_RECOVERY
                    self.state_timer = self.recovery_duration
                    self.hitbox_active = False
                    if self.combo_step == 1:
                        self.combo_window_timer = self.combo_window
                    else:
                        self.combo_window_timer = 0.0
                        self.combo_step = 0
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
                if self.combo_window_timer <= 0:
                    self.combo_step = 0
            return

        # 5. Atordoado (STUNNED)
        if self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o modelo voxel 3D do Benkei com armadura de ferro e naginata."""
        roll_p = 0.0
        if self.state == STATE_ROLL:
            roll_p = max(0.0, min(1.0, 1.0 - (self.state_timer / max(0.001, self.roll_duration))))

        base_extra = getattr(self, "extra_props", {}) or {}
        extra = {
            **base_extra,
            "has_naginata": self.has_naginata,
            "is_throwing": (self.state == STATE_NAGINATA_THROW),
            "is_charging": False,
            "is_roll": (self.state == STATE_ROLL),
            "roll_prog": roll_p,
            "combo_step": getattr(self, "combo_step", 1),
            "hoist_slam_phase": getattr(self, "hoist_slam_phase", None),
            "hoist_slam_prog": getattr(self, "hoist_slam_prog", 0.0),
            "action_name": getattr(self, "action_name", ""),
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
            is_moving=(self.is_moving or self.state == STATE_ROLL),
            extra_props=extra
        )
