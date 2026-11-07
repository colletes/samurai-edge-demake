"""
Goro, o Fazendeiro da Kuwa (Ciclo 3):
- Rebelde e camponês robusto da era Bakumatsu, de musculatura maciça e têmpera forjada no trabalho da terra.
- Tenugui índigo amarrado na testa sobre cabelos negros despenteados.
- Noragi (colete de trabalho) índigo aberto no peito com remendos e costuras sashiko rústicas.
- Corda de cânhamo torcida (shimenawa/nawa) amarrada na cintura como cinturão.
- Calças largas índigo presas por polainas de canela (kyahan) em malha contínua 3D e sandálias waraji reforçadas.
- Enxada de Aço Forjado (Kuwa):
  - Haste pesada de carvalho escuro envelhecido (~1.35m).
  - Lâmina de ferro forjada em ângulo, larga e letal com fio de corte prateado brilhante.
  - Ordenação dinâmica Painter's Algorithm para oclusão 360°.
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

SKIN = (212, 160, 122)
SKIN_SHADOW = (172, 122, 90)

PALETTE = {
    # Vestes de Camponês / Noragi Índigo
    "noragi": (28, 44, 70),
    "torso": (28, 44, 70),
    "noragi_dark": (18, 28, 48),
    "noragi_light": (42, 64, 98),
    "noragi_stitch": (195, 205, 220), # Costura Sashiko
    "undershirt": (48, 44, 40),
    "patch": (36, 52, 80),

    # Faixa da Cabeça e Cabelos
    "tenugui": (38, 58, 92),
    "tenugui_dark": (24, 38, 62),
    "hair": (24, 20, 22),
    "hair_dark": (14, 12, 14),
    "beard": (32, 26, 26),
    "eye": (30, 24, 20),
    "brow": (22, 18, 16),

    # Cinturão de Corda de Cânhamo e Pernas
    "rope_belt": (185, 155, 105),
    "rope_dark": (135, 108, 68),
    "belt": (185, 155, 105),
    "pants": (24, 38, 60),
    "pants_dark": (16, 26, 44),
    "kyahan": (62, 54, 44),
    "kyahan_strap": (24, 20, 22),
    "waraji": (165, 135, 90),
    "waraji_sole": (120, 95, 60),
    "mud": (65, 48, 34),

    # Anatomia
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "chest_hair": (36, 28, 24),

    # Kuwa (Enxada de Guerra de Aço)
    "wood_shaft": (54, 38, 26),
    "wood_dark": (36, 24, 16),
    "iron_bracket": (48, 52, 58),
    "iron_kuwa": (82, 88, 96),
    "steel_edge": (235, 242, 255),
    "trail_kuwa": (245, 230, 180),
    "trail_core": (255, 255, 240),
    "earth_dust": (145, 115, 80),
}

MATERIALS = {
    "noragi": "canvas",
    "noragi_dark": "canvas",
    "pants": "canvas",
    "kyahan": "canvas",
    "rope_belt": "canvas",
    "iron_kuwa": "metal",
    "steel_edge": "metal",
    "wood_shaft": "wood",
    "waraji": "canvas",
}
LEGACY_MATERIALS = {k: "matte" for k in MATERIALS}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses de Braços e Animação de Combate
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """
    Guarda imponente de Goro:
    - Apoia o pesado cabo da Kuwa descansando confortavelmente sobre o ombro direito.
    - Mão direita segura o cabo próximo ao peito, mão esquerda relaxada.
    """
    breathe = math.sin(c.walk_timer * 2.4) * 0.014
    tz = c.torso_z + breathe
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    pose = c.extra_props.get("pose") if c.extra_props else None

    if pose == "iron_guard":
        left = (bx + fx * 0.16 + px * 0.12, by + fy * 0.16 + py * 0.12, tz + 0.18)
        right = (bx + fx * 0.14 - px * 0.14, by + fy * 0.14 - py * 0.14, tz + 0.14)
        return left, right

    if pose == "kuwa_victory":
        right = (bx + fx * 0.08 - px * 0.16, by + fy * 0.08 - py * 0.16, tz + 0.38)
        left = (bx - fx * 0.10 + px * 0.18, by - fy * 0.10 + py * 0.18, tz + 0.04)
        return left, right

    # Mão direita segura o cabo da enxada apoiada no ombro
    right = (
        bx + fx * 0.12 - px * 0.13,
        by + fy * 0.12 - py * 0.13,
        tz + 0.16
    )
    # Mão esquerda repousa na frente do corpo
    left = (
        bx - fx * 0.04 + px * 0.15,
        by - fy * 0.04 + py * 0.15,
        tz + 0.04
    )
    return left, right


def walk_arms(c):
    """Caminhada pesada e determinada com a Kuwa equilibrada no ombro."""
    sw = math.sin(c.walk_timer * 7.5) * 0.12
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    right = (
        bx + fx * (0.12 + sw * 0.04) - px * 0.13,
        by + fy * (0.12 + sw * 0.04) - py * 0.13,
        tz + 0.16 + abs(sw) * 0.02
    )
    left = (
        bx - fx * (0.04 - sw * 0.06) + px * 0.15,
        by - fy * (0.04 - sw * 0.06) + py * 0.15,
        tz + 0.04 + abs(sw) * 0.02
    )
    return left, right


def attack_arms(c):
    """
    Golpe Brutal da Kuwa (KUWA_CLEAVE e Pisão):
    - Elevação maciça com ambas as mãos no início e descida esmagadora no clímax.
    """
    p = c.atk_progress
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    is_stomp = c.extra_props.get("is_stomp", False) if c.extra_props else False
    if is_stomp:
        left = (bx + fx * 0.15 + px * 0.18, by + fy * 0.15 + py * 0.18, tz + 0.12)
        right = (bx + fx * 0.18 - px * 0.12, by + fy * 0.18 - py * 0.12, tz + 0.18)
        return left, right

    if p < 0.35:
        # Preparação / Windup com a enxada erguida acima da cabeça
        wind = p / 0.35
        left = (bx + fx * 0.06 + px * 0.08, by + fy * 0.06 + py * 0.08, tz + 0.22 + wind * 0.32)
        right = (bx - fx * 0.06 - px * 0.08, by - fy * 0.06 - py * 0.08, tz + 0.24 + wind * 0.34)
    else:
        # Golpe descendente demolidor com alcance longo (2.40m)
        cleave = (p - 0.35) / 0.65
        cleave_curve = cleave ** 1.8
        reach = 0.24 + cleave_curve * 0.32
        cleave_z = tz + 0.52 - cleave_curve * 0.60
        left = (bx + fx * reach + px * 0.08, by + fy * reach + py * 0.08, cleave_z + 0.04)
        right = (bx + fx * (reach - 0.14) - px * 0.06, by + fy * (reach - 0.14) - py * 0.06, cleave_z)

    return left, right


def _hands(c):
    """Calcula posição instantânea das mãos para ordenação de profundidade e renderização articulada."""
    extra = c.extra_props if c.extra_props else {}
    pose = extra.get("pose")
    u = extra.get("seg_u", extra.get("p", 0.0))
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    # 1. Esquiva / Peasant Mud Roll (Rolamento de Lavrador)
    if extra.get("is_mud_roll", False) or extra.get("is_roll", False) or pose == "mud_roll":
        roll_p = extra.get("roll_prog", u)
        roll_s = math.sin(roll_p * math.pi)
        left = (
            bx + fx * (0.10 - roll_s * 0.05) + px * 0.12,
            by + fy * (0.10 - roll_s * 0.05) + py * 0.12,
            tz + 0.10 - roll_s * 0.04
        )
        right = (
            bx - fx * (0.08 + roll_s * 0.06) - px * 0.12,
            by - fy * (0.08 + roll_s * 0.06) - py * 0.12,
            tz + 0.08 - roll_s * 0.03
        )
        return left, right

    # 2. Cancelamento Evasivo / Pocket Dirt (Terra nos Olhos)
    if extra.get("is_pocket_dirt", False) or pose == "pocket_dirt":
        throw_prog = math.sin(u * math.pi)
        left = (
            bx + fx * (0.15 + u * 0.22) + px * 0.05,
            by + fy * (0.15 + u * 0.22) + py * 0.05,
            tz + 0.08 + throw_prog * 0.16
        )
        right = (
            bx - fx * 0.06 - px * 0.14,
            by - fy * 0.06 - py * 0.14,
            tz + 0.16
        )
        return left, right

    # 3. Intro Fase 1: Enxada no Ombro com Passadas Firmes (0.00 -> 0.35)
    if pose == "kuwa_shoulder_carry":
        sw = math.sin(u * math.pi * 3.0) * 0.04
        left = (
            bx - fx * (0.04 - sw) + px * 0.15,
            by - fy * (0.04 - sw) + py * 0.15,
            tz + 0.04 + abs(sw) * 0.02
        )
        right = (
            bx + fx * (0.12 + sw * 0.5) - px * 0.13,
            by + fy * (0.12 + sw * 0.5) - py * 0.13,
            tz + 0.16
        )
        return left, right

    # 4. Intro Fase 2: Ajuste do Tenugui e Cravada da Enxada (0.35 -> 0.70)
    if pose == "tenugui_tighten_plant":
        start_l = (bx - fx * 0.04 + px * 0.15, by - fy * 0.04 + py * 0.15, tz + 0.04)
        start_r = (bx + fx * 0.12 - px * 0.13, by + fy * 0.12 - py * 0.13, tz + 0.16)
        end_l = (bx - fx * 0.02 + px * 0.16, by - fy * 0.02 + py * 0.16, tz + 0.05)
        end_r = (bx + fx * 0.20 - px * 0.04, by + fy * 0.20 - py * 0.04, tz + 0.20)

        # Mão esquerda sobe até a testa para apertar o tenugui e depois desce
        tighten = math.sin(u * math.pi)
        left = (
            start_l[0] * (1.0 - u) + end_l[0] * u + px * tighten * 0.04,
            start_l[1] * (1.0 - u) + end_l[1] * u + py * tighten * 0.04,
            start_l[2] * (1.0 - u) + end_l[2] * u + tighten * 0.22
        )
        # Mão direita traz a enxada do ombro para a cravada firme à frente
        plant_s = u ** 1.5
        right = (
            start_r[0] * (1.0 - plant_s) + end_r[0] * plant_s,
            start_r[1] * (1.0 - plant_s) + end_r[1] * plant_s,
            start_r[2] * (1.0 - plant_s) + end_r[2] * plant_s
        )
        return left, right

    # 5. Intro Fase 3: Postura Rebelde com Peito Erguido (0.70 -> 1.00)
    if pose == "peasant_rebel_stance":
        breathe = math.sin(u * math.pi * 4.0) * 0.012
        left = (
            bx - fx * 0.02 + px * 0.16,
            by - fy * 0.02 + py * 0.16,
            tz + 0.05 + breathe * 0.5
        )
        right = (
            bx + fx * 0.20 - px * 0.04,
            by + fy * 0.20 - py * 0.04,
            tz + 0.20 + breathe
        )
        return left, right

    # 6. Vitória Fase 1: Crava e Descansa Ambas as Mãos no Cabo (0.00 -> 0.38)
    if pose == "kuwa_earth_rest":
        left = (
            bx + fx * 0.12 + px * 0.04,
            by + fy * 0.12 + py * 0.04,
            tz + 0.25
        )
        right = (
            bx + fx * 0.12 - px * 0.04,
            by + fy * 0.12 - py * 0.04,
            tz + 0.26
        )
        return left, right

    # 7. Vitória Fase 2: Enxuga Suor com a Ponta do Tenugui (0.38 -> 0.75)
    if pose == "sweat_wipe":
        start_l = (bx + fx * 0.12 + px * 0.04, by + fy * 0.12 + py * 0.04, tz + 0.25)
        end_l = (bx - fx * 0.02 + px * 0.18, by - fy * 0.02 + py * 0.18, tz + 0.06)
        wipe = math.sin(u * math.pi)
        left = (
            start_l[0] * (1.0 - u) + end_l[0] * u + px * wipe * 0.06,
            start_l[1] * (1.0 - u) + end_l[1] * u + py * wipe * 0.06,
            start_l[2] * (1.0 - u) + end_l[2] * u + wipe * 0.24
        )
        right = (
            bx + fx * 0.12 - px * 0.04,
            by + fy * 0.12 - py * 0.04,
            tz + 0.26
        )
        return left, right

    # 8. Vitória Fase 3: Risada Orgulhosa com Tórax Arfando (0.75 -> 1.00)
    if pose == "farmer_proud_laugh":
        laugh = math.sin(u * math.pi * 5.0) * 0.015
        left = (
            bx - fx * 0.02 + px * 0.18,
            by - fy * 0.02 + py * 0.18,
            tz + 0.06 + laugh * 0.4
        )
        right = (
            bx + fx * 0.12 - px * 0.04,
            by + fy * 0.12 - py * 0.04,
            tz + 0.26 + laugh
        )
        return left, right

    # 9. Guarda de Ferro / Bloqueio
    if pose == "iron_guard" or extra.get("is_parry", False):
        left = (bx + fx * 0.16 + px * 0.12, by + fy * 0.16 + py * 0.12, tz + 0.18)
        right = (bx + fx * 0.14 - px * 0.14, by + fy * 0.14 - py * 0.14, tz + 0.14)
        return left, right

    # 10. Pisotão Sísmico
    if extra.get("is_stomp", False) or pose == "earth_stomp":
        left = (bx + fx * 0.15 + px * 0.18, by + fy * 0.15 + py * 0.18, tz + 0.12)
        right = (bx + fx * 0.18 - px * 0.12, by + fy * 0.18 - py * 0.12, tz + 0.18)
        return left, right

    # 11. Ataque Primário
    if getattr(c, "is_melee", False):
        return attack_arms(c)

    # 12. Movimentação
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
    - Nó do tenugui atrás da cabeça com duas pontas de tecido.
    - Se a Kuwa estiver atrás do tronco, desenha aqui antes do noragi para oclusão limpa.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    hz = c.head_z
    hw = c.head_w + 0.01
    d_torso = mk.depth(c, bx, by)

    # Nó do tenugui atrás da cabeça
    d_nape = mk.depth(c, bx - fx * 0.08, by - fy * 0.08)
    if d_nape <= d_torso + 0.02:
        knot_pt = (bx - fx * (hw * 0.50 + 0.015), by - fy * (hw * 0.50 + 0.015), hz + 0.08)
        mk.obox(c, knot_pt, (-fx, -fy, 0.0), 0.045, 0.045, 0.045, P["tenugui_dark"], outline=False)

        trail, amp, freq = mk.motion(c, 0.05)
        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.8, trail, (px, py), amp=amp * 0.8, freq=freq)
        p0 = knot_pt
        p1 = (knot_pt[0] - fx * 0.04 + o1[0], knot_pt[1] - fy * 0.04 + o1[1], hz + 0.03 + o1[2])
        p2 = (knot_pt[0] - fx * 0.08 + o2[0], knot_pt[1] - fy * 0.08 + o2[1], hz - 0.04 + o2[2])
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[p0, p1, p2],
            widths=[0.035, 0.038, 0.028],
            depth_thick=0.014,
            colors=[P["tenugui"], P["tenugui_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(-fx, -fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

    # Ordenação dinâmica: se as mãos estiverem atrás do tronco ao encarar de costas
    hand_l, hand_r = _hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_kuwa(c, hand_l, hand_r)


def draw_legs(c):
    """
    Pernas musculosas em malha contínua 3D:
    - Calças largas índigo (hakama rústica) de camponês.
    - Polainas de canela terrosas (kyahan) enroladas.
    - Sandálias waraji com sola de corda e tiras reforçadas.
    """
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
        knee = (sh[0] + o1[0] * 0.4, sh[1] + o1[1] * 0.4, sh[2] + 0.16)
        cuff_pos = (sh[0] + o1[0] * 0.2, sh[1] + o1[1] * 0.2, sh[2] + 0.08)
        ankle = (foot[0] + o2[0] * 0.3, foot[1] + o2[1] * 0.3, foot[2] + 0.04)

        # Calça índigo folgada em malha contínua 3D
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos],
            widths=[0.125, 0.115, 0.098],
            depth_thick=0.095,
            colors=[P["pants"], P["pants_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Polaina de canela Kyahan em tecido terroso
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[cuff_pos, ankle],
            widths=[0.095, 0.082],
            depth_thick=0.082,
            colors=[P["kyahan"], P["kyahan"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Sandália Waraji de palha trançada com solado de corda
        flen, fwidth = 0.13, 0.072
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.016, flen, fwidth, 0.034, P["waraji"], outline=True)
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.003, flen + 0.004, fwidth + 0.004, 0.010, P["waraji_sole"], outline=False)


def draw_obi(c):
    """Cinturão de corda de cânhamo torcida (shimenawa rústica) com nós amarrados à frente."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.06

    mk.cbox(c, bx, by, z, c.pelvis_w + 0.010, c.pelvis_w * 0.74, 0.075, P["rope_belt"])
    mk.cbox(c, bx, by, z + 0.015, c.pelvis_w + 0.015, c.pelvis_w * 0.75, 0.030, P["rope_dark"], outline=False)

    # Nó frontal volumoso de corda com pontas caídas
    kx, ky = bx + fx * 0.10, by + fy * 0.10
    mk.cbox(c, kx, ky, z + 0.010, 0.065, 0.045, 0.065, P["rope_belt"], outline=False)
    mk.cbox(c, kx - px * 0.02, ky - py * 0.02, z - 0.045, 0.034, 0.028, 0.060, P["rope_dark"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braços fortes e musculosos com mangas curtas do noragi e munhequeiras de corda."""
    P = pal()
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["noragi"],
        sleeve_to=0.35,
        bracer=P["kyahan"],
        bracer_span=(0.60, 0.90),
        w=0.065,
        bend=0.032
    )


def draw_torso(c):
    """
    Tronco musculoso de trabalhador:
    - Noragi índigo com gola em V aberto no peito mostrando a têmpera rústica.
    - Remendo sashiko com costura no ombro.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    front = 0.098

    if mk.depth(c, fx, fy) > -0.05:
        # Peitoral musculoso exposto na abertura do colete
        mk.obox(c, (bx + fx * (front - 0.008), by + fy * (front - 0.008), tz + 0.10), (0.0, 0.0, 1.0), 0.14, 0.08, 0.016, P["skin"], up=(fx, fy, 0.0), outline=False)
        mk.obox(c, (bx + fx * front, by + fy * front, tz + 0.04), (0.0, 0.0, 1.0), 0.09, 0.05, 0.012, P["skin_shadow"], up=(fx, fy, 0.0), outline=False)

        # Abas do noragi índigo transpassadas
        for s in (-1.0, 1.0):
            top = (bx + fx * front + px * 0.075 * s, by + fy * front + py * 0.075 * s, tz + 0.245)
            apex = (bx + fx * (front + 0.004), by + fy * (front + 0.004), tz + 0.08)
            draw_tapered_frustum_3d(c.surface, c.camera, top, apex, w_start=0.032, h_start=0.016, w_end=0.022, h_end=0.012, color=P["noragi_dark"], up=(fx, fy, 0.0), outline=False, alpha=c.alpha)

        # Remendo sashiko no ombro direito
        mk.obox(c, (bx + px * 0.11, by + py * 0.11, tz + 0.22), (0.0, 0.0, 1.0), 0.065, 0.065, 0.015, P["patch"], up=(fx, fy, 0.0), outline=False)
        mk.obox(c, (bx + px * 0.11, by + py * 0.11, tz + 0.23), (0.0, 0.0, 1.0), 0.045, 0.045, 0.008, P["noragi_stitch"], up=(fx, fy, 0.0), outline=False)


def draw_head(c):
    """
    Cabeça de Goro:
    - Tenugui índigo na testa amarrado firme.
    - Cabelo negro espesso e rebelde.
    - Maxilar forte esculpido em 3D e barba por fazer.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # Cabelos negros despenteados no topo e nuca
    cran_top = (bx - fx * 0.005, by - fy * 0.005, hz + 0.165)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, hz + 0.138), cran_top,
        w_start=hw * 0.95, h_start=hw * 0.95,
        w_end=hw * 0.70, h_end=hw * 0.70,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Tenugui (faixa índigo na testa amarrada acima das sobrancelhas)
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.006
        t_len = hw * 0.94
        t_start = (bx + fx * front_d - px * (t_len * 0.50), by + fy * front_d - py * (t_len * 0.50), hz + 0.118)
        mk.obox(c, t_start, (px, py, 0.0), t_len, 0.022, 0.030, P["tenugui"], outline=True)

    legacy_mode = c.extra_props.get("legacy_mode", False) if c.extra_props else False
    if not legacy_mode and mk.depth(c, fx, fy) > -0.05:
        draw_portrait_face_3d(c, char_type="goro")
        c._face_drawn = True


# ---------------------------------------------------------------------------------------------------------------------
# Renderizador Especializado da Kuwa (Enxada de Aço Forjado)
# ---------------------------------------------------------------------------------------------------------------------

def _draw_kuwa_prop(c, hand_pt, direction, length=1.35):
    """
    Desenha a Kuwa (Enxada de Guerra de Camponês):
    - Cabo pesado de carvalho escuro (~1.35m).
    - Braçadeira de ferro forjado e lâmina perpendicular afiada com bisel de corte prateado.
    """
    P = pal()
    d = mk.norm(direction)
    grip_offset = 0.38

    # 1. Haste de madeira de carvalho escuro
    shaft_start = mk.add(hand_pt, d, -grip_offset)
    mk.obox(c, shaft_start, d, length, 0.038, 0.038, P["wood_shaft"], texture="wood")

    # 2. Cabeça da Enxada: braçadeira de ferro no topo
    head_pt = mk.add(shaft_start, d, length - 0.06)
    mk.obox(c, head_pt, d, 0.08, 0.052, 0.052, P["iron_bracket"], outline=True)

    # 3. Lâmina perpendicular afiada de ferro forjado
    blade_dir = mk.norm((-c.fx * 0.65, -c.fy * 0.65, -0.75))
    blade_len = 0.36
    mk.obox(c, head_pt, blade_dir, blade_len, 0.14, 0.028, P["iron_kuwa"], outline=True)
    # Fio de corte de aço afiado na ponta
    mk.obox(c, mk.add(head_pt, blade_dir, blade_len - 0.04), blade_dir, 0.04, 0.15, 0.022, P["steel_edge"], outline=False)

    return mk.add(head_pt, blade_dir, blade_len)


def _render_kuwa(c, left_hand, right_hand):
    """Renderiza a Kuwa empunhada e os rastros de choque telúricos."""
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    for hand in (left_hand, right_hand):
        mk.cbox(c, hand[0], hand[1], hand[2] - 0.015, 0.058, 0.058, 0.052, P["kyahan"], outline=True)

    if c.is_melee:
        p = c.atk_progress
        is_stomp = c.extra_props.get("is_stomp", False) if c.extra_props else False

        if is_stomp:
            kuwa_dir = mk.norm((fx * 0.35 + px * 0.40, fy * 0.35 + py * 0.40, 0.85))
            tip = _draw_kuwa_prop(c, right_hand, kuwa_dir, length=1.45)
        else:
            if p < 0.35:
                wind = p / 0.35
                kuwa_dir = mk.norm((fx * 0.15 - px * 0.25, fy * 0.15 - py * 0.25, 0.94))
                tip = _draw_kuwa_prop(c, right_hand, kuwa_dir, length=1.45)
            else:
                cleave = (p - 0.35) / 0.65
                cleave_curve = cleave ** 1.8
                kuwa_dir = mk.norm((fx * 0.85 + px * 0.10, fy * 0.85 + py * 0.10, -0.65))
                tip = _draw_kuwa_prop(c, right_hand, kuwa_dir, length=1.45)

                if 0.15 < cleave < 0.90:
                    mid = mk.lerp(right_hand, tip, 0.55)
                    prev_tip = (tip[0] - fx * 0.24, tip[1] - fy * 0.24, tip[2] + 0.20)
                    prev_mid = (mid[0] - fx * 0.15, mid[1] - fy * 0.15, mid[2] + 0.12)
                    mk.band(c, (mid, tip, prev_tip, prev_mid), P["trail_kuwa"] + (215,))
                    mk.band(c, (mk.lerp(mid, tip, 0.6), tip, prev_tip, mk.lerp(prev_mid, prev_tip, 0.6)), P["trail_core"] + (250,))

                if cleave > 0.70:
                    # Impacto telúrico e poeira de terra batida no solo
                    mk.cbox(c, tip[0], tip[1], 0.03, 0.16, 0.16, 0.04, P["earth_dust"], outline=False)
                    mk.cbox(c, tip[0] + fx * 0.06, tip[1] + fy * 0.06, 0.05, 0.08, 0.08, 0.06, P["iron_bracket"], outline=False)
    else:
        pose = c.extra_props.get("pose") if c.extra_props else None
        u = c.extra_props.get("seg_u", c.extra_props.get("p", 0.0)) if c.extra_props else 0.0

        if pose in ("kuwa_earth_rest", "sweat_wipe", "farmer_proud_laugh", "peasant_rebel_stance"):
            # Enxada cravada verticalmente no solo à frente
            planted_grip = (c.base_x + fx * 0.20 - px * 0.04, c.base_y + fy * 0.20 - py * 0.04, c.torso_z + 0.20)
            _draw_kuwa_prop(c, planted_grip, (0.0, 0.0, -1.0), length=1.45)
            # Pequeno monte de terra batida no ponto de fixação
            mk.cbox(c, planted_grip[0], planted_grip[1], 0.03, 0.14, 0.14, 0.05, P["earth_dust"], outline=False)
        elif pose == "tenugui_tighten_plant":
            # Transição: saindo do ombro e descendo até cravar na terra
            plant_s = u ** 1.5
            start_d = (-fx * 0.55 - px * 0.40, -fy * 0.55 - py * 0.40, 0.72)
            end_d = (0.0, 0.0, -1.0)
            cur_d = mk.norm((
                start_d[0] * (1.0 - plant_s) + end_d[0] * plant_s,
                start_d[1] * (1.0 - plant_s) + end_d[1] * plant_s,
                start_d[2] * (1.0 - plant_s) + end_d[2] * plant_s
            ))
            _draw_kuwa_prop(c, right_hand, cur_d, length=1.45)
        elif pose == "pocket_dirt":
            # Enxada recolhida na mão direita enquanto a esquerda atira terra
            kuwa_dir = mk.norm((-fx * 0.60 - px * 0.30, -fy * 0.60 - py * 0.30, 0.60))
            _draw_kuwa_prop(c, right_hand, kuwa_dir, length=1.45)
            # Nuvem de terra e cascalho lançada no rosto do rival
            cloud_p = math.sin(u * math.pi)
            if cloud_p > 0.08:
                sp_x = left_hand[0] + fx * (0.12 + u * 0.28)
                sp_y = left_hand[1] + fy * (0.12 + u * 0.28)
                sp_z = left_hand[2] + cloud_p * 0.08
                mk.cbox(c, sp_x, sp_y, sp_z, 0.16 * cloud_p, 0.16 * cloud_p, 0.10 * cloud_p, P["earth_dust"], outline=False)
                mk.cbox(c, sp_x + px * 0.06, sp_y + py * 0.06, sp_z + 0.04, 0.08 * cloud_p, 0.08 * cloud_p, 0.08 * cloud_p, P["mud"], outline=False)
        elif pose in ("mud_roll", "roll"):
            # Enxada rente ao flanco durante o rolamento de lavrador
            kuwa_dir = mk.norm((fx * 0.40 - px * 0.20, fy * 0.40 - py * 0.20, 0.20))
            _draw_kuwa_prop(c, right_hand, kuwa_dir, length=1.45)
        elif pose == "iron_guard":
            kuwa_dir = mk.norm((px * 0.95, py * 0.95, 0.30))
            _draw_kuwa_prop(c, right_hand, kuwa_dir, length=1.45)
        elif pose == "kuwa_victory":
            kuwa_dir = mk.norm((-fx * 0.15 - px * 0.25, -fy * 0.15 - py * 0.25, 0.96))
            _draw_kuwa_prop(c, right_hand, kuwa_dir, length=1.45)
        else:
            # Pousada no ombro direito apontando diagonalmente para trás
            kuwa_dir = mk.norm((-fx * 0.55 - px * 0.40, -fy * 0.55 - py * 0.40, 0.72))
            _draw_kuwa_prop(c, right_hand, kuwa_dir, length=1.45)


def draw_front(c, left_hand, right_hand):
    """Camada frontal: Kuwa empunhada à frente do tronco."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    w_mid = ((left_hand[0] + right_hand[0]) * 0.5, (left_hand[1] + right_hand[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_kuwa(c, left_hand, right_hand)
