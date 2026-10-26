"""
Escalonador de Exibição e Viewport Responsivo (Display Scaler).
Adapta a resolução canônica do jogo (1280x720) para qualquer tamanho de tela mobile ou desktop,
preservando a proporção exata (Letterbox/Pillarbox) e convertendo coordenadas de toque/mouse.
"""
import pygame

class DisplayScaler:
    def __init__(self, virtual_width: int = 1280, virtual_height: int = 720, scale_mode: str = "sharp"):
        self.virtual_width = virtual_width
        self.virtual_height = virtual_height
        self.virtual_aspect = virtual_width / virtual_height

        self.window_width = virtual_width
        self.window_height = virtual_height
        self.scale_mode = scale_mode

        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.scaled_rect = pygame.Rect(0, 0, virtual_width, virtual_height)

        # Superfície canônica de renderização interna
        self.canvas = pygame.Surface((virtual_width, virtual_height))
        # Buffer de escala pré-alocado (Zero-alloc por frame para máxima fluidez no iPhone/Mac)
        self._scaled_buffer = None

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
        # Pré-aloca o buffer de escala quando o tamanho muda
        if self.scaled_rect.size != (self.virtual_width, self.virtual_height):
            self._scaled_buffer = pygame.Surface(self.scaled_rect.size)
        else:
            self._scaled_buffer = None

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

    def virtual_to_screen(self, vx: float, vy: float) -> tuple[float, float]:
        """Converte coordenadas virtuais 1280x720 para coordenadas físicas na janela do dispositivo."""
        sx = vx * self.scale + self.offset_x
        sy = vy * self.scale + self.offset_y
        return sx, sy

    def is_point_inside(self, screen_x: float, screen_y: float) -> bool:
        """Verifica se um ponto físico na tela está dentro da área útil 16:9 (fora das barras pretas)."""
        return self.scaled_rect.collidepoint(screen_x, screen_y)

    def render_to_screen(self, screen: pygame.Surface):
        """Redimensiona e renderiza a tela virtual na janela/display real mantendo barras pretas puras."""
        # Se a janela possuir letterbox/pillarbox ou dimensões excedentes, preenche com preto puro
        if self.offset_x > 0 or self.offset_y > 0 or screen.get_size() != self.scaled_rect.size:
            screen.fill((0, 0, 0))

        if self.scaled_rect.size == (self.virtual_width, self.virtual_height):
            screen.blit(self.canvas, (self.offset_x, self.offset_y))
        else:
            # Garante que o buffer pré-alocado corresponda ao tamanho do viewport atual
            if self._scaled_buffer is None or self._scaled_buffer.get_size() != self.scaled_rect.size:
                self._scaled_buffer = pygame.Surface(self.scaled_rect.size)

            if self.scale_mode == "sharp":
                # Renderização Pixel-Crisp Ultra-Nítida (estilo PS1 / sem borrão bilinear)
                pygame.transform.scale(self.canvas, self.scaled_rect.size, self._scaled_buffer)
            else:
                # Interpolação bilinear suave
                pygame.transform.smoothscale(self.canvas, self.scaled_rect.size, self._scaled_buffer)

            screen.blit(self._scaled_buffer, self.scaled_rect.topleft)
