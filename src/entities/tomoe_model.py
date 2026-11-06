"""
Tomoe, a Miko Kyudo Arqueira (Sacerdotisa Shinto do Arco Sagrado):
- Rosto anime gracioso com olhos luminosos castanho-quentes, brilho duplo e cílios alados; nariz delicado e lábios cereja.
- Cabelo longo negro sedoso (kurokami) em corte Hime com franja acima das sobrancelhas, mechas laterais (tsuya-kami) ordenadas por profundidade.
- Laço sagrado de seda escarlate (kami-musubi) amarrado na nuca com pontas longas esvoaçantes.
- Kosode cerimonial de seda branca pura com decote em V forrado em carmim escarlate e mangas drapeadas com cordões vermelhos (sode-kukuri).
- Hakama vermelha tradicional pregueada em malha 3D contínua (sem degraus ou prateleiras nos joelhos), tabi branco e sandálias Zori de palha com tiras de veludo carmim.
- Faixa na cintura com laço de cordão branco ceremonial e amuleto Omamori sagrado com sino dourado.
- Monumental arco longo assimétrico japonês Yumi (madeira de amoreira laqueada, núcleo de bambu dourado, ponteiras de latão e corda tsuru de seda branca) com flechas Ya de ponta de aço e penas brancas de falcão.
- Ordenação dinâmica de profundidade 3D (Painter's Algorithm) garantindo que arco e mãos fiquem perfeitamente ocluídos pelo dorso ao encarar de costas.
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
    "kosode": (252, 250, 248),
    "kosode_dark": (218, 214, 212),
    "collar_red": (195, 28, 36),
    "hakama": (195, 28, 36),
    "hakama_dark": (138, 18, 24),
    "hakama_crease": (165, 22, 28),
    "skin": (250, 228, 214),
    "skin_shadow": (224, 192, 175),
    "hair": (20, 20, 24),
    "hair_light": (45, 42, 52),
    "ribbon": (210, 32, 42),
    "ribbon_dark": (145, 18, 26),
    "tabi": (252, 250, 248),
    "zori": (195, 160, 115),
    "zori_cord": (195, 28, 36),
    "cord_white": (248, 248, 250),
    "omamori": (205, 30, 40),
    "omamori_gold": (235, 195, 65),
    "yumi_wood": (115, 68, 38),
    "yumi_bamboo": (185, 138, 75),
    "yumi_brass": (225, 185, 60),
    "tsuru": (250, 248, 240),
    "arrow_shaft": (168, 128, 72),
    "arrow_fletch": (245, 245, 248),
    "arrow_point": (215, 222, 235),
    "quiver": (68, 48, 38),
    "quiver_gold": (225, 185, 60),
}

MATERIALS = {
    "kosode": "silk", "kosode_dark": "silk",
    "collar_red": "silk", "hakama": "silk", "hakama_dark": "silk", "hakama_crease": "silk",
    "ribbon": "silk", "ribbon_dark": "silk", "zori": "canvas",
    "yumi_brass": "gold", "arrow_point": "steel", "arrow_shaft": "wood",
    "yumi_wood": "wood", "yumi_bamboo": "wood", "tsuru": "silk",
    "omamori_gold": "gold", "omamori": "silk",
}

LEGACY_MATERIALS = {
    "kosode": "matte", "kosode_dark": "matte",
    "collar_red": "matte", "hakama": "matte", "hakama_dark": "matte", "hakama_crease": "matte",
    "ribbon": "matte", "ribbon_dark": "matte", "zori": "matte",
    "yumi_brass": "matte", "arrow_point": "matte", "arrow_shaft": "matte",
    "yumi_wood": "matte", "yumi_bamboo": "matte", "tsuru": "matte",
    "omamori_gold": "matte", "omamori": "matte",
}


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Arco Yumi
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """Postura Kyudo neutra e serena: mão esquerda empunha o Yumi na altura da cintura ao lado, mão direita relaxada."""
    tz = c.torso_z + math.sin(c.walk_timer * 2.5) * 0.010
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    left = (bx + fx * 0.08 + px * 0.16, by + fy * 0.08 + py * 0.16, tz + 0.02)
    right = (bx + fx * 0.02 - px * 0.12, by + fy * 0.02 - py * 0.12, tz - 0.04)
    return left, right


def attack_arms(c):
    """Postura de disparo Kyudo (Kai): braço esquerdo estendido à frente sustentando o arco, direito puxando a corda junto à bochecha."""
    p = c.atk_progress if c.atk_progress is not None else 0.0
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    pull = math.sin(p * math.pi)
    left = (bx + fx * (0.24 + pull * 0.12) + px * 0.04,
            by + fy * (0.24 + pull * 0.12) + py * 0.04,
            tz + 0.14)
    right = (bx + fx * (0.04 - pull * 0.16) - px * (0.06 + pull * 0.06),
             by + fy * (0.04 - pull * 0.16) - py * (0.06 + pull * 0.06),
             tz + 0.16 + pull * 0.04)
    return left, right


def _hands(c):
    """
    Cinemática articulada modular de Tomoe (Miko Kyudo Arqueira):
    Retorna posição das mãos (mão esquerda que empunha o arco Yumi, mão direita que puxa a corda Tsuru e flechas).
    Suporta todas as 12 poses da Fase 2 Overhaul:
    - quick_snipe / attack_arms (disparo preciso com Yumi)
    - sacred_volley / aim_volley (chuva de flechas sagradas em arco balístico celeste)
    - rope_arrow / aim_rope (flecha de corda para salto/fuga tática)
    - dodge_cancel (cancelamento de mira em esquiva ágil)
    - parry_reaction (bloqueio sagrado cruzado com arco Yumi)
    - draw_sky_wind (Intro 1: arco erguido contra o vento)
    - test_tsuru_tension (Intro 2: teste de tensão e vibração da corda Tsuru)
    - serene_kyudo_stance (Intro 3: postura zen de arqueira Kyudo)
    - lower_yumi_rest (Vitória 1: arco pousado verticalmente no solo)
    - solemn_kami_bow (Vitória 2: reverência solene aos Kami com vênia cerimonial)
    - steady_breath_zen (Vitória 3: respiração tranquila com arco apoiado)
    - finisher_pinned (Finisher A: Jifuu Kyoukyuu / 地縫強弓 - flecha no peito cravando no solo)
    - finisher_volley (Finisher B: Hama Tenkan / 破魔天貫 - disparo zenital com feixe sagrado)
    """
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    p = extra.get("p", getattr(c, "atk_progress", 0.0) or 0.0)
    state = getattr(c, "state", "IDLE")

    bx, by, tz = c.base_x, c.base_y, c.torso_z
    fx = getattr(c, "fx", 1.0)
    fy = getattr(c, "fy", 0.0)
    px = getattr(c, "px", 0.0)
    py = getattr(c, "py", 1.0)

    # 0. Esquiva / Salto Acrobático Hakama (Miko Roll)
    if state == "ROLL" or pose in ("miko_roll", "dodge", "roll") or extra.get("is_roll", False):
        prog = float(extra.get("roll_prog", p if p is not None else 0.5))
        tuck = math.sin(prog * math.pi)
        left = (bx + fx * 0.12 - px * 0.08, by + fy * 0.12 - py * 0.08, tz + 0.06 - tuck * 0.08)
        right = (bx + fx * 0.10 + px * 0.10, by + fy * 0.10 + py * 0.10, tz + 0.06 - tuck * 0.08)
        return left, right

    # 1. Intro Fase 1: Vento Celeste (Arco erguido testando a direção do vento)
    if pose == "draw_sky_wind":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        start_l = (bx + fx * 0.12 + px * 0.14, by + fy * 0.12 + py * 0.14, tz + 0.08)
        peak_l = (bx + fx * 0.16 + px * 0.14, by + fy * 0.16 + py * 0.14, tz + 0.32)
        end_l = (bx + fx * 0.18 + px * 0.10, by + fy * 0.18 + py * 0.10, tz + 0.16)
        start_r = (bx + fx * 0.02 - px * 0.08, by + fy * 0.02 - py * 0.08, tz + 0.02)
        end_r = (bx + fx * 0.08 + px * 0.02, by + fy * 0.08 + py * 0.02, tz + 0.15)
        if u < 0.50:
            w = u / 0.50
            left = mk.lerp(start_l, peak_l, w)
            right = mk.lerp(start_r, (start_r[0], start_r[1], tz + 0.10), w)
        else:
            w = (u - 0.50) / 0.50
            left = mk.lerp(peak_l, end_l, w)
            right = mk.lerp((start_r[0], start_r[1], tz + 0.10), end_r, w)
        return left, right

    # 2. Intro Fase 2: Tensão da Corda Tsuru (Dedos testam a ressonância da corda)
    elif pose == "test_tsuru_tension":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        start_l = (bx + fx * 0.18 + px * 0.10, by + fy * 0.18 + py * 0.10, tz + 0.16)
        end_l = (bx + fx * 0.12 + px * 0.14, by + fy * 0.12 + py * 0.14, tz + 0.06)
        start_r = (bx + fx * 0.08 + px * 0.02, by + fy * 0.08 + py * 0.02, tz + 0.15)
        end_r = (bx + fx * 0.02 - px * 0.12, by + fy * 0.02 - py * 0.12, tz - 0.03)
        vib = math.sin(u * 22.0) * 0.012 * (1.0 - u * 0.5)
        left = mk.lerp(start_l, end_l, u)
        base_r = mk.lerp(start_r, end_r, u)
        right = (base_r[0] + fx * vib, base_r[1] + fy * vib, base_r[2] + vib)
        return left, right

    # 3. Intro Fase 3: Postura Kyudo Zen (Respiração serena e concentração máxima)
    elif pose == "serene_kyudo_stance":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        start_l = (bx + fx * 0.12 + px * 0.14, by + fy * 0.12 + py * 0.14, tz + 0.06)
        start_r = (bx + fx * 0.02 - px * 0.12, by + fy * 0.02 - py * 0.12, tz - 0.03)
        breath = math.sin(u * math.pi * 3.0) * 0.008
        left = (start_l[0], start_l[1], start_l[2] + breath)
        right = (start_r[0], start_r[1], start_r[2] + breath * 0.8)
        return left, right

    # 4. Vitória Fase 1: Pouso do Yumi no Solo (Apoia suavemente a extremidade inferior no piso)
    elif pose == "lower_yumi_rest":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        start_l = (bx + fx * 0.12 + px * 0.14, by + fy * 0.12 + py * 0.14, tz + 0.08)
        end_l = (bx + fx * 0.10 + px * 0.16, by + fy * 0.10 + py * 0.16, tz - 0.02)
        start_r = (bx + fx * 0.02 - px * 0.10, by + fy * 0.02 - py * 0.10, tz - 0.02)
        end_r = (bx + fx * 0.02 - px * 0.06, by + fy * 0.02 - py * 0.06, tz - 0.06)
        left = mk.lerp(start_l, end_l, u)
        right = mk.lerp(start_r, end_r, u)
        return left, right

    # 5. Vitória Fase 2: Reverência aos Kami (Vênia cerimonial solene com arco fixo)
    elif pose == "solemn_kami_bow":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        bow_pitch = math.sin(u * math.pi) * 0.14
        left = (bx + fx * 0.10 + px * 0.16, by + fy * 0.10 + py * 0.16, tz - 0.02 - bow_pitch * 0.4)
        right = (bx + fx * (0.02 + bow_pitch * 0.3) - px * 0.06, by + fy * (0.02 + bow_pitch * 0.3) - py * 0.06, tz - 0.06 - bow_pitch)
        return left, right

    # 6. Vitória Fase 3: Respiração Tranquila Zen (Respiração orgânica contínua)
    elif pose == "steady_breath_zen":
        u = _smooth(float(extra.get("seg_u", p if p is not None else 0.5)))
        start_l = (bx + fx * 0.10 + px * 0.16, by + fy * 0.10 + py * 0.16, tz - 0.02)
        start_r = (bx + fx * 0.02 - px * 0.06, by + fy * 0.02 - py * 0.06, tz - 0.06)
        breath = math.sin(u * math.pi * 3.0) * 0.008
        left = (start_l[0], start_l[1], start_l[2] + breath)
        right = (start_r[0], start_r[1], start_r[2] + breath * 0.7)
        return left, right

    # 7. Salva Sagrada Celeste em Arco (Sacred Volley / Aim Volley)
    elif pose in ("sacred_volley", "aim_volley") or extra.get("is_aiming_volley", False):
        u = _smooth(p)
        pull = math.sin(u * math.pi) if u > 0.0 else 0.8
        left = (bx + fx * 0.22 + px * 0.04, by + fy * 0.22 + py * 0.04, tz + 0.34)
        right = (bx + fx * (0.04 - pull * 0.10) - px * 0.06, by + fy * (0.04 - pull * 0.10) - py * 0.06, tz + 0.18 + pull * 0.04)
        return left, right

    # 8. Flecha de Corda Tática (Rope Arrow / Aim Rope)
    elif pose in ("rope_arrow", "aim_rope") or extra.get("is_charging_rope", False):
        u = _smooth(p)
        left = (bx + fx * 0.26 + px * 0.06, by + fy * 0.26 + py * 0.06, tz + 0.10)
        right = (bx + fx * 0.06 - px * 0.08, by + fy * 0.06 - py * 0.08, tz + 0.12)
        return left, right

    # 9. Reação de Bloqueio Sagrado (Parry Reaction)
    elif pose == "parry_reaction" or state == "PARRY":
        u = _smooth(p)
        deflect = math.sin(u * math.pi) * 0.04
        left = (bx + fx * (0.16 + deflect) + px * 0.12, by + fy * (0.16 + deflect) + py * 0.12, tz + 0.22)
        right = (bx + fx * (0.12 + deflect) - px * 0.14, by + fy * (0.12 + deflect) - py * 0.14, tz + 0.04)
        return left, right

    # 10. Finisher A: Jifuu Kyoukyuu / Flecha Pregada à Terra (PINNED_TO_EARTH)
    elif pose in ("finisher_pinned", "finisher_1"):
        u = _smooth(p)
        if u < 0.40:
            w = u / 0.40
            left = (bx + fx * (0.26 + 0.10 * w) + px * 0.02, by + fy * (0.26 + 0.10 * w) + py * 0.02, tz + 0.15)
            right = (bx + fx * (0.06 - 0.16 * w) - px * 0.08, by + fy * (0.06 - 0.16 * w) - py * 0.08, tz + 0.16)
        else:
            w = (u - 0.40) / 0.60
            left = (bx + fx * (0.36 + 0.04 * (1.0 - w)) + px * 0.02, by + fy * (0.36 + 0.04 * (1.0 - w)) + py * 0.02, tz + 0.15)
            right = (bx - fx * 0.10 - px * (0.08 + 0.08 * w), by - fy * 0.10 - py * (0.08 + 0.08 * w), tz + 0.16 + 0.04 * w)
        return left, right

    # 11. Finisher B: Hama Tenkan / Perfuração Sagrada Celeste (HAMAYA_HOLY_PIERCE)
    elif pose in ("finisher_volley", "finisher_2"):
        u = _smooth(p)
        if u < 0.45:
            w = u / 0.45
            left = (bx + fx * 0.22 + px * 0.02, by + fy * 0.22 + py * 0.02, tz + 0.25 + 0.18 * w)
            right = (bx + fx * (0.04 - 0.10 * w) - px * 0.06, by + fy * (0.04 - 0.10 * w) - py * 0.06, tz + 0.16)
        else:
            w = (u - 0.45) / 0.55
            left = (bx + fx * 0.24 + px * 0.02, by + fy * 0.24 + py * 0.02, tz + 0.43)
            right = (bx - fx * 0.08 - px * 0.12, by - fy * 0.08 - py * 0.12, tz + 0.20 + 0.05 * w)
        return left, right

    # 12. Ataque Primário / Quick Snipe / Disparo Yumi Convencional
    elif state == "ATTACK" or pose in ("quick_snipe", "fan_strike", "tanto_slash") or c.is_melee:
        return attack_arms(c)

    # 13. Movimentação / Caminhada
    elif c.is_moving and hasattr(c, "walk_timer"):
        sw = math.sin(c.walk_timer * 7.5) * 0.035
        left = (bx + fx * 0.10 + px * 0.14 + fx * sw, by + fy * 0.10 + py * 0.14 + fy * sw, tz + 0.04)
        right = (bx + fx * 0.04 - px * 0.12 - fx * sw, by + fy * 0.04 - py * 0.12 - fy * sw, tz - 0.02)
        return left, right

    return idle_arms(c)


def get_arms(c):
    """Exposição modular da cinemática dos braços para sincronização com o renderizador humanoide."""
    return _hands(c)


def _current_hands(c):
    return _hands(c)


# ---------------------------------------------------------------------------------------------------------------------
# Monumental Arco Yumi 3D
# ---------------------------------------------------------------------------------------------------------------------

def _draw_yumi_bow(c, hand_l, hand_r):
    """
    Renderiza o monumental arco longo japonês Yumi:
    - Curvatura assimétrica tradicional (2/3 da extensão acima da empunhadura, 1/3 abaixo).
    - Corpo laminado em madeira de amoreira laqueada e bambu dourado.
    - Ponteiras e colarinhos de latão (motohazu e urazu).
    - Corda de seda branca (tsuru) esticada ou tensionada até a mão direita.
    - Flecha sagrada (Ya ou Hamaya) nockada durante ataque, salva sagrada ou finalizações.
    """
    P = pal()
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    p = extra.get("p", getattr(c, "atk_progress", 0.0) or 0.0)
    state = getattr(c, "state", "IDLE")

    is_atk = (c.is_melee and c.atk_progress is not None) or state == "ATTACK" or pose in ("quick_snipe", "finisher_pinned", "finisher_1")
    is_aiming_sky = pose in ("sacred_volley", "aim_volley", "finisher_volley", "finisher_2") or extra.get("is_aiming_volley", False)
    is_parry = pose == "parry_reaction" or state == "PARRY"
    is_resting = pose in ("lower_yumi_rest", "solemn_kami_bow", "steady_breath_zen") or (not is_atk and not is_aiming_sky and not is_parry and not c.is_moving and pose not in ("draw_sky_wind", "test_tsuru_tension"))

    pull = math.sin(p * math.pi) if (is_atk or is_aiming_sky) else (0.4 if pose == "test_tsuru_tension" else 0.0)
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    if is_resting:
        # Arco em repouso vertical ao lado apoiado perto do solo
        grip = (hand_l[0] + fx * 0.02, hand_l[1] + fy * 0.02, hand_l[2] + 0.02)
        bow_dir = (0.0, 0.0, 1.0)
        p_top = (grip[0] + fx * 0.04, grip[1] + fy * 0.04, grip[2] + 0.72)
        p_bot = (grip[0] - fx * 0.02, grip[1] - fy * 0.02, grip[2] - 0.38)
        p_mid_up = mk.lerp(grip, p_top, 0.5)
        p_mid_down = mk.lerp(grip, p_bot, 0.5)

        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_top, w_start=0.032, h_start=0.024, w_end=0.022, h_end=0.016, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)
        mk.obox(c, p_mid_up, bow_dir, 0.35, 0.014, 0.025, P["yumi_bamboo"], up=(fx, fy, 0.0), outline=False)
        mk.obox(c, p_top, bow_dir, 0.035, 0.024, 0.024, P["yumi_brass"], outline=False)

        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_bot, w_start=0.032, h_start=0.024, w_end=0.024, h_end=0.018, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)
        mk.obox(c, p_mid_down, (0.0, 0.0, -1.0), 0.20, 0.014, 0.025, P["yumi_bamboo"], up=(fx, fy, 0.0), outline=False)
        mk.obox(c, p_bot, (0.0, 0.0, -1.0), 0.030, 0.024, 0.024, P["yumi_brass"], outline=False)

        mk.obox(c, (grip[0], grip[1], grip[2] - 0.04), bow_dir, 0.08, 0.036, 0.030, P["collar_red"], up=(fx, fy, 0.0), outline=False)

        t_top = (p_top[0] - fx * 0.03, p_top[1] - fy * 0.03, p_top[2] - 0.02)
        t_bot = (p_bot[0] - fx * 0.03, p_bot[1] - fy * 0.03, p_bot[2] + 0.02)
        mk.limb(c, t_top, t_bot, 0.010, P["tsuru"], outline=False)

    elif is_parry:
        # Arco empunhado diagonalmente diante do corpo como bastão protetor / barreira sagrada
        grip = (hand_l[0], hand_l[1], hand_l[2])
        bow_vec = mk.norm((px * 0.85 + fx * 0.15, py * 0.85 + fy * 0.15, 0.45))
        p_top = mk.add(grip, bow_vec, 0.65)
        p_bot = mk.add(grip, bow_vec, -0.42)

        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_top, w_start=0.034, h_start=0.024, w_end=0.022, h_end=0.016, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)
        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_bot, w_start=0.034, h_start=0.024, w_end=0.024, h_end=0.018, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)

        mk.obox(c, mk.add(grip, bow_vec, -0.04), bow_vec, 0.08, 0.036, 0.030, P["collar_red"], up=(fx, fy, 0.0), outline=False)
        t_top = mk.add(p_top, (-fx * 0.02, -fy * 0.02, 0.0), 1.0)
        t_bot = mk.add(p_bot, (-fx * 0.02, -fy * 0.02, 0.0), 1.0)
        mk.limb(c, t_top, t_bot, 0.010, P["tsuru"], outline=False)

    elif is_aiming_sky:
        # Arco erguido em arco balístico na direção dos céus (65° a 75° de elevação)
        grip = (hand_l[0] + fx * 0.04, hand_l[1] + fy * 0.04, hand_l[2] + 0.02)
        bow_vec = mk.norm((fx * 0.25 + px * 0.05, fy * 0.25 + py * 0.05, 1.25))

        p_top = mk.add(grip, bow_vec, 0.68)
        p_bot = mk.add(grip, bow_vec, -0.38)

        # Curvatura sob tensão
        c_curve = mk.norm((fx * 0.3, fy * 0.3, -0.7))
        p_top_c = mk.add(p_top, c_curve, -0.07 * pull)
        p_bot_c = mk.add(p_bot, c_curve, -0.05 * pull)

        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_top_c, w_start=0.034, h_start=0.024, w_end=0.022, h_end=0.016, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)
        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_bot_c, w_start=0.034, h_start=0.024, w_end=0.024, h_end=0.018, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)

        mk.obox(c, mk.add(grip, bow_vec, -0.04), bow_vec, 0.08, 0.036, 0.030, P["collar_red"], up=(fx, fy, 0.0), outline=False)

        t_top = mk.add(p_top_c, (-fx * 0.02, -fy * 0.02, -0.02), 1.0)
        t_bot = mk.add(p_bot_c, (-fx * 0.02, -fy * 0.02, 0.02), 1.0)
        nock_point = mk.add(hand_r, (fx * 0.02, fy * 0.02, 0.0), 1.0)

        mk.limb(c, t_top, nock_point, 0.010, P["tsuru"], outline=False)
        mk.limb(c, nock_point, t_bot, 0.010, P["tsuru"], outline=False)

        # Flecha Sagrada Hamaya dourada nockada apontada ao zênite
        if pull >= 0.15:
            arrow_dir = mk.norm(mk.sub(grip, nock_point))
            arrow_len = 0.62
            # Haste cerimonial branca
            mk.obox(c, nock_point, arrow_dir, arrow_len, 0.015, 0.015, (252, 248, 240), outline=False)
            # Ponta de ouro sagrada
            tip = mk.add(nock_point, arrow_dir, arrow_len)
            mk.obox(c, tip, arrow_dir, 0.050, 0.024, 0.016, (245, 215, 80), outline=False)
            # Penas cerimoniais douradas
            mk.obox(c, nock_point, arrow_dir, 0.09, 0.034, 0.012, (255, 235, 120), up=(0.0, 0.0, 1.0), outline=False)

    else:
        # Arco empunhado dinamicamente no ataque frontal ou corrida
        grip = (hand_l[0] + fx * 0.05, hand_l[1] + fy * 0.05, hand_l[2] + 0.02)
        bow_vec = mk.norm((fx * 0.15 + px * 0.05, fy * 0.15 + py * 0.05, 0.98))

        p_top = mk.add(grip, bow_vec, 0.70)
        p_bot = mk.add(grip, bow_vec, -0.38)

        # Curvatura no ataque sob tensão
        c_curve = mk.norm((fx, fy, 0.0))
        p_top_c = mk.add(p_top, c_curve, -0.06 * pull)
        p_bot_c = mk.add(p_bot, c_curve, -0.04 * pull)

        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_top_c, w_start=0.034, h_start=0.024, w_end=0.022, h_end=0.016, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)
        draw_tapered_frustum_3d(c.surface, c.camera, grip, p_bot_c, w_start=0.034, h_start=0.024, w_end=0.024, h_end=0.018, color=P["yumi_wood"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)

        # Empunhadura Nigiri
        mk.obox(c, mk.add(grip, bow_vec, -0.04), bow_vec, 0.08, 0.036, 0.030, P["collar_red"], up=(fx, fy, 0.0), outline=False)

        # Corda Tsuru (puxada até a mão direita no ataque)
        t_top = mk.add(p_top_c, (-fx * 0.02, -fy * 0.02, 0.0), 1.0)
        t_bot = mk.add(p_bot_c, (-fx * 0.02, -fy * 0.02, 0.0), 1.0)
        nock_point = mk.add(hand_r, (fx * 0.02, fy * 0.02, 0.0), 1.0) if (is_atk or pull > 0.05) else mk.lerp(t_top, t_bot, 0.5)

        mk.limb(c, t_top, nock_point, 0.010, P["tsuru"], outline=False)
        mk.limb(c, nock_point, t_bot, 0.010, P["tsuru"], outline=False)

        # Flecha sagrada Ya nockada
        if is_atk and pull >= 0.15:
            arrow_dir = mk.norm(mk.sub(grip, nock_point))
            arrow_len = 0.62
            # Haste de bambu
            mk.obox(c, nock_point, arrow_dir, arrow_len, 0.014, 0.014, P["arrow_shaft"], outline=False)
            # Ponta de aço afiado
            tip = mk.add(nock_point, arrow_dir, arrow_len)
            mk.obox(c, tip, arrow_dir, 0.045, 0.020, 0.014, P["arrow_point"], outline=False)
            # Penas de falcão brancas (fletching)
            mk.obox(c, nock_point, arrow_dir, 0.08, 0.030, 0.010, P["arrow_fletch"], up=(0.0, 0.0, 1.0), outline=False)


# ---------------------------------------------------------------------------------------------------------------------
# Cabelo Kurokami, Mechas Laterais e Laço Kami-Musubi
# ---------------------------------------------------------------------------------------------------------------------

def _lock_is_behind(c, side_sign):
    """Determina se a mecha lateral esquerda (-1) ou direita (+1) está atrás da cabeça."""
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    lx = bx + fx * 0.02 + px * 0.065 * side_sign
    ly = by + fy * 0.02 + py * 0.065 * side_sign
    return mk.depth(c, lx, ly) < mk.depth(c, bx, by) - 0.008


def _side_lock(c, side_sign):
    """Mecha lateral graciosa (tsuya-kami) emoldurando as bochechas no corte Hime."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.06)
    o = mk.cloth_offsets(c, 1, 0.8 * side_sign, trail, amp * 1.2, freq * 1.1, (bx, by))[0]

    p0 = (bx + fx * 0.042 + px * 0.048 * side_sign, by + fy * 0.042 + py * 0.048 * side_sign, hz + 0.138)
    p1 = (bx + fx * 0.046 + px * 0.052 * side_sign + o[0] * 0.4, by + fy * 0.046 + py * 0.052 * side_sign + o[1] * 0.4, hz + 0.070)
    p2 = (bx + fx * 0.048 + px * 0.048 * side_sign + o[0], by + fy * 0.048 + py * 0.048 * side_sign + o[1], hz + 0.005 + o[2])

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


def _draw_flowing_hair(c):
    """Cabelo longo negro sedoso (kurokami) descendo pelas costas até a cintura com ondulação de vento."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.08)

    # Raiz na nuca abaixo da fita vermelha
    p0 = (bx - fx * 0.065, by - fy * 0.065, hz + 0.100)

    offs = cloth.chain_offsets(3, c.walk_timer, 0.0, trail, (px, py), amp=amp * 1.8, freq=freq * 1.1, wind=cloth.wind_at(bx, by))

    p1 = (bx - fx * 0.085 + offs[0][0], by - fy * 0.085 + offs[0][1], hz + 0.020 + offs[0][2])
    p2 = (bx - fx * 0.095 + offs[1][0], by - fy * 0.095 + offs[1][1], c.torso_z + 0.080 + offs[1][2])
    p3 = (bx - fx * 0.105 + offs[2][0], by - fy * 0.105 + offs[2][1], c.pelvis_z + 0.060 + offs[2][2])

    # Faixa volumosa central de cabelo
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1, p2, p3],
        widths=[0.115, 0.135, 0.125, 0.085],
        depth_thick=0.045,
        colors=[P["hair"], P["hair_light"], P["hair"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )


def _draw_kami_musubi_ribbon(c):
    """Laço sagrado de seda carmim (kami-musubi) com asas volumosas e pontas esvoaçantes."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    root = (bx - fx * 0.075, by - fy * 0.075, hz + 0.115)

    # Nó central
    mk.cbox(c, root[0], root[1], root[2], 0.038, 0.038, 0.035, P["ribbon"])

    # Asas do laço arqueadas diagonalmente
    for s in (-1.0, 1.0):
        w_dir = mk.norm((px * s * 0.85 - fx * 0.15, py * s * 0.85 - fy * 0.15, 0.40))
        mk.obox(c, root, w_dir, 0.085, 0.024, 0.045, P["ribbon"], up=(fx, fy, 0.0), outline=False)

    # Fitas longas penduradas balançando
    trail, amp, freq = mk.motion(c, 0.07)
    for k, s in enumerate((-1.0, 1.0)):
        offs = cloth.chain_offsets(2, c.walk_timer, 0.9 * k, trail, (px, py), amp=amp * 1.6, freq=freq * 1.2)
        r0 = (root[0] + px * 0.015 * s, root[1] + py * 0.015 * s, root[2] - 0.015)
        r1 = (r0[0] - fx * 0.02 + offs[0][0], r0[1] - fy * 0.02 + offs[0][1], r0[2] - 0.06 + offs[0][2])
        r2 = (r1[0] - fx * 0.02 + offs[1][0], r1[1] - fy * 0.02 + offs[1][1], r1[2] - 0.07 + offs[1][2])
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[r0, r1, r2],
            widths=[0.024, 0.020, 0.014],
            depth_thick=0.008,
            colors=[P["ribbon"], P["ribbon_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(-fx, -fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )


# ---------------------------------------------------------------------------------------------------------------------
# Ganchos de Renderização (Painter's Algorithm)
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Mechas laterais que caem no lado oculto da cabeça.
    - Cabelo longo esvoaçante e laço Kami-Musubi nas costas.
    - Arco Yumi e mãos se estiverem atrás do tronco ao encarar de costas.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)

    # 1. Mechas laterais do lado oculto
    for s in (-1.0, 1.0):
        if _lock_is_behind(c, s):
            _side_lock(c, s)

    # 2. Cabelo longo e laço traseiro se atrás do crânio
    d_back_hair = mk.depth(c, c.base_x - c.fx * 0.08, c.base_y - c.fy * 0.08)
    if d_back_hair <= d_torso + 0.02:
        _draw_flowing_hair(c)
        _draw_kami_musubi_ribbon(c)

    # 3. Yumi e mãos se estiverem atrás do tronco
    hand_l, hand_r = _current_hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _draw_yumi_bow(c, hand_l, hand_r)


def draw_legs(c):
    """Hakama vermelha pregueada contínua em malha 3D (sem degraus de joelho), tabi branco e zori de palha."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.04)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0
        flare = 0.04 * c.lunge_curve

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.8 * sign, trail, (c.px, c.py), amp=amp * 0.6, freq=freq, wind=cloth.wind_at(foot[0], foot[1]))

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.5, sh[1] + o1[1] * 0.5, sh[2] + 0.16)
        ankle = (foot[0] + o2[0] * 0.4, foot[1] + o2[1] * 0.4, foot[2] + 0.05)

        # Hakama pregueada ampla em malha 3D contínua
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, ankle],
            widths=[0.125, 0.155 + flare, 0.170 + flare],
            depth_thick=0.115,
            colors=[P["hakama"], P["hakama_dark"], P["hakama_crease"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Meia Tabi branca
        mk.obox(c, (foot[0] + c.fx * 0.015, foot[1] + c.fy * 0.015, foot[2] + 0.015), (c.fx, c.fy, 0.0), 0.11, 0.060, 0.038, P["tabi"])
        # Sandália Zori de palha com sola de madeira
        mk.obox(c, (foot[0], foot[1], foot[2] - 0.010), (c.fx, c.fy, 0.0), 0.125, 0.066, 0.018, P["zori"])
        # Tira de veludo carmim da zori
        mk.obox(c, (foot[0] + c.fx * 0.025, foot[1] + c.fy * 0.025, foot[2] + 0.025), (c.fx, c.fy, 0.0), 0.020, 0.068, 0.016, P["zori_cord"], outline=False)


def draw_obi(c):
    """Cós da Hakama carmim com cordões brancos cerimoniais atados na frente e Omamori no quadril."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    # Cós largo da hakama
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.008, c.pelvis_w * 0.76, 0.065, P["hakama_dark"])

    # Cordão cerimonial branco (himo)
    mk.cbox(c, bx + fx * 0.086, by + fy * 0.086, z + 0.010, 0.065, 0.022, 0.035, P["cord_white"], outline=False)

    # Pontas caídas do nó do cordão branco
    trail, amp, freq = mk.motion(c, 0.05)
    offs = cloth.chain_offsets(2, c.walk_timer, 0.8, trail, (px, py), amp=amp * 1.3, freq=freq)
    for i, o in enumerate(offs):
        mk.cbox(c, bx + fx * 0.095 + px * 0.018 + o[0],
                by + fy * 0.095 + py * 0.018 + o[1],
                z - 0.045 * (i + 1) + o[2],
                0.022, 0.016, 0.050, P["cord_white"], outline=False)

    # Amuleto sagrado Omamori carmim no quadril direito com sino dourado
    bag = (bx - px * 0.125 - fx * 0.02, by - py * 0.125 - fy * 0.02, z - 0.05)
    mk.obox(c, bag, (0.0, 0.0, -1.0), 0.075, 0.045, 0.022, P["omamori"], up=(px, py, 0.0), outline=False)
    # Sino dourado (suzu)
    mk.cbox(c, bag[0], bag[1], bag[2] + 0.015, 0.020, 0.020, 0.020, P["omamori_gold"], outline=False)


def draw_torso(c):
    """
    Kosode cerimonial de seda branca pura:
    - Colarinho em V com forro carmim exposto (eri).
    - Pele de porcelana delicada da clavícula à mostra.
    """
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.090

    # Decote frontal com forro carmim
    if mk.depth(c, fx, fy) > -0.05:
        apex = (bx + fx * front, by + fy * front, tz + 0.100)
        for s in (-1.0, 1.0):
            top = (bx + fx * (front - 0.003) + px * 0.052 * s, by + fy * (front - 0.003) + py * 0.052 * s, tz + 0.245)
            # Forro carmim
            draw_tapered_frustum_3d(c.surface, c.camera, top, apex, w_start=0.026, h_start=0.014, w_end=0.016, h_end=0.010, color=P["collar_red"], up=(0.0, 0.0, 1.0), outline=False, alpha=c.alpha)
            # Borda externa branca do Kosode
            top_w = (top[0] - px * 0.006 * s, top[1] - py * 0.006 * s, top[2] - 0.004)
            apex_w = (apex[0] - px * 0.004 * s, apex[1] - py * 0.004 * s, apex[2] + 0.006)
            draw_tapered_frustum_3d(c.surface, c.camera, top_w, apex_w, w_start=0.014, h_start=0.012, w_end=0.008, h_end=0.008, color=P["kosode_dark"], up=(0.0, 0.0, 1.0), outline=False, alpha=c.alpha)

        # Pele delicada no centro do decote
        mk.obox(c, (bx + fx * (front - 0.004), by + fy * (front - 0.004), tz + 0.155), (0.0, 0.0, 1.0), 0.075, 0.038, 0.014, P["skin"], up=(fx, fy, 0.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço esguio feminino de Miko."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.20)
    h = (hand[0], hand[1], hand[2] - 0.060)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.025), (0.0, 0.0, -0.025))

    mk.limb(c, s, e, 0.046, P["skin"], w_end=0.040)
    mk.limb(c, e, h, 0.040, P["skin"], w_end=0.034)
    mk.cbox(c, h[0], h[1], h[2] - 0.020, 0.040, 0.040, 0.040, P["skin"])
    return s, e


def draw_sleeves(c, arms):
    """Mangas amplas e fluidas de Miko em seda branca pura, com caimento vertical e cordões carmim (sode-kukuri)."""
    P = pal()
    for k, (s, e, side) in enumerate(arms):
        anchor = (s[0] + c.px * side * 0.015, s[1] + c.py * side * 0.015, s[2] + 0.008)
        mid = mk.add(mk.lerp(s, e, 0.45), (c.px * side * 0.025, c.py * side * 0.025, -0.035))
        hem = mk.add(mk.lerp(s, e, 0.85), (c.px * side * 0.035, c.py * side * 0.035, -0.110))

        # Manga de seda branca pura drapeada
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[anchor, mid, hem],
            widths=[0.105, 0.140, 0.160],
            depth_thick=0.078,
            colors=[P["kosode"], P["kosode_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Cordão carmim (sode-kukuri) atado no punho da manga
        mk.obox(c, (hem[0], hem[1], hem[2] + 0.012), (0.0, 0.0, -1.0),
                0.016, 0.160, 0.080, P["collar_red"], up=(c.fx, c.fy, 0.0), outline=False)


def draw_head(c):
    """
    Cabeça de Tomoe:
    - Crânio esculpido 3D com olhos castanho-quentes expressivos, nariz delicado e lábios cereja via draw_portrait_face_3d.
    - Franja Hime reta estritamente acima das sobrancelhas (z >= hz + 0.108).
    - Mechas laterais tsuya-kami emoldurando a face se visíveis da câmera.
    - Cabelo longo traseiro e laço Kami-Musubi (se visíveis da câmera).
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    d_torso = mk.depth(c, bx, by)

    # Franja reta Hime clássica estritamente acima das sobrancelhas (z >= hz + 0.108)
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.005
        # Painel central da franja reta
        p0 = (bx + fx * front_d, by + fy * front_d, hz + 0.140)
        p1 = (bx + fx * (front_d + 0.002), by + fy * (front_d + 0.002), hz + 0.116)
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            p0, p1,
            w_start=0.088, h_start=0.014,
            w_end=0.082, h_end=0.010,
            color=P["hair"],
            up=(0.0, 0.0, 1.0),
            outline=False,
            alpha=c.alpha,
        )

    # Mechas laterais tsuya-kami do lado visível da câmera
    for s in (-1.0, 1.0):
        if not _lock_is_behind(c, s):
            _side_lock(c, s)

    # Cabelo longo e laço traseiro se estiverem do lado visível da câmera
    d_back_hair = mk.depth(c, bx - fx * 0.08, by - fy * 0.08)
    if d_back_hair > d_torso + 0.02:
        _draw_flowing_hair(c)
        _draw_kami_musubi_ribbon(c)


def draw_front(c, arm_l, arm_r):
    """
    Camada frontal (Painter's Algorithm):
    - O monumental Yumi e flecha são desenhados aqui APENAS se as mãos/arco estiverem à frente do tronco.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.060)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.060)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)

    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _draw_yumi_bow(c, hand_l, hand_r)
