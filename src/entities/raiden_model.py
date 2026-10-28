"""
Raiden Tameemon — O Grande Campeão Yokozuna dos Trovões (Fase 2 Overhaul):
- Lendário grande campeão Yokozuna em postura cerimonial inabalável.
- Físico colossal e imponente de rikishi: peitoral e abdômen pesados, ombros largos e braços maciços
  com palmas abertas monumentais para empurrões Harite e Morote-Tsuppari.
- Grand Yokozuna Mawashi: faixa de seda carvão pesada com corda sagrada Shimenawa trançada,
  serpentinas brancas rituais Gohei em zigue-zague e cordões Sagari dourados/vermelhos.
- Manto cerimonial Haori de seda vermelho escuro (carmesim nobre) com brasões Mon dourados e mangas amplas.
- Penteado tradicional Oicho-mage em leque tradicional preso com cordão de papel ritual Motoyui.
- Cinemática 3D completa de 11 entregáveis:
  1. Idle: Postura Kamae de Sumô com respiração viva e peso inabalável.
  2. Walk: Suriashi Yokozuna — passada arrastada cerimonial no dohyo.
  3. Golpe 1 (Harite): Empurrão de palma direita com rotação de quadril e peso corporal.
  4. Golpe 2 (Morote-Tsuppari): Bofetada dupla convergente nas têmporas que quebra guardas.
  5. Investida (Tachiai Tackle 3-Fases): Crouch Kamae -> Aceleração contínua (4.0 -> 12.5 m/s) com
     inclinação frontal de 35° -> Impacto devastador (2 de dano em velocidade máxima).
  6. Esquiva (Shiko Slip-Step): Deslize baixo no solo do dohyo sem rolamento, com pisada firme e poeira.
  7. Guarda/Parry (Gassho-hineri): Braços cruzados anulando 100% de recuo de impacto e refletindo projéteis.
  8. Reação de Parry (Hataki-komi): Empurrão descendente de contra-ataque.
  9. Intro: Dupla palmada trovejante com sal ritual -> postura sagrada Sonkyo -> guarda Kamae.
  0. Vitória: Elevação da perna a 90° em Shiko ritual -> queda telúrica no solo -> punhos no mawashi com rugido.
  F1. Finisher 1: Tsuppari Sonic Decapitation (雷電掌断) — Bofetada sônica de palma aberta.
  F2. Finisher 2: Tachiai Cataclysmic Slam — Encontrão supersônico que arremessa o rival voando.
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

    # Mawashi de Seda, Corda Sagrada Shimenawa e Gohei
    "mawashi": (28, 32, 42),
    "mawashi_dark": (18, 20, 28),
    "mawashi_light": (45, 52, 68),
    "belt": (28, 32, 42),
    "sagari": (225, 185, 70),
    "sagari_red": (175, 36, 42),
    "knot": (24, 28, 38),
    "shimenawa": (235, 228, 210),     # Corda sagrada de cânhamo torcida
    "shimenawa_dark": (188, 178, 158),
    "gohei": (250, 250, 252),         # Serpentinas brancas rituais em zigue-zague
    "gohei_shadow": (205, 208, 215),

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

    # Efeitos de Palma Tsuppari, Sal Cerimonial e Impacto Sísmico
    "palm_aura": (255, 225, 140),
    "palm_core": (255, 250, 220),
    "shock_dust": (222, 198, 165),
    "salt_white": (255, 255, 255),
    "speed_line": (255, 230, 180),
}

MATERIALS = {
    "haori": "silk",
    "haori_dark": "silk",
    "haori_gold": "gold",
    "haori_lining": "silk",
    "mawashi": "silk",
    "mawashi_dark": "silk",
    "shimenawa": "rope",
    "gohei": "paper",
    "sagari": "gold",
    "skin": "skin",
}

LEGACY_MATERIALS = {
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


def _smooth(x: float) -> float:
    cx = max(0.0, min(1.0, x))
    return cx * cx * (3.0 - 2.0 * cx)


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Cinemática de Combate
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """Postura Kamae / Shikiri de Sumô com respiração e palmas imponentes."""
    breathe = math.sin(c.walk_timer * 2.2) * 0.012
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    left = (bx + fx * 0.20 + px * 0.15, by + fy * 0.20 + py * 0.15, tz + 0.12)
    right = (bx + fx * 0.24 - px * 0.10, by + fy * 0.24 - py * 0.10, tz + 0.14)
    return left, right


def attack_arms(c):
    """
    Combo de Palma Tsuppari Devastador:
    - Golpe 1 (Harite): Wind-up com rotação de quadril e recuo da mão direita, explodindo frontalmente com onda sônica.
    - Golpe 2 (Morote-Tsuppari): Ambos os braços abrem em arco e convergem nas têmporas quebrando defesas.
    """
    p = c.atk_progress if c.atk_progress is not None else 0.0
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    pose = c.extra_props.get("pose") if c.extra_props else None

    if pose == "tsuppari_2":
        # Morote-Tsuppari: Bofetada Dupla nas têmporas
        if p < 0.24:
            u = _smooth(p / 0.24)
            spread = 0.26 + 0.16 * u
            thrust = -0.08 * u
            lift = 0.06 * u
        else:
            u = _smooth((p - 0.24) / 0.76)
            spread = 0.42 - 0.28 * u
            thrust = -0.08 + 0.62 * math.sin(u * math.pi)
            lift = 0.06 - 0.02 * u

        left = (bx + fx * (0.24 + thrust) + px * spread,
                by + fy * (0.24 + thrust) + py * spread,
                tz + 0.15 + lift)
        right = (bx + fx * (0.24 + thrust) - px * spread,
                 by + fy * (0.24 + thrust) - py * spread,
                 tz + 0.15 + lift)
        return left, right

    # Golpe 1: Harite (Palma Direita Explosiva com rotação de tronco)
    if p < 0.20:
        u = _smooth(p / 0.20)
        thrust = -0.10 * u
        left_guard = 0.14 + 0.04 * u
        height_r = 0.14 + 0.04 * u
    else:
        u = _smooth((p - 0.20) / 0.80)
        thrust = -0.10 + 0.64 * math.sin(u * math.pi)
        left_guard = 0.18 - 0.06 * u
        height_r = 0.18 - 0.04 * math.sin(u * math.pi)

    right = (bx + fx * (0.25 + thrust) - px * 0.04,
             by + fy * (0.25 + thrust) - py * 0.04,
             tz + height_r)
    left = (bx + fx * left_guard + px * 0.16,
            by + fy * left_guard + py * 0.16,
            tz + 0.11)
    return left, right


def tackle_arms(c):
    """
    Cinemática 3-Fases do Tachiai Tackle:
    - Fase 1 (Crouch Kamae, p < 0.25): Mãos baixadas tocando a terra no dohyo.
    - Fase 2 (Aceleração, 0.25 <= p < 0.80): Corpo inclinado à frente em arremetida, braços bombeando com vigor.
    - Fase 3 (Impacto, p >= 0.80): Extensão explosiva das duas palmas impulsionando o rival.
    """
    p = c.atk_progress if c.atk_progress is not None else 0.5
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    if p < 0.25:
        # Mãos na argila do dohyo
        u = _smooth(p / 0.25)
        reach = 0.14 + 0.06 * u
        left = (bx + fx * reach + px * 0.14, by + fy * reach + py * 0.14, c.base_z + 0.12 - 0.04 * u)
        right = (bx + fx * reach - px * 0.14, by + fy * reach - py * 0.14, c.base_z + 0.12 - 0.04 * u)
        return left, right
    elif p < 0.80:
        # Carga acelerada com ombro direito projetado e braços bombeando
        charge_u = (p - 0.25) / 0.55
        pump = math.sin(charge_u * math.pi * 4.0) * 0.10
        left = (bx + fx * (0.24 - pump) + px * 0.18, by + fy * (0.24 - pump) + py * 0.18, tz + 0.08)
        right = (bx + fx * (0.36 + pump) - px * 0.12, by + fy * (0.36 + pump) - py * 0.12, tz + 0.14)
        return left, right
    else:
        # Impacto e empurrão devastador
        hit_u = _smooth((p - 0.80) / 0.20)
        thrust = 0.48 + 0.12 * math.sin(hit_u * math.pi)
        left = (bx + fx * thrust + px * 0.12, by + fy * thrust + py * 0.12, tz + 0.18)
        right = (bx + fx * thrust - px * 0.12, by + fy * thrust - py * 0.12, tz + 0.18)
        return left, right


def parry_arms(c):
    """Guarda Cerimonial Gassho-hineri: braços maciços cruzados diante do peito."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    pose = c.extra_props.get("pose") if c.extra_props else ""

    if pose == "hataki_komi":
        # Contra-ataque de empurrão descendente
        left = (bx + fx * 0.38 + px * 0.10, by + fy * 0.38 + py * 0.10, tz + 0.02)
        right = (bx + fx * 0.38 - px * 0.10, by + fy * 0.38 - py * 0.10, tz + 0.02)
        return left, right

    # Braços cruzados travados (Gassho-hineri)
    left = (bx + fx * 0.18 - px * 0.06, by + fy * 0.18 - py * 0.06, tz + 0.16)
    right = (bx + fx * 0.20 + px * 0.06, by + fy * 0.20 + py * 0.06, tz + 0.14)
    return left, right


def slip_step_arms(c):
    """Esquiva Shiko Slip-Step: guarda alta protetora enquanto desliza na argila."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    left = (bx + fx * 0.16 + px * 0.16, by + fy * 0.16 + py * 0.16, tz + 0.20)
    right = (bx + fx * 0.14 - px * 0.14, by + fy * 0.14 - py * 0.14, tz + 0.16)
    return left, right


def intro_arms(c):
    """Cerimonial de Intro: Palmas trovejantes -> Postura sagrada Sonkyo."""
    pose = c.extra_props.get("pose") if c.extra_props else ""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    if pose == "ceremonial_clap":
        # Palmas unidas no centro do peito com impacto
        left = (bx + fx * 0.18 + px * 0.02, by + fy * 0.18 + py * 0.02, tz + 0.16)
        right = (bx + fx * 0.18 - px * 0.02, by + fy * 0.18 - py * 0.02, tz + 0.16)
        return left, right
    elif pose == "sonkyo_squat":
        # Antebraços e punhos apoiados firmemente sobre os joelhos abertos
        left = (bx + fx * 0.18 + px * 0.26, by + fy * 0.18 + py * 0.26, c.base_z + 0.26)
        right = (bx + fx * 0.18 - px * 0.26, by + fy * 0.18 - py * 0.26, c.base_z + 0.26)
        return left, right

    return idle_arms(c)


def victory_arms(c):
    """Cerimonial de Vitória: Shiko ritual com punhos cravados no Mawashi."""
    pose = c.extra_props.get("pose") if c.extra_props else ""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    if pose == "shiko_raise":
        # Braço esquerdo apoia a coxa esquerda, braço direito ergue-se em equilíbrio
        left = (bx + px * 0.24, by + py * 0.24, tz + 0.04)
        right = (bx - px * 0.28, by - py * 0.28, tz + 0.32)
        return left, right
    elif pose in ("shiko_stomp", "mawashi_fists"):
        # Ambos os punhos cerrados e apoiados firmemente na cintura/mawashi
        left = (bx + px * 0.21, by + py * 0.21, tz - 0.02)
        right = (bx - px * 0.21, by - py * 0.21, tz - 0.02)
        return left, right

    return idle_arms(c)


def finisher_arms(c):
    """Fatalidades: Tsuppari Sonic Decapitation ou Tachiai Cataclysm."""
    p = c.atk_progress if c.atk_progress is not None else 0.5
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    pose = c.extra_props.get("pose") if c.extra_props else ""

    if pose in ("finisher_1", "sonic_decapitation"):
        # Bofetada sônica de palma aberta 360°
        rot = p * math.pi * 1.5
        thrust = math.sin(p * math.pi) * 0.60
        rx = bx + fx * thrust - px * math.cos(rot) * 0.35
        ry = by + fy * thrust - py * math.cos(rot) * 0.35
        right = (rx, ry, tz + 0.18)
        left = (bx + px * 0.18, by + py * 0.18, tz + 0.10)
        return left, right

    # Finisher 2: Cataclysm Tackle
    return tackle_arms(c)


def _current_hands(c):
    """Despacha as posições das mãos com suporte integral a todas as 11 poses da Fase 2."""
    state = getattr(c, "state", "IDLE")
    extra = getattr(c, "extra_props", None) or {}
    pose = extra.get("pose", "")

    if state == "INTRO" or pose in ("ceremonial_clap", "sonkyo_squat", "sumo_kamae"):
        return intro_arms(c)
    if state == "VICTORY" or pose in ("shiko_raise", "shiko_stomp", "mawashi_fists"):
        return victory_arms(c)
    if state == "TACHIAI_TACKLE" or pose in ("tackle", "tachiai_crouch", "tachiai_charge"):
        return tackle_arms(c)
    if state in ("ROLL", "DODGE") or pose in ("shiko_slip", "shiko_pivot"):
        return slip_step_arms(c)
    if state in ("PARRY", "DEFEND") or getattr(c, "is_parrying", False) or pose in ("sumo_guard", "hataki_komi"):
        return parry_arms(c)
    if pose in ("finisher_1", "finisher_2", "sonic_decapitation", "cataclysm_slam"):
        return finisher_arms(c)
    if (c.is_melee and c.atk_progress is not None) or state in ("ATTACK", "TSUPPARI_RUSH", "TSUPPARI_STRIKE_1", "TSUPPARI_STRIKE_2"):
        return attack_arms(c)

    return idle_arms(c)


# ---------------------------------------------------------------------------------------------------------------------
# Renderização 3D das Partes do Corpo
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Elementos renderizados atrás do corpo quando vistos do plano frontal:
    - Manto Haori cerimonial de seda vermelho escuro nas costas.
    - Nó Tate-mitsu traseiro do Mawashi.
    - Efeitos de choque se as mãos estiverem atrás do tronco.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    d_torso = mk.depth(c, bx, by)

    # 1. Manto Haori Cerimonial de Seda Vermelha escura nas costas
    if mk.depth(c, fx, fy) > -0.05:
        _render_haori_back(c, P)

    # 2. Nó traseiro rígido do Mawashi (Tate-mitsu)
    knot_pos = (bx - fx * 0.12, by - fy * 0.12, c.pelvis_z + 0.06)
    mk.obox(c, knot_pos, (-fx, -fy, 0.0), 0.080, 0.110, 0.075, P["knot"], up=(0.0, 0.0, 1.0), outline=True)

    # 3. Mãos e impactos de palma se ficarem atrás do tronco
    hl, hr = _current_hands(c)
    w_mid = ((hl[0] + hr[0]) * 0.5, (hl[1] + hr[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_palm_effects(c, hl, hr)


def _render_haori_back(c, P):
    """Manto cerimonial dorsal em seda carmesim nobre com brasão Mon dourado."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.035)
    o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.6, trail, (px, py), amp=amp * 0.5, freq=freq)

    p_neck = (bx - fx * 0.04, by - fy * 0.04, tz + 0.24)
    p_mid = (bx - fx * 0.07 + o1[0], by - fy * 0.07 + o1[1], tz + 0.06 + o1[2])
    p_hem = (bx - fx * 0.09 + o2[0], by - fy * 0.09 + o2[1], tz - 0.18 + o2[2])

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

    # Barra dourada inferior
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

    # Brasão Mon dourado central
    mk.obox(c, p_mid, (-fx, -fy, 0.0), 0.018, 0.110, 0.110, P["haori_gold"], up=(0.0, 0.0, 1.0), outline=False)
    mk.obox(c, p_mid, (-fx, -fy, 0.0), 0.022, 0.068, 0.068, P["haori_dark"], up=(0.0, 0.0, 1.0), outline=False)


def draw_legs(c):
    """
    Pernas monumentais de Rikishi com adaptação biomecânica a todas as posturas:
    - Sonkyo (Agachamento sagrado nos artelhos com joelhos abertos).
    - Shiko Raise (Elevação lateral da perna a 90°).
    - Tachiai Charge (Inclinação frontal e passadas em arremetida).
    """
    P = pal()
    trail, amp, freq = mk.motion(c, 0.030)
    extra = getattr(c, "extra_props", None) or {}
    pose = extra.get("pose", "")

    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.70 * sign, trail, (c.px, c.py), amp=amp * 0.3, freq=freq)

        if pose == "sonkyo_squat":
            # Agachamento profundo Sonkyo: joelhos projetados para os lados, calcanhares erguidos
            top = (th[0] + c.px * sign * 0.08, th[1] + c.py * sign * 0.08, c.pelvis_z + 0.02)
            knee = (th[0] + c.px * sign * 0.22 + c.fx * 0.10, th[1] + c.py * sign * 0.22 + c.fy * 0.10, c.base_z + 0.16)
            cuff_pos = (th[0] + c.px * sign * 0.16 + c.fx * 0.05, th[1] + c.py * sign * 0.16 + c.fy * 0.05, c.base_z + 0.08)
            ankle = (foot[0] + c.px * sign * 0.08, foot[1] + c.py * sign * 0.08, foot[2])
        elif pose == "shiko_raise" and side == "R":
            # Perna direita erguida a 90° em Shiko cerimonial
            top = (th[0], th[1], th[2] + 0.22)
            knee = (c.base_x - c.px * 0.34, c.base_y - c.py * 0.34, c.pelvis_z + 0.28)
            cuff_pos = (c.base_x - c.px * 0.42, c.base_y - c.py * 0.42, c.pelvis_z + 0.34)
            ankle = (c.base_x - c.px * 0.48, c.base_y - c.py * 0.48, c.pelvis_z + 0.38)
        else:
            top = (th[0], th[1], th[2] + 0.22)
            knee = (sh[0] + o1[0] * 0.15, sh[1] + o1[1] * 0.15, sh[2] + 0.14)
            cuff_pos = (sh[0] + o1[0] * 0.10, sh[1] + o1[1] * 0.10, sh[2] + 0.06)
            ankle = (foot[0] + o2[0] * 0.10, foot[1] + o2[1] * 0.10, foot[2] + 0.02)

        # Coxa e canela maciças em malha 3D contínua
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos, ankle],
            widths=[0.148, 0.140, 0.122, 0.098],
            depth_thick=0.128,
            colors=[P["skin"], P["skin_shadow"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Pé descalço largo ancorado ao dohyo
        flen, fwidth = 0.145, 0.082
        mk.obox(c, (ankle[0] + c.fx * 0.015, ankle[1] + c.fy * 0.015, ankle[2]), (c.fx, c.fy, 0.0), flen, fwidth, 0.038, P["skin"])
        mk.obox(c, (ankle[0] + c.fx * 0.065, ankle[1] + c.fy * 0.065, ankle[2] + 0.005), (c.fx, c.fy, 0.0), 0.035, 0.076, 0.022, P["skin_shadow"], outline=False)


def draw_obi(c):
    """
    Grand Yokozuna Mawashi:
    - Faixa de seda escura espessa enrolada.
    - Corda Sagrada Shimenawa trançada em relevo frontal e lateral (Overhaul Fase 2).
    - Serpentinas Gohei de papel sagrado branco em zigue-zague pendentes (Overhaul Fase 2).
    - Cordões Sagari dourados rituais.
    """
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065
    pelvis_w = getattr(c, "pelvis_w", 0.35)
    extra = getattr(c, "extra_props", None) or {}
    legacy = bool(extra.get("legacy_mode", False))

    # 1. Faixa principal de seda pesada do Mawashi
    mk.cbox(c, bx, by, z, pelvis_w + 0.045, pelvis_w * 0.88, 0.090, P["mawashi"])

    # 2. Corda sagrada Shimenawa de Yokozuna (apenas na versão atualizada Overhaul)
    if not legacy:
        shime_pos = (bx + fx * 0.02, by + fy * 0.02, z + 0.01)
        mk.obox(c, shime_pos, (fx, fy, 0.0), pelvis_w * 0.90, pelvis_w + 0.065, 0.045, P["shimenawa"], up=(0.0, 0.0, 1.0), outline=True)
        mk.obox(c, (shime_pos[0] + fx * 0.01, shime_pos[1] + fy * 0.01, shime_pos[2]), (fx, fy, 0.0), pelvis_w * 0.86, pelvis_w + 0.045, 0.020, P["shimenawa_dark"], up=(0.0, 0.0, 1.0), outline=False)

    # 3. Serpentinas brancas Gohei rituais em zigue-zague pendendo da Shimenawa
    if mk.depth(c, fx, fy) > -0.15:
        if not legacy:
            for offset_x in (-0.08, -0.025, 0.025, 0.08):
                g_pos = (bx + fx * 0.135 + px * offset_x, by + fy * 0.135 + py * offset_x, z - 0.01)
                # Parte superior do zigue-zague
                mk.obox(c, g_pos, (0.0, 0.0, -1.0), 0.065, 0.042, 0.012, P["gohei"], up=(px, py, 0.0), outline=False)
                # Parte inferior do zigue-zague defasada
                mk.obox(c, (g_pos[0] + px * 0.012, g_pos[1] + py * 0.012, g_pos[2] - 0.050), (0.0, 0.0, -1.0), 0.060, 0.038, 0.012, P["gohei"], up=(px, py, 0.0), outline=False)
                mk.obox(c, (g_pos[0] - px * 0.010, g_pos[1] - py * 0.010, g_pos[2] - 0.095), (0.0, 0.0, -1.0), 0.055, 0.034, 0.012, P["gohei_shadow"], up=(px, py, 0.0), outline=False)

        # Cordões rituais Sagari descendo sob o Gohei / Mawashi
        sagari_pos = (bx + fx * 0.125, by + fy * 0.125, z - 0.025)
        mk.obox(c, sagari_pos, (0.0, 0.0, -1.0), 0.110, 0.120, 0.018, P["sagari"], up=(px, py, 0.0), outline=False)
        mk.obox(c, (sagari_pos[0], sagari_pos[1], sagari_pos[2] - 0.02), (0.0, 0.0, -1.0), 0.075, 0.045, 0.022, P["sagari_red"], up=(px, py, 0.0), outline=False)


def draw_torso(c):
    """
    Tronco Colossal de Raiden com manto cerimonial Haori carmesim e peitoral exposto:
    - Em Tachiai Tackle, aplica inclinação corporal de 35° à frente.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    torso_w = getattr(c, "torso_w", 0.36)
    extra = getattr(c, "extra_props", None) or {}
    pose = extra.get("pose", "")

    # Inclinação dinâmica em investida Tachiai
    lean_fwd = 0.0
    if pose in ("tackle", "tachiai_charge") or getattr(c, "state", "") == "TACHIAI_TACKLE":
        lean_fwd = 0.12

    # 1. Base do Tronco com Haori vermelho escuro
    mk.cbox(c, bx - fx * 0.015 + fx * lean_fwd, by - fy * 0.015 + fy * lean_fwd, tz + 0.08, torso_w + 0.05, torso_w * 0.74, 0.20, P["haori"])

    # 2. Jugo e manto sobre os ombros
    mk.cbox(c, bx - fx * 0.010 + fx * lean_fwd, by - fy * 0.010 + fy * lean_fwd, tz + 0.20, torso_w + 0.14, torso_w * 0.78, 0.075, P["haori"])

    # 3. Gola cerimonial alta com debrum dourado
    collar_pos = (bx - fx * 0.035 + fx * lean_fwd, by - fy * 0.035 + fy * lean_fwd, tz + 0.24)
    mk.obox(c, collar_pos, (fx, fy, 0.0), 0.065, 0.170, 0.045, P["haori_gold"], up=(0.0, 0.0, 1.0), outline=False)
    mk.obox(c, (collar_pos[0] + fx * 0.012, collar_pos[1] + fy * 0.012, collar_pos[2]), (fx, fy, 0.0), 0.055, 0.155, 0.040, P["haori_dark"], up=(0.0, 0.0, 1.0), outline=False)

    # 4. Capas dos ombros
    for s in (-1.0, 1.0):
        sh_pos = (bx + px * 0.180 * s + fx * lean_fwd, by + py * 0.180 * s + fy * lean_fwd, tz + 0.19)
        mk.obox(c, sh_pos, (0.0, 0.0, -1.0), 0.135, 0.130, 0.110, P["haori"], up=(fx, fy, 0.0), outline=True)
        mk.obox(c, (sh_pos[0], sh_pos[1], sh_pos[2] + 0.020), (0.0, 0.0, -1.0), 0.125, 0.125, 0.020, P["haori_gold"], up=(fx, fy, 0.0), outline=False)
        mk.obox(c, (sh_pos[0] + px * 0.048 * s, sh_pos[1] + py * 0.048 * s, sh_pos[2]), (px * s, py * s, 0.0), 0.012, 0.046, 0.046, P["haori_gold"], up=(0.0, 0.0, 1.0), outline=False)

    # 5. Peitoral e ventre musculoso expostos na abertura frontal em V
    if mk.depth(c, fx, fy) > -0.15:
        chest_pos = (bx + fx * 0.060 + fx * lean_fwd, by + fy * 0.060 + fy * lean_fwd, tz + 0.10)
        mk.obox(c, chest_pos, (fx, fy, 0.0), 0.065, 0.185, 0.165, P["skin"], up=(0.0, 0.0, 1.0), outline=False)
        mk.obox(c, (bx + fx * 0.095 + fx * lean_fwd, by + fy * 0.095 + fy * lean_fwd, tz + 0.14), (fx, fy, 0.0), 0.045, 0.175, 0.082, P["skin_shadow"], up=(0.0, 0.0, 1.0), outline=False)
        mk.obox(c, (bx + fx * 0.105 + fx * lean_fwd, by + fy * 0.105 + fy * lean_fwd, tz + 0.14), (fx, fy, 0.0), 0.025, 0.015, 0.075, P["skin_shadow"], up=(0.0, 0.0, 1.0), outline=False)

    # 6. Lapelas frontais do Haori com orla dourada e brasões Mon
    if mk.depth(c, fx, fy) > -0.05:
        for s in (-1.0, 1.0):
            lapel_anchor = (bx + fx * 0.085 + px * 0.125 * s + fx * lean_fwd, by + fy * 0.085 + py * 0.125 * s + fy * lean_fwd, tz + 0.20)
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
            mk.obox(c, (p_mid[0] - px * 0.030 * s, p_mid[1] - py * 0.030 * s, p_mid[2]), (0.0, 0.0, -1.0), 0.17, 0.022, 0.028, P["haori_gold"], up=(fx, fy, 0.0), outline=False)
            mk.obox(c, (p_top[0], p_top[1], p_top[2] - 0.025), (fx, fy, 0.0), 0.015, 0.044, 0.044, P["haori_gold"], up=(0.0, 0.0, 1.0), outline=False)
            mk.obox(c, (p_mid[0], p_mid[1], p_mid[2] - 0.020), (fx, fy, 0.0), 0.015, 0.038, 0.038, P["haori_gold"], up=(0.0, 0.0, 1.0), outline=False)

    # 7. Manto dorsal do Haori
    if mk.depth(c, -fx, -fy) > -0.05:
        _render_haori_back(c, P)


def draw_arm(c, shoulder, hand, side):
    """Braço monumental de Rikishi com manga de seda no bíceps, antebraço espesso e palma ampla."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.19)
    h = (hand[0], hand[1], hand[2] - 0.060)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.035), (0.0, 0.0, -0.025))

    # Manga do Haori no terço superior do braço
    mk.limb(c, s, e, 0.096, P["haori"], w_end=0.084)
    # Borda de brocado dourado na boca da manga
    mk.obox(c, e, (c.fx, c.fy, 0.0), 0.088, 0.088, 0.024, P["haori_gold"], outline=False)

    # Antebraço maciço de pele firme de rikishi
    mk.limb(c, e, h, 0.078, P["skin"], w_end=0.068)

    # Palma aberta maciça de Sumô
    h_box = (h[0], h[1], h[2] - 0.020)
    mk.cbox(c, h_box[0], h_box[1], h_box[2], 0.072, 0.072, 0.062, P["skin"])
    fwd_x = h_box[0] + c.fx * 0.035
    fwd_y = h_box[1] + c.fy * 0.035
    mk.obox(c, (fwd_x, fwd_y, h_box[2]), (c.fx, c.fy, 0.0), 0.040, 0.065, 0.042, P["skin_shadow"], up=(0.0, 0.0, 1.0), outline=False)

    return s, e


def draw_sleeves(c, arms):
    """Mangas amplas do Haori de seda vermelho escuro drapeando a partir dos ombros."""
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
    Cabeça Esculpida HD de Raiden:
    - Calota craniana robusta com topete Oicho-mage em leque tradicional de Yokozuna.
    - Cordão de papel branco ritual Motoyui.
    - Olhar marcial estóico e intimidador via `draw_portrait_face_3d`.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    hw = getattr(c, "head_w", 0.165)
    extra = getattr(c, "extra_props", None) or {}
    pose = extra.get("pose", "")

    lean_fwd = 0.08 if (pose in ("tackle", "tachiai_charge") or getattr(c, "state", "") == "TACHIAI_TACKLE") else 0.0

    # 1. Calota craniana e cabelos negros
    cran_top = (bx - fx * 0.015 + fx * lean_fwd, by - fy * 0.015 + fy * lean_fwd, hz + 0.175)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx + fx * lean_fwd, by + fy * lean_fwd, hz + 0.130), cran_top,
        w_start=hw * 1.05, h_start=hw * 1.05,
        w_end=hw * 0.75, h_end=hw * 0.75,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # 2. Coque tradicional de Sumô (Oicho-mage) com expansão em leque de ginkgo
    bun_base = (bx - fx * 0.025 + fx * lean_fwd, by - fy * 0.025 + fy * lean_fwd, hz + 0.170)
    bun_fan = (bx + fx * 0.015 + fx * lean_fwd, by + fy * 0.015 + fy * lean_fwd, hz + 0.238)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        bun_base, bun_fan,
        w_start=0.068, h_start=0.068,
        w_end=0.086, h_end=0.048,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )
    # Cordão de papel branco Motoyui
    mk.obox(c, bun_base, (0.0, 0.0, 1.0), 0.026, 0.068, 0.068, P["motoyui"], up=(fx, fy, 0.0), outline=False)

    # 3. Rosto marcial masculino 3D low-poly estilizado
    if not getattr(c, "_face_drawn", False):
        draw_portrait_face_3d(c, char_type="raiden")
        c._face_drawn = True


def _render_palm_effects(c, hand_l, hand_r):
    """Renderiza auras de choque Tsuppari, linhas de velocidade Tachiai e pó de sal."""
    P = pal()
    extra = getattr(c, "extra_props", None) or {}
    pose = extra.get("pose", "")

    # 1. Efeito de investida Tachiai (Linhas de velocidade sísmica e poeira)
    if pose in ("tackle", "tachiai_charge") or getattr(c, "state", "") == "TACHIAI_TACKLE":
        rx, ry, rz = hand_r
        mk.cbox(c, rx + c.fx * 0.08, ry + c.fy * 0.08, rz, 0.18, 0.18, 0.18, P["shock_dust"], outline=False)
        mk.cbox(c, rx + c.fx * 0.12, ry + c.fy * 0.12, rz, 0.10, 0.10, 0.10, P["speed_line"], outline=False)
        return

    # 2. Efeito de Palma Tsuppari
    if (c.is_melee and c.atk_progress is not None and 0.20 <= c.atk_progress <= 0.82) or getattr(c, "state", "") in ("TSUPPARI_RUSH", "TSUPPARI_STRIKE_1", "TSUPPARI_STRIKE_2"):
        rx, ry, rz = hand_r
        mk.cbox(c, rx, ry, rz, 0.16, 0.16, 0.16, P["palm_aura"], outline=False)
        mk.cbox(c, rx, ry, rz, 0.08, 0.08, 0.08, P["palm_core"], outline=False)

        if pose == "tsuppari_2":
            lx, ly, lz = hand_l
            mk.cbox(c, lx, ly, lz, 0.16, 0.16, 0.16, P["palm_aura"], outline=False)
            mk.cbox(c, lx, ly, lz, 0.08, 0.08, 0.08, P["palm_core"], outline=False)


def draw_front(c, hand_l, hand_r):
    """Camada frontal com efeitos de palma ou poeira de sal cerimonial."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_palm_effects(c, hand_l, hand_r)
