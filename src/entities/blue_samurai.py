"""
Samurai Azul (Musashi): Mestre do Niten Ichi-ryū (Duas Espadas).
Ataque de alto windup preparatório seguido por um combo rápido
e devastador de 3 cortes consecutivos, além de postura de bloqueio (parry).
"""
import math
import pygame
from src.config import (
    COLOR_BLUE_KIMONO, COLOR_BLUE_HAIR, COLOR_BLUE_HAKAMA,
    COLOR_BLUE_AURA, COLOR_STEEL, COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_WINDUP,
    STATE_ATTACK, STATE_RECOVERY, STATE_PARRY, STATE_STUNNED, STATE_DEAD, STATE_ROLL
)
from src.entities.voxel_models import render_voxel_humanoid

class BlueSamurai(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Musashi")
        self.speed = 2.8  # Passos pesados, deliberados e firmes

        # Parâmetros do Combo Manual de 3 Cortes (Item 12)
        self.windup_duration = 0.42
        self.hit_duration = 0.12
        self.combo_step = 0               # 1, 2 ou 3
        self.combo_buffered = False
        self.combo_window_timer = 0.0
        self.recovery_duration = 0.20

        # Defesa / Parry
        self.parry_timer = 0.0

        # Ângulos visuais das lâminas
        self.blade_l_angle = 0.0
        self.blade_r_angle = 0.0

    def can_act(self) -> bool:
        return self.is_alive and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY) and self.dash_recovery_timer <= 0

    def trigger_combo_attack(self, target_wx: float, target_wy: float):
        """Dispara ou encadeia os 3 ataques em sequência manual e ritmada (Item 12)."""
        if self.state in (STATE_IDLE, STATE_WALK):
            if self.dash_recovery_timer > 0:
                return
            self.set_facing(target_wx, target_wy)
            self.combo_step = 1
            self.combo_buffered = False
            self.state = STATE_ATTACK
            self.state_timer = 0.18
            self.hitbox_active = True
            self.hitbox_radius = 1.30
            self.slash_dir = (self.facing_x, self.facing_y)
            self.hitbox_center = (self.wx + self.facing_x * 0.9, self.wy + self.facing_y * 0.9)
        elif self.state == STATE_ATTACK:
            # O jogador pressionou o botão durante o golpe atual para encadear o próximo
            if self.combo_step < 3:
                self.combo_buffered = True
                self.set_facing(target_wx, target_wy)
        elif self.state == STATE_RECOVERY and self.combo_step < 3 and self.combo_window_timer > 0:
            # Encadeia o próximo corte imediatamente a partir da janela de combo
            self.set_facing(target_wx, target_wy)
            self.combo_step += 1
            self.combo_buffered = False
            self.state = STATE_ATTACK
            self.state_timer = 0.18
            self.hitbox_active = True
            self.hitbox_radius = 1.45 if self.combo_step == 2 else 1.85
            self.slash_dir = (self.facing_x, self.facing_y)

    def trigger_parry(self):
        """Assume a postura de guarda defensiva com lâminas cruzadas."""
        if not self.can_move() or self.dash_recovery_timer > 0:
            return
        self.state = STATE_PARRY
        self.state_timer = 0.45

    def update(self, dt: float, game_map):
        """Atualiza a lógica e os golpes do combo manual de Musashi."""
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.dash_recovery_timer > 0:
            self.dash_recovery_timer -= dt
        if self.combo_window_timer > 0:
            self.combo_window_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Avanço de pressão: 3º golpe projeta Musashi a uma distância maior para frente (Forward Lunge - Item 12)
            step_speed = 3.2 if self.combo_step == 1 else (4.0 if self.combo_step == 2 else 6.2)
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt

            # Colisão com obstáculos
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
                self.stun(0.8)
                self.combo_step = 0
                self.combo_buffered = False
                return

            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            self.hitbox_center = (self.wx + self.facing_x * 0.9, self.wy + self.facing_y * 0.9)

            if self.state_timer <= 0:
                if self.combo_buffered and self.combo_step < 3:
                    # Encadeia o próximo golpe somente porque o jogador apertou o botão!
                    self.combo_step += 1
                    self.combo_buffered = False
                    self.state_timer = 0.18
                    self.hitbox_active = True
                    self.hitbox_radius = 1.45 if self.combo_step == 2 else 1.85
                else:
                    # Se NÃO pressionou consecutivamente, para o combo aqui e entra em recovery
                    self.state = STATE_RECOVERY
                    self.state_timer = self.recovery_duration
                    self.combo_window_timer = 0.14
                    self.hitbox_active = False

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.combo_step = 0
                self.combo_buffered = False

        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_ROLL:
            self.update_roll(dt, game_map)

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Samurai Azul no autêntico estilo Voxel 3D Isométrico."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="musashi",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props={"combo_step": self.combo_step}
        )
