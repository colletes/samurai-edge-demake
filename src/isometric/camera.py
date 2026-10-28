"""
Gerenciador de câmera isométrica com suporte a suavização (lerp) e Screen Shake.
"""
import math
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.isometric.iso_math import world_to_iso, iso_depth

class Camera:
    ZOOM_CLOSE = 1.75
    ZOOM_CLOSE_MOBILE = 1.90
    ZOOM_FAR = 0.95
    DIST_CLOSE = 2.8
    DIST_FAR = 8.5
    HUD_SAFE_TOP = 95.0

    def __init__(self, target_wx: float = 11.0, target_wy: float = 11.0):
        # Posição central no mundo que a câmera está olhando
        self.wx = target_wx
        self.wy = target_wy
        self.vx = 0.0
        self.vy = 0.0

        # Offset na tela
        self.screen_x = SCREEN_WIDTH // 2
        self.base_screen_y = SCREEN_HEIGHT // 2
        self.screen_y = self.base_screen_y
        self.overhead_offset_y = 0.0

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

        # Suavização dinâmica de intenção de velocidade (anti-solavanco)
        self.lead_x = 0.0
        self.lead_y = 0.0
        # Enquadramento reativo de projéteis rápidos balísticos (Entregável C-1.3)
        self.projectile_bias_x = 0.0
        self.projectile_bias_y = 0.0

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
    def compute_distance_zoom(cls, dist: float, is_mobile: bool = False) -> float:
        """Calcula o zoom ideal em função da distância entre os lutadores (1.75x no desktop / 1.90x no mobile até 0.95x)."""
        close_zoom = cls.ZOOM_CLOSE_MOBILE if is_mobile else cls.ZOOM_CLOSE
        if dist <= cls.DIST_CLOSE:
            return close_zoom
        if dist >= cls.DIST_FAR:
            return cls.ZOOM_FAR
        t = (dist - cls.DIST_CLOSE) / (cls.DIST_FAR - cls.DIST_CLOSE)
        # Curva Hermite smoothstep cúbica para sustentação orgânica do enquadramento próximo
        smooth_t = t * t * (3.0 - 2.0 * t)
        return close_zoom + (cls.ZOOM_FAR - close_zoom) * smooth_t

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

    def update_combat_framing(self, p1, p2, game_map=None, dt: float = 0.016, is_boss: bool = False, projectiles=None):
        """
        Enquadramento dinâmico de combate (Pilar 7, Entregáveis C-1.1, C-1.2 e C-1.3):
        - Mantém a rotação fixa (`azimuth == 0.0` em duelo normal).
        - Auto-zoom dinâmico com base mais próxima (1.75x a 0.95x).
        - Overhead clamping vertical: evita que saltos e golpes aéreos cortem no HUD.
        - Rastreamento com avanço de velocidade suave (exponential lead decay) sem solavancos em dashes/ataques.
        - Enquadramento direcional reativo de projéteis rápidos (balas de mosquete e flechas).
        - Micro-zoom reativo (`+0.06x`) em parries e deflexões.
        - Clamping inteligente nas bordas da arena.
        """
        if p1 is None or p2 is None:
            return

        w2 = 0.65 if is_boss else 0.50
        mid_x = p1.wx * (1.0 - w2) + p2.wx * w2
        mid_y = p1.wy * (1.0 - w2) + p2.wy * w2

        # Velocity / Action Lead com decaimento exponencial suave (elimina estalos e solavancos)
        desired_lead_x, desired_lead_y = 0.0, 0.0
        for f in (p1, p2):
            st = getattr(f, "state", "IDLE")
            if st in ("DASH", "ROLL", "GATOTSU_CHARGE", "FLECHE", "TACKLE_CHARGE", "JUMP"):
                desired_lead_x += getattr(f, "facing_x", 0.0) * 0.28
                desired_lead_y += getattr(f, "facing_y", 0.0) * 0.28
            elif st in ("ATTACK", "CUTLASS_CLEAVE", "ZEROSHIKI"):
                desired_lead_x += getattr(f, "facing_x", 0.0) * 0.16
                desired_lead_y += getattr(f, "facing_y", 0.0) * 0.16

        # Entregável C-1.3: Enquadramento Direcional Reativo de Projéteis Rápidos
        desired_proj_bias_x = 0.0
        desired_proj_bias_y = 0.0
        max_proj_reach_dist = 0.0

        if projectiles:
            for proj in projectiles:
                if not getattr(proj, "is_active", False):
                    continue
                cls_name = getattr(proj, "__class__", type(None)).__name__
                vx = getattr(proj, "vx", 0.0)
                vy = getattr(proj, "vy", 0.0)
                speed = math.hypot(vx, vy)
                if cls_name in ("MusketBulletProjectile", "KyudoArrowProjectile", "HamayaArrowProjectile", "RopeArrowProjectile", "SacredArrowVolleyProjectile") or speed >= 18.0:
                    dir_x = getattr(proj, "dir_x", None)
                    dir_y = getattr(proj, "dir_y", None)
                    if dir_x is None or dir_y is None:
                        if speed > 1e-4:
                            dir_x = vx / speed
                            dir_y = vy / speed
                        else:
                            dir_x, dir_y = 0.0, 0.0

                    # Adiantamento direcional reativo ao disparo veloz
                    desired_proj_bias_x += dir_x * 0.36
                    desired_proj_bias_y += dir_y * 0.36

                    p_wx = getattr(proj, "wx", 0.0)
                    p_wy = getattr(proj, "wy", 0.0)

                    # Expande o enquadramento se o projétil avançar além do perímetro dos lutadores
                    min_fx = min(p1.wx, p2.wx)
                    max_fx = max(p1.wx, p2.wx)
                    min_fy = min(p1.wy, p2.wy)
                    max_fy = max(p1.wy, p2.wy)

                    if p_wx > max_fx:
                        desired_proj_bias_x += (p_wx - max_fx) * 0.25
                    elif p_wx < min_fx:
                        desired_proj_bias_x += (p_wx - min_fx) * 0.25

                    if p_wy > max_fy:
                        desired_proj_bias_y += (p_wy - max_fy) * 0.25
                    elif p_wy < min_fy:
                        desired_proj_bias_y += (p_wy - min_fy) * 0.25

                    proj_dist = max(math.hypot(p1.wx - p_wx, p1.wy - p_wy), math.hypot(p2.wx - p_wx, p2.wy - p_wy))
                    if proj_dist > max_proj_reach_dist:
                        max_proj_reach_dist = proj_dist
                    break

        # Filtro passa-baixa criticamente amortecido para adiantamento suave
        lead_decay = 1.0 - math.exp(-7.5 * dt)
        self.lead_x += (desired_lead_x - self.lead_x) * min(1.0, lead_decay)
        self.lead_y += (desired_lead_y - self.lead_y) * min(1.0, lead_decay)

        # Filtro passa-baixa para viés de projétil balístico
        proj_decay = 1.0 - math.exp(-8.0 * dt)
        self.projectile_bias_x += (desired_proj_bias_x - self.projectile_bias_x) * min(1.0, proj_decay)
        self.projectile_bias_y += (desired_proj_bias_y - self.projectile_bias_y) * min(1.0, proj_decay)

        target_wx = mid_x + self.lead_x + self.projectile_bias_x
        target_wy = mid_y + self.lead_y + self.projectile_bias_y

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

        from src.input.device_info import is_mobile_device
        is_mobile = is_mobile_device()

        # Calcular zoom alvo pela distância entre os combatentes (Entregável C-1.1 & C-1.3)
        if is_boss:
            base_zoom = 0.90
        else:
            dist = math.hypot(p1.wx - p2.wx, p1.wy - p2.wy)
            if max_proj_reach_dist > dist:
                # Expansão sutil do enquadramento balístico sem perder o duelo de vista
                effective_dist = dist + (max_proj_reach_dist - dist) * 0.45
            else:
                effective_dist = dist
            base_zoom = self.compute_distance_zoom(effective_dist, is_mobile=is_mobile)

        max_cap = 2.05 if is_mobile else 1.90
        self.target_zoom = min(max_cap, base_zoom + self.zoom_impulse)

        # Interpolação suave e criticamente amortecida do zoom
        zoom_lerp = 1.0 - math.exp(-4.5 * dt)
        new_zoom = self.zoom + (self.target_zoom - self.zoom) * min(1.0, zoom_lerp)
        if abs(self.target_zoom - new_zoom) < 0.003:
            self.zoom = round(self.target_zoom, 3)
        else:
            self.zoom = round(new_zoom, 3)

        # Entregável C-1.2: Overhead Clamping & Margem de Segurança contra corte no HUD
        max_overhead_deficit = 0.0
        for f in (p1, p2):
            if not getattr(f, "is_alive", True):
                continue
            f_wz = getattr(f, "wz", 0.0)
            head_wz = f_wz + getattr(f, "height", 1.65)
            st = getattr(f, "state", "")
            if st in ("RYUU_TSUI_SEN", "POLE_VAULT", "JUMP"):
                head_wz += 0.35

            # Projeta a altura da cabeça com a posição de câmera alvo
            _, iso_head_y = world_to_iso(f.wx - target_wx, f.wy - target_wy, head_wz, self.azimuth)
            projected_y = iso_head_y * self.zoom + self.base_screen_y
            if projected_y < self.HUD_SAFE_TOP:
                deficit = self.HUD_SAFE_TOP - projected_y
                if deficit > max_overhead_deficit:
                    max_overhead_deficit = deficit

        # Limitar o deslocamento para não empurrar os pés fora do chão visível
        desired_overhead_shift = min(120.0, max_overhead_deficit)
        lerp_rate = 8.5 if desired_overhead_shift > self.overhead_offset_y else 5.0
        decay = 1.0 - math.exp(-lerp_rate * dt)
        self.overhead_offset_y += (desired_overhead_shift - self.overhead_offset_y) * min(1.0, decay)

        self.screen_y = int(round(self.base_screen_y + self.overhead_offset_y))

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

