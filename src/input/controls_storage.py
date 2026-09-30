"""
Módulo de persistência e integridade das preferências de controles.
Salva e recupera as configurações de Teclado, Gamepads e Touch em controls_config.json.
Previne atribuição de comandos espúrios/aleatórios ao plugar novos controles.
"""
import os
import json
import pygame
from src.config import BASE_DIR, DEFAULT_CONTROLS

CONFIG_FILENAME = "controls_config.json"
CONFIG_PATH = os.path.join(BASE_DIR, CONFIG_FILENAME)


def get_default_config() -> dict:
    """Retorna a estrutura de configuração padrão de fábrica."""
    return {
        "version": "1.4.0",
        "keyboard": {k: int(v) for k, v in DEFAULT_CONTROLS.items()},
        "controllers": {
            "P1": {},
            "P2": {},
        },
        "touch_mode": "auto",
        "audio": {
            "master": 1.0,
            "sfx": 0.85,
            "bgm": 0.65,
        }
    }


def load_controls_config() -> dict:
    """
    Carrega as preferências salvas de controls_config.json.
    Retorna estrutura padrão segura se o arquivo não existir ou for inválido.
    """
    if not os.path.exists(CONFIG_PATH):
        return get_default_config()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return get_default_config()

        default_cfg = get_default_config()
        if "keyboard" not in data or not isinstance(data["keyboard"], dict):
            data["keyboard"] = default_cfg["keyboard"]
        else:
            for k, v in default_cfg["keyboard"].items():
                if k not in data["keyboard"]:
                    data["keyboard"][k] = v

        if "controllers" not in data or not isinstance(data["controllers"], dict):
            data["controllers"] = default_cfg["controllers"]
        if "touch_mode" not in data:
            data["touch_mode"] = default_cfg["touch_mode"]
        if "audio" not in data or not isinstance(data["audio"], dict):
            data["audio"] = default_cfg["audio"]
        else:
            for k, v in default_cfg["audio"].items():
                if k not in data["audio"]:
                    data["audio"][k] = v

        return data
    except Exception as e:
        print(f"Aviso: Erro ao ler {CONFIG_PATH}, usando padrões: {e}")
        return get_default_config()


def save_controls_config(keyboard_controls: dict, controller_mgr=None, touch_mode: str = "auto", audio_cfg: dict = None) -> bool:
    """
    Persiste as configurações de teclado, gamepads, touch e volumes de áudio em controls_config.json.
    """
    try:
        default_cfg = get_default_config()

        audio_section = audio_cfg
        if audio_section is None and "audio" in keyboard_controls and isinstance(keyboard_controls["audio"], dict):
            audio_section = keyboard_controls["audio"]

        if audio_section is None:
            audio_section = default_cfg["audio"]
        else:
            merged_audio = dict(default_cfg["audio"])
            merged_audio.update(audio_section)
            audio_section = merged_audio

        keyboard_section = {}
        for k, v in keyboard_controls.items():
            if k == "audio":
                continue
            try:
                keyboard_section[k] = int(v)
            except (ValueError, TypeError):
                pass

        cfg = {
            "version": "1.4.0",
            "keyboard": keyboard_section,
            "controllers": {
                "P1": {},
                "P2": {},
            },
            "touch_mode": touch_mode or "auto",
            "audio": audio_section,
        }

        if controller_mgr:
            for p_idx, p_key in ((0, "P1"), (1, "P2")):
                ctrl = controller_mgr.get_controller_for_player(p_idx)
                if ctrl and hasattr(ctrl, "custom_mappings"):
                    p_map = {}
                    for act, btns in ctrl.custom_mappings.items():
                        if isinstance(btns, list):
                            p_map[act] = [int(b) for b in btns]
                        elif isinstance(btns, int):
                            p_map[act] = [int(btns)]
                    cfg["controllers"][p_key] = p_map

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar controles em {CONFIG_PATH}: {e}")
        return False

