"""
Tela / Player do Video de Abertura: Samurai Edge Bakumatsu.
Exibido antes da Tela de Titulo.
Permite pular com um toque no Start (Options/Menu) ou Cross (Confirm/Espaco/Enter/Clique/Toque).
FIXED: Usa SVG dos botoes PlayStation em vez de texto simples.
"""
import os
import math
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, get_asset_path, COLOR_WHITE
from src.ui.fonts import get_text_font
from src.i18n import t


class OpeningVideoScreen:
    """Controla a reproducao do video cinematografico de abertura."""

    def __init__(self, video_path: str = None):
        self.font = get_text_font(18)
        self.video = None
        self.video_path = video_path
        self.is_finished = False
        self.is_ios_native = False
        self.prompt_timer = 0.0
        self.hold_timer = 0.0
        self.is_holding = False
        self.hold_pos = (SCREEN_WIDTH - 140, SCREEN_HEIGHT - 60)
        self.open(video_path)

    def open(self, video_path: str = None):
        """Inicializa ou reinicializa a reprodução do vídeo de abertura."""
        self.stop()
        self.is_finished = False
        self.prompt_timer = 0.0
        self.hold_timer = 0.0
        self.is_holding = False
        self.is_ios_native = False
        self.hold_pos = (SCREEN_WIDTH - 140, SCREEN_HEIGHT - 60)

        if not video_path and not self.video_path:
            candidates = [
                get_asset_path("assets/Opening Videos/Samurai_Edge_Opening_Final.mp4"),
                get_asset_path("assets/Opening Videos/Samurai_Edge_Opening.mp4"),
            ]
            for c_path in candidates:
                if os.path.exists(c_path):
                    video_path = c_path
                    break
            if not video_path:
                video_path = candidates[0]
        elif video_path:
            self.video_path = video_path

        # Em ambiente headless ou se arquivo não existir, encerrar de imediato
        if os.environ.get("SDL_VIDEODRIVER") == "dummy" or not self.video_path or not os.path.exists(self.video_path):
            self.is_finished = True
            return

        # Tentativa de reprodução nativa acelerada no iOS via AVPlayer
        self.is_ios_native = False
        try:
            import ctypes
            self._ios_lib = ctypes.CDLL(None)
            self._ios_lib.play_native_ios_video.argtypes = [ctypes.c_char_p]
            self._ios_lib.play_native_ios_video.restype = None
            self._ios_lib.stop_native_ios_video.argtypes = []
            self._ios_lib.stop_native_ios_video.restype = None
            self._ios_lib.is_native_ios_video_playing.argtypes = []
            self._ios_lib.is_native_ios_video_playing.restype = ctypes.c_int

            abs_path = os.path.abspath(self.video_path)
            if os.path.exists(abs_path):
                self._ios_lib.play_native_ios_video(abs_path.encode("utf-8"))
                self.is_ios_native = True
                return
        except Exception:
            self.is_ios_native = False

        try:
            from pyvidplayer2 import Video
            import pyvidplayer2.mixer_handler

            # Blindagem defensiva do MixerHandler contra quedas de driver, CoreAudio reset e hotplug de gamepad
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
                    from io import BytesIO
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

            # Parar qualquer música de fundo anterior antes de inicializar o player
            try:
                from src.audio.sound_manager import SoundManager
                SoundManager.get_instance().stop_music()
            except Exception:
                pass

            # use_pygame_audio=True garante que o audio saia pelo mixer do Pygame (dispositivo de som ativo do jogo)
            # chunk_size=120 carrega a trilha inteira (99.6s) em um unico buffer continuo sem cortes
            self.video = Video(self.video_path, use_pygame_audio=True, chunk_size=120, max_chunks=1)
            if self.video.original_size != (SCREEN_WIDTH, SCREEN_HEIGHT):
                self.video.resize((SCREEN_WIDTH, SCREEN_HEIGHT))
            try:
                self.video.set_volume(1.0)
            except Exception:
                pass
        except Exception as e:
            print(f"[OpeningVideoScreen] Falha ao carregar video: {e}")
            self.is_finished = True
            if self.video:
                try:
                    self.video.close()
                except Exception:
                    pass
                self.video = None

    def play(self, screen: pygame.Surface):
        """Loop modal autônomo para reprodução na Galeria ou cutscene."""
        self.open()
        if self.is_finished:
            return
        clock = pygame.time.Clock()
        running = True
        while running and not self.is_finished:
            dt = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                    running = False
                    break
                if self.handle_event(event):
                    running = False
                    break
            if not running or self.is_finished:
                break
            self.update(dt)
            self.render(screen)
            pygame.display.flip()
        self.stop()

    def handle_event(self, event) -> bool:
        """
        Processa eventos de entrada para pular a abertura.
        Retorna True se o video foi pulado, False se continua.
        """
        if self.is_finished:
            return True

        # Periodo de carencia de 0.25s para ignorar cliques residuais de foco de janela no startup
        if self.prompt_timer < 0.25:
            return False

        try:
            should_skip = False

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                    should_skip = True

            elif event.type == pygame.JOYBUTTONDOWN:
                from src.input.controller_manager import get_controller_manager
                ctrl_mgr = get_controller_manager()
                if (ctrl_mgr.is_event_menu_pause(event, 0) or
                    ctrl_mgr.is_event_menu_pause(event, 1) or
                    event.button in (6, 7)):
                    should_skip = True
                elif (ctrl_mgr.is_event_menu_confirm(event) or
                      ctrl_mgr.is_event_menu_cancel(event) or
                      event.button in (0, 1, 2)):
                    self.is_holding = True

            elif event.type == pygame.JOYBUTTONUP:
                self.is_holding = False
                self.hold_timer = 0.0

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.is_holding = True
                self.hold_pos = getattr(event, "pos", self.hold_pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_holding = False
                self.hold_timer = 0.0

            elif event.type == pygame.FINGERDOWN:
                self.is_holding = True
                self.hold_pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT)

            elif event.type == pygame.FINGERUP:
                self.is_holding = False
                self.hold_timer = 0.0

            if should_skip:
                self.stop()
                return True

            return False
        except Exception as e:
            print(f"[OpeningVideoScreen] Erro no processamento de eventos: {e}")
            return False

    def update(self, dt: float):
        """Atualiza estado e temporizadores do player de video."""
        if self.is_finished:
            return

        try:
            self.prompt_timer += dt

            if self.is_holding:
                self.hold_timer += dt
                if self.hold_timer >= 0.75:
                    self.stop()
                    return
            else:
                self.hold_timer = max(0.0, self.hold_timer - dt * 2.5)

            if self.is_ios_native:
                if not self._ios_lib.is_native_ios_video_playing():
                    self.is_finished = True
                return

            if not self.video or not self.video.active:
                self.stop()
                return

            frame_idx = getattr(self.video, "frame", 0)
            total_frames = getattr(self.video, "frame_count", 0)
            if total_frames > 0 and frame_idx >= total_frames - 2:
                self.stop()
        except Exception as e:
            print(f"[OpeningVideoScreen] Erro no update do video: {e}")
            self.stop()

    def render(self, screen: pygame.Surface):
        """Renderiza o quadro atual do video e a legenda de 'Segure para pular' com anel de progresso radial."""
        if self.is_finished:
            return

        if self.is_ios_native:
            screen.fill((0, 0, 0))
            return

        if self.video and self.video.active:
            try:
                drawn = self.video.draw(screen, (0, 0), force_draw=True)
                if not drawn and getattr(self.video, "frame_surf", None) is None:
                    screen.fill((0, 0, 0))
            except Exception as e:
                print(f"[OpeningVideoScreen] Erro na renderizacao do video: {e}")
                self.stop()
                return
        else:
            screen.fill((0, 0, 0))

        # Indicador de "Segure para pular" com progresso radial
        progress = min(1.0, self.hold_timer / 0.75)
        pulse = 0.85 + 0.15 * math.sin(self.prompt_timer * 4.0) if self.hold_timer <= 0 else 1.0
        alpha = int((160 + 60 * math.sin(self.prompt_timer * 2.5)) if self.hold_timer <= 0 else 230)

        prompt_text = "Segure para pular"
        prompt_surf = self.font.render(prompt_text, True, COLOR_WHITE)
        if alpha < 255:
            fade_mask = pygame.Surface(prompt_surf.get_size(), pygame.SRCALPHA)
            fade_mask.fill((255, 255, 255, max(0, min(255, alpha))))
            prompt_surf.blit(fade_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        target_w = screen.get_width()
        target_h = screen.get_height()
        pill_w = prompt_surf.get_width() + 56
        pill_h = 38
        margin = 32
        pill_x = target_w - pill_w - margin
        pill_y = target_h - pill_h - margin

        pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pill_surf.fill((0, 0, 0, 0))
        bg_color = (0, 0, 0, int(alpha * 0.70)) if self.hold_timer <= 0 else (15, 12, 10, int(alpha * 0.90))
        pygame.draw.rect(pill_surf, bg_color, (0, 0, pill_w, pill_h), border_radius=19)
        border_col = (215, 185, 95, alpha) if self.hold_timer > 0 else (160, 140, 90, int(alpha * 0.6))
        pygame.draw.rect(pill_surf, border_col, (0, 0, pill_w, pill_h), width=1, border_radius=19)

        # Anel de progresso circular
        cx, cy = 20, pill_h // 2
        r = 10
        pygame.draw.circle(pill_surf, (255, 255, 255, 60), (cx, cy), r, width=2)
        if progress > 0:
            # Desenha fatias radiais do progresso
            pts = [(cx, cy)]
            steps = max(3, int(32 * progress))
            start_angle = -math.pi / 2.0
            end_angle = start_angle + progress * 2.0 * math.pi
            for s in range(steps + 1):
                ang = start_angle + (s / float(steps)) * (end_angle - start_angle)
                pts.append((cx + int(math.cos(ang) * (r + 1)), cy + int(math.sin(ang) * (r + 1))))
            if len(pts) > 2:
                pygame.draw.polygon(pill_surf, (255, 215, 75, 240), pts)
                pygame.draw.circle(pill_surf, (255, 245, 180), (cx, cy), max(2, int(r * 0.35)))

        pill_surf.blit(prompt_surf, (40, (pill_h - prompt_surf.get_height()) // 2))
        screen.blit(pill_surf, (pill_x, pill_y))

    def stop(self):
        """Finaliza e fecha o leitor de video liberando recursos."""
        self.is_finished = True
        if self.is_ios_native:
            try:
                self._ios_lib.stop_native_ios_video()
            except Exception:
                pass
        if self.video:
            try:
                self.video.close()
            except Exception:
                pass
            self.video = None
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass

    def close(self):
        self.stop()