"""
Sistema de Controles Virtuais Touchscreen (On-Screen Touch Controls).
Oferece Joystick Virtual direcional, botões táteis de ação com multi-touch real (FINGER*),
suporte a toque contínuo (hold) e estética visual feudal samurai com transparência e brilho.
"""
import math
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_RED_AURA,
    COLOR_BLUE_AURA, COLOR_STEEL
)
from src.ui.font_manager import render_text_fx

# Modos de exibição dos controles na tela
TOUCH_MODE_AUTO = "auto"
TOUCH_MODE_ALWAYS = "always"
TOUCH_MODE_OFF = "off"

class VirtualJoystick:
    """Joystick analógico virtual para o polegar esquerdo."""
    def __init__(self, base_x: float = 160, base_y: float = 570, radius: float = 80, knob_radius: float = 38):
        self.default_x = base_x
        self.default_y = base_y
        self.center_x = base_x
        self.center_y = base_y
        self.knob_x = base_x
        self.knob_y = base_y
        self.radius = radius
        self.knob_radius = knob_radius
        self.deadzone = 14.0

        self.finger_id: int | None = None
        self.is_active = False
        self.dx = 0.0
        self.dy = 0.0

        # Cache de superfícies para 60 FPS estáveis
        self._cached_base_surf: pygame.Surface | None = None
        self._base_cache_radius: int = -1
        self._cached_knob_normal: pygame.Surface | None = None
        self._cached_knob_active: pygame.Surface | None = None
        self._knob_cache_radius: int = -1

    def contains(self, vx: float, vy: float) -> bool:
        """Determina se uma coordenada virtual cai na zona de ativação do joystick (toda a metade esquerda da tela)."""
        return vx <= (SCREEN_WIDTH * 0.50)

    def on_touch_down(self, finger_id: int, vx: float, vy: float) -> bool:
        if self.contains(vx, vy) and self.finger_id is None:
            self.finger_id = finger_id
            self.is_active = True
            # Posicionamento dinâmico no ponto do toque inicial
            self.center_x = vx
            self.center_y = vy
            self.knob_x = vx
            self.knob_y = vy
            self._update_vector(vx, vy)
            return True
        return False

    def on_touch_motion(self, finger_id: int, vx: float, vy: float) -> bool:
        if self.is_active and self.finger_id == finger_id:
            self._update_vector(vx, vy)
            return True
        return False

    def on_touch_up(self, finger_id: int) -> bool:
        if self.is_active and self.finger_id == finger_id:
            self.reset()
            return True
        return False

    def _update_vector(self, vx: float, vy: float):
        delta_x = vx - self.center_x
        delta_y = vy - self.center_y
        dist = math.hypot(delta_x, delta_y)

        if dist < self.deadzone:
            self.dx = 0.0
            self.dy = 0.0
            self.knob_x = self.center_x
            self.knob_y = self.center_y
        else:
            # Trava o knob dentro do raio máximo do anel
            clamped_dist = min(dist, self.radius)
            norm_x = delta_x / dist
            norm_y = delta_y / dist
            self.knob_x = self.center_x + norm_x * clamped_dist
            self.knob_y = self.center_y + norm_y * clamped_dist

            # Intensidade normalizada (0.0 a 1.0)
            factor = (clamped_dist - self.deadzone) / (self.radius - self.deadzone)
            self.dx = norm_x * factor
            self.dy = norm_y * factor

    def reset(self):
        self.finger_id = None
        self.is_active = False
        self.dx = 0.0
        self.dy = 0.0
        self.center_x = self.default_x
        self.center_y = self.default_y
        self.knob_x = self.default_x
        self.knob_y = self.default_y

    def render(self, surface: pygame.Surface):
        # 1. Base do Manche (Arruela de Poeira / Dust Washer & Aro de Montagem do Gabinete)
        r_int = int(self.radius)
        if self._cached_base_surf is None or self._base_cache_radius != r_int:
            self._cached_base_surf = _render_joystick_base_surf(self.radius, self.knob_radius)
            self._base_cache_radius = r_int

        base_ox = self._cached_base_surf.get_width() // 2
        base_oy = self._cached_base_surf.get_height() // 2
        surface.blit(self._cached_base_surf, (int(self.center_x - base_ox), int(self.center_y - base_oy)))

        # 2. Haste de Aço Cromada (Steel Shaft) quando o manche é inclinado
        dist = math.hypot(self.knob_x - self.center_x, self.knob_y - self.center_y)
        if dist > 5.0:
            # Sombra tubular inferior
            pygame.draw.line(surface, (25, 28, 32), (int(self.center_x + 1), int(self.center_y + 2)), (int(self.knob_x + 1), int(self.knob_y + 2)), 8)
            # Haste cilíndrica de aço polido
            pygame.draw.line(surface, (145, 155, 165), (int(self.center_x), int(self.center_y)), (int(self.knob_x), int(self.knob_y)), 7)
            # Filete de reflexo de luz cromado
            pygame.draw.line(surface, (238, 244, 250), (int(self.center_x - 1), int(self.center_y - 1)), (int(self.knob_x - 1), int(self.knob_y - 1)), 2)

        # 3. Manopla Esférica Sanwa LB-35 Translúcida (Balltop)
        kr_int = int(self.knob_radius)
        if self._cached_knob_normal is None or self._knob_cache_radius != kr_int:
            self._cached_knob_normal = _render_joystick_balltop_surf(self.knob_radius, False)
            self._cached_knob_active = _render_joystick_balltop_surf(self.knob_radius, True)
            self._knob_cache_radius = kr_int

        knob_surf = self._cached_knob_active if self.is_active else self._cached_knob_normal
        knob_ox = knob_surf.get_width() // 2
        knob_oy = knob_surf.get_height() // 2
        surface.blit(knob_surf, (int(self.knob_x - knob_ox), int(self.knob_y - knob_oy)))


class TouchButton:
    """Botão circular tátil com estética de botão de arcade retro translúcido (Sanwa OBSF-30 Candy)."""
    def __init__(self, cx: float, cy: float, radius: float, label: str, sublabel: str = "", primary_color=(195, 32, 42)):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.label = label
        self.sublabel = sublabel
        self.primary_color = primary_color

        self.finger_id: int | None = None
        self.is_down = False
        self.just_pressed = False
        self.just_released = False

        # Cache de superfícies pré-renderizadas para 60 FPS estáveis
        self._cached_surf_normal: pygame.Surface | None = None
        self._cached_surf_pressed: pygame.Surface | None = None
        self._cache_key: tuple | None = None

    def contains(self, vx: float, vy: float) -> bool:
        return math.hypot(vx - self.cx, vy - self.cy) <= (self.radius * 1.25)

    def on_touch_down(self, finger_id: int, vx: float, vy: float) -> bool:
        if self.contains(vx, vy) and self.finger_id is None:
            self.finger_id = finger_id
            self.is_down = True
            self.just_pressed = True
            return True
        return False

    def on_touch_up(self, finger_id: int) -> bool:
        if self.finger_id == finger_id:
            self.finger_id = None
            self.is_down = False
            self.just_released = True
            return True
        return False

    def reset_frame_state(self):
        """Limpa o gatilho de disparo de clique no início de cada frame."""
        self.just_pressed = False
        self.just_released = False

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_small: pygame.font.Font):
        key = (int(self.radius), self.label, self.sublabel, self.primary_color)
        if self._cached_surf_normal is None or self._cache_key != key:
            self._cached_surf_normal = _render_arcade_button_surf(
                self.radius, self.label, self.sublabel, self.primary_color, False, font_large, font_small
            )
            self._cached_surf_pressed = _render_arcade_button_surf(
                self.radius, self.label, self.sublabel, self.primary_color, True, font_large, font_small
            )
            self._cache_key = key

        surf = self._cached_surf_pressed if self.is_down else self._cached_surf_normal
        ox = surf.get_width() // 2
        oy = surf.get_height() // 2
        surface.blit(surf, (int(self.cx - ox), int(self.cy - oy)))


def _render_arcade_button_surf(
    radius: float,
    label: str,
    sublabel: str,
    primary_color: tuple[int, int, int],
    is_pressed: bool,
    font_large: pygame.font.Font,
    font_small: pygame.font.Font
) -> pygame.Surface:
    """Gera uma superfície com o botão de arcade translúcido (OBSF-30 Candy)."""
    pad = 12
    dim = int((radius + pad) * 2)
    surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
    bcx = dim // 2
    bcy = dim // 2

    r, g, b = primary_color

    # 1. Sombra de montagem no painel do gabinete
    shadow_y = 3
    shadow_alpha = 75 if not is_pressed else 95
    pygame.draw.circle(surf, (0, 0, 0, shadow_alpha), (bcx + 1, bcy + shadow_y), int(radius + 1))

    # 2. Aro Externo / Bezel de Montagem (Anel de retenção escurecido chanfrado)
    pygame.draw.circle(surf, (26, 30, 34, 215), (bcx, bcy), int(radius))
    bezel_rect = pygame.Rect(bcx - radius, bcy - radius, radius * 2, radius * 2)
    # Chanfro superior (luz de topo do gabinete)
    pygame.draw.arc(surf, (180, 192, 204, 150), bezel_rect, 0.7, 2.5, width=2)
    # Chanfro inferior (sombra de rebaixo)
    pygame.draw.arc(surf, (10, 12, 14, 235), bezel_rect, 3.8, 5.6, width=2)
    pygame.draw.circle(surf, (14, 16, 18, 220), (bcx, bcy), int(radius), width=1)

    # 3. Folga Mecânica do Cilindro (Recessed Well Gap)
    pygame.draw.circle(surf, (6, 8, 10, 240), (bcx, bcy), int(radius - 3), width=2)

    # 4. Êmbolo Convexo Translúcido (Plunger)
    p_radius = radius - 5.0
    # Deslocamento mecânico para baixo ao pressionar (afunda 3px no gabinete!)
    p_cy = bcy + (3 if is_pressed else 0)

    # Se pressionado, expõe sombra interna no topo do cilindro
    if is_pressed:
        p_well = pygame.Rect(bcx - p_radius - 1, bcy - p_radius - 2, (p_radius + 1) * 2, (p_radius + 1) * 2)
        pygame.draw.arc(surf, (5, 5, 8, 210), p_well, 0.5, 2.6, width=3)

    # Saia translúcida principal
    skirt_alpha = 235 if is_pressed else 165
    pygame.draw.circle(surf, (r, g, b, skirt_alpha), (bcx, int(p_cy)), int(p_radius))

    # Degrau interno de refração acrílica (gradiente de profundidade)
    depth_alpha = 200 if is_pressed else 135
    depth_col = (min(255, r + 28), min(255, g + 28), min(255, b + 28), depth_alpha)
    pygame.draw.circle(surf, depth_col, (bcx, int(p_cy)), int(p_radius * 0.82))

    # Borda externa polida do êmbolo
    rim_col = (min(255, r + 65), min(255, g + 65), min(255, b + 65), 210)
    pygame.draw.circle(surf, rim_col, (bcx, int(p_cy)), int(p_radius), width=2)

    # 5. Núcleo Mecânico Interno (Microswitch Activator Stem visível pelo acrílico)
    core_r = int(p_radius * 0.42)
    if is_pressed:
        # Iluminação interna do switch ativado (Glow LED)
        pygame.draw.circle(surf, (255, 248, 210, 240), (bcx, int(p_cy)), core_r)
        pygame.draw.circle(surf, (255, 255, 255, 255), (bcx, int(p_cy)), int(core_r * 0.55))
        pygame.draw.circle(surf, (255, 215, 0, 230), (bcx, int(p_cy)), int(core_r * 1.15), width=2)
    else:
        # Haste interna de contato mecânico na penumbra
        core_col = (max(0, r - 35), max(0, g - 35), max(0, b - 35), 180)
        pygame.draw.circle(surf, core_col, (bcx, int(p_cy)), core_r)
        pygame.draw.circle(surf, (255, 235, 170, 110), (bcx, int(p_cy)), int(core_r * 0.40))
        pygame.draw.circle(surf, (min(255, r + 45), min(255, g + 45), min(255, b + 45), 150), (bcx, int(p_cy)), core_r, width=1)

    # 6. Reflexo Curvo do Domo Acrílico (Acrylic Convex Dome Highlight)
    # Lábio superior do êmbolo (arco nítido)
    top_lip_rect = pygame.Rect(bcx - p_radius + 1, int(p_cy - p_radius + 1), int((p_radius - 1) * 2), int((p_radius - 1) * 2))
    pygame.draw.arc(surf, (255, 255, 255, 220), top_lip_rect, 0.7, 2.4, width=2)

    # Arco secundário interno suave
    inner_arc_rect = pygame.Rect(bcx - p_radius + 3, int(p_cy - p_radius + 3), int((p_radius - 3) * 2), int((p_radius - 3) * 2))
    pygame.draw.arc(surf, (255, 255, 255, 120), inner_arc_rect, 0.8, 2.3, width=2)

    # Brilho elíptico superior no domo (posicionado no topo, sem encobrir o texto)
    hl_w = int(p_radius * 0.80)
    hl_h = int(p_radius * 0.28)
    hl_cx = bcx
    hl_cy = int(p_cy - p_radius * 0.48)
    hl_rect = pygame.Rect(hl_cx - hl_w // 2, hl_cy - hl_h // 2, hl_w, hl_h)
    pygame.draw.ellipse(surf, (255, 255, 255, 85 if not is_pressed else 130), hl_rect)

    # 7. Tipografia Diegética de Arcade (render_text_fx com contorno nítido e relevo)
    lbl_base_y = p_cy - (7 if sublabel else 0)
    lbl_col = (255, 255, 255) if not is_pressed else (255, 250, 190)
    lbl_surf = render_text_fx(
        font_large,
        label,
        color=lbl_col,
        outline=True,
        outline_color=(10, 12, 16),
        outline_width=1,
        shadow=True,
        shadow_color=(0, 0, 0),
        shadow_offset=(1, 2)
    )
    surf.blit(lbl_surf, (bcx - lbl_surf.get_width() // 2, int(lbl_base_y - lbl_surf.get_height() // 2)))

    if sublabel:
        sub_y = p_cy + 13
        sub_col = (255, 225, 150) if not is_pressed else (255, 255, 225)
        sub_surf = render_text_fx(
            font_small,
            sublabel,
            color=sub_col,
            outline=True,
            outline_color=(8, 10, 14),
            outline_width=1,
            shadow=True,
            shadow_color=(0, 0, 0),
            shadow_offset=(1, 1)
        )
        surf.blit(sub_surf, (bcx - sub_surf.get_width() // 2, int(sub_y)))

    return surf


def _render_joystick_base_surf(radius: float, knob_radius: float) -> pygame.Surface:
    """Gera a base do manche de arcade (arruela de borracha com estrias concêntricas e rebites)."""
    pad = 16
    dim = int((radius + pad) * 2)
    surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
    bcx = dim // 2
    bcy = dim // 2

    # 1. Sombra projetada da base
    pygame.draw.circle(surf, (0, 0, 0, 75), (bcx + 2, bcy + 3), int(radius + 2))

    # 2. Aro metálico externo do gabinete
    pygame.draw.circle(surf, (45, 50, 56, 190), (bcx, bcy), int(radius))
    pygame.draw.circle(surf, (160, 170, 180, 120), (bcx, bcy), int(radius), width=2)
    pygame.draw.circle(surf, (15, 18, 22, 220), (bcx, bcy), int(radius - 3), width=1)

    # 3. 4 Rebites / Parafusos Cromados de Fixação (45°, 135°, 225°, 315°)
    for deg in (45, 135, 225, 315):
        rad = math.radians(deg)
        sx = bcx + math.cos(rad) * (radius - 5)
        sy = bcy + math.sin(rad) * (radius - 5)
        pygame.draw.circle(surf, (190, 200, 210, 220), (int(sx), int(sy)), 3)
        pygame.draw.circle(surf, (40, 45, 50, 240), (int(sx), int(sy)), 1)

    # 4. Disco da Arruela de Poeira (Dust Washer) em acrílico preto acetinado
    pygame.draw.circle(surf, (22, 25, 29, 205), (bcx, bcy), int(radius - 5))

    # 5. Estrias Concêntricas Típicas de Borracha (Vinyl Grooves)
    pygame.draw.circle(surf, (48, 54, 60, 150), (bcx, bcy), int(radius * 0.76), width=1)
    pygame.draw.circle(surf, (48, 54, 60, 150), (bcx, bcy), int(radius * 0.52), width=1)
    pygame.draw.circle(surf, (48, 54, 60, 150), (bcx, bcy), int(radius * 0.32), width=1)

    # 6. Marcadores Japoneses de Direção (8-way Gate Ticks)
    for deg in (0, 45, 90, 135, 180, 225, 270, 315):
        rad = math.radians(deg)
        is_cardinal = (deg % 90 == 0)
        r_start = radius * (0.84 if is_cardinal else 0.88)
        r_end = radius * 0.94
        x1 = bcx + math.cos(rad) * r_start
        y1 = bcy + math.sin(rad) * r_start
        x2 = bcx + math.cos(rad) * r_end
        y2 = bcy + math.sin(rad) * r_end
        tick_col = (212, 175, 55, 180) if is_cardinal else (130, 140, 150, 130)
        pygame.draw.line(surf, tick_col, (int(x1), int(y1)), (int(x2), int(y2)), 2 if is_cardinal else 1)

    # 7. Abertura Central onde o Manche Penetra (Socket)
    socket_r = int(knob_radius * 0.40)
    pygame.draw.circle(surf, (8, 10, 12, 240), (bcx, bcy), socket_r)
    pygame.draw.circle(surf, (95, 105, 115, 180), (bcx, bcy), socket_r, width=2)

    return surf


def _render_joystick_balltop_surf(knob_radius: float, is_active: bool) -> pygame.Surface:
    """Gera a manopla esférica translúcida Sanwa LB-35 estilo Candy Cab."""
    pad = 12
    dim = int((knob_radius + pad) * 2)
    surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
    kcx = dim // 2
    kcy = dim // 2

    r, g, b = (225, 32, 45) if is_active else (135, 28, 38)
    alpha = 235 if is_active else 170

    # 1. Sombra esférica da manopla
    pygame.draw.circle(surf, (0, 0, 0, 75), (kcx + 2, kcy + 3), int(knob_radius))

    # 2. Corpo esférico translúcido rubi
    pygame.draw.circle(surf, (r, g, b, alpha), (kcx, kcy), int(knob_radius))

    # 3. Lábio de refração polida
    rim_col = (min(255, r + 55), min(255, g + 55), min(255, b + 55), 210)
    pygame.draw.circle(surf, rim_col, (kcx, kcy), int(knob_radius), width=2)

    # 4. Sombra 3D de relevo na parte inferior direita
    arc_rect = pygame.Rect(kcx - knob_radius, kcy - knob_radius, knob_radius * 2, knob_radius * 2)
    pygame.draw.arc(surf, (15, 18, 22, 190), arc_rect, 4.2, 5.8, width=3)

    # 5. Porca Interna de Latão Rosqueada (Visível dentro do acrílico translúcido)
    nut_r = int(knob_radius * 0.32)
    if is_active:
        pygame.draw.circle(surf, (255, 230, 140, 220), (kcx, kcy), nut_r)
        pygame.draw.circle(surf, (255, 255, 255, 240), (kcx, kcy), int(nut_r * 0.50))
    else:
        pygame.draw.circle(surf, (212, 175, 55, 185), (kcx, kcy), nut_r)
        pygame.draw.circle(surf, (35, 28, 18, 220), (kcx, kcy), int(nut_r * 0.50))
    pygame.draw.circle(surf, (180, 140, 45, 190), (kcx, kcy), nut_r, width=1)

    # 6. Reflexo Especular Suave em Camadas (Smooth Spherical Specular Glint)
    hl_x = kcx - int(knob_radius * 0.32)
    hl_y = kcy - int(knob_radius * 0.32)
    # Camada externa difusa
    pygame.draw.circle(surf, (255, 255, 255, 45 if not is_active else 65), (hl_x, hl_y), int(knob_radius * 0.38))
    # Camada intermediária
    pygame.draw.circle(surf, (255, 255, 255, 100 if not is_active else 140), (hl_x, hl_y), int(knob_radius * 0.22))
    # Ponto de brilho puro
    pygame.draw.circle(surf, (255, 255, 255, 230), (hl_x - 1, hl_y - 1), max(2, int(knob_radius * 0.08)))

    return surf


class TouchControls:
    """Controlador completo de interface de toque para o jogo."""
    def __init__(self):
        self.mode = TOUCH_MODE_AUTO
        self.has_detected_touch = False

        # Joystick virtual flutuante na metade esquerda da tela
        self.joystick = VirtualJoystick(base_x=160, base_y=570, radius=80, knob_radius=36)

        self.default_positions = {
            "attack": [1140, 580],
            "secondary": [1020, 520],
            "dash": [1160, 440]
        }
        self.button_scale = 1.0

        # Botão Ataque (Principal)
        self.btn_attack = TouchButton(
            cx=1140, cy=580, radius=50,
            label="ATK", sublabel="GOLPE",
            primary_color=(195, 32, 42) # Carmim Iai
        )

        # Botão Ação Secundária / Especial / Parry
        self.btn_secondary = TouchButton(
            cx=1020, cy=520, radius=42,
            label="ESP", sublabel="ESPECIAL",
            primary_color=(212, 145, 30) # Âmbar Dourado
        )

        # Botão Terceira Ação: Roll / Dash dedicado
        self.btn_dash = TouchButton(
            cx=1160, cy=440, radius=38,
            label="ROLL", sublabel="ESQUIVA",
            primary_color=(36, 74, 150) # Azul Noite
        )

        # Botão de Menu / Opções (Pausa)
        self.btn_menu = pygame.Rect(SCREEN_WIDTH - 130, 16, 110, 42)
        self.menu_just_pressed = False
        self.menu_finger_id: int | None = None

        # Botão Seleção de Guerreiros
        self.btn_select = pygame.Rect(25, 18, 170, 36)
        self.select_just_pressed = False
        self.select_finger_id: int | None = None

        # Mouse Desktop Simulation
        self._mouse_active_finger = -999

    def apply_layout(self, cfg: dict):
        """Aplica posições e escala customizadas salvas em controls_config.json."""
        if not cfg or not isinstance(cfg, dict):
            return
        self.button_scale = float(cfg.get("scale", 1.0))
        self.btn_attack.radius = 50 * self.button_scale
        self.btn_secondary.radius = 42 * self.button_scale
        self.btn_dash.radius = 38 * self.button_scale

        pos = cfg.get("positions", {})
        if "attack" in pos and len(pos["attack"]) == 2:
            self.btn_attack.cx, self.btn_attack.cy = float(pos["attack"][0]), float(pos["attack"][1])
        if "secondary" in pos and len(pos["secondary"]) == 2:
            self.btn_secondary.cx, self.btn_secondary.cy = float(pos["secondary"][0]), float(pos["secondary"][1])
        if "dash" in pos and len(pos["dash"]) == 2:
            self.btn_dash.cx, self.btn_dash.cy = float(pos["dash"][0]), float(pos["dash"][1])

    def get_layout_config(self) -> dict:
        """Retorna o dicionário de layout para persistência."""
        return {
            "scale": self.button_scale,
            "positions": {
                "attack": [int(self.btn_attack.cx), int(self.btn_attack.cy)],
                "secondary": [int(self.btn_secondary.cx), int(self.btn_secondary.cy)],
                "dash": [int(self.btn_dash.cx), int(self.btn_dash.cy)],
            }
        }

    def reset_to_default_layout(self):
        """Restaura as posições e escala padrão de fábrica."""
        self.button_scale = 1.0
        self.apply_layout({"scale": 1.0, "positions": self.default_positions})

    @property
    def is_visible(self) -> bool:
        if self.mode == TOUCH_MODE_ALWAYS:
            return True
        elif self.mode == TOUCH_MODE_OFF:
            return False
        return self.has_detected_touch

    def set_action_labels(self, label_atk: str, label_sec: str = "ESPECIAL", label_dash: str = "ESQUIVA"):
        """Atualiza dinamicamente os subtítulos dos botões de toque com as ações do personagem escolhido."""
        self.btn_attack.sublabel = label_atk[:8]
        self.btn_secondary.sublabel = label_sec[:8]
        self.btn_dash.sublabel = label_dash[:8]

    def reset_frame_triggers(self):
        """Reseta disparos pontuais (just_pressed) em cada iteração do game loop."""
        self.btn_attack.reset_frame_state()
        self.btn_secondary.reset_frame_state()
        self.btn_dash.reset_frame_state()
        self.menu_just_pressed = False
        self.select_just_pressed = False

    def handle_event(self, event: pygame.event.Event, scaler=None) -> bool:
        """
        Interpreta eventos nativos FINGER* do SDL e MOUSE* para desktop.
        Retorna True se o evento foi consumido pelos controles de toque.
        """
        # 1. Eventos Nativos de Toque (Multi-Touch real do celular)
        if event.type == pygame.FINGERDOWN:
            self.has_detected_touch = True
            fx, fy = event.x, event.y
            fid = event.finger_id
            if scaler:
                vx, vy = scaler.normalized_finger_to_virtual(fx, fy)
            else:
                vx, vy = fx * SCREEN_WIDTH, fy * SCREEN_HEIGHT

            # Verificar menu e seletores de topo
            if self.btn_menu.collidepoint(vx, vy):
                self.menu_just_pressed = True
                self.menu_finger_id = fid
                return True
            if self.btn_select.collidepoint(vx, vy):
                self.select_just_pressed = True
                self.select_finger_id = fid
                return True

            consumed = self.btn_attack.on_touch_down(fid, vx, vy)
            if not consumed:
                consumed = self.btn_secondary.on_touch_down(fid, vx, vy)
            if not consumed:
                consumed = self.btn_dash.on_touch_down(fid, vx, vy)
            if not consumed:
                consumed = self.joystick.on_touch_down(fid, vx, vy)
            return consumed

        elif event.type == pygame.FINGERMOTION:
            fx, fy = event.x, event.y
            fid = event.finger_id
            if scaler:
                vx, vy = scaler.normalized_finger_to_virtual(fx, fy)
            else:
                vx, vy = fx * SCREEN_WIDTH, fy * SCREEN_HEIGHT
            return self.joystick.on_touch_motion(fid, vx, vy)

        elif event.type == pygame.FINGERUP:
            fid = event.finger_id
            if self.menu_finger_id == fid:
                self.menu_finger_id = None
            if self.select_finger_id == fid:
                self.select_finger_id = None
            self.btn_attack.on_touch_up(fid)
            self.btn_secondary.on_touch_up(fid)
            self.btn_dash.on_touch_up(fid)
            self.joystick.on_touch_up(fid)
            return True

        # 2. Emulação via Mouse (para testes no macOS / Desktop)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if scaler:
                vx, vy = scaler.screen_to_virtual(mx, my)
            else:
                vx, vy = mx, my

            # Se os controles touch estão ativos ou visíveis, interceptar cliques neles
            if self.is_visible:
                if self.btn_menu.collidepoint(vx, vy):
                    self.menu_just_pressed = True
                    return True
                if self.btn_select.collidepoint(vx, vy):
                    self.select_just_pressed = True
                    return True
                if self.btn_attack.on_touch_down(self._mouse_active_finger, vx, vy):
                    return True
                if self.btn_secondary.on_touch_down(self._mouse_active_finger, vx, vy):
                    return True
                if self.btn_dash.on_touch_down(self._mouse_active_finger, vx, vy):
                    return True
                if self.joystick.on_touch_down(self._mouse_active_finger, vx, vy):
                    return True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_visible and self.joystick.is_active:
                mx, my = event.pos
                if scaler:
                    vx, vy = scaler.screen_to_virtual(mx, my)
                else:
                    vx, vy = mx, my
                return self.joystick.on_touch_motion(self._mouse_active_finger, vx, vy)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_visible:
                self.btn_attack.on_touch_up(self._mouse_active_finger)
                self.btn_secondary.on_touch_up(self._mouse_active_finger)
                self.btn_dash.on_touch_up(self._mouse_active_finger)
                self.joystick.on_touch_up(self._mouse_active_finger)

        return False

    def get_movement(self) -> tuple[float, float]:
        """Retorna o vetor de movimentação (dx, dy) do joystick virtual."""
        return self.joystick.dx, self.joystick.dy

    def is_attack_just_pressed(self) -> bool:
        return self.btn_attack.just_pressed

    def is_attack_held(self) -> bool:
        return self.btn_attack.is_down

    def is_secondary_just_pressed(self) -> bool:
        return self.btn_secondary.just_pressed

    def is_secondary_held(self) -> bool:
        return self.btn_secondary.is_down

    def is_secondary_just_released(self) -> bool:
        return self.btn_secondary.just_released

    def is_dash_just_pressed(self) -> bool:
        return self.btn_dash.just_pressed

    def is_dash_just_released(self) -> bool:
        return self.btn_dash.just_released

    def is_dash_held(self) -> bool:
        return self.btn_dash.is_down

    def is_menu_requested(self) -> bool:
        return self.menu_just_pressed

    def is_select_requested(self) -> bool:
        return self.select_just_pressed

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_small: pygame.font.Font):
        """Renderiza os botões e joystick virtuais com acabamento premium."""
        if not self.is_visible:
            return

        # Renderizar Joystick
        self.joystick.render(surface)

        # Renderizar Botões de Ação
        self.btn_attack.render(surface, font_large, font_small)
        self.btn_secondary.render(surface, font_large, font_small)
        self.btn_dash.render(surface, font_large, font_small)

        # Renderizar Botão de Menu Flutuante ([⚙ OPÇÕES])
        btn_surf = pygame.Surface((self.btn_menu.w, self.btn_menu.h), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (20, 26, 24, 205), btn_surf.get_rect(), border_radius=8)
        pygame.draw.rect(btn_surf, COLOR_GOLD, btn_surf.get_rect(), 1, border_radius=8)
        surface.blit(btn_surf, self.btn_menu.topleft)
        cfg_icon = font_small.render("⚙ OPÇÕES", True, COLOR_GOLD)
        surface.blit(cfg_icon, (self.btn_menu.centerx - cfg_icon.get_width() // 2, self.btn_menu.centery - cfg_icon.get_height() // 2))
