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

    def contains(self, vx: float, vy: float) -> bool:
        """Determina se uma coordenada virtual cai na zona de ativação do joystick (quadrante inferior esquerdo)."""
        return vx <= (SCREEN_WIDTH * 0.45) and vy >= (SCREEN_HEIGHT * 0.40)

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
        # Superfície com suporte a canal alfa
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Base / Anel Externo
        base_alpha = 140 if self.is_active else 85
        pygame.draw.circle(overlay, (20, 26, 24, base_alpha), (int(self.center_x), int(self.center_y)), int(self.radius))
        pygame.draw.circle(overlay, (212, 175, 55, base_alpha + 60), (int(self.center_x), int(self.center_y)), int(self.radius), 2)
        pygame.draw.circle(overlay, (120, 140, 130, base_alpha), (int(self.center_x), int(self.center_y)), int(self.radius * 0.4), 1)

        # Knob / Manopla de Toque
        knob_alpha = 220 if self.is_active else 120
        knob_color = (195, 32, 42, knob_alpha) if self.is_active else (55, 68, 62, knob_alpha)
        pygame.draw.circle(overlay, knob_color, (int(self.knob_x), int(self.knob_y)), int(self.knob_radius))
        pygame.draw.circle(overlay, (255, 230, 140, knob_alpha), (int(self.knob_x), int(self.knob_y)), int(self.knob_radius), 2)
        # Ponto central dourado
        pygame.draw.circle(overlay, (255, 215, 0, knob_alpha), (int(self.knob_x), int(self.knob_y)), 6)

        surface.blit(overlay, (0, 0))


class TouchButton:
    """Botão circular tátil com detecção de toque único e toque contínuo (hold)."""
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
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = 230 if self.is_down else 130

        # Cor de preenchimento
        r, g, b = self.primary_color
        fill_color = (min(255, r + 40), min(255, g + 40), min(255, b + 40), alpha) if self.is_down else (r, g, b, alpha)

        # Círculo externo
        pygame.draw.circle(overlay, fill_color, (int(self.cx), int(self.cy)), int(self.radius))
        border_col = COLOR_GOLD if self.is_down else (200, 205, 210, alpha + 40)
        pygame.draw.circle(overlay, border_col, (int(self.cx), int(self.cy)), int(self.radius), 3 if self.is_down else 2)

        # Anel de respiro interno
        pygame.draw.circle(overlay, (255, 255, 255, 60), (int(self.cx), int(self.cy)), int(self.radius - 5), 1)

        surface.blit(overlay, (0, 0))

        # Texto do Botão
        lbl_surf = font_large.render(self.label, True, COLOR_WHITE)
        surface.blit(lbl_surf, (self.cx - lbl_surf.get_width() // 2, self.cy - lbl_surf.get_height() // 2 - (6 if self.sublabel else 0)))

        if self.sublabel:
            sub_surf = font_small.render(self.sublabel, True, (240, 220, 160))
            surface.blit(sub_surf, (self.cx - sub_surf.get_width() // 2, self.cy + 12))


class TouchControls:
    """Controlador completo de interface de toque para o jogo."""
    def __init__(self):
        self.mode = TOUCH_MODE_AUTO
        self.has_detected_touch = False

        # Joystick virtual no canto inferior esquerdo
        self.joystick = VirtualJoystick(base_x=160, base_y=570, radius=80, knob_radius=36)

        # Botão Ataque (Principal) no canto inferior direito
        self.btn_attack = TouchButton(
            cx=1140, cy=565, radius=52,
            label="ATK", sublabel="GOLPE",
            primary_color=(195, 32, 42) # Carmim Iai
        )

        # Botão Ação Secundária (Dash / Parry / Recarga)
        self.btn_dash = TouchButton(
            cx=1005, cy=615, radius=42,
            label="DASH", sublabel="DEFESA",
            primary_color=(36, 74, 150) # Azul Parry / Vento
        )

        # Botão de Menu / Configurações (Pausa)
        self.btn_menu = pygame.Rect(SCREEN_WIDTH - 85, 18, 65, 36)
        self.menu_just_pressed = False
        self.menu_finger_id: int | None = None

        # Botão Seleção de Guerreiros
        self.btn_select = pygame.Rect(25, 18, 170, 36)
        self.select_just_pressed = False
        self.select_finger_id: int | None = None

        # Mouse Desktop Simulation
        self._mouse_active_finger = -999

    @property
    def is_visible(self) -> bool:
        if self.mode == TOUCH_MODE_ALWAYS:
            return True
        elif self.mode == TOUCH_MODE_OFF:
            return False
        return self.has_detected_touch

    def set_action_labels(self, label_atk: str, label_dash: str):
        """Atualiza dinamicamente os subtítulos dos botões de toque com as ações do personagem escolhido."""
        self.btn_attack.sublabel = label_atk[:8]
        self.btn_dash.sublabel = label_dash[:8]

    def reset_frame_triggers(self):
        """Reseta disparos pontuais (just_pressed) em cada iteração do game loop."""
        self.btn_attack.reset_frame_state()
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
        self.btn_dash.render(surface, font_large, font_small)

        # Renderizar Botão de Menu Flutuante (⚙️)
        btn_surf = pygame.Surface((self.btn_menu.w, self.btn_menu.h), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (25, 32, 28, 180), btn_surf.get_rect(), border_radius=6)
        pygame.draw.rect(btn_surf, COLOR_GOLD, btn_surf.get_rect(), 1, border_radius=6)
        surface.blit(btn_surf, self.btn_menu.topleft)
        cfg_icon = font_small.render("⚙ ESC", True, COLOR_GOLD)
        surface.blit(cfg_icon, (self.btn_menu.centerx - cfg_icon.get_width() // 2, self.btn_menu.centery - cfg_icon.get_height() // 2))
