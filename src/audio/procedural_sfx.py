"""
Sintetizador procedural de efeitos sonoros feudais (SFX) e faixas ambientes (BGM).
Gera áudio 16-bit 44.1kHz em memória sem dependências externas, garantindo
que o jogo tenha som completo e autônomo em qualquer plataforma.
"""
import io
import math
import random
import struct
import wave
import pygame
from src.audio.sound_events import SoundEvent, MusicTrack


SAMPLE_RATE = 44100


def _samples_to_sound(samples: list[float], sample_rate: int = SAMPLE_RATE) -> pygame.mixer.Sound:
    """Converte uma lista de amostras normalizadas (-1.0 a 1.0) em um objeto pygame.mixer.Sound em memória."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(2)       # Estéreo
        wav.setsampwidth(2)       # 16-bit
        wav.setframerate(sample_rate)

        frames = bytearray()
        for s in samples:
            # Clampar entre -1.0 e 1.0 e converter para inteiro de 16 bits (-32767 a 32767)
            clamped = max(-1.0, min(1.0, s))
            val = int(clamped * 32767.0)
            frames.extend(struct.pack("<hh", val, val))
        wav.writeframes(frames)

    buf.seek(0)
    return pygame.mixer.Sound(buf)


def generate_sword_clash() -> pygame.mixer.Sound:
    """Choque simultâneo de lâminas de aço (ataque metálico rápido + ressonância)."""
    duration = 0.28
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    f1, f2, f3 = 1320.0, 2640.0, 3960.0
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        decay = math.exp(-14.0 * t)
        noise = (random.random() * 2.0 - 1.0) * math.exp(-40.0 * t) * 0.4
        tone = (
            math.sin(2.0 * math.pi * f1 * t) * 0.45 +
            math.sin(2.0 * math.pi * f2 * t) * 0.30 +
            math.sin(2.0 * math.pi * f3 * t) * 0.15
        )
        samples.append((tone + noise) * decay * 0.9)

    return _samples_to_sound(samples)


def generate_parry() -> pygame.mixer.Sound:
    """Aparada perfeita frontal com ressonância cristalina."""
    duration = 0.35
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    f1, f2 = 1850.0, 3700.0
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        decay = math.exp(-10.0 * t)
        tone = (
            math.sin(2.0 * math.pi * f1 * t) * 0.60 +
            math.sin(2.0 * math.pi * f2 * t) * 0.35
        )
        samples.append(tone * decay * 0.85)

    return _samples_to_sound(samples)


def generate_sword_slash() -> pygame.mixer.Sound:
    """Corte de lâmina no ar (whoosh aerodinâmico)."""
    duration = 0.15
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Envelope de sino assimétrico
        env = math.sin(math.pi * (t / duration)) ** 2.0
        # Ruído com modulação de tom descendente
        freq = 700.0 - 400.0 * (t / duration)
        noise = (random.random() * 2.0 - 1.0) * 0.7
        sine = math.sin(2.0 * math.pi * freq * t) * 0.3
        samples.append((noise + sine) * env * 0.65)

    return _samples_to_sound(samples)


def generate_fatal_strike() -> pygame.mixer.Sound:
    """Impacto do golpe fatal (1-hit kill): grave visceral profundo + corte agudo."""
    duration = 0.48
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Sub-grave visceral com queda de pitch
        freq_low = 85.0 * math.exp(-6.0 * t)
        sub = math.sin(2.0 * math.pi * freq_low * t) * 0.70
        # Ruído de corte fatiador
        slice_noise = (random.random() * 2.0 - 1.0) * math.exp(-18.0 * t) * 0.45
        # Ressonância de sangue
        decay = math.exp(-7.5 * t)
        samples.append((sub + slice_noise) * decay * 0.95)

    return _samples_to_sound(samples)


def generate_obstacle_hit() -> pygame.mixer.Sound:
    """Impacto de aço contra rocha ou madeira sólida."""
    duration = 0.14
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        decay = math.exp(-22.0 * t)
        thud = math.sin(2.0 * math.pi * 210.0 * t) * 0.6
        spark_noise = (random.random() * 2.0 - 1.0) * math.exp(-50.0 * t) * 0.5
        samples.append((thud + spark_noise) * decay * 0.75)

    return _samples_to_sound(samples)


def generate_flintlock_shot() -> pygame.mixer.Sound:
    """Tiro de pistola de pederneira (estalo seco de disparo + queima de pólvora)."""
    duration = 0.32
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Estalo de alta pressão inicial
        crack = (random.random() * 2.0 - 1.0) * math.exp(-45.0 * t) * 0.8
        # Corpo da explosão
        body = math.sin(2.0 * math.pi * (160.0 * math.exp(-8.0 * t)) * t) * math.exp(-12.0 * t) * 0.6
        samples.append((crack + body) * 0.9)

    return _samples_to_sound(samples)


def generate_tanegashima_shot() -> pygame.mixer.Sound:
    """Tiro encorpado de arcabuz Tanegashima (estrondo maior com eco de vale)."""
    duration = 0.45
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        crack = (random.random() * 2.0 - 1.0) * math.exp(-25.0 * t) * 0.75
        sub = math.sin(2.0 * math.pi * (120.0 * math.exp(-5.0 * t)) * t) * math.exp(-8.0 * t) * 0.7
        samples.append((crack + sub) * 0.95)

    return _samples_to_sound(samples)


def generate_bomb_explode() -> pygame.mixer.Sound:
    """Detonação de bomba de pólvora preta com tremor sub-grave."""
    duration = 0.55
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        sub = math.sin(2.0 * math.pi * (90.0 * math.exp(-4.0 * t)) * t) * 0.7
        noise = (random.random() * 2.0 - 1.0) * math.exp(-8.0 * t) * 0.6
        decay = math.exp(-5.5 * t)
        samples.append((sub + noise) * decay * 0.95)

    return _samples_to_sound(samples)


def generate_cannon_fire() -> pygame.mixer.Sound:
    """Disparo estrondoso de artilharia naval celestial (Anne)."""
    duration = 0.70
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        sub = math.sin(2.0 * math.pi * (55.0 * math.exp(-3.0 * t)) * t) * 0.85
        rumble = (random.random() * 2.0 - 1.0) * math.exp(-6.0 * t) * 0.5
        decay = math.exp(-4.2 * t)
        samples.append((sub + rumble) * decay)

    return _samples_to_sound(samples)


def generate_arrow_release() -> pygame.mixer.Sound:
    """Zunido da corda do arco longo Yumi ao ser solta."""
    duration = 0.12
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        twang = math.sin(2.0 * math.pi * 360.0 * t) * math.exp(-24.0 * t) * 0.7
        air = (random.random() * 2.0 - 1.0) * math.exp(-30.0 * t) * 0.3
        samples.append((twang + air) * 0.8)

    return _samples_to_sound(samples)


def generate_arrow_hit() -> pygame.mixer.Sound:
    """Impacto seco da flecha cravando."""
    duration = 0.10
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        thud = math.sin(2.0 * math.pi * 180.0 * t) * math.exp(-35.0 * t) * 0.8
        samples.append(thud)

    return _samples_to_sound(samples)


def generate_shuriken_throw() -> pygame.mixer.Sound:
    """Zumbido cortante e rotativo de shuriken em voo."""
    duration = 0.16
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / duration)) ** 1.5
        # Modulação de frequência simulando rotação
        freq = 920.0 + math.sin(2.0 * math.pi * 45.0 * t) * 150.0
        tone = math.sin(2.0 * math.pi * freq * t) * env * 0.65
        samples.append(tone)

    return _samples_to_sound(samples)


def generate_chain_whip() -> pygame.mixer.Sound:
    """Ruído metálico rápido da corrente Kusarigama chicoteando."""
    duration = 0.20
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / duration))
        clink = math.sin(2.0 * math.pi * (2100.0 + (i % 300)) * t) * 0.5
        noise = (random.random() * 2.0 - 1.0) * 0.4
        samples.append((clink + noise) * env * math.exp(-8.0 * t) * 0.7)

    return _samples_to_sound(samples)


def generate_dodge_whoosh() -> pygame.mixer.Sound:
    """Deslocamento ágil de ar na esquiva ou rolamento."""
    duration = 0.14
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / duration)) ** 2.0
        noise = (random.random() * 2.0 - 1.0) * env * 0.55
        samples.append(noise)

    return _samples_to_sound(samples)


def generate_shukuchi() -> pygame.mixer.Sound:
    """Teletransporte Shukuchi (passo relâmpago veloz de Kenshi)."""
    duration = 0.18
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / duration)) ** 1.8
        freq = 450.0 + 850.0 * (t / duration)
        sine = math.sin(2.0 * math.pi * freq * t) * 0.4
        noise = (random.random() * 2.0 - 1.0) * 0.5
        samples.append((sine + noise) * env * 0.75)

    return _samples_to_sound(samples)


def generate_ryuu_tsui_sen() -> pygame.mixer.Sound:
    """Vento cortante descendente acelerado do ataque aéreo."""
    duration = 0.28
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (t / duration) ** 2.0
        freq = 300.0 + 700.0 * (1.0 - t / duration)
        sine = math.sin(2.0 * math.pi * freq * t) * 0.4
        noise = (random.random() * 2.0 - 1.0) * 0.5
        samples.append((sine + noise) * env * 0.8)

    return _samples_to_sound(samples)


def generate_smoke_puff() -> pygame.mixer.Sound:
    """Puff de fumaça suave ao ativar bomba de fumaça ou sumir em stealth."""
    duration = 0.22
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        decay = math.exp(-12.0 * t)
        noise = (random.random() * 2.0 - 1.0) * decay * 0.65
        samples.append(noise)

    return _samples_to_sound(samples)


def generate_poison_breath() -> pygame.mixer.Sound:
    """Sopro sibilante de névoa venenosa Dokukiri."""
    duration = 0.35
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / duration)) ** 1.5
        hiss = math.sin(2.0 * math.pi * 3200.0 * t) * 0.25 + (random.random() * 2.0 - 1.0) * 0.45
        samples.append(hiss * env * 0.6)

    return _samples_to_sound(samples)


def generate_footstep() -> pygame.mixer.Sound:
    """Passo leve e abafado na grama ou pedra."""
    duration = 0.05
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        decay = math.exp(-60.0 * t)
        thud = math.sin(2.0 * math.pi * 140.0 * t) * decay * 0.35
        samples.append(thud)

    return _samples_to_sound(samples)


def generate_round_start() -> pygame.mixer.Sound:
    """Batida cerimonial de tambor Taiko de início de duelo."""
    duration = 0.60
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        taiko = math.sin(2.0 * math.pi * 72.0 * t) * math.exp(-5.0 * t) * 0.8
        thud = math.sin(2.0 * math.pi * 144.0 * t) * math.exp(-10.0 * t) * 0.4
        samples.append((taiko + thud) * 0.95)

    return _samples_to_sound(samples)


def generate_round_win() -> pygame.mixer.Sound:
    """Ressonância de sino budista de vitória."""
    duration = 0.95
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        decay = math.exp(-3.2 * t)
        gong = (
            math.sin(2.0 * math.pi * 220.0 * t) * 0.50 +
            math.sin(2.0 * math.pi * 440.0 * t) * 0.30 +
            math.sin(2.0 * math.pi * 660.0 * t) * 0.15
        )
        samples.append(gong * decay * 0.85)

    return _samples_to_sound(samples)


def generate_ui_select() -> pygame.mixer.Sound:
    """Clique sutil de navegação em menus."""
    duration = 0.04
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        tone = math.sin(2.0 * math.pi * 880.0 * t) * math.exp(-70.0 * t) * 0.4
        samples.append(tone)

    return _samples_to_sound(samples)


def generate_ui_confirm() -> pygame.mixer.Sound:
    """Confirmação de opção com dois tons ascendentes."""
    duration = 0.12
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        freq = 587.0 if t < 0.06 else 880.0
        tone = math.sin(2.0 * math.pi * freq * t) * math.exp(-25.0 * (t % 0.06)) * 0.55
        samples.append(tone)

    return _samples_to_sound(samples)


def generate_ui_cancel() -> pygame.mixer.Sound:
    """Cancelamento com tom descendente."""
    duration = 0.10
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        freq = 440.0 if t < 0.05 else 330.0
        tone = math.sin(2.0 * math.pi * freq * t) * math.exp(-30.0 * (t % 0.05)) * 0.45
        samples.append(tone)

    return _samples_to_sound(samples)


def generate_dog_bark() -> pygame.mixer.Sound:
    """Latido rápido e agressivo do cão Yamato."""
    duration = 0.16
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        decay = math.exp(-22.0 * t)
        freq = 320.0 - 140.0 * (t / duration)
        noise = (random.random() * 2.0 - 1.0) * 0.35
        tone = math.sin(2.0 * math.pi * freq * t) * 0.65
        samples.append((tone + noise) * decay * 0.85)

    return _samples_to_sound(samples)


_GENERATOR_MAP = {
    SoundEvent.SWORD_SLASH: generate_sword_slash,
    SoundEvent.SWORD_CLASH: generate_sword_clash,
    SoundEvent.PARRY: generate_parry,
    SoundEvent.FATAL_STRIKE: generate_fatal_strike,
    SoundEvent.OBSTACLE_HIT: generate_obstacle_hit,
    SoundEvent.FLINTLOCK_SHOT: generate_flintlock_shot,
    SoundEvent.TANEGASHIMA_SHOT: generate_tanegashima_shot,
    SoundEvent.BOMB_EXPLODE: generate_bomb_explode,
    SoundEvent.CANNON_FIRE: generate_cannon_fire,
    SoundEvent.ARROW_RELEASE: generate_arrow_release,
    SoundEvent.ARROW_HIT: generate_arrow_hit,
    SoundEvent.SHURIKEN_THROW: generate_shuriken_throw,
    SoundEvent.CHAIN_WHIP: generate_chain_whip,
    SoundEvent.DODGE_WHOOSH: generate_dodge_whoosh,
    SoundEvent.SHUKUCHI: generate_shukuchi,
    SoundEvent.RYUU_TSUI_SEN: generate_ryuu_tsui_sen,
    SoundEvent.SMOKE_PUFF: generate_smoke_puff,
    SoundEvent.POISON_BREATH: generate_poison_breath,
    SoundEvent.FOOTSTEP: generate_footstep,
    SoundEvent.DOG_BARK: generate_dog_bark,
    SoundEvent.ROUND_START: generate_round_start,
    SoundEvent.ROUND_WIN: generate_round_win,
    SoundEvent.UI_SELECT: generate_ui_select,
    SoundEvent.UI_CONFIRM: generate_ui_confirm,
    SoundEvent.UI_CANCEL: generate_ui_cancel,
}


def generate_procedural_sound(event: SoundEvent) -> pygame.mixer.Sound | None:
    """Gera o som procedural sob demanda de acordo com o evento."""
    gen = _GENERATOR_MAP.get(event)
    if gen:
        return gen()
    return None
