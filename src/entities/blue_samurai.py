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
    STATE_ATTACK, STATE_RECOVERY, STATE_PARRY, STATE_STUNNED, STATE_DEAD
)

class BlueSamurai(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Musashi (Blue)")
        self.speed = 2.8  # Passos pesados, deliberados e firmes

        # Parâmetros do Combo de 3 Cortes
        self.windup_duration = 0.42       # ALTO WINDUP preparatório!
        self.hit_duration = 0.12          # Duração de cada corte
        self.combo_step = 0               # 1, 2 ou 3
        self.recovery_duration = 0.22     # Recuperação rápida após o combo

        # Defesa / Parry
        self.parry_timer = 0.0

        # Ângulos visuais das lâminas
        self.blade_l_angle = 0.0
        self.blade_r_angle = 0.0

    def trigger_combo_attack(self, target_wx: float, target_wy: float):
        """Dispara ou encadeia os 3 ataques em sequência rápida."""
        if self.state in (STATE_IDLE, STATE_WALK):
            self.set_facing(target_wx, target_wy)
            self.combo_step = 1
            self.state = STATE_ATTACK
            self.state_timer = 0.18
            self.hitbox_active = True
            self.hitbox_radius = 1.3
            self.slash_dir = (self.facing_x, self.facing_y)
            self.hitbox_center = (self.wx + self.facing_x * 0.9, self.wy + self.facing_y * 0.9)
        elif self.state == STATE_ATTACK:
            # Bufferiza o próximo golpe do combo triplo
            if self.combo_step < 3:
                self.combo_buffered = True
        elif self.state == STATE_RECOVERY and self.combo_step < 3:
            # Encadeia o próximo corte imediatamente a partir do recovery
            self.set_facing(target_wx, target_wy)
            self.combo_step += 1
            self.state = STATE_ATTACK
            self.state_timer = 0.18
            self.hitbox_active = True
            self.hitbox_radius = 1.4 if self.combo_step == 2 else 1.7
            self.slash_dir = (self.facing_x, self.facing_y)

    def trigger_parry(self):
        """Assume a postura de guarda defensiva com lâminas cruzadas."""
        if not self.can_move():
            return
        self.state = STATE_PARRY
        self.state_timer = 0.45

    def update(self, dt: float, game_map):
        """Atualiza a lógica e os 3 ataques em sequência do Samurai Azul."""
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Avanço de pressão a cada golpe
            step_speed = 3.2 if self.combo_step < 3 else 4.2
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
                return

            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            self.hitbox_center = (self.wx + self.facing_x * 0.9, self.wy + self.facing_y * 0.9)

            if self.state_timer <= 0:
                if self.combo_step < 3:
                    # Encadeia automaticamente ou com buffer o próximo ataque da sequência de 3
                    self.combo_step += 1
                    self.state_timer = 0.18
                    self.hitbox_active = True
                    self.hitbox_radius = 1.4 if self.combo_step == 2 else 1.8
                else:
                    # Completou os 3 ataques em sequência!
                    self.state = STATE_RECOVERY
                    self.state_timer = self.recovery_duration
                    self.hitbox_active = False

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.combo_step = 0

        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Samurai Azul com as duas katanas empunhadas."""
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

        char_surf = pygame.Surface((70, 70), pygame.SRCALPHA)
        cx, cy = 35, 45

        # 1. Sombra
        pygame.draw.ellipse(char_surf, (10, 15, 12, 120), (cx - 14, cy - 6, 28, 12))

        if not self.is_alive:
            pygame.draw.ellipse(char_surf, (*COLOR_BLUE_KIMONO, self.alpha), (cx - 16, cy - 8, 32, 14))
            pygame.draw.circle(char_surf, (*COLOR_BLUE_HAIR, self.alpha), (cx - 14, cy - 4), 6)
            char_surf.set_alpha(self.alpha)
            surface.blit(char_surf, (base_sx - 35, base_sy - 45))
            return

        # 2. Hakama Azul Escuro
        leg_offset = math.sin(self.walk_cycle) * 3.5 if self.state == STATE_WALK else 0.0
        pygame.draw.polygon(char_surf, (*COLOR_BLUE_HAKAMA, self.alpha), [
            (cx - 8, cy - 14), (cx + 8, cy - 14),
            (cx + 6 + leg_offset, cy), (cx - 6 - leg_offset, cy)
        ])

        # 3. Quimono Azul Profundo (Tronco)
        chest_y = cy - 26
        pygame.draw.polygon(char_surf, (*COLOR_BLUE_KIMONO, self.alpha), [
            (cx - 9, chest_y), (cx + 9, chest_y),
            (cx + 7, cy - 12), (cx - 7, cy - 12)
        ])
        # Faixa branca (Obi)
        pygame.draw.line(char_surf, (*COLOR_WHITE, self.alpha), (cx - 7, cy - 13), (cx + 7, cy - 13), 3)

        # 4. As Duas Espadas (Niten Ichi-ryū)
        face_angle = math.atan2(self.facing_y, self.facing_x)

        if self.state == STATE_WINDUP:
            # Posição de Windup: Lâminas levantadas em guarda alta acima da cabeça!
            pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx - 6, chest_y), (cx - 12, cy - 42), 3)
            pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx + 6, chest_y), (cx + 12, cy - 42), 3)
            # Brilho de energia azul de aviso
            pygame.draw.circle(char_surf, (*COLOR_BLUE_AURA, 200), (cx, cy - 38), 5)

        elif self.state == STATE_PARRY:
            # Lâminas cruzadas em 'X' à frente do peito
            pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx - 12, chest_y + 8), (cx + 12, chest_y - 8), 3)
            pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx + 12, chest_y + 8), (cx - 12, chest_y - 8), 3)
            pygame.draw.circle(char_surf, (*COLOR_GOLD, self.alpha), (cx, chest_y), 4)

        elif self.state == STATE_ATTACK:
            # Combo em ação: varia a posição das espadas a cada golpe!
            if self.combo_step == 1:
                # Espada direita cortando para frente
                ex = cx + int(math.cos(face_angle + 0.3) * 22)
                ey = chest_y + int(math.sin(face_angle + 0.3) * 14)
                pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx + 5, chest_y), (ex, ey), 3)
                pygame.draw.line(char_surf, (*COLOR_BLUE_AURA, self.alpha), (cx + 5, chest_y), (ex, ey), 1)
            elif self.combo_step == 2:
                # Espada esquerda cortando em contra-golpe
                ex = cx + int(math.cos(face_angle - 0.4) * 22)
                ey = chest_y + int(math.sin(face_angle - 0.4) * 14)
                pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx - 5, chest_y), (ex, ey), 3)
                pygame.draw.line(char_surf, (*COLOR_BLUE_AURA, self.alpha), (cx - 5, chest_y), (ex, ey), 1)
            else:
                # Corte 3: Corte duplo em X
                ex1 = cx + int(math.cos(face_angle + 0.4) * 24)
                ey1 = chest_y + int(math.sin(face_angle + 0.4) * 16)
                ex2 = cx + int(math.cos(face_angle - 0.4) * 24)
                ey2 = chest_y + int(math.sin(face_angle - 0.4) * 16)
                pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx, chest_y), (ex1, ey1), 3)
                pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx, chest_y), (ex2, ey2), 3)
                pygame.draw.circle(char_surf, (*COLOR_BLUE_AURA, 220), ((ex1 + ex2)//2, (ey1 + ey2)//2), 6)

        else:
            # Posição neutra: Duas katanas empunhadas relaxadas dos lados
            pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx - 8, cy - 16), (cx - 16, cy - 2), 3)
            pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx + 8, cy - 16), (cx + 16, cy - 2), 3)

        # 5. Cabeça e Cabelo Preto (Nó Samurai)
        head_y = cy - 32
        pygame.draw.circle(char_surf, (240, 210, 185, self.alpha), (cx, head_y), 5)
        # Faixa branca na testa
        pygame.draw.line(char_surf, (*COLOR_WHITE, self.alpha), (cx - 4, head_y - 2), (cx + 4, head_y - 2), 2)
        # Chonmage (Nó no topo da cabeça)
        pygame.draw.circle(char_surf, (*COLOR_BLUE_HAIR, self.alpha), (cx, head_y - 5), 4)

        if self.is_hidden:
            pygame.draw.circle(char_surf, (120, 220, 100, 200), (cx, cy - 45), 3)

        char_surf.set_alpha(self.alpha)
        surface.blit(char_surf, (base_sx - 35, base_sy - 45))
