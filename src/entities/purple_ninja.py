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
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_ROLL
)
from src.entities.projectile import KusarigamaChainEntity
from src.entities.voxel_models import render_voxel_humanoid

class PurpleNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Murasaki")
        self.char_type = "murasaki"
        self.speed = 5.1  # Velocidade ágil e evasiva de kunoichi das sombras

        # Ataque Curto de Foice (Kama Strike)
        self.is_priority_strike = False
        self.kama_cooldown = 0.35
        self.kama_timer = 0.0

        # Ataque Especial: Kusarigama Chain Grapple / Pull
        self.chain_cooldown = 3.2  # Cooldown aumentado (era 2.5s) para cadência mais justa
        self.chain_timer = 0.0

        # Timers da animação de ataque (windup 0.04s, janela ativa ampliada para 0.22s - Entregável 4.2)
        self.windup_time = 0.04
        self.active_time = 0.22
        self.recovery_time = 0.28

        # Escudo de Corrente Hold & Release (Item 24)
        self.chain_spin_timer = 0.0
        self.is_spinning_chain = False
        self.is_holding_shield = False
        self.shield_spin_angle = 0.0

        # Terceira Ação: Esquiva Ágil Shinobi (Chain Whirl Backflip)
        self.is_agile_dodge = True
        self.roll_speed = 9.5
        self.roll_duration = 0.28
        self.roll_recovery_duration = 0.10
        self.roll_cooldown_duration = 0.35
        self.pose_lerp_tracker = {"lerp_duration": 0.08, "blend_timer": 0.0, "pose_key": None}

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def can_move(self) -> bool:
        if self.is_holding_shield:
            return self.is_alive
        return super().can_move()

    def apply_movement(self, move_x: float, move_y: float, dt: float, game_map):
        if self.is_holding_shield:
            orig = self.speed
            self.speed = orig * 0.70  # Movimentação suave enquanto mantém o escudo giratório
            super().apply_movement(move_x, move_y, dt, game_map)
            self.speed = orig
        else:
            super().apply_movement(move_x, move_y, dt, game_map)

    def trigger_kama_strike(self, target_wx: float, target_wy: float, game_map = None, particles = None):
        """
        Ataque Primário: Golpe rápido de foice de alcance ampliado (1.15m),
        com PRECEDÊNCIA ABSOLUTA sobre qualquer outro ataque. Corta bambus no caminho.
        """
        if not self.can_act() or self.kama_timer > 0:
            return False

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.0
        self.kama_timer = self.kama_cooldown
        self.is_priority_strike = False  # Ajustado: Murasaki agora entra em QTE de choque de lâminas (clash) normalmente

        # Avanço súbito à queima-roupa
        self.vx = self.facing_x * 4.5
        self.vy = self.facing_y * 4.5

        # Hitbox ampliada para 1.50m de alcance da foice
        self.hitbox_active = False
        self.hitbox_center = (self.wx + self.facing_x * 0.95, self.wy + self.facing_y * 0.95)
        self.hitbox_radius = 1.50

        if game_map:
            for b in game_map.bamboos:
                if not b.is_cut and math.hypot(self.hitbox_center[0] - b.wx, self.hitbox_center[1] - b.wy) < 0.65:
                    part = b.cut((self.facing_x, self.facing_y))
                    if part and particles is not None:
                        particles.append(part)
        return True

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None):
        """Roll evasivo sombrio: sem faíscas, com névoa violeta (Item 12)."""
        if not self.is_alive or self.state in (STATE_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK) or self.dash_recovery_timer > 0:
            return False

        res = super().trigger_roll(dir_x, dir_y, particles=None)  # Sem faíscas
        if not res:
            return False
        if particles is not None:
            from src.effects.particles import SmokeParticle
            for _ in range(8):
                particles.append(SmokeParticle(self.wx, self.wy, 0.35, color=(85, 45, 115), size=5))
        return True

    def start_chain_shield(self, target_wx: float, target_wy: float):
        """Inicia o escudo giratório de corrente (Hold - Item 24)."""
        if not self.can_act() or self.chain_timer > 0:
            return False
        self.set_facing(target_wx, target_wy)
        self.is_holding_shield = True
        self.is_spinning_chain = True
        self.shield_spin_angle = 0.0
        return True

    def update_chain_shield(self, dt: float, target_wx: float, target_wy: float):
        """Atualiza a mira/direção e giro protetor da corrente enquanto segurado (Item 24)."""
        if not self.is_alive or not self.is_holding_shield:
            self.is_holding_shield = False
            self.is_spinning_chain = False
            return
        self.set_facing(target_wx, target_wy)
        self.shield_spin_angle += dt * 35.0
        self.is_spinning_chain = True

    def release_chain_shield(self, projectiles: list, particles: list = None):
        """Dispara a corrente ao soltar o botão de secundário (Release - Item 24)."""
        if not self.is_holding_shield or not self.is_alive:
            self.is_holding_shield = False
            self.is_spinning_chain = False
            return
        self.is_holding_shield = False
        self.is_spinning_chain = False
        self.chain_timer = self.chain_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.18

        chain = KusarigamaChainEntity(
            wx=self.wx + self.facing_x * 0.35,
            wy=self.wy + self.facing_y * 0.35,
            wz=0.4,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self
        )
        projectiles.append(chain)
        if particles is not None:
            from src.effects.particles import SparkParticle
            for _ in range(6):
                particles.append(SparkParticle(chain.wx, chain.wy, 0.3))

    def trigger_kusarigama_pull(self, target_wx: float, target_wy: float, projectiles: list):
        """Compatibilidade para IA e testes legados."""
        self.start_chain_shield(target_wx, target_wy)
        self.release_chain_shield(projectiles)

    def update(self, dt: float, game_map):
        if not self.is_alive:
            self.hitbox_active = False
            self.is_priority_strike = False
            self.is_spinning_chain = False
            self.is_holding_shield = False
            return

        self.update_stealth(game_map)
        self.update_dodge_timers(dt)

        if not self.is_holding_shield:
            if self.chain_spin_timer > 0:
                self.chain_spin_timer -= dt
                self.is_spinning_chain = (self.chain_spin_timer > 0)
            else:
                self.is_spinning_chain = False

        if self.kama_timer > 0:
            self.kama_timer -= dt
        if self.chain_timer > 0:
            self.chain_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer += dt
            # Fase 1: Windup ultra-curto (0.04s)
            if self.state_timer < self.windup_time:
                self.hitbox_active = False
            # Fase 2: Lâmina ativa (1.15m de alcance)
            elif self.state_timer < (self.windup_time + self.active_time):
                self.hitbox_active = True
                self.is_priority_strike = False
                self.hitbox_center = (self.wx + self.facing_x * 0.80, self.wy + self.facing_y * 0.80)
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

        elif self.state == STATE_ROLL:
            self.update_roll(dt, game_map)
            if self.state == STATE_IDLE:
                self.dash_recovery_timer = self.dash_recovery_duration

        elif self.state == STATE_STUNNED:
            self.hitbox_active = False
            self.is_priority_strike = False
            self.is_spinning_chain = False
            self.is_holding_shield = False
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza Murasaki no autêntico estilo Voxel 3D Isométrico com animações fluidas e SSAA 2x."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        extra_props = {
            "ssaa_2x": getattr(self, "ssaa_enabled", True),
            "pose_lerp_tracker": getattr(self, "pose_lerp_tracker", None),
        }

        # Durante esquiva / roll (Chain Whirl Backflip com giro mortal 360°)
        is_roll = (self.state == STATE_ROLL)
        if is_roll:
            roll_prog = max(0.0, min(1.0, 1.0 - (self.state_timer / max(0.001, self.roll_duration))))
            extra_props["roll_prog"] = roll_prog
            extra_props["pose"] = "chain_whirl_backflip"
            extra_props["somersault_angle"] = 360.0 * roll_prog
            extra_props["somersault_pivot_z"] = self.wz + 0.30
            extra_props["is_roll"] = True

        elif self.is_holding_shield:
            extra_props["pose"] = "chain_shield"

        elif self.state == STATE_ATTACK:
            prog = max(0.0, min(1.0, self.state_timer / max(0.001, self.windup_time + self.active_time + self.recovery_time)))
            extra_props["pose"] = "kama_strike"
            extra_props["p"] = prog

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="murasaki",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props=extra_props
        )
