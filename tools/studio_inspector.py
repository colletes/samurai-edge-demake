#!/usr/bin/env python3
"""
tools/studio_inspector.py - Studio 3D Unificado para Samurai Edge (Bakumatsu)

Plataforma unificada de inspeção, renderização e composição 3D:
  - [F1] Model Inspector 3D: Catálogo completo dos 20 combatentes com câmera orbital,
    zoom macro facial (F / 2), troca de poses (1-6) e turntable automático (Space / T).
  - [F2] Arena Free-Cam 3D: Inspeção livre com câmera 6-eixos (WASD / EQ / Mouse)
    por todas as 20 arenas temáticas, com controle de camadas, clima e iluminação.
  - [F3] Composição & Staging: Posicionamento em tempo real de qualquer um dos 20
    combatentes dentro de qualquer uma das 20 arenas com iluminação e partículas ao vivo.
"""
import argparse
import math
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if sys.platform == "darwin":
    os.environ.setdefault("SDL_JOYSTICK_IOKIT", "0")
    os.environ.setdefault("SDL_JOYSTICK_MFI", "1")

if "--headless" in sys.argv or "--snapshot" in sys.argv:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

from src.config import HALF_TILE_W, HALF_TILE_H, MAP_COLS, MAP_ROWS
from src.isometric.iso_math import PIXELS_PER_Z, iso_depth
from src.entities.voxel_models import render_voxel_humanoid
from src.world.arenas import ARENA_SPECS, HIDDEN_ARENA_SPECS, arena_ids, create_arena
from src.world.arena_cache import get_terrain_cache, get_prop_cache
from src.effects.lighting import ArenaLighting
from src.effects.fog import FogVolume
from src.effects.particles import AmbientLeafParticle, set_wind_source
from tools.model_inspector import InspectorCamera, CHARACTERS, POSES
from tools.arena_inspector import FreeFlyCamera, ARENA_DISPLAY_INFO


MODE_MODELS = "models"
MODE_ARENAS = "arenas"
MODE_STAGING = "staging"


class StudioInspector:
    def __init__(self, width: int = 1280, height: int = 720, initial_mode: str = MODE_MODELS,
                 char_key: str = "valerius", arena_key: str = "gothic_cemetery", headless: bool = False):
        self.width = width
        self.height = height
        self.mode = initial_mode
        self.headless = headless

        if headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            os.environ["SDL_AUDIODRIVER"] = "dummy"

        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption("Samurai Edge — Studio 3D Unificado [F1 Modelos | F2 Arenas | F3 Staging]")

        flags = pygame.DOUBLEBUF | pygame.RESIZABLE if not headless else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        self.clock = pygame.time.Clock()

        # Listas de seleção
        self.char_keys = list(CHARACTERS.keys())
        self.arena_keys = arena_ids()
        if "gashadokuro_graveyard" in HIDDEN_ARENA_SPECS and "gashadokuro_graveyard" not in self.arena_keys:
            self.arena_keys.append("gashadokuro_graveyard")

        # Seleção atual de personagem e arena
        self.current_char_idx = self.char_keys.index(char_key) if char_key in self.char_keys else 0
        self.current_arena_idx = self.arena_keys.index(arena_key) if arena_key in self.arena_keys else 0

        # Câmeras especializadas
        self.model_camera = InspectorCamera(width, height)
        self.arena_camera = FreeFlyCamera(width, height)
        self.staging_camera = FreeFlyCamera(width, height)
        self.staging_camera.zoom = 1.6

        # Estado do Model Inspector
        self.current_pose = "IDLE"
        self.turntable_active = False
        self.turntable_speed = 0.65
        self.show_wireframe_marker = False
        self.current_focus = "body"

        # Estado da Arena
        self.game_map = None
        self.staging_map = None
        self.arena_lighting = None
        self.staging_lighting = None
        self.arena_fog = None
        self.staging_fog = None
        self.arena_leaves = []
        self.staging_leaves = []
        self.use_cache = True
        self.is_paused = False
        self.show_lighting = True
        self.show_fog = True
        self.show_weather = True
        self.show_grid = False
        self.show_props = True
        self.show_bounds = False

        # Estado de Staging (Composição)
        self.actor_wx = 10.5
        self.actor_wy = 10.5
        self.actor_wz = 0.0
        self.actor_facing_x = 1.0
        self.actor_facing_y = 1.0
        self.actor_control_active = False  # False = controla câmera livre; True = controla ator com WASD/Setas

        # Interatividade comum
        self.show_hud = True
        self.is_dragging_orbit = False
        self.is_dragging_pan = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.keys_held = set()
        self.anim_time = 0.0
        self.fps = 60.0

        # Fontes do HUD
        self.font_title = pygame.font.Font(None, 24)
        self.font_header = pygame.font.Font(None, 22)
        self.font_body = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 15)

        # Regiões clicáveis
        self.tab_rects: dict[str, pygame.Rect] = {}
        self.char_btn_rects: list[pygame.Rect] = []
        self.arena_btn_rects: list[pygame.Rect] = []
        self.pose_btn_rects: list[pygame.Rect] = []

        # Inicializa mapas
        self.load_arena_for_arena_mode(self.arena_keys[self.current_arena_idx])
        self.load_arena_for_staging_mode(self.arena_keys[self.current_arena_idx])

    # -------------------------------------------------------------------------
    # Gerenciamento de Mapas
    # -------------------------------------------------------------------------
    def load_arena_for_arena_mode(self, arena_key: str):
        try:
            self.game_map = create_arena(arena_key)
            self.arena_camera.reset(MAP_COLS * 0.5, MAP_ROWS * 0.5)
            self.arena_lighting = ArenaLighting(self.game_map)
            self.arena_fog = self.game_map.fog = FogVolume(self.game_map)
            set_wind_source(lambda x, y: self.game_map.wind_at(x, y, self.anim_time))
            self.arena_leaves = [
                AmbientLeafParticle(self.game_map.cols, self.game_map.rows, self.game_map.spec.drift_petals)
                for _ in range(getattr(self.game_map.spec, "drift_count", 24))
            ]
        except Exception as e:
            print(f"[StudioInspector] Erro ao carregar arena '{arena_key}': {e}")

    def load_arena_for_staging_mode(self, arena_key: str):
        try:
            self.staging_map = create_arena(arena_key)
            spawns = getattr(self.staging_map.spec.spawns, "fallback", ((10.5, 10.5), (10.5, 10.5)))
            self.actor_wx, self.actor_wy = spawns[0]
            self.staging_camera.reset(self.actor_wx, self.actor_wy)
            self.staging_camera.zoom = 1.85
            self.staging_lighting = ArenaLighting(self.staging_map)
            self.staging_fog = self.staging_map.fog = FogVolume(self.staging_map)
            self.staging_leaves = [
                AmbientLeafParticle(self.staging_map.cols, self.staging_map.rows, self.staging_map.spec.drift_petals)
                for _ in range(getattr(self.staging_map.spec, "drift_count", 24))
            ]
        except Exception as e:
            print(f"[StudioInspector] Erro ao carregar staging arena '{arena_key}': {e}")

    # -------------------------------------------------------------------------
    # Navegação e Seleção
    # -------------------------------------------------------------------------
    def select_char(self, idx: int):
        self.current_char_idx = idx % len(self.char_keys)

    def select_arena(self, idx: int):
        self.current_arena_idx = idx % len(self.arena_keys)
        arena_key = self.arena_keys[self.current_arena_idx]
        self.load_arena_for_arena_mode(arena_key)
        self.load_arena_for_staging_mode(arena_key)

    def set_mode(self, mode: str):
        if mode in (MODE_MODELS, MODE_ARENAS, MODE_STAGING):
            self.mode = mode

    # -------------------------------------------------------------------------
    # Entrada e Eventos
    # -------------------------------------------------------------------------
    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                # Troca global de Abas
                if event.key == pygame.K_F1:
                    self.set_mode(MODE_MODELS)
                elif event.key == pygame.K_F2:
                    self.set_mode(MODE_ARENAS)
                elif event.key == pygame.K_F3:
                    self.set_mode(MODE_STAGING)
                elif event.key == pygame.K_F12:
                    os.makedirs(os.path.join(ROOT, "docs", "screenshots"), exist_ok=True)
                    snap_name = f"studio_{self.mode}_{int(time.time())}.png"
                    self.snapshot(os.path.join(ROOT, "docs", "screenshots", snap_name))
                elif event.key == pygame.K_h:
                    self.show_hud = not self.show_hud
                elif event.key == pygame.K_ESCAPE:
                    return False

                # Eventos por Modo
                if self.mode == MODE_MODELS:
                    self._handle_keydown_models(event.key)
                elif self.mode == MODE_ARENAS:
                    self._handle_keydown_arenas(event.key)
                elif self.mode == MODE_STAGING:
                    self._handle_keydown_staging(event.key)

            elif event.type == pygame.KEYUP:
                self.keys_held.discard(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Checa cliques em botões do HUD
                    if self._handle_hud_clicks(event.pos):
                        continue
                    self.is_dragging_orbit = True
                    self.drag_start_x, self.drag_start_y = event.pos
                elif event.button == 3:
                    self.is_dragging_pan = True
                    self.drag_start_x, self.drag_start_y = event.pos
                elif event.button == 4:  # Scroll Up -> Zoom In
                    self._active_camera().zoom_in(1.15)
                elif event.button == 5:  # Scroll Down -> Zoom Out
                    self._active_camera().zoom_out(1.15)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging_orbit = False
                elif event.button == 3:
                    self.is_dragging_pan = False

            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging_orbit:
                    dx = event.pos[0] - self.drag_start_x
                    dy = event.pos[1] - self.drag_start_y
                    self.drag_start_x, self.drag_start_y = event.pos
                    cam = self._active_camera()
                    cam.orbit(dx * 0.007, -dy * 0.007)
                elif self.is_dragging_pan:
                    dx = event.pos[0] - self.drag_start_x
                    dy = event.pos[1] - self.drag_start_y
                    self.drag_start_x, self.drag_start_y = event.pos
                    cam = self._active_camera()
                    cam.pan(dx, dy)

            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.DOUBLEBUF | pygame.RESIZABLE)
                self.model_camera.screen_w = event.w
                self.model_camera.screen_h = event.h
                self.arena_camera.screen_w = event.w
                self.arena_camera.screen_h = event.h
                self.staging_camera.screen_w = event.w
                self.staging_camera.screen_h = event.h

        return True

    def _active_camera(self):
        if self.mode == MODE_MODELS:
            return self.model_camera
        elif self.mode == MODE_ARENAS:
            return self.arena_camera
        else:
            return self.staging_camera

    def _handle_keydown_models(self, key):
        if key in (pygame.K_SPACE, pygame.K_t):
            self.turntable_active = not self.turntable_active
        elif key in (pygame.K_f, pygame.K_2):
            self.current_focus = "face" if self.current_focus == "body" else "body"
            self.model_camera.set_focus_target(self.current_focus)
        elif key in (pygame.K_r, pygame.K_HOME):
            self.model_camera.reset(self.current_focus)
        elif key == pygame.K_w:
            self.show_wireframe_marker = not self.show_wireframe_marker
        elif key == pygame.K_TAB:
            mods = pygame.key.get_mods()
            step = -1 if (mods & pygame.KMOD_SHIFT) else 1
            self.select_char(self.current_char_idx + step)
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6):
            idx = key - pygame.K_1
            if 0 <= idx < len(POSES):
                self.current_pose = POSES[idx]

    def _handle_keydown_arenas(self, key):
        if key == pygame.K_p:
            self.is_paused = not self.is_paused
        elif key == pygame.K_v:
            self.use_cache = not self.use_cache
        elif key == pygame.K_l:
            self.show_lighting = not self.show_lighting
        elif key == pygame.K_n:
            self.show_fog = not self.show_fog
        elif key == pygame.K_k:
            self.show_weather = not self.show_weather
        elif key == pygame.K_g:
            self.show_grid = not self.show_grid
        elif key == pygame.K_o:
            self.show_props = not self.show_props
        elif key == pygame.K_b:
            self.show_bounds = not self.show_bounds
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
            phase_idx = key - pygame.K_1
            if self.game_map:
                for h in getattr(self.game_map, "hazards", []):
                    if hasattr(h, "set_phase"):
                        h.set_phase(phase_idx)
        elif key in (pygame.K_r, pygame.K_HOME):
            self.arena_camera.reset(MAP_COLS * 0.5, MAP_ROWS * 0.5)
        elif key == pygame.K_TAB:
            mods = pygame.key.get_mods()
            step = -1 if (mods & pygame.KMOD_SHIFT) else 1
            self.select_arena(self.current_arena_idx + step)
        else:
            self.keys_held.add(key)


    def _handle_keydown_staging(self, key):
        if key == pygame.K_c:
            self.actor_control_active = not self.actor_control_active
        elif key == pygame.K_p:
            self.is_paused = not self.is_paused
        elif key == pygame.K_l:
            self.show_lighting = not self.show_lighting
        elif key == pygame.K_n:
            self.show_fog = not self.show_fog
        elif key == pygame.K_k:
            self.show_weather = not self.show_weather
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6):
            idx = key - pygame.K_1
            if 0 <= idx < len(POSES):
                self.current_pose = POSES[idx]
        elif key in (pygame.K_LEFTBRACKET, pygame.K_COMMA):
            self.select_char(self.current_char_idx - 1)
        elif key in (pygame.K_RIGHTBRACKET, pygame.K_PERIOD):
            self.select_char(self.current_char_idx + 1)
        elif key in (pygame.K_r, pygame.K_HOME):
            self.staging_camera.reset(self.actor_wx, self.actor_wy)
        else:
            self.keys_held.add(key)

    def _handle_hud_clicks(self, pos: tuple[int, int]) -> bool:
        # Clique nas abas superiores
        for mode, rect in self.tab_rects.items():
            if rect.collidepoint(pos):
                self.set_mode(mode)
                return True

        if not self.show_hud:
            return False

        if self.mode == MODE_MODELS:
            # Lista de personagens
            for idx, rect in enumerate(self.char_btn_rects):
                if rect.collidepoint(pos):
                    self.select_char(idx)
                    return True
            # Poses
            for pose_name, rect in self.pose_btn_rects:
                if rect.collidepoint(pos):
                    self.current_pose = pose_name
                    return True

        elif self.mode == MODE_ARENAS:
            # Lista de arenas
            for idx, rect in enumerate(self.arena_btn_rects):
                if rect.collidepoint(pos):
                    self.select_arena(idx)
                    return True

        elif self.mode == MODE_STAGING:
            # Seleção rápida de personagem ou arena no painel de staging
            for idx, rect in enumerate(self.char_btn_rects):
                if rect.collidepoint(pos):
                    self.select_char(idx)
                    return True
            for idx, rect in enumerate(self.arena_btn_rects):
                if rect.collidepoint(pos):
                    self.select_arena(idx)
                    return True

        return False

    # -------------------------------------------------------------------------
    # Atualização
    # -------------------------------------------------------------------------
    def update(self, dt: float):
        if not self.is_paused:
            self.anim_time += dt
            if self.mode == MODE_ARENAS and getattr(self, "arena_fog", None):
                self.arena_fog.update(dt, self.anim_time)
            elif self.mode == MODE_STAGING and getattr(self, "staging_fog", None):
                self.staging_fog.update(dt, self.anim_time)

            leaves = getattr(self, "arena_leaves" if self.mode == MODE_ARENAS else "staging_leaves", [])
            for leaf in leaves:
                leaf.update(dt)

        # Atualizações do Model Inspector
        if self.mode == MODE_MODELS and self.turntable_active:
            self.model_camera.orbit(self.turntable_speed * dt, 0.0)

        # Atualizações da Câmera Livre em Arenas
        if self.mode == MODE_ARENAS:
            self._update_freecam(self.arena_camera, dt)
            if self.game_map and not self.is_paused:
                self.game_map.update(dt, [], self.arena_camera, [], [])

        # Atualizações em Staging (Composição)
        if self.mode == MODE_STAGING:
            if self.staging_map and not self.is_paused:
                self.staging_map.update(dt, [], self.staging_camera, [], [])

            if self.actor_control_active:
                # Move o ator com WASD / Setas
                speed = 3.5
                vx, vy = 0.0, 0.0
                if pygame.K_w in self.keys_held or pygame.K_UP in self.keys_held:
                    vy -= 1.0
                if pygame.K_s in self.keys_held or pygame.K_DOWN in self.keys_held:
                    vy += 1.0
                if pygame.K_a in self.keys_held or pygame.K_LEFT in self.keys_held:
                    vx -= 1.0
                if pygame.K_d in self.keys_held or pygame.K_RIGHT in self.keys_held:
                    vx += 1.0

                if vx != 0.0 or vy != 0.0:
                    norm = math.hypot(vx, vy)
                    self.actor_wx += (vx / norm) * speed * dt
                    self.actor_wy += (vy / norm) * speed * dt
                    self.actor_facing_x = vx / norm
                    self.actor_facing_y = vy / norm
                    self.current_pose = "WALK"
                else:
                    if self.current_pose == "WALK":
                        self.current_pose = "IDLE"
            else:
                # Move a câmera livre
                self._update_freecam(self.staging_camera, dt)

    def _update_freecam(self, cam: FreeFlyCamera, dt: float):
        if not self.keys_held:
            return

        mods = pygame.key.get_mods()
        speed = 8.0
        if mods & pygame.KMOD_SHIFT:
            speed *= 2.8
        elif mods & pygame.KMOD_CTRL:
            speed *= 0.35

        dx, dy, dz = 0.0, 0.0, 0.0
        if pygame.K_w in self.keys_held:
            dy -= 1.0
        if pygame.K_s in self.keys_held:
            dy += 1.0
        if pygame.K_a in self.keys_held:
            dx -= 1.0
        if pygame.K_d in self.keys_held:
            dx += 1.0
        if pygame.K_e in self.keys_held:
            dz += 1.0
        if pygame.K_q in self.keys_held:
            dz -= 1.0

        if dx != 0.0 or dy != 0.0:
            norm = math.hypot(dx, dy)
            dx /= norm
            dy /= norm

        c, s = math.cos(cam.azimuth), math.sin(cam.azimuth)
        world_dx = dx * c - dy * s
        world_dy = dx * s + dy * c

        cam.move_world(world_dx * speed * dt, world_dy * speed * dt, dz * speed * dt)

    # -------------------------------------------------------------------------
    # Renderização Geral
    # -------------------------------------------------------------------------
    def render(self):
        if self.mode == MODE_MODELS:
            self._render_models_mode()
        elif self.mode == MODE_ARENAS:
            self._render_arenas_mode()
        elif self.mode == MODE_STAGING:
            self._render_staging_mode()

        # Barra de Abas e HUD Superior Unificado
        self._render_header_bar()

        pygame.display.flip()

    # -------------------------------------------------------------------------
    # Renderização: Modo [F1] Modelos
    # -------------------------------------------------------------------------
    def _render_models_mode(self):
        char_info = CHARACTERS[self.char_keys[self.current_char_idx]]
        accent = char_info.get("color_accent", (75, 80, 110))
        bg_col = (max(8, int(accent[0] * 0.12)), max(8, int(accent[1] * 0.12)), max(12, int(accent[2] * 0.16)))
        self.screen.fill(bg_col)

        # Pedestal e sombra
        self._draw_model_pedestal()

        # Renderização oficial do combatente
        facing_x, facing_y = 1.0, 1.0
        state = self.current_pose
        state_timer = 0.0
        is_moving = (self.current_pose == "WALK")
        walk_timer = self.anim_time * 2.6 if is_moving else self.anim_time

        if self.current_pose == "ATTACK":
            state_timer = 0.08 + (math.sin(self.anim_time * 4.0) * 0.5 + 0.5) * 0.12
        elif self.current_pose == "RECOVERY":
            state_timer = 0.35
        elif self.current_pose in ("INTRO", "VICTORY"):
            state_timer = (self.anim_time * 0.35) % 1.0

        if char_info["char_type"] == "gashadokuro":
            self._render_boss(self.model_camera, 0.0, 0.0, 0.0)
        else:
            render_voxel_humanoid(
                self.screen, self.model_camera,
                0.0, 0.0, 0.0,
                facing_x, facing_y,
                state, state_timer,
                is_alive=True,
                char_type=char_info["char_type"],
                walk_timer=walk_timer,
                alpha=255,
                is_moving=is_moving
            )

        if self.show_hud:
            self._draw_models_hud(char_info)

    def _render_boss(self, camera, wx, wy, wz):
        """Renderiza o Oni Gashadokuro no estúdio 3D unificado."""
        if getattr(self, "_boss_instance", None) is None:
            from src.entities.boss_oni import BossOni
            self._boss_instance = BossOni(wx, wy)
        boss = self._boss_instance
        boss.wx = wx
        boss.wy = wy
        boss.wz = wz
        boss.time = self.anim_time

        pose_to_phase = {
            "IDLE": 0, "WALK": 1, "ATTACK": 2, "RECOVERY": 3, "INTRO": 4, "VICTORY": 4
        }
        phase_idx = pose_to_phase.get(self.current_pose, 0)
        if boss.phase != phase_idx:
            boss.set_phase(phase_idx)

        if self.current_pose == "IDLE":
            boss.pose["stomp"] = (math.sin(self.anim_time * 2.2) * 0.5 + 0.5) * 0.35
            boss.pose["head_up"] = 1.0 + 0.08 * math.sin(self.anim_time * 1.5)
        elif self.current_pose == "WALK":
            boss.pose["head_up"] = 0.8 + 0.2 * math.sin(self.anim_time * 2.0)
        elif self.current_pose == "ATTACK":
            boss.pose["head_up"] = 0.4 + 0.6 * (math.sin(self.anim_time * 3.0) * 0.5 + 0.5)
        elif self.current_pose == "RECOVERY":
            boss.pose["raise"] = 0.3 + 0.7 * (math.sin(self.anim_time * 2.0) * 0.5 + 0.5)
        elif self.current_pose == "INTRO":
            boss.pose["jaw"] = (math.sin(self.anim_time * 5.0) * 0.5 + 0.5) * 0.32
        elif self.current_pose == "VICTORY":
            boss.pose["jaw"] = (math.sin(self.anim_time * 8.0) * 0.5 + 0.5) * 0.45

        boss.render(self.screen, camera, self.anim_time)

    def _draw_model_pedestal(self):
        sx0, sy0 = self.model_camera.apply(0.0, 0.0, 0.0)
        shadow_w = int(68 * self.model_camera.zoom)
        shadow_h = int(32 * self.model_camera.zoom * (math.sin(self.model_camera.elevation) / 0.5))
        shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (6, 8, 12, 190), (0, 0, shadow_w * 2, shadow_h * 2))
        self.screen.blit(shadow_surf, (sx0 - shadow_w, sy0 - shadow_h // 2))

        # Pedestal de cantaria circular
        char_info = CHARACTERS[self.char_keys[self.current_char_idx]]
        is_colossal = (char_info["char_type"] == "gashadokuro")
        num_segments = 32 if is_colossal else 28
        radius = 1.65 if is_colossal else 0.70
        top_pts = [self.model_camera.apply(math.cos(i / num_segments * math.pi * 2) * radius,
                                           math.sin(i / num_segments * math.pi * 2) * radius, 0.0)
                   for i in range(num_segments)]
        if len(top_pts) >= 3:
            pygame.draw.polygon(self.screen, (34, 32, 38), top_pts)
            pygame.draw.polygon(self.screen, (140, 110, 60), top_pts, max(1, int(1.5 * self.model_camera.zoom)))

    def _draw_models_hud(self, char_info: dict):
        # Sidebar esquerda: lista dos 20 combatentes
        sb_w = 230
        sb_surf = pygame.Surface((sb_w, self.height - 44), pygame.SRCALPHA)
        sb_surf.fill((16, 18, 24, 235))
        self.screen.blit(sb_surf, (0, 44))
        pygame.draw.line(self.screen, (55, 60, 75), (sb_w, 44), (sb_w, self.height), 2)

        title = self.font_header.render(f"COMBATENTES ({len(self.char_keys)})", True, (240, 205, 90))
        self.screen.blit(title, (14, 52))

        self.char_btn_rects = []
        btn_y = 78
        btn_h = 27
        for idx, key in enumerate(self.char_keys):
            info = CHARACTERS[key]
            rect = pygame.Rect(8, btn_y, sb_w - 16, btn_h)
            self.char_btn_rects.append(rect)
            is_sel = (idx == self.current_char_idx)

            if is_sel:
                pygame.draw.rect(self.screen, (45, 52, 70), rect, border_radius=4)
                pygame.draw.rect(self.screen, (230, 195, 90), rect, width=2, border_radius=4)
            else:
                pygame.draw.rect(self.screen, (22, 26, 34), rect, border_radius=4)

            name_col = (255, 255, 255) if is_sel else (175, 180, 195)
            name_s = self.font_body.render(f"{idx+1}. {info['name']}", True, name_col)
            self.screen.blit(name_s, (rect.x + 8, rect.centery - 6))
            btn_y += btn_h + 3

        # Painel Superior Direito: Ficha Técnica do Lutador
        card_w, card_h = 380, 150
        card_x = self.width - card_w - 18
        card_y = 54
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((16, 18, 24, 230))
        self.screen.blit(card_surf, (card_x, card_y))
        pygame.draw.rect(self.screen, (220, 180, 80), (card_x, card_y, card_w, card_h), 2, border_radius=6)

        name_s = self.font_title.render(char_info["name"].upper(), True, (255, 255, 255))
        self.screen.blit(name_s, (card_x + 14, card_y + 10))
        sub_s = self.font_small.render(char_info["title"], True, (230, 200, 120))
        self.screen.blit(sub_s, (card_x + 14, card_y + 34))

        w_s = self.font_body.render(f"Arma: {char_info['weapon']}", True, (160, 215, 255))
        self.screen.blit(w_s, (card_x + 14, card_y + 58))

        # Descrição multiline
        desc_lines = self._wrap_text(char_info["description"], self.font_small, card_w - 28)
        for i, line in enumerate(desc_lines[:3]):
            l_s = self.font_small.render(line, True, (185, 190, 200))
            self.screen.blit(l_s, (card_x + 14, card_y + 82 + i * 16))

        # Barra inferior de Poses e Controles
        self._draw_models_bottom_bar()

    def _draw_models_bottom_bar(self):
        bar_w = self.width - 248
        bar_x = 240
        bar_h = 58
        bar_y = self.height - bar_h - 10

        bar_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        bar_surf.fill((16, 18, 24, 230))
        self.screen.blit(bar_surf, (bar_x, bar_y))
        pygame.draw.rect(self.screen, (55, 60, 75), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=6)

        # Botões de pose 1-6
        self.pose_btn_rects = []
        px = bar_x + 12
        for idx, pose_name in enumerate(POSES):
            rect = pygame.Rect(px, bar_y + 12, 70, 32)
            self.pose_btn_rects.append((pose_name, rect))
            is_active = (pose_name == self.current_pose)
            col = (45, 52, 70) if is_active else (24, 28, 36)
            border = (230, 195, 90) if is_active else (48, 54, 66)
            pygame.draw.rect(self.screen, col, rect, border_radius=4)
            pygame.draw.rect(self.screen, border, rect, 1, border_radius=4)
            txt = self.font_small.render(f"[{idx+1}] {pose_name[:5]}", True, (255, 255, 255) if is_active else (160, 165, 175))
            self.screen.blit(txt, (rect.x + 6, rect.centery - 6))
            px += 76

        info_txt = self.font_small.render(
            f"Foco: [F] {self.current_focus.upper()} | Órbita: [Mouse E] | Pan: [Mouse D] | Turntable: [Space] {'ATIVO' if self.turntable_active else 'OFF'}",
            True, (200, 210, 225)
        )
        self.screen.blit(info_txt, (px + 14, bar_y + 20))

    # -------------------------------------------------------------------------
    # Renderização: Modo [F2] Arenas
    # -------------------------------------------------------------------------
    def _render_arenas_mode(self):
        bg_col = getattr(self.game_map, "bg_color", (14, 16, 20)) if self.game_map else (14, 16, 20)
        self.screen.fill(bg_col)

        if self.game_map:
            self._draw_arena_world(self.game_map, self.arena_camera)

        if self.show_hud:
            self._draw_arenas_hud()

    def _draw_arena_world(self, game_map, camera):
        # 1. Terreno estático/dinâmico
        game_map.render_terrain(self.screen, camera, self.anim_time)

        # Perigos de solo (Pentagrama, Gêiseres de Miasma, Vórtice de Almas, etc.)
        if hasattr(game_map, "render_ground_hazards"):
            try:
                game_map.render_ground_hazards(self.screen, camera, self.anim_time)
            except Exception:
                pass

        # 2. Props, Obstáculos e Névoa Volumétrica
        draw_order = []
        if self.show_props:
            for collection_name in ("rocks", "trees", "torii_gates", "lanterns", "buildings", "bamboos", "solid_props"):
                items = getattr(game_map, collection_name, [])
                for item in items:
                    wx = getattr(item, "wx", 0.0)
                    wy = getattr(item, "wy", 0.0)
                    depth = iso_depth(wx, wy, camera.azimuth)
                    draw_order.append((depth, item))

        # Entidades dinâmicas de hazards (Almas Sombrias, Espíritos, Zumbis, Kitsune, etc.)
        for h in getattr(game_map, "hazards", []):
            if hasattr(h, "get_render_items"):
                try:
                    for depth, _, obj in h.get_render_items(camera):
                        draw_order.append((depth, obj))
                except Exception:
                    pass

        # Névoa Volumétrica 3D
        if self.show_fog and getattr(self, "arena_fog", None):
            for depth, _, puff in self.arena_fog.queue_items(camera):
                draw_order.append((depth, puff))

        draw_order.sort(key=lambda pair: pair[0])
        for _, item in draw_order:
            render_fn = getattr(item, "render", None)
            if render_fn:
                try:
                    render_fn(self.screen, camera, self.anim_time)
                except TypeError:
                    render_fn(self.screen, camera)


        # 3. Overhead hazards
        game_map.render_overhead(self.screen, camera, self.anim_time)

        # 4. Clima / folhas e pétalas flutuantes
        if self.show_weather:
            for leaf in getattr(self, "arena_leaves", []):
                try:
                    leaf.render(self.screen, camera)
                except Exception:
                    pass

        # 5. Iluminação, vinheta e atmosfera 2.5D
        if self.show_lighting and getattr(self, "arena_lighting", None):
            try:
                self.arena_lighting.render(self.screen, camera, self.anim_time)
            except Exception:
                pass

    def _draw_arenas_hud(self):
        # Sidebar esquerda: lista das arenas
        sb_w = 230
        sb_surf = pygame.Surface((sb_w, self.height - 44), pygame.SRCALPHA)
        sb_surf.fill((16, 18, 24, 235))
        self.screen.blit(sb_surf, (0, 44))
        pygame.draw.line(self.screen, (55, 60, 75), (sb_w, 44), (sb_w, self.height), 2)

        title = self.font_header.render(f"ARENAS ({len(self.arena_keys)})", True, (240, 205, 90))
        self.screen.blit(title, (14, 52))

        self.arena_btn_rects = []
        btn_y = 78
        btn_h = 26
        for idx, key in enumerate(self.arena_keys):
            meta = ARENA_DISPLAY_INFO.get(key, {"title": key, "subtitle": "—", "fighter": "—"})
            rect = pygame.Rect(8, btn_y, sb_w - 16, btn_h)
            self.arena_btn_rects.append(rect)
            is_sel = (idx == self.current_arena_idx)

            if is_sel:
                pygame.draw.rect(self.screen, (45, 52, 70), rect, border_radius=4)
                pygame.draw.rect(self.screen, (230, 195, 90), rect, width=2, border_radius=4)
            else:
                pygame.draw.rect(self.screen, (22, 26, 34), rect, border_radius=4)

            name_col = (255, 255, 255) if is_sel else (175, 180, 195)
            name_s = self.font_body.render(f"{idx+1}. {meta['title']}", True, name_col)
            self.screen.blit(name_s, (rect.x + 8, rect.centery - 6))
            btn_y += btn_h + 3

        # Painel Superior Direito: Metadados da Arena
        cur_key = self.arena_keys[self.current_arena_idx]
        cur_meta = ARENA_DISPLAY_INFO.get(cur_key, {"title": cur_key, "subtitle": "—", "fighter": "—"})

        card_w, card_h = 360, 105
        card_x = self.width - card_w - 18
        card_y = 54
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((16, 18, 24, 230))
        self.screen.blit(card_surf, (card_x, card_y))
        pygame.draw.rect(self.screen, (220, 180, 80), (card_x, card_y, card_w, card_h), 2, border_radius=6)

        t_s = self.font_title.render(cur_meta["title"].upper(), True, (255, 255, 255))
        self.screen.blit(t_s, (card_x + 14, card_y + 10))
        sub_s = self.font_small.render(cur_meta["subtitle"], True, (230, 200, 120))
        self.screen.blit(sub_s, (card_x + 14, card_y + 36))
        f_s = self.font_body.render(f"Guerreiro-Tema: {cur_meta['fighter']}", True, (160, 210, 255))
        self.screen.blit(f_s, (card_x + 14, card_y + 60))

        # Telemetria inferior da câmera livre
        self._draw_arenas_bottom_bar()

    def _draw_arenas_bottom_bar(self):
        bar_w = self.width - 248
        bar_x = 240
        bar_h = 58
        bar_y = self.height - bar_h - 10

        bar_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        bar_surf.fill((16, 18, 24, 230))
        self.screen.blit(bar_surf, (bar_x, bar_y))
        pygame.draw.rect(self.screen, (55, 60, 75), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=6)

        cam = self.arena_camera
        t1 = self.font_small.render(
            f"FREE-CAM 6-EIXOS: Posição ({cam.wx:.1f}, {cam.wy:.1f}, Z:{cam.wz:.1f}) | Azimute: {int(math.degrees(cam.azimuth))%360}° | Inclinação: {int(math.degrees(cam.elevation))}° | Zoom: {cam.zoom:.2f}x | FPS: {int(self.fps)}",
            True, (240, 215, 120)
        )
        self.screen.blit(t1, (bar_x + 14, bar_y + 10))

        t2 = self.font_small.render(
            f"Voo: [WASD] Plano | [E/Q] Alt | [Mouse] Órbita || Toggles: [L] Luz {'ON' if self.show_lighting else 'OFF'} | [N] Névoa {'ON' if self.show_fog else 'OFF'} | [K] Clima {'ON' if self.show_weather else 'OFF'} | [O] Props | [P] Pausar",
            True, (175, 185, 200)
        )
        self.screen.blit(t2, (bar_x + 14, bar_y + 32))

    # -------------------------------------------------------------------------
    # Renderização: Modo [F3] Composição & Staging
    # -------------------------------------------------------------------------
    def _render_staging_mode(self):
        bg_col = getattr(self.staging_map, "bg_color", (14, 16, 20)) if self.staging_map else (14, 16, 20)
        self.screen.fill(bg_col)

        if self.staging_map:
            # 1. Desenha terreno
            self.staging_map.render_terrain(self.screen, self.staging_camera, self.anim_time)

            # 2. Desenha props e o combatente ordenados por profundidade Y-Sort
            actor_depth = iso_depth(self.actor_wx, self.actor_wy, self.staging_camera.azimuth)
            draw_order = [(actor_depth, "actor")]

            if self.show_props:
                for collection_name in ("rocks", "trees", "torii_gates", "lanterns", "buildings", "bamboos"):
                    items = getattr(self.staging_map, collection_name, [])
                    for item in items:
                        wx = getattr(item, "wx", 0.0)
                        wy = getattr(item, "wy", 0.0)
                        depth = iso_depth(wx, wy, self.staging_camera.azimuth)
                        draw_order.append((depth, item))

            if self.show_fog and getattr(self, "staging_fog", None):
                for depth, _, puff in self.staging_fog.queue_items(self.staging_camera):
                    draw_order.append((depth, puff))

            draw_order.sort(key=lambda pair: pair[0])
            for _, item in draw_order:
                if item == "actor":
                    self._draw_staging_actor()
                else:
                    render_fn = getattr(item, "render", None)
                    if render_fn:
                        try:
                            render_fn(self.screen, self.staging_camera, self.anim_time)
                        except TypeError:
                            render_fn(self.screen, self.staging_camera)

            # 3. Overhead, Clima e Iluminação 2.5D
            self.staging_map.render_overhead(self.screen, self.staging_camera, self.anim_time)
            if self.show_weather:
                for leaf in getattr(self, "staging_leaves", []):
                    try:
                        leaf.render(self.screen, self.staging_camera)
                    except Exception:
                        pass
            if self.show_lighting and getattr(self, "staging_lighting", None):
                try:
                    self.staging_lighting.render(self.screen, self.staging_camera, self.anim_time)
                except Exception:
                    pass

        if self.show_hud:
            self._draw_staging_hud()

    def _draw_staging_actor(self):
        # Sombra suave sob os pés do combatente no terreno da arena
        sx0, sy0 = self.staging_camera.apply(self.actor_wx, self.actor_wy, 0.0)
        shadow_w = int(32 * self.staging_camera.zoom)
        shadow_h = int(16 * self.staging_camera.zoom * (math.sin(self.staging_camera.elevation) / 0.5))
        shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (8, 10, 14, 180), (0, 0, shadow_w * 2, shadow_h * 2))
        self.screen.blit(shadow_surf, (sx0 - shadow_w, sy0 - shadow_h // 2))

        # Renderização do combatente posicionado no mapa
        char_info = CHARACTERS[self.char_keys[self.current_char_idx]]
        state = self.current_pose
        is_moving = (self.current_pose == "WALK")
        walk_timer = self.anim_time * 2.6 if is_moving else self.anim_time
        state_timer = 0.0
        if self.current_pose == "ATTACK":
            state_timer = 0.08 + (math.sin(self.anim_time * 4.0) * 0.5 + 0.5) * 0.12
        elif self.current_pose == "RECOVERY":
            state_timer = 0.35
        elif self.current_pose in ("INTRO", "VICTORY"):
            state_timer = (self.anim_time * 0.35) % 1.0

        if char_info["char_type"] == "gashadokuro":
            self._render_boss(self.staging_camera, self.actor_wx, self.actor_wy, self.actor_wz)
        else:
            render_voxel_humanoid(
                self.screen, self.staging_camera,
                self.actor_wx, self.actor_wy, self.actor_wz,
                self.actor_facing_x, self.actor_facing_y,
                state, state_timer,
                is_alive=True,
                char_type=char_info["char_type"],
                walk_timer=walk_timer,
                alpha=255,
                is_moving=is_moving
            )

        # Indicador de seleção de ator
        if self.actor_control_active:
            ret_sx, ret_sy = self.staging_camera.apply(self.actor_wx, self.actor_wy, 0.85)
            pygame.draw.polygon(self.screen, (255, 215, 60), [(ret_sx, ret_sy), (ret_sx - 6, ret_sy - 10), (ret_sx + 6, ret_sy - 10)])

    def _draw_staging_hud(self):
        char_info = CHARACTERS[self.char_keys[self.current_char_idx]]
        cur_arena_key = self.arena_keys[self.current_arena_idx]
        arena_meta = ARENA_DISPLAY_INFO.get(cur_arena_key, {"title": cur_arena_key, "subtitle": "—", "fighter": "—"})

        # Painel Superior Direito: Staging Info
        card_w, card_h = 380, 115
        card_x = self.width - card_w - 18
        card_y = 54
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((16, 18, 24, 235))
        self.screen.blit(card_surf, (card_x, card_y))
        pygame.draw.rect(self.screen, (230, 195, 80), (card_x, card_y, card_w, card_h), 2, border_radius=6)

        t1 = self.font_header.render(f"COMBATENTE: {char_info['name'].upper()} [{self.current_char_idx+1}/20]", True, (255, 230, 100))
        self.screen.blit(t1, (card_x + 14, card_y + 10))
        t2 = self.font_body.render(f"Cenário: {arena_meta['title']} [{self.current_arena_idx+1}/{len(self.arena_keys)}]", True, (160, 215, 255))
        self.screen.blit(t2, (card_x + 14, card_y + 36))
        t3 = self.font_small.render(f"Posição do Ator: ({self.actor_wx:.2f}, {self.actor_wy:.2f}, Z:{self.actor_wz:.2f})", True, (200, 210, 225))
        self.screen.blit(t3, (card_x + 14, card_y + 60))
        mode_txt = "MODO DE CONTROLE: [C] ATOR (WASD / Setas)" if self.actor_control_active else "MODO DE CONTROLE: [C] CÂMERA LIVRE (WASD / Mouse)"
        t4 = self.font_body.render(mode_txt, True, (255, 140, 80) if self.actor_control_active else (100, 220, 180))
        self.screen.blit(t4, (card_x + 14, card_y + 84))

        # Barra inferior de staging
        bar_w = self.width - 36
        bar_x = 18
        bar_h = 48
        bar_y = self.height - bar_h - 10

        bar_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        bar_surf.fill((16, 18, 24, 230))
        self.screen.blit(bar_surf, (bar_x, bar_y))
        pygame.draw.rect(self.screen, (55, 60, 75), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=6)

        info = self.font_small.render(
            "Trocar Lutador: [ / ] | Trocar Arena: Tab | Poses: [1-6] | Alternar Controle Ator/Câmera: [C] | Zoom: Scroll | Snapshot: [F12]",
            True, (220, 225, 235)
        )
        self.screen.blit(info, (bar_x + 16, bar_y + 16))

    # -------------------------------------------------------------------------
    # Barra de Abas e Cabeçalho Superior Unificado
    # -------------------------------------------------------------------------
    def _render_header_bar(self):
        bar_h = 44
        bar_surf = pygame.Surface((self.width, bar_h), pygame.SRCALPHA)
        bar_surf.fill((12, 14, 18, 250))
        self.screen.blit(bar_surf, (0, 0))
        pygame.draw.line(self.screen, (55, 60, 75), (0, bar_h), (self.width, bar_h), 2)

        # Título da Ferramenta
        title_s = self.font_header.render("SAMURAI EDGE", True, (240, 205, 90))
        sub_s = self.font_small.render("STUDIO 3D UNIFICADO", True, (165, 175, 195))
        self.screen.blit(title_s, (14, 6))
        self.screen.blit(sub_s, (14, 25))

        # Abas Centrais: [F1] Modelos | [F2] Arenas | [F3] Staging
        tab_defs = [
            (MODE_MODELS, "[F1] MODELOS (20)", 165),
            (MODE_ARENAS, "[F2] ARENAS (20+)", 165),
            (MODE_STAGING, "[F3] COMPOSIÇÃO & STAGING", 220),
        ]

        tx = 250
        self.tab_rects = {}
        for mode_key, label, tab_w in tab_defs:
            rect = pygame.Rect(tx, 6, tab_w, 32)
            self.tab_rects[mode_key] = rect
            is_active = (self.mode == mode_key)

            if is_active:
                pygame.draw.rect(self.screen, (45, 52, 70), rect, border_radius=4)
                pygame.draw.rect(self.screen, (235, 195, 60), rect, width=2, border_radius=4)
                text_col = (255, 235, 140)
            else:
                pygame.draw.rect(self.screen, (20, 22, 28), rect, border_radius=4)
                pygame.draw.rect(self.screen, (40, 45, 55), rect, width=1, border_radius=4)
                text_col = (160, 168, 182)

            lbl = self.font_body.render(label, True, text_col)
            self.screen.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.centery - 6))
            tx += tab_w + 10

        # Botão Snapshot F12 no canto direito
        snap_rect = pygame.Rect(self.width - 150, 6, 134, 32)
        pygame.draw.rect(self.screen, (28, 32, 42), snap_rect, border_radius=4)
        pygame.draw.rect(self.screen, (65, 75, 95), snap_rect, 1, border_radius=4)
        snap_lbl = self.font_small.render("[F12] SNAPSHOT", True, (215, 225, 245))
        self.screen.blit(snap_lbl, (snap_rect.centerx - snap_lbl.get_width() // 2, snap_rect.centery - 5))

    # -------------------------------------------------------------------------
    # Utilidades
    # -------------------------------------------------------------------------
    def _wrap_text(self, text: str, font: pygame.font.Font, max_w: int) -> list[str]:
        words = text.split(" ")
        lines = []
        cur_line = []
        for w in words:
            test_line = " ".join(cur_line + [w])
            if font.size(test_line)[0] <= max_w:
                cur_line.append(w)
            else:
                if cur_line:
                    lines.append(" ".join(cur_line))
                cur_line = [w]
        if cur_line:
            lines.append(" ".join(cur_line))
        return lines

    def snapshot(self, output_path: str):
        self.render()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pygame.image.save(self.screen, output_path)
        print(f"[StudioInspector] Snapshot salvo em: {output_path}")

    def run(self):
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


# =============================================================================
# CLI
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Studio 3D Unificado — Samurai Edge")
    parser.add_argument("--mode", choices=[MODE_MODELS, MODE_ARENAS, MODE_STAGING], default=MODE_MODELS, help="Modo inicial")
    parser.add_argument("--char", type=str, default="valerius", help="Combatente inicial")
    parser.add_argument("--arena", type=str, default="gothic_cemetery", help="Arena inicial")
    parser.add_argument("--snapshot", type=str, default=None, help="Salva snapshot PNG e sai")
    parser.add_argument("--width", type=int, default=1280, help="Largura da janela")
    parser.add_argument("--height", type=int, default=720, help="Altura da janela")
    parser.add_argument("--headless", action="store_true", help="Executa sem janela gráfica")
    args = parser.parse_args()

    is_headless = args.headless or (args.snapshot is not None)
    studio = StudioInspector(
        width=args.width,
        height=args.height,
        initial_mode=args.mode,
        char_key=args.char,
        arena_key=args.arena,
        headless=is_headless
    )

    if args.snapshot:
        studio.snapshot(args.snapshot)
        pygame.quit()
        sys.exit(0)
    else:
        studio.run()


if __name__ == "__main__":
    main()
