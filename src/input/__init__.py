"""
Módulo de entrada para Samurai Edge Demake.
Suporte unificado para Teclado, Controles (Xbox, DualShock, DualSense, Genérico) e Touchscreen.
"""
from src.input.controller_manager import ControllerManager, get_controller_manager
from src.input.touch_controls import TouchControls
from src.input.display_scaler import DisplayScaler

__all__ = ["ControllerManager", "get_controller_manager", "TouchControls", "DisplayScaler"]
