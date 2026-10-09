"""
tools/build_hd2d_pilot_sprites.py - Gerador de Spritesheets HD-2D para os 3 Lutadores Piloto

Gera spritesheets em Pixel Art HD-2D de alta definição (72x80, FEET_Y = 72)
para os 3 combatentes da demo técnica:
  1. Okuni (Dançarina Kabuki / Mestra dos Leques Tessen)
  2. Kasumi (Kunoichi da Névoa / Armadura Cromada)
  3. Saitou (Capitão Shinsengumi / Estocada Gatotsu)

Produz:
  - Frames individuais RGBA em assets/sprites/<char>/:
      idle.png, walk_0.png, walk_1.png, attack.png, recovery.png, stunned.png, dead.png
  - Spritesheet agregada (504x80 px):
      spritesheet_<char>.png
  - Folha de contato comparativa do elenco (504x240 px):
      hd2d_demo_roster_sheet.png
  - Cópia sincronizada para hd2d_edition/assets/sprites/
"""
import os
import math
import shutil
import pygame

pygame.init()

SPRITE_W = 72
SPRITE_H = 80
FEET_Y = 72

OUTLINE = (18, 16, 22)


def create_surface() -> pygame.Surface:
    return pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)


# =============================================================================
# 1. OKUNI (DANÇARINA KABUKI)
# =============================================================================
OKUNI_SKIN = (252, 240, 235)
OKUNI_SKIN_SHADOW = (230, 205, 195)
OKUNI_KUMADORI = (215, 30, 48)
OKUNI_LIP = (220, 24, 45)
OKUNI_HAIR = (20, 18, 24)
OKUNI_KIMONO_RED = (190, 28, 42)
OKUNI_KIMONO_DARK = (130, 16, 30)
OKUNI_KIMONO_LIGHT = (225, 55, 70)
OKUNI_GOLD = (240, 198, 65)
OKUNI_GOLD_DARK = (180, 140, 45)
OKUNI_WHITE = (250, 250, 255)
OKUNI_STEEL = (225, 232, 245)
OKUNI_OBI_DARK = (28, 25, 32)
OKUNI_OBI_CORD = (210, 35, 45)


def draw_okuni_base(surf, cx, cy, state="IDLE", leg_offset=0, pose="IDLE"):
    # 1. Pés e Sandálias Zori com meias Tabi brancas
    foot_l_x = cx - 6 + leg_offset
    foot_r_x = cx + 5 - leg_offset
    foot_y = cy - 2
    pygame.draw.rect(surf, (245, 245, 250), (foot_l_x - 3, foot_y, 6, 3), border_radius=1)
    pygame.draw.rect(surf, (245, 245, 250), (foot_r_x - 3, foot_y, 6, 3), border_radius=1)
    pygame.draw.line(surf, OKUNI_KIMONO_RED, (foot_l_x, foot_y), (foot_l_x, foot_y + 2), 1)
    pygame.draw.line(surf, OKUNI_KIMONO_RED, (foot_r_x, foot_y), (foot_r_x, foot_y + 2), 1)

    # 2. Saia e Cauda do Quimono Uchikake em camadas
    skirt_pts = [
        (cx - 7, cy - 26),
        (cx + 7, cy - 26),
        (cx + 15 - leg_offset, cy - 2),
        (cx - 15 + leg_offset, cy - 2),
    ]
    pygame.draw.polygon(surf, OKUNI_KIMONO_RED, skirt_pts)
    # Barra acolchoada fuki dourada/vermelho escuro no solo
    pygame.draw.rect(surf, OKUNI_GOLD, (cx - 15 + leg_offset, cy - 5, 30, 3), border_radius=1)
    pygame.draw.rect(surf, OKUNI_KIMONO_DARK, (cx - 14 + leg_offset, cy - 8, 28, 3))
    # Dobras do quimono
    pygame.draw.line(surf, OKUNI_KIMONO_LIGHT, (cx - 4, cy - 25), (cx - 8 + leg_offset, cy - 5), 2)
    pygame.draw.line(surf, OKUNI_KIMONO_LIGHT, (cx + 4, cy - 25), (cx + 8 - leg_offset, cy - 5), 2)
    pygame.draw.polygon(surf, OUTLINE, skirt_pts, 1)

    # 3. Faixa Obi Cerimonial larga com laço e cordão
    pygame.draw.rect(surf, OKUNI_OBI_DARK, (cx - 8, cy - 30, 16, 6), border_radius=1)
    pygame.draw.line(surf, OKUNI_GOLD, (cx - 7, cy - 29), (cx + 7, cy - 29), 2)
    pygame.draw.line(surf, OKUNI_OBI_CORD, (cx - 6, cy - 27), (cx + 6, cy - 27), 1)
    # Broche de jade no centro
    pygame.draw.circle(surf, (75, 185, 150), (cx, cy - 27), 2)

    # 4. Torso e Quimono Superior
    torso_pts = [
        (cx - 7, cy - 40),
        (cx + 7, cy - 40),
        (cx + 8, cy - 30),
        (cx - 8, cy - 30),
    ]
    pygame.draw.polygon(surf, OKUNI_KIMONO_RED, torso_pts)
    # Decote em V e gola branca dupla
    pygame.draw.line(surf, OKUNI_WHITE, (cx - 5, cy - 40), (cx, cy - 33), 2)
    pygame.draw.line(surf, OKUNI_WHITE, (cx + 5, cy - 40), (cx, cy - 33), 2)
    pygame.draw.line(surf, OKUNI_GOLD, (cx - 6, cy - 40), (cx - 1, cy - 32), 1)
    pygame.draw.polygon(surf, OUTLINE, torso_pts, 1)

    # 5. Braços, Mangas Furisode Largas e Leques Tessen
    if pose == "IDLE":
        # Manga esquerda com leque fechado na cintura
        pygame.draw.ellipse(surf, OKUNI_KIMONO_RED, (cx - 14, cy - 39, 9, 15))
        pygame.draw.rect(surf, OKUNI_GOLD, (cx - 14, cy - 27, 9, 3))
        # Manga direita elevada com leque tessen semi-aberto
        pygame.draw.ellipse(surf, OKUNI_KIMONO_RED, (cx + 5, cy - 42, 10, 16))
        pygame.draw.rect(surf, OKUNI_GOLD, (cx + 6, cy - 29, 9, 3))
        # Leque tessen aberto na mão direita
        fan_pts = [(cx + 10, cy - 42), (cx + 22, cy - 48), (cx + 25, cy - 38), (cx + 12, cy - 36)]
        pygame.draw.polygon(surf, OKUNI_KIMONO_RED, fan_pts)
        pygame.draw.circle(surf, OKUNI_GOLD, (cx + 18, cy - 42), 3)
        pygame.draw.line(surf, OKUNI_STEEL, (cx + 10, cy - 42), (cx + 23, cy - 43), 1)
        pygame.draw.polygon(surf, OUTLINE, fan_pts, 1)

    elif pose == "ATTACK":
        # Giro duplo de leques cortantes com lâminas de aço estendidas
        # Manga esquerda projetada
        pygame.draw.line(surf, OKUNI_KIMONO_RED, (cx - 6, cy - 38), (cx - 20, cy - 36), 6)
        # Manga direita estendida à frente
        pygame.draw.line(surf, OKUNI_KIMONO_RED, (cx + 6, cy - 38), (cx + 20, cy - 34), 6)
        # Leque Esquerdo aberto em arco cortante
        fan_l = [(cx - 20, cy - 36), (cx - 32, cy - 44), (cx - 30, cy - 30)]
        pygame.draw.polygon(surf, OKUNI_KIMONO_RED, fan_l)
        pygame.draw.line(surf, OKUNI_STEEL, (cx - 20, cy - 36), (cx - 32, cy - 44), 2)
        # Leque Direito aberto com sol dourado
        fan_r = [(cx + 20, cy - 34), (cx + 34, cy - 42), (cx + 32, cy - 26)]
        pygame.draw.polygon(surf, OKUNI_KIMONO_RED, fan_r)
        pygame.draw.line(surf, OKUNI_STEEL, (cx + 20, cy - 34), (cx + 34, cy - 42), 2)
        pygame.draw.circle(surf, OKUNI_GOLD, (cx + 27, cy - 34), 3)

    elif pose == "RECOVERY":
        # Pose de Mie tradicional: leques cruzados na altura do peito
        pygame.draw.ellipse(surf, OKUNI_KIMONO_RED, (cx - 12, cy - 38, 8, 14))
        pygame.draw.ellipse(surf, OKUNI_KIMONO_RED, (cx + 4, cy - 38, 8, 14))
        pygame.draw.line(surf, OKUNI_STEEL, (cx - 6, cy - 34), (cx + 10, cy - 44), 2)
        pygame.draw.line(surf, OKUNI_STEEL, (cx + 6, cy - 34), (cx - 10, cy - 44), 2)

    elif pose == "STUN":
        # Recuo sobressaltado
        pygame.draw.line(surf, OKUNI_KIMONO_RED, (cx - 6, cy - 36), (cx - 16, cy - 42), 5)
        pygame.draw.line(surf, OKUNI_KIMONO_RED, (cx + 6, cy - 36), (cx + 16, cy - 42), 5)

    # 6. Cabeça, Rosto Oshiroi e Kumadori
    head_y = cy - 46
    pygame.draw.circle(surf, OKUNI_SKIN, (cx, head_y), 6)
    # Kumadori vermelho ao redor dos olhos e lábios
    pygame.draw.circle(surf, OKUNI_KUMADORI, (cx - 2, head_y - 1), 2)
    pygame.draw.circle(surf, OKUNI_KUMADORI, (cx + 2, head_y - 1), 2)
    pygame.draw.circle(surf, OKUNI_HAIR, (cx - 2, head_y - 1), 1)
    pygame.draw.circle(surf, OKUNI_HAIR, (cx + 2, head_y - 1), 1)
    pygame.draw.line(surf, OKUNI_LIP, (cx - 1, head_y + 3), (cx + 1, head_y + 3), 1)

    # 7. Penteado Taka-shimada laqueado e joias Kanzashi douradas
    pygame.draw.ellipse(surf, OKUNI_HAIR, (cx - 7, head_y - 8, 14, 8))
    # Coque volumoso superior
    pygame.draw.circle(surf, OKUNI_HAIR, (cx, head_y - 8), 5)
    # Pente kushi dourado frontal
    pygame.draw.rect(surf, OKUNI_GOLD, (cx - 5, head_y - 9, 10, 3), border_radius=1)
    # Kanzashi (três agulhas douradas)
    pygame.draw.line(surf, OKUNI_GOLD, (cx - 6, head_y - 8), (cx - 11, head_y - 12), 2)
    pygame.draw.line(surf, OKUNI_GOLD, (cx + 6, head_y - 8), (cx + 11, head_y - 12), 2)
    pygame.draw.line(surf, OKUNI_GOLD, (cx + 2, head_y - 10), (cx + 5, head_y - 14), 2)
    # Fita vermelha kanoko na base
    pygame.draw.circle(surf, OKUNI_KIMONO_RED, (cx, head_y - 6), 2)


# =============================================================================
# 2. KASUMI (KUNOICHI DA NÉVOA)
# =============================================================================
KASUMI_SKIN = (245, 214, 192)
KASUMI_SKIN_SHADOW = (212, 175, 150)
KASUMI_HAIR = (235, 240, 248)
KASUMI_HAIR_DARK = (175, 185, 200)
KASUMI_SUIT = (34, 36, 44)
KASUMI_SUIT_DARK = (20, 22, 28)
KASUMI_STEEL = (215, 225, 238)
KASUMI_STEEL_DARK = (130, 140, 155)
KASUMI_SCARF = (160, 170, 185)
KASUMI_SCARF_LIGHT = (200, 210, 225)
KASUMI_CYAN_AURA = (80, 220, 235)


def draw_kasumi_base(surf, cx, cy, state="IDLE", leg_offset=0, pose="IDLE"):
    # 1. Pés e Caneleiras de Aço Cromado
    foot_l_x = cx - 6 + leg_offset
    foot_r_x = cx + 5 - leg_offset
    foot_y = cy - 2
    # Botas/meias ninja com solado flexível
    pygame.draw.rect(surf, KASUMI_SUIT_DARK, (foot_l_x - 3, foot_y, 6, 3), border_radius=1)
    pygame.draw.rect(surf, KASUMI_SUIT_DARK, (foot_r_x - 3, foot_y, 6, 3), border_radius=1)
    # Caneleiras cromadas (Suneate)
    pygame.draw.rect(surf, KASUMI_STEEL, (foot_l_x - 2, foot_y - 10, 5, 9), border_radius=1)
    pygame.draw.rect(surf, KASUMI_STEEL, (foot_r_x - 2, foot_y - 10, 5, 9), border_radius=1)

    # 2. Pernas e Calças Táticas Shinobi
    leg_pts = [
        (cx - 5, cy - 24),
        (cx + 5, cy - 24),
        (cx + 7 - leg_offset, cy - 11),
        (cx - 7 + leg_offset, cy - 11)
    ]
    pygame.draw.polygon(surf, KASUMI_SUIT, leg_pts)

    # 3. Cintura com cinturão de fivelas e coldres para kunai
    pygame.draw.rect(surf, KASUMI_SUIT_DARK, (cx - 6, cy - 27, 12, 4), border_radius=1)
    pygame.draw.rect(surf, KASUMI_STEEL, (cx - 2, cy - 27, 4, 4), 1)

    # 4. Torso com Placas de Armadura Cromada
    torso_pts = [
        (cx - 6, cy - 38),
        (cx + 6, cy - 38),
        (cx + 6, cy - 26),
        (cx - 6, cy - 26)
    ]
    pygame.draw.polygon(surf, KASUMI_SUIT, torso_pts)
    # Peitoral de armadura cromada curva
    pygame.draw.polygon(surf, KASUMI_STEEL, [(cx - 5, cy - 37), (cx + 5, cy - 37), (cx + 3, cy - 28), (cx - 3, cy - 28)])
    pygame.draw.line(surf, (255, 255, 255), (cx - 3, cy - 36), (cx - 1, cy - 30), 1) # Reflexo de luz

    # 5. Cachecol drapeado esvoaçante que ondula ao vento
    scarf_pts = [
        (cx - 5, cy - 38),
        (cx + 5, cy - 38),
        (cx - 14, cy - 42),
        (cx - 22, cy - 36),
        (cx - 16, cy - 32)
    ]
    pygame.draw.polygon(surf, KASUMI_SCARF, scarf_pts)
    pygame.draw.lines(surf, KASUMI_SCARF_LIGHT, False, [(cx - 5, cy - 38), (cx - 16, cy - 40), (cx - 22, cy - 36)], 2)

    # 6. Braços, Ombreiras Cromadas e Adagas Duplas
    if pose == "IDLE":
        # Ombreiras de placas
        pygame.draw.circle(surf, KASUMI_STEEL, (cx - 7, cy - 37), 4)
        pygame.draw.circle(surf, KASUMI_STEEL, (cx + 7, cy - 37), 4)
        # Braços em guarda média com adagas em empunhadura invertida
        pygame.draw.line(surf, KASUMI_SUIT, (cx - 7, cy - 37), (cx - 10, cy - 28), 3)
        pygame.draw.line(surf, KASUMI_SUIT, (cx + 7, cy - 37), (cx + 10, cy - 28), 3)
        # Lâminas afiadas das adagas
        pygame.draw.line(surf, KASUMI_STEEL, (cx - 10, cy - 28), (cx - 13, cy - 20), 2)
        pygame.draw.line(surf, KASUMI_STEEL, (cx + 10, cy - 28), (cx + 13, cy - 20), 2)

    elif pose == "ATTACK":
        # Corte cruzado veloz com arco de lâmina reluzente
        pygame.draw.line(surf, KASUMI_SUIT, (cx - 6, cy - 36), (cx + 16, cy - 34), 4)
        pygame.draw.line(surf, KASUMI_SUIT, (cx + 6, cy - 36), (cx + 20, cy - 28), 4)
        # Duas lâminas cortando para a frente
        pygame.draw.line(surf, KASUMI_STEEL, (cx + 16, cy - 34), (cx + 34, cy - 38), 3)
        pygame.draw.line(surf, KASUMI_STEEL, (cx + 20, cy - 28), (cx + 36, cy - 30), 3)
        # Arco de corte e vento
        pygame.draw.lines(surf, KASUMI_CYAN_AURA, False, [(cx + 14, cy - 44), (cx + 32, cy - 38), (cx + 38, cy - 24)], 3)
        pygame.draw.lines(surf, (255, 255, 255), False, [(cx + 15, cy - 43), (cx + 31, cy - 37), (cx + 36, cy - 25)], 1)

    elif pose == "RECOVERY":
        # Pouso agachado ágil
        pygame.draw.line(surf, KASUMI_SUIT, (cx - 6, cy - 34), (cx - 12, cy - 26), 3)
        pygame.draw.line(surf, KASUMI_SUIT, (cx + 6, cy - 34), (cx + 12, cy - 26), 3)
        pygame.draw.line(surf, KASUMI_STEEL, (cx - 12, cy - 26), (cx - 16, cy - 20), 2)

    elif pose == "STUN":
        pygame.draw.line(surf, KASUMI_SUIT, (cx - 6, cy - 35), (cx - 14, cy - 40), 3)
        pygame.draw.line(surf, KASUMI_SUIT, (cx + 6, cy - 35), (cx + 14, cy - 40), 3)

    # 7. Cabeça, Rosto e Máscara Shinobi
    head_y = cy - 44
    pygame.draw.circle(surf, KASUMI_SKIN, (cx, head_y), 5)
    # Máscara cobrindo boca e queixo
    pygame.draw.rect(surf, KASUMI_SUIT_DARK, (cx - 4, head_y, 8, 4), border_radius=1)
    # Olhos expressivos azuis-aço
    pygame.draw.line(surf, (20, 22, 28), (cx - 3, head_y - 2), (cx - 1, head_y - 2), 1)
    pygame.draw.line(surf, (20, 22, 28), (cx + 1, head_y - 2), (cx + 3, head_y - 2), 1)
    pygame.draw.circle(surf, KASUMI_CYAN_AURA, (cx - 2, head_y - 2), 1)
    pygame.draw.circle(surf, KASUMI_CYAN_AURA, (cx + 2, head_y - 2), 1)

    # 8. Cabelo Prateado em Rabo de Cavalo Alto
    pygame.draw.ellipse(surf, KASUMI_HAIR, (cx - 5, head_y - 7, 10, 6))
    # Rabo de cavalo alto volumoso com fita
    pygame.draw.polygon(surf, KASUMI_HAIR, [(cx - 2, head_y - 6), (cx - 12, head_y - 12), (cx - 18, head_y - 4), (cx - 8, head_y - 2)])
    pygame.draw.polygon(surf, KASUMI_HAIR_DARK, [(cx - 2, head_y - 6), (cx - 10, head_y - 10), (cx - 14, head_y - 4)])
    pygame.draw.circle(surf, KASUMI_SUIT_DARK, (cx - 2, head_y - 6), 2)


# =============================================================================
# 3. SAITOU (CAPITÃO SHINSENGUMI)
# =============================================================================
SAITOU_SKIN = (242, 210, 185)
SAITOU_HAIR = (22, 20, 26)
SAITOU_HAORI_BLUE = (85, 165, 220)
SAITOU_HAORI_LIGHT = (130, 195, 245)
SAITOU_HAORI_DARK = (50, 110, 160)
SAITOU_DANDARA = (250, 250, 255)
SAITOU_HAKAMA = (26, 30, 42)
SAITOU_STEEL = (225, 235, 245)
SAITOU_STEEL_DARK = (140, 150, 165)
SAITOU_GOLD = (235, 195, 60)
SAITOU_GATOTSU_AURA = (100, 210, 255)


def draw_saitou_base(surf, cx, cy, state="IDLE", leg_offset=0, pose="IDLE"):
    # 1. Pés e Sandálias Waraji
    foot_l_x = cx - 6 + leg_offset
    foot_r_x = cx + 5 - leg_offset
    foot_y = cy - 2
    pygame.draw.rect(surf, (160, 140, 110), (foot_l_x - 3, foot_y, 6, 3), border_radius=1)
    pygame.draw.rect(surf, (160, 140, 110), (foot_r_x - 3, foot_y, 6, 3), border_radius=1)

    # 2. Hakama Azul-Marinho / Preto Pregueado
    hakama_pts = [
        (cx - 5, cy - 24),
        (cx + 5, cy - 24),
        (cx + 11 - leg_offset, cy - 3),
        (cx - 11 + leg_offset, cy - 3)
    ]
    pygame.draw.polygon(surf, SAITOU_HAKAMA, hakama_pts)
    pygame.draw.line(surf, (45, 52, 70), (cx - 3, cy - 23), (cx - 6 + leg_offset, cy - 4), 2)
    pygame.draw.line(surf, (45, 52, 70), (cx + 3, cy - 23), (cx + 6 - leg_offset, cy - 4), 2)
    pygame.draw.polygon(surf, OUTLINE, hakama_pts, 1)

    # 3. Faixa Obi e Bainha da Katana
    pygame.draw.rect(surf, (20, 22, 28), (cx - 6, cy - 27, 12, 4), border_radius=1)
    if pose != "DEAD":
        pygame.draw.line(surf, (15, 15, 18), (cx + 12, cy - 16), (cx - 5, cy - 26), 3) # Bainha Saya preta
        pygame.draw.circle(surf, SAITOU_GOLD, (cx - 4, cy - 26), 2) # Tsuba

    # 4. Haori Azul-Celeste Shinsengumi (Asagi-iro) com Estampa Dandara Branca
    torso_pts = [
        (cx - 7, cy - 39),
        (cx + 7, cy - 39),
        (cx + 7, cy - 26),
        (cx - 7, cy - 26)
    ]
    pygame.draw.polygon(surf, SAITOU_HAORI_BLUE, torso_pts)
    # Gola branca interna
    pygame.draw.line(surf, (245, 245, 250), (cx - 4, cy - 39), (cx, cy - 32), 2)
    pygame.draw.line(surf, (245, 245, 250), (cx + 4, cy - 39), (cx, cy - 32), 2)
    # Faixa branca dandara na borda inferior do haori
    pygame.draw.rect(surf, SAITOU_DANDARA, (cx - 7, cy - 27, 14, 2))
    pygame.draw.polygon(surf, OUTLINE, torso_pts, 1)

    # 5. Mangas do Haori com Triângulos Shinsengumi (Dandara Pattern)
    if pose == "IDLE":
        # Braço esquerdo na bainha da cintura
        pygame.draw.ellipse(surf, SAITOU_HAORI_BLUE, (cx - 13, cy - 38, 8, 14))
        # Padrão serrilhado dandara na manga
        pygame.draw.polygon(surf, SAITOU_DANDARA, [(cx - 13, cy - 27), (cx - 9, cy - 24), (cx - 5, cy - 27)])
        # Braço direito apoiando na guarda da katana
        pygame.draw.line(surf, SAITOU_HAORI_BLUE, (cx + 6, cy - 37), (cx + 1, cy - 27), 4)
        pygame.draw.polygon(surf, SAITOU_DANDARA, [(cx + 2, cy - 29), (cx + 5, cy - 26), (cx + 8, cy - 29)])
        pygame.draw.circle(surf, SAITOU_SKIN, (cx, cy - 26), 2)

    elif pose == "ATTACK":
        # POSTURA CLÁSSICA GATOTSU (Estocada Perfurante Horizontal Fulminante!)
        # Corpo inclinado para a frente em postura baixa
        # Braço direito estendido reto em estocada
        pygame.draw.line(surf, SAITOU_HAORI_BLUE, (cx - 2, cy - 36), (cx + 18, cy - 34), 5)
        # Mão direita segurando o cabo
        pygame.draw.circle(surf, SAITOU_SKIN, (cx + 18, cy - 34), 3)
        # Lâmina longa da katana em linha reta penetrante
        pygame.draw.line(surf, SAITOU_STEEL, (cx + 19, cy - 34), (cx + 42, cy - 34), 3)
        pygame.draw.line(surf, (255, 255, 255), (cx + 20, cy - 35), (cx + 41, cy - 35), 1)
        # Mão esquerda apoiando a lâmina/cabo na postura Gatotsu
        pygame.draw.line(surf, SAITOU_HAORI_BLUE, (cx - 6, cy - 36), (cx + 8, cy - 33), 4)
        pygame.draw.circle(surf, SAITOU_SKIN, (cx + 8, cy - 33), 2)
        # Feixe perfurante azul-celeste em linha reta
        pygame.draw.line(surf, SAITOU_GATOTSU_AURA, (cx + 22, cy - 34), (cx + 46, cy - 34), 4)
        pygame.draw.circle(surf, (255, 255, 255), (cx + 43, cy - 34), 3)

    elif pose == "RECOVERY":
        # Recolhendo a katana após o Gatotsu
        pygame.draw.line(surf, SAITOU_HAORI_BLUE, (cx + 5, cy - 36), (cx + 12, cy - 32), 4)
        pygame.draw.line(surf, SAITOU_STEEL, (cx + 12, cy - 32), (cx + 26, cy - 36), 2)

    elif pose == "STUN":
        pygame.draw.line(surf, SAITOU_HAORI_BLUE, (cx - 6, cy - 35), (cx - 15, cy - 38), 4)
        pygame.draw.line(surf, SAITOU_HAORI_BLUE, (cx + 6, cy - 35), (cx + 14, cy - 38), 4)

    # 6. Cabeça, Rosto e Bandana Hachigane com Placa de Ferro
    head_y = cy - 45
    pygame.draw.circle(surf, SAITOU_SKIN, (cx, head_y), 6)
    # Olhos penetrantes de lobo de Mibu
    pygame.draw.line(surf, (20, 20, 25), (cx + 1, head_y - 1), (cx + 4, head_y - 1), 2)
    # Bandana hachigane com placa de aço polido na testa
    pygame.draw.rect(surf, (20, 22, 28), (cx - 6, head_y - 6, 12, 3))
    pygame.draw.rect(surf, SAITOU_STEEL, (cx - 3, head_y - 6, 6, 3), border_radius=1)

    # 7. Cabelo Preto em Coque Samurai Tradicional
    pygame.draw.ellipse(surf, SAITOU_HAIR, (cx - 6, head_y - 8, 12, 6))
    # Topete / Chonmage samurai atrás
    pygame.draw.polygon(surf, SAITOU_HAIR, [(cx - 2, head_y - 8), (cx - 6, head_y - 13), (cx + 1, head_y - 11)])


# =============================================================================
# CONSTRUTORES DE FRAMES HD-2D
# =============================================================================

def build_frames_for_char(char_key: str):
    """Constrói os 7 frames padronizados do personagem."""
    frames = {}

    if char_key == "okuni":
        base_fn = draw_okuni_base
        dead_hair_color = OKUNI_HAIR
        dead_dress_color = OKUNI_KIMONO_RED
    elif char_key == "kasumi":
        base_fn = draw_kasumi_base
        dead_hair_color = KASUMI_HAIR
        dead_dress_color = KASUMI_SUIT
    else:  # saitou
        base_fn = draw_saitou_base
        dead_hair_color = SAITOU_HAIR
        dead_dress_color = SAITOU_HAORI_BLUE

    # 1. idle
    s = create_surface()
    base_fn(s, SPRITE_W // 2, FEET_Y, state="IDLE", leg_offset=0, pose="IDLE")
    frames["idle"] = s

    # 2. walk_0
    s0 = create_surface()
    base_fn(s0, SPRITE_W // 2, FEET_Y, state="WALK", leg_offset=3, pose="IDLE")
    frames["walk_0"] = s0

    # 3. walk_1
    s1 = create_surface()
    base_fn(s1, SPRITE_W // 2, FEET_Y, state="WALK", leg_offset=-3, pose="IDLE")
    frames["walk_1"] = s1

    # 4. attack
    sa = create_surface()
    cx_atk = SPRITE_W // 2 - 4
    base_fn(sa, cx_atk, FEET_Y, state="ATTACK", leg_offset=4, pose="ATTACK")
    frames["attack"] = sa

    # 5. recovery
    sr = create_surface()
    base_fn(sr, SPRITE_W // 2, FEET_Y, state="RECOVERY", leg_offset=1, pose="RECOVERY")
    frames["recovery"] = sr

    # 6. stunned
    ss = create_surface()
    base_fn(ss, SPRITE_W // 2 - 3, FEET_Y, state="STUNNED", leg_offset=-3, pose="STUN")
    pygame.draw.circle(ss, (255, 215, 60), (SPRITE_W // 2 + 5, FEET_Y - 48), 3)
    frames["stunned"] = ss

    # 7. dead
    sd = create_surface()
    cx = SPRITE_W // 2
    cy = FEET_Y
    pygame.draw.ellipse(sd, (15, 12, 18, 120), (cx - 24, cy - 8, 48, 14)) # Sombra
    pygame.draw.rect(sd, dead_dress_color, (cx - 15, cy - 9, 22, 8), border_radius=2)
    pygame.draw.circle(sd, dead_hair_color, (cx + 14, cy - 7), 5)
    pygame.draw.line(sd, (220, 230, 245), (cx - 18, cy - 2), (cx + 2, cy - 2), 2)
    frames["dead"] = sd

    return frames


def build_spritesheet(frames: dict) -> pygame.Surface:
    """Combina os 7 frames em uma fita horizontal única (504x80)."""
    order = ["idle", "walk_0", "walk_1", "attack", "recovery", "stunned", "dead"]
    sheet = pygame.Surface((SPRITE_W * len(order), SPRITE_H), pygame.SRCALPHA)
    for idx, name in enumerate(order):
        sheet.blit(frames[name], (idx * SPRITE_W, 0))
    return sheet


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dirs = [
        os.path.join(root_dir, "assets", "sprites"),
        os.path.join(root_dir, "hd2d_edition", "assets", "sprites")
    ]

    characters = ["okuni", "kasumi", "saitou"]
    all_char_sheets = {}

    for char_key in characters:
        frames = build_frames_for_char(char_key)
        sheet = build_spritesheet(frames)
        all_char_sheets[char_key] = sheet

        for base in target_dirs:
            char_dir = os.path.join(base, char_key)
            os.makedirs(char_dir, exist_ok=True)

            # Salva frames individuais
            for name, surf in frames.items():
                out_path = os.path.join(char_dir, f"{name}.png")
                pygame.image.save(surf, out_path)

            # Salva spritesheet consolidada do personagem
            sheet_path = os.path.join(char_dir, f"spritesheet_{char_key}.png")
            pygame.image.save(sheet, sheet_path)
            print(f"[OK] Sprites e folha de {char_key} salvos em: {char_dir}")

    # Salva também a folha comparativa geral (3 linhas x 7 colunas = 504x240)
    roster_sheet = pygame.Surface((SPRITE_W * 7, SPRITE_H * len(characters)), pygame.SRCALPHA)
    for row_idx, char_key in enumerate(characters):
        roster_sheet.blit(all_char_sheets[char_key], (0, row_idx * SPRITE_H))

    for base in target_dirs:
        comp_path = os.path.join(base, "hd2d_demo_roster_sheet.png")
        pygame.image.save(roster_sheet, comp_path)
        print(f"[OK] Folha agregada do elenco salva em: {comp_path}")

    print("\n✅ Todos os sprites e spritesheets HD-2D para Okuni, Kasumi e Saitou foram gerados com sucesso!")


if __name__ == "__main__":
    main()
