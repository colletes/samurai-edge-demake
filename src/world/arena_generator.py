"""
Motor de arenas parametrizadas (Entregável 6.2).

Uma arena é descrita por um `ArenaSpec` (dataclasses puras): camadas de tiles, estilos de tile,
props posicionados ou espalhados por semente, estruturas (ex.: ponte), perigos dinâmicos, regra de
spawn, palco da introdução e ambiente de iluminação. `ArenaMap` constrói o mapa a partir do spec e
implementa o protocolo que o resto do jogo usa (`cols`, `rows`, `tiles`, `rocks`, `well`, `trees`,
`bamboos`, `torii_gates`, `lanterns`, `buildings`, `fireflies`, `carriages`, `falling_debris`,
`playable_bounds`, `is_water`, `is_hidden_in_bamboo`, `render_terrain`, `update`, ...).

O motor não conhece nenhuma arena específica: props, estruturas e perigos entram por registros
(`register_prop`, `register_structure`, `register_hazard`), preenchidos em `src/world/arenas.py`.
O `LightingEnvironment` é apenas dado; o desenho da iluminação é o Entregável 6.4.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field, replace
from typing import Any, Callable

import pygame

from src.isometric.iso_math import rotate_xy
from src.isometric.voxel_renderer import draw_voxel_box

Color = tuple[int, int, int]

# Folga entre a borda do buraco e o centro de quem anda (a esquiva parte dessa distância)
PIT_EDGE_MARGIN = 0.15
# Distância das estacas ao buraco protegido (menor que a folga de borda: ninguém anda para além da corda)
RAIL_OFFSET = 0.12
# Alcance medido de cada tipo de travessia (velocidade x duração em src/entities)
CROSS_REACH = {"heavy_roll": 1.70, "agile_roll": 2.31, "jump": 3.07, "shukuchi": 4.2}
# Largura (menor lado) de cada classe de buraco: até o alcance menos a folga e uma margem de aterrissagem
GAP_WIDTHS = {"S": 1.0, "M": 1.48, "L": 2.08, "J": 2.82}
GAP_TOLERANCE = 0.02
VOID_MIN_WIDTH = 3.6


def max_crossable_gap(reach: float) -> float:
    """Maior largura de buraco que uma travessia de alcance `reach` ainda vence partindo da borda."""
    return reach - PIT_EDGE_MARGIN - 0.02


class ArenaSpecError(ValueError):
    """Especificação de arena inválida."""


# ---------------------------------------------------------------------------
# Tiles
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class StoneDecor:
    """Laje voxel baixa cravada em tiles planos (ex.: Tobi-ishi), nos tiles com (x + y) % 2 == parity."""
    color: Color
    inset: float = 0.15
    size: float = 0.70
    height: float = 0.04
    parity: int = 0


@dataclass(frozen=True)
class TileStyle:
    """
    kind: "flat" (quad plano), "slab" (bloco voxel baixo), "water" (rebaixado com ondas e barrancos),
          "anchor" (sem desenho próprio; marca o piso de uma estrutura) ou "void" (nada).
    pattern: "single" usa colors[0]; "parity" usa colors[(x+y)%2]; "third" usa colors[1] se (x+y)%3==0;
             "rows" usa colors[y%2] (fileiras, como telhas de um telhado).
    """
    kind: str
    colors: tuple[Color, ...] = ()
    pattern: str = "single"
    edge: Color | None = None
    height: float = 0.0
    outline: bool = True
    top_edge: Color | None = None
    decor: StoneDecor | None = None
    depth: float = 0.15
    bank_ns: tuple[Color, Color] | None = None
    bank_ew: tuple[Color, Color] | None = None
    speed_mult: float = 1.0
    surface: str = "stone"  # material do piso, usado pelas partículas de terreno (ver SURFACES em terrain_particles.py)

    def color_at(self, x: int, y: int) -> Color:
        if self.pattern == "parity":
            return self.colors[(x + y) % 2]
        if self.pattern == "third":
            return self.colors[1] if (x + y) % 3 == 0 else self.colors[0]
        if self.pattern == "rows":
            return self.colors[y % 2]
        return self.colors[0]

    @property
    def water_like(self) -> bool:
        return self.kind in ("water", "anchor")


@dataclass(frozen=True)
class FillLayer:
    tile: int


@dataclass(frozen=True)
class RectLayer:
    """Retângulo inclusivo; `y0/y1 = None` cobre todas as linhas. `skip` lista tiles que não são sobrescritos."""
    tile: int
    x0: int
    x1: int
    y0: int | None = None
    y1: int | None = None
    skip: tuple[int, ...] = ()


@dataclass(frozen=True)
class EllipseLayer:
    """Tiles com hypot((x-cx)*sx, (y-cy)*sy) < radius."""
    tile: int
    cx: float
    cy: float
    radius: float
    sx: float = 1.0
    sy: float = 1.0


@dataclass(frozen=True)
class CheckerLayer:
    even: int
    odd: int
    x0: int
    x1: int
    y0: int | None = None
    y1: int | None = None


TileLayer = FillLayer | RectLayer | EllipseLayer | CheckerLayer


@dataclass(frozen=True)
class PitZone:
    """
    Buraco retangular em coordenadas reais (não em tiles). `gap_class` fixa a largura (menor lado): S, M, L e J
    são vencidas por travessias cada vez mais longas (ver GAP_WIDTHS); VOID é intransponível (penhasco).
    Sem proteção (`railed=False`) quem passa por cima com o centro dentro dele cai, andando ou não. Com proteção
    (`railed=True`: corda e estacas, ou corrimão de ponte) andar é bloqueado na borda e só cai quem termina um
    deslocamento (empurrão, puxão, esquiva ou salto curto demais) dentro dele.
    """
    x0: float
    y0: float
    x1: float
    y1: float
    gap_class: str = "VOID"
    railed: bool = False
    depth: float = 1.2
    floor_color: Color = (8, 6, 10)
    wall_colors: tuple[Color, Color] = ((96, 86, 74), (18, 15, 18))
    rim_color: Color = (92, 84, 72)
    water: tuple[Color, Color] | None = None  # (água, espuma): o fundo do buraco vira mar com ondas animadas

    @property
    def width(self) -> float:
        return min(self.x1 - self.x0, self.y1 - self.y0)

    def signed_distance(self, x: float, y: float) -> float:
        """Distância até a borda: negativa dentro do buraco, positiva fora."""
        dx = max(self.x0 - x, 0.0, x - self.x1)
        dy = max(self.y0 - y, 0.0, y - self.y1)
        if dx > 0.0 or dy > 0.0:
            return math.hypot(dx, dy)
        return -min(x - self.x0, self.x1 - x, y - self.y0, self.y1 - y)


# ---------------------------------------------------------------------------
# Props, estruturas, perigos, spawns, palco e iluminação
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RoofSlope:
    """
    Telhado de duas águas só visual: o piso sobe de 0 nas beiradas (x0 e x1) até `height` na cumeeira (x = ridge).
    Lutadores, props e tiles são desenhados sobre essa altura (Camera.height_fn); a lógica de jogo segue plana.
    """
    x0: float
    x1: float
    ridge: float
    height: float


@dataclass(frozen=True)
class PropSpec:
    kind: str
    x: float
    y: float
    params: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ScatterSpec:
    """Espalha `kind` pelos tiles com RNG semeado (ordem x, y); `clearances` = (coleção, distância mínima)."""
    kind: str
    seed: int
    blocked_tiles: tuple[int, ...] = ()
    clearances: tuple[tuple[str, float], ...] = ()
    cleared: tuple[tuple[float, float, float, float], ...] = ()  # retângulos (x0, y0, x1, y1) sem props, aplicados após o sorteio
    center: tuple[float, float] = (0.0, 0.0)
    inner_radius: float = 5.0
    density_inner: float = 0.25
    density_outer: float = 0.72
    jitter: float = 0.35


@dataclass(frozen=True)
class StructureSpec:
    kind: str
    anchor_tile: int
    params: dict = field(default_factory=dict)


@dataclass(frozen=True)
class HazardSpec:
    kind: str
    params: dict = field(default_factory=dict)


@dataclass(frozen=True)
class SpawnRule:
    x_range: tuple[float, float] | None = None
    margin: float = 3.0
    y_margin: float | None = None
    min_distance: float = 7.0
    min_pit_distance: float = 1.0  # distância mínima de qualquer buraco (acima de 1.0 também evita nascer em vigas estreitas)
    check_obstacles: bool = True
    rock_clearance: float = 0.65
    well_clearance: float = 1.6
    tree_clearance: float = 1.7
    outer_attempts: int = 250
    inner_attempts: int = 40
    fallback: tuple[tuple[float, float], tuple[float, float]] = ((10.5, 7.0), (10.5, 15.0))


@dataclass(frozen=True)
class StageSpec:
    """Ponto da introdução da batalha; `structure` (índice) eleva o personagem ao topo dessa estrutura."""
    x: float
    y: float
    structure: int | None = None


@dataclass(frozen=True)
class LightSource:
    x: float
    y: float
    z: float
    color: Color
    radius: float
    flicker: float = 0.0


@dataclass(frozen=True)
class AtmosphereEffect:
    kind: str
    density: float = 1.0
    points: tuple[tuple[float, float, float], ...] = ()


@dataclass(frozen=True)
class LightingEnvironment:
    ambient_color: Color = (255, 255, 255)
    ambient_strength: float = 1.0
    vignette: float = 0.0
    lights: tuple[LightSource, ...] = ()
    atmosphere: tuple[AtmosphereEffect, ...] = ()


@dataclass(frozen=True)
class WindSpec:
    """Vento da arena em unidades de mundo por segundo; `gust` 0 = constante, 1 = rajadas que vão de 0 a 2x."""
    dir_x: float = 1.0
    dir_y: float = 0.4
    strength: float = 0.4
    gust: float = 0.5


@dataclass(frozen=True)
class ArenaSpec:
    id: str
    name: str
    cols: int
    rows: int
    bg_color: Color
    music: str
    tile_styles: dict[int, TileStyle]
    layers: tuple[TileLayer, ...]
    spawns: SpawnRule
    stage: StageSpec
    props: tuple[PropSpec, ...] = ()
    scatters: tuple[ScatterSpec, ...] = ()
    structures: tuple[StructureSpec, ...] = ()
    hazards: tuple[HazardSpec, ...] = ()
    lighting: LightingEnvironment = field(default_factory=LightingEnvironment)
    playable_bounds: tuple[float, float, float, float] | None = None
    reflections: tuple[tuple[int, int], ...] = ()
    pits: tuple[PitZone, ...] = ()
    nav_points: tuple[tuple[float, float], ...] = ()
    slopes: tuple[RoofSlope, ...] = ()
    drift_count: int = 45  # folhas e pétalas ao vento (0 = nenhuma)
    drift_petals: float = 0.25  # fração das partículas que são pétalas de sakura
    wind: WindSpec = field(default_factory=WindSpec)


# ---------------------------------------------------------------------------
# Registros
# ---------------------------------------------------------------------------
COLLECTIONS = ("rocks", "trees", "torii_gates", "lanterns", "buildings", "bamboos")


@dataclass(frozen=True)
class PropKind:
    factory: Callable[..., Any]
    collection: str
    single: bool = False


PROP_KINDS: dict[str, PropKind] = {}
STRUCTURE_KINDS: dict[str, Callable[..., Any]] = {}
HAZARD_KINDS: dict[str, Callable[..., Any]] = {}


def register_prop(kind: str, factory: Callable[..., Any], collection: str, single: bool = False):
    """`factory(x, y, **params)` devolve o objeto; `collection` é a lista do mapa (ou 'well' se single)."""
    PROP_KINDS[kind] = PropKind(factory, collection, single)


def register_structure(kind: str, factory: Callable[..., Any]):
    """Estrutura: `draw(surface, camera, time_val)` e `deck_height(wx, wy)`."""
    STRUCTURE_KINDS[kind] = factory


def register_hazard(kind: str, factory: Callable[..., Any]):
    """Perigo: `update(arena, dt, fighters, camera, particles, banners, cinematic_director)`."""
    HAZARD_KINDS[kind] = factory


# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------
def _check_color(value, label: str):
    if len(value) != 3 or any(not 0 <= c <= 255 for c in value):
        raise ArenaSpecError(f"{label}: cor inválida {value}")


def validate_spec(spec: ArenaSpec):
    """Valida a estrutura do spec (sem construir o mapa). Levanta ArenaSpecError."""
    if spec.cols < 4 or spec.rows < 4:
        raise ArenaSpecError(f"{spec.id}: tamanho mínimo 4x4")
    _check_color(spec.bg_color, f"{spec.id}.bg_color")
    for tile_id, style in spec.tile_styles.items():
        if style.kind not in ("flat", "slab", "water", "anchor", "void"):
            raise ArenaSpecError(f"{spec.id}: tile {tile_id} com kind desconhecido '{style.kind}'")
        needs_colors = style.kind in ("flat", "slab", "water")
        if needs_colors and not style.colors:
            raise ArenaSpecError(f"{spec.id}: tile {tile_id} sem cores")
        for color in style.colors:
            _check_color(color, f"{spec.id}.tile {tile_id}")
        if style.pattern == "parity" and len(style.colors) < 2:
            raise ArenaSpecError(f"{spec.id}: tile {tile_id} com padrão 'parity' precisa de 2 cores")
        if style.pattern == "rows" and len(style.colors) < 2:
            raise ArenaSpecError(f"{spec.id}: tile {tile_id} com padrão 'rows' precisa de 2 cores")
        if style.pattern == "third" and len(style.colors) < 2:
            raise ArenaSpecError(f"{spec.id}: tile {tile_id} com padrão 'third' precisa de 2 cores")

    def need_tile(tile: int, where: str):
        if tile not in spec.tile_styles:
            raise ArenaSpecError(f"{spec.id}: {where} usa tile {tile} sem estilo")

    def need_span(lo: int | None, hi: int | None, size: int, where: str):
        lo = 0 if lo is None else lo
        hi = size - 1 if hi is None else hi
        if not (0 <= lo <= hi < size):
            raise ArenaSpecError(f"{spec.id}: {where} fora da grade ({lo}..{hi} de {size})")

    if not spec.layers or not isinstance(spec.layers[0], FillLayer):
        raise ArenaSpecError(f"{spec.id}: a primeira camada deve ser um FillLayer")
    for layer in spec.layers:
        if isinstance(layer, FillLayer):
            need_tile(layer.tile, "FillLayer")
        elif isinstance(layer, RectLayer):
            need_tile(layer.tile, "RectLayer")
            need_span(layer.x0, layer.x1, spec.cols, "RectLayer.x")
            need_span(layer.y0, layer.y1, spec.rows, "RectLayer.y")
        elif isinstance(layer, EllipseLayer):
            need_tile(layer.tile, "EllipseLayer")
        elif isinstance(layer, CheckerLayer):
            need_tile(layer.even, "CheckerLayer")
            need_tile(layer.odd, "CheckerLayer")
            need_span(layer.x0, layer.x1, spec.cols, "CheckerLayer.x")
            need_span(layer.y0, layer.y1, spec.rows, "CheckerLayer.y")
        else:
            raise ArenaSpecError(f"{spec.id}: camada desconhecida {layer!r}")

    def need_inside(x: float, y: float, where: str):
        if not (0.0 <= x <= spec.cols and 0.0 <= y <= spec.rows):
            raise ArenaSpecError(f"{spec.id}: {where} ({x}, {y}) fora do mapa")

    for prop in spec.props:
        if prop.kind not in PROP_KINDS:
            raise ArenaSpecError(f"{spec.id}: prop desconhecido '{prop.kind}'")
        need_inside(prop.x, prop.y, f"prop '{prop.kind}'")
    for scatter in spec.scatters:
        if scatter.kind not in PROP_KINDS:
            raise ArenaSpecError(f"{spec.id}: scatter com prop desconhecido '{scatter.kind}'")
        if not (0.0 <= scatter.density_inner <= 1.0 and 0.0 <= scatter.density_outer <= 1.0):
            raise ArenaSpecError(f"{spec.id}: densidades do scatter devem estar em 0..1")
        for collection, dist in scatter.clearances:
            if collection not in COLLECTIONS and collection != "well":
                raise ArenaSpecError(f"{spec.id}: clearance para coleção desconhecida '{collection}'")
            if dist < 0:
                raise ArenaSpecError(f"{spec.id}: clearance negativo")
    for struct in spec.structures:
        if struct.kind not in STRUCTURE_KINDS:
            raise ArenaSpecError(f"{spec.id}: estrutura desconhecida '{struct.kind}'")
        style = spec.tile_styles.get(struct.anchor_tile)
        if style is None or style.kind != "anchor":
            raise ArenaSpecError(f"{spec.id}: estrutura '{struct.kind}' precisa de um tile 'anchor'")
    for hazard in spec.hazards:
        if hazard.kind not in HAZARD_KINDS:
            raise ArenaSpecError(f"{spec.id}: perigo desconhecido '{hazard.kind}'")

    need_inside(spec.stage.x, spec.stage.y, "palco")
    if spec.stage.structure is not None and not 0 <= spec.stage.structure < len(spec.structures):
        raise ArenaSpecError(f"{spec.id}: palco aponta para estrutura inexistente")
    for point in spec.spawns.fallback:
        need_inside(point[0], point[1], "spawn de reserva")
    if spec.spawns.min_distance <= 0 or spec.spawns.outer_attempts < 1 or spec.spawns.inner_attempts < 1:
        raise ArenaSpecError(f"{spec.id}: regra de spawn inválida")

    light = spec.lighting
    _check_color(light.ambient_color, f"{spec.id}.ambient")
    if not (0.0 <= light.ambient_strength <= 1.0 and 0.0 <= light.vignette <= 1.0):
        raise ArenaSpecError(f"{spec.id}: ambient_strength e vignette devem estar em 0..1")
    for src in light.lights:
        _check_color(src.color, f"{spec.id}.luz")
        if src.radius <= 0:
            raise ArenaSpecError(f"{spec.id}: luz com raio não positivo")
        need_inside(src.x, src.y, "luz")
    for effect in light.atmosphere:
        if effect.density < 0:
            raise ArenaSpecError(f"{spec.id}: densidade atmosférica negativa")
    for x, y in spec.reflections:
        need_inside(x, y, "reflexo")

    for tile_id, style in spec.tile_styles.items():
        if not 0.1 <= style.speed_mult <= 2.0:
            raise ArenaSpecError(f"{spec.id}: tile {tile_id} com speed_mult fora de 0.1..2.0")
    for i, pit in enumerate(spec.pits):
        where = f"buraco {i + 1}"
        if not (pit.x0 < pit.x1 and pit.y0 < pit.y1):
            raise ArenaSpecError(f"{spec.id}: {where} com retângulo inválido")
        need_inside(pit.x0, pit.y0, where)
        need_inside(pit.x1, pit.y1, where)
        if pit.gap_class == "VOID":
            if pit.width < VOID_MIN_WIDTH:
                raise ArenaSpecError(f"{spec.id}: {where} VOID precisa de largura mínima {VOID_MIN_WIDTH}")
        elif pit.gap_class in GAP_WIDTHS:
            if abs(pit.width - GAP_WIDTHS[pit.gap_class]) > GAP_TOLERANCE:
                raise ArenaSpecError(
                    f"{spec.id}: {where} classe {pit.gap_class} pede largura {GAP_WIDTHS[pit.gap_class]}, tem {pit.width:.2f}")
        else:
            raise ArenaSpecError(f"{spec.id}: {where} com classe desconhecida '{pit.gap_class}'")
        _check_color(pit.floor_color, f"{spec.id}.{where}")
        for other in spec.pits[:i]:
            if pit.x0 < other.x1 and other.x0 < pit.x1 and pit.y0 < other.y1 and other.y0 < pit.y1:
                raise ArenaSpecError(f"{spec.id}: {where} sobrepõe outro buraco")
    for x, y in spec.nav_points:
        need_inside(x, y, "ponto de navegação")
    for i, slope in enumerate(spec.slopes):
        if not (slope.x0 < slope.ridge < slope.x1) or slope.height <= 0:
            raise ArenaSpecError(f"{spec.id}: telhado {i + 1} inválido")


def derive_spec(base: ArenaSpec, **changes) -> ArenaSpec:
    """Variante de uma arena: copia o spec base trocando só os campos informados (valida o resultado)."""
    spec = replace(base, **changes)
    validate_spec(spec)
    return spec


# ---------------------------------------------------------------------------
# Mapa
# ---------------------------------------------------------------------------
def _distance(ax: float, ay: float, bx: float, by: float) -> float:
    return math.hypot(ax - bx, ay - by)


class ArenaMap:
    """Mapa jogável construído a partir de um `ArenaSpec`."""

    def __init__(self, spec: ArenaSpec):
        from src.world import arenas  # noqa: F401  (garante os registros padrão de props/estruturas/perigos)

        validate_spec(spec)
        self.spec = spec
        self.arena_id = spec.id
        self.theme_name = spec.name
        self.cols = spec.cols
        self.rows = spec.rows
        self.bg_color = spec.bg_color
        self.music = spec.music
        self.lighting = spec.lighting
        self.playable_bounds = spec.playable_bounds
        self.styles = spec.tile_styles
        self.pits: list[PitZone] = list(spec.pits)
        self.nav_points: list[tuple[float, float]] = list(spec.nav_points)

        self.rocks: list = []
        self.trees: list = []
        self.torii_gates: list = []
        self.lanterns: list = []
        self.buildings: list = []
        self.bamboos: list = []
        self.interactives: list = []  # props com `tick` e `ignite` (ex.: canhão aceso por golpes e projéteis)
        self.emitters: list = []  # props só com `tick` (ex.: incensário que solta fumaça)
        self.fog = None  # FogVolume ligado pelo main (rastros da Kasumi e banco de névoa)
        self.dispel_requested = False  # o sino do santuário pede que main apague fumaças e nuvens de veneno
        self.well = None
        self.carriages: list = []
        self.falling_debris: list = []
        self.fireflies: list[tuple[float, float, float]] = []
        for effect in spec.lighting.atmosphere:
            if effect.kind == "fireflies":
                self.fireflies = list(effect.points)

        self.tiles = self._build_tiles()
        self._build_props()
        self._build_rails()
        self.structures = [STRUCTURE_KINDS[s.kind](**s.params) for s in spec.structures]
        self.hazards = [HAZARD_KINDS[h.kind](**h.params) for h in spec.hazards]
        self._validate_built()

    # -- construção ---------------------------------------------------------
    def _build_tiles(self) -> list[list[int]]:
        spec = self.spec
        grid = [[0 for _ in range(self.rows)] for _ in range(self.cols)]
        for layer in spec.layers:
            if isinstance(layer, FillLayer):
                for x in range(self.cols):
                    for y in range(self.rows):
                        grid[x][y] = layer.tile
            elif isinstance(layer, RectLayer):
                y0 = 0 if layer.y0 is None else layer.y0
                y1 = self.rows - 1 if layer.y1 is None else layer.y1
                for x in range(layer.x0, layer.x1 + 1):
                    for y in range(y0, y1 + 1):
                        if grid[x][y] not in layer.skip:
                            grid[x][y] = layer.tile
            elif isinstance(layer, EllipseLayer):
                for x in range(self.cols):
                    for y in range(self.rows):
                        if math.hypot((x - layer.cx) * layer.sx, (y - layer.cy) * layer.sy) < layer.radius:
                            grid[x][y] = layer.tile
            elif isinstance(layer, CheckerLayer):
                y0 = 0 if layer.y0 is None else layer.y0
                y1 = self.rows - 1 if layer.y1 is None else layer.y1
                for x in range(layer.x0, layer.x1 + 1):
                    for y in range(y0, y1 + 1):
                        grid[x][y] = layer.even if (x + y) % 2 == 0 else layer.odd
        return grid

    def _place(self, kind: PropKind, obj):
        if kind.single:
            setattr(self, kind.collection, obj)
        else:
            getattr(self, kind.collection).append(obj)
        if hasattr(obj, "tick"):
            (self.interactives if hasattr(obj, "ignite") else self.emitters).append(obj)

    def _build_props(self):
        for prop in self.spec.props:
            kind = PROP_KINDS[prop.kind]
            self._place(kind, kind.factory(prop.x, prop.y, **prop.params))
        for scatter in self.spec.scatters:
            self._scatter(scatter)

    def _build_rails(self):
        """Estacas com corda em volta dos buracos protegidos (menos nos lados que encostam na borda do mapa)."""
        from src.world.solid_props import RailPost
        off = RAIL_OFFSET
        for pit in self.pits:
            if not pit.railed:
                continue
            edges = []
            if pit.y0 > 0.01:
                edges.append(((pit.x0 - off, pit.y0 - off), (pit.x1 + off, pit.y0 - off)))
            if pit.x1 < self.cols - 0.01:
                edges.append(((pit.x1 + off, pit.y0 - off), (pit.x1 + off, pit.y1 + off)))
            if pit.y1 < self.rows - 0.01:
                edges.append(((pit.x1 + off, pit.y1 + off), (pit.x0 - off, pit.y1 + off)))
            if pit.x0 > 0.01:
                edges.append(((pit.x0 - off, pit.y1 + off), (pit.x0 - off, pit.y0 - off)))
            for (ax, ay), (bx, by) in edges:
                count = max(1, round(math.hypot(bx - ax, by - ay) / 1.0))
                points = [(ax + (bx - ax) * i / count, ay + (by - ay) * i / count) for i in range(count + 1)]
                for i, (px, py) in enumerate(points):
                    nxt = points[i + 1] if i + 1 < len(points) else None
                    self.lanterns.append(RailPost(px, py, nxt))

    def _clear_of(self, x: float, y: float, clearances) -> bool:
        for collection, dist in clearances:
            objs = getattr(self, collection)
            if collection == "well":
                objs = [objs] if objs else []
            if any(_distance(x, y, o.wx, o.wy) < dist for o in objs):
                return False
        return True

    def _scatter(self, scatter: ScatterSpec):
        kind = PROP_KINDS[scatter.kind]
        rng = random.Random(scatter.seed)
        for x in range(self.cols):
            for y in range(self.rows):
                if self.tiles[x][y] in scatter.blocked_tiles:
                    continue
                if not self._clear_of(x, y, scatter.clearances):
                    continue
                dist_to_center = _distance(x, y, *scatter.center)
                chance = scatter.density_outer if dist_to_center > scatter.inner_radius else scatter.density_inner
                if rng.random() < chance:
                    ox = rng.uniform(-scatter.jitter, scatter.jitter)
                    oy = rng.uniform(-scatter.jitter, scatter.jitter)
                    px, py = x + 0.5 + ox, y + 0.5 + oy
                    if any(r[0] <= px <= r[2] and r[1] <= py <= r[3] for r in scatter.cleared):
                        continue
                    self._place(kind, kind.factory(px, py))

    def _solid_objects(self) -> list:
        objs = list(self.rocks) + list(self.trees) + list(self.buildings)
        if self.well:
            objs.append(self.well)
        return objs

    def _validate_built(self):
        """Palco e spawns de reserva precisam estar em chão livre."""
        points = [("palco", (self.spec.stage.x, self.spec.stage.y))]
        points += [(f"spawn de reserva {i + 1}", p) for i, p in enumerate(self.spec.spawns.fallback)]
        for label, (x, y) in points:
            if self.is_water(x, y) or any(o.check_collision(x, y, 0.5)[0] for o in self._solid_objects()):
                raise ArenaSpecError(f"{self.spec.id}: {label} ({x}, {y}) cai em água ou obstáculo")
            if self.pit_edge_distance(x, y) < 1.0:
                raise ArenaSpecError(f"{self.spec.id}: {label} ({x}, {y}) cai em buraco ou colado nele")

    # -- consultas ----------------------------------------------------------
    def height_at(self, wx: float, wy: float) -> float:
        """Altura visual do piso (telhados inclinados); 0.0 em arenas planas."""
        for slope in self.spec.slopes:
            if slope.x0 < wx < slope.x1:
                if wx <= slope.ridge:
                    return slope.height * (wx - slope.x0) / (slope.ridge - slope.x0)
                return slope.height * (slope.x1 - wx) / (slope.x1 - slope.ridge)
        return 0.0

    def attach_camera(self, camera):
        """Liga o relevo visual da arena à câmera (sem efeito em arenas planas)."""
        camera.height_fn = self.height_at if self.spec.slopes else None
        return camera

    def style_at(self, x: int, y: int) -> TileStyle:
        return self.styles[self.tiles[x][y]]

    def is_water(self, wx: float, wy: float) -> bool:
        """Verifica se uma coordenada de mundo está sobre água não coberta por estrutura."""
        tx, ty = int(math.floor(wx)), int(math.floor(wy))
        if 0 <= tx < self.cols and 0 <= ty < self.rows:
            return self.style_at(tx, ty).kind == "water"
        return False

    def is_hidden_in_bamboo(self, wx: float, wy: float) -> bool:
        return any(b.is_samurai_hidden(wx, wy) for b in self.bamboos)

    def speed_mult_at(self, wx: float, wy: float) -> float:
        """Multiplicador de velocidade de caminhada do tile sob a coordenada (1.0 fora da grade)."""
        tx, ty = int(math.floor(wx)), int(math.floor(wy))
        if 0 <= tx < self.cols and 0 <= ty < self.rows:
            return self.style_at(tx, ty).speed_mult
        return 1.0

    def surface_at(self, wx: float, wy: float) -> str | None:
        """Material do piso sob a coordenada ("water" para tiles de água); None fora da grade."""
        tx, ty = int(math.floor(wx)), int(math.floor(wy))
        if not (0 <= tx < self.cols and 0 <= ty < self.rows):
            return None
        style = self.style_at(tx, ty)
        return "water" if style.kind == "water" else style.surface

    def wind_at(self, wx: float, wy: float, t: float) -> tuple[float, float]:
        """Vento (vx, vy) em u/s no ponto e no instante t, com rajadas que variam no espaço e no tempo."""
        wind = self.spec.wind
        norm = math.hypot(wind.dir_x, wind.dir_y) or 1.0
        gust = 1.0 + wind.gust * (0.55 * math.sin(0.45 * t + 0.17 * wx + 0.11 * wy)
                                  + 0.45 * math.sin(1.1 * t + 0.23 * wy - 0.13 * wx + 1.7))
        gust = max(0.0, gust) * wind.strength / norm
        return wind.dir_x * gust, wind.dir_y * gust

    def pit_edge_distance(self, wx: float, wy: float) -> float:
        """Menor distância com sinal até qualquer buraco (negativa dentro; infinita sem buracos)."""
        if not self.pits:
            return math.inf
        return min(p.signed_distance(wx, wy) for p in self.pits)

    @property
    def has_rails(self) -> bool:
        return any(p.railed for p in self.pits)

    def rail_edge_distance(self, wx: float, wy: float) -> float:
        """Como `pit_edge_distance`, mas só para buracos protegidos (os que bloqueiam o andar)."""
        railed = [p for p in self.pits if p.railed]
        if not railed:
            return math.inf
        return min(p.signed_distance(wx, wy) for p in railed)

    def pit_at(self, wx: float, wy: float) -> PitZone | None:
        """Buraco que contém o ponto (centro estritamente dentro), ou None."""
        for pit in self.pits:
            if pit.signed_distance(wx, wy) < 0.0:
                return pit
        return None

    def segment_crosses_pit(self, ax: float, ay: float, bx: float, by: float) -> PitZone | None:
        """Primeiro buraco cortado pelo segmento A-B (amostragem de 0.25), usado pela IA para escolher rota."""
        if not self.pits:
            return None
        steps = max(1, int(math.hypot(bx - ax, by - ay) / 0.25))
        for i in range(steps + 1):
            t = i / steps
            pit = self.pit_at(ax + (bx - ax) * t, ay + (by - ay) * t)
            if pit:
                return pit
        return None

    @property
    def has_hazards(self) -> bool:
        return bool(self.hazards) or bool(self.interactives)

    @property
    def has_updates(self) -> bool:
        """Algo precisa de `update` a cada frame (perigos, props interativos ou emissores)."""
        return self.has_hazards or bool(self.emitters)

    def intro_stage_point(self) -> tuple[float, float, float]:
        """Palco da introdução da batalha (x, y, z); z segue a estrutura indicada no spec."""
        stage = self.spec.stage
        z = 0.0
        if stage.structure is not None:
            z = self.structures[stage.structure].deck_height(stage.x, stage.y)
        return stage.x, stage.y, z

    # -- spawns -------------------------------------------------------------
    def _spawn_valid(self, x: float, y: float, rule: SpawnRule) -> bool:
        if self.pit_edge_distance(x, y) < rule.min_pit_distance:
            return False
        if any(math.hypot(x - e.wx, y - e.wy) < getattr(e, "spawn_clearance", 0.0) for e in self.emitters):
            return False  # armadilhas e afins: ninguém nasce em cima
        if not rule.check_obstacles:
            return True
        if self.is_water(x, y):
            return False
        if any(_distance(x, y, r.wx, r.wy) < (r.radius + rule.rock_clearance) for r in self.rocks):
            return False
        if any(b.check_collision(x, y, 0.9)[0] for b in self.buildings):
            return False
        if self.well and _distance(x, y, self.well.wx, self.well.wy) < rule.well_clearance:
            return False
        return not any(_distance(x, y, t.wx, t.wy) < rule.tree_clearance for t in self.trees)

    def pick_spawns(self, min_distance: float | None = None) -> tuple[tuple[float, float], tuple[float, float]]:
        """Duas posições válidas separadas por pelo menos `min_distance` (evita melee logo no início)."""
        rule = self.spec.spawns
        min_dist = rule.min_distance if min_distance is None else min_distance
        x_lo, x_hi = rule.x_range if rule.x_range else (rule.margin, self.cols - rule.margin)
        y_margin = rule.margin if rule.y_margin is None else rule.y_margin
        y_lo, y_hi = y_margin, self.rows - y_margin

        for _ in range(rule.outer_attempts):
            x1 = round(random.uniform(x_lo, x_hi), 1)
            y1 = round(random.uniform(y_lo, y_hi), 1)
            if not self._spawn_valid(x1, y1, rule):
                continue
            for _ in range(rule.inner_attempts):
                x2 = round(random.uniform(x_lo, x_hi), 1)
                y2 = round(random.uniform(y_lo, y_hi), 1)
                if _distance(x1, y1, x2, y2) < min_dist:
                    continue
                if not self._spawn_valid(x2, y2, rule):
                    continue
                return (x1, y1), (x2, y2)
        return rule.fallback

    # -- simulação e desenho ------------------------------------------------
    def update(self, dt: float, fighters: list, camera, particles: list, banners: list, cinematic_director=None):
        for hazard in self.hazards:
            hazard.update(self, dt, fighters, camera, particles, banners, cinematic_director)
        for prop in self.interactives + self.emitters:
            prop.tick(self, dt, fighters, camera, particles, banners)

    def render_overhead(self, surface: pygame.Surface, camera, time_val: float):
        """Elementos no ar (corrente e peso do pêndulo), desenhados por cima dos lutadores."""
        for hazard in self.hazards:
            draw = getattr(hazard, "render_overhead", None)
            if draw:
                draw(self, surface, camera, time_val)

    def render_terrain(self, surface: pygame.Surface, camera, time_val: float):
        """Desenha os tiles (válido para qualquer azimute) e, por cima, as estruturas cujo piso está à vista."""
        visible_anchors: set[int] = set()
        width, height = surface.get_width(), surface.get_height()
        reflections = set(self.spec.reflections)

        for x in range(self.cols):
            for y in range(self.rows):
                tile = self.tiles[x][y]
                style = self.styles[tile]

                p_top = camera.apply(x, y, 0.0)
                p_right = camera.apply(x + 1, y, 0.0)
                p_bottom = camera.apply(x + 1, y + 1, 0.0)
                p_left = camera.apply(x, y + 1, 0.0)
                quad = [p_top, p_right, p_bottom, p_left]

                qxs = [p[0] for p in quad]
                qys = [p[1] for p in quad]
                if max(qys) < -60 or min(qys) > height + 60 or max(qxs) < -60 or min(qxs) > width + 60:
                    continue

                if style.kind == "flat":
                    self._draw_flat(surface, camera, style, x, y, quad)
                elif style.kind == "slab":
                    self._draw_slab(surface, camera, style, x, y)
                elif style.kind == "water":
                    self._draw_water(surface, camera, style, x, y, quad, time_val, (x, y) in reflections)
                elif style.kind == "anchor":
                    visible_anchors.add(tile)

        for struct_spec, struct in zip(self.spec.structures, self.structures):
            if struct_spec.anchor_tile in visible_anchors:
                struct.draw(surface, camera, time_val)

        for pit in self.pits:
            self._draw_pit(surface, camera, pit, time_val)
        for hazard in self.hazards + self.interactives:
            draw_ground = getattr(hazard, "render_ground", None)
            if draw_ground:
                draw_ground(self, surface, camera, time_val)

    @staticmethod
    def _draw_pit(surface, camera, pit: PitZone, time_val: float = 0.0):
        """
        Buraco integrado ao terreno: lábio de terra irregular, paredes internas em camadas que escurecem com a
        profundidade (só as voltadas para a câmera), fundo em névoa, espessura do lábio nas bordas da frente,
        pedriscos e rachaduras que saem da borda.
        """
        corners = [(pit.x0, pit.y0), (pit.x1, pit.y0), (pit.x1, pit.y1), (pit.x0, pit.y1)]
        top = [camera.apply(x, y, 0.0) for x, y in corners]
        width, height = surface.get_width(), surface.get_height()
        if max(p[1] for p in top) < -80 or min(p[1] for p in top) > height + 80 \
                or max(p[0] for p in top) < -80 or min(p[0] for p in top) > width + 80:
            return
        rng = random.Random(int(pit.x0 * 131 + pit.y0 * 71 + pit.x1 * 17 + pit.y1 * 5))
        wall_top, wall_deep = pit.wall_colors

        def lerp(a, b, f):
            return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))

        # 1. Lábio de terra irregular em volta da abertura (contorno com variação determinística)
        ring = []
        steps_x = max(2, int((pit.x1 - pit.x0) / 0.45))
        steps_y = max(2, int((pit.y1 - pit.y0) / 0.45))
        for i in range(steps_x):
            ring.append((pit.x0 + (pit.x1 - pit.x0) * i / steps_x, pit.y0 - 0.16 - rng.uniform(0.0, 0.10)))
        for i in range(steps_y):
            ring.append((pit.x1 + 0.16 + rng.uniform(0.0, 0.10), pit.y0 + (pit.y1 - pit.y0) * i / steps_y))
        for i in range(steps_x):
            ring.append((pit.x1 - (pit.x1 - pit.x0) * i / steps_x, pit.y1 + 0.16 + rng.uniform(0.0, 0.10)))
        for i in range(steps_y):
            ring.append((pit.x0 - 0.16 - rng.uniform(0.0, 0.10), pit.y1 - (pit.y1 - pit.y0) * i / steps_y))
        pygame.draw.polygon(surface, lerp(pit.rim_color, (0, 0, 0), 0.28), [camera.apply(x, y, 0.0) for x, y in ring])
        inner_ring = [(pit.x0 - 0.07, pit.y0 - 0.07), (pit.x1 + 0.07, pit.y0 - 0.07),
                      (pit.x1 + 0.07, pit.y1 + 0.07), (pit.x0 - 0.07, pit.y1 + 0.07)]
        pygame.draw.polygon(surface, pit.rim_color, [camera.apply(x, y, 0.0) for x, y in inner_ring])

        # 2. Interior (fundo em névoa e paredes em camadas) desenhado à parte e recortado pela abertura: o que
        #    ficaria abaixo da borda da frente é encoberto pelo chão, como num buraco de verdade
        bottom = [camera.apply(x, y, -pit.depth) for x, y in corners]
        xs = [p[0] for p in top + bottom]
        ys = [p[1] for p in top + bottom]
        area = pygame.Rect(int(min(xs)) - 2, int(min(ys)) - 2, int(max(xs) - min(xs)) + 5, int(max(ys) - min(ys)) + 5)
        interior = pygame.Surface(area.size, pygame.SRCALPHA)

        def local(point):
            return point[0] - area.x, point[1] - area.y

        pygame.draw.polygon(interior, pit.floor_color, [local(p) for p in bottom])
        cx, cy = (pit.x0 + pit.x1) / 2.0, (pit.y0 + pit.y1) / 2.0
        for k, glow in enumerate((0.06, 0.12)):
            f = 0.70 - 0.30 * k
            mist = [local(camera.apply(cx + (x - cx) * f, cy + (y - cy) * f, -pit.depth)) for x, y in corners]
            pygame.draw.polygon(interior, lerp(pit.floor_color, wall_top, glow), mist)

        if pit.water is not None:
            ArenaMap._draw_pit_water(interior, local, camera, pit, rng, time_val)

        bands = 7
        near_edges = []
        for (ndx, ndy), (i, j) in (((0, -1), (0, 1)), ((1, 0), (1, 2)), ((0, 1), (2, 3)), ((-1, 0), (3, 0))):
            face_x, face_y = rotate_xy(-ndx, -ndy, camera.azimuth)
            (xa, ya), (xb, yb) = corners[i], corners[j]
            if face_x + face_y > 1e-6:
                for k in range(bands):
                    z0, z1 = -pit.depth * k / bands, -pit.depth * (k + 1) / bands
                    shade = lerp(wall_top, wall_deep, ((k + 0.5) / bands) ** 0.75)
                    quad = [local(camera.apply(xa, ya, z0)), local(camera.apply(xb, yb, z0)),
                            local(camera.apply(xb, yb, z1)), local(camera.apply(xa, ya, z1))]
                    pygame.draw.polygon(interior, shade, quad)
                    pygame.draw.line(interior, lerp(shade, (0, 0, 0), 0.35), quad[3], quad[2], 1)
            else:
                near_edges.append(((xa, ya), (xb, yb)))
        mask = pygame.Surface(area.size, pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), [local(p) for p in top])
        interior.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(interior, area.topleft)

        # 3. Espessura do lábio nas bordas da frente
        for (xa, ya), (xb, yb) in near_edges:
            lip = [camera.apply(xa, ya, 0.0), camera.apply(xb, yb, 0.0), camera.apply(xb, yb, -0.14), camera.apply(xa, ya, -0.14)]
            pygame.draw.polygon(surface, lerp(pit.rim_color, (255, 255, 255), 0.12), lip)
            pygame.draw.line(surface, lerp(pit.rim_color, (0, 0, 0), 0.45), lip[3], lip[2], 1)
        pygame.draw.polygon(surface, lerp(pit.rim_color, (0, 0, 0), 0.5), top, 1)

        # 4. Pedriscos soltos e rachaduras saindo da borda, para ancorar o buraco no chão
        for _ in range(int((pit.x1 - pit.x0 + pit.y1 - pit.y0) * 1.1)):
            side = rng.randint(0, 3)
            t = rng.random()
            off = rng.uniform(0.18, 0.40)
            px = pit.x0 + (pit.x1 - pit.x0) * t if side in (0, 2) else (pit.x0 - off if side == 3 else pit.x1 + off)
            py = pit.y0 + (pit.y1 - pit.y0) * t if side in (1, 3) else (pit.y0 - off if side == 0 else pit.y1 + off)
            size = rng.uniform(0.05, 0.11)
            chip = [camera.apply(px, py, 0.02), camera.apply(px + size, py, 0.02),
                    camera.apply(px + size, py + size * 0.8, 0.02), camera.apply(px, py + size * 0.8, 0.02)]
            pygame.draw.polygon(surface, lerp(pit.rim_color, (255, 255, 255), rng.uniform(0.0, 0.22)), chip)
        for _ in range(3):
            side = rng.randint(0, 3)
            t = rng.uniform(0.15, 0.85)
            sx = pit.x0 + (pit.x1 - pit.x0) * t if side in (0, 2) else (pit.x0 - 0.1 if side == 3 else pit.x1 + 0.1)
            sy = pit.y0 + (pit.y1 - pit.y0) * t if side in (1, 3) else (pit.y0 - 0.1 if side == 0 else pit.y1 + 0.1)
            dx = (-1.0 if side == 3 else 1.0 if side == 1 else rng.uniform(-0.4, 0.4))
            dy = (-1.0 if side == 0 else 1.0 if side == 2 else rng.uniform(-0.4, 0.4))
            points = [(sx, sy)]
            for _ in range(3):
                sx += dx * rng.uniform(0.18, 0.34) + rng.uniform(-0.08, 0.08)
                sy += dy * rng.uniform(0.18, 0.34) + rng.uniform(-0.08, 0.08)
                points.append((sx, sy))
            pygame.draw.lines(surface, lerp(pit.rim_color, (0, 0, 0), 0.6), False, [camera.apply(x, y, 0.01) for x, y in points], 1)

    @staticmethod
    def _draw_pit_water(interior, local, camera, pit: PitZone, rng, time_val: float):
        """Mar no fundo do buraco: lâmina d'água com reflexos, cristas de onda que andam e espuma junto às paredes."""
        water, foam = pit.water
        z = -pit.depth

        def lerp(a, b, f):
            return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))

        corners = [(pit.x0, pit.y0), (pit.x1, pit.y0), (pit.x1, pit.y1), (pit.x0, pit.y1)]
        pygame.draw.polygon(interior, water, [local(camera.apply(x, y, z)) for x, y in corners])
        w, h = pit.x1 - pit.x0, pit.y1 - pit.y0
        for _ in range(int((w + h) * 1.6)):
            px, py = pit.x0 + rng.random() * w, pit.y0 + rng.random() * h
            phase = rng.uniform(0.0, 6.28)
            length = rng.uniform(0.5, 1.1)
            drift = 0.25 * math.sin(time_val * 1.6 + phase)
            level = 0.5 + 0.5 * math.sin(time_val * 2.4 + phase)
            crest = lerp(water, foam, 0.25 + 0.4 * level)
            a = camera.apply(px + drift, py, z + 0.02)
            b = camera.apply(px + drift + length, py, z + 0.02)
            pygame.draw.line(interior, crest, local(a), local(b), 2)
        # Espuma na linha d'água, encostada nas quatro paredes
        for (xa, ya), (xb, yb) in zip(corners, corners[1:] + corners[:1]):
            n = max(2, int(math.hypot(xb - xa, yb - ya) / 0.7))
            for i in range(n):
                t = (i + 0.5) / n
                fx, fy = xa + (xb - xa) * t, ya + (yb - ya) * t
                bob = 0.5 + 0.5 * math.sin(time_val * 2.0 + i * 1.7 + fx)
                r = 3 + int(2 * bob)
                pygame.draw.circle(interior, lerp(water, foam, 0.55 + 0.3 * bob), local(camera.apply(fx, fy, z + 0.03)), r)

    @staticmethod
    def _draw_flat(surface, camera, style: TileStyle, x: int, y: int, quad: list):
        pygame.draw.polygon(surface, style.color_at(x, y), quad)
        if style.edge:
            pygame.draw.polygon(surface, style.edge, quad, 1)
        decor = style.decor
        if decor and (x + y) % 2 == decor.parity:
            draw_voxel_box(surface, camera, x + decor.inset, y + decor.inset, 0.0,
                           decor.size, decor.size, decor.height, decor.color, outline=True)

    @staticmethod
    def _draw_slab(surface, camera, style: TileStyle, x: int, y: int):
        draw_voxel_box(surface, camera, x, y, 0.0, 1.0, 1.0, style.height, style.color_at(x, y), outline=style.outline)
        if style.top_edge:
            top = [camera.apply(x, y, style.height), camera.apply(x + 1, y, style.height),
                   camera.apply(x + 1, y + 1, style.height), camera.apply(x, y + 1, style.height)]
            pygame.draw.polygon(surface, style.top_edge, top, 1)

    def _draw_water(self, surface, camera, style: TileStyle, x: int, y: int, quad: list, time_val: float, reflect: bool):
        p_top, p_right, p_bottom, p_left = quad
        z = -style.depth
        w_top = camera.apply(x, y, z)
        w_right = camera.apply(x + 1, y, z)
        w_bottom = camera.apply(x + 1, y + 1, z)
        w_left = camera.apply(x, y + 1, z)

        # A parede do barranco fica entre a terra firme vizinha e a água; só as voltadas para a câmera aparecem
        banks = {(0, -1): (p_top, p_right, w_right, w_top), (-1, 0): (p_left, p_top, w_top, w_left),
                 (1, 0): (p_right, p_bottom, w_bottom, w_right), (0, 1): (p_bottom, p_left, w_left, w_bottom)}
        for (ndx, ndy), bank in banks.items():
            nx, ny = x + ndx, y + ndy
            if not (0 <= nx < self.cols and 0 <= ny < self.rows):
                continue
            if self.style_at(nx, ny).water_like:
                continue
            colors = style.bank_ew if ndx != 0 else style.bank_ns
            if colors is None:
                continue
            face_x, face_y = rotate_xy(-ndx, -ndy, camera.azimuth)
            if face_x + face_y <= 1e-6:
                continue
            pygame.draw.polygon(surface, colors[0], list(bank))
            pygame.draw.polygon(surface, colors[1], list(bank), 1)

        wave = math.sin(time_val * 3.0 + x * 0.9 + y * 0.9)
        surface_color = style.colors[1] if (wave > 0.45 and len(style.colors) > 1) else style.colors[0]
        w_quad = [w_top, w_right, w_bottom, w_left]
        pygame.draw.polygon(surface, surface_color, w_quad)
        if style.edge:
            pygame.draw.polygon(surface, style.edge, w_quad, 1)
        if reflect:
            pygame.draw.circle(surface, (120, 205, 240, 180), camera.apply(x + 0.5, y + 0.5, z + 0.01), 8)
