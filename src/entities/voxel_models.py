"""
Modelos de Voxel 3D Paramétricos, Anatômicos e Articulados para Samurai Edge:
- Kenshi (Duelista Samurai Vermelha - Battojutsu)
- Musashi (Samurai Azul de Duas Lâminas - Niten Ichi-ryū)
- Hanzo (Ninja Amarelo Shinobi)
- Joe (American Ninja)
- Doberman (Cão de Combate)
- Kasumi (Kunoichi Cinza da Névoa)
- Murasaki (Kunoichi Roxa de Kusarigama)
- Saitou (Capitão Shinsengumi de Gatotsu)
- Tanegashima (Rifleman de Infantaria)
- Okuni (Mestra do Kabuki e Leques Tessen)
- Tomoe (Miko Arqueira de Kyudo)
- Anne (Capitã Pirata de Alfanje Cutlass)
- Julie (Mosqueteira de Florete e Duelo)

Padrão Proposta 2A: Proporções Humanas (~5.7 cabeças), Foco nas Silhuetas Nítidas,
Membros Articulados (Coxa, Joelho/Canela, Pés com Waraji/Geta; Ombros, Cotovelos, Mãos)
e Lâminas com Orientação Angular 3D Dinâmica (nunca estáticas em eixos puros).
"""
from types import SimpleNamespace
import math
import pygame
from src.isometric.iso_math import rotate_xy
from src.isometric import cel_outline, voxel_renderer
from src.isometric.voxel_renderer import draw_voxel_box, draw_oriented_voxel_box
from src.entities import model_kit, okuni_model, kenshi_model, murasaki_model, musashi_model, hanzo_model, joe_model, saitou_model, teppo_model, kasumi_model, tomoe_model, anne_model, julie_model
from src.isometric.voxel_rig import calc_leg_joints, calc_blade_slash_3d, calc_character_idle_pose
from src.config import (
    COLOR_STEEL, COLOR_GOLD, COLOR_WHITE, COLOR_BLACK,
    COLOR_RED_KIMONO, COLOR_RED_HAIR, COLOR_RED_HAKAMA, COLOR_RED_AURA,
    COLOR_BLUE_KIMONO, COLOR_BLUE_HAIR, COLOR_BLUE_HAKAMA, COLOR_BLUE_AURA,
    COLOR_YELLOW_NINJA, COLOR_YELLOW_DARK, COLOR_YELLOW_AURA,
    COLOR_AMERICAN_NINJA, COLOR_AMERICAN_VEST, COLOR_AMERICAN_BANDANA,
    COLOR_DOBERMAN_BLACK, COLOR_DOBERMAN_RUST, COLOR_DOBERMAN_COLLAR,
    COLOR_GRAY_NINJA, COLOR_GRAY_DARK, COLOR_SMOKE, COLOR_BOMB_FUSE,
    COLOR_PURPLE_NINJA, COLOR_PURPLE_DARK, COLOR_PURPLE_AURA, COLOR_CHAIN,
    COLOR_SAITOU_LIGHT_BLUE, COLOR_SAITOU_HAORI_DARK, COLOR_SAITOU_HAKAMA, COLOR_SAITOU_AURA,
    COLOR_RIFLE_COAT, COLOR_RIFLE_HAT, COLOR_RIFLE_AURA, COLOR_RIFLE_WOOD,
    COLOR_KABUKI_WHITE, COLOR_KABUKI_RED, COLOR_KABUKI_HAIR, COLOR_KABUKI_KIMONO, COLOR_KABUKI_AURA, COLOR_POISON_GREEN,
    COLOR_ARCHER_HAKAMA, COLOR_ARCHER_KIMONO, COLOR_ARCHER_AURA, COLOR_BOW_WOOD, COLOR_ROPE,
    COLOR_PIRATE_COAT, COLOR_PIRATE_HAT, COLOR_PIRATE_SHIRT, COLOR_PIRATE_GOLD, COLOR_PIRATE_AURA, COLOR_CUTLASS_STEEL,
    COLOR_MUSKETEER_BLUE, COLOR_MUSKETEER_HAT, COLOR_MUSKETEER_FEATHER, COLOR_MUSKETEER_LACE, COLOR_MUSKETEER_AURA, COLOR_RAPIER_STEEL,
    COLOR_KASUMI_HAIR, COLOR_OKUNI_KIMONO, COLOR_TOMOE_HAKAMA
)

SKIN_COLOR = (248, 218, 192)
SKIN_SHADOW = (220, 180, 150)
COLOR_SANDAL = (185, 155, 105)
COLOR_SCABBARD_DARK = (32, 28, 32)

# Joe (American Ninja): paleta tirada do retrato (farda oliva, colete coiote, balaclava preta)
JOE_BALACLAVA = (26, 27, 31)
JOE_GLOVE = (28, 28, 30)
JOE_BOOT = (66, 58, 40)
JOE_KNEE_PAD = (54, 58, 50)
JOE_VEST = (136, 120, 78)
JOE_POUCH = (108, 96, 62)
JOE_PACK = (60, 66, 44)
JOE_HEADBAND = (222, 206, 150)
JOE_SUN_RED = (200, 36, 40)
JOE_NVG = (38, 42, 46)
JOE_NVG_LENS = (96, 214, 196)
JOE_GRENADE = (62, 92, 52)
JOE_FLAG_BLUE = (36, 62, 150)

def is_female_character(char_type: str) -> bool:
    """Identifica se o combatente possui silhueta e anatomia humana feminina."""
    c = char_type.lower()
    return c in ("kenshin", "kenshi", "kasumi", "gray", "murasaki", "purple",
                 "okuni", "kabuki", "tomoe", "archer", "anne", "pirate", "julie", "musketeer")


def _canonical_char_type(char_type: str) -> str:
    char_type = char_type.lower()
    if "yellow" in char_type: return "ninja"
    if "american" in char_type: return "american"
    if "gray" in char_type or "kemuri" in char_type or "kasumi" in char_type: return "kasumi"
    if "purple" in char_type or "murasaki" in char_type: return "murasaki"
    if "kenshin" in char_type or "kenshi" in char_type or "red" in char_type: return "kenshin"
    if "musashi" in char_type or "blue" in char_type: return "musashi"
    return char_type


# Lutadores com modelo em cel-shading (6.5.5): o contorno de silhueta é feito por `cel_outline` numa camada própria.
CEL_FIGHTERS = {"kenshin": kenshi_model, "murasaki": murasaki_model}
# Todos os lutadores com modelo próprio (ganchos por parte); o estilo cel vale só para os de CEL_FIGHTERS
MODEL_FIGHTERS = {**CEL_FIGHTERS, "musashi": musashi_model, "ninja": hanzo_model, "american": joe_model, "saitou": saitou_model, "rifleman": teppo_model, "kasumi": kasumi_model, "tomoe": tomoe_model, "pirate": anne_model, "musketeer": julie_model}


def _material(model_c, color):
    """Textura de material da cor para as peças genéricas do corpo (None sem modelo próprio)."""
    return None if model_c is None else model_kit.material_for(model_c, color)


def _skin_colors(char_type: str):
    """(pele, sombra da pele): a rampa dos sprites HD-2D no cel-shading dos lutadores que têm modelo próprio."""
    model = CEL_FIGHTERS.get(char_type)
    if model is not None and voxel_renderer.get_render_style() == "cel":
        p = model.pal()
        return p["skin"], p["skin_shadow"]
    if model is None and char_type in MODEL_FIGHTERS:
        p = MODEL_FIGHTERS[char_type].pal()
        if "skin" in p:
            return p["skin"], p["skin_shadow"]
    return SKIN_COLOR, SKIN_SHADOW


def render_voxel_humanoid(
    surface: pygame.Surface,
    camera,
    wx: float, wy: float, wz: float,
    facing_x: float, facing_y: float,
    state: str,
    state_timer: float,
    is_alive: bool,
    char_type: str,
    walk_timer: float = 0.0,
    alpha: int = 255,
    is_moving: bool = False,
    extra_props: dict = None
):
    """Desenha o lutador; os de `CEL_FIGHTERS` passam por uma camada com contorno quando o estilo é "cel"."""
    if (voxel_renderer.get_render_style() == "cel" and state != "CORPSE_SLICED"
            and _canonical_char_type(char_type) in CEL_FIGHTERS):
        def draw(layer, layer_camera):
            _render_voxel_humanoid(layer, layer_camera, wx, wy, wz, facing_x, facing_y, state, state_timer, is_alive, char_type,
                                   walk_timer, 255, is_moving, extra_props)
        cel_outline.render_cel(surface, camera, wx, wy, wz, alpha, draw)
        return
    _render_voxel_humanoid(surface, camera, wx, wy, wz, facing_x, facing_y, state, state_timer, is_alive, char_type,
                           walk_timer, alpha, is_moving, extra_props)


def _render_voxel_humanoid(
    surface: pygame.Surface,
    camera,
    wx: float, wy: float, wz: float,
    facing_x: float, facing_y: float,
    state: str,
    state_timer: float,
    is_alive: bool,
    char_type: str,
    walk_timer: float = 0.0,
    alpha: int = 255,
    is_moving: bool = False,
    extra_props: dict = None
):
    """
    Renderiza combatente humanoide no padrão Proposta 2A (~5.7 cabeças):
    - Anatomia humana refinada com silhuetas marcantes.
    - Membros inferiores articulados (coxa, joelho/canela dobrando, pés com sandálias).
    - Membros superiores articulados (ombros/mangas, antebraço com braçadeira, mão).
    - Lâminas e armas orientadas em arcos tridimensionais fluidos (draw_oriented_voxel_box).
    """
    if extra_props is None:
        extra_props = {}

    char_type = char_type.lower()
    if "yellow" in char_type: char_type = "ninja"
    elif "american" in char_type: char_type = "american"
    elif "gray" in char_type or "kemuri" in char_type or "kasumi" in char_type: char_type = "kasumi"
    elif "purple" in char_type or "murasaki" in char_type: char_type = "murasaki"
    elif "kenshin" in char_type or "kenshi" in char_type or "red" in char_type: char_type = "kenshin"
    elif "musashi" in char_type or "blue" in char_type: char_type = "musashi"
    elif "saitou" in char_type or "saito" in char_type: char_type = "saitou"
    elif "rifle" in char_type or "teppo" in char_type: char_type = "rifleman"
    elif "kabuki" in char_type or "okuni" in char_type: char_type = "okuni"
    elif "archer" in char_type or "kyudo" in char_type or "tomoe" in char_type: char_type = "tomoe"
    elif "pirate" in char_type or "anne" in char_type or "sayuri" in char_type: char_type = "pirate"
    elif "musketeer" in char_type or "julie" in char_type: char_type = "musketeer"

    # Morte com desmembramento ativo
    if state == "CORPSE_SLICED":
        return

    skin_color, skin_shadow = _skin_colors(char_type)
    col_torso = _get_char_torso_color(char_type)
    col_pants = _get_char_pants_color(char_type)
    col_hair = _get_char_hair_color(char_type)
    col_belt = _get_char_belt_color(char_type)
    is_female = is_female_character(char_type)

    # Estado de Morte no solo
    if (not is_alive and state != "DYING_FREEZE") or state == "DEAD":
        sx, sy = camera.apply(wx, wy, 0.0)
        # Poça de sangue dramática no solo
        pygame.draw.ellipse(surface, (120, 16, 20, 180), (sx - 30, sy - 14, 60, 28))
        pygame.draw.ellipse(surface, (70, 10, 12, 220), (sx - 20, sy - 10, 40, 20))
        # Torso caído
        draw_voxel_box(surface, camera, wx - 0.18, wy - 0.12, 0.03, 0.36, 0.24, 0.15, col_torso, outline=True, alpha=alpha)
        # Pelve e cinto
        draw_voxel_box(surface, camera, wx - 0.28, wy - 0.10, 0.03, 0.12, 0.20, 0.13, col_belt, outline=True, alpha=alpha)
        # Pernas estendidas no chão
        draw_voxel_box(surface, camera, wx - 0.52, wy - 0.08, 0.03, 0.26, 0.16, 0.11, col_pants, outline=True, alpha=alpha)
        # Cabeça caída de lado
        draw_voxel_box(surface, camera, wx + 0.18, wy - 0.09, 0.03, 0.18, 0.18, 0.15, skin_color, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, wx + 0.20, wy - 0.10, 0.05, 0.18, 0.18, 0.13, col_hair, outline=True, alpha=alpha)
        # Braço estendido
        draw_voxel_box(surface, camera, wx - 0.08, wy + 0.12, 0.03, 0.24, 0.10, 0.09, col_torso, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, wx + 0.16, wy + 0.12, 0.03, 0.08, 0.08, 0.07, skin_color, outline=False, alpha=alpha)
        return

    # Sombra dinâmica no chão com transparência real atenuada para furtividade
    sx, sy = camera.apply(wx, wy, getattr(camera, "ground_z", 0.0))
    shadow_w = 42 if not is_female else 38
    shadow_h = 18 if not is_female else 16
    shadow_alpha = int(125 * (alpha / 255.0))
    if shadow_alpha > 0:
        shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (14, 18, 16, shadow_alpha), (0, 0, shadow_w, shadow_h))
        surface.blit(shadow_surf, (sx - shadow_w // 2, sy - shadow_h // 2))

    # Vetor de orientação
    fx, fy = facing_x, facing_y
    fnorm = math.hypot(fx, fy)
    if fnorm > 0.001:
        fx /= fnorm; fy /= fnorm
    else:
        fx, fy = 1.0, 0.0
    px, py = -fy, fx

    # As costas do personagem estão voltadas para a câmera? (define se a mochila/katana vai antes ou depois do tronco)
    back_rx, back_ry = rotate_xy(-fx, -fy, getattr(camera, "azimuth", 0.0))
    back_to_camera = (back_rx + back_ry) > 0.0

    # Animação de ataque melee
    is_melee = state in ("ATTACK", "CUTLASS_CLEAVE", "FLECHE", "ZEROSHIKI", "GATOTSU_CHARGE")
    atk_progress = 0.0
    if is_melee:
        atk_dur = 0.20
        if char_type == "kenshin": atk_dur = 0.16
        elif char_type == "musashi": atk_dur = 0.18
        elif char_type in ("pirate", "anne"): atk_dur = 0.22
        elif char_type in ("musketeer", "julie"): atk_dur = 0.24
        elif char_type == "purple": atk_dur = 0.16
        elif char_type == "ninja": atk_dur = 0.18
        elif char_type == "saitou": atk_dur = 0.25

        if state_timer > 0:
            atk_progress = max(0.0, min(1.0, 1.0 - (state_timer / atk_dur)))
        else:
            atk_progress = 0.85

    # Lunge dinâmico com agachamento
    lunge_curve = math.sin(atk_progress * math.pi) if is_melee else 0.0
    lunge_dist = 0.32 if char_type in ("kenshin", "musketeer", "saitou") else 0.22
    lunge_x = fx * lunge_dist * lunge_curve
    lunge_y = fy * lunge_dist * lunge_curve

    # Respiração / Idle bob / Caminhada orgânica
    if is_moving:
        # Elevação elástica da cintura na passada (a cada meio ciclo de passada)
        step_bob = abs(math.sin(walk_timer * 9.0)) * 0.025
        # Sutil inclinação do tronco no sentido do movimento (dinamismo e peso)
        torso_lean_x = fx * 0.035
        torso_lean_y = fy * 0.035
        base_x = wx + lunge_x + torso_lean_x
        base_y = wy + lunge_y + torso_lean_y
        base_z = wz + step_bob
    else:
        idle_bob = math.sin(walk_timer * 2.8) * 0.015
        base_x = wx + lunge_x
        base_y = wy + lunge_y
        base_z = wz + idle_bob

    # -------------------------------------------------------------
    # 1. PERNAS HUMANAS ARTICULADAS (COXA + JOELHO/CANELA + PÉ)
    # -------------------------------------------------------------
    hip_w = 0.075 if is_female else 0.09
    legs_data = calc_leg_joints(
        base_x, base_y, base_z, fx, fy, px, py,
        is_moving, walk_timer, is_melee, atk_progress,
        hip_w, is_female, char_type=char_type
    )

    pelvis_z = base_z + (0.48 if is_female else 0.46)
    pelvis_w = 0.27 if char_type == "kenshin" else (0.24 if is_female else 0.28)
    pelvis_d = 0.18 if is_female else 0.21

    # Contexto dos modelos próprios (Kenshi e Murasaki): alturas do tronco e da cabeça já são conhecidas aqui
    model = MODEL_FIGHTERS.get(char_type)
    model_c = None
    if model is not None:
        torso_z0 = pelvis_z + 0.13
        model_c = SimpleNamespace(
            surface=surface, camera=camera, alpha=alpha, azimuth=getattr(camera, "azimuth", 0.0), base_x=base_x, base_y=base_y, base_z=base_z,
            fx=fx, fy=fy, px=px, py=py, pelvis_z=pelvis_z, pelvis_w=pelvis_w, walk_timer=walk_timer, is_moving=is_moving, is_melee=is_melee,
            atk_progress=atk_progress, lunge_curve=lunge_curve, legs_data=legs_data, state=state, state_timer=state_timer, extra_props=extra_props,
            materials=model_kit.material_map(model.pal(), getattr(model, "MATERIALS", {})), torso_z=torso_z0, neck_z=torso_z0 + 0.26, head_z=torso_z0 + 0.31, head_w=0.13 if is_female else 0.15, sh_span=0.14 if is_female else 0.17)
        if hasattr(model, "draw_behind"):
            model.draw_behind(model_c)
        if hasattr(model, "draw_legs"):
            model.draw_legs(model_c)

    for side in (() if (model_c is not None and hasattr(model, "draw_legs")) else ("L", "R")):
        ld = legs_data[side]
        th_pos = ld["thigh"]
        sh_pos = ld["shin"]
        ft_pos = ld["foot"]
        lift = ld["lift"]

        # Coxa (Hakama superior / calça)
        th_w = 0.10 if is_female else 0.12
        draw_voxel_box(surface, camera, th_pos[0] - th_w/2, th_pos[1] - th_w/2, th_pos[2], th_w, th_w, 0.22, col_pants, outline=True, alpha=alpha)

        # Joelho / Canela (Hakama afunilada ou bota alta)
        sh_w = 0.09 if is_female else 0.11
        shin_col = (95, 52, 28) if char_type == "musketeer" else col_pants
        draw_voxel_box(surface, camera, sh_pos[0] - sh_w/2, sh_pos[1] - sh_w/2, sh_pos[2], sh_w, sh_w, 0.20, shin_col, outline=True, alpha=alpha)

        # Tornozelo / Pele exposta
        if (is_female and char_type != "musketeer") or char_type in ("ninja", "kenshin"):
            draw_voxel_box(surface, camera, sh_pos[0] - 0.03, sh_pos[1] - 0.03, sh_pos[2] - 0.02, 0.06, 0.06, 0.04, skin_color, outline=False, alpha=alpha)

        # Pé com Sandália Waraji / Geta / Bota de couro
        ft_w = 0.07 if is_female else 0.08
        if char_type == "musketeer":
            sandal_col = (85, 46, 24) # Bota de montaria de couro marrom rica
        elif char_type == "american":
            sandal_col = JOE_BOOT     # Bota de combate
        elif char_type in ("saitou", "pirate"):
            sandal_col = COLOR_BLACK
        else:
            sandal_col = COLOR_SANDAL
        draw_voxel_box(surface, camera, ft_pos[0] - ft_w/2 + fx*0.02, ft_pos[1] - ft_w/2 + fy*0.02, ft_pos[2], ft_w, ft_w, 0.05, sandal_col, outline=True, alpha=alpha)
        if char_type == "american":
            # Cano alto da bota e joelheira tática
            draw_voxel_box(surface, camera, sh_pos[0] - sh_w/2 - 0.008, sh_pos[1] - sh_w/2 - 0.008, sh_pos[2] - 0.01, sh_w + 0.016, sh_w + 0.016, 0.11, JOE_BOOT, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, sh_pos[0] - 0.055 + fx*0.035, sh_pos[1] - 0.055 + fy*0.035, sh_pos[2] + 0.13, 0.11, 0.11, 0.075, JOE_KNEE_PAD, outline=True, alpha=alpha)
        # Tira frontal preta da sandália
        if sandal_col == COLOR_SANDAL:
            draw_voxel_box(surface, camera, ft_pos[0] - 0.02 + fx*0.03, ft_pos[1] - 0.02 + fy*0.03, ft_pos[2] + 0.03, 0.04, 0.04, 0.03, COLOR_BLACK, outline=False, alpha=alpha)

    # -------------------------------------------------------------
    # 2. QUADRIL, FAIXA OBI E CINTURA FEMININA/MASCULINA
    # -------------------------------------------------------------
    draw_voxel_box(surface, camera, base_x - pelvis_w/2, base_y - pelvis_d/2, pelvis_z, pelvis_w, pelvis_d, 0.08, col_pants, outline=True, alpha=alpha, texture=_material(model_c, col_pants))
    okuni_c = None
    if char_type == "okuni":
        okuni_c = SimpleNamespace(
            surface=surface, camera=camera, alpha=alpha, base_x=base_x, base_y=base_y, base_z=base_z, fx=fx, fy=fy, px=px, py=py,
            pelvis_z=pelvis_z, pelvis_w=pelvis_w, walk_timer=walk_timer, is_moving=is_moving, is_melee=is_melee, atk_progress=atk_progress,
            lunge_curve=lunge_curve, legs_data=legs_data, state=state, extra_props=extra_props, torso_z=0.0, head_z=0.0, neck_z=0.0, head_w=0.13)
        okuni_model.draw_skirt(okuni_c)

    # Faixa Obi / Cinto marcado
    belt_w = pelvis_w - 0.02
    belt_d = pelvis_d - 0.02
    draw_voxel_box(surface, camera, base_x - belt_w/2, base_y - belt_d/2, pelvis_z + 0.07, belt_w, belt_d, 0.07, col_belt, outline=True, alpha=alpha, texture=_material(model_c, col_belt))
    # Nó / Laço frontal do Obi ou fivela
    draw_voxel_box(surface, camera, base_x - 0.03 + fx * (belt_d/2 + 0.01), base_y - 0.03 + fy * (belt_d/2 + 0.01), pelvis_z + 0.06, 0.06, 0.06, 0.08, COLOR_GOLD if char_type in ("pirate", "musketeer", "okuni") else (COLOR_BLACK if char_type == "american" else COLOR_WHITE), outline=False, alpha=alpha)

    if model_c is not None and hasattr(model, "draw_obi"):
        model.draw_obi(model_c)

    # -------------------------------------------------------------
    # 3. TRONCO HUMANO (QUIMONO TRANSPASSADO / COLETE / HAKAMA)
    # -------------------------------------------------------------
    torso_z = pelvis_z + 0.13
    waist_w = 0.20 if is_female else 0.25
    waist_d = 0.15 if is_female else 0.19

    def draw_joe_back_gear():
        """Mochila tática e katana em diagonal nas costas do Joe."""
        draw_voxel_box(surface, camera, base_x - fx * 0.15 - 0.07, base_y - fy * 0.15 - 0.07, torso_z + 0.02, 0.14, 0.14, 0.22, JOE_PACK, outline=True, alpha=alpha)
        kx, ky, kz = px * 0.35 - fx * 0.05, py * 0.35 - fy * 0.05, 0.9
        klen = math.sqrt(kx * kx + ky * ky + kz * kz)
        ox, oy, oz = base_x - fx * 0.22 - px * 0.07, base_y - fy * 0.22 - py * 0.07, torso_z - 0.06
        draw_oriented_voxel_box(surface, camera, ox, oy, oz, kx, ky, kz, 0.34, 0.04, 0.04, JOE_BALACLAVA, outline=True, alpha=alpha)
        draw_oriented_voxel_box(surface, camera, ox + kx / klen * 0.32, oy + ky / klen * 0.32, oz + kz / klen * 0.32, kx, ky, kz, 0.12, 0.045, 0.045, (92, 66, 40), outline=True, alpha=alpha)

    if char_type == "american" and not back_to_camera and model_c is None:
        draw_joe_back_gear()

    if okuni_c is not None:
        okuni_c.torso_z = torso_z
        if not back_to_camera:
            okuni_model.draw_bow(okuni_c)
    draw_voxel_box(surface, camera, base_x - waist_w/2, base_y - waist_d/2, torso_z, waist_w, waist_d, 0.12, col_torso, outline=True, alpha=alpha, texture=_material(model_c, col_torso))

    # Tórax / Busto feminino ou peitoral masculino
    chest_w = 0.23 if is_female else 0.29
    chest_d = 0.17 if is_female else 0.22
    draw_voxel_box(surface, camera, base_x - chest_w/2, base_y - chest_d/2, torso_z + 0.10, chest_w, chest_d, 0.15, col_torso, outline=True, alpha=alpha, texture=_material(model_c, col_torso))

    # Gola em V do quimono / Colete / Sarashi
    if char_type == "american" and model_c is None:
        # Colete tático coiote com bolsos de carregador, granada e shuriken (como no retrato)
        draw_voxel_box(surface, camera, base_x - 0.15, base_y - 0.12, torso_z + 0.08, 0.30, 0.24, 0.18, JOE_VEST, outline=True, alpha=alpha)
        front = chest_d / 2 + 0.02
        for side in (-0.075, 0.0, 0.075):
            draw_voxel_box(surface, camera, base_x + fx * front + px * side - 0.03, base_y + fy * front + py * side - 0.03, torso_z + 0.01, 0.06, 0.06, 0.08, JOE_POUCH, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x + fx * front + px * 0.10 - 0.02, base_y + fy * front + py * 0.10 - 0.02, torso_z + 0.15, 0.04, 0.04, 0.055, JOE_GRENADE, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x + fx * front - px * 0.09 - 0.03, base_y + fy * front - py * 0.09 - 0.03, torso_z + 0.16, 0.06, 0.06, 0.015, (110, 114, 122), outline=True, alpha=alpha)
        # Coldre na coxa e granada no cinto
        draw_voxel_box(surface, camera, base_x + px * 0.16 - 0.03, base_y + py * 0.16 - 0.03, pelvis_z - 0.13, 0.06, 0.06, 0.14, JOE_BALACLAVA, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - px * 0.12 + fx * 0.10 - 0.02, base_y - py * 0.12 + fy * 0.10 - 0.02, pelvis_z + 0.02, 0.04, 0.04, 0.06, JOE_GRENADE, outline=True, alpha=alpha)
        if back_to_camera:
            draw_joe_back_gear()
    elif char_type == "kenshin":
        # Sarashi branca (faixas de tecido no busto) visível no decote profundo em V
        draw_voxel_box(surface, camera, base_x - 0.04 + fx * (chest_d/2 - 0.01), base_y - 0.04 + fy * (chest_d/2 - 0.01), torso_z + 0.08, 0.08, 0.08, 0.07, (242, 240, 245), outline=False, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.035 + fx * (chest_d/2), base_y - 0.035 + fy * (chest_d/2), torso_z + 0.15, 0.07, 0.07, 0.05, (230, 228, 235), outline=False, alpha=alpha)
        # Colo / Pele
        draw_voxel_box(surface, camera, base_x - 0.03 + fx * (chest_d/2), base_y - 0.03 + fy * (chest_d/2), torso_z + 0.20, 0.06, 0.06, 0.05, skin_color, outline=False, alpha=alpha)
        # Cabaça de saquê (Hyoutan) no quadril direito (conforme arte conceitual)
        draw_voxel_box(surface, camera, base_x - px * 0.14 - fx * 0.04, base_y - py * 0.14 - fy * 0.04, pelvis_z - 0.04, 0.06, 0.06, 0.08, (190, 150, 95), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - px * 0.14 - fx * 0.04, base_y - py * 0.14 - fy * 0.04, pelvis_z + 0.03, 0.04, 0.04, 0.04, (165, 125, 75), outline=False, alpha=alpha)
    elif char_type in ("murasaki", "musashi"):
        draw_voxel_box(surface, camera, base_x - 0.03 + fx * (chest_d/2), base_y - 0.03 + fy * (chest_d/2), torso_z + 0.18, 0.06, 0.06, 0.06, skin_color, outline=False, alpha=alpha)
    elif model_c is None:
        # Gola interna branca em V
        draw_voxel_box(surface, camera, base_x - 0.035 + fx * (chest_d/2 - 0.01), base_y - 0.035 + fy * (chest_d/2 - 0.01), torso_z + 0.12, 0.07, 0.07, 0.11, COLOR_WHITE, outline=False, alpha=alpha)
        # Colo / Pele
        draw_voxel_box(surface, camera, base_x - 0.03 + fx * (chest_d/2), base_y - 0.03 + fy * (chest_d/2), torso_z + 0.18, 0.06, 0.06, 0.06, skin_color, outline=False, alpha=alpha)

    if okuni_c is not None and back_to_camera:
        okuni_model.draw_bow(okuni_c)
    if model_c is not None:
        model_c.torso_z = torso_z
        if hasattr(model, "draw_torso"):
            model.draw_torso(model_c)

    sh_span = 0.14 if is_female else 0.17

    # Capa azul para Julie (Mosqueteira) com animação dinâmica em CAPE_FLOURISH (Item 8)
    if char_type in ("musketeer", "julie") and model_c is None:
        if state == "CAPE_FLOURISH":
            flourish_t = max(0.0, min(1.0, 1.0 - (state_timer / 0.16)))
            spin_ang = flourish_t * math.pi * 2.2
            cape_fx = fx * math.cos(spin_ang) - px * math.sin(spin_ang)
            cape_fy = fy * math.cos(spin_ang) + py * math.sin(spin_ang)
            draw_oriented_voxel_box(
                surface, camera,
                base_x + cape_fx * 0.22, base_y + cape_fy * 0.22, torso_z + 0.02,
                cape_fx, cape_fy, -0.15,
                length=0.48, width=0.18, height=0.32,
                color=(28, 68, 175), outline=True, alpha=alpha
            )
            # Chute frontal Coup de Pied
            kick_z = pelvis_z - 0.12
            draw_oriented_voxel_box(
                surface, camera,
                base_x + fx * 0.18, base_y + fy * 0.18, kick_z,
                fx, fy, 0.10,
                length=0.38, width=0.08, height=0.08,
                color=(180, 185, 195), outline=True, alpha=alpha
            )
            # Bota de couro na ponta do chute
            draw_oriented_voxel_box(
                surface, camera,
                base_x + fx * 0.36, base_y + fy * 0.36, kick_z + 0.02,
                fx, fy, 0.10,
                length=0.14, width=0.09, height=0.09,
                color=(85, 46, 24), outline=True, alpha=alpha
            )
        else:
            draw_voxel_box(surface, camera, base_x - fx * 0.10 - 0.07, base_y - fy * 0.10 - 0.07, torso_z - 0.08, 0.14, 0.14, 0.30, (24, 58, 140), outline=True, alpha=alpha)

    # Dragona dourada militar para Anne (Pirata)
    if char_type == "pirate" and model_c is None:
        draw_voxel_box(surface, camera, base_x + px * sh_span - 0.04, base_y + py * sh_span - 0.04, torso_z + 0.21, 0.08, 0.08, 0.03, COLOR_GOLD, outline=False, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - px * sh_span - 0.04, base_y - py * sh_span - 0.04, torso_z + 0.21, 0.08, 0.08, 0.03, COLOR_GOLD, outline=False, alpha=alpha)

    # Amuleto Omamori no quadril para Tomoe
    if char_type == "tomoe" and model_c is None:
        draw_voxel_box(surface, camera, base_x + px * 0.13 - fx * 0.02, base_y + py * 0.13 - fy * 0.02, pelvis_z - 0.04, 0.04, 0.04, 0.07, (215, 45, 40), outline=False, alpha=alpha)

    # Cachecol e bombas de fumaça no cinto para Kasumi
    if char_type == "kasumi" and model_c is None:
        draw_voxel_box(surface, camera, base_x - fx * 0.08 - 0.03, base_y - fy * 0.08 - 0.03, torso_z + 0.24, 0.06, 0.06, 0.04, (155, 160, 170), outline=False, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - px * 0.13, base_y - py * 0.13, pelvis_z + 0.04, 0.05, 0.05, 0.06, (32, 34, 38), outline=False, alpha=alpha)

    # -------------------------------------------------------------
    # 4. OMBROS E BRAÇOS ARTICULADOS
    # -------------------------------------------------------------
    walk_swing = math.sin(walk_timer * 9.0) if is_moving else 0.0

    arm_l_pos = [base_x + px * sh_span, base_y + py * sh_span, torso_z + 0.18]
    arm_r_pos = [base_x - px * sh_span, base_y - py * sh_span, torso_z + 0.18]

    # Dinâmica dos braços
    if is_melee:
        if model_c is not None and hasattr(model, "attack_arms"):
            (arm_l_x, arm_l_y, arm_l_z), (arm_r_x, arm_r_y, arm_r_z) = model.attack_arms(model_c)
        elif char_type == "kenshin":
            # Kenshi Iai: Braço direito saque relâmpago, esquerdo segura a bainha
            arc_a = -0.75 + atk_progress * 2.15
            arm_r_x = base_x + fx * math.cos(arc_a) * 0.24 - px * math.sin(arc_a) * 0.24
            arm_r_y = base_y + fy * math.cos(arc_a) * 0.24 - py * math.sin(arc_a) * 0.24
            arm_r_z = torso_z + 0.18 - atk_progress * 0.10
            arm_l_x = base_x - px * 0.14 - fx * 0.06
            arm_l_y = base_y - py * 0.14 - fy * 0.06
            arm_l_z = pelvis_z + 0.05
        elif char_type in ("pirate", "anne"):
            sw_a = -1.60 + atk_progress * 3.20
            arm_r_x = base_x + fx * math.cos(sw_a) * 0.30 - px * math.sin(sw_a) * 0.30
            arm_r_y = base_y + fy * math.cos(sw_a) * 0.30 - py * math.sin(sw_a) * 0.30
            arm_r_z = torso_z + 0.16
            arm_l_x = base_x - fx * math.cos(sw_a) * 0.16 + px * math.sin(sw_a) * 0.16
            arm_l_y = base_y - fy * math.cos(sw_a) * 0.16 + py * math.sin(sw_a) * 0.16
            arm_l_z = torso_z + 0.12
        elif char_type in ("musketeer", "julie"):
            reach = math.sin(atk_progress * math.pi) * 0.45
            arm_r_x = base_x + fx * (0.26 + reach) - px * 0.04
            arm_r_y = base_y + fy * (0.26 + reach) - py * 0.04
            arm_r_z = torso_z + 0.16
            arm_l_x = base_x - fx * (0.18 + reach * 0.3) + px * 0.16
            arm_l_y = base_y - fy * (0.18 + reach * 0.3) + py * 0.16
            arm_l_z = torso_z + 0.22
        elif okuni_c is not None:
            arm_l, arm_r = okuni_model.attack_arms(okuni_c)
            arm_l_x, arm_l_y, arm_l_z = arm_l
            arm_r_x, arm_r_y, arm_r_z = arm_r
        elif char_type in ("saitou", "saito"):
            reach = math.sin(atk_progress * math.pi) * 0.35 if state == "ZEROSHIKI" else 0.24
            arm_l_x = base_x + fx * (0.34 + reach)
            arm_l_y = base_y + fy * (0.34 + reach)
            arm_l_z = torso_z + 0.18
            arm_r_x = base_x - fx * 0.08 - px * 0.15
            arm_r_y = base_y - fy * 0.08 - py * 0.15
            arm_r_z = torso_z + 0.12
        else:
            arm_l_x = base_x + px * sh_span - fx * 0.10
            arm_l_y = base_y + py * sh_span - fy * 0.10
            arm_l_z = torso_z + 0.12
            arm_r_x = base_x - px * sh_span + fx * 0.20
            arm_r_y = base_y - py * sh_span + fy * 0.20
            arm_r_z = torso_z + 0.16
    else:
        # Caminhada ou Idle
        if is_moving:
            # Balanço contra-fase dinâmico com cotovelos suaves e elevação orgânica
            arm_sw = -walk_swing * 0.16
            arm_lift = abs(walk_swing) * 0.02
            arm_l_x = base_x + px * sh_span + fx * arm_sw
            arm_l_y = base_y + py * sh_span + fy * arm_sw
            arm_l_z = torso_z + 0.06 + arm_lift
            arm_r_x = base_x - px * sh_span - fx * arm_sw
            arm_r_y = base_y - py * sh_span - fy * arm_sw
            arm_r_z = torso_z + 0.06 + arm_lift
            if model_c is not None and hasattr(model, "walk_arms"):
                (arm_l_x, arm_l_y, arm_l_z), (arm_r_x, arm_r_y, arm_r_z) = model.walk_arms(model_c)
        else:
            # IDLE: Poses características exclusivas de cada combatente com respiração suave
            arm_l_pose, arm_r_pose, idle_weap_data = calc_character_idle_pose(
                char_type, base_x, base_y, torso_z, fx, fy, px, py, walk_timer, extra_props
            )
            arm_l_x, arm_l_y, arm_l_z = arm_l_pose
            arm_r_x, arm_r_y, arm_r_z = arm_r_pose
            if model_c is not None and hasattr(model, "idle_arms"):
                (arm_l_x, arm_l_y, arm_l_z), (arm_r_x, arm_r_y, arm_r_z) = model.idle_arms(model_c)

    # Desenho dos Braços (Ombro/Manga + Antebraço + Mão)
    if model_c is not None and hasattr(model, "draw_arm"):
        model_arms = []
        for hand, shoulder, side in (((arm_l_x, arm_l_y, arm_l_z), arm_l_pos, 1.0), ((arm_r_x, arm_r_y, arm_r_z), arm_r_pos, -1.0)):
            shoulder_pt, elbow_pt = model.draw_arm(model_c, shoulder, hand, side)
            model_arms.append((shoulder_pt, elbow_pt, side))
        if hasattr(model, "draw_sleeves"):
            model.draw_sleeves(model_c, model_arms)
    for arm_x, arm_y, arm_z_curr, sh_x, sh_y in ([] if (model_c is not None and hasattr(model, "draw_arm")) else [
        (arm_l_x, arm_l_y, arm_l_z, arm_l_pos[0], arm_l_pos[1]),
        (arm_r_x, arm_r_y, arm_r_z, arm_r_pos[0], arm_r_pos[1])
    ]):
        # Ombreira / Manga
        draw_voxel_box(surface, camera, sh_x - 0.05, sh_y - 0.05, torso_z + 0.10, 0.10, 0.10, 0.12, col_torso, outline=True, alpha=alpha)
        if char_type == "american":
            # Remendo da bandeira dos EUA na manga (lado de fora do ombro)
            out = 1.0 if (sh_x - base_x) * px + (sh_y - base_y) * py > 0 else -1.0
            fx_p, fy_p = sh_x + px * out * 0.055, sh_y + py * out * 0.055
            draw_voxel_box(surface, camera, fx_p - 0.022, fy_p - 0.022, torso_z + 0.15, 0.044, 0.044, 0.04, JOE_SUN_RED, outline=False, alpha=alpha)
            draw_voxel_box(surface, camera, fx_p - 0.026, fy_p - 0.026, torso_z + 0.175, 0.022, 0.022, 0.022, JOE_FLAG_BLUE, outline=False, alpha=alpha)
        # Antebraço com braçadeira
        draw_voxel_box(surface, camera, arm_x - 0.035, arm_y - 0.035, arm_z_curr - 0.06, 0.07, 0.07, 0.12, col_torso, outline=True, alpha=alpha)
        # Mão esculpida (luva tática preta para o Joe)
        hand_col = JOE_GLOVE if char_type == "american" else skin_color
        draw_voxel_box(surface, camera, arm_x - 0.025, arm_y - 0.025, arm_z_curr - 0.10, 0.05, 0.05, 0.05, hand_col, outline=True, alpha=alpha)

    if okuni_c is not None:
        okuni_model.draw_sleeves(okuni_c, [(arm_l_x, arm_l_y, arm_l_z), (arm_r_x, arm_r_y, arm_r_z)])

    # -------------------------------------------------------------
    # 5. CABEÇA, SILHUETAS FACIAIS E CABELO ESCULPIDO
    # -------------------------------------------------------------
    neck_z = torso_z + 0.26
    draw_voxel_box(surface, camera, base_x - 0.035, base_y - 0.035, neck_z, 0.07, 0.07, 0.06, skin_color, outline=False, alpha=alpha)

    head_z = neck_z + 0.05
    # Crânio esculpido e queixo refinado (foco nas silhuetas)
    head_w = 0.13 if is_female else 0.15
    draw_voxel_box(surface, camera, base_x - head_w/2, base_y - head_w/2, head_z + 0.03, head_w, head_w, 0.14, skin_color, outline=True, alpha=alpha)
    draw_voxel_box(surface, camera, base_x - 0.035 + fx*0.045, base_y - 0.035 + fy*0.045, head_z, 0.07, 0.07, 0.06, skin_shadow, outline=False, alpha=alpha)

    # Cabelos / Capuzes / Chapéus específicos
    if model_c is not None:
        model_c.neck_z, model_c.head_z, model_c.head_w = neck_z, head_z, head_w
    if model_c is not None and hasattr(model, "draw_head"):
        model.draw_head(model_c)

    elif char_type == "ninja":
        # Capuz shinobi amarelo e máscara preta
        draw_voxel_box(surface, camera, base_x - 0.08, base_y - 0.08, head_z + 0.10, 0.16, 0.16, 0.12, COLOR_YELLOW_NINJA, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.07 + fx*0.03, base_y - 0.07 + fy*0.03, head_z, 0.14, 0.14, 0.08, COLOR_BLACK, outline=True, alpha=alpha)

    elif char_type == "kasumi":
        # Cabelo prateado/platinado em coque alto com franja (sem capuz) e cachecol shinobi cinza esvoaçante
        draw_voxel_box(surface, camera, base_x - 0.075, base_y - 0.075, head_z + 0.11, 0.15, 0.15, 0.08, COLOR_KASUMI_HAIR, outline=True, alpha=alpha)
        # Franja frontal prateada
        draw_voxel_box(surface, camera, base_x - 0.045 + fx*0.06, base_y - 0.045 + fy*0.06, head_z + 0.08, 0.09, 0.09, 0.06, (235, 240, 248), outline=False, alpha=alpha)
        # Coque alto no topo da cabeça
        draw_voxel_box(surface, camera, base_x - 0.035, base_y - 0.035, head_z + 0.19, 0.07, 0.07, 0.07, COLOR_KASUMI_HAIR, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.025, base_y - 0.025, head_z + 0.18, 0.05, 0.05, 0.02, (45, 48, 55), outline=False, alpha=alpha) # laço do coque
        # Cachecol shinobi cinza no pescoço e ponta longa esvoaçante para trás
        draw_voxel_box(surface, camera, base_x - 0.06, base_y - 0.06, neck_z - 0.01, 0.12, 0.12, 0.05, (160, 168, 178), outline=False, alpha=alpha)
        scarf_sw = math.sin(walk_timer * 7.5) * 0.04 if is_moving else 0.0
        draw_voxel_box(surface, camera, base_x - fx * 0.12 + px * (0.04 + scarf_sw) - 0.03, base_y - fy * 0.12 + py * (0.04 + scarf_sw) - 0.03, neck_z - 0.06, 0.06, 0.06, 0.14, (145, 152, 162), outline=True, alpha=alpha)

    elif char_type == "american":
        # Balaclava preta cobrindo cabeça, nuca e rosto; só a faixa dos olhos fica à mostra
        draw_voxel_box(surface, camera, base_x - 0.04, base_y - 0.04, neck_z - 0.01, 0.08, 0.08, 0.07, JOE_BALACLAVA, outline=False, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - head_w/2 - 0.008, base_y - head_w/2 - 0.008, head_z + 0.02, head_w + 0.016, head_w + 0.016, 0.16, JOE_BALACLAVA, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x + fx * 0.075 - 0.035, base_y + fy * 0.075 - 0.035, head_z + 0.055, 0.07, 0.07, 0.035, skin_color, outline=False, alpha=alpha)
        for eye in (-1.0, 1.0):
            draw_voxel_box(surface, camera, base_x + fx * 0.098 + px * 0.022 * eye - 0.01, base_y + fy * 0.098 + py * 0.022 * eye - 0.01, head_z + 0.063, 0.02, 0.02, 0.016, (30, 30, 34), outline=False, alpha=alpha)
        # Faixa de pano na testa com o sol vermelho e pontas do nó balançando atrás
        draw_voxel_box(surface, camera, base_x - 0.086, base_y - 0.086, head_z + 0.095, 0.172, 0.172, 0.04, JOE_HEADBAND, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x + fx * 0.09 - 0.024, base_y + fy * 0.09 - 0.024, head_z + 0.10, 0.048, 0.048, 0.03, JOE_SUN_RED, outline=False, alpha=alpha)
        knot_sway = math.sin(walk_timer * 6.0) * 0.035 if is_moving else math.sin(walk_timer * 2.2) * 0.012
        for tail in (-1.0, 1.0):
            draw_voxel_box(surface, camera, base_x - fx * 0.115 + px * (0.03 * tail + knot_sway) - 0.016, base_y - fy * 0.115 + py * (0.03 * tail + knot_sway) - 0.016, head_z + 0.07, 0.032, 0.032, 0.10, JOE_HEADBAND, outline=False, alpha=alpha)
        # Óculos de visão noturna (NVG) erguidos sobre a cabeça
        draw_voxel_box(surface, camera, base_x - 0.045 + fx * 0.02, base_y - 0.045 + fy * 0.02, head_z + 0.175, 0.09, 0.09, 0.03, JOE_NVG, outline=True, alpha=alpha)
        for tube in (-1.0, 1.0):
            tx_, ty_ = base_x + fx * 0.04 + px * 0.04 * tube, base_y + fy * 0.04 + py * 0.04 * tube
            draw_voxel_box(surface, camera, tx_ - 0.025, ty_ - 0.025, head_z + 0.205, 0.05, 0.05, 0.07, JOE_NVG, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, tx_ + fx * 0.03 - 0.013, ty_ + fy * 0.03 - 0.013, head_z + 0.23, 0.026, 0.026, 0.024, JOE_NVG_LENS, outline=False, alpha=alpha)

    elif char_type == "saitou":
        draw_voxel_box(surface, camera, base_x - 0.08, base_y - 0.08, head_z + 0.12, 0.16, 0.16, 0.08, (25, 25, 30), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.04 + fx*0.06, base_y - 0.04 + fy*0.06, head_z + 0.06, 0.08, 0.08, 0.08, (25, 25, 30), outline=False, alpha=alpha)

    elif char_type == "rifleman":
        draw_voxel_box(surface, camera, base_x - 0.14, base_y - 0.14, head_z + 0.12, 0.28, 0.28, 0.06, COLOR_RIFLE_HAT, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.07, base_y - 0.07, head_z + 0.18, 0.14, 0.14, 0.06, COLOR_RIFLE_HAT, outline=True, alpha=alpha)

    elif char_type == "okuni":
        okuni_c.neck_z, okuni_c.head_z, okuni_c.head_w = neck_z, head_z, head_w
        okuni_model.draw_head(okuni_c)

    elif char_type == "tomoe":
        draw_voxel_box(surface, camera, base_x - 0.08, base_y - 0.08, head_z + 0.12, 0.16, 0.16, 0.08, (20, 20, 24), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.085, base_y - 0.085, head_z + 0.08, 0.17, 0.17, 0.05, COLOR_WHITE, outline=True, alpha=alpha)
        tail_x = base_x - fx * 0.10
        tail_y = base_y - fy * 0.10
        draw_voxel_box(surface, camera, tail_x - 0.05, tail_y - 0.05, head_z - 0.06, 0.10, 0.10, 0.20, (20, 20, 24), outline=True, alpha=alpha)

    elif char_type == "pirate":
        draw_voxel_box(surface, camera, base_x - 0.08, base_y - 0.08, head_z + 0.10, 0.16, 0.16, 0.08, (150, 70, 35), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.15, base_y - 0.15, head_z + 0.14, 0.30, 0.30, 0.06, COLOR_PIRATE_HAT, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.08, base_y - 0.08, head_z + 0.20, 0.16, 0.16, 0.06, COLOR_PIRATE_HAT, outline=True, alpha=alpha)

    elif char_type == "musketeer":
        draw_voxel_box(surface, camera, base_x - 0.08, base_y - 0.08, head_z + 0.10, 0.16, 0.16, 0.08, (220, 190, 95), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.15, base_y - 0.15, head_z + 0.14, 0.30, 0.30, 0.06, COLOR_MUSKETEER_HAT, outline=True, alpha=alpha)
        # Pluma esvoaçante
        draw_voxel_box(surface, camera, base_x + px*0.08, base_y + py*0.08, head_z + 0.20, 0.06, 0.06, 0.14, COLOR_MUSKETEER_FEATHER, outline=True, alpha=alpha)

    # -------------------------------------------------------------
    # 6. ARMAS E ESPADAS COM FLUXO ANGULAR 3D (NUNCA ESTÁTICAS)
    # -------------------------------------------------------------
    if char_type == "american" and model_c is None:
        # Kunai na mão direita e shuriken na esquerda, como no retrato
        draw_oriented_voxel_box(surface, camera, arm_r_x, arm_r_y, arm_r_z - 0.02, fx * 0.7, fy * 0.7, 0.55, 0.22, 0.03, 0.014, COLOR_STEEL, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, arm_l_x - 0.04, arm_l_y - 0.04, arm_l_z - 0.075, 0.08, 0.08, 0.015, (112, 116, 124), outline=True, alpha=alpha)

    if model_c is not None and hasattr(model, "draw_front"):
        model.draw_front(model_c, (arm_l_x, arm_l_y, arm_l_z), (arm_r_x, arm_r_y, arm_r_z))

    elif char_type in ("saitou", "saito"):
        if is_melee:
            b_info = calc_blade_slash_3d("saitou", state, atk_progress, base_x, base_y, torso_z, fx, fy, px, py)
            ox, oy, oz = b_info["origin"]
            dx, dy, dz = b_info["dir"]
            draw_oriented_voxel_box(surface, camera, ox, oy, oz, dx, dy, dz, length=b_info["length"], width=b_info["width"], height=b_info["height"], color=COLOR_STEEL, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, ox - 0.03, oy - 0.03, oz, 0.06, 0.06, 0.06, COLOR_GOLD, outline=False, alpha=alpha)
            draw_voxel_box(surface, camera, ox + dx*0.3, oy + dy*0.3, oz, 0.12, 0.12, 0.35, COLOR_SAITOU_AURA, outline=False, alpha=160)
        else:
            if not is_moving:
                # Gatotsu Kamae de perfil em IDLE: Katana horizontal no nível dos olhos
                draw_oriented_voxel_box(
                    surface, camera,
                    arm_l_x, arm_l_y, arm_l_z,
                    dir_x=fx*0.92, dir_y=fy*0.92, dir_z=-0.04,
                    length=0.72, width=0.045, height=0.04,
                    color=COLOR_STEEL, outline=True, alpha=alpha
                )
                draw_voxel_box(surface, camera, arm_r_x - 0.025, arm_r_y - 0.025, arm_r_z, 0.05, 0.05, 0.05, COLOR_GOLD, outline=False, alpha=alpha)
                # Bainha vazia no quadril
                draw_oriented_voxel_box(surface, camera, base_x - px*0.15, base_y - py*0.15, pelvis_z + 0.05, fx*0.7, fy*0.7, -0.20, 0.45, 0.05, 0.05, (30, 32, 38))
            else:
                draw_oriented_voxel_box(surface, camera, base_x - px*0.15, base_y - py*0.15, pelvis_z + 0.05, fx*0.7, fy*0.7, -0.20, 0.48, 0.05, 0.05, (30, 32, 38))

    elif char_type in ("musketeer", "julie"):
        if is_melee:
            b_info = calc_blade_slash_3d("musketeer", state, atk_progress, base_x, base_y, torso_z, fx, fy, px, py)
            ox, oy, oz = b_info["origin"]
            dx, dy, dz = b_info["dir"]
            # Cazoleta / guarda em concha
            draw_voxel_box(surface, camera, ox - 0.04, oy - 0.04, oz - 0.03, 0.08, 0.08, 0.06, COLOR_STEEL, outline=True, alpha=alpha)
            # Florete estocado
            draw_oriented_voxel_box(surface, camera, ox, oy, oz, dx, dy, dz, length=b_info["length"], width=b_info["width"], height=b_info["height"], color=COLOR_RAPIER_STEEL, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, ox + dx*b_info["length"], oy + dy*b_info["length"], oz, 0.08, 0.08, 0.08, COLOR_MUSKETEER_AURA, outline=False, alpha=180)
        else:
            if not is_moving:
                # En Garde de Esgrima em IDLE
                draw_voxel_box(surface, camera, arm_r_x - 0.035, arm_r_y - 0.035, arm_r_z - 0.02, 0.07, 0.07, 0.05, COLOR_STEEL, outline=True, alpha=alpha)
                draw_oriented_voxel_box(
                    surface, camera,
                    arm_r_x, arm_r_y, arm_r_z,
                    dir_x=fx*0.82 + px*0.1, dir_y=fy*0.82 + py*0.1, dir_z=0.08,
                    length=0.72, width=0.03, height=0.03,
                    color=COLOR_RAPIER_STEEL, outline=True, alpha=alpha
                )
            else:
                # Florete abaixado ao lado na caminhada
                draw_voxel_box(surface, camera, arm_r_x - 0.03, arm_r_y - 0.03, arm_r_z - 0.02, 0.06, 0.06, 0.05, COLOR_STEEL, outline=True, alpha=alpha)
                draw_oriented_voxel_box(
                    surface, camera,
                    arm_r_x, arm_r_y, arm_r_z,
                    dir_x=fx*0.3, dir_y=fy*0.3, dir_z=-0.75,
                    length=0.68, width=0.03, height=0.03,
                    color=COLOR_RAPIER_STEEL, outline=True, alpha=alpha
                )

    elif char_type in ("pirate", "anne"):
        if is_melee:
            b_info = calc_blade_slash_3d("pirate", state, atk_progress, base_x, base_y, torso_z, fx, fy, px, py)
            ox, oy, oz = b_info["origin"]
            dx, dy, dz = b_info["dir"]
            draw_voxel_box(surface, camera, ox - 0.04, oy - 0.04, oz - 0.03, 0.08, 0.08, 0.06, COLOR_PIRATE_GOLD, outline=True, alpha=alpha)
            draw_oriented_voxel_box(surface, camera, ox, oy, oz, dx, dy, dz, length=b_info["length"], width=b_info["width"], height=b_info["height"], color=COLOR_CUTLASS_STEEL, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, ox - dx*0.15, oy - dy*0.15, oz + 0.05, 0.15, 0.15, 0.25, COLOR_PIRATE_AURA, outline=False, alpha=160)
        else:
            if not is_moving:
                # Descansando o alfanje cutlass sobre o ombro direito em pose desafiadora de pirata
                draw_voxel_box(surface, camera, arm_r_x - 0.03, arm_r_y - 0.03, arm_r_z - 0.02, 0.07, 0.07, 0.06, COLOR_PIRATE_GOLD, outline=True, alpha=alpha)
                draw_oriented_voxel_box(
                    surface, camera,
                    arm_r_x, arm_r_y, arm_r_z,
                    dir_x=-fx*0.65 - px*0.3, dir_y=-fy*0.65 - py*0.3, dir_z=0.60,
                    length=0.58, width=0.065, height=0.04,
                    color=COLOR_CUTLASS_STEEL, outline=True, alpha=alpha
                )
            else:
                # Alfanje abaixado na mão direita durante a marcha
                draw_voxel_box(surface, camera, arm_r_x - 0.03, arm_r_y - 0.03, arm_r_z - 0.02, 0.07, 0.07, 0.06, COLOR_PIRATE_GOLD, outline=True, alpha=alpha)
                draw_oriented_voxel_box(
                    surface, camera,
                    arm_r_x, arm_r_y, arm_r_z,
                    dir_x=fx*0.4, dir_y=fy*0.4, dir_z=-0.70,
                    length=0.55, width=0.065, height=0.04,
                    color=COLOR_CUTLASS_STEEL, outline=True, alpha=alpha
                )

    elif char_type in ("ninja", "yellow_ninja", "hanzo"):
        # Tantō embainhado nas costas em diagonal
        draw_oriented_voxel_box(
            surface, camera,
            base_x - fx * 0.12 - px * 0.06,
            base_y - fy * 0.12 - py * 0.06,
            torso_z + 0.12,
            dir_x=px*0.7, dir_y=py*0.7, dir_z=0.55,
            length=0.38, width=0.04, height=0.04,
            color=(35, 35, 40), outline=True, alpha=alpha
        )
        has_kunai = extra_props.get("has_kunai", True)
        if has_kunai:
            kx = arm_r_x + fx * 0.10
            ky = arm_r_y + fy * 0.10
            kz = arm_r_z - 0.04
            draw_oriented_voxel_box(surface, camera, kx, ky, kz, fx, fy, -0.15, 0.28, 0.05, 0.04, COLOR_STEEL, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, kx - 0.03, ky - 0.03, kz - 0.02, 0.06, 0.06, 0.04, COLOR_GOLD, outline=False, alpha=alpha)
            if is_melee:
                draw_voxel_box(surface, camera, kx + fx*0.12, ky + fy*0.12, kz, 0.08, 0.08, 0.15, COLOR_YELLOW_AURA, outline=False, alpha=160)

    elif char_type in ("gray", "kasumi"):
        # Adaga shinobi na mão direita em guarda rápida
        draw_oriented_voxel_box(
            surface, camera,
            arm_r_x, arm_r_y, arm_r_z - 0.04,
            dir_x=fx*0.7 - px*0.3, dir_y=fy*0.7 - py*0.3, dir_z=-0.15,
            length=0.26, width=0.045, height=0.035,
            color=COLOR_STEEL, outline=True, alpha=alpha
        )
        # Bomba de fumaça na cintura
        bx = base_x + px * 0.15
        by = base_y + py * 0.15
        draw_voxel_box(surface, camera, bx - 0.05, by - 0.05, torso_z - 0.02, 0.10, 0.10, 0.10, (30, 30, 35), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, bx - 0.015, by - 0.015, torso_z + 0.08, 0.03, 0.03, 0.05, COLOR_BOMB_FUSE, outline=False, alpha=alpha)

    elif char_type in ("rifleman", "teppo"):
        rx = arm_r_x + fx * 0.15
        ry = arm_r_y + fy * 0.15
        rz = torso_z + 0.08
        if not is_moving and not is_melee:
            # Em guarda de infantaria diagonal pelo peito
            draw_oriented_voxel_box(surface, camera, rx - fx*0.12 - px*0.08, ry - fy*0.12 - py*0.08, rz - 0.02, fx*0.6 + px*0.5, fy*0.6 + py*0.5, 0.35, 0.58, 0.065, 0.075, COLOR_RIFLE_WOOD)
            draw_oriented_voxel_box(surface, camera, rx + fx*0.16 + px*0.12, ry + fy*0.16 + py*0.12, rz + 0.12, fx*0.6 + px*0.5, fy*0.6 + py*0.5, 0.35, 0.28, 0.045, 0.045, COLOR_STEEL)
        else:
            draw_oriented_voxel_box(surface, camera, rx - fx*0.15, ry - fy*0.15, rz - 0.02, fx, fy, 0.08, 0.55, 0.07, 0.08, COLOR_RIFLE_WOOD)
            draw_oriented_voxel_box(surface, camera, rx + fx*0.18, ry + fy*0.18, rz + 0.02, fx, fy, 0.08, 0.25, 0.05, 0.05, COLOR_STEEL)

    elif char_type in ("kabuki", "okuni"):
        okuni_model.draw_fans(okuni_c, (arm_l_x, arm_l_y, arm_l_z), (arm_r_x, arm_r_y, arm_r_z))
        if extra_props.get("has_poisoned", False):
            draw_voxel_box(surface, camera, arm_r_x - 0.04, arm_r_y - 0.04, torso_z + 0.18, 0.08, 0.08, 0.08, COLOR_POISON_GREEN, outline=False, alpha=160)

    elif char_type in ("archer", "tomoe"):
        if not is_moving and not is_melee:
            # Arco Yumi vertical clássico segurado ao lado pela mão esquerda até o chão
            bx = arm_l_x + fx * 0.04
            by = arm_l_y + fy * 0.04
            bz = base_z + 0.40
            draw_oriented_voxel_box(surface, camera, bx, by, bz - 0.42, 0.0, 0.0, 1.0, 0.96, 0.05, 0.05, COLOR_BOW_WOOD)
            # Corda do arco (Tsuru)
            sx_top, sy_top = camera.apply(bx, by, bz + 0.54)
            sx_bot, sy_bot = camera.apply(bx, by, bz - 0.42)
            pygame.draw.line(surface, COLOR_WHITE, (sx_top, sy_top), (sx_bot, sy_bot), 1)
        else:
            bx = arm_l_x + fx * 0.12
            by = arm_l_y + fy * 0.12
            bz = torso_z + 0.05
            draw_oriented_voxel_box(surface, camera, bx, by, bz - 0.35, fx*0.2, fy*0.2, 0.95, 0.85, 0.06, 0.06, COLOR_BOW_WOOD)
            sx_top, sy_top = camera.apply(bx + fx*0.1, by + fy*0.1, bz + 0.50)
            sx_bot, sy_bot = camera.apply(bx - fx*0.05, by - fy*0.05, bz - 0.35)
            pygame.draw.line(surface, COLOR_WHITE, (sx_top, sy_top), (sx_bot, sy_bot), 1)
            if extra_props.get("is_drawing", False):
                draw_oriented_voxel_box(surface, camera, bx + fx*0.15, by + fy*0.15, bz + 0.08, fx, fy, 0.0, 0.50, 0.04, 0.04, (180, 140, 80))


def render_voxel_doberman(
    surface: pygame.Surface,
    camera,
    wx: float, wy: float, wz: float,
    facing_x: float, facing_y: float,
    state: str,
    state_timer: float,
    is_alive: bool
):
    """
    Renderiza o cão Doberman com articulação quadrúpede de 4 patas (coxa, jarrete e pata).
    Suporta trote fluido, bote rasante e colapso no solo ao morrer.
    """
    if not is_alive or state in ("DEAD", "KNOCKED_OUT"):
        sx, sy = camera.apply(wx, wy, 0.0)
        pygame.draw.ellipse(surface, (14, 18, 16, 120), (sx - 20, sy - 8, 40, 16))
        # Corpo caído de lado no solo (Item 23)
        draw_voxel_box(surface, camera, wx - 0.22, wy - 0.10, wz + 0.02, 0.44, 0.20, 0.10, COLOR_DOBERMAN_BLACK, outline=True)
        draw_voxel_box(surface, camera, wx + 0.16, wy - 0.08, wz + 0.02, 0.16, 0.16, 0.09, COLOR_DOBERMAN_RUST, outline=True)
        # Patas estendidas lateralmente no chão
        draw_voxel_box(surface, camera, wx - 0.12, wy + 0.10, wz + 0.01, 0.24, 0.06, 0.05, COLOR_DOBERMAN_RUST, outline=True)
        draw_voxel_box(surface, camera, wx + 0.04, wy + 0.10, wz + 0.01, 0.20, 0.06, 0.05, COLOR_DOBERMAN_RUST, outline=True)
        # Cabeça pousada de lado no solo
        draw_voxel_box(surface, camera, wx + 0.26, wy - 0.04, wz + 0.02, 0.12, 0.12, 0.08, COLOR_DOBERMAN_BLACK, outline=True)
        return

    # Sombra
    sx, sy = camera.apply(wx, wy, 0.0)
    pygame.draw.ellipse(surface, (14, 18, 16, 135), (sx - 24, sy - 11, 48, 22))

    fx, fy = facing_x, facing_y
    fn = math.hypot(fx, fy)
    if fn > 0.001:
        fx /= fn; fy /= fn
    else:
        fx, fy = 1.0, 0.0
    px, py = -fy, fx

    is_charging = (state == "CHARGE")
    trot = math.sin(state_timer * 14.0) if not is_charging else 0.0

    body_z = wz + 0.22 if not is_charging else wz + 0.16

    # 1. Pernas Articuladas com Jarretes (Front Left, Front Right, Back Left, Back Right)
    leg_span = 0.07
    leg_configs = [
        ("FL", 1.0, 0.16, trot),
        ("FR", -1.0, 0.16, -trot),
        ("BL", 1.0, -0.16, -trot),
        ("BR", -1.0, -0.16, trot)
    ]
    for name, s_sign, f_offset, sw in leg_configs:
        lx = wx + px * leg_span * s_sign + fx * f_offset
        ly = wy + py * leg_span * s_sign + fy * f_offset
        # Coxa / Espádua
        draw_voxel_box(surface, camera, lx - 0.04, ly - 0.04, body_z - 0.10, 0.08, 0.08, 0.12, COLOR_DOBERMAN_BLACK, outline=True)
        # Canela / Jarrete
        shin_x = lx + fx * sw * 0.06
        shin_y = ly + fy * sw * 0.06
        draw_voxel_box(surface, camera, shin_x - 0.03, shin_y - 0.03, wz + 0.02, 0.06, 0.06, 0.12, COLOR_DOBERMAN_RUST, outline=True)

    # 2. Tronco Musculoso
    draw_voxel_box(surface, camera, wx - 0.22, wy - 0.11, body_z, 0.44, 0.22, 0.18, COLOR_DOBERMAN_BLACK, outline=True)
    draw_voxel_box(surface, camera, wx + fx*0.12 - 0.09, wy + fy*0.12 - 0.09, body_z + 0.02, 0.18, 0.18, 0.16, COLOR_DOBERMAN_RUST, outline=False)

    # Coleira de combate
    col_x = wx + fx * 0.18
    col_y = wy + fy * 0.18
    draw_voxel_box(surface, camera, col_x - 0.07, col_y - 0.07, body_z + 0.12, 0.14, 0.14, 0.06, COLOR_DOBERMAN_COLLAR, outline=True)

    # Colete tático de combate (como no retrato do Joe) com bolsos laterais
    draw_voxel_box(surface, camera, wx + fx * 0.02 - 0.13, wy + fy * 0.02 - 0.13, body_z + 0.15, 0.26, 0.26, 0.06, (44, 48, 52), outline=True)
    for side in (-1.0, 1.0):
        draw_voxel_box(surface, camera, wx + px * 0.13 * side - 0.035, wy + py * 0.13 * side - 0.035, body_z + 0.07, 0.07, 0.07, 0.09, (62, 66, 68), outline=True)

    # 3. Cabeça e Focinho Afunilado
    head_x = col_x + fx * 0.08
    head_y = col_y + fy * 0.08
    head_z = body_z + 0.14
    draw_voxel_box(surface, camera, head_x - 0.07, head_y - 0.07, head_z, 0.14, 0.14, 0.12, COLOR_DOBERMAN_BLACK, outline=True)
    # Focinho com detalhes ferrugem
    draw_voxel_box(surface, camera, head_x + fx*0.09 - 0.04, head_y + fy*0.09 - 0.04, head_z - 0.02, 0.08, 0.08, 0.08, COLOR_DOBERMAN_RUST, outline=True)

    # Orelhas pontiagudas cortadas
    draw_voxel_box(surface, camera, head_x + px*0.05 - 0.02, head_y + py*0.05 - 0.02, head_z + 0.12, 0.04, 0.04, 0.10, COLOR_DOBERMAN_BLACK, outline=False)
    draw_voxel_box(surface, camera, head_x - px*0.05 - 0.02, head_y - py*0.05 - 0.02, head_z + 0.12, 0.04, 0.04, 0.10, COLOR_DOBERMAN_BLACK, outline=False)

    # Cauda curta
    draw_voxel_box(surface, camera, wx - fx*0.24 - 0.02, wy - fy*0.24 - 0.02, body_z + 0.12, 0.05, 0.05, 0.08, COLOR_DOBERMAN_BLACK, outline=False)


# Helpers para cores dos guerreiros baseados estritamente na arte conceitual oficial
def _get_char_torso_color(char_type: str):
    model = MODEL_FIGHTERS.get(char_type)
    if model is not None and "torso" in model.pal():
        return model.pal()["torso"]
    if char_type == "kenshin": return kenshi_model.pal()["kimono"]      # Quimono carmim (Kenshi)
    if char_type == "musashi": return musashi_model.pal()["kimono"]     # Quimono azul índigo desbotado de Musashi
    if char_type in ("ninja", "hanzo"): return COLOR_YELLOW_NINJA # Shozoku amarelo
    if char_type in ("american", "joe"): return (82, 88, 62)  # Colete tático verde-oliva com bolsos
    if char_type in ("gray", "kasumi"): return (34, 38, 44)   # Colete de couro preto sobre traje prateado
    if char_type in ("purple", "murasaki"): return murasaki_model.pal()["suit"]  # Traje shinobi preto-violáceo
    if char_type == "saitou": return COLOR_SAITOU_LIGHT_BLUE # Haori azul-piscina Asagi-iro do Shinsengumi
    if char_type == "rifleman": return (72, 82, 58)          # Casaco militar verde-oliva com peitoral de ferro
    if char_type in ("kabuki", "okuni"): return (165, 24, 35) # Quimono carmim e preto com detalhes dourados
    if char_type in ("archer", "tomoe"): return COLOR_WHITE   # Kosode cerimonial branco de Miko
    if char_type in ("pirate", "anne"): return (26, 36, 52)   # Casaco azul-marinho de capitã com dragona dourada
    if char_type in ("musketeer", "julie"): return (28, 68, 160) # Túnica azul-real com flor-de-lis
    return (200, 200, 200)

def _get_char_pants_color(char_type: str):
    model = MODEL_FIGHTERS.get(char_type)
    if model is not None and "pants" in model.pal():
        return model.pal()["pants"]
    if char_type == "kenshin": return kenshi_model.pal()["hakama"]      # Hakama escura pregueada
    if char_type == "musashi": return musashi_model.pal()["hakama"]     # Hakama marrom-carvão escura
    if char_type in ("ninja", "hanzo"): return (190, 145, 20) # Calça shinobi amarela com caneleiras pretas
    if char_type in ("american", "joe"): return (70, 75, 54) # Calça militar tática verde-oliva com joelheiras
    if char_type in ("gray", "kasumi"): return (185, 192, 202) # Traje furtivo prateado / cinza metálico
    if char_type in ("purple", "murasaki"): return murasaki_model.pal()["suit"]  # Calça justa preta-violeta
    if char_type == "saitou": return (24, 28, 42)            # Hakama azul-marinho escura nas caneleiras
    if char_type == "rifleman": return (64, 72, 52)          # Calça verde-oliva com polainas escuras
    if char_type in ("kabuki", "okuni"): return (28, 24, 32) # Saia inferior preta com ornatos dourados
    if char_type in ("archer", "tomoe"): return (195, 34, 30) # Hakama vermelho-vermelhão de Miko
    if char_type in ("pirate", "anne"): return (48, 44, 40)   # Calça marrom-carvão de montaria
    if char_type in ("musketeer", "julie"): return (180, 185, 195) # Calção cinza-claro / botas de couro marrom
    return (150, 150, 150)

def _get_char_hair_color(char_type: str):
    model = MODEL_FIGHTERS.get(char_type)
    if model is not None and "hair" in model.pal():
        return model.pal()["hair"]
    if char_type == "kenshin": return kenshi_model.pal()["hair"]        # Cabelo castanho-ruivo de Kenshi
    if char_type == "musashi": return musashi_model.pal()["hair"]       # Cabelo preto do coque
    if char_type in ("ninja", "hanzo"): return COLOR_YELLOW_NINJA
    if char_type in ("american", "joe"): return (24, 24, 28)
    if char_type in ("gray", "kasumi"): return (220, 225, 232) # Cabelo prateado / platinado em coque da Kasumi
    if char_type in ("purple", "murasaki"): return murasaki_model.pal()["hair"]  # Cabelo preto com laço roxo
    if char_type == "saitou": return (22, 24, 28)
    if char_type == "rifleman": return (28, 26, 24)
    if char_type in ("kabuki", "okuni"): return (22, 22, 26) # Cabelo laqueado preto com Kanzashi dourados
    if char_type in ("archer", "tomoe"): return (20, 20, 24) # Cabelo longo negro sedoso
    if char_type in ("pirate", "anne"): return (170, 65, 35)  # Cabelo ondulado ruivo-acobreado
    if char_type in ("musketeer", "julie"): return (145, 65, 40) # Cabelo castanho-acobreado em trança
    return (50, 50, 50)

def _get_char_belt_color(char_type: str):
    model = MODEL_FIGHTERS.get(char_type)
    if model is not None and "belt" in model.pal():
        return model.pal()["belt"]
    if char_type == "kenshin": return kenshi_model.pal()["obi"]         # Obi com nó frontal da Kenshi
    if char_type == "musashi": return musashi_model.pal()["sash"]       # Faixa azul-arroxeada
    if char_type in ("ninja", "hanzo"): return (24, 24, 28)  # Faixa preta com kunais
    if char_type in ("american", "joe"): return (55, 45, 35)  # Cinto tático com coldre e granadas
    if char_type in ("gray", "kasumi"): return (42, 45, 50)   # Cinto de couro com bombas de fumaça
    if char_type in ("purple", "murasaki"): return murasaki_model.pal()["wrap"]  # Faixa Obi púrpura brilhante
    if char_type == "saitou": return COLOR_WHITE             # Faixa branca Shinsengumi
    if char_type == "rifleman": return (52, 42, 32)          # Talabarte com chifre de pólvora
    if char_type in ("kabuki", "okuni"): return COLOR_GOLD   # Faixa cerimonial dourada e preta
    if char_type in ("archer", "tomoe"): return COLOR_WHITE   # Cordão cerimonial branco e amuleto
    if char_type in ("pirate", "anne"): return COLOR_PIRATE_GOLD # Fivela e cinto de couro duplo
    if char_type in ("musketeer", "julie"): return COLOR_GOLD # Fivela dourada e faixa
    return (20, 20, 20)

def _get_char_mask_color(char_type: str):
    if char_type in ("ninja", "hanzo"): return (22, 22, 26)  # Máscara Menpo preta
    if char_type in ("gray", "kasumi"): return (160, 165, 175) # Cachecol cinza esvoaçante
    if char_type in ("purple", "murasaki"): return (135, 45, 185) # Máscara shinobi púrpura
    return (30, 30, 30)
