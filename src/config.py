"""
Configurações globais e constantes para o Duelo de Samurais Isométrico.
"""
import pygame

# Resolução da Janela
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Samurai Edge Demake"

# Dimensões do Tile Isométrico (Proporção 2:1 clássica)
TILE_WIDTH = 64
TILE_HEIGHT = 32
HALF_TILE_W = TILE_WIDTH // 2   # 32
HALF_TILE_H = TILE_HEIGHT // 2  # 16

# Dimensões do Mapa (em tiles)
MAP_COLS = 22
MAP_ROWS = 22

# Paleta de Cores Japonesa Feudal
COLOR_BG = (14, 18, 16)               # Noite na floresta profunda
COLOR_GRASS = (36, 54, 32)            # Grama escura de musgo
COLOR_GRASS_LIGHT = (48, 72, 42)      # Detalhes de grama
COLOR_EARTH = (58, 46, 32)            # Caminho de terra batida
COLOR_WATER = (32, 74, 98)            # Água serena do lago
COLOR_WATER_HIGHLIGHT = (56, 114, 142)# Espuma/reflexo da água
COLOR_BRIDGE = (112, 70, 42)          # Madeira da ponte
COLOR_BRIDGE_DARK = (78, 48, 28)      # Vigas da ponte
COLOR_STONE = (88, 92, 96)            # Pedra cinza de rochas e poço
COLOR_STONE_DARK = (60, 64, 68)       # Sombra da pedra
COLOR_BAMBOO = (68, 140, 54)          # Tronco do bambu
COLOR_BAMBOO_LIGHT = (102, 188, 78)   # Nós do bambu
COLOR_BAMBOO_LEAF = (82, 162, 66)     # Folhagem do bambu
COLOR_SAKURA_PINK = (235, 150, 180)   # Pétalas de cerejeira

# Cores dos Samurais
COLOR_RED_KIMONO = (195, 32, 42)      # Carmim intenso (Kenshin)
COLOR_RED_HAIR = (210, 85, 45)        # Cabelo ruivo flamejante
COLOR_RED_HAKAMA = (220, 220, 225)    # Calça branca/cinza claro
COLOR_RED_AURA = (255, 60, 60)        # Efeito de rastro do Iai

COLOR_BLUE_KIMONO = (28, 56, 138)     # Azul meia-noite profundo
COLOR_BLUE_HAIR = (24, 24, 30)        # Cabelo preto amarrado
COLOR_BLUE_HAKAMA = (45, 52, 70)      # Hakama azul ardósia
COLOR_BLUE_AURA = (60, 140, 255)      # Efeito de corte das duas espadas

# Cores do Ninja Amarelo (Hanzo)
COLOR_YELLOW_NINJA = (240, 205, 30)   # Amarelo ninja vibrante
COLOR_YELLOW_DARK = (180, 150, 20)    # Amarelo escuro para detalhes
COLOR_NINJA_MASK = (26, 26, 30)       # Máscara e capuz preto
COLOR_YELLOW_AURA = (255, 225, 60)    # Brilho da kunai

# Cores do American Ninja & Doberman
COLOR_AMERICAN_NINJA = (38, 42, 48)   # Preto tático militar
COLOR_AMERICAN_VEST = (85, 95, 102)   # Colete cinza tático
COLOR_AMERICAN_BANDANA = (225, 45, 45)# Bandana vermelha heróica
COLOR_DOBERMAN_BLACK = (22, 22, 26)   # Pelagem preta Doberman
COLOR_DOBERMAN_RUST = (175, 90, 40)   # Manchas castanho-ferrugem
COLOR_DOBERMAN_COLLAR = (215, 35, 35) # Coleira com rebites

# Cores do Ninja Cinza (Kemuri)
COLOR_GRAY_NINJA = (80, 88, 96)       # Cinza ardósia shinobi
COLOR_GRAY_DARK = (46, 52, 58)        # Cinza escuro para máscara/colete
COLOR_SMOKE = (165, 175, 185)         # Fumaça densa
COLOR_BOMB_FUSE = (255, 140, 20)      # Pavio aceso faiscante

# Cores do Ninja Roxo (Murasaki & Kusarigama)
COLOR_PURPLE_NINJA = (150, 75, 205)   # Púrpura profundo shinobi
COLOR_PURPLE_DARK = (55, 25, 80)      # Roxo escuro para colete e máscara
COLOR_PURPLE_AURA = (195, 120, 255)   # Brilho místico da foice
COLOR_CHAIN = (175, 180, 192)         # Corrente metálica da Kusarigama

COLOR_STEEL = (220, 230, 242)         # Aço afiado da katana/kunai/shuriken
COLOR_GOLD = (235, 195, 50)           # Guarda (Tsuba) e detalhes
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BLOOD = (180, 20, 25)           # Sangue no golpe fatal

# Cores do Samurai Azul Claro (Hajime Saitou & Shinsengumi)
COLOR_SAITOU_LIGHT_BLUE = (115, 190, 220) # Asagi-iro Shinsengumi (Azul bem claro)
COLOR_SAITOU_HAORI_DARK = (75, 140, 170)  # Sombra do haori
COLOR_SAITOU_HAKAMA = (32, 35, 40)        # Hakama escuro tradicional
COLOR_SAITOU_AURA = (140, 220, 255)       # Brilho cortante da estocada Gatotsu

# Identificadores de Personagens
CHAR_KENSHIN = "kenshin"
CHAR_MUSASHI = "musashi"
CHAR_NINJA = "ninja"
CHAR_AMERICAN = "american"
CHAR_GRAY = "gray"
CHAR_PURPLE = "purple"
CHAR_SAITOU = "saitou"

# Mapeamento de Teclas Padrão
# Jogador 1 (Samurai Vermelho - Kenshin)
KEY_P1_UP = pygame.K_w
KEY_P1_DOWN = pygame.K_s
KEY_P1_LEFT = pygame.K_a
KEY_P1_RIGHT = pygame.K_d
KEY_P1_ATTACK = pygame.K_e    # Iai Flash Slash (Agora padrão Tecla E)
KEY_P1_DASH = pygame.K_r      # Esquiva / Dash (Agora padrão Tecla R)

# Jogador 2 (Samurai Azul - Musashi)
KEY_P2_UP = pygame.K_UP
KEY_P2_DOWN = pygame.K_DOWN
KEY_P2_LEFT = pygame.K_LEFT
KEY_P2_RIGHT = pygame.K_RIGHT
KEY_P2_ATTACK = pygame.K_u    # Combo 3-Cortes
KEY_P2_PARRY = pygame.K_i     # Postura de Defesa / Bloqueio

# Teclas de Sistema
KEY_RESTART = pygame.K_SPACE
KEY_TOGGLE_AI = pygame.K_TAB  # Alternar J2 entre Humano e IA
KEY_SETTINGS = pygame.K_c     # Abrir/Fechar tela de Configurações de Controles

DEFAULT_CONTROLS = {
    "P1_UP": KEY_P1_UP,
    "P1_DOWN": KEY_P1_DOWN,
    "P1_LEFT": KEY_P1_LEFT,
    "P1_RIGHT": KEY_P1_RIGHT,
    "P1_ATTACK": KEY_P1_ATTACK,
    "P1_DASH": KEY_P1_DASH,
    "P2_UP": KEY_P2_UP,
    "P2_DOWN": KEY_P2_DOWN,
    "P2_LEFT": KEY_P2_LEFT,
    "P2_RIGHT": KEY_P2_RIGHT,
    "P2_ATTACK": KEY_P2_ATTACK,
    "P2_PARRY": KEY_P2_PARRY,
}

