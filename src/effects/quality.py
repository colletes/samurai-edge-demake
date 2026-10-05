"""
Qualidade dos efeitos visuais (6.5.6): alta (padrão) ou baixa.

A baixa corta o que mais custa por quadro sem mudar o jogo: menos partículas de ar, de terreno e de névoa, e sem
texturas de material nos voxels. Névoa que esconde lutadores (`FogVolume`), vento e iluminação continuam iguais, porque
afetam a luta. Guardada em `settings.json`, em `video.effects_quality`.
"""
import json
import os

HIGH, LOW = "high", "low"
LEVELS = (HIGH, LOW)
_level = HIGH


def set_effects_quality(level: str):
    global _level
    _level = level if level in LEVELS else HIGH


def get_effects_quality() -> str:
    return _level


def is_high() -> bool:
    return _level == HIGH


def scaled(count: int, minimum: int = 1) -> int:
    """Quantidade de partículas na qualidade atual: a baixa usa um terço."""
    return count if _level == HIGH else max(minimum, int(count / 3))


def load_effects_quality(settings_path: str):
    """Aplica `video.effects_quality` do settings.json; sem o arquivo ou a chave fica "high"."""
    try:
        with open(settings_path, encoding="utf-8") as f:
            set_effects_quality(json.load(f).get("video", {}).get("effects_quality", HIGH))
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
