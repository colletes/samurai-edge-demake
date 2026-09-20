"""
Ninja Amarelo (Hanzo): Mestre furtivo de artes ninjas e kunai.
Possui velocidade máxima (igual ao Kenshin), estocada rápida corpo a corpo (requer 2 acertos)
e arremesso de kunai mortal à distância (1-hit kill, mas requer pegar a kunai do solo).
"""
import math
import pygame
from src.config import (
    COLOR_YELLOW_NINJA, COLOR_YELLOW_DARK, COLOR_NINJA_MASK,
    COLOR_YELLOW_AURA, COLOR_STEEL, COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import KunaiProjectile

class YellowNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Hanzo (Ninja)")
        self.speed = 5.4  # Mesma velocidade máxima do Kenshin!

        # Atributos de Kunai
        self.has_kunai = True
        self.thrust_duration = 0.14
        self.recovery_duration = 0.15
        self.thrust_step = 0.0

    def trigger_thrust_attack(self, target_wx: float, target_wy: float):
        """Ataque Melee Padrão: Estocada rápida com a kunai (causa 1 de dano)."""
        if not self.can_move() or not self.has_kunai:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = self.thrust_duration
        self.hitbox_active = True
        self.hitbox_radius = 1.05
        self.slash_dir = (self.facing_x, self.facing_y)
        self.hitbox_center = (self.wx + self.facing_x * 0.85, self.wy + self.facing_y * 0.85)

    def trigger_throw_attack(self, target_wx: float, target_wy: float, projectiles: list):
        """Ataque Ranged: Arremessa a kunai em linha reta (1-hit kill mortal)."""
        if not self.can_move() or not self.has_kunai:
            return

        self.set_facing(target_wx, target_wy)
        self.has_kunai = False
        self.state = STATE_RECOVERY
        self.state_timer = 0.18

        # Cria a kunai em vôo
        kunai = KunaiProjectile(
            wx=self.wx + self.facing_x * 0.4,
            wy=self.wy + self.facing_y * 0.4,
            wz=0.6,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self
        )
        projectiles.append(kunai)

    def update(self, dt: float, game_map):
        """Atualiza a lógica do Ninja Amarelo."""
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Pequeno impulso na estocada
            thrust_speed = 4.0
            new_wx = self.wx + self.facing_x * thrust_speed * dt
            new_wy = self.wy + self.facing_y * thrust_speed * dt

            # Colisão com rochas/poço
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
                self.stun(0.6)
                return

            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            self.hitbox_center = (self.wx + self.facing_x * 0.85, self.wy + self.facing_y * 0.85)

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
                self.hitbox_active = False

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Ninja Amarelo com traje de shinobi e kunai."""
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

        char_surf = pygame.Surface((70, 70), pygame.SRCALPHA)
        cx, cy = 35, 45

        # 1. Sombra no chão
        pygame.draw.ellipse(char_surf, (10, 15, 12, 120), (cx - 14, cy - 6, 28, 12))

        if not self.is_alive:
            pygame.draw.ellipse(char_surf, (*COLOR_YELLOW_NINJA, self.alpha), (cx - 16, cy - 8, 32, 14))
            pygame.draw.circle(char_surf, (*COLOR_NINJA_MASK, self.alpha), (cx - 14, cy - 4), 6)
            char_surf.set_alpha(self.alpha)
            surface.blit(char_surf, (base_sx - 35, base_sy - 45))
            return

        # 2. Pernas / Calça Shinobi Amarela
        leg_offset = math.sin(self.walk_cycle) * 4.0 if self.state == STATE_WALK else 0.0
        pygame.draw.polygon(char_surf, (*COLOR_YELLOW_NINJA, self.alpha), [
            (cx - 7, cy - 14), (cx + 7, cy - 14),
            (cx + 5 + leg_offset, cy), (cx - 5 - leg_offset, cy)
        ])
        # Faixas pretas nas canelas (Kyahan)
        pygame.draw.line(char_surf, (*COLOR_NINJA_MASK, self.alpha), (cx - 6, cy - 4), (cx + 6, cy - 4), 2)

        # 3. Tronco (Colete Shinobi Amarelo com cinto preto)
        chest_y = cy - 25
        pygame.draw.polygon(char_surf, (*COLOR_YELLOW_NINJA, self.alpha), [
            (cx - 8, chest_y), (cx + 8, chest_y),
            (cx + 6, cy - 12), (cx - 6, cy - 12)
        ])
        # Cinto de utilidades preto
        pygame.draw.line(char_surf, (*COLOR_NINJA_MASK, self.alpha), (cx - 6, cy - 13), (cx + 6, cy - 13), 3)

        # 4. Braços e Kunai
        face_angle = math.atan2(self.facing_y, self.facing_x)

        if self.has_kunai:
            if self.state == STATE_ATTACK:
                # Estocada frontal com a kunai esticada!
                kx = cx + int(math.cos(face_angle) * 20)
                ky = chest_y + int(math.sin(face_angle) * 12)
                pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx, chest_y), (kx, ky), 3)
                pygame.draw.circle(char_surf, (*COLOR_GOLD, self.alpha), (kx, ky), 3)
                # Faísca amarela na ponta
                pygame.draw.circle(char_surf, (*COLOR_YELLOW_AURA, self.alpha), (kx, ky), 2)
            else:
                # Kunai empunhada em posição de combate invertida (estilo ninja)
                kx = cx + int(math.cos(face_angle) * 10)
                ky = chest_y + int(math.sin(face_angle) * 8) + 4
                pygame.draw.line(char_surf, (*COLOR_STEEL, self.alpha), (cx, chest_y), (kx, ky), 3)
                pygame.draw.circle(char_surf, (*COLOR_GOLD, self.alpha), (kx, ky), 2)
        else:
            # Desarmado: mãos abertas em postura defensiva desarmada
            pygame.draw.circle(char_surf, (240, 200, 160, self.alpha), (cx - 6, chest_y + 4), 3)
            pygame.draw.circle(char_surf, (240, 200, 160, self.alpha), (cx + 6, chest_y + 4), 3)
            # Indicador de alerta acima da cabeça (Sem Kunai!)
            pygame.draw.circle(char_surf, (255, 80, 80, 220), (cx, cy - 42), 3)

        # 5. Cabeça e Capuz Shinobi
        head_y = cy - 31
        # Capuz amarelo
        pygame.draw.circle(char_surf, (*COLOR_YELLOW_NINJA, self.alpha), (cx, head_y), 6)
        # Máscara facial preta
        pygame.draw.rect(char_surf, (*COLOR_NINJA_MASK, self.alpha), (cx - 4, head_y - 1, 8, 5), border_radius=2)
        # Faixa da testa preta com placa de metal
        pygame.draw.line(char_surf, (*COLOR_NINJA_MASK, self.alpha), (cx - 5, head_y - 4), (cx + 5, head_y - 4), 2)
        pygame.draw.circle(char_surf, (*COLOR_STEEL, self.alpha), (cx, head_y - 4), 2)

        # Indicador de Stealth se escondido
        if self.is_hidden:
            pygame.draw.circle(char_surf, (120, 220, 100, 200), (cx, cy - 45), 3)

        # Barra de Vida (se tomou dano mas ainda está vivo)
        if self.hp < self.max_hp and self.is_alive:
            pygame.draw.rect(char_surf, (40, 40, 40, 200), (cx - 10, cy - 42, 20, 3))
            pygame.draw.rect(char_surf, (255, 50, 50, 220), (cx - 10, cy - 42, 10, 3))

        char_surf.set_alpha(self.alpha)
        surface.blit(char_surf, (base_sx - 35, base_sy - 45))
