"""
Escalonador de Exibição e Viewport Responsivo (Display Scaler).
Adapta a resolução canônica do jogo (1280x720) para qualquer tamanho de tela mobile ou desktop,
preservando a proporção exata (Letterbox/Pillarbox) e convertendo coordenadas de toque/mouse.
"""
import pygame

class DisplayScaler:
    def __init__(self, virtual_width: int = 1280, virtual_height: int = 720):
        self.virtual_width = virtual_width
        self.virtual_height = virtual_height
        self.virtual_aspect = virtual_width / virtual_height

        self.window_width = virtual_width
        self.window_height = virtual_height

        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.scaled_rect = pygame.Rect(0, 0, virtual_width, virtual_height)

        # Superfície canônica de renderização interna
        self.canvas = pygame.Surface((virtual_width, virtual_height))

    def update_window_size(self, window_width: int, window_height: int):
        """Atualiza a geometria do viewport após redimensionamento ou rotação da tela."""
        self.window_width = max(1, window_width)
        self.window_height = max(1, window_height)

        window_aspect = self.window_width / self.window_height

        if window_aspect > self.virtual_aspect:
            # Tela mais larga (Pillarbox: barras pretas laterais)
            self.scale = self.window_height / self.virtual_height
            scaled_w = int(self.virtual_width * self.scale)
            scaled_h = self.window_height
            self.offset_x = (self.window_width - scaled_w) // 2
            self.offset_y = 0
        else:
            # Tela mais alta (Letterbox: barras pretas superior/inferior)
            self.scale = self.window_width / self.virtual_width
            scaled_w = self.window_width
            scaled_h = int(self.virtual_height * self.scale)
            self.offset_x = 0
            self.offset_y = (self.window_height - scaled_h) // 2

        self.scaled_rect = pygame.Rect(self.offset_x, self.offset_y, scaled_w, scaled_h)

    def screen_to_virtual(self, screen_x: float, screen_y: float) -> tuple[float, float]:
        """Converte coordenadas físicas de clique ou toque na tela para o espaço virtual 1280x720."""
        vx = (screen_x - self.offset_x) / self.scale
        vy = (screen_y - self.offset_y) / self.scale
        return vx, vy

    def normalized_finger_to_virtual(self, finger_x: float, finger_y: float) -> tuple[float, float]:
        """Converte coordenadas normalizadas do Pygame (0.0 a 1.0) para coordenadas virtuais."""
        screen_x = finger_x * self.window_width
        screen_y = finger_y * self.window_height
        return self.screen_to_virtual(screen_x, screen_y)

    def render_to_screen(self, screen: pygame.Surface):
        """Redimensiona e renderiza a tela virtual na janela/display real."""
        if self.scaled_rect.size == (self.virtual_width, self.virtual_height):
            screen.blit(self.canvas, (self.offset_x, self.offset_y))
        else:
            scaled_surface = pygame.transform.smoothscale(self.canvas, self.scaled_rect.size)
            screen.fill((10, 12, 10)) # Barras de letterbox escuras
            screen.blit(scaled_surface, self.scaled_rect.topleft)
