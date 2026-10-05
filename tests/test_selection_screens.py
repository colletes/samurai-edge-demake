"""
Testes da Fase 6.3.3 — telas de seleção: retratos, ordem do elenco e sorteios.
Execução: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_selection_screens.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

from src import i18n
from src.config import ARENA_RANDOM, CHAR_RANDOM, SCREEN_HEIGHT, SCREEN_WIDTH
from src.roster import ARENA_BY_FIGHTER, ARENA_ORDER, FIGHTER_BY_ARENA, ROSTER_ORDER
from src.ui.arena_select import ArenaSelectScreen
from src.ui.character_select import CharacterSelectScreen
from src.world.arenas import arena_ids


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def _render_arena(screen_obj):
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen_obj.update(0.016)
    screen_obj.render(surf, None, None, None)
    return surf


def test_roster_is_single_source_of_order():
    assert len(ROSTER_ORDER) == 12 and len(ARENA_ORDER) == 12
    assert [ARENA_BY_FIGHTER[f] for f in ROSTER_ORDER] == list(ARENA_ORDER)
    assert all(FIGHTER_BY_ARENA[a] == f for f, a in ARENA_BY_FIGHTER.items())
    print("  [OK] src/roster.py: ordem do elenco, arena e lutador consistentes.", flush=True)


def test_arena_cards_follow_roster_order():
    sel = ArenaSelectScreen()
    cards = sel.arenas
    assert len(cards) == 13
    assert [c["id"] for c in cards[:12]] == list(ARENA_ORDER)
    assert [c["fighter_id"] for c in cards[:12]] == list(ROSTER_ORDER)
    assert cards[12]["id"] == ARENA_RANDOM and cards[12]["fighter_id"] is None
    assert sel.selected_idx == 0
    print("  [OK] Arenas seguem a ordem do elenco, Aleatório por último.", flush=True)


class _WithoutArena:
    """Tira temporariamente uma arena do registro para simular uma carta bloqueada (todas as 12 já existem)."""

    def __init__(self, arena_id):
        self.arena_id = arena_id

    def __enter__(self):
        from src.world import arenas as arena_registry
        self.registry = arena_registry.ARENA_SPECS
        self.spec = self.registry.pop(self.arena_id)
        return self.arena_id

    def __exit__(self, *exc):
        self.registry[self.arena_id] = self.spec


def test_locked_cards_match_registry():
    sel = ArenaSelectScreen()
    built = set(arena_ids())
    assert built == set(ARENA_ORDER), "as 12 arenas estão registradas"
    for card in sel.arenas[:12]:
        assert card["locked"] == (card["id"] not in built), card["id"]
    assert not any(c["locked"] for c in sel.arenas)
    with _WithoutArena(ARENA_ORDER[-1]) as missing:
        sel = ArenaSelectScreen()
        assert [c["id"] for c in sel.arenas if c["locked"]] == [missing]
    print("  [OK] Cartas bloqueadas = arenas não registradas (nenhuma com as 12 prontas).", flush=True)


def test_unlock_follows_registry():
    """Registrar um spec novo libera a carta automaticamente (sem mexer na tela)."""
    from src.world import arenas as arena_registry
    with _WithoutArena(ARENA_ORDER[-1]) as locked_id:
        assert next(c for c in ArenaSelectScreen().arenas if c["id"] == locked_id)["locked"]
        spec = arena_registry.BAROQUE_COURT_SPEC
        arena_registry.ARENA_SPECS[locked_id] = spec
        sel = ArenaSelectScreen()
        card = next(c for c in sel.arenas if c["id"] == locked_id)
        assert not card["locked"]
        sel.selected_idx = [c["id"] for c in sel.arenas].index(locked_id)
        assert sel.handle_event(key(pygame.K_RETURN)) == locked_id
        del arena_registry.ARENA_SPECS[locked_id]
    print("  [OK] Arena registrada libera a carta sozinha.", flush=True)


def test_confirm_on_locked_is_ignored():
    with _WithoutArena(ARENA_ORDER[-1]):
        sel = ArenaSelectScreen()
        locked_idx = next(i for i, c in enumerate(sel.arenas) if c["locked"])
        sel.selected_idx = locked_idx
        assert sel.handle_event(key(pygame.K_RETURN)) is None
        assert sel.locked_flash > 0
        # clique do mouse numa carta bloqueada também não confirma
        _render_arena(sel)
        pos = sel.card_rects[locked_idx].center
        ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)
        assert sel.handle_event(ev) is None
        assert sel.handle_event(key(pygame.K_ESCAPE)) == "BACK"
    print("  [OK] Confirmar arena bloqueada não inicia a partida.", flush=True)


def test_confirm_unlocked_returns_arena():
    sel = ArenaSelectScreen()
    for idx, card in enumerate(sel.arenas[:12]):
        if card["locked"]:
            continue
        sel.selected_idx = idx
        assert sel.handle_event(key(pygame.K_RETURN)) == card["id"]
    _render_arena(sel)
    idx = 4  # Kyoto
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=sel.card_rects[idx].center)
    assert sel.handle_event(ev) == sel.arenas[idx]["id"]
    print("  [OK] Confirmar arena liberada devolve o id correto (teclado e mouse).", flush=True)


def test_random_arena_only_unlocked():
    sel = ArenaSelectScreen()
    sel.selected_idx = 12
    built = set(arena_ids())
    seen = set()
    for _ in range(200):
        resolved = sel.handle_event(key(pygame.K_RETURN))
        assert resolved in built, resolved
        seen.add(resolved)
    assert len(seen) == len(built), "o sorteio deve alcançar todas as arenas liberadas"
    print("  [OK] Arena Aleatória sorteia só entre arenas liberadas.", flush=True)


def test_arena_navigation_cycles_all_cards():
    sel = ArenaSelectScreen()
    visited = [sel.selected_idx]
    for _ in range(12):
        sel.handle_event(key(pygame.K_RIGHT))
        visited.append(sel.selected_idx)
    assert visited == list(range(13)), visited
    sel.handle_event(key(pygame.K_RIGHT))
    assert sel.selected_idx == 0
    sel.handle_event(key(pygame.K_LEFT))
    assert sel.selected_idx == 12
    # vertical: linha 1 -> linha 2 -> volta
    sel.selected_idx = 2
    sel.handle_event(key(pygame.K_DOWN))
    assert sel.selected_idx == 9
    sel.handle_event(key(pygame.K_UP))
    assert sel.selected_idx == 2
    sel.selected_idx = 6
    sel.handle_event(key(pygame.K_DOWN))
    assert sel.selected_idx == 12  # as duas últimas colunas pertencem ao Aleatório
    sel.handle_event(key(pygame.K_UP))
    assert sel.selected_idx == 5
    # direcional do controle
    sel.selected_idx = 0
    sel.handle_event(pygame.event.Event(pygame.JOYHATMOTION, hat=0, value=(1, 0), instance_id=0, joy=0))
    assert sel.selected_idx == 1
    print("  [OK] Navegação por teclado/controle percorre as 13 cartas sem pular.", flush=True)


def test_arena_screen_renders_pt_en_all_cards():
    for lang in ("pt", "en"):
        i18n.set_lang(lang)
        sel = ArenaSelectScreen()
        for idx in range(13):
            sel.selected_idx = idx
            _render_arena(sel)
        assert len(sel.card_rects) == 13
        # as cartas não se sobrepõem
        for i, a in enumerate(sel.card_rects):
            for b in sel.card_rects[i + 1:]:
                assert not a.colliderect(b)
    i18n.set_lang("pt")
    print("  [OK] Tela de arena renderiza em PT/EN com todas as cartas.", flush=True)


def test_arena_portraits_present():
    from src.ui.portraits import get_portrait
    for fighter_id in ROSTER_ORDER:
        assert get_portrait(fighter_id, size=(44, 44), circular=True) is not None, fighter_id
    print("  [OK] Cada arena tem o retrato do seu lutador disponível.", flush=True)


def test_char_select_random_card_and_navigation():
    cs = CharacterSelectScreen()
    assert len(cs.characters) == 13
    assert [c["id"] for c in cs.characters[:12]] == list(ROSTER_ORDER)
    assert cs.characters[12]["id"] == CHAR_RANDOM
    assert cs.random_idx == 12
    # percorre as 13 cartas: direita nas 2 linhas de 6, depois desce para o Aleatório
    cs.p1_choice_idx = 0
    seen = {0}
    for step in range(5):
        cs.handle_event(key(pygame.K_d))
        seen.add(cs.p1_choice_idx)
    cs.handle_event(key(pygame.K_s))
    seen.add(cs.p1_choice_idx)
    assert cs.p1_choice_idx == 11
    cs.handle_event(key(pygame.K_s))
    assert cs.p1_choice_idx == 12
    cs.handle_event(key(pygame.K_w))
    assert cs.p1_choice_idx == 11  # volta para a coluna lembrada
    cs.p1_choice_idx = 12
    cs.handle_event(key(pygame.K_s))
    assert cs.p1_choice_idx == 5  # rotação vertical completa, na coluna lembrada
    # gamepad
    cs.p1_choice_idx = 12
    cs.handle_event(pygame.event.Event(pygame.JOYHATMOTION, hat=0, value=(0, 1), instance_id=0, joy=0))
    print("  [OK] Seleção de personagem: 13ª carta e navegação.", flush=True)


def test_char_select_random_reveal_resolves_to_fighter():
    for _ in range(40):
        cs = CharacterSelectScreen()
        cs.vs_ai = True
        cs.p1_choice_idx = cs.random_idx
        cs.p2_choice_idx = cs.random_idx
        cs.selection_step = "AI"
        assert cs.handle_event(key(pygame.K_RETURN)) is False  # começa a roleta, não inicia direto
        assert cs.reveal is not None
        finished = False
        for _ in range(400):
            if cs.update(0.016):
                finished = True
                break
        assert finished, "a roleta precisa terminar"
        assert cs.reveal is None
        p1, p2, vs_ai = cs.get_selected_characters()
        assert p1 in ROSTER_ORDER and p2 in ROSTER_ORDER and vs_ai is True
    print("  [OK] Aleatório revela e resolve para um dos 12 lutadores.", flush=True)


def test_char_select_random_only_when_chosen():
    cs = CharacterSelectScreen()
    cs.vs_ai = True
    cs.p1_choice_idx = 3
    cs.p2_choice_idx = 5
    cs.selection_step = "AI"
    assert cs.handle_event(key(pygame.K_RETURN)) is True  # sem Aleatório não há roleta
    assert cs.reveal is None
    assert cs.get_selected_characters()[:2] == (ROSTER_ORDER[3], ROSTER_ORDER[5])
    # um só Aleatório: o outro lutador não muda
    cs = CharacterSelectScreen()
    cs.p1_choice_idx = cs.random_idx
    cs.p2_choice_idx = 7
    cs.selection_step = "AI"
    cs.handle_event(key(pygame.K_RETURN))
    while not cs.update(0.05):
        pass
    p1, p2, _ = cs.get_selected_characters()
    assert p2 == ROSTER_ORDER[7] and p1 in ROSTER_ORDER
    print("  [OK] Roleta só quando o Aleatório é escolhido.", flush=True)


def test_char_select_get_selected_resolves_direct_call():
    cs = CharacterSelectScreen()
    cs.p1_choice_idx = cs.random_idx
    cs.p2_choice_idx = cs.random_idx
    for _ in range(30):
        p1, p2, _ = cs.get_selected_characters()
        assert p1 in ROSTER_ORDER and p2 in ROSTER_ORDER
    print("  [OK] get_selected_characters nunca devolve o marcador Aleatório.", flush=True)


def test_char_select_input_ignored_during_reveal():
    cs = CharacterSelectScreen()
    cs.p1_choice_idx = cs.random_idx
    cs.selection_step = "AI"
    cs.handle_event(key(pygame.K_RETURN))
    assert cs.reveal is not None
    assert cs.handle_event(key(pygame.K_ESCAPE)) is False
    assert cs.reveal is not None
    print("  [OK] Entradas são ignoradas durante a roleta.", flush=True)


def test_char_select_renders_pt_en():
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 24)
    for lang in ("pt", "en"):
        i18n.set_lang(lang)
        cs = CharacterSelectScreen()
        for idx in (0, 11, 12):
            cs.p1_choice_idx = idx
            cs.update(0.016)
            cs.render(surf, font, font, font)
        cs.p1_choice_idx = cs.random_idx
        cs.selection_step = "AI"
        cs.handle_event(key(pygame.K_RETURN))
        cs.update(0.5)
        cs.render(surf, font, font, font)  # durante a roleta
    i18n.set_lang("pt")
    print("  [OK] Seleção de personagem renderiza em PT/EN (inclusive durante a roleta).", flush=True)


def test_every_registered_arena_has_card_texts_and_music():
    """Arena liberada sem texto de detalhe quebraria a tela; toda arena do registro precisa de PT/EN e música."""
    from src.world.arenas import ARENA_SPECS
    detail = {"bamboo": "bamboo", "kyoto": "kyoto", "ganryu_island": "ganryu"}
    for arena_id, spec in ARENA_SPECS.items():
        stem = detail.get(arena_id, arena_id)
        for lang in ("pt", "en"):
            i18n.set_lang(lang)
            for part in ("name", "subtitle", "hazard", "features", "tactics"):
                assert i18n.t(f"arena_{stem}_{part}") != f"arena_{stem}_{part}", f"{lang}: arena_{stem}_{part}"
        assert os.path.exists(os.path.join(ROOT, "assets", "sounds", "music", f"{spec.music}.mp3")), spec.music
    i18n.set_lang("pt")
    sel = ArenaSelectScreen()
    for idx, card in enumerate(sel.arenas):
        sel.selected_idx = idx
        _render_arena(sel)  # painel de detalhe das liberadas não pode falhar
    print("  [OK] Toda arena registrada tem textos PT/EN e música.", flush=True)


def test_i18n_keys_present():
    from src.roster import FIGHTER_NAME_KEY
    keys = ["char_random_name", "char_random_title", "char_random_style", "arena_of_fighter",
            "arena_locked", "arena_locked_hint"]
    keys += [f"arena_{a}_name" for a in ARENA_ORDER if a not in ("bamboo", "kyoto", "ganryu_island")]
    keys += list(FIGHTER_NAME_KEY.values())
    for lang in ("pt", "en"):
        i18n.set_lang(lang)
        for k in keys:
            assert i18n.t(k) != k, f"{lang}: chave ausente {k}"
    i18n.set_lang("pt")
    print("  [OK] Textos PT/EN presentes.", flush=True)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    # mantém a ordem de definição
    tests = [v for v in globals().values() if callable(v) and getattr(v, "__name__", "").startswith("test_")]
    for fn in tests:
        print(fn.__name__, flush=True)
        fn()
    print(f"\nTODOS OS {len(tests)} TESTES DE TELAS DE SELEÇÃO PASSARAM!")
