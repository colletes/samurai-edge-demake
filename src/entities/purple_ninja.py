"""
Ninja Roxo (Murasaki): Especialista em Kusarigama (foice curta com corrente e peso de ferro).
Possui ataque especial que puxa o adversário para perto com a corrente, e golpe padrão de foice
de alcance bem curto mas com PRECEDÊNCIA ABSOLUTA sobre qualquer outro ataque.
"""
import math
import pygame
from src.config import (
    COLOR_PURPLE_NINJA, COLOR_PURPLE_DARK, COLOR_PURPLE_AURA, COLOR_CHAIN,
    COLOR_WHITE, COLOR_BLACK, COLOR_GOLD, COLOR_STEEL
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import KusarigamaChainEntity

class PurpleNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Murasaki (Purple Ninja)")
        self.speed = 4.6

        # Ataque Curto de Foice (Kama Strike) com Precedência Absoluta
        self.is_priority_strike = False
        self.kama_cooldown = 0.45
        self.kama_timer = 0.0

        # Ataque Especial: Kusarigama Chain Grapple / Pull
        self.chain_cooldown = 2.0
        self.chain_timer = 0.0

        # Timers da animação de ataque
        self.windup_time = 0.07
        self.active_time = 0.14
        self.recovery_time = 0.28

    def trigger_kama_strike(self, target_wx: float, target_wy: float):
        """
        Ataque Primário: Golpe rápido de foice de alcance bem curto (0.7m),
        mas com PRECEDÊNCIA ABSOLUTA sobre qualquer outro ataque.
        """
        if not self.can_move() or self.kama_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.0
        self.kama_timer = self.kama_cooldown
        self.is_priority_strike = True

        # Avanço súbito à queima-roupa
        self.vx = self.facing_x * 4.5
        self.vy = self.facing_y * 4.5

        # Hitbox curta
        self.hitbox_active = False
        self.hitbox_center = (self.wx + self.facing_x * 0.65, self.wy + self.facing_y * 0.65)
        self.hitbox_radius = 0.70  # Bem curto conforme especificado

    def trigger_kusarigama_pull(self, target_wx: float, target_wy: float, projectiles: list):
        """
        Ataque Secundário / Especial: Arremessa a corrente com peso de ferro para engatar
        e puxar o adversário para perto. O adversário permanece livre para agir/atacar.
        """
        if not self.can_move() or self.chain_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.chain_timer = self.chain_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.18

        # Spawn da corrente saindo das mãos
        chain = KusarigamaChainEntity(
            wx=self.wx + self.facing_x * 0.35,
            wy=self.wy + self.facing_y * 0.35,
            wz=0.4,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self
        )
        projectiles.append(chain)

    def update(self, dt: float, game_map):
        if not self.is_alive:
            self.hitbox_active = False
            self.is_priority_strike = False
            return

        self.update_stealth(game_map)

        if self.kama_timer > 0:
            self.kama_timer -= dt
        if self.chain_timer > 0:
            self.chain_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer += dt
            # Fase 1: Windup curto
            if self.state_timer < self.windup_time:
                self.hitbox_active = False
            # Fase 2: Lâmina ativa com precedência
            elif self.state_timer < (self.windup_time + self.active_time):
                self.hitbox_active = True
                self.is_priority_strike = True
                self.hitbox_center = (self.wx + self.facing_x * 0.65, self.wy + self.facing_y * 0.65)
            # Fase 3: Recovery
            elif self.state_timer < (self.windup_time + self.active_time + self.recovery_time):
                self.hitbox_active = False
                self.is_priority_strike = False
            else:
                self.state = STATE_IDLE
                self.hitbox_active = False
                self.is_priority_strike = False

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.hitbox_active = False
            self.is_priority_strike = False
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        if self.state == STATE_DEAD:
            sx, sy = camera.apply(self.wx, self.wy, 0.0)
            pygame.draw.ellipse(surface, (14, 18, 16, 120), (sx - 18, sy - 8, 36, 16))
            pygame.draw.circle(surface, COLOR_PURPLE_DARK, (sx, sy - 4), 11)
            pygame.draw.line(surface, COLOR_STEEL, (sx - 12, sy - 6), (sx + 8, sy - 1), 3)
            return

        sx, sy = camera.apply(self.wx, self.wy, self.wz)

        # Sombra
        pygame.draw.ellipse(surface, (14, 18, 16, 140), (sx - 16, sy - 6, 32, 12))

        # Efeito de brilho de Precedência Absoluta durante o ataque de foice
        if self.state == STATE_ATTACK and self.hitbox_active:
            for r in range(3):
                pygame.draw.circle(surface, (195, 120, 255, 60), (int(sx), int(sy - 16)), 26 + r * 6, 1)

        # Corpo / Traje Ninja Roxo
        pygame.draw.rect(surface, COLOR_PURPLE_DARK, (sx - 10, sy - 28, 20, 24), border_radius=4)
        pygame.draw.rect(surface, COLOR_PURPLE_NINJA, (sx - 8, sy - 26, 16, 18), border_radius=3)

        # Faixa / Obi no abdômen com elos de corrente pendurados
        pygame.draw.rect(surface, COLOR_BLACK, (sx - 9, sy - 18, 18, 5))
        pygame.draw.line(surface, COLOR_CHAIN, (sx - 7, sy - 13), (sx - 2, sy - 8), 2)
        pygame.draw.line(surface, COLOR_CHAIN, (sx - 2, sy - 8), (sx + 5, sy - 12), 2)

        # Cabeça com capuz e máscara roxa
        pygame.draw.circle(surface, COLOR_PURPLE_NINJA, (sx, sy - 34), 9)
        pygame.draw.rect(surface, COLOR_PURPLE_DARK, (sx - 8, sy - 38, 16, 6))

        # Olhos focados brilhantes (Dourado/Branco)
        eye_ox = int(self.facing_x * 3)
        eye_oy = int(self.facing_y * 2)
        pygame.draw.line(surface, COLOR_GOLD, (sx - 4 + eye_ox, sy - 34 + eye_oy), (sx - 1 + eye_ox, sy - 34 + eye_oy), 2)
        pygame.draw.line(surface, COLOR_GOLD, (sx + 1 + eye_ox, sy - 34 + eye_oy), (sx + 4 + eye_ox, sy - 34 + eye_oy), 2)

        # Arma: Kama (Foice curta)
        kama_hand_x = sx + int(self.facing_x * 12)
        kama_hand_y = sy - 20 + int(self.facing_y * 8)

        if self.state == STATE_ATTACK:
            # Foice golpeando em arco veloz com rastro roxo
            blade_tip_x = kama_hand_x + int(self.facing_x * 18)
            blade_tip_y = kama_hand_y + int(self.facing_y * 12) - 4
            # Cabo de madeira da foice
            pygame.draw.line(surface, (80, 50, 30), (kama_hand_x, kama_hand_y), (blade_tip_x - int(self.facing_x * 6), blade_tip_y), 3)
            # Lâmina curvada de aço afiado com fio violeta
            pygame.draw.line(surface, COLOR_STEEL, (blade_tip_x - int(self.facing_x * 6), blade_tip_y), (blade_tip_x, blade_tip_y - 8), 4)
            pygame.draw.line(surface, COLOR_PURPLE_AURA, (blade_tip_x, blade_tip_y - 8), (blade_tip_x + 6, blade_tip_y - 2), 2)
        else:
            # Foice empunhada em guarda
            pygame.draw.line(surface, (80, 50, 30), (kama_hand_x, kama_hand_y), (kama_hand_x, kama_hand_y - 12), 3)
            pygame.draw.line(surface, COLOR_STEEL, (kama_hand_x, kama_hand_y - 12), (kama_hand_x + 8, kama_hand_y - 14), 3)
