# 05 — Ajustes de balanceamento aplicados (sem aumento de HP)

Método idêntico ao `01_balance_diagnostico.md` (13.248 duelos × 2 réplicas, IA vs IA, `tools/balance_full_matrix.py`). `mist_temple` ainda perde ~25 duelos/réplica por causa do crash de `hazards.py:462` (não corrigido aqui).

## Mudanças

- **IA vs Gatotsu** (`ai_controller.py`): sidestep perpendicular à investida, visão no corredor da investida em qualquer distância, chance própria por dificuldade (0,50/0,85/0,97) em vez da porta de parry (0,55). Gatotsu acertando: **69,6% → 34,5%** (esquivado 10,7% → 51,7%).
- **Teppo**: bala 31,2 → 18 m/s e alcance 18 → 12 m (só Teppo; Mosqueteira inalterada).
- **Benkei**: Naginata boomerang (volta sozinha, acerta na ida e na volta); Tackle removido; IA/textos/testes ajustados.
- **Hanzo**: esquiva (Salto Ninja) 6,4 → 9,0 m/s (~3,1 → ~4,3 m); kunai horizontal de alcance cheio durante a esquiva (1 por salto); IA arremessa na esquiva e **não persegue mais a kunai no chão com o rival a ≤ 4,5 m** (isso, e não a esquiva, foi o que moveu o winrate: 29 → ~42%).
- **Goro**: armor no Pisotão (−1 de dano por golpe, sem stagger), onda de terra instantânea (0,30 → 0,06 s) e 7 torrões (2 s) que destroem projéteis inimigos (corrige também a limpeza que ignorava Kunai).

## Resultado (média de 2 réplicas)

| Lutador | Antes | Depois | Réplica 1 | Réplica 2 |
|:--|:-:|:-:|:-:|:-:|
| Teppo | 72.8% | **61.0%** | 59.7% | 62.3% |
| Valerius | 57.5% | **58.3%** | 57.8% | 58.8% |
| Okuni | 56.8% | **57.1%** | 56.2% | 57.9% |
| Joe | 55.6% | **54.2%** | 56.2% | 52.1% |
| Raiden | 54.5% | **54.0%** | 54.0% | 54.0% |
| Ichi | 55.4% | **53.7%** | 54.2% | 53.1% |
| Benkei | 38.7% | **53.2%** | 55.4% | 51.0% |
| Hendrika | 53.1% | **52.5%** | 53.2% | 51.9% |
| Kenshin | 52.4% | **51.8%** | 51.5% | 52.0% |
| Musashi | 50.9% | **51.0%** | 50.9% | 51.1% |
| Murasaki | 50.8% | **50.9%** | 51.1% | 50.6% |
| Goro | 39.1% | **50.7%** | 51.0% | 50.5% |
| Tomoe | 49.1% | **49.3%** | 48.4% | 50.2% |
| Saitou | 65.0% | **49.2%** | 49.0% | 49.5% |
| Anne | 50.3% | **48.9%** | 50.0% | 47.8% |
| Ren | 49.4% | **48.3%** | 47.7% | 48.9% |
| O-Rin | 47.7% | **48.1%** | 46.0% | 50.2% |
| Daiki | 47.8% | **45.9%** | 45.7% | 46.1% |
| Seimei | 46.2% | **45.7%** | 45.4% | 46.0% |
| Aoi | 46.4% | **44.9%** | 45.3% | 44.6% |
| Kasumi | 43.8% | **43.6%** | 43.7% | 43.5% |
| Julie | 44.0% | **43.4%** | 44.1% | 42.6% |
| Chiyo | 42.7% | **42.3%** | 43.0% | 41.7% |
| Hanzo | 29.9% | **42.0%** | 40.5% | 43.6% |

Mín 42.0% / máx 61.0% (médias); por réplica: mín 40.5% / máx 62.3%. Meta 40–65% atendida nas duas réplicas.

## Observações / riscos
- Hanzo (40,5% na réplica 1) e Chiyo/Julie/Kasumi (41–44%) ficam perto do piso: lista de observação.
- A matriz mede IA. Playtest humano recomendado para: boomerang do Benkei, esquiva+kunai do Hanzo e Pisotão/torrões do Goro.
- Descoberta: a baixa taxa do Hanzo vinha do comportamento da IA (corria atrás da kunai ignorando ameaças), não dos números do personagem; a esquiva da IA contra melee em geral usa uma porta de 55% (`_get_parry_chance`) — vale revisar para lutadores sem parry.
- Testes: `tests/test_balance_no_hp_changes.py` (novo, 14 testes) + testes de Benkei/Goro/Hanzo atualizados. Falhas pré-existentes (11) inalteradas, ver `03_crashes_diagnostico.md` (inclui `test_hanzo_two_step_combo`, desatualizado pelo buff de dano 1→2 que já estava no working tree).

