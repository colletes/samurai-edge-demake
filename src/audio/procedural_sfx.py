"""
Sintetizador procedural de efeitos sonoros feudais (SFX) e faixas ambientes (BGM).
Gera áudio 16-bit 44.1kHz em memória sem dependências externas, garantindo
que o jogo tenha som completo e autônomo em qualquer plataforma.
"""
import io
import math
import os
import random
import struct
import wave
import pygame
from src.audio.sound_events import SoundEvent, MusicTrack


SAMPLE_RATE = 44100


def _white_noise(n: int) -> list[float]:
    return [random.uniform(-1.0, 1.0) for _ in range(n)]


def _lowpass(samples: list[float], alpha: float) -> list[float]:
    """Filtro IIR passa-baixa de 1 polo (suaviza/escurece ruído branco em um 'whoosh' de ar)."""
    out = []
    prev = 0.0
    for s in samples:
        prev += alpha * (s - prev)
        out.append(prev)
    return out


def _highpass(samples: list[float], alpha: float) -> list[float]:
    """Filtro IIR passa-alta de 1 polo (realça transientes para um 'shing' metálico brilhante)."""
    out = []
    prev_in = 0.0
    prev_out = 0.0
    for s in samples:
        cur = alpha * (prev_out + s - prev_in)
        out.append(cur)
        prev_in = s
        prev_out = cur
    return out


def _metal_ring(t: float, base_freq: float, partials: list[tuple[float, float, float]]) -> float:
    """Soma de parciais INARMÔNICOS (razões não-inteiras, como barras/sinos reais) com decaimentos
    independentes por parcial — produz um timbre metálico muito mais realista que harmônicos puros."""
    val = 0.0
    for ratio, amp, decay in partials:
        val += math.sin(2.0 * math.pi * base_freq * ratio * t) * amp * math.exp(-decay * t)
    return val


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
    """Choque simultâneo de lâminas de aço: transiente brilhante de contato + ressonância
    metálica inarmônica + um segundo micro-contato levemente defasado (duplo toque real)."""
    duration = 0.32
    num_samples = int(SAMPLE_RATE * duration)
    noise = _highpass(_white_noise(num_samples), 0.55)
    partials = [
        (1.00, 0.42, 16.0),
        (2.37, 0.26, 20.0),
        (3.91, 0.16, 26.0),
        (5.23, 0.10, 34.0),
        (6.81, 0.06, 42.0),
    ]
    base_freq = 1480.0
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        transient = noise[i] * math.exp(-70.0 * t) * 0.6
        ring = _metal_ring(t, base_freq, partials)
        t2 = t - 0.018
        ring2 = _metal_ring(t2, base_freq * 0.92, partials) * 0.5 if t2 > 0 else 0.0
        samples.append((transient + ring + ring2) * 0.85)

    return _samples_to_sound(samples)


def generate_parry() -> pygame.mixer.Sound:
    """Aparada perfeita frontal: contato único e limpo, mais brilhante e sustentado que o
    choque mútuo, com ressonância cristalina inarmônica de lâmina bem temperada."""
    duration = 0.4
    num_samples = int(SAMPLE_RATE * duration)
    noise = _white_noise(num_samples)
    partials = [
        (1.00, 0.50, 9.0),
        (2.76, 0.28, 12.0),
        (4.18, 0.14, 16.0),
        (6.02, 0.08, 22.0),
    ]
    base_freq = 1900.0
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        transient = noise[i] * math.exp(-90.0 * t) * 0.5
        ring = _metal_ring(t, base_freq, partials)
        samples.append((transient + ring) * 0.8)

    return _samples_to_sound(samples)


def generate_sword_slash() -> pygame.mixer.Sound:
    """Corte de lâmina no ar (whoosh aerodinâmico): ruído filtrado com varredura de tom
    descendente, simulando o deslocamento de ar ao redor do aço em movimento rápido."""
    duration = 0.22
    num_samples = int(SAMPLE_RATE * duration)
    filtered = _lowpass(_white_noise(num_samples), 0.35)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        prog = t / duration
        env = math.sin(math.pi * prog) ** 1.6
        sweep_freq = 1400.0 * (1.0 - prog) + 220.0 * prog
        sweep = math.sin(2.0 * math.pi * sweep_freq * t) * 0.18
        samples.append((filtered[i] * 0.8 + sweep) * env * 0.75)

    return _samples_to_sound(samples)


def generate_fatal_strike() -> pygame.mixer.Sound:
    """Impacto do golpe fatal (1-hit kill): grave visceral profundo + corte agudo filtrado
    + breve ressonância metálica da lâmina completando a trajetória através do alvo."""
    duration = 0.5
    num_samples = int(SAMPLE_RATE * duration)
    noise = _white_noise(num_samples)
    partials = [(1.0, 0.30, 18.0), (2.6, 0.14, 24.0)]
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        freq_low = 78.0 * math.exp(-5.0 * t)
        sub = math.sin(2.0 * math.pi * freq_low * t) * math.exp(-6.5 * t) * 0.75
        slice_noise = noise[i] * math.exp(-22.0 * t) * 0.4
        ring = _metal_ring(t, 1250.0, partials) * math.exp(-2.0 * t)
        samples.append((sub + slice_noise + ring) * 0.9)

    return _samples_to_sound(samples)


def generate_obstacle_hit() -> pygame.mixer.Sound:
    """Impacto de aço contra rocha ou madeira sólida: thud grave + faísca de atrito + crack seco."""
    duration = 0.16
    num_samples = int(SAMPLE_RATE * duration)
    noise = _white_noise(num_samples)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        thud = math.sin(2.0 * math.pi * 185.0 * t) * math.exp(-28.0 * t) * 0.55
        spark = noise[i] * math.exp(-60.0 * t) * 0.5
        crack = noise[i] * math.exp(-140.0 * t) * 0.4
        samples.append((thud + spark + crack) * 0.8)

    return _samples_to_sound(samples)


def generate_flintlock_shot() -> pygame.mixer.Sound:
    """Tiro de pistola de pederneira: estalo seco de alta pressão + corpo grave de queima de pólvora."""
    duration = 0.32
    num_samples = int(SAMPLE_RATE * duration)
    noise = _white_noise(num_samples)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        crack = noise[i] * math.exp(-50.0 * t) * 0.78
        body = math.sin(2.0 * math.pi * (160.0 * math.exp(-8.0 * t)) * t) * math.exp(-12.0 * t) * 0.6
        samples.append((crack + body) * 0.9)

    return _samples_to_sound(samples)


def generate_tanegashima_shot() -> pygame.mixer.Sound:
    """Tiro encorpado de arcabuz Tanegashima: estrondo maior + eco de vale (repetição atenuada e atrasada)."""
    duration = 0.5
    num_samples = int(SAMPLE_RATE * duration)
    noise = _white_noise(num_samples)
    samples = [0.0] * num_samples
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        crack = noise[i] * math.exp(-26.0 * t) * 0.7
        sub = math.sin(2.0 * math.pi * (110.0 * math.exp(-5.0 * t)) * t) * math.exp(-7.0 * t) * 0.65
        samples[i] += crack + sub
    delay = int(0.09 * SAMPLE_RATE)
    for i in range(num_samples - delay):
        samples[i + delay] += samples[i] * 0.22

    return _samples_to_sound([s * 0.85 for s in samples])


def generate_bomb_explode() -> pygame.mixer.Sound:
    """Detonação de bomba de pólvora preta: tremor sub-grave + ruído de estilhaços filtrado."""
    duration = 0.6
    num_samples = int(SAMPLE_RATE * duration)
    rumble = _lowpass(_white_noise(num_samples), 0.25)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        sub = math.sin(2.0 * math.pi * (85.0 * math.exp(-4.0 * t)) * t) * 0.72
        decay = math.exp(-5.5 * t)
        samples.append((sub + rumble[i] * math.exp(-7.0 * t) * 0.6) * decay * 0.95)

    return _samples_to_sound(samples)


def generate_cannon_fire() -> pygame.mixer.Sound:
    """Disparo estrondoso de artilharia naval celestial (Anne): sub-grave profundo + rumble filtrado."""
    duration = 0.70
    num_samples = int(SAMPLE_RATE * duration)
    rumble = _lowpass(_white_noise(num_samples), 0.2)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        sub = math.sin(2.0 * math.pi * (55.0 * math.exp(-3.0 * t)) * t) * 0.85
        decay = math.exp(-4.2 * t)
        samples.append((sub + rumble[i] * math.exp(-6.0 * t) * 0.5) * decay)

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
    """Ruído metálico da corrente Kusarigama: sequência de elos colidindo (múltiplos micro-cliques)."""
    duration = 0.24
    num_samples = int(SAMPLE_RATE * duration)
    noise = _white_noise(num_samples)
    link_times = (0.0, 0.045, 0.085, 0.13)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        val = 0.0
        for lt in link_times:
            dt = t - lt
            if dt >= 0.0:
                freq = 2300.0 + 400.0 * math.sin(dt * 90.0)
                val += math.sin(2.0 * math.pi * freq * dt) * math.exp(-55.0 * dt) * 0.35
        val += noise[i] * math.exp(-30.0 * t) * 0.25
        samples.append(val * 0.85)

    return _samples_to_sound(samples)


def generate_dodge_whoosh() -> pygame.mixer.Sound:
    """Deslocamento ágil de ar na esquiva ou rolamento (ruído filtrado, sem bleep tonal)."""
    duration = 0.16
    num_samples = int(SAMPLE_RATE * duration)
    filtered = _lowpass(_white_noise(num_samples), 0.3)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / duration)) ** 2.0
        samples.append(filtered[i] * env * 0.7)

    return _samples_to_sound(samples)


def generate_shukuchi() -> pygame.mixer.Sound:
    """Teletransporte Shukuchi (passo relâmpago veloz de Kenshi): varredura ascendente + ruído brilhante."""
    duration = 0.18
    num_samples = int(SAMPLE_RATE * duration)
    noise = _highpass(_white_noise(num_samples), 0.6)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / duration)) ** 1.8
        freq = 450.0 + 850.0 * (t / duration)
        sine = math.sin(2.0 * math.pi * freq * t) * 0.4
        samples.append((sine + noise[i] * 0.5) * env * 0.75)

    return _samples_to_sound(samples)


def generate_ryuu_tsui_sen() -> pygame.mixer.Sound:
    """Vento cortante descendente acelerado do ataque aéreo: ruído filtrado + queda de tom."""
    duration = 0.28
    num_samples = int(SAMPLE_RATE * duration)
    noise = _lowpass(_white_noise(num_samples), 0.4)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = (t / duration) ** 2.0
        freq = 300.0 + 700.0 * (1.0 - t / duration)
        sine = math.sin(2.0 * math.pi * freq * t) * 0.4
        samples.append((sine + noise[i] * 0.5) * env * 0.8)

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
    """Passo leve e abafado na grama ou pedra: thud grave + textura de solo filtrada."""
    duration = 0.06
    num_samples = int(SAMPLE_RATE * duration)
    noise = _lowpass(_white_noise(num_samples), 0.3)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        decay = math.exp(-60.0 * t)
        thud = math.sin(2.0 * math.pi * 140.0 * t) * decay * 0.35
        samples.append(thud + noise[i] * decay * 0.12)

    return _samples_to_sound(samples)


def generate_round_start() -> pygame.mixer.Sound:
    """Batida cerimonial de tambor Taiko: clique seco de baqueta + corpo grave ressonante."""
    duration = 0.7
    num_samples = int(SAMPLE_RATE * duration)
    noise = _white_noise(num_samples)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        click = noise[i] * math.exp(-250.0 * t) * 0.5
        body = math.sin(2.0 * math.pi * 68.0 * t) * math.exp(-6.0 * t) * 0.8
        overtone = math.sin(2.0 * math.pi * 136.0 * t) * math.exp(-11.0 * t) * 0.35
        samples.append((click + body + overtone) * 0.95)

    return _samples_to_sound(samples)


def generate_round_win() -> pygame.mixer.Sound:
    """Ressonância de sino budista de vitória: parciais inarmônicas de sino real + golpe inicial."""
    duration = 1.1
    num_samples = int(SAMPLE_RATE * duration)
    noise = _white_noise(num_samples)
    partials = [
        (1.00, 0.45, 2.6),
        (1.79, 0.26, 3.4),
        (2.42, 0.16, 4.2),
        (3.14, 0.10, 5.0),
        (4.08, 0.06, 6.0),
    ]
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        strike_noise = noise[i] * math.exp(-40.0 * t) * 0.3 if t < 0.02 else 0.0
        samples.append((_metal_ring(t, 210.0, partials) + strike_noise) * 0.85)

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
    """Latido rápido e agressivo do cão Yamato: corpo tonal descendente + ruído áspero de gãnido."""
    duration = 0.16
    num_samples = int(SAMPLE_RATE * duration)
    noise = _white_noise(num_samples)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        decay = math.exp(-22.0 * t)
        freq = 320.0 - 140.0 * (t / duration)
        tone = math.sin(2.0 * math.pi * freq * t) * 0.65
        samples.append((tone + noise[i] * 0.35) * decay * 0.85)

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


def render_all_to_wav_files(output_dir: str) -> list[str]:
    """Renderiza todos os eventos sonoros procedurais como arquivos .wav reais em disco,
    substituindo quaisquer placeholders antigos (uso: regenerar assets/sounds/sfx)."""
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
    os.makedirs(output_dir, exist_ok=True)
    written = []
    for event, gen in _GENERATOR_MAP.items():
        sound = gen()
        raw = sound.get_raw()
        path = os.path.join(output_dir, f"{event.value}.wav")
        with wave.open(path, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(raw)
        written.append(path)
    return written


if __name__ == "__main__":
    import sys
    _target_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "..", "assets", "sounds", "sfx"
    )
    _target_dir = os.path.abspath(_target_dir)
    _paths = render_all_to_wav_files(_target_dir)
    print(f"Gerados {len(_paths)} arquivos .wav em {_target_dir}")
