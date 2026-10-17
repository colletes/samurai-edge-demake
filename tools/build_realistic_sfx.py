"""
Script para síntese acústica realista e geração do banco de efeitos sonoros feudais (Fase M-3.1).
Renderiza modelos físicos de áudio (ressonância metálica, lâminas de aço temperado, impactos viscerais,
estilhaçamento de bambu e passos por superfície) como arquivos WAV 16-bit 44.1kHz estéreo em assets/sounds/sfx/.

Uso:
    ./venv/bin/python tools/build_realistic_sfx.py
"""
import os
import sys
import wave
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.audio.procedural_sfx import _GENERATOR_MAP, SAMPLE_RATE
from src.audio.sound_events import SoundEvent

OUTPUT_DIR = os.path.join(ROOT, "assets", "sounds", "sfx")


def build_all_realistic_sfx(output_dir: str = OUTPUT_DIR) -> list[str]:
    """Renderiza a biblioteca de SFX foley autêntica com gravações reais de alta fidelidade."""
    # 1. Executar masterização Foley autêntica (amostras reais gravadas)
    from tools.upgrade_realistic_audio import build_all_audio
    build_all_audio()

    # 2. Para quaisquer eventos adicionais que não estejam na suite foley, sintetizar proceduralmente
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)

    os.makedirs(output_dir, exist_ok=True)
    generated_files = []

    for event, generator_fn in _GENERATOR_MAP.items():
        event_name = event.value if isinstance(event, SoundEvent) else str(event)
        file_path = os.path.join(output_dir, f"{event_name}.wav")
        if not os.path.exists(file_path):
            sound = generator_fn()
            raw_bytes = sound.get_raw()
            with wave.open(file_path, "wb") as wf:
                wf.setnchannels(2)        # Estéreo
                wf.setsampwidth(2)        # 16-bit
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(raw_bytes)
            generated_files.append(file_path)

    print(f"✨ Concluído! Banco de áudio Foley atualizado com sucesso em {output_dir}.")
    return generated_files


if __name__ == "__main__":
    build_all_realistic_sfx()
