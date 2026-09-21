"""
Samurai Hajime Saitou (Líder do Shinsengumi).
Mestre absoluto da técnica Gatotsu (Estocada Crescente).
Inicia na velocidade normal e ganha aceleração contínua até velocidade extrema,
mas perde manobrabilidade (esterçamento rígido) e sofre alta inércia de frenagem (demora a frear).
"""
import math
import pygame
from src.config import (
    COLOR_SAITOU_LIGHT_BLUE, COLOR_SAITOU_HAORI_DARK, COLOR_SAITOU_HAKAMA,
    COLOR_SAITOU_AURA, COLOR_STEEL, COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_PARRY, STATE_STUNNED, STATE_DEAD
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle

STATE_GATOTSU_CHARGE = "GATOTSU_CHARGE"
STATE_BRAKING = "BRAKING"
STATE_ZEROSHIKI = "ZEROSHIKI"

class SaitouSamurai(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Saitou")
        self.speed = 4.6  # Velocidade padrão de deslocamento

        # -------------------------------------------------------------
        # Parâmetros do Gatotsu (Estocada com Aceleração e Inércia)
        # -------------------------------------------------------------
        self.initial_charge_speed = 4.8  # Começa na velocidade normal
        self.charge_speed = self.initial_charge_speed
        self.max_charge_speed = 15.5      # Calibrado: velocidade alta com reação viável
        self.charge_accel = 18.0          # Taxa de ganho de velocidade (tiles/s²)

        self.charge_dir_x = 1.0
        self.charge_dir_y = 0.0
        self.gatotsu_timer = 0.0
        self.gatotsu_max_duration = 0.90  # Alcance longo pelo mapa/ponte

        # Perda de manobrabilidade (esterçamento rígido: 1.1 rad/s)
        self.turn_rate = 1.15

        # Inércia e frenagem demorada
        self.brake_speed = 0.0
        self.brake_duration = 0.45
        self.slide_particle_timer = 0.0

        # Rastro de velocidade do Gatotsu
        self.trail_points: list[tuple[float, float]] = []

        # -------------------------------------------------------------
        # Parâmetros do Gatotsu Zeroshiki (Estocada Curta à Queima-Roupa)
        # -------------------------------------------------------------
        self.zeroshiki_windup = 0.07
        self.zeroshiki_active = 0.12
        self.zeroshiki_recovery = 0.35
        self.zeroshiki_phase = "NONE" # "WINDUP", "ACTIVE", "RECOVERY"

    def can_act(self) -> bool:
        return (
            self.is_alive and
            self.state not in (STATE_GATOTSU_CHARGE, STATE_BRAKING, STATE_ZEROSHIKI, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD)
        )

    def trigger_gatotsu_thrust(self, target_wx: float, target_wy: float):
        """
        Ataque Primário: GATOTSU (Estocada Crescente).
        Inicia na velocidade normal, ganha aceleração contínua, perde esterçamento
        e sofre derrapagem prolongada ao frear.
        """
        if not self.can_act():
            return

        dx = target_wx - self.wx
        dy = target_wy - self.wy
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            self.charge_dir_x = dx / dist
            self.charge_dir_y = dy / dist
        else:
            self.charge_dir_x = self.facing_x
            self.charge_dir_y = self.facing_y

        self.facing_x = self.charge_dir_x
        self.facing_y = self.charge_dir_y

        self.charge_speed = self.initial_charge_speed
        self.state = STATE_GATOTSU_CHARGE
        self.gatotsu_timer = 0.0

        # Hitbox ativa na ponta da lâmina estendida
        self.hitbox_active = True
        self.hitbox_radius = 0.85
        self.slash_dir = (self.charge_dir_x, self.charge_dir_y)
        self.hitbox_center = (
            self.wx + self.charge_dir_x * 0.95,
            self.wy + self.charge_dir_y * 0.95
        )
        self.trail_points = [(self.wx, self.wy)]

    def trigger_gatotsu(self, target_wx: float, target_wy: float):
        self.trigger_gatotsu_thrust(target_wx, target_wy)

    def trigger_secondary(self, target_wx: float, target_wy: float):
        self.trigger_zeroshiki(target_wx, target_wy)

    def apply_gatotsu_steering(self, dwx: float, dwy: float, dt: float):
        """
        Aplica esterçamento rígido durante a investida do Gatotsu.
        O jogador pode tentar mudar de direção, mas a manobrabilidade é severamente limitada.
        """
        if self.state != STATE_GATOTSU_CHARGE:
            return

        input_mag = math.hypot(dwx, dwy)
        if input_mag > 0.1:
            target_angle = math.atan2(dwy, dwx)
            current_angle = math.atan2(self.charge_dir_y, self.charge_dir_x)

            # Menor diferença angular entre -pi e +pi
            diff = (target_angle - current_angle + math.pi) % (2.0 * math.pi) - math.pi

            # Limitar curva pela taxa rígida de esterçamento
            max_turn = self.turn_rate * dt
            turn = max(-max_turn, min(max_turn, diff))

            new_angle = current_angle + turn
            self.charge_dir_x = math.cos(new_angle)
            self.charge_dir_y = math.sin(new_angle)
            self.facing_x = self.charge_dir_x
            self.facing_y = self.charge_dir_y
            self.slash_dir = (self.charge_dir_x, self.charge_dir_y)

    def trigger_zeroshiki(self, target_wx: float, target_wy: float):
        """
        Ataque Secundário: GATOTSU ZEROSHIKI (Estocada Curta à Queima-Roupa).
        Golpe instantâneo sem corrida, disparado do corpo a corpo.
        """
        if not self.can_act():
            return

        dx = target_wx - self.wx
        dy = target_wy - self.wy
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            self.facing_x = dx / dist
            self.facing_y = dy / dist

        self.state = STATE_ZEROSHIKI
        self.zeroshiki_phase = "WINDUP"
        self.state_timer = self.zeroshiki_windup
        self.hitbox_active = False

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.slow_timer > 0:
            self.slow_timer -= dt

        # -------------------------------------------------------------
        # 1. ESTADO DE CARGA DO GATOTSU (Aceleração Contínua)
        # -------------------------------------------------------------
        if self.state == STATE_GATOTSU_CHARGE:
            self.gatotsu_timer += dt

            # Ganho progressivo de velocidade
            self.charge_speed = min(self.max_charge_speed, self.charge_speed + self.charge_accel * dt)

            # Avanço físico
            step = self.charge_speed * dt
            new_x = self.wx + self.charge_dir_x * step
            new_y = self.wy + self.charge_dir_y * step

            # Corte de bambus no caminho com a ponta da lâmina
            for b in game_map.bamboos:
                if not b.is_cut:
                    b_dist = math.hypot(new_x - b.wx, new_y - b.wy)
                    if b_dist < 0.65:
                        part = b.cut((self.charge_dir_x, self.charge_dir_y))
                        if part and particles is not None:
                            particles.append(part)

            # Colisão punitiva com obstáculos rígidos (Recoil / Wall Splat)
            hit_hard_obstacle = False
            for r in game_map.rocks:
                col, _, _ = r.check_collision(new_x, new_y, self.radius)
                if col:
                    hit_hard_obstacle = True
                    break

            if game_map.well:
                col, _, _ = game_map.well.check_collision(new_x, new_y, self.radius)
                if col:
                    hit_hard_obstacle = True

            if hit_hard_obstacle:
                # Ricochete violento contra pedra: atordoa Saitou!
                self.state = STATE_STUNNED
                self.state_timer = 0.70
                self.hitbox_active = False
                if particles is not None:
                    for _ in range(8):
                        particles.append(SparkParticle(self.wx, self.wy, 0.5))
                return

            self.wx = new_x
            self.wy = new_y
            self.hitbox_center = (
                self.wx + self.charge_dir_x * 0.95,
                self.wy + self.charge_dir_y * 0.95
            )

            # Registro de rastro
            self.trail_points.append((self.wx, self.wy))
            if len(self.trail_points) > 12:
                self.trail_points.pop(0)

            # Transição para Frenagem Demorada (Braking / Inércia) ao fim do fôlego
            if self.gatotsu_timer >= self.gatotsu_max_duration:
                self.state = STATE_BRAKING
                self.hitbox_active = False
                self.brake_speed = self.charge_speed
                self.state_timer = self.brake_duration

        # -------------------------------------------------------------
        # 2. ESTADO DE FRENAGEM E DERRAPAGEM (Demora a Frear)
        # -------------------------------------------------------------
        elif self.state == STATE_BRAKING:
            self.state_timer -= dt
            # Desaceleração por atrito
            self.brake_speed = max(0.0, self.brake_speed - 36.0 * dt)

            step = self.brake_speed * dt
            new_x = self.wx + self.charge_dir_x * step
            new_y = self.wy + self.charge_dir_y * step

            # Checar limites contra pedras ao deslizar
            can_slide = True
            for r in game_map.rocks:
                col, _, _ = r.check_collision(new_x, new_y, self.radius)
                if col: can_slide = False; break
            if can_slide and game_map.well:
                col, _, _ = game_map.well.check_collision(new_x, new_y, self.radius)
                if col: can_slide = False

            if can_slide:
                self.wx = new_x
                self.wy = new_y

            # Faíscas de atrito dos calçados derrapando
            self.slide_particle_timer += dt
            if self.slide_particle_timer > 0.06:
                self.slide_particle_timer = 0.0
                if particles is not None and self.brake_speed > 3.0:
                    particles.append(SparkParticle(self.wx, self.wy, 0.1))

            if self.state_timer <= 0 and self.brake_speed <= 0.5:
                self.state = STATE_IDLE
                self.is_moving = False
                self.trail_points.clear()

        # -------------------------------------------------------------
        # 3. ESTADO GATOTSU ZEROSHIKI (Estocada Curta)
        # -------------------------------------------------------------
        elif self.state == STATE_ZEROSHIKI:
            self.state_timer -= dt
            if self.zeroshiki_phase == "WINDUP":
                if self.state_timer <= 0:
                    self.zeroshiki_phase = "ACTIVE"
                    self.state_timer = self.zeroshiki_active
                    self.hitbox_active = True
                    self.hitbox_radius = 0.70
                    self.slash_dir = (self.facing_x, self.facing_y)
                    self.hitbox_center = (
                        self.wx + self.facing_x * 0.75,
                        self.wy + self.facing_y * 0.75
                    )
            elif self.zeroshiki_phase == "ACTIVE":
                if self.state_timer <= 0:
                    self.zeroshiki_phase = "RECOVERY"
                    self.state_timer = self.zeroshiki_recovery
                    self.hitbox_active = False
            elif self.zeroshiki_phase == "RECOVERY":
                if self.state_timer <= 0:
                    self.state = STATE_IDLE
                    self.zeroshiki_phase = "NONE"

        # -------------------------------------------------------------
        # 4. OUTROS ESTADOS (Stun, Recovery)
        # -------------------------------------------------------------
        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza Hajime Saitou no autêntico estilo 3D Voxel Art."""
        # Rastro luminoso ciano do Gatotsu no solo
        if len(self.trail_points) >= 2:
            pts = [camera.apply(px, py, 0.05) for px, py in self.trail_points]
            if len(pts) >= 2:
                pygame.draw.lines(surface, COLOR_SAITOU_AURA, False, pts, 4)
                pygame.draw.lines(surface, COLOR_WHITE, False, pts, 2)

        # Indicador de stealth
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="saitou",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving
        )
