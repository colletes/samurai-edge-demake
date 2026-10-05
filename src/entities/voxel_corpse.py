"""
Corpos abatidos: o modelo voxel atual do lutador é desenhado numa camada transparente, recortado em peças
conforme o golpe fatal e animado com a física 3D das peças (queda, rotação, quique).

Estilos: corte diagonal (KENSHIN_SPLIT), decapitação (MURASAKI_DECAP/CLEAN_DECAP), corte na cintura (PIRATE_CLEAVE),
explosão (KASUMI_EXPLODE), tiro na cabeça (HEADSHOT_EXPLODE), dissolução ácida (OKUNI_MELT), perfuração com a arma
cravada (SAITOU_IMPALE, KUNAI_PIN, ARROW_PIN, STAB_FALL), mordida (MAULED), esmagamento (CRUSHED) e queda simples
(BLUNT_FALL e o padrão).
"""
import math
import random
import numpy as np
import pygame
from src.config import COLOR_BLOOD
from src.isometric.voxel_renderer import draw_voxel_box

ALPHA_CUT = 200      # descarta sombras e auras translúcidas do recorte
NECK_Z = 0.88        # altura do pescoço nos modelos
WAIST_Z = 0.55       # altura da cintura nos modelos
CHEST_Z = 0.72
FALL_DEG = 88.0

STUCK_WEAPON = {"SAITOU_IMPALE": "blade", "KUNAI_PIN": "kunai", "ARROW_PIN": "arrow", "STAB_FALL": "kunai"}


class _LayerCamera:
    """Câmera que projeta como a original, mas com a origem deslocada para o canto da camada."""

    def __init__(self, camera, ox: int, oy: int):
        self._camera = camera
        self._ox = ox
        self._oy = oy

    def apply(self, wx, wy, wz=0.0):
        x, y = self._camera.apply(wx, wy, wz)
        return x - self._ox, y - self._oy

    def __getattr__(self, name):
        return getattr(self._camera, name)


def layer_geometry(zoom: float) -> tuple[int, int, int]:
    """Margens (esquerda/direita, acima, abaixo) da camada do lutador; as mesmas do contorno cel-shading."""
    return int(80 * zoom) + 6, int(105 * zoom) + 6, int(44 * zoom) + 6


def render_body_layer(camera, wx: float, wy: float, wz: float, draw):
    """Desenha o lutador com `draw(layer, layer_camera)`; devolve (camada limpa, camada-câmera, (left, up))."""
    left, up, down = layer_geometry(camera.zoom)
    ox, oy = camera.apply(wx, wy, wz)
    layer = pygame.Surface((2 * left, up + down), pygame.SRCALPHA)
    lc = _LayerCamera(camera, ox - left, oy - up)
    draw(layer, lc)
    solid = pygame.mask.from_surface(layer, ALPHA_CUT)
    return solid.to_surface(setsurface=layer, unsetcolor=(0, 0, 0, 0)), lc, (left, up)


def fall_factor(camera, wx: float, wy: float, dx: float, dy: float) -> float:
    """Sinal da rotação em tela (negativo = tomba para a direita); suave para a queda não inverter com o azimute."""
    a = camera.apply(wx, wy, 0.0)
    b = camera.apply(wx + dx, wy + dy, 0.0)
    sx, sy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(sx, sy) or 1.0
    g = max(-1.0, min(1.0, sx / n * 3.0))
    if abs(g) < 0.3:
        g = 0.3 if g >= 0 else -0.3
    return -g


def blit_rotated(surface: pygame.Surface, img: pygame.Surface, pivot_screen: tuple[float, float],
                 pivot_in_img: tuple[float, float], angle_deg: float):
    """Desenha `img` girada (anti-horário positivo) mantendo `pivot_in_img` fixo em `pivot_screen`."""
    w, h = img.get_size()
    vx, vy = pivot_in_img[0] - w / 2.0, pivot_in_img[1] - h / 2.0
    if abs(angle_deg) < 0.01:
        surface.blit(img, (pivot_screen[0] - pivot_in_img[0], pivot_screen[1] - pivot_in_img[1]))
        return
    rad = math.radians(angle_deg)
    rvx = vx * math.cos(rad) + vy * math.sin(rad)
    rvy = -vx * math.sin(rad) + vy * math.cos(rad)
    rotated = pygame.transform.rotate(img, angle_deg)
    surface.blit(rotated, rotated.get_rect(center=(pivot_screen[0] - rvx, pivot_screen[1] - rvy)))


def _cut(sprite: pygame.Surface, polygon):
    """Recorta `sprite` pelo polígono; devolve (superfície, canto superior esquerdo) ou None se ficar vazio."""
    mask_surf = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask_surf, (255, 255, 255, 255), polygon)
    piece = sprite.copy()
    piece.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    rects = pygame.mask.from_surface(piece, 10).get_bounding_rects()
    if not rects:
        return None
    rect = rects[0].unionall(rects[1:]) if len(rects) > 1 else rects[0]
    return piece.subsurface(rect).copy(), rect.topleft


def sample_colors(sprite: pygame.Surface, count: int, min_y: int = 0, max_y: int | None = None) -> list[tuple]:
    """Cores aleatórias dos pixels opacos do modelo (para os estilhaços combinarem com o lutador)."""
    h = sprite.get_height()
    max_y = h if max_y is None else max(min_y + 1, min(h, max_y))
    alpha = pygame.surfarray.array_alpha(sprite)[:, min_y:max_y]
    xs, ys = np.nonzero(alpha >= ALPHA_CUT)
    if len(xs) == 0:
        return []
    colors = []
    for i in np.random.randint(0, len(xs), count):
        c = sprite.get_at((int(xs[i]), int(ys[i]) + min_y))
        colors.append((c.r, c.g, c.b))
    return colors


def _draw_stuck(layer: pygame.Surface, kind: str, x: float, y: float, ax: float, ay: float):
    """Arma cravada no peito, com a ponta para fora voltada ao agressor (ax, ay = direção em tela)."""
    length = {"arrow": 18, "kunai": 9, "blade": 22}[kind]
    tail = (x + ax * length, y + ay * length)
    if kind == "arrow":
        pygame.draw.line(layer, (176, 132, 76), (x, y), tail, 2)
        for off in (0.0, 3.0):
            bx, by = tail[0] - ax * off, tail[1] - ay * off
            pygame.draw.line(layer, (236, 236, 226), (bx, by), (bx - ay * 3, by + ax * 3), 1)
            pygame.draw.line(layer, (236, 236, 226), (bx, by), (bx + ay * 3, by - ax * 3), 1)
    elif kind == "kunai":
        pygame.draw.line(layer, (190, 196, 206), (x, y), tail, 2)
        pygame.draw.circle(layer, (48, 48, 54), (int(tail[0]), int(tail[1])), 3, 1)
    else:
        pygame.draw.line(layer, (214, 219, 228), (x, y), tail, 3)
        hilt = (tail[0] - ax * 5, tail[1] - ay * 5)
        pygame.draw.line(layer, (70, 44, 34), hilt, tail, 4)


class _Ctx:
    """Medidas da camada do corpo para montar os polígonos de corte."""
    def __init__(self, corpse, lc, size, camera):
        self.w, self.h = size
        self.cx = lc.apply(corpse.wx, corpse.wy, corpse.wz)[0]
        self._lc = lc
        self._corpse = corpse
        self.ground_y = self.y_of(0.0)
        self.unit = max(1.0, self.ground_y - self.y_of(1.0))
        self.g = fall_factor(camera, corpse.wx, corpse.wy, corpse.dx, corpse.dy)

    def y_of(self, z: float) -> float:
        return self._lc.apply(self._corpse.wx, self._corpse.wy, self._corpse.wz + z)[1]

    def band(self, z_top: float | None, z_bottom: float | None):
        """Faixa horizontal entre duas alturas (None = sem limite)."""
        top = 0 if z_top is None else self.y_of(z_top)
        bottom = self.h if z_bottom is None else self.y_of(z_bottom)
        return [(0, top), (self.w, top), (self.w, bottom), (0, bottom)]

    def diagonal(self, upper: bool):
        """Corte que desce no sentido da queda (a metade de cima escorrega pelo corte)."""
        yc = self.y_of(0.62)
        slope = (self.y_of(0.42) - self.y_of(0.82)) / 36.0 * (1.0 if self.g < 0 else -1.0)
        yl, yr = yc - slope * self.cx, yc + slope * (self.w - self.cx)
        if upper:
            return [(0, 0), (self.w, 0), (self.w, yr), (0, yl)]
        return [(0, yl), (self.w, yr), (self.w, self.h), (0, self.h)]


class VoxelCorpsePiece:
    """Pedaço do corpo com física 3D de queda, rotação e quique; pode exibir um recorte do modelo do lutador."""
    def __init__(self, wx: float, wy: float, wz: float, size_x: float, size_y: float, size_z: float, color: tuple,
                 vx: float = 0.0, vy: float = 0.0, vz: float = 0.0, rot_speed: float = 0.0, piece_type: str = "gib",
                 region=None, pivot: str = "bottom", rot_target: float | None = None, rot_delay: float = 0.0,
                 floor_z: float = 0.02, squash: str | None = None):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.rest = (wx, wy, wz)
        self.sx = size_x
        self.sy = size_y
        self.sz = size_z
        self.color = color
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.rot_speed = rot_speed
        self.rot_angle = 0.0
        self.rot_target = rot_target
        self.rot_delay = rot_delay
        self.piece_type = piece_type
        self.is_grounded = False
        self.bounces = 0
        self.max_bounces = 2
        self.floor_z = floor_z
        self.region = region          # callable(_Ctx) -> polígono; None = peça de caixa simples
        self.pivot = pivot
        self.squash = squash          # "melt" (derrete) ou "crush" (achata) ao longo do tempo
        self.surf = None              # recorte atual do modelo (refeito quando a câmera muda)
        self.pivot_layer = (0.0, 0.0)
        self.pivot_img = (0.0, 0.0)
        self.age = 0.0

    def update(self, dt: float) -> bool:
        self.age += dt
        if self.rot_target is not None:
            if self.rot_delay > 0:
                self.rot_delay -= dt
            elif self.rot_angle < self.rot_target:
                self.rot_angle = min(self.rot_target, self.rot_angle + abs(self.rot_speed) * dt)
        if not self.is_grounded:
            self.wx += self.vx * dt
            self.wy += self.vy * dt
            self.wz += self.vz * dt
            self.vz -= 14.0 * dt  # Gravidade
            if self.rot_target is None:
                self.rot_angle += self.rot_speed * dt

            if self.wz <= self.floor_z:
                self.wz = self.floor_z
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

    def render_box(self, surface: pygame.Surface, camera):
        draw_voxel_box(surface, camera, self.wx - self.sx / 2, self.wy - self.sy / 2, self.wz, self.sx, self.sy, self.sz, self.color, outline=True)


class VoxelCorpse:
    """Corpo abatido: peças recortadas do modelo do lutador, animadas conforme o golpe fatal."""
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
        self._key = None
        self._left = self._up = 0
        self._sprite_failed = False
        self._gibs_recolored = False

        dx, dy = slash_dir
        mag = math.hypot(dx, dy)
        self.dx, self.dy = (dx / mag, dy / mag) if mag > 0.001 else (1.0, 0.0)

        # Cores anatômicas do guerreiro (usadas só se o recorte do modelo falhar)
        from src.entities.voxel_models import (
            _canonical_char_type, _get_char_torso_color, _get_char_pants_color, _get_char_hair_color
        )
        canonical = _canonical_char_type(self.char_type)
        self.col_torso = _get_char_torso_color(canonical)
        self.col_pants = _get_char_pants_color(canonical)
        self.col_hair = _get_char_hair_color(canonical)

        self._initialize_death_pieces()

    # ------------------------------------------------------------------ construção das peças
    def _initialize_death_pieces(self):
        """Gera as peças específicas do golpe fatal recebido."""
        dx, dy = self.dx, self.dy
        x, y = self.wx, self.wy
        style = self.death_style
        P = VoxelCorpsePiece

        if style == "KENSHIN_SPLIT":
            # Tronco superior escorrega pelo corte diagonal e tomba; as pernas desabam logo depois
            self.bottom_half = P(x, y, 0.0, 0.30, 0.22, 0.52, self.col_pants, piece_type="bottom",
                                 region=lambda c: c.diagonal(upper=False), rot_target=80.0, rot_speed=140.0, rot_delay=0.25)
            self.top_half = P(x, y, WAIST_Z, 0.28, 0.20, 0.50, self.col_torso, vx=dx * 2.8, vy=dy * 2.8, vz=1.8,
                              piece_type="top", region=lambda c: c.diagonal(upper=True), rot_target=100.0, rot_speed=260.0)
            self.pieces.extend([self.bottom_half, self.top_half])

        elif style in ("MURASAKI_DECAP", "CLEAN_DECAP"):
            self.headless_body = P(x, y, 0.0, 0.28, 0.22, 0.85, self.col_torso, piece_type="body",
                                   region=lambda c: c.band(NECK_Z, None), rot_target=FALL_DEG, rot_speed=110.0, rot_delay=0.35)
            self.severed_head = P(x, y, NECK_Z + 0.15, 0.16, 0.16, 0.16, self.col_hair,
                                  vx=dx * 2.2 + random.uniform(-0.5, 0.5), vy=dy * 2.2 + random.uniform(-0.5, 0.5),
                                  vz=3.8, rot_speed=320.0, piece_type="head", region=lambda c: c.band(None, NECK_Z),
                                  pivot="center", floor_z=0.15)
            self.pieces.extend([self.headless_body, self.severed_head])

        elif style == "KASUMI_EXPLODE":
            for _ in range(26):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2.5, 7.5)
                c = random.choice([self.col_torso, self.col_pants, (40, 42, 45), (180, 25, 30), (255, 140, 20)])
                sz = random.uniform(0.10, 0.18)
                self.pieces.append(P(x, y, random.uniform(0.2, 0.8), sz, sz, sz, c,
                                     vx=math.cos(angle) * speed, vy=math.sin(angle) * speed, vz=random.uniform(3.0, 7.0),
                                     rot_speed=random.uniform(-400, 400), piece_type="gib"))

        elif style == "OKUNI_MELT":
            self.acid_radius = 0.2
            self.acid_max_radius = 0.85
            self.pieces.append(P(x, y, 0.0, 0.40, 0.30, 0.70, (60, 180, 90), piece_type="melting_body",
                                 region=lambda c: c.band(None, None), squash="melt"))

        elif style in STUCK_WEAPON:
            # Perfurado: a arma fica cravada e o corpo é jogado para longe do agressor
            self.pieces.append(P(x, y, 0.0, 0.44, 0.34, 0.75, self.col_torso, vx=dx * 1.8, vy=dy * 1.8, vz=1.2,
                                 piece_type="impaled_body", region=lambda c: c.band(None, None),
                                 rot_target=FALL_DEG, rot_speed=170.0))

        elif style == "HEADSHOT_EXPLODE":
            self.pieces.append(P(x, y, 0.0, 0.42, 0.32, 0.65, self.col_torso, vx=dx * 0.8, vy=dy * 0.8, vz=0.2,
                                 piece_type="torso_headless", region=lambda c: c.band(NECK_Z, None),
                                 rot_target=FALL_DEG, rot_speed=120.0, rot_delay=0.1))
            for _ in range(14):
                angle = random.uniform(0, math.pi * 2)
                sp = random.uniform(1.8, 5.2)
                self.pieces.append(P(x, y, 0.85, 0.08, 0.08, 0.08, random.choice([self.col_hair, COLOR_BLOOD, (60, 60, 65)]),
                                     vx=math.cos(angle) * sp, vy=math.sin(angle) * sp, vz=random.uniform(1.5, 4.5),
                                     rot_speed=random.uniform(-300, 300), piece_type="skull_gib"))

        elif style == "PIRATE_CLEAVE":
            self.pieces.append(P(x, y, 0.0, 0.44, 0.32, 0.40, self.col_pants, vx=-dy * 1.2, vy=dx * 1.2, vz=0.5,
                                 piece_type="half_left", region=lambda c: c.band(WAIST_Z, None),
                                 rot_target=75.0, rot_speed=130.0, rot_delay=0.2))
            self.pieces.append(P(x, y, WAIST_Z, 0.44, 0.32, 0.42, self.col_torso, vx=dy * 1.5 + dx * 1.0, vy=-dx * 1.5 + dy * 1.0, vz=1.5,
                                 piece_type="half_right", region=lambda c: c.band(None, WAIST_Z),
                                 rot_target=105.0, rot_speed=240.0))

        elif style == "MAULED":
            # Derrubado pelo cão: jogado para trás com força
            self.pieces.append(P(x, y, 0.0, 0.45, 0.32, 0.70, self.col_torso, vx=dx * 3.4, vy=dy * 3.4, vz=1.6,
                                 piece_type="mauled_body", region=lambda c: c.band(None, None),
                                 rot_target=FALL_DEG, rot_speed=300.0))

        elif style == "CRUSHED":
            self.pieces.append(P(x, y, 0.0, 0.50, 0.36, 0.60, self.col_torso, piece_type="crushed_body",
                                 region=lambda c: c.band(None, None), squash="crush"))
            for _ in range(30):
                self._add_blood_drop(spread=0.9)

        else:
            # Padrão e BLUNT_FALL: tombo cinematográfico para trás
            self.pieces.append(P(x, y, 0.0, 0.45, 0.32, 0.70, self.col_torso, vx=dx * 1.4, vy=dy * 1.4, vz=0.8,
                                 piece_type="fallen_body", region=lambda c: c.band(None, None),
                                 rot_target=FALL_DEG, rot_speed=190.0))

    def _add_blood_drop(self, spread: float = 0.2):
        self.blood_droplets.append({
            "wx": self.wx + random.uniform(-spread, spread),
            "wy": self.wy + random.uniform(-spread, spread),
            "size": random.randint(3, 5),
            "color": random.choice([(140, 15, 20), (170, 20, 25), (110, 10, 15)])
        })

    # ------------------------------------------------------------------ recorte do modelo
    def _refresh_sprite(self, camera):
        """Redesenha o modelo do lutador e refaz os recortes quando a câmera muda (azimute/zoom)."""
        key = (round(camera.azimuth, 3), round(camera.zoom, 3), getattr(camera, "height_fn", None) is None)
        if key == self._key or self._sprite_failed:
            return
        victim = self.victim
        saved_state = victim.state
        victim.state = "DYING_FREEZE"
        try:
            sprite, lc, (left, up) = render_body_layer(camera, self.wx, self.wy, self.wz, victim.render)
        except Exception:
            self._sprite_failed = True
            return
        finally:
            victim.state = saved_state
        self._key = key
        self._left, self._up = left, up
        ctx = _Ctx(self, lc, sprite.get_size(), camera)

        stuck = STUCK_WEAPON.get(self.death_style)
        if stuck:
            a = camera.apply(self.wx, self.wy, 0.0)
            b = camera.apply(self.wx + self.dx, self.wy + self.dy, 0.0)
            n = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
            _draw_stuck(sprite, stuck, ctx.cx, ctx.y_of(CHEST_Z), -(b[0] - a[0]) / n, -(b[1] - a[1]) / n)

        for piece in self.pieces:
            if piece.region is None:
                continue
            cut = _cut(sprite, piece.region(ctx))
            if cut is None:
                piece.surf = None
                continue
            surf, (tx, ty) = cut
            w, h = surf.get_size()
            piece.surf = surf
            piece.pivot_img = (w / 2.0, h / 2.0) if piece.pivot == "center" else (w / 2.0, float(h))
            piece.pivot_layer = (tx + piece.pivot_img[0], ty + piece.pivot_img[1])

        if not self._gibs_recolored:
            self._gibs_recolored = True
            head_bottom = int(ctx.y_of(NECK_Z))
            for piece in self.pieces:
                if piece.piece_type in ("gib", "skull_gib"):
                    colors = sample_colors(sprite, 1, 0, head_bottom if piece.piece_type == "skull_gib" else None)
                    if colors:
                        piece.color = colors[0]

    # ------------------------------------------------------------------ simulação
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

    # ------------------------------------------------------------------ desenho
    @staticmethod
    def _squash_scale(piece: VoxelCorpsePiece) -> float:
        if piece.squash == "melt":
            return max(0.0, 1.0 - piece.age / 1.6)
        return max(0.22, 1.0 - piece.age / 0.18)

    def _draw_sprite_piece(self, surface: pygame.Surface, camera, piece: VoxelCorpsePiece, fall: float):
        ox, oy = camera.apply(self.wx, self.wy, self.wz)
        a0 = camera.apply(*piece.rest)
        a1 = camera.apply(piece.wx, piece.wy, piece.wz)
        px = ox + piece.pivot_layer[0] - self._left + (a1[0] - a0[0])
        py = oy + piece.pivot_layer[1] - self._up + (a1[1] - a0[1])
        img, pivot = piece.surf, piece.pivot_img

        if piece.squash:
            scale = self._squash_scale(piece)
            if scale <= 0.02:
                return
            w, h = img.get_size()
            wide = w if piece.squash == "melt" else int(w * (1.0 + (1.0 - scale) * 0.35))
            img = pygame.transform.scale(img, (wide, max(1, int(h * scale))))
            pivot = (img.get_width() / 2.0, float(img.get_height()))
            if piece.squash == "melt":
                img.fill((0, int(110 * (1.0 - scale)), int(30 * (1.0 - scale))), special_flags=pygame.BLEND_RGB_ADD)
            angle = 0.0
        else:
            angle = piece.rot_angle * fall
        blit_rotated(surface, img, (px, py), pivot, angle)

    def render(self, surface: pygame.Surface, camera):
        self._refresh_sprite(camera)

        # 1. Poças e manchas de sangue no chão (piso 2D)
        for d in self.blood_droplets:
            sx, sy = camera.apply(d["wx"], d["wy"], 0.01)
            pygame.draw.circle(surface, d["color"], (sx, sy), d["size"])

        # Poça de veneno de Okuni
        if self.death_style == "OKUNI_MELT" and hasattr(self, "acid_radius"):
            sx, sy = camera.apply(self.wx, self.wy, 0.02)
            rw = max(2, int(self.acid_radius * 48 * camera.zoom))
            rh = max(2, int(self.acid_radius * 24 * camera.zoom))
            acid_surf = pygame.Surface((rw * 2, rh * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(acid_surf, (40, 180, 90, 180), (0, 0, rw * 2, rh * 2))
            pygame.draw.ellipse(acid_surf, (120, 240, 140, 220), (rw // 2, rh // 2, rw, rh))
            surface.blit(acid_surf, (sx - rw, sy - rh))

        # Marca de queimado sob os estilhaços da explosão
        if self.death_style == "KASUMI_EXPLODE":
            sx, sy = camera.apply(self.wx, self.wy, 0.01)
            scorch = pygame.Surface((int(76 * camera.zoom), int(36 * camera.zoom)), pygame.SRCALPHA)
            pygame.draw.ellipse(scorch, (18, 16, 16, 150), scorch.get_rect())
            surface.blit(scorch, (sx - scorch.get_width() // 2, sy - scorch.get_height() // 2))

        # 2. Peças: recortes do modelo e estilhaços em voxel 3D, do fundo para a frente
        fall = fall_factor(camera, self.wx, self.wy, self.dx, self.dy)
        for p in sorted(self.pieces, key=lambda q: (camera.depth(q.wx, q.wy), q.wz)):
            if p.region is not None and p.surf is not None:
                self._draw_sprite_piece(surface, camera, p, fall)
            elif p.region is None or self._sprite_failed:
                p.render_box(surface, camera)


def draw_fallen_model(surface: pygame.Surface, camera, wx: float, wy: float, wz: float, facing_x: float, facing_y: float, draw) -> bool:
    """Corpo caído sem cinemática (ex.: tiro de canhão): o próprio modelo deitado, de costas para onde olhava."""
    try:
        sprite, lc, (left, up) = render_body_layer(camera, wx, wy, wz, draw)
    except Exception:
        return False
    rects = pygame.mask.from_surface(sprite, 10).get_bounding_rects()
    if not rects:
        return False
    rect = rects[0].unionall(rects[1:]) if len(rects) > 1 else rects[0]
    mag = math.hypot(facing_x, facing_y) or 1.0
    fall = fall_factor(camera, wx, wy, -facing_x / mag, -facing_y / mag)
    body = sprite.subsurface(rect).copy()
    ox, oy = camera.apply(wx, wy, wz)
    pivot = (ox + rect.centerx - left, oy + rect.bottom - up)
    blit_rotated(surface, body, pivot, (rect.w / 2.0, float(rect.h)), FALL_DEG * fall)
    return True
