"""
src/entities/microvoxel_roster.py - Motor Unificado de Micro-voxels 3D para Todos os Combatentes

Centraliza e padroniza a renderização em Micro-voxels 3D de alta fidelidade visual
para os 12 combatentes do elenco de Samurai Edge:
  1. Okuni (Dançarina Kabuki) -> okuni_t1_model
  2. Kasumi (Kunoichi da Névoa) -> kasumi_t1_model
  3. Saitou (Capitão Shinsengumi) -> saitou_t1_model
  4. Kenshi (Espadachim Iaijutsu Carmim) -> kenshi_t1_model
  5. Musashi (Mestre Niten Ichi-ryu de Duas Lâminas) -> musashi_t1_model
  6. Hanzo (Mestre Ninja de Iga & Máscara Oni Menpo)
  7. Murasaki (Kunoichi de Foice Kusarigama com Corrente)
  8. Tomoe (Arqueira Sagrada Miko & Arco Yumi Longo)
  9. Teppo (Atirador Tanegashima Ashigaru com Chapéu Jingasa)
 10. Joe (American Ninja Tático & Camuflagem Militar)
 11. Anne (Capitã Pirata dos Sete Mares & Alfanje Cortante)
 12. Julie (Mosqueteira Real Francesa & Florete de Esgrima)

Resolução de nomes robusta com suporte aos nomes oficiais e apelidos legados.
Totalmente desacoplado e pronto para migração direta nas arenas e no Model Viewer.
"""
import math
from types import SimpleNamespace
import pygame

from src.config import COLOR_WHITE, COLOR_BLACK, COLOR_GOLD
from src.isometric.iso_math import rotate_xy
from src.isometric.voxel_rig import calc_leg_joints
from src.isometric.voxel_renderer import draw_voxel_box, draw_oriented_voxel_box
from src.entities.okuni_t1_model import render_okuni_t1
from src.entities.kasumi_t1_model import render_kasumi_t1
from src.entities.saitou_t1_model import render_saitou_t1
from src.entities.kenshi_t1_model import render_kenshi_t1
from src.entities.musashi_t1_model import render_musashi_t1


def _box(c, x, y, z, w, d, h, color, outline=True, texture=None):
    """Desenha paralelepípedo voxel alinhado nos eixos mundiais."""
    draw_voxel_box(c.surface, c.camera, x, y, z, w, d, h, color, outline=outline, alpha=c.alpha, texture=texture)


def _cbox(c, cx, cy, z, w, d, h, color, outline=True, texture=None):
    """Desenha caixa voxel centrada nas coordenadas (cx, cy)."""
    draw_voxel_box(c.surface, c.camera, cx - w * 0.5, cy - d * 0.5, z, w, d, h, color, outline=outline, alpha=c.alpha, texture=texture)


def _obox(c, *args, **kwargs):
    """Desenha paralelepípedo de micro-voxel orientado."""
    if len(args) >= 2 and isinstance(args[0], (tuple, list)):
        ox, oy, oz = args[0]
        direction = args[1]
        length = args[2] if len(args) > 2 else kwargs.get("length")
        width = args[3] if len(args) > 3 else kwargs.get("width")
        height = args[4] if len(args) > 4 else kwargs.get("height")
        color = args[5] if len(args) > 5 else kwargs.get("color")
    else:
        ox, oy, oz = args[0], args[1], args[2]
        direction = args[3]
        length = args[4] if len(args) > 4 else kwargs.get("length")
        width = args[5] if len(args) > 5 else kwargs.get("width")
        height = args[6] if len(args) > 6 else kwargs.get("height")
        color = args[7] if len(args) > 7 else kwargs.get("color")

    up = kwargs.get("up", (0.0, 0.0, 1.0))
    outline = kwargs.get("outline", True)
    texture = kwargs.get("texture", None)
    draw_oriented_voxel_box(c.surface, c.camera, ox, oy, oz, direction[0], direction[1], direction[2],
                            length, width, height, color, up_x=up[0], up_y=up[1], up_z=up[2],
                            outline=outline, alpha=c.alpha, texture=texture)


def _draw_shadow(c):
    """Sombra de solo elíptica de contato."""
    sx0, sy0 = c.camera.apply(c.base_x, c.base_y, 0.0)
    shadow_w = int(24 * c.camera.zoom)
    shadow_h = int(12 * c.camera.zoom)
    shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (15, 12, 18, 120), (0, 0, shadow_w * 2, shadow_h * 2))
    c.surface.blit(shadow_surf, (sx0 - shadow_w, sy0 - shadow_h // 2))


def _ensure_legs(c):
    if not hasattr(c, "legs_data") or not c.legs_data:
        c.legs_data = calc_leg_joints(
            c.base_x, c.base_y, c.base_z, c.fx, c.fy, c.px, c.py,
            c.is_moving, c.walk_timer, c.is_melee, c.atk_progress,
            hip_width=0.075 if c.is_female else 0.09,
            is_female=c.is_female, char_type=c.char_type
        )


def _draw_humanoid_legs(c, color_pants, color_shin=None, color_shoe=(160, 140, 110), texture="silk", shin_texture=None):
    """Desenha pernas anatômicas articuladas usando o rig cinemático com suporte a texturas procedurais."""
    _ensure_legs(c)
    shin_c = color_shin if color_shin else color_pants
    shin_tex = shin_texture if shin_texture is not None else texture

    for side in ("L", "R"):
        ld = c.legs_data[side]
        th_pos = ld["thigh"]
        sh_pos = ld["shin"]
        ft_pos = ld["foot"]

        # Coxa
        _box(c, th_pos[0] - 0.065, th_pos[1] - 0.065, th_pos[2], 0.130, 0.130, 0.200, color_pants, texture=texture)

        # Canela / Joelho (permite botas de couro polido ou caneleiras metálicas)
        _box(c, sh_pos[0] - 0.050, sh_pos[1] - 0.050, sh_pos[2], 0.100, 0.100, 0.180, shin_c, texture=shin_tex)

        # Pé / Sandália / Bota
        shoe_tex = "leather" if color_shoe in ((35, 38, 42), (32, 22, 18), (48, 30, 20), (18, 18, 22), (20, 14, 28)) else None
        _box(c, ft_pos[0] - 0.038 + c.fx * 0.025, ft_pos[1] - 0.038 + c.fy * 0.025, ft_pos[2], 0.076, 0.076, 0.045, color_shoe, outline=True, texture=shoe_tex)


# =============================================================================
# HELPER: CONSTRUÇÃO DE CONTEXTO CINEMÁTICO COMPATÍVEL
# =============================================================================
def build_fighter_context(
    surface: pygame.Surface,
    camera,
    wx: float, wy: float, wz: float,
    facing_x: float, facing_y: float,
    state: str = "IDLE",
    state_timer: float = 0.0,
    is_alive: bool = True,
    char_type: str = "okuni",
    walk_timer: float = 0.0,
    alpha: int = 255,
    is_moving: bool = False
) -> SimpleNamespace:
    """
    Constrói e normaliza o contexto cinemático necessário para renderizar
    qualquer combatente em Micro-voxels 3D, facilitando a migração para Samurai.render().
    """
    norm = math.hypot(facing_x, facing_y)
    if norm > 0.001:
        fx = facing_x / norm
        fy = facing_y / norm
    else:
        fx, fy = 1.0, 1.0

    px = -fy
    py = fx

    is_female = char_type in ("okuni", "kasumi", "murasaki", "tomoe", "anne", "julie")

    is_melee = (state in ("ATTACK", "SHUKUCHI", "DASH"))
    atk_progress = min(1.0, state_timer / 0.35) if is_melee else 0.0
    lunge_curve = math.sin(atk_progress * math.pi) if is_melee else 0.0

    lunge_dist = lunge_curve * 0.16
    base_x = wx + fx * lunge_dist
    base_y = wy + fy * lunge_dist
    base_z = wz

    pelvis_z = base_z + (0.34 if is_female else 0.36)
    pelvis_w = 0.12 if is_female else 0.14
    torso_z = pelvis_z + 0.13
    neck_z = torso_z + 0.26
    head_z = torso_z + 0.31

    legs_data = calc_leg_joints(
        base_x, base_y, base_z, fx, fy, px, py,
        is_moving, walk_timer, is_melee, atk_progress,
        hip_width=0.075 if is_female else 0.09,
        is_female=is_female, char_type=char_type
    )

    c = SimpleNamespace(
        surface=surface,
        camera=camera,
        alpha=alpha,
        azimuth=getattr(camera, "azimuth", 0.0),
        elevation=getattr(camera, "elevation", math.radians(30)),
        base_x=base_x,
        base_y=base_y,
        base_z=base_z,
        fx=fx,
        fy=fy,
        px=px,
        py=py,
        pelvis_z=pelvis_z,
        pelvis_w=pelvis_w,
        torso_z=torso_z,
        neck_z=neck_z,
        head_z=head_z,
        head_w=0.13 if is_female else 0.15,
        sh_span=0.14 if is_female else 0.17,
        legs_data=legs_data,
        walk_timer=walk_timer,
        is_moving=is_moving,
        is_melee=is_melee,
        atk_progress=atk_progress,
        lunge_curve=lunge_curve,
        state=state,
        state_timer=state_timer,
        is_alive=is_alive,
        is_female=is_female,
        char_type=char_type,
        extra_props={}
    )
    return c


# =============================================================================
# MICRO-VOXELS: 6. HANZO (MESTRE NINJA DE IGA & MÁSCARA ONI)
# =============================================================================
# MICRO-VOXELS: 6. HANZO (MESTRE NINJA DE IGA & MÁSCARA ONI MENPO)
# =============================================================================
def _render_hanzo_microvoxel(c: SimpleNamespace):
    """Hanzo: Shinobi lendário de Iga com máscara Menpo demoníaca, 2 kunais e katana nas costas."""
    _draw_shadow(c)
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    tz = c.torso_z
    pz = c.pelvis_z

    # 1. Pernas articuladas com amarras Shinobi nos tornozelos
    _draw_humanoid_legs(c, (28, 26, 32), (20, 20, 24), (18, 18, 22), texture="silk")

    # 2. Torso contínuo com Traje Dourado/Mostarda e Colete de Malha
    torso_bottom = pz + 0.04
    torso_top = tz + 0.26
    _box(c, bx - 0.12, by - 0.09, torso_bottom, 0.24, 0.18, torso_top - torso_bottom, (205, 155, 32), texture="silk")
    # Colete de malha escuro transpassado
    _box(c, bx + fx * 0.04 - 0.08, by + fy * 0.04 - 0.08, tz + 0.02, 0.16, 0.16, 0.20, (38, 38, 44), outline=False)
    # Faixa Obi preta com amarração
    _box(c, bx - 0.122, by - 0.092, pz + 0.06, 0.244, 0.184, 0.07, (22, 22, 26), outline=True)

    # 3. Espada Ninja-to diagonal nas costas (Saya com Tsuka)
    blade_pos = (bx - fx * 0.10 - px * 0.04, by - fy * 0.10 - py * 0.04, tz + 0.06)
    _obox(c, blade_pos, (px * 0.72 - fx * 0.15, py * 0.72 - fy * 0.15, 0.68),
          length=0.48, width=0.042, height=0.042, color=(22, 22, 26), outline=True)
    _obox(c, (blade_pos[0] + px * 0.32, blade_pos[1] + py * 0.32, blade_pos[2] + 0.28),
          (px * 0.72 - fx * 0.15, py * 0.72 - fy * 0.15, 0.68),
          length=0.12, width=0.038, height=0.038, color=(42, 38, 48), outline=False)

    # 4. Braços e Kunais duplos em aço polido
    _box(c, bx - px * 0.12 - 0.04, by - py * 0.12 - 0.04, tz + 0.04, 0.08, 0.08, 0.17, (205, 155, 32))
    _box(c, bx + px * 0.12 - 0.04, by + py * 0.12 - 0.04, tz + 0.04, 0.08, 0.08, 0.17, (205, 155, 32))
    # Kunai mão direita
    _obox(c, (bx + px * 0.14 + fx * 0.04, by + py * 0.14 + fy * 0.04, tz + 0.02), (fx * 0.8, fy * 0.8, -0.4),
          length=0.18, width=0.032, height=0.016, color=(225, 235, 248), outline=True, texture="steel")
    # Kunai mão esquerda
    _obox(c, (bx - px * 0.14 + fx * 0.04, by - py * 0.14 + fy * 0.04, tz + 0.02), (fx * 0.8, fy * 0.8, -0.4),
          length=0.18, width=0.032, height=0.016, color=(225, 235, 248), outline=True, texture="steel")

    # 5. Cabeça, Capuz e Máscara Oni Menpo (com presas douradas e pele limpa)
    hz = c.head_z
    hw = c.head_w
    _box(c, bx - hw / 2, by - hw / 2, hz - 0.015, hw, hw, 0.165, (205, 155, 32))

    rx, ry = rotate_xy(fx, fy, getattr(c, "azimuth", 0.0))
    is_facing = (rx + ry > -0.15)
    if is_facing:
        front = hw / 2 + 0.006
        # Faixa escura da fenda dos olhos
        _box(c, bx + fx * front - 0.05, by + fy * front - 0.05, hz + 0.085, 0.10, 0.10, 0.028, (15, 15, 18), outline=False)
        # Máscara facial Oni com presas douradas
        _box(c, bx + fx * front - 0.055, by + fy * front - 0.055, hz + 0.015, 0.11, 0.11, 0.065, (34, 32, 38), outline=True)
        _box(c, bx + fx * (front + 0.008) - px * 0.025 - 0.006, by + fy * (front + 0.008) - py * 0.025 - 0.006, hz + 0.025, 0.012, 0.012, 0.024, COLOR_GOLD, outline=False, texture="gold")
        _box(c, bx + fx * (front + 0.008) + px * 0.025 - 0.006, by + fy * (front + 0.008) + py * 0.025 - 0.006, hz + 0.025, 0.012, 0.012, 0.024, COLOR_GOLD, outline=False, texture="gold")


# =============================================================================
# MICRO-VOXELS: 7. MURASAKI (KUNOICHI DA KUSARIGAMA & TRAJE EM LÁTEX)
# =============================================================================
def _render_murasaki_microvoxel(c: SimpleNamespace):
    """Murasaki: Kunoichi letal em traje de látex violeta brilhante com foice Kusarigama e corrente 3D."""
    _draw_shadow(c)
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    tz = c.torso_z
    pz = c.pelvis_z

    # 1. Pernas anatômicas com textura de LÁTEX violeta/escuro brilhante
    _draw_humanoid_legs(c, (45, 18, 65), (32, 12, 48), (20, 14, 28), texture="latex", shin_texture="latex")

    # 2. Torso contínuo esculpido em LÁTEX com reflexo especular vibrante
    torso_bottom = pz + 0.04
    torso_top = tz + 0.26
    _box(c, bx - 0.11, by - 0.085, torso_bottom, 0.22, 0.17, torso_top - torso_bottom, (85, 34, 122), texture="latex")
    # Cinta e corset de látex escuro
    _box(c, bx - 0.112, by - 0.087, pz + 0.06, 0.224, 0.174, 0.08, (28, 12, 42), texture="latex")

    # 3. Ombreiras metálicas de aço polido
    _box(c, bx - px * 0.12 - 0.035, by - py * 0.12 - 0.035, tz + 0.11, 0.07, 0.07, 0.06, (190, 195, 210), texture="metal")
    _box(c, bx + px * 0.12 - 0.035, by + py * 0.12 - 0.035, tz + 0.11, 0.07, 0.07, 0.06, (190, 195, 210), texture="metal")

    # Braços em látex violeta
    _box(c, bx - px * 0.11 - 0.03, by - py * 0.11 - 0.03, tz + 0.03, 0.06, 0.06, 0.12, (85, 34, 122), texture="latex")
    _box(c, bx + px * 0.11 - 0.03, by + py * 0.11 - 0.03, tz + 0.03, 0.06, 0.06, 0.12, (85, 34, 122), texture="latex")

    # 4. Foice Kusarigama afiada em aço com corrente 3D
    kama_pos = (bx + px * 0.14 + fx * 0.08, by + py * 0.14 + fy * 0.08, tz + 0.04)
    # Cabo de madeira escura com anéis de metal
    _obox(c, kama_pos, (fx * 0.7, fy * 0.7, 0.4), length=0.30, width=0.032, height=0.032, color=(35, 28, 38), outline=True)
    # Lâmina curvada afiada de aço reluzente
    blade_tip = (kama_pos[0] + fx * 0.15, kama_pos[1] + fy * 0.15, kama_pos[2] + 0.10)
    _obox(c, blade_tip, (-fx * 0.4 + px * 0.8, -fy * 0.4 + py * 0.8, 0.1), length=0.22, width=0.038, height=0.014, color=(235, 242, 255), outline=True, texture="steel")
    # Corrente de elos 3D suspensa e peso ponderal de ferro
    for i in range(3):
        _box(c, kama_pos[0] - 0.01, kama_pos[1] - 0.01, kama_pos[2] - 0.05 * (i + 1), 0.02, 0.02, 0.035, (180, 185, 200), outline=False)
    _box(c, kama_pos[0] - 0.02, kama_pos[1] - 0.02, kama_pos[2] - 0.20, 0.04, 0.04, 0.04, (140, 145, 160), outline=True, texture="metal")

    # 5. Cabeça limpa, máscara facial e cabelo violeta com rabo de cavalo
    hz = c.head_z
    hw = c.head_w
    _box(c, bx - hw / 2, by - hw / 2, hz - 0.015, hw, hw, 0.165, (245, 212, 190))
    # Máscara facial inferior em látex violeta
    _box(c, bx + fx * (hw / 2) - 0.045, by + fy * (hw / 2) - 0.045, hz + 0.01, 0.09, 0.09, 0.065, (45, 18, 65), texture="latex")
    # Cabelo violeta escuro
    _box(c, bx - 0.075, by - 0.075, hz + 0.12, 0.15, 0.15, 0.07, (42, 18, 60))
    # Rabo de cavalo atrás da cabeça com ordenação 360°
    _obox(c, (bx - fx * 0.06, by - fy * 0.06, hz + 0.14), (-fx * 0.5, -fy * 0.5, -0.8),
          length=0.26, width=0.065, height=0.065, color=(42, 18, 60), outline=True)


# =============================================================================
# MICRO-VOXELS: 8. TOMOE (ARQUEIRA SAGRADA MIKO & ARCO YUMI)
# =============================================================================
def _render_tomoe_microvoxel(c: SimpleNamespace):
    """Tomoe: Miko sagrada com hakama escarlate de seda, quimono branco cerimonial e arco Yumi."""
    _draw_shadow(c)
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    tz = c.torso_z
    pz = c.pelvis_z

    # 1. Hakama escarlate articulado em seda
    _draw_humanoid_legs(c, (195, 30, 45), (180, 25, 40), (245, 245, 250), texture="silk")

    # 2. Torso branco cerimonial com Obi escarlate
    torso_bottom = pz + 0.04
    torso_top = tz + 0.26
    _box(c, bx - 0.12, by - 0.09, torso_bottom, 0.24, 0.18, torso_top - torso_bottom, (248, 248, 252), texture="silk")
    _box(c, bx - 0.122, by - 0.092, pz + 0.06, 0.244, 0.184, 0.07, (195, 30, 45), outline=True)

    # 3. Mangas largas brancas cerimoniais com tasuki vermelho
    _box(c, bx - px * 0.12 - 0.045, by - py * 0.12 - 0.045, tz + 0.03, 0.09, 0.09, 0.17, (245, 245, 250), texture="silk")
    _box(c, bx + px * 0.12 - 0.045, by + py * 0.12 - 0.045, tz + 0.03, 0.09, 0.09, 0.17, (245, 245, 250), texture="silk")
    _box(c, bx - px * 0.125, by - py * 0.125, tz + 0.12, 0.095, 0.095, 0.015, (200, 32, 45), outline=False)
    _box(c, bx + px * 0.125, by + py * 0.125, tz + 0.12, 0.095, 0.095, 0.015, (200, 32, 45), outline=False)

    # 4. Arco Yumi longo tradicional nas costas
    yumi_pos = (bx - fx * 0.08, by - fy * 0.08, tz - 0.12)
    _obox(c, yumi_pos, (-fx * 0.18 + px * 0.10, -fy * 0.18 + py * 0.10, 0.96),
          length=0.76, width=0.032, height=0.032, color=(145, 80, 38), outline=True)
    # Aljava de bambu com flechas emplumadas
    _box(c, bx - fx * 0.09 + px * 0.06 - 0.03, by - fy * 0.09 + py * 0.06 - 0.03, tz + 0.04, 0.06, 0.06, 0.22, (95, 48, 26))
    _box(c, bx - fx * 0.09 + px * 0.06 - 0.02, by - fy * 0.09 + py * 0.06 - 0.02, tz + 0.26, 0.04, 0.04, 0.06, (245, 245, 250), outline=False)

    # 5. Cabeça limpa, fita miko escarlate e cabelo negro
    hz = c.head_z
    hw = c.head_w
    _box(c, bx - hw / 2, by - hw / 2, hz - 0.015, hw, hw, 0.165, (245, 215, 195))
    _box(c, bx - 0.08, by - 0.08, hz + 0.12, 0.16, 0.16, 0.07, (20, 18, 24))
    _box(c, bx - 0.085, by - 0.085, hz + 0.11, 0.17, 0.17, 0.025, (215, 35, 50), outline=False)


# =============================================================================
# MICRO-VOXELS: 9. TEPPO (ATIRADOR TANEGASHIMA & CHAPÉU JINGASA)
# =============================================================================
def _render_teppo_microvoxel(c: SimpleNamespace):
    """Teppo: Atirador de infantaria Ashigaru com arcabuz Tanegashima e Jingasa de metal."""
    _draw_shadow(c)
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    tz = c.torso_z
    pz = c.pelvis_z

    # 1. Pernas com calças de batalha e kyahan
    _draw_humanoid_legs(c, (65, 75, 60), (50, 60, 45), (150, 130, 105), texture="silk")

    # 2. Torso com Armadura Dō de ferro verde-oliva
    torso_bottom = pz + 0.04
    torso_top = tz + 0.26
    _box(c, bx - 0.125, by - 0.095, torso_bottom, 0.25, 0.19, torso_top - torso_bottom, (75, 95, 65), texture="metal")
    _box(c, bx + fx * 0.06 - 0.04, by + fy * 0.06 - 0.04, tz + 0.05, 0.08, 0.08, 0.12, (45, 60, 40), outline=False)

    # 3. Chifre de pólvora no quadril
    _box(c, bx - px * 0.13 - 0.02, by - py * 0.13 - 0.02, pz + 0.08, 0.04, 0.04, 0.09, (210, 195, 160), outline=True)

    # 4. Arcabuz Tanegashima autêntico
    gun_pos = (bx + px * 0.12 + fx * 0.06, by + py * 0.12 + fy * 0.06, tz + 0.06)
    # Coronha de madeira de lei
    _obox(c, gun_pos, (fx * 0.9 + px * 0.1, fy * 0.9 + py * 0.1, 0.2), length=0.64, width=0.045, height=0.045, color=(145, 95, 42), outline=True)
    # Cano de ferro longo
    _obox(c, (gun_pos[0] + fx * 0.35, gun_pos[1] + fy * 0.35, gun_pos[2] + 0.08), (fx * 0.9, fy * 0.9, 0.2), length=0.32, width=0.028, height=0.028, color=(200, 205, 215), outline=True)

    # 5. Cabeça e Chapéu cônico de ferro Jingasa com brasão dourado
    hz = c.head_z
    hw = c.head_w
    _box(c, bx - hw / 2, by - hw / 2, hz - 0.015, hw, hw, 0.165, (240, 205, 175))
    _box(c, bx - 0.14, by - 0.14, hz + 0.12, 0.28, 0.28, 0.04, (38, 42, 46), texture="metal")
    _box(c, bx - 0.07, by - 0.07, hz + 0.15, 0.14, 0.14, 0.035, (38, 42, 46), texture="metal")
    _box(c, bx - 0.025, by - 0.025, hz + 0.18, 0.05, 0.05, 0.02, COLOR_GOLD, outline=False)


# =============================================================================
# MICRO-VOXELS: 10. JOE (AMERICAN NINJA TÁTICO)
# =============================================================================
def _render_joe_microvoxel(c: SimpleNamespace):
    """Joe: Operador Shinobi ocidental com camuflagem militar, colete modular e bandana com sol."""
    _draw_shadow(c)
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    tz = c.torso_z
    pz = c.pelvis_z

    # 1. Pernas com farda camuflada e joelheiras táticas
    _draw_humanoid_legs(c, (75, 90, 65), (55, 70, 48), (35, 38, 42), texture="silk")

    # 2. Colete tático modular com bolsos em relevo
    torso_bottom = pz + 0.04
    torso_top = tz + 0.26
    _box(c, bx - 0.125, by - 0.095, torso_bottom, 0.25, 0.19, torso_top - torso_bottom, (55, 68, 50))
    # Bolsos táticos
    _box(c, bx + fx * 0.06 - 0.04, by + fy * 0.06 - 0.04, tz + 0.06, 0.08, 0.08, 0.08, (75, 88, 65), outline=False)

    # 3. Katana tática moderna preta fosca
    _obox(c, (bx + px * 0.14 + fx * 0.06, by + py * 0.14 + fy * 0.06, tz + 0.06), (fx * 0.9, fy * 0.9, 0.1), length=0.50, width=0.036, height=0.036, color=(32, 34, 38), outline=True)

    # 4. Cabeça limpa e Bandana com sol nascente vermelho
    hz = c.head_z
    hw = c.head_w
    _box(c, bx - hw / 2, by - hw / 2, hz - 0.015, hw, hw, 0.165, (245, 210, 180))
    # Bandana branca
    _box(c, bx - hw / 2 - 0.005, by - hw / 2 - 0.005, hz + 0.10, hw + 0.01, hw + 0.01, 0.035, (245, 245, 250), outline=True)
    # Sol nascente vermelho frontal
    _box(c, bx + fx * (hw / 2 + 0.006) - 0.018, by + fy * (hw / 2 + 0.006) - 0.018, hz + 0.105, 0.036, 0.036, 0.025, (215, 35, 45), outline=False)


# =============================================================================
# MICRO-VOXELS: 11. ANNE (CAPITÃ PIRATA & SOBRETUDO BORDÔ)
# =============================================================================
def _render_anne_microvoxel(c: SimpleNamespace):
    """Anne: Capitã Pirata dos Sete Mares com sobretudo bordô, dragonas de ouro, tricórnio e alfanje."""
    _draw_shadow(c)
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    tz = c.torso_z
    pz = c.pelvis_z

    # 1. Pernas com calças pretas e botas de montaria de couro com dobras
    _draw_humanoid_legs(c, (35, 30, 38), (48, 32, 24), (32, 22, 18), texture="canvas", shin_texture="leather")

    # 2. Sobretudo Bordô Imperial com camisa branca e dragonas douradas
    torso_bottom = pz + 0.04
    torso_top = tz + 0.26
    _box(c, bx - 0.12, by - 0.09, torso_bottom, 0.24, 0.18, torso_top - torso_bottom, (165, 32, 52), texture="silk")
    # Camisa branca de pirata por baixo
    _box(c, bx + fx * 0.05 - 0.035, by + fy * 0.05 - 0.035, tz + 0.08, 0.07, 0.07, 0.12, (245, 245, 250), outline=False)
    # Dragonas douradas nos ombros
    _box(c, bx - px * 0.12 - 0.03, by - py * 0.12 - 0.03, tz + 0.18, 0.06, 0.06, 0.03, COLOR_GOLD, outline=False, texture="gold")
    _box(c, bx + px * 0.12 - 0.03, by + py * 0.12 - 0.03, tz + 0.18, 0.06, 0.06, 0.03, COLOR_GOLD, outline=False, texture="gold")

    # 3. Alfanje cortante naval (Cutlass) com guarda em concha dourada
    sword_pos = (bx + px * 0.14 + fx * 0.08, by + py * 0.14 + fy * 0.08, tz + 0.04)
    _obox(c, sword_pos, (fx * 0.8 + px * 0.2, fy * 0.8 + py * 0.2, 0.2), length=0.46, width=0.048, height=0.048, color=(228, 236, 248), outline=True, texture="steel")
    _box(c, sword_pos[0] - 0.025, sword_pos[1] - 0.025, sword_pos[2], 0.055, 0.055, 0.055, COLOR_GOLD, outline=True, texture="gold")

    # 4. Cabeça limpa e Chapéu Tricórnio Pirata com pluma branca
    hz = c.head_z
    hw = c.head_w
    _box(c, bx - hw / 2, by - hw / 2, hz - 0.015, hw, hw, 0.165, (245, 215, 190))
    _box(c, bx - 0.075, by - 0.075, hz + 0.12, 0.15, 0.15, 0.06, (195, 115, 45))
    # Tricórnio de abas dobradas com debrum
    _box(c, bx - 0.13, by - 0.13, hz + 0.13, 0.26, 0.26, 0.04, (26, 22, 28), outline=True)
    _box(c, bx - 0.07, by - 0.07, hz + 0.16, 0.14, 0.14, 0.035, (26, 22, 28), outline=True)
    # Pluma branca elegante
    _box(c, bx - px * 0.08 - 0.02, by - py * 0.08 - 0.02, hz + 0.18, 0.05, 0.05, 0.08, (250, 250, 255), outline=False)


# =============================================================================
# MICRO-VOXELS: 12. JULIE (MOSQUETEIRA REAL FRANCESA & FLORETE)
# =============================================================================
def _render_julie_microvoxel(c: SimpleNamespace):
    """Julie: Mosqueteira Real Francesa com casaca azul, gola de renda, pluma arqueada e florete."""
    _draw_shadow(c)
    bx, by, fx, fy, px, py = c.base_x, c.base_y, c.fx, c.fy, c.px, c.py
    tz = c.torso_z
    pz = c.pelvis_z

    # 1. Pernas de montaria claras e botas nobres de couro marrom
    _draw_humanoid_legs(c, (235, 230, 225), (65, 42, 28), (48, 30, 20), texture="silk", shin_texture="leather")

    # 2. Casaca Azul Real Francesa com gola de renda branca volumosa
    torso_bottom = pz + 0.04
    torso_top = tz + 0.26
    _box(c, bx - 0.12, by - 0.09, torso_bottom, 0.24, 0.18, torso_top - torso_bottom, (38, 88, 175), texture="silk")
    # Gola de renda branca (Jabot)
    _box(c, bx + fx * 0.06 - 0.04, by + fy * 0.06 - 0.04, tz + 0.13, 0.08, 0.08, 0.09, (250, 250, 255), outline=False)
    # Botões dourados duplos
    _box(c, bx + fx * 0.065 - px * 0.03 - 0.005, by + fy * 0.065 - py * 0.03 - 0.005, tz + 0.06, 0.012, 0.012, 0.05, COLOR_GOLD, outline=False, texture="gold")
    _box(c, bx + fx * 0.065 + px * 0.03 - 0.005, by + fy * 0.065 + py * 0.03 - 0.005, tz + 0.06, 0.012, 0.012, 0.05, COLOR_GOLD, outline=False, texture="gold")

    # 3. Florete de esgrima reluzente com copo protetor
    foil_pos = (bx + px * 0.13 + fx * 0.08, by + py * 0.13 + fy * 0.08, tz + 0.04)
    _obox(c, foil_pos, (fx * 0.95, fy * 0.95, 0.1), length=0.58, width=0.024, height=0.024, color=(235, 245, 255), outline=True, texture="steel")
    _box(c, foil_pos[0] - 0.025, foil_pos[1] - 0.025, foil_pos[2], 0.05, 0.05, 0.05, COLOR_GOLD, outline=True, texture="gold")

    # 4. Cabeça limpa e Chapéu Cavalier de Mosqueteira com aba curvada e pluma branca arqueada
    hz = c.head_z
    hw = c.head_w
    _box(c, bx - hw / 2, by - hw / 2, hz - 0.015, hw, hw, 0.165, (245, 215, 195))
    # Copa alta cônica em Azul Real
    _box(c, bx - 0.065, by - 0.065, hz + 0.08, 0.13, 0.13, 0.05, (28, 66, 156), outline=True)
    _box(c, bx - 0.07, by - 0.07, hz + 0.10, 0.14, 0.14, 0.02, COLOR_GOLD, outline=False, texture="gold")
    _box(c, bx - 0.055, by - 0.055, hz + 0.13, 0.11, 0.11, 0.05, (28, 66, 156), outline=True)
    # Aba frontal em declive suave
    front_d = (fx, fy, -0.22)
    fl = math.hypot(*front_d); f_norm = (front_d[0]/fl, front_d[1]/fl, front_d[2]/fl)
    _obox(c, (bx + fx * 0.055, by + fy * 0.055, hz + 0.075), f_norm, 0.075, 0.15, 0.02, (28, 66, 156))
    # Aba lateral esquerda virada para cima (cocked brim)
    _obox(c, (bx + px * 0.065, by + py * 0.065, hz + 0.08), (px * 0.15, py * 0.15, 0.98), 0.12, 0.14, 0.022, (28, 66, 156))
    _box(c, bx + px * 0.085, by + py * 0.085, hz + 0.12, 0.035, 0.035, 0.035, COLOR_GOLD, outline=True, texture="gold")
    # Majestosa pluma branca de avestruz
    _box(c, bx + px * 0.05 - fx * 0.03, by + py * 0.05 - fy * 0.03, hz + 0.22, 0.06, 0.06, 0.06, (252, 252, 255), outline=False)
    _box(c, bx + px * 0.01 - fx * 0.08, by + py * 0.01 - fy * 0.08, hz + 0.26, 0.07, 0.07, 0.055, (252, 252, 255), outline=False)
    _box(c, bx - px * 0.03 - fx * 0.13, by - py * 0.03 - fy * 0.13, hz + 0.23, 0.065, 0.065, 0.05, (230, 235, 245), outline=False)


# =============================================================================
# DESPACHADOR CENTRAL DE MICRO-VOXELS COM MAPEAMENTO EXAUSTIVO DE NOMES
# =============================================================================
from src.entities.voxel_models import render_voxel_humanoid, MODEL_FIGHTERS


def _call_detailed_model(c: SimpleNamespace, char_canonical: str):
    """
    Renderiza o modelo volumétrico T1 evoluído de alta fidelidade visual (com vestimentas dinâmicas,
    armas e acessórios detalhados, reflexos procedurais de materiais como látex, seda e metal,
    sem olhos ou boca saltados) utilizando o pipeline articulado do jogo.
    """
    render_voxel_humanoid(
        surface=c.surface,
        camera=c.camera,
        wx=c.base_x,
        wy=c.base_y,
        wz=c.base_z,
        facing_x=c.fx,
        facing_y=c.fy,
        state=getattr(c, "state", "IDLE"),
        state_timer=getattr(c, "state_timer", 0.0),
        is_alive=getattr(c, "is_alive", True),
        char_type=char_canonical,
        walk_timer=getattr(c, "walk_timer", 0.0),
        alpha=getattr(c, "alpha", 255),
        is_moving=getattr(c, "is_moving", False),
        extra_props=getattr(c, "extra_props", {})
    )


def _call_base_voxel_model(c: SimpleNamespace, char_canonical: str):
    """
    Renderiza o modelo canônico original de voxel clássico do jogo base
    para fins de comparação direta de evolução.
    """
    saved_hook = MODEL_FIGHTERS.pop(char_canonical, None)
    try:
        render_voxel_humanoid(
            surface=c.surface,
            camera=c.camera,
            wx=c.base_x,
            wy=c.base_y,
            wz=c.base_z,
            facing_x=c.fx,
            facing_y=c.fy,
            state=getattr(c, "state", "IDLE"),
            state_timer=getattr(c, "state_timer", 0.0),
            is_alive=getattr(c, "is_alive", True),
            char_type=char_canonical,
            walk_timer=getattr(c, "walk_timer", 0.0),
            alpha=getattr(c, "alpha", 255),
            is_moving=getattr(c, "is_moving", False),
            extra_props=getattr(c, "extra_props", {})
        )
    finally:
        if saved_hook is not None:
            MODEL_FIGHTERS[char_canonical] = saved_hook


DISPATCHER = {
    # 1. Okuni (Dançarina Kabuki - Modelo T1 Master)
    "okuni": render_okuni_t1,
    "kabuki": render_okuni_t1,

    # 2. Kasumi (Kunoichi da Névoa - Modelo T1 Master com calça em Látex e armadura cromada)
    "kasumi": render_kasumi_t1,
    "gray": render_kasumi_t1,
    "gray_ninja": render_kasumi_t1,

    # 3. Saitou (Capitão Shinsengumi - Modelo T1 Master)
    "saitou": render_saitou_t1,
    "saitou_samurai": render_saitou_t1,

    # 4. Kenshi (Espadachim Iaijutsu - Modelo T1 Master: Sarashi, Mangas Fluidas, Hakama, Saya e Katana)
    "kenshi": lambda c: _call_detailed_model(c, "kenshin"),
    "kenshin": lambda c: _call_detailed_model(c, "kenshin"),
    "red": lambda c: _call_detailed_model(c, "kenshin"),

    # 5. Musashi (Mestre Niten Ichi-ryu - Modelo T1 Master: 2 Espadas, Tasuki, Barba e Quimono Canvas)
    "musashi": lambda c: _call_detailed_model(c, "musashi"),
    "blue": lambda c: _call_detailed_model(c, "musashi"),

    # 6. Hanzo (Mestre Shinobi de Iga - Modelo T1 Master: Katana nas costas, Cota de Malha e Menpo Oni)
    "hanzo": lambda c: _call_detailed_model(c, "ninja"),
    "ninja": lambda c: _call_detailed_model(c, "ninja"),
    "yellow": lambda c: _call_detailed_model(c, "ninja"),
    "yellow_ninja": lambda c: _call_detailed_model(c, "ninja"),

    # 7. Murasaki (Kunoichi da Kusarigama - Modelo T1 Master: Traje em Látex com Especular, Ombreiras e Foice com Corrente 3D)
    "murasaki": lambda c: _call_detailed_model(c, "murasaki"),
    "purple": lambda c: _call_detailed_model(c, "murasaki"),
    "purple_ninja": lambda c: _call_detailed_model(c, "murasaki"),

    # 8. Tomoe (Arqueira Sagrada Miko - Modelo T1 Master: Hakama de Seda, Omamori, Arco Yumi e Aljava)
    "tomoe": lambda c: _call_detailed_model(c, "tomoe"),
    "archer": lambda c: _call_detailed_model(c, "tomoe"),
    "miko": lambda c: _call_detailed_model(c, "tomoe"),

    # 9. Teppo (Atirador Tanegashima Ashigaru - Modelo T1 Master: Jingasa de Ferro, Chifre de Pólvora e Arcabuz)
    "teppo": lambda c: _call_detailed_model(c, "rifleman"),
    "rifleman": lambda c: _call_detailed_model(c, "rifleman"),
    "rifle": lambda c: _call_detailed_model(c, "rifleman"),

    # 10. Joe (American Ninja Tático - Modelo T1 Master: Farda Camuflada, Colete Multi-Bolsos e Bandana com Sol)
    "joe": lambda c: _call_detailed_model(c, "american"),
    "american": lambda c: _call_detailed_model(c, "american"),
    "american_ninja": lambda c: _call_detailed_model(c, "american"),

    # 11. Anne (Capitã Pirata - Modelo T1 Master: Sobretudo Bordô, Dragonas de Ouro, Tricórnio com Pluma e Alfanje)
    "anne": lambda c: _call_detailed_model(c, "pirate"),
    "pirate": lambda c: _call_detailed_model(c, "pirate"),

    # 12. Julie (Mosqueteira Real - Modelo T1 Master: Casaca Azul Real, Gola de Renda, Pluma e Florete)
    "julie": lambda c: _call_detailed_model(c, "musketeer"),
    "musketeer": lambda c: _call_detailed_model(c, "musketeer"),
}


def render_microvoxel_fighter(c: SimpleNamespace, char_type: str, version: str = "new"):
    """
    Despacha a renderização do combatente em Micro-voxels 3D:
      - version == "new": renderiza a versão T1 atualizada/evoluída (com reflexos de materiais,
        quimonos em camadas, saias estruturadas, rostos limpos e armas detalhadas).
      - version == "original": renderiza a versão canônica original de voxel clássico para comparação direta.
    """
    key = str(char_type).lower().strip()
    canon_map = {
        "okuni": "okuni", "kabuki": "okuni",
        "kasumi": "kasumi", "gray": "kasumi", "gray_ninja": "kasumi",
        "saitou": "saitou", "saitou_samurai": "saitou",
        "kenshi": "kenshin", "kenshin": "kenshin", "red": "kenshin",
        "musashi": "musashi", "blue": "musashi",
        "hanzo": "ninja", "ninja": "ninja", "yellow": "ninja", "yellow_ninja": "ninja",
        "murasaki": "murasaki", "purple": "murasaki", "purple_ninja": "murasaki",
        "tomoe": "tomoe", "archer": "tomoe", "miko": "tomoe",
        "teppo": "rifleman", "rifleman": "rifleman", "rifle": "rifleman",
        "joe": "american", "american": "american", "american_ninja": "american",
        "anne": "pirate", "pirate": "pirate",
        "julie": "musketeer", "musketeer": "musketeer"
    }
    canon_key = canon_map.get(key, "okuni")

    if version == "original":
        _call_base_voxel_model(c, canon_key)
        return

    fn = DISPATCHER.get(key, render_okuni_t1)
    fn(c)
