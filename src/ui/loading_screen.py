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

    def draw_enso_symbol(self, cx: int, cy: int, radius: int, anim_time: float):
        """Desenha o círculo zen Ensō com caligrafia em nanquim e carimbo vermelho tradicional."""
        num_points = 32
        points = []
        pulse = 0.85 + 0.15 * math.sin(anim_time * 3.0)
        col = (int(175 * pulse), int(145 * pulse), int(75 * pulse))

        for i in range(num_points):
            angle = (i / num_points) * math.pi * 2
            # Variação orgânica simulando cerdas de pincel
            r_offset = math.sin(angle * 4.0 + anim_time * 2.0) * 2.5
            px = cx + int((radius + r_offset) * math.cos(angle))
            py = cy + int((radius + r_offset) * math.sin(angle))
            points.append((px, py))

        if len(points) > 2:
            pygame.draw.polygon(self.screen, col, points, 2)

        # Selo tradicional Hanko vermelho no canto do círculo
        seal_x = cx + radius - 6
        seal_y = cy + radius - 14
        pygame.draw.rect(self.screen, (185, 35, 35), (seal_x, seal_y, 16, 16), border_radius=2)
        pygame.draw.rect(self.screen, (220, 70, 70), (seal_x + 3, seal_y + 3, 10, 10), 1)

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

        # 3. Ensō e Título
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2 - 40

        self.draw_enso_symbol(center_x, center_y - 20, 68, self.anim_time)

        font_title = get_title_font(44)
        font_sub = get_text_font(18)
        font_status = get_text_font(16)
        font_pct = get_title_font(20)

        # Sombra e Título Principal
        title_text = "SAMURAI EDGE"
        shadow_surf = font_title.render(title_text, True, (0, 0, 0))
        title_surf = font_title.render(title_text, True, COLOR_GOLD)
        t_rect = title_surf.get_rect(center=(center_x, center_y - 20))
        self.screen.blit(shadow_surf, (t_rect.x + 3, t_rect.y + 3))
        self.screen.blit(title_surf, t_rect)

        # Subtítulo
        sub_text = "B A K U M A T S U   S L I C E"
        sub_surf = font_sub.render(sub_text, True, (190, 180, 165))
        sub_rect = sub_surf.get_rect(center=(center_x, center_y + 32))
        self.screen.blit(sub_surf, sub_rect)

        # Divisor sutil
        div_w = 260
        div_y = center_y + 54
        pygame.draw.line(self.screen, (75, 65, 50), (center_x - div_w // 2, div_y), (center_x + div_w // 2, div_y), 1)
        pygame.draw.circle(self.screen, COLOR_GOLD, (center_x, div_y), 3)

        # 4. Barra de Progresso
        bar_w = 540
        bar_h = 16
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        bar_y = center_y + 110

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
        pct_surf = font_pct.render(pct_text, True, COLOR_GOLD)
        pct_rect = pct_surf.get_rect(midleft=(bg_rect.right + 16, bg_rect.centery))
        self.screen.blit(pct_surf, pct_rect)

        # 6. Mensagem de Status
        pulse_dots = "." * (int(self.anim_time * 3.5) % 4)
        status_text = f"[ CARREGANDO ]  {self.message}{pulse_dots}"
        stat_surf = font_status.render(status_text, True, (200, 195, 185))
        stat_rect = stat_surf.get_rect(center=(center_x, bar_y + 36))
        self.screen.blit(stat_surf, stat_rect)

        if pygame.display.get_surface() is not None:
            pygame.display.flip()
