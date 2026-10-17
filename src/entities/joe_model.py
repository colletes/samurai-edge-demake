"""
Joe, o American Ninja & Operador Tático (6.5.5):
- Balaclava preta tática cobrindo cabeça, nuca e mandíbula com abertura para o olhar penetrante.
- Bandana tática na testa com emblema do sol vermelho e pontas de tecido esvoaçando atrás ao vento.
- Óculos de visão noturna (NVG) de lente dupla ciano/esmeralda articulados e erguidos sobre a testa.
- Colete tático plate-carrier coiote com carregadores de 30 tiros, rádio tático com antena, granada M67 e patch da bandeira.
- Farda militar camuflada verde-oliva com mangas arregaçadas, luvas táticas e cotoveleiras.
- Calças táticas contínuas sem quebras ou degraus exagerados nos joelhos, com joelheiras anatômicas e botas de combate.
- Mochila de assalto 3D e bainha de katana cruzando as costas em diagonal.
- Kunai tática na mão direita e Shuriken de combate na esquerda.
- Ordenação dinâmica por profundidade (Painter's Algorithm): costas e mochila ocluem braços e armas em 360°.
"""
import math

import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.mesh_primitives import draw_ribbon_mesh_3d, draw_tapered_frustum_3d

PALETTE = {
    "camo": (82, 90, 62), "camo_dark": (54, 60, 40), "camo_light": (110, 120, 84),
    "vest": (138, 120, 82), "vest_dark": (98, 84, 56), "vest_light": (168, 148, 104),
    "pouch": (112, 98, 66), "pouch_dark": (80, 68, 44),
    "balaclava": (26, 27, 31), "balaclava_light": (46, 48, 56), "balaclava_dark": (16, 17, 20),
    "hair": (26, 27, 31), "neck": (26, 27, 31),
    "skin": (228, 186, 150), "skin_shadow": (196, 152, 120),
    "headband": (226, 212, 172), "headband_dark": (168, 154, 118),
    "sun": (198, 38, 42), "sun_light": (235, 65, 70),
    "nvg": (34, 38, 42), "nvg_mount": (58, 62, 68), "lens": (64, 215, 195), "lens_glow": (160, 248, 238),
    "knee": (38, 42, 36), "knee_strap": (24, 26, 22),
    "boot": (48, 44, 36), "sole": (24, 22, 18), "glove": (28, 28, 30),
    "pack": (68, 76, 52), "pack_dark": (48, 54, 38), "strap": (38, 34, 26),
    "steel": (216, 226, 240), "steel_dark": (88, 92, 102),
    "wood": (96, 68, 42), "scabbard": (32, 32, 36),
    "radio": (32, 34, 36), "antenna": (22, 22, 24), "grenade": (58, 82, 48),
    "flag_blue": (32, 58, 138), "flag_red": (186, 32, 38), "flag_white": (235, 238, 242),
}

MATERIALS = {
    "camo": "canvas", "camo_dark": "canvas", "vest": "canvas", "vest_dark": "canvas",
    "pouch": "canvas", "pack": "canvas", "pack_dark": "canvas",
    "boot": "leather", "glove": "leather", "knee": "leather", "strap": "leather",
    "balaclava": "knit", "headband": "canvas", "steel": "steel", "steel_dark": "metal",
    "scabbard": "lacquer", "nvg": "metal"
}


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def attack_arms(c):
    """Estocada tática de kunai: a mão direita avança em linha reta com zanshin; esquerda em guarda."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    p = c.atk_progress if c.atk_progress is not None else 0.0
    t = _smooth((p - 0.2) / 0.45)
    back = 1.0 - _smooth(p / 0.2)
    reach = 0.04 + 0.42 * t - 0.12 * back
    right = (bx + fx * reach - px * 0.12, by + fy * reach - py * 0.12, tz + 0.11 + 0.08 * t)
    left = (bx + fx * (0.15 + 0.06 * t) + px * 0.11, by + fy * (0.15 + 0.06 * t) + py * 0.11, tz + 0.19)
    return left, right


def attack_arms_at(c, p):
    saved = c.atk_progress
    c.atk_progress = p
    try:
        return attack_arms(c)[1]
    finally:
        c.atk_progress = saved


def _hands(c):
    """Retorna a posição das mãos (esquerda, direita) calculadas com animação ou guarda padrão."""
    if c.is_melee and c.atk_progress is not None:
        return attack_arms(c)
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    sway = math.sin(c.walk_timer * (6.5 if c.is_moving else 2.2)) * (0.025 if c.is_moving else 0.012)
    # Guarda tática compacta de operações especiais
    left = (bx + fx * 0.14 + px * 0.12, by + fy * 0.14 + py * 0.12 + sway, tz + 0.16)
    right = (bx + fx * 0.18 - px * 0.11, by + fy * 0.18 - py * 0.11 - sway, tz + 0.14)
    return left, right


def _back_gear(c):
    """Mochila tática de assalto e bainha de katana em diagonal nas costas."""
    P = pal()
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    back_dist = 0.13

    # Mochila modular MOLLE
    pack_pos = (bx - fx * back_dist, by - fy * back_dist, tz + 0.06)
    mk.cbox(c, pack_pos[0], pack_pos[1], pack_pos[2], 0.18, 0.15, 0.22, P["pack"])
    # Bolso superior da mochila
    mk.cbox(c, pack_pos[0] - fx * 0.025, pack_pos[1] - fy * 0.025, pack_pos[2] + 0.04, 0.15, 0.12, 0.10, P["pack_dark"], outline=False)
    # Fitas de compressão horizontais
    for zoff in (-0.03, 0.05):
        mk.cbox(c, pack_pos[0] - fx * 0.028, pack_pos[1] - fy * 0.028, pack_pos[2] + zoff, 0.16, 0.13, 0.015, P["strap"], outline=False)

    # Katana tática compacta e justa nas costas (sem vazar para fora do ombro/braço)
    d = mk.norm((px * 0.18 - fx * 0.02, py * 0.18 - fy * 0.02, 0.94))
    origin = (bx - fx * (back_dist + 0.03) - px * 0.06, by - fy * (back_dist + 0.03) - py * 0.06, tz - 0.06)
    # Bainha (saya) preta laqueada
    mk.obox(c, origin, d, 0.40, 0.036, 0.036, P["scabbard"])
    # Empunhadura tática com cordão (tsuka) projetando sobre o ombro
    hilt_orig = mk.add(origin, d, 0.36)
    mk.obox(c, hilt_orig, d, 0.14, 0.038, 0.038, P["camo_dark"])
    # Tsuba discreta e pomo
    mk.obox(c, hilt_orig, d, 0.018, 0.056, 0.056, P["steel_dark"], outline=False)
    mk.obox(c, mk.add(hilt_orig, d, 0.13), d, 0.018, 0.040, 0.040, P["steel"], outline=False)


def _draw_nvg(c):
    """Óculos de visão noturna (NVG) com lente dupla ciano/esmeralda articulados para cima."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py

    # Suporte basculante de titânio (mount bracket)
    mount_pt = (bx + fx * 0.065, by + fy * 0.065, hz + 0.155)
    mk.cbox(c, mount_pt[0], mount_pt[1], mount_pt[2], 0.055, 0.055, 0.028, P["nvg_mount"], outline=False)

    # Tubos binoculares orientados para cima/frente a 45°
    nvg_dir = mk.norm((fx * 0.55, fy * 0.55, 0.85))
    tubes_base = mk.add(mount_pt, nvg_dir, 0.025)

    # Ponte de ligação entre os tubos
    mk.obox(c, tubes_base, (px, py, 0.0), 0.09, 0.025, 0.025, P["nvg"], outline=False)

    # Cilindros ópticos dos dois olhos
    for s in (-1.0, 1.0):
        t_pos = (tubes_base[0] + px * 0.036 * s, tubes_base[1] + py * 0.036 * s, tubes_base[2])
        # Corpo do tubo
        mk.obox(c, t_pos, nvg_dir, 0.075, 0.032, 0.032, P["nvg"])
        # Anel de ajuste de foco metálico
        mk.obox(c, mk.add(t_pos, nvg_dir, 0.045), nvg_dir, 0.014, 0.036, 0.036, P["steel_dark"], outline=False)
        # Lente frontal brilhante ciano/esmeralda
        lens_pt = mk.add(t_pos, nvg_dir, 0.070)
        mk.obox(c, lens_pt, nvg_dir, 0.012, 0.030, 0.030, P["lens"], outline=False)
        mk.obox(c, mk.add(lens_pt, nvg_dir, 0.004), nvg_dir, 0.006, 0.016, 0.016, P["lens_glow"], outline=False)


def _headband_tails(c):
    """Pontas de tecido da bandana que esvoaçam dinamicamente na nuca."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    knot_root = (bx - fx * 0.082, by - fy * 0.082, hz + 0.095)
    trail, amp, freq = mk.motion(c, 0.07)

    for k, s in enumerate((-1.0, 1.0)):
        offs = cloth.chain_offsets(3, c.walk_timer, 0.8 * k, trail, (px, py),
                                   amp=amp * 1.8, freq=freq * 1.2,
                                   wind=cloth.wind_at(knot_root[0], knot_root[1]), wind_gain=0.08)
        pts = [knot_root]
        for i, o in enumerate(offs):
            pt = (knot_root[0] - fx * 0.045 * (i + 1) + px * s * 0.028 * (i + 1) + o[0],
                  knot_root[1] - fy * 0.045 * (i + 1) + py * s * 0.028 * (i + 1) + o[1],
                  knot_root[2] - 0.035 * (i + 1) + o[2])
            pts.append(pt)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=pts,
            widths=[0.022, 0.018, 0.012, 0.007],
            depth_thick=0.010,
            colors=[P["headband"], P["headband_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(fx, fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )


def _draw_weapons(c, arm_l, arm_r):
    """Kunai tática na direita e shuriken na esquerda."""
    P = pal()
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)

    # 1. Kunai na mão direita (alinhada ao antebraço/ataque)
    d = mk.norm((c.fx * 0.95, c.fy * 0.95, 0.15 if c.is_melee else 0.40))
    # Empunhadura tática enrolada com anel pommel
    mk.obox(c, mk.add(hand_r, d, -0.09), d, 0.10, 0.030, 0.030, P["glove"])
    mk.obox(c, mk.add(hand_r, d, -0.11), d, 0.020, 0.042, 0.016, P["steel_dark"], outline=False)  # anel pommel
    # Lâmina triangular da kunai de aço fosco
    mk.obox(c, mk.add(hand_r, d, 0.02), d, 0.018, 0.052, 0.030, P["steel_dark"], outline=False)  # guarda
    mk.obox(c, mk.add(hand_r, d, 0.04), d, 0.130, 0.044, 0.014, P["steel"])
    mk.obox(c, mk.add(hand_r, d, 0.16), d, 0.060, 0.024, 0.012, P["steel"], outline=False)

    # 2. Shuriken de 4 pontas na mão esquerda
    for ang in (0.0, math.pi / 4):
        dir_s = (math.cos(ang) * c.fx + math.sin(ang) * c.px, math.cos(ang) * c.fy + math.sin(ang) * c.py, 0.0)
        mk.obox(c, (hand_l[0] - dir_s[0] * 0.06, hand_l[1] - dir_s[1] * 0.06, hand_l[2] - 0.01), dir_s, 0.12, 0.026, 0.012, P["steel_dark"], outline=False)
    mk.cbox(c, hand_l[0], hand_l[1], hand_l[2] - 0.010, 0.024, 0.024, 0.016, P["steel"], outline=False)

    # Rastro de ataque marcial durante golpe
    if c.is_melee and c.atk_progress is not None and c.atk_progress >= 0.35:
        for j in range(1, 4):
            ghost = attack_arms_at(c, c.atk_progress - 0.045 * j)
            g = (ghost[0], ghost[1], ghost[2] - 0.065)
            mk.band(c, (mk.add(g, d, 0.08), mk.add(g, d, 0.22), mk.add(hand_r, d, 0.22), mk.add(hand_r, d, 0.08)), (190, 220, 245, int(150 / j)))


def draw_behind(c):
    """Camada traseira: renderizada ANTES do tronco/pernas para elementos que ficam atrás."""
    d_torso = mk.depth(c, c.base_x, c.base_y)

    # 1. Mochila tática e katana se estiverem no lado de trás
    d_back = mk.depth(c, c.base_x - c.fx * 0.15, c.base_y - c.fy * 0.15)
    if d_back < d_torso:
        _back_gear(c)

    # 2. Cauda da bandana se estiver atrás
    d_knot = mk.depth(c, c.base_x - c.fx * 0.08, c.base_y - c.fy * 0.08)
    if d_knot < d_torso:
        _headband_tails(c)

    # 3. Braços e armas se as mãos estiverem atrás do tronco (costas voltadas para a câmera)
    hand_l, hand_r = _hands(c)
    d_gear = max(mk.depth(c, hand_l[0], hand_l[1]), mk.depth(c, hand_r[0], hand_r[1]))
    if d_gear < d_torso - 0.01:
        _draw_weapons(c, hand_l, hand_r)


def draw_legs(c):
    """Calças táticas contínuas sem degraus/prateleiras nos joelhos, com joelheiras anatômicas e botas."""
    P = pal()
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]

        # Perna contínua 3D: coxa, joelho e canela compartilham vértices
        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0], sh[1], sh[2] + 0.16)
        ankle = (ft[0], ft[1], ft[2] + 0.06)

        # Calça tática camuflada contínua
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, ankle],
            widths=[0.118, 0.104, 0.086],
            depth_thick=0.092,
            colors=[P["camo"], P["camo_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Joelheira tática anatômica curva (sem prateleira)
        mk.cbox(c, knee[0] + c.fx * 0.024, knee[1] + c.fy * 0.024, knee[2] - 0.015, 0.088, 0.088, 0.065, P["knee"], outline=True)
        # Rebites da joelheira
        mk.cbox(c, knee[0] + c.fx * 0.034, knee[1] + c.fy * 0.034, knee[2] - 0.015, 0.054, 0.054, 0.032, P["knee_strap"], outline=False)

        # Bota de combate com cano e solado de borracha
        mk.obox(c, (ft[0] - c.fx * 0.040, ft[1] - c.fy * 0.040, ft[2]), (c.fx, c.fy, 0.0), 0.145, 0.085, 0.026, P["sole"])
        mk.obox(c, (ft[0] - c.fx * 0.020, ft[1] - c.fy * 0.020, ft[2] + 0.024), (c.fx, c.fy, 0.0), 0.115, 0.075, 0.042, P["boot"])
        mk.cbox(c, ankle[0], ankle[1], ankle[2] + 0.010, 0.086, 0.086, 0.070, P["boot"], outline=True)


def draw_obi(c):
    """Cinto de nylon tático com fivela, coldre moldado na coxa direita e bolsa de primeiros socorros."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07

    # Cinto tático
    mk.cbox(c, bx, by, z, c.pelvis_w, c.pelvis_w * 0.78, 0.065, P["strap"])
    # Fivela metálica frontal com fecho rápido
    if mk.depth(c, fx, fy) > -0.05:
        mk.cbox(c, bx + fx * 0.098, by + fy * 0.098, z + 0.005, 0.046, 0.028, 0.045, P["steel_dark"], outline=False)

    # Coldre rígido de pistola na coxa direita
    hx, hy = bx + px * 0.155 - fx * 0.01, by + py * 0.155 - fy * 0.01
    mk.cbox(c, hx, hy, z - 0.11, 0.055, 0.065, 0.13, P["balaclava_dark"])
    mk.cbox(c, hx + fx * 0.01, hy + fy * 0.01, z - 0.09, 0.045, 0.055, 0.03, P["pouch"], outline=False)

    # Granada e bolsa utilitária no flanco esquerdo
    mk.cbox(c, bx - px * 0.135 + fx * 0.03, by - py * 0.135 + fy * 0.03, z - 0.01, 0.048, 0.048, 0.065, P["grenade"])


def draw_torso(c):
    """Colete plate-carrier coiote com 3 porta-carregadores, rádio tático com antena e patch da bandeira."""
    P = pal()
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    d_torso = mk.depth(c, bx, by)

    # Base da farda militar BDU verde-oliva
    mk.cbox(c, bx, by, tz + 0.02, 0.29, 0.22, 0.16, P["camo"])

    # Colete tático plate-carrier coiote
    mk.cbox(c, bx, by, tz + 0.07, 0.31, 0.24, 0.19, P["vest"])

    # Mochila e katana se estiverem no lado frontal/visível da câmera
    d_back = mk.depth(c, bx - fx * 0.15, by - fy * 0.15)
    if d_back >= d_torso:
        _back_gear(c)

    # Detalhes frontais táticos SÓ renderizam se a frente estiver voltada para a câmera
    if mk.depth(c, fx, fy) > -0.05:
        front = 0.135

        # Três bolsos frontais para carregadores de fuzil (MOLLE mag pouches)
        for side in (-0.082, 0.0, 0.082):
            mk.cbox(c, bx + fx * front + px * side, by + fy * front + py * side, tz + 0.025, 0.065, 0.042, 0.088, P["pouch"])
            # Topo do carregador com ranhuras pretas
            mk.cbox(c, bx + fx * front + px * side, by + fy * front + py * side, tz + 0.082, 0.052, 0.032, 0.025, P["balaclava"], outline=False)

        # Rádio tático no ombro esquerdo com antena
        rad_x = bx + fx * (front - 0.015) + px * 0.105
        rad_y = by + fy * (front - 0.015) + py * 0.105
        mk.cbox(c, rad_x, rad_y, tz + 0.175, 0.040, 0.035, 0.070, P["radio"])
        # Antena flexível saindo do rádio
        mk.limb(c, (rad_x, rad_y, tz + 0.210), (rad_x + fx * 0.01, rad_y + fy * 0.01, tz + 0.310), 0.010, P["antenna"], outline=False)

        # Granada de fragmentação M67 no peitoral direito
        mk.cbox(c, bx + fx * front - px * 0.095, by + fy * front - py * 0.095, tz + 0.165, 0.045, 0.042, 0.055, P["grenade"])

        # Patch da bandeira dos EUA no painel de velcro central do peito
        flag_x = bx + fx * (front + 0.005)
        flag_y = by + fy * (front + 0.005)
        # Fundo e listras vermelhas e brancas
        mk.cbox(c, flag_x, flag_y, tz + 0.185, 0.068, 0.012, 0.042, P["flag_red"], outline=False)
        mk.cbox(c, flag_x, flag_y, tz + 0.185, 0.068, 0.013, 0.020, P["flag_white"], outline=False)
        # Cantão azul no canto superior
        mk.cbox(c, flag_x - px * 0.018, flag_y - py * 0.018, tz + 0.195, 0.032, 0.014, 0.022, P["flag_blue"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço com manga militar BDU arregaçada, antebraço musculoso e luva tática."""
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], sleeve=P["camo"], sleeve_to=0.55, glove=P["glove"], w=0.066)


def draw_sleeves(c, arms):
    """Patch militar de ombro integrado na manga (sem cubos flutuando) e cotoveleiras táticas."""
    P = pal()
    for s, e, side in arms:
        # Cotoveleira tática curva
        mk.cbox(c, e[0], e[1], e[2] - 0.015, 0.068, 0.068, 0.048, P["knee"], outline=False)


def draw_head(c):
    """Balaclava tática 3D contínua, bandana com sol vermelho e óculos NVG articulados."""
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    d_torso = mk.depth(c, bx, by)

    # 1. Bandana tática na testa (4 facetas verticais abraçando o crânio, sem tampa horizontal superior)
    z_b0 = hz + 0.088
    z_b1 = hz + 0.116
    r0 = hw * 0.495 + 0.002
    r1 = hw * 0.475 + 0.002

    # Vértices da borda inferior e superior da bandana
    fl0 = (bx + fx * r0 - px * r0, by + fy * r0 - py * r0, z_b0)
    fr0 = (bx + fx * r0 + px * r0, by + fy * r0 + py * r0, z_b0)
    br0 = (bx - fx * r0 + px * r0, by - fy * r0 + py * r0, z_b0)
    bl0 = (bx - fx * r0 - px * r0, by - fy * r0 - py * r0, z_b0)

    fl1 = (bx + fx * r1 - px * r1, by + fy * r1 - py * r1, z_b1)
    fr1 = (bx + fx * r1 + px * r1, by + fy * r1 + py * r1, z_b1)
    br1 = (bx - fx * r1 + px * r1, by - fy * r1 + py * r1, z_b1)
    bl1 = (bx - fx * r1 - px * r1, by - fy * r1 - py * r1, z_b1)

    s_fl0 = c.camera.apply(fl0[0], fl0[1], fl0[2])
    s_fr0 = c.camera.apply(fr0[0], fr0[1], fr0[2])
    s_br0 = c.camera.apply(br0[0], br0[1], br0[2])
    s_bl0 = c.camera.apply(bl0[0], bl0[1], bl0[2])

    s_fl1 = c.camera.apply(fl1[0], fl1[1], fl1[2])
    s_fr1 = c.camera.apply(fr1[0], fr1[1], fr1[2])
    s_br1 = c.camera.apply(br1[0], br1[1], br1[2])
    s_bl1 = c.camera.apply(bl1[0], bl1[1], bl1[2])

    azimuth = getattr(c.camera, "azimuth", 0.0)
    fn_rx, fn_ry = mk.rotate_xy(fx, fy, azimuth)
    rn_rx, rn_ry = mk.rotate_xy(px, py, azimuth)

    band_faces = [
        # (visível, profundidade, polígono, cor, é_frente)
        ((fn_rx + fn_ry) > -0.05, (fn_rx + fn_ry) * r0, [s_fl0, s_fr0, s_fr1, s_fl1], P["headband"], True),
        ((rn_rx + rn_ry) > -0.05, (rn_rx + rn_ry) * r0, [s_fr0, s_br0, s_br1, s_fr1], P["headband_dark"], False),
        ((-fn_rx - fn_ry) > -0.05, (-fn_rx - fn_ry) * r0, [s_br0, s_bl0, s_bl1, s_br1], P["headband_dark"], False),
        ((-rn_rx - rn_ry) > -0.05, (-rn_rx - rn_ry) * r0, [s_bl0, s_fl0, s_fl1, s_bl1], P["headband_dark"], False),
    ]

    # Ordenar por profundidade e renderizar apenas faces voltadas para a câmera
    band_faces.sort(key=lambda item: item[1])
    for visible, depth_val, poly, col, is_front in band_faces:
        if not visible:
            continue
        pygame.draw.polygon(c.surface, col, poly)
        # Costura sutil nas bordas
        pygame.draw.line(c.surface, P["headband_dark"], poly[0], poly[1], 1)
        pygame.draw.line(c.surface, P["headband_dark"], poly[3], poly[2], 1)

        # Se for a face frontal, renderizar o Emblema do Sol Vermelho perfeitamente centrado na testa
        if is_front:
            sun_z = (z_b0 + z_b1) * 0.5
            r_sun = 0.012
            r_core = 0.006
            c_sun = (bx + fx * (r0 + 0.003), by + fy * (r0 + 0.003), sun_z)
            poly_sun = []
            poly_core = []
            for k in range(8):
                ang = k * math.pi / 4.0
                dx = px * math.cos(ang)
                dy = py * math.cos(ang)
                dz = math.sin(ang)
                ps = (c_sun[0] + dx * r_sun, c_sun[1] + dy * r_sun, c_sun[2] + dz * r_sun)
                poly_sun.append(c.camera.apply(ps[0], ps[1], ps[2]))
                pc = (c_sun[0] + dx * r_core, pc_y := (c_sun[1] + dy * r_core), ps[2])
                poly_core.append(c.camera.apply(pc[0], pc_y, c_sun[2] + dz * r_core))
            pygame.draw.polygon(c.surface, P["sun"], poly_sun)
            pygame.draw.polygon(c.surface, P["sun_light"], poly_core)

    # 2. Cauda da bandana se estiver voltada para a câmera
    d_knot = mk.depth(c, bx - fx * 0.08, by - fy * 0.08)
    if d_knot >= d_torso:
        _headband_tails(c)

    # 3. Óculos de visão noturna (NVG) articulados
    _draw_nvg(c)


def draw_front(c, arm_l, arm_r):
    """Camada frontal: armas desenham APENAS se as mãos estiverem na frente do tronco."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_l, hand_r = _hands(c)
    d_gear = max(mk.depth(c, hand_l[0], hand_l[1]), mk.depth(c, hand_r[0], hand_r[1]))
    if d_gear >= d_torso - 0.01:
        _draw_weapons(c, hand_l, hand_r)
