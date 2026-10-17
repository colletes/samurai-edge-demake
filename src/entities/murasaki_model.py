"""
Murasaki, a kunoichi da Kusarigama (6.5.5):
- Rosto esculpido em 3D Tekken 2/3 com máscara shinobi púrpura, olhos violeta amendoados com duplo brilho e delineador.
- Cabelo preto com reflexo violeta: coque alto (odango) com laço e fitas esvoaçantes ao vento.
- Franja anime repartida e mechas laterais (tsuya-kami) com pontas amarradas em fitas roxas (ordenadas por profundidade 3D).
- Traje kunoichi justo preto-violáceo com transpasse em V sobre o busto e faixa Obi púrpura na cintura.
- Ombreiras metálicas de aço escuro com friso polido contornando os ombros.
- Pernas contínuas em leggings pretas sem quebras ou degraus nos joelhos, com botas tabi roxas e solado geta.
- Kusarigama completa: foice curva (kama) na direita e corrente com peso esférico (fundo) na esquerda.
- Ordenação dinâmica por profundidade (Painter's Algorithm): costas ocluem braços e armas perfeitamente quando virada.
"""
import math

import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.mesh_primitives import draw_ribbon_mesh_3d, draw_tapered_frustum_3d

DETAILED = {
    "suit": (26, 20, 36), "suit_dark": (16, 12, 22), "suit_light": (44, 34, 58),
    "wrap": (128, 54, 186), "wrap_dark": (84, 32, 126), "wrap_light": (185, 102, 246),
    "skin": (245, 218, 196), "skin_shadow": (212, 178, 155),
    "neck": (26, 20, 36),
    "hair": (24, 18, 30), "hair_light": (72, 48, 92), "hair_dark": (14, 10, 18),
    "mask": (118, 52, 172), "mask_light": (172, 98, 234),
    "eye": (188, 88, 235), "eye_core": (245, 215, 255), "liner": (14, 10, 18),
    "steel_dark": (48, 46, 58), "steel": (95, 92, 115), "steel_light": (195, 198, 218),
    "gold_trim": (214, 175, 78),
    "boot": (68, 36, 104), "sole": (32, 26, 32), "strap": (38, 24, 54),
    "chain": (168, 172, 186), "ball": (58, 56, 70), "ball_light": (140, 138, 158),
    "wood": (68, 42, 26), "blade": (224, 230, 244), "edge": (252, 254, 255),
    "aura": (195, 110, 255), "aura_core": (248, 225, 255),
}

MATERIALS = {
    "suit": "latex", "suit_dark": "latex", "wrap": "latex", "wrap_dark": "latex", "wrap_light": "latex",
    "boot": "leather", "strap": "leather", "steel_dark": "metal", "steel": "metal", "steel_light": "chrome",
    "mask": "latex", "mask_light": "latex", "ball": "metal", "chain": "metal", "blade": "steel", "edge": "steel"
}


def pal() -> dict:
    return DETAILED


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def _hand_pose(c, p=None):
    """(mão direita da foice, mão esquerda da corrente) da pose atual, antes do respiro."""
    bx, by, fx, fy, px, py, tz = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py, c.torso_z
    if p is not None:  # ataque
        if p < 0.3:
            w = _smooth(p / 0.3)
            right = (bx + fx * (0.10 - 0.18 * w) - px * 0.16, by + fy * (0.10 - 0.18 * w) - py * 0.16, tz + 0.27 + 0.14 * w)
        elif p < 0.7:
            t = (p - 0.3) / 0.4
            reach = 0.06 + 0.30 * math.sin(math.pi * t)
            lat = -0.17 + 0.34 * _smooth(t)
            right = (bx + fx * reach + px * lat, by + fy * reach + py * lat, tz + 0.41 - 0.34 * _smooth(t))
        else:
            right = (bx + fx * 0.14 + px * 0.17, by + fy * 0.14 + py * 0.17, tz + 0.07)
        left = (bx + px * 0.19 - fx * 0.05, by + py * 0.19 - fy * 0.05, tz + 0.13 - 0.05 * math.sin(math.pi * p))
        return right, left
    bob = math.sin(c.walk_timer * 2.8) * 0.015
    if c.is_moving:
        sw = math.sin(c.walk_timer * 9.0)
        right = (bx + fx * 0.11 - px * 0.16, by + fy * 0.11 - py * 0.16, tz + 0.20 + abs(sw) * 0.02)
        left = (bx + px * 0.17 + fx * sw * -0.15, by + py * 0.17 + fy * sw * -0.15, tz + 0.05 + abs(sw) * 0.02)
        return right, left
    return ((bx + fx * 0.10 - px * 0.16, by + fy * 0.10 - py * 0.16, tz + 0.28 + bob),
            (bx + fx * 0.13 + px * 0.18, by + fy * 0.13 + py * 0.18, tz - 0.01 + bob))


def idle_arms(c):
    right, left = _hand_pose(c)
    return left, right


def attack_arms(c):
    right, left = _hand_pose(c, c.atk_progress)
    return left, right


walk_arms = idle_arms


def _kama_dirs(c, arm_r):
    """(direção do cabo, lado para onde a lâmina se curva) da foice conforme a pose."""
    f, p = (c.fx, c.fy, 0.0), (c.px, c.py, 0.0)
    if c.is_melee:
        q = c.atk_progress
        if q < 0.3:
            return mk.norm((-c.fx * 0.35, -c.fy * 0.35, 0.95)), mk.norm(f)
        t = _smooth((q - 0.3) / 0.45)
        kd = mk.norm((c.fx * (-0.35 + 1.25 * t), c.fy * (-0.35 + 1.25 * t), 0.95 - 1.75 * t))
        bs = mk.norm((c.fx * (1.0 - t) + c.px * 1.1 * t, c.fy * (1.0 - t) + c.py * 1.1 * t, 0.0))
        return kd, bs
    if c.is_moving:
        return mk.norm((c.fx * 0.45 - c.px * 0.1, c.fy * 0.45 - c.py * 0.1, 0.9)), mk.norm(f)
    return mk.norm((c.fx * 0.30 - c.px * 0.08, c.fy * 0.30 - c.py * 0.08, 0.95)), mk.norm(f)


def _orbit_radius(q):
    return 0.55 + 0.30 * math.sin(math.pi * min(1.0, q))


def _ball_state(c, arm_l):
    """Posição da bola, ponto de controle da curva da corrente e a fase do giro (None fora do ataque)."""
    if c.is_melee:
        q = c.atk_progress
        theta = -2.2 + 5.0 * q
        radius = _orbit_radius(q)
        pos = (c.base_x + (math.cos(theta) * c.fx + math.sin(theta) * c.px) * radius,
               c.base_y + (math.cos(theta) * c.fy + math.sin(theta) * c.py) * radius,
               c.base_z + 0.58 + 0.10 * math.sin(theta))
        lag = theta - 0.9
        ctrl = (c.base_x + (math.cos(lag) * c.fx + math.sin(lag) * c.px) * radius * 0.6,
                c.base_y + (math.cos(lag) * c.fy + math.sin(lag) * c.py) * radius * 0.6, c.base_z + 0.55)
        return pos, ctrl, theta
    t = c.walk_timer
    sway = math.sin(t * (7.0 if c.is_moving else 1.9)) * (0.07 if c.is_moving else 0.035)
    drop = 0.30 if not c.is_moving else 0.26
    pos = (arm_l[0] + c.px * sway + c.fx * 0.02, arm_l[1] + c.py * sway + c.fy * 0.02, arm_l[2] - 0.075 - drop)
    return pos, None, None


def _curve(a, ctrl, b, count):
    if ctrl is None:
        return mk.chain_points(a, b, count, sag=0.05)
    pts = []
    for i in range(count + 1):
        t = i / count
        u = 1.0 - t
        pts.append((u * u * a[0] + 2 * u * t * ctrl[0] + t * t * b[0], u * u * a[1] + 2 * u * t * ctrl[1] + t * t * b[1],
                    u * u * a[2] + 2 * u * t * ctrl[2] + t * t * b[2]))
    return pts


def _behind(c, point) -> bool:
    """Retorna True se o ponto estiver atrás do centro do tronco em relação à câmera."""
    return mk.depth(c, point[0], point[1]) < mk.depth(c, c.base_x, c.base_y) - 0.015


def _lock_is_behind(c, s: float) -> bool:
    """Retorna True se a mecha lateral da têmpora estiver no lado posterior da cabeça."""
    tx = c.base_x + c.px * 0.058 * s
    ty = c.base_y + c.py * 0.058 * s
    return mk.is_lock_behind(c, (tx, ty), margin=0.005)


def _side_lock(c, s: float):
    """Mecha lateral kunoichi esguia com ponta amarrada em fita roxa (fiel ao retrato)."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.05)
    o = cloth.chain_offsets(2, c.walk_timer, 0.9 * s, trail, (px, py), amp=amp * 0.6, freq=freq)

    m_top = (bx + px * 0.058 * s + fx * 0.012, by + py * 0.058 * s + fy * 0.012, hz + 0.088)
    m_mid = (bx + px * 0.056 * s + fx * 0.016 + o[0][0], by + py * 0.056 * s + fy * 0.016 + o[0][1], hz + 0.028 + o[0][2])
    m_bot = (bx + px * 0.054 * s + fx * 0.016 + o[1][0], by + py * 0.054 * s + fy * 0.016 + o[1][1], hz - 0.026 + o[1][2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[m_top, m_mid, m_bot],
        widths=[0.016, 0.013, 0.008],
        depth_thick=0.010,
        colors=[P["hair"], P["hair_dark"]],
        side_vec=(fx, fy, 0.0),
        normal_vec=(px * s, py * s, 0.0),
        outline=False,
        alpha=c.alpha,
    )
    # Fita roxa amarrada na ponta da mecha
    mk.cbox(c, m_bot[0], m_bot[1], m_bot[2] - 0.006, 0.016, 0.016, 0.012, P["wrap"], outline=False)


def _bun_pos(c):
    return (c.base_x - c.fx * 0.020, c.base_y - c.fy * 0.020, c.head_z + 0.165)


def _draw_bun(c):
    """Coque alto estilo odango no topo posterior da cabeça com laço em borboleta de seda púrpura."""
    P = pal()
    root = _bun_pos(c)
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # 1. Base do coque amarrada com fita de seda roxa
    mk.cbox(c, root[0], root[1], root[2] - 0.008, 0.062, 0.062, 0.022, P["wrap"], outline=False)

    # 2. Coque volumoso esculpido
    mk.cbox(c, root[0], root[1], root[2] + 0.014, 0.076, 0.076, 0.062, P["hair"])
    mk.cbox(c, root[0], root[1], root[2] + 0.038, 0.054, 0.054, 0.025, P["hair_light"], outline=False)

    # 3. Asas do laço roxo na base do coque
    for s in (-1.0, 1.0):
        wing_dir = (px * s * 0.75 - fx * 0.15, py * s * 0.75 - fy * 0.15, 0.5)
        mk.obox(c, (root[0] + px * s * 0.022 - fx * 0.008, root[1] + py * s * 0.022 - fy * 0.008, root[2] + 0.006),
                wing_dir, 0.058, 0.022, 0.030, P["wrap"], outline=True)


def _streamers(c):
    """Duas fitas de seda roxa longas que esvoaçam dinamicamente ao vento a partir do coque."""
    P = pal()
    root = _bun_pos(c)
    trail, amp, freq = mk.motion(c, 0.09)
    fx, fy = c.fx, c.fy
    px, py = c.px, c.py

    for k, side in enumerate((0.6, -0.8)):
        offs = cloth.chain_offsets(4, c.walk_timer, 1.2 * k, trail, (px, py),
                                   amp=amp * 2.0, freq=freq * 1.1,
                                   wind=cloth.wind_at(root[0], root[1]), wind_gain=0.07)
        pts = [root]
        for i, o in enumerate(offs):
            pt = (root[0] - fx * 0.065 * (i + 1) + px * side * 0.045 * (i + 1) + o[0],
                  root[1] - fy * 0.065 * (i + 1) + py * side * 0.045 * (i + 1) + o[1],
                  root[2] - 0.030 * (i + 1) + o[2])
            pts.append(pt)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=pts,
            widths=[0.024, 0.022, 0.016, 0.012, 0.008],
            depth_thick=0.010,
            colors=[P["wrap"], P["wrap_light"], P["wrap_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(fx, fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )


def _draw_gear(c, hand_l, hand_r):
    """Renderiza a foice (kama), a corrente de ferro e o peso esférico (fundo)."""
    P = pal()
    kd, bs = _kama_dirs(c, hand_r)
    pommel = mk.add(hand_r, kd, -0.075)
    ball, ctrl, theta = _ball_state(c, hand_l)
    if theta is not None:
        _ball_trail(c, theta)
    first = mk.chain_points(pommel, hand_l, 5, sag=0.07)
    second = _curve(hand_l, ctrl, ball, 6)
    for pts in (first, second):
        for i in range(len(pts) - 1):
            mk.limb(c, pts[i], pts[i + 1], 0.022, P["chain"] if i % 2 else P["steel"], outline=False)
    mk.limb(c, mk.add(hand_l, (0, 0, 1), 0.040), mk.add(hand_l, (0, 0, -1), 0.040), 0.030, P["steel_dark"])
    _ball(c, ball)
    _kama(c, hand_r, kd, bs)


def draw_behind(c):
    """Camada traseira: desenhada antes do corpo para itens do lado oposto à câmera."""
    d_torso = mk.depth(c, c.base_x, c.base_y)

    # 1. Coque e fitas esvoaçantes se estiverem no lado de trás
    bp = _bun_pos(c)
    if _behind(c, bp):
        _draw_bun(c)
        _streamers(c)

    # 2. Mechas laterais que estão no lado posterior da cabeça (oclusão perfeita pelo crânio)
    for s in (-1.0, 1.0):
        if _lock_is_behind(c, s):
            _side_lock(c, s)

    # 3. Foice e corrente se as mãos estiverem atrás do tronco (ocluídas pelo dorso)
    hand_r, hand_l = _hand_pose(c, c.atk_progress if c.is_melee else None)
    d_gear = mk.depth(c, (hand_r[0] + hand_l[0]) * 0.5, (hand_r[1] + hand_l[1]) * 0.5)
    if d_gear < d_torso:
        _draw_gear(c, hand_l, hand_r)


def draw_legs(c):
    """Leggings kunoichi justas e contínuas sem degraus nos joelhos, com botas tabi e sola geta."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.04)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]
        sign = 1.0 if side == "L" else -1.0
        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.9 * sign, trail, (c.px, c.py), amp=amp * 0.5, freq=freq, wind=cloth.wind_at(ft[0], ft[1]))

        # Pé e sola geta
        mk.obox(c, (ft[0] - c.fx * 0.045, ft[1] - c.fy * 0.045, ft[2]), (c.fx, c.fy, 0.0), 0.125, 0.065, 0.022, P["sole"])
        mk.obox(c, (ft[0] - c.fx * 0.025, ft[1] - c.fy * 0.025, ft[2] + 0.022), (c.fx, c.fy, 0.0), 0.095, 0.055, 0.038, P["boot"])

        # Perna contínua 3D elegante: coxa, joelho e canela compartilham vértices
        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.4, sh[1] + o1[1] * 0.4, sh[2] + 0.16)
        ankle = (ft[0] + o2[0] * 0.3, ft[1] + o2[1] * 0.3, ft[2] + 0.06)

        # Coxa e canela em tecido justo preto-violáceo com acabamento latex
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, ankle],
            widths=[0.108, 0.094, 0.078],
            depth_thick=0.088,
            colors=[P["suit"], P["suit_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Cano da bota tabi roxa no tornozelo/canela inferior
        mk.cbox(c, ankle[0], ankle[1], ankle[2] + 0.015, 0.082, 0.082, 0.065, P["boot"], outline=True)
        # Tira de amarração da bota
        mk.cbox(c, ankle[0], ankle[1], ankle[2] + 0.042, 0.086, 0.086, 0.016, P["strap"], outline=False)


def draw_obi(c):
    """Faixa Obi púrpura na cintura; nó e laços pendurados nas costas só desenham quando as costas estão visíveis."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.08
    d_torso = mk.depth(c, bx, by)

    # Faixa base do obi na cintura
    mk.cbox(c, bx, by, z - 0.010, c.pelvis_w, c.pelvis_w * 0.76, 0.075, P["wrap"], texture="latex")
    # Filete central contrastante
    mk.cbox(c, bx, by, z + 0.015, c.pelvis_w + 0.004, c.pelvis_w * 0.77, 0.018, P["wrap_light"], outline=False)

    # Nó das costas e pontas soltas: só renderizam se as costas estiverem voltadas para a câmera
    d_back = mk.depth(c, bx - fx * 0.110, by - fy * 0.110)
    if d_back >= d_torso - 0.04:
        kx, ky = bx - fx * 0.105, by - fy * 0.105
        mk.cbox(c, kx, ky, z + 0.01, 0.065, 0.045, 0.065, P["wrap_dark"])
        for s in (-1.0, 1.0):
            mk.obox(c, (kx, ky, z + 0.025), (px * s, py * s, 0.35), 0.065, 0.026, 0.045, P["wrap"])
        trail, amp, freq = mk.motion(c, 0.06)
        for k, s in enumerate((-1.0, 1.0)):
            offs = cloth.chain_offsets(2, c.walk_timer, 0.9 * k, trail, (px, py), amp=amp * 1.3, freq=freq, wind=cloth.wind_at(kx, ky))
            for i, o in enumerate(offs):
                mk.cbox(c, kx - fx * 0.018 * (i + 1) + px * 0.022 * s + o[0],
                        ky - fy * 0.018 * (i + 1) + py * 0.022 * s + o[1],
                        z - 0.055 * (i + 1) + o[2],
                        0.028, 0.020, 0.058, P["wrap"] if i == 0 else P["wrap_dark"], outline=False)


def draw_torso(c):
    """Traje shinobi justo com transpasse em V roxo sobre o busto e decote sutil de pele."""
    P = pal()
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.085

    # Base justa do colete shinobi preto-violáceo
    mk.cbox(c, bx, by, tz - 0.005, 0.210, 0.160, 0.130, P["suit"], texture="latex")

    # Detalhes frontais (transpasse em V roxo e pele) SÓ renderizam se a frente estiver voltada para a câmera
    if mk.depth(c, fx, fy) > -0.05:
        # Transpasse em V roxo sobre o busto
        apex = (bx + fx * (front + 0.008), by + fy * (front + 0.008), tz + 0.130)
        for s in (-1.0, 1.0):
            top = (bx + fx * (front + 0.004) + px * 0.054 * s, by + fy * (front + 0.004) + py * 0.054 * s, tz + 0.245)
            mk.limb(c, top, apex, 0.026, P["wrap"], outline=False, height=0.016)

        # Traje interno escuro no centro do decote V
        mk.cbox(c, bx + fx * (front + 0.003), by + fy * (front + 0.003), tz + 0.180, 0.042, 0.014, 0.055, P["suit_dark"], outline=False)

        # Faixas purpuras cruzadas no abdômen (estilo kunoichi do retrato)
        for s in (-1.0, 1.0):
            a = (bx + fx * (front + 0.005) + px * 0.068 * s, by + fy * (front + 0.005) + py * 0.068 * s, tz + 0.110)
            b = (bx + fx * (front + 0.005) - px * 0.056 * s, by + fy * (front + 0.005) - py * 0.056 * s, tz + 0.015)
            mk.limb(c, a, b, 0.026, P["wrap_dark"], outline=False, height=0.014)


def draw_arm(c, shoulder, hand, side):
    """Braço ágil com pele lisa, ombreira escura e braçadeira kunoichi com friso prateado."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.205)
    h = (hand[0], hand[1], hand[2] - 0.065)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.025), (0.0, 0.0, -0.030))

    # Ombro e braço superior de pele feminina esguia
    mk.cbox(c, s[0], s[1], s[2] - 0.018, 0.056, 0.056, 0.050, P["skin"], outline=False)
    mk.limb(c, s, e, 0.050, P["skin"], w_end=0.044)

    # Braçadeira / manopla de aço escuro no antebraço
    wrist = mk.lerp(e, h, 0.88)
    mk.limb(c, e, wrist, 0.052, P["steel_dark"], w_end=0.048, texture="metal")
    # Friso de contraste em aço polido
    mk.limb(c, mk.lerp(e, h, 0.72), wrist, 0.056, P["steel_light"], w_end=0.052, outline=False, texture="chrome")
    # Mão enluvada
    mk.cbox(c, h[0], h[1], h[2] - 0.024, 0.044, 0.044, 0.044, P["suit_dark"])
    return s, e


def draw_sleeves(c, arms):
    """Ombreiras kunoichi elegantes de aço escuro com borda metálica polida contornando o deltoide."""
    P = pal()
    for s, e, side in arms:
        z = s[2] + 0.015
        ox, oy = s[0] + c.px * side * 0.015, s[1] + c.py * side * 0.015
        # Placa curva principal do ombro
        mk.obox(c, (ox - c.fx * 0.015, oy - c.fy * 0.015, z - 0.035), (c.px * side * 0.5, c.py * side * 0.5, -0.8),
                0.085, 0.090, 0.035, P["steel_dark"], texture="metal")
        # Borda chanfrada de contraste em aço polido
        mk.obox(c, (ox - c.fx * 0.012, oy - c.fy * 0.012, z - 0.028), (c.px * side * 0.5, c.py * side * 0.5, -0.8),
                0.075, 0.094, 0.014, P["steel_light"], outline=False, texture="chrome")
        # Detalhe de engaste dourado sutil
        mk.cbox(c, ox + c.fx * 0.035, oy + c.fy * 0.035, z - 0.015, 0.020, 0.020, 0.020, P["gold_trim"], outline=False)


def draw_head(c):
    """
    Cabeça e Cabelos de Murasaki (fiel ao retrato oficial):
    - Crânio esculpido em 3D com linha capilar orgânica via draw_sculpted_head_3d.
    - Máscara shinobi 3D roxa e olhos violeta expressivos com delineador alado via draw_portrait_face_3d.
    - Franja anime repartida flutuando sobre a testa.
    - Mechas laterais esguias emoldurando a face no lado visível da câmera com fitas nas pontas.
    - Coque alto (odango) e fitas esvoaçantes ao vento.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py

    # 1. Mechas laterais no lado voltado para a câmera
    for s in (-1.0, 1.0):
        if not _lock_is_behind(c, s):
            _side_lock(c, s)

    # 2. Franja repartida anime flutuante na parte superior da testa
    if mk.facing_camera(c):
        front_d = c.head_w * 0.50 + 0.005
        for s in (-1.0, 1.0):
            b_start = (bx + fx * (front_d + 0.002) - px * 0.006 * s, by + fy * (front_d + 0.002) - py * 0.006 * s, hz + 0.146)
            b_mid = (bx + fx * (front_d + 0.003) + px * 0.022 * s, by + fy * (front_d + 0.003) + py * 0.022 * s, hz + 0.136)
            b_end = (bx + fx * front_d + px * 0.042 * s, by + fy * front_d + py * 0.042 * s, hz + 0.124)
            draw_ribbon_mesh_3d(
                c.surface, c.camera,
                spine_points=[b_start, b_mid, b_end],
                widths=[0.016, 0.018, 0.012],
                depth_thick=0.008,
                colors=[P["hair"], P["hair_light"]],
                side_vec=(0.0, 0.0, 1.0),
                normal_vec=(fx, fy, 0.35),
                outline=False,
                alpha=c.alpha,
            )

    # 3. Coque e fitas esvoaçantes se estiverem no lado voltado para a câmera (ex: costas ou perfil)
    bp = _bun_pos(c)
    if not _behind(c, bp):
        _draw_bun(c)
        _streamers(c)


def draw_front(c, arm_l, arm_r):
    """Camada frontal: desenhada após o corpo se as armas estiverem à frente do tronco."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    d_gear = mk.depth(c, (hand_r[0] + hand_l[0]) * 0.5, (hand_r[1] + hand_l[1]) * 0.5)
    if d_gear >= d_torso:
        _draw_gear(c, hand_l, hand_r)


def _kama(c, hand, kd, bs):
    """Foice de combate (kama) com lâmina prateada curva e encaixes de ferro negro."""
    P = pal()
    mk.limb(c, mk.add(hand, kd, -0.075), mk.add(hand, kd, 0.27), 0.042, P["wood"], texture="wood")
    mk.limb(c, mk.add(hand, kd, -0.085), mk.add(hand, kd, -0.06), 0.052, P["steel_dark"], outline=False)
    mk.limb(c, mk.add(hand, kd, 0.245), mk.add(hand, kd, 0.30), 0.054, P["steel_dark"])
    top = mk.add(hand, kd, 0.29)
    prev = top
    segments = (
        (mk.norm(mk.add(bs, kd, 0.25)), 0.17, 0.058),
        (mk.norm(mk.add(mk.add((0, 0, 0), bs, 0.65), kd, -0.65)), 0.13, 0.050),
        (mk.norm(mk.add(mk.add((0, 0, 0), bs, 0.2), kd, -1.0)), 0.095, 0.042),
    )
    for d, length, height in segments:
        mk.obox(c, prev, d, length, 0.016, height, P["blade"], up=kd, texture="steel")
        mk.obox(c, prev, d, length, 0.018, 0.010, P["edge"], up=kd, outline=False)
        prev = mk.add(prev, d, length)


def _ball(c, pos):
    """Peso esférico facetado de ferro negro (fundo) na ponta da corrente."""
    P = pal()
    for w, d, h in ((0.110, 0.080, 0.080), (0.080, 0.110, 0.080), (0.080, 0.080, 0.110)):
        mk.cbox(c, pos[0], pos[1], pos[2] - h / 2, w, d, h, P["ball"], texture="metal")
    mk.cbox(c, pos[0] - 0.010, pos[1] - 0.010, pos[2] + 0.018, 0.026, 0.026, 0.026, P["ball_light"], outline=False)


def _ball_trail(c, theta):
    """Rastro de energia mística púrpura deixado pelo arco veloz do ataque com o peso da corrente."""
    P = pal()
    q = c.atk_progress
    pts = []
    for j in range(9):
        th = theta - 0.22 * j
        qj = q - 0.044 * j
        if qj < 0.0:
            break
        r = _orbit_radius(qj)
        pts.append((c.base_x + (math.cos(th) * c.fx + math.sin(th) * c.px) * r,
                    c.base_y + (math.cos(th) * c.fy + math.sin(th) * c.py) * r,
                    c.base_z + 0.58 + 0.10 * math.sin(th)))
    for j in range(len(pts) - 1):
        fade = 1.0 - j / 9.0
        a, b = pts[j], pts[j + 1]
        mk.band(c, ((a[0], a[1], a[2] + 0.07), (b[0], b[1], b[2] + 0.07), (b[0], b[1], b[2] - 0.07), (a[0], a[1], a[2] - 0.07)), P["aura"] + (int(170 * fade),))
        mk.band(c, ((a[0], a[1], a[2] + 0.025), (b[0], b[1], b[2] + 0.025), (b[0], b[1], b[2] - 0.025), (a[0], a[1], a[2] - 0.025)), P["aura_core"] + (int(210 * fade),))
