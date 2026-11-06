"""
Okuni, mestra do Kabuki e dos leques Tessen (Izumo no Okuni):
- Rosto Oshiroi de porcelana branca pura, maquiagem teatral Kumadori carmim com asas nas têmporas.
- Olhos anime rubi expressivos com brilho duplo e cílios alados; lábios facetados em 3 planos com brilho cereja.
- Penteado tradicional Shimada em laca preta, coque alto, franja acima das sobrancelhas e grampos Kanzashi dourados com borlas de seda.
- Quimono Furisode cerimonial carmim em camadas com barra preta bordada a ouro e mangas longas ondulantes.
- Grande laço borboleta no Obi dourado nas costas com pontas esvoaçantes.
- Leques de guerra de ferro Tessen (fechados em guarda/marcha, abrindo-se em semicírculos radiantes de carmim e ouro nos golpes).
- Ordenação dinâmica de profundidade 3D (Painter's Algorithm) para oclusão perfeita dos leques e braços de costas.
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

PALETTE = {
    "kimono": (175, 24, 38),
    "kimono_dark": (118, 16, 28),
    "kimono_light": (215, 48, 62),
    "skirt": (28, 24, 32),
    "skirt_dark": (18, 15, 20),
    "collar": (252, 250, 248),
    "collar_gold": (224, 182, 54),
    "obi": (224, 182, 54),
    "obi_knot": (32, 28, 36),
    "tassel": (195, 30, 45),
    "skin": (252, 250, 248),
    "skin_shadow": (230, 224, 218),
    "hair": (22, 20, 26),
    "hair_light": (48, 42, 54),
    "hair_dark": (14, 12, 16),
    "kanzashi": (245, 205, 75),
    "fan_rib": (48, 44, 52),
    "fan_cloth": (185, 28, 42),
    "fan_gold": (240, 198, 65),
    "steel": (215, 222, 235),
    "tabi": (252, 250, 248),
    "geta": (145, 95, 55),
    "poison": (80, 220, 120),
    "aura": (195, 45, 85),
    "aura_core": (255, 225, 235),
}

MATERIALS = {
    "kimono": "silk", "kimono_dark": "silk", "kimono_light": "silk",
    "skirt": "silk", "obi": "gold", "kanzashi": "gold",
    "fan_cloth": "silk", "fan_gold": "gold", "steel": "steel",
    "tessen_blade": "steel", "geta": "wood"
}

LEGACY_MATERIALS = {
    "kimono": "matte", "kimono_dark": "matte", "kimono_light": "matte",
    "skirt": "matte", "obi": "matte", "kanzashi": "matte",
    "fan_cloth": "matte", "fan_gold": "matte", "steel": "matte",
    "tessen_blade": "matte", "geta": "matte"
}


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Leques Tessen
# ---------------------------------------------------------------------------------------------------------------------

def _hands(c):
    """
    Cinemática articulada modular de Okuni (Izumo no Okuni):
    Retorna posição das mãos (mão esquerda, mão direita com leques Tessen).
    Suporta todas as 12 poses da Fase 2 Overhaul:
    - fan_strike (ataque melee com leques Tessen e micro-avanço)
    - dokukiri_breath (sopro venenoso Dokukiri em cone frontal)
    - kawarimi_feint (pirueta teatral Kawarimi)
    - kumadori_steps (Intro 1: passos rítmicos com batida de pé)
    - kimono_spin (Intro 2: giro de quimono e abertura de leques)
    - tessen_cross_guard (Intro 3: guarda cruzada de Tessen diante do rosto)
    - theatrical_flourish (Vitória 1: giro gracioso com arcos de leque)
    - mie_pose (Vitória 2: pose dramática clássica Mie)
    - fan_hide_smile (Vitória 3: leque ocultando sorriso)
    - finisher_decap (Finisher A: Tessen Zanshu / 鉄扇斬首)
    - finisher_melt (Finisher B: Dokukiri Youkai / 毒霧溶解)
    - dodge_cancel (Cancelamento de pirueta em golpe de leque)
    """
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    p = extra.get("p", getattr(c, "atk_progress", 0.0))
    state = getattr(c, "state", "IDLE")

    tz = getattr(c, "torso_z", 0.40)
    bx = getattr(c, "base_x", 0.0)
    by = getattr(c, "base_y", 0.0)
    fx = getattr(c, "fx", 1.0)
    fy = getattr(c, "fy", 0.0)
    px = getattr(c, "px", 0.0)
    py = getattr(c, "py", 1.0)

    # 1. ATAQUE PRIMÁRIO: DANÇA DOS LEQUES DE AÇO (fan_strike / ATTACK)
    if (pose in ("fan_strike", "attack", "fan_flurry")) or (not pose and state == "ATTACK"):
        prog = p if p is not None else 0.5
        if prog < 0.35:
            w = _smooth(prog / 0.35)
            right = (bx + fx * 0.10 - px * (0.12 - 0.06 * w), by + fy * 0.10 - py * (0.12 - 0.06 * w), tz + 0.18 + 0.12 * w)
            left = (bx + fx * 0.14 + px * 0.12, by + fy * 0.14 + py * 0.12, tz + 0.08)
        elif prog < 0.75:
            t = (prog - 0.35) / 0.40
            reach = 0.12 + 0.36 * math.sin(math.pi * t)
            right = (bx + fx * reach + px * (0.04 - 0.22 * _smooth(t)),
                     by + fy * reach + py * (0.04 - 0.22 * _smooth(t)),
                     tz + 0.24 - 0.16 * _smooth(t))
            left = (bx + fx * (reach * 0.8) - px * (0.10 - 0.18 * _smooth(t)),
                    by + fy * (reach * 0.8) - py * (0.10 - 0.18 * _smooth(t)),
                    tz + 0.14 + 0.10 * math.sin(math.pi * t))
        else:
            u = (prog - 0.75) / 0.25
            right = (bx + fx * (0.16 - 0.04 * u) + px * 0.08, by + fy * (0.16 - 0.04 * u) + py * 0.08, tz + 0.12)
            left = (bx + fx * (0.08 + 0.04 * u) - px * 0.12, by + fy * (0.08 + 0.04 * u) - py * 0.12, tz + 0.10)
        return left, right

    # 2. AÇÃO SECUNDÁRIA: DOKUKIRI (SOPRO VENENOSO EM CONE)
    if (pose in ("dokukiri", "dokukiri_breath", "poison_breath")) or (not pose and state == "DOKUKIRI"):
        prog = p if p is not None else 0.5
        u = _smooth(prog)
        if u < 0.35:
            # Inspiração: recolhe os dois leques fechados rente ao peito
            w = u / 0.35
            right = (bx + fx * 0.06 + px * 0.04, by + fy * 0.06 + py * 0.04, tz + 0.20 + 0.06 * w)
            left = (bx + fx * 0.06 - px * 0.04, by + fy * 0.06 - py * 0.04, tz + 0.20 + 0.06 * w)
        else:
            # Sopro teatral e abertura em leque para projetar o cone
            w = (u - 0.35) / 0.65
            flare = math.sin(math.pi * w)
            right = (bx + fx * (0.18 + 0.12 * flare) + px * (0.16 + 0.08 * flare),
                     by + fy * (0.18 + 0.12 * flare) + py * (0.16 + 0.08 * flare),
                     tz + 0.18 - 0.06 * w)
            left = (bx + fx * (0.18 + 0.12 * flare) - px * (0.16 + 0.08 * flare),
                    by + fy * (0.18 + 0.12 * flare) - py * (0.16 + 0.08 * flare),
                    tz + 0.18 - 0.06 * w)
        return left, right

    # 3. ESQUIVA / KAWARIMI FEINT
    if (pose in ("kawarimi", "kawarimi_feint", "dodge")) or (not pose and state in ("ROLL", "KABUKI_ROLL")):
        prog = extra.get("roll_prog", p if p is not None else 0.5)
        spin = math.sin(prog * math.pi)
        left = (bx - fx * 0.06 - px * 0.16, by - fy * 0.06 - py * 0.16, tz + 0.16 + spin * 0.12)
        right = (bx + fx * 0.18 + px * 0.10, by + fy * 0.18 + py * 0.10, tz + 0.16 - spin * 0.08)
        return left, right

    # 4. INTRO FASE 1: PASSOS KUMADORI (kumadori_steps)
    if pose == "kumadori_steps":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        stomp = math.sin(u * math.pi * 3.0) * 0.02
        start_l = (bx + fx * 0.06 - px * 0.12, by + fy * 0.06 - py * 0.12, tz + 0.06)
        end_l = (bx + fx * 0.08 - px * 0.10, by + fy * 0.08 - py * 0.10, tz + 0.08)
        start_r = (bx + fx * 0.10 + px * 0.12, by + fy * 0.10 + py * 0.12, tz + 0.06)
        end_r = (bx + fx * 0.14 + px * 0.10, by + fy * 0.14 + py * 0.10, tz + 0.12)
        left = mk.lerp(start_l, end_l, u)
        right = mk.lerp(start_r, end_r, u)
        return (left[0], left[1], left[2] + stomp), (right[0], right[1], right[2] - stomp)

    # 5. INTRO FASE 2: GIRO DE QUIMONO E ABERTURA (kimono_spin)
    if pose == "kimono_spin":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        ang = u * math.pi
        spin_l = (bx + fx * (0.08 + 0.06 * math.sin(ang)) - px * (0.10 - 0.14 * math.sin(ang)),
                  by + fy * (0.08 + 0.06 * math.sin(ang)) - py * (0.10 - 0.14 * math.sin(ang)),
                  tz + 0.08 + 0.10 * math.sin(ang))
        spin_r = (bx + fx * (0.14 + 0.02 * math.cos(ang)) + px * (0.10 - 0.06 * math.sin(ang)),
                  by + fy * (0.14 + 0.02 * math.cos(ang)) - py * (0.10 - 0.06 * math.sin(ang)),
                  tz + 0.12 + 0.06 * math.sin(ang))
        guard_l = (bx + fx * 0.14 - px * 0.04, by + fy * 0.14 - py * 0.04, tz + 0.18)
        guard_r = (bx + fx * 0.16 + px * 0.04, by + fy * 0.16 + py * 0.04, tz + 0.16)
        return mk.lerp(spin_l, guard_l, u), mk.lerp(spin_r, guard_r, u)

    # 6. INTRO FASE 3: GUARDA CRUZADA DE TESSEN (tessen_cross_guard)
    if pose == "tessen_cross_guard":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        glo_p = float(extra.get("p", 0.70 + 0.30 * u))
        start_l = (bx + fx * 0.14 - px * 0.04, by + fy * 0.14 - py * 0.04, tz + 0.18)
        start_r = (bx + fx * 0.16 + px * 0.04, by + fy * 0.16 + py * 0.04, tz + 0.16)
        cross_l = (bx + fx * 0.15 - px * 0.03, by + fy * 0.15 - py * 0.03, tz + 0.19)
        cross_r = (bx + fx * 0.17 + px * 0.03, by + fy * 0.17 + py * 0.03, tz + 0.17)
        breathe = math.sin(glo_p * 14.0 + c.walk_timer * 2.5) * 0.012
        fan_pulse = math.sin(glo_p * 10.0) * 0.008
        cur_l = mk.lerp(start_l, cross_l, u)
        cur_r = mk.lerp(start_r, cross_r, u)
        return (cur_l[0], cur_l[1], cur_l[2] + breathe + fan_pulse), (cur_r[0], cur_r[1], cur_r[2] - breathe - fan_pulse)

    # 7. VITÓRIA FASE 1: GIRO TEATRAL COM PÉTALAS (theatrical_flourish)
    if pose == "theatrical_flourish":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        idle_l = (bx + fx * 0.12 - px * 0.14, by + fy * 0.12 - py * 0.14, tz + 0.12)
        idle_r = (bx + fx * 0.16 + px * 0.10, by + fy * 0.16 + py * 0.10, tz + 0.14)
        flare = math.sin(u * math.pi)
        flourish_l = (bx + fx * (0.12 - 0.06 * flare) - px * (0.14 + 0.12 * flare),
                      by + fy * (0.12 - 0.06 * flare) - py * (0.14 + 0.12 * flare),
                      tz + 0.12 + 0.16 * flare)
        flourish_r = (bx + fx * (0.16 + 0.10 * flare) + px * (0.10 + 0.12 * flare),
                      by + fy * (0.16 + 0.10 * flare) + py * (0.10 + 0.12 * flare),
                      tz + 0.14 + 0.14 * flare)
        mie_start_l = (bx + fx * 0.06 - px * 0.18, by + fy * 0.06 - py * 0.18, tz + 0.06)
        mie_start_r = (bx + fx * 0.22 + px * 0.12, by + fy * 0.22 + py * 0.12, tz + 0.22)
        return mk.lerp(flourish_l, mie_start_l, u * 0.6), mk.lerp(flourish_r, mie_start_r, u * 0.6)

    # 8. VITÓRIA FASE 2: POSE MIE DRAMÁTICA (mie_pose)
    if pose == "mie_pose":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        mie_start_l = (bx + fx * 0.06 - px * 0.18, by + fy * 0.06 - py * 0.18, tz + 0.06)
        mie_start_r = (bx + fx * 0.22 + px * 0.12, by + fy * 0.22 + py * 0.12, tz + 0.22)
        mie_hold_l = (bx + fx * 0.07 - px * 0.16, by + fy * 0.07 - py * 0.16, tz + 0.05)
        mie_hold_r = (bx + fx * 0.24 + px * 0.10, by + fy * 0.24 + py * 0.10, tz + 0.24)
        hide_ready_l = (bx + fx * 0.05 + px * 0.12, by + fy * 0.05 + py * 0.12, tz + 0.05)
        hide_ready_r = (bx + fx * 0.18 + px * 0.04, by + fy * 0.18 + py * 0.04, tz + 0.26)
        if u < 0.65:
            w = u / 0.65
            return mk.lerp(mie_start_l, mie_hold_l, w), mk.lerp(mie_start_r, mie_hold_r, w)
        else:
            w = (u - 0.65) / 0.35
            return mk.lerp(mie_hold_l, hide_ready_l, w), mk.lerp(mie_hold_r, hide_ready_r, w)

    # 9. VITÓRIA FASE 3: LEQUE OCULTANDO SORRISO (fan_hide_smile - 100% Animado)
    if pose == "fan_hide_smile":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        glo_p = float(extra.get("p", 0.70 + 0.30 * u))
        hide_ready_l = (bx + fx * 0.05 + px * 0.12, by + fy * 0.05 + py * 0.12, tz + 0.05)
        hide_ready_r = (bx + fx * 0.18 + px * 0.04, by + fy * 0.18 + py * 0.04, tz + 0.26)
        hide_final_l = (bx + fx * 0.04 + px * 0.14, by + fy * 0.04 + py * 0.14, tz + 0.04)
        hide_final_r = (bx + fx * 0.15 + px * 0.02, by + fy * 0.15 + py * 0.02, tz + 0.28)
        base_l = mk.lerp(hide_ready_l, hide_final_l, u)
        base_r = mk.lerp(hide_ready_r, hide_final_r, u)
        flutter = math.sin((glo_p * 22.0) + c.walk_timer * 3.0) * 0.016
        sway = math.cos((glo_p * 10.0)) * 0.012
        return (base_l[0], base_l[1], base_l[2] + sway), (base_r[0], base_r[1], base_r[2] + flutter)

    # 10. FINISHER A: TESSEN ZANSHU / DECAPITAÇÃO DE LEQUES (finisher_decap / finisher_1)
    if pose in ("finisher_decap", "finisher_tessen", "finisher_1"):
        prog = p if p is not None else 0.5
        u = _smooth(prog)
        reach = 0.14 + 0.38 * math.sin(u * math.pi)
        scissor = (1.0 - u) * 0.18
        right = (bx + fx * reach + px * scissor, by + fy * reach + py * scissor, tz + 0.26 - 0.06 * u)
        left = (bx + fx * reach - px * scissor, by + fy * reach - py * scissor, tz + 0.26 - 0.06 * u)
        return left, right

    # 11. FINISHER B: DOKUKIRI YOUKAI / DISSOLUÇÃO EM ÁCIDO (finisher_melt / finisher_2)
    if pose in ("finisher_melt", "finisher_poison", "finisher_2"):
        prog = p if p is not None else 0.5
        u = _smooth(prog)
        right = (bx + fx * (0.20 + 0.10 * math.sin(u * math.pi)) + px * 0.12,
                 by + fy * (0.20 + 0.10 * math.sin(u * math.pi)) + py * 0.12,
                 tz + 0.22)
        left = (bx + fx * (0.20 + 0.10 * math.sin(u * math.pi)) - px * 0.12,
                by + fy * (0.20 + 0.10 * math.sin(u * math.pi)) - py * 0.12,
                tz + 0.22)
        return left, right

    # 12. CANCELAMENTO: KAWARIMI PIRUETA -> GOLPE DE LEQUES (dodge_cancel)
    if pose == "dodge_cancel":
        prog = p if p is not None else 0.5
        if prog < 0.45:
            u = prog / 0.45
            spin = math.sin(u * math.pi)
            left = (bx - fx * 0.06 - px * 0.16, by - fy * 0.06 - py * 0.16, tz + 0.16 + spin * 0.12)
            right = (bx + fx * 0.18 + px * 0.10, by + fy * 0.18 + py * 0.10, tz + 0.16 - spin * 0.08)
        else:
            u = (prog - 0.45) / 0.55
            reach = 0.12 + 0.36 * math.sin(u * math.pi)
            right = (bx + fx * reach + px * (0.04 - 0.22 * _smooth(u)),
                     by + fy * reach + py * (0.04 - 0.22 * _smooth(u)),
                     tz + 0.24 - 0.16 * _smooth(u))
            left = (bx + fx * (reach * 0.8) - px * (0.10 - 0.18 * _smooth(u)),
                    by + fy * (reach * 0.8) - py * (0.10 - 0.18 * _smooth(u)),
                    tz + 0.14)
        return left, right

    # Padrão: guarda graciosa de dançarina
    return idle_arms(c)


def idle_arms(c):
    """Guarda graciosa de dançarina: leque direito em semicírculo diante do peito, leque esquerdo invertido ao lado."""
    tz = getattr(c, "torso_z", 0.40) + math.sin(getattr(c, "walk_timer", 0.0) * 2.8) * 0.012
    bx = getattr(c, "base_x", 0.0)
    by = getattr(c, "base_y", 0.0)
    fx = getattr(c, "fx", 1.0)
    fy = getattr(c, "fy", 0.0)
    px = getattr(c, "px", 0.0)
    py = getattr(c, "py", 1.0)
    right = (bx + fx * 0.16 - px * 0.06, by + fy * 0.16 - py * 0.06, tz + 0.12)
    left = (bx + fx * 0.06 + px * 0.14, by + fy * 0.06 + py * 0.14, tz + 0.02)
    return left, right


def attack_arms(c):
    """Ataque rodopiante de leques de ferro (Tessen-jutsu): leque direito cortando em leque e esquerdo bloqueando."""
    p = getattr(c, "atk_progress", 0.0)
    if p is None:
        p = 0.0
    tz = getattr(c, "torso_z", 0.40)
    bx = getattr(c, "base_x", 0.0)
    by = getattr(c, "base_y", 0.0)
    fx = getattr(c, "fx", 1.0)
    fy = getattr(c, "fy", 0.0)
    px = getattr(c, "px", 0.0)
    py = getattr(c, "py", 1.0)
    sw = math.sin(p * math.pi)
    right = (bx + fx * (0.18 + sw * 0.28) - px * (0.04 - p * 0.18),
             by + fy * (0.18 + sw * 0.28) - py * (0.04 - p * 0.18),
             tz + 0.15 + sw * 0.12)
    left = (bx + fx * (0.10 + p * 0.16) + px * (0.12 - p * 0.10),
            by + fy * (0.10 + p * 0.16) + py * (0.12 - p * 0.10),
            tz + 0.06 + sw * 0.08)
    return left, right


def _current_hands(c):
    extra = getattr(c, "extra_props", {}) or {}
    if extra.get("pose") or getattr(c, "state", "IDLE") not in ("IDLE", "WALK"):
        return _hands(c)
    if getattr(c, "is_melee", False) and getattr(c, "atk_progress", None) is not None:
        return attack_arms(c)
    if getattr(c, "is_moving", False) and hasattr(c, "walk_timer"):
        tz = getattr(c, "torso_z", 0.40)
        bx = getattr(c, "base_x", 0.0)
        by = getattr(c, "base_y", 0.0)
        fx = getattr(c, "fx", 1.0)
        fy = getattr(c, "fy", 0.0)
        px = getattr(c, "px", 0.0)
        py = getattr(c, "py", 1.0)
        sw = math.sin(c.walk_timer * 7.5) * 0.035
        right = (bx + fx * 0.12 - px * 0.08 + fx * sw, by + fy * 0.12 - py * 0.08 + fy * sw, tz + 0.08)
        left = (bx + fx * 0.04 + px * 0.12 - fx * sw, by + fy * 0.04 + py * 0.12 - fy * sw, tz + 0.04)
        return left, right
    return idle_arms(c)


def get_arms(c):
    """Exposição modular da cinemática dos braços para sincronização com o renderizador humanoide."""
    left, right = _current_hands(c)
    return left, right


# ---------------------------------------------------------------------------------------------------------------------
# Leque Tessen 3D (Fechado e Aberto)
# ---------------------------------------------------------------------------------------------------------------------

def _draw_tessen_fan(c, hand, fwd_dir, side_dir, open_frac=0.0):
    """
    Renderiza o leque de guerra de ferro Tessen:
    - Fechado: bastão sólido de ferro laqueado com anel de seda e borla.
    - Aberto: semicírculo de varetas de aço e seda carmim com sol dourado pintado.
    """
    P = pal()
    u = mk.norm(fwd_dir)
    v = mk.norm(side_dir)

    if open_frac < 0.15:
        # Leque Fechado (bastão Tessen)
        p_base = mk.add(hand, u, -0.04)
        mk.obox(c, p_base, u, 0.26, 0.032, 0.026, P["fan_rib"])
        mk.obox(c, mk.add(p_base, u, 0.02), u, 0.022, 0.036, 0.030, P["fan_gold"], outline=False)
        mk.obox(c, mk.add(p_base, u, 0.22), u, 0.035, 0.030, 0.024, P["steel"], outline=False)
    else:
        # Leque Aberto em Semicírculo Radiante
        p_rivet = mk.add(hand, u, 0.01)
        mk.cbox(c, p_rivet[0], p_rivet[1], p_rivet[2], 0.022, 0.022, 0.022, P["fan_gold"], outline=False)

        # 5 varetas radiais de ferro e leque de seda em leque
        fan_radius = 0.26 * (0.85 + 0.15 * open_frac)
        spread_angle = math.pi * 0.55 * open_frac
        num_ribs = 5

        fan_pts = []
        for i in range(num_ribs):
            frac = (i / (num_ribs - 1) - 0.5) * 2.0  # -1.0 a +1.0
            ang = frac * (spread_angle * 0.5)
            # Direção radial da vareta
            cos_a = math.cos(ang)
            sin_a = math.sin(ang)
            rib_dir = (u[0] * cos_a + v[0] * sin_a,
                       u[1] * cos_a + v[1] * sin_a,
                       u[2] * cos_a + v[2] * sin_a)
            tip = mk.add(p_rivet, rib_dir, fan_radius)
            fan_pts.append(tip)
            # Vareta de ferro
            mk.obox(c, p_rivet, rib_dir, fan_radius, 0.016, 0.016, P["fan_rib"], outline=False)
            # Ponteira de aço afiado na extremidade
            mk.obox(c, mk.add(tip, rib_dir, -0.03), rib_dir, 0.03, 0.018, 0.018, P["steel"], outline=False)

        # Seda carmim estendida entre as varetas
        for i in range(len(fan_pts) - 1):
            p0 = mk.lerp(p_rivet, fan_pts[i], 0.35)
            p1 = fan_pts[i]
            p2 = fan_pts[i + 1]
            p3 = mk.lerp(p_rivet, fan_pts[i + 1], 0.35)
            mk.band(c, (p0, p1, p2, p3), P["fan_cloth"] + (235,))
            # Arco dourado de sol kabuki no centro da seda
            g0 = mk.lerp(p0, p1, 0.40)
            g1 = mk.lerp(p0, p1, 0.65)
            g2 = mk.lerp(p3, p2, 0.65)
            g3 = mk.lerp(p3, p2, 0.40)
            mk.band(c, (g0, g1, g2, g3), P["fan_gold"] + (245,))


def _render_fans_and_hands(c, arm_l, arm_r):
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)

    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    p = extra.get("p", getattr(c, "atk_progress", 0.0))
    is_atk = (c.is_melee and c.atk_progress is not None) or (pose in ("fan_strike", "attack", "fan_flurry"))

    if is_atk:
        prog = p if p is not None else 0.5
        open_frac = math.sin(prog * math.pi)
    elif pose in ("tessen_cross_guard", "theatrical_flourish", "mie_pose", "fan_hide_smile", "finisher_decap", "finisher_melt"):
        open_frac = 1.0
    elif pose in ("dokukiri", "dokukiri_breath"):
        prog = p if p is not None else 0.5
        open_frac = 0.0 if prog < 0.35 else min(1.0, (prog - 0.35) / 0.30)
    elif pose == "kimono_spin":
        prog = p if p is not None else 0.5
        open_frac = max(0.0, min(1.0, (prog - 0.30) / 0.50))
    else:
        open_frac = 0.0

    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    dir_r_fwd = (fx * 0.8 + px * 0.3, fy * 0.8 + py * 0.3, 0.2 if is_atk else 0.4)
    dir_r_side = (-px * 0.7 + fx * 0.2, -py * 0.7 + fy * 0.2, 0.1)
    _draw_tessen_fan(c, hand_r, dir_r_fwd, dir_r_side, open_frac=open_frac)

    dir_l_fwd = (fx * 0.5 - px * 0.5, fy * 0.5 - py * 0.5, -0.2 if is_atk else 0.1)
    dir_l_side = (px * 0.7 + fx * 0.1, py * 0.7 + fy * 0.1, 0.0)
    _draw_tessen_fan(c, hand_l, dir_l_fwd, dir_l_side, open_frac=open_frac * (0.85 if pose else 0.7))

    # Rastro mágico/venenoso em arco durante o ataque
    if is_atk and getattr(c, "atk_progress", 0.0) >= 0.25:
        P = pal()
        tip_r = mk.add(hand_r, mk.norm(dir_r_fwd), 0.28)
        pts = [
            (tip_r[0] + px * 0.12, tip_r[1] + py * 0.12, tip_r[2] + 0.06),
            (tip_r[0] - px * 0.12, tip_r[1] - py * 0.12, tip_r[2] - 0.06),
            (hand_r[0] - px * 0.06, hand_r[1] - py * 0.06, hand_r[2]),
            (hand_r[0] + px * 0.06, hand_r[1] + py * 0.06, hand_r[2]),
        ]
        mk.band(c, pts, P["aura"] + (180,))


# ---------------------------------------------------------------------------------------------------------------------
# Penteado Shimada & Kanzashi
# ---------------------------------------------------------------------------------------------------------------------

def _shimada_bun_root(c):
    return (c.base_x - c.fx * 0.045, c.base_y - c.fy * 0.045, c.head_z + 0.170)


def _draw_shimada_hair(c):
    """Coque Shimada alto com laço de cabelo laqueado, pente dourado e Kanzashis."""
    P = pal()
    root = _shimada_bun_root(c)
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # Coque volumoso em forma de laço duplo (chignon Shimada)
    bun_top = (root[0] - fx * 0.02, root[1] - fy * 0.02, root[2] + 0.08)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        root, bun_top,
        w_start=0.075, h_start=0.075,
        w_end=0.060, h_end=0.060,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Pente dourado tradicional (kushi) na base do coque
    mk.obox(c, (root[0] + fx * 0.025, root[1] + fy * 0.025, root[2] + 0.02),
            (px, py, 0.0), 0.10, 0.016, 0.038, P["kanzashi"], up=(0.0, 0.0, 1.0), outline=False)

    # Grampos Kanzashi dourados radiais dos dois lados
    for s in (-1.0, 1.0):
        for j in range(3):
            k_dir = mk.norm((px * s * (0.60 + 0.20 * j) - fx * 0.10,
                             py * s * (0.60 + 0.20 * j) - fy * 0.10,
                             0.80 - 0.25 * j))
            k_origin = (root[0] + px * s * 0.035, root[1] + py * s * 0.035, root[2] + 0.03)
            mk.obox(c, k_origin, k_dir, 0.14, 0.010, 0.010, P["kanzashi"], outline=False)

        # Borla dourada pendurada que balança com o movimento
        trail, amp, freq = mk.motion(c, 0.05)
        offs = cloth.chain_offsets(2, c.walk_timer, 0.9 * s, trail, (px, py), amp=amp * 1.4, freq=freq)
        p_tassel = (root[0] + px * s * 0.08 + offs[1][0], root[1] + py * s * 0.08 + offs[1][1], root[2] - 0.04 + offs[1][2])
        mk.obox(c, p_tassel, (0.0, 0.0, -1.0), 0.050, 0.014, 0.014, P["tassel"], outline=False)


# ---------------------------------------------------------------------------------------------------------------------
# Ganchos de Renderização (Painter's Algorithm)
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Laço borboleta monumental do Obi dourado nas costas.
    - Coque Shimada traseiro se estiver do lado oposto à câmera.
    - Leques e mãos se estiverem atrás do tronco ao encarar de costas.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    # Laço borboleta monumental do Obi nas costas
    d_back = mk.depth(c, bx - fx * 0.11, by - fy * 0.11)
    if d_back >= d_torso - 0.03:
        b_root = (bx - fx * 0.11, by - fy * 0.11, c.pelvis_z + 0.08)
        # Nó central
        mk.cbox(c, b_root[0], b_root[1], b_root[2], 0.065, 0.045, 0.065, P["obi_knot"])
        # Asas borboleta douradas arqueadas
        for s in (-1.0, 1.0):
            wing_dir = mk.norm((px * s * 0.70 - fx * 0.15, py * s * 0.70 - fy * 0.15, 0.45))
            mk.obox(c, (b_root[0] + px * s * 0.02, b_root[1] + py * s * 0.02, b_root[2] + 0.01),
                    wing_dir, 0.11, 0.030, 0.065, P["obi"], up=(fx, fy, 0.0), outline=True)

        # Fitas longas do obi penduradas com movimento
        trail, amp, freq = mk.motion(c, 0.06)
        for k, s in enumerate((-1.0, 1.0)):
            offs = cloth.chain_offsets(3, c.walk_timer, 0.8 * k, trail, (px, py), amp=amp * 1.5, freq=freq)
            for i, o in enumerate(offs):
                mk.cbox(c, b_root[0] - fx * 0.02 + px * 0.03 * s + o[0],
                        b_root[1] - fy * 0.02 + py * 0.03 * s + o[1],
                        b_root[2] - 0.03 - 0.06 * (i + 1) + o[2],
                        0.035, 0.022, 0.065, P["obi"], outline=False)

    # Coque Shimada se atrás da cabeça
    b_root_pos = _shimada_bun_root(c)
    if mk.depth(c, b_root_pos[0], b_root_pos[1]) < d_torso:
        _draw_shimada_hair(c)

    # Mãos e leques ordenados por profundidade
    hand_l, hand_r = _current_hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_fans_and_hands(c, hand_l, hand_r)


def draw_legs(c):
    """Saia Furisode cerimonial contínua em fita 3D com barra dourada e sandálias Geta."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.06)
    flare = 0.08 * c.lunge_curve
    top = c.pelvis_z + 0.02
    bottom = c.base_z + 0.04

    offs = cloth.chain_offsets(3, c.walk_timer, 0.0, trail, (px, py), amp=amp * 1.2, freq=freq, wind=cloth.wind_at(bx, by))

    p0 = (bx, by, top)
    p1 = (bx + offs[0][0] * 0.5, by + offs[0][1] * 0.5, top - 0.14)
    p2 = (bx + offs[1][0] * 0.8, by + offs[1][1] * 0.8, bottom + 0.06)
    p3 = (bx + offs[2][0], by + offs[2][1], bottom)

    # Saia de seda carmim contínua em malha 3D
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1, p2, p3],
        widths=[c.pelvis_w + 0.04, c.pelvis_w + 0.08, c.pelvis_w + 0.12 + flare, c.pelvis_w + 0.14 + flare],
        depth_thick=0.130,
        colors=[P["kimono"], P["kimono_dark"], P["skirt"]],
        side_vec=(px, py, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Barra inferior dourada ricamente bordada
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p2, p3],
        widths=[c.pelvis_w + 0.125 + flare, c.pelvis_w + 0.145 + flare],
        depth_thick=0.134,
        colors=[P["collar_gold"], P["obi"]],
        side_vec=(px, py, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Sandálias de madeira Geta sob a barra
    for side in (-1.0, 1.0):
        gx = bx + px * (0.065 * side)
        gy = by + py * (0.065 * side)
        gz = bottom - 0.015
        mk.obox(c, (gx - fx * 0.035, gy - fy * 0.035, gz), (fx, fy, 0.0), 0.12, 0.065, 0.025, P["geta"])
        mk.obox(c, (gx - fx * 0.015, gy - fy * 0.015, gz + 0.025), (fx, fy, 0.0), 0.09, 0.055, 0.022, P["tabi"])
        mk.obox(c, (gx + fx * 0.015, gy + fy * 0.015, gz + 0.025), (fx, fy, 0.0), 0.015, 0.058, 0.024, P["tassel"], outline=False)


def draw_obi(c):
    """Obi dourado largo na cintura com nó frontal estilizado."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07
    d_torso = mk.depth(c, bx, by)

    # Faixa principal dourada do obi
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.005, c.pelvis_w * 0.76, 0.075, P["obi"])
    # Faixa superior de contraste
    mk.cbox(c, bx, by, z + 0.065, c.pelvis_w - 0.008, c.pelvis_w * 0.74, 0.012, P["obi_knot"], outline=False)


def draw_torso(c):
    """
    Tronco de Okuni:
    - Quimono Furisode cerimonial carmim com decote em V sutil.
    - Colarinho branco de seda pura (collar) com debrum dourado de contraste.
    - Pele Oshiroi branca pura de porcelana.
    """
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.105

    # Detalhes frontais (colarinho branco e debrum dourado)
    if mk.depth(c, fx, fy) > -0.05:
        apex = (bx + fx * front, by + fy * front, tz + 0.095)
        for s in (-1.0, 1.0):
            top = (bx + fx * (front - 0.003) + px * 0.052 * s, by + fy * (front - 0.003) + py * 0.052 * s, tz + 0.245)
            # Colarinho branco
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                top, apex,
                w_start=0.024, h_start=0.014,
                w_end=0.016, h_end=0.010,
                color=P["collar"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )
            # Debrum dourado de seda
            top_g = (top[0] - px * 0.006 * s, top[1] - py * 0.006 * s, top[2] - 0.004)
            apex_g = (apex[0] - px * 0.004 * s, apex[1] - py * 0.004 * s, apex[2] + 0.006)
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                top_g, apex_g,
                w_start=0.010, h_start=0.010,
                w_end=0.007, h_end=0.007,
                color=P["collar_gold"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )

        # Pele Oshiroi no centro do decote
        mk.obox(c, (bx + fx * (front - 0.005), by + fy * (front - 0.005), tz + 0.145),
                (0.0, 0.0, 1.0), 0.080, 0.040, 0.014, P["skin"], up=(fx, fy, 0.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço feminino esguio de pele Oshiroi branca pura."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.20)
    h = (hand[0], hand[1], hand[2] - 0.065)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.025), (0.0, 0.0, -0.025))

    # Braço e antebraço esguios de porcelana
    mk.limb(c, s, e, 0.048, P["skin"], w_end=0.042)
    mk.limb(c, e, h, 0.042, P["skin"], w_end=0.036)
    # Mão delicada
    mk.cbox(c, h[0], h[1], h[2] - 0.022, 0.042, 0.042, 0.042, P["skin"])
    return s, e


def draw_sleeves(c, arms):
    """Mangas Furisode amplas e ondulantes com caimento vertical natural e debrum dourado."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.07)
    for k, (s, e, side) in enumerate(arms):
        anchor = (s[0] + c.px * side * 0.015, s[1] + c.py * side * 0.015, s[2] + 0.010)
        mid = mk.add(mk.lerp(s, e, 0.45), (c.px * side * 0.025, c.py * side * 0.025, -0.040))
        hem = mk.add(mk.lerp(s, e, 0.85), (c.px * side * 0.040, c.py * side * 0.040, -0.120))

        # Manga de seda carmim
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[anchor, mid, hem],
            widths=[0.110, 0.145, 0.165],
            depth_thick=0.082,
            colors=[P["kimono"], P["kimono_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Debrum dourado na borda inferior da manga
        mk.obox(c, (hem[0], hem[1], hem[2] + 0.010), (0.0, 0.0, -1.0),
                0.016, 0.165, 0.084, P["collar_gold"], up=(c.fx, c.fy, 0.0), outline=False)


def draw_head(c):
    """
    Cabeça de Okuni:
    - Crânio esculpido em 3D com pele Oshiroi branca pura.
    - Olhos anime rubi expressivos, Kumadori alado carmim nas têmporas, nariz delicado e lábios cereja via draw_portrait_face_3d.
    - Cabelo laqueado Shimada com franja arqueada acima das sobrancelhas.
    - Coque Shimada alto com Kanzashi dourados (se visível).
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    d_torso = mk.depth(c, bx, by)
    extra = getattr(c, "extra_props", {}) or {}
    legacy = extra.get("legacy_mode", False)

    # 1. Rosto Kumadori HD esculpido via draw_portrait_face_3d (quando virada para a câmera)
    if not legacy and mk.depth(c, fx, fy) > -0.05:
        draw_portrait_face_3d(c, char_type="okuni")
        c._face_drawn = True

    # 2. Franja repartida clássica acima das sobrancelhas (z >= hz + 0.108)
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.005
        for s in (-1.0, 1.0):
            p0 = (bx + fx * front_d + px * 0.012 * s, by + fy * front_d + py * 0.012 * s, hz + 0.140)
            p1 = (bx + fx * (front_d + 0.002) + px * 0.038 * s, by + fy * (front_d + 0.002) + py * 0.038 * s, hz + 0.118)
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                p0, p1,
                w_start=0.020, h_start=0.012,
                w_end=0.012, h_end=0.008,
                color=P["hair"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )

    # 3. Coque Shimada se do lado visível da câmera
    b_root_pos = _shimada_bun_root(c)
    if mk.depth(c, b_root_pos[0], b_root_pos[1]) >= d_torso:
        _draw_shimada_hair(c)


def draw_front(c, arm_l, arm_r):
    """
    Camada frontal (Painter's Algorithm):
    - Leques Tessen são renderizados aqui APENAS se as mãos estiverem à frente do tronco.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)

    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_fans_and_hands(c, hand_l, hand_r)
