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
    os.environ.setdefault("SDL_JOYSTICK_IOKIT", "0")
    os.environ.setdefault("SDL_JOYSTICK_MFI", "1")

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

# Catálogo de botões de animação e golpes dedicados por personagem (Fase 2 Overhaul)
CHARACTER_ANIM_BUTTONS = {
    "kenshi": [
        ("IDLE", "1. Idle (Postura Iai)", 0.0),
        ("WALK", "2. Walk (Passada)", 0.0),
        ("IAI_SLICE", "3. Golpe 1: Iai Slice (Koiguchi + Dash + Noto)", 0.72),
        ("RYUU_TSUI_SEN", "4. Golpe 2: Ryuu Tsui Sen (3 Fases + Zanzou)", 0.65),
        ("SHUKUCHI", "5. Esquiva: Shukuchi Dash (Zanzou)", 0.48),
        ("SHUKUCHI_CANCEL", "6. Cancel: Shukuchi Battou-Giri (40% -> Iai)", 0.72),
        ("PARRY_GROUND", "7. Parry Terrestre: Backhop + Noto", 0.85),
        ("PARRY_AERIAL", "8. Parry Aéreo: Mortal 360° no Ar", 1.15),
        ("INTRO", "9. Intro: Meditação & Koiguchi-Kiri", 2.00),
        ("VICTORY", "0. Vitória: Chiburi Lateral & Noto", 2.20),
        ("FINISHER_1", "F1. Finisher 1: Ittou Ryoudan (5 Zanzou)", 1.25),
        ("FINISHER_2", "F2. Finisher 2: Divisão Celestial (Ryuu)", 1.35),
    ],
    "raiden": [
        ("IDLE", "1. Idle (Postura Kamae)", 0.0),
        ("WALK", "2. Walk (Suriashi Yokozuna)", 0.0),
        ("TSUPPARI_1", "3. Golpe 1: Harite (Palma Direita)", 0.60),
        ("TSUPPARI_2", "4. Golpe 2: Morote-Tsuppari (Quebra Guarda)", 0.65),
        ("TACHIAI_TACKLE", "5. Investida: Tachiai Tackle (3 Fases / Aceleração)", 0.75),
        ("SHIKO_SLIP", "6. Esquiva: Shiko Slip-Step (Solo)", 0.45),
        ("GASSHO_PARRY", "7. Guarda: Gassho-hineri (Braços Cruzados)", 0.50),
        ("HATAKI_KOMI", "8. Contra-ataque: Hataki-komi Shove", 0.55),
        ("INTRO", "9. Intro: Palmas Cerimoniais & Sonkyo", 2.00),
        ("VICTORY", "0. Vitória: Shiko 90° & Rugido no Mawashi", 2.20),
        ("FINISHER_1", "F1. Finisher 1: Tsuppari Sonic Decapitation", 1.25),
        ("FINISHER_2", "F2. Finisher 2: Tachiai Cataclysmic Slam", 1.35),
    ],
    "musashi": [
        ("IDLE", "1. Idle (Postura Chūdan)", 0.0),
        ("WALK", "2. Walk (Passada Marcial)", 0.0),
        ("ATTACK_1", "3. Golpe 1: Katana Descendente", 0.60),
        ("ATTACK_2", "4. Golpe 2: Wakizashi Ascendente", 0.60),
        ("ATTACK_3", "5. Golpe 3: Clivagem em X (Onda)", 0.65),
        ("CROSS_GUARD", "6. Guarda: Cross Guard Parry", 0.50),
        ("CROSS_SHOCKWAVE", "7. Contra-Ataque: Cross Shockwave", 0.65),
        ("TACTICAL_ROLL", "8. Esquiva: Rolamento Tático (Sem Zanzou)", 0.45),
        ("ROLL_CANCEL", "9. Cancel: Lunge do Rolamento (40% -> Golpe)", 0.65),
        ("INTRO", "0. Intro: Saque Duplo & Faíscas em X", 2.00),
        ("VICTORY", "V. Vitória: Duplo Chiburi & Dois Céus", 2.20),
        ("FINISHER_1", "F1. Finisher 1: Niten Ichi-ryu (3 Partes)", 1.25),
        ("FINISHER_2", "F2. Finisher 2: Cross Vacuum Slicer (4 Partes)", 1.35),
    ],
    "ninja": [
        ("IDLE", "1. Idle (Postura Ninja)", 0.0),
        ("WALK", "2. Walk (Passo Furtivo)", 0.0),
        ("ATTACK_1", "3. Golpe 1: Ninjato Reverse Slash", 0.60),
        ("ATTACK_2", "4. Golpe 2: Solar Plexus Thrust", 0.60),
        ("KUNAI_SNIPE", "5. Secundário: Kunai Snipe (Solo)", 0.50),
        ("KUNAI_AERIAL", "6. Secundário: Kunai Snipe (Aéreo)", 0.55),
        ("SHINOBI_JUMP", "7. Esquiva: Salto Ninja Parabólico", 0.65),
        ("JUMP_CANCEL", "8. Cancel: Landing Strike Lunge", 0.65),
        ("PARRY_RECOIL", "9. Parry Reaction: Queda Imediata", 0.60),
        ("INTRO", "0. Intro: Leaf Cover & Saque Ninjato", 2.00),
        ("VICTORY", "V. Vitória: Kuji-Kiri & Fumaça Negra", 2.20),
        ("FINISHER_1", "F1. Finisher 1: Tantou Kyuusho (Garganta)", 1.25),
        ("FINISHER_2", "F2. Finisher 2: Kunai Miken (Testa)", 1.25),
    ],
    "american": [
        ("IDLE", "1. Guarda Tática & Respiração", 0.0),
        ("WALK", "2. Marcha Operacional", 0.0),
        ("ATTACK", "3. Kunai Estocada Rápida", 0.35),
        ("SHURIKEN", "4. Shuriken de Combate (15.5m/s)", 0.40),
        ("FLIC_FLAC", "5. Flic-Flac Acrobático (Frente / 360°)", 0.66),
        ("YAMATO_CHARGE", "6. Yamato Bote Letal", 0.70),
        ("INTRO", "7. Intro: Luvas, Assobio & Alerta", 2.00),
        ("VICTORY", "8. Vitória: Chapéu & Banjo Clássico", 2.20),
        ("FINISHER_1", "F1. Finisher 1: 3x Shurikens (Membros & Cabeça)", 1.25),
        ("FINISHER_2", "F2. Finisher 2: Fuma Shuriken Moinho Gigante", 1.25),
    ],
    "saitou": [
        ("IDLE", "1. Idle (Postura Mibu & Kiseru)", 0.0),
        ("WALK", "2. Walk (Suriashi Rápido)", 0.0),
        ("GATOTSU_ISHIKI", "3. Golpe 1: Gatotsu Ishiki (Aceleração 14.5 m/s)", 0.70),
        ("GATOTSU_ZEROSHIKI", "4. Golpe 2: Gatotsu Zeroshiki (Queima-Roupa / Chip)", 0.55),
        ("HAORI_SIDESTEP", "5. Esquiva: Haori Sidestep (14 i-frames)", 0.45),
        ("GATOTSU_CANCEL", "6. Cancel: Gatotsu -> Sidestep (50%)", 0.65),
        ("PARRY_RECOIL", "7. Guarda/Parry: Frenagem & Recuo Elástico", 0.55),
        ("INTRO", "8. Intro: Traga no Kiseru & Saque Koiguchi", 2.20),
        ("VICTORY", "9. Vitória: Chiburi, Noto & Kiseru", 2.20),
        ("FINISHER_1", "F1. Finisher A: Gatotsu Shinkan (Empalamento)", 1.25),
        ("FINISHER_2", "F2. Finisher B: Zeroshiki Bakutotsu (Bissecção 2 Partes)", 1.35),
    ],
    "teppo": [
        ("IDLE", "1. Idle (Postura Ashigaru & Mecha Acesa)", 0.0),
        ("WALK", "2. Walk (Marcha de Infantaria)", 0.0),
        ("PRIMARY_SHOT", "3. Golpe 1: Tiro Tanegashima (26 m/s & Recuo)", 0.65),
        ("RIFLE_BUTT", "4. Golpe 2: Coronhada de Carvalho (Knockback & Stun)", 0.55),
        ("RAMROD_RELOAD", "5. Recarga: Vareta de Ferro (Ramrod Pump)", 0.85),
        ("POWDER_TRAP", "6. Secundário: Mina de Pólvora (Zoneamento)", 0.60),
        ("TRENCH_DIVE", "7. Esquiva: Trench Ashigaru Dive & Auto-Reload", 0.60),
        ("PARRY_DEFENSE", "8. Guarda: Bloqueio do Cano de Ferro", 0.50),
        ("INTRO", "9. Intro: Sopro na Brasa da Mecha & Pontaria", 2.00),
        ("VICTORY", "0. Vitória: Fuzil no Ombro & Cachimbo Kiseru", 2.20),
        ("FINISHER_1", "F1. Finisher A: Headshot Explode (一発必中)", 1.25),
        ("FINISHER_2", "F2. Finisher B: Hayago Keg Blast (Detonação)", 1.35),
    ],
    "murasaki": [
        ("IDLE", "1. Idle (Postura Kunoichi)", 0.0),
        ("WALK", "2. Walk (Passada Silenciosa)", 0.0),
        ("KAMA_STRIKE", "3. Golpe 1: Kama Strike (Precedência / 1.30m)", 0.54),
        ("CHAIN_DRAG", "4. Golpe 2: Chain Drag (Grapple / 3.80m / 1 HP)", 0.65),
        ("BACKFLIP", "5. Salto: Chain Whirl Backflip (360° / Escudo)", 0.55),
        ("DODGE_CANCEL", "6. Cancelamento: Backflip -> Kama Strike", 0.60),
        ("PARRY_GROUND", "7. Reação: Parry no Solo", 0.40),
        ("PARRY_AERIAL", "8. Reação: Parry Aéreo", 0.45),
        ("INTRO", "9. Intro: Giro no Dedo -> Parada Palma -> Guarda", 2.20),
        ("VICTORY", "0. Vitória: Recolhe Corrente -> Ombro -> Sumiço", 2.40),
        ("FINISHER_1", "F1. Finisher A: Kamaitachi Chain Decap (三弦微塵)", 1.20),
        ("FINISHER_2", "F2. Finisher B: Senpuu Chain Shred (旋風爆砕)", 1.40),
    ],
    "kasumi": [
        ("IDLE", "1. Idle (Postura Kunoichi da Névoa)", 0.0),
        ("WALK", "2. Walk (Passada Furtiva)", 0.0),
        ("TANTO_SLASH", "3. Golpe 1: Adaga Tanto (Precedência / 1.20m / 2 Dano)", 0.45),
        ("HOROKU_BOMB", "4. Golpe 2: Bomba Horoku (Arco Parabólico 3D)", 0.60),
        ("REMOTE_MINE", "5. Secundário: Mina Remota (Plant / Detonate)", 0.50),
        ("SMOKE_ROLL", "6. Esquiva: Salto Furtivo / Rolo de Fumaça (14 i-frames)", 0.55),
        ("DODGE_CANCEL", "7. Cancelamento: Smoke Roll -> Tanto Slash", 0.55),
        ("PARRY_REACTION", "8. Reação: Bloqueio Defensivo", 0.40),
        ("INTRO", "9. Intro: Queda Ninja -> Saque de Pavio -> Postura", 2.00),
        ("VICTORY", "0. Vitória: Chiburi -> Cápsula de Fumaça -> Sumiço", 2.20),
        ("FINISHER_1", "F1. Finisher A: Moujin Shundan (霧刃瞬断)", 1.20),
        ("FINISHER_2", "F2. Finisher B: Bakuen Funsai (爆炎粉砕)", 1.35),
    ],
    "okuni": [
        ("IDLE", "1. Idle (Dança Teatral Kabuki)", 0.0),
        ("WALK", "2. Walk (Passadas Cerimoniosas Kumadori)", 0.0),
        ("FAN_STRIKE", "3. Golpe 1: Dança dos Leques Tessen (1.45m / Duplo / 2 Dano)", 0.50),
        ("DOKUKIRI", "4. Golpe 2: Sopro Dokukiri (Cone 3.0m / Push 1.6m / Stun 0.8s)", 0.60),
        ("KAWARIMI_FEINT", "5. Esquiva: Finta Teatral Kawarimi (Manequim + i-frames)", 0.55),
        ("DODGE_CANCEL", "6. Cancelamento: Finta Kawarimi -> Fan Strike", 0.55),
        ("PARRY_REACTION", "7. Reação: Bloqueio Cruzado dos Leques", 0.40),
        ("INTRO", "8. Intro: Passadas Kumadori -> Giro Quimono -> Guarda X", 2.00),
        ("VICTORY", "9. Vitória: Ondulação Leques -> Pose Mie -> Oculta Sorriso", 2.20),
        ("FINISHER_1", "F1. Finisher A: Tessen Zanshu (鉄扇斬首)", 1.20),
        ("FINISHER_2", "F2. Finisher B: Dokukiri Youkai (毒霧溶解)", 1.40),
    ],
    "anne": [
        ("IDLE", "1. Idle (Postura Bucaneira)", 0.0),
        ("WALK", "2. Walk (Passadas com Ginga Pirata)", 0.0),
        ("CUTLASS_CLEAVE", "3. Golpe 1: Cutlass Cleave 180° (1.65m / 2 Dano / Lunge 0.65m)", 0.50),
        ("CANNON_STRIKE", "4. Golpe 2: Bombardeio Naval Celeste (Hold / Mira Orbital)", 0.60),
        ("SWASHBUCKLE_DASH", "5. Esquiva: Salto com Pólvora Negra (12 i-frames / Fuligem)", 0.55),
        ("DODGE_CANCEL", "6. Cancelamento: Swashbuckle Dash -> Cutlass Cleave", 0.55),
        ("PARRY_REACTION", "7. Reação: Guarda Defensiva com Alfanje", 0.40),
        ("INTRO", "8. Intro: Giro do Alfanje -> Lâmina na Garganta -> Guarda", 2.20),
        ("VICTORY", "9. Vitória: Gole de Rum -> Estandarte Jolly Roger -> Riso", 2.40),
        ("FINISHER_1", "F1. Finisher A: Aranami Ryoudan (荒波両断)", 1.20),
        ("FINISHER_2", "F2. Finisher B: Kanpou Senmetsu (艦砲殲滅)", 1.40),
    ],
    "julie": [
        ("IDLE", "1. Idle (Postura En Garde Nobre)", 0.0),
        ("WALK", "2. Walk (Passadas Ágeis de Esgrima)", 0.0),
        ("FLECHE_THRUST", "3. Golpe 1: Fleche Thrust (1.30m Reach / 0.70m Hitbox / 2 Dano)", 0.48),
        ("FLINTLOCK_SHOT", "4. Golpe 2: Pederneira de Bolso (5.8m Range / 6.0s CD)", 0.50),
        ("CAPE_FLOURISH", "5. Secundário: Floreio de Capa & Coup de Pied (Repel 2.0m)", 0.45),
        ("CAPE_SWIRL_BACKHOP", "6. Esquiva: Salto Acrobático com Capa (13 i-frames)", 0.55),
        ("DODGE_CANCEL", "7. Cancelamento: Cape Swirl -> Fleche Thrust", 0.55),
        ("PARRY_REACTION", "8. Reação: Guarda En Garde com Florete", 0.40),
        ("INTRO", "9. Intro: Retirada de Chapéu -> Reverência Nobre -> En Garde", 2.20),
        ("VICTORY", "0. Vitória: Embainhar às Cegas -> Luva Branca -> Fumaça", 2.40),
        ("FINISHER_1", "F1. Finisher A: Hyakka Rantotsu (百花乱突)", 1.20),
        ("FINISHER_2", "F2. Finisher B: Zero-Kyori Juusatsu (零距離銃殺)", 1.35),
    ],
    "tomoe": [
        ("IDLE", "1. Idle (Postura Kyudo Zen)", 0.0),
        ("WALK", "2. Walk (Passadas Serenas Hakama)", 0.0),
        ("QUICK_SNIPE", "3. Golpe 1: Disparo Direto Yumi (32.0 vel / 0.50s CD)", 0.50),
        ("SACRED_VOLLEY", "4. Secundário: Chuva de Flechas Sagradas em Arco", 0.65),
        ("ROPE_ARROW", "5. Golpe 2: Flecha de Corda & Deslocamento", 0.55),
        ("MIKO_ROLL", "6. Esquiva: Salto Giratório Hakama (12 i-frames)", 0.50),
        ("DODGE_CANCEL", "7. Cancelamento: Miko Roll -> Quick Snipe", 0.55),
        ("PARRY_REACTION", "8. Reação: Guarda Defensiva com Arco Yumi", 0.40),
        ("INTRO", "9. Intro: Vento no Yumi -> Teste de Tensão -> Postura Zen", 2.20),
        ("VICTORY", "0. Vitória: Descanso do Arco -> Reverência Kami -> Respiração Zen", 2.40),
        ("FINISHER_1", "F1. Finisher A: Jifuu Kyoukyuu (地縫強弓 - Pinned to Earth)", 1.20),
        ("FINISHER_2", "F2. Finisher B: Hama Tenkan (破魔天貫 - Salva Purificadora)", 1.40),
    ],
    "ren": [
        ("IDLE", "1. Idle (Postura dos Três Dragões)", 0.0),
        ("WALK", "2. Walk (Passadas Firmes Shaolin)", 0.0),
        ("JAB_STRIKE", "3. Golpe 1: Jab Frontal Veloz (Passo 1 / 1.30m)", 0.45),
        ("COMBO_STRIKES", "4. Golpe 2: Palma de Ferro & Chute do Dragão", 0.60),
        ("KIAI_SHOUT", "5. Secundário: Grito Místico Kiai (Barreira Chi 360°)", 0.50),
        ("SHAOLIN_ROLL", "6. Esquiva: Salto Acrobático Shaolin (12 i-frames)", 0.45),
        ("DODGE_CANCEL", "7. Cancelamento: Salto Acrobático -> Jab/Palma", 0.50),
        ("PARRY_REACTION", "8. Reação: Guarda Defensiva de Palma de Ferro", 0.40),
        ("INTRO", "9. Intro: Saudação Baoquan -> Jab & Chute -> Postura Zen", 2.20),
        ("VICTORY", "0. Vitória: Chute do Dragão -> Rugido Kiai -> Reverência", 2.40),
        ("FINISHER_1", "F1. Finisher A: Hyakuretsu Ken (百烈拳 - Cem Punhos)", 1.20),
        ("FINISHER_2", "F2. Finisher B: Kiai Shougeki (気合衝撃 - Rugido Chi)", 1.35),
    ],
    "chiyo": [
        ("IDLE", "1. Idle (Postura Felina Kunoichi)", 0.0),
        ("WALK", "2. Walk (Passadas Silenciosas)", 0.0),
        ("KODACHI_CROSS", "3. Golpe 1: Corte Cruzado Duplo (Combo 3-Hit)", 0.45),
        ("MAI_DANCE", "4. Secundário A: Dança Mai Evasiva (Deflexão)", 0.40),
        ("ACROBAT_LUNGE", "5. Secundário B: Salto Acrobático Lunge (3.2m)", 0.55),
        ("SHADOW_STEP", "6. Esquiva: Shadow Step Slip (14 i-frames & Pétalas)", 0.45),
        ("DODGE_CANCEL", "7. Cancelamento: Shadow Step -> Dança Mai", 0.50),
        ("PARRY_REACTION", "8. Reação: Guarda em X com as Duas Kodachis", 0.40),
        ("INTRO", "9. Intro: Saque das Costas -> Giro de Lâminas -> Postura Felina", 2.20),
        ("VICTORY", "0. Vitória: Espiral dos Pulsos -> Embainhar Reverso -> Triunfo", 2.40),
        ("FINISHER_1", "F1. Finisher A: Triple Scissor Cleave (双刃十字)", 1.20),
        ("FINISHER_2", "F2. Finisher B: Shadow Lotus Flurry (影蓮乱舞)", 1.35),
    ],
    "benkei": [
        ("IDLE", "1. Idle (Postura do Monge Guardião)", 0.0),
        ("WALK", "2. Walk (Passos Firmes de Tanque)", 0.0),
        ("NAGINATA_CLEAVE", "3. Golpe 1: Varredura Circular 170°", 0.40),
        ("NAGINATA_THRUST", "4. Golpe 2: Estocada Colossal 2.8m", 0.45),
        ("NAGINATA_THROW", "5. Secundário: Arremesso Supersônico", 0.45),
        ("TACKLE_CHARGE", "6. Desarmado: Tackle de Atropelo com Stun", 0.50),
        ("ADAMANTINE_PUSH", "7. Terceira Ação: Adamantine Guard Push", 0.45),
        ("PARRY_REACTION", "8. Reação: Guarda Defensiva de Ferro", 0.40),
        ("INTRO", "9. Intro: Giro de Haste -> Cravada Ishizuki -> Guarda", 2.20),
        ("VICTORY", "0. Vitória: Chiburi Helicoidal -> Descanso -> Reverência", 2.40),
        ("FINISHER_1", "F1. Finisher A: Kongou Tataki-Otoshi (金剛叩落)", 1.25),
        ("FINISHER_2", "F2. Finisher B: Naginata Souki (薙刀槍旗)", 1.30),
    ],
    "orin": [
        ("IDLE", "1. Idle (Postura de Cortesã com Shamisen)", 0.0),
        ("WALK", "2. Walk (Passo Leve e Fluido)", 0.0),
        ("SONIC_CLEAVE_1", "3. Golpe 1: Kamaitachi Sônico (1 Lâmina)", 0.40),
        ("SONIC_CLEAVE_2", "4. Golpe 2: Kamaitachi Duplo em V", 0.42),
        ("RESONANCE_360", "5. Secundário: Ressonância Acústica 360°", 0.45),
        ("SILK_GLIDE", "6. Esquiva: Deslize de Seda (Silk Sleeve Glide)", 0.40),
        ("EVASIVE_CANCEL", "7. Cancelamento: Corte Sônico Evasivo", 0.38),
        ("PARRY_REACTION", "8. Reação: Guarda Acústica de Seda", 0.40),
        ("INTRO", "9. Intro: Afinação -> Giro Furisode -> Postura de Cortesã", 2.20),
        ("VICTORY", "0. Vitória: Acorde Triunfal -> Giro Costas -> Pétalas", 2.40),
        ("FINISHER_1", "F1. Finisher A: Kamaitachi Mince (鎌鼬千切)", 1.20),
        ("FINISHER_2", "F2. Finisher B: Resonance Wind Gale (風鳴共鳴)", 1.30),
    ],
    "goro": [
        ("IDLE", "1. Idle (Postura do Fazendeiro com Kuwa)", 0.0),
        ("WALK", "2. Walk (Passadas Pesadas de Lavrador)", 0.0),
        ("KUWA_HEAVY_CLEAVE", "3. Golpe Primário: Corte da Kuwa (Hiper-Inércia 2.4m)", 0.44),
        ("EARTH_STOMP_ACTION", "4. Secundário: Pisotão Sísmico (Terremoto 4.2m)", 0.45),
        ("MUD_ROLL", "5. Esquiva: Rolamento de Lama (Peasant Mud Roll)", 0.40),
        ("POCKET_DIRT", "6. Cancelamento: Pocket Dirt (Terra nos Olhos)", 0.35),
        ("IRON_GUARD", "7. Guarda: Defesa de Ferro com o Cabo da Kuwa", 0.40),
        ("PARRY_REACTION", "8. Reação: Bloqueio Firme Telúrico", 0.40),
        ("INTRO", "9. Intro: Enxada no Ombro -> Cravada no Solo -> Desafio", 2.20),
        ("VICTORY", "0. Vitória: Apoio na Enxada -> Limpeza de Suor -> Risada", 2.40),
        ("FINISHER_1", "F1. Finisher A: Kuwa Skull Cleave (鍬頭砕断)", 1.25),
        ("FINISHER_2", "F2. Finisher B: Earthquake Stomp Crush (地鳴踏潰)", 1.30),
    ],
    "ichi": [
        ("IDLE", "1. Idle (Postura da Bengala de Viagem)", 0.0),
        ("WALK", "2. Walk (Caminhada Tateante de Bengala)", 0.0),
        ("GYAKU_IAI_QUICKDRAW", "3. Primário: Gyaku-Iai Cego (Saque Relâmpago 1.8m)", 0.38),
        ("LISTEN_STANCE", "4. Secundário: Postura de Escuta Sensorial (Ecolocalização)", 0.42),
        ("BLIND_COUNTER_THRUST", "5. Contra-Ataque: Blind Counter-Thrust (Estocada 1.7m)", 0.38),
        ("CANE_TAP_SLIP", "6. Esquiva: Desvio Evasivo da Bengala (13 i-frames)", 0.35),
        ("SHEATH_PARRY", "7. Defesa: Bloqueio Técnico com a Bainha de Madeira", 0.36),
        ("PARRY_REACTION", "8. Reação: Desvio Táctil & Repelência de Lâmina", 0.38),
        ("INTRO", "9. Intro: Caminhada Tateante -> Destrave do Aço -> Guarda Serena", 2.20),
        ("VICTORY", "0. Vitória: Limpeza de Lâmina na Manga -> Embainhar Zen -> Brisa", 2.40),
        ("FINISHER_1", "F1. Finisher A: Blind Carotid Slice (盲刃頚断)", 1.25),
        ("FINISHER_2", "F2. Finisher B: Blind Spine Pierce (盲背心貫)", 1.30),
    ],
    "valerius": [
        ("IDLE", "1. Idle (Respiração & Guarda Cerimonial)", 0.0),
        ("WALK", "2. Walk (Passos Aristocráticos com Foice)", 0.0),
        ("SCYTHE_REAP", "3. Primário: Ceifada Fúnebre (Alcance 1.95m, Dano 2)", 0.40),
        ("SUMMON_GRASPER", "4. Secundário A: Evocar Rastejante (Ankle Grab)", 0.42),
        ("SUMMON_SWORDSMAN", "5. Secundário B: Evocar Soldado (Saber Slash)", 0.42),
        ("SUMMON_WIGHT", "6. Secundário C: Evocar Wight (Pyre Sprint)", 0.42),
        ("CORPSE_DETONATION", "7. Detonação: Estalo de Dedos & Chamas Azuis", 0.38),
        ("MIST_DASH", "8. Esquiva: Névoa Espectral (13 i-frames)", 0.35),
        ("SCYTHE_GUARD", "9. Guarda: Defesa Técnica com Foice & Cabo", 0.36),
        ("INTRO", "0. Intro: Névoa -> Ajuste do Monóculo -> Guarda", 2.20),
        ("VICTORY", "F1. Vitória: Dissipação da Foice -> Vênia Prussiana", 2.40),
        ("FINISHER_1", "F2. Finisher A: Soul Reap (首刈骸生)", 1.25),
        ("FINISHER_2", "F3. Finisher B: Dragged to the Grave (黄泉引摺)", 1.30),
    ],
    "seimei": [
        ("IDLE", "1. Idle (Flutuação Zen & Leque Sensu)", 0.0),
        ("WALK", "2. Walk (Passos Espirituais Flutuantes)", 0.0),
        ("OFUDA_TOSS", "3. Primário: Disparo Ofuda Reto (6.5m, Dano 2)", 0.35),
        ("SACRED_WARD", "4. Secundário: Selo Kekkai (5.5s, Limite 2)", 0.40),
        ("SHIKIGAMI_GLIDE", "5. Esquiva: Deslize Shikigami (13 i-frames)", 0.36),
        ("ASTRAL_GUARD", "6. Guarda: Kekkai Protetor Onmyōdō", 0.36),
        ("PARRY_REACTION", "7. Reação: Repelência Astral & Pétalas", 0.38),
        ("INTRO", "8. Intro: Voo Shikigami -> Abertura Sensu -> Foco", 2.20),
        ("VICTORY", "9. Vitória: Giro do Sensu -> Pássaros -> Vênia", 2.40),
        ("FATAL_FIRE", "0. Fatal Fogo: Seien Kaijin (青炎灰燼)", 1.30),
        ("FATAL_WATER", "F1. Fatal Água: Suisou Shouka (水葬昇華)", 1.30),
        ("FATAL_WOOD", "F2. Fatal Madeira: Shinju Rinne (神樹輪廻)", 1.30),
        ("FATAL_METAL", "F3. Fatal Metal: Kongou Fuubaku (金剛封縛)", 1.30),
        ("FATAL_EARTH", "F4. Fatal Terra: Ganshuku Kaseki (岩宿化石)", 1.30),
        ("FATAL_YINYANG", "F5. Fatal Yin-Yang: In-You Tenchuu (陰陽天誅)", 1.30),
    ],
    "daiki": [
        ("IDLE", "1. Idle (Postura Chudan Zen)", 0.0),
        ("WALK", "2. Walk (Passada de Peregrino)", 0.0),
        ("BO_STRIKE", "3. Primário: Varredura Helicoidal 180° (2.4m)", 0.48),
        ("POLE_VAULT", "4. Secundário: Salto com Vara & Queda Meteoro (2 HP)", 0.65),
        ("STAFF_HOP", "5. Esquiva: Salto com Apoio no Bastão (13 i-frames)", 0.36),
        ("BO_TWIRL", "6. Cancel: Giro de Hélice Repelente", 0.42),
        ("BO_SPIN_GUARD", "7. Guarda: Deflexão Giratória com Bō", 0.38),
        ("INTRO", "8. Intro: Giro Helicoidal -> Cravada Zen", 2.20),
        ("VICTORY", "9. Vitória: Equilíbrio Zen na Palma -> Reverência", 2.40),
        ("FINISHER_1", "F1. Finisher 1: Alavanca Cervical na Garganta", 1.25),
        ("FINISHER_2", "F2. Finisher 2: Meteor Staff Slam no Solo", 1.35),
    ],
    "aoi": [
        ("IDLE", "1. Idle (Postura de Caça Neutra)", 0.0),
        ("WALK", "2. Walk (Passo Rastreador na Neve)", 0.0),
        ("SPEAR_LUNGE", "3. Primário: Bone Spear Lunge (2.20m, 1 HP)", 0.44),
        ("BEAR_TRAP", "4. Secundário: Plantar Armadilha (Root 1.4s)", 0.50),
        ("HUNT_SLIDE", "5. Esquiva: Tundra Hunt Slide (13 i-frames)", 0.36),
        ("HUNTER_GUARD", "6. Defesa: Guarda Técnica Makiri & Lança", 0.45),
        ("INTRO", "7. Intro: Saudação Kamuy & Capuz de Pele", 2.00),
        ("VICTORY", "8. Vitória: Chamado Solene da Taiga", 2.20),
        ("FINISHER_1", "F1. Finisher 1: Armadilha & Estocada na Jugular", 1.25),
        ("FINISHER_2", "F2. Finisher 2: Empalação & Arremesso no Solo", 1.35),
    ],
    "hendrika": [
        ("IDLE", "1. Idle (Análise Química)", 0.0),
        ("WALK", "2. Walk (Passo Acadêmico)", 0.0),
        ("STILETTO_THRUST", "3. Primário: Surgical Stiletto (1.15m)", 0.36),
        ("FLASK_TOSS", "4. Secundário: Arremesso Frasco Alquímico", 0.42),
        ("DEJIMA_SLIDE", "5. Esquiva: Dejima Chemist Slide (13 i-frames)", 0.35),
        ("ALCHEMIST_GUARD", "6. Defesa: Guarda com Estilete & Fumaça", 0.36),
        ("CYCLE_REAGENT", "7. Síntese: Ciclar Reagente da Bandoleira", 0.30),
        ("INTRO", "8. Intro: Inspeção de Frasco & Teste no Estilete", 2.00),
        ("VICTORY", "9. Vitória: Caderno de Campo & Relógio de Bolso", 2.20),
        ("FINISHER_1", "F1. Finisher 1: Estilete Dissolvente na Carótida", 1.25),
        ("FINISHER_2", "F2. Finisher 2: Cataclismo Alquímico com Frasco", 1.35),
    ],
}
# Aliases para chaves alternativas do catálogo
CHARACTER_ANIM_BUTTONS["alchemist"] = CHARACTER_ANIM_BUTTONS["hendrika"]
CHARACTER_ANIM_BUTTONS["huntress"] = CHARACTER_ANIM_BUTTONS["aoi"]
CHARACTER_ANIM_BUTTONS["pilgrim"] = CHARACTER_ANIM_BUTTONS["daiki"]
CHARACTER_ANIM_BUTTONS["joe"] = CHARACTER_ANIM_BUTTONS["american"]
CHARACTER_ANIM_BUTTONS["hanzo"] = CHARACTER_ANIM_BUTTONS["ninja"]
CHARACTER_ANIM_BUTTONS["rifleman"] = CHARACTER_ANIM_BUTTONS["teppo"]
CHARACTER_ANIM_BUTTONS["purple"] = CHARACTER_ANIM_BUTTONS["murasaki"]
CHARACTER_ANIM_BUTTONS["gray"] = CHARACTER_ANIM_BUTTONS["kasumi"]
CHARACTER_ANIM_BUTTONS["kabuki"] = CHARACTER_ANIM_BUTTONS["okuni"]
CHARACTER_ANIM_BUTTONS["pirate"] = CHARACTER_ANIM_BUTTONS["anne"]
CHARACTER_ANIM_BUTTONS["musketeer"] = CHARACTER_ANIM_BUTTONS["julie"]
CHARACTER_ANIM_BUTTONS["archer"] = CHARACTER_ANIM_BUTTONS["tomoe"]
CHARACTER_ANIM_BUTTONS["shaolin"] = CHARACTER_ANIM_BUTTONS["ren"]
CHARACTER_ANIM_BUTTONS["nodachi"] = CHARACTER_ANIM_BUTTONS["chiyo"]
CHARACTER_ANIM_BUTTONS["sohei"] = CHARACTER_ANIM_BUTTONS["benkei"]
CHARACTER_ANIM_BUTTONS["minstrel"] = CHARACTER_ANIM_BUTTONS["orin"]
CHARACTER_ANIM_BUTTONS["farmer"] = CHARACTER_ANIM_BUTTONS["goro"]
CHARACTER_ANIM_BUTTONS["blind"] = CHARACTER_ANIM_BUTTONS["ichi"]
CHARACTER_ANIM_BUTTONS["shikomizue"] = CHARACTER_ANIM_BUTTONS["ichi"]
CHARACTER_ANIM_BUTTONS["necromancer"] = CHARACTER_ANIM_BUTTONS["valerius"]
CHARACTER_ANIM_BUTTONS["faust"] = CHARACTER_ANIM_BUTTONS["valerius"]
CHARACTER_ANIM_BUTTONS["onmyoji"] = CHARACTER_ANIM_BUTTONS["seimei"]

DEFAULT_ANIM_BUTTONS = [
    ("IDLE", "1. Idle (Respiração)", 0.0),
    ("WALK", "2. Walk (Caminhada)", 0.0),
    ("ATTACK", "3. Golpe Primário (Attack)", 0.60),
    ("RECOVERY", "4. Recuperação (Recovery)", 0.60),
    ("INTRO", "5. Animação de Intro", 2.00),
    ("VICTORY", "6. Animação de Vitória", 2.20),
]

OVERHAUL_DE_PARA_NOTES = {
    "kenshi": [
        "SSAA 2x Offscreen (Zero serrilhado na lâmina/silhueta)",
        "Olhos Anime HD (Anel limbal, degradê mel, meditação)",
        "Materiais: Seda Chirimen, Linho Índigo, Laca Urushi, Hamon",
        "Pose LERP 0.08s + Koiguchi-kiri + Ryuu 3-Fases + Mortal 360°",
    ],
    "raiden": [
        "SSAA 2x Offscreen (Zero serrilhado no porte colossal e cordas sagradas)",
        "Olhos Anime Rikishi HD (Olhar marcial focado, sobrancelhas cerradas, coque Oicho em leque)",
        "Materiais: Corda Sagrada Shimenawa, Serpentinas Gohei, Seda Carmesim, Ouro, Couro",
        "Tachiai 3 Fases: Aceleração contínua (4.0 -> 12.5 m/s) + 2 de Dano em Velocidade Máxima",
        "Combo Tsuppari: Harite + Morote Quebra-Guarda + Esquiva Shiko no Dohyo",
    ],
    "musashi": [
        "SSAA 2x Offscreen (Zero serrilhado nas lâminas duplas e cordões)",
        "Rosto Marcial Veterano (Olhar severo, cicatriz na sobrancelha e barba por fazer)",
        "Materiais: Quimono Índigo, Linho Cru, Laca Urushi, Hamon Tamahagane",
        "Combo Niten 3 Tempos (Sem embainhar) + Postura dos Dois Céus",
        "Rolamento Tático sem Zanzou + Cancelamento Ofensivo aos 40%",
    ],
    "ninja": [
        "SSAA 2x Offscreen (Zero serrilhado nas lâminas, capuz e kunais)",
        "Olhos Marciais Ambarinos HD (Anel limbal dourado penetrante sob a máscara)",
        "Materiais: Seda Shozoku, Lona Tabi, Aço Tamahagane, Ouro Urushi",
        "Ninjato com Empunhadura Invertida (Bainha vazia ao sacar para combate)",
        "Salto Acrobático sem Zanzou + Cancelamento Ofensivo aos 40%",
        "Anti-Floating: Queda imediata no solo se aparado no ar",
    ],
    "american": [
        "SSAA 2x Offscreen (Zero serrilhado no colete, rádio e mochila MOLLE)",
        "Olhos Marciais Masculinos HD (Olhar focado sem vazamento sob balaclava)",
        "Materiais: Farda Camuflada Ripstop, Couro, Tricô Balaclava, Madeira e Aço",
        "Flic-Flacs Acrobáticos: Encadeável até 3x com colisão em obstáculos sólidos",
        "Yamato Letal (1-Hit Kill fatal a 18.5 m/s com perseguição) + Banjo na Vitória",
        "Finishers: 3x Shurikens Desmembradoras & Fuma Shuriken Decapitadora",
    ],
    "saitou": [
        "SSAA 2x Offscreen (Zero serrilhado no haori Asagi-iro e padrão Dandara)",
        "Olhos Marciais Sanpaku HD (Olhar severo do Lobo de Mibu com anel limbal de aço)",
        "Materiais: Seda Asagi-iro, Linho Branco com Kanji 誠, Laca Urushi, Fumo de Kiseru 3D",
        "Gatotsu Ishiki: Aceleração contínua (5.2 -> 14.5 m/s) + Cancelamento em Haori Sidestep aos 50%",
        "Gatotsu Zeroshiki: Explosão a queima-roupa com 1 de Dano Garantido (Chip Damage através do Parry)",
        "Finishers: Gatotsu Shinkan (Empalamento Cardíaco) & Zeroshiki Bakutotsu (Bissecção Horizontal)",
    ],
    "teppo": [
        "SSAA 2x Offscreen (Zero serrilhado no longo cano octogonal de ferro e na Jingasa)",
        "Olhos Marciais Ashigaru HD (Olho direito contraído na mira com anel limbal + bigode 3D)",
        "Materiais: Carvalho Envernizado, Ferro Fundido, Laca Jingasa Tonbo, Cânhamo e Couro",
        "Ciclo de Munição Fluido: Tiro Supersônico (26 m/s) + Recarga por Vareta Ramrod ou Trench Dive",
        "Coronhada Pesada de Madeira sem bala (1.8m Knockback + 0.65s Stun) + Mina de Pólvora Secundária",
        "Finishers: Headshot Explode (Queixo) & Hayago Keg Blast (Detonação de Cargas de Pólvora)",
        "Intro (Sopro na Brasa da Mecha) & Vitória (Fuzil no Ombro + Cachimbo Kiseru 3D)",
    ],
    "murasaki": [
        "SSAA 2x Offscreen + Rosto Anime HD (Olhos ametista brilhantes, máscara shinobi sem vazamento)",
        "Materiais Físicos Realistas: Seda Chirimen púrpura, Aço temperado de alto carbono, Ferro negro",
        "Kama Strike (1.30m, Precedência absoluta / clash fluido) & Chain Drag (3.80m, Dano 1 + Puxão + Stun)",
        "Chain Whirl Backflip: Salto mortal 360° com escudo giratório de corrente (deflete projéteis leves)",
        "Finishers Duplos: Kamaitachi Chain Decap (三弦微塵) & Senpuu Chain Shred Tornado (旋風爆砕)",
        "Intro (Giro orbital no dedo -> Palma -> Guarda) & Vitória (Recolhimento espiral -> Ombro -> Sumiço)",
    ],
    "kasumi": [
        "SSAA 2x Offscreen + Rosto Anime HD (Olhos azul-aço luminosos, nariz delicado e cílios alados)",
        "Materiais PBR Realistas: Couro preto curtido, Traje justo cromado, Cachecol de linho névoa",
        "Gola Shinobi Perfeita: neck e jaw herdam cor do cachecol sem vazamento de pele sob o colarinho",
        "Sistema Híbrido: Corte de Adaga Tanto (<= 1.6m / 2 Dano) + Bomba Horoku (> 1.6m em arco 3D)",
        "Ação Secundária: Mina de Detonação Remota (1º toque planta, 2º detona / 2.2m raio com dano 2)",
        "Esquiva Furtiva: Rolo ninja com tapete espesso de fumaça e 1.0s de camuflagem (alpha=15)",
        "Finishers Duplos: Moujin Shundan (Decapitação limpa) & Bakuen Funsai (Cataclismo 26+ pedaços)",
        "Intro (Queda Shinobi -> Saque de Pavio -> Guarda) & Vitória (Chiburi -> Cápsula -> Sumiço)",
    ],
    "okuni": [
        "SSAA 2x Offscreen + Rosto Anime HD (Kumadori carmesim dramático, olhos vermelhos, nariz e lábios delicados)",
        "Materiais PBR Realistas: Seda Chirimen bordada em ouro, Linho do quimono, Laca Urushi, Aço temperado Tessen",
        "Dança dos Leques Tessen: Alcance de 1.45m, golpe duplo gracioso e letal com 2 de dano",
        "Sopro Venenoso Dokukiri: Cone frontal 3.0m, empurrão de 1.6m, Whiff Stun de tosse 0.8s e debuff -25% SPD",
        "Microvoxels 3D Volumétricos na névoa venenosa com vórtices alternando púrpura e esmeralda",
        "Finta Teatral Kawarimi: Manequim de seda no ponto de partida que causa whiff punish fatal de 0.45s se golpeado",
        "Finishers Duplos: Tessen Zanshu (Decapitação em tesoura com sakura) & Dokukiri Youkai (Dissolução ácida com esqueleto)",
        "Intro Cerimonial & Vitória Teatral com interpolação suave Hermite e leques dinâmicos",
    ],
    "anne": [
        "SSAA 2x Offscreen + Rosto Anime HD (Olhos cor de avelã luminosos, queixo e lábios modelados)",
        "Materiais PBR Realistas: Couro envelhecido do sobretudo, Latão oxidado, Linho marfim, Aço damasco",
        "Cutlass Cleave 180°: Alcance amplo de 1.65m, lunge frontal de 0.65m e 2 de dano",
        "Bombardeio Naval Orbital: Retículo isométrico com astrolábio giratório dourado vindo dos céus",
        "Swashbuckle Dash: Rolamento pesado com fumaça espessa de pólvora negra (12 i-frames / slow no rival)",
        "Finishers Duplos: Aranami Ryoudan (荒波両断 - Bissecção diagonal) & Kanpou Senmetsu (艦砲殲滅 - Impacto celeste)",
        "Intro (Giro do alfanje no dedo -> Mira na garganta) & Vitória (Gole de cantil de rum -> Estandarte pirata 3D)",
    ],
    "julie": [
        "SSAA 2x Offscreen + Rosto Anime HD (Olhos safira profundos, cílios alados, postura aristocrática)",
        "Materiais PBR Realistas: Veludo azul real da casaca, Renda de seda no decote, Ouro polido, Aço fino",
        "Fleche Thrust: Bote linear perfurante com alcance de 1.30m, 2 de dano e hitbox precisa de 0.70m",
        "Pistola Pederneira de Bolso: Disparo veloz a média distância (5.8m) com fumaça volumétrica e recuo",
        "Floreio de Capa & Coup de Pied: Giro de capa que reflete projéteis e repele oponentes em 2.0m",
        "Finishers Duplos: Hyakka Rantotsu (百花乱突 - Fonte de sangue arterial) & Zero-Kyori Juusatsu (零距離銃殺)",
        "Intro (Reverência solene com chapéu na mão -> En Garde) & Vitória (Embainhar às cegas com clique -> Fumaça)",
    ],
    "tomoe": [
        "SSAA 2x Offscreen (Zero serrilhado no grande arco assimétrico Yumi e flechas Ya/Hamaya)",
        "Olhos Anime HD (Sclera de marfim, íris esmeralda vertical com anel limbal e catchlight duplo)",
        "Materiais PBR Realistas: Seda Miko Branca, Hakama Carmesim, Laca Urushi do Yumi, Couro Yugake",
        "Pose LERP 0.08s + 12 Poses Articuladas + Rotação 3D de Flechas e Tração Dinâmica de Corda",
        "Projéteis Físicos Varridos (Sub-stepped sweep contra obstáculos + Evasão perfeita por Esquiva)",
        "Fatalidades Cinematográficas: Jifuu Kyoukyuu (Flecha cravada no chão) e Hama Tenkan (Chuva Celestial)",
    ],
    "ren": [
        "SSAA 2x Offscreen (Zero serrilhado nas marcas sagradas Jieba e contas Mala)",
        "Olhos Anime HD (Esclera marfim, íris castanho-avelã, olhar marcial focado e sobrancelhas determinadas)",
        "Materiais PBR Realistas: Lona Kasaya açafrão, Seda da faixa, Linho das perneiras e Madeira de cedro",
        "Pose LERP 0.08s + 12 Poses Articuladas + Combo Marcial Rítmico de 3 Passos (Jab -> Palma -> Chute)",
        "Grito Kiai 360° com Reflexão Balística de Projéteis e Salto Acrobático com Cancelamento Ofensivo",
        "Fatalidades Cinematográficas: Hyakuretsu Ken (百烈拳) e Kiai Shougeki (気合衝撃)",
    ],
    "chiyo": [
        "SSAA 2x Offscreen (Zero serrilhado nas lâminas duplas e silhueta ágil de kunoichi)",
        "Olhos Anime HD (Esclera marfim, íris âmbar vertical luminosa, delineado carmim benibake alado)",
        "Materiais PBR Realistas: Couro preto fosco, Seda carmesim do lenço/faixa, Laca Urushi negra das bainhas, Aço polido",
        "Pose LERP 0.08s + 12 Poses Articuladas + Dança das Duas Kodachi com Salto Acrobático Lunge (3.2m)",
        "Esquiva Evasiva Shadow Step Slip (14 i-frames + Rastro de pétalas de Higanbana)",
        "Fatalidades Cinematográficas: Triple Scissor Cleave (双刃十字) e Shadow Lotus Flurry (影蓮乱舞)",
    ],
    "benkei": [
        "SSAA 2x Offscreen (Zero serrilhado no cabo da naginata, lâmina e couraça Dō-maru)",
        "Olhos Anime HD & Barba Marcial (Esclera marfim, íris âmbar/avelã profunda, barba encorpada esculpida)",
        "Materiais PBR Realistas: Placas de ferro negro laqueado, Madeira de carvalho escuro, Aço temperado e Linho cru",
        "Pose LERP 0.08s + 12 Poses Articuladas + Combo de Inércia (Varredura 170° -> Estocada Colossal 2.8m)",
        "Adamantine Guard Push (12 i-frames + Deflexão de projéteis 1.8m + Empurrão com deslocamento forçado)",
        "Fatalidades Cinematográficas: Kongou Tataki-Otoshi (金剛叩落) e Naginata Souki (薙刀槍旗)",
    ],
    "orin": [
        "SSAA 2x Offscreen (Zero serrilhado nas mangas Furisode, cordas do shamisen e penteado Shimada)",
        "Olhos Anime HD Âmbar Luminosos com Delineado Carmesim Kumadori & Tatuagem de Higanbana na Clavícula",
        "Materiais PBR Realistas: Seda Chirimen do quimono e obi, Madeira de cerejeira do shamisen, Marfim polido e Prata dos sinos",
        "Pose LERP 0.08s + 12 Poses Articuladas + Combo Acústico em 2 Etapas (Kamaitachi Sônico -> Duplo em V)",
        "Esquiva Deslize de Seda / Silk Sleeve Glide (13 i-frames + Fluidez evasiva com mangas esvoaçantes)",
        "Fatalidades Cinematográficas: Kamaitachi Mince (鎌鼬千切) e Resonance Wind Gale (風鳴共鳴)",
    ],
    "goro": [
        "SSAA 2x Offscreen (Zero serrilhado na haste de carvalho da Kuwa, lâmina de ferro e faixa Tenugui)",
        "Rosto Anime HD Masculino & Barba Rústica (Esclera marfim, íris castanho profundo, cavanhaque/stubble esculpido)",
        "Materiais PBR Realistas: Cânhamo cru do colete Noragi com costura Sashiko, Ferro rústico oxidado e Madeira áspera",
        "Pose LERP 0.08s + 12 Poses Articuladas + Kuwa Heavy Cleave (Hiper-Inércia, 2.40m de alcance e Quebra de Guarda)",
        "Rolamento de Lavrador (13 i-frames) & Cancelamento Evasivo Pocket Dirt (Micro-stun 0.22s com nuvem de terra)",
        "Fatalidades Cinematográficas: Kuwa Skull Cleave (鍬頭砕断) e Earthquake Stomp Crush (地鳴踏潰)",
    ],
    "ichi": [
        "SSAA 2x Offscreen + Iluminação Isométrica 3D Direcional e Sombra Projetada",
        "Rosto Anime 3D: Olhos cerrados serenos com cílios alados, lábios delicados e coque Mage alto com Kanzashi dourado",
        "Materiais Realistas: Seda Chirimen Ameixa, Linho Branco Juban, Cerejeira Polida e Lâmina Tamahagane com Fio Navalha",
        "Pose LERP 0.08s + 12 Poses Articuladas + Saque Invertido Gyaku-Iai (Startup 7f / 0.11s e alcance 1.80m)",
        "Postura de Escuta Auditiva com Contra-Ataque Automático (Blind Counter-Thrust) e Desvio Evasivo de Bengala (13 i-frames)",
        "Fatalidades Cinematográficas: Blind Carotid Slice (盲刃頚断) e Blind Spine Pierce (盲背心貫)",
    ],
    "valerius": [
        "SSAA 2x Offscreen + Iluminação Isométrica 3D Direcional e Sombra Projetada",
        "Rosto Aristocrático Anime 3D: Olhos azul-aço resolutos, monóculo dourado com correntinha e mechas brancas pompadour",
        "Materiais Realistas: Veludo Negro Frac, Cetim Violeta Fúnebre, Ouro Envelhecido e Lâmina com Chamas Azuis Espectrais",
        "Pose LERP 0.08s + 12 Poses Articuladas + Ceifada Cerimonial (Startup 0.25s, alcance 1.95m, raio 1.35m, dano 2)",
        "Tríade dos Mortos: Ciclo ritual de 3 servos (Rastejante imobilizador, Soldado com Pickelhaube e Wight de chamas azuis)",
        "Detonação Cadavérica: Estalo de dedos com detonação manual em chamas azuis (raio 1.6m, dano 1)",
        "Fatalidades Cinematográficas: Soul Reap (首刈骸生 - decapitação e corpo esquelético em chamas azuis) e Dragged to Grave (黄泉引摺)",
    ],
    "seimei": [
        "SSAA 2x Offscreen + Iluminação Isométrica 3D Direcional e Sombra Projetada",
        "Rosto Anime 3D: Olhos místicos safira/índigo, chapéu cerimonial Eboshi de laca negra e franja Heian",
        "Materiais Realistas: Seda Kariginu Branca com Padrão Kikko, Laca Eboshi Lustrosa, Cetim Índigo e Ouro Cerimonial",
        "Pose LERP 0.08s + 15 Poses Articuladas + Leque Sensu Dobrável + Origami Shikigami Flutuante",
        "Talismãs Ofuda Retos Bloqueáveis por Obstáculos (Alcance 6.5m, Dano 2) + Rondel Elemental Gogyō Completo",
        "Selo Sagrado Kekkai Elemental de 5.5s (Limite de 2 simultâneos) + Deslize Shikigami Evasivo (13 i-frames)",
        "6 Fatalidades Únicas por Elemento: Fogo (Cinzas), Água (Névoa/Orvalho), Madeira (Árvore Sagrada), Metal (5 Lâminas), Terra (Estátua Kintsugi) e Yin-Yang (Vórtice Taijitu)",
    ],
    "daiki": [
        "SSAA 2x Offscreen + Iluminação Isométrica 3D Direcional e Sombra Projetada",
        "Rosto Anime 3D: Olhar marcial focado, sobrancelhas expressivas, coque Chonmage e faixa Hachimaki de palha",
        "Materiais Realistas: Carvalho Vermelho Maciço envernizado, Ponteiras de Ferro Forjado, Cânhamo Azul-Ardósia e Rosário Juzu",
        "Pose LERP 0.08s + Single-Pass Rendering (get_arms) + Oclusão 360° perfeita",
        "Varredura Helicoidal de Bō de 180° (Alcance 2.40m, Anti-Spam) + Salto com Vara Acrobático (2.2m de altura, 2 HP Guard Crush)",
        "Salto Acrobático com Apoio no Bastão (Staff Vault Hop com 13 i-frames e travessia de buracos)",
        "Fatalidades Cinematográficas: Throat Temple Crush (Alavanca Cervical 360°) e Meteor Staff Slam (Cravada no Solo)",
        "Zero Static Freeze: Intro (Giro Helicoidal com folhas ao vento) e Vitória (Equilíbrio Zen na palma da mão estendida)",
    ],
    "aoi": [
        "SSAA 2x Offscreen + Shading Boreal (Pelagem de Lobo Ártico, Tecido Attush com bordados Moreu e Lança de Osso)",
        "Rosto Anime HD Boreal: Olhos azul-ártico luminosos, delicado nariz de caçadora, bochechas coradas e sutil tatuagem labial Ainu (Sinuye)",
        "Biblioteca de Materiais Realistas: Pele de lobo ártico com relevo, osso fóssil esculpido, couro de cervo (Ker) e lona Attush",
        "Golpe Primário Bone-Tipped Spear Lunge: Estocada linear veloz de altíssimo alcance (2.20m, 1 HP) com hitbox frontal estreita",
        "Ação Secundária Hunting Bear Trap: Posiciona armadilha mecânica de mandíbula de ferro no solo (máx. 2, imobilização de 1.4s e 1 HP)",
        "Esquiva Tundra Hunt Slide: Deslize rasteiro rente ao solo sobre a neve com 13 i-frames passando por baixo de tiros e flechas",
        "Fatalidades Bespoke: Trap & Execute (Armadilha fecha na perna e estocada na jugular) e Spear Impalement & Northern Sky Toss",
        "Zero Static Freeze: Intro (Reverência sagrada Kamuy, ajuste do capuz de lobo e postura de caça) e Vitória (Elevação da lança e chamado da taiga)",
    ],
    "hendrika": [
        "SSAA 2x Offscreen + Shading Barroco Holandês (Casaca de Veludo Azul-Safira, Jabot de Linho e Quepe Mercantil)",
        "Rosto Anime HD 'Mad Scientist': Olhos cinzento-aço analíticos, monóculo de latão na aba do quepe e cachos loiros em camadas 3D",
        "Biblioteca de Materiais Realistas: Vidro borossilicato translúcido, latão polido, veludo azul e couro encerado de cavalaria",
        "Balão Alquímico Dinâmico: Frasco seguro na mão esquerda com líquido e vapor que mudam de cor conforme o reagente selecionado",
        "Golpe Primário Surgical Stiletto Arterial Thrust: Estocada cirúrgica precisa nos vasos do pescoço (1.15m) que quebra parry com solvente",
        "Ação Secundária Alchemic Flask Toss: Arremesso balístico em arco gerando poça química corrosiva de 3.0s com 5 reagentes em ciclo",
        "Esquiva Dejima Chemist Slide: Deslize com manto de couro com 13 i-frames e imunidade absoluta a dano de poças ácidas",
        "Fatalidades Bespoke: Surgical Carotid Vitriol (Injeção cáustica na carótida) e Alchemic Acid Dissolve (Dissolução até esqueleto)",
        "Zero Static Freeze: Intro (Exame do frasco contra a luz e teste cáustico) e Vitória (Anotações no caderno de campo e relógio de bolso)",
    ],
}
OVERHAUL_DE_PARA_NOTES["alchemist"] = OVERHAUL_DE_PARA_NOTES["hendrika"]
OVERHAUL_DE_PARA_NOTES["huntress"] = OVERHAUL_DE_PARA_NOTES["aoi"]
OVERHAUL_DE_PARA_NOTES["pilgrim"] = OVERHAUL_DE_PARA_NOTES["daiki"]
OVERHAUL_DE_PARA_NOTES["joe"] = OVERHAUL_DE_PARA_NOTES["american"]
OVERHAUL_DE_PARA_NOTES["hanzo"] = OVERHAUL_DE_PARA_NOTES["ninja"]
OVERHAUL_DE_PARA_NOTES["rifleman"] = OVERHAUL_DE_PARA_NOTES["teppo"]
OVERHAUL_DE_PARA_NOTES["purple"] = OVERHAUL_DE_PARA_NOTES["murasaki"]
OVERHAUL_DE_PARA_NOTES["gray"] = OVERHAUL_DE_PARA_NOTES["kasumi"]
OVERHAUL_DE_PARA_NOTES["kabuki"] = OVERHAUL_DE_PARA_NOTES["okuni"]
OVERHAUL_DE_PARA_NOTES["pirate"] = OVERHAUL_DE_PARA_NOTES["anne"]
OVERHAUL_DE_PARA_NOTES["musketeer"] = OVERHAUL_DE_PARA_NOTES["julie"]
OVERHAUL_DE_PARA_NOTES["archer"] = OVERHAUL_DE_PARA_NOTES["tomoe"]
OVERHAUL_DE_PARA_NOTES["shaolin"] = OVERHAUL_DE_PARA_NOTES["ren"]
OVERHAUL_DE_PARA_NOTES["nodachi"] = OVERHAUL_DE_PARA_NOTES["chiyo"]
OVERHAUL_DE_PARA_NOTES["sohei"] = OVERHAUL_DE_PARA_NOTES["benkei"]
OVERHAUL_DE_PARA_NOTES["minstrel"] = OVERHAUL_DE_PARA_NOTES["orin"]
OVERHAUL_DE_PARA_NOTES["farmer"] = OVERHAUL_DE_PARA_NOTES["goro"]
OVERHAUL_DE_PARA_NOTES["blind"] = OVERHAUL_DE_PARA_NOTES["ichi"]
OVERHAUL_DE_PARA_NOTES["shikomizue"] = OVERHAUL_DE_PARA_NOTES["ichi"]
OVERHAUL_DE_PARA_NOTES["necromancer"] = OVERHAUL_DE_PARA_NOTES["valerius"]
OVERHAUL_DE_PARA_NOTES["faust"] = OVERHAUL_DE_PARA_NOTES["valerius"]
OVERHAUL_DE_PARA_NOTES["onmyoji"] = OVERHAUL_DE_PARA_NOTES["seimei"]


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

        pygame.display.init()
        pygame.font.init()
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

        # Modo De / Para (Comparação Lado a Lado: Modelo Antigo vs Modelo Novo Overhaul)
        self.compare_mode = False
        self.active_action = "IDLE"
        self.action_timer = 0.0
        self.action_duration = 0.0
        self._inspector_lerp_tracker = {
            "lerp_duration": 0.08,
            "blend_timer": 0.0,
            "pose_key": None,
            "prev_snap": None,
            "last_snap": None,
            "transitions_count": 0,
        }

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
        self.anim_action_btn_rects: list[tuple[str, pygame.Rect]] = []
        self.reload_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.reset_cam_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.compare_btn_rect = pygame.Rect(0, 0, 0, 0)

        # Joystick / Fightstick support (opcional no Inspector para evitar crash IOHIDManager no macOS 26)
        if os.environ.get("SAMURAI_INSPECTOR_JOYSTICK") == "1":
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
    def current_char_key(self) -> str:
        return self.char_keys[self.current_char_idx]

    @property
    def current_char_info(self) -> dict:
        return CHARACTERS[self.char_keys[self.current_char_idx]]

    @property
    def current_pose(self) -> str:
        return POSES[self.current_pose_idx]

    def get_anim_buttons(self) -> list[tuple[str, str, float]]:
        return CHARACTER_ANIM_BUTTONS.get(self.current_char_key, DEFAULT_ANIM_BUTTONS)

    def trigger_action(self, action_id: str):
        """Dispara uma animação interativa (golpe, esquiva, parry, intro, vitória ou finisher) no pedestal."""
        self.active_action = action_id
        self.action_timer = 0.0
        dur = 0.0
        for aid, _lbl, adur in self.get_anim_buttons():
            if aid == action_id:
                dur = adur
                break
        self.action_duration = dur
        if action_id in POSES:
            self.current_pose_idx = POSES.index(action_id)
        elif action_id in ("IAI_SLICE", "RYUU_TSUI_SEN", "SHUKUCHI_CANCEL", "TSUPPARI_1", "TSUPPARI_2", "HATAKI_KOMI", "ATTACK_1", "ATTACK_2", "ATTACK_3", "CROSS_SHOCKWAVE", "ROLL_CANCEL", "FINISHER_1", "FINISHER_2", "KAMA_STRIKE", "CHAIN_DRAG", "KODACHI_CROSS", "MAI_DANCE", "ACROBAT_LUNGE", "NAGINATA_CLEAVE", "NAGINATA_THRUST", "NAGINATA_THROW", "TACKLE_CHARGE", "SONIC_CLEAVE_1", "SONIC_CLEAVE_2", "RESONANCE_360", "EVASIVE_CANCEL", "KUWA_HEAVY_CLEAVE", "EARTH_STOMP_ACTION", "POCKET_DIRT", "GYAKU_IAI_QUICKDRAW", "BLIND_COUNTER_THRUST", "SCYTHE_REAP", "SUMMON_GRASPER", "SUMMON_SWORDSMAN", "SUMMON_WIGHT", "CORPSE_DETONATION", "OFUDA_TOSS", "SACRED_WARD", "FATAL_FIRE", "FATAL_WATER", "FATAL_WOOD", "FATAL_METAL", "FATAL_EARTH", "FATAL_YINYANG", "BO_STRIKE", "POLE_VAULT", "BO_TWIRL", "SPEAR_LUNGE", "BEAR_TRAP", "STILETTO_THRUST", "FLASK_TOSS"):
            self.current_pose_idx = POSES.index("ATTACK")
        elif action_id in ("SHUKUCHI", "PARRY_GROUND", "PARRY_AERIAL", "TACHIAI_TACKLE", "SHIKO_SLIP", "GASSHO_PARRY", "CROSS_GUARD", "TACTICAL_ROLL", "BACKFLIP", "DODGE_CANCEL", "SHADOW_STEP", "ADAMANTINE_PUSH", "SILK_GLIDE", "MUD_ROLL", "LISTEN_STANCE", "CANE_TAP_SLIP", "SHEATH_PARRY", "PARRY_REACTION", "MIST_DASH", "SCYTHE_GUARD", "SHIKIGAMI_GLIDE", "ASTRAL_GUARD", "STAFF_HOP", "BO_SPIN_GUARD", "HUNT_SLIDE", "HUNTER_GUARD", "DEJIMA_SLIDE", "ALCHEMIST_GUARD", "CYCLE_REAGENT"):
            self.current_pose_idx = POSES.index("RECOVERY")

    def select_character(self, idx: int | str):
        if isinstance(idx, str):
            if idx in self.char_keys:
                idx = self.char_keys.index(idx)
            else:
                idx = 0
        prev_colossal = (self.char_keys[self.current_char_idx] == "gashadokuro")
        self.current_char_idx = idx % len(self.char_keys)
        now_colossal = (self.char_keys[self.current_char_idx] == "gashadokuro")
        if prev_colossal != now_colossal:
            self.camera.reset(self.macro_focus, is_colossal=now_colossal)
        self.trigger_action("IDLE")
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
        self.trigger_action(POSES[self.current_pose_idx])

    def set_pose_by_name(self, pose: str):
        if pose in POSES:
            self.current_pose_idx = POSES.index(pose)
            self.trigger_action(pose)

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

    def _make_sub_camera(self, dx_screen: int, zoom_scale: float = 1.0) -> InspectorCamera:
        sub = InspectorCamera(self.width, self.height)
        sub.screen_x = self.camera.screen_x + dx_screen
        sub.screen_y = self.camera.screen_y
        sub.wx = self.camera.wx
        sub.wy = self.camera.wy
        sub.target_z = self.camera.target_z
        sub.azimuth = self.camera.azimuth
        sub.elevation = self.camera.elevation
        sub.zoom = self.camera.zoom * zoom_scale
        return sub

    def _draw_single_pedestal(self, surface: pygame.Surface, cam: InspectorCamera, border_col=(140, 110, 60)):
        sx0, sy0 = cam.apply(0.0, 0.0, 0.0)
        shadow_w = max(8, int(68 * cam.zoom))
        shadow_h = max(4, int(32 * cam.zoom * (math.sin(cam.elevation) / 0.5)))
        shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 0))
        pygame.draw.ellipse(shadow_surf, (8, 10, 14, 185), (0, 0, shadow_w * 2, shadow_h * 2))
        surface.blit(shadow_surf, (sx0 - shadow_w, sy0 - shadow_h // 2))

        char_info = self.current_char_info
        is_colossal = (char_info["char_type"] == "gashadokuro")
        num_segments = 32 if is_colossal else 28
        radius = 1.65 if is_colossal else 0.70
        top_points = []
        for i in range(num_segments):
            angle = (i / num_segments) * math.pi * 2.0
            px = math.cos(angle) * radius
            py = math.sin(angle) * radius
            top_points.append(cam.apply(px, py, 0.0))

        if len(top_points) >= 3:
            pygame.draw.polygon(surface, (38, 34, 30), top_points)
            pygame.draw.polygon(surface, border_col, top_points, max(1, int(1.5 * cam.zoom)))

            inner_points = []
            for i in range(num_segments):
                angle = (i / num_segments) * math.pi * 2.0
                px = math.cos(angle) * (radius * 0.78)
                py = math.sin(angle) * (radius * 0.78)
                inner_points.append(cam.apply(px, py, 0.002))
            pygame.draw.polygon(surface, (48, 42, 36), inner_points)
            pygame.draw.polygon(surface, (85, 72, 55), inner_points, 1)

    def draw_pedestal(self, surface: pygame.Surface):
        """Desenha a plataforma circular (ou duas plataformas lado a lado no modo De/Para)."""
        if self.compare_mode and self.current_char_info["char_type"] != "gashadokuro":
            cam_l = self._make_sub_camera(-175, zoom_scale=0.88)
            cam_r = self._make_sub_camera(+115, zoom_scale=0.88)
            self._draw_single_pedestal(surface, cam_l, border_col=(135, 115, 95))
            self._draw_single_pedestal(surface, cam_r, border_col=(90, 225, 165))
        else:
            self._draw_single_pedestal(surface, self.camera)

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

    def _eval_action_frame(self, char_type: str, is_legacy: bool = False):
        """
        Calcula (wx, wy, wz, state, state_timer, is_moving, walk_timer, extra_props, ghosts)
        para a animação ativa no Model Inspector.
        """
        from src.entities import pose_scripts
        act = self.active_action
        dur = self.action_duration
        t = self.action_timer if dur > 0.0 else self.anim_time
        prog = max(0.0, min(1.0, t / max(0.001, dur))) if dur > 0.0 else 0.0

        wx, wy, wz = 0.0, 0.0, 0.0
        state = "IDLE"
        state_timer = 0.0
        is_moving = False
        walk_timer = self.anim_time
        extra_props = {
            "legacy_mode": is_legacy,
            "ssaa_2x": not is_legacy,
            "pose_lerp_tracker": None if is_legacy else self._inspector_lerp_tracker,
        }

        if act == "IDLE":
            state = "IDLE"
        elif act == "WALK":
            state = "WALK"
            is_moving = True
            walk_timer = self.anim_time * 2.6
        elif act == "ATTACK":
            state = "ATTACK"
            state_timer = 0.08 + (math.sin(self.anim_time * 4.0) * 0.5 + 0.5) * 0.12
        elif act == "RECOVERY":
            state = "RECOVERY"
            state_timer = 0.35
            if not is_legacy and char_type == "kenshin":
                extra_props["pose"] = "noto_sheath"
                extra_props["noto_prog"] = (self.anim_time * 1.4) % 1.0
        elif act == "IAI_SLICE":
            # 2.1.1: Startup Koiguchi-kiri (0..0.22) -> Dash Iai (0.22..0.55) -> Noto caminhando (0.55..1.0)
            if is_legacy:
                state = "ATTACK"
                state_timer = max(0.01, (1.0 - min(1.0, prog * 1.4)) * 0.16)
            else:
                if prog < 0.22:
                    state = "ATTACK"
                    state_timer = 0.14
                    extra_props["pose"] = "koiguchi_glint"
                elif prog < 0.56:
                    u = (prog - 0.22) / 0.34
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - u) * 0.14)
                    wx = (u - 0.5) * 0.38
                    wy = (u - 0.5) * 0.38
                else:
                    u = (prog - 0.56) / 0.44
                    state = "RECOVERY"
                    state_timer = max(0.01, (1.0 - u) * 0.45)
                    extra_props["pose"] = "noto_sheath"
                    extra_props["noto_prog"] = u
                    is_moving = True
                    walk_timer = self.anim_time * 1.6
        elif act == "RYUU_TSUI_SEN":
            # 2.1.2: ASCEND com Zanzou (0..0.28) -> APEX duas mãos (0.28..0.52) -> DESCEND meteórico (0.52..1.0)
            if is_legacy:
                state = "ATTACK"
                wz = max(0.0, 0.95 * (1.0 - prog))
                state_timer = max(0.01, (1.0 - prog) * 0.16)
            else:
                state = "RYUU_TSUI_SEN"
                if prog < 0.28:
                    u = prog / 0.28
                    extra_props["ryuu_phase"] = "ASCEND"
                    wz = 0.15 + 0.85 * (1.0 - (1.0 - u) ** 2)
                elif prog < 0.52:
                    extra_props["ryuu_phase"] = "APEX"
                    wz = 1.00
                else:
                    u = (prog - 0.52) / 0.48
                    extra_props["ryuu_phase"] = "DESCEND"
                    wz = max(0.0, 1.00 * (1.0 - min(1.0, u * 1.35) ** 2))
        elif act == "SHUKUCHI":
            state = "SHUKUCHI" if not is_legacy else "IDLE"
            shift = math.sin(prog * math.pi) * 0.34
            wx, wy = shift, shift
        elif act == "SHUKUCHI_CANCEL":
            # 2.1.3: Shukuchi (0..0.38) -> Cancelamento nos últimos 40% direto para Iai Slice!
            if prog < 0.38:
                u = prog / 0.38
                state = "SHUKUCHI"
                wx, wy = -0.25 + 0.25 * u, -0.25 + 0.25 * u
            elif prog < 0.50 and not is_legacy:
                state = "ATTACK"
                extra_props["pose"] = "koiguchi_glint"
            else:
                u = (prog - 0.50) / 0.50
                state = "ATTACK"
                state_timer = max(0.01, (1.0 - u) * 0.14)
                wx, wy = 0.22 * u, 0.22 * u
        elif act == "PARRY_GROUND":
            # 2.1.1: Salto parabático para trás + Noto andando ao pousar
            if prog < 0.52:
                u = prog / 0.52
                state = "PARRY_BACKHOP"
                wz = math.sin(u * math.pi) * 0.48
                wx, wy = -0.26 * u, -0.26 * u
            else:
                u = (prog - 0.52) / 0.48
                state = "RECOVERY"
                wx, wy = -0.26 + 0.14 * u, -0.26 + 0.14 * u
                is_moving = True
                walk_timer = self.anim_time * 1.6
                if not is_legacy:
                    extra_props["pose"] = "noto_sheath"
                    extra_props["noto_prog"] = u
        elif act == "PARRY_AERIAL":
            # 2.1.2: Mortal 360° para trás no ar
            if prog < 0.65:
                u = prog / 0.65
                state = "PARRY_BACKHOP"
                wz = math.sin(u * math.pi) * 0.95
                wx, wy = -0.32 * u, -0.32 * u
                if not is_legacy:
                    extra_props["is_aerial_parry"] = True
                    extra_props["somersault_angle"] = u * 360.0
            else:
                u = (prog - 0.65) / 0.35
                state = "RECOVERY"
                wx, wy = -0.32, -0.32
                if not is_legacy:
                    extra_props["pose"] = "noto_sheath"
                    extra_props["noto_prog"] = u
        elif act == "TSUPPARI_1":
            # Golpe 1: Harite (palma pesada de direita)
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            if not is_legacy:
                extra_props["tsuppari_hit"] = 1
                wx = 0.08 * math.sin(prog * math.pi)
                wy = 0.08 * math.sin(prog * math.pi)
        elif act == "TSUPPARI_2":
            # Golpe 2: Morote-Tsuppari (dupla palma sônica frontal, quebra guarda)
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            if not is_legacy:
                extra_props["tsuppari_hit"] = 2
                wx = 0.14 * math.sin(prog * math.pi)
                wy = 0.14 * math.sin(prog * math.pi)
        elif act == "TACHIAI_TACKLE":
            # Investida autêntica de 3 fases: Startup agachado -> Aceleração contínua -> Impacto
            if is_legacy:
                state = "IDLE"
                wx = -0.30 + 0.60 * prog
                wy = -0.30 + 0.60 * prog
            else:
                if prog < 0.25:
                    state = "TACHIAI_TACKLE"
                    extra_props["pose"] = "tachiai_crouch"
                    extra_props["tachiai_phase"] = "STARTUP"
                elif prog < 0.85:
                    u = (prog - 0.25) / 0.60
                    state = "TACHIAI_TACKLE"
                    extra_props["pose"] = "tackle"
                    extra_props["tachiai_phase"] = "DASH"
                    shift = (u ** 1.6) * 0.85 - 0.42
                    wx, wy = shift, shift
                else:
                    state = "RECOVERY"
                    state_timer = 0.20
                    wx, wy = 0.43, 0.43
        elif act == "SHIKO_SLIP":
            # Esquiva Shiko Slip-Step (Suriashi no solo com joelhos flexionados)
            state = "DODGE"
            if not is_legacy:
                extra_props["pose"] = "shiko_slip"
                shift = math.sin(prog * math.pi) * 0.42
                wx, wy = shift, shift
            else:
                wx = math.sin(prog * math.pi) * 0.25
                wy = math.sin(prog * math.pi) * 0.25
        elif act == "GASSHO_PARRY":
            # Bloqueio de ferro Gassho-hineri (antebraços maciços cruzados)
            if is_legacy:
                state = "PARRY_BACKHOP"
                wx, wy = -0.15 * prog, -0.15 * prog
            else:
                state = "PARRY"
                extra_props["pose"] = "gassho_parry"
        elif act == "HATAKI_KOMI":
            # Contra-ataque Hataki-komi (empurrão descendente esmagador)
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            if not is_legacy:
                extra_props["pose"] = "hataki_komi"
                wx = 0.12 * math.sin(prog * math.pi)
                wy = 0.12 * math.sin(prog * math.pi)
        elif act == "ATTACK_1":
            state = "ATTACK"
            extra_props["combo_step"] = 1
            if char_type == "ninja":
                extra_props["pose"] = "reverse_slash"
                state_timer = max(0.01, (1.0 - prog) * 0.16)
                wx = 0.08 * math.sin(prog * math.pi)
                wy = 0.08 * math.sin(prog * math.pi)
            else:
                # Musashi Golpe 1: Katana descendente
                state_timer = max(0.01, (1.0 - prog) * 0.18)
                wx = 0.10 * math.sin(prog * math.pi)
                wy = 0.10 * math.sin(prog * math.pi)
        elif act == "ATTACK_2":
            state = "ATTACK"
            extra_props["combo_step"] = 2
            if char_type == "ninja":
                extra_props["pose"] = "thrust_lunge"
                state_timer = max(0.01, (1.0 - prog) * 0.18)
                wx = 0.22 * math.sin(prog * math.pi)
                wy = 0.22 * math.sin(prog * math.pi)
            else:
                # Musashi Golpe 2: Wakizashi ascendente
                state_timer = max(0.01, (1.0 - prog) * 0.18)
                wx = 0.15 * math.sin(prog * math.pi)
                wy = 0.15 * math.sin(prog * math.pi)
        elif act == "KUNAI_SNIPE":
            # Hanzo Secundário Solo: Kunai Snipe veloz
            state = "RECOVERY"
            extra_props["has_kunai"] = False
            state_timer = max(0.01, (1.0 - prog) * 0.12)
        elif act == "KUNAI_AERIAL":
            # Hanzo Secundário Aéreo: Salto com mergulho de Kunai
            state = "JUMP"
            wz = math.sin(prog * math.pi) * 1.35
            extra_props["has_kunai"] = (prog < 0.40)
            wx = 0.35 * prog
            wy = 0.35 * prog
        elif act == "SHINOBI_JUMP":
            # Hanzo Salto Ninja Acrobático Parabólico
            state = "JUMP"
            wz = math.sin(prog * math.pi) * 1.35
            wx = 0.42 * prog
            wy = 0.42 * prog
        elif act == "JUMP_CANCEL":
            # Hanzo Cancelamento de Aterrissagem (Landing Strike Lunge)
            if prog < 0.45:
                state = "JUMP"
                wz = (1.0 - (prog / 0.45)) * 0.50
                wx = 0.25 * (prog / 0.45)
                wy = 0.25 * (prog / 0.45)
            else:
                u = (prog - 0.45) / 0.55
                state = "ATTACK"
                wz = 0.0
                extra_props["combo_step"] = 2
                extra_props["is_landing_cancel"] = True
                extra_props["pose"] = "thrust_lunge"
                state_timer = max(0.01, (1.0 - u) * 0.18)
                wx = 0.25 + 0.32 * u
                wy = 0.25 + 0.32 * u
        elif act == "PARRY_RECOIL":
            # Hanzo Queda Imediata ao Sofrer Parry (Anti-Floating)
            state = "STUNNED"
            wz = 0.0
            state_timer = max(0.01, (1.0 - prog) * 0.60)
            wx = -0.15 * math.sin(prog * math.pi)
            wy = -0.15 * math.sin(prog * math.pi)
        elif act == "ATTACK_3":
            # Musashi Golpe 3: Clivagem em X com lunge e onda
            state = "ATTACK"
            extra_props["combo_step"] = 3
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            wx = 0.32 * math.sin(prog * math.pi)
            wy = 0.32 * math.sin(prog * math.pi)
        elif act == "CROSS_GUARD":
            # Musashi Postura Cross Guard Parry
            state = "PARRY"
            extra_props["pose"] = "cross_guard"
        elif act == "CROSS_SHOCKWAVE":
            # Musashi Contra-Ataque Cross Shockwave
            state = "CROSS_SHOCKWAVE"
            extra_props["pose"] = "cross_shockwave"
            extra_props["cross_shockwave"] = True
            state_timer = max(0.01, (1.0 - prog) * 0.24)
            wx = 0.18 * math.sin(prog * math.pi)
            wy = 0.18 * math.sin(prog * math.pi)
        elif act == "TACTICAL_ROLL":
            # Musashi Rolamento Tático (sem zanzou, sem duplicação)
            state = "ROLL"
            extra_props["is_roll"] = True
            extra_props["pose"] = "tactical_roll"
            wx = 0.45 * prog
            wy = 0.45 * prog
        elif act == "ROLL_CANCEL":
            # Cancelamento ofensivo aos 40% em lunge de ataque
            if prog < 0.40:
                state = "ROLL"
                extra_props["is_roll"] = True
                extra_props["pose"] = "tactical_roll"
                wx = 0.35 * (prog / 0.40)
                wy = 0.35 * (prog / 0.40)
            else:
                state = "ATTACK"
                extra_props["combo_step"] = 1
                state_timer = max(0.01, (1.0 - (prog - 0.40) / 0.60) * 0.18)
                wx = 0.35 + 0.25 * ((prog - 0.40) / 0.60)
                wy = 0.35 + 0.25 * ((prog - 0.40) / 0.60)
        elif act == "SHURIKEN":
            # Joe Arremesso de Shuriken Rápido (15.5 m/s)
            state = "RECOVERY"
            state_timer = max(0.01, (1.0 - prog) * 0.12)
            extra_props["pose"] = "shuriken_throw"
            extra_props["progress"] = prog
        elif act == "FLIC_FLAC":
            # Joe Flic-Flac Acrobático para frente com cambalhota 360° (encadeável)
            state = "ROLL"
            wz = math.sin(prog * math.pi) * 0.42
            wx = 0.45 * prog
            wy = 0.45 * prog
            extra_props["pose"] = "flic_flac"
            extra_props["p"] = prog
            extra_props["somersault_angle"] = 360.0 * prog
        elif act == "GATOTSU_ISHIKI":
            state = "GATOTSU_CHARGE"
            extra_props["pose"] = "gatotsu_lunge"
            extra_props["gatotsu_lunge"] = True
            extra_props["p"] = prog
            wx = 0.55 * prog
            wy = 0.55 * prog
        elif act == "GATOTSU_ZEROSHIKI":
            state = "ZEROSHIKI"
            extra_props["pose"] = "zeroshiki_blast"
            extra_props["zeroshiki_blast"] = True
            extra_props["p"] = prog
            wx = 0.15 * math.sin(prog * math.pi)
            wy = 0.15 * math.sin(prog * math.pi)
        elif act == "HAORI_SIDESTEP":
            state = "ROLL"
            extra_props["pose"] = "haori_sidestep"
            extra_props["haori_sidestep"] = True
            extra_props["p"] = prog
            wx = 0.30 * math.sin(prog * math.pi)
            wy = -0.30 * math.sin(prog * math.pi)
        elif act == "GATOTSU_CANCEL":
            if prog < 0.50:
                state = "GATOTSU_CHARGE"
                extra_props["pose"] = "gatotsu_lunge"
                extra_props["gatotsu_lunge"] = True
                extra_props["p"] = prog / 0.50
                wx = 0.30 * (prog / 0.50)
                wy = 0.30 * (prog / 0.50)
            else:
                u = (prog - 0.50) / 0.50
                state = "ROLL"
                extra_props["pose"] = "haori_sidestep"
                extra_props["haori_sidestep"] = True
                extra_props["p"] = u
                wx = 0.30 + 0.20 * math.sin(u * math.pi)
                wy = 0.30 - 0.30 * math.sin(u * math.pi)
        elif act == "PARRY_RECOIL":
            state = "PARRIED_STAGGER"
            wx = -0.22 * math.sin(prog * math.pi)
            wy = -0.22 * math.sin(prog * math.pi)
        elif act == "YAMATO_CHARGE":
            # Joe Comando com Assobio e Yamato
            state = "RECOVERY"
            state_timer = max(0.01, (1.0 - prog) * 0.15)
            extra_props["pose"] = "dog_whistle"
            extra_props["progress"] = prog
        elif act == "PRIMARY_SHOT":
            # Teppo Disparo de Arcabuz (Mira + Tiro com Recuo)
            if prog < 0.35:
                state = "RIFLE_AIM"
                extra_props["pose"] = "ready_aim"
                extra_props["p"] = prog / 0.35
            else:
                state = "ATTACK"
                u = (prog - 0.35) / 0.65
                state_timer = max(0.01, (1.0 - u) * 0.22)
                extra_props["pose"] = "aim_shoot"
                extra_props["p"] = u
                wx = -0.08 * math.sin(u * math.pi)
                wy = -0.08 * math.sin(u * math.pi)
        elif act == "RIFLE_BUTT":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["pose"] = "rifle_butt"
            extra_props["is_rifle_butt"] = True
            extra_props["p"] = prog
            wx = 0.20 * math.sin(prog * math.pi)
            wy = 0.20 * math.sin(prog * math.pi)
        elif act == "RAMROD_RELOAD":
            state = "IDLE"
            extra_props["pose"] = "ramrod_reload"
            extra_props["is_reloading"] = True
            extra_props["p"] = prog
        elif act == "POWDER_TRAP":
            state = "IDLE"
            extra_props["pose"] = "plant_trap"
            extra_props["is_planting_trap"] = True
            extra_props["p"] = prog
            wz = -0.06 * math.sin(prog * math.pi)
        elif act == "TRENCH_DIVE":
            state = "RIFLE_ROLL"
            extra_props["pose"] = "trench_dive"
            extra_props["p"] = prog
            extra_props["roll_prog"] = prog
            extra_props["somersault_angle"] = -360.0 * prog
            extra_props["somersault_pivot_z"] = wz + 0.24
            extra_props["is_roll"] = True
            wz = max(0.0, wz - 0.14 * math.sin(prog * math.pi))
            wx = 0.50 * prog
            wy = 0.50 * prog
        elif act == "PARRY_DEFENSE":
            state = "PARRY"
            extra_props["pose"] = "ready_aim"
            wx = -0.12 * math.sin(prog * math.pi)
            wy = -0.12 * math.sin(prog * math.pi)
        elif act == "KAMA_STRIKE":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["pose"] = "kama_strike"
            extra_props["p"] = prog
            wx = 0.18 * math.sin(prog * math.pi)
            wy = 0.18 * math.sin(prog * math.pi)
        elif act == "CHAIN_DRAG":
            state = "CHAIN_PULL"
            extra_props["pose"] = "chain_drag"
            extra_props["p"] = prog
        elif act == "BACKFLIP":
            state = "ROLL"
            extra_props["pose"] = "chain_whirl_backflip"
            extra_props["p"] = prog
            extra_props["roll_prog"] = prog
            extra_props["somersault_angle"] = 360.0 * prog
            extra_props["somersault_pivot_z"] = wz + 0.30
            extra_props["is_roll"] = True
            wz = math.sin(prog * math.pi) * 0.40
            wx = -0.40 * prog
            wy = -0.40 * prog
        elif act == "TANTO_SLASH":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.14)
            extra_props["pose"] = "tanto_slash"
            extra_props["p"] = prog
            wx = 0.20 * math.sin(prog * math.pi)
            wy = 0.20 * math.sin(prog * math.pi)
        elif act == "HOROKU_BOMB":
            state = "RECOVERY"
            extra_props["pose"] = "bomb_throw"
            extra_props["p"] = prog
            wx = 0.10 * math.sin(prog * math.pi)
            wy = 0.10 * math.sin(prog * math.pi)
        elif act == "REMOTE_MINE":
            state = "RECOVERY"
            extra_props["pose"] = "plant_mine"
            extra_props["p"] = prog
            wz = -0.10 * math.sin(prog * math.pi)
        elif act == "SMOKE_ROLL":
            state = "ROLL"
            extra_props["pose"] = "smoke_roll"
            extra_props["p"] = prog
            extra_props["roll_prog"] = prog
            extra_props["somersault_angle"] = 360.0 * prog
            extra_props["somersault_pivot_z"] = wz + 0.25
            extra_props["is_roll"] = True
            wx = 0.35 * prog
            wy = 0.35 * prog
        elif act == "FAN_STRIKE":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.14)
            extra_props["pose"] = "fan_strike"
            extra_props["p"] = prog
            wx = 0.20 * math.sin(prog * math.pi)
            wy = 0.20 * math.sin(prog * math.pi)
        elif act == "DOKUKIRI":
            state = "DOKUKIRI"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["pose"] = "dokukiri_breath"
            extra_props["p"] = prog
            wx = 0.08 * math.sin(prog * math.pi)
            wy = 0.08 * math.sin(prog * math.pi)
        elif act == "KAWARIMI_FEINT":
            state = "ROLL"
            extra_props["pose"] = "kawarimi_feint"
            extra_props["p"] = prog
            extra_props["roll_prog"] = prog
            extra_props["is_roll"] = True
            wx = 0.30 * prog
            wy = 0.30 * prog
        elif act == "CUTLASS_CLEAVE":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["pose"] = "cutlass_cleave"
            extra_props["p"] = prog
            wx = 0.35 * prog
            wy = 0.35 * prog
        elif act == "CANNON_STRIKE":
            state = "ATTACK"
            extra_props["pose"] = "cannon_strike"
            extra_props["p"] = prog
            extra_props["is_aiming_cannon"] = True
        elif act == "SWASHBUCKLE_DASH":
            state = "ROLL"
            extra_props["pose"] = "swashbuckle_dash"
            extra_props["p"] = prog
            extra_props["roll_prog"] = prog
            extra_props["is_roll"] = True
            wx = 0.40 * prog
            wy = 0.40 * prog
        elif act == "FLECHE_THRUST":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["pose"] = "fleche_thrust"
            extra_props["p"] = prog
            wx = 0.45 * prog
            wy = 0.45 * prog
        elif act == "FLINTLOCK_SHOT":
            state = "ATTACK"
            extra_props["pose"] = "flintlock"
            extra_props["p"] = prog
            wx = -0.10 * math.sin(prog * math.pi)
        elif act == "CAPE_FLOURISH":
            state = "CAPE_FLOURISH"
            extra_props["pose"] = "cape_flourish"
            extra_props["p"] = prog
        elif act == "CAPE_SWIRL_BACKHOP":
            state = "ROLL"
            extra_props["pose"] = "cape_swirl_backhop"
            extra_props["p"] = prog
            extra_props["roll_prog"] = prog
            extra_props["is_roll"] = True
            wz = math.sin(prog * math.pi) * 0.25
            wx = -0.35 * prog
            wy = -0.35 * prog
        elif act == "QUICK_SNIPE":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["pose"] = "quick_snipe"
            extra_props["p"] = prog
            extra_props["is_drawing"] = True
            wx = -0.06 * math.sin(prog * math.pi)
            wy = -0.06 * math.sin(prog * math.pi)
        elif act == "SACRED_VOLLEY":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["pose"] = "sacred_volley"
            extra_props["p"] = prog
            extra_props["is_aiming_volley"] = True
            extra_props["is_drawing"] = True
            wz = 0.05 * math.sin(prog * math.pi)
        elif act == "ROPE_ARROW":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["pose"] = "rope_arrow"
            extra_props["p"] = prog
            extra_props["is_charging_rope"] = True
            wx = 0.20 * prog
            wy = 0.20 * prog
        elif act == "MIKO_ROLL":
            state = "ROLL"
            extra_props["pose"] = "miko_roll"
            extra_props["p"] = prog
            extra_props["roll_prog"] = prog
            extra_props["somersault_angle"] = 360.0 * prog
            extra_props["somersault_pivot_z"] = wz + 0.28
            extra_props["is_roll"] = True
            wx = 0.35 * prog
            wy = 0.35 * prog
        elif act == "JAB_STRIKE":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.14)
            extra_props["combo_step"] = 1
            extra_props["pose"] = "combo_step_1_jab"
            extra_props["p"] = prog
            wx = 0.18 * math.sin(prog * math.pi)
            wy = 0.18 * math.sin(prog * math.pi)
        elif act == "COMBO_STRIKES":
            state = "ATTACK"
            if prog < 0.48:
                u = prog / 0.48
                state_timer = max(0.01, (1.0 - u) * 0.16)
                extra_props["combo_step"] = 2
                extra_props["pose"] = "combo_step_2_palm"
                extra_props["p"] = u
                wx = 0.22 * math.sin(u * math.pi)
                wy = 0.22 * math.sin(u * math.pi)
            else:
                u = (prog - 0.48) / 0.52
                state_timer = max(0.01, (1.0 - u) * 0.24)
                extra_props["combo_step"] = 3
                extra_props["pose"] = "combo_step_3_dragon_kick"
                extra_props["p"] = u
                wx = 0.35 * math.sin(u * math.pi)
                wy = 0.35 * math.sin(u * math.pi)
        elif act == "KIAI_SHOUT":
            state = "KIAI_SHOUT"
            state_timer = max(0.01, (1.0 - prog) * 0.35)
            extra_props["pose"] = "kiai_roar"
            extra_props["p"] = prog
            extra_props["seg_u"] = prog
        elif act == "SHAOLIN_ROLL":
            state = "ROLL"
            extra_props["pose"] = "shaolin_roll"
            extra_props["p"] = prog
            extra_props["roll_prog"] = prog
            extra_props["somersault_angle"] = 360.0 * prog
            extra_props["somersault_pivot_z"] = wz + 0.28
            extra_props["is_roll"] = True
            wx = 0.38 * prog
            wy = 0.38 * prog
        elif act == "PARRY_REACTION":
            state = "PARRY"
            if char_type in ("okuni", "kabuki"):
                extra_props["pose"] = "tessen_cross_guard"
            elif char_type in ("tomoe", "archer"):
                extra_props["pose"] = "parry_reaction"
            elif char_type in ("ren", "shaolin"):
                extra_props["pose"] = "iron_palm_parry"
            elif char_type in ("chiyo", "nodachi"):
                extra_props["pose"] = "kodachi_x_pose"
            elif char_type in ("benkei", "sohei"):
                extra_props["pose"] = "iron_guard_reaction"
            elif char_type in ("orin", "minstrel"):
                extra_props["pose"] = "parry_reaction"
            elif char_type in ("goro", "farmer"):
                extra_props["pose"] = "iron_guard"
            elif char_type in ("anne", "pirate", "julie", "musketeer"):
                extra_props["pose"] = "en_garde"
            else:
                extra_props["pose"] = "tanto_slash"
            extra_props["p"] = 0.15
            wx = -0.08 * math.sin(prog * math.pi)
            wy = -0.08 * math.sin(prog * math.pi)
        elif act == "DODGE_CANCEL":
            if char_type in ("okuni", "kabuki"):
                if prog < 0.45:
                    u = prog / 0.45
                    state = "ROLL"
                    extra_props["pose"] = "kawarimi_feint"
                    extra_props["p"] = u
                    extra_props["roll_prog"] = u
                    extra_props["is_roll"] = True
                    wx = 0.25 * u
                    wy = 0.25 * u
                else:
                    u = (prog - 0.45) / 0.55
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - u) * 0.14)
                    extra_props["pose"] = "fan_strike"
                    extra_props["p"] = u
                    wx = 0.25 + 0.15 * u
                    wy = 0.25 + 0.15 * u
            elif char_type in ("kasumi", "gray"):
                if prog < 0.45:
                    u = prog / 0.45
                    state = "ROLL"
                    extra_props["pose"] = "smoke_roll"
                    extra_props["p"] = u
                    extra_props["roll_prog"] = u
                    extra_props["somersault_angle"] = 360.0 * u
                    extra_props["somersault_pivot_z"] = wz + 0.25
                    extra_props["is_roll"] = True
                    wx = 0.25 * u
                    wy = 0.25 * u
                else:
                    u = (prog - 0.45) / 0.55
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - u) * 0.14)
                    extra_props["pose"] = "tanto_slash"
                    extra_props["p"] = u
                    wx = 0.25 + 0.15 * u
                    wy = 0.25 + 0.15 * u
            elif char_type in ("anne", "pirate"):
                if prog < 0.45:
                    u = prog / 0.45
                    state = "ROLL"
                    extra_props["pose"] = "swashbuckle_dash"
                    extra_props["p"] = u
                    extra_props["roll_prog"] = u
                    extra_props["is_roll"] = True
                    wx = 0.30 * u
                    wy = 0.30 * u
                else:
                    u = (prog - 0.45) / 0.55
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - u) * 0.22)
                    extra_props["pose"] = "cutlass_cleave"
                    extra_props["p"] = u
                    wx = 0.30 + 0.25 * u
                    wy = 0.30 + 0.25 * u
            elif char_type in ("julie", "musketeer"):
                if prog < 0.45:
                    u = prog / 0.45
                    state = "ROLL"
                    extra_props["pose"] = "cape_swirl_backhop"
                    extra_props["p"] = u
                    extra_props["roll_prog"] = u
                    extra_props["is_roll"] = True
                    wz = math.sin(u * math.pi) * 0.20
                    wx = -0.25 * u
                    wy = -0.25 * u
                else:
                    u = (prog - 0.45) / 0.55
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - u) * 0.20)
                    extra_props["pose"] = "fleche_thrust"
                    extra_props["p"] = u
                    wx = -0.25 + 0.45 * u
                    wy = -0.25 + 0.45 * u
            elif char_type in ("tomoe", "archer"):
                if prog < 0.45:
                    u = prog / 0.45
                    state = "ROLL"
                    extra_props["pose"] = "miko_roll"
                    extra_props["p"] = u
                    extra_props["roll_prog"] = u
                    extra_props["somersault_angle"] = 360.0 * u
                    extra_props["somersault_pivot_z"] = wz + 0.28
                    extra_props["is_roll"] = True
                    wx = 0.25 * u
                    wy = 0.25 * u
                else:
                    u = (prog - 0.45) / 0.55
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - u) * 0.20)
                    extra_props["pose"] = "quick_snipe"
                    extra_props["p"] = u
                    extra_props["is_drawing"] = True
                    wx = 0.25 + 0.10 * u
                    wy = 0.25 + 0.10 * u
            elif char_type in ("ren", "shaolin"):
                if prog < 0.45:
                    u = prog / 0.45
                    state = "ROLL"
                    extra_props["pose"] = "shaolin_roll"
                    extra_props["p"] = u
                    extra_props["roll_prog"] = u
                    extra_props["somersault_angle"] = 360.0 * u
                    extra_props["somersault_pivot_z"] = wz + 0.28
                    extra_props["is_roll"] = True
                    wx = 0.25 * u
                    wy = 0.25 * u
                else:
                    u = (prog - 0.45) / 0.55
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - u) * 0.14)
                    extra_props["combo_step"] = 1
                    extra_props["pose"] = "combo_step_1_jab"
                    extra_props["p"] = u
                    wx = 0.25 + 0.15 * u
                    wy = 0.25 + 0.15 * u
            elif char_type in ("chiyo", "nodachi"):
                if prog < 0.45:
                    u = prog / 0.45
                    state = "ROLL"
                    extra_props["pose"] = "shadow_step"
                    extra_props["p"] = u
                    extra_props["roll_prog"] = u
                    extra_props["is_roll"] = True
                    wx = 0.25 * u
                    wy = 0.25 * u
                else:
                    u = (prog - 0.45) / 0.55
                    state = "MAI_DANCE"
                    state_timer = max(0.01, (1.0 - u) * 0.20)
                    extra_props["pose"] = "mai_dance"
                    extra_props["p"] = u
                    wx = 0.25 + 0.15 * u
                    wy = 0.25 + 0.15 * u
            else:
                if prog < 0.45:
                    u = prog / 0.45
                    state = "ROLL"
                    extra_props["pose"] = "chain_whirl_backflip"
                    extra_props["p"] = u
                    extra_props["roll_prog"] = u
                    extra_props["somersault_angle"] = 360.0 * u
                    extra_props["somersault_pivot_z"] = wz + 0.30
                    extra_props["is_roll"] = True
                    wz = math.sin(u * math.pi) * 0.35
                    wx = -0.25 * u
                    wy = -0.25 * u
                else:
                    u = (prog - 0.45) / 0.55
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - u) * 0.20)
                    extra_props["pose"] = "kama_strike"
                    extra_props["p"] = u
                    wx = -0.25 + 0.40 * u
                    wy = -0.25 + 0.40 * u
        elif act == "KODACHI_CROSS":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.14)
            extra_props["combo_step"] = 1 if prog < 0.35 else (2 if prog < 0.70 else 3)
            extra_props["p"] = (prog % 0.35) / 0.35
            wx = 0.15 * math.sin(prog * math.pi)
            wy = 0.15 * math.sin(prog * math.pi)
        elif act == "MAI_DANCE":
            state = "MAI_DANCE"
            state_timer = max(0.01, (1.0 - prog) * 0.40)
            extra_props["pose"] = "mai_dance"
            extra_props["mai_spin_angle"] = prog * math.pi * 4.0
            extra_props["p"] = prog
            wx = 0.10 * math.sin(prog * math.pi * 2.0)
            wy = 0.10 * math.cos(prog * math.pi * 2.0)
        elif act == "ACROBAT_LUNGE":
            state = "ACROBAT_LUNGE"
            state_timer = max(0.01, (1.0 - prog) * 0.32)
            extra_props["pose"] = "acrobat_lunge"
            extra_props["p"] = prog
            wz = math.sin(prog * math.pi) * 0.25
            wx = 0.45 * prog
            wy = 0.45 * prog
        elif act == "SHADOW_STEP":
            state = "ROLL"
            extra_props["pose"] = "shadow_step"
            extra_props["p"] = prog
            extra_props["roll_prog"] = prog
            extra_props["is_roll"] = True
            wx = 0.42 * prog
            wy = 0.42 * prog
        elif act == "NAGINATA_CLEAVE":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.21)
            extra_props["combo_step"] = 1
            extra_props["p"] = prog
            wx = 0.12 * math.sin(prog * math.pi)
            wy = 0.12 * math.sin(prog * math.pi)
        elif act == "NAGINATA_THRUST":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.18)
            extra_props["combo_step"] = 2
            extra_props["p"] = prog
            wx = 0.45 * prog
            wy = 0.45 * prog
        elif act == "NAGINATA_THROW":
            state = "NAGINATA_THROW"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["is_throwing"] = True
            extra_props["p"] = prog
            wx = 0.10 * math.sin(prog * math.pi)
            wy = 0.10 * math.sin(prog * math.pi)
        elif act == "TACKLE_CHARGE":
            state = "TACKLE_CHARGE"
            state_timer = max(0.01, (1.0 - prog) * 0.38)
            extra_props["has_naginata"] = False
            extra_props["is_charging"] = True
            extra_props["p"] = prog
            wx = 0.55 * prog
            wy = 0.55 * prog
        elif act == "ADAMANTINE_PUSH":
            state = "ROLL"
            extra_props["pose"] = "adamantine_push"
            extra_props["is_roll"] = True
            extra_props["roll_prog"] = prog
            extra_props["p"] = prog
            wx = 0.38 * prog
            wy = 0.38 * prog
        elif act == "SONIC_CLEAVE_1":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["combo_step"] = 1
            extra_props["p"] = prog
            wx = 0.08 * math.sin(prog * math.pi)
            wy = 0.08 * math.sin(prog * math.pi)
        elif act == "SONIC_CLEAVE_2":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["combo_step"] = 2
            extra_props["p"] = prog
            wx = 0.20 * prog
            wy = 0.20 * prog
        elif act == "RESONANCE_360":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.25)
            extra_props["is_resonance"] = True
            extra_props["p"] = prog
        elif act == "SILK_GLIDE":
            state = "ROLL"
            extra_props["pose"] = "silk_glide"
            extra_props["is_roll"] = True
            extra_props["roll_prog"] = prog
            extra_props["p"] = prog
            wx = 0.35 * prog
            wy = 0.35 * prog
        elif act == "EVASIVE_CANCEL":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.18)
            extra_props["combo_step"] = 1
            extra_props["p"] = prog
            wx = -0.15 * prog
            wy = -0.15 * prog
        elif act == "KUWA_HEAVY_CLEAVE":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["p"] = prog
            wx = 0.24 * prog
            wy = 0.24 * prog
        elif act == "EARTH_STOMP_ACTION":
            state = "EARTH_STOMP"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["is_stomp"] = True
            extra_props["pose"] = "earth_stomp"
            extra_props["p"] = prog
        elif act == "MUD_ROLL":
            state = "ROLL"
            extra_props["pose"] = "mud_roll"
            extra_props["is_mud_roll"] = True
            extra_props["roll_prog"] = prog
            extra_props["p"] = prog
            wx = 0.35 * prog
            wy = 0.35 * prog
        elif act == "POCKET_DIRT":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["pose"] = "pocket_dirt"
            extra_props["is_pocket_dirt"] = True
            extra_props["p"] = prog
            wx = 0.12 * math.sin(prog * math.pi)
            wy = 0.12 * math.sin(prog * math.pi)
        elif act == "IRON_GUARD":
            state = "PARRY"
            state_timer = max(0.01, (1.0 - prog) * 0.40)
            extra_props["pose"] = "iron_guard"
            extra_props["is_parry"] = True
            extra_props["p"] = prog
        elif act == "GYAKU_IAI_QUICKDRAW":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.16)
            extra_props["p"] = prog
            wx = 0.22 * prog
            wy = 0.22 * prog
        elif act == "LISTEN_STANCE":
            state = "LISTEN"
            state_timer = max(0.01, (1.0 - prog) * 0.40)
            extra_props["is_listen"] = True
            extra_props["pose"] = "listen_stance"
            extra_props["p"] = prog
        elif act == "BLIND_COUNTER_THRUST":
            state = "COUNTER_THRUST"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["is_pierce"] = True
            extra_props["pose"] = "counter_thrust"
            extra_props["p"] = prog
            wx = 0.32 * prog
            wy = 0.32 * prog
        elif act == "CANE_TAP_SLIP":
            state = "ROLL"
            state_timer = max(0.01, (1.0 - prog) * 0.28)
            extra_props["is_roll"] = True
            extra_props["pose"] = "cane_slip"
            extra_props["roll_prog"] = prog
            extra_props["p"] = prog
            wx = 0.40 * prog
            wy = 0.40 * prog
        elif act in ("SHEATH_PARRY", "PARRY_REACTION"):
            state = "PARRY"
            state_timer = max(0.01, (1.0 - prog) * 0.36)
            extra_props["is_parry"] = True
            extra_props["pose"] = "sheath_parry"
            extra_props["p"] = prog
        elif act == "SCYTHE_REAP":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.25)
            extra_props["pose"] = "scythe_reap"
            extra_props["p"] = prog
            wx = 0.20 * math.sin(prog * math.pi)
            wy = 0.20 * math.sin(prog * math.pi)
        elif act == "SUMMON_GRASPER":
            state = "RECOVERY"
            state_timer = max(0.01, (1.0 - prog) * 0.18)
            extra_props["pose"] = "summon_grasper"
            extra_props["p"] = prog
        elif act == "SUMMON_SWORDSMAN":
            state = "RECOVERY"
            state_timer = max(0.01, (1.0 - prog) * 0.18)
            extra_props["pose"] = "summon_swordsman"
            extra_props["p"] = prog
        elif act == "SUMMON_WIGHT":
            state = "RECOVERY"
            state_timer = max(0.01, (1.0 - prog) * 0.18)
            extra_props["pose"] = "summon_wight"
            extra_props["p"] = prog
        elif act == "CORPSE_DETONATION":
            state = "RECOVERY"
            state_timer = max(0.01, (1.0 - prog) * 0.18)
            extra_props["pose"] = "corpse_detonation"
            extra_props["p"] = prog
        elif act == "MIST_DASH":
            state = "ROLL"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["is_roll"] = True
            extra_props["pose"] = "mist_dash"
            extra_props["roll_prog"] = prog
            extra_props["p"] = prog
            wx = 0.40 * prog
            wy = 0.40 * prog
        elif act == "SCYTHE_GUARD":
            state = "PARRY"
            state_timer = max(0.01, (1.0 - prog) * 0.36)
            extra_props["is_parry"] = True
            extra_props["pose"] = "scythe_guard"
            extra_props["p"] = prog
        elif act == "OFUDA_TOSS":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["pose"] = "ofuda_toss"
            extra_props["p"] = prog
            extra_props["talisman_flying"] = True
            wx = 0.15 * math.sin(prog * math.pi)
            wy = 0.15 * math.sin(prog * math.pi)
        elif act == "SACRED_WARD":
            state = "RECOVERY"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["pose"] = "sacred_ward"
            extra_props["p"] = prog
        elif act == "SHIKIGAMI_GLIDE":
            state = "ROLL"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["is_roll"] = True
            extra_props["pose"] = "shikigami_glide"
            extra_props["roll_prog"] = prog
            extra_props["p"] = prog
            wx = 0.40 * prog
            wy = 0.40 * prog
        elif act == "ASTRAL_GUARD":
            state = "PARRY"
            state_timer = max(0.01, (1.0 - prog) * 0.36)
            extra_props["is_parry"] = True
            extra_props["pose"] = "astral_guard"
            extra_props["p"] = prog
        elif act in ("FATAL_FIRE", "FATAL_WATER", "FATAL_WOOD", "FATAL_METAL", "FATAL_EARTH", "FATAL_YINYANG"):
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.25)
            elem_map = {
                "FATAL_FIRE": "fire", "FATAL_WATER": "water", "FATAL_WOOD": "wood",
                "FATAL_METAL": "metal", "FATAL_EARTH": "earth", "FATAL_YINYANG": "yinyang"
            }
            elem = elem_map.get(act, "fire")
            extra_props["pose"] = f"finisher_{elem}"
            extra_props["current_element"] = elem
            extra_props["p"] = prog
            wx = 0.20 * math.sin(prog * math.pi)
            wy = 0.20 * math.sin(prog * math.pi)
        elif act == "BO_STRIKE":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["pose"] = "bo_strike"
            extra_props["p"] = prog
            wx = 0.20 * math.sin(prog * math.pi)
            wy = 0.20 * math.sin(prog * math.pi)
        elif act == "POLE_VAULT":
            state = "POLE_VAULT"
            state_timer = max(0.01, (1.0 - prog) * 0.45)
            extra_props["pose"] = "pole_vault"
            extra_props["p"] = prog
            extra_props["pole_vault_prog"] = prog
            wz = math.sin(prog * math.pi) * 2.2
            wx = 0.40 * prog
            wy = 0.40 * prog
        elif act == "STAFF_HOP":
            state = "STAFF_HOP"
            state_timer = max(0.01, (1.0 - prog) * 0.32)
            extra_props["pose"] = "staff_vault_hop"
            extra_props["p"] = prog
            extra_props["staff_hop_prog"] = prog
            wz = math.sin(prog * math.pi) * 0.9
            wx = 0.35 * prog
            wy = 0.35 * prog
        elif act == "BO_SPIN_GUARD":
            state = "PARRY"
            state_timer = max(0.01, (1.0 - prog) * 0.35)
            extra_props["is_parry"] = True
            extra_props["pose"] = "bo_spin_guard"
            extra_props["p"] = prog
        elif act == "SPEAR_LUNGE":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.18)
            extra_props["pose"] = "spear_lunge"
            extra_props["p"] = prog
            wx = 0.22 * math.sin(prog * math.pi)
            wy = 0.22 * math.sin(prog * math.pi)
        elif act == "BEAR_TRAP":
            state = "RECOVERY"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["pose"] = "bear_trap_place"
            extra_props["is_trap"] = True
            extra_props["p"] = prog
            wx = -0.15 * prog
            wy = -0.15 * prog
        elif act == "HUNT_SLIDE":
            state = "ROLL"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["is_roll"] = True
            extra_props["is_slide"] = True
            extra_props["pose"] = "tundra_hunt_slide"
            extra_props["roll_prog"] = prog
            extra_props["slide_prog"] = prog
            extra_props["p"] = prog
            wx = 0.42 * prog
            wy = 0.42 * prog
        elif act == "HUNTER_GUARD":
            state = "PARRY"
            state_timer = max(0.01, (1.0 - prog) * 0.38)
            extra_props["is_parry"] = True
            extra_props["pose"] = "hunter_guard"
            extra_props["p"] = prog
        elif act == "STILETTO_THRUST":
            state = "ATTACK"
            state_timer = max(0.01, (1.0 - prog) * 0.16)
            extra_props["pose"] = "stiletto_thrust"
            extra_props["p"] = prog
            wx = 0.20 * math.sin(prog * math.pi)
            wy = 0.20 * math.sin(prog * math.pi)
        elif act == "FLASK_TOSS":
            state = "FLASK_THROW"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            extra_props["pose"] = "flask_throw"
            extra_props["p"] = prog
        elif act == "DEJIMA_SLIDE":
            state = "ROLL"
            state_timer = max(0.01, (1.0 - prog) * 0.22)
            extra_props["is_roll"] = True
            extra_props["is_slide"] = True
            extra_props["pose"] = "dejima_slide"
            extra_props["roll_prog"] = prog
            extra_props["slide_prog"] = prog
            extra_props["p"] = prog
            wx = 0.40 * prog
            wy = 0.40 * prog
        elif act == "ALCHEMIST_GUARD":
            state = "PARRY"
            state_timer = max(0.01, (1.0 - prog) * 0.36)
            extra_props["is_parry"] = True
            extra_props["pose"] = "alchemist_guard"
            extra_props["p"] = prog
        elif act == "CYCLE_REAGENT":
            state = "RECOVERY"
            state_timer = max(0.01, (1.0 - prog) * 0.20)
            reagents = ["acid", "fire", "ether", "frost", "miasma"]
            extra_props["reagent"] = reagents[int(prog * 5) % 5]
            extra_props["p"] = prog
        elif act in ("INTRO", "VICTORY"):
            kind = "intro" if act == "INTRO" else "victory"
            p_sample = prog if dur > 0.0 else ((self.anim_time * 0.42) % 1.0)
            if is_legacy and char_type in ("kenshin", "raiden", "musashi", "ninja", "american", "joe", "saitou", "teppo", "rifleman", "murasaki", "purple", "kasumi", "gray", "okuni", "kabuki", "anne", "pirate", "julie", "musketeer", "tomoe", "archer", "ren", "shaolin", "chiyo", "nodachi", "benkei", "sohei", "orin", "minstrel", "goro", "farmer", "ichi", "blind", "shikomizue", "valerius", "necromancer", "faust", "seimei", "onmyoji", "daiki", "pilgrim", "aoi", "huntress", "hendrika", "alchemist"):
                # Roteiro legado pré-Fase 2 (apenas IDLE + ATTACK simples)
                if p_sample < 0.25 or p_sample > 0.75:
                    state = "IDLE"
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - (p_sample - 0.25) / 0.50) * 0.16)
            else:
                pf = pose_scripts.sample(char_type, kind, p_sample)
                state = pf.state
                state_timer = pose_scripts.state_timer_for(char_type, pf)
                extra_props.update(pf.extra)
                extra_props["p"] = p_sample
                extra_props["intro_victory_state"] = act
                walk_timer = self.anim_time
        elif act == "FINISHER_1":
            if char_type == "raiden":
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.22)
                    extra_props["tsuppari_hit"] = 2
                    extra_props["pose"] = "finisher_morote"
                    wx, wy = 0.15 * prog, 0.15 * prog
            elif char_type == "musashi":
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.20)
                    extra_props["pose"] = "finisher_1"
                    extra_props["p"] = prog
                    wx, wy = 0.15 * prog, 0.15 * prog
            elif char_type in ("ninja", "hanzo"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "IDLE"
                    extra_props["pose"] = "finisher_1"
                    wx, wy = 0.18 * prog, 0.18 * prog
            elif char_type in ("american", "joe"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "triple_shuriken"
                    extra_props["progress"] = prog
                    wx, wy = 0.12 * prog, 0.12 * prog
            elif char_type == "saitou":
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "GATOTSU_CHARGE"
                    extra_props["pose"] = "gatotsu_lunge"
                    extra_props["gatotsu_lunge"] = True
                    extra_props["p"] = prog
                    wx, wy = 0.35 * prog, 0.35 * prog
            elif char_type in ("teppo", "rifleman"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "RIFLE_AIM" if prog < 0.40 else "ATTACK"
                    extra_props["pose"] = "finisher_headshot"
                    extra_props["p"] = prog
                    wx, wy = 0.14 * prog, 0.14 * prog
            elif char_type in ("murasaki", "purple"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_decap"
                    extra_props["p"] = prog
                    wx, wy = 0.16 * prog, 0.16 * prog
            elif char_type in ("kasumi", "gray"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_tanto"
                    extra_props["p"] = prog
                    wx, wy = 0.20 * prog, 0.20 * prog
            elif char_type in ("okuni", "kabuki"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_decap"
                    extra_props["p"] = prog
                    wx, wy = 0.18 * prog, 0.18 * prog
            elif char_type in ("anne", "pirate"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_cutlass"
                    extra_props["p"] = prog
                    wx, wy = 0.22 * prog, 0.22 * prog
            elif char_type in ("julie", "musketeer"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_a"
                    extra_props["p"] = prog
                    wx, wy = 0.24 * prog, 0.24 * prog
            elif char_type in ("tomoe", "archer"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_pinned"
                    extra_props["p"] = prog
                    wx, wy = 0.15 * prog, 0.15 * prog
            elif char_type in ("ren", "shaolin"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["hyakuretsu_phase"] = "FLURRY" if prog < 0.70 else "PAUSE"
                    extra_props["hyakuretsu_clock"] = prog * 8.0
                    extra_props["pose"] = "finisher_hyakuretsu"
                    extra_props["p"] = prog
                    wx, wy = 0.15 * prog, 0.15 * prog
            elif char_type in ("chiyo", "nodachi"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_scissor_spin"
                    extra_props["p"] = prog
                    wx, wy = 0.14 * prog, 0.14 * prog
            elif char_type in ("benkei", "sohei"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    if prog < 0.65:
                        extra_props["hoist_slam_phase"] = "HOIST"
                        extra_props["hoist_slam_prog"] = prog / 0.65
                    else:
                        extra_props["hoist_slam_phase"] = "SLAM"
                        extra_props["hoist_slam_prog"] = (prog - 0.65) / 0.35
                    extra_props["p"] = prog
                    wx = 0.12 * prog
                    wy = 0.12 * prog
            elif char_type in ("orin", "minstrel"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.20)
                    extra_props["combo_step"] = 2
                    extra_props["p"] = prog
                    wx = 0.15 * math.sin(prog * math.pi)
                    wy = 0.15 * math.sin(prog * math.pi)
            elif char_type in ("goro", "farmer"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.22)
                    extra_props["p"] = prog
                    wx = 0.22 * math.sin(prog * math.pi)
                    wy = 0.22 * math.sin(prog * math.pi)
            elif char_type in ("ichi", "blind", "shikomizue"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.16)
                    extra_props["pose"] = "gyaku_iai"
                    extra_props["p"] = prog
                    wx = 0.25 * math.sin(prog * math.pi)
                    wy = 0.25 * math.sin(prog * math.pi)
            elif char_type in ("valerius", "necromancer", "faust"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.25)
                    extra_props["pose"] = "scythe_reap"
                    extra_props["p"] = prog
                    wx = 0.24 * math.sin(prog * math.pi)
                    wy = 0.24 * math.sin(prog * math.pi)
            elif char_type in ("seimei", "onmyoji"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.25)
                    extra_props["pose"] = "finisher_fire"
                    extra_props["current_element"] = "fire"
                    extra_props["p"] = prog
                    wx = 0.20 * math.sin(prog * math.pi)
                    wy = 0.20 * math.sin(prog * math.pi)
            elif char_type in ("daiki", "pilgrim"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.25)
                    extra_props["pose"] = "finisher_throat_temple"
                    extra_props["p"] = prog
                    wx = 0.20 * math.sin(prog * math.pi)
                    wy = 0.20 * math.sin(prog * math.pi)
            elif char_type in ("aoi", "huntress"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.25)
                    extra_props["pose"] = "finisher_trap_execute"
                    extra_props["p"] = prog
                    wx = 0.28 * math.sin(prog * math.pi)
                    wy = 0.28 * math.sin(prog * math.pi)
            elif char_type in ("hendrika", "alchemist"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.25)
                    extra_props["pose"] = "finisher_carotid_vitriol"
                    extra_props["p"] = prog
                    wx = 0.25 * math.sin(prog * math.pi)
                    wy = 0.25 * math.sin(prog * math.pi)
            else:
                # 2.1.4a: Ittou Ryoudan
                state = "RECOVERY"
                wx, wy = 0.28, 0.28
                if not is_legacy:
                    extra_props["pose"] = "noto_sheath"
                    extra_props["noto_prog"] = min(1.0, prog * 1.25)
        elif act == "FINISHER_2":
            if char_type == "raiden":
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "TACHIAI_TACKLE"
                    if prog < 0.20:
                        extra_props["pose"] = "tachiai_crouch"
                        extra_props["tachiai_phase"] = "STARTUP"
                    elif prog < 0.70:
                        u = (prog - 0.20) / 0.50
                        extra_props["pose"] = "tackle"
                        extra_props["tachiai_phase"] = "DASH"
                        wx, wy = (u - 0.5) * 0.55, (u - 0.5) * 0.55
                    else:
                        extra_props["pose"] = "cataclysm_slam"
                        extra_props["tachiai_phase"] = "IMPACT"
                        wx, wy = 0.28, 0.28
            elif char_type == "musashi":
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "CROSS_SHOCKWAVE"
                    extra_props["pose"] = "finisher_2"
                    extra_props["p"] = prog
                    extra_props["cross_shockwave"] = True
                    wx, wy = 0.12 * prog, 0.12 * prog
            elif char_type in ("ninja", "hanzo"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "IDLE"
                    extra_props["pose"] = "finisher_2"
                    wz = math.sin(prog * math.pi) * 0.60
                    wx, wy = 0.22 * prog, 0.22 * prog
            elif char_type in ("american", "joe"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "fuma_throw"
                    extra_props["progress"] = prog
                    wx, wy = 0.15 * prog, 0.15 * prog
            elif char_type == "saitou":
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ZEROSHIKI"
                    extra_props["pose"] = "finisher_zeroshiki"
                    extra_props["zeroshiki_blast"] = True
                    extra_props["p"] = prog
                    wx, wy = 0.18 * prog, 0.18 * prog
            elif char_type in ("teppo", "rifleman"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "rifle_butt"
                    extra_props["finisher_style"] = "HAYAGO_KEG_BLAST"
                    extra_props["p"] = prog
                    wx = 0.22 * math.sin(prog * math.pi)
                    wy = 0.22 * math.sin(prog * math.pi)
            elif char_type in ("murasaki", "purple"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_tornado_shred"
                    extra_props["p"] = prog
                    wx, wy = 0.12 * prog, 0.12 * prog
            elif char_type in ("kasumi", "gray"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "RECOVERY"
                    extra_props["pose"] = "finisher_bomb"
                    extra_props["p"] = prog
                    wx, wy = 0.10 * prog, 0.10 * prog
            elif char_type in ("okuni", "kabuki"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "DOKUKIRI"
                    extra_props["pose"] = "finisher_melt"
                    extra_props["p"] = prog
                    wx, wy = 0.12 * prog, 0.12 * prog
            elif char_type in ("anne", "pirate"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_cannon"
                    extra_props["p"] = prog
                    wx, wy = 0.10 * prog, 0.10 * prog
            elif char_type in ("julie", "musketeer"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_b"
                    extra_props["p"] = prog
                    wx, wy = 0.12 * prog, 0.12 * prog
            elif char_type in ("tomoe", "archer"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_volley"
                    extra_props["p"] = prog
                    wx, wy = 0.12 * prog, 0.12 * prog
            elif char_type in ("ren", "shaolin"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_kiai"
                    extra_props["p"] = prog
                    wx = 0.20 * math.sin(prog * math.pi)
                    wy = 0.20 * math.sin(prog * math.pi)
            elif char_type in ("chiyo", "nodachi"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    extra_props["pose"] = "finisher_lotus_flurry"
                    extra_props["p"] = prog
                    wx = 0.15 * math.sin(prog * math.pi)
                    wy = 0.15 * math.sin(prog * math.pi)
            elif char_type in ("benkei", "sohei"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "NAGINATA_THROW"
                    extra_props["is_throwing"] = True
                    extra_props["p"] = prog
                    wx = 0.20 * math.sin(prog * math.pi)
                    wy = 0.20 * math.sin(prog * math.pi)
            elif char_type in ("orin", "minstrel"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.25)
                    extra_props["is_resonance"] = True
                    extra_props["p"] = prog
                    wx = 0.10 * math.sin(prog * math.pi)
                    wy = 0.10 * math.sin(prog * math.pi)
            elif char_type in ("goro", "farmer"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "EARTH_STOMP"
                    state_timer = max(0.01, (1.0 - prog) * 0.22)
                    extra_props["is_stomp"] = True
                    extra_props["pose"] = "earth_stomp"
                    extra_props["p"] = prog
                    wx = 0.12 * math.sin(prog * math.pi)
                    wy = 0.12 * math.sin(prog * math.pi)
            elif char_type in ("ichi", "blind", "shikomizue"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "COUNTER_THRUST"
                    state_timer = max(0.01, (1.0 - prog) * 0.20)
                    extra_props["is_pierce"] = True
                    extra_props["pose"] = "counter_thrust"
                    extra_props["p"] = prog
                    wx = 0.30 * math.sin(prog * math.pi)
                    wy = 0.30 * math.sin(prog * math.pi)
            elif char_type in ("valerius", "necromancer", "faust"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "RECOVERY"
                    state_timer = max(0.01, (1.0 - prog) * 0.35)
                    extra_props["pose"] = "corpse_detonation"
                    extra_props["p"] = prog
            elif char_type in ("seimei", "onmyoji"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.25)
                    extra_props["pose"] = "finisher_water"
                    extra_props["current_element"] = "water"
                    extra_props["p"] = prog
                    wx = 0.20 * math.sin(prog * math.pi)
                    wy = 0.20 * math.sin(prog * math.pi)
            elif char_type in ("daiki", "pilgrim"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "POLE_VAULT"
                    state_timer = max(0.01, (1.0 - prog) * 0.40)
                    extra_props["pose"] = "finisher_meteor_slam"
                    extra_props["p"] = prog
                    wz = math.sin(prog * math.pi) * 1.6
                    wx = 0.25 * prog
                    wy = 0.25 * prog
            elif char_type in ("aoi", "huntress"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.25)
                    extra_props["pose"] = "finisher_spear_toss"
                    extra_props["p"] = prog
                    wx = 0.18 * math.sin(prog * math.pi)
                    wy = 0.18 * math.sin(prog * math.pi)
            elif char_type in ("hendrika", "alchemist"):
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "ATTACK"
                    state_timer = max(0.01, (1.0 - prog) * 0.25)
                    extra_props["pose"] = "finisher_acid_dissolve"
                    extra_props["p"] = prog
                    wx = 0.15 * math.sin(prog * math.pi)
                    wy = 0.15 * math.sin(prog * math.pi)
            else:
                # 2.1.4b: Divisão Celestial de Bambu (Ápice + Queda Meteórica)
                if prog < 0.42:
                    state = "RYUU_TSUI_SEN"
                    extra_props["ryuu_phase"] = "APEX"
                    wz = 0.95
                else:
                    u = (prog - 0.42) / 0.58
                    state = "RYUU_TSUI_SEN" if u < 0.65 else "RECOVERY"
                    extra_props["ryuu_phase"] = "DESCEND"
                    wz = max(0.0, 0.95 * (1.0 - min(1.0, u * 1.65) ** 2))
                    if state == "RECOVERY" and not is_legacy:
                        extra_props["pose"] = "noto_sheath"
                        extra_props["noto_prog"] = (u - 0.65) / 0.35

        return wx, wy, wz, state, state_timer, is_moving, walk_timer, extra_props

    def _draw_single_character(self, surface: pygame.Surface, cam: InspectorCamera, is_legacy: bool = False):
        char_info = self.current_char_info
        char_type = char_info["char_type"]
        facing_x, facing_y = 1.0, 1.0

        wx, wy, wz, state, state_timer, is_moving, walk_timer, extra_props = self._eval_action_frame(char_type, is_legacy=is_legacy)

        render_voxel_humanoid(
            surface, cam,
            wx, wy, wz,
            facing_x, facing_y,
            state, state_timer,
            is_alive=True,
            char_type=char_type,
            walk_timer=walk_timer,
            alpha=255,
            is_moving=is_moving,
            extra_props=extra_props,
        )

    def draw_character(self, surface: pygame.Surface):
        """Renderiza o combatente selecionado (ou o comparativo De/Para Antigo vs Novo)."""
        char_info = self.current_char_info
        char_type = char_info["char_type"]

        if char_type == "gashadokuro":
            self.draw_boss(surface)
            return

        if self.compare_mode:
            cam_l = self._make_sub_camera(-175, zoom_scale=0.88)
            cam_r = self._make_sub_camera(+115, zoom_scale=0.88)
            self._draw_single_character(surface, cam_l, is_legacy=True)
            self._draw_single_character(surface, cam_r, is_legacy=False)

            # Linha divisória e badges De / Para acima de cada pedestal
            mid_x = (cam_l.screen_x + cam_r.screen_x) // 2
            pygame.draw.line(surface, (70, 80, 100), (mid_x, 195), (mid_x, self.height - 86), 1)

            lbl_old = self.font_body.render("ANTES (MODELO LEGADO)", True, (225, 175, 130))
            lbl_new = self.font_body.render("DEPOIS (NOVO OVERHAUL)", True, (95, 245, 175))
            surface.blit(lbl_old, (cam_l.screen_x - lbl_old.get_width() // 2, 198))
            surface.blit(lbl_new, (cam_r.screen_x - lbl_new.get_width() // 2, 198))

            notes = OVERHAUL_DE_PARA_NOTES.get(self.current_char_key, [])
            if notes:
                note_box_x, note_box_y = 258, 64
                note_box_w, note_box_h = 560, 24 + len(notes) * 16
                note_bg = pygame.Surface((note_box_w, note_box_h), pygame.SRCALPHA)
                note_bg.fill((16, 22, 28, 215))
                surface.blit(note_bg, (note_box_x, note_box_y))
                pygame.draw.rect(surface, (65, 145, 110), (note_box_x, note_box_y, note_box_w, note_box_h), 1, border_radius=5)
                hdr_n = self.font_small.render("MELHORIAS DO OVERHAUL (ESQUERDA = LEGADO  |  DIREITA = NOVO):", True, (115, 245, 180))
                surface.blit(hdr_n, (note_box_x + 10, note_box_y + 5))
                for ni, note_txt in enumerate(notes):
                    ns = self.font_small.render(f"• {note_txt}", True, (205, 235, 220))
                    surface.blit(ns, (note_box_x + 12, note_box_y + 22 + ni * 15))
        else:
            self._draw_single_character(surface, self.camera, is_legacy=False)

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

        # Botão DE / PARA (Comparativo Lado a Lado: Antigo vs Novo Overhaul)
        cmp_btn_x = cam_btn_x + cam_btn_w + 10
        cmp_btn_w = 225
        self.compare_btn_rect = pygame.Rect(cmp_btn_x, reload_btn_y, cmp_btn_w, reload_btn_h)
        is_hover_cmp = self.compare_btn_rect.collidepoint(mouse_pos)
        cmp_bg = (28, 72, 54) if self.compare_mode else ((42, 48, 62) if is_hover_cmp else (22, 28, 38))
        cmp_border = (95, 245, 175) if (self.compare_mode or is_hover_cmp) else (65, 85, 105)

        cmp_btn_surf = pygame.Surface((cmp_btn_w, reload_btn_h), pygame.SRCALPHA)
        cmp_btn_surf.fill((*cmp_bg, 238))
        surface.blit(cmp_btn_surf, (cmp_btn_x, reload_btn_y))
        pygame.draw.rect(surface, cmp_border, self.compare_btn_rect, width=2 if (self.compare_mode or is_hover_cmp) else 1, border_radius=6)

        cmp_txt_col = (120, 255, 190) if self.compare_mode else ((240, 225, 140) if is_hover_cmp else (200, 210, 225))
        cmp_label_str = "DE / PARA: ATIVO [D]" if self.compare_mode else "DE / PARA: ANTIGO vs NOVO [D]"
        cmp_label_s = self.font_body.render(cmp_label_str, True, cmp_txt_col)
        surface.blit(cmp_label_s, (cmp_btn_x + (cmp_btn_w - cmp_label_s.get_width()) // 2, reload_btn_y + 10))

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
        # 2.5 Painel Direito: Botões Interativos de Animações & Golpes
        # -------------------------------------------------------------
        anim_btns = self.get_anim_buttons()
        self.anim_action_btn_rects.clear()
        panel_w = 278
        panel_x = self.width - panel_w - 18
        panel_y = card_y + card_h + 10
        row_h = 26
        row_gap = 3
        panel_h = 34 + len(anim_btns) * (row_h + row_gap) + 6

        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((16, 18, 24, 232))
        surface.blit(panel_surf, (panel_x, panel_y))
        pygame.draw.rect(surface, (65, 75, 95), (panel_x, panel_y, panel_w, panel_h), 1, border_radius=6)

        hdr_s = self.font_body.render("ANIMAÇÕES & GOLPES (CLIQUE)", True, (240, 215, 120))
        surface.blit(hdr_s, (panel_x + 12, panel_y + 8))

        for b_idx, (act_id, act_label, _act_dur) in enumerate(anim_btns):
            by = panel_y + 30 + b_idx * (row_h + row_gap)
            b_rect = pygame.Rect(panel_x + 8, by, panel_w - 16, row_h)
            self.anim_action_btn_rects.append((act_id, b_rect))
            is_act = (self.active_action == act_id)
            is_hov = b_rect.collidepoint(mouse_pos)
            bg_c = (48, 56, 78) if is_act else ((34, 40, 56) if is_hov else (22, 26, 36))
            bd_c = info["color_accent"] if is_act else ((140, 165, 210) if is_hov else (48, 54, 68))
            pygame.draw.rect(surface, bg_c, b_rect, border_radius=4)
            pygame.draw.rect(surface, bd_c, b_rect, 2 if is_act else 1, border_radius=4)

            # Ícone de play [▶]
            play_col = (110, 245, 175) if is_act else (180, 188, 205)
            px0, py0 = b_rect.x + 8, b_rect.centery
            pygame.draw.polygon(surface, play_col, [(px0, py0 - 4), (px0, py0 + 4), (px0 + 6, py0)])

            txt_c = (255, 255, 255) if is_act else (185, 192, 208)
            lbl_surf = self.font_small.render(act_label, True, txt_c)
            surface.blit(lbl_surf, (b_rect.x + 18, b_rect.centery - lbl_surf.get_height() // 2))

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
        cam_text = f"Azimute {deg_az}° | Inclin. {deg_el}° | Zoom {self.camera.zoom:.2f}x | Foco: {self.macro_focus.upper()} | Ação: {self.active_action}"
        cam_s = self.font_body.render(cam_text, True, (240, 215, 120))
        surface.blit(cam_s, (hud_bar_x + 16, hud_bar_y + 10))

        # Controles
        ctrl_text = "Mouse: Girar (Esq) | Pan (Dir) | Zoom  ||  [D] De/Para  |  [F] Foco  |  [1-0] Golpes  |  [Espaço] Turntable"
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
                    # Verificar clique no botão De / Para
                    elif self.show_hud and self.compare_btn_rect.collidepoint(event.pos):
                        self.compare_mode = not self.compare_mode
                        clicked_btn = True
                    # Verificar clique nos botões de animação/golpe ou lista lateral
                    elif self.show_hud:
                        for act_id, a_rect in self.anim_action_btn_rects:
                            if a_rect.collidepoint(event.pos):
                                self.trigger_action(act_id)
                                clicked_btn = True
                                break
                        if not clicked_btn:
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

                # Alternar Modo Comparativo De / Para (Antigo vs Novo)
                elif event.key == pygame.K_d:
                    self.compare_mode = not self.compare_mode

                # Poses / Animações (1..9, 0, F1, F2)
                elif event.key in (pygame.K_p, pygame.K_TAB):
                    self.next_pose()
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0):
                    key_order = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
                    k_idx = key_order.index(event.key)
                    btns = self.get_anim_buttons()
                    if k_idx < len(btns):
                        self.trigger_action(btns[k_idx][0])
                elif event.key in (pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5, pygame.K_F6):
                    f_keys = [pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5, pygame.K_F6]
                    f_idx = 10 + f_keys.index(event.key)
                    btns = self.get_anim_buttons()
                    if f_idx < len(btns):
                        self.trigger_action(btns[f_idx][0])

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
        if self._inspector_lerp_tracker["blend_timer"] > 0.0:
            self._inspector_lerp_tracker["blend_timer"] = max(0.0, self._inspector_lerp_tracker["blend_timer"] - dt)
        if self.action_duration > 0.0:
            self.action_timer = (self.action_timer + dt) % self.action_duration
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
    parser.add_argument("--action", type=str, default=None, help="Ação/animação específica inicial (ex: IAI_SLICE, RYUU_TSUI_SEN)")
    parser.add_argument("--compare", action="store_true", help="Inicia no modo comparativo De / Para (Antigo vs Novo)")
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
    if args.action:
        inspector.trigger_action(args.action)
        if inspector.action_duration > 0.0:
            inspector.action_timer = inspector.action_duration * 0.45
    inspector.compare_mode = bool(args.compare)
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
