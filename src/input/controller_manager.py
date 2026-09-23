"""
Gerenciador de Controles (Gamepads) para Samurai Edge Demake.
Reconhece modelos específicos:
- Xbox (360, One, Series X/S, XInput)
- PlayStation (DualShock 4, DualSense PS5, Sony)
- Nintendo (Switch Pro Controller, Joy-Con)
- Genérico (DirectInput, 8BitDo, USB Arcade Stick, etc.)

Fornece mapeamento ergonômico, glifos/ícones visuais apropriados para HUD e suporte a Rumble.
"""
import math
import pygame

# Tipos de Controle
CONTROLLER_TYPE_XBOX = "xbox"
CONTROLLER_TYPE_DUALSHOCK = "dualshock"
CONTROLLER_TYPE_DUALSENSE = "dualsense"
CONTROLLER_TYPE_PLAYSTATION = "playstation"
CONTROLLER_TYPE_NINTENDO = "nintendo"
CONTROLLER_TYPE_GENERIC = "generic"

# Identificadores de Ações
ACTION_ATTACK = "attack"
ACTION_DASH = "dash"
ACTION_PARRY = "parry"
ACTION_SPECIAL = "special"
ACTION_MENU = "menu"
ACTION_RESTART = "restart"
ACTION_CONFIRM = "confirm"
ACTION_CANCEL = "cancel"

# Constantes de Botões Padrão SDL GameController
BTN_A = 0               # Xbox: A | PS: ✕ Cross | Switch: B | Genérico: 1
BTN_B = 1               # Xbox: B | PS: ○ Circle | Switch: A | Genérico: 2
BTN_X = 2               # Xbox: X | PS: ▢ Square | Switch: Y | Genérico: 3
BTN_Y = 3               # Xbox: Y | PS: △ Triangle | Switch: X | Genérico: 4
BTN_BACK = 4            # Xbox: View / Back | PS: Share / Touchpad | Genérico: Select
BTN_GUIDE = 5           # Xbox / PS Home
BTN_START = 6           # Xbox: Menu / Start | PS: Options | Genérico: Start
BTN_LEFTSTICK = 7
BTN_RIGHTSTICK = 8
BTN_LEFTSHOULDER = 9    # LB / L1
BTN_RIGHTSHOULDER = 10  # RB / R1
BTN_DPAD_UP = 11
BTN_DPAD_DOWN = 12
BTN_DPAD_LEFT = 13
BTN_DPAD_RIGHT = 14

def detect_controller_type(name: str, guid: str = "") -> str:
    """
    Classifica o tipo do controle a partir do nome anunciado pelo driver e/ou GUID SDL.
    """
    name_lower = (name or "").lower()
    guid_lower = (guid or "").lower()

    # 1. PlayStation (DualSense PS5 vs DualShock 4 PS4 vs Sony genérico)
    if "dualsense" in name_lower or "ps5" in name_lower:
        return CONTROLLER_TYPE_DUALSENSE
    if "dualshock" in name_lower or "ps4" in name_lower:
        return CONTROLLER_TYPE_DUALSHOCK
    if "playstation" in name_lower or "sony" in name_lower or "054c" in guid_lower or "4c05" in guid_lower:
        if "5" in name_lower:
            return CONTROLLER_TYPE_DUALSENSE
        return CONTROLLER_TYPE_DUALSHOCK

    # 2. Xbox (360, One, Series, Microsoft XInput)
    if (
        "xbox" in name_lower
        or "x-box" in name_lower
        or "microsoft" in name_lower
        or "xinput" in name_lower
        or "045e" in guid_lower
        or "5e04" in guid_lower
    ):
        return CONTROLLER_TYPE_XBOX

    # 3. Nintendo Switch
    if (
        "switch" in name_lower
        or "pro controller" in name_lower
        or "joy-con" in name_lower
        or "nintendo" in name_lower
        or "057e" in guid_lower
        or "7e05" in guid_lower
    ):
        return CONTROLLER_TYPE_NINTENDO

    # 4. Genérico
    return CONTROLLER_TYPE_GENERIC


class ControllerDevice:
    """Representa uma instância ativa de controle conectado."""
    def __init__(self, joystick: pygame.joystick.Joystick):
        self.joystick = joystick
        self.instance_id = joystick.get_instance_id()
        self.name = joystick.get_name()
        try:
            self.guid = joystick.get_guid()
        except Exception:
            self.guid = ""
        self.controller_type = detect_controller_type(self.name, self.guid)
        self.deadzone = 0.22

    @property
    def friendly_name(self) -> str:
        if self.controller_type == CONTROLLER_TYPE_DUALSENSE:
            return "PlayStation DualSense (PS5)"
        elif self.controller_type == CONTROLLER_TYPE_DUALSHOCK:
            return "PlayStation DualShock 4 (PS4)"
        elif self.controller_type == CONTROLLER_TYPE_XBOX:
            return "Xbox Wireless / One Controller"
        elif self.controller_type == CONTROLLER_TYPE_NINTENDO:
            return "Nintendo Switch Controller"
        return f"Controle Genérico ({self.name[:16]})"

    def get_button_glyph(self, action: str) -> str:
        """Retorna o glifo visual correspondente à ação de acordo com a fabricante."""
        if self.controller_type in (CONTROLLER_TYPE_DUALSHOCK, CONTROLLER_TYPE_DUALSENSE):
            glyphs = {
                ACTION_ATTACK: "✕",
                ACTION_CONFIRM: "✕",
                ACTION_DASH: "○",
                ACTION_CANCEL: "○",
                ACTION_PARRY: "○",
                ACTION_SPECIAL: "▢",
                ACTION_MENU: "Options",
                ACTION_RESTART: "Touchpad",
            }
        elif self.controller_type == CONTROLLER_TYPE_XBOX:
            glyphs = {
                ACTION_ATTACK: "A",
                ACTION_CONFIRM: "A",
                ACTION_DASH: "B",
                ACTION_CANCEL: "B",
                ACTION_PARRY: "B",
                ACTION_SPECIAL: "X",
                ACTION_MENU: "Menu",
                ACTION_RESTART: "View",
            }
        elif self.controller_type == CONTROLLER_TYPE_NINTENDO:
            glyphs = {
                ACTION_ATTACK: "B",
                ACTION_CONFIRM: "A",
                ACTION_DASH: "A",
                ACTION_CANCEL: "B",
                ACTION_PARRY: "A",
                ACTION_SPECIAL: "Y",
                ACTION_MENU: "+",
                ACTION_RESTART: "-",
            }
        else: # Genérico
            glyphs = {
                ACTION_ATTACK: "1",
                ACTION_CONFIRM: "1",
                ACTION_DASH: "2",
                ACTION_CANCEL: "2",
                ACTION_PARRY: "2",
                ACTION_SPECIAL: "3",
                ACTION_MENU: "Start",
                ACTION_RESTART: "Select",
            }
        return glyphs.get(action, "?")

    def get_movement(self) -> tuple[float, float]:
        """
        Retorna o vetor de movimentação normalizado (dx, dy) combinando analógico e D-pad.
        """
        dx, dy = 0.0, 0.0

        # 1. Leitura do Analógico Esquerdo (Eixos 0 e 1)
        try:
            if self.joystick.get_numaxes() >= 2:
                raw_x = self.joystick.get_axis(0)
                raw_y = self.joystick.get_axis(1)
                mag = math.hypot(raw_x, raw_y)
                if mag > self.deadzone:
                    # Normalizar além da deadzone
                    norm = min(1.0, (mag - self.deadzone) / (1.0 - self.deadzone))
                    dx = (raw_x / mag) * norm
                    dy = (raw_y / mag) * norm
        except Exception:
            pass

        # 2. Leitura do D-Pad (Hat 0 ou botões virtuais 11-14)
        try:
            if self.joystick.get_numhats() > 0:
                hx, hy = self.joystick.get_hat(0)
                if hx != 0 or hy != 0:
                    dx = float(hx)
                    dy = float(-hy) # Inverter eixo Y do hat SDL
        except Exception:
            pass

        # Botões de D-Pad em controladores SDL
        try:
            num_btn = self.joystick.get_numbuttons()
            if num_btn > BTN_DPAD_RIGHT:
                if self.joystick.get_button(BTN_DPAD_LEFT):
                    dx = -1.0
                elif self.joystick.get_button(BTN_DPAD_RIGHT):
                    dx = 1.0
                if self.joystick.get_button(BTN_DPAD_UP):
                    dy = -1.0
                elif self.joystick.get_button(BTN_DPAD_DOWN):
                    dy = 1.0
        except Exception:
            pass

        # Limitar magnitude máxima a 1.0
        dist = math.hypot(dx, dy)
        if dist > 1.0:
            dx /= dist
            dy /= dist

        return dx, dy

    def is_action_pressed(self, button_index: int, action: str) -> bool:
        """Verifica se o botão que acabou de ser pressionado corresponde à ação."""
        if action in (ACTION_ATTACK, ACTION_CONFIRM):
            return button_index == BTN_A or button_index == BTN_RIGHTSHOULDER
        elif action in (ACTION_DASH, ACTION_PARRY, ACTION_CANCEL):
            return button_index == BTN_B or button_index == BTN_LEFTSHOULDER
        elif action == ACTION_SPECIAL:
            return button_index == BTN_X
        elif action == ACTION_MENU:
            return button_index == BTN_START
        elif action == ACTION_RESTART:
            return button_index == BTN_BACK
        return False

    def is_action_down(self, action: str) -> bool:
        """Verifica se o botão associado à ação está sendo mantido pressionado (útil para recarga do Rifleman)."""
        try:
            num_b = self.joystick.get_numbuttons()
            if action in (ACTION_ATTACK, ACTION_CONFIRM):
                return bool(self.joystick.get_button(BTN_A)) or (num_b > BTN_RIGHTSHOULDER and bool(self.joystick.get_button(BTN_RIGHTSHOULDER)))
            elif action in (ACTION_DASH, ACTION_PARRY, ACTION_CANCEL):
                return bool(self.joystick.get_button(BTN_B)) or (num_b > BTN_LEFTSHOULDER and bool(self.joystick.get_button(BTN_LEFTSHOULDER)))
            elif action == ACTION_SPECIAL:
                return num_b > BTN_X and bool(self.joystick.get_button(BTN_X))
            elif action == ACTION_MENU:
                return num_b > BTN_START and bool(self.joystick.get_button(BTN_START))
            elif action == ACTION_RESTART:
                return num_b > BTN_BACK and bool(self.joystick.get_button(BTN_BACK))
        except Exception:
            pass
        return False

    def rumble(self, low_freq: float = 0.5, high_freq: float = 0.8, duration_ms: int = 150):
        """Ativa o feedback tátil de vibração no controle (se suportado pelo hardware)."""
        try:
            if hasattr(self.joystick, "rumble"):
                self.joystick.rumble(low_freq, high_freq, duration_ms)
        except Exception:
            pass


class ControllerManager:
    """Gerencia a detecção, hotplug e eventos de todos os controles conectados."""
    def __init__(self):
        self.controllers: dict[int, ControllerDevice] = {} # instance_id -> ControllerDevice
        self.player_map: list[int | None] = [None, None]   # [P1_instance_id, P2_instance_id]
        self._init_joysticks()

    def _init_joysticks(self):
        if not pygame.joystick.get_init():
            try:
                pygame.joystick.init()
            except Exception:
                return

        for i in range(pygame.joystick.get_count()):
            self._add_device(i)

    def _add_device(self, device_index: int):
        try:
            joy = pygame.joystick.Joystick(device_index)
            joy.init()
            inst_id = joy.get_instance_id()
            dev = ControllerDevice(joy)
            self.controllers[inst_id] = dev

            # Atribuição automática a P1 ou P2
            if self.player_map[0] is None:
                self.player_map[0] = inst_id
            elif self.player_map[1] is None:
                self.player_map[1] = inst_id
        except Exception:
            pass

    def _remove_device(self, instance_id: int):
        if instance_id in self.controllers:
            del self.controllers[instance_id]
        if self.player_map[0] == instance_id:
            self.player_map[0] = None
        if self.player_map[1] == instance_id:
            self.player_map[1] = None

        # Reorganizar P1/P2
        remaining = list(self.controllers.keys())
        if self.player_map[0] is None and len(remaining) > 0:
            self.player_map[0] = remaining[0]
        if self.player_map[1] is None and len(remaining) > 1:
            self.player_map[1] = remaining[1]

    def handle_event(self, event: pygame.event.Event):
        """Atualiza a lista de controles em caso de plug/unplug."""
        if event.type == pygame.JOYDEVICEADDED:
            self._add_device(event.device_index)
        elif event.type == pygame.JOYDEVICEREMOVED:
            self._remove_device(event.instance_id)

    def get_controller_for_player(self, player_idx: int) -> ControllerDevice | None:
        if 0 <= player_idx < len(self.player_map):
            inst_id = self.player_map[player_idx]
            if inst_id is not None and inst_id in self.controllers:
                return self.controllers[inst_id]
        return None

    def has_controller(self, player_idx: int = 0) -> bool:
        return self.get_controller_for_player(player_idx) is not None

    def get_movement(self, player_idx: int = 0) -> tuple[float, float]:
        ctrl = self.get_controller_for_player(player_idx)
        if ctrl:
            return ctrl.get_movement()
        return 0.0, 0.0

    def is_action_down(self, player_idx: int, action: str) -> bool:
        ctrl = self.get_controller_for_player(player_idx)
        if ctrl:
            return ctrl.is_action_down(action)
        return False

    def is_event_action(self, event: pygame.event.Event, player_idx: int, action: str) -> bool:
        """Verifica se o evento JOYBUTTONDOWN atual corresponde à ação para o jogador especificado."""
        if event.type != pygame.JOYBUTTONDOWN:
            return False
        ctrl = self.get_controller_for_player(player_idx)
        if not ctrl:
            return False
        if event.instance_id != ctrl.instance_id:
            return False
        return ctrl.is_action_pressed(event.button, action)

    def rumble_player(self, player_idx: int, low_freq: float = 0.5, high_freq: float = 0.8, duration_ms: int = 150):
        ctrl = self.get_controller_for_player(player_idx)
        if ctrl:
            ctrl.rumble(low_freq, high_freq, duration_ms)

    def get_badge_text(self, player_idx: int = 0) -> str:
        ctrl = self.get_controller_for_player(player_idx)
        if not ctrl:
            return ""
        type_str = ctrl.controller_type.upper()
        if ctrl.controller_type == CONTROLLER_TYPE_DUALSENSE:
            return "[🎮 DualSense PS5]"
        elif ctrl.controller_type == CONTROLLER_TYPE_DUALSHOCK:
            return "[🎮 DualShock 4 PS4]"
        elif ctrl.controller_type == CONTROLLER_TYPE_XBOX:
            return "[🎮 Xbox Controller]"
        elif ctrl.controller_type == CONTROLLER_TYPE_NINTENDO:
            return "[🎮 Switch Pro]"
        return f"[🎮 Genérico: {ctrl.name[:12]}]"

    def get_prompts_summary(self, player_idx: int = 0) -> str:
        ctrl = self.get_controller_for_player(player_idx)
        if not ctrl:
            return ""
        btn_atk = ctrl.get_button_glyph(ACTION_ATTACK)
        btn_dash = ctrl.get_button_glyph(ACTION_DASH)
        return f"[{btn_atk}] Ataque  [{btn_dash}] Especial / Dash"


_GLOBAL_CONTROLLER_MGR: ControllerManager | None = None

def get_controller_manager() -> ControllerManager:
    global _GLOBAL_CONTROLLER_MGR
    if _GLOBAL_CONTROLLER_MGR is None:
        _GLOBAL_CONTROLLER_MGR = ControllerManager()
    return _GLOBAL_CONTROLLER_MGR
