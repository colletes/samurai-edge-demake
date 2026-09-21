# Relatório Detalhado de Balanceamento & Merge Sort de Duelos Simulados

> **Métricas Globais da Simulação**:
> - Total de Guerreiros Avaliados: 12
> - Combinações Únicas de Duelos: 66 confrontos $\binom{12}{2}$
> - Volume de Lutas por Combinação: 24 batalhas simétricas (12 com P1/P2 alternados)
> - **Volume Total de Batalhas Simuladas**: **1584 batalhas**
> - Tempo Total de Simulação Física: 8.32 segundos (190.4 lutas/segundo)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Julie** | Mosqueteira (Florete/Riposte) | 182 | 82 | 0 | **68.9%** | A (Forte / Vantajoso) |
| 2 | **Saitou** | Lobo de Mibu (Gatotsu) | 165 | 97 | 2 | **62.5%** | A (Forte / Vantajoso) |
| 3 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 148 | 115 | 1 | **56.1%** | A (Forte / Vantajoso) |
| 4 | **Teppo** | Marksman (Tanegashima/Pólvora) | 146 | 117 | 1 | **55.3%** | A (Forte / Vantajoso) |
| 5 | **Kenshin** | Retalhador (Iai/Shukuchi) | 145 | 118 | 1 | **54.9%** | B (Balanceado / Saudável) |
| 6 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 130 | 134 | 0 | **49.2%** | B (Balanceado / Saudável) |
| 7 | **Musashi** | Duas Lâminas (Combo/Parry) | 128 | 134 | 2 | **48.5%** | B (Balanceado / Saudável) |
| 8 | **Tomoe** | Arqueira Miko (Arco Yumi) | 116 | 148 | 0 | **43.9%** | C (Desfavorecido / Técnico) |
| 9 | **Hanzo** | Ninja Mestre (Kunai) | 109 | 154 | 1 | **41.3%** | C (Desfavorecido / Técnico) |
| 10 | **Joe** | American Ninja (Shuriken/Cão) | 109 | 155 | 0 | **41.3%** | C (Desfavorecido / Técnico) |
| 11 | **Anne** | Espadachim (Alfanje 180°) | 106 | 158 | 0 | **40.1%** | C (Desfavorecido / Técnico) |
| 12 | **Murasaki** | Kunoichi Foice (Kusarigama) | 96 | 168 | 0 | **36.4%** | C (Desfavorecido / Técnico) |

## 2. Matriz de Confrontos Head-to-Head (H2H 12x12)
A tabela exibe a taxa percentual de vitórias da linha contra a coluna nas 24 lutas disputadas:

| Lutador | Kenshi | Musash | Hanzo | Joe | Saitou | Teppo | Murasa | Kasumi | Okuni | Tomoe | Anne | Julie |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 42% | 83% | 83% | 12% | 58% | 88% | 92% | 21% | 75% | 29% | 21% |
| **Musashi** | 58% | — | 92% | 79% | 8% | 46% | 96% | 4% | 42% | 33% | 38% | 38% |
| **Hanzo** | 17% | 8% | — | 67% | 46% | 38% | 71% | 33% | 21% | 54% | 71% | 29% |
| **Joe** | 17% | 21% | 33% | — | 50% | 25% | 58% | 50% | 58% | 71% | 62% | 8% |
| **Saitou** | 83% | 92% | 50% | 50% | — | 46% | 58% | 29% | 79% | 54% | 71% | 75% |
| **Teppo** | 42% | 50% | 62% | 75% | 54% | — | 54% | 58% | 58% | 67% | 71% | 17% |
| **Murasaki** | 12% | 4% | 29% | 42% | 42% | 46% | — | 50% | 46% | 62% | 50% | 17% |
| **Kasumi** | 8% | 92% | 67% | 50% | 71% | 42% | 50% | — | 46% | 46% | 88% | 58% |
| **Okuni** | 79% | 58% | 79% | 42% | 21% | 42% | 54% | 54% | — | 50% | 46% | 17% |
| **Tomoe** | 25% | 67% | 46% | 29% | 46% | 33% | 38% | 54% | 50% | — | 75% | 21% |
| **Anne** | 71% | 62% | 29% | 38% | 29% | 29% | 50% | 12% | 54% | 25% | — | 42% |
| **Julie** | 79% | 62% | 71% | 92% | 25% | 83% | 83% | 42% | 83% | 79% | 58% | — |

## 3. Resultado do Algoritmo Merge Sort de Duelos
O Merge Sort executou uma ordenação por divisão e conquista onde cada decisão de precedência foi arbitrada pelo retrospecto direto de combates:

1. **Julie** — Winrate Geral: 68.9% (182V / 82D / 0E)
2. **Teppo** — Winrate Geral: 55.3% (146V / 117D / 1E)
3. **Saitou** — Winrate Geral: 62.5% (165V / 97D / 2E)
4. **Okuni** — Winrate Geral: 49.2% (130V / 134D / 0E)
5. **Tomoe** — Winrate Geral: 43.9% (116V / 148D / 0E)
6. **Kasumi** — Winrate Geral: 56.1% (148V / 115D / 1E)
7. **Anne** — Winrate Geral: 40.1% (106V / 158D / 0E)
8. **Musashi** — Winrate Geral: 48.5% (128V / 134D / 2E)
9. **Kenshin** — Winrate Geral: 54.9% (145V / 118D / 1E)
10. **Hanzo** — Winrate Geral: 41.3% (109V / 154D / 1E)
11. **Joe** — Winrate Geral: 41.3% (109V / 155D / 0E)
12. **Murasaki** — Winrate Geral: 36.4% (96V / 168D / 0E)

## 4. Avaliação Técnica Aprofundada do Balanceamento

### 4.1 Opressão e Dominância (Top Tiers)
- **Julie (68.9%) & Saitou (62.5%)**:
  - As mecânicas de ataque com prioridade/precedência absoluta, alcance de projéteis instantâneos (snipers) ou frames defensivos de Parry/Riposte garantem uma taxa de vitória esmagadora contra lutadores de aproximação pura.

### 4.2 Vulnerabilidades Críticas (Bottom Tiers)
- **Murasaki (36.4%) & Anne (40.1%)**:
  - Lutadores que dependem de tempos longos de recarga parada (ex: recarga do arcabuz sem cobertura móvel), auto-dano/suicídio por fogo amigo de explosivos, ou windup de retesamento de arco sofrem punições instantâneas contra oponentes rápidos.

### 4.3 Dinâmica de Pedra-Papel-Tesoura e Polarização Extrema
Foram detectados confrontos com polarização extrema (>= 87% de vitória para um lado):
- **Kenshin vs Murasaki**: Placar esmagador de 21 a 3 (87.5% de dominância)
- **Kenshin vs Kasumi**: Placar esmagador de 22 a 2 (91.7% de dominância)
- **Musashi vs Hanzo**: Placar esmagador de 22 a 2 (91.7% de dominância)
- **Saitou vs Musashi**: Placar esmagador de 22 a 2 (91.7% de dominância)
- **Musashi vs Murasaki**: Placar esmagador de 23 a 1 (95.8% de dominância)
- **Kasumi vs Musashi**: Placar esmagador de 22 a 1 (91.7% de dominância)
- **Julie vs Joe**: Placar esmagador de 22 a 2 (91.7% de dominância)
- **Kasumi vs Anne**: Placar esmagador de 21 a 3 (87.5% de dominância)

## 5. Propostas Concretas de Balance Patch (Recomendações de Design)
Para equalizar o elenco e aproximar todos os combatentes da faixa saudável de 45% a 55% de winrate:
1. **Ajuste de Precedência e Cooldowns de Projéteis**: Aumentar ligeiramente o recovery de golpes com prioridade e projéteis rápidos.
2. **Mobilidade durante a Recarga**: Permitir que classes que recarregam mantenham movimentação a 50% da velocidade, evitando vulnerabilidade estática total.
3. **Redução de Fogo Amigo**: Diminuir o raio de explosão auto-infligido para armas de área (como bombas).
4. **Janela de Defesa (Parry/Riposte)**: Ajustar a janela de parry para exigir timing mais preciso contra sequências rápidas.
