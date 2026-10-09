"""
Julie, a mosqueteira (6.5.5): chapéu azul de aba larga com pluma branca longa, cabelo ruivo com trança sobre o ombro, gola de
renda, túnica azul-real com botões dourados e mangas bufantes com punhos de renda, bandoleira de couro com flor-de-lis, luvas
brancas, calça cinza em botas marrons altas de cano dobrado, capa azul que esvoaça (e gira no CAPE_FLOURISH) e o florete de
guarda em concha.
Só o visual muda: duração do ataque, alcance e hitboxes não mudam.
"""
import math

from src.entities import model_kit as mk
from src.isometric.voxel_rig import calc_blade_slash_3d

PALETTE = {
    "torso": (30, 70, 164), "pants": (150, 152, 162), "hair": (176, 62, 42), "belt": (112, 72, 42),
    "skin": (244, 214, 190), "skin_shadow": (212, 176, 152),
    "blue": (30, 70, 164), "blue_dark": (20, 48, 124), "cape": (34, 74, 172), "cape_dark": (22, 52, 130), "gold": (232, 190, 70), "lace": (246, 244, 238), "lace_dark": (214, 212, 208),
    "leather": (112, 72, 42), "boot": (96, 58, 30), "boot_cuff": (140, 92, 52), "glove": (246, 244, 238), "hat": (28, 66, 156), "plume": (248, 246, 240), "plume_dark": (214, 212, 214),
    "eye": (52, 96, 120), "brow": (130, 50, 36), "lip": (196, 84, 90), "steel": (196, 214, 250), "edge": (252, 254, 255), "grip": (60, 40, 28),
    "aura": (150, 190, 255), "aura_core": (240, 248, 255),
}


MATERIALS = {"cape": "velvet", "cape_dark": "velvet", "blue": "brocade", "blue_dark": "velvet", "leather": "leather", "boot": "leather", "boot_cuff": "leather", "lace": "knit", "lace_dark": "knit", "glove": "silk", "hat": "velvet", "pants": "silk", "steel": "steel", "gold": "gold"}  # chave da paleta -> textura de material (6.5.8)


def pal() -> dict:
    return PALETTE


def _flourishing(c) -> bool:
    return c.state == "CAPE_FLOURISH"


def _cape(c):
    """Capa pendurada nas costas, com bordado dourado; balança e é empurrada pelo vento."""
    P = pal()
    anchor = (c.base_x - c.fx * 0.1, c.base_y - c.fy * 0.1, c.torso_z + 0.24)
    last = mk.panels(c, anchor, 5, 0.13, 0.26, 0.026, (P["cape"], P["cape"], P["cape"], P["cape_dark"], P["cape_dark"]), phase=0.4, up=(c.fx, c.fy, 0.0),
                     drag=(-c.fx * 0.05, -c.fy * 0.05), flare=0.016)
    for i in range(3):
        mk.cbox(c, last[0] + c.px * (i - 1) * 0.07, last[1] + c.py * (i - 1) * 0.07, last[2] - 0.01, 0.034, 0.03, 0.03, P["gold"], outline=False)


def draw_behind(c):
    if mk.facing_camera(c):
        mk.hair_volume(c, pal()["hair"], size=0.15, height=0.13)
        if not _flourishing(c):
            _cape(c)


def draw_legs(c):
    """Calça cinza justa em botas marrons altas com o cano dobrado."""
    P = pal()
    mk.legs(c, P["pants"], boot=P["boot"], boot_h=0.24, tight_w=(0.108, 0.092), foot_color=P["boot"], foot_len=0.15, foot_w=0.07, sole=(40, 26, 16), cuff=P["boot_cuff"])


def draw_obi(c):
    """Cinto de couro com fivela dourada e a bainha do florete no quadril esquerdo."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z
    mk.cbox(c, bx, by, z + 0.065, c.pelvis_w - 0.008, c.pelvis_w * 0.8, 0.06, P["leather"])
    mk.cbox(c, bx + fx * 0.088, by + fy * 0.088, z + 0.068, 0.05, 0.02, 0.05, P["gold"], outline=False)
    k = (bx + px * 0.13, by + py * 0.13, z + 0.06)
    d = mk.norm((-fx * 0.75 + px * 0.2, -fy * 0.75 + py * 0.2, -0.55))
    mk.obox(c, k, d, 0.5, 0.034, 0.034, P["leather"])
    mk.obox(c, mk.add(k, d, 0.47), d, 0.04, 0.04, 0.04, P["gold"], outline=False)


def draw_torso(c):
    """Gola de renda, botões dourados, bandoleira de couro com flor-de-lis e a capa quando está nas costas."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.085 + 0.006
    for i in range(3):
        mk.cbox(c, bx + fx * front, by + fy * front, tz + 0.02 + i * 0.055, 0.022, 0.012, 0.022, P["gold"], outline=False)
    a = (bx - px * 0.1 + fx * (front + 0.004), by - py * 0.1 + fy * (front + 0.004), tz + 0.26)
    b = (bx + px * 0.1 + fx * (front + 0.004), by + py * 0.1 + fy * (front + 0.004), tz + 0.0)
    mk.limb(c, a, b, 0.036, P["leather"], outline=False, height=0.018)
    mk.cbox(c, bx + fx * (front + 0.008), by + fy * (front + 0.008), tz + 0.115, 0.04, 0.014, 0.04, P["gold"], outline=False)
    nz = c.neck_z
    mk.cbox(c, bx, by, nz - 0.03, 0.15, 0.14, 0.04, P["lace"])
    for k in range(6):  # pontas da renda
        ang = k * math.pi / 3.0
        mk.cbox(c, bx + math.cos(ang) * 0.075 - 0.012, by + math.sin(ang) * 0.07 - 0.012, nz - 0.055, 0.024, 0.024, 0.03, P["lace"], outline=False)
    if not mk.facing_camera(c) and not _flourishing(c):
        _cape(c)


def draw_arm(c, shoulder, hand, side):
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], sleeve=P["blue"], sleeve_to=1.1, glove=P["glove"], bracer=P["lace"], bracer_span=(0.72, 0.97), w=0.052)


def draw_sleeves(c, arms):
    """Mangas bufantes: ombro volumoso com talhos dourados e punho de renda."""
    P = pal()
    for s, e, side in arms:
        ox, oy = c.px * side * 0.02, c.py * side * 0.02
        mk.cbox(c, s[0] + ox, s[1] + oy, s[2] - 0.075, 0.1, 0.1, 0.11, P["blue"])
        for k in (-1.0, 1.0):
            mk.limb(c, (s[0] + ox + c.fx * 0.05 * k, s[1] + oy + c.fy * 0.05 * k, s[2] + 0.03), (s[0] + ox + c.fx * 0.05 * k, s[1] + oy + c.fy * 0.05 * k, s[2] - 0.07), 0.01, P["gold"], outline=False)
        mk.cbox(c, e[0], e[1], e[2] - 0.02, 0.08, 0.08, 0.06, P["blue_dark"], outline=False)


def draw_head(c):
    """
    Rosto limpo de pele suave, cabelo castanho-acobreado com trança elegante,
    e o autêntico Chapéu de Mosqueteira Cavalier do séc. XVII fiel ao concept art oficial:
    - Copa arredondada / cônica alta em Azul Royal com fita dourada e topo vincado
    - Aba assimétrica viva (NUNCA plana/quadrada): aba direita e frontal suavemente caídas,
      e aba lateral esquerda dobrada acentuadamente para cima (cocked brim) com debrum de ouro
    - Broche dourado floral / Flor-de-lis prendendo a aba dobrada
    - Majestosa e volumosa pluma branca de avestruz que se ergue alta e arqueia graciosamente para trás
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py

    # 1. Volume da cabeça, nuca e cabelo castanho-acobreado (Auburn)
    # Rosto limpo (sem olhos ou boca de cubo saltados)
    hair_col = P["hair"]
    hair_dark = (135, 52, 28)
    skin_col = P["skin"]

    # Cabelo lateral e traseiro sob o chapéu
    mk.cbox(c, bx - fx * 0.02, by - fy * 0.02, hz + 0.03, 0.12, 0.12, 0.08, hair_col, outline=False)
    # Franja estilosa e mechas frontais emoldurando o rosto
    mk.cbox(c, bx + fx * 0.055 - px * 0.03, by + fy * 0.055 - py * 0.03, hz + 0.045, 0.045, 0.045, 0.035, hair_col, outline=False)
    mk.cbox(c, bx + fx * 0.055 + px * 0.03, by + fy * 0.055 + py * 0.03, hz + 0.045, 0.04, 0.04, 0.035, hair_col, outline=False)

    # Trança elegante descendo suavemente sobre o ombro
    trail, amp, freq = mk.motion(c, 0.06)
    braid_root = (bx - px * 0.06 - fx * 0.03, by - py * 0.06 - fy * 0.03, hz + 0.02)
    mk.panels(c, braid_root, 5, 0.05, 0.04, 0.038, (hair_col, hair_dark, hair_col, hair_dark, hair_col),
              phase=1.0, up=(fx, fy, 0.0), trail=trail, amp=amp, freq=freq, flare=-0.003)
    # Fita azul amarrando o final da trança
    braid_tip = (braid_root[0] - trail[0] * 0.6, braid_root[1] - trail[1] * 0.6, braid_root[2] - 0.14)
    mk.cbox(c, braid_tip[0], braid_tip[1], braid_tip[2], 0.035, 0.035, 0.022, P["blue"], outline=False)

    # =========================================================================
    # CHAPÉU CAVALIER DE MOSQUEIRO (SEVENTEENTH CENTURY FLAMBOYANT HAT)
    # =========================================================================
    hat_blue = P["hat"]
    hat_dark = P["blue_dark"]
    gold = P["gold"]

    # -------------------------------------------------------------------------
    # A. COPA DO CHAPÉU (CROWN): Alta, afunilada e arredondada (NÃO plana)
    # -------------------------------------------------------------------------
    # Base da copa que se assenta na cabeça
    mk.cbox(c, bx - fx * 0.015, by - fy * 0.015, hz + 0.075, 0.13, 0.13, 0.045, hat_blue)
    # Faixa dourada elegante de couro/tecido (hatband) circulando a copa
    mk.cbox(c, bx - fx * 0.015, by - fy * 0.015, hz + 0.10, 0.138, 0.138, 0.022, gold, texture="gold", outline=False)
    # Corpo médio da copa afunilando
    mk.cbox(c, bx - fx * 0.018, by - fy * 0.018, hz + 0.12, 0.12, 0.12, 0.045, hat_blue)
    # Topo arredondado da copa
    mk.cbox(c, bx - fx * 0.020, by - fy * 0.020, hz + 0.16, 0.105, 0.105, 0.035, hat_blue)
    # Vinco/fenda sutil no topo do feltro (creased crown)
    mk.cbox(c, bx - fx * 0.020, by - fy * 0.020, hz + 0.19, 0.075, 0.065, 0.015, hat_dark, outline=False)

    # -------------------------------------------------------------------------
    # B. ABA ASSIMÉTRICA CAVALIER (BRIM): Fluida, orgânica e com curvaturas 3D
    # -------------------------------------------------------------------------
    # 1. Base interna circular da aba conectada à copa
    mk.cbox(c, bx - fx * 0.01, by - fy * 0.01, hz + 0.07, 0.155, 0.155, 0.02, hat_blue, outline=False)

    # 2. Aba Frontal: projeta-se à frente ao longo de (fx, fy) e desce em declive suave
    front_dir = mk.norm((fx, fy, -0.22))
    mk.obox(c, (bx + fx * 0.055, by + fy * 0.055, hz + 0.072), front_dir, 0.075, 0.15, 0.02, hat_blue)

    # 3. Aba Lateral Direita: estende-se sobre o ombro direito (-px, -py) e cai suavemente
    right_dir = mk.norm((-px, -py, -0.28))
    mk.obox(c, (bx - px * 0.055, by - py * 0.055, hz + 0.072), right_dir, 0.075, 0.14, 0.02, hat_blue)

    # 4. Aba Traseira: curva suave sobre a nuca
    back_dir = mk.norm((-fx, -fy, -0.15))
    mk.obox(c, (bx - fx * 0.055, by - fy * 0.055, hz + 0.072), back_dir, 0.065, 0.14, 0.02, hat_blue)

    # 5. ABA LATERAL ESQUERDA DOBRADA PARA CIMA (COCKED / TURNED-UP BRIM):
    # No concept art oficial, a aba do lado esquerdo sobe na vertical encostada na copa!
    cocked_dir = mk.norm((px * 0.15, py * 0.15, 0.98))
    cocked_origin = (bx + px * 0.065 - fx * 0.01, by + py * 0.065 - fy * 0.01, hz + 0.075)
    mk.obox(c, cocked_origin, cocked_dir, 0.125, 0.14, 0.024, hat_blue, up=(-fx, -fy, 0.0))

    # Debrum dourado bordado no topo da aba dobrada
    trim_dir = mk.norm((fx, fy, 0.0))
    trim_start = (bx + px * 0.082 - fx * 0.07, by + py * 0.082 - fy * 0.07, hz + 0.195)
    mk.obox(c, trim_start, trim_dir, 0.13, 0.018, 0.016, gold, texture="gold", outline=False)

    # 6. Broche / Fivela de Ouro (Flor-de-lis) prendendo a aba dobrada
    mk.cbox(c, bx + px * 0.088 + fx * 0.01, by + py * 0.088 + fy * 0.01, hz + 0.125, 0.035, 0.035, 0.035, gold, texture="gold", outline=True)

    # -------------------------------------------------------------------------
    # C. MAJESTOSA PLUMA DE AVESTRUZ BRANCA (SWEEPING OSTRICH PLUME)
    # -------------------------------------------------------------------------
    plume_white = (252, 252, 255)
    plume_shade = (218, 226, 238)
    plume_core  = (195, 205, 220)

    # Raiz da pluma saindo de trás do broche dourado
    mk.cbox(c, bx + px * 0.075 + fx * 0.01, by + py * 0.075 + fy * 0.01, hz + 0.145, 0.045, 0.045, 0.05, plume_white, outline=False)
    # Haste subindo além da copa
    mk.cbox(c, bx + px * 0.065 - fx * 0.02, by + py * 0.065 - fy * 0.02, hz + 0.190, 0.055, 0.055, 0.06, plume_white, outline=False)
    # Arco alto ultrapassando a altura do chapéu
    mk.cbox(c, bx + px * 0.040 - fx * 0.05, by + py * 0.040 - fy * 0.05, hz + 0.240, 0.065, 0.065, 0.06, plume_white, outline=False)
    # Ponto mais alto da pluma (crista farta)
    mk.cbox(c, bx + px * 0.010 - fx * 0.09, by + py * 0.010 - fy * 0.09, hz + 0.270, 0.075, 0.075, 0.055, plume_white, outline=False)
    # Franjas fofas superiores dando aspecto plumoso
    mk.cbox(c, bx + px * 0.015 - fx * 0.08, by + py * 0.015 - fy * 0.08, hz + 0.295, 0.050, 0.050, 0.030, plume_white, outline=False)
    mk.cbox(c, bx + px * 0.020 - fx * 0.07, by + py * 0.020 - fy * 0.07, hz + 0.250, 0.045, 0.045, 0.045, plume_shade, outline=False)
    # Cascata descendo pelas costas
    mk.cbox(c, bx - px * 0.02 - fx * 0.13 + trail[0] * 0.5, by - py * 0.02 - fy * 0.13 + trail[1] * 0.5, hz + 0.235, 0.070, 0.070, 0.050, plume_white, outline=False)
    mk.cbox(c, bx - px * 0.05 - fx * 0.17 + trail[0], by - py * 0.05 - fy * 0.17 + trail[1], hz + 0.185, 0.060, 0.060, 0.045, plume_shade, outline=False)
    # Ponta da pluma esvoaçando graciosa atrás da nuca
    mk.cbox(c, bx - px * 0.08 - fx * 0.21 + trail[0] * 1.4, by - py * 0.08 - fy * 0.21 + trail[1] * 1.4, hz + 0.135, 0.048, 0.048, 0.040, plume_white, outline=False)
    mk.cbox(c, bx - px * 0.10 - fx * 0.24 + trail[0] * 1.8, by - py * 0.10 - fy * 0.24 + trail[1] * 1.8, hz + 0.098, 0.035, 0.035, 0.030, plume_core, outline=False)


def _rapier(c, hand, d, length):
    P = pal()
    mk.obox(c, mk.add(hand, d, -0.1), d, 0.12, 0.034, 0.034, P["grip"])
    mk.obox(c, mk.add(hand, d, -0.11), d, 0.02, 0.046, 0.046, P["gold"], outline=False)
    mk.cbox(c, hand[0] + d[0] * 0.04 - 0.045, hand[1] + d[1] * 0.04 - 0.045, hand[2] + d[2] * 0.04 - 0.03, 0.09, 0.09, 0.06, P["gold"])  # guarda em concha
    mk.obox(c, mk.add(hand, d, 0.04), d, length, 0.028, 0.026, P["steel"])
    mk.obox(c, mk.add(hand, d, 0.05), d, length - 0.02, 0.012, 0.028, P["edge"], outline=False)
    return mk.add(hand, d, 0.04 + length)


def draw_front(c, arm_l, arm_r):
    """Florete (en garde, baixo na caminhada, estocada no fleche) e a capa girando no CAPE_FLOURISH com o chute."""
    P = pal()
    hand = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    if _flourishing(c):
        t = max(0.0, min(1.0, 1.0 - c.state_timer / 0.16))
        a = t * math.pi * 2.2
        cf = (c.fx * math.cos(a) + c.px * math.sin(a), c.fy * math.cos(a) + c.py * math.sin(a))
        mk.obox(c, (c.base_x + cf[0] * 0.2, c.base_y + cf[1] * 0.2, c.torso_z + 0.06), (cf[0], cf[1], -0.15), 0.5, 0.22, 0.04, P["cape"], up=(0.0, 0.0, 1.0))
        mk.obox(c, (c.base_x + cf[0] * 0.2, c.base_y + cf[1] * 0.2, c.torso_z + 0.06), (cf[0], cf[1], -0.15), 0.5, 0.22, 0.012, P["gold"], up=(0.0, 0.0, 1.0), outline=False)
        kick = c.pelvis_z - 0.12
        mk.obox(c, (c.base_x + c.fx * 0.18, c.base_y + c.fy * 0.18, kick), (c.fx, c.fy, 0.1), 0.38, 0.08, 0.08, P["pants"])
        mk.obox(c, (c.base_x + c.fx * 0.36, c.base_y + c.fy * 0.36, kick + 0.02), (c.fx, c.fy, 0.1), 0.14, 0.09, 0.09, P["boot"])
    if c.is_melee:
        info = calc_blade_slash_3d("musketeer", "ATTACK", c.atk_progress, c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py)
        d, length = mk.norm(tuple(info["dir"])), 0.78
        tip = _rapier(c, hand, d, length)
        if c.atk_progress >= 0.25:
            for j in range(1, 4):
                back = mk.add(hand, d, -0.12 * j)
                fade = 1.0 - j / 4.0
                side = (c.px * 0.04, c.py * 0.04, 0.0)
                a0, a1 = mk.add(back, d, 0.35), mk.add(back, d, length + 0.1)
                mk.band(c, (a0, a1, mk.add(a1, side, 1.0), mk.add(a0, side, 1.0)), P["aura"] + (int(190 * fade),))
        return
    if c.is_moving:
        d = mk.norm((c.fx * 0.3, c.fy * 0.3, -0.75))
    else:
        d = mk.norm((c.fx * 0.82 + c.px * 0.1, c.fy * 0.82 + c.py * 0.1, 0.08))
    _rapier(c, hand, d, 0.72 if not c.is_moving else 0.68)
