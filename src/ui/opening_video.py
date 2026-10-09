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
        self.is_finished = False
        self.video = None
        self.font = get_text_font(18)
        self.prompt_timer = 0.0

        if not video_path:
            video_path = get_asset_path("assets/Opening Videos/Samurai_Edge_Opening_Final.mp4")
        self.video_path = video_path

        # Em ambiente headless ou se arquivo não existir, encerrar de imediato
        if os.environ.get("SDL_VIDEODRIVER") == "dummy" or not os.path.exists(self.video_path):
            self.is_finished = True
            return

        try:
            from pyvidplayer2 import Video
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

        should_skip = False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                should_skip = True

        elif event.type == pygame.JOYBUTTONDOWN:
            from src.input.controller_manager import get_controller_manager
            ctrl_mgr = get_controller_manager()
            # Botao Start / Options / Menu
            if (ctrl_mgr.is_event_menu_pause(event, 0) or
                ctrl_mgr.is_event_menu_pause(event, 1) or
                event.button in (6, 7)):
                should_skip = True
            # Botão Confirmar (Cruz / Quadrado) ou Cancelar (Círculo)
            elif (ctrl_mgr.is_event_menu_confirm(event) or
                  ctrl_mgr.is_event_menu_cancel(event) or
                  event.button in (0, 1, 2)):
                should_skip = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            should_skip = True

        elif event.type == pygame.FINGERDOWN:
            should_skip = True

        if should_skip:
            self.stop()
            return True

        return False

    def update(self, dt: float):
        """Atualiza estado e temporizadores do player de video."""
        if self.is_finished:
            return

        self.prompt_timer += dt

        if not self.video or not self.video.active:
            self.stop()
            return

        # So encerra naturalmente se todos os quadros do video foram completamente consumidos
        frame_idx = getattr(self.video, "frame", 0)
        total_frames = getattr(self.video, "frame_count", 0)
        if total_frames > 0 and frame_idx >= total_frames - 2:
            self.stop()

    def render(self, screen: pygame.Surface):
        """Renderiza o quadro atual do video e o indicador discreto de pulo com SVG buttons."""
        if self.is_finished:
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

        # Indicador sutil de como pular com SVG dos botoes PlayStation
        try:
            from src.ui.svg_icon_renderer import get_button_icon_surface
            
            alpha = int(140 + 60 * math.sin(self.prompt_timer * 3.0))
            
            # Obter icones dos botoes
            icon_options_surf = get_button_icon_surface("options", 20, 20)
            icon_cross_surf = get_button_icon_surface("cross", 20, 20)
            icon_options_surf.set_alpha(alpha)
            icon_cross_surf.set_alpha(alpha)
            
            # Texto de prompt
            prompt_text = t("skip_video")
            prompt_surf = self.font.render(prompt_text, True, COLOR_WHITE)
            prompt_surf.set_alpha(alpha)
            
            # Calcular dimensoes do box
            total_width = icon_options_surf.get_width() + 4 + 16 + 4 + icon_cross_surf.get_width() + 4 + prompt_surf.get_width() + 12
            total_height = max(20, prompt_surf.get_height()) + 8
            
            padding = 8
            margin = 32
            bg_rect = pygame.Rect(
                SCREEN_WIDTH - total_width - padding * 2 - margin,
                SCREEN_HEIGHT - total_height - padding * 2 - margin,
                total_width + padding * 2,
                total_height + padding * 2
            )
            
            # Desenhar fundo escuro
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, int(alpha * 0.45)))
            screen.blit(bg_surf, bg_rect.topleft)
            
            # Desenhar conteudo: [START] / [Cross] Pular
            x_offset = bg_rect.x + padding + 4
            y_center = bg_rect.y + padding + (total_height // 2)
            
            # START icon
            screen.blit(icon_options_surf, (x_offset, y_center - 10))
            x_offset += icon_options_surf.get_width() + 4
            
            # Separador " / "
            sep_surf = self.font.render("/", True, COLOR_WHITE)
            sep_surf.set_alpha(alpha)
            screen.blit(sep_surf, (x_offset, y_center - sep_surf.get_height() // 2))
            x_offset += 16
            
            # Cross icon
            screen.blit(icon_cross_surf, (x_offset, y_center - 10))
            x_offset += icon_cross_surf.get_width() + 4
            
            # Texto " Pular"
            screen.blit(prompt_surf, (x_offset, y_center - prompt_surf.get_height() // 2))
        
        except ImportError:
            # Fallback para texto simples se SVG nao disponivel
            alpha = int(140 + 60 * math.sin(self.prompt_timer * 3.0))
            prompt_text = f"[START / Cross] {t('skip_video')}"
            prompt_surf = self.font.render(prompt_text, True, COLOR_WHITE)
            prompt_surf.set_alpha(alpha)

            padding = 8
            margin = 32
            bg_rect = pygame.Rect(
                SCREEN_WIDTH - prompt_surf.get_width() - padding * 2 - margin,
                SCREEN_HEIGHT - prompt_surf.get_height() - padding * 2 - margin,
                prompt_surf.get_width() + padding * 2,
                prompt_surf.get_height() + padding * 2
            )
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, int(alpha * 0.45)))
            screen.blit(bg_surf, bg_rect.topleft)
            screen.blit(prompt_surf, (bg_rect.x + padding, bg_rect.y + padding))

    def stop(self):
        """Finaliza e fecha o leitor de video liberando recursos."""
        self.is_finished = True
        if self.video:
            try:
                self.video.close()
            except Exception:
                pass
            self.video = None
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def close(self):
        self.stop()