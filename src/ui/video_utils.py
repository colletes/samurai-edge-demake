"""
Utilitários de suporte para reprodução de vídeo e áudio via pyvidplayer2 / FFmpeg.
Garante que o FFmpeg empacotado estático (imageio_ffmpeg) ou do sistema seja descoberto
em qualquer ambiente (macOS app bundle, Windows, Linux, venv ou standalone).
"""
import os
import sys
import shutil


def get_ffmpeg_binary():
    """Localiza o binário executável do FFmpeg empacotado ou do sistema."""
    # 1. Tentar imageio_ffmpeg
    try:
        import imageio_ffmpeg
        candidate = imageio_ffmpeg.get_ffmpeg_exe()
        if candidate and os.path.isfile(candidate):
            try:
                os.chmod(candidate, 0o755)
            except Exception:
                pass
            return candidate
    except Exception:
        pass

    # 2. Se congelado via PyInstaller, buscar dentro do bundle (_MEIPASS, Contents/MacOS, etc.)
    search_dirs = []
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            search_dirs.append(sys._MEIPASS)
            search_dirs.append(os.path.join(sys._MEIPASS, "imageio_ffmpeg", "binaries"))
            search_dirs.append(os.path.join(sys._MEIPASS, "_internal", "imageio_ffmpeg", "binaries"))
        exe_dir = os.path.dirname(sys.executable)
        search_dirs.append(exe_dir)
        search_dirs.append(os.path.join(exe_dir, "_internal", "imageio_ffmpeg", "binaries"))
        search_dirs.append(os.path.join(exe_dir, "imageio_ffmpeg", "binaries"))
        # No macOS bundle: SamuraiEdge.app/Contents/MacOS/.. -> SamuraiEdge.app/Contents/Resources
        bundle_res = os.path.normpath(os.path.join(exe_dir, "..", "Resources"))
        if os.path.isdir(bundle_res):
            search_dirs.append(bundle_res)
            search_dirs.append(os.path.join(bundle_res, "imageio_ffmpeg", "binaries"))

    for d in search_dirs:
        if os.path.isdir(d):
            for root, _, files in os.walk(d):
                for f in files:
                    if "ffmpeg" in f.lower() and not f.endswith((".py", ".pyc", ".txt", ".md")):
                        p = os.path.join(root, f)
                        if os.path.isfile(p):
                            try:
                                os.chmod(p, 0o755)
                            except Exception:
                                pass
                            return p

    # 3. PATH do sistema (adicionando Homebrew e MacPorts no macOS caso não estejam)
    if sys.platform == "darwin":
        for extra in ("/opt/homebrew/bin", "/usr/local/bin", "/opt/local/bin"):
            if os.path.isdir(extra) and extra not in os.environ.get("PATH", ""):
                os.environ["PATH"] = extra + os.pathsep + os.environ.get("PATH", "")

    found = shutil.which("ffmpeg")
    if found:
        return found

    return None


def setup_pyvidplayer2():
    """Configura pyvidplayer2 com ffmpeg e aplica patches defensivos."""
    try:
        import pyvidplayer2
    except ImportError:
        return False, None

    ffmpeg_bin = get_ffmpeg_binary()
    if ffmpeg_bin:
        try:
            pyvidplayer2.set_ffmpeg_path(ffmpeg_bin)
        except Exception:
            pass

    # Patch defensivo para ffprobe: caso o executável ffprobe não exista,
    # pyvidplayer2.video.Video.set_audio_track não deve lançar exceção fatal.
    try:
        orig_set_audio_track = pyvidplayer2.video.Video.set_audio_track
        def _safe_set_audio_track(v_self, index):
            try:
                orig_set_audio_track(v_self, index)
            except Exception:
                v_self.audio_channels = 2
                v_self.num_audio_tracks = 1
                v_self.audio_track = index
        pyvidplayer2.video.Video.set_audio_track = _safe_set_audio_track
    except Exception:
        pass

    # Blindagem defensiva do MixerHandler contra quedas de driver e buffers descarregados
    try:
        import pyvidplayer2.mixer_handler
        import pygame
        from io import BytesIO

        def _safe_mixer_get_busy(handler_self):
            try:
                if not pygame.mixer.get_init():
                    try:
                        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                    except Exception:
                        return False
                return bool(pygame.mixer.music.get_busy())
            except Exception:
                return False

        def _safe_mixer_get_pos(handler_self):
            if not getattr(handler_self, "loaded", False):
                return 0.0
            try:
                if not pygame.mixer.get_init():
                    try:
                        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                    except Exception:
                        return 0.0
                return max(0.0, pygame.mixer.music.get_pos() / 1000.0)
            except Exception:
                return 0.0

        def _safe_mixer_load(handler_self, audio_chunk):
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                pygame.mixer.music.load(BytesIO(audio_chunk), "wav")
                handler_self.loaded = True
            except Exception:
                handler_self.loaded = False

        def _safe_mixer_play(handler_self):
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                pygame.mixer.music.play()
            except Exception:
                pass

        def _safe_mixer_stop(handler_self):
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
            except Exception:
                pass

        def _safe_mixer_unload(handler_self):
            try:
                handler_self.stop()
                if pygame.mixer.get_init():
                    pygame.mixer.music.unload()
            except Exception:
                pass
            handler_self.loaded = False

        pyvidplayer2.mixer_handler.MixerHandler.get_busy = _safe_mixer_get_busy
        pyvidplayer2.mixer_handler.MixerHandler.get_pos = _safe_mixer_get_pos
        pyvidplayer2.mixer_handler.MixerHandler.load = _safe_mixer_load
        pyvidplayer2.mixer_handler.MixerHandler.play = _safe_mixer_play
        pyvidplayer2.mixer_handler.MixerHandler.stop = _safe_mixer_stop
        pyvidplayer2.mixer_handler.MixerHandler.unload = _safe_mixer_unload
    except Exception:
        pass

    return True, ffmpeg_bin
