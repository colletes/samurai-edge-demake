"""
Registro das arenas do jogo e seus `ArenaSpec` (Entregável 6.2).

Aqui ficam os dados de cada arena e o registro dos tipos de prop, estrutura e perigo que o motor
(`arena_generator.py`) sabe instanciar. Novas arenas (Entregável 6.3) são só novos specs.
"""
from src.config import (
    ARENA_BAMBOO, ARENA_KYOTO, ARENA_GANRYU, ARENA_IGA, ARENA_PIRATE_DECK, ARENA_SHADOW_CAVE, ARENA_MIST_TEMPLE, ARENA_FOREST_CAMP, ARENA_NAGASHINO, ARENA_KABUKI_STAGE, ARENA_MOUNTAIN_SHRINE, ARENA_BAROQUE_COURT, ARENA_GASHADOKURO,
    ARENA_SHAOLIN, ARENA_HIGANBANA, ARENA_GOJO_BRIDGE, ARENA_YOSHIWARA, ARENA_RICE_PADDIES, ARENA_RAIN_MILL,
    ARENA_GOTHIC_CEMETERY, ARENA_HEIAN_SHRINE, ARENA_SACRED_PINES, ARENA_EZO_TUNDRA,
    ARENA_DOHYO, ARENA_DEJIMA, COLOR_BG, COLOR_KYOTO_BG,
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
    VoxelCricket, VoxelSparrow, Scarecrow, HayBale, WaterMillWheel, DuneGrass,
    GojoRailing, KagaribiBrazier, BladeCluster, BridgeSupport, WaterChute,
    GothicHeadstone, MausoleumCrypt, WroughtIronFence, GothicDeadTree, HeianTorii, GinkgoTree, ShimenawaBanner, HeianToro,
    SoulFissure, BoneMound, SpectralToro,
    AkamatsuPine, MountainHokora, TimberLogPile, AinuInauTotem, HideDryingRack, SnowSpruceTree,
    DohyoCornerPost, SacredSaltMound, DohyoBrazier, AlchemyWorkbench, ReagentBarrel, WharfMooringBollard, WarehouseDoorwayArch,
    SacredBushBarrier, WarehouseGlassWall, LargeSacredCenser, WharfPiling,
)
from src.world.hazards import (
    ChainPendulum, FireworkMortars, RotatingStage, ShipRoll, TideSurge,
    GothicCemeteryHazard, HeianShrineHazard, GashadokuroArenaHazard,
    PineForestHazard, EzoTaigaHazard,
    DohyoHazard, DejimaHazard,
)
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
register_prop("cricket", lambda x, y, **p: VoxelCricket(x, y, **p), "lanterns")
register_prop("sparrow", lambda x, y, **p: VoxelSparrow(x, y, **p), "lanterns")
register_prop("scarecrow", lambda x, y, **p: Scarecrow(x, y, **p), "lanterns")
register_prop("hay_bale", lambda x, y, **p: HayBale(x, y, **p), "rocks")
register_prop("watermill", lambda x, y, **p: WaterMillWheel(x, y, **p), "buildings")
register_prop("dune_grass", lambda x, y, **p: DuneGrass(x, y, **p), "lanterns")
register_prop("gojo_railing", lambda x, y, **p: GojoRailing(wy=y, **p), "buildings")
register_prop("kagaribi", lambda x, y, **p: KagaribiBrazier(x, y, **p), "rocks")
register_prop("blade_cluster", lambda x, y, **p: BladeCluster(x, y, **p), "rocks")
register_prop("bridge_support", lambda x, y, **p: BridgeSupport(x, y, **p), "lanterns")
register_prop("water_chute", lambda x, y, **p: WaterChute(x, y, **p), "lanterns")
register_prop("gothic_headstone", lambda x, y, **p: GothicHeadstone(x, y, **p), "rocks")
register_prop("mausoleum", lambda x, y, **p: MausoleumCrypt(x, y, **p), "buildings")
register_prop("iron_fence", lambda x, y, **p: WroughtIronFence(x, y, **p), "rocks")
register_prop("dead_tree", lambda x, y, **p: GothicDeadTree(x, y), "trees")
register_prop("heian_torii", lambda x, y, **p: HeianTorii(x, y), "torii_gates")
register_prop("ginkgo_tree", lambda x, y, **p: GinkgoTree(x, y), "trees")
register_prop("shimenawa", lambda x, y, **p: ShimenawaBanner(x, y, **p), "lanterns")
register_prop("heian_toro", lambda x, y, **p: HeianToro(x, y), "rocks")
register_prop("soul_fissure", lambda x, y, **p: SoulFissure(x, y, **p), "lanterns")
register_prop("bone_mound", lambda x, y, **p: BoneMound(x, y, **p), "rocks")
register_prop("spectral_toro", lambda x, y, **p: SpectralToro(x, y), "rocks")
register_prop("akamatsu_pine", lambda x, y, **p: AkamatsuPine(x, y, **p), "trees")
register_prop("mountain_hokora", lambda x, y, **p: MountainHokora(x, y), "rocks")
register_prop("timber_logs", lambda x, y, **p: TimberLogPile(x, y), "rocks")
register_prop("ainu_inau", lambda x, y, **p: AinuInauTotem(x, y), "rocks")
register_prop("hide_rack", lambda x, y, **p: HideDryingRack(x, y), "rocks")
register_prop("snow_spruce", lambda x, y, **p: SnowSpruceTree(x, y, **p), "trees")
register_prop("dohyo_post", lambda x, y, **p: DohyoCornerPost(x, y, **p), "lanterns")
register_prop("salt_mound", lambda x, y, **p: SacredSaltMound(x, y), "rocks")
register_prop("dohyo_brazier", lambda x, y, **p: DohyoBrazier(x, y), "lanterns")
register_prop("alchemy_bench", lambda x, y, **p: AlchemyWorkbench(x, y), "rocks")
register_prop("reagent_barrel", lambda x, y, **p: ReagentBarrel(x, y, **p), "buildings")
register_prop("wharf_bollard", lambda x, y, **p: WharfMooringBollard(x, y), "rocks")
register_prop("doorway_arch", lambda x, y, **p: WarehouseDoorwayArch(x, y), "buildings")
register_prop("sacred_bush", lambda x, y, **p: SacredBushBarrier(x, y, **p), "trees")
register_prop("glass_wall", lambda x, y, **p: WarehouseGlassWall(x, y, **p), "buildings")
register_prop("large_censer", lambda x, y, **p: LargeSacredCenser(x, y), "lanterns")
register_prop("wharf_piling", lambda x, y, **p: WharfPiling(x, y), "rocks")
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
register_hazard("gothic_cemetery_hazard", GothicCemeteryHazard)
register_hazard("heian_shrine_hazard", HeianShrineHazard)
register_hazard("gashadokuro_hazard", GashadokuroArenaHazard)
register_hazard("pine_forest_hazard", PineForestHazard)
register_hazard("ezo_taiga_hazard", EzoTaigaHazard)
register_hazard("dohyo_hazard", DohyoHazard)
register_hazard("dejima_hazard", DejimaHazard)


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
    ) + tuple(PropSpec("stone_lantern", x, y) for x, y in _GANRYU_LANTERNS)
      + tuple(PropSpec("dune_grass", x, y, {"seed": 30 + i}) for i, (x, y) in enumerate(
          ((5.2, 4.2), (15.2, 5.5), (4.5, 16.8), (17.5, 16.2), (8.5, 7.5), (13.5, 16.5), (7.0, 18.2), (15.8, 8.8))
      )),
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
    drift_count=48,
    drift_petals=0.60,
    lighting=LightingEnvironment(
        ambient_color=(150, 160, 172), ambient_strength=0.55, vignette=0.30,
        lights=tuple(LightSource(x, y, 0.9, (255, 214, 150), 2.5, flicker=0.12) for x, y in _GANRYU_LANTERNS),
        atmosphere=(
            AtmosphereEffect("fog", density=0.85),
            AtmosphereEffect("mist", density=0.75),
            AtmosphereEffect("dust", density=0.40),
        ),
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
    drift_count=52,
    drift_petals=0.75,
    lighting=LightingEnvironment(
        ambient_color=(68, 85, 130), ambient_strength=0.46, vignette=0.42,
        lights=tuple(LightSource(x, y, 1.0, (255, 190, 110), 3.0, flicker=0.15) for x, y in _IGA_LANTERNS),
        atmosphere=(
            AtmosphereEffect("fogbank", density=0.85),
            AtmosphereEffect("mist", density=0.65),
            AtmosphereEffect("dust", density=0.30),
        ),
    ),
)

# ---------------------------------------------------------------------------
# Convés na Tempestade (Anne) — 6.3.5 (Revamp Visual Ciclo 5)
# ---------------------------------------------------------------------------
TILE_DECK = 27
TILE_DECK_GRATE = 115
TILE_DECK_QUARTER = 116

_SEA_PIT = dict(depth=1.9, floor_color=(18, 52, 70), wall_colors=((96, 68, 46), (22, 54, 68)), rim_color=(108, 76, 50),
                water=((24, 70, 92), (196, 224, 234)))
_HOLE_PIT = dict(depth=1.6, floor_color=(6, 12, 18), wall_colors=((96, 68, 46), (10, 14, 20)), rim_color=(96, 68, 46))
_PIRATE_LANTERNS = ((7.9, 10.0), (14.7, 10.0), (1.2, 4.6), (20.8, 17.4), (3.6, 10.5), (18.4, 10.5))

PIRATE_SPEC = ArenaSpec(
    id=ARENA_PIRATE_DECK,
    name="Convés na Tempestade",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(14, 24, 34),
    music="bgm_pirate_deck",
    wind=WindSpec(1, 0.6, 1.8, 0.9),
    tile_styles={
        TILE_DECK: TileStyle("flat", ((124, 92, 64), (110, 80, 56)), pattern="rows", edge=(64, 44, 30), surface="wood"),
        TILE_DECK_GRATE: TileStyle("flat", ((76, 52, 34), (62, 42, 28)), pattern="parity", edge=(42, 28, 18), surface="wood"),
        TILE_DECK_QUARTER: TileStyle("flat", ((138, 102, 70), (126, 92, 62)), pattern="rows", edge=(82, 58, 38), surface="wood"),
    },
    layers=(
        FillLayer(TILE_DECK),
        RectLayer(TILE_DECK_QUARTER, 0, 3, 4, 17),
        RectLayer(TILE_DECK_QUARTER, 18, 21, 4, 17),
        RectLayer(TILE_DECK_GRATE, 9, 12, 9, 12),
    ),
    drift_count=28,
    drift_petals=0.15,
    props=(
        PropSpec("mast", 7.6, 10.7, {"width": 0.65, "depth": 0.65, "height": 3.6, "color": (112, 80, 52)}),
        PropSpec("mast", 14.4, 10.7, {"width": 0.65, "depth": 0.65, "height": 3.6, "color": (112, 80, 52)}),
        PropSpec("bunting", 7.6, 10.7, {"x1": 14.4, "y1": 10.7, "z": 3.1}),
        PropSpec("cannon", 1.0, 12.0, {"facing": (1.0, 0.0)}),
        PropSpec("cannon", 19.5, 8.5, {"facing": (-1.0, 0.0)}),
        PropSpec("powder_barrel", 3.0, 6.2),
        PropSpec("powder_barrel", 18.2, 15.2),
        PropSpec("barrel", 3.0, 4.6, {"width": 0.7, "depth": 0.7, "height": 0.8, "color": (104, 70, 44)}),
        PropSpec("barrel", 3.9, 4.9, {"width": 0.7, "depth": 0.7, "height": 0.8, "color": (96, 64, 42)}),
        PropSpec("barrel", 17.6, 16.6, {"width": 0.7, "depth": 0.7, "height": 0.8, "color": (104, 70, 44)}),
        PropSpec("barrel", 18.5, 16.9, {"width": 0.7, "depth": 0.7, "height": 0.8, "color": (96, 64, 42)}),
        PropSpec("barrel", 9.0, 16.6, {"width": 0.7, "depth": 0.7, "height": 0.8, "color": (104, 70, 44)}),
        PropSpec("crate", 12.5, 4.8),
        PropSpec("solid_block", 19.8, 4.6, {"width": 0.9, "depth": 0.9, "height": 0.7, "color": (118, 92, 62)}),
        PropSpec("solid_block", 1.2, 16.6, {"width": 0.9, "depth": 0.9, "height": 0.7, "color": (118, 92, 62)}),
        PropSpec("paper_lantern", 7.6, 10.2, {"color": (245, 165, 65)}),
        PropSpec("paper_lantern", 14.4, 10.2, {"color": (245, 165, 65)}),
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
        ambient_color=(70, 92, 112), ambient_strength=0.42, vignette=0.42,
        lights=tuple(LightSource(x, y, 1.6, (255, 190, 100), 3.2, flicker=0.30) for x, y in _PIRATE_LANTERNS),
        atmosphere=(
            AtmosphereEffect("rain", density=1.0),
            AtmosphereEffect("mist", density=0.55),
            AtmosphereEffect("fog", density=0.30),
        ),
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
    drift_count=32,
    drift_petals=0.1,
    lighting=LightingEnvironment(
        ambient_color=(65, 45, 95), ambient_strength=0.30, vignette=0.50,
        lights=tuple(LightSource(x, y, 0.9, (190, 110, 255), 3.8, flicker=0.25) for x, y in _CAVE_LANTERNS)
        + (LightSource(10.5, 10.5, 0.2, (220, 90, 255), 4.2, flicker=0.18),),
        atmosphere=(
            AtmosphereEffect("mist", density=0.85),
            AtmosphereEffect("fog", density=0.45),
            AtmosphereEffect("dust", density=0.55),
            AtmosphereEffect("fireflies", density=0.35),
        ),
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
    drift_count=48,
    drift_petals=0.75,
    lighting=LightingEnvironment(
        ambient_color=(155, 185, 215), ambient_strength=0.62, vignette=0.22,
        lights=(LightSource(11.0, 11.0, 0.6, (255, 160, 80), 3.5, flicker=0.35),),
        atmosphere=(
            AtmosphereEffect("embers", density=0.75),
            AtmosphereEffect("smoke", density=0.45),
            AtmosphereEffect("fireflies", density=0.35),
            AtmosphereEffect("dust", density=0.30),
        ),
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
    wind=WindSpec(-1, 0.5, 1.2, 0.85),
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
    drift_count=45,
    drift_petals=0.0,
    lighting=LightingEnvironment(
        ambient_color=(255, 170, 120), ambient_strength=0.68, vignette=0.32,
        lights=(
            LightSource(2.5, 6.8, 1.2, (255, 140, 50), 3.5, flicker=0.35),
            LightSource(16.5, 6.8, 1.2, (255, 140, 50), 3.5, flicker=0.35),
            LightSource(5.5, 14.8, 1.2, (255, 140, 50), 3.5, flicker=0.35),
            LightSource(14.5, 14.8, 1.2, (255, 140, 50), 3.5, flicker=0.35),
        ),
        atmosphere=(
            AtmosphereEffect("smoke", density=0.85),
            AtmosphereEffect("embers", density=0.80),
            AtmosphereEffect("dust", density=0.40),
        ),
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
# Santuário na Montanha (Tomoe) — 6.3.12 (Revamp Visual Ciclo 5)
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
        + (
            PropSpec("shimenawa", 10.5, 2.6, {"span": 3.4, "z": 2.4, "ribbons": 5}),
            PropSpec("shimenawa", 10.5, 16.2, {"span": 3.4, "z": 2.4, "ribbons": 5}),
            PropSpec("shrine_bell", 5.2, 6.2),
            PropSpec("mountain_hokora", 3.6, 11.5),
            PropSpec("akamatsu_pine", 19.2, 7.2, {"scale": 0.95}),
        )
        + tuple(PropSpec("archery_target", x, 3.8) for x in (15.7, 16.9, 18.1))
        + (PropSpec("cabin", 14.9, 17.8, {"width": 3.6, "depth": 2.2, "height": 1.3, "color": (176, 142, 100)}),)
        + tuple(PropSpec("stone_lantern", x, y) for x, y in _SHRINE_LANTERNS)
        + tuple(PropSpec("pine", x, y) for x, y in _SHRINE_PINES)
        + tuple(PropSpec("rock", x, y, {"radius": 1.0, "height": 1.7}) for x, y in _SHRINE_OUTCROPS)
    ),
    spawns=SpawnRule(x_range=(3.0, 19.0), margin=4.0, min_distance=7.0, fallback=((6.5, 13.0), (14.0, 13.5))),
    stage=StageSpec(10.5, 11.0),
    drift_count=44,
    drift_petals=0.78,
    lighting=LightingEnvironment(
        ambient_color=(205, 224, 255), ambient_strength=0.85, vignette=0.18,
        lights=tuple(LightSource(x, y, 0.9, (255, 220, 160), 2.4, flicker=0.08) for x, y in _SHRINE_LANTERNS),
        atmosphere=(
            AtmosphereEffect("sunbeams", density=0.45),
            AtmosphereEffect("mist", density=0.35),
            AtmosphereEffect("fog", density=0.25),
        ),
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
    drift_count=42,
    drift_petals=0.90,
    lighting=LightingEnvironment(
        ambient_color=(255, 246, 228), ambient_strength=0.92, vignette=0.14,
        lights=(),
        atmosphere=(
            AtmosphereEffect("sunbeams", density=0.50),
            AtmosphereEffect("steam", density=0.70, points=((11.0, 11.0, 1.9),)),
            AtmosphereEffect("mist", density=0.35),
        ),
    ),
)

# ---------------------------------------------------------------------------
# Pátio dos Sinos Shaolin (Ren)
# ---------------------------------------------------------------------------
TILE_SHAOLIN_BORDER = 61
TILE_SHAOLIN_TERRACE = 62
TILE_SHAOLIN_PAVING = 63
TILE_SHAOLIN_GRAVEL = 64

_SHAOLIN_LANTERNS = ((7.5, 4.5), (13.5, 4.5), (7.5, 16.5), (13.5, 16.5))
_SHAOLIN_INCENSE = ((6.8, 6.8), (14.2, 6.8), (6.8, 14.2), (14.2, 14.2))
_SHAOLIN_PINES = ((2.2, 2.2), (18.8, 2.2), (2.2, 18.8), (18.8, 18.8))
_SHAOLIN_JIZO = ((4.5, 10.5), (16.5, 10.5))
_SHAOLIN_CRICKETS = ((5.5, 7.8), (15.2, 7.2), (6.8, 15.5), (14.5, 14.0), (10.5, 5.2), (11.0, 16.0))
_SHAOLIN_SPARROWS = ((8.5, 9.2), (12.5, 11.8), (9.2, 12.2), (11.8, 8.5))

SHAOLIN_SPEC = ArenaSpec(
    id=ARENA_SHAOLIN,
    name="Pátio dos Sinos Shaolin",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(175, 145, 125),
    music="bgm_shaolin_temple",
    wind=WindSpec(1, 0.3, 0.45, 0.4),
    tile_styles={
        TILE_SHAOLIN_BORDER: TileStyle("flat", ((74, 62, 54), (66, 54, 46)), pattern="parity", edge=(48, 38, 32), surface="stone"),
        TILE_SHAOLIN_TERRACE: TileStyle("flat", ((140, 122, 104), (128, 110, 94)), pattern="parity", edge=(96, 82, 70), surface="stone"),
        TILE_SHAOLIN_PAVING: TileStyle("flat", ((186, 172, 152), (174, 160, 140)), pattern="rows", edge=(130, 118, 100), surface="stone"),
        TILE_SHAOLIN_GRAVEL: TileStyle("flat", ((210, 195, 165), (198, 182, 152)), pattern="parity", edge=(152, 138, 112), surface="gravel"),
    },
    layers=(
        FillLayer(TILE_SHAOLIN_BORDER),
        RectLayer(TILE_SHAOLIN_TERRACE, 2, 19, 2, 19),
        RectLayer(TILE_SHAOLIN_PAVING, 4, 17, 4, 17),
        EllipseLayer(TILE_SHAOLIN_GRAVEL, cx=10.5, cy=10.5, radius=4.5),
    ),
    props=(
        (PropSpec("shrine_bell", 4.2, 4.8), PropSpec("shrine_bell", 16.8, 16.2))
        + tuple(PropSpec("incense", x, y) for x, y in _SHAOLIN_INCENSE)
        + tuple(PropSpec("stone_lantern", x, y) for x, y in _SHAOLIN_LANTERNS)
        + tuple(PropSpec("pine", x, y) for x, y in _SHAOLIN_PINES)
        + tuple(PropSpec("jizo", x, y) for x, y in _SHAOLIN_JIZO)
        + tuple(PropSpec("cricket", x, y, {"seed": 10 + i * 17}) for i, (x, y) in enumerate(_SHAOLIN_CRICKETS))
        + tuple(PropSpec("sparrow", x, y, {"seed": 30 + i * 23}) for i, (x, y) in enumerate(_SHAOLIN_SPARROWS))
    ),
    spawns=SpawnRule(x_range=(4.0, 17.0), margin=4.0, min_distance=7.0, fallback=((6.5, 10.5), (14.5, 10.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=42,
    drift_petals=0.65,
    lighting=LightingEnvironment(
        ambient_color=(255, 230, 185), ambient_strength=0.88, vignette=0.15,
        lights=tuple(LightSource(x, y, 0.9, (255, 210, 130), 2.8, flicker=0.10) for x, y in _SHAOLIN_LANTERNS),
        atmosphere=(
            AtmosphereEffect("incense", density=0.85),
            AtmosphereEffect("sunbeams", density=0.50),
            AtmosphereEffect("dust", density=0.45),
        ),
    ),
)

# ---------------------------------------------------------------------------
# Jardim dos Lírios Carmim (Chiyo)
# ---------------------------------------------------------------------------
TILE_HIGAN_GRASS = 65
TILE_HIGAN_FLOWERS = 66
TILE_HIGAN_STONE = 67
TILE_HIGAN_WATER = 68

_HIGAN_LANTERNS = ((8.5, 6.0), (12.5, 6.0), (8.5, 15.0), (12.5, 15.0))
_HIGAN_BAMBOOS = (
    (2.5, 5.0), (3.0, 9.0), (2.5, 13.0), (3.0, 16.5),
    (18.5, 5.0), (18.0, 9.0), (18.5, 13.0), (18.0, 16.5),
)
_HIGAN_MIST = ((5.0, 7.0), (16.0, 7.0), (5.0, 14.0), (16.0, 14.0), (10.5, 10.5))
_HIGAN_JIZO = ((6.0, 6.0), (15.0, 15.0))

HIGANBANA_SPEC = ArenaSpec(
    id=ARENA_HIGANBANA,
    name="Jardim dos Lírios Carmim",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(18, 10, 24),
    music="bgm_higanbana_garden",
    wind=WindSpec(-1, 0.4, 0.7, 0.6),
    tile_styles={
        TILE_HIGAN_GRASS: TileStyle("flat", ((32, 26, 36), (26, 20, 30)), pattern="parity", edge=(16, 12, 20), surface="grass"),
        TILE_HIGAN_FLOWERS: TileStyle("flat", ((178, 24, 46), (142, 18, 36)), pattern="third", edge=(108, 12, 26), surface="grass"),
        TILE_HIGAN_STONE: TileStyle("flat", ((68, 64, 76), (56, 52, 64)), pattern="rows", edge=(38, 34, 44), surface="stone"),
        TILE_HIGAN_WATER: TileStyle("water", ((22, 16, 32), (64, 38, 72)), edge=(14, 10, 20), depth=0.14, speed_mult=0.5, surface="water"),
    },
    layers=(
        FillLayer(TILE_HIGAN_FLOWERS),
        EllipseLayer(TILE_HIGAN_WATER, cx=10.5, cy=10.5, radius=8.2, sx=1.0, sy=0.9),
        RectLayer(TILE_HIGAN_STONE, 9, 12, 0, 21),
        EllipseLayer(TILE_HIGAN_STONE, cx=10.5, cy=10.5, radius=3.8),
        EllipseLayer(TILE_HIGAN_FLOWERS, cx=10.5, cy=10.5, radius=2.2),
    ),
    props=(
        (PropSpec("torii", 10.5, 2.5), PropSpec("torii", 10.5, 18.5))
        + tuple(PropSpec("bamboo", x, y) for x, y in _HIGAN_BAMBOOS)
        + tuple(PropSpec("stone_lantern", x, y) for x, y in _HIGAN_LANTERNS)
        + tuple(PropSpec("mist", x, y, {"radius": 3.0}) for x, y in _HIGAN_MIST)
        + tuple(PropSpec("jizo", x, y) for x, y in _HIGAN_JIZO)
    ),
    spawns=SpawnRule(x_range=(4.0, 17.0), margin=4.0, min_distance=7.0, fallback=((10.5, 6.5), (10.5, 14.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=55,
    drift_petals=0.95,
    lighting=LightingEnvironment(
        ambient_color=(75, 52, 98), ambient_strength=0.38, vignette=0.45,
        lights=tuple(LightSource(x, y, 0.9, (255, 100, 130), 3.2, flicker=0.22) for x, y in _HIGAN_LANTERNS),
        atmosphere=(
            AtmosphereEffect("mist", density=0.75),
            AtmosphereEffect("fogbank", density=0.60),
            AtmosphereEffect("fireflies", density=0.80),
        ),
    ),
)

# ---------------------------------------------------------------------------
# Ponte Gojo (Benkei) — Ciclo 2
# ---------------------------------------------------------------------------
TILE_GOJO_RIVER = 69
TILE_GOJO_BANK = 70
TILE_GOJO_PLANK = 71
TILE_GOJO_CENTER = 72

_GOJO_LANTERNS = ((4.5, 7.2), (10.5, 7.2), (16.5, 7.2), (4.5, 13.8), (10.5, 13.8), (16.5, 13.8))
_GOJO_JIZO = ((2.0, 9.5), (2.0, 11.5), (19.5, 9.5), (19.5, 11.5))
_GOJO_KAGARIBI = ((2.2, 7.0), (2.2, 14.0), (10.5, 6.8), (10.5, 14.2), (18.8, 7.0), (18.8, 14.0))
_GOJO_BLADES = ((1.5, 8.5), (1.5, 12.5), (19.5, 8.5), (19.5, 12.5), (2.8, 10.5), (18.2, 10.5))
_GOJO_SUPPORTS = ((5.5, 6.7), (10.5, 6.7), (15.5, 6.7), (5.5, 14.3), (10.5, 14.3), (15.5, 14.3))

GOJO_BRIDGE_SPEC = ArenaSpec(
    id=ARENA_GOJO_BRIDGE,
    name="Ponte Gojo",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(14, 18, 28),
    music="bgm_gojo_bridge",
    wind=WindSpec(-1, 0.4, 0.6, 0.5),
    tile_styles={
        TILE_GOJO_RIVER: TileStyle("water", ((16, 22, 36), (36, 52, 78)), edge=(10, 14, 24), depth=0.25, speed_mult=0.45, surface="water"),
        TILE_GOJO_BANK: TileStyle("flat", ((72, 66, 60), (60, 54, 48)), pattern="parity", edge=(40, 36, 32), surface="stone"),
        TILE_GOJO_PLANK: TileStyle("flat", ((118, 88, 58), (104, 76, 48)), pattern="rows", edge=(72, 50, 32), surface="wood"),
        TILE_GOJO_CENTER: TileStyle("flat", ((88, 64, 42), (78, 54, 34)), pattern="rows", edge=(54, 38, 24), surface="wood"),
    },
    layers=(
        FillLayer(TILE_GOJO_RIVER),
        RectLayer(TILE_GOJO_BANK, 0, 2, 0, 21),
        RectLayer(TILE_GOJO_BANK, 19, 21, 0, 21),
        RectLayer(TILE_GOJO_PLANK, 0, 21, 7, 14),
        RectLayer(TILE_GOJO_CENTER, 0, 21, 9, 12),
    ),
    pits=(
        PitZone(0.0, 0.0, float(MAP_COLS), 6.9, "VOID", railed=False, water=((16, 22, 36), (36, 52, 78))),
        PitZone(0.0, 14.1, float(MAP_COLS), float(MAP_ROWS), "VOID", railed=False, water=((16, 22, 36), (36, 52, 78))),
    ),
    props=(
        # Balustradas de madeira com corrimão contínuo e ponteiras giboshi de bronze
        (
            PropSpec("gojo_railing", 4.5, 7.0, {"x0": 2.0, "x1": 7.0}),
            PropSpec("gojo_railing", 10.5, 7.0, {"x0": 9.0, "x1": 12.0}),
            PropSpec("gojo_railing", 16.5, 7.0, {"x0": 14.0, "x1": 19.0}),
            PropSpec("gojo_railing", 4.5, 14.0, {"x0": 2.0, "x1": 7.0}),
            PropSpec("gojo_railing", 10.5, 14.0, {"x0": 9.0, "x1": 12.0}),
            PropSpec("gojo_railing", 16.5, 14.0, {"x0": 14.0, "x1": 19.0}),
        )
        # Braseiros de ferro crepitante (Kagaribi)
        + tuple(PropSpec("kagaribi", x, y) for x, y in _GOJO_KAGARIBI)
        # As 999 Lâminas da Lenda de Benkei cravadas nas margens de pedra
        + tuple(PropSpec("blade_cluster", x, y, {"seed": 10 + i * 7}) for i, (x, y) in enumerate(_GOJO_BLADES))
        # Pilares estruturais descendo ao rio
        + tuple(PropSpec("bridge_support", x, y) for x, y in _GOJO_SUPPORTS)
        # Lanternas e estátuas Jizo
        + tuple(PropSpec("stone_lantern", x, y) for x, y in _GOJO_LANTERNS)
        + tuple(PropSpec("jizo", x, y) for x, y in _GOJO_JIZO)
    ),
    spawns=SpawnRule(x_range=(4.0, 17.0), margin=3.0, min_distance=7.0, fallback=((5.5, 10.5), (15.5, 10.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=48,
    drift_petals=0.35,
    lighting=LightingEnvironment(
        ambient_color=(125, 140, 170), ambient_strength=0.46, vignette=0.36,
        lights=(
            tuple(LightSource(x, y, 0.9, (255, 195, 120), 2.8, flicker=0.12) for x, y in _GOJO_LANTERNS)
            + tuple(LightSource(x, y, 1.2, (255, 145, 50), 3.4, flicker=0.25) for x, y in _GOJO_KAGARIBI)
        ),
        atmosphere=(
            AtmosphereEffect("mist", density=0.80),
            AtmosphereEffect("fogbank", density=0.60),
            AtmosphereEffect("dust", density=0.30),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Beco Yoshiwara (O-Rin) — Ciclo 2
# ---------------------------------------------------------------------------
TILE_YOSHI_BUILDING = 73
TILE_YOSHI_COBBLE = 74
TILE_YOSHI_SIDEWALK = 75
TILE_YOSHI_PUDDLE = 76

_YOSHI_LANTERNS = ((6.8, 4.0), (14.2, 4.0), (6.8, 10.5), (14.2, 10.5), (6.8, 17.0), (14.2, 17.0))
_YOSHI_CURTAINS = ((5.2, 8.5), (15.8, 8.5), (5.2, 13.5), (15.8, 13.5))
_YOSHI_MACHIAS = (1.5, 5.5, 9.5, 13.5, 17.5)

YOSHIWARA_SPEC = ArenaSpec(
    id=ARENA_YOSHIWARA,
    name="Beco Yoshiwara",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(22, 14, 26),
    music="bgm_yoshiwara_alley",
    wind=WindSpec(1, 0.2, 0.35, 0.3),
    tile_styles={
        TILE_YOSHI_BUILDING: TileStyle("flat", ((36, 26, 32), (28, 20, 24)), pattern="parity", edge=(18, 12, 16), surface="wood"),
        TILE_YOSHI_COBBLE: TileStyle("flat", ((60, 56, 66), (50, 46, 54)), pattern="parity", edge=(34, 30, 38), surface="stone"),
        TILE_YOSHI_SIDEWALK: TileStyle("flat", ((96, 74, 56), (82, 62, 46)), pattern="rows", edge=(54, 40, 30), surface="wood"),
        TILE_YOSHI_PUDDLE: TileStyle("water", ((32, 20, 34), (68, 30, 48)), edge=(22, 14, 22), depth=0.08, speed_mult=0.90, surface="water"),
    },
    layers=(
        FillLayer(TILE_YOSHI_BUILDING),
        RectLayer(TILE_YOSHI_COBBLE, 5, 16, 0, 21),
        RectLayer(TILE_YOSHI_SIDEWALK, 5, 6, 0, 21),
        RectLayer(TILE_YOSHI_SIDEWALK, 15, 16, 0, 21),
        EllipseLayer(TILE_YOSHI_PUDDLE, cx=10.5, cy=6.5, radius=2.6, sx=1.0, sy=0.8),
        EllipseLayer(TILE_YOSHI_PUDDLE, cx=10.5, cy=14.5, radius=2.4, sx=1.0, sy=0.8),
    ),
    props=(
        tuple(PropSpec("machiya", 0.8, by, {"width": 4.2, "depth": 3.6, "is_transparent": False, "seed": 300 + i * 29, "burning": False, "style": "yoshiwara"})
              for i, by in enumerate(_YOSHI_MACHIAS))
        + tuple(PropSpec("machiya", 17.0, by, {"width": 4.2, "depth": 3.6, "is_transparent": True, "seed": 400 + i * 31, "burning": False, "style": "yoshiwara"})
                for i, by in enumerate(_YOSHI_MACHIAS))
        + tuple(PropSpec("paper_lantern", x, y) for x, y in _YOSHI_LANTERNS)
        + tuple(PropSpec("curtain", x, y) for x, y in _YOSHI_CURTAINS)
        + _folding_screen(8.2, 7.5, "x")
        + _folding_screen(12.8, 7.5, "x")
        + _folding_screen(8.2, 13.5, "x")
        + _folding_screen(12.8, 13.5, "x")
    ),
    spawns=SpawnRule(x_range=(7.0, 14.0), margin=3.0, min_distance=5.0, fallback=((8.0, 10.5), (13.0, 10.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=52,
    drift_petals=0.85,
    lighting=LightingEnvironment(
        ambient_color=(68, 44, 76), ambient_strength=0.36, vignette=0.46,
        lights=tuple(LightSource(x, y, 0.9, (255, 60, 85), 3.0, flicker=0.18) for x, y in _YOSHI_LANTERNS),
        atmosphere=(
            AtmosphereEffect("mist", density=0.72),
            AtmosphereEffect("fireflies", density=0.45),
            AtmosphereEffect("dust", density=0.35),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Arrozais Terraciados (Goro) — Ciclo 3
# ---------------------------------------------------------------------------
TILE_RICE_EARTH = 80
TILE_RICE_EARTH = 80
TILE_RICE_MUD = 81
TILE_RICE_WATER = 82
TILE_RICE_CROP = 83
TILE_RICE_TERRACE_HIGH = 95
TILE_RICE_WATER_HIGH = 96
TILE_RICE_CROP_HIGH = 97
TILE_RICE_TERRACE_MID = 98
TILE_RICE_WATER_MID = 99

_RICE_LANTERNS = ((4.5, 6.5), (16.5, 6.5), (4.5, 13.5), (16.5, 13.5))
_RICE_HAYBALES = ((8.5, 3.5), (12.5, 3.5), (2.5, 10.5), (18.5, 10.5), (8.5, 17.5), (12.5, 17.5))
_RICE_SCARECROWS = ((10.5, 2.2), (5.5, 9.5), (15.5, 16.5))
_RICE_CHUTES = (
    # Vertedouros do Patamar Superior para o Intermediário
    {"wx": 7.5, "wy": 6.8, "z_top": 0.28, "z_bottom": 0.14},
    {"wx": 13.5, "wy": 6.8, "z_top": 0.28, "z_bottom": 0.14},
    # Vertedouros do Patamar Intermediário para o Inferior
    {"wx": 7.5, "wy": 13.8, "z_top": 0.14, "z_bottom": 0.00},
    {"wx": 13.5, "wy": 13.8, "z_top": 0.14, "z_bottom": 0.00},
)

RICE_PADDIES_SPEC = ArenaSpec(
    id=ARENA_RICE_PADDIES,
    name="Arrozais Terraciados",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(36, 26, 20),
    music="bgm_rice_paddies",
    wind=WindSpec(1, 0.4, 0.5, 0.4),
    tile_styles={
        TILE_RICE_EARTH: TileStyle("flat", ((138, 96, 62), (124, 84, 52)), pattern="parity", edge=(88, 58, 36), surface="earth"),
        TILE_RICE_MUD: TileStyle("flat", ((98, 70, 48), (86, 60, 40)), edge=(64, 44, 28), speed_mult=0.88, surface="mud"),
        TILE_RICE_WATER: TileStyle("water", ((56, 44, 38), (170, 110, 60)), edge=(42, 32, 28), depth=0.08, speed_mult=0.92, surface="water"),
        TILE_RICE_CROP: TileStyle("flat", ((102, 134, 68), (88, 118, 56)), pattern="rows", edge=(62, 86, 40), surface="grass"),
        # Patamar Superior (Norte: Z = 0.28m)
        TILE_RICE_TERRACE_HIGH: TileStyle("slab", ((156, 112, 74), (142, 100, 64)), height=0.28, outline=True, top_edge=(102, 72, 46), surface="earth"),
        TILE_RICE_CROP_HIGH: TileStyle("slab", ((122, 154, 76), (106, 134, 62)), height=0.28, pattern="rows", outline=True, top_edge=(78, 102, 48), surface="grass"),
        TILE_RICE_WATER_HIGH: TileStyle("slab", ((68, 54, 46), (185, 125, 75)), height=0.22, outline=True, top_edge=(48, 38, 32), surface="water"),
        # Patamar Intermediário (Centro: Z = 0.14m)
        TILE_RICE_TERRACE_MID: TileStyle("slab", ((144, 102, 66), (130, 90, 56)), height=0.14, outline=True, top_edge=(92, 62, 38), surface="earth"),
        TILE_RICE_WATER_MID: TileStyle("slab", ((60, 46, 40), (175, 115, 65)), height=0.10, outline=True, top_edge=(44, 34, 28), surface="water"),
    },
    layers=(
        FillLayer(TILE_RICE_EARTH),
        # 1. Patamar Superior (Y: 0..6)
        RectLayer(TILE_RICE_TERRACE_HIGH, 0, 20, 0, 6),
        RectLayer(TILE_RICE_CROP_HIGH, 2, 7, 1, 5),
        RectLayer(TILE_RICE_CROP_HIGH, 13, 18, 1, 5),
        RectLayer(TILE_RICE_WATER_HIGH, 8, 12, 1, 5),
        # Rampa de conexão norte-centro
        RectLayer(TILE_RICE_TERRACE_MID, 10, 11, 5, 7),
        # 2. Patamar Intermediário (Y: 7..13)
        RectLayer(TILE_RICE_TERRACE_MID, 0, 20, 7, 13),
        RectLayer(TILE_RICE_WATER_MID, 3, 8, 8, 12),
        RectLayer(TILE_RICE_WATER_MID, 13, 18, 8, 12),
        # Rampa de conexão centro-sul
        RectLayer(TILE_RICE_EARTH, 10, 11, 12, 14),
        # 3. Patamar Inferior (Y: 14..20)
        RectLayer(TILE_RICE_MUD, 8, 13, 14, 20),
        RectLayer(TILE_RICE_WATER, 3, 7, 15, 19),
        RectLayer(TILE_RICE_WATER, 14, 18, 15, 19),
        RectLayer(TILE_RICE_CROP, 1, 2, 14, 18),
        RectLayer(TILE_RICE_CROP, 19, 20, 14, 18),
    ),
    props=(
        tuple(PropSpec("scarecrow", x, y, {"seed": 100 + i * 17}) for i, (x, y) in enumerate(_RICE_SCARECROWS))
        + tuple(PropSpec("hay_bale", x, y, {"seed": 200 + i}) for i, (x, y) in enumerate(_RICE_HAYBALES))
        + tuple(PropSpec("stone_lantern", x, y) for x, y in _RICE_LANTERNS)
        + tuple(PropSpec("water_chute", c["wx"], c["wy"], {"z_top": c["z_top"], "z_bottom": c["z_bottom"]}) for c in _RICE_CHUTES)
        + (
            PropSpec("tree", 1.8, 1.8),
            PropSpec("tree", 19.2, 1.8),
            PropSpec("crate", 10.5, 3.5),
            PropSpec("crate", 10.5, 18.2),
        )
    ),
    spawns=SpawnRule(x_range=(6.0, 15.0), margin=4.0, min_distance=6.5, fallback=((8.0, 10.5), (13.0, 10.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=45,
    drift_petals=0.65,
    lighting=LightingEnvironment(
        ambient_color=(195, 125, 75), ambient_strength=0.62, vignette=0.30,
        lights=tuple(LightSource(x, y, 0.9, (255, 175, 90), 2.8, flicker=0.15) for x, y in _RICE_LANTERNS),
        atmosphere=(
            AtmosphereEffect("dust", density=0.55),
            AtmosphereEffect("mist", density=0.45),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Moinho na Chuva (Ichi) — Ciclo 3
# ---------------------------------------------------------------------------
TILE_MILL_WOOD = 85
TILE_MILL_RIVER = 86
TILE_MILL_GRAVEL = 87
TILE_MILL_FOUNDATION = 88
TILE_MILL_BRIDGE = 89

_MILL_LANTERNS = ((6.5, 8.5), (14.5, 8.5), (6.5, 13.5), (14.5, 13.5))
_MILL_PILLARS = ((7.4, 8.8), (13.6, 8.8), (7.4, 13.2), (13.6, 13.2))

_MILL_RIVER_PIT = {
    "water": ((24, 46, 75), (95, 150, 210)),
    "wall_colors": ((40, 48, 58), (18, 24, 34)),
    "rim_color": (54, 62, 74),
    "depth": 1.5,
}

RAIN_MILL_SPEC = ArenaSpec(
    id=ARENA_RAIN_MILL,
    name="Moinho na Chuva",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(18, 22, 32),
    music="bgm_rain_mill",
    wind=WindSpec(-1, 0.6, 1.2, 0.8),
    tile_styles={
        TILE_MILL_WOOD: TileStyle("flat", ((78, 62, 52), (66, 52, 44)), pattern="rows", edge=(42, 32, 26), surface="wood"),
        TILE_MILL_RIVER: TileStyle("water", ((28, 48, 72), (64, 105, 145)), edge=(18, 32, 48), depth=0.25, speed_mult=0.45, surface="water"),
        TILE_MILL_GRAVEL: TileStyle("flat", ((88, 92, 102), (76, 80, 90)), pattern="parity", edge=(52, 56, 64), surface="gravel"),
        TILE_MILL_FOUNDATION: TileStyle("slab", ((50, 54, 62),), height=0.18, outline=True, surface="stone"),
        TILE_MILL_BRIDGE: TileStyle("anchor", surface="wood"),
    },
    layers=(
        FillLayer(TILE_MILL_GRAVEL),
        RectLayer(TILE_MILL_RIVER, 8, 13, 0, 21),
        RectLayer(TILE_MILL_FOUNDATION, 2, 7, 4, 17),
        RectLayer(TILE_MILL_WOOD, 3, 6, 5, 16),
        RectLayer(TILE_MILL_BRIDGE, 7, 14, 9, 12),
    ),
    props=(
        (PropSpec("watermill", 7.6, 7.0, {"radius": 1.7, "speed": 1.4}),)
        + tuple(PropSpec("pillar", x, y, {"width": 0.5, "depth": 0.5, "height": 1.4, "color": (56, 46, 40)}) for x, y in _MILL_PILLARS)
        + tuple(PropSpec("stone_lantern", x, y) for x, y in _MILL_LANTERNS)
        + (
            PropSpec("cabin", 2.6, 4.5, {"width": 4.5, "depth": 3.0, "height": 2.2, "color": (65, 52, 45)}),
            PropSpec("crate", 4.5, 9.0),
            PropSpec("crate", 5.5, 9.0),
            PropSpec("barrel", 4.5, 13.0, {"width": 0.7, "depth": 0.7, "height": 0.8, "color": (96, 64, 42)}),
            PropSpec("rock", 15.5, 5.0, {"radius": 0.65, "height": 0.7}),
            PropSpec("rock", 16.5, 16.0, {"radius": 0.8, "height": 0.9}),
        )
    ),
    structures=(StructureSpec("roof_beam", TILE_MILL_BRIDGE, {"x0": 7.0, "y0": 9.0, "x1": 14.5, "y1": 13.0}),),
    pits=(
        PitZone(8.0, 0.0, 13.0, 8.8, "VOID", railed=False, **_MILL_RIVER_PIT),
        PitZone(8.0, 12.2, 13.0, 21.0, "VOID", railed=False, **_MILL_RIVER_PIT),
    ),
    spawns=SpawnRule(x_range=(4.0, 17.0), margin=4.0, min_distance=6.5, fallback=((5.5, 11.0), (15.5, 11.0))),
    stage=StageSpec(10.5, 11.0),
    drift_count=60,
    drift_petals=0.95,
    lighting=LightingEnvironment(
        ambient_color=(85, 95, 125), ambient_strength=0.40, vignette=0.45,
        lights=tuple(LightSource(x, y, 0.9, (200, 220, 255), 2.8, flicker=0.15) for x, y in _MILL_LANTERNS),
        atmosphere=(
            AtmosphereEffect("rain", density=1.0),
            AtmosphereEffect("mist", density=0.75),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Cemitério Gótico (Ciclo 4 - Valerius)
# ---------------------------------------------------------------------------
TILE_CEMETERY_DIRT = 101
TILE_CEMETERY_FLAGSTONE = 102
TILE_CEMETERY_GRAVEPLOT = 103
TILE_CEMETERY_CRYPT_BASE = 104

_CEMETERY_HEADSTONES = (
    # Quadrante Noroeste (NW)
    PropSpec("gothic_headstone", 4.0, 4.2, {"style": "cross"}),
    PropSpec("gothic_headstone", 6.2, 4.2, {"style": "slab"}),
    PropSpec("gothic_headstone", 4.0, 6.4, {"style": "slab"}),
    PropSpec("gothic_headstone", 6.2, 6.4, {"style": "cross"}),
    # Quadrante Nordeste (NE)
    PropSpec("gothic_headstone", 14.5, 4.2, {"style": "slab"}),
    PropSpec("gothic_headstone", 16.8, 4.2, {"style": "cross"}),
    PropSpec("gothic_headstone", 14.5, 6.4, {"style": "cross"}),
    PropSpec("gothic_headstone", 16.8, 6.4, {"style": "slab"}),
    # Quadrante Sudoeste (SW)
    PropSpec("gothic_headstone", 4.0, 14.2, {"style": "cross"}),
    PropSpec("gothic_headstone", 6.2, 14.2, {"style": "slab"}),
    PropSpec("gothic_headstone", 4.0, 16.5, {"style": "slab"}),
    PropSpec("gothic_headstone", 6.2, 16.5, {"style": "cross"}),
    # Quadrante Sudeste (SE)
    PropSpec("gothic_headstone", 14.5, 14.2, {"style": "slab"}),
    PropSpec("gothic_headstone", 16.8, 14.2, {"style": "cross"}),
    PropSpec("gothic_headstone", 14.5, 16.5, {"style": "cross"}),
    PropSpec("gothic_headstone", 16.8, 16.5, {"style": "slab"}),
)

_CEMETERY_TREES = (
    PropSpec("dead_tree", 2.2, 2.5),
    PropSpec("dead_tree", 18.8, 2.5),
    PropSpec("dead_tree", 2.0, 18.5),
    PropSpec("dead_tree", 18.5, 18.5),
)

_CEMETERY_FENCES = (
    PropSpec("iron_fence", 7.6, 2.2, {"length": 1.6, "orientation": "x"}),
    PropSpec("iron_fence", 13.4, 2.2, {"length": 1.6, "orientation": "x"}),
    PropSpec("iron_fence", 2.0, 10.5, {"length": 1.8, "orientation": "y"}),
    PropSpec("iron_fence", 19.0, 10.5, {"length": 1.8, "orientation": "y"}),
)

_CEMETERY_LIGHTS = (
    LightSource(10.5, 2.2, 0.8, (60, 225, 180), 3.4, flicker=0.20),
    LightSource(5.0, 5.5, 0.6, (120, 180, 240), 2.5, flicker=0.15),
    LightSource(15.5, 5.5, 0.6, (120, 180, 240), 2.5, flicker=0.15),
    LightSource(5.0, 15.5, 0.6, (120, 180, 240), 2.5, flicker=0.15),
    LightSource(15.5, 15.5, 0.6, (120, 180, 240), 2.5, flicker=0.15),
)

GOTHIC_CEMETERY_SPEC = ArenaSpec(
    id=ARENA_GOTHIC_CEMETERY,
    name="Cemitério Gótico",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(12, 10, 16),
    music="bgm_prussian_cemetery",
    wind=WindSpec(0.8, 0.2, 0.5, 0.6),
    tile_styles={
        TILE_CEMETERY_DIRT: TileStyle("flat", ((36, 34, 40), (44, 40, 48)), pattern="parity", edge=(22, 20, 26), surface="earth"),
        TILE_CEMETERY_FLAGSTONE: TileStyle("flat", ((64, 66, 74), (54, 56, 64)), pattern="parity", edge=(38, 40, 46), surface="stone"),
        TILE_CEMETERY_GRAVEPLOT: TileStyle("flat", ((26, 24, 30), (32, 28, 36)), pattern="parity", edge=(18, 16, 22), surface="earth"),
        TILE_CEMETERY_CRYPT_BASE: TileStyle("slab", ((48, 50, 58),), height=0.16, outline=True, top_edge=(32, 34, 40), surface="stone"),
    },
    layers=(
        FillLayer(TILE_CEMETERY_DIRT),
        # Caminhos em cruz de lajes de granito
        RectLayer(TILE_CEMETERY_FLAGSTONE, 9, 11, 0, 20),
        RectLayer(TILE_CEMETERY_FLAGSTONE, 0, 20, 9, 11),
        EllipseLayer(TILE_CEMETERY_FLAGSTONE, cx=10.5, cy=10.5, radius=3.6),
        # Covas e talhões fúnebres nos 4 quadrantes
        RectLayer(TILE_CEMETERY_GRAVEPLOT, 3, 7, 3, 7),
        RectLayer(TILE_CEMETERY_GRAVEPLOT, 13, 17, 3, 7),
        RectLayer(TILE_CEMETERY_GRAVEPLOT, 3, 7, 13, 17),
        RectLayer(TILE_CEMETERY_GRAVEPLOT, 13, 17, 13, 17),
        # Base da cripta monumental ao norte
        RectLayer(TILE_CEMETERY_CRYPT_BASE, 9, 12, 1, 3),
    ),
    props=(
        (PropSpec("mausoleum", 9.3, 1.2, {"width": 2.4, "depth": 1.8, "height": 2.3}),)
        + _CEMETERY_TREES
        + _CEMETERY_HEADSTONES
        + _CEMETERY_FENCES
    ),
    hazards=(HazardSpec("gothic_cemetery_hazard", {}),),
    playable_bounds=(2.0, 3.0, 19.0, 19.0),
    spawns=SpawnRule(x_range=(6.0, 15.0), margin=4.0, min_distance=6.5, fallback=((6.5, 10.5), (14.5, 10.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=35,
    drift_petals=0.15,
    lighting=LightingEnvironment(
        ambient_color=(65, 80, 120), ambient_strength=0.40, vignette=0.50,
        lights=_CEMETERY_LIGHTS,
        atmosphere=(
            AtmosphereEffect("mist", density=0.90),
            AtmosphereEffect("fogbank", density=0.70),
            AtmosphereEffect("dust", density=0.35),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Pavilhão Astral Heian (Ciclo 4 - Seimei)
# ---------------------------------------------------------------------------
TILE_HEIAN_COURT = 105
TILE_HEIAN_BORDER = 106
TILE_HEIAN_MANDALA = 107
TILE_HEIAN_PEBBLE = 108

_HEIAN_TORO_PROPS = (
    PropSpec("heian_toro", 6.8, 6.8),
    PropSpec("heian_toro", 14.2, 6.8),
    PropSpec("heian_toro", 6.8, 14.2),
    PropSpec("heian_toro", 14.2, 14.2),
    PropSpec("heian_toro", 7.2, 18.2),
    PropSpec("heian_toro", 13.8, 18.2),
)

_HEIAN_GINKGO = (
    PropSpec("ginkgo_tree", 2.4, 3.5),
    PropSpec("ginkgo_tree", 18.6, 3.5),
    PropSpec("ginkgo_tree", 2.2, 16.5),
    PropSpec("ginkgo_tree", 18.8, 16.5),
)

_HEIAN_LIGHTS = (
    LightSource(6.8, 6.8, 0.9, (255, 190, 80), 2.8, flicker=0.12),
    LightSource(14.2, 6.8, 0.9, (255, 190, 80), 2.8, flicker=0.12),
    LightSource(6.8, 14.2, 0.9, (255, 190, 80), 2.8, flicker=0.12),
    LightSource(14.2, 14.2, 0.9, (255, 190, 80), 2.8, flicker=0.12),
    LightSource(7.2, 18.2, 0.9, (255, 180, 70), 2.5, flicker=0.12),
    LightSource(13.8, 18.2, 0.9, (255, 180, 70), 2.5, flicker=0.12),
    LightSource(10.5, 10.5, 0.5, (160, 140, 255), 3.2, flicker=0.08),
)

HEIAN_SHRINE_SPEC = ArenaSpec(
    id=ARENA_HEIAN_SHRINE,
    name="Pavilhão Astral Heian",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(18, 14, 28),
    music="bgm_heian_temple",
    wind=WindSpec(0.5, 0.4, 0.35, 0.30),
    tile_styles={
        TILE_HEIAN_COURT: TileStyle("flat", ((228, 224, 216), (214, 210, 202)), pattern="parity", edge=(185, 180, 170), surface="stone"),
        TILE_HEIAN_BORDER: TileStyle("flat", ((180, 48, 38), (160, 40, 32)), pattern="parity", edge=(120, 30, 24), surface="stone"),
        TILE_HEIAN_MANDALA: TileStyle("flat", ((52, 48, 82), (68, 62, 105)), pattern="parity", edge=(195, 165, 60), surface="stone"),
        TILE_HEIAN_PEBBLE: TileStyle("flat", ((196, 192, 186), (180, 176, 170)), pattern="parity", edge=(150, 146, 140), surface="gravel"),
    },
    layers=(
        FillLayer(TILE_HEIAN_PEBBLE),
        # Pátio cerimonial
        RectLayer(TILE_HEIAN_BORDER, 3, 17, 3, 17),
        RectLayer(TILE_HEIAN_COURT, 4, 16, 4, 16),
        # Corredor sagrado de entrada (Sul)
        RectLayer(TILE_HEIAN_BORDER, 8, 12, 16, 20),
        RectLayer(TILE_HEIAN_COURT, 9, 11, 16, 20),
        # Mandala Astral de Onmyodo no centro
        EllipseLayer(TILE_HEIAN_BORDER, cx=10.5, cy=10.5, radius=4.6),
        EllipseLayer(TILE_HEIAN_MANDALA, cx=10.5, cy=10.5, radius=4.0),
        EllipseLayer(TILE_HEIAN_COURT, cx=10.5, cy=10.5, radius=2.2),
        EllipseLayer(TILE_HEIAN_MANDALA, cx=10.5, cy=10.5, radius=1.0),
    ),
    props=(
        (
            PropSpec("heian_torii", 10.5, 18.0),
            PropSpec("shimenawa", 10.5, 18.0, {"span": 4.0, "z": 2.7, "ribbons": 5}),
            PropSpec("shimenawa", 10.5, 3.5, {"span": 6.0, "z": 2.6, "ribbons": 7}),
        )
        + _HEIAN_GINKGO
        + _HEIAN_TORO_PROPS
    ),
    hazards=(HazardSpec("heian_shrine_hazard", {}),),
    playable_bounds=(2.0, 2.0, 19.0, 19.0),
    spawns=SpawnRule(x_range=(5.0, 16.0), margin=4.0, min_distance=6.5, fallback=((6.5, 10.5), (14.5, 10.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=55,
    drift_petals=0.85,
    lighting=LightingEnvironment(
        ambient_color=(120, 95, 145), ambient_strength=0.50, vignette=0.35,
        lights=_HEIAN_LIGHTS,
        atmosphere=(
            AtmosphereEffect("sunbeams", density=0.45),
            AtmosphereEffect("mist", density=0.40),
            AtmosphereEffect("dust", density=0.50),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Floresta dos Pinheiros (Ciclo 5 - Daiki)
# ---------------------------------------------------------------------------
TILE_PINE_MOSS = 109
TILE_PINE_EARTH = 110
TILE_PINE_STEPS = 111

_PINE_TREES = (
    PropSpec("akamatsu_pine", 2.8, 3.0, {"scale": 1.10}),
    PropSpec("akamatsu_pine", 18.2, 3.0, {"scale": 1.15}),
    PropSpec("akamatsu_pine", 2.5, 10.5, {"scale": 1.00}),
    PropSpec("akamatsu_pine", 18.5, 10.5, {"scale": 1.05}),
    PropSpec("akamatsu_pine", 2.8, 18.0, {"scale": 1.10}),
    PropSpec("akamatsu_pine", 18.2, 18.0, {"scale": 1.08}),
)

_PINE_LIGHTS = (
    LightSource(6.5, 4.2, 0.9, (255, 200, 110), 2.8, flicker=0.14),
    LightSource(14.5, 4.2, 0.9, (255, 200, 110), 2.8, flicker=0.14),
    LightSource(10.5, 2.6, 0.8, (255, 215, 120), 3.2, flicker=0.10),
    LightSource(10.5, 10.5, 1.2, (240, 220, 145), 4.0, flicker=0.05),
)

SACRED_PINES_SPEC = ArenaSpec(
    id=ARENA_SACRED_PINES,
    name="Floresta dos Pinheiros",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(28, 38, 32),
    music="bgm_pine_forest",
    wind=WindSpec(1.0, 0.55, 1.35, 0.75),
    tile_styles={
        TILE_PINE_MOSS: TileStyle("flat", ((58, 92, 52), (50, 82, 46)), pattern="third", edge=(36, 62, 34), surface="grass"),
        TILE_PINE_EARTH: TileStyle("flat", ((132, 98, 66), (120, 88, 58)), pattern="parity", edge=(88, 64, 42), surface="dirt"),
        TILE_PINE_STEPS: TileStyle("flat", ((138, 142, 134), (124, 128, 120)), pattern="rows", edge=(88, 92, 86), surface="stone"),
    },
    layers=(
        FillLayer(TILE_PINE_MOSS),
        # Trilha de degraus de pedra musgosa norte-sul
        RectLayer(TILE_PINE_STEPS, 9, 12, 0, 21),
        # Clareira central de terra batida e agulhas de pinheiro
        EllipseLayer(TILE_PINE_EARTH, cx=10.5, cy=10.5, radius=6.4),
        EllipseLayer(TILE_PINE_STEPS, cx=10.5, cy=10.5, radius=1.8),
    ),
    props=(
        _PINE_TREES
        + (
            PropSpec("mountain_hokora", 10.5, 2.6),
            PropSpec("stone_lantern", 6.5, 4.2),
            PropSpec("stone_lantern", 14.5, 4.2),
            PropSpec("jizo", 6.2, 16.5),
            PropSpec("jizo", 14.8, 16.5),
            PropSpec("timber_logs", 4.6, 7.2),
            PropSpec("timber_logs", 16.4, 14.2),
            PropSpec("rock", 4.4, 14.2, {"radius": 0.75, "height": 1.1}),
            PropSpec("rock", 16.6, 6.8, {"radius": 0.80, "height": 1.2}),
        )
    ),
    hazards=(HazardSpec("pine_forest_hazard", {}),),
    playable_bounds=(2.5, 2.5, 18.5, 18.5),
    spawns=SpawnRule(x_range=(5.0, 16.0), margin=4.0, min_distance=6.5, fallback=((6.5, 10.5), (14.5, 10.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=52,
    drift_petals=0.45,
    lighting=LightingEnvironment(
        ambient_color=(215, 195, 145), ambient_strength=0.68, vignette=0.28,
        lights=_PINE_LIGHTS,
        atmosphere=(
            AtmosphereEffect("sunbeams", density=0.65),
            AtmosphereEffect("mist", density=0.45),
            AtmosphereEffect("dust", density=0.50),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Taiga de Ezo (Ciclo 5 - Aoi)
# ---------------------------------------------------------------------------
TILE_EZO_SNOW = 112
TILE_EZO_ICE = 113
TILE_EZO_FROZEN_EARTH = 114

_EZO_SPRUCES = (
    PropSpec("snow_spruce", 2.4, 2.8, {"scale": 1.10}),
    PropSpec("snow_spruce", 18.6, 2.8, {"scale": 1.05}),
    PropSpec("snow_spruce", 2.2, 10.5, {"scale": 1.00}),
    PropSpec("snow_spruce", 18.8, 10.5, {"scale": 1.08}),
    PropSpec("snow_spruce", 2.6, 18.2, {"scale": 1.12}),
    PropSpec("snow_spruce", 18.4, 18.2, {"scale": 1.05}),
)

_EZO_INAUS = (
    PropSpec("ainu_inau", 5.8, 4.2),
    PropSpec("ainu_inau", 15.2, 4.2),
    PropSpec("ainu_inau", 5.8, 16.8),
    PropSpec("ainu_inau", 15.2, 16.8),
)

_EZO_LIGHTS = (
    LightSource(6.8, 6.8, 0.7, (255, 155, 65), 3.6, flicker=0.32),
    LightSource(14.2, 14.2, 0.7, (255, 155, 65), 3.6, flicker=0.32),
    LightSource(10.5, 10.5, 1.0, (175, 215, 255), 3.4, flicker=0.06),
)

EZO_TUNDRA_SPEC = ArenaSpec(
    id=ARENA_EZO_TUNDRA,
    name="Taiga de Ezo",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(20, 32, 48),
    music="bgm_ezo_taiga",
    wind=WindSpec(1.0, 0.65, 1.45, 0.85),
    tile_styles={
        TILE_EZO_SNOW: TileStyle("flat", ((226, 236, 248), (212, 224, 240)), pattern="parity", edge=(170, 188, 212), surface="sand"),
        TILE_EZO_ICE: TileStyle("flat", ((152, 198, 236), (138, 184, 226)), pattern="rows", edge=(102, 148, 194), speed_mult=1.18, surface="marble"),
        TILE_EZO_FROZEN_EARTH: TileStyle("flat", ((96, 88, 86), (84, 76, 74)), pattern="parity", edge=(62, 56, 56), surface="earth"),
    },
    layers=(
        FillLayer(TILE_EZO_SNOW),
        # Anel externo de gelo escorregadio azul-cristalino
        EllipseLayer(TILE_EZO_ICE, cx=10.5, cy=10.5, radius=7.6),
        # Clareira central de neve compactada
        EllipseLayer(TILE_EZO_SNOW, cx=10.5, cy=10.5, radius=5.4),
        # Círculos de terra descongelada ao redor das fogueiras de caça
        EllipseLayer(TILE_EZO_FROZEN_EARTH, cx=6.8, cy=6.8, radius=1.5),
        EllipseLayer(TILE_EZO_FROZEN_EARTH, cx=14.2, cy=14.2, radius=1.5),
    ),
    props=(
        _EZO_SPRUCES
        + _EZO_INAUS
        + (
            PropSpec("campfire", 6.8, 6.8),
            PropSpec("campfire", 14.2, 14.2),
            PropSpec("hide_rack", 10.5, 3.0),
            PropSpec("hide_rack", 4.2, 13.5),
            PropSpec("snare", 13.8, 7.2),
            PropSpec("snare", 7.2, 13.8),
            PropSpec("rock", 16.2, 8.2, {"radius": 0.72, "height": 1.0}),
        )
    ),
    hazards=(HazardSpec("ezo_taiga_hazard", {}),),
    playable_bounds=(2.5, 2.5, 18.5, 18.5),
    spawns=SpawnRule(x_range=(5.0, 16.0), margin=4.0, min_distance=6.5, fallback=((6.5, 10.5), (14.5, 10.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=64,
    drift_petals=0.0,
    lighting=LightingEnvironment(
        ambient_color=(155, 188, 230), ambient_strength=0.62, vignette=0.34,
        lights=_EZO_LIGHTS,
        atmosphere=(
            AtmosphereEffect("mist", density=0.65),
            AtmosphereEffect("embers", density=0.45),
            AtmosphereEffect("fogbank", density=0.40),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Dohyo Sagrado (Ciclo 6 - Raiden)
# ---------------------------------------------------------------------------
TILE_DOHYO_MOSS = 123
TILE_DOHYO_WOOD = 115
TILE_DOHYO_RING = 116
TILE_DOHYO_CLAY = 117
TILE_DOHYO_DIRT = 124

_DOHYO_LIGHTS = (
    LightSource(5.2, 5.2, 1.8, (255, 185, 95), 3.8, flicker=0.15),
    LightSource(15.8, 5.2, 1.8, (255, 185, 95), 3.8, flicker=0.15),
    LightSource(15.8, 15.8, 1.8, (255, 185, 95), 3.8, flicker=0.15),
    LightSource(5.2, 15.8, 1.8, (255, 185, 95), 3.8, flicker=0.15),
    LightSource(10.5, 3.8, 1.2, (255, 160, 60), 3.5, flicker=0.22),
    LightSource(10.5, 17.2, 1.2, (255, 160, 60), 3.5, flicker=0.22),
    LightSource(10.5, 10.5, 2.4, (255, 235, 180), 5.5, flicker=0.04),
)

SACRED_DOHYO_SPEC = ArenaSpec(
    id=ARENA_DOHYO,
    name="Dohyo Sagrado",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(20, 24, 18),
    music="bgm_sacred_dohyo",
    wind=WindSpec(0.4, 0.20, 0.60, 0.35),
    tile_styles={
        TILE_DOHYO_MOSS: TileStyle("flat", ((32, 64, 38), (26, 52, 30)), pattern="third", edge=(18, 38, 22), surface="grass"),
        TILE_DOHYO_WOOD: TileStyle("flat", ((138, 102, 68), (124, 90, 58)), pattern="rows", edge=(94, 68, 42), surface="wood"),
        TILE_DOHYO_RING: TileStyle("flat", ((198, 168, 114), (184, 154, 102)), pattern="parity", edge=(146, 118, 76), surface="grass"),
        TILE_DOHYO_CLAY: TileStyle("flat", ((182, 142, 98), (170, 130, 88)), pattern="parity", edge=(132, 98, 64), surface="sand"),
        TILE_DOHYO_DIRT: TileStyle("flat", ((154, 118, 80), (138, 104, 68)), pattern="parity", edge=(104, 76, 48), surface="sand"),
    },
    layers=(
        # Vegetação densa e solo de bosque sagrado circundando o santuário
        FillLayer(TILE_DOHYO_MOSS),
        # Caminho de terra no canto inferior direito que dá acesso ao santuário
        RectLayer(TILE_DOHYO_DIRT, 17, 21, 17, 21),
        RectLayer(TILE_DOHYO_DIRT, 15, 18, 15, 18),
        RectLayer(TILE_DOHYO_DIRT, 14, 16, 14, 16),
        # Passadiço circular de madeira Hinoki delimitado
        EllipseLayer(TILE_DOHYO_WOOD, cx=10.5, cy=10.5, radius=7.2),
        # Fardos de palha Shōbu-tawara
        EllipseLayer(TILE_DOHYO_RING, cx=10.5, cy=10.5, radius=5.2),
        # Terra batida sagrada Arakida no centro
        EllipseLayer(TILE_DOHYO_CLAY, cx=10.5, cy=10.5, radius=4.8),
    ),
    props=(
        # Pilares cerimoniais Shihobashira com borlas direcionais Fusa
        PropSpec("dohyo_post", 5.2, 5.2, {"fusa": "green"}),
        PropSpec("dohyo_post", 15.8, 5.2, {"fusa": "red"}),
        PropSpec("dohyo_post", 15.8, 15.8, {"fusa": "white"}),
        PropSpec("dohyo_post", 5.2, 15.8, {"fusa": "black"}),
        # Montes de sal sagrado purificador Sanbō
        PropSpec("salt_mound", 5.2, 10.5),
        PropSpec("salt_mound", 15.8, 10.5),
        # Braseiros cerimoniais nas bordas norte/sul
        PropSpec("dohyo_brazier", 10.5, 3.8),
        PropSpec("dohyo_brazier", 10.5, 17.2),
        # Grandes incensários cerimoniais nos cantos da arena exalando plumas de fumaça aromática
        PropSpec("large_censer", 4.0, 4.0),
        PropSpec("large_censer", 17.0, 4.0),
        PropSpec("large_censer", 4.0, 17.0),
        PropSpec("large_censer", 16.5, 16.5),
        # Lanternas de pedra ladeando o caminho de terra do canto inferior direito
        PropSpec("stone_lantern", 18.8, 15.2),
        PropSpec("stone_lantern", 15.2, 18.8),
        # --- Floresta densa e intransponível preenchendo a área verde ---
        # Faixa Norte (y <= 3.5)
        PropSpec("akamatsu_pine", 1.2, 1.2),
        PropSpec("akamatsu_pine", 3.6, 1.0),
        PropSpec("akamatsu_pine", 6.2, 1.2),
        PropSpec("akamatsu_pine", 8.8, 1.0),
        PropSpec("akamatsu_pine", 11.5, 1.2),
        PropSpec("akamatsu_pine", 14.2, 1.0),
        PropSpec("akamatsu_pine", 16.8, 1.2),
        PropSpec("akamatsu_pine", 19.5, 1.2),
        PropSpec("pine", 2.4, 2.4),
        PropSpec("pine", 5.0, 2.0),
        PropSpec("pine", 7.6, 1.8),
        PropSpec("pine", 10.5, 1.6),
        PropSpec("pine", 13.2, 1.8),
        PropSpec("pine", 15.8, 2.0),
        PropSpec("pine", 18.2, 2.4),
        PropSpec("sacred_bush", 1.5, 3.0),
        PropSpec("sacred_bush", 3.8, 2.8),
        PropSpec("sacred_bush", 6.0, 2.8),
        PropSpec("sacred_bush", 8.4, 2.6),
        PropSpec("sacred_bush", 12.6, 2.6),
        PropSpec("sacred_bush", 15.0, 2.8),
        PropSpec("sacred_bush", 17.4, 2.8),
        PropSpec("sacred_bush", 19.8, 3.0),
        # Faixa Sul (y >= 17.5, exceto canto sudeste reservado ao caminho de terra)
        PropSpec("akamatsu_pine", 1.2, 19.5),
        PropSpec("akamatsu_pine", 3.6, 19.5),
        PropSpec("akamatsu_pine", 6.2, 19.2),
        PropSpec("akamatsu_pine", 8.8, 19.5),
        PropSpec("akamatsu_pine", 11.5, 19.2),
        PropSpec("akamatsu_pine", 13.8, 19.5),
        PropSpec("pine", 2.4, 18.2),
        PropSpec("pine", 5.0, 18.4),
        PropSpec("pine", 7.6, 18.2),
        PropSpec("pine", 10.5, 18.8),
        PropSpec("pine", 12.8, 18.4),
        PropSpec("sacred_bush", 1.5, 17.2),
        PropSpec("sacred_bush", 3.8, 17.0),
        PropSpec("sacred_bush", 6.0, 17.2),
        PropSpec("sacred_bush", 8.4, 17.2),
        PropSpec("sacred_bush", 12.4, 17.2),
        # Faixa Oeste (x <= 3.5)
        PropSpec("akamatsu_pine", 1.0, 4.0),
        PropSpec("akamatsu_pine", 1.2, 6.8),
        PropSpec("akamatsu_pine", 1.0, 9.5),
        PropSpec("akamatsu_pine", 1.2, 12.2),
        PropSpec("akamatsu_pine", 1.0, 15.0),
        PropSpec("akamatsu_pine", 1.2, 17.2),
        PropSpec("pine", 2.2, 5.0),
        PropSpec("pine", 2.4, 7.8),
        PropSpec("pine", 2.2, 10.5),
        PropSpec("pine", 2.4, 13.2),
        PropSpec("pine", 2.2, 15.8),
        PropSpec("sacred_bush", 3.0, 4.5),
        PropSpec("sacred_bush", 3.0, 7.2),
        PropSpec("sacred_bush", 3.0, 11.2),
        PropSpec("sacred_bush", 3.0, 14.0),
        PropSpec("sacred_bush", 3.0, 16.5),
        # Faixa Leste (x >= 17.5, y <= 14.5)
        PropSpec("akamatsu_pine", 19.5, 4.0),
        PropSpec("akamatsu_pine", 19.2, 6.8),
        PropSpec("akamatsu_pine", 19.5, 9.5),
        PropSpec("akamatsu_pine", 19.2, 12.2),
        PropSpec("akamatsu_pine", 19.5, 14.0),
        PropSpec("pine", 18.4, 5.0),
        PropSpec("pine", 18.2, 7.8),
        PropSpec("pine", 18.4, 10.5),
        PropSpec("pine", 18.2, 13.0),
        PropSpec("sacred_bush", 17.5, 4.5),
        PropSpec("sacred_bush", 17.5, 7.2),
        PropSpec("sacred_bush", 17.5, 11.2),
        PropSpec("sacred_bush", 17.5, 13.8),
        # Sebes protetoras contornando o anel do Dohyo
        PropSpec("sacred_bush", 3.4, 6.8),
        PropSpec("sacred_bush", 3.4, 10.5),
        PropSpec("sacred_bush", 3.4, 14.2),
        PropSpec("sacred_bush", 17.6, 6.8),
        PropSpec("sacred_bush", 17.6, 10.5),
        PropSpec("sacred_bush", 6.8, 3.4),
        PropSpec("sacred_bush", 10.5, 3.4),
        PropSpec("sacred_bush", 14.2, 3.4),
        PropSpec("sacred_bush", 6.8, 17.6),
        PropSpec("sacred_bush", 10.5, 17.6),
    ),
    hazards=(HazardSpec("dohyo_hazard", {}),),
    playable_bounds=(3.8, 3.8, 17.2, 17.2),
    spawns=SpawnRule(x_range=(7.5, 13.5), margin=4.0, min_distance=5.5, fallback=((8.5, 10.5), (12.5, 10.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=42,
    drift_petals=0.0,
    lighting=LightingEnvironment(
        ambient_color=(235, 205, 155), ambient_strength=0.72, vignette=0.32,
        lights=_DOHYO_LIGHTS,
        atmosphere=(
            AtmosphereEffect("sunbeams", density=0.55),
            AtmosphereEffect("dust", density=0.45),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Armazém de Dejima com Doca Chuvosa (Ciclo 6 - Hendrika)
# ---------------------------------------------------------------------------
TILE_DEJIMA_WOOD = 119
TILE_DEJIMA_PLANK = 120
TILE_DEJIMA_WET_PLANK = 121
TILE_DEJIMA_WATER = 122

_DEJIMA_LIGHTS = (
    LightSource(4.5, 5.5, 1.2, (255, 195, 115), 3.8, flicker=0.12),
    LightSource(4.5, 15.5, 1.2, (255, 195, 115), 3.8, flicker=0.12),
    LightSource(7.5, 8.2, 1.8, (245, 185, 95), 3.5, flicker=0.15),
    LightSource(7.5, 12.8, 1.8, (245, 185, 95), 3.5, flicker=0.15),
    LightSource(10.5, 7.5, 1.4, (140, 185, 235), 4.2, flicker=0.08),
    LightSource(10.5, 16.5, 1.4, (140, 185, 235), 4.5, flicker=0.10),
    LightSource(16.5, 5.5, 0.8, (135, 195, 245), 3.5, flicker=0.18),
    LightSource(16.5, 15.5, 0.8, (135, 195, 245), 3.8, flicker=0.18),
)

DEJIMA_WAREHOUSE_SPEC = ArenaSpec(
    id=ARENA_DEJIMA,
    name="Armazém de Dejima",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(16, 22, 30),
    music="bgm_dejima_dock",
    wind=WindSpec(1.2, 0.70, 1.65, 0.85),
    tile_styles={
        TILE_DEJIMA_WOOD: TileStyle("flat", ((118, 82, 54), (104, 72, 46)), pattern="rows", edge=(72, 48, 30), surface="wood"),
        TILE_DEJIMA_PLANK: TileStyle("slab", ((96, 82, 72), (84, 72, 62)), height=0.22, edge=(58, 48, 40), speed_mult=1.05, surface="wood", outline=True),
        TILE_DEJIMA_WET_PLANK: TileStyle("slab", ((68, 84, 98), (56, 72, 86)), height=0.20, edge=(42, 54, 66), speed_mult=1.12, surface="marble", outline=True),
        TILE_DEJIMA_WATER: TileStyle("water", ((22, 38, 54), (16, 30, 44)), edge=(12, 22, 32), depth=0.35, speed_mult=0.50, surface="water"),
    },
    layers=(
        # 1. Base geral do canal portuário (águas escuras)
        FillLayer(TILE_DEJIMA_WATER),
        # 2. Área interna reduzida do armazém (x de 1 a 7): piso de madeira nobre
        RectLayer(TILE_DEJIMA_WOOD, 1, 7, 2, 19),
        # 3. Grande Plataforma Superior e Central do Cais (x de 7 a 16, y de 3 a 11)
        RectLayer(TILE_DEJIMA_PLANK, 7, 16, 3, 11),
        RectLayer(TILE_DEJIMA_WET_PLANK, 14, 16, 3, 11),
        # 4. Grandes Pranchas ligando o Cais Superior ao Cais Inferior sobre o Buraco 1
        RectLayer(TILE_DEJIMA_PLANK, 7, 9, 12, 13),   # Prancha larga oeste
        RectLayer(TILE_DEJIMA_PLANK, 14, 16, 12, 13), # Prancha larga leste
        # 5. Doca Inferior Expandida (fazendo excelente uso do espaço inferior com grandes pranchas)
        RectLayer(TILE_DEJIMA_PLANK, 7, 16, 14, 15),  # Plataforma norte do cais inferior
        RectLayer(TILE_DEJIMA_PLANK, 7, 9, 16, 17),   # Prancha larga oeste do cais inferior
        RectLayer(TILE_DEJIMA_PLANK, 14, 16, 16, 17), # Prancha larga leste do cais inferior
        RectLayer(TILE_DEJIMA_PLANK, 7, 16, 18, 19),  # Grande calçadão sul de tábuas
        RectLayer(TILE_DEJIMA_WET_PLANK, 14, 16, 18, 19), # Borda sul molhada
    ),
    pits=(
        # Canais abertos e buracos entrecortando o deck de madeira suspensa:
        # 1. Canal marítimo norte ao redor da doca
        PitZone(7.0, 0.0, 17.0, 3.6, "VOID", railed=False, water=((20, 36, 52), (52, 92, 134))),
        # 2. Mar aberto a leste da doca
        PitZone(17.0, 3.6, float(MAP_COLS), float(MAP_ROWS), "VOID", railed=False, water=((20, 36, 52), (52, 92, 134))),
        # 3. Foz marítima ao sul do calçadão inferior
        PitZone(7.0, 19.92, 17.0, float(MAP_ROWS), "L", railed=False, water=((20, 36, 52), (52, 92, 134))),
        # 4. Buraco 1: vão de água central entre o cais superior e o cais inferior
        PitZone(10.0, 12.0, 14.0, 14.08, "L", railed=False, water=((20, 36, 52), (52, 92, 134))),
        # 5. Buraco 2: fosso marítimo de descarga em pleno deck do espaço inferior
        PitZone(10.0, 16.0, 14.0, 18.08, "L", railed=False, water=((20, 36, 52), (52, 92, 134))),
    ),
    props=(
        # Interior do Laboratório Alquímico (x <= 7.0)
        PropSpec("alchemy_bench", 4.2, 5.8),
        PropSpec("reagent_barrel", 3.8, 14.5, {"style": "acid"}),
        PropSpec("reagent_barrel", 4.8, 15.2, {"style": "volatile"}),
        PropSpec("crate", 3.2, 9.5),
        PropSpec("crate", 3.2, 11.5),
        PropSpec("paper_lantern", 5.5, 3.8, {"color": (235, 185, 75)}),
        PropSpec("paper_lantern", 5.5, 17.2, {"color": (235, 185, 75)}),
        # Paredes Semitransparentes com Vidraças no limiar x = 7.5
        PropSpec("glass_wall", 7.5, 2.2),
        PropSpec("glass_wall", 7.5, 3.4),
        PropSpec("glass_wall", 7.5, 4.6),
        PropSpec("glass_wall", 7.5, 5.8),
        PropSpec("glass_wall", 7.5, 7.0),
        # Portal / Vãos de passagem central do Armazém para a doca
        PropSpec("doorway_arch", 7.5, 8.5),
        PropSpec("doorway_arch", 7.5, 12.5),
        # Paredes Semitransparentes ao sul da porta
        PropSpec("glass_wall", 7.5, 14.0),
        PropSpec("glass_wall", 7.5, 15.2),
        PropSpec("glass_wall", 7.5, 16.4),
        PropSpec("glass_wall", 7.5, 17.6),
        PropSpec("glass_wall", 7.5, 18.8),
        # Estacas de sustentação em torno dos buracos e na orla da doca
        PropSpec("wharf_piling", 9.8, 12.0),
        PropSpec("wharf_piling", 14.2, 12.0),
        PropSpec("wharf_piling", 9.8, 14.1),
        PropSpec("wharf_piling", 14.2, 14.1),
        PropSpec("wharf_piling", 9.8, 16.0),
        PropSpec("wharf_piling", 14.2, 16.0),
        PropSpec("wharf_piling", 9.8, 18.1),
        PropSpec("wharf_piling", 14.2, 18.1),
        PropSpec("wharf_piling", 16.8, 5.5),
        PropSpec("wharf_piling", 16.8, 9.5),
        PropSpec("wharf_piling", 16.8, 14.5),
        PropSpec("wharf_piling", 16.8, 18.5),
        # Cabeços de amarração na beirada da doca suspensa
        PropSpec("wharf_bollard", 15.8, 6.5),
        PropSpec("wharf_bollard", 15.8, 11.0),
        PropSpec("wharf_bollard", 15.8, 15.5),
        PropSpec("wharf_bollard", 15.8, 19.0),
        # Barris químicos e caixotes de carga distribuídos nos decks superior e inferior
        PropSpec("reagent_barrel", 15.0, 7.5, {"style": "acid"}),
        PropSpec("reagent_barrel", 15.0, 18.2, {"style": "volatile"}),
        PropSpec("crate", 11.5, 5.5),
        PropSpec("crate", 8.2, 15.5),
        PropSpec("crate", 15.2, 14.8),
    ),
    hazards=(HazardSpec("dejima_hazard", {}),),
    playable_bounds=(1.5, 2.5, 16.5, 19.5),
    spawns=SpawnRule(x_range=(4.5, 12.5), margin=3.0, min_distance=5.5, fallback=((4.5, 10.5), (11.5, 7.5))),
    stage=StageSpec(10.5, 7.5),
    drift_count=55,
    drift_petals=0.0,
    lighting=LightingEnvironment(
        ambient_color=(165, 192, 225), ambient_strength=0.58, vignette=0.42,
        lights=_DEJIMA_LIGHTS,
        atmosphere=(
            AtmosphereEffect("mist", density=0.65),
            AtmosphereEffect("rain", density=0.85),
        ),
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
    ARENA_SHAOLIN: SHAOLIN_SPEC,
    ARENA_HIGANBANA: HIGANBANA_SPEC,
    ARENA_GOJO_BRIDGE: GOJO_BRIDGE_SPEC,
    ARENA_YOSHIWARA: YOSHIWARA_SPEC,
    ARENA_RICE_PADDIES: RICE_PADDIES_SPEC,
    ARENA_RAIN_MILL: RAIN_MILL_SPEC,
    ARENA_GOTHIC_CEMETERY: GOTHIC_CEMETERY_SPEC,
    ARENA_HEIAN_SHRINE: HEIAN_SHRINE_SPEC,
    ARENA_SACRED_PINES: SACRED_PINES_SPEC,
    ARENA_EZO_TUNDRA: EZO_TUNDRA_SPEC,
    ARENA_DOHYO: SACRED_DOHYO_SPEC,
    ARENA_DEJIMA: DEJIMA_WAREHOUSE_SPEC,
}


# ---------------------------------------------------------------------------
# Campo dos Mortos de Fome (chefe Oni Gashadokuro) — Etapa 5.3, fora das telas de seleção
# ---------------------------------------------------------------------------
TILE_GY_SOIL = 58
TILE_GY_PATH = 59
TILE_GY_MOUND = 60
TILE_GY_FISSURE = 77

_GY_GRAVES = ((5.2, 5.2), (15.8, 5.2), (3.4, 10.5), (17.6, 10.5), (5.2, 15.8), (15.8, 15.8))
_GY_LANTERNS = ((6.8, 3.6), (14.2, 3.6), (6.8, 17.4), (14.2, 17.4))
_GY_FISSURES = (
    (6.2, 6.5, {"length": 2.2, "angle": 0.55, "seed": 1}),
    (14.8, 6.5, {"length": 2.2, "angle": -0.55, "seed": 2}),
    (4.8, 11.0, {"length": 2.0, "angle": 0.15, "seed": 3}),
    (16.2, 11.0, {"length": 2.0, "angle": -0.15, "seed": 4}),
    (6.5, 15.2, {"length": 2.3, "angle": -0.45, "seed": 5}),
    (14.5, 15.2, {"length": 2.3, "angle": 0.45, "seed": 6}),
)
_GY_BONE_MOUNDS = ((3.2, 4.2, 1), (17.8, 4.2, 2), (3.2, 16.8, 3), (17.8, 16.8, 4))
_GY_BLADES = ((8.5, 3.2, 11), (12.5, 3.2, 22), (3.8, 7.5, 33), (17.2, 7.5, 44), (8.5, 18.2, 55), (12.5, 18.2, 66))
_GY_TREES = ((1.8, 2.2), (19.2, 2.2), (1.8, 18.8), (19.2, 18.8))
_GY_NOBORI = (
    (4.5, 2.6, {"text": "怨", "cloth": (44, 16, 28), "ink": (220, 60, 80)}),
    (16.5, 2.6, {"text": "骸", "cloth": (36, 18, 42), "ink": (195, 110, 255)}),
    (4.5, 18.4, {"text": "飢", "cloth": (36, 18, 42), "ink": (195, 110, 255)}),
    (16.5, 18.4, {"text": "鬼", "cloth": (44, 16, 28), "ink": (220, 60, 80)}),
)

GASHADOKURO_SPEC = ArenaSpec(
    id=ARENA_GASHADOKURO,
    name="Campo dos Mortos de Fome",
    cols=MAP_COLS,
    rows=MAP_ROWS,
    bg_color=(16, 6, 14),
    music="bgm_gashadokuro",
    wind=WindSpec(1, 0.45, 0.30, 0.65),
    tile_styles={
        TILE_GY_SOIL: TileStyle("flat", ((42, 28, 32), (36, 24, 28)), pattern="parity", edge=(24, 14, 18), surface="earth"),
        TILE_GY_PATH: TileStyle("flat", ((68, 48, 52), (60, 42, 46)), pattern="parity", edge=(38, 24, 28), surface="earth"),
        TILE_GY_MOUND: TileStyle("flat", ((92, 64, 66), (82, 56, 58)), pattern="parity", edge=(52, 34, 38), surface="earth"),
        TILE_GY_FISSURE: TileStyle("flat", ((64, 22, 82), (82, 28, 104)), pattern="parity", edge=(175, 55, 225), surface="stone"),
    },
    layers=(
        FillLayer(TILE_GY_SOIL),
        EllipseLayer(TILE_GY_PATH, cx=10.5, cy=10.5, radius=8.8),
        # Veios espirituais da fenda abissal
        RectLayer(TILE_GY_FISSURE, 6, 6, 6, 15),
        RectLayer(TILE_GY_FISSURE, 14, 14, 6, 15),
        EllipseLayer(TILE_GY_MOUND, cx=10.5, cy=10.5, radius=3.4),
        EllipseLayer(TILE_GY_FISSURE, cx=10.5, cy=10.5, radius=1.4),
    ),
    props=(
        tuple(PropSpec("jizo", x, y) for x, y in _GY_GRAVES)
        + tuple(PropSpec("spectral_toro", x, y) for x, y in _GY_LANTERNS)
        + tuple(PropSpec("soul_fissure", x, y, params) for x, y, params in _GY_FISSURES)
        + tuple(PropSpec("bone_mound", x, y, {"seed": s}) for x, y, s in _GY_BONE_MOUNDS)
        + tuple(PropSpec("blade_cluster", x, y, {"seed": s}) for x, y, s in _GY_BLADES)
        + tuple(PropSpec("dead_tree", x, y) for x, y in _GY_TREES)
        + tuple(PropSpec("nobori", x, y, params) for x, y, params in _GY_NOBORI)
    ),
    hazards=(HazardSpec("gashadokuro_hazard", {}),),
    playable_bounds=(2.0, 2.0, 19.0, 19.0),
    spawns=SpawnRule(x_range=(4.0, 17.0), margin=4.0, min_distance=7.0, fallback=((10.5, 16.5), (10.5, 7.5))),
    stage=StageSpec(10.5, 10.5),
    drift_count=46,
    drift_petals=0.85,
    lighting=LightingEnvironment(
        ambient_color=(125, 45, 75), ambient_strength=0.42, vignette=0.52,
        lights=(
            tuple(LightSource(x, y, 0.9, (220, 55, 185), 3.6, flicker=0.25) for x, y in _GY_LANTERNS)
            + tuple(LightSource(x, y, 0.3, (165, 45, 235), 2.6, flicker=0.20) for x, y, _ in _GY_FISSURES)
            + (LightSource(10.5, 10.5, 0.5, (235, 45, 85), 3.8, flicker=0.18),)
        ),
        atmosphere=(
            AtmosphereEffect("mist", density=0.75),
            AtmosphereEffect("embers", density=0.65),
        ),
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
