"""
Ferramentas compartilhadas pelos modelos detalhados dos lutadores (6.5.5): caixas alinhadas e orientadas, membros entre
dois pontos e uma cadeia de elos pendurada. O `c` é o contexto que `render_voxel_humanoid` monta para cada modelo
(superfície, câmera, alfa, posição base, vetores de frente e lado, fase de caminhada e estado de ataque).
"""
import math

import pygame

from src.isometric.iso_math import rotate_xy
from src.isometric.voxel_renderer import draw_oriented_voxel_box, draw_voxel_box


def band(c, points, rgba):
    """Polígono translúcido entre pontos do mundo (rastro de golpe, brilho de energia); o alfa acompanha o do lutador."""
    scr = [c.camera.apply(p[0], p[1], p[2]) for p in points]
    x0, y0 = min(p[0] for p in scr) - 1, min(p[1] for p in scr) - 1
    w, h = max(p[0] for p in scr) - x0 + 2, max(p[1] for p in scr) - y0 + 2
    if w < 2 or h < 2 or w > 1600 or h > 1600:
        return
    layer = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(layer, (rgba[0], rgba[1], rgba[2], int(rgba[3] * c.alpha / 255)), [(p[0] - x0, p[1] - y0) for p in scr])
    c.surface.blit(layer, (x0, y0))


def material_for(c, color, texture=None):
    """Textura da peça: a pedida ou, sem ela, a do material que o lutador declara para essa cor (`c.materials`)."""
    if texture:
        return texture
    materials = getattr(c, "materials", None)
    return materials.get(tuple(color[:3])) if materials else None


def material_map(palette: dict, materials: dict) -> dict:
    """{cor: textura} a partir de {chave da paleta: textura}; chaves que a paleta não tem são ignoradas."""
    return {tuple(palette[key][:3]): texture for key, texture in materials.items() if key in palette}


def box(c, x, y, z, w, d, h, color, outline=True, texture=None):
    """Caixa alinhada aos eixos com o canto mínimo em (x, y, z)."""
    draw_voxel_box(c.surface, c.camera, x, y, z, w, d, h, color, outline=outline, alpha=c.alpha, texture=material_for(c, color, texture))


def cbox(c, cx, cy, z, w, d, h, color, outline=True, texture=None):
    """Caixa alinhada aos eixos centrada em (cx, cy), com a base em z."""
    draw_voxel_box(c.surface, c.camera, cx - w / 2, cy - d / 2, z, w, d, h, color, outline=outline, alpha=c.alpha, texture=material_for(c, color, texture))


def obox(c, origin, direction, length, width, height, color, up=(0.0, 0.0, 1.0), outline=True, alpha=None, texture=None):
    """Caixa orientada: o comprimento corre de `origin` ao longo de `direction`."""
    draw_oriented_voxel_box(c.surface, c.camera, origin[0], origin[1], origin[2], direction[0], direction[1], direction[2],
                            length, width, height, color, up_x=up[0], up_y=up[1], up_z=up[2], outline=outline,
                            alpha=c.alpha if alpha is None else alpha, texture=material_for(c, color, texture))


def limb(c, a, b, width, color, outline=True, height=None, texture=None):
    """Caixa orientada de `a` até `b` (braço, cabo, corrente)."""
    d = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    length = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
    if length < 1e-4:
        return
    obox(c, a, d, length, width, width if height is None else height, color, outline=outline, texture=texture)


def norm(v):
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) or 1.0
    return (v[0] / n, v[1] / n, v[2] / n)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def facing_camera(c) -> bool:
    """O rosto está voltado para a câmera (ou de perfil)? Detalhes do rosto só aparecem nesse caso."""
    rx, ry = rotate_xy(c.fx, c.fy, c.azimuth)
    return rx + ry > -0.15


def depth(c, x, y) -> float:
    """Profundidade na tela (maior = mais perto da câmera) para desenhar de trás para a frente."""
    rx, ry = rotate_xy(x, y, c.azimuth)
    return rx + ry


def motion(c, scale=0.07):
    """(arrasto, amplitude do balanço, frequência) conforme o lutador ande ou fique parado."""
    if c.is_moving:
        return (-c.fx * scale, -c.fy * scale), 0.04, 7.0
    return (0.0, 0.0), 0.014, 1.7


def chain_points(a, b, count, sag, sway=(0.0, 0.0, 0.0)):
    """Pontos de uma corrente frouxa entre `a` e `b`: uma parábola que cai `sag` no meio, mais um balanço lateral."""
    pts = []
    for i in range(count + 1):
        t = i / count
        bend = 4.0 * t * (1.0 - t)
        pts.append((a[0] + (b[0] - a[0]) * t + sway[0] * bend, a[1] + (b[1] - a[1]) * t + sway[1] * bend,
                    a[2] + (b[2] - a[2]) * t - sag * bend + sway[2] * bend))
    return pts


# ---------------------------------------------------------------------------------------------------------------------
# Peças comuns dos modelos detalhados (pernas, braços, panos pendurados, rosto, espada)
# ---------------------------------------------------------------------------------------------------------------------

def sorted_sides(c):
    """('L', 'R') do lado mais distante da câmera para o mais próximo."""
    return sorted(("L", "R"), key=lambda s: depth(c, c.legs_data[s]["foot"][0], c.legs_data[s]["foot"][1]))


def legs(c, pants, boot=None, boot_h=0.12, baggy=None, tight_w=(0.105, 0.09), foot_color=(60, 52, 40), foot_len=0.13, foot_w=0.075,
         sole=None, cuff=None, texture=None):
    """
    Pernas de um lutador. `baggy=(coxa, canela)` desenha calça larga em caixas que se estreita na bota; sem ele, pernas justas
    em membros. `boot=(cor, borda)` cobre a canela de baixo; `cuff` é a cor do punho da bota.
    """
    trail, amp, freq = motion(c, 0.04)
    for side in sorted_sides(c):
        ld = c.legs_data[side]
        th, sh, ft = ld["thigh"], ld["shin"], ld["foot"]
        sign = 1.0 if side == "L" else -1.0
        o1, o2 = cloth_offsets(c, 2, 0.9 * sign, trail, amp * 0.7, freq, ft)
        if sole is not None:
            obox(c, (ft[0] - c.fx * 0.05, ft[1] - c.fy * 0.05, ft[2]), (c.fx, c.fy, 0.0), foot_len, foot_w, 0.022, sole)
        obox(c, (ft[0] - c.fx * 0.03, ft[1] - c.fy * 0.03, ft[2] + (0.02 if sole is not None else 0.0)), (c.fx, c.fy, 0.0), foot_len - 0.02, foot_w - 0.012, 0.045, foot_color)
        if baggy is not None:
            cbox(c, th[0], th[1], th[2], baggy[0], baggy[0], 0.22, pants, texture=texture)
            cbox(c, sh[0] + o1[0], sh[1] + o1[1], sh[2] + 0.08, baggy[1], baggy[1], 0.13, pants, texture=texture)
            cbox(c, sh[0] + o2[0] * 0.5, sh[1] + o2[1] * 0.5, sh[2] + 0.02, baggy[1] - 0.025, baggy[1] - 0.025, 0.07, pants)
        else:
            top, knee, ankle = (th[0], th[1], th[2] + 0.215), (sh[0], sh[1], sh[2] + 0.205), (ft[0], ft[1], ft[2] + 0.1)
            limb(c, top, knee, tight_w[0], pants)
            cbox(c, knee[0], knee[1], knee[2] - 0.045, tight_w[0] - 0.01, tight_w[0] - 0.01, 0.07, pants, outline=False)
            limb(c, knee, ankle, tight_w[1], pants)
        if boot is not None:
            cbox(c, sh[0], sh[1], sh[2] + 0.005, 0.1, 0.1, boot_h, boot)
            if cuff is not None:
                cbox(c, sh[0], sh[1], sh[2] + boot_h - 0.012, 0.108, 0.108, 0.02, cuff, outline=False)


def cloth_offsets(c, count, phase, trail, amp, freq, at, wind_gain=0.035):
    from src.isometric import cloth
    return cloth.chain_offsets(count, c.walk_timer, phase, trail, (c.px, c.py), amp=amp, freq=freq, wind=cloth.wind_at(at[0], at[1]), wind_gain=wind_gain)


def arm(c, shoulder, hand, side, skin, sleeve=None, sleeve_to=1.0, glove=None, bracer=None, bracer_span=(0.45, 0.92), w=0.056, bend=0.03):
    """Braço em duas partes, ombro-cotovelo-mão. `sleeve` cobre o braço até `sleeve_to`; `bracer` é a braçadeira do antebraço."""
    s = (shoulder[0], shoulder[1], c.torso_z + 0.205)
    h = (hand[0], hand[1], hand[2] - 0.065)
    out = (c.px * side, c.py * side, 0.0)
    e = add(add(lerp(s, h, 0.5), out, bend), (0.0, 0.0, -0.035))
    upper = sleeve if sleeve is not None else skin
    limb(c, s, e, w + 0.01, upper)
    fore_color = sleeve if (sleeve is not None and sleeve_to > 1.0) else skin
    limb(c, e, h, w, fore_color)
    if bracer is not None:
        limb(c, lerp(e, h, bracer_span[0]), lerp(e, h, bracer_span[1]), w + 0.016, bracer)
    cbox(c, h[0], h[1], h[2] - 0.028, w, w, w, glove if glove is not None else skin)
    return s, e


def panels(c, anchor, count, seg, width, depth_, colors, phase=0.0, up=None, spread=0.0, side=1.0, trail=None, amp=None, freq=None,
           drag=(0.0, 0.0), flare=0.0, outline=True):
    """Pano pendurado (manga, capa, casaco): `count` segmentos que descem de `anchor`, balançando; devolve a origem do último."""
    if trail is None:
        trail, amp, freq = motion(c, 0.07)
    offs = cloth_offsets(c, count, phase, (trail[0] + drag[0], trail[1] + drag[1]), amp * 1.5, freq, anchor)
    up = up if up is not None else (c.fx, c.fy, 0.0)
    last = anchor
    for i, o in enumerate(offs):
        origin = (anchor[0] + o[0] + c.px * side * spread * i, anchor[1] + o[1] + c.py * side * spread * i, anchor[2] - seg * i + o[2])
        color = colors[min(i, len(colors) - 1)]
        obox(c, origin, (0.0, 0.0, -1.0), seg, width + flare * i, depth_ + flare * 2 * i, color, up=up, outline=outline)
        last = (origin[0], origin[1], origin[2] - seg)
    return last


def face(c, eye, brow, mouth, skin_shadow, eye_z=0.088, brow_z=0.13, spacing=0.036, brow_tilt=0.0, mouth_w=0.026, nose=True):
    """Olhos, sobrancelhas, nariz e boca; só aparecem quando o rosto está voltado para a câmera."""
    if not facing_camera(c):
        return
    hz, hw = c.head_z, c.head_w
    front = hw / 2 + 0.004
    for s in (-1.0, 1.0):
        ex, ey = c.base_x + c.fx * front + c.px * spacing * s, c.base_y + c.fy * front + c.py * spacing * s
        cbox(c, ex, ey, hz + eye_z, 0.024, 0.02, 0.022, eye, outline=False)
        limb(c, (ex - c.px * 0.022 * s, ey - c.py * 0.022 * s, hz + brow_z - brow_tilt), (ex + c.px * 0.022 * s, ey + c.py * 0.022 * s, hz + brow_z + brow_tilt), 0.011, brow, outline=False)
    if nose:
        cbox(c, c.base_x + c.fx * front, c.base_y + c.fy * front, hz + 0.062, 0.012, 0.012, 0.012, skin_shadow, outline=False)
    cbox(c, c.base_x + c.fx * front, c.base_y + c.fy * front, hz + 0.043, mouth_w, 0.012, 0.009, mouth, outline=False)


def hair_volume(c, color, size=0.15, height=0.12, back=0.036):
    """Volume de cabelo atrás da cabeça: fica atrás do rosto, e de costas cobre a cabeça."""
    cbox(c, c.base_x - c.fx * back, c.base_y - c.fy * back, c.head_z + 0.03, size, size, height, color, outline=False)


def plate(c, z, h, color, thickness=0.03, outline=True, inset=0.0):
    """Placa fina na frente da cabeça (máscara, faixa dos olhos), orientada pelo rosto."""
    hw = c.head_w
    obox(c, (c.base_x + c.fx * (hw / 2 - thickness + 0.012 - inset), c.base_y + c.fy * (hw / 2 - thickness + 0.012 - inset), z), (c.fx, c.fy, 0.0), thickness,
         hw + 0.012, h, color, outline=outline)


def sword(c, hand, d, length, steel, edge, grip, guard, gold, guard_w=0.085, grip_len=0.16, blade_w=0.044):
    """Espada na mão: cabo atrás da mão, guarda, habaki e lâmina com fio claro."""
    tsuba = add(hand, d, 0.06)
    obox(c, add(tsuba, d, -grip_len), d, grip_len, 0.04, 0.04, grip)
    obox(c, add(tsuba, d, -grip_len - 0.012), d, 0.02, 0.046, 0.046, gold, outline=False)
    obox(c, add(tsuba, d, -0.008), d, 0.016, guard_w, guard_w, guard)
    obox(c, add(tsuba, d, 0.008), d, 0.03, 0.05, 0.036, gold, outline=False)
    obox(c, add(tsuba, d, 0.03), d, length, blade_w, 0.03, steel)
    obox(c, add(tsuba, d, 0.04), d, max(0.0, length - 0.02), 0.016, 0.034, edge, outline=False)
    return add(tsuba, d, 0.03 + length)


def behind(c, point) -> bool:
    return depth(c, point[0], point[1]) < depth(c, c.base_x, c.base_y) - 0.02
