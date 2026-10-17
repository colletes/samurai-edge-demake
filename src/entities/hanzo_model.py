"""
Hanzo, o mestre shinobi de Iga (Yellow Shinobi):
- Capuz shinobi dourado com máscara preta e abertura para olhos marciais ambarinos penetrantes.
- Rosto esculpido 3D com mandíbula/gola de tecido preto contínuo sem vazamento de cor de pele.
- Túnica shozoku amarela com lapelas pretas cruzadas e filamentos dourados no peito.
- Ombreira de aço escuro no ombro esquerdo com rebordo polido e rebite dourado.
- Calças shinobi amarelas contínuas afunilando em botas tabi pretas com amarrações, sem degraus nos joelhos.
- Katana shinobi (Ninja-to) nas costas em diagonal, ordenada por profundidade 3D (Painter's Algorithm).
- Par de kunais de aço afiado empunhados nas mãos com empunhadura preta e anel pommel.
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
    "torso": (224, 172, 36),
    "torso_dark": (168, 122, 20),
    "pants": (206, 154, 28),
    "pants_dark": (155, 112, 18),
    "mask": (28, 24, 30),
    "mask_dark": (18, 15, 20),
    "neck": (28, 24, 30),
    "hair": (224, 172, 36),
    "hair_dark": (168, 122, 20),
    "skin": (226, 190, 156),
    "skin_shadow": (175, 138, 110),
    "gold": (244, 204, 84),
    "gold_trim": (218, 175, 62),
    "belt": (28, 24, 30),
    "steel": (195, 200, 212),
    "steel_dark": (78, 80, 92),
    "steel_light": (230, 235, 245),
    "boot": (30, 26, 32),
    "sole": (20, 18, 22),
    "wrap": (28, 24, 30),
    "ito": (30, 26, 28),
    "aura": (255, 214, 70),
    "aura_core": (255, 244, 190),
}

MATERIALS = {
    "torso": "knit", "pants": "knit", "torso_dark": "knit", "pants_dark": "knit",
    "mask": "leather", "boot": "leather", "belt": "leather", "wrap": "canvas",
    "steel": "steel", "steel_dark": "metal", "steel_light": "metal",
    "gold": "gold", "gold_trim": "gold"
}


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


# ---------------------------------------------------------------------------------------------------------------------
# Cinemática dos Braços e Kunais
# ---------------------------------------------------------------------------------------------------------------------

def _hands(c, p):
    """(esquerda, direita) do golpe de kunais: antecipação recolhida, estocada da direita e corte cruzado da esquerda."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    r = _smooth((p - 0.2) / 0.4)
    reach_r = 0.08 + 0.36 * r
    right = (bx + fx * reach_r - px * 0.10, by + fy * reach_r - py * 0.10, tz + 0.14 + 0.02 * r)
    s = _smooth((p - 0.35) / 0.4)
    lat = 0.18 - 0.30 * s
    reach_l = 0.0 + 0.30 * s
    left = (bx + fx * reach_l + px * lat, by + fy * reach_l + py * lat, tz + 0.12 - 0.02 * s)
    return left, right


def attack_arms(c):
    return _hands(c, c.atk_progress)


def idle_arms(c):
    tz = c.torso_z + math.sin(c.walk_timer * 2.8) * 0.012
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    right = (bx + fx * 0.14 - px * 0.10, by + fy * 0.14 - py * 0.10, tz + 0.12)
    left = (bx + fx * 0.08 + px * 0.12, by + fy * 0.08 + py * 0.12, tz + 0.08)
    return left, right


def _current_hands(c):
    if c.is_melee and c.atk_progress is not None:
        return attack_arms(c)
    if c.is_moving and hasattr(c, "walk_timer"):
        tz = c.torso_z
        bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
        sw = math.sin(c.walk_timer * 8.0) * 0.04
        right = (bx + fx * 0.10 - px * 0.12 + fx * sw, by + fy * 0.10 - py * 0.12 + fy * sw, tz + 0.10)
        left = (bx + fx * 0.06 + px * 0.12 - fx * sw, by + fy * 0.06 + py * 0.12 - fy * sw, tz + 0.08)
        return left, right
    return idle_arms(c)


def _kunai_dirs(c):
    return (mk.norm((c.fx * 0.9, c.fy * 0.9, -0.1)), mk.norm((c.fx * 0.5 + c.px * 0.3, c.fy * 0.5 + c.py * 0.3, -0.2)))


def _kunai(c, hand, d):
    """Kunai tática de aço afiado com anel pommel e habaki dourado."""
    P = pal()
    tip = mk.add(hand, d, 0.04)
    # Empunhadura com ito preto
    mk.obox(c, mk.add(hand, d, -0.10), d, 0.10, 0.034, 0.034, P["ito"])
    # Anel pommel
    mk.obox(c, mk.add(hand, d, -0.125), d, 0.025, 0.055, 0.014, P["steel_dark"], outline=False)
    # Habaki / colar dourado
    mk.obox(c, mk.add(tip, d, -0.005), d, 0.018, 0.062, 0.036, P["gold"], outline=False)
    # Lâmina triangular de dois gumes
    mk.obox(c, tip, d, 0.12, 0.048, 0.016, P["steel"])
    mk.obox(c, mk.add(tip, d, 0.12), d, 0.08, 0.024, 0.014, P["steel"])
    return mk.add(tip, d, 0.20)


def _render_kunais_and_hands(c, arm_l, arm_r):
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    dr, dl = _kunai_dirs(c)
    if c.is_melee:
        dr = mk.norm((c.fx * 0.95, c.fy * 0.95, 0.0))
        dl = mk.norm((c.fx * 0.4 - c.px * 0.55, c.fy * 0.4 - c.py * 0.55, -0.05))
    if c.is_moving and not c.is_melee:
        dr = mk.norm((c.fx * 0.3, c.fy * 0.3, -0.8))
        dl = mk.norm((c.fx * 0.3, c.fy * 0.3, -0.8))

    if (c.extra_props or {}).get("has_kunai", True):
        _kunai(c, hand_r, dr)
    _kunai(c, hand_l, dl)

    if c.is_melee and c.atk_progress >= 0.30:
        _trail(c, c.atk_progress)


def _trail(c, p):
    P = pal()
    ghosts = []
    for j in range(5):
        pj = p - 0.06 * j
        if pj < 0.25:
            break
        left, right = _hands(c, pj)
        h = (right[0], right[1], right[2] - 0.065)
        d = mk.norm((c.fx * 0.95, c.fy * 0.95, 0.0))
        h2 = (left[0], left[1], left[2] - 0.065)
        d2 = mk.norm((c.fx * 0.4 - c.px * 0.55, c.fy * 0.4 - c.py * 0.55, -0.05))
        ghosts.append((mk.add(h, d, 0.12), mk.add(h, d, 0.24), mk.add(h2, d2, 0.12), mk.add(h2, d2, 0.24)))
    for j in range(len(ghosts) - 1):
        fade = 1.0 - j / 5.0
        for a0, a1, b0, b1 in ((ghosts[j][0], ghosts[j][1], ghosts[j + 1][0], ghosts[j + 1][1]),
                               (ghosts[j][2], ghosts[j][3], ghosts[j + 1][2], ghosts[j + 1][3])):
            mk.band(c, (a0, a1, b1, b0), P["aura"] + (int(215 * fade),))
            mk.band(c, (mk.lerp(a0, a1, 0.5), a1, b1, mk.lerp(b0, b1, 0.5)), P["aura_core"] + (int(245 * fade),))


# ---------------------------------------------------------------------------------------------------------------------
# Katana Dorsal (Ninja-to)
# ---------------------------------------------------------------------------------------------------------------------

def _back_sword_origin(c):
    return (c.base_x - c.fx * 0.12 + c.px * 0.07, c.base_y - c.fy * 0.12 + c.py * 0.07, c.torso_z + 0.02)


def _draw_back_sword(c):
    """Espada ninja curta (ninja-to) embainhada na diagonal rente às costas."""
    P = pal()
    origin = _back_sword_origin(c)
    d = mk.norm((-c.px * 0.45 - c.fx * 0.10, -c.py * 0.45 - c.fy * 0.10, 0.88))

    # Bainha de laca preta fosca
    mk.obox(c, origin, d, 0.46, 0.040, 0.040, P["mask"])
    # Colarinho koiguchi dourado
    mk.obox(c, origin, d, 0.025, 0.048, 0.048, P["gold"], outline=False)

    # Empunhadura com ito preto e tsuba quadrada shinobi
    top = mk.add(origin, d, 0.46)
    mk.obox(c, top, d, 0.13, 0.036, 0.036, P["ito"])
    mk.obox(c, mk.add(top, d, -0.005), d, 0.012, 0.072, 0.072, P["gold"], outline=True)


# ---------------------------------------------------------------------------------------------------------------------
# Ganchos de Renderização (Painter's Algorithm)
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Katana dorsal (se estiver do lado oposto à câmera).
    - Cauda esvoaçante do capuz shinobi (se estiver atrás da cabeça).
    - Braços e kunais (se as mãos estiverem atrás do tronco ao encarar de costas).
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)

    # Katana nas costas
    mid_sword = mk.add(_back_sword_origin(c), (-c.px * 0.15, -c.py * 0.15, 0.20))
    if mk.depth(c, mid_sword[0], mid_sword[1]) < d_torso:
        _draw_back_sword(c)

    # Cauda do capuz
    d_cowl = mk.depth(c, c.base_x - c.fx * 0.08, c.base_y - c.fy * 0.08)
    if d_cowl < d_torso:
        _draw_hood_tail(c)

    # Mãos e kunais
    hand_l, hand_r = _current_hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_kunais_and_hands(c, hand_l, hand_r)


def draw_legs(c):
    """Calças shinobi amarelas contínuas com caneleiras/amarrações pretas e botas tabi."""
    P = pal()
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0], sh[1], sh[2] + 0.15)
        ankle = (ft[0], ft[1], ft[2] + 0.05)

        # Calça shinobi contínua 3D (elimina prateleiras e caixas nos joelhos)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, ankle],
            widths=[0.115, 0.100, 0.080],
            depth_thick=0.085,
            colors=[P["pants"], P["pants_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Caneleira/faixa preta protetora na canela
        sh_top = (sh[0], sh[1], sh[2] + 0.11)
        sh_bot = (ft[0], ft[1], ft[2] + 0.04)
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            sh_top, sh_bot,
            w_start=0.090, h_start=0.090,
            w_end=0.076, h_end=0.076,
            color=P["mask"],
            up=(c.fx, c.fy, 0.0),
            outline=False,
            alpha=c.alpha,
            cap_end=False,
        )

        # Bota tabi de shinobi com solado flexível
        mk.obox(c, (ft[0] - c.fx * 0.045, ft[1] - c.fy * 0.045, ft[2]), (c.fx, c.fy, 0.0), 0.14, 0.075, 0.026, P["sole"])
        mk.obox(c, (ft[0] - c.fx * 0.020, ft[1] - c.fy * 0.020, ft[2] + 0.022), (c.fx, c.fy, 0.0), 0.105, 0.065, 0.038, P["boot"])


def draw_obi(c):
    """Cinto preto com bordado dourado e nó lateral com pontas que balançam."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    # Faixa base do cinto na cintura
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.008, c.pelvis_w * 0.74, 0.085, P["belt"])
    mk.cbox(c, bx, by, z + 0.078, c.pelvis_w - 0.008, c.pelvis_w * 0.74, 0.012, P["gold"], outline=False)

    # Nó frontal e pontas penduradas (se voltado para a câmera)
    kx, ky = bx + fx * 0.095 + px * 0.04, by + fy * 0.095 + py * 0.04
    d_torso = mk.depth(c, bx, by)
    if mk.depth(c, kx, ky) >= d_torso - 0.04:
        mk.cbox(c, kx, ky, z + 0.010, 0.065, 0.045, 0.060, P["belt"])
        trail, amp, freq = mk.motion(c, 0.05)
        for k, s in enumerate((-1.0, 1.0)):
            offs = cloth.chain_offsets(3, c.walk_timer, 0.8 * k, trail, (px, py), amp=amp * 1.3, freq=freq, wind=cloth.wind_at(kx, ky))
            for i, o in enumerate(offs):
                mk.cbox(c, kx + px * 0.020 * s + o[0], ky + o[1], z - 0.055 * (i + 1) + o[2], 0.030, 0.022, 0.060, P["belt"], outline=False)


def draw_torso(c):
    """
    Tronco de Hanzo:
    - Túnica shozoku amarelo-ouro com lapelas pretas cruzadas e bordado dourado em V.
    - Peito com transpasse sem cubos flutuantes.
    """
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.115

    # Lapelas pretas cruzadas com filete dourado
    if mk.depth(c, fx, fy) > -0.05:
        apex = (bx + fx * front - px * 0.015, by + fy * front - py * 0.015, tz + 0.06)
        for s in (-1.0, 1.0):
            top = (bx + fx * (front - 0.003) + px * 0.070 * s, by + fy * (front - 0.003) + py * 0.070 * s, tz + 0.260)
            # Lapela preta
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                top, apex,
                w_start=0.030, h_start=0.015,
                w_end=0.022, h_end=0.010,
                color=P["mask"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )
            # Filete dourado de bordado
            top_g = (top[0] - px * 0.008 * s, top[1] - py * 0.008 * s, top[2] - 0.005)
            apex_g = (apex[0] - px * 0.006 * s, apex[1] - py * 0.006 * s, apex[2] + 0.008)
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                top_g, apex_g,
                w_start=0.010, h_start=0.012,
                w_end=0.008, h_end=0.008,
                color=P["gold"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )

        # Gola alta interior preta cobrindo o peito sob o decote
        mk.obox(c, (bx + fx * (front - 0.005), by + fy * (front - 0.005), tz + 0.16),
                (0.0, 0.0, 1.0), 0.080, 0.045, 0.015, P["mask"], up=(fx, fy, 0.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço ágil com manga amarela no bíceps e braçadeira/luva preta no antebraço."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.20)
    h = (hand[0], hand[1], hand[2] - 0.065)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.030), (0.0, 0.0, -0.030))

    # Manga amarela no bíceps
    mk.limb(c, s, e, 0.060, P["torso"], w_end=0.054)
    # Braçadeira preta no antebraço
    mk.limb(c, e, h, 0.054, P["mask"], w_end=0.046)
    # Rebite metálico na braçadeira
    wrist_mid = mk.lerp(e, h, 0.5)
    mk.obox(c, (wrist_mid[0] + c.px * side * 0.025, wrist_mid[1] + c.py * side * 0.025, wrist_mid[2]),
            (c.px * side, c.py * side, 0.0), 0.012, 0.020, 0.020, P["steel_dark"], outline=False)
    # Luva preta
    mk.cbox(c, h[0], h[1], h[2] - 0.025, 0.050, 0.050, 0.050, P["mask"])
    return s, e


def draw_sleeves(c, arms):
    """Ombreira articulada de aço escuro com rebordo de aço brilhante no ombro esquerdo."""
    P = pal()
    for s, e, side in arms:
        # Ombreira no ombro esquerdo (side > 0)
        if side > 0:
            z = s[2] + 0.015
            ox = s[0] + c.px * 0.018
            oy = s[1] + c.py * 0.018
            sh_dir = mk.norm((c.px * 0.40, c.py * 0.40, -0.90))

            # Placa de aço escuro superior curvada
            mk.obox(c, (ox - c.fx * 0.010, oy - c.fy * 0.010, z - 0.015), sh_dir,
                    0.090, 0.085, 0.038, P["steel_dark"], up=(c.fx, c.fy, 0.0), texture="metal")
            # Rebordo chanfrado de aço brilhante
            mk.obox(c, (ox - c.fx * 0.008, oy - c.fy * 0.008, z - 0.010), sh_dir,
                    0.080, 0.088, 0.014, P["steel_light"], up=(c.fx, c.fy, 0.0), outline=False)
            # Rebite dourado central
            mk.cbox(c, ox + c.fx * 0.020, oy + c.fy * 0.020, z - 0.005, 0.018, 0.018, 0.018, P["gold"], outline=False)


def _draw_hood_tail(c):
    """Cauda do capuz shinobi esvoaçando para trás com o vento."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.08)
    root = (bx - fx * 0.075, by - fy * 0.075, hz + 0.07)
    offs = cloth.chain_offsets(3, c.walk_timer, 0.7, trail, (px, py), amp=amp * 1.5, freq=freq, wind=cloth.wind_at(root[0], root[1]), wind_gain=0.06)

    last_pt = root
    for i, o in enumerate(offs):
        cur_pt = (root[0] - fx * 0.040 * (i + 1) + o[0],
                  root[1] - fy * 0.040 * (i + 1) + o[1],
                  root[2] - 0.055 * (i + 1) + o[2])
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            last_pt, cur_pt,
            w_start=max(0.020, 0.048 - 0.010 * i), h_start=max(0.015, 0.036 - 0.008 * i),
            w_end=max(0.014, 0.038 - 0.010 * i), h_end=max(0.010, 0.028 - 0.008 * i),
            color=P["torso"],
            up=(0.0, 0.0, 1.0),
            outline=(i == 0),
            alpha=c.alpha,
        )
        last_pt = cur_pt


def draw_head(c):
    """
    Cabeça de Hanzo:
    - Crânio com balaclava e queixo pretos esculpidos em draw_sculpted_head_3d.
    - Olhos marciais ambarinos penetrantes focados na fenda da máscara via draw_portrait_face_3d.
    - Capuz shinobi amarelo-ouro cobrindo a coroa e nuca sem caixas abertas ou artefatos de chaminé.
    - Cauda do capuz esvoaçante atrás da cabeça.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    d_torso = mk.depth(c, bx, by)

    # 1. Borda frontal do capuz sobre a testa (emoldura a abertura dos olhos)
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.004
        mk.obox(c, (bx + fx * front_d, by + fy * front_d, hz + 0.096),
                (0.0, 0.0, 1.0), 0.018, hw * 0.88, 0.010, P["torso_dark"], up=(fx, fy, 0.0), outline=False)
        # Têmporas da máscara preta integrando mandíbula e capuz
        for s in (-1.0, 1.0):
            mk.obox(c, (bx + px * (hw * 0.42 * s) + fx * (front_d * 0.7), by + py * (hw * 0.42 * s) + fy * (front_d * 0.7), hz + 0.045),
                    (0.0, 0.0, 1.0), 0.060, 0.016, 0.016, P["mask"], up=(fx, fy, 0.0), outline=False)

    # 2. Cauda do capuz (se voltada para a câmera)
    d_cowl = mk.depth(c, bx - fx * 0.08, by - fy * 0.08)
    if d_cowl >= d_torso:
        _draw_hood_tail(c)


def draw_front(c, arm_l, arm_r):
    """
    Camada frontal (Painter's Algorithm):
    - Katana dorsal (se estiver do lado voltado para a câmera).
    - Kunais e manoplas são renderizadas aqui APENAS se as mãos estiverem à frente do tronco.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)

    mid_sword = mk.add(_back_sword_origin(c), (-c.px * 0.15, -c.py * 0.15, 0.20))
    if mk.depth(c, mid_sword[0], mid_sword[1]) >= d_torso:
        _draw_back_sword(c)

    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)

    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_kunais_and_hands(c, hand_l, hand_r)
