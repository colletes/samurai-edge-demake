"""Tela da Galeria de Honra (Artes Conceituais, Vídeos e Músicas/Jukebox).

Desbloqueada após concluir com sucesso o Modo Arcade com qualquer lutador.
"""
import math
import os
import pygame

from src.config import (
    COLOR_GOLD,
    COLOR_WHITE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    get_asset_path,
)
from src.effects import parchment as pm
from src.i18n import t
from src.ui.fonts import get_text_font, get_title_font
from src.ui.svg_icon_renderer import render_text_with_icons

TAB_IMAGES = 0
TAB_VIDEOS = 1
TAB_MUSIC = 2

CAT_ALL = "ALL"
CAT_CHARACTERS = "CHARACTERS"
CAT_ARENAS = "ARENAS"
CAT_ENDING = "ENDING_SLIDES"
FILTER_KEYS = [CAT_ALL, CAT_CHARACTERS, CAT_ARENAS, CAT_ENDING]

# Faixas que contêm vocais cantados com suporte a Karaokê
KARAOKE_TRACKS = {
    "Samurai Edge- Opening Theme",
    "Samurai Edge - Closing Theme",
    "bgm_ninja_challenge",
    "bgm_shadow_cave",
    "bgm_mist_temple",
    "bgm_pirate_deck",
    "bgm_baroque_court",
    "bgm_rice_paddies",
}

# Letras oficiais sincronizadas para o tema de abertura
OPENING_THEME_LYRICS = [
    {"start": 13.2, "end": 18.2, "sung": "Kaze ga naku, take no mori ni", "trans": "Wind howls on the bamboo forest"},
    {"start": 18.21, "end": 23.4, "sung": "Chōchin no hi ga yurete", "trans": "Flickering lantern light"},
    {"start": 23.41, "end": 28.8, "sung": "Kyoto no sora wa akaku somari", "trans": "Kyoto's sky, crimson red"},
    {"start": 29.1, "end": 34.5, "sung": "Hono-o no naka, yaiba ga hibiku", "trans": "Between the fires, blades clash!"},
    {"start": 35.12, "end": 37.88, "sung": "Shadows moving through the broken gates"},
    {"start": 37.88, "end": 40.68, "sung": "Every clan must seal their own fate!"},
    {"start": 40.68, "end": 43.52, "sung": "Ronin, shinobi, honor and blood"},
    {"start": 43.52, "end": 49.5, "sung": "Wash the innocent in the crimson flood!"},
    {"start": 51.25, "end": 52.05, "sung": "HAI!"},
    {"start": 52.16, "end": 56.1, "sung": "Blades in the burning night, cut through the fallen dawn!"},
    {"start": 56.1, "end": 58.5, "sung": "Tsubasa naki tori no yō ni", "trans": "Like birds without wings"},
    {"start": 58.74, "end": 61.66, "sung": "Even if the era dies, our steel will live on!"},
    {"start": 61.66, "end": 64.74, "sung": "Tsumi to batsu wo koete", "trans": "Overcoming crime and punishment"},
    {"start": 64.74, "end": 67.86, "sung": "Strike like thunder, bleed for the weak!"},
    {"start": 67.86, "end": 70.14, "sung": "In this war of iron and smoke"},
    {"start": 70.14, "end": 74.82, "sung": "We forge the peace we seek!"},
]

try:
    from src.arcade.arcade_credits import CLOSING_THEME_LYRICS
except Exception:
    CLOSING_THEME_LYRICS = []

FRIENDLY_NAMES = {
    "Samurai Edge- Opening Theme": "Tema Vocal de Abertura (Shojumaru)",
    "Samurai Edge - Closing Theme": "Tema de Encerramento (Alvorada)",
    "bgm_bamboo": "Floresta de Bambu (Kenshi)",
    "bgm_ganryu_island": "Ilha Ganryū (Musashi)",
    "bgm_iga_rooftops": "Telhados de Iga (Hanzo)",
    "bgm_forest_camp": "Acampamento na Floresta (Joe)",
    "bgm_kyoto": "Kyoto em Chamas (Saitou)",
    "bgm_nagashino_field": "Campo de Nagashino (Teppo)",
    "bgm_shadow_cave": "Gruta das Sombras (Murasaki)",
    "bgm_mist_temple": "Templo na Névoa (Kasumi)",
    "bgm_kabuki_stage": "Palco Kabuki (Okuni)",
    "bgm_mountain_shrine": "Santuário na Montanha (Tomoe)",
    "bgm_pirate_deck": "Convés na Tempestade (Anne)",
    "bgm_baroque_court": "Pátio Barroco (Julie)",
    "bgm_shaolin_temple": "Pátio Shaolin (Ren)",
    "bgm_higanbana_garden": "Lírios Carmim (Chiyo)",
    "bgm_gojo_bridge": "Ponte Gojo (Benkei)",
    "bgm_yoshiwara_alley": "Beco Yoshiwara (O-Rin)",
    "bgm_rice_paddies": "Arrozais Terraciados (Goro)",
    "bgm_rain_mill": "Moinho na Chuva (Ichi)",
    "bgm_prussian_cemetery": "Cemitério Gótico (Valerius)",
    "bgm_heian_temple": "Pavilhão Astral Heian (Seimei)",
    "bgm_pine_forest": "Floresta dos Pinheiros (Daiki)",
    "bgm_ezo_taiga": "Taiga Gelada de Ezo (Aoi)",
    "bgm_sacred_dohyo": "Dohyō Sagrado (Raiden)",
    "bgm_dejima_dock": "Armazém de Dejima (Hendrika)",
    "bgm_ninja_challenge": "Desafio Ninja (Joe, Kasumi, Murasaki, Hanzo)",
    "bgm_gashadokuro": "Cemitério da Ossada (Oni Gashadokuro)",
    "bgm_menu": "Tema do Menu Principal",
    "bgm_char_select": "Seleção de Lutadores",
    "bgm_death": "Cena de Morte / Fim de Round",
    "bgm_death_full": "Elegia dos Caídos",
}


def _clean_concept_name(filename: str) -> str:
    stem = os.path.splitext(filename)[0]
    for suf in ("_full_concept", "_concept"):
        if stem.endswith(suf):
            stem = stem[: -len(suf)]
    return stem.replace("_", " ").title()


def _clean_slide_title(filename: str) -> str:
    import re
    stem = os.path.splitext(filename)[0]
    cleaned = re.sub(r"\s*\([^)]*\)", "", stem)
    if "SLIDE FINAL" in cleaned.upper() or "🌅" in cleaned:
        return "Slide Final ― Monte Fuji (Elenco Completo)"
    if "-" in cleaned:
        parts = cleaned.split("-", 1)
        slide_part = parts[0].strip()
        desc_part = parts[1].strip()
        return f"{slide_part} ― {desc_part}"
    return cleaned.replace("_", " ").title()


class GalleryScreen:
    """Tela da Galeria de Honra integrada ao Menu de Opções."""

    def __init__(self):
        self.is_open = False
        self.current_tab = TAB_IMAGES
        self.current_filter = CAT_ALL
        self.image_index = 0
        self.video_index = 0
        self.music_index = 0

        self.concept_entries: list[dict] = []
        self.concept_images: list[str] = []
        self._image_cache: dict[str, pygame.Surface] = {}
        self.music_tracks: list[str] = []

        self.is_playing_music = False
        self.current_playing_track: str | None = None
        self.music_playback_time = 0.0

        self.karaoke_enabled = True
        self.is_looping = True

        # Retângulos clicáveis
        self.tab_rects: list[pygame.Rect] = []
        self.filter_rects: list[tuple[pygame.Rect, str]] = []
        self.prev_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.next_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.play_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.stop_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.prev_track_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.next_track_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.loop_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.karaoke_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.music_scroll_up_rect = pygame.Rect(0, 0, 0, 0)
        self.music_scroll_down_rect = pygame.Rect(0, 0, 0, 0)
        self.music_item_rects: list[tuple[pygame.Rect, int]] = []
        self.back_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.video_cards_rects: list[pygame.Rect] = []

        self._scan_assets()

    def get_current_items(self) -> list[dict]:
        """Retorna as imagens filtradas pela categoria ativa."""
        if self.current_filter == CAT_ALL:
            return self.concept_entries
        return [e for e in self.concept_entries if e["category"] == self.current_filter]

    def _scan_assets(self):
        """Escaneia as pastas de imagens conceituais, ending slides e músicas."""
        self.concept_entries = []
        valid_exts = (".jpg", ".jpeg", ".png")

        # 1. Artes Conceituais Principais (assets/concepts)
        concepts_dir = get_asset_path("assets/concepts")
        if os.path.isdir(concepts_dir):
            for f in sorted(os.listdir(concepts_dir)):
                if not f.lower().endswith(valid_exts):
                    continue
                full_p = os.path.join(concepts_dir, f)
                if not os.path.isfile(full_p):
                    continue

                # Classificação em categorias
                f_lower = f.lower()
                if "ending" in f_lower:
                    cat = CAT_ENDING
                elif "_full_concept" in f_lower or "roster_" in f_lower or "_duel" in f_lower:
                    cat = CAT_CHARACTERS
                elif "_concept" in f_lower:
                    cat = CAT_ARENAS
                else:
                    cat = CAT_CHARACTERS

                self.concept_entries.append({
                    "path": full_p,
                    "filename": f,
                    "rel_path": f,
                    "category": cat,
                    "title": _clean_concept_name(f),
                })

        # 2. Ensaios de Fim / Ending Slides em Arte Pura (assets/concepts/Ending Slides)
        ending_dir = get_asset_path("assets/concepts/Ending Slides")
        if os.path.isdir(ending_dir):
            for f in sorted(os.listdir(ending_dir)):
                if not f.lower().endswith(valid_exts):
                    continue
                full_p = os.path.join(ending_dir, f)
                if not os.path.isfile(full_p):
                    continue

                rel_p = os.path.join("Ending Slides", f)
                self.concept_entries.append({
                    "path": full_p,
                    "filename": f,
                    "rel_path": rel_p,
                    "category": CAT_ENDING,
                    "title": _clean_slide_title(f),
                })

        # Lista retrocompatível mantendo len >= 50
        self.concept_images = [e["rel_path"] for e in self.concept_entries]

        # 3. Músicas e Trilhas
        music_dir = get_asset_path("assets/sounds/music")
        if os.path.isdir(music_dir):
            m_files = [
                os.path.splitext(f)[0]
                for f in os.listdir(music_dir)
                if f.lower().endswith((".mp3", ".ogg"))
            ]
            top = [
                k
                for k in (
                    "Samurai Edge- Opening Theme",
                    "Samurai Edge - Closing Theme",
                    "bgm_ninja_challenge",
                )
                if k in m_files
            ]
            rest = sorted(k for k in m_files if k not in top)
            self.music_tracks = top + rest

    def set_filter(self, new_filter: str):
        """Define o filtro de categoria de imagens e reseta o índice."""
        if new_filter in FILTER_KEYS and self.current_filter != new_filter:
            self.current_filter = new_filter
            self.image_index = 0

    def open(self):
        self.is_open = True
        self._scan_assets()

    def close(self):
        self.is_open = False

    def handle_event(
        self, event: pygame.event.Event, ctrl_mgr=None
    ) -> str | None:
        """Processa eventos.

        Retorna "OPEN_OPENING_VIDEO", "OPEN_CREDITS_SLIDESHOW" ou "BACK".
        """
        if not self.is_open:
            return None

        # Botão de voltar (ESC, Círculo, Clique)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return "BACK"
        elif event.type == pygame.JOYBUTTONDOWN:
            if ctrl_mgr and ctrl_mgr.is_event_menu_cancel(event):
                self.close()
                return "BACK"
            elif event.button == 1:
                self.close()
                return "BACK"

        # Troca de abas (Q / E ou L1 / R1)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_q, pygame.K_1):
                self.current_tab = (self.current_tab - 1) % 3
            elif event.key in (pygame.K_e, pygame.K_2):
                self.current_tab = (self.current_tab + 1) % 3
        elif event.type == pygame.JOYBUTTONDOWN and event.button in (4, 5):
            delta = -1 if event.button == 4 else 1
            self.current_tab = (self.current_tab + delta) % 3

        # Navegação específica por aba
        if self.current_tab == TAB_IMAGES:
            items = self.get_current_items()
            num_items = len(items)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a) and num_items > 0:
                    self.image_index = (self.image_index - 1) % num_items
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and num_items > 0:
                    self.image_index = (self.image_index + 1) % num_items
                elif event.key in (pygame.K_UP, pygame.K_w):
                    # Alterna filtro de categoria anterior
                    cur_f_idx = FILTER_KEYS.index(self.current_filter) if self.current_filter in FILTER_KEYS else 0
                    self.set_filter(FILTER_KEYS[(cur_f_idx - 1) % len(FILTER_KEYS)])
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    # Alterna filtro de categoria seguinte
                    cur_f_idx = FILTER_KEYS.index(self.current_filter) if self.current_filter in FILTER_KEYS else 0
                    self.set_filter(FILTER_KEYS[(cur_f_idx + 1) % len(FILTER_KEYS)])
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Verificação de clique nas pílulas de filtro
                for f_rect, f_key in self.filter_rects:
                    if f_rect.collidepoint(event.pos):
                        self.set_filter(f_key)
                        return None

                if self.prev_btn_rect.collidepoint(event.pos) and num_items > 0:
                    self.image_index = (self.image_index - 1) % num_items
                elif self.next_btn_rect.collidepoint(event.pos) and num_items > 0:
                    self.image_index = (self.image_index + 1) % num_items

        elif self.current_tab == TAB_VIDEOS:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.video_index = 0
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.video_index = 1
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return (
                        "OPEN_OPENING_VIDEO"
                        if self.video_index == 0
                        else "OPEN_CREDITS_SLIDESHOW"
                    )
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, r in enumerate(self.video_cards_rects):
                    if r.collidepoint(event.pos):
                        return (
                            "OPEN_OPENING_VIDEO"
                            if idx == 0
                            else "OPEN_CREDITS_SLIDESHOW"
                        )

        elif self.current_tab == TAB_MUSIC:
            if event.type == pygame.KEYDOWN:
                if (
                    event.key in (pygame.K_UP, pygame.K_w)
                    and self.music_tracks
                ):
                    self.music_index = (self.music_index - 1) % len(
                        self.music_tracks
                    )
                elif (
                    event.key in (pygame.K_DOWN, pygame.K_s)
                    and self.music_tracks
                ):
                    self.music_index = (self.music_index + 1) % len(
                        self.music_tracks
                    )
                elif (
                    event.key in (pygame.K_LEFT, pygame.K_a)
                    and self.music_tracks
                ):
                    self._prev_track()
                elif (
                    event.key in (pygame.K_RIGHT, pygame.K_d)
                    and self.music_tracks
                ):
                    self._next_track()
                elif (
                    event.key in (pygame.K_RETURN, pygame.K_SPACE)
                    and self.music_tracks
                ):
                    self._play_track(self.music_tracks[self.music_index])
                elif event.key == pygame.K_k:
                    self.karaoke_enabled = not self.karaoke_enabled
                elif event.key == pygame.K_l:
                    self.is_looping = not self.is_looping
            elif event.type == pygame.JOYBUTTONDOWN:
                if ctrl_mgr and ctrl_mgr.is_event_menu_confirm(event) or event.button in (0, 2):
                    if self.music_tracks:
                        self._play_track(self.music_tracks[self.music_index])
                elif event.button == 3:  # Quadrado / X
                    self.karaoke_enabled = not self.karaoke_enabled
                elif event.button == 4:  # L1
                    self._prev_track()
                elif event.button == 5:  # R1
                    self._next_track()
                from src.input.controller_manager import get_dpad_motion_from_event
                d_dir = get_dpad_motion_from_event(event)
                if d_dir:
                    dx, dy = d_dir
                    if dy < 0 and self.music_tracks:
                        self.music_index = (self.music_index - 1) % len(self.music_tracks)
                    elif dy > 0 and self.music_tracks:
                        self.music_index = (self.music_index + 1) % len(self.music_tracks)
                    elif dx < 0 and self.music_tracks:
                        self._prev_track()
                    elif dx > 0 and self.music_tracks:
                        self._next_track()
            elif event.type == pygame.MOUSEWHEEL:
                if self.music_tracks:
                    self.music_index = max(0, min(len(self.music_tracks) - 1, self.music_index - event.y))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (4, 5):
                    delta = -1 if event.button == 4 else 1
                    if self.music_tracks:
                        self.music_index = max(0, min(len(self.music_tracks) - 1, self.music_index + delta))
                elif event.button == 1:
                    for item_r, idx in self.music_item_rects:
                        if item_r.collidepoint(event.pos):
                            if self.music_index == idx:
                                self._play_track(self.music_tracks[idx])
                            else:
                                self.music_index = idx
                                self._play_track(self.music_tracks[idx])
                            return None

                    if self.music_scroll_up_rect.collidepoint(event.pos) and self.music_tracks:
                        self.music_index = max(0, self.music_index - 1)
                    elif self.music_scroll_down_rect.collidepoint(event.pos) and self.music_tracks:
                        self.music_index = min(len(self.music_tracks) - 1, self.music_index + 1)
                    elif self.prev_track_btn_rect.collidepoint(event.pos):
                        self._prev_track()
                    elif self.play_btn_rect.collidepoint(event.pos):
                        if self.music_tracks:
                            self._play_track(self.music_tracks[self.music_index])
                    elif self.stop_btn_rect.collidepoint(event.pos):
                        self._stop_track()
                    elif self.next_track_btn_rect.collidepoint(event.pos):
                        self._next_track()
                    elif self.loop_btn_rect.collidepoint(event.pos):
                        self.is_looping = not self.is_looping
                    elif self.karaoke_btn_rect.collidepoint(event.pos):
                        self.karaoke_enabled = not self.karaoke_enabled

        # Cliques em abas e botão voltar
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, tab_r in enumerate(self.tab_rects):
                if tab_r.collidepoint(event.pos):
                    self.current_tab = idx
            if self.back_btn_rect.collidepoint(event.pos):
                self.close()
                return "BACK"

        return None

    def _prev_track(self):
        if not self.music_tracks:
            return
        self.music_index = (self.music_index - 1) % len(self.music_tracks)
        self._play_track(self.music_tracks[self.music_index])

    def _next_track(self):
        if not self.music_tracks:
            return
        self.music_index = (self.music_index + 1) % len(self.music_tracks)
        self._play_track(self.music_tracks[self.music_index])

    def _stop_track(self):
        from src.audio.sound_manager import SoundManager
        SoundManager.get_instance().stop_music()
        self.is_playing_music = False
        self.music_playback_time = 0.0

    def _play_track(self, track_key: str):
        from src.audio.sound_manager import SoundManager

        mgr = SoundManager.get_instance()
        if self.current_playing_track == track_key and self.is_playing_music:
            mgr.stop_music()
            self.is_playing_music = False
        else:
            loops = -1 if self.is_looping else 0
            mgr.play_music(track_key, fade_ms=500, loops=loops, force_restart=True)
            self.current_playing_track = track_key
            self.is_playing_music = True
            self.music_playback_time = 0.0

    def update(self, dt: float):
        if self.is_playing_music:
            self.music_playback_time += dt

    def render(self, surface: pygame.Surface):
        if not self.is_open:
            return

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        # 1. Overlay escuro e pergaminho central
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 6, 10, 215))
        surface.blit(overlay, (0, 0))

        panel_w, panel_h = 1060, 640
        panel_rect = pygame.Rect(
            cx - panel_w // 2, cy - panel_h // 2 - 10, panel_w, panel_h
        )

        paper = pm.make_paper(
            panel_w,
            panel_h,
            seed=77,
            ragged=(False, False, True, True),
            burn=0.25,
        )
        surface.blit(
            pm._soft_shadow(paper, blur=10, opacity=140),
            (panel_rect.x + 4, panel_rect.y + 6),
        )
        surface.blit(paper, (panel_rect.x, panel_rect.y))

        # 2. Cabeçalho com abas
        font_head = get_title_font(28)
        font_tab = get_title_font(20)
        font_text = get_text_font(16)
        font_sub = get_text_font(14)

        title_surf = font_head.render(t("gallery_title"), True, pm.INK)
        surface.blit(
            title_surf,
            (panel_rect.centerx - title_surf.get_width() // 2, panel_rect.y + 16),
        )

        # Três Abas estilizadas
        self.tab_rects = []
        tabs = [
            t("gallery_tab_images"),
            t("gallery_tab_videos"),
            t("gallery_tab_music"),
        ]
        tab_w = 200
        tab_gap = 14
        tabs_total_w = len(tabs) * tab_w + (len(tabs) - 1) * tab_gap
        tab_start_x = cx - tabs_total_w // 2
        tab_y = panel_rect.y + 60

        for i, tab_name in enumerate(tabs):
            tr = pygame.Rect(
                tab_start_x + i * (tab_w + tab_gap), tab_y, tab_w, 36
            )
            self.tab_rects.append(tr)
            is_cur = self.current_tab == i
            bg_col = (195, 140, 50) if is_cur else (226, 212, 185)
            border_col = pm.SEAL_RED if is_cur else (160, 145, 125)
            text_col = COLOR_WHITE if is_cur else pm.INK

            pygame.draw.rect(surface, bg_col, tr, border_radius=6)
            pygame.draw.rect(
                surface, border_col, tr, 2 if is_cur else 1, border_radius=6
            )

            ts = font_tab.render(tab_name, True, text_col)
            surface.blit(
                ts, (tr.centerx - ts.get_width() // 2, tr.centery - ts.get_height() // 2)
            )

        # 3. Conteúdo da aba selecionada
        content_rect = pygame.Rect(
            panel_rect.x + 30, tab_y + 50, panel_w - 60, panel_h - 180
        )

        if self.current_tab == TAB_IMAGES:
            self._render_images_tab(surface, content_rect, font_text, font_sub)
        elif self.current_tab == TAB_VIDEOS:
            self._render_videos_tab(
                surface, content_rect, font_tab, font_text, font_sub
            )
        elif self.current_tab == TAB_MUSIC:
            self._render_music_tab(
                surface, content_rect, font_tab, font_text, font_sub
            )

        # 4. Botão Voltar no rodapé
        self.back_btn_rect = pygame.Rect(
            cx - 140, panel_rect.bottom - 52, 280, 42
        )
        pygame.draw.rect(
            surface, pm.SEAL_RED, self.back_btn_rect, border_radius=6
        )
        pygame.draw.rect(
            surface, (212, 175, 55), self.back_btn_rect, 2, border_radius=6
        )
        ret_txt = t("settings_return_button")
        if "{icon:" in ret_txt:
            from src.ui.svg_icon_renderer import create_text_with_icons_surface
            b_surf = create_text_with_icons_surface(font_tab, ret_txt, COLOR_WHITE, icon_size=max(16, font_tab.get_height() - 2))
        else:
            b_surf = font_tab.render(ret_txt, True, COLOR_WHITE)
        surface.blit(b_surf, b_surf.get_rect(center=self.back_btn_rect.center))

    def _render_images_tab(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        font_text: pygame.font.Font,
        font_sub: pygame.font.Font,
    ):
        """Renderiza a visualização da imagem conceitual ou ending slide em arte pura."""
        # 1. Pílulas de Filtro de Categoria no Topo da Área de Imagem
        mouse_pos = pygame.mouse.get_pos()
        self.filter_rects = []
        filter_data = [
            (CAT_ALL, t("gallery_filter_all")),
            (CAT_CHARACTERS, t("gallery_filter_characters")),
            (CAT_ARENAS, t("gallery_filter_arenas")),
            (CAT_ENDING, t("gallery_filter_ending")),
        ]

        pill_w = 175
        pill_h = 28
        pill_gap = 12
        total_pills_w = len(filter_data) * pill_w + (len(filter_data) - 1) * pill_gap
        start_pill_x = rect.centerx - total_pills_w // 2
        pills_y = rect.y - 12

        for idx, (cat_key, cat_label) in enumerate(filter_data):
            pr = pygame.Rect(
                start_pill_x + idx * (pill_w + pill_gap), pills_y, pill_w, pill_h
            )
            self.filter_rects.append((pr, cat_key))
            is_active = self.current_filter == cat_key
            is_hover = pr.collidepoint(mouse_pos)

            if is_active:
                bg = (195, 140, 50)
                border = pm.SEAL_RED
                txt_c = COLOR_WHITE
                bw = 2
            elif is_hover:
                bg = (235, 222, 196)
                border = pm.SEAL_RED
                txt_c = pm.INK
                bw = 1
            else:
                bg = (226, 212, 185)
                border = (160, 145, 125)
                txt_c = pm.INK_SOFT
                bw = 1

            pygame.draw.rect(surface, bg, pr, border_radius=6)
            pygame.draw.rect(surface, border, pr, bw, border_radius=6)
            lbl_surf = font_sub.render(cat_label, True, txt_c)
            surface.blit(lbl_surf, lbl_surf.get_rect(center=pr.center))

        # 2. Itens da categoria selecionada
        items = self.get_current_items()
        if not items:
            msg = font_text.render("Nenhuma ilustração encontrada nesta categoria.", True, pm.INK_SOFT)
            surface.blit(msg, msg.get_rect(center=rect.center))
            return

        self.image_index = max(0, min(self.image_index, len(items) - 1))
        entry = items[self.image_index]
        img_cache_key = entry["path"]

        if img_cache_key not in self._image_cache:
            try:
                raw = pygame.image.load(img_cache_key)
                if pygame.display.get_surface():
                    raw = raw.convert()
                # Escalar proporcionalmente ao quadro mantendo aspect ratio
                max_w = rect.width - 180
                max_h = rect.height - 70
                scale = min(max_w / raw.get_width(), max_h / raw.get_height())
                nw = max(1, int(raw.get_width() * scale))
                nh = max(1, int(raw.get_height() * scale))
                scaled = pygame.transform.smoothscale(raw, (nw, nh))
                self._image_cache[img_cache_key] = scaled
            except Exception as e:
                print(f"[Gallery] Erro ao carregar {img_cache_key}: {e}")
                self._image_cache[img_cache_key] = None

        cur_surf = self._image_cache.get(img_cache_key)
        if cur_surf:
            img_r = cur_surf.get_rect(center=(rect.centerx, rect.centery + 10))
            # Moldura pergaminho Sumi-E em tons de madeira e dourado
            pygame.draw.rect(
                surface, (30, 24, 20), img_r.inflate(8, 8), border_radius=4
            )
            pygame.draw.rect(
                surface, (180, 140, 75), img_r.inflate(8, 8), 2, border_radius=4
            )
            surface.blit(cur_surf, img_r)

        # 3. Botões de Navegação Anterior / Próxima com Polígonos Geométricos Nítidos
        self.prev_btn_rect = pygame.Rect(rect.x + 16, rect.centery - 15, 48, 52)
        self.next_btn_rect = pygame.Rect(
            rect.right - 64, rect.centery - 15, 48, 52
        )

        prev_hover = self.prev_btn_rect.collidepoint(mouse_pos)
        next_hover = self.next_btn_rect.collidepoint(mouse_pos)

        # Botão Anterior (Triângulo para a Esquerda)
        pygame.draw.rect(surface, (235, 222, 196) if prev_hover else (226, 212, 185), self.prev_btn_rect, border_radius=6)
        pygame.draw.rect(surface, pm.SEAL_RED if prev_hover else (140, 125, 105), self.prev_btn_rect, 2 if prev_hover else 1, border_radius=6)
        tri_prev_c = pm.SEAL_RED if prev_hover else pm.INK
        p_prev = [
            (self.prev_btn_rect.centerx + 6, self.prev_btn_rect.centery - 10),
            (self.prev_btn_rect.centerx - 7, self.prev_btn_rect.centery),
            (self.prev_btn_rect.centerx + 6, self.prev_btn_rect.centery + 10),
        ]
        pygame.draw.polygon(surface, tri_prev_c, p_prev)

        # Botão Próximo (Triângulo para a Direita)
        pygame.draw.rect(surface, (235, 222, 196) if next_hover else (226, 212, 185), self.next_btn_rect, border_radius=6)
        pygame.draw.rect(surface, pm.SEAL_RED if next_hover else (140, 125, 105), self.next_btn_rect, 2 if next_hover else 1, border_radius=6)
        tri_next_c = pm.SEAL_RED if next_hover else pm.INK
        p_next = [
            (self.next_btn_rect.centerx - 6, self.next_btn_rect.centery - 10),
            (self.next_btn_rect.centerx + 7, self.next_btn_rect.centery),
            (self.next_btn_rect.centerx - 6, self.next_btn_rect.centery + 10),
        ]
        pygame.draw.polygon(surface, tri_next_c, p_next)

        # 4. Legenda e contador no rodapé da arte
        count_str = f"[{self.image_index + 1:02d} / {len(items):02d}]  ―  {entry['title']}"
        c_surf = font_text.render(count_str, True, pm.INK)
        surface.blit(
            c_surf, (rect.centerx - c_surf.get_width() // 2, rect.bottom - 16)
        )

    def _render_videos_tab(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        font_tab: pygame.font.Font,
        font_text: pygame.font.Font,
        font_sub: pygame.font.Font,
    ):
        """Renderiza cartões dos vídeos disponíveis."""
        self.video_cards_rects = []
        card_w = rect.width - 120
        card_h = 100
        start_y = rect.y + 40

        videos_data = [
            (
                t("gallery_video_opening_title"),
                t("gallery_video_opening_desc"),
                "Samurai_Edge_Opening_Final.mp4",
            ),
            (
                t("gallery_video_credits_title"),
                t("gallery_video_credits_desc"),
                "Samurai_Edge_Credits_Slideshow.mp4",
            ),
        ]

        for i, (v_title, v_desc, v_asset) in enumerate(videos_data):
            cr = pygame.Rect(
                rect.centerx - card_w // 2, start_y + i * (card_h + 30), card_w, card_h
            )
            self.video_cards_rects.append(cr)
            is_sel = self.video_index == i

            bg_col = (235, 222, 196) if is_sel else (226, 212, 185)
            border_col = pm.SEAL_RED if is_sel else (150, 135, 115)
            border_w = 2 if is_sel else 1

            pygame.draw.rect(surface, bg_col, cr, border_radius=8)
            pygame.draw.rect(
                surface, border_col, cr, border_w, border_radius=8
            )

            # Ícone play estilizado
            pygame.draw.circle(
                surface, pm.SEAL_RED, (cr.x + 45, cr.centery), 24
            )
            pygame.draw.polygon(
                surface,
                COLOR_WHITE,
                [
                    (cr.x + 40, cr.centery - 12),
                    (cr.x + 55, cr.centery),
                    (cr.x + 40, cr.centery + 12),
                ],
            )

            # Textos do cartão
            t_surf = font_tab.render(v_title, True, pm.INK)
            d_surf = font_sub.render(v_desc, True, pm.INK_SOFT)
            surface.blit(t_surf, (cr.x + 85, cr.y + 24))
            surface.blit(d_surf, (cr.x + 85, cr.y + 54))

    def _render_music_tab(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        font_tab: pygame.font.Font,
        font_text: pygame.font.Font,
        font_sub: pygame.font.Font,
    ):
        """Renderiza a lista completa do Jukebox e o reprodutor com transporte e Karaokê sincronizado."""
        if not self.music_tracks:
            return

        # 1. Painel Esquerdo: Lista de faixas (todas as 32 músicas com rolagem suave e botões)
        list_w = rect.width // 2 - 12
        list_x = rect.x
        list_y = rect.y + 10
        list_h = rect.height - 20
        list_rect = pygame.Rect(list_x, list_y, list_w, list_h)

        pygame.draw.rect(surface, (230, 218, 192), list_rect, border_radius=8)
        pygame.draw.rect(surface, (160, 145, 125), list_rect, 1, border_radius=8)

        # Cabeçalho da Lista
        h_txt = f"TRILHA SONORA [{self.music_index + 1:02d} / {len(self.music_tracks):02d}]"
        h_surf = font_sub.render(h_txt, True, pm.SEAL_RED)
        surface.blit(h_surf, (list_x + 14, list_y + 10))

        # Botões de rolagem Up e Down
        self.music_scroll_up_rect = pygame.Rect(list_x + list_w - 32, list_y + 8, 24, 20)
        self.music_scroll_down_rect = pygame.Rect(list_x + list_w - 32, list_y + list_h - 28, 24, 20)

        for btn_r, symb in ((self.music_scroll_up_rect, "▲"), (self.music_scroll_down_rect, "▼")):
            pygame.draw.rect(surface, (220, 206, 178), btn_r, border_radius=4)
            pygame.draw.rect(surface, (160, 140, 115), btn_r, 1, border_radius=4)
            s_surf = font_sub.render(symb, True, pm.INK)
            surface.blit(s_surf, s_surf.get_rect(center=btn_r.center))

        # Trilho de rolagem e Thumb indicador
        scroll_rail_y0 = self.music_scroll_up_rect.bottom + 4
        scroll_rail_y1 = self.music_scroll_down_rect.top - 4
        scroll_rail_h = max(20, scroll_rail_y1 - scroll_rail_y0)
        pygame.draw.line(surface, (180, 165, 145), (list_x + list_w - 20, scroll_rail_y0), (list_x + list_w - 20, scroll_rail_y1), 2)

        thumb_pct = self.music_index / max(1, len(self.music_tracks) - 1)
        thumb_y = scroll_rail_y0 + int((scroll_rail_h - 16) * thumb_pct)
        thumb_r = pygame.Rect(list_x + list_w - 24, thumb_y, 8, 16)
        pygame.draw.rect(surface, pm.SEAL_RED, thumb_r, border_radius=3)

        # 7 faixas visíveis por vez
        visible_count = 7
        start_idx = max(
            0,
            min(
                self.music_index - 3,
                len(self.music_tracks) - visible_count,
            ),
        )

        self.music_item_rects = []
        item_h = 36
        gap = 5
        items_start_y = list_y + 36

        for i in range(visible_count):
            idx = start_idx + i
            if idx >= len(self.music_tracks):
                break
            track_key = self.music_tracks[idx]
            item_r = pygame.Rect(list_x + 10, items_start_y + i * (item_h + gap), list_w - 48, item_h)
            self.music_item_rects.append((item_r, idx))

            is_sel = self.music_index == idx
            is_curr_play = (self.current_playing_track == track_key and self.is_playing_music)

            bg_col = (
                (238, 224, 192)
                if is_sel
                else ((222, 208, 180) if is_curr_play else (226, 212, 185))
            )
            border_col = (
                pm.SEAL_RED
                if is_sel
                else ((180, 130, 45) if is_curr_play else (160, 145, 125))
            )

            pygame.draw.rect(surface, bg_col, item_r, border_radius=6)
            pygame.draw.rect(surface, border_col, item_r, 2 if is_sel else 1, border_radius=6)

            title = FRIENDLY_NAMES.get(track_key, track_key.replace("_", " ").title())
            marker = "▶ " if is_curr_play else "  "
            t_col = pm.SEAL_RED if (is_sel or is_curr_play) else pm.INK
            max_char = 24 if track_key in KARAOKE_TRACKS else 28
            ts = font_sub.render(f"{marker}{idx + 1:02d}. {title[:max_char]}", True, t_col)
            surface.blit(ts, (item_r.x + 8, item_r.centery - ts.get_height() // 2))

            if track_key in KARAOKE_TRACKS:
                k_badge = font_sub.render("🎤", True, pm.SEAL_RED)
                surface.blit(k_badge, (item_r.right - 24, item_r.centery - k_badge.get_height() // 2))

        # 2. Painel Direito: Reprodutor Central com Karaokê e Transporte Completo
        player_x = rect.centerx + 6
        player_y = rect.y + 10
        player_w = rect.width // 2 - 10
        player_h = rect.height - 20
        player_r = pygame.Rect(player_x, player_y, player_w, player_h)

        pygame.draw.rect(surface, (235, 222, 196), player_r, border_radius=8)
        pygame.draw.rect(surface, (160, 135, 95), player_r, 1, border_radius=8)

        cur_track_key = (
            self.current_playing_track or self.music_tracks[self.music_index]
        )
        friendly = FRIENDLY_NAMES.get(
            cur_track_key, cur_track_key.replace("_", " ").title()
        )

        h_surf = font_sub.render(
            f"{t('gallery_music_now_playing')}: [ Faixa {self.music_index + 1:02d} de {len(self.music_tracks):02d} ]",
            True, pm.INK_SOFT
        )
        surface.blit(h_surf, (player_r.x + 20, player_r.y + 14))

        title_s = font_tab.render(friendly, True, pm.INK)
        if title_s.get_width() > player_w - 40:
            title_s = font_sub.render(friendly, True, pm.INK)
        surface.blit(title_s, (player_r.x + 20, player_r.y + 38))

        # Linha de Tempo / Duração
        time_y = player_r.y + 68
        mins = int(self.music_playback_time) // 60
        secs = int(self.music_playback_time) % 60
        t_surf = font_sub.render(f"⏱ {mins:02d}:{secs:02d}", True, pm.INK_SOFT)
        surface.blit(t_surf, (player_r.x + 20, time_y))

        bar_x = player_r.x + 24 + t_surf.get_width()
        bar_w = player_w - 44 - t_surf.get_width()
        bar_r = pygame.Rect(bar_x, time_y + 4, bar_w, 8)
        pygame.draw.rect(surface, (216, 202, 175), bar_r, border_radius=4)
        pygame.draw.rect(surface, (160, 140, 115), bar_r, 1, border_radius=4)

        if self.is_playing_music:
            loop_cycle = (self.music_playback_time % 180.0) / 180.0
            fill_w = max(4, int(bar_w * loop_cycle))
            pygame.draw.rect(surface, pm.SEAL_RED, (bar_x, time_y + 4, fill_w, 8), border_radius=4)

        # Botão Interativo de Karaokê
        is_karaoke_avail = cur_track_key in KARAOKE_TRACKS
        self.karaoke_btn_rect = pygame.Rect(player_r.x + 20, player_r.y + 92, player_w - 40, 32)
        if is_karaoke_avail:
            if self.karaoke_enabled:
                pygame.draw.rect(surface, pm.SEAL_RED, self.karaoke_btn_rect, border_radius=6)
                pygame.draw.rect(surface, (212, 175, 55), self.karaoke_btn_rect, 2, border_radius=6)
                k_txt = font_sub.render("🎤 MODO KARAOKÊ: ATIVADO (Sincronizado)", True, COLOR_WHITE)
            else:
                pygame.draw.rect(surface, (224, 210, 182), self.karaoke_btn_rect, border_radius=6)
                pygame.draw.rect(surface, (160, 140, 115), self.karaoke_btn_rect, 1, border_radius=6)
                k_txt = font_sub.render("🎤 ATIVAR MODO KARAOKÊ", True, pm.INK)
            surface.blit(k_txt, k_txt.get_rect(center=self.karaoke_btn_rect.center))
        else:
            pygame.draw.rect(surface, (226, 214, 188), self.karaoke_btn_rect, border_radius=6)
            pygame.draw.rect(surface, (170, 155, 130), self.karaoke_btn_rect, 1, border_radius=6)
            k_txt = font_sub.render("🎵 TEMA INSTRUMENTAL ORIGINAL BAKUMATSU", True, pm.INK_SOFT)
            surface.blit(k_txt, k_txt.get_rect(center=self.karaoke_btn_rect.center))

        # Área de Letra Sincronizada / Informações da Trilha
        display_box = pygame.Rect(player_r.x + 18, player_r.y + 132, player_w - 36, player_h - 192)
        pygame.draw.rect(surface, (228, 214, 186), display_box, border_radius=6)
        pygame.draw.rect(surface, (180, 160, 130), display_box, 1, border_radius=6)

        if is_karaoke_avail and self.karaoke_enabled:
            lyrics_table = OPENING_THEME_LYRICS if "Opening" in cur_track_key else (CLOSING_THEME_LYRICS if "Closing" in cur_track_key else [])
            active_lyric = None
            t_cur = self.music_playback_time
            for lyr in lyrics_table:
                if lyr["start"] <= t_cur <= lyr["end"] + 0.8:
                    active_lyric = lyr
                    break

            if active_lyric:
                # Tradução em inglês no topo (se houver)
                if "trans" in active_lyric:
                    tr_s = font_sub.render(f'"{active_lyric["trans"]}"', True, (130, 80, 45))
                    surface.blit(tr_s, (display_box.centerx - tr_s.get_width() // 2, display_box.centery - 24))

                # Letra cantada com varredura cyan (wipe progress)
                sung_text = active_lyric["sung"]
                dur = max(0.1, active_lyric["end"] - active_lyric["start"])
                prog = max(0.0, min(1.0, (t_cur - active_lyric["start"]) / dur))

                base_s = font_tab.render(sung_text, True, pm.INK)
                cyan_s = font_tab.render(sung_text, True, (0, 150, 220))
                bw, bh = base_s.get_size()
                bx = display_box.centerx - bw // 2
                by = display_box.centery + (4 if "trans" in active_lyric else -bh // 2)

                comp = base_s.copy()
                wipe_px = int(bw * prog)
                if wipe_px > 0:
                    comp.blit(cyan_s, (0, 0), area=pygame.Rect(0, 0, wipe_px, bh))
                surface.blit(comp, (bx, by))
            else:
                if self.is_playing_music:
                    pulse = abs(math.sin(self.music_playback_time * 2))
                    p_col = (int(160 + 40 * pulse), int(100 + 30 * pulse), 60)
                    msg = font_sub.render("♪ (Interlúdio Instrumental) ♪", True, p_col)
                    surface.blit(msg, msg.get_rect(center=display_box.center))
                else:
                    msg = font_sub.render("Pressione ▶ PLAY para iniciar a faixa com Karaokê", True, pm.INK_SOFT)
                    surface.blit(msg, msg.get_rect(center=display_box.center))
        else:
            lines = [
                "Trilha sonora orquestrada de Samurai Edge: Bakumatsu.",
                "Instrumentação original com Taiko, Shamisen, Shakuhachi,",
                "Koto, Biwa e ritmos marciais da era feudal.",
                "",
                f"Modo de Repetição: {'Repetição Contínua [Loop]' if self.is_looping else 'Tocar Uma Vez'}",
            ]
            for li, line in enumerate(lines):
                ls = font_sub.render(line, True, pm.INK_SOFT if li < 4 else pm.SEAL_RED)
                surface.blit(ls, (display_box.centerx - ls.get_width() // 2, display_box.y + 16 + li * 20))

        # 5 Botões de Transporte no Rodapé do Reprodutor
        cx_p = player_r.centerx
        btn_y = player_r.bottom - 48
        btn_h = 36

        self.prev_track_btn_rect = pygame.Rect(cx_p - 150, btn_y, 50, btn_h)
        self.play_btn_rect = pygame.Rect(cx_p - 90, btn_y, 70, btn_h)
        self.stop_btn_rect = pygame.Rect(cx_p - 10, btn_y, 50, btn_h)
        self.next_track_btn_rect = pygame.Rect(cx_p + 50, btn_y, 50, btn_h)
        self.loop_btn_rect = pygame.Rect(cx_p + 110, btn_y, 70, btn_h)

        # 1. Prev
        pygame.draw.rect(surface, (222, 208, 180), self.prev_track_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (160, 140, 115), self.prev_track_btn_rect, 1, border_radius=6)
        pr_s = font_sub.render("|<<", True, pm.INK)
        surface.blit(pr_s, pr_s.get_rect(center=self.prev_track_btn_rect.center))

        # 2. Play / Pause
        pygame.draw.rect(surface, pm.SEAL_RED, self.play_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (212, 175, 55), self.play_btn_rect, 2, border_radius=6)
        btn_txt = "❚❚ PAUSA" if self.is_playing_music else "▶ PLAY"
        p_surf = font_sub.render(btn_txt, True, COLOR_WHITE)
        surface.blit(p_surf, p_surf.get_rect(center=self.play_btn_rect.center))

        # 3. Stop
        pygame.draw.rect(surface, (222, 208, 180), self.stop_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (160, 140, 115), self.stop_btn_rect, 1, border_radius=6)
        st_s = font_sub.render("■ STOP", True, pm.INK)
        surface.blit(st_s, st_s.get_rect(center=self.stop_btn_rect.center))

        # 4. Next
        pygame.draw.rect(surface, (222, 208, 180), self.next_track_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (160, 140, 115), self.next_track_btn_rect, 1, border_radius=6)
        nx_s = font_sub.render(">>|", True, pm.INK)
        surface.blit(nx_s, nx_s.get_rect(center=self.next_track_btn_rect.center))

        # 5. Loop
        l_col = pm.SEAL_RED if self.is_looping else (222, 208, 180)
        l_txt_col = COLOR_WHITE if self.is_looping else pm.INK
        pygame.draw.rect(surface, l_col, self.loop_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (212, 175, 55) if self.is_looping else (160, 140, 115), self.loop_btn_rect, 1, border_radius=6)
        lp_s = font_sub.render("🔁 LOOP" if self.is_looping else "➡ 1X", True, l_txt_col)
        surface.blit(lp_s, lp_s.get_rect(center=self.loop_btn_rect.center))
