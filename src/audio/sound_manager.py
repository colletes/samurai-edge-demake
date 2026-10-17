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
        self._pitch_pool: dict[str, list[pygame.mixer.Sound]] = {}
        self.current_music_track: str | None = None
        self._pending_music: tuple[str, int, int] | None = None
        self._pending_music_timer: float = 0.0
        self._pending_music_deadline: int = 0

        self._init_mixer()

    def _init_mixer(self):
        """Inicializa o pygame.mixer com parâmetros de baixa latência e alta fidelidade."""
        try:
            if not pygame.mixer.get_init():
                # 44.1kHz, 16-bit com sinal, 2 canais (estéreo), buffer de 512 amostras para baixa latência
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(24)  # Até 24 sons simultâneos sem interrupções
            self.is_audio_available = True
        except Exception:
            # Fallback seguro para ambientes sem hardware de som
            self.is_audio_available = False

    def _build_pitch_variants(self, sound: pygame.mixer.Sound) -> list[pygame.mixer.Sound]:
        """Gera 3 variações de afinação (0.94x grave, 1.00x original, 1.06x agudo) para prevenir monotonia robótica."""
        variants = [sound]
        try:
            import numpy as np
            arr = pygame.sndarray.array(sound)
            if len(arr) > 100:
                for rate in (0.94, 1.06):
                    n_samples = max(10, int(len(arr) / rate))
                    indices = np.linspace(0, len(arr) - 1, n_samples)
                    if arr.ndim == 2:
                        ch0 = np.interp(indices, np.arange(len(arr)), arr[:, 0])
                        ch1 = np.interp(indices, np.arange(len(arr)), arr[:, 1])
                        resampled = np.column_stack((ch0, ch1)).astype(np.int16)
                    else:
                        resampled = np.interp(indices, np.arange(len(arr)), arr).astype(np.int16)
                    var_sound = pygame.sndarray.make_sound(resampled)
                    variants.append(var_sound)
        except Exception:
            pass
        return variants

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

    def get_sound_with_variation(self, event: SoundEvent | str) -> pygame.mixer.Sound | None:
        """Retorna uma variação de afinação de micro-timbre do som solicitado."""
        event_key = event.value if isinstance(event, SoundEvent) else str(event)
        if event_key not in self._pitch_pool:
            base_sound = self.get_sound(event)
            if not base_sound:
                return None
            self._pitch_pool[event_key] = self._build_pitch_variants(base_sound)
        variants = self._pitch_pool.get(event_key)
        if variants:
            import random
            return random.choice(variants)
        return self.get_sound(event)

    def play(self, event: SoundEvent | str, volume_scale: float = 1.0, pitch_variance: bool = True) -> pygame.mixer.Channel | None:
        """
        Toca um efeito sonoro (SFX) ajustando o volume relativo pelo volume global.
        Aplica micro-variação de afinação (±6%) e micro-jitter de volume (±8%) para máxima fidelidade.
        """
        if not self.is_audio_available:
            return None

        if pitch_variance:
            sound = self.get_sound_with_variation(event)
        else:
            sound = self.get_sound(event)

        if not sound:
            return None

        import random
        jitter = random.uniform(0.92, 1.08) if pitch_variance else 1.0
        eff_vol = max(0.0, min(1.0, self.master_volume * self.sfx_volume * volume_scale * jitter))
        sound.set_volume(eff_vol)
        try:
            return sound.play()
        except Exception:
            return None

    def play_layered(self, event: SoundEvent | str, surface: str | None = None, weapon: str | None = None, volume_scale: float = 1.0) -> list[pygame.mixer.Channel]:
        """
        Dispara áudio multi-camada: combina o impacto primário, camada de superfície e timbre de arma.
        """
        channels = []
        # Resolver arma se fornecida e o evento for de ataque/corte
        if weapon and event in (SoundEvent.SWORD_SLASH, "sword_slash"):
            from src.audio.sound_events import get_weapon_swing_event
            event = get_weapon_swing_event(weapon)

        # Resolver superfície se fornecida e o evento for passo
        if surface and event in (SoundEvent.FOOTSTEP, "footstep"):
            from src.audio.sound_events import get_surface_footstep_event
            event = get_surface_footstep_event(surface)

        ch = self.play(event, volume_scale=volume_scale)
        if ch:
            channels.append(ch)

        # Camada visceral para impactos letais e cortes
        if event in (SoundEvent.FATAL_STRIKE, "fatal_strike"):
            ch_visceral = self.play(SoundEvent.FLESH_CLEAVE, volume_scale=volume_scale * 0.85)
            if ch_visceral:
                channels.append(ch_visceral)
            ch_spray = self.play(SoundEvent.ARTERIAL_SPRAY, volume_scale=volume_scale * 0.70)
            if ch_spray:
                channels.append(ch_spray)
        elif event in (SoundEvent.PARRY, "parry"):
            ch_metal = self.play(SoundEvent.ARMOR_CLANG, volume_scale=volume_scale * 0.65)
            if ch_metal:
                channels.append(ch_metal)

        return channels

    def _play_music_file(self, track_key: str, loops: int = -1, fade_in_ms: int = 0) -> bool:
        """Carrega e inicia a reprodução do arquivo de música especificado."""
        if not self.is_audio_available:
            return False

        self.current_music_track = track_key
        eff_vol = max(0.0, min(1.0, self.master_volume * self.bgm_volume))

        for ext in (".ogg", ".wav", ".mp3"):
            file_path = os.path.join(MUSIC_DIR, f"{track_key}{ext}")
            if os.path.isfile(file_path):
                try:
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.set_volume(eff_vol)
                    if fade_in_ms > 0:
                        pygame.mixer.music.play(loops=loops, fade_ms=fade_in_ms)
                    else:
                        pygame.mixer.music.play(loops=loops)
                    return True
                except Exception:
                    pass
        return False

    def play_music(self, track: MusicTrack | str, fade_ms: int = 800, loops: int = -1):
        """
        Inicia ou transiciona suavemente a música de fundo (BGM).
        Se o arquivo não existir em disco, silencia a música mantendo o SFX ativo.
        """
        if not self.is_audio_available:
            return

        self._pending_music = None
        self._pending_music_timer = 0.0
        self._pending_music_deadline = 0

        track_key = track.value if isinstance(track, MusicTrack) else str(track)
        if self.current_music_track == track_key and pygame.mixer.music.get_busy():
            return

        if pygame.mixer.music.get_busy() and fade_ms > 0:
            try:
                pygame.mixer.music.fadeout(fade_ms)
            except Exception:
                pass

        self._play_music_file(track_key, loops=loops, fade_in_ms=fade_ms)

    def play_death_music(self, fadeout_ms: int = 350):
        """
        Aplica um fadeout rápido na música atual do cenário e inicia a música de morte
        (bgm_death) logo em seguida, sem fade-in.
        """
        if not self.is_audio_available:
            return

        # Se já estiver tocando a música de morte ou pendente, não reiniciar
        if self.current_music_track == "bgm_death" or (self._pending_music and self._pending_music[0] == "bgm_death"):
            return

        # Fadeout rápido na música atual se estiver tocando
        if pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.fadeout(fadeout_ms)
            except Exception:
                pass
            self._pending_music = ("bgm_death", 0, 0)
            self._pending_music_timer = max(0.05, fadeout_ms / 1000.0)
            if pygame.get_init():
                self._pending_music_deadline = pygame.time.get_ticks() + fadeout_ms
            else:
                self._pending_music_deadline = 0
        else:
            self._pending_music = None
            self._pending_music_timer = 0.0
            self._pending_music_deadline = 0
            self._play_music_file("bgm_death", loops=0, fade_in_ms=0)

    def update(self, dt: float = 0.0):
        """Atualiza temporizadores de transição suave/agendada de música."""
        if not self.is_audio_available or not self._pending_music:
            return

        should_trigger = False
        if self._pending_music_deadline > 0 and pygame.get_init():
            if pygame.time.get_ticks() >= self._pending_music_deadline:
                should_trigger = True
        else:
            self._pending_music_timer -= dt
            if self._pending_music_timer <= 0:
                should_trigger = True

        if should_trigger:
            track_key, loops, fade_in_ms = self._pending_music
            self._pending_music = None
            self._pending_music_timer = 0.0
            self._pending_music_deadline = 0
            self._play_music_file(track_key, loops=loops, fade_in_ms=fade_in_ms)

    def stop_music(self, fade_ms: int = 500):
        """Para a música com fadeout suave."""
        self._pending_music = None
        self._pending_music_timer = 0.0
        self._pending_music_deadline = 0
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


def play_sfx(event: SoundEvent | str, volume_scale: float = 1.0, pitch_variance: bool = True):
    """Atalho universal para tocar SFX através do SoundManager global."""
    return get_sound_manager().play(event, volume_scale=volume_scale, pitch_variance=pitch_variance)

