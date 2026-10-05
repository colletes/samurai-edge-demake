"""
Entregável 7.2: câmera dramática de nocaute (instant replay orbital).

Quando um lutador é abatido, a câmera gira lentamente (azimute real, Entregável 6.1) ao redor do
derrotado em câmera lenta e depois volta suave à vista clássica. A tela de resultados da partida só
aparece depois do replay. A classe guarda apenas tempo e estado; o laço principal aplica o resultado.
"""
import math

from src.config import SCREEN_HEIGHT
from src.ui.camera_moves import smooth as _smooth, ease_out as _ease_out, lerp as _lerp

T_ORBIT = 2.5            # órbita lenta ao redor do derrotado
T_RETURN = 0.6           # volta suave à vista clássica
ORBIT_DEG = 70.0
ORBIT_ZOOM = 1.75
ORBIT_SHIFT_Y = 40
SLOWMO_SCALE = 0.3       # fração da velocidade normal no auge do replay
SLOWMO_HOLD = 1.2        # tempo sustentado em câmera lenta antes de voltar à velocidade normal


class KnockoutCam:
    def __init__(self):
        self.pending = False     # aguardando o fim do congelamento cinematográfico para começar
        self.active = False
        self.used = False        # um replay por round
        self.time = 0.0
        self.target = (0.0, 0.0)
        self.mid = (0.0, 0.0)
        self.deferred_result = None  # dados da tela de resultados, exibidos só após o replay

    def reset(self):
        self.pending = False
        self.active = False
        self.used = False
        self.time = 0.0
        self.deferred_result = None

    def arm(self, target: tuple[float, float]):
        """Marca o nocaute; o replay começa em begin() quando a simulação descongela."""
        if self.used:
            return
        self.used = True
        self.pending = True
        self.target = target

    def begin(self):
        self.pending = False
        self.active = True
        self.time = 0.0

    def skip(self):
        self.active = False
        self.pending = False

    def update(self, dt: float, mid: tuple[float, float]):
        """dt em tempo real (sem a câmera lenta)."""
        self.mid = mid
        if not self.active:
            return
        self.time += dt
        if self.time >= T_ORBIT + T_RETURN:
            self.active = False

    def time_scale(self) -> float:
        """Fator de câmera lenta aplicado à simulação durante o replay."""
        if not self.active:
            return 1.0
        if self.time <= SLOWMO_HOLD:
            return SLOWMO_SCALE
        return _lerp(SLOWMO_SCALE, 1.0, _smooth((self.time - SLOWMO_HOLD) / (T_ORBIT - SLOWMO_HOLD)))

    def camera_state(self) -> dict:
        """Foco (wx, wy), azimute (rad), zoom e deslocamento vertical no instante atual."""
        sweep = math.radians(ORBIT_DEG)
        if self.time <= T_ORBIT:
            k = _ease_out(self.time / T_ORBIT)
            return dict(focus=self.target, azimuth=sweep * k, zoom=_lerp(1.0, ORBIT_ZOOM, k),
                        shift_y=ORBIT_SHIFT_Y * k)
        k = _smooth((self.time - T_ORBIT) / T_RETURN)
        return dict(focus=(_lerp(self.target[0], self.mid[0], k), _lerp(self.target[1], self.mid[1], k)),
                    azimuth=_lerp(sweep, 0.0, k), zoom=_lerp(ORBIT_ZOOM, 1.0, k),
                    shift_y=ORBIT_SHIFT_Y * (1.0 - k))

    def apply_camera(self, camera, dt: float):
        st = self.camera_state()
        camera.update(st["focus"][0], st["focus"][1], dt)
        camera.set_azimuth(st["azimuth"])
        camera.zoom = st["zoom"]
        camera.screen_y = SCREEN_HEIGHT // 2 + int(st["shift_y"])

    @staticmethod
    def restore_classic(camera):
        """Garante a vista clássica depois do replay."""
        camera.set_azimuth(0.0)
        camera.zoom = 1.0
        camera.screen_y = SCREEN_HEIGHT // 2
