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
    is_female: bool = True,
    char_type: str = "kenshin"
):
    """
    Calcula as posições 3D anatômicas das juntas das pernas (coxa, joelho/canela e pé).
    Aplica flexão natural na passada durante a caminhada e posturas marciais no idle.
    Retorna dict com dados de cada perna.
    """
    char_type = char_type.lower()
    walk_phase = walk_timer * 9.0
    walk_swing = math.sin(walk_phase) if is_moving else 0.0
    # Elevação de passada fluida na marcha
    walk_lift_l = max(0.0, math.sin(walk_phase)) * 0.10 if is_moving else 0.0
    walk_lift_r = max(0.0, -math.sin(walk_phase)) * 0.10 if is_moving else 0.0

    legs = {}
    for side, lift, swing in [("L", walk_lift_l, walk_swing), ("R", walk_lift_r, -walk_swing)]:
        s_sign = 1.0 if side == "L" else -1.0
        hip_x = base_x + px * hip_width * s_sign
        hip_y = base_y + py * hip_width * s_sign
        hip_z = base_z + (0.48 if is_female else 0.46)

        if is_attack:
            knee_fwd = 0.18 if side == "R" else -0.14
            foot_fwd = 0.32 if side == "R" else -0.24
            knee_lift = -0.04 if side == "R" else -0.02
        elif is_moving:
            # Passada natural: joelho flexiona e avança no lift enquanto a perna de apoio empurra
            knee_fwd = swing * 0.16 + (lift * 0.55)
            foot_fwd = swing * 0.26
            knee_lift = lift * 0.45
        else:
            # Posturas marciais de pés no IDLE
            if "kenshin" in char_type or "kenshi" in char_type:
                # Kenshi: Pé esquerdo à frente, perna direita recuada em mola de saque Iai
                foot_fwd = 0.07 if side == "L" else -0.06
                knee_fwd = 0.03 if side == "L" else -0.02
                knee_lift = -0.02
            elif "musashi" in char_type:
                # Musashi: base larga e firme de duas espadas, joelhos levemente flexionados
                foot_fwd = 0.10 if side == "R" else -0.09
                knee_fwd = 0.05 if side == "R" else -0.04
                knee_lift = -0.01
            elif "ninja" in char_type or "hanzo" in char_type or "kasumi" in char_type:
                # Ninja: Postura abaixada e ágil com centro de massa baixo
                foot_fwd = 0.06 if side == "R" else -0.06
                knee_fwd = 0.04 if side == "R" else -0.02
                knee_lift = -0.04
            elif "saitou" in char_type or "musketeer" in char_type:
                # Esgrima/Gatotsu: perfil lateral, perna guia dianteira estendida
                foot_fwd = 0.09 if side == "R" else -0.08
                knee_fwd = 0.05 if side == "R" else -0.03
                knee_lift = -0.015
            elif "kabuki" in char_type or "okuni" in char_type:
                # Kabuki: pés delicadamente alinhados na 3ª posição
                foot_fwd = 0.04 if side == "L" else -0.04
                knee_fwd = 0.02
                knee_lift = -0.01
            elif "pirate" in char_type or "anne" in char_type:
                # Pirata: base firme e espaçada de convés marítimo
                foot_fwd = 0.06 if side == "R" else -0.06
                knee_fwd = 0.02
                knee_lift = -0.02
            else:
                foot_fwd = 0.04 if side == "R" else -0.04
                knee_fwd = 0.02 if side == "R" else -0.02
                knee_lift = -0.015

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


def calc_character_idle_pose(
    char_type: str,
    base_x: float, base_y: float, torso_z: float,
    fx: float, fy: float, px: float, py: float,
    walk_timer: float,
    extra_props: dict = None
):
    """
    Calcula poses exclusivas de IDLE para cada um dos 12 lutadores, refletindo seu
    temperamento marcial, empunhadura e estilo de combate, com respiração suave.
    Retorna: (arm_l_xyz, arm_r_xyz, weapon_data)
    """
    if extra_props is None:
        extra_props = {}

    char_type = char_type.lower()
    breathe = math.sin(walk_timer * 2.8) * 0.015
    tz = torso_z + breathe

    if char_type in ("kenshin", "kenshi", "red"):
        # Kenshi (Battojutsu): Katana embainhada na cintura esquerda.
        # Mão esquerda repousa na boca da bainha (saya), mão direita engatilhada sobre a empunhadura (tsuka).
        arm_l = (
            base_x - px * 0.13 - fx * 0.03,
            base_y - py * 0.13 - fy * 0.03,
            tz - 0.06
        )
        arm_r = (
            base_x - px * 0.05 + fx * 0.06,
            base_y - py * 0.05 + fy * 0.06,
            tz - 0.02
        )
        return arm_l, arm_r, {"pose": "IAI_SHEATHED"}

    elif char_type in ("musashi", "blue"):
        # Musashi (Niten Ichi-ryū): Postura dupla de duas lâminas desembainhadas em combate!
        # Braço direito à frente com Katana em Chūdan-no-kamae (guarda média),
        # Braço esquerdo cruzando o plexo com a Wakizashi em guarda baixa invertida.
        arm_r = (
            base_x + fx * 0.20 - px * 0.08,
            base_y + fy * 0.20 - py * 0.08,
            tz + 0.12
        )
        arm_l = (
            base_x + fx * 0.08 + px * 0.12,
            base_y + fy * 0.08 + py * 0.12,
            tz + 0.02
        )
        return arm_l, arm_r, {"pose": "NITEN_DUAL_BLADES"}

    elif char_type in ("ninja", "yellow_ninja", "hanzo"):
        # Hanzo (Shinobi): Postura abaixada e furtiva.
        # Braço direito à frente empunhando kunai, braço esquerdo colado à silhueta com tantō nas costas.
        arm_r = (
            base_x + fx * 0.16 - px * 0.08,
            base_y + fy * 0.16 - py * 0.08,
            tz + 0.08
        )
        arm_l = (
            base_x - fx * 0.08 + px * 0.14,
            base_y - fy * 0.08 + py * 0.14,
            tz + 0.04
        )
        return arm_l, arm_r, {"pose": "SHINOBI_KUNAI"}

    elif char_type in ("tomoe", "archer", "kyudo"):
        # Tomoe (Miko Arqueira): Postura aprumada e solene de kyudo cerimonial.
        # Braço esquerdo segurando o grande arco Yumi verticalmente ao chão.
        # Braço direito descansando na dobra do hakama/aljava.
        arm_l = (
            base_x + px * 0.16 + fx * 0.05,
            base_y + py * 0.16 + fy * 0.05,
            tz + 0.06
        )
        arm_r = (
            base_x - px * 0.14,
            base_y - py * 0.14,
            tz - 0.02
        )
        return arm_l, arm_r, {"pose": "YUMI_VERTICAL"}

    elif char_type in ("saitou", "saito"):
        # Saitou (Gatotsu Kamae): Perfilado afiado.
        # Braço esquerdo estendido apontando a espada horizontalmente nos olhos do rival.
        # Braço direito engatilhado junto ao colarinho/ombro segurando o pomo da espada.
        arm_l = (
            base_x + fx * 0.28,
            base_y + fy * 0.28,
            tz + 0.15
        )
        arm_r = (
            base_x - fx * 0.06 - px * 0.12,
            base_y - fy * 0.06 - py * 0.12,
            tz + 0.15
        )
        return arm_l, arm_r, {"pose": "GATOTSU_STANCE"}

    elif char_type in ("okuni", "kabuki"):
        # Okuni (Dançarina Kabuki): Posição teatral graciosa.
        # Ambos os braços dobrados delicadamente à frente da cintura segurando os leques cruzados.
        # Direita ergue o leque aberto junto ao rosto (como no conceito); esquerda segura o leque fechado baixo e cruzado.
        arm_r = (base_x + fx * 0.07 - px * 0.14, base_y + fy * 0.07 - py * 0.14, tz + 0.30)
        arm_l = (base_x + fx * 0.11 + px * 0.07, base_y + fy * 0.11 + py * 0.07, tz - 0.03)
        return arm_l, arm_r, {"pose": "KABUKI_FANS"}

    elif char_type in ("rifleman", "teppo"):
        # Teppo (Arcabuzeiro): Guarda de infantaria com Tanegashima.
        # Ambas as mãos segurando o arcabuz em diagonal cruzando o peito.
        arm_l = (
            base_x + fx * 0.20 + px * 0.06,
            base_y + fy * 0.20 + py * 0.06,
            tz + 0.10
        )
        arm_r = (
            base_x - fx * 0.02 - px * 0.10,
            base_y - fy * 0.02 - py * 0.10,
            tz + 0.06
        )
        return arm_l, arm_r, {"pose": "TANEGASHIMA_REST"}

    elif char_type in ("pirate", "anne"):
        # Anne (A Pirata): Postura de desafio de convés.
        # Mão direita apoiando o alfanje pesado de costas sobre o ombro.
        # Mão esquerda descansando no cinto/fivela dourada.
        arm_r = (
            base_x - px * 0.13 - fx * 0.04,
            base_y - py * 0.13 - fy * 0.04,
            tz + 0.24
        )
        arm_l = (
            base_x + px * 0.15,
            base_y + py * 0.15,
            tz - 0.02
        )
        return arm_l, arm_r, {"pose": "CUTLASS_SHOULDER"}

    elif char_type in ("musketeer", "julie"):
        # Julie (Mosqueteira): Postura clássica de esgrima En Garde.
        # Braço direito projetado à frente com o florete, braço esquerdo em arco arqueado atrás.
        arm_r = (
            base_x + fx * 0.24 - px * 0.04,
            base_y + fy * 0.24 - py * 0.04,
            tz + 0.14
        )
        arm_l = (
            base_x - fx * 0.16 + px * 0.14,
            base_y - fy * 0.16 + py * 0.14,
            tz + 0.22
        )
        return arm_l, arm_r, {"pose": "EN_GARDE_RAPIER"}

    elif char_type in ("american", "joe"):
        # Joe (American Ninja): Guarda de combate corpo a corpo tático.
        # Punhos erguidos protegendo mandíbula e queixo.
        arm_l = (
            base_x + fx * 0.14 + px * 0.08,
            base_y + fy * 0.14 + py * 0.08,
            tz + 0.18
        )
        arm_r = (
            base_x + fx * 0.14 - px * 0.08,
            base_y + fy * 0.14 - py * 0.08,
            tz + 0.18
        )
        return arm_l, arm_r, {"pose": "TACTICAL_GUARD"}

    elif char_type in ("kasumi", "gray"):
        # Kasumi (Kunoichi Cinza): Agilidade e adagas prontas.
        arm_r = (
            base_x + fx * 0.14 - px * 0.10,
            base_y + fy * 0.14 - py * 0.10,
            tz + 0.08
        )
        arm_l = (
            base_x - fx * 0.06 + px * 0.12,
            base_y - fy * 0.06 + py * 0.12,
            tz + 0.04
        )
        return arm_l, arm_r, {"pose": "KASUMI_DAGGER"}

    elif char_type in ("murasaki", "purple"):
        # Murasaki (Kunoichi de Foice e Corrente): Foice à frente, corrente pendendo suavemente.
        chain_swing = math.sin(walk_timer * 2.2) * 0.04
        arm_r = (
            base_x + fx * 0.16 - px * 0.08,
            base_y + fy * 0.16 - py * 0.08,
            tz + 0.08
        )
        arm_l = (
            base_x - fx * 0.04 + px * 0.14,
            base_y - fy * 0.04 + py * 0.14,
            tz + 0.06 + chain_swing
        )
        return arm_l, arm_r, {"pose": "KUSARIGAMA_READY"}

    # Padrão
    arm_l = (base_x + px * 0.14, base_y + py * 0.14, tz + 0.06)
    arm_r = (base_x - px * 0.14, base_y - py * 0.14, tz + 0.06)
    return arm_l, arm_r, {"pose": "DEFAULT"}

