"""Gerado por tools/generate_arcade_tables.py a partir de tournament_results.json. Não editar à mão."""

ARCADE_TIER_ORDER = ('kabuki', 'ren', 'chiyo', 'kenshin', 'saitou', 'purple', 'ninja', 'gray', 'pirate', 'musketeer', 'musashi', 'archer', 'american', 'rifleman',)

ARCADE_MATCHUP_TABLE = {
    'american': {'archer': 60.0, 'chiyo': 80.0, 'gray': 60.0, 'kabuki': 90.0, 'kenshin': 80.0, 'musashi': 60.0, 'musketeer': 50.0, 'ninja': 50.0, 'pirate': 40.0, 'purple': 70.0, 'ren': 80.0, 'rifleman': 10.0, 'saitou': 90.0},
    'archer': {'american': 30.0, 'chiyo': 90.0, 'gray': 60.0, 'kabuki': 80.0, 'kenshin': 70.0, 'musashi': 50.0, 'musketeer': 70.0, 'ninja': 40.0, 'pirate': 90.0, 'purple': 60.0, 'ren': 60.0, 'rifleman': 40.0, 'saitou': 20.0},
    'chiyo': {'american': 0.0, 'archer': 10.0, 'gray': 40.0, 'kabuki': 50.0, 'kenshin': 30.0, 'musashi': 30.0, 'musketeer': 60.0, 'ninja': 30.0, 'pirate': 50.0, 'purple': 40.0, 'ren': 60.0, 'rifleman': 10.0, 'saitou': 40.0},
    'gray': {'american': 30.0, 'archer': 40.0, 'chiyo': 60.0, 'kabuki': 60.0, 'kenshin': 40.0, 'musashi': 30.0, 'musketeer': 30.0, 'ninja': 70.0, 'pirate': 80.0, 'purple': 80.0, 'ren': 70.0, 'rifleman': 20.0, 'saitou': 40.0},
    'kabuki': {'american': 0.0, 'archer': 10.0, 'chiyo': 40.0, 'gray': 30.0, 'kenshin': 20.0, 'musashi': 20.0, 'musketeer': 0.0, 'ninja': 40.0, 'pirate': 30.0, 'purple': 30.0, 'ren': 10.0, 'rifleman': 20.0, 'saitou': 40.0},
    'kenshin': {'american': 20.0, 'archer': 20.0, 'chiyo': 70.0, 'gray': 60.0, 'kabuki': 70.0, 'musashi': 30.0, 'musketeer': 30.0, 'ninja': 50.0, 'pirate': 20.0, 'purple': 30.0, 'ren': 70.0, 'rifleman': 30.0, 'saitou': 30.0},
    'musashi': {'american': 40.0, 'archer': 40.0, 'chiyo': 70.0, 'gray': 70.0, 'kabuki': 70.0, 'kenshin': 70.0, 'musketeer': 60.0, 'ninja': 40.0, 'pirate': 50.0, 'purple': 70.0, 'ren': 50.0, 'rifleman': 30.0, 'saitou': 60.0},
    'musketeer': {'american': 40.0, 'archer': 30.0, 'chiyo': 40.0, 'gray': 70.0, 'kabuki': 80.0, 'kenshin': 60.0, 'musashi': 40.0, 'ninja': 70.0, 'pirate': 60.0, 'purple': 50.0, 'ren': 60.0, 'rifleman': 40.0, 'saitou': 50.0},
    'ninja': {'american': 50.0, 'archer': 60.0, 'chiyo': 60.0, 'gray': 30.0, 'kabuki': 50.0, 'kenshin': 30.0, 'musashi': 60.0, 'musketeer': 20.0, 'pirate': 40.0, 'purple': 30.0, 'ren': 70.0, 'rifleman': 40.0, 'saitou': 50.0},
    'pirate': {'american': 50.0, 'archer': 10.0, 'chiyo': 50.0, 'gray': 20.0, 'kabuki': 70.0, 'kenshin': 50.0, 'musashi': 50.0, 'musketeer': 30.0, 'ninja': 40.0, 'purple': 90.0, 'ren': 90.0, 'rifleman': 20.0, 'saitou': 80.0},
    'purple': {'american': 30.0, 'archer': 30.0, 'chiyo': 60.0, 'gray': 20.0, 'kabuki': 70.0, 'kenshin': 60.0, 'musashi': 20.0, 'musketeer': 50.0, 'ninja': 70.0, 'pirate': 10.0, 'ren': 90.0, 'rifleman': 10.0, 'saitou': 60.0},
    'ren': {'american': 20.0, 'archer': 30.0, 'chiyo': 40.0, 'gray': 20.0, 'kabuki': 70.0, 'kenshin': 30.0, 'musashi': 30.0, 'musketeer': 30.0, 'ninja': 30.0, 'pirate': 10.0, 'purple': 10.0, 'rifleman': 10.0, 'saitou': 30.0},
    'rifleman': {'american': 60.0, 'archer': 50.0, 'chiyo': 90.0, 'gray': 80.0, 'kabuki': 80.0, 'kenshin': 60.0, 'musashi': 50.0, 'musketeer': 50.0, 'ninja': 50.0, 'pirate': 80.0, 'purple': 90.0, 'ren': 80.0, 'saitou': 80.0},
    'saitou': {'american': 10.0, 'archer': 70.0, 'chiyo': 50.0, 'gray': 60.0, 'kabuki': 60.0, 'kenshin': 50.0, 'musashi': 20.0, 'musketeer': 50.0, 'ninja': 50.0, 'pirate': 20.0, 'purple': 40.0, 'ren': 70.0, 'rifleman': 20.0},
}
