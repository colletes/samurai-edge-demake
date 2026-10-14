"""
O-Rin, a Menestrel de Yoshiwara e Zoner Acústica (Ciclo 2):
- Menestrel e assassina graciosa de postura elegante e passos fluidos.
- Quimono de seda preto-azeviche com lírios carmesins estampados e detalhes dourados.
- Obi largo carmim com nó tradicional borboleta nas costas e mangas longas ondulantes.
- Olhos abertos penetrantes cor de âmbar dourado com delineado carmesim teatral (kumadori).
- Tatuagem floral delicada de lírio-da-ressurreição (Higanbana) subindo da clavícula ao pescoço.
- Brincos longos de sinos de prata ressonantes (suzu) e penteado em coque com kanzashi dourado.
- Tsugaru Shamisen com corpo de cerejeira nobre, cravelhas de marfim e 3 cordas de seda.
- Ataques puramente acústicos: palheta de marfim (bachi) disparando lâminas de vácuo Kamaitachi.
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth

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

    # Mão esquerda segura o braço do shamisen diante do peito
    left = (bx + fx * 0.16 + px * 0.12, by + fy * 0.16 + py * 0.12, tz + 0.18)
    # Mão direita segura a palheta (bachi) sobre a pele do corpo do instrumento
    right = (bx + fx * 0.18 - px * 0.06, by + fy * 0.18 - py * 0.06, tz + 0.04)
    return left, right


def attack_arms(c):
    """
    Animações de Ataque Sonoro:
    1. Kamaitachi (Lâminas de Vácuo): Palhetada percussiva descendente ultrarrápida.
    2. Acorde Ressonante: Golpe duplo nas cordas com vibração sonora expansiva.
    """
    p = c.atk_progress
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    is_resonance = c.extra_props.get("is_resonance", False) if c.extra_props else False

    if is_resonance:
        # Acorde de ressonância: ambas as mãos golpeiam e abrem em arco expansivo
        snap = math.sin(p * math.pi)
        left = (bx + fx * 0.14 + px * (0.10 + snap * 0.16), by + fy * 0.14 + py * (0.10 + snap * 0.16), tz + 0.16 + snap * 0.10)
        right = (bx + fx * 0.16 - px * (0.08 + snap * 0.18), by + fy * 0.16 - py * (0.08 + snap * 0.18), tz + 0.06 + snap * 0.12)
        return left, right

    # Palhetada Rápida Kamaitachi: mão direita corta para baixo com a bachi em movimento relâmpago
    stroke = math.sin(p * math.pi * 1.5)
    left = (bx + fx * 0.16 + px * 0.12, by + fy * 0.16 + py * 0.12, tz + 0.20)
    right = (
        bx + fx * (0.22 + p * 0.08) - px * 0.04,
        by + fy * (0.22 + p * 0.08) - py * 0.04,
        tz + 0.12 - stroke * 0.16
    )
    return left, right


# ---------------------------------------------------------------------------------------------------------------------
# Detalhamento Voxel do Guerreiro
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Trás da O-Rin:
    - O grande laço de seda carmesim do Obi (Musubi em nó de borboleta) com pontas caindo.
    - Mangas longas de seda (Furisode) que oscilam graciosamente com o vento.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    oz = c.pelvis_z + 0.08

    # Nó borboleta do Obi nas costas
    knot_x = bx - fx * 0.11
    knot_y = by - fy * 0.11
    mk.cbox(c, knot_x, knot_y, oz, 0.12, 0.06, 0.08, P["obi"], outline=True)
    mk.cbox(c, knot_x, knot_y, oz + 0.02, 0.14, 0.04, 0.04, P["obi_gold"], outline=False)

    # Pontas caídas do laço do obi
    trail, amp, freq = mk.motion(c, 0.04)
    offs = mk.cloth_offsets(c, 3, 0.6, trail, amp * 1.4, freq, (knot_x, knot_y))
    for i, o in enumerate(offs):
        mk.cbox(c, knot_x + o[0], knot_y + o[1], oz - 0.05 * (i + 1) + o[2], 0.07, 0.025, 0.06, P["obi"], outline=False)


def draw_legs(c):
    """
    Pernas delicadas: quimono longo até os tornozelos, meias brancas Tabi e sandálias Geta de madeira.
    """
    P = pal()
    for leg_key in ("L", "R"):
        ld = c.legs_data.get(leg_key)
        if not ld:
            continue
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]
        # Saia longa do quimono cobrindo as pernas
        mk.cbox(c, th[0], th[1], th[2], 0.13, 0.13, 0.22, P["kimono"], texture="silk")
        # Meia Tabi branca
        mk.cbox(c, sh[0], sh[1], sh[2] + 0.03, 0.09, 0.09, 0.16, P["tabi_white"])
        # Sandália de madeira Geta com tiras vermelhas
        mk.obox(c, (ft[0] - c.fx * 0.03, ft[1] - c.fy * 0.03, ft[2]), (c.fx, c.fy, 0.0), 0.12, 0.065, 0.035, P["geta"])
        mk.obox(c, (ft[0] - c.fx * 0.01, ft[1] - c.fy * 0.01, ft[2] + 0.03), (c.fx, c.fy, 0.0), 0.09, 0.055, 0.025, P["strap_red"], outline=False)


def draw_belt(c):
    """
    Faixa de cintura de seda Obi carmesim com fita dourada de amarração (Obijime).
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07

    # Obi largo de seda
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.01, c.pelvis_w * 0.70, 0.09, P["obi"], outline=True, texture="silk")
    # Cordão decorativo dourado Obijime no centro do obi
    mk.cbox(c, bx + fx * 0.07, by + fy * 0.07, z + 0.03, c.pelvis_w - 0.005, 0.015, 0.018, P["obi_gold"], outline=False)


def draw_torso(c):
    """
    Quimono de seda escura elegantemente transpassado:
    - Decote delicado com gola interna de seda branca.
    - Tatuagem floral de Higanbana (lírio-da-ressurreição) subindo pela clavícula esquerda.
    - Mangas amplas de seda que caem dos ombros.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    # 1. Gola interna de seda branca
    mk.cbox(c, bx + fx * 0.08, by + fy * 0.08, tz + 0.14, 0.09, 0.03, 0.10, P["collar_white"], outline=False)

    # 2. Pele da clavícula / decote
    mk.cbox(c, bx + fx * 0.075, by + fy * 0.075, tz + 0.16, 0.08, 0.025, 0.06, P["skin"], outline=False)

    # 3. Tatuagem floral de Higanbana (lírio-aranha vermelho) na clavícula/pescoço esquerdo
    mk.cbox(c, bx + fx * 0.082 + px * 0.03, by + fy * 0.082 + py * 0.03, tz + 0.17, 0.024, 0.015, 0.035, P["tattoo_higan"], outline=False)

    # 4. Quimono escuro sobreposto
    mk.cbox(c, bx, by, tz + 0.04, 0.20, 0.15, 0.22, P["kimono"], outline=True, texture="silk")
    # Detalhe floral carmesim bordado no peito
    mk.cbox(c, bx + fx * 0.085 - px * 0.03, by + fy * 0.085 - py * 0.03, tz + 0.08, 0.05, 0.02, 0.07, P["kimono_red"], outline=False)
    mk.cbox(c, bx + fx * 0.088 - px * 0.03, by + fy * 0.088 - py * 0.03, tz + 0.08, 0.02, 0.015, 0.03, P["kimono_gold"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """
    Braço feminino com manga esvoaçante de quimono (Furisode):
    - A manga de seda escura pende do antebraço até o cotovelo.
    """
    P = pal()
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["kimono"],
        sleeve_to=0.55,
        w=0.052,
        bend=0.03
    )


def draw_head(c):
    """
    Rosto e Penteado de O-Rin:
    - Olhos abertos e penetrantes cor de âmbar dourado com delineado carmesim teatral (kumadori sutil).
    - Tatuagem de lírio-aranha alcançando a lateral esquerda do pescoço.
    - Brincos longos de sinos de prata ressonantes (suzu) que balançam com a música.
    - Coque tradicional de cortesã decorado com kanzashi e presilhas douradas.
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    hz = c.head_z
    hw = c.head_w - 0.01  # Traços femininos delicados

    # 1. Rosto e queixo esculpidos
    mk.cbox(c, bx, by, hz, hw, hw, 0.14, P["skin"], outline=True)

    # 2. Cabelo negro lustroso em coque elaborado
    # Base do cabelo cobrindo topo e trás
    mk.cbox(c, bx - fx * 0.02, by - fy * 0.02, hz + 0.06, hw + 0.015, hw + 0.015, 0.11, P["hair"], outline=False)
    # Coque volumoso alto (Shimada)
    mk.cbox(c, bx - fx * 0.04, by - fy * 0.04, hz + 0.15, hw * 0.85, hw * 0.85, 0.08, P["hair_dark"], outline=True)
    # Presilha e grampos dourados Kanzashi
    mk.cbox(c, bx - fx * 0.02 + px * 0.06, by - fy * 0.02 + py * 0.06, hz + 0.17, 0.04, 0.02, 0.03, P["kanzashi_gold"], outline=False)
    mk.cbox(c, bx - fx * 0.02 - px * 0.06, by - fy * 0.02 - py * 0.06, hz + 0.17, 0.04, 0.02, 0.03, P["kanzashi_red"], outline=False)

    # 3. Brincos de sinos de prata ressonantes (Suzu) em ambas as orelhas
    for side_sign in (-1.0, 1.0):
        ear_x = bx - fx * 0.01 + px * (0.062 * side_sign)
        ear_y = by - fy * 0.01 + py * (0.062 * side_sign)
        # Fio de prata descendo da orelha
        mk.cbox(c, ear_x, ear_y, hz + 0.01, 0.008, 0.008, 0.035, P["bell_silver"], outline=False)
        # Sino esférico ressonante na ponta
        mk.cbox(c, ear_x, ear_y, hz - 0.03, 0.022, 0.022, 0.022, P["bell_silver_bright"], outline=True)

    if mk.facing_camera(c):
        front_d = hw / 2 + 0.005
        # Lábios rubros delicados
        mk.cbox(c, bx + fx * front_d, by + fy * front_d, hz + 0.02, 0.022, 0.012, 0.012, P["lip_red"], outline=False)

        # Olhos de Âmbar Dourado com delineado carmesim teatral alado
        for side in (-1.0, 1.0):
            ex = bx + fx * front_d + px * (0.026 * side)
            ey = by + fy * front_d + py * (0.026 * side)
            # Delineador carmesim alado (kumadori sutil)
            mk.cbox(c, ex + px * (0.010 * side), ey + py * (0.010 * side), hz + 0.068, 0.018, 0.010, 0.012, P["liner_crimson"], outline=False)
            # Íris de âmbar dourado brilhante
            mk.cbox(c, ex, ey, hz + 0.065, 0.016, 0.012, 0.014, P["eye_amber_bright"], outline=False)


def _draw_shamisen_prop(c, left_hand, right_hand):
    """
    Desenha o Tsugaru Shamisen empunhado em mãos:
    - Corpo de ressonância (Dō): caixa de cerejeira nobre com tampo de pele marfim.
    - Braço esguio (Sao): haste longa de madeira escura com as 3 cordas de seda.
    - Cravelhas de afinação (Itogomaki) em marfim no cabeçote.
    - Palheta triangular de marfim (Bachi) empunhada na mão direita.
    """
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # Vetor de orientação do shamisen (apoiado no colo e erguido na diagonal esquerda)
    shamisen_dir = mk.norm((fx * 0.40 + px * 0.45, fy * 0.40 + py * 0.45, 0.78))
    # Ponto central do corpo de ressonância (Dō) próximo à mão direita
    do_pt = (right_hand[0] + fx * 0.04, right_hand[1] + fy * 0.04, right_hand[2] - 0.02)

    # 1. Corpo de ressonância (Dō)
    mk.obox(c, mk.add(do_pt, shamisen_dir, -0.10), shamisen_dir, 0.20, 0.16, 0.10, P["shamisen_wood"], outline=True)
    # Tampo frontal claro de pele
    mk.obox(c, mk.add(do_pt, shamisen_dir, -0.08), shamisen_dir, 0.16, 0.14, 0.02, P["shamisen_skin"], outline=False)

    # 2. Braço do instrumento (Sao)
    sao_start = mk.add(do_pt, shamisen_dir, 0.10)
    sao_len = 0.55
    mk.obox(c, sao_start, shamisen_dir, sao_len, 0.035, 0.030, P["shamisen_wood_dark"], outline=True)

    # 3. Cabeçote (Tenjin) e cravelhas de marfim (Itogomaki)
    head_pt = mk.add(sao_start, shamisen_dir, sao_len)
    mk.obox(c, head_pt, shamisen_dir, 0.08, 0.045, 0.040, P["shamisen_wood"])
    # Cravelhas de marfim projetadas lateralmente
    mk.cbox(c, head_pt[0] + px * 0.035, head_pt[1] + py * 0.035, head_pt[2] + 0.02, 0.015, 0.04, 0.015, P["ivory_peg"], outline=False)
    mk.cbox(c, head_pt[0] - px * 0.035, head_pt[1] - py * 0.035, head_pt[2] + 0.04, 0.015, 0.04, 0.015, P["ivory_peg"], outline=False)

    # 4. Cordas de seda dourada esticadas
    mk.limb(c, mk.add(do_pt, shamisen_dir, -0.06), mk.add(head_pt, shamisen_dir, 0.04), 0.012, P["silk_string"], outline=False)

    # 5. Palheta de marfim (Bachi) na mão direita
    bachi_pt = (right_hand[0] + fx * 0.02, right_hand[1] + fy * 0.02, right_hand[2] + 0.01)
    mk.obox(c, bachi_pt, (fx, fy, 0.3), 0.07, 0.045, 0.012, P["bachi_ivory"], outline=True)

    return do_pt, mk.add(head_pt, shamisen_dir, 0.08)


def draw_front(c, left_hand, right_hand):
    """
    Desenho do Shamisen e efeitos visuais acústicos de ataque:
    - Kamaitachi: Lâminas de choque cortantes de vácuo sônico em arco ciano/dourado.
    - Acorde Ressonante: Onda de choque sônica expansiva concêntrica.
    """
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # Desenha o Shamisen empunhado
    do_pt, tip_pt = _draw_shamisen_prop(c, left_hand, right_hand)

    # Efeitos de Combate Acústico
    if c.is_melee:
        p = c.atk_progress
        is_resonance = c.extra_props.get("is_resonance", False) if c.extra_props else False

        if is_resonance:
            # Onda de choque esférica concêntrica do Acorde Ressonante
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
            # Kamaitachi: Lâmina cortante de vácuo sônico em arco veloz
            if 0.10 < p < 0.90:
                arc_w = 0.28 * math.sin(p * math.pi)
                wave_front = (do_pt[0] + fx * (0.35 + p * 0.55), do_pt[1] + fy * (0.35 + p * 0.55), do_pt[2] + 0.06)
                p0 = (wave_front[0] + px * arc_w, wave_front[1] + py * arc_w, wave_front[2] + 0.12)
                p1 = (wave_front[0] - px * arc_w, wave_front[1] - py * arc_w, wave_front[2] + 0.12)
                p2 = (wave_front[0] - px * arc_w * 0.6, wave_front[1] - py * arc_w * 0.6, wave_front[2] - 0.10)
                p3 = (wave_front[0] + px * arc_w * 0.6, wave_front[1] + py * arc_w * 0.6, wave_front[2] - 0.10)

                mk.band(c, (p0, p1, p2, p3), P["sonic_cyan"] + (210,))
                mk.band(c, (mk.lerp(p0, p1, 0.25), mk.lerp(p0, p1, 0.75), mk.lerp(p2, p3, 0.75), mk.lerp(p2, p3, 0.25)), P["sonic_core"] + (250,))
