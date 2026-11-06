"""
Teppo, o arcabuzeiro Tanegashima & Mestre de Artilharia (Fase 2 Overhaul — Sub-fase 2.6):
- Jingasa cônica 3D facetada em 8 planos com laca Urushi e brasão dourado Tonbo (libélula da vitória).
- Rosto de veterano esculpido em 3D Tekken 2/3 com olhar determinado, olho direito mirando na alça de mira,
  nariz estruturado, bigode tradicional em blocos 3D e fuligem autêntica de pólvora na bochecha.
- Armadura Ashigaru feudal: hitatare verde-oliva com colarinho branco interno, couraça Dō de ferro fundido com rebites de aço.
- Ombreiras segmentadas em placas laqueadas (sode) com cordões dourados.
- Bandoleira de couro com 6 tubos rápidos de bambu (hayago) e chifre de pólvora negra (kayakutsubo).
- Calças largas kukuri-bakama contínuas sem degraus nos joelhos, presas em caneleiras de ferro (suneate) e sandálias waraji.
- Arcabuz feudal Tanegashima de coronha de cerejeira/carvalho polido, cano longo octogonal de ferro com anéis de latão e mecha fumegante.
- Cinemática completa: Mira precisa, coronhada de carvalho, recarga com vareta de ferro (ramrod),
  Intro (sopro na brasa da mecha), Vitória (cachimbo Kiseru fumegante e fuzil no ombro) e Finishers duplos.
- Suporte a Modo Comparativo De / Para (legacy_mode) e SSAA 2x Offscreen.
"""
import math
import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.mesh_primitives import (
    draw_ribbon_mesh_3d,
    draw_tapered_frustum_3d,
    _clamp_color,
    draw_portrait_face_3d,
)

PALETTE = {
    "hitatare": (68, 82, 54), "hitatare_dark": (46, 56, 36), "hitatare_light": (92, 110, 74),
    "collar_white": (235, 235, 238),
    "cuirass": (42, 46, 48), "cuirass_dark": (26, 28, 30), "cuirass_light": (78, 84, 90),
    "rivet": (180, 185, 192), "sode": (48, 52, 54), "sode_lace": (142, 118, 72),
    "jingasa": (26, 26, 28), "jingasa_rim": (48, 48, 54), "jingasa_light": (64, 64, 72),
    "gold": (224, 185, 68), "strap": (225, 215, 195),
    "skin": (222, 180, 142), "skin_shadow": (186, 142, 108),
    "hair": (28, 26, 24), "neck": (68, 82, 54),
    "wood": (128, 74, 38), "wood_dark": (88, 48, 24),
    "barrel": (62, 66, 74), "barrel_light": (135, 140, 150), "brass": (210, 172, 64),
    "ember": (255, 145, 40), "smoke": (215, 215, 220),
    "horn": (210, 185, 130), "hayago": (185, 155, 95), "bandolier": (74, 48, 28),
    "belt": (54, 44, 34), "scabbard": (32, 28, 30),
    "hakama": (72, 78, 58), "hakama_dark": (48, 52, 38),
    "suneate": (44, 46, 50), "tabi": (48, 46, 42), "waraji": (180, 150, 95),
    "cord": (195, 170, 120), "ramrod": (175, 180, 188),
    "kiseru_wood": (62, 40, 28), "kiseru_brass": (222, 186, 96),
    "soot": (38, 34, 32),
}

LEGACY_MATERIALS = {
    "cuirass": "diffuse", "cuirass_dark": "diffuse", "sode": "diffuse",
    "jingasa": "diffuse", "barrel": "diffuse", "wood": "diffuse",
    "hakama": "diffuse", "hitatare": "diffuse",
}

MATERIALS = {
    "cuirass": "metal", "cuirass_dark": "metal", "sode": "metal", "jingasa": "lacquer",
    "barrel": "metal", "barrel_light": "chrome", "brass": "gold", "gold": "gold",
    "wood": "planks", "wood_dark": "planks", "horn": "lacquer", "bandolier": "leather",
    "belt": "leather", "hakama": "canvas", "hitatare": "cloth", "suneate": "metal",
    "kiseru_brass": "gold", "kiseru_wood": "wood", "ramrod": "metal",
}


def pal() -> dict:
    return PALETTE


def _smooth(x: float) -> float:
    x = max(0.0, min(1.0, float(x)))
    return x * x * (3.0 - 2.0 * x)


def idle_arms(c):
    """Empunhadura clássica de infantaria: guarda baixa diagonal cruzando o peito."""
    bx, by, tz, fx, fy, px, py = c.base_x, c.base_y, c.torso_z, c.fx, c.fy, c.px, c.py
    sway = math.sin(c.walk_timer * (6.0 if c.is_moving else 2.0)) * (0.02 if c.is_moving else 0.008)
    hand_r = (bx + fx * 0.14 - px * 0.08, by + fy * 0.14 - py * 0.08, tz + 0.12 + sway)
    hand_l = (bx + fx * 0.32 + px * 0.06, by + fy * 0.32 + py * 0.06, tz + 0.10 - sway)
    return hand_l, hand_r


def _hands(c):
    """
    Cinemática articular dinâmica e poses de ação com interpolação contínua para Teppo:
    - Mira e disparo com recuo balístico.
    - Coronhada pesada de carvalho (Rifle Butt Smash).
    - Recarga rústica por vareta de ferro (Ramrod pump).
    - Mergulho de trincheira e rolamento (Trench Dive).
    - Intro em 3 fases: sopro na mecha -> inspeção de fecho -> pontaria.
    - Vitória em 3 fases: fuzil no ombro -> acendimento do Kiseru -> baforada relaxada.
    """
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    p = extra.get("p", getattr(c, "atk_progress", 0.0) or 0.0)
    state = getattr(c, "state", "IDLE")
    bx, by, tz, hz = c.base_x, c.base_y, c.torso_z, c.head_z
    fx, fy, px, py = c.fx, c.fy, c.px, c.py

    # 1. COREOGRAFIA DE INTRO (3 Fases Contínuas)
    if pose in ("match_blow", "lock_check", "ready_aim") or state == "INTRO":
        glo_p = float(extra.get("p", p if p is not None else 0.5))
        # Fase 1 (0.0 a 0.38): Sopro solene na mecha acesa
        if pose == "match_blow" or (not pose and glo_p < 0.38):
            u = _smooth(float(extra.get("seg_u", (glo_p / 0.38) if glo_p < 0.38 else 1.0)))
            left = (bx + fx * 0.12 + px * 0.14, by + fy * 0.12 + py * 0.14, tz + 0.08)
            blow_lift = math.sin(u * math.pi) * 0.03
            right = (bx + fx * (0.13 + u * 0.02) - px * 0.03, by + fy * (0.13 + u * 0.02) - py * 0.03, hz + 0.02 + blow_lift)
            return left, right

        # Fase 2 (0.38 a 0.70): Ajuste e encaixe da mecha na serpentina (hibasami)
        elif pose == "lock_check" or (not pose and glo_p < 0.70):
            u = _smooth(float(extra.get("seg_u", ((glo_p - 0.38) / 0.32) if glo_p < 0.70 else 1.0)))
            left = (bx + fx * 0.22 + px * 0.08, by + fy * 0.22 + py * 0.08, tz + 0.14)
            start_r = (bx + fx * 0.13 - px * 0.03, by + fy * 0.13 - py * 0.03, hz + 0.02)
            target_r = (bx + fx * 0.16 - px * 0.06, by + fy * 0.16 - py * 0.06, tz + 0.16)
            return left, mk.lerp(start_r, target_r, u)

        # Fase 3 (0.70 a 1.0): Empunha o arcabuz em guarda firme e mira resoluta à frente (100% Animado)
        else:
            u = _smooth(float(extra.get("seg_u", ((glo_p - 0.70) / 0.30))))
            start_l = (bx + fx * 0.22 + px * 0.08, by + fy * 0.22 + py * 0.08, tz + 0.14)
            start_r = (bx + fx * 0.16 - px * 0.06, by + fy * 0.16 - py * 0.06, tz + 0.16)
            aim_l = (bx + fx * 0.38 + px * 0.04, by + fy * 0.38 + py * 0.04, tz + 0.22)
            aim_r = (bx + fx * 0.16 - px * 0.06, by + fy * 0.16 - py * 0.06, tz + 0.24)
            cur_l = mk.lerp(start_l, aim_l, u)
            cur_r = mk.lerp(start_r, aim_r, u)
            aim_sway = math.sin((glo_p * 12.0) + c.walk_timer * 2.0) * 0.008
            breathe = math.cos((glo_p * 8.0)) * 0.010
            return (cur_l[0], cur_l[1], cur_l[2] + breathe), (cur_r[0] + aim_sway, cur_r[1] + aim_sway, cur_r[2] + breathe)

    # 2. COREOGRAFIA DE VITÓRIA (3 Fases Contínuas - 100% Animado)
    if pose in ("shoulder_rest", "kiseru_light", "kiseru_puff") or state == "VICTORY":
        glo_p = float(extra.get("p", p if p is not None else 0.5))
        # Fase 1 (0.0 a 0.35): Apoia o arcabuz fumegante no ombro esquerdo
        if pose == "shoulder_rest" or (not pose and glo_p < 0.35):
            u = _smooth(float(extra.get("seg_u", (glo_p / 0.35) if glo_p < 0.35 else 1.0)))
            left = (bx - px * 0.06 + fx * 0.04, by - py * 0.06 + fy * 0.04, tz + 0.20 + u * 0.06)
            right = (bx + fx * 0.12 - px * 0.12, by + fy * 0.12 - py * 0.12, tz + 0.08)
            return left, right

        # Fase 2 (0.35 a 0.68): Saca o Kiseru e acende o fornilho na ponta da mecha
        elif pose == "kiseru_light" or (not pose and glo_p < 0.68):
            u = _smooth(float(extra.get("seg_u", ((glo_p - 0.35) / 0.33) if glo_p < 0.68 else 1.0)))
            left = (bx - px * 0.06 + fx * 0.04, by - py * 0.06 + fy * 0.04, tz + 0.26)
            start_r = (bx + fx * 0.12 - px * 0.12, by + fy * 0.12 - py * 0.12, tz + 0.08)
            pipe_pos = (bx + fx * 0.13 - px * 0.04, by + fy * 0.13 - py * 0.04, hz + 0.02)
            return left, mk.lerp(start_r, pipe_pos, u)

        # Fase 3 (0.68 a 1.0): Baforada solene e risada rouca de veterano Ashigaru (100% Animado)
        else:
            u = _smooth(float(extra.get("seg_u", ((glo_p - 0.68) / 0.32))))
            left_pos = (bx - px * 0.06 + fx * 0.04, by - py * 0.06 + fy * 0.04, tz + 0.26)
            pipe_light_r = (bx + fx * 0.13 - px * 0.04, by + fy * 0.13 - py * 0.04, hz + 0.02)
            pipe_lips_r = (bx + fx * 0.14 - px * 0.02, by + fy * 0.14 - py * 0.02, hz + 0.03)
            base_r = mk.lerp(pipe_light_r, pipe_lips_r, u)
            puff = math.sin((glo_p * 20.0)) * 0.014
            laugh = math.sin((glo_p * 14.0) + c.walk_timer * 3.0) * 0.010
            return (left_pos[0], left_pos[1], left_pos[2] + laugh * 0.6), (base_r[0], base_r[1] + laugh, base_r[2] + puff)

    # 3. RECARGA TÁTICA POR VARETA (Ramrod Reload / Trench Recovery)
    if pose == "ramrod_reload" or extra.get("is_reloading", False):
        u = _smooth(p)
        pump = math.sin(u * math.pi * 3.0) * 0.10  # 3 bombadas de socar pólvora
        # Mão esquerda sustenta o arcabuz verticalmente
        left = (bx + fx * 0.22 + px * 0.06, by + fy * 0.22 + py * 0.06, tz + 0.12)
        # Mão direita segura a vareta de ferro entrando na boca do cano
        right = (bx + fx * 0.22 - px * 0.02, by + fy * 0.22 - py * 0.02, tz + 0.34 + pump)
        return left, right

    # 4. CORONHADA PESADA DE CARVALHO (Rifle Butt Smash)
    if pose == "rifle_butt" or (state == "ATTACK" and extra.get("is_rifle_butt", False)):
        u = _smooth(p)
        swing = math.sin(u * math.pi) * 0.28
        # Ambos os braços avançam num golpe rotacional com a coronha
        hand_r = (bx + fx * (0.24 + swing) - px * 0.10, by + fy * (0.24 + swing) - py * 0.10, tz + 0.22 + swing * 0.3)
        hand_l = (bx + fx * (0.16 + swing * 0.5) + px * 0.08, by + fy * (0.16 + swing * 0.5) + py * 0.08, tz + 0.18)
        return hand_l, hand_r

    # 5. MIRA E DISPARO DE ARCABUZ COM RECUO
    if state in ("RIFLE_AIM", "ATTACK") or pose in ("aim_shoot", "finisher_headshot"):
        t = _smooth(p)
        recoil = math.sin(t * math.pi) * 0.08 if state == "ATTACK" else 0.0
        aim_z = 0.24 + recoil * 0.5
        hand_r = (bx + fx * (0.16 - recoil) - px * 0.06, by + fy * (0.16 - recoil) - py * 0.06, tz + aim_z)
        hand_l = (bx + fx * (0.38 - recoil) + px * 0.05, by + fy * (0.38 - recoil) + py * 0.05, tz + aim_z - 0.02)
        return hand_l, hand_r

    # 6. PLANTANDO ARMADILHA DE PÓLVORA (Ground Trap)
    if pose == "plant_trap" or extra.get("is_planting_trap", False):
        u = _smooth(p)
        # Teppo agacha brevemente e deposita o canister com a mão direita
        hand_r = (bx + fx * 0.16 - px * 0.04, by + fy * 0.16 - py * 0.04, tz - 0.08 + (1.0 - u) * 0.10)
        hand_l = (bx + fx * 0.12 + px * 0.12, by + fy * 0.12 + py * 0.12, tz + 0.10)
        return hand_l, hand_r

    # 7. MERGULHO DE TRINCHEIRA (Trench Ashigaru Dive / Roll)
    if state in ("RIFLE_ROLL", "ROLL") or pose == "trench_dive":
        prog = extra.get("roll_prog", p)
        tuck = math.sin(prog * math.pi)
        # Braços dinamicamente encolhidos protegendo o fuzil colado ao peito durante o giro 360°
        hand_r = (bx + fx * (0.10 + tuck * 0.05) - px * 0.05, by + fy * (0.10 + tuck * 0.05) - py * 0.05, tz + 0.08 - tuck * 0.05)
        hand_l = (bx + fx * (0.18 + tuck * 0.04) + px * 0.07, by + fy * (0.18 + tuck * 0.04) + py * 0.07, tz + 0.10 - tuck * 0.04)
        return hand_l, hand_r

    # Padrão de combate em guarda
    return idle_arms(c)


def get_arms(c):
    """Exposição modular da cinemática dos braços para sincronização com o renderizador humanoide."""
    return _hands(c)


def _draw_jingasa(c):
    """Jingasa cônica 3D facetada em 8 planos com laca Urushi, crista Tonbo e jugular de algodão."""
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    apex_z = hz + 0.245
    brim_z = hz + 0.135
    radius = 0.205
    apex = (bx - fx * 0.010, by - fy * 0.010, apex_z)

    # 8 vértices no contorno do bordo
    num_pts = 8
    brim_pts = []
    for i in range(num_pts):
        ang = (i / num_pts) * math.pi * 2.0
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        pt = (bx + (fx * cos_a + px * sin_a) * radius,
              by + (fy * cos_a + py * sin_a) * radius,
              brim_z)
        brim_pts.append(pt)

    scr_apex = c.camera.apply(apex[0], apex[1], apex[2])
    scr_brim = [c.camera.apply(p[0], p[1], p[2]) for p in brim_pts]

    # Ordenação das 8 facetas cônicas por profundidade
    azimuth = getattr(c.camera, "azimuth", 0.0)
    facets = []
    for i in range(num_pts):
        p1 = brim_pts[i]
        p2 = brim_pts[(i + 1) % num_pts]
        mid_x = (p1[0] + p2[0] + apex[0]) / 3.0
        mid_y = (p1[1] + p2[1] + apex[1]) / 3.0
        mid_z = (p1[2] + p2[2] + apex[2]) / 3.0
        rx, ry = mk.rotate_xy(mid_x, mid_y, azimuth)
        d = rx + ry + mid_z * 0.35

        # Normal da faceta para iluminação direcional
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        vz = p2[2] - p1[2]
        wx = apex[0] - p1[0]
        wy = apex[1] - p1[1]
        wz = apex[2] - p1[2]
        nx = vy * wz - vz * wy
        ny = vz * wx - vx * wz
        nz = vx * wy - vy * wx
        nlen = math.hypot(nx, math.hypot(ny, nz))
        dot = (nx * 0.45 + ny * -0.55 + nz * 0.70) / (nlen if nlen > 1e-4 else 1.0)
        col_facet = _clamp_color(P["jingasa"], 0.72 + 0.40 * max(0.0, dot))
        poly_scr = [scr_apex, scr_brim[i], scr_brim[(i + 1) % num_pts]]
        facets.append((d, poly_scr, col_facet, i))

    facets.sort(key=lambda f: f[0])
    for _, poly, col, idx in facets:
        pygame.draw.polygon(c.surface, col, poly)
        pygame.draw.polygon(c.surface, P["jingasa_rim"], poly, 1)

    # Capelote metálico no ápice (tehen teppen)
    mk.cbox(c, apex[0], apex[1], apex[2] + 0.006, 0.038, 0.038, 0.016, P["gold"], outline=False)

    # Brasão da Libélula Dourada (Tonbo) na faceta frontal
    if mk.depth(c, fx, fy) > -0.05:
        crest_pt = (bx + fx * (radius * 0.55), by + fy * (radius * 0.55), hz + 0.178)
        # Corpo da libélula
        mk.obox(c, (crest_pt[0] - fx * 0.01, crest_pt[1] - fy * 0.01, crest_pt[2] - 0.012), (fx, fy, 0.5), 0.032, 0.008, 0.008, P["gold"], outline=False)
        # Asas horizontais da libélula
        mk.obox(c, (crest_pt[0] - px * 0.018, crest_pt[1] - py * 0.018, crest_pt[2] + 0.004), (px, py, 0.0), 0.036, 0.007, 0.007, P["gold"], outline=False)

    # Jugular de algodão (chin strap) amarrada sob a mandíbula
    for s in (-1.0, 1.0):
        strap_top = (bx + px * 0.085 * s, by + py * 0.085 * s, brim_z)
        strap_bot = (bx + fx * 0.035, by + fy * 0.035, hz + 0.015)
        mk.limb(c, strap_top, strap_bot, 0.012, P["strap"], outline=False, height=0.010)


def _draw_kiseru(c, hand, smoking=False):
    """Cachimbo japonês tradicional (Kiseru) de latão dourado e bambu com baforada 3D de fumaça."""
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

    # Baforada de fumaça aromática esvoaçando
    if smoking:
        smoke_pos = mk.add(tip, bowl_up, 0.045)
        for i in range(3):
            sw = 0.020 + i * 0.014
            mk.cbox(c, smoke_pos[0] + fx * (i * 0.020), smoke_pos[1] + fy * (i * 0.020), smoke_pos[2] + i * 0.030,
                    sw, sw, sw, P["smoke"], outline=False)


def _draw_rifle(c, hand_r, hand_l):
    """Arcabuz Tanegashima autêntico: cano longo de ferro, coronha de carvalho/cerejeira, mecha e serpentina."""
    P = pal()
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    state = getattr(c, "state", "IDLE")

    # Caso especial: Pose de vitória com o fuzil descansado verticalmente sobre o ombro esquerdo
    is_shoulder_rest = (pose in ("shoulder_rest", "kiseru_light", "kiseru_puff") or state == "VICTORY")
    if is_shoulder_rest:
        # Cano apontado para cima e para trás sobre o ombro
        d = mk.norm((-c.fx * 0.35 - c.px * 0.15, -c.fy * 0.35 - c.py * 0.15, 0.92))
        butt = (c.base_x - c.px * 0.08 + c.fx * 0.02, c.base_y - c.py * 0.08 + c.fy * 0.02, c.torso_z + 0.15)
    else:
        d = (hand_l[0] - hand_r[0], hand_l[1] - hand_r[1], hand_l[2] - hand_r[2])
        dlen = math.hypot(d[0], math.hypot(d[1], d[2]))
        if dlen < 1e-3:
            d = mk.norm((c.fx, c.fy, 0.15))
        else:
            d = (d[0] / dlen, d[1] / dlen, d[2] / dlen)
        butt = mk.add(hand_r, d, -0.22)

    # Coronha de madeira (stock)
    mk.obox(c, butt, d, 0.18, 0.052, 0.082, P["wood_dark"])
    # Corpo principal de madeira sob o cano
    mk.obox(c, mk.add(butt, d, 0.18), d, 0.32, 0.048, 0.058, P["wood"])
    mk.obox(c, mk.add(butt, d, 0.50), d, 0.24, 0.042, 0.046, P["wood"])

    # Cano octogonal de ferro longo
    barrel_start = mk.add(butt, d, 0.28)
    mk.obox(c, barrel_start, d, 0.56, 0.034, 0.034, P["barrel"])
    # Anéis de fixação de latão no cano
    for t in (0.12, 0.28, 0.44):
        mk.obox(c, mk.add(barrel_start, d, t), d, 0.016, 0.042, 0.042, P["brass"], outline=False)

    # Mecanismo de fecho de mecha (serpentina / hibasami)
    lock_pt = mk.add(butt, d, 0.22)
    mk.cbox(c, lock_pt[0], lock_pt[1], lock_pt[2] + 0.032, 0.036, 0.036, 0.045, P["brass"])
    ember_pt = (lock_pt[0], lock_pt[1], lock_pt[2] + 0.075)
    mk.cbox(c, ember_pt[0], ember_pt[1], ember_pt[2], 0.022, 0.022, 0.022, P["ember"], outline=False)

    # Cordão da mecha (hinawa) enrolado com ponta pendurada
    trail, amp, freq = mk.motion(c, 0.06)
    offs = cloth.chain_offsets(3, c.walk_timer, 0.5, trail, (c.px, c.py), amp=amp * 1.4, freq=freq, wind=cloth.wind_at(ember_pt[0], ember_pt[1]))
    pts = [ember_pt]
    for i, o in enumerate(offs):
        pt = (ember_pt[0] - c.fx * 0.025 * (i + 1) + o[0],
              ember_pt[1] - c.fy * 0.025 * (i + 1) + o[1],
              ember_pt[2] - 0.035 * (i + 1) + o[2])
        pts.append(pt)
    draw_ribbon_mesh_3d(
        c.surface, c.camera,
        spine_points=pts,
        widths=[0.014, 0.012, 0.010, 0.007],
        depth_thick=0.008,
        colors=[P["cord"], P["ember"]],
        side_vec=(c.px, c.py, 0.0),
        normal_vec=(c.fx, c.fy, 0.0),
        outline=False,
        alpha=c.alpha,
    )

    # Fumaça aromática esvoaçando da brasa ou da boca do cano
    muzzle_pt = mk.add(barrel_start, d, 0.58)
    smoke_origin = muzzle_pt if is_shoulder_rest else ember_pt
    for i in range(2):
        s_off = cloth.chain_offsets(2, c.walk_timer * 1.5, 1.2 * i, (0.0, 0.0), (c.px, c.py), amp=0.03, freq=1.6, wind=cloth.wind_at(smoke_origin[0], smoke_origin[1]))[1]
        mk.cbox(c, smoke_origin[0] + s_off[0], smoke_origin[1] + s_off[1], smoke_origin[2] + 0.05 + 0.04 * i,
                0.032 + 0.015 * i, 0.032 + 0.015 * i, 0.032 + 0.015 * i, P["smoke"], outline=False)

    # Vareta de ferro (Ramrod) visível sendo empurrada se em recarga
    if pose == "ramrod_reload" or extra.get("is_reloading", False):
        p_reload = extra.get("p", 0.5)
        rod_depth = math.sin(_smooth(p_reload) * math.pi * 3.0) * 0.22
        mk.obox(c, mk.add(muzzle_pt, d, -rod_depth), d, 0.40, 0.012, 0.012, P["ramrod"], outline=False)


def draw_behind(c):
    """Camada traseira com ordenação dinâmica de profundidade 3D."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_l, hand_r = _hands(c)
    d_rifle = max(mk.depth(c, hand_l[0], hand_l[1]), mk.depth(c, hand_r[0], hand_r[1]))

    # Arcabuz se estiver atrás do tronco
    if d_rifle < d_torso - 0.01:
        _draw_rifle(c, hand_r, hand_l)

    # Kiseru em vitória se estiver sendo segurado atrás do tronco
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    if pose in ("kiseru_light", "kiseru_puff") or (getattr(c, "state", "") == "VICTORY" and float((c.extra_props or {}).get("p", 0.0)) >= 0.35):
        if mk.depth(c, hand_r[0], hand_r[1]) < d_torso:
            _draw_kiseru(c, hand_r, smoking=True)


def draw_legs(c):
    """Calças largas kukuri-bakama contínuas presas em caneleiras de ferro (suneate) e sandálias waraji."""
    P = pal()
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]

        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0], sh[1], sh[2] + 0.16)
        ankle = (ft[0], ft[1], ft[2] + 0.06)

        # Hakama contínua 3D
        draw_ribbon_mesh_3d(
            c.surface, c.camera,
            spine_points=[top, knee, ankle],
            widths=[0.125, 0.112, 0.088],
            depth_thick=0.098,
            colors=[P["hakama"], P["hakama_dark"]],
            side_vec=(c.px, c.py, 0.0),
            normal_vec=(c.fx, c.fy, 0.0),
            outline=True,
            alpha=c.alpha,
        )

        # Caneleira de ferro (suneate)
        mk.cbox(c, sh[0] + c.fx * 0.020, sh[1] + c.fy * 0.020, sh[2] + 0.04, 0.082, 0.082, 0.088, P["suneate"], outline=True)

        # Sandálias de palha Waraji com meias Tabi escuras
        mk.obox(c, (ft[0] - c.fx * 0.038, ft[1] - c.fy * 0.038, ft[2]), (c.fx, c.fy, 0.0), 0.140, 0.080, 0.024, P["waraji"])
        mk.obox(c, (ft[0] - c.fx * 0.020, ft[1] - c.fy * 0.020, ft[2] + 0.022), (c.fx, c.fy, 0.0), 0.110, 0.070, 0.038, P["tabi"])


def draw_obi(c):
    """Cinto com placas kusazuri, chifre de pólvora negra (kayakutsubo) e bolsa de balas de chumbo."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07

    # Cinto de couro
    mk.cbox(c, bx, by, z, c.pelvis_w, c.pelvis_w * 0.78, 0.065, P["belt"])

    # Placas da saia de armadura (kusazuri)
    for s in (-1.0, 1.0):
        t_pos = (bx + px * 0.145 * s, by + py * 0.145 * s, z - 0.06)
        mk.cbox(c, t_pos[0], t_pos[1], t_pos[2], 0.072, 0.035, 0.082, P["cuirass"])
        mk.cbox(c, t_pos[0], t_pos[1], t_pos[2] + 0.015, 0.076, 0.038, 0.016, P["sode_lace"], outline=False)

    # Chifre de pólvora negra (kayakutsubo) no lado direito
    horn_pos = (bx - px * 0.145 - fx * 0.02, by - py * 0.145 - fy * 0.02, z + 0.01)
    mk.obox(c, horn_pos, mk.norm((-px * 0.4, -py * 0.4, -0.9)), 0.11, 0.048, 0.048, P["horn"])
    mk.obox(c, mk.add(horn_pos, mk.norm((-px * 0.4, -py * 0.4, -0.9)), 0.10), mk.norm((-px * 0.5 + fx * 0.3, -py * 0.5 + fy * 0.3, -0.8)), 0.05, 0.038, 0.038, P["brass"])

    # Bolsa de balas de chumbo no flanco esquerdo
    mk.cbox(c, bx + px * 0.145 - fx * 0.03, by + py * 0.145 - fy * 0.03, z - 0.01, 0.065, 0.055, 0.075, P["belt"])


def draw_torso(c):
    """Couraça Dō de ferro com rebites, colarinho branco eri e bandoleira com 6 cargas rápidas de bambu (hayago)."""
    P = pal()
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    # Hitatare verde-oliva interno
    mk.cbox(c, bx, by, tz + 0.02, 0.29, 0.22, 0.16, P["hitatare"])

    # Couraça Dō de ferro fundido
    mk.cbox(c, bx, by, tz + 0.07, 0.315, 0.245, 0.19, P["cuirass"])

    front = 0.135
    # Detalhes frontais (visíveis se a frente estiver voltada para a câmera)
    if mk.depth(c, fx, fy) > -0.05:
        # Colarinho branco cruzado (eri)
        c_left = (bx + fx * (front - 0.010) - px * 0.065, by + fy * (front - 0.010) - py * 0.065, tz + 0.255)
        c_apex = (bx + fx * (front - 0.005), by + fy * (front - 0.005), tz + 0.185)
        c_right = (bx + fx * (front - 0.010) + px * 0.065, by + fy * (front - 0.010) + py * 0.065, tz + 0.255)
        mk.limb(c, c_left, c_apex, 0.024, P["collar_white"], outline=False, height=0.016)
        mk.limb(c, c_right, c_apex, 0.024, P["collar_white"], outline=False, height=0.016)

        # Rebites de ferro e tiras de amarração
        for i in range(3):
            z_rib = tz + 0.045 + i * 0.055
            mk.cbox(c, bx + fx * front, by + fy * front, z_rib, 0.21, 0.014, 0.014, P["sode_lace"], outline=False)
            for s in (-1.0, 1.0):
                mk.cbox(c, bx + fx * (front + 0.005) + px * 0.085 * s, by + fy * (front + 0.005) + py * 0.085 * s, z_rib, 0.014, 0.014, 0.014, P["rivet"], outline=False)

        # Bandoleira de couro cruzando o peito
        a = (bx - px * 0.115 + fx * front, by - py * 0.115 + fy * front, tz + 0.26)
        b = (bx + px * 0.115 + fx * front, by + py * 0.115 + fy * front, tz + 0.02)
        mk.limb(c, a, b, 0.030, P["bandolier"], outline=False, height=0.016)

        # 3 cargas rápidas de bambu (hayago) no peito
        for i in range(3):
            t = 0.28 + i * 0.22
            h_pos = (a[0] * (1.0 - t) + b[0] * t + fx * 0.018,
                     a[1] * (1.0 - t) + b[1] * t + fy * 0.018,
                     a[2] * (1.0 - t) + b[2] * t)
            mk.obox(c, h_pos, (0.0, 0.0, 1.0), 0.055, 0.024, 0.024, P["hayago"], outline=False)
            # Tampa de latão do hayago
            mk.obox(c, (h_pos[0], h_pos[1], h_pos[2] + 0.048), (0.0, 0.0, 1.0), 0.012, 0.026, 0.026, P["brass"], outline=False)

    # Detalhes das costas: 3 tubos hayago adicionais na bandoleira dorsal
    if mk.depth(c, -fx, -fy) > -0.05:
        back = -0.135
        ba = (bx + px * 0.115 + fx * back, by + py * 0.115 + fy * back, tz + 0.26)
        bb = (bx - px * 0.115 + fx * back, by - py * 0.115 + fy * back, tz + 0.02)
        mk.limb(c, ba, bb, 0.030, P["bandolier"], outline=False, height=0.016)
        for i in range(3):
            t = 0.28 + i * 0.22
            h_pos = (ba[0] * (1.0 - t) + bb[0] * t - fx * 0.018,
                     ba[1] * (1.0 - t) + bb[1] * t - fy * 0.018,
                     ba[2] * (1.0 - t) + bb[2] * t)
            mk.obox(c, h_pos, (0.0, 0.0, 1.0), 0.055, 0.024, 0.024, P["hayago"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """Manga larga de hitatare verde, cotovelo articulado e braçadeira de ferro (kote)."""
    P = pal()
    return mk.arm(c, shoulder, hand, side, P["skin"], sleeve=P["hitatare"], sleeve_to=0.52, bracer=P["suneate"], bracer_span=(0.40, 0.95), w=0.065)


def draw_sleeves(c, arms):
    """Ombreiras de ferro segmentadas (sode) em 3 lâminas com cordões dourados."""
    P = pal()
    for s, e, side in arms:
        z = s[2] + 0.02
        ox, oy = c.px * side * 0.028, c.py * side * 0.028
        for i, (w, h, col) in enumerate(((0.145, 0.038, P["cuirass"]), (0.132, 0.038, P["cuirass_dark"]), (0.118, 0.038, P["cuirass"]))):
            mk.cbox(c, s[0] + ox * (1 + 0.45 * i), s[1] + oy * (1 + 0.45 * i), z - 0.042 * i - 0.02, w, w - 0.018, h, col)
            mk.cbox(c, s[0] + ox * (1 + 0.45 * i) * 1.4, s[1] + oy * (1 + 0.45 * i) * 1.4, z - 0.042 * i - 0.015, 0.014, 0.014, 0.014, P["sode_lace"], outline=False)


def draw_head(c):
    """
    Cabeça do Veterano Teppo:
    - Rosto esculpido em 3D com olhos marciais HD (olho direito contraído na mira com anel limbal).
    - Bigode tradicional de veterano esculpido em 3D.
    - Fuligem de pólvora na bochecha direita.
    - Jingasa cônica laqueada com o brasão Tonbo e jugular de algodão.
    """
    P = pal()
    bx, by, hz, fx, fy, px, py, hw = c.base_x, c.base_y, c.head_z, c.fx, c.fy, c.px, c.py, c.head_w
    extra = getattr(c, "extra_props", {}) or {}
    legacy = extra.get("legacy_mode", False)

    # 1. Rosto HD esculpido via draw_portrait_face_3d (quando a face está virada para a câmera)
    if not legacy and mk.depth(c, fx, fy) > -0.05:
        draw_portrait_face_3d(c, char_type="teppo")
        c._face_drawn = True

        # Fuligem autêntica de pólvora queimada na bochecha direita
        soot_pt = (bx + fx * 0.082 + px * 0.035, by + fy * 0.082 + py * 0.035, hz + 0.045)
        mk.cbox(c, soot_pt[0], soot_pt[1], soot_pt[2], 0.026, 0.026, 0.018, P["soot"], outline=False)

    # 2. Jingasa cônica laqueada no topo da cabeça
    _draw_jingasa(c)


def draw_front(c, arm_l, arm_r):
    """Camada frontal com ordenação por profundidade: renderiza fuzil e kiseru à frente do tronco."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_l, hand_r = _hands(c)
    d_rifle = max(mk.depth(c, hand_l[0], hand_l[1]), mk.depth(c, hand_r[0], hand_r[1]))

    # Arcabuz se estiver à frente do tronco
    if d_rifle >= d_torso - 0.01:
        _draw_rifle(c, hand_r, hand_l)

    # Kiseru em vitória se estiver sendo segurado à frente do tronco
    extra = getattr(c, "extra_props", {}) or {}
    pose = extra.get("pose", "")
    if pose in ("kiseru_light", "kiseru_puff") or (getattr(c, "state", "") == "VICTORY" and float((c.extra_props or {}).get("p", 0.0)) >= 0.35):
        if mk.depth(c, hand_r[0], hand_r[1]) >= d_torso:
            _draw_kiseru(c, hand_r, smoking=True)
