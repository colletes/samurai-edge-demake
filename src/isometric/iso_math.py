"""
Funções matemáticas para projeção isométrica 2:1 e conversão de coordenadas.
"""
import math
from src.config import HALF_TILE_W, HALF_TILE_H

# Escala vertical em pixels por unidade Z no mundo
PIXELS_PER_Z = 32.0

def world_to_iso(wx: float, wy: float, wz: float = 0.0) -> tuple[float, float]:
    """
    Converte coordenadas contínuas de mundo (wx, wy, wz)
    para coordenadas de tela na projeção isométrica 2:1.
    """
    sx = (wx - wy) * HALF_TILE_W
    sy = (wx + wy) * HALF_TILE_H - (wz * PIXELS_PER_Z)
    return sx, sy

def iso_to_world(sx: float, sy: float) -> tuple[float, float]:
    """
    Converte coordenadas de tela relativas à câmera
    de volta para coordenadas de mundo (plano z=0).
    """
    wx = (sx / HALF_TILE_W + sy / HALF_TILE_H) / 2.0
    wy = (sy / HALF_TILE_H - sx / HALF_TILE_W) / 2.0
    return wx, wy

def world_distance(wx1: float, wy1: float, wx2: float, wy2: float) -> float:
    """Calcula a distância euclidiana entre dois pontos no espaço de mundo."""
    return math.hypot(wx2 - wx1, wy2 - wy1)

def input_to_world_direction(dx: float, dy: float) -> tuple[float, float]:
    """
    Converte direções do teclado (dx: -1 a 1 na tela, dy: -1 a 1 na tela)
    em vetores de movimento no espaço de mundo isométrico.
    Garante que 'W' mova o personagem para o topo da tela e 'D' para a direita.
    """
    if dx == 0 and dy == 0:
        return 0.0, 0.0

    # Conversão de tela (dx, dy) para mundo (dwx, dwy)
    # Direita na tela: (+1, -1) no mundo
    # Cima na tela:    (-1, -1) no mundo
    dwx = dx + dy
    dwy = dy - dx

    # Normalizar para velocidade uniforme independente de diagonais
    length = math.hypot(dwx, dwy)
    if length > 0.0001:
        dwx /= length
        dwy /= length

    return dwx, dwy
