# Relatório Detalhado de Balanceamento & Merge Sort de Duelos Simulados

> **Métricas Globais da Simulação**:
> - Total de Guerreiros Avaliados: 12
> - Combinações Únicas de Duelos: 66 confrontos $\binom{12}{2}$
> - Volume de Lutas por Combinação: 24 batalhas simétricas (12 com P1/P2 alternados)
> - **Volume Total de Batalhas Simuladas**: **1584 batalhas**
> - Tempo Total de Simulação Física: 7.61 segundos (208.1 lutas/segundo)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Teppo** | Marksman (Tanegashima/Pólvora) | 174 | 90 | 0 | **65.9%** | A (Forte / Vantajoso) |
| 2 | **Julie** | Mosqueteira (Florete/Riposte) | 162 | 102 | 0 | **61.4%** | A (Forte / Vantajoso) |
| 3 | **Tomoe** | Arqueira Miko (Arco Yumi) | 161 | 103 | 0 | **61.0%** | A (Forte / Vantajoso) |
| 4 | **Anne** | Espadachim (Alfanje 180°) | 154 | 110 | 0 | **58.3%** | A (Forte / Vantajoso) |
| 5 | **Saitou** | Lobo de Mibu (Gatotsu) | 145 | 119 | 0 | **54.9%** | B (Balanceado / Saudável) |
| 6 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 132 | 132 | 0 | **50.0%** | B (Balanceado / Saudável) |
| 7 | **Kenshin** | Retalhador (Iai/Shukuchi) | 129 | 133 | 2 | **48.9%** | B (Balanceado / Saudável) |
| 8 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 116 | 147 | 1 | **43.9%** | C (Desfavorecido / Técnico) |
| 9 | **Musashi** | Duas Lâminas (Combo/Parry) | 109 | 153 | 2 | **41.3%** | C (Desfavorecido / Técnico) |
| 10 | **Joe** | American Ninja (Shuriken/Cão) | 108 | 156 | 0 | **40.9%** | C (Desfavorecido / Técnico) |
| 11 | **Hanzo** | Ninja Mestre (Kunai) | 100 | 163 | 1 | **37.9%** | C (Desfavorecido / Técnico) |
| 12 | **Murasaki** | Kunoichi Foice (Kusarigama) | 91 | 173 | 0 | **34.5%** | C (Desfavorecido / Técnico) |

## 2. Matriz de Confrontos Head-to-Head (H2H 12x12)
A tabela exibe a taxa percentual de vitórias da linha contra a coluna nas 24 lutas disputadas:

| Lutador | Kenshi | Musash | Hanzo | Joe | Saitou | Teppo | Murasa | Kasumi | Okuni | Tomoe | Anne | Julie |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 50% | 46% | 79% | 17% | 75% | 79% | 83% | 17% | 75% | 12% | 4% |
| **Musashi** | 46% | — | 92% | 75% | 4% | 42% | 100% | 0% | 33% | 17% | 12% | 33% |
| **Hanzo** | 54% | 4% | — | 50% | 42% | 33% | 50% | 58% | 33% | 21% | 50% | 21% |
| **Joe** | 21% | 25% | 50% | — | 42% | 25% | 58% | 67% | 58% | 46% | 38% | 21% |
| **Saitou** | 83% | 96% | 58% | 58% | — | 21% | 33% | 54% | 71% | 21% | 42% | 67% |
| **Teppo** | 25% | 58% | 67% | 75% | 79% | — | 92% | 83% | 62% | 58% | 83% | 42% |
| **Murasaki** | 21% | 0% | 50% | 42% | 67% | 8% | — | 62% | 38% | 38% | 33% | 21% |
| **Kasumi** | 12% | 100% | 42% | 33% | 46% | 17% | 38% | — | 50% | 33% | 54% | 58% |
| **Okuni** | 83% | 67% | 67% | 42% | 29% | 38% | 62% | 50% | — | 38% | 46% | 29% |
| **Tomoe** | 25% | 83% | 79% | 54% | 79% | 42% | 62% | 67% | 62% | — | 62% | 54% |
| **Anne** | 88% | 88% | 50% | 62% | 58% | 17% | 67% | 46% | 54% | 38% | — | 75% |
| **Julie** | 96% | 67% | 79% | 79% | 33% | 58% | 79% | 42% | 71% | 46% | 25% | — |

## 3. Resultado do Algoritmo Merge Sort de Duelos
O Merge Sort executou uma ordenação por divisão e conquista onde cada decisão de precedência foi arbitrada pelo retrospecto direto de combates:

1. **Kenshin** — Winrate Geral: 48.9% (129V / 133D / 2E)
2. **Teppo** — Winrate Geral: 65.9% (174V / 90D / 0E)
3. **Tomoe** — Winrate Geral: 61.0% (161V / 103D / 0E)
4. **Anne** — Winrate Geral: 58.3% (154V / 110D / 0E)
5. **Saitou** — Winrate Geral: 54.9% (145V / 119D / 0E)
6. **Julie** — Winrate Geral: 61.4% (162V / 102D / 0E)
7. **Okuni** — Winrate Geral: 50.0% (132V / 132D / 0E)
8. **Musashi** — Winrate Geral: 41.3% (109V / 153D / 2E)
9. **Joe** — Winrate Geral: 40.9% (108V / 156D / 0E)
10. **Hanzo** — Winrate Geral: 37.9% (100V / 163D / 1E)
11. **Murasaki** — Winrate Geral: 34.5% (91V / 173D / 0E)
12. **Kasumi** — Winrate Geral: 43.9% (116V / 147D / 1E)

## 4. Avaliação Técnica Aprofundada do Balanceamento

### 4.1 Opressão e Dominância (Top Tiers)
- **Teppo (65.9%) & Julie (61.4%)**:
  - As mecânicas de ataque com prioridade/precedência absoluta, alcance de projéteis instantâneos (snipers) ou frames defensivos de Parry/Riposte garantem uma taxa de vitória esmagadora contra lutadores de aproximação pura.

### 4.2 Vulnerabilidades Críticas (Bottom Tiers)
- **Murasaki (34.5%) & Hanzo (37.9%)**:
  - Lutadores que dependem de tempos longos de recarga parada (ex: recarga do arcabuz sem cobertura móvel), auto-dano/suicídio por fogo amigo de explosivos, ou windup de retesamento de arco sofrem punições instantâneas contra oponentes rápidos.

### 4.3 Dinâmica de Pedra-Papel-Tesoura e Polarização Extrema
Foram detectados confrontos com polarização extrema (>= 87% de vitória para um lado):
- **Anne vs Kenshin**: Placar esmagador de 21 a 3 (87.5% de dominância)
- **Julie vs Kenshin**: Placar esmagador de 23 a 1 (95.8% de dominância)
- **Musashi vs Hanzo**: Placar esmagador de 22 a 1 (91.7% de dominância)
- **Saitou vs Musashi**: Placar esmagador de 23 a 1 (95.8% de dominância)
- **Musashi vs Murasaki**: Placar esmagador de 24 a 0 (100.0% de dominância)
- **Kasumi vs Musashi**: Placar esmagador de 24 a 0 (100.0% de dominância)
- **Anne vs Musashi**: Placar esmagador de 21 a 3 (87.5% de dominância)
- **Teppo vs Murasaki**: Placar esmagador de 22 a 2 (91.7% de dominância)

## 5. Propostas Concretas de Balance Patch (Recomendações de Design)
Para equalizar o elenco e aproximar todos os combatentes da faixa saudável de 45% a 55% de winrate:
1. **Ajuste de Precedência e Cooldowns de Projéteis**: Aumentar ligeiramente o recovery de golpes com prioridade e projéteis rápidos.
2. **Mobilidade durante a Recarga**: Permitir que classes que recarregam mantenham movimentação a 50% da velocidade, evitando vulnerabilidade estática total.
3. **Redução de Fogo Amigo**: Diminuir o raio de explosão auto-infligido para armas de área (como bombas).
4. **Janela de Defesa (Parry/Riposte)**: Ajustar a janela de parry para exigir timing mais preciso contra sequências rápidas.
