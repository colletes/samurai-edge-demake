"""
Driver headless para o Samurai Edge: injeta eventos sinteticos e avanca frames com dt fixo.
Uso: import drv; drv.run(script_factory, sandbox=..., dt_ms=33)
O script e um generator: `def script(ctx): ... yield` (um yield = um frame do jogo).
"""
import os, sys, time, math, traceback, random, resource, collections

SANDBOX_DEFAULT = "/tmp/se/play"
PROJECT = "/Users/thiagocarvalho/Public/SamuraiEdge"


def make_sandbox(path, copy_files=()):
    """Cria diretorio com main.py (copia) e symlinks para src/ e assets/ (saves ficam isolados aqui)."""
    os.makedirs(path, exist_ok=True)
    for name in ("src", "assets"):
        dst = os.path.join(path, name)
        if not os.path.islink(dst) and not os.path.exists(dst):
            os.symlink(os.path.join(PROJECT, name), dst)
    import shutil
    shutil.copy2(os.path.join(PROJECT, "main.py"), os.path.join(path, "main.py"))
    return path


class Keys:
    def __init__(self):
        self.held = set()

    def __getitem__(self, k):
        return k in self.held

    def get_pressed(self):
        return self


class FakeClock:
    dt_ms = 33
    on_tick = None
    frame = 0

    def __init__(self, *a, **k):
        pass

    def tick(self, fps=0):
        FakeClock.frame += 1
        if FakeClock.on_tick:
            FakeClock.on_tick()
        d = FakeClock.dt_ms
        if callable(d):
            d = d(FakeClock.frame)
        return d

    def tick_busy_loop(self, fps=0):
        return self.tick(fps)

    def get_fps(self):
        return 1000.0 / max(1, FakeClock.dt_ms if not callable(FakeClock.dt_ms) else 33)

    def get_time(self):
        return 16

    def get_rawtime(self):
        return 16


class Done(BaseException):
    pass


class Ctx:
    """Contexto entregue ao script."""

    def __init__(self):
        self.pending = []
        self.keys = Keys()
        self.frame_stats = []
        self.errors = []
        self.log_lines = []
        self.max_frame_ms = 0.0
        self.t_last = time.perf_counter()

    # ---- acesso ao estado de run_game
    def L(self):
        f = sys._getframe(1)
        while f is not None:
            if f.f_code.co_name == "run_game":
                return f.f_locals
            f = f.f_back
        return {}

    @property
    def state(self):
        return self.L().get("game_state")

    def log(self, *a):
        s = " ".join(str(x) for x in a)
        self.log_lines.append(s)
        print(s, flush=True)

    # ---- eventos
    def key(self, k, mod=0, ch=""):
        import pygame
        self.pending.append(pygame.event.Event(pygame.KEYDOWN, key=k, mod=mod, unicode=ch, scancode=0))
        self.pending.append(pygame.event.Event(pygame.KEYUP, key=k, mod=mod, unicode=ch, scancode=0))

    def keydown(self, k, mod=0):
        import pygame
        self.keys.held.add(k)
        self.pending.append(pygame.event.Event(pygame.KEYDOWN, key=k, mod=mod, unicode="", scancode=0))

    def keyup(self, k):
        import pygame
        self.keys.held.discard(k)
        self.pending.append(pygame.event.Event(pygame.KEYUP, key=k, mod=0, unicode="", scancode=0))

    def post(self, ev_type, **kw):
        import pygame
        self.pending.append(pygame.event.Event(ev_type, **kw))

    def click(self, x, y, button=1):
        import pygame
        self.pending.append(pygame.event.Event(pygame.MOUSEMOTION, pos=(x, y), rel=(0, 0), buttons=(0, 0, 0)))
        self.pending.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(x, y), button=button))
        self.pending.append(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(x, y), button=button))


def run(script_factory, sandbox=SANDBOX_DEFAULT, dt_ms=33, max_frames=10_000_000, quiet_pygame=True):
    make_sandbox(sandbox)
    os.chdir(sandbox)
    sys.path.insert(0, sandbox)
    if os.environ.get('RUN_CWD'):
        os.chdir(os.environ['RUN_CWD'])
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame
    ctx = Ctx()
    FakeClock.dt_ms = dt_ms
    FakeClock.frame = 0
    pygame.time.Clock = FakeClock
    pygame.time.delay = lambda ms: 0
    pygame.time.wait = lambda ms: 0
    orig_get = pygame.event.get

    def fake_get(*a, **k):
        try:
            orig_get()  # drena eventos reais (SDL dummy) para nao acumular
        except Exception:
            pass
        evs, ctx.pending = ctx.pending, []
        return evs

    pygame.event.get = fake_get
    pygame.event.pump = lambda *a, **k: None
    pygame.key.get_pressed = lambda: ctx.keys
    if os.environ.get("FAIL_MIXER") == "1":
        def _bad(*a, **k):
            raise pygame.error("simulated: no audio device")
        pygame.mixer.init = _bad
        pygame.mixer.pre_init = lambda *a, **k: None
        _orig_get_init = pygame.mixer.get_init
        pygame.mixer.get_init = lambda: None
    if os.environ.get("FAIL_MIXER") == "2":   # mixer inicia mas Sound()/music.load falham
        class _BadSound:
            def __init__(self, *a, **k):
                raise pygame.error("simulated sound load failure")
        pygame.mixer.Sound = _BadSound
        def _badload(*a, **k):
            raise pygame.error("simulated music load failure")
        pygame.mixer.music.load = _badload
    for _m in filter(None, os.environ.get("BLOCK_MODULES", "").split(",")):
        sys.modules[_m] = None
    if os.environ.get("RAISE_QUIT") != "0":
        os._exit = lambda code=0: (_ for _ in ()).throw(Done())
    if os.environ.get("WORKAROUNDS") == "1":
        import src.input.touch_editor as _te
        _orig_r = _te.TouchControlsEditorScreen.render
        def _r(self, surface, fl=None, fs=None):
            return _orig_r(self, surface, fl or pygame.font.Font(None, 48), fs or pygame.font.Font(None, 20))
        _te.TouchControlsEditorScreen.render = _r
        import src.world.hazards as _hz
        _orig_ph = _hz.FireworkMortars.on_phase
        def _ph(self, *a, **k):
            try:
                return _orig_ph(self, *a, **k)
            except UnboundLocalError:
                ctx.log("  [WORKAROUND] FireworkMortars.on_phase UnboundLocalError (bug conhecido)")
        _hz.FireworkMortars.on_phase = _ph
    gen = script_factory(ctx)
    state = {"done": False}

    def on_tick():
        now = time.perf_counter()
        dtw = (now - ctx.t_last) * 1000
        ctx.max_frame_ms = max(ctx.max_frame_ms, dtw)
        if dtw > 1000 and FakeClock.frame > 2:
            try:
                L = ctx.L()
            except Exception:
                L = {}
            print(f"  [HITCH] frame {FakeClock.frame} took {dtw:.0f} ms; state={L.get('game_state')} prev_state_arena={L.get('selected_arena_id')}", flush=True)
        try:
            next(gen)
        except StopIteration:
            raise Done()
        ctx.t_last = time.perf_counter()

    FakeClock.on_tick = on_tick
    import main as game_main
    ctx.game_main = game_main
    result = {"ok": True}
    try:
        game_main.run_game()
    except Done:
        pass
    except SystemExit:
        pass
    except BaseException:
        result["ok"] = False
        result["tb"] = traceback.format_exc()
        print("=== CRASH in run_game ===")
        print(result["tb"], flush=True)
    return ctx, result


def rss_mb():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / (1024 * 1024) if sys.platform == "darwin" else r / 1024
