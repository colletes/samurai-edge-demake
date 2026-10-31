"""
Entregável 8.1.3: Tela de Créditos com Slideshow de Imagens Promocionais e de Conceito.
Exibida ao concluir com sucesso o Modo Arcade (derrota do Chefe Final Oni Gashadokuro).
Apresenta transições suaves (crossfade), letterboxing cinematográfico, cartões de texto
localizados para Game Design/QA, Apoiadores e Agradecimento Especial.
"""
import glob
import math
import os
import re
import pygame

from src.config import COLOR_GOLD, COLOR_WHITE, SCREEN_HEIGHT, SCREEN_WIDTH, get_asset_path
from src.i18n import get_lang, t
from src.ui.fonts import get_text_font, get_title_font
from src.ui.game_logo import get_logo
from src.ui.svg_icon_renderer import render_text_with_icons

# Lista ordenada de 13 slides sincronizados com o tema de encerramento (291 segundos)
SLIDE_CONFIG = [
    {
        "slide_idx": 0,
        "duration": 30.0,
        "fallback": "assets/concepts/gashadokuro_concept.jpg",
        "header_key": "credits_title",
        "name_key": "credits_subtitle",
        "color": COLOR_GOLD,
    },
    {
        "slide_idx": 1,
        "duration": 20.0,
        "fallback": "assets/concepts/kyoto_bakumatsu_concept.jpg",
    },
    {
        "slide_idx": 2,
        "duration": 20.0,
        "fallback": "assets/concepts/rice_paddies_concept.jpg",
    },
    {
        "slide_idx": 3,
        "duration": 18.0,
        "fallback": "assets/concepts/iga_rooftops_concept.jpg",
        "header_key": "credits_design_qa_role",
        "name_key": "credits_design_qa_name",
        "color": (255, 140, 100),
    },
    {
        "slide_idx": 4,
        "duration": 28.0,
        "fallback": "assets/concepts/mist_temple_concept.jpg",
    },
    {
        "slide_idx": 5,
        "duration": 24.0,
        "fallback": "assets/concepts/kabuki_stage_concept.jpg",
    },
    {
        "slide_idx": 6,
        "duration": 30.0,
        "fallback": "assets/concepts/saitou_julie_kyoto_duel.jpg",
        "header_key": "credits_supporters_role",
        "name_key": "credits_supporters_name",
        "color": (120, 220, 175),
    },
    {
        "slide_idx": 7,
        "duration": 12.0,
        "fallback": "assets/concepts/bamboo_forest_concept.jpg",
    },
    {
        "slide_idx": 8,
        "duration": 16.0,
        "fallback": "assets/concepts/heian_shrine_concept.jpg",
        "header_key": "credits_special_thanks_role",
        "name_key": "credits_special_thanks_name",
        "color": (255, 185, 215),
    },
    {
        "slide_idx": 9,
        "duration": 16.0,
        "fallback": "assets/concepts/gojo_bridge_concept.jpg",
    },
    {
        "slide_idx": 10,
        "duration": 16.0,
        "fallback": "assets/concepts/pirate_deck_concept.jpg",
        "header_key": "credits_tech_role",
        "name_key": "credits_tech_desc",
        "color": (150, 195, 255),
    },
    {
        "slide_idx": 11,
        "duration": 20.0,
        "fallback": "assets/concepts/mountain_shrine_concept.jpg",
    },
    {
        "slide_idx": 12,
        "duration": 41.0,
        "fallback": "assets/concepts/game_ending_concept_1_1.jpg",
        "header_key": "credits_thanks",
        "logo": "dark",  # Logo oficial "Samurai Edge: Bakumatsu"
        "color": COLOR_GOLD,
        "card_delay": 19.0,  # Card surge após o fim dos vocais (269s) para valorizar a foto do elenco
    },
]

# Letras e karaokê sincronizados com o áudio oficial (Samurai Edge - Closing Theme.mp3)
# Regra do padrão cinematográfico:
# - Versos em japonês: exibem tradução em inglês no topo.
# - Versos em inglês: NÃO exibem tradução no topo (permanece limpo).
CLOSING_THEME_LYRICS = [
    # Verso 1 (0:44 - 1:09) [Japonês]
    {
        "start": 44.0, "end": 50.0,
        "sung": "Asahi ga sasu, take no mori ni",
        "trans": "The morning sun shines upon the bamboo forest",
    },
    {
        "start": 50.0, "end": 56.5,
        "sung": "Chōchin no hi wa shizuka ni kie",
        "trans": "The lantern lights quietly fade away",
    },
    {
        "start": 56.5, "end": 63.0,
        "sung": "Kyoto no sora wa kogane ni somari",
        "trans": "Kyoto's sky is dyed in brilliant gold",
    },
    {
        "start": 63.0, "end": 69.0,
        "sung": "Kaze no naka, yaiba wa nemuru",
        "trans": "In the whispering wind, our blades find their sleep",
    },

    # Pré-Refrão (1:09 - 1:26.5) [Inglês - sem tradução no topo]
    {
        "start": 69.0, "end": 73.0,
        "sung": "Sunlight breaking through the shattered gate",
    },
    {
        "start": 73.0, "end": 76.5,
        "sung": "We have conquered the curse of fate",
    },
    {
        "start": 76.5, "end": 80.0,
        "sung": "Ronin, shinobi, scars and pride",
    },
    {
        "start": 80.0, "end": 86.5,
        "sung": "Stand as one on the other side!",
    },

    # Refrão 1 (1:27 - 1:55.5)
    {
        "start": 87.0, "end": 91.0,
        "sung": "Dawn of the golden sky",
    },
    {
        "start": 91.0, "end": 95.0,
        "sung": "Rise from the ashes of night!",
    },
    {
        "start": 95.0, "end": 100.0,
        "sung": "Tsubasa eru tori no yō ni",
        "trans": "Like birds taking wing into the sky",
    },
    {
        "start": 100.0, "end": 102.5,
        "sung": "Beyond the storm, our oath shines bright!",
    },
    {
        "start": 102.5, "end": 105.5,
        "sung": "Tsumi to batsu wo yurushite",
        "trans": "Forgiving the crime and the punishment",
    },
    {
        "start": 105.5, "end": 108.5,
        "sung": "Ride the morning wind, stand for the free!",
    },
    {
        "start": 108.5, "end": 115.5,
        "sung": "Out of the iron and smoke, we found the peace we seek!",
    },

    # Verso 2 (2:22.5 - 2:44.5)
    {
        "start": 142.5, "end": 146.5,
        "sung": "Haru no kaze ga kizu wo iyasu",
        "trans": "The spring breeze heals every wound",
    },
    {
        "start": 146.5, "end": 152.0,
        "sung": "Dōro no kakehashi, hatashita chikai",
        "trans": "Upon the bridge of fate, our promise fulfilled",
    },
    {
        "start": 152.0, "end": 158.0,
        "sung": "No shadows left to chain my soul",
    },
    {
        "start": 158.0, "end": 164.5,
        "sung": "This newborn sunrise makes our spirit whole!",
    },

    # Ponte (2:55.5 - 3:10.5) [Inglês - sem tradução no topo]
    {
        "start": 175.5, "end": 179.0,
        "sung": "Sakura bloom above the quiet stone lake...",
    },
    {
        "start": 179.0, "end": 183.0,
        "sung": "For every fallen soul, a brand new world awaits...",
    },
    {
        "start": 183.0, "end": 190.5,
        "sung": "Into the golden dawn we fly!",
    },

    # Refrão Final (3:54.5 - 4:22.0)
    {
        "start": 234.5, "end": 237.0,
        "sung": "Dawn of the golden sky",
    },
    {
        "start": 237.0, "end": 240.5,
        "sung": "Rise from the ashes of night!",
    },
    {
        "start": 240.5, "end": 245.5,
        "sung": "Tsubasa eru tori no yō ni",
        "trans": "Like birds taking wing into the sky",
    },
    {
        "start": 245.5, "end": 248.0,
        "sung": "Beyond the storm, our oath shines bright!",
    },
    {
        "start": 248.0, "end": 251.2,
        "sung": "Tsumi to batsu wo yurushite",
        "trans": "Forgiving the crime and the punishment",
    },
    {
        "start": 251.2, "end": 254.3,
        "sung": "Through the fire, into the clear sky",
    },
    {
        "start": 254.3, "end": 262.0,
        "sung": "We have crowned a brand new age!",
    },

    # Outro (4:22.0 - 4:28.5) [Japonês]
    {
        "start": 262.0, "end": 268.5,
        "sung": "Yoake wo hirake...",
        "trans": "Open the dawn...",
    },
]

def _load_ass_lyrics(ass_path: str) -> list[dict]:
    """Carrega letras de karaoke e tradução diretamente do arquivo .ass se disponível."""
    if not os.path.isfile(ass_path):
        return []
    import re

    def parse_time(ts: str) -> float:
        parts = ts.strip().split(":")
        if len(parts) == 3:
            return float(parts[0]) * 3600.0 + float(parts[1]) * 60.0 + float(parts[2])
        return 0.0

    karaoke_lines = []
    translation_lines = []
    try:
        with open(ass_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("Dialogue:"):
                    continue
                parts = line.split(",", 9)
                if len(parts) < 10:
                    continue
                style = parts[3].strip()
                st = parse_time(parts[1])
                et = parse_time(parts[2])
                raw = parts[9].strip()
                clean = re.sub(r"\{[^}]*\}", "", raw).strip()
                if "Karaoke" in style or "Default" in style:
                    matches = re.findall(r"\{(\\[kK][fFoO]?(\d+))\}([^\{]*)", raw)
                    syllables = []
                    for full_tag, dur_cs, txt in matches:
                        syllables.append({
                            "dur": float(dur_cs) / 100.0,
                            "text": txt,
                        })
                    if syllables:
                        syllables[-1]["text"] = syllables[-1]["text"].rstrip()
                        clean = "".join(s["text"] for s in syllables)
                    karaoke_lines.append({
                        "start": st,
                        "end": et,
                        "sung": clean,
                        "raw": raw,
                        "syllables": syllables,
                    })
                elif "Translation" in style:
                    translation_lines.append({
                        "start": st,
                        "end": et,
                        "trans": clean,
                    })

        for k in karaoke_lines:
            for tr in translation_lines:
                if abs(k["start"] - tr["start"]) < 0.5 or (tr["start"] <= k["start"] and k["end"] <= tr["end"] + 0.5):
                    k["trans"] = tr["trans"]
                    break
        return karaoke_lines
    except Exception as e:
        print(f"[ArcadeCredits] Erro ao analisar {ass_path}: {e}")
        return []

# Sincronização automática com arquivo .ass gerado pelo usuário no Aegisub
_ass_candidate = get_asset_path("assets/Opening Videos/Samurai_Edge_Credits_Slideshow.ass")
_loaded_ass = _load_ass_lyrics(_ass_candidate)
if _loaded_ass:
    CLOSING_THEME_LYRICS = _loaded_ass

_KARAOKE_FONT_CACHE: dict = {}
_TEXT_OUTLINE_CACHE: dict = {}
_SYLLABLE_LAYOUT_CACHE: dict = {}


def _get_syllable_layout(font, lyric: dict, outline_px: float = 2.5):
    """Calcula posições de pixel contínuas para cada sílaba, preservando kerning cumulativo exato."""
    key = (id(font), lyric.get("sung", ""), outline_px)
    if key in _SYLLABLE_LAYOUT_CACHE:
        return _SYLLABLE_LAYOUT_CACHE[key]

    syllables = lyric.get("syllables", [])
    if not syllables:
        _SYLLABLE_LAYOUT_CACHE[key] = None
        return None

    opx = int(math.ceil(outline_px))
    layout = []
    prefix = ""
    for s in syllables:
        w_before = font.size(prefix)[0]
        prefix += s["text"]
        w_after = font.size(prefix)[0]
        layout.append({
            "text": s["text"],
            "dur": s["dur"],
            "px0": opx + w_before,
            "px1": opx + w_after,
        })

    _SYLLABLE_LAYOUT_CACHE[key] = layout
    return layout


def _get_karaoke_fonts():
    """Retorna fontes Trebuchet MS exatamente como no arquivo Samurai_Edge_Opening_Final.ass."""
    if "fonts" in _KARAOKE_FONT_CACHE:
        return _KARAOKE_FONT_CACHE["fonts"]

    font_path = pygame.font.match_font("Trebuchet MS") or pygame.font.match_font("trebuchet")
    if font_path:
        font_sung = pygame.font.Font(font_path, 38)
        font_trans = pygame.font.Font(font_path, 24)
    else:
        font_sung = get_title_font(38)
        font_trans = get_text_font(24)

    font_sung.bold = True
    font_trans.italic = True
    _KARAOKE_FONT_CACHE["fonts"] = (font_sung, font_trans)
    return font_sung, font_trans


def _render_outlined_text(
    font,
    text: str,
    fill_color: tuple,
    outline_color: tuple = (0, 0, 0),
    outline_px: float = 2.5,
):
    """Renderiza texto com contorno preto e sombra, cacheado para performance."""
    key = (id(font), text, fill_color, outline_color, outline_px)
    if key in _TEXT_OUTLINE_CACHE:
        return _TEXT_OUTLINE_CACHE[key]

    base = font.render(text, True, fill_color)
    bw, bh = base.get_size()
    opx = int(math.ceil(outline_px))
    surf = pygame.Surface((bw + opx * 2 + 2, bh + opx * 2 + 2), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))

    # Sombra suave 1px para baixo e direita (BackColour: &H60000000)
    sh_text = font.render(text, True, (0, 0, 0, 160))
    surf.blit(sh_text, (opx + 1, opx + 1))

    # Contorno circular
    steps = 12
    for i in range(steps):
        angle = (2.0 * math.pi * i) / steps
        dx = int(round(outline_px * math.cos(angle)))
        dy = int(round(outline_px * math.sin(angle)))
        outl = font.render(text, True, outline_color)
        surf.blit(outl, (opx + dx, opx + dy))

    surf.blit(base, (opx, opx))
    _TEXT_OUTLINE_CACHE[key] = surf
    return surf


_IMAGE_CACHE: dict[str, pygame.Surface] = {}


def _resolve_slide_image_path(cfg: dict) -> str:
    """Busca primeiro a imagem gerada em Ending Slides/Slide {idx}*, com fallback."""
    idx = cfg.get("slide_idx")
    if idx is not None:
        folder = get_asset_path("assets/concepts/Ending Slides")
        if os.path.isdir(folder):
            valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
            try:
                for fname in sorted(os.listdir(folder)):
                    low = fname.lower()
                    _, ext = os.path.splitext(low)
                    if ext in valid_exts:
                        if idx == 12:
                            if "slide final" in low or "slide 12" in low or "slide_12" in low or "slide-12" in low:
                                return os.path.join(folder, fname)
                        else:
                            prefix_match = (
                                f"slide {idx}-" in low or
                                f"slide {idx} " in low or
                                f"slide {idx}." in low or
                                f"slide_{idx:02d}" in low or
                                f"slide_{idx}" in low or
                                f"slide{idx}-" in low or
                                low.startswith(f"slide {idx}")
                            )
                            if prefix_match:
                                return os.path.join(folder, fname)
            except OSError:
                pass

    fallback = cfg.get("fallback") or cfg.get("image", "")
    return get_asset_path(fallback)


def _get_scaled_slide_image(path: str) -> pygame.Surface | None:
    """Carrega e escala a ilustração proporcionalmente ao formato da tela com fundo preto."""
    if path in _IMAGE_CACHE:
        return _IMAGE_CACHE[path]

    if not os.path.exists(path):
        return None

    try:
        raw = pygame.image.load(path)
        rw, rh = raw.get_size()
        scale = max(SCREEN_WIDTH / rw, SCREEN_HEIGHT / rh)
        nw, nh = int(rw * scale), int(rh * scale)
        scaled = pygame.transform.smoothscale(raw, (nw, nh))

        comp = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        comp.fill((12, 10, 14))
        # Centralizar na tela
        ox = (SCREEN_WIDTH - nw) // 2
        oy = (SCREEN_HEIGHT - nh) // 2
        comp.blit(scaled, (ox, oy))

        _IMAGE_CACHE[path] = comp
        return comp
    except Exception as e:
        print(f"[ArcadeCredits] Erro ao carregar imagem {path}: {e}")
        return None


class ArcadeCreditsScreen:
    """Tela de Slideshow e Créditos do Modo Arcade com suporte a vídeo pré-renderizado e fallback."""

    def __init__(self):
        self.active = False
        self.run = None
        self.rank = None
        self.high_scores = []
        self.current_slide = 0
        self.slide_timer = 0.0
        self.fade_duration = 1.2     # 1.2s de transição suave / crossfade entre ilustrações
        self.total_time = 0.0
        self.white_fade_in = False
        self.return_to_gallery = False
        self.show_skip_prompt = True

        self.video = None
        self.video_path = None
        self.is_holding = False
        self.hold_timer = 0.0
        self.hold_duration = 1.0     # 1.0s para pular após o desbloqueio
        self.prompt_font = get_text_font(18)
        self.is_ios_native = False

    def open(
        self,
        run,
        rank: int | None = None,
        high_scores: list = None,
        white_fade_in: bool = False,
        return_to_gallery: bool = False,
        show_skip_prompt: bool = True,
    ):
        """Inicializa e abre a tela de créditos com vídeo .mp4 se disponível."""
        self.active = True
        self.run = run
        self.rank = rank
        self.high_scores = high_scores or []
        self.current_slide = 0
        self.slide_timer = 0.0
        self.total_time = 0.0
        self.hold_timer = 0.0
        self.is_holding = False
        self.white_fade_in = white_fade_in
        self.return_to_gallery = return_to_gallery
        self.show_skip_prompt = show_skip_prompt

        # Pré-carregar imagens dos slides em cache para fallback imediato
        for cfg in SLIDE_CONFIG:
            _get_scaled_slide_image(_resolve_slide_image_path(cfg))

        # Busca pelo arquivo de vídeo renderizado com áudio sincronizado
        candidates = [
            get_asset_path("assets/Opening Videos/Samurai_Edge_Credits_Slideshow.mp4"),
            get_asset_path("assets/concepts/Ending Slides/Samurai_Edge_Credits_Slideshow.mp4"),
        ]
        self.video_path = None
        for cand in candidates:
            if os.path.exists(cand):
                self.video_path = cand
                break

        # Tenta carregar reprodutor de vídeo caso não esteja em ambiente headless dummy
        self.video = None
        if self.video_path and os.environ.get("SDL_VIDEODRIVER") != "dummy":
            try:
                from src.ui.video_utils import setup_pyvidplayer2
                has_pyvid, ffmpeg_bin = setup_pyvidplayer2()
                if has_pyvid:
                    from pyvidplayer2 import Video
                    from src.audio.sound_manager import SoundManager

                    # Parar reprodução de trilha de fundo para não misturar áudios
                    SoundManager.get_instance().stop_music()
                    try:
                        if pygame.mixer.get_init():
                            pygame.mixer.music.stop()
                            pygame.mixer.music.unload()
                    except Exception:
                        pass

                    # Tentativa 1: áudio embutido via ffmpeg
                    if ffmpeg_bin:
                        try:
                            self.video = Video(
                                self.video_path,
                                use_pygame_audio=True,
                                chunk_size=120,
                                max_chunks=1,
                            )
                        except Exception:
                            self.video = None

                    # Tentativa 2: vídeo via OpenCV sem ffmpeg + áudio abridged exato
                    if not self.video:
                        try:
                            self.video = Video(self.video_path, no_audio=True)
                            audio_candidates = [
                                get_asset_path("assets/Opening Videos/Samurai_Edge_Credits_Audio.mp3"),
                                get_asset_path("assets/sounds/music/Samurai Edge - Closing Theme.mp3"),
                            ]
                            for cand in audio_candidates:
                                if os.path.exists(cand):
                                    try:
                                        if not pygame.mixer.get_init():
                                            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                                        pygame.mixer.music.load(cand)
                                        pygame.mixer.music.play()
                                        break
                                    except Exception:
                                        pass
                        except Exception as e_noaudio:
                            print(f"[ArcadeCredits] Vídeo não pôde ser carregado ({e_noaudio}), usando modo de slides.")
                            self.video = None

                    if self.video and self.video.original_size != (SCREEN_WIDTH, SCREEN_HEIGHT):
                        self.video.resize((SCREEN_WIDTH, SCREEN_HEIGHT))
                    try:
                        if self.video:
                            self.video.set_volume(1.0)
                    except Exception:
                        pass
            except Exception as e:
                print(f"[ArcadeCredits] Falha geral no player de vídeo: {e}")
                self.video = None

        if not self.video and os.environ.get("SDL_AUDIODRIVER") != "dummy":
            try:
                from src.audio.sound_manager import SoundManager
                SoundManager.get_instance().stop_music()
                closing_audio = get_asset_path("assets/sounds/music/Samurai Edge - Closing Theme.mp3")
                if os.path.exists(closing_audio) and pygame.mixer.get_init():
                    pygame.mixer.music.load(closing_audio)
                    pygame.mixer.music.play()
            except Exception as e:
                print(f"[ArcadeCredits] Erro ao tocar áudio de encerramento: {e}")

    def stop(self):
        """Finaliza e fecha os recursos de vídeo e créditos."""
        self.active = False
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

    def play(self, screen: pygame.Surface, show_skip_prompt: bool = True):
        """Loop modal autônomo para reprodução na Galeria."""
        self.open(None, white_fade_in=False, show_skip_prompt=show_skip_prompt)
        clock = pygame.time.Clock()
        running = True
        while running and self.active:
            dt = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                    running = False
                    break
                res = self.handle_event(event)
                if res == "DONE":
                    running = False
                    break
            if not running or not self.active:
                break
            if self.update(dt) == "DONE":
                break
            self.render(screen)
            pygame.display.flip()
        self.stop()

    def play_video(self, screen: pygame.Surface, show_skip_prompt: bool = True):
        """Alias retrocompatível com chamadas legadas."""
        self.play(screen, show_skip_prompt=show_skip_prompt)

    def update(self, dt: float) -> str | None:
        if not self.active:
            return None

        self.total_time += dt

        # Gerenciamento do botão segurar para pular (disponível após 5 segundos)
        if self.is_holding and self.total_time >= 5.0:
            self.hold_timer += dt
            if self.hold_timer >= self.hold_duration:
                self.stop()
                return "DONE"
        else:
            self.hold_timer = max(0.0, self.hold_timer - dt * 2.5)

        # Se estiver executando via vídeo
        if self.video and self.video.active:
            frame_idx = getattr(self.video, "frame", 0)
            total_frames = getattr(self.video, "frame_count", 0)
            if total_frames > 0 and frame_idx >= total_frames - 2 or not self.video.active:
                self.stop()
                return "DONE"
            return None

        # Fallback procedural de slides
        self.slide_timer += dt
        cur_dur = SLIDE_CONFIG[self.current_slide].get("duration", 20.0) if self.current_slide < len(SLIDE_CONFIG) else 20.0
        if self.slide_timer >= cur_dur:
            self.slide_timer = 0.0
            self.current_slide += 1
            if self.current_slide >= len(SLIDE_CONFIG):
                self.active = False
                return "DONE"

        return None

    def handle_event(self, event: pygame.event.Event, ctrl_mgr=None) -> str | None:
        """
        Interação durante os créditos:
        - Bloqueio nos primeiros 5 segundos para garantir imersão inicial.
        - Após 5 segundos: segurar (Start, Espaço, Enter, Cruz, Mouse, Toque) por 1.0s para pular.
        """
        if not self.active:
            return None

        # Período de trava nos primeiros 5 segundos
        if self.total_time < 5.0:
            return None

        # Teclado
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                self.is_holding = True
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                self.is_holding = False
                self.hold_timer = 0.0

        # Gamepad
        elif event.type == pygame.JOYBUTTONDOWN:
            self.is_holding = True
        elif event.type == pygame.JOYBUTTONUP:
            self.is_holding = False
            self.hold_timer = 0.0

        # Mouse
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_holding = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_holding = False
            self.hold_timer = 0.0

        # Touchscreen
        elif event.type == pygame.FINGERDOWN:
            self.is_holding = True
        elif event.type == pygame.FINGERUP:
            self.is_holding = False
            self.hold_timer = 0.0

        return None

    def render(self, surface: pygame.Surface, render_subtitles: bool = True):
        """Renderiza o vídeo pré-renderizado ou a imagem atual com crossfade autêntico e cartões de créditos."""
        if not self.active:
            return

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        # 1. Se estiver executando pelo reprodutor de vídeo
        if self.video and self.video.active:
            try:
                drawn = self.video.draw(surface, (0, 0), force_draw=True)
                if not drawn and getattr(self.video, "frame_surf", None) is None:
                    surface.fill((0, 0, 0))
            except Exception as e:
                print(f"[ArcadeCredits] Erro na renderização do vídeo: {e}")
                self.stop()
                return
        else:
            # 2. Modo fallback: transição procedural de slides
            idx = min(self.current_slide, len(SLIDE_CONFIG) - 1)
            cfg = SLIDE_CONFIG[idx]
            cur_img = _get_scaled_slide_image(_resolve_slide_image_path(cfg))

            slide_dur = cfg.get("duration", 20.0)
            time_left = slide_dur - self.slide_timer

            # Crossfade entre o slide anterior e o atual
            if self.current_slide > 0 and self.slide_timer < self.fade_duration:
                prev_cfg = SLIDE_CONFIG[self.current_slide - 1]
                prev_img = _get_scaled_slide_image(_resolve_slide_image_path(prev_cfg))
                if prev_img:
                    surface.blit(prev_img, (0, 0))
                else:
                    surface.fill((16, 14, 18))

                if cur_img:
                    alpha = int(255 * max(0.0, min(1.0, self.slide_timer / self.fade_duration)))
                    cur_blend = cur_img.copy()
                    if alpha < 255:
                        fade_m = pygame.Surface(cur_blend.get_size(), pygame.SRCALPHA)
                        fade_m.fill((255, 255, 255, alpha))
                        cur_blend.blit(fade_m, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    surface.blit(cur_blend, (0, 0))
            else:
                if cur_img:
                    surface.blit(cur_img, (0, 0))
                else:
                    surface.fill((16, 14, 18))

            # Transição inicial do Slide 0 (White-in da explosão do Oni ou Fade-in suave de preto)
            if self.current_slide == 0 and self.slide_timer < self.fade_duration:
                alpha = int(255 * (1.0 - (self.slide_timer / self.fade_duration)))
                fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                if self.white_fade_in:
                    fade_overlay.fill((255, 255, 255, alpha))
                else:
                    fade_overlay.fill((10, 8, 12, alpha))
                surface.blit(fade_overlay, (0, 0))

            # Transição final do Slide 12 (Fade out suave para preto nos últimos 3.0s do encerramento)
            if self.current_slide == len(SLIDE_CONFIG) - 1 and time_left < 3.0:
                fade_out_dur = 3.0
                alpha = int(255 * (1.0 - max(0.0, time_left / fade_out_dur)))
                fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                fade_overlay.fill((10, 8, 12, alpha))
                surface.blit(fade_overlay, (0, 0))

            font_sung, font_trans = _get_karaoke_fonts()
            sh = font_sung.get_height()
            sy = SCREEN_HEIGHT - 35 - sh

            # Painel laqueado translúcido para exibição do cartão de créditos (se houver papel/apoiador/logo)
            card_delay = cfg.get("card_delay", 0.0)
            has_card_configured = bool(cfg.get("header_key") or cfg.get("header_text") or cfg.get("logo"))
            has_card = has_card_configured and (self.slide_timer >= card_delay)

            panel_w = 900
            panel_h = 62
            panel_x = cx - panel_w // 2
            panel_y = sy - panel_h - 12  # Posicionado logo acima da legenda de karaokê

            if has_card:
                card_time = self.slide_timer - card_delay
                card_fade = 0.8
                if card_time < card_fade:
                    card_alpha = int(255 * (card_time / card_fade))
                elif time_left < card_fade:
                    card_alpha = int(255 * (time_left / card_fade))
                else:
                    card_alpha = 255

                panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                panel_surf.fill((16, 14, 18, 220))
                card_col = cfg.get("color", COLOR_GOLD)
                pygame.draw.rect(panel_surf, card_col, (0, 0, panel_w, panel_h), 1, border_radius=6)
                pygame.draw.rect(panel_surf, (80, 75, 70), (2, 2, panel_w - 4, panel_h - 4), 1, border_radius=5)

                header_text = t(cfg["header_key"]) if "header_key" in cfg else cfg.get("header_text", "")
                name_text = t(cfg["name_key"]) if "name_key" in cfg else cfg.get("name_text", "")

                logo = get_logo(cfg["logo"], 320) if "logo" in cfg else None
                if logo is not None:
                    lw, lh = logo.get_size()
                    if lh > 44:
                        scale = 44.0 / lh
                        logo = pygame.transform.smoothscale(logo, (int(lw * scale), 44))
                    panel_surf.blit(logo, ((panel_w - logo.get_width()) // 2, (panel_h - logo.get_height()) // 2))
                elif header_text and name_text:
                    font_h = get_title_font(18)
                    font_n = get_title_font(24)
                    sh_head = font_h.render(header_text, True, (12, 10, 14))
                    tx_head = font_h.render(header_text, True, card_col)
                    panel_surf.blit(sh_head, ((panel_w - tx_head.get_width()) // 2 + 1, 9))
                    panel_surf.blit(tx_head, ((panel_w - tx_head.get_width()) // 2, 8))

                    sh_name = font_n.render(name_text, True, (12, 10, 14))
                    tx_name = font_n.render(name_text, True, COLOR_WHITE)
                    panel_surf.blit(sh_name, ((panel_w - tx_name.get_width()) // 2 + 1, 31))
                    panel_surf.blit(tx_name, ((panel_w - tx_name.get_width()) // 2, 30))
                elif header_text or name_text:
                    font_single = get_title_font(24)
                    txt = header_text or name_text
                    col = card_col if header_text else COLOR_WHITE
                    sh_s = font_single.render(txt, True, (12, 10, 14))
                    tx_s = font_single.render(txt, True, col)
                    panel_surf.blit(sh_s, ((panel_w - tx_s.get_width()) // 2 + 1, (panel_h - tx_s.get_height()) // 2 + 1))
                    panel_surf.blit(tx_s, ((panel_w - tx_s.get_width()) // 2, (panel_h - tx_s.get_height()) // 2))

                # Aplicar fade suave do cartão respeitando a Zero Artifacts Policy
                if card_alpha < 255:
                    fade_mask = pygame.Surface(panel_surf.get_size(), pygame.SRCALPHA)
                    fade_mask.fill((255, 255, 255, max(0, min(255, card_alpha))))
                    panel_surf.blit(fade_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                surface.blit(panel_surf, (panel_x, panel_y))

            # -------------------------------------------------------------
            # Legendas Traduzidas (Topo) & Letra do Karaokê com Wipe Animado
            # -------------------------------------------------------------
            if render_subtitles:
                active_lyric = None
                for item in CLOSING_THEME_LYRICS:
                    if item["start"] <= self.total_time <= item["end"]:
                        active_lyric = item
                        break

                if active_lyric is not None:
                    l_start = active_lyric["start"]
                    l_end = active_lyric["end"]

                    fade_window = 0.22
                    in_f = min(1.0, (self.total_time - l_start) / fade_window) if fade_window > 0 else 1.0
                    out_f = min(1.0, (l_end - self.total_time) / fade_window) if fade_window > 0 else 1.0
                    lyric_alpha = int(255 * max(0.0, min(1.0, in_f, out_f)))

                    if lyric_alpha > 5:
                        # 1. Tradução em inglês no topo (apenas para versos em japonês)
                        trans_text = active_lyric.get("trans")
                        if trans_text:
                            surf_trans = _render_outlined_text(
                                font_trans, trans_text, (245, 248, 255), (0, 0, 0), outline_px=1.5
                            )
                            tw, th = surf_trans.get_size()
                            tx = cx - tw // 2
                            ty = 28

                            if lyric_alpha < 255:
                                surf_trans_f = surf_trans.copy()
                                fade_m = pygame.Surface(surf_trans.get_size(), pygame.SRCALPHA)
                                fade_m.fill((255, 255, 255, lyric_alpha))
                                surf_trans_f.blit(fade_m, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                                surface.blit(surf_trans_f, (tx, ty))
                            else:
                                surface.blit(surf_trans, (tx, ty))

                        # 2. Karaokê Animado (Fixo no fundo da tela com wipe por sílaba e kerning pixel-exato)
                        sung_text = active_lyric["sung"]
                        surf_white = _render_outlined_text(
                            font_sung, sung_text, (255, 255, 255), (0, 0, 0), outline_px=2.5
                        )
                        surf_cyan = _render_outlined_text(
                            font_sung, sung_text, (48, 208, 255), (0, 0, 0), outline_px=2.5
                        )

                        sw, sh = surf_white.get_size()
                        sx = cx - sw // 2

                        layout = _get_syllable_layout(font_sung, active_lyric, outline_px=2.5)
                        if layout:
                            elapsed = self.total_time - l_start
                            if elapsed <= 0.0:
                                wipe_w = 0
                            else:
                                acc = 0.0
                                for item in layout:
                                    i_dur = item["dur"]
                                    if elapsed < acc + i_dur:
                                        frac = max(0.0, elapsed - acc) / max(0.001, i_dur)
                                        wipe_w = int(round(item["px0"] + frac * (item["px1"] - item["px0"])))
                                        break
                                    acc += i_dur
                                else:
                                    wipe_w = sw
                        else:
                            dur = max(0.1, l_end - l_start)
                            progress = max(0.0, min(1.0, (self.total_time - l_start) / dur))
                            wipe_w = int(sw * progress)

                        # Composite do wipe de karaokê
                        comp_karaoke = surf_white.copy()
                        if wipe_w > 0:
                            comp_karaoke.blit(surf_cyan, (0, 0), area=pygame.Rect(0, 0, min(sw, wipe_w), sh))

                        if lyric_alpha < 255:
                            fade_ms = pygame.Surface((sw, sh), pygame.SRCALPHA)
                            fade_ms.fill((255, 255, 255, lyric_alpha))
                            comp_karaoke.blit(fade_ms, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                        surface.blit(comp_karaoke, (sx, sy))

        # 3. Indicador de "Segure para pular" com anel radial após 5 segundos de exibição
        if self.show_skip_prompt and self.total_time >= 5.0:
            progress = min(1.0, self.hold_timer / self.hold_duration)
            alpha = int((160 + 60 * math.sin(self.total_time * 2.5)) if self.hold_timer <= 0 else 240)

            prompt_text = t("credits_skip_prompt") if t("credits_skip_prompt") else "Segure para pular"
            prompt_surf = self.prompt_font.render(prompt_text, True, COLOR_WHITE)
            if alpha < 255:
                fade_mask = pygame.Surface(prompt_surf.get_size(), pygame.SRCALPHA)
                fade_mask.fill((255, 255, 255, max(0, min(255, alpha))))
                prompt_surf.blit(fade_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            target_w = surface.get_width()
            target_h = surface.get_height()
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
            cx_ring, cy_ring = 20, pill_h // 2
            r = 10
            pygame.draw.circle(pill_surf, (255, 255, 255, 60), (cx_ring, cy_ring), r, width=2)
            if progress > 0:
                pts = [(cx_ring, cy_ring)]
                steps = max(3, int(32 * progress))
                start_angle = -math.pi / 2.0
                end_angle = start_angle + progress * 2.0 * math.pi
                for s in range(steps + 1):
                    ang = start_angle + (s / float(steps)) * (end_angle - start_angle)
                    pts.append((cx_ring + int(math.cos(ang) * (r + 1)), cy_ring + int(math.sin(ang) * (r + 1))))
                if len(pts) > 2:
                    pygame.draw.polygon(pill_surf, (255, 215, 75, 240), pts)
                    pygame.draw.circle(pill_surf, (255, 245, 180), (cx_ring, cy_ring), max(2, int(r * 0.35)))

            pill_surf.blit(prompt_surf, (40, (pill_h - prompt_surf.get_height()) // 2))
            surface.blit(pill_surf, (pill_x, pill_y))
