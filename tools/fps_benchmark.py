"""
Benchmark de FPS do loop REAL do jogo (main.run_game) em uma arena, com IA vs IA ("watch").

Roda 1 arena por processo (run_game termina com os._exit). Mede o tempo de parede de cada iteração do loop
principal (update + draw + escala para a janela), sem limitar a 60 FPS, e grava um JSON com os tempos por quadro.
O relógio do jogo é simulado: dt = max(tempo real do quadro, 1/60), igual ao que clock.tick(60) devolveria.

Uso:
  python tools/fps_benchmark.py --arena bamboo [--p1 kenshin --p2 musashi] [--frames 1800]
                                [--quality high|low|auto] [--window 1280x800] [--out /tmp/x.json] [--profile]
O resumo (p50/p95/p99/máx, % de quadros > 16,6 ms) fica em "summary" no JSON. Para o Steam Deck: rode no próprio
aparelho (SteamOS/Linux, sem SDL_VIDEODRIVER=dummy se quiser incluir o custo real de apresentação: --real-display).
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arena", required=True)
    ap.add_argument("--p1", default="kenshin")
    ap.add_argument("--p2", default="musashi")
    ap.add_argument("--frames", type=int, default=1800)
    ap.add_argument("--skip", type=int, default=30, help="quadros iniciais descartados (menus/aquecimento)")
    ap.add_argument("--quality", default="high", choices=["high", "low", "auto"])
    ap.add_argument("--window", default="1280x720")
    ap.add_argument("--out", required=True)
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--shot", type=int, default=0, help="salva um PNG da janela neste quadro (conferência visual)")
    ap.add_argument("--hotfix-mist", action="store_true", help="contorna o crash de hazards.py na mist_temple (só para medir)")
    ap.add_argument("--real-display", action="store_true", help="não força SDL dummy (usa a janela real)")
    args = ap.parse_args()

    if not args.real_display:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"

    import pygame
    import main as game
    from src.effects import quality
    from src.ui.title_screen import SumieTitleScreen
    from src.ui.versus_config import VersusConfigScreen
    from src.ui.character_select import CharacterSelectScreen
    from src.ui.arena_select import ArenaSelectScreen

    # Contorno SÓ para medir FPS na mist_temple: hazards.py:462 sombreia SmokeParticle dentro de on_phase (UnboundLocalError)
    if args.hotfix_mist:
        import inspect
        import textwrap
        import src.world.hazards as hz
        for _n, _cls in vars(hz).items():
            _oc = vars(_cls).get("on_phase") if inspect.isclass(_cls) else None
            if _oc is not None and "BloodParticle, SmokeParticle, SparkParticle" in inspect.getsource(_oc):
                _src = textwrap.dedent(inspect.getsource(_oc)).replace(
                    "from src.effects.particles import BloodParticle, SmokeParticle, SparkParticle",
                    "from src.effects.particles import BloodParticle, SparkParticle")
                _ns = {}
                exec(_src, vars(hz), _ns)
                _cls.on_phase = _ns["on_phase"]

    # Atravessa os menus: cada tela devolve a ação de "confirmar" na primeira vez que recebe um evento
    SumieTitleScreen.handle_event = lambda self, ev: "VERSUS"
    VersusConfigScreen.handle_event = lambda self, ev, ctrl=None: "PROCEED"
    CharacterSelectScreen.handle_event = lambda self, ev: True

    def _selected(self):
        self.rounds_to_win = 99  # a partida não termina durante a medição
        return args.p1, args.p2, "watch"
    CharacterSelectScreen.get_selected_characters = _selected
    ArenaSelectScreen.handle_event = lambda self, ev: args.arena

    # Eventos sintéticos: uma tecla por quadro até a partida começar (também pula o vídeo de abertura)
    _orig_get = pygame.event.get

    def fake_get(*a, **k):
        _orig_get(*a, **k)
        return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r", scancode=40)]
    pygame.event.get = fake_get

    w, h = (int(x) for x in args.window.split("x"))
    if not args.real_display:
        _orig_set_mode = pygame.display.set_mode
        pygame.display.set_mode = lambda size=(0, 0), flags=0, *a, **k: _orig_set_mode((w, h), 0)

    frames = []
    cpu_frames = []  # tempo de CPU da thread principal por quadro: robusto a carga externa (host compartilhado)
    state = {"last": None, "last_cpu": 0.0, "n": 0}
    prof = None
    if args.profile:
        import cProfile
        prof = cProfile.Profile()

    class BenchClock:
        def tick(self, fps=0):
            now = time.perf_counter()
            cpu_now = time.thread_time()
            if state["last"] is None:
                state["last"] = now
                state["last_cpu"] = cpu_now
                if prof:
                    prof.enable()
                return 16
            dt = now - state["last"]
            state["last"] = now
            cpu_dt = cpu_now - state["last_cpu"]
            state["last_cpu"] = cpu_now
            state["n"] += 1
            if args.shot and state["n"] == args.shot:
                pygame.image.save(pygame.display.get_surface(), args.out.replace(".json", ".png"))
            if state["n"] > args.skip:
                frames.append(dt)
                cpu_frames.append(cpu_dt)
            if state["n"] >= args.frames + args.skip:
                if prof:
                    prof.disable()
                finish()
            # dt fixo (carga de jogo idêntica entre execuções); em 'auto' usa o tempo real para o governador reagir
            return 16.667 if args.quality != "auto" else max(16.667, cpu_dt * 1000.0)

        def get_fps(self):
            return 60.0

        def get_time(self):
            return 16

    pygame.time.Clock = BenchClock

    def finish():
        fs = sorted(frames)
        n = len(fs)
        pct = lambda p: fs[min(n - 1, int(n * p))] * 1000.0
        # pior janela de 1 s consecutiva (60 quadros): média do tempo de quadro
        worst_1s = max((sum(frames[i:i + 60]) / 60 for i in range(0, max(1, n - 60), 10)), default=0) * 1000.0
        cs = sorted(cpu_frames)
        cpct = lambda p: cs[min(n - 1, int(n * p))] * 1000.0
        summary = {
            "cpu_mean_ms": sum(cs) / n * 1000.0, "cpu_p50_ms": cpct(0.50), "cpu_p95_ms": cpct(0.95),
            "cpu_p99_ms": cpct(0.99), "cpu_max_ms": cs[-1] * 1000.0,
            "cpu_pct_over_16_7": sum(1 for f in cs if f > 1 / 60) / n * 100.0,
            "n": n, "mean_ms": sum(fs) / n * 1000.0, "p50_ms": pct(0.50), "p95_ms": pct(0.95), "p99_ms": pct(0.99),
            "max_ms": fs[-1] * 1000.0, "pct_over_16_7": sum(1 for f in fs if f > 1 / 60) / n * 100.0,
            "worst_1s_mean_ms": worst_1s, "quality_end": quality.get_effects_quality(),
            "governor_stepped_down": quality.is_governor_stepped_down(),
        }
        out = {"args": vars(args), "summary": summary, "frames_ms": [round(f * 1000.0, 3) for f in frames],
               "cpu_frames_ms": [round(f * 1000.0, 3) for f in cpu_frames],
               "loadavg": os.getloadavg()}
        with open(args.out, "w") as f:
            json.dump(out, f)
        if prof:
            import pstats
            with open(args.out.replace(".json", ".prof.txt"), "w") as f:
                pstats.Stats(prof, stream=f).sort_stats("cumulative").print_stats(45)
        print(json.dumps(summary))
        sys.stdout.flush()
        os._exit(0)

    # Qualidade/governador: "high"/"low" fixam o nível (governador desligado); "auto" = comportamento de produção
    _orig_load = quality.load_effects_quality

    def load_q(path):
        _orig_load(path)
        if args.quality != "auto":
            quality.set_effects_quality(args.quality)
            quality.set_auto_adjust(False)
    quality.load_effects_quality = load_q

    game.run_game()


if __name__ == "__main__":
    main()
