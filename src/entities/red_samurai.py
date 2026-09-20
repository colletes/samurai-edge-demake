"""
Samurai Vermelho (Kenshin): Mestre do Iai-jutsu.
Ataque relâmpago de saque instantâneo com avanço veloz,
mas com alto tempo de recuperação (recovery) após o golpe.
"""
import math
import pygame
from src.config import (
    COLOR_RED_KIMONO, COLOR_RED_HAIR, COLOR_RED_HAKAMA,
    COLOR_RED_AURA, COLOR_STEEL, COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_WINDUP,
    STATE_ATTACK, STATE_RECOVERY, STATE_DASH, STATE_STUNNED, STATE_DEAD
)
from src.isometric.iso_math import world_to_iso

class RedSamurai(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Kenshin (Red)")
        self.speed = 5.4  # Agilidade máxima do retalhador

        # Parâmetros do Iai-jutsu
        self.dash_speed = 22.0
        self.dash_duration = 0.16   # Avanço supersônico
        self.recovery_duration = 1.35 # ALTO COOLDOWN embainhando a katana!
        self.attack_range = 2.4

        # Efeito visual de rastro de lâmina
        self.slash_trail_points: list[tuple[float, float]] = []

    def trigger_iai_attack(self, target_wx: float, target_wy: float):
        """Inicia o golpe Iai-jutsu se puder agir."""
        if not self.can_move():
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = self.dash_duration
        self.hitbox_active = True
        self.hitbox_radius = 1.2
        self.slash_dir = (self.facing_x, self.facing_y)
        self.slash_trail_points = [(self.wx, self.wy)]
        self.hitbox_center = (self.wx + self.facing_x * 0.8, self.wy + self.facing_y * 0.8)

    def trigger_dash(self, dir_x: float, dir_y: float):
        """Esquiva rápida de reposicionamento."""
        if not self.can_move():
            return
        if dir_x == 0 and dir_y == 0:
            dir_x, dir_y = -self.facing_x, -self.facing_y # Recuo para trás

        self.state = STATE_DASH
        self.state_timer = 0.22
        self.facing_x = dir_x
        self.facing_y = dir_y

    def update(self, dt: float, game_map):
        """Atualiza os estados e timings do Samurai Vermelho."""
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.state == STATE_ATTACK:
            # Avanço relâmpago Iai
            self.state_timer -= dt
            dash_dist = self.dash_speed * dt
            new_wx = self.wx + self.facing_x * dash_dist
            new_wy = self.wy + self.facing_y * dash_dist

            # Verificar colisão com rochas/poço durante o golpe
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
                # Bateu em pedra durante o corte! Ricocheteia e fica atordoado
                self.stun(duration=1.0)
                return

            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            self.slash_trail_points.append((self.wx, self.wy))
            self.hitbox_center = (self.wx + self.facing_x * 0.8, self.wy + self.facing_y * 0.8)

            if self.state_timer <= 0:
                # Fim do avanço: entra no LONGO RECOVERY embainhando a espada
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
                self.hitbox_active = False

        elif self.state == STATE_RECOVERY:
            # Samurai fica travado no cooldown vulnerável
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.slash_trail_points.clear()

        elif self.state == STATE_DASH:
            self.state_timer -= dt
            new_wx = self.wx + self.facing_x * 8.5 * dt
            new_wy = self.wy + self.facing_y * 8.5 * dt
            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Samurai Vermelho em pixel art procedural estilizado."""
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

        # Superfície com canal alfa para transparência de camuflagem
        char_surf = pygame.Surface((70, 70), pygame.SRCALPHA)
        cx, cy = 35, 45  # Centro dos pés dentro da mini-superfície

        # 1. Sombra no chão
        pygame.draw.ellipse(char_surf, (10, 15, 12, 120), (cx - 14, cy - 6, 28, 12))

        # Se estiver morto: pose caída
        if not self.is_alive:
            pygame.draw.ellipse(char_surf, (*COLOR_RED_KIMONO, self.alpha), (cx - 16, cy - 8, 32, 14))
            pygame.draw.circle(char_surf, (*COLOR_RED_HAIR, self.alpha), (cx - 14, cy - 4), 6)
            char_surf.set_alpha(self.alpha)
            surface.blit(char_surf, (base_sx - 35, base_sy - 45))
            return

        # 2. Hakama (Calça branca ampla tradicional)
        leg_offset = math.sin(self.walk_cycle) * 4.0 if self.state == STATE_WALK else 0.0
        # Perna esquerda e direita
        pygame.draw.polygon(char_surf, (*COLOR_RED_HAKAMA, self.alpha), [
            (cx - 8, cy - 14), (cx + 8, cy - 14),
            (cx + 6 + leg_offset, cy), (cx - 6 - leg_offset, cy)
        ])

        # 3. Quimono Vermelho Carmim (Tronco)
        chest_y = cy - 26
        body_poly = [
            (cx - 9, chest_y), (cx + 9, chest_y),
            (cx + 7, cy - 12), (cx - 7, cy - 12)
        ]
        pygame.draw.polygon(char_surf, (*COLOR_RED_KIMONO, self.alpha), body_poly)
        # Faixa preta na cintura (Obi)
        pygame.draw.line(char_surf, (*COLOR_BLACK, self.alpha), (cx - 7, cy - 13), (cx + 7, cy - 13), 3)

        # 4. Pose dos Braços e Katana
        # Na pose do Iai: Katana embainhada na cintura esquerda
        sword_angle = math.atan2(self.facing_y, self.facing_x)

        if self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY):
            # Bainha preta na cintura
            pygame.draw.line(char_surf, (*COLOR_BLACK, self.alpha), (cx - 4, cy - 15), (cx - 14, cy - 9), 3)
            # Tsuka (empunhadura dourada) na mão direita pronta para puxar
            pygame.draw.line(char_surf, (*COLOR_GOLD, self.alpha), (cx - 4, cy - 15), (cx + 2, cy - 18), 3)

            if self.state == STATE_RECOVERY:
                # Pose agachada e concentrada embainhando devagar (notō)
                pygame.draw.circle(char_surf, (*COLOR_GOLD, self.alpha), (cx - 4, cy - 15), 3)
                # Barra sutil de cooldown sobre a cabeça
                progress = max(0.0, self.state_timer / self.recovery_duration)
                bar_w = 24
                pygame.draw.rect(char_surf, (50, 50, 50, 180), (cx - 12, cy - 42, bar_w, 3))
                pygame.draw.rect(char_surf, (*COLOR_RED_AURA, 220), (cx - 12, cy - 42, int(bar_w * (1.0 - progress)), 3))

        elif self.state == STATE_ATTACK:
            # Lâmina desembainhada cortando em avanço supersônico!
            kx = cx + int(math.cos(sword_angle) * 22)
            ky = chest_y + int(math.sin(sword_angle) * 14)
            pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx, chest_y), (kx, ky), 3)
            pygame.draw.line(char_surf, (*COLOR_WHITE, self.alpha), (cx, chest_y), (kx, ky), 1)

        # 5. Cabeça e Cabelo Ruivo (Kenshin)
        head_y = cy - 32
        pygame.draw.circle(char_surf, (245, 215, 190, self.alpha), (cx, head_y), 5)  # Rosto
        # Cabelo ruivo volumoso com franja
        pygame.draw.circle(char_surf, (*COLOR_RED_HAIR, self.alpha), (cx - 2, head_y - 2), 6)
        # Rabo de cavalo longo balançando para trás
        tail_offset_x = -int(self.facing_x * 8)
        tail_offset_y = -int(self.facing_y * 4) + 2
        pygame.draw.line(char_surf, (*COLOR_RED_HAIR, self.alpha), (cx, head_y - 2), (cx + tail_offset_x, head_y + tail_offset_y), 4)

        # Efeito de Camuflagem (ícone de stealth)
        if self.is_hidden:
            pygame.draw.circle(char_surf, (120, 220, 100, 200), (cx, cy - 45), 3)

        char_surf.set_alpha(self.alpha)
        surface.blit(char_surf, (base_sx - 35, base_sy - 45))

        # Renderizar rastro brilhante do corte do Iai no chão
        if len(self.slash_trail_points) >= 2:
            pts = [camera.apply(px, py, 0.4) for px, py in self.slash_trail_points]
            if len(pts) >= 2:
                pygame.draw.lines(surface, COLOR_RED_AURA, False, pts, 3)
                pygame.draw.lines(surface, COLOR_WHITE, False, pts, 1)
