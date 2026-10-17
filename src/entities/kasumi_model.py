"""
Kasumi, a kunoichi da Névoa (6.5.5):
- Cabelo prateado com coque alto, laço e mechas laterais (tsuya-kami) dinamicamente ordenadas por profundidade 3D.
- Rosto esculpido em 3D Tekken 2/3 com olhos azul-aço luminosos, delineador alado e nariz delicado via draw_portrait_face_3d.
- Cachecol cinza-névoa com gola volumosa e ponta longa esvoaçante com física de tecido 3D.
- Colete-espartilho de couro preto com fivelas prateadas sobre traje justo cromado.
- Pernas contínuas em leggings cromadas sem degraus/prateleiras nos joelhos, com joelheiras de placa e coldre de couro.
- Ombreiras cromadas articuladas e braçadeiras polidas com luvas ninja pretas.
- Adaga shinobi na mão direita com corte prateado translúcido e ordenação dinâmica por profundidade (Painter's Algorithm).
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.mesh_primitives import draw_ribbon_mesh_3d, draw_tapered_frustum_3d

PALETTE = {
    # Traje e Couro
    "torso": (32, 36, 44),
    "torso_dark": (20, 22, 28),
    "torso_light": (48, 54, 66),
    "belt": (40, 36, 32),
    "leather": (48, 40, 36),
    "buckle": (220, 226, 236),
    "bomb": (34, 34, 40),
    "fuse": (255, 145, 55),

    # Traje Cromado e Armadura
    "chrome": (196, 204, 218),
    "chrome_dark": (124, 132, 146),
    "chrome_light": (244, 248, 254),
    "black": (26, 28, 34),
    "glove": (26, 28, 32),
    "boot": (30, 32, 38),
    "sole": (18, 18, 22),

    # Cabelo Prateado e Adornos
    "hair": (218, 224, 236),
    "hair_light": (246, 250, 255),
    "hair_dark": (160, 168, 184),
    "tie": (32, 34, 40),

    # Cachecol Shinobi
    "scarf": (148, 154, 166),
    "neck": (148, 154, 166),
    "scarf_dark": (105, 110, 120),
    "scarf_light": (190, 196, 208),

    # Anatomia e Rosto
    "skin": (245, 220, 204),
    "skin_shadow": (214, 185, 168),
    "eye": (86, 152, 178),
    "brow": (88, 94, 108),
    "lip": (205, 115, 125),

    # Arma
    "blade": (226, 234, 246),
    "edge": (255, 255, 255),
    "steel_dark": (72, 76, 88),
}

MATERIALS = {
    "pants": "latex", "chrome": "chrome", "chrome_dark": "metal", "chrome_light": "chrome",
    "torso": "leather", "torso_dark": "leather", "black": "leather", "leather": "leather",
    "belt": "leather", "scarf": "canvas", "scarf_dark": "canvas", "bomb": "lacquer",
    "buckle": "chrome", "blade": "steel", "edge": "steel"
}


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def _hands(c):
    """Retorna posição das mãos (esquerda, direita) com guarda ágil ou animação de golpe."""
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    if c.is_melee and c.atk_progress is not None:
        p = c.atk_progress
        if p < 0.35:
            # Antecipação recuada com adaga armada
            w = _smooth(p / 0.35)
            right = (bx - fx * 0.08 + px * 0.12, by - fy * 0.08 + py * 0.12, tz + 0.18 + 0.10 * w)
            left = (bx + fx * 0.14 - px * 0.12, by + fy * 0.14 - py * 0.12, tz + 0.12)
        elif p < 0.75:
            # Estocada/corte fulgurante à frente
            t = (p - 0.35) / 0.40
            reach = 0.08 + 0.38 * math.sin(math.pi * t)
            right = (bx + fx * reach + px * (0.12 - 0.24 * _smooth(t)),
                     by + fy * reach + py * (0.12 - 0.24 * _smooth(t)),
                     tz + 0.22 - 0.14 * _smooth(t))
            left = (bx - fx * 0.06 - px * 0.16, by - fy * 0.06 - py * 0.16, tz + 0.14)
        else:
            # Recuperação com zanshin
            right = (bx + fx * 0.18 + px * 0.05, by + fy * 0.18 + py * 0.05, tz + 0.12)
            left = (bx + fx * 0.08 - px * 0.14, by + fy * 0.08 - py * 0.14, tz + 0.15)
        return left, right

    # Guarda padrão fluida da kunoichi
    breathe = math.sin(c.walk_timer * (6.5 if c.is_moving else 2.5)) * (0.020 if c.is_moving else 0.010)
    left = (bx + fx * 0.12 - px * 0.13, by + fy * 0.12 - py * 0.13 + breathe, tz + 0.15)
    right = (bx + fx * 0.16 + px * 0.11, by + fy * 0.16 + py * 0.11 - breathe, tz + 0.11)
    return left, right


def _lock_is_behind(c, side_sign):
    """Determina se a mecha lateral esquerda (-1) ou direita (+1) está atrás da cabeça."""
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    lx = bx + fx * 0.02 + px * 0.065 * side_sign
    ly = by + fy * 0.02 + py * 0.065 * side_sign
    return mk.depth(c, lx, ly) < mk.depth(c, bx, by) - 0.008


def _side_lock(c, side_sign):
    """Mecha lateral feminina esguia (tsuya-kami) que emoldura graciosamente a bochecha."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.06)
    o = mk.cloth_offsets(c, 1, 0.8 * side_sign, trail, amp * 1.2, freq * 1.1, (bx, by))[0]

    p0 = (bx + fx * 0.040 + px * 0.046 * side_sign, by + fy * 0.040 + py * 0.046 * side_sign, hz + 0.138)
    p1 = (bx + fx * 0.045 + px * 0.050 * side_sign + o[0] * 0.4, by + fy * 0.045 + py * 0.050 * side_sign + o[1] * 0.4, hz + 0.075)
    p2 = (bx + fx * 0.048 + px * 0.046 * side_sign + o[0], by + fy * 0.048 + py * 0.046 * side_sign + o[1], hz + 0.015 + o[2])

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


def _draw_bun(c):
    """Coque alto estilo dango na coroa da cabeça com laço preto e mecha solta."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    bun_base = (bx - fx * 0.025, by - fy * 0.025, hz + 0.155)
    bun_top = (bx - fx * 0.032, by - fy * 0.032, hz + 0.198)

    # Base e corpo do coque afunilado compacto
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        bun_base, bun_top,
        w_start=0.065, h_start=0.065,
        w_end=0.046, h_end=0.046,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )
    # Laço preto prendendo a base do coque
    mk.cbox(c, bun_base[0], bun_base[1], bun_base[2] + 0.004, 0.072, 0.072, 0.014, P["tie"], outline=False)

    # Mecha/flick solto do coque esvoaçando para trás
    trail, amp, freq = mk.motion(c, 0.08)
    o = mk.cloth_offsets(c, 1, 0.5, trail, amp * 2.0, freq * 1.3, (bx, by))[0]
    tail_start = (bun_top[0] - fx * 0.015, bun_top[1] - fy * 0.015, bun_top[2] - 0.005)
    tail_end = (tail_start[0] - fx * 0.055 + px * 0.02 + o[0], tail_start[1] - fy * 0.055 + py * 0.02 + o[1], tail_start[2] - 0.025 + o[2])
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[tail_start, tail_end],
        widths=[0.018, 0.008],
        depth_thick=0.008,
        colors=[P["hair"], P["hair_light"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )


def _draw_scarf_tail(c):
    """Ponta longa do cachecol cinza billowing dinamicamente para trás no vento."""
    P = pal()
    bx, by, nz, fx, fy, px, py = c.base_x, c.base_y, c.neck_z, c.fx, c.fy, c.px, c.py
    root = (bx - fx * 0.07 + px * 0.03, by - fy * 0.07 + py * 0.03, nz + 0.02)
    trail, amp, freq = mk.motion(c, 0.12)
    offs = cloth.chain_offsets(4, c.walk_timer, 0.5, trail, (px, py),
                               amp=amp * 2.4, freq=freq * 1.2,
                               wind=cloth.wind_at(root[0], root[1]), wind_gain=0.12)
    spine = [root]
    for i, o in enumerate(offs):
        pt = (root[0] - fx * 0.07 * (i + 1) + px * 0.035 * (i + 1) + o[0],
              root[1] - fy * 0.07 * (i + 1) + py * 0.035 * (i + 1) + o[1],
              root[2] - 0.035 * (i + 1) + o[2])
        spine.append(pt)

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=spine,
        widths=[0.065, 0.055, 0.045, 0.032, 0.018],
        depth_thick=0.012,
        colors=[P["scarf"], P["scarf_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )


def _draw_dagger(c, hand):
    """Adaga curta shinobi com lâmina de aço forjado reluzente."""
    P = pal()
    d = mk.norm((c.fx * 0.70 - c.px * 0.25, c.fy * 0.70 - c.py * 0.25, -0.20 if not c.is_moving else -0.65))
    # Cabo envolto em couro preto e pomo metálico
    mk.obox(c, mk.add(hand, d, -0.07), d, 0.08, 0.024, 0.024, P["black"])
    mk.obox(c, mk.add(hand, d, -0.085), d, 0.016, 0.032, 0.020, P["chrome_dark"], outline=False)
    # Guarda oval cromada
    mk.obox(c, mk.add(hand, d, 0.015), d, 0.014, 0.046, 0.026, P["chrome_light"], outline=False)
    # Lâmina triangular afiada
    mk.obox(c, mk.add(hand, d, 0.03), d, 0.24, 0.038, 0.014, P["blade"])
    mk.obox(c, mk.add(hand, d, 0.04), d, 0.22, 0.012, 0.016, P["edge"], outline=False)

    # Rastro prateado translúcido durante golpe
    if c.is_melee and c.atk_progress is not None and c.atk_progress >= 0.30:
        for j in range(1, 4):
            g = mk.add(hand, (c.px * 0.03, c.py * 0.03, 0.0), -j * 1.5)
            mk.band(c, (mk.add(g, d, 0.08), mk.add(g, d, 0.28), mk.add(hand, d, 0.28), mk.add(hand, d, 0.08)), (220, 236, 255, int(160 / j)))


def draw_behind(c):
    """Camada traseira: mechas distantes, coque, cauda do cachecol e adaga quando virada de costas."""
    d_torso = mk.depth(c, c.base_x, c.base_y)

    # 1. Mechas laterais que caem no lado oculto da cabeça
    for s in (-1.0, 1.0):
        if _lock_is_behind(c, s):
            _side_lock(c, s)

    # 2. Coque se estiver no lado de trás da cabeça
    d_bun = mk.depth(c, c.base_x - c.fx * 0.02, c.base_y - c.fy * 0.02)
    if d_bun < d_torso + 0.01:
        _draw_bun(c)

    # 3. Ponta longa do cachecol se projetada para trás
    d_scarf = mk.depth(c, c.base_x - c.fx * 0.12, c.base_y - c.fy * 0.12)
    if d_scarf < d_torso:
        _draw_scarf_tail(c)

    # 4. Braços e armas se as mãos estiverem atrás do tronco
    hand_l, hand_r = _hands(c)
    d_gear = max(mk.depth(c, hand_l[0], hand_l[1]), mk.depth(c, hand_r[0], hand_r[1]))
    if d_gear < d_torso - 0.01:
        _draw_dagger(c, hand_r)


def draw_legs(c):
    """Pernas kunoichi contínuas sem degraus/prateleiras nos joelhos, com joelheira cromada e coldre."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.04)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0
        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.9 * sign, trail, (c.px, c.py), amp=amp * 0.5, freq=freq, wind=cloth.wind_at(foot[0], foot[1]))

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.4, sh[1] + o1[1] * 0.4, sh[2] + 0.16)
        ankle = (foot[0] + o2[0] * 0.3, foot[1] + o2[1] * 0.3, foot[2] + 0.06)

        # Fita contínua 3D da perna inteira (coxa até o tornozelo em malha justa)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, ankle],
            widths=[0.110, 0.096, 0.076],
            depth_thick=0.084,
            colors=[P["chrome"], P["chrome_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Joelheira cromada anatômica integrada no joelho (sem cubo gigante)
        mk.obox(c, (knee[0] + c.fx * 0.025, knee[1] + c.fy * 0.025, knee[2] - 0.015),
                (c.fx * 0.4, c.fy * 0.4, 0.8), 0.055, 0.075, 0.025, P["chrome_light"], outline=False)

        # Bota/tabi ninja justa no tornozelo e pé
        mk.cbox(c, ankle[0], ankle[1], ankle[2] + 0.015, 0.072, 0.072, 0.055, P["boot"], outline=True)
        # Pé com solado escuro
        flen, fwidth = 0.13, 0.065
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.016,
                flen, fwidth, 0.034, P["boot"], outline=True)
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.003,
                flen + 0.005, fwidth + 0.005, 0.010, P["sole"], outline=False)


def draw_obi(c):
    """Cinto de couro com fivela prateada e bombas de fumaça esféricas no quadril."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.075

    # Cinto de couro
    mk.cbox(c, bx, by, z - 0.008, c.pelvis_w, c.pelvis_w * 0.78, 0.060, P["belt"])
    # Fivela retangular cromada frontal
    if mk.depth(c, fx, fy) > -0.05:
        mk.cbox(c, bx + fx * 0.090, by + fy * 0.090, z + 0.002, 0.048, 0.018, 0.042, P["buckle"], outline=False)

    # Recipientes de bombas de fumaça no flanco direito
    for s_idx, b_off in enumerate((-0.035, 0.035)):
        b_pos = (bx - px * 0.13 + fx * (0.02 + b_off), by - py * 0.13 + fy * (0.02 + b_off), z - 0.02)
        mk.cbox(c, b_pos[0], b_pos[1], b_pos[2], 0.052, 0.052, 0.052, P["bomb"])
        mk.cbox(c, b_pos[0], b_pos[1], b_pos[2] + 0.032, 0.016, 0.016, 0.024, P["fuse"], outline=False)

    # Bolsa de utilidades em couro no flanco esquerdo
    mk.cbox(c, bx + px * 0.12 - fx * 0.02, by + py * 0.12 - fy * 0.02, z - 0.01, 0.055, 0.068, 0.075, P["leather"])


def draw_torso(c):
    """Colete-espartilho de couro preto com 4 fechos prateados sobre o traje justo cromado e gola scarf."""
    P = pal()
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.084

    # Base anatômica do colete de couro preto
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, tz - 0.010),
        (bx, by, tz + 0.220),
        w_start=0.205, h_start=0.155,
        w_end=0.225, h_end=0.165,
        color=P["torso"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Detalhes frontais: decote e fechos horizontais cromados
    if mk.depth(c, fx, fy) > -0.05:
        # Traje interno prateado no colarinho superior
        mk.cbox(c, bx + fx * (front - 0.002), by + fy * (front - 0.002), tz + 0.185, 0.072, 0.022, 0.045, P["chrome"], outline=False)
        # Toque sutil de pele no decote
        mk.cbox(c, bx + fx * front, by + fy * front, tz + 0.198, 0.045, 0.016, 0.026, P["skin"], outline=False)

        # 4 fivelas horizontais metálicas alinhadas no centro do peito
        for i in range(4):
            fz = tz + 0.025 + i * 0.042
            mk.cbox(c, bx + fx * (front + 0.005), by + fy * (front + 0.005), fz, 0.058, 0.012, 0.014, P["buckle"], outline=False)
            mk.cbox(c, bx + fx * (front + 0.007), by + fy * (front + 0.007), fz, 0.022, 0.014, 0.016, P["torso_dark"], outline=False)

    # Gola/cowl do cachecol cinza envolvendo a base do pescoço (desenhada no tronco para nunca sobrepor o queixo)
    nz = tz + 0.26
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, nz - 0.045),
        (bx, by, nz + 0.020),
        w_start=0.106, h_start=0.106,
        w_end=0.088, h_end=0.088,
        color=P["scarf"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
        cap_end=False,
    )
    mk.cbox(c, bx + fx * 0.010, by + fy * 0.010, nz - 0.012, 0.098, 0.098, 0.016, P["scarf_light"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço ágil com manga justa prateada, braçadeira cromada e luva ninja preta."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.205)
    h = (hand[0], hand[1], hand[2] - 0.065)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.020), (0.0, 0.0, -0.025))

    # Braço superior em traje cromado justo
    mk.limb(c, s, e, 0.052, P["chrome"], w_end=0.046)

    # Braçadeira / manopla cromada no antebraço
    wrist = mk.lerp(e, h, 0.88)
    mk.limb(c, e, wrist, 0.050, P["chrome_dark"], w_end=0.046, texture="metal")
    mk.limb(c, mk.lerp(e, h, 0.70), wrist, 0.054, P["chrome_light"], w_end=0.050, outline=False, texture="chrome")

    # Mão com luva ninja preta
    mk.cbox(c, h[0], h[1], h[2] - 0.020, 0.042, 0.042, 0.042, P["glove"])
    return s, e


def draw_sleeves(c, arms):
    """Ombreiras cromadas articuladas elegantes contornando os ombros femininos."""
    P = pal()
    for s, e, side in arms:
        z = s[2] + 0.015
        ox, oy = s[0] + c.px * side * 0.012, s[1] + c.py * side * 0.012
        # Placa superior cromada
        mk.obox(c, (ox - c.fx * 0.010, oy - c.fy * 0.010, z - 0.025),
                (c.px * side * 0.5, c.py * side * 0.5, -0.85),
                0.078, 0.086, 0.028, P["chrome"], texture="metal")
        # Rebordo polido brilhante
        mk.obox(c, (ox - c.fx * 0.008, oy - c.fy * 0.008, z - 0.020),
                (c.px * side * 0.5, c.py * side * 0.5, -0.85),
                0.068, 0.090, 0.012, P["chrome_light"], outline=False, texture="chrome")


def draw_head(c):
    """
    Cabeça e Cabelos de Kasumi (fiel ao retrato oficial):
    - Crânio esculpido em 3D com mechas platinadas integradas via draw_sculpted_head_3d.
    - Olhos anime azul-aço luminosos e nariz delicado via draw_portrait_face_3d.
    - Franja anime em mechas fluidas sobre a testa (acima da linha das sobrancelhas).
    - Mechas laterais (tsuya-kami) no lado visível da câmera.
    - Coque alto (dango) com laço e cauda.
    - Gola do cachecol cinza envolvendo o pescoço e ponta ao vento.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # 1. Mechas laterais que caem no lado visível da câmera
    for s in (-1.0, 1.0):
        if not _lock_is_behind(c, s):
            _side_lock(c, s)

    # 2. Franja anime em camadas na testa (estritamente acima dos olhos)
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.006
        for s in (-1.0, 1.0):
            b0 = (bx + fx * (front_d + 0.002) - px * 0.008 * s, by + fy * (front_d + 0.002) - py * 0.008 * s, hz + 0.148)
            b1 = (bx + fx * (front_d + 0.003) + px * 0.022 * s, by + fy * (front_d + 0.003) + py * 0.022 * s, hz + 0.136)
            b2 = (bx + fx * front_d + px * 0.040 * s, by + fy * front_d + py * 0.040 * s, hz + 0.118)
            draw_ribbon_mesh_3d(
                c.surface, c.camera,
                spine_points=[b0, b1, b2],
                widths=[0.016, 0.018, 0.010],
                depth_thick=0.008,
                colors=[P["hair"], P["hair_light"]],
                side_vec=(0.0, 0.0, 1.0),
                normal_vec=(fx, fy, 0.35),
                outline=False,
                alpha=c.alpha,
            )
        # Mecha central sutil
        b_mid0 = (bx + fx * (front_d + 0.003), by + fy * (front_d + 0.003), hz + 0.150)
        b_mid1 = (bx + fx * (front_d + 0.004) + px * 0.006, by + fy * (front_d + 0.004) + py * 0.006, hz + 0.126)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[b_mid0, b_mid1],
            widths=[0.014, 0.008],
            depth_thick=0.006,
            colors=[P["hair"], P["hair_light"]],
            side_vec=(0.0, 0.0, 1.0),
            normal_vec=(fx, fy, 0.35),
            outline=False,
            alpha=c.alpha,
        )

    # 3. Coque se estiver no lado visível
    d_torso = mk.depth(c, bx, by)
    d_bun = mk.depth(c, bx - fx * 0.02, by - fy * 0.02)
    if d_bun >= d_torso + 0.01:
        _draw_bun(c)

    # 4. Cauda longa do cachecol se projetada para frente/lado
    d_scarf = mk.depth(c, bx - fx * 0.12, by - fy * 0.12)
    if d_scarf >= d_torso:
        _draw_scarf_tail(c)


def draw_front(c, arm_l, arm_r):
    """Camada frontal: adaga renderiza APENAS se as mãos estiverem na frente do tronco."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_l, hand_r = _hands(c)
    d_gear = max(mk.depth(c, hand_l[0], hand_l[1]), mk.depth(c, hand_r[0], hand_r[1]))
    if d_gear >= d_torso - 0.01:
        _draw_dagger(c, hand_r)
