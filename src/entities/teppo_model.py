"""
Teppo, o arcabuzeiro Tanegashima & Mestre de Artilharia (6.5.5):
- Jingasa cônica 3D facetada laqueada em preto com brasão do dragão-alado/libélula dourada (Tonbo) e jugular de algodão.
- Rosto de veterano esculpido em 3D Tekken 2/3 com olhar determinado, nariz estruturado e bigode tradicional.
- Armadura Ashigaru do feudal: hitatare verde-oliva com colarinho branco interno, couraça de ferro escuro (do) com rebites.
- Ombreiras segmentadas em placas laqueadas (sode) com cordões dourados.
- Bandoleira de couro com tubos rápidos de bambu (hayago) e chifre de pólvora negra (kayakutsubo).
- Calças largas kukuri-bakama contínuas sem degraus nos joelhos, presas em caneleiras de ferro (suneate) e sandálias waraji.
- Arcabuz feudal Tanegashima de coronha de cerejeira polida, cano longo de ferro com anéis e mecha fumegante acesa.
- Ordenação dinâmica por profundidade (Painter's Algorithm): couraça das costas oclui arcabuz e braços em 360°.
"""
import math

import pygame

from src.entities import model_kit as mk
from src.isometric import cloth
from src.isometric.mesh_primitives import draw_ribbon_mesh_3d, draw_tapered_frustum_3d, _clamp_color

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
    "cord": (195, 170, 120),
}

MATERIALS = {
    "cuirass": "metal", "cuirass_dark": "metal", "sode": "metal", "jingasa": "lacquer",
    "barrel": "metal", "barrel_light": "chrome", "brass": "gold", "gold": "gold",
    "wood": "planks", "wood_dark": "planks", "horn": "lacquer", "bandolier": "leather",
    "belt": "leather", "hakama": "canvas", "hitatare": "cloth", "suneate": "metal",
}


def pal() -> dict:
    return PALETTE


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def _hands(c):
    """Posição das mãos empunhando o arcabuz em guarda ou em pontaria."""
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    if c.is_melee and c.atk_progress is not None:
        p = c.atk_progress
        t = _smooth(p)
        # Recuo e elevação do tiro fatal
        recoil = math.sin(t * math.pi) * 0.08
        aim_z = 0.24 + recoil * 0.5
        hand_r = (bx + fx * (0.16 - recoil) - px * 0.06, by + fy * (0.16 - recoil) - py * 0.06, tz + aim_z)
        hand_l = (bx + fx * (0.38 - recoil) + px * 0.05, by + fy * (0.38 - recoil) + py * 0.05, tz + aim_z - 0.02)
        return hand_l, hand_r

    sway = math.sin(c.walk_timer * (6.0 if c.is_moving else 2.0)) * (0.02 if c.is_moving else 0.008)
    # Empunhadura clássica de guarda baixa do arcabuz
    hand_r = (bx + fx * 0.14 - px * 0.08, by + fy * 0.14 - py * 0.08, tz + 0.12 + sway)
    hand_l = (bx + fx * 0.32 + px * 0.06, by + fy * 0.32 + py * 0.06, tz + 0.10 - sway)
    return hand_l, hand_r


def _draw_jingasa(c):
    """Jingasa cônica 3D facetada em 8 planos com crista dourada Tonbo e jugular de algodão."""
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

    # Projeção dos vértices na tela
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




def _draw_rifle(c, hand_r, hand_l):
    """Arcabuz Tanegashima autêntico: cano longo de ferro, coronha de cerejeira polida, serpentina com mecha acesa."""
    P = pal()
    d = (hand_l[0] - hand_r[0], hand_l[1] - hand_r[1], hand_l[2] - hand_r[2])
    dlen = math.hypot(d[0], math.hypot(d[1], d[2]))
    if dlen < 1e-3:
        d = mk.norm((c.fx, c.fy, 0.15))
    else:
        d = (d[0] / dlen, d[1] / dlen, d[2] / dlen)

    # Coronha de madeira (stock) estendendo para trás do punho
    butt = mk.add(hand_r, d, -0.22)
    mk.obox(c, butt, d, 0.18, 0.052, 0.082, P["wood_dark"])
    # Corpo principal de madeira sob o cano
    mk.obox(c, mk.add(butt, d, 0.18), d, 0.32, 0.048, 0.058, P["wood"])
    mk.obox(c, mk.add(butt, d, 0.50), d, 0.24, 0.042, 0.046, P["wood"])

    # Cano octagonal de ferro longo
    barrel_start = mk.add(butt, d, 0.28)
    mk.obox(c, barrel_start, d, 0.56, 0.034, 0.034, P["barrel"])
    # Anéis de fixação de latão (anéis mecânicos do cano)
    for t in (0.12, 0.28, 0.44):
        mk.obox(c, mk.add(barrel_start, d, t), d, 0.016, 0.042, 0.042, P["brass"], outline=False)

    # Mecanismo de fecho de mecha (serpentina / hibasami)
    lock_pt = mk.add(hand_r, d, 0.02)
    mk.cbox(c, lock_pt[0], lock_pt[1], lock_pt[2] + 0.032, 0.036, 0.036, 0.045, P["brass"])
    # Brasa acesa na ponta da serpentina
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

    # Fumaça aromática esvoaçando da brasa
    for i in range(2):
        s_off = cloth.chain_offsets(2, c.walk_timer * 1.5, 1.2 * i, (0.0, 0.0), (c.px, c.py), amp=0.03, freq=1.6, wind=cloth.wind_at(ember_pt[0], ember_pt[1]))[1]
        mk.cbox(c, ember_pt[0] + s_off[0], ember_pt[1] + s_off[1], ember_pt[2] + 0.05 + 0.04 * i, 0.032 + 0.015 * i, 0.032 + 0.015 * i, 0.032 + 0.015 * i, P["smoke"], outline=False)


def draw_behind(c):
    """Camada traseira: renderizada ANTES do tronco/pernas."""
    d_torso = mk.depth(c, c.base_x, c.base_y)

    # Arcabuz e braços se estiverem atrás do tronco (costas voltadas para a câmera)
    hand_l, hand_r = _hands(c)
    d_rifle = max(mk.depth(c, hand_l[0], hand_l[1]), mk.depth(c, hand_r[0], hand_r[1]))
    if d_rifle < d_torso - 0.01:
        _draw_rifle(c, hand_r, hand_l)


def draw_legs(c):
    """Calças largas kukuri-bakama contínuas presas em caneleiras de ferro (suneate) e sandálias waraji."""
    P = pal()
    order = sorted(("L", "R"), key=lambda s: mk.depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))
    for side in order:
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]

        # Perna contínua 3D: coxa, joelho e canela compartilham vértices
        top = (th[0], th[1], th[2] + 0.22)
        knee = (sh[0], sh[1], sh[2] + 0.16)
        ankle = (ft[0], ft[1], ft[2] + 0.06)

        # Hakama larga oliva contínua
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

        # Caneleira de ferro (suneate) no terço inferior da perna
        mk.cbox(c, sh[0] + c.fx * 0.020, sh[1] + c.fy * 0.020, sh[2] + 0.04, 0.082, 0.082, 0.088, P["suneate"], outline=True)

        # Sandálias de palha Waraji com meias Tabi escuras
        mk.obox(c, (ft[0] - c.fx * 0.038, ft[1] - c.fy * 0.038, ft[2]), (c.fx, c.fy, 0.0), 0.140, 0.080, 0.024, P["waraji"])
        mk.obox(c, (ft[0] - c.fx * 0.020, ft[1] - c.fy * 0.020, ft[2] + 0.022), (c.fx, c.fy, 0.0), 0.110, 0.070, 0.038, P["tabi"])


def draw_obi(c):
    """Cinto com kusazuri (placas de armadura da saia), chifre de pólvora e bolsa de munição."""
    P = pal()
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    z = c.pelvis_z + 0.07

    # Cinto de couro
    mk.cbox(c, bx, by, z, c.pelvis_w, c.pelvis_w * 0.78, 0.065, P["belt"])

    # Placas da saia de armadura (kusazuri) protegendo quadril
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
    """Couraça de ferro escuro (do) com rebites, colarinho branco interno e bandoleira de hayago cruzando o peito."""
    P = pal()
    tz = c.torso_z
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py

    # Hitatare verde-oliva interno
    mk.cbox(c, bx, by, tz + 0.02, 0.29, 0.22, 0.16, P["hitatare"])

    # Couraça de ferro escuro (do)
    mk.cbox(c, bx, by, tz + 0.07, 0.315, 0.245, 0.19, P["cuirass"])

    # Detalhes frontais SÓ renderizam se a frente estiver voltada para a câmera
    if mk.depth(c, fx, fy) > -0.05:
        front = 0.135

        # Colarinho branco tradicional cruzado (eri)
        c_left = (bx + fx * (front - 0.010) - px * 0.065, by + fy * (front - 0.010) - py * 0.065, tz + 0.255)
        c_apex = (bx + fx * (front - 0.005), by + fy * (front - 0.005), tz + 0.185)
        c_right = (bx + fx * (front - 0.010) + px * 0.065, by + fy * (front - 0.010) + py * 0.065, tz + 0.255)
        mk.limb(c, c_left, c_apex, 0.024, P["collar_white"], outline=False, height=0.016)
        mk.limb(c, c_right, c_apex, 0.024, P["collar_white"], outline=False, height=0.016)

        # Rebites de aço e cordões na couraça
        for i in range(3):
            z_rib = tz + 0.045 + i * 0.055
            mk.cbox(c, bx + fx * front, by + fy * front, z_rib, 0.21, 0.014, 0.014, P["sode_lace"], outline=False)
            for s in (-1.0, 1.0):
                mk.cbox(c, bx + fx * (front + 0.005) + px * 0.085 * s, by + fy * (front + 0.005) + py * 0.085 * s, z_rib, 0.014, 0.014, 0.014, P["rivet"], outline=False)

        # Bandoleira de couro cruzando o peito da esquerda para a direita
        a = (bx - px * 0.115 + fx * front, by - py * 0.115 + fy * front, tz + 0.26)
        b = (bx + px * 0.115 + fx * front, by + py * 0.115 + fy * front, tz + 0.02)
        mk.limb(c, a, b, 0.030, P["bandolier"], outline=False, height=0.016)

        # Três cargas rápidas de bambu (hayago) presas na bandoleira
        for i in range(3):
            t = 0.30 + i * 0.20
            h_pos = (a[0] * (1.0 - t) + b[0] * t + fx * 0.018,
                     a[1] * (1.0 - t) + b[1] * t + fy * 0.018,
                     a[2] * (1.0 - t) + b[2] * t)
            mk.obox(c, h_pos, (0.0, 0.0, 1.0), 0.055, 0.024, 0.024, P["hayago"], outline=False)


def draw_arm(c, shoulder, hand, side):
    """Manga larga de hitatare, cotovelo articulado e braçadeira de ferro (kote)."""
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
            # Cordão dourado unindo as lâminas
            mk.cbox(c, s[0] + ox * (1 + 0.45 * i) * 1.4, s[1] + oy * (1 + 0.45 * i) * 1.4, z - 0.042 * i - 0.015, 0.014, 0.014, 0.014, P["sode_lace"], outline=False)


def draw_head(c):
    """Jingasa cônica 3D, queixo estruturado e bigode tradicional de atirador."""
    _draw_jingasa(c)


def draw_front(c, arm_l, arm_r):
    """Camada frontal: arcabuz só renderiza aqui se estiver na frente do tronco."""
    d_torso = mk.depth(c, c.base_x, c.base_y)
    hand_l, hand_r = _hands(c)
    d_rifle = max(mk.depth(c, hand_l[0], hand_l[1]), mk.depth(c, hand_r[0], hand_r[1]))
    if d_rifle >= d_torso - 0.01:
        _draw_rifle(c, hand_r, hand_l)
