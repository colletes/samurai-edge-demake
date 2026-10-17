"""
Gerenciador de câmera isométrica com suporte a suavização (lerp) e Screen Shake.
"""
import math
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.isometric.iso_math import world_to_iso, iso_depth

class Camera:
    ZOOM_CLOSE = 1.28
    ZOOM_FAR = 0.88
    DIST_CLOSE = 3.0
    DIST_FAR = 9.0

    def __init__(self, target_wx: float = 11.0, target_wy: float = 11.0):
        # Posição central no mundo que a câmera está olhando
        self.wx = target_wx
        self.wy = target_wy
        self.vx = 0.0
        self.vy = 0.0

        # Offset na tela
        self.screen_x = SCREEN_WIDTH // 2
        self.screen_y = SCREEN_HEIGHT // 2

        # Sistema de Screen Shake (tremor na tela)
        self.shake_intensity = 0.0
        self.shake_decay = 0.90
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

        # Fator de zoom dramático e auto-zoom de combate. 1.0 = neutro padrão.
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_impulse = 0.0
        self._last_parry_state = (False, False)

        # Altura do piso sob o foco (ex.: tabuleiro da ponte), onde as sombras dos lutadores são desenhadas
        self.ground_z = 0.0
        # Azimute (radianos): giro do mundo em torno do alvo da câmera. 0.0 = vista isométrica clássica.
        self.azimuth = 0.0
        # Relevo visual do piso (arenas com telhados inclinados): altura extra somada a todo ponto desenhado
        self.height_fn = None

    def set_azimuth(self, azimuth: float):
        """Define o azimute normalizado em (-pi, pi]."""
        self.azimuth = math.atan2(math.sin(azimuth), math.cos(azimuth))

    def rotate(self, delta: float):
        """Gira a câmera por delta radianos a partir do azimute atual."""
        self.set_azimuth(self.azimuth + delta)

    def depth(self, wx: float, wy: float) -> float:
        """Profundidade na tela (maior = mais próximo) para ordenação de renderização com o azimute atual."""
        return iso_depth(wx, wy, self.azimuth)

    def add_shake(self, intensity: float):
        """Adiciona intensidade de tremor na tela (ex: golpes pesados, clash ou morte)."""
        self.shake_intensity = max(self.shake_intensity, intensity)

    def add_zoom_impulse(self, impulse: float = 0.06):
        """Adiciona um micro-zoom temporário de impacto (ex.: parry, deflexão, golpe pesado)."""
        self.zoom_impulse = max(self.zoom_impulse, min(0.16, impulse))

    @classmethod
    def compute_distance_zoom(cls, dist: float) -> float:
        """Calcula o zoom ideal em função da distância entre os lutadores (1.28x em melee <=3u até 0.88x >=9u)."""
        if dist <= cls.DIST_CLOSE:
            return cls.ZOOM_CLOSE
        if dist >= cls.DIST_FAR:
            return cls.ZOOM_FAR
        t = (dist - cls.DIST_CLOSE) / (cls.DIST_FAR - cls.DIST_CLOSE)
        # Curva Hermite smoothstep
        smooth_t = t * t * (3.0 - 2.0 * t)
        return cls.ZOOM_CLOSE + (cls.ZOOM_FAR - cls.ZOOM_CLOSE) * smooth_t

    def update(self, target_wx: float, target_wy: float, dt: float):
        """Atualiza a posição da câmera com suavização (lerp) em direção ao alvo."""
        lerp_speed = 6.0 * dt
        self.wx += (target_wx - self.wx) * min(lerp_speed, 1.0)
        self.wy += (target_wy - self.wy) * min(lerp_speed, 1.0)

        if self.zoom_impulse > 0.001:
            self.zoom_impulse *= math.exp(-6.0 * dt)
        else:
            self.zoom_impulse = 0.0

        # Atualizar tremor de tela
        if self.shake_intensity > 0.5:
            self.shake_offset_x = (random.random() * 2.0 - 1.0) * self.shake_intensity
            self.shake_offset_y = (random.random() * 2.0 - 1.0) * self.shake_intensity
            self.shake_intensity *= self.shake_decay
        else:
            self.shake_intensity = 0.0
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0

    def update_combat_framing(self, p1, p2, game_map=None, dt: float = 0.016, is_boss: bool = False):
        """
        Enquadramento dinâmico de combate (Pilar 7):
        - Mantém a rotação fixa (`azimuth == 0.0` em duelo normal).
        - Auto-zoom suave baseado na distância entre os lutadores (`0.88x` a `1.28x`).
        - Rastreamento com avanço de velocidade/intenção (velocity lead) durante ataques/dashes.
        - Micro-zoom reativo (`+0.06x`) em parries e deflexões.
        - Clamping inteligente nas bordas da arena.
        """
        if p1 is None or p2 is None:
            return

        w2 = 0.65 if is_boss else 0.50
        mid_x = p1.wx * (1.0 - w2) + p2.wx * w2
        mid_y = p1.wy * (1.0 - w2) + p2.wy * w2

        # Velocity / Action Lead: antecipa levemente o movimento em investidas e ataques
        lead_x, lead_y = 0.0, 0.0
        for f in (p1, p2):
            st = getattr(f, "state", "IDLE")
            if st in ("DASH", "ROLL", "GATOTSU_CHARGE", "FLECHE", "TACKLE_CHARGE", "JUMP"):
                lead_x += getattr(f, "facing_x", 0.0) * 0.28
                lead_y += getattr(f, "facing_y", 0.0) * 0.28
            elif st in ("ATTACK", "CUTLASS_CLEAVE", "ZEROSHIKI"):
                lead_x += getattr(f, "facing_x", 0.0) * 0.16
                lead_y += getattr(f, "facing_y", 0.0) * 0.16

        target_wx = mid_x + lead_x
        target_wy = mid_y + lead_y

        # Clamping inteligente dentro dos limites da arena
        if game_map is not None:
            bounds = getattr(game_map, "playable_bounds", None)
            if bounds is not None and len(bounds) == 4:
                x0, y0, x1, y1 = bounds
                margin_x = min(2.2, (x1 - x0) * 0.18)
                margin_y = min(2.2, (y1 - y0) * 0.18)
                target_wx = max(x0 + margin_x, min(x1 - margin_x, target_wx))
                target_wy = max(y0 + margin_y, min(y1 - margin_y, target_wy))
            else:
                cols = getattr(game_map, "cols", 22)
                rows = getattr(game_map, "rows", 22)
                margin = 3.2
                target_wx = max(margin, min(cols - margin, target_wx))
                target_wy = max(margin, min(rows - margin, target_wy))

        # Detectar parry / postura defensiva recém-ativada para micro-zoom
        p1_parry = getattr(p1, "state", "") in ("PARRY", "COUNTER_THRUST")
        p2_parry = getattr(p2, "state", "") in ("PARRY", "COUNTER_THRUST")
        if (p1_parry and not self._last_parry_state[0]) or (p2_parry and not self._last_parry_state[1]):
            self.add_zoom_impulse(0.06)
        self._last_parry_state = (p1_parry, p2_parry)

        # Calcular zoom alvo pela distância entre os combatentes
        if is_boss:
            base_zoom = 0.85
        else:
            dist = math.hypot(p1.wx - p2.wx, p1.wy - p2.wy)
            base_zoom = self.compute_distance_zoom(dist)

        self.target_zoom = min(1.42, base_zoom + self.zoom_impulse)

        # Interpolação criticamente amortecida do zoom (quantizada ao estabilizar para maximizar hits do cache de terreno)
        zoom_lerp = min(1.0, dt * 5.2)
        new_zoom = self.zoom + (self.target_zoom - self.zoom) * zoom_lerp
        if abs(self.target_zoom - new_zoom) < 0.004:
            self.zoom = round(self.target_zoom, 3)
        else:
            self.zoom = round(new_zoom, 3)

        # Atualizar posição e screen shake
        self.update(target_wx, target_wy, dt)

    def apply(self, wx: float, wy: float, wz: float = 0.0) -> tuple[int, int]:
        """
        Converte coordenadas de mundo para as coordenadas finais de renderização
        na janela, considerando a posição da câmera e o screen shake.
        """
        if self.height_fn is not None:
            wz += self.height_fn(wx, wy)
        iso_x, iso_y = world_to_iso(wx - self.wx, wy - self.wy, wz, self.azimuth)

        dx = iso_x * self.zoom
        dy = iso_y * self.zoom

        final_x = int(dx + self.screen_x + self.shake_offset_x)
        final_y = int(dy + self.screen_y + self.shake_offset_y)
        return final_x, final_y

