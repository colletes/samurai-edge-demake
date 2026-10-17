"""
Ichi, a Lâmina Cega e Mestra do Shikomizue (Ciclo 3):
- Espadachim cega extraordinária de audição aguçada e reflexos imperceptíveis (homenagem à lenda de Zatoichi).
- Postura serena e equilibrada, ouvindo o respirar do vento, passos e corte de ar do adversário.
- Quimono de viagem ameixa-escuro com forro e colarinho branco puro em malha contínua 3D, envolto por xale de viagem.
- Cabelos negros refinados presos em coque tradicional com grampo de madeira nobre (kanzashi).
- Olhos leitosos fechados em contemplação serena e foco absoluto.
- Espada-Bengala Oculta (Shikomizue):
  - Bastão de madeira nobre lisa de cerejeira parecendo uma bengala de caminhada inofensiva.
  - Lâmina interna de aço dobrado de altíssima pureza com fio de navalha e rastro prateado reluzente.
  - Ordenação dinâmica Painter's Algorithm para oclusão 360°.
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

SKIN = (212, 185, 172)
SKIN_SHADOW = (175, 142, 130)

PALETTE = {
    # Quimono de Viagem e Xale
    "kimono": (46, 28, 48),
    "torso": (46, 28, 48),
    "kimono_dark": (28, 18, 30),
    "kimono_light": (68, 42, 72),
    "kimono_trim": (118, 92, 122),
    "collar_white": (244, 240, 234),
    "scarf": (38, 36, 42),
    "scarf_dark": (24, 22, 28),

    # Obi e Adornos
    "obi": (26, 22, 30),
    "belt": (26, 22, 30),
    "obijime": (195, 160, 80),

    # Cabelo e Kanzashi
    "hair": (18, 16, 20),
    "hair_dark": (12, 10, 14),
    "kanzashi": (135, 78, 42),
    "kanzashi_gold": (218, 172, 75),

    # Anatomia e Expressão Cega
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "blind_eye": (188, 198, 218),
    "blind_core": (232, 238, 250),
    "eyelid": (212, 178, 154),
    "lash": (28, 22, 28),
    "lip": (205, 120, 130),
    "lip_shadow": (165, 80, 90),

    # Calçados e Pernas
    "tabi": (242, 238, 232),
    "geta": (135, 92, 58),
    "geta_dark": (95, 62, 38),
    "strap": (32, 26, 32),
    "pants": (46, 28, 48),

    # Shikomizue (Espada-Bengala Oculta)
    "cane_wood": (72, 44, 30),
    "cane_dark": (46, 26, 18),
    "brass_fitting": (210, 172, 70),
    "steel_blade": (235, 242, 255),
    "steel_edge": (255, 255, 255),
    "blood_groove": (180, 195, 215),

    # Rastros de Corte em Vácuo Prateado
    "slash_silver": (215, 235, 255),
    "slash_core": (255, 255, 255),
}

MATERIALS = {
    "kimono": "silk",
    "kimono_dark": "silk",
    "scarf": "canvas",
    "obi": "silk",
    "cane_wood": "wood",
    "steel_blade": "metal",
    "steel_edge": "metal",
    "brass_fitting": "metal",
    "geta": "wood",
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses de Braços e Animação de Combate Shikomizue
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Postura da Bengala de Viagem de Ichi:
    - Mão direita apoia o topo da empunhadura da shikomizue em repouso vertical.
    - Mão esquerda levemente apoiada no corpo da bengala.
    """
    breathe = math.sin(c.walk_timer * 2.2) * 0.010
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    right = (
        bx + fx * 0.16 + px * 0.08,
        by + fy * 0.16 + py * 0.08,
        tz + 0.16
    )
    left = (
        bx + fx * 0.14 + px * 0.06,
        by + fy * 0.14 + py * 0.06,
        tz + 0.02
    )
    return left, right


def walk_arms(c):
    """Caminhada tateante da bengala (bengala guiando os passos com calma)."""
    tap = math.sin(c.walk_timer * 6.5) * 0.08
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    right = (
        bx + fx * (0.18 + tap * 0.06) + px * 0.08,
        by + fy * (0.18 + tap * 0.06) + py * 0.08,
        tz + 0.16 + abs(tap) * 0.02
    )
    left = (
        bx + fx * 0.10 - px * 0.08,
        by + fy * 0.10 - py * 0.08,
        tz + 0.06
    )
    return left, right


def attack_arms(c):
    """
    Golpe Gyaku-Iai Cego:
    - O aço prateado se desvencilha da madeira da bengala em fração de segundo.
    - Saque horizontal relâmpago com pegada invertida.
    """
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    prog = c.atk_progress

    is_pierce = c.extra_props.get("is_pierce", False) if c.extra_props else False
    if is_pierce:
        left = (bx - fx * 0.08 + px * 0.12, by - fy * 0.08 + py * 0.12, tz + 0.10)
        right = (bx + fx * 0.38 - px * 0.02, by + fy * 0.38 - py * 0.02, tz + 0.14)
        return left, right

    if prog < 0.25:
        left = (bx + fx * 0.12 + px * 0.08, by + fy * 0.12 + py * 0.08, tz + 0.10)
        right = (bx + fx * 0.10 - px * 0.08, by + fy * 0.10 - py * 0.08, tz + 0.14)
    elif prog < 0.65:
        p_sub = (prog - 0.25) / 0.40
        arc_ang = -1.2 + p_sub * 2.5
        left = (bx - fx * 0.10 + px * 0.12, by - fy * 0.10 + py * 0.12, tz + 0.08)
        rx = bx + fx * 0.25 + px * (math.sin(arc_ang) * 0.28)
        ry = by + fy * 0.25 + py * (math.sin(arc_ang) * 0.28)
        right = (rx, ry, tz + 0.12)
    else:
        left = (bx - fx * 0.06 + px * 0.10, by - fy * 0.06 + py * 0.10, tz + 0.09)
        right = (bx + fx * 0.28 + px * 0.22, by + fy * 0.28 + py * 0.22, tz + 0.13)

    return left, right


# ---------------------------------------------------------------------------------------------------------------------
# Detalhamento Voxel do Guerreiro
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Coque nobre elevado com kanzashi de cerejeira (se visto de costas).
    - Pontas do xale de viagem caindo pelas costas.
    - Se a bengala estiver atrás do corpo, desenha aqui antes do quimono.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    hz = c.head_z
    hw = c.head_w
    d_torso = mk.depth(c, bx, by)

    # Coque tradicional elevado (Mage) nas costas da cabeça
    d_bun = mk.depth(c, bx - fx * 0.06, by - fy * 0.06)
    if d_bun <= d_torso + 0.02:
        bun_pos = (bx - fx * 0.05, by - fy * 0.05, hz + 0.165)
        mk.obox(c, bun_pos, (-fx, -fy, 0.0), 0.065, 0.075, 0.065, P["hair_dark"], outline=True)
        # Grampo Kanzashi de madeira nobre atravessando o coque
        mk.obox(c, (bun_pos[0] - px * 0.08, bun_pos[1] - py * 0.08, bun_pos[2] + 0.01), (px, py, 0.0), 0.16, 0.014, 0.014, P["kanzashi"], outline=False)
        mk.obox(c, (bun_pos[0] + px * 0.08, bun_pos[1] + py * 0.08, bun_pos[2] + 0.01), (px, py, 0.0), 0.02, 0.018, 0.018, P["kanzashi_gold"], outline=False)

    # Xale de viagem caindo pelas costas em fita 3D
    trail, amp, freq = mk.motion(c, 0.05)
    o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.7, trail, (-fx, -fy), amp=amp * 0.8, freq=freq)
    p0 = (bx - fx * 0.08, by - fy * 0.08, tz + 0.22)
    p1 = (bx - fx * 0.10 + o1[0], by - fy * 0.10 + o1[1], tz + 0.12 + o1[2])
    p2 = (bx - fx * 0.12 + o2[0], by - fy * 0.12 + o2[1], tz + 0.02 + o2[2])
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1, p2],
        widths=[0.125, 0.135, 0.140],
        depth_thick=0.025,
        colors=[P["scarf"], P["scarf_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Ordenação dinâmica da bengala
    hand_l, hand_r = idle_arms(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_shikomizue(c, hand_l, hand_r)


def draw_legs(c):
    """
    Quimono de viagem ameixa em malha contínua 3D descendo até os tornozelos,
    meias tabi brancas e calçado geta.
    """
    P = pal()
    trail, amp, freq = mk.motion(c, 0.03)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.8 * sign, trail, (c.px, c.py), amp=amp * 0.4, freq=freq)

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.3, sh[1] + o1[1] * 0.3, sh[2] + 0.15)
        hem = (sh[0] + o1[0] * 0.15, sh[1] + o1[1] * 0.15, sh[2] + 0.06)
        ankle = (foot[0] + o2[0] * 0.2, foot[1] + o2[1] * 0.2, foot[2] + 0.03)

        # Quimono longo em malha contínua 3D
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, hem],
            widths=[0.115, 0.125, 0.135],
            depth_thick=0.100,
            colors=[P["kimono"], P["kimono_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Meia Tabi branca em malha contínua descendo do quimono até o calçado
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[hem, ankle],
            widths=[0.065, 0.054],
            depth_thick=0.054,
            colors=[P["tabi"], P["tabi"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

        # Calçado Geta de madeira com tiras escuras
        flen, fwidth = 0.12, 0.062
        mk.obox(c, (foot[0] - c.fx * 0.02, foot[1] - c.fy * 0.02, foot[2]), (c.fx, c.fy, 0.0), flen, fwidth, 0.030, P["geta"])
        mk.obox(c, (foot[0] + c.fx * 0.01, foot[1] + c.fy * 0.01, foot[2] + 0.025), (c.fx, c.fy, 0.0), 0.04, 0.066, 0.018, P["strap"], outline=False)


def draw_obi(c):
    """Faixa Obi estreita com cordão dourado (obijime) no centro."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    mk.cbox(c, bx, by, z, c.pelvis_w - 0.005, c.pelvis_w * 0.72, 0.075, P["obi"])
    mk.cbox(c, bx + fx * 0.082, by + fy * 0.082, z + 0.015, c.pelvis_w - 0.01, 0.014, 0.016, P["obijime"], outline=False)


def draw_torso(c):
    """
    Tronco elegante de espadachim cega:
    - Quimono ameixa cruzado sobre colarinho branco puro em V.
    - Xale de viagem cinza sobre os ombros.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    front = 0.088

    if mk.depth(c, fx, fy) > -0.05:
        # Colarinho interno branco (Juban)
        apex = (bx + fx * (front + 0.002), by + fy * (front + 0.002), tz + 0.10)
        for s in (-1.0, 1.0):
            top = (bx + fx * front + px * 0.052 * s, by + fy * front + py * 0.052 * s, tz + 0.245)
            draw_tapered_frustum_3d(c.surface, c.camera, top, apex, w_start=0.022, h_start=0.012, w_end=0.015, h_end=0.008, color=P["collar_white"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)

        # Pele do decote
        mk.obox(c, (bx + fx * (front - 0.006), by + fy * (front - 0.006), tz + 0.14), (0.0, 0.0, 1.0), 0.08, 0.045, 0.014, P["skin"], up=(fx, fy, 0.0), outline=False)

        # Xale de viagem cinza cobrindo os ombros e clavícula
        mk.obox(c, (bx + fx * 0.03, by + fy * 0.03, tz + 0.21), (0.0, 0.0, 1.0), 0.16, 0.15, 0.045, P["scarf"], up=(fx, fy, 0.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço ágil com manga de quimono."""
    P = pal()
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["kimono"],
        sleeve_to=0.58,
        w=0.048,
        bend=0.024
    )


def draw_head(c):
    """
    Cabeça e Cabelos de Ichi:
    - Cabelo negro com calota esculpida e mechas fluidas.
    - Feições serenas com olhos leitosos cegos via draw_portrait_face_3d.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    cran_top = (bx - fx * 0.005, by - fy * 0.005, hz + 0.160)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, hz + 0.138), cran_top,
        w_start=hw * 0.94, h_start=hw * 0.94,
        w_end=hw * 0.70, h_end=hw * 0.70,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )


# ---------------------------------------------------------------------------------------------------------------------
# Renderização da Shikomizue (Espada-Bengala Oculta) e Efeitos
# ---------------------------------------------------------------------------------------------------------------------

def _draw_cane_scabbard(c, hand_pt, direction, length=0.88):
    """Bainha/corpo de madeira nobre da bengala de caminhada."""
    P = pal()
    d = mk.norm(direction)
    mk.obox(c, hand_pt, d, length, 0.030, 0.030, P["cane_wood"], texture="wood")
    mk.obox(c, mk.add(hand_pt, d, length - 0.03), d, 0.032, 0.034, 0.034, P["brass_fitting"], outline=False)


def _draw_shikomizue_blade(c, hand_pt, direction, length=0.82):
    """Lâmina de katana sacada em pegada invertida."""
    P = pal()
    d = mk.norm(direction)

    mk.obox(c, mk.add(hand_pt, d, -0.15), d, 0.15, 0.032, 0.032, P["cane_wood"], texture="wood")
    mk.obox(c, hand_pt, d, 0.022, 0.036, 0.036, P["brass_fitting"], outline=False)

    mk.obox(c, mk.add(hand_pt, d, 0.022), d, length, 0.034, 0.020, P["steel_blade"])
    mk.obox(c, mk.add(hand_pt, d, 0.030), d, max(0.0, length - 0.02), 0.014, 0.022, P["steel_edge"], outline=False)

    return mk.add(hand_pt, d, 0.022 + length)


def _render_shikomizue(c, left_hand, right_hand):
    """Renderiza a Shikomizue e os cortes Gyaku-Iai em combate."""
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    for hand in (left_hand, right_hand):
        mk.cbox(c, hand[0], hand[1], hand[2] - 0.015, 0.048, 0.048, 0.045, P["skin"], outline=True)

    if c.is_melee:
        prog = c.atk_progress
        is_pierce = c.extra_props.get("is_pierce", False) if c.extra_props else False

        if is_pierce:
            b_dir = mk.norm((fx * 0.95, fy * 0.95, 0.0))
            tip = _draw_shikomizue_blade(c, right_hand, b_dir, length=0.82)
            _draw_cane_scabbard(c, left_hand, mk.norm((-fx * 0.70 + px * 0.30, -fy * 0.70 + py * 0.30, -0.65)), length=0.85)
        else:
            if prog < 0.25:
                cane_dir = mk.norm((fx * 0.10 + px * 0.05, fy * 0.10 + py * 0.05, -0.98))
                _draw_cane_scabbard(c, right_hand, cane_dir, length=0.88)
            else:
                p_sub = (prog - 0.25) / 0.75
                arc_ang = -1.2 + p_sub * 2.5
                blade_dir = mk.norm((fx * math.cos(arc_ang) + px * math.sin(arc_ang), fy * math.cos(arc_ang) + py * math.sin(arc_ang), -0.05))
                tip = _draw_shikomizue_blade(c, right_hand, blade_dir, length=0.82)
                _draw_cane_scabbard(c, left_hand, mk.norm((-fx * 0.50 + px * 0.40, -fy * 0.50 + py * 0.40, -0.75)), length=0.85)

                if 0.10 < p_sub < 0.85:
                    mid = mk.lerp(right_hand, tip, 0.5)
                    prev_tip = (tip[0] - fx * 0.18, tip[1] - fy * 0.18, tip[2] + 0.05)
                    prev_mid = (mid[0] - fx * 0.10, mid[1] - fy * 0.10, mid[2] + 0.03)
                    mk.band(c, (mid, tip, prev_tip, prev_mid), P["slash_silver"] + (210,))
                    mk.band(c, (mk.lerp(mid, tip, 0.6), tip, prev_tip, mk.lerp(prev_mid, prev_tip, 0.6)), P["slash_core"] + (250,))
    else:
        # Bengala de caminhada vertical apoiada no chão
        cane_dir = mk.norm((fx * 0.08 + px * 0.05, fy * 0.08 + py * 0.05, -0.98))
        _draw_cane_scabbard(c, right_hand, cane_dir, length=0.88)


def draw_front(c, left_hand, right_hand):
    """Camada frontal: Shikomizue empunhada à frente do corpo."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    w_mid = ((left_hand[0] + right_hand[0]) * 0.5, (left_hand[1] + right_hand[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_shikomizue(c, left_hand, right_hand)
