"""
Okuni (Mestra dos Leques de Aço & Finta Teatral Kawarimi):
Abandona o veneno em favor de combate corpo a corpo técnico e gracioso
com Leques de Ferro (Tessen-jutsu) e manequim teatral de seda (Kawarimi Decoy)
que aplica whiff punish / stun no adversário ao ser golpeado.
"""
import math
import random
import pygame
from src.config import (
    COLOR_KABUKI_WHITE, COLOR_KABUKI_RED, COLOR_KABUKI_HAIR, COLOR_KABUKI_AURA,
    COLOR_SAKURA_PINK, COLOR_WHITE, COLOR_GOLD, COLOR_STEEL
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle, FloatingBanner

STATE_KABUKI_ROLL = "KABUKI_ROLL"

class PoisonCloud:
    """Névoa tóxica de Dokukiri soprada por Okuni com seus leques (bruma rasteira e vapores esvoaçantes)."""
    def __init__(self, wx: float, wy: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = 0.2
        self.owner = owner
        self.lifetime = 2.8
        self.max_lifetime = 2.8
        self.age = 0.0
        self.radius = 1.35
        self.is_active = True
        self.exposure: dict[int, float] = {}

        # Plumas orgânicas de névoa em vórtice (angle, dist_ratio, z_off, sz_mult, drift_spd, col_type)
        self.plumes = [
            (
                i * (math.pi * 2 / 12) + random.uniform(-0.18, 0.18),
                random.uniform(0.25, 0.85),
                random.uniform(0.06, 0.35),
                random.uniform(0.75, 1.25),
                random.uniform(0.85, 1.35),
                i % 3
            )
            for i in range(13)
        ]
        # Vórtices de vapor rasteiro volumétrico em voxel
        self.wisps = [
            (random.uniform(-0.85, 0.85), random.uniform(-0.85, 0.85), random.uniform(0.03, 0.16), random.uniform(0.7, 1.2))
            for _ in range(7)
        ]

    def update(self, dt: float, fighters: list = None, particles: list = None, banners: list = None, cinematic_director = None) -> bool:
        self.age += dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.is_active = False
            return False

        if particles is not None and random.random() < 0.35:
            ox = self.wx + random.uniform(-self.radius, self.radius) * 0.75
            oy = self.wy + random.uniform(-self.radius, self.radius) * 0.75
            particles.append(SparkParticle(ox, oy, random.uniform(0.15, 0.45), color=random.choice([(140, 50, 180), (70, 210, 120), (185, 75, 225)])))

        if fighters:
            for f in fighters:
                if f is not self.owner and getattr(f, "is_alive", False):
                    d = math.hypot(f.wx - self.wx, f.wy - self.wy)
                    if d < (self.radius + f.radius):
                        if hasattr(f, "apply_slow"):
                            f.apply_slow(0.8)

                        # Infectar com veneno se ainda não estiver
                        if not getattr(f, "is_poisoned", False):
                            f.is_poisoned = True
                            f.poison_timer = 6.0
                            if banners is not None:
                                banners.append(FloatingBanner("POISONED! 6s TO SURVIVE!", f.wx, f.wy, wz=1.8, color=(80, 225, 120), duration=2.5))
                        else:
                            # Respiração contínua na névoa acelera o veneno
                            f.poison_timer -= dt * 1.5

                        if particles is not None and random.random() < 0.3:
                            particles.append(SparkParticle(f.wx, f.wy, 0.5, color=(80, 225, 120)))

                        if f.poison_timer <= 0:
                            f.is_poisoned = False
                            hit, dead = f.take_hit((0, 0), damage=99)
                            if dead:
                                if banners is not None:
                                    banners.append(FloatingBanner("POISON DEATH!", f.wx, f.wy, wz=1.8, color=(80, 225, 120)))
                                if particles is not None:
                                    from src.effects.particles import BloodParticle
                                    for _ in range(30):
                                        particles.append(BloodParticle(f.wx, f.wy, 0.6))
                                if cinematic_director:
                                    cinematic_director.trigger_fatal_strike(self.owner, f, "OKUNI_MELT", (0, 0))
        return self.is_active

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active or self.lifetime <= 0:
            return

        progress = min(1.0, max(0.0, self.age / self.max_lifetime))
        fade_in = min(1.0, self.age / 0.35)
        fade_out = max(0.0, min(1.0, self.lifetime / 0.70))
        base_alpha = fade_in * fade_out
        if base_alpha <= 0.01:
            return

        # 1. Manto de Névoa Rasteira no Solo (Creeping Ground Haze em elipse isométrica 2:1)
        gx, gy = camera.apply(self.wx, self.wy, 0.02)
        ground_w = int(self.radius * 55 * (0.85 + 0.3 * progress))
        ground_h = max(3, int(ground_w * 0.52))
        ground_surf = pygame.Surface((ground_w * 2, ground_h * 2), pygame.SRCALPHA)
        g_alpha = int(50 * base_alpha)
        pygame.draw.ellipse(ground_surf, (75, 20, 105, g_alpha), (0, 0, ground_w * 2, ground_h * 2))
        pygame.draw.ellipse(ground_surf, (45, 135, 75, int(g_alpha * 0.65)), (ground_w // 4, ground_h // 4, int(ground_w * 1.5), int(ground_h * 1.5)))
        surface.blit(ground_surf, (gx - ground_w, gy - ground_h))

        # 2. Plumas de Névoa Orgânicas Drifting (Brumas volumétricas esvoaçantes)
        for angle, dist_ratio, z_off, sz_mult, drift_spd, col_type in self.plumes:
            curr_dist = dist_ratio * self.radius * (0.75 + 0.35 * progress)
            curr_angle = angle + self.age * 0.35 * drift_spd
            p_wx = self.wx + math.cos(curr_angle) * curr_dist
            p_wy = self.wy + math.sin(curr_angle) * curr_dist
            p_wz = self.wz + z_off + math.sin(self.age * 2.0 + angle) * 0.05

            px, py = camera.apply(p_wx, p_wy, p_wz)
            pw = int(sz_mult * 30 * (0.85 + 0.3 * progress))
            ph = max(3, int(pw * 0.55))

            plume_surf = pygame.Surface((pw * 2, ph * 2), pygame.SRCALPHA)
            if col_type == 0:
                c_outer = (115, 30, 155)   # Púrpura velado
                c_inner = (155, 55, 200)
            elif col_type == 1:
                c_outer = (145, 50, 185)   # Lavanda mística
                c_inner = (90, 195, 120)   # Núcleo verde-veneno
            else:
                c_outer = (45, 125, 75)    # Vapor tóxico esmeralda
                c_inner = (130, 45, 175)   # Núcleo violeta

            p_alpha = int(70 * base_alpha)
            pygame.draw.ellipse(plume_surf, (*c_outer, p_alpha), (0, 0, pw * 2, ph * 2))
            pygame.draw.ellipse(plume_surf, (*c_inner, int(p_alpha * 0.7)), (pw // 4, ph // 4, int(pw * 1.5), int(ph * 1.5)))
            pygame.draw.ellipse(plume_surf, (170, 245, 185, int(p_alpha * 0.35)), (pw // 2, ph // 2, pw, ph))
            surface.blit(plume_surf, (px - pw, py - ph))

        # 3. Micro-vapores Volumétricos em Voxel 3D (Wisps de fumaça tóxica)
        from src.isometric.voxel_renderer import draw_voxel_box
        v_alpha = int(85 * base_alpha)
        for ox, oy, oz, v_sz in self.wisps:
            swirl = self.age * 0.45
            vx = self.wx + (ox * math.cos(swirl) - oy * math.sin(swirl)) * self.radius * 0.75
            vy = self.wy + (ox * math.sin(swirl) + oy * math.cos(swirl)) * self.radius * 0.75
            vz = oz + (self.age * 0.09) % 0.38
            sz = 0.13 * v_sz
            draw_voxel_box(surface, camera, vx - sz*0.5, vy - sz*0.5, vz, sz, sz, sz*0.65, (130, 60, 175), outline=False, alpha=v_alpha)

class OkuniDecoy:
    """Manequim teatral de seda deixado por Okuni durante a finta Kawarimi."""
    def __init__(self, wx: float, wy: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.owner = owner
        self.lifetime = 1.4   # Permanece ativa por 1.4s
        self.radius = 0.38
        self.is_active = True
        self.facing_x = getattr(owner, "facing_x", 1.0)
        self.facing_y = getattr(owner, "facing_y", 0.0)

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.is_active = False
        return self.is_active

    def on_hit(self, attacker, particles: list, banners: list, camera):
        """Absorve o golpe adversário, causa whiff stun e estoura em pétalas de cerejeira."""
        self.is_active = False
        camera.add_shake(7.0)
        banners.append(FloatingBanner("KAWARIMI WHIFF!", self.wx, self.wy, wz=1.7, color=COLOR_SAKURA_PINK))
        if attacker and attacker.is_alive:
            attacker.stun(0.45)  # Whiff punish fatal!
        if particles is not None:
            for _ in range(22):
                particles.append(SparkParticle(self.wx, self.wy, 0.45))

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        # Renderiza a ilusão em voxel com leve transparência teatral
        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            STATE_IDLE, 0.0, True,
            char_type="kabuki",
            alpha=210
        )
        sx, sy = camera.apply(self.wx, self.wy, 1.35)
        font = pygame.font.Font(None, 18)
        txt = font.render("KAWARIMI", True, COLOR_SAKURA_PINK)
        surface.blit(txt, (sx - txt.get_width() // 2, sy))


class Kabuki(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Okuni")
        self.char_type = "okuni"
        self.speed = 4.4

        # Ataque Melee: Dança dos Leques de Aço (Tessen-jutsu)
        self.attack_duration = 0.16
        self.recovery_duration = 0.12

        # Ação Secundária: Dokukiri (Névoa Venenosa)
        self.poison_cooldown = 3.2
        self.poison_cooldown_timer = 0.0

        # Terceira Ação: Pirueta Teatral Kabuki (Roll)
        self.roll_speed = 12.0
        self.roll_duration = 0.20
        self.roll_dir_x = 1.0
        self.roll_dir_y = 0.0
        self.decoy_cooldown = 2.8
        self.decoy_cooldown_timer = 0.0

    def can_act(self) -> bool:
        if not self.is_alive or self.state in (STATE_KABUKI_ROLL, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, "DOKUKIRI"):
            return False
        return True

    def trigger_fan_strike(self, target_wx: float, target_wy: float, particles: list = None):
        """Ataque Primário: Golpe veloz e duplo de leques de ferro afiados (Tessen)."""
        if not self.can_act():
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = self.attack_duration
        self.hitbox_active = True
        self.hitbox_radius = 1.25
        self.hitbox_center = (self.wx + self.facing_x * 0.75, self.wy + self.facing_y * 0.75)
        self.slash_dir = (self.facing_x, self.facing_y)

        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.35))

    def trigger_dokukiri(self, target_wx: float, target_wy: float, clouds: list = None, particles: list = None):
        """Ação Secundária: Dokukiri (Sopro Venenoso) — sopro de névoa arroxeada de veneno que causa lentidão e dano fatal."""
        if not self.can_act() or self.poison_cooldown_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.state = "DOKUKIRI"
        self.state_timer = 0.20
        self.poison_cooldown_timer = self.poison_cooldown

        cloud_x = self.wx + self.facing_x * 0.95
        cloud_y = self.wy + self.facing_y * 0.95

        if clouds is not None:
            clouds.append(PoisonCloud(cloud_x, cloud_y, owner=self))

        if particles is not None:
            for _ in range(16):
                particles.append(SparkParticle(cloud_x, cloud_y, 0.5))

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None, decoys: list = None):
        """Terceira Ação: Kawarimi Dash Teatral com manequim de seda, pétalas de sakura e i-frames."""
        if not self.is_alive or self.state in (STATE_KABUKI_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK):
            return

        if dir_x == 0 and dir_y == 0:
            dir_x, dir_y = -self.facing_x, -self.facing_y
        else:
            mag = math.hypot(dir_x, dir_y)
            if mag > 0.001:
                dir_x /= mag
                dir_y /= mag

        # Deixar o manequim teatral Kawarimi na posição de partida
        target_decoys = decoys if decoys is not None else getattr(self, "registered_decoys", None)
        if target_decoys is not None:
            decoy = OkuniDecoy(self.wx, self.wy, owner=self)
            target_decoys.append(decoy)

        self.state = STATE_KABUKI_ROLL
        self.state_timer = self.roll_duration
        self.roll_dir_x = dir_x
        self.roll_dir_y = dir_y
        self.facing_x = dir_x
        self.facing_y = dir_y
        self.is_invulnerable_dodge = True
        self.hitbox_active = False

        if particles is not None:
            from src.config import COLOR_SAKURA_PINK
            for _ in range(16):
                particles.append(SparkParticle(self.wx, self.wy, 0.45, color=COLOR_SAKURA_PINK))

    def trigger_kabuki_roll(self, dir_x: float, dir_y: float, particles: list = None, decoys: list = None):
        self.trigger_roll(dir_x, dir_y, particles=particles, decoys=decoys)

    def trigger_kawarimi_decoy(self, dir_x: float, dir_y: float, decoys: list, particles: list = None):
        """Compatibilidade: finta teatral com manequim e pirueta."""
        self.trigger_roll(dir_x, dir_y, particles=particles, decoys=decoys)

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.poison_cooldown_timer > 0:
            self.poison_cooldown_timer -= dt

        if self.decoy_cooldown_timer > 0:
            self.decoy_cooldown_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            # Passo leve à frente durante o golpe dos leques
            step = 3.2 * dt
            new_wx = self.wx + self.facing_x * step
            new_wy = self.wy + self.facing_y * step

            hit_col = False
            for r in game_map.rocks:
                if r.check_collision(new_wx, new_wy, self.radius)[0]:
                    hit_col = True; break
            if game_map.well and game_map.well.check_collision(new_wx, new_wy, self.radius)[0]:
                hit_col = True

            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            self.hitbox_center = (self.wx + self.facing_x * 0.75, self.wy + self.facing_y * 0.75)

            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
                self.hitbox_active = False

        elif self.state == STATE_KABUKI_ROLL:
            self.state_timer -= dt
            step = self.roll_speed * dt
            new_wx = self.wx + self.roll_dir_x * step
            new_wy = self.wy + self.roll_dir_y * step

            hit_col = False
            for r in game_map.rocks:
                if r.check_collision(new_wx, new_wy, self.radius)[0]:
                    hit_col = True; break
            if game_map.well and game_map.well.check_collision(new_wx, new_wy, self.radius)[0]:
                hit_col = True

            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            if particles is not None and random.random() < 0.4:
                particles.append(SparkParticle(self.wx, self.wy, 0.25))

            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.is_invulnerable_dodge = False

        elif self.state == "DOKUKIRI":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza Okuni com leques de aço e efeito de camuflagem."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (235, 150, 180), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="kabuki",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving
        )
