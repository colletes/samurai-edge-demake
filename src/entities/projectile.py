"""
Entidade KunaiProjectile: projétil arremessado pelo Ninja Amarelo.
Mortal à distância; se errar, crava no solo e pode ser recuperada.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_BLACK, COLOR_GOLD, COLOR_WHITE, COLOR_YELLOW_AURA,
    COLOR_BLUE_AURA
)
from src.isometric.iso_math import world_distance
from src.effects.particles import SparkParticle, FlameVoxelParticle

class KunaiProjectile:
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner, vz: float = 0.0, max_range: float = 6.8):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.owner = owner
        self.vz = vz

        # Velocidade de arremesso
        speed = 24.0  # Velocidade aumentada para tornar a kunai veloz e difícil de parriar a média distância
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.dir_x = dir_x
        self.dir_y = dir_y

        self.state = "FLYING"  # "FLYING" ou "ON_GROUND"
        self.max_range = max_range
        self.dist_traveled = 0.0
        self.angle = math.atan2(dir_y, dir_x)
        self.is_active = True
        self.pickup_delay = 0.25 # Pequeno delay antes de poder pegar para evitar auto-pegar no mesmo frame
        self.has_been_reflected = False  # Anti-spam: previne reflexão infinita

    def update(self, dt: float, game_map, particles: list, opponent=None, **kwargs) -> bool:
        """Atualiza a posição da kunai. Retorna False se deve ser removida."""
        if not self.is_active:
            return False

        if self.state == "FLYING":
            step = math.hypot(self.vx * dt, self.vy * dt)
            self.wx += self.vx * dt
            self.wy += self.vy * dt
            self.dist_traveled += step

            # Item 18: Limites estritos da arena [1.2, cols - 1.2]
            min_bound = 1.2
            max_bound_x = (game_map.cols - 1.2) if (game_map and hasattr(game_map, "cols")) else 19.8
            max_bound_y = (game_map.rows - 1.2) if (game_map and hasattr(game_map, "rows")) else 19.8

            hit_bound = False
            if self.wx <= min_bound or self.wx >= max_bound_x or self.wy <= min_bound or self.wy >= max_bound_y:
                self.wx = max(min_bound, min(max_bound_x, self.wx))
                self.wy = max(min_bound, min(max_bound_y, self.wy))
                hit_bound = True

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
            for r in getattr(game_map, "rocks", []):
                if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                    if world_distance(self.wx, self.wy, r.wx, r.wy) < (getattr(r, "radius", 0.5) + 0.15):
                        r.break_panel((self.dir_x, self.dir_y), particles)
                        hit_obstacle = True
                        break
                elif not getattr(r, "is_broken", False) and world_distance(self.wx, self.wy, r.wx, r.wy) < getattr(r, "radius", 0.6):
                    hit_obstacle = True
                    break
            if game_map and getattr(game_map, "well", None) and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
                hit_obstacle = True

            if hit_obstacle or hit_bound or self.dist_traveled >= self.max_range:
                # Crava no chão
                self.state = "ON_GROUND"
                self.wz = 0.05
                for _ in range(6):
                    particles.append(SparkParticle(self.wx, self.wy, 0.2))

        elif self.state == "ON_GROUND":
            if self.pickup_delay > 0:
                self.pickup_delay -= dt
            else:
                # Se o dono (Hanzo/Ninja) passar por perto (raio 0.95m), chuta/re-arremessa a kunai automaticamente contra o rival!
                if self.owner and getattr(self.owner, "is_alive", True):
                    if world_distance(self.wx, self.wy, self.owner.wx, self.owner.wy) < 0.95:
                        tgt = opponent
                        if tgt is None and hasattr(self.owner, "opponent"):
                            tgt = self.owner.opponent
                        if tgt and getattr(tgt, "is_alive", True):
                            dx = tgt.wx - self.wx
                            dy = tgt.wy - self.wy
                            dist = math.hypot(dx, dy) or 1.0
                            self.dir_x = dx / dist
                            self.dir_y = dy / dist
                        else:
                            self.dir_x = getattr(self.owner, "facing_x", 1.0)
                            self.dir_y = getattr(self.owner, "facing_y", 0.0)

                        speed = 26.0
                        self.vx = self.dir_x * speed
                        self.vy = self.dir_y * speed
                        self.angle = math.atan2(self.dir_y, self.dir_x)
                        self.wz = 0.35
                        self.vz = 0.15
                        self.state = "FLYING"
                        self.dist_traveled = 0.0
                        self.pickup_delay = 0.40
                        self.has_been_reflected = False
                        try:
                            from src.audio.sound_effects import play_sound
                            play_sound("sword_slash", volume=0.90)
                        except Exception:
                            pass
                        for _ in range(10):
                            particles.append(SparkParticle(self.wx, self.wy, 0.35, color=(255, 230, 80)))

        return True

    def render(self, surface: pygame.Surface, camera):
        """Renderiza a kunai no ar com brilho luminoso, rastro e glint estelar ou cravada no chão."""
        if not self.is_active:
            return

        from src.isometric.voxel_renderer import draw_voxel_box

        if self.state == "FLYING":
            sx, sy = camera.apply(self.wx, self.wy, self.wz)

            # 1. Rastro de velocidade luminoso (3 pontos em leque)
            for i in (1, 2, 3):
                trail_wx = self.wx - self.dir_x * (0.08 * i)
                trail_wy = self.wy - self.dir_y * (0.08 * i)
                tsx, tsy = camera.apply(trail_wx, trail_wy, self.wz)
                alpha_t = int(140 / i)
                radius_t = max(1, int(3 - i * 0.7))
                t_surf = pygame.Surface((radius_t * 4, radius_t * 4), pygame.SRCALPHA)
                pygame.draw.circle(t_surf, (255, 220, 60, alpha_t), (radius_t * 2, radius_t * 2), radius_t)
                surface.blit(t_surf, (tsx - radius_t * 2, tsy - radius_t * 2))

            # 2. Lâmina voxel em voo orientada
            draw_voxel_box(surface, camera, self.wx - 0.06, self.wy - 0.06, self.wz, 0.12, 0.12, 0.12, COLOR_STEEL)
            draw_voxel_box(surface, camera, self.wx - self.dir_x * 0.12 - 0.04, self.wy - self.dir_y * 0.12 - 0.04, self.wz + 0.02, 0.08, 0.08, 0.08, COLOR_GOLD)

            # 3. Aura e corona de luz dourada/esmeralda no projétil
            glow_surf = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 230, 90, 85), (14, 14), 13)
            pygame.draw.circle(glow_surf, (255, 255, 200, 160), (14, 14), 7)
            surface.blit(glow_surf, (sx - 14, sy - 14))

            # 4. Glint estelar em cruz (+) e x na ponta da kunai
            pygame.draw.line(surface, (255, 255, 255), (sx - 5, sy), (sx + 5, sy), 2)
            pygame.draw.line(surface, (255, 255, 255), (sx, sy - 5), (sx, sy + 5), 2)
            pygame.draw.circle(surface, (255, 255, 240), (sx, sy), 2)

        else:
            # Cravada no solo em ângulo
            base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)

            # Indicador visual pulsante no piso com aura expandida
            ticks = pygame.time.get_ticks()
            pulse = 0.5 + 0.5 * math.sin(ticks * 0.007)
            glow_rad = int(14 + pulse * 8)
            glow_surf = pygame.Surface((glow_rad * 2, glow_rad * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255, 220, 60, int(55 + pulse * 55)), (0, glow_rad // 2, glow_rad * 2, glow_rad))
            pygame.draw.ellipse(glow_surf, (255, 255, 180, int(90 + pulse * 70)), (glow_rad // 2, glow_rad * 3 // 4, glow_rad, glow_rad // 2))
            surface.blit(glow_surf, (base_sx - glow_rad, base_sy - glow_rad // 2))

            # Sombra e haste cravada
            pygame.draw.ellipse(surface, (15, 20, 18), (base_sx - 6, base_sy - 3, 12, 6))
            draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05, 0.02, 0.10, 0.10, 0.16, COLOR_STEEL)
            draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - 0.04, 0.18, 0.08, 0.08, 0.08, COLOR_GOLD)

            # Marcador vertical flutuante (Bobbing marker com brilho)
            bob = math.sin(ticks * 0.009) * 4.0
            arrow_sx, arrow_sy = camera.apply(self.wx, self.wy, 0.65)
            tip_y = arrow_sy + bob
            pts = [(arrow_sx, tip_y), (arrow_sx - 6, tip_y - 9), (arrow_sx + 6, tip_y - 9)]
            pygame.draw.polygon(surface, (255, 235, 60), pts)
            pygame.draw.polygon(surface, (255, 255, 220), [(arrow_sx, tip_y), (arrow_sx - 3, tip_y - 5), (arrow_sx + 3, tip_y - 5)])
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
        self.has_been_reflected = False  # Anti-spam: previne reflexão infinita

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
        for r in getattr(game_map, "rocks", []):
            if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                if world_distance(self.wx, self.wy, r.wx, r.wy) < (getattr(r, "radius", 0.5) + 0.15):
                    r.break_panel((self.dir_x, self.dir_y), particles)
                    hit_obstacle = True
                    break
            elif not getattr(r, "is_broken", False) and world_distance(self.wx, self.wy, r.wx, r.wy) < getattr(r, "radius", 0.6):
                hit_obstacle = True
                break
        if game_map and getattr(game_map, "well", None) and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
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

        speed = 12.0
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.vz = 3.8
        self.gz = -13.5
        self.is_airborne = True

        self.fuse_timer = 0.85
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
        self.arm_delay = 0.28  # Entregável 4.3: Armamento acelerado para 0.28s (era 0.40s)
        self.age = 0.0
        self.is_active = True
        self.is_armed = False

    def is_ready_to_detonate(self) -> bool:
        return self.is_active and self.age >= self.arm_delay

    def update(self, dt: float, game_map, particles: list = None) -> bool:
        if not self.is_active:
            return False
        self.game_map = game_map
        self.age += dt
        if self.age >= self.arm_delay:
            self.is_armed = True
        return True

    def detonate(self, fighters: list, particles: list = None, banners: list = None, cinematic_director = None, game_map = None):
        """Detona a mina: danifica todos os combatentes no raio de 2.2m (com imunidade a auto-suicídio se Kasumi tiver <= 1 HP)."""
        if not self.is_active:
            return
        self.is_active = False

        gmap = game_map or getattr(self, "game_map", None)
        if gmap:
            for b in getattr(gmap, "bamboos", []):
                if not getattr(b, "is_cut", False) and world_distance(self.wx, self.wy, b.wx, b.wy) < (self.radius + 0.4):
                    part = b.cut((1.0, 0.0))
                    if part and particles is not None:
                        particles.append(part)
            for r in getattr(gmap, "rocks", []):
                if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                    if world_distance(self.wx, self.wy, r.wx, r.wy) < (self.radius + 0.5):
                        r.break_panel((1.0, 0.0), particles)

        if particles is not None:
            from src.effects.particles import SparkParticle
            for _ in range(25):
                particles.append(SparkParticle(self.wx, self.wy, 0.6))

        if banners is not None:
            from src.effects.particles import FloatingBanner

        target_list = list(fighters) if fighters is not None else []
        if self.owner and self.owner not in target_list:
            target_list.append(self.owner)

        for f in target_list:
            if getattr(f, "is_alive", False):
                dist = world_distance(self.wx, self.wy, f.wx, f.wy)
                if dist <= (self.radius + getattr(f, "radius", 0.4)):
                    if f == self.owner:
                        # Entregável 4.3: Imunidade a auto-dano se estiver com <= 1 HP (previne suicídio em desespero)
                        if f.hp > 1:
                            f.hp -= 1
                            f.stun(0.35)
                        else:
                            f.stun(0.15)
                    else:
                        hit, dead = f.take_hit((0.0, 0.0), damage=2)
                        if dead and cinematic_director:
                            cinematic_director.trigger_fatal_strike(self.owner, f, "KASUMI_EXPLODE", (0.0, 0.0))
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
            for r in getattr(game_map, "rocks", []):
                if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                    if world_distance(self.wx, self.wy, r.wx, r.wy) < (getattr(r, "radius", 0.5) + 0.15):
                        r.break_panel((self.dir_x, self.dir_y), particles)
                        hit_obs = True
                        break
                elif not getattr(r, "is_broken", False) and world_distance(self.wx, self.wy, r.wx, r.wy) < getattr(r, "radius", 0.6):
                    hit_obs = True
                    break
            if game_map and getattr(game_map, "well", None) and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
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
    """Bala de chumbo supersônica disparada pelo Rifleman Tanegashima ou Pederneira da Mosqueteira. 1-Hit Kill."""
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner, max_range: float = 18.0):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.owner = owner
        speed = 26.0  # Velocidade balística supersônica de arcabuz / pederneira
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.is_active = True
        self.dist_traveled = 0.0
        self.max_range = max_range
        self.has_been_reflected = False  # Anti-spam: previne reflexão infinita

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
        for r in getattr(game_map, "rocks", []):
            if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                if world_distance(self.wx, self.wy, r.wx, r.wy) < (getattr(r, "radius", 0.5) + 0.15):
                    r.break_panel((self.dir_x, self.dir_y), particles)
                    hit_obstacle = True
                    break
            elif not getattr(r, "is_broken", False) and world_distance(self.wx, self.wy, r.wx, r.wy) < getattr(r, "radius", 0.6):
                hit_obstacle = True
                break
        if game_map and getattr(game_map, "well", None) and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
            hit_obstacle = True

        if hit_obstacle or self.dist_traveled >= self.max_range:
            self.is_active = False
            if particles is not None:
                from src.effects.particles import SmokeParticle
                for _ in range(4):
                    particles.append(SparkParticle(self.wx, self.wy, 0.4))
                particles.append(SmokeParticle(self.wx, self.wy, 0.35, color=(160, 160, 170), size=5))
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
        speed = 32.0  # Velocidade calibrada da flecha Yumi para pressionar esquivas reativas a média distância
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.dist_traveled = 0.0
        self.max_range = 16.0
        self.is_active = True
        self.has_been_reflected = False  # Anti-spam: previne reflexão infinita

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
        for r in getattr(game_map, "rocks", []):
            if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                if world_distance(self.wx, self.wy, r.wx, r.wy) < (getattr(r, "radius", 0.5) + 0.15):
                    r.break_panel((self.dir_x, self.dir_y), particles)
                    hit_obstacle = True
                    break
            elif not getattr(r, "is_broken", False) and world_distance(self.wx, self.wy, r.wx, r.wy) < getattr(r, "radius", 0.6):
                hit_obstacle = True
                break
        if game_map and getattr(game_map, "well", None) and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
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


class HamayaArrowProjectile:
    """
    Flecha ritual sagrada de luz (破魔矢 / Hamaya) do Kyudo.
    Atravessa obstáculos sólidos e exorciza/anula projéteis inimigos em voo.
    1-Hit Kill / Lethal Strike.
    """
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.owner = owner
        speed = 30.0
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.dist_traveled = 0.0
        self.max_range = 18.0
        self.is_active = True
        self.trail_timer = 0.0
        self.has_been_reflected = False  # Anti-spam: previne reflexão infinita

    def update(self, dt: float, game_map, particles: list = None, projectiles: list = None) -> bool:
        if not self.is_active:
            return False
        step = math.hypot(self.vx * dt, self.vy * dt)
        self.wx += self.vx * dt
        self.wy += self.vy * dt
        self.dist_traveled += step

        # Rastro cintilante dourado e sagrado (Kami Spark Trail)
        self.trail_timer += dt
        if particles is not None and self.trail_timer >= 0.02:
            self.trail_timer = 0.0
            particles.append(SparkParticle(self.wx, self.wy, self.wz, color=(255, 235, 110)))
            particles.append(SparkParticle(self.wx - self.dir_x * 0.15, self.wy - self.dir_y * 0.15, self.wz, color=(255, 255, 240)))

        # Transpassa e corta bambus no caminho sem desacelerar
        if game_map and hasattr(game_map, "bamboos"):
            for b in game_map.bamboos:
                if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.55:
                    part = b.cut((self.dir_x, self.dir_y))
                    if part and particles is not None:
                        particles.append(part)

        # Destruição de biombos quebráveis no caminho sem interromper a flecha
        if game_map and hasattr(game_map, "rocks"):
            for r in game_map.rocks:
                if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                    if world_distance(self.wx, self.wy, r.wx, r.wy) < 0.65:
                        r.break_panel((self.dir_x, self.dir_y), particles)

        # Anular projéteis inimigos interceptados no trajeto
        if projectiles:
            for p in projectiles:
                if p is not self and getattr(p, "is_active", False) and getattr(p, "owner", None) is not self.owner:
                    if world_distance(self.wx, self.wy, p.wx, p.wy) < 0.85:
                        p.is_active = False
                        if particles is not None:
                            for _ in range(8):
                                particles.append(SparkParticle(p.wx, p.wy, getattr(p, "wz", 0.4), color=(255, 230, 90)))

        # Perfuração absoluta de rochas e poço (Hamaya atravessa sólidos!)
        # Para apenas se atingir o alcance máximo ou os limites extremos da arena
        min_x = 0.5
        max_x = (game_map.cols - 0.5) if (game_map and hasattr(game_map, "cols")) else 25.0
        min_y = 0.5
        max_y = (game_map.rows - 0.5) if (game_map and hasattr(game_map, "rows")) else 25.0

        if (self.dist_traveled >= self.max_range or 
            self.wx <= min_x or self.wx >= max_x or 
            self.wy <= min_y or self.wy >= max_y):
            self.is_active = False
            if particles is not None:
                for _ in range(6):
                    particles.append(SparkParticle(self.wx, self.wy, self.wz, color=(255, 230, 100)))
            return False
        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.voxel_renderer import draw_voxel_box
        # Ponta de ouro sagrada purificadora
        draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05, self.wz, 0.10, 0.10, 0.10, COLOR_GOLD)
        # Haste de madeira sagrada xintoísta branca
        hx = self.wx - self.dir_x * 0.18
        hy = self.wy - self.dir_y * 0.18
        draw_voxel_box(surface, camera, hx - 0.035, hy - 0.035, self.wz, 0.07, 0.07, 0.07, (250, 245, 235))
        # Penas cerimoniais douradas
        fx = self.wx - self.dir_x * 0.35
        fy = self.wy - self.dir_y * 0.35
        draw_voxel_box(surface, camera, fx - 0.05, fy - 0.05, self.wz, 0.10, 0.10, 0.10, (255, 240, 150))
        # Halo de luz sagrada
        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        pygame.draw.circle(surface, (255, 245, 180), (sx, sy), 5, 1)


class SacredArrowVolleyProjectile:
    """
    Chuva / Salva de Flechas Sagradas em Arco (Hama-no-Ya Rain) disparada por Tomoe.
    Projétil balístico em arco que lança múltiplas flechas sagradas dos céus sobre uma pequena área concentrada.
    Causa dano letal (2 HP) aos alvos pegos no raio de impacto.
    """
    def __init__(self, start_wx: float, start_wy: float, target_wx: float, target_wy: float, owner):
        self.wx = target_wx
        self.wy = target_wy
        self.target_wx = target_wx
        self.target_wy = target_wy
        self.start_wx = start_wx
        self.start_wy = start_wy
        self.start_wz = 0.65
        self.owner = owner
        self.radius = 1.35   # Pequena área concentrada
        self.damage = 2      # Dano letal (2 HP)
        self.is_active = True
        self.has_impacted = False
        self.damage_dealt = False
        self.has_been_reflected = False
        self.elapsed = 0.0
        self.flight_duration = 0.42
        self.linger_duration = 0.38
        self.total_duration = self.flight_duration + self.linger_duration
        self.impact_flash_timer = 0.35

        # Criação de múltiplas flechas sagradas na salva (7 flechas)
        self.arrows = []
        num_arrows = 7
        rng = random.Random(int((target_wx * 37.0 + target_wy * 73.0 + start_wx * 19.0) * 100))
        for i in range(num_arrows):
            angle = (i * (2.0 * math.pi / num_arrows)) + rng.uniform(-0.25, 0.25)
            dist = rng.uniform(0.12, 0.65)
            dest_x = target_wx + dist * math.cos(angle)
            dest_y = target_wy + dist * math.sin(angle)
            stagger = i * 0.016
            apex = rng.uniform(4.5, 5.2)
            self.arrows.append({
                "dest_x": dest_x,
                "dest_y": dest_y,
                "stagger": stagger,
                "apex": apex,
                "landed": False,
                "cur_wx": start_wx,
                "cur_wy": start_wy,
                "cur_wz": self.start_wz,
                "prev_wx": start_wx,
                "prev_wy": start_wy,
                "prev_wz": self.start_wz,
            })

    def update(self, dt: float, game_map=None, particles: list = None, camera=None, fighters: list = None) -> bool:
        if not self.is_active:
            return False

        self.elapsed += dt

        # Atualiza a posição de cada flecha ao longo de sua trajetória parabólica em arco
        all_landed = True
        for a in self.arrows:
            effective_time = self.elapsed - a["stagger"]
            if effective_time < 0.0:
                all_landed = False
                continue
            progress = min(1.0, effective_time / self.flight_duration)
            if progress < 1.0:
                all_landed = False
                a["prev_wx"] = a["cur_wx"]
                a["prev_wy"] = a["cur_wy"]
                a["prev_wz"] = a["cur_wz"]
                # Interpolação no plano horizontal
                a["cur_wx"] = self.start_wx + (a["dest_x"] - self.start_wx) * progress
                a["cur_wy"] = self.start_wy + (a["dest_y"] - self.start_wy) * progress
                # Altura parabólica em arco
                a["cur_wz"] = self.start_wz * (1.0 - progress) + a["apex"] * 4.0 * progress * (1.0 - progress)

                # Rastro cintilante sagrado de kami durante o voo
                if particles is not None and random.random() < 0.45:
                    particles.append(SparkParticle(a["cur_wx"], a["cur_wy"], a["cur_wz"], color=(255, 235, 110)))
            else:
                if not a["landed"]:
                    a["landed"] = True
                    a["cur_wx"] = a["dest_x"]
                    a["cur_wy"] = a["dest_y"]
                    a["cur_wz"] = 0.0
                    # Partículas ao cravar no solo
                    if particles is not None:
                        for _ in range(3):
                            particles.append(SparkParticle(a["dest_x"], a["dest_y"], 0.25, color=(255, 240, 150)))

        # Impacto da salva na área quando as primeiras flechas tocam o solo
        if not self.has_impacted and (self.elapsed >= self.flight_duration or all_landed):
            self.has_impacted = True
            if camera and hasattr(camera, "add_shake"):
                camera.add_shake(12.0)
            if particles is not None:
                for _ in range(24):
                    particles.append(FlameVoxelParticle(self.target_wx, self.target_wy, wz=0.15))
                for _ in range(18):
                    particles.append(SparkParticle(self.target_wx, self.target_wy, 0.45, color=(255, 220, 80)))
                for _ in range(12):
                    particles.append(SparkParticle(self.target_wx, self.target_wy, 0.55, color=(255, 255, 240)))

            if game_map:
                for b in getattr(game_map, "bamboos", []):
                    if not getattr(b, "is_cut", False) and world_distance(self.target_wx, self.target_wy, b.wx, b.wy) < (self.radius + 0.5):
                        slice_part = b.cut((1.0, 0.0))
                        if slice_part and particles is not None:
                            particles.append(slice_part)
                for r in getattr(game_map, "rocks", []):
                    if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                        if world_distance(self.target_wx, self.target_wy, r.wx, r.wy) < (self.radius + 0.65):
                            r.break_panel((1.0, 0.0), particles)

            # Aplica dano letal (2 HP) se fighters fornecidos diretamente
            if fighters and not self.damage_dealt:
                self.damage_dealt = True
                for f in fighters:
                    if getattr(f, "is_alive", False) and f is not self.owner:
                        dist = math.hypot(f.wx - self.target_wx, f.wy - self.target_wy)
                        if dist < (self.radius + getattr(f, "radius", 0.35)):
                            f.take_hit((0.0, 0.0), damage=self.damage)

        if self.has_impacted:
            self.impact_flash_timer -= dt

        if self.elapsed >= self.total_duration:
            self.is_active = False
            return False

        return self.is_active

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        # 1. Selo sagrado e sombra no solo da área de impacto
        cx, cy = camera.apply(self.target_wx, self.target_wy, 0.0)
        rx = int(self.radius * 24)
        ry = max(8, rx // 2)

        # Círculo sagrado translúcido no piso sob a mira durante o voo
        if not self.has_impacted:
            progress = min(1.0, self.elapsed / self.flight_duration)
            aura_surf = pygame.Surface((rx * 2 + 16, ry * 2 + 16), pygame.SRCALPHA)
            alpha = int(40 + 50 * progress)
            pygame.draw.ellipse(aura_surf, (255, 220, 80, alpha), (8, 8, rx * 2, ry * 2))
            pygame.draw.ellipse(aura_surf, (255, 240, 180, alpha + 30), (8, 8, rx * 2, ry * 2), 2)
            surface.blit(aura_surf, (cx - rx - 8, cy - ry - 8))
        else:
            # Clarão de impacto inicial e anel de purificação xintoísta expandindo
            progress = max(0.0, min(1.0, 1.0 - (self.impact_flash_timer / 0.35)))
            exp_w = int(self.radius * 32 * (0.8 + 0.4 * progress))
            exp_h = max(2, exp_w // 2)
            alpha_val = max(0, min(255, int((1.0 - progress) * 220)))
            exp_surf = pygame.Surface((exp_w * 2 + 16, exp_h * 2 + 16), pygame.SRCALPHA)
            pygame.draw.ellipse(exp_surf, (255, 230, 80, alpha_val), (8, 8, exp_w * 2, exp_h * 2))
            pygame.draw.ellipse(exp_surf, (255, 255, 240, min(255, alpha_val + 35)), (8 + exp_w // 4, 8 + exp_h // 4, int(exp_w * 1.5), int(exp_h * 1.5)))
            surface.blit(exp_surf, (cx - exp_w - 8, cy - exp_h - 8))

        # 2. Renderização de cada flecha sagrada individual
        for a in self.arrows:
            if self.elapsed < a["stagger"]:
                continue

            wx, wy, wz = a["cur_wx"], a["cur_wy"], a["cur_wz"]

            if not a["landed"]:
                # Sombra no solo correspondente à flecha em voo
                sx_g, sy_g = camera.apply(wx, wy, 0.0)
                sh_progress = max(0.1, 1.0 - (wz / 6.0))
                sh_r = max(2, int(5 * sh_progress))
                pygame.draw.ellipse(surface, (10, 10, 12, int(140 * sh_progress)), (sx_g - sh_r, sy_g - sh_r // 2, sh_r * 2, sh_r))

                # Posição da flecha na tela
                sx, sy = camera.apply(wx, wy, wz)
                # Vetor de movimento para orientação realista da ponta
                dx = a["cur_wx"] - a["prev_wx"]
                dy = a["cur_wy"] - a["prev_wy"]
                dz = a["cur_wz"] - a["prev_wz"]
                mag = math.hypot(dx, dy, dz)
                if mag > 0.001:
                    dir_x, dir_y, dir_z = dx / mag, dy / mag, dz / mag
                else:
                    dir_x, dir_y, dir_z = 0.0, 0.0, -1.0

                sx_tail, sy_tail = camera.apply(wx - dir_x * 0.35, wy - dir_y * 0.35, wz - dir_z * 0.35)

                # Haste branca sagrada
                pygame.draw.line(surface, (250, 248, 240), (int(sx_tail), int(sy_tail)), (int(sx), int(sy)), 2)
                # Ponta dourada de purificação
                pygame.draw.circle(surface, COLOR_GOLD, (int(sx), int(sy)), 3)
                # Brilho sagrado
                pygame.draw.circle(surface, (255, 255, 230), (int(sx), int(sy)), 1)
                # Penas cerimoniais douradas na cauda
                pygame.draw.circle(surface, (255, 230, 120), (int(sx_tail), int(sy_tail)), 2)
            else:
                # Flecha cravada no solo
                sx_tip, sy_tip = camera.apply(a["dest_x"], a["dest_y"], 0.0)
                sx_tail, sy_tail = camera.apply(a["dest_x"] - 0.15, a["dest_y"] - 0.15, 0.40)
                # Haste no chão
                pygame.draw.line(surface, (240, 235, 220), (int(sx_tail), int(sy_tail)), (int(sx_tip), int(sy_tip)), 2)
                # Ponta de ouro fincada
                pygame.draw.circle(surface, COLOR_GOLD, (int(sx_tip), int(sy_tip)), 2)
                # Penas sagradas
                pygame.draw.circle(surface, (255, 225, 110), (int(sx_tail), int(sy_tail)), 2)


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
                for r in getattr(game_map, "rocks", []):
                    if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                        if world_distance(self.wx, self.wy, r.wx, r.wy) < (getattr(r, "radius", 0.5) + 0.2):
                            r.break_panel((self.dir_x, self.dir_y), particles)
                            hit = True
                            break
                    elif not getattr(r, "is_broken", False) and world_distance(self.wx, self.wy, r.wx, r.wy) < r.radius + 0.2:
                        hit = True
                        break
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
                # A corda leva a arqueira por cima de buracos; ao soltar, o pouso decide (ver Samurai.update_pit)
                self.owner.pit_cross_timer = 0.10
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
        self.has_been_reflected = False  # Anti-spam: previne reflexão infinita

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
                if game_map:
                    for b in getattr(game_map, "bamboos", []):
                        if not getattr(b, "is_cut", False) and world_distance(self.wx, self.wy, b.wx, b.wy) < (self.radius + 0.6):
                            part = b.cut((1.0, 0.0))
                            if part and particles is not None:
                                particles.append(part)
                    for r in getattr(game_map, "rocks", []):
                        if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                            if world_distance(self.wx, self.wy, r.wx, r.wy) < (self.radius + 0.8):
                                r.break_panel((1.0, 0.0), particles)
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


class MusashiWaveProjectile:
    """Onda azul semi-transparente disparada pelo Musashi no terceiro ataque.
    Projétil horizontal que causa 2 de dano ao atingir um oponente."""
    
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.owner = owner
        self.dir_x = dir_x
        self.dir_y = dir_y
        
        # Velocidade da onda
        speed = 14.0
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        
        # Propriedades da onda
        self.width = 1.5  # 1.5 tiles de largura
        self.max_range = 6.5
        self.dist_traveled = 0.0
        self.is_active = True
        self.damage = 2
        self.has_been_reflected = False
        
        # Animação de onda (pulsação visual)
        self.pulse_timer = 0.0
        
    def update(self, dt: float, game_map, particles: list) -> bool:
        """Atualiza a posição da onda. Retorna False se deve ser removida."""
        if not self.is_active:
            return False
        
        # Movimento
        step = math.hypot(self.vx * dt, self.vy * dt)
        self.wx += self.vx * dt
        self.wy += self.vy * dt
        self.dist_traveled += step
        
        # Pulsação visual
        self.pulse_timer += dt
        
        # Limites da arena [1.2, cols-1.2]
        min_bound = 1.2
        max_bound_x = (game_map.cols - 1.2) if (game_map and hasattr(game_map, "cols")) else 19.8
        max_bound_y = (game_map.rows - 1.2) if (game_map and hasattr(game_map, "rows")) else 19.8
        
        hit_bound = False
        if self.wx <= min_bound or self.wx >= max_bound_x or self.wy <= min_bound or self.wy >= max_bound_y:
            self.is_active = False
            return False
        
        # Corte de bambus no caminho
        for b in game_map.bamboos:
            if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.6:
                part = b.cut((self.dir_x, self.dir_y))
                if part:
                    particles.append(part)
        
        # Colisão com rochas ou poço
        hit_obstacle = False
        for r in getattr(game_map, "rocks", []):
            if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                if world_distance(self.wx, self.wy, r.wx, r.wy) < 0.65:
                    r.break_panel((self.dir_x, self.dir_y), particles)
            elif not getattr(r, "is_broken", False) and world_distance(self.wx, self.wy, r.wx, r.wy) < getattr(r, "radius", 0.6):
                hit_obstacle = True
                break
        if game_map and getattr(game_map, "well", None) and world_distance(self.wx, self.wy, game_map.well.wx, game_map.well.wy) < game_map.well.radius:
            hit_obstacle = True
        
        if hit_obstacle or self.dist_traveled >= self.max_range:
            self.is_active = False
            return False
        
        return True
    
    def render(self, surface: pygame.Surface, camera):
        """Renderiza a onda azul semi-transparente."""
        if not self.is_active:
            return
        
        # Posição isométrica
        sx, sy = camera.apply(self.wx, self.wy, self.wz)
        
        # Pulsação visual (cresce e diminui)
        pulse = 0.8 + 0.3 * math.sin(self.pulse_timer * 12.0)
        
        # Largura e altura da onda
        wave_w = int(self.width * 20 * pulse)
        wave_h = int(8 * pulse)
        
        # Criar superfície com canal alfa para semi-transparência
        wave_surf = pygame.Surface((wave_w, wave_h), pygame.SRCALPHA)
        
        # Cor azul com alpha semi-transparente
        alpha = int(150 * pulse)
        blue_wave = (*COLOR_BLUE_AURA, alpha)
        
        # Desenhar onda como elipse horizontal
        pygame.draw.ellipse(wave_surf, blue_wave, (0, 0, wave_w, wave_h))
        
        # Brilho central (mais opaco)
        bright_alpha = int(200 * pulse)
        bright_blue = (min(255, COLOR_BLUE_AURA[0] + 50), 
                      min(255, COLOR_BLUE_AURA[1] + 50), 
                      min(255, COLOR_BLUE_AURA[2]), 
                      bright_alpha)
        pygame.draw.ellipse(wave_surf, bright_blue, 
                           (wave_w // 4, wave_h // 3, wave_w // 2, wave_h // 3))
        
        # Blit no surface principal
        surface.blit(wave_surf, (sx - wave_w // 2, sy - wave_h // 2))


class NaginataProjectile:
    """Naginata arremessada por Benkei.
    Projétil pesado e maciço que penetra oponentes.
    Ao parar ou atingir um obstáculo, crava-se no chão.
    Garante que nunca caia em buracos ou água (clamp de terreno firme)."""

    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner, max_range: float = 7.5):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.owner = owner
        self.original_owner = owner
        self.dir_x = dir_x
        self.dir_y = dir_y

        speed = 15.5
        self.vx = dir_x * speed
        self.vy = dir_y * speed
        self.vz = 0.0

        self.state = "FLYING"  # "FLYING" ou "ON_GROUND"
        self.max_range = max_range
        self.dist_traveled = 0.0
        self.is_active = True
        self.pickup_delay = 0.20
        self.damage = 2
        self.pulse_timer = 0.0
        self.has_hit_fighter = False

    def update(self, dt: float, game_map, particles: list) -> bool:
        if not self.is_active:
            return False

        self.pulse_timer += dt

        if self.state == "FLYING":
            step = math.hypot(self.vx * dt, self.vy * dt)
            self.wx += self.vx * dt
            self.wy += self.vy * dt
            self.dist_traveled += step

            # Partículas de velocidade de arremesso pesado
            if particles is not None and random.random() < 0.6:
                particles.append(SparkParticle(self.wx, self.wy, 0.15))

            # Limites da arena
            min_bound = 1.2
            max_bound_x = (game_map.cols - 1.2) if (game_map and hasattr(game_map, "cols")) else 19.8
            max_bound_y = (game_map.rows - 1.2) if (game_map and hasattr(game_map, "rows")) else 19.8

            hit_bound = False
            if self.wx <= min_bound or self.wx >= max_bound_x or self.wy <= min_bound or self.wy >= max_bound_y:
                self.wx = max(min_bound, min(max_bound_x, self.wx))
                self.wy = max(min_bound, min(max_bound_y, self.wy))
                hit_bound = True

            # Colisão com rochas ou construções
            hit_obstacle = False
            if hasattr(game_map, "rocks"):
                for r in game_map.rocks:
                    if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                        if world_distance(self.wx, self.wy, r.wx, r.wy) < 0.65:
                            r.break_panel((self.dir_x, self.dir_y), particles)
                    elif not getattr(r, "is_broken", False) and world_distance(self.wx, self.wy, r.wx, r.wy) < getattr(r, "radius", 0.6):
                        hit_obstacle = True
                        break
            if hasattr(game_map, "buildings"):
                for b in game_map.buildings:
                    c, _, _ = b.check_collision(self.wx, self.wy, 0.25)
                    if c:
                        hit_obstacle = True
                        break

            # Cortar bambus
            if hasattr(game_map, "bamboos"):
                for b in game_map.bamboos:
                    if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.55:
                        b.cut((self.dir_x, self.dir_y))
                        if particles is not None:
                            for _ in range(4):
                                particles.append(SparkParticle(b.wx, b.wy, 0.2))

            if hit_bound or hit_obstacle or self.dist_traveled >= self.max_range:
                self._embed_into_ground(game_map, particles)
        else:
            # ON_GROUND: Espera apenas o Benkei recuperar
            if self.pickup_delay > 0:
                self.pickup_delay -= dt
            else:
                # Checar se Benkei (dono legítimo da Naginata) está sobre a arma
                legit_owner = getattr(self, "original_owner", self.owner)
                if legit_owner and getattr(legit_owner, "is_alive", True) and hasattr(legit_owner, "recover_naginata"):
                    d = world_distance(self.wx, self.wy, legit_owner.wx, legit_owner.wy)
                    if d < 0.65:
                        legit_owner.recover_naginata()
                        self.is_active = False
                        if particles is not None:
                            for _ in range(6):
                                particles.append(SparkParticle(self.wx, self.wy, 0.25))
                        return False

        return self.is_active

    def _embed_into_ground(self, game_map, particles):
        """Crava a naginata no solo, garantindo que retroceda caso atinja buracos ou água."""
        self.state = "ON_GROUND"
        self.vx = 0.0
        self.vy = 0.0
        self.wz = 0.0

        # Clamp de segurança absoluta contra buracos (Pits) e água
        curr_x, curr_y = self.wx, self.wy
        step_back_x = -self.dir_x * 0.25
        step_back_y = -self.dir_y * 0.25

        for _ in range(24):
            is_unsafe = False
            if hasattr(game_map, "pit_zones"):
                for pz in game_map.pit_zones:
                    if pz.contains(curr_x, curr_y):
                        is_unsafe = True
                        break
            if hasattr(game_map, "pit_at") and game_map.pit_at(curr_x, curr_y) is not None:
                is_unsafe = True
            if hasattr(game_map, "is_pit") and game_map.is_pit(curr_x, curr_y):
                is_unsafe = True
            if hasattr(game_map, "get_tile_kind"):
                kind = game_map.get_tile_kind(int(curr_x), int(curr_y))
                if kind in ("water", "pit", "void"):
                    is_unsafe = True

            if not is_unsafe:
                self.wx, self.wy = curr_x, curr_y
                break
            curr_x += step_back_x
            curr_y += step_back_y

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.3))

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        from src.isometric.voxel_renderer import draw_oriented_voxel_box, draw_voxel_box

        if self.state == "FLYING":
            # Naginata em voo supersônico
            draw_oriented_voxel_box(
                surface, camera,
                self.wx, self.wy, max(0.2, self.wz + 0.35),
                self.dir_x, self.dir_y, 0.05,
                length=1.65, width=0.06, height=0.06,
                color=(36, 26, 20), outline=True
            )
            # Lâmina na ponta
            tip_x = self.wx + self.dir_x * 1.10
            tip_y = self.wy + self.dir_y * 1.10
            draw_oriented_voxel_box(
                surface, camera,
                tip_x, tip_y, max(0.2, self.wz + 0.35),
                self.dir_x, self.dir_y, 0.05,
                length=0.55, width=0.07, height=0.08,
                color=COLOR_STEEL, outline=True
            )
        else:
            # ON_GROUND: Cravada vertical/diagonal no solo com baliza dourada
            sx_g, sy_g = camera.apply(self.wx, self.wy, 0.0)
            pulse = 0.85 + 0.15 * math.sin(self.pulse_timer * 8.0)
            beacon_r = int(18 * pulse)

            beacon_surf = pygame.Surface((beacon_r * 2, beacon_r), pygame.SRCALPHA)
            pygame.draw.ellipse(beacon_surf, (220, 175, 50, 110), (0, 0, beacon_r * 2, beacon_r))
            pygame.draw.ellipse(beacon_surf, (255, 230, 120, 190), (0, 0, beacon_r * 2, beacon_r), 2)
            surface.blit(beacon_surf, (sx_g - beacon_r, sy_g - beacon_r // 2))

            # Haste cravada
            draw_oriented_voxel_box(
                surface, camera,
                self.wx, self.wy, 0.0,
                self.dir_x * 0.15, self.dir_y * 0.15, 0.95,
                length=1.40, width=0.065, height=0.065,
                color=(36, 26, 20), outline=True
            )
            # Tsuba e lâmina no topo
            blade_base_z = 0.85
            draw_voxel_box(
                surface, camera,
                self.wx - 0.04, self.wy - 0.04, blade_base_z,
                0.08, 0.08, 0.03, COLOR_GOLD, outline=False
            )
            draw_oriented_voxel_box(
                surface, camera,
                self.wx + self.dir_x * 0.12, self.wy + self.dir_y * 0.12, blade_base_z + 0.02,
                self.dir_x * 0.20, self.dir_y * 0.20, 0.90,
                length=0.48, width=0.065, height=0.08,
                color=COLOR_STEEL, outline=True
            )


class KamaitachiProjectile:
    """Lâmina acústica de vácuo disparada pelo Shamisen da O-Rin.
    Onda cortante em crescente de alta velocidade e alcance 6.0 tiles."""

    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner, max_range: float = 6.2):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.owner = owner
        self.dir_x = dir_x
        self.dir_y = dir_y

        speed = 17.5
        self.vx = dir_x * speed
        self.vy = dir_y * speed

        self.max_range = max_range
        self.dist_traveled = 0.0
        self.is_active = True
        self.damage = 1
        self.width = 1.3
        self.pulse_timer = 0.0
        self.has_been_reflected = False

    def update(self, dt: float, game_map, particles: list) -> bool:
        if not self.is_active:
            return False

        self.pulse_timer += dt
        step = math.hypot(self.vx * dt, self.vy * dt)
        self.wx += self.vx * dt
        self.wy += self.vy * dt
        self.dist_traveled += step

        # Partículas de vácuo sônico ciano
        if particles is not None and random.random() < 0.5:
            from src.effects.particles import SparkParticle
            particles.append(SparkParticle(self.wx, self.wy, 0.2))

        # Limites da arena
        min_bound = 1.2
        max_bound_x = (game_map.cols - 1.2) if (game_map and hasattr(game_map, "cols")) else 19.8
        max_bound_y = (game_map.rows - 1.2) if (game_map and hasattr(game_map, "rows")) else 19.8

        if self.wx <= min_bound or self.wx >= max_bound_x or self.wy <= min_bound or self.wy >= max_bound_y:
            self.is_active = False
            return False

        # Cortar bambus e colidir com rochas
        if hasattr(game_map, "bamboos"):
            for b in game_map.bamboos:
                if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.55:
                    b.cut((self.dir_x, self.dir_y))
        if hasattr(game_map, "rocks"):
            for r in game_map.rocks:
                if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                    if world_distance(self.wx, self.wy, r.wx, r.wy) < 0.65:
                        r.break_panel((self.dir_x, self.dir_y), particles)
                elif not getattr(r, "is_broken", False) and world_distance(self.wx, self.wy, r.wx, r.wy) < getattr(r, "radius", 0.6):
                    self.is_active = False
                    return False

        if self.dist_traveled >= self.max_range:
            self.is_active = False
            return False

        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        sx, sy = camera.apply(self.wx, self.wy, self.wz + 0.35)
        pulse = 0.90 + 0.20 * math.sin(self.pulse_timer * 16.0)
        w = int(self.width * 22 * pulse)
        h = int(14 * pulse)

        wave_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Onda em crescente ciano esbranquiçado
        pygame.draw.ellipse(wave_surf, (80, 220, 245, 185), (0, 0, w, h))
        pygame.draw.ellipse(wave_surf, (220, 255, 255, 240), (w // 4, h // 4, w // 2, h // 2))

        # Rotacionar no ângulo do vetor de disparo
        ang_deg = -math.degrees(math.atan2(self.dir_y, self.dir_x)) - 45
        rot_surf = pygame.transform.rotate(wave_surf, ang_deg)
        rw, rh = rot_surf.get_size()
        surface.blit(rot_surf, (sx - rw // 2, sy - rh // 2))


class AcousticResonanceWave:
    """Onda de Choque Ressonante 360° da O-Rin.
    Expande radialmente, repele oponentes e desvia projéteis leves."""

    def __init__(self, wx: float, wy: float, owner, max_radius: float = 2.8, duration: float = 0.32):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.owner = owner
        self.radius = 0.25
        self.max_radius = max_radius
        self.duration = duration
        self.timer = 0.0
        self.is_active = True
        self.pushed_fighters = set()

    def update(self, dt: float, projectiles: list, fighters: list = None, game_map = None) -> bool:
        if not self.is_active:
            return False

        self.timer += dt
        prog = min(1.0, self.timer / self.duration)
        self.radius = 0.25 + (self.max_radius - 0.25) * prog

        # 1. Desviar projéteis leves
        if projectiles:
            for p in projectiles:
                if getattr(p, "is_active", False) and getattr(p, "owner", None) is not self.owner:
                    dist = world_distance(self.wx, self.wy, getattr(p, "wx", 0.0), getattr(p, "wy", 0.0))
                    if dist <= self.radius + 0.35:
                        # Desviar projétil
                        if not getattr(p, "has_been_reflected", False):
                            p.has_been_reflected = True
                            p.owner = self.owner
                            if hasattr(p, "vx") and hasattr(p, "vy"):
                                p.vx = -p.vx * 1.15
                                p.vy = -p.vy * 1.15

        # 2. Empurrão cinético nos oponentes
        if fighters and game_map:
            for f in fighters:
                if f is not self.owner and getattr(f, "is_alive", True) and id(f) not in self.pushed_fighters:
                    dist = world_distance(self.wx, self.wy, f.wx, f.wy)
                    if dist <= self.radius + getattr(f, "radius", 0.35):
                        self.pushed_fighters.add(id(f))
                        dx = f.wx - self.wx
                        dy = f.wy - self.wy
                        dnorm = math.hypot(dx, dy)
                        if dnorm > 0.01:
                            dx /= dnorm
                            dy /= dnorm
                        else:
                            dx, dy = 1.0, 0.0
                        f.apply_forced_displacement(dx * 1.10, dy * 1.10, game_map)
                        # Interrupção de whiff
                        if getattr(f, "state", "") == "ATTACK":
                            f.stun(0.25)

        # 3. Quebrar biombos e cortar bambus na expansão acústica
        if game_map:
            for b in getattr(game_map, "bamboos", []):
                if not getattr(b, "is_cut", False) and world_distance(self.wx, self.wy, b.wx, b.wy) <= self.radius + 0.2:
                    b.cut((1.0, 0.0))
            for r in getattr(game_map, "rocks", []):
                if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                    if world_distance(self.wx, self.wy, r.wx, r.wy) <= self.radius + 0.35:
                        r.break_panel((1.0, 0.0), None)

        if self.timer >= self.duration:
            self.is_active = False
            return False

        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        sx, sy = camera.apply(self.wx, self.wy, 0.0)
        prog = min(1.0, self.timer / self.duration)
        r_px = int(self.radius * 32)
        alpha = int((1.0 - prog) * 210)

        ring_surf = pygame.Surface((r_px * 2 + 10, r_px + 10), pygame.SRCALPHA)
        # Anel ressonante magenta floral
        pygame.draw.ellipse(ring_surf, (235, 75, 120, alpha // 2), (5, 5, r_px * 2, r_px))
        pygame.draw.ellipse(ring_surf, (255, 185, 210, alpha), (5, 5, r_px * 2, r_px), 3)
        surface.blit(ring_surf, (sx - r_px - 5, sy - r_px // 2 - 5))


class SpiralResonanceProjectile:
    """Onda Sônica Espiralada (Acorde de Ressonância Mortal da O-Rin).
    Disparada em trios separados por 120°, avança em trajetória espiral curvada com velocidade angular,
    expandindo o raio e causando corte acústico letal."""

    def __init__(self, wx: float, wy: float, wz: float, initial_angle: float, owner,
                 curve_direction: float = 1.0, speed: float = 11.5, angular_speed: float = 2.2,
                 max_range: float = 7.0):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.owner = owner
        self.original_owner = owner
        self.current_angle = initial_angle
        self.curve_direction = curve_direction
        self.speed = speed
        self.angular_speed = angular_speed
        self.dir_x = math.cos(initial_angle)
        self.dir_y = math.sin(initial_angle)
        self.vx = self.dir_x * speed
        self.vy = self.dir_y * speed

        self.max_range = max_range
        self.dist_traveled = 0.0
        self.is_active = True
        self.damage = 2
        self.width = 1.45
        self.pulse_timer = 0.0
        self.has_been_reflected = False

    def update(self, dt: float, game_map, particles: list) -> bool:
        if not self.is_active:
            return False

        self.pulse_timer += dt
        if not self.has_been_reflected:
            self.current_angle += self.curve_direction * self.angular_speed * dt
            self.dir_x = math.cos(self.current_angle)
            self.dir_y = math.sin(self.current_angle)
            self.vx = self.dir_x * self.speed
            self.vy = self.dir_y * self.speed

        step = math.hypot(self.vx * dt, self.vy * dt)
        self.wx += self.vx * dt
        self.wy += self.vy * dt
        self.dist_traveled += step

        # Partículas de ressonância floral/magenta
        if particles is not None and random.random() < 0.55:
            from src.effects.particles import SparkParticle
            particles.append(SparkParticle(self.wx, self.wy, 0.25, color=(255, 100, 150)))

        # Limites da arena
        min_bound = 1.2
        max_bound_x = (game_map.cols - 1.2) if (game_map and hasattr(game_map, "cols")) else 19.8
        max_bound_y = (game_map.rows - 1.2) if (game_map and hasattr(game_map, "rows")) else 19.8

        if self.wx <= min_bound or self.wx >= max_bound_x or self.wy <= min_bound or self.wy >= max_bound_y:
            self.is_active = False
            return False

        # Cortar bambus e biombos
        if hasattr(game_map, "bamboos"):
            for b in game_map.bamboos:
                if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.6:
                    b.cut((self.dir_x, self.dir_y))
        if hasattr(game_map, "rocks"):
            for r in game_map.rocks:
                if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                    if world_distance(self.wx, self.wy, r.wx, r.wy) < 0.70:
                        r.break_panel((self.dir_x, self.dir_y), particles)
                elif not getattr(r, "is_broken", False) and world_distance(self.wx, self.wy, r.wx, r.wy) < getattr(r, "radius", 0.6):
                    self.is_active = False
                    return False

        if self.dist_traveled >= self.max_range:
            self.is_active = False
            return False

        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        sx, sy = camera.apply(self.wx, self.wy, self.wz + 0.35)
        pulse = 0.90 + 0.22 * math.sin(self.pulse_timer * 18.0)
        w = int(self.width * 24 * pulse)
        h = int(16 * pulse)

        wave_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(wave_surf, (235, 75, 140, 200), (0, 0, w, h))
        pygame.draw.ellipse(wave_surf, (255, 210, 230, 240), (w // 5, h // 5, 3 * w // 5, 3 * h // 5))
        pygame.draw.arc(wave_surf, (255, 230, 140, 230), (2, 2, w - 4, h - 4), 0, math.pi, 2)

        ang_deg = -math.degrees(math.atan2(self.dir_y, self.dir_x)) - 45
        rot_surf = pygame.transform.rotate(wave_surf, ang_deg)
        rw, rh = rot_surf.get_size()
        surface.blit(rot_surf, (sx - rw // 2, sy - rh // 2))


class EarthStompShockwave:
    """Onda de Choque Sísmica Frontal em 120 Graus (Pisotão Sísmico do Goro).
    Arrasta-se pela terra em um arco frontal de 120° num curto alcance (2 voxels de piso),
    levantando fisicamente os voxels de terra do piso em cristas de pedra e poeira,
    desestabilizando e atordoando (STUN) os oponentes apanhados no cone de impacto."""

    def __init__(self, wx: float, wy: float, owner, facing: tuple[float, float] = (1.0, 0.0), max_radius: float = 4.2, duration: float = 0.30):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.owner = owner
        fx, fy = facing if facing != (0.0, 0.0) else (getattr(owner, "facing_x", 1.0), getattr(owner, "facing_y", 0.0))
        f_norm = math.hypot(fx, fy) or 1.0
        self.facing_x = fx / f_norm
        self.facing_y = fy / f_norm
        self.radius = 0.30
        self.max_radius = max_radius
        self.duration = duration
        self.timer = 0.0
        self.is_active = True
        self.hit_fighters = set()

    def update(self, dt: float, *args, **kwargs) -> bool:
        if not self.is_active:
            return False

        game_map = kwargs.get("game_map")
        particles = kwargs.get("particles")
        fighters = kwargs.get("fighters")
        projectiles = kwargs.get("projectiles")

        for a in args:
            if hasattr(a, "cols") or hasattr(a, "rows"):
                game_map = a
            elif isinstance(a, list):
                if a and hasattr(a[0], "is_alive"):
                    fighters = a
                elif a and hasattr(a[0], "lifetime"):
                    particles = a
                elif a and (hasattr(a[0], "dir_x") or hasattr(a[0], "vx") or hasattr(a[0], "is_active")):
                    projectiles = a

        is_sub_update = (fighters is None and not any(isinstance(a, list) and a and hasattr(a[0], "is_alive") for a in args))
        if not is_sub_update or not getattr(self.owner, "active_shockwaves", None) or self not in self.owner.active_shockwaves:
            self.timer += dt
        prog = min(1.0, self.timer / self.duration)
        self.radius = 0.30 + (self.max_radius - 0.30) * prog

        # Spawna partículas de terra e cascalho no arco frontal enquanto avança
        if particles is not None and random.random() < 0.65:
            base_ang = math.atan2(self.facing_y, self.facing_x)
            rnd_offset = random.uniform(-math.pi / 3.0, math.pi / 3.0)
            ang = base_ang + rnd_offset
            px = self.wx + math.cos(ang) * self.radius
            py = self.wy + math.sin(ang) * self.radius
            particles.append(SparkParticle(px, py, random.uniform(0.15, 0.45), color=random.choice([(140, 105, 65), (175, 135, 85), (95, 70, 45)])))

        # Apagar / dissipar projéteis inimigos na área de impacto sísmico (cone frontal de 120°)
        if projectiles:
            for p in projectiles:
                if p is not self and getattr(p, "is_active", False) and getattr(p, "owner", None) != self.owner:
                    p_wx = getattr(p, "wx", None)
                    p_wy = getattr(p, "wy", None)
                    if p_wx is not None and p_wy is not None:
                        dist_p = world_distance(self.wx, self.wy, p_wx, p_wy)
                        if dist_p <= self.radius + 0.45:
                            dx_p = p_wx - self.wx
                            dy_p = p_wy - self.wy
                            dnorm_p = math.hypot(dx_p, dy_p)
                            if dnorm_p > 0.01:
                                ndx_p, ndy_p = dx_p / dnorm_p, dy_p / dnorm_p
                            else:
                                ndx_p, ndy_p = self.facing_x, self.facing_y
                            if ndx_p * self.facing_x + ndy_p * self.facing_y >= 0.40:
                                p.is_active = False
                                if particles is not None:
                                    for _ in range(8):
                                        particles.append(SparkParticle(p_wx, p_wy, 0.30, color=(245, 215, 110)))
                                    for _ in range(5):
                                        particles.append(SparkParticle(p_wx, p_wy, 0.20, color=(140, 105, 65)))

        # Desestabilização e Stun nos oponentes dentro do cone frontal de 120°
        if fighters and game_map:
            for f in fighters:
                if f is not self.owner and getattr(f, "is_alive", True) and id(f) not in self.hit_fighters:
                    dist = world_distance(self.wx, self.wy, f.wx, f.wy)
                    if dist <= self.radius + getattr(f, "radius", 0.35):
                        dx = f.wx - self.wx
                        dy = f.wy - self.wy
                        dnorm = math.hypot(dx, dy)
                        if dnorm > 0.01:
                            ndx, ndy = dx / dnorm, dy / dnorm
                        else:
                            ndx, ndy = self.facing_x, self.facing_y

                        # Checar se está dentro do leque frontal de 120° (cos(60°) = 0.5)
                        dot = ndx * self.facing_x + ndy * self.facing_y
                        if dot >= 0.45:
                            self.hit_fighters.add(id(f))
                            # Tremor sísmico sob os pés com solavanco
                            f.apply_forced_displacement(ndx * 0.45, ndy * 0.45, game_map)
                            # Aplica 1 de dano direto do impacto da terra e das rochas
                            f.take_hit((ndx, ndy), damage=1)
                            # Aplica atordoamento (STUN) de 0.9s se ainda estiver vivo
                            if getattr(f, "is_alive", True):
                                f.stun(0.90)
                            if particles is not None:
                                for _ in range(12):
                                    particles.append(SparkParticle(f.wx, f.wy, 0.35, color=(185, 145, 95)))

        # Quebrar biombos e cortar bambus com a onda de choque no cone frontal
        if game_map:
            for b in getattr(game_map, "bamboos", []):
                if not getattr(b, "is_cut", False) and world_distance(self.wx, self.wy, b.wx, b.wy) <= self.radius + 0.2:
                    dx, dy = b.wx - self.wx, b.wy - self.wy
                    dnorm = math.hypot(dx, dy) or 1.0
                    if (dx / dnorm) * self.facing_x + (dy / dnorm) * self.facing_y >= 0.45:
                        part = b.cut((self.facing_x, self.facing_y))
                        if part and particles is not None:
                            particles.append(part)
            for r in getattr(game_map, "rocks", []):
                if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                    if world_distance(self.wx, self.wy, r.wx, r.wy) <= self.radius + 0.35:
                        dx, dy = r.wx - self.wx, r.wy - self.wy
                        dnorm = math.hypot(dx, dy) or 1.0
                        if (dx / dnorm) * self.facing_x + (dy / dnorm) * self.facing_y >= 0.45:
                            r.break_panel((self.facing_x, self.facing_y), particles)

        if self.timer >= self.duration:
            self.is_active = False
            return False

        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        from src.isometric.voxel_renderer import draw_voxel_box

        prog = min(1.0, self.timer / self.duration)
        base_ang = math.atan2(self.facing_y, self.facing_x)

        # Altura do solo levantado pela onda telúrica (sobe e se assenta)
        lift_peak = math.sin(prog * math.pi) * 0.36
        earth_colors = [
            (115, 85, 55),
            (145, 110, 75),
            (85, 60, 40),
            (160, 125, 85),
            (100, 75, 50),
        ]

        # Desenhar 7 colunas de blocos de voxels do piso levantados ao longo do arco frontal de 120 graus (-60° a +60°)
        offsets_deg = [-55, -36, -18, 0, 18, 36, 55]
        front_points = []
        for i, deg in enumerate(offsets_deg):
            ang = base_ang + math.radians(deg)
            # Fator de elevação maior no centro do leque
            center_fact = math.cos(math.radians(deg))
            cur_lift = lift_peak * (0.55 + 0.45 * center_fact)

            r_front = self.radius
            bx = self.wx + math.cos(ang) * r_front
            by = self.wy + math.sin(ang) * r_front
            col = earth_colors[i % len(earth_colors)]

            # Voxel cúbico de terra levantado do piso
            box_sz = 0.22
            box_h = 0.14 + cur_lift * 0.6
            draw_voxel_box(surface, camera, bx - box_sz * 0.5, by - box_sz * 0.5, cur_lift * 0.5, box_sz, box_sz, box_h, col, outline=True)

            # Ponto em tela para traçar a fissura de solo na crista
            sx, sy = camera.apply(bx, by, cur_lift * 0.4)
            front_points.append((sx, sy))

            # Crista secundária menor imediatamente atrás (solo rachado quebrado)
            if self.radius > 0.6:
                r_back = max(0.2, self.radius - 0.28)
                bbx = self.wx + math.cos(ang) * r_back
                bby = self.wy + math.sin(ang) * r_back
                sub_h = max(0.06, box_h * 0.45)
                draw_voxel_box(surface, camera, bbx - 0.08, bby - 0.08, 0.0, 0.16, 0.16, sub_h, (75, 52, 34), outline=True)

        # Traçar linhas de fissura no chão entre os pontos do arco
        if len(front_points) >= 2:
            alpha = int((1.0 - prog) * 220)
            fissure_col = (50, 35, 22)
            for j in range(len(front_points) - 1):
                pygame.draw.line(surface, fissure_col, front_points[j], front_points[j + 1], 3)


# =============================================================================
# CICLO 4: TALISMÃ OFUDA E SELO SAGRADO (SEIMEI)
# =============================================================================

class OfudaProjectile:
    """
    Talismã Sagrado e Projétil Elemental de Seimei (Rondel Onmyōdō).
    - Madeira (wood): Agulhas Kusabi-Bari em leque com enraizamento imediato (Root 1.8s) e folhas verdes.
    - Fogo (fire): Guren no Ofuda, esfera ígnea de alto impacto que explode em área (1.4m) e quebra guarda.
    - Terra (earth): Ganseki-dan, monólito rochoso pesado que causa tremor e derruba o rival (Knockdown).
    - Metal (metal): Hagane no Yaiba, lâmina de prata supersônica (32 m/s) 100% IMPARÁVEL (Unblockable).
    - Água (water): Suiryū no Ya, serpente líquida curva e teleguiada que ricocheteia 2 vezes e causa lentidão (-65%).
    - Yin-Yang (yinyang): Senkō / Kurayami, esferas duplas em espiral que atravessam obstáculos e invertem controles.
    """
    def __init__(self, wx: float, wy: float, wz: float, dir_x: float, dir_y: float, owner, max_range: float = 6.8, element: str = "wood"):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.owner = owner
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.element = element

        # Configuração de velocidade, massa, alcance e dano por afinidade elemental
        if element == "metal":
            self.speed = 32.0
            self.damage = 2
            self.radius = 0.34
            self.is_unblockable = True
            self.is_homing = False
        elif element == "earth":
            self.speed = 11.8
            self.damage = 2
            self.radius = 0.52
            self.is_unblockable = False
            self.is_homing = False
        elif element == "fire":
            self.speed = 16.5
            self.damage = 2
            self.radius = 0.44
            self.is_unblockable = False
            self.is_homing = False
        elif element == "water":
            self.speed = 15.2
            self.damage = 1
            self.radius = 0.40
            self.is_unblockable = False
            self.is_homing = True
        elif element == "yinyang":
            self.speed = 14.5
            self.damage = 2
            self.radius = 0.42
            self.is_unblockable = False
            self.is_homing = False
        else:  # wood (default)
            self.speed = 16.0
            self.damage = 1
            self.radius = 0.36
            self.is_unblockable = False
            self.is_homing = False

        self.vx = dir_x * self.speed
        self.vy = dir_y * self.speed
        self.max_range = max_range
        self.dist_traveled = 0.0
        self.is_active = True
        self.spin_timer = 0.0
        self.has_been_reflected = False
        self.bounce_count = 0

    def update(self, dt: float, game_map, particles: list, opponent=None) -> bool:
        if not self.is_active:
            return False

        self.spin_timer += dt * 18.0

        # Água: Guiamento suave em direção ao oponente (Homing Serpent)
        if self.is_homing and opponent and getattr(opponent, "is_alive", True):
            dx_t = opponent.wx - self.wx
            dy_t = opponent.wy - self.wy
            dist_t = math.hypot(dx_t, dy_t)
            if 0.4 < dist_t < 6.5:
                ndx, ndy = dx_t / dist_t, dy_t / dist_t
                steer_rate = 3.8 * dt
                self.dir_x += (ndx - self.dir_x) * steer_rate
                self.dir_y += (ndy - self.dir_y) * steer_rate
                mag = math.hypot(self.dir_x, self.dir_y) or 1.0
                self.dir_x /= mag
                self.dir_y /= mag
                self.vx = self.dir_x * self.speed
                self.vy = self.dir_y * self.speed

        # Yin-Yang: Trajetória ondulatória espiral de dupla hélice
        if self.element == "yinyang":
            perp_x = -self.dir_y
            perp_y = self.dir_x
            wobble = math.sin(self.spin_timer * 1.6) * 0.12
            cur_vx = self.vx + perp_x * wobble * 18.0
            cur_vy = self.vy + perp_y * wobble * 18.0
        else:
            cur_vx = self.vx
            cur_vy = self.vy

        step = math.hypot(cur_vx * dt, cur_vy * dt)
        self.wx += cur_vx * dt
        self.wy += cur_vy * dt
        self.dist_traveled += step

        # Efeitos visuais e partículas contínuas características por elemento
        if particles is not None and random.random() < 0.70:
            from src.effects.particles import SparkParticle, SmokeParticle, FlameVoxelParticle
            if self.element == "fire":
                particles.append(FlameVoxelParticle(self.wx, self.wy, random.uniform(0.18, 0.55), color=random.choice([(255, 80, 35), (255, 170, 45), (255, 235, 95)])))
            elif self.element == "water":
                particles.append(SparkParticle(self.wx, self.wy, random.uniform(0.20, 0.45), color=random.choice([(70, 185, 255), (140, 225, 255), (225, 245, 255)])))
            elif self.element == "wood":
                particles.append(SparkParticle(self.wx, self.wy, random.uniform(0.18, 0.45), color=random.choice([(45, 225, 120), (120, 245, 150), (200, 255, 180)])))
            elif self.element == "metal":
                particles.append(SparkParticle(self.wx, self.wy, random.uniform(0.15, 0.35), color=random.choice([(250, 252, 255), (185, 205, 235), (255, 245, 200)])))
            elif self.element == "earth":
                particles.append(SmokeParticle(self.wx, self.wy, wz=0.25, color=(165, 125, 65), radius=0.18, lifetime=0.35))
            else:  # yinyang
                particles.append(SparkParticle(self.wx, self.wy, random.uniform(0.20, 0.50), color=random.choice([(235, 180, 255), (35, 25, 45), (255, 255, 255)])))

        min_bound = 1.2
        max_bound_x = (game_map.cols - 1.2) if (game_map and hasattr(game_map, "cols")) else 19.8
        max_bound_y = (game_map.rows - 1.2) if (game_map and hasattr(game_map, "rows")) else 19.8

        # Ricochete duplo da Água
        if self.element == "water" and self.bounce_count < 2:
            bounced = False
            if self.wx <= min_bound or self.wx >= max_bound_x:
                self.vx = -self.vx
                self.dir_x = -self.dir_x
                bounced = True
            if self.wy <= min_bound or self.wy >= max_bound_y:
                self.vy = -self.vy
                self.dir_y = -self.dir_y
                bounced = True
            if bounced:
                self.bounce_count += 1
                if particles is not None:
                    from src.effects.particles import SparkParticle
                    for _ in range(8):
                        particles.append(SparkParticle(self.wx, self.wy, 0.45, color=(100, 210, 255)))
        else:
            if self.wx <= min_bound or self.wx >= max_bound_x or self.wy <= min_bound or self.wy >= max_bound_y:
                self.is_active = False
                return False

        if self.dist_traveled >= self.max_range:
            self.is_active = False
            return False

        # Cortar bambus e colidir com rochas
        if hasattr(game_map, "bamboos"):
            for b in game_map.bamboos:
                if not b.is_cut and world_distance(self.wx, self.wy, b.wx, b.wy) < 0.55:
                    b.cut((self.dir_x, self.dir_y))
        return True

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.mesh_primitives import draw_oriented_voxel_box, draw_voxel_box
        wz = getattr(self, "wz", 0.45)
        el = self.element

        if el == "fire":
            # 1. FOGO: Esfera ígnea de plasma com chamas vivas e núcleo incandescente
            draw_voxel_box(surface, camera, self.wx - 0.16, self.wy - 0.16, wz - 0.08, 0.32, 0.32, 0.20, (255, 70, 30), outline=False, alpha=160)
            draw_voxel_box(surface, camera, self.wx - 0.10, self.wy - 0.10, wz - 0.04, 0.20, 0.20, 0.14, (255, 175, 45), outline=False, alpha=210)
            draw_voxel_box(surface, camera, self.wx - 0.05, self.wy - 0.05, wz - 0.02, 0.10, 0.10, 0.08, (255, 255, 200), outline=False, alpha=255)
            # Línguas de fogo orbitais
            rot_a = self.spin_timer * 0.8
            fx = math.cos(rot_a) * 0.14
            fy = math.sin(rot_a) * 0.14
            draw_voxel_box(surface, camera, self.wx + fx - 0.04, self.wy + fy - 0.04, wz + 0.04, 0.08, 0.08, 0.08, (255, 95, 30), outline=False, alpha=180)
            draw_voxel_box(surface, camera, self.wx - fx - 0.04, self.wy - fy - 0.04, wz - 0.04, 0.08, 0.08, 0.08, (255, 140, 40), outline=False, alpha=180)

        elif el == "earth":
            # 2. TERRA: Monólito rochoso facetado denso com rachaduras rúnicas
            draw_voxel_box(surface, camera, self.wx - 0.18, self.wy - 0.18, wz - 0.10, 0.36, 0.36, 0.24, (145, 105, 55), outline=True)
            draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.12, wz + 0.08, 0.24, 0.24, 0.14, (185, 145, 75), outline=True)
            draw_voxel_box(surface, camera, self.wx - 0.06, self.wy - 0.06, wz - 0.04, 0.12, 0.12, 0.10, (245, 205, 95), outline=False, alpha=200)

        elif el == "metal":
            # 3. METAL: Lâmina de prata supersônica estilizada em agulha aerodinâmica afiada
            draw_oriented_voxel_box(surface, camera, self.wx, self.wy, wz, self.dir_x, self.dir_y, 0.0, 0.50, 0.08, 0.03, (240, 245, 255), outline=True)
            draw_oriented_voxel_box(surface, camera, self.wx - self.dir_x * 0.08, self.wy - self.dir_y * 0.08, wz, self.dir_x, self.dir_y, 0.0, 0.20, 0.18, 0.02, (180, 195, 220), outline=True)
            # Rastro de velocidade prateado
            draw_oriented_voxel_box(surface, camera, self.wx - self.dir_x * 0.26, self.wy - self.dir_y * 0.26, wz, self.dir_x, self.dir_y, 0.0, 0.32, 0.04, 0.02, (255, 255, 255), outline=False, alpha=150)

        elif el == "water":
            # 4. ÁGUA: Esfera líquida azul celeste com anel turbilhonante
            draw_voxel_box(surface, camera, self.wx - 0.14, self.wy - 0.14, wz - 0.06, 0.28, 0.28, 0.18, (60, 170, 255), outline=False, alpha=175)
            draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, wz - 0.03, 0.16, 0.16, 0.12, (180, 230, 255), outline=False, alpha=220)
            # Anel de água rodopiante
            ring_rot = self.spin_timer * 1.2
            rx = math.cos(ring_rot) * 0.18
            ry = math.sin(ring_rot) * 0.18
            draw_voxel_box(surface, camera, self.wx + rx - 0.03, self.wy + ry - 0.03, wz, 0.06, 0.06, 0.06, (220, 245, 255), outline=False, alpha=200)
            draw_voxel_box(surface, camera, self.wx - rx - 0.03, self.wy - ry - 0.03, wz, 0.06, 0.06, 0.06, (90, 195, 255), outline=False, alpha=200)

        elif el == "yinyang":
            # 5. YIN-YANG: Orbes duplas entrelaçadas em órbita perpétua (Luz e Vácuo)
            orbit_a = self.spin_timer * 1.5
            ox = math.cos(orbit_a) * 0.14
            oy = math.sin(orbit_a) * 0.14
            # Orbe de Luz (Yang)
            draw_voxel_box(surface, camera, self.wx + ox - 0.07, self.wy + oy - 0.07, wz - 0.04, 0.14, 0.14, 0.12, (255, 255, 255), outline=True, alpha=240)
            draw_voxel_box(surface, camera, self.wx + ox - 0.04, self.wy + oy - 0.04, wz - 0.02, 0.08, 0.08, 0.08, (230, 180, 255), outline=False, alpha=220)
            # Orbe de Escuridão (Yin)
            draw_voxel_box(surface, camera, self.wx - ox - 0.07, self.wy - oy - 0.07, wz - 0.04, 0.14, 0.14, 0.12, (28, 20, 38), outline=True, alpha=240)
            draw_voxel_box(surface, camera, self.wx - ox - 0.04, self.wy - oy - 0.04, wz - 0.02, 0.08, 0.08, 0.08, (140, 50, 200), outline=False, alpha=220)

        else:  # wood (default)
            # 6. MADEIRA: Talismã Ofuda de cipreste com papéis rituais e folhas de esmeralda
            draw_voxel_box(surface, camera, self.wx - 0.10, self.wy - 0.10, wz - 0.04, 0.20, 0.20, 0.10, (45, 215, 120), outline=False, alpha=160)
            draw_oriented_voxel_box(surface, camera, self.wx, self.wy, wz, self.dir_x, self.dir_y, 0.0, 0.30, 0.12, 0.02, (235, 255, 240), outline=True)
            draw_oriented_voxel_box(surface, camera, self.wx + self.dir_x * 0.02, self.wy + self.dir_y * 0.02, wz + 0.005, self.dir_x, self.dir_y, 0.0, 0.18, 0.06, 0.025, (25, 160, 65), outline=False)


class TalismanWard:
    """
    Selo Sagrado, Barreira Kekkai e Rito Elemental de Seimei (Rondel Onmyōdō).
    - Madeira: Shinju no Ibuki (Muralha de Raízes que bloqueia passagem e absorve projéteis).
    - Fogo: Hi-bashira (Pilar de Chamas Eruptivo de dano massivo).
    - Terra: Doryū-heki (Megalito Sísmico com 2 HP de cobertura física).
    - Metal: Kongō-jin no Tate (Escudo Adamantino com deflexão e stun de contra-ataque).
    - Água: Kagami-Mizu no Kekkai (Cúpula de Espelho d'Água que reflete projéteis inimigos).
    - Yin-Yang: Tenmei no Senkoku (Diagrama Astrológico que paralisa o rival em estase celeste).
    """
    def __init__(self, wx: float, wy: float, owner, duration: float = 5.5, element: str = "wood"):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.owner = owner
        self.element = element
        self.duration = duration
        self.timer = duration
        self.state = "ARMED"  # "ARMED" -> "DETONATING" -> "EXPIRED"
        self.detonate_duration = 0.55
        self.detonate_timer = 0.0
        self.trigger_radius = 1.35
        self.pillar_radius = 1.50
        self.is_active = True
        self.hit_fighters = set()
        self.rot_ang = 0.0
        self.hp = 2  # Para terra (megalito)

    def update(self, dt: float, *args, **kwargs) -> bool:
        if not self.is_active:
            return False

        # Extração flexível de argumentos para suportar chamadas do loop universal e chamadas diretas
        fighters = kwargs.get("fighters", None)
        projectiles = kwargs.get("projectiles", None)
        particles = kwargs.get("particles", None)
        game_map = kwargs.get("game_map", None)

        if len(args) == 1:
            game_map = args[0]
        elif len(args) == 2:
            game_map, particles = args[0], args[1]
        elif len(args) >= 3:
            if isinstance(args[0], (list, tuple)):
                fighters = args[0]
                projectiles = args[1] if len(args) > 1 else None
                particles = args[2] if len(args) > 2 else None
                game_map = args[3] if len(args) > 3 else None
            else:
                game_map = args[0]
                particles = args[1]
                fighters = args[2] if len(args) > 2 else None

        self.rot_ang += dt * 3.2

        if self.state == "ARMED":
            self.timer -= dt
            if particles is not None and random.random() < 0.30:
                from src.effects.particles import SparkParticle
                r = random.uniform(0.3, 1.2)
                ang = random.uniform(0, math.pi * 2)
                if self.element == "fire":
                    p_col = (255, 120, 60)
                elif self.element == "water":
                    p_col = (80, 180, 255)
                elif self.element == "wood":
                    p_col = (60, 225, 130)
                elif self.element == "metal":
                    p_col = (235, 240, 255)
                elif self.element == "earth":
                    p_col = (235, 185, 65)
                else:  # yinyang
                    p_col = (220, 150, 255)
                particles.append(SparkParticle(self.wx + math.cos(ang) * r, self.wy + math.sin(ang) * r, 0.10, color=p_col))

            # Purificação e bloqueio/reflexão de projéteis inimigos que tocam a barreira Kekkai armada
            if projectiles:
                for p in projectiles:
                    if p is not self and getattr(p, "is_active", False) and getattr(p, "owner", None) != self.owner:
                        pw_x, pw_y = getattr(p, "wx", None), getattr(p, "wy", None)
                        if pw_x is not None and pw_y is not None:
                            if world_distance(self.wx, self.wy, pw_x, pw_y) <= self.trigger_radius:
                                if self.element == "water" and not getattr(p, "has_been_reflected", False):
                                    # Reflexão do Espelho d'Água
                                    p.dir_x = -getattr(p, "dir_x", 1.0)
                                    p.dir_y = -getattr(p, "dir_y", 0.0)
                                    p.vx = -getattr(p, "vx", 0.0)
                                    p.vy = -getattr(p, "vy", 0.0)
                                    p.owner = self.owner
                                    p.has_been_reflected = True
                                else:
                                    p.is_active = False
                                if particles is not None:
                                    from src.effects.particles import SparkParticle
                                    for _ in range(8):
                                        particles.append(SparkParticle(pw_x, pw_y, 0.45, color=(120, 220, 255)))

            if fighters:
                for f in fighters:
                    if f is not self.owner and getattr(f, "is_alive", True):
                        dist = world_distance(self.wx, self.wy, f.wx, f.wy)
                        if dist <= self.trigger_radius:
                            if self.element == "metal":
                                # Escudo Adamantino: se oponente atacar, sofre deflexão e stun de sino Kagura
                                if getattr(f, "state", "") == "ATTACK":
                                    f.stun(0.70)
                            elif self.element == "yinyang":
                                # Paralisia cósmica direta
                                f.stun(0.75)
                            self.detonate()
                            break

            if self.timer <= 0:
                self.detonate()

        elif self.state == "DETONATING":
            self.detonate_timer += dt
            prog = min(1.0, self.detonate_timer / self.detonate_duration)

            if particles is not None:
                from src.effects.particles import FlameVoxelParticle, SparkParticle
                for _ in range(4):
                    ang = random.uniform(0, math.pi * 2)
                    r = random.uniform(0.1, self.pillar_radius * 0.8)
                    if self.element == "fire":
                        col_list = [(255, 60, 40), (255, 160, 60), (255, 230, 90)]
                        particles.append(FlameVoxelParticle(self.wx + math.cos(ang) * r, self.wy + math.sin(ang) * r, random.uniform(0.1, 1.4), color=random.choice(col_list)))
                    elif self.element == "wood":
                        col_list = [(45, 215, 120), (120, 240, 140), (200, 255, 180)]
                        particles.append(SparkParticle(self.wx + math.cos(ang) * r, self.wy + math.sin(ang) * r, random.uniform(0.1, 0.8), color=random.choice(col_list)))
                    elif self.element == "water":
                        col_list = [(60, 160, 255), (140, 215, 255), (255, 255, 255)]
                        particles.append(SparkParticle(self.wx + math.cos(ang) * r, self.wy + math.sin(ang) * r, random.uniform(0.1, 0.8), color=random.choice(col_list)))
                    elif self.element == "metal":
                        col_list = [(245, 248, 255), (195, 205, 230), (255, 240, 160)]
                        particles.append(SparkParticle(self.wx + math.cos(ang) * r, self.wy + math.sin(ang) * r, random.uniform(0.1, 0.8), color=random.choice(col_list)))
                    elif self.element == "earth":
                        col_list = [(235, 185, 65), (180, 135, 45), (255, 240, 140)]
                        particles.append(SparkParticle(self.wx + math.cos(ang) * r, self.wy + math.sin(ang) * r, random.uniform(0.1, 0.8), color=random.choice(col_list)))
                    else:  # yinyang
                        col_list = [(225, 150, 255), (30, 25, 40), (255, 255, 255)]
                        particles.append(SparkParticle(self.wx + math.cos(ang) * r, self.wy + math.sin(ang) * r, random.uniform(0.1, 1.2), color=random.choice(col_list)))

            if projectiles:
                for p in projectiles:
                    if p is not self and getattr(p, "is_active", False) and getattr(p, "owner", None) != self.owner:
                        pw_x, pw_y = getattr(p, "wx", None), getattr(p, "wy", None)
                        if pw_x is not None and pw_y is not None:
                            if world_distance(self.wx, self.wy, pw_x, pw_y) <= self.pillar_radius:
                                p.is_active = False

            if fighters:
                for f in fighters:
                    if f is not self.owner and getattr(f, "is_alive", True) and id(f) not in self.hit_fighters:
                        dist = world_distance(self.wx, self.wy, f.wx, f.wy)
                        if dist <= self.pillar_radius:
                            self.hit_fighters.add(id(f))
                            dx = f.wx - self.wx
                            dy = f.wy - self.wy
                            mag = math.hypot(dx, dy) or 1.0
                            ndx, ndy = dx / mag, dy / mag
                            if dist <= 0.85:
                                f.take_hit((ndx, ndy), damage=2)
                            else:
                                if game_map is not None:
                                    f.apply_forced_displacement(ndx * 0.55, ndy * 0.55, game_map)
                                f.take_hit((ndx, ndy), damage=1)
                                if getattr(f, "is_alive", True):
                                    f.stun(0.90)

            if self.detonate_timer >= self.detonate_duration:
                self.is_active = False
                return False

        return True

    def detonate(self):
        if self.state == "ARMED":
            self.state = "DETONATING"
            self.detonate_timer = 0.0

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.mesh_primitives import draw_voxel_box

        # Cor do mandala por elemento
        if self.element == "fire":
            ring_col = (255, 90, 50)
            inner_col = (255, 220, 100)
            kekkai_col = (255, 90, 50, 45)
            pillar_c = (255, 120, 60)
        elif self.element == "water":
            ring_col = (70, 180, 255)
            inner_col = (210, 240, 255)
            kekkai_col = (70, 180, 255, 45)
            pillar_c = (140, 220, 255)
        elif self.element == "wood":
            ring_col = (50, 220, 120)
            inner_col = (180, 255, 160)
            kekkai_col = (50, 220, 120, 45)
            pillar_c = (120, 240, 150)
        elif self.element == "metal":
            ring_col = (235, 240, 255)
            inner_col = (255, 245, 180)
            kekkai_col = (235, 240, 255, 45)
            pillar_c = (245, 248, 255)
        elif self.element == "earth":
            ring_col = (235, 185, 65)
            inner_col = (255, 230, 120)
            kekkai_col = (235, 185, 65, 45)
            pillar_c = (220, 175, 60)
        else:  # yinyang
            ring_col = (225, 150, 255)
            inner_col = (255, 255, 255)
            kekkai_col = (225, 150, 255, 45)
            pillar_c = (210, 140, 255)

        if self.state == "ARMED":
            sx, sy = camera.apply(self.wx, self.wy, 0.0)
            r_px = int(self.trigger_radius * 36 * camera.zoom)
            pulse = int(150 + math.sin(self.rot_ang * 2.5) * 50)

            # Anel externo da mandala sagrada com cor do elemento
            pygame.draw.ellipse(surface, (*ring_col, pulse), (sx - r_px, sy - r_px // 2, r_px * 2, r_px), max(2, int(2 * camera.zoom)))
            r_inner = r_px // 2
            pygame.draw.ellipse(surface, (*inner_col, pulse // 2), (sx - r_inner, sy - r_inner // 2, r_inner * 2, r_inner), 1)

            # Estrutura 3D temática facetada por elemento no centro da barreira
            if self.element == "wood":
                # Raízes sagradas e estacas de madeira vivas entrelaçadas
                draw_voxel_box(surface, camera, self.wx - 0.18, self.wy - 0.18, 0.0, 0.36, 0.36, 0.65, (75, 160, 80), outline=True)
                draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, 0.65, 0.16, 0.16, 0.40, (120, 220, 110), outline=True)
                draw_voxel_box(surface, camera, self.wx - 0.28, self.wy - 0.05, 0.0, 0.56, 0.10, 0.35, (55, 120, 60), outline=True)
            elif self.element == "fire":
                # Braseiro ritual com carvão em brasa e chamas ativas
                draw_voxel_box(surface, camera, self.wx - 0.16, self.wy - 0.16, 0.0, 0.32, 0.32, 0.20, (60, 45, 45), outline=True)
                draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.12, 0.20, 0.24, 0.24, 0.12, (255, 80, 30), outline=False, alpha=220)
                draw_voxel_box(surface, camera, self.wx - 0.06, self.wy - 0.06, 0.32, 0.12, 0.12, 0.25, (255, 210, 60), outline=False, alpha=240)
            elif self.element == "earth":
                # Monólito megalítico de pedra rúnica ancestral
                draw_voxel_box(surface, camera, self.wx - 0.22, self.wy - 0.22, 0.0, 0.44, 0.44, 0.85, (135, 105, 65), outline=True)
                draw_voxel_box(surface, camera, self.wx - 0.15, self.wy - 0.15, 0.85, 0.30, 0.30, 0.35, (175, 140, 85), outline=True)
            elif self.element == "metal":
                # Espelho Kagami adamantino de 8 faces refletoras
                draw_voxel_box(surface, camera, self.wx - 0.15, self.wy - 0.15, 0.0, 0.30, 0.30, 0.90, (235, 240, 255), outline=True)
                draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, 0.25, 0.16, 0.16, 0.40, (255, 255, 255), outline=False, alpha=220)
            elif self.element == "water":
                # Bacia sagrada com redemoinho de água translúcido
                draw_voxel_box(surface, camera, self.wx - 0.18, self.wy - 0.18, 0.0, 0.36, 0.36, 0.22, (50, 75, 110), outline=True)
                draw_voxel_box(surface, camera, self.wx - 0.14, self.wy - 0.14, 0.22, 0.28, 0.28, 0.20, (70, 180, 255), outline=False, alpha=180)
            else:  # yinyang
                # Disco Taijitu astral flutuante
                draw_voxel_box(surface, camera, self.wx - 0.16, self.wy - 0.16, 0.15, 0.32, 0.32, 0.10, (255, 255, 255), outline=True, alpha=230)
                draw_voxel_box(surface, camera, self.wx - 0.10, self.wy - 0.10, 0.25, 0.20, 0.20, 0.10, (30, 22, 40), outline=True, alpha=230)

            # Cúpula Kekkai translúcida de proteção espiritual
            b_height = int(36 * camera.zoom)
            kekkai_surf = pygame.Surface((r_px * 2 + 8, b_height + r_px // 2 + 8), pygame.SRCALPHA)
            cx_k = r_px + 4
            top_y = b_height // 2
            bot_y = b_height
            pygame.draw.ellipse(kekkai_surf, kekkai_col, (cx_k - r_px, top_y, r_px * 2, r_px // 2))
            pygame.draw.ellipse(kekkai_surf, (*ring_col, 80), (cx_k - r_px, bot_y, r_px * 2, r_px // 2), 1)
            surface.blit(kekkai_surf, (sx - cx_k, sy - bot_y - r_px // 4))

        elif self.state == "DETONATING":
            prog = self.detonate_timer / self.detonate_duration
            height = 2.8 * math.sin(prog * math.pi)
            sx, sy = camera.apply(self.wx, self.wy, 0.0)
            r_px = int(self.pillar_radius * 36 * camera.zoom * math.sin(prog * math.pi))
            if r_px > 4:
                pygame.draw.ellipse(surface, (*ring_col, 200), (sx - r_px, sy - r_px // 2, r_px * 2, r_px))
                pygame.draw.ellipse(surface, (*inner_col, 240), (sx - r_px // 2, sy - r_px // 4, r_px, r_px // 2))
            draw_voxel_box(surface, camera, self.wx - 0.22, self.wy - 0.22, 0.0, 0.44, 0.44, height, pillar_c, outline=False, alpha=220)
            draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.12, 0.1, 0.24, 0.24, height * 0.85, (255, 245, 160), outline=False, alpha=240)


# =============================================================================
# CICLO 5: ARMADILHA DE URSO DE FERRO FORJADO (AOI — CAÇADORA AINU)
# =============================================================================

class BearTrapProjectile:
    """
    Armadilha de Urso de Ferro Dentado (Bear Trap) plantada no solo por Aoi (Ciclo 5).
    - Permanece armada no solo por até 9.0s (máximo de 2 simultâneas).
    - Quando um oponente pisa no raio de 0.85m (e wz < 0.35m), fecha as mandíbulas de aço com impacto visceral:
      causa 1 de dano, imobiliza/atordoa por 1.15s (deixando o alvo vulnerável à execução com lança/Makiri)
      e aplica lentidão residual nas pernas.
    - Se o dano da armadilha matar o oponente, engatilha o fatality 'TRAP_AND_EXECUTE'.
    """
    def __init__(self, wx: float, wy: float, owner, duration: float = 9.0):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.owner = owner
        self.duration = duration
        self.timer = duration
        self.state = "ARMED"  # "ARMED" -> "SNAPPED" -> "EXPIRED"
        self.snap_duration = 0.85
        self.snap_timer = 0.0
        self.trigger_radius = 0.85
        self.is_active = True
        self.trapped_fighter = None

    def update(self, dt: float, *args, **kwargs) -> bool:
        if not self.is_active:
            return False

        fighters = kwargs.get("fighters", None)
        particles = kwargs.get("particles", None)
        banners = kwargs.get("banners", None)
        cinematic_director = kwargs.get("cinematic_director", None)

        if len(args) >= 2 and particles is None:
            particles = args[1]
        if len(args) >= 3 and fighters is None and isinstance(args[2], (list, tuple)):
            fighters = args[2]

        if self.state == "ARMED":
            self.timer -= dt
            if fighters:
                for f in fighters:
                    if f is not self.owner and getattr(f, "is_alive", True):
                        if getattr(f, "wz", 0.0) < 0.35:
                            dist = world_distance(self.wx, self.wy, f.wx, f.wy)
                            if dist <= self.trigger_radius:
                                self.snap_on_target(f, particles=particles, banners=banners, cinematic_director=cinematic_director)
                                break
            if self.timer <= 0 and self.state == "ARMED":
                self.is_active = False
                return False

        elif self.state == "SNAPPED":
            self.snap_timer += dt
            # Mantém o alvo preso no centro da armadilha enquanto imobilizado
            if self.trapped_fighter and getattr(self.trapped_fighter, "is_alive", False):
                if self.snap_timer < 0.95:
                    self.trapped_fighter.wx = self.wx
                    self.trapped_fighter.wy = self.wy
            if self.snap_timer >= self.snap_duration:
                self.is_active = False
                return False

        return True

    def snap_on_target(self, target, particles: list = None, banners: list = None, cinematic_director=None):
        """Fecha as mandíbulas dentadas de ferro na perna do oponente."""
        if self.state != "ARMED":
            return
        self.state = "SNAPPED"
        self.snap_timer = 0.0
        self.trapped_fighter = target

        if target is not None and getattr(target, "is_alive", True):
            target.wx = self.wx
            target.wy = self.wy
            dx = target.wx - getattr(self.owner, "wx", self.wx)
            dy = target.wy - getattr(self.owner, "wy", self.wy)
            mag = math.hypot(dx, dy) or 1.0
            hit, dead = target.take_hit((dx / mag, dy / mag), damage=1)
            if getattr(target, "is_alive", True):
                target.stun(0.65)
                if hasattr(target, "apply_slow"):
                    target.apply_slow(1.2)
            elif dead and cinematic_director is not None:
                cinematic_director.trigger_fatal_strike(self.owner, target, "TRAP_AND_EXECUTE", (dx / mag, dy / mag))

        if particles is not None:
            from src.effects.particles import BloodParticle, SparkParticle
            for _ in range(18):
                particles.append(BloodParticle(self.wx, self.wy, 0.25))
            for _ in range(10):
                particles.append(SparkParticle(self.wx, self.wy, 0.15, color=(210, 218, 230)))

        if banners is not None:
            from src.effects.particles import FloatingBanner
            banners.append(FloatingBanner("BEAR TRAP!", self.wx, self.wy, wz=1.6, color=(235, 75, 65)))

    def detonate(self):
        """Desarma a armadilha mais antiga quando o limite de 2 é excedido."""
        self.is_active = False

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.mesh_primitives import draw_voxel_box
        iron_dark = (48, 52, 60)
        iron_mid = (82, 88, 98)
        tooth_steel = (185, 192, 205)

        # Base circular/quadrada de ferro forjado e mola lateral no solo
        draw_voxel_box(surface, camera, self.wx - 0.18, self.wy - 0.18, 0.0, 0.36, 0.36, 0.035, iron_dark, outline=True)
        # Prato de pressão central de bronze/ferro
        draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, 0.035, 0.16, 0.16, 0.02, (115, 92, 58), outline=False)

        if self.state == "ARMED":
            # Mandíbulas abertas deitadas nas bordas com dentes de aço apontando para cima
            draw_voxel_box(surface, camera, self.wx - 0.22, self.wy - 0.16, 0.02, 0.06, 0.32, 0.045, iron_mid, outline=True)
            draw_voxel_box(surface, camera, self.wx + 0.16, self.wy - 0.16, 0.02, 0.06, 0.32, 0.045, iron_mid, outline=True)
            for ty in (-0.11, 0.0, 0.11):
                draw_voxel_box(surface, camera, self.wx - 0.20, self.wy + ty - 0.015, 0.065, 0.03, 0.03, 0.04, tooth_steel, outline=False)
                draw_voxel_box(surface, camera, self.wx + 0.17, self.wy + ty - 0.015, 0.065, 0.03, 0.03, 0.04, tooth_steel, outline=False)
        else:
            # Mandíbulas fechadas verticalmente cravadas no centro com mancha carmesim
            draw_voxel_box(surface, camera, self.wx - 0.07, self.wy - 0.15, 0.03, 0.06, 0.30, 0.18, iron_mid, outline=True)
            draw_voxel_box(surface, camera, self.wx + 0.01, self.wy - 0.15, 0.03, 0.06, 0.30, 0.18, iron_mid, outline=True)
            draw_voxel_box(surface, camera, self.wx - 0.03, self.wy - 0.12, 0.18, 0.06, 0.24, 0.04, (175, 28, 32), outline=False)


# ---------------------------------------------------------------------------
# Ciclo 6 — Frascos Alquímicos e Poças Químicas de Hendrika van der Bilt
# ---------------------------------------------------------------------------

REAGENT_COLORS = {
    "acid": ((45, 225, 120), (20, 140, 65)),     # Ácido Corrosivo (Verde Esmeralda)
    "fire": ((255, 125, 35), (205, 50, 20)),     # Fogo Grego (Laranja Flamejante)
    "ether": ((185, 85, 235), (115, 35, 165)),   # Éter Soporífero (Violeta Espectral)
    "frost": ((95, 215, 250), (45, 135, 195)),   # Salitre Congelante (Ciano Gélido)
    "miasma": ((235, 210, 45), (165, 140, 25)),  # Miasma Neurotóxico (Ocre Tóxico)
}


class ChemicalPoolHazard:
    """Poça ou nuvem persistente gerada pelo impacto do frasco alquímico de Hendrika."""

    def __init__(self, wx: float, wy: float, reagent: str = "acid", tier: int = 1, owner=None):
        self.wx = wx
        self.wy = wy
        self.reagent = reagent
        self.tier = tier
        self.owner = owner
        self.is_active = True
        self.duration = 4.2 if tier == 1 else 6.0
        self.timer = self.duration
        self.radius = 1.15 if tier == 1 else 1.65
        self.tick_timer = 0.0
        self.col_core, self.col_edge = REAGENT_COLORS.get(reagent, ((45, 225, 120), (20, 140, 65)))

    def update(self, dt: float, fighters: list = None, particles: list = None, banners: list = None, cinematic_director=None):
        if not self.is_active:
            return False

        self.timer -= dt
        self.tick_timer += dt
        if self.timer <= 0:
            self.is_active = False
            return False

        # Efeito de bolhas e fumaça química emanando da poça
        if particles is not None and random.random() < 0.45:
            from src.effects.particles import SmokeParticle
            bx = self.wx + random.uniform(-self.radius * 0.75, self.radius * 0.75)
            by = self.wy + random.uniform(-self.radius * 0.75, self.radius * 0.75)
            particles.append(SmokeParticle(
                bx, by, wz=random.uniform(0.05, 0.35),
                color=self.col_core,
                radius=random.uniform(0.12, 0.24),
                lifetime=random.uniform(0.5, 0.9)
            ))

        # Interação contínua com os combatentes
        if fighters and self.tick_timer >= 0.75:
            self.tick_timer = 0.0
            for f in fighters:
                if f is not self.owner and getattr(f, "is_alive", True):
                    dist = math.hypot(f.wx - self.wx, f.wy - self.wy)
                    if dist <= self.radius + getattr(f, "radius", 0.35):
                        self._apply_effect_to_target(f, particles, banners, cinematic_director)

        return True

    def _apply_effect_to_target(self, target, particles: list = None, banners: list = None, cinematic_director=None, is_direct: bool = False):
        if not target or not getattr(target, "is_alive", True):
            return

        from src.effects.particles import FloatingBanner, SparkParticle, SmokeParticle

        if self.reagent == "acid":
            # Ácido Corrosivo: Quebra parry com stun severo + 1 de dano + corrosão contínua
            target.acid_timer = 4.0
            if getattr(target, "state", "") == "PARRY":
                target.stun(1.10)
                if banners is not None:
                    banners.append(FloatingBanner("ARMOR ERODED (GUARD CRUSH)!", target.wx, target.wy, wz=1.75, color=(80, 245, 90), duration=1.0))
            hit, dead = target.take_hit((0.0, 0.0), damage=1)
            if banners is not None and getattr(target, "state", "") != "PARRY":
                banners.append(FloatingBanner("VITRIOL ACID CORROSION!", target.wx, target.wy, wz=1.75, color=(80, 245, 90), duration=0.85))
            if particles is not None:
                for _ in range(16):
                    particles.append(SparkParticle(target.wx, target.wy, 0.40, color=(100, 255, 110)))
            if dead and cinematic_director:
                cinematic_director.trigger_fatal_strike(self.owner, target, "ALCHEMIC_ACID_DISSOLVE", (1.0, 0.0))

        elif self.reagent == "fire":
            # Fogo Grego: Dano térmico imediato + queimação contínua + repulsão violenta
            target.burning_timer = 3.5
            dx = target.wx - self.wx
            dy = target.wy - self.wy
            mag = math.hypot(dx, dy) or 1.0
            hit, dead = target.take_hit((dx / mag, dy / mag), damage=1)
            push_force = 1.65 if self.tier == 1 else 2.25
            target.wx += (dx / mag) * push_force
            target.wy += (dy / mag) * push_force
            if banners is not None:
                banners.append(FloatingBanner("GREEK FIRE (BLAZE)!", target.wx, target.wy, wz=1.75, color=(255, 90, 35), duration=0.85))
            if particles is not None:
                from src.effects.particles import FlameVoxelParticle
                for _ in range(16):
                    particles.append(FlameVoxelParticle(target.wx, target.wy, 0.50, color=(255, 110, 40)))
            if dead and cinematic_director:
                cinematic_director.trigger_fatal_strike(self.owner, target, "ALCHEMIC_FIRE_ASH", (dx / mag, dy / mag))

        elif self.reagent == "ether":
            # Éter Soporífero: Névoa narcótica densa que coloca o rival em sono profundo (Sleep Stun)
            target.sleep_timer = 2.4 if self.tier == 1 else 3.5
            target.stun(2.4 if self.tier == 1 else 3.5)
            if banners is not None:
                banners.append(FloatingBanner("SOPORIFIC ETHER (SLEEP)!", target.wx, target.wy, wz=1.75, color=(130, 235, 255), duration=1.2))
            if particles is not None:
                for _ in range(16):
                    particles.append(SmokeParticle(target.wx, target.wy, wz=0.5, color=(140, 240, 255), radius=0.35, lifetime=1.1))

        elif self.reagent == "frost":
            # Salitre Congelante: Dano de geada + aprisionamento em gelo (Frozen) + lentidão severa
            target.frozen_timer = 2.2 if self.tier == 1 else 3.2
            if hasattr(target, "apply_slow"):
                target.apply_slow(4.5 if self.tier == 1 else 6.5)
            else:
                target.slow_timer = 4.5 if self.tier == 1 else 6.5
            if is_direct or self.tier == 2:
                hit, dead = target.take_hit((0.0, 0.0), damage=1)
                if dead and cinematic_director:
                    cinematic_director.trigger_fatal_strike(self.owner, target, "ALCHEMIC_FROST_SHATTER", (1.0, 0.0))
            if banners is not None:
                banners.append(FloatingBanner("FROSTBITE (DEEP FREEZE)!", target.wx, target.wy, wz=1.75, color=(160, 230, 255), duration=1.0))
            if particles is not None:
                for _ in range(18):
                    particles.append(SparkParticle(target.wx, target.wy, 0.40, color=(190, 240, 255)))

        elif self.reagent == "miasma":
            # Miasma Neurotóxico: Inverte controles do rival (Confusão) e causa 1 de dano
            target.confused_timer = 4.0 if self.tier == 1 else 6.0
            hit, dead = target.take_hit((0.0, 0.0), damage=1)
            if banners is not None:
                banners.append(FloatingBanner("NEUROTOXIC MIASMA (CONFUSED)!", target.wx, target.wy, wz=1.75, color=(220, 110, 255), duration=1.0))
            if particles is not None:
                for _ in range(16):
                    particles.append(SmokeParticle(target.wx, target.wy, wz=0.4, color=(190, 80, 245), radius=0.30, lifetime=1.1))
            if dead and cinematic_director:
                cinematic_director.trigger_fatal_strike(self.owner, target, "ALCHEMIC_MIASMA_MELT", (1.0, 0.0))

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.mesh_primitives import draw_voxel_box
        t = pygame.time.get_ticks() * 0.0035
        pulse = 0.09 * math.sin(t + self.wx * 2.0)
        r = self.radius + pulse

        # 1. Poça química translúcida ampla no solo
        draw_voxel_box(surface, camera, self.wx - r * 0.88, self.wy - r * 0.88, 0.004, r * 1.76, r * 1.76, 0.02, self.col_edge, outline=False, alpha=110)
        # 2. Anel intermediário saturado com cor da substância
        draw_voxel_box(surface, camera, self.wx - r * 0.58, self.wy - r * 0.58, 0.010, r * 1.16, r * 1.16, 0.025, self.col_core, outline=False, alpha=160)
        # 3. Núcleo central
        draw_voxel_box(surface, camera, self.wx - 0.24, self.wy - 0.24, 0.018, 0.48, 0.48, 0.03, (255, 255, 255), outline=False, alpha=140)

        # 4. Elementos volumétricos 3D característicos para cada um dos 5 reagentes alquímicos
        reagent = self.reagent
        if reagent == "frost":
            # Agulhas / Espetos de cristal de gelo 3D pontiagudos brotando da poça
            c_ice = (210, 245, 255)
            c_ice_core = (140, 215, 255)
            draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.12, 0.02, 0.24, 0.24, 0.38, c_ice_core, outline=True)
            draw_voxel_box(surface, camera, self.wx + 0.18, self.wy - 0.10, 0.02, 0.16, 0.16, 0.28, c_ice, outline=True)
            draw_voxel_box(surface, camera, self.wx - 0.20, self.wy + 0.12, 0.02, 0.18, 0.18, 0.32, c_ice, outline=True)
            draw_voxel_box(surface, camera, self.wx + 0.08, self.wy + 0.18, 0.02, 0.14, 0.14, 0.24, c_ice_core, outline=True)

        elif reagent == "fire":
            # Línguas de fogo 3D saltitantes e chamas ativas dançando na poça
            flame_h = 0.35 + 0.10 * math.sin(t * 4.0 + self.wy)
            draw_voxel_box(surface, camera, self.wx - 0.14, self.wy - 0.14, 0.02, 0.28, 0.28, flame_h, (255, 80, 25), outline=False, alpha=230)
            draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, 0.04, 0.16, 0.16, flame_h * 1.25, (255, 190, 50), outline=False, alpha=240)
            draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - 0.04, 0.08, 0.08, 0.08, flame_h * 0.70, (255, 255, 180), outline=False, alpha=255)

        elif reagent == "acid":
            # Bolhas volumétricas de ácido verde efervescente surgindo na superfície
            b_bob = 0.03 * math.sin(t * 5.0)
            draw_voxel_box(surface, camera, self.wx - 0.10, self.wy - 0.10, 0.02 + b_bob, 0.20, 0.20, 0.15, (65, 235, 85), outline=True, alpha=220)
            draw_voxel_box(surface, camera, self.wx + 0.14, self.wy + 0.08, 0.02 - b_bob, 0.14, 0.14, 0.12, (95, 255, 115), outline=True, alpha=200)
            draw_voxel_box(surface, camera, self.wx - 0.16, self.wy + 0.12, 0.02 + b_bob * 0.5, 0.12, 0.12, 0.10, (140, 255, 150), outline=True, alpha=200)

        elif reagent == "ether":
            # Nuvens de névoa ciano ondulantes acima da poça soporífera
            mist_bob = 0.05 * math.sin(t * 2.2)
            draw_voxel_box(surface, camera, self.wx - 0.22, self.wy - 0.22, 0.12 + mist_bob, 0.44, 0.44, 0.14, (160, 235, 255), outline=False, alpha=130)
            draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.12, 0.22 - mist_bob, 0.24, 0.24, 0.16, (220, 250, 255), outline=False, alpha=160)

        elif reagent == "miasma":
            # Orbes densas de lodo roxo venenoso e emanação tóxica
            draw_voxel_box(surface, camera, self.wx - 0.15, self.wy - 0.15, 0.02, 0.30, 0.30, 0.18, (140, 45, 195), outline=True, alpha=210)
            draw_voxel_box(surface, camera, self.wx - 0.08, self.wy - 0.08, 0.15, 0.16, 0.16, 0.15, (200, 85, 245), outline=True, alpha=230)
            draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - 0.04, 0.26, 0.08, 0.08, 0.08, (255, 195, 255), outline=False, alpha=250)


class AlchemicFlaskProjectile:
    """Frasco de vidro químico arremessado em arco parabólico 3D por Hendrika."""

    def __init__(self, owner, start_x: float, start_y: float, target_x: float, target_y: float, reagent: str = "acid", tier: int = 1):
        self.owner = owner
        self.wx = start_x
        self.wy = start_y
        self.wz = 0.75  # Altura da mão de Hendrika
        self.target_x = target_x
        self.target_y = target_y
        self.reagent = reagent
        self.tier = tier
        self.is_active = True

        dx = target_x - start_x
        dy = target_y - start_y
        self.total_dist = math.hypot(dx, dy) or 1.0
        self.dir_x = dx / self.total_dist
        self.dir_y = dy / self.total_dist

        self.speed = 10.5
        self.total_time = max(0.28, min(0.65, self.total_dist / self.speed))
        self.elapsed = 0.0
        self.peak_h = 1.35
        self.rot_angle = 0.0
        self.col_core, self.col_edge = REAGENT_COLORS.get(reagent, ((45, 225, 120), (20, 140, 65)))

    def update(self, dt: float, game_map=None, particles: list = None, fighters: list = None, banners: list = None, cinematic_director=None, chemical_pools: list = None, **kwargs):
        if not self.is_active:
            return False

        self.elapsed += dt
        prog = min(1.0, self.elapsed / self.total_time)
        self.rot_angle += dt * 720.0

        # Trajetória horizontal interpolada
        self.wx += self.dir_x * self.speed * dt
        self.wy += self.dir_y * self.speed * dt

        # Trajetória balística no eixo Z
        self.wz = max(0.0, math.sin(prog * math.pi) * self.peak_h)

        # Trilha de vapor químico colorido
        if particles is not None and random.random() < 0.65:
            from src.effects.particles import SmokeParticle
            particles.append(SmokeParticle(
                self.wx, self.wy, wz=self.wz + 0.05,
                color=self.col_core,
                radius=0.14,
                lifetime=0.35
            ))

        # Colisão direta em voo com combatentes
        if fighters and prog > 0.15:
            for f in fighters:
                if f is not self.owner and getattr(f, "is_alive", True):
                    dist = math.hypot(f.wx - self.wx, f.wy - self.wy)
                    if dist <= 0.55 and abs(self.wz - getattr(f, "wz", 0.0)) < 0.85:
                        self.detonate(game_map, particles, fighters, banners, cinematic_director, chemical_pools, direct_hit=f)
                        return False

        # Impacto com o solo
        if prog >= 1.0 or self.wz <= 0.02:
            self.detonate(game_map, particles, fighters, banners, cinematic_director, chemical_pools)
            return False

        return True

    def detonate(self, game_map=None, particles: list = None, fighters: list = None, banners: list = None, cinematic_director=None, chemical_pools: list = None, direct_hit=None):
        self.is_active = False

        # Fallback para as poças ativas do proprietário (Hendrika)
        if chemical_pools is None and self.owner and hasattr(self.owner, "active_pools"):
            chemical_pools = self.owner.active_pools

        # Efeito de estilhaço de vidro e respingos químicos
        if particles is not None:
            from src.effects.particles import SparkParticle, SmokeParticle
            # Estilhaços de vidro translúcido
            for _ in range(16):
                particles.append(SparkParticle(self.wx, self.wy, 0.20, color=(210, 245, 255)))
            # Nuvem de impacto químico volumétrica
            for _ in range(20):
                particles.append(SmokeParticle(self.wx, self.wy, wz=random.uniform(0.15, 0.40), color=self.col_core, radius=random.uniform(0.24, 0.42), lifetime=1.0))

        # Som de vidro quebrando / splash
        from src.audio.sound_manager import get_sound_manager
        from src.audio.sound_events import SoundEvent
        get_sound_manager().play(SoundEvent.OBSTACLE_HIT, volume_scale=1.0)

        # Criar a poça persistente no solo
        pool = ChemicalPoolHazard(self.wx, self.wy, self.reagent, self.tier, self.owner)
        if chemical_pools is not None:
            chemical_pools.append(pool)

        # 1. Se acertou em cheio um alvo no ar
        if direct_hit and getattr(direct_hit, "is_alive", True):
            dx = direct_hit.wx - self.wx
            dy = direct_hit.wy - self.wy
            mag = math.hypot(dx, dy) or 1.0
            damage = 1 if self.tier == 1 else 2
            hit, dead = direct_hit.take_hit((dx / mag, dy / mag), damage=damage)
            if dead and cinematic_director:
                death_style = "ALCHEMIC_ACID_DISSOLVE"
                if self.reagent == "fire":
                    death_style = "ALCHEMIC_FIRE_ASH"
                elif self.reagent == "ether":
                    death_style = "ALCHEMIC_ETHER_SUFFOCATION"
                elif self.reagent == "frost":
                    death_style = "ALCHEMIC_FROST_SHATTER"
                elif self.reagent == "miasma":
                    death_style = "ALCHEMIC_MIASMA_MELT"
                cinematic_director.trigger_fatal_strike(self.owner, direct_hit, death_style, (dx / mag, dy / mag))
            pool._apply_effect_to_target(direct_hit, particles, banners, cinematic_director, is_direct=True)

        # 2. Splash de impacto imediato no solo para qualquer combatente rival dentro do raio
        elif fighters:
            for f in fighters:
                if f is not self.owner and getattr(f, "is_alive", True):
                    dist = math.hypot(f.wx - self.wx, f.wy - self.wy)
                    if dist <= pool.radius + getattr(f, "radius", 0.35):
                        pool._apply_effect_to_target(f, particles, banners, cinematic_director, is_direct=False)

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.mesh_primitives import draw_voxel_box
        # Sombra no solo
        draw_voxel_box(surface, camera, self.wx - 0.10, self.wy - 0.10, 0.0, 0.20, 0.20, 0.015, (20, 24, 30), outline=False, alpha=90)
        # Frasco esférico/cônico de vidro químico no ar
        draw_voxel_box(surface, camera, self.wx - 0.09, self.wy - 0.09, self.wz, 0.18, 0.18, 0.22, (215, 245, 255), outline=True, alpha=185)
        # Reagente líquido brilhante no interior
        draw_voxel_box(surface, camera, self.wx - 0.07, self.wy - 0.07, self.wz + 0.02, 0.14, 0.14, 0.15, self.col_core, outline=False)
        # Gargalo e rolha de cortiça
        draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - 0.04, self.wz + 0.22, 0.08, 0.08, 0.08, (135, 95, 55), outline=False)


