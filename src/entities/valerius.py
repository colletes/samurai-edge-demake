"""
Valerius (O Necromante / Exorcista Prussiano - Ciclo 4):
Aristocrata prussiano e necromante misterioso em terras nipônicas durante a era Bakumatsu.
- Arquétipo: Lutador tático de alcance com foice fúnebre e controle de campo com a Tríade dos Mortos (velocidade 3.8, 2 HP).
- Guarda de Foice: Parry técnico com o cabo reforçado e a lâmina da foice.
- Ataque Primário: Cursed Scythe Reap (SOUL_REAP) - ceifada ampla em arco com rastro de chamas azuis (alcance 1.95m, raio 1.35m, dano 2).
  No golpe fatal, decapita o rival (a cabeça é arremessada preservando feições normais) enquanto o corpo transforma-se em um esqueleto de voxels 3D em chamas azuis.
- Ação Secundária: Tríade dos Mortos (SKELETON_SUMMON) & Detonação Cadavérica (CORPSE_DETONATION)
  Ciclo ritual de 3 servos invocados:
    1. Rastejante de Tornozelos (Crawling Grasper): rasteja rente ao chão, persegue a 3.4 m/s, agarra com 1.4s de imobilização/lentidão pesada (0 dano direto).
    2. Soldado com Espada (Bone Swordsman): caminha ereto com Pickelhaube prussiano e sabre de infantaria, corte rápido (dano 1).
    3. Wight de Chamas Azuis (Pyre Wight): corre a 4.4 m/s em chamas azuis espectrais, explode em área de 1.6m (dano 1) ao aproximar-se (<1.1m) ou ao ser atingido.
  Detonação de Cadáver: Pressionar [R] com um servo vivo estala os dedos e detona o lacaio prematuramente em chamas azuis onde estiver.
- Esquiva: Névoa Espectral (MIST_DASH) - 13 i-frames (0.22s de invulnerabilidade) com fumaça violeta e fagulhas azuis.
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


class ValeriusUndeadSummon:
    """
    Servo morto-vivo invocado das profundezas fúnebres por Valerius.
    Suporta 3 variantes rituais:
      - 'grasper': Rastejante baixo, persegue e agarra tornozelos com imobilização pesada de 1.4s.
      - 'swordsman': Soldado com Pickelhaube prussiano e sabre enferrujado (1 dano).
      - 'wight': Wight de chamas azuis veloz que detona ao aproximar-se ou ao ser atingido (1 dano em área 1.6m).
    """
    def __init__(self, owner, wx: float, wy: float, kind: str = "grasper", opponent=None):
        self.owner = owner
        self.opponent = opponent
        self.kind = kind if kind in ("grasper", "swordsman", "wight") else "grasper"
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.facing_x = 1.0
        self.facing_y = 0.0

        self.hp = 1
        self.is_alive = True
        self.state = "EMERGING"  # "EMERGING", "CHASING", "DEAD"
        self.emerge_timer = 0.35
        self.radius = 0.38
        self.anim_time = 0.0

        # Calibragem de velocidade por arquétipo
        if self.kind == "grasper":
            self.speed = 3.4
        elif self.kind == "swordsman":
            self.speed = 3.6
        else:  # wight
            self.speed = 4.4

    def take_hit(self, slash_dir: tuple[float, float] = (0.0, 0.0), damage: int = 1, particles: list = None) -> bool:
        """Destrói instantaneamente o servo. Se for Pyre Wight, detona em chamas azuis."""
        if not self.is_alive:
            return False

        if self.kind == "wight":
            return self.explode(particles=particles, opponent=self.opponent)

        self.is_alive = False
        self.state = "DEAD"
        if particles is not None:
            # Fragmentos de ossos brancos e faíscas espectrais azuis
            for _ in range(16):
                particles.append(SparkParticle(
                    self.wx + random.uniform(-0.15, 0.15),
                    self.wy + random.uniform(-0.15, 0.15),
                    random.uniform(0.1, 0.6),
                    color=random.choice([(235, 230, 215), (200, 195, 185), (60, 160, 255)])
                ))
        return True

    def explode(self, particles: list = None, opponent=None, banners: list = None) -> bool:
        """Detonação em chamas azuis espectrais (usada por Pyre Wight ou Detonação Cadavérica de Valerius)."""
        if not self.is_alive:
            return False

        self.is_alive = False
        self.state = "DEAD"

        target = opponent or self.opponent
        if target is not None and getattr(target, "is_alive", True):
            dx = target.wx - self.wx
            dy = target.wy - self.wy
            dist = math.hypot(dx, dy)
            if dist <= 1.60:
                push_dir = (dx / max(0.001, dist), dy / max(0.001, dist))
                target.take_hit(push_dir, damage=1)
                if getattr(target, "is_alive", True):
                    target.stun(0.35)

        if banners is not None:
            banners.append(FloatingBanner("PYRE BLAST!", self.wx, self.wy, wz=1.6, color=(60, 160, 255)))

        if particles is not None:
            # Erupção espectral de chamas azuis e fumaça violeta
            for _ in range(22):
                particles.append(SparkParticle(
                    self.wx + random.uniform(-0.35, 0.35),
                    self.wy + random.uniform(-0.35, 0.35),
                    0.20 + random.uniform(0.0, 0.70),
                    color=random.choice([(60, 160, 255), (100, 200, 255), (180, 235, 255), (140, 70, 220)])
                ))
            for _ in range(12):
                particles.append(SmokeParticle(
                    self.wx + random.uniform(-0.25, 0.25),
                    self.wy + random.uniform(-0.25, 0.25),
                    wz=0.15,
                    color=(35, 20, 50),
                    radius=0.28,
                    lifetime=0.55
                ))

        try:
            from src.audio.sound_manager import get_sound_manager
            from src.audio.sound_events import SoundEvent
            get_sound_manager().play(SoundEvent.BONE_CRUSH, volume_scale=0.9)
        except Exception:
            pass

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
            self.wz = -0.40 * (self.emerge_timer / 0.35)
            if particles is not None and random.random() < 0.40:
                particles.append(SmokeParticle(
                    self.wx + random.uniform(-0.15, 0.15),
                    self.wy + random.uniform(-0.15, 0.15),
                    wz=0.06,
                    color=(40, 25, 55),
                    radius=0.18,
                    lifetime=0.45
                ))
                particles.append(SparkParticle(
                    self.wx + random.uniform(-0.12, 0.12),
                    self.wy + random.uniform(-0.12, 0.12),
                    0.05,
                    color=(60, 160, 255)
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

            # Deslocamento em direção ao oponente
            step = self.speed * dt
            if dist > step:
                self.wx += self.facing_x * step
                self.wy += self.facing_y * step
            else:
                self.wx = self.opponent.wx
                self.wy = self.opponent.wy

            # 1. Variante Rastejante de Tornozelos (Grasper)
            if self.kind == "grasper":
                if dist <= 0.85 and getattr(self.opponent, "is_alive", True):
                    opp_facing = (self.opponent.facing_x * (-self.facing_x) + self.opponent.facing_y * (-self.facing_y)) > 0.0
                    if getattr(self.opponent, "state", "") == STATE_PARRY and opp_facing:
                        self.take_hit(damage=1, particles=particles)
                        if banners is not None:
                            banners.append(FloatingBanner("PARRY SUMMON!", self.wx, self.wy, wz=1.4, color=(100, 200, 255)))
                        return False

                    # Imobilização pesada de 1.4s (sem dano direto)
                    self.opponent.take_hit((self.facing_x, self.facing_y), damage=0)
                    if getattr(self.opponent, "is_alive", True):
                        self.opponent.stun(1.4)
                    if banners is not None:
                        banners.append(FloatingBanner("ANKLE GRAB!", self.opponent.wx, self.opponent.wy, wz=1.6, color=(140, 70, 220)))
                    self.take_hit(damage=1, particles=particles)
                    return False

            # 2. Variante Soldado com Espada (Swordsman)
            elif self.kind == "swordsman":
                if dist <= 1.25 and getattr(self.opponent, "is_alive", True):
                    opp_facing = (self.opponent.facing_x * (-self.facing_x) + self.opponent.facing_y * (-self.facing_y)) > 0.0
                    if getattr(self.opponent, "state", "") == STATE_PARRY and opp_facing:
                        self.take_hit(damage=1, particles=particles)
                        if banners is not None:
                            banners.append(FloatingBanner("PARRY SUMMON!", self.wx, self.wy, wz=1.4, color=(100, 200, 255)))
                        return False

                    # Golpe cortante de sabre (1 de dano)
                    self.opponent.take_hit((self.facing_x, self.facing_y), damage=1)
                    if getattr(self.opponent, "is_alive", True):
                        self.opponent.stun(0.25)
                    if banners is not None:
                        banners.append(FloatingBanner("SABER SLASH!", self.opponent.wx, self.opponent.wy, wz=1.6, color=(100, 180, 255)))
                    self.take_hit(damage=1, particles=particles)
                    return False

            # 3. Variante Wight de Chamas Azuis (Wight)
            elif self.kind == "wight":
                # Partículas constantes de chama azul durante a corrida
                if particles is not None and random.random() < 0.45:
                    particles.append(SparkParticle(
                        self.wx + random.uniform(-0.12, 0.12),
                        self.wy + random.uniform(-0.12, 0.12),
                        0.35 + random.uniform(0.0, 0.35),
                        color=random.choice([(60, 160, 255), (120, 200, 255)])
                    ))

                if dist <= 1.05 and getattr(self.opponent, "is_alive", True):
                    self.explode(particles=particles, opponent=self.opponent, banners=banners)
                    return False

        return self.is_alive

    def render(self, surface: pygame.Surface, camera):
        """Renderização 3D low-poly de anatomia esquelética facetada com Painter's Algorithm."""
        if not self.is_alive:
            return

        from src.isometric.mesh_primitives import draw_voxel_box, draw_oriented_voxel_box

        c_bone = (235, 230, 215)
        c_bone_shadow = (185, 180, 168)
        c_dark = (25, 20, 28)
        c_spectral_blue = (60, 160, 255)
        base_z = max(0.0, self.wz)

        # -------------------------------------------------------------
        # 1. Rastejante de Tornozelos (Grasper) - Anatomia rente ao solo
        # -------------------------------------------------------------
        if self.kind == "grasper":
            crawl_phase = math.sin(self.anim_time * 12.0)
            crawl_arm_l = math.sin(self.anim_time * 12.0) * 0.15
            crawl_arm_r = math.cos(self.anim_time * 12.0) * 0.15

            # Coluna e caixa torácica inclinadas para a frente
            draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05, base_z + 0.04, 0.10, 0.10, 0.10, c_bone_shadow, outline=True)
            draw_voxel_box(surface, camera, self.wx - 0.07, self.wy - 0.07, base_z + 0.10, 0.14, 0.14, 0.08, c_bone, outline=True)

            # Crânio baixo farejando o solo com olhos azuis
            crank_x = self.wx + self.facing_x * 0.12
            crank_y = self.wy + self.facing_y * 0.12
            draw_voxel_box(surface, camera, crank_x - 0.06, crank_y - 0.06, base_z + 0.14, 0.12, 0.12, 0.12, c_bone, outline=True)
            # Órbitas oculares
            eye_off_x = self.facing_x * 0.06
            eye_off_y = self.facing_y * 0.06
            draw_voxel_box(surface, camera, crank_x + eye_off_x - 0.02, crank_y + eye_off_y - 0.02, base_z + 0.18, 0.04, 0.04, 0.04, c_spectral_blue, outline=False)

            # Braços rastejantes arrastando o chão alternados
            side_x = -self.facing_y * 0.12
            side_y = self.facing_x * 0.12
            draw_oriented_voxel_box(
                surface, camera,
                self.wx + side_x + self.facing_x * crawl_arm_l,
                self.wy + side_y + self.facing_y * crawl_arm_l,
                base_z + 0.04,
                self.facing_x, self.facing_y, -0.3,
                0.24, 0.04, 0.04, c_bone, outline=True
            )
            draw_oriented_voxel_box(
                surface, camera,
                self.wx - side_x + self.facing_x * crawl_arm_r,
                self.wy - side_y + self.facing_y * crawl_arm_r,
                base_z + 0.04,
                self.facing_x, self.facing_y, -0.3,
                0.24, 0.04, 0.04, c_bone, outline=True
            )
            return

        # -------------------------------------------------------------
        # 2. Soldado com Espada (Swordsman) e 3. Wight de Chamas Azuis
        # -------------------------------------------------------------
        # Coluna vertebral e pélvis
        draw_voxel_box(surface, camera, self.wx - 0.03, self.wy - 0.03, base_z + 0.25, 0.06, 0.06, 0.32, c_bone_shadow, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.05, base_z + 0.22, 0.16, 0.10, 0.06, c_bone, outline=True)

        # Caixa torácica (Ribcage)
        draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.08, base_z + 0.34, 0.24, 0.16, 0.04, c_bone, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.14, self.wy - 0.09, base_z + 0.42, 0.28, 0.18, 0.05, c_bone, outline=True)
        draw_voxel_box(surface, camera, self.wx - 0.11, self.wy - 0.08, base_z + 0.50, 0.22, 0.16, 0.04, c_bone, outline=True)

        # Crânio
        draw_voxel_box(surface, camera, self.wx - 0.09, self.wy - 0.09, base_z + 0.60, 0.18, 0.18, 0.18, c_bone, outline=True)
        eye_off_x = self.facing_x * 0.09
        eye_off_y = self.facing_y * 0.09
        draw_voxel_box(surface, camera, self.wx + eye_off_x - 0.04, self.wy + eye_off_y - 0.04, base_z + 0.65, 0.08, 0.08, 0.06, c_dark, outline=False)
        draw_voxel_box(surface, camera, self.wx + eye_off_x - 0.02, self.wy + eye_off_y - 0.02, base_z + 0.66, 0.04, 0.04, 0.04, c_spectral_blue, outline=False)

        # Pernas em marcha
        leg_phase = math.sin(self.anim_time * 14.0) * 0.16
        draw_voxel_box(surface, camera, self.wx - 0.08 - self.facing_x * leg_phase, self.wy - 0.04, base_z, 0.05, 0.05, 0.22, c_bone_shadow, outline=True)
        draw_voxel_box(surface, camera, self.wx + 0.03 + self.facing_x * leg_phase, self.wy - 0.04, base_z, 0.05, 0.05, 0.22, c_bone_shadow, outline=True)

        if self.kind == "swordsman":
            # Elmo Pickelhaube prussiano voxel
            c_pickel_steel = (35, 38, 42)
            c_pickel_brass = (205, 170, 60)
            # Casco do elmo
            draw_voxel_box(surface, camera, self.wx - 0.10, self.wy - 0.10, base_z + 0.72, 0.20, 0.20, 0.08, c_pickel_steel, outline=True)
            # Ponta pontiaguda de latão
            draw_voxel_box(surface, camera, self.wx - 0.025, self.wy - 0.025, base_z + 0.80, 0.05, 0.05, 0.10, c_pickel_brass, outline=True)

            # Braço esquerdo de guarda
            draw_voxel_box(surface, camera, self.wx - 0.15, self.wy - 0.03, base_z + 0.38, 0.05, 0.05, 0.20, c_bone_shadow, outline=True)

            # Braço direito empunhando o sabre prussiano
            hand_rx = self.wx + self.facing_x * 0.20 + (-self.facing_y) * 0.14
            hand_ry = self.wy + self.facing_y * 0.20 + (self.facing_x) * 0.14
            draw_voxel_box(surface, camera, hand_rx - 0.03, hand_ry - 0.03, base_z + 0.45, 0.06, 0.06, 0.06, c_bone, outline=True)

            # Sabre de infantaria (guarda de latão e lâmina de aço enferrujado)
            draw_voxel_box(surface, camera, hand_rx - 0.04, hand_ry - 0.04, base_z + 0.44, 0.08, 0.08, 0.03, c_pickel_brass, outline=True)
            draw_oriented_voxel_box(
                surface, camera,
                hand_rx + self.facing_x * 0.06, hand_ry + self.facing_y * 0.06, base_z + 0.45,
                self.facing_x, self.facing_y, -0.15,
                0.48, 0.03, 0.05, (185, 190, 200), outline=True
            )

        elif self.kind == "wight":
            # Labaredas azuis pulsantes no crânio e na caixa torácica
            flame_flicker = math.sin(self.anim_time * 18.0) * 0.02
            c_flame_core = (175, 220, 255)
            # Labareda do crânio
            draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05, base_z + 0.77 + flame_flicker, 0.10, 0.10, 0.12, c_spectral_blue, outline=False)
            draw_voxel_box(surface, camera, self.wx - 0.025, self.wy - 0.025, base_z + 0.79, 0.05, 0.05, 0.08, c_flame_core, outline=False)

            # Chamas saindo pelas costelas
            draw_voxel_box(surface, camera, self.wx - 0.10, self.wy - 0.06, base_z + 0.42, 0.06, 0.06, 0.06, c_spectral_blue, outline=False)
            draw_voxel_box(surface, camera, self.wx + 0.04, self.wy - 0.06, base_z + 0.42, 0.06, 0.06, 0.06, c_spectral_blue, outline=False)

            # Braços em corrida agressiva
            arm_phase = math.cos(self.anim_time * 14.0) * 0.18
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


# Alias para retrocompatibilidade
SkeletonSummon = ValeriusUndeadSummon


class ValeriusNecromancer(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Valerius")
        self.char_type = "valerius"
        self.speed = 3.80  # Velocidade ponderada de necromante com foice cerimonial
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Ataque Primário: Cursed Scythe Reap (SOUL_REAP)
        self.scythe_duration = 0.25  # Windup deliberado de foice pesada permitindo reação justa
        self.scythe_recovery = 0.48  # Recovery calibrado para punição justa
        self.scythe_reach = 1.95     # Alcance calibrado
        self.scythe_radius = 1.35
        self.scythe_timer = 0.0

        # Ação Secundária: Tríade dos Mortos & Detonação Cadavérica
        self.summon_cooldown = 5.5
        self.summon_timer = 0.0
        self.summon_cycle = 0  # 0: Grasper, 1: Swordsman, 2: Wight
        self.summon: ValeriusUndeadSummon | None = None

        # Esquiva: Névoa Espectral (Mist Dash)
        self.is_agile_dodge = False
        self.roll_speed = 8.6
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.18
        self.roll_cooldown_duration = 0.40
        self.recovery_duration = self.scythe_recovery

        # Fatalities
        self.finisher_style_primary = "SOUL_REAP"
        self.finisher_style_secondary = "DRAGGED_TO_GRAVE"

    def trigger_parry(self) -> bool:
        """Apara golpes utilizando o robusto cabo de freixo e a curvatura da foice."""
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
        """Ataque Primário: Amplo corte ceifador com a foice cerimonial."""
        if not self.can_act():
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.scythe_duration
        self.hitbox_active = True
        self.hitbox_damage = 2

        self.hitbox_center = (
            self.wx + self.facing_x * 1.05,
            self.wy + self.facing_y * 1.05
        )
        self.hitbox_radius = self.scythe_radius
        self.slash_dir = (self.facing_x, self.facing_y)
        return True

    def get_next_summon_name(self) -> str:
        """Retorna o nome amigável do próximo servo no ciclo ritual."""
        names = ["Evocar Rastejante", "Evocar Soldado", "Evocar Wight"]
        return names[self.summon_cycle % 3]

    def trigger_summon_undead(self, aim_x: float = None, aim_y: float = None, particles: list = None, opponent=None, banners: list = None) -> bool:
        """
        Ação Secundária:
        - Se já houver servo vivo, executa Detonação Cadavérica imediata.
        - Caso contrário, invoca o próximo servo da Tríade dos Mortos (Grasper -> Swordsman -> Wight).
        """
        if self.summon and self.summon.is_alive:
            return self.trigger_corpse_detonation(particles=particles, opponent=opponent, banners=banners)

        if not self.can_act() or self.summon_timer > 0:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        kinds = ["grasper", "swordsman", "wight"]
        current_kind = kinds[self.summon_cycle % 3]
        self.summon_cycle = (self.summon_cycle + 1) % 3

        spawn_x = self.wx + self.facing_x * 1.35
        spawn_y = self.wy + self.facing_y * 1.35

        self.summon = ValeriusUndeadSummon(self, spawn_x, spawn_y, kind=current_kind, opponent=opponent)
        self.summon_timer = self.summon_cooldown

        self.state = STATE_RECOVERY
        self.state_timer = 0.18

        if banners is not None:
            banner_titles = {
                "grasper": "SUMMON GRASPER!",
                "swordsman": "SUMMON SWORDSMAN!",
                "wight": "SUMMON WIGHT!"
            }
            banners.append(FloatingBanner(banner_titles.get(current_kind, "NECROMANCY!"), self.wx, self.wy, wz=1.8, color=(140, 70, 180)))

        if particles is not None:
            for _ in range(16):
                particles.append(SmokeParticle(
                    spawn_x + random.uniform(-0.25, 0.25),
                    spawn_y + random.uniform(-0.25, 0.25),
                    wz=0.08,
                    color=random.choice([(40, 25, 50), (60, 160, 255)]),
                    radius=0.22,
                    lifetime=0.55
                ))
        return True

    def trigger_corpse_detonation(self, particles: list = None, opponent=None, banners: list = None) -> bool:
        """Detonação de Cadáver: Estala os dedos e explode o servo ativo em chamas azuis de área."""
        if not self.summon or not self.summon.is_alive:
            return False

        self.summon.explode(particles=particles, opponent=opponent, banners=banners)
        self.summon = None
        self.summon_timer = self.summon_cooldown

        self.state = STATE_RECOVERY
        self.state_timer = 0.18

        if banners is not None:
            banners.append(FloatingBanner("CORPSE DETONATION!", self.wx, self.wy, wz=1.8, color=(60, 160, 255)))

        return True

    def trigger_mist_dash(self, dwx: float, dwy: float, particles: list = None, game_map=None) -> bool:
        """Esquiva especial: Deslizamento etéreo de névoa espectral com 13 i-frames."""
        if not self.can_act() or self.roll_cooldown_timer > 0:
            return False

        res = super().trigger_roll(dwx, dwy, particles)
        if not res:
            return False

        if particles is not None:
            for _ in range(14):
                particles.append(SmokeParticle(
                    self.wx + random.uniform(-0.2, 0.2),
                    self.wy + random.uniform(-0.2, 0.2),
                    wz=0.25,
                    color=(50, 25, 65),
                    radius=0.22,
                    lifetime=0.45
                ))
                particles.append(SparkParticle(
                    self.wx + random.uniform(-0.15, 0.15),
                    self.wy + random.uniform(-0.15, 0.15),
                    0.15,
                    color=(60, 160, 255)
                ))
        return True

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None, cinematic_director=None, **kwargs):
        """Atualiza a máquina de estados, timers de recarga e o servo morto-vivo."""
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
                self.wx + self.facing_x * 1.15,
                self.wy + self.facing_y * 1.15
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

        # Atualiza o servo invocado
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
