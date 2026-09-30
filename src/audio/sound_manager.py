"""
Gerenciador central de áudio (SoundManager Singleton) para o Samurai Edge Demake.
Controla canais de efeitos sonoros (SFX), música de fundo (BGM), volumes globais,
fallback procedural automático e carregamento de arquivos de disco.
"""
import os
import pygame
from src.audio.sound_events import SoundEvent, MusicTrack
from src.audio.procedural_sfx import generate_procedural_sound


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SFX_DIR = os.path.join(BASE_DIR, "assets", "sounds", "sfx")
MUSIC_DIR = os.path.join(BASE_DIR, "assets", "sounds", "music")


class SoundManager:
    """Gerenciador de áudio unificado com suporte a cache, fallback procedural e controle de canais."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @classmethod
    def get_instance(cls) -> "SoundManager":
        """Retorna a instância única (Singleton) do gerenciador."""
        return cls()

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.master_volume: float = 1.0
        self.sfx_volume: float = 0.85
        self.bgm_volume: float = 0.65

        self.is_audio_available: bool = False
        self._sfx_cache: dict[str, pygame.mixer.Sound] = {}
        self.current_music_track: str | None = None

        self._init_mixer()

    def _init_mixer(self):
        """Inicializa o pygame.mixer com parâmetros de baixa latência e alta fidelidade."""
        try:
            if not pygame.mixer.get_init():
                # 44.1kHz, 16-bit com sinal, 2 canais (estéreo), buffer de 512 amostras para baixa latência
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(24)  # Até 24 sons simultâneos sem interrupções
            self.is_audio_available = True
        except Exception as e:
            # Fallback seguro para ambientes sem hardware de som
            self.is_audio_available = False

    def get_sound(self, event: SoundEvent | str) -> pygame.mixer.Sound | None:
        """
        Retorna o som correspondente ao evento.
        Busca primeiro em disco (assets/sounds/sfx/*.ogg ou *.wav).
        Se não existir, gera proceduralmente em memória e faz cache.
        """
        if not self.is_audio_available:
            return None

        event_key = event.value if isinstance(event, SoundEvent) else str(event)
        if event_key in self._sfx_cache:
            return self._sfx_cache[event_key]

        # 1. Tentar carregar de arquivo externo em disco
        for ext in (".ogg", ".wav", ".mp3"):
            file_path = os.path.join(SFX_DIR, f"{event_key}{ext}")
            if os.path.isfile(file_path):
                try:
                    sound = pygame.mixer.Sound(file_path)
                    self._sfx_cache[event_key] = sound
                    return sound
                except Exception:
                    pass

        # 2. Fallback procedural em memória
        if isinstance(event, SoundEvent):
            sound = generate_procedural_sound(event)
            if sound:
                self._sfx_cache[event_key] = sound
                return sound

        return None

    def play(self, event: SoundEvent | str, volume_scale: float = 1.0) -> pygame.mixer.Channel | None:
        """
        Toca um efeito sonoro (SFX) ajustando o volume relativo pelo volume global.
        Retorna o canal de reprodução do pygame.
        """
        if not self.is_audio_available:
            return None

        sound = self.get_sound(event)
        if not sound:
            return None

        eff_vol = max(0.0, min(1.0, self.master_volume * self.sfx_volume * volume_scale))
        sound.set_volume(eff_vol)
        try:
            return sound.play()
        except Exception:
            return None

    def play_music(self, track: MusicTrack | str, fade_ms: int = 800):
        """
        Inicia ou transiciona suavemente a música de fundo (BGM).
        Se o arquivo não existir em disco, silencia a música mantendo o SFX ativo.
        """
        if not self.is_audio_available:
            return

        track_key = track.value if isinstance(track, MusicTrack) else str(track)
        if self.current_music_track == track_key and pygame.mixer.music.get_busy():
            return

        self.current_music_track = track_key
        eff_vol = max(0.0, min(1.0, self.master_volume * self.bgm_volume))

        for ext in (".ogg", ".wav", ".mp3"):
            file_path = os.path.join(MUSIC_DIR, f"{track_key}{ext}")
            if os.path.isfile(file_path):
                try:
                    pygame.mixer.music.fadeout(fade_ms)
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.set_volume(eff_vol)
                    pygame.mixer.music.play(loops=-1, fade_ms=fade_ms)
                    return
                except Exception:
                    pass

    def stop_music(self, fade_ms: int = 500):
        """Para a música com fadeout suave."""
        if not self.is_audio_available:
            return
        try:
            pygame.mixer.music.fadeout(fade_ms)
            self.current_music_track = None
        except Exception:
            pass

    def set_master_volume(self, vol: float):
        """Ajusta o volume geral (0.0 a 1.0)."""
        self.master_volume = max(0.0, min(1.0, vol))
        self._update_music_volume()

    def set_sfx_volume(self, vol: float):
        """Ajusta o volume dos efeitos sonoros (0.0 a 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, vol))

    def set_bgm_volume(self, vol: float):
        """Ajusta o volume da música de fundo (0.0 a 1.0)."""
        self.bgm_volume = max(0.0, min(1.0, vol))
        self._update_music_volume()

    def _update_music_volume(self):
        if self.is_audio_available:
            try:
                eff_vol = max(0.0, min(1.0, self.master_volume * self.bgm_volume))
                pygame.mixer.music.set_volume(eff_vol)
            except Exception:
                pass


_GLOBAL_SOUND_MANAGER: SoundManager | None = None


def get_sound_manager() -> SoundManager:
    """Retorna a instância única e global do SoundManager."""
    global _GLOBAL_SOUND_MANAGER
    if _GLOBAL_SOUND_MANAGER is None:
        _GLOBAL_SOUND_MANAGER = SoundManager()
    return _GLOBAL_SOUND_MANAGER
