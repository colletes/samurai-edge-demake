"""
Módulo de corpos fatiados, desmembramentos e física de violência em Voxel 3D.
Suporta corte bipartido (Kenshin), decapitação (Murasaki), desintegração em gibs (Kasumi),
perfuração transfixante (Saitou), derretimento ácido (Okuni) e empalação.
"""
import math
import random
import pygame
from src.config import COLOR_BLOOD, COLOR_STEEL, COLOR_GOLD, COLOR_WHITE
from src.isometric.voxel_renderer import draw_voxel_box

class VoxelCorpsePiece:
    """Pedaço anatômico individual em voxel com física 3D de queda, rotação e quique."""
    def __init__(self, wx: float, wy: float, wz: float, size_x: float, size_y: float, size_z: float, color: tuple,
                 vx: float = 0.0, vy: float = 0.0, vz: float = 0.0, rot_speed: float = 0.0, piece_type: str = "gib"):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.sx = size_x
        self.sy = size_y
        self.sz = size_z
        self.color = color
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.rot_speed = rot_speed
        self.rot_angle = 0.0
        self.piece_type = piece_type
        self.is_grounded = False
        self.bounces = 0
        self.max_bounces = 2

    def update(self, dt: float) -> bool:
        if not self.is_grounded:
            self.wx += self.vx * dt
            self.wy += self.vy * dt
            self.wz += self.vz * dt
            self.vz -= 14.0 * dt  # Gravidade
            self.rot_angle += self.rot_speed * dt

            if self.wz <= 0.02:
                self.wz = 0.02
                self.bounces += 1
                if self.bounces <= self.max_bounces and abs(self.vz) > 1.0:
                    self.vz = -self.vz * 0.40
                    self.vx *= 0.65
                    self.vy *= 0.65
                else:
                    self.is_grounded = True
                    self.vz = 0.0
                    self.vx = 0.0
                    self.vy = 0.0
        return True

    def render(self, surface: pygame.Surface, camera):
        draw_voxel_box(surface, camera, self.wx - self.sx / 2, self.wy - self.sy / 2, self.wz, self.sx, self.sy, self.sz, self.color, outline=True)


class VoxelCorpse:
    """
    Entidade completa de corpo fatiado/destruído que gerencia a morte cinematográfica.
    """
    def __init__(self, victim, death_style: str, slash_dir: tuple[float, float] = (1.0, 0.0)):
        self.victim = victim
        self.wx = victim.wx
        self.wy = victim.wy
        self.wz = victim.wz
        self.death_style = death_style
        self.slash_dir = slash_dir
        self.char_type = getattr(victim, "char_type", "kenshin")
        self.pieces: list[VoxelCorpsePiece] = []
        self.blood_droplets: list[dict] = []  # Sangue que escorre e mancha o piso
        self.timer = 0.0
        self.delayed_action_done = False
        self.geyser_timer = 0.0

        # Cores anatômicas do guerreiro
        from src.entities.voxel_models import (
            _get_char_torso_color, _get_char_pants_color, _get_char_hair_color
        )
        self.col_torso = _get_char_torso_color(self.char_type)
        self.col_pants = _get_char_pants_color(self.char_type)
        self.col_hair = _get_char_hair_color(self.char_type)

        self._initialize_death_pieces()

    def _initialize_death_pieces(self):
        """Gera as peças anatômicas específicas dependendo do golpe fatal recebido."""
        dx, dy = self.slash_dir
        mag = math.hypot(dx, dy)
        if mag > 0.001:
            dx /= mag; dy /= mag
        else:
            dx, dy = 1.0, 0.0

        if self.death_style == "KENSHIN_SPLIT":
            # 1. Kenshi Split: Tronco superior escorrega diagonalmente e tomba
            # Metade Inferior (Pernas articuladas + cintura)
            self.bottom_half = VoxelCorpsePiece(
                self.wx, self.wy, 0.0, 0.30, 0.22, 0.52, self.col_pants,
                vx=0.0, vy=0.0, vz=0.0, piece_type="bottom"
            )
            # Metade Superior (Tronco superior + cabeça cortados em ângulo)
            self.top_half = VoxelCorpsePiece(
                self.wx, self.wy, 0.52, 0.28, 0.20, 0.50, self.col_torso,
                vx=dx * 2.8, vy=dy * 2.8, vz=1.8, rot_speed=90.0, piece_type="top"
            )
            self.pieces.extend([self.bottom_half, self.top_half])

        elif self.death_style in ("MURASAKI_DECAP", "CLEAN_DECAP"):
            # 2. Murasaki: Decapitação limpa com a cabeça saltando no ar e rolando
            self.headless_body = VoxelCorpsePiece(
                self.wx, self.wy, 0.0, 0.28, 0.22, 0.85, self.col_torso,
                vx=0.0, vy=0.0, vz=0.0, piece_type="body"
            )
            self.severed_head = VoxelCorpsePiece(
                self.wx, self.wy, 0.90, 0.16, 0.16, 0.16, self.col_hair,
                vx=dx * 2.2 + random.uniform(-0.5, 0.5), vy=dy * 2.2 + random.uniform(-0.5, 0.5),
                vz=3.8, rot_speed=320.0, piece_type="head"
            )
            self.pieces.extend([self.headless_body, self.severed_head])

        elif self.death_style == "KASUMI_EXPLODE":
            # 3. Kasumi (Bomba): Corpo desintegrado em dezenas de fragmentos chamuscados
            for _ in range(26):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2.5, 7.5)
                c = random.choice([self.col_torso, self.col_pants, (40, 42, 45), (180, 25, 30), (255, 140, 20)])
                sz = random.uniform(0.10, 0.18)
                self.pieces.append(VoxelCorpsePiece(
                    self.wx, self.wy, random.uniform(0.2, 0.8), sz, sz, sz, c,
                    vx=math.cos(angle) * speed, vy=math.sin(angle) * speed, vz=random.uniform(3.0, 7.0),
                    rot_speed=random.uniform(-400, 400), piece_type="gib"
                ))

        elif self.death_style == "OKUNI_MELT":
            # 4. Okuni (Veneno): Dissolução em poça cáustica verde-ácida
            self.acid_radius = 0.2
            self.acid_max_radius = 0.85
            self.pieces.append(VoxelCorpsePiece(
                self.wx, self.wy, 0.05, 0.45, 0.35, 0.20, (60, 180, 90),
                vx=0, vy=0, vz=0, piece_type="acid_core"
            ))

        elif self.death_style == "SAITOU_IMPALE":
            # 5. Saitou (Gatotsu): Perfuração transfixante torácica e tombo de costas
            self.pieces.append(VoxelCorpsePiece(
                self.wx, self.wy, 0.0, 0.44, 0.34, 0.75, self.col_torso,
                vx=-dx * 1.8, vy=-dy * 1.8, vz=1.2, rot_speed=-45.0, piece_type="impaled_body"
            ))

        elif self.death_style == "HEADSHOT_EXPLODE":
            # 6. Tanegashima (Tiro): Headshot explosivo
            self.pieces.append(VoxelCorpsePiece(
                self.wx, self.wy, 0.0, 0.42, 0.32, 0.65, self.col_torso,
                vx=-dx * 0.8, vy=-dy * 0.8, vz=0.2, piece_type="torso_headless"
            ))
            for _ in range(14):
                angle = random.uniform(0, math.pi * 2)
                sp = random.uniform(1.8, 5.2)
                self.pieces.append(VoxelCorpsePiece(
                    self.wx, self.wy, 0.85, 0.08, 0.08, 0.08, random.choice([self.col_hair, COLOR_BLOOD, (60, 60, 65)]),
                    vx=math.cos(angle) * sp, vy=math.sin(angle) * sp, vz=random.uniform(1.5, 4.5),
                    rot_speed=random.uniform(-300, 300), piece_type="skull_gib"
                ))

        elif self.death_style == "PIRATE_CLEAVE":
            # 7. Pirata (Anne): Corte horizontal ao meio
            self.pieces.append(VoxelCorpsePiece(
                self.wx, self.wy, 0.0, 0.44, 0.32, 0.40, self.col_pants,
                vx=-dy * 1.2, vy=dx * 1.2, vz=0.5, piece_type="half_left"
            ))
            self.pieces.append(VoxelCorpsePiece(
                self.wx, self.wy, 0.42, 0.44, 0.32, 0.42, self.col_torso,
                vx=dy * 1.5, vy=-dx * 1.5, vz=1.5, rot_speed=120.0, piece_type="half_right"
            ))

        else:
            # Padrão: Tombo cinematográfico para trás
            self.pieces.append(VoxelCorpsePiece(
                self.wx, self.wy, 0.0, 0.45, 0.32, 0.70, self.col_torso,
                vx=-dx * 1.4, vy=-dy * 1.4, vz=0.8, rot_speed=-60.0, piece_type="fallen_body"
            ))

    def update(self, dt: float, game_map, particles: list = None):
        self.timer += dt

        # Spawn de geiser de sangue contínuo nos primeiros momentos da morte
        if self.timer < 1.2 and particles is not None:
            self.geyser_timer += dt
            if self.geyser_timer > 0.04:
                self.geyser_timer = 0.0
                from src.effects.particles import BloodParticle
                for _ in range(4):
                    bx = self.wx + random.uniform(-0.15, 0.15)
                    by = self.wy + random.uniform(-0.15, 0.15)
                    bz = 0.5 + random.uniform(0.0, 0.4)
                    particles.append(BloodParticle(bx, by, bz))

        # Atualizar física das peças individuais
        for p in self.pieces:
            p.update(dt)
            # Pedaços rolando deixam marcas de sangue no chão
            if not p.is_grounded and random.random() < 0.25:
                self.blood_droplets.append({
                    "wx": p.wx + random.uniform(-0.1, 0.1),
                    "wy": p.wy + random.uniform(-0.1, 0.1),
                    "size": random.randint(3, 5),
                    "color": random.choice([(140, 15, 20), (170, 20, 25), (110, 10, 15)])
                })

        # Expansão de poça ácida para Okuni
        if self.death_style == "OKUNI_MELT" and hasattr(self, "acid_radius"):
            if self.acid_radius < self.acid_max_radius:
                self.acid_radius += dt * 0.35

    def render(self, surface: pygame.Surface, camera):
        # 1. Poças e manchas de sangue no chão (piso 2D)
        for d in self.blood_droplets:
            sx, sy = camera.apply(d["wx"], d["wy"], 0.01)
            pygame.draw.circle(surface, d["color"], (sx, sy), d["size"])

        # Poça de veneno de Okuni
        if self.death_style == "OKUNI_MELT" and hasattr(self, "acid_radius"):
            sx, sy = camera.apply(self.wx, self.wy, 0.02)
            rw = int(self.acid_radius * 48)
            rh = int(self.acid_radius * 24)
            pygame.draw.ellipse(surface, (40, 180, 90, 180), (sx - rw, sy - rh, rw * 2, rh * 2))
            pygame.draw.ellipse(surface, (120, 240, 140), (sx - rw // 2, sy - rh // 2, rw, rh))

        # 2. Peças volumétricas em Voxel 3D
        for p in self.pieces:
            p.render(surface, camera)
