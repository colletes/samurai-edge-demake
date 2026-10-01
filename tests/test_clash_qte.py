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


if __name__ == "__main__":
    test_clash_trigger_and_resolution()
    print("\nTODOS OS TESTES DE CLASH QTE PASSARAM!")
