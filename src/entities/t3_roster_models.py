"""
src/entities/t3_roster_models.py - Gerenciador Unificado da Técnica 3 (Voxel Base + Overlays 2.5D)

Fornece renderização completa da Técnica 3 para todo o elenco dos 12 combatentes:
1. Okuni (Dançarina Kabuki)
2. Kasumi (Kunoichi da Névoa)
3. Saitou (Capitão Shinsengumi)
4. Kenshi (Espadachim Iaijutsu)
5. Musashi (Mestre Niten Ichi-ryu)
6. Hanzo (Shinobi de Iga)
7. Murasaki (Kunoichi Kusarigama)
8. Tomoe (Arqueira Miko)
9. Teppo (Atirador Tanegashima)
10. Joe (American Ninja)
11. Anne (Capitã Pirata)
12. Julie (Mosqueteira)

Estruturado para permitir migração direta e indolor para as arenas do jogo principal.
"""
import math
import pygame

from src.isometric.decal_renderer import (
    draw_decal_billboard,
    get_or_create_decal
)
from src.entities.okuni_t3_model import render_okuni_t3
from src.entities.kasumi_t3_model import render_kasumi_t3
from src.entities.saitou_t3_model import render_saitou_t3
from src.entities.voxel_models import render_voxel_humanoid


# =============================================================================
# DECALQUES ESPECÍFICOS PARA OS DEMAIS 9 COMBATENTES
# =============================================================================

def _build_kenshi_ribbon(surf: pygame.Surface):
    """Fita de seda carmim esvoaçante e laço no obi de Kenshi."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2
    pygame.draw.ellipse(surf, (220, 35, 50, 240), (cx - 10, cy - 6, 20, 12))
    pygame.draw.circle(surf, (245, 200, 60, 255), (cx, cy), 3)


def _build_musashi_scar(surf: pygame.Surface):
    """Cicatriz e olhar indomável de Musashi."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2
    # Hachimaki branco com manchas de batalha
    pygame.draw.rect(surf, (245, 245, 250, 250), (cx - 12, cy - 10, 24, 5))
    # Olhos severos
    pygame.draw.line(surf, (20, 18, 24, 255), (cx - 9, cy - 3), (cx - 3, cy - 3), 2)
    pygame.draw.line(surf, (20, 18, 24, 255), (cx + 3, cy - 3), (cx + 9, cy - 3), 2)
    # Cicatriz de duelo
    pygame.draw.line(surf, (180, 50, 40, 220), (cx - 4, cy - 6), (cx + 2, cy + 6), 2)


def _build_hanzo_oni_mask(surf: pygame.Surface):
    """Máscara de ferro de demônio (Menpo/Hanya) de Hanzo com dentes e chifres dourados."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2
    # Base de ferro escuro da máscara
    pygame.draw.polygon(surf, (30, 32, 38, 245), [
        (cx - 12, cy - 4), (cx + 12, cy - 4), (cx + 8, cy + 12), (cx - 8, cy + 12)
    ])
    # Dentes dourados afiados de demônio
    for i in range(4):
        x = cx - 6 + i * 4
        pygame.draw.polygon(surf, (235, 195, 60, 255), [(x, cy + 3), (x + 3, cy + 3), (x + 1, cy + 7)])


def _build_murasaki_mask(surf: pygame.Surface):
    """Máscara púrpura refinada e olhos de Kunoichi de Murasaki."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2
    # Máscara púrpura
    pygame.draw.polygon(surf, (120, 45, 175, 240), [
        (cx - 12, cy - 2), (cx + 12, cy - 2), (cx + 7, cy + 11), (cx - 7, cy + 11)
    ])
    # Olhos expressivos com brilho lilás
    pygame.draw.ellipse(surf, (20, 15, 25, 255), (cx - 10, cy - 5, 6, 3))
    pygame.draw.ellipse(surf, (20, 15, 25, 255), (cx + 4, cy - 5, 6, 3))
    pygame.draw.circle(surf, (220, 140, 255, 255), (cx - 7, cy - 4), 1)
    pygame.draw.circle(surf, (220, 140, 255, 255), (cx + 7, cy - 4), 1)


def _build_tomoe_miko(surf: pygame.Surface):
    """Tiara cerimonial Miko e pintura facial sagrada da arqueira Tomoe."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2
    # Fita vermelha na testa
    pygame.draw.rect(surf, (210, 35, 45, 250), (cx - 12, cy - 10, 24, 4))
    # Pingente de jade sagrado
    pygame.draw.circle(surf, (65, 185, 150, 255), (cx, cy - 8), 2)
    # Marcas vermelhas nas têmporas
    pygame.draw.circle(surf, (220, 40, 50, 220), (cx - 9, cy - 2), 2)
    pygame.draw.circle(surf, (220, 40, 50, 220), (cx + 9, cy - 2), 2)


def _build_teppo_crest(surf: pygame.Surface):
    """Brasão do clã no chapéu Jingasa de ferro do atirador Tanegashima."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2
    # Brasão circular dourado
    pygame.draw.circle(surf, (245, 205, 65, 245), (cx, cy), 9, 2)
    pygame.draw.line(surf, (245, 205, 65, 245), (cx - 6, cy), (cx + 6, cy), 2)
    pygame.draw.line(surf, (245, 205, 65, 245), (cx, cy - 6), (cx, cy + 6), 2)


def _build_anne_pirate_buckle(surf: pygame.Surface):
    """Fivela de ouro do chapéu tricórnio e insígnia da pirata Anne."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2
    pygame.draw.rect(surf, (245, 205, 60, 255), (cx - 8, cy - 6, 16, 12), 2, border_radius=2)
    pygame.draw.circle(surf, (255, 60, 70, 240), (cx, cy), 3)


def _build_julie_fleur_de_lis(surf: pygame.Surface):
    """Flor-de-lis dourada real francesa da mosqueteira Julie."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2
    gold = (245, 205, 60, 255)
    # Pétala central
    pygame.draw.polygon(surf, gold, [(cx, cy - 10), (cx - 3, cy), (cx + 3, cy)])
    # Pétalas laterais curvadas
    pygame.draw.arc(surf, gold, (cx - 10, cy - 8, 8, 12), 0, math.pi * 1.5, 2)
    pygame.draw.arc(surf, gold, (cx + 2, cy - 8, 8, 12), math.pi * 1.5, math.pi * 3, 2)
    # Barra horizontal
    pygame.draw.line(surf, gold, (cx - 7, cy + 2), (cx + 7, cy + 2), 2)


# =============================================================================
# DESPACHADOR T3 PARA QUALQUER COMBATENTE
# =============================================================================

def render_character_t3(c, char_type: str):
    """
    Renderiza qualquer um dos 12 personagens na Técnica 3 (Voxel Base + Overlays 2.5D).
    Garante portabilidade imediata para o jogo principal.
    """
    char_type = char_type.lower()

    # 1. Os 3 combatentes com modelos dedicados de altíssima fidelidade
    if "okuni" in char_type or "kabuki" in char_type:
        render_okuni_t3(c)
        return
    elif "kasumi" in char_type or "gray" in char_type or "kemuri" in char_type:
        render_kasumi_t3(c)
        return
    elif "saitou" in char_type or "saito" in char_type:
        render_saitou_t3(c)
        return

    # 2. Demais combatentes: renderiza a base volumétrica voxel rica do jogo
    render_voxel_humanoid(
        c.surface, c.camera,
        wx=c.base_x, wy=c.base_y, wz=0.0,
        facing_x=c.fx, facing_y=c.fy,
        state=c.state, state_timer=c.state_timer,
        is_alive=True, char_type=char_type,
        walk_timer=c.walk_timer, alpha=c.alpha,
        is_moving=c.is_moving, extra_props=c.extra_props
    )

    # 3. Sobrepõe os Overlays 2.5D específicos ancorados na anatomia do personagem
    fx, fy = c.fx, c.fy
    bx, by = c.base_x, c.base_y
    tz = c.torso_z
    hz = c.head_z
    norm_front = (fx, fy)

    if "kenshi" in char_type or "kenshin" in char_type or "red" in char_type:
        decal = get_or_create_decal("kenshi_ribbon_t3", 26, 26, _build_kenshi_ribbon)
        draw_decal_billboard(c.surface, c.camera, bx + fx * 0.10, by + fy * 0.10, tz + 0.05,
                             decal, norm_front, scale=0.72, alpha=c.alpha)

    elif "musashi" in char_type or "blue" in char_type:
        decal = get_or_create_decal("musashi_scar_t3", 32, 32, _build_musashi_scar)
        draw_decal_billboard(c.surface, c.camera, bx + fx * 0.08, by + fy * 0.08, hz + 0.10,
                             decal, norm_front, scale=0.68, alpha=c.alpha)

    elif "hanzo" in char_type or "ninja" in char_type:
        decal = get_or_create_decal("hanzo_mask_t3", 32, 32, _build_hanzo_oni_mask)
        draw_decal_billboard(c.surface, c.camera, bx + fx * 0.08, by + fy * 0.08, hz + 0.09,
                             decal, norm_front, scale=0.70, alpha=c.alpha)

    elif "murasaki" in char_type or "purple" in char_type:
        decal = get_or_create_decal("murasaki_mask_t3", 32, 32, _build_murasaki_mask)
        draw_decal_billboard(c.surface, c.camera, bx + fx * 0.08, by + fy * 0.08, hz + 0.10,
                             decal, norm_front, scale=0.68, alpha=c.alpha)

    elif "tomoe" in char_type or "archer" in char_type:
        decal = get_or_create_decal("tomoe_miko_t3", 32, 32, _build_tomoe_miko)
        draw_decal_billboard(c.surface, c.camera, bx + fx * 0.08, by + fy * 0.08, hz + 0.11,
                             decal, norm_front, scale=0.68, alpha=c.alpha)

    elif "rifle" in char_type or "teppo" in char_type:
        decal = get_or_create_decal("teppo_crest_t3", 28, 28, _build_teppo_crest)
        draw_decal_billboard(c.surface, c.camera, bx + fx * 0.10, by + fy * 0.10, hz + 0.18,
                             decal, norm_front, scale=0.75, alpha=c.alpha)

    elif "pirate" in char_type or "anne" in char_type:
        decal = get_or_create_decal("anne_buckle_t3", 26, 26, _build_anne_pirate_buckle)
        draw_decal_billboard(c.surface, c.camera, bx + fx * 0.09, by + fy * 0.09, hz + 0.17,
                             decal, norm_front, scale=0.75, alpha=c.alpha)

    elif "musketeer" in char_type or "julie" in char_type:
        decal = get_or_create_decal("julie_fleur_t3", 28, 28, _build_julie_fleur_de_lis)
        draw_decal_billboard(c.surface, c.camera, bx + fx * 0.11, by + fy * 0.11, tz + 0.12,
                             decal, norm_front, scale=0.70, alpha=c.alpha)
