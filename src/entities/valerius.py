"""
Valerius (O Necromante Prussiano - Ciclo 4):
Aristocrata prussiano e necromante misterioso em terras nipônicas durante a era Bakumatsu.
- Arquétipo: Lutador tático de alcance com foice fúnebre e controle de campo com lacaios esqueléticos (velocidade 4.5, 2 HP).
- Guarda de Foice (Parry técnico com o cabo reforçado e a lâmina da foice).
- Ataque Primário: Foice Fúnebre (SOUL_REAP) - ceifada ampla em arco largo (alcance 2.25m, raio 1.35m, dano 2). No golpe fatal, decapita a cabeça do rival prendendo-a na ponta da foice, recolhe-a na mão e reanima o cadáver decapitado transformando-o em um esqueleto servo.
- Ação Secundária: Evocar Mortos (SKELETON_SUMMON) - ergue do solo um esqueleto guerreiro voxel que rasteja e avança contra o rival, causando 1 de dano e imobilização de 1.4s ao agarrar, ou estilhaça em pó de ossos se golpeado. Cooldown 4.5s.
- Esquiva: Névoa Espectral (MIST_DASH) - deslizamento etéreo com fumaça esmeralda e violeta fúnebre.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_VALERIUS_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, STATE_PARRY, resolve_playable_bounds
)
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric.iso_math import world_distance
from src.effects.particles import SparkParticle, SmokeParticle, FloatingBanner


class SkeletonSummon:
    """
    Esqueleto guerreiro invocado das profundezas fúnebres por Valerius.
    - 1 HP: estilhaça com qualquer golpe, projétil ou parry adversário.
    - Emerge do solo envolto em névoa espectral (0.35s de surgimento).
    - Persegue o oponente a velocidade 3.8m/s.
    - Ao colidir (< 0.85m), agarra as pernas do rival: inflige 1 de dano e 1.4s de stun/lentidão, desfazendo-se em pó.
    - Modelo 100% 3D low-poly facetado (crânio com órbitas ocas, costelas e vértebras voxel).
    """
    def __init__(self, owner, wx: float, wy: float, opponent=None):
        self.owner = owner
        self.opponent = opponent
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.facing_x = 1.0
        self.facing_y = 0.0

        self.hp = 1
        self.is_alive = True
        self.state = "EMERGING"  # "EMERGING", "CHASING", "DEAD"
        self.emerge_timer = 0.40
        self.speed = 2.65  # Velocidade calibrada de esqueleto para permitir contra-ataque e fuga tática
        self.radius = 0.38
        self.anim_time = 0.0
        self.grab_cooldown = 0.0

    def take_hit(self, slash_dir: tuple[float, float] = (0.0, 0.0), damage: int = 1, particles: list = None) -> bool:
        """Destrói instantaneamente o esqueleto em fragmentos de ossos."""
        if not self.is_alive:
            return False
        self.is_alive = False
        self.state = "DEAD"
        if particles is not None:
            # Fragmentos de ossos brancos e faíscas espectrais esmeralda
            for _ in range(16):
                particles.append(SparkParticle(
                    self.wx + random.uniform(-0.15, 0.15),
                    self.wy + random.uniform(-0.15, 0.15),
                    random.uniform(0.1, 0.6),
                    color=random.choice([(235, 230, 215), (210, 205, 195), (65, 230, 170)])
                ))
        return True

    def update(self, dt: float, game_map, opponent, particles: list = None, banners: list = None) -> bool:
        """Atualiza a física, inteligência de perseguição e detecção de bote."""
        if not self.is_alive:
            return False

        self.anim_time += dt
        if opponent is not None:
            self.opponent = opponent

        if self.state == "EMERGING":
            self.emerge_timer -= dt
            self.wz = -0.45 * (self.emerge_timer / 0.35)
            if particles is not None and random.random() < 0.35:
                particles.append(SmokeParticle(
                    self.wx + random.uniform(-0.15, 0.15),
                    self.wy + random.uniform(-0.15, 0.15),
                    wz=0.05,
                    color=(55, 30, 65),
                    radius=0.15,
                    lifetime=0.4
                ))
            if self.emerge_timer <= 0:
                self.state = "CHASING"
                self.wz = 0.0
            return True

        elif self.state == "CHASING":
            if not self.opponent or not getattr(self.opponent, "is_alive", False):
                return True

            dx = self.opponent.wx - self.wx
            dy = self.opponent.wy - self.wy
            dist = math.hypot(dx, dy)

            if dist > 0.001:
                self.facing_x = dx / dist
                self.facing_y = dy / dist

            # Deslocamento em direção ao oponente com amortecimento em terreno
            step = self.speed * dt
            if dist > step:
                self.wx += self.facing_x * step
                self.wy += self.facing_y * step
            else:
                self.wx = self.opponent.wx
                self.wy = self.opponent.wy

            # Detecção de agarre nos tornozelos (Bote)
            if dist <= 0.82 and getattr(self.opponent, "is_alive", True):
                # Se o oponente estiver em Parry ou com ataque ativo virado contra o esqueleto, o esqueleto é destruído
                opp_facing_skeleton = (self.opponent.facing_x * (-self.facing_x) + self.opponent.facing_y * (-self.facing_y)) > 0.0
                if getattr(self.opponent, "state", "") == STATE_PARRY and opp_facing_skeleton:
                    self.take_hit(damage=1, particles=particles)
                    if banners is not None:
                        banners.append(FloatingBanner("PARRY SUMMON!", self.wx, self.wy, wz=1.4, color=(100, 200, 255)))
                    return False

                # Dano e imobilização espectral calibrada
                hit, dead = self.opponent.take_hit((self.facing_x, self.facing_y), damage=1)
                if getattr(self.opponent, "is_alive", True):
                    self.opponent.stun(0.45)
                if banners is not None:
                    banners.append(FloatingBanner("CORPSE GRAB!", self.opponent.wx, self.opponent.wy, wz=1.6, color=(140, 70, 180)))
                self.take_hit(damage=1, particles=particles)
                return False

            # Partículas ocasionais de poeira e névoa no solo
            if particles is not None and random.random() < 0.20:
                particles.append(SparkParticle(
                    self.wx, self.wy, 0.05,
                    color=(65, 230, 170)
                ))

        return self.is_alive

    def render(self, surface: pygame.Surface, camera):
        """Renderização 3D low-poly de anatomia esquelética facetada com Painter's Algorithm."""
        if not self.is_alive:
            return

        from src.isometric.mesh_primitives import draw_voxel_box, draw_oriented_voxel_box

        c_bone = (235, 230, 215)
        c_bone_shadow = (185, 180, 168)
        c_dark = (25, 20, 28)

        base_z = max(0.0, self.wz)

        # 1. Coluna vertebral (Spine)
        draw_voxel_box(surface, camera, self.wx - 0.03, self.wy - 0.03, base_z + 0.25, 0.06, 0.06, 0.32, c_bone_shadow, outline=True)

        # 2. Pélvis (Pelvis)
        draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.05, base_z + 0.22, 0.16, 0.10, 0.06, c_bone, outline=True)

        # 3. Caixa torácica (Ribcage - 3 arcos de costelas)
        draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.08, base_z + 0.34, 0.24, 0.16, 0.04, c_bone, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.14, self.wy - 0.09, base_z + 0.42, 0.28, 0.18, 0.05, c_bone, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.11, self.wy - 0.08, base_z + 0.50, 0.22, 0.16, 0.04, c_bone, outline=True)

        # 4. Crânio (Skull) com órbitas oculares vazadas
        draw_voxel_box(surface, camera, self.wx - 0.09, self.wy - 0.09, base_z + 0.60, 0.18, 0.18, 0.18, c_bone, outline=True)
        # Órbitas oculares escuras na direção do olhar
        eye_off_x = self.facing_x * 0.09
        eye_off_y = self.facing_y * 0.09
        draw_voxel_box(surface, camera, self.wx + eye_off_x - 0.04, self.wy + eye_off_y - 0.04, base_z + 0.65, 0.08, 0.08, 0.06, c_dark, outline=False)

        # Brilho espectral esmeralda nas órbitas
        draw_voxel_box(surface, camera, self.wx + eye_off_x - 0.02, self.wy + eye_off_y - 0.02, base_z + 0.66, 0.04, 0.04, 0.04, (65, 230, 170), outline=False)

        # 5. Membros articulados em corrida (Braços e Pernas delgados)
        leg_phase = math.sin(self.anim_time * 14.0) * 0.16
        arm_phase = math.cos(self.anim_time * 14.0) * 0.18

        # Braços estendidos para frente agarrando
        draw_oriented_voxel_box(
            surface, camera,
            self.wx + self.facing_x * 0.15 - self.facing_y * 0.14,
            self.wy + self.facing_y * 0.15 + self.facing_x * 0.14,
            base_z + 0.45 + arm_phase,
            self.facing_x, self.facing_y, -0.2,
            0.28, 0.04, 0.04, c_bone, outline=True
        )
        draw_oriented_voxel_box(
            surface, camera,
            self.wx + self.facing_x * 0.15 + self.facing_y * 0.14,
            self.wy + self.facing_y * 0.15 - self.facing_x * 0.14,
            base_z + 0.45 - arm_phase,
            self.facing_x, self.facing_y, -0.2,
            0.28, 0.04, 0.04, c_bone, outline=True
        )

        # Pernas delgadas de osso
        draw_voxel_box(surface, camera, self.wx - 0.08 - self.facing_x * leg_phase, self.wy - 0.04, base_z, 0.05, 0.05, 0.22, c_bone_shadow, outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.03 + self.facing_x * leg_phase, self.wy - 0.04, base_z, 0.05, 0.05, 0.22, c_bone_shadow, outline=True)


class ValeriusNecromancer(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Valerius")
        self.char_type = "valerius"
        self.speed = 3.80  # Velocidade ponderada de necromante com foice pesada
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Ataque Primário: Foice Fúnebre (Soul Reap)
        self.scythe_duration = 0.25  # Windup deliberado de foice pesada permitindo reação justa
        self.scythe_recovery = 0.54  # Recovery calibrado para punição justa
        self.scythe_reach = 1.95     # Alcance calibrado para permitir contestação melee
        self.scythe_radius = 1.35
        self.scythe_timer = 0.0

        # Ação Secundária: Evocar Mortos (Summon Skeleton)
        self.summon_cooldown = 6.2
        self.summon_timer = 0.0
        self.summon: SkeletonSummon | None = None

        # Esquiva: Névoa Espectral
        self.is_agile_dodge = False
        self.roll_speed = 8.6
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.18
        self.roll_cooldown_duration = 0.40
        self.recovery_duration = self.scythe_recovery

    def trigger_parry(self) -> bool:
        """Apara golpes utilizando o robusto cabo de freixo e a curvatura da lâmina da foice."""
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

    def trigger_scythe_reap(self, aim_x: float, aim_y: float) -> bool:
        """Ataque Primário: Amplo corte ceifador com a foice fúnebre."""
        if not self.can_act():
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.scythe_duration
        self.hitbox_active = True
        self.hitbox_damage = 2

        # Centro da hitbox à frente (calibrado para 1.05m mantendo raio 1.35)
        self.hitbox_center = (
            self.wx + self.facing_x * 1.05,
            self.wy + self.facing_y * 1.05
        )
        self.hitbox_radius = self.scythe_radius
        self.slash_dir = (self.facing_x, self.facing_y)
        return True

    def trigger_summon_undead(self, aim_x: float = None, aim_y: float = None, particles: list = None, opponent=None, banners: list = None) -> bool:
        """Ação Secundária: Invoca do solo um esqueleto guerreiro perseguidor."""
        if not self.can_act() or self.summon_timer > 0:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        # Destrói invocação anterior se houver
        if self.summon and self.summon.is_alive:
            self.summon.take_hit(damage=1, particles=particles)

        # Posição de surgimento à frente de Valerius
        spawn_x = self.wx + self.facing_x * 1.35
        spawn_y = self.wy + self.facing_y * 1.35

        self.summon = SkeletonSummon(self, spawn_x, spawn_y, opponent=opponent)
        self.summon_timer = self.summon_cooldown

        self.state = STATE_RECOVERY
        self.state_timer = 0.16

        if banners is not None:
            banners.append(FloatingBanner("NECROMANCY!", self.wx, self.wy, wz=1.8, color=(140, 70, 180)))

        if particles is not None:
            # Erupção espectral de névoa escura e chamas etéreas
            for _ in range(16):
                particles.append(SmokeParticle(
                    spawn_x + random.uniform(-0.25, 0.25),
                    spawn_y + random.uniform(-0.25, 0.25),
                    wz=0.08,
                    color=random.choice([(40, 25, 50), (65, 230, 170)]),
                    radius=0.22,
                    lifetime=0.55
                ))
        return True

    def trigger_mist_dash(self, dwx: float, dwy: float, particles: list = None):
        """Esquiva especial: Deslizamento etéreo de névoa espectral com i-frames."""
        if not self.can_act() or self.roll_cooldown_timer > 0:
            return

        super().trigger_roll(dwx, dwy, particles)
        if particles is not None:
            for _ in range(12):
                particles.append(SmokeParticle(
                    self.wx + random.uniform(-0.2, 0.2),
                    self.wy + random.uniform(-0.2, 0.2),
                    wz=0.3,
                    color=(55, 30, 70),
                    radius=0.20,
                    lifetime=0.45
                ))

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None):
        """Atualiza a máquina de estados, timers de recarga e o lacaio esquelético."""
        self.update_dodge_timers(dt)

        if self.summon_timer > 0:
            self.summon_timer = max(0.0, self.summon_timer - dt)

        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            if self.summon and self.summon.is_alive:
                self.summon.take_hit(damage=1, particles=particles)
            return

        if self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            step_speed = 2.0
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map and hasattr(game_map, "cols"):
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.20,
                self.wy + self.facing_y * 1.20
            )
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.scythe_recovery
                self.hitbox_active = False
            return

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # Atualiza o lacaio invocado
        if self.summon and self.summon.is_alive:
            still_active = self.summon.update(dt, game_map, opponent, particles=particles, banners=banners)
            if not still_active:
                self.summon = None

    def render(self, surface: pygame.Surface, camera):
        extra = {}
        if self.state in ("DEFEND", "PARRY") or getattr(self, "is_parrying", False):
            extra = {"pose": "scythe_guard"}

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
            char_type="valerius",
            walk_timer=getattr(self, "walk_cycle", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
