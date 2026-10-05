"""
Teste da 6.5.7: todo cenário jogável tem prompts de música (Suno e Gemini) no ROADMAP.md, com o arquivo de destino certo.
Uso: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_music_prompts.py
"""
import os
import re
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.roster import ARENA_ORDER, FIGHTER_BY_ARENA
from src.world.arenas import ARENA_SPECS

HEADER = re.compile(r"^    - \*\*(?P<fighter>[^,\n*]+), (?P<arena>[^(\n]+)\(`(?P<id>[a-z_]+)`, `(?P<music>bgm_[a-z_]+)`\)\*\*$", re.M)
FIGHTER_NAMES = {"kenshin": "Kenshi", "saitou": "Saitou", "musashi": "Musashi", "ninja": "Hanzo", "pirate": "Anne", "purple": "Murasaki",
                 "gray": "Kasumi", "american": "Joe", "rifleman": "Teppo", "kabuki": "Okuni", "archer": "Tomoe", "musketeer": "Julie"}


def _sections():
    text = open(os.path.join(ROOT, "ROADMAP.md"), encoding="utf-8").read()
    start = text.index("**6.5.7: Prompts de música por cenário**")
    end = text.index("### 🔵 FASE 7", start)
    body = text[start:end]
    heads = list(HEADER.finditer(body))
    out = {}
    for k, m in enumerate(heads):
        stop = heads[k + 1].start() if k + 1 < len(heads) else len(body)
        out[m["id"]] = (m, body[m.end():stop])
    return out


def _field(block, label):
    m = re.search(r"- \*\*" + re.escape(label) + r":\*\* (.+)", block)
    assert m, f"campo ausente: {label}"
    return m.group(1).strip()


def test_music_prompts():
    sections = _sections()
    assert set(sections) == set(ARENA_SPECS) == set(ARENA_ORDER), "uma seção por arena registrada"
    names = set()
    for arena_id, spec in ARENA_SPECS.items():
        head, block = sections[arena_id]
        assert head["music"] == spec.music, f"{arena_id}: arquivo {head['music']} != {spec.music}"
        assert os.path.exists(os.path.join(ROOT, "assets", "sounds", "music", f"{spec.music}.mp3")), spec.music
        assert head["fighter"].strip() == FIGHTER_NAMES[FIGHTER_BY_ARENA[arena_id]], f"{arena_id}: lutador {head['fighter']}"
        names.add(head["fighter"].strip())
        assert len(_field(block, "Mood do cenário")) > 30 and len(_field(block, "Personalidade")) > 30
        style = re.search(r"\*\*Suno, estilo \(até 200 caracteres\):\*\* `([^`]+)`", block)
        assert style and 60 <= len(style.group(1)) <= 200, f"{arena_id}: estilo do Suno com {len(style.group(1)) if style else 0} caracteres"
        lyrics = re.search(r"\*\*Suno, letra \(estrutura\):\*\* `([^`]+)`", block)
        assert lyrics and lyrics.group(1).startswith("[Instrumental]") and "[Intro:" in lyrics.group(1) and "loop" in lyrics.group(1).lower(), arena_id
        gem = re.search(r"\*\*Gemini:\*\* \"([^\"]+)\"", block)
        assert gem and len(gem.group(1)) > 250 and "seamless" in gem.group(1) and "no vocals" in gem.group(1).lower(), arena_id
        assert "bpm" in style.group(1).lower() and "BPM" in gem.group(1), f"{arena_id}: andamento nos dois prompts"
        assert len(_field(block, "Evitar")) > 10
    assert len(names) == 12
    print(f"  [OK] As {len(sections)} arenas têm mood, personalidade e prompts de Suno (estilo até 200 caracteres) e Gemini, e o arquivo de música de destino existe.", flush=True)


if __name__ == "__main__":
    test_music_prompts()
    print("=== TESTE 6.5.7 CONCLUÍDO ===", flush=True)
