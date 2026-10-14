# Relatório Detalhado de Balanceamento & Merge Sort de Duelos Simulados

> **Métricas Globais da Simulação**:
> - Dificuldade da IA (ambos os lutadores): **EASY**
> - Total de Guerreiros Avaliados: 12
> - Combinações Únicas de Duelos: 66 confrontos $\binom{12}{2}$
> - Volume de Lutas por Combinação: 24 batalhas simétricas (12 com P1/P2 alternados)
> - **Volume Total de Batalhas Simuladas**: **1584 batalhas**
> - Tempo Total de Simulação Física: 6.82 segundos (232.3 lutas/segundo)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Julie** | Mosqueteira (Florete/Riposte) | 167 | 86 | 11 | **63.3%** | A (Forte / Vantajoso) |
| 2 | **Teppo** | Marksman (Tanegashima/Pólvora) | 157 | 88 | 19 | **59.5%** | A (Forte / Vantajoso) |
| 3 | **Kenshin** | Retalhador (Iai/Shukuchi) | 148 | 93 | 23 | **56.1%** | A (Forte / Vantajoso) |
| 4 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 143 | 114 | 7 | **54.2%** | B (Balanceado / Saudável) |
| 5 | **Saitou** | Lobo de Mibu (Gatotsu) | 137 | 110 | 17 | **51.9%** | B (Balanceado / Saudável) |
| 6 | **Murasaki** | Kunoichi Foice (Kusarigama) | 136 | 119 | 9 | **51.5%** | B (Balanceado / Saudável) |
| 7 | **Tomoe** | Arqueira Miko (Arco Yumi) | 135 | 113 | 16 | **51.1%** | B (Balanceado / Saudável) |
| 8 | **Joe** | American Ninja (Shuriken/Cão) | 125 | 126 | 13 | **47.4%** | B (Balanceado / Saudável) |
| 9 | **Anne** | Espadachim (Alfanje 180°) | 115 | 137 | 12 | **43.6%** | C (Desfavorecido / Técnico) |
| 10 | **Hanzo** | Ninja Mestre (Kunai) | 94 | 152 | 18 | **35.6%** | C (Desfavorecido / Técnico) |
| 11 | **Musashi** | Duas Lâminas (Combo/Parry) | 74 | 179 | 11 | **28.0%** | D (Underpowered / Crítico) |
| 12 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 67 | 181 | 16 | **25.4%** | D (Underpowered / Crítico) |

## 2. Comparativo de Desempenho por Cenário (Bambu vs Kyoto)
Impacto do layout (área aberta e reflexiva do lago vs via estreita de Kyoto com perigo ativo de carruagens e escombros):

| Rank | Lutador | Winrate Geral | Winrate Bambu | Winrate Kyoto | Impacto Kyoto vs Bambu |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | **Julie** | **63.3%** | 67.4% | 59.1% | -8.3% |
| 2 | **Teppo** | **59.5%** | 64.4% | 54.5% | -9.8% |
| 3 | **Kenshin** | **56.1%** | 65.9% | 46.2% | -19.7% |
| 4 | **Kasumi** | **54.2%** | 56.1% | 52.3% | -3.8% |
| 5 | **Saitou** | **51.9%** | 53.0% | 50.8% | -2.3% |
| 6 | **Murasaki** | **51.5%** | 53.8% | 49.2% | -4.5% |
| 7 | **Tomoe** | **51.1%** | 44.7% | 57.6% | +12.9% |
| 8 | **Joe** | **47.4%** | 50.0% | 44.7% | -5.3% |
| 9 | **Anne** | **43.6%** | 47.0% | 40.1% | -6.8% |
| 10 | **Hanzo** | **35.6%** | 41.7% | 29.6% | -12.1% |
| 11 | **Musashi** | **28.0%** | 29.6% | 26.5% | -3.0% |
| 12 | **Okuni** | **25.4%** | 26.5% | 24.2% | -2.3% |

## 3. Matriz de Confrontos Head-to-Head (H2H 12x12)
A tabela exibe a taxa percentual de vitórias da linha contra a coluna nas 24 lutas disputadas (12 em cada arena):

| Lutador | Kenshi | Musash | Hanzo | Joe | Saitou | Teppo | Murasa | Kasumi | Okuni | Tomoe | Anne | Julie |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 67% | 54% | 42% | 50% | 58% | 58% | 50% | 71% | 62% | 67% | 38% |
| **Musashi** | 25% | — | 38% | 38% | 25% | 25% | 21% | 21% | 50% | 21% | 38% | 8% |
| **Hanzo** | 25% | 58% | — | 38% | 46% | 25% | 38% | 29% | 38% | 21% | 42% | 33% |
| **Joe** | 50% | 54% | 58% | — | 33% | 33% | 50% | 42% | 62% | 54% | 54% | 29% |
| **Saitou** | 38% | 75% | 46% | 67% | — | 33% | 46% | 42% | 79% | 46% | 62% | 38% |
| **Teppo** | 38% | 71% | 67% | 62% | 58% | — | 71% | 50% | 75% | 46% | 67% | 50% |
| **Murasaki** | 38% | 79% | 62% | 38% | 46% | 25% | — | 54% | 79% | 54% | 50% | 42% |
| **Kasumi** | 46% | 75% | 67% | 58% | 54% | 38% | 46% | — | 75% | 50% | 38% | 50% |
| **Okuni** | 21% | 46% | 50% | 33% | 21% | 8% | 17% | 25% | — | 21% | 29% | 8% |
| **Tomoe** | 25% | 75% | 79% | 38% | 46% | 46% | 46% | 50% | 71% | — | 50% | 38% |
| **Anne** | 25% | 58% | 50% | 42% | 25% | 33% | 46% | 62% | 67% | 46% | — | 25% |
| **Julie** | 58% | 88% | 62% | 71% | 54% | 42% | 58% | 50% | 88% | 50% | 75% | — |

## 4. Resultado do Algoritmo Merge Sort de Duelos
O Merge Sort executou uma ordenação por divisão e conquista onde cada decisão de precedência foi arbitrada pelo retrospecto direto de combates:

1. **Julie** — Winrate Geral: 63.3% (167V / 86D / 11E)
2. **Kenshin** — Winrate Geral: 56.1% (148V / 93D / 23E)
3. **Teppo** — Winrate Geral: 59.5% (157V / 88D / 19E)
4. **Saitou** — Winrate Geral: 51.9% (137V / 110D / 17E)
5. **Joe** — Winrate Geral: 47.4% (125V / 126D / 13E)
6. **Murasaki** — Winrate Geral: 51.5% (136V / 119D / 9E)
7. **Kasumi** — Winrate Geral: 54.2% (143V / 114D / 7E)
8. **Tomoe** — Winrate Geral: 51.1% (135V / 113D / 16E)
9. **Anne** — Winrate Geral: 43.6% (115V / 137D / 12E)
10. **Okuni** — Winrate Geral: 25.4% (67V / 181D / 16E)
11. **Hanzo** — Winrate Geral: 35.6% (94V / 152D / 18E)
12. **Musashi** — Winrate Geral: 28.0% (74V / 179D / 11E)

## 5. Avaliação Técnica Aprofundada do Balanceamento

### 5.1 Opressão e Dominância (Top Tiers)
- **Julie (63.3%) & Teppo (59.5%)**:
  - As mecânicas de ataque com prioridade/precedência absoluta, alcance de projéteis instantâneos (snipers) ou frames defensivos de Parry/Riposte garantem uma taxa de vitória esmagadora contra lutadores de aproximação pura.

### 5.2 Vulnerabilidades Críticas (Bottom Tiers)
- **Okuni (25.4%) & Musashi (28.0%)**:
  - Lutadores que dependem de tempos longos de recarga parada (ex: recarga do arcabuz sem cobertura móvel), auto-dano/suicídio por fogo amigo de explosivos, ou windup de retesamento de arco sofrem punições instantâneas contra oponentes rápidos.

### 5.3 Dinâmica de Pedra-Papel-Tesoura e Polarização Extrema
Foram detectados confrontos com polarização extrema (>= 87% de vitória para um lado):
- **Julie vs Musashi**: Placar esmagador de 21 a 2 (87.5% de dominância)
- **Julie vs Okuni**: Placar esmagador de 21 a 2 (87.5% de dominância)

## 6. Propostas Concretas de Balance Patch (Recomendações de Design)
Para equalizar o elenco e aproximar todos os combatentes da faixa saudável de 45% a 55% de winrate:
1. **Ajuste de Precedência e Cooldowns de Projéteis**: Aumentar ligeiramente o recovery de golpes com prioridade e projéteis rápidos.
2. **Mobilidade durante a Recarga**: Permitir que classes que recarregam mantenham movimentação a 50% da velocidade, evitando vulnerabilidade estática total.
3. **Redução de Fogo Amigo**: Diminuir o raio de explosão auto-infligido para armas de área (como bombas).
4. **Janela de Defesa (Parry/Riposte)**: Ajustar a janela de parry para exigir timing mais preciso contra sequências rápidas.
