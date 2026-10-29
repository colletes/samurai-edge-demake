"""
Sistema Geométrico de Hitboxes (Cápsula, Arco Setorial e Radial) + Inspetor Visual F3
e Alinhamento Magnético de Finishers para Samurai Edge — Bakumatsu (Fase M-2.3).
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import pygame


def _point_to_segment_dist(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    """Menor distância no plano do mundo entre o ponto (px, py) e o segmento (ax, ay)-(bx, by)."""
    abx = bx - ax
    aby = by - ay
    ab_len_sq = abx * abx + aby * aby
    if ab_len_sq < 1e-8:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * abx + (py - ay) * aby) / ab_len_sq))
    proj_x = ax + t * abx
    proj_y = ay + t * aby
    return math.hypot(px - proj_x, py - proj_y)


@dataclass
class CapsuleHitbox:
    """Hitbox em cápsula (segmento de reta + raio) ideal para estocadas, lanças e projéteis."""
    ax: float
    ay: float
    bx: float
    by: float
    radius: float
    z_min: float = 0.0
    z_max: float = 1.15

    def intersects_circle(self, tx: float, ty: float, tr: float) -> bool:
        return _point_to_segment_dist(tx, ty, self.ax, self.ay, self.bx, self.by) <= (self.radius + tr)


@dataclass
class ArcSectorHitbox:
    """Hitbox em setor de arco (varredura de espada/alfanje/naginata/kuwa)."""
    ox: float
    oy: float
    fx: float
    fy: float
    reach: float
    half_angle_rad: float
    inner_radius: float = 0.0
    z_min: float = 0.0
    z_max: float = 1.15

    def intersects_circle(self, tx: float, ty: float, tr: float) -> bool:
        dx = tx - self.ox
        dy = ty - self.oy
        dist = math.hypot(dx, dy)
        if dist > self.reach + tr:
            return False
        if dist < max(0.0, self.inner_radius - tr):
            return False
        if dist < 1e-5 or tr >= dist:
            return True
        fn = math.hypot(self.fx, self.fy) or 1.0
        ux, uy = self.fx / fn, self.fy / fn
        dot = max(-1.0, min(1.0, (dx * ux + dy * uy) / dist))
        ang = math.acos(dot)
        # Margem angular proporcional ao raio do alvo
        ang_margin = math.asin(min(1.0, tr / max(dist, 1e-4)))
        return ang <= (self.half_angle_rad + ang_margin)


@dataclass
class RadialHitbox:
    """Hitbox radial 360° (explosões, Kiai, pisotão sísmico, giros completos)."""
    cx: float
    cy: float
    radius: float
    z_min: float = 0.0
    z_max: float = 1.25

    def intersects_circle(self, tx: float, ty: float, tr: float) -> bool:
        return math.hypot(tx - self.cx, ty - self.cy) <= (self.radius + tr)


def build_fighter_melee_hitbox(fighter):
    """
    Constrói a primitiva geométrica de hitbox (CapsuleHitbox, ArcSectorHitbox ou RadialHitbox)
    correspondente à arma e ao golpe ativo do lutador.
    """
    hx, hy = getattr(fighter, "hitbox_center", (fighter.wx, fighter.wy))
    hr = float(getattr(fighter, "hitbox_radius", 0.8))
    fx = float(getattr(fighter, "facing_x", 1.0))
    fy = float(getattr(fighter, "facing_y", 0.0))
    fn = math.hypot(fx, fy) or 1.0
    fx, fy = fx / fn, fy / fn
    char_type = getattr(fighter, "char_type", "").lower()
    state = getattr(fighter, "state", "")

    # 1. Golpes de Estocada Linear -> CapsuleHitbox ao longo da lâmina/haste
    if state in ("GATOTSU_CHARGE", "ZEROSHIKI", "FLECHE", "COUNTER_THRUST") or char_type in ("saitou", "musketeer", "julie"):
        reach = math.hypot(hx - fighter.wx, hy - fighter.wy) + hr * 0.55
        return CapsuleHitbox(
            ax=fighter.wx + fx * 0.15,
            ay=fighter.wy + fy * 0.15,
            bx=fighter.wx + fx * max(0.65, reach),
            by=fighter.wy + fy * max(0.65, reach),
            radius=max(0.42, hr * 0.78),
        )

    # 2. Golpes Radiais 360° -> RadialHitbox
    if state in ("EARTH_STOMP", "KIAI", "WHIRLWIND"):
        return RadialHitbox(cx=hx, cy=hy, radius=hr)

    # 3. Golpes de Corte em Arco -> ArcSectorHitbox
    center_dist = math.hypot(hx - fighter.wx, hy - fighter.wy)
    reach = center_dist + hr
    half_angle = math.radians(85.0 if char_type in ("pirate", "anne", "benkei", "goro") else 68.0)
    return ArcSectorHitbox(
        ox=fighter.wx,
        oy=fighter.wy,
        fx=fx,
        fy=fy,
        reach=reach,
        half_angle_rad=half_angle,
    )


def check_fighter_melee_hit(attacker, target_wx: float, target_wy: float, target_radius: float) -> bool:
    """
    Avalia colisão melee combinando a hitbox geométrica (Cápsula/Arco/Radial) com o círculo
    de compatibilidade `hitbox_center`/`hitbox_radius`.
    """
    hx, hy = attacker.hitbox_center
    if math.hypot(hx - target_wx, hy - target_wy) < (attacker.hitbox_radius + target_radius):
        return True
    shape = build_fighter_melee_hitbox(attacker)
    return shape.intersects_circle(target_wx, target_wy, target_radius)


def align_finisher_pair(attacker, victim, game_map=None) -> None:
    """
    Alinhamento magnético de Finisher (Fase M-2.3):
    Quando um golpe melee fatal conecta, ajusta suavemente o espaçamento e a orientação entre
    atacante e vítima para que a lâmina atravesse exatamente o plano anatômico do corte sem
    desalinhamento ("cortar o vento") e sem empurrar nenhum lutador para fora da arena.
    """
    if attacker is None or victim is None:
        return
    dx = victim.wx - attacker.wx
    dy = victim.wy - attacker.wy
    dist = math.hypot(dx, dy)
    if dist < 1e-4 or dist > 2.8:
        # Não reposiciona abates à distância (projéteis/tiros)
        return

    # Garante que lutadores aéreos aterrissem com firmeza no chão para a execução do finisher
    if getattr(attacker, "wz", 0.0) > 0.0:
        attacker.wz = 0.0
        if hasattr(attacker, "vz"):
            attacker.vz = 0.0
    if getattr(victim, "wz", 0.0) > 0.0:
        victim.wz = 0.0
        if hasattr(victim, "vz"):
            victim.vz = 0.0

    ux, uy = dx / dist, dy / dist
    char_type = getattr(attacker, "char_type", "").lower()
    ideal_dist = 1.32 if char_type in ("benkei", "goro", "saitou", "musketeer", "julie") else 1.08

    # Move a vítima suavemente (blend 65%) para a distância ideal na linha do golpe
    target_vx = attacker.wx + ux * ideal_dist
    target_vy = attacker.wy + uy * ideal_dist
    new_vx = victim.wx * 0.35 + target_vx * 0.65
    new_vy = victim.wy * 0.35 + target_vy * 0.65

    if game_map is not None:
        cols = getattr(game_map, "cols", 22)
        rows = getattr(game_map, "rows", 22)
        new_vx = max(1.2, min(cols - 1.2, new_vx))
        new_vy = max(1.2, min(rows - 1.2, new_vy))

    victim.wx = new_vx
    victim.wy = new_vy
    attacker.set_facing(victim.wx, victim.wy)
    if hasattr(victim, "set_facing"):
        victim.set_facing(attacker.wx, attacker.wy)


class HitboxDebugInspector:
    """
    Inspetor visual de Hitboxes/Hurtboxes/Parry ativado via tecla F3 (Fase M-2.3):
    - Verde: Hurtbox 3D do corpo do lutador
    - Vermelho: Hitbox ativa da arma (Cápsula, Setor de Arco ou Radial)
    - Ciano: Janela ativa de Parry / Deflexão / Contra-ataque
    """

    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def render(self, surface: pygame.Surface, camera, fighters: list, projectiles: list | None = None) -> None:
        if not self.enabled:
            return

        for f in fighters:
            if f is None or not getattr(f, "is_alive", False):
                continue
            wz = getattr(f, "wz", 0.0)
            radius = getattr(f, "radius", 0.38)

            # 1. Hurtbox (Cilindro isométrico verde)
            self._draw_iso_circle(surface, camera, f.wx, f.wy, wz + 0.02, radius, (60, 235, 100), width=1)
            self._draw_iso_circle(surface, camera, f.wx, f.wy, wz + 0.95, radius, (60, 235, 100), width=1)

            # 2. Janela de Parry / Contra-Ataque (Anel Ciano)
            if getattr(f, "state", "") in ("PARRY", "MAI_DANCE", "LISTEN", "CAPE_FLOURISH") or getattr(f, "counter_active", False):
                self._draw_iso_circle(surface, camera, f.wx, f.wy, wz + 0.50, radius + 0.22, (70, 220, 255), width=2)

            # 3. Hitbox de Ataque Ativa (Vermelho)
            if getattr(f, "hitbox_active", False):
                shape = build_fighter_melee_hitbox(f)
                self._draw_hitbox_shape(surface, camera, shape, wz + 0.55, (255, 65, 65))

        if projectiles:
            for p in projectiles:
                if getattr(p, "is_active", False):
                    pr = getattr(p, "radius", 0.25)
                    pz = getattr(p, "wz", 0.5)
                    self._draw_iso_circle(surface, camera, p.wx, p.wy, pz, pr, (255, 180, 50), width=1)

    @staticmethod
    def _draw_iso_circle(surface: pygame.Surface, camera, wx: float, wy: float, wz: float, radius: float,
                         color: tuple[int, int, int], width: int = 1, segments: int = 16) -> None:
        pts = []
        for i in range(segments):
            ang = (2.0 * math.pi * i) / segments
            px = wx + math.cos(ang) * radius
            py = wy + math.sin(ang) * radius
            pts.append(camera.apply(px, py, wz))
        if len(pts) >= 3:
            pygame.draw.polygon(surface, color, pts, width)

    def _draw_hitbox_shape(self, surface: pygame.Surface, camera, shape, wz: float, color: tuple[int, int, int]) -> None:
        if isinstance(shape, CapsuleHitbox):
            p0 = camera.apply(shape.ax, shape.ay, wz)
            p1 = camera.apply(shape.bx, shape.by, wz)
            pygame.draw.line(surface, color, p0, p1, 2)
            self._draw_iso_circle(surface, camera, shape.ax, shape.ay, wz, shape.radius, color, width=1, segments=12)
            self._draw_iso_circle(surface, camera, shape.bx, shape.by, wz, shape.radius, color, width=2, segments=12)
        elif isinstance(shape, ArcSectorHitbox):
            base_ang = math.atan2(shape.fy, shape.fx)
            pts = [camera.apply(shape.ox, shape.oy, wz)]
            steps = 12
            for i in range(steps + 1):
                a = base_ang - shape.half_angle_rad + (2.0 * shape.half_angle_rad * i) / steps
                pts.append(camera.apply(shape.ox + math.cos(a) * shape.reach, shape.oy + math.sin(a) * shape.reach, wz))
            if len(pts) >= 3:
                pygame.draw.polygon(surface, color, pts, 2)
        elif isinstance(shape, RadialHitbox):
            self._draw_iso_circle(surface, camera, shape.cx, shape.cy, wz, shape.radius, color, width=2, segments=18)
