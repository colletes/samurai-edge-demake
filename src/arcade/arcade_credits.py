"""
Entregável 8.1.3: Tela de Créditos com Slideshow de Imagens Promocionais e de Conceito.
Exibida ao concluir com sucesso o Modo Arcade (derrota do Chefe Final Oni Gashadokuro).
Apresenta transições suaves (crossfade), letterboxing cinematográfico, cartões de texto
localizados para Game Design/QA, Apoiadores e Agradecimento Especial.
"""
import os
import math
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE
from src.i18n import t
from src.ui.fonts import get_title_font, get_text_font
from src.ui.svg_icon_renderer import render_text_with_icons


# Lista ordenada de ilustrações e cartões dos créditos
SLIDE_CONFIG = [
    {
        "image": "assets/promotional/wide_cover.png",
        "header_key": "credits_title",
        "name_key": "credits_subtitle",
        "color": COLOR_GOLD,
    },
    {
        "image": "assets/concepts/kenshi_musashi_duel.jpg",
        "header_key": "credits_design_qa_role",
        "name_key": "credits_design_qa_name",
        "color": (255, 140, 100),
    },
    {
        "image": "assets/concepts/anne_murasaki_deck_duel.jpg",
        "header_key": "credits_supporters_role",
        "name_key": "credits_supporters_name",
        "color": (120, 220, 175),
    },
    {
        "image": "assets/concepts/saitou_julie_kyoto_duel.jpg",
        "header_key": "credits_special_thanks_role",
        "name_key": "credits_special_thanks_name",
        "color": (255, 185, 215),
    },
    {
        "image": "assets/concepts/okuni_joe_kabuki_duel.jpg",
        "header_key": "credits_tech_role",
        "name_key": "credits_tech_desc",
        "color": (150, 195, 255),
    },
    {
        "image": "assets/promotional/social_media_image.png",
        "header_key": "credits_thanks",
        "name_text": "Bakumatsu Noir • 2026",
        "color": COLOR_GOLD,
    },
]

_IMAGE_CACHE: dict[str, pygame.Surface] = {}


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

        # Vinheta cinematográfica (escurecimento suave das bordas para realce dos textos)
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Sombra nas extremidades superior e inferior
        pygame.draw.rect(vignette, (8, 6, 10, 190), (0, 0, SCREEN_WIDTH, 120))
        pygame.draw.rect(vignette, (8, 6, 10, 210), (0, SCREEN_HEIGHT - 160, SCREEN_WIDTH, 160))
        comp.blit(vignette, (0, 0))

        _IMAGE_CACHE[path] = comp
        return comp
    except Exception as e:
        print(f"[ArcadeCredits] Erro ao carregar imagem {path}: {e}")
        return None


class ArcadeCreditsScreen:
    """Tela de Slideshow e Créditos do Modo Arcade."""

    def __init__(self):
        self.active = False
        self.run = None
        self.rank = None
        self.high_scores = []
        self.current_slide = 0
        self.slide_timer = 0.0
        self.slide_duration = 5.0    # 5 segundos por slide
        self.fade_duration = 0.9     # 0.9s de transição suave entre slides
        self.total_time = 0.0

    def open(self, run, rank: int | None = None, high_scores: list = None):
        """Inicializa e abre a tela de créditos."""
        self.active = True
        self.run = run
        self.rank = rank
        self.high_scores = high_scores or []
        self.current_slide = 0
        self.slide_timer = 0.0
        self.total_time = 0.0

        # Pré-carregar imagens dos slides em cache
        for cfg in SLIDE_CONFIG:
            _get_scaled_slide_image(cfg["image"])

    def update(self, dt: float) -> str | None:
        if not self.active:
            return None

        self.slide_timer += dt
        self.total_time += dt

        if self.slide_timer >= self.slide_duration:
            self.slide_timer = 0.0
            self.current_slide += 1
            if self.current_slide >= len(SLIDE_CONFIG):
                self.active = False
                return "DONE"

        return None

    def handle_event(self, event: pygame.event.Event, ctrl_mgr=None) -> str | None:
        """
        Interação durante os créditos:
        - Confirmação (ENTER, ESPAÇO, Cruz, Quadrado): Avança para o próximo slide ou conclui.
        - Cancelar (ESC, Círculo): Pula os créditos imediatamente para a tela de recordes.
        """
        if not self.active:
            return None

        # Clique do mouse
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._advance_slide()

        # Teclado
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_e, pygame.K_j):
                return self._advance_slide()
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                return "DONE"

        # Gamepad
        elif event.type == pygame.JOYBUTTONDOWN:
            if ctrl_mgr is not None:
                if ctrl_mgr.is_event_menu_confirm(event) or event.button in (0, 2):
                    return self._advance_slide()
                elif ctrl_mgr.is_event_menu_cancel(event) or event.button == 1:
                    self.active = False
                    return "DONE"
            else:
                if event.button in (0, 2):
                    return self._advance_slide()
                elif event.button == 1:
                    self.active = False
                    return "DONE"

        return None

    def _advance_slide(self) -> str | None:
        """Avança manualmente para o próximo slide ao confirmar."""
        self.current_slide += 1
        self.slide_timer = 0.0
        if self.current_slide >= len(SLIDE_CONFIG):
            self.active = False
            return "DONE"
        return None

    def render(self, surface: pygame.Surface):
        """Renderiza a imagem atual, transição e textos dos créditos."""
        if not self.active:
            return

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        idx = min(self.current_slide, len(SLIDE_CONFIG) - 1)
        cfg = SLIDE_CONFIG[idx]
        cur_img = _get_scaled_slide_image(cfg["image"])

        # Desenhar imagem de fundo
        if cur_img:
            surface.blit(cur_img, (0, 0))
        else:
            surface.fill((16, 14, 18))

        # Transição de Fade-In no início do slide
        if self.slide_timer < self.fade_duration:
            alpha = int(255 * (1.0 - (self.slide_timer / self.fade_duration)))
            fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_overlay.fill((10, 8, 12, alpha))
            surface.blit(fade_overlay, (0, 0))

        # Transição de Fade-Out no término do slide
        time_left = self.slide_duration - self.slide_timer
        if time_left < self.fade_duration:
            alpha = int(255 * (1.0 - (time_left / self.fade_duration)))
            fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_overlay.fill((10, 8, 12, alpha))
            surface.blit(fade_overlay, (0, 0))

        # Painel laqueado translúcido para exibição do cartão de créditos
        panel_w = 680
        panel_h = 160
        panel_x = cx - panel_w // 2
        panel_y = SCREEN_HEIGHT - 210

        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((18, 16, 20, 215))
        pygame.draw.rect(panel_surf, cfg["color"], (0, 0, panel_w, panel_h), 2, border_radius=8)
        # Detalhe nos cantos
        pygame.draw.rect(panel_surf, (80, 75, 70), (4, 4, panel_w - 8, panel_h - 8), 1, border_radius=6)
        surface.blit(panel_surf, (panel_x, panel_y))

        # Textos do cartão
        font_header = get_title_font(26)
        font_name = get_title_font(34)

        header_text = t(cfg["header_key"]) if "header_key" in cfg else cfg.get("header_text", "")
        name_text = t(cfg["name_key"]) if "name_key" in cfg else cfg.get("name_text", "")

        # Sombra dos textos
        sh_head = font_header.render(header_text, True, (12, 10, 14))
        tx_head = font_header.render(header_text, True, cfg["color"])
        surface.blit(sh_head, (cx - tx_head.get_width() // 2 + 2, panel_y + 26))
        surface.blit(tx_head, (cx - tx_head.get_width() // 2, panel_y + 24))

        sh_name = font_name.render(name_text, True, (12, 10, 14))
        tx_name = font_name.render(name_text, True, COLOR_WHITE)
        surface.blit(sh_name, (cx - tx_name.get_width() // 2 + 2, panel_y + 78))
        surface.blit(tx_name, (cx - tx_name.get_width() // 2, panel_y + 76))

        # Indicador de pular créditos na barra inferior
        font_prompt = get_text_font(16)
        pulse = 0.70 + 0.30 * abs(math.sin(self.total_time * 3.5))
        prompt_alpha = int(255 * pulse)
        render_text_with_icons(
            surface, font_prompt, t("credits_skip_hint"),
            cx, SCREEN_HEIGHT - 26,
            text_color=(205, 205, 205), icon_size=18, alpha=prompt_alpha, shadow=True
        )
