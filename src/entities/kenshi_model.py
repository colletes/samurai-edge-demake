"""
Kenshi, a espadachim do Iaijutsu (6.5.5): cabelo castanho-ruivo em rabo de cavalo alto com laço vermelho, quimono
carmim sem mangas com colarinho branco, mangas soltas largas com punho dourado, hakama larga e pregueada, obi com nó
na frente e a katana na cintura (saya à esquerda, mão direita no cabo).
Os ganchos são chamados por `render_voxel_humanoid`.
Mudanças só visuais: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.voxel_rig import calc_blade_slash_3d
from src.isometric.mesh_primitives import draw_ribbon_mesh_3d, draw_tapered_frustum_3d

SKIN = (248, 218, 192)
SKIN_SHADOW = (220, 180, 150)

DETAILED = {
    "hair": (152, 84, 50), "hair_light": (200, 122, 70), "hair_dark": (96, 50, 36), "ribbon": (206, 36, 54),
    "skin": SKIN, "skin_shadow": SKIN_SHADOW, "eye": (58, 34, 30), "lip": (206, 98, 104),
    "kimono": (180, 32, 54), "kimono_dark": (122, 20, 42), "collar": (244, 240, 236),
    "cuff": (214, 162, 52), "cuff_dark": (150, 104, 30),
    "hakama": (78, 66, 120), "hakama_dark": (50, 42, 84), "obi": (112, 94, 170),
    "sandal": (180, 146, 100), "strap": (40, 32, 36),
    "saya": (34, 28, 38), "ito": (52, 38, 40), "ito_light": (226, 216, 196), "gold": (232, 190, 66),
    "steel": (228, 236, 248), "edge": (252, 254, 255),
    "trail": (222, 38, 56), "trail_core": (255, 214, 196),
}


MATERIALS = {"kimono": "silk", "kimono_dark": "silk", "obi": "silk", "collar": "silk", "ribbon": "silk", "saya": "lacquer", "steel": "steel", "edge": "steel", "gold": "gold", "cuff": "gold", "hakama": "pleats"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return DETAILED


def _outward(c, side):
    return (c.px * side, c.py * side, 0.0)


def _sword_frame(c):
    """Ponto da boca da bainha (K), direção da bainha/lâmina (B) e do cabo (-B), na cintura esquerda."""
    k = (c.base_x + c.px * 0.11 + c.fx * 0.075, c.base_y + c.py * 0.11 + c.fy * 0.075, c.pelvis_z + 0.07)
    b = mk.norm((-c.fx * 0.80 + c.px * 0.40, -c.fy * 0.80 + c.py * 0.40, -0.32))
    return k, b


def idle_arms(c):
    """Neutra: mão direita cruza a barriga e empunha o cabo, esquerda segura a boca da bainha."""
    k, b = _sword_frame(c)
    grip = mk.add(k, b, -0.08)
    left = mk.add(k, b, 0.09)
    return (left[0], left[1], left[2] + 0.07), (grip[0], grip[1], grip[2] + 0.07)


def _arc_hand(c, p):
    a = -0.75 + p * 2.15
    return (c.base_x + c.fx * math.cos(a) * 0.24 - c.px * math.sin(a) * 0.24,
            c.base_y + c.fy * math.cos(a) * 0.24 - c.py * math.sin(a) * 0.24,
            c.torso_z + 0.18 - p * 0.10)


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def attack_arms(c):
    """Antecipação (mão no cabo, bainha presa), saque e corte em arco da esquerda para a direita, acompanhamento aberto."""
    p = c.atk_progress
    k, b = _sword_frame(c)
    grip = mk.add(mk.add(k, b, -0.08), (0.0, 0.0, 0.07))
    hand_r = mk.lerp(grip, _arc_hand(c, 0.22), _smooth((p - 0.08) / 0.14)) if p < 0.22 else _arc_hand(c, p)
    pull = _smooth((p - 0.1) / 0.3)
    left = mk.add(k, b, 0.09 + 0.10 * pull)
    return (left[0], left[1], left[2] + 0.07 - 0.04 * pull), hand_r


def _blade_dir(c, p):
    """Direção da lâmina: sai pela linha da bainha e gira rápido até a tangente do arco do corte."""
    _, b = _sword_frame(c)
    arc = calc_blade_slash_3d("kenshin", "ATTACK", p, c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py)["dir"]
    return mk.norm(mk.lerp(b, arc, _smooth((p - 0.2) / 0.1)))


# ---------------------------------------------------------------------------------------------------------------------
# Peças desenhadas por trás do corpo quando estão do lado oposto à câmera (rabo de cavalo, bainha) ou à frente dele
# ---------------------------------------------------------------------------------------------------------------------

def _tail_root(c):
    return (c.base_x - c.fx * 0.040, c.base_y - c.fy * 0.040, c.head_z + 0.160)


def _behind(c, point) -> bool:
    """Retorna True se o ponto estiver atrás do centro do tronco em relação à câmera."""
    return mk.depth(c, point[0], point[1]) < mk.depth(c, c.base_x, c.base_y) - 0.015


def _lock_is_behind(c, s: float) -> bool:
    """Retorna True se a mecha lateral da têmpora/bochecha estiver atrás do centro da cabeça."""
    tx = c.base_x + c.px * 0.058 * s
    ty = c.base_y + c.py * 0.058 * s
    return mk.is_lock_behind(c, (tx, ty), margin=0.005)


def _side_lock(c, s: float):
    """Mecha lateral flutuante que emoldura a têmpora e bochecha até a clavícula com física de vento."""
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
        widths=[0.018, 0.014, 0.009],
        depth_thick=0.010,
        colors=[P["hair"], P["hair_dark"]],
        side_vec=(fx, fy, 0.0),
        normal_vec=(px * s, py * s, 0.0),
        outline=False,
        alpha=c.alpha,
    )


def draw_behind(c):
    """Camada traseira: desenhada antes do corpo para itens do lado oposto à câmera."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    if _behind(c, _tail_root(c)):
        _ponytail(c)
    # Mechas laterais que estão no lado posterior da cabeça (desenhadas antes do crânio para oclusão perfeita)
    for s in (-1.0, 1.0):
        if _lock_is_behind(c, s):
            _side_lock(c, s)
    k, b = _sword_frame(c)
    saya_mid = mk.add(k, b, 0.22)
    if mk.depth(c, saya_mid[0], saya_mid[1]) < d_torso:
        _saya(c)
    if not c.is_melee or c.atk_progress < 0.1:
        tsuka_mid = mk.add(k, b, -0.08)
        if mk.depth(c, tsuka_mid[0], tsuka_mid[1]) < d_torso:
            _tsuka(c, k, b)


def _ponytail(c):
    """
    Rabo de cavalo alto e volumoso estilo anime com laço vermelho de seda:
    - Emerge do topo posterior da coroa com fonte arqueada para cima e para trás.
    - Cascata longa, orgânica e fluida em curva S que desce sobre as costas com física de vento.
    - Malha 3D volumosa facetada com mecha de brilho luminoso na crista.
    """
    P = pal()
    root = _tail_root(c)
    trail, amp, freq = mk.motion(c, 0.09)
    fx, fy = c.fx, c.fy
    px, py = c.px, c.py

    # 1. Base presa do cabelo (elástico / nó)
    mk.cbox(c, root[0], root[1], root[2] - 0.005, 0.046, 0.046, 0.032, P["hair_dark"], outline=False)

    # 2. Laço Vermelho de Seda na amarração (Laço em borboleta expressivo do retrato)
    mk.cbox(c, root[0] - fx * 0.008, root[1] - fy * 0.008, root[2] + 0.008, 0.042, 0.042, 0.034, P["ribbon"], outline=True)
    # Asas do laço arqueadas para cima e para fora (estilo anime perolado)
    for s in (-1.0, 1.0):
        wing_dir = (px * s * 0.72 - fx * 0.12, py * s * 0.72 - fy * 0.12, 0.55)
        mk.obox(c, (root[0] + px * s * 0.020 - fx * 0.006, root[1] + py * s * 0.020 - fy * 0.006, root[2] + 0.020),
                wing_dir, 0.062, 0.026, 0.036, P["ribbon"], outline=True)
    # Fitas penduradas do laço que balançam com o vento
    offs_ribbon = cloth.chain_offsets(3, c.walk_timer, 2.1, trail, (px, py), amp=amp * 1.5, freq=freq * 1.2, wind=cloth.wind_at(root[0], root[1]))
    for i, o in enumerate(offs_ribbon):
        mk.cbox(c, root[0] - fx * 0.025 + o[0], root[1] - fy * 0.025 + o[1],
                root[2] - 0.020 - 0.045 * i + o[2], 0.020, 0.016, 0.044, P["ribbon"], outline=False)

    # 3. Cascata Longa e Arqueada do Rabo de Cavalo Anime
    # Varre graciosamente lateralizado sobre o ombro direito como no retrato oficial (kenshi_bust.png)
    offs = cloth.chain_offsets(5, c.walk_timer, 0.4, trail, (px, py),
                               amp=amp * 1.8, freq=freq * 0.9, wind=cloth.wind_at(root[0], root[1]),
                               wind_gain=0.06)

    # Trajetória da mecha: sai da coroa, arqueia suavemente para trás e varre graciosamente como no retrato oficial (kenshi_bust.png)
    base_pts = [
        root,
        (root[0] - fx * 0.040 - px * 0.042, root[1] - fy * 0.040 - py * 0.042, root[2] + 0.038),  # Fonte arqueada elegante
        (root[0] - fx * 0.085 - px * 0.078, root[1] - fy * 0.085 - py * 0.078, root[2] + 0.012),  # Varredura lateral do ombro
        (root[0] - fx * 0.120 - px * 0.110, root[1] - fy * 0.120 - py * 0.110, root[2] - 0.075),  # Cascata no nível da clavícula/nuca
        (root[0] - fx * 0.135 - px * 0.132, root[1] - fy * 0.135 - py * 0.132, root[2] - 0.200),  # Mecha fluindo sobre o quimono
        (root[0] - fx * 0.115 - px * 0.150, root[1] - fy * 0.115 - py * 0.150, root[2] - 0.335),  # Flick final gracioso
    ]
    pts = [base_pts[0]] + [mk.add(base_pts[i + 1], offs[i]) for i in range(5)]
    widths = (0.048, 0.082, 0.092, 0.080, 0.060, 0.026)
    colors = (P["hair"], P["hair_light"], P["hair"], P["hair_dark"], P["hair"])

    # Malha 3D volumosa facetada
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=pts,
        widths=widths,
        depth_thick=0.062,
        colors=colors,
        side_vec=(px, py, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # 4. Mecha de Brilho Superior / Destaque de Volume
    hl_pts = [
        mk.add(pts[0], (0, 0, 0.006)),
        mk.add(pts[1], (0, 0, 0.010)),
        mk.add(pts[2], (0, 0, 0.008)),
        mk.add(pts[3], (0, 0, 0.005)),
    ]
    hl_widths = (0.025, 0.042, 0.046, 0.030)
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=hl_pts,
        widths=hl_widths,
        depth_thick=0.035,
        colors=[P["hair_light"], P["hair_light"], P["hair"]],
        side_vec=(px, py, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )


def _saya(c):
    P = pal()
    k, b = _sword_frame(c)
    mk.obox(c, k, b, 0.46, 0.044, 0.044, P["saya"])
    mk.obox(c, k, b, 0.03, 0.054, 0.054, P["gold"], outline=False)  # koiguchi
    mk.obox(c, mk.add(k, b, 0.43), b, 0.035, 0.048, 0.048, P["gold"], outline=False)  # kojiri
    offs = cloth.chain_offsets(2, c.walk_timer, 1.3, mk.motion(c, 0.05)[0], (c.px, c.py), amp=0.02, freq=2.2)  # sageo
    for i, o in enumerate(offs):
        a = mk.add(k, b, 0.05 + 0.035 * i)
        mk.cbox(c, a[0] + o[0], a[1] + o[1], a[2] - 0.05 - 0.04 * i, 0.016, 0.016, 0.05, P["ribbon"], outline=False)


def _tsuka(c, tsuba, blade_dir):
    P = pal()
    hilt = (-blade_dir[0], -blade_dir[1], -blade_dir[2])
    mk.obox(c, tsuba, hilt, 0.16, 0.036, 0.036, P["ito"])
    for t in (0.04, 0.085, 0.13):
        mk.obox(c, mk.add(tsuba, hilt, t), hilt, 0.02, 0.041, 0.041, P["ito_light"], outline=False)
    mk.obox(c, mk.add(tsuba, hilt, 0.155), hilt, 0.022, 0.042, 0.042, P["gold"], outline=False)  # kashira
    mk.obox(c, mk.add(tsuba, blade_dir, -0.008), blade_dir, 0.016, 0.082, 0.082, P["gold"], outline=False)  # tsuba


def draw_legs(c):
    """Hakama larga e pregueada contínua sem quebras ou degraus nas articulações, com waraji aparecendo sob a barra."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.05)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]
        sign = 1.0 if side == "L" else -1.0
        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.9 * sign, trail, (c.px, c.py), amp=amp * 0.7, freq=freq, wind=cloth.wind_at(ft[0], ft[1]))
        # Sandália waraji e pele do pé sob a barra
        mk.obox(c, (ft[0] - c.fx * 0.045, ft[1] - c.fy * 0.045, ft[2]), (c.fx, c.fy, 0.0), 0.13, 0.07, 0.03, P["sandal"])
        mk.obox(c, (ft[0] - c.fx * 0.02, ft[1] - c.fy * 0.02, ft[2] + 0.03), (c.fx, c.fy, 0.0), 0.095, 0.055, 0.03, P["skin"], outline=False)
        mk.obox(c, (ft[0] + c.fx * 0.02, ft[1] + c.fy * 0.02, ft[2] + 0.03), (c.fx, c.fy, 0.0), 0.02, 0.058, 0.032, P["strap"], outline=False)
        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.6, sh[1] + o1[1] * 0.6, sh[2] + 0.14)
        hem = (sh[0] + o2[0] * 0.6, sh[1] + o2[1] * 0.6, sh[2] + 0.015)
        # Hakama contínua 3D: compartilha vértices no joelho eliminando degraus ou tampas internas
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, hem],
            widths=[0.136, 0.152, 0.168],
            depth_thick=0.125,
            colors=[P["hakama"], P["hakama_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )


def draw_obi(c):
    """Obi largo com o nó na frente e duas pontas penduradas que balançam; placa lombar da hakama nas costas."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07
    d_torso = mk.depth(c, bx, by)

    # Faixa base do obi na cintura
    mk.cbox(c, bx, by, z - 0.012, c.pelvis_w, c.pelvis_w * 0.78, 0.018, P["hakama_dark"], outline=False)

    d_back = mk.depth(c, bx - fx * 0.108, by - fy * 0.108)
    kx, ky = bx + fx * 0.098 + px * 0.012, by + fy * 0.098 + py * 0.012
    d_front = mk.depth(c, kx, ky)

    # Koshi-ita (placa lombar da hakama nas costas): desenha apenas se o dorso/costas estiver voltado para a câmera
    if d_back >= d_torso - 0.04:
        mk.cbox(c, bx - fx * 0.108, by - fy * 0.108, c.pelvis_z + 0.04, 0.10, 0.07, 0.15, P["hakama_dark"])

    # Nó frontal do obi e laços pendurados: desenha apenas se a frente estiver voltada para a câmera
    if d_front >= d_torso - 0.04:
        mk.cbox(c, kx, ky, z + 0.005, 0.085, 0.05, 0.075, P["obi"])
        for s in (-1.0, 1.0):  # laços do nó
            mk.obox(c, (kx + px * 0.03 * s, ky + py * 0.03 * s, z + 0.045), (px * s, py * s, 0.25), 0.065, 0.032, 0.05, P["obi"])
        trail, amp, freq = mk.motion(c, 0.05)
        for k_idx, (s, length) in enumerate(((-1.0, 3), (1.0, 2))):
            offs = cloth.chain_offsets(length, c.walk_timer, 1.1 * k_idx, trail, (px, py), amp=amp * 1.4, freq=freq, wind=cloth.wind_at(kx, ky))
            for i, o in enumerate(offs):
                mk.cbox(c, kx + px * 0.03 * s + o[0], ky + fy * 0.012 + py * 0.03 * s + o[1], z - 0.012 - 0.07 * (i + 1) + o[2], 0.04, 0.026, 0.075, P["obi"])


def draw_torso(c):
    """
    Tronco de Kenshi fiel ao retrato oficial:
    - Quimono carmim sem mangas evidenciando ombros e clavícula nus de pele porcelana.
    - Decote sutil em V revelando forro de colarinho branco puro (collar).
    - Dobra transpassada do quimono carmim.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    chest_d = 0.17
    front = chest_d * 0.50 + 0.005

    # Detalhes frontais (colarinho branco, pele e transpasse) só devem ser renderizados
    # se o peito estiver voltado para a câmera, evitando que apareçam nas costas.
    if mk.depth(c, fx, fy) > -0.05:
        # 1. Colarinho branco (under-collar) sutil no decote em V
        c_apex = (bx + fx * front, by + fy * front, tz + 0.115)
        for s in (-1.0, 1.0):
            c_top = (bx + fx * (front - 0.003) + px * 0.048 * s, by + fy * (front - 0.003) + py * 0.048 * s, tz + 0.235)
            mk.limb(c, c_top, c_apex, 0.018, P["collar"], outline=False, height=0.010)

        # 2. Pele porcelana no centro do decote
        mk.cbox(c, bx + fx * (front - 0.002), by + fy * (front - 0.002), tz + 0.190, 0.040, 0.016, 0.050, P["skin"], outline=False)

        # 3. Transpasse carmim do quimono sobre o peito
        mk.cbox(c, bx + fx * (front + 0.002) + px * 0.018, by + fy * (front + 0.002) + py * 0.018, tz + 0.125, 0.068, 0.018, 0.110, P["kimono"], outline=False, texture="silk")


def draw_arm(c, shoulder, hand, side):
    """Braço ágil com ombro nu e punho flexível; mangas separadas caem do bíceps."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.205)
    h = (hand[0], hand[1], hand[2] - 0.065)
    out = _outward(c, side)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.03), (0.0, 0.0, -0.035))

    # Ombro nu anatômico proporcional
    mk.cbox(c, s[0], s[1], s[2] - 0.020, 0.062, 0.062, 0.058, P["skin"], outline=False)
    # Braço e antebraço afunilados de pele lisa
    mk.limb(c, s, e, 0.052, P["skin"], w_end=0.046)
    mk.limb(c, e, h, 0.046, P["skin"], w_end=0.040)
    # Mão
    mk.cbox(c, h[0], h[1], h[2] - 0.024, 0.044, 0.044, 0.044, P["skin"])
    return s, e


def draw_sleeves(c, arms):
    """Mangas soltas largas do quimono carmim caídas do bíceps, com barra brocada dourada."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.07)
    atk = math.sin(c.atk_progress * math.pi) if c.is_melee else 0.0
    for k, (s, e, side) in enumerate(arms):
        # A manga começa no bíceps abaixo do ombro nu (s[2] - 0.045)
        anchor = (s[0] + c.px * side * 0.040, s[1] + c.py * side * 0.040, s[2] - 0.045)
        drag = (trail[0] - c.fx * 0.12 * atk + c.px * side * 0.07 * atk, trail[1] - c.fy * 0.12 * atk + c.py * side * 0.07 * atk)
        offs = cloth.chain_offsets(3, c.walk_timer, 1.7 * k, drag, (c.px, c.py), amp=amp * 1.5, freq=freq, wind=cloth.wind_at(anchor[0], anchor[1]))
        up = (c.fx, c.fy, 0.0)
        spine_pts = [anchor]
        widths = [0.125]
        for i, o in enumerate(offs):
            pt = (anchor[0] + o[0] + c.px * side * 0.014 * (i + 1), anchor[1] + o[1] + c.py * side * 0.014 * (i + 1), anchor[2] - 0.088 * (i + 1) + o[2])
            spine_pts.append(pt)
            widths.append(0.140 + 0.028 * (i + 1))
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=spine_pts,
            widths=widths,
            depth_thick=0.055,
            colors=[P["kimono"], P["kimono"], P["kimono_dark"]],
            side_vec=up,
            normal_vec=(c.px * side, c.py * side, 0.0),
            outline=True,
            alpha=c.alpha,
        )
        o = offs[-1]
        bottom = (anchor[0] + o[0] + c.px * side * 0.042, anchor[1] + o[1] + c.py * side * 0.042, anchor[2] - 0.088 * 3 + o[2])
        # Barra brocada dourada graciosa (fita fina ao longo da borda inferior da manga, não um bloco)
        mk.obox(c, (bottom[0], bottom[1], bottom[2] + 0.015), (0.0, 0.0, -1.0), 0.028, 0.065, 0.190, P["cuff"], up=up)
        mk.obox(c, (bottom[0], bottom[1], bottom[2] + 0.015 - 0.010), (0.0, 0.0, -1.0), 0.008, 0.068, 0.194, P["cuff_dark"], up=up, outline=False)


def draw_head(c):
    """
    Cabeça e Cabelos de Kenshi (fiel ao retrato oficial):
    - Crânio esculpido em 3D com linha capilar orgânica via draw_sculpted_head_3d.
    - Mechas laterais esguias emoldurando a face no lado visível da câmera (far side vai para draw_behind).
    - Franja anime flutuante em arco gracioso na testa (acima dos olhos e sobrancelhas).
    - Rabo de cavalo alto anime ordenado por profundidade 3D (atrás se visto de frente, na frente se visto de costas).
    - Feições faciais Tekken 2/3 projetadas com nitidez absoluta via draw_portrait_face_3d.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py

    # 1. Mechas laterais voltadas para a câmera (emolduram as bochechas sem cruzar a face)
    for s in (-1.0, 1.0):
        if not _lock_is_behind(c, s):
            _side_lock(c, s)

    # 2. Franja anime flutuante sobre a testa (desenhada quando de frente ou perfil)
    if mk.facing_camera(c):
        front_d = c.head_w * 0.50 + 0.005

        # Franja primária varrida em arco gracioso pela parte superior da testa (acima das sobrancelhas)
        f_start = (bx + fx * front_d - px * 0.046, by + fy * front_d - py * 0.046, hz + 0.148)
        f_mid = (bx + fx * (front_d + 0.003) - px * 0.005, by + fy * (front_d + 0.003) - py * 0.005, hz + 0.138)
        f_end = (bx + fx * (front_d + 0.003) + px * 0.042, by + fy * (front_d + 0.003) + py * 0.042, hz + 0.126)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[f_start, f_mid, f_end],
            widths=[0.016, 0.020, 0.013],
            depth_thick=0.008,
            colors=[P["hair"], P["hair_light"]],
            side_vec=(0.0, 0.0, 1.0),
            normal_vec=(fx, fy, 0.35),
            outline=False,
            alpha=c.alpha,
        )

        # Camada secundária da franja para profundidade volumétrica anime
        f2_start = (bx + fx * (front_d + 0.002) - px * 0.024, by + fy * (front_d + 0.002) - py * 0.024, hz + 0.144)
        f2_end = (bx + fx * (front_d + 0.004) + px * 0.022, by + fy * (front_d + 0.004) + py * 0.022, hz + 0.130)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[f2_start, f2_end],
            widths=[0.014, 0.010],
            depth_thick=0.006,
            colors=[P["hair_light"], P["hair"]],
            side_vec=(0.0, 0.0, 1.0),
            normal_vec=(fx, fy, 0.35),
            outline=False,
            alpha=c.alpha,
        )

    # 3. Rabo de cavalo (se estiver do lado visível da câmera, ex: costas ou perfil)
    if not _behind(c, _tail_root(c)):
        _ponytail(c)


def draw_front(c, arm_l, arm_r):
    """Bainha (se estiver do lado da câmera), cabo e lâmina; no ataque a lâmina sai da bainha e deixa o rastro vermelho."""
    P = pal()
    d_torso = mk.depth(c, c.base_x, c.base_y)
    k, b = _sword_frame(c)
    saya_mid = mk.add(k, b, 0.22)
    if mk.depth(c, saya_mid[0], saya_mid[1]) >= d_torso:
        _saya(c)
    if not c.is_melee:
        tsuka_mid = mk.add(k, b, -0.08)
        if mk.depth(c, tsuka_mid[0], tsuka_mid[1]) >= d_torso:
            _tsuka(c, k, b)
        return
    p = c.atk_progress
    if p < 0.1:  # ainda embainhada, mão no cabo
        tsuka_mid = mk.add(k, b, -0.08)
        if mk.depth(c, tsuka_mid[0], tsuka_mid[1]) >= d_torso:
            _tsuka(c, k, b)
        return
    hand = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    d = _blade_dir(c, p)
    s_draw = _smooth((p - 0.1) / 0.1)  # saque: a lâmina aparece conforme o cabo vem da cintura para a mão
    tsuba = mk.lerp(k, hand, s_draw)
    length = 0.72 * s_draw
    _tsuka(c, tsuba, d)
    mk.obox(c, tsuba, d, length, 0.05, 0.034, P["steel"])
    mk.obox(c, mk.add(tsuba, d, 0.02), d, max(0.0, length - 0.02), 0.018, 0.036, P["edge"], outline=False)  # fio
    if p >= 0.34:
        _slash_trail(c, p, length)


def _slash_trail(c, p, length):
    """Meia-lua do corte: faixas translúcidas entre as posições recentes da ponta, de vermelho a branco quente no centro."""
    P = pal()
    steps = []
    for j in range(10):
        pj = p - 0.017 * j
        if pj < 0.3:
            break
        h = _arc_hand(c, pj)
        h = (h[0], h[1], h[2] - 0.065)
        d = _blade_dir(c, pj)
        steps.append((mk.add(h, d, length * 0.72), mk.add(h, d, length * 1.06)))
    for j in range(len(steps) - 1):
        a0, a1 = steps[j]
        b0, b1 = steps[j + 1]
        fade = (1.0 - j / 10.0) ** 1.3
        mk.band(c, (a0, a1, b1, b0), P["trail"] + (int(240 * fade),))
        mk.band(c, (mk.lerp(a0, a1, 0.55), a1, b1, mk.lerp(b0, b1, 0.55)), P["trail_core"] + (int(255 * fade),))
