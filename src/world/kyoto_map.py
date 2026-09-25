"""
Novo Cenário: Rua de Kyoto durante o Bakumatsu (Noite em Chamas).
- Estrada diagonal estreita (4 tiles de largura) inspirada em Sannenzaka e Sanjo Dori.
- Fachadas densas de Machiyas tradicionais de 2 andares (engawa sobre pedras, reboco branco, telhado duplo kawara).
- Sistema de chamas dinâmicas nos telhados: as labaredas nascem, crescem, diminuem e somem aleatoriamente.
- Canto Noroeste (NW): estalagens em chamas intensas com vigas carbonizadas e fumaça.
- Canto Sudeste (SE): estalagens com transparência seletiva (Opção A) TAMBÉM em chamas vivas nos telhados.
- Perigos: Carruagem desgovernada em disparada pela via estreita e escombros incandescentes caindo.
"""
import math
import random
import pygame
from src.config import (
    MAP_COLS, MAP_ROWS, HALF_TILE_W, HALF_TILE_H,
    COLOR_KYOTO_BG, COLOR_KYOTO_STONE, COLOR_KYOTO_STONE_LIGHT,
    COLOR_KYOTO_STONE_DARK, COLOR_KYOTO_CURB, COLOR_KYOTO_PAVEMENT,
    COLOR_KYOTO_WOOD_BURNT, COLOR_KYOTO_WOOD_DARK, COLOR_KYOTO_ROOF_TILE,
    COLOR_KYOTO_FIRE_CORE, COLOR_KYOTO_FIRE_MID, COLOR_KYOTO_FIRE_EDGE,
    COLOR_KYOTO_EMBER, COLOR_KYOTO_CARRIAGE_WOOD, COLOR_KYOTO_CARRIAGE_GOLD,
    COLOR_KYOTO_HORSE_DARK, COLOR_WHITE, COLOR_GOLD
)
from src.isometric.voxel_renderer import draw_voxel_box
from src.isometric.iso_math import world_to_iso, world_distance
from src.effects.particles import SparkParticle, BloodParticle, FloatingBanner

TILE_KYOTO_STREET = 10
TILE_KYOTO_STREET_ALT = 11
TILE_KYOTO_CURB = 12
TILE_KYOTO_SIDEWALK = 13
TILE_KYOTO_BUILDING = 14

# Cores arquitetônicas inspiradas nas fotos históricas de Kyoto
COLOR_PLASTER = (218, 212, 198)       # Reboco tradicional Shikkui branco/creme
COLOR_ENGAWA_WOOD = (105, 78, 55)     # Madeira nobre do assoalho do Engawa
COLOR_STONE_FOOTING = (90, 88, 85)     # Pedras naturais de fundação
COLOR_LATTICE = (62, 45, 32)           # Treliça Koushi de madeira escura


class KyotoLantern:
    """Lanterna de pedra tradicional japonesa (Ishi-doro) com chama cálida."""
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy

    def render(self, surface: pygame.Surface, camera, time_val: float):
        cx, cy = self.wx, self.wy
        # 1. Base de pedra chanfrada
        draw_voxel_box(surface, camera, cx - 0.22, cy - 0.22, 0.08, 0.44, 0.44, 0.15, COLOR_KYOTO_STONE_DARK, outline=True)
        # 2. Pilar central
        draw_voxel_box(surface, camera, cx - 0.10, cy - 0.10, 0.23, 0.20, 0.20, 0.38, COLOR_KYOTO_STONE, outline=True)
        # 3. Câmara de luz (fogo suave da lanterna)
        flicker = 0.85 + 0.15 * math.sin(time_val * 10.0 + cx * 3.0)
        draw_voxel_box(surface, camera, cx - 0.16, cy - 0.16, 0.61, 0.32, 0.32, 0.22, (int(255 * flicker), int(200 * flicker), 80), outline=False)
        # 4. Teto pagoda de pedra
        draw_voxel_box(surface, camera, cx - 0.26, cy - 0.26, 0.83, 0.52, 0.52, 0.14, COLOR_KYOTO_ROOF_TILE, outline=True)
        draw_voxel_box(surface, camera, cx - 0.08, cy - 0.08, 0.97, 0.16, 0.16, 0.08, COLOR_KYOTO_STONE, outline=False)


class DynamicFlameSpot:
    """Foco de chama que nasce, cresce, atinge o ápice, diminui e some ciclicamente."""
    def __init__(self, rel_x: float, rel_y: float, period: float, burn_time: float, max_h: float, phase_shift: float):
        self.rel_x = rel_x
        self.rel_y = rel_y
        self.period = period          # Período total do ciclo em segundos
        self.burn_time = burn_time    # Duração em chamas
        self.max_h = max_h            # Altura máxima da labareda
        self.phase_shift = phase_shift

    def get_height(self, time_val: float) -> float:
        cycle_t = (time_val + self.phase_shift) % self.period
        if cycle_t < self.burn_time:
            prog = cycle_t / self.burn_time
            flicker = 0.86 + 0.14 * math.sin(time_val * 14.0 + self.phase_shift * 4.0)
            return math.sin(prog * math.pi) * self.max_h * flicker
        return 0.0


class MachiyaFacade:
    """
    Fachada de Machiya tradicional japonesa de 2 andares densa:
    - Base com pedras naturais e varanda Engawa elevada
    - Andar 1: paredes Shikkui e pilares de sustentação verticais
    - Telhado intermediário com beiral saliente
    - Andar 2: sacada com treliça Koushi e grande telhado de telhas pretas Kawara
    - Chamas dinâmicas nos telhados (nascem, crescem e somem)
    - Suporte a modo translúcido (is_transparent=True para o Canto Sudeste)
    """
    def __init__(self, wx: float, wy: float, width: float, depth: float, is_transparent: bool = False, seed: int = 0):
        self.wx = wx
        self.wy = wy
        self.width = width
        self.depth = depth
        self.is_transparent = is_transparent
        self.seed = seed

        rng = random.Random(seed)
        self.flame_spots: list[DynamicFlameSpot] = []
        num_spots = 4
        for i in range(num_spots):
            rx = 0.4 + (i + rng.uniform(-0.15, 0.15)) * ((width - 0.8) / max(1, num_spots - 1))
            ry = depth * rng.uniform(0.25, 0.60)
            period = rng.uniform(4.2, 7.2)
            burn_time = rng.uniform(2.0, period * 0.65)
            max_h = rng.uniform(0.65, 1.25)
            shift = rng.uniform(0.0, 10.0)
            self.flame_spots.append(DynamicFlameSpot(rx, ry, period, burn_time, max_h, shift))

    def render(self, surface: pygame.Surface, camera, time_val: float):
        alpha = 75 if self.is_transparent else 255
        roof_alpha = 65 if self.is_transparent else 255

        # 1. Pedras de fundação naturais
        footing_h = 0.12
        for fx_off in [0.15, self.width * 0.5 - 0.1, self.width - 0.35]:
            draw_voxel_box(surface, camera, self.wx + fx_off, self.wy + 0.1, 0.0, 0.25, 0.25, footing_h, COLOR_STONE_FOOTING, outline=True, alpha=alpha)

        # 2. Varanda Engawa elevada
        engawa_d = 0.75
        engawa_h = 0.14
        engawa_col = (48, 36, 28) if not self.is_transparent else COLOR_ENGAWA_WOOD
        draw_voxel_box(surface, camera, self.wx, self.wy + self.depth - engawa_d, footing_h, self.width, engawa_d, engawa_h, engawa_col, outline=True, alpha=alpha)

        # 3. Andar 1: Paredes de reboco Shikkui e pilares
        p1_h = 1.35
        p1_z = footing_h + engawa_h
        wall_col = (65, 52, 45) if not self.is_transparent else COLOR_PLASTER
        beam_col = COLOR_KYOTO_WOOD_BURNT if not self.is_transparent else COLOR_KYOTO_WOOD_DARK

        draw_voxel_box(surface, camera, self.wx + 0.15, self.wy + 0.15, p1_z, self.width - 0.3, self.depth - engawa_d - 0.2, p1_h, wall_col, outline=False, alpha=alpha)

        # Pilares verticais
        for i in range(4):
            px = self.wx + i * ((self.width - 0.20) / 3.0)
            draw_voxel_box(surface, camera, px, self.wy + self.depth - engawa_d, p1_z, 0.20, 0.20, p1_h, beam_col, outline=True, alpha=alpha)

        # Viga transversal Nageshi
        draw_voxel_box(surface, camera, self.wx - 0.05, self.wy + 0.1, p1_z + p1_h - 0.10, self.width + 0.10, self.depth - 0.15, 0.12, beam_col, outline=True, alpha=alpha)

        # 4. Telhado intermediário (Beiral do 1º andar)
        eave_z = p1_z + p1_h
        draw_voxel_box(surface, camera, self.wx - 0.20, self.wy - 0.10, eave_z, self.width + 0.40, self.depth + 0.15, 0.20, COLOR_KYOTO_ROOF_TILE, outline=True, alpha=roof_alpha)

        # 5. Andar 2: Balcão com treliça Koushi
        p2_z = eave_z + 0.16
        p2_h = 1.25
        draw_voxel_box(surface, camera, self.wx + 0.25, self.wy + 0.25, p2_z, self.width - 0.5, self.depth - 0.75, p2_h, wall_col, outline=False, alpha=alpha)
        draw_voxel_box(surface, camera, self.wx + 0.35, self.wy + self.depth - 0.60, p2_z + 0.15, self.width - 0.70, 0.10, p2_h - 0.30, COLOR_LATTICE, outline=True, alpha=alpha)

        # 6. Telhado Superior Imponente (Telhas Kawara)
        roof_z = p2_z + p2_h
        roof_d = self.depth - 0.25
        draw_voxel_box(surface, camera, self.wx - 0.25, self.wy - 0.15, roof_z, self.width + 0.50, roof_d, 0.28, COLOR_KYOTO_ROOF_TILE, outline=True, alpha=roof_alpha)
        draw_voxel_box(surface, camera, self.wx - 0.10, self.wy + roof_d * 0.32, roof_z + 0.26, self.width + 0.20, 0.30, 0.20, (52, 54, 58), outline=True, alpha=roof_alpha)

        # 7. Chamas Dinâmicas nos Telhados (Nascem, crescem, diminuem e somem)
        flame_alpha = 185 if self.is_transparent else 255
        for spot in self.flame_spots:
            fh = spot.get_height(time_val)
            if fh > 0.04:
                fx = self.wx + spot.rel_x
                fy = self.wy + spot.rel_y

                # Núcleo amarelo brilhante
                draw_voxel_box(surface, camera, fx - 0.20, fy - 0.20, roof_z + 0.32, 0.40, 0.40, fh * 0.55, COLOR_KYOTO_FIRE_CORE, outline=False, alpha=flame_alpha)
                # Corpo laranja
                draw_voxel_box(surface, camera, fx - 0.15, fy - 0.15, roof_z + 0.32 + fh * 0.45, 0.30, 0.30, fh * 0.45, COLOR_KYOTO_FIRE_MID, outline=False, alpha=flame_alpha)
                # Ponta avermelhada
                if fh > 0.35:
                    draw_voxel_box(surface, camera, fx - 0.10, fy - 0.10, roof_z + 0.32 + fh * 0.85, 0.20, 0.20, fh * 0.25, COLOR_KYOTO_FIRE_EDGE, outline=False, alpha=flame_alpha)

                # Fumaça ascendente quando o fogo está alto
                if fh > 0.5:
                    sm_phase = time_val * 2.5 + spot.phase_shift
                    sm_z = roof_z + 1.2 + (sm_phase % 2.0)
                    sm_alpha = max(0, int(130 * (1.0 - (sm_z - roof_z - 1.2) / 2.0)))
                    draw_voxel_box(surface, camera, fx, fy, sm_z, 0.35, 0.35, 0.22, (60, 55, 55), outline=False, alpha=sm_alpha)


class RunawayCarriage:
    """
    Carruagem tradicional desgovernada em disparada pela rua diagonal estreita.
    Modelada em Voxel 3D com cabine laqueada, frisos dourados, rodas e cavalo acoplado.
    Lethal: atropela e mata instantaneamente quem estiver na rota.
    """
    def __init__(self, start_pos: tuple[float, float], end_pos: tuple[float, float], speed: float = 14.0):
        self.wx, self.wy = start_pos
        self.start_x, self.start_y = start_pos
        self.end_x, self.end_y = end_pos
        self.wz = 0.0
        self.speed = speed
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy)
        self.dir_x = dx / dist if dist > 0.001 else 0.0
        self.dir_y = dy / dist if dist > 0.001 else 1.0
        self.total_dist = dist
        self.traveled = 0.0
        self.is_active = True
        self.wheel_rot = 0.0
        self.hit_radius = 1.30
        self.warning_active = True
        self.warning_timer = 1.2

    def update(self, dt: float, camera, particles: list) -> bool:
        if not self.is_active:
            return False

        if self.warning_timer > 0:
            self.warning_timer -= dt
            if random.random() < 0.6:
                particles.append(SparkParticle(self.wx, self.wy, wz=0.1, color=(140, 130, 120)))
            return True

        step = self.speed * dt
        self.wx += self.dir_x * step
        self.wy += self.dir_y * step
        self.traveled += step
        self.wheel_rot += step * 4.0

        if random.random() < 0.7:
            particles.append(SparkParticle(self.wx - self.dir_x * 0.8, self.wy - self.dir_y * 0.8, wz=0.1, color=(130, 115, 100)))
        if random.random() < 0.25:
            particles.append(SparkParticle(self.wx, self.wy, wz=0.2, color=COLOR_KYOTO_EMBER))

        if self.traveled >= self.total_dist + 4.0:
            self.is_active = False
            return False

        return True

    def check_fighter_hit(self, fighter, particles: list, banners: list, camera, cinematic_director=None) -> bool:
        if not self.is_active or self.warning_timer > 0 or not fighter.is_alive:
            return False

        dist = world_distance(self.wx, self.wy, fighter.wx, fighter.wy)
        horse_wx = self.wx + self.dir_x * 1.4
        horse_wy = self.wy + self.dir_y * 1.4
        dist_horse = world_distance(horse_wx, horse_wy, fighter.wx, fighter.wy)

        if dist < self.hit_radius or dist_horse < 1.15:
            fighter.take_hit((self.dir_x, self.dir_y), damage=99)
            fighter.is_alive = False

            for _ in range(25):
                particles.append(BloodParticle(fighter.wx, fighter.wy, 0.7))
                particles.append(SparkParticle(fighter.wx, fighter.wy, 0.5, color=COLOR_KYOTO_CARRIAGE_WOOD))

            banners.append(FloatingBanner("CARRIAGE CRUSH!", fighter.wx, fighter.wy, wz=1.8, color=(255, 60, 40)))
            camera.add_shake(14.0)

            if cinematic_director:
                cinematic_director.trigger_fatal_strike(
                    None,
                    fighter,
                    death_style="HEADSHOT_EXPLODE",
                    slash_dir=(self.dir_x, self.dir_y)
                )
            return True
        return False

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active or self.warning_timer > 0:
            return

        cx, cy = self.wx, self.wy

        # 1. Sombra alongada no chão de pedra
        base_sx, base_sy = camera.apply(cx, cy, 0.0)
        pygame.draw.ellipse(surface, (14, 12, 14, 140), (base_sx - 45, base_sy - 22, 90, 44))

        # 2. Chassi de madeira escura
        draw_voxel_box(surface, camera, cx - 0.55, cy - 0.60, 0.22, 1.10, 1.20, 0.18, (42, 28, 20), outline=True)

        # 3. Cabine Nobre da Carruagem (Laca preta com frisos dourados)
        draw_voxel_box(surface, camera, cx - 0.50, cy - 0.55, 0.40, 1.00, 1.10, 0.85, COLOR_KYOTO_CARRIAGE_WOOD, outline=True)
        # Friso dourado ornamental
        draw_voxel_box(surface, camera, cx - 0.52, cy - 0.40, 0.70, 1.04, 0.80, 0.08, COLOR_KYOTO_CARRIAGE_GOLD, outline=False)
        # Janela com treliça
        draw_voxel_box(surface, camera, cx - 0.53, cy - 0.20, 0.82, 1.06, 0.45, 0.32, (20, 16, 14), outline=True)

        # 4. Teto curvo da carruagem
        draw_voxel_box(surface, camera, cx - 0.60, cy - 0.65, 1.25, 1.20, 1.30, 0.18, (28, 20, 16), outline=True)
        draw_voxel_box(surface, camera, cx - 0.40, cy - 0.45, 1.40, 0.80, 0.90, 0.12, (38, 28, 22), outline=False)

        # 5. Lanternas da carruagem acesas
        draw_voxel_box(surface, camera, cx + 0.52, cy - 0.30, 0.75, 0.16, 0.16, 0.24, (255, 210, 80), outline=False)
        draw_voxel_box(surface, camera, cx - 0.68, cy - 0.30, 0.75, 0.16, 0.16, 0.24, (255, 210, 80), outline=False)

        # 6. Rodas Voxel com aro de ferro
        for ox, oy in [(-0.55, -0.45), (0.55, -0.45), (-0.55, 0.45), (0.55, 0.45)]:
            draw_voxel_box(surface, camera, cx + ox - 0.08, cy + oy - 0.12, 0.04, 0.16, 0.24, 0.38, (65, 48, 35), outline=True)

        # 7. Cavalo de tração galopando na frente ao longo da direção (+dir_y * 1.4)
        hx = cx + self.dir_x * 1.4
        hy = cy + self.dir_y * 1.4
        draw_voxel_box(surface, camera, hx - 0.35, hy - 0.45, 0.32, 0.70, 0.90, 0.58, COLOR_KYOTO_HORSE_DARK, outline=True)
        draw_voxel_box(surface, camera, hx - 0.20, hy + self.dir_y * 0.4 - 0.15, 0.75, 0.40, 0.45, 0.55, COLOR_KYOTO_HORSE_DARK, outline=True)
        draw_voxel_box(surface, camera, hx - 0.08, hy + self.dir_y * 0.3 - 0.10, 1.15, 0.16, 0.30, 0.20, (18, 14, 14), outline=False)
        draw_voxel_box(surface, camera, hx - 0.36, hy - 0.10, 0.45, 0.72, 0.10, 0.30, (140, 35, 25), outline=False)


class FallingDebris:
    """
    Pedaço de viga ou telhado em chamas caindo nas calçadas.
    Telegrafa uma sombra flamejante crescente no chão antes do impacto fatal.
    """
    def __init__(self, target_x: float, target_y: float):
        self.target_x = target_x
        self.target_y = target_y
        self.wz = 4.5
        self.fall_speed = 7.5
        self.is_active = True
        self.has_impacted = False
        self.warning_duration = 0.95
        self.timer = 0.0
        self.rubble_timer = 2.2
        self.radius = 1.05

    def update(self, dt: float, camera, particles: list, fighters: list, banners: list, cinematic_director=None) -> bool:
        if not self.is_active:
            return False

        self.timer += dt

        if self.timer < self.warning_duration:
            if random.random() < 0.4:
                particles.append(SparkParticle(
                    self.target_x + random.uniform(-0.3, 0.3),
                    self.target_y + random.uniform(-0.3, 0.3),
                    wz=0.05, color=COLOR_KYOTO_FIRE_MID
                ))
            return True

        if not self.has_impacted:
            self.wz -= self.fall_speed * dt
            if self.wz <= 0.0:
                self.wz = 0.0
                self.has_impacted = True
                self._trigger_impact(camera, particles, fighters, banners, cinematic_director)
            return True

        self.rubble_timer -= dt
        if random.random() < 0.25:
            particles.append(SparkParticle(self.target_x, self.target_y, wz=0.1, color=COLOR_KYOTO_EMBER))

        if self.rubble_timer <= 0:
            self.is_active = False
            return False

        return True

    def _trigger_impact(self, camera, particles: list, fighters: list, banners: list, cinematic_director=None):
        camera.add_shake(7.0)
        for _ in range(18):
            particles.append(SparkParticle(self.target_x, self.target_y, wz=0.2, color=COLOR_KYOTO_FIRE_MID))
            particles.append(SparkParticle(self.target_x, self.target_y, wz=0.3, color=COLOR_KYOTO_EMBER))

        for f in fighters:
            if f and f.is_alive:
                dist = world_distance(self.target_x, self.target_y, f.wx, f.wy)
                if dist < self.radius:
                    f.take_hit((0.0, 1.0), damage=99)
                    f.is_alive = False
                    for _ in range(20):
                        particles.append(BloodParticle(f.wx, f.wy, 0.6))
                    banners.append(FloatingBanner("CRUSHED BY DEBRIS!", f.wx, f.wy, wz=1.8, color=(255, 100, 30)))
                    if cinematic_director:
                        cinematic_director.trigger_fatal_strike(
                            None,
                            f,
                            death_style="KASUMI_EXPLODE",
                            slash_dir=(0.0, 1.0)
                        )

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return

        tx, ty = self.target_x, self.target_y
        sx, sy = camera.apply(tx, ty, 0.0)

        if self.timer < self.warning_duration:
            prog = min(1.0, self.timer / self.warning_duration)
            shadow_rad = int(20 + 16 * prog)
            pulse = math.sin(self.timer * 14.0)
            glow_col = (220, 60 + int(40 * pulse), 20)
            pygame.draw.ellipse(surface, (18, 12, 10), (sx - shadow_rad, sy - shadow_rad // 2, shadow_rad * 2, shadow_rad))
            pygame.draw.ellipse(surface, glow_col, (sx - shadow_rad + 4, sy - shadow_rad // 2 + 2, (shadow_rad - 4) * 2, shadow_rad - 4), 2)
            return

        draw_voxel_box(
            surface, camera,
            tx - 0.35, ty - 0.35, self.wz,
            0.70, 0.70, 0.35,
            COLOR_KYOTO_WOOD_BURNT, outline=True
        )
        draw_voxel_box(
            surface, camera,
            tx - 0.20, ty - 0.20, self.wz + 0.30,
            0.40, 0.40, 0.30,
            COLOR_KYOTO_FIRE_MID, outline=False
        )


class KyotoMap:
    """
    Arena de Kyoto durante a Guerra do Bakumatsu.
    Estrada estreita diagonal (4 tiles), fachadas geminadas de machiyas em chamas nos dois lados,
    chamas que nascem e somem organicamente nos telhados e perigos dinâmicos de carruagem e escombros.
    """
    def __init__(self):
        self.cols = MAP_COLS
        self.rows = MAP_ROWS
        self.theme_name = "Kyoto: Bakumatsu em Chamas"
        self.tiles = [[TILE_KYOTO_STREET for _ in range(self.rows)] for _ in range(self.cols)]

        self.bamboos = []
        self.rocks = []
        self.well = None
        self.trees = []

        self.buildings: list[MachiyaFacade] = []
        self.lanterns: list[KyotoLantern] = []
        self.carriages: list[RunawayCarriage] = []
        self.falling_debris: list[FallingDebris] = []

        self.carriage_timer = 2.5
        self.debris_timer = 1.2

        self._build_terrain()
        self._populate_buildings()

    def _build_terrain(self):
        """
        Gera uma estrada estreita de 4 tiles de granito ao longo do eixo Y isométrico (9 a 12),
        meio-fio em 8 e 13, calçadas em 7 e 14 e terrenos sob as estalagens em <= 6 e >= 15.
        """
        for x in range(self.cols):
            for y in range(self.rows):
                if 9 <= x <= 12:
                    self.tiles[x][y] = TILE_KYOTO_STREET if (x + y) % 2 == 0 else TILE_KYOTO_STREET_ALT
                elif x in (8, 13):
                    self.tiles[x][y] = TILE_KYOTO_CURB
                elif x in (7, 14):
                    self.tiles[x][y] = TILE_KYOTO_SIDEWALK
                else:
                    self.tiles[x][y] = TILE_KYOTO_BUILDING

    def _populate_buildings(self):
        """Cria as estalagens densas geminadas ao longo de ambos os lados da via e lanternas de pedra."""
        # 1. Canto Noroeste (NW - wx = 2.4): 6 Machiyas geminadas em chamas opacas
        for idx, by in enumerate([0.4, 3.9, 7.4, 10.9, 14.4, 17.9]):
            self.buildings.append(MachiyaFacade(
                wx=2.4, wy=by, width=4.4, depth=3.3,
                is_transparent=False, seed=100 + idx * 37
            ))

        # 2. Canto Sudeste (SE - wx = 15.0): 6 Machiyas geminadas translúcidas TAMBÉM em chamas
        for idx, by in enumerate([0.4, 3.9, 7.4, 10.9, 14.4, 17.9]):
            self.buildings.append(MachiyaFacade(
                wx=15.0, wy=by, width=4.4, depth=3.3,
                is_transparent=True, seed=200 + idx * 43
            ))

        # 3. Lanternas de pedra tradicionais nas calçadas
        for ly in [3.0, 8.5, 14.0, 19.5]:
            self.lanterns.append(KyotoLantern(7.30, ly))
            self.lanterns.append(KyotoLantern(14.25, ly))

    def is_water(self, wx: float, wy: float) -> bool:
        return False

    def is_hidden_in_bamboo(self, wx: float, wy: float) -> bool:
        return False

    def update(self, dt: float, fighters: list, camera, particles: list, banners: list, cinematic_director=None):
        # 1. Carruagens em disparada pela via (frequência elevada com chance de cruzamento duplo)
        self.carriage_timer -= dt
        if self.carriage_timer <= 0:
            # 40% de chance de duas carruagens simultâneas passando em sentidos opostos
            is_double = random.random() < 0.40

            if is_double:
                lane1_x = 9.8
                lane2_x = 11.2
                if random.random() < 0.5:
                    # Lane 1 desce (Norte -> Sul), Lane 2 sobe (Sul -> Norte)
                    c1 = RunawayCarriage((lane1_x, -4.0), (lane1_x, float(self.rows + 4)), speed=14.0)
                    c2 = RunawayCarriage((lane2_x, float(self.rows + 4)), (lane2_x, -4.0), speed=14.0)
                else:
                    # Lane 1 sobe (Sul -> Norte), Lane 2 desce (Norte -> Sul)
                    c1 = RunawayCarriage((lane1_x, float(self.rows + 4)), (lane1_x, -4.0), speed=14.0)
                    c2 = RunawayCarriage((lane2_x, -4.0), (lane2_x, float(self.rows + 4)), speed=14.0)

                self.carriages.append(c1)
                self.carriages.append(c2)
                banners.append(FloatingBanner("PERIGO DUPLO: CARRUAGENS CRUZADAS!", 10.5, 11.0, wz=2.5, color=(255, 60, 40), duration=2.5))
                camera.add_shake(7.0)
            else:
                # Carruagem única passando em uma das faixas da avenida
                lane_x = random.choice([9.8, 10.5, 11.2])
                if random.random() < 0.5:
                    start_p = (lane_x, -4.0)
                    end_p = (lane_x, float(self.rows + 4))
                else:
                    start_p = (lane_x, float(self.rows + 4))
                    end_p = (lane_x, -4.0)

                carriage = RunawayCarriage(start_p, end_p, speed=14.0)
                self.carriages.append(carriage)
                banners.append(FloatingBanner("PERIGO: CARRUAGEM!", lane_x, 11.0, wz=2.5, color=(255, 190, 40), duration=2.2))
                camera.add_shake(4.0)

            # Nova frequência de carruagens: a cada 4.0 a 6.5s (anteriormente 8.0 a 12.0s)
            self.carriage_timer = random.uniform(4.0, 6.5)

        for carriage in self.carriages:
            carriage.update(dt, camera, particles)
            for f in fighters:
                if f:
                    carriage.check_fighter_hit(f, particles, banners, camera, cinematic_director)

        self.carriages = [c for c in self.carriages if c.is_active]

        # 2. Escombros incandescentes caindo com maior frequência e possibilidade de queda dupla
        self.debris_timer -= dt
        if self.debris_timer <= 0:
            debris_count = 2 if random.random() < 0.35 else 1
            for _ in range(debris_count):
                if random.random() < 0.5:
                    target_x = random.uniform(7.4, 8.6)
                else:
                    target_x = random.uniform(12.4, 14.2)
                target_y = random.uniform(2.0, float(self.rows - 2.0))
                self.falling_debris.append(FallingDebris(target_x, target_y))

            # Nova frequência de escombros: a cada 1.2 a 2.4s (anteriormente 3.0 a 5.5s)
            self.debris_timer = random.uniform(1.2, 2.4)

        for debris in self.falling_debris:
            debris.update(dt, camera, particles, fighters, banners, cinematic_director)

        self.falling_debris = [d for d in self.falling_debris if d.is_active]

    def render_terrain(self, surface: pygame.Surface, camera, time_val: float):
        for x in range(self.cols):
            for y in range(self.rows):
                tile = self.tiles[x][y]

                p_top = camera.apply(x, y, 0.0)
                p_right = camera.apply(x + 1, y, 0.0)
                p_bottom = camera.apply(x + 1, y + 1, 0.0)
                p_left = camera.apply(x, y + 1, 0.0)
                quad = [p_top, p_right, p_bottom, p_left]

                if p_bottom[1] < -60 or p_top[1] > surface.get_height() + 60 or \
                   p_right[0] < -60 or p_left[0] > surface.get_width() + 60:
                    continue

                if tile == TILE_KYOTO_STREET:
                    c = COLOR_KYOTO_STONE if (x + y) % 2 == 0 else COLOR_KYOTO_STONE_LIGHT
                    pygame.draw.polygon(surface, c, quad)
                    pygame.draw.polygon(surface, COLOR_KYOTO_STONE_DARK, quad, 1)

                elif tile == TILE_KYOTO_STREET_ALT:
                    pygame.draw.polygon(surface, (54, 50, 52), quad)
                    pygame.draw.polygon(surface, COLOR_KYOTO_STONE_DARK, quad, 1)

                elif tile == TILE_KYOTO_CURB:
                    draw_voxel_box(surface, camera, x, y, 0.0, 1.0, 1.0, 0.10, COLOR_KYOTO_CURB, outline=True)

                elif tile == TILE_KYOTO_SIDEWALK:
                    draw_voxel_box(surface, camera, x, y, 0.0, 1.0, 1.0, 0.08, COLOR_KYOTO_PAVEMENT, outline=False)
                    pygame.draw.polygon(surface, (38, 34, 36), [
                        camera.apply(x, y, 0.08), camera.apply(x+1, y, 0.08),
                        camera.apply(x+1, y+1, 0.08), camera.apply(x, y+1, 0.08)
                    ], 1)

                elif tile == TILE_KYOTO_BUILDING:
                    pygame.draw.polygon(surface, (20, 15, 17), quad)
