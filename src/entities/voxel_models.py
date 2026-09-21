"""
Modelos de Voxel 3D Paramétricos e Animados para os Combatentes de Samurai Edge Demake:
- Kenshin (Samurai Vermelho)
- Musashi (Samurai Azul de Duas Lâminas)
- Hanzo (Ninja Amarelo)
- Joe (American Ninja)
- Doberman (Cão de Combate)
- Kemuri (Ninja Cinza)
- Murasaki (Ninja Roxo de Kusarigama)
"""
import math
import pygame
from src.isometric.voxel_renderer import draw_voxel_box
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

SKIN_COLOR = (245, 210, 180)

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
    """
    Renderiza um combatente humanoide com proporções e blocos de voxel 3D,
    incluindo animação procedural de caminhada, postura de combate e golpes de armas.
    """
    if extra_props is None:
        extra_props = {}

    # Normalizar nomes de char_type para aceitar sufixos e identidades femininas
    char_type = char_type.lower()
    if "yellow" in char_type: char_type = "ninja"
    elif "american" in char_type: char_type = "american"
    elif "gray" in char_type or "kemuri" in char_type or "kasumi" in char_type: char_type = "kasumi"
    elif "purple" in char_type or "murasaki" in char_type: char_type = "murasaki"
    elif "kenshin" in char_type or "red" in char_type: char_type = "kenshin"
    elif "musashi" in char_type or "blue" in char_type: char_type = "musashi"
    elif "saitou" in char_type or "saito" in char_type: char_type = "saitou"
    elif "rifle" in char_type or "teppo" in char_type: char_type = "rifleman"
    elif "kabuki" in char_type or "okuni" in char_type: char_type = "okuni"
    elif "archer" in char_type or "kyudo" in char_type or "tomoe" in char_type: char_type = "tomoe"
    elif "pirate" in char_type or "anne" in char_type or "sayuri" in char_type: char_type = "pirate"
    elif "musketeer" in char_type or "julie" in char_type: char_type = "musketeer"

    # Se o corpo foi fatiado em peças voxel dinâmicas, não renderiza o corpo padrão
    if state == "CORPSE_SLICED":
        return

    # Estado de Morte simples (quando não houver fatiamento ou freeze ativo)
    if (not is_alive and state != "DYING_FREEZE") or state == "DEAD":
        sx, sy = camera.apply(wx, wy, 0.0)
        pygame.draw.ellipse(surface, (12, 16, 14, 120), (sx - 20, sy - 8, 40, 16))
        # Torso caído
        col_torso = _get_char_torso_color(char_type)
        col_hair = _get_char_hair_color(char_type)
        draw_voxel_box(surface, camera, wx - 0.25, wy - 0.15, 0.05, 0.50, 0.30, 0.15, col_torso, outline=True, alpha=alpha)
        # Cabeça caída
        draw_voxel_box(surface, camera, wx + 0.25, wy - 0.12, 0.05, 0.22, 0.24, 0.18, col_hair, outline=True, alpha=alpha)
        return

    # Sombra dinâmica no chão
    sx, sy = camera.apply(wx, wy, 0.0)
    shadow_w = 42
    shadow_h = 18
    pygame.draw.ellipse(surface, (12, 16, 14, 130), (sx - shadow_w // 2, sy - shadow_h // 2, shadow_w, shadow_h))

    # Ângulo de orientação
    fx, fy = facing_x, facing_y
    fnorm = math.hypot(fx, fy)
    if fnorm > 0.001:
        fx /= fnorm
        fy /= fnorm
    else:
        fx, fy = 1.0, 0.0

    # Vetor perpendicular (ombros / passos laterais)
    px = -fy
    py = fx

    # Animação de caminhada
    leg_swing = math.sin(walk_timer * 11.0) * 0.14 if is_moving else 0.0
    arm_swing = math.cos(walk_timer * 11.0) * 0.12 if is_moving else 0.0

    # Lunge no ataque
    lunge_x = 0.0
    lunge_y = 0.0
    if state == "ATTACK":
        lunge_x = fx * 0.15
        lunge_y = fy * 0.15

    base_x = wx + lunge_x
    base_y = wy + lunge_y
    base_z = wz

    col_torso = _get_char_torso_color(char_type)
    col_pants = _get_char_pants_color(char_type)
    col_hair = _get_char_hair_color(char_type)
    col_belt = _get_char_belt_color(char_type)

    # -------------------------------------------------------------
    # 1. PERNAS EM VOXEL
    # -------------------------------------------------------------
    # Perna esquerda
    l_ox = base_x + px * 0.10 + fx * leg_swing
    l_oy = base_y + py * 0.10 + fy * leg_swing
    draw_voxel_box(surface, camera, l_ox - 0.07, l_oy - 0.07, base_z, 0.14, 0.14, 0.35, col_pants, outline=True, alpha=alpha)

    # Perna direita
    r_ox = base_x - px * 0.10 - fx * leg_swing
    r_oy = base_y - py * 0.10 - fy * leg_swing
    draw_voxel_box(surface, camera, r_ox - 0.07, r_oy - 0.07, base_z, 0.14, 0.14, 0.35, col_pants, outline=True, alpha=alpha)

    # -------------------------------------------------------------
    # 2. TORSO / QUIMONO EM VOXEL
    # -------------------------------------------------------------
    torso_z = base_z + 0.35
    # Faixa / Obi
    draw_voxel_box(surface, camera, base_x - 0.22, base_y - 0.16, torso_z, 0.44, 0.32, 0.09, col_belt, outline=True, alpha=alpha)
    # Tronco
    draw_voxel_box(surface, camera, base_x - 0.20, base_y - 0.14, torso_z + 0.08, 0.40, 0.28, 0.38, col_torso, outline=True, alpha=alpha)

    # Colete tático adicional (para Joe)
    if char_type == "american":
        draw_voxel_box(surface, camera, base_x - 0.21, base_y - 0.15, torso_z + 0.10, 0.42, 0.30, 0.32, COLOR_AMERICAN_VEST, outline=True, alpha=alpha)

    # -------------------------------------------------------------
    # 3. CABEÇA, CABELO E MÁSCARA EM VOXEL
    # -------------------------------------------------------------
    head_z = torso_z + 0.46
    # Rosto / Cabeça
    draw_voxel_box(surface, camera, base_x - 0.15, base_y - 0.13, head_z, 0.30, 0.26, 0.28, SKIN_COLOR, outline=True, alpha=alpha)

    # Cabelos / Capuz / Bandana
    if char_type == "kenshin":
        # Cabelo ruivo volumoso com mechas
        draw_voxel_box(surface, camera, base_x - 0.17, base_y - 0.15, head_z + 0.22, 0.34, 0.30, 0.12, COLOR_RED_HAIR, outline=True, alpha=alpha)
        # Rabo de cavalo atrás
        tail_x = base_x - fx * 0.18
        tail_y = base_y - fy * 0.18
        draw_voxel_box(surface, camera, tail_x - 0.08, tail_y - 0.08, head_z + 0.12, 0.16, 0.16, 0.22, COLOR_RED_HAIR, outline=True, alpha=alpha)

    elif char_type == "musashi":
        # Cabelo preto com coque samurai (Chonmage)
        draw_voxel_box(surface, camera, base_x - 0.16, base_y - 0.14, head_z + 0.22, 0.32, 0.28, 0.11, COLOR_BLUE_HAIR, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.06, base_y - 0.06, head_z + 0.33, 0.12, 0.12, 0.14, COLOR_BLUE_HAIR, outline=True, alpha=alpha)

    elif char_type == "ninja":
        # Hanzo: Capuz shinobi amarelo completo e máscara preta
        draw_voxel_box(surface, camera, base_x - 0.17, base_y - 0.15, head_z + 0.16, 0.34, 0.30, 0.16, COLOR_YELLOW_NINJA, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.16 + fx * 0.04, base_y - 0.14 + fy * 0.04, head_z, 0.32, 0.28, 0.16, COLOR_BLACK, outline=True, alpha=alpha)

    elif char_type == "kasumi":
        # Kasumi (Kunoichi Cinza da Névoa): Capuz cinza e trança prateada lateral longa sobre o ombro
        draw_voxel_box(surface, camera, base_x - 0.16, base_y - 0.14, head_z + 0.16, 0.32, 0.28, 0.14, COLOR_GRAY_NINJA, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.15 + fx * 0.04, base_y - 0.13 + fy * 0.04, head_z, 0.30, 0.26, 0.14, COLOR_GRAY_DARK, outline=True, alpha=alpha)
        braid_x = base_x + px * 0.16
        braid_y = base_y + py * 0.16
        draw_voxel_box(surface, camera, braid_x - 0.05, braid_y - 0.05, head_z + 0.08, 0.10, 0.10, 0.26, COLOR_KASUMI_HAIR, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, braid_x - 0.04 + fx * 0.04, braid_y - 0.04 + fy * 0.04, head_z - 0.12, 0.08, 0.08, 0.22, COLOR_KASUMI_HAIR, outline=False, alpha=alpha)

    elif char_type == "murasaki":
        # Murasaki (Kunoichi Roxa): Máscara e rabo de cavalo púrpura longo esvoaçante
        draw_voxel_box(surface, camera, base_x - 0.16, base_y - 0.14, head_z + 0.16, 0.32, 0.28, 0.14, COLOR_PURPLE_NINJA, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.15 + fx * 0.04, base_y - 0.13 + fy * 0.04, head_z, 0.30, 0.26, 0.14, COLOR_PURPLE_DARK, outline=True, alpha=alpha)
        pony_swing = math.sin(walk_timer * 8.0) * 0.08 if is_moving else 0.0
        tail_x = base_x - fx * 0.18 + px * pony_swing
        tail_y = base_y - fy * 0.18 + py * pony_swing
        draw_voxel_box(surface, camera, tail_x - 0.06, tail_y - 0.06, head_z + 0.12, 0.12, 0.12, 0.32, (185, 95, 235), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, tail_x - 0.04 - fx * 0.05, tail_y - 0.04 - fy * 0.05, head_z - 0.08, 0.08, 0.08, 0.22, (160, 75, 215), outline=False, alpha=alpha)

    elif char_type == "american":
        # Cabelo curto e bandana vermelha icônica
        draw_voxel_box(surface, camera, base_x - 0.16, base_y - 0.14, head_z + 0.20, 0.32, 0.28, 0.12, (32, 28, 26), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.17, base_y - 0.15, head_z + 0.16, 0.34, 0.30, 0.08, COLOR_AMERICAN_BANDANA, outline=True, alpha=alpha)

    elif char_type == "saitou":
        # Cabelo preto samurai com a franja frontal de Saitou
        draw_voxel_box(surface, camera, base_x - 0.16, base_y - 0.14, head_z + 0.20, 0.32, 0.28, 0.12, (25, 25, 30), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.08 + fx * 0.10, base_y - 0.08 + fy * 0.10, head_z + 0.12, 0.16, 0.16, 0.10, (25, 25, 30), outline=False, alpha=alpha)

    elif char_type == "rifleman":
        # Jingasa (chapéu cônico de infantaria) e coque
        draw_voxel_box(surface, camera, base_x - 0.22, base_y - 0.20, head_z + 0.22, 0.44, 0.40, 0.08, COLOR_RIFLE_HAT, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.12, base_y - 0.10, head_z + 0.30, 0.24, 0.20, 0.06, COLOR_RIFLE_HAT, outline=True, alpha=alpha)

    elif char_type == "okuni":
        # Okuni (Criadora do Kabuki): Maquiagem branca, lábios carmim e coque com espetos dourados Kanzashi
        draw_voxel_box(surface, camera, base_x - 0.15 + fx * 0.05, base_y - 0.13 + fy * 0.05, head_z, 0.30, 0.26, 0.22, COLOR_KABUKI_WHITE, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.08 + fx * 0.08, base_y - 0.06 + fy * 0.08, head_z + 0.02, 0.16, 0.12, 0.05, COLOR_KABUKI_RED, outline=False, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.16, base_y - 0.14, head_z + 0.18, 0.32, 0.28, 0.14, (24, 24, 28), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.08, base_y - 0.08, head_z + 0.30, 0.16, 0.16, 0.12, (24, 24, 28), outline=True, alpha=alpha)
        # Espetos Kanzashi dourados
        draw_voxel_box(surface, camera, base_x + px * 0.16 - 0.02, base_y + py * 0.16 - 0.02, head_z + 0.32, 0.05, 0.05, 0.22, COLOR_GOLD, outline=False, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - px * 0.16 - 0.02, base_y - py * 0.16 - 0.02, head_z + 0.32, 0.05, 0.05, 0.22, COLOR_GOLD, outline=False, alpha=alpha)

    elif char_type == "tomoe":
        # Tomoe (Miko Arqueira): Cabelo longo negro e faixa cerimonial branca Hachimaki
        draw_voxel_box(surface, camera, base_x - 0.16, base_y - 0.14, head_z + 0.18, 0.32, 0.28, 0.14, (20, 20, 24), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.17, base_y - 0.15, head_z + 0.15, 0.34, 0.30, 0.06, COLOR_WHITE, outline=True, alpha=alpha)
        hair_x = base_x - fx * 0.14
        hair_y = base_y - fy * 0.14
        draw_voxel_box(surface, camera, hair_x - 0.10, hair_y - 0.08, head_z - 0.10, 0.20, 0.16, 0.28, (20, 20, 24), outline=True, alpha=alpha)

    elif char_type == "pirate":
        # Anne (Espadachim Pirata): Cabelo acobreado e Tricórnio preto com fivela dourada
        draw_voxel_box(surface, camera, base_x - 0.16, base_y - 0.14, head_z + 0.16, 0.32, 0.28, 0.12, (150, 70, 35), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.24, base_y - 0.22, head_z + 0.22, 0.48, 0.44, 0.08, COLOR_PIRATE_HAT, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.15, base_y - 0.13, head_z + 0.28, 0.30, 0.26, 0.10, COLOR_PIRATE_HAT, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x + fx * 0.15 - 0.04, base_y + fy * 0.15 - 0.04, head_z + 0.24, 0.08, 0.08, 0.08, COLOR_PIRATE_GOLD, outline=False, alpha=alpha)

    elif char_type == "musketeer":
        # Julie (Mosqueteira): Cabelo loiro e chapéu de feltro com grande pluma branca
        draw_voxel_box(surface, camera, base_x - 0.15, base_y - 0.13, head_z + 0.16, 0.30, 0.26, 0.12, (220, 190, 95), outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.24, base_y - 0.22, head_z + 0.22, 0.48, 0.44, 0.07, COLOR_MUSKETEER_HAT, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x - 0.14, base_y - 0.12, head_z + 0.27, 0.28, 0.24, 0.10, COLOR_MUSKETEER_HAT, outline=True, alpha=alpha)
        feather_swing = math.sin(walk_timer * 7.0) * 0.06 if is_moving else 0.0
        draw_voxel_box(surface, camera, base_x + px * 0.12 - 0.05, base_y + py * 0.12 - 0.05, head_z + 0.34, 0.10, 0.10, 0.18, COLOR_MUSKETEER_FEATHER, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, base_x + px * 0.18 - fx * 0.08 - 0.04 + px * feather_swing, base_y + py * 0.18 - fy * 0.08 - 0.04 + py * feather_swing, head_z + 0.46, 0.08, 0.08, 0.12, COLOR_MUSKETEER_FEATHER, outline=False, alpha=alpha)

    # -------------------------------------------------------------
    # 4. BRAÇOS E ARMAS EM VOXEL
    # -------------------------------------------------------------
    arm_l_x = base_x + px * 0.22 - fx * arm_swing
    arm_l_y = base_y + py * 0.22 - fy * arm_swing
    arm_r_x = base_x - px * 0.22 + fx * arm_swing
    arm_r_y = base_y - py * 0.22 + fy * arm_swing
    arm_z = torso_z + 0.20

    # Braço esquerdo
    draw_voxel_box(surface, camera, arm_l_x - 0.06, arm_l_y - 0.06, arm_z - 0.14, 0.12, 0.12, 0.28, col_torso, outline=True, alpha=alpha)
    # Braço direito
    draw_voxel_box(surface, camera, arm_r_x - 0.06, arm_r_y - 0.06, arm_z - 0.14, 0.12, 0.12, 0.28, col_torso, outline=True, alpha=alpha)

    # -------------------------------------------------------------
    # 5. ARMAS ESPECÍFICAS DE CADA GUERREIRO
    # -------------------------------------------------------------
    if char_type == "kenshin":
        # Katana: Embainhada na cintura quando Idle; empunhada e golpeando no Ataque
        if state == "ATTACK":
            # Golpe Iai: lâmina de aço longa de voxel projetada à frente
            blade_x = base_x + fx * 0.55
            blade_y = base_y + fy * 0.55
            draw_voxel_box(surface, camera, blade_x - 0.04, blade_y - 0.04, torso_z + 0.18, 0.08, 0.08, 0.70, COLOR_STEEL, outline=True, alpha=alpha)
            # Rastro de luz de voxel vermelho (Aura)
            draw_voxel_box(surface, camera, blade_x - 0.08 + px * 0.10, blade_y - 0.08 + py * 0.10, torso_z + 0.12, 0.16, 0.16, 0.40, COLOR_RED_AURA, outline=False, alpha=160)
        else:
            # Bainha no quadril esquerdo
            draw_voxel_box(surface, camera, base_x - 0.28, base_y - 0.08, torso_z - 0.04, 0.09, 0.46, 0.07, (42, 38, 42), outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, base_x - 0.31, base_y + 0.36, torso_z - 0.02, 0.08, 0.14, 0.06, COLOR_GOLD, outline=True, alpha=alpha)

    elif char_type == "musashi":
        # Duas Espadas de Voxel (Niten Ichi-ryū)
        if state == "PARRY":
            # Lâminas cruzadas em X defensivo de voxel
            draw_voxel_box(surface, camera, base_x + fx * 0.22 - px * 0.15, base_y + fy * 0.22 - py * 0.15, torso_z + 0.05, 0.08, 0.08, 0.65, COLOR_STEEL, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, base_x + fx * 0.22 + px * 0.15, base_y + fy * 0.22 + py * 0.15, torso_z + 0.05, 0.08, 0.08, 0.65, COLOR_STEEL, outline=True, alpha=alpha)
            # Brilho de parry azul
            draw_voxel_box(surface, camera, base_x + fx * 0.22, base_y + fy * 0.22, torso_z + 0.25, 0.18, 0.18, 0.25, COLOR_BLUE_AURA, outline=False, alpha=150)
        elif state == "ATTACK":
            # Espadas cortando
            draw_voxel_box(surface, camera, base_x + fx * 0.50, base_y + fy * 0.50, torso_z + 0.10, 0.08, 0.08, 0.62, COLOR_STEEL, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, base_x + fx * 0.35 - px * 0.25, base_y + fy * 0.35 - py * 0.25, torso_z + 0.25, 0.07, 0.07, 0.45, COLOR_STEEL, outline=True, alpha=alpha)
        else:
            # Duas bainhas
            draw_voxel_box(surface, camera, base_x - 0.28, base_y - 0.06, torso_z - 0.02, 0.08, 0.44, 0.06, (30, 36, 48), outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, base_x - 0.25, base_y - 0.16, torso_z + 0.05, 0.07, 0.32, 0.06, (30, 36, 48), outline=True, alpha=alpha)

    elif char_type == "ninja":
        # Kunai empunhada (se tiver kunai)
        has_kunai = extra_props.get("has_kunai", True)
        if has_kunai:
            kx = arm_r_x + fx * 0.20
            ky = arm_r_y + fy * 0.20
            draw_voxel_box(surface, camera, kx - 0.04, ky - 0.04, arm_z - 0.10, 0.08, 0.08, 0.30, COLOR_STEEL, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, kx - 0.05, ky - 0.05, arm_z - 0.14, 0.10, 0.10, 0.06, COLOR_GOLD, outline=True, alpha=alpha)

    elif char_type == "american":
        # Shuriken na mão
        draw_voxel_box(surface, camera, arm_r_x + fx * 0.15 - 0.05, arm_r_y + fy * 0.15 - 0.05, arm_z - 0.05, 0.10, 0.10, 0.04, COLOR_STEEL, outline=True, alpha=alpha)

    elif char_type == "gray":
        # Bomba relógio na cintura ou empunhada
        bx = base_x + fx * 0.20 if state == "ATTACK" else base_x + px * 0.22
        by = base_y + fy * 0.20 if state == "ATTACK" else base_y + py * 0.22
        draw_voxel_box(surface, camera, bx - 0.08, by - 0.08, torso_z - 0.04, 0.16, 0.16, 0.16, (25, 25, 30), outline=True, alpha=alpha)
        # Pavio de voxel
        draw_voxel_box(surface, camera, bx - 0.02, by - 0.02, torso_z + 0.12, 0.04, 0.04, 0.08, COLOR_BOMB_FUSE, outline=False, alpha=alpha)

    elif char_type == "purple":
        # Kusarigama: Foice curta (Kama) na mão direita
        kx = arm_r_x + fx * 0.22
        ky = arm_r_y + fy * 0.22
        # Cabo de madeira da foice
        draw_voxel_box(surface, camera, kx - 0.04, ky - 0.04, arm_z - 0.15, 0.08, 0.08, 0.28, (80, 50, 30), outline=True, alpha=alpha)
        # Lâmina curvada de foice
        draw_voxel_box(surface, camera, kx + fx * 0.10 - 0.04, ky + fy * 0.10 - 0.04, arm_z + 0.10, 0.15, 0.15, 0.07, COLOR_STEEL, outline=True, alpha=alpha)
        if state == "ATTACK":
            # Brilho de Precedência Absoluta
            draw_voxel_box(surface, camera, kx + fx * 0.20 - 0.08, ky + fy * 0.20 - 0.08, arm_z + 0.05, 0.24, 0.24, 0.20, COLOR_PURPLE_AURA, outline=False, alpha=160)

    elif char_type == "saitou":
        # Detalhes das mangas Shinsengumi (triângulos brancos)
        draw_voxel_box(surface, camera, arm_l_x - 0.07, arm_l_y - 0.07, arm_z - 0.12, 0.14, 0.14, 0.06, COLOR_WHITE, outline=False, alpha=alpha)
        draw_voxel_box(surface, camera, arm_r_x - 0.07, arm_r_y - 0.07, arm_z - 0.12, 0.14, 0.14, 0.06, COLOR_WHITE, outline=False, alpha=alpha)

        # Postura de Gatotsu Canhoto (Katana empunhada com a mão esquerda à frente)
        if state == "GATOTSU_CHARGE":
            # Investida baixa do Gatotsu: lâmina longa estendida frontalmente
            blade_x = base_x + fx * 0.72
            blade_y = base_y + fy * 0.72
            # Lâmina de aço estendida na horizontal
            draw_voxel_box(surface, camera, blade_x - 0.04, blade_y - 0.04, torso_z + 0.18, 0.08, 0.08, 0.88, COLOR_STEEL, outline=True, alpha=alpha)
            # Tsuba (guarda) dourada
            draw_voxel_box(surface, camera, blade_x - fx * 0.25 - 0.06, blade_y - fy * 0.25 - 0.06, torso_z + 0.15, 0.12, 0.12, 0.06, COLOR_GOLD, outline=True, alpha=alpha)
            # Brilho cortante ciano (Aura Gatotsu)
            draw_voxel_box(surface, camera, blade_x + fx * 0.30 - 0.06, blade_y + fy * 0.30 - 0.06, torso_z + 0.16, 0.12, 0.12, 0.55, COLOR_SAITOU_AURA, outline=False, alpha=170)
        elif state == "BRAKING":
            # Derrapagem de frenagem com lâmina em guarda recuada
            blade_x = base_x + fx * 0.40
            blade_y = base_y + fy * 0.40
            draw_voxel_box(surface, camera, blade_x - 0.04, blade_y - 0.04, torso_z + 0.12, 0.08, 0.08, 0.65, COLOR_STEEL, outline=True, alpha=alpha)
        elif state == "ZEROSHIKI":
            # Estocada súbita curta
            blade_x = base_x + fx * 0.50
            blade_y = base_y + fy * 0.50
            draw_voxel_box(surface, camera, blade_x - 0.04, blade_y - 0.04, torso_z + 0.18, 0.08, 0.08, 0.60, COLOR_STEEL, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, blade_x + fx * 0.15 - 0.04, blade_y + fy * 0.15 - 0.04, torso_z + 0.17, 0.08, 0.08, 0.25, COLOR_SAITOU_AURA, outline=False, alpha=150)
        else:
            # Em repouso / caminhada: bainha na cintura esquerda e empunhadura pronta
            scab_x = base_x - px * 0.18
            scab_y = base_y - py * 0.18
            draw_voxel_box(surface, camera, scab_x - 0.05, scab_y - 0.05, torso_z + 0.05, 0.10, 0.10, 0.65, (30, 32, 38), outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, scab_x - fx * 0.16 - 0.04, scab_y - fy * 0.16 - 0.04, torso_z + 0.10, 0.08, 0.08, 0.20, COLOR_WHITE, outline=True, alpha=alpha)

    elif char_type == "rifleman":
        # Arcabuz Tanegashima longo
        rx = arm_r_x + fx * 0.25
        ry = arm_r_y + fy * 0.25
        rz = torso_z + 0.10
        # Coronha de madeira de cerejeira
        draw_voxel_box(surface, camera, rx - fx * 0.22 - 0.05, ry - fy * 0.22 - 0.05, rz - 0.04, 0.10, 0.10, 0.12, COLOR_RIFLE_WOOD, outline=True, alpha=alpha)
        # Cano longo de ferro
        draw_voxel_box(surface, camera, rx - 0.04, ry - 0.04, rz, 0.08, 0.08, 0.12, COLOR_STEEL, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, rx + fx * 0.25 - 0.03, ry + fy * 0.25 - 0.03, rz + 0.02, 0.06, 0.06, 0.10, COLOR_STEEL, outline=False, alpha=alpha)
        # Mecha acesa fumegante
        draw_voxel_box(surface, camera, rx - fx * 0.08 - 0.02, ry - fy * 0.08 - 0.02, rz + 0.08, 0.05, 0.05, 0.05, (255, 130, 30), outline=False, alpha=alpha)

    elif char_type == "kabuki":
        # Leque teatral Sensu dourado e carmim na mão direita
        kx = arm_r_x + fx * 0.18
        ky = arm_r_y + fy * 0.18
        draw_voxel_box(surface, camera, kx - 0.08, ky - 0.08, arm_z - 0.05, 0.16, 0.16, 0.22, COLOR_KABUKI_RED, outline=True, alpha=alpha)
        draw_voxel_box(surface, camera, kx - 0.06, ky - 0.06, arm_z + 0.08, 0.12, 0.12, 0.10, COLOR_GOLD, outline=False, alpha=alpha)
        if extra_props.get("has_poisoned", False):
            # Efeito de veneno esmeralda sutil nas mãos
            draw_voxel_box(surface, camera, kx - 0.05, ky - 0.05, arm_z + 0.15, 0.10, 0.10, 0.10, COLOR_POISON_GREEN, outline=False, alpha=150)

    elif char_type == "archer":
        # Grande Arco Yumi japonês na mão esquerda
        bx = arm_l_x + fx * 0.15
        by = arm_l_y + fy * 0.15
        bz = torso_z + 0.05
        # Arco curvado longo de madeira
        draw_voxel_box(surface, camera, bx - 0.04, by - 0.04, bz - 0.40, 0.08, 0.08, 0.95, COLOR_BOW_WOOD, outline=True, alpha=alpha)
        # Corda do arco (linha branca)
        sx_top, sy_top = camera.apply(bx, by, bz + 0.55)
        sx_bot, sy_bot = camera.apply(bx, by, bz - 0.40)
        pygame.draw.line(surface, COLOR_WHITE, (sx_top, sy_top), (sx_bot, sy_bot), 1)
        # Flecha pronta se estiver retesando o arco
        if extra_props.get("is_drawing", False):
            draw_voxel_box(surface, camera, bx + fx * 0.20 - 0.03, by + fy * 0.20 - 0.03, bz + 0.10, 0.06, 0.06, 0.55, (180, 140, 80), outline=False, alpha=alpha)

    elif char_type in ("pirate", "anne"):
        # Alfanje Pirata (Cutlass): Lâmina larga e curva com guarda-mão dourado
        cx = arm_r_x + fx * 0.20
        cy = arm_r_y + fy * 0.20
        cz = torso_z + 0.10
        if state in ("ATTACK", "CUTLASS_CLEAVE"):
            # Golpe em arco amplo de 180 graus
            blade_x = base_x + fx * 0.52 + px * 0.15
            blade_y = base_y + fy * 0.52 + py * 0.15
            # Guarda em concha dourada
            draw_voxel_box(surface, camera, cx - 0.06, cy - 0.06, cz - 0.04, 0.12, 0.12, 0.10, COLOR_PIRATE_GOLD, outline=True, alpha=alpha)
            # Lâmina curvada cortante
            draw_voxel_box(surface, camera, blade_x - 0.06, blade_y - 0.06, cz + 0.05, 0.12, 0.12, 0.65, COLOR_CUTLASS_STEEL, outline=True, alpha=alpha)
            # Rastro de corte dourado / pirata
            draw_voxel_box(surface, camera, blade_x + px * 0.20 - 0.08, blade_y + py * 0.20 - 0.08, cz + 0.10, 0.22, 0.22, 0.35, COLOR_PIRATE_AURA, outline=False, alpha=160)
        else:
            # Cutlass embainhado ou empunhado relaxado na mão direita
            draw_voxel_box(surface, camera, cx - 0.05, cy - 0.05, cz - 0.06, 0.10, 0.10, 0.08, COLOR_PIRATE_GOLD, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, cx + fx * 0.08 - 0.04, cy + fy * 0.08 - 0.04, cz - 0.02, 0.08, 0.08, 0.50, COLOR_CUTLASS_STEEL, outline=True, alpha=alpha)

    elif char_type in ("musketeer", "julie"):
        # Florete de Duelo (Rapier): Lâmina delgada de aço e copo protetor na guarda
        rx = arm_r_x + fx * 0.22
        ry = arm_r_y + fy * 0.22
        rz = torso_z + 0.12
        if state in ("ATTACK", "FLECHE"):
            # Estocada Fleche fulminante longa à frente
            blade_x = base_x + fx * 0.68
            blade_y = base_y + fy * 0.68
            # Guarda em copo de prata
            draw_voxel_box(surface, camera, rx - 0.06, ry - 0.06, rz - 0.04, 0.12, 0.12, 0.10, COLOR_STEEL, outline=True, alpha=alpha)
            # Lâmina perfurante longa e fina
            draw_voxel_box(surface, camera, blade_x - 0.03, blade_y - 0.03, rz + 0.04, 0.06, 0.06, 0.85, COLOR_RAPIER_STEEL, outline=True, alpha=alpha)
            # Rastro de estocada precisa
            draw_voxel_box(surface, camera, blade_x + fx * 0.25 - 0.04, blade_y + fy * 0.25 - 0.04, rz + 0.05, 0.08, 0.08, 0.30, COLOR_MUSKETEER_AURA, outline=False, alpha=170)
        elif state == "PARRY":
            # Postura de Riposte com capa e florete erguido na vertical
            draw_voxel_box(surface, camera, rx - 0.04, ry - 0.04, rz, 0.08, 0.08, 0.70, COLOR_RAPIER_STEEL, outline=True, alpha=alpha)
            # Brilho de riposte
            draw_voxel_box(surface, camera, rx - 0.08, ry - 0.08, rz + 0.20, 0.16, 0.16, 0.25, COLOR_MUSKETEER_AURA, outline=False, alpha=160)
        else:
            # Florete em repouso
            draw_voxel_box(surface, camera, rx - 0.05, ry - 0.05, rz - 0.04, 0.10, 0.10, 0.08, COLOR_STEEL, outline=True, alpha=alpha)
            draw_voxel_box(surface, camera, rx - 0.03, ry - 0.03, rz + 0.04, 0.06, 0.06, 0.60, COLOR_RAPIER_STEEL, outline=True, alpha=alpha)


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
    Renderiza o cão Doberman articulado totalmente construído em blocos de voxel 3D.
    Suporta postura em pé/trote, salto predatório no CHARGE e nocaute estirado no solo.
    """
    # Nocauteado (deitado no chão)
    if state == "KNOCKED_OUT":
        sx, sy = camera.apply(wx, wy, 0.0)
        pygame.draw.ellipse(surface, (12, 16, 14, 120), (sx - 24, sy - 8, 48, 16))
        # Corpo deitado no chão
        draw_voxel_box(surface, camera, wx - 0.25, wy - 0.15, 0.04, 0.50, 0.30, 0.14, COLOR_DOBERMAN_BLACK, outline=True)
        draw_voxel_box(surface, camera, wx + 0.22, wy - 0.12, 0.04, 0.20, 0.22, 0.15, COLOR_DOBERMAN_BLACK, outline=True)
        return

    # Sombra
    sx, sy = camera.apply(wx, wy, 0.0)
    pygame.draw.ellipse(surface, (12, 16, 14, 140), (sx - 22, sy - 8, 44, 16))

    fx, fy = facing_x, facing_y
    fnorm = math.hypot(fx, fy)
    if fnorm > 0.001:
        fx /= fnorm
        fy /= fnorm
    else:
        fx, fy = 1.0, 0.0

    px = -fy
    py = fx

    is_charge = (state == "CHARGE")
    body_z = wz + (0.28 if is_charge else 0.22)

    # 1. Quatro Patas em Voxel com Manchas Castanhas
    leg_h = 0.25
    paw_swing = math.sin(state_timer * 18.0) * 0.14 if is_charge else 0.0

    # Patas traseiras
    draw_voxel_box(surface, camera, wx - fx * 0.20 + px * 0.10 - 0.05, wy - fy * 0.20 + py * 0.10 - 0.05, wz, 0.10, 0.10, leg_h, COLOR_DOBERMAN_BLACK, outline=True)
    draw_voxel_box(surface, camera, wx - fx * 0.20 - px * 0.10 - 0.05, wy - fy * 0.20 - py * 0.10 - 0.05, wz, 0.10, 0.10, leg_h, COLOR_DOBERMAN_BLACK, outline=True)

    # Patas dianteiras
    draw_voxel_box(surface, camera, wx + fx * 0.18 + px * 0.10 - 0.05 + fx * paw_swing, wy + fy * 0.18 + py * 0.10 - 0.05 + fy * paw_swing, wz, 0.10, 0.10, leg_h, COLOR_DOBERMAN_RUST, outline=True)
    draw_voxel_box(surface, camera, wx + fx * 0.18 - px * 0.10 - 0.05 - fx * paw_swing, wy + fy * 0.18 - py * 0.10 - 0.05 - fy * paw_swing, wz, 0.10, 0.10, leg_h, COLOR_DOBERMAN_RUST, outline=True)

    # 2. Tronco Musculoso do Doberman (Preto e Rust no Peito)
    draw_voxel_box(surface, camera, wx - 0.24, wy - 0.14, body_z, 0.48, 0.28, 0.24, COLOR_DOBERMAN_BLACK, outline=True)
    # Peitoral com manchas castanho-ferrugem
    draw_voxel_box(surface, camera, wx + fx * 0.12 - 0.10, wy + fy * 0.12 - 0.10, body_z + 0.04, 0.20, 0.20, 0.18, COLOR_DOBERMAN_RUST, outline=True)

    # Coleira vermelha
    draw_voxel_box(surface, camera, wx + fx * 0.22 - 0.08, wy + fy * 0.22 - 0.08, body_z + 0.12, 0.16, 0.16, 0.07, COLOR_DOBERMAN_COLLAR, outline=True)

    # 3. Cabeça, Focinho e Orelhas Pontudas
    head_x = wx + fx * 0.32
    head_y = wy + fy * 0.32
    head_z = body_z + 0.16

    # Crânio
    draw_voxel_box(surface, camera, head_x - 0.10, head_y - 0.09, head_z, 0.20, 0.18, 0.18, COLOR_DOBERMAN_BLACK, outline=True)
    # Focinho projetado com queixo castanho
    snout_x = head_x + fx * 0.14
    snout_y = head_y + fy * 0.14
    draw_voxel_box(surface, camera, snout_x - 0.07, snout_y - 0.06, head_z - 0.02, 0.14, 0.12, 0.12, COLOR_DOBERMAN_RUST, outline=True)
    # Nariz preto
    draw_voxel_box(surface, camera, snout_x + fx * 0.06 - 0.03, snout_y + fy * 0.06 - 0.03, head_z + 0.04, 0.06, 0.06, 0.06, (15, 15, 18), outline=False)

    # Orelhas pontudas em pé
    ear_l_x = head_x + px * 0.08
    ear_l_y = head_y + py * 0.08
    draw_voxel_box(surface, camera, ear_l_x - 0.03, ear_l_y - 0.03, head_z + 0.16, 0.06, 0.06, 0.14, COLOR_DOBERMAN_BLACK, outline=True)

    ear_r_x = head_x - px * 0.08
    ear_r_y = head_y - py * 0.08
    draw_voxel_box(surface, camera, ear_r_x - 0.03, ear_r_y - 0.03, head_z + 0.16, 0.06, 0.06, 0.14, COLOR_DOBERMAN_BLACK, outline=True)

    # 4. Cauda curta
    tail_x = wx - fx * 0.26
    tail_y = wy - fy * 0.26
    draw_voxel_box(surface, camera, tail_x - 0.03, tail_y - 0.03, body_z + 0.14, 0.06, 0.06, 0.12, COLOR_DOBERMAN_BLACK, outline=False)


# Helpers para cores dos guerreiros
def _get_char_torso_color(char_type: str):
    if char_type == "kenshin": return COLOR_RED_KIMONO
    if char_type == "musashi": return COLOR_BLUE_KIMONO
    if char_type in ("ninja", "hanzo"): return COLOR_YELLOW_NINJA
    if char_type in ("american", "joe"): return COLOR_AMERICAN_NINJA
    if char_type in ("gray", "kasumi"): return COLOR_GRAY_NINJA
    if char_type in ("purple", "murasaki"): return COLOR_PURPLE_NINJA
    if char_type == "saitou": return COLOR_SAITOU_LIGHT_BLUE
    if char_type == "rifleman": return COLOR_RIFLE_COAT
    if char_type in ("kabuki", "okuni"): return COLOR_OKUNI_KIMONO
    if char_type in ("archer", "tomoe"): return COLOR_ARCHER_KIMONO
    if char_type in ("pirate", "anne"): return COLOR_PIRATE_COAT
    if char_type in ("musketeer", "julie"): return COLOR_MUSKETEER_BLUE
    return (200, 200, 200)

def _get_char_pants_color(char_type: str):
    if char_type == "kenshin": return COLOR_RED_HAKAMA
    if char_type == "musashi": return COLOR_BLUE_HAKAMA
    if char_type in ("ninja", "hanzo"): return COLOR_YELLOW_DARK
    if char_type in ("american", "joe"): return (30, 32, 36)
    if char_type in ("gray", "kasumi"): return COLOR_GRAY_DARK
    if char_type in ("purple", "murasaki"): return COLOR_PURPLE_DARK
    if char_type == "saitou": return COLOR_SAITOU_HAKAMA
    if char_type == "rifleman": return (45, 42, 38)
    if char_type in ("kabuki", "okuni"): return (45, 20, 32)
    if char_type in ("archer", "tomoe"): return COLOR_TOMOE_HAKAMA
    if char_type in ("pirate", "anne"): return (35, 30, 30)
    if char_type in ("musketeer", "julie"): return COLOR_WHITE
    return (150, 150, 150)

def _get_char_hair_color(char_type: str):
    if char_type == "kenshin": return COLOR_RED_HAIR
    if char_type == "musashi": return COLOR_BLUE_HAIR
    if char_type in ("ninja", "hanzo"): return COLOR_YELLOW_NINJA
    if char_type in ("american", "joe"): return (32, 28, 26)
    if char_type in ("gray", "kasumi"): return COLOR_KASUMI_HAIR
    if char_type in ("purple", "murasaki"): return COLOR_PURPLE_NINJA
    if char_type == "saitou": return (25, 25, 30)
    if char_type == "rifleman": return (30, 28, 25)
    if char_type in ("kabuki", "okuni"): return COLOR_KABUKI_HAIR
    if char_type in ("archer", "tomoe"): return (25, 25, 30)
    if char_type in ("pirate", "anne"): return (42, 28, 20)
    if char_type in ("musketeer", "julie"): return (80, 50, 30)
    return (50, 50, 50)

def _get_char_belt_color(char_type: str):
    if char_type == "kenshin": return (25, 25, 30)
    if char_type == "musashi": return (20, 22, 28)
    if char_type in ("ninja", "hanzo"): return (26, 26, 30)
    if char_type in ("american", "joe"): return (45, 48, 52)
    if char_type in ("gray", "kasumi"): return (35, 38, 42)
    if char_type in ("purple", "murasaki"): return (35, 18, 50)
    if char_type == "saitou": return COLOR_WHITE
    if char_type == "rifleman": return (65, 45, 30)
    if char_type in ("kabuki", "okuni"): return COLOR_GOLD
    if char_type in ("archer", "tomoe"): return (60, 55, 48)
    if char_type in ("pirate", "anne"): return COLOR_PIRATE_GOLD
    if char_type in ("musketeer", "julie"): return COLOR_GOLD
    return (20, 20, 20)

def _get_char_mask_color(char_type: str):
    if char_type in ("ninja", "hanzo"): return (26, 26, 30)
    if char_type in ("gray", "kasumi"): return COLOR_GRAY_DARK
    if char_type in ("purple", "murasaki"): return COLOR_PURPLE_DARK
    return (30, 30, 30)
