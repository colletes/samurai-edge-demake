"""
Aoi, a Caçadora Ainu de Hokkaido (Ciclo 5):
- Jovem caçadora Ainu de Ezo (Hokkaido), ágil e letal nas florestas boreais nevadas.
- Faixa tradicional Matanpushi azul-índigo na testa com bordados geométricos brancos (Moreu) e vermelhos.
- Longos cabelos negros lustrosos com mechas laterais (tsuya-kami) ordenadas dinamicamente em 3D e brincos de prata Ninkari.
- Casaco Attush azul-índigo profundo com padrões espirais brancos Ainu, gola e punhos espessos de pele de lobo branca/cinza.
- Faca ritual Makiri embainhada em osso/madeira entalhada na cintura e armadilha de urso de ferro presa ao quadril.
- Leggings de caça em malha contínua 3D conectadas sem degraus às botas de neve de couro e pele (Ker).
- Lança de Caça Ainu (Op / Makiri-Spear ~1.65m) com borla de pele branca, cordão carmesim e lâmina de aço polido.
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

SKIN = (246, 214, 192)
SKIN_SHADOW = (212, 172, 148)

PALETTE = {
    # Casaco Tradicional Ainu Attush & Bordados Moreu
    "attush": (28, 48, 86),
    "torso": (28, 48, 86),
    "attush_dark": (18, 32, 60),
    "attush_light": (46, 72, 122),
    "moreu_white": (240, 242, 248),
    "ainu_red": (198, 44, 48),
    "ainu_red_dark": (142, 28, 32),

    # Pelagem de Lobo/Urso do Norte
    "fur_white": (232, 235, 240),
    "fur_grey": (176, 182, 192),

    # Faixa Matanpushi, Cabelos e Joias Ninkari
    "matanpushi": (32, 54, 96),
    "hair": (22, 20, 28),
    "hair_dark": (12, 10, 16),
    "silver_ring": (215, 222, 235),

    # Cinturão, Faca Makiri e Armadilha de Urso
    "sash": (188, 40, 44),
    "belt": (188, 40, 44),
    "makiri_sheath": (148, 106, 68),
    "makiri_bone": (232, 224, 204),
    "trap_iron": (72, 78, 88),
    "trap_teeth": (195, 204, 216),

    # Pernas e Botas de Neve Ker
    "pants": (24, 38, 66),
    "pants_dark": (16, 26, 46),
    "boot_leather": (118, 78, 48),
    "boot_dark": (82, 52, 32),
    "boot_fur": (228, 230, 236),

    # Anatomia Feminina
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "neck": SKIN,
    "eye": (168, 102, 38),
    "brow": (28, 22, 26),
    "lip": (218, 104, 112),

    # Lança de Caça Op / Makiri-Spear
    "spear_shaft": (96, 60, 36),
    "spear_wrap": (198, 44, 48),
    "spear_blade": (205, 216, 230),
    "spear_edge": (245, 250, 255),
    "frost_aura": (165, 228, 255),
    "frost_core": (235, 250, 255),
}

MATERIALS = {
    "attush": "canvas",
    "attush_dark": "canvas",
    "fur_white": "velvet",
    "boot_leather": "leather",
    "spear_shaft": "wood",
    "spear_blade": "steel",
    "trap_iron": "metal",
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Animação da Lança Ainu (Op)
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Postura ágil de caçadora Ainu:
    - Mão direita segura a haste da lança Op pronta para o bote.
    - Mão esquerda à frente equilibrando a ponta da lança em diagonal.
    """
    breathe = math.sin(c.walk_timer * 2.6) * 0.010
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    pose = c.extra_props.get("pose") if c.extra_props else None

    if pose == "huntress_kneel":
        left = (bx + fx * 0.16 + px * 0.10, by + fy * 0.16 + py * 0.10, tz + 0.08)
        right = (bx + fx * 0.10 - px * 0.12, by + fy * 0.10 - py * 0.12, tz + 0.18)
        return left, right

    if pose == "ainu_prayer":
        # Saudação tradicional Ainu (Rimme / Inonno) com as palmas erguidas
        left = (bx + fx * 0.15 + px * 0.05, by + fy * 0.15 + py * 0.05, tz + 0.18)
        right = (bx + fx * 0.15 - px * 0.05, by + fy * 0.15 - py * 0.05, tz + 0.18)
        return left, right

    right = (
        bx - fx * 0.04 - px * 0.12,
        by - fy * 0.04 - py * 0.12,
        tz + 0.12,
    )
    left = (
        bx + fx * 0.16 + px * 0.09,
        by + fy * 0.16 + py * 0.09,
        tz + 0.14,
    )
    return left, right


def walk_arms(c):
    """Passada silenciosa na neve com a lança equilibrada."""
    sw = math.sin(c.walk_timer * 8.5) * 0.07
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    right = (
        bx - fx * (0.04 - sw * 0.04) - px * 0.12,
        by - fy * (0.04 - sw * 0.04) - py * 0.12,
        tz + 0.12 + abs(sw) * 0.015,
    )
    left = (
        bx + fx * (0.16 + sw * 0.05) + px * 0.09,
        by + fy * (0.16 + sw * 0.05) + py * 0.09,
        tz + 0.14 + abs(sw) * 0.015,
    )
    return left, right


def attack_arms(c):
    """
    Ataques de Aoi:
    - Plantar Armadilha (`state == 'PLANT_TRAP'` ou `is_trap=True`): mão esquerda lança/arma a armadilha no solo.
    - Estocada de Caça + Corte de Recuo: bote perfurante veloz seguido de puxada cortante.
    """
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    prog = c.atk_progress if c.atk_progress is not None else 0.0
    is_trap = (c.state == "PLANT_TRAP") or (c.extra_props.get("is_trap", False) if c.extra_props else False)

    if is_trap:
        left = (bx + fx * 0.22 + px * 0.08, by + fy * 0.22 + py * 0.08, tz + 0.02)
        right = (bx - fx * 0.06 - px * 0.14, by - fy * 0.06 - py * 0.14, tz + 0.16)
        return left, right

    if prog < 0.24:
        # Recuo rápido de bote
        t = prog / 0.24
        right = (bx - fx * (0.08 + t * 0.10) - px * 0.13, by - fy * (0.08 + t * 0.10) - py * 0.13, tz + 0.14)
        left = (bx + fx * (0.12 - t * 0.04) + px * 0.08, by + fy * (0.12 - t * 0.04) + py * 0.08, tz + 0.15)
    elif prog < 0.66:
        # Estocada perfurante profunda
        t = (prog - 0.24) / 0.42
        thrust = math.sin(t * math.pi)
        right = (bx + fx * (0.14 + thrust * 0.20) - px * 0.08, by + fy * (0.14 + thrust * 0.20) - py * 0.08, tz + 0.16)
        left = (bx + fx * (0.26 + thrust * 0.22) + px * 0.05, by + fy * (0.26 + thrust * 0.22) + py * 0.05, tz + 0.17)
    else:
        # Corte de recuo ágil
        t = (prog - 0.66) / 0.34
        right = (bx - fx * 0.04 - px * 0.12, by - fy * 0.04 - py * 0.12, tz + 0.12)
        left = (bx + fx * (0.22 - t * 0.06) + px * (0.12 - t * 0.03), by + fy * (0.22 - t * 0.06) + py * (0.12 - t * 0.03), tz + 0.14)

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
    1. Longos cabelos negros descendo pelas costas em fita contínua 3D.
    2. Aba traseira do casaco Attush com barra geométrica branca Ainu.
    3. Mechas laterais (tsuya-kami) do lado oposto à câmera (para que o crânio as oclua naturalmente).
    4. Lança de caça Op quando o personagem está de costas para a câmera.
    """
    P = pal()
    bx, by, tz, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.torso_z, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    d_torso = mk.depth(c, bx, by)

    # 1. Cabelos negros longos em cascata 3D pelas costas
    trail, amp, freq = mk.motion(c, 0.04)
    o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.65, trail, (-fx, -fy), amp=amp * 0.6, freq=freq)
    h0 = (bx - fx * 0.06, by - fy * 0.06, hz + 0.11)
    h1 = (bx - fx * 0.10 + o1[0], by - fy * 0.10 + o1[1], tz + 0.14 + o1[2])
    h2 = (bx - fx * 0.12 + o2[0], by - fy * 0.12 + o2[1], tz - 0.01 + o2[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[h0, h1, h2],
        widths=[0.115, 0.128, 0.122],
        depth_thick=0.032,
        colors=[P["hair"], P["hair_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # 2. Caimento traseiro do casaco Attush com bordado branco Moreu
    p0 = (bx - fx * 0.08, by - fy * 0.08, tz + 0.06)
    p1 = (bx - fx * 0.11 + o1[0] * 0.5, by - fy * 0.11 + o1[1] * 0.5, tz - 0.14 + o1[2] * 0.5)
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1],
        widths=[0.20, 0.23],
        depth_thick=0.028,
        colors=[P["attush"], P["attush_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # 3. Mecha lateral do lado distante da câmera (oculta pelo crânio)
    for s in (-1.0, 1.0):
        is_behind = mk.depth(c, px * s, py * s) < -0.01
        if is_behind:
            p_top = (bx + px * (hw * 0.48 * s) + fx * 0.010, by + py * (hw * 0.48 * s) + fy * 0.010, hz + 0.135)
            p_mid = (bx + px * (hw * 0.46 * s) + fx * 0.012, by + py * (hw * 0.46 * s) + fy * 0.012, hz + 0.082)
            p_bot = (bx + px * (hw * 0.44 * s) + fx * 0.014, by + py * (hw * 0.44 * s) + fy * 0.014, hz + 0.030)
            draw_ribbon_mesh_3d(
                c.surface, c.camera,
                spine_points=[p_top, p_mid, p_bot],
                widths=[0.022, 0.026, 0.022],
                depth_thick=0.010,
                colors=[P["hair"], P["hair_dark"]],
                side_vec=(px * s, py * s, 0.0),
                normal_vec=(fx, fy, 0.0),
                outline=False,
                alpha=c.alpha,
            )

    # 4. Ordenação da Lança Op se as mãos estiverem atrás do tronco
    hand_l, hand_r = _current_hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_hunting_spear(c, hand_l, hand_r)


def draw_legs(c):
    """
    Pernas femininas ágeis em malha contínua 3D:
    - Leggings de caça azul-índigo conectadas sem degraus até o cano da bota (`cuff_pos`).
    - Cano de pele branca de inverno e botas de couro de cervo (`Ker`) amarradas com cordões.
    """
    P = pal()
    trail, amp, freq = mk.motion(c, 0.03)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.7 * sign, trail, (c.px, c.py), amp=amp * 0.35, freq=freq)

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.2, sh[1] + o1[1] * 0.2, sh[2] + 0.14)
        cuff_pos = (sh[0] + o1[0] * 0.1, sh[1] + o1[1] * 0.1, sh[2] + 0.08)
        ankle = (foot[0] + o2[0] * 0.15, foot[1] + o2[1] * 0.15, foot[2] + 0.03)

        # Legging de caça azul-índigo contínua até a bota
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos],
            widths=[0.105, 0.095, 0.084],
            depth_thick=0.086,
            colors=[P["pants"], P["pants_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Debrum de pele branca no topo da bota Ker
        mk.obox(c, cuff_pos, (c.fx, c.fy, 0.0), 0.088, 0.092, 0.026, P["boot_fur"], outline=True)

        # Cano da bota de couro de cervo (Ker)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[cuff_pos, ankle],
            widths=[0.084, 0.072],
            depth_thick=0.076,
            colors=[P["boot_leather"], P["boot_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Pé da bota de neve
        flen, fwidth = 0.115, 0.064
        mk.obox(c, (foot[0] + c.fx * 0.01, foot[1] + c.fy * 0.01, foot[2]), (c.fx, c.fy, 0.0), flen, fwidth, 0.034, P["boot_leather"])


def draw_obi(c):
    """
    Cinturão tejido Ainu carmesim e branco com:
    - Faca ritual Makiri em bainha de osso/madeira entalhada no quadril esquerdo.
    - Armadilha de Urso de ferro dentada presa no quadril direito.
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    mk.cbox(c, bx, by, z, c.pelvis_w - 0.01, c.pelvis_w * 0.72, 0.068, P["sash"])
    # Padrão geométrico branco central no obi
    mk.obox(c, (bx + fx * 0.082, by + fy * 0.082, z + 0.012), (px, py, 0.0), 0.075, 0.014, 0.018, P["moreu_white"], outline=False)

    # Faca Makiri embainhada no quadril esquerdo (s = +1.0)
    mak_pos = (bx + px * 0.125 + fx * 0.02, by + py * 0.125 + fy * 0.02, z - 0.01)
    mk.obox(c, mak_pos, (fx * 0.85, fy * 0.85, -0.35), 0.22, 0.032, 0.036, P["makiri_sheath"], outline=True)
    mk.obox(c, mak_pos, (fx * 0.85, fy * 0.85, -0.35), 0.06, 0.035, 0.038, P["makiri_bone"], outline=False)

    # Armadilha de Urso de ferro pendurada no quadril direito (s = -1.0)
    trap_pos = (bx - px * 0.130 - fx * 0.01, by - py * 0.130 - fy * 0.01, z - 0.02)
    mk.obox(c, trap_pos, (0.0, 0.0, 1.0), 0.085, 0.085, 0.030, P["trap_iron"], up=(fx, fy, 0.0), outline=True)
    mk.obox(c, (trap_pos[0] - px * 0.012, trap_pos[1] - py * 0.012, trap_pos[2] + 0.015), (0.0, 0.0, 1.0), 0.055, 0.055, 0.018, P["trap_teeth"], up=(fx, fy, 0.0), outline=False)


def draw_torso(c):
    """
    Tronco de Aoi fiel ao conceito de corpo inteiro:
    - Casaco Attush azul-índigo com bordados geométricos brancos (Moreu) nas lapelas e barra.
    - Gola espessa de pele de lobo branca/cinza envolvendo os ombros e a nuca.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    front = 0.086

    # 1. Gola espessa de pele de lobo branca/cinza ao redor do colarinho e ombros
    for s in (-1.0, 1.0):
        fur_sh = (bx + px * 0.078 * s, by + py * 0.078 * s, tz + 0.225)
        mk.obox(c, fur_sh, (fx, fy, 0.0), 0.095, 0.075, 0.045, P["fur_white"], up=(0.0, 0.0, 1.0), outline=True)
    fur_back = (bx - fx * 0.055, by - fy * 0.055, tz + 0.232)
    mk.obox(c, fur_back, (px, py, 0.0), 0.16, 0.065, 0.042, P["fur_grey"], up=(0.0, 0.0, 1.0), outline=True)

    # 2. Bordados geométricos brancos Ainu (Moreu) e frisos vermelhos nas lapelas frontais
    if mk.depth(c, fx, fy) > -0.05:
        for s in (-1.0, 1.0):
            lapel_p = (bx + fx * front + px * 0.038 * s, by + fy * front + py * 0.038 * s, tz + 0.13)
            mk.obox(c, lapel_p, (0.0, 0.0, 1.0), 0.16, 0.026, 0.016, P["moreu_white"], up=(fx, fy, 0.0), outline=False)
            red_p = (bx + fx * (front + 0.003) + px * 0.052 * s, by + fy * (front + 0.003) + py * 0.052 * s, tz + 0.13)
            mk.obox(c, red_p, (0.0, 0.0, 1.0), 0.15, 0.012, 0.012, P["ainu_red"], up=(fx, fy, 0.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço ágil com manga azul-índigo Attush e punho de pele de lobo branca."""
    P = pal()
    s_pt, e_pt = mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["attush"],
        sleeve_to=0.68,
        w=0.046,
        bend=0.024,
    )
    # Punho de pele branca e bordado Moreu no antebraço
    cuff_x = e_pt[0] * 0.38 + hand[0] * 0.62
    cuff_y = e_pt[1] * 0.38 + hand[1] * 0.62
    cuff_z = e_pt[2] * 0.38 + hand[2] * 0.62
    dx, dy, dz = hand[0] - e_pt[0], hand[1] - e_pt[1], hand[2] - e_pt[2]
    mk.obox(c, (cuff_x, cuff_y, cuff_z), (dx, dy, dz), 0.055, 0.058, 0.058, P["fur_white"], outline=True)
    return s_pt, e_pt


def draw_head(c):
    """
    Cabeça de Aoi:
    1. Calota de cabelos negros lustrosos.
    2. Faixa tradicional Ainu Matanpushi azul-índigo na testa com bordado geométrico branco e vermelho.
    3. Brincos circulares de prata Ninkari sob as orelhas.
    4. Rosto anime feminino 3D com olhos âmbar luminosos, cílios alados e nariz delicado.
    5. Mechas laterais (tsuya-kami) voltadas para a câmera emoldurando as bochechas.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # 1. Topo do cabelo negro
    cran_top = (bx - fx * 0.010, by - fy * 0.010, hz + 0.172)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, hz + 0.136), cran_top,
        w_start=hw * 0.98, h_start=hw * 0.98,
        w_end=hw * 0.72, h_end=hw * 0.72,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # 2. Faixa Ainu Matanpushi na testa (z: hz + 0.114 -> hz + 0.144, acima das sobrancelhas)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, hz + 0.114), (bx, by, hz + 0.144),
        w_start=hw + 0.016, h_start=hw + 0.018,
        w_end=hw + 0.014, h_end=hw + 0.016,
        color=P["matanpushi"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )
    if mk.facing_camera(c):
        # Emblema geométrico branco Moreu e detalhe vermelho no centro da Matanpushi
        f_dist = hw * 0.50 + 0.012
        mk.obox(c, (bx + fx * f_dist, by + fy * f_dist, hz + 0.128), (px, py, 0.0), 0.068, 0.012, 0.016, P["moreu_white"], up=(0.0, 0.0, 1.0), outline=False)
        mk.obox(c, (bx + fx * (f_dist + 0.002), by + fy * (f_dist + 0.002), hz + 0.128), (0.0, 0.0, 1.0), 0.018, 0.018, 0.010, P["ainu_red"], up=(fx, fy, 0.0), outline=False)

    # 3. Brincos de prata Ninkari sob a orelha visível
    for s in (-1.0, 1.0):
        if mk.depth(c, px * s, py * s) >= -0.01:
            ear_pos = (bx + px * (hw * 0.48 * s) - fx * 0.008, by + py * (hw * 0.48 * s) - fy * 0.008, hz + 0.052)
            mk.obox(c, ear_pos, (0.0, 0.0, 1.0), 0.018, 0.018, 0.018, P["silver_ring"], outline=True)

    # 4. Rosto anime feminino 3D
    if not getattr(c, "_face_drawn", False):
        draw_portrait_face_3d(c, char_type="aoi")
        c._face_drawn = True

    # 5. Mechas laterais (tsuya-kami) no lado voltado para a câmera
    for s in (-1.0, 1.0):
        is_behind = mk.depth(c, px * s, py * s) < -0.02
        if not is_behind:
            p_top = (bx + px * (hw * 0.48 * s) + fx * 0.010, by + py * (hw * 0.48 * s) + fy * 0.010, hz + 0.135)
            p_mid = (bx + px * (hw * 0.46 * s) + fx * 0.014, by + py * (hw * 0.46 * s) + fy * 0.014, hz + 0.082)
            p_bot = (bx + px * (hw * 0.44 * s) + fx * 0.016, by + py * (hw * 0.44 * s) + fy * 0.016, hz + 0.028)
            draw_ribbon_mesh_3d(
                c.surface, c.camera,
                spine_points=[p_top, p_mid, p_bot],
                widths=[0.024, 0.028, 0.022],
                depth_thick=0.010,
                colors=[P["hair"], P["hair_dark"]],
                side_vec=(px * s, py * s, 0.0),
                normal_vec=(fx, fy, 0.0),
                outline=False,
                alpha=c.alpha,
            )


def draw_front(c, hand_l, hand_r):
    """Renderiza a Lança de Caça Ainu (Op) à frente quando no plano frontal."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_hunting_spear(c, hand_l, hand_r)


# ---------------------------------------------------------------------------------------------------------------------
# Renderização da Lança de Caça Ainu (Op / Makiri-Spear ~1.65m)
# ---------------------------------------------------------------------------------------------------------------------

def _render_hunting_spear(c, hand_l, hand_r):
    """
    Renderiza a Lança de Caça Ainu (Op):
    - Haste de madeira resistente (~1.32m) com amarrações vermelhas.
    - Borla volumosa de pele branca e cordão carmesim na junção da lâmina.
    - Lâmina larga de aço/osso polido (~0.36m) com fio reluzente.
    """
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # Direção da haste da mão direita (traseira) passando pela mão esquerda (dianteira)
    dx = hand_l[0] - hand_r[0]
    dy = hand_l[1] - hand_r[1]
    dz = hand_l[2] - hand_r[2]
    dlen = math.sqrt(dx * dx + dy * dy + dz * dz)
    if dlen < 0.05:
        dx, dy, dz = fx * 0.90, fy * 0.90, 0.20
        dlen = math.sqrt(dx * dx + dy * dy + dz * dz)
    dx /= dlen
    dy /= dlen
    dz /= dlen

    mid_x = (hand_l[0] + hand_r[0]) * 0.5
    mid_y = (hand_l[1] + hand_r[1]) * 0.5
    mid_z = (hand_l[2] + hand_r[2]) * 0.5

    shaft_len = 1.32
    tail_pos = (mid_x - dx * 0.58, mid_y - dy * 0.58, mid_z - dz * 0.58)
    collar_pos = (tail_pos[0] + dx * shaft_len, tail_pos[1] + dy * shaft_len, tail_pos[2] + dz * shaft_len)

    # 1. Haste de madeira
    mk.obox(c, tail_pos, (dx, dy, dz), shaft_len, 0.036, 0.036, P["spear_shaft"], texture="wood")

    # 2. Amarrações vermelhas e borla de pele de lobo na base da lâmina
    mk.obox(c, (collar_pos[0] - dx * 0.10, collar_pos[1] - dy * 0.10, collar_pos[2] - dz * 0.10), (dx, dy, dz), 0.10, 0.044, 0.044, P["spear_wrap"], outline=False)
    mk.obox(c, (collar_pos[0] - dx * 0.04, collar_pos[1] - dy * 0.04, collar_pos[2] - dz * 0.04), (dx, dy, dz), 0.065, 0.068, 0.068, P["fur_white"], outline=True)

    # 3. Lâmina de lança Op em aço/osso polido
    mk.obox(c, collar_pos, (dx, dy, dz), 0.36, 0.052, 0.022, P["spear_blade"], outline=True)
    mk.obox(c, (collar_pos[0] + dx * 0.04, collar_pos[1] + dy * 0.04, collar_pos[2] + dz * 0.04), (dx, dy, dz), 0.32, 0.026, 0.012, P["spear_edge"], outline=False)

    # 4. Brilho glacial do norte nos ataques ativos
    if c.is_melee and c.atk_progress is not None and 0.24 <= c.atk_progress <= 0.68:
        tip_pt = (collar_pos[0] + dx * 0.32, collar_pos[1] + dy * 0.32, collar_pos[2] + dz * 0.32)
        mk.cbox(c, tip_pt[0], tip_pt[1], tip_pt[2], 0.16, 0.16, 0.16, P["frost_aura"], outline=False)
        mk.cbox(c, tip_pt[0], tip_pt[1], tip_pt[2], 0.09, 0.09, 0.09, P["frost_core"], outline=False)
