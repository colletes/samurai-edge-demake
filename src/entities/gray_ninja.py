"""
Ninja Cinza (Kemuri): Mestre em explosivos com delay e bombas de fumaça com slow para fuga.
"""
import math
import pygame
from src.config import (
    COLOR_GRAY_NINJA, COLOR_GRAY_DARK, COLOR_SMOKE, COLOR_WHITE, COLOR_BLACK, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import TimedBombEntity, SmokeCloudEntity

class GrayNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Kemuri (Gray Ninja)")
        self.speed = 4.8
        self.bomb_cooldown = 1.2
        self.bomb_timer = 0.0
        self.smoke_cooldown = 3.5
        self.smoke_timer = 0.0

    def trigger_throw_bomb(self, target_wx: float, target_wy: float, projectiles: list):
        """Ataque Primário: Arremessa bomba com pavio de 1.5s que explode em área (1-hit fatal)."""
        if not self.can_move() or self.bomb_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.bomb_timer = self.bomb_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.14

        # Lança a bomba na direção do alvo a ~2.5 tiles
        throw_dist = min(3.5, math.hypot(target_wx - self.wx, target_wy - self.wy))
        bx = self.wx + self.facing_x * throw_dist
        by = self.wy + self.facing_y * throw_dist

        bomb = TimedBombEntity(wx=bx, wy=by, owner=self)
        projectiles.append(bomb)

    def trigger_smoke_bomb(self, target_wx: float, target_wy: float, projectiles: list):
        """Ataque Secundário: Bomba de fumaça instantânea que dá slow ao oponente e permite fuga."""
        if not self.can_move() or self.smoke_timer > 0:
            return

        self.smoke_timer = self.smoke_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.16

        # Cortina de fumaça instantânea no chão
        smoke = SmokeCloudEntity(wx=self.wx, wy=self.wy, owner=self)
        projectiles.append(smoke)

        # Recuo evasivo do Ninja Cinza para escapar
        self.wx -= self.facing_x * 0.9
        self.wy -= self.facing_y * 0.9
        self.alpha = 90  # Camuflagem de fuga na fumaça

    def update(self, dt: float, game_map):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.bomb_timer > 0:
            self.bomb_timer -= dt
        if self.smoke_timer > 0:
            self.smoke_timer -= dt

        if self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

        char_surf = pygame.Surface((70, 70), pygame.SRCALPHA)
        cx, cy = 35, 45

        # 1. Sombra
        pygame.draw.ellipse(char_surf, (10, 15, 12, 120), (cx - 14, cy - 6, 28, 12))

        if not self.is_alive:
            pygame.draw.ellipse(char_surf, (*COLOR_GRAY_NINJA, self.alpha), (cx - 16, cy - 8, 32, 14))
            pygame.draw.circle(char_surf, (*COLOR_GRAY_DARK, self.alpha), (cx - 14, cy - 4), 6)
            char_surf.set_alpha(self.alpha)
            surface.blit(char_surf, (base_sx - 35, base_sy - 45))
            return

        # 2. Pernas / Calça Shinobi Cinza Ardósia
        leg_offset = math.sin(self.walk_cycle) * 4.0 if self.state == STATE_WALK else 0.0
        pygame.draw.polygon(char_surf, (*COLOR_GRAY_NINJA, self.alpha), [
            (cx - 7, cy - 14), (cx + 7, cy - 14),
            (cx + 5 + leg_offset, cy), (cx - 5 - leg_offset, cy)
        ])

        # 3. Tronco e Colete com Coldres de Bombas
        chest_y = cy - 25
        pygame.draw.polygon(char_surf, (*COLOR_GRAY_NINJA, self.alpha), [
            (cx - 8, chest_y), (cx + 8, chest_y),
            (cx + 6, cy - 12), (cx - 6, cy - 12)
        ])
        # Faixas cruzadas cinza escuro
        pygame.draw.line(char_surf, (*COLOR_GRAY_DARK, self.alpha), (cx - 7, chest_y + 2), (cx + 7, cy - 13), 2)
        pygame.draw.line(char_surf, (*COLOR_GRAY_DARK, self.alpha), (cx + 7, chest_y + 2), (cx - 7, cy - 13), 2)
        # Mini esferas de bombas na cintura
        pygame.draw.circle(char_surf, (*COLOR_BLACK, self.alpha), (cx - 6, cy - 13), 2)
        pygame.draw.circle(char_surf, (*COLOR_BLACK, self.alpha), (cx + 6, cy - 13), 2)

        # 4. Braços
        face_angle = math.atan2(self.facing_y, self.facing_x)
        arm_x = cx + int(math.cos(face_angle) * 11)
        arm_y = chest_y + int(math.sin(face_angle) * 8) + 3
        pygame.draw.line(char_surf, (*COLOR_GRAY_NINJA, self.alpha), (cx, chest_y + 3), (arm_x, arm_y), 3)

        # 5. Cabeça e Capuz Cinza com Máscara Escura
        head_y = cy - 31
        pygame.draw.circle(char_surf, (*COLOR_GRAY_NINJA, self.alpha), (cx, head_y), 6)
        pygame.draw.rect(char_surf, (*COLOR_GRAY_DARK, self.alpha), (cx - 4, head_y - 1, 8, 5), border_radius=2)
        # Faixa fumê na testa
        pygame.draw.line(char_surf, (*COLOR_SMOKE, self.alpha), (cx - 5, head_y - 3), (cx + 5, head_y - 3), 2)

        if self.is_hidden:
            pygame.draw.circle(char_surf, (120, 220, 100, 200), (cx, cy - 45), 3)

        if self.hp < self.max_hp and self.is_alive:
            pygame.draw.rect(char_surf, (40, 40, 40, 200), (cx - 10, cy - 42, 20, 3))
            pygame.draw.rect(char_surf, (255, 50, 50, 220), (cx - 10, cy - 42, 10, 3))

        char_surf.set_alpha(self.alpha)
        surface.blit(char_surf, (base_sx - 35, base_sy - 45))
