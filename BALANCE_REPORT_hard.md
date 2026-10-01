# Relatório Detalhado de Balanceamento & Merge Sort de Duelos Simulados

> **Métricas Globais da Simulação**:
> - Dificuldade da IA (ambos os lutadores): **HARD**
> - Total de Guerreiros Avaliados: 12
> - Combinações Únicas de Duelos: 66 confrontos $\binom{12}{2}$
> - Volume de Lutas por Combinação: 24 batalhas simétricas (12 com P1/P2 alternados)
> - **Volume Total de Batalhas Simuladas**: **1584 batalhas**
> - Tempo Total de Simulação Física: 6.05 segundos (261.8 lutas/segundo)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Teppo** | Marksman (Tanegashima/Pólvora) | 221 | 35 | 8 | **83.7%** | S (Top Tier - Opressivo) |
| 2 | **Tomoe** | Arqueira Miko (Arco Yumi) | 190 | 67 | 7 | **72.0%** | S (Top Tier - Opressivo) |
| 3 | **Joe** | American Ninja (Shuriken/Cão) | 169 | 86 | 9 | **64.0%** | A (Forte / Vantajoso) |
| 4 | **Julie** | Mosqueteira (Florete/Riposte) | 147 | 102 | 15 | **55.7%** | A (Forte / Vantajoso) |
| 5 | **Kenshin** | Retalhador (Iai/Shukuchi) | 127 | 123 | 14 | **48.1%** | B (Balanceado / Saudável) |
| 6 | **Murasaki** | Kunoichi Foice (Kusarigama) | 126 | 131 | 7 | **47.7%** | B (Balanceado / Saudável) |
| 7 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 126 | 129 | 9 | **47.7%** | B (Balanceado / Saudável) |
| 8 | **Saitou** | Lobo de Mibu (Gatotsu) | 124 | 132 | 8 | **47.0%** | B (Balanceado / Saudável) |
| 9 | **Hanzo** | Ninja Mestre (Kunai) | 111 | 147 | 6 | **42.0%** | C (Desfavorecido / Técnico) |
| 10 | **Anne** | Espadachim (Alfanje 180°) | 91 | 162 | 11 | **34.5%** | C (Desfavorecido / Técnico) |
| 11 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 46 | 203 | 15 | **17.4%** | D (Underpowered / Crítico) |
| 12 | **Musashi** | Duas Lâminas (Combo/Parry) | 44 | 205 | 15 | **16.7%** | D (Underpowered / Crítico) |

## 2. Comparativo de Desempenho por Cenário (Bambu vs Kyoto)
Impacto do layout (área aberta e reflexiva do lago vs via estreita de Kyoto com perigo ativo de carruagens e escombros):

| Rank | Lutador | Winrate Geral | Winrate Bambu | Winrate Kyoto | Impacto Kyoto vs Bambu |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | **Teppo** | **83.7%** | 84.1% | 83.3% | -0.8% |
| 2 | **Tomoe** | **72.0%** | 76.5% | 67.4% | -9.1% |
| 3 | **Joe** | **64.0%** | 71.2% | 56.8% | -14.4% |
| 4 | **Julie** | **55.7%** | 62.1% | 49.2% | -12.9% |
| 5 | **Kenshin** | **48.1%** | 49.2% | 47.0% | -2.3% |
| 6 | **Murasaki** | **47.7%** | 46.2% | 49.2% | +3.0% |
| 7 | **Kasumi** | **47.7%** | 51.5% | 43.9% | -7.6% |
| 8 | **Saitou** | **47.0%** | 47.0% | 47.0% | 0.0% |
| 9 | **Hanzo** | **42.0%** | 44.7% | 39.4% | -5.3% |
| 10 | **Anne** | **34.5%** | 34.9% | 34.1% | -0.8% |
| 11 | **Okuni** | **17.4%** | 15.2% | 19.7% | +4.5% |
| 12 | **Musashi** | **16.7%** | 17.4% | 15.9% | -1.5% |

## 3. Matriz de Confrontos Head-to-Head (H2H 12x12)
A tabela exibe a taxa percentual de vitórias da linha contra a coluna nas 24 lutas disputadas (12 em cada arena):

| Lutador | Kenshi | Musash | Hanzo | Joe | Saitou | Teppo | Murasa | Kasumi | Okuni | Tomoe | Anne | Julie |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 79% | 71% | 33% | 38% | 8% | 38% | 50% | 75% | 33% | 71% | 33% |
| **Musashi** | 17% | — | 33% | 8% | 8% | 0% | 17% | 8% | 42% | 8% | 33% | 8% |
| **Hanzo** | 29% | 67% | — | 25% | 50% | 4% | 42% | 50% | 62% | 33% | 67% | 33% |
| **Joe** | 67% | 88% | 67% | — | 67% | 33% | 62% | 71% | 79% | 33% | 79% | 58% |
| **Saitou** | 54% | 88% | 50% | 29% | — | 0% | 50% | 33% | 75% | 21% | 67% | 50% |
| **Teppo** | 88% | 96% | 96% | 62% | 100% | — | 88% | 71% | 100% | 54% | 88% | 79% |
| **Murasaki** | 62% | 79% | 58% | 38% | 50% | 4% | — | 58% | 88% | 17% | 38% | 33% |
| **Kasumi** | 46% | 83% | 50% | 29% | 67% | 25% | 42% | — | 71% | 29% | 50% | 33% |
| **Okuni** | 8% | 46% | 29% | 17% | 17% | 0% | 12% | 25% | — | 0% | 29% | 8% |
| **Tomoe** | 58% | 92% | 62% | 62% | 79% | 46% | 83% | 62% | 100% | — | 79% | 67% |
| **Anne** | 21% | 58% | 33% | 17% | 29% | 12% | 54% | 46% | 67% | 21% | — | 21% |
| **Julie** | 62% | 79% | 62% | 38% | 46% | 12% | 58% | 62% | 88% | 29% | 75% | — |

## 4. Resultado do Algoritmo Merge Sort de Duelos
O Merge Sort executou uma ordenação por divisão e conquista onde cada decisão de precedência foi arbitrada pelo retrospecto direto de combates:

1. **Teppo** — Winrate Geral: 83.7% (221V / 35D / 8E)
2. **Tomoe** — Winrate Geral: 72.0% (190V / 67D / 7E)
3. **Joe** — Winrate Geral: 64.0% (169V / 86D / 9E)
4. **Saitou** — Winrate Geral: 47.0% (124V / 132D / 8E)
5. **Julie** — Winrate Geral: 55.7% (147V / 102D / 15E)
6. **Kenshin** — Winrate Geral: 48.1% (127V / 123D / 14E)
7. **Hanzo** — Winrate Geral: 42.0% (111V / 147D / 6E)
8. **Anne** — Winrate Geral: 34.5% (91V / 162D / 11E)
9. **Murasaki** — Winrate Geral: 47.7% (126V / 131D / 7E)
10. **Kasumi** — Winrate Geral: 47.7% (126V / 129D / 9E)
11. **Okuni** — Winrate Geral: 17.4% (46V / 203D / 15E)
12. **Musashi** — Winrate Geral: 16.7% (44V / 205D / 15E)

## 5. Avaliação Técnica Aprofundada do Balanceamento

### 5.1 Opressão e Dominância (Top Tiers)
- **Teppo (83.7%) & Tomoe (72.0%)**:
  - As mecânicas de ataque com prioridade/precedência absoluta, alcance de projéteis instantâneos (snipers) ou frames defensivos de Parry/Riposte garantem uma taxa de vitória esmagadora contra lutadores de aproximação pura.

### 5.2 Vulnerabilidades Críticas (Bottom Tiers)
- **Musashi (16.7%) & Okuni (17.4%)**:
  - Lutadores que dependem de tempos longos de recarga parada (ex: recarga do arcabuz sem cobertura móvel), auto-dano/suicídio por fogo amigo de explosivos, ou windup de retesamento de arco sofrem punições instantâneas contra oponentes rápidos.

### 5.3 Dinâmica de Pedra-Papel-Tesoura e Polarização Extrema
Foram detectados confrontos com polarização extrema (>= 87% de vitória para um lado):
- **Teppo vs Kenshin**: Placar esmagador de 21 a 2 (87.5% de dominância)
- **Joe vs Musashi**: Placar esmagador de 21 a 2 (87.5% de dominância)
- **Saitou vs Musashi**: Placar esmagador de 21 a 2 (87.5% de dominância)
- **Teppo vs Musashi**: Placar esmagador de 23 a 0 (95.8% de dominância)
- **Tomoe vs Musashi**: Placar esmagador de 22 a 2 (91.7% de dominância)
- **Teppo vs Hanzo**: Placar esmagador de 23 a 1 (95.8% de dominância)
- **Teppo vs Saitou**: Placar esmagador de 24 a 0 (100.0% de dominância)
- **Teppo vs Murasaki**: Placar esmagador de 21 a 1 (87.5% de dominância)

## 6. Propostas Concretas de Balance Patch (Recomendações de Design)
Para equalizar o elenco e aproximar todos os combatentes da faixa saudável de 45% a 55% de winrate:
1. **Ajuste de Precedência e Cooldowns de Projéteis**: Aumentar ligeiramente o recovery de golpes com prioridade e projéteis rápidos.
2. **Mobilidade durante a Recarga**: Permitir que classes que recarregam mantenham movimentação a 50% da velocidade, evitando vulnerabilidade estática total.
3. **Redução de Fogo Amigo**: Diminuir o raio de explosão auto-infligido para armas de área (como bombas).
4. **Janela de Defesa (Parry/Riposte)**: Ajustar a janela de parry para exigir timing mais preciso contra sequências rápidas.
