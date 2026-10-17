#!/usr/bin/env python3
"""
tools/arena_inspector.py - Arena Free-Cam Inspector 3D para Samurai Edge

Visualizador interativo 3D dedicado com CÂMERA FLUTUANTE 6-EIXOS (Free-Cam)
para sobrevoar, examinar de perto e inspecionar qualquer uma das 18 arenas do jogo:
  - Movimento Livre 6-Eixos:
      • Eixo X / Y (Plano de Solo): W / A / S / D ou Arrastar Botão Direito do Mouse.
      • Eixo Z (Altitude / Altura): E (subir) / Q (descer) ou PageUp / PageDown.
      • Azimute Orbital (360° Horizontal): J / L ou Arrastar Botão Esquerdo do Mouse.
      • Elevação Pitch (5° a 85° Vertical): I / K ou Arrastar Verticalmente.
      • Zoom de Lente (0.35x Panorâmica a 4.5x Macro): Roda do Mouse ou teclas + / -.
      • Multiplicador de Velocidade: Segurar Shift (3.0x Fast Fly) ou Ctrl (0.3x Micro).
      • Reset de Câmera: Tecla Home ou R.
  - Controles de Arena:
      • Alternar Arenas: Tab / Shift+Tab ou clicar na lista lateral de 18 arenas.
      • Pausar/Continuar Vento & Clima: Tecla P.
      • Alternar Renderização 3D ao Vivo vs Cache de Superfície: Tecla V.
      • Alternar Grid Isométrico & Coordenadas: Tecla G.
      • Alternar Iluminação & Atmosfera: Tecla L.
      • Alternar Visibilidade de Props: Tecla O.
      • Alternar Destacar Pits & Colisões: Tecla B.
      • Ocultar/Exibir HUD: Tecla H.
      • Salvar Captura de Tela: F12 ou C (salva em docs/screenshots/).
  - Totalmente desacoplado do código do jogo.
"""
import argparse
import math
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pygame

from src.config import HALF_TILE_W, HALF_TILE_H, MAP_COLS, MAP_ROWS
from src.isometric.iso_math import PIXELS_PER_Z, iso_depth
from src.world.arenas import ARENA_SPECS, HIDDEN_ARENA_SPECS, arena_ids, create_arena
from src.world.arena_cache import get_terrain_cache, get_prop_cache


# =============================================================================
# CÂMERA FLUTUANTE 6-EIXOS (FREE-CAM 3D)
# =============================================================================
class FreeFlyCamera:
    """
    Câmera de voo livre com 6 graus de liberdade isométrica:
    Posição 3D de mundo (wx, wy, wz), rotação orbital 360° (azimute),
    inclinação vertical (elevação) e zoom óptico contínuo.
    Compatível com os métodos esperados por props, terreno e iluminação.
    """
    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.screen_x = screen_w // 2 + 110  # Espaço para o menu lateral
        self.screen_y = screen_h // 2

        # Posição 3D de foco no mundo
        self.wx = 10.5
        self.wy = 10.5
        self.wz = 0.0

        # Rotação e escala
        self.azimuth = 0.0                   # Radianos (0.0 = ângulo canônico)
        self.elevation = math.radians(30.0)  # 30° = clássico 2:1
        self.zoom = 1.15                     # Escala padrão de visão da arena

        # Compatibilidade com o motor de jogo
        self.ground_z = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
        self.height_fn = None

    def reset(self, center_x: float = 10.5, center_y: float = 10.5):
        """Restaura a câmera para o centro da arena atual com ângulo padrão."""
        self.wx = center_x
        self.wy = center_y
        self.wz = 0.0
        self.azimuth = 0.0
        self.elevation = math.radians(30.0)
        self.zoom = 1.15
        self.screen_x = self.screen_w // 2 + 110
        self.screen_y = self.screen_h // 2

    def move_relative(self, forward: float, right: float, up: float):
        """
        Move a câmera no espaço de mundo de forma orientada pelo azimute atual:
        'forward' avança na direção para onde a câmera aponta;
        'right' faz strafe lateral;
        'up' sobe ou desce o eixo Z de altitude.
        """
        # Vetor frontal projetado no plano de solo
        # No azimute 0, a direção de avanço no mundo é (1.0, 1.0) normalizado
        cos_az = math.cos(self.azimuth)
        sin_az = math.sin(self.azimuth)

        # Frente e direita no plano do mundo
        fwd_x = cos_az + sin_az
        fwd_y = cos_az - sin_az
        fwd_len = math.hypot(fwd_x, fwd_y) or 1.0
        fwd_x /= fwd_len
        fwd_y /= fwd_len

        # Vetor lateral direito (perpendicular)
        right_x = -fwd_y
        right_y = fwd_x

        self.wx += fwd_x * forward + right_x * right
        self.wy += fwd_y * forward + right_y * right
        self.wz += up

    def pan_screen(self, dx: int, dy: int):
        """Desloca a câmera em pixels na tela."""
        self.screen_x += dx
        self.screen_y += dy

    def rotate_orbit(self, d_azimuth: float, d_elevation: float):
        """Rotaciona o ângulo orbital horizontal e a inclinação vertical."""
        self.azimuth = (self.azimuth + d_azimuth) % (math.pi * 2.0)
        min_elev = math.radians(5.0)   # Quase rente ao chão
        max_elev = math.radians(85.0)  # Quase vista superior (satélite)
        self.elevation = max(min_elev, min(max_elev, self.elevation + d_elevation))

    def zoom_in(self, factor: float = 1.12):
        self.zoom = max(0.35, min(4.8, self.zoom * factor))

    def zoom_out(self, factor: float = 1.12):
        self.zoom = max(0.35, min(4.8, self.zoom / factor))

    def depth(self, wx: float, wy: float) -> float:
        """Profundidade de ordenação contínua respeitando o azimute."""
        return iso_depth(wx, wy, self.azimuth)

    def apply(self, wx: float, wy: float, wz: float = 0.0) -> tuple[int, int]:
        """Projeta coordenadas 3D de mundo para a tela 2D."""
        rx = wx - self.wx
        ry = wy - self.wy
        rz = wz - self.wz

        c, s = math.cos(self.azimuth), math.sin(self.azimuth)
        rot_x = rx * c - ry * s
        rot_y = rx * s + ry * c

        sin_elev = math.sin(self.elevation)
        cos_elev = math.cos(self.elevation)

        iso_x = (rot_x - rot_y) * HALF_TILE_W
        elev_ratio = sin_elev / 0.5
        z_ratio = cos_elev / 0.866

        iso_y = (rot_x + rot_y) * (HALF_TILE_H * elev_ratio) - (rz * (PIXELS_PER_Z * z_ratio))

        dx = iso_x * self.zoom
        dy = iso_y * self.zoom

        final_x = int(dx + self.screen_x + self.shake_offset_x)
        final_y = int(dy + self.screen_y + self.shake_offset_y)
        return final_x, final_y


# =============================================================================
# METADADOS DAS ARENAS PARA INSPEÇÃO
# =============================================================================
ARENA_DISPLAY_INFO = {
    "bamboo": {"title": "Floresta de Bambu", "subtitle": "O Santuário dos Bambus Sagrados", "fighter": "Kenshi"},
    "kyoto": {"title": "Kyoto: Bakumatsu", "subtitle": "Avenida das Chamas e Carruagens", "fighter": "Murasaki"},
    "shaolin_temple": {"title": "Pátio Shaolin", "subtitle": "O Templo das Mil Contas", "fighter": "Ren"},
    "higanbana_garden": {"title": "Lírios Carmim", "subtitle": "O Bosque do Adeus Noturno", "fighter": "Chiyo"},
    "gojo_bridge": {"title": "Ponte Gojo", "subtitle": "A Travessia das Mil Lâminas", "fighter": "Benkei"},
    "yoshiwara_alley": {"title": "Beco Yoshiwara", "subtitle": "O Labirinto das Sombras Rubras", "fighter": "O-Rin"},
    "rice_paddies": {"title": "Arrozais Terraciados", "subtitle": "A Fúria dos Campos Alagados", "fighter": "Goro"},
    "rain_mill": {"title": "Moinho na Chuva", "subtitle": "O Pranto das Águas do Moinho", "fighter": "Ichi"},
    "dojo": {"title": "Dojo Clássico", "subtitle": "O Tatami Sagrado do Duelo", "fighter": "Veteranos"},
    "forest_camp": {"title": "Acampamento Florestal", "subtitle": "Fogueiras sob o Luar", "fighter": "Joe"},
    "nagashino_field": {"title": "Campo de Nagashino", "subtitle": "A Batalha dos Arcabuzes", "fighter": "Teppo"},
    "shadow_cave": {"title": "Caverna das Sombras", "subtitle": "A Gruta dos Ecos Perdidos", "fighter": "Kasumi"},
    "baroque_court": {"title": "Pátio Barroco", "subtitle": "O Mármore dos Nobres", "fighter": "Julie"},
    "ganryu_island": {"title": "Ilha Ganryū", "subtitle": "O Duelo dos Dois Mestres", "fighter": "Musashi"},
    "iga_rooftops": {"title": "Telhados de Iga", "subtitle": "A Noite dos Shinobi", "fighter": "Hanzo"},
    "mist_temple": {"title": "Templo da Névoa", "subtitle": "O Lago dos Lótus Imortais", "fighter": "Tomoe"},
    "kabuki_stage": {"title": "Palco Kabuki", "subtitle": "O Teatro das Ilusões", "fighter": "Okuni"},
    "pirate_deck": {"title": "Convés Pirata", "subtitle": "O Galeão da Tempestade", "fighter": "Anne"},
    "mountain_shrine": {"title": "Santuário da Montanha", "subtitle": "O Sino dos Deuses", "fighter": "Saitou"},
    "gashadokuro_graveyard": {"title": "Cemitério Gashadokuro", "subtitle": "O Despertar do Titã de Ossos", "fighter": "Boss Oni"},
}


# =============================================================================
# ARENA INSPECTOR CORE
# =============================================================================
class ArenaInspector:
    def __init__(self, width: int = 1280, height: int = 720, headless: bool = False):
        self.width = width
        self.height = height
        self.headless = headless

        if headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            os.environ["SDL_AUDIODRIVER"] = "dummy"

        pygame.init()
        pygame.display.set_caption("Samurai Edge — Arena Free-Cam Inspector 3D")

        flags = pygame.DOUBLEBUF | pygame.RESIZABLE if not headless else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        self.clock = pygame.time.Clock()

        self.camera = FreeFlyCamera(width, height)

        # Lista de arenas disponíveis
        self.available_arenas = arena_ids()
        if "gashadokuro_graveyard" in HIDDEN_ARENA_SPECS:
            self.available_arenas.append("gashadokuro_graveyard")
        self.current_arena_idx = 0

        # Arena carregada
        self.game_map = None
        self.load_arena(self.available_arenas[self.current_arena_idx])

        # Estado e modos de exibição
        self.use_cache = True
        self.is_paused = False
        self.show_lighting = True
        self.show_grid = False
        self.show_props = True
        self.show_bounds = False
        self.show_hud = True

        # Interatividade do mouse
        self.is_dragging_orbit = False
        self.is_dragging_pan = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Movimento contínuo por teclado
        self.keys_held = set()

        # Tempo e animações
        self.current_time = 0.0
        self.fps = 60.0

        # Fontes do HUD
        self.font_header = pygame.font.Font(None, 30)
        self.font_body = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)

        # Regiões clicáveis
        self.sidebar_rects: list[tuple[pygame.Rect, int]] = []

    def load_arena(self, arena_id: str):
        """Instancia e carrega a arena especificada."""
        try:
            self.game_map = create_arena(arena_id)
            cols = getattr(self.game_map, "cols", MAP_COLS)
            rows = getattr(self.game_map, "rows", MAP_ROWS)
            self.camera.reset(cols / 2.0, rows / 2.0)
        except Exception as e:
            print(f"[ArenaInspector] Erro ao carregar arena '{arena_id}': {e}")

    def next_arena(self):
        self.current_arena_idx = (self.current_arena_idx + 1) % len(self.available_arenas)
        self.load_arena(self.available_arenas[self.current_arena_idx])

    def prev_arena(self):
        self.current_arena_idx = (self.current_arena_idx - 1) % len(self.available_arenas)
        self.load_arena(self.available_arenas[self.current_arena_idx])

    def select_arena(self, idx: int):
        self.current_arena_idx = idx % len(self.available_arenas)
        self.load_arena(self.available_arenas[self.current_arena_idx])

    def handle_events(self) -> bool:
        """Processa interações de mouse e teclado."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.VIDEORESIZE:
                self.width = max(800, event.w)
                self.height = max(600, event.h)
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.RESIZABLE)
                self.camera.screen_w = self.width
                self.camera.screen_h = self.height

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão Esquerdo (Órbita ou Clique na Sidebar)
                    clicked_ui = False
                    for rect, idx in self.sidebar_rects:
                        if rect.collidepoint(event.pos):
                            self.select_arena(idx)
                            clicked_ui = True
                            break
                    if not clicked_ui:
                        self.is_dragging_orbit = True
                        self.drag_start_x, self.drag_start_y = event.pos
                elif event.button == 3:  # Botão Direito (Pan de tela)
                    self.is_dragging_pan = True
                    self.drag_start_x, self.drag_start_y = event.pos
                elif event.button == 4:  # Scroll Up (Zoom In)
                    self.camera.zoom_in(1.10)
                elif event.button == 5:  # Scroll Down (Zoom Out)
                    self.camera.zoom_out(1.10)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging_orbit = False
                elif event.button == 3:
                    self.is_dragging_pan = False

            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging_orbit:
                    dx = event.pos[0] - self.drag_start_x
                    dy = event.pos[1] - self.drag_start_y
                    self.camera.rotate_orbit(dx * 0.007, -dy * 0.007)
                    self.drag_start_x, self.drag_start_y = event.pos
                elif self.is_dragging_pan:
                    dx = event.pos[0] - self.drag_start_x
                    dy = event.pos[1] - self.drag_start_y
                    self.camera.pan_screen(dx, dy)
                    self.drag_start_x, self.drag_start_y = event.pos

            elif event.type == pygame.KEYDOWN:
                self.keys_held.add(event.key)

                if event.key == pygame.K_ESCAPE:
                    return False

                # Navegação de Arenas
                elif event.key in (pygame.K_TAB, pygame.K_RIGHTBRACKET):
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        self.prev_arena()
                    else:
                        self.next_arena()
                elif event.key == pygame.K_LEFTBRACKET:
                    self.prev_arena()

                # Toggles de Exibição
                elif event.key == pygame.K_p:
                    self.is_paused = not self.is_paused
                elif event.key == pygame.K_v:
                    self.use_cache = not self.use_cache
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_l:
                    self.show_lighting = not self.show_lighting
                elif event.key == pygame.K_o:
                    self.show_props = not self.show_props
                elif event.key == pygame.K_b:
                    self.show_bounds = not self.show_bounds
                elif event.key == pygame.K_h:
                    self.show_hud = not self.show_hud

                # Reset de Câmera
                elif event.key in (pygame.K_r, pygame.K_HOME):
                    cols = getattr(self.game_map, "cols", MAP_COLS)
                    rows = getattr(self.game_map, "rows", MAP_ROWS)
                    self.camera.reset(cols / 2.0, rows / 2.0)

                # Zoom Teclado
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.camera.zoom_in(1.15)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.camera.zoom_out(1.15)

                # Snapshot
                elif event.key in (pygame.K_F12, pygame.K_c):
                    arena_name = self.available_arenas[self.current_arena_idx]
                    snap_name = f"arena_{arena_name}_aerial.png"
                    snap_path = os.path.join(ROOT, "docs", "screenshots", snap_name)
                    self.snapshot(snap_path)

            elif event.type == pygame.KEYUP:
                if event.key in self.keys_held:
                    self.keys_held.remove(event.key)

        return True

    def update(self, dt: float):
        """Atualiza a física de voo da câmera livre e animações do mundo."""
        if not self.is_paused:
            self.current_time += dt

        # Velocidade de voo livre
        base_speed = 7.5 * dt
        mods = pygame.key.get_mods()
        if mods & pygame.KMOD_SHIFT:
            base_speed *= 2.8
        elif mods & pygame.KMOD_CTRL:
            base_speed *= 0.28

        # Deslocamento no espaço 3D (W/A/S/D + E/Q)
        fwd, right, up = 0.0, 0.0, 0.0
        if pygame.K_w in self.keys_held or pygame.K_UP in self.keys_held:
            fwd += base_speed
        if pygame.K_s in self.keys_held or pygame.K_DOWN in self.keys_held:
            fwd -= base_speed
        if pygame.K_d in self.keys_held:
            right += base_speed
        if pygame.K_a in self.keys_held:
            right -= base_speed
        if pygame.K_e in self.keys_held or pygame.K_PAGEUP in self.keys_held or pygame.K_SPACE in self.keys_held:
            up += base_speed * 0.8
        if pygame.K_q in self.keys_held or pygame.K_PAGEDOWN in self.keys_held:
            up -= base_speed * 0.8

        if fwd != 0.0 or right != 0.0 or up != 0.0:
            self.camera.move_relative(fwd, right, up)

        # Rotação suave por teclas J/L (Azimute) e I/K (Elevação)
        rot_speed = 1.4 * dt
        if pygame.K_j in self.keys_held:
            self.camera.rotate_orbit(-rot_speed, 0.0)
        if pygame.K_l in self.keys_held:
            self.camera.rotate_orbit(rot_speed, 0.0)
        if pygame.K_i in self.keys_held:
            self.camera.rotate_orbit(0.0, rot_speed * 0.8)
        if pygame.K_k in self.keys_held:
            self.camera.rotate_orbit(0.0, -rot_speed * 0.8)

    def draw_world(self, surface: pygame.Surface):
        """Renderiza terreno, props, perigos e estruturas da arena."""
        if not self.game_map:
            return

        # 1. Terreno (Cache Estático ou Voxel 3D Dinâmico)
        if self.use_cache and self.camera.azimuth == 0.0:
            cache = get_terrain_cache()
            # Se a rotação for 0, utiliza o cache acelerado de superfície
            self.game_map.render_terrain(surface, self.camera, self.current_time)
        else:
            # Desenho volumétrico contínuo de terreno com rotação livre 360°
            self.game_map.render_terrain(surface, self.camera, self.current_time)

        # 2. Grid Isométrico Auxiliar (se ativo)
        if self.show_grid:
            self.draw_debug_grid(surface)

        # 3. Fila de Renderização com Y-Sorting Contínuo
        if self.show_props:
            render_queue = []
            for r in getattr(self.game_map, "rocks", []):
                render_queue.append((self.camera.depth(r.wx, r.wy), "rock", r))
            if getattr(self.game_map, "well", None):
                w = self.game_map.well
                render_queue.append((self.camera.depth(w.wx, w.wy), "well", w))
            for t in getattr(self.game_map, "trees", []):
                render_queue.append((self.camera.depth(t.wx, t.wy), "tree", t))
            for lt in getattr(self.game_map, "lanterns", []):
                render_queue.append((self.camera.depth(lt.wx, lt.wy), "lantern", lt))
            for tg in getattr(self.game_map, "torii_gates", []):
                render_queue.append((self.camera.depth(tg.wx, tg.wy), "torii", tg))
            for b in getattr(self.game_map, "bamboos", []):
                render_queue.append((self.camera.depth(b.wx, b.wy), "bamboo", b))
            for bd in getattr(self.game_map, "buildings", []):
                render_queue.append((self.camera.depth(bd.wx, bd.wy), "building", bd))
            for sp in getattr(self.game_map, "solid_props", []):
                render_queue.append((self.camera.depth(sp.wx, sp.wy), "solid_prop", sp))

            render_queue.sort(key=lambda item: item[0])
            for _, item_type, obj in render_queue:
                try:
                    if item_type in ("bamboo", "building", "lantern") or getattr(obj, "animated", False):
                        obj.render(surface, self.camera, self.current_time)
                    else:
                        obj.render(surface, self.camera)
                except Exception:
                    pass

        # 4. Elementos Aéreos, Iluminação e Atmosfera
        if self.show_lighting and hasattr(self.game_map, "render_overhead"):
            try:
                self.game_map.render_overhead(surface, self.camera, self.current_time)
            except Exception:
                pass

        # 5. Bordas de Colisão / Limites Jogáveis / Zonas de Abismo (se ativo)
        if self.show_bounds:
            self.draw_bounds_overlay(surface)

    def draw_debug_grid(self, surface: pygame.Surface):
        """Desenha as linhas do grid do mundo no plano Z=0."""
        cols = getattr(self.game_map, "cols", MAP_COLS)
        rows = getattr(self.game_map, "rows", MAP_ROWS)
        step = 2

        for x in range(0, cols + 1, step):
            p0 = self.camera.apply(float(x), 0.0, 0.0)
            p1 = self.camera.apply(float(x), float(rows), 0.0)
            pygame.draw.line(surface, (70, 75, 90), p0, p1, 1)

        for y in range(0, rows + 1, step):
            p0 = self.camera.apply(0.0, float(y), 0.0)
            p1 = self.camera.apply(float(cols), float(y), 0.0)
            pygame.draw.line(surface, (70, 75, 90), p0, p1, 1)

    def draw_bounds_overlay(self, surface: pygame.Surface):
        """Exibe o contorno do limite jogável e abismos."""
        bounds = getattr(self.game_map, "playable_bounds", None)
        if bounds:
            min_x, min_y, max_x, max_y = bounds
            pts = [
                self.camera.apply(min_x, min_y, 0.05),
                self.camera.apply(max_x, min_y, 0.05),
                self.camera.apply(max_x, max_y, 0.05),
                self.camera.apply(min_x, max_y, 0.05),
            ]
            pygame.draw.polygon(surface, (240, 190, 60), pts, 2)

    def draw_hud(self, surface: pygame.Surface):
        """Desenha os painéis de navegação, status e atalhos."""
        if not self.show_hud:
            return

        # -------------------------------------------------------------
        # 1. Barra Lateral: Lista das 18 Arenas
        # -------------------------------------------------------------
        sidebar_w = 230
        sidebar_surf = pygame.Surface((sidebar_w, self.height), pygame.SRCALPHA)
        sidebar_surf.fill((16, 18, 24, 235))
        surface.blit(sidebar_surf, (0, 0))
        pygame.draw.line(surface, (55, 60, 75), (sidebar_w, 0), (sidebar_w, self.height), 2)

        title_s = self.font_header.render("ARENAS (18+)", True, (240, 215, 120))
        surface.blit(title_s, (16, 16))
        sub_s = self.font_small.render("Tab / Clique para carregar", True, (160, 165, 180))
        surface.blit(sub_s, (16, 46))

        self.sidebar_rects.clear()
        btn_y = 70
        btn_h = 28
        for idx, key in enumerate(self.available_arenas):
            meta = ARENA_DISPLAY_INFO.get(key, {"title": key, "fighter": "—"})
            is_selected = (idx == self.current_arena_idx)
            btn_rect = pygame.Rect(12, btn_y, sidebar_w - 24, btn_h)
            self.sidebar_rects.append((btn_rect, idx))

            if is_selected:
                pygame.draw.rect(surface, (45, 52, 70), btn_rect, border_radius=4)
                pygame.draw.rect(surface, (230, 195, 90), btn_rect, width=2, border_radius=4)
            else:
                pygame.draw.rect(surface, (22, 26, 34), btn_rect, border_radius=4)

            text_color = (255, 255, 255) if is_selected else (175, 180, 195)
            name_s = self.font_body.render(f"{idx+1}. {meta['title']}", True, text_color)
            surface.blit(name_s, (btn_rect.x + 10, btn_rect.centery - 7))

            btn_y += btn_h + 3

        # -------------------------------------------------------------
        # 2. Painel Superior Direito: Informações da Arena Atual
        # -------------------------------------------------------------
        cur_key = self.available_arenas[self.current_arena_idx]
        cur_meta = ARENA_DISPLAY_INFO.get(cur_key, {"title": cur_key, "subtitle": "—", "fighter": "—"})

        card_w, card_h = 360, 105
        card_x = self.width - card_w - 18
        card_y = 18

        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((16, 18, 24, 230))
        surface.blit(card_surf, (card_x, card_y))
        pygame.draw.rect(surface, (220, 180, 80), (card_x, card_y, card_w, card_h), 2, border_radius=6)

        title_s = self.font_header.render(cur_meta["title"].upper(), True, (255, 255, 255))
        surface.blit(title_s, (card_x + 16, card_y + 12))

        sub_s = self.font_small.render(cur_meta["subtitle"], True, (230, 200, 120))
        surface.blit(sub_s, (card_x + 16, card_y + 42))

        f_s = self.font_body.render(f"Guerreiro-Tema: {cur_meta['fighter']}", True, (160, 210, 255))
        surface.blit(f_s, (card_x + 16, card_y + 64))

        # -------------------------------------------------------------
        # 3. Painel Inferior: Telemetria da Câmera Livre & Teclas
        # -------------------------------------------------------------
        hud_bar_w = self.width - sidebar_w - 36
        hud_bar_x = sidebar_w + 18
        hud_bar_y = self.height - 76

        bar_surf = pygame.Surface((hud_bar_w, 58), pygame.SRCALPHA)
        bar_surf.fill((16, 18, 24, 235))
        surface.blit(bar_surf, (hud_bar_x, hud_bar_y))
        pygame.draw.rect(surface, (55, 60, 75), (hud_bar_x, hud_bar_y, hud_bar_w, 58), 1, border_radius=6)

        deg_az = int(math.degrees(self.camera.azimuth))
        deg_el = int(math.degrees(self.camera.elevation))
        telemetry = (
            f"FREE-CAM 6-EIXOS: Posição ({self.camera.wx:.1f}, {self.camera.wy:.1f}, Z:{self.camera.wz:+.1f}) | "
            f"Azimute: {deg_az}° | Inclinação: {deg_el}° | Zoom: {self.camera.zoom:.2f}x | FPS: {self.fps:.0f}"
        )
        t_s = self.font_body.render(telemetry, True, (240, 215, 120))
        surface.blit(t_s, (hud_bar_x + 16, hud_bar_y + 10))

        controls = "Voo: [W/A/S/D] Plano | [E/Q] Altitude Z | [Mouse E/D] Órbita/Pan | [Roda] Zoom  ||  Toggles: [V] 3D Voxel | [L] Luz | [G] Grid | [P] Pausar | [H] Ocultar HUD"
        c_s = self.font_small.render(controls, True, (170, 175, 190))
        surface.blit(c_s, (hud_bar_x + 16, hud_bar_y + 34))

    def render(self):
        # Cor de fundo padrão da arena
        bg_color = getattr(self.game_map, "bg_color", (14, 16, 20)) if self.game_map else (14, 16, 20)
        self.screen.fill(bg_color)

        self.draw_world(self.screen)
        self.draw_hud(self.screen)

        pygame.display.flip()

    def run(self):
        """Loop principal de execução interativa."""
        running = True
        last_time = time.time()
        while running:
            now = time.time()
            dt = min(0.1, now - last_time)
            last_time = now

            running = self.handle_events()
            self.update(dt)
            self.render()

            self.clock.tick(60)
            self.fps = self.clock.get_fps()

        pygame.quit()

    def snapshot(self, output_path: str):
        """Salva a visualização atual da arena em PNG."""
        self.render()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pygame.image.save(self.screen, output_path)
        print(f"[ArenaInspector] Snapshot da arena salvo em: {output_path}")


# =============================================================================
# CLI
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Arena Free-Cam Inspector 3D — Samurai Edge")
    parser.add_argument("--arena", choices=arena_ids() + ["gashadokuro_graveyard"], default="bamboo", help="Arena inicial")
    parser.add_argument("--snapshot", type=str, default=None, help="Salva snapshot PNG e sai")
    parser.add_argument("--save-all", action="store_true", help="Salva snapshots de todas as 18 arenas em docs/screenshots/ e sai")
    parser.add_argument("--width", type=int, default=1280, help="Largura da janela")
    parser.add_argument("--height", type=int, default=720, help="Altura da janela")
    parser.add_argument("--headless", action="store_true", help="Executa sem interface gráfica visível")
    args = parser.parse_args()

    is_headless = args.headless or (args.snapshot is not None) or args.save_all
    inspector = ArenaInspector(width=args.width, height=args.height, headless=is_headless)

    if args.save_all:
        out_dir = os.path.join(ROOT, "docs", "screenshots", "arenas")
        os.makedirs(out_dir, exist_ok=True)
        for idx, key in enumerate(inspector.available_arenas):
            inspector.select_arena(idx)
            snap_path = os.path.join(out_dir, f"arena_{key}_inspection.png")
            inspector.snapshot(snap_path)
        print(f"[ArenaInspector] Todas as arenas inspecionadas e salvas em: {out_dir}")
        pygame.quit()
        sys.exit(0)

    if args.arena in inspector.available_arenas:
        idx = inspector.available_arenas.index(args.arena)
        inspector.select_arena(idx)

    if args.snapshot:
        inspector.snapshot(args.snapshot)
        pygame.quit()
        sys.exit(0)
    else:
        inspector.run()


if __name__ == "__main__":
    main()
