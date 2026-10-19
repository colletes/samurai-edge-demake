"""
Módulo de Detecção de Dispositivo e Layout de Interface (Mobile Phone vs Tablet / Desktop).
Permite adaptar telas e controles para smartphones enquanto preserva a interface clássica em tablets e PCs.
"""
import os
import sys
import pygame

_UI_MODE_OVERRIDE = None

def get_saved_ui_mode() -> str:
    """Retorna o modo configurado: 'auto', 'mobile' ou 'classic'."""
    global _UI_MODE_OVERRIDE
    if _UI_MODE_OVERRIDE is not None:
        return _UI_MODE_OVERRIDE
    from src.input.controls_storage import load_controls_config
    cfg = load_controls_config()
    return cfg.get("ui_mode", "auto")

def set_ui_mode(mode: str):
    """Define o modo de interface ('auto', 'mobile', 'classic')."""
    global _UI_MODE_OVERRIDE
    _UI_MODE_OVERRIDE = mode
    from src.input.controls_storage import load_controls_config, save_controls_config
    cfg = load_controls_config()
    cfg["ui_mode"] = mode
    save_controls_config(
        cfg.get("keyboard", {}),
        touch_mode=cfg.get("touch_mode", "auto"),
        audio_cfg=cfg.get("audio", {}),
        ai_difficulty=cfg.get("ai_difficulty", "normal"),
        ui_mode=mode,
        touch_controls_cfg=cfg.get("touch_controls", {})
    )

def is_mobile_device() -> bool:
    """
    Determina se a interface deve ser adaptada para smartphone (Mobile Phone).
    iPhones e smartphones usam interface mobile simplificada com cards ovais generosos.
    iPads, tablets e desktops usam a interface clássica completa.
    """
    mode = get_saved_ui_mode()
    if mode == "mobile":
        return True
    if mode == "classic":
        return False

    # Detecção nativa em runtime no iOS via C/ObjC exportado no main.m
    try:
        import ctypes
        lib = ctypes.CDLL(None)
        if hasattr(lib, "is_iphone_device"):
            lib.is_iphone_device.argtypes = []
            lib.is_iphone_device.restype = ctypes.c_int
            res = lib.is_iphone_device()
            if res == 1:
                return True
            elif res == 0:
                return False
    except Exception:
        pass

    # Heurística por aspect ratio e plataforma
    is_ios = os.environ.get("KIVY_BUILD") == "ios" or os.environ.get("PYGAME_IOS") == "1"
    is_android = "ANDROID_ARGUMENT" in os.environ

    if is_ios or is_android:
        # Smartphones modernos possuem aspect ratio largo (18:9, 19.5:9, 20:9 -> ratio >= 1.85)
        # iPads possuem 4:3 (~1.33) ou 16:10 (~1.6)
        screen = pygame.display.get_surface()
        if screen:
            w, h = screen.get_size()
            if h > 0 and (max(w, h) / float(min(w, h))) >= 1.80:
                return True
        return True

    return False
