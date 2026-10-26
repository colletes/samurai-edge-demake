"""
Hendrika van der Meer, a Alquimista de Dejima (Ciclo 6):
- Cientista e estudiosa holandesa da Companhia das Índias Orientais (VOC) em Nagasaki.
- Rosto anime delicado e inteligente com sorriso travesso e excêntrico de 'mad scientist', olhos turquesa elétricos brilhantes e cachos loiros rebeldes.
- Traje barroco aristocrático: casaca de veludo azul-safira com botões de latão dourado, gola com folhos de linho branco (Jabot), culotes afunilados e botas de montaria em couro.
- Quepe mercantil de feltro escuro com óculos de proteção alquímica (Goggles) de aros de latão polido repousados na aba.
- Braços articulados contínuos (draw_arm) com mangas de veludo e punhos rendados.
- Estilete cirúrgico de prata empunhado firmemente dentro da mão direita (sem flutuação).
- Balão químico com líquido borbulhante e vapor luminescente seguro na mão esquerda.
- Ordenação dinâmica 3D (Painter's Algorithm) rigorosa: bandoleira, poção e adaga são ocluídos perfeitamente pelas costas da casaca quando de costas (180°), e os cachos loiros posteriores permanecem exuberantemente visíveis na visão dorsal.
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

SKIN = (248, 226, 210)
SKIN_SHADOW = (216, 188, 170)

PALETTE = {
    # Casaca de Veludo Azul-Safira e Forro
    "velvet_blue": (24, 52, 115),
    "velvet_dark": (14, 32, 75),
    "velvet_light": (42, 82, 168),
    "torso": (24, 52, 115),
    "gold_button": (235, 195, 65),

    # Folhos de Renda (Jabot) e Camisa de Linho
    "lace_jabot": (248, 246, 240),
    "lace_dark": (212, 210, 204),

    # Couro da Bandoleira, Cintos e Botas
    "leather_strap": (95, 58, 34),
    "leather_dark": (60, 36, 20),
    "boot": (75, 46, 28),
    "boot_cuff": (115, 72, 44),
    "belt": (95, 58, 34),
    "glove": (238, 235, 226),

    # Calças de Cavalaria / Culotes
    "pants": (32, 38, 52),
    "pants_dark": (20, 24, 35),

    # Quepe Mercantil e Óculos de Proteção (Goggles)
    "tricorn": (24, 28, 38),
    "tricorn_rim": (48, 54, 70),
    "goggle_brass": (218, 172, 60),
    "goggle_lens": (85, 220, 230),
    "goggle_strap": (48, 32, 20),

    # Cabelos Loiros e Ondulados
    "hair": (235, 195, 88),
    "hair_dark": (185, 145, 52),
    "hair_light": (255, 225, 128),

    # Anatomia Feminina
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "neck": SKIN,
    "eye": (38, 165, 175),
    "brow": (160, 105, 52),
    "lip": (224, 96, 114),

    # Balão Alquímico, Reagentes Luminescentes e Estilete
    "glass_vial": (195, 235, 245),
    "reagent_green": (65, 240, 140),
    "reagent_white": (255, 255, 255),
    "reagent_violet": (215, 110, 255),
    "reagent_amber": (255, 185, 45),
    "vapor_glow": (140, 245, 250),
    "stiletto_steel": (235, 242, 252),
    "stiletto_edge": (255, 255, 255),
    "stiletto_guard": (218, 172, 60),
    "stiletto_grip": (45, 30, 22),
}

MATERIALS = {
    "velvet_blue": "velvet",
    "velvet_dark": "velvet",
    "gold_button": "gold",
    "lace_jabot": "silk",
    "leather_strap": "leather",
    "boot": "leather",
    "pants": "canvas",
    "stiletto_steel": "steel",
    "goggle_brass": "gold",
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Animação Alquímica
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Postura Ativa da Alquimista:
    - Mão esquerda ergue um balão químico borbulhante em análise científica curiosa.
    - Mão direita empunha o estilete cirúrgico fino apontado em ângulo pronto para corte rápido.
    """
    breathe = math.sin(c.walk_timer * 2.8) * 0.010
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    pose = c.extra_props.get("pose") if c.extra_props else None

    if pose == "alchemist_inspect":
        # Balão erguido bem próximo aos olhos para examinar a cor da reação
        left = (bx + fx * 0.16 + px * 0.06, by + fy * 0.16 + py * 0.06, tz + 0.22)
        right = (bx - fx * 0.04 - px * 0.12, by - fy * 0.04 - py * 0.12, tz + 0.08)
        return left, right

    if pose == "alchemist_laugh":
        # Mão direita na cintura e mão esquerda erguendo a poção em triunfo excêntrico
        right = (bx - px * 0.16, by - py * 0.16, tz + 0.06)
        left = (bx + fx * 0.12 + px * 0.14, by + fy * 0.12 + py * 0.14, tz + 0.26)
        return left, right

    # Guarda neutra
    left = (bx + fx * 0.16 + px * 0.12, by + fy * 0.16 + py * 0.12, tz + 0.15)
    right = (bx + fx * 0.18 - px * 0.08, by + fy * 0.18 - py * 0.08, tz + 0.10)
    return left, right


def attack_arms(c):
    """
    Estocada Cirúrgica / Arremesso Alquímico:
    - Ataque perfurante com o estilete de prata em velocidade relâmpago.
    - Mão esquerda recua mantendo o frasco seguro ou arremessa fumaça cáustica.
    """
    p = c.atk_progress if c.atk_progress is not None else 0.0
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    thrust = math.sin(p * math.pi) * 0.44

    # Estilete direito estocado em linha reta
    right = (bx + fx * (0.24 + thrust) - px * 0.02,
             by + fy * (0.24 + thrust) - py * 0.02,
             tz + 0.15)
    # Braço esquerdo recuando em balanço com o frasco
    left = (bx - fx * (0.08 + thrust * 0.2) + px * 0.16,
            by - fy * (0.08 + thrust * 0.2) + py * 0.16,
            tz + 0.18)
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
    - Abas da casaca de veludo azul-safira (Frock Coat tails) descendo pelas costas até as coxas.
    - Bainha de couro do estilete no quadril direito (se do lado visível).
    - Frasco alquímico e estilete SE as mãos estiverem atrás do tronco em relação à câmera (Painter's Algorithm).
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    d_torso = mk.depth(c, bx, by)
    trail, amp, freq = mk.motion(c, 0.035)

    # 1. Abas da Casaca de Veludo Azul nas costas
    o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.65, trail, (px, py), amp=amp * 0.5, freq=freq)
    p_top = (bx - fx * 0.06, by - fy * 0.06, tz + 0.12)
    p_mid = (bx - fx * 0.13 + o1[0], by - fy * 0.13 + o1[1], tz - 0.04 + o1[2])
    p_hem = (bx - fx * 0.16 + o2[0], by - fy * 0.16 + o2[1], tz - 0.22 + o2[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p_top, p_mid, p_hem],
        widths=[0.24, 0.28, 0.32],
        depth_thick=0.024,
        colors=[P["velvet_blue"], P["velvet_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # 2. Bainha de couro do estilete no quadril
    scabbard_pos = (bx - px * 0.13 - fx * 0.02, by - py * 0.13 - fy * 0.02, tz - 0.02)
    if mk.depth(c, scabbard_pos[0], scabbard_pos[1]) < d_torso + 0.04:
        mk.obox(c, scabbard_pos, (0.0, 0.0, -1.0), 0.22, 0.028, 0.038, P["leather_strap"], up=(fx, fy, 0.0), outline=True)
        mk.obox(c, (scabbard_pos[0], scabbard_pos[1], scabbard_pos[2] + 0.01), (0.0, 0.0, -1.0), 0.03, 0.032, 0.042, P["stiletto_guard"], up=(fx, fy, 0.0), outline=False)

    # 3. Ordenação dinâmica: se as mãos estiverem atrás do tronco (personagem de costas),
    # renderiza os itens segurados AQUI para que o tronco os oclua naturalmente
    hand_l, hand_r = _current_hands(c)
    if mk.depth(c, hand_l[0], hand_l[1]) < d_torso:
        _render_chemical_flask(c, hand_l)
    if mk.depth(c, hand_r[0], hand_r[1]) < d_torso:
        _render_stiletto(c, hand_r)


def draw_legs(c):
    """
    Pernas ágeis em malha contínua 3D:
    - Culotes escuros afunilados entrando sem degraus em botas altas de montaria.
    - Botas de couro marrom com cano dobrado (cuff) e fivela dourada.
    """
    P = pal()
    trail, amp, freq = mk.motion(c, 0.032)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.75 * sign, trail, (c.px, c.py), amp=amp * 0.35, freq=freq)

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.2, sh[1] + o1[1] * 0.2, sh[2] + 0.15)
        cuff_pos = (sh[0] + o1[0] * 0.1, sh[1] + o1[1] * 0.1, sh[2] + 0.08)
        ankle = (foot[0] + o2[0] * 0.1, foot[1] + o2[1] * 0.1, foot[2] + 0.02)

        # 1. Culote ajustado em malha contínua até o cano da bota
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos],
            widths=[0.108, 0.096, 0.082],
            depth_thick=0.085,
            colors=[P["pants"], P["pants_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # 2. Bota de montaria contínua do cano ao tornozelo
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[cuff_pos, ankle],
            widths=[0.084, 0.070],
            depth_thick=0.075,
            colors=[P["boot"], P["leather_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Cano dobrado superior da bota (Cuff)
        mk.obox(c, cuff_pos, (c.fx, c.fy, 0.0), 0.082, 0.088, 0.024, P["boot_cuff"], outline=False)
        mk.obox(c, (cuff_pos[0] + c.fx * 0.04, cuff_pos[1] + c.fy * 0.04, cuff_pos[2]), (c.fx, c.fy, 0.0), 0.012, 0.024, 0.016, P["gold_button"], outline=False)

        # Pé da bota de montaria
        flen, fwidth = 0.125, 0.062
        mk.obox(c, (foot[0] + c.fx * 0.015, foot[1] + c.fy * 0.015, foot[2]), (c.fx, c.fy, 0.0), flen, fwidth, 0.034, P["boot"])


def draw_obi(c):
    """Cinto mercantil de couro com fivela de latão e bolsas de reagentes."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065
    pelvis_w = getattr(c, "pelvis_w", 0.24)

    # Cinto principal de couro
    mk.cbox(c, bx, by, z, pelvis_w - 0.01, pelvis_w * 0.74, 0.052, P["leather_strap"])
    # Fivela dourada retangular (apenas visível pela frente)
    if mk.depth(c, fx, fy) > -0.05:
        mk.obox(c, (bx + fx * 0.088, by + fy * 0.088, z + 0.002), (0.0, 0.0, 1.0), 0.045, 0.048, 0.014, P["gold_button"], up=(fx, fy, 0.0), outline=False)


def draw_torso(c):
    """
    Tronco Barroco de Hendrika:
    - Casaca acinturada de veludo azul-safira com lapelas orientadas e fileira de botões dourados.
    - Folhos de linho branco (Jabot) no peito.
    - Bandoleira transversal de couro: desenhada de frente COM os tubos de ensaio químicos, ou de costas apenas com a tira dorsal sem vazamento de reagentes.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    torso_w = getattr(c, "torso_w", 0.23)

    # 1. Casaca de veludo acinturada
    mk.cbox(c, bx, by, tz + 0.075, torso_w - 0.015, torso_w * 0.68, 0.17, P["velvet_blue"])

    # 2. Detalhes frontais: Jabot, botões dourados e bandoleira com frascos
    # (Renderizados ESTRITAMENTE quando o peito está voltado para a câmera)
    if mk.depth(c, fx, fy) > -0.05:
        # Folhos de renda branca (Jabot)
        jabot_pos = (bx + fx * 0.075, by + fy * 0.075, tz + 0.13)
        mk.obox(c, jabot_pos, (0.0, 0.0, -1.0), 0.075, 0.085, 0.022, P["lace_jabot"], up=(px, py, 0.0), outline=False)
        mk.obox(c, (jabot_pos[0] + fx * 0.01, jabot_pos[1] + fy * 0.01, jabot_pos[2] - 0.03), (0.0, 0.0, -1.0), 0.045, 0.055, 0.018, P["lace_dark"], up=(px, py, 0.0), outline=False)

        # Botões dourados da casaca
        for i in range(3):
            bz = tz + 0.08 - i * 0.035
            mk.obox(c, (bx + fx * 0.082, by + fy * 0.082, bz), (fx, fy, 0.0), 0.012, 0.016, 0.016, P["gold_button"], outline=False)

        # Bandoleira frontal de couro cruzando do ombro direito ao quadril esquerdo
        bando_top = (bx - px * 0.11, by - py * 0.11, tz + 0.19)
        bando_mid = (bx + fx * 0.075, by + fy * 0.075, tz + 0.08)
        bando_bot = (bx + px * 0.11, by + py * 0.11, tz - 0.02)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[bando_top, bando_mid, bando_bot],
            widths=[0.038, 0.038, 0.038],
            depth_thick=0.015,
            colors=[P["leather_strap"], P["leather_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(fx, fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

        # Tubos de ensaio químicos presos na bandoleira (verde ácido, fósforo branco, enxofre)
        colors_vials = [P["reagent_green"], P["reagent_white"], P["reagent_violet"]]
        for i, col in enumerate(colors_vials):
            vx = bx + fx * 0.085 + px * (0.035 - i * 0.035)
            vy = by + fy * 0.085 + py * (0.035 - i * 0.035)
            vz = tz + 0.11 - i * 0.035
            mk.obox(c, (vx, vy, vz), (0.0, 0.0, 1.0), 0.045, 0.014, 0.014, col, outline=False)
            mk.obox(c, (vx, vy, vz + 0.02), (0.0, 0.0, 1.0), 0.012, 0.016, 0.016, P["leather_dark"], outline=False)

    # 3. Alça traseira da bandoleira nas costas (se de costas para a câmera)
    elif mk.depth(c, -fx, -fy) > -0.05:
        bando_back_top = (bx - px * 0.11, by - py * 0.11, tz + 0.19)
        bando_back_mid = (bx - fx * 0.075, by - fy * 0.075, tz + 0.08)
        bando_back_bot = (bx + px * 0.11, by + py * 0.11, tz - 0.02)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[bando_back_top, bando_back_mid, bando_back_bot],
            widths=[0.036, 0.036, 0.036],
            depth_thick=0.012,
            colors=[P["leather_strap"], P["leather_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(-fx, -fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )


def draw_arm(c, shoulder, hand, side):
    """
    Braço Anatômico da Alquimista:
    - Manga justa de veludo azul-safira do ombro ao cotovelo.
    - Punho rendado francês (lace cuff) e luva fina de couro no antebraço e mão.
    """
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.19)
    h = (hand[0], hand[1], hand[2] - 0.060)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.025), (0.0, 0.0, -0.022))

    # Manga de veludo azul do ombro ao cotovelo
    mk.limb(c, s, e, 0.056, P["velvet_blue"], w_end=0.046)
    # Dobra da manga / vira no cotovelo
    mk.obox(c, e, (c.fx, c.fy, 0.0), 0.054, 0.054, 0.020, P["velvet_dark"], outline=False)

    # Antebraço com luva e manga ajustada
    mk.limb(c, e, h, 0.044, P["glove"], w_end=0.036)
    # Punho de renda branca no pulso
    wrist_pt = mk.lerp(e, h, 0.82)
    mk.obox(c, wrist_pt, (c.fx, c.fy, 0.0), 0.048, 0.048, 0.018, P["lace_jabot"], outline=False)

    # Mão enluvada
    mk.cbox(c, h[0], h[1], h[2] - 0.018, 0.040, 0.040, 0.038, P["glove"])
    return s, e


def draw_head(c):
    """
    Cabeça Esculpida de Hendrika:
    - Quepe mercantil de feltro escuro com óculos de proteção (Goggles) de latão na aba.
    - Cachos loiros laterais emoldurando as bochechas.
    - Cachos loiros posteriores exuberantes na nuca visíveis quando vista de costas.
    - Rosto delicado anime expressivo com olhar de 'mad scientist' via `draw_portrait_face_3d`.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    hw = getattr(c, "head_w", 0.13)
    trail, amp, freq = mk.motion(c, 0.035)

    # 1. Cachos loiros laterais sob o quepe
    for sign in (-1.0, 1.0):
        lock_top = (bx + px * 0.052 * sign, by + py * 0.052 * sign, hz + 0.125)
        lock_mid = (bx + px * 0.062 * sign + fx * 0.02, by + py * 0.062 * sign + fy * 0.02, hz + 0.060)
        lock_tip = (bx + px * 0.055 * sign + fx * 0.03, by + py * 0.055 * sign + fy * 0.03, hz + 0.015)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[lock_top, lock_mid, lock_tip],
            widths=[0.028, 0.035, 0.020],
            depth_thick=0.016,
            colors=[P["hair"], P["hair_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(fx, fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

    # 2. Cachos loiros posteriores na nuca e costas (Renderizados aqui no draw_head
    # para NUNCA serem ocluídos pela calota craniana na visão de costas!)
    if mk.depth(c, -fx, -fy) > -0.15:
        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.5, trail, (px, py), amp=amp * 0.5, freq=freq)
        hair_back_base = (bx - fx * 0.045, by - fy * 0.045, hz + 0.120)
        hair_back_mid = (bx - fx * 0.075 + o1[0] * 0.4, by - fy * 0.075 + o1[1] * 0.4, hz + 0.035)
        hair_back_tip = (bx - fx * 0.100 + o2[0] * 0.5, by - fy * 0.100 + o2[1] * 0.5, hz - 0.045)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[hair_back_base, hair_back_mid, hair_back_tip],
            widths=[0.145, 0.165, 0.130],
            depth_thick=0.028,
            colors=[P["hair"], P["hair_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(-fx, -fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )
        # Mecha lateral dourada iluminada sobre as costas
        mk.obox(c, hair_back_mid, (-fx, -fy, 0.0), 0.020, 0.085, 0.075, P["hair_light"], up=(0.0, 0.0, 1.0), outline=False)

    # 3. Quepe Mercantil de Feltro (Tricorn / Merchant Cap)
    cap_base = (bx, by, hz + 0.138)
    cap_top = (bx - fx * 0.015, by - fy * 0.015, hz + 0.195)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        cap_base, cap_top,
        w_start=hw * 1.12, h_start=hw * 1.12,
        w_end=hw * 0.85, h_end=hw * 0.85,
        color=P["tricorn"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Aba frontal do quepe
    mk.obox(c, (bx + fx * 0.045, by + fy * 0.045, hz + 0.142), (fx, fy, 0.0), 0.045, hw * 1.05, 0.018, P["tricorn_rim"], up=(0.0, 0.0, 1.0), outline=False)

    # 4. Óculos Alquímicos de Proteção (Goggles) repousados na aba do quepe
    if mk.depth(c, fx, fy) > -0.2:
        gog_z = hz + 0.145
        # Tira de couro ao redor do quepe
        mk.obox(c, (bx, by, gog_z), (0.0, 0.0, 1.0), 0.014, hw * 1.08, hw * 1.08, P["goggle_strap"], up=(fx, fy, 0.0), outline=False)
        # Dois aros de latão dos óculos
        for sign in (-1.0, 1.0):
            gx = bx + fx * 0.055 + px * 0.026 * sign
            gy = by + fy * 0.055 + py * 0.026 * sign
            # Aro de latão
            mk.obox(c, (gx, gy, gog_z), (fx, fy, 0.0), 0.020, 0.032, 0.032, P["goggle_brass"], up=(0.0, 0.0, 1.0), outline=True)
            # Lente ciano translúcida brilhante
            mk.obox(c, (gx + fx * 0.005, gy + fy * 0.005, gog_z), (fx, fy, 0.0), 0.014, 0.022, 0.022, P["goggle_lens"], up=(0.0, 0.0, 1.0), outline=False)

    # 5. Rosto anime feminino com expressão de 'mad scientist'
    if not getattr(c, "_face_drawn", False):
        draw_portrait_face_3d(c, char_type="hendrika")
        c._face_drawn = True


def _render_chemical_flask(c, hand_l):
    """Renderiza o balão químico esférico com reagente luminescente borbulhante e vapor."""
    P = pal()
    fx, fy = c.fx, c.fy
    lx, ly, lz = hand_l[0], hand_l[1], hand_l[2] - 0.060
    flask_pos = (lx + fx * 0.03, ly + fy * 0.03, lz)

    # Frasco de vidro esférico repousado na palma
    mk.cbox(c, flask_pos[0], flask_pos[1], flask_pos[2], 0.065, 0.065, 0.065, P["glass_vial"], outline=False)
    # Reagente líquido brilhante verde ácido / turquesa
    mk.cbox(c, flask_pos[0], flask_pos[1], flask_pos[2] - 0.008, 0.050, 0.050, 0.044, P["reagent_green"], outline=False)
    # Gargalo do frasco com rolha de cortiça seguro pelos dedos
    mk.obox(c, (flask_pos[0], flask_pos[1], flask_pos[2] + 0.042), (0.0, 0.0, 1.0), 0.035, 0.020, 0.020, P["glass_vial"], up=(fx, fy, 0.0), outline=False)
    mk.obox(c, (flask_pos[0], flask_pos[1], flask_pos[2] + 0.062), (0.0, 0.0, 1.0), 0.015, 0.022, 0.022, P["leather_dark"], up=(fx, fy, 0.0), outline=False)

    # Vapor químico ascendente com brilho e oscilação
    flicker = math.sin(c.walk_timer * 6.0) * 0.01
    vapor_pos = (flask_pos[0] + fx * 0.01, flask_pos[1] + fy * 0.01, flask_pos[2] + 0.085 + flicker)
    mk.cbox(c, vapor_pos[0], vapor_pos[1], vapor_pos[2], 0.038, 0.038, 0.038, P["vapor_glow"], outline=False)


def _render_stiletto(c, hand_r):
    """Renderiza o estilete cirúrgico de aço empunhado solidamente na mão direita."""
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    # Mão direita posicionada
    rx, ry, rz = hand_r[0], hand_r[1], hand_r[2] - 0.060

    if c.is_melee and c.atk_progress is not None:
        s_dir = (fx, fy, 0.0)
    else:
        # Direção diagonal para baixo e ligeiramente para frente
        s_dir = (fx * 0.65 + px * 0.15, fy * 0.65 + py * 0.15, -0.65)

    # Empunhadura (grip) de madeira escura segurada diretamente dentro da mão
    mk.obox(c, (rx, ry, rz), s_dir, 0.090, 0.024, 0.024, P["stiletto_grip"], up=(0.0, 0.0, 1.0), outline=False)
    # Pomo dourado na base da mão
    mk.obox(c, (rx - s_dir[0] * 0.045, ry - s_dir[1] * 0.045, rz - s_dir[2] * 0.045), s_dir, 0.022, 0.036, 0.036, P["stiletto_guard"], up=(0.0, 0.0, 1.0), outline=False)
    # Guarda cruciforme dourada na frente dos dedos
    g_pt = (rx + s_dir[0] * 0.045, ry + s_dir[1] * 0.045, rz + s_dir[2] * 0.045)
    mk.obox(c, g_pt, s_dir, 0.022, 0.058, 0.058, P["stiletto_guard"], up=(0.0, 0.0, 1.0), outline=False)

    # Lâmina afiada fina de aço cirúrgico partindo da guarda
    blade_len = 0.30
    b_pt = (g_pt[0] + s_dir[0] * 0.015, g_pt[1] + s_dir[1] * 0.015, g_pt[2] + s_dir[2] * 0.015)
    mk.obox(c, b_pt, s_dir, blade_len, 0.020, 0.014, P["stiletto_steel"], up=(0.0, 0.0, 1.0), outline=False)
    # Fio de corte reluzente no gume
    mk.obox(c, b_pt, s_dir, blade_len, 0.008, 0.010, P["stiletto_edge"], up=(0.0, 0.0, 1.0), outline=False)


def draw_front(c, hand_l, hand_r):
    """
    Camada frontal:
    - Balão químico e estilete cirúrgico são renderizados aqui SE as mãos estiverem
      no plano frontal à frente do tronco (Painter's Algorithm).
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    if mk.depth(c, hand_l[0], hand_l[1]) >= d_torso:
        _render_chemical_flask(c, hand_l)
    if mk.depth(c, hand_r[0], hand_r[1]) >= d_torso:
        _render_stiletto(c, hand_r)
