"""
Teste da Fase 5 - Entregável 5.3: Contador Best of 3 (BO3) e Tela de Resultados.

Valida que:
1. check_match_winner() só declara um vencedor quando um jogador atinge o
   número de rounds necessário (2 de 3, por padrão).
2. A tela de resultados (RoundResultScreen) bloqueia a revanche instantânea
   (evita pular sem querer a tela) e libera a revanche após um pequeno atraso.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()
pygame.font.init()

from src.ui.round_result import check_match_winner, RoundResultScreen, MATCH_WINS_NEEDED


def test_bo3_match_winner():
    print("=== TESTE 5.3: Contador Best of 3 (BO3) e Tela de Resultados ===", flush=True)

    assert MATCH_WINS_NEEDED == 2, "Melhor-de-3 exige 2 vitórias para fechar a partida"

    # --- 1. Nenhum vencedor ainda ---
    for score_p1, score_p2 in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        assert check_match_winner(score_p1, score_p2) is None, \
            f"Não deveria haver vencedor de partida em {score_p1}x{score_p2}"
    print("  [OK] Nenhum vencedor declarado antes de 2 rounds vencidos.", flush=True)

    # --- 2. P1 fecha a partida 2x0 ---
    assert check_match_winner(2, 0) == "P1"
    # --- 3. P1 fecha a partida 2x1 ---
    assert check_match_winner(2, 1) == "P1"
    # --- 4. P2 fecha a partida 0x2 ---
    assert check_match_winner(0, 2) == "P2"
    # --- 5. P2 fecha a partida 1x2 ---
    assert check_match_winner(1, 2) == "P2"
    print("  [OK] Vencedor de partida corretamente identificado em 2x0, 2x1, 0x2 e 1x2.", flush=True)

    # --- 6. Parâmetro wins_needed customizado (ex: Melhor-de-5) ---
    assert check_match_winner(2, 0, wins_needed=3) is None, "Não deveria fechar Melhor-de-5 com apenas 2 vitórias"
    assert check_match_winner(3, 1, wins_needed=3) == "P1"
    print("  [OK] Parâmetro wins_needed customizado respeitado (ex: Melhor-de-5).", flush=True)

    # --- 7. Tela de resultados: bloqueia revanche instantânea, libera após atraso ---
    screen_result = RoundResultScreen()
    screen_result.show("SAMURAI VERMELHO", (220, 60, 60), 2, 1)
    assert screen_result.active, "A tela de resultados deve ficar ativa após show()"
    assert not screen_result.can_accept_rematch(), "Não deve aceitar revanche instantaneamente (evita pular a tela sem querer)"

    # Avança o tempo até passar do limiar de 0.35s
    for _ in range(20):
        screen_result.update(dt=0.05)
    assert screen_result.can_accept_rematch(), "Deve aceitar revanche após o pequeno atraso de segurança"
    print("  [OK] RoundResultScreen bloqueia revanche instantânea e libera após o atraso de segurança.", flush=True)

    # --- 8. hide() desativa a tela corretamente ---
    screen_result.hide()
    assert not screen_result.active, "hide() deve desativar a tela de resultados"
    print("  [OK] hide() desativa corretamente a tela de resultados.", flush=True)

    print("=== TESTE 5.3 CONCLUÍDO COM SUCESSO ===", flush=True)


if __name__ == "__main__":
    test_bo3_match_winner()
    print("\nTODOS OS TESTES DE PROGRESSÃO DE ROUNDS (BO3) PASSARAM!")
