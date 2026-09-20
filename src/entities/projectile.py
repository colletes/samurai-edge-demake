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
        """Renderiza a kunai no ar ou cravada no chão."""
        if not self.is_active:
            return

        sx, sy = camera.apply(self.wx, self.wy, self.wz)

        if self.state == "FLYING":
            # Lâmina em vôo orientada para a direção
            rad = self.angle
            tail_x = int(sx - math.cos(rad) * 12)
            tail_y = int(sy - math.sin(rad) * 8)
            head_x = int(sx + math.cos(rad) * 12)
            head_y = int(sy + math.sin(rad) * 8)

            pygame.draw.line(surface, COLOR_STEEL, (tail_x, tail_y), (head_x, head_y), 4)
            pygame.draw.line(surface, COLOR_WHITE, (tail_x, tail_y), (head_x, head_y), 2)
            # Rastro de velocidade
            pygame.draw.circle(surface, COLOR_YELLOW_AURA, (head_x, head_y), 3)

        else:
            # Cravada diagonalmente no solo
            pygame.draw.line(surface, COLOR_BLACK, (sx - 2, sy), (sx + 2, sy), 4)
            # Lâmina fincada
            pygame.draw.line(surface, COLOR_STEEL, (sx, sy), (sx + 5, sy - 14), 3)
            # Anel circular da empunhadura da kunai
            pygame.draw.circle(surface, COLOR_GOLD, (sx + 5, sy - 14), 3, 1)


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

        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        rad = math.radians(self.rot_angle)

        # Desenhar Shuriken de 4 pontas com rotação
        radius = 7
        p1 = (sx + int(math.cos(rad) * radius), sy + int(math.sin(rad) * radius * 0.6))
        p2 = (sx + int(math.cos(rad + math.pi/2) * radius), sy + int(math.sin(rad + math.pi/2) * radius * 0.6))
        p3 = (sx + int(math.cos(rad + math.pi) * radius), sy + int(math.sin(rad + math.pi) * radius * 0.6))
        p4 = (sx + int(math.cos(rad + 3*math.pi/2) * radius), sy + int(math.sin(rad + 3*math.pi/2) * radius * 0.6))

        pygame.draw.line(surface, COLOR_STEEL, p1, p3, 3)
        pygame.draw.line(surface, COLOR_STEEL, p2, p4, 3)
        pygame.draw.circle(surface, COLOR_WHITE, (sx, sy), 2)


class TimedBombEntity:
    """Bomba explosiva com delay de pavio (1.5s). Causa explosão fatal em área (AOE)."""
    def __init__(self, wx: float, wy: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = 0.05
        self.owner = owner
        self.fuse_timer = 1.5
        self.explosion_radius = 2.2
        self.is_active = True
        self.spark_timer = 0.0

    def update(self, dt: float, game_map, particles: list = None) -> bool:
        if not self.is_active:
            return False

        self.fuse_timer -= dt
        self.spark_timer += dt

        # Faíscas saindo do pavio enquanto queima
        if self.spark_timer > 0.08:
            self.spark_timer = 0.0
            if particles is not None:
                particles.append(SparkParticle(self.wx, self.wy, 0.45))

        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        sx, sy = camera.apply(self.wx, self.wy, self.wz)

        # Sombra no chão
        pygame.draw.ellipse(surface, (10, 15, 12, 120), (sx - 8, sy - 3, 16, 6))
        # Esfera preta de ferro
        pygame.draw.circle(surface, (25, 25, 30), (sx, sy - 5), 7)
        pygame.draw.circle(surface, (60, 65, 75), (sx - 2, sy - 7), 2)  # Reflexo metálico
        # Bocal e Pavio aceso
        pygame.draw.line(surface, (140, 110, 60), (sx, sy - 12), (sx + 3, sy - 16), 2)
        # Faísca no topo do pavio
        fuse_color = (255, 160, 30) if int(self.fuse_timer * 15) % 2 == 0 else (255, 230, 80)
        pygame.draw.circle(surface, fuse_color, (sx + 3, sy - 16), 3)


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

        # Partículas internas da fumaça
        self.puffs = [
            (math.cos(i * 0.7) * 1.2, math.sin(i * 0.7) * 1.2, 18 + (i % 3) * 6)
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

        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        alpha = max(0, min(180, int((1.0 - (self.age / self.duration)) * 180)))

        smoke_surf = pygame.Surface((180, 140), pygame.SRCALPHA)
        scx, scy = 90, 70

        # Desenhar múltiplas nuvens volumosas com transparência
        for ox, oy, r in self.puffs:
            px = scx + int(ox * 28)
            py = scy + int(oy * 16)
            pygame.draw.circle(smoke_surf, (150, 160, 165, alpha), (px, py), r)
            pygame.draw.circle(smoke_surf, (185, 195, 200, alpha // 2), (px, py), r - 4)

        surface.blit(smoke_surf, (sx - 90, sy - 70))


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

        # Ponta: Peso de ferro esférico multifacetado (Fundo)
        pygame.draw.circle(surface, (20, 20, 25), (int(sx2), int(sy2)), 6)
        pygame.draw.circle(surface, (140, 145, 160), (int(sx2 - 1), int(sy2 - 1)), 4)
        pygame.draw.circle(surface, (210, 215, 230), (int(sx2 - 2), int(sy2 - 2)), 2)

        # Brilho místico se estiver puxando o oponente
        if self.state == "HOOKED_PULLING":
            pygame.draw.circle(surface, (195, 120, 255), (int(sx2), int(sy2)), 8, 1)



