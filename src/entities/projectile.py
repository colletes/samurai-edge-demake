"""
Entidade KunaiProjectile: projétil arremessado pelo Ninja Amarelo.
Mortal à distância; se errar, crava no solo e pode ser recuperada.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_BLACK, COLOR_GOLD, COLOR_WHITE, COLOR_YELLOW_AURA
)
from src.isometric.iso_math import world_distance
from src.effects.particles import SparkParticle

class KunaiProjectile:
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner, vz: float = 0.0):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.owner = owner
        self.vz = vz

        # Velocidade de arremesso
        speed = 16.0
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.dir_x = dir_x
        self.dir_y = dir_y

        self.state = "FLYING"  # "FLYING" ou "ON_GROUND"
        self.max_range = 6.8
        self.dist_traveled = 0.0
        self.angle = math.atan2(dir_y, dir_x)
        self.is_active = True
        self.pickup_delay = 0.25 # Pequeno delay antes de poder pegar para evitar auto-pegar no mesmo frame

    def update(self, dt: float, game_map, particles: list) -> bool:
        """Atualiza a posição da kunai. Retorna False se deve ser removida."""
        if not self.is_active:
            return False

        if self.state == "FLYING":
            step = math.hypot(self.vx * dt, self.vy * dt)
            self.wx += self.vx * dt
            self.wy += self.vy * dt
            self.dist_traveled += step

            if self.vz != 0.0:
                self.wz += self.vz * dt
                if self.wz <= 0.05:
                    self.wz = 0.05
                    self.state = "ON_GROUND"
                    for _ in range(4):
                        particles.append(SparkParticle(self.wx, self.wy, 0.2))

            # Corte de bambus no caminho (atravessa sem ser parada)
            for b in game_map.bamboos:
                if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.45:
                    part = b.cut((self.dir_x, self.dir_y))
                    if part:
                        particles.append(part)

            # Colisão com rochas ou poço (ricocheteia e cai)
            hit_obstacle = False
            for r in game_map.rocks:
                if world_distance(self.wx, self.wy, r.wx, r.wy) < r.radius:
                    hit_obstacle = True
                    break
            if game_map.well and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
                hit_obstacle = True

            if hit_obstacle or self.dist_traveled >= self.max_range:
                # Crava no chão
                self.state = "ON_GROUND"
                self.wz = 0.05
                for _ in range(6):
                    particles.append(SparkParticle(self.wx, self.wy, 0.2))

        elif self.state == "ON_GROUND":
            if self.pickup_delay > 0:
                self.pickup_delay -= dt
            else:
                # Verificar se o dono (Ninja) passou por cima para recuperar a arma
                if self.owner and self.owner.is_alive and not self.owner.has_kunai:
                    if world_distance(self.wx, self.wy, self.owner.wx, self.owner.wy) < 0.65:
                        self.owner.has_kunai = True
                        self.is_active = False
                        # Efeito visual de coleta
                        for _ in range(8):
                            particles.append(SparkParticle(self.wx, self.wy, 0.4))
                        return False

        return True

    def render(self, surface: pygame.Surface, camera):
        """Renderiza a kunai no ar ou cravada no chão com indicador pulsante."""
        if not self.is_active:
            return

        from src.isometric.voxel_renderer import draw_voxel_box

        if self.state == "FLYING":
            # Lâmina voxel em voo orientada
            draw_voxel_box(surface, camera, self.wx - 0.06, self.wy - 0.06, self.wz, 0.12, 0.12, 0.12, COLOR_STEEL)
            draw_voxel_box(surface, camera, self.wx - self.dir_x * 0.12 - 0.04, self.wy - self.dir_y * 0.12 - 0.04, self.wz + 0.02, 0.08, 0.08, 0.08, COLOR_GOLD)
            # Rastro de energia
            sx, sy = camera.apply(self.wx, self.wy, self.wz)
            pygame.draw.circle(surface, COLOR_YELLOW_AURA, (sx, sy), 3)

        else:
            # Cravada no solo em ângulo
            base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

            # Indicador visual pulsante no piso (Item 2)
            ticks = pygame.time.get_ticks()
            pulse = 0.5 + 0.5 * math.sin(ticks * 0.007)
            glow_rad = int(12 + pulse * 6)
            glow_surf = pygame.Surface((glow_rad * 2, glow_rad * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255, 215, 50, int(45 + pulse * 45)), (0, glow_rad // 2, glow_rad * 2, glow_rad))
            surface.blit(glow_surf, (base_sx - glow_rad, base_sy - glow_rad // 2))

            # Sombra e haste cravada
            pygame.draw.ellipse(surface, (15, 20, 18), (base_sx - 6, base_sy - 3, 12, 6))
            draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05, 0.02, 0.10, 0.10, 0.16, COLOR_STEEL)
            draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - 0.04, 0.18, 0.08, 0.08, 0.08, COLOR_GOLD)

            # Marcador vertical flutuante (Bobbing marker)
            bob = math.sin(ticks * 0.009) * 4.0
            arrow_sx, arrow_sy = camera.apply(self.wx, self.wy, 0.65)
            tip_y = arrow_sy + bob
            pts = [(arrow_sx, tip_y), (arrow_sx - 5, tip_y - 8), (arrow_sx + 5, tip_y - 8)]
            pygame.draw.polygon(surface, (255, 225, 50), pts)
            pygame.draw.polygon(surface, (180, 140, 20), pts, 1)


class ShurikenProjectile:
    """Estrela ninja de 4 pontas rápida; não mata, mas atordoa o oponente temporariamente."""
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.owner = owner

        speed = 18.0
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.dir_x = dir_x
        self.dir_y = dir_y

        self.rot_angle = 0.0
        self.rot_speed = 900.0  # Rotação ultra rápida no ar
        self.max_range = 6.5
        self.dist_traveled = 0.0
        self.is_active = True

    def update(self, dt: float, game_map, particles: list) -> bool:
        if not self.is_active:
            return False

        step = math.hypot(self.vx * dt, self.vy * dt)
        self.wx += self.vx * dt
        self.wy += self.vy * dt
        self.dist_traveled += step
        self.rot_angle += self.rot_speed * dt

        # Corte de bambus
        for b in game_map.bamboos:
            if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.4:
                part = b.cut((self.dir_x, self.dir_y))
                if part:
                    particles.append(part)

        # Colisão com rochas ou poço
        hit_obstacle = False
        for r in game_map.rocks:
            if world_distance(self.wx, self.wy, r.wx, r.wy) < r.radius:
                hit_obstacle = True
                break
        if game_map.well and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
            hit_obstacle = True

        if hit_obstacle or self.dist_traveled >= self.max_range:
            for _ in range(4):
                particles.append(SparkParticle(self.wx, self.wy, 0.4))
            self.is_active = False
            return False

        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        from src.isometric.voxel_renderer import draw_voxel_box

        # Núcleo central da shuriken
        draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05, self.wz, 0.10, 0.10, 0.05, COLOR_STEEL)

        # 4 pontas afiadas girando
        rad = math.radians(self.rot_angle)
        rx = math.cos(rad) * 0.12
        ry = math.sin(rad) * 0.12
        draw_voxel_box(surface, camera, self.wx + rx - 0.03, self.wy + ry - 0.03, self.wz, 0.06, 0.06, 0.04, COLOR_WHITE)
        draw_voxel_box(surface, camera, self.wx - rx - 0.03, self.wy - ry - 0.03, self.wz, 0.06, 0.06, 0.04, COLOR_WHITE)
        draw_voxel_box(surface, camera, self.wx - ry - 0.03, self.wy + rx - 0.03, self.wz, 0.06, 0.06, 0.04, COLOR_STEEL)
        draw_voxel_box(surface, camera, self.wx + ry - 0.03, self.wy - rx - 0.03, self.wz, 0.06, 0.06, 0.04, COLOR_STEEL)


class TimedBombEntity:
    """Bomba explosiva arremessada em arco parabólico 3D lento. Detona por contato ou tempo (2.0s)."""
    def __init__(self, wx: float, wy: float, wz: float = 0.65, dir_x: float = 0.0, dir_y: float = 0.0, owner = None):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.owner = owner

        speed = 9.2
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.vz = 3.6
        self.gz = -12.5
        self.is_airborne = True

        self.fuse_timer = 1.2
        self.explosion_radius = 2.1
        self.is_active = True
        self.spark_timer = 0.0

    def update(self, dt: float, game_map, particles: list = None) -> bool:
        if not self.is_active:
            return False

        self.fuse_timer -= dt
        self.spark_timer += dt

        # Movimento balístico em arco 3D
        if self.is_airborne:
            self.wx += self.vx * dt
            self.wy += self.vy * dt
            self.wz += self.vz * dt
            self.vz += self.gz * dt

            # Colisão com rochas ou poço durante o voo
            for r in game_map.rocks:
                if world_distance(self.wx, self.wy, r.wx, r.wy) < r.radius:
                    self.vx = 0.0
                    self.vy = 0.0
                    break
            if game_map.well and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
                self.vx = 0.0
                self.vy = 0.0

            if self.wz <= 0.05:
                self.wz = 0.05
                self.is_airborne = False
                self.vx = 0.0
                self.vy = 0.0
                if particles is not None:
                    for _ in range(4):
                        particles.append(SparkParticle(self.wx, self.wy, 0.2))

        # Faíscas saindo do pavio enquanto queima
        if self.spark_timer > 0.08:
            self.spark_timer = 0.0
            if particles is not None:
                particles.append(SparkParticle(self.wx, self.wy, self.wz + 0.3))

        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        from src.isometric.voxel_renderer import draw_voxel_box

        # Sombra no solo projetada
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)
        shadow_scale = max(0.4, 1.0 - self.wz * 0.4)
        sw = max(6, int(20 * shadow_scale))
        sh = max(3, int(10 * shadow_scale))
        pygame.draw.ellipse(surface, (12, 16, 14), (base_sx - sw // 2, base_sy - sh // 2, sw, sh))

        # Cubo de ferro da bomba
        draw_voxel_box(surface, camera, self.wx - 0.13, self.wy - 0.13, self.wz, 0.26, 0.26, 0.26, (30, 32, 38))
        # Aro de reforço metálico
        draw_voxel_box(surface, camera, self.wx - 0.15, self.wy - 0.15, self.wz + 0.08, 0.30, 0.30, 0.10, (55, 60, 70), outline=False)
        # Bocal do pavio
        draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - 0.04, self.wz + 0.26, 0.08, 0.08, 0.08, (140, 110, 60))
        # Faísca voxel pulsante no pavio
        fuse_color = (255, 160, 30) if int(self.fuse_timer * 15) % 2 == 0 else (255, 230, 80)
        draw_voxel_box(surface, camera, self.wx - 0.03, self.wy - 0.03, self.wz + 0.34, 0.06, 0.06, 0.06, fuse_color)


class SmokeCloudEntity:
    """Cortina de fumaça instantânea que causa Slow severo no oponente e camufla fuga."""
    def __init__(self, wx: float, wy: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = 0.2
        self.owner = owner
        self.duration = 3.2
        self.age = 0.0
        self.radius = 2.4
        self.is_active = True

        # Partículas internas da fumaça em coordenadas volumétricas de mundo
        self.puffs = [
            (math.cos(i * 0.78) * 0.9, math.sin(i * 0.78) * 0.9, 0.08 + (i % 3) * 0.12, 0.44 + (i % 2) * 0.12)
            for i in range(8)
        ]

    def update(self, dt: float, game_map, particles: list = None) -> bool:
        self.age += dt
        if self.age >= self.duration:
            self.is_active = False
            return False
        return True

    def is_inside(self, target_wx: float, target_wy: float) -> bool:
        return world_distance(self.wx, self.wy, target_wx, target_wy) < self.radius

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        from src.isometric.voxel_renderer import draw_voxel_box

        alpha = max(0, min(160, int((1.0 - (self.age / self.duration)) * 160)))

        # Nuvem de blocos voxels semitransparentes que se expandem suavemente
        expansion = 1.0 + (self.age / self.duration) * 0.5
        for ox, oy, oz, size in self.puffs:
            bx = self.wx + ox * expansion - size * 0.5
            by = self.wy + oy * expansion - size * 0.5
            bz = self.wz + oz
            draw_voxel_box(
                surface, camera,
                bx, by, bz,
                size, size, size * 0.8,
                (160, 168, 175),
                outline=True,
                alpha=alpha
            )


class RemoteMineEntity:
    """Mina de detonação remota de Kasumi (Item 16).
    1º toque: Planta no solo com atraso de armamento de 0.4s.
    2º toque: Detona remotamente gerando explosão letal que atinge também Kasumi se estiver no raio.
    """
    def __init__(self, wx: float, wy: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = 0.05
        self.owner = owner
        self.radius = 2.2
        self.arm_delay = 0.40
        self.age = 0.0
        self.is_active = True
        self.is_armed = False

    def is_ready_to_detonate(self) -> bool:
        return self.is_active and self.age >= self.arm_delay

    def update(self, dt: float, game_map, particles: list = None) -> bool:
        if not self.is_active:
            return False
        self.age += dt
        if self.age >= self.arm_delay:
            self.is_armed = True
        return True

    def detonate(self, fighters: list, particles: list = None, banners: list = None, cinematic_director = None):
        """Detona a mina: danifica todos os combatentes no raio de 2.2m (incluindo o próprio dono se estiver no raio - Item 16)."""
        if not self.is_active:
            return
        self.is_active = False

        if particles is not None:
            from src.effects.particles import SparkParticle
            for _ in range(25):
                particles.append(SparkParticle(self.wx, self.wy, 0.6))

        if banners is not None:
            from src.effects.particles import FloatingBanner
            banners.append(FloatingBanner("REMOTE DETONATION!", self.wx, self.wy, wz=1.8, color=(255, 120, 40)))

        for f in fighters:
            if getattr(f, "is_alive", False):
                dist = world_distance(self.wx, self.wy, f.wx, f.wy)
                if dist <= (self.radius + getattr(f, "radius", 0.4)):
                    dmg = 1 if f == self.owner else 2
                    hit, dead = f.take_hit((0.0, 0.0), damage=dmg)
                    if dead and cinematic_director:
                        cinematic_director.trigger_fatal_strike(self.owner, f, "HEADSHOT_EXPLODE", (0, 0))
            if hasattr(f, "dog") and f.dog and f.dog.state != "KNOCKED_OUT":
                if world_distance(self.wx, self.wy, f.dog.wx, f.dog.wy) <= (self.radius + f.dog.radius):
                    f.dog.knock_out(2.0)
                    if banners is not None:
                        banners.append(FloatingBanner("DOG STUNNED! (2.0s)", f.dog.wx, f.dog.wy, wz=1.4, color=(255, 80, 80)))

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.voxel_renderer import draw_voxel_box

        # Sombra suave no chão
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)
        pygame.draw.ellipse(surface, (15, 18, 16), (base_sx - 12, base_sy - 6, 24, 12))

        # Base da mina em ferro fundido facetado em voxel
        draw_voxel_box(surface, camera, self.wx - 0.14, self.wy - 0.14, 0.0, 0.28, 0.28, 0.10, (45, 48, 54))
        # Placa central metálica
        draw_voxel_box(surface, camera, self.wx - 0.10, self.wy - 0.10, 0.09, 0.20, 0.20, 0.06, (70, 75, 85))

        # LED indicador de armamento (Vermelho pulsante enquanto arma, Verde/Vermelho brilhante após armada)
        if self.is_armed:
            pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.015)
            led_color = (255, int(40 + pulse * 60), 30)
            glow_rad = int(8 + pulse * 4)
            glow_s = pygame.Surface((glow_rad * 2, glow_rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_s, (255, 60, 40, int(60 + pulse * 80)), (glow_rad, glow_rad), glow_rad)
            surface.blit(glow_s, (base_sx - glow_rad, base_sy - 15 - glow_rad))
        else:
            led_color = (255, 200, 40)  # Âmbar (armando...)

        draw_voxel_box(surface, camera, self.wx - 0.03, self.wy - 0.03, 0.15, 0.06, 0.06, 0.06, led_color, outline=False)


class KusarigamaChainEntity:
    """
    Corrente da Kusarigama com peso de ferro na ponta.
    Lançada a média distância; ao atingir o alvo, engata e puxa o oponente rapidamente para perto.
    O oponente puxado permanece livre para agir ou desferir golpes durante/após a puxada.
    """
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner):
        self.owner = owner
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.dir_x = dir_x
        self.dir_y = dir_y

        self.speed = 17.0
        self.pull_speed = 11.0
        self.max_reach = 5.2
        self.reach_traveled = 0.0

        self.state = "FLYING"  # "FLYING", "HOOKED_PULLING", "RETRACTING"
        self.target = None
        self.hook_timer = 0.0
        self.max_pull_time = 0.65
        self.is_active = True

    def update(self, dt: float, game_map, particles: list = None) -> bool:
        if not self.is_active:
            return False

        if self.state == "FLYING":
            step = self.speed * dt
            self.wx += self.dir_x * step
            self.wy += self.dir_y * step
            self.reach_traveled += step

            # Corte de bambus na trajetória da corrente pesada
            for b in game_map.bamboos:
                if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.45:
                    slice_part = b.cut((self.dir_x, self.dir_y))
                    if slice_part and particles is not None:
                        particles.append(slice_part)

            # Colisão com rochas ou poço retrai a corrente
            hit_obs = False
            for r in game_map.rocks:
                if world_distance(self.wx, self.wy, r.wx, r.wy) < r.radius:
                    hit_obs = True
                    break
            if game_map.well and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
                hit_obs = True

            if hit_obs or self.reach_traveled >= self.max_reach:
                self.state = "RETRACTING"
                if particles is not None:
                    for _ in range(4):
                        particles.append(SparkParticle(self.wx, self.wy, 0.3))

        elif self.state == "HOOKED_PULLING":
            if not self.target or not self.target.is_alive:
                self.state = "RETRACTING"
                return True

            # Ponta da corrente permanece fixada no adversário
            self.wx = self.target.wx
            self.wy = self.target.wy

            # Puxar o oponente em linha reta em direção ao Ninja Roxo
            dx = self.owner.wx - self.target.wx
            dy = self.owner.wy - self.target.wy
            dist = math.hypot(dx, dy)

            self.hook_timer += dt

            # Se já puxou bem para perto (dist <= 0.95) ou o tempo limite estourou, solta
            if dist <= 0.95 or self.hook_timer >= self.max_pull_time:
                self.state = "RETRACTING"
            else:
                step_pull = min(dist, self.pull_speed * dt)
                nx, ny = dx / dist, dy / dist
                self.target.wx += nx * step_pull
                self.target.wy += ny * step_pull

                if particles is not None and random.random() < 0.3:
                    particles.append(SparkParticle(self.target.wx, self.target.wy, 0.2))

        elif self.state == "RETRACTING":
            dx = self.owner.wx - self.wx
            dy = self.owner.wy - self.wy
            dist = math.hypot(dx, dy)

            if dist < 0.6:
                self.is_active = False
                return False

            step_retract = min(dist, (self.speed * 1.6) * dt)
            self.wx += (dx / dist) * step_retract
            self.wy += (dy / dist) * step_retract

        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        # Ponto de origem: mãos/cintura do dono
        ox = self.owner.wx
        oy = self.owner.wy
        oz = 0.4
        sx1, sy1 = camera.apply(ox, oy, oz)
        sx2, sy2 = camera.apply(self.wx, self.wy, self.wz)

        # Desenhar elos de corrente entre a origem e a ponta
        chain_dx = sx2 - sx1
        chain_dy = sy2 - sy1
        chain_dist = math.hypot(chain_dx, chain_dy)

        if chain_dist > 5:
            num_links = max(2, int(chain_dist / 11))
            for i in range(num_links + 1):
                t = i / float(num_links)
                lx = int(sx1 + chain_dx * t)
                ly = int(sy1 + chain_dy * t)
                # Efeito ondulatório tênue na corrente
                wobble = int(math.sin(t * math.pi * 3 + self.reach_traveled * 4) * 2)
                link_color = (185, 190, 200) if i % 2 == 0 else (130, 135, 145)
                pygame.draw.circle(surface, link_color, (lx, ly + wobble), 2)

        # Ponta: Peso de ferro cúbico facetado em voxel 3D (Fundo)
        from src.isometric.voxel_renderer import draw_voxel_box
        draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, self.wz - 0.04, 0.16, 0.16, 0.16, (65, 70, 80))

        # Brilho místico se estiver puxando o oponente
        if self.state == "HOOKED_PULLING":
            pygame.draw.circle(surface, (195, 120, 255), (int(sx2), int(sy2)), 10, 2)


class MusketBulletProjectile:
    """Bala de chumbo supersônica disparada pelo Rifleman Tanegashima. 1-Hit Kill."""
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.owner = owner
        speed = 18.5  # Velocidade calibrada (era 24.0) para permitir reação e esquiva tática
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.is_active = True
        self.dist_traveled = 0.0
        self.max_range = 18.0

    def update(self, dt: float, game_map, particles: list = None) -> bool:
        if not self.is_active:
            return False

        step = math.hypot(self.vx * dt, self.vy * dt)
        self.wx += self.vx * dt
        self.wy += self.vy * dt
        self.dist_traveled += step

        # Fumaça no rastro da bala
        if particles is not None and random.random() < 0.4:
            particles.append(SparkParticle(self.wx, self.wy, self.wz))

        # Cortar bambus no caminho
        for b in game_map.bamboos:
            if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.5:
                part = b.cut((self.dir_x, self.dir_y))
                if part and particles is not None:
                    particles.append(part)

        # Colisão com rochas ou poço
        hit_obstacle = False
        for r in game_map.rocks:
            if world_distance(self.wx, self.wy, r.wx, r.wy) < r.radius:
                hit_obstacle = True; break
        if game_map.well and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
            hit_obstacle = True

        if hit_obstacle or self.dist_traveled >= self.max_range:
            self.is_active = False
            if particles is not None:
                for _ in range(6):
                    particles.append(SparkParticle(self.wx, self.wy, 0.4))
            return False

        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.voxel_renderer import draw_voxel_box
        draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05, self.wz, 0.10, 0.10, 0.10, (230, 220, 180))
        # Brilho do tiro de pólvora
        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        pygame.draw.circle(surface, (255, 235, 120), (sx, sy), 3)


class PoisonCloudProjectile:
    """Nuvem de veneno cusparada pelo Kabuki. Aplica contagem regressiva fatal de 10s."""
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.owner = owner
        speed = 7.2
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.radius = 0.55
        self.max_radius = 1.40
        self.lifetime = 1.35
        self.age = 0.0
        self.is_active = True

    def update(self, dt: float, game_map, particles: list = None) -> bool:
        if not self.is_active:
            return False
        self.age += dt
        if self.age >= self.lifetime:
            self.is_active = False
            return False

        # Desacelera e expande em raio
        friction = max(0.0, 1.0 - (self.age / self.lifetime))
        self.wx += self.vx * friction * dt
        self.wy += self.vy * friction * dt
        self.radius = 0.55 + (self.max_radius - 0.55) * (self.age / self.lifetime)
        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active or self.age >= self.lifetime:
            return

        progress = min(1.0, max(0.0, self.age / self.lifetime))
        alpha = max(0, min(140, int(160 * (1.0 - progress))))
        if alpha <= 0:
            return

        # Plumas de vapor esvoaçante em formato de névoa orgânica
        for i in range(5):
            angle = i * 1.25 + self.age * 2.2
            dist = (self.radius * 0.45) * (0.6 + 0.4 * progress)
            ox = math.cos(angle) * dist
            oy = math.sin(angle) * dist
            px, py = camera.apply(self.wx + ox, self.wy + oy, self.wz + math.sin(angle) * 0.05)
            pw = int(self.radius * 18)
            ph = max(3, int(pw * 0.55))

            surf = pygame.Surface((pw * 2, ph * 2), pygame.SRCALPHA)
            col = (135, 45, 185) if i % 2 == 0 else (65, 165, 95)
            pygame.draw.ellipse(surf, (*col, alpha), (0, 0, pw * 2, ph * 2))
            pygame.draw.ellipse(surf, (180, 85, 230, int(alpha * 0.6)), (pw // 4, ph // 4, int(pw * 1.5), int(ph * 1.5)))
            surface.blit(surf, (px - pw, py - ph))


class KyudoArrowProjectile:
    """Flecha letal disparada pelo grande arco Yumi do arqueiro tradicional. 1-Hit Kill."""
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.owner = owner
        speed = 28.0
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.dist_traveled = 0.0
        self.max_range = 16.0
        self.is_active = True

    def update(self, dt: float, game_map, particles: list = None) -> bool:
        if not self.is_active:
            return False
        step = math.hypot(self.vx * dt, self.vy * dt)
        self.wx += self.vx * dt
        self.wy += self.vy * dt
        self.dist_traveled += step

        # Cortar bambus no caminho
        for b in game_map.bamboos:
            if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.45:
                part = b.cut((self.dir_x, self.dir_y))
                if part and particles is not None:
                    particles.append(part)

        # Colisão com rochas ou poço
        hit_obstacle = False
        for r in game_map.rocks:
            if world_distance(self.wx, self.wy, r.wx, r.wy) < r.radius:
                hit_obstacle = True; break
        if game_map.well and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
            hit_obstacle = True

        if hit_obstacle or self.dist_traveled >= self.max_range:
            self.is_active = False
            if particles is not None:
                for _ in range(4):
                    particles.append(SparkParticle(self.wx, self.wy, 0.3))
            return False
        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.voxel_renderer import draw_voxel_box
        # Ponta de ferro
        draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - 0.04, self.wz, 0.08, 0.08, 0.08, COLOR_STEEL)
        # Haste de bambu
        hx = self.wx - self.dir_x * 0.16
        hy = self.wy - self.dir_y * 0.16
        draw_voxel_box(surface, camera, hx - 0.03, hy - 0.03, self.wz, 0.06, 0.06, 0.06, (180, 140, 80))
        # Penas brancas
        fx = self.wx - self.dir_x * 0.30
        fy = self.wy - self.dir_y * 0.30
        draw_voxel_box(surface, camera, fx - 0.04, fy - 0.04, self.wz, 0.08, 0.08, 0.08, COLOR_WHITE)


class RopeArrowProjectile:
    """Flecha de corda do Arqueiro Kyudo. Ao se fixar em obstáculo ou solo, puxa o arqueiro velozmente."""
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner, start_latched: bool = False):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.owner = owner
        speed = 24.0
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.state = "LATCHED_PULLING" if start_latched else "FLYING"
        self.dist_traveled = 0.0
        self.max_range = 10.5
        self.is_active = True
        self.pull_timer = 0.0

    def update(self, dt: float, game_map, particles: list = None) -> bool:
        if not self.is_active:
            return False

        min_x = 1.0
        max_x = (game_map.cols - 1.0) if game_map else 20.0
        min_y = 1.0
        max_y = (game_map.rows - 1.0) if game_map else 20.0

        if self.state == "FLYING":
            step = math.hypot(self.vx * dt, self.vy * dt)
            self.wx += self.vx * dt
            self.wy += self.vy * dt
            self.dist_traveled += step

            # Cravar em obstáculos rígidos da arena (rochas e poço)
            hit = False
            if game_map:
                for r in game_map.rocks:
                    if world_distance(self.wx, self.wy, r.wx, r.wy) < r.radius + 0.2:
                        hit = True; break
                if not hit and game_map.well and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius + 0.2:
                    hit = True

                # Cortar bambus no trajeto sem ser interrompida
                for b in game_map.bamboos:
                    if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.5:
                        part = b.cut((self.dir_x, self.dir_y))
                        if part and particles is not None:
                            particles.append(part)

            # Limite estrito de arena: a flecha NÃO pode ultrapassar as bordas do mapa
            hit_boundary = False
            if self.wx <= min_x:
                self.wx = min_x
                hit_boundary = True
            elif self.wx >= max_x:
                self.wx = max_x
                hit_boundary = True

            if self.wy <= min_y:
                self.wy = min_y
                hit_boundary = True
            elif self.wy >= max_y:
                self.wy = max_y
                hit_boundary = True

            if hit or hit_boundary or self.dist_traveled >= self.max_range:
                self.wx = max(min_x, min(max_x, self.wx))
                self.wy = max(min_y, min(max_y, self.wy))
                self.state = "LATCHED_PULLING"
                if particles is not None:
                    for _ in range(6):
                        particles.append(SparkParticle(self.wx, self.wy, 0.3))

        elif self.state == "LATCHED_PULLING":
            self.pull_timer += dt
            # Garante que a ponta cravada permaneça dentro dos limites
            self.wx = max(min_x, min(max_x, self.wx))
            self.wy = max(min_y, min(max_y, self.wy))

            # Puxar o arqueiro até a ponta cravada
            dx = self.wx - self.owner.wx
            dy = self.wy - self.owner.wy
            dist = math.hypot(dx, dy)
            if dist <= 0.85 or self.pull_timer >= 0.70:
                self.is_active = False
                return False
            else:
                pull_speed = 22.0
                step = min(dist, pull_speed * dt)
                self.owner.wx += (dx / dist) * step
                self.owner.wy += (dy / dist) * step
                # Garantir que o arqueiro permaneça 100% dentro dos limites do mapa durante o trajeto
                self.owner.wx = max(min_x, min(max_x, self.owner.wx))
                self.owner.wy = max(min_y, min(max_y, self.owner.wy))

                # Cortar bambus atravessados durante o deslocamento de fuga
                if game_map:
                    for b in game_map.bamboos:
                        if not b.is_cut and world_distance(self.owner.wx, self.owner.wy, b.wx, b.wy) < 0.6:
                            part = b.cut((dx / dist, dy / dist))
                            if part and particles is not None:
                                particles.append(part)

                if particles is not None and random.random() < 0.4:
                    particles.append(SparkParticle(self.owner.wx, self.owner.wy, 0.2))

        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.voxel_renderer import draw_voxel_box

        # Desenhar corda entre o arqueiro e a ponta
        ox, oy = self.owner.wx, self.owner.wy
        sx1, sy1 = camera.apply(ox, oy, 0.4)
        sx2, sy2 = camera.apply(self.wx, self.wy, self.wz)
        pygame.draw.line(surface, (190, 175, 140), (sx1, sy1), (sx2, sy2), 2)

        # Gancho / ponta da flecha cravada
        draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05, self.wz, 0.10, 0.10, 0.10, (140, 145, 155))
        if self.state == "LATCHED_PULLING":
            pygame.draw.circle(surface, (120, 220, 160), (int(sx2), int(sy2)), 8, 2)


class CannonballProjectile:
    """Bala de canhão naval pesada que cai verticalmente do céu em área de impacto com explosão fatal."""
    def __init__(self, target_wx: float, target_wy: float, owner):
        self.wx = target_wx
        self.wy = target_wy
        self.wz = 9.0       # Altura no céu
        self.target_wx = target_wx
        self.target_wy = target_wy
        self.fall_speed = 22.0
        self.owner = owner
        self.radius = 1.6   # Raio de dano em área
        self.is_active = True
        self.has_exploded = False
        self.explosion_timer = 0.35

    def update(self, dt: float, game_map=None, particles: list = None, camera = None, fighters: list = None) -> bool:
        if not self.is_active:
            return False

        if not self.has_exploded:
            self.wz -= self.fall_speed * dt
            if self.wz <= 0.0:
                self.wz = 0.0
                self.has_exploded = True
                if camera and hasattr(camera, "add_shake"):
                    camera.add_shake(12.0)
                if particles is not None:
                    from src.effects.particles import SparkParticle, FlameVoxelParticle
                    for _ in range(40):
                        particles.append(FlameVoxelParticle(self.wx, self.wy, wz=0.15))
                    for _ in range(16):
                        particles.append(SparkParticle(self.wx, self.wy, 0.45))
                # Dano fatal de área em todos os combatentes no raio de explosão
                if fighters:
                    for f in fighters:
                        if getattr(f, "is_alive", False) and f is not self.owner:
                            dist = math.hypot(f.wx - self.wx, f.wy - self.wy)
                            if dist < (self.radius + getattr(f, "radius", 0.35)):
                                f.take_hit((0.0, 0.0), damage=2)
        else:
            self.explosion_timer -= dt
            if self.explosion_timer <= 0:
                self.is_active = False
                return False
        return self.is_active

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        # Sombra no solo que expande à medida que a bala se aproxima
        sx_g, sy_g = camera.apply(self.wx, self.wy, 0.0)
        progress = max(0.1, 1.0 - (self.wz / 9.0))
        shadow_r = int(14 * progress)
        pygame.draw.ellipse(surface, (10, 10, 12, 180), (sx_g - shadow_r, sy_g - shadow_r // 2, shadow_r * 2, shadow_r))

        if not self.has_exploded:
            # Bala esférica pesada de ferro fundido com Jolly Roger pirata estampada
            sx, sy = camera.apply(self.wx, self.wy, self.wz)
            ball_r = 13
            # Corpo metálico e sombreamento esférico
            pygame.draw.circle(surface, (28, 30, 36), (sx, sy), ball_r)
            pygame.draw.circle(surface, (45, 50, 60), (sx - 1, sy - 1), ball_r - 2)
            pygame.draw.circle(surface, (80, 90, 105), (sx - 4, sy - 4), 4) # Brilho especular zenital
            pygame.draw.circle(surface, (14, 16, 20), (sx, sy), ball_r, 2) # Borda de ferro forjado

            # Caveira Pirata estilizada (Jolly Roger) em osso branco fosco
            skull_col = (235, 235, 235)
            dark_col = (20, 22, 26)

            # Ossos cruzados atrás (X)
            pygame.draw.line(surface, (190, 195, 205), (sx - 7, sy - 6), (sx + 7, sy + 6), 2)
            pygame.draw.line(surface, (190, 195, 205), (sx + 7, sy - 6), (sx - 7, sy + 6), 2)

            # Crânio
            pygame.draw.circle(surface, skull_col, (sx, sy - 1), 5)
            # Mandíbula / dentes
            pygame.draw.rect(surface, skull_col, (sx - 3, sy + 2, 6, 4), border_radius=1)
            # Linha de divisão dos dentes
            pygame.draw.line(surface, dark_col, (sx, sy + 3), (sx, sy + 5), 1)

            # Órbitas oculares vazias
            pygame.draw.circle(surface, dark_col, (sx - 2, sy - 1), 1)
            pygame.draw.circle(surface, dark_col, (sx + 2, sy - 1), 1)
            # Cavidade nasal
            pygame.draw.rect(surface, dark_col, (sx, sy + 1, 1, 1))
        else:
            # Clarão de impacto inicial e onda de choque no solo
            progress = max(0.0, min(1.0, 1.0 - (self.explosion_timer / 0.35)))
            exp_w = int(self.radius * 34 * progress)
            exp_h = max(2, exp_w // 2)
            if exp_w > 4:
                exp_surf = pygame.Surface((exp_w * 2, exp_h * 2 + 10), pygame.SRCALPHA)
                alpha_val = max(0, min(255, int((1.0 - progress) * 220)))
                pygame.draw.ellipse(exp_surf, (255, 120, 20, alpha_val), (0, 0, exp_w * 2, exp_h * 2))
                pygame.draw.ellipse(exp_surf, (255, 220, 70, min(255, alpha_val + 30)), (exp_w // 4, exp_h // 4, int(exp_w * 1.5), int(exp_h * 1.5)))
                pygame.draw.ellipse(exp_surf, (255, 255, 200, alpha_val), (exp_w // 2, exp_h // 2, exp_w, exp_h))
                surface.blit(exp_surf, (sx_g - exp_w, sy_g - exp_h))




