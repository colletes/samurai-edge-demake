"""
build_hd2d_sprites.py
Gera os sprites em Pixel Art HD-2D de alta definição para Kenshi e Murasaki (Kunoichi Roxa).
Produz sprites RGBA transparentes com proporções compatíveis com os tiles isométricos da arena (64x32),
com sombreamento detalhado, contorno escurecido, armas e efeitos de lâmina/foice.
"""
import os
import math
import pygame

pygame.init()

SPRITE_W = 72
SPRITE_H = 80
FEET_Y = 72 # Ponto de contato dos pés com o solo no sprite

# Paleta Kenshi
KENSHI_SKIN = (248, 214, 186)
KENSHI_SKIN_SHADOW = (220, 175, 145)
KENSHI_HAIR = (185, 70, 35)
KENSHI_HAIR_DARK = (130, 42, 20)
KENSHI_HAIR_HIGHLIGHT = (225, 105, 55)
KENSHI_RIBBON = (210, 35, 45)
KENSHI_KIMONO_RED = (195, 30, 45)
KENSHI_KIMONO_DARK = (135, 18, 30)
KENSHI_KIMONO_LIGHT = (230, 60, 75)
KENSHI_GOLD = (235, 195, 60)
KENSHI_HAKAMA_DARK = (34, 36, 44)
KENSHI_HAKAMA_MID = (48, 52, 64)
KENSHI_WHITE = (245, 245, 250)
KENSHI_STEEL = (220, 235, 245)
KENSHI_STEEL_DARK = (140, 155, 170)
KENSHI_AURA_RED = (255, 50, 60)

# Paleta Murasaki
MURA_SKIN = (245, 212, 190)
MURA_SKIN_SHADOW = (210, 170, 150)
MURA_HAIR = (28, 24, 38)
MURA_HAIR_DARK = (16, 12, 22)
MURA_HAIR_HIGHLIGHT = (70, 60, 95)
MURA_SUIT_PURPLE = (140, 65, 190)
MURA_SUIT_DARK = (55, 24, 82)
MURA_SUIT_DEEP = (32, 14, 48)
MURA_SUIT_LIGHT = (185, 105, 235)
MURA_ARMOR_STEEL = (60, 64, 75)
MURA_ARMOR_HIGHLIGHT = (160, 170, 190)
MURA_CHAIN = (185, 190, 205)
MURA_KAMA_STEEL = (225, 230, 245)
MURA_AURA_PURPLE = (210, 110, 255)
MURA_AURA_DEEP = (160, 40, 230)

OUTLINE = (18, 16, 22)

def create_surface():
    return pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

# ==============================================================================
# KENSHI SPRITES
# ==============================================================================

def draw_kenshi_base(surf, cx, cy, state="IDLE", leg_offset=0, arm_pose="IAI"):
    """
    Desenha Kenshi:
    cx: centro horizontal dos pés
    cy: base dos pés
    """
    # 1. Pés e Sandálias (Waraji)
    foot_l_x = cx - 7 + leg_offset
    foot_r_x = cx + 5 - leg_offset
    foot_y = cy - 2
    # Sola
    pygame.draw.rect(surf, (160, 140, 110), (foot_l_x - 3, foot_y, 7, 3), border_radius=1)
    pygame.draw.rect(surf, (160, 140, 110), (foot_r_x - 3, foot_y, 7, 3), border_radius=1)
    # Tiras pretas
    pygame.draw.line(surf, OUTLINE, (foot_l_x, foot_y), (foot_l_x, foot_y + 2), 1)
    pygame.draw.line(surf, OUTLINE, (foot_r_x, foot_y), (foot_r_x, foot_y + 2), 1)

    # 2. Hakama (Calça samurai larga tradicional)
    # Altura do hakama: de cy - 25 até cy - 2
    hakama_pts = [
        (cx - 5, cy - 24), # Cintura esq
        (cx + 5, cy - 24), # Cintura dir
        (cx + 12 - leg_offset, cy - 3), # Barra dir
        (cx + 1, cy - 8),  # Meio fenda
        (cx - 12 + leg_offset, cy - 3), # Barra esq
    ]
    pygame.draw.polygon(surf, KENSHI_HAKAMA_DARK, hakama_pts)
    # Pregas e destaques no tecido do Hakama
    pygame.draw.line(surf, KENSHI_HAKAMA_MID, (cx - 3, cy - 23), (cx - 7 + leg_offset, cy - 4), 2)
    pygame.draw.line(surf, KENSHI_HAKAMA_MID, (cx + 3, cy - 23), (cx + 7 - leg_offset, cy - 4), 2)
    pygame.draw.polygon(surf, OUTLINE, hakama_pts, 1)

    # 3. Faixa Obi na cintura (Azul marinho escuro com nós)
    pygame.draw.rect(surf, (22, 25, 34), (cx - 6, cy - 27, 12, 4), border_radius=1)
    pygame.draw.line(surf, (40, 48, 65), (cx - 5, cy - 26), (cx + 5, cy - 26), 1)

    # 4. Kimono Carmim (Torso)
    torso_pts = [
        (cx - 7, cy - 38), # Ombro esq
        (cx + 7, cy - 38), # Ombro dir
        (cx + 6, cy - 26), # Cintura dir
        (cx - 6, cy - 26), # Cintura esq
    ]
    pygame.draw.polygon(surf, KENSHI_KIMONO_RED, torso_pts)
    # Destaque de dobra no peito
    pygame.draw.polygon(surf, KENSHI_KIMONO_LIGHT, [(cx - 4, cy - 36), (cx + 4, cy - 36), (cx + 1, cy - 28), (cx - 2, cy - 28)])
    # Gola branca interna e decote
    pygame.draw.line(surf, KENSHI_WHITE, (cx - 4, cy - 38), (cx, cy - 31), 2)
    pygame.draw.line(surf, KENSHI_WHITE, (cx + 4, cy - 38), (cx, cy - 31), 2)
    pygame.draw.line(surf, KENSHI_SKIN, (cx - 2, cy - 36), (cx + 2, cy - 36), 2)
    pygame.draw.polygon(surf, OUTLINE, torso_pts, 1)

    # 5. Bainha da Katana (Saya) presa no quadril esquerdo
    if arm_pose != "DEAD":
        pygame.draw.line(surf, (15, 15, 18), (cx + 14, cy - 14), (cx - 4, cy - 26), 3) # Bainha preta laqueada
        pygame.draw.line(surf, KENSHI_GOLD, (cx - 3, cy - 27), (cx - 1, cy - 25), 2)  # Tsuba (guarda) dourada

    # 6. Braços e Mangas Largas com Bordado Dourado
    if arm_pose == "IAI":
        # Braço esquerdo segurando a bainha na cintura
        pygame.draw.circle(surf, KENSHI_KIMONO_RED, (cx - 6, cy - 26), 5)
        pygame.draw.rect(surf, KENSHI_GOLD, (cx - 9, cy - 24, 4, 3))
        pygame.draw.circle(surf, KENSHI_SKIN, (cx - 4, cy - 26), 3) # Mão esquerda no saque
        # Braço direito empunhando a empunhadura da katana (Tsuka)
        pygame.draw.line(surf, KENSHI_KIMONO_RED, (cx + 6, cy - 36), (cx + 1, cy - 27), 4)
        pygame.draw.circle(surf, KENSHI_SKIN, (cx, cy - 26), 3) # Mão direita na empunhadura
        # Tsuka (cabo)
        pygame.draw.line(surf, (20, 20, 25), (cx - 2, cy - 26), (cx - 7, cy - 29), 2)
    elif arm_pose == "SLASH":
        # Golpe estendido! Lâmina reluzente cortando o ar
        pygame.draw.line(surf, KENSHI_KIMONO_RED, (cx - 5, cy - 36), (cx - 14, cy - 28), 4)
        pygame.draw.line(surf, KENSHI_SKIN, (cx - 14, cy - 28), (cx - 20, cy - 26), 3)
        # Braço direito estendido para frente em corte Iai
        pygame.draw.line(surf, KENSHI_KIMONO_RED, (cx + 6, cy - 36), (cx + 16, cy - 34), 4)
        pygame.draw.circle(surf, KENSHI_SKIN, (cx + 17, cy - 34), 3)
        # Katana de aço afiado reluzindo
        pygame.draw.line(surf, KENSHI_STEEL, (cx + 18, cy - 34), (cx + 34, cy - 38), 3)
        pygame.draw.line(surf, KENSHI_WHITE, (cx + 19, cy - 35), (cx + 33, cy - 38), 1)
        pygame.draw.circle(surf, KENSHI_GOLD, (cx + 18, cy - 34), 2)
    elif arm_pose == "NOTO": # Guardando a katana
        pygame.draw.line(surf, KENSHI_KIMONO_RED, (cx + 5, cy - 36), (cx + 3, cy - 26), 4)
        pygame.draw.circle(surf, KENSHI_SKIN, (cx + 3, cy - 25), 3)
        pygame.draw.line(surf, KENSHI_STEEL, (cx + 2, cy - 26), (cx + 12, cy - 32), 2) # Lâmina quase guardada
        pygame.draw.circle(surf, KENSHI_SKIN, (cx - 4, cy - 26), 3) # Mão esquerda no bocal da bainha
    elif arm_pose == "STUN":
        # Braços abertos em recuo
        pygame.draw.line(surf, KENSHI_KIMONO_RED, (cx - 6, cy - 35), (cx - 15, cy - 38), 4)
        pygame.draw.line(surf, KENSHI_KIMONO_RED, (cx + 6, cy - 35), (cx + 14, cy - 38), 4)

    # 7. Cabeça e Rosto
    head_y = cy - 44
    pygame.draw.circle(surf, KENSHI_SKIN, (cx, head_y), 6)
    # Sombra do queixo e pescoço
    pygame.draw.rect(surf, KENSHI_SKIN_SHADOW, (cx - 2, head_y + 4, 4, 3))
    # Olhos expressivos
    pygame.draw.line(surf, (40, 20, 15), (cx + 1, head_y - 1), (cx + 4, head_y - 1), 1)
    pygame.draw.circle(surf, (70, 35, 20), (cx + 3, head_y - 1), 1)
    # Lábios
    pygame.draw.line(surf, (200, 100, 90), (cx + 2, head_y + 3), (cx + 3, head_y + 3), 1)

    # 8. Cabelo Ruivo Castanho e Rabo de Cavalo com Fita Vermelha
    # Franja charmosa
    pygame.draw.line(surf, KENSHI_HAIR, (cx - 4, head_y - 6), (cx - 1, head_y + 2), 2)
    pygame.draw.line(surf, KENSHI_HAIR, (cx - 2, head_y - 6), (cx + 2, head_y - 1), 2)
    pygame.draw.line(surf, KENSHI_HAIR, (cx + 1, head_y - 6), (cx + 5, head_y + 2), 2)
    # Topo da cabeça
    pygame.draw.ellipse(surf, KENSHI_HAIR, (cx - 6, head_y - 8, 12, 8))
    pygame.draw.ellipse(surf, KENSHI_HAIR_HIGHLIGHT, (cx - 4, head_y - 7, 8, 4))
    # Laço vermelho da fita
    pygame.draw.circle(surf, KENSHI_RIBBON, (cx - 3, head_y - 7), 3)
    pygame.draw.line(surf, KENSHI_RIBBON, (cx - 5, head_y - 7), (cx - 8, head_y - 4), 2)
    # Rabo de cavalo volumoso caindo para trás
    ponytail_pts = [
        (cx - 3, head_y - 7),
        (cx - 11, head_y - 3),
        (cx - 14, head_y + 8),
        (cx - 9, head_y + 16),
        (cx - 7, head_y + 10),
        (cx - 5, head_y + 2),
    ]
    pygame.draw.polygon(surf, KENSHI_HAIR_DARK, ponytail_pts)
    pygame.draw.polygon(surf, KENSHI_HAIR, [(cx - 4, head_y - 6), (cx - 10, head_y), (cx - 12, head_y + 8), (cx - 8, head_y + 4)])
    pygame.draw.polygon(surf, OUTLINE, ponytail_pts, 1)

def build_kenshi_idle():
    surf = create_surface()
    draw_kenshi_base(surf, SPRITE_W // 2, FEET_Y, state="IDLE", leg_offset=0, arm_pose="IAI")
    return surf

def build_kenshi_walk(frame=0):
    surf = create_surface()
    offset = 3 if frame == 0 else -3
    draw_kenshi_base(surf, SPRITE_W // 2, FEET_Y, state="WALK", leg_offset=offset, arm_pose="IAI")
    return surf

def build_kenshi_attack():
    surf = create_surface()
    cx = SPRITE_W // 2 - 6
    draw_kenshi_base(surf, cx, FEET_Y, state="ATTACK", leg_offset=5, arm_pose="SLASH")
    # Rastro brilhante da lâmina Iai em arco carmim
    arc_pts = [
        (cx + 12, FEET_Y - 42),
        (cx + 24, FEET_Y - 38),
        (cx + 36, FEET_Y - 32),
        (cx + 40, FEET_Y - 26),
    ]
    pygame.draw.lines(surf, KENSHI_AURA_RED, False, arc_pts, 4)
    pygame.draw.lines(surf, KENSHI_WHITE, False, arc_pts, 2)
    # Faíscas
    pygame.draw.circle(surf, KENSHI_GOLD, (cx + 38, FEET_Y - 28), 2)
    pygame.draw.circle(surf, KENSHI_WHITE, (cx + 41, FEET_Y - 25), 1)
    return surf

def build_kenshi_recovery():
    surf = create_surface()
    draw_kenshi_base(surf, SPRITE_W // 2, FEET_Y, state="RECOVERY", leg_offset=1, arm_pose="NOTO")
    return surf

def build_kenshi_stunned():
    surf = create_surface()
    cx = SPRITE_W // 2 - 4
    draw_kenshi_base(surf, cx, FEET_Y, state="STUNNED", leg_offset=-4, arm_pose="STUN")
    # Pequena estrela / impacto
    pygame.draw.circle(surf, KENSHI_GOLD, (cx + 4, FEET_Y - 48), 3)
    return surf

def build_kenshi_dead():
    surf = create_surface()
    cx = SPRITE_W // 2
    cy = FEET_Y
    # Silhueta horizontal caída com quimono carmim
    pygame.draw.ellipse(surf, (15, 12, 18, 120), (cx - 24, cy - 8, 48, 14)) # Sombra
    pygame.draw.rect(surf, KENSHI_HAKAMA_DARK, (cx - 16, cy - 9, 22, 9), border_radius=2)
    pygame.draw.rect(surf, KENSHI_KIMONO_RED, (cx + 4, cy - 10, 16, 8), border_radius=2)
    pygame.draw.circle(surf, KENSHI_HAIR, (cx + 20, cy - 7), 5)
    # Katana caída ao lado
    pygame.draw.line(surf, KENSHI_STEEL, (cx - 18, cy - 2), (cx + 2, cy - 2), 2)
    pygame.draw.circle(surf, KENSHI_GOLD, (cx + 3, cy - 2), 2)
    return surf

# ==============================================================================
# MURASAKI SPRITES
# ==============================================================================

def draw_murasaki_base(surf, cx, cy, state="IDLE", leg_offset=0, arm_pose="READY"):
    # 1. Pés e Meias Ninja Tabanashi
    foot_l_x = cx - 6 + leg_offset
    foot_r_x = cx + 5 - leg_offset
    foot_y = cy - 2
    pygame.draw.rect(surf, MURA_SUIT_DARK, (foot_l_x - 3, foot_y, 6, 3), border_radius=1)
    pygame.draw.rect(surf, MURA_SUIT_DARK, (foot_r_x - 3, foot_y, 6, 3), border_radius=1)
    # Tiras roxas na canela (Kyahan)
    pygame.draw.rect(surf, MURA_SUIT_PURPLE, (foot_l_x - 2, foot_y - 6, 5, 5))
    pygame.draw.rect(surf, MURA_SUIT_PURPLE, (foot_r_x - 2, foot_y - 6, 5, 5))

    # 2. Pernas e Quadris com Traje Furtivo de Couro Shinobi Roxo
    hip_y = cy - 22
    # Perna esquerda
    pygame.draw.polygon(surf, MURA_SUIT_PURPLE, [(cx - 6, hip_y), (cx - 1, hip_y), (foot_l_x + 1, foot_y - 6), (foot_l_x - 2, foot_y - 6)])
    # Perna direita
    pygame.draw.polygon(surf, MURA_SUIT_PURPLE, [(cx + 1, hip_y), (cx + 6, hip_y), (foot_r_x + 2, foot_y - 6), (foot_r_x - 1, foot_y - 6)])
    # Brilho de couro nas coxas
    pygame.draw.line(surf, MURA_SUIT_LIGHT, (cx - 4, hip_y + 4), (foot_l_x, foot_y - 8), 1)
    pygame.draw.line(surf, MURA_SUIT_LIGHT, (cx + 4, hip_y + 4), (foot_r_x, foot_y - 8), 1)

    # 3. Cintura e Faixa Ninja Púrpura (Obi)
    pygame.draw.rect(surf, MURA_SUIT_DARK, (cx - 6, hip_y - 4, 12, 5), border_radius=1)
    pygame.draw.rect(surf, MURA_SUIT_PURPLE, (cx - 5, hip_y - 3, 10, 3))

    # 4. Torso Shinobi e Colete com Proteção
    chest_y = cy - 35
    torso_pts = [(cx - 6, chest_y), (cx + 6, chest_y), (cx + 5, hip_y - 4), (cx - 5, hip_y - 4)]
    pygame.draw.polygon(surf, MURA_SUIT_DEEP, torso_pts)
    pygame.draw.polygon(surf, MURA_SUIT_PURPLE, [(cx - 4, chest_y + 2), (cx + 4, chest_y + 2), (cx + 3, hip_y - 4), (cx - 3, hip_y - 4)])
    # Ombreiras de aço laqueado negro com detalhes
    pygame.draw.circle(surf, MURA_ARMOR_STEEL, (cx - 7, chest_y + 2), 3)
    pygame.draw.circle(surf, MURA_ARMOR_STEEL, (cx + 7, chest_y + 2), 3)
    pygame.draw.circle(surf, MURA_ARMOR_HIGHLIGHT, (cx - 7, chest_y + 1), 1)
    pygame.draw.circle(surf, MURA_ARMOR_HIGHLIGHT, (cx + 7, chest_y + 1), 1)

    # 5. Braços e Kusarigama
    if arm_pose == "READY":
        # Braço esquerdo segurando a Foice (Kama)
        pygame.draw.line(surf, MURA_SUIT_PURPLE, (cx - 6, chest_y + 2), (cx - 12, cy - 26), 3)
        pygame.draw.circle(surf, MURA_ARMOR_STEEL, (cx - 12, cy - 26), 2)
        # Cabo e Lâmina curvada da Foice
        pygame.draw.line(surf, (20, 20, 24), (cx - 12, cy - 22), (cx - 12, cy - 34), 2)
        pygame.draw.line(surf, MURA_KAMA_STEEL, (cx - 12, cy - 34), (cx - 20, cy - 31), 3) # Lâmina da foice
        pygame.draw.circle(surf, MURA_AURA_PURPLE, (cx - 20, cy - 31), 1)
        # Braço direito segurando o peso de corrente
        pygame.draw.line(surf, MURA_SUIT_PURPLE, (cx + 6, chest_y + 2), (cx + 10, cy - 24), 3)
        pygame.draw.circle(surf, MURA_SKIN, (cx + 10, cy - 24), 2)
        # Corrente curvada suspensa
        chain_pts = [(cx - 12, cy - 22), (cx - 4, cy - 14), (cx + 6, cy - 16), (cx + 10, cy - 24)]
        pygame.draw.lines(surf, MURA_CHAIN, False, chain_pts, 2)
        # Peso de ferro esférico
        pygame.draw.circle(surf, (50, 54, 65), (cx + 14, cy - 22), 3)
    elif arm_pose == "SWING":
        # Foice girando no ar em arco violento
        pygame.draw.line(surf, MURA_SUIT_PURPLE, (cx - 6, chest_y + 2), (cx - 8, cy - 42), 3)
        pygame.draw.circle(surf, MURA_SKIN, (cx - 8, cy - 42), 2)
        # Lâmina no ápice
        pygame.draw.line(surf, (20, 20, 25), (cx - 8, cy - 42), (cx - 12, cy - 50), 2)
        pygame.draw.line(surf, MURA_KAMA_STEEL, (cx - 12, cy - 50), (cx - 4, cy - 54), 3)
        # Braço direito arremessando a corrente
        pygame.draw.line(surf, MURA_SUIT_PURPLE, (cx + 6, chest_y + 2), (cx + 16, cy - 28), 3)
        pygame.draw.circle(surf, MURA_SKIN, (cx + 16, cy - 28), 2)
        # Corrente chicoteando
        pygame.draw.line(surf, MURA_CHAIN, (cx + 16, cy - 28), (cx + 28, cy - 20), 2)
        pygame.draw.circle(surf, (50, 54, 65), (cx + 29, cy - 19), 4)
    elif arm_pose == "RECOVER":
        # Posição recolhendo a corrente
        pygame.draw.line(surf, MURA_SUIT_PURPLE, (cx - 6, chest_y + 2), (cx - 9, cy - 25), 3)
        pygame.draw.line(surf, MURA_SUIT_PURPLE, (cx + 6, chest_y + 2), (cx + 8, cy - 25), 3)
        pygame.draw.circle(surf, MURA_SKIN, (cx - 9, cy - 25), 2)
        pygame.draw.circle(surf, MURA_SKIN, (cx + 8, cy - 25), 2)
        pygame.draw.line(surf, (20, 20, 25), (cx - 9, cy - 22), (cx - 9, cy - 32), 2)
        pygame.draw.line(surf, MURA_KAMA_STEEL, (cx - 9, cy - 32), (cx - 15, cy - 29), 2)

    # 6. Cabeça e Máscara Shinobi
    head_y = cy - 42
    pygame.draw.circle(surf, MURA_SKIN, (cx, head_y), 5)
    # Máscara roxa cobrindo boca e nariz
    pygame.draw.polygon(surf, MURA_SUIT_PURPLE, [(cx - 4, head_y), (cx + 4, head_y), (cx + 3, head_y + 5), (cx - 3, head_y + 5)])
    pygame.draw.line(surf, MURA_SUIT_DARK, (cx - 4, head_y), (cx + 4, head_y), 1)
    # Olhos misteriosos e letais
    pygame.draw.line(surf, OUTLINE, (cx + 1, head_y - 2), (cx + 4, head_y - 2), 1)
    pygame.draw.circle(surf, MURA_AURA_PURPLE, (cx + 3, head_y - 2), 1)

    # 7. Cabelo Preto em Coque Duplo com Fitas Púrpuras
    # Coque no topo
    pygame.draw.circle(surf, MURA_HAIR, (cx - 2, head_y - 7), 4)
    pygame.draw.circle(surf, MURA_HAIR_HIGHLIGHT, (cx - 2, head_y - 8), 2)
    # Fita púrpura amarrando o coque
    pygame.draw.rect(surf, MURA_SUIT_PURPLE, (cx - 4, head_y - 6, 6, 2))
    # Fitas esvoaçantes para trás
    pygame.draw.line(surf, MURA_SUIT_LIGHT, (cx - 4, head_y - 5), (cx - 10, head_y - 3), 2)
    pygame.draw.line(surf, MURA_SUIT_LIGHT, (cx - 10, head_y - 3), (cx - 15, head_y + 2), 1)
    # Mechas laterais descendo pelo ombro
    pygame.draw.line(surf, MURA_HAIR, (cx - 4, head_y - 4), (cx - 5, head_y + 3), 2)
    pygame.draw.line(surf, MURA_HAIR, (cx + 3, head_y - 4), (cx + 4, head_y + 1), 1)

def build_murasaki_idle():
    surf = create_surface()
    draw_murasaki_base(surf, SPRITE_W // 2, FEET_Y, state="IDLE", leg_offset=0, arm_pose="READY")
    return surf

def build_murasaki_walk(frame=0):
    surf = create_surface()
    offset = 2 if frame == 0 else -2
    draw_murasaki_base(surf, SPRITE_W // 2, FEET_Y, state="WALK", leg_offset=offset, arm_pose="READY")
    return surf

def build_murasaki_attack():
    surf = create_surface()
    cx = SPRITE_W // 2
    draw_murasaki_base(surf, cx, FEET_Y, state="ATTACK", leg_offset=4, arm_pose="SWING")
    # Arco crescente magnífico do corte da foice púrpura (como no mockup!)
    arc_pts = [
        (cx - 16, FEET_Y - 54),
        (cx - 4, FEET_Y - 60),
        (cx + 14, FEET_Y - 58),
        (cx + 28, FEET_Y - 48),
        (cx + 34, FEET_Y - 34),
        (cx + 26, FEET_Y - 20),
    ]
    pygame.draw.lines(surf, MURA_AURA_PURPLE, False, arc_pts, 4)
    pygame.draw.lines(surf, (255, 230, 255), False, arc_pts, 2)
    # Faíscas púrpuras
    pygame.draw.circle(surf, MURA_AURA_PURPLE, (cx + 32, FEET_Y - 42), 2)
    pygame.draw.circle(surf, (255, 255, 255), (cx + 35, FEET_Y - 30), 1)
    pygame.draw.circle(surf, MURA_AURA_PURPLE, (cx + 22, FEET_Y - 16), 2)
    return surf

def build_murasaki_recovery():
    surf = create_surface()
    draw_murasaki_base(surf, SPRITE_W // 2, FEET_Y, state="RECOVERY", leg_offset=1, arm_pose="RECOVER")
    return surf

def build_murasaki_stunned():
    surf = create_surface()
    cx = SPRITE_W // 2 - 3
    draw_murasaki_base(surf, cx, FEET_Y, state="STUNNED", leg_offset=-3, arm_pose="READY")
    pygame.draw.circle(surf, MURA_AURA_PURPLE, (cx + 4, FEET_Y - 46), 3)
    return surf

def build_murasaki_dead():
    surf = create_surface()
    cx = SPRITE_W // 2
    cy = FEET_Y
    # Silhueta horizontal caída shinobi no chão
    pygame.draw.ellipse(surf, (15, 12, 18, 120), (cx - 22, cy - 8, 44, 14)) # Sombra
    pygame.draw.rect(surf, MURA_SUIT_DARK, (cx - 14, cy - 8, 26, 7), border_radius=2)
    pygame.draw.circle(surf, MURA_HAIR, (cx + 15, cy - 6), 5)
    # Kusarigama caída
    pygame.draw.line(surf, MURA_CHAIN, (cx - 18, cy - 2), (cx - 6, cy - 2), 1)
    pygame.draw.circle(surf, (50, 54, 65), (cx - 19, cy - 2), 3)
    return surf

# ==============================================================================
# SALVAR ARQUIVOS
# ==============================================================================

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kenshi_dir = os.path.join(base_dir, "assets", "sprites", "kenshi")
    mura_dir = os.path.join(base_dir, "assets", "sprites", "murasaki")
    os.makedirs(kenshi_dir, exist_ok=True)
    os.makedirs(mura_dir, exist_ok=True)

    sprites_to_build = [
        # Kenshi
        (os.path.join(kenshi_dir, "idle.png"), build_kenshi_idle),
        (os.path.join(kenshi_dir, "walk_0.png"), lambda: build_kenshi_walk(0)),
        (os.path.join(kenshi_dir, "walk_1.png"), lambda: build_kenshi_walk(1)),
        (os.path.join(kenshi_dir, "attack.png"), build_kenshi_attack),
        (os.path.join(kenshi_dir, "recovery.png"), build_kenshi_recovery),
        (os.path.join(kenshi_dir, "stunned.png"), build_kenshi_stunned),
        (os.path.join(kenshi_dir, "dead.png"), build_kenshi_dead),

        # Murasaki
        (os.path.join(mura_dir, "idle.png"), build_murasaki_idle),
        (os.path.join(mura_dir, "walk_0.png"), lambda: build_murasaki_walk(0)),
        (os.path.join(mura_dir, "walk_1.png"), lambda: build_murasaki_walk(1)),
        (os.path.join(mura_dir, "attack.png"), build_murasaki_attack),
        (os.path.join(mura_dir, "recovery.png"), build_murasaki_recovery),
        (os.path.join(mura_dir, "stunned.png"), build_murasaki_stunned),
        (os.path.join(mura_dir, "dead.png"), build_murasaki_dead),
    ]

    for path, func in sprites_to_build:
        surf = func()
        pygame.image.save(surf, path)
        print(f"Salvo: {os.path.relpath(path, base_dir)} ({surf.get_width()}x{surf.get_height()})")

    print(f"\n[OK] Todos os {len(sprites_to_build)} sprites HD-2D foram gerados com sucesso!")

if __name__ == "__main__":
    main()
