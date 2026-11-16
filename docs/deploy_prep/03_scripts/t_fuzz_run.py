import os, sys, random, json, collections, traceback
sys.path.insert(0, "/Users/thiagocarvalho/Public/SamuraiEdge")
from src.arcade.arcade_mode import ArcadeRun
from src.roster import PLAYABLE_FIGHTERS
base = ArcadeRun(player_char="kenshin", difficulty_start=1, seed=3).to_dict()
rnd = random.Random(1)
vals = [None, "x", "", -1, 0, 1, 2, 7, 999, 10**30, -10**30, 1.5, float("nan"), float("inf"), [], [1, 2], {}, {"a": 1}, True, False, "kenshin", "tier", "random", [None], [{"score": "x"}], [{"score": 100}], "gashadokuro"]
exc = collections.Counter(); ex_example = {}
ok = 0
for i in range(20000):
    d = json.loads(json.dumps(base, default=str))
    for _ in range(rnd.choice([1, 1, 2, 3])):
        k = rnd.choice(list(d.keys()) + ["junk"])
        if rnd.random() < 0.1 and k in d: del d[k]
        else: d[k] = rnd.choice(vals)
    try:
        r = ArcadeRun.from_dict(d)
        # usar o objeto como o main usaria
        r.current_fight(); r.current_opponent(); r.difficulty_name; r.ladder; r.is_finished
        ok += 1
    except (ValueError, KeyError, TypeError) as e:
        exc["tratado:"+type(e).__name__] += 1
    except BaseException as e:
        key = type(e).__name__
        exc["NAO-TRATADO:"+key] += 1
        ex_example.setdefault(key, (d, traceback.format_exc().strip().splitlines()[-3:]))
print("ok", ok, dict(exc))
for k, (d, tb) in ex_example.items():
    print("EXEMPLO", k, {kk: d[kk] for kk in d if d[kk] != base.get(kk)}, tb)
