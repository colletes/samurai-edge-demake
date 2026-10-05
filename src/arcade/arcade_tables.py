"""Gerado por tools/generate_arcade_tables.py a partir de tournament_results.json. Não editar à mão."""

ARCADE_TIER_ORDER = ('kabuki', 'pirate', 'saitou', 'kenshin', 'ninja', 'gray', 'musashi', 'purple', 'musketeer', 'american', 'archer', 'rifleman',)

ARCADE_MATCHUP_TABLE = {
    'american': {'archer': 37.5, 'gray': 37.5, 'kabuki': 79.17, 'kenshin': 50.0, 'musashi': 75.0, 'musketeer': 50.0, 'ninja': 58.33, 'pirate': 87.5, 'purple': 70.83, 'rifleman': 29.17, 'saitou': 62.5},
    'archer': {'american': 58.33, 'gray': 54.17, 'kabuki': 87.5, 'kenshin': 70.83, 'musashi': 70.83, 'musketeer': 58.33, 'ninja': 45.83, 'pirate': 70.83, 'purple': 33.33, 'rifleman': 41.67, 'saitou': 58.33},
    'gray': {'american': 58.33, 'archer': 37.5, 'kabuki': 95.83, 'kenshin': 45.83, 'musashi': 4.17, 'musketeer': 20.83, 'ninja': 66.67, 'pirate': 45.83, 'purple': 41.67, 'rifleman': 29.17, 'saitou': 70.83},
    'kabuki': {'american': 20.83, 'archer': 12.5, 'gray': 0.0, 'kenshin': 20.83, 'musashi': 12.5, 'musketeer': 12.5, 'ninja': 20.83, 'pirate': 29.17, 'purple': 8.33, 'rifleman': 4.17, 'saitou': 25.0},
    'kenshin': {'american': 50.0, 'archer': 12.5, 'gray': 54.17, 'kabuki': 62.5, 'musashi': 16.67, 'musketeer': 41.67, 'ninja': 54.17, 'pirate': 66.67, 'purple': 33.33, 'rifleman': 16.67, 'saitou': 45.83},
    'musashi': {'american': 16.67, 'archer': 25.0, 'gray': 91.67, 'kabuki': 75.0, 'kenshin': 83.33, 'musketeer': 75.0, 'ninja': 16.67, 'pirate': 79.17, 'purple': 25.0, 'rifleman': 33.33, 'saitou': 50.0},
    'musketeer': {'american': 50.0, 'archer': 37.5, 'gray': 70.83, 'kabuki': 87.5, 'kenshin': 58.33, 'musashi': 16.67, 'ninja': 58.33, 'pirate': 62.5, 'purple': 45.83, 'rifleman': 45.83, 'saitou': 50.0},
    'ninja': {'american': 20.83, 'archer': 50.0, 'gray': 33.33, 'kabuki': 66.67, 'kenshin': 33.33, 'musashi': 83.33, 'musketeer': 37.5, 'pirate': 54.17, 'purple': 37.5, 'rifleman': 25.0, 'saitou': 37.5},
    'pirate': {'american': 8.33, 'archer': 20.83, 'gray': 50.0, 'kabuki': 66.67, 'kenshin': 20.83, 'musashi': 20.83, 'musketeer': 29.17, 'ninja': 37.5, 'purple': 45.83, 'rifleman': 20.83, 'saitou': 33.33},
    'purple': {'american': 29.17, 'archer': 41.67, 'gray': 54.17, 'kabuki': 83.33, 'kenshin': 62.5, 'musashi': 62.5, 'musketeer': 50.0, 'ninja': 62.5, 'pirate': 54.17, 'rifleman': 12.5, 'saitou': 70.83},
    'rifleman': {'american': 70.83, 'archer': 58.33, 'gray': 70.83, 'kabuki': 91.67, 'kenshin': 83.33, 'musashi': 54.17, 'musketeer': 45.83, 'ninja': 75.0, 'pirate': 75.0, 'purple': 79.17, 'saitou': 83.33},
    'saitou': {'american': 33.33, 'archer': 37.5, 'gray': 29.17, 'kabuki': 70.83, 'kenshin': 33.33, 'musashi': 25.0, 'musketeer': 41.67, 'ninja': 58.33, 'pirate': 62.5, 'purple': 29.17, 'rifleman': 16.67},
}
