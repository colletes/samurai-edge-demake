"""
Módulo de Cinemática Procedural e Rigging de Membros Articulados para Samurai Edge.
Calcula transformações de juntas 3D (Forward Kinematics) para:
- Pernas: Coxa, Joelho/Canela e Pés com Sandálias Waraji/Geta.
- Braços: Ombro/Manga, Cotovelo/Antebraço e Mãos.
- Armas e Lâminas: Orientação angular contínua 3D ao longo do arco de ataque (nunca estáticas em eixos puros).
"""
import math

def calc_leg_joints(
    base_x: float, base_y: float, base_z: float,
    fx: float, fy: float, px: float, py: float,
    is_moving: bool, walk_timer: float,
    is_attack: bool, atk_progress: float,
    hip_width: float = 0.08,
    is_female: bool = True
):
    """
    Calcula as posições 3D anatômicas das juntas das pernas (coxa, joelho/canela e pé).
    Retorna dict com dados de cada perna.
    """
    walk_swing = math.sin(walk_timer * 9.0) if is_moving else 0.0
    walk_lift_l = max(0.0, math.sin(walk_timer * 9.0)) * 0.085 if is_moving else 0.0
    walk_lift_r = max(0.0, -math.sin(walk_timer * 9.0)) * 0.085 if is_moving else 0.0

    legs = {}
    for side, lift, swing in [("L", walk_lift_l, walk_swing), ("R", walk_lift_r, -walk_swing)]:
        s_sign = 1.0 if side == "L" else -1.0
        hip_x = base_x + px * hip_width * s_sign
        hip_y = base_y + py * hip_width * s_sign
        hip_z = base_z + (0.48 if is_female else 0.46)

        if is_attack:
            # Agachamento elástico na perna traseira e estiramento na dianteira
            knee_fwd = 0.18 if side == "R" else -0.14
            foot_fwd = 0.32 if side == "R" else -0.24
            knee_lift = -0.04 if side == "R" else -0.02
        elif is_moving:
            knee_fwd = fx * swing * 0.13
            foot_fwd = fx * swing * 0.22
            knee_lift = lift * 0.4
        else:
            knee_fwd = 0.0
            foot_fwd = 0.0
            knee_lift = 0.0

        thigh_x = hip_x + fx * (knee_fwd * 0.35)
        thigh_y = hip_y + fy * (knee_fwd * 0.35)
        thigh_z = hip_z - 0.22

        shin_x = hip_x + fx * knee_fwd
        shin_y = hip_y + fy * knee_fwd
        shin_z = base_z + 0.06 + lift + knee_lift

        foot_x = hip_x + fx * foot_fwd
        foot_y = hip_y + fy * foot_fwd
        foot_z = base_z + lift

        legs[side] = {
            "thigh": (thigh_x, thigh_y, thigh_z),
            "shin": (shin_x, shin_y, shin_z),
            "foot": (foot_x, foot_y, foot_z),
            "lift": lift
        }

    return legs


def calc_blade_slash_3d(
    char_type: str, state: str, atk_progress: float,
    base_x: float, base_y: float, torso_z: float,
    fx: float, fy: float, px: float, py: float,
    extra_props: dict = None
):
    """
    Calcula a orientação tridimensional fluida da espada/arma ao longo do golpe.
    A lâmina flui em ângulo diagonal ou arco curvo no espaço 3D, nunca estática.
    Retorna: (origin, dir_vec, up_vec, length, width, height)
    """
    if extra_props is None:
        extra_props = {}

    if char_type in ("kenshin", "kenshi"):
        # Kenshi Iai Flash: Arco diagonal contínuo cortando de baixo-esquerda para cima-direita
        # Ângulo horizontal percorre de -45° até +75°
        sweep_angle = -0.80 + atk_progress * 2.20
        # Inclinação vertical (pitch): inicia levemente descendente e sobe no clímax do corte
        pitch_angle = -0.35 + math.sin(atk_progress * math.pi) * 0.70

        # Posição da empunhadura (guarda Tsuba)
        reach = 0.28 + math.sin(atk_progress * math.pi) * 0.25
        hx = base_x + fx * math.cos(sweep_angle) * reach - px * math.sin(sweep_angle) * reach
        hy = base_y + fy * math.cos(sweep_angle) * reach - py * math.sin(sweep_angle) * reach
        hz = torso_z + 0.16 + pitch_angle * 0.20

        # Vetor de direção da lâmina ao longo do corte (tangente do arco)
        blade_dir_x = fx * math.cos(sweep_angle + 0.35) - px * math.sin(sweep_angle + 0.35)
        blade_dir_y = fy * math.cos(sweep_angle + 0.35) - py * math.sin(sweep_angle + 0.35)
        blade_dir_z = math.sin(pitch_angle) * 0.85

        # Normalizar
        norm = math.hypot(blade_dir_x, blade_dir_y, blade_dir_z)
        if norm > 0.0001:
            blade_dir_x /= norm; blade_dir_y /= norm; blade_dir_z /= norm

        # Vetor Up da lâmina (fio de corte voltado na direção do golpe)
        up_x = -blade_dir_y * 0.4
        up_y = blade_dir_x * 0.4
        up_z = 0.9

        return {
            "origin": (hx, hy, hz),
            "dir": (blade_dir_x, blade_dir_y, blade_dir_z),
            "up": (up_x, up_y, up_z),
            "length": 0.72,
            "width": 0.05,
            "height": 0.04
        }

    elif char_type == "musashi":
        combo_step = extra_props.get("combo_step", 1)
        if combo_step == 1:
            # Corte 1: Katana descendo em corte diagonal pesado
            pitch = -0.85 + atk_progress * 1.50
            hx = base_x + fx * (0.24 + atk_progress * 0.25) - px * 0.08
            hy = base_y + fy * (0.24 + atk_progress * 0.25) - py * 0.08
            hz = torso_z + 0.38 - atk_progress * 0.34
            dir_x = fx * 0.60 - px * 0.30
            dir_y = fy * 0.60 - py * 0.30
            dir_z = -0.75 + atk_progress * 0.30
            length = 0.68
        elif combo_step == 2:
            # Corte 2: Wakizashi subindo em diagonal inversa
            hx = base_x + fx * (0.22 + atk_progress * 0.25) + px * 0.08
            hy = base_y + fy * (0.22 + atk_progress * 0.25) + py * 0.08
            hz = torso_z + 0.08 + atk_progress * 0.32
            dir_x = fx * 0.55 + px * 0.35
            dir_y = fy * 0.55 + py * 0.35
            dir_z = 0.70
            length = 0.50
        else:
            # Corte 3: Cruzamento frontal duplo
            hx = base_x + fx * 0.32
            hy = base_y + fy * 0.32
            hz = torso_z + 0.18
            dir_x = fx * 0.70
            dir_y = fy * 0.70
            dir_z = 0.15
            length = 0.65

        norm = math.hypot(dir_x, dir_y, dir_z)
        if norm > 0.0001:
            dir_x /= norm; dir_y /= norm; dir_z /= norm

        return {
            "origin": (hx, hy, hz),
            "dir": (dir_x, dir_y, dir_z),
            "up": (0.0, 0.0, 1.0),
            "length": length,
            "width": 0.05,
            "height": 0.04
        }

    elif char_type in ("saitou", "saito"):
        # Gatotsu: Estocada transfixante horizontal-penetrante
        reach = math.sin(atk_progress * math.pi) * 0.40 if state == "ZEROSHIKI" else 0.28
        hx = base_x + fx * (0.35 + reach)
        hy = base_y + fy * (0.35 + reach)
        hz = torso_z + 0.18
        dir_x, dir_y, dir_z = fx, fy, -0.08  # Ligeira inclinação descendente letal
        return {
            "origin": (hx, hy, hz),
            "dir": (dir_x, dir_y, dir_z),
            "up": (0.0, 0.0, 1.0),
            "length": 0.74,
            "width": 0.05,
            "height": 0.04
        }

    elif char_type in ("musketeer", "julie"):
        # Fleche: Florete em linha de estocada pura com o braço estendido
        reach = math.sin(atk_progress * math.pi) * 0.48
        hx = base_x + fx * (0.28 + reach) - px * 0.04
        hy = base_y + fy * (0.28 + reach) - py * 0.04
        hz = torso_z + 0.18
        dir_x, dir_y, dir_z = fx, fy, 0.02
        return {
            "origin": (hx, hy, hz),
            "dir": (dir_x, dir_y, dir_z),
            "up": (0.0, 0.0, 1.0),
            "length": 0.80,
            "width": 0.035,
            "height": 0.035
        }

    elif char_type in ("pirate", "anne"):
        # Cutlass: Corte curvo naval de 180 graus
        sw_a = -1.60 + atk_progress * 3.20
        hx = base_x + fx * math.cos(sw_a) * 0.32 - px * math.sin(sw_a) * 0.32
        hy = base_y + fy * math.cos(sw_a) * 0.32 - py * math.sin(sw_a) * 0.32
        hz = torso_z + 0.16
        dir_x = fx * math.cos(sw_a + 0.50) - px * math.sin(sw_a + 0.50)
        dir_y = fy * math.cos(sw_a + 0.50) - py * math.sin(sw_a + 0.50)
        dir_z = -0.20
        norm = math.hypot(dir_x, dir_y, dir_z)
        if norm > 0.0001:
            dir_x /= norm; dir_y /= norm; dir_z /= norm
        return {
            "origin": (hx, hy, hz),
            "dir": (dir_x, dir_y, dir_z),
            "up": (0.0, 0.0, 1.0),
            "length": 0.62,
            "width": 0.07,
            "height": 0.04
        }

    # Padrão para outros
    hx = base_x + fx * 0.35
    hy = base_y + fy * 0.35
    hz = torso_z + 0.16
    return {
        "origin": (hx, hy, hz),
        "dir": (fx, fy, 0.0),
        "up": (0.0, 0.0, 1.0),
        "length": 0.60,
        "width": 0.05,
        "height": 0.04
    }
