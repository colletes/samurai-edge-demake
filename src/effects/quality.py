"""
Qualidade dos efeitos visuais (6.5.6): alta (padrão) ou baixa.

A baixa corta o que mais custa por quadro sem mudar o jogo: menos partículas de ar, de terreno e de névoa, e sem
texturas de material nos voxels. Névoa que esconde lutadores (`FogVolume`), vento e iluminação continuam iguais, porque
afetam a luta. Guardada em `settings.json`, em `video.effects_quality`.
"""
from collections import deque
import json
import os

HIGH, LOW = "high", "low"
LEVELS = (HIGH, LOW)
_level = HIGH
_user_preferred_level = HIGH
_auto_adjust_enabled = True
_dt_history: deque[float] = deque(maxlen=60)
_low_fps_streak = 0
_high_fps_streak = 0
_governor_stepped_down = False
_game_boost_enabled: bool = False


def set_game_boost(enabled: bool):
    global _game_boost_enabled
    _game_boost_enabled = bool(enabled)
    if _game_boost_enabled:
        _apply_process_boost()


def is_game_boost_enabled() -> bool:
    return _game_boost_enabled


def _apply_process_boost():
    """Eleva a prioridade de processo / QoS para Game Mode no macOS / POSIX quando suportado."""
    try:
        import os
        if hasattr(os, "nice"):
            try:
                os.nice(-2)
            except Exception:
                pass
    except Exception:
        pass


def set_effects_quality(level: str):
    global _level, _user_preferred_level, _governor_stepped_down, _low_fps_streak, _high_fps_streak
    _level = level if level in LEVELS else HIGH
    _user_preferred_level = _level
    _governor_stepped_down = False
    _low_fps_streak = 0
    _high_fps_streak = 0


def get_effects_quality() -> str:
    return _level


def is_high() -> bool:
    return _level == HIGH


def scaled(count: int, minimum: int = 1) -> int:
    """Quantidade de partículas na qualidade atual: com Game Boost ativo usa um quarto; baixa usa um terço."""
    if _game_boost_enabled:
        return max(minimum, int(count / 4))
    return count if _level == HIGH else max(minimum, int(count / 3))


def set_auto_adjust(enabled: bool):
    """Ativa ou desativa o governador automático de FPS."""
    global _auto_adjust_enabled, _level, _governor_stepped_down
    _auto_adjust_enabled = bool(enabled)
    if not _auto_adjust_enabled and _governor_stepped_down:
        _level = _user_preferred_level
        _governor_stepped_down = False


def get_auto_adjust() -> bool:
    return _auto_adjust_enabled


def is_governor_stepped_down() -> bool:
    """Retorna True se o governador reduziu temporariamente a qualidade por queda de FPS."""
    return _governor_stepped_down


def get_rolling_fps() -> float:
    """Retorna a média móvel de FPS dos últimos até 60 frames."""
    if not _dt_history:
        return 60.0
    avg_dt = sum(_dt_history) / len(_dt_history)
    return (1.0 / avg_dt) if avg_dt > 1e-6 else 60.0


def reset_fps_governor():
    """Limpa o histórico de frame-time do governador."""
    global _low_fps_streak, _high_fps_streak, _governor_stepped_down, _level
    _dt_history.clear()
    _low_fps_streak = 0
    _high_fps_streak = 0
    if _governor_stepped_down:
        _level = _user_preferred_level
        _governor_stepped_down = False


def update_fps_governor(dt: float) -> str:
    """
    Alimenta o governador automático com o `dt` real do frame (em segundos).
    Se o FPS médio cair abaixo de 48 FPS sustentado por 45 frames, reduz de HIGH para LOW.
    Se o FPS médio subir acima de 57 FPS por 150 frames e a preferência do usuário for HIGH, restaura HIGH.
    """
    global _level, _low_fps_streak, _high_fps_streak, _governor_stepped_down
    if dt <= 0.0 or dt > 0.5:
        return _level
    _dt_history.append(dt)
    if not _auto_adjust_enabled or len(_dt_history) < 15:
        return _level

    fps = get_rolling_fps()
    if _level == HIGH and fps < 48.0:
        _low_fps_streak += 1
        _high_fps_streak = 0
        if _low_fps_streak >= 45:
            _level = LOW
            _governor_stepped_down = True
            _low_fps_streak = 0
    elif _governor_stepped_down and _user_preferred_level == HIGH and fps >= 57.0:
        _high_fps_streak += 1
        _low_fps_streak = 0
        if _high_fps_streak >= 150:
            _level = HIGH
            _governor_stepped_down = False
            _high_fps_streak = 0
    else:
        _low_fps_streak = max(0, _low_fps_streak - 1)
        _high_fps_streak = max(0, _high_fps_streak - 1)
    return _level


def load_effects_quality(settings_path: str):
    """Aplica `video.effects_quality` e `video.game_boost` do settings.json; sem o arquivo ou a chave fica "high"."""
    try:
        with open(settings_path, encoding="utf-8") as f:
            video = json.load(f).get("video", {})
            set_effects_quality(video.get("effects_quality", HIGH))
            if "auto_fps_governor" in video:
                set_auto_adjust(bool(video.get("auto_fps_governor", True)))
            if "game_boost" in video:
                set_game_boost(bool(video.get("game_boost", False)))
    except (OSError, ValueError, AttributeError):
        set_effects_quality(HIGH)


def save_video_setting(settings_path: str, key: str, value: str) -> bool:
    """Grava uma chave de `video` no settings.json sem mexer no resto do arquivo."""
    try:
        try:
            with open(settings_path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            data = {}
        if not isinstance(data, dict):
            data = {}
        data.setdefault("video", {})[key] = value
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except OSError:
        return False


SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "settings.json")

