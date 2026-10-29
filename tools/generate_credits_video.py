#!/usr/bin/env python3
"""
Gera o vídeo cinematográfico em alta qualidade (.mp4) do Slideshow de Créditos e Epílogo
de Samurai Edge: Bakumatsu, sincronizado com o tema vocal de encerramento.

Resolução: 1280x720 (720p 16:9)
Taxa de quadros: 30 FPS
Áudio: Samurai Edge - Closing Theme.mp3 (291 segundos)
Destino: assets/concepts/Ending Slides/Samurai_Edge_Credits_Slideshow.mp4
         assets/Opening Videos/Samurai_Edge_Credits_Slideshow.mp4
"""

import os
import shutil
import subprocess
import sys
import time

# Forçar renderizador headless antes de importar pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.arcade.arcade_credits import ArcadeCreditsScreen, SLIDE_CONFIG, _resolve_slide_image_path
from src.config import get_asset_path


def main():
    print("=" * 70)
    print("SAMURAI EDGE: BAKUMATSU — GERADOR DE VÍDEO DOS CRÉDITOS (.MP4)")
    print("=" * 70)

    audio_path = get_asset_path("assets/sounds/music/Samurai Edge - Closing Theme.mp3")
    if not os.path.exists(audio_path):
        print(f"ERRO: Áudio não encontrado: {audio_path}")
        sys.exit(1)

    out_folder_1 = get_asset_path("assets/concepts/Ending Slides")
    out_video_1 = os.path.join(out_folder_1, "Samurai_Edge_Credits_Slideshow.mp4")

    out_folder_2 = get_asset_path("assets/Opening Videos")
    out_video_2 = os.path.join(out_folder_2, "Samurai_Edge_Credits_Slideshow.mp4")

    pygame.init()
    width, height = 1280, 720
    screen = pygame.Surface((width, height))

    # Inicializar tela de créditos sem prompt de pular
    credits = ArcadeCreditsScreen()
    credits.open(None, white_fade_in=True, show_skip_prompt=False)

    total_duration = sum(cfg.get("duration", 20.0) for cfg in SLIDE_CONFIG)
    fps = 30
    total_frames = int(round(total_duration * fps))
    dt = 1.0 / fps

    print(f"Slides: {len(SLIDE_CONFIG)}")
    print(f"Duração total: {total_duration:.1f}s ({total_frames} quadros a {fps} FPS)")
    print(f"Áudio de trilha: {audio_path}")
    print(f"Destino principal: {out_video_1}")

    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    if not os.path.exists(ffmpeg_bin):
        print(f"ERRO: ffmpeg não encontrado em {ffmpeg_bin}")
        sys.exit(1)

    cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        out_video_1,
    ]

    print("\nIniciando renderização de quadros e encoding ffmpeg...")
    t_start = time.time()
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        for f in range(total_frames):
            credits.render(screen)
            raw_rgb = pygame.image.tobytes(screen, "RGB")
            proc.stdin.write(raw_rgb)
            credits.update(dt)

            if (f + 1) % (fps * 10) == 0 or (f + 1) == total_frames:
                elapsed = time.time() - t_start
                pct = ((f + 1) / total_frames) * 100
                sec_rendered = (f + 1) / fps
                speed = (f + 1) / max(0.001, elapsed)
                print(
                    f"Progresso: {pct:5.1f}% | {sec_rendered:5.1f}s / {total_duration:.1f}s "
                    f"| {speed:4.1f} fps | decorrido: {elapsed:.1f}s"
                )

        proc.stdin.close()
        proc.wait()
    except Exception as e:
        proc.kill()
        print(f"\nERRO durante renderização: {e}")
        sys.exit(1)

    if proc.returncode != 0:
        err_out = proc.stderr.read().decode("utf-8", errors="ignore")
        print(f"ERRO do ffmpeg (código {proc.returncode}):\n{err_out}")
        sys.exit(1)

    file_size_mb = os.path.getsize(out_video_1) / (1024 * 1024)
    total_time = time.time() - t_start
    print(f"\n[SUCESSO] Vídeo gerado em: {out_video_1}")
    print(f"Tamanho: {file_size_mb:.2f} MB | Tempo de geração: {total_time:.1f}s")

    # Copiar também para assets/Opening Videos se a pasta existir
    if os.path.isdir(out_folder_2):
        shutil.copy2(out_video_1, out_video_2)
        print(f"[SUCESSO] Cópia sincronizada para: {out_video_2}")

    print("=" * 70)


if __name__ == "__main__":
    main()
