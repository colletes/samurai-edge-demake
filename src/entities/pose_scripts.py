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
                   "purple": 0.16, "ninja": 0.18, "saitou": 0.25, "ren": 0.14, "chiyo": 0.14, "benkei": 0.32, "orin": 0.20}
DEFAULT_ATTACK_DURATION = 0.20
STATE_DURATION = {"PARRY": 0.45, "CAPE_FLOURISH": 0.5, "KIAI": 0.35, "MAI_DANCE": 0.36}
MELEE_STATES = ("ATTACK", "CUTLASS_CLEAVE", "FLECHE", "ZEROSHIKI", "GATOTSU_CHARGE", "KIAI", "MAI_DANCE")


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
    return c


def _seg(t0, t1, state="IDLE", a0=0.0, a1=None, alpha=(1.0, 1.0), **extra):
    return (t0, t1, state, a0, a0 if a1 is None else a1, alpha, extra)


def _idle(t0, t1, alpha=(1.0, 1.0), **extra):
    return _seg(t0, t1, "IDLE", 0.0, 0.0, alpha, **extra)


INTRO = {
    # Iai: saque e corte, e a lâmina volta à saya
    "kenshin": [_idle(0.0, 0.2), _seg(0.2, 0.7, "ATTACK", 0.0, 1.0), _idle(0.7, 1.0)],
    # Niten: dois cortes, aparada cruzada e guarda
    "musashi": [_idle(0.0, 0.15), _seg(0.15, 0.4, "ATTACK", 0.0, 1.0, combo_step=1),
                _seg(0.4, 0.62, "ATTACK", 0.0, 1.0, combo_step=2), _seg(0.62, 0.82, "PARRY", 0.5, 0.5), _idle(0.82, 1.0)],
    # Dois golpes de kunai
    "ninja": [_idle(0.0, 0.2), _seg(0.2, 0.5, "ATTACK", 0.0, 1.0), _idle(0.5, 0.6), _seg(0.6, 0.85, "ATTACK", 0.0, 1.0), _idle(0.85, 1.0)],
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
}

VICTORY = {
    # Saca e embainha devagar (o progresso do saque vai e volta)
    "kenshin": [_idle(0.0, 0.15), _seg(0.15, 0.35, "ATTACK", 0.05, 0.33), _seg(0.35, 0.55, "ATTACK", 0.33, 0.33),
                _seg(0.55, 0.8, "ATTACK", 0.33, 0.1), _idle(0.8, 1.0)],
    "musashi": [_idle(0.0, 0.1), _seg(0.1, 0.4, "ATTACK", 0.0, 1.0, combo_step=1), _seg(0.4, 0.85, "PARRY", 0.15, 0.85), _idle(0.85, 1.0)],
    "ninja": [_idle(0.0, 0.1), _seg(0.1, 0.45, "ATTACK", 0.0, 1.0), _idle(0.45, 0.55), _seg(0.55, 0.9, "ATTACK", 0.0, 1.0), _idle(0.9, 1.0)],
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
}

SCRIPTS = {"intro": INTRO, "victory": VICTORY}

# (p, evento): "sfx:<nome do SoundEvent>" ou "fx:<smoke|petals|sparks>"
BEATS = {
    "intro": {
        "kenshin": [(0.22, "sfx:sword_slash")],
        "musashi": [(0.16, "sfx:sword_slash"), (0.41, "sfx:sword_slash"), (0.64, "sfx:parry")],
        "ninja": [(0.22, "sfx:kunai_throw"), (0.62, "sfx:kunai_throw")],
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
    },
    "victory": {
        "kenshin": [(0.17, "sfx:sword_slash"), (0.6, "sfx:sword_slash"), (0.4, "fx:petals")],
        "musashi": [(0.12, "sfx:parry")],
        "ninja": [(0.12, "sfx:kunai_throw"), (0.57, "sfx:kunai_throw")],
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
            return PoseFrame(state, a0 + (a1 - a0) * u, dict(extra), alpha[0] + (alpha[1] - alpha[0]) * u)
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
