#!/usr/bin/env python3
"""
tools/model_inspector.py - Model Inspector 3D para Samurai Edge (Roster Completo)

Visualizador interativo 3D dedicado para examinar de perto os novos modelos dos
20 combatentes criados no padrão de malha 3D esculpida, fitas contínuas de tecido/cabelo
e feições faciais fiéis aos portraits:
  - 20 Combatentes: Kenshi, Musashi, Saitou, Okuni, Hanzo, Joe, Kasumi, Murasaki,
    Teppo, Tomoe, Anne, Julie, Ren, Chiyo, Benkei, O-Rin, Goro, Ichi, Valerius, Seimei.
  - Câmera Orbital 3D: Azimute (360°), Elevação (Pitch 6°-84°), Zoom Suave Macro (até 8.0x).
  - Foco Facial Macro (Tecla 'F' / '2'): Aproximação direta na face para ver cicatrizes,
    olhos 3D, delineados, maquiagem teatral Kumadori e cortes de cabelo.
  - Poses / Animações: IDLE (respiração/vento), WALK (passada articulada), ATTACK (golpe 3D),
    RECOVERY (embainhar), INTRO e VICTORY.
  - Turntable Automático (Tecla 'Space' / 'T') para exibição contínua.
  - Totalmente desacoplado do código central do jogo.
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
    os.environ.setdefault("SDL_JOYSTICK_MFI", "0")

if "--headless" in sys.argv or "--snapshot" in sys.argv or "--save-all" in sys.argv:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

from src.config import HALF_TILE_W, HALF_TILE_H
from src.isometric.iso_math import PIXELS_PER_Z
from src.entities.voxel_models import render_voxel_humanoid


# =============================================================================
# CÂMERA ORBITAL 3D COM FOCO MACRO
# =============================================================================
class InspectorCamera:
    """
    Câmera de órbita 3D livre com controle de Azimute (360°), Elevação (Pitch),
    Pan horizontal/vertical e Zoom Macro (até 8.0x) para examinar rostos e detalhes.
    """
    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.screen_x = screen_w // 2 + 100  # Espaço para o menu lateral esquerdo
        self.screen_y = int(screen_h * 0.58)

        # Foco de alvo no modelo
        self.wx = 0.0
        self.wy = 0.0
        self.target_z = 0.45  # 0.45 = centro do corpo, 0.72 = rosto/cabeça

        # Ângulos de rotação orbital
        self.azimuth = 0.0                  # Radianos (0.0 = ângulo isométrico canônico)
        self.elevation = math.radians(30.0) # Inclinação (30° = clássico)
        self.zoom = 3.4                     # Escala generosa para close-up nítido

        # Parâmetros de compatibilidade com o motor do jogo
        self.ground_z = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
        self.height_fn = lambda wx, wy: 0.0

    def reset(self, target: str = "body", is_colossal: bool = False):
        """Restaura a câmera para enquadramento ideal."""
        self.azimuth = 0.0
        self.elevation = math.radians(30.0)
        self.screen_x = self.screen_w // 2 + 100
        self.screen_y = int(self.screen_h * 0.58)
        self.set_focus_target(target, is_colossal=is_colossal)

    def set_focus_target(self, target: str, is_colossal: bool = False):
        """Alterna o ponto de foco vertical (rosto, corpo inteiro, armas, pés)."""
        if is_colossal:
            if target == "head":
                self.target_z = 2.45
                self.zoom = 2.2
            elif target == "hands":
                self.target_z = 1.40
                self.zoom = 1.8
            elif target == "feet":
                self.target_z = 0.35
                self.zoom = 1.9
            else:  # "body"
                self.target_z = 1.40
                self.zoom = 1.35
        else:
            if target == "head":
                self.target_z = 0.72
                self.zoom = 5.6
            elif target == "hands":
                self.target_z = 0.40
                self.zoom = 4.4
            elif target == "feet":
                self.target_z = 0.12
                self.zoom = 4.6
            else:  # "body"
                self.target_z = 0.45
                self.zoom = 3.4

    def rotate_orbit(self, d_azimuth: float, d_elevation: float):
        """Aplica rotação horizontal e vertical."""
        self.azimuth = (self.azimuth + d_azimuth) % (math.pi * 2.0)
        min_elev = math.radians(6.0)
        max_elev = math.radians(84.0)
        self.elevation = max(min_elev, min(max_elev, self.elevation + d_elevation))

    def orbit(self, d_azimuth: float, d_elevation: float):
        """Alias compatível para rotate_orbit."""
        self.rotate_orbit(d_azimuth, d_elevation)

    def pan(self, dx: int, dy: int):
        """Desloca a câmera na tela 2D."""
        self.screen_x += dx
        self.screen_y += dy

    def pan_screen(self, dx: int, dy: int):
        """Alias compatível para pan."""
        self.pan(dx, dy)

    def zoom_in(self, factor: float = 1.15):
        self.zoom = max(0.8, min(8.5, self.zoom * factor))

    def zoom_out(self, factor: float = 1.15):
        self.zoom = max(0.8, min(8.5, self.zoom / factor))

    def apply(self, wx: float, wy: float, wz: float = 0.0) -> tuple[int, int]:
        """Projeta coordenadas 3D de mundo para a tela 2D usando a órbita da câmera."""
        rx = wx - self.wx
        ry = wy - self.wy
        rz = wz - self.target_z

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
# CATÁLOGO COMPLETO DOS 18 COMBATENTES
# =============================================================================
CHARACTERS = {
    "kenshi": {
        "name": "Kenshi",
        "char_type": "kenshin",
        "title": "Duelista Samurai Vermelha & Battojutsu",
        "weapon": "Katana Sakabatō + Bainha Saya",
        "description": "Quimono carmim com hakama escura, cicatriz em X esculpida em 3D e rabo de cavalo com fita vermelha fluida.",
        "concept_file": "kenshi_full_concept.jpg",
        "portrait_file": "kenshi_bust.png",
        "color_accent": (220, 50, 60),
    },
    "musashi": {
        "name": "Musashi",
        "char_type": "musashi",
        "title": "Mestre Invicto do Niten Ichi-ryū",
        "weapon": "Katana Longa + Wakizashi Curva",
        "description": "Quimono azul rasgado de batalha, duas lâminas afiadas empunhadas e cicatrizes de combate.",
        "concept_file": "musashi_full_concept.jpg",
        "portrait_file": "musashi_bust.png",
        "color_accent": (70, 130, 200),
    },
    "saitou": {
        "name": "Saitou",
        "char_type": "saitou",
        "title": "Lobo de Mibu & Capitão da 3ª Divisão",
        "weapon": "Katana Shinsengumi (Postura Gatotsu)",
        "description": "Haori azul-celeste com estampa serrilhada dandara branca nos punhos e postura frontal mortal.",
        "concept_file": "saitou_full_concept.jpg",
        "portrait_file": "saitou_bust.png",
        "color_accent": (110, 195, 230),
    },
    "okuni": {
        "name": "Okuni",
        "char_type": "okuni",
        "title": "Dançarina Sagrada & Mestra dos Leques Tessen",
        "weapon": "Leques Gêmeos de Aço Cortante",
        "description": "Quimono carmim/dourado em camadas, maquiagem teatral Kumadori e kanzashi dourado.",
        "concept_file": "okuni_full_concept.jpg",
        "portrait_file": "okuni_bust.png",
        "color_accent": (210, 40, 55),
    },
    "hanzo": {
        "name": "Hanzo",
        "char_type": "hanzo",
        "title": "Líder das Sombras & Mestre Ninja de Iga",
        "weapon": "Ninjato de Aço Negro + Kunai de Precisão",
        "description": "Traje shinobi preto com armadura de malha, máscara demoníaca menpo e capuz estilizado.",
        "concept_file": "hanzo_full_concept.jpg",
        "portrait_file": "hanzo_bust.png",
        "color_accent": (230, 190, 50),
    },
    "joe": {
        "name": "Joe & Yamato",
        "char_type": "joe",
        "title": "American Ninja & Operador Tático",
        "weapon": "Katana Tática + Cão Doberman de Ataque",
        "description": "Uniforme camuflado urbano com bandana de combate, colete tático e coldres de shuriken.",
        "concept_file": "joe_full_concept.jpg",
        "portrait_file": "joe_bust.png",
        "color_accent": (120, 175, 100),
    },
    "kasumi": {
        "name": "Kasumi",
        "char_type": "kasumi",
        "title": "Kunoichi da Névoa & Assassina de Koga",
        "weapon": "Adagas Ninjato Duplas + Bombas Cerâmicas",
        "description": "Armadura cromada esguia, colete com fivelas, cachecol longo drapeado e adagas cruzadas.",
        "concept_file": "kasumi_full_concept.jpg",
        "portrait_file": "kasumi_bust.png",
        "color_accent": (140, 180, 215),
    },
    "murasaki": {
        "name": "Murasaki",
        "char_type": "murasaki",
        "title": "Ceifadora das Sombras de Kusarigama",
        "weapon": "Kusarigama com Foice Curva e Corrente de Aço",
        "description": "Traje tático púrpura esguio, máscara refinada, foice curvada e anéis de corrente giratória.",
        "concept_file": "murasaki_full_concept.jpg",
        "portrait_file": "murasaki_bust.png",
        "color_accent": (180, 90, 235),
    },
    "teppo": {
        "name": "Teppo",
        "char_type": "teppo",
        "title": "Atirador de Infantaria Tanegashima",
        "weapon": "Arcabuz de Mecha Pesado + Coronha de Carvalho",
        "description": "Colete de laca marrom tradicional, chapéu de ferro Jingasa e arcabuz de mecha longo com pavio aceso.",
        "concept_file": "teppo_full_concept.jpg",
        "portrait_file": "teppo_bust.png",
        "color_accent": (210, 150, 70),
    },
    "tomoe": {
        "name": "Tomoe",
        "char_type": "tomoe",
        "title": "Arqueira Sagrada de Kyudo",
        "weapon": "Arco Longo Yumi + Flechas Hamaya",
        "description": "Traje cerimonial Miko com hakama vermelho-rubro, tiara sagrada e arco longo entalhado.",
        "concept_file": "tomoe_full_concept.jpg",
        "portrait_file": "tomoe_bust.png",
        "color_accent": (230, 70, 80),
    },
    "anne": {
        "name": "Anne",
        "char_type": "anne",
        "title": "Capitã Pirata dos Mares do Sul",
        "weapon": "Alfanje Cutlass de Guarda Dourada + Canhão",
        "description": "Sobretudo bordô com fivelas de ouro, chapéu tricórnio com pluma e corte horizontal largo.",
        "concept_file": "anne_full_concept.jpg",
        "portrait_file": "anne_bust.png",
        "color_accent": (220, 80, 90),
    },
    "julie": {
        "name": "Julie",
        "char_type": "julie",
        "title": "Mosqueteira Real de Paris",
        "weapon": "Florete de Esgrima + Pistola de Pederneira",
        "description": "Casaca azul-real com gola de renda de seda, chapéu emplumado e capa de seda com física 3D.",
        "concept_file": "julie_full_concept.jpg",
        "portrait_file": "julie_bust.png",
        "color_accent": (65, 140, 245),
    },
    "ren": {
        "name": "Ren",
        "char_type": "ren",
        "title": "Monge Shaolin dos Punhos de Ferro",
        "weapon": "Punhos Nus + Rosário Budista de Madeira",
        "description": "Túnica monástica açafrão, cabeça raspada com marcas sagradas de ordenação e postura dos Três Dragões.",
        "concept_file": "ren_full_concept.jpg",
        "portrait_file": "ren_bust.png",
        "color_accent": (235, 160, 45),
    },
    "chiyo": {
        "name": "Chiyo",
        "char_type": "chiyo",
        "title": "Kunoichi das Lâminas Duplas Kodachi",
        "weapon": "Duas Espadas Curtas Kodachi",
        "description": "Traje de seda carmesim e ébano com mangas soltas, mechas que emolduram o rosto e dança Mai.",
        "concept_file": "chiyo_full_concept.jpg",
        "portrait_file": "chiyo_bust.png",
        "color_accent": (225, 55, 75),
    },
    "benkei": {
        "name": "Benkei",
        "char_type": "benkei",
        "title": "Monge Guerreiro Sohei da Ponte Gojo",
        "weapon": "Naginata Colossal com Lâmina de Aço Temperado",
        "description": "Armadura de placas pesada, capuz de monge guerreiro e estatura colossal de 2.10m.",
        "concept_file": "benkei_full_concept.jpg",
        "portrait_file": "benkei_bust.png",
        "color_accent": (160, 140, 110),
    },
    "orin": {
        "name": "O-Rin",
        "char_type": "orin",
        "title": "Menestrel Itinerante do Shamisen",
        "weapon": "Shamisen de Madeira Nobre com Lâmina Kamaitachi",
        "description": "Chapéu tradicional de palha trançada, quimono com estampas florais e olhos misteriosos vendados.",
        "concept_file": "orin_full_concept.jpg",
        "portrait_file": "orin_bust.png",
        "color_accent": (210, 100, 160),
    },
    "goro": {
        "name": "Goro",
        "char_type": "goro",
        "title": "Camponês Rebelde dos Arrozais",
        "weapon": "Enxada de Aço Kuwa de Duas Mãos",
        "description": "Músculos esculpidos, colete rústico rasgado, bandana de palha e força física bruta nos pés descalços.",
        "concept_file": "goro_full_concept.jpg",
        "portrait_file": "goro_bust.png",
        "color_accent": (175, 120, 65),
    },
    "ichi": {
        "name": "Ichi",
        "char_type": "ichi",
        "title": "A Lâmina Cega do Moinho",
        "weapon": "Bengala Shikomizue com Lâmina Oculta de Saque Invertido",
        "description": "Quimono desgastado pela chuva, olhos cegos leitosos serenos e postura de escuta absoluta.",
        "concept_file": "ichi_full_concept.jpg",
        "portrait_file": "ichi_bust.png",
        "color_accent": (120, 185, 225),
    },
    "valerius": {
        "name": "Valerius",
        "char_type": "valerius",
        "title": "Necromante Prussiano & Aristocrata Ocultista",
        "weapon": "Foice Fúnebre de Ferro Forjado e Ébano",
        "description": "Sobretudo militar gótico azul-noite com dragonas prateadas, cravat alto de seda branca e cabelos platinados.",
        "concept_file": "valerius_full_concept.jpg",
        "portrait_file": "valerius_bust.png",
        "color_accent": (145, 175, 215),
    },
    "seimei": {
        "name": "Seimei",
        "char_type": "seimei",
        "title": "Onmyoji dos Talismãs & Sacerdotisa de Heian",
        "weapon": "Talismãs Ofuda Sagrados de Seda e Fogo Espiritual",
        "description": "Vestes Kariginu de seda branca pura e índigo celestial, chapéu cerimonial Eboshi laqueado e longos cabelos negros.",
        "concept_file": "seimei_full_concept.jpg",
        "portrait_file": "seimei_bust.png",
        "color_accent": (175, 130, 225),
    },
    "daiki": {
        "name": "Daiki",
        "char_type": "daiki",
        "title": "Peregrino do Bastão Bō & Yamabushi",
        "weapon": "Bastão Bō de Carvalho com Ponteiras de Ferro",
        "description": "Túnica monástica índigo com ombro exposto, contas Juzu gigantes no peito, hachimaki de palha e bastão Bō de duas mãos.",
        "concept_file": "daiki_full_concept.jpg",
        "portrait_file": "daiki_bust.png",
        "color_accent": (180, 235, 195),
    },
    "aoi": {
        "name": "Aoi",
        "char_type": "aoi",
        "title": "A Caçadora Ainu de Hokkaido",
        "weapon": "Lança Op de Caça e Armadilha de Urso",
        "description": "Traje tradicional Attush índigo com bordados Moreu brancos, gola de pele de lobo, tiara Matanpushi e lança Op.",
        "concept_file": "aoi_full_concept.jpg",
        "portrait_file": "aoi_bust.png",
        "color_accent": (155, 225, 255),
    },
    "raiden": {
        "name": "Raiden",
        "char_type": "raiden",
        "title": "O Yokozuna dos Trovões & Força Rikishi",
        "weapon": "Palmas Tsuppari Pesadas e Tachiai Tackle",
        "description": "Físico colossal de rikishi em trânsito com manto cerimonial Haori bordado a ouro e brasões Mon, mawashi índigo com cordões Sagari e coque Oicho-mage.",
        "concept_file": "raiden_full_concept.jpg",
        "portrait_file": "raiden_bust.png",
        "color_accent": (235, 185, 70),
    },
    "hendrika": {
        "name": "Hendrika",
        "char_type": "hendrika",
        "title": "A Alquimista de Dejima & VOC Scholar",
        "weapon": "Estilete Corrosivo, 5 Frascos Alquímicos e Bandoleira de Reagentes",
        "description": "Casaca barroca de veludo azul-safira com botões dourados, quepe com óculos de latão (goggles), bandoleira de reagentes luminescentes e sorriso excêntrico.",
        "concept_file": "hendrika_full_concept.jpg",
        "portrait_file": "hendrika_bust.png",
        "color_accent": (85, 225, 235),
    },
    "gashadokuro": {
        "name": "Gashadokuro",
        "char_type": "gashadokuro",
        "title": "Oni Colossal & Espírito da Fome Insaciável (Final Boss)",
        "weapon": "Ossos Ancestrais, Clava Titânica e Fogo Espectral",
        "description": "Crânio colossal de marfim antigo desgastado com chifres demoníacos curvados, órbitas em chamas roxas e carmesins e 5 fases transmórficas.",
        "concept_file": "gashadokuro_concept.jpg",
        "portrait_file": "gashadokuro_bust.png",
        "color_accent": (175, 55, 230),
    },
}

POSES = ["IDLE", "WALK", "ATTACK", "RECOVERY", "INTRO", "VICTORY"]


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
        pygame.display.set_caption("Samurai Edge — Model Inspector 3D (Roster Completo)")

        flags = pygame.DOUBLEBUF | pygame.RESIZABLE if not headless else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        self.clock = pygame.time.Clock()

        self.camera = InspectorCamera(width, height)

        # Estado atual
        self.char_keys = list(CHARACTERS.keys())
        self.current_char_idx = 0
        self.current_pose_idx = 0
        self.macro_focus = "body"  # "body", "head", "hands", "feet"

        # Interatividade do mouse
        self.is_dragging_orbit = False
        self.is_dragging_pan = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.auto_rotate = False
        self.auto_rotate_speed = 0.45  # Radianos por segundo
        self.show_hud = True
        self.show_wireframe_marker = False

        # Timers e animações
        self.anim_time = 0.0
        self.fps = 60.0

        # Fontes do HUD
        self.font_header = pygame.font.Font(None, 32)
        self.font_title = pygame.font.Font(None, 24)
        self.font_body = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 15)

        # Cache de imagens
        self._thumb_cache = {}

        # Botões clicáveis do menu lateral e ações
        self.sidebar_rects: list[tuple[pygame.Rect, int]] = []
        self.sidebar_scroll_y = 0.0
        self.sidebar_target_scroll_y = 0.0
        self.sidebar_max_scroll = 0.0
        self.pose_btn_rects: list[tuple[str, pygame.Rect]] = []
        self.reload_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.reset_cam_btn_rect = pygame.Rect(0, 0, 0, 0)

        # Joystick / Fightstick support
        if not pygame.joystick.get_init():
            try:
                pygame.joystick.init()
            except Exception:
                pass
        for i in range(pygame.joystick.get_count()):
            try:
                joy = pygame.joystick.Joystick(i)
            except Exception:
                pass

        # Mensagem toast de status do reload
        self.status_message = ""
        self.status_message_timer = 0.0
        self.status_is_error = False

    @property
    def current_char_info(self) -> dict:
        return CHARACTERS[self.char_keys[self.current_char_idx]]

    @property
    def current_pose(self) -> str:
        return POSES[self.current_pose_idx]

    def select_character(self, idx: int):
        prev_colossal = (self.char_keys[self.current_char_idx] == "gashadokuro")
        self.current_char_idx = idx % len(self.char_keys)
        now_colossal = (self.char_keys[self.current_char_idx] == "gashadokuro")
        if prev_colossal != now_colossal:
            self.camera.reset(self.macro_focus, is_colossal=now_colossal)
        self.ensure_char_visible(self.current_char_idx)

    def ensure_char_visible(self, idx: int):
        btn_h = 28 if len(self.char_keys) > 18 else 32
        spacing = 2 if len(self.char_keys) > 18 else 3
        item_top = idx * (btn_h + spacing)
        item_bot = item_top + btn_h
        list_h = max(100, self.height - 80)

        if item_top < self.sidebar_target_scroll_y:
            self.sidebar_target_scroll_y = float(item_top)
        elif item_bot > self.sidebar_target_scroll_y + list_h:
            self.sidebar_target_scroll_y = float(item_bot - list_h)

    def next_character(self):
        self.select_character(self.current_char_idx + 1)

    def prev_character(self):
        self.select_character(self.current_char_idx - 1)

    def next_pose(self):
        self.current_pose_idx = (self.current_pose_idx + 1) % len(POSES)

    def set_pose_by_name(self, pose: str):
        if pose in POSES:
            self.current_pose_idx = POSES.index(pose)

    def toggle_focus_target(self):
        targets = ["body", "head", "hands", "feet"]
        cur_idx = targets.index(self.macro_focus) if self.macro_focus in targets else 0
        next_target = targets[(cur_idx + 1) % len(targets)]
        self.macro_focus = next_target
        now_colossal = (self.char_keys[self.current_char_idx] == "gashadokuro")
        self.camera.set_focus_target(next_target, is_colossal=now_colossal)

    def reload_modules(self) -> bool:
        """
        Recarrega a quente (hot-reload) todos os módulos de modelos 3D, geometrias e rigs
        sem precisar reiniciar o visualizador.
        """
        import importlib
        try:
            # 1. Dependências fundamentais na ordem canônica
            core_deps = [
                "src.config",
                "src.isometric.iso_math",
                "src.isometric.voxel_textures",
                "src.isometric.voxel_rig",
                "src.isometric.cloth",
                "src.isometric.mesh_primitives",
                "src.isometric.voxel_renderer",
                "src.entities.model_kit",
                "src.entities.pose_scripts",
            ]
            for mod_name in core_deps:
                if mod_name in sys.modules:
                    importlib.reload(sys.modules[mod_name])

            # 2. Todos os modelos específicos de guerreiros (*_model)
            for mod_name in list(sys.modules.keys()):
                if mod_name.startswith("src.entities.") and mod_name.endswith("_model"):
                    importlib.reload(sys.modules[mod_name])

            # 3. Orquestrador principal de modelos voxel
            if "src.entities.voxel_models" in sys.modules:
                importlib.reload(sys.modules["src.entities.voxel_models"])

            # 4. Atualizar ponteiro global de renderização
            global render_voxel_humanoid
            from src.entities.voxel_models import render_voxel_humanoid as rvh
            render_voxel_humanoid = rvh

            # 5. Limpar caches visuais
            self._thumb_cache.clear()

            self.status_message = "CÓDIGO RECARREGADO COM SUCESSO!"
            self.status_message_timer = 2.5
            self.status_is_error = False
            print("[ModelInspector] Hot-reload de scripts e modelos executado com sucesso.")
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            err_msg = str(e).split("\n")[0]
            self.status_message = f"ERRO NO RELOAD: {err_msg[:40]}"
            self.status_message_timer = 4.0
            self.status_is_error = True
            return False

    def _load_portrait_thumbnail(self, filename: str) -> pygame.Surface | None:
        """Carrega e escala o portrait do personagem para exibição na ficha técnica."""
        if not filename:
            return None
        if filename in self._thumb_cache:
            return self._thumb_cache[filename]

        path = os.path.join(ROOT, "assets", "portraits", filename)
        if not os.path.exists(path):
            path = os.path.join(ROOT, "assets", "concepts", filename)
        if not os.path.exists(path):
            return None

        try:
            raw = pygame.image.load(path).convert_alpha()
            thumb = pygame.transform.smoothscale(raw, (96, 96))
            self._thumb_cache[filename] = thumb
            return thumb
        except Exception:
            return None

    def draw_pedestal(self, surface: pygame.Surface):
        """Desenha a plataforma circular de madeira nobre e anel dourado sob o modelo."""
        # Sombra de oclusão de contato no chão
        sx0, sy0 = self.camera.apply(0.0, 0.0, 0.0)
        shadow_w = int(68 * self.camera.zoom)
        shadow_h = int(32 * self.camera.zoom * (math.sin(self.camera.elevation) / 0.5))
        shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (8, 10, 14, 185), (0, 0, shadow_w * 2, shadow_h * 2))
        surface.blit(shadow_surf, (sx0 - shadow_w, sy0 - shadow_h // 2))

        # Pedestal cilíndrico de madeira tradicional com anéis concêntricos
        char_info = self.current_char_info
        is_colossal = (char_info["char_type"] == "gashadokuro")
        num_segments = 32 if is_colossal else 28
        radius = 1.65 if is_colossal else 0.70
        top_points = []
        for i in range(num_segments):
            angle = (i / num_segments) * math.pi * 2.0
            px = math.cos(angle) * radius
            py = math.sin(angle) * radius
            top_points.append(self.camera.apply(px, py, 0.0))

        if len(top_points) >= 3:
            pygame.draw.polygon(surface, (38, 34, 30), top_points)
            pygame.draw.polygon(surface, (140, 110, 60), top_points, max(1, int(1.5 * self.camera.zoom)))

            inner_points = []
            for i in range(num_segments):
                angle = (i / num_segments) * math.pi * 2.0
                px = math.cos(angle) * (radius * 0.78)
                py = math.sin(angle) * (radius * 0.78)
                inner_points.append(self.camera.apply(px, py, 0.002))
            pygame.draw.polygon(surface, (48, 42, 36), inner_points)
            pygame.draw.polygon(surface, (85, 72, 55), inner_points, 1)

    def draw_boss(self, surface: pygame.Surface):
        """Renderiza o Oni Gashadokuro com suas 5 formas transmórficas no estúdio 3D."""
        if getattr(self, "_boss_instance", None) is None:
            from src.entities.boss_oni import BossOni
            self._boss_instance = BossOni(0.0, 0.0)
        boss = self._boss_instance
        boss.time = self.anim_time
        boss.wx = 0.0
        boss.wy = 0.0
        boss.wz = 0.0

        pose_to_phase = {
            "IDLE": 0,       # Fase 1: Bípede com cutelo
            "WALK": 1,       # Fase 2: Serpente rastejante
            "ATTACK": 2,     # Fase 3: Torso com salto
            "RECOVERY": 3,   # Fase 4: Clava viva
            "INTRO": 4,      # Fase 5: Crânio colossal
            "VICTORY": 4,    # Fase 5: Gargalhada
        }
        phase_idx = pose_to_phase.get(self.current_pose, 0)
        if boss.phase != phase_idx:
            boss.set_phase(phase_idx)

        # Configurações cinemáticas da pose
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

        boss.render(surface, self.camera, self.anim_time)

    def draw_character(self, surface: pygame.Surface):
        """Renderiza o combatente selecionado utilizando o motor oficial de modelos do jogo."""
        char_info = self.current_char_info
        char_type = char_info["char_type"]

        if char_type == "gashadokuro":
            self.draw_boss(surface)
            return

        # Orientação do guerreiro (vetor frontal padrão: 1.0, 1.0)
        facing_x, facing_y = 1.0, 1.0

        # Animação e parâmetros baseados na pose selecionada
        state = "IDLE"
        state_timer = 0.0
        is_moving = False
        walk_timer = self.anim_time

        if self.current_pose == "IDLE":
            state = "IDLE"
            is_moving = False
            walk_timer = self.anim_time
        elif self.current_pose == "WALK":
            state = "WALK"
            is_moving = True
            walk_timer = self.anim_time * 2.6
        elif self.current_pose == "ATTACK":
            state = "ATTACK"
            is_moving = False
            # Ciclo oscilante de golpe 3D para examinar antecipação, corte e lâmina
            state_timer = 0.08 + (math.sin(self.anim_time * 4.0) * 0.5 + 0.5) * 0.12
            walk_timer = self.anim_time
        elif self.current_pose == "RECOVERY":
            state = "RECOVERY"
            state_timer = 0.35
            is_moving = False
            walk_timer = self.anim_time
        elif self.current_pose == "INTRO":
            state = "INTRO"
            state_timer = (self.anim_time * 0.35) % 1.0
            walk_timer = self.anim_time
        elif self.current_pose == "VICTORY":
            state = "VICTORY"
            state_timer = (self.anim_time * 0.35) % 1.0
            walk_timer = self.anim_time

        # Renderização oficial do modelo 3D do jogo
        render_voxel_humanoid(
            surface, self.camera,
            0.0, 0.0, 0.0,
            facing_x, facing_y,
            state, state_timer,
            is_alive=True,
            char_type=char_type,
            walk_timer=walk_timer,
            alpha=255,
            is_moving=is_moving
        )

        # Marcador de juntas / wireframe (se ativo)
        if self.show_wireframe_marker:
            head_x, head_y = self.camera.apply(0.0, 0.0, 0.72)
            pygame.draw.circle(surface, (255, 230, 80), (head_x, head_y), 4, 1)
            pelvis_x, pelvis_y = self.camera.apply(0.0, 0.0, 0.44)
            pygame.draw.circle(surface, (100, 220, 255), (pelvis_x, pelvis_y), 4, 1)

    def draw_hud(self, surface: pygame.Surface):
        """Desenha a interface lateral de seleção dos 18 personagens e ficha técnica."""
        if not self.show_hud:
            return

        # -------------------------------------------------------------
        # 1. Menu Lateral Esquerdo: Lista dos 18 Guerreiros
        # -------------------------------------------------------------
        sidebar_w = 230
        sidebar_surf = pygame.Surface((sidebar_w, self.height), pygame.SRCALPHA)
        sidebar_surf.fill((16, 18, 24, 235))
        surface.blit(sidebar_surf, (0, 0))
        pygame.draw.line(surface, (55, 60, 75), (sidebar_w, 0), (sidebar_w, self.height), 2)

        # Título da Barra Lateral
        title_s = self.font_header.render(f"ROSTER ({len(self.char_keys)})", True, (240, 215, 120))
        surface.blit(title_s, (16, 16))
        sub_s = self.font_small.render("Scroll / Clique para navegar", True, (160, 165, 180))
        surface.blit(sub_s, (16, 44))

        self.sidebar_rects.clear()
        list_top = 68
        list_h = max(100, self.height - list_top - 12)
        btn_h = 28
        spacing = 3
        total_content_h = len(self.char_keys) * (btn_h + spacing)
        self.sidebar_max_scroll = max(0.0, float(total_content_h - list_h))

        # Suavização da rolagem (Damped interpolation)
        self.sidebar_target_scroll_y = max(0.0, min(self.sidebar_max_scroll, self.sidebar_target_scroll_y))
        self.sidebar_scroll_y += (self.sidebar_target_scroll_y - self.sidebar_scroll_y) * 0.35
        if abs(self.sidebar_target_scroll_y - self.sidebar_scroll_y) < 0.5:
            self.sidebar_scroll_y = self.sidebar_target_scroll_y
        scroll_offset = int(self.sidebar_scroll_y)

        # Região de recorte para que os botões não vazem fora da barra lateral
        old_clip = surface.get_clip()
        surface.set_clip(pygame.Rect(0, list_top, sidebar_w, list_h))

        for idx, key in enumerate(self.char_keys):
            info = CHARACTERS[key]
            is_selected = (idx == self.current_char_idx)
            btn_y = list_top - scroll_offset + idx * (btn_h + spacing)
            btn_rect = pygame.Rect(12, btn_y, sidebar_w - 28, btn_h)

            # Apenas registra e desenha se estiver visível na janela de rolagem
            if btn_rect.bottom >= list_top and btn_rect.top <= list_top + list_h:
                self.sidebar_rects.append((btn_rect, idx))

                if is_selected:
                    pygame.draw.rect(surface, (45, 52, 70), btn_rect, border_radius=4)
                    pygame.draw.rect(surface, info["color_accent"], btn_rect, width=2, border_radius=4)
                    pygame.draw.circle(surface, info["color_accent"], (btn_rect.x + 10, btn_rect.centery), 4)
                else:
                    pygame.draw.rect(surface, (22, 26, 34), btn_rect, border_radius=4)

                text_color = (255, 255, 255) if is_selected else (175, 180, 195)
                name_s = self.font_body.render(f"{idx+1}. {info['name']}", True, text_color)
                surface.blit(name_s, (btn_rect.x + 22, btn_rect.centery - 6))

        surface.set_clip(old_clip)

        # Barra de rolagem visual (Scrollbar indicator)
        if self.sidebar_max_scroll > 0:
            bar_x = sidebar_w - 8
            track_y = list_top
            track_h = list_h
            pygame.draw.rect(surface, (25, 28, 38), (bar_x, track_y, 4, track_h), border_radius=2)

            thumb_ratio = list_h / total_content_h
            thumb_h = max(24, int(track_h * thumb_ratio))
            scroll_pct = self.sidebar_scroll_y / self.sidebar_max_scroll
            thumb_y = track_y + int((track_h - thumb_h) * scroll_pct)
            pygame.draw.rect(surface, (220, 195, 115), (bar_x, thumb_y, 4, thumb_h), border_radius=2)

        # -------------------------------------------------------------
        # 1.5 Barra de Ação Superior: Hot-Reload e Reset de Câmera
        # -------------------------------------------------------------
        mouse_pos = pygame.mouse.get_pos()
        reload_btn_x = sidebar_w + 18
        reload_btn_y = 18
        reload_btn_w = 175
        reload_btn_h = 36
        self.reload_btn_rect = pygame.Rect(reload_btn_x, reload_btn_y, reload_btn_w, reload_btn_h)

        is_hover_reload = self.reload_btn_rect.collidepoint(mouse_pos)
        btn_bg = (38, 54, 72) if is_hover_reload else (22, 28, 38)
        border_col = (85, 230, 165) if is_hover_reload else (55, 75, 95)

        btn_surf = pygame.Surface((reload_btn_w, reload_btn_h), pygame.SRCALPHA)
        btn_surf.fill((*btn_bg, 235))
        surface.blit(btn_surf, (reload_btn_x, reload_btn_y))
        pygame.draw.rect(surface, border_col, self.reload_btn_rect, width=2 if is_hover_reload else 1, border_radius=6)

        # Ícone circular de reload desenhado via vetor
        label_col = (110, 245, 175) if is_hover_reload else (210, 220, 235)
        center = (reload_btn_x + 18, reload_btn_y + 18)
        radius = 7
        pygame.draw.arc(surface, label_col, (center[0] - radius, center[1] - radius, radius * 2, radius * 2), 0.5, 5.8, 2)
        pygame.draw.polygon(surface, label_col, [
            (center[0] + radius - 2, center[1] - 4),
            (center[0] + radius + 4, center[1] - 4),
            (center[0] + radius + 1, center[1] + 2),
        ])
        r_text_s = self.font_body.render("RELOAD (F5 / R)", True, label_col)
        surface.blit(r_text_s, (reload_btn_x + 32, reload_btn_y + 10))

        # Botão Reset Câmera ao lado
        cam_btn_x = reload_btn_x + reload_btn_w + 10
        cam_btn_w = 150
        self.reset_cam_btn_rect = pygame.Rect(cam_btn_x, reload_btn_y, cam_btn_w, reload_btn_h)
        is_hover_cam = self.reset_cam_btn_rect.collidepoint(mouse_pos)
        cam_bg = (42, 48, 62) if is_hover_cam else (22, 28, 38)
        cam_border = (240, 215, 120) if is_hover_cam else (55, 65, 80)

        cam_btn_surf = pygame.Surface((cam_btn_w, reload_btn_h), pygame.SRCALPHA)
        cam_btn_surf.fill((*cam_bg, 235))
        surface.blit(cam_btn_surf, (cam_btn_x, reload_btn_y))
        pygame.draw.rect(surface, cam_border, self.reset_cam_btn_rect, width=2 if is_hover_cam else 1, border_radius=6)

        cam_label_col = (240, 215, 120) if is_hover_cam else (175, 180, 195)
        center_c = (cam_btn_x + 18, reload_btn_y + 18)
        pygame.draw.arc(surface, cam_label_col, (center_c[0] - radius, center_c[1] - radius, radius * 2, radius * 2), 1.0, 5.5, 2)
        pygame.draw.polygon(surface, cam_label_col, [
            (center_c[0] - radius - 1, center_c[1] - 4),
            (center_c[0] - radius + 5, center_c[1] - 4),
            (center_c[0] - radius + 2, center_c[1] + 2),
        ])
        cam_label_s = self.font_body.render("RESET CÂMERA", True, cam_label_col)
        surface.blit(cam_label_s, (cam_btn_x + 30, reload_btn_y + 10))

        # Notificação Toast de status do reload
        if self.status_message_timer > 0.0:
            toast_text = self.status_message
            toast_surf_text = self.font_body.render(toast_text, True, (255, 255, 255))
            tw, th = toast_surf_text.get_size()
            toast_w = tw + 42
            toast_h = th + 14
            toast_x = reload_btn_x
            toast_y = reload_btn_y + reload_btn_h + 8

            bg_col = (130, 24, 34, 240) if self.status_is_error else (18, 90, 56, 240)
            toast_bg = pygame.Surface((toast_w, toast_h), pygame.SRCALPHA)
            toast_bg.fill(bg_col)
            surface.blit(toast_bg, (toast_x, toast_y))
            border_toast = (255, 80, 90) if self.status_is_error else (80, 240, 160)
            pygame.draw.rect(surface, border_toast, (toast_x, toast_y, toast_w, toast_h), width=1, border_radius=4)

            # Ícone vetorial de status (Checkmark ou X)
            if not self.status_is_error:
                chk_x, chk_y = toast_x + 14, toast_y + 17
                pygame.draw.lines(surface, (80, 240, 160), False, [
                    (chk_x, chk_y),
                    (chk_x + 4, chk_y + 4),
                    (chk_x + 10, chk_y - 5),
                ], 2)
            else:
                err_x, err_y = toast_x + 14, toast_y + 17
                pygame.draw.line(surface, (255, 80, 90), (err_x, err_y - 4), (err_x + 8, err_y + 4), 2)
                pygame.draw.line(surface, (255, 80, 90), (err_x, err_y + 4), (err_x + 8, err_y - 4), 2)
            surface.blit(toast_surf_text, (toast_x + 30, toast_y + 7))

        # -------------------------------------------------------------
        # 2. Painel Superior Direito: Ficha Técnica do Lutador
        # -------------------------------------------------------------
        info = self.current_char_info
        card_w, card_h = 420, 165
        card_x = self.width - card_w - 18
        card_y = 18

        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((16, 18, 24, 230))
        surface.blit(card_surf, (card_x, card_y))
        pygame.draw.rect(surface, info["color_accent"], (card_x, card_y, card_w, card_h), 2, border_radius=6)

        # Portrait do Lutador
        thumb = self._load_portrait_thumbnail(info.get("portrait_file", ""))
        if thumb:
            surface.blit(thumb, (card_x + 14, card_y + 14))
            pygame.draw.rect(surface, info["color_accent"], (card_x + 14, card_y + 14, 96, 96), 1)

        # Textos da Ficha
        tx = card_x + 120
        name_s = self.font_header.render(info["name"].upper(), True, (255, 255, 255))
        surface.blit(name_s, (tx, card_y + 14))

        title_s = self.font_small.render(info["title"], True, info["color_accent"])
        surface.blit(title_s, (tx, card_y + 44))

        weap_lbl = self.font_small.render("Arma:", True, (160, 165, 180))
        weap_val = self.font_body.render(info["weapon"], True, (240, 225, 150))
        surface.blit(weap_lbl, (tx, card_y + 64))
        surface.blit(weap_val, (tx + 45, card_y + 63))

        # Descrição multiline simples
        desc_lines = self._wrap_text(info["description"], self.font_small, card_w - 135)
        dy = card_y + 90
        for line in desc_lines[:3]:
            line_s = self.font_small.render(line, True, (190, 195, 205))
            surface.blit(line_s, (tx, dy))
            dy += 16

        # -------------------------------------------------------------
        # 3. Painel Inferior: Controles e Câmera
        # -------------------------------------------------------------
        hud_bar_w = self.width - sidebar_w - 36
        hud_bar_x = sidebar_w + 18
        hud_bar_y = self.height - 72

        bar_surf = pygame.Surface((hud_bar_w, 54), pygame.SRCALPHA)
        bar_surf.fill((16, 18, 24, 230))
        surface.blit(bar_surf, (hud_bar_x, hud_bar_y))
        pygame.draw.rect(surface, (55, 60, 75), (hud_bar_x, hud_bar_y, hud_bar_w, 54), 1, border_radius=6)

        # Informações da Câmera
        deg_az = int(math.degrees(self.camera.azimuth))
        deg_el = int(math.degrees(self.camera.elevation))
        cam_text = f"ÓRBITA: Azimute {deg_az}° | Inclinação {deg_el}° | Zoom {self.camera.zoom:.2f}x | Foco: {self.macro_focus.upper()}"
        cam_s = self.font_body.render(cam_text, True, (240, 215, 120))
        surface.blit(cam_s, (hud_bar_x + 16, hud_bar_y + 10))

        # Controles
        ctrl_text = "Mouse: Girar (Esq) | Pan (Dir) | Zoom  ||  [F] Foco  |  [P] Pose  |  [Espaço] Turntable"
        ctrl_s = self.font_small.render(ctrl_text, True, (170, 175, 190))
        surface.blit(ctrl_s, (hud_bar_x + 16, hud_bar_y + 32))

        # Botões Interativos de Pose 1 a 6
        self.pose_btn_rects.clear()
        is_boss = (self.char_keys[self.current_char_idx] == "gashadokuro")
        boss_phase_labels = {
            "IDLE": "P1: Bípede",
            "WALK": "P2: Serp.",
            "ATTACK": "P3: Torso",
            "RECOVERY": "P4: Clava",
            "INTRO": "P5: Crânio",
            "VICTORY": "P5: Riso",
        }
        bx = hud_bar_x + hud_bar_w - 6 * 84 - 12
        for p_idx, p_name in enumerate(POSES):
            p_rect = pygame.Rect(bx + p_idx * 84, hud_bar_y + 11, 80, 32)
            self.pose_btn_rects.append((p_name, p_rect))
            is_active = (p_name == self.current_pose)
            col_bg = (55, 40, 80) if (is_boss and is_active) else ((45, 52, 70) if is_active else (22, 26, 34))
            col_border = (215, 125, 255) if (is_boss and is_active) else ((230, 195, 90) if is_active else (48, 54, 66))
            pygame.draw.rect(surface, col_bg, p_rect, border_radius=4)
            pygame.draw.rect(surface, col_border, p_rect, 2 if is_active else 1, border_radius=4)

            display_lbl = boss_phase_labels.get(p_name, p_name) if is_boss else p_name
            lbl_s = self.font_small.render(f"[{p_idx+1}] {display_lbl}", True, (255, 255, 255) if is_active else (160, 165, 175))
            surface.blit(lbl_s, (p_rect.centerx - lbl_s.get_width() // 2, p_rect.centery - lbl_s.get_height() // 2))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        words = text.split(" ")
        lines = []
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines

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

            elif event.type == pygame.MOUSEWHEEL:
                mouse_pos = pygame.mouse.get_pos()
                if self.show_hud and mouse_pos[0] < 240:
                    self.sidebar_target_scroll_y -= event.y * 42.0
                    self.sidebar_target_scroll_y = max(0.0, min(self.sidebar_max_scroll, self.sidebar_target_scroll_y))
                else:
                    if event.y > 0:
                        self.camera.zoom_in(1.10)
                    elif event.y < 0:
                        self.camera.zoom_out(1.10)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão Esquerdo
                    clicked_btn = False
                    # Verificar clique no botão de Reload
                    if self.show_hud and self.reload_btn_rect.collidepoint(event.pos):
                        self.reload_modules()
                        clicked_btn = True
                    # Verificar clique no botão de Reset Câmera
                    elif self.show_hud and self.reset_cam_btn_rect.collidepoint(event.pos):
                        self.camera.reset(self.macro_focus)
                        clicked_btn = True
                    # Verificar clique na lista lateral de personagens
                    elif self.show_hud:
                        for p_name, p_rect in self.pose_btn_rects:
                            if p_rect.collidepoint(event.pos):
                                self.set_pose_by_name(p_name)
                                clicked_btn = True
                                break
                        if not clicked_btn:
                            for rect, idx in self.sidebar_rects:
                                if rect.collidepoint(event.pos):
                                    self.select_character(idx)
                                    clicked_btn = True
                                    break
                    if not clicked_btn:
                        self.is_dragging_orbit = True
                        self.drag_start_x, self.drag_start_y = event.pos
                elif event.button == 3:  # Botão Direito (Pan)
                    self.is_dragging_pan = True
                    self.drag_start_x, self.drag_start_y = event.pos
                elif event.button == 4:  # Scroll Up
                    if self.show_hud and event.pos[0] < 240:
                        self.sidebar_target_scroll_y -= 45.0
                        self.sidebar_target_scroll_y = max(0.0, min(self.sidebar_max_scroll, self.sidebar_target_scroll_y))
                    else:
                        self.camera.zoom_in(1.10)
                elif event.button == 5:  # Scroll Down
                    if self.show_hud and event.pos[0] < 240:
                        self.sidebar_target_scroll_y += 45.0
                        self.sidebar_target_scroll_y = max(0.0, min(self.sidebar_max_scroll, self.sidebar_target_scroll_y))
                    else:
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
                    self.camera.rotate_orbit(dx * 0.008, -dy * 0.008)
                    self.drag_start_x, self.drag_start_y = event.pos
                elif self.is_dragging_pan:
                    dx = event.pos[0] - self.drag_start_x
                    dy = event.pos[1] - self.drag_start_y
                    self.camera.pan(dx, dy)
                    self.drag_start_x, self.drag_start_y = event.pos

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                # Navegação de personagens
                elif event.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_PAGEDOWN, pygame.K_RIGHTBRACKET):
                    self.next_character()
                elif event.key in (pygame.K_LEFT, pygame.K_UP, pygame.K_PAGEUP, pygame.K_LEFTBRACKET):
                    self.prev_character()

                # Poses
                elif event.key in (pygame.K_p, pygame.K_TAB):
                    self.next_pose()
                elif event.key == pygame.K_1:
                    self.set_pose_by_name("IDLE")
                elif event.key == pygame.K_2:
                    self.set_pose_by_name("WALK")
                elif event.key == pygame.K_3:
                    self.set_pose_by_name("ATTACK")
                elif event.key == pygame.K_4:
                    self.set_pose_by_name("RECOVERY")
                elif event.key == pygame.K_5:
                    self.set_pose_by_name("INTRO")
                elif event.key == pygame.K_6:
                    self.set_pose_by_name("VICTORY")

                # Foco Macro (Rosto / Cabeça)
                elif event.key == pygame.K_f:
                    self.toggle_focus_target()

                # Turntable automático
                elif event.key in (pygame.K_SPACE, pygame.K_t):
                    self.auto_rotate = not self.auto_rotate

                # Hot-reload de código e modelos
                elif event.key in (pygame.K_F5, pygame.K_r):
                    self.reload_modules()

                # Reset de Câmera
                elif event.key in (pygame.K_c, pygame.K_HOME, pygame.K_BACKSPACE):
                    self.camera.reset(self.macro_focus)

                # Zoom
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.camera.zoom_in(1.20)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.camera.zoom_out(1.20)

                # Alternar overlays
                elif event.key == pygame.K_h:
                    self.show_hud = not self.show_hud
                elif event.key == pygame.K_w:
                    self.show_wireframe_marker = not self.show_wireframe_marker

                # Snapshot
                elif event.key in (pygame.K_F12, pygame.K_s):
                    snap_name = f"model_inspector_{self.char_keys[self.current_char_idx]}_{self.current_pose.lower()}.png"
                    snap_path = os.path.join(ROOT, "docs", "screenshots", snap_name)
                    self.snapshot(snap_path)

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 6:  # Options -> Reset Câmera
                    self.camera.reset(self.macro_focus)
                elif event.button in (0, 2):  # ✕ / ▢ -> Próxima Pose
                    self.next_pose()
                elif event.button == 3:  # △ -> Alternar Foco Macro (Rosto / Corpo)
                    self.toggle_focus_target()
                elif event.button == 1:  # ○ -> Turntable Automático
                    self.auto_rotate = not self.auto_rotate
                elif event.button == 9:  # L1 -> Guerreiro Anterior
                    self.prev_character()
                elif event.button == 10:  # R1 -> Próximo Guerreiro
                    self.next_character()

            elif event.type == pygame.JOYHATMOTION:
                hx, hy = event.value
                if hx > 0:
                    self.next_character()
                elif hx < 0:
                    self.prev_character()
                if hy > 0:
                    self.camera.zoom_in(1.10)
                elif hy < 0:
                    self.camera.zoom_out(1.10)

        return True

    def update(self, dt: float):
        self.anim_time += dt
        if self.auto_rotate:
            self.camera.rotate_orbit(self.auto_rotate_speed * dt, 0.0)
        if self.status_message_timer > 0.0:
            self.status_message_timer = max(0.0, self.status_message_timer - dt)

    def render(self):
        # Fundo do estúdio: gradiente radial suave em grafite escuro
        self.screen.fill((20, 22, 28))

        # Desenhar pedestal e modelo
        self.draw_pedestal(self.screen)
        self.draw_character(self.screen)

        # Desenhar HUD e fichas
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

        try:
            pygame.joystick.quit()
        except Exception:
            pass
        try:
            pygame.quit()
        except Exception:
            pass
        os._exit(0)

    def snapshot(self, output_path: str):
        """Renderiza e salva um frame PNG em alta fidelidade no caminho especificado."""
        self.render()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pygame.image.save(self.screen, output_path)
        print(f"[ModelInspector] Snapshot salvo com sucesso em: {output_path}")


# =============================================================================
# CLI
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Model Inspector 3D — Samurai Edge (Roster Completo)")
    parser.add_argument("--char", choices=list(CHARACTERS.keys()), default="kenshi", help="Personagem inicial")
    parser.add_argument("--pose", choices=POSES, default="IDLE", help="Pose inicial")
    parser.add_argument("--focus", choices=["body", "head", "hands", "feet"], default="body", help="Ponto de foco inicial")
    parser.add_argument("--azimuth", type=float, default=0.0, help="Azimute inicial em graus")
    parser.add_argument("--elevation", type=float, default=30.0, help="Elevação inicial em graus")
    parser.add_argument("--zoom", type=float, default=3.4, help="Nível de zoom inicial")
    parser.add_argument("--snapshot", type=str, default=None, help="Salva snapshot PNG e sai")
    parser.add_argument("--save-all", action="store_true", help="Salva snapshots de todos os 18 modelos em docs/screenshots/ e sai")
    parser.add_argument("--width", type=int, default=1280, help="Largura da janela")
    parser.add_argument("--height", type=int, default=720, help="Altura da janela")
    parser.add_argument("--headless", action="store_true", help="Executa sem janela gráfica aberta")
    args = parser.parse_args()

    is_headless = args.headless or (args.snapshot is not None) or args.save_all
    inspector = ModelInspector(width=args.width, height=args.height, headless=is_headless)

    if args.save_all:
        out_dir = os.path.join(ROOT, "docs", "screenshots", "models")
        os.makedirs(out_dir, exist_ok=True)
        for idx, key in enumerate(CHARACTERS.keys()):
            inspector.select_character(idx)
            inspector.macro_focus = "body"
            inspector.camera.set_focus_target("body")
            snap_path = os.path.join(out_dir, f"model_{key}_full.png")
            inspector.snapshot(snap_path)
            # Close-up na face
            inspector.macro_focus = "head"
            inspector.camera.set_focus_target("head")
            snap_face_path = os.path.join(out_dir, f"model_{key}_face.png")
            inspector.snapshot(snap_face_path)
        print(f"[ModelInspector] Todos os 18 modelos salvos em: {out_dir}")
        try:
            pygame.joystick.quit()
        except Exception:
            pass
        try:
            pygame.quit()
        except Exception:
            pass
        os._exit(0)

    char_idx = list(CHARACTERS.keys()).index(args.char)
    inspector.select_character(char_idx)
    inspector.set_pose_by_name(args.pose)
    inspector.macro_focus = args.focus
    inspector.camera.set_focus_target(args.focus)
    inspector.camera.azimuth = math.radians(args.azimuth)
    inspector.camera.elevation = math.radians(args.elevation)
    if args.zoom != 3.4:
        inspector.camera.zoom = args.zoom

    if args.snapshot:
        inspector.snapshot(args.snapshot)
        try:
            pygame.joystick.quit()
        except Exception:
            pass
        try:
            pygame.quit()
        except Exception:
            pass
        os._exit(0)
    else:
        inspector.run()


if __name__ == "__main__":
    main()
