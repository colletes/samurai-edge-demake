"""
Musashi, o espadachim lendário de duas lâminas (Niten Ichi-ryu):
- Rosto marcial maduro e severo Tekken 2/3, cicatriz na sobrancelha direita, barba por fazer (stubble), olhar resoluto.
- Penteado samurai tradicional (motodori/chonmage) com topknot desgrenhado preso por cordão tasuki.
- Quimono índigo desbotado com colarinho bege em V, cordão tasuki cruzado no peito e costas com nó no ombro direito.
- Mangas soltas que cobrem os ombros e bíceps, antebraços fortes com bandagens e cicatriz.
- Hakama escura pregueada contínua sem quebras ou degraus nas articulações, tabi preto e sandálias de palha (waraji).
- Duas lâminas lendárias: Katana principal na mão direita e Wakizashi na esquerda; bainhas na cintura esquerda.
- Musashi NUNCA embainha suas espadas durante combate ou vitória (sempre empunhadas em guarda alta/dois céus).
- Ordenação dinâmica de profundidade 3D (Painter's Algorithm) para oclusão perfeita das lâminas e braços quando de costas.
- Suporte a SSAA 2x offscreen buffer, materiais realistas e modo De/Para (legacy_mode).
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.voxel_rig import calc_blade_slash_3d
from src.isometric.mesh_primitives import (
    draw_ribbon_mesh_3d,
    draw_tapered_frustum_3d,
    draw_sculpted_head_3d,
    draw_portrait_face_3d,
)

PALETTE = {
    "kimono": (64, 94, 144),
    "kimono_dark": (44, 66, 106),
    "kimono_light": (92, 124, 176),
    "collar": (224, 208, 172),
    "tasuki": (198, 160, 100),
    "wrap": (216, 202, 170),
    "hakama": (78, 68, 62),
    "hakama_dark": (46, 40, 38),
    "sash": (58, 56, 118),
    "knot": (36, 32, 36),
    "skin": (216, 168, 130),
    "skin_shadow": (176, 130, 98),
    "stubble": (118, 92, 76),
    "hair": (38, 32, 32),
    "hair_light": (88, 72, 64),
    "hair_dark": (22, 18, 18),
    "eye": (34, 24, 20),
    "brow": (28, 22, 22),
    "scar": (195, 115, 102),
    "tabi": (32, 30, 36),
    "straw": (182, 150, 94),
    "rope": (122, 92, 52),
    "saya": (116, 68, 36),
    "saya_tip": (176, 140, 70),
    "saya_short": (36, 44, 70),
    "ito": (30, 26, 28),
    "tsuba": (158, 156, 168),
    "gold": (210, 176, 84),
    "steel": (214, 224, 238),
    "edge": (250, 253, 255),
    "trail": (116, 172, 255),
    "trail_core": (232, 246, 255),
}

# Materiais realistas do Overhaul (Entregável 2.2.10)
MATERIALS = {
    "kimono": "indigo_canvas",
    "kimono_dark": "indigo_canvas",
    "kimono_light": "indigo_canvas",
    "collar": "raw_linen",
    "tasuki": "braided_cord",
    "wrap": "canvas",
    "hakama": "indigo_linen",
    "hakama_dark": "indigo_linen",
    "sash": "silk",
    "saya": "urushi_lacquer",
    "saya_short": "urushi_lacquer",
    "steel": "tamahagane_hamon",
    "edge": "steel",
    "tsuba": "metal",
    "gold": "gold",
}

# Materiais legados pré-Fase 2 (para comparação De/Para no Model Inspector)
LEGACY_MATERIALS = {
    "kimono": "canvas",
    "kimono_dark": "canvas",
    "sash": "canvas",
    "saya": "lacquer",
    "steel": "chrome",
    "edge": "chrome",
}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Cinemática dos Braços e Lâminas Gêmeas (Niten Ichi-ryu)
# ---------------------------------------------------------------------------------------------------------------------

def idle_arms(c):
    """Postura Chūdan Niten: Katana à frente na direita e Wakizashi na cintura em guarda na esquerda."""
    tz = c.torso_z + math.sin(c.walk_timer * 2.8) * 0.015
    right = (c.base_x + c.fx * 0.20 - c.px * 0.08, c.base_y + c.fy * 0.20 - c.py * 0.08, tz + 0.12)
    left = (c.base_x + c.fx * 0.08 + c.px * 0.12, c.base_y + c.fy * 0.08 + c.py * 0.12, tz + 0.02)
    return left, right


def walk_arms(c):
    """Caminhada marcial: espadas sempre empunhadas em prontidão imediata (sem embainhar)."""
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    sw = math.sin(c.walk_timer * 7.5) * 0.045
    left = (bx + fx * 0.10 + px * 0.12 - fx * sw, by + fy * 0.10 + py * 0.12 - fy * sw, tz + 0.06)
    right = (bx + fx * 0.16 - px * 0.10 + fx * sw, by + fy * 0.16 - py * 0.10 + fy * sw, tz + 0.12)
    return left, right


def roll_arms(c):
    """Rolamento Marcial no Solo (Mae Ukemi): braço direito forma arco/roda pelo ombro, braço esquerdo acolhe na inércia."""
    tz = c.torso_z - 0.06
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    roll_p = (c.extra_props or {}).get("roll_prog", 0.5)
    lead_x = math.sin(roll_p * math.pi) * 0.12
    right = (bx + fx * (0.14 + lead_x) - px * 0.08, by + fy * (0.14 + lead_x) - py * 0.08, tz - 0.04 + lead_x * 0.5)
    left = (bx + fx * (0.08 - lead_x * 0.5) + px * 0.08, by + fy * (0.08 - lead_x * 0.5) + py * 0.08, tz + 0.02)
    return left, right


def cross_guard_arms(c):
    """Cross Guard Parry: Lâminas cruzadas em 'X' frontal à altura do peito/ombros."""
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.torso_z + 0.06
    left = (bx + fx * 0.15 + px * 0.10, by + fy * 0.15 + py * 0.10, z)
    right = (bx + fx * 0.15 - px * 0.10, by + fy * 0.15 - py * 0.10, z)
    return left, right


def cross_shockwave_arms(c):
    """Cross Shockwave: Braços cruzando em corte violento para frente."""
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.torso_z + 0.10
    left = (bx + fx * 0.28 - px * 0.06, by + fy * 0.28 - py * 0.06, z)
    right = (bx + fx * 0.28 + px * 0.06, by + fy * 0.28 + py * 0.06, z)
    return left, right


def intro_arms(c, p, pose):
    """Coreografia de Intro: Saque duplo fluido -> atrito em X com faíscas metálicas -> postura de duelo dos Dois Céus."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    if p < 0.35:
        u = _smooth(p / 0.35)
        # Mãos partem das bainhas na cintura esquerda e sobem sacando em arco
        left = (bx + px * (0.16 - u * 0.06) + fx * (0.02 + u * 0.12), by + py * (0.16 - u * 0.06) + fy * (0.02 + u * 0.12), tz + 0.02 + u * 0.10)
        right = (bx + px * (0.12 - u * 0.22) + fx * (0.02 + u * 0.14), by + py * (0.12 - u * 0.22) + fy * (0.02 + u * 0.14), tz + 0.06 + u * 0.08)
        return left, right
    elif p < 0.70:
        u = _smooth((p - 0.35) / 0.35)
        # Lâminas se cruzam em 'X' diante do peito e deslizam com atrito
        shake = math.sin(p * 35.0) * 0.006
        mid_l = (bx + fx * 0.16 + px * 0.08 + shake, by + fy * 0.16 + py * 0.08, tz + 0.12 + u * 0.04)
        mid_r = (bx + fx * 0.16 - px * 0.08 - shake, by + fy * 0.16 - py * 0.08, tz + 0.14 - u * 0.02)
        return mid_l, mid_r
    else:
        # Transição suave para a postura dos Dois Céus (Niten Ichi-ryu)
        u = _smooth((p - 0.70) / 0.30)
        l_idle, r_idle = idle_arms(c)
        l_clash = (bx + fx * 0.16 + px * 0.08, by + fy * 0.16 + py * 0.08, tz + 0.16)
        r_clash = (bx + fx * 0.16 - px * 0.08, by + fy * 0.16 - py * 0.08, tz + 0.12)
        return mk.lerp(l_clash, l_idle, u), mk.lerp(r_clash, r_idle, u)


def victory_arms(c, p, pose):
    """Coreografia de Vitória: Duplo Chiburi simultâneo e Postura dos Dois Céus sem embainhar."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    if pose == "double_chiburi" or p < 0.45:
        u = p / 0.45 if p < 0.45 else 1.0
        # Sacudida lateral rápida de ambas as lâminas em direção ao solo (esquerda e direita)
        snap = math.sin(u * math.pi)
        left = (bx + px * (0.14 + snap * 0.18) - fx * 0.04, by + py * (0.14 + snap * 0.18) - fy * 0.04, tz + 0.02 - snap * 0.12)
        right = (bx - px * (0.14 + snap * 0.18) - fx * 0.04, by - py * (0.14 + snap * 0.18) - fy * 0.04, tz + 0.06 - snap * 0.12)
        return left, right
    else:
        # Elevação na Postura dos Dois Céus: Katana apontada para o céu, Wakizashi na cintura
        u = min(1.0, (p - 0.45) / 0.55)
        left = (bx + fx * 0.10 + px * 0.14, by + fy * 0.10 + py * 0.14, tz + 0.02)
        right = (bx + fx * (0.12 - u * 0.04) - px * (0.08 + u * 0.04), by + fy * (0.12 - u * 0.04) - py * (0.08 + u * 0.04), tz + 0.10 + u * 0.32)
        return left, right


def finisher_arms(c, p, style):
    """Poses dos Finishers de Musashi: Finisher 1 em 3 Atos Viscerais (Katana -> Wakizashi -> Rasgo em X)."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    if style in ("DUAL_IMPALE_X_SPREAD", "FINISHER_1", "niten_impale"):
        if p < 0.35:
            u = p / 0.35
            # Ato a: Katana empala o peito do alvo; Wakizashi aguarda engatilhada na cintura
            right = (bx + fx * (0.16 + u * 0.36) - px * 0.04, by + fy * (0.16 + u * 0.36) - py * 0.04, tz + 0.14 - u * 0.02)
            left = (bx + px * 0.15 - fx * 0.02, by + py * 0.15 - fy * 0.02, tz + 0.04)
        elif p < 0.70:
            u = (p - 0.35) / 0.35
            # Ato b: Wakizashi desfere segunda estocada cruzada, cravando ambas as espadas no peito
            right = (bx + fx * 0.52 - px * 0.04, by + fy * 0.52 - py * 0.04, tz + 0.12)
            left = (bx + fx * (0.16 + u * 0.34) + px * (0.15 - u * 0.10), by + fy * (0.16 + u * 0.34) + py * (0.15 - u * 0.10), tz + 0.04 + u * 0.08)
        else:
            u = (p - 0.70) / 0.30
            # Ato c: Musashi abre os braços violentamente em 'X', rasgando o torso do oponente em 3 partes!
            right = (bx + fx * (0.52 - u * 0.22) - px * (0.04 + u * 0.42), by + fy * (0.52 - u * 0.22) - py * (0.04 + u * 0.42), tz + 0.12 + u * 0.10)
            left = (bx + fx * (0.50 - u * 0.22) + px * (0.05 + u * 0.42), by + fy * (0.50 - u * 0.22) + py * (0.05 + u * 0.42), tz + 0.12 + u * 0.10)
        return left, right
    else:
        # Finisher 2: Cross Vacuum Slicer em 4 Quadrantes
        u = min(1.0, p * 1.5)
        right = (bx + fx * (0.24 + u * 0.16) - px * (0.18 - u * 0.30), by + fy * (0.24 + u * 0.16) - py * (0.18 - u * 0.30), tz + 0.16)
        left = (bx + fx * (0.24 + u * 0.16) + px * (0.18 - u * 0.30), by + fy * (0.24 + u * 0.16) + py * (0.18 - u * 0.30), tz + 0.16)
        return left, right


def _step(c):
    return c.extra_props.get("combo_step", 1) if c.extra_props else 1


def _hands_at(c, p, step):
    """(esquerda, direita) no progresso p: corte 1 descendente Katana, corte 2 ascendente Wakizashi, corte 3 cruzado duplo."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    if step == 1:
        right = (bx + fx * (0.16 + p * 0.30) - px * 0.06, by + fy * (0.16 + p * 0.30) - py * 0.06, tz + 0.40 - p * 0.36)
        left = (bx + px * 0.15 - fx * 0.05, by + py * 0.15 - fy * 0.05, tz + 0.10)
    elif step == 2:
        left = (bx + fx * (0.16 + p * 0.28) + px * 0.06, by + fy * (0.16 + p * 0.28) + py * 0.06, tz + 0.04 + p * 0.34)
        right = (bx - px * 0.15 - fx * 0.08, by - py * 0.15 - fy * 0.08, tz + 0.20)
    else:
        cross = math.sin(p * math.pi)
        lat = 0.20 - p * 0.35
        right = (bx + fx * (0.22 + cross * 0.22) - px * lat, by + fy * (0.22 + cross * 0.22) - py * lat, tz + 0.18)
        left = (bx + fx * (0.22 + cross * 0.22) + px * lat, by + fy * (0.22 + cross * 0.22) + py * lat, tz + 0.18)
    return left, right


def get_arms(c):
    """Retorna as posições 3D articuladas dos punhos com suporte a todos os estados e LERP."""
    return _hands(c)


def attack_arms(c):
    return _hands_at(c, c.atk_progress, _step(c))


def _blade_dirs(c, p, step):
    """(direção katana, comp katana, direção wakizashi, comp wakizashi) no progresso p."""
    info = calc_blade_slash_3d("musashi", "ATTACK", p, c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py, {"combo_step": step})
    swing = tuple(info["dir"])
    guard_k = mk.norm((c.fx * 0.60 - c.px * 0.10, c.fy * 0.60 - c.py * 0.10, -0.30))
    guard_w = mk.norm((c.fx * 0.50 + c.px * 0.10, c.fy * 0.50 + c.py * 0.10, -0.20))
    if step == 1:
        return swing, info["length"], guard_w, 0.48
    if step == 2:
        return guard_k, 0.66, swing, info["length"]
    return (mk.norm((c.fx * 0.70 + c.px * 0.28, c.fy * 0.70 + c.py * 0.28, 0.12)), 0.66,
            mk.norm((c.fx * 0.70 - c.px * 0.28, c.fy * 0.70 - c.py * 0.28, 0.12)), 0.50)


def _drawn_dirs(c):
    return (mk.norm((c.fx * 0.80 - c.px * 0.25, c.fy * 0.80 - c.py * 0.25, 0.12)), 0.68,
            mk.norm((c.fx * 0.45 + c.px * 0.40, c.fy * 0.45 + c.py * 0.40, -0.28)), 0.48)


def _hands(c):
    """Posição atual das mãos com suporte a todos os estados, poses e LERP."""
    extra = getattr(c, "extra_props", None) or {}
    pose = extra.get("pose", "")
    eff_state = extra.get("intro_victory_state", getattr(c, "state", "IDLE"))
    p = extra.get("p", c.state_timer if hasattr(c, "state_timer") else 0.0)
    f_style = extra.get("finisher_style", "")

    # 1. Finalizadores Cinemáticos
    if f_style in ("DUAL_IMPALE_X_SPREAD", "CROSS_VACUUM_SLICER") or pose in ("finisher_1", "niten_impale", "finisher_2", "cross_slicer") or eff_state in ("FINISHER_1", "FINISHER_2"):
        return finisher_arms(c, p, f_style or pose or eff_state)

    # 2. Intro e Vitória
    if eff_state == "INTRO" or pose in ("dual_draw", "cross_blade_clash", "two_heavens_guard"):
        return intro_arms(c, p, pose)
    if eff_state == "VICTORY" or pose in ("double_chiburi", "two_heavens_victory"):
        return victory_arms(c, p, pose)

    # 3. Rolamento Tático
    if eff_state == "ROLL" or extra.get("is_roll", False) or pose == "tactical_roll":
        return roll_arms(c)

    # 4. Cross Shockwave
    if eff_state == "CROSS_SHOCKWAVE" or extra.get("cross_shockwave", False):
        return cross_shockwave_arms(c)

    # 5. Cross Guard Parry
    if c.state == "PARRY" or pose == "cross_guard":
        return cross_guard_arms(c)

    # 6. Combo Melee
    if c.is_melee and c.atk_progress is not None:
        return attack_arms(c)

    # 7. Caminhada (espadas sempre sacadas)
    if c.is_moving and hasattr(c, "walk_timer"):
        return walk_arms(c)

    # 8. Neutra Chūdan
    return idle_arms(c)


# ---------------------------------------------------------------------------------------------------------------------
# Bainhas e Espadas
# ---------------------------------------------------------------------------------------------------------------------

def _scabbards(c):
    """Katana (marrom, longa) e wakizashi (azul-escura, curta) na cintura esquerda."""
    k = (c.base_x + c.px * 0.15 + c.fx * 0.02, c.base_y + c.py * 0.15 + c.fy * 0.02, c.pelvis_z + 0.06)
    b1 = mk.norm((-c.fx * 0.78 + c.px * 0.40, -c.fy * 0.78 + c.py * 0.40, -0.34))
    k2 = (k[0] + c.fx * 0.025, k[1] + c.fy * 0.025, k[2] + 0.05)
    b2 = mk.norm((-c.fx * 0.60 + c.px * 0.62, -c.fy * 0.60 + c.py * 0.62, -0.26))
    return (k, b1), (k2, b2)


def _sheaths(c):
    P = pal()
    (k, b1), (k2, b2) = _scabbards(c)
    mk.obox(c, k2, b2, 0.36, 0.04, 0.04, P["saya_short"])
    mk.obox(c, mk.add(k2, b2, 0.33), b2, 0.03, 0.044, 0.044, P["gold"], outline=False)
    mk.obox(c, k, b1, 0.52, 0.046, 0.046, P["saya"])
    mk.obox(c, k, b1, 0.03, 0.054, 0.054, P["gold"], outline=False)
    mk.obox(c, mk.add(k, b1, 0.49), b1, 0.035, 0.05, 0.05, P["saya_tip"], outline=False)
    offs = cloth.chain_offsets(2, c.walk_timer, 1.3, mk.motion(c, 0.05)[0], (c.px, c.py), amp=0.02, freq=2.2)
    for i, o in enumerate(offs):
        a = mk.add(k, b1, 0.06 + 0.04 * i)
        mk.cbox(c, a[0] + o[0], a[1] + o[1], a[2] - 0.05 - 0.04 * i, 0.016, 0.016, 0.05, P["sash"], outline=False)


def _blade(c, hand, d, length, short=False):
    """Espada na mão com tsuba, habaki e lâmina de aço com fio polido."""
    P = pal()
    tsuba = mk.add(hand, d, 0.06)
    mk.obox(c, mk.add(tsuba, d, -0.16 if not short else -0.13), d, 0.16 if not short else 0.13, 0.04, 0.04, P["ito"])
    mk.obox(c, mk.add(tsuba, d, -0.172), d, 0.02, 0.046, 0.046, P["gold"], outline=False)
    mk.obox(c, mk.add(tsuba, d, -0.008), d, 0.016, 0.09 if not short else 0.07, 0.09 if not short else 0.07, P["tsuba"])
    mk.obox(c, mk.add(tsuba, d, 0.008), d, 0.03, 0.05, 0.036, P["gold"], outline=False)
    mk.obox(c, mk.add(tsuba, d, 0.03), d, length, 0.044, 0.03, P["steel"])
    mk.obox(c, mk.add(tsuba, d, 0.04), d, max(0.0, length - 0.02), 0.016, 0.034, P["edge"], outline=False)


def _render_weapons_and_hands(c, arm_l, arm_r):
    """Renderiza as lâminas empunhadas e o rastro de corte."""
    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)
    extra = getattr(c, "extra_props", None) or {}
    pose = extra.get("pose", "")
    eff_state = extra.get("intro_victory_state", getattr(c, "state", "IDLE"))
    p = extra.get("p", c.state_timer if hasattr(c, "state_timer") else 0.0)
    f_style = extra.get("finisher_style", "")

    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # 0. Finalizadores Cinemáticos
    if f_style in ("DUAL_IMPALE_X_SPREAD", "CROSS_VACUUM_SLICER") or pose in ("finisher_1", "niten_impale", "finisher_2", "cross_slicer") or eff_state in ("FINISHER_1", "FINISHER_2"):
        if f_style == "CROSS_VACUUM_SLICER" or pose in ("finisher_2", "cross_slicer"):
            _blade(c, hand_r, mk.norm((fx * 0.70 + px * 0.40, fy * 0.70 + py * 0.40, -0.30)), 0.68)
            _blade(c, hand_l, mk.norm((fx * 0.70 - px * 0.40, fy * 0.70 - py * 0.40, 0.30)), 0.52, short=True)
        else:
            # DUAL_IMPALE_X_SPREAD em 3 Atos Viscerais
            if p < 0.35:
                # Ato a: Katana empala à frente; Wakizashi na cintura aguardando
                _blade(c, hand_r, mk.norm((fx * 0.98 - px * 0.04, fy * 0.98 - py * 0.04, -0.05)), 0.68)
                _blade(c, hand_l, mk.norm((fx * 0.30 + px * 0.80, fy * 0.30 + py * 0.80, -0.35)), 0.48, short=True)
            elif p < 0.70:
                # Ato b: Wakizashi também empala cruzada no peito
                u = (p - 0.35) / 0.35
                w_dir = mk.lerp((fx * 0.30 + px * 0.80, fy * 0.30 + py * 0.80, -0.35),
                                (fx * 0.95 + px * 0.14, fy * 0.95 + py * 0.14, -0.05), u)
                _blade(c, hand_r, mk.norm((fx * 0.98 - px * 0.04, fy * 0.98 - py * 0.04, -0.05)), 0.68)
                _blade(c, hand_l, mk.norm(w_dir), 0.50, short=True)
            else:
                # Ato c: Ruptura e abertura violenta dos braços em 'X'
                u = (p - 0.70) / 0.30
                r_dir = mk.lerp((fx * 0.98 - px * 0.04, fy * 0.98 - py * 0.04, -0.05),
                                (fx * 0.25 - px * 0.92, fy * 0.25 - py * 0.92, 0.15), u)
                l_dir = mk.lerp((fx * 0.95 + px * 0.14, fy * 0.95 + py * 0.14, -0.05),
                                (fx * 0.25 + px * 0.92, fy * 0.25 + py * 0.92, 0.15), u)
                _blade(c, hand_r, mk.norm(r_dir), 0.68)
                _blade(c, hand_l, mk.norm(l_dir), 0.50, short=True)

    # 1. Cross Guard Parry
    elif eff_state == "PARRY" or pose == "cross_guard":
        _blade(c, hand_r, mk.norm((fx * 0.35 + px * 0.55, fy * 0.35 + py * 0.55, 0.70)), 0.64)
        _blade(c, hand_l, mk.norm((fx * 0.35 - px * 0.55, fy * 0.35 - py * 0.55, 0.70)), 0.48, short=True)

    # 2. Cross Shockwave
    elif eff_state == "CROSS_SHOCKWAVE" or extra.get("cross_shockwave", False):
        _blade(c, hand_r, mk.norm((fx * 0.75 + px * 0.45, fy * 0.75 + py * 0.45, -0.20)), 0.66)
        _blade(c, hand_l, mk.norm((fx * 0.75 - px * 0.45, fy * 0.75 - py * 0.45, 0.20)), 0.50, short=True)

    # 3. Rolamento Tático (Mae Ukemi)
    elif eff_state == "ROLL" or extra.get("is_roll", False) or pose == "tactical_roll":
        r_dir = mk.norm((-fx * 0.60 + px * 0.40, -fy * 0.60 + py * 0.40, -0.40))
        l_dir = mk.norm((-fx * 0.60 - px * 0.40, -fy * 0.60 - py * 0.40, -0.40))
        _blade(c, hand_r, r_dir, 0.60)
        _blade(c, hand_l, l_dir, 0.46, short=True)

    # 4. Intro (Saque fluido contínuo -> atrito em X com faíscas -> guarda Dois Céus)
    elif eff_state == "INTRO" or pose in ("dual_draw", "cross_blade_clash", "two_heavens_guard"):
        if p < 0.35:
            u = _smooth(p / 0.35)
            (k, b1), (k2, b2) = _scabbards(c)
            r_dir = mk.lerp(b1, (fx * 0.30 + px * 0.65, fy * 0.30 + py * 0.65, 0.68), u)
            l_dir = mk.lerp(b2, (fx * 0.30 - px * 0.65, fy * 0.30 - py * 0.65, 0.68), u)
            _blade(c, hand_r, mk.norm(r_dir), 0.64)
            _blade(c, hand_l, mk.norm(l_dir), 0.48, short=True)
        elif p < 0.70:
            _blade(c, hand_r, mk.norm((fx * 0.30 + px * 0.65, fy * 0.30 + py * 0.65, 0.68)), 0.64)
            _blade(c, hand_l, mk.norm((fx * 0.30 - px * 0.65, fy * 0.30 - py * 0.65, 0.68)), 0.48, short=True)
            # Faíscas metálicas no ponto de contato das lâminas
            clash_pt = ((hand_l[0] + hand_r[0]) * 0.5 + fx * 0.12, (hand_l[1] + hand_r[1]) * 0.5 + fy * 0.12, hand_r[2] + 0.18)
            sx, sy = c.camera.apply(clash_pt[0], clash_pt[1], clash_pt[2])
            pygame.draw.circle(c.surface, (255, 235, 120), (sx, sy), 3)
            pygame.draw.circle(c.surface, (255, 255, 255), (sx, sy), 1)
        else:
            u = _smooth((p - 0.70) / 0.30)
            dk, lk, dw, lw = _drawn_dirs(c)
            r_dir = mk.lerp((fx * 0.30 + px * 0.65, fy * 0.30 + py * 0.65, 0.68), dk, u)
            l_dir = mk.lerp((fx * 0.30 - px * 0.65, fy * 0.30 - py * 0.65, 0.68), dw, u)
            _blade(c, hand_r, mk.norm(r_dir), lk)
            _blade(c, hand_l, mk.norm(l_dir), lw, short=True)

    # 5. Vitória (Duplo Chiburi e Postura dos Dois Céus)
    elif eff_state == "VICTORY" or pose in ("double_chiburi", "two_heavens_victory"):
        if pose == "double_chiburi" or p < 0.45:
            _blade(c, hand_r, mk.norm((fx * 0.20 - px * 0.85, fy * 0.20 - py * 0.85, -0.45)), 0.66)
            _blade(c, hand_l, mk.norm((fx * 0.20 + px * 0.85, fy * 0.20 + py * 0.85, -0.45)), 0.50, short=True)
        else:
            # Postura dos Dois Céus: Katana apontada para o alto (~65°), Wakizashi na cintura
            _blade(c, hand_r, mk.norm((fx * 0.20 - px * 0.10, fy * 0.20 - py * 0.10, 0.95)), 0.66)
            _blade(c, hand_l, mk.norm((fx * 0.60 + px * 0.45, fy * 0.60 + py * 0.45, -0.15)), 0.50, short=True)

    # 6. Combo Melee
    elif c.is_melee:
        step, p_atk = _step(c), c.atk_progress
        dk, lk, dw, lw = _blade_dirs(c, p_atk, step)
        _blade(c, hand_r, dk, lk)
        _blade(c, hand_l, dw, lw, short=True)
        _slash_trail(c, p_atk, step)

    # 7. Neutra e Caminhada (sempre empunhadas!)
    else:
        dk, lk, dw, lw = _drawn_dirs(c)
        _blade(c, hand_r, dk, lk)
        _blade(c, hand_l, dw, lw, short=True)


def _slash_trail(c, p, step):
    P = pal()
    ghosts = []
    for j in range(6):
        pj = p - 0.07 * j
        if pj < 0.05:
            break
        left, right = _hands_at(c, pj, step)
        dk, lk, dw, lw = _blade_dirs(c, pj, step)
        hand, d, length = ((left, dw, lw) if step == 2 else (right, dk, lk))
        h = (hand[0], hand[1], hand[2] - 0.065)
        ghosts.append((mk.add(h, d, length * 0.5), mk.add(h, d, length * 1.06)))
    for j in range(len(ghosts) - 1):
        a0, a1 = ghosts[j]
        b0, b1 = ghosts[j + 1]
        fade = 1.0 - j / 6.0
        mk.band(c, (a0, a1, b1, b0), P["trail"] + (int(225 * fade),))
        mk.band(c, (mk.lerp(a0, a1, 0.5), a1, b1, mk.lerp(b0, b1, 0.5)), P["trail_core"] + (int(250 * fade),))


# ---------------------------------------------------------------------------------------------------------------------
# Topknot (Coque Samurai) e Mechas
# ---------------------------------------------------------------------------------------------------------------------

def _topknot_root(c):
    return (c.base_x - c.fx * 0.035, c.base_y - c.fy * 0.035, c.head_z + 0.175)


def _draw_topknot(c):
    """Topknot samurai esculpido em fitas 3D facetadas amarrado com cordão tasuki."""
    P = pal()
    root = _topknot_root(c)
    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.06)
    wind = cloth.wind_at(root[0], root[1])

    # Base da amarração (nó tasuki bege)
    mk.obox(c, (root[0] - fx * 0.01, root[1] - fy * 0.01, root[2] + 0.005), (0.0, 0.0, 1.0), 0.028, 0.044, 0.044, P["tasuki"], up=(fx, fy, 0.0), outline=True)

    # Haste principal do topknot arqueada para trás
    base_tip = (root[0] - fx * 0.035, root[1] - fy * 0.035, root[2] + 0.075)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        root, base_tip,
        w_start=0.055, h_start=0.055,
        w_end=0.042, h_end=0.042,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Pontas do coque desgrenhado de rōnin
    spikes = ((0.5, 0.2, 0.055), (-0.5, 0.15, 0.050), (0.1, 0.5, 0.065), (-0.2, -0.4, 0.055), (0.0, 0.0, 0.075))
    for i, (a, b, length) in enumerate(spikes):
        o = cloth.chain_offsets(1, c.walk_timer, 0.9 * i, trail, (px, py), amp=amp * 1.4, freq=freq * 1.1, wind=wind, wind_gain=0.04)[0]
        tip = (base_tip[0] + px * a * 0.045 - fx * b * 0.045 + o[0],
               base_tip[1] + py * a * 0.045 - fy * b * 0.045 + o[1],
               base_tip[2] + length + o[2])
        draw_tapered_frustum_3d(
            c.surface, c.camera,
            base_tip, tip,
            w_start=0.024, h_start=0.024,
            w_end=0.010, h_end=0.010,
            color=P["hair"] if i % 2 == 0 else P["hair_light"],
            up=(0.0, 0.0, 1.0),
            outline=False,
            alpha=c.alpha,
        )


def _side_lock_is_behind(c, side: float) -> bool:
    """Verifica se a costeleta/mecha lateral está no lado oposto à câmera."""
    lx = c.base_x + c.px * 0.08 * side
    ly = c.base_y + c.py * 0.08 * side
    return mk.depth(c, lx, ly) < mk.depth(c, c.base_x, c.base_y) - 0.01


def _draw_side_lock(c, side: float):
    """Costeleta/mecha lateral desgrenhada emoldurando a face."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    trail, amp, freq = mk.motion(c, 0.05)
    o = cloth.chain_offsets(1, c.walk_timer, 0.8 * side, trail, (px, py), amp=amp * 0.7, freq=freq)[0]
    p_top = (bx + px * 0.072 * side, by + py * 0.072 * side, hz + 0.12)
    p_bot = (bx + px * 0.076 * side + o[0], by + py * 0.076 * side + o[1], hz + 0.01 + o[2])
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        p_top, p_bot,
        w_start=0.024, h_start=0.028,
        w_end=0.012, h_end=0.014,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )


# ---------------------------------------------------------------------------------------------------------------------
# Ganchos de Renderização (Painter's Algorithm)
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Camada traseira (Painter's Algorithm):
    - Topknot samurai (se estiver do lado oposto à câmera).
    - Costeletas no lado oposto à câmera (ocultadas pelo crânio).
    - Bainhas (se estiverem do lado oposto à câmera).
    - Lâminas e manoplas (se as mãos estiverem atrás do tronco ao encarar de costas).
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)

    # Topknot atrás do crânio
    t_root = _topknot_root(c)
    if mk.depth(c, t_root[0], t_root[1]) < d_torso:
        _draw_topknot(c)

    # Costeletas no lado oculto
    for s in (-1.0, 1.0):
        if _side_lock_is_behind(c, s):
            _draw_side_lock(c, s)

    # Bainhas
    (k, b1), _ = _scabbards(c)
    mid_saya = mk.add(k, b1, 0.25)
    if mk.depth(c, mid_saya[0], mid_saya[1]) < d_torso - 0.02:
        _sheaths(c)

    # Ordenação dinâmica: se as mãos estiverem atrás do tronco, renderiza ANTES do tronco
    hand_l, hand_r = _hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)
    if mk.depth(c, w_mid[0], w_mid[1]) < d_torso:
        _render_weapons_and_hands(c, hand_l, hand_r)


def draw_legs(c):
    """Hakama larga e pregueada esculpida em fita contínua 3D com tabi preto e sandálias waraji."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.05)
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]
        sign = 1.0 if side == "L" else -1.0
        o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.9 * sign, trail, (c.px, c.py), amp=amp * 0.7, freq=freq, wind=cloth.wind_at(ft[0], ft[1]))

        # Sandália de palha waraji e sola
        mk.obox(c, (ft[0] - c.fx * 0.05, ft[1] - c.fy * 0.05, ft[2]), (c.fx, c.fy, 0.0), 0.15, 0.085, 0.028, P["straw"])
        mk.obox(c, (ft[0] - c.fx * 0.025, ft[1] - c.fy * 0.025, ft[2] + 0.028), (c.fx, c.fy, 0.0), 0.11, 0.070, 0.034, P["tabi"])
        mk.obox(c, (ft[0] + c.fx * 0.010, ft[1] + c.fy * 0.010, ft[2] + 0.030), (c.fx, c.fy, 0.0), 0.02, 0.074, 0.036, P["rope"], outline=False)

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0] + o1[0] * 0.6, sh[1] + o1[1] * 0.6, sh[2] + 0.16)
        hem = (sh[0] + o2[0] * 0.6, sh[1] + o2[1] * 0.6, sh[2] + 0.018)

        # Hakama contínua em malha 3D sem degraus
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, hem],
            widths=[0.145, 0.165, 0.185],
            depth_thick=0.130,
            colors=[P["hakama"], P["hakama_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )


def draw_obi(c):
    """Faixa azul-arroxeada com o nó escuro na frente e placa lombar nas costas."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07
    d_torso = mk.depth(c, bx, by)

    # Koshi-ita (placa lombar da hakama nas costas)
    d_back = mk.depth(c, bx - fx * 0.11, by - fy * 0.11)
    if d_back >= d_torso - 0.04:
        mk.cbox(c, bx - fx * 0.11, by - fy * 0.11, c.pelvis_z + 0.03, 0.12, 0.07, 0.16, P["hakama_dark"])

    # Nó e faixa frontal
    kx, ky = bx + fx * 0.115, by + fy * 0.115
    d_front = mk.depth(c, kx, ky)
    if d_front >= d_torso - 0.04:
        mk.cbox(c, kx, ky, z + 0.005, 0.07, 0.045, 0.07, P["knot"])
        trail, amp, freq = mk.motion(c, 0.05)
        offs = cloth.chain_offsets(3, c.walk_timer, 0.7, trail, (px, py), amp=amp * 1.3, freq=freq, wind=cloth.wind_at(kx, ky))
        for i, o in enumerate(offs):
            mk.cbox(c, kx - px * 0.02 + o[0], ky + o[1], z - 0.012 - 0.07 * (i + 1) + o[2], 0.034, 0.024, 0.075, P["sash"])


def draw_torso(c):
    """
    Tronco de Musashi:
    - Quimono índigo desbotado com colarinho em V de linho cru.
    - Tasuki bege cruzando peito e costas com laço e pontas esvoaçantes no ombro direito.
    """
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    chest_d = 0.22
    front = chest_d * 0.50 + 0.006
    back = -(chest_d * 0.50 + 0.006)

    # Detalhes frontais (colarinho e tasuki frontal) desenhados apenas se o peito estiver voltado para a câmera
    if mk.depth(c, fx, fy) > -0.05:
        # Colarinho bege em V
        apex = (bx + fx * front, by + fy * front, tz + 0.09)
        for s in (-1.0, 1.0):
            top = (bx + fx * (front - 0.003) + px * 0.062 * s, by + fy * (front - 0.003) + py * 0.062 * s, tz + 0.255)
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                top, apex,
                w_start=0.026, h_start=0.014,
                w_end=0.018, h_end=0.010,
                color=P["collar"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )

        # Pele exposta no decote central
        mk.obox(c, (bx + fx * (front - 0.006), by + fy * (front - 0.006), tz + 0.135),
                (0.0, 0.0, 1.0), 0.095, 0.048, 0.016, P["skin"], up=(fx, fy, 0.0), outline=False)

        # Tiras tasuki cruzadas no peito
        p_top_l = (bx + fx * front - px * 0.09, by + fy * front - py * 0.09, tz + 0.25)
        p_bot_r = (bx + fx * front + px * 0.11, by + fy * front + py * 0.11, tz + 0.03)
        mk.limb(c, p_top_l, p_bot_r, 0.022, P["tasuki"], outline=False, height=0.012)

        p_top_r = (bx + fx * front + px * 0.09, by + fy * front + py * 0.09, tz + 0.25)
        p_bot_l = (bx + fx * front - px * 0.11, by + fy * front - py * 0.11, tz + 0.03)
        mk.limb(c, p_top_r, p_bot_l, 0.022, P["tasuki"], outline=False, height=0.012)

        # Laço do tasuki no ombro direito
        bow = (bx + fx * (front - 0.01) - px * 0.095, by + fy * (front - 0.01) - py * 0.095, tz + 0.245)
        mk.obox(c, bow, (fx, fy, 0.0), 0.035, 0.035, 0.025, P["tasuki"], outline=True)
        trail, amp, freq = mk.motion(c, 0.06)
        for k, s in enumerate((-1.0, 1.0)):
            offs = cloth.chain_offsets(2, c.walk_timer, 0.9 * k, trail, (px, py), amp=amp * 1.3, freq=freq, wind=cloth.wind_at(bow[0], bow[1]))
            p_tie0 = (bow[0] + px * 0.018 * s, bow[1] + py * 0.018 * s, bow[2] - 0.015)
            p_tie1 = (p_tie0[0] + offs[1][0], p_tie0[1] + offs[1][1], p_tie0[2] - 0.085 + offs[1][2])
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                p_tie0, p_tie1,
                w_start=0.018, h_start=0.012,
                w_end=0.010, h_end=0.008,
                color=P["tasuki"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )

    # Detalhes dorsais (tasuki cruzado em X nas costas) se o dorso estiver voltado para a câmera
    if mk.depth(c, -fx, -fy) > -0.05:
        p_back_tl = (bx + fx * back - px * 0.09, by + fy * back - py * 0.09, tz + 0.25)
        p_back_br = (bx + fx * back + px * 0.10, by + fy * back + py * 0.10, tz + 0.04)
        mk.limb(c, p_back_tl, p_back_br, 0.022, P["tasuki"], outline=False, height=0.012)

        p_back_tr = (bx + fx * back + px * 0.09, by + fy * back + py * 0.09, tz + 0.25)
        p_back_bl = (bx + fx * back - px * 0.10, by + fy * back - py * 0.10, tz + 0.04)
        mk.limb(c, p_back_tr, p_back_bl, 0.022, P["tasuki"], outline=False, height=0.012)


def draw_arm(c, shoulder, hand, side):
    """Braço forte e calejado: bandagem nos pulsos, cicatriz no antebraço e mãos calejadas."""
    P = pal()
    s = (shoulder[0], shoulder[1], c.torso_z + 0.21)
    h = (hand[0], hand[1], hand[2] - 0.065)
    out = (c.px * side, c.py * side, 0.0)
    e = mk.add(mk.add(mk.lerp(s, h, 0.5), out, 0.035), (0.0, 0.0, -0.035))

    # Bíceps e antebraço afunilados
    mk.limb(c, s, e, 0.068, P["skin"], w_end=0.062)
    mk.limb(c, e, h, 0.060, P["skin"], w_end=0.054)

    # Cicatriz no antebraço direito
    if side < 0:
        mk.limb(c, mk.lerp(e, h, 0.3), mk.lerp(e, h, 0.52), 0.020, P["scar"], outline=False, height=0.075)

    # Bandagem protetora de combate nos punhos
    mk.limb(c, mk.lerp(e, h, 0.66), mk.lerp(e, h, 0.96), 0.066, P["wrap"], w_end=0.062)
    # Mão
    mk.cbox(c, h[0], h[1], h[2] - 0.03, 0.060, 0.060, 0.058, P["skin"])
    return s, e


def draw_sleeves(c, arms):
    """Mangas do quimono cobrindo os ombros e bíceps até o cotovelo, com caimento vertical natural."""
    P = pal()
    for k, (s, e, side) in enumerate(arms):
        anchor = (s[0] + c.px * side * 0.012, s[1] + c.py * side * 0.012, s[2] + 0.015)
        mid = mk.add(mk.lerp(s, e, 0.40), (c.px * side * 0.015, c.py * side * 0.015, -0.015))
        hem = mk.add(mk.lerp(s, e, 0.75), (c.px * side * 0.018, c.py * side * 0.018, -0.030))

        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[anchor, mid, hem],
            widths=[0.088, 0.096, 0.092],
            depth_thick=0.082,
            colors=[P["kimono"], P["kimono_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )


def draw_head(c):
    """
    Cabeça de Miyamoto Musashi (Entregável 2.2.8):
    - Crânio esculpido em 3D anatômico com mandíbula angular masculina.
    - Feições marciais Tekken 2/3 (olhos focados de guerreiro, nariz proeminente, barba por fazer).
    - Cicatriz marcante na sobrancelha direita.
    - Franja desalinhada de rōnin estritamente contornada ACIMA da linha das sobrancelhas (z >= hz + 0.108).
    - Costeletas emoldurando a face no lado visível da câmera.
    - Topknot samurai amarrado (se visível no ângulo da câmera).
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    extra = getattr(c, "extra_props", None) or {}
    legacy_mode = extra.get("legacy_mode", False)

    # Costeletas no lado voltado para a câmera
    for s in (-1.0, 1.0):
        if not _side_lock_is_behind(c, s):
            _draw_side_lock(c, s)

    # Franja rōnin na testa (estritamente acima das sobrancelhas para manter os olhos marciais limpos)
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.005
        # 3 mechas angulares esculpidas acima da linha dos olhos (z >= hz + 0.108)
        for s, dz in ((-1.0, 0.0), (0.0, 0.008), (1.0, 0.002)):
            p0 = (bx + fx * front_d + px * 0.035 * s, by + fy * front_d + py * 0.035 * s, hz + 0.138)
            p1 = (bx + fx * (front_d + 0.003) + px * 0.048 * s, by + fy * (front_d + 0.003) + py * 0.048 * s, hz + 0.110 + dz)
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                p0, p1,
                w_start=0.024, h_start=0.016,
                w_end=0.014, h_end=0.010,
                color=P["hair"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )

        # Cicatriz na sobrancelha direita do veterano Musashi (Fase 2 Overhaul)
        if not legacy_mode:
            p_scar_0 = (bx + fx * (front_d + 0.006) - px * 0.042, by + fy * (front_d + 0.006) - py * 0.042, hz + 0.116)
            p_scar_1 = (bx + fx * (front_d + 0.006) - px * 0.030, by + fy * (front_d + 0.006) - py * 0.030, hz + 0.092)
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                p_scar_0, p_scar_1,
                w_start=0.008, h_start=0.006,
                w_end=0.006, h_end=0.004,
                color=P["scar"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )

    # Topknot (se estiver no lado voltado para a câmera)
    t_root = _topknot_root(c)
    if mk.depth(c, t_root[0], t_root[1]) >= mk.depth(c, bx, by):
        _draw_topknot(c)


def draw_front(c, arm_l, arm_r):
    """
    Camada frontal (Painter's Algorithm):
    - Bainhas (se do lado visível da câmera).
    - Lâminas e manoplas são renderizadas aqui APENAS se as mãos estiverem à frente do tronco.
    """
    d_torso = mk.depth(c, c.base_x, c.base_y)

    (k, b1), _ = _scabbards(c)
    mid_saya = mk.add(k, b1, 0.25)
    if mk.depth(c, mid_saya[0], mid_saya[1]) >= d_torso - 0.02:
        _sheaths(c)

    hand_l, hand_r = _hands(c)
    w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)

    if mk.depth(c, w_mid[0], w_mid[1]) >= d_torso:
        _render_weapons_and_hands(c, hand_l, hand_r)
