"""
Chiyo, a Kunoichi das Duas Kodachi (Ciclo 1):
- Cabelo negro como a noite em corte hime com franja reta, mechas laterais (tsuya-kami) e presilha dourada Kanzashi.
- Olhos cor de âmbar com delineado carmim alado (estilo benibake) e sorriso sutil.
- Traje shinobi de couro preto-carvão ajustado com malha ninja (kusari) na gola e antebraços.
- Lenço carmim-vinho volumoso em volta do pescoço com pontas esvoaçantes em fita contínua 3D.
- Ombreira laqueada negra no ombro direito com bordas douradas e brasão do lírio-aranha (higanbana).
- Duas espadas Kodachi:
  - Bainhas cruzadas em 'X' nas costas com acabamentos dourados.
  - Empunhaduras com cordão ito preto e vermelho, tsuba dourada e lâminas de aço polido.
  - Ordenação dinâmica Painter's Algorithm com oclusão 360° perfeita.
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.mesh_primitives import (
    draw_ribbon_mesh_3d,
    draw_tapered_frustum_3d,
    draw_portrait_face_3d,
)

SKIN = (244, 212, 186)
SKIN_SHADOW = (212, 172, 144)

PALETTE = {
    # Cabelo e Adornos
    "hair": (24, 22, 26),
    "hair_highlight": (48, 44, 52),
    "hair_dark": (14, 12, 16),
    "gold": (224, 182, 64),
    "gold_bright": (255, 218, 96),
    "kanzashi_red": (210, 38, 48),

    # Rosto e Olhos
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "eye_amber": (218, 142, 36),
    "liner_red": (188, 30, 42),
    "lip": (195, 75, 85),

    # Traje Shinobi
    "leather": (28, 26, 30),
    "torso": (28, 26, 30),
    "leather_dark": (18, 16, 20),
    "leather_light": (44, 40, 48),
    "mesh": (20, 18, 22),
    "scarf": (152, 28, 48),
    "scarf_dark": (102, 18, 32),
    "scarf_light": (192, 42, 64),
    "sode_black": (22, 20, 24),
    "crest_red": (220, 36, 48),

    # Faixa e Pernas
    "sash": (132, 24, 40),
    "belt": (132, 24, 40),
    "pants": (26, 24, 28),
    "boot": (20, 18, 22),
    "boot_wrap": (142, 26, 44),
    "sole": (14, 12, 16),

    # Nodachi / Kodachi (Armas)
    "saya": (24, 22, 26),
    "saya_gold": (214, 174, 56),
    "ito_black": (22, 20, 22),
    "ito_red": (175, 30, 42),
    "steel": (230, 238, 248),
    "edge": (254, 255, 255),
    "trail": (214, 32, 52),
    "trail_core": (255, 196, 208),
}

MATERIALS = {
    "leather": "latex",
    "leather_dark": "latex",
    "scarf": "silk",
    "scarf_dark": "silk",
    "sash": "silk",
    "pants": "latex",
    "boot": "leather",
    "sode_black": "lacquer",
    "saya": "lacquer",
    "steel": "steel",
    "edge": "steel",
    "gold": "gold",
    "gold_bright": "gold",
}


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


# ---------------------------------------------------------------------------------------------------------------------
# Poses de Braços e Combate com Duas Kodachi
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Postura marcial de guarda da Dança das Duas Kodachi e poses especiais (Intro/Victory):
    - 'kodachi_draw': Mãos levadas acima dos ombros sacando as Kodachi gêmeas das bainhas nas costas.
    - 'kodachi_x_pose': Ambas as mãos à frente cruzando as duas Kodachi em 'X' diante do peito.
    - 'kodachi_victory': Mão esquerda erguida ao alto com a Kodachi apontando para o céu e direita aberta em guarda baixa.
    - Padrão: Mão direita baixa/recuada e mão esquerda alta em guarda de interceptação.
    """
    breathe = math.sin(c.walk_timer * 2.8) * 0.015
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    pose = c.extra_props.get("pose") if c.extra_props else None

    if c.state == "MAI_DANCE":
        spin = c.extra_props.get("mai_spin_angle", 0.0) if c.extra_props else 0.0
        wave = math.sin(spin * 2.0) * 0.06
        left = (bx + fx * 0.14 + px * 0.24, by + fy * 0.14 + py * 0.24, tz + 0.22 + wave)
        right = (bx - fx * 0.14 - px * 0.24, by - fy * 0.14 - py * 0.24, tz + 0.14 - wave)
        return left, right

    if c.extra_props and c.extra_props.get("mai_exhausted"):
        left = (bx + fx * 0.06 + px * 0.16, by + fy * 0.06 + py * 0.16, tz + 0.02)
        right = (bx + fx * 0.04 - px * 0.16, by + fy * 0.04 - py * 0.16, tz + 0.01)
        return left, right

    if pose == "kodachi_draw":
        left = (bx - fx * 0.04 + px * 0.14, by - fy * 0.04 + py * 0.14, tz + 0.28)
        right = (bx - fx * 0.04 - px * 0.14, by - fy * 0.04 - py * 0.14, tz + 0.28)
        return left, right
    if pose == "kodachi_x_pose":
        left = (bx + fx * 0.20 + px * 0.08, by + fy * 0.20 + py * 0.08, tz + 0.14)
        right = (bx + fx * 0.22 - px * 0.08, by + fy * 0.22 - py * 0.08, tz + 0.16)
        return left, right
    if pose == "kodachi_victory":
        left = (bx + fx * 0.08 + px * 0.16, by + fy * 0.08 + py * 0.16, tz + 0.36)
        right = (bx - fx * 0.10 - px * 0.22, by - fy * 0.10 - py * 0.22, tz + 0.05)
        return left, right

    # Mão direita baixa e recuada
    right = (
        bx - fx * 0.12 - px * 0.14,
        by - fy * 0.12 - py * 0.14,
        tz + 0.04
    )
    # Mão esquerda alta na frente do torso
    left = (
        bx + fx * 0.16 + px * 0.10,
        by + fy * 0.16 + py * 0.10,
        tz + 0.20
    )
    return left, right


def walk_arms(c):
    """Caminhada ágil e furtiva com as Kodachi balanceadas nas laterais."""
    sw = math.sin(c.walk_timer * 9.0)
    tz = c.torso_z
    right = (
        c.base_x - c.fx * 0.08 - c.px * (0.16 + sw * 0.03),
        c.base_y - c.fy * 0.08 - c.py * (0.16 + sw * 0.03),
        tz + 0.06 + abs(sw) * 0.02
    )
    left = (
        c.base_x + c.fx * 0.10 + c.px * (0.12 - sw * 0.03),
        c.base_y + c.fy * 0.10 + c.py * (0.12 - sw * 0.03),
        tz + 0.14 + abs(sw) * 0.02
    )
    return left, right


def _step(c):
    return c.extra_props.get("combo_step", 1) if c.extra_props else 1


def attack_arms(c):
    """
    Dança das Duas Kodachi (Combo 3-Hit com arcos amplos):
    - Passo 1: Corte ascendente diagonal com a Kodachi direita.
    - Passo 2: Giro horizontal rasante com a Kodachi esquerda.
    - Passo 3: Corte em tesoura cruzada com ambas as Kodachis se encontrando.
    """
    p = c.atk_progress
    step = _step(c)
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    if step == 1:
        arc_a = -1.2 + p * 2.4
        right = (
            bx + fx * math.cos(arc_a) * 0.28 - px * math.sin(arc_a) * 0.22,
            by + fy * math.cos(arc_a) * 0.28 - py * math.sin(arc_a) * 0.22,
            tz + 0.02 + p * 0.36
        )
        left = (
            bx + px * 0.16 - fx * 0.06,
            by + py * 0.16 - fy * 0.06,
            tz + 0.18
        )
    elif step == 2:
        arc_l = 1.4 - p * 2.8
        left = (
            bx + fx * math.cos(arc_l) * 0.30 + px * math.sin(arc_l) * 0.26,
            by + fy * math.cos(arc_l) * 0.30 + py * math.sin(arc_l) * 0.26,
            tz + 0.16
        )
        right = (
            bx - px * 0.16 - fx * 0.08,
            by - py * 0.16 - fy * 0.08,
            tz + 0.08
        )
    else:
        cross_t = math.sin(p * math.pi)
        right = (
            bx + fx * (0.18 + cross_t * 0.24) - px * (0.16 - p * 0.26),
            by + fy * (0.18 + cross_t * 0.24) - py * (0.16 - p * 0.26),
            tz + 0.22 - p * 0.10
        )
        left = (
            bx + fx * (0.18 + cross_t * 0.24) + px * (0.16 - p * 0.26),
            by + fy * (0.18 + cross_t * 0.24) + py * (0.16 - p * 0.26),
            tz + 0.12 + p * 0.10
        )
    return left, right


# ---------------------------------------------------------------------------------------------------------------------
# Bainhas das Duas Kodachi nas Costas
# ---------------------------------------------------------------------------------------------------------------------

def _sheath_frames(c):
    """
    Duas grandes bainhas de Kodachi cruzadas nas costas em formato de 'X':
    - Bainha 1: diagonal do ombro direito ao quadril esquerdo.
    - Bainha 2: diagonal do ombro esquerdo ao quadril direito.
    """
    bx, by, pz, fx, fy, px, py = c.base_x, c.base_y, c.pelvis_z, c.fx, c.fy, c.px, c.py
    back_center = (bx - fx * 0.10, by - fy * 0.10, pz + 0.18)

    dir1 = mk.norm((-fx * 0.15 + px * 0.45, -fy * 0.15 + py * 0.45, -0.85))
    orig1 = (back_center[0] - px * 0.08, back_center[1] - py * 0.08, back_center[2] + 0.16)

    dir2 = mk.norm((-fx * 0.15 - px * 0.45, -fy * 0.15 - py * 0.45, -0.85))
    orig2 = (back_center[0] + px * 0.08, back_center[1] + py * 0.08, back_center[2] + 0.16)

    return (orig1, dir1), (orig2, dir2)


def _draw_side_lock(c, side: float):
    """Mecha lateral lisa Hime descendo além da mandíbula em fita contínua 3D."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.04)
    o = cloth.chain_offsets(1, c.walk_timer, 0.8 * side, trail, (px, py), amp=amp * 0.6, freq=freq)[0]

    p0 = (bx + fx * 0.015 + px * (0.065 * side), by + fy * 0.015 + py * (0.065 * side), hz + 0.125)
    p1 = (bx + fx * 0.020 + px * (0.070 * side) + o[0] * 0.5, by + fy * 0.020 + py * (0.070 * side) + o[1] * 0.5, hz + 0.050 + o[2] * 0.5)
    p2 = (bx + fx * 0.025 + px * (0.072 * side) + o[0], by + fy * 0.025 + py * (0.072 * side) + o[1], hz - 0.020 + o[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1, p2],
        widths=[0.024, 0.020, 0.012],
        depth_thick=0.014,
        colors=[P["hair"], P["hair_dark"]],
        side_vec=(px * side, py * side, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )


def _side_lock_is_behind(c, side: float) -> bool:
    lx = c.base_x + c.px * 0.07 * side
    ly = c.base_y + c.py * 0.07 * side
    return mk.depth(c, lx, ly) < mk.depth(c, c.base_x, c.base_y) - 0.01


# ---------------------------------------------------------------------------------------------------------------------
# Camadas do Modelo: Trás, Pernas, Faixa, Tronco, Cabeça e Frente
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Cascata de cabelo negro liso caindo pelas costas.
    - Pontas esvoaçantes do lenço carmim em fita contínua 3D.
    - As duas bainhas de Kodachi cruzadas em 'X' nas costas.
    - Lâminas e manoplas se as mãos estiverem atrás do tronco ao encarar de costas.
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    hz, tz = c.head_z, c.torso_z
    d_torso = mk.depth(c, bx, by)

    # Cascata de cabelo negro liso caindo pelas costas
    d_nape = mk.depth(c, bx - fx * 0.08, by - fy * 0.08)
    if d_nape <= d_torso + 0.02:
        trail, amp, freq = mk.motion(c, 0.05)
        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.6, trail, (-fx, -fy), amp=amp * 0.8, freq=freq)
        p_hair0 = (bx - fx * 0.06, by - fy * 0.06, hz + 0.12)
        p_hair1 = (bx - fx * 0.08 + o1[0], by - fy * 0.08 + o1[1], hz + 0.02 + o1[2])
        p_hair2 = (bx - fx * 0.10 + o2[0], by - fy * 0.10 + o2[1], hz - 0.10 + o2[2])
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[p_hair0, p_hair1, p_hair2],
            widths=[0.115, 0.130, 0.140],
            depth_thick=0.035,
            colors=[P["hair"], P["hair_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(-fx, -fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

    # Mechas laterais no lado oculto da câmera
    for s in (-1.0, 1.0):
        if _side_lock_is_behind(c, s):
            _draw_side_lock(c, s)

    # Pontas esvoaçantes do lenço carmim atrás do pescoço
    scarf_anchor = (bx - fx * 0.09, by - fy * 0.09, tz + 0.21)
    trail, amp, freq = mk.motion(c, 0.07)
    offs = cloth.chain_offsets(3, c.walk_timer, 0.8, trail, (px, py), amp=amp * 1.5, freq=freq)
    p_sc0 = scarf_anchor
    p_sc1 = (scarf_anchor[0] - fx * 0.05 + offs[0][0], scarf_anchor[1] - fy * 0.05 + offs[0][1], tz + 0.15 + offs[0][2])
    p_sc2 = (scarf_anchor[0] - fx * 0.10 + offs[1][0], scarf_anchor[1] - fy * 0.10 + offs[1][1], tz + 0.07 + offs[1][2])
    p_sc3 = (scarf_anchor[0] - fx * 0.15 + offs[2][0], scarf_anchor[1] - fy * 0.15 + offs[2][2], tz - 0.01 + offs[2][2])
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p_sc0, p_sc1, p_sc2, p_sc3],
        widths=[0.065, 0.075, 0.082, 0.088],
        depth_thick=0.022,
        colors=[P["scarf"], P["scarf_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Bainhas das Kodachi cruzadas nas costas
    (orig1, dir1), (orig2, dir2) = _sheath_frames(c)
    kodachi_sheath_len = 0.44

    for orig, d in ((orig1, dir1), (orig2, dir2)):
        mk.obox(c, orig, d, kodachi_sheath_len, 0.038, 0.038, P["saya"], outline=True)
        mk.obox(c, orig, d, 0.035, 0.044, 0.044, P["saya_gold"], outline=False)
        mk.obox(c, mk.add(orig, d, kodachi_sheath_len - 0.035), d, 0.035, 0.042, 0.042, P["saya_gold"], outline=False)

    # Ordenação dinâmica: se as mãos estiverem atrás do tronco ao encarar de costas
    hand_l, hand_r = idle_arms(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_weapons(c, hand_l, hand_r)


def draw_legs(c):
    """
    Pernas femininas ágeis em malha contínua 3D:
    - Calça shinobi de couro/látex preto contínua do quadril ao tornozelo (sem degraus de blocos).
    - Amarrações carmim cruzadas nas canelas.
    - Botas shinobi de sola fina articulada.
    """
    P = pal()
    trail, amp, freq = mk.motion(c, 0.04)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.8 * sign, trail, (c.px, c.py), amp=amp * 0.5, freq=freq)

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.4, sh[1] + o1[1] * 0.4, sh[2] + 0.15)
        cuff_pos = (sh[0] + o1[0] * 0.2, sh[1] + o1[1] * 0.2, sh[2] + 0.08)
        ankle = (foot[0] + o2[0] * 0.3, foot[1] + o2[1] * 0.3, foot[2] + 0.04)

        # Calça shinobi preta em malha contínua 3D
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos],
            widths=[0.098, 0.088, 0.075],
            depth_thick=0.072,
            colors=[P["pants"], P["leather_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Cano da bota com amarração carmim
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[cuff_pos, ankle],
            widths=[0.075, 0.068],
            depth_thick=0.068,
            colors=[P["boot"], P["boot"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )



        # Bota shinobi feminina
        flen, fwidth = 0.12, 0.058
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.014, flen, fwidth, 0.030, P["boot"], outline=True)
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.002, flen + 0.004, fwidth + 0.004, 0.010, P["sole"], outline=False)


def draw_obi(c):
    """Cinto shinobi fino de couro preto com faixa carmim e fivela dourada."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    mk.cbox(c, bx, by, z, c.pelvis_w - 0.01, c.pelvis_w * 0.70, 0.065, P["sash"])
    mk.cbox(c, bx, by, z + 0.012, c.pelvis_w - 0.005, c.pelvis_w * 0.72, 0.032, P["leather_dark"])
    mk.cbox(c, bx + fx * 0.085, by + fy * 0.085, z + 0.015, 0.040, 0.026, 0.038, P["gold"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço ágil articulado de kunoichi com manga e braçadeira de couro."""
    P = pal()
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["leather"],
        sleeve_to=0.55,
        bracer=P["leather_dark"],
        bracer_span=(0.45, 0.90),
        w=0.048,
        bend=0.025
    )


def draw_torso(c):
    """
    Tronco:
    - Gola interna com malha ninja (kusari) no decote.
    - Lenço carmim envolto no pescoço com drapeado natural.
    - Corpete de couro ajustado preto com rebites dourados.
    - Ombreira laqueada negra (Sode) no ombro direito orientada corretamente com up=(fx, fy, 0.0).
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    front = 0.085

    if mk.depth(c, fx, fy) > -0.05:
        # Decote e malha ninja kusari
        mk.obox(c, (bx + fx * front, by + fy * front, tz + 0.12), (0.0, 0.0, 1.0), 0.10, 0.08, 0.015, P["mesh"], up=(fx, fy, 0.0), outline=False)
        mk.obox(c, (bx + fx * (front + 0.004), by + fy * (front + 0.004), tz + 0.15), (0.0, 0.0, 1.0), 0.08, 0.04, 0.012, P["skin"], up=(fx, fy, 0.0), outline=False)

        # Lenço carmim no pescoço
        mk.obox(c, (bx + fx * 0.02, by + fy * 0.02, tz + 0.22), (0.0, 0.0, 1.0), 0.15, 0.14, 0.045, P["scarf"], up=(fx, fy, 0.0), outline=False)
        mk.obox(c, (bx + fx * (front + 0.008), by + fy * (front + 0.008), tz + 0.20), (0.0, 0.0, 1.0), 0.11, 0.05, 0.035, P["scarf_light"], up=(fx, fy, 0.0), outline=False)

        # Rebites dourados no corpete
        for side_sign in (-1.0, 1.0):
            for rz in (tz + 0.05, tz + 0.10, tz + 0.15):
                mk.cbox(c, bx + fx * (front + 0.006) + px * (0.045 * side_sign), by + fy * (front + 0.006) + py * (0.045 * side_sign), rz, 0.012, 0.012, 0.012, P["gold"], outline=False)

    # Ombreira laqueada negra (Sode) no ombro direito
    sh_r_x = bx - px * 0.15
    sh_r_y = by - py * 0.15
    sh_r_z = tz + 0.19
    sode_dir = mk.norm((-px * 0.25, -py * 0.25, -0.95))
    up_sode = (fx, fy, 0.0)

    mk.obox(c, (sh_r_x, sh_r_y, sh_r_z), sode_dir, 0.12, 0.045, 0.16, P["sode_black"], up=up_sode, outline=True)
    mk.obox(c, (sh_r_x - px * 0.015, sh_r_y - py * 0.015, sh_r_z + 0.01), sode_dir, 0.03, 0.050, 0.165, P["gold"], up=up_sode, outline=False)
    mk.obox(c, (sh_r_x - px * 0.025, sh_r_y - py * 0.025, sh_r_z - 0.03), sode_dir, 0.04, 0.048, 0.04, P["crest_red"], up=up_sode, outline=False)


def draw_head(c):
    """
    Cabeça de Chiyo:
    - Corte Hime com franja frontal reta e mechas laterais limpas.
    - Franja acima das sobrancelhas para manter os olhos luminosos limpos.
    - Presilha Kanzashi dourada com pingente carmim no lado visível.
    - Mechas laterais renderizadas no lado visível.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # Mechas laterais no lado voltado para a câmera
    for s in (-1.0, 1.0):
        if not _side_lock_is_behind(c, s):
            _draw_side_lock(c, s)

    # Franja frontal reta Hime
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.006
        # Franja perfeitamente esculpida acima da linha dos olhos (z >= hz + 0.108)
        p0 = (bx + fx * front_d, by + fy * front_d, hz + 0.142)
        p1 = (bx + fx * (front_d + 0.004), by + fy * (front_d + 0.004), hz + 0.110)
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            p0, p1,
            w_start=hw * 0.88, h_start=0.022,
            w_end=hw * 0.84, h_end=0.018,
            color=P["hair"],
            up=(0.0, 0.0, 1.0),
            outline=False,
            alpha=c.alpha,
        )

        # Presilha Kanzashi dourada no lado esquerdo da cabeça
        pin_x = bx + px * 0.068 + fx * 0.020
        pin_y = by + py * 0.068 + fy * 0.020
        pin_z = hz + 0.125
        mk.cbox(c, pin_x, pin_y, pin_z, 0.030, 0.030, 0.024, P["gold_bright"], outline=False)
        mk.cbox(c, pin_x + px * 0.008, pin_y + py * 0.008, pin_z - 0.025, 0.016, 0.016, 0.032, P["kanzashi_red"], outline=False)


# ---------------------------------------------------------------------------------------------------------------------
# Renderizador Especializado das Duas Kodachis
# ---------------------------------------------------------------------------------------------------------------------

def _draw_kodachi_blade(c, hand, direction, length=0.44):
    """
    Desenha uma espada Kodachi ágil:
    - Empunhadura compacta (tsuka) com cordão preto e vermelho.
    - Pomo dourado (kashira) e guarda oval (tsuba).
    - Lâmina de aço polido com fio cortante claro.
    """
    P = pal()
    d = mk.norm(direction)
    grip_len = 0.11
    guard_w = 0.048

    tsuba_pt = mk.add(hand, d, 0.04)

    mk.obox(c, mk.add(tsuba_pt, d, -grip_len), d, grip_len, 0.030, 0.030, P["ito_black"])
    mk.obox(c, mk.add(tsuba_pt, d, -grip_len * 0.55), d, 0.030, 0.032, 0.032, P["ito_red"], outline=False)
    mk.obox(c, mk.add(tsuba_pt, d, -grip_len - 0.010), d, 0.014, 0.034, 0.034, P["gold"], outline=False)

    mk.obox(c, mk.add(tsuba_pt, d, -0.006), d, 0.012, guard_w, guard_w, P["gold"])
    mk.obox(c, mk.add(tsuba_pt, d, 0.006), d, 0.020, 0.036, 0.026, P["gold"], outline=False)

    mk.obox(c, mk.add(tsuba_pt, d, 0.026), d, length, 0.036, 0.020, P["steel"])
    mk.obox(c, mk.add(tsuba_pt, d, 0.034), d, max(0.0, length - 0.016), 0.014, 0.022, P["edge"], outline=False)

    return mk.add(tsuba_pt, d, 0.026 + length)


def _render_weapons(c, left_hand, right_hand):
    """Renderiza as duas Kodachi e seus rastros em combate."""
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    for hand in (left_hand, right_hand):
        mk.cbox(c, hand[0], hand[1], hand[2] - 0.015, 0.052, 0.052, 0.050, P["leather_dark"], outline=True)

    if c.is_melee:
        step = _step(c)
        p = c.atk_progress

        if step == 1:
            slash_d1 = mk.norm((fx * 0.70 + px * 0.20, fy * 0.70 + py * 0.20, 0.75 - p * 0.30))
            guard_d2 = mk.norm((fx * 0.40 - px * 0.40, fy * 0.40 - py * 0.40, 0.80))
            tip1 = _draw_kodachi_blade(c, right_hand, slash_d1, length=0.46)
            _draw_kodachi_blade(c, left_hand, guard_d2, length=0.42)

            if 0.15 < p < 0.88:
                mid = mk.lerp(right_hand, tip1, 0.55)
                prev_tip = (tip1[0] - fx * 0.12 - px * 0.06, tip1[1] - fy * 0.12 - py * 0.06, tip1[2] - 0.14)
                prev_mid = (mid[0] - fx * 0.08 - px * 0.03, mid[1] - fy * 0.08 - py * 0.03, mid[2] - 0.08)
                mk.band(c, (mid, tip1, prev_tip, prev_mid), P["trail"] + (180,))
                mk.band(c, (mk.lerp(mid, tip1, 0.6), tip1, prev_tip, mk.lerp(prev_mid, prev_tip, 0.6)), P["trail_core"] + (230,))

        elif step == 2:
            slash_d2 = mk.norm((fx * 0.85 - px * 0.35, fy * 0.85 - py * 0.35, -0.15))
            guard_d1 = mk.norm((-fx * 0.20 - px * 0.60, -fy * 0.20 - py * 0.60, -0.75))
            _draw_kodachi_blade(c, right_hand, guard_d1, length=0.42)
            tip2 = _draw_kodachi_blade(c, left_hand, slash_d2, length=0.46)

            if 0.15 < p < 0.88:
                mid = mk.lerp(left_hand, tip2, 0.55)
                prev_tip = (tip2[0] - fx * 0.10 + px * 0.12, tip2[1] - fy * 0.10 + py * 0.12, tip2[2] + 0.05)
                prev_mid = (mid[0] - fx * 0.06 + px * 0.08, mid[1] - fy * 0.06 + py * 0.08, mid[2] + 0.03)
                mk.band(c, (mid, tip2, prev_tip, prev_mid), P["trail"] + (180,))
                mk.band(c, (mk.lerp(mid, tip2, 0.6), tip2, prev_tip, mk.lerp(prev_mid, prev_tip, 0.6)), P["trail_core"] + (230,))

        else:
            cross_d1 = mk.norm((fx * 0.75 + px * 0.35, fy * 0.75 + py * 0.35, -0.25))
            cross_d2 = mk.norm((fx * 0.75 - px * 0.35, fy * 0.75 - py * 0.35, 0.25))
            tip1 = _draw_kodachi_blade(c, right_hand, cross_d1, length=0.45)
            tip2 = _draw_kodachi_blade(c, left_hand, cross_d2, length=0.45)

            if 0.15 < p < 0.88:
                mid1 = mk.lerp(right_hand, tip1, 0.5)
                mid2 = mk.lerp(left_hand, tip2, 0.5)
                mk.band(c, (mid1, tip1, tip2, mid2), P["trail"] + (190,))
                mk.band(c, (mk.lerp(mid1, tip1, 0.6), tip1, tip2, mk.lerp(mid2, tip2, 0.6)), P["trail_core"] + (240,))
    else:
        pose = c.extra_props.get("pose") if c.extra_props else None
        if c.state == "MAI_DANCE":
            dir_r = mk.norm((-fx * 0.45 - px * 0.85, -fy * 0.45 - py * 0.85, 0.20))
            dir_l = mk.norm((fx * 0.45 + px * 0.85, fy * 0.45 + py * 0.85, 0.35))
            tip1 = _draw_kodachi_blade(c, right_hand, dir_r, length=0.46)
            tip2 = _draw_kodachi_blade(c, left_hand, dir_l, length=0.46)

            mid1 = mk.lerp(right_hand, tip1, 0.45)
            prev_tip1 = (tip1[0] - fx * 0.24 + px * 0.12, tip1[1] - fy * 0.24 + py * 0.12, tip1[2] - 0.06)
            prev_mid1 = (mid1[0] - fx * 0.16 + px * 0.08, mid1[1] - fy * 0.16 + py * 0.08, mid1[2] - 0.04)
            mk.band(c, (mid1, tip1, prev_tip1, prev_mid1), P["trail"] + (195,))
            mk.band(c, (mk.lerp(mid1, tip1, 0.6), tip1, prev_tip1, mk.lerp(prev_mid1, prev_tip1, 0.6)), P["trail_core"] + (235,))

            mid2 = mk.lerp(left_hand, tip2, 0.45)
            prev_tip2 = (tip2[0] + fx * 0.24 - px * 0.12, tip2[1] + fy * 0.24 - py * 0.12, tip2[2] + 0.06)
            prev_mid2 = (mid2[0] + fx * 0.16 - px * 0.08, mid2[1] + fy * 0.16 - py * 0.08, mid2[2] + 0.04)
            mk.band(c, (mid2, tip2, prev_tip2, prev_mid2), P["trail"] + (195,))
            mk.band(c, (mk.lerp(mid2, tip2, 0.6), tip2, prev_tip2, mk.lerp(prev_mid2, prev_tip2, 0.6)), P["trail_core"] + (235,))
        elif pose == "kodachi_draw":
            dir_r = mk.norm((-fx * 0.25 + px * 0.55, -fy * 0.25 + py * 0.55, -0.78))
            dir_l = mk.norm((-fx * 0.25 - px * 0.55, -fy * 0.25 - py * 0.55, -0.78))
            _draw_kodachi_blade(c, right_hand, dir_r, length=0.40)
            _draw_kodachi_blade(c, left_hand, dir_l, length=0.40)
        elif pose == "kodachi_x_pose":
            dir_r = mk.norm((fx * 0.35 + px * 0.72, fy * 0.35 + py * 0.72, 0.58))
            dir_l = mk.norm((fx * 0.35 - px * 0.72, fy * 0.35 - py * 0.72, 0.58))
            tip1 = _draw_kodachi_blade(c, right_hand, dir_r, length=0.45)
            tip2 = _draw_kodachi_blade(c, left_hand, dir_l, length=0.45)
            mid1 = mk.lerp(right_hand, tip1, 0.55)
            mid2 = mk.lerp(left_hand, tip2, 0.55)
            mk.band(c, (mid1, tip1, tip2, mid2), P["trail"] + (135,))
        elif pose == "kodachi_victory":
            dir_r = mk.norm((-fx * 0.35 - px * 0.75, -fy * 0.35 - py * 0.75, -0.55))
            dir_l = mk.norm((-fx * 0.15 + px * 0.22, -fy * 0.15 + py * 0.22, 0.96))
            _draw_kodachi_blade(c, right_hand, dir_r, length=0.45)
            _draw_kodachi_blade(c, left_hand, dir_l, length=0.46)
        else:
            dir_r = mk.norm((-fx * 0.55 - px * 0.35, -fy * 0.55 - py * 0.35, -0.75))
            dir_l = mk.norm((fx * 0.45 + px * 0.25, fy * 0.45 + py * 0.25, 0.85))
            _draw_kodachi_blade(c, right_hand, dir_r, length=0.44)
            _draw_kodachi_blade(c, left_hand, dir_l, length=0.44)


def draw_front(c, left_hand, right_hand):
    """Camada frontal: lâminas e manoplas se estiverem à frente do tronco."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    w_mid = ((left_hand[0] + right_hand[0]) * 0.5, (left_hand[1] + right_hand[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_weapons(c, left_hand, right_hand)
