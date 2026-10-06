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
    """
    Névoa tóxica de Dokukiri soprada por Okuni com seus leques de ferro.
    Projetada em cone frontal à frente de Okuni com área reduzida.
    Empurra o oponente para trás com a rajada de vento dos leques.
    O oponente envenenado ganha adrenalina: fica mais rápido e com cooldowns 20% menores.
    """
    def __init__(self, wx: float, wy: float, dir_x_or_owner = 1.0, dir_y: float = 0.0, owner = None):
        if owner is None and not isinstance(dir_x_or_owner, (int, float)):
            self.owner = dir_x_or_owner
            self.dir_x = getattr(self.owner, "facing_x", 1.0)
            self.dir_y = getattr(self.owner, "facing_y", 0.0)
        else:
            self.dir_x = float(dir_x_or_owner)
            self.dir_y = float(dir_y)
            self.owner = owner

        norm = math.hypot(self.dir_x, self.dir_y)
        if norm > 0.001:
            self.dir_x /= norm
            self.dir_y /= norm
        else:
            self.dir_x, self.dir_y = 1.0, 0.0

        self.origin_x = wx
        self.origin_y = wy
        self.wx = wx + self.dir_x * 0.85
        self.wy = wy + self.dir_y * 0.85
        self.wz = 0.2
        self.cone_length = 1.85   # Alcance frontal concentrado em cone (área menor)
        self.cone_half_angle = math.radians(40)  # Abertura de 80° à frente
        self.cos_cone_half_angle = math.cos(self.cone_half_angle)
        self.radius = 0.95        # Raio efetivo reduzido (era 1.35)
        self.lifetime = 1.9       # Rajada concentrada de 1.9s
        self.max_lifetime = 1.9
        self.age = 0.0
        self.is_active = True
        self.has_pushed: set[int] = set()

        base_ang = math.atan2(self.dir_y, self.dir_x)
        # Plumas de névoa projetadas estritamente dentro do cone frontal
        self.plumes = [
            (
                base_ang + random.uniform(-self.cone_half_angle * 0.95, self.cone_half_angle * 0.95),
                random.uniform(0.35, 1.0),
                random.uniform(0.04, 0.28),
                random.uniform(0.70, 1.15),
                random.uniform(0.9, 1.35),
                i % 3
            )
            for i in range(12)
        ]
        # Vórtices de vapor orientados ao longo do cone
        self.wisps = [
            (random.uniform(0.20, 0.95), random.uniform(-0.35, 0.35), random.uniform(0.03, 0.16), random.uniform(0.65, 1.1))
            for _ in range(6)
        ]

    def update(self, dt: float, fighters: list = None, particles: list = None, banners: list = None, cinematic_director = None) -> bool:
        self.age += dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.is_active = False
            return False

        if particles is not None and random.random() < 0.40:
            cone_dist = random.uniform(0.4, self.cone_length)
            cone_ang = math.atan2(self.dir_y, self.dir_x) + random.uniform(-self.cone_half_angle, self.cone_half_angle)
            px = self.origin_x + math.cos(cone_ang) * cone_dist
            py = self.origin_y + math.sin(cone_ang) * cone_dist
            particles.append(SparkParticle(px, py, random.uniform(0.15, 0.40), color=random.choice([(140, 50, 180), (70, 210, 120), (185, 75, 225)])))

        if fighters:
            for f in fighters:
                if f is not self.owner and getattr(f, "is_alive", False):
                    dx = f.wx - self.origin_x
                    dy = f.wy - self.origin_y
                    dist = math.hypot(dx, dy)
                    in_cone = False
                    if dist <= (self.cone_length + f.radius):
                        if dist < 0.40:
                            in_cone = True
                        else:
                            dot = (dx * self.dir_x + dy * self.dir_y) / dist
                            if dot >= self.cos_cone_half_angle:
                                in_cone = True

                    if in_cone:
                        # 1. Empurrão (Push Back): repele o oponente para trás na direção do sopro
                        fid = id(f)
                        if fid not in self.has_pushed:
                            self.has_pushed.add(fid)
                            push_dist = 1.35
                            f.wx += self.dir_x * push_dist
                            f.wy += self.dir_y * push_dist
                            f.wx = max(1.0, min(24.0, f.wx))
                            f.wy = max(1.0, min(24.0, f.wy))
                            f.slow_timer = 0.0 # Sem lentidão!

                        # 2. Infectar com veneno (sem slow, concedendo adrenalina de velocidade e cooldowns 20% menores)
                        if not getattr(f, "is_poisoned", False):
                            f.is_poisoned = True
                            f.poison_timer = 6.0
                            f.slow_timer = 0.0
                            # Redução imediata de 20% nos cooldowns já ativos
                            for cd_attr in (
                                "ryuu_timer", "dash_recovery_timer", "jump_timer", "jump_cooldown_timer",
                                "chain_timer", "mine_timer", "bomb_timer", "smoke_timer", "rope_timer",
                                "arrow_cooldown_timer", "ofuda_cooldown_timer", "cannon_cooldown_timer",
                                "flintlock_timer", "cape_timer", "trap_timer", "zeroshiki_timer",
                                "shuriken_timer", "thrust_timer", "kama_timer", "backstep_timer"
                            ):
                                val = getattr(f, cd_attr, 0.0)
                                if val > 0:
                                    setattr(f, cd_attr, val * 0.80)
                            if hasattr(f, "dog") and f.dog and getattr(f.dog, "cooldown_timer", 0.0) > 0:
                                f.dog.cooldown_timer *= 0.80

                            if banners is not None:
                                banners.append(FloatingBanner("POISON FRENZY! (+25% SPD & -20% CD)", f.wx, f.wy, wz=1.8, color=(80, 240, 130), duration=2.4))
                        else:
                            # Respirar dentro do cone acelera o relógio do veneno
                            f.poison_timer -= dt * 1.2

                        if particles is not None and random.random() < 0.35:
                            particles.append(SparkParticle(f.wx, f.wy, 0.45, color=(80, 225, 120)))

                        if f.poison_timer <= 0:
                            f.is_poisoned = False
                            hit, dead = f.take_hit((0, 0), damage=2)
                            if dead:
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
        fade_in = min(1.0, self.age / 0.25)
        fade_out = max(0.0, min(1.0, self.lifetime / 0.50))
        base_alpha = fade_in * fade_out
        if base_alpha <= 0.01:
            return

        # 1. Manto de Bruma no Solo ao longo do cone projetado
        cone_mid_x = self.origin_x + self.dir_x * (self.cone_length * 0.55)
        cone_mid_y = self.origin_y + self.dir_y * (self.cone_length * 0.55)
        gx, gy = camera.apply(cone_mid_x, cone_mid_y, 0.02)
        ground_w = int(self.cone_length * 42 * (0.85 + 0.25 * progress))
        ground_h = max(3, int(ground_w * 0.52))
        ground_surf = pygame.Surface((ground_w * 2, ground_h * 2), pygame.SRCALPHA)
        g_alpha = int(45 * base_alpha)
        pygame.draw.ellipse(ground_surf, (75, 20, 105, g_alpha), (0, 0, ground_w * 2, ground_h * 2))
        pygame.draw.ellipse(ground_surf, (45, 135, 75, int(g_alpha * 0.60)), (ground_w // 4, ground_h // 4, int(ground_w * 1.5), int(ground_h * 1.5)))
        surface.blit(ground_surf, (gx - ground_w, gy - ground_h))

        # 2. Plumas de Névoa fanning out dentro do cone
        base_ang = math.atan2(self.dir_y, self.dir_x)
        for angle, dist_ratio, z_off, sz_mult, drift_spd, col_type in self.plumes:
            curr_dist = dist_ratio * self.cone_length * (0.65 + 0.35 * progress)
            spread_ang = base_ang + (angle - base_ang) * (0.80 + 0.25 * progress)
            p_wx = self.origin_x + math.cos(spread_ang) * curr_dist
            p_wy = self.origin_y + math.sin(spread_ang) * curr_dist
            p_wz = self.wz + z_off + math.sin(self.age * 2.5 + angle) * 0.04

            px, py = camera.apply(p_wx, p_wy, p_wz)
            pw = int(sz_mult * 26 * (0.80 + 0.3 * progress))
            ph = max(3, int(pw * 0.55))

            plume_surf = pygame.Surface((pw * 2, ph * 2), pygame.SRCALPHA)
            if col_type == 0:
                c_outer = (120, 30, 160)
                c_inner = (160, 55, 205)
            elif col_type == 1:
                c_outer = (145, 50, 185)
                c_inner = (80, 205, 125)
            else:
                c_outer = (45, 135, 80)
                c_inner = (135, 50, 180)

            p_alpha = int(72 * base_alpha)
            pygame.draw.ellipse(plume_surf, (*c_outer, p_alpha), (0, 0, pw * 2, ph * 2))
            pygame.draw.ellipse(plume_surf, (*c_inner, int(p_alpha * 0.7)), (pw // 4, ph // 4, int(pw * 1.5), int(ph * 1.5)))
            pygame.draw.ellipse(plume_surf, (170, 245, 185, int(p_alpha * 0.35)), (pw // 2, ph // 2, pw, ph))
            surface.blit(plume_surf, (px - pw, py - ph))

        # 3. Micro-vapores Volumétricos em Voxel 3D
        from src.isometric.voxel_renderer import draw_voxel_box
        v_alpha = int(80 * base_alpha)
        perp_x = -self.dir_y
        perp_y = self.dir_x
        for forward_ratio, lateral_ratio, oz, v_sz in self.wisps:
            dist_f = forward_ratio * self.cone_length * (0.7 + 0.3 * progress)
            dist_l = lateral_ratio * (dist_f * 0.75)
            vx = self.origin_x + self.dir_x * dist_f + perp_x * dist_l
            vy = self.origin_y + self.dir_y * dist_f + perp_y * dist_l
            vz = oz + (self.age * 0.08) % 0.35
            sz = 0.12 * v_sz
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

        # Terceira Ação: Pirueta Teatral Kabuki (Especial / Ágil)
        self.is_agile_dodge = True
        self.roll_speed = 10.5
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.12
        self.roll_cooldown_duration = 0.35
        self.roll_dir_x = 1.0
        self.roll_dir_y = 0.0
        self.decoy_cooldown = 2.8
        self.decoy_cooldown_timer = 0.0

    def can_act(self) -> bool:
        if (
            not self.is_alive
            or self.state in (STATE_KABUKI_ROLL, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, "DOKUKIRI")
            or self.roll_recovery_timer > 0
            or self.dash_recovery_timer > 0
        ):
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
        """Ação Secundária: Dokukiri (Sopro Venenoso) — cone frontal projetado com leques que empurra o adversário."""
        if not self.can_act() or self.poison_cooldown_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.state = "DOKUKIRI"
        self.state_timer = 0.20
        self.poison_cooldown_timer = self.poison_cooldown

        if clouds is not None:
            clouds.append(PoisonCloud(self.wx, self.wy, self.facing_x, self.facing_y, owner=self))

        if particles is not None:
            for _ in range(16):
                particles.append(SparkParticle(self.wx + self.facing_x * 0.8, self.wy + self.facing_y * 0.8, 0.5))

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None, decoys: list = None):
        """Terceira Ação: Kawarimi Dash Teatral com manequim de seda, pétalas de sakura e i-frames."""
        if (
            not self.is_alive
            or self.state in (STATE_KABUKI_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK, "DOKUKIRI")
            or self.roll_recovery_timer > 0
            or self.roll_cooldown_timer > 0
            or self.dash_recovery_timer > 0
        ):
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
        self.update_dodge_timers(dt)

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
                self.roll_recovery_timer = self.roll_recovery_duration
                self.roll_cooldown_timer = self.roll_cooldown_duration
                self.dash_recovery_timer = self.roll_cooldown_duration

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
