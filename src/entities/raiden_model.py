"""
Raiden, o Yokozuna dos Trovões (Ciclo 6):
- Lendário grande campeão Yokozuna em trânsito entre torneios imperiais.
- Manto cerimonial de seda vermelho escuro (Haori) com bordados dourados e brasões de clã (Mon) cobrindo completamente os ombros maciços, com abas frontais, mangas amplas (draw_sleeves) e grande brasão dorsal visíveis em todos os ângulos 360°.
- Físico colossal e imponente de rikishi: peitoral e abdômen pesados, ombros largos e braços maciços (draw_arm) com bíceps musculosos e palmas abertas para empurrões Tsuppari.
- Mawashi tradicional de seda pesada índigo-carvão com cordões rituais pendentes (Sagari) na parte frontal e nó rígido (Tate-mitsu) nas costas.
- Cabeça esculpida com maxilar pesado, olhar estóico marcial de Yokozuna no tachiai e coque tradicional Chonmage / Oicho-mage preso com cordão de papel ritual (Motoyui).
- Ordenação dinâmica 3D (Painter's Algorithm) rigorosa para oclusão 360° perfeita.
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

SKIN = (226, 180, 148)
SKIN_SHADOW = (184, 138, 108)

PALETTE = {
    # Manto Cerimonial de Yokozuna (Haori de Trânsito - Vermelho Escuro & Dourado Nobre)
    "haori": (136, 24, 32),          # Vermelho escuro nobre / seda carmesim
    "haori_dark": (88, 14, 20),       # Sombra bordô profunda
    "haori_light": (172, 38, 48),     # Realce de seda vermelho escuro
    "haori_gold": (232, 192, 70),     # Bordados e galões dourados
    "haori_lining": (58, 10, 15),     # Forro interno carmesim profundo
    "torso": (136, 24, 32),

    # Mawashi de Seda e Cordões Sagari
    "mawashi": (28, 32, 42),
    "mawashi_dark": (18, 20, 28),
    "mawashi_light": (45, 52, 68),
    "belt": (28, 32, 42),
    "sagari": (225, 185, 70),
    "sagari_red": (175, 36, 42),
    "knot": (24, 28, 38),

    # Cabelos, Chonmage e Cordão Motoyui
    "hair": (20, 18, 22),
    "hair_dark": (12, 10, 14),
    "motoyui": (242, 238, 225),

    # Anatomia Rikishi
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "neck": SKIN,
    "eye": (72, 45, 26),
    "brow": (22, 18, 16),
    "lip": (168, 112, 98),

    # Efeitos de Palma Tsuppari e Impacto Sísmico
    "palm_aura": (255, 225, 140),
    "palm_core": (255, 250, 220),
    "shock_dust": (215, 192, 158),
}

MATERIALS = {
    "haori": "silk",
    "haori_dark": "silk",
    "haori_gold": "gold",
    "haori_lining": "silk",
    "mawashi": "silk",
    "mawashi_dark": "silk",
    "sagari": "gold",
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Animação de Combate Rikishi
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Postura Tachiai / Shikiri de Sumô:
    - Físico rebaixado, braços pesados em arco frontal com mãos abertas voltadas para frente.
    - Palmas prontas para interceptação ou rajada de empurrões Tsuppari.
    """
    breathe = math.sin(c.walk_timer * 2.2) * 0.012
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    pose = c.extra_props.get("pose") if c.extra_props else None

    if pose == "sumo_shikiri":
        # Punhos tocando o solo na preparação inicial do combate
        left = (bx + fx * 0.16 + px * 0.14, by + fy * 0.16 + py * 0.14, c.base_z + 0.15)
        right = (bx + fx * 0.16 - px * 0.14, by + fy * 0.16 - py * 0.14, c.base_z + 0.15)
        return left, right

    if pose == "sumo_yokozuna_dohyo_iri":
        # Pose cerimonial de entrada no anel com os dois braços abertos horizontalmente
        left = (bx + px * 0.32, by + py * 0.32, tz + 0.22)
        right = (bx - px * 0.32, by - py * 0.32, tz + 0.22)
        return left, right

    # Guarda neutra: palmas abertas para frente, posicionadas à frente do peito
    left = (bx + fx * 0.20 + px * 0.15, by + fy * 0.20 + py * 0.15, tz + 0.12)
    right = (bx + fx * 0.24 - px * 0.10, by + fy * 0.24 - py * 0.10, tz + 0.14)
    return left, right


def attack_arms(c):
    """
    Golpe de Palma Tsuppari Devastador:
    - O braço de ataque estende a palma espalmada em linha reta com peso corporal completo.
    - O outro braço recolhe junto à costela para gerar o contragolpe rítmico.
    """
    p = c.atk_progress if c.atk_progress is not None else 0.0
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    thrust = math.sin(p * math.pi) * 0.42

    # Palma direita em investida frontal com impacto de massa
    right = (bx + fx * (0.26 + thrust) - px * 0.04,
             by + fy * (0.26 + thrust) - py * 0.04,
             tz + 0.14)
    # Mão esquerda de apoio protegendo o peito
    left = (bx + fx * 0.14 + px * 0.16,
            by + fy * 0.14 + py * 0.16,
            tz + 0.10)
    return left, right


def _current_hands(c):
    if c.is_melee and c.atk_progress is not None:
        return attack_arms(c)
    return idle_arms(c)


# ---------------------------------------------------------------------------------------------------------------------
# Renderização 3D das Partes do Corpo
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Elementos renderizados atrás do corpo quando vistos do plano frontal:
    - Manto Haori cerimonial de Yokozuna drapeado pelas costas (quando de frente para a câmera).
    - Nó traseiro rígido do mawashi (Tate-mitsu).
    - Mãos e impactos de palma se as mãos estiverem atrás do tronco em relação à câmera.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    d_torso = mk.depth(c, bx, by)

    # 1. Manto Haori Cerimonial de Seda Vermelha escura nas costas (apenas quando de frente)
    if mk.depth(c, fx, fy) > -0.05:
        _render_haori_back(c, P)

    # 2. Nó traseiro rígido do Mawashi (Tate-mitsu)
    knot_pos = (bx - fx * 0.12, by - fy * 0.12, c.pelvis_z + 0.06)
    mk.obox(c, knot_pos, (-fx, -fy, 0.0), 0.080, 0.110, 0.075, P["knot"], up=(0.0, 0.0, 1.0), outline=True)

    # 3. Se as mãos estiverem atrás do tronco em relação à câmera, desenha o impacto de palmas aqui
    hl, hr = _current_hands(c)
    w_mid = ((hl[0] + hr[0]) * 0.5, (hl[1] + hr[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_palm_effects(c, hr)


def _render_haori_back(c, P):
    """Desenha o manto cerimonial cobrindo as costas com bordados dourados e brasão Mon."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.035)
    o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.6, trail, (px, py), amp=amp * 0.5, freq=freq)

    # Âncoras do caimento dorsal ajustadas rentes ao dorso do rikishi (sem flutuar como capa descolada)
    p_neck = (bx - fx * 0.04, by - fy * 0.04, tz + 0.24)
    p_mid = (bx - fx * 0.07 + o1[0], by - fy * 0.07 + o1[1], tz + 0.06 + o1[2])
    p_hem = (bx - fx * 0.09 + o2[0], by - fy * 0.09 + o2[1], tz - 0.18 + o2[2])

    # Fita de seda vermelho escuro das costas do Haori
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p_neck, p_mid, p_hem],
        widths=[0.44, 0.48, 0.52],
        depth_thick=0.045,
        colors=[P["haori"], P["haori_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Barra dourada na bainha inferior do Haori
    p_gold_hem = (p_hem[0], p_hem[1], p_hem[2] + 0.018)
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p_gold_hem, p_hem],
        widths=[0.52, 0.52],
        depth_thick=0.025,
        colors=[P["haori_gold"], P["haori_gold"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Grande Brasão Mon circular dourado central nas costas (emblema imperial de clã)
    mk.obox(c, p_mid, (-fx, -fy, 0.0), 0.018, 0.110, 0.110, P["haori_gold"], up=(0.0, 0.0, 1.0), outline=False)
    mk.obox(c, p_mid, (-fx, -fy, 0.0), 0.022, 0.068, 0.068, P["haori_dark"], up=(0.0, 0.0, 1.0), outline=False)


def draw_legs(c):
    """
    Pernas monumentais e maciças de Rikishi:
    - Coxas e panturrilhas pesadas esculpidas em malha 3D contínua sem quebras articulares.
    - Pés descalços pesados com sola sólida ancorada ao dohyo.
    """
    P = pal()
    trail, amp, freq = mk.motion(c, 0.030)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.70 * sign, trail, (c.px, c.py), amp=amp * 0.3, freq=freq)

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.15, sh[1] + o1[1] * 0.15, sh[2] + 0.14)
        cuff_pos = (sh[0] + o1[0] * 0.10, sh[1] + o1[1] * 0.10, sh[2] + 0.06)
        ankle = (foot[0] + o2[0] * 0.10, foot[1] + o2[1] * 0.10, foot[2] + 0.02)

        # Coxa e canela maciças de Rikishi (músculo puro)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos, ankle],
            widths=[0.145, 0.138, 0.120, 0.095],
            depth_thick=0.125,
            colors=[P["skin"], P["skin_shadow"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Pé descalço largo ancorado ao chão
        flen, fwidth = 0.145, 0.082
        mk.obox(c, (foot[0] + c.fx * 0.015, foot[1] + c.fy * 0.015, foot[2]), (c.fx, c.fy, 0.0), flen, fwidth, 0.038, P["skin"])
        # Dedos dos pés
        mk.obox(c, (foot[0] + c.fx * 0.065, foot[1] + c.fy * 0.065, foot[2] + 0.005), (c.fx, c.fy, 0.0), 0.035, 0.076, 0.022, P["skin_shadow"], outline=False)


def draw_obi(c):
    """
    Mawashi Tradicional de Sumô:
    - Faixa espessa de seda escura enrolada múltiplas vezes ao redor da cintura/pélvis.
    - Cordões rituais dourados e vermelhos pendentes (Sagari) na frente do ventre.
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065
    pelvis_w = getattr(c, "pelvis_w", 0.35)

    # Faixa principal espessa do Mawashi
    mk.cbox(c, bx, by, z, pelvis_w + 0.045, pelvis_w * 0.88, 0.088, P["mawashi"])

    # Cordões rituais Sagari pendentes na frente da faixa
    if mk.depth(c, fx, fy) > -0.15:
        sagari_pos = (bx + fx * 0.125, by + fy * 0.125, z - 0.015)
        # Faixas de cordões rituais de seda
        mk.obox(c, sagari_pos, (0.0, 0.0, -1.0), 0.130, 0.140, 0.022, P["sagari"], up=(px, py, 0.0), outline=True)
        # Detalhe central carmim do Sagari
        mk.obox(c, (sagari_pos[0], sagari_pos[1], sagari_pos[2] - 0.02), (0.0, 0.0, -1.0), 0.085, 0.048, 0.026, P["sagari_red"], up=(px, py, 0.0), outline=False)


def draw_torso(c):
    """
    Tronco Colossal de Raiden fiel ao conceito oficial:
    - Casaco/manto Haori cerimonial de seda vermelho escuro cobrindo completamente os ombros,
      laterais e costas, vestindo o corpo como casaco tradicional (e não como capa).
    - Ombreiras e jugo superior contínuo em seda vermelho escuro sobre os deltoides e clavículas.
    - Peitoral e abdômen pesados e musculosos de rikishi expostos na abertura frontal em V.
    - Lapelas frontais com bordado dourado e brasões Mon descendo até a cintura.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    torso_w = getattr(c, "torso_w", 0.36)

    # 1. Base do Tronco vestida pelo Haori vermelho escuro (costas e laterais sólidas)
    mk.cbox(c, bx - fx * 0.015, by - fy * 0.015, tz + 0.08, torso_w + 0.05, torso_w * 0.74, 0.20, P["haori"])

    # 2. Jugo e manto sobre os ombros (cobre completamente os ombros e clavículas com tecido vermelho escuro)
    mk.cbox(c, bx - fx * 0.010, by - fy * 0.010, tz + 0.20, torso_w + 0.14, torso_w * 0.78, 0.075, P["haori"])

    # 3. Gola alta cerimonial de seda vermelho escuro com debrum dourado ao redor do pescoço
    collar_pos = (bx - fx * 0.035, by - fy * 0.035, tz + 0.24)
    mk.obox(c, collar_pos, (fx, fy, 0.0), 0.065, 0.170, 0.045, P["haori_gold"], up=(0.0, 0.0, 1.0), outline=False)
    mk.obox(c, (collar_pos[0] + fx * 0.012, collar_pos[1] + fy * 0.012, collar_pos[2]), (fx, fy, 0.0), 0.055, 0.155, 0.040, P["haori_dark"], up=(0.0, 0.0, 1.0), outline=False)

    # 4. Capas dos ombros em seda vermelho escuro cobrindo a junção dos deltoides
    for s in (-1.0, 1.0):
        sh_pos = (bx + px * 0.180 * s, by + py * 0.180 * s, tz + 0.19)
        mk.obox(c, sh_pos, (0.0, 0.0, -1.0), 0.135, 0.130, 0.110, P["haori"], up=(fx, fy, 0.0), outline=True)
        # Galão dourado na curvatura superior do ombro
        mk.obox(c, (sh_pos[0], sh_pos[1], sh_pos[2] + 0.020), (0.0, 0.0, -1.0), 0.125, 0.125, 0.020, P["haori_gold"], up=(fx, fy, 0.0), outline=False)
        # Brasão Mon dourado circular na lateral externa do ombro (fiel ao conceito)
        mk.obox(c, (sh_pos[0] + px * 0.048 * s, sh_pos[1] + py * 0.048 * s, sh_pos[2]), (px * s, py * s, 0.0), 0.012, 0.046, 0.046, P["haori_gold"], up=(0.0, 0.0, 1.0), outline=False)

    # 5. Abertura frontal em V: Peitoral e ventre musculoso expostos (visíveis quando voltado para a câmera)
    if mk.depth(c, fx, fy) > -0.15:
        chest_pos = (bx + fx * 0.060, by + fy * 0.060, tz + 0.10)
        mk.obox(c, chest_pos, (fx, fy, 0.0), 0.065, 0.185, 0.165, P["skin"], up=(0.0, 0.0, 1.0), outline=False)
        # Relevo e sombra anatômica dos peitorais maciços de rikishi
        mk.obox(c, (bx + fx * 0.095, by + fy * 0.095, tz + 0.14), (fx, fy, 0.0), 0.045, 0.175, 0.082, P["skin_shadow"], up=(0.0, 0.0, 1.0), outline=False)
        # Cicatriz marcial / sulco peitoral estóico
        mk.obox(c, (bx + fx * 0.105, by + fy * 0.105, tz + 0.14), (fx, fy, 0.0), 0.025, 0.015, 0.075, P["skin_shadow"], up=(0.0, 0.0, 1.0), outline=False)

    # 6. Lapelas frontais do Haori descendo pelo peito (visíveis quando de frente para a câmera)
    if mk.depth(c, fx, fy) > -0.05:
        for s in (-1.0, 1.0):
            lapel_anchor = (bx + fx * 0.085 + px * 0.125 * s, by + fy * 0.085 + py * 0.125 * s, tz + 0.20)
            p_top = lapel_anchor
            p_mid = (lapel_anchor[0] + fx * 0.01, lapel_anchor[1] + fy * 0.01, tz + 0.08)
            p_bot = (lapel_anchor[0], lapel_anchor[1], tz - 0.04)
            draw_ribbon_mesh_3d(
                c.surface, c.camera,
                spine_points=[p_top, p_mid, p_bot],
                widths=[0.095, 0.100, 0.090],
                depth_thick=0.035,
                colors=[P["haori"], P["haori_dark"]],
                side_vec=(px * s, py * s, 0.0),
                normal_vec=(fx, fy, 0.0),
                outline=True,
                alpha=c.alpha,
            )
            # Orla dourada brocada na borda interna da lapela
            mk.obox(c, (p_mid[0] - px * 0.030 * s, p_mid[1] - py * 0.030 * s, p_mid[2]), (0.0, 0.0, -1.0), 0.17, 0.022, 0.028, P["haori_gold"], up=(fx, fy, 0.0), outline=False)
            # Brasões Mon circulares dourados ao longo da lapela (fiel ao conceito)
            mk.obox(c, (p_top[0], p_top[1], p_top[2] - 0.025), (fx, fy, 0.0), 0.015, 0.044, 0.044, P["haori_gold"], up=(0.0, 0.0, 1.0), outline=False)
            mk.obox(c, (p_mid[0], p_mid[1], p_mid[2] - 0.020), (fx, fy, 0.0), 0.015, 0.038, 0.038, P["haori_gold"], up=(0.0, 0.0, 1.0), outline=False)

    # 7. Manto dorsal do Haori (quando visto de costas em relação à câmera)
    if mk.depth(c, -fx, -fy) > -0.05:
        _render_haori_back(c, P)


def draw_arm(c, shoulder, hand, side):
    """
    Braço Colossal de Rikishi:
    - Manga de seda vermelho escuro do Haori cobrindo o ombro e o terço superior do bíceps.
    - Barra de brocado dourado na boca da manga.
    - Antebraço musculoso e maciço com tom de pele pura de rikishi.
    - Palma pesada e ampla para golpes Tsuppari.
    """
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.19)
    h = (hand[0], hand[1], hand[2] - 0.060)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.035), (0.0, 0.0, -0.025))

    # Manga do Haori de seda vermelho escuro no ombro/bíceps
    mk.limb(c, s, e, 0.095, P["haori"], w_end=0.082)
    # Borda dourada da manga
    mk.obox(c, e, (c.fx, c.fy, 0.0), 0.086, 0.086, 0.024, P["haori_gold"], outline=False)

    # Antebraço musculoso e maciço com tom de pele pura
    mk.limb(c, e, h, 0.076, P["skin"], w_end=0.065)

    # Palma aberta maciça de Sumô
    h_box = (h[0], h[1], h[2] - 0.020)
    mk.cbox(c, h_box[0], h_box[1], h_box[2], 0.068, 0.068, 0.058, P["skin"])
    # Dedos da palma estendidos
    fwd_x = h_box[0] + c.fx * 0.035
    fwd_y = h_box[1] + c.fy * 0.035
    mk.obox(c, (fwd_x, fwd_y, h_box[2]), (c.fx, c.fy, 0.0), 0.038, 0.062, 0.040, P["skin_shadow"], up=(0.0, 0.0, 1.0), outline=False)

    return s, e

    return s, e


def draw_sleeves(c, arms):
    """Mangas amplas do Haori de seda preta drapeando para baixo a partir dos ombros."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.05)
    for s, e, side in arms:
        anchor = (s[0] + c.px * side * 0.03, s[1] + c.py * side * 0.03, s[2] - 0.01)
        offs = cloth.chain_offsets(2, c.walk_timer, 1.5 * side, (0.0, 0.0), (c.px, c.py), amp=amp * 1.2, freq=freq)
        mid = (anchor[0] + offs[0][0], anchor[1] + offs[0][1], anchor[2] - 0.09 + offs[0][2])
        hem = (anchor[0] + offs[1][0], anchor[1] + offs[1][1], anchor[2] - 0.18 + offs[1][2])

        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[anchor, mid, hem],
            widths=[0.11, 0.13, 0.15],
            depth_thick=0.045,
            colors=[P["haori"], P["haori_dark"]],
            side_vec=(c.fx, c.fy, 0.0),
            normal_vec=(c.px * side, c.py * side, 0.0),
            outline=True,
            alpha=c.alpha,
        )
        # Barra dourada na boca da manga
        p_gold = (hem[0], hem[1], hem[2] + 0.015)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[p_gold, hem],
            widths=[0.15, 0.15],
            depth_thick=0.025,
            colors=[P["haori_gold"], P["haori_gold"]],
            side_vec=(c.fx, c.fy, 0.0),
            normal_vec=(c.px * side, c.py * side, 0.0),
            outline=False,
            alpha=c.alpha,
        )


def draw_head(c):
    """
    Cabeça Esculpida de Raiden:
    - Calota craniana robusta com penteado tradicional Chonmage / Oicho-mage amarrado no topo.
    - Fita branca cerimonial Motoyui segurando o coque.
    - Rosto marcial com olhar estóico de Yokozuna via `draw_portrait_face_3d`.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    hw = getattr(c, "head_w", 0.165)

    # 1. Calota craniana e cabelos negros
    cran_top = (bx - fx * 0.015, by - fy * 0.015, hz + 0.175)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, hz + 0.130), cran_top,
        w_start=hw * 1.05, h_start=hw * 1.05,
        w_end=hw * 0.75, h_end=hw * 0.75,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # 2. Coque tradicional de Sumô (Oicho-mage) com laço de leque no topo
    bun_base = (bx - fx * 0.025, by - fy * 0.025, hz + 0.170)
    bun_fan = (bx + fx * 0.015, by + fy * 0.015, hz + 0.235)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        bun_base, bun_fan,
        w_start=0.068, h_start=0.068,
        w_end=0.082, h_end=0.048,  # Expansão em leque Oicho-mage
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )
    # Cordão de papel branco ritual Motoyui amarrando a base do coque
    mk.obox(c, bun_base, (0.0, 0.0, 1.0), 0.025, 0.065, 0.065, P["motoyui"], up=(fx, fy, 0.0), outline=False)

    # 3. Rosto marcial masculino 3D low-poly estilizado
    if not getattr(c, "_face_drawn", False):
        draw_portrait_face_3d(c, char_type="raiden")
        c._face_drawn = True


def _render_palm_effects(c, hand_r):
    """Desenha a aura e o impacto de choque da investida Tsuppari."""
    P = pal()
    if c.is_melee and c.atk_progress is not None and 0.20 <= c.atk_progress <= 0.70:
        rx, ry, rz = hand_r
        mk.cbox(c, rx, ry, rz, 0.16, 0.16, 0.16, P["palm_aura"], outline=False)
        mk.cbox(c, rx, ry, rz, 0.08, 0.08, 0.08, P["palm_core"], outline=False)


def draw_front(c, hand_l, hand_r):
    """
    Camada frontal:
    - Renderiza auras e impactos de palma se as mãos estiverem no plano frontal à frente do tronco.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_palm_effects(c, hand_r)
