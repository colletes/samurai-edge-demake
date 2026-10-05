"""
Gerenciador de câmera isométrica com suporte a suavização (lerp) e Screen Shake.
"""
import math
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.isometric.iso_math import world_to_iso, iso_depth

class Camera:
    def __init__(self, target_wx: float = 11.0, target_wy: float = 11.0):
        # Posição central no mundo que a câmera está olhando
        self.wx = target_wx
        self.wy = target_wy

        # Offset na tela
        self.screen_x = SCREEN_WIDTH // 2
        self.screen_y = SCREEN_HEIGHT // 2

        # Sistema de Screen Shake (tremor na tela)
        self.shake_intensity = 0.0
        self.shake_decay = 0.90
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

        # Fator de zoom dramático (Fase 5.1: Clash de Espadas). 1.0 = sem zoom.
        self.zoom = 1.0

        # Altura do piso sob o foco (ex.: tabuleiro da ponte), onde as sombras dos lutadores são desenhadas
        self.ground_z = 0.0
        # Azimute (radianos): giro do mundo em torno do alvo da câmera. 0.0 = vista isométrica clássica.
        self.azimuth = 0.0
        # Relevo visual do piso (arenas com telhados inclinados): altura extra somada a todo ponto desenhado
        self.height_fn = None

    def set_azimuth(self, azimuth: float):
        """Define o azimute normalizado em (-pi, pi]."""
        self.azimuth = math.atan2(math.sin(azimuth), math.cos(azimuth))

    def rotate(self, delta: float):
        """Gira a câmera por delta radianos a partir do azimute atual."""
        self.set_azimuth(self.azimuth + delta)

    def depth(self, wx: float, wy: float) -> float:
        """Profundidade na tela (maior = mais próximo) para ordenação de renderização com o azimute atual."""
        return iso_depth(wx, wy, self.azimuth)

    def add_shake(self, intensity: float):
        """Adiciona intensidade de tremor na tela (ex: golpes pesados, clash ou morte)."""
        self.shake_intensity = max(self.shake_intensity, intensity)

    def update(self, target_wx: float, target_wy: float, dt: float):
        """Atualiza a posição da câmera com suavização (lerp) em direção ao alvo."""
        lerp_speed = 6.0 * dt
        self.wx += (target_wx - self.wx) * min(lerp_speed, 1.0)
        self.wy += (target_wy - self.wy) * min(lerp_speed, 1.0)

        # Atualizar tremor de tela
        if self.shake_intensity > 0.5:
            self.shake_offset_x = (random.random() * 2.0 - 1.0) * self.shake_intensity
            self.shake_offset_y = (random.random() * 2.0 - 1.0) * self.shake_intensity
            self.shake_intensity *= self.shake_decay
        else:
            self.shake_intensity = 0.0
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0

    def apply(self, wx: float, wy: float, wz: float = 0.0) -> tuple[int, int]:
        """
        Converte coordenadas de mundo para as coordenadas finais de renderização
        na janela, considerando a posição da câmera e o screen shake.
        """
        if self.height_fn is not None:
            wz += self.height_fn(wx, wy)
        iso_x, iso_y = world_to_iso(wx - self.wx, wy - self.wy, wz, self.azimuth)

        dx = iso_x * self.zoom
        dy = iso_y * self.zoom

        final_x = int(dx + self.screen_x + self.shake_offset_x)
        final_y = int(dy + self.screen_y + self.shake_offset_y)
        return final_x, final_y
