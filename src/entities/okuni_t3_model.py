"""
src/entities/okuni_t3_model.py - Okuni (Técnica 3: Voxel Base + Overlays 2.5D / Decalques)

Combina o melhor dos dois mundos:
1. Base volumétrica 3D física de micro-voxels (a mesma aprovada em T1, com tronco contínuo,
   sem deformação angular ao girar a câmera em 360° e com depth sorting perfeito).
2. Decalques e Overlays 2.5D de alta definição ancorados na anatomia:
   - Maquiagem kabuki refinada nos olhos e lábios com reflexo de laca brilhante.
   - Kamon imperial floral em ouro nos painéis do quimono.
   - Broche de jade esmeralda no fecho central do Obi.
   - Sol nascente radiante dourado com ondas marinhas seigaiha no centro dos leques Tessen.
   - Verificação angular da normal da face para garantir que decalques frontais
     nunca apareçam nas costas e vice-versa.
"""
import math
import pygame

from src.isometric.decal_renderer import (
    draw_decal_billboard,
    get_decal_okuni_face,
    get_decal_okuni_kamon,
    get_decal_okuni_brooch,
    get_decal_okuni_fan
)
from src.entities.okuni_t1_model import (
    render_okuni_t1,
    depth
)


def render_okuni_t3(c):
    """
    Renderiza Okuni na Técnica 3:
    1. Renderiza a escultura volumétrica sólida de micro-voxels T1 (estabilidade 360°).
    2. Aplica Overlays 2.5D semi-transparentes de alta fidelidade ancorados nos membros.
    """
    # 1. Renderiza a base sólida de micro-voxels
    render_okuni_t1(c)

    # Vetores de orientação do personagem
    fx, fy = c.fx, c.fy
    bx, by = c.base_x, c.base_y
    tz = c.torso_z
    hz = c.head_z

    # Normal apontando para frente do personagem
    norm_front = (fx, fy)

    # 2. OVERLAY ROSTO KABUKI (ancorado na face frontal da cabeça)
    head_front_x = bx + fx * 0.08
    head_front_y = by + fy * 0.08
    head_front_z = hz + 0.11

    draw_decal_billboard(
        c.surface, c.camera,
        wx=head_front_x, wy=head_front_y, wz=head_front_z,
        decal_surf=get_decal_okuni_face(),
        normal_dir=norm_front,
        scale=0.62,
        alpha=c.alpha,
        facing_threshold=0.10
    )

    # 3. OVERLAY KAMON IMPERIAL DOURADO (ancorado no peito do quimono)
    chest_x = bx + fx * 0.11
    chest_y = by + fy * 0.11
    chest_z = tz + 0.13

    draw_decal_billboard(
        c.surface, c.camera,
        wx=chest_x, wy=chest_y, wz=chest_z,
        decal_surf=get_decal_okuni_kamon(),
        normal_dir=norm_front,
        scale=0.52,
        alpha=c.alpha,
        facing_threshold=0.12
    )

    # 4. OVERLAY BROCHE DE JADE NO OBI (ancorado no fecho frontal da cintura)
    obi_x = bx + fx * 0.13
    obi_y = by + fy * 0.13
    obi_z = tz + 0.01

    draw_decal_billboard(
        c.surface, c.camera,
        wx=obi_x, wy=obi_y, wz=obi_z,
        decal_surf=get_decal_okuni_brooch(),
        normal_dir=norm_front,
        scale=0.85,
        alpha=c.alpha,
        facing_threshold=0.12
    )

    # 5. OVERLAY DO LEQUE TESSEN (ancorado na posição do leque de aço)
    # Braço direito empunhando leque
    yaw = math.atan2(fy, fx) - math.pi * 0.25
    fan_x = bx + 0.22 * math.cos(yaw + 0.8) + fx * 0.12
    fan_y = by + 0.22 * math.sin(yaw + 0.8) + fy * 0.12
    fan_z = tz + 0.28

    # O leque é desenhado quando voltado para o observador
    draw_decal_billboard(
        c.surface, c.camera,
        wx=fan_x, wy=fan_y, wz=fan_z,
        decal_surf=get_decal_okuni_fan(),
        normal_dir=norm_front,
        scale=0.95,
        alpha=c.alpha,
        facing_threshold=-0.15
    )
