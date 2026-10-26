"""
Daiki, o Peregrino do Bastão Bō (Ciclo 5):
- Monge-peregrino errante (Yamabushi / Komusō) de porte atlético e olhar marcial resoluto.
- Faixa Hachimaki de palha trançada na testa com nó na nuca e coque Chonmage negro firme.
- Túnica rústica de cânhamo azul-ardósia com o ombro e peitoral esquerdo musculoso expostos.
- Grande colar de contas Juzu de madeira de sândalo cruzando o peito e chapéu Kasa de palha nas costas.
- Munhequeiras brancas (Tekko), faixa de cânhamo na cintura, calças escuras (Hakama-shita) com polainas Kyahan em malha 3D contínua e sandálias Waraji.
- Bastão Longo Bō de Carvalho (Roku-shaku Bō ~1.85m) reforçado com ponteiras e anéis de ferro forjado.
- Ordenação dinâmica Painter's Algorithm para oclusão 360° perfeita.
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

SKIN = (224, 178, 142)
SKIN_SHADOW = (182, 136, 102)

PALETTE = {
    # Túnica de Peregrino (Cânhamo Azul-Ardósia)
    "tunic": (54, 72, 92),
    "torso": (54, 72, 92),
    "tunic_dark": (36, 48, 64),
    "tunic_light": (76, 98, 122),
    "sash": (218, 204, 174),
    "sash_dark": (175, 160, 130),
    "belt": (218, 204, 174),

    # Faixa de Palha, Chapéu Kasa e Cabelos
    "straw_band": (212, 184, 128),
    "straw_dark": (164, 136, 86),
    "kasa_straw": (204, 172, 114),
    "kasa_rim": (148, 118, 68),
    "hair": (24, 22, 26),
    "hair_dark": (14, 12, 16),

    # Rosário Juzu de Madeira e Ferro
    "juzu_bead": (142, 62, 36),
    "juzu_dark": (96, 38, 22),
    "juzu_accent": (215, 175, 85),

    # Calças, Kyahan, Tekko e Waraji
    "pants": (34, 42, 56),
    "pants_dark": (22, 28, 38),
    "kyahan": (222, 214, 196),
    "kyahan_strap": (42, 38, 34),
    "tekko": (232, 226, 212),
    "waraji": (188, 156, 102),
    "waraji_strap": (165, 42, 36),

    # Anatomia
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "neck": SKIN,
    "eye": (82, 54, 34),
    "brow": (26, 22, 20),
    "lip": (172, 118, 104),

    # Bastão Bō de Carvalho e Ponteiras de Ferro
    "bo_wood": (122, 76, 42),
    "bo_wood_dark": (84, 50, 26),
    "bo_grip": (228, 222, 208),
    "bo_iron": (68, 74, 84),
    "bo_steel_ring": (195, 204, 216),
    "bo_gold_ring": (212, 172, 78),
    "wind_aura": (190, 238, 215),
    "wind_core": (240, 255, 248),
}

MATERIALS = {
    "tunic": "canvas",
    "tunic_dark": "canvas",
    "pants": "canvas",
    "kyahan": "canvas",
    "sash": "canvas",
    "bo_wood": "wood",
    "bo_iron": "metal",
    "bo_steel_ring": "steel",
    "bo_gold_ring": "gold",
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Animação do Bastão Bō
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Guarda Clássica Bojutsu (Chudan-no-Kamae):
    - Mão direita segura o terço posterior do Bō junto ao quadril.
    - Mão esquerda avança segurando o centro-frente do bastão em diagonal firme.
    """
    breathe = math.sin(c.walk_timer * 2.5) * 0.010
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    pose = c.extra_props.get("pose") if c.extra_props else None

    if pose == "pilgrim_bow":
        # Saudação Gassho com o bastão vertical junto ao braço direito
        left = (bx + fx * 0.14 + px * 0.04, by + fy * 0.14 + py * 0.04, tz + 0.16)
        right = (bx + fx * 0.14 - px * 0.04, by + fy * 0.14 - py * 0.04, tz + 0.16)
        return left, right

    if pose == "bo_plant_stance":
        # Posição de monge sentinela com o Bō cravado verticalmente na vertical ao lado
        right = (bx + fx * 0.12 - px * 0.16, by + fy * 0.12 - py * 0.16, tz + 0.28)
        left = (bx + fx * 0.08 + px * 0.12, by + fy * 0.08 + py * 0.12, tz + 0.12)
        return left, right

    if pose == "bo_twirl":
        # Braços sustentando o centro de gravidade do bastão giratório em transição acrobática
        twirl_prog = c.extra_props.get("twirl_progress", 0.0) if c.extra_props else 0.0
        bob = math.sin(twirl_prog * math.pi * 4.0) * 0.02
        left = (bx + fx * 0.16 + px * 0.06, by + fy * 0.16 + py * 0.06, tz + 0.14 + bob)
        right = (bx + fx * 0.16 - px * 0.06, by + fy * 0.16 - py * 0.06, tz + 0.14 - bob)
        return left, right

    left = (
        bx + fx * 0.18 + px * 0.10,
        by + fy * 0.18 + py * 0.10,
        tz + 0.15,
    )
    right = (
        bx - fx * 0.04 - px * 0.13,
        by - fy * 0.04 - py * 0.13,
        tz + 0.08,
    )
    return left, right


def walk_arms(c):
    """Passada ágil de peregrino da montanha mantendo o Bō em equilíbrio transversal."""
    sw = math.sin(c.walk_timer * 8.0) * 0.08
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    left = (
        bx + fx * (0.18 + sw * 0.05) + px * 0.10,
        by + fy * (0.18 + sw * 0.05) + py * 0.10,
        tz + 0.15 + abs(sw) * 0.02,
    )
    right = (
        bx - fx * (0.04 + sw * 0.05) - px * 0.13,
        by - fy * (0.04 + sw * 0.05) - py * 0.13,
        tz + 0.08 + abs(sw) * 0.02,
    )
    return left, right


def attack_arms(c):
    """
    Ataques de Bojutsu:
    - Salto com Vara / Impacto Meteoro (`is_vault=True` ou `state == 'POLE_VAULT'`): ergue o bastão acima e crava/desce em arco.
    - Golpe Primário: Estocada de longo alcance (2.8m) seguida de varredura giratória repelente.
    """
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    prog = c.atk_progress if c.atk_progress is not None else 0.0
    is_vault = (c.state == "POLE_VAULT") or (c.extra_props.get("is_vault", False) if c.extra_props else False)

    if is_vault:
        if prog < 0.40:
            # Impulso na vara
            t = prog / 0.40
            left = (bx + fx * 0.16 + px * 0.08, by + fy * 0.16 + py * 0.08, tz + 0.24 + t * 0.18)
            right = (bx + fx * 0.14 - px * 0.08, by + fy * 0.14 - py * 0.08, tz + 0.20 + t * 0.18)
        else:
            # Queda meteórica esmagadora a duas mãos
            t = (prog - 0.40) / 0.60
            drop = t ** 1.6
            reach = 0.22 + drop * 0.24
            z_h = tz + 0.42 - drop * 0.44
            left = (bx + fx * reach + px * 0.06, by + fy * reach + py * 0.06, z_h + 0.04)
            right = (bx + fx * (reach - 0.10) - px * 0.06, by + fy * (reach - 0.10) - py * 0.06, z_h)
        return left, right

    # Estocada de Longo Alcance + Giro Varredura
    if prog < 0.25:
        # Recuo de alavanca junto ao quadril
        t = prog / 0.25
        left = (bx + fx * (0.14 - t * 0.06) + px * 0.12, by + fy * (0.14 - t * 0.06) + py * 0.12, tz + 0.14)
        right = (bx - fx * (0.08 + t * 0.10) - px * 0.14, by - fy * (0.08 + t * 0.10) - py * 0.14, tz + 0.10)
    elif prog < 0.68:
        # Estocada explosiva de ponta + varredura lateral
        t = (prog - 0.25) / 0.43
        thrust = math.sin(t * math.pi)
        left = (bx + fx * (0.28 + thrust * 0.22) + px * (0.06 - t * 0.10), by + fy * (0.28 + thrust * 0.22) + py * (0.06 - t * 0.10), tz + 0.16)
        right = (bx + fx * (0.10 + thrust * 0.18) - px * 0.08, by + fy * (0.10 + thrust * 0.18) - py * 0.08, tz + 0.15)
    else:
        # Retorno à guarda Chudan
        t = (prog - 0.68) / 0.32
        left = (bx + fx * (0.24 - t * 0.06) + px * 0.10, by + fy * (0.24 - t * 0.06) + py * 0.10, tz + 0.15)
        right = (bx - fx * 0.04 - px * 0.13, by - fy * 0.04 - py * 0.13, tz + 0.08)

    return left, right


def _current_hands(c):
    if c.is_melee and c.atk_progress is not None:
        return attack_arms(c)
    if c.is_moving:
        return walk_arms(c)
    return idle_arms(c)


# ---------------------------------------------------------------------------------------------------------------------
# Hooks do Modelo Voxel 3D (Chamados por voxel_models.py)
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    1. Chapéu de palha trançada Komusō/Yamabushi (Ajirogasa) pendurado nas costas quando visto de frente,
       ou renderizado sobre o dorso quando de costas.
    2. Fitas da faixa de palha Hachimaki esvoaçando na nuca.
    3. Bastão Bō quando o personagem está voltado para o fundo.
    """
    P = pal()
    bx, by, tz, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.torso_z, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    d_torso = mk.depth(c, bx, by)

    # 1. Pontas da faixa Hachimaki na nuca
    d_nape = mk.depth(c, bx - fx * 0.08, by - fy * 0.08)
    if d_nape <= d_torso + 0.03:
        knot_pt = (bx - fx * (hw * 0.50 + 0.012), by - fy * (hw * 0.50 + 0.012), hz + 0.105)
        mk.obox(c, knot_pt, (-fx, -fy, 0.0), 0.036, 0.036, 0.036, P["straw_dark"], outline=False)

        trail, amp, freq = mk.motion(c, 0.04)
        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.7, trail, (px, py), amp=amp * 0.7, freq=freq)
        p0 = knot_pt
        p1 = (knot_pt[0] - fx * 0.05 + o1[0], knot_pt[1] - fy * 0.05 + o1[1], hz + 0.05 + o1[2])
        p2 = (knot_pt[0] - fx * 0.09 + o2[0], knot_pt[1] - fy * 0.09 + o2[1], hz - 0.02 + o2[2])
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[p0, p1, p2],
            widths=[0.030, 0.034, 0.024],
            depth_thick=0.012,
            colors=[P["straw_band"], P["straw_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(-fx, -fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

    # 2. Chapéu Kasa de palha nas costas (se as costas estão atrás do peito em relação à câmera)
    if mk.depth(c, bx - fx * 0.12, by - fy * 0.12) < d_torso:
        _render_back_kasa(c)

    # 3. Ordenação do Bastão Bō se as mãos estiverem atrás do tronco
    hand_l, hand_r = _current_hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_bo_staff(c, hand_l, hand_r)


def _render_back_kasa(c):
    """Renderiza o chapéu cônico de palha trançada pendurado nas costas do peregrino."""
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    kasa_base = (bx - fx * 0.125, by - fy * 0.125, tz + 0.16)
    kasa_tip = (bx - fx * 0.215, by - fy * 0.215, tz + 0.18)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        kasa_base, kasa_tip,
        w_start=0.28, h_start=0.28,
        w_end=0.06, h_end=0.06,
        color=P["kasa_straw"],
        up=(0.0, 0.0, 1.0),
        outline=True,
        alpha=c.alpha,
    )
    mk.obox(c, kasa_tip, (-fx, -fy, 0.1), 0.028, 0.055, 0.055, P["kasa_rim"], up=(0.0, 0.0, 1.0), outline=False)


def draw_legs(c):
    """
    Pernas atléticas de peregrino em malha contínua 3D:
    - Calças largas azul-carvão (Hakama-shita) até o joelho.
    - Polainas de viagem brancas/creme (Kyahan) amarradas com fitas escuras nas canelas.
    - Sandálias de palha Waraji com tiras vermelhas tradicionais.
    """
    P = pal()
    trail, amp, freq = mk.motion(c, 0.035)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.75 * sign, trail, (c.px, c.py), amp=amp * 0.4, freq=freq)

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.25, sh[1] + o1[1] * 0.25, sh[2] + 0.15)
        cuff_pos = (sh[0] + o1[0] * 0.15, sh[1] + o1[1] * 0.15, sh[2] + 0.08)
        ankle = (foot[0] + o2[0] * 0.15, foot[1] + o2[1] * 0.15, foot[2] + 0.03)

        # Calça Hakama-shita azul-carvão até abaixo do joelho
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos],
            widths=[0.125, 0.118, 0.096],
            depth_thick=0.100,
            colors=[P["pants"], P["pants_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Polaina Kyahan branca/creme contínua da canela ao tornozelo
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[cuff_pos, ankle],
            widths=[0.088, 0.072],
            depth_thick=0.075,
            colors=[P["kyahan"], P["sash_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Tira escura de amarração da Kyahan
        mk.obox(c, cuff_pos, (c.fx, c.fy, 0.0), 0.082, 0.090, 0.018, P["kyahan_strap"], outline=False)

        # Sandália Waraji de palha com tira vermelha
        flen, fwidth = 0.13, 0.068
        mk.obox(c, (foot[0] + c.fx * 0.01, foot[1] + c.fy * 0.01, foot[2]), (c.fx, c.fy, 0.0), flen, fwidth, 0.032, P["waraji"])
        mk.obox(c, (foot[0] + c.fx * 0.02, foot[1] + c.fy * 0.02, foot[2] + 0.024), (c.fx, c.fy, 0.0), 0.038, 0.068, 0.014, P["waraji_strap"], outline=False)


def draw_obi(c):
    """Faixa Obi de cânhamo claro amarrada na cintura com nó robusto e abas."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    mk.cbox(c, bx, by, z, c.pelvis_w - 0.01, c.pelvis_w * 0.74, 0.072, P["sash"])
    # Nó frontal da faixa de cânhamo
    if mk.depth(c, fx, fy) > -0.1:
        mk.obox(c, (bx + fx * 0.092, by + fy * 0.092, z + 0.008), (0.0, 0.0, 1.0), 0.052, 0.048, 0.032, P["sash_dark"], up=(fx, fy, 0.0), outline=True)


def draw_torso(c):
    """
    Tronco de Daiki fiel ao conceito de corpo inteiro:
    - Túnica azul-ardósia cobrindo o lado direito, com o ombro e peitoral esquerdo musculoso expostos.
    - Gola diagonal de cânhamo cruzando o peito.
    - Grande colar de contas de oração Juzu (madeira de sândalo e contas douradas) no pescoço/peito.
    - Se de costas para a câmera, desenha o chapéu Kasa nas costas.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    front = 0.094
    d_torso = mk.depth(c, bx, by)

    # Se as costas estão voltadas para a câmera, desenha o Kasa por cima das costas do tronco
    if mk.depth(c, bx - fx * 0.12, by - fy * 0.12) >= d_torso:
        _render_back_kasa(c)

    if mk.depth(c, fx, fy) > -0.15:
        # 1. Peitoral e ombro esquerdo musculoso exposto (s = +1.0 corresponde ao lado esquerdo)
        chest_l = (bx + fx * (front - 0.008) + px * 0.055, by + fy * (front - 0.008) + py * 0.055, tz + 0.15)
        mk.obox(c, chest_l, (0.0, 0.0, 1.0), 0.13, 0.11, 0.045, P["skin"], up=(fx, fy, 0.0), outline=False)
        sh_bare = (bx + px * (c.sh_span * 0.85), by + py * (c.sh_span * 0.85), tz + 0.21)
        mk.obox(c, sh_bare, (px, py, 0.0), 0.065, 0.085, 0.055, P["skin"], up=(0.0, 0.0, 1.0), outline=False)

        # 2. Lapela diagonal da túnica azul-ardósia cruzando do ombro direito (s=-1) para a cintura esquerda (s=+1)
        lapel_mid = (bx + fx * front - px * 0.015, by + fy * front - py * 0.015, tz + 0.13)
        mk.obox(c, lapel_mid, (px * 0.48, py * 0.48, -0.88), 0.18, 0.042, 0.024, P["tunic_light"], up=(fx, fy, 0.0), outline=False)

        # 3. Grande Rosário Juzu 3D pendurado ao redor do pescoço e peito
        juzu_pts = [
            (bx + px * 0.065 + fx * 0.045, by + py * 0.065 + fy * 0.045, tz + 0.235),
            (bx + px * 0.045 + fx * (front + 0.008), by + py * 0.045 + fy * (front + 0.008), tz + 0.185),
            (bx + fx * (front + 0.012), by + fy * (front + 0.012), tz + 0.150),
            (bx - px * 0.045 + fx * (front + 0.008), by - py * 0.045 + fy * (front + 0.008), tz + 0.185),
            (bx - px * 0.065 + fx * 0.045, by - py * 0.065 + fy * 0.045, tz + 0.235),
        ]
        for idx, bpt in enumerate(juzu_pts):
            bcol = P["juzu_accent"] if idx == 2 else P["juzu_bead"]
            bsz = 0.032 if idx == 2 else 0.025
            mk.obox(c, bpt, (0.0, 0.0, 1.0), bsz, bsz, bsz, bcol, up=(fx, fy, 0.0), outline=True)


def draw_arm(c, shoulder, hand, side):
    """
    Braços assimétricos de Daiki (fiel ao retrato/conceito):
    - Braço esquerdo (side > 0): Ombro e bíceps musculoso nu (`sleeve_to=0.12`), com munhequeira branca `tekko` no antebraço.
    - Braço direito (side < 0): Manga de cânhamo azul-ardósia (`sleeve_to=0.58`) e munhequeira branca `tekko`.
    """
    P = pal()
    is_left = side > 0
    s_pt, e_pt = mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["skin"] if is_left else P["tunic"],
        sleeve_to=0.15 if is_left else 0.58,
        w=0.056,
        bend=0.028,
    )
    # Munhequeira branca (Tekko) no antebraço próximo ao pulso
    wrist_x = e_pt[0] * 0.35 + hand[0] * 0.65
    wrist_y = e_pt[1] * 0.35 + hand[1] * 0.65
    wrist_z = e_pt[2] * 0.35 + hand[2] * 0.65
    dx, dy, dz = hand[0] - e_pt[0], hand[1] - e_pt[1], hand[2] - e_pt[2]
    mk.obox(c, (wrist_x, wrist_y, wrist_z), (dx, dy, dz), 0.075, 0.052, 0.052, P["tekko"], outline=True)
    return s_pt, e_pt


def draw_head(c):
    """
    Cabeça de Daiki:
    - Cabelos negros presos em coque alto de guerreiro/peregrino (Chonmage/Motodori).
    - Faixa Hachimaki de palha trançada envolvendo a testa acima das sobrancelhas.
    - Feições marciais masculinas 3D low-poly via `draw_portrait_face_3d`.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # 1. Calota craniana de cabelos negros e coque superior
    cran_top = (bx - fx * 0.012, by - fy * 0.012, hz + 0.170)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, hz + 0.132), cran_top,
        w_start=hw * 0.98, h_start=hw * 0.98,
        w_end=hw * 0.68, h_end=hw * 0.68,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Coque alto (Chonmage) preso com cordão de palha
    bun_base = (bx - fx * 0.022, by - fy * 0.022, hz + 0.168)
    bun_tip = (bx + fx * 0.010, by + fy * 0.010, hz + 0.228)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        bun_base, bun_tip,
        w_start=0.058, h_start=0.062,
        w_end=0.042, h_end=0.046,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )
    mk.obox(c, bun_base, (0.0, 0.0, 1.0), 0.022, 0.052, 0.052, P["straw_band"], up=(fx, fy, 0.0), outline=False)

    # 2. Faixa Hachimaki de palha trançada na testa (z: hz + 0.112 -> hz + 0.140, acima das sobrancelhas)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, hz + 0.112), (bx, by, hz + 0.140),
        w_start=hw + 0.016, h_start=hw + 0.018,
        w_end=hw + 0.014, h_end=hw + 0.016,
        color=P["straw_band"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # 3. Rosto masculino marcial 3D
    if not getattr(c, "_face_drawn", False):
        draw_portrait_face_3d(c, char_type="daiki")
        c._face_drawn = True


def draw_front(c, hand_l, hand_r):
    """Renderiza o Bastão Bō à frente quando as mãos estão no plano frontal."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_bo_staff(c, hand_l, hand_r)


# ---------------------------------------------------------------------------------------------------------------------
# Renderização do Bastão Longo Bō (Roku-shaku Bō ~1.85m)
# ---------------------------------------------------------------------------------------------------------------------

def _render_bo_staff(c, hand_l, hand_r):
    """
    Renderiza o Bastão Bō de carvalho reforçado com ponteiras e anéis de ferro:
    - Comprimento longo (1.82m) conectando ambas as mãos.
    - Empunhadura central enfaixada em linho branco.
    - Ponteiras de ferro forjado com anéis dourados/aço nas duas extremidades.
    """
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    pose = c.extra_props.get("pose") if c.extra_props else None

    if pose == "bo_plant_stance":
        # Bastão cravado verticalmente no solo ao lado da mão direita
        rx, ry, rz = hand_r
        bot = (rx, ry, c.base_z)
        mk.obox(c, bot, (0.0, 0.0, 1.0), 1.82, 0.042, 0.042, P["bo_wood"], up=(fx, fy, 0.0), texture="wood")
        mk.obox(c, (rx, ry, c.base_z + 0.72), (0.0, 0.0, 1.0), 0.36, 0.045, 0.045, P["bo_grip"], up=(fx, fy, 0.0), outline=False)
        mk.obox(c, bot, (0.0, 0.0, 1.0), 0.16, 0.046, 0.046, P["bo_iron"], up=(fx, fy, 0.0))
        mk.obox(c, (rx, ry, c.base_z + 1.66), (0.0, 0.0, 1.0), 0.16, 0.046, 0.046, P["bo_iron"], up=(fx, fy, 0.0))
        mk.obox(c, (rx, ry, c.base_z + 1.64), (0.0, 0.0, 1.0), 0.03, 0.050, 0.050, P["bo_gold_ring"], up=(fx, fy, 0.0), outline=False)
        return

    if pose == "bo_twirl":
        # Giro acrobático do bastão Yamabushi entre golpes (reduz frequência de ataque)
        twirl_prog = c.extra_props.get("twirl_progress", 0.0) if c.extra_props else 0.0
        angle = twirl_prog * math.pi * 4.0  # 2 rotações de 360° no recovery
        rot_cos = math.cos(angle)
        rot_sin = math.sin(angle)

        dx = px * rot_cos + fx * rot_sin * 0.45
        dy = py * rot_cos + fy * rot_sin * 0.45
        dz = math.sin(angle * 2.0) * 0.35 + rot_sin * 0.75
        dlen = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dlen > 0.001:
            dx /= dlen; dy /= dlen; dz /= dlen
        else:
            dx, dy, dz = px, py, 0.0

        mid_x = (hand_l[0] + hand_r[0]) * 0.5 + fx * 0.08
        mid_y = (hand_l[1] + hand_r[1]) * 0.5 + fy * 0.08
        mid_z = (hand_l[2] + hand_r[2]) * 0.5

        staff_len = 1.82
        half_len = staff_len * 0.5
        tail_pos = (mid_x - dx * half_len, mid_y - dy * half_len, mid_z - dz * half_len)
        tip_cap = (mid_x + dx * (half_len - 0.18), mid_y + dy * (half_len - 0.18), mid_z + dz * (half_len - 0.18))
        grip_pos = (mid_x - dx * 0.22, mid_y - dy * 0.22, mid_z - dz * 0.22)

        mk.obox(c, tail_pos, (dx, dy, dz), staff_len, 0.040, 0.040, P["bo_wood"], texture="wood")
        mk.obox(c, grip_pos, (dx, dy, dz), 0.44, 0.044, 0.044, P["bo_grip"], outline=False)
        mk.obox(c, tail_pos, (dx, dy, dz), 0.18, 0.045, 0.045, P["bo_iron"])
        mk.obox(c, (tail_pos[0] + dx * 0.16, tail_pos[1] + dy * 0.16, tail_pos[2] + dz * 0.16), (dx, dy, dz), 0.03, 0.050, 0.050, P["bo_gold_ring"], outline=False)
        mk.obox(c, tip_cap, (dx, dy, dz), 0.18, 0.045, 0.045, P["bo_iron"])
        mk.obox(c, (tip_cap[0] - dx * 0.02, tip_cap[1] - dy * 0.02, tip_cap[2] - dz * 0.02), (dx, dy, dz), 0.03, 0.050, 0.050, P["bo_gold_ring"], outline=False)

        # Brilho de vento montanhês nas pontas giratórias
        tip_end1 = (mid_x + dx * half_len, mid_y + dy * half_len, mid_z + dz * half_len)
        tip_end2 = (mid_x - dx * half_len, mid_y - dy * half_len, mid_z - dz * half_len)
        mk.cbox(c, tip_end1[0], tip_end1[1], tip_end1[2], 0.10, 0.10, 0.10, P["wind_aura"], outline=False)
        mk.cbox(c, tip_end2[0], tip_end2[1], tip_end2[2], 0.10, 0.10, 0.10, P["wind_aura"], outline=False)
        return

    # Vetor direcional ligando a mão direita (traseira) à mão esquerda (dianteira)
    dx = hand_l[0] - hand_r[0]
    dy = hand_l[1] - hand_r[1]
    dz = hand_l[2] - hand_r[2]
    dlen = math.sqrt(dx * dx + dy * dy + dz * dz)
    if dlen < 0.05:
        dx, dy, dz = fx * 0.85, fy * 0.85, 0.35
        dlen = math.sqrt(dx * dx + dy * dy + dz * dz)
    dx /= dlen
    dy /= dlen
    dz /= dlen

    mid_x = (hand_l[0] + hand_r[0]) * 0.5
    mid_y = (hand_l[1] + hand_r[1]) * 0.5
    mid_z = (hand_l[2] + hand_r[2]) * 0.5

    staff_len = 1.82
    half_len = staff_len * 0.5
    tail_pos = (mid_x - dx * half_len, mid_y - dy * half_len, mid_z - dz * half_len)
    tip_cap = (mid_x + dx * (half_len - 0.18), mid_y + dy * (half_len - 0.18), mid_z + dz * (half_len - 0.18))
    grip_pos = (mid_x - dx * 0.22, mid_y - dy * 0.22, mid_z - dz * 0.22)

    # 1. Haste principal de carvalho
    mk.obox(c, tail_pos, (dx, dy, dz), staff_len, 0.040, 0.040, P["bo_wood"], texture="wood")

    # 2. Faixa central de aderência em pano branco
    mk.obox(c, grip_pos, (dx, dy, dz), 0.44, 0.044, 0.044, P["bo_grip"], outline=False)

    # 3. Ponteiras de ferro forjado e anéis nas duas extremidades
    mk.obox(c, tail_pos, (dx, dy, dz), 0.18, 0.045, 0.045, P["bo_iron"])
    mk.obox(c, (tail_pos[0] + dx * 0.16, tail_pos[1] + dy * 0.16, tail_pos[2] + dz * 0.16), (dx, dy, dz), 0.03, 0.050, 0.050, P["bo_gold_ring"], outline=False)

    mk.obox(c, tip_cap, (dx, dy, dz), 0.18, 0.045, 0.045, P["bo_iron"])
    mk.obox(c, (tip_cap[0] - dx * 0.02, tip_cap[1] - dy * 0.02, tip_cap[2] - dz * 0.02), (dx, dy, dz), 0.03, 0.050, 0.050, P["bo_gold_ring"], outline=False)

    # 4. Rastro de vento montanhês nos frames ativos de ataque
    if c.is_melee and c.atk_progress is not None and 0.25 <= c.atk_progress <= 0.72:
        tip_end = (mid_x + dx * half_len, mid_y + dy * half_len, mid_z + dz * half_len)
        mk.cbox(c, tip_end[0], tip_end[1], tip_end[2], 0.18, 0.18, 0.18, P["wind_aura"], outline=False)
        mk.cbox(c, tip_end[0], tip_end[1], tip_end[2], 0.10, 0.10, 0.10, P["wind_core"], outline=False)
