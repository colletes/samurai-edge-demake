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
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.owner = owner

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

            # Corte de bambus no caminho
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
        """Renderiza a kunai no ar ou cravada no chão como modelo voxel 3D."""
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
            pygame.draw.ellipse(surface, (15, 20, 18), (base_sx - 6, base_sy - 3, 12, 6))
            # Haste cravada
            draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05, 0.02, 0.10, 0.10, 0.16, COLOR_STEEL)
            # Anel / empunhadura dourada
            draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - 0.04, 0.18, 0.08, 0.08, 0.08, COLOR_GOLD)


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
        speed = 24.0
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
        if not self.is_active:
            return
        from src.isometric.voxel_renderer import draw_voxel_box
        color_p = (165, 60, 215)
        color_g = (70, 220, 125)

        for i in range(4):
            angle = i * 1.57 + self.age * 3.5
            ox = math.cos(angle) * (self.radius * 0.45)
            oy = math.sin(angle) * (self.radius * 0.45)
            c = color_p if i % 2 == 0 else color_g
            draw_voxel_box(surface, camera, self.wx + ox - 0.12, self.wy + oy - 0.12, self.wz, 0.24, 0.24, 0.24, c)


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
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.owner = owner
        speed = 22.0
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.state = "FLYING" # "FLYING", "LATCHED_PULLING"
        self.dist_traveled = 0.0
        self.max_range = 11.5
        self.is_active = True
        self.pull_timer = 0.0

    def update(self, dt: float, game_map, particles: list = None) -> bool:
        if not self.is_active:
            return False

        if self.state == "FLYING":
            step = math.hypot(self.vx * dt, self.vy * dt)
            self.wx += self.vx * dt
            self.wy += self.vy * dt
            self.dist_traveled += step

            # Cravar em obstáculos ou alcance
            hit = False
            for r in game_map.rocks:
                if world_distance(self.wx, self.wy, r.wx, r.wy) < r.radius + 0.2:
                    hit = True; break
            if game_map.well and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius + 0.2:
                hit = True
            for b in game_map.bamboos:
                if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.5:
                    hit = True; break

            if hit or self.dist_traveled >= self.max_range:
                self.state = "LATCHED_PULLING"
                if particles is not None:
                    for _ in range(6):
                        particles.append(SparkParticle(self.wx, self.wy, 0.3))

        elif self.state == "LATCHED_PULLING":
            self.pull_timer += dt
            # Puxar o arqueiro até a ponta cravada
            dx = self.wx - self.owner.wx
            dy = self.wy - self.owner.wy
            dist = math.hypot(dx, dy)
            if dist <= 0.85 or self.pull_timer >= 0.60:
                self.is_active = False
                return False
            else:
                pull_speed = 20.0
                step = min(dist, pull_speed * dt)
                self.owner.wx += (dx / dist) * step
                self.owner.wy += (dy / dist) * step
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



