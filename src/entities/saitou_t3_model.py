"""
src/entities/saitou_t3_model.py - Saitou (Técnica 3: Voxel Base + Overlays 2.5D / Decalques)

Combina a base de micro-voxels do Capitão Shinsengumi de T1 com Overlays 2.5D:
- Base física sólida de micro-voxels: postura Gatotsu mortal, katana longa com tsuba,
  haori azul-celeste com padrão dandara nas barras e mangas, penteado chonmage samurai.
- Decalque 2.5D Frontal: Rosto severo do Lobo de Mibu com olhar afiado e bandô branco.
- Decalque 2.5D Dorsal: O lendário brasão do Shinsengumi "Makoto" (誠 - Fidelidade)
  em branco puro com moldura circular nas costas do haori azul-celeste!
- Verificação angular da normal: o brasão dorsal 'Makoto' aparece exclusivamente
  na vista traseira da câmera orbital, e o rosto na vista frontal.
"""
import math
import pygame

from src.isometric.decal_renderer import (
    draw_decal_billboard,
    get_decal_saitou_face,
    get_decal_saitou_makoto
)
from src.entities.saitou_t1_model import render_saitou_t1


def render_saitou_t3(c):
    """
    Renderiza Saitou na Técnica 3:
    1. Renderiza a base sólida de micro-voxels T1 (estabilidade 360°).
    2. Aplica Overlays 2.5D de alta fidelidade ancorados nos membros.
    """
    # 1. Base volumétrica 3D de micro-voxels (sem distorções afins)
    render_saitou_t1(c)

    fx, fy = c.fx, c.fy
    bx, by = c.base_x, c.base_y
    tz = c.torso_z
    hz = c.head_z

    norm_front = (fx, fy)
    norm_back  = (-fx, -fy)

    # 2. OVERLAY ROSTO SEVERO DO LOBO DE MIBU (ancorado na frente da cabeça)
    head_front_x = bx + fx * 0.09
    head_front_y = by + fy * 0.09
    head_front_z = hz + 0.12

    draw_decal_billboard(
        c.surface, c.camera,
        wx=head_front_x, wy=head_front_y, wz=head_front_z,
        decal_surf=get_decal_saitou_face(),
        normal_dir=norm_front,
        scale=0.64,
        alpha=c.alpha,
        facing_threshold=0.10
    )

    # 3. OVERLAY DORSAL: BRASÃO SHINSENGUMI "MAKOTO" (誠)
    # Ancorado no centro das costas do haori azul-celeste
    back_x = bx - fx * 0.11
    back_y = by - fy * 0.11
    back_z = tz + 0.14

    draw_decal_billboard(
        c.surface, c.camera,
        wx=back_x, wy=back_y, wz=back_z,
        decal_surf=get_decal_saitou_makoto(),
        normal_dir=norm_back,
        scale=0.82,
        alpha=c.alpha,
        facing_threshold=0.10
    )
