# Relatório Detalhado de Balanceamento & Merge Sort de Duelos Simulados

> **Métricas Globais da Simulação**:
> - Total de Guerreiros Avaliados: 12
> - Combinações Únicas de Duelos: 66 confrontos $\binom{12}{2}$
> - Volume de Lutas por Combinação: 24 batalhas simétricas (12 com P1/P2 alternados)
> - **Volume Total de Batalhas Simuladas**: **1584 batalhas**
> - Tempo Total de Simulação Física: 8.33 segundos (190.2 lutas/segundo)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Anne** | Espadachim (Alfanje 180°) | 176 | 50 | 38 | **66.7%** | A (Forte / Vantajoso) |
| 2 | **Teppo** | Marksman (Tanegashima/Pólvora) | 153 | 67 | 44 | **58.0%** | A (Forte / Vantajoso) |
| 3 | **Julie** | Mosqueteira (Florete/Riposte) | 149 | 58 | 57 | **56.4%** | A (Forte / Vantajoso) |
| 4 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 128 | 69 | 67 | **48.5%** | B (Balanceado / Saudável) |
| 5 | **Tomoe** | Arqueira Miko (Arco Yumi) | 115 | 108 | 41 | **43.6%** | C (Desfavorecido / Técnico) |
| 6 | **Saitou** | Lobo de Mibu (Gatotsu) | 95 | 126 | 43 | **36.0%** | C (Desfavorecido / Técnico) |
| 7 | **Musashi** | Duas Lâminas (Combo/Parry) | 89 | 104 | 71 | **33.7%** | C (Desfavorecido / Técnico) |
| 8 | **Kenshin** | Retalhador (Iai/Shukuchi) | 78 | 127 | 59 | **29.6%** | D (Underpowered / Crítico) |
| 9 | **Murasaki** | Kunoichi Foice (Kusarigama) | 77 | 135 | 52 | **29.2%** | D (Underpowered / Crítico) |
| 10 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 75 | 140 | 49 | **28.4%** | D (Underpowered / Crítico) |
| 11 | **Hanzo** | Ninja Mestre (Kunai) | 71 | 141 | 52 | **26.9%** | D (Underpowered / Crítico) |
| 12 | **Joe** | American Ninja (Shuriken/Cão) | 63 | 144 | 57 | **23.9%** | D (Underpowered / Crítico) |

## 2. Comparativo de Desempenho por Cenário (Bambu vs Kyoto)
Impacto do layout (área aberta e reflexiva do lago vs via estreita de Kyoto com perigo ativo de carruagens e escombros):

| Rank | Lutador | Winrate Geral | Winrate Bambu | Winrate Kyoto | Impacto Kyoto vs Bambu |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | **Anne** | **66.7%** | 75.8% | 57.6% | -18.2% |
| 2 | **Teppo** | **58.0%** | 62.9% | 53.0% | -9.9% |
| 3 | **Julie** | **56.4%** | 77.3% | 35.6% | -41.7% |
| 4 | **Okuni** | **48.5%** | 65.9% | 31.1% | -34.8% |
| 5 | **Tomoe** | **43.6%** | 51.5% | 35.6% | -15.9% |
| 6 | **Saitou** | **36.0%** | 45.5% | 26.5% | -18.9% |
| 7 | **Musashi** | **33.7%** | 47.7% | 19.7% | -28.0% |
| 8 | **Kenshin** | **29.6%** | 37.1% | 22.0% | -15.1% |
| 9 | **Murasaki** | **29.2%** | 38.6% | 19.7% | -18.9% |
| 10 | **Kasumi** | **28.4%** | 34.9% | 22.0% | -12.9% |
| 11 | **Hanzo** | **26.9%** | 34.9% | 18.9% | -15.9% |
| 12 | **Joe** | **23.9%** | 26.5% | 21.2% | -5.3% |

## 3. Matriz de Confrontos Head-to-Head (H2H 12x12)
A tabela exibe a taxa percentual de vitórias da linha contra a coluna nas 24 lutas disputadas (12 em cada arena):

| Lutador | Kenshi | Musash | Hanzo | Joe | Saitou | Teppo | Murasa | Kasumi | Okuni | Tomoe | Anne | Julie |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 29% | 25% | 58% | 25% | 12% | 17% | 71% | 17% | 50% | 4% | 17% |
| **Musashi** | 46% | — | 50% | 50% | 0% | 29% | 62% | 8% | 33% | 42% | 0% | 50% |
| **Hanzo** | 58% | 4% | — | 25% | 38% | 17% | 25% | 46% | 8% | 29% | 38% | 8% |
| **Joe** | 17% | 25% | 54% | — | 54% | 12% | 38% | 21% | 21% | 4% | 8% | 8% |
| **Saitou** | 58% | 79% | 42% | 33% | — | 4% | 29% | 29% | 67% | 12% | 8% | 33% |
| **Teppo** | 75% | 29% | 75% | 71% | 88% | — | 75% | 88% | 21% | 75% | 25% | 17% |
| **Murasaki** | 54% | 8% | 54% | 38% | 54% | 8% | — | 46% | 0% | 25% | 12% | 21% |
| **Kasumi** | 8% | 71% | 38% | 62% | 42% | 8% | 38% | — | 8% | 29% | 8% | 0% |
| **Okuni** | 58% | 38% | 79% | 46% | 8% | 38% | 83% | 62% | — | 54% | 29% | 38% |
| **Tomoe** | 25% | 33% | 58% | 79% | 79% | 21% | 54% | 58% | 29% | — | 25% | 17% |
| **Anne** | 67% | 92% | 50% | 71% | 88% | 71% | 79% | 75% | 46% | 62% | — | 33% |
| **Julie** | 62% | 25% | 62% | 67% | 50% | 58% | 62% | 79% | 38% | 67% | 50% | — |

## 4. Resultado do Algoritmo Merge Sort de Duelos
O Merge Sort executou uma ordenação por divisão e conquista onde cada decisão de precedência foi arbitrada pelo retrospecto direto de combates:

1. **Julie** — Winrate Geral: 56.4% (149V / 58D / 57E)
2. **Anne** — Winrate Geral: 66.7% (176V / 50D / 38E)
3. **Okuni** — Winrate Geral: 48.5% (128V / 69D / 67E)
4. **Teppo** — Winrate Geral: 58.0% (153V / 67D / 44E)
5. **Musashi** — Winrate Geral: 33.7% (89V / 104D / 71E)
6. **Tomoe** — Winrate Geral: 43.6% (115V / 108D / 41E)
7. **Murasaki** — Winrate Geral: 29.2% (77V / 135D / 52E)
8. **Kasumi** — Winrate Geral: 28.4% (75V / 140D / 49E)
9. **Joe** — Winrate Geral: 23.9% (63V / 144D / 57E)
10. **Saitou** — Winrate Geral: 36.0% (95V / 126D / 43E)
11. **Hanzo** — Winrate Geral: 26.9% (71V / 141D / 52E)
12. **Kenshin** — Winrate Geral: 29.6% (78V / 127D / 59E)

## 5. Avaliação Técnica Aprofundada do Balanceamento

### 5.1 Opressão e Dominância (Top Tiers)
- **Anne (66.7%) & Teppo (58.0%)**:
  - As mecânicas de ataque com prioridade/precedência absoluta, alcance de projéteis instantâneos (snipers) ou frames defensivos de Parry/Riposte garantem uma taxa de vitória esmagadora contra lutadores de aproximação pura.

### 5.2 Vulnerabilidades Críticas (Bottom Tiers)
- **Joe (23.9%) & Hanzo (26.9%)**:
  - Lutadores que dependem de tempos longos de recarga parada (ex: recarga do arcabuz sem cobertura móvel), auto-dano/suicídio por fogo amigo de explosivos, ou windup de retesamento de arco sofrem punições instantâneas contra oponentes rápidos.

### 5.3 Dinâmica de Pedra-Papel-Tesoura e Polarização Extrema
Foram detectados confrontos com polarização extrema (>= 87% de vitória para um lado):
- **Anne vs Musashi**: Placar esmagador de 22 a 0 (91.7% de dominância)
- **Teppo vs Saitou**: Placar esmagador de 21 a 1 (87.5% de dominância)
- **Anne vs Saitou**: Placar esmagador de 21 a 2 (87.5% de dominância)
- **Teppo vs Kasumi**: Placar esmagador de 21 a 2 (87.5% de dominância)

## 6. Propostas Concretas de Balance Patch (Recomendações de Design)
Para equalizar o elenco e aproximar todos os combatentes da faixa saudável de 45% a 55% de winrate:
1. **Ajuste de Precedência e Cooldowns de Projéteis**: Aumentar ligeiramente o recovery de golpes com prioridade e projéteis rápidos.
2. **Mobilidade durante a Recarga**: Permitir que classes que recarregam mantenham movimentação a 50% da velocidade, evitando vulnerabilidade estática total.
3. **Redução de Fogo Amigo**: Diminuir o raio de explosão auto-infligido para armas de área (como bombas).
4. **Janela de Defesa (Parry/Riposte)**: Ajustar a janela de parry para exigir timing mais preciso contra sequências rápidas.
