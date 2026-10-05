"""
Movimento secundário de tecido (6.5.5): mangas, caudas de faixa, cachecóis e capas balançam sem estado guardado.

O renderizador dos lutadores é sem estado (recebe só posição, estado e tempo), então o balanço sai de uma defasagem de
fase por segmento: cada pedaço da cadeia repete o movimento do anterior com atraso, arrasta para trás do movimento do
lutador e é empurrado pelo vento da arena (`particles.WIND_SOURCE`, ligado pelo `main.py`).
"""
import math

from src.effects import particles


def wind_at(x: float, y: float) -> tuple[float, float]:
    source = particles.WIND_SOURCE
    return source(x, y) if source is not None else (0.0, 0.0)


def chain_offsets(count: int, t: float, phase: float, trail: tuple[float, float], side: tuple[float, float],
                  amp: float = 0.02, freq: float = 2.4, lag: float = 0.55, wind: tuple[float, float] = (0.0, 0.0),
                  wind_gain: float = 0.035) -> list[tuple[float, float, float]]:
    """
    Deslocamentos (dx, dy, dz) de `count` segmentos pendurados, do mais perto ao mais longe da fixação.
    `trail` é o quanto a cadeia é arrastada (já na direção oposta ao movimento), `side` o vetor lateral do balanço,
    `amp` a amplitude do balanço em repouso e `wind` o vento (u/s).
    """
    out = []
    for i in range(count):
        k = (i + 1) / count
        wave = math.sin(t * freq - i * lag + phase)
        dx = trail[0] * k + side[0] * wave * amp * k + wind[0] * wind_gain * k
        dy = trail[1] * k + side[1] * wave * amp * k + wind[1] * wind_gain * k
        dz = -0.012 * i * k  # a ponta cai um pouco ao se afastar da fixação
        out.append((dx, dy, dz))
    return out
