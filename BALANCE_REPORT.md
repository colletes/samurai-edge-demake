# Relatório Detalhado de Balanceamento & Merge Sort de Duelos Simulados

> **Métricas Globais da Simulação**:
> - Dificuldade da IA (ambos os lutadores): **NORMAL**
> - Total de Guerreiros Avaliados: 12
> - Combinações Únicas de Duelos: 66 confrontos $\binom{12}{2}$
> - Volume de Lutas por Combinação: 24 batalhas simétricas (12 com P1/P2 alternados)
> - **Volume Total de Batalhas Simuladas**: **2184 batalhas**
> - Tempo Total de Simulação Física: 10.51 segundos (207.8 lutas/segundo)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Teppo** | Marksman (Tanegashima/Pólvora) | 211 | 87 | 14 | **67.6%** | A (Forte / Vantajoso) |
| 2 | **Joe** | American Ninja (Shuriken/Cão) | 202 | 104 | 6 | **64.7%** | A (Forte / Vantajoso) |
| 3 | **Tomoe** | Arqueira Miko (Arco Yumi) | 201 | 95 | 16 | **64.4%** | A (Forte / Vantajoso) |
| 4 | **Julie** | Mosqueteira (Florete/Riposte) | 174 | 124 | 14 | **55.8%** | A (Forte / Vantajoso) |
| 5 | **Hanzo** | Ninja Mestre (Kunai) | 167 | 136 | 9 | **53.5%** | B (Balanceado / Saudável) |
| 6 | **Murasaki** | Kunoichi Foice (Kusarigama) | 164 | 128 | 20 | **52.6%** | B (Balanceado / Saudável) |
| 7 | **Anne** | Espadachim (Alfanje 180°) | 146 | 151 | 15 | **46.8%** | B (Balanceado / Saudável) |
| 8 | **Musashi** | Duas Lâminas (Combo/Parry) | 139 | 154 | 19 | **44.5%** | C (Desfavorecido / Técnico) |
| 9 | **Kenshin** | Retalhador (Iai/Shukuchi) | 130 | 155 | 27 | **41.7%** | C (Desfavorecido / Técnico) |
| 10 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 128 | 171 | 13 | **41.0%** | C (Desfavorecido / Técnico) |
| 11 | **Saitou** | Lobo de Mibu (Gatotsu) | 116 | 178 | 18 | **37.2%** | C (Desfavorecido / Técnico) |
| 12 | **Chiyo** | Lâminas Gêmeas (Dual Nodachi) | 113 | 178 | 21 | **36.2%** | C (Desfavorecido / Técnico) |
| 13 | **Ren** | Monge Shaolin (Kiai/Flurry) | 109 | 187 | 16 | **34.9%** | C (Desfavorecido / Técnico) |
| 14 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 68 | 220 | 24 | **21.8%** | D (Underpowered / Crítico) |

## 2. Comparativo de Desempenho por Cenário (Bambu vs Kyoto)
Impacto do layout (área aberta e reflexiva do lago vs via estreita de Kyoto com perigo ativo de carruagens e escombros):

| Rank | Lutador | Winrate Geral | Winrate Bambu | Winrate Kyoto | Impacto Kyoto vs Bambu |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | **Teppo** | **67.6%** | 70.5% | 64.7% | -5.8% |
| 2 | **Joe** | **64.7%** | 69.9% | 59.6% | -10.3% |
| 3 | **Tomoe** | **64.4%** | 62.8% | 66.0% | +3.2% |
| 4 | **Julie** | **55.8%** | 60.3% | 51.3% | -9.0% |
| 5 | **Hanzo** | **53.5%** | 55.1% | 51.9% | -3.2% |
| 6 | **Murasaki** | **52.6%** | 59.6% | 45.5% | -14.1% |
| 7 | **Anne** | **46.8%** | 50.0% | 43.6% | -6.4% |
| 8 | **Musashi** | **44.5%** | 47.4% | 41.7% | -5.8% |
| 9 | **Kenshin** | **41.7%** | 42.3% | 41.0% | -1.3% |
| 10 | **Kasumi** | **41.0%** | 47.4% | 34.6% | -12.8% |
| 11 | **Saitou** | **37.2%** | 39.7% | 34.6% | -5.1% |
| 12 | **Chiyo** | **36.2%** | 36.5% | 35.9% | -0.6% |
| 13 | **Ren** | **34.9%** | 32.7% | 37.2% | +4.5% |
| 14 | **Okuni** | **21.8%** | 25.6% | 17.9% | -7.7% |

## 3. Matriz de Confrontos Head-to-Head (H2H 12x12)
A tabela exibe a taxa percentual de vitórias da linha contra a coluna nas 24 lutas disputadas (12 em cada arena):

| Lutador | Kenshi | Musash | Hanzo | Joe | Saitou | Teppo | Murasa | Kasumi | Okuni | Tomoe | Anne | Julie | Ren | Chiyo |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 8% | 33% | 33% | 58% | 54% | 29% | 67% | 62% | 33% | 54% | 21% | 42% | 46% |
| **Musashi** | 83% | — | 12% | 21% | 83% | 38% | 12% | 62% | 58% | 29% | 33% | 42% | 50% | 54% |
| **Hanzo** | 58% | 83% | — | 29% | 54% | 33% | 42% | 54% | 71% | 25% | 46% | 50% | 83% | 67% |
| **Joe** | 67% | 75% | 71% | — | 67% | 38% | 71% | 62% | 83% | 42% | 71% | 67% | 58% | 71% |
| **Saitou** | 29% | 4% | 42% | 33% | — | 29% | 33% | 42% | 71% | 17% | 33% | 29% | 67% | 54% |
| **Teppo** | 33% | 54% | 67% | 58% | 67% | — | 50% | 92% | 83% | 67% | 83% | 62% | 79% | 83% |
| **Murasaki** | 67% | 83% | 54% | 29% | 67% | 46% | — | 58% | 62% | 42% | 0% | 38% | 62% | 75% |
| **Kasumi** | 25% | 25% | 46% | 38% | 54% | 8% | 38% | — | 75% | 42% | 62% | 21% | 62% | 38% |
| **Okuni** | 25% | 33% | 29% | 17% | 17% | 8% | 17% | 21% | — | 8% | 29% | 25% | 29% | 25% |
| **Tomoe** | 50% | 67% | 71% | 54% | 75% | 33% | 54% | 58% | 92% | — | 58% | 71% | 83% | 71% |
| **Anne** | 42% | 58% | 54% | 29% | 62% | 12% | 88% | 38% | 62% | 29% | — | 25% | 54% | 54% |
| **Julie** | 79% | 54% | 42% | 33% | 67% | 33% | 58% | 75% | 75% | 25% | 71% | — | 67% | 46% |
| **Ren** | 50% | 50% | 12% | 33% | 33% | 17% | 29% | 29% | 54% | 12% | 46% | 29% | — | 58% |
| **Chiyo** | 38% | 46% | 33% | 25% | 38% | 12% | 12% | 54% | 67% | 25% | 42% | 38% | 42% | — |

## 4. Resultado do Algoritmo Merge Sort de Duelos
O Merge Sort executou uma ordenação por divisão e conquista onde cada decisão de precedência foi arbitrada pelo retrospecto direto de combates:

1. **Teppo** — Winrate Geral: 67.6% (211V / 87D / 14E)
2. **Tomoe** — Winrate Geral: 64.4% (201V / 95D / 16E)
3. **Joe** — Winrate Geral: 64.7% (202V / 104D / 6E)
4. **Julie** — Winrate Geral: 55.8% (174V / 124D / 14E)
5. **Murasaki** — Winrate Geral: 52.6% (164V / 128D / 20E)
6. **Hanzo** — Winrate Geral: 53.5% (167V / 136D / 9E)
7. **Musashi** — Winrate Geral: 44.5% (139V / 154D / 19E)
8. **Kenshin** — Winrate Geral: 41.7% (130V / 155D / 27E)
9. **Kasumi** — Winrate Geral: 41.0% (128V / 171D / 13E)
10. **Anne** — Winrate Geral: 46.8% (146V / 151D / 15E)
11. **Saitou** — Winrate Geral: 37.2% (116V / 178D / 18E)
12. **Ren** — Winrate Geral: 34.9% (109V / 187D / 16E)
13. **Chiyo** — Winrate Geral: 36.2% (113V / 178D / 21E)
14. **Okuni** — Winrate Geral: 21.8% (68V / 220D / 24E)

## 5. Avaliação Técnica Aprofundada do Balanceamento

### 5.1 Opressão e Dominância (Top Tiers)
- **Teppo (67.6%) & Joe (64.7%)**:
  - As mecânicas de ataque com prioridade/precedência absoluta, alcance de projéteis instantâneos (snipers) ou frames defensivos de Parry/Riposte garantem uma taxa de vitória esmagadora contra lutadores de aproximação pura.

### 5.2 Vulnerabilidades Críticas (Bottom Tiers)
- **Okuni (21.8%) & Ren (34.9%)**:
  - Lutadores que dependem de tempos longos de recarga parada (ex: recarga do arcabuz sem cobertura móvel), auto-dano/suicídio por fogo amigo de explosivos, ou windup de retesamento de arco sofrem punições instantâneas contra oponentes rápidos.

### 5.3 Dinâmica de Pedra-Papel-Tesoura e Polarização Extrema
Foram detectados confrontos com polarização extrema (>= 87% de vitória para um lado):
- **Teppo vs Kasumi**: Placar esmagador de 22 a 2 (91.7% de dominância)
- **Anne vs Murasaki**: Placar esmagador de 21 a 0 (87.5% de dominância)
- **Tomoe vs Okuni**: Placar esmagador de 22 a 2 (91.7% de dominância)

## 6. Propostas Concretas de Balance Patch (Recomendações de Design)
Para equalizar o elenco e aproximar todos os combatentes da faixa saudável de 45% a 55% de winrate:
1. **Ajuste de Precedência e Cooldowns de Projéteis**: Aumentar ligeiramente o recovery de golpes com prioridade e projéteis rápidos.
2. **Mobilidade durante a Recarga**: Permitir que classes que recarregam mantenham movimentação a 50% da velocidade, evitando vulnerabilidade estática total.
3. **Redução de Fogo Amigo**: Diminuir o raio de explosão auto-infligido para armas de área (como bombas).
4. **Janela de Defesa (Parry/Riposte)**: Ajustar a janela de parry para exigir timing mais preciso contra sequências rápidas.
