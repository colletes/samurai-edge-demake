"""
Entregável 8.1.5: persistência do Arcade em arcade_save.json (recordes, melhores tempos e jornada em andamento).
Leitura tolerante (arquivo ausente, JSON quebrado ou versão desconhecida viram dados vazios) e escrita atômica.
"""
import json
import os
import tempfile
import time

SAVE_VERSION = 1
MAX_HIGH_SCORES = 10
SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "arcade_save.json")


def empty_data() -> dict:
    return {"version": SAVE_VERSION, "high_scores": [], "best_clear_time": {}, "clears": {}, "current_run": None}


def load(path: str = SAVE_PATH) -> dict:
    for attempt in range(3):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or data.get("version") != SAVE_VERSION:
                return empty_data()
            out = empty_data()
            scores = data.get("high_scores")
            if isinstance(scores, list):
                out["high_scores"] = [e for e in scores if isinstance(e, dict) and isinstance(e.get("score"), int)]
            for key in ("best_clear_time", "clears"):
                if isinstance(data.get(key), dict):
                    out[key] = data[key]
            if isinstance(data.get("current_run"), dict):
                out["current_run"] = data["current_run"]
            return out
        except (OSError, ValueError):
            if attempt < 2 and os.path.exists(path):
                time.sleep(0.04)
                continue
            return empty_data()
    return empty_data()


def save(data: dict, path: str = SAVE_PATH) -> bool:
    """Grava num arquivo temporário e troca por `os.replace`; tolerante a bloqueios do iCloud Drive."""
    tmp = None
    try:
        directory = os.path.dirname(path) or "."
        fd, tmp = tempfile.mkstemp(dir=directory, prefix=".arcade_save_", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Tenta substituir atomicamente; se bloqueado temporariamente pelo iCloud (bird/fileproviderd), tenta com backoff
        for attempt in range(3):
            try:
                os.replace(tmp, path)
                tmp = None
                return True
            except OSError:
                if attempt < 2:
                    time.sleep(0.04)
                else:
                    break

        # Fallback se os.replace for bloqueado pelo sistema de arquivos em nuvem
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False
    except OSError:
        return False
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _rank_key(entry: dict):
    # Mais pontos primeiro; empate: menos Continues, depois menor tempo
    return (-entry["score"], entry.get("continues", 0), entry.get("time", 0.0))


def add_high_score(data: dict, run, now: float | None = None) -> int | None:
    """Registra a jornada concluída; devolve a posição (1 a 10) na tabela ou None se não entrou."""
    entry = {"score": int(run.score), "char": run.player_char, "difficulty_start": run.difficulty_start,
             "difficulty_end": run.difficulty_level, "continues": run.continues, "time": round(run.elapsed, 2),
             "date": time.strftime("%Y-%m-%d", time.localtime(now if now is not None else time.time()))}
    scores = sorted(data["high_scores"] + [entry], key=_rank_key)
    data["high_scores"] = scores[:MAX_HIGH_SCORES]
    data["clears"][run.player_char] = data["clears"].get(run.player_char, 0) + 1
    best = data["best_clear_time"].get(run.player_char)
    if best is None or run.elapsed < best:
        data["best_clear_time"][run.player_char] = round(run.elapsed, 2)
    return next((i + 1 for i, e in enumerate(data["high_scores"]) if e is entry), None)
