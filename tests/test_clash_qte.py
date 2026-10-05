"""
Teste da Fase 5 - Entregável 5.1: Clash de Espadas Tsubazeriai (QTE "STRIKE!").

Valida que:
1. Dois ataques de mesma prioridade colidindo disparam o ClashSystem (via
   CombatSystem.process_combat) em vez do antigo atordoamento mútuo simples.
2. Ambos os lutadores ficam congelados (estado CLASH_QTE, hitbox desativada)
   enquanto o choque estiver ativo.
3. O jogador que aperta o botão primeiro vence o choque, empurra e atordoa
   o oponente.
4. Se nenhum jogador apertar a tempo, o choque termina em empate (ambos
   levemente atordoados, sem vencedor de round).
5. Contra a IA, o oponente aperta o botão após o tempo de reação da dificuldade
   (ou não reage), então o jogador humano não vence o choque por padrão.
6. Os avisos são localizados (PT/EN), o perdedor é empurrado respeitando os
   limites do mapa e pode cair em um buraco, e o botão arcade é desenhado.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()
pygame.font.init()

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.samurai import STATE_STUNNED
from src.combat.collision import CombatSystem
from src.combat.clash_system import ClashSystem, STATE_CLASH_QTE, QTE_WINDOW
from src.world.map_data import GameMap
from src.isometric.camera import Camera


def _make_mutual_clash(p1, p2):
    """Posiciona e arma os dois lutadores para colidirem no mesmo instante, com a
    mesma prioridade (nenhum é um golpe de precedência absoluta)."""
    p1.wx, p1.wy = 10.0, 10.0
    p2.wx, p2.wy = 11.4, 10.0
    p1.set_facing(p2.wx, p2.wy)
    p2.set_facing(p1.wx, p1.wy)

    for fighter in (p1, p2):
        fighter.hitbox_active = True
        fighter.hitbox_radius = 1.25
        fighter.is_priority_strike = False
    p1.hitbox_center = (p1.wx + p1.facing_x * 0.7, p1.wy + p1.facing_y * 0.7)
    p2.hitbox_center = (p2.wx + p2.facing_x * 0.7, p2.wy + p2.facing_y * 0.7)
    p1.slash_dir = (p1.facing_x, p1.facing_y)
    p2.slash_dir = (p2.facing_x, p2.facing_y)


def test_clash_trigger_and_resolution():
    game_map = GameMap()
    camera = Camera()
    particles = []
    banners = []
    projectiles = []

    print("=== TESTE 5.1: Clash de Espadas Tsubazeriai (QTE 'STRIKE!') ===", flush=True)

    # --- 1. Disparo do choque: dois ataques de mesma prioridade colidindo ---
    combat = CombatSystem()
    clash_system = ClashSystem()
    p1 = RedSamurai(0.0, 0.0)
    p2 = BlueSamurai(0.0, 0.0)
    _make_mutual_clash(p1, p2)

    assert not clash_system.is_frozen(), "ClashSystem não deveria começar ativo"

    winner = combat.process_combat(p1, p2, game_map, particles, banners, camera, projectiles, dt=0.016, clash_system=clash_system)

    assert winner is None, "Um choque de espadas não deve declarar vencedor de round imediatamente"
    assert clash_system.is_frozen(), "ClashSystem DEVE ativar o QTE quando dois ataques de mesma prioridade colidem"
    assert p1.state == STATE_CLASH_QTE and p2.state == STATE_CLASH_QTE, "Ambos os lutadores devem ficar no estado CLASH_QTE"
    assert not p1.hitbox_active and not p2.hitbox_active, "Hitboxes devem ser desativadas durante o choque"
    assert not p1.can_act() and not p2.can_act(), "Nenhum lutador deve poder agir durante o choque de espadas"
    print("  [OK] Choque de espadas disparado corretamente, ambos congelados em CLASH_QTE.", flush=True)

    # --- 2. Zoom dramático aplicado à câmera durante o choque ---
    clash_system.update(dt=0.3, camera=camera, particles=particles, banners=banners)
    assert camera.zoom > 1.0, "A câmera deve aplicar um zoom dramático durante o choque"
    print(f"  [OK] Zoom dramático da câmera aplicado (zoom={camera.zoom:.3f}).", flush=True)

    # --- 3. P1 aperta o botão primeiro -> P1 vence o choque ---
    clash_system.register_press(0)
    result = clash_system.update(dt=0.016, camera=camera, particles=particles, banners=banners)
    assert result == "P1_WINS_CLASH", f"Esperado P1_WINS_CLASH, obtido {result}"
    assert not clash_system.is_frozen(), "ClashSystem deve se desativar após resolver o choque"
    assert p2.state == STATE_STUNNED and p2.state_timer > 0, "O perdedor do choque deve ficar atordoado"
    assert camera.zoom == 1.0, "O zoom dramático deve ser resetado ao final do choque"
    print("  [OK] P1 apertou primeiro e venceu o choque; câmera restaurada ao zoom normal.", flush=True)

    # --- 4. Empate: nenhum jogador aperta a tempo ---
    p1b = RedSamurai(0.0, 0.0)
    p2b = BlueSamurai(0.0, 0.0)
    _make_mutual_clash(p1b, p2b)
    clash_system2 = ClashSystem()
    combat.process_combat(p1b, p2b, game_map, particles, banners, camera, projectiles, dt=0.016, clash_system=clash_system2)
    assert clash_system2.is_frozen(), "Segundo choque deveria ter sido disparado"

    # Avança o tempo além da janela de QTE sem nenhum input
    result2 = None
    elapsed = 0.0
    while elapsed < QTE_WINDOW + 0.2 and result2 is None:
        result2 = clash_system2.update(dt=0.05, camera=camera, particles=particles, banners=banners)
        elapsed += 0.05

    assert result2 == "DRAW_CLASH", f"Esperado DRAW_CLASH quando ninguém aperta a tempo, obtido {result2}"
    assert not clash_system2.is_frozen()
    print("  [OK] Choque sem input de nenhum jogador termina corretamente em DRAW_CLASH.", flush=True)

    print("=== TESTE 5.1 CONCLUÍDO COM SUCESSO ===", flush=True)


def _start_clash(game_map, camera, clash_system, x1=10.0, x2=11.4, y=10.0):
    p1, p2 = RedSamurai(0.0, 0.0), BlueSamurai(0.0, 0.0)
    _make_mutual_clash(p1, p2)
    p1.wx, p2.wx = x1, x2
    p1.wy = p2.wy = y
    p1.set_facing(p2.wx, p2.wy)
    p2.set_facing(p1.wx, p1.wy)
    p1.hitbox_center = (p1.wx + p1.facing_x * 0.7, p1.wy + p1.facing_y * 0.7)
    p2.hitbox_center = (p2.wx + p2.facing_x * 0.7, p2.wy + p2.facing_y * 0.7)
    CombatSystem().process_combat(p1, p2, game_map, [], [], camera, [], dt=0.016, clash_system=clash_system)
    assert clash_system.is_frozen()
    return p1, p2


def _run_until_result(clash_system, game_map=None, camera=None, banners=None):
    for _ in range(100):
        result = clash_system.update(dt=0.02, camera=camera, banners=banners, game_map=game_map)
        if result:
            return result
    return None


def test_clash_ai_localization_pushback_and_render():
    from src.i18n import set_lang, get_lang
    from src.entities.ai_controller import SamuraiAI
    game_map, camera = GameMap(), Camera()

    # IA aperta depois do tempo de reação: P2 vence, pois P1 não apertou nada
    cs = ClashSystem()
    cs.ai_player, cs.ai_reaction_fn = 1, lambda: 0.2
    p1, p2 = _start_clash(game_map, camera, cs)
    assert _run_until_result(cs, game_map, camera) == "P2_WINS_CLASH"
    assert p1.state == STATE_STUNNED and p2.state != STATE_STUNNED

    # IA que não reage a tempo: empate
    cs = ClashSystem()
    cs.ai_player, cs.ai_reaction_fn = 1, lambda: None
    _start_clash(game_map, camera, cs)
    assert _run_until_result(cs, game_map, camera) == "DRAW_CLASH"

    # Humano aperta antes da IA (reação de 0.5 s): P1 vence
    cs = ClashSystem()
    cs.ai_player, cs.ai_reaction_fn = 1, lambda: 0.5
    _start_clash(game_map, camera, cs)
    cs.register_press(0)
    assert _run_until_result(cs, game_map, camera) == "P1_WINS_CLASH"

    # Tempos de reação por dificuldade ficam dentro da janela do QTE; mais fácil = mais lento
    for difficulty, ceiling in (("easy", 0.60), ("normal", 0.45), ("hard", 0.28)):
        ai = SamuraiAI(difficulty)
        delays = [d for d in (ai.get_clash_reaction() for _ in range(300)) if d is not None]
        assert delays and max(delays) <= ceiling and max(delays) < QTE_WINDOW
    hard = [ai.get_clash_reaction() is None for ai in [SamuraiAI("hard")] * 400]
    easy = [ai.get_clash_reaction() is None for ai in [SamuraiAI("easy")] * 400]
    assert sum(easy) > sum(hard), "a IA fácil perde mais choques por não reagir"

    # Avisos localizados
    previous = get_lang()
    texts = {}
    for lang in ("pt", "en"):
        set_lang(lang)
        banners = []
        cs = ClashSystem()
        _start_clash(game_map, camera, cs)
        cs.register_press(0)
        cs.update(dt=0.02, camera=camera, banners=banners, game_map=game_map)
        texts[lang] = banners[0].text if hasattr(banners[0], "text") else str(vars(banners[0]))
    set_lang(previous)
    assert texts["pt"] != texts["en"] and "VENCE" in texts["pt"] and "WINS" in texts["en"], texts

    # Empurrão do perdedor respeita o limite do mapa (não sai da arena)
    cs = ClashSystem()
    p1, p2 = _start_clash(game_map, camera, cs, x1=1.5, x2=1.2, y=10.0)
    p1.wx, p2.wx = 2.0, 1.2
    cs.register_press(0)
    cs.update(dt=0.02, camera=camera, game_map=game_map)
    assert p2.wx >= 1.0 - 1e-9, f"perdedor empurrado para fora do mapa: x={p2.wx}"

    # Empurrão pode derrubar o perdedor em um buraco
    from tests.test_arena_engine import _crossing_arena
    arena = _crossing_arena()
    pit = arena.pits[1]
    cs = ClashSystem()
    p1, p2 = _start_clash(arena, camera, cs, x1=pit.x0 - 1.3, x2=pit.x0 - 0.1, y=11.0)
    p1.wx, p2.wx = pit.x0 - 1.3, pit.x0 - 0.1
    cs.register_press(0)
    cs.update(dt=0.02, camera=camera, game_map=arena)
    assert p2.update_pit(0.016, arena) is True, "o perdedor do choque cai se for empurrado para dentro do buraco"

    # Botão arcade desenhado com as teclas de cada jogador
    cs = ClashSystem()
    cs.key_hints = ("E", "O")
    p1, p2 = _start_clash(game_map, camera, cs)
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill((20, 20, 24))
    cs.render(surf, camera)
    painted = SCREEN_WIDTH * SCREEN_HEIGHT - pygame.mask.from_threshold(surf, (20, 20, 24), (2, 2, 2, 255)).count()
    assert painted > 3000, "o botão STRIKE! deve ser desenhado"
    print("  [OK] IA aperta pelo tempo de reação, avisos PT/EN, empurrão com limites e queda, botão arcade.", flush=True)


if __name__ == "__main__":
    test_clash_trigger_and_resolution()
    test_clash_ai_localization_pushback_and_render()
    print("\nTODOS OS TESTES DE CLASH QTE PASSARAM!")
