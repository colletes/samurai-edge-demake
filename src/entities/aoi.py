"""
Aoi (A Caçadora Ainu de Hokkaido - Sub-fase 2.22):
Jovem guerreira e rastreadora indígena Ainu das florestas boreais de Ezo (Hokkaido).
- Arquétipo: Caçadora ágil de controle de terreno, armadilhas de dentes de ferro e estocadas lineares de osso (velocidade 5.15, 2 HP).
- Guarda de Caça (Hunter Guard): Deflexão técnica de lâminas com a haste da lança Op e a faca ritual Makiri.
- Ataque Primário: Bone-Tipped Spear Lunge (SPEAR_THRUST) - estocada perfurante veloz de altíssimo alcance (2.20m, raio 0.42m, execução 0.18s, dano 1 HP).
- Ação Secundária: Hunting Bear Trap (BEAR_TRAP) - planta no solo uma armadilha mecânica de mandíbula de ferro camuflada (máx. 2 simultâneas na arena, duração 12.0s). Quem pisar sofre 1 HP de dano mecânico e imobilização completa (Root por 1.4s) com sangramento, abrindo brecha letal para estocada de lança. Cooldown 4.0s.
- Esquiva: Tundra Hunt Slide (SNOW_SLIDE) - deslize rasteiro rente ao solo sobre a neve/terra com 13 i-frames passando por baixo de projéteis e flechas, com recuperação limpa.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_AOI_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, STATE_PARRY,
    resolve_playable_bounds, slide_movement_against_obstacles
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import BearTrapProjectile
from src.effects.particles import SparkParticle, SmokeParticle, FloatingBanner


class AoiHuntress(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Aoi")
        self.char_type = "aoi"
        self.speed = 5.15
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Ataque Primário: Estocada Linear de Lança de Osso (Bone-Tipped Spear Lunge)
        self.spear_duration = 0.18
        self.spear_recovery = 0.28   # Whiff recovery punível
        self.spear_reach = 2.20      # Longo alcance linear
        self.spear_radius = 0.42     # Hitbox frontal estreita de alta precisão

        # Ação Secundária: Armadilha de Urso Mecânica (Hunting Bear Trap)
        self.trap_cooldown = 4.0     # Cooldown calibrado
        self.trap_timer = 0.0
        self.active_traps: list[BearTrapProjectile] = []
        self.is_planting_trap = False

        # Esquiva: Deslize da Taiga (Tundra Hunt Slide)
        self.is_agile_dodge = True
        self.roll_speed = 9.4
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.14
        self.roll_cooldown_duration = 0.32
        self.recovery_duration = self.spear_recovery

    def trigger_parry(self) -> bool:
        """Guarda da Taiga: postura defensiva técnica com a haste da lança Op e a faca Makiri."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.38
        return True

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_spear_thrust(self, aim_x: float = None, aim_y: float = None, particles: list = None) -> bool:
        """Ataque Primário: Estocada linear de altíssimo alcance (2.20m) com ponta afiada de osso de urso."""
        if not self.can_act():
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        self.state = STATE_ATTACK
        self.state_timer = self.spear_duration
        self.hitbox_active = True
        self.hitbox_damage = 1

        self.hitbox_center = (
            self.wx + self.facing_x * 1.35,
            self.wy + self.facing_y * 1.35
        )
        self.hitbox_radius = self.spear_radius
        self.slash_dir = (self.facing_x, self.facing_y)
        self.is_planting_trap = False

        if particles is not None:
            # Silvo cortante de ar gélido na ponta da lança
            for _ in range(5):
                particles.append(SparkParticle(
                    self.wx + self.facing_x * 1.8 + random.uniform(-0.15, 0.15),
                    self.wy + self.facing_y * 1.8 + random.uniform(-0.15, 0.15),
                    0.20,
                    color=(215, 238, 255)
                ))
        return True

    def trigger_attack(self, aim_x: float = None, aim_y: float = None, **kwargs) -> bool:
        """Alias para integração com controles genéricos."""
        return self.trigger_spear_thrust(aim_x, aim_y, particles=kwargs.get("particles"))

    def trigger_bear_trap(self, aim_x: float = None, aim_y: float = None, projectiles: list = None, particles: list = None, banners: list = None, game_map=None) -> bool:
        """
        Ação Secundária: Posiciona uma Armadilha de Urso camuflada no solo à frente de Aoi
        e recua em passo ágil de caçadora (máx 2 simultâneas na arena).
        """
        if not self.can_act() or self.trap_timer > 0 or projectiles is None:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        trap_x = self.wx + self.facing_x * 1.10
        trap_y = self.wy + self.facing_y * 1.10

        if game_map is not None:
            min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
            trap_x = max(min_x + 0.35, min(max_x - 0.35, trap_x))
            trap_y = max(min_y + 0.35, min(max_y - 0.35, trap_y))

        # Manter no máximo 2 armadilhas ativas simultaneamente
        self.active_traps = [t for t in self.active_traps if getattr(t, "is_active", False)]
        if len(self.active_traps) >= 2:
            oldest = self.active_traps.pop(0)
            oldest.detonate()

        trap = BearTrapProjectile(trap_x, trap_y, owner=self, duration=12.0)
        self.active_traps.append(trap)
        projectiles.append(trap)

        # Passo tático de recuo ágil ao armar no solo
        back_x = self.wx - self.facing_x * 0.55
        back_y = self.wy - self.facing_y * 0.55
        if game_map is not None:
            new_wx, new_wy = slide_movement_against_obstacles(self.wx, self.wy, back_x - self.wx, back_y - self.wy, self.radius, game_map)
            self.wx, self.wy = new_wx, new_wy
        else:
            self.wx, self.wy = back_x, back_y

        self.trap_timer = self.trap_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.18
        self.is_planting_trap = True

        if banners is not None:
            banners.append(FloatingBanner("TRAP SET!", trap_x, trap_y, wz=1.4, color=COLOR_AOI_AURA, duration=0.75))

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(trap_x, trap_y, 0.12, color=(205, 225, 245)))

        return True

    def trigger_secondary(self, aim_x: float = None, aim_y: float = None, **kwargs) -> bool:
        """Alias para integração com controles genéricos."""
        return self.trigger_bear_trap(
            aim_x, aim_y,
            projectiles=kwargs.get("projectiles"),
            particles=kwargs.get("particles"),
            banners=kwargs.get("banners"),
            game_map=kwargs.get("game_map")
        )

    def trigger_snow_slide(self, dwx: float, dwy: float, particles: list = None, game_map=None) -> bool:
        """
        Esquiva especial: Deslize rasteiro na neve/terra (Tundra Hunt Slide) com 13 i-frames.
        Passa rente ao solo por baixo de tiros, kunais e flechas com recuperação rápida.
        """
        if not self.can_act() or self.roll_cooldown_timer > 0:
            return False

        mag = math.hypot(dwx, dwy)
        if mag > 0.05:
            self.roll_dir_x = dwx / mag
            self.roll_dir_y = dwy / mag
            self.set_facing(self.wx + self.roll_dir_x, self.wy + self.roll_dir_y)
        else:
            self.roll_dir_x = self.facing_x
            self.roll_dir_y = self.facing_y

        self.state = STATE_ROLL
        self.state_timer = self.roll_duration
        self.is_planting_trap = False

        if particles is not None:
            for _ in range(10):
                particles.append(SparkParticle(
                    self.wx + random.uniform(-0.25, 0.25),
                    self.wy + random.uniform(-0.25, 0.25),
                    random.uniform(0.05, 0.30),
                    color=random.choice([(235, 245, 255), (160, 215, 245), (200, 230, 255)])
                ))
        return True

    def trigger_roll(self, dwx: float, dwy: float, particles: list = None, **kwargs) -> bool:
        """Alias de esquiva."""
        return self.trigger_snow_slide(dwx, dwy, particles=particles, game_map=kwargs.get("game_map"))

    def update_roll(self, dt: float, game_map=None, particles: list = None):
        """Atualiza a física do deslize veloz no gelo/terra."""
        self.state_timer -= dt
        dx = self.roll_dir_x * self.roll_speed * dt
        dy = self.roll_dir_y * self.roll_speed * dt

        if game_map is not None:
            new_wx, new_wy = slide_movement_against_obstacles(self.wx, self.wy, dx, dy, self.radius, game_map)
            self.wx, self.wy = new_wx, new_wy
        else:
            self.wx += dx
            self.wy += dy

        if particles is not None and random.random() < 0.45:
            particles.append(SparkParticle(
                self.wx + random.uniform(-0.15, 0.15),
                self.wy + random.uniform(-0.15, 0.15),
                0.08,
                color=random.choice([(240, 248, 255), (170, 220, 250)])
            ))

        if self.state_timer <= 0:
            self.state = STATE_IDLE
            self.roll_recovery_timer = self.roll_recovery_duration
            self.roll_cooldown_timer = self.roll_cooldown_duration

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None, **kwargs):
        self.update_dodge_timers(dt)

        if self.trap_timer > 0:
            self.trap_timer = max(0.0, self.trap_timer - dt)

        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            return

        if self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Avanço sutil e focado de estocada
            adv = 2.4 * dt
            if game_map is not None:
                new_wx, new_wy = slide_movement_against_obstacles(self.wx, self.wy, self.facing_x * adv, self.facing_y * adv, self.radius, game_map)
                self.wx, self.wy = new_wx, new_wy
            else:
                self.wx += self.facing_x * adv
                self.wy += self.facing_y * adv

            self.hitbox_center = (
                self.wx + self.facing_x * 1.35,
                self.wy + self.facing_y * 1.35
            )
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.spear_recovery
                self.hitbox_active = False
            return

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.is_planting_trap = False
            return

        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        self.active_traps = [t for t in self.active_traps if getattr(t, "is_active", False)]

    def get_extra_props(self) -> dict:
        """Garante propriedades extras e poses ricas para a renderização 3D."""
        extra = {}
        if self.state == STATE_ROLL:
            extra["pose"] = "tundra_hunt_slide"
            extra["is_roll"] = True
            extra["is_slide"] = True
            prog = 1.0 - max(0.0, self.state_timer) / max(0.001, self.roll_duration)
            extra["roll_prog"] = prog
            extra["slide_prog"] = prog
            extra["p"] = prog
        elif self.state in ("DEFEND", STATE_PARRY) or getattr(self, "is_parrying", False):
            extra["pose"] = "hunter_guard"
            extra["is_parry"] = True
        elif self.state == STATE_ATTACK:
            prog = 1.0 - max(0.0, self.state_timer) / max(0.001, self.spear_duration)
            extra["pose"] = "spear_lunge"
            extra["atk_progress"] = prog
            extra["p"] = prog
        elif self.state == STATE_RECOVERY and self.is_planting_trap:
            extra["pose"] = "bear_trap_place"
            extra["is_trap"] = True
        return extra

    def render(self, surface: pygame.Surface, camera):
        extra = self.get_extra_props()

        render_voxel_humanoid(
            surface=surface,
            camera=camera,
            wx=self.wx,
            wy=self.wy,
            wz=getattr(self, "wz", 0.0),
            facing_x=self.facing_x,
            facing_y=self.facing_y,
            state=self.state,
            state_timer=self.state_timer,
            is_alive=self.is_alive,
            char_type="aoi",
            walk_timer=getattr(self, "walk_cycle", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
