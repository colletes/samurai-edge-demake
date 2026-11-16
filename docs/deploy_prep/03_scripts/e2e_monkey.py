"""Monkey test: eventos aleatorios (teclado, mouse, gamepad, toque, resize) em todas as telas via main.run_game().
Uso: e2e_monkey.py SEED FRAMES SANDBOX"""
import os, sys, time, random, json, collections
sys.path.insert(0, "/tmp/se")
import drv
import pygame

SEED = int(sys.argv[1])
FRAMES = int(sys.argv[2])
SANDBOX = sys.argv[3]
rnd = random.Random(SEED)

NAV = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN, pygame.K_RETURN, pygame.K_RETURN,
       pygame.K_SPACE, pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_e, pygame.K_j, pygame.K_k, pygame.K_i,
       pygame.K_TAB, pygame.K_c, pygame.K_F3, pygame.K_BACKSPACE, pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET, pygame.K_BACKSLASH,
       pygame.K_r, pygame.K_t, pygame.K_o, pygame.K_p, pygame.K_l, pygame.K_KP_ENTER, pygame.K_PAGEUP, pygame.K_PAGEDOWN,
       pygame.K_HOME, pygame.K_END, pygame.K_DELETE, pygame.K_F1, pygame.K_F2, pygame.K_F5, pygame.K_F11, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_0]
DTS = [0, 1, 8, 16, 16, 33, 33, 33, 50, 100, 250, 1000]


def script(ctx):
    sys.path.insert(0, SANDBOX)
    import src.ui.pause_menu as pmod
    _oc = pmod.PauseMenu._choose
    def _choose(self, index):
        r = _oc(self, index)
        return None if r == pmod.ACTION_QUIT else r
    pmod.PauseMenu._choose = _choose
    drv.FakeClock.dt_ms = lambda fr: rnd.choice(DTS)
    visited = collections.Counter()
    last_state = None
    t0 = time.time()
    held = set()
    for fr in range(FRAMES):
        L = ctx.L()
        st = L.get("game_state")
        pm = L.get("pause_menu")
        sm = L.get("settings_menu")
        gal = L.get("gallery_screen")
        tag = st
        if pm is not None and pm.is_open: tag = f"{st}/pause"
        if sm is not None and sm.is_open: tag = f"{st}/settings"
        if gal is not None and gal.is_open: tag = f"{st}/gallery"
        visited[tag] += 1
        if tag != last_state:
            ctx.log(f"[{fr}] -> {tag}")
            last_state = tag
        n_events = rnd.choice([0, 1, 1, 2, 3])
        for _ in range(n_events):
            r = rnd.random()
            if r < 0.50:
                k = rnd.choice(NAV)
                if k == pygame.K_ESCAPE and st == "title":
                    continue
                mod = rnd.choice([0, 0, 0, pygame.KMOD_SHIFT, pygame.KMOD_CTRL, pygame.KMOD_META, pygame.KMOD_ALT])
                if rnd.random() < 0.25 and k not in held:
                    ctx.keydown(k, mod); held.add(k)
                elif k in held:
                    ctx.keyup(k); held.discard(k)
                else:
                    ctx.key(k, mod, ch=chr(k) if 32 <= k < 127 else "")
            elif r < 0.55 and st != "title":
                ctx.key(pygame.K_ESCAPE)
            elif r < 0.68:
                x, y = rnd.randint(-50, 1330), rnd.randint(-50, 770)
                kind = rnd.random()
                if kind < 0.5:
                    ctx.click(x, y, rnd.choice([1, 1, 1, 2, 3]))
                elif kind < 0.8:
                    ctx.post(pygame.MOUSEMOTION, pos=(x, y), rel=(rnd.randint(-30, 30), rnd.randint(-30, 30)), buttons=(0, 0, 0))
                else:
                    ctx.post(pygame.MOUSEWHEEL, x=rnd.randint(-3, 3), y=rnd.randint(-3, 3), flipped=False, which=0, precise_x=0.0, precise_y=0.0)
                    ctx.post(pygame.MOUSEBUTTONDOWN, pos=(x, y), button=rnd.choice([4, 5]))
            elif r < 0.80:
                kind = rnd.random()
                if kind < 0.45:
                    b = rnd.randint(0, 20)
                    if tag == "title" and b in (4, 5):
                        b = 0
                    ctx.post(pygame.JOYBUTTONDOWN, instance_id=rnd.choice([0, 1, 7]), joy=0, button=b)
                    ctx.post(pygame.JOYBUTTONUP, instance_id=0, joy=0, button=rnd.randint(0, 20))
                elif kind < 0.65:
                    ctx.post(pygame.JOYHATMOTION, instance_id=0, joy=0, hat=0, value=(rnd.choice([-1, 0, 1]), rnd.choice([-1, 0, 1])))
                elif kind < 0.85:
                    ctx.post(pygame.JOYAXISMOTION, instance_id=0, joy=0, axis=rnd.randint(0, 6), value=rnd.choice([-1.0, -0.7, 0.0, 0.3, 0.9, 1.0, float('nan')]))
                elif kind < 0.93:
                    ctx.post(pygame.JOYDEVICEADDED, device_index=rnd.randint(0, 3))
                else:
                    ctx.post(pygame.JOYDEVICEREMOVED, instance_id=rnd.randint(0, 3))
            elif r < 0.86:
                x, y = rnd.random(), rnd.random()
                t = rnd.choice([pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP])
                ctx.post(t, x=x, y=y, dx=0.0, dy=0.0, pressure=1.0, finger_id=rnd.randint(0, 3), touch_id=0)
            elif r < 0.90:
                w, h = rnd.choice([(1280, 720), (1280, 800), (1920, 1080), (800, 600), (320, 200), (1, 1), (0, 0), (2560, 1440), (640, 1136), (3840, 2160)])
                ctx.post(pygame.VIDEORESIZE, size=(w, h), w=w, h=h)
            elif r < 0.93:
                ctx.post(pygame.WINDOWFOCUSLOST) if hasattr(pygame, "WINDOWFOCUSLOST") else None
                ctx.post(pygame.WINDOWFOCUSGAINED) if hasattr(pygame, "WINDOWFOCUSGAINED") else None
                ctx.post(pygame.TEXTINPUT, text=rnd.choice(["a", "é", "日", "😀"]))
            elif r < 0.95:
                ctx.post(pygame.ACTIVEEVENT, gain=rnd.choice([0, 1]), state=2)
            else:
                ctx.post(pygame.USEREVENT + rnd.randint(0, 5))
        yield
    ctx.log("MONKEY_DONE visited:", dict(visited), f"t={time.time()-t0:.0f}s maxframe={ctx.max_frame_ms:.0f}ms")
    raise drv.Done()


if __name__ == "__main__":
    ctx, res = drv.run(script, sandbox=SANDBOX, dt_ms=33)
    sys.exit(0 if res["ok"] else 3)
