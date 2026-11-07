"""
Valerius, o Necromante Prussiano (Ciclo 4 — Overhaul 2.19):
- Aristocrata e ocultista prussiano da era Bakumatsu, de linhagem nobre e tez cadavérica gélida.
- Sobretudo militar gótico (frock coat) azul-noite/preto com dragonas douradas/prateadas e forro carmesim.
- Colete de brocado escuro com cravat de seda branca pura alto no pescoço e monóculo dourado no olho direito.
- Calças retas escuras em malha 3D contínua entrando em botas de montaria pretas lustrosas.
- Cabelos platinados grisalhos penteados para trás com volume aristocrático; olhos marciais gélidos cor de aço.
- Foice Fúnebre de Duelo (Funeral Scythe):
  - Haste pesada de ferro forjado e ébano com engastes dourados e prateados (~1.45m).
  - Lâmina recurva gótica de aço escuro com fio de corte prateado e labaredas de chamas azuis espectrais.
  - Ordenação dinâmica Painter's Algorithm para oclusão 360° e rig de membros com Pose LERP 0.08s.
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
    "epaulet_gold": (218, 182, 75),
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
    "eye": (110, 165, 205),
    "brow": (160, 168, 178),
    "lip": (175, 135, 138),
    "monocle_gold": (225, 185, 65),

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

    # Chamas Azuis Espectrais / Necromancia
    "spectral_aura": (60, 160, 255),
    "spectral_core": (205, 235, 255),
    "flame_blue": (40, 120, 240),
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

LEGACY_MATERIALS = {k: "matte" for k in MATERIALS}


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
        right = (bx + fx * (0.32 - t * 0.14) - px * 0.08, by + fy * (0.32 - t * 0.14) - py * 0.08, tz + 0.12 + t * 0.06)
        left = (bx + fx * (0.16 - t * 0.06) + px * (t * 0.10), by + fy * (0.16 - t * 0.06) + py * (t * 0.10), tz + 0.12 - t * 0.06)

    return left, right


def _hands(c):
    """Calcula posição instantânea dos braços e mãos para todas as 12 ações de combate e visualização."""
    extra = c.extra_props if c.extra_props else {}
    pose = extra.get("pose")
    u = extra.get("seg_u", extra.get("p", 0.0))
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    # 1. Esquiva: Dissipação em Névoa Espectral (Mist Dash)
    if extra.get("is_roll", False) or pose in ("mist_dash", "spectral_dash"):
        glide = math.sin(u * math.pi)
        right = (
            bx - fx * (0.05 + glide * 0.10) - px * 0.12,
            by - fy * (0.05 + glide * 0.10) - py * 0.12,
            tz + 0.14 - glide * 0.04
        )
        left = (
            bx - fx * (0.05 + glide * 0.10) + px * 0.12,
            by - fy * (0.05 + glide * 0.10) + py * 0.12,
            tz + 0.14 - glide * 0.04
        )
        return left, right

    # 2. Invocação de Servo 1: Rastejante de Tornozelos (Grasper)
    if pose in ("summon_grasper", "summon_undead_1"):
        right = (bx + fx * 0.12 - px * 0.08, by + fy * 0.12 - py * 0.08, tz + 0.18)
        # Mão esquerda aponta para o solo em rito de evocação
        left = (bx + fx * 0.22 + px * 0.10, by + fy * 0.22 + py * 0.10, tz - 0.08)
        return left, right

    # 3. Invocação de Servo 2: Soldado com Espada (Swordsman)
    if pose in ("summon_swordsman", "summon_undead_2"):
        right = (bx + fx * 0.12 - px * 0.08, by + fy * 0.12 - py * 0.08, tz + 0.18)
        # Mão esquerda aponta autoritária para a frente
        left = (bx + fx * 0.32 + px * 0.08, by + fy * 0.32 + py * 0.08, tz + 0.12)
        return left, right

    # 4. Invocação de Servo 3: Wight de Chamas Azuis (Wight)
    if pose in ("summon_wight", "summon_undead_3"):
        right = (bx + fx * 0.14 - px * 0.08, by + fy * 0.14 - py * 0.08, tz + 0.24)
        # Mão esquerda espalmada para o alto conjurando chamas
        left = (bx + fx * 0.18 + px * 0.14, by + fy * 0.18 + py * 0.14, tz + 0.26)
        return left, right

    # 5. Detonação de Cadáver / Corpse Detonation
    if pose in ("corpse_detonation", "finger_snap_detonate"):
        right = (bx + fx * 0.12 - px * 0.08, by + fy * 0.12 - py * 0.08, tz + 0.18)
        # Mão esquerda ergue-se para estalar os dedos
        snap = math.sin(u * math.pi)
        left = (bx + fx * 0.15 + px * 0.16, by + fy * 0.15 + py * 0.16, tz + 0.22 + snap * 0.04)
        return left, right

    # 6. Defesa com a Foice (Scythe Guard / Parry)
    if pose in ("scythe_guard", "parry_reaction") or extra.get("is_parry", False):
        right = (bx + fx * 0.18 - px * 0.06, by + fy * 0.18 - py * 0.06, tz + 0.22)
        left = (bx + fx * 0.14 + px * 0.10, by + fy * 0.14 + py * 0.10, tz + 0.12)
        return left, right

    # 7. Intro Fase 1: Vórtice de Névoa Fúnebre (0.00 -> 0.35)
    if pose == "mist_emergence":
        swirl = math.sin(u * math.pi * 2.0)
        right = (bx + fx * 0.08 - px * (0.06 + swirl * 0.04), by + fy * 0.08 - py * (0.06 + swirl * 0.04), tz + 0.12)
        left = (bx + fx * 0.08 + px * (0.06 + swirl * 0.04), by + fy * 0.08 + py * (0.06 + swirl * 0.04), tz + 0.08)
        return left, right

    # 8. Intro Fase 2: Ajuste de Monóculo e Manifestação da Foice (0.35 -> 0.70)
    if pose == "monocle_adjust":
        right = (bx + fx * 0.12 - px * 0.08, by + fy * 0.12 - py * 0.08, tz + 0.18)
        # Mão esquerda erguida ajustando o monóculo no olho direito
        left = (bx + fx * 0.10 + px * 0.06, by + fy * 0.10 + py * 0.06, tz + 0.32)
        return left, right

    # 9. Intro Fase 3: Postura Nobre de Duelista do Além (0.70 -> 1.00)
    if pose == "aristocrat_ready":
        breathe = math.sin(u * math.pi * 4.0) * 0.008
        right = (bx + fx * 0.12 - px * 0.08, by + fy * 0.12 - py * 0.08, tz + 0.18 + breathe)
        left = (bx + fx * 0.10 + px * 0.14, by + fy * 0.10 + py * 0.14, tz + 0.06 + breathe * 0.5)
        return left, right

    # 10. Vitória Fase 1: Dissipação da Foice em Brasas (0.00 -> 0.38)
    if pose == "scythe_dissipate":
        t = u
        right = (bx + fx * (0.12 - t * 0.06) - px * 0.08, by + fy * (0.12 - t * 0.06) - py * 0.08, tz + 0.18 - t * 0.08)
        left = (bx + fx * 0.10 + px * 0.14, by + fy * 0.10 + py * 0.14, tz + 0.06)
        return left, right

    # 11. Vitória Fase 2: Estalo de Dedos e Reverência Solene (0.38 -> 0.72)
    if pose == "finger_snap_bow":
        bow = math.sin(u * math.pi)
        right = (bx - fx * 0.04 - px * 0.10, by - fy * 0.04 - py * 0.10, tz + 0.06 - bow * 0.08)
        left = (bx + fx * 0.04 + px * 0.06, by + fy * 0.04 + py * 0.06, tz + 0.08 - bow * 0.08)
        return left, right

    # 12. Vitória Fase 3: Olhar Condescendente (0.72 -> 1.00)
    if pose == "condescending_gaze":
        breathe = math.sin(u * math.pi * 4.0) * 0.008
        right = (bx + fx * 0.08 - px * 0.10, by + fy * 0.08 - py * 0.10, tz + 0.10 + breathe)
        left = (bx + fx * 0.08 + px * 0.12, by + fy * 0.08 + py * 0.12, tz + 0.08 + breathe)
        return left, right

    # 13. Golpe Primário (Ceifada de Foice)
    if getattr(c, "is_melee", False):
        return attack_arms(c)

    # 14. Caminhada
    if getattr(c, "is_moving", False):
        return walk_arms(c)

    # 15. Padrão Idle
    return idle_arms(c)


def get_arms(c):
    """Interface padrão para consulta modular de membros superiores articulados."""
    return _hands(c)


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
    hand_l, hand_r = _hands(c)
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
            widths=[0.125, 0.115, 0.108],
            depth_thick=0.038,
            colors=[P["pants"], P["pants_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

        # Dobra superior da bota de cavalaria (Cuff)
        mk.obox(c, cuff_pos, (c.fx, c.fy, 0.0), 0.110, 0.098, 0.040, P["boot_cuff"], outline=False)

        # Cano da bota de montaria até o calcanhar
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            cuff_pos, ankle,
            w_start=0.048, h_start=0.045,
            w_end=0.040, h_end=0.038,
            color=P["boot"],
            up=(c.fx, c.fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

        # Pé e sola
        sole_pos = (foot[0] + c.fx * 0.02, foot[1] + c.fy * 0.02, foot[2] + 0.012)
        mk.obox(c, sole_pos, (c.fx, c.fy, 0.0), 0.095, 0.042, 0.022, P["boot"], outline=True)
        mk.obox(c, (sole_pos[0], sole_pos[1], sole_pos[2] - 0.008), (c.fx, c.fy, 0.0), 0.098, 0.044, 0.008, P["boot_sole"], outline=False)


def draw_torso(c):
    """
    Tronco de Valerius:
    - Sobretudo militar prussiano azul-noite/preto com dragonas e bordados prateados.
    - Colete de brocado escuro com cravat de seda branca pura e botões metálicos.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    # Sobretudo militar principal (Frock Coat) em malha 3D
    torso_top = (bx, by, tz + 0.25)
    torso_mid = (bx, by, tz + 0.13)
    torso_bot = (bx, by, tz + 0.02)

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[torso_top, torso_mid, torso_bot],
        widths=[0.175, 0.165, 0.155],
        depth_thick=0.095,
        colors=[P["coat"], P["coat_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Detalhes frontais (visíveis quando virado para a frente/lado)
    if mk.depth(c, fx, fy) > -0.05:
        front_d = 0.070
        # Colete de brocado fechado no centro
        mk.obox(c, (bx + fx * front_d, by + fy * front_d, tz + 0.11), (0.0, 0.0, 1.0), 0.14, 0.08, 0.015, P["waistcoat"], up=(fx, fy, 0.0), outline=False)

        # Cravat de seda branca volumoso sob o colarinho
        cravat_pos = (bx + fx * (front_d + 0.006), by + fy * (front_d + 0.006), tz + 0.19)
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            (cravat_pos[0], cravat_pos[1], cravat_pos[2] + 0.04),
            (cravat_pos[0], cravat_pos[1], cravat_pos[2] - 0.04),
            w_start=0.038, h_start=0.018,
            w_end=0.022, h_end=0.012,
            color=P["cravat"],
            up=(fx, fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

        # Fileira dupla de botões prateados
        for b_side in (-0.035, 0.035):
            for b_z in (tz + 0.07, tz + 0.11, tz + 0.15):
                btn_pos = (bx + fx * (front_d + 0.008) + px * b_side, by + fy * (front_d + 0.008) + py * b_side, b_z)
                mk.cbox(c, btn_pos[0], btn_pos[1], btn_pos[2], 0.010, 0.010, 0.010, P["silver_button"], outline=False)

    # Dragonas militares prateadas/douradas nos ombros
    for s in (-1.0, 1.0):
        sh_pos = (bx + px * 0.115 * s, by + py * 0.115 * s, tz + 0.24)
        mk.obox(c, sh_pos, (0.0, 0.0, 1.0), 0.020, 0.070, 0.080, P["epaulet"], up=(fx, fy, 0.0), outline=True)
        # Franjas das dragonas
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
    - Feições marciais austeras projetadas via draw_portrait_face_3d (olhos azuis-aço e monóculo dourado).
    - Cabelos grisalhos platinados penteados para trás com volume aristocrático.
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

    # Desenho facial 3D com olhos marciais gélidos e monóculo dourado
    draw_portrait_face_3d(c, char_type="valerius")
    c._face_drawn = True


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
    - Rastro e chamas espectrais azuis/violetas em golpes e repouso.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    extra = c.extra_props if c.extra_props else {}
    pose = extra.get("pose")

    # Mãos com luva de oficial
    for hand in (hand_l, hand_r):
        mk.cbox(c, hand[0], hand[1], hand[2] - 0.012, 0.046, 0.046, 0.044, P["glove"], outline=True)

    # Dissipação na vitória: não desenha foice quando já dissipada
    if pose in ("finger_snap_bow", "condescending_gaze"):
        return

    if c.is_melee and c.atk_progress is not None:
        prog = c.atk_progress
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

        # 1. Haste de Ferro Forjado e Ébano
        mk.obox(c, (tail_x, tail_y, tail_z), (pole_dx, pole_dy, pole_dz), pole_len, 0.038, 0.038, P["scythe_pole"], texture="wood")
        mk.obox(c, (head_x, head_y, head_z), (pole_dx, pole_dy, pole_dz), 0.05, 0.052, 0.052, P["pole_silver"], outline=False)

        # 2. Lâmina Curva Gótica da Foice
        blade_dir_x = fx * 0.8 - px * 0.2
        blade_dir_y = fy * 0.8 - py * 0.2
        blade_dir_z = -0.35

        # Corpo da lâmina
        mk.obox(c, (head_x, head_y, head_z), (blade_dir_x, blade_dir_y, blade_dir_z), 0.58, 0.065, 0.024, P["scythe_blade"], outline=True)
        # Fio de corte prateado afiado
        mk.obox(c, (head_x + blade_dir_x * 0.04, head_y + blade_dir_y * 0.04, head_z + blade_dir_z * 0.04), (blade_dir_x, blade_dir_y, blade_dir_z), 0.55, 0.025, 0.012, P["scythe_edge"], outline=False)

        # Rastro e chamas azuis espectrais no arco do golpe
        if 0.25 <= prog <= 0.75:
            glow_x = head_x + blade_dir_x * 0.30
            glow_y = head_y + blade_dir_y * 0.30
            glow_z = head_z + blade_dir_z * 0.30
            mk.cbox(c, glow_x, glow_y, glow_z, 0.20, 0.20, 0.20, P["spectral_aura"], outline=False)
            mk.cbox(c, glow_x, glow_y, glow_z, 0.12, 0.12, 0.12, P["spectral_core"], outline=False)

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

        # Fagulhas azuis sutis na lâmina em repouso
        if math.sin(c.walk_timer * 3.5) > 0.4:
            mk.cbox(c, head_pos[0] + b_dx * 0.35, head_pos[1] + b_dy * 0.35, head_pos[2] + b_dz * 0.35, 0.06, 0.06, 0.06, P["spectral_core"], outline=False)
