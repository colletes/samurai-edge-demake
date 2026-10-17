"""
Tomoe, a Miko Kyudo Arqueira (Sacerdotisa Shinto do Arco Sagrado):
- Rosto anime gracioso com olhos luminosos castanho-quentes, brilho duplo e cílios alados; nariz delicado e lábios cereja.
- Cabelo longo negro sedoso (kurokami) em corte Hime com franja acima das sobrancelhas, mechas laterais (tsuya-kami) ordenadas por profundidade.
- Laço sagrado de seda escarlate (kami-musubi) amarrado na nuca com pontas longas esvoaçantes.
- Kosode cerimonial de seda branca pura com decote em V forrado em carmim escarlate e mangas drapeadas com cordões vermelhos (sode-kukuri).
- Hakama vermelha tradicional pregueada em malha 3D contínua (sem degraus ou prateleiras nos joelhos), tabi branco e sandálias Zori de palha com tiras de veludo carmim.
- Faixa na cintura com laço de cordão branco ceremonial e amuleto Omamori sagrado com sino dourado.
- Monumental arco longo assimétrico japonês Yumi (madeira de amoreira laqueada, núcleo de bambu dourado, ponteiras de latão e corda tsuru de seda branca) com flechas Ya de ponta de aço e penas brancas de falcão.
- Ordenação dinâmica de profundidade 3D (Painter's Algorithm) garantindo que arco e mãos fiquem perfeitamente ocluídos pelo dorso ao encarar de costas.
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.mesh_primitives import (
    draw_ribbon_mesh_3d,
    draw_tapered_frustum_3d,
    draw_sculpted_head_3d,
    draw_portrait_face_3d,
)

PALETTE = {
    "kosode": (252, 250, 248),
    "kosode_dark": (218, 214, 212),
    "collar_red": (195, 28, 36),
    "hakama": (195, 28, 36),
    "hakama_dark": (138, 18, 24),
    "hakama_crease": (165, 22, 28),
    "skin": (250, 228, 214),
    "skin_shadow": (224, 192, 175),
    "hair": (20, 20, 24),
    "hair_light": (45, 42, 52),
    "ribbon": (210, 32, 42),
    "ribbon_dark": (145, 18, 26),
    "tabi": (252, 250, 248),
    "zori": (195, 160, 115),
    "zori_cord": (195, 28, 36),
    "cord_white": (248, 248, 250),
    "omamori": (205, 30, 40),
    "omamori_gold": (235, 195, 65),
    "yumi_wood": (115, 68, 38),
    "yumi_bamboo": (185, 138, 75),
    "yumi_brass": (225, 185, 60),
    "tsuru": (250, 248, 240),
    "arrow_shaft": (168, 128, 72),
    "arrow_fletch": (245, 245, 248),
    "arrow_point": (215, 222, 235),
    "quiver": (68, 48, 38),
    "quiver_gold": (225, 185, 60),
}

MATERIALS = {
    "kosode": "silk", "kosode_dark": "silk",
    "hakama": "silk", "hakama_dark": "silk",
    "ribbon": "silk", "zori": "canvas",
    "yumi_brass": "gold", "arrow_point": "steel"
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Arco Yumi
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """Postura Kyudo neutra e serena: mão esquerda empunha o Yumi na altura da cintura ao lado, mão direita relaxada."""
    tz = c.torso_z + math.sin(c.walk_timer * 2.5) * 0.010
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    left = (bx + fx * 0.08 + px * 0.16, by + fy * 0.08 + py * 0.16, tz + 0.02)
    right = (bx + fx * 0.02 - px * 0.12, by + fy * 0.02 - py * 0.12, tz - 0.04)
    return left, right


def attack_arms(c):
    """Postura de disparo Kyudo (Kai): braço esquerdo estendido à frente sustentando o arco, direito puxando a corda junto à bochecha."""
    p = c.atk_progress if c.atk_progress is not None else 0.0
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    pull = math.sin(p * math.pi)
    left = (bx + fx * (0.24 + pull * 0.12) + px * 0.04,
            by + fy * (0.24 + pull * 0.12) + py * 0.04,
            tz + 0.14)
    right = (bx + fx * (0.04 - pull * 0.16) - px * (0.06 + pull * 0.06),
             by + fy * (0.04 - pull * 0.16) - py * (0.06 + pull * 0.06),
             tz + 0.16 + pull * 0.04)
    return left, right


def _current_hands(c):
    if c.is_melee and c.atk_progress is not None:
        return attack_arms(c)
    if c.is_moving and hasattr(c, "walk_timer"):
        tz = c.torso_z
        bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
        sw = math.sin(c.walk_timer * 7.5) * 0.035
        left = (bx + fx * 0.10 + px * 0.14 + fx * sw, by + fy * 0.10 + py * 0.14 + fy * sw, tz + 0.04)
        right = (bx + fx * 0.04 - px * 0.12 - fx * sw, by + fy * 0.04 - py * 0.12 - fy * sw, tz - 0.02)
        return left, right
    return idle_arms(c)


# ---------------------------------------------------------------------------------------------------------------------
# Monumental Arco Yumi 3D
# ---------------------------------------------------------------------------------------------------------------------

def _draw_yumi_bow(c, hand_l, hand_r):
    """
    Renderiza o monumental arco longo japonês Yumi:
    - Curvatura assimétrica tradicional (2/3 da extensão acima da empunhadura, 1/3 abaixo).
    - Corpo laminado em madeira de amoreira laqueada e bambu dourado.
    - Ponteiras e colarinhos de latão (motohazu e urazu).
    - Corda de seda branca (tsuru) esticada.
    - Flecha sagrada (Ya) nockada durante disparo.
    """
    P = pal()
    is_atk = c.is_melee and c.atk_progress is not None
    pull = math.sin(c.atk_progress * math.pi) if is_atk else 0.0

    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    if not is_atk and not c.is_moving:
        # Arco em repouso vertical ao lado apoiado perto do solo
        grip = (hand_l[0] + fx * 0.02, hand_l[1] + fy * 0.02, hand_l[2] + 0.02)
        bow_dir = (0.0, 0.0, 1.0)
        # O Yumi mede ~1.10m no jogo: 0.72m acima da empunhadura e 0.38m abaixo
        p_top = (grip[0] + fx * 0.04, grip[1] + fy * 0.04, grip[2] + 0.72)
        p_bot = (grip[0] - fx * 0.02, grip[1] - fy * 0.02, grip[2] - 0.38)
        p_mid_up = mk.lerp(grip, p_top, 0.5)
        p_mid_down = mk.lerp(grip, p_bot, 0.5)

        # Lâmina superior longa de bambu/madeira
        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_top, w_start=0.032, h_start=0.024, w_end=0.022, h_end=0.016, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)
        mk.obox(c, p_mid_up, bow_dir, 0.35, 0.014, 0.025, P["yumi_bamboo"], up=(fx, fy, 0.0), outline=False)
        # Ponteira superior de latão
        mk.obox(c, p_top, bow_dir, 0.035, 0.024, 0.024, P["yumi_brass"], outline=False)

        # Lâmina inferior curta
        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_bot, w_start=0.032, h_start=0.024, w_end=0.024, h_end=0.018, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)
        mk.obox(c, p_mid_down, (0.0, 0.0, -1.0), 0.20, 0.014, 0.025, P["yumi_bamboo"], up=(fx, fy, 0.0), outline=False)
        # Ponteira inferior de latão
        mk.obox(c, p_bot, (0.0, 0.0, -1.0), 0.030, 0.024, 0.024, P["yumi_brass"], outline=False)

        # Empunhadura de couro/tecido vermelho (Nigiri)
        mk.obox(c, (grip[0], grip[1], grip[2] - 0.04), bow_dir, 0.08, 0.036, 0.030, P["collar_red"], up=(fx, fy, 0.0), outline=False)

        # Corda Tsuru tensionada
        t_top = (p_top[0] - fx * 0.03, p_top[1] - fy * 0.03, p_top[2] - 0.02)
        t_bot = (p_bot[0] - fx * 0.03, p_bot[1] - fy * 0.03, p_bot[2] + 0.02)
        mk.limb(c, t_top, t_bot, 0.010, P["tsuru"], outline=False)

    else:
        # Arco empunhado dinamicamente no ataque ou em corrida
        grip = (hand_l[0] + fx * 0.05, hand_l[1] + fy * 0.05, hand_l[2] + 0.02)
        bow_vec = mk.norm((fx * 0.15 + px * 0.05, fy * 0.15 + py * 0.05, 0.98))

        p_top = mk.add(grip, bow_vec, 0.70)
        p_bot = mk.add(grip, bow_vec, -0.38)

        # Curvatura no ataque sob tensão
        c_curve = mk.norm((fx, fy, 0.0))
        p_top_c = mk.add(p_top, c_curve, -0.06 * pull)
        p_bot_c = mk.add(p_bot, c_curve, -0.04 * pull)

        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_top_c, w_start=0.034, h_start=0.024, w_end=0.022, h_end=0.016, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)
        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_bot_c, w_start=0.034, h_start=0.024, w_end=0.024, h_end=0.018, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)

        # Empunhadura Nigiri
        mk.obox(c, mk.add(grip, bow_vec, -0.04), bow_vec, 0.08, 0.036, 0.030, P["collar_red"], up=(fx, fy, 0.0), outline=False)

        # Corda Tsuru (puxada até a mão direita no ataque)
        t_top = mk.add(p_top_c, (-fx * 0.02, -fy * 0.02, 0.0), 1.0)
        t_bot = mk.add(p_bot_c, (-fx * 0.02, -fy * 0.02, 0.0), 1.0)
        nock_point = mk.add(hand_r, (fx * 0.02, fy * 0.02, 0.0), 1.0) if is_atk else mk.lerp(t_top, t_bot, 0.5)

        mk.limb(c, t_top, nock_point, 0.010, P["tsuru"], outline=False)
        mk.limb(c, nock_point, t_bot, 0.010, P["tsuru"], outline=False)

        # Flecha sagrada Ya nockada
        if is_atk and pull >= 0.15:
            arrow_dir = mk.norm(mk.sub(grip, nock_point))
            arrow_len = 0.62
            # Haste de bambu
            mk.obox(c, nock_point, arrow_dir, arrow_len, 0.014, 0.014, P["arrow_shaft"], outline=False)
            # Ponta de aço afiado
            tip = mk.add(nock_point, arrow_dir, arrow_len)
            mk.obox(c, tip, arrow_dir, 0.045, 0.020, 0.014, P["arrow_point"], outline=False)
            # Penas de falcão brancas (fletching)
            mk.obox(c, nock_point, arrow_dir, 0.08, 0.030, 0.010, P["arrow_fletch"], up=(0.0, 0.0, 1.0), outline=False)


# ---------------------------------------------------------------------------------------------------------------------
# Cabelo Kurokami, Mechas Laterais e Laço Kami-Musubi
# ---------------------------------------------------------------------------------------------------------------------

def _lock_is_behind(c, side_sign):
    """Determina se a mecha lateral esquerda (-1) ou direita (+1) está atrás da cabeça."""
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    lx = bx + fx * 0.02 + px * 0.065 * side_sign
    ly = by + fy * 0.02 + py * 0.065 * side_sign
    return mk.depth(c, lx, ly) < mk.depth(c, bx, by) - 0.008


def _side_lock(c, side_sign):
    """Mecha lateral graciosa (tsuya-kami) emoldurando as bochechas no corte Hime."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.06)
    o = mk.cloth_offsets(c, 1, 0.8 * side_sign, trail, amp * 1.2, freq * 1.1, (bx, by))[0]

    p0 = (bx + fx * 0.042 + px * 0.048 * side_sign, by + fy * 0.042 + py * 0.048 * side_sign, hz + 0.138)
    p1 = (bx + fx * 0.046 + px * 0.052 * side_sign + o[0] * 0.4, by + fy * 0.046 + py * 0.052 * side_sign + o[1] * 0.4, hz + 0.070)
    p2 = (bx + fx * 0.048 + px * 0.048 * side_sign + o[0], by + fy * 0.048 + py * 0.048 * side_sign + o[1], hz + 0.005 + o[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1, p2],
        widths=[0.022, 0.018, 0.010],
        depth_thick=0.010,
        colors=[P["hair"], P["hair_light"]],
        side_vec=(px * side_sign, py * side_sign, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )


def _draw_flowing_hair(c):
    """Cabelo longo negro sedoso (kurokami) descendo pelas costas até a cintura com ondulação de vento."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.08)

    # Raiz na nuca abaixo da fita vermelha
    p0 = (bx - fx * 0.065, by - fy * 0.065, hz + 0.100)

    offs = cloth.chain_offsets(3, c.walk_timer, 0.0, trail, (px, py), amp=amp * 1.8, freq=freq * 1.1, wind=cloth.wind_at(bx, by))

    p1 = (bx - fx * 0.085 + offs[0][0], by - fy * 0.085 + offs[0][1], hz + 0.020 + offs[0][2])
    p2 = (bx - fx * 0.095 + offs[1][0], by - fy * 0.095 + offs[1][1], c.torso_z + 0.080 + offs[1][2])
    p3 = (bx - fx * 0.105 + offs[2][0], by - fy * 0.105 + offs[2][1], c.pelvis_z + 0.060 + offs[2][2])

    # Faixa volumosa central de cabelo
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1, p2, p3],
        widths=[0.115, 0.135, 0.125, 0.085],
        depth_thick=0.045,
        colors=[P["hair"], P["hair_light"], P["hair"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )


def _draw_kami_musubi_ribbon(c):
    """Laço sagrado de seda carmim (kami-musubi) com asas volumosas e pontas esvoaçantes."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    root = (bx - fx * 0.075, by - fy * 0.075, hz + 0.115)

    # Nó central
    mk.cbox(c, root[0], root[1], root[2], 0.038, 0.038, 0.035, P["ribbon"])

    # Asas do laço arqueadas diagonalmente
    for s in (-1.0, 1.0):
        w_dir = mk.norm((px * s * 0.85 - fx * 0.15, py * s * 0.85 - fy * 0.15, 0.40))
        mk.obox(c, root, w_dir, 0.085, 0.024, 0.045, P["ribbon"], up=(fx, fy, 0.0), outline=False)

    # Fitas longas penduradas balançando
    trail, amp, freq = mk.motion(c, 0.07)
    for k, s in enumerate((-1.0, 1.0)):
        offs = cloth.chain_offsets(2, c.walk_timer, 0.9 * k, trail, (px, py), amp=amp * 1.6, freq=freq * 1.2)
        r0 = (root[0] + px * 0.015 * s, root[1] + py * 0.015 * s, root[2] - 0.015)
        r1 = (r0[0] - fx * 0.02 + offs[0][0], r0[1] - fy * 0.02 + offs[0][1], r0[2] - 0.06 + offs[0][2])
        r2 = (r1[0] - fx * 0.02 + offs[1][0], r1[1] - fy * 0.02 + offs[1][1], r1[2] - 0.07 + offs[1][2])
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[r0, r1, r2],
            widths=[0.024, 0.020, 0.014],
            depth_thick=0.008,
            colors=[P["ribbon"], P["ribbon_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(-fx, -fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )


# ---------------------------------------------------------------------------------------------------------------------
# Ganchos de Renderização (Painter's Algorithm)
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Mechas laterais que caem no lado oculto da cabeça.
    - Cabelo longo esvoaçante e laço Kami-Musubi nas costas.
    - Arco Yumi e mãos se estiverem atrás do tronco ao encarar de costas.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)

    # 1. Mechas laterais do lado oculto
    for s in (-1.0, 1.0):
        if _lock_is_behind(c, s):
            _side_lock(c, s)

    # 2. Cabelo longo e laço traseiro se atrás do crânio
    d_back_hair = mk.depth(c, c.base_x - c.fx * 0.08, c.base_y - c.fy * 0.08)
    if d_back_hair <= d_torso + 0.02:
        _draw_flowing_hair(c)
        _draw_kami_musubi_ribbon(c)

    # 3. Yumi e mãos se estiverem atrás do tronco
    hand_l, hand_r = _current_hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _draw_yumi_bow(c, hand_l, hand_r)


def draw_legs(c):
    """Hakama vermelha pregueada contínua em malha 3D (sem degraus de joelho), tabi branco e zori de palha."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.04)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0
        flare = 0.04 * c.lunge_curve

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.8 * sign, trail, (c.px, c.py), amp=amp * 0.6, freq=freq, wind=cloth.wind_at(foot[0], foot[1]))

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.5, sh[1] + o1[1] * 0.5, sh[2] + 0.16)
        ankle = (foot[0] + o2[0] * 0.4, foot[1] + o2[1] * 0.4, foot[2] + 0.05)

        # Hakama pregueada ampla em malha 3D contínua
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, ankle],
            widths=[0.125, 0.155 + flare, 0.170 + flare],
            depth_thick=0.115,
            colors=[P["hakama"], P["hakama_dark"], P["hakama_crease"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Meia Tabi branca
        mk.obox(c, (foot[0] + c.fx * 0.015, foot[1] + c.fy * 0.015, foot[2] + 0.015), (c.fx, c.fy, 0.0), 0.11, 0.060, 0.038, P["tabi"])
        # Sandália Zori de palha com sola de madeira
        mk.obox(c, (foot[0], foot[1], foot[2] - 0.010), (c.fx, c.fy, 0.0), 0.125, 0.066, 0.018, P["zori"])
        # Tira de veludo carmim da zori
        mk.obox(c, (foot[0] + c.fx * 0.025, foot[1] + c.fy * 0.025, foot[2] + 0.025), (c.fx, c.fy, 0.0), 0.020, 0.068, 0.016, P["zori_cord"], outline=False)


def draw_obi(c):
    """Cós da Hakama carmim com cordões brancos cerimoniais atados na frente e Omamori no quadril."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    # Cós largo da hakama
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.008, c.pelvis_w * 0.76, 0.065, P["hakama_dark"])

    # Cordão cerimonial branco (himo)
    mk.cbox(c, bx + fx * 0.086, by + fy * 0.086, z + 0.010, 0.065, 0.022, 0.035, P["cord_white"], outline=False)

    # Pontas caídas do nó do cordão branco
    trail, amp, freq = mk.motion(c, 0.05)
    offs = cloth.chain_offsets(2, c.walk_timer, 0.8, trail, (px, py), amp=amp * 1.3, freq=freq)
    for i, o in enumerate(offs):
        mk.cbox(c, bx + fx * 0.095 + px * 0.018 + o[0],
                by + fy * 0.095 + py * 0.018 + o[1],
                z - 0.045 * (i + 1) + o[2],
                0.022, 0.016, 0.050, P["cord_white"], outline=False)

    # Amuleto sagrado Omamori carmim no quadril direito com sino dourado
    bag = (bx - px * 0.125 - fx * 0.02, by - py * 0.125 - fy * 0.02, z - 0.05)
    mk.obox(c, bag, (0.0, 0.0, -1.0), 0.075, 0.045, 0.022, P["omamori"], up=(px, py, 0.0), outline=False)
    # Sino dourado (suzu)
    mk.cbox(c, bag[0], bag[1], bag[2] + 0.015, 0.020, 0.020, 0.020, P["omamori_gold"], outline=False)


def draw_torso(c):
    """
    Kosode cerimonial de seda branca pura:
    - Colarinho em V com forro carmim exposto (eri).
    - Pele de porcelana delicada da clavícula à mostra.
    """
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.090

    # Decote frontal com forro carmim
    if mk.depth(c, fx, fy) > -0.05:
        apex = (bx + fx * front, by + fy * front, tz + 0.100)
        for s in (-1.0, 1.0):
            top = (bx + fx * (front - 0.003) + px * 0.052 * s, by + fy * (front - 0.003) + py * 0.052 * s, tz + 0.245)
            # Forro carmim
            draw_tapered_frustum_3d(c.surface, c.camera, top, apex, w_start=0.026, h_start=0.014, w_end=0.016, h_end=0.010, color=P["collar_red"], up=(0.0, 0.0, 1.0), outline=False, alpha=c.alpha)
            # Borda externa branca do Kosode
            top_w = (top[0] - px * 0.006 * s, top[1] - py * 0.006 * s, top[2] - 0.004)
            apex_w = (apex[0] - px * 0.004 * s, apex[1] - py * 0.004 * s, apex[2] + 0.006)
            draw_tapered_frustum_3d(c.surface, c.camera, top_w, apex_w, w_start=0.014, h_start=0.012, w_end=0.008, h_end=0.008, color=P["kosode_dark"], up=(0.0, 0.0, 1.0), outline=False, alpha=c.alpha)

        # Pele delicada no centro do decote
        mk.obox(c, (bx + fx * (front - 0.004), by + fy * (front - 0.004), tz + 0.155), (0.0, 0.0, 1.0), 0.075, 0.038, 0.014, P["skin"], up=(fx, fy, 0.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço esguio feminino de Miko."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.20)
    h = (hand[0], hand[1], hand[2] - 0.060)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.025), (0.0, 0.0, -0.025))

    mk.limb(c, s, e, 0.046, P["skin"], w_end=0.040)
    mk.limb(c, e, h, 0.040, P["skin"], w_end=0.034)
    mk.cbox(c, h[0], h[1], h[2] - 0.020, 0.040, 0.040, 0.040, P["skin"])
    return s, e


def draw_sleeves(c, arms):
    """Mangas amplas e fluidas de Miko em seda branca pura, com caimento vertical e cordões carmim (sode-kukuri)."""
    P = pal()
    for k, (s, e, side) in enumerate(arms):
        anchor = (s[0] + c.px * side * 0.015, s[1] + c.py * side * 0.015, s[2] + 0.008)
        mid = mk.add(mk.lerp(s, e, 0.45), (c.px * side * 0.025, c.py * side * 0.025, -0.035))
        hem = mk.add(mk.lerp(s, e, 0.85), (c.px * side * 0.035, c.py * side * 0.035, -0.110))

        # Manga de seda branca pura drapeada
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[anchor, mid, hem],
            widths=[0.105, 0.140, 0.160],
            depth_thick=0.078,
            colors=[P["kosode"], P["kosode_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Cordão carmim (sode-kukuri) atado no punho da manga
        mk.obox(c, (hem[0], hem[1], hem[2] + 0.012), (0.0, 0.0, -1.0),
                0.016, 0.160, 0.080, P["collar_red"], up=(c.fx, c.fy, 0.0), outline=False)


def draw_head(c):
    """
    Cabeça de Tomoe:
    - Crânio esculpido 3D com olhos castanho-quentes expressivos, nariz delicado e lábios cereja via draw_portrait_face_3d.
    - Franja Hime reta estritamente acima das sobrancelhas (z >= hz + 0.108).
    - Mechas laterais tsuya-kami emoldurando a face se visíveis da câmera.
    - Cabelo longo traseiro e laço Kami-Musubi (se visíveis da câmera).
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    d_torso = mk.depth(c, bx, by)

    # Franja reta Hime clássica estritamente acima das sobrancelhas (z >= hz + 0.108)
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.005
        # Painel central da franja reta
        p0 = (bx + fx * front_d, by + fy * front_d, hz + 0.140)
        p1 = (bx + fx * (front_d + 0.002), by + fy * (front_d + 0.002), hz + 0.116)
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            p0, p1,
            w_start=0.088, h_start=0.014,
            w_end=0.082, h_end=0.010,
            color=P["hair"],
            up=(0.0, 0.0, 1.0),
            outline=False,
            alpha=c.alpha,
        )

    # Mechas laterais tsuya-kami do lado visível da câmera
    for s in (-1.0, 1.0):
        if not _lock_is_behind(c, s):
            _side_lock(c, s)

    # Cabelo longo e laço traseiro se estiverem do lado visível da câmera
    d_back_hair = mk.depth(c, bx - fx * 0.08, by - fy * 0.08)
    if d_back_hair > d_torso + 0.02:
        _draw_flowing_hair(c)
        _draw_kami_musubi_ribbon(c)


def draw_front(c, arm_l, arm_r):
    """
    Camada frontal (Painter's Algorithm):
    - O monumental Yumi e flecha são desenhados aqui APENAS se as mãos/arco estiverem à frente do tronco.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.060)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.060)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)

    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _draw_yumi_bow(c, hand_l, hand_r)
