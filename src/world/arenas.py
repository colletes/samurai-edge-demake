"""
Registro das arenas do jogo e seus `ArenaSpec` (Entregável 6.2).

Aqui ficam os dados de cada arena e o registro dos tipos de prop, estrutura e perigo que o motor
(`arena_generator.py`) sabe instanciar. Novas arenas (Entregável 6.3) são só novos specs.
"""
from src.config import (
    ARENA_BAMBOO, ARENA_KYOTO, ARENA_GANRYU, ARENA_IGA, ARENA_PIRATE_DECK, ARENA_SHADOW_CAVE, ARENA_MIST_TEMPLE, ARENA_FOREST_CAMP, ARENA_NAGASHINO, ARENA_KABUKI_STAGE, ARENA_MOUNTAIN_SHRINE, ARENA_BAROQUE_COURT, ARENA_GASHADOKURO, COLOR_BG, COLOR_KYOTO_BG,
    COLOR_GRASS, COLOR_GRASS_LIGHT, COLOR_EARTH, COLOR_WATER, COLOR_WATER_HIGHLIGHT,
    COLOR_KYOTO_STONE, COLOR_KYOTO_STONE_LIGHT, COLOR_KYOTO_STONE_DARK, COLOR_KYOTO_CURB, COLOR_KYOTO_PAVEMENT,
    MAP_COLS, MAP_ROWS,
)
from src.world.arena_generator import (
    ArenaMap, ArenaSpec, AtmosphereEffect, WindSpec, CheckerLayer, EllipseLayer, FillLayer, HazardSpec, LightingEnvironment,
    LightSource, PitZone, PropSpec, RectLayer, RoofSlope, ScatterSpec, SpawnRule, StageSpec, StoneDecor, StructureSpec, TileStyle,
    register_hazard, register_prop, register_structure,
)
from src.world.bamboo import Bamboo
from src.world.decor import (
    Bunting, Campfire, ForestTree, HangingChain, IncenseBurner, JizoStatue, KoiFish, MistBank, NoboriBanner, PaperLantern,
    ArcheryTarget, Fountain, HedgeBlock, MarbleStatue, PineTree, ScreenPanel, SnareTrap, StripedCurtain, SupplyCrate,
)
from src.world.hazards import ChainPendulum, FireworkMortars, RotatingStage, ShipRoll, TideSurge
from src.world.solid_props import Cannon, PowderBarrel, ShrineBell, SolidProp
from src.world.kyoto_map import (
    CarriageTraffic, DebrisRain, KyotoLantern, MachiyaFacade,
    TILE_KYOTO_STREET, TILE_KYOTO_STREET_ALT, TILE_KYOTO_CURB, TILE_KYOTO_SIDEWALK, TILE_KYOTO_BUILDING,
)
from src.world.map_data import TILE_GRASS, TILE_EARTH, TILE_WATER, TILE_BRIDGE
from src.world.obstacles import AncientTree, Rock, StoneLantern, ToriiGate, Tsukubai
from src.world.structures import ArchedBridge, PlankBridge, RoofBeam

# ---------------------------------------------------------------------------
# Registros de tipos
# ---------------------------------------------------------------------------
register_prop("rock", lambda x, y, **p: Rock(x, y, **p), "rocks")
register_prop("tree", lambda x, y, **p: AncientTree(x, y), "trees")
register_prop("torii", lambda x, y, **p: ToriiGate(x, y), "torii_gates")
register_prop("stone_lantern", lambda x, y, **p: StoneLantern(x, y), "lanterns")
register_prop("kyoto_lantern", lambda x, y, **p: KyotoLantern(x, y), "lanterns")
register_prop("tsukubai", lambda x, y, **p: Tsukubai(x, y), "well", single=True)
register_prop("machiya", lambda x, y, **p: MachiyaFacade(wx=x, wy=y, **p), "buildings")
register_prop("bamboo", lambda x, y, **p: Bamboo(x, y), "bamboos")
register_prop("boat", lambda x, y, **p: SolidProp(x, y, style="boat", **p), "buildings")
register_prop("solid_block", lambda x, y, **p: SolidProp(x, y, **p), "buildings")
register_prop("mast", lambda x, y, **p: SolidProp(x, y, style="mast", **p), "buildings")
register_prop("dojo", lambda x, y, **p: SolidProp(x, y, style="dojo", **p), "buildings")
register_prop("guard_post", lambda x, y, **p: SolidProp(x, y, style="guardpost", **p), "buildings")
register_prop("paper_lantern", lambda x, y, **p: PaperLantern(x, y, **p), "lanterns")
register_prop("bunting", lambda x, y, **p: Bunting(x, y, **p), "lanterns")
register_prop("nobori", lambda x, y, **p: NoboriBanner(x, y, **p), "lanterns")
register_prop("incense", lambda x, y, **p: IncenseBurner(x, y), "lanterns")
register_prop("jizo", lambda x, y, **p: JizoStatue(x, y), "rocks")
register_prop("hanging_chain", lambda x, y, **p: HangingChain(x, y, **p), "lanterns")
register_prop("pillar", lambda x, y, **p: SolidProp(x, y, style="pillar", **p), "buildings")
register_prop("pine", lambda x, y, **p: PineTree(x, y), "trees")
register_prop("koi", lambda x, y, **p: KoiFish(x, y, **p), "lanterns")
register_prop("mist", lambda x, y, **p: MistBank(x, y, **p), "lanterns")
register_prop("forest_tree", lambda x, y, **p: ForestTree(x, y), "trees")
register_prop("crate", lambda x, y, **p: SupplyCrate(x, y), "rocks")
register_prop("campfire", lambda x, y, **p: Campfire(x, y), "lanterns")
register_prop("snare", lambda x, y, **p: SnareTrap(x, y), "lanterns")
register_prop("cabin", lambda x, y, **p: SolidProp(x, y, style="cabin", **p), "buildings")
register_prop("tent", lambda x, y, **p: SolidProp(x, y, style="tent", **p), "buildings")
register_prop("powder_barrel", lambda x, y, **p: PowderBarrel(x, y, **p), "buildings")
register_prop("palisade", lambda x, y, **p: SolidProp(x, y, style="palisade", **p), "buildings")
register_prop("screen_panel", lambda x, y, **p: ScreenPanel(x, y, **p), "rocks")
register_prop("curtain", lambda x, y, **p: StripedCurtain(x, y, **p), "lanterns")
register_prop("archery_target", lambda x, y, **p: ArcheryTarget(x, y), "rocks")
register_prop("shrine_bell", lambda x, y, **p: ShrineBell(x, y), "buildings")
register_prop("hedge", lambda x, y, **p: HedgeBlock(x, y), "rocks")
register_prop("marble_statue", lambda x, y, **p: MarbleStatue(x, y), "rocks")
register_prop("fountain", lambda x, y, **p: Fountain(x, y), "rocks")
register_prop("barrel", lambda x, y, **p: SolidProp(x, y, style="barrel", **p), "buildings")
register_prop("cannon", lambda x, y, **p: Cannon(x, y, **p), "buildings")
register_structure("arched_bridge", ArchedBridge)
register_structure("roof_beam", RoofBeam)
register_structure("plank_bridge", PlankBridge)
register_hazard("carriage_traffic", CarriageTraffic)
register_hazard("debris_rain", DebrisRain)
register_hazard("tide_surge", TideSurge)
register_hazard("ship_roll", ShipRoll)
register_hazard("chain_pendulum", ChainPendulum)
register_hazard("firework_mortars", FireworkMortars)
register_hazard("rotating_stage", RotatingStage)

# ---------------------------------------------------------------------------
# Floresta de Bambu
# ---------------------------------------------------------------------------
TILE_KARESANSUI = 30  # jardim de pedras rastelado (cascalho claro em fileiras)
_BAMBOO_LANTERNS = ((8.8, 6.2), (12.2, 6.2), (8.8, 15.8), (12.2, 15.8), (5.8, 7.8))
_BAMBOO_FIREFLIES = (
    (10.2, 11.8, 0.7), (11.8, 12.5, 0.5), (8.5, 10.2, 0.3),
    (12.5, 9.5, 0.6), (7.8, 7.8, 0.8), (11.0, 6.2, 0.9), (6.2, 6.8, 0.6),
)

BAMBOO_SPEC = ArenaSpec(
    id=ARENA_BAMBOO,
    name="Floresta de Bambu",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=COLOR_BG,
    music="bgm_bamboo",
    wind=WindSpec(1, 0.4, 0.55, 0.5),
    tile_styles={
        TILE_GRASS: TileStyle("flat", (COLOR_GRASS, COLOR_GRASS_LIGHT), pattern="third", edge=(28, 44, 24), surface="grass"),
        TILE_EARTH: TileStyle("flat", (COLOR_EARTH,), edge=(44, 34, 22), decor=StoneDecor((88, 92, 95)), surface="dirt"),
        TILE_WATER: TileStyle("water", (COLOR_WATER, COLOR_WATER_HIGHLIGHT), edge=(14, 48, 72), depth=0.15, speed_mult=0.55,
                              bank_ns=((36, 26, 18), (22, 16, 12)), bank_ew=((46, 32, 22), (28, 20, 14)), surface="water"),
        TILE_BRIDGE: TileStyle("anchor", surface="wood"),
        TILE_KARESANSUI: TileStyle("flat", ((204, 198, 184), (176, 170, 156)), pattern="rows", edge=(132, 126, 114), surface="gravel"),
    },
    layers=(
        FillLayer(TILE_GRASS),
        EllipseLayer(TILE_WATER, cx=11.0, cy=11.0, radius=4.2, sx=1.12, sy=0.90),
        RectLayer(TILE_BRIDGE, 10, 11, 7, 15),
        # Estrada de terra batida ligada às duas pontas da ponte (entrada norte passando pelo Torii e entrada sul)
        RectLayer(TILE_EARTH, 10, 11, 0, 7),
        RectLayer(TILE_EARTH, 9, 12, 6, 7),
        RectLayer(TILE_EARTH, 10, 11, 15, 21),
        RectLayer(TILE_EARTH, 9, 12, 15, 16),
        # Caminho secundário contornando o lago até o lavatório Tsukubai
        RectLayer(TILE_EARTH, 6, 10, 6, 7, skip=(TILE_WATER, TILE_BRIDGE)),
        RectLayer(TILE_EARTH, 6, 7, 6, 9),
        # Karesansui: cascalho rastelado diante do dojo
        RectLayer(TILE_KARESANSUI, 1, 5, 5, 8),
    ),
    props=(
        PropSpec("dojo", 0.6, 0.6, {"width": 4.6, "depth": 3.6, "height": 1.7}),
        PropSpec("rock", 2.3, 6.2, {"radius": 0.5, "height": 0.7}),
        PropSpec("rock", 4.3, 7.4, {"radius": 0.42, "height": 0.55}),
        PropSpec("tsukubai", 6.5, 6.5),
        PropSpec("rock", 6.0, 14.5, {"radius": 0.7, "height": 0.9}),
        PropSpec("rock", 15.5, 7.0, {"radius": 0.6, "height": 0.8}),
        PropSpec("rock", 16.0, 15.0, {"radius": 0.75, "height": 1.0}),
        PropSpec("rock", 3.5, 10.0, {"radius": 0.55, "height": 0.75}),
        PropSpec("tree", 17.5, 17.5),
        PropSpec("torii", 10.5, 5.0),
    ) + tuple(PropSpec("stone_lantern", x, y) for x, y in _BAMBOO_LANTERNS),
    scatters=(
        ScatterSpec(
            "bamboo", seed=42, blocked_tiles=(TILE_WATER, TILE_BRIDGE, TILE_EARTH),
            clearances=(("rocks", 1.3), ("well", 1.4), ("trees", 2.6), ("torii_gates", 1.6), ("lanterns", 0.8)),
            center=(11.0, 11.0), inner_radius=5.0, density_inner=0.25, density_outer=0.72, jitter=0.35,
            cleared=((0.0, 0.0, 6.0, 5.0), (1.0, 5.0, 6.0, 9.0)),  # dojo e karesansui sem bambu
        ),
    ),
    drift_petals=0.65,
    structures=(StructureSpec("arched_bridge", TILE_BRIDGE, {"x0": 10.0, "width": 2.0, "y_start": 7, "y_end": 16}),),
    spawns=SpawnRule(margin=3.0, min_distance=7.0, check_obstacles=True, fallback=((10.5, 7.0), (10.5, 15.0))),
    stage=StageSpec(11.0, 11.5, structure=0),
    reflections=((11, 11), (11, 12), (10, 12)),
    lighting=LightingEnvironment(
        ambient_color=(120, 150, 170), ambient_strength=0.35, vignette=0.25,
        lights=tuple(LightSource(x, y, 0.9, (255, 200, 120), 3.0, flicker=0.10) for x, y in _BAMBOO_LANTERNS),
        atmosphere=(AtmosphereEffect("fireflies", density=1.0, points=_BAMBOO_FIREFLIES),),
    ),
)

# ---------------------------------------------------------------------------
# Kyoto Bakumatsu
# ---------------------------------------------------------------------------
_KYOTO_FACADE_ROWS = (0.4, 3.9, 7.4, 10.9, 14.4, 17.9)
_KYOTO_LANTERN_ROWS = (3.0, 8.5, 14.0, 19.5)
_KYOTO_LANTERNS = tuple(p for ly in _KYOTO_LANTERN_ROWS for p in ((7.30, ly), (14.25, ly)))
_KYOTO_PAPER_ROWS = (5.75, 11.25, 16.75)
_KYOTO_PAPER_LANTERNS = tuple(p for ly in _KYOTO_PAPER_ROWS for p in ((7.35, ly), (14.2, ly)))

KYOTO_SPEC = ArenaSpec(
    id=ARENA_KYOTO,
    name="Kyoto: Bakumatsu em Chamas",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=COLOR_KYOTO_BG,
    music="bgm_kyoto",
    wind=WindSpec(1, 0.3, 0.3, 0.4),
    tile_styles={
        TILE_KYOTO_STREET: TileStyle("flat", (COLOR_KYOTO_STONE, COLOR_KYOTO_STONE_LIGHT), pattern="parity", edge=COLOR_KYOTO_STONE_DARK, surface="stone"),
        TILE_KYOTO_STREET_ALT: TileStyle("flat", ((54, 50, 52),), edge=COLOR_KYOTO_STONE_DARK, surface="stone"),
        TILE_KYOTO_CURB: TileStyle("slab", (COLOR_KYOTO_CURB,), height=0.10, outline=True, surface="stone"),
        TILE_KYOTO_SIDEWALK: TileStyle("slab", (COLOR_KYOTO_PAVEMENT,), height=0.08, outline=False, top_edge=(38, 34, 36), surface="stone"),
        TILE_KYOTO_BUILDING: TileStyle("flat", ((20, 15, 17),), surface="stone"),
    },
    layers=(
        FillLayer(TILE_KYOTO_BUILDING),
        RectLayer(TILE_KYOTO_SIDEWALK, 7, 7),
        RectLayer(TILE_KYOTO_SIDEWALK, 14, 14),
        RectLayer(TILE_KYOTO_CURB, 8, 8),
        RectLayer(TILE_KYOTO_CURB, 13, 13),
        CheckerLayer(TILE_KYOTO_STREET, TILE_KYOTO_STREET_ALT, 9, 12),
    ),
    props=(
        # Canto noroeste: machiyas opacas; canto sudeste: machiyas translúcidas (ambas em chamas)
        tuple(PropSpec("machiya", 2.4, by, {"width": 4.4, "depth": 3.3, "is_transparent": False, "seed": 100 + i * 37})
              for i, by in enumerate(_KYOTO_FACADE_ROWS))
        + tuple(PropSpec("machiya", 15.0, by, {"width": 4.4, "depth": 3.3, "is_transparent": True, "seed": 200 + i * 43})
                for i, by in enumerate(_KYOTO_FACADE_ROWS))
        + tuple(PropSpec("kyoto_lantern", x, y) for x, y in _KYOTO_LANTERNS)
        # Shinsengumi: lanternas vermelhas, faixas azul-claro e branco do haori, banners, posto de guarda e incenso
        + tuple(PropSpec("paper_lantern", x, y) for x, y in _KYOTO_PAPER_LANTERNS)
        + tuple(PropSpec("bunting", 7.35, ly, {"x1": 14.2, "y1": ly}) for ly in _KYOTO_PAPER_ROWS)
        + (
            PropSpec("nobori", 8.55, 8.5, {"text": "誠"}),
            PropSpec("nobori", 13.45, 14.0, {"text": "誠"}),
            PropSpec("nobori", 13.45, 8.5, {"text": "悪即斬", "cloth": (34, 32, 40)}),
            PropSpec("nobori", 8.55, 14.0, {"text": "悪即斬", "cloth": (34, 32, 40)}),
            PropSpec("guard_post", 13.55, 12.3, {"width": 1.35, "depth": 1.5, "height": 1.5}),
            PropSpec("incense", 7.65, 8.9),
            PropSpec("incense", 14.1, 10.6),
        )
    ),
    hazards=(
        HazardSpec("carriage_traffic", {"initial_timer": 2.5, "interval": (4.0, 6.5), "speed": 14.0}),
        HazardSpec("debris_rain", {"initial_timer": 1.2, "interval": (1.2, 2.4)}),
    ),
    # Faixa real caminhável (calçadas + meio-fio + rua): impede atravessar as fachadas das machiyas
    playable_bounds=(7.0, 1.0, 14.9, MAP_ROWS - 1.0),
    spawns=SpawnRule(x_range=(9.5, 11.5), y_margin=4.0, min_distance=7.0, check_obstacles=False,
                     outer_attempts=150, inner_attempts=30, fallback=((10.5, 6.0), (10.5, 15.0))),
    stage=StageSpec(11.0, MAP_ROWS / 2.0),
    lighting=LightingEnvironment(
        ambient_color=(90, 50, 40), ambient_strength=0.45, vignette=0.35,
        lights=tuple(LightSource(x, y, 0.9, (255, 170, 80), 3.5, flicker=0.25) for x, y in _KYOTO_LANTERNS)
        + tuple(LightSource(x, y, 1.4, (255, 90, 60), 2.6, flicker=0.2) for x, y in _KYOTO_PAPER_LANTERNS),
        atmosphere=(AtmosphereEffect("embers", density=0.8), AtmosphereEffect("smoke", density=0.3),
                    AtmosphereEffect("incense", density=0.4, points=((7.65, 8.9, 0.8), (14.1, 10.6, 0.8)))),
    ),
)

# ---------------------------------------------------------------------------
# Ilha de Ganryū (Musashi) — arena piloto do motor de arenas temáticas (6.3.2)
# ---------------------------------------------------------------------------
TILE_GRAVEL = 20
TILE_WET_SAND = 21
TILE_SEA = 22
TILE_PLANK = 23

_GANRYU_LANTERNS = ((10.2, 8.2), (13.8, 8.2), (10.2, 14.8), (13.8, 14.8))

GANRYU_SPEC = ArenaSpec(
    id=ARENA_GANRYU,
    name="Ilha de Ganryū",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(30, 36, 44),
    music="bgm_ganryu_island",
    wind=WindSpec(-1, 0.3, 1.1, 0.6),
    tile_styles={
        TILE_GRAVEL: TileStyle("flat", ((122, 118, 110), (108, 104, 98)), pattern="parity", edge=(88, 84, 78), surface="gravel"),
        TILE_WET_SAND: TileStyle("flat", ((96, 88, 76),), edge=(76, 70, 60), speed_mult=0.8, surface="wet_sand"),
        TILE_SEA: TileStyle("water", ((52, 86, 104), (96, 138, 154)), edge=(30, 56, 72), depth=0.12, speed_mult=0.55, surface="water"),
        TILE_PLANK: TileStyle("anchor", surface="wood"),
    },
    layers=(
        FillLayer(TILE_GRAVEL),
        RectLayer(TILE_WET_SAND, 2, 3, 0, MAP_ROWS - 1),
        RectLayer(TILE_WET_SAND, 4, 18, 9, 9),
        RectLayer(TILE_WET_SAND, 4, 18, 13, 13),
        RectLayer(TILE_SEA, 0, 1, 0, MAP_ROWS - 1),
        RectLayer(TILE_SEA, 2, 18, 10, 12),
        RectLayer(TILE_PLANK, 11, 12, 10, 12),
    ),
    props=(
        PropSpec("boat", 2.8, 18.2, {"width": 3.4, "depth": 1.4, "height": 0.6, "color": (110, 80, 54)}),
        PropSpec("rock", 12.5, 4.5, {"radius": 0.7, "height": 0.9}),
        PropSpec("rock", 16.5, 18.5, {"radius": 0.75, "height": 1.0}),
        PropSpec("rock", 3.8, 6.5, {"radius": 0.6, "height": 0.8}),
    ) + tuple(PropSpec("stone_lantern", x, y) for x, y in _GANRYU_LANTERNS),
    structures=(StructureSpec("plank_bridge", TILE_PLANK, {"x0": 11.0, "width": 2.0, "y_start": 9, "y_end": 14}),),
    hazards=(HazardSpec("tide_surge", {"x_from": 0.0, "x_to": float(MAP_COLS), "band_width": 3.2, "sweep_speed": 6.5,
                                       "push_speed": 4.0, "warn_time": 2.4, "interval": (7.0, 10.0), "initial_delay": 5.0}),),
    # Fendas de rocha de largura crescente (S, M, L) e o penhasco a leste, onde a maré empurra
    pits=(
        PitZone(6.0, 3.0, 7.0, 8.0, "S"),
        PitZone(14.0, 2.5, 15.48, 7.5, "M"),
        PitZone(8.0, 15.0, 10.08, 19.0, "L"),
        PitZone(18.4, 5.0, float(MAP_COLS), 17.0, "VOID", railed=True),
    ),
    spawns=SpawnRule(x_range=(4.0, 17.0), margin=3.0, min_distance=7.0, fallback=((4.5, 14.0), (16.0, 14.0))),
    stage=StageSpec(12.0, 11.0, structure=0),
    lighting=LightingEnvironment(
        ambient_color=(150, 160, 172), ambient_strength=0.55, vignette=0.30,
        lights=tuple(LightSource(x, y, 0.9, (255, 214, 150), 2.5, flicker=0.12) for x, y in _GANRYU_LANTERNS),
        atmosphere=(AtmosphereEffect("fog", density=0.8),),
    ),
)

# ---------------------------------------------------------------------------
# Telhados de Iga (Hanzo) — 6.3.4
# ---------------------------------------------------------------------------
TILE_ROOF = 24
TILE_RIDGE = 25
TILE_BEAM = 26
TILE_ROOF_PATINA = 28
TILE_ROOF_RED = 29
TILE_ROOF_R = 31  # vertente oposta ao sol de cada telhado (mais escura)
TILE_ROOF_PATINA_R = 32
TILE_ROOF_RED_R = 33
_IGA_WALL = dict(depth=2.2, floor_color=(6, 8, 14), wall_colors=((146, 128, 100), (16, 14, 20)), rim_color=(58, 62, 80))
_IGA_CRACK = dict(depth=1.6, floor_color=(8, 8, 14), wall_colors=((120, 104, 84), (14, 12, 18)), rim_color=(40, 30, 30))

_IGA_LANTERNS = ((0.8, 1.6), (5.2, 20.2), (9.2, 20.2), (13.2, 1.6), (21.0, 2.6), (17.4, 20.2))

IGA_SPEC = ArenaSpec(
    id=ARENA_IGA,
    name="Telhados de Iga",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(16, 20, 32),
    music="bgm_iga_rooftops",
    wind=WindSpec(1, -0.3, 0.8, 0.7),
    tile_styles={
        TILE_ROOF: TileStyle("flat", ((84, 94, 120), (66, 76, 100)), pattern="rows", edge=(40, 46, 64), surface="roof"),
        TILE_ROOF_PATINA: TileStyle("flat", ((76, 108, 108), (60, 90, 92)), pattern="rows", edge=(34, 52, 56), surface="roof"),
        TILE_ROOF_RED: TileStyle("flat", ((126, 78, 70), (104, 62, 58)), pattern="rows", edge=(58, 34, 32), surface="roof"),
        TILE_ROOF_R: TileStyle("flat", ((60, 68, 90), (48, 56, 76)), pattern="rows", edge=(30, 34, 50), surface="roof"),
        TILE_ROOF_PATINA_R: TileStyle("flat", ((52, 78, 80), (42, 64, 66)), pattern="rows", edge=(26, 42, 46), surface="roof"),
        TILE_ROOF_RED_R: TileStyle("flat", ((92, 56, 52), (76, 46, 44)), pattern="rows", edge=(44, 26, 26), surface="roof"),
        TILE_RIDGE: TileStyle("slab", ((100, 104, 128),), height=0.16, outline=True, surface="roof"),
        TILE_BEAM: TileStyle("anchor", surface="wood"),
    },
    layers=(
        FillLayer(TILE_ROOF),
        RectLayer(TILE_ROOF_R, 4, 5),
        RectLayer(TILE_ROOF_PATINA, 8, 10),
        RectLayer(TILE_ROOF_PATINA_R, 11, 13),
        RectLayer(TILE_ROOF_RED, 16, 19),
        RectLayer(TILE_ROOF_RED_R, 20, 21),
        # Cumeeira de cada telhado (oeste, centro e leste)
        RectLayer(TILE_RIDGE, 3, 3, 0, MAP_ROWS - 1),
        RectLayer(TILE_RIDGE, 10, 10, 0, MAP_ROWS - 1),
        RectLayer(TILE_RIDGE, 19, 19, 0, MAP_ROWS - 1),
        # Piso das duas vigas: o convés da viga cobre o vão
        RectLayer(TILE_BEAM, 6, 7, 14, 15),
        RectLayer(TILE_BEAM, 14, 16, 6, 7),
    ),
    props=(
        PropSpec("solid_block", 1.2, 9.0, {"width": 0.9, "depth": 0.9, "height": 1.2, "color": (76, 66, 62)}),
        PropSpec("solid_block", 20.0, 11.0, {"width": 0.9, "depth": 0.9, "height": 1.2, "color": (76, 66, 62)}),
        PropSpec("solid_block", 12.0, 17.0, {"width": 0.9, "depth": 0.9, "height": 1.1, "color": (84, 72, 64)}),
        PropSpec("rock", 9.4, 3.0, {"radius": 0.45, "height": 0.5}),
        PropSpec("rock", 20.6, 20.4, {"radius": 0.5, "height": 0.55}),
    ) + tuple(PropSpec("kyoto_lantern", x, y) for x, y in _IGA_LANTERNS),
    # Vigas sobre os becos: a rota sem salto entre os telhados
    structures=(
        StructureSpec("roof_beam", TILE_BEAM, {"x0": 5.75, "y0": 14.0, "x1": 8.33, "y1": 16.0}),
        StructureSpec("roof_beam", TILE_BEAM, {"x0": 13.75, "y0": 6.0, "x1": 17.07, "y1": 8.0}),
    ),
    # Becos L (esquivas ágeis) e J (salto do Hanzo, Shukuchi do Kenshi) cortados pelas vigas, mais rachaduras S e M
    pits=(
        PitZone(6.0, 0.0, 8.08, 14.0, "L", **_IGA_WALL),
        PitZone(6.0, 16.0, 8.08, 22.0, "L", **_IGA_WALL),
        PitZone(14.0, 0.0, 16.82, 6.0, "J", **_IGA_WALL),
        PitZone(14.0, 8.0, 16.82, 22.0, "J", **_IGA_WALL),
        PitZone(8.08, 5.0, 10.4, 6.0, "S", **_IGA_CRACK),
        PitZone(1.0, 16.0, 2.0, 20.0, "S", **_IGA_CRACK),
        PitZone(19.6, 17.0, 22.0, 18.48, "M", **_IGA_CRACK),
    ),
    # Telhados de duas águas: sobem das beiradas (junto aos becos) até a cumeeira
    slopes=(RoofSlope(0.0, 6.0, 3.5, 1.1), RoofSlope(8.08, 14.0, 10.5, 1.1), RoofSlope(16.82, 22.0, 19.5, 1.1)),
    spawns=SpawnRule(x_range=(1.0, 21.0), margin=2.0, min_distance=7.0, min_pit_distance=1.1, fallback=((3.0, 11.0), (19.5, 12.0))),
    stage=StageSpec(11.0, 11.0),
    lighting=LightingEnvironment(
        ambient_color=(96, 110, 150), ambient_strength=0.40, vignette=0.35,
        lights=tuple(LightSource(x, y, 1.0, (255, 190, 110), 3.0, flicker=0.15) for x, y in _IGA_LANTERNS),
        atmosphere=(AtmosphereEffect("fog", density=0.5),),
    ),
)

# ---------------------------------------------------------------------------
# Convés na Tempestade (Anne) — 6.3.5
# ---------------------------------------------------------------------------
TILE_DECK = 27

_SEA_PIT = dict(depth=1.9, floor_color=(18, 52, 70), wall_colors=((96, 68, 46), (22, 54, 68)), rim_color=(108, 76, 50),
                water=((24, 70, 92), (196, 224, 234)))
_HOLE_PIT = dict(depth=1.6, floor_color=(6, 12, 18), wall_colors=((96, 68, 46), (10, 14, 20)), rim_color=(96, 68, 46))
_PIRATE_LANTERNS = ((7.9, 10.0), (14.7, 10.0), (1.2, 4.6), (20.8, 17.4))

PIRATE_SPEC = ArenaSpec(
    id=ARENA_PIRATE_DECK,
    name="Convés na Tempestade",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(14, 24, 34),
    music="bgm_pirate_deck",
    wind=WindSpec(1, 0.6, 1.8, 0.9),
    tile_styles={
        TILE_DECK: TileStyle("flat", ((124, 92, 64), (110, 80, 56)), pattern="parity", edge=(64, 44, 30), surface="wood"),
    },
    layers=(FillLayer(TILE_DECK),),
    drift_count=0,
    props=(
        PropSpec("mast", 7.6, 10.7, {"width": 0.6, "depth": 0.6, "height": 3.4, "color": (112, 80, 52)}),
        PropSpec("mast", 14.4, 10.7, {"width": 0.6, "depth": 0.6, "height": 3.4, "color": (112, 80, 52)}),
        PropSpec("cannon", 1.0, 12.0, {"facing": (1.0, 0.0)}),
        PropSpec("cannon", 19.5, 8.5, {"facing": (-1.0, 0.0)}),
        PropSpec("barrel", 3.0, 4.6, {"width": 0.7, "depth": 0.7, "height": 0.8, "color": (104, 70, 44)}),
        PropSpec("barrel", 3.9, 4.9, {"width": 0.7, "depth": 0.7, "height": 0.8, "color": (96, 64, 42)}),
        PropSpec("barrel", 17.6, 16.6, {"width": 0.7, "depth": 0.7, "height": 0.8, "color": (104, 70, 44)}),
        PropSpec("barrel", 18.5, 16.9, {"width": 0.7, "depth": 0.7, "height": 0.8, "color": (96, 64, 42)}),
        PropSpec("barrel", 9.0, 16.6, {"width": 0.7, "depth": 0.7, "height": 0.8, "color": (104, 70, 44)}),
        PropSpec("solid_block", 19.8, 4.6, {"width": 0.9, "depth": 0.9, "height": 0.7, "color": (118, 92, 62)}),
        PropSpec("solid_block", 1.2, 16.6, {"width": 0.9, "depth": 0.9, "height": 0.7, "color": (118, 92, 62)}),
    ),
    hazards=(HazardSpec("ship_roll", {"push_speed": 3.4, "warn_time": 2.2, "active_time": 1.3, "interval": (7.0, 10.0),
                                      "initial_delay": 5.0, "x_range": (0.0, float(MAP_COLS)), "y_center": 11.0}),),
    # Mar além das amurada (corda e estacas: só cai quem é empurrado) e tábuas quebradas S, M e L
    pits=(
        PitZone(0.0, 0.0, float(MAP_COLS), 4.0, "VOID", railed=True, **_SEA_PIT),
        PitZone(0.0, 18.0, float(MAP_COLS), float(MAP_ROWS), "VOID", railed=True, **_SEA_PIT),
        PitZone(5.0, 7.0, 6.0, 10.0, "S", **_HOLE_PIT),
        PitZone(12.0, 13.0, 13.48, 16.0, "M", **_HOLE_PIT),
        PitZone(16.0, 6.0, 18.08, 8.5, "L", **_HOLE_PIT),
    ),
    spawns=SpawnRule(x_range=(2.0, 20.0), margin=5.0, min_distance=7.0, fallback=((3.5, 13.5), (18.5, 12.5))),
    stage=StageSpec(11.0, 12.5),
    lighting=LightingEnvironment(
        ambient_color=(70, 92, 112), ambient_strength=0.40, vignette=0.40,
        lights=tuple(LightSource(x, y, 1.6, (255, 190, 100), 3.2, flicker=0.30) for x, y in _PIRATE_LANTERNS),
        atmosphere=(AtmosphereEffect("rain", density=1.0), AtmosphereEffect("fog", density=0.3)),
    ),
)

# ---------------------------------------------------------------------------
# Gruta das Sombras (Murasaki) — 6.3.7
# ---------------------------------------------------------------------------
TILE_CAVE_ROCK = 34
TILE_CAVE_FLOOR = 35
TILE_RITUAL = 36
TILE_CAVE_RING = 37  # anel magenta gasto no piso, como na arte de conceito

_CAVE_JIZO = ((15.49, 12.57), (12.57, 15.49), (8.43, 15.49), (5.51, 12.57), (5.51, 8.43), (8.43, 5.51), (12.57, 5.51), (15.49, 8.43))  # roda de Jizo em volta do círculo ritual
_CAVE_LANTERNS = ((8.6, 5.0), (13.4, 5.0), (8.6, 17.0), (13.4, 17.0))
_CAVE_CHAINS = ((3.0, 9.0), (3.0, 13.0), (19.0, 9.0), (19.0, 13.0), (9.0, 3.0), (13.0, 3.0), (9.0, 19.0), (13.0, 19.0))
_CAVE_PILLARS = ((3.6, 3.6), (17.5, 3.6), (3.6, 17.5), (17.5, 17.5))

SHADOW_CAVE_SPEC = ArenaSpec(
    id=ARENA_SHADOW_CAVE,
    name="Gruta das Sombras",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(12, 8, 20),
    music="bgm_shadow_cave",
    wind=WindSpec(1, 0.2, 0.1, 0.3),
    tile_styles={
        TILE_CAVE_ROCK: TileStyle("flat", ((50, 40, 64), (44, 35, 58)), pattern="parity", edge=(26, 20, 36), surface="stone"),
        TILE_CAVE_FLOOR: TileStyle("flat", ((84, 70, 104), (76, 62, 96)), pattern="parity", edge=(46, 38, 62), surface="stone"),
        TILE_RITUAL: TileStyle("flat", ((136, 110, 156), (122, 98, 142)), pattern="parity", edge=(72, 56, 90), surface="stone"),
        TILE_CAVE_RING: TileStyle("flat", ((118, 52, 110), (104, 44, 98)), pattern="parity", edge=(70, 28, 66), surface="stone"),
    },
    layers=(
        FillLayer(TILE_CAVE_ROCK),
        EllipseLayer(TILE_CAVE_FLOOR, cx=10.5, cy=10.5, radius=9.4),
        EllipseLayer(TILE_CAVE_RING, cx=10.5, cy=10.5, radius=7.9),
        EllipseLayer(TILE_CAVE_FLOOR, cx=10.5, cy=10.5, radius=6.9),
        EllipseLayer(TILE_RITUAL, cx=10.5, cy=10.5, radius=3.6),
    ),
    props=(
        tuple(PropSpec("jizo", x, y) for x, y in _CAVE_JIZO)
        + tuple(PropSpec("pillar", x, y, {"width": 0.9, "depth": 0.9, "height": 2.8, "color": (66, 54, 82)}) for x, y in _CAVE_PILLARS)
        + tuple(PropSpec("stone_lantern", x, y) for x, y in _CAVE_LANTERNS)
        + tuple(PropSpec("hanging_chain", x, y, {"length": 2.4 + 0.5 * (i % 3)}) for i, (x, y) in enumerate(_CAVE_CHAINS))
    ),
    hazards=(HazardSpec("chain_pendulum", {}),),
    playable_bounds=(2.0, 2.0, 20.0, 20.0),
    spawns=SpawnRule(x_range=(4.0, 18.0), margin=4.0, min_distance=7.0, fallback=((5.0, 11.0), (17.0, 11.0))),
    stage=StageSpec(11.0, 11.0),
    drift_count=0,
    lighting=LightingEnvironment(
        ambient_color=(90, 70, 130), ambient_strength=0.35, vignette=0.45,
        lights=tuple(LightSource(x, y, 0.9, (176, 120, 255), 3.4, flicker=0.2) for x, y in _CAVE_LANTERNS),
        atmosphere=(AtmosphereEffect("mist", density=0.6),),
    ),
)

# ---------------------------------------------------------------------------
# Templo na Névoa (Kasumi) — 6.3.8
# ---------------------------------------------------------------------------
TILE_MIST_GRASS = 38
TILE_MIST_STONE = 39
TILE_MIST_PATH = 40
TILE_MIST_POND = 41

_MIST_LANTERNS = ((9.0, 6.0), (13.0, 6.0), (9.0, 12.0), (13.0, 12.0), (9.0, 18.0), (13.0, 18.0))
_MIST_PINES = ((2.0, 5.5), (20.0, 6.0), (2.0, 18.5), (20.0, 18.0))
_MIST_BANKS = ((4.5, 8.0), (16.5, 9.0), (8.0, 16.5), (17.0, 15.5), (11.0, 4.5), (3.5, 14.0), (13.5, 11.0), (10.0, 19.0))

MIST_TEMPLE_SPEC = ArenaSpec(
    id=ARENA_MIST_TEMPLE,
    name="Templo na Névoa",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(16, 24, 34),
    music="bgm_mist_temple",
    wind=WindSpec(1, 0.5, 0.6, 0.7),
    tile_styles={
        TILE_MIST_GRASS: TileStyle("flat", ((38, 58, 62), (34, 52, 58)), pattern="parity", edge=(24, 38, 42), surface="grass"),
        TILE_MIST_STONE: TileStyle("flat", ((96, 102, 118), (86, 92, 108)), pattern="parity", edge=(54, 60, 74), surface="stone"),
        TILE_MIST_PATH: TileStyle("flat", ((126, 132, 148), (116, 122, 138)), pattern="parity", edge=(76, 82, 98), surface="stone"),
        TILE_MIST_POND: TileStyle("water", ((36, 76, 100), (86, 140, 164)), edge=(18, 44, 62), depth=0.12, speed_mult=0.6,
                                  bank_ns=((60, 66, 80), (36, 40, 52)), bank_ew=((72, 78, 92), (44, 48, 60)), surface="water"),
    },
    layers=(
        FillLayer(TILE_MIST_GRASS),
        RectLayer(TILE_MIST_STONE, 3, 18, 4, 19),
        RectLayer(TILE_MIST_PATH, 10, 11, 4, 21),
        EllipseLayer(TILE_MIST_POND, cx=6.5, cy=13.5, radius=3.2),
    ),
    props=(
        PropSpec("dojo", 6.5, 0.4, {"width": 9.0, "depth": 3.3, "height": 2.0}),
        PropSpec("torii", 10.5, 20.2),
        PropSpec("koi", 6.5, 13.5, {"radius": 1.7, "speed": 0.55, "phase": 0.0}),
        PropSpec("koi", 6.5, 13.5, {"radius": 1.4, "speed": -0.45, "phase": 2.1, "color": (250, 244, 232)}),
        PropSpec("koi", 6.5, 13.5, {"radius": 1.9, "speed": 0.4, "phase": 4.0, "color": (240, 190, 60)}),
    ) + tuple(PropSpec("pine", x, y) for x, y in _MIST_PINES)
      + tuple(PropSpec("stone_lantern", x, y) for x, y in _MIST_LANTERNS)
      + tuple(PropSpec("mist", x, y, {"radius": 3.4}) for x, y in _MIST_BANKS),
    hazards=(HazardSpec("firework_mortars", {"circles": 3, "radius": 1.5, "bounds": (3.0, 5.0, 19.0, 19.0)}),),
    spawns=SpawnRule(x_range=(3.0, 19.0), margin=5.0, min_distance=7.0, fallback=((12.5, 7.5), (14.5, 16.5))),
    stage=StageSpec(11.0, 12.0),
    drift_count=24,
    drift_petals=0.8,
    lighting=LightingEnvironment(
        ambient_color=(110, 130, 170), ambient_strength=0.40, vignette=0.40,
        lights=tuple(LightSource(x, y, 0.9, (190, 220, 255), 3.0, flicker=0.1) for x, y in _MIST_LANTERNS),
        atmosphere=(AtmosphereEffect("fogbank", density=1.0), AtmosphereEffect("fireworks", density=0.5)),
    ),
)

# ---------------------------------------------------------------------------
# Acampamento na Floresta (Joe) — 6.3.9
# ---------------------------------------------------------------------------
TILE_FOREST_GRASS = 42
TILE_FOREST_DIRT = 43
TILE_FOREST_ROAD = 44

_FOREST_CRATES = ((8.0, 8.0), (14.0, 8.5), (8.5, 14.0), (14.5, 14.0), (11.0, 5.8), (11.0, 16.2))
_FOREST_SNARES = ((7.0, 11.5), (15.0, 11.0), (11.5, 8.8), (10.5, 13.5), (13.5, 5.5), (8.5, 17.0))
_FOREST_TREES = ((5.0, 1.8), (18.5, 2.0), (20.0, 8.5), (20.2, 13.0), (18.0, 20.0), (6.0, 20.0), (3.0, 12.5), (12.5, 2.0))

FOREST_CAMP_SPEC = ArenaSpec(
    id=ARENA_FOREST_CAMP,
    name="Acampamento na Floresta",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(126, 176, 210),
    music="bgm_forest_camp",
    wind=WindSpec(1, 0.5, 0.45, 0.5),
    tile_styles={
        TILE_FOREST_GRASS: TileStyle("flat", ((92, 152, 72), (84, 142, 66)), pattern="third", edge=(66, 116, 52), surface="grass"),
        TILE_FOREST_DIRT: TileStyle("flat", ((176, 140, 98), (166, 130, 90)), pattern="parity", edge=(130, 98, 66), surface="dirt"),
        TILE_FOREST_ROAD: TileStyle("flat", ((150, 116, 78), (140, 106, 72)), pattern="rows", edge=(112, 82, 54), surface="dirt"),
    },
    layers=(
        FillLayer(TILE_FOREST_GRASS),
        RectLayer(TILE_FOREST_ROAD, 0, 9, 10, 11),
        EllipseLayer(TILE_FOREST_DIRT, cx=10.5, cy=10.5, radius=6.4),
    ),
    props=(
        PropSpec("cabin", 0.5, 3.0, {"width": 3.4, "depth": 2.8, "height": 1.5, "color": (150, 110, 74)}),
        PropSpec("cabin", 0.5, 15.0, {"width": 3.4, "depth": 2.8, "height": 1.5, "color": (138, 102, 70)}),
        PropSpec("cabin", 7.8, 0.4, {"width": 3.0, "depth": 2.4, "height": 1.4, "color": (156, 116, 78)}),
        PropSpec("cabin", 4.2, 7.6, {"width": 1.3, "depth": 1.3, "height": 0.8, "color": (118, 84, 56)}),  # canil
        PropSpec("tent", 15.4, 3.6, {"width": 2.6, "depth": 2.2, "height": 1.6, "color": (214, 196, 156)}),
        PropSpec("tent", 16.6, 17.0, {"width": 2.6, "depth": 2.2, "height": 1.6, "color": (198, 176, 140)}),
        PropSpec("campfire", 11.0, 11.0),
    ) + tuple(PropSpec("crate", x, y) for x, y in _FOREST_CRATES)
      + tuple(PropSpec("snare", x, y) for x, y in _FOREST_SNARES)
      + tuple(PropSpec("forest_tree", x, y) for x, y in _FOREST_TREES),
    spawns=SpawnRule(x_range=(5.0, 18.0), margin=5.0, min_distance=7.0, fallback=((6.0, 13.0), (16.0, 9.0))),
    stage=StageSpec(11.0, 12.8),
    drift_count=30,
    drift_petals=0.05,
    lighting=LightingEnvironment(
        ambient_color=(255, 248, 232), ambient_strength=0.95, vignette=0.05,
        lights=(LightSource(11.0, 11.0, 0.6, (255, 160, 80), 3.0, flicker=0.3),),
        atmosphere=(AtmosphereEffect("dust", density=0.4),),
    ),
)

# ---------------------------------------------------------------------------
# Campo de Nagashino (Teppo) — 6.3.10
# ---------------------------------------------------------------------------
TILE_NAG_GRASS = 45
TILE_NAG_MUD = 46

_NAG_BARRELS = ((9.6, 10.6), (11.4, 10.0), (5.0, 11.5), (16.5, 11.0), (10.0, 18.0), (14.0, 4.0), (3.2, 3.2))
_NAG_PALISADES = (
    (2.5, 6.8, 5.0, 0.45), (11.5, 6.8, 5.0, 0.45),   # primeira linha, vão no meio
    (5.5, 14.8, 5.0, 0.45), (14.5, 14.8, 5.0, 0.45),  # segunda linha, vão deslocado
    (19.2, 9.0, 0.45, 3.4), (2.2, 10.0, 0.45, 3.0),
)

NAGASHINO_SPEC = ArenaSpec(
    id=ARENA_NAGASHINO,
    name="Campo de Nagashino",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(98, 84, 96),
    music="bgm_nagashino_field",
    wind=WindSpec(-1, 0.4, 0.9, 0.6),
    tile_styles={
        TILE_NAG_GRASS: TileStyle("flat", ((152, 150, 86), (140, 140, 78)), pattern="third", edge=(112, 112, 62), surface="grass"),
        TILE_NAG_MUD: TileStyle("flat", ((108, 82, 56), (94, 72, 50)), pattern="parity", edge=(70, 52, 36), speed_mult=0.6, surface="mud"),
    },
    layers=(
        FillLayer(TILE_NAG_GRASS),
        EllipseLayer(TILE_NAG_MUD, cx=5.5, cy=11.0, radius=2.4),
        EllipseLayer(TILE_NAG_MUD, cx=16.5, cy=12.0, radius=2.2),
        EllipseLayer(TILE_NAG_MUD, cx=11.0, cy=17.0, radius=2.0),
        EllipseLayer(TILE_NAG_MUD, cx=10.5, cy=3.5, radius=1.8),
    ),
    props=(
        tuple(PropSpec("palisade", x, y, {"width": w, "depth": d, "height": 1.5, "color": (124, 94, 60)}) for x, y, w, d in _NAG_PALISADES)
        + tuple(PropSpec("powder_barrel", x, y) for x, y in _NAG_BARRELS)
        + (
            PropSpec("nobori", 2.2, 6.2, {"text": "織", "cloth": (36, 64, 128), "pole_height": 3.0}),
            PropSpec("nobori", 16.9, 6.2, {"text": "鉄", "cloth": (36, 64, 128), "pole_height": 3.0}),
            PropSpec("nobori", 5.2, 15.8, {"text": "武", "cloth": (156, 30, 34), "pole_height": 3.0}),
            PropSpec("nobori", 19.8, 15.8, {"text": "武", "cloth": (156, 30, 34), "pole_height": 3.0}),
        )
    ),
    spawns=SpawnRule(x_range=(3.0, 19.0), margin=3.5, min_distance=7.0, fallback=((5.0, 4.8), (17.0, 18.5))),
    stage=StageSpec(10.5, 12.5),
    drift_count=20,
    drift_petals=0.0,
    lighting=LightingEnvironment(
        ambient_color=(255, 190, 140), ambient_strength=0.7, vignette=0.25,
        lights=(), atmosphere=(AtmosphereEffect("smoke", density=0.5),),
    ),
)

# ---------------------------------------------------------------------------
# Palco Kabuki (Okuni) — 6.3.11
# ---------------------------------------------------------------------------
TILE_KABUKI_FLOOR = 47
TILE_KABUKI_DISC = 48
TILE_HANAMICHI = 49


def _folding_screen(cx: float, cy: float, axis: str) -> tuple:
    """Biombo de três painéis em zigue-zague, centrado em (cx, cy) ao longo do eixo informado."""
    out = []
    for i, tilt in enumerate((1.0, -1.0, 1.0)):
        d = (i - 1) * 0.84
        out.append(PropSpec("screen_panel", cx + (d if axis == "x" else 0.0), cy + (d if axis == "y" else 0.0), {"axis": axis, "tilt": tilt}))
    return tuple(out)


_KABUKI_LANTERNS = ((3.0, 3.6), (19.0, 3.6), (3.0, 18.4), (19.0, 18.4))

KABUKI_STAGE_SPEC = ArenaSpec(
    id=ARENA_KABUKI_STAGE,
    name="Palco Kabuki",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(30, 14, 24),
    music="bgm_kabuki_stage",
    wind=WindSpec(1, 0.0, 0.05, 0.2),
    tile_styles={
        TILE_KABUKI_FLOOR: TileStyle("flat", ((148, 100, 64), (136, 90, 58)), pattern="rows", edge=(86, 54, 34), surface="wood"),
        TILE_KABUKI_DISC: TileStyle("flat", ((176, 40, 48), (160, 32, 42)), pattern="parity", edge=(104, 22, 30), surface="wood"),
        TILE_HANAMICHI: TileStyle("slab", ((196, 150, 96),), height=0.12, outline=True, top_edge=(120, 84, 52), surface="wood"),
    },
    layers=(
        FillLayer(TILE_KABUKI_FLOOR),
        EllipseLayer(TILE_KABUKI_DISC, cx=10.5, cy=10.5, radius=4.3),
        RectLayer(TILE_HANAMICHI, 0, 6, 10, 11),  # passarela hanamichi
    ),
    props=(
        PropSpec("curtain", 3.0, 0.8, {"length": 16.0, "axis": "x", "height": 3.4, "drop": 3.2}),
    ) + _folding_screen(7.0, 6.2, "x") + _folding_screen(15.0, 6.8, "y") + _folding_screen(7.2, 16.0, "y")
      + tuple(PropSpec("paper_lantern", x, y, {"color": (220, 60, 44)}) for x, y in _KABUKI_LANTERNS),
    hazards=(HazardSpec("rotating_stage", {"cx": 11.0, "cy": 11.0, "radius": 4.3}),),
    spawns=SpawnRule(x_range=(3.0, 19.0), margin=3.5, min_distance=7.0, fallback=((4.5, 13.5), (17.5, 14.0))),
    stage=StageSpec(11.0, 11.0),
    drift_count=18,
    drift_petals=0.9,
    lighting=LightingEnvironment(
        ambient_color=(255, 200, 170), ambient_strength=0.6, vignette=0.35,
        lights=tuple(LightSource(x, y, 1.4, (255, 90, 60), 3.0, flicker=0.15) for x, y in _KABUKI_LANTERNS),
        atmosphere=(AtmosphereEffect("spotlight", density=0.5, points=((11.0, 11.0, 4.0),)),),
    ),
)

# ---------------------------------------------------------------------------
# Santuário na Montanha (Tomoe) — 6.3.12
# ---------------------------------------------------------------------------
TILE_SHRINE_GRASS = 50
TILE_SHRINE_STONE = 51
TILE_SHRINE_SAND = 52
TILE_SHRINE_GRAVEL = 53

_SHRINE_TORII = ((10.5, 2.6), (10.5, 6.0), (10.5, 9.4), (10.5, 12.8), (10.5, 16.2))
_SHRINE_LANTERNS = ((8.4, 4.3), (12.6, 4.3), (8.4, 11.1), (12.6, 11.1), (8.4, 18.0), (12.6, 18.0))
_SHRINE_PINES = ((1.8, 7.0), (2.2, 15.5), (19.8, 20.0), (5.0, 20.0))
_SHRINE_OUTCROPS = ((1.3, 1.3), (20.7, 1.3), (1.3, 20.7), (20.7, 12.0))

MOUNTAIN_SHRINE_SPEC = ArenaSpec(
    id=ARENA_MOUNTAIN_SHRINE,
    name="Santuário na Montanha",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(128, 156, 196),
    music="bgm_mountain_shrine",
    wind=WindSpec(1, -0.5, 0.9, 0.8),
    tile_styles={
        TILE_SHRINE_GRASS: TileStyle("flat", ((100, 142, 112), (90, 132, 104)), pattern="third", edge=(66, 100, 80), surface="grass"),
        TILE_SHRINE_STONE: TileStyle("flat", ((156, 156, 164), (144, 144, 154)), pattern="parity", edge=(104, 104, 114), surface="stone"),
        TILE_SHRINE_SAND: TileStyle("flat", ((218, 202, 164), (206, 190, 154)), pattern="rows", edge=(170, 154, 120), surface="sand"),
        TILE_SHRINE_GRAVEL: TileStyle("flat", ((126, 126, 136), (116, 116, 126)), pattern="parity", edge=(84, 84, 94), surface="gravel"),
    },
    layers=(
        FillLayer(TILE_SHRINE_GRASS),
        RectLayer(TILE_SHRINE_STONE, 9, 11, 0, 21),
        RectLayer(TILE_SHRINE_GRAVEL, 3, 7, 3, 9),
        RectLayer(TILE_SHRINE_SAND, 15, 18, 3, 17),
    ),
    props=(
        tuple(PropSpec("torii", x, y) for x, y in _SHRINE_TORII)
        + (PropSpec("shrine_bell", 5.2, 6.2),)
        + tuple(PropSpec("archery_target", x, 3.8) for x in (15.7, 16.9, 18.1))
        + (PropSpec("cabin", 14.9, 17.8, {"width": 3.6, "depth": 2.2, "height": 1.3, "color": (176, 142, 100)}),)
        + tuple(PropSpec("stone_lantern", x, y) for x, y in _SHRINE_LANTERNS)
        + tuple(PropSpec("pine", x, y) for x, y in _SHRINE_PINES)
        + tuple(PropSpec("rock", x, y, {"radius": 1.0, "height": 1.7}) for x, y in _SHRINE_OUTCROPS)
    ),
    spawns=SpawnRule(x_range=(3.0, 19.0), margin=4.0, min_distance=7.0, fallback=((6.5, 13.0), (14.0, 13.5))),
    stage=StageSpec(10.5, 11.0),
    drift_count=36,
    drift_petals=0.7,
    lighting=LightingEnvironment(
        ambient_color=(205, 224, 255), ambient_strength=0.85, vignette=0.15,
        lights=tuple(LightSource(x, y, 0.9, (255, 220, 160), 2.4, flicker=0.08) for x, y in _SHRINE_LANTERNS),
        atmosphere=(AtmosphereEffect("fog", density=0.3),),
    ),
)

# ---------------------------------------------------------------------------
# Pátio Barroco (Julie) — 6.3.13
# ---------------------------------------------------------------------------
TILE_BAROQUE_GRASS = 54
TILE_MARBLE_LIGHT = 55
TILE_MARBLE_DARK = 56
TILE_BAROQUE_WATER = 57


def _hedge_row(x: float, y: float, axis: str, count: int = 4) -> tuple:
    return tuple(PropSpec("hedge", x + (i * 0.9 if axis == "x" else 0.0), y + (i * 0.9 if axis == "y" else 0.0)) for i in range(count))


_BAROQUE_STATUES = ((3.6, 3.6), (18.4, 3.6), (3.6, 18.4), (18.4, 18.4), (11.0, 3.8), (11.0, 18.2))
_BAROQUE_BANNERS = ((6.0, 2.6), (16.0, 2.6), (6.0, 19.4), (16.0, 19.4))

BAROQUE_COURT_SPEC = ArenaSpec(
    id=ARENA_BAROQUE_COURT,
    name="Pátio Barroco",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(146, 168, 200),
    music="bgm_baroque_court",
    wind=WindSpec(1, 0.5, 0.3, 0.4),
    tile_styles={
        TILE_BAROQUE_GRASS: TileStyle("flat", ((84, 140, 82), (76, 130, 76)), pattern="third", edge=(56, 98, 58), surface="grass"),
        TILE_MARBLE_LIGHT: TileStyle("flat", ((236, 232, 224),), edge=(176, 170, 160), surface="marble"),
        TILE_MARBLE_DARK: TileStyle("flat", ((78, 80, 92),), edge=(46, 48, 58), surface="marble"),
        TILE_BAROQUE_WATER: TileStyle("water", ((70, 130, 170), (150, 200, 226)), edge=(120, 118, 112), depth=0.1, speed_mult=0.6,
                                      bank_ns=((210, 206, 196), (150, 146, 138)), bank_ew=((220, 216, 206), (160, 156, 148)), surface="water"),
    },
    layers=(
        FillLayer(TILE_BAROQUE_GRASS),
        CheckerLayer(TILE_MARBLE_LIGHT, TILE_MARBLE_DARK, 2, 19, 2, 19),
        EllipseLayer(TILE_BAROQUE_WATER, cx=10.5, cy=10.5, radius=3.1),
    ),
    props=(
        (PropSpec("fountain", 11.0, 11.0),)
        + _hedge_row(4.6, 6.4, "x") + _hedge_row(15.8, 4.6, "y") + _hedge_row(5.2, 14.4, "y") + _hedge_row(14.6, 15.6, "x")
        + tuple(PropSpec("marble_statue", x, y) for x, y in _BAROQUE_STATUES)
        + tuple(PropSpec("nobori", x, y, {"text": "", "emblem": "fleur", "cloth": (34, 58, 142), "ink": (238, 204, 90), "pole_height": 3.2}) for x, y in _BAROQUE_BANNERS)
    ),
    spawns=SpawnRule(x_range=(3.5, 18.5), margin=4.0, min_distance=7.0, fallback=((5.0, 11.0), (17.0, 11.0))),
    stage=StageSpec(11.0, 14.6),
    drift_count=14,
    drift_petals=0.5,
    lighting=LightingEnvironment(
        ambient_color=(255, 238, 210), ambient_strength=0.9, vignette=0.1,
        lights=(), atmosphere=(AtmosphereEffect("sunbeams", density=0.4),
                                AtmosphereEffect("steam", density=0.3, points=((11.0, 11.0, 1.9),))),
    ),
)

# ---------------------------------------------------------------------------
# Registro de arenas jogáveis
# ---------------------------------------------------------------------------
ARENA_SPECS: dict[str, ArenaSpec] = {
    ARENA_BAMBOO: BAMBOO_SPEC, ARENA_KYOTO: KYOTO_SPEC, ARENA_GANRYU: GANRYU_SPEC,
    ARENA_IGA: IGA_SPEC, ARENA_PIRATE_DECK: PIRATE_SPEC, ARENA_SHADOW_CAVE: SHADOW_CAVE_SPEC,
    ARENA_MIST_TEMPLE: MIST_TEMPLE_SPEC, ARENA_FOREST_CAMP: FOREST_CAMP_SPEC,
    ARENA_NAGASHINO: NAGASHINO_SPEC,
    ARENA_KABUKI_STAGE: KABUKI_STAGE_SPEC,
    ARENA_MOUNTAIN_SHRINE: MOUNTAIN_SHRINE_SPEC,
    ARENA_BAROQUE_COURT: BAROQUE_COURT_SPEC,
}


# ---------------------------------------------------------------------------
# Campo dos Mortos de Fome (chefe Oni Gashadokuro) — 8.2.3, fora das telas de seleção
# ---------------------------------------------------------------------------
TILE_GY_SOIL = 58
TILE_GY_PATH = 59
TILE_GY_MOUND = 60

_GY_GRAVES = ((5.5, 5.5), (16.5, 5.5), (3.5, 11.0), (18.5, 11.0), (5.5, 16.5), (16.5, 16.5), (9.0, 13.5), (13.0, 8.5))
_GY_LANTERNS = ((7.0, 3.5), (15.0, 3.5), (7.0, 18.5), (15.0, 18.5))

GASHADOKURO_SPEC = ArenaSpec(
    id=ARENA_GASHADOKURO,
    name="Campo dos Mortos de Fome",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(18, 8, 12),
    music="bgm_gashadokuro",
    wind=WindSpec(1, 0.3, 0.2, 0.5),
    tile_styles={
        TILE_GY_SOIL: TileStyle("flat", ((58, 44, 40), (52, 39, 36)), pattern="parity", edge=(30, 22, 22), surface="earth"),
        TILE_GY_PATH: TileStyle("flat", ((92, 74, 68), (84, 67, 62)), pattern="parity", edge=(48, 36, 34), surface="earth"),
        TILE_GY_MOUND: TileStyle("flat", ((120, 96, 84), (110, 88, 77)), pattern="parity", edge=(62, 46, 42), surface="earth"),
    },
    layers=(
        FillLayer(TILE_GY_SOIL),
        EllipseLayer(TILE_GY_PATH, cx=10.5, cy=10.5, radius=9.0),
        EllipseLayer(TILE_GY_MOUND, cx=10.5, cy=7.5, radius=2.6),
    ),
    props=(
        tuple(PropSpec("jizo", x, y) for x, y in _GY_GRAVES)
        + tuple(PropSpec("stone_lantern", x, y) for x, y in _GY_LANTERNS)
    ),
    playable_bounds=(2.0, 2.0, 20.0, 20.0),
    spawns=SpawnRule(x_range=(4.0, 18.0), margin=4.0, min_distance=7.0, fallback=((10.5, 17.5), (10.5, 7.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=0,
    lighting=LightingEnvironment(
        ambient_color=(130, 60, 70), ambient_strength=0.4, vignette=0.5,
        lights=tuple(LightSource(x, y, 0.9, (255, 80, 60), 3.6, flicker=0.25) for x, y in _GY_LANTERNS),
        atmosphere=(AtmosphereEffect("mist", density=0.7),),
    ),
)

# Arenas que só o Arcade usa: ficam fora de `arena_ids()` e, portanto, das telas de seleção e do sorteio
HIDDEN_ARENA_SPECS = {ARENA_GASHADOKURO: GASHADOKURO_SPEC}


def arena_ids() -> list[str]:
    """Ids das arenas jogáveis, na ordem de registro (a 'Arena Aleatória' sorteia entre elas)."""
    return list(ARENA_SPECS)


def create_arena(arena_id: str) -> ArenaMap:
    spec = ARENA_SPECS.get(arena_id) or HIDDEN_ARENA_SPECS.get(arena_id)
    if spec is None:
        raise KeyError(f"Arena desconhecida: {arena_id}")
    return ArenaMap(spec)
