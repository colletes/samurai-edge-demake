import os, sys, json, subprocess, shutil, time
SB = "/tmp/se/play_boot"
PY = "/Users/thiagocarvalho/Public/SamuraiEdge/venv/bin/python"
env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", PYTHONUNBUFFERED="1", PYTHONPYCACHEPREFIX="/tmp/se/pyc")

good_run = None
def clear():
    for f in ("settings.json", "controls_config.json", "arcade_save.json"):
        p = os.path.join(SB, f)
        if os.path.lexists(p):
            os.remove(p)

def run_case(name, files, frames=120):
    if name.startswith("save:"):
        env["RESUME"] = "1"; frames = 400
    else:
        env.pop("RESUME", None)
    clear()
    for fn, content in files.items():
        mode = "wb" if isinstance(content, bytes) else "w"
        with open(os.path.join(SB, fn), mode) as f:
            f.write(content)
    t = time.time()
    r = subprocess.run([PY, "/tmp/se/e2e_boot.py", SB, str(frames)], env=env, capture_output=True, text=True, timeout=120)
    out = r.stdout + r.stderr
    ok = "BOOT_OK" in out and "CRASH" not in out
    tb = ""
    if not ok:
        lines = [l for l in out.splitlines() if l.strip()]
        tb = "\n      ".join(lines[-8:])
    print(f"{'OK  ' if ok else 'FAIL'} {name:55s} {time.time()-t:4.1f}s" + (("\n      " + tb) if tb else ""), flush=True)
    return ok

def dumps(o): return json.dumps(o)

cases = []
# --- controls_config.json
cc = "controls_config.json"
cases += [
    ("controls: ausente", {}),
    ("controls: vazio (0 bytes)", {cc: ""}),
    ("controls: '{' truncado", {cc: "{"}),
    ("controls: lixo binario", {cc: bytes(range(256)) * 4}),
    ("controls: []", {cc: "[]"}),
    ("controls: null", {cc: "null"}),
    ("controls: 'string'", {cc: '"abc"'}),
    ("controls: keyboard=lista", {cc: dumps({"keyboard": []})}),
    ("controls: keyboard P1_UP='abc'", {cc: dumps({"keyboard": {"P1_UP": "abc"}})}),
    ("controls: keyboard P1_UP=null", {cc: dumps({"keyboard": {"P1_UP": None}})}),
    ("controls: keyboard P1_UP=[1]", {cc: dumps({"keyboard": {"P1_UP": [1]}})}),
    ("controls: keyboard P1_UP=99999999999999999999", {cc: dumps({"keyboard": {"P1_UP": 99999999999999999999}})}),
    ("controls: keyboard P1_UP=-5", {cc: dumps({"keyboard": {"P1_UP": -5}})}),
    ("controls: keyboard P1_UP=1.5", {cc: dumps({"keyboard": {"P1_UP": 1.5}})}),
    ("controls: controllers=string", {cc: dumps({"controllers": "x"})}),
    ("controls: controllers.P1 lista", {cc: dumps({"controllers": {"P1": [1, 2]}})}),
    ("controls: controllers.P1.attack='x'", {cc: dumps({"controllers": {"P1": {"attack": "x"}}})}),
    ("controls: controllers.P1.attack=[null]", {cc: dumps({"controllers": {"P1": {"attack": [None]}}})}),
    ("controls: controllers.P1.attack=[-1,9999]", {cc: dumps({"controllers": {"P1": {"attack": [-1, 9999]}}})}),
    ("controls: touch_mode=123", {cc: dumps({"touch_mode": 123})}),
    ("controls: touch_mode='zzz'", {cc: dumps({"touch_mode": "zzz"})}),
    ("controls: audio master='loud'", {cc: dumps({"audio": {"master": "loud"}})}),
    ("controls: audio master=null", {cc: dumps({"audio": {"master": None}})}),
    ("controls: audio master=1e999", {cc: '{"audio": {"master": 1e999}}'}),
    ("controls: audio master=-3 sfx=NaN", {cc: '{"audio": {"master": -3, "sfx": NaN, "bgm": 99}}'}),
    ("controls: ai_difficulty=7", {cc: dumps({"ai_difficulty": 7})}),
    ("controls: touch_controls=lista", {cc: dumps({"touch_controls": []})}),
    ("controls: versao antiga (so keyboard antigo)", {cc: dumps({"version": "1.0.0", "keyboard": {"P1_UP": 119}})}),
]
# --- settings.json
st = "settings.json"
cases += [
    ("settings: vazio", {st: ""}),
    ("settings: '{'", {st: "{"}),
    ("settings: binario", {st: bytes(range(256)) * 4}),
    ("settings: []", {st: "[]"}),
    ("settings: null", {st: "null"}),
    ("settings: video=5", {st: dumps({"video": 5})}),
    ("settings: video=[]", {st: dumps({"video": []})}),
    ("settings: video.effects_quality=99", {st: dumps({"video": {"effects_quality": 99}})}),
    ("settings: video.effects_quality='ultra'", {st: dumps({"video": {"effects_quality": "ultra"}})}),
    ("settings: video.effects_quality=null", {st: dumps({"video": {"effects_quality": None}})}),
    ("settings: video.game_boost='x'", {st: dumps({"video": {"game_boost": "x", "auto_fps_governor": [1]}})}),
    ("settings: gameplay=5", {st: dumps({"gameplay": 5})}),
    ("settings: gameplay.language=5", {st: dumps({"gameplay": {"language": 5}})}),
    ("settings: gameplay.language='klingon'", {st: dumps({"gameplay": {"language": "klingon"}})}),
    ("settings: versus=lista", {st: dumps({"versus": []})}),
    ("settings: versus.rounds_to_win=99999", {st: dumps({"versus": {"rounds_to_win": 99999, "mode": 3, "ai_difficulty": []}})}),
    ("settings: versus.rounds_to_win=True", {st: dumps({"versus": {"rounds_to_win": True}})}),
    ("settings: versus.mode=[]", {st: dumps({"versus": {"mode": [], "ai_difficulty": {}}})}),
]
# --- arcade_save.json
sv = "arcade_save.json"
run_ok = {"player_char": "kenshin", "difficulty_start": 1, "seed": 5, "order": "tier", "difficulty_level": 1, "clean_streak": 0,
          "continues": 0, "score": 0, "points_lost_to_continues": 0, "index": 3, "elapsed": 10.0, "stats": [], "boss_phase": 0, "is_practice": False}
def sv_(**kw):
    d = {"version": 1, "high_scores": [], "best_clear_time": {}, "clears": {}, "current_run": None, "gallery_unlocked": False}
    d.update(kw); return dumps(d)
def run_(**kw):
    r = dict(run_ok); r.update(kw); return r
cases += [
    ("save: vazio", {sv: ""}),
    ("save: '{'", {sv: "{"}),
    ("save: binario", {sv: bytes(range(256)) * 4}),
    ("save: []", {sv: "[]"}),
    ("save: version=0 (antiga)", {sv: dumps({"version": 0, "high_scores": [{"score": 1}]})}),
    ("save: version=99 (futura)", {sv: dumps({"version": 99})}),
    ("save: version='1'", {sv: dumps({"version": "1"})}),
    ("save: run valida (resume)", {sv: sv_(current_run=run_ok)}),
    ("save: run player_char desconhecido", {sv: sv_(current_run=run_(player_char="naoexiste"))}),
    ("save: run index=999", {sv: sv_(current_run=run_(index=999))}),
    ("save: run index=-1", {sv: sv_(current_run=run_(index=-1))}),
    ("save: run index='x'", {sv: sv_(current_run=run_(index="x"))}),
    ("save: run difficulty_level=7", {sv: sv_(current_run=run_(difficulty_level=7))}),
    ("save: run difficulty_start=0", {sv: sv_(current_run=run_(difficulty_start=0))}),
    ("save: run stats=string", {sv: sv_(current_run=run_(stats="abc"))}),
    ("save: run stats=[1,2,3]", {sv: sv_(current_run=run_(stats=[1, 2, 3]))}),
    ("save: run seed=null", {sv: sv_(current_run=run_(seed=None))}),
    ("save: run order='zzz'", {sv: sv_(current_run=run_(order="zzz"))}),
    ("save: run vazio {}", {sv: sv_(current_run={})}),
    ("save: run boss_phase=99", {sv: sv_(current_run=run_(boss_phase=99))}),
    ("save: run elapsed=null", {sv: sv_(current_run=run_(elapsed=None))}),
    ("save: run score='x'", {sv: sv_(current_run=run_(score="x"))}),
    ("save: high_scores com lixo", {sv: sv_(high_scores=[1, "a", None, {"score": "x"}, {"score": 5}, {"score": 7, "char": 5, "time": "x"}])}),
    ("save: high_scores sem char/date, score float", {sv: sv_(high_scores=[{"score": 5.5}, {"score": 9}])}),
    ("save: clears={'kenshin':'x'}", {sv: sv_(clears={"kenshin": "x"}, gallery_unlocked=True)}),
    ("save: best_clear_time lixo", {sv: sv_(best_clear_time=[1, 2])}),
    ("save: current_run=lista", {sv: sv_(current_run=[1])}),
    ("save: arquivo e' diretorio (EISDIR)", "DIR"),
]

only = sys.argv[1] if len(sys.argv) > 1 else None
fails = 0
for name, files in cases:
    if only and only not in name:
        continue
    if files == "DIR":
        clear()
        os.makedirs(os.path.join(SB, "arcade_save.json"), exist_ok=True)
        t = time.time()
        r = subprocess.run([PY, "/tmp/se/e2e_boot.py", SB, "120"], env=env, capture_output=True, text=True, timeout=120)
        out = r.stdout + r.stderr
        ok = "BOOT_OK" in out and "CRASH" not in out
        print(f"{'OK  ' if ok else 'FAIL'} {name}" + ("" if ok else "\n      " + "\n      ".join([l for l in out.splitlines() if l.strip()][-8:])))
        os.rmdir(os.path.join(SB, "arcade_save.json"))
        fails += (not ok)
        continue
    fails += (not run_case(name, files))
clear()
print("TOTAL FAILS:", fails)
