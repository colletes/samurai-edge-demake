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
    COLOR_SAITOU_LIGHT_BLUE, COLOR_SAITOU_HAORI_DARK, COLOR_SAITOU_HAKAMA, COLOR_SAITOU_AURA
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

    # Normalizar nomes de char_type para aceitar sufixos _ninja
    char_type = char_type.lower()
    if "yellow" in char_type: char_type = "ninja"
    elif "american" in char_type: char_type = "american"
    elif "gray" in char_type or "kemuri" in char_type: char_type = "gray"
    elif "purple" in char_type or "murasaki" in char_type: char_type = "purple"
    elif "kenshin" in char_type or "red" in char_type: char_type = "kenshin"
    elif "musashi" in char_type or "blue" in char_type: char_type = "musashi"
    elif "saitou" in char_type or "saito" in char_type: char_type = "saitou"

    # Estado de Morte (corpo tombado em blocos no solo)
    if not is_alive or state == "DEAD":
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

    elif char_type in ("ninja", "gray", "purple"):
        # Capuz shinobi completo
        hood_col = col_torso
        draw_voxel_box(surface, camera, base_x - 0.17, base_y - 0.15, head_z + 0.16, 0.34, 0.30, 0.16, hood_col, outline=True, alpha=alpha)
        # Máscara cobrindo boca e nariz
        draw_voxel_box(surface, camera, base_x - 0.16 + fx * 0.04, base_y - 0.14 + fy * 0.04, head_z, 0.32, 0.28, 0.16, _get_char_mask_color(char_type), outline=True, alpha=alpha)

    elif char_type == "american":
        # Cabelo curto e bandana vermelha icônica
        draw_voxel_box(surface, camera, base_x - 0.16, base_y - 0.14, head_z + 0.20, 0.32, 0.28, 0.12, (32, 28, 26), outline=True, alpha=alpha)
        # Faixa vermelha da bandana
        draw_voxel_box(surface, camera, base_x - 0.17, base_y - 0.15, head_z + 0.16, 0.34, 0.30, 0.08, COLOR_AMERICAN_BANDANA, outline=True, alpha=alpha)

    elif char_type == "saitou":
        # Cabelo preto samurai com a franja frontal de Saitou
        draw_voxel_box(surface, camera, base_x - 0.16, base_y - 0.14, head_z + 0.20, 0.32, 0.28, 0.12, (25, 25, 30), outline=True, alpha=alpha)
        # Franja frontal pontuda característica
        draw_voxel_box(surface, camera, base_x - 0.08 + fx * 0.10, base_y - 0.08 + fy * 0.10, head_z + 0.12, 0.16, 0.16, 0.10, (25, 25, 30), outline=False, alpha=alpha)

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
    if char_type == "ninja": return COLOR_YELLOW_NINJA
    if char_type == "american": return COLOR_AMERICAN_NINJA
    if char_type == "gray": return COLOR_GRAY_NINJA
    if char_type == "purple": return COLOR_PURPLE_NINJA
    if char_type == "saitou": return COLOR_SAITOU_LIGHT_BLUE
    return (200, 200, 200)

def _get_char_pants_color(char_type: str):
    if char_type == "kenshin": return COLOR_RED_HAKAMA
    if char_type == "musashi": return COLOR_BLUE_HAKAMA
    if char_type == "ninja": return COLOR_YELLOW_DARK
    if char_type == "american": return (30, 32, 36)
    if char_type == "gray": return COLOR_GRAY_DARK
    if char_type == "purple": return COLOR_PURPLE_DARK
    if char_type == "saitou": return COLOR_SAITOU_HAKAMA
    return (150, 150, 150)

def _get_char_hair_color(char_type: str):
    if char_type == "kenshin": return COLOR_RED_HAIR
    if char_type == "musashi": return COLOR_BLUE_HAIR
    if char_type == "ninja": return COLOR_YELLOW_NINJA
    if char_type == "american": return (32, 28, 26)
    if char_type == "gray": return COLOR_GRAY_NINJA
    if char_type == "purple": return COLOR_PURPLE_NINJA
    if char_type == "saitou": return (25, 25, 30)
    return (50, 50, 50)

def _get_char_belt_color(char_type: str):
    if char_type == "kenshin": return (25, 25, 30)
    if char_type == "musashi": return (20, 22, 28)
    if char_type == "ninja": return (26, 26, 30)
    if char_type == "american": return (45, 48, 52)
    if char_type == "gray": return (35, 38, 42)
    if char_type == "purple": return (35, 18, 50)
    if char_type == "saitou": return COLOR_WHITE
    return (20, 20, 20)

def _get_char_mask_color(char_type: str):
    if char_type == "ninja": return (26, 26, 30)
    if char_type == "gray": return COLOR_GRAY_DARK
    if char_type == "purple": return COLOR_PURPLE_DARK
    return (30, 30, 30)
