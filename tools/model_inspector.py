#!/usr/bin/env python3
"""
tools/model_inspector.py - Model Inspector 3D para Samurai Edge

Visualizador interativo 3D dedicado para comparar e inspecionar os modelos
dos combatentes (Okuni, Kasumi e Saitou) nas 4 técnicas de evolução visual:
  - T1: Micro-voxels e Texturas Procedurais Ricas
  - T2: Mapeamento UV / Pixel Art em Cubos
  - T3: Voxel Base + Overlays 2.5D / Decalques
  - T4: Modelo 3D Tradicional Low-Poly com Cel Shading

Suporta órbita 360° livre (azimute e elevação), zoom suave, poses alternáveis,
modo vitrine (turntable automático) e captura de snapshots/turntables.
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

from src.config import HALF_TILE_W, HALF_TILE_H
from src.isometric.iso_math import rotate_xy, PIXELS_PER_Z
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric.voxel_renderer import draw_voxel_box


# =============================================================================
# CÂMERA ORBITAL 3D DO INSPECTOR
# =============================================================================
class InspectorCamera:
    """
    Câmera de órbita 3D livre com controle de Azimute (360°), Elevação (Pitch)
    e Zoom, 100% compatível com a interface esperada por render_voxel_humanoid.
    """
    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.screen_x = screen_w // 2
        self.screen_y = int(screen_h * 0.58)

        # Foco no mundo (centro do modelo: em z ~ 0.4 para focar na cintura/peitoral)
        self.wx = 0.0
        self.wy = 0.0
        self.target_z = 0.45

        # Ângulos de rotação orbital
        self.azimuth = 0.0              # Radianos (0.0 = ângulo isométrico canônico)
        self.elevation = math.radians(30.0) # Inclinação (30° = clássico 2:1)
        self.zoom = 2.8                 # Escala de aproximação

        # Parâmetros de compatibilidade com o motor do jogo
        self.ground_z = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
        self.height_fn = None

    def reset(self):
        """Restaura os valores para o ângulo canônico de visualização."""
        self.azimuth = 0.0
        self.elevation = math.radians(30.0)
        self.zoom = 2.8
        self.screen_x = self.screen_w // 2
        self.screen_y = int(self.screen_h * 0.58)

    def rotate_orbit(self, d_azimuth: float, d_elevation: float):
        """Aplica rotação horizontal e vertical."""
        self.azimuth = (self.azimuth + d_azimuth) % (math.pi * 2.0)
        # Limita a elevação entre 6° e 84° para evitar inversão de câmera
        min_elev = math.radians(6.0)
        max_elev = math.radians(84.0)
        self.elevation = max(min_elev, min(max_elev, self.elevation + d_elevation))

    def zoom_in(self, factor: float = 1.15):
        self.zoom = max(0.8, min(7.5, self.zoom * factor))

    def zoom_out(self, factor: float = 1.15):
        self.zoom = max(0.8, min(7.5, self.zoom / factor))

    def apply(self, wx: float, wy: float, wz: float = 0.0) -> tuple[int, int]:
        """
        Projeta coordenadas 3D de mundo para a tela 2D usando a órbita da câmera.
        Calcula rotação em torno do centro do personagem e compensa elevação.
        """
        # Deslocamento em relação ao alvo da câmera
        rx = wx - self.wx
        ry = wy - self.wy
        rz = wz - self.target_z

        # Rotação horizontal (azimute em torno do eixo Z)
        c, s = math.cos(self.azimuth), math.sin(self.azimuth)
        rot_x = rx * c - ry * s
        rot_y = rx * s + ry * c

        # Relação de projeção considerando a elevação (padrão 30° -> sen=0.5, cos=0.866)
        sin_elev = math.sin(self.elevation)
        cos_elev = math.cos(self.elevation)

        # Projeção isométrica/axonometrica orbital
        # Horizontal: baseado na diferença rot_x - rot_y
        iso_x = (rot_x - rot_y) * HALF_TILE_W
        # Vertical: soma de rot_x + rot_y escalada pela inclinação, menos altura Z
        elev_ratio = sin_elev / 0.5  # 1.0 quando elevation = 30°
        z_ratio = cos_elev / 0.866   # 1.0 quando elevation = 30°

        iso_y = (rot_x + rot_y) * (HALF_TILE_H * elev_ratio) - (rz * (PIXELS_PER_Z * z_ratio))

        dx = iso_x * self.zoom
        dy = iso_y * self.zoom

        final_x = int(dx + self.screen_x + self.shake_offset_x)
        final_y = int(dy + self.screen_y + self.shake_offset_y)
        return final_x, final_y


# =============================================================================
# DEFINIÇÃO DOS PERSONAGENS E TÉCNICAS
# =============================================================================
CHARACTERS = {
    "okuni": {
        "name": "Okuni (Dançarina Kabuki)",
        "char_type": "okuni",
        "title": "Mestra dos Leques Tessen & Teatro Sagrado de Izumo",
        "description": "Quimono carmim/dourado em camadas, kanzashi no penteado shimada e maquiagem branca.",
        "concept_file": "okuni_concept.jpg",
        "color_accent": (210, 40, 55),
    },
    "kasumi": {
        "name": "Kasumi (Kunoichi da Névoa)",
        "char_type": "kasumi",
        "title": "Assassina Shinobi & Dançarina das Sombras de Koga",
        "description": "Armadura cromada, colete com fivelas, cachecol drapeado e adagas duplas.",
        "concept_file": "kasumi_concept.jpg",
        "color_accent": (140, 180, 215),
    },
    "saitou": {
        "name": "Saitou (Capitão Shinsengumi)",
        "char_type": "saitou",
        "title": "Lobo de Mibu & Capitão da 3ª Divisão",
        "description": "Haori azul-celeste com estampa dandara branca e postura frontal mortal Gatotsu.",
        "concept_file": "saitou_concept.jpg",
        "color_accent": (110, 195, 230),
    },
    "kenshi": {
        "name": "Kenshi (Espadachim Errante)",
        "char_type": "kenshi",
        "title": "Mestre do Iaijutsu & Saque Veloz da Katana",
        "description": "Quimono carmim tradicional com hakama escura e fita vermelha no rabo de cavalo.",
        "concept_file": "kenshi_concept.jpg",
        "color_accent": (220, 50, 60),
    },
    "musashi": {
        "name": "Musashi (O Invencível)",
        "char_type": "musashi",
        "title": "Criador do Estilo das Duas Espadas Niten Ichi-ryu",
        "description": "Quimono azul-escuro rasgado de batalha, katana longa e wakizashi empunhadas.",
        "concept_file": "musashi_concept.jpg",
        "color_accent": (70, 130, 200),
    },
    "hanzo": {
        "name": "Hanzo (Mestre Ninja de Iga)",
        "char_type": "hanzo",
        "title": "Líder das Sombras & Mestre do Ninjutsu",
        "description": "Traje shinobi preto com armadura de malha, máscara demoníaca menpo e ninjato.",
        "concept_file": "hanzo_concept.jpg",
        "color_accent": (230, 190, 50),
    },
    "murasaki": {
        "name": "Murasaki (Ceifadora das Sombras)",
        "char_type": "murasaki",
        "title": "Kunoichi da Foice Kusarigama com Corrente",
        "description": "Traje tático púrpura esguio, máscara refinada e foice curva de corte crescente.",
        "concept_file": "murasaki_concept.jpg",
        "color_accent": (180, 90, 235),
    },
    "tomoe": {
        "name": "Tomoe (Arqueira Sagrada)",
        "char_type": "tomoe",
        "title": "Guardiã do Santuário de Kyoto & Mestra Kyudo",
        "description": "Traje cerimonial Miko com hakama vermelho, tiara sagrada e arco longo Yumi.",
        "concept_file": "tomoe_concept.jpg",
        "color_accent": (230, 70, 80),
    },
    "teppo": {
        "name": "Teppo (Atirador Tanegashima)",
        "char_type": "teppo",
        "title": "Mestre dos Mosquetes de Fogo & Veterano de Nagashino",
        "description": "Colete de laca marrom, chapéu de ferro Jingasa e arcabuz de mecha longo.",
        "concept_file": "teppo_concept.jpg",
        "color_accent": (210, 150, 70),
    },
    "joe": {
        "name": "Joe (American Ninja)",
        "char_type": "joe",
        "title": "Combatente Tático Ocidental & Operador Shinobi",
        "description": "Traje tático camuflado com bandana de combate e katana tática.",
        "concept_file": "joe_concept.jpg",
        "color_accent": (120, 175, 100),
    },
    "anne": {
        "name": "Anne (Capitã Pirata)",
        "char_type": "anne",
        "title": "Rainha dos Mares do Sul & Duelo de Alfanje",
        "description": "Sobretudo bordô com fivelas de ouro, tricórnio com pluma e alfanje cortante.",
        "concept_file": "anne_concept.jpg",
        "color_accent": (220, 80, 90),
    },
    "julie": {
        "name": "Julie (Mosqueteira Real)",
        "char_type": "julie",
        "title": "Campeã de Esgrima de Paris & Florete Reluzente",
        "description": "Casaca azul-real francesa com gola de renda, chapéu com pluma e florete.",
        "concept_file": "julie_concept.jpg",
        "color_accent": (65, 140, 245),
    },
}

POSES = ["IDLE", "CONCEPT", "ATTACK"]


# =============================================================================
# MODEL INSPECTOR CORE
# =============================================================================
class ModelInspector:
    def __init__(self, width: int = 1280, height: int = 720, headless: bool = False):
        self.width = width
        self.height = height
        self.headless = headless

        if headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            os.environ["SDL_AUDIODRIVER"] = "dummy"

        pygame.init()
        pygame.display.set_caption("Samurai Edge — Model Inspector 3D (Character Evolution PoC)")

        flags = pygame.DOUBLEBUF | pygame.RESIZABLE if not headless else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        self.clock = pygame.time.Clock()

        self.camera = InspectorCamera(width, height)

        # Estado atual
        self.char_keys = list(CHARACTERS.keys())
        self.current_char_idx = 0
        self.current_pose_idx = 0  # 0=IDLE, 1=CONCEPT, 2=ATTACK
        self.model_version = "new"  # "new" = T1 Master/Evoluído, "original" = Modelo Canônico Base

        # Regiões clicáveis com mouse no HUD
        self.clickable_regions: list[tuple[pygame.Rect, callable]] = []

        # Controle de órbita do mouse
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.auto_rotate = False
        self.auto_rotate_speed = 0.5  # Radianos por segundo

        # Timers de animação
        self.anim_time = 0.0
        self.fps = 60.0

        # Fontes do HUD
        self.font_title = pygame.font.Font(None, 28)
        self.font_body = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)

        # Cache de imagem de conceito para referência comparativa
        self._concept_cache = {}

    @property
    def current_char_info(self) -> dict:
        return CHARACTERS[self.char_keys[self.current_char_idx]]

    @property
    def current_pose(self) -> str:
        return POSES[self.current_pose_idx]

    def select_character(self, idx: int):
        self.current_char_idx = idx % len(self.char_keys)

    def next_pose(self):
        self.current_pose_idx = (self.current_pose_idx + 1) % len(POSES)

    def set_model_version(self, version: str):
        if version in ("new", "original"):
            self.model_version = version

    def toggle_model_version(self):
        self.model_version = "original" if self.model_version == "new" else "new"

    def _load_concept_thumbnail(self, concept_file: str) -> pygame.Surface | None:
        """Carrega e escala a arte conceito para exibição no painel de referência."""
        if concept_file in self._concept_cache:
            return self._concept_cache[concept_file]

        path = os.path.join(ROOT, "assets", "concepts", concept_file)
        if not os.path.exists(path):
            return None

        try:
            raw = pygame.image.load(path)
            # Redimensiona mantendo proporção com largura de 140px
            w, h = raw.get_size()
            target_w = 140
            target_h = int(h * (target_w / w))
            thumb = pygame.transform.smoothscale(raw, (target_w, target_h))
            self._concept_cache[concept_file] = thumb
            return thumb
        except Exception:
            return None

    def draw_studio_pedestal(self, surface: pygame.Surface):
        """
        Desenha a plataforma circular de madeira/tatami sob o lutador
        com anéis concêntricos projetados pela câmera orbital.
        """
        # Sombra de oclusão direta de contato no chão
        sx0, sy0 = self.camera.apply(0.0, 0.0, 0.0)
        shadow_w = int(68 * self.camera.zoom)
        shadow_h = int(32 * self.camera.zoom * (math.sin(self.camera.elevation) / 0.5))
        shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (10, 10, 14, 180), (0, 0, shadow_w * 2, shadow_h * 2))
        surface.blit(shadow_surf, (sx0 - shadow_w, sy0 - shadow_h // 2))

        # Pedestal cilíndrico de madeira tradicional (fatiado em polígono circular)
        num_segments = 24
        radius = 0.65
        pedestal_h = 0.06

        top_points = []
        for i in range(num_segments):
            angle = (i / num_segments) * math.pi * 2.0
            px = math.cos(angle) * radius
            py = math.sin(angle) * radius
            top_points.append(self.camera.apply(px, py, 0.0))

        # Desenha a face superior do tablado
        if len(top_points) >= 3:
            # Cor de madeira escura nobre
            pygame.draw.polygon(surface, (45, 38, 32), top_points)
            # Aro decorativo dourado/bronze
            pygame.draw.polygon(surface, (110, 88, 52), top_points, max(1, int(1.5 * self.camera.zoom)))

            # Anel interior do tablado
            inner_points = []
            for i in range(num_segments):
                angle = (i / num_segments) * math.pi * 2.0
                px = math.cos(angle) * (radius * 0.75)
                py = math.sin(angle) * (radius * 0.75)
                inner_points.append(self.camera.apply(px, py, 0.002))
            pygame.draw.polygon(surface, (54, 46, 38), inner_points)
            pygame.draw.polygon(surface, (80, 68, 50), inner_points, 1)

    def _build_model_context(self, surface: pygame.Surface, char_type: str, state: str, state_timer: float, walk_timer: float, is_moving: bool):
        """Monta o contexto anatômico e cinemático do modelo do guerreiro."""
        from types import SimpleNamespace
        from src.isometric.voxel_rig import calc_leg_joints

        fx, fy = 1.0, 1.0
        n = math.hypot(fx, fy) or 1.0
        fx, fy = fx / n, fy / n
        px, py = -fy, fx

        wx, wy, wz = 0.0, 0.0, 0.0
        is_melee = (state == "ATTACK")
        atk_progress = 0.55 if is_melee else 0.0
        lunge_curve = math.sin(atk_progress * math.pi) if is_melee else 0.0

        idle_bob = math.sin(walk_timer * 2.8) * 0.015
        base_x = wx
        base_y = wy
        base_z = wz + idle_bob

        is_female = char_type in ("okuni", "kasumi")
        pelvis_w = 0.17 if is_female else 0.20
        pelvis_z = base_z + 0.44
        torso_z0 = pelvis_z + 0.13

        legs_data = calc_leg_joints(
            base_x, base_y, base_z, fx, fy, px, py,
            is_moving, walk_timer, is_melee, atk_progress,
            hip_width=0.075 if is_female else 0.09,
            is_female=is_female, char_type=char_type
        )

        c = SimpleNamespace(
            surface=surface,
            camera=self.camera,
            alpha=255,
            azimuth=getattr(self.camera, "azimuth", 0.0),
            base_x=base_x,
            base_y=base_y,
            base_z=base_z,
            fx=fx,
            fy=fy,
            px=px,
            py=py,
            pelvis_z=pelvis_z,
            pelvis_w=pelvis_w,
            walk_timer=walk_timer,
            is_moving=is_moving,
            is_melee=is_melee,
            atk_progress=atk_progress,
            lunge_curve=lunge_curve,
            legs_data=legs_data,
            state=state,
            state_timer=state_timer,
            extra_props={},
            torso_z=torso_z0,
            neck_z=torso_z0 + 0.26,
            head_z=torso_z0 + 0.31,
            head_w=0.13 if is_female else 0.15,
            sh_span=0.14 if is_female else 0.17
        )
        return c

    def draw_character(self, surface: pygame.Surface):
        """Renderiza o combatente selecionado utilizando o motor de Micro-voxels 3D."""
        char_info = self.current_char_info
        char_type = char_info["char_type"]

        # Orientação do guerreiro no mundo (frente padrão: 1.0, 1.0)
        facing_x, facing_y = 1.0, 1.0

        # Estado e animação conforme a pose selecionada
        state = "IDLE"
        state_timer = 0.0
        is_moving = False
        walk_timer = 0.0

        if self.current_pose == "IDLE":
            state = "IDLE"
            walk_timer = self.anim_time
        elif self.current_pose == "CONCEPT":
            state = "INTRO"
            state_timer = 0.55
        elif self.current_pose == "ATTACK":
            state = "ATTACK"
            state_timer = 0.08 + (math.sin(self.anim_time * 4.0) * 0.5 + 0.5) * 0.08

        # Renderização em Micro-voxels 3D (Despacho unificado e modular para as arenas)
        c = self._build_model_context(surface, char_type, state, state_timer, walk_timer, is_moving)
        from src.entities.microvoxel_roster import render_microvoxel_fighter
        render_microvoxel_fighter(c, char_type, version=self.model_version)

    def toggle_auto_rotate(self):
        self.auto_rotate = not self.auto_rotate

    def set_pose(self, pose_name: str):
        if pose_name in POSES:
            self.current_pose_idx = POSES.index(pose_name)

    def draw_hud(self, surface: pygame.Surface):
        """Renderiza interface moderna e minimalista de navegação com todas as opções clicáveis com o mouse."""
        self.clickable_regions.clear()
        w, h = self.width, self.height
        char_info = self.current_char_info
        accent = char_info["color_accent"]

        # =====================================================================
        # PAINEL SUPERIOR ESQUERDO: INFORMAÇÕES DO COMBATENTE
        # =====================================================================
        card_w, card_h = 420, 96
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (22, 24, 30, 235), (0, 0, card_w, card_h), border_radius=8)
        pygame.draw.rect(card_surf, accent, (0, 0, 5, card_h), border_top_left_radius=8, border_bottom_left_radius=8)
        pygame.draw.rect(card_surf, (55, 60, 75, 180), (0, 0, card_w, card_h), 1, border_radius=8)

        txt_name = self.font_title.render(char_info["name"], True, (245, 245, 250))
        txt_title = self.font_body.render(char_info["title"], True, accent)
        txt_desc = self.font_small.render(char_info["description"][:58] + "...", True, (175, 180, 195))

        card_surf.blit(txt_name, (16, 10))
        card_surf.blit(txt_title, (16, 36))
        card_surf.blit(txt_desc, (16, 62))
        surface.blit(card_surf, (20, 20))

        # Grade de seleção de combatentes: 12 Personagens em 2 linhas de 6 botões clicáveis
        btn_w, btn_h = 96, 26
        gap_x, gap_y = 6, 6
        grid_start_y = 124

        for i, key in enumerate(self.char_keys):
            col = i % 6
            row = i // 6
            btn_x = 20 + col * (btn_w + gap_x)
            btn_y = grid_start_y + row * (btn_h + gap_y)
            is_cur = (i == self.current_char_idx)

            # Registra região para clique de mouse
            hit_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            self.clickable_regions.append((hit_rect, lambda idx=i: self.select_character(idx)))

            bg_col = (*accent, 220) if is_cur else (28, 32, 42, 200)
            border_col = (255, 255, 255) if is_cur else (60, 65, 80)
            btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, bg_col, (0, 0, btn_w, btn_h), border_radius=4)
            pygame.draw.rect(btn_surf, border_col, (0, 0, btn_w, btn_h), 1, border_radius=4)

            short_name = CHARACTERS[key]['name'].split()[0]
            label = f"{i+1}. {short_name}"
            t_col = (255, 255, 255) if is_cur else (185, 190, 205)
            t_surf = self.font_small.render(label, True, t_col)
            btn_surf.blit(t_surf, (8, 5))
            surface.blit(btn_surf, (btn_x, btn_y))

        # =====================================================================
        # PAINEL SUPERIOR DIREITO: MOTOR MICRO-VOXELS 3D & CONTROLE DE VERSÃO/POSES
        # =====================================================================
        engine_w, engine_h = 420, 166
        engine_x = w - engine_w - 20
        engine_y = 20
        engine_surf = pygame.Surface((engine_w, engine_h), pygame.SRCALPHA)
        pygame.draw.rect(engine_surf, (22, 24, 30, 235), (0, 0, engine_w, engine_h), border_radius=8)
        pygame.draw.rect(engine_surf, (55, 60, 75, 180), (0, 0, engine_w, engine_h), 1, border_radius=8)

        t_header = self.font_body.render("MOTOR: MICRO-VOXELS 3D", True, (245, 205, 80))
        ver_badge = "NOVO (T1)" if self.model_version == "new" else "ORIGINAL"
        ver_color = (80, 235, 120) if self.model_version == "new" else (240, 175, 65)
        t_status = self.font_small.render(f"[ {ver_badge} ]", True, ver_color)
        engine_surf.blit(t_header, (14, 10))
        engine_surf.blit(t_status, (engine_w - 130, 12))

        # Botões de Comparação Direta: [NOVO (T1)] e [ORIGINAL]
        v_btn_w = 190
        v_btn_h = 28
        
        # Botão 1: NOVO (T1 Master)
        is_new = (self.model_version == "new")
        b_new_rect = pygame.Rect(engine_x + 14, engine_y + 36, v_btn_w, v_btn_h)
        self.clickable_regions.append((b_new_rect, lambda: self.set_model_version("new")))
        s_new = pygame.Surface((v_btn_w, v_btn_h), pygame.SRCALPHA)
        bg_new = (35, 65, 48, 240) if is_new else (28, 32, 42, 180)
        bd_new = (80, 235, 120) if is_new else (60, 65, 80)
        pygame.draw.rect(s_new, bg_new, (0, 0, v_btn_w, v_btn_h), border_radius=4)
        pygame.draw.rect(s_new, bd_new, (0, 0, v_btn_w, v_btn_h), 2 if is_new else 1, border_radius=4)
        t_new = self.font_small.render("NOVO (T1 Master) [M]", True, (255, 255, 255) if is_new else (165, 175, 190))
        s_new.blit(t_new, (18, 6))
        engine_surf.blit(s_new, (14, 36))

        # Botão 2: ORIGINAL (Canônico)
        is_orig = (self.model_version == "original")
        b_orig_rect = pygame.Rect(engine_x + 14 + v_btn_w + 12, engine_y + 36, v_btn_w, v_btn_h)
        self.clickable_regions.append((b_orig_rect, lambda: self.set_model_version("original")))
        s_orig = pygame.Surface((v_btn_w, v_btn_h), pygame.SRCALPHA)
        bg_orig = (65, 48, 28, 240) if is_orig else (28, 32, 42, 180)
        bd_orig = (240, 175, 65) if is_orig else (60, 65, 80)
        pygame.draw.rect(s_orig, bg_orig, (0, 0, v_btn_w, v_btn_h), border_radius=4)
        pygame.draw.rect(s_orig, bd_orig, (0, 0, v_btn_w, v_btn_h), 2 if is_orig else 1, border_radius=4)
        t_orig = self.font_small.render("ORIGINAL (Base) [M]", True, (255, 255, 255) if is_orig else (165, 175, 190))
        s_orig.blit(t_orig, (20, 6))
        engine_surf.blit(s_orig, (14 + v_btn_w + 12, 36))

        t_desc2 = self.font_small.render("Poses de Combate / Animacao:", True, (215, 220, 230))
        engine_surf.blit(t_desc2, (14, 74))

        # Botões clicáveis de Poses rápidas no painel superior: IDLE, CONCEPT, ATTACK
        pose_btn_w = 124
        pose_btn_h = 28
        pose_gap = 10
        for p_i, p_name in enumerate(POSES):
            p_bx = engine_x + 14 + p_i * (pose_btn_w + pose_gap)
            p_by = engine_y + 96
            p_rect = pygame.Rect(p_bx, p_by, pose_btn_w, pose_btn_h)
            self.clickable_regions.append((p_rect, lambda name=p_name: self.set_pose(name)))

            is_active_pose = (p_name == self.current_pose)
            p_surf = pygame.Surface((pose_btn_w, pose_btn_h), pygame.SRCALPHA)
            p_bg = (55, 70, 95, 230) if is_active_pose else (32, 36, 46, 180)
            p_border = (245, 205, 80) if is_active_pose else (60, 65, 80)
            pygame.draw.rect(p_surf, p_bg, (0, 0, pose_btn_w, pose_btn_h), border_radius=4)
            pygame.draw.rect(p_surf, p_border, (0, 0, pose_btn_w, pose_btn_h), 1, border_radius=4)

            p_lbl = f"> {p_name}" if is_active_pose else p_name
            p_col = (255, 255, 255) if is_active_pose else (175, 180, 195)
            p_txt = self.font_small.render(p_lbl, True, p_col)
            p_surf.blit(p_txt, (18, 6))
            engine_surf.blit(p_surf, (14 + p_i * (pose_btn_w + pose_gap), 96))

        t_shortcuts = self.font_small.render("Atalhos: [M]=Versao  |  [P]=Pose  |  [Espaco]=Girar", True, (150, 155, 170))
        engine_surf.blit(t_shortcuts, (14, 136))

        surface.blit(engine_surf, (engine_x, engine_y))

        # =====================================================================
        # PAINEL LATERAL DIREITO: THUMBNAIL DA ARTE CONCEITO
        # =====================================================================
        thumb = self._load_concept_thumbnail(char_info["concept_file"])
        if thumb is not None:
            thumb_w, thumb_h = thumb.get_size()
            box_x = w - thumb_w - 24
            box_y = engine_y + engine_h + 14
            box_surf = pygame.Surface((thumb_w + 8, thumb_h + 30), pygame.SRCALPHA)
            pygame.draw.rect(box_surf, (18, 20, 26, 210), (0, 0, thumb_w + 8, thumb_h + 30), border_radius=6)
            pygame.draw.rect(box_surf, (60, 65, 80), (0, 0, thumb_w + 8, thumb_h + 30), 1, border_radius=6)
            box_surf.blit(thumb, (4, 4))
            lbl = self.font_small.render("Concept Original", True, (190, 195, 205))
            box_surf.blit(lbl, (12, thumb_h + 8))
            surface.blit(box_surf, (box_x, box_y))

        # =====================================================================
        # PAINEL INFERIOR ESQUERDO: MÉTRICAS DA CÂMERA
        # =====================================================================
        cam_w, cam_h = 280, 72
        cam_surf = pygame.Surface((cam_w, cam_h), pygame.SRCALPHA)
        pygame.draw.rect(cam_surf, (18, 20, 26, 200), (0, 0, cam_w, cam_h), border_radius=6)
        pygame.draw.rect(cam_surf, (45, 50, 65), (0, 0, cam_w, cam_h), 1, border_radius=6)

        deg_azimuth = int(math.degrees(self.camera.azimuth))
        deg_elev = int(math.degrees(self.camera.elevation))
        rot_status = "LIGADO" if self.auto_rotate else "DESLIGADO"

        line1 = self.font_small.render(f"Azimute: {deg_azimuth:3d}*  |  Elevacao: {deg_elev:2d}*", True, (210, 215, 225))
        line2 = self.font_small.render(f"Zoom: {self.camera.zoom:.2f}x  |  FPS: {self.fps:.0f}", True, (170, 175, 185))
        line3 = self.font_small.render(f"Turntable: {rot_status}", True, (240, 190, 80) if self.auto_rotate else (130, 135, 145))

        cam_surf.blit(line1, (10, 8))
        cam_surf.blit(line2, (10, 28))
        cam_surf.blit(line3, (10, 48))
        surface.blit(cam_surf, (20, h - cam_h - 20))

        # =====================================================================
        # PAINEL INFERIOR DIREITO: CONTROLES E BOTÕES DE AÇÃO INTERATIVOS
        # =====================================================================
        ctrl_w, ctrl_h = 610, 72
        ctrl_x = w - ctrl_w - 20
        ctrl_y = h - ctrl_h - 20
        ctrl_surf = pygame.Surface((ctrl_w, ctrl_h), pygame.SRCALPHA)
        pygame.draw.rect(ctrl_surf, (18, 20, 26, 220), (0, 0, ctrl_w, ctrl_h), border_radius=6)
        pygame.draw.rect(ctrl_surf, (50, 55, 70), (0, 0, ctrl_w, ctrl_h), 1, border_radius=6)

        h1 = self.font_small.render("Mouse: Arrastar = Orbita 360* | Scroll = Zoom in/out | [M] = Alternar Modelo", True, (200, 205, 215))
        ctrl_surf.blit(h1, (12, 8))

        # Botões clicáveis interativos: Versão, Pose, Turntable, Reset Câmera
        # 1. Botão Versão (Novo vs Original)
        ver_rect = pygame.Rect(ctrl_x + 10, ctrl_y + 32, 142, 28)
        self.clickable_regions.append((ver_rect, self.toggle_model_version))
        v_surf = pygame.Surface((142, 28), pygame.SRCALPHA)
        v_bg = (35, 65, 48) if self.model_version == "new" else (65, 48, 28)
        v_bd = (80, 235, 120) if self.model_version == "new" else (240, 175, 65)
        pygame.draw.rect(v_surf, v_bg, (0, 0, 142, 28), border_radius=4)
        pygame.draw.rect(v_surf, v_bd, (0, 0, 142, 28), 1, border_radius=4)
        v_lbl = f"{'NOVO (T1)' if self.model_version == 'new' else 'ORIGINAL'} [M]"
        v_txt = self.font_small.render(v_lbl, True, (255, 255, 255))
        v_surf.blit(v_txt, (12, 6))
        ctrl_surf.blit(v_surf, (10, 32))

        # 2. Botão Pose
        pose_rect = pygame.Rect(ctrl_x + 158, ctrl_y + 32, 138, 28)
        self.clickable_regions.append((pose_rect, self.next_pose))
        p_surf = pygame.Surface((138, 28), pygame.SRCALPHA)
        pygame.draw.rect(p_surf, (36, 42, 58), (0, 0, 138, 28), border_radius=4)
        pygame.draw.rect(p_surf, (75, 85, 110), (0, 0, 138, 28), 1, border_radius=4)
        p_txt = self.font_small.render(f"Pose: {self.current_pose} [P]", True, (230, 235, 245))
        p_surf.blit(p_txt, (10, 6))
        ctrl_surf.blit(p_surf, (158, 32))

        # 3. Botão Turntable
        tt_rect = pygame.Rect(ctrl_x + 302, ctrl_y + 32, 155, 28)
        self.clickable_regions.append((tt_rect, self.toggle_auto_rotate))
        tt_surf = pygame.Surface((155, 28), pygame.SRCALPHA)
        tt_bg = (55, 45, 25) if self.auto_rotate else (36, 42, 58)
        tt_border = (230, 180, 50) if self.auto_rotate else (75, 85, 110)
        pygame.draw.rect(tt_surf, tt_bg, (0, 0, 155, 28), border_radius=4)
        pygame.draw.rect(tt_surf, tt_border, (0, 0, 155, 28), 1, border_radius=4)
        tt_label = f"Turntable: {'ON' if self.auto_rotate else 'OFF'} [Espaço]"
        tt_txt = self.font_small.render(tt_label, True, (245, 205, 80) if self.auto_rotate else (200, 205, 215))
        tt_surf.blit(tt_txt, (10, 6))
        ctrl_surf.blit(tt_surf, (302, 32))

        # 4. Botão Reset Câmera
        rst_rect = pygame.Rect(ctrl_x + 463, ctrl_y + 32, 137, 28)
        self.clickable_regions.append((rst_rect, self.camera.reset))
        rst_surf = pygame.Surface((137, 28), pygame.SRCALPHA)
        pygame.draw.rect(rst_surf, (36, 42, 58), (0, 0, 137, 28), border_radius=4)
        pygame.draw.rect(rst_surf, (75, 85, 110), (0, 0, 137, 28), 1, border_radius=4)
        rst_txt = self.font_small.render("Reset Câmera [R]", True, (200, 205, 215))
        rst_surf.blit(rst_txt, (10, 6))
        ctrl_surf.blit(rst_surf, (463, 32))

        surface.blit(ctrl_surf, (ctrl_x, ctrl_y))

    def update(self, dt: float):
        """Atualiza estado, timers e rotação automática."""
        self.anim_time += dt

        if self.auto_rotate:
            self.camera.rotate_orbit(self.auto_rotate_speed * dt, 0.0)

    def render(self):
        """Desenha todo o cenário, piso, personagem e HUD."""
        # Fundo degradê cinematográfico estilo showroom museu
        w, h = self.width, self.height
        self.screen.fill((20, 22, 28))

        # Vinheta sutil e brilho radial central sob a plataforma
        cx, cy = self.camera.screen_x, self.camera.screen_y
        glow_radius = int(240 * (self.camera.zoom / 2.8))
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (34, 38, 48, 120), (glow_radius, glow_radius), glow_radius)
        self.screen.blit(glow_surf, (cx - glow_radius, cy - glow_radius))

        # Plataforma / Pedestal de exposição
        self.draw_studio_pedestal(self.screen)

        # Guerreiro 3D
        self.draw_character(self.screen)

        # Interface gráfica
        self.draw_hud(self.screen)

        pygame.display.flip()

    def handle_events(self) -> bool:
        """Processa entrada de teclado e mouse. Retorna False ao sair."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.DOUBLEBUF | pygame.RESIZABLE)
                self.camera.screen_w = event.w
                self.camera.screen_h = event.h
                self.camera.screen_x = event.w // 2
                self.camera.screen_y = int(event.h * 0.58)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo: verifica cliques no HUD primeiro
                    clicked_hud = False
                    for rect, action in self.clickable_regions:
                        if rect.collidepoint(event.pos):
                            action()
                            clicked_hud = True
                            break
                    if not clicked_hud:
                        self.is_dragging = True
                        self.drag_start_x, self.drag_start_y = event.pos
                elif event.button == 4:  # Scroll para cima: zoom in
                    self.camera.zoom_in(1.10)
                elif event.button == 5:  # Scroll para baixo: zoom out
                    self.camera.zoom_out(1.10)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    dx = event.pos[0] - self.drag_start_x
                    dy = event.pos[1] - self.drag_start_y
                    self.drag_start_x, self.drag_start_y = event.pos

                    # Sensibilidade de órbita
                    azimuth_speed = 0.008
                    elevation_speed = 0.006
                    self.camera.rotate_orbit(dx * azimuth_speed, -dy * elevation_speed)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.toggle_auto_rotate()
                elif event.key == pygame.K_r:
                    self.camera.reset()
                elif event.key == pygame.K_p:
                    self.next_pose()
                elif event.key in (pygame.K_m, pygame.K_o):
                    self.toggle_model_version()

                # Seleção de personagens por número [1] a [9] e [0]
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    if idx < len(self.char_keys):
                        self.select_character(idx)
                elif event.key == pygame.K_0:
                    if len(self.char_keys) >= 10:
                        self.select_character(9)

                # Teclas de atalho para poses: [P] cicla poses, ou [I], [C], [A]
                elif event.key == pygame.K_i:
                    self.set_pose("IDLE")
                elif event.key == pygame.K_c:
                    self.set_pose("CONCEPT")
                elif event.key == pygame.K_a:
                    self.set_pose("ATTACK")


                # Ajuste manual de zoom
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    self.camera.zoom_in(1.15)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.camera.zoom_out(1.15)

                # Rotação por setas
                elif event.key == pygame.K_LEFT:
                    self.camera.rotate_orbit(-0.10, 0.0)
                elif event.key == pygame.K_RIGHT:
                    self.camera.rotate_orbit(0.10, 0.0)
                elif event.key == pygame.K_UP:
                    self.camera.rotate_orbit(0.0, 0.08)
                elif event.key == pygame.K_DOWN:
                    self.camera.rotate_orbit(0.0, -0.08)

        return True

    def run(self):
        """Loop principal do visualizador interativo."""
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
        """Renderiza um único frame em alta definição e salva no disco."""
        self.render()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pygame.image.save(self.screen, output_path)
        print(f"[ModelInspector] Snapshot salvo com sucesso em: {output_path}")


# =============================================================================
# PONTO DE ENTRADA CLI
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Model Inspector 3D — Samurai Edge (Micro-voxels)")
    parser.add_argument("--char", choices=list(CHARACTERS.keys()), default="okuni", help="Personagem inicial")
    parser.add_argument("--pose", choices=["IDLE", "CONCEPT", "ATTACK"], default="IDLE", help="Pose inicial")
    parser.add_argument("--azimuth", type=float, default=0.0, help="Ângulo de azimute em graus (0 a 360)")
    parser.add_argument("--elevation", type=float, default=30.0, help="Ângulo de elevação em graus (6 a 84)")
    parser.add_argument("--zoom", type=float, default=2.8, help="Nível de zoom da câmera")
    parser.add_argument("--snapshot", type=str, default=None, help="Salva snapshot PNG e sai")
    parser.add_argument("--width", type=int, default=1280, help="Largura da janela")
    parser.add_argument("--height", type=int, default=720, help="Altura da janela")
    parser.add_argument("--headless", action="store_true", help="Executa sem interface gráfica visível (dummy SDL)")
    args = parser.parse_args()

    is_headless = args.headless or (args.snapshot is not None)
    inspector = ModelInspector(width=args.width, height=args.height, headless=is_headless)

    char_idx = list(CHARACTERS.keys()).index(args.char)
    inspector.select_character(char_idx)
    if args.pose in POSES:
        inspector.current_pose_idx = POSES.index(args.pose)

    inspector.camera.azimuth = math.radians(args.azimuth)
    inspector.camera.elevation = math.radians(args.elevation)
    inspector.camera.zoom = args.zoom

    if args.snapshot:
        inspector.snapshot(args.snapshot)
        pygame.quit()
        sys.exit(0)
    else:
        inspector.run()


if __name__ == "__main__":
    main()
