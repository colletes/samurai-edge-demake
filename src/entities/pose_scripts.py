"""
Roteiros de pose da introdução (7.3) e da vitória (7.4) de cada lutador.

Cada roteiro é uma lista de trechos sobre o progresso `p` de 0 a 1. Um trecho escolhe o estado de pose do renderer
(IDLE, ATTACK, PARRY, GATOTSU_CHARGE...) e o progresso desse estado, de modo que a pose reaproveita as animações
e as armas que cada modelo já desenha (saque, giro da corrente, leques, arco...). A função é pura: o mesmo `p`
sempre dá a mesma pose, então pular, repetir e capturar quadros funcionam. Não há hitbox nem gameplay aqui.
"""
from dataclasses import dataclass, field

INTRO_DURATION = 2.0      # segundos de animação dentro dos 2.4 s do ato (o resto é pose final parada)
VICTORY_FULL = 3.2        # vitória que fecha a partida
VICTORY_SHORT = 1.6       # vitória de um round que não fecha a partida
VICTORY_RETURN = 0.6      # câmera volta à vista clássica depois da pose

# Duração de cada estado de golpe no renderer (`atk_progress = 1 - state_timer / duração`).
ATTACK_DURATION = {"kenshin": 0.16, "musashi": 0.18, "pirate": 0.22, "anne": 0.22, "musketeer": 0.24, "julie": 0.24,
                   "purple": 0.16, "ninja": 0.18, "saitou": 0.25, "ren": 0.14, "chiyo": 0.14, "benkei": 0.32, "orin": 0.20,
                   "goro": 0.26, "ichi": 0.16, "valerius": 0.20, "seimei": 0.18, "daiki": 0.20, "aoi": 0.17, "raiden": 0.22}
DEFAULT_ATTACK_DURATION = 0.20
STATE_DURATION = {"PARRY": 0.45, "CAPE_FLOURISH": 0.5, "KIAI": 0.35, "MAI_DANCE": 0.36}
MELEE_STATES = ("ATTACK", "CUTLASS_CLEAVE", "FLECHE", "ZEROSHIKI", "GATOTSU_CHARGE", "KIAI", "MAI_DANCE", "POLE_VAULT", "PLANT_TRAP", "TACHIAI_TACKLE", "TSUPPARI_RUSH", "TSUPPARI_STRIKE_1", "TSUPPARI_STRIKE_2")


@dataclass
class PoseFrame:
    state: str = "IDLE"
    progress: float = 0.0
    extra: dict = field(default_factory=dict)
    alpha: float = 1.0


def canonical(char_type: str) -> str:
    """Nome canônico do lutador, igual ao que `render_voxel_humanoid` usa para escolher o modelo."""
    c = char_type.lower()
    if "yellow" in c:
        return "ninja"
    if "american" in c:
        return "american"
    if "gray" in c or "kemuri" in c or "kasumi" in c:
        return "kasumi"
    if "purple" in c or "murasaki" in c:
        return "murasaki"
    if "kenshin" in c or "kenshi" in c or "red" in c:
        return "kenshin"
    if "musashi" in c or "blue" in c:
        return "musashi"
    if "saitou" in c or "saito" in c:
        return "saitou"
    if "rifle" in c or "teppo" in c:
        return "rifleman"
    if "kabuki" in c or "okuni" in c:
        return "okuni"
    if "archer" in c or "kyudo" in c or "tomoe" in c:
        return "tomoe"
    if "pirate" in c or "anne" in c or "sayuri" in c:
        return "pirate"
    if "musketeer" in c or "julie" in c:
        return "musketeer"
    if "ren" in c or "shaolin" in c:
        return "ren"
    if "chiyo" in c or "nodachi" in c or "kodachi" in c:
        return "chiyo"
    if "benkei" in c or "sohei" in c:
        return "benkei"
    if "orin" in c or "minstrel" in c:
        return "orin"
    if "goro" in c or "farmer" in c or "kuwa" in c:
        return "goro"
    if "ichi" in c or "blind" in c or "shikomizue" in c:
        return "ichi"
    if "valerius" in c or "necromancer" in c:
        return "valerius"
    if "seimei" in c or "onmyoji" in c:
        return "seimei"
    if "daiki" in c or "pilgrim" in c or "bostaff" in c:
        return "daiki"
    if "aoi" in c or "ainu" in c or "huntress" in c:
        return "aoi"
    if "raiden" in c or "sumo" in c or "rikishi" in c:
        return "raiden"
    return c


def _seg(t0, t1, state="IDLE", a0=0.0, a1=None, alpha=(1.0, 1.0), **extra):
    return (t0, t1, state, a0, a0 if a1 is None else a1, alpha, extra)


def _idle(t0, t1, alpha=(1.0, 1.0), **extra):
    return _seg(t0, t1, "IDLE", 0.0, 0.0, alpha, **extra)


INTRO = {
    # Kenshi (2.1.5): Meditação serena de olhos fechados -> abre os olhos âmbar com brilho intenso e destrava a tsuba com o polegar (Koiguchi-kiri clink + faísca dourada) -> saque relâmpago e retorno à guarda
    "kenshin": [
        _idle(0.0, 0.36, pose="meditation_eyes_closed", eyes_closed=True),
        _idle(0.36, 0.66, pose="koiguchi_glint", eye_glint_boost=1.0),
        _seg(0.66, 0.88, "ATTACK", 0.0, 1.0),
        _idle(0.88, 1.0),
    ],
    # Musashi (2.2.5): Saque duplo de ambas as espadas -> atrito de lâminas em 'X' com faíscas metálicas ('shhh-clink') -> transição contínua para a guarda de duelo
    "musashi": [
        _idle(0.0, 0.30, pose="dual_draw"),
        _idle(0.30, 0.65, pose="cross_blade_clash"),
        _idle(0.65, 1.0, pose="two_heavens_guard"),
    ],
    # Hanzo (2.3.8): Redemoinho de folhas secas revela Hanzo agachado em guarda -> saque da Ninjato das costas com estalo metálico -> guarda baixa invertida
    "ninja": [
        _idle(0.0, 0.35, pose="leaf_crouch"),
        _idle(0.35, 0.70, pose="ninjato_draw"),
        _idle(0.70, 1.0, pose="shinobi_stance"),
    ],
    # Shuriken/kunai e o cão que chega correndo
    "american": [_idle(0.0, 0.25), _seg(0.25, 0.65, "ATTACK", 0.0, 1.0), _idle(0.65, 1.0)],
    # Postura do Gatotsu: lâmina apontada à frente
    "saitou": [_idle(0.0, 0.2), _seg(0.2, 0.75, "GATOTSU_CHARGE", 0.2, 0.7), _idle(0.75, 1.0)],
    # Coronhada do arcabuz
    "rifleman": [_idle(0.0, 0.2), _seg(0.2, 0.6, "ATTACK", 0.0, 1.0), _idle(0.6, 1.0)],
    # Dois giros da bola da corrente
    "murasaki": [_idle(0.0, 0.1), _seg(0.1, 0.45, "ATTACK", 0.0, 1.0), _seg(0.45, 0.8, "ATTACK", 0.0, 1.0), _idle(0.8, 1.0)],
    # Surge da fumaça (alfa 0 a 1) e arremessa a bomba
    "kasumi": [_idle(0.0, 0.5, alpha=(0.0, 1.0)), _seg(0.5, 0.82, "ATTACK", 0.0, 1.0), _idle(0.82, 1.0)],
    # Leques e a pose "mie" congelada
    "okuni": [_idle(0.0, 0.15), _seg(0.15, 0.5, "ATTACK", 0.0, 0.5), _seg(0.5, 0.82, "ATTACK", 0.5, 0.5), _idle(0.82, 1.0)],
    # Arco levantado, flecha encaixada e corda esticada
    "tomoe": [_idle(0.0, 0.15), _seg(0.15, 0.82, "ATTACK", 0.2, 0.8, is_drawing=True), _idle(0.82, 1.0)],
    # Corte do alfanje
    "pirate": [_idle(0.0, 0.15), _seg(0.15, 0.55, "CUTLASS_CLEAVE", 0.0, 1.0), _idle(0.55, 1.0)],
    # Estocada do florete e floreio da capa
    "musketeer": [_idle(0.0, 0.15), _seg(0.15, 0.5, "FLECHE", 0.0, 1.0), _seg(0.5, 0.82, "CAPE_FLOURISH", 0.5, 0.5), _idle(0.82, 1.0)],
    # Ren (Shaolin): Saudação Baoquan (punho na palma), Jab Direto, Chute Alto do Dragão com Chi e guarda Shaolin
    "ren": [
        _seg(0.0, 0.25, "IDLE", 0.0, 1.0, pose="shaolin_salute"),
        _seg(0.25, 0.48, "ATTACK", 0.0, 1.0, combo_step=1),
        _seg(0.48, 0.78, "ATTACK", 0.0, 1.0, combo_step=3),
        _idle(0.78, 1.0),
    ],
    # Chiyo (Duas Kodachi): Surge da fumaça sacando as duas Kodachi das costas, corte diagonal, tesoura cruzada em 'X' e guarda
    "chiyo": [
        _seg(0.0, 0.28, "IDLE", 0.0, 1.0, alpha=(0.15, 1.0), pose="kodachi_draw"),
        _seg(0.28, 0.54, "ATTACK", 0.0, 1.0, combo_step=1),
        _seg(0.54, 0.82, "ATTACK", 0.0, 1.0, combo_step=3),
        _idle(0.82, 1.0),
    ],
    # Benkei (Sōhei Warrior Monk): Bate o cabo de ferro da naginata no chão, ergue a manopla em desafio e assume guarda inabalável
    "benkei": [
        _idle(0.0, 0.20),
        _seg(0.20, 0.65, "ATTACK", 0.0, 1.0),
        _idle(0.65, 1.0, pose="iron_guard"),
    ],
    # O-Rin (Menestrel Shamisen): Dedilha o shamisen com o plectro bachi, gira com leveza e assume postura de cortesã
    "orin": [
        _idle(0.0, 0.20),
        _seg(0.20, 0.68, "ATTACK", 0.0, 1.0),
        _idle(0.68, 1.0, pose="courtesan_stance"),
    ],
    # Goro (Fazendeiro da Kuwa): Descida da Kuwa rachando o solo, poeira e guarda de ferro
    "goro": [
        _idle(0.0, 0.20),
        _seg(0.20, 0.65, "ATTACK", 0.0, 1.0),
        _idle(0.65, 1.0, pose="iron_guard"),
    ],
    # Ichi (Lâmina Cega): Postura de escuta sensorial, saque relâmpago Gyaku-Iai em leque e embainhar sereno
    "ichi": [
        _idle(0.0, 0.25, pose="listen_stance"),
        _seg(0.25, 0.65, "ATTACK", 0.0, 1.0),
        _idle(0.65, 1.0, pose="sheath_click"),
    ],
    # Valerius (Necromante Prussiano): Vórtice fúnebre, corte cerimonial da foice e postura aristocrática
    "valerius": [
        _idle(0.0, 0.20),
        _seg(0.20, 0.65, "ATTACK", 0.0, 1.0),
        _idle(0.65, 1.0, pose="aristocrat_stance"),
    ],
    # Seimei (Mestra Onmyoji): Meditação astral, lançamento celestial de Ofuda com leque e reverência
    "seimei": [
        _idle(0.0, 0.20),
        _seg(0.20, 0.65, "ATTACK", 0.0, 1.0),
        _idle(0.65, 1.0, pose="onmyo_guard"),
    ],
    # Daiki (Peregrino do Bastão Bō): Saudação de peregrino, giro veloz de Bō levantando folhas e guarda Chudan
    "daiki": [
        _idle(0.0, 0.22, pose="pilgrim_bow"),
        _seg(0.22, 0.68, "ATTACK", 0.0, 1.0),
        _idle(0.68, 1.0),
    ],
    # Aoi (Caçadora Ainu de Hokkaido): Rastreia o solo nevado, estoca a lança Op e assume guarda de caça
    "aoi": [
        _idle(0.0, 0.22, pose="huntress_kneel"),
        _seg(0.22, 0.66, "ATTACK", 0.0, 1.0),
        _idle(0.66, 1.0),
    ],
    # Raiden (2.23.5): Dupla palmada trovejante com sal ritual -> postura sagrada Sonkyo -> guarda Kamae
    "raiden": [
        _idle(0.0, 0.38, pose="ceremonial_clap", salt_flash=True),
        _idle(0.38, 0.78, pose="sonkyo_squat"),
        _idle(0.78, 1.0, pose="sumo_kamae"),
    ],
}

VICTORY = {
    # Kenshi (2.1.6): Chiburi lateral elegante (sacode o sangue da lâmina no piso) -> Noto fluido para dentro da bainha com estalo metálico -> reverência serena com pétalas
    "kenshin": [
        _seg(0.0, 0.22, "ATTACK", 0.35, 0.96),
        _idle(0.22, 0.46, pose="chiburi_flick"),
        _idle(0.46, 0.82, pose="noto_sheath"),
        _idle(0.82, 1.0, pose="victory_bow"),
    ],
    # Musashi (2.2.6): Duplo Chiburi simultâneo (sacudida lateral do sangue no piso à esquerda e direita) -> elevação na Postura dos Dois Céus sem embainhar
    "musashi": [
        _idle(0.0, 0.45, pose="double_chiburi"),
        _idle(0.45, 1.0, pose="two_heavens_victory"),
    ],
    # Hanzo (2.3.8): Selo de dedos Kuji-Kiri no peito -> desvanecimento total em fumaça negra shinobi
    "ninja": [
        _idle(0.0, 0.45, pose="kuji_kiri"),
        _idle(0.45, 1.0, pose="smoke_vanish", alpha=(1.0, 0.0)),
    ],
    "american": [_idle(0.0, 0.1), _seg(0.1, 0.55, "ATTACK", 0.0, 1.0), _idle(0.55, 1.0)],
    "saitou": [_idle(0.0, 0.1), _seg(0.1, 0.8, "GATOTSU_CHARGE", 0.2, 0.7), _idle(0.8, 1.0)],
    "rifleman": [_idle(0.0, 0.15), _seg(0.15, 0.55, "ATTACK", 0.0, 1.0), _idle(0.55, 1.0)],
    "murasaki": [_idle(0.0, 0.1), _seg(0.1, 0.5, "ATTACK", 0.0, 1.0), _seg(0.5, 0.9, "ATTACK", 0.0, 1.0), _idle(0.9, 1.0)],
    # Some em fumaça e reaparece, depois arremessa a bomba
    "kasumi": [_idle(0.0, 0.3, alpha=(1.0, 0.25)), _idle(0.3, 0.55, alpha=(0.25, 1.0)), _seg(0.55, 0.9, "ATTACK", 0.0, 1.0), _idle(0.9, 1.0)],
    "okuni": [_idle(0.0, 0.1), _seg(0.1, 0.4, "ATTACK", 0.0, 0.5), _seg(0.4, 0.9, "ATTACK", 0.5, 0.5), _idle(0.9, 1.0)],
    # Arco erguido sem flecha
    "tomoe": [_idle(0.0, 0.1), _seg(0.1, 0.85, "ATTACK", 0.2, 0.8, is_drawing=False), _idle(0.85, 1.0)],
    "pirate": [_idle(0.0, 0.1), _seg(0.1, 0.3, "CUTLASS_CLEAVE", 0.0, 0.3), _seg(0.3, 0.85, "CUTLASS_CLEAVE", 0.3, 0.6), _idle(0.85, 1.0)],
    "musketeer": [_idle(0.0, 0.1), _seg(0.1, 0.35, "FLECHE", 0.0, 1.0), _seg(0.35, 0.85, "CAPE_FLOURISH", 0.5, 0.5), _idle(0.85, 1.0)],
    # Ren (Shaolin): Chute Alto do Dragão, Rugido de Kiai com aura dourada e Reverência Gassho de paz
    "ren": [
        _seg(0.0, 0.32, "ATTACK", 0.0, 1.0, combo_step=3),
        _seg(0.32, 0.64, "IDLE", 0.0, 1.0, pose="kiai_roar"),
        _seg(0.64, 1.0, "IDLE", 0.0, 1.0, pose="shaolin_bow"),
    ],
    # Chiyo (Duas Kodachi): Giro de Dança Mai, Cruzamento em 'X' das Kodachis e Pose Final Kunoichi com pétalas
    "chiyo": [
        _seg(0.0, 0.35, "ATTACK", 0.0, 1.0, combo_step=2),
        _seg(0.35, 0.65, "IDLE", 0.0, 1.0, pose="kodachi_x_pose"),
        _seg(0.65, 1.0, "IDLE", 0.0, 1.0, pose="kodachi_victory"),
    ],
    # Benkei: Apoia a naginata sobre os ombros, cruza os braços com presença de fortaleza
    "benkei": [
        _idle(0.0, 0.25),
        _seg(0.25, 0.70, "ATTACK", 0.0, 0.5),
        _idle(0.70, 1.0, pose="benkei_shoulder_rest"),
    ],
    # O-Rin: Toca acorde melancólico, vira de costas e olha por cima do ombro com pétalas de higanbana
    "orin": [
        _idle(0.0, 0.20),
        _seg(0.20, 0.55, "ATTACK", 0.0, 1.0),
        _idle(0.55, 1.0, pose="orin_backward_glance"),
    ],
    # Goro: Pisotão sísmico triunfante, giro da enxada e descanso sobre o ombro
    "goro": [
        _idle(0.0, 0.20, pose="earth_stomp"),
        _seg(0.20, 0.65, "ATTACK", 0.0, 0.5),
        _idle(0.65, 1.0),
    ],
    # Ichi: Corte em arco, embainhar silencioso com clique oco e postura serena
    "ichi": [
        _idle(0.0, 0.15),
        _seg(0.15, 0.55, "ATTACK", 0.0, 0.7),
        _idle(0.55, 0.85, pose="sheath_click"),
        _idle(0.85, 1.0),
    ],
    # Valerius: Giro cerimonial da foice, estalar de dedos e reverência prussiana solene
    "valerius": [
        _idle(0.0, 0.15),
        _seg(0.15, 0.55, "ATTACK", 0.0, 0.8),
        _idle(0.55, 1.0, pose="aristocrat_bow"),
    ],
    # Seimei: Ofuda cósmico incandescente, giro de vestes e reverência tradicional Heian
    "seimei": [
        _idle(0.0, 0.15),
        _seg(0.15, 0.60, "ATTACK", 0.0, 0.9),
        _idle(0.60, 1.0, pose="heian_bow"),
    ],
    # Daiki: Giro aéreo do bastão Bō, cravada firme no chão e saudação de monge peregrino
    "daiki": [
        _seg(0.0, 0.45, "POLE_VAULT", 0.0, 1.0, is_vault=True),
        _idle(0.45, 0.75, pose="bo_plant_stance"),
        _idle(0.75, 1.0, pose="pilgrim_bow"),
    ],
    # Aoi: Giro de lança Op e prece tradicional Ainu (Inonno) aos espíritos Kamuy
    "aoi": [
        _seg(0.0, 0.45, "ATTACK", 0.0, 1.0),
        _idle(0.45, 1.0, pose="ainu_prayer"),
    ],
    # Raiden (2.23.6): Elevação de perna a 90° em Shiko ritual -> queda telúrica no solo -> punhos no mawashi com rugido
    "raiden": [
        _idle(0.0, 0.44, pose="shiko_raise"),
        _idle(0.44, 0.74, pose="shiko_stomp", seismic_dust=True),
        _idle(0.74, 1.0, pose="mawashi_fists"),
    ],
}

SCRIPTS = {"intro": INTRO, "victory": VICTORY}

# (p, evento): "sfx:<nome do SoundEvent>" ou "fx:<smoke|petals|sparks>"
BEATS = {
    "intro": {
        "kenshin": [(0.37, "sfx:parry"), (0.38, "fx:sparks"), (0.68, "sfx:sword_slash")],
        "musashi": [(0.26, "sfx:sword_slash"), (0.42, "sfx:parry"), (0.44, "fx:sparks")],
        "ninja": [(0.02, "fx:petals"), (0.36, "sfx:parry"), (0.38, "fx:sparks"), (0.68, "sfx:sword_slash")],
        "american": [(0.12, "sfx:dog_bark"), (0.3, "sfx:shuriken_throw")],
        "saitou": [(0.22, "sfx:sword_slash")],
        "rifleman": [(0.28, "sfx:obstacle_hit")],
        "murasaki": [(0.12, "sfx:chain_spin"), (0.47, "sfx:chain_spin")],
        "kasumi": [(0.02, "fx:smoke"), (0.02, "sfx:smoke_puff"), (0.52, "sfx:bomb_fuse")],
        "okuni": [(0.17, "fx:petals"), (0.5, "fx:petals")],
        "tomoe": [(0.8, "sfx:bow_release")],
        "pirate": [(0.2, "sfx:sword_slash")],
        "musketeer": [(0.2, "sfx:sword_slash"), (0.52, "sfx:dodge_whoosh")],
        "ren": [(0.26, "sfx:dodge_whoosh"), (0.50, "sfx:sword_slash"), (0.58, "fx:sparks")],
        "chiyo": [(0.02, "fx:smoke"), (0.02, "sfx:smoke_puff"), (0.30, "sfx:sword_slash"), (0.56, "sfx:sword_slash"), (0.60, "fx:petals")],
        "benkei": [(0.24, "sfx:obstacle_hit"), (0.45, "sfx:sword_slash"), (0.50, "fx:sparks")],
        "orin": [(0.22, "sfx:sword_slash"), (0.50, "fx:petals")],
        "goro": [(0.24, "sfx:obstacle_hit"), (0.45, "sfx:sword_slash"), (0.50, "fx:sparks")],
        "ichi": [(0.18, "sfx:dodge_whoosh"), (0.32, "sfx:sword_slash"), (0.68, "sfx:parry")],
        "valerius": [(0.22, "sfx:sword_slash"), (0.45, "fx:smoke")],
        "seimei": [(0.20, "sfx:kunai_throw"), (0.40, "fx:sparks"), (0.65, "fx:petals")],
        "daiki": [(0.25, "sfx:dodge_whoosh"), (0.48, "sfx:obstacle_hit")],
        "aoi": [(0.24, "sfx:sword_slash"), (0.52, "sfx:dodge_whoosh")],
        "raiden": [(0.12, "sfx:parry"), (0.24, "sfx:parry"), (0.38, "fx:sparks"), (0.40, "sfx:dodge_whoosh")],
    },
    "victory": {
        "kenshin": [(0.08, "sfx:sword_slash"), (0.28, "sfx:dodge_whoosh"), (0.30, "fx:blood"), (0.74, "sfx:parry"), (0.76, "fx:petals")],
        "musashi": [(0.14, "sfx:sword_slash"), (0.20, "fx:blood"), (0.50, "sfx:parry")],
        "ninja": [(0.15, "sfx:dodge_whoosh"), (0.46, "fx:smoke"), (0.48, "sfx:smoke_puff")],
        "american": [(0.1, "sfx:dog_bark"), (0.3, "sfx:shuriken_throw")],
        "saitou": [(0.12, "sfx:sword_slash")],
        "rifleman": [(0.2, "sfx:obstacle_hit")],
        "murasaki": [(0.12, "sfx:chain_spin"), (0.52, "sfx:chain_spin")],
        "kasumi": [(0.02, "fx:smoke"), (0.3, "fx:smoke"), (0.57, "sfx:bomb_fuse")],
        "okuni": [(0.12, "fx:petals"), (0.4, "fx:petals")],
        "tomoe": [(0.5, "sfx:bow_release")],
        "pirate": [(0.12, "sfx:sword_slash")],
        "musketeer": [(0.12, "sfx:sword_slash"), (0.36, "sfx:dodge_whoosh")],
        "ren": [(0.08, "sfx:dodge_whoosh"), (0.34, "sfx:sword_clash"), (0.36, "fx:sparks"), (0.68, "fx:petals")],
        "chiyo": [(0.08, "sfx:sword_slash"), (0.38, "sfx:parry"), (0.42, "fx:petals"), (0.72, "fx:petals")],
        "benkei": [(0.28, "sfx:parry"), (0.35, "fx:sparks")],
        "orin": [(0.24, "sfx:sword_slash"), (0.40, "fx:petals"), (0.75, "fx:petals")],
        "goro": [(0.15, "sfx:obstacle_hit"), (0.40, "sfx:sword_slash"), (0.45, "fx:sparks")],
        "ichi": [(0.15, "sfx:sword_slash"), (0.55, "sfx:parry"), (0.65, "fx:petals")],
        "valerius": [(0.18, "sfx:sword_slash"), (0.50, "fx:smoke")],
        "seimei": [(0.15, "sfx:kunai_throw"), (0.35, "fx:sparks"), (0.70, "fx:petals")],
        "daiki": [(0.18, "sfx:dodge_whoosh"), (0.44, "sfx:obstacle_hit")],
        "aoi": [(0.16, "sfx:sword_slash"), (0.50, "fx:petals")],
        "raiden": [(0.20, "sfx:dodge_whoosh"), (0.45, "sfx:obstacle_hit"), (0.46, "fx:smoke"), (0.76, "sfx:sword_slash")],
    },
}


def sample(char_type: str, kind: str, p: float) -> PoseFrame:
    """Pose do lutador no progresso `p` (0..1) da introdução (`kind="intro"`) ou da vitória (`kind="victory"`)."""
    script = SCRIPTS.get(kind, {}).get(canonical(char_type))
    if not script:
        return PoseFrame()
    p = max(0.0, min(1.0, p))
    for t0, t1, state, a0, a1, alpha, extra in script:
        if p <= t1 or t1 >= 1.0:
            u = 0.0 if t1 <= t0 else max(0.0, min(1.0, (p - t0) / (t1 - t0)))
            ex = dict(extra)
            ex.setdefault("seg_u", u)
            if ex.get("pose") == "noto_sheath" and "noto_prog" not in extra:
                ex["noto_prog"] = u
            return PoseFrame(state, a0 + (a1 - a0) * u, ex, alpha[0] + (alpha[1] - alpha[0]) * u)
    return PoseFrame()


def state_timer_for(char_type: str, frame: PoseFrame) -> float:
    """`state_timer` que o renderer converte de volta no progresso do estado (0 fora dos estados de golpe)."""
    c = canonical(char_type)
    if frame.state in MELEE_STATES:
        if c == "ren":
            r_step = frame.extra.get("combo_step", 1) if frame.extra else 1
            duration = 0.24 if r_step == 3 else (0.16 if r_step == 2 else 0.14)
        else:
            duration = ATTACK_DURATION.get(c, DEFAULT_ATTACK_DURATION)
    elif frame.state in STATE_DURATION:
        duration = STATE_DURATION[frame.state]
    else:
        return 0.0
    return max(0.001, duration * (1.0 - frame.progress))


class BeatPlayer:
    """Dispara cada marcador (som/efeito) uma única vez, mesmo quando o progresso salta."""

    def __init__(self, char_type: str, kind: str):
        self.beats = sorted(BEATS.get(kind, {}).get(canonical(char_type), []))
        self.last = -1.0

    def advance(self, p: float) -> list[str]:
        fired = [name for t, name in self.beats if self.last < t <= p]
        self.last = max(self.last, p)
        return fired
