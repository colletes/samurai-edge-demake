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
}

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
}


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
        elif action_id in ("IAI_SLICE", "RYUU_TSUI_SEN", "SHUKUCHI_CANCEL", "TSUPPARI_1", "TSUPPARI_2", "HATAKI_KOMI", "ATTACK_1", "ATTACK_2", "ATTACK_3", "CROSS_SHOCKWAVE", "ROLL_CANCEL", "FINISHER_1", "FINISHER_2"):
            self.current_pose_idx = POSES.index("ATTACK")
        elif action_id in ("SHUKUCHI", "PARRY_GROUND", "PARRY_AERIAL", "TACHIAI_TACKLE", "SHIKO_SLIP", "GASSHO_PARRY", "CROSS_GUARD", "TACTICAL_ROLL"):
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
        elif act in ("INTRO", "VICTORY"):
            kind = "intro" if act == "INTRO" else "victory"
            p_sample = prog if dur > 0.0 else ((self.anim_time * 0.42) % 1.0)
            if is_legacy and char_type in ("kenshin", "raiden", "musashi"):
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
            elif char_type == "ninja":
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "IDLE"
                    extra_props["pose"] = "finisher_1"
                    wx, wy = 0.18 * prog, 0.18 * prog
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
            elif char_type == "ninja":
                if is_legacy:
                    state = "ATTACK"
                    state_timer = 0.10
                else:
                    state = "IDLE"
                    extra_props["pose"] = "finisher_2"
                    wz = math.sin(prog * math.pi) * 0.60
                    wx, wy = 0.22 * prog, 0.22 * prog
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
                elif event.key == pygame.K_F1:
                    btns = self.get_anim_buttons()
                    if len(btns) >= 11:
                        self.trigger_action(btns[10][0])
                elif event.key == pygame.K_F2:
                    btns = self.get_anim_buttons()
                    if len(btns) >= 12:
                        self.trigger_action(btns[11][0])

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
