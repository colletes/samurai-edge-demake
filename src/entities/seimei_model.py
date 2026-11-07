"""
Seimei, a Onmyoji dos Talismãs (Ciclo 4 - Overhaul 2.20):
- Mestra espiritual dos kami e do yin-yang (Onmyōdō) da era Bakumatsu, herdeira da linhagem nobre de Heian-kyo.
- Vestes nobres cerimoniais Kariginu / Suikan da corte Heian em seda branca pura com bordas em índigo celestial e debrum dourado.
- Mangas amplas esvoaçantes em fita contínua 3D com caimento vertical autêntico (normal_vec frontal).
- Chapéu cerimonial Tate-Eboshi alto preto laqueado com dobra de vinco e cordão de seda púrpura.
- Cabelos negros lustrosos longos descendo pelas costas com mechas laterais (tsuya-kami) e franja reta Hime-cut.
- Olhos anime luminosos em ametista celestial com brilho duplo, cílios alados e nariz esculpido delicado.
- Talismãs Ofuda sagrados incandescentes com caligrafia kanji espiritual que muda de cor conforme o Rondel Elemental Onmyōdō.
- Leque cerimonial Sensu articulado e espíritos Shikigami de origami em revoada celestial.
- Exposição mandatória de get_arms(c) e materiais realistas com suporte a SSAA 2x e modo comparativo De / Para.
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
    draw_voxel_box,
    draw_oriented_voxel_box,
)

SKIN = (254, 242, 238)
SKIN_SHADOW = (225, 202, 195)

PALETTE = {
    # Vestes Kariginu da Corte Heian / Seda Branca e Índigo Celestial
    "robe_white": (252, 252, 255),
    "robe_dark": (218, 222, 235),
    "torso": (252, 252, 255),
    "indigo": (40, 52, 130),
    "indigo_dark": (24, 32, 85),
    "indigo_light": (65, 82, 175),
    "gold_thread": (235, 195, 65),  # Brasão e bordados imperiais
    "purple_cord": (130, 55, 160),  # Cordão de seda púrpura (Agemaki)

    # Chapéu Cerimonial Eboshi (Laca negra com reflexos púrpura-seda Heian)
    "eboshi": (44, 40, 52),
    "eboshi_dark": (26, 24, 32),
    "eboshi_light": (66, 60, 78),
    "eboshi_crease": (52, 46, 62),
    "eboshi_gold": (215, 180, 60),

    # Cabelos Longos Negros e Rosto
    "hair": (22, 20, 28),
    "hair_dark": (14, 12, 18),
    "hair_light": (45, 40, 55),
    "skin": SKIN,
    "skin_shadow": SKIN_SHADOW,
    "eye": (135, 115, 215),
    "brow": (32, 24, 38),
    "lip": (225, 110, 128),

    # Hakama / Calças Sashinuki Heian e Calçados
    "hakama": (42, 54, 135),
    "hakama_dark": (26, 34, 88),
    "obi": (130, 55, 160),
    "tabi": (250, 248, 252),
    "zori": (145, 115, 80),
    "zori_strap": (185, 36, 45),

    # Talismãs Ofuda, Leque Sensu e Cores Elementais
    "ofuda_paper": (255, 252, 245),
    "ofuda_gold": (255, 215, 80),
    "ofuda_kanji": (215, 42, 35),
    "sensu_paper": (250, 246, 238),
    "sensu_wood": (48, 42, 56),
    "spiritual_aura": (170, 140, 255),
    "spiritual_core": (245, 235, 255),

    # Cores dos 6 Elementos do Rondel
    "elem_wood": (45, 215, 120),
    "elem_fire": (255, 75, 45),
    "elem_earth": (235, 185, 65),
    "elem_metal": (245, 248, 255),
    "elem_water": (65, 175, 255),
    "elem_yinyang": (225, 160, 255),
}

MATERIALS = {
    "robe_white": "silk",
    "robe_dark": "silk",
    "indigo": "silk",
    "indigo_dark": "silk",
    "hakama": "silk",
    "eboshi": "lacquer",
    "gold_thread": "gold",
    "purple_cord": "silk",
    "tabi": "silk",
    "sensu_wood": "lacquer",
    "ofuda_paper": "paper",
}

LEGACY_MATERIALS = {k: "matte" for k in MATERIALS}


def pal() -> dict:
    return PALETTE


# ---------------------------------------------------------------------------------------------------------------------
# Poses dos Braços e Animação Ritual dos Talismãs
# ---------------------------------------------------------------------------------------------------------------------

def _coords(c):
    bx = getattr(c, "base_x", getattr(c, "wx", 0.0))
    by = getattr(c, "base_y", getattr(c, "wy", 0.0))
    tz = getattr(c, "torso_z", getattr(c, "wz", 0.0) + 0.35)
    fx = getattr(c, "fx", getattr(c, "facing_x", 1.0))
    fy = getattr(c, "fy", getattr(c, "facing_y", 0.0))
    px = getattr(c, "px", -fy)
    py = getattr(c, "py", fx)
    return bx, by, tz, fx, fy, px, py


def idle_arms(c):
    """
    Postura Onmyoji graciosa:
    - Mão direita sustentando um talismã Ofuda sagrado erguido no nível do peito/olhos.
    - Mão esquerda segurando o leque Sensu fechado junto à manga larga.
    """
    walk_t = getattr(c, "walk_timer", 0.0)
    breathe = math.sin(walk_t * 2.2) * 0.008
    bx, by, tz, fx, fy, px, py = _coords(c)
    tz = tz + breathe

    right = (
        bx + fx * 0.16 + px * 0.06,
        by + fy * 0.16 + py * 0.06,
        tz + 0.16
    )
    left = (
        bx + fx * 0.10 - px * 0.10,
        by + fy * 0.10 - py * 0.10,
        tz + 0.06
    )
    return left, right


def walk_arms(c):
    """Passo suave e flutuante de sacerdotisa com mangas esvoaçantes."""
    walk_t = getattr(c, "walk_timer", 0.0)
    drift = math.sin(walk_t * 7.0) * 0.05
    bx, by, tz, fx, fy, px, py = _coords(c)

    right = (
        bx + fx * (0.16 + drift * 0.03) + px * 0.06,
        by + fy * (0.16 + drift * 0.03) + py * 0.06,
        tz + 0.16 + abs(drift) * 0.015
    )
    left = (
        bx + fx * (0.10 - drift * 0.04) - px * 0.10,
        by + fy * (0.10 - drift * 0.04) - py * 0.10,
        tz + 0.06
    )
    return left, right


def attack_arms(c):
    """
    Lançamento de Talismã Ofuda (Ofuda Slash / Seal Stasis):
    - Gesto ritual gracioso: o braço direito arremessa o talismã para a frente em linha reta com rastro místico.
    """
    bx, by, tz, fx, fy, px, py = _coords(c)
    atk_p = getattr(c, "atk_progress", None)
    prog = atk_p if atk_p is not None else 0.0

    if prog < 0.30:
        # Puxa o talismã junto ao peito carregando energia
        t = prog / 0.30
        right = (bx + fx * 0.08 + px * 0.04, by + fy * 0.08 + py * 0.04, tz + 0.20 + t * 0.04)
        left = (bx - fx * 0.04 - px * 0.12, by - fy * 0.04 - py * 0.12, tz + 0.10)
    elif prog < 0.70:
        # Projeção instantânea do selo para a frente
        t = (prog - 0.30) / 0.40
        right = (bx + fx * (0.24 + t * 0.18), by + fy * (0.24 + t * 0.18), tz + 0.18)
        left = (bx - fx * 0.06 - px * 0.14, by - fy * 0.06 - py * 0.14, tz + 0.12)
    else:
        # Retorno gracioso com movimento de manga
        t = (prog - 0.70) / 0.30
        right = (bx + fx * 0.18 + px * 0.06, by + fy * 0.18 + py * 0.06, tz + 0.16)
        left = (bx + fx * 0.08 - px * 0.10, by + fy * 0.08 - py * 0.10, tz + 0.08)

    return left, right


def _current_hands(c):
    """Mapeamento contínuo de braços e gestos rituais Onmyōdō."""
    extra = getattr(c, "extra_props", None) or getattr(c, "extra", None) or {}
    pose = extra.get("pose", "")
    p = extra.get("p", 0.0)
    bx, by, tz, fx, fy, px, py = _coords(c)

    # 1. Poses de Intro (100% Contínuas C0/C1)
    if pose == "shikigami_descent":
        # Descida e levitação suave com braços abertos flutuando
        u = extra.get("seg_u", p / 0.35 if p <= 0.35 else 1.0)
        float_w = math.sin(u * math.pi) * 0.04
        r_start = (bx + px * 0.20 - fx * 0.02, by + py * 0.20 - fy * 0.02, tz + 0.22)
        r_end   = (bx + fx * 0.08 + px * 0.12, by + fy * 0.08 + py * 0.12, tz + 0.16)
        l_start = (bx - px * 0.20 - fx * 0.02, by - py * 0.20 - fy * 0.02, tz + 0.22)
        l_end   = (bx + fx * 0.06 - px * 0.12, by + fy * 0.06 - py * 0.12, tz + 0.08)

        right = (
            (1.0 - u) * r_start[0] + u * r_end[0],
            (1.0 - u) * r_start[1] + u * r_end[1],
            (1.0 - u) * r_start[2] + u * r_end[2] + float_w
        )
        left = (
            (1.0 - u) * l_start[0] + u * l_end[0],
            (1.0 - u) * l_start[1] + u * l_end[1],
            (1.0 - u) * l_start[2] + u * l_end[2] + float_w
        )
        return left, right

    elif pose == "sensu_fan_flick":
        # Abre o leque Sensu em arco gracioso e projeta o talismã para a guarda
        u = extra.get("seg_u", (p - 0.35) / 0.35 if 0.35 <= p <= 0.70 else 0.5)
        flick_arc = math.sin(u * math.pi) * 0.04
        r_start = (bx + fx * 0.08 + px * 0.12, by + fy * 0.08 + py * 0.12, tz + 0.16)
        r_end   = (bx + fx * 0.18 + px * 0.05, by + fy * 0.18 + py * 0.05, tz + 0.16)
        l_start = (bx + fx * 0.06 - px * 0.12, by + fy * 0.06 - py * 0.12, tz + 0.08)
        l_end   = (bx + fx * 0.08 - px * 0.10, by + fy * 0.08 - py * 0.10, tz + 0.06)

        right = (
            (1.0 - u) * r_start[0] + u * r_end[0],
            (1.0 - u) * r_start[1] + u * r_end[1],
            (1.0 - u) * r_start[2] + u * r_end[2] + flick_arc
        )
        left = (
            (1.0 - u) * l_start[0] + u * l_end[0],
            (1.0 - u) * l_start[1] + u * l_end[1],
            (1.0 - u) * l_start[2] + u * l_end[2] + flick_arc * 0.5
        )
        return left, right

    elif pose == "onmyoji_ready":
        # Guarda cerimonial pronta com respiração rítmica, flutuação e ondulação contínua do talismã
        u = extra.get("seg_u", (p - 0.70) / 0.30 if p >= 0.70 else 1.0)
        breath = math.sin(u * math.pi * 3.0) * 0.012
        flutter = math.sin(u * math.pi * 5.0) * 0.008
        hover = math.sin(u * math.pi * 2.0) * 0.015
        right = (
            bx + fx * (0.16 + 0.04 * math.sin(u * math.pi * 1.5)) + px * 0.05,
            by + fy * (0.16 + 0.04 * math.sin(u * math.pi * 1.5)) + py * 0.05,
            tz + 0.16 + breath + hover + flutter
        )
        left = (
            bx + fx * 0.08 - px * (0.10 + 0.02 * math.cos(u * math.pi * 2.0)),
            by + fy * 0.08 - py * (0.10 + 0.02 * math.cos(u * math.pi * 2.0)),
            tz + 0.06 - breath + hover * 0.5
        )
        return left, right

    # 2. Poses de Vitória
    elif pose == "sensu_twirl":
        # Giro gracioso do leque Sensu
        u = extra.get("seg_u", p / 0.38 if p <= 0.38 else 1.0)
        twirl_ang = u * math.pi * 2.0
        r_start = (bx + fx * 0.18 + px * 0.05, by + fy * 0.18 + py * 0.05, tz + 0.16)
        r_end   = (bx + fx * 0.12 + px * 0.06, by + fy * 0.12 + py * 0.06, tz + 0.16)
        right = (
            (1.0 - u) * r_start[0] + u * r_end[0],
            (1.0 - u) * r_start[1] + u * r_end[1],
            (1.0 - u) * r_start[2] + u * r_end[2]
        )
        left = (
            bx + fx * 0.10 - px * (0.08 + math.cos(twirl_ang) * 0.06),
            by + fy * 0.10 - py * (0.08 + math.cos(twirl_ang) * 0.06),
            tz + 0.10 + math.sin(twirl_ang) * 0.06
        )
        return left, right

    elif pose == "birds_ascend":
        # Braços elevam-se convocando pássaros de origami
        u = extra.get("seg_u", (p - 0.38) / 0.34 if 0.38 <= p <= 0.72 else 0.5)
        r_start = (bx + fx * 0.12 + px * 0.06, by + fy * 0.12 + py * 0.06, tz + 0.16)
        r_end   = (bx + fx * 0.12 + px * 0.16, by + fy * 0.12 + py * 0.16, tz + 0.30)
        l_start = (bx + fx * 0.12 - px * 0.06, by + fy * 0.12 - py * 0.06, tz + 0.16)
        l_end   = (bx + fx * 0.12 - px * 0.16, by + fy * 0.12 - py * 0.16, tz + 0.30)

        right = (
            (1.0 - u) * r_start[0] + u * r_end[0],
            (1.0 - u) * r_start[1] + u * r_end[1],
            (1.0 - u) * r_start[2] + u * r_end[2]
        )
        left = (
            (1.0 - u) * l_start[0] + u * l_end[0],
            (1.0 - u) * l_start[1] + u * l_end[1],
            (1.0 - u) * l_start[2] + u * l_end[2]
        )
        return left, right

    elif pose in ("imperial_bow", "heian_bow"):
        # Reverência imperial da corte Heian com mãos cruzadas no regaço
        u = extra.get("seg_u", (p - 0.72) / 0.28 if p >= 0.72 else 1.0)
        bow_depth = math.sin(min(1.0, u * 1.5) * math.pi * 0.5) * 0.03
        breath = math.sin(u * math.pi * 3.0) * 0.005
        right = (bx + fx * 0.10 + px * 0.02, by + fy * 0.10 + py * 0.02, tz + 0.04 - bow_depth + breath)
        left = (bx + fx * 0.10 - px * 0.02, by + fy * 0.10 - py * 0.02, tz + 0.04 - bow_depth + breath)
        return left, right

    # 3. Poses de Ação e Combate
    elif pose in ("sacred_ward", "plant_ward"):
        # Ambas as mãos projetadas para o solo conjurando o selo Kekkai
        right = (bx + fx * 0.22 + px * 0.06, by + fy * 0.22 + py * 0.06, tz + 0.04)
        left = (bx + fx * 0.22 - px * 0.06, by + fy * 0.22 - py * 0.06, tz + 0.04)
        return left, right

    elif pose == "shikigami_glide":
        # Deslize evasivo com asas de papel
        right = (bx - fx * 0.15 + px * 0.18, by - fy * 0.15 + py * 0.18, tz + 0.18)
        left = (bx - fx * 0.15 - px * 0.18, by - fy * 0.15 - py * 0.18, tz + 0.18)
        return left, right

    elif pose in ("astral_guard", "parry", "onmyo_guard"):
        # Guarda protetora com mangas elevadas e leque Sensu aberto em escudo
        right = (bx + fx * 0.14 + px * 0.04, by + fy * 0.14 + py * 0.04, tz + 0.22)
        left = (bx + fx * 0.10 - px * 0.08, by + fy * 0.10 - py * 0.08, tz + 0.18)
        return left, right

    elif pose == "parry_reaction":
        # Repulsa astral rápida
        right = (bx + fx * 0.25 + px * 0.10, by + fy * 0.25 + py * 0.10, tz + 0.20)
        left = (bx + fx * 0.20 - px * 0.12, by + fy * 0.20 - py * 0.12, tz + 0.16)
        return left, right

    # 4. Poses das Fatalidades Elementais
    elif pose.startswith("finisher_"):
        elem = pose.split("_")[1] if "_" in pose else "fire"
        if elem == "fire":
            # Gesto apontando para a vítima convocando chamas azuis/verdes
            right = (bx + fx * 0.32, by + fy * 0.32, tz + 0.20)
            left = (bx + fx * 0.08 - px * 0.12, by + fy * 0.08 - py * 0.12, tz + 0.10)
        elif elem == "water":
            # Ambas as mãos subindo em voluta aquática
            right = (bx + fx * 0.16 + px * 0.12, by + fy * 0.16 + py * 0.12, tz + 0.24)
            left = (bx + fx * 0.16 - px * 0.12, by + fy * 0.16 - py * 0.12, tz + 0.24)
        elif elem == "wood":
            # Mudra vegetal com palma erguida
            right = (bx + fx * 0.20 + px * 0.04, by + fy * 0.20 + py * 0.04, tz + 0.28)
            left = (bx - px * 0.10, by - py * 0.10, tz + 0.08)
        elif elem == "metal":
            # Dois dedos apontados para baixo convocando as lâminas celestes
            right = (bx + fx * 0.26 + px * 0.05, by + fy * 0.26 + py * 0.05, tz + 0.05)
            left = (bx + fx * 0.10 - px * 0.12, by + fy * 0.10 - py * 0.12, tz + 0.18)
        elif elem == "earth":
            # Palmas voltadas para o chão ordenando a rocha
            right = (bx + fx * 0.20 + px * 0.10, by + fy * 0.20 + py * 0.10, tz + 0.02)
            left = (bx + fx * 0.20 - px * 0.10, by + fy * 0.20 - py * 0.10, tz + 0.02)
        else:  # yinyang
            # Ambas as mãos unidas no centro em mudra Taijitu
            right = (bx + fx * 0.14 + px * 0.02, by + fy * 0.14 + py * 0.02, tz + 0.16)
            left = (bx + fx * 0.14 - px * 0.02, by + fy * 0.14 - py * 0.02, tz + 0.16)
        return left, right

    # Fallbacks padrão
    is_melee = getattr(c, "is_melee", False)
    atk_p = getattr(c, "atk_progress", None)
    if is_melee and atk_p is not None:
        return attack_arms(c)
    if getattr(c, "is_moving", False):
        return walk_arms(c)
    return idle_arms(c)


def get_arms(c):
    """Exportação mandatória para compatibilidade com o pipeline modular humanoid."""
    return _current_hands(c)


# ---------------------------------------------------------------------------------------------------------------------
# Hooks do Modelo Voxel 3D (Chamados por voxel_models.py)
# ---------------------------------------------------------------------------------------------------------------------

def draw_behind(c):
    """
    Renderiza os elementos nas costas:
    - Longos cabelos negros lustrosos descendo em cascata fluida 3D pelas costas.
    - Caimento traseiro do manto Kariginu branco e laço Agemaki púrpura.
    - Mechas laterais que caem para trás da cabeça quando em ângulo de perfil.
    """
    P = pal()
    bx, by, tz, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.torso_z, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # 1. Cabelos Negros Longos em fita 3D contínua pelas costas
    trail, amp, freq = mk.motion(c, 0.04)
    o1, o2 = cloth.chain_offsets(2, c.walk_timer, 0.6, trail, (-fx, -fy), amp=amp * 0.6, freq=freq)
    h0 = (bx - fx * 0.06, by - fy * 0.06, hz + 0.12)
    h1 = (bx - fx * 0.10 + o1[0], by - fy * 0.10 + o1[1], tz + 0.14 + o1[2])
    h2 = (bx - fx * 0.12 + o2[0], by - fy * 0.12 + o2[1], tz - 0.02 + o2[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[h0, h1, h2],
        widths=[0.115, 0.125, 0.130],
        depth_thick=0.035,
        colors=[P["hair"], P["hair_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # 2. Laço Cerimonial Agemaki Púrpura nas Costas
    mk.obox(c, (bx - fx * 0.08, by - fy * 0.08, tz + 0.16), (0.0, 0.0, 1.0), 0.055, 0.045, 0.025, P["purple_cord"], up=(fx, fy, 0.0), outline=False)

    # 3. Manto Kariginu Traseiro em seda branca pura
    p0 = (bx - fx * 0.08, by - fy * 0.08, tz + 0.14)
    p1 = (bx - fx * 0.10 + o1[0] * 0.5, by - fy * 0.10 + o1[1] * 0.5, tz - 0.04 + o1[2] * 0.5)
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[p0, p1],
        widths=[0.20, 0.22],
        depth_thick=0.030,
        colors=[P["robe_white"], P["robe_dark"]],
        side_vec=(px, py, 0.0),
        normal_vec=(-fx, -fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # 4. Mechas laterais e cordões do lado OPOSTO à câmera
    for s in (-1.0, 1.0):
        is_behind = mk.depth(c, px * s, py * s) < -0.01
        if is_behind:
            p_top = (bx + px * (hw * 0.48 * s) + fx * 0.010, by + py * (hw * 0.48 * s) + fy * 0.010, hz + 0.150)
            p_mid = (bx + px * (hw * 0.46 * s) + fx * 0.012, by + py * (hw * 0.46 * s) + fy * 0.012, hz + 0.100)
            p_bot = (bx + px * (hw * 0.44 * s) + fx * 0.014, by + py * (hw * 0.44 * s) + fy * 0.014, hz + 0.050)
            draw_ribbon_mesh_3d(
                c.surface, c.camera,
                spine_points=[p_top, p_mid, p_bot],
                widths=[0.022, 0.026, 0.026],
                depth_thick=0.012,
                colors=[P["hair"], P["hair_dark"]],
                side_vec=(px * s, py * s, 0.0),
                normal_vec=(fx, fy, 0.0),
                outline=False,
                alpha=c.alpha,
            )
            c_ear_back = (bx + px * (hw * 0.44 * s) - fx * 0.020, by + py * (hw * 0.44 * s) - fy * 0.020, hz + 0.075)
            c_neck_back = (bx + px * (hw * 0.25 * s) - fx * 0.030, by + py * (hw * 0.25 * s) - fy * 0.030, tz + 0.20)
            mk.limb(c, c_ear_back, c_neck_back, 0.006, P["purple_cord"], outline=False)


def draw_legs(c):
    """
    Hakama Sashinuki volumoso índigo da nobreza Heian em malha contínua 3D,
    com meias tabi brancas e sandálias zori delicadas.
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
        hem = (sh[0] + o1[0] * 0.1, sh[1] + o1[1] * 0.1, sh[2] + 0.05)
        ankle = (foot[0] + o2[0] * 0.15, foot[1] + o2[1] * 0.15, foot[2] + 0.03)

        # Hakama Sashinuki amplo índigo
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, hem],
            widths=[0.125, 0.135, 0.125],
            depth_thick=0.100,
            colors=[P["hakama"], P["hakama_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Meia Tabi de seda branca pura
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[hem, ankle],
            widths=[0.065, 0.054],
            depth_thick=0.054,
            colors=[P["tabi"], P["tabi"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )

        # Sandália Zori de palha clara com tiras vermelhas
        flen, fwidth = 0.11, 0.058
        mk.obox(c, (foot[0] + c.fx * 0.01, foot[1] + c.fy * 0.01, foot[2]), (c.fx, c.fy, 0.0), flen, fwidth, 0.026, P["zori"])
        mk.obox(c, (foot[0] + c.fx * 0.015, foot[1] + c.fy * 0.015, foot[2] + 0.022), (c.fx, c.fy, 0.0), 0.035, 0.060, 0.014, P["zori_strap"], outline=False)


def draw_obi(c):
    """Faixa Obi de seda púrpura Heian amarrada na cintura."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065

    mk.cbox(c, bx, by, z, c.pelvis_w - 0.01, c.pelvis_w * 0.72, 0.070, P["obi"])
    mk.obox(c, (bx + fx * 0.078, by + fy * 0.078, z + 0.010), (px, py, 0.0), 0.045, 0.006, 0.006, P["gold_thread"], outline=False)


def draw_torso(c):
    """
    Tronco nobre Kariginu de Seimei:
    - Manto de seda branca pura com caimento amplo.
    - Colarinho cerimonial Heian arredondado em índigo celestial com debrum dourado rente ao pescoço.
    - Palas cerimoniais em índigo com bordados dourados no topo dos ombros.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    front = 0.088

    if mk.depth(c, fx, fy) > -0.05:
        # Colarinho cerimonial Heian arredondado rente ao pescoço
        mk.obox(c, (bx + fx * (front - 0.004), by + fy * (front - 0.004), tz + 0.220), (0.0, 0.0, 1.0), 0.035, 0.080, 0.016, P["robe_white"], up=(fx, fy, 0.0), outline=False)
        mk.obox(c, (bx + fx * front, by + fy * front, tz + 0.222), (0.0, 0.0, 1.0), 0.025, 0.065, 0.010, P["indigo"], up=(fx, fy, 0.0), outline=False)

        # Palas cerimoniais em índigo sobre os ombros com debrum dourado
        for s in (-1.0, 1.0):
            yoke_pos = (bx + px * 0.085 * s, by + py * 0.085 * s, tz + 0.225)
            mk.obox(c, yoke_pos, (fx, fy, 0.0), 0.052, 0.045, 0.014, P["indigo"], up=(0.0, 0.0, 1.0), outline=False)
            mk.obox(c, (yoke_pos[0] + fx * 0.012, yoke_pos[1] + fy * 0.012, yoke_pos[2] + 0.002), (fx, fy, 0.0), 0.026, 0.038, 0.006, P["gold_thread"], up=(0.0, 0.0, 1.0), outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço com manga ampla de seda branca Kariginu."""
    P = pal()
    return mk.arm(
        c, shoulder, hand, side,
        skin=P["skin"],
        sleeve=P["robe_white"],
        sleeve_to=0.72,
        w=0.046,
        bend=0.022
    )


def draw_sleeves(c, arm_segments):
    """
    Mangas amplas esvoaçantes de Kariginu pendendo dos ombros aos cotovelos:
    - Aplicam normal_vec = (fx, fy, 0.0) e side_vec = (px, py, 0.0) para caimento vertical natural.
    """
    P = pal()
    for s_pt, e_pt, side in arm_segments:
        drop_z = e_pt[2] - 0.12
        mid_drop = (e_pt[0] - c.fx * 0.03, e_pt[1] - c.fy * 0.03, drop_z)

        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[s_pt, e_pt, mid_drop],
            widths=[0.065, 0.095, 0.115],
            depth_thick=0.025,
            colors=[P["robe_white"], P["robe_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )
        # Barra da manga em índigo celestial com borda dourada
        mk.obox(c, mid_drop, (c.px * side, c.py * side, 0.0), 0.10, 0.022, 0.015, P["indigo"], up=(c.fx, c.fy, 0.0), outline=False)


def draw_head(c):
    """
    Cabeça de Seimei e Chapéu Cerimonial Eboshi Heian:
    1. Chapéu Tate-Eboshi alto laqueado preto no topo da cabeça.
    2. Cordão ornamental fino de seda púrpura subindo pelo flanco esquerdo do Eboshi.
    3. Cordões de seda púrpura (Kake-o) descendo rente à mandíbula até o nó na garganta.
    4. Brincos dourados delicados sob as orelhas.
    5. Rosto anime 3D desenhado com olhos ametista luminosos, cílios alados e lábios facetados.
    6. Franja reta Hime-cut sobre a testa e mechas laterais (bin-sogi) emoldurando as bochechas.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w

    # 1. Base do Chapéu Eboshi repousando sobre a coroa da cabeça
    crown_z = hz + 0.142
    eboshi_base = (bx - fx * 0.008, by - fy * 0.008, crown_z)
    eboshi_tip = (bx - fx * 0.030, by - fy * 0.030, crown_z + 0.220)

    # Tate-Eboshi Heian de laca negra
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        eboshi_base, eboshi_tip,
        w_start=hw * 0.96, h_start=hw * 0.98,
        w_end=hw * 0.38, h_end=hw * 0.54,
        color=P["eboshi"],
        up=(fx, fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Vinco tradicional no topo do Eboshi
    fold_base = (eboshi_tip[0] + fx * 0.006, eboshi_tip[1] + fy * 0.006, crown_z + 0.155)
    fold_tip = (eboshi_tip[0], eboshi_tip[1], crown_z + 0.222)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        fold_base, fold_tip,
        w_start=hw * 0.22, h_start=hw * 0.28,
        w_end=hw * 0.12, h_end=hw * 0.16,
        color=P["eboshi_crease"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Cordão ornamental no flanco do Eboshi
    cord_eboshi_bot = (eboshi_base[0] + px * (hw * 0.46) - fx * 0.008, eboshi_base[1] + py * (hw * 0.46) - fy * 0.008, crown_z + 0.012)
    cord_eboshi_top = (eboshi_tip[0] + px * (hw * 0.18) - fx * 0.010, eboshi_tip[1] + py * (hw * 0.18) - fy * 0.010, crown_z + 0.185)
    mk.obox(c, cord_eboshi_bot, (0.0, 0.0, 1.0), 0.012, 0.012, 0.012, P["purple_cord"], outline=False)
    mk.limb(c, cord_eboshi_bot, cord_eboshi_top, 0.007, P["purple_cord"], outline=False)

    # 2. Cordões laterais (Kake-o)
    c_throat = (bx + fx * 0.032, by + fy * 0.032, hz - 0.018)
    for s in (-1.0, 1.0):
        is_behind = mk.depth(c, px * s, py * s) < -0.01
        if not is_behind:
            c_ear = (bx + px * (hw * 0.44 * s) - fx * 0.015, by + py * (hw * 0.44 * s) - fy * 0.015, hz + 0.070)
            c_jaw = (bx + px * (hw * 0.24 * s) - fx * 0.002, by + py * (hw * 0.24 * s) - fy * 0.002, hz + 0.002)
            mk.limb(c, c_ear, c_jaw, 0.003, P["purple_cord"], outline=False)
            mk.limb(c, c_jaw, c_throat, 0.003, P["purple_cord"], outline=False)
            mk.obox(c, (c_ear[0] + fx * 0.006, c_ear[1] + fy * 0.006, hz + 0.048), (0.0, 0.0, 1.0), 0.008, 0.008, 0.012, P["gold_thread"], outline=False)

    # Laço cerimonial sob o queixo
    if mk.facing_camera(c):
        mk.obox(c, c_throat, (0.0, 0.0, 1.0), 0.012, 0.014, 0.006, P["purple_cord"], up=(px, py, 0.0), outline=False)
        mk.limb(c, (c_throat[0] - px * 0.003, c_throat[1] - py * 0.003, c_throat[2]),
                   (c_throat[0] - px * 0.006 + fx * 0.003, c_throat[1] - py * 0.006 + fy * 0.003, c_throat[2] - 0.022), 0.003, P["purple_cord"], outline=False)
        mk.limb(c, (c_throat[0] + px * 0.003, c_throat[1] + py * 0.003, c_throat[2]),
                   (c_throat[0] + px * 0.006 + fx * 0.003, c_throat[1] + py * 0.006 + fy * 0.003, c_throat[2] - 0.022), 0.003, P["purple_cord"], outline=False)

    # 3. Rosto anime esculpido 3D
    if not getattr(c, "_face_drawn", False):
        draw_portrait_face_3d(c, char_type="seimei")
        c._face_drawn = True

    # 4. Franja Hime-cut reta sobre a testa
    if mk.facing_camera(c):
        front_d = hw * 0.50 + 0.006
        for s in (-1.0, 1.0):
            p0 = (bx + fx * front_d + px * 0.004 * s, by + fy * front_d + py * 0.004 * s, hz + 0.144)
            p1 = (bx + fx * (front_d + 0.002) + px * 0.036 * s, by + fy * (front_d + 0.002) + py * 0.036 * s, hz + 0.122)
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                p0, p1,
                w_start=0.022, h_start=0.010,
                w_end=0.016, h_end=0.008,
                color=P["hair"],
                up=(0.0, 0.0, 1.0),
                outline=False,
                alpha=c.alpha,
            )

    # 5. Mechas laterais Hime-cut (bin-sogi)
    for s in (-1.0, 1.0):
        is_behind = mk.depth(c, px * s, py * s) < -0.02
        if not is_behind:
            p_top = (bx + px * (hw * 0.48 * s) + fx * 0.010, by + py * (hw * 0.48 * s) + fy * 0.010, hz + 0.142)
            p_mid = (bx + px * (hw * 0.46 * s) + fx * 0.014, by + py * (hw * 0.46 * s) + fy * 0.014, hz + 0.090)
            p_bot = (bx + px * (hw * 0.44 * s) + fx * 0.016, by + py * (hw * 0.44 * s) + fy * 0.016, hz + 0.038)
            draw_ribbon_mesh_3d(
                c.surface, c.camera,
                spine_points=[p_top, p_mid, p_bot],
                widths=[0.024, 0.028, 0.026],
                depth_thick=0.010,
                colors=[P["hair"], P["hair_dark"]],
                side_vec=(px * s, py * s, 0.0),
                normal_vec=(fx, fy, 0.0),
                outline=False,
                alpha=c.alpha,
            )


def draw_front(c, hand_l, hand_r):
    """
    Renderiza os artefatos sagrados:
    - Talismã Ofuda incandescente na mão direita com a cor do elemento ativo.
    - Leque cerimonial Sensu (fechado ou aberto em leque).
    - Pássaros Shikigami de origami em voo astral quando em intro, vitória ou deslize.
    """
    P = pal()
    r_x, r_y, r_z = hand_r
    l_x, l_y, l_z = hand_l
    bx, by, tz, fx, fy, px, py = _coords(c)
    extra = getattr(c, "extra_props", None) or getattr(c, "extra", None) or {}
    elem = extra.get("element", "wood")

    # Mapeamento da cor do elemento ativo
    elem_colors = {
        "wood": P["elem_wood"],
        "fire": P["elem_fire"],
        "earth": P["elem_earth"],
        "metal": P["elem_metal"],
        "water": P["elem_water"],
        "yinyang": P["elem_yinyang"],
    }
    col_aura = elem_colors.get(elem, P["spiritual_aura"])

    # 1. Talismã Ofuda retangular de papel sagrado
    pose = extra.get("pose", "")
    show_ofuda = pose not in ("imperial_bow", "heian_bow", "shikigami_glide")

    if show_ofuda:
        ofuda_pos = (r_x + fx * 0.04, r_y + fy * 0.04, r_z + 0.04)
        mk.obox(c, ofuda_pos, (fx * 0.4, fy * 0.4, 0.9), 0.14, 0.065, 0.012, P["ofuda_paper"], up=(px, py, 0.0), outline=True)
        # Inscrição do kanji místico colorido conforme o elemento ativo
        mk.obox(c, (ofuda_pos[0] + fx * 0.01, ofuda_pos[1] + fy * 0.01, ofuda_pos[2] + 0.02), (fx * 0.4, fy * 0.4, 0.9), 0.09, 0.032, 0.014, col_aura, up=(px, py, 0.0), outline=False)

        # Brilho místico ao conjurar / atacar
        is_melee = getattr(c, "is_melee", False)
        atk_p = getattr(c, "atk_progress", None)
        if is_melee and atk_p is not None:
            prog = atk_p
            if 0.20 <= prog <= 0.80:
                mk.cbox(c, ofuda_pos[0] + fx * 0.08, ofuda_pos[1] + fy * 0.08, ofuda_pos[2], 0.16, 0.16, 0.16, col_aura, outline=False)
                mk.cbox(c, ofuda_pos[0] + fx * 0.08, ofuda_pos[1] + fy * 0.08, ofuda_pos[2], 0.09, 0.09, 0.09, P["spiritual_core"], outline=False)

    # 2. Leque Sensu Cerimonial na mão esquerda
    is_fan_open = pose in ("sensu_fan_flick", "onmyoji_ready", "sensu_twirl", "astral_guard", "parry") or extra.get("is_parry", False)
    fan_pos = (l_x - fx * 0.02 - px * 0.02, l_y - fy * 0.02 - py * 0.02, l_z + 0.04)

    if is_fan_open:
        # Leque aberto em semicírculo gracioso
        mk.obox(c, fan_pos, (fx, fy, 0.0), 0.08, 0.18, 0.012, P["sensu_paper"], up=(0.0, 0.0, 1.0), outline=True)
        mk.obox(c, (fan_pos[0] + fx * 0.005, fan_pos[1] + fy * 0.005, fan_pos[2]), (fx, fy, 0.0), 0.03, 0.04, 0.016, P["sensu_wood"], up=(0.0, 0.0, 1.0), outline=False)
    else:
        # Leque dobrado compacto
        mk.obox(c, fan_pos, (fx * 0.6, fy * 0.6, -0.8), 0.20, 0.035, 0.022, P["sensu_wood"], up=(px, py, 0.0), outline=True)

    # 3. Pássaros de Papel Origami Shikigami (em voo orbital durante intro, vitória e deslize)
    if pose in ("shikigami_descent", "sensu_fan_flick", "onmyoji_ready", "birds_ascend", "shikigami_glide"):
        walk_t = getattr(c, "walk_timer", 0.0)
        p_val = extra.get("p", walk_t)
        for i, ang_off in enumerate((0.0, 2.1, 4.2)):
            bird_ang = p_val * 6.0 + ang_off
            bird_r = 0.28 + 0.08 * math.sin(bird_ang * 2.0)
            bird_x = bx + math.cos(bird_ang) * bird_r
            bird_y = by + math.sin(bird_ang) * bird_r
            bird_z = tz + 0.15 + 0.06 * math.cos(bird_ang * 3.0)

            # Asas de origami facetadas
            wing_flap = math.sin(p_val * 16.0 + i) * 0.03
            draw_tapered_frustum_3d(
                c.surface, c.camera,
                (bird_x, bird_y, bird_z - 0.02),
                (bird_x + math.cos(bird_ang) * 0.06, bird_y + math.sin(bird_ang) * 0.06, bird_z + 0.02 + wing_flap),
                w_start=0.05, h_start=0.01,
                w_end=0.02, h_end=0.005,
                color=P["ofuda_paper"],
                up=(0.0, 0.0, 1.0),
                outline=True,
                alpha=c.alpha,
            )
