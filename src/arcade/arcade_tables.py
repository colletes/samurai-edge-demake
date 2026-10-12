"""Gerado por tools/generate_arcade_tables.py a partir de tournament_results.json. Não editar à mão."""

ARCADE_TIER_ORDER = ('kabuki', 'ren', 'chiyo', 'saitou', 'gray', 'kenshin', 'musashi', 'pirate', 'purple', 'ninja', 'musketeer', 'archer', 'american', 'rifleman',)

ARCADE_MATCHUP_TABLE = {
    'american': {'archer': 41.67, 'chiyo': 70.83, 'gray': 62.5, 'kabuki': 83.33, 'kenshin': 66.67, 'musashi': 75.0, 'musketeer': 66.67, 'ninja': 70.83, 'pirate': 70.83, 'purple': 70.83, 'ren': 58.33, 'rifleman': 37.5, 'saitou': 66.67},
    'archer': {'american': 54.17, 'chiyo': 70.83, 'gray': 58.33, 'kabuki': 91.67, 'kenshin': 50.0, 'musashi': 66.67, 'musketeer': 70.83, 'ninja': 70.83, 'pirate': 58.33, 'purple': 54.17, 'ren': 83.33, 'rifleman': 33.33, 'saitou': 75.0},
    'chiyo': {'american': 25.0, 'archer': 25.0, 'gray': 54.17, 'kabuki': 66.67, 'kenshin': 37.5, 'musashi': 45.83, 'musketeer': 37.5, 'ninja': 33.33, 'pirate': 41.67, 'purple': 12.5, 'ren': 41.67, 'rifleman': 12.5, 'saitou': 37.5},
    'gray': {'american': 37.5, 'archer': 41.67, 'chiyo': 37.5, 'kabuki': 75.0, 'kenshin': 25.0, 'musashi': 25.0, 'musketeer': 20.83, 'ninja': 45.83, 'pirate': 62.5, 'purple': 37.5, 'ren': 62.5, 'rifleman': 8.33, 'saitou': 54.17},
    'kabuki': {'american': 16.67, 'archer': 8.33, 'chiyo': 25.0, 'gray': 20.83, 'kenshin': 25.0, 'musashi': 33.33, 'musketeer': 25.0, 'ninja': 29.17, 'pirate': 29.17, 'purple': 16.67, 'ren': 29.17, 'rifleman': 8.33, 'saitou': 16.67},
    'kenshin': {'american': 33.33, 'archer': 33.33, 'chiyo': 45.83, 'gray': 66.67, 'kabuki': 62.5, 'musashi': 8.33, 'musketeer': 20.83, 'ninja': 33.33, 'pirate': 54.17, 'purple': 29.17, 'ren': 41.67, 'rifleman': 54.17, 'saitou': 58.33},
    'musashi': {'american': 20.83, 'archer': 29.17, 'chiyo': 54.17, 'gray': 62.5, 'kabuki': 58.33, 'kenshin': 83.33, 'musketeer': 41.67, 'ninja': 12.5, 'pirate': 33.33, 'purple': 12.5, 'ren': 50.0, 'rifleman': 37.5, 'saitou': 83.33},
    'musketeer': {'american': 33.33, 'archer': 25.0, 'chiyo': 45.83, 'gray': 75.0, 'kabuki': 75.0, 'kenshin': 79.17, 'musashi': 54.17, 'ninja': 41.67, 'pirate': 70.83, 'purple': 58.33, 'ren': 66.67, 'rifleman': 33.33, 'saitou': 66.67},
    'ninja': {'american': 29.17, 'archer': 25.0, 'chiyo': 66.67, 'gray': 54.17, 'kabuki': 70.83, 'kenshin': 58.33, 'musashi': 83.33, 'musketeer': 50.0, 'pirate': 45.83, 'purple': 41.67, 'ren': 83.33, 'rifleman': 33.33, 'saitou': 54.17},
    'pirate': {'american': 29.17, 'archer': 29.17, 'chiyo': 54.17, 'gray': 37.5, 'kabuki': 62.5, 'kenshin': 41.67, 'musashi': 58.33, 'musketeer': 25.0, 'ninja': 54.17, 'purple': 87.5, 'ren': 54.17, 'rifleman': 12.5, 'saitou': 62.5},
    'purple': {'american': 29.17, 'archer': 41.67, 'chiyo': 75.0, 'gray': 58.33, 'kabuki': 62.5, 'kenshin': 66.67, 'musashi': 83.33, 'musketeer': 37.5, 'ninja': 54.17, 'pirate': 0.0, 'ren': 62.5, 'rifleman': 45.83, 'saitou': 66.67},
    'ren': {'american': 33.33, 'archer': 12.5, 'chiyo': 58.33, 'gray': 29.17, 'kabuki': 54.17, 'kenshin': 50.0, 'musashi': 50.0, 'musketeer': 29.17, 'ninja': 12.5, 'pirate': 45.83, 'purple': 29.17, 'rifleman': 16.67, 'saitou': 33.33},
    'rifleman': {'american': 58.33, 'archer': 66.67, 'chiyo': 83.33, 'gray': 91.67, 'kabuki': 83.33, 'kenshin': 33.33, 'musashi': 54.17, 'musketeer': 62.5, 'ninja': 66.67, 'pirate': 83.33, 'purple': 50.0, 'ren': 79.17, 'saitou': 66.67},
    'saitou': {'american': 33.33, 'archer': 16.67, 'chiyo': 54.17, 'gray': 41.67, 'kabuki': 70.83, 'kenshin': 29.17, 'musashi': 4.17, 'musketeer': 29.17, 'ninja': 41.67, 'pirate': 33.33, 'purple': 33.33, 'ren': 66.67, 'rifleman': 29.17},
}
