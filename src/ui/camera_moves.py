"""Funções de easing compartilhadas pelas câmeras cinematográficas (introdução 7.1, nocaute 7.2 e vitória 7.4)."""


def smooth(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def ease_out(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3


def lerp(a: float, b: float, x: float) -> float:
    return a + (b - a) * x
