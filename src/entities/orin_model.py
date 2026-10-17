"""
O-Rin, a Menestrel de Yoshiwara e Zoner Acústica (Ciclo 2):
- Menestrel e assassina graciosa de postura elegante e passos fluidos.
- Quimono de seda preto-azeviche com lírios carmesins estampados e detalhes dourados esculpido em malha contínua 3D.
- Obi largo carmim com nó tradicional borboleta nas costas e mangas longas ondulantes (Furisode).
- Olhos abertos penetrantes cor de âmbar dourado com delineado carmesim teatral (kumadori) e lábios de cereja.
- Tatuagem floral delicada de lírio-da-ressurreição (Higanbana) subindo da clavícula ao pescoço.
- Brincos longos de sinos de prata ressonantes (suzu) e penteado em coque alto Shimada com kanzashi dourado.
- Tsugaru Shamisen nobre de cerejeira com corpo de ressonância, cravelhas de marfim e bachi.
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

SKIN = (246, 216, 192)
SKIN_SHADOW = (216, 178, 150)

PALETTE = {
    # Seda do Quimono e Obi
    "kimono": (22, 20, 28),
    "torso": (22, 20, 28),
    "kimono_dark": (14, 12, 18),
    "kimono_red": (188, 28, 45),
    "kimono_gold": (228, 182, 60),
    "obi": (172, 24, 38),
    "belt": (172, 24, 38),
    "obi_gold": (235, 194, 68),
    "collar_white": (245, 242, 235),

    # Cabelo e Adornos
    "hair": (18, 16, 22),
    "hair_dark": (12, 10, 14),
    "hair_gloss": (45, 38, 52),
    "kanzashi_gold": (230, 188, 64),
    "kanzashi_red": (210, 32, 44),
    "bell_silver": (225, 230, 242),
    "bell_silver_bright": (255, 255, 255),

    # Rosto, Olhos e Tatuagem
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "eye_amber": (228, 154, 38),
    "eye_amber_bright": (255, 185, 65),
    "liner_crimson": (195, 25, 40),
    "lip_red": (205, 52, 68),
    "tattoo_higan": (180, 22, 36),

    # Calçados e Pernas
    "tabi_white": (240, 238, 232),
    "geta": (145, 96, 58),
    "strap_red": (185, 26, 40),
    "pants": (22, 20, 28),

    # Shamisen (Instrumento Musical)
    "shamisen_wood": (88, 34, 24),
    "shamisen_wood_dark": (58, 20, 14),
    "shamisen_skin": (244, 240, 230),
    "ivory_peg": (248, 244, 235),
    "silk_string": (240, 205, 110),
    "bachi_ivory": (250, 246, 238),

    # Ondas Sonoras e Vácuo Kamaitachi
    "sonic_cyan": (90, 215, 255),
    "sonic_core": (240, 255, 255),
    "sonic_gold": (255, 220, 85),
    "res_shock": (255, 75, 95),
}

MATERIALS = {
    "kimono": "silk",
    "kimono_dark": "silk",
    "obi": "silk",
    "collar_white": "silk",
    "geta": "wood",
    "shamisen_wood": "wood",
    "bell_silver": "metal",
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses de Braços e Animações Acústicas
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Postura elegante de segurar o Tsugaru Shamisen:
    - Mão esquerda apoia o braço superior do instrumento (sao).
    - Mão direita posiciona a palheta bachi sobre o corpo de ressonância.
    """
    breathe = math.sin(c.walk_timer * 2.6) * 0.010
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    left = (
        bx + fx * 0.16 + px * 0.16,
        by + fy * 0.16 + py * 0.16,
        tz + 0.22
    )
    right = (
        bx + fx * 0.12 - px * 0.08,
        by + fy * 0.12 - py * 0.08,
        tz + 0.06
    )
    return left, right


def walk_arms(c):
    """Passo suave e ritmado segurando o Shamisen sem oscilações bruscas."""
    breathe = math.sin(c.walk_timer * 5.0) * 0.012
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    left = (
        bx + fx * 0.15 + px * 0.15,
        by + fy * 0.15 + py * 0.15,
        tz + 0.20
    )
    right = (
        bx + fx * 0.11 - px * 0.07,
        by + fy * 0.11 - py * 0.07,
        tz + 0.05
    )
    return left, right


def attack_arms(c):
    """
    Dedilhada de Shamisen: Golpe acústico veloz da palheta de marfim (bachi).
    """
    p = c.atk_progress
    stroke = math.sin(p * math.pi)
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    left = (
        bx + fx * 0.18 + px * 0.14,
        by + fy * 0.18 + py * 0.14,
        tz + 0.24 + stroke * 0.02
    )
    right = (
        bx + fx * (0.12 + p * 0.08) - px * 0.04,
        by + fy * (0.12 + p * 0.08) - py * 0.04,
        tz + 0.08 - stroke * 0.14
    )
    return left, right


# ---------------------------------------------------------------------------------------------------------------------
# Detalhamento Voxel do Guerreiro
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Trás da O-Rin (Painter's Algorithm):
    - O grande laço de seda carmesim do Obi (Musubi em nó de borboleta) com pontas caindo.
    - Se o Shamisen estiver no lado oposto à câmera, desenha aqui antes do quimono para oclusão.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    oz = c.pelvis_z + 0.07
    d_torso = mk.depth(c, bx, by)

    # Nó borboleta do Obi nas costas
    d_back = mk.depth(c, bx - fx * 0.11, by - fy * 0.11)
    if d_back <= d_torso + 0.02:
        knot_x = bx - fx * 0.11
        knot_y = by - fy * 0.11
        mk.obox(c, (knot_x, knot_y, oz), (-fx, -fy, 0.0), 0.06, 0.14, 0.08, P["obi"])
        mk.obox(c, (knot_x - fx * 0.015, knot_y - fy * 0.015, oz + 0.01), (-fx, -fy, 0.0), 0.04, 0.16, 0.04, P["obi_gold"], outline=False)

        # Pontas caídas do laço do obi em fita contínua 3D
        trail, amp, freq = mk.motion(c, 0.04)
        offs = cloth.chain_offsets(2, c.walk_timer, 0.7, trail, (px, py), amp=amp * 1.3, freq=freq)
        p0 = (knot_x, knot_y, oz - 0.02)
        p1 = (knot_x - fx * 0.03 + offs[0][0], knot_y - fy * 0.03 + offs[0][1], oz - 0.09 + offs[0][2])
        p2 = (knot_x - fx * 0.06 + offs[1][0], knot_y - fy * 0.06 + offs[1][1], oz - 0.17 + offs[1][2])
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[p0, p1, p2],
            widths=[0.08, 0.09, 0.07],
            depth_thick=0.018,
            colors=[P["obi"], P["obi"]],
            side_vec=(px, py, 0.0),
            normal_vec=(-fx, -fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

    # Ordenação dinâmica: se o Shamisen estiver no lado oposto à câmera
    hand_l, hand_r = idle_arms(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_shamisen(c, hand_l, hand_r)


def draw_legs(c):
    """
    Quimono de seda preto longo contínuo até os tornozelos, meias brancas Tabi
    e sandálias Geta de madeira com tiras vermelhas.
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

        # Quimono longo em malha contínua 3D (saia tubular fluida)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, hem],
            widths=[0.125, 0.135, 0.145],
            depth_thick=0.110,
            colors=[P["kimono"], P["kimono_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Meia Tabi branca em malha contínua 3D descendo do quimono até a sandália
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[hem, ankle],
            widths=[0.065, 0.054],
            depth_thick=0.054,
            colors=[P["tabi_white"], P["tabi_white"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

        # Sandália de madeira Geta elevada com tiras hanao carmim
        flen, fwidth = 0.12, 0.062
        mk.obox(c, (foot[0] - c.fx * 0.02, foot[1] - c.fy * 0.02, foot[2]), (c.fx, c.fy, 0.0), flen, fwidth, 0.030, P["geta"])
        mk.obox(c, (foot[0] + c.fx * 0.01, foot[1] + c.fy * 0.01, foot[2] + 0.025), (c.fx, c.fy, 0.0), 0.04, 0.066, 0.018, P["strap_red"], outline=False)


def draw_obi(c):
    """Obi largo de seda carmesim com cordão dourado Obijime no centro."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    mk.cbox(c, bx, by, z, c.pelvis_w - 0.005, c.pelvis_w * 0.72, 0.085, P["obi"])
    mk.cbox(c, bx + fx * 0.085, by + fy * 0.085, z + 0.015, c.pelvis_w - 0.01, 0.016, 0.018, P["obi_gold"], outline=False)


def draw_torso(c):
    """
    Quimono de seda escura elegantemente transpassado:
    - Decote delicado com gola interna de seda branca em V.
    - Tatuagem floral de Higanbana (lírio-aranha vermelho) na clavícula esquerda.
    - Ornatos bordados em carmim e ouro.
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

        # Pele da clavícula / decote
        mk.obox(c, (bx + fx * (front - 0.006), by + fy * (front - 0.006), tz + 0.14), (0.0, 0.0, 1.0), 0.08, 0.045, 0.014, P["skin"], up=(fx, fy, 0.0), outline=False)

        # Tatuagem floral de Higanbana na clavícula/pescoço esquerdo
        mk.obox(c, (bx + fx * front + px * 0.032, by + fy * front + py * 0.032, tz + 0.165), (0.0, 0.0, 1.0), 0.022, 0.025, 0.012, P["tattoo_higan"], up=(fx, fy, 0.0), outline=False)

        # Detalhe floral carmesim e dourado bordado no peito
        mk.obox(c, (bx + fx * (front + 0.004) - px * 0.03, by + fy * (front + 0.004) - py * 0.03, tz + 0.075), (0.0, 0.0, 1.0), 0.045, 0.035, 0.010, P["kimono_red"], up=(fx, fy, 0.0), outline=False)
        mk.obox(c, (bx + fx * (front + 0.006) - px * 0.03, by + fy * (front + 0.006) - py * 0.03, tz + 0.075), (0.0, 0.0, 1.0), 0.018, 0.018, 0.008, P["kimono_gold"], up=(fx, fy, 0.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço feminino gracioso com quimono de seda."""
    P = pal()
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["kimono"],
        sleeve_to=0.55,
        w=0.048,
        bend=0.025
    )


def draw_sleeves(c, arms):
    """
    Mangas amplas de cortesã (Furisode) que caem dos ombros e cotovelos:
    - Draperia fluida em fita contínua 3D orientada com front-to-back normal_vec e lateral side_vec.
    """
    P = pal()
    trail, amp, freq = mk.motion(c, 0.06)

    for shoulder, elbow, side in arms:
        sign = 1.0 if side > 0 else -1.0
        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.8 * sign, trail, (c.px, c.py), amp=amp * 0.6, freq=freq)

        p0 = (elbow[0], elbow[1], elbow[2] + 0.02)
        p1 = (elbow[0] + o1[0] * 0.4, elbow[1] + o1[1] * 0.4, elbow[2] - 0.12 + o1[2] * 0.4)
        p2 = (elbow[0] + o2[0] * 0.7, elbow[1] + o2[1] * 0.7, elbow[2] - 0.24 + o2[2] * 0.7)

        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[p0, p1, p2],
            widths=[0.085, 0.115, 0.125],
            depth_thick=0.025,
            colors=[P["kimono"], P["kimono_dark"]],
            side_vec=(c.px * sign, c.py * sign, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )


def draw_head(c):
    """
    Cabeça de O-Rin:
    - Penteado elaborado Shimada: cúpula craniana polida e coque alto escultural.
    - Kanzashi dourado e pente vermelho de laca.
    - Brincos longos de sinos de prata (Suzu) balançando junto às orelhas.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # Cúpula e coque alto tradicional Shimada
    chignon_base = (bx - fx * 0.02, by - fy * 0.02, hz + 0.150)
    chignon_top = (bx - fx * 0.03, by - fy * 0.03, hz + 0.215)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        chignon_base, chignon_top,
        w_start=hw * 0.78, h_start=hw * 0.78,
        w_end=hw * 0.55, h_end=hw * 0.55,
        color=P["hair_dark"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Grampos Kanzashi dourados e pente carmim no coque
    mk.obox(c, (chignon_base[0] + px * 0.045, chignon_base[1] + py * 0.045, hz + 0.180), (px * 0.8, py * 0.8, 0.2), 0.065, 0.015, 0.018, P["kanzashi_gold"], outline=False)
    mk.obox(c, (chignon_base[0] - px * 0.045, chignon_base[1] - py * 0.045, hz + 0.180), (-px * 0.8, -py * 0.8, 0.2), 0.065, 0.015, 0.018, P["kanzashi_red"], outline=False)

    # Brincos de sinos de prata ressonantes (Suzu) em ambas as orelhas
    for side_sign in (-1.0, 1.0):
        ear_x = bx - fx * 0.015 + px * (0.062 * side_sign)
        ear_y = by - fy * 0.015 + py * (0.062 * side_sign)
        mk.obox(c, (ear_x, ear_y, hz + 0.040), (0.0, 0.0, -1.0), 0.045, 0.006, 0.006, P["bell_silver"], outline=False)
        mk.obox(c, (ear_x, ear_y, hz - 0.015), (0.0, 0.0, 1.0), 0.018, 0.018, 0.018, P["bell_silver_bright"], outline=True)


# ---------------------------------------------------------------------------------------------------------------------
# Renderizador Especializado do Tsugaru Shamisen
# ---------------------------------------------------------------------------------------------------------------------

def _draw_shamisen_prop(c, left_hand, right_hand):
    """
    Desenha o Tsugaru Shamisen empunhado em mãos:
    - Corpo de ressonância (Dō): cerejeira nobre com tampo de pele marfim.
    - Braço esguio (Sao): haste de madeira escura com as 3 cordas de seda.
    - Cravelhas de afinação (Itogomaki) em marfim.
    - Palheta triangular de marfim (Bachi) na mão direita.
    """
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    shamisen_dir = mk.norm((fx * 0.35 + px * 0.42, fy * 0.35 + py * 0.42, 0.78))
    do_pt = (right_hand[0] + fx * 0.03, right_hand[1] + fy * 0.03, right_hand[2] - 0.02)

    # 1. Corpo de ressonância (Dō)
    mk.obox(c, mk.add(do_pt, shamisen_dir, -0.09), shamisen_dir, 0.18, 0.15, 0.09, P["shamisen_wood"], outline=True)
    mk.obox(c, mk.add(do_pt, shamisen_dir, -0.07), shamisen_dir, 0.14, 0.13, 0.02, P["shamisen_skin"], outline=False)

    # 2. Braço do instrumento (Sao)
    sao_start = mk.add(do_pt, shamisen_dir, 0.09)
    sao_len = 0.52
    mk.obox(c, sao_start, shamisen_dir, sao_len, 0.032, 0.028, P["shamisen_wood_dark"], outline=True)

    # 3. Cabeçote (Tenjin) e cravelhas de marfim (Itogomaki)
    head_pt = mk.add(sao_start, shamisen_dir, sao_len)
    mk.obox(c, head_pt, shamisen_dir, 0.075, 0.040, 0.036, P["shamisen_wood"])
    mk.cbox(c, head_pt[0] + px * 0.032, head_pt[1] + py * 0.032, head_pt[2] + 0.02, 0.014, 0.036, 0.014, P["ivory_peg"], outline=False)
    mk.cbox(c, head_pt[0] - px * 0.032, head_pt[1] - py * 0.032, head_pt[2] + 0.04, 0.014, 0.036, 0.014, P["ivory_peg"], outline=False)

    # 4. Cordas de seda dourada esticadas
    mk.limb(c, mk.add(do_pt, shamisen_dir, -0.05), mk.add(head_pt, shamisen_dir, 0.03), 0.010, P["silk_string"], outline=False)

    # 5. Palheta de marfim (Bachi) na mão direita
    bachi_pt = (right_hand[0] + fx * 0.02, right_hand[1] + fy * 0.02, right_hand[2] + 0.01)
    mk.obox(c, bachi_pt, (fx, fy, 0.25), 0.065, 0.042, 0.012, P["bachi_ivory"], outline=True)

    return do_pt, mk.add(head_pt, shamisen_dir, 0.07)


def _render_shamisen(c, left_hand, right_hand):
    """Renderiza o Tsugaru Shamisen empunhado e seus efeitos de combate acústico."""
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    do_pt, tip_pt = _draw_shamisen_prop(c, left_hand, right_hand)

    if c.is_melee:
        p = c.atk_progress
        is_resonance = c.extra_props.get("is_resonance", False) if c.extra_props else False

        if is_resonance:
            wave_r = 0.35 * math.sin(p * math.pi)
            if wave_r > 0.04:
                rc = (c.base_x + fx * 0.15, c.base_y + fy * 0.15, c.torso_z + 0.08)
                pts = [
                    (rc[0] + px * wave_r, rc[1] + py * wave_r, rc[2]),
                    (rc[0] + fx * wave_r * 0.9, rc[1] + fy * wave_r * 0.9, rc[2] + wave_r * 0.6),
                    (rc[0] - px * wave_r, rc[1] - py * wave_r, rc[2]),
                    (rc[0] - fx * wave_r * 0.9, rc[1] - fy * wave_r * 0.9, rc[2] - wave_r * 0.6),
                ]
                mk.band(c, pts, P["res_shock"] + (190,))
        else:
            if 0.10 < p < 0.90:
                arc_w = 0.28 * math.sin(p * math.pi)
                wave_front = (do_pt[0] + fx * (0.35 + p * 0.55), do_pt[1] + fy * (0.35 + p * 0.55), do_pt[2] + 0.06)
                p0 = (wave_front[0] + px * arc_w, wave_front[1] + py * arc_w, wave_front[2] + 0.12)
                p1 = (wave_front[0] - px * arc_w, wave_front[1] - py * arc_w, wave_front[2] + 0.12)
                p2 = (wave_front[0] - px * arc_w * 0.6, wave_front[1] - py * arc_w * 0.6, wave_front[2] - 0.10)
                p3 = (wave_front[0] + px * arc_w * 0.6, wave_front[1] + py * arc_w * 0.6, wave_front[2] - 0.10)

                mk.band(c, (p0, p1, p2, p3), P["sonic_cyan"] + (210,))
                mk.band(c, (mk.lerp(p0, p1, 0.25), mk.lerp(p0, p1, 0.75), mk.lerp(p2, p3, 0.75), mk.lerp(p2, p3, 0.25)), P["sonic_core"] + (250,))


def draw_front(c, left_hand, right_hand):
    """Camada frontal: Tsugaru Shamisen empunhado à frente do corpo."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    w_mid = ((left_hand[0] + right_hand[0]) * 0.5, (left_hand[1] + right_hand[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_shamisen(c, left_hand, right_hand)
