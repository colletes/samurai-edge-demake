"""
Ichi, a Lâmina Cega e Mestra do Shikomizue (Ciclo 3 — Overhaul 2.18):
- Espadachim cega extraordinária de audição aguçada e reflexos imperceptíveis (homenagem à lenda de Zatoichi).
- Postura serena e equilibrada, ouvindo o respirar do vento, passos e corte de ar do adversário.
- Quimono de viagem ameixa-escuro com forro e colarinho branco puro em malha contínua 3D, envolto por xale de viagem.
- Cabelos negros refinados presos em coque tradicional elevado (Mage) com grampo de madeira nobre (kanzashi).
- Olhos suaves leitosos/cerrados em contemplação serena e foco absoluto.
- Espada-Bengala Oculta (Shikomizue):
  - Bastão de madeira nobre lisa de cerejeira parecendo uma bengala de caminhada inofensiva.
  - Lâmina interna de aço dobrado de altíssima pureza com fio de navalha e rastro prateado reluzente.
  - Ordenação dinâmica Painter's Algorithm para oclusão 360° e rig de membros com Pose LERP 0.08s.
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

SKIN = (212, 185, 172)
SKIN_SHADOW = (175, 142, 130)

PALETTE = {
    # Quimono de Viagem e Xale
    "kimono": (46, 28, 48),
    "torso": (46, 28, 48),
    "kimono_dark": (28, 18, 30),
    "kimono_light": (68, 42, 72),
    "kimono_trim": (118, 92, 122),
    "collar_white": (244, 240, 234),
    "scarf": (38, 36, 42),
    "scarf_dark": (24, 22, 28),

    # Obi e Adornos
    "obi": (26, 22, 30),
    "belt": (26, 22, 30),
    "obijime": (195, 160, 80),

    # Cabelo e Kanzashi
    "hair": (18, 16, 20),
    "hair_dark": (12, 10, 14),
    "kanzashi": (135, 78, 42),
    "kanzashi_gold": (218, 172, 75),

    # Anatomia e Expressão Cega
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "blind_eye": (188, 198, 218),
    "blind_core": (232, 238, 250),
    "eyelid": (212, 178, 154),
    "lash": (28, 22, 28),
    "lip": (205, 120, 130),
    "lip_shadow": (165, 80, 90),

    # Calçados e Pernas
    "tabi": (242, 238, 232),
    "geta": (135, 92, 58),
    "geta_dark": (95, 62, 38),
    "strap": (32, 26, 32),
    "pants": (46, 28, 48),

    # Shikomizue (Espada-Bengala Oculta)
    "cane_wood": (72, 44, 30),
    "cane_dark": (46, 26, 18),
    "brass_fitting": (210, 172, 70),
    "steel_blade": (235, 242, 255),
    "steel_edge": (255, 255, 255),
    "blood_groove": (180, 195, 215),

    # Rastros de Corte em Vácuo Prateado
    "slash_silver": (215, 235, 255),
    "slash_core": (255, 255, 255),
}

MATERIALS = {
    "kimono": "silk",
    "kimono_dark": "silk",
    "scarf": "canvas",
    "obi": "silk",
    "cane_wood": "wood",
    "steel_blade": "metal",
    "steel_edge": "metal",
    "brass_fitting": "metal",
    "geta": "wood",
}

LEGACY_MATERIALS = {k: "matte" for k in MATERIALS}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses de Braços e Animação de Combate Shikomizue
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Postura da Bengala de Viagem de Ichi:
    - Mão direita apoia o topo da empunhadura da shikomizue em repouso vertical.
    - Mão esquerda levemente apoiada no corpo da bengala.
    - Respiração viva contínua.
    """
    breathe = math.sin(c.walk_timer * 2.2) * 0.010
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    right = (
        bx + fx * 0.16 + px * 0.08,
        by + fy * 0.16 + py * 0.08,
        tz + 0.16
    )
    left = (
        bx + fx * 0.14 + px * 0.06,
        by + fy * 0.14 + py * 0.06,
        tz + 0.02
    )
    return left, right


def walk_arms(c):
    """Caminhada tateante da bengala (bengala guiando os passos com calma)."""
    tap = math.sin(c.walk_timer * 6.5) * 0.08
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    right = (
        bx + fx * (0.18 + tap * 0.06) + px * 0.08,
        by + fy * (0.18 + tap * 0.06) + py * 0.08,
        tz + 0.16 + abs(tap) * 0.02
    )
    left = (
        bx + fx * 0.10 - px * 0.08,
        by + fy * 0.10 - py * 0.08,
        tz + 0.06
    )
    return left, right


def attack_arms(c):
    """
    Golpe Gyaku-Iai Cego (Opção A):
    - O aço prateado se desvencilha da madeira da bengala em fração de segundo.
    - Saque horizontal relâmpago com pegada invertida.
    """
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    prog = c.atk_progress

    is_pierce = c.extra_props.get("is_pierce", False) if c.extra_props else False
    if is_pierce:
        left = (bx - fx * 0.08 + px * 0.12, by - fy * 0.08 + py * 0.12, tz + 0.10)
        right = (bx + fx * 0.38 - px * 0.02, by + fy * 0.38 - py * 0.02, tz + 0.14)
        return left, right

    if prog < 0.25:
        p_sub = prog / 0.25
        left = (
            bx + fx * (0.14 - p_sub * 0.02) + px * (0.06 + p_sub * 0.04),
            by + fy * (0.14 - p_sub * 0.02) + py * (0.06 + p_sub * 0.04),
            tz + 0.04 + p_sub * 0.06
        )
        right = (
            bx + fx * (0.16 - p_sub * 0.06) + px * (0.08 - p_sub * 0.16),
            by + fy * (0.16 - p_sub * 0.06) + py * (0.08 - p_sub * 0.16),
            tz + 0.16 - p_sub * 0.02
        )
    elif prog < 0.65:
        p_sub = (prog - 0.25) / 0.40
        arc_ang = -1.2 + p_sub * 2.5
        left = (bx - fx * 0.10 + px * 0.12, by - fy * 0.10 + py * 0.12, tz + 0.08)
        rx = bx + fx * 0.25 + px * (math.sin(arc_ang) * 0.28)
        ry = by + fy * 0.25 + py * (math.sin(arc_ang) * 0.28)
        right = (rx, ry, tz + 0.12)
    else:
        p_sub = (prog - 0.65) / 0.35
        left = (
            bx - fx * (0.10 - p_sub * 0.04) + px * (0.12 - p_sub * 0.02),
            by - fy * (0.10 - p_sub * 0.04) + py * (0.12 - p_sub * 0.02),
            tz + 0.08 + p_sub * 0.01
        )
        right = (
            bx + fx * (0.28 - p_sub * 0.04) + px * (0.22 - p_sub * 0.06),
            by + fy * (0.28 - p_sub * 0.04) + py * (0.22 - p_sub * 0.06),
            tz + 0.12 + p_sub * 0.02
        )

    return left, right


def _hands(c):
    """Calcula posição instantânea das mãos para ordenação de profundidade e renderização articulada."""
    extra = c.extra_props if c.extra_props else {}
    pose = extra.get("pose")
    u = extra.get("seg_u", extra.get("p", 0.0))
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    # 1. Esquiva Evasiva / Cane Tap Slip (13 i-frames)
    if extra.get("is_roll", False) or pose in ("cane_slip", "cane_tap_slip"):
        roll_p = extra.get("roll_prog", u)
        slip_s = math.sin(roll_p * math.pi)
        right = (
            bx + fx * (0.16 + slip_s * 0.08) + px * 0.10,
            by + fy * (0.16 + slip_s * 0.08) + py * 0.10,
            tz + 0.14 - slip_s * 0.05
        )
        left = (
            bx - fx * (0.04 + slip_s * 0.06) - px * 0.08,
            by - fy * (0.04 + slip_s * 0.06) - py * 0.08,
            tz + 0.06 - slip_s * 0.03
        )
        return left, right

    # 2. Postura de Escuta Sensorial (Listen Stance)
    if pose == "listen_stance" or extra.get("is_listen", False):
        listen_w = math.sin(u * math.pi * 3.0) * 0.008
        right = (
            bx + fx * 0.14 + px * 0.05,
            by + fy * 0.14 + py * 0.05,
            tz + 0.18 + listen_w
        )
        left = (
            bx + fx * 0.12 + px * 0.04,
            by + fy * 0.12 + py * 0.04,
            tz + 0.06 + listen_w
        )
        return left, right

    # 3. Contra-Ataque Perfurante / Blind Counter-Thrust
    if pose in ("counter_thrust", "blind_counter_thrust") or extra.get("is_pierce", False):
        left = (bx - fx * 0.08 + px * 0.12, by - fy * 0.08 + py * 0.12, tz + 0.10)
        right = (bx + fx * 0.38 - px * 0.02, by + fy * 0.38 - py * 0.02, tz + 0.14)
        return left, right

    # 4. Defesa com a Bainha / Sheath Parry
    if pose in ("sheath_parry", "parry_reaction") or extra.get("is_parry", False):
        left = (bx + fx * 0.16 - px * 0.08, by + fy * 0.16 - py * 0.08, tz + 0.16)
        right = (bx + fx * 0.20 + px * 0.08, by + fy * 0.20 + py * 0.08, tz + 0.18)
        return left, right

    # 5. Intro Fase 1: Caminhada Tateante da Bengala (0.00 -> 0.35)
    if pose == "cane_ground_listen":
        tap = math.sin(u * math.pi * 3.5) * 0.06
        right = (
            bx + fx * (0.16 + tap * 0.05) + px * 0.08,
            by + fy * (0.16 + tap * 0.05) + py * 0.08,
            tz + 0.16 + abs(tap) * 0.02
        )
        left = (
            bx + fx * 0.12 - px * 0.06,
            by + fy * 0.12 - py * 0.06,
            tz + 0.05
        )
        return left, right

    # 6. Intro Fase 2: Destrave do Aço com o Polegar (0.35 -> 0.70)
    if pose == "blade_unlock_thumb":
        click = math.sin(min(1.0, u * 1.5) * (math.pi * 0.5))
        left = (
            bx + fx * 0.14 + px * 0.06,
            by + fy * 0.14 + py * 0.06,
            tz + 0.06
        )
        right = (
            bx + fx * 0.15 + px * (0.07 + click * 0.015),
            by + fy * 0.15 + py * (0.07 + click * 0.015),
            tz + 0.16 + click * 0.025
        )
        return left, right

    # 7. Intro Fase 3: Postura Serena de Combate com Respiração Viva (0.70 -> 1.00)
    if pose == "serene_ready_stance":
        breathe = math.sin(u * math.pi * 4.0) * 0.010
        right = (
            bx + fx * 0.16 + px * 0.08,
            by + fy * 0.16 + py * 0.08,
            tz + 0.17 + breathe
        )
        left = (
            bx + fx * 0.14 + px * 0.06,
            by + fy * 0.14 + py * 0.06,
            tz + 0.05 + breathe * 0.5
        )
        return left, right

    # 8. Vitória Fase 1: Limpeza da Lâmina no Forro da Manga (0.00 -> 0.38)
    if pose == "blade_sleeve_wipe":
        wipe = math.sin(u * math.pi)
        left = (
            bx + fx * 0.12 - px * 0.10,
            by + fy * 0.12 - py * 0.10,
            tz + 0.12
        )
        right = (
            bx + fx * 0.14 - px * (0.06 + wipe * 0.08),
            by + fy * 0.14 - py * (0.06 + wipe * 0.08),
            tz + 0.14 - wipe * 0.04
        )
        return left, right

    # 9. Vitória Fase 2: Embainhar com Clique Audível (0.38 -> 0.72)
    if pose == "sheath_click_lock":
        slide = min(1.0, u * 1.2)
        left = (
            bx + fx * 0.14 + px * 0.06,
            by + fy * 0.14 + py * 0.06,
            tz + 0.04
        )
        right = (
            bx + fx * 0.15 + px * (0.08 - slide * 0.01),
            by + fy * 0.15 + py * (0.08 - slide * 0.01),
            tz + 0.22 - slide * 0.06
        )
        return left, right

    # 10. Vitória Fase 3: Repouso Sereno da Bengala (0.72 -> 1.00)
    if pose == "serene_cane_rest":
        breathe = math.sin(u * math.pi * 4.0) * 0.010
        right = (
            bx + fx * 0.16 + px * 0.08,
            by + fy * 0.16 + py * 0.08,
            tz + 0.16 + breathe
        )
        left = (
            bx + fx * 0.14 + px * 0.06,
            by + fy * 0.14 + py * 0.06,
            tz + 0.03 + breathe * 0.6
        )
        return left, right

    # 11. Ataque de Golpe Primário / Secundário
    if getattr(c, "is_melee", False):
        return attack_arms(c)

    # 12. Movimento / Caminhada
    if getattr(c, "is_moving", False):
        return walk_arms(c)

    # 13. Padrão Idle
    return idle_arms(c)


def get_arms(c):
    """Interface padrão para consulta modular de membros superiores articulados."""
    return _hands(c)


# ---------------------------------------------------------------------------------------------------------------------
# Detalhamento Voxel do Guerreiro
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Coque tradicional elevado (Mage) com kanzashi de cerejeira (se visto de costas).
    - Pontas do xale de viagem caindo pelas costas em malha contínua 3D.
    - Se a bengala estiver atrás do corpo, desenha aqui antes do quimono.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    hz = c.head_z
    d_torso = mk.depth(c, bx, by)

    # Coque tradicional elevado (Mage) nas costas da cabeça
    d_bun = mk.depth(c, bx - fx * 0.06, by - fy * 0.06)
    if d_bun <= d_torso + 0.02:
        bun_pos = (bx - fx * 0.05, by - fy * 0.05, hz + 0.165)
        mk.obox(c, bun_pos, (-fx, -fy, 0.0), 0.065, 0.075, 0.065, P["hair_dark"], outline=True)
        # Grampo Kanzashi de madeira nobre atravessando o coque
        mk.obox(c, (bun_pos[0] - px * 0.08, bun_pos[1] - py * 0.08, bun_pos[2] + 0.01), (px, py, 0.0), 0.16, 0.014, 0.014, P["kanzashi"], outline=False)
        mk.obox(c, (bun_pos[0] + px * 0.08, bun_pos[1] + py * 0.08, bun_pos[2] + 0.01), (px, py, 0.0), 0.02, 0.018, 0.018, P["kanzashi_gold"], outline=False)

    # Xale de viagem caindo pelas costas em fita 3D
    trail, amp, freq = mk.motion(c, 0.05)
    o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.7, trail, (-fx, -fy), amp=amp * 0.8, freq=freq)
    p0 = (bx - fx * 0.08, by - fy * 0.08, tz + 0.22)
    p1 = (bx - fx * 0.10 + o1[0], by - fy * 0.10 + o1[1], tz + 0.12 + o1[2])
    p2 = (bx - fx * 0.12 + o2[0], by - fy * 0.12 + o2[1], tz + 0.02 + o2[2])
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1, p2],
        widths=[0.125, 0.135, 0.140],
        depth_thick=0.025,
        colors=[P["scarf"], P["scarf_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Ordenação dinâmica da bengala
    hand_l, hand_r = _hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_shikomizue(c, hand_l, hand_r)


def draw_legs(c):
    """
    Quimono de viagem ameixa em malha contínua 3D descendo até os tornozelos,
    meias tabi brancas e calçado geta.
    """
    P = pal()
    trail, amp, freq = mk.motion(c, 0.03)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))

    for side in order:
        th = c.legs_data[side]["thigh"]
        sh = c.legs_data[side]["shin"]
        foot = c.legs_data[side]["foot"]
        sign = 1.0 if side == "L" else -1.0

        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.8 * sign, trail, (c.px, c.py), amp=amp * 0.4, freq=freq)

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.3, sh[1] + o1[1] * 0.3, sh[2] + 0.15)
        hem = (sh[0] + o1[0] * 0.15, sh[1] + o1[1] * 0.15, sh[2] + 0.06)
        ankle = (foot[0] + o2[0] * 0.2, foot[1] + o2[1] * 0.2, foot[2] + 0.03)

        # Quimono longo em malha contínua 3D
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, hem],
            widths=[0.115, 0.125, 0.130],
            depth_thick=0.032,
            colors=[P["kimono"], P["kimono_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

        # Bainha inferior com forro claro
        mk.band(c, [
            (hem[0] - c.px * 0.055, hem[1] - c.py * 0.055, hem[2]),
            (hem[0] + c.px * 0.055, hem[1] + c.py * 0.055, hem[2]),
            (hem[0] + c.px * 0.052, hem[1] + c.py * 0.052, hem[2] - 0.02),
            (hem[0] - c.px * 0.052, hem[1] - c.py * 0.052, hem[2] - 0.02),
        ], P["kimono_trim"])

        # Tornozelo com meia Tabi branca
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            hem, ankle,
            w_start=0.040, h_start=0.038,
            w_end=0.034, h_end=0.032,
            color=P["tabi"],
            up=(c.fx, c.fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

        # Calçado Geta de madeira tradicional
        sole_pos = (foot[0] + c.fx * 0.015, foot[1] + c.fy * 0.015, foot[2] + 0.012)
        mk.obox(c, sole_pos, (c.fx, c.fy, 0.0), 0.080, 0.038, 0.018, P["geta"], texture="wood")
        # Correias (Hanao)
        mk.obox(c, (sole_pos[0] + c.fx * 0.01, sole_pos[1] + c.fy * 0.01, sole_pos[2] + 0.012), (c.px, c.py, 0.0), 0.036, 0.010, 0.010, P["strap"], outline=False)


def draw_torso(c):
    """
    Tronco e Quimono de Ichi:
    - Obi elegante com cordão Obijime dourado.
    - Colarinho branco puro em V (Juban) e decote modesto.
    - Xale de viagem cinza envolto nos ombros.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    front = 0.065

    # Torso principal do quimono ameixa
    torso_top = (bx, by, tz + 0.24)
    torso_mid = (bx, by, tz + 0.12)
    torso_bot = (bx, by, tz + 0.01)

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[torso_top, torso_mid, torso_bot],
        widths=[0.160, 0.150, 0.145],
        depth_thick=0.080,
        colors=[P["kimono"], P["kimono_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Faixa Obi preta ajustada na cintura
    mk.obox(c, (bx, by, tz + 0.07), (0.0, 0.0, 1.0), 0.075, 0.155, 0.086, P["obi"], outline=False)
    # Cordão Obijime dourado no centro do Obi
    mk.obox(c, (bx + fx * (front + 0.005), by + fy * (front + 0.005), tz + 0.07), (px, py, 0.0), 0.156, 0.008, 0.008, P["obijime"], outline=False)

    if mk.depth(c, fx, fy) > -0.05:
        # Colarinho interno branco (Juban)
        apex = (bx + fx * (front + 0.002), by + fy * (front + 0.002), tz + 0.10)
        for s in (-1.0, 1.0):
            top = (bx + fx * front + px * 0.052 * s, by + fy * front + py * 0.052 * s, tz + 0.245)
            draw_tapered_frustum_3d(c.surface, c.camera, top, apex, w_start=0.022, h_start=0.012, w_end=0.015, h_end=0.008, color=P["collar_white"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)

        # Pele do decote
        mk.obox(c, (bx + fx * (front - 0.006), by + fy * (front - 0.006), tz + 0.14), (0.0, 0.0, 1.0), 0.08, 0.045, 0.014, P["skin"], up=(fx, fy, 0.0), outline=False)

        # Xale de viagem cobrindo os ombros e clavícula
        mk.obox(c, (bx + fx * 0.03, by + fy * 0.03, tz + 0.21), (0.0, 0.0, 1.0), 0.16, 0.15, 0.045, P["scarf"], up=(fx, fy, 0.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço ágil com manga de quimono."""
    P = pal()
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["kimono"],
        sleeve_to=0.58,
        w=0.048,
        bend=0.024
    )


def draw_head(c):
    """
    Cabeça e Cabelos de Ichi:
    - Feições serenas com olhos suaves cerrados/leitosos via draw_portrait_face_3d.
    - Cabelo negro com calota esculpida, franja contornada e coque tradicional Mage alto com Kanzashi dourado.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    cran_top = (bx - fx * 0.005, by - fy * 0.005, hz + 0.160)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, hz + 0.138), cran_top,
        w_start=hw * 0.94, h_start=hw * 0.94,
        w_end=hw * 0.70, h_end=hw * 0.70,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Coque tradicional elevado (Mage) no topo posterior
    bun_pos = (bx - fx * 0.045, by - fy * 0.045, hz + 0.165)
    mk.obox(c, bun_pos, (-fx, -fy, 0.0), 0.065, 0.075, 0.065, P["hair_dark"], outline=True)
    # Grampo Kanzashi de madeira nobre com ponta dourada
    mk.obox(c, (bun_pos[0] - px * 0.08, bun_pos[1] - py * 0.08, bun_pos[2] + 0.01), (px, py, 0.0), 0.16, 0.014, 0.014, P["kanzashi"], outline=False)
    mk.obox(c, (bun_pos[0] + px * 0.08, bun_pos[1] + py * 0.08, bun_pos[2] + 0.01), (px, py, 0.0), 0.02, 0.018, 0.018, P["kanzashi_gold"], outline=False)

    # Mechas laterais (tsuya-kami) emoldurando as maçãs do rosto
    for s in (-1.0, 1.0):
        lock_top = (bx + fx * 0.02 + px * 0.052 * s, by + fy * 0.02 + py * 0.052 * s, hz + 0.12)
        lock_bot = (bx + fx * 0.03 + px * 0.048 * s, by + fy * 0.03 + py * 0.048 * s, hz + 0.02)
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            lock_top, lock_bot,
            w_start=0.018, h_start=0.012,
            w_end=0.010, h_end=0.008,
            color=P["hair_dark"],
            up=(fx, fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

    # Franja suave acima das sobrancelhas
    bang_pos = (bx + fx * 0.055, by + fy * 0.055, hz + 0.122)
    mk.obox(c, bang_pos, (px, py, 0.0), 0.09, 0.025, 0.018, P["hair_dark"], outline=False)

    # Rostinho sereno em alta definição com olhos cerrados e lábios delicados
    draw_portrait_face_3d(c, char_type="ichi")
    c._face_drawn = True


# ---------------------------------------------------------------------------------------------------------------------
# Renderização da Shikomizue (Espada-Bengala Oculta) e Efeitos
# ---------------------------------------------------------------------------------------------------------------------

def _draw_cane_scabbard(c, hand_pt, direction, length=0.88):
    """Bainha/corpo de madeira nobre de cerejeira da bengala de caminhada."""
    P = pal()
    d = mk.norm(direction)
    mk.obox(c, hand_pt, d, length, 0.030, 0.030, P["cane_wood"], texture="wood")
    mk.obox(c, mk.add(hand_pt, d, length - 0.03), d, 0.032, 0.034, 0.034, P["brass_fitting"], outline=False)


def _draw_shikomizue_blade(c, hand_pt, direction, length=0.82):
    """Lâmina de katana sacada em pegada invertida."""
    P = pal()
    d = mk.norm(direction)

    # Empunhadura de cerejeira (topo da bengala que se solta)
    mk.obox(c, mk.add(hand_pt, d, -0.15), d, 0.15, 0.032, 0.032, P["cane_wood"], texture="wood")
    mk.obox(c, hand_pt, d, 0.022, 0.036, 0.036, P["brass_fitting"], outline=False)

    # Lâmina de aço retificado com linha de corte
    mk.obox(c, mk.add(hand_pt, d, 0.022), d, length, 0.034, 0.020, P["steel_blade"])
    mk.obox(c, mk.add(hand_pt, d, 0.030), d, max(0.0, length - 0.02), 0.014, 0.022, P["steel_edge"], outline=False)

    return mk.add(hand_pt, d, 0.022 + length)


def _render_shikomizue(c, left_hand, right_hand):
    """Renderiza a Shikomizue e os cortes Gyaku-Iai em combate."""
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    extra = c.extra_props if c.extra_props else {}
    pose = extra.get("pose")
    u = extra.get("seg_u", extra.get("p", 0.0))

    # Mãos humanas
    for hand in (left_hand, right_hand):
        mk.cbox(c, hand[0], hand[1], hand[2] - 0.015, 0.048, 0.048, 0.045, P["skin"], outline=True)

    # A. Ataque Primário (Gyaku-Iai) ou Contra-Ataque (Pierce)
    if c.is_melee:
        prog = c.atk_progress
        is_pierce = extra.get("is_pierce", False)

        if is_pierce:
            b_dir = mk.norm((fx * 0.95, fy * 0.95, 0.0))
            tip = _draw_shikomizue_blade(c, right_hand, b_dir, length=0.82)
            _draw_cane_scabbard(c, left_hand, mk.norm((-fx * 0.70 + px * 0.30, -fy * 0.70 + py * 0.30, -0.65)), length=0.85)
        else:
            if prog < 0.25:
                cane_dir = mk.norm((fx * 0.10 + px * 0.05, fy * 0.10 + py * 0.05, -0.98))
                _draw_cane_scabbard(c, right_hand, cane_dir, length=0.88)
            else:
                p_sub = (prog - 0.25) / 0.75
                arc_ang = -1.2 + p_sub * 2.5
                blade_dir = mk.norm((fx * math.cos(arc_ang) + px * math.sin(arc_ang), fy * math.cos(arc_ang) + py * math.sin(arc_ang), -0.05))
                tip = _draw_shikomizue_blade(c, right_hand, blade_dir, length=0.82)
                _draw_cane_scabbard(c, left_hand, mk.norm((-fx * 0.50 + px * 0.40, -fy * 0.50 + py * 0.40, -0.75)), length=0.85)

                if 0.10 < p_sub < 0.85:
                    mid = mk.lerp(right_hand, tip, 0.5)
                    prev_tip = (tip[0] - fx * 0.18, tip[1] - fy * 0.18, tip[2] + 0.05)
                    prev_mid = (mid[0] - fx * 0.10, mid[1] - fy * 0.10, mid[2] + 0.03)
                    mk.band(c, (mid, tip, prev_tip, prev_mid), P["slash_silver"] + (210,))
                    mk.band(c, (mk.lerp(mid, tip, 0.6), tip, prev_tip, mk.lerp(prev_mid, prev_tip, 0.6)), P["slash_core"] + (250,))
        return

    # B. Intro e Vitória
    if pose == "blade_unlock_thumb":
        # Destrave do aço pelo polegar: bengala com 2cm de lâmina exposta
        cane_dir = mk.norm((fx * 0.08 + px * 0.05, fy * 0.08 + py * 0.05, -0.98))
        _draw_cane_scabbard(c, left_hand, cane_dir, length=0.86)
        # Ponta de aço exposta
        mk.obox(c, (left_hand[0], left_hand[1], left_hand[2] + 0.03), (0.0, 0.0, 1.0), 0.035, 0.024, 0.016, P["steel_blade"])
        return

    if pose == "blade_sleeve_wipe":
        # Limpeza zen da lâmina no forro da manga
        b_dir = mk.norm((-fx * 0.30 - px * 0.80, -fy * 0.30 - py * 0.80, -0.20))
        _draw_shikomizue_blade(c, right_hand, b_dir, length=0.78)
        _draw_cane_scabbard(c, left_hand, mk.norm((fx * 0.20 + px * 0.20, fy * 0.20 + py * 0.20, -0.92)), length=0.85)
        return

    if pose == "sheath_click_lock":
        if u < 0.82:
            # Deslizando de volta na madeira
            b_dir = mk.norm((0.0, 0.0, -0.98))
            _draw_shikomizue_blade(c, right_hand, b_dir, length=0.76)
            _draw_cane_scabbard(c, left_hand, mk.norm((0.0, 0.0, -0.98)), length=0.86)
        else:
            # Travada e fechada
            cane_dir = mk.norm((fx * 0.08 + px * 0.05, fy * 0.08 + py * 0.05, -0.98))
            _draw_cane_scabbard(c, right_hand, cane_dir, length=0.88)
        return

    # C. Defesa com a Bainha (Sheath Parry)
    if pose in ("sheath_parry", "parry_reaction") or extra.get("is_parry", False):
        p_dir = mk.norm((px * 0.90 + fx * 0.15, py * 0.90 + fy * 0.15, 0.35))
        _draw_cane_scabbard(c, left_hand, p_dir, length=0.88)
        return

    # D. Estado Padrão: Bengala de caminhada vertical apoiada no chão
    cane_dir = mk.norm((fx * 0.08 + px * 0.05, fy * 0.08 + py * 0.05, -0.98))
    _draw_cane_scabbard(c, right_hand, cane_dir, length=0.88)


def draw_front(c, left_hand, right_hand):
    """Camada frontal: Shikomizue empunhada à frente do corpo."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    w_mid = ((left_hand[0] + right_hand[0]) * 0.5, (left_hand[1] + right_hand[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_shikomizue(c, left_hand, right_hand)
