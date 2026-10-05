"""
Arena Floresta de Bambu: lago zen, ponte arqueada Taiko-bashi, caminho de terra com lajes Tobi-ishi,
lavatório Tsukubai, portal Torii, lanternas Ishi-doro, árvores de sakura e floresta de bambus cortáveis.

O mapa é descrito por `arenas.BAMBOO_SPEC` e construído pelo motor de arenas parametrizadas;
`GameMap` permanece como construtor de compatibilidade.
"""
from src.world.arena_generator import ArenaMap
from src.world.bamboo import Bamboo  # noqa: F401  (re-exportado por compatibilidade)
from src.world.obstacles import Rock, Well, AncientTree, Tsukubai, ToriiGate, StoneLantern  # noqa: F401

# Constantes de Tile de Terreno
TILE_GRASS = 0
TILE_EARTH = 1
TILE_WATER = 2
TILE_BRIDGE = 3


class GameMap(ArenaMap):
    def __init__(self):
        from src.world.arenas import BAMBOO_SPEC
        super().__init__(BAMBOO_SPEC)
