"""
Entregável 8.2.1: modelo voxel do Oni Gashadokuro.

O esqueleto tem um conjunto FIXO de 31 ossos (cada um é uma fileira de cubos entre dois pontos do mundo). As 5 fases só
mudam a disposição dos mesmos ossos (`layout_*`); os ossos perdidos viram entulho no chão em vez de sumir, então a
quantidade de partes é a mesma em todas as fases. Todas as funções de disposição recebem um `Frame` e devolvem
`{id_do_osso: (ponto_a, ponto_b)}` em coordenadas do mundo (x, y, z).
"""
import math
import random
from dataclasses import dataclass

from src.isometric.voxel_renderer import draw_voxel_box

BONE = (226, 218, 188)
BONE_DARK = (186, 174, 144)
RUST = (130, 76, 50)
STEEL = (170, 174, 178)
HANDLE = (94, 64, 46)
EYE = (255, 72, 42)

TRANSFORM_TIME = 2.5
COLLAPSE_TIME = 3.2


@dataclass(frozen=True)
class Bone:
    id: str
    thick: float
    color: tuple


BONES = (
    Bone("skull", 0.95, BONE), Bone("jaw", 0.55, BONE_DARK), Bone("eye_l", 0.24, EYE), Bone("eye_r", 0.24, EYE),
    *[Bone(f"spine{i}", 0.42, RUST if i >= 4 else BONE) for i in range(6)],
    *[Bone(f"rib_l{i}", 0.2, BONE_DARK) for i in range(4)],
    *[Bone(f"rib_r{i}", 0.2, BONE_DARK) for i in range(4)],
    Bone("pelvis", 0.7, RUST),
    Bone("arm_l_up", 0.34, BONE), Bone("arm_l_low", 0.3, BONE), Bone("arm_r_up", 0.34, BONE), Bone("arm_r_low", 0.3, BONE),
    Bone("blade", 0.26, STEEL), Bone("handle", 0.3, HANDLE),
    Bone("leg_l_up", 0.42, BONE), Bone("leg_l_low", 0.36, BONE), Bone("leg_r_up", 0.42, BONE), Bone("leg_r_low", 0.36, BONE),
    Bone("foot_l", 0.4, BONE_DARK), Bone("foot_r", 0.4, BONE_DARK),
)
BONE_BY_ID = {b.id: b for b in BONES}
BONE_COUNT = len(BONES)

_HEAD = ("skull", "jaw", "eye_l", "eye_r")
_RIGHT_LEG = ("leg_r_up", "leg_r_low", "foot_r")
_LEFT_LEG = ("leg_l_up", "leg_l_low", "foot_l")
# Ossos que viram entulho a partir de cada fase (índice 0 a 4); cumulativo
DEBRIS_BY_PHASE = (
    (),
    _RIGHT_LEG,
    _RIGHT_LEG + _LEFT_LEG,
    _RIGHT_LEG + _LEFT_LEG + ("arm_l_up", "arm_l_low", "blade", "handle"),
    tuple(b.id for b in BONES if b.id not in _HEAD),
)


class Frame:
    """Referencial do chefe: origem no chão sob ele, `f` para a frente, `s` para a esquerda, `h` para cima."""

    def __init__(self, x: float, y: float, z: float, fx: float, fy: float):
        self.x, self.y, self.z = x, y, z
        n = math.hypot(fx, fy) or 1.0
        self.fx, self.fy = fx / n, fy / n

    def w(self, f: float, s: float, h: float) -> tuple[float, float, float]:
        return (self.x + f * self.fx - s * self.fy, self.y + f * self.fy + s * self.fx, self.z + h)


def _pt(bone_pair):
    return bone_pair


def _single(p):
    return (p, p)


def layout_stand(fr: Frame, pose: dict) -> dict:
    """Fase 1: esqueleto de pé com o facão no braço direito (pose: t, stomp 0..1, sweep em radianos ou None)."""
    L = fr.w
    out = {}
    hip_h = 2.5 + 0.04 * math.sin(pose.get("t", 0.0) * 2.0)
    stomp = pose.get("stomp", 0.0)
    for side, k in ((1, "l"), (-1, "r")):
        lift = stomp if side == 1 else 0.0
        hip = L(0, side * 0.5, hip_h)
        knee = L(0.25 + lift * 0.7, side * 0.55, 1.3 + lift * 1.0)
        ankle = L(0.1 + lift * 1.0, side * 0.55, 0.35 + lift * 1.9)
        toe = L(0.7 + lift * 1.0, side * 0.55, 0.15 + lift * 1.8)
        out[f"leg_{k}_up"], out[f"leg_{k}_low"], out[f"foot_{k}"] = (hip, knee), (knee, ankle), (ankle, toe)
    out["pelvis"] = (L(0, -0.4, hip_h), L(0, 0.4, hip_h))
    step = 1.5 / 6
    for i in range(6):
        out[f"spine{i}"] = (L(0, 0, hip_h + 0.1 + i * step), L(0, 0, hip_h + 0.1 + (i + 1) * step))
    for i in range(4):
        h = hip_h + 0.7 + i * 0.3
        w = 0.85 + 0.12 * math.sin(i * 1.2 + 0.3)
        out[f"rib_l{i}"] = (L(0, 0.1, h), L(0.1, w, h - 0.25))
        out[f"rib_r{i}"] = (L(0, -0.1, h), L(0.1, -w, h - 0.25))
    neck_h = hip_h + 1.6
    sk = neck_h + 0.55
    out["skull"] = _single(L(0.1, 0, sk))
    out["jaw"] = (L(0.4, 0, sk - 0.55), L(0.25, 0, sk - 0.5))
    out["eye_l"] = _single(L(0.62, 0.22, sk + 0.1))
    out["eye_r"] = _single(L(0.62, -0.22, sk + 0.1))
    sh = neck_h - 0.15
    out["arm_l_up"] = (L(0, 0.7, sh), L(0.25, 1.0, sh - 0.9))
    out["arm_l_low"] = (L(0.25, 1.0, sh - 0.9), L(0.8, 0.9, sh - 1.6))
    sweep = pose.get("sweep")
    shoulder = L(0, -0.7, sh)
    if sweep is None:
        elbow, hand = L(0.35, -1.0, sh - 0.8), L(0.9, -0.9, sh - 1.6)
        out["handle"] = (hand, (hand[0], hand[1], hand[2] - 0.35))
        out["blade"] = ((hand[0], hand[1], hand[2] - 0.35), (hand[0], hand[1], hand[2] - 1.9))
    else:
        d = (math.cos(sweep), math.sin(sweep))
        hand = L(d[0] * 1.8, -0.7 + d[1] * 1.8, 1.0)
        elbow = L(d[0] * 0.9, -0.7 + d[1] * 0.9, 2.0)
        out["handle"] = (hand, L(d[0] * 2.15, -0.7 + d[1] * 2.15, 1.0))
        out["blade"] = (L(d[0] * 2.15, -0.7 + d[1] * 2.15, 1.0), L(d[0] * 4.0, -0.7 + d[1] * 4.0, 1.0))
    out["arm_r_up"] = (shoulder, elbow)
    out["arm_r_low"] = (elbow, hand)
    return out


SERPENT_CHAIN = (
    ("spine5", 0.45), ("spine4", 0.45), ("spine3", 0.45), ("spine2", 0.45), ("spine1", 0.45), ("spine0", 0.45),
    ("pelvis", 0.45), ("arm_l_up", 0.3), ("arm_l_low", 0.3), ("arm_r_up", 0.3), ("arm_r_low", 0.3),
    ("handle", 0.2), ("blade", 0.5), ("leg_l_up", 0.4), ("leg_l_low", 0.35), ("foot_l", 0.25),
)
SERPENT_RIBS = {"spine4": 0, "spine3": 1, "spine2": 2, "spine1": 3}


def layout_serpent(trail_point, pose: dict) -> dict:
    """Fase 2: vértebras e costelas seguem o histórico da cabeça (`trail_point(d)` = (x, y) a d unidades da cabeça)."""
    t = pose.get("t", 0.0)
    head_up = pose.get("head_up", 1.0)
    out = {}

    def body_h(d):
        return 0.5 + 0.1 * math.sin(d * 1.5 - t * 4.0)

    head = trail_point(0.0)
    ahead = trail_point(0.4)
    tx, ty = head[0] - ahead[0], head[1] - ahead[1]
    tn = math.hypot(tx, ty) or 1.0
    tx, ty = tx / tn, ty / tn
    hh = 0.45 + head_up * 0.6
    out["skull"] = _single((head[0], head[1], hh + 0.3))
    out["jaw"] = ((head[0] + tx * 0.35, head[1] + ty * 0.35, hh - 0.2), (head[0] + tx * 0.2, head[1] + ty * 0.2, hh - 0.25))
    for k, sgn in (("eye_l", 1), ("eye_r", -1)):
        out[k] = _single((head[0] + tx * 0.55 - ty * sgn * 0.22, head[1] + ty * 0.55 + tx * sgn * 0.22, hh + 0.4))
    d = 0.95
    for bone_id, length in SERPENT_CHAIN:
        a, b = trail_point(d), trail_point(d + length)
        out[bone_id] = ((a[0], a[1], body_h(d)), (b[0], b[1], body_h(d + length)))
        if bone_id in SERPENT_RIBS:
            i = SERPENT_RIBS[bone_id]
            mid = trail_point(d + length * 0.5)
            ox, oy = trail_point(d + length * 0.5 + 0.2), trail_point(max(0.0, d + length * 0.5 - 0.2))
            px, py = -(ox[1] - oy[1]), ox[0] - oy[0]
            pn = math.hypot(px, py) or 1.0
            px, py = px / pn, py / pn
            h0 = body_h(d)
            out[f"rib_l{i}"] = ((mid[0], mid[1], h0 + 0.3), (mid[0] + px * 0.75, mid[1] + py * 0.75, h0 + 0.05))
            out[f"rib_r{i}"] = ((mid[0], mid[1], h0 + 0.3), (mid[0] - px * 0.75, mid[1] - py * 0.75, h0 + 0.05))
        d += length
    return out


def layout_torso(fr: Frame, pose: dict) -> dict:
    """Fase 3: só o tronco, quicando pela arena (pose: t, swing)."""
    L = fr.w
    out = {}
    swing = math.sin(pose.get("t", 0.0) * 5.0) * 0.25 + pose.get("lean", 0.0)
    base = 0.35
    out["pelvis"] = (L(0, -0.4, base), L(0, 0.4, base))
    step = 1.7 / 6
    for i in range(6):
        out[f"spine{i}"] = (L(swing * 0.1 * i, 0, base + 0.2 + i * step), L(swing * 0.1 * (i + 1), 0, base + 0.2 + (i + 1) * step))
    for i in range(4):
        h = base + 0.8 + i * 0.3
        w = 0.85 + 0.1 * math.sin(i * 1.2)
        out[f"rib_l{i}"] = (L(0, 0.1, h), L(0.1, w, h - 0.25))
        out[f"rib_r{i}"] = (L(0, -0.1, h), L(0.1, -w, h - 0.25))
    sk = base + 2.45
    out["skull"] = _single(L(0.1 + swing * 0.5, 0, sk))
    out["jaw"] = (L(0.4 + swing * 0.5, 0, sk - 0.55), L(0.25 + swing * 0.5, 0, sk - 0.5))
    out["eye_l"] = _single(L(0.62 + swing * 0.5, 0.22, sk + 0.1))
    out["eye_r"] = _single(L(0.62 + swing * 0.5, -0.22, sk + 0.1))
    sh = base + 2.0
    out["arm_l_up"] = (L(0, 0.7, sh), L(0.4 + swing, 1.1, sh - 0.7))
    out["arm_l_low"] = (L(0.4 + swing, 1.1, sh - 0.7), L(0.9 + swing * 2, 1.0, sh - 1.5))
    out["arm_r_up"] = (L(0, -0.7, sh), L(0.4 - swing, -1.1, sh - 0.7))
    out["arm_r_low"] = (L(0.4 - swing, -1.1, sh - 0.7), L(0.9 - swing * 2, -1.0, sh - 1.5))
    hand = L(0.9 - swing * 2, -1.0, sh - 1.5)
    out["handle"] = (hand, (hand[0], hand[1], hand[2] - 0.35))
    out["blade"] = ((hand[0], hand[1], hand[2] - 0.35), (hand[0], hand[1], hand[2] - 1.5))
    return out


CLUB_LENGTH = 3.8


def layout_club(fr: Frame, pose: dict) -> dict:
    """Fase 4: coluna e braço restante viram o cabo; a cabeça é a ponta. `fr` fica na ponta (crânio); `raise` 0..1."""
    L = fr.w
    out = {}
    lift = pose.get("raise", 0.0)
    tip_h = 0.55 + lift * 2.6
    base_h = 0.35 + lift * 0.1

    def at(u, s=0.0, h_off=0.0):
        u = max(0.0, min(1.0, u))
        return L(-CLUB_LENGTH * (1.0 - u), s, base_h + (tip_h - base_h) * u + h_off)

    out["pelvis"] = (at(0.0, -0.35), at(0.0, 0.35))
    for i in range(6):
        out[f"spine{i}"] = (at(i / 6.0 * 0.82), at((i + 1) / 6.0 * 0.82))
    out["arm_r_up"] = (at(0.1, -0.45), at(0.5, -0.45))
    out["arm_r_low"] = (at(0.5, -0.45), at(0.85, -0.45))
    for i in range(4):
        u = 0.62 + i * 0.075
        out[f"rib_l{i}"] = (at(u), at(u + 0.03, 0.8, 0.25 - 0.12 * i))
        out[f"rib_r{i}"] = (at(u), at(u + 0.03, -0.8, 0.25 - 0.12 * i))
    out["skull"] = _single(at(1.0, 0.0, 0.0))
    out["jaw"] = (at(1.0, 0.0, -0.45), at(0.97, 0.0, -0.5))
    out["eye_l"] = _single(L(0.45, 0.22, tip_h + 0.1))
    out["eye_r"] = _single(L(0.45, -0.22, tip_h + 0.1))
    return out


def layout_skull(fr: Frame, pose: dict) -> dict:
    """Fase 5: só o crânio (`h` = altura do salto)."""
    L = fr.w
    h = 0.75 + pose.get("h", 0.0)
    return {
        "skull": _single(L(0, 0, h)),
        "jaw": (L(0.4, 0, h - 0.6 + pose.get("jaw", 0.0)), L(0.25, 0, h - 0.65 + pose.get("jaw", 0.0))),
        "eye_l": _single(L(0.62, 0.24, h + 0.12)),
        "eye_r": _single(L(0.62, -0.24, h + 0.12)),
    }


def _lerp(a, b, k):
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))


def _smooth(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def lying(pair, thick: float, rng: random.Random, origin):
    """Pose do osso caído no chão perto de `origin`, com a mesma orientação horizontal e um espalhamento sorteado."""
    (x0, y0, _), (x1, y1, _) = pair
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    length = max(0.3, math.dist((x0, y0), (x1, y1)))
    ang = math.atan2(y1 - y0, x1 - x0) + rng.uniform(-0.9, 0.9)
    ox = origin[0] + (cx - origin[0]) * 0.6 + rng.uniform(-1.6, 1.6)
    oy = origin[1] + (cy - origin[1]) * 0.6 + rng.uniform(-1.6, 1.6)
    dx, dy = math.cos(ang) * length / 2.0, math.sin(ang) * length / 2.0
    z = thick / 2.0
    return ((ox - dx, oy - dy, z), (ox + dx, oy + dy, z))


class BossModel:
    """Estado visual do esqueleto: transformação entre fases, entulho e desabamento final."""

    def __init__(self, seed: int = 8):
        self.rng = random.Random(seed)
        self.debris: dict[str, tuple] = {}
        self.xform_t = 1.0           # 0..1 durante a transformação; 1 = parado na fase atual
        self.xform_from: dict = {}
        self.xform_phase = 0
        self.collapse: dict | None = None
        self.last_poses: dict = {}

    # ------------------------------------------------------------------ fases
    def prime(self, phase: int, fr: Frame):
        """Começa direto em `phase` (checkpoint): os ossos já perdidos aparecem caídos ao redor do chefe."""
        self.debris.clear()
        self.xform_t = 1.0
        base = layout_stand(fr, {})
        for bone_id in DEBRIS_BY_PHASE[phase]:
            self.debris[bone_id] = lying(base[bone_id], BONE_BY_ID[bone_id].thick, self.rng, (fr.x, fr.y))

    def begin_transform(self, new_phase: int, fr: Frame):
        self.xform_from = dict(self.last_poses)
        self.xform_t = 0.0
        self.xform_phase = new_phase
        for bone_id in DEBRIS_BY_PHASE[new_phase]:
            if bone_id not in self.debris and bone_id in self.xform_from:
                self.debris[bone_id] = lying(self.xform_from[bone_id], BONE_BY_ID[bone_id].thick, self.rng, (fr.x, fr.y))

    @property
    def transforming(self) -> bool:
        return self.xform_t < 1.0

    def update(self, dt: float):
        if self.xform_t < 1.0:
            self.xform_t = min(1.0, self.xform_t + dt / TRANSFORM_TIME)
        if self.collapse is not None:
            self._update_collapse(dt)

    # ------------------------------------------------------------------ poses
    def poses(self, layout: dict) -> dict:
        """Poses finais de todos os ossos a partir da disposição da fase atual (mais a transformação, se houver)."""
        if self.collapse is not None:
            return self.collapse["poses"]
        out = {}
        e = _smooth(self.xform_t)
        arc = math.sin(math.pi * e) * 0.9 if self.transforming else 0.0
        for bone in BONES:
            target = self.debris.get(bone.id) if bone.id in self.debris else layout.get(bone.id)
            if target is None:
                target = self.debris.get(bone.id) or self.xform_from.get(bone.id)
            if self.transforming and bone.id in self.xform_from:
                src = self.xform_from[bone.id]
                a, b = _lerp(src[0], target[0], e), _lerp(src[1], target[1], e)
                a, b = (a[0], a[1], a[2] + arc), (b[0], b[1], b[2] + arc)
            else:
                a, b = target
            out[bone.id] = (a, b)
        self.last_poses = out
        return out

    # ------------------------------------------------------------------ desabamento
    def begin_collapse(self, poses: dict):
        pieces = {}
        for bone_id, (a, b) in poses.items():
            cx, cy, cz = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, (a[2] + b[2]) / 2.0
            ang = self.rng.uniform(0, math.tau)
            pieces[bone_id] = {"a": list(a), "b": list(b), "v": [math.cos(ang) * self.rng.uniform(0.5, 2.5),
                                                                  math.sin(ang) * self.rng.uniform(0.5, 2.5),
                                                                  self.rng.uniform(1.0, 4.5)],
                               "landed": bone_id in self.debris, "c": (cx, cy, cz)}
        self.collapse = {"t": 0.0, "pieces": pieces, "poses": dict(poses)}

    def _update_collapse(self, dt: float):
        c = self.collapse
        c["t"] += dt
        for bone_id, p in c["pieces"].items():
            thick = BONE_BY_ID[bone_id].thick
            if not p["landed"]:
                p["v"][2] -= 14.0 * dt
                for end in (p["a"], p["b"]):
                    end[0] += p["v"][0] * dt
                    end[1] += p["v"][1] * dt
                    end[2] += p["v"][2] * dt
                low = min(p["a"][2], p["b"][2])
                if low <= thick / 2.0:
                    for end in (p["a"], p["b"]):
                        end[2] = max(thick / 2.0, end[2] - (low - thick / 2.0))
                        end[2] = thick / 2.0 + (end[2] - thick / 2.0) * 0.2
                    p["landed"] = True
            c["poses"][bone_id] = (tuple(p["a"]), tuple(p["b"]))

    @property
    def collapse_done(self) -> bool:
        return self.collapse is not None and self.collapse["t"] >= COLLAPSE_TIME

    # ------------------------------------------------------------------ desenho
    def draw(self, surface, camera, poses: dict, alpha: int = 255):
        cubes = []
        for bone in BONES:
            a, b = poses[bone.id]
            length = math.dist(a, b)
            n = 1 if length < 1e-3 else min(9, int(length / (bone.thick * 1.05)) + 1)
            for i in range(n):
                k = 0.5 if n == 1 else i / (n - 1)
                x, y, z = a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k
                cubes.append((camera.depth(x, y), z, x, y, bone.thick, bone.color))
        cubes.sort(key=lambda c: (c[0], c[1]))
        for _, z, x, y, t, color in cubes:
            draw_voxel_box(surface, camera, x - t / 2, y - t / 2, z - t / 2, t, t, t, color, outline=True)
