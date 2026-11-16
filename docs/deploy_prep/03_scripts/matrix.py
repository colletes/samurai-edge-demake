"""Orquestra o lote de partidas (todos os arenas x pares), reiniciando o processo apos cada crash.
Uso: matrix.py OUTDIR ARENA|ALL FPJ MODE [START] [extra env KEY=VAL ...]
"""
import os, sys, re, subprocess, time, json
OUT = sys.argv[1]
ARENA = sys.argv[2]
FPJ = sys.argv[3]
MODE = sys.argv[4]
START = int(sys.argv[5]) if len(sys.argv) > 5 else 0
extra = dict(a.split("=", 1) for a in sys.argv[6:])
os.makedirs(OUT, exist_ok=True)
PY = "/Users/thiagocarvalho/Public/SamuraiEdge/venv/bin/python"
env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", PYTHONUNBUFFERED="1",
           PYTHONPYCACHEPREFIX="/tmp/se/pyc", SANDBOX=os.path.join(OUT, "sandbox"))
env.update(extra)
crashes = []
start = START
run_no = 0
t0 = time.time()
while True:
    run_no += 1
    log = os.path.join(OUT, f"run{run_no}.log")
    with open(log, "w") as lf:
        r = subprocess.run([PY, "/tmp/se/e2e_matches.py", ARENA, str(start), FPJ, MODE], env=env, stdout=lf, stderr=subprocess.STDOUT)
    txt = open(log, errors="replace").read()
    jobs = re.findall(r"\[job (\d+)\] (\S+) vs (\S+) @ (\S+) mode=(\S+)", txt)
    last = jobs[-1] if jobs else None
    done = "STATS" in txt and "=== CRASH" not in txt
    if "=== CRASH" in txt:
        tb = txt[txt.index("=== CRASH"):]
        tb = tb[:3500]
        crashes.append({"job": last, "tb": tb})
        print(f"[{time.time()-t0:.0f}s] CRASH run{run_no} at job {last}: {tb.strip().splitlines()[-1]}", flush=True)
        start = int(last[0]) + 1 if last else start + 1
        continue
    if done:
        print(f"[{time.time()-t0:.0f}s] run{run_no} concluiu (start={start}); ultimo job {last}", flush=True)
        break
    # saiu sem STATS nem CRASH (timeout/kill/segfault?)
    print(f"[{time.time()-t0:.0f}s] run{run_no} terminou anormalmente rc={r.returncode}; ultimo job {last}; cauda: {txt[-400:]!r}", flush=True)
    crashes.append({"job": last, "tb": f"abnormal rc={r.returncode}: {txt[-1500:]}"})
    start = int(last[0]) + 1 if last else start + 1
    if start > 100000:
        break
json.dump(crashes, open(os.path.join(OUT, "crashes.json"), "w"), indent=1)
print("TOTAL CRASHES:", len(crashes))
