#!/usr/bin/env python3
"""
Gera o vídeo cinematográfico em alta qualidade (.mp4) do Slideshow de Créditos e Epílogo
de Samurai Edge: Bakumatsu, sincronizado com o tema vocal de encerramento.

Renderização dos slides e cartões de crédito via Pygame (sem barras pretas letterbox,
com cartões finos e compridos centralizados acima da legenda).
Queima das legendas de Karaokê (.ass) via libass nativa, garantindo timing e renderização
100% idênticos ao Aegisub e VLC, sem nenhum desvio ou atraso.

Resolução: 1280x720 (720p 16:9)
Taxa de quadros: 30 FPS
Áudio: Samurai Edge - Closing Theme.mp3 (291 segundos)
Destino: assets/concepts/Ending Slides/Samurai_Edge_Credits_Slideshow.mp4
         assets/Opening Videos/Samurai_Edge_Credits_Slideshow.mp4
"""

import ctypes
import os
import shutil
import subprocess
import sys
import time
import numpy as np

# Forçar renderizador headless antes de importar pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.arcade.arcade_credits import ArcadeCreditsScreen, SLIDE_CONFIG
from src.config import get_asset_path

# Estruturas C do libass
class ASS_Image(ctypes.Structure):
    pass

ASS_Image._fields_ = [
    ("w", ctypes.c_int),
    ("h", ctypes.c_int),
    ("stride", ctypes.c_int),
    ("bitmap", ctypes.POINTER(ctypes.c_uint8)),
    ("color", ctypes.c_uint32),
    ("dst_x", ctypes.c_int),
    ("dst_y", ctypes.c_int),
    ("next", ctypes.POINTER(ASS_Image)),
]


def load_libass():
    libass_paths = [
        "/opt/homebrew/Cellar/libass/0.17.1/lib/libass.dylib",
        "/opt/homebrew/lib/libass.dylib",
        "/usr/local/lib/libass.dylib",
    ]
    for p in libass_paths:
        if os.path.exists(p):
            lib = ctypes.CDLL(p)
            lib.ass_library_init.restype = ctypes.c_void_p
            lib.ass_renderer_init.restype = ctypes.c_void_p
            lib.ass_renderer_init.argtypes = [ctypes.c_void_p]
            lib.ass_set_frame_size.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
            lib.ass_set_fonts.argtypes = [
                ctypes.c_void_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_int,
                ctypes.c_char_p,
                ctypes.c_int,
            ]
            lib.ass_read_file.restype = ctypes.c_void_p
            lib.ass_read_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
            lib.ass_render_frame.restype = ctypes.POINTER(ASS_Image)
            lib.ass_render_frame.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_longlong,
                ctypes.POINTER(ctypes.c_int),
            ]
            return lib
    raise RuntimeError("libass.dylib não encontrado no sistema.")


def main():
    print("=" * 70)
    print("SAMURAI EDGE: BAKUMATSU — GERADOR DE VÍDEO DOS CRÉDITOS (.MP4)")
    print("Renderização de legendas nativa via libass com timing pixel-exato")
    print("=" * 70)

    audio_path = get_asset_path("assets/sounds/music/Samurai Edge - Closing Theme.mp3")
    if not os.path.exists(audio_path):
        print(f"ERRO: Áudio não encontrado: {audio_path}")
        sys.exit(1)

    ass_path = get_asset_path("assets/Opening Videos/Samurai_Edge_Credits_Slideshow.ass")
    if not os.path.exists(ass_path):
        print(f"ERRO: Arquivo ASS não encontrado: {ass_path}")
        sys.exit(1)

    out_folder_1 = get_asset_path("assets/concepts/Ending Slides")
    out_video_1 = os.path.join(out_folder_1, "Samurai_Edge_Credits_Slideshow.mp4")

    out_folder_2 = get_asset_path("assets/Opening Videos")
    out_video_2 = os.path.join(out_folder_2, "Samurai_Edge_Credits_Slideshow.mp4")

    # Inicializar libass
    print("Carregando libass...")
    libass = load_libass()
    ass_lib = libass.ass_library_init()
    renderer = libass.ass_renderer_init(ass_lib)

    width, height = 1280, 720
    libass.ass_set_frame_size(renderer, width, height)
    libass.ass_set_fonts(renderer, None, b"Trebuchet MS", 1, None, 1)

    ass_track = libass.ass_read_file(ass_lib, ass_path.encode("utf-8"), b"UTF-8")
    if not ass_track:
        print(f"ERRO ao carregar arquivo de legenda: {ass_path}")
        sys.exit(1)
    print(f"Legenda carregada com sucesso: {ass_path}")

    # Inicializar Pygame
    pygame.init()
    screen = pygame.Surface((width, height))

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

    # Testar se h264_videotoolbox está disponível
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
        "-c:v", "h264_videotoolbox",
        "-b:v", "6000k",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        out_video_1,
    ]

    print("\nIniciando renderização e composição libass...")
    t_start = time.time()
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    detect_change = ctypes.c_int(0)

    try:
        for f in range(total_frames):
            # 1. Renderizar slides e cartões de créditos (sem legendas Pygame)
            credits.render(screen, render_subtitles=False)

            # Converter tela Pygame para array NumPy RGB uint8
            raw_rgb = pygame.image.tobytes(screen, "RGB")
            frame = np.frombuffer(raw_rgb, dtype=np.uint8).reshape((height, width, 3)).copy()

            # 2. Renderizar legendas ASS pelo libass no milissegundo exato
            ms = int((f / fps) * 1000)
            img_ptr = libass.ass_render_frame(renderer, ass_track, ms, ctypes.byref(detect_change))

            curr = img_ptr
            while curr:
                img = curr.contents
                w, h, stride = img.w, img.h, img.stride
                dst_x, dst_y = img.dst_x, img.dst_y
                color = img.color

                # Desempacotar RGBA do libass (0xRRGGBBAA)
                r = (color >> 24) & 0xFF
                g = (color >> 16) & 0xFF
                b = (color >> 8) & 0xFF
                a = 255 - (color & 0xFF)

                if a > 0 and w > 0 and h > 0:
                    buf = np.ctypeslib.as_array(img.bitmap, shape=(h, stride))[:, :w]
                    alpha = (buf.astype(np.float32) / 255.0) * (a / 255.0)

                    x1, y1 = max(0, dst_x), max(0, dst_y)
                    x2, y2 = min(width, dst_x + w), min(height, dst_y + h)

                    bx1, by1 = x1 - dst_x, y1 - dst_y
                    bx2, by2 = bx1 + (x2 - x1), by1 + (y2 - y1)

                    sub_alpha = alpha[by1:by2, bx1:bx2, np.newaxis]
                    rgb_val = np.array([r, g, b], dtype=np.float32)

                    slice_dst = frame[y1:y2, x1:x2].astype(np.float32)
                    frame[y1:y2, x1:x2] = (slice_dst * (1.0 - sub_alpha) + rgb_val * sub_alpha).astype(np.uint8)

                curr = curr.contents.next

            # Escrever quadro compositado no pipe do ffmpeg
            proc.stdin.write(frame.tobytes())

            # Avançar temporizador da tela de créditos
            credits.update(dt)

            if (f + 1) % (fps * 15) == 0 or (f + 1) == total_frames:
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
