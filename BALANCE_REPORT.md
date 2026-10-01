# Relatório Detalhado de Balanceamento & Merge Sort de Duelos Simulados

> **Métricas Globais da Simulação**:
> - Dificuldade da IA (ambos os lutadores): **NORMAL**
> - Total de Guerreiros Avaliados: 12
> - Combinações Únicas de Duelos: 66 confrontos $\binom{12}{2}$
> - Volume de Lutas por Combinação: 24 batalhas simétricas (12 com P1/P2 alternados)
> - **Volume Total de Batalhas Simuladas**: **1584 batalhas**
> - Tempo Total de Simulação Física: 6.29 segundos (251.8 lutas/segundo)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Teppo** | Marksman (Tanegashima/Pólvora) | 189 | 66 | 9 | **71.6%** | S (Top Tier - Opressivo) |
| 2 | **Tomoe** | Arqueira Miko (Arco Yumi) | 156 | 89 | 19 | **59.1%** | A (Forte / Vantajoso) |
| 3 | **Joe** | American Ninja (Shuriken/Cão) | 153 | 100 | 11 | **58.0%** | A (Forte / Vantajoso) |
| 4 | **Murasaki** | Kunoichi Foice (Kusarigama) | 140 | 108 | 16 | **53.0%** | B (Balanceado / Saudável) |
| 5 | **Julie** | Mosqueteira (Florete/Riposte) | 140 | 111 | 13 | **53.0%** | B (Balanceado / Saudável) |
| 6 | **Musashi** | Duas Lâminas (Combo/Parry) | 137 | 106 | 21 | **51.9%** | B (Balanceado / Saudável) |
| 7 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 124 | 131 | 9 | **47.0%** | B (Balanceado / Saudável) |
| 8 | **Hanzo** | Ninja Mestre (Kunai) | 115 | 133 | 16 | **43.6%** | C (Desfavorecido / Técnico) |
| 9 | **Kenshin** | Retalhador (Iai/Shukuchi) | 109 | 135 | 20 | **41.3%** | C (Desfavorecido / Técnico) |
| 10 | **Saitou** | Lobo de Mibu (Gatotsu) | 105 | 141 | 18 | **39.8%** | C (Desfavorecido / Técnico) |
| 11 | **Anne** | Espadachim (Alfanje 180°) | 85 | 165 | 14 | **32.2%** | C (Desfavorecido / Técnico) |
| 12 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 40 | 208 | 16 | **15.2%** | D (Underpowered / Crítico) |

## 2. Comparativo de Desempenho por Cenário (Bambu vs Kyoto)
Impacto do layout (área aberta e reflexiva do lago vs via estreita de Kyoto com perigo ativo de carruagens e escombros):

| Rank | Lutador | Winrate Geral | Winrate Bambu | Winrate Kyoto | Impacto Kyoto vs Bambu |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | **Teppo** | **71.6%** | 73.5% | 69.7% | -3.8% |
| 2 | **Tomoe** | **59.1%** | 61.4% | 56.8% | -4.5% |
| 3 | **Joe** | **58.0%** | 62.1% | 53.8% | -8.3% |
| 4 | **Murasaki** | **53.0%** | 52.3% | 53.8% | +1.5% |
| 5 | **Julie** | **53.0%** | 62.9% | 43.2% | -19.7% |
| 6 | **Musashi** | **51.9%** | 56.8% | 47.0% | -9.9% |
| 7 | **Kasumi** | **47.0%** | 48.5% | 45.5% | -3.0% |
| 8 | **Hanzo** | **43.6%** | 46.2% | 40.9% | -5.3% |
| 9 | **Kenshin** | **41.3%** | 43.2% | 39.4% | -3.8% |
| 10 | **Saitou** | **39.8%** | 43.2% | 36.4% | -6.8% |
| 11 | **Anne** | **32.2%** | 31.8% | 32.6% | +0.8% |
| 12 | **Okuni** | **15.2%** | 17.4% | 12.9% | -4.5% |

## 3. Matriz de Confrontos Head-to-Head (H2H 12x12)
A tabela exibe a taxa percentual de vitórias da linha contra a coluna nas 24 lutas disputadas (12 em cada arena):

| Lutador | Kenshi | Musash | Hanzo | Joe | Saitou | Teppo | Murasa | Kasumi | Okuni | Tomoe | Anne | Julie |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 17% | 54% | 50% | 46% | 17% | 33% | 54% | 62% | 12% | 67% | 42% |
| **Musashi** | 83% | — | 17% | 17% | 50% | 33% | 25% | 92% | 75% | 25% | 79% | 75% |
| **Hanzo** | 33% | 83% | — | 21% | 38% | 25% | 38% | 33% | 67% | 50% | 54% | 38% |
| **Joe** | 50% | 75% | 58% | — | 62% | 29% | 71% | 38% | 79% | 38% | 88% | 50% |
| **Saitou** | 33% | 25% | 58% | 33% | — | 17% | 29% | 29% | 71% | 38% | 62% | 42% |
| **Teppo** | 83% | 54% | 75% | 71% | 83% | — | 79% | 71% | 92% | 58% | 75% | 46% |
| **Murasaki** | 62% | 62% | 62% | 29% | 71% | 12% | — | 54% | 83% | 42% | 54% | 50% |
| **Kasumi** | 46% | 4% | 67% | 58% | 71% | 29% | 42% | — | 96% | 38% | 46% | 21% |
| **Okuni** | 21% | 12% | 21% | 21% | 25% | 4% | 8% | 0% | — | 12% | 29% | 12% |
| **Tomoe** | 71% | 71% | 46% | 58% | 58% | 42% | 33% | 54% | 88% | — | 71% | 58% |
| **Anne** | 21% | 21% | 38% | 8% | 33% | 21% | 46% | 50% | 67% | 21% | — | 29% |
| **Julie** | 58% | 17% | 58% | 50% | 50% | 46% | 46% | 71% | 88% | 38% | 62% | — |

## 4. Resultado do Algoritmo Merge Sort de Duelos
O Merge Sort executou uma ordenação por divisão e conquista onde cada decisão de precedência foi arbitrada pelo retrospecto direto de combates:

1. **Teppo** — Winrate Geral: 71.6% (189V / 66D / 9E)
2. **Joe** — Winrate Geral: 58.0% (153V / 100D / 11E)
3. **Murasaki** — Winrate Geral: 53.0% (140V / 108D / 16E)
4. **Tomoe** — Winrate Geral: 59.1% (156V / 89D / 19E)
5. **Julie** — Winrate Geral: 53.0% (140V / 111D / 13E)
6. **Kenshin** — Winrate Geral: 41.3% (109V / 135D / 20E)
7. **Saitou** — Winrate Geral: 39.8% (105V / 141D / 18E)
8. **Hanzo** — Winrate Geral: 43.6% (115V / 133D / 16E)
9. **Musashi** — Winrate Geral: 51.9% (137V / 106D / 21E)
10. **Anne** — Winrate Geral: 32.2% (85V / 165D / 14E)
11. **Kasumi** — Winrate Geral: 47.0% (124V / 131D / 9E)
12. **Okuni** — Winrate Geral: 15.2% (40V / 208D / 16E)

## 5. Avaliação Técnica Aprofundada do Balanceamento

### 5.1 Opressão e Dominância (Top Tiers)
- **Teppo (71.6%) & Tomoe (59.1%)**:
  - As mecânicas de ataque com prioridade/precedência absoluta, alcance de projéteis instantâneos (snipers) ou frames defensivos de Parry/Riposte garantem uma taxa de vitória esmagadora contra lutadores de aproximação pura.

### 5.2 Vulnerabilidades Críticas (Bottom Tiers)
- **Okuni (15.2%) & Anne (32.2%)**:
  - Lutadores que dependem de tempos longos de recarga parada (ex: recarga do arcabuz sem cobertura móvel), auto-dano/suicídio por fogo amigo de explosivos, ou windup de retesamento de arco sofrem punições instantâneas contra oponentes rápidos.

### 5.3 Dinâmica de Pedra-Papel-Tesoura e Polarização Extrema
Foram detectados confrontos com polarização extrema (>= 87% de vitória para um lado):
- **Musashi vs Kasumi**: Placar esmagador de 22 a 1 (91.7% de dominância)
- **Joe vs Anne**: Placar esmagador de 21 a 2 (87.5% de dominância)
- **Teppo vs Okuni**: Placar esmagador de 22 a 1 (91.7% de dominância)
- **Kasumi vs Okuni**: Placar esmagador de 23 a 0 (95.8% de dominância)
- **Tomoe vs Okuni**: Placar esmagador de 21 a 3 (87.5% de dominância)
- **Julie vs Okuni**: Placar esmagador de 21 a 3 (87.5% de dominância)

## 6. Propostas Concretas de Balance Patch (Recomendações de Design)
Para equalizar o elenco e aproximar todos os combatentes da faixa saudável de 45% a 55% de winrate:
1. **Ajuste de Precedência e Cooldowns de Projéteis**: Aumentar ligeiramente o recovery de golpes com prioridade e projéteis rápidos.
2. **Mobilidade durante a Recarga**: Permitir que classes que recarregam mantenham movimentação a 50% da velocidade, evitando vulnerabilidade estática total.
3. **Redução de Fogo Amigo**: Diminuir o raio de explosão auto-infligido para armas de área (como bombas).
4. **Janela de Defesa (Parry/Riposte)**: Ajustar a janela de parry para exigir timing mais preciso contra sequências rápidas.
