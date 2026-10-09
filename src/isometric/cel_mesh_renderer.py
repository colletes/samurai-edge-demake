"""
src/isometric/cel_mesh_renderer.py - Renderizador 3D Low-Poly Cel-Shaded via Software (Técnica 4)

Pipeline poligonal tridimensional em software puro (Pygame) sem dependência de OpenGL:
- Geometria Low-Poly estilizada (vértices e faces poligonais 3D).
- Transformação hierárquica por nó (rotação horizontal yaw, escala e translação 3D).
- Projeção axonometrica / orbital integrada à InspectorCamera.
- Back-face culling automático via winding order do polígono projetado.
- Z-sorting / Painter's Algorithm para ordenação estrita de profundidade de faces.
- Toon / Cel Shading em 2 bandas de iluminação (luz direta vs sombra de recorte nítido).
- Ink Outline (contorno de tinta preta estilo anime/mangá nos contornos das faces).
"""
import math
import pygame
from src.isometric.iso_math import rotate_xy


def shade_cel(base_color: tuple[int, int, int], light_factor: float, threshold: float = 0.28) -> tuple[int, int, int]:
    """
    Toon / Cel Shading com 2 bandas nítidas de iluminação:
    - Se a incidência de luz >= threshold: banda clara iluminada (1.05x).
    - Se a incidência de luz < threshold: banda sombreada de recorte nítido (0.62x).
    """
    r, g, b = base_color[:3]
    factor = 1.05 if light_factor >= threshold else 0.62
    return (
        max(0, min(255, int(r * factor))),
        max(0, min(255, int(g * factor))),
        max(0, min(255, int(b * factor)))
    )


class Mesh:
    """Representa uma malha tridimensional low-poly com vértices locais e faces."""
    def __init__(self):
        self.vertices: list[tuple[float, float, float]] = []
        # faces: lista de tuplas (índices_vértices, cor_base, outline_color)
        self.faces: list[tuple[list[int], tuple[int, int, int], tuple[int, int, int] | None]] = []

    def add_vertex(self, x: float, y: float, z: float) -> int:
        idx = len(self.vertices)
        self.vertices.append((x, y, z))
        return idx

    def add_face(self, indices: list[int], color: tuple[int, int, int], outline_color: tuple[int, int, int] | None = (20, 20, 25)):
        self.faces.append((indices, color, outline_color))


# =============================================================================
# GERADORES DE PRIMITIVAS LOW-POLY ESTILIZADAS
# =============================================================================

def create_frustum_mesh(
    w_bottom: float, d_bottom: float,
    w_top: float, d_top: float,
    height: float,
    color: tuple[int, int, int],
    color_top: tuple[int, int, int] | None = None
) -> Mesh:
    """Cria tronco de pirâmide/prisma (ideal para quimonos, saias, mangas e troncos)."""
    mesh = Mesh()
    c_top = color_top or color

    wb2, db2 = w_bottom * 0.5, d_bottom * 0.5
    wt2, dt2 = w_top * 0.5, d_top * 0.5

    # 4 vértices da base inferior (z=0)
    mesh.add_vertex(-wb2, -db2, 0.0)      # 0: base trás-esquerda
    mesh.add_vertex( wb2, -db2, 0.0)      # 1: base trás-direita
    mesh.add_vertex( wb2,  db2, 0.0)      # 2: base frente-direita
    mesh.add_vertex(-wb2,  db2, 0.0)      # 3: base frente-esquerda

    # 4 vértices do topo (z=height)
    mesh.add_vertex(-wt2, -dt2, height)   # 4: topo trás-esquerda
    mesh.add_vertex( wt2, -dt2, height)   # 5: topo trás-direita
    mesh.add_vertex( wt2,  dt2, height)   # 6: topo frente-direita
    mesh.add_vertex(-wt2,  dt2, height)   # 7: topo frente-esquerda

    # Faces com vértices em ordem horária vista de fora
    mesh.add_face([7, 6, 5, 4], c_top)     # Topo (+Z)
    mesh.add_face([2, 3, 7, 6], color)     # Frente (+Y)
    mesh.add_face([0, 1, 5, 4], color)     # Costas (-Y)
    mesh.add_face([1, 2, 6, 5], color)     # Direita (+X)
    mesh.add_face([3, 0, 4, 7], color)     # Esquerda (-X)
    return mesh


def create_octagonal_cylinder_mesh(radius: float, height: float, color: tuple[int, int, int]) -> Mesh:
    """Cria cilindro octogonal estilizado para membros, pescoço e coque de cabelo."""
    mesh = Mesh()
    n = 8
    bot_indices = []
    top_indices = []

    for i in range(n):
        ang = i * (math.pi * 2 / n)
        x = radius * math.cos(ang)
        y = radius * math.sin(ang)
        bot_indices.append(mesh.add_vertex(x, y, 0.0))
        top_indices.append(mesh.add_vertex(x, y, height))

    # Topo
    mesh.add_face(list(reversed(top_indices)), color)

    # Lados
    for i in range(n):
        next_i = (i + 1) % n
        mesh.add_face([bot_indices[i], bot_indices[next_i], top_indices[next_i], top_indices[i]], color)
    return mesh


def create_blade_mesh(length: float, width: float, thickness: float, color: tuple[int, int, int]) -> Mesh:
    """Cria lâmina afiada chanfrada com fio cortante biselado (tsurugi/katana/adaga)."""
    mesh = Mesh()
    w2 = width * 0.5
    t2 = thickness * 0.5

    # Base da lâmina
    v0 = mesh.add_vertex(0.0, -w2, 0.0)
    v1 = mesh.add_vertex( t2,  0.0, 0.0)
    v2 = mesh.add_vertex(0.0,  w2, 0.0)
    v3 = mesh.add_vertex(-t2,  0.0, 0.0)

    # Ponta afiada
    v_tip = mesh.add_vertex(0.0, w2 * 0.6, length)

    # Faces biseladas
    edge_color = (245, 250, 255)
    mesh.add_face([v0, v1, v_tip], color)
    mesh.add_face([v1, v2, v_tip], edge_color)
    mesh.add_face([v2, v3, v_tip], edge_color)
    mesh.add_face([v3, v0, v_tip], color)
    return mesh


# =============================================================================
# MOTOR DE RENDERIZAÇÃO POLIGONAL CEL-SHADED
# =============================================================================

def render_cel_mesh(
    surface: pygame.Surface,
    camera,
    mesh: Mesh,
    wx: float, wy: float, wz: float,
    yaw: float = 0.0,
    scale: float = 1.0,
    alpha: int = 255,
    outline_width: int = 1,
    light_dir: tuple[float, float, float] = (0.5, -0.6, 0.8)
):
    """
    Renderiza a malha tridimensional:
    1. Transforma vértices por rotação horizontal, escala e translação 3D.
    2. Projeta vértices na InspectorCamera.
    3. Executa Back-face Culling 2D por winding order shoelace.
    4. Aplica Cel Shading (luz difusa toon de 2 bandas).
    5. Ordena faces por profundidade de trás para frente (Painter's Algorithm).
    6. Desenha as faces com Ink Outline estilizado.
    """
    cos_y = math.cos(yaw)
    sin_y = math.sin(yaw)

    # Normaliza vetor de luz
    lx, ly, lz = light_dir
    l_len = math.sqrt(lx * lx + ly * ly + lz * lz) or 1.0
    lx, ly, lz = lx / l_len, ly / l_len, lz / l_len

    # 1. Transforma vértices locais -> mundo
    world_verts = []
    screen_pts = []
    cam_azimuth = getattr(camera, "azimuth", 0.0)

    for vx, vy, vz in mesh.vertices:
        # Escala e rotação por yaw
        rx = (vx * cos_y - vy * sin_y) * scale
        ry = (vx * sin_y + vy * cos_y) * scale
        rz = vz * scale

        mx = wx + rx
        my = wy + ry
        mz = wz + rz
        world_verts.append((mx, my, mz))

        # Projeção na tela
        px, py = camera.apply(mx, my, mz)
        screen_pts.append((px, py))

    # 2. Processa faces visíveis e calcula profundidade
    visible_faces = []

    for vert_indices, base_color, outline_color in mesh.faces:
        if len(vert_indices) < 3:
            continue

        poly_2d = [screen_pts[idx] for idx in vert_indices]

        # Back-face culling 2D: calcula área orientada com sinal
        p0 = poly_2d[0]
        p1 = poly_2d[1]
        p2 = poly_2d[2]
        cross2d = (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])
        if cross2d <= 0:
            continue  # Face voltada para longe do observador

        # Normal 3D no espaço do mundo para cálculo do Cel Shading
        v0 = world_verts[vert_indices[0]]
        v1 = world_verts[vert_indices[1]]
        v2 = world_verts[vert_indices[2]]

        e1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
        e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])

        nx = e1[1] * e2[2] - e1[2] * e2[1]
        ny = e1[2] * e2[0] - e1[0] * e2[2]
        nz = e1[0] * e2[1] - e1[1] * e2[0]
        n_len = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        nx, ny, nz = nx / n_len, ny / n_len, nz / n_len

        # Incidência de luz (dot product com vetor da luz)
        dot_l = nx * lx + ny * ly + nz * lz
        shaded_color = shade_cel(base_color, dot_l)

        # Profundidade média na perspectiva da câmera (maior = mais próximo)
        avg_depth = 0.0
        for idx in vert_indices:
            wv = world_verts[idx]
            rx, ry = rotate_xy(wv[0], wv[1], cam_azimuth)
            avg_depth += (rx + ry)
        avg_depth /= len(vert_indices)

        visible_faces.append((avg_depth, poly_2d, shaded_color, outline_color))

    # 3. Z-Sorting: desenha da menor profundidade (mais longe) para a maior (mais perto)
    visible_faces.sort(key=lambda item: item[0])

    for _, poly_2d, color, out_col in visible_faces:
        if alpha < 255:
            # Preenchimento translúcido
            min_x = min(p[0] for p in poly_2d)
            max_x = max(p[0] for p in poly_2d)
            min_y = min(p[1] for p in poly_2d)
            max_y = max(p[1] for p in poly_2d)
            pw = max(1, max_x - min_x + 1)
            ph = max(1, max_y - min_y + 1)

            poly_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
            local_poly = [(p[0] - min_x, p[1] - min_y) for p in poly_2d]
            pygame.draw.polygon(poly_surf, (*color, alpha), local_poly)
            if out_col and outline_width > 0:
                pygame.draw.polygon(poly_surf, (*out_col, alpha), local_poly, outline_width)
            surface.blit(poly_surf, (min_x, min_y))
        else:
            # Preenchimento direto de alta performance
            pygame.draw.polygon(surface, color, poly_2d)
            if out_col and outline_width > 0:
                pygame.draw.polygon(surface, out_col, poly_2d, outline_width)
