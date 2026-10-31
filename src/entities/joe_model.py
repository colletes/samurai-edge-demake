"""
Joe, o American Ninja & Operador Tático (Sub-fase 2.4):
- Balaclava preta tática contínua cobrindo cabeça, nuca e mandíbula com abertura para o olhar penetrante.
- Bandana tática na testa com emblema do sol vermelho e pontas de tecido esvoaçando atrás ao vento.
- Óculos de visão noturna (NVG) de lente dupla ciano/esmeralda articulados e erguidos sobre a testa.
- Chapéu de cowboy 3D em couro marrom com aba modelada e vinco na copa para a pose de vitória.
- Banjo de madeira 3D artesanal com ressonador oitavado, pele clara, braço de trastes e cordas para a pose de vitória.
- Fuma Shuriken (Moinho Gigante) de 4 lâminas recurvadas de aço fosco para o Finisher B.
- Colete tático plate-carrier coiote com carregadores de 30 tiros, rádio tático com antena, granada M67 e patch da bandeira.
- Farda militar camuflada verde-oliva com mangas arregaçadas, luvas táticas e cotoveleiras.
- Calças táticas contínuas sem quebras ou degraus nos joelhos, com joelheiras anatômicas e botas de combate.
- Mochila de assalto 3D e bainha de katana cruzando as costas em diagonal.
- Kunai tática na mão direita e Shuriken de combate na esquerda; single-pass rendering garantido sem duplicação de braços.
- Ordenação dinâmica por profundidade (Painter's Algorithm): costas e mochila ocluem braços e armas em 360°.
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.mesh_primitives import draw_ribbon_mesh_3d

PALETTE = {
    "camo": (82, 90, 62), "camo_dark": (54, 60, 40), "camo_light": (110, 120, 84),
    "vest": (138, 120, 82), "vest_dark": (98, 84, 56), "vest_light": (168, 148, 104),
    "pouch": (112, 98, 66), "pouch_dark": (80, 68, 44),
    "balaclava": (26, 27, 31), "balaclava_light": (46, 48, 56), "balaclava_dark": (16, 17, 20),
    "hair": (26, 27, 31), "neck": (26, 27, 31),
    "skin": (228, 186, 150), "skin_shadow": (196, 152, 120),
    "headband": (226, 212, 172), "headband_dark": (168, 154, 118),
    "sun": (198, 38, 42), "sun_light": (235, 65, 70),
    "nvg": (34, 38, 42), "nvg_mount": (58, 62, 68), "lens": (64, 215, 195), "lens_glow": (160, 248, 238),
    "knee": (38, 42, 36), "knee_strap": (24, 26, 22),
    "boot": (48, 44, 36), "sole": (24, 22, 18), "glove": (28, 28, 30),
    "pack": (68, 76, 52), "pack_dark": (48, 54, 38), "strap": (38, 34, 26),
    "steel": (216, 226, 240), "steel_dark": (88, 92, 102),
    "wood": (96, 68, 42), "scabbard": (32, 32, 36),
    "radio": (32, 34, 36), "antenna": (22, 22, 24), "grenade": (58, 82, 48),
    "flag_blue": (32, 58, 138), "flag_red": (186, 32, 38), "flag_white": (235, 238, 242),
    # Novos elementos: Chapéu de Cowboy, Banjo e Fuma Shuriken
    "hat": (92, 58, 36), "hat_dark": (60, 36, 22), "hat_band": (34, 28, 26),
    "banjo_wood": (132, 82, 44), "banjo_rim": (195, 202, 212), "banjo_skin": (245, 240, 225),
    "banjo_neck": (105, 62, 34), "banjo_strings": (225, 235, 250),
    "fuma_steel": (214, 224, 238), "fuma_dark": (70, 75, 85), "fuma_core": (185, 38, 42),
}

LEGACY_MATERIALS = {
    "camo": "canvas", "camo_dark": "canvas", "vest": "canvas", "vest_dark": "canvas",
    "pouch": "canvas", "pack": "canvas", "pack_dark": "canvas",
    "boot": "leather", "glove": "leather", "knee": "leather", "strap": "leather",
    "balaclava": "knit", "headband": "canvas", "steel": "steel", "steel_dark": "metal",
    "scabbard": "lacquer", "nvg": "metal"
}

MATERIALS = {
    "camo": "canvas", "camo_dark": "canvas", "camo_light": "canvas",
    "vest": "canvas", "vest_dark": "canvas", "vest_light": "canvas",
    "pouch": "canvas", "pouch_dark": "canvas",
    "pack": "canvas", "pack_dark": "canvas", "strap": "leather",
    "boot": "leather", "sole": "leather", "glove": "leather", "knee": "leather", "knee_strap": "leather",
    "balaclava": "knit", "balaclava_light": "knit", "balaclava_dark": "knit",
    "headband": "canvas", "headband_dark": "canvas",
    "steel": "steel", "steel_dark": "metal",
    "scabbard": "lacquer", "nvg": "metal", "nvg_mount": "metal",
    "hat": "leather", "hat_dark": "leather",
    "banjo_wood": "wood", "banjo_rim": "metal", "banjo_skin": "canvas", "banjo_neck": "wood",
    "fuma_steel": "steel", "fuma_dark": "metal",
}


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def attack_arms(c):
    """Estocada tática de kunai: a mão direita avança em linha reta com zanshin; esquerda em guarda."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    p = c.atk_progress if c.atk_progress is not None else 0.0
    t = _smooth((p - 0.2) / 0.45)
    back = 1.0 - _smooth(p / 0.2)
    reach = 0.04 + 0.42 * t - 0.12 * back
    right = (bx + fx * reach - px * 0.12, by + fy * reach - py * 0.12, tz + 0.11 + 0.08 * t)
    left = (bx + fx * (0.15 + 0.06 * t) + px * 0.11, by + fy * (0.15 + 0.06 * t) + py * 0.11, tz + 0.19)
    return left, right


def attack_arms_at(c, p):
    saved = c.atk_progress
    c.atk_progress = p
    try:
        return attack_arms(c)[1]
    finally:
        c.atk_progress = saved


def idle_arms(c):
    """Guarda tática compacta de operações especiais."""
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    sway = math.sin(c.walk_timer * (6.5 if c.is_moving else 2.2)) * (0.025 if c.is_moving else 0.012)
    left = (bx + fx * 0.14 + px * 0.12, by + fy * 0.14 + py * 0.12 + sway, tz + 0.16)
    right = (bx + fx * 0.18 - px * 0.11, by + fy * 0.18 - py * 0.11 - sway, tz + 0.14)
    return left, right


def victory_arms(c, p=0.0, pose=""):
    """
    Coreografia cinemática de vitória do Joe com LERP contínuo (Zero Freeze Policy):
    - Fase 1 (0.00 <= p < 0.22 ou pose == 'hat_tip'):
      Transição suave da guarda de combate para a mão direita subir e tocar/inclinar a aba do chapéu de cowboy (Hat Tip de veterano), com a mão esquerda repousando no cinto.
    - Fase 2 (0.22 <= p < 0.45 ou pose == 'draw_banjo'):
      Transição da ponta do chapéu para sacar e empunhar o banjo de madeira na altura do peito/cintura com as duas mãos.
    - Fase 3 (0.45 <= p <= 1.0 ou pose in ('cowboy_banjo', 'cowboy_victory')):
      Dedilhado rápido e swing rítmico ininterrupto sobre as cordas do banjo, com micro-slide nos trastes e vibração de palhetada!
    """
    bx, by, tz, hz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.head_z, c.fx, c.fy, c.px, c.py
    extra = getattr(c, "extra_props", {}) or {}

    vic_p = extra.get("p", p)
    seg_u = extra.get("seg_u", 0.0)

    idle_l, idle_r = idle_arms(c)
    belt_l = (bx + fx * 0.05 - px * 0.16, by + fy * 0.05 - py * 0.16, tz + 0.03)
    hat_touch = (bx + fx * 0.12 + px * 0.04, by + fy * 0.12 + py * 0.04, hz + 0.14)
    banjo_ready_l = (bx + fx * 0.14 - px * 0.17, by + fy * 0.14 - py * 0.17, tz + 0.23)
    banjo_ready_r = (bx + fx * 0.17 + px * 0.03, by + fy * 0.17 + py * 0.03, tz + 0.08)

    if pose == "hat_tip" or (not pose and vic_p < 0.22):
        u = _smooth(seg_u if pose == "hat_tip" else (vic_p / 0.22))
        tip = math.sin(u * math.pi) * 0.022
        hat_r = (hat_touch[0], hat_touch[1], hat_touch[2] - tip)
        left = mk.lerp(idle_l, belt_l, u)
        right = mk.lerp(idle_r, hat_r, u)
        return left, right

    elif pose == "draw_banjo" or (not pose and vic_p < 0.45):
        u = _smooth(seg_u if pose == "draw_banjo" else ((vic_p - 0.22) / 0.23))
        left = mk.lerp(belt_l, banjo_ready_l, u)
        right = mk.lerp(hat_touch, banjo_ready_r, u)
        return left, right

    else:
        # Fase 3: Dedilhado rítmico e swing do banjo ininterrupto
        t_tick = getattr(c, "walk_timer", 0.0) * 16.0 + getattr(c, "state_timer", 0.0) * 12.0
        t_strum = (vic_p * 46.0) + t_tick

        strum_x = math.sin(t_strum) * 0.036
        strum_z = math.cos(t_strum * 1.6) * 0.018
        strum_y = math.sin(t_strum * 0.8) * 0.012

        fret_slide = math.sin(t_strum * 0.28) * 0.032
        fret_tap = abs(math.cos(t_strum * 1.3)) * 0.010

        left = (banjo_ready_l[0] - px * fret_slide,
                banjo_ready_l[1] - py * fret_slide,
                banjo_ready_l[2] - fret_slide * 0.45 + fret_tap)
        right = (banjo_ready_r[0] + fx * strum_x + px * strum_y,
                 banjo_ready_r[1] + fy * strum_x + py * strum_y,
                 banjo_ready_r[2] + strum_z)
        return left, right


def _hands(c):
    """Retorna a posição das mãos (esquerda, direita) calculadas com animação contínua (LERP)."""
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    p = extra.get("progress", 0.0)
    bx, by, tz, hz = c.base_x, c.base_y, c.torso_z, c.head_z
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # 1. Coreografia Contínua de Intro com Interpolação LERP (Sem poses estáticas)
    if pose in ("adjust_gloves", "dog_whistle", "tactical_guard") or getattr(c, "state", "") == "INTRO":
        intro_p = getattr(c, "atk_progress", 0.0) or extra.get("seg_u", p) or p
        # Fase 1: Ajuste de luvas táticas com tração e micro-movimento
        if intro_p < 0.38:
            u = _smooth(intro_p / 0.38)
            pull = math.sin(u * math.pi * 3.0) * 0.025
            left = (bx + fx * (0.12 + u * 0.04) - px * 0.06, by + fy * (0.12 + u * 0.04) - py * 0.06, tz + 0.10 + u * 0.04)
            right = (left[0] + fx * 0.02 + px * (0.02 + pull), left[1] + fy * 0.02 + py * (0.02 + pull), left[2] - 0.02)
            return left, right

        # Fase 2: Transição fluida da luva para o assobio tático aos lábios
        elif intro_p < 0.70:
            u = _smooth((intro_p - 0.38) / 0.32)
            # Posições de partida (fim do ajuste de luva)
            start_l = (bx + fx * 0.16 - px * 0.06, by + fy * 0.16 - py * 0.06, tz + 0.14)
            start_r = (start_l[0] + fx * 0.02 + px * 0.02, start_l[1] + fy * 0.02 + py * 0.02, start_l[2] - 0.02)
            # Posições-alvo do assobio (dedos aos lábios e braço esquerdo chamando o cão)
            target_r = (bx + fx * 0.09, by + fy * 0.09, hz + 0.04)
            target_l = (bx + fx * 0.24 + px * 0.14, by + fy * 0.24 + py * 0.14, tz + 0.04)
            return mk.lerp(start_l, target_l, u), mk.lerp(start_r, target_r, u)

        # Fase 3: Transição contínua do assobio para a postura de guarda tática
        else:
            u = _smooth((intro_p - 0.70) / 0.30)
            whistle_r = (bx + fx * 0.09, by + fy * 0.09, hz + 0.04)
            whistle_l = (bx + fx * 0.24 + px * 0.14, by + fy * 0.24 + py * 0.14, tz + 0.04)
            idle_l, idle_r = idle_arms(c)
            guard_l = (idle_l[0] + fx * 0.06, idle_l[1] + fy * 0.06, idle_l[2] + 0.04)
            guard_r = (idle_r[0] + fx * 0.08, idle_r[1] + fy * 0.08, idle_r[2] + 0.02)
            return mk.lerp(whistle_l, guard_l, u), mk.lerp(whistle_r, guard_r, u)

    # 2. Sequência Cinemática de Vitória com Chapéu de Cowboy e Banjo (LERP Contínuo)
    if pose in ("hat_tip", "draw_banjo", "cowboy_banjo", "cowboy_victory") or extra.get("intro_victory_state") == "VICTORY":
        return victory_arms(c, p, pose)

    # 5. Flic-flac acrobático para frente (Esquiva / Roll 360°)
    if pose == "flic_flac" or getattr(c, "state", "") == "ROLL":
        prog = extra.get("p", p)
        # Transição cinemática de mãos tocando o solo e impulsionando o corpo
        if prog < 0.30:
            u = _smooth(prog / 0.30)
            # Braços descem para frente buscando o solo
            fl_l = (bx + fx * (0.08 + u * 0.14) + px * 0.14, by + fy * (0.08 + u * 0.14) + py * 0.14, tz + 0.18 - u * 0.16)
            fl_r = (bx + fx * (0.08 + u * 0.14) - px * 0.14, by + fy * (0.08 + u * 0.14) - py * 0.14, tz + 0.18 - u * 0.16)
            return fl_l, fl_r
        elif prog < 0.70:
            # Ponto de apoio no chão (mãos impulsionam o solo)
            fl_l = (bx + fx * 0.16 + px * 0.15, by + fy * 0.16 + py * 0.15, max(0.04, c.base_z + 0.05))
            fl_r = (bx + fx * 0.16 - px * 0.15, by + fy * 0.16 - py * 0.15, max(0.04, c.base_z + 0.05))
            return fl_l, fl_r
        else:
            u = _smooth((prog - 0.70) / 0.30)
            # Recolhimento para a aterrissagem em pé
            fl_l = (bx + fx * (0.16 - u * 0.08) + px * 0.16, by + fy * (0.16 - u * 0.08) + py * 0.16, max(0.04, c.base_z + 0.05) + u * 0.22)
            fl_r = (bx + fx * (0.16 - u * 0.08) - px * 0.16, by + fy * (0.16 - u * 0.08) - py * 0.16, max(0.04, c.base_z + 0.05) + u * 0.22)
            return fl_l, fl_r

    # 6. Arremesso de Shuriken Triplo (Finisher A)
    if pose == "triple_shuriken":
        cycle_p = (p * 3.0) % 1.0
        t = _smooth(cycle_p)
        throw_reach = 0.05 + 0.38 * t
        left = (bx + fx * throw_reach + px * 0.08, by + fy * throw_reach + py * 0.08, tz + 0.16)
        right = (bx - fx * 0.10 - px * 0.14, by - fy * 0.10 - py * 0.14, tz + 0.09)
        return left, right

    # 7. Arremesso da Fuma Shuriken Moinho (Finisher B)
    if pose == "fuma_throw":
        t = _smooth(p)
        right = (bx + fx * (0.05 + 0.45 * t) - px * 0.08, by + fy * (0.05 + 0.45 * t) - py * 0.08, tz + 0.22 - 0.10 * t)
        left = (bx - fx * 0.14 + px * 0.16, by - fy * 0.14 + py * 0.16, tz + 0.12)
        return left, right

    if c.is_melee and c.atk_progress is not None:
        return attack_arms(c)

    return idle_arms(c)


def get_arms(c):
    """Exposição modular da cinemática dos braços para sincronização com o renderizador de humanoides."""
    return _hands(c)


def _back_gear(c):
    """Mochila tática de assalto e bainha de katana em diagonal nas costas."""
    P = pal()
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    back_dist = 0.13

    # Mochila modular MOLLE
    pack_pos = (bx - fx * back_dist, by - fy * back_dist, tz + 0.06)
    mk.cbox(c, pack_pos[0], pack_pos[1], pack_pos[2], 0.18, 0.15, 0.22, P["pack"])
    # Bolso superior da mochila
    mk.cbox(c, pack_pos[0] - fx * 0.025, pack_pos[1] - fy * 0.025, pack_pos[2] + 0.04, 0.15, 0.12, 0.10, P["pack_dark"], outline=False)
    # Fitas de compressão horizontais
    for zoff in (-0.03, 0.05):
        mk.cbox(c, pack_pos[0] - fx * 0.028, pack_pos[1] - fy * 0.028, pack_pos[2] + zoff, 0.16, 0.13, 0.015, P["strap"], outline=False)

    # Katana tática compacta e justa nas costas (sem vazar para fora do ombro/braço)
    d = mk.norm((px * 0.18 - fx * 0.02, py * 0.18 - fy * 0.02, 0.94))
    origin = (bx - fx * (back_dist + 0.03) - px * 0.06, by - fy * (back_dist + 0.03) - py * 0.06, tz - 0.06)
    # Bainha (saya) preta laqueada
    mk.obox(c, origin, d, 0.40, 0.036, 0.036, P["scabbard"])
    # Empunhadura tática com cordão (tsuka) projetando sobre o ombro
    hilt_orig = mk.add(origin, d, 0.36)
    mk.obox(c, hilt_orig, d, 0.14, 0.038, 0.038, P["camo_dark"])
    # Tsuba discreta e pomo
    mk.obox(c, hilt_orig, d, 0.018, 0.056, 0.056, P["steel_dark"], outline=False)
    mk.obox(c, mk.add(hilt_orig, d, 0.13), d, 0.018, 0.040, 0.040, P["steel"], outline=False)


def _draw_nvg(c):
    """Óculos de visão noturna (NVG) com lente dupla ciano/esmeralda articulados para cima."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py

    # Suporte basculante de titânio (mount bracket)
    mount_pt = (bx + fx * 0.065, by + fy * 0.065, hz + 0.155)
    mk.cbox(c, mount_pt[0], mount_pt[1], mount_pt[2], 0.055, 0.055, 0.028, P["nvg_mount"], outline=False)

    # Tubos binoculares orientados para cima/frente a 45°
    nvg_dir = mk.norm((fx * 0.55, fy * 0.55, 0.85))
    tubes_base = mk.add(mount_pt, nvg_dir, 0.025)

    # Ponte de ligação entre os tubos
    mk.obox(c, tubes_base, (px, py, 0.0), 0.09, 0.025, 0.025, P["nvg"], outline=False)

    # Cilindros ópticos dos dois olhos
    for s in (-1.0, 1.0):
        t_pos = (tubes_base[0] + px * 0.036 * s, tubes_base[1] + py * 0.036 * s, tubes_base[2])
        # Corpo do tubo
        mk.obox(c, t_pos, nvg_dir, 0.075, 0.032, 0.032, P["nvg"])
        # Anel de ajuste de foco metálico
        mk.obox(c, mk.add(t_pos, nvg_dir, 0.045), nvg_dir, 0.014, 0.036, 0.036, P["steel_dark"], outline=False)
        # Lente frontal brilhante ciano/esmeralda
        lens_pt = mk.add(t_pos, nvg_dir, 0.070)
        mk.obox(c, lens_pt, nvg_dir, 0.012, 0.030, 0.030, P["lens"], outline=False)
        mk.obox(c, mk.add(lens_pt, nvg_dir, 0.004), nvg_dir, 0.006, 0.016, 0.016, P["lens_glow"], outline=False)


def _draw_cowboy_hat(c):
    """
    Chapéu de cowboy clássico de couro marrom com aba modelada e vinco na copa.
    Diretiva 8: Aba estritamente horizontal (dir_z = 0.0) a partir da coroa (crown_z >= hz + 0.145).
    Montagem rígida e unificada com o crânio (zero deformação ou deslocamento de vértices).
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    
    # Altura fixa e segura da coroa: repousa perfeitamente sobre o topo do crânio sem cisalhamento
    crown_z = hz + 0.158

    # 1. Aba larga ovalada com laterais curvadas para cima (Aba do chapéu)
    brim_center = (bx, by, crown_z)
    mk.obox(c, brim_center, (fx, fy, 0.0), 0.28, 0.24, 0.018, P["hat"])
    for s in (-1.0, 1.0):
        flap_pt = (bx + px * 0.10 * s, by + py * 0.10 * s, crown_z + 0.012)
        mk.obox(c, flap_pt, (fx, fy, 0.0), 0.24, 0.05, 0.020, P["hat_dark"], outline=False)

    # 2. Faixa de couro preto na base da copa
    band_pt = (bx, by, crown_z + 0.018)
    mk.obox(c, band_pt, (fx, fy, 0.0), 0.16, 0.14, 0.022, P["hat_band"], outline=False)

    # 3. Copa estruturada com vinco central (Cattleman crease)
    mk.cbox(c, bx, by, crown_z + 0.055, 0.15, 0.13, 0.075, P["hat"])
    mk.cbox(c, bx, by, crown_z + 0.092, 0.14, 0.05, 0.016, P["hat_dark"], outline=False)


def _draw_banjo(c, hand_l, hand_r):
    """
    Banjo de madeira artesanal 3D:
    - Corpo circular de ressonador de madeira nobre.
    - Pele clara de bezerro/pergaminho no tambor central.
    - Aro metálico de afinação com colchetes prateados.
    - Braço comprido de jacarandá com escala freteada estendendo até a mão esquerda.
    - Cordas prateadas brilhantes com vibração sonora.
    """
    P = pal()
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py

    # Posição do tambor do banjo (junto ao abdômen/peito inferior de Joe)
    drum_pos = (bx + fx * 0.15 + px * 0.03, by + fy * 0.15 + py * 0.03, tz + 0.06)
    neck_dir = mk.norm((hand_l[0] - drum_pos[0], hand_l[1] - drum_pos[1], hand_l[2] - drum_pos[2]))

    # 1. Corpo/Ressonador circular (aproximação octagonal de caixa 3D orientada)
    mk.obox(c, drum_pos, (fx, fy, 0.1), 0.06, 0.17, 0.17, P["banjo_wood"])
    mk.obox(c, mk.add(drum_pos, (fx, fy, 0.1), 0.025), (fx, fy, 0.1), 0.02, 0.155, 0.155, P["banjo_rim"], outline=False)
    mk.obox(c, mk.add(drum_pos, (fx, fy, 0.1), 0.036), (fx, fy, 0.1), 0.01, 0.140, 0.140, P["banjo_skin"], outline=False)

    # Cavalete de madeira de bordo sobre a pele
    bridge_pos = mk.add(drum_pos, (fx, fy, 0.1), 0.042)
    mk.obox(c, bridge_pos, (px, py, 0.0), 0.045, 0.010, 0.012, P["wood"], outline=False)

    # 2. Braço do Banjo (Neck) ligando o tambor até a mão esquerda
    neck_len = math.dist(drum_pos, hand_l) + 0.08
    mk.obox(c, drum_pos, neck_dir, neck_len, 0.028, 0.024, P["banjo_neck"])
    mk.obox(c, mk.add(drum_pos, (fx, fy, 0.1), 0.012), neck_dir, neck_len, 0.024, 0.010, P["balaclava_dark"], outline=False)

    # 3. Mão do braço (Headstock) com 4 tarraxas prateadas no final
    head_pos = mk.add(drum_pos, neck_dir, neck_len)
    mk.obox(c, head_pos, neck_dir, 0.06, 0.038, 0.020, P["banjo_wood"])
    for s in (-1.0, 1.0):
        t_pos1 = (head_pos[0] + px * 0.022 * s, head_pos[1] + py * 0.022 * s, head_pos[2] + 0.01)
        t_pos2 = (head_pos[0] + px * 0.022 * s, head_pos[1] + py * 0.022 * s, head_pos[2] + 0.035)
        mk.cbox(c, t_pos1[0], t_pos1[1], t_pos1[2], 0.012, 0.012, 0.012, P["banjo_rim"], outline=False)
        mk.cbox(c, t_pos2[0], t_pos2[1], t_pos2[2], 0.012, 0.012, 0.012, P["banjo_rim"], outline=False)

    # 4. Cordas esticadas com brilho
    wire_start = mk.add(drum_pos, (fx, fy, 0.1), 0.045)
    wire_end = mk.add(head_pos, (fx, fy, 0.1), 0.010)
    mk.limb(c, wire_start, wire_end, 0.008, P["banjo_strings"], outline=False)


def _draw_fuma_shuriken(c, pos=None, angle=0.0):
    """
    Fuma Shuriken (Moinho de Vento Gigante) de 4 lâminas de aço recurvadas com núcleo vermelho.
    """
    P = pal()
    if pos is None:
        pos = (c.base_x + c.fx * 0.35, c.base_y + c.fy * 0.35, c.torso_z + 0.15)

    # 4 Lâminas recurvadas dispostas em cruz giratória
    for k in range(4):
        ang = angle + k * (math.pi / 2.0)
        blade_dir = (math.cos(ang) * c.fx + math.sin(ang) * c.px,
                     math.cos(ang) * c.fy + math.sin(ang) * c.py,
                     0.0)
        mk.obox(c, pos, blade_dir, 0.22, 0.048, 0.016, P["fuma_steel"])
        tip = mk.add(pos, blade_dir, 0.18)
        mk.obox(c, tip, blade_dir, 0.08, 0.026, 0.012, P["fuma_dark"], outline=False)

    mk.cbox(c, pos[0], pos[1], pos[2], 0.065, 0.065, 0.024, P["steel_dark"], outline=False)
    mk.cbox(c, pos[0], pos[1], pos[2], 0.038, 0.038, 0.028, P["fuma_core"], outline=False)


def _headband_tails(c):
    """Pontas de tecido da bandana que esvoaçam dinamicamente na nuca."""
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    knot_root = (bx - fx * 0.082, by - fy * 0.082, hz + 0.095)
    trail, amp, freq = mk.motion(c, 0.07)

    for k, s in enumerate((-1.0, 1.0)):
        offs = cloth.chain_offsets(3, c.walk_timer, 0.8 * k, trail, (px, py),
                                   amp=amp * 1.8, freq=freq * 1.2,
                                   wind=cloth.wind_at(knot_root[0], knot_root[1]), wind_gain=0.08)
        pts = [knot_root]
        for i, o in enumerate(offs):
            pt = (knot_root[0] - fx * 0.045 * (i + 1) + px * s * 0.028 * (i + 1) + o[0],
                  knot_root[1] - fy * 0.045 * (i + 1) + py * s * 0.028 * (i + 1) + o[1],
                  knot_root[2] - 0.035 * (i + 1) + o[2])
            pts.append(pt)
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=pts,
            widths=[0.022, 0.018, 0.012, 0.007],
            depth_thick=0.010,
            colors=[P["headband"], P["headband_dark"]],
            side_vec=(px, py, 0.0),
            normal_vec=(fx, fy, 0.0),
            outline=False,
            alpha=c.alpha,
        )


def _draw_weapons(c, arm_l, arm_r):
    """Renderiza equipamentos nas mãos com garantia de passagem única e sem armas duplicadas."""
    P = pal()
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")

    # Se estiver na pose de vitória de tocar banjo, desenha o banjo
    if pose in ("draw_banjo", "cowboy_banjo", "cowboy_victory") or (extra.get("intro_victory_state") == "VICTORY" and extra.get("p", 0.0) >= 0.22):
        _draw_banjo(c, arm_l, arm_r)
        return

    # Se estiver ajustando luvas, assobiando, flic flac ou tocando no chapéu, as mãos estão ocupadas/livres de armas
    if pose in ("adjust_gloves", "dog_whistle", "flic_flac", "hat_tip") or (extra.get("intro_victory_state") == "VICTORY" and extra.get("p", 0.0) < 0.22):
        return

    # Se estiver arremessando a Fuma Shuriken
    if pose == "fuma_throw":
        p = extra.get("progress", 0.0)
        rot = p * 18.0 * math.pi
        _draw_fuma_shuriken(c, pos=arm_r, angle=rot)
        return

    hand_l = (arm_l[0], arm_l[1], arm_l[2] - 0.065)
    hand_r = (arm_r[0], arm_r[1], arm_r[2] - 0.065)

    # 1. Kunai na mão direita (alinhada ao antebraço/ataque)
    d = mk.norm((c.fx * 0.95, c.fy * 0.95, 0.15 if c.is_melee else 0.40))
    mk.obox(c, mk.add(hand_r, d, -0.09), d, 0.10, 0.030, 0.030, P["glove"])
    mk.obox(c, mk.add(hand_r, d, -0.11), d, 0.020, 0.042, 0.016, P["steel_dark"], outline=False)  # anel pommel
    mk.obox(c, mk.add(hand_r, d, 0.02), d, 0.018, 0.052, 0.030, P["steel_dark"], outline=False)  # guarda
    mk.obox(c, mk.add(hand_r, d, 0.04), d, 0.130, 0.044, 0.014, P["steel"])
    mk.obox(c, mk.add(hand_r, d, 0.16), d, 0.060, 0.024, 0.012, P["steel"], outline=False)

    # 2. Shuriken de 4 pontas na mão esquerda
    for ang in (0.0, math.pi / 4):
        dir_s = (math.cos(ang) * c.fx + math.sin(ang) * c.px, math.cos(ang) * c.fy + math.sin(ang) * c.py, 0.0)
        mk.obox(c, (hand_l[0] - dir_s[0] * 0.06, hand_l[1] - dir_s[1] * 0.06, hand_l[2] - 0.01), dir_s, 0.12, 0.026, 0.012, P["steel_dark"], outline=False)
    mk.cbox(c, hand_l[0], hand_l[1], hand_l[2] - 0.010, 0.024, 0.024, 0.016, P["steel"], outline=False)

    # Rastro de ataque marcial durante golpe
    if c.is_melee and c.atk_progress is not None and c.atk_progress >= 0.35:
        for j in range(1, 4):
            ghost = attack_arms_at(c, c.atk_progress - 0.045 * j)
            g = (ghost[0], ghost[1], ghost[2] - 0.065)
            mk.band(c, (mk.add(g, d, 0.08), mk.add(g, d, 0.22), mk.add(hand_r, d, 0.22), mk.add(hand_r, d, 0.08)), (190, 220, 245, int(150 / j)))


def draw_behind(c):
    """Camada traseira: renderizada ANTES do tronco/pernas para elementos que ficam atrás."""
    d_torso = mk.depth(c, c.base_x, c.base_y)

    # 1. Mochila tática e katana se estiverem no lado de trás
    d_back = mk.depth(c, c.base_x - c.fx * 0.15, c.base_y - c.fy * 0.15)
    if d_back < d_torso:
        _back_gear(c)

    # 2. Cauda da bandana se estiver atrás
    d_knot = mk.depth(c, c.base_x - c.fx * 0.08, c.base_y - c.fy * 0.08)
    if d_knot < d_torso:
        _headband_tails(c)

    # 3. Braços e armas se as mãos estiverem atrás do tronco (costas voltadas para a câmera)
    hand_l, hand_r = _hands(c)
    d_gear = max(mk.depth(c, hand_l[0], hand_l[1]), mk.depth(c, hand_r[0], hand_r[1]))
    if d_gear < d_torso - 0.01:
        _draw_weapons(c, hand_l, hand_r)


def draw_legs(c):
    """Calças táticas contínuas sem degraus nos joelhos, com joelheiras anatômicas e botas."""
    P = pal()
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]

        # Perna contínua 3D: coxa, joelho e canela compartilham vértices
        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0], sh[1], sh[2] + 0.16)
        ankle = (ft[0], ft[1], ft[2] + 0.06)

        # Calça tática camuflada contínua
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, ankle],
            widths=[0.118, 0.104, 0.086],
            depth_thick=0.092,
            colors=[P["camo"], P["camo_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Joelheira tática anatômica curva (sem prateleira)
        mk.cbox(c, knee[0] + c.fx * 0.024, knee[1] + c.fy * 0.024, knee[2] - 0.015, 0.088, 0.088, 0.065, P["knee"], outline=True)
        mk.cbox(c, knee[0] + c.fx * 0.034, knee[1] + c.fy * 0.034, knee[2] - 0.015, 0.054, 0.054, 0.032, P["knee_strap"], outline=False)

        # Bota de combate com cano e solado de borracha
        mk.obox(c, (ft[0] - c.fx * 0.040, ft[1] - c.fy * 0.040, ft[2]), (c.fx, c.fy, 0.0), 0.145, 0.085, 0.026, P["sole"])
        mk.obox(c, (ft[0] - c.fx * 0.020, ft[1] - c.fy * 0.020, ft[2] + 0.024), (c.fx, c.fy, 0.0), 0.115, 0.075, 0.042, P["boot"])
        mk.cbox(c, ankle[0], ankle[1], ankle[2] + 0.010, 0.086, 0.086, 0.070, P["boot"], outline=True)


def draw_obi(c):
    """Cinto de nylon tático com fivela, coldre moldado na coxa direita e bolsa utilitária."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07

    # Cinto tático
    mk.cbox(c, bx, by, z, c.pelvis_w, c.pelvis_w * 0.78, 0.065, P["strap"])
    if mk.depth(c, fx, fy) > -0.05:
        mk.cbox(c, bx + fx * 0.098, by + fy * 0.098, z + 0.005, 0.046, 0.028, 0.045, P["steel_dark"], outline=False)

    # Coldre rígido de pistola na coxa direita
    hx, hy = bx + px * 0.155 - fx * 0.01, by + py * 0.155 - fy * 0.01
    mk.cbox(c, hx, hy, z - 0.11, 0.055, 0.065, 0.13, P["balaclava_dark"])
    mk.cbox(c, hx + fx * 0.01, hy + fy * 0.01, z - 0.09, 0.045, 0.055, 0.03, P["pouch"], outline=False)

    # Granada e bolsa utilitária no flanco esquerdo
    mk.cbox(c, bx - px * 0.135 + fx * 0.03, by - py * 0.135 + fy * 0.03, z - 0.01, 0.048, 0.048, 0.065, P["grenade"])


def draw_torso(c):
    """Colete plate-carrier coiote com 3 porta-carregadores, rádio tático com antena e patch da bandeira."""
    P = pal()
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    d_torso = mk.depth(c, bx, by)

    # Base da farda militar BDU verde-oliva
    mk.cbox(c, bx, by, tz + 0.02, 0.29, 0.22, 0.16, P["camo"])

    # Colete tático plate-carrier coiote
    mk.cbox(c, bx, by, tz + 0.07, 0.31, 0.24, 0.19, P["vest"])

    # Mochila e katana se estiverem no lado frontal/visível da câmera
    d_back = mk.depth(c, bx - fx * 0.15, by - fy * 0.15)
    if d_back >= d_torso:
        _back_gear(c)

    # Detalhes frontais táticos SÓ renderizam se a frente estiver voltada para a câmera
    if mk.depth(c, fx, fy) > -0.05:
        front = 0.135

        # Três bolsos frontais para carregadores de fuzil (MOLLE mag pouches)
        for side in (-0.082, 0.0, 0.082):
            mk.cbox(c, bx + fx * front + px * side, by + fy * front + py * side, tz + 0.025, 0.065, 0.042, 0.088, P["pouch"])
            mk.cbox(c, bx + fx * front + px * side, by + fy * front + py * side, tz + 0.082, 0.052, 0.032, 0.025, P["balaclava"], outline=False)

        # Rádio tático no ombro esquerdo com antena
        rad_x = bx + fx * (front - 0.015) + px * 0.105
        rad_y = by + fy * (front - 0.015) + py * 0.105
        mk.cbox(c, rad_x, rad_y, tz + 0.175, 0.040, 0.035, 0.070, P["radio"])
        mk.limb(c, (rad_x, rad_y, tz + 0.210), (rad_x + fx * 0.01, rad_y + fy * 0.01, tz + 0.310), 0.010, P["antenna"], outline=False)

        # Granada de fragmentação M67 no peitoral direito
        mk.cbox(c, bx + fx * front - px * 0.095, by + fy * front - py * 0.095, tz + 0.165, 0.045, 0.042, 0.055, P["grenade"])

        # Patch da bandeira dos EUA no painel de velcro central do peito
        flag_x = bx + fx * (front + 0.005)
        flag_y = by + fy * (front + 0.005)
        mk.cbox(c, flag_x, flag_y, tz + 0.185, 0.068, 0.012, 0.042, P["flag_red"], outline=False)
        mk.cbox(c, flag_x, flag_y, tz + 0.185, 0.068, 0.013, 0.020, P["flag_white"], outline=False)
        mk.cbox(c, flag_x - px * 0.018, flag_y - py * 0.018, tz + 0.195, 0.032, 0.014, 0.022, P["flag_blue"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """Braço com manga militar BDU arregaçada, antebraço musculoso e luva tática."""
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], sleeve=P["camo"], sleeve_to=0.55, glove=P["glove"], w=0.066)


def draw_sleeves(c, arms):
    """Cotoveleiras táticas nos cotovelos."""
    P = pal()
    for s, e, side in arms:
        mk.cbox(c, e[0], e[1], e[2] - 0.015, 0.068, 0.068, 0.048, P["knee"], outline=False)


def draw_head(c):
    """Balaclava tática 3D contínua, bandana com sol vermelho e óculos NVG ou chapéu de cowboy."""
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    d_torso = mk.depth(c, bx, by)
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")

    # 1. Bandana tática na testa (4 facetas verticais abraçando o crânio)
    z_b0 = hz + 0.088
    z_b1 = hz + 0.116
    r0 = hw * 0.495 + 0.002
    r1 = hw * 0.475 + 0.002

    fl0 = (bx + fx * r0 - px * r0, by + fy * r0 - py * r0, z_b0)
    fr0 = (bx + fx * r0 + px * r0, by + fy * r0 + py * r0, z_b0)
    br0 = (bx - fx * r0 + px * r0, by - fy * r0 + py * r0, z_b0)
    bl0 = (bx - fx * r0 - px * r0, by - fy * r0 - py * r0, z_b0)

    fl1 = (bx + fx * r1 - px * r1, by + fy * r1 - py * r1, z_b1)
    fr1 = (bx + fx * r1 + px * r1, by + fy * r1 + py * r1, z_b1)
    br1 = (bx - fx * r1 + px * r1, by - fy * r1 + py * r1, z_b1)
    bl1 = (bx - fx * r1 - px * r1, by - fy * r1 - py * r1, z_b1)

    s_fl0 = c.camera.apply(fl0[0], fl0[1], fl0[2])
    s_fr0 = c.camera.apply(fr0[0], fr0[1], fr0[2])
    s_br0 = c.camera.apply(br0[0], br0[1], br0[2])
    s_bl0 = c.camera.apply(bl0[0], bl0[1], bl0[2])

    s_fl1 = c.camera.apply(fl1[0], fl1[1], fl1[2])
    s_fr1 = c.camera.apply(fr1[0], fr1[1], fr1[2])
    s_br1 = c.camera.apply(br1[0], br1[1], br1[2])
    s_bl1 = c.camera.apply(bl1[0], bl1[1], bl1[2])

    azimuth = getattr(c.camera, "azimuth", 0.0)
    fn_rx, fn_ry = mk.rotate_xy(fx, fy, azimuth)
    rn_rx, rn_ry = mk.rotate_xy(px, py, azimuth)

    band_faces = [
        ((fn_rx + fn_ry) > -0.05, (fn_rx + fn_ry) * r0, [s_fl0, s_fr0, s_fr1, s_fl1], P["headband"], True),
        ((rn_rx + rn_ry) > -0.05, (rn_rx + rn_ry) * r0, [s_fr0, s_br0, s_br1, s_fr1], P["headband_dark"], False),
        ((-fn_rx - fn_ry) > -0.05, (-fn_rx - fn_ry) * r0, [s_br0, s_bl0, s_bl1, s_br1], P["headband_dark"], False),
        ((-rn_rx - rn_ry) > -0.05, (-rn_rx - rn_ry) * r0, [s_bl0, s_fl0, s_fl1, s_bl1], P["headband_dark"], False),
    ]

    band_faces.sort(key=lambda item: item[1])
    for visible, depth_val, poly, col, is_front in band_faces:
        if not visible:
            continue
        pygame.draw.polygon(c.surface, col, poly)
        pygame.draw.line(c.surface, P["headband_dark"], poly[0], poly[1], 1)
        pygame.draw.line(c.surface, P["headband_dark"], poly[3], poly[2], 1)

        if is_front:
            sun_z = (z_b0 + z_b1) * 0.5
            r_sun = 0.012
            r_core = 0.006
            c_sun = (bx + fx * (r0 + 0.003), by + fy * (r0 + 0.003), sun_z)
            poly_sun = []
            poly_core = []
            for k in range(8):
                ang = k * math.pi / 4.0
                dx = px * math.cos(ang)
                dy = py * math.cos(ang)
                dz = math.sin(ang)
                ps = (c_sun[0] + dx * r_sun, c_sun[1] + dy * r_sun, c_sun[2] + dz * r_sun)
                poly_sun.append(c.camera.apply(ps[0], ps[1], ps[2]))
                pc = (c_sun[0] + dx * r_core, pc_y := (c_sun[1] + dy * r_core), ps[2])
                poly_core.append(c.camera.apply(pc[0], pc_y, c_sun[2] + dz * r_core))
            pygame.draw.polygon(c.surface, P["sun"], poly_sun)
            pygame.draw.polygon(c.surface, P["sun_light"], poly_core)

    # 2. Cauda da bandana se estiver voltada para a câmera
    d_knot = mk.depth(c, bx - fx * 0.08, by - fy * 0.08)
    if d_knot >= d_torso:
        _headband_tails(c)

    # 3. Chapéu de Cowboy OU Óculos de visão noturna (NVG)
    has_cowboy_hat = extra.get("cowboy_hat", False) or pose in ("cowboy_banjo", "cowboy_victory", "hat_tip", "draw_banjo") or extra.get("intro_victory_state") == "VICTORY"
    if has_cowboy_hat:
        _draw_cowboy_hat(c)
    else:
        _draw_nvg(c)


def draw_front(c, arm_l, arm_r):
    """Camada frontal: armas desenham APENAS se as mãos estiverem na frente do tronco."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_l, hand_r = _hands(c)
    d_gear = max(mk.depth(c, hand_l[0], hand_l[1]), mk.depth(c, hand_r[0], hand_r[1]))
    if d_gear >= d_torso - 0.01:
        _draw_weapons(c, hand_l, hand_r)
