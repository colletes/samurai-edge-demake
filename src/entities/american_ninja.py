"""
American Ninja: Guerreiro tático acompanhado pelo seu leal cão Doberman (Yamato).
Ataca com Shurikens velozes (15.5 m/s, cooldown 0.90s) e comanda Yamato para botes letais.
Possui sequência de flic-flacs acrobáticos para trás (encadeáveis até 3x com colisão/atordoamento em obstáculos).
"""
import math
import pygame
from src.config import (
    COLOR_AMERICAN_NINJA, COLOR_AMERICAN_VEST, COLOR_AMERICAN_BANDANA,
    COLOR_STEEL, COLOR_WHITE, COLOR_BLACK, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_ROLL,
    slide_movement_against_obstacles
)
from src.entities.doberman import DobermanDog
from src.entities.projectile import ShurikenProjectile
from src.entities.voxel_models import render_voxel_humanoid

class AmericanNinja(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Joe")
        self.char_type = "joe"
        self.speed = 5.5

        # O Cão Doberman companheiro (Yamato)
        self.dog = DobermanDog(self)

        # Timings de Shuriken e Comando (Disparo rápido 0.45s com micro-stun)
        self.shuriken_cooldown = 0.45
        self.shuriken_timer = 0.0

        # Terceira Ação: Sequência de Flic-Flacs Acrobáticos para frente (Encadeamento ágil e contínuo)
        self.is_agile_dodge = True
        self.roll_speed = 9.8
        self.roll_duration = 0.26
        self.roll_recovery_duration = 0.03
        self.roll_cooldown_duration = 0.02
        self.flic_flac_chain = 0
        self.roll_dir_x = 1.0
        self.roll_dir_y = 0.0

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
            and getattr(self, "wz", 0.0) <= 0.05
        )

    def trigger_shuriken(self, target_wx: float, target_wy: float, projectiles: list):
        """Arremessa uma shuriken rápida a 16.5 m/s com alta cadência e micro-stun."""
        if not self.can_act() or self.shuriken_timer > 0:
            return False

        self.set_facing(target_wx, target_wy)
        self.shuriken_timer = self.shuriken_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.08

        shuriken = ShurikenProjectile(
            wx=self.wx + self.facing_x * 0.4,
            wy=self.wy + self.facing_y * 0.4,
            wz=0.6,
            dir_x=self.facing_x,
            dir_y=self.facing_y,
            owner=self
        )
        projectiles.append(shuriken)
        return True

    def trigger_dog_attack(self, target_wx: float, target_wy: float, target_entity=None):
        """Ordena o Doberman a disparar em um bote veloz com teleguiamento (1-hit kill fatal)."""
        if not self.can_act():
            return False
        if self.dog and self.dog.can_attack():
            self.set_facing(target_wx, target_wy)
            self.state = STATE_RECOVERY
            self.state_timer = 0.12
            self.dog.charge(target_wx, target_wy, target_entity=target_entity)
            return True
        return False

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None):
        """
        Flic-Flac Acrobático na direção do movimento/visada:
        - Salto acrobático 360° fluido para frente na direção em que o jogador olha.
        - Encadeável sem travamentos para atravessar o combate com extrema agilidade.
        """
        if (
            not self.is_alive
            or self.state in (STATE_STUNNED, STATE_DEAD, STATE_ATTACK)
            or getattr(self, "wz", 0.0) > 0.45
        ):
            return False

        # Se já estiver em ROLL, permite encadear se estiver nos últimos 35% do salto
        if self.state == STATE_ROLL:
            if self.state_timer > 0.09:
                return False

        # Direção do salto: se houver entrada direcional, segue a entrada; senão, segue o facing atual
        d_len = math.hypot(dir_x, dir_y)
        if d_len > 0.1:
            self.roll_dir_x = dir_x / d_len
            self.roll_dir_y = dir_y / d_len
            self.facing_x = self.roll_dir_x
            self.facing_y = self.roll_dir_y
        else:
            self.roll_dir_x = self.facing_x
            self.roll_dir_y = self.facing_y

        self.state = STATE_ROLL
        self.state_timer = self.roll_duration
        self.is_invulnerable_dodge = True
        self.flic_flac_chain += 1

        try:
            from src.audio.sound_manager import get_sound_manager
            from src.audio.sound_events import SoundEvent
            get_sound_manager().play(SoundEvent.DODGE_WHOOSH, volume_scale=0.9)
        except Exception:
            pass

        return True

    def update_roll(self, dt: float, game_map):
        """Atualiza a trajetória do flic-flac com detecção de impacto em obstáculos sólidos."""
        if self.state != STATE_ROLL:
            return

        self.state_timer -= dt
        prog = max(0.0, min(1.0, 1.0 - (self.state_timer / self.roll_duration)))

        # Arco parabólico de altura no salto
        self.wz = math.sin(prog * math.pi) * 0.42

        step = self.roll_speed * dt
        dx = self.roll_dir_x * step
        dy = self.roll_dir_y * step

        new_wx, new_wy = slide_movement_against_obstacles(self.wx, self.wy, dx, dy, self.radius, game_map)

        # Checagem de colisão com obstáculo sólido (rocha, poço, parede ou limite de mapa)
        blocked_dist = math.hypot((self.wx + dx) - new_wx, (self.wy + dy) - new_wy)
        if blocked_dist > 0.05:
            # Bateu em obstáculo rígido: atordoamento imediato de 0.60s e quebra da cadeia de saltos!
            self.state = STATE_STUNNED
            self.state_timer = 0.60
            self.wz = 0.0
            self.is_invulnerable_dodge = False
            self.flic_flac_chain = 0
            self.roll_recovery_timer = 0.30
            self.roll_cooldown_timer = 0.40
            try:
                from src.audio.sound_manager import get_sound_manager
                from src.audio.sound_events import SoundEvent
                get_sound_manager().play(SoundEvent.OBSTACLE_HIT, volume_scale=1.0)
            except Exception:
                pass
            return

        self.wx, self.wy = new_wx, new_wy

        if self.state_timer <= 0:
            self.state = STATE_IDLE
            self.wz = 0.0
            self.is_invulnerable_dodge = False
            # Intervalo mínimo de recuperação para permitir encadeamento fluido e infinito
            self.roll_recovery_timer = 0.02
            self.roll_cooldown_timer = 0.01
            self.dash_recovery_timer = 0.02

    def update(self, dt: float, game_map):
        """Atualiza o Ninja e seu Doberman."""
        if not self.is_alive:
            return

        self.update_stealth(game_map)
        self.update_dodge_timers(dt)

        if self.shuriken_timer > 0:
            self.shuriken_timer -= dt

        if self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_ROLL:
            self.update_roll(dt, game_map)

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        # Atualiza a IA e movimentação do Doberman (Yamato)
        if self.dog:
            self.dog.update(dt, game_map)

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o American Ninja no autêntico estilo Voxel 3D Isométrico."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        extra_props = {}
        if self.state == STATE_ROLL:
            prog = max(0.0, min(1.0, 1.0 - (self.state_timer / max(0.001, self.roll_duration))))
            extra_props = {
                "pose": "flic_flac",
                "p": prog,
                "somersault_angle": 360.0 * prog,
                "flic_flac": True,
            }

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="american",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props=extra_props
        )
