"""
src/entities/kasumi_t3_model.py - Kasumi (Técnica 3: Voxel Base + Overlays 2.5D / Decalques)

Combina a base de micro-voxels anatômica de T1 com Overlays 2.5D de alta fidelidade:
- Base física sólida de micro-voxels: máscara volumétrica, colete com profundidade,
  cachecol dinâmico em cascata e adagas duplas com sulco fuller.
- Decalque 2.5D do Rosto Shinobi: protetor de testa cromado reluzente com rebites,
  olhos azuis-gelo afiados e penetrantes com reflexo especular e trama da máscara.
- Decalque 2.5D do Colete Tático: 4 fivelas cromadas de alta definição com reflexos
  metálicos especulares sobre correias de couro.
- Verificação angular da normal: visíveis apenas na vista frontal/lateral e ocultos nas costas.
"""
import math
import pygame

from src.isometric.decal_renderer import (
    draw_decal_billboard,
    get_decal_kasumi_mask,
    get_decal_kasumi_buckles
)
from src.entities.kasumi_t1_model import render_kasumi_t1


def render_kasumi_t3(c):
    """
    Renderiza Kasumi na Técnica 3:
    1. Renderiza a base sólida de micro-voxels T1.
    2. Aplica Overlays 2.5D de alta fidelidade ancorados nos membros.
    """
    # 1. Base volumétrica 3D de micro-voxels (sem distorções afins)
    render_kasumi_t1(c)

    fx, fy = c.fx, c.fy
    bx, by = c.base_x, c.base_y
    tz = c.torso_z
    hz = c.head_z

    norm_front = (fx, fy)

    # 2. OVERLAY ROSTO SHINOBI & OLHOS AZUIS-GELO (ancorado na frente da cabeça)
    head_front_x = bx + fx * 0.08
    head_front_y = by + fy * 0.08
    head_front_z = hz + 0.11

    draw_decal_billboard(
        c.surface, c.camera,
        wx=head_front_x, wy=head_front_y, wz=head_front_z,
        decal_surf=get_decal_kasumi_mask(),
        normal_dir=norm_front,
        scale=0.64,
        alpha=c.alpha,
        facing_threshold=0.10
    )

    # 3. OVERLAY DAS 4 FIVELAS CROMADAS (ancorado no centro do colete-espartilho)
    chest_x = bx + fx * 0.11
    chest_y = by + fy * 0.11
    chest_z = tz + 0.10

    draw_decal_billboard(
        c.surface, c.camera,
        wx=chest_x, wy=chest_y, wz=chest_z,
        decal_surf=get_decal_kasumi_buckles(),
        normal_dir=norm_front,
        scale=0.68,
        alpha=c.alpha,
        facing_threshold=0.12
    )
