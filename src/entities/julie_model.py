"""
Julie, a Nobre Mosqueteira da Guarda Real:
- Rosto anime delicado com resplandecentes olhos azul-safira, brilho duplo e cílios alados; nariz feminino esguio e lábios rosa-veludo.
- Cabelo castanho-acobreado em corte nobre com franja acima das sobrancelhas, mechas emoldurando a face e trança elegante com laço azul.
- Autêntico Chapéu Cavalier do séc. XVII em veludo azul-real com aba esquerda dobrada para cima (cocked brim), broche Flor-de-lis de ouro e majestosa pluma branca de avestruz em arco 3D fluido.
- Túnica azul-real com botões dourados, gola de renda francesa Jabot em camadas e mangas bufantes com punhos de renda.
- Calça cinza de esgrima justa em malha 3D contínua entrando em botas altas de couro com cano dobrado (sem degraus nos joelhos).
- Capa azul-real drapeada em fita 3D contínua com bordado dourado na barra e rodopio acrobático no golpe CAPE_FLOURISH.
- Florete de duelo com lâmina delgada de aço temperado, guarda em concha dourada com quillons e bainha de couro no quadril.
- Ordenação dinâmica de profundidade 3D (Painter's Algorithm) com oclusão limpa de costas (180°).
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

PALETTE = {
    "blue": (28, 68, 165),
    "blue_dark": (18, 45, 115),
    "cape": (32, 74, 175),
    "cape_dark": (20, 50, 125),
    "gold": (235, 195, 65),
    "lace": (250, 248, 242),
    "lace_dark": (218, 215, 210),
    "skin": (248, 224, 206),
    "skin_shadow": (218, 186, 168),
    "hair": (175, 72, 44),
    "hair_light": (215, 105, 68),
    "hair_dark": (125, 45, 26),
    "pants": (175, 180, 192),
    "pants_dark": (145, 150, 162),
    "boot": (88, 54, 30),
    "boot_cuff": (135, 88, 52),
    "leather": (105, 68, 38),
    "glove": (248, 246, 240),
    "hat": (26, 62, 150),
    "plume": (252, 252, 255),
    "plume_shade": (218, 226, 238),
    "steel": (220, 230, 245),
    "edge": (252, 254, 255),
    "guard": (235, 195, 65),
    "grip": (60, 40, 28),
    "aura": (150, 190, 255),
    "aura_core": (240, 248, 255),
}

MATERIALS = {
    "cape": "velvet", "cape_dark": "velvet",
    "blue": "brocade", "blue_dark": "velvet",
    "leather": "leather", "boot": "leather", "boot_cuff": "leather",
    "lace": "knit", "glove": "silk", "hat": "velvet",
    "pants": "silk", "steel": "steel", "gold": "gold"
}

LEGACY_MATERIALS = {k: "matte" for k in MATERIALS}


def pal() -> dict:
    return PALETTE


def _flourishing(c) -> bool:
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose") or getattr(c, "pose_name", None)
    return getattr(c, "state", "") == "CAPE_FLOURISH" or pose in ("cape_flourish", "flourish")


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Florete de Duelo
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """Postura nobre En Garde de esgrima clássica: mão direita sustentando o florete à frente, mão esquerda erguida em balanço."""
    tz = getattr(c, "torso_z", 0.40) + math.sin(getattr(c, "walk_timer", 0.0) * 2.8) * 0.010
    bx = getattr(c, "base_x", 0.0)
    by = getattr(c, "base_y", 0.0)
    fx = getattr(c, "fx", 1.0)
    fy = getattr(c, "fy", 0.0)
    px = getattr(c, "px", 0.0)
    py = getattr(c, "py", 1.0)
    right = (bx + fx * 0.16 + px * 0.04, by + fy * 0.16 + py * 0.04, tz + 0.12)
    left = (bx - fx * 0.08 - px * 0.14, by - fy * 0.08 - py * 0.14, tz + 0.18)
    return left, right


def attack_arms(c):
    """Estocada precisa (Fleche): braço direito estendido ao máximo para a frente, braço esquerdo esticado para trás."""
    p = getattr(c, "atk_progress", 0.0)
    if p is None:
        p = 0.0
    bx = getattr(c, "base_x", 0.0)
    by = getattr(c, "base_y", 0.0)
    tz = getattr(c, "torso_z", 0.40)
    fx = getattr(c, "fx", 1.0)
    fy = getattr(c, "fy", 0.0)
    px = getattr(c, "px", 0.0)
    py = getattr(c, "py", 1.0)
    reach = math.sin(p * math.pi) * 0.45
    right = (bx + fx * (0.26 + reach) - px * 0.04,
             by + fy * (0.26 + reach) - py * 0.04,
             tz + 0.16)
    left = (bx - fx * (0.18 + reach * 0.3) + px * 0.16,
            by - fy * (0.18 + reach * 0.3) + py * 0.16,
            tz + 0.22)
    return left, right


def _smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _hands(c):
    """Cinemática completa dos braços de Julie cobrindo as 12 poses de esgrima e sequências cinematográficas."""
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose") or getattr(c, "pose_name", None)
    state = getattr(c, "state", "IDLE")
    p = extra.get("p", 0.0)
    seg_u = extra.get("seg_u", p)
    tz = getattr(c, "torso_z", 0.40)
    bx = getattr(c, "base_x", 0.0)
    by = getattr(c, "base_y", 0.0)
    fx = getattr(c, "fx", 1.0)
    fy = getattr(c, "fy", 0.0)
    px = getattr(c, "px", 0.0)
    py = getattr(c, "py", 1.0)

    # 1. Intro - Roteiro Aristocrático da Guarda Real (3 Fases com C0 contínuo)
    if pose == "cavalier_hat_bow" or (state == "INTRO" and p < 0.35):
        u = _smooth(seg_u if pose == "cavalier_hat_bow" else min(1.0, max(0.0, p / 0.35)))
        p0_left = (bx + fx * 0.04 - px * 0.06, by + fy * 0.04 - py * 0.06, tz + 0.28)
        p0_right = (bx - px * 0.14 + fx * 0.02, by - py * 0.14 + fy * 0.02, tz + 0.08)
        p1_left = (bx + fx * 0.10 - px * 0.08, by + fy * 0.10 - py * 0.08, tz + 0.06)
        p1_right = (bx - px * 0.14 + fx * 0.02, by - py * 0.14 + fy * 0.02, tz + 0.08)
        left = mk.lerp(p0_left, p1_left, u)
        right = mk.lerp(p0_right, p1_right, u)
        return left, right

    if pose == "noble_reverence" or (state == "INTRO" and p < 0.70):
        u = seg_u if pose == "noble_reverence" else min(1.0, max(0.0, (p - 0.35) / 0.35))
        p1_left = (bx + fx * 0.10 - px * 0.08, by + fy * 0.10 - py * 0.08, tz + 0.06)
        p1_right = (bx - px * 0.14 + fx * 0.02, by - py * 0.14 + fy * 0.02, tz + 0.08)
        p2_left = (bx + fx * 0.14 - px * 0.08, by + fy * 0.14 - py * 0.08, tz + 0.06)
        p2_right = (bx - px * 0.14 + fx * 0.02, by - py * 0.14 + fy * 0.02, tz + 0.08)
        bow = math.sin(u * math.pi) * 0.08
        sm_u = _smooth(u)
        base_l = mk.lerp(p1_left, p2_left, sm_u)
        base_r = mk.lerp(p1_right, p2_right, sm_u)
        left = (base_l[0], base_l[1], base_l[2] - bow)
        right = (base_r[0], base_r[1], base_r[2] - bow)
        return left, right

    if pose == "en_garde" or (state == "INTRO" and p >= 0.70):
        u = _smooth(seg_u if pose == "en_garde" else min(1.0, max(0.0, (p - 0.70) / 0.30)))
        p2_left = (bx + fx * 0.14 - px * 0.08, by + fy * 0.14 - py * 0.08, tz + 0.06)
        p2_right = (bx - px * 0.14 + fx * 0.02, by - py * 0.14 + fy * 0.02, tz + 0.08)
        p3_left = (bx - px * 0.12 - fx * 0.06, by - py * 0.12 - fy * 0.06, tz + 0.14)
        p3_right = (bx + fx * 0.22 - px * 0.02, by + fy * 0.22 - py * 0.02, tz + 0.16)
        glo_p = float(extra.get("p", 0.70 + 0.30 * u))
        breathe = math.sin(glo_p * 12.0) * 0.008
        sway = math.cos(glo_p * 8.0) * 0.006
        cur_l = mk.lerp(p2_left, p3_left, u)
        cur_r = mk.lerp(p2_right, p3_right, u)
        left = (cur_l[0], cur_l[1] + sway, cur_l[2] + breathe)
        right = (cur_r[0] + sway, cur_r[1] - sway, cur_r[2] + breathe)
        return left, right

    # 2. Vitória - Roteiro Aristocrático da Guarda Real (3 Fases com C0 contínuo)
    if pose == "blind_sheath" or (state in ("VICTORY", "VICTORY_SHORT") and p < 0.35):
        u = _smooth(seg_u if pose == "blind_sheath" else min(1.0, max(0.0, p / 0.35)))
        v0_left = (bx - px * 0.14 - fx * 0.04, by - py * 0.14 - fy * 0.04, tz + 0.05)
        v0_right = (bx + fx * 0.20 - px * 0.02, by + fy * 0.20 - py * 0.02, tz + 0.16)
        v1_left = (bx - px * 0.14 - fx * 0.04, by - py * 0.14 - fy * 0.04, tz + 0.05)
        v1_right = (bx - px * 0.12 - fx * 0.02, by - py * 0.12 - fy * 0.02, tz + 0.07)
        arc = math.sin(u * math.pi) * 0.10
        base_r = mk.lerp(v0_right, v1_right, u)
        right = (base_r[0] - arc * 0.08,
                 base_r[1] - arc * 0.08,
                 base_r[2] + arc * 0.06)
        left = mk.lerp(v0_left, v1_left, u)
        return left, right

    if pose == "adjust_glove_flintlock" or (state in ("VICTORY", "VICTORY_SHORT") and p < 0.70):
        u = _smooth(seg_u if pose == "adjust_glove_flintlock" else min(1.0, max(0.0, (p - 0.35) / 0.35)))
        v1_left = (bx - px * 0.14 - fx * 0.04, by - py * 0.14 - fy * 0.04, tz + 0.05)
        v1_right = (bx - px * 0.12 - fx * 0.02, by - py * 0.12 - fy * 0.02, tz + 0.07)
        v2_left = (bx + fx * 0.10 - px * 0.04, by + fy * 0.10 - py * 0.04, tz + 0.18)
        v2_right = (bx + fx * 0.04 + px * 0.02, by + fy * 0.04 + py * 0.02, tz + 0.14)
        left = mk.lerp(v1_left, v2_left, u)
        right = mk.lerp(v1_right, v2_right, u)
        return left, right

    if pose == "blow_smoke_smirk" or (state in ("VICTORY", "VICTORY_SHORT") and p >= 0.70):
        u = _smooth(seg_u if pose == "blow_smoke_smirk" else min(1.0, max(0.0, (p - 0.70) / 0.30)))
        v2_left = (bx + fx * 0.10 - px * 0.04, by + fy * 0.10 - py * 0.04, tz + 0.18)
        v2_right = (bx + fx * 0.04 + px * 0.02, by + fy * 0.04 + py * 0.02, tz + 0.14)
        v3_left = (bx + fx * 0.08 - px * 0.02, by + fy * 0.08 - py * 0.02, tz + 0.26)
        v3_right = (bx + px * 0.14 - fx * 0.02, by + py * 0.14 - fy * 0.02, tz + 0.06)
        glo_p = float(extra.get("p", 0.70 + 0.30 * u))
        breathe = math.cos(glo_p * 12.0) * 0.008
        sway = math.sin(glo_p * 8.0) * 0.006
        cur_l = mk.lerp(v2_left, v3_left, u)
        cur_r = mk.lerp(v2_right, v3_right, u)
        left = (cur_l[0], cur_l[1] + sway, cur_l[2] + breathe)
        right = (cur_r[0] - sway, cur_r[1] - sway, cur_r[2] + breathe * 0.5)
        return left, right

    # 3. Finishers A & B (Hyakka Rantotsu & Zero-Kyori Juusatsu)
    if pose in ("finisher_a", "hyakka_rantotsu") or state in ("FINISHER_A", "HYAKKA_RANTOTSU") or extra.get("is_flurry"):
        clock = float(extra.get("flurry_clock", p * 2.0 if p else getattr(c, "atk_progress", 0.0) * 2.0))
        # Velocidade moderada e claramente visível de estocadas (7.0Hz em pistão)
        thrust_cycle = math.sin(clock * 7.0 * math.tau)
        thrust_reach = 0.20 + 0.30 * max(0.0, thrust_cycle)  # avanço de lâmina entre 0.20m e 0.50m
        # Dispersão geométrica atingindo múltiplos pontos vitais no tronco (coração, esterno, costelas)
        spread_p = math.sin(clock * 4.2 * math.tau) * 0.07
        spread_z = math.cos(clock * 5.5 * math.tau) * 0.06
        right = (bx + fx * (0.20 + thrust_reach) + px * (-0.03 + spread_p),
                 by + fy * (0.20 + thrust_reach) + py * (-0.03 + spread_p),
                 tz + 0.16 + spread_z)
        # Braço esquerdo mantendo postura nobre de esgrima com micro-ondulação
        flourish_sway = math.cos(clock * 3.5 * math.tau) * 0.025
        left = (bx - fx * (0.16 + flourish_sway) + px * (0.18 + flourish_sway),
                by - fy * (0.16 + flourish_sway) + py * (0.18 + flourish_sway),
                tz + 0.24 + flourish_sway * 0.5)
        return left, right

    if state in ("FINISHER_B", "ZERO_KYORI_JUUSATSU") or pose in ("finisher_b", "zero_kyori_juusatsu"):
        # Zero-Kyori Juusatsu: fuzilamento à queima-roupa com pederneira
        left = (bx + fx * 0.24 - px * 0.02, by + fy * 0.24 - py * 0.02, tz + 0.17)
        right = (bx - fx * 0.12 + px * 0.16, by - fy * 0.12 + py * 0.16, tz + 0.12)
        return left, right

    # 4. Ataque Primário (Fleche Thrust)
    if state in ("ATTACK", "FLECHE") or pose == "attack":
        return attack_arms(c)

    # 4. Ação Secundária (Floreio de Capa / Chute Coup de Pied)
    if state == "CAPE_FLOURISH" or pose in ("cape_flourish", "flourish"):
        flourish_p = extra.get("p", 0.5)
        arc = math.sin(flourish_p * math.pi)
        right = (bx + fx * (0.14 - arc * 0.08) - px * 0.12, by + fy * (0.14 - arc * 0.08) - py * 0.12, tz + 0.10 - arc * 0.04)
        left = (bx + fx * (0.16 + arc * 0.12) + px * (0.12 + arc * 0.14), by + fy * (0.16 + arc * 0.12) + py * (0.12 + arc * 0.14), tz + 0.14 + arc * 0.16)
        return left, right

    # 5. Disparo de Pederneira (Flintlock Shot)
    if state in ("FLINTLOCK", "FLINTLOCK_SHOT") or pose in ("flintlock", "shot"):
        left = (bx + fx * 0.28 - px * 0.02, by + fy * 0.28 - py * 0.02, tz + 0.18)
        right = (bx - fx * 0.10 + px * 0.14, by - fy * 0.10 + py * 0.14, tz + 0.12)
        return left, right

    # 6. Esquiva (Cape Swirl Backhop)
    if state in ("DODGE", "ROLL", "STATE_ROLL", "DASH", "CAPE_SWIRL") or pose in ("cape_swirl_backhop", "dodge", "roll"):
        prog = extra.get("roll_prog", p if p is not None else 0.5)
        tuck = math.sin(prog * math.pi)
        right = (bx + fx * (0.10 - tuck * 0.06) + px * (0.08 + tuck * 0.06),
                 by + fy * (0.10 - tuck * 0.06) + py * (0.08 + tuck * 0.06),
                 tz + 0.10 - tuck * 0.16)
        left = (bx - fx * (0.06 + tuck * 0.08) - px * (0.12 + tuck * 0.08),
                by - fy * (0.06 + tuck * 0.08) - py * (0.12 + tuck * 0.08),
                tz + 0.14 + tuck * 0.12)
        return left, right

    # 7. Defesa / Parry
    if state in ("PARRY", "STATE_PARRY", "GUARD") or pose == "parry":
        right = (bx + fx * 0.18 - px * 0.02, by + fy * 0.18 - py * 0.02, tz + 0.16)
        left = (bx - fx * 0.08 - px * 0.14, by - fy * 0.08 - py * 0.14, tz + 0.20)
        return left, right

    # 9. Reação a Golpe / Flinch / Stun
    if state in ("STUNNED", "FLINCH", "HIT") or pose in ("hit", "flinch"):
        right = (bx - fx * 0.12 + px * 0.16, by - fy * 0.12 + py * 0.16, tz + 0.08)
        left = (bx + fx * 0.06 - px * 0.12, by + fy * 0.06 - py * 0.12, tz + 0.24)
        return left, right

    # Padrão: corrida ou repouso
    if getattr(c, "is_moving", False) and hasattr(c, "walk_timer"):
        sw = math.sin(c.walk_timer * 7.5) * 0.035
        right = (bx + fx * 0.10 + px * 0.06 + fx * sw, by + fy * 0.10 + py * 0.06 + fy * sw, tz + 0.04)
        left = (bx - fx * 0.06 - px * 0.12 - fx * sw, by - fy * 0.06 - py * 0.12 - fy * sw, tz + 0.08)
        return left, right

    return idle_arms(c)


def _current_hands(c):
    return _hands(c)


def get_arms(c):
    """Exposição modular da cinemática dos braços para sincronização com o renderizador humanoide."""
    return _current_hands(c)


# ---------------------------------------------------------------------------------------------------------------------
# Florete de Duelo 3D (Rapier)
# ---------------------------------------------------------------------------------------------------------------------

def _draw_rapier(c, hand, d, length):
    """Florete de corte e estocada com lâmina delgada, guarda em concha dourada com gavilanes e pomo trabalhado."""
    P = pal()
    # Empunhadura de couro trabalhado
    mk.obox(c, mk.add(hand, d, -0.09), d, 0.11, 0.030, 0.030, P["grip"])
    # Pomo dourado
    mk.obox(c, mk.add(hand, d, -0.10), d, 0.020, 0.042, 0.042, P["gold"], outline=False)
    # Guarda em concha (cazoleta) dourada estilizada
    mk.obox(c, mk.add(hand, d, 0.02), d, 0.024, 0.080, 0.068, P["guard"])
    # Quillons cruzados (gavilanes)
    mk.obox(c, mk.add(hand, d, 0.02), (c.px, c.py, 0.0), 0.140, 0.016, 0.016, P["guard"], outline=False)
    # Lâmina delgada de aço temperado
    mk.obox(c, mk.add(hand, d, 0.04), d, length, 0.024, 0.022, P["steel"])
    mk.obox(c, mk.add(hand, d, 0.05), d, length - 0.02, 0.010, 0.024, P["edge"], outline=False)
    return mk.add(hand, d, 0.04 + length)


def _draw_weapons(c, hand_l, hand_r):
    P = pal()
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose") or getattr(c, "pose_name", None)
    state = getattr(c, "state", "IDLE")
    p = extra.get("p", 0.0)
    seg_u = extra.get("seg_u", p)
    hand = hand_r
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    # 1. Floreio de Capa (Cape Flourish) e Chute Coup de Pied
    if _flourishing(c):
        t = max(0.0, min(1.0, 1.0 - getattr(c, "state_timer", 0.0) / 0.16)) if getattr(c, "state_timer", None) else seg_u
        a = t * math.pi * 2.2
        cf = (fx * math.cos(a) + px * math.sin(a), fy * math.cos(a) + py * math.sin(a))
        # Capa rodopiando em arco
        mk.obox(c, (bx + cf[0] * 0.20, by + cf[1] * 0.20, c.torso_z + 0.06), (cf[0], cf[1], -0.15), 0.50, 0.22, 0.035, P["cape"], up=(0.0, 0.0, 1.0))
        mk.obox(c, (bx + cf[0] * 0.20, by + cf[1] * 0.20, c.torso_z + 0.06), (cf[0], cf[1], -0.15), 0.50, 0.22, 0.010, P["gold"], up=(0.0, 0.0, 1.0), outline=False)
        # Chute acrobático alto
        kick = c.pelvis_z - 0.10
        mk.obox(c, (bx + fx * 0.18, by + fy * 0.18, kick), (fx, fy, 0.10), 0.38, 0.08, 0.08, P["pants"])
        mk.obox(c, (bx + fx * 0.36, by + fy * 0.36, kick + 0.02), (fx, fy, 0.10), 0.14, 0.09, 0.09, P["boot"])

    # 2. Chapéu Cavalier seguro na mão esquerda durante a reverência aristocrática
    if pose in ("cavalier_hat_bow", "noble_reverence") or (state == "INTRO" and p < 0.70):
        hat_pos = (hand_l[0], hand_l[1], hand_l[2] - 0.02)
        mk.cbox(c, hat_pos[0], hat_pos[1], hat_pos[2], 0.120, 0.120, 0.045, P["hat"])
        mk.cbox(c, hat_pos[0], hat_pos[1], hat_pos[2] + 0.025, 0.090, 0.090, 0.035, P["gold"], outline=False)
        # Pluma branca arqueando do chapéu na mão
        mk.obox(c, (hat_pos[0] + px * 0.06, hat_pos[1] + py * 0.06, hat_pos[2] + 0.02), (px, py, 0.3), 0.140, 0.030, 0.018, P["plume"], outline=False)

    # 3. Pistola de Pederneira de Bolso na mão esquerda (Vitória, Disparo ou Finisher B)
    if pose in ("adjust_glove_flintlock", "blow_smoke_smirk", "flintlock") or state in ("FLINTLOCK", "FLINTLOCK_SHOT", "FINISHER_B") or (state in ("VICTORY", "VICTORY_SHORT") and p >= 0.35):
        pistol_pos = hand_l
        mk.obox(c, pistol_pos, (fx, fy, 0.0), 0.105, 0.028, 0.036, P["leather"])
        mk.obox(c, mk.add(pistol_pos, (fx, fy, 0.0), 0.05), (fx, fy, 0.0), 0.080, 0.020, 0.020, P["steel"], outline=False)
        mk.obox(c, mk.add(pistol_pos, (fx, fy, 0.0), 0.02), (0.0, 0.0, 1.0), 0.022, 0.014, 0.030, P["gold"], outline=False)
        # Fumaça aromática de pólvora saindo do cano
        if pose in ("blow_smoke_smirk", "adjust_glove_flintlock") or (state in ("VICTORY", "VICTORY_SHORT") and p >= 0.50):
            tip = mk.add(pistol_pos, (fx, fy, 0.0), 0.12)
            mk.cbox(c, tip[0], tip[1], tip[2] + 0.02, 0.026, 0.026, 0.035, (225, 230, 240), outline=False)

    # 4. Estocada / Finisher A (Hyakka Rantotsu: barragem de florete)
    if pose in ("finisher_a", "hyakka_rantotsu") or state in ("FINISHER_A", "HYAKKA_RANTOTSU") or extra.get("is_flurry"):
        clock = float(extra.get("flurry_clock", p * 2.0 if p else getattr(c, "atk_progress", 0.0) * 2.0))
        spread_p = math.sin(clock * 4.2 * math.tau) * 0.07
        spread_z = math.cos(clock * 5.5 * math.tau) * 0.06
        d = mk.norm((fx + px * spread_p * 1.5, fy + py * spread_p * 1.5, spread_z * 1.5))
        _draw_rapier(c, hand, d, 0.82)
        # Rastros múltiplos estroboscópicos da lâmina transpassando o ar
        for j in range(1, 5):
            back = mk.add(hand, d, -0.09 * j)
            fade = 1.0 - j / 5.0
            side = (px * 0.04, py * 0.04, 0.0)
            a0, a1 = mk.add(back, d, 0.25), mk.add(back, d, 0.95)
            mk.band(c, (a0, a1, mk.add(a1, side, 1.0), mk.add(a0, side, 1.0)), P["aura"] + (int(210 * fade),))
        return

    # 5. Estocada Melee Normal (Fleche)
    if c.is_melee or state in ("ATTACK", "FLECHE") or pose == "attack":
        prog = getattr(c, "atk_progress", 0.0) or 0.0
        info = calc_blade_slash_3d("musketeer", "ATTACK", prog, bx, by, c.torso_z, fx, fy, px, py)
        d, length = mk.norm(tuple(info["dir"])), 0.78
        _draw_rapier(c, hand, d, length)

        # Rastro luminoso etéreo durante estocada
        if prog >= 0.20:
            for j in range(1, 4):
                back = mk.add(hand, d, -0.12 * j)
                fade = 1.0 - j / 4.0
                side = (px * 0.035, py * 0.035, 0.0)
                a0, a1 = mk.add(back, d, 0.35), mk.add(back, d, length + 0.10)
                mk.band(c, (a0, a1, mk.add(a1, side, 1.0), mk.add(a0, side, 1.0)), P["aura"] + (int(190 * fade),))
        return

    # 5. Embainhar às cegas na vitória (Fase 1)
    if pose == "blind_sheath" or (state in ("VICTORY", "VICTORY_SHORT") and p < 0.35):
        # Lâmina deslizando para dentro da bainha no quadril
        d = mk.norm((-fx * 0.40 - px * 0.40, -fy * 0.40 - py * 0.40, -0.70))
        _draw_rapier(c, hand, d, 0.45)
        return

    # 6. Modo padrão de locomoção / guarda
    if c.is_moving:
        d = mk.norm((fx * 0.30, fy * 0.30, -0.75))
    else:
        d = mk.norm((fx * 0.82 + px * 0.10, fy * 0.82 + py * 0.10, 0.08))
    _draw_rapier(c, hand, d, 0.72 if not c.is_moving else 0.68)


# ---------------------------------------------------------------------------------------------------------------------
# Cabelo com Trança Lateral & Majestoso Chapéu Cavalier
# ---------------------------------------------------------------------------------------------------------------------

def _lock_is_behind(c, side_sign):
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    lx = bx + fx * 0.02 + px * 0.065 * side_sign
    ly = by + fy * 0.02 + py * 0.065 * side_sign
    return mk.depth(c, lx, ly) < mk.depth(c, bx, by) - 0.008


def _side_lock(c, side_sign):
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.06)
    o = mk.cloth_offsets(c, 1, 0.8 * side_sign, trail, amp * 1.2, freq * 1.1, (bx, by))[0]

    p0 = (bx + fx * 0.040 + px * 0.048 * side_sign, by + fy * 0.040 + py * 0.048 * side_sign, hz + 0.135)
    p1 = (bx + fx * 0.044 + px * 0.052 * side_sign + o[0] * 0.4, by + fy * 0.044 + py * 0.052 * side_sign + o[1] * 0.4, hz + 0.070)
    p2 = (bx + fx * 0.046 + px * 0.048 * side_sign + o[0], by + fy * 0.046 + py * 0.048 * side_sign + o[1], hz + 0.005 + o[2])

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


def _draw_braid(c):
    """Trança nobre descendo suavemente sobre o ombro esquerdo com laço azul."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.06)

    root = (bx - px * 0.060 - fx * 0.025, by - py * 0.060 - fy * 0.025, hz + 0.080)
    o1 = mk.cloth_offsets(c, 1, 0.6, trail, amp * 1.3, freq, root)[0]
    mid = (root[0] - px * 0.020 + fx * 0.040 + o1[0] * 0.5,
           root[1] - py * 0.020 + fy * 0.040 + o1[1] * 0.5,
           c.torso_z + 0.180 + o1[2] * 0.5)
    tip = (mid[0] + fx * 0.020 + o1[0],
           mid[1] + fy * 0.020 + o1[1],
           c.torso_z + 0.070 + o1[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[root, mid, tip],
        widths=[0.028, 0.024, 0.016],
        depth_thick=0.018,
        colors=[P["hair"], P["hair_light"], P["hair_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )
    # Laço azul na ponta da trança
    mk.cbox(c, tip[0], tip[1], tip[2] - 0.010, 0.026, 0.026, 0.018, P["blue"], outline=False)


def _draw_cavalier_hat(c):
    """
    Autêntico Chapéu Cavalier do séc. XVII:
    - Copa afunilada assente acima da testa (hz + 0.145).
    - Aba assimétrica elegante: aba esquerda dobrada para cima (cocked brim) com debrum de ouro.
    - Broche Flor-de-lis de ouro prendendo a dobra.
    - Majestosa e volumosa pluma branca de avestruz em arco 3D fluido que se ergue alta e arqueia graciosamente para trás.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    crown_z = hz + 0.145

    # 1. Copa do chapéu (crown)
    mk.cbox(c, bx - fx * 0.015, by - fy * 0.015, crown_z + 0.025, 0.125, 0.125, 0.050, P["hat"])
    # Faixa dourada elegante de couro/tecido
    mk.cbox(c, bx - fx * 0.015, by - fy * 0.015, crown_z + 0.010, 0.134, 0.134, 0.018, P["gold"], outline=False)

    # 2. Abas Cavalier assimétricas (acima dos olhos e sobrancelhas, sem Z-drop no rosto!)
    # Aba Frontal horizontal rente ao topo da testa
    mk.obox(c, (bx + fx * 0.050, by + fy * 0.050, crown_z), (fx, fy, 0.0), 0.055, 0.140, 0.014, P["hat"], up=(0.0, 0.0, 1.0))

    # Aba Lateral Direita horizontal com leve caimento suave
    mk.obox(c, (bx - px * 0.055, by - py * 0.055, crown_z), (-px, -py, 0.0), 0.060, 0.135, 0.014, P["hat"], up=(0.0, 0.0, 1.0))

    # Aba Traseira sobre a nuca
    mk.obox(c, (bx - fx * 0.050, by - fy * 0.050, crown_z), (-fx, -fy, 0.0), 0.055, 0.135, 0.014, P["hat"], up=(0.0, 0.0, 1.0))

    # 3. Aba Lateral Esquerda Dobrada para Cima (Cocked Brim)
    dir_cocked = mk.norm((px * 0.15, py * 0.15, 0.98))
    pos_cocked = (bx + px * 0.065, by + py * 0.065, crown_z)
    mk.obox(c, pos_cocked, dir_cocked, 0.095, 0.135, 0.018, P["hat"], up=(fx, fy, 0.0))

    # Debrum de ouro bordado no topo da aba dobrada
    mk.obox(c, (pos_cocked[0], pos_cocked[1], crown_z + 0.095), (fx, fy, 0.0), 0.135, 0.014, 0.014, P["gold"], outline=False)

    # Broche Flor-de-lis dourado prendendo a aba
    mk.cbox(c, bx + px * 0.078 + fx * 0.010, by + py * 0.078 + fy * 0.010, crown_z + 0.045, 0.028, 0.028, 0.028, P["gold"], outline=True)

    # 4. Majestosa Pluma de Avestruz Branca 3D em Arco Fluido
    trail, amp, freq = mk.motion(c, 0.07)
    plume_root = (bx + px * 0.070 + fx * 0.010, by + py * 0.070 + fy * 0.010, crown_z + 0.050)
    o1 = mk.cloth_offsets(c, 1, 0.5, trail, amp * 1.5, freq, plume_root)[0]

    # Arco fluido que sobe além da copa e curva graciosamente para trás
    p_high = (plume_root[0] - fx * 0.030 - px * 0.010, plume_root[1] - fy * 0.030 - py * 0.010, crown_z + 0.140)
    p_mid = (plume_root[0] - fx * 0.100 - px * 0.030 + o1[0] * 0.5, plume_root[1] - fy * 0.100 - py * 0.030 + o1[1] * 0.5, crown_z + 0.120 + o1[2] * 0.5)
    p_tip = (plume_root[0] - fx * 0.170 - px * 0.050 + o1[0], plume_root[1] - fy * 0.170 - py * 0.050 + o1[1], crown_z + 0.060 + o1[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[plume_root, p_high, p_mid, p_tip],
        widths=[0.025, 0.042, 0.038, 0.018],
        depth_thick=0.016,
        colors=[P["plume"], P["plume"], P["plume_shade"]],
        side_vec=(px, py, 0.0),
        normal_vec=(0.0, 0.0, 1.0),
        outline=False,
        alpha=c.alpha,
    )


# ---------------------------------------------------------------------------------------------------------------------
# Capa de Nobre (Costas)
# ---------------------------------------------------------------------------------------------------------------------

def _draw_cape(c):
    """Capa azul-real drapeada em fita 3D contínua com debrum e bordados de ouro na barra."""
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.06)

    anchor = (bx - fx * 0.105, by - fy * 0.105, tz + 0.24)
    offs = cloth.chain_offsets(2, c.walk_timer, 0.0, trail, (px, py), amp=amp * 1.5, freq=freq, wind=cloth.wind_at(bx, by))

    p1 = (anchor[0] + offs[0][0], anchor[1] + offs[0][1], tz + 0.08 + offs[0][2])
    p2 = (anchor[0] - fx * 0.02 + offs[1][0], anchor[1] - fy * 0.02 + offs[1][1], c.pelvis_z - 0.06 + offs[1][2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[anchor, p1, p2],
        widths=[0.22, 0.26, 0.29],
        depth_thick=0.030,
        colors=[P["cape"], P["cape_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Bordados dourados Flor-de-lis na barra inferior da capa
    for i in range(3):
        lat = (i - 1) * 0.08
        mk.cbox(c, p2[0] + px * lat, p2[1] + py * lat, p2[2] + 0.015, 0.024, 0.024, 0.024, P["gold"], outline=False)


# ---------------------------------------------------------------------------------------------------------------------
# Ganchos de Renderização (Painter's Algorithm)
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Mechas distantes do cabelo.
    - Capa azul nas costas (se não estiver no rodopio do CAPE_FLOURISH).
    - Florete se a mão estiver atrás do tronco ao encarar de costas.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)

    for s in (-1.0, 1.0):
        if _lock_is_behind(c, s):
            _side_lock(c, s)

    # Capa nas costas se não estiver no rodopio
    d_back = mk.depth(c, c.base_x - c.fx * 0.08, c.base_y - c.fy * 0.08)
    if d_back <= d_torso + 0.02 and not _flourishing(c):
        _draw_cape(c)

    # Florete se estiver atrás do tronco
    hand_l, hand_r = _current_hands(c)
    if mk.depth(c, hand_r[0], hand_r[1]) < d_torso and not _flourishing(c):
        _draw_weapons(c, hand_l, hand_r)
        c._weapon_drawn = True
    else:
        c._weapon_drawn = False


def draw_legs(c):
    """Calça cinza justa em malha 3D contínua e botas altas de couro com cano dobrado (sem degraus de joelho)."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.04)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.8 * sign, trail, (c.px, c.py), amp=amp * 0.5, freq=freq)

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.4, sh[1] + o1[1] * 0.4, sh[2] + 0.15)
        cuff_pos = (sh[0] + o1[0] * 0.2, sh[1] + o1[1] * 0.2, sh[2] + 0.08)
        ankle = (foot[0] + o2[0] * 0.3, foot[1] + o2[1] * 0.3, foot[2] + 0.05)

        # Calça de esgrima cinza justa contínua até o cano da bota
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos],
            widths=[0.105, 0.092, 0.084],
            depth_thick=0.082,
            colors=[P["pants"], P["pants_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Cano dobrado da bota (cuff) ajustado à perna
        mk.obox(c, cuff_pos, (c.fx, c.fy, 0.0), 0.065, 0.100, 0.092, P["boot_cuff"], up=(0.0, 0.0, 1.0))

        # Bota de montaria de couro contínua até o tornozelo
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[cuff_pos, ankle],
            widths=[0.084, 0.074],
            depth_thick=0.076,
            colors=[P["boot"], P["boot"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Pé da bota de couro com salto nobre e sola
        flen, fwidth = 0.13, 0.064
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.016, flen, fwidth, 0.034, P["boot"], outline=True)
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.003, flen + 0.004, fwidth + 0.004, 0.010, (48, 30, 18), outline=False)


def draw_obi(c):
    """Cinto de couro com fivela dourada e a bainha do florete no quadril esquerdo."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    # Cinto de couro
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.005, c.pelvis_w * 0.78, 0.065, P["leather"])
    # Fivela dourada
    mk.cbox(c, bx + fx * 0.090, by + fy * 0.090, z + 0.008, 0.050, 0.022, 0.045, P["gold"], outline=False)

    # Bainha do florete no quadril esquerdo
    sheath_pos = (bx + px * 0.13, by + py * 0.13, z + 0.04)
    mk.obox(c, sheath_pos, mk.norm((-fx * 0.75 + px * 0.20, -fy * 0.75 + py * 0.20, -0.55)), 0.48, 0.032, 0.032, P["leather"])
    mk.obox(c, mk.add(sheath_pos, mk.norm((-fx * 0.75 + px * 0.20, -fy * 0.75 + py * 0.20, -0.55)), 0.45),
            mk.norm((-fx * 0.75 + px * 0.20, -fy * 0.75 + py * 0.20, -0.55)), 0.035, 0.036, 0.036, P["gold"], outline=False)


def draw_torso(c):
    """
    Túnica azul-real com botões dourados, gola de renda Jabot em camadas e bandoleira de couro.
    """
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.092

    if mk.depth(c, fx, fy) > -0.05:
        # Fileira vertical de botões dourados Flor-de-lis
        for i in range(3):
            mk.cbox(c, bx + fx * front, by + fy * front, tz + 0.030 + i * 0.055, 0.020, 0.012, 0.020, P["gold"], outline=False)

        # Bandoleira de couro transversal
        a = (bx - px * 0.10 + fx * (front + 0.004), by - py * 0.10 + fy * (front + 0.004), tz + 0.25)
        b = (bx + px * 0.10 + fx * (front + 0.004), by + py * 0.10 + fy * (front + 0.004), tz + 0.01)
        mk.limb(c, a, b, 0.032, P["leather"], outline=False, height=0.016)
        # Broche Flor-de-lis dourado na bandoleira
        mk.cbox(c, bx + fx * (front + 0.006), by + fy * (front + 0.006), tz + 0.125, 0.036, 0.014, 0.036, P["gold"], outline=False)

        # Gola Jabot de renda francesa pregueada em camadas
        top_j = (bx + fx * (front - 0.002), by + fy * (front - 0.002), tz + 0.250)
        bot_j = (bx + fx * (front + 0.002), by + fy * (front + 0.002), tz + 0.155)
        draw_tapered_frustum_3d(c.surface, c.camera, top_j, bot_j, w_start=0.070, h_start=0.020, w_end=0.045, h_end=0.014, color=P["lace"], up=(0.0, 0.0, 1.0), outline=False, alpha=c.alpha)


def draw_arm(c, shoulder, hand, side):
    """Braço esguio com manga azul e luva de duelo branca."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.20)
    h = (hand[0], hand[1], hand[2] - 0.060)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.025), (0.0, 0.0, -0.025))

    # Manga bufante azul do ombro ao cotovelo
    mk.limb(c, s, e, 0.052, P["blue"], w_end=0.044)
    # Antebraço com luva branca de duelo
    mk.limb(c, e, h, 0.042, P["glove"], w_end=0.036)
    # Punho de renda francesa
    mk.obox(c, e, (c.fx, c.fy, 0.0), 0.055, 0.055, 0.020, P["lace"], outline=False)
    # Mão calçada com luva
    mk.cbox(c, h[0], h[1], h[2] - 0.020, 0.038, 0.038, 0.038, P["glove"])
    return s, e


def draw_sleeves(c, arms):
    """Talhos e ombreiras douradas nas mangas bufantes da túnica real."""
    P = pal()
    for s, e, side in arms:
        # Ombreira estruturada
        mk.obox(c, (s[0] + c.px * side * 0.02, s[1] + c.py * side * 0.02, s[2] + 0.01), (0.0, 0.0, -1.0), 0.065, 0.080, 0.075, P["blue"])
        # Galão dourado
        mk.obox(c, (s[0] + c.px * side * 0.02, s[1] + c.py * side * 0.02, s[2] + 0.01), (c.fx, c.fy, 0.0), 0.075, 0.012, 0.065, P["gold"], outline=False)


def draw_head(c):
    """
    Cabeça de Julie:
    - Crânio esculpido 3D com olhos azul-safira luminosos, nariz delicado e lábios rosa-veludo via draw_portrait_face_3d.
    - Franja ondulada acima das sobrancelhas (z >= hz + 0.108).
    - Mechas laterais emoldurando a face se visíveis da câmera.
    - Trança nobre caindo sobre o ombro.
    - Autêntico Chapéu Cavalier do séc. XVII com aba dobrada para cima, broche Flor-de-lis e pluma branca arqueada.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    d_torso = mk.depth(c, bx, by)

    # Franja acima das sobrancelhas (z >= hz + 0.108)
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.005
        p0 = (bx + fx * front_d, by + fy * front_d, hz + 0.138)
        p1 = (bx + fx * (front_d + 0.002), by + fy * (front_d + 0.002), hz + 0.116)
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            p0, p1,
            w_start=0.082, h_start=0.014,
            w_end=0.076, h_end=0.010,
            color=P["hair"],
            up=(0.0, 0.0, 1.0),
            outline=False,
            alpha=c.alpha,
        )

    # Mechas laterais do lado visível da câmera
    for s in (-1.0, 1.0):
        if not _lock_is_behind(c, s):
            _side_lock(c, s)

    # Trança descendo sobre o ombro
    _draw_braid(c)

    # Capa nas costas se virada de costas
    d_back = mk.depth(c, bx - fx * 0.08, by - fy * 0.08)
    if d_back > d_torso + 0.02 and not _flourishing(c):
        _draw_cape(c)

    # Autêntico Chapéu Cavalier 3D (apenas na cabeça se não estiver seguro na mão em reverência)
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose") or getattr(c, "pose_name", None)
    state = getattr(c, "state", "IDLE")
    p = extra.get("p", 0.0)
    if not (pose in ("cavalier_hat_bow", "noble_reverence") or (state == "INTRO" and p < 0.70)):
        _draw_cavalier_hat(c)


def draw_front(c, arm_l, arm_r):
    """
    Camada frontal (Painter's Algorithm):
    - O florete e a capa do CAPE_FLOURISH são desenhados aqui se não foram desenhados em draw_behind.
    """
    if getattr(c, "_weapon_drawn", False):
        return

    hand_l, hand_r = _current_hands(c)
    _draw_weapons(c, hand_l, hand_r)
    c._weapon_drawn = True
