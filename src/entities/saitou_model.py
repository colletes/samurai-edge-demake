"""
Saitou Hajime, Capitão da 3ª Divisão do Shinsengumi (O Lobo de Mibu):
- Rosto severo e impassível com olhar marcial focado (Sanpaku eyes), sobrancelhas cerradas e lábios firmes.
- Cabelo negro com topete samurai clássico, mechas caídas sobre a testa e rabo-de-cavalo (chonmage) amarrado com laço branco.
- Haori azul-claro (Asagi-iro) autêntico com padrão em zigue-zague branco (Dandara) nas barras e mangas.
- Kanji 誠 (Makoto / Sinceridade) em branco bordado em relevo nas costas do haori.
- Cachimbo tradicional Kiseru estilizado em latão e bambu escuro com baforada de fumaça na intro e vitória.
- Hakama escura ampla com pregas em malha 3D contínua, caneleiras pretas (kyahan), meias tabi brancas e sandálias waraji.
- Mangas amplas de haori em fita 3D fluida drapeando para baixo.
- Katana longa em guarda mortal de Gatotsu (estocada horizontal na altura dos olhos) e bainha laqueada preta no quadril.
- Single-pass weapon rendering: quando a espada é empunhada, a bainha fica vazia sem cabo duplicado.
- Suporte a De/Para (legacy_mode) e biblioteca de materiais realistas.
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

PALETTE = {
    "haori": (134, 202, 226),
    "haori_dark": (92, 154, 186),
    "torso": (134, 202, 226),
    "zig": (244, 248, 252),
    "makoto": (248, 250, 254),
    "navy": (28, 36, 62),
    "navy_dark": (18, 24, 44),
    "pants": (32, 38, 68),
    "hakama_dark": (22, 26, 48),
    "belt": (238, 238, 244),
    "kyahan": (24, 24, 30),
    "tabi": (238, 238, 242),
    "sandal": (46, 40, 36),
    "strap": (210, 210, 220),
    "skin": (238, 204, 176),
    "skin_shadow": (206, 168, 140),
    "hair": (22, 22, 28),
    "hair_light": (42, 44, 54),
    "saya": (26, 28, 38),
    "gold": (214, 184, 96),
    "steel": (224, 234, 246),
    "edge": (252, 254, 255),
    "ito": (24, 26, 36),
    "aura": (150, 214, 255),
    "aura_core": (236, 250, 255),
    "kiseru_wood": (62, 40, 28),
    "kiseru_brass": (222, 186, 96),
    "smoke": (225, 230, 240),
}

LEGACY_MATERIALS = {
    "haori": "diffuse", "haori_dark": "diffuse", "navy": "diffuse",
    "pants": "diffuse", "saya": "diffuse", "steel": "diffuse"
}

MATERIALS = {
    "haori": "silk", "haori_dark": "silk", "navy": "silk",
    "belt": "silk", "kyahan": "leather", "saya": "lacquer",
    "strap": "canvas", "steel": "steel", "gold": "gold",
    "kiseru_brass": "gold", "kiseru_wood": "wood", "makoto": "silk"
}


def pal() -> dict:
    return PALETTE


def _smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _sheath(c):
    k = (c.base_x + c.px * 0.14 + c.fx * 0.03, c.base_y + c.py * 0.14 + c.fy * 0.03, c.pelvis_z + 0.07)
    b = mk.norm((-c.fx * 0.82 + c.px * 0.30, -c.fy * 0.82 + c.py * 0.30, -0.30))
    return k, b


def _is_blade_in_hand(c) -> bool:
    """Verifica se a katana está empunhada nas mãos (deixando a bainha vazia sem espada duplicada)."""
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    state = getattr(c, "state", "IDLE")

    if c.is_melee or state in ("GATOTSU_CHARGE", "ZEROSHIKI", "ATTACK", "BRAKING"):
        return True
    if pose in ("gatotsu_stance", "chiburi_flick", "gatotsu_lunge", "zeroshiki_blast"):
        return True
    if pose == "noto_sheath":
        prog = extra.get("noto_prog", extra.get("seg_u", 0.0))
        return prog < 0.85
    return False


def _draw_sheath(c):
    """Bainha (Saya) laqueada no quadril esquerdo; só desenha o cabo da espada se ela NÃO estiver na mão."""
    P = pal()
    k, b = _sheath(c)
    # Bainha laqueada escura (Saya)
    mk.obox(c, k, b, 0.50, 0.044, 0.044, P["saya"])
    # Boca da bainha (Koiguchi) dourada
    mk.obox(c, k, b, 0.030, 0.052, 0.052, P["gold"], outline=False)
    # Ponteira dourada (Kojiri)
    mk.obox(c, mk.add(k, b, 0.47), b, 0.030, 0.050, 0.050, P["gold"], outline=False)

    # Apenas renderiza o cabo na bainha se a espada estiver efetivamente embainhada!
    if not _is_blade_in_hand(c):
        h = (-b[0], -b[1], -b[2])
        mk.obox(c, k, h, 0.17, 0.040, 0.040, P["ito"])
        mk.obox(c, mk.add(k, b, -0.008), b, 0.016, 0.075, 0.075, P["gold"])


def _gatotsu_blade_dir(c):
    return mk.norm((c.fx * 0.95, c.fy * 0.95, -0.14 if not c.is_melee else -0.08))


def _draw_gatotsu_blade(c, hand):
    P = pal()
    d = _gatotsu_blade_dir(c)
    length = 0.78 if c.is_melee else 0.72
    mk.sword(c, mk.add(hand, d, -0.02), d, length, P["steel"], P["edge"], P["ito"], P["gold"], P["gold"], guard_w=0.070)

    # Zanzou / rastro de vácuo do Gatotsu em velocidade
    if c.is_melee and c.atk_progress is not None and c.atk_progress >= 0.25:
        for j in range(1, 5):
            p = c.atk_progress - 0.06 * j
            if p < 0.15:
                break
            ghost = mk.add(hand, d, -0.06 * j)
            fade = 1.0 - j / 5.0
            tip, mid = mk.add(ghost, d, length), mk.add(ghost, d, length * 0.45)
            side = (c.px * 0.030, c.py * 0.030, 0.0)
            mk.band(c, (mid, tip, mk.add(tip, side, 1.0), mk.add(mid, side, 1.0)), P["aura"] + (int(200 * fade),))


def _draw_kiseru(c, hand, smoking=False):
    """Cachimbo japonês tradicional (Kiseru) de latão dourado e bambu escuro com fumaça."""
    P = pal()
    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    d = mk.norm((fx * 0.80 - px * 0.40, fy * 0.80 - py * 0.40, 0.25))

    # Bocal de latão (Suikuchi)
    mk.obox(c, hand, d, 0.040, 0.016, 0.016, P["kiseru_brass"], outline=False)
    # Haste de bambu escuro (Rau)
    mid = mk.add(hand, d, 0.038)
    mk.obox(c, mid, d, 0.110, 0.014, 0.014, P["kiseru_wood"], outline=False)
    # Fornilho de latão na ponta (Gankubi)
    tip = mk.add(mid, d, 0.105)
    mk.obox(c, tip, d, 0.035, 0.022, 0.022, P["kiseru_brass"], outline=False)
    bowl_up = mk.norm((-fx * 0.20, -fy * 0.20, 0.95))
    mk.obox(c, tip, bowl_up, 0.038, 0.026, 0.026, P["kiseru_brass"], outline=False)

    # Baforada de fumaça cinzenta suave
    if smoking:
        smoke_pos = mk.add(tip, bowl_up, 0.045)
        for i in range(3):
            sw = 0.018 + i * 0.012
            mk.cbox(c, smoke_pos[0] + fx * (i * 0.015), smoke_pos[1] + fy * (i * 0.015), smoke_pos[2] + i * 0.025,
                    sw, sw, sw, P["smoke"], outline=False)


def _draw_makoto_emblem(c, center_pos):
    """Borda o lendário Kanji 誠 (Makoto / Sinceridade) em relevo branco nas costas do Haori."""
    P = pal()
    px, py = c.px, c.py
    cx, cy, cz = center_pos

    # Fundo do losango ou base do kanji em branco
    # 1. Traço vertical central
    mk.cbox(c, cx, cy, cz, 0.014, 0.014, 0.090, P["makoto"], outline=False)
    # 2. Barra horizontal superior
    mk.cbox(c, cx, cy, cz + 0.038, 0.080, 0.014, 0.014, P["makoto"], outline=False)
    # 3. Traços angulares laterais sugerindo o radical 言 (palavra/fala) e 成 (completar/tornar)
    mk.cbox(c, cx - px * 0.032, cy - py * 0.032, cz + 0.010, 0.038, 0.014, 0.012, P["makoto"], outline=False)
    mk.cbox(c, cx - px * 0.032, cy - py * 0.032, cz - 0.018, 0.042, 0.014, 0.012, P["makoto"], outline=False)
    mk.cbox(c, cx + px * 0.030, cy + py * 0.030, cz + 0.012, 0.048, 0.014, 0.012, P["makoto"], outline=False)
    mk.cbox(c, cx + px * 0.035, cy + py * 0.035, cz - 0.025, 0.052, 0.014, 0.014, P["makoto"], outline=False)


def _back_panel(c, P):
    anchor = (c.base_x - c.fx * 0.12, c.base_y - c.fy * 0.12, c.torso_z + 0.22)
    trail, amp, freq = mk.motion(c, 0.06)
    offs = mk.cloth_offsets(c, 3, 0.6, trail, amp * 1.5, freq, anchor)
    p1 = (anchor[0] + offs[0][0], anchor[1] + offs[0][1], anchor[2] - 0.12 + offs[0][2])
    p2 = (anchor[0] + offs[1][0], anchor[1] + offs[1][1], anchor[2] - 0.24 + offs[1][2])
    p3 = (anchor[0] + offs[2][0], anchor[1] + offs[2][1], anchor[2] - 0.36 + offs[2][2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[anchor, p1, p2, p3],
        widths=(0.26, 0.28, 0.30, 0.32),
        depth_thick=0.032,
        colors=(P["haori"], P["haori"], P["haori_dark"]),
        side_vec=(c.px, c.py, 0.0),
        normal_vec=(-c.fx, -c.fy, 0.0),
        outline=True,
        alpha=c.alpha,
    )

    # Kanji 誠 (Makoto) bordado em relevo no dorso do Haori
    makoto_pos = (anchor[0] - c.fx * 0.010, anchor[1] - c.fy * 0.010, anchor[2] - 0.06)
    _draw_makoto_emblem(c, makoto_pos)

    # Zigue-zague branco tradicional do Shinsengumi (Dandara) na barra inferior
    for i in range(5):
        lat = (i - 2) * 0.055
        mk.cbox(c, p3[0] + c.px * lat, p3[1] + c.py * lat, p3[2] - 0.015, 0.034, 0.028, 0.040, P["zig"], outline=False)


def idle_arms(c):
    """Guarda firme e austera do Shinsengumi: mão esquerda na empunhadura e mão direita relaxada."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    bob = math.sin(c.walk_timer * 3.0) * 0.008
    left = (bx + fx * 0.24 + px * 0.08, by + fy * 0.24 + py * 0.08, tz + 0.14 + bob)
    right = (bx + fx * 0.10 - px * 0.16, by + fy * 0.10 - py * 0.16, tz + 0.06 + bob)
    return left, right


def _hands(c):
    """Cinemática articular dinâmica e poses de ação com LERP contínuo para Saitou."""
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    p = extra.get("p", getattr(c, "atk_progress", 0.0) or 0.0)
    bx, by, tz, hz = c.base_x, c.base_y, c.torso_z, c.head_z
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # 1. Coreografia Contínua de Intro: Kiseru -> Destravar Koiguchi -> Postura Gatotsu
    if pose in ("kiseru_smoke", "koiguchi_unlock", "gatotsu_stance") or getattr(c, "state", "") == "INTRO":
        intro_p = getattr(c, "atk_progress", 0.0) or extra.get("seg_u", p) or p
        # Fase 1: Traga solene do Kiseru com a mão direita
        if intro_p < 0.38:
            u = _smooth(intro_p / 0.38)
            # Mão direita segura o Kiseru próximo à boca
            right = (bx + fx * (0.12 + u * 0.02) - px * 0.04, by + fy * (0.12 + u * 0.02) - py * 0.04, hz + 0.02 + math.sin(u * math.pi) * 0.015)
            # Mão esquerda repousa na cintura sobre a bainha
            left = (bx + fx * 0.06 + px * 0.16, by + fy * 0.06 + py * 0.16, tz + 0.08)
            return left, right

        # Fase 2: Guarda o Kiseru e destrava a tsuba com o polegar (Koiguchi-kiri)
        elif intro_p < 0.70:
            u = _smooth((intro_p - 0.38) / 0.32)
            # Mão direita desce para empunhar o cabo da katana
            target_r = (bx + fx * 0.16 + px * 0.08, by + fy * 0.16 + py * 0.08, tz + 0.14)
            start_r = (bx + fx * 0.14 - px * 0.04, by + fy * 0.14 - py * 0.04, hz + 0.02)
            # Mão esquerda sobe firme destravando o koiguchi
            left = (bx + fx * 0.18 + px * 0.12, by + fy * 0.18 + py * 0.12, tz + 0.16)
            return left, mk.lerp(start_r, target_r, u)

        # Fase 3: Transição estonteante para a postura horizontal definitiva do Gatotsu
        else:
            u = _smooth((intro_p - 0.70) / 0.30)
            start_l = (bx + fx * 0.18 + px * 0.12, by + fy * 0.18 + py * 0.12, tz + 0.16)
            start_r = (bx + fx * 0.16 + px * 0.08, by + fy * 0.16 + py * 0.08, tz + 0.14)
            # Gatotsu: mão esquerda estende a lâmina paralela aos olhos; mão direita apoia
            target_l = (bx + fx * 0.36, by + fy * 0.36, tz + 0.18)
            target_r = (bx + fx * 0.20 - px * 0.08, by + fy * 0.20 - py * 0.08, tz + 0.16)
            return mk.lerp(start_l, target_l, u), mk.lerp(start_r, target_r, u)

    # 2. Coreografia Contínua de Vitória: Chiburi -> Noto -> Acende Kiseru
    if pose in ("chiburi_flick", "noto_sheath", "kiseru_light") or getattr(c, "state", "") == "VICTORY":
        vic_p = getattr(c, "atk_progress", 0.0) or extra.get("seg_u", p) or p
        # Fase 1: Chiburi marcial (giro seco lateral para sacudir o sangue)
        if vic_p < 0.35:
            u = _smooth(vic_p / 0.35)
            flick_angle = math.sin(u * math.pi) * 0.30
            left = (bx + fx * 0.24 - px * (0.10 + flick_angle), by + fy * 0.24 - py * (0.10 + flick_angle), tz + 0.12 - u * 0.04)
            right = (bx + fx * 0.12 - px * 0.14, by + fy * 0.12 - py * 0.14, tz + 0.08)
            return left, right

        # Fase 2: Noto ceremonial (embainhamento fluido na saya sem olhar)
        elif vic_p < 0.70:
            u = _smooth((vic_p - 0.35) / 0.35)
            # Mão esquerda traz a lâmina de volta em direção ao koiguchi na cintura
            k, b = _sheath(c)
            koiguchi_pos = (k[0] + fx * 0.02, k[1] + fy * 0.02, k[2] + 0.02)
            start_l = (bx + fx * 0.24 - px * 0.10, by + fy * 0.24 - py * 0.10, tz + 0.08)
            left = mk.lerp(start_l, koiguchi_pos, u)
            right = (bx + fx * 0.12 - px * 0.14, by + fy * 0.12 - py * 0.14, tz + 0.08)
            return left, right

        # Fase 3: Pega o Kiseru e o contempla solenemente
        else:
            u = _smooth((vic_p - 0.70) / 0.30)
            k, b = _sheath(c)
            left = (k[0], k[1], k[2] + 0.02)
            # Mão direita leva o Kiseru aos lábios
            target_r = (bx + fx * 0.14 - px * 0.04, by + fy * 0.14 - py * 0.04, hz + 0.02)
            start_r = (bx + fx * 0.12 - px * 0.14, by + fy * 0.12 - py * 0.14, tz + 0.08)
            return left, mk.lerp(start_r, target_r, u)

    # 3. Ataque Primário: Gatotsu Lunge (Estocada Crescente)
    if pose == "gatotsu_lunge" or getattr(c, "state", "") == "GATOTSU_CHARGE":
        u = _smooth(p)
        reach = 0.28 + u * 0.22
        left = (bx + fx * (0.34 + reach), by + fy * (0.34 + reach), tz + 0.18)
        right = (bx + fx * 0.18 - px * 0.08, by + fy * 0.18 - py * 0.08, tz + 0.15)
        return left, right

    # 4. Ataque Secundário: Gatotsu Zeroshiki (Disparo à Queima-Roupa)
    if pose == "zeroshiki_blast" or getattr(c, "state", "") == "ZEROSHIKI":
        burst = math.sin(p * math.pi) * 0.40
        left = (bx + fx * (0.42 + burst), by + fy * (0.42 + burst), tz + 0.19)
        right = (bx + fx * 0.20 - px * 0.10, by + fy * 0.20 - py * 0.10, tz + 0.16)
        return left, right

    # 5. Haori Sidestep (Esquiva 3ª Ação)
    if pose == "haori_sidestep" or getattr(c, "state", "") == "ROLL":
        u = math.sin(p * math.pi)
        left = (bx + fx * 0.20 - px * (0.12 + u * 0.10), by + fy * 0.20 - py * (0.12 + u * 0.10), tz + 0.10)
        right = (bx + fx * 0.14 + px * (0.12 + u * 0.08), by + fy * 0.14 + py * (0.12 + u * 0.08), tz + 0.12)
        return left, right

    # Padrão de combate
    return idle_arms(c)


def get_arms(c):
    """Exposição modular da cinemática dos braços para sincronização com o renderizador de humanoides."""
    return _hands(c)


def draw_behind(c):
    """Camada traseira com ordenação dinâmica de profundidade 3D."""
    P = pal()
    d_torso = mk.depth(c, c.base_x, c.base_y)
    k, b = _sheath(c)
    if mk.depth(c, k[0] + b[0] * 0.25, k[1] + b[1] * 0.25) < d_torso:
        _draw_sheath(c)

    d_back = mk.depth(c, c.base_x - c.fx * 0.10, c.base_y - c.fy * 0.10)
    if d_back <= d_torso + 0.02:
        _back_panel(c, P)

    # Katana em draw_behind se as mãos estiverem atrás do torso
    if _is_blade_in_hand(c):
        hand_l, hand_r = _hands(c)
        if mk.depth(c, hand_l[0], hand_l[1]) < d_torso:
            _draw_gatotsu_blade(c, hand_l)

    # Kiseru se estiver sendo fumado e atrás do torso
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    if pose in ("kiseru_smoke", "kiseru_light") or (getattr(c, "state", "") == "INTRO" and getattr(c, "atk_progress", 0.0) < 0.38):
        hand_l, hand_r = _hands(c)
        if mk.depth(c, hand_r[0], hand_r[1]) < d_torso:
            _draw_kiseru(c, hand_r, smoking=True)


def draw_legs(c):
    """Hakama larga e escura em malha 3D contínua, caneleira preta, tabi branco e sandália waraji."""
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

        # Hakama azul-escura com pregas volumosas em malha contínua 3D
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, cuff_pos],
            widths=[0.130, 0.118, 0.095],
            depth_thick=0.092,
            colors=[P["pants"], P["hakama_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Caneleira preta protetora (Kyahan)
        mk.obox(c, cuff_pos, (c.fx, c.fy, 0.0), 0.065, 0.102, 0.095, P["kyahan"], up=(0.0, 0.0, 1.0))

        # Meias Tabi brancas até o tornozelo
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[cuff_pos, ankle],
            widths=[0.085, 0.075],
            depth_thick=0.078,
            colors=[P["tabi"], P["tabi"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Pé com sandália Waraji e sola
        flen, fwidth = 0.13, 0.066
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.016, flen, fwidth, 0.034, P["tabi"], outline=True)
        mk.cbox(c, foot[0] + c.fx * (flen * 0.25), foot[1] + c.fy * (flen * 0.25), foot[2] + 0.003, flen + 0.004, fwidth + 0.004, 0.010, P["sandal"], outline=False)
        mk.cbox(c, foot[0] + c.fx * (flen * 0.35), foot[1] + c.fy * (flen * 0.35), foot[2] + 0.018, 0.024, 0.024, 0.012, P["strap"], outline=False)


def draw_obi(c):
    """Faixa branca de seda com nó lateral esvoaçante."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.065
    mk.cbox(c, bx, by, z, c.pelvis_w - 0.008, c.pelvis_w * 0.74, 0.080, P["belt"])
    kx, ky = bx + fx * 0.10 - px * 0.04, by + fy * 0.10 - py * 0.04
    mk.cbox(c, kx, ky, z + 0.010, 0.070, 0.040, 0.060, P["belt"])
    trail, amp, freq = mk.motion(c, 0.05)
    offs = mk.cloth_offsets(c, 2, 0.9, trail, amp * 1.4, freq, (kx, ky))
    for i, o in enumerate(offs):
        mk.cbox(c, kx + o[0], ky + o[1], z - 0.060 * (i + 1) + o[2], 0.034, 0.024, 0.066, P["belt"], outline=False)


def draw_torso(c):
    """Quimono azul-marinho com colarinho branco e abas frontais do haori com padrão Dandara."""
    P = pal()
    tz, bx, by, fx, fy, px, py = c.torso_z, c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    front = 0.110

    if mk.depth(c, fx, fy) > -0.05:
        # Quimono azul-marinho interno
        mk.obox(c, (bx + fx * (front - 0.008), by + fy * (front - 0.008), tz + 0.02), (0.0, 0.0, 1.0), 0.240, 0.110, 0.020, P["navy"], up=(fx, fy, 0.0), outline=False)
        # Colarinho branco (Juban)
        apex = (bx + fx * (front + 0.004), by + fy * (front + 0.004), tz + 0.10)
        for s in (-1.0, 1.0):
            top = (bx + fx * front + px * 0.065 * s, by + fy * front + py * 0.065 * s, tz + 0.265)
            mk.limb(c, top, apex, 0.034, P["strap"], outline=False, height=0.018)
        mk.cbox(c, bx + fx * front, by + fy * front, tz + 0.20, 0.040, 0.018, 0.060, P["skin"], outline=False)

        # Abas frontais do haori azul-turquesa
        for s in (-1.0, 1.0):
            anchor = (bx + fx * 0.120 + px * 0.130 * s, by + fy * 0.120 + py * 0.130 * s, tz + 0.20)
            last = mk.panels(c, anchor, 3, 0.10, 0.075, 0.022, (P["haori"], P["haori"], P["haori_dark"]), phase=0.9 * s, up=(fx, fy, 0.0), flare=0.006)
            for i in range(2):
                lat = (i - 0.5) * 0.040
                mk.cbox(c, last[0] + px * lat, last[1] + py * lat, last[2] - 0.015, 0.030, 0.026, 0.035, P["zig"], outline=False)

    if mk.depth(c, -fx, -fy) > -0.05:
        _back_panel(c, P)


def draw_arm(c, shoulder, hand, side):
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], bracer=P["kyahan"], bracer_span=(0.35, 0.95), w=0.058)


def draw_sleeves(c, arms):
    """Mangas amplas do haori em fita contínua 3D drapeando para baixo com padrão Dandara."""
    P = pal()
    trail, amp, freq = mk.motion(c, 0.07)
    atk = math.sin(c.atk_progress * math.pi) if c.is_melee and c.atk_progress is not None else 0.0
    for k, (s, e, side) in enumerate(arms):
        anchor = (s[0] + c.px * side * 0.040, s[1] + c.py * side * 0.040, s[2] - 0.010)
        drag = (-c.fx * 0.10 * atk, -c.fy * 0.10 * atk)
        offs = cloth.chain_offsets(2, c.walk_timer, 1.7 * k, drag, (c.px, c.py), amp=amp * 1.5, freq=freq, wind=cloth.wind_at(anchor[0], anchor[1]))

        mid = (anchor[0] + offs[0][0] + c.px * side * 0.015, anchor[1] + offs[0][1] + c.py * side * 0.015, anchor[2] - 0.100 + offs[0][2])
        hem = (anchor[0] + offs[1][0] + c.px * side * 0.025, anchor[1] + offs[1][1] + c.py * side * 0.025, anchor[2] - 0.200 + offs[1][2])

        spine_pts = [anchor, mid, hem]
        widths = (0.10, 0.13, 0.16)
        colors = (P["haori"], P["haori_dark"])
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=spine_pts,
            widths=widths,
            depth_thick=0.046,
            colors=colors,
            side_vec=(c.fx, c.fy, 0.0),
            normal_vec=(c.px * side, c.py * side, 0.0),
            outline=True,
            alpha=c.alpha,
        )
        # Pontas brancas em zigue-zague na barra da manga (Dandara)
        for i in range(3):
            lat = (i - 1) * 0.045
            mk.obox(c, (hem[0] + c.fx * lat, hem[1] + c.fy * lat, hem[2] - 0.005), (0.0, 0.0, -1.0), 0.025, 0.030, 0.035, P["zig"], up=(c.fx, c.fy, 0.0), outline=False)


def draw_head(c):
    """
    Cabeça de Saitou:
    - Olhar marcial afiado (Sanpaku eyes), sobrancelhas cerradas e lábios impassíveis.
    - Topete samurai esculpido ajustado ao crânio com mechas caídas na fronte.
    - Costeletas marcadas descendo pelas têmporas.
    - Rabo de cavalo samurai (Chonmage) com laço branco.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py
    hw = c.head_w
    d_torso = mk.depth(c, bx, by)

    # Costeletas e mechas laterais rente às têmporas
    for s in (-1.0, 1.0):
        lx = bx + fx * 0.015 + px * 0.065 * s
        ly = by + fy * 0.015 + py * 0.065 * s
        if mk.depth(c, lx, ly) >= d_torso - 0.01:
            p0 = (lx, ly, hz + 0.125)
            p1 = (lx + fx * 0.010, ly + fy * 0.010, hz + 0.065)
            p2 = (lx + fx * 0.012, ly + fy * 0.012, hz + 0.020)
            draw_ribbon_mesh_3d(
                c.surface, c.camera,
                spine_points=[p0, p1, p2],
                widths=[0.024, 0.020, 0.012],
                depth_thick=0.012,
                colors=[P["hair"], P["hair"]],
                side_vec=(px * s, py * s, 0.0),
                normal_vec=(fx, fy, 0.0),
                outline=False,
                alpha=c.alpha,
            )

    # Mechas frontais caídas sobre a testa (estilo lobo solitário impassível)
    if mk.depth(c, fx, fy) > 0.0:
        for s in (-0.03, 0.02):
            f_top = (bx + fx * 0.075 + px * s, by + fy * 0.075 + py * s, hz + 0.140)
            f_mid = (bx + fx * 0.082 + px * (s + 0.01), by + fy * 0.082 + py * (s + 0.01), hz + 0.100)
            f_tip = (bx + fx * 0.080 + px * (s + 0.015), by + fy * 0.080 + py * (s + 0.015), hz + 0.070)
            draw_ribbon_mesh_3d(
                c.surface, c.camera,
                spine_points=[f_top, f_mid, f_tip],
                widths=[0.018, 0.014, 0.008],
                depth_thick=0.008,
                colors=[P["hair"], P["hair"]],
                side_vec=(px, py, 0.0),
                normal_vec=(fx, fy, 0.0),
                outline=False,
                alpha=c.alpha,
            )

    # Topete samurai clássico no topo da cabeça
    cran_top = (bx - fx * 0.005, by - fy * 0.005, hz + 0.165)
    draw_tapered_frustum_3d(
        c.surface, c.camera,
        (bx, by, hz + 0.140), cran_top,
        w_start=hw * 0.95, h_start=hw * 0.95,
        w_end=hw * 0.72, h_end=hw * 0.72,
        color=P["hair"],
        up=(fx, fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Rabo de cavalo samurai (Chonmage) amarrado com laço branco atrás
    knot_pos = (bx - fx * 0.040, by - fy * 0.040, hz + 0.165)
    mk.obox(c, knot_pos, (0.0, 0.0, 1.0), 0.015, 0.024, 0.024, P["belt"], up=(fx, fy, 0.0), outline=False)

    trail, amp, freq = mk.motion(c, 0.06)
    o = mk.cloth_offsets(c, 1, 0.8, trail, amp * 1.5, freq, knot_pos)[0]
    p_tail1 = (knot_pos[0] - fx * 0.040 + o[0] * 0.5, knot_pos[1] - fy * 0.040 + o[1] * 0.5, hz + 0.170 + o[2] * 0.5)
    p_tail2 = (knot_pos[0] - fx * 0.090 + o[0], knot_pos[1] - fy * 0.090 + o[1], hz + 0.120 + o[2])

    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=[knot_pos, p_tail1, p_tail2],
        widths=[0.026, 0.028, 0.018],
        depth_thick=0.018,
        colors=[P["hair"], P["hair"]],
        side_vec=(px, py, 0.0),
        normal_vec=(0.0, 0.0, 1.0),
        outline=False,
        alpha=c.alpha,
    )


def draw_front(c, arm_l, arm_r):
    """Camada frontal: Bainha voltada para a frente, Katana e Kiseru."""
    P = pal()
    d_torso = mk.depth(c, c.base_x, c.base_y)
    k, b = _sheath(c)
    if mk.depth(c, k[0] + b[0] * 0.25, k[1] + b[1] * 0.25) >= d_torso:
        _draw_sheath(c)

    hand_l, hand_r = _hands(c)

    # Katana em draw_front se a mão esquerda estiver à frente do torso
    if _is_blade_in_hand(c):
        if mk.depth(c, hand_l[0], hand_l[1]) >= d_torso:
            _draw_gatotsu_blade(c, hand_l)

    # Kiseru se estiver sendo fumado e à frente do torso
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    if pose in ("kiseru_smoke", "kiseru_light") or (getattr(c, "state", "") == "INTRO" and getattr(c, "atk_progress", 0.0) < 0.38):
        if mk.depth(c, hand_r[0], hand_r[1]) >= d_torso:
            _draw_kiseru(c, hand_r, smoking=True)
