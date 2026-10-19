"""
Valerius, o Necromante Prussiano (Ciclo 4):
- Aristocrata e ocultista prussiano da era Bakumatsu, de linhagem nobre e tez cadavérica gélida.
- Sobretudo militar gótico (frock coat) azul-noite/preto com dragonas prateadas e botões ornamentados.
- Colete de brocado escuro com cravat de seda branca pura alto no pescoço.
- Calças retas escuras em malha 3D contínua entrando em botas de montaria pretas lustrosas.
- Cabelos platinados grisalhos penteados para trás com mechas angulares; olhos marciais gélidos cor de aço.
- Foice Fúnebre de Duelo (Funeral Scythe):
  - Haste pesada de ferro forjado e ébano com engastes prateados (~1.45m).
  - Lâmina recurva gótica de aço escuro com fio de corte prateado acetinado e entalhes fúnebres.
  - Ordenação dinâmica Painter's Algorithm para oclusão 360° com as costas do sobretudo.
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
from src.isometric.voxel_rig import calc_blade_slash_3d

SKIN = (235, 230, 228)
SKIN_SHADOW = (195, 188, 190)

PALETTE = {
    # Sobretudo Militar Gótico / Frock Coat Prussiano
    "coat": (24, 26, 36),
    "torso": (24, 26, 36),
    "coat_dark": (14, 15, 22),
    "coat_light": (42, 46, 62),
    "coat_trim": (195, 205, 220), # Bordado prateado
    "epaulet": (210, 218, 230),   # Dragonas prateadas de oficial
    "epaulet_gold": (180, 190, 205),
    "waistcoat": (32, 34, 44),
    "silver_button": (225, 232, 245),

    # Cravat e Colarinho Alto
    "cravat": (245, 245, 250),
    "cravat_dark": (200, 205, 215),
    "neck": (245, 245, 250),     # Colarinho alto embutido na gola

    # Cabelos Platinados e Rosto
    "hair": (218, 222, 230),
    "hair_dark": (165, 172, 182),
    "hair_light": (245, 248, 255),
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "eye": (130, 165, 195),
    "brow": (160, 168, 178),
    "lip": (175, 135, 138),

    # Pernas, Calças e Botas de Cavalaria
    "pants": (28, 30, 38),
    "pants_dark": (18, 20, 26),
    "boot": (20, 22, 26),
    "boot_cuff": (38, 40, 48),
    "boot_sole": (12, 14, 16),
    "glove": (26, 28, 34),

    # Foice Fúnebre (Funeral Scythe)
    "scythe_pole": (35, 38, 42),
    "pole_silver": (185, 195, 210),
    "scythe_blade": (155, 170, 190),
    "scythe_edge": (245, 250, 255),
    "scythe_dark": (95, 105, 120),
    "scythe_crest": (205, 215, 230),

    # Brilho Espectral / Necromancia
    "spectral_aura": (65, 230, 170),
    "spectral_core": (200, 255, 235),
}

MATERIALS = {
    "coat": "velvet",
    "coat_dark": "velvet",
    "waistcoat": "brocade",
    "cravat": "silk",
    "glove": "leather",
    "boot": "leather",
    "boot_cuff": "leather",
    "scythe_pole": "wood",
    "scythe_blade": "steel",
    "scythe_edge": "steel",
    "epaulet": "steel",
    "epaulet_gold": "gold",
    "coat_trim": "steel",
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Animação da Foice Fúnebre
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Postura gótica cerimonial de Valerius:
    - Mão direita segura o fuste da foice na altura do peito, a lâmina curva arqueada sobre o ombro direito.
    - Mão esquerda levemente apoiada na cintura ou segurando o cabo inferior.
    """
    breathe = math.sin(c.walk_timer * 2.4) * 0.008
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    right = (
        bx + fx * 0.12 - px * 0.08,
        by + fy * 0.12 - py * 0.08,
        tz + 0.18
    )
    left = (
        bx + fx * 0.10 + px * 0.14,
        by + fy * 0.10 + py * 0.14,
        tz + 0.06
    )
    return left, right


def walk_arms(c):
    """Passada austera e imponente de oficial prussiano."""
    swing = math.sin(c.walk_timer * 8.0) * 0.07
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    right = (
        bx + fx * (0.14 + swing * 0.04) - px * 0.08,
        by + fy * (0.14 + swing * 0.04) - py * 0.08,
        tz + 0.18 + abs(swing) * 0.015
    )
    left = (
        bx + fx * (0.10 - swing * 0.08) + px * 0.14,
        by + fy * (0.10 - swing * 0.08) + py * 0.14,
        tz + 0.06
    )
    return left, right


def attack_arms(c):
    """
    Ceifada Fúnebre Ampla (Soul Reap):
    - Movimento em arco amplo de ceifador a duas mãos, cobrindo o plano frontal com corte devastador.
    """
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    prog = c.atk_progress if c.atk_progress is not None else 0.0

    # 3 Fases: Antecipação (puxa foice atrás) -> Ceifada (arco rasante) -> Retorno fluido
    if prog < 0.28:
        # Antecipação: ergue a foice sobre o ombro direito para trás
        t = prog / 0.28
        right = (bx - fx * 0.10 - px * 0.18 * t, by - fy * 0.10 - py * 0.18 * t, tz + 0.26 + t * 0.08)
        left = (bx + fx * 0.04 - px * 0.06, by + fy * 0.04 - py * 0.06, tz + 0.14)
    elif prog < 0.72:
        # Impacto do corte: avança ceifando em arco horizontal rasante
        t = (prog - 0.28) / 0.44
        ang = -0.8 + t * 1.9
        c_cos = math.cos(ang)
        c_sin = math.sin(ang)
        sweep_x = fx * c_cos + px * c_sin
        sweep_y = fy * c_cos + py * c_sin
        right = (bx + sweep_x * 0.32, by + sweep_y * 0.32, tz + 0.16 - t * 0.04)
        left = (bx + sweep_x * 0.16 - px * 0.08, by + sweep_y * 0.16 - py * 0.08, tz + 0.12)
    else:
        # Recuperação austera
        t = (prog - 0.72) / 0.28
        right = (bx + fx * 0.18 - px * 0.08, by + fy * 0.18 - py * 0.08, tz + 0.18)
        left = (bx + fx * 0.10 + px * 0.10, by + fy * 0.10 + py * 0.10, tz + 0.08)

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
    Renderiza os elementos nas costas e armas/braços quando o personagem está de costas para a câmera:
    - Abas do sobretudo militar prussiano (frock coat tails) em fita 3D esvoaçante.
    - Ordenação de profundidade: foice fúnebre quando voltada para o fundo.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    d_torso = mk.depth(c, bx, by)

    # 1. Abas do Sobretudo (Frock Coat Tails) caindo pelas costas em fita contínua 3D
    trail, amp, freq = mk.motion(c, 0.04)
    o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.6, trail, (-fx, -fy), amp=amp * 0.7, freq=freq)
    p0 = (bx - fx * 0.09, by - fy * 0.09, tz + 0.08)
    p1 = (bx - fx * 0.12 + o1[0], by - fy * 0.12 + o1[1], tz - 0.06 + o1[2])
    p2 = (bx - fx * 0.14 + o2[0], by - fy * 0.14 + o2[1], tz - 0.20 + o2[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1, p2],
        widths=[0.24, 0.26, 0.28],
        depth_thick=0.030,
        colors=[P["coat"], P["coat_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # 2. Ordenação da Foice Fúnebre se as mãos estiverem atrás do tronco
    hand_l, hand_r = _current_hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_scythe(c, hand_l, hand_r)


def draw_legs(c):
    """
    Pernas masculinas em calças escuras justas de montaria em malha contínua 3D,
    entrando diretamente em botas de cavalaria prussianas de cano alto.
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
        cuff_pos = (sh[0] + o1[0] * 0.1, sh[1] + o1[1] * 0.1, sh[2] + 0.06)
        ankle = (foot[0] + o2[0] * 0.15, foot[1] + o2[1] * 0.15, foot[2] + 0.03)

        # Calça militar escura em malha contínua 3D conectada sem degraus ao topo da bota
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos],
            widths=[0.115, 0.105, 0.095],
            depth_thick=0.095,
            colors=[P["pants"], P["pants_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Bota de cavalaria de couro preto lustroso
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[cuff_pos, ankle],
            widths=[0.092, 0.078],
            depth_thick=0.078,
            colors=[P["boot_cuff"], P["boot"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Pé com sola de bota
        flen, fwidth = 0.13, 0.070
        mk.obox(c, (foot[0] + c.fx * 0.01, foot[1] + c.fy * 0.01, foot[2]), (c.fx, c.fy, 0.0), flen, fwidth, 0.040, P["boot"])
        mk.obox(c, (foot[0] + c.fx * 0.01, foot[1] + c.fy * 0.01, foot[2] - 0.01), (c.fx, c.fy, 0.0), flen + 0.01, fwidth + 0.005, 0.015, P["boot_sole"], outline=False)


def draw_obi(c):
    """Cinturão de oficial com fivela prateada e abas fechadas do colete."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    # Cinturão preto de couro
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.01, c.pelvis_w * 0.72, 0.065, P["coat_dark"])
    # Fivela prateada central
    mk.obox(c, (bx + fx * 0.085, by + fy * 0.085, z + 0.010), (0.0, 0.0, 1.0), 0.040, 0.030, 0.015, P["coat_trim"], up=(fx, fy, 0.0), outline=False)


def draw_torso(c):
    """
    Tronco de oficial prussiano:
    - Cravat de seda branca pura franzido no pescoço.
    - Lapelas cruzadas do sobreturo com botões duplos prateados.
    - Dragonas prateadas com franjas nos ombros (up-vector alinhado para evitar colapso de matriz).
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    front = 0.092

    if mk.depth(c, fx, fy) > -0.05:
        # Cravat de seda branca pura franzido sob a gola
        mk.obox(c, (bx + fx * (front - 0.005), by + fy * (front - 0.005), tz + 0.17), (0.0, 0.0, 1.0), 0.075, 0.055, 0.025, P["cravat"], up=(fx, fy, 0.0), outline=False)
        mk.obox(c, (bx + fx * (front + 0.008), by + fy * (front + 0.008), tz + 0.13), (0.0, 0.0, 1.0), 0.055, 0.040, 0.022, P["cravat_dark"], up=(fx, fy, 0.0), outline=False)

        # Lapelas do sobretudo abertas em V mostrando o colete
        for s in (-1.0, 1.0):
            lapel_pos = (bx + fx * front + px * 0.045 * s, by + fy * front + py * 0.045 * s, tz + 0.15)
            mk.obox(c, lapel_pos, (0.0, 0.0, 1.0), 0.11, 0.035, 0.018, P["coat_trim"], up=(fx, fy, 0.0), outline=False)
            # Botões prateados duplos
            mk.obox(c, (bx + fx * (front + 0.004) + px * 0.035 * s, by + fy * (front + 0.004) + py * 0.035 * s, tz + 0.08), (0.0, 0.0, 1.0), 0.020, 0.018, 0.010, P["silver_button"], up=(fx, fy, 0.0), outline=False)

    # Dragonas Prateadas de Oficial nos Ombros (com up-vector fx, fy explicitado para estabilidade 3D)
    for s in (-1.0, 1.0):
        sh_pos = (bx + px * c.sh_span * s, by + py * c.sh_span * s, tz + 0.22)
        mk.obox(c, sh_pos, (px * s, py * s, -0.2), 0.075, 0.065, 0.028, P["epaulet"], up=(fx, fy, 0.0), outline=True)
        # Franjas prateadas pendendo da dragona
        mk.obox(c, (sh_pos[0] + px * 0.025 * s, sh_pos[1] + py * 0.025 * s, sh_pos[2] - 0.025), (0.0, 0.0, -1.0), 0.040, 0.055, 0.015, P["coat_trim"], up=(fx, fy, 0.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço articulado com manga militar azul-noite e luva de couro escuro."""
    P = pal()
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["coat"],
        sleeve_to=0.68,
        w=0.052,
        bend=0.025,
        glove=P["glove"]
    )


def draw_head(c):
    """
    Cabeça e Cabelos Platinados de Valerius:
    - Cabelos grisalhos platinados penteados para trás com mechas esculpidas.
    - Feições marciais gélidas projetadas via draw_portrait_face_3d.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # Cabelo platinado penteado para trás em camadas 3D
    cran_top = (bx - fx * 0.010, by - fy * 0.010, hz + 0.172)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, hz + 0.140), cran_top,
        w_start=hw * 0.96, h_start=hw * 0.96,
        w_end=hw * 0.72, h_end=hw * 0.72,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Topete platinado levemente arqueado na fronte
    mk.obox(c, (bx + fx * 0.04, by + fy * 0.04, hz + 0.155), (fx, fy, 0.3), 0.050, hw * 0.65, 0.028, P["hair_light"], up=(-px, -py, 0.0), outline=False)

    # Mechas laterais temporais
    for s in (-1.0, 1.0):
        is_behind = mk.depth(c, px * s, py * s) < 0
        if not is_behind:
            side_pos = (bx + px * hw * 0.44 * s, by + py * hw * 0.44 * s, hz + 0.10)
            mk.obox(c, side_pos, (-fx * 0.4, -fy * 0.4, -0.8), 0.065, 0.022, 0.020, P["hair"], up=(fx, fy, 0.0), outline=False)


def draw_front(c, hand_l, hand_r):
    """Renderiza a foice fúnebre à frente se as mãos estiverem no plano frontal."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_scythe(c, hand_l, hand_r)


# ---------------------------------------------------------------------------------------------------------------------
# Renderização da Foice Fúnebre e Efeitos de Ceifador
# ---------------------------------------------------------------------------------------------------------------------

def _render_scythe(c, hand_l, hand_r):
    """
    Renderiza a Foice Fúnebre (Funeral Scythe) 3D:
    - Haste de ferro escuro entalhado (~1.45m).
    - Topo com lâmina curva gótica e contra-ponta em espinho de ferro.
    - Rastro espectral verde-esmeralda em golpes letais.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    if c.is_melee and c.atk_progress is not None:
        prog = c.atk_progress
        # Durante o ataque, a foice gira na trajetória de corte
        r_x, r_y, r_z = hand_r
        l_x, l_y, l_z = hand_l

        # Vetor do cabo ligando as mãos até a lâmina
        pole_dx = r_x - l_x
        pole_dy = r_y - l_y
        pole_dz = r_z - l_z
        plen = math.sqrt(pole_dx * pole_dx + pole_dy * pole_dy + pole_dz * pole_dz) or 1.0
        pole_dx /= plen
        pole_dy /= plen
        pole_dz /= plen

        # Base do cabo e cabeça da foice
        pole_len = 1.45
        head_x = r_x + pole_dx * 0.55
        head_y = r_y + pole_dy * 0.55
        head_z = r_z + pole_dz * 0.55

        tail_x = l_x - pole_dx * 0.65
        tail_y = l_y - pole_dy * 0.65
        tail_z = l_z - pole_dz * 0.65

        # 1. Haste de Ferro Forjado
        mk.obox(c, (tail_x, tail_y, tail_z), (pole_dx, pole_dy, pole_dz), pole_len, 0.038, 0.038, P["scythe_pole"], texture="wood")
        # Anel de reforço prateado
        mk.obox(c, (head_x, head_y, head_z), (pole_dx, pole_dy, pole_dz), 0.05, 0.052, 0.052, P["pole_silver"], outline=False)

        # 2. Lâmina Curva Gótica da Foice
        # A lâmina curva projeta-se em ângulo perpendicular ao cabo
        blade_dir_x = fx * 0.8 - px * 0.2
        blade_dir_y = fy * 0.8 - py * 0.2
        blade_dir_z = -0.35

        # Corpo da lâmina
        mk.obox(c, (head_x, head_y, head_z), (blade_dir_x, blade_dir_y, blade_dir_z), 0.58, 0.065, 0.024, P["scythe_blade"], outline=True)
        # Fio de corte prateado afiado
        mk.obox(c, (head_x + blade_dir_x * 0.04, head_y + blade_dir_y * 0.04, head_z + blade_dir_z * 0.04), (blade_dir_x, blade_dir_y, blade_dir_z), 0.55, 0.025, 0.012, P["scythe_edge"], outline=False)

        # Rastro espectral nos frames rápidos do golpe
        if 0.30 <= prog <= 0.70:
            glow_x = head_x + blade_dir_x * 0.30
            glow_y = head_y + blade_dir_y * 0.30
            glow_z = head_z + blade_dir_z * 0.30
            mk.cbox(c, glow_x, glow_y, glow_z, 0.18, 0.18, 0.18, P["spectral_aura"], outline=False)
            mk.cbox(c, glow_x, glow_y, glow_z, 0.10, 0.10, 0.10, P["spectral_core"], outline=False)

    else:
        # Posição de repouso / caminhada: foice na mão direita com lâmina arqueada atrás do ombro
        r_x, r_y, r_z = hand_r
        pole_dx = fx * 0.2 - px * 0.3
        pole_dy = fy * 0.2 - py * 0.3
        pole_dz = 0.94
        plen = math.sqrt(pole_dx * pole_dx + pole_dy * pole_dy + pole_dz * pole_dz) or 1.0
        pole_dx /= plen
        pole_dy /= plen
        pole_dz /= plen

        pole_bottom = (r_x - pole_dx * 0.75, r_y - pole_dy * 0.75, r_z - pole_dz * 0.75)
        head_pos = (r_x + pole_dx * 0.65, r_y + pole_dy * 0.65, r_z + pole_dz * 0.65)

        # Haste
        mk.obox(c, pole_bottom, (pole_dx, pole_dy, pole_dz), 1.40, 0.036, 0.036, P["scythe_pole"], texture="wood")
        mk.obox(c, head_pos, (pole_dx, pole_dy, pole_dz), 0.06, 0.050, 0.050, P["pole_silver"], outline=False)

        # Lâmina recurva estendendo-se para trás/lado
        b_dx = -fx * 0.7 - px * 0.6
        b_dy = -fy * 0.7 - py * 0.6
        b_dz = -0.32
        mk.obox(c, head_pos, (b_dx, b_dy, b_dz), 0.62, 0.068, 0.024, P["scythe_blade"], outline=True)
        mk.obox(c, head_pos, (b_dx, b_dy, b_dz), 0.60, 0.025, 0.012, P["scythe_edge"], outline=False)
