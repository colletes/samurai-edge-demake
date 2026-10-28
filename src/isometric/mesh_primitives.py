"""
Primitivas de Malha 3D Esculpida (Low-Poly / Tapered Frustums, Fitas de Tecido Contínuas e Rostos 3D)
para Samurai Edge — Bakumatsu (Fase M-2.1).

Regras de Arquitetura Visual:
- PROIBIDO o uso de rotação/escala 2D (`pygame.transform.rotate` / `smoothscale`) acoplada a ossos 3D.
- Todos os membros, troncos em V, cabeças esculpidas, fitas de tecido/cabelo e feições faciais
  são projetados a partir de coordenadas 3D puras no espaço do mundo via `camera.apply(wx, wy, wz)`.
"""
from __future__ import annotations

import math
import pygame

from src.isometric.iso_math import rotate_xy
from src.isometric.voxel_renderer import _get_alpha_scratch, draw_oriented_voxel_box, draw_voxel_box
from src.isometric.voxel_textures import draw_face_texture

COLOR_OUTLINE = (22, 18, 24)


def _clamp_color(color: tuple[int, int, int], factor: float = 1.0) -> tuple[int, int, int]:
    r, g, b = color[:3]
    return (
        max(0, min(255, int(r * factor))),
        max(0, min(255, int(g * factor))),
        max(0, min(255, int(b * factor))),
    )


def _norm3(vx: float, vy: float, vz: float) -> tuple[float, float, float]:
    n = math.sqrt(vx * vx + vy * vy + vz * vz)
    if n < 1e-6:
        return (1.0, 0.0, 0.0)
    return (vx / n, vy / n, vz / n)


def _cross3(ax: float, ay: float, az: float, bx: float, by: float, bz: float) -> tuple[float, float, float]:
    return (
        ay * bz - az * by,
        az * bx - ax * bz,
        ax * by - ay * bx,
    )


def draw_tapered_frustum_3d(
    surface: pygame.Surface,
    camera,
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    w_start: float,
    h_start: float,
    w_end: float,
    h_end: float,
    color: tuple[int, int, int],
    up: tuple[float, float, float] = (0.0, 0.0, 1.0),
    outline: bool = True,
    alpha: int = 255,
    texture: str | None = None,
    cap_start: bool = True,
    cap_end: bool = True,
):
    """
    Desenha um tronco piramidal 3D (frustum de 8 vértices) orientado de `a` para `b`,
    afunilando suavemente de `(w_start, h_start)` em `a` até `(w_end, h_end)` em `b`.
    Ideal para coxas, canelas, braços, antebraços, troncos em V e bainhas/lâminas cônicas.
    """
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-5:
        return

    ux, uy, uz = dx / length, dy / length, dz / length
    up_x, up_y, up_z = _norm3(up[0], up[1], up[2])

    # Eixo lateral V = U x Up
    vx, vy, vz = _cross3(ux, uy, uz, up_x, up_y, up_z)
    v_len = math.sqrt(vx * vx + vy * vy + vz * vz)
    if v_len < 1e-5:
        vx, vy, vz = _cross3(ux, uy, uz, 1.0, 0.0, 0.0)
        v_len = math.sqrt(vx * vx + vy * vy + vz * vz) or 1.0
    vx, vy, vz = vx / v_len, vy / v_len, vz / v_len

    # Eixo ortogonal W = V x U
    wx, wy, wz = _cross3(vx, vy, vz, ux, uy, uz)
    w_len = math.sqrt(wx * wx + wy * wy + wz * wz) or 1.0
    wx, wy, wz = wx / w_len, wy / w_len, wz / w_len

    hw0, hh0 = w_start * 0.5, h_start * 0.5
    hw1, hh1 = w_end * 0.5, h_end * 0.5

    # 4 vértices na base A (0..3) e 4 vértices no topo B (4..7)
    ax, ay, az = a
    bx, by, bz = b
    verts_3d = [
        # Base A (u=0): (-v,-w), (+v,-w), (+v,+w), (-v,+w)
        (ax - vx * hw0 - wx * hh0, ay - vy * hw0 - wy * hh0, az - vz * hw0 - wz * hh0),
        (ax + vx * hw0 - wx * hh0, ay + vy * hw0 - wy * hh0, az + vz * hw0 - wz * hh0),
        (ax + vx * hw0 + wx * hh0, ay + vy * hw0 + wy * hh0, az + vz * hw0 + wz * hh0),
        (ax - vx * hw0 + wx * hh0, ay - vy * hw0 + wy * hh0, az - vz * hw0 + wz * hh0),
        # Topo B (u=length): (-v,-w), (+v,-w), (+v,+w), (-v,+w)
        (bx - vx * hw1 - wx * hh1, by - vy * hw1 - wy * hh1, bz - vz * hw1 - wz * hh1),
        (bx + vx * hw1 - wx * hh1, by + vy * hw1 - wy * hh1, bz + vz * hw1 - wz * hh1),
        (bx + vx * hw1 + wx * hh1, by + vy * hw1 + wy * hh1, bz + vz * hw1 + wz * hh1),
        (bx - vx * hw1 + wx * hh1, by - vy * hw1 + wy * hh1, bz - vz * hw1 + wz * hh1),
    ]

    scr = [camera.apply(p[0], p[1], p[2]) for p in verts_3d]
    azimuth = getattr(camera, "azimuth", 0.0)

    c_top = _clamp_color(color, 1.15)
    c_front = _clamp_color(color, 1.02)
    c_side = _clamp_color(color, 0.85)
    c_dark = _clamp_color(color, 0.68)

    w_avg = (w_start + w_end) * 0.5
    h_avg = (h_start + h_end) * 0.5
    face_defs = [
        ((3, 2, 6, 7), c_front, "front", w_avg, length),
        ((0, 1, 5, 4), c_dark,  "back",  w_avg, length),
        ((1, 2, 6, 5), c_side,  "right", length, h_avg),
        ((0, 3, 7, 4), c_side,  "left",  length, h_avg),
    ]
    if cap_end:
        face_defs.append(((4, 5, 6, 7), c_top, "top", w_end, h_end))
    if cap_start:
        face_defs.append(((0, 1, 2, 3), c_dark, "bottom", w_start, h_start))

    faces = []
    for idxs, shade, kind, ulen, vlen in face_defs:
        cx = sum(verts_3d[i][0] for i in idxs) * 0.25
        cy = sum(verts_3d[i][1] for i in idxs) * 0.25
        cz = sum(verts_3d[i][2] for i in idxs) * 0.25
        rx, ry = rotate_xy(cx, cy, azimuth)
        depth = (rx + ry) + cz * 0.45
        poly = [scr[i] for i in idxs]
        faces.append((depth, poly, shade, kind, ulen, vlen))

    faces.sort(key=lambda f: f[0])
    # Desenha as 4 faces mais visíveis (evita overdraw das faces ocultas traseiras)
    visible_faces = faces[2:]
    seed = int(ax * 73856093) ^ int(ay * 19349663) ^ int(az * 83492791)

    if alpha < 255:
        xs = [p[0] for p in scr]
        ys = [p[1] for p in scr]
        min_x, max_x = min(xs) - 2, max(xs) + 2
        min_y, max_y = min(ys) - 2, max(ys) + 2
        bw, bh = max(1, max_x - min_x), max(1, max_y - min_y)
        temp, sub_rect = _get_alpha_scratch(bw, bh)
        for _, poly, shade, _, _, _ in visible_faces:
            loc = [(p[0] - min_x, p[1] - min_y) for p in poly]
            pygame.draw.polygon(temp, (*shade, alpha), loc)
            if outline:
                pygame.draw.polygon(temp, (*COLOR_OUTLINE, int(alpha * 0.75)), loc, 1)
        surface.blit(temp, (min_x, min_y), sub_rect)
    else:
        for _, poly, shade, kind, ulen, vlen in visible_faces:
            pygame.draw.polygon(surface, shade, poly)
            if texture:
                draw_face_texture(surface, texture, poly, kind, ulen, vlen, shade, seed)
            if outline:
                pygame.draw.polygon(surface, COLOR_OUTLINE, poly, 1)


def draw_ribbon_mesh_3d(
    surface: pygame.Surface,
    camera,
    spine_points: list[tuple[float, float, float]],
    widths: list[float] | tuple[float, ...],
    depth_thick: float,
    colors: list[tuple[int, int, int]] | tuple[tuple[int, int, int], ...],
    side_vec: tuple[float, float, float],
    normal_vec: tuple[float, float, float],
    outline: bool = True,
    alpha: int = 255,
    texture: str | None = None,
):
    """
    Renderiza uma fita contínua 3D (quad-strip volumétrico para mangas furisode/haori, abas de hakama,
    capas, faixas obi e rabos de cavalo) ao longo de `spine_points`.
    Segmentos adjacentes compartilham exatamente os mesmos vértices 3D, eliminando linhas de costura
    internas e desenhando contorno apenas na silhueta externa da peça.
    """
    n = len(spine_points)
    if n < 2:
        return

    sx, sy, sz = _norm3(side_vec[0], side_vec[1], side_vec[2])
    nx, ny, nz = _norm3(normal_vec[0], normal_vec[1], normal_vec[2])
    half_d = depth_thick * 0.5

    # Construir anéis de 4 vértices em cada ponto da espinha:
    # 0: frente-esquerda, 1: frente-direita, 2: trás-direita, 3: trás-esquerda
    rings_3d = []
    rings_scr = []
    for i, (px, py, pz) in enumerate(spine_points):
        w = widths[min(i, len(widths) - 1)] * 0.5
        r3d = (
            (px - sx * w + nx * half_d, py - sy * w + ny * half_d, pz - sz * w + nz * half_d),
            (px + sx * w + nx * half_d, py + sy * w + ny * half_d, pz + sz * w + nz * half_d),
            (px + sx * w - nx * half_d, py + sy * w - ny * half_d, pz - sz * w - nz * half_d),
            (px - sx * w - nx * half_d, py - sy * w - ny * half_d, pz - sz * w - nz * half_d),
        )
        rings_3d.append(r3d)
        rings_scr.append([camera.apply(v[0], v[1], v[2]) for v in r3d])

    azimuth = getattr(camera, "azimuth", 0.0)
    nrx, nry = rotate_xy(nx, ny, azimuth)
    front_faces_cam = (nrx + nry) >= 0.0
    srx, sry = rotate_xy(sx, sy, azimuth)
    right_faces_cam = (srx + sry) >= 0.0

    if alpha < 255:
        all_pts = [pt for r in rings_scr for pt in r]
        xs = [p[0] for p in all_pts]
        ys = [p[1] for p in all_pts]
        min_x, max_x = min(xs) - 2, max(xs) + 2
        min_y, max_y = min(ys) - 2, max(ys) + 2
        bw, bh = max(1, max_x - min_x), max(1, max_y - min_y)
        temp, sub_rect = _get_alpha_scratch(bw, bh)
        target_surf = temp
        ox, oy = min_x, min_y
    else:
        target_surf = surface
        ox, oy = 0, 0

    # Para cada segmento i -> i+1, desenhamos a face lateral visível e a face principal (frente ou costas)
    for i in range(n - 1):
        base_col = colors[min(i, len(colors) - 1)]
        c_main = _clamp_color(base_col, 1.04 if front_faces_cam else 0.90)
        c_side = _clamp_color(base_col, 0.80)
        c_fold = _clamp_color(base_col, 0.74)
        c_sheen = _clamp_color(base_col, 1.18)

        r0 = [(p[0] - ox, p[1] - oy) for p in rings_scr[i]]
        r1 = [(p[0] - ox, p[1] - oy) for p in rings_scr[i + 1]]

        # Face lateral de espessura
        if right_faces_cam:
            side_poly = (r0[1], r0[2], r1[2], r1[1])
        else:
            side_poly = (r0[3], r0[0], r1[0], r1[3])
        if alpha < 255:
            pygame.draw.polygon(target_surf, (*c_side, alpha), side_poly)
        else:
            pygame.draw.polygon(target_surf, c_side, side_poly)

        # Face principal contínua (frente ou trás)
        if front_faces_cam:
            main_poly = (r0[0], r0[1], r1[1], r1[0])
        else:
            main_poly = (r0[2], r0[3], r1[3], r1[2])
        if alpha < 255:
            pygame.draw.polygon(target_surf, (*c_main, alpha), main_poly)
        else:
            pygame.draw.polygon(target_surf, c_main, main_poly)

        # Vincos de tecido / brilho de seda ao longo da fita (apenas para fitas com largura suficiente em tela)
        p00, p01, p11, p10 = main_poly
        w_top_px = math.hypot(p01[0] - p00[0], p01[1] - p00[1])
        w_bot_px = math.hypot(p11[0] - p10[0], p11[1] - p10[1])
        if min(w_top_px, w_bot_px) >= 6.0:
            mid_top = (int(p00[0] * 0.5 + p01[0] * 0.5), int(p00[1] * 0.5 + p01[1] * 0.5))
            mid_bot = (int(p10[0] * 0.5 + p11[0] * 0.5), int(p10[1] * 0.5 + p11[1] * 0.5))
            pygame.draw.line(target_surf, (*c_fold, alpha) if alpha < 255 else c_fold, mid_top, mid_bot, 1)
            sh_top = (int(p00[0] * 0.72 + p01[0] * 0.28), int(p00[1] * 0.72 + p01[1] * 0.28))
            sh_bot = (int(p10[0] * 0.72 + p11[0] * 0.28), int(p10[1] * 0.72 + p11[1] * 0.28))
            pygame.draw.line(target_surf, (*c_sheen, alpha) if alpha < 255 else c_sheen, sh_top, sh_bot, 1)

        # Contorno APENAS nas bordas laterais externas (sem linhas horizontais entre segmentos!)
        if outline and max(w_top_px, w_bot_px) >= 3.0:
            out_col = (*COLOR_OUTLINE, int(alpha * 0.75)) if alpha < 255 else COLOR_OUTLINE
            pygame.draw.line(target_surf, out_col, p00, p10, 1)
            pygame.draw.line(target_surf, out_col, p01, p11, 1)
            if i == 0:
                pygame.draw.line(target_surf, out_col, p00, p01, 1)
            if i == n - 2:
                pygame.draw.line(target_surf, out_col, p10, p11, 1)

    if alpha < 255:
        surface.blit(temp, (min_x, min_y), sub_rect)


def _draw_cranium_with_hair_facets(
    surface: pygame.Surface,
    camera,
    p_start: tuple[float, float, float],
    p_end: tuple[float, float, float],
    w_start: float,
    h_start: float,
    w_end: float,
    h_end: float,
    skin_color: tuple[int, int, int],
    hair_color: tuple[int, int, int],
    up: tuple[float, float, float] = (0.0, 0.0, 1.0),
    alpha: int = 255,
    t_hair_lat: float = 0.38,
    t_hair_mid: float = 0.54,
):
    """
    Renderiza o crânio 3D com facetas anatômicas integradas de cabelo e fronte:
    - O topo da cabeça (calota), a nuca (traseira) e as laterais (têmporas/orelhas) recebem cor de cabelo.
    - A fronte (face anterior) é dividida organicamente: metade superior com a risca da franja e metade inferior com a pele da testa.
    Isso impede 100% que apareçam 'calvícies' laterais ou que cabelos fiquem flutuando sobre a face.
    """
    ax = p_end[0] - p_start[0]
    ay = p_end[1] - p_start[1]
    az = p_end[2] - p_start[2]
    length = math.sqrt(ax * ax + ay * ay + az * az)
    if length < 1e-4:
        return
    ux, uy, uz = ax / length, ay / length, az / length

    dot = up[0] * ux + up[1] * uy + up[2] * uz
    wx = up[0] - dot * ux
    wy = up[1] - dot * uy
    wz = up[2] - dot * uz
    wlen = math.sqrt(wx * wx + wy * wy + wz * wz)
    if wlen < 1e-4:
        wx, wy, wz = 0.0, 1.0, 0.0
    else:
        wx /= wlen; wy /= wlen; wz /= wlen

    vx = uy * wz - uz * wy
    vy = uz * wx - ux * wz
    vz = ux * wy - uy * wx

    hw0, hh0 = w_start * 0.5, h_start * 0.5
    hw1, hh1 = w_end * 0.5, h_end * 0.5

    v3d = [
        (p_start[0] - vx * hw0 - wx * hh0, p_start[1] - vy * hw0 - wy * hh0, p_start[2] - vz * hw0 - wz * hh0), # 0: trás-esq
        (p_start[0] + vx * hw0 - wx * hh0, p_start[1] + vy * hw0 - wy * hh0, p_start[2] + vz * hw0 - wz * hh0), # 1: trás-dir
        (p_start[0] + vx * hw0 + wx * hh0, p_start[1] + vy * hw0 + wy * hh0, p_start[2] + vz * hw0 + wz * hh0), # 2: frente-dir
        (p_start[0] - vx * hw0 + wx * hh0, p_start[1] - vy * hw0 + wy * hh0, p_start[2] - vz * hw0 + wz * hh0), # 3: frente-esq
        (p_end[0] - vx * hw1 - wx * hh1, p_end[1] - vy * hw1 - wy * hh1, p_end[2] - vz * hw1 - wz * hh1),     # 4: topo-trás-esq
        (p_end[0] + vx * hw1 - wx * hh1, p_end[1] + vy * hw1 - wy * hh1, p_end[2] + vz * hw1 - wz * hh1),     # 5: topo-trás-dir
        (p_end[0] + vx * hw1 + wx * hh1, p_end[1] + vy * hw1 + wy * hh1, p_end[2] + vz * hw1 + wz * hh1),     # 6: topo-frente-dir
        (p_end[0] - vx * hw1 + wx * hh1, p_end[1] - vy * hw1 + wy * hh1, p_end[2] - vz * hw1 + wz * hh1),     # 7: topo-frente-esq
    ]

    scr = [camera.apply(p[0], p[1], p[2]) for p in v3d]
    azimuth = getattr(camera, "azimuth", 0.0)

    # Shading do cabelo
    c_hair_top = _clamp_color(hair_color, 1.15)
    c_hair_front = _clamp_color(hair_color, 1.02)
    c_hair_side = _clamp_color(hair_color, 0.85)
    c_hair_back = _clamp_color(hair_color, 0.70)

    # Shading da pele da testa
    c_skin_front = _clamp_color(skin_color, 1.05)

    # Hairline orgânica e graciosa: risca central sutil com mechas descendo pelas têmporas
    t_hair_swoop = (t_hair_lat + t_hair_mid) * 0.5

    hl_l = (v3d[3][0] * (1.0 - t_hair_lat) + v3d[7][0] * t_hair_lat,
            v3d[3][1] * (1.0 - t_hair_lat) + v3d[7][1] * t_hair_lat,
            v3d[3][2] * (1.0 - t_hair_lat) + v3d[7][2] * t_hair_lat)
    hl_r = (v3d[2][0] * (1.0 - t_hair_lat) + v3d[6][0] * t_hair_lat,
            v3d[2][1] * (1.0 - t_hair_lat) + v3d[6][1] * t_hair_lat,
            v3d[2][2] * (1.0 - t_hair_lat) + v3d[6][2] * t_hair_lat)

    v_mid_bot = ((v3d[3][0] + v3d[2][0]) * 0.5, (v3d[3][1] + v3d[2][1]) * 0.5, (v3d[3][2] + v3d[2][2]) * 0.5)
    v_mid_top = ((v3d[7][0] + v3d[6][0]) * 0.5, (v3d[7][1] + v3d[6][1]) * 0.5, (v3d[7][2] + v3d[6][2]) * 0.5)
    hl_m = (v_mid_bot[0] * (1.0 - t_hair_mid) + v_mid_top[0] * t_hair_mid,
            v_mid_bot[1] * (1.0 - t_hair_mid) + v_mid_top[1] * t_hair_mid,
            v_mid_bot[2] * (1.0 - t_hair_mid) + v_mid_top[2] * t_hair_mid)

    v_ml_bot = (v3d[3][0] * 0.75 + v3d[2][0] * 0.25, v3d[3][1] * 0.75 + v3d[2][1] * 0.25, v3d[3][2] * 0.75 + v3d[2][2] * 0.25)
    v_ml_top = (v3d[7][0] * 0.75 + v3d[6][0] * 0.25, v3d[7][1] * 0.75 + v3d[6][1] * 0.25, v3d[7][2] * 0.75 + v3d[6][2] * 0.25)
    hl_ml = (v_ml_bot[0] * (1.0 - t_hair_swoop) + v_ml_top[0] * t_hair_swoop,
             v_ml_bot[1] * (1.0 - t_hair_swoop) + v_ml_top[1] * t_hair_swoop,
             v_ml_bot[2] * (1.0 - t_hair_swoop) + v_ml_top[2] * t_hair_swoop)

    v_mr_bot = (v3d[3][0] * 0.25 + v3d[2][0] * 0.75, v3d[3][1] * 0.25 + v3d[2][1] * 0.75, v3d[3][2] * 0.25 + v3d[2][2] * 0.75)
    v_mr_top = (v3d[7][0] * 0.25 + v3d[6][0] * 0.75, v3d[7][1] * 0.25 + v3d[6][1] * 0.75, v3d[7][2] * 0.25 + v3d[6][2] * 0.75)
    hl_mr = (v_mr_bot[0] * (1.0 - t_hair_swoop) + v_mr_top[0] * t_hair_swoop,
             v_mr_bot[1] * (1.0 - t_hair_swoop) + v_mr_top[1] * t_hair_swoop,
             v_mr_bot[2] * (1.0 - t_hair_swoop) + v_mr_top[2] * t_hair_swoop)

    s_hl_l = camera.apply(hl_l[0], hl_l[1], hl_l[2])
    s_hl_r = camera.apply(hl_r[0], hl_r[1], hl_r[2])
    s_hl_m = camera.apply(hl_m[0], hl_m[1], hl_m[2])
    s_hl_ml = camera.apply(hl_ml[0], hl_ml[1], hl_ml[2])
    s_hl_mr = camera.apply(hl_mr[0], hl_mr[1], hl_mr[2])

    faces = []
    # 1. Topo da cabeça (cabelo)
    cx = sum(v3d[i][0] for i in (4, 5, 6, 7)) * 0.25
    cy = sum(v3d[i][1] for i in (4, 5, 6, 7)) * 0.25
    cz = sum(v3d[i][2] for i in (4, 5, 6, 7)) * 0.25
    rx, ry = rotate_xy(cx, cy, azimuth)
    faces.append((rx + ry + cz * 0.45, [scr[4], scr[5], scr[6], scr[7]], c_hair_top))

    # 2. Nuca / Costas (cabelo)
    cx = sum(v3d[i][0] for i in (0, 1, 5, 4)) * 0.25
    cy = sum(v3d[i][1] for i in (0, 1, 5, 4)) * 0.25
    cz = sum(v3d[i][2] for i in (0, 1, 5, 4)) * 0.25
    rx, ry = rotate_xy(cx, cy, azimuth)
    faces.append((rx + ry + cz * 0.45, [scr[0], scr[1], scr[5], scr[4]], c_hair_back))

    # 3. Lado Direito (têmpora / orelha - cabelo)
    cx = sum(v3d[i][0] for i in (1, 2, 6, 5)) * 0.25
    cy = sum(v3d[i][1] for i in (1, 2, 6, 5)) * 0.25
    cz = sum(v3d[i][2] for i in (1, 2, 6, 5)) * 0.25
    rx, ry = rotate_xy(cx, cy, azimuth)
    faces.append((rx + ry + cz * 0.45, [scr[1], scr[2], scr[6], scr[5]], c_hair_side))

    # 4. Lado Esquerdo (têmpora / orelha - cabelo)
    cx = sum(v3d[i][0] for i in (0, 3, 7, 4)) * 0.25
    cy = sum(v3d[i][1] for i in (0, 3, 7, 4)) * 0.25
    cz = sum(v3d[i][2] for i in (0, 3, 7, 4)) * 0.25
    rx, ry = rotate_xy(cx, cy, azimuth)
    faces.append((rx + ry + cz * 0.45, [scr[0], scr[3], scr[7], scr[4]], c_hair_side))

    # 5. Fronte: Cabelo da Franja (topo da face anterior)
    cx = (hl_m[0] + v_mid_top[0]) * 0.5
    cy = (hl_m[1] + v_mid_top[1]) * 0.5
    cz = (hl_m[2] + v_mid_top[2]) * 0.5
    rx, ry = rotate_xy(cx, cy, azimuth)
    faces.append((rx + ry + cz * 0.45, [s_hl_l, s_hl_ml, s_hl_m, s_hl_mr, s_hl_r, scr[6], scr[7]], c_hair_front))

    # 6. Fronte: Pele da Testa (abaixo da linha da franja)
    cx = (hl_m[0] + v_mid_bot[0]) * 0.5
    cy = (hl_m[1] + v_mid_bot[1]) * 0.5
    cz = (hl_m[2] + v_mid_bot[2]) * 0.5
    rx, ry = rotate_xy(cx, cy, azimuth)
    faces.append((rx + ry + cz * 0.45, [scr[3], scr[2], s_hl_r, s_hl_mr, s_hl_m, s_hl_ml, s_hl_l], c_skin_front))

    faces.sort(key=lambda f: f[0])
    for _, poly, col in faces:
        pygame.draw.polygon(surface, col, poly)


def draw_sculpted_head_3d(
    surface: pygame.Surface,
    camera,
    base_x: float,
    base_y: float,
    head_z: float,
    head_w: float,
    fx: float,
    fy: float,
    px: float,
    py: float,
    skin_color: tuple[int, int, int],
    skin_shadow: tuple[int, int, int],
    hair_color: tuple[int, int, int] | None = None,
    alpha: int = 255,
    hairline_mid: float = 0.54,
    hairline_lat: float = 0.38,
    jaw_color: tuple[int, int, int] | None = None,
):
    """
    Desenha uma cabeça humana 3D esculpida em duas seções contínuas:
    - Mandíbula/queixo afunilado na base (frustum 3D estreitando em direção ao queixo).
    - Crânio superior proporcionado com maçãs do rosto definidas e facetas integradas de cabelo.
    """
    # 1. Mandíbula e queixo afunilados (z: head_z -> head_z + 0.065)
    jaw_bottom = (base_x + fx * 0.012, base_y + fy * 0.012, head_z + 0.005)
    jaw_top = (base_x + fx * 0.004, base_y + fy * 0.004, head_z + 0.068)
    draw_tapered_frustum_3d(
        surface, camera,
        jaw_bottom, jaw_top,
        w_start=head_w * 0.70, h_start=head_w * 0.74,
        w_end=head_w * 0.96, h_end=head_w * 0.96,
        color=jaw_color if jaw_color is not None else skin_color,
        up=(fx, fy, 0.0),
        outline=False,
        alpha=alpha,
        cap_end=False,  # O crânio se apoia sobre o topo da mandíbula; sem tampa horizontal visível
    )
    # 2. Crânio superior e têmporas (z: head_z + 0.055 -> head_z + 0.168)
    cran_bottom = (base_x, base_y, head_z + 0.055)
    cran_top = (base_x - fx * 0.004, base_y - fy * 0.004, head_z + 0.168)
    if hair_color is not None:
        _draw_cranium_with_hair_facets(
            surface, camera,
            cran_bottom, cran_top,
            head_w * 1.0, head_w * 1.0,
            head_w * 0.92, head_w * 0.94,
            skin_color=skin_color,
            hair_color=hair_color,
            up=(fx, fy, 0.0),
            alpha=alpha,
            t_hair_lat=hairline_lat,
            t_hair_mid=hairline_mid,
        )
    else:
        draw_tapered_frustum_3d(
            surface, camera,
            cran_bottom, cran_top,
            w_start=head_w * 1.0, h_start=head_w * 1.0,
            w_end=head_w * 0.92, h_end=head_w * 0.94,
            color=skin_color,
            up=(fx, fy, 0.0),
            outline=False,
            alpha=alpha,
        )


# Paleta de feições faciais dos retratos por personagem
PORTRAIT_FACE_STYLES = {
    "kenshin": {
        "iris": (198, 108, 36), "iris_core": (255, 198, 72), "iris_limbal": (96, 42, 18),
        "brow": (118, 54, 34), "lip": (208, 86, 96), "lip_lower": (234, 118, 128), "lip_shadow": (145, 52, 62),
        "brow_tilt": 0.14, "lashes": True, "feminine_lips": True, "hd_anime_eyes": True,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
        "hairline_mid": 0.65, "hairline_lat": 0.48,
    },
    "kenshi": {
        "iris": (198, 108, 36), "iris_core": (255, 198, 72), "iris_limbal": (96, 42, 18),
        "brow": (118, 54, 34), "lip": (208, 86, 96), "lip_lower": (234, 118, 128), "lip_shadow": (145, 52, 62),
        "brow_tilt": 0.14, "lashes": True, "feminine_lips": True, "hd_anime_eyes": True,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
        "hairline_mid": 0.65, "hairline_lat": 0.48,
    },
    "musashi": {
        "iris": (52, 68, 92), "iris_core": (102, 138, 185), "iris_limbal": (24, 34, 48),
        "brow": (28, 28, 32), "lip": (172, 120, 108),
        "brow_tilt": 0.28, "stubble": True, "delicate_nose": False,
        "eye_z": 0.080, "brow_z": 0.104, "spacing": 0.036,
    },
    "saitou": {
        "iris": (215, 168, 42), "iris_core": (245, 205, 95), "iris_limbal": (75, 55, 18),
        "brow": (24, 28, 38), "lip": (182, 138, 124),
        "brow_tilt": 0.30, "delicate_nose": False,
        "eye_z": 0.080, "brow_z": 0.104, "spacing": 0.036, "mouth_w": 0.026,
    },
    "okuni": {
        "iris": (185, 36, 52), "iris_core": (245, 120, 140), "iris_limbal": (85, 16, 24),
        "brow": (28, 18, 22), "lip": (215, 30, 52), "lip_lower": (245, 60, 80), "lip_shadow": (145, 20, 36),
        "brow_tilt": 0.12, "kumadori": True, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "kasumi": {
        "iris": (86, 152, 178), "iris_core": (175, 222, 248), "iris_limbal": (38, 64, 88),
        "brow": (88, 94, 108), "lip": (205, 115, 125), "lip_lower": (228, 138, 148), "lip_shadow": (142, 68, 74),
        "brow_tilt": 0.16, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "murasaki": {
        "iris": (188, 88, 235), "iris_core": (245, 215, 255), "iris_limbal": (58, 24, 78),
        "brow": (32, 20, 42), "lip": (188, 78, 128),
        "mask": (118, 52, 172), "mask_light": (172, 98, 234),
        "brow_tilt": 0.22, "lashes": True, "delicate_nose": True,
        "hairline_mid": 0.62, "hairline_lat": 0.44,
    },
    "tomoe": {
        "iris": (75, 48, 38), "iris_core": (185, 125, 95), "iris_limbal": (38, 24, 18),
        "brow": (34, 26, 28), "lip": (212, 95, 105), "lip_lower": (235, 125, 135), "lip_shadow": (142, 60, 70),
        "brow_tilt": 0.10, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "pirate": {
        "iris": (45, 148, 112), "iris_core": (85, 215, 168), "iris_limbal": (22, 70, 52),
        "brow": (128, 56, 32), "lip": (204, 78, 82), "lip_lower": (235, 110, 115), "lip_shadow": (145, 45, 50),
        "brow_tilt": 0.20, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "musketeer": {
        "iris": (48, 120, 210), "iris_core": (110, 185, 255), "iris_limbal": (24, 60, 120),
        "brow": (145, 78, 46), "lip": (214, 92, 106), "lip_lower": (240, 128, 140), "lip_shadow": (148, 55, 68),
        "brow_tilt": 0.14, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "ren": {
        "iris": (82, 54, 38), "iris_core": (152, 112, 75), "iris_limbal": (36, 24, 18),
        "brow": (38, 30, 26), "lip": (186, 134, 118),
        "brow_tilt": 0.26, "delicate_nose": False,
        "eye_z": 0.080, "brow_z": 0.104, "spacing": 0.036, "mouth_w": 0.026,
    },
    "chiyo": {
        "iris": (218, 142, 36), "iris_core": (255, 192, 75), "iris_limbal": (88, 52, 16),
        "brow": (28, 24, 30), "lip": (204, 68, 82), "lip_lower": (235, 102, 115), "lip_shadow": (142, 40, 52),
        "brow_tilt": 0.18, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "benkei": {
        "iris": (58, 42, 32), "iris_core": (118, 88, 62), "iris_limbal": (24, 18, 16),
        "brow": (24, 20, 20), "lip": (162, 112, 98),
        "brow_tilt": 0.32, "stubble": True, "beard": True, "beard_col": (32, 28, 26),
        "delicate_nose": False,
        "eye_z": 0.080, "brow_z": 0.104, "spacing": 0.038,
    },
    "orin": {
        "iris": (158, 82, 172), "iris_core": (224, 156, 238), "iris_limbal": (64, 24, 75),
        "brow": (34, 24, 38), "lip": (218, 42, 68), "lip_lower": (248, 72, 98), "lip_shadow": (148, 22, 42),
        "brow_tilt": 0.10, "kumadori": True, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.66, "hairline_lat": 0.48,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "goro": {
        "iris": (68, 48, 34), "iris_core": (118, 88, 62), "iris_limbal": (28, 20, 16),
        "brow": (38, 32, 28), "lip": (172, 122, 106),
        "brow_tilt": 0.28, "stubble": True, "delicate_nose": False,
        "eye_z": 0.080, "brow_z": 0.104, "spacing": 0.038, "mouth_w": 0.028,
    },
    "ichi": {
        "iris": (185, 198, 225), "iris_core": (245, 250, 255), "iris_limbal": (120, 135, 160),
        "brow": (36, 28, 32), "lip": (208, 108, 118), "lip_lower": (232, 138, 148), "lip_shadow": (140, 62, 72),
        "brow_tilt": -0.02, "blind_eyes": True, "lashes": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "rifleman": {
        "iris": (68, 50, 38), "iris_core": (115, 88, 62), "iris_limbal": (32, 24, 18),
        "brow": (36, 30, 28), "lip": (178, 132, 116),
        "brow_tilt": 0.25, "stubble": True, "delicate_nose": False,
        "eye_z": 0.078, "brow_z": 0.102, "spacing": 0.035,
        "chin_strap": True, "strap_col": (225, 215, 195),
    },
    "teppo": {
        "iris": (68, 50, 38), "iris_core": (115, 88, 62), "iris_limbal": (32, 24, 18),
        "brow": (36, 30, 28), "lip": (178, 132, 116),
        "brow_tilt": 0.25, "stubble": True, "delicate_nose": False,
        "eye_z": 0.078, "brow_z": 0.102, "spacing": 0.035,
        "chin_strap": True, "strap_col": (225, 215, 195),
    },
    "ninja": {
        "iris": (235, 185, 45), "iris_core": (255, 225, 95), "iris_limbal": (75, 50, 15),
        "brow": (24, 20, 22), "lip": (172, 118, 108),
        "mask": (28, 24, 30), "mask_light": (45, 40, 48),
        "brow_tilt": 0.28, "delicate_nose": False,
        "eye_z": 0.076, "brow_z": 0.096, "spacing": 0.035,
        "hairline_mid": 0.48, "hairline_lat": 0.38,
    },
    "hanzo": {
        "iris": (235, 185, 45), "iris_core": (255, 225, 95), "iris_limbal": (75, 50, 15),
        "brow": (24, 20, 22), "lip": (172, 118, 108),
        "mask": (28, 24, 30), "mask_light": (45, 40, 48),
        "brow_tilt": 0.28, "delicate_nose": False,
        "eye_z": 0.076, "brow_z": 0.096, "spacing": 0.035,
        "hairline_mid": 0.48, "hairline_lat": 0.38,
    },
    "american": {
        "iris": (75, 110, 140), "iris_core": (120, 180, 225), "iris_limbal": (32, 50, 70),
        "brow": (55, 40, 30), "lip": (180, 125, 115),
        "brow_tilt": 0.22, "mask": (26, 27, 31), "mask_light": (46, 48, 56),
        "delicate_nose": False, "eye_z": 0.068, "brow_z": 0.082, "spacing": 0.034,
    },
    "joe": {
        "iris": (75, 110, 140), "iris_core": (120, 180, 225), "iris_limbal": (32, 50, 70),
        "brow": (55, 40, 30), "lip": (180, 125, 115),
        "brow_tilt": 0.22, "mask": (26, 27, 31), "mask_light": (46, 48, 56),
        "delicate_nose": False, "eye_z": 0.068, "brow_z": 0.082, "spacing": 0.034,
    },
    "anne": {
        "iris": (45, 148, 112), "iris_core": (85, 215, 168), "iris_limbal": (22, 70, 52),
        "brow": (128, 56, 32), "lip": (204, 78, 82), "lip_lower": (235, 110, 115), "lip_shadow": (145, 45, 50),
        "brow_tilt": 0.20, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "julie": {
        "iris": (48, 120, 210), "iris_core": (110, 185, 255), "iris_limbal": (24, 60, 120),
        "brow": (145, 78, 46), "lip": (214, 92, 106), "lip_lower": (240, 128, 140), "lip_shadow": (148, 55, 68),
        "brow_tilt": 0.14, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "boss": {
        "iris": (255, 65, 35), "brow": (20, 15, 15), "lip": (145, 30, 35),
        "brow_tilt": 0.42,
    },
    "oni": {
        "iris": (255, 65, 35), "brow": (20, 15, 15), "lip": (145, 30, 35),
        "brow_tilt": 0.42,
    },
    "valerius": {
        "iris": (130, 165, 195), "iris_core": (195, 225, 245), "iris_limbal": (50, 75, 100),
        "brow": (160, 168, 178), "lip": (175, 135, 138),
        "brow_tilt": 0.28, "delicate_nose": False,
        "eye_z": 0.080, "brow_z": 0.104, "spacing": 0.036, "mouth_w": 0.025,
        "hairline_mid": 0.68, "hairline_lat": 0.52,
    },
    "seimei": {
        "iris": (135, 115, 215), "iris_core": (195, 175, 255), "iris_limbal": (55, 40, 115),
        "brow": (32, 24, 38), "lip": (225, 110, 128), "lip_lower": (245, 140, 155), "lip_shadow": (148, 62, 75),
        "brow_tilt": 0.12, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "daiki": {
        "iris": (82, 54, 34), "iris_core": (145, 98, 56), "iris_limbal": (36, 22, 14),
        "brow": (24, 20, 18), "lip": (172, 118, 104),
        "brow_tilt": 0.26, "delicate_nose": False,
        "eye_z": 0.080, "brow_z": 0.102, "spacing": 0.035, "mouth_w": 0.026,
        "hairline_mid": 0.66, "hairline_lat": 0.48,
    },
    "aoi": {
        "iris": (168, 102, 38), "iris_core": (235, 175, 78), "iris_limbal": (78, 42, 18),
        "brow": (28, 22, 26), "lip": (218, 104, 112), "lip_lower": (242, 134, 142), "lip_shadow": (148, 58, 66),
        "brow_tilt": 0.16, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.106, "spacing": 0.033, "mouth_w": 0.024,
    },
    "raiden": {
        # Olhar marcial estóico e intimidador de Yokozuna no tachiai (olhos amendoados focados, íris âmbar-escura)
        "iris": (72, 45, 26), "iris_core": (150, 95, 45), "iris_limbal": (24, 16, 12),
        "brow": (22, 18, 16), "lip": (168, 112, 98),
        "brow_tilt": 0.30, "delicate_nose": False,
        "eye_z": 0.076, "brow_z": 0.098, "spacing": 0.038, "mouth_w": 0.030,
        "hairline_mid": 0.68, "hairline_lat": 0.50,
    },
    "hendrika": {
        # Olhar calculista, inquisitivo e excêntrico de "mad scientist" (íris turquesa brilhante com núcleo elétrico e faísca)
        "iris": (38, 165, 175), "iris_core": (140, 245, 250), "iris_limbal": (16, 68, 75),
        "brow": (160, 105, 52), "lip": (224, 96, 114), "lip_lower": (248, 138, 150), "lip_shadow": (155, 52, 68),
        "brow_tilt": 0.10, "lashes": True, "delicate_nose": True, "feminine_lips": True,
        "hairline_mid": 0.65, "hairline_lat": 0.46,
        "eye_z": 0.082, "brow_z": 0.108, "spacing": 0.033, "mouth_w": 0.024,
    },
}


import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_PORTRAIT_DECALS: dict[str, pygame.Surface] = {}


def get_portrait_face_decal(char_type: str) -> pygame.Surface | None:
    """Carrega o decalque facial de alta resolução extraído do retrato oficial do lutador."""
    if not char_type:
        return None
    key = char_type.lower()
    if key in _PORTRAIT_DECALS:
        return _PORTRAIT_DECALS[key]

    decal_path = os.path.join(ROOT, "assets", "portraits", "decals", f"{key}_face_decal.png")
    if os.path.exists(decal_path):
        surf = pygame.image.load(decal_path).convert_alpha()
        _PORTRAIT_DECALS[key] = surf
        return surf
    return None


def draw_portrait_face_3d(
    c,
    char_type: str = "",
    eye: tuple[int, int, int] | None = None,
    brow: tuple[int, int, int] | None = None,
    mouth: tuple[int, int, int] | None = None,
    skin_shadow: tuple[int, int, int] | None = None,
    eye_z: float = 0.088,
    brow_z: float = 0.128,
    spacing: float = 0.036,
    brow_tilt: float | None = None,
    mouth_w: float = 0.026,
    nose: bool = True,
):
    """
    Desenha as feições faciais projetadas em 3D sobre o plano frontal da cabeça:
    - Se houver decalque facial oficial do retrato (`assets/portraits/decals/{char}_face_decal.png`),
      ele é mapeado e projetado no plano 3D com rotação, escala e oclusão de visão isométrica.
    - Caso contrário, desenha feições anatômicas painterly procedurais em multicamadas.
    """
    if getattr(c, "alpha", 255) < 80:
        return
    rx, ry = rotate_xy(c.fx, c.fy, getattr(c, "azimuth", 0.0))
    if rx + ry <= -0.10:
        return

    bx, by, hz = c.base_x, c.base_y, c.head_z
    fx, fy, px, py = c.fx, c.fy, c.px, c.py
    front_dist = c.head_w * 0.50 + 0.008

    # -------------------------------------------------------------------------------------------------
    # Arquitetura Facial Low-Poly Facetada estilo Tekken 2/3 (PS1)
    # - Geometria puramente poligonal em 3D (sem círculos 2D e sem decalques planos)
    # - Órbitas oculares recuadas e sombreadas em 3D
    # - Olhos amendoados anatômicos com esclera facetada, íris poligonal e delineado maduro
    # - Nariz em prisma 3D saliente com facetas laterais iluminadas e sombreadas conforme o ângulo
    # - Lábios facetados em 3 planos: arco de cupido superior, plano inferior iluminado e fenda oral
    # -------------------------------------------------------------------------------------------------
    style = PORTRAIT_FACE_STYLES.get(char_type, {})
    iris_col = eye or style.get("iris", (52, 38, 34))
    brow_col = brow or style.get("brow", (38, 30, 28))
    lip_col = mouth or style.get("lip", (182, 110, 115))
    shadow_col = skin_shadow or (175, 142, 130)
    tilt = brow_tilt if brow_tilt is not None else style.get("brow_tilt", 0.18)
    eye_z = style.get("eye_z", eye_z)
    brow_z = style.get("brow_z", brow_z)
    spacing = style.get("spacing", spacing)
    mouth_w = style.get("mouth_w", mouth_w)

    state = getattr(c, "state", "IDLE")
    extra_props = getattr(c, "extra_props", None) or {}
    pose_name = extra_props.get("pose", "")
    eyes_closed = bool(extra_props.get("eyes_closed", False) or pose_name == "meditation_eyes_closed")
    eye_glint_boost = float(extra_props.get("eye_glint_boost", 0.0))
    if pose_name == "koiguchi_glint":
        eye_glint_boost = max(eye_glint_boost, 1.0)

    is_fierce = getattr(c, "is_melee", False) or state in ("ATTACK", "IAI_STARTUP", "RYUU_TSUI_SEN", "GATOTSU_CHARGE", "ZEROSHIKI")
    is_shocked = state in ("DYING_FREEZE", "STUNNED")
    if is_fierce:
        tilt += 0.16
    elif is_shocked:
        tilt -= 0.14

    # Projeção 3D com profundidade lateral e saliência para frente
    def _p3(lat: float, z_off: float, fwd: float = 0.0) -> tuple[int, int]:
        d = front_dist + fwd
        return c.camera.apply(
            bx + fx * d + px * lat,
            by + fy * d + py * lat,
            hz + z_off,
        )

    surface = c.surface
    cam_lateral = (rx - ry) / 1.414  # > 0 se o lado direito do rosto estiver voltado para a câmera

    # Escala e espessuras proporcionais
    p_ref_top = _p3(0.0, 0.10)
    p_ref_bot = _p3(0.0, 0.0)
    scale_px = max(1.0, math.hypot(p_ref_top[0] - p_ref_bot[0], p_ref_top[1] - p_ref_bot[1]))
    lash_thick = max(1, min(2, int(scale_px * 0.014)))
    brow_thick = max(1, min(2, int(scale_px * 0.016)))

    # Base da pele
    col_base_skin = getattr(c, "skin", (212, 185, 172)) if hasattr(c, "skin") else (212, 185, 172)
    is_female_char = style.get("lashes", False) or style.get("feminine_lips", False) or (
        char_type.lower() in (
            "kasumi", "gray", "murasaki", "purple",
            "okuni", "kabuki", "tomoe", "archer", "anne", "pirate", "julie", "musketeer",
            "chiyo", "nodachi", "orin", "o-rin", "shamisen", "ichi", "blind", "shikomizue",
            "aoi", "hendrika", "alchemist"
        )
    )
    is_male = not is_female_char

    # 1. Olhos Expressivos (Femininos: Luminosos e Abertos; Masculinos: Marciais, Focados e Penetráveis)
    for s in (-1.0, 1.0):
        if eyes_closed:
            # Olhos fechados em meditação serena (curva graciosa de cílios fechados)
            p_cl_in = _p3(spacing * 0.48 * s, eye_z - 0.002, 0.003)
            p_cl_mid = _p3(spacing * 1.05 * s, eye_z - 0.005, 0.004)
            p_cl_out = _p3(spacing * 1.62 * s, eye_z - 0.001, 0.003)
            lash_col = (24, 18, 22)
            pygame.draw.lines(surface, lash_col, False, [p_cl_in, p_cl_mid, p_cl_out], max(1, lash_thick))
            if not is_male:
                p_wing = _p3(spacing * 1.70 * s, eye_z + 0.004, 0.003)
                pygame.draw.line(surface, lash_col, p_cl_out, p_wing, max(1, lash_thick))
            b_z_base = brow_z if brow_z is not None else (eye_z + (0.022 if is_male else 0.026))
            b_z = max(b_z_base, eye_z + (0.020 if is_male else 0.025))
            b_in = _p3(spacing * 0.48 * s, b_z - 0.002, 0.004)
            b_mid = _p3(spacing * 1.00 * s, b_z + 0.003, 0.005)
            b_out = _p3(spacing * 1.50 * s, b_z - 0.002, 0.003)
            pygame.draw.lines(surface, brow_col, False, [b_in, b_mid, b_out], max(1, brow_thick) if is_male else 1)
            continue

        if is_male:
            # Olhar masculino marcial: fenda nítida, mirada resoluta de guerreiro/atirador com esclera marfim visível
            p_in = _p3(spacing * 0.46 * s, eye_z - 0.001, 0.002)
            p_top_in = _p3(spacing * 0.72 * s, eye_z + 0.007, 0.003)
            p_top_mid = _p3(spacing * 1.04 * s, eye_z + 0.008, 0.003)
            p_top_out = _p3(spacing * 1.36 * s, eye_z + 0.006, 0.003)
            p_out = _p3(spacing * 1.58 * s, eye_z - 0.001, 0.002)
            p_bot_out = _p3(spacing * 1.36 * s, eye_z - 0.006, 0.002)
            p_bot_mid = _p3(spacing * 1.04 * s, eye_z - 0.007, 0.002)
            p_bot_in = _p3(spacing * 0.72 * s, eye_z - 0.005, 0.002)
            ir_w = 0.010
            ir_h = 0.009
        else:
            # Vértices da esclera amendoada expressiva, ampla e aberta (feminina)
            ap_top_mod = -0.002 if is_fierce else (0.003 if is_shocked else 0.0)
            p_in = _p3(spacing * 0.48 * s, eye_z - 0.001, 0.002)
            p_top_in = _p3(spacing * 0.72 * s, eye_z + 0.012 + ap_top_mod, 0.003)
            p_top_mid = _p3(spacing * 1.05 * s, eye_z + 0.016 + ap_top_mod, 0.003)
            p_top_out = _p3(spacing * 1.36 * s, eye_z + 0.010 + ap_top_mod * 0.5, 0.003)
            p_out = _p3(spacing * 1.62 * s, eye_z + 0.002, 0.002)
            p_bot_out = _p3(spacing * 1.36 * s, eye_z - 0.008, 0.002)
            p_bot_mid = _p3(spacing * 1.05 * s, eye_z - 0.010, 0.002)
            p_bot_in = _p3(spacing * 0.72 * s, eye_z - 0.007, 0.002)
            ir_w = 0.0125 * (0.86 if is_shocked else 1.0)
            ir_h = 0.0135 * (0.86 if is_shocked else 1.0)

        # Esclera límpida, marfim brilhante (sempre visível nas laterais do olho)
        sclera_poly = [p_in, p_top_in, p_top_mid, p_top_out, p_out, p_bot_out, p_bot_mid, p_bot_in]
        pygame.draw.polygon(surface, (255, 252, 248), sclera_poly)

        # Íris (Facetada, Proporcional e Radiante)
        ir_x = spacing * 1.05 * s
        ir_y = eye_z + (0.000 if is_male else 0.001)

        # Anel límbico externo de alta definição (HD Anime Eye Ring)
        if style.get("hd_anime_eyes", False):
            limbal_col = style.get("iris_limbal", (88, 40, 24))
            lw, lh = ir_w * 1.12, ir_h * 1.08
            limbal_poly = [
                _p3(ir_x - lw * 0.50, ir_y, 0.0026),
                _p3(ir_x - lw * 0.38, ir_y + lh * 0.70, 0.0026),
                _p3(ir_x + lw * 0.38, ir_y + lh * 0.70, 0.0026),
                _p3(ir_x + lw * 0.50, ir_y, 0.0026),
                _p3(ir_x + lw * 0.38, ir_y - lh * 0.70, 0.0026),
                _p3(ir_x - lw * 0.38, ir_y - lh * 0.70, 0.0026),
            ]
            pygame.draw.polygon(surface, limbal_col, limbal_poly)

        # Corpo principal da íris (cor viva e translúcida)
        ir_p0 = _p3(ir_x - ir_w * 0.50, ir_y, 0.003)
        ir_p1 = _p3(ir_x - ir_w * 0.38, ir_y + ir_h * 0.70, 0.003)
        ir_p2 = _p3(ir_x + ir_w * 0.38, ir_y + ir_h * 0.70, 0.003)
        ir_p3 = _p3(ir_x + ir_w * 0.50, ir_y, 0.003)
        ir_p4 = _p3(ir_x + ir_w * 0.38, ir_y - ir_h * 0.70, 0.003)
        ir_p5 = _p3(ir_x - ir_w * 0.38, ir_y - ir_h * 0.70, 0.003)
        iris_poly = [ir_p0, ir_p1, ir_p2, ir_p3, ir_p4, ir_p5]
        pygame.draw.polygon(surface, iris_col, iris_poly)

        # Gradiente âmbar/mel na meia-lua inferior da íris (HD Anime Eye)
        if style.get("hd_anime_eyes", False):
            honey_col = style.get("iris_core", (255, 198, 72))
            crescent_poly = [
                ir_p0,
                _p3(ir_x, ir_y - ir_h * 0.15, 0.0035),
                ir_p3,
                ir_p4,
                ir_p5,
            ]
            pygame.draw.polygon(surface, honey_col, crescent_poly)

        # Pupila central compacta
        pupil_scale = 0.34 if is_shocked else (0.38 if is_fierce else 0.44)
        pupil_w, pupil_h = ir_w * pupil_scale, ir_h * pupil_scale
        pupil_poly = [
            _p3(ir_x - pupil_w * 0.5, ir_y, 0.004),
            _p3(ir_x - pupil_w * 0.3, ir_y + pupil_h * 0.6, 0.004),
            _p3(ir_x + pupil_w * 0.3, ir_y + pupil_h * 0.6, 0.004),
            _p3(ir_x + pupil_w * 0.5, ir_y, 0.004),
            _p3(ir_x + pupil_w * 0.3, ir_y - pupil_h * 0.6, 0.004),
            _p3(ir_x - pupil_w * 0.3, ir_y - pupil_h * 0.6, 0.004),
        ]
        pupil_col = style.get("pupil", (24, 20, 26))
        pygame.draw.polygon(surface, pupil_col, pupil_poly)

        # Núcleo brilhante da íris (profundidade anime)
        core_col = style.get("iris_core", (242, 248, 255))
        core_w, core_h = ir_w * 0.32, ir_h * 0.32
        core_poly = [
            _p3(ir_x - core_w * 0.5, ir_y - 0.001, 0.005),
            _p3(ir_x, ir_y + core_h * 0.5, 0.005),
            _p3(ir_x + core_w * 0.5, ir_y - 0.001, 0.005),
            _p3(ir_x, ir_y - core_h * 0.5, 0.005),
        ]
        pygame.draw.polygon(surface, core_col, core_poly)

        # Brilho Especular Principal (Glint / Catchlight no topo da íris)
        glint_scale = 1.0 + 0.35 * eye_glint_boost
        sp_poly = [
            _p3(ir_x + ir_w * 0.08, ir_y + ir_h * (0.10 if is_male else 0.16), 0.006),
            _p3(ir_x + ir_w * (0.38 * glint_scale), ir_y + ir_h * (0.10 if is_male else 0.16), 0.006),
            _p3(ir_x + ir_w * (0.38 * glint_scale), ir_y + ir_h * ((0.44 if is_male else 0.50) * glint_scale), 0.006),
            _p3(ir_x + ir_w * 0.08, ir_y + ir_h * ((0.44 if is_male else 0.50) * glint_scale), 0.006),
        ]
        pygame.draw.polygon(surface, (255, 255, 255), sp_poly)

        # Segundo ponto de luz anime (brilho doce no canto inferior - apenas feminino)
        if not is_male:
            sp2_poly = [
                _p3(ir_x - ir_w * 0.32, ir_y - ir_h * 0.38, 0.006),
                _p3(ir_x - ir_w * 0.14, ir_y - ir_h * 0.38, 0.006),
                _p3(ir_x - ir_w * 0.14, ir_y - ir_h * 0.20, 0.006),
                _p3(ir_x - ir_w * 0.32, ir_y - ir_h * 0.20, 0.006),
            ]
            pygame.draw.polygon(surface, (255, 252, 235) if eye_glint_boost > 0 else (255, 255, 255), sp2_poly)

        # Delineador Superior Nítido (Lashline: reta e imponente para homens; alada graciosa para mulheres; borda inferior aberta)
        lash_col = (20, 16, 22)
        pygame.draw.lines(surface, lash_col, False, [p_in, p_top_in, p_top_mid, p_top_out, p_out], lash_thick)
        if not is_male:
            p_wing = _p3(spacing * 1.68 * s, eye_z + 0.008, 0.003)
            pygame.draw.polygon(surface, lash_col, [p_top_out, p_out, p_wing])
            if style.get("kumadori", False):
                # Linha carmim Kumadori alada varrendo a têmpora
                p_kuma0 = _p3(spacing * 1.15 * s, eye_z + 0.010, 0.003)
                p_kuma1 = _p3(spacing * 1.82 * s, eye_z + 0.015, 0.003)
                p_kuma2 = _p3(spacing * 1.55 * s, eye_z - 0.005, 0.003)
                pygame.draw.lines(surface, (212, 32, 54), False, [p_kuma0, p_kuma1], lash_thick)
                pygame.draw.line(surface, (185, 24, 44), p_out, p_kuma2, max(1, lash_thick - 1))

        # Sobrancelha (Descolada do olho com espaçamento anatômico seguro para nunca fundir com a esclera)
        b_z_base = brow_z if brow_z is not None else (eye_z + (0.022 if is_male else 0.026))
        b_z = max(b_z_base, eye_z + (0.020 if is_male else 0.025))
        b_in = _p3(spacing * 0.48 * s, b_z - 0.001 - tilt * 0.008, 0.004)
        b_mid = _p3(spacing * 1.00 * s, b_z + (0.003 if is_male else 0.005) + tilt * 0.006, 0.005)
        b_out = _p3(spacing * 1.50 * s, b_z - (0.004 if is_male else 0.002) + tilt * 0.010, 0.003)
        b_thick = max(1, brow_thick) if is_male else 1
        pygame.draw.lines(surface, brow_col, False, [b_in, b_mid, b_out], b_thick)

    # 3. Nariz em Prisma 3D Saliente (Low-Poly 3D Wedge Protrusion com Sombreamento Direcional)
    if nose:
        is_delicate = style.get("delicate_nose", False) or style.get("feminine_lips", False) or (
            char_type.lower() in (
                "kenshin", "kenshi", "kasumi", "gray", "murasaki", "purple",
                "okuni", "kabuki", "tomoe", "archer", "anne", "pirate", "julie", "musketeer",
                "chiyo", "nodachi", "orin", "o-rin", "shamisen", "ichi", "blind", "shikomizue"
            )
        )
        if is_delicate:
            # Nariz feminino esguio e delicado estilo anime (ponte fina, narinas sutis e pequeno prisma elegante)
            n_nasion = _p3(0.0, eye_z + 0.006, 0.003)
            n_rhinion = _p3(0.0, eye_z - 0.008, 0.008)
            n_tip = _p3(0.0, eye_z - 0.021, 0.013)
            n_base = _p3(0.0, eye_z - 0.026, 0.006)

            n_left_bridge = _p3(-0.0045, eye_z - 0.008, 0.002)
            n_right_bridge = _p3(0.0045, eye_z - 0.008, 0.002)
            n_left_nostril = _p3(-0.0075, eye_z - 0.024, 0.003)
            n_right_nostril = _p3(0.0075, eye_z - 0.024, 0.003)

            if cam_lateral >= 0:
                col_l_flank = _clamp_color(col_base_skin, 0.90)
                col_r_flank = _clamp_color(col_base_skin, 1.05)
            else:
                col_l_flank = _clamp_color(col_base_skin, 1.05)
                col_r_flank = _clamp_color(col_base_skin, 0.90)

            pygame.draw.polygon(surface, col_l_flank, [n_nasion, n_rhinion, n_tip, n_left_nostril, n_left_bridge])
            pygame.draw.polygon(surface, col_r_flank, [n_nasion, n_right_bridge, n_right_nostril, n_tip, n_rhinion])
            col_sub_nasal = _clamp_color(shadow_col, 0.88)
            pygame.draw.polygon(surface, col_sub_nasal, [n_left_nostril, n_tip, n_right_nostril, n_base])
            pygame.draw.line(surface, (255, 248, 244), n_rhinion, n_tip, max(1, int(scale_px * 0.005)))
        else:
            # Nariz masculino estruturado e marcante
            n_nasion = _p3(0.0, eye_z + 0.010, 0.006)
            n_rhinion = _p3(0.0, eye_z - 0.008, 0.016)
            n_tip = _p3(0.0, eye_z - 0.024, 0.022)
            n_base = _p3(0.0, eye_z - 0.030, 0.012)

            n_left_bridge = _p3(-0.010, eye_z - 0.008, 0.004)
            n_right_bridge = _p3(0.010, eye_z - 0.008, 0.004)
            n_left_nostril = _p3(-0.015, eye_z - 0.027, 0.006)
            n_right_nostril = _p3(0.015, eye_z - 0.027, 0.006)

            if cam_lateral >= 0:
                col_l_flank = _clamp_color(col_base_skin, 0.80)
                col_r_flank = _clamp_color(col_base_skin, 1.10)
            else:
                col_l_flank = _clamp_color(col_base_skin, 1.10)
                col_r_flank = _clamp_color(col_base_skin, 0.80)

            pygame.draw.polygon(surface, col_l_flank, [n_nasion, n_rhinion, n_tip, n_left_nostril, n_left_bridge])
            pygame.draw.polygon(surface, col_r_flank, [n_nasion, n_right_bridge, n_right_nostril, n_tip, n_rhinion])
            col_sub_nasal = _clamp_color(shadow_col, 0.75)
            pygame.draw.polygon(surface, col_sub_nasal, [n_left_nostril, n_tip, n_right_nostril, n_base])
            pygame.draw.line(surface, (255, 245, 240), n_rhinion, n_tip, max(1, int(scale_px * 0.008)))

    mask_col = style.get("mask", None)
    if mask_col is not None:
        # Máscara Shinobi Facetada em 3D (cobrindo a ponte inferior do nariz, boca e contornando o queixo)
        m_top_mid = _p3(0.0, eye_z - 0.010, 0.010)
        m_top_l = _p3(-spacing * 1.35, eye_z - 0.014, 0.004)
        m_top_r = _p3(spacing * 1.35, eye_z - 0.014, 0.004)
        m_mid_apex = _p3(0.0, 0.038, 0.014)
        m_mid_l = _p3(-spacing * 1.20, 0.035, 0.004)
        m_mid_r = _p3(spacing * 1.20, 0.035, 0.004)
        m_bot_apex = _p3(0.0, 0.008, 0.008)
        m_bot_l = _p3(-spacing * 0.75, 0.012, 0.004)
        m_bot_r = _p3(spacing * 0.75, 0.012, 0.004)

        if cam_lateral >= 0:
            c_mask_l = _clamp_color(mask_col, 0.85)
            c_mask_r = _clamp_color(mask_col, 1.08)
        else:
            c_mask_l = _clamp_color(mask_col, 1.08)
            c_mask_r = _clamp_color(mask_col, 0.85)

        # Flanco esquerdo e direito da máscara com crista central
        pygame.draw.polygon(surface, c_mask_l, [m_top_mid, m_top_l, m_mid_l, m_bot_l, m_bot_apex, m_mid_apex])
        pygame.draw.polygon(surface, c_mask_r, [m_top_mid, m_mid_apex, m_bot_apex, m_bot_r, m_mid_r, m_top_r])

        # Borda superior com debrum e brilho de tecido
        rim_col = style.get("mask_light", _clamp_color(mask_col, 1.25))
        pygame.draw.lines(surface, rim_col, False, [m_top_l, m_top_mid, m_top_r], max(1, int(scale_px * 0.008)))
    else:
        # 4. Lábios Facetados em 3 Planos 3D
        m_z = 0.038
        w = mouth_w
        m_left = _p3(-w * 0.75, m_z, 0.001)
        m_right = _p3(w * 0.75, m_z, 0.001)
        m_seam_mid = _p3(0.0, m_z - 0.002, 0.003)

        if is_male:
            # Fenda oral masculina firme com lábio inferior sombreado e sóbrio (sem batom brilhante)
            m_bot_mid = _p3(0.0, m_z - 0.008, 0.004)
            m_bot_l = _p3(-w * 0.35, m_z - 0.006, 0.002)
            m_bot_r = _p3(w * 0.35, m_z - 0.006, 0.002)
            pygame.draw.polygon(surface, _clamp_color(col_base_skin, 0.90), [m_left, m_seam_mid, m_right, m_bot_r, m_bot_mid, m_bot_l])
            lip_seam_col = _clamp_color(shadow_col, 0.65)
            pygame.draw.lines(surface, lip_seam_col, False, [m_left, m_seam_mid, m_right], max(1, int(scale_px * 0.009)))
        else:
            # Lábio Superior
            m_cupid_l = _p3(-w * 0.24, m_z + 0.006, 0.004)
            m_cupid_r = _p3(w * 0.24, m_z + 0.006, 0.004)
            m_cupid_mid = _p3(0.0, m_z + 0.003, 0.003)
            col_upper_lip = _clamp_color(lip_col, 0.86)
            pygame.draw.polygon(surface, col_upper_lip, [m_left, m_cupid_l, m_cupid_mid, m_cupid_r, m_right, m_seam_mid])

            # Lábio Inferior
            m_bot_mid = _p3(0.0, m_z - 0.010, 0.005)
            m_bot_l = _p3(-w * 0.38, m_z - 0.007, 0.003)
            m_bot_r = _p3(w * 0.38, m_z - 0.007, 0.003)
            col_lower_lip = _clamp_color(lip_col, 1.08)
            pygame.draw.polygon(surface, col_lower_lip, [m_left, m_seam_mid, m_right, m_bot_r, m_bot_mid, m_bot_l])

            # Brilho no lábio inferior
            hl_poly = [
                _p3(-w * 0.12, m_z - 0.005, 0.006),
                _p3(w * 0.12, m_z - 0.005, 0.006),
                _p3(w * 0.08, m_z - 0.008, 0.006),
                _p3(-w * 0.08, m_z - 0.008, 0.006),
            ]
            pygame.draw.polygon(surface, (246, 205, 212), hl_poly)

            # Fenda Oral
            lip_seam_col = (110, 42, 52)
            pygame.draw.lines(surface, lip_seam_col, False, [m_left, m_seam_mid, m_right], max(1, int(scale_px * 0.009)))

        # Sulco do Queixo
        ch_l = _p3(-w * 0.28, m_z - 0.016, 0.002)
        ch_r = _p3(w * 0.28, m_z - 0.016, 0.002)
        pygame.draw.line(surface, shadow_col, ch_l, ch_r, max(1, int(scale_px * 0.007)))

        # Barba marcial encorpada (Benkei, o Monge Guerreiro)
        if style.get("beard", False) or char_type == "benkei":
            b_col = style.get("beard_col", (32, 28, 26))
            if cam_lateral >= 0:
                c_brd_l = _clamp_color(b_col, 0.85)
                c_brd_r = _clamp_color(b_col, 1.08)
            else:
                c_brd_l = _clamp_color(b_col, 1.08)
                c_brd_r = _clamp_color(b_col, 0.85)

            # Bigode volumoso conectando à barba
            mst_top = _p3(0.0, 0.048, 0.007)
            mst_l = _p3(-w * 0.48, 0.038, 0.006)
            mst_r = _p3(w * 0.48, 0.038, 0.006)
            pygame.draw.polygon(surface, c_brd_l, [mst_top, mst_l, m_left, m_seam_mid])
            pygame.draw.polygon(surface, c_brd_r, [mst_top, m_seam_mid, m_right, mst_r])

            # Barba encorpada cobrindo mandíbula e queixo em 3D
            brd_chin_apex = _p3(0.0, -0.004, 0.012)
            brd_chin_bot = _p3(0.0, -0.014, 0.008)
            brd_jaw_l = _p3(-spacing * 1.30, 0.024, 0.004)
            brd_jaw_r = _p3(spacing * 1.30, 0.024, 0.004)
            brd_mid_l = _p3(-w * 0.42, 0.012, 0.008)
            brd_mid_r = _p3(w * 0.42, 0.012, 0.008)

            pygame.draw.polygon(surface, c_brd_l, [m_left, brd_jaw_l, brd_mid_l, brd_chin_bot, brd_chin_apex, m_seam_mid])
            pygame.draw.polygon(surface, c_brd_r, [m_right, m_seam_mid, brd_chin_apex, brd_chin_bot, brd_mid_r, brd_jaw_r])

        elif style.get("mustache", False) or char_type in ("rifleman", "teppo"):
            m_col = style.get("mustache_col", (34, 30, 26))
            mst_top = _p3(0.0, 0.046, 0.006)
            mst_l_mid = _p3(-w * 0.42, 0.041, 0.005)
            mst_l_tip = _p3(-w * 0.72, 0.034, 0.003)
            mst_r_mid = _p3(w * 0.42, 0.041, 0.005)
            mst_r_tip = _p3(w * 0.72, 0.034, 0.003)
            pygame.draw.polygon(surface, m_col, [mst_top, mst_l_mid, mst_l_tip, m_left, m_seam_mid])
            pygame.draw.polygon(surface, m_col, [mst_top, m_seam_mid, m_right, mst_r_tip, mst_r_mid])

        # Queixo Facetado (Chin Pad)
        if not (style.get("beard", False) or char_type == "benkei"):
            chin_tip = _p3(0.0, 0.014, 0.008)
            chin_l = _p3(-w * 0.25, 0.020, 0.004)
            chin_r = _p3(w * 0.25, 0.020, 0.004)
            chin_bot = _p3(0.0, 0.008, 0.005)
            pygame.draw.polygon(surface, _clamp_color(col_base_skin, 1.04), [chin_l, chin_tip, chin_r, chin_bot])

    # 5. Jugular da Jingasa (Chin Strap) contornando a mandíbula até o queixo
    if style.get("chin_strap", False):
        strap_col = style.get("strap_col", (225, 215, 195))
        p_strap_l = _p3(-spacing * 1.55, eye_z - 0.010, -0.002)
        p_strap_jaw_l = _p3(-spacing * 1.05, 0.020, 0.002)
        p_strap_chin = _p3(0.0, 0.006, 0.008)
        p_strap_jaw_r = _p3(spacing * 1.05, 0.020, 0.002)
        p_strap_r = _p3(spacing * 1.55, eye_z - 0.010, -0.002)
        pygame.draw.lines(surface, strap_col, False, [p_strap_l, p_strap_jaw_l, p_strap_chin, p_strap_jaw_r, p_strap_r], max(1, int(scale_px * 0.014)))

