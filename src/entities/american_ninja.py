"""
American Ninja: Guerreiro tático acompanhado pelo seu leal cão Doberman.
Ataca com Shurikens atordoantes (não matam) e comanda o Doberman para botes letais.
"""
import math
import pygame
from src.config import (
    COLOR_AMERICAN_NINJA, COLOR_AMERICAN_VEST, COLOR_AMERICAN_BANDANA,
    COLOR_STEEL, COLOR_WHITE, COLOR_BLACK, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.doberman import DobermanDog
from src.entities.projectile import ShurikenProjectile

class AmericanNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Joe (American Ninja)")
        self.speed = 4.8

        # O Cão Doberman companheiro
        self.dog = DobermanDog(self)

        # Timings de Shuriken e Comando
        self.shuriken_cooldown = 0.35
        self.shuriken_timer = 0.0

    def trigger_shuriken(self, target_wx: float, target_wy: float, projectiles: list):
        """Arremessa uma shuriken atordoante (não mata, mas dá stun de 0.48s)."""
        if not self.can_move() or self.shuriken_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.shuriken_timer = self.shuriken_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.12

        shuriken = ShurikenProjectile(
            wx=self.wx + self.facing_x * 0.4,
            wy=self.wy + self.facing_y * 0.4,
            wz=0.6,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self
        )
        projectiles.append(shuriken)

    def trigger_dog_attack(self, target_wx: float, target_wy: float):
        """Ordena o Doberman a disparar em um dash de mordida letal (1-hit kill)."""
        if not self.can_move():
            return
        if self.dog and self.dog.can_attack():
            self.set_facing(target_wx, target_wy)
            self.state = STATE_RECOVERY
            self.state_timer = 0.15
            self.dog.charge(target_wx, target_wy)

    def update(self, dt: float, game_map):
        """Atualiza o Ninja e seu Doberman."""
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.shuriken_timer > 0:
            self.shuriken_timer -= dt

        if self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        # Atualiza a IA e movimentação do Doberman
        if self.dog:
            self.dog.update(dt, game_map)

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o American Ninja com colete tático e bandana vermelha."""
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

        char_surf = pygame.Surface((70, 70), pygame.SRCALPHA)
        cx, cy = 35, 45

        # 1. Sombra no chão
        pygame.draw.ellipse(char_surf, (10, 15, 12, 120), (cx - 14, cy - 6, 28, 12))

        if not self.is_alive:
            pygame.draw.ellipse(char_surf, (*COLOR_AMERICAN_NINJA, self.alpha), (cx - 16, cy - 8, 32, 14))
            pygame.draw.circle(char_surf, (*COLOR_AMERICAN_BANDANA, self.alpha), (cx - 14, cy - 4), 6)
            char_surf.set_alpha(self.alpha)
            surface.blit(char_surf, (base_sx - 35, base_sy - 45))
            return

        # 2. Pernas / Calça Tática Preta
        leg_offset = math.sin(self.walk_cycle) * 4.0 if self.state == STATE_WALK else 0.0
        pygame.draw.polygon(char_surf, (*COLOR_AMERICAN_NINJA, self.alpha), [
            (cx - 7, cy - 14), (cx + 7, cy - 14),
            (cx + 5 + leg_offset, cy), (cx - 5 - leg_offset, cy)
        ])

        # 3. Tronco e Colete Tático Militar (Cinza sobre Preto)
        chest_y = cy - 25
        pygame.draw.polygon(char_surf, (*COLOR_AMERICAN_NINJA, self.alpha), [
            (cx - 8, chest_y), (cx + 8, chest_y),
            (cx + 6, cy - 12), (cx - 6, cy - 12)
        ])
        # Colete tático cinza
        pygame.draw.rect(char_surf, (*COLOR_AMERICAN_VEST, self.alpha), (cx - 6, chest_y + 2, 12, 10), border_radius=2)
        # Cinto tático com fivela dourada
        pygame.draw.line(char_surf, (*COLOR_BLACK, self.alpha), (cx - 6, cy - 13), (cx + 6, cy - 13), 3)
        pygame.draw.rect(char_surf, (*COLOR_GOLD, self.alpha), (cx - 2, cy - 14, 4, 3))

        # 4. Braços e Pose
        face_angle = math.atan2(self.facing_y, self.facing_x)
        # Mão apontando ou em posição de saque de shuriken
        arm_x = cx + int(math.cos(face_angle) * 12)
        arm_y = chest_y + int(math.sin(face_angle) * 8) + 3
        pygame.draw.line(char_surf, (*COLOR_AMERICAN_NINJA, self.alpha), (cx, chest_y + 3), (arm_x, arm_y), 3)
        pygame.draw.circle(char_surf, (240, 205, 180, self.alpha), (arm_x, arm_y), 3)

        # 5. Cabeça e Bandana Vermelha Estilo Anos 80
        head_y = cy - 31
        # Rosto
        pygame.draw.circle(char_surf, (240, 205, 180, self.alpha), (cx, head_y), 5)
        # Cabelo castanho/preto
        pygame.draw.circle(char_surf, (30, 25, 25, self.alpha), (cx, head_y - 3), 5)
        # Bandana Vermelha na testa
        pygame.draw.line(char_surf, (*COLOR_AMERICAN_BANDANA, self.alpha), (cx - 5, head_y - 2), (cx + 5, head_y - 2), 3)
        # Pontas da bandana voando para trás
        tail_bx = cx - int(self.facing_x * 8)
        tail_by = head_y - 2 - int(self.facing_y * 4)
        pygame.draw.line(char_surf, (*COLOR_AMERICAN_BANDANA, self.alpha), (cx - 4, head_y - 2), (tail_bx, tail_by), 2)

        if self.is_hidden:
            pygame.draw.circle(char_surf, (120, 220, 100, 200), (cx, cy - 45), 3)

        # Barra de Vida se ferido
        if self.hp < self.max_hp and self.is_alive:
            pygame.draw.rect(char_surf, (40, 40, 40, 200), (cx - 10, cy - 42, 20, 3))
            pygame.draw.rect(char_surf, (255, 50, 50, 220), (cx - 10, cy - 42, 10, 3))

        char_surf.set_alpha(self.alpha)
        surface.blit(char_surf, (base_sx - 35, base_sy - 45))
