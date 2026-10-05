"""
Tela de Carregamento Estilizada em Sumi-E (Loading Screen).
Fornece feedback visual imediato e responsivo durante a inicialização do jogo
e pré-carregamento de assets pesados (fontes, retratos dos 12 guerreiros, arenas e configurações).
"""
import os
import math
import random
import time
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_RED_AURA, get_asset_path
)
from src.ui.fonts import get_title_font, get_text_font
from src.ui.font_manager import render_text_fx

class LoadingScreen:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.progress = 0.0
        self.target_progress = 0.0
        self.message = "Iniciando motor e carregando assets..."
        self.anim_time = 0.0
        self.clock = pygame.time.Clock()

        # Carregar imagem de fundo conceitual Sumi-E escurecida se existir
        self.bg_surf = None
        bg_path = get_asset_path("assets/concepts/sumie_title_logo_concept.jpg")
        if os.path.exists(bg_path):
            try:
                try:
                    raw_img = pygame.image.load(bg_path).convert()
                except Exception:
                    raw_img = pygame.image.load(bg_path)
                scaled = pygame.transform.smoothscale(raw_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                # Aplicar vinheta escura para contraste do carregador
                vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                vignette.fill((10, 10, 14, 160))
                scaled.blit(vignette, (0, 0))
                self.bg_surf = scaled
            except Exception:
                self.bg_surf = None

        # Partículas de brasa / cinza de nanquim flutuantes
        self.particles = []
        for _ in range(25):
            self.particles.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(0, SCREEN_HEIGHT),
                "speed_x": random.uniform(-0.4, 0.4),
                "speed_y": random.uniform(-0.8, -0.2),
                "size": random.uniform(1.5, 3.0),
                "alpha": random.randint(70, 180)
            })

    _footer_h = 190

    def _get_footer_shade(self) -> pygame.Surface:
        """Gradiente vertical escuro (transparente -> opaco) atrás da barra de progresso."""
        shade = getattr(self, "_footer_shade", None)
        if shade is None:
            shade = pygame.Surface((SCREEN_WIDTH, self._footer_h), pygame.SRCALPHA)
            for y in range(self._footer_h):
                a = int(215 * (y / (self._footer_h - 1)) ** 0.8)
                pygame.draw.line(shade, (8, 7, 10, a), (0, y), (SCREEN_WIDTH, y))
            self._footer_shade = shade
        return shade

    def update(self, progress: float, message: str, delay_ms: int = 50):
        """
        Atualiza o progresso (0.0 a 1.0) e a mensagem de status.
        Atualiza a janela imediatamente e processa a fila de eventos do SO para evitar travamento.
        """
        self.target_progress = max(0.0, min(1.0, progress))
        self.message = message

        # Interpolação suave em pequenas etapas para animação fluida
        steps = 4 if delay_ms > 0 else 1
        step_dt = (delay_ms / 1000.0) / steps if steps > 0 else 0.016

        for _ in range(steps):
            self.anim_time += step_dt
            self.progress += (self.target_progress - self.progress) * 0.45

            # Atualizar partículas
            for p in self.particles:
                p["x"] += p["speed_x"]
                p["y"] += p["speed_y"]
                if p["y"] < 0:
                    p["y"] = SCREEN_HEIGHT + random.uniform(0, 20)
                    p["x"] = random.uniform(0, SCREEN_WIDTH)

            self.render()
            pygame.event.pump()
            if delay_ms > 0:
                pygame.time.delay(int(delay_ms / steps))

        # Garantir valor exato ao final do passo
        self.progress = self.target_progress
        self.render()
        pygame.event.pump()

    def render(self):
        """Renderiza um frame da tela de carregamento."""
        # 1. Fundo
        if self.bg_surf:
            self.screen.blit(self.bg_surf, (0, 0))
        else:
            self.screen.fill((13, 12, 16))

        # 2. Partículas sutis de cinzas / nanquim
        for p in self.particles:
            alpha = p["alpha"]
            part_surf = pygame.Surface((int(p["size"] * 2), int(p["size"] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(part_surf, (225, 200, 140, alpha), (int(p["size"]), int(p["size"])), int(p["size"]))
            self.screen.blit(part_surf, (int(p["x"]), int(p["y"])))

        # 3. Painel inferior translúcido: o título já vem impresso na arte de fundo,
        # então apenas a barra e o status ficam sobre um gradiente escuro legível.
        center_x = SCREEN_WIDTH // 2
        self.screen.blit(self._get_footer_shade(), (0, SCREEN_HEIGHT - self._footer_h))

        font_status = get_text_font(16)
        font_pct = get_title_font(20)

        # 4. Barra de Progresso
        bar_w = 540
        bar_h = 16
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        bar_y = SCREEN_HEIGHT - 112

        # Calha de fundo da barra
        bg_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        pygame.draw.rect(self.screen, (20, 18, 22), bg_rect, border_radius=4)

        # Preenchimento em gradiente (Vermelho Carmim a Dourado Quente)
        fill_w = max(4, int(bar_w * self.progress))
        if fill_w > 4:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
            # Desenha barra com cantos arredondados
            fill_surf = pygame.Surface((fill_w, bar_h), pygame.SRCALPHA)
            for x_i in range(fill_w):
                ratio = x_i / float(bar_w)
                # Interpolação de cor: Carmim -> Laranja -> Dourado
                r = int(215 + 40 * ratio)
                g = int(50 + 155 * ratio)
                b = int(45 + 25 * ratio)
                pygame.draw.line(fill_surf, (r, g, b), (x_i, 0), (x_i, bar_h))

            # Brilho sutil no topo do preenchimento
            pygame.draw.line(fill_surf, (255, 255, 230, 140), (0, 1), (fill_w, 1))
            self.screen.blit(fill_surf, (bar_x, bar_y))

            # Brilho de ponta na frente da barra
            glint_x = bar_x + fill_w
            glint_pulse = 0.7 + 0.3 * math.sin(self.anim_time * 8.0)
            pygame.draw.circle(self.screen, (255, 245, 180), (glint_x, bar_y + bar_h // 2), int(5 * glint_pulse))

        # Moldura externa laqueada
        border_col = (145, 120, 70)
        pygame.draw.rect(self.screen, border_col, bg_rect, 1, border_radius=4)

        # Cantoneiras ornamentais nos 4 cantos
        c_sz = 6
        corners = [
            (bg_rect.left, bg_rect.top),
            (bg_rect.right - c_sz, bg_rect.top),
            (bg_rect.left, bg_rect.bottom - c_sz),
            (bg_rect.right - c_sz, bg_rect.bottom - c_sz)
        ]
        for cx_i, cy_i in corners:
            pygame.draw.rect(self.screen, COLOR_GOLD, (cx_i, cy_i, c_sz, c_sz), 1)

        # 5. Indicador de Porcentagem
        pct_text = f"{int(self.progress * 100)}%"
        pct_surf = render_text_fx(font_pct, pct_text, COLOR_GOLD, outline=True, outline_color=(10, 8, 6), outline_width=1,
                                  shadow=True, shadow_offset=(2, 2))
        pct_rect = pct_surf.get_rect(midleft=(bg_rect.right + 12, bg_rect.centery))
        self.screen.blit(pct_surf, pct_rect)

        # 6. Mensagem de Status (sombra 2px + contorno 1px, mesmo padrão do FontManager).
        # Os pontos animados são desenhados à parte para o texto não "tremer" ao mudar de largura.
        pulse_dots = "." * (int(self.anim_time * 3.5) % 4)
        status_text = f"[ CARREGANDO ]  {self.message}"
        fx = dict(outline=True, outline_color=(10, 8, 6), outline_width=1, shadow=True, shadow_offset=(2, 2))
        stat_surf = render_text_fx(font_status, status_text, (232, 222, 205), **fx)
        stat_rect = stat_surf.get_rect(midtop=(center_x, bar_y + 26))
        self.screen.blit(stat_surf, stat_rect)
        if pulse_dots:
            dots_surf = render_text_fx(font_status, pulse_dots, (232, 222, 205), **fx)
            self.screen.blit(dots_surf, dots_surf.get_rect(midleft=(stat_rect.right - 2, stat_rect.centery)))

        if pygame.display.get_surface() is not None:
            pygame.display.flip()
