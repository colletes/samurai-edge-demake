"""
Contorno externo dos modelos em cel-shading (6.5.5).

O lutador é desenhado numa camada transparente própria; só os pixels opacos (alfa > 160) entram na máscara, então
sombras, rastros e auras translúcidos não ganham contorno. A máscara é dilatada por um disco e pintada com a tinta dos
sprites HD-2D, por baixo do desenho, o que dá a silhueta grossa do cel-shading. As arestas internas continuam finas,
desenhadas pelo próprio voxel com um tom escuro da cor.
"""
import pygame

from src.isometric import voxel_renderer

ALPHA_THRESHOLD = 160
_scratch: dict[tuple, pygame.Surface] = {}
_disks: dict[int, pygame.mask.Mask] = {}


class _LayerCamera:
    """Câmera que projeta como a original, mas com a origem deslocada para o canto da camada."""

    def __init__(self, camera, ox: int, oy: int):
        self._camera = camera
        self._ox = ox
        self._oy = oy

    def apply(self, wx, wy, wz=0.0):
        x, y = self._camera.apply(wx, wy, wz)
        return x - self._ox, y - self._oy

    def __getattr__(self, name):
        return getattr(self._camera, name)


def thickness(zoom: float) -> int:
    """Espessura da silhueta em pixels: acompanha o zoom para a tinta parecer a mesma em qualquer escala."""
    return 1 if zoom < 1.7 else (2 if zoom < 3.6 else 3)


def _disk(t: int) -> pygame.mask.Mask:
    disk = _disks.get(t)
    if disk is None:
        disk = pygame.mask.Mask((2 * t + 1, 2 * t + 1))
        for dx in range(-t, t + 1):
            for dy in range(-t, t + 1):
                if dx * dx + dy * dy <= t * t + 1:
                    disk.set_at((dx + t, dy + t), 1)
        _disks[t] = disk
    return disk


def _surface(name: str, w: int, h: int) -> pygame.Surface:
    key = (name, w, h)
    surf = _scratch.get(key)
    if surf is None:
        if len(_scratch) > 12:
            _scratch.clear()
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        _scratch[key] = surf
    surf.fill((0, 0, 0, 0))
    return surf


def render_cel(surface, camera, wx: float, wy: float, wz: float, alpha: int, draw):
    """`draw(layer, layer_camera)` desenha o lutador na camada; depois a silhueta e a camada vão para `surface`."""
    zoom = camera.zoom
    ox, oy = camera.apply(wx, wy, wz)
    left, up, down = int(80 * zoom) + 6, int(105 * zoom) + 6, int(44 * zoom) + 6
    w, h = 2 * left, up + down
    layer = _surface("layer", w, h)
    with voxel_renderer.render_style("cel"):
        draw(layer, _LayerCamera(camera, ox - left, oy - up))
    t = thickness(zoom)
    grown = pygame.mask.Mask((w, h))
    pygame.mask.from_surface(layer, ALPHA_THRESHOLD).convolve(_disk(t), grown, (-t, -t))
    out = _surface("out", w, h)
    grown.to_surface(out, setcolor=voxel_renderer.CEL_INK + (255,), unsetcolor=(0, 0, 0, 0))
    out.blit(layer, (0, 0))
    if alpha < 255:
        out.set_alpha(alpha)
    surface.blit(out, (ox - left, oy - up))
    out.set_alpha(255)
