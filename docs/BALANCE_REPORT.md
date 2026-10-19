# Relatório Detalhado de Balanceamento & Merge Sort de Duelos (NORMAL)

> **Métricas Globais da Simulação**:
> - Dificuldade da IA (ambos os lutadores): **NORMAL**
> - Total de Guerreiros Avaliados: **20**
> - Total de Arenas Avaliadas: **20** (Cobertura Integral do Jogo)
> - Combinações Únicas de Duelos: **190 confrontos** $\binom{20}{2}$
> - Lutas por Combinação: **40 batalhas** (2 por arena, paridade simétrica P1/P2)
> - **Volume Total de Batalhas Simuladas**: **7600 batalhas**
> - Tempo Total de Simulação Física: **78.08 segundos** (97.3 lutas/s)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Valerius** | Necromante Prussiano (Foice/Invocações) | 542 | 217 | 1 | **71.3%** | S (Dominante / Alta Vantagem) |
| 2 | **Seimei** | Onmyoji dos Talismãs (Ofuda/Selo Sagrado) | 536 | 196 | 28 | **70.5%** | S (Dominante / Alta Vantagem) |
| 3 | **Joe** | American Ninja (Shuriken/Cão) | 440 | 319 | 1 | **57.9%** | A (Forte / Vantajoso) |
| 4 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 430 | 327 | 3 | **56.6%** | A (Forte / Vantajoso) |
| 5 | **Murasaki** | Kunoichi Foice (Kusarigama) | 427 | 332 | 1 | **56.2%** | A (Forte / Vantajoso) |
| 6 | **Tomoe** | Arqueira Miko (Arco Yumi) | 418 | 342 | 0 | **55.0%** | A (Forte / Vantajoso) |
| 7 | **Julie** | Mosqueteira (Florete/Riposte) | 417 | 342 | 1 | **54.9%** | A (Forte / Vantajoso) |
| 8 | **Musashi** | Duas Lâminas (Combo/Parry) | 407 | 351 | 2 | **53.5%** | A (Forte / Vantajoso) |
| 9 | **Anne** | Espadachim (Alfanje 180°) | 389 | 370 | 1 | **51.2%** | B (Balanceado / Saudável) |
| 10 | **Ichi** | Lâmina Cega (Shikomizue/Gyaku-Iai) | 382 | 374 | 4 | **50.3%** | B (Balanceado / Saudável) |
| 11 | **O-Rin** | Menestrel Acústica (Shamisen/Kamaitachi) | 374 | 358 | 28 | **49.2%** | B (Balanceado / Saudável) |
| 12 | **Hanzo** | Ninja Mestre (Kunai) | 360 | 400 | 0 | **47.4%** | B (Balanceado / Saudável) |
| 13 | **Benkei** | Sōhei Monge Guerreiro (Naginata Colossal) | 343 | 405 | 12 | **45.1%** | C (Desfavorecido / Técnico) |
| 14 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 342 | 417 | 1 | **45.0%** | C (Desfavorecido / Técnico) |
| 15 | **Goro** | Fazendeiro da Kuwa (Kuwa Cleave/Pisotão) | 302 | 458 | 0 | **39.7%** | D (Crítico / Sob Investigação) |
| 16 | **Kenshin** | Retalhador (Iai/Shukuchi) | 292 | 461 | 7 | **38.4%** | D (Crítico / Sob Investigação) |
| 17 | **Ren** | Monge Shaolin (Kiai/Flurry) | 292 | 465 | 3 | **38.4%** | D (Crítico / Sob Investigação) |
| 18 | **Saitou** | Lobo de Mibu (Gatotsu) | 289 | 470 | 1 | **38.0%** | D (Crítico / Sob Investigação) |
| 19 | **Chiyo** | Lâminas Gêmeas (Dual Nodachi) | 287 | 468 | 5 | **37.8%** | D (Crítico / Sob Investigação) |
| 20 | **Teppo** | Marksman (Tanegashima/Pólvora) | 281 | 478 | 1 | **37.0%** | D (Crítico / Sob Investigação) |

## 2. Desempenho por Arena & Variância Geográfica
Identificação das arenas de maior e menor eficácia para cada combatente (impacto de fossos, obstáculos, projéteis e perigos de fase):

| Rank | Lutador | Winrate Geral | Melhor Arena | WR Max | Pior Arena | WR Min | Dispersão |
|:---:|:---|:---:|:---|:---:|:---|:---:|:---:|
| 1 | **Valerius** | **71.3%** | Kyoto: Bakumatsu em Chamas | 81.6% | Floresta de Bambu | 60.5% | 21.0% |
| 2 | **Seimei** | **70.5%** | Cemitério Gótico | 86.8% | Telhados de Iga | 52.6% | 34.2% |
| 3 | **Joe** | **57.9%** | Kyoto: Bakumatsu em Chamas | 68.4% | Jardim dos Lírios Carmim | 44.7% | 23.7% |
| 4 | **Kasumi** | **56.6%** | Cemitério Gótico | 68.4% | Convés na Tempestade | 42.1% | 26.3% |
| 5 | **Murasaki** | **56.2%** | Telhados de Iga | 63.2% | Jardim dos Lírios Carmim | 44.7% | 18.4% |
| 6 | **Tomoe** | **55.0%** | Convés na Tempestade | 68.4% | Kyoto: Bakumatsu em Chamas | 42.1% | 26.3% |
| 7 | **Julie** | **54.9%** | Gruta das Sombras | 71.0% | Pavilhão Astral Heian | 39.5% | 31.6% |
| 8 | **Musashi** | **53.5%** | Pavilhão Astral Heian | 65.8% | Templo na Névoa | 39.5% | 26.3% |
| 9 | **Anne** | **51.2%** | Beco Yoshiwara | 60.5% | Cemitério Gótico | 34.2% | 26.3% |
| 10 | **Ichi** | **50.3%** | Convés na Tempestade | 63.2% | Kyoto: Bakumatsu em Chamas | 42.1% | 21.0% |
| 11 | **O-Rin** | **49.2%** | Moinho na Chuva | 71.0% | Kyoto: Bakumatsu em Chamas | 36.8% | 34.2% |
| 12 | **Hanzo** | **47.4%** | Acampamento na Floresta | 60.5% | Campo de Nagashino | 28.9% | 31.6% |
| 13 | **Benkei** | **45.1%** | Cemitério Gótico | 63.2% | Pátio Barroco | 21.1% | 42.1% |
| 14 | **Okuni** | **45.0%** | Convés na Tempestade | 57.9% | Floresta de Bambu | 28.9% | 28.9% |
| 15 | **Goro** | **39.7%** | Jardim dos Lírios Carmim | 52.6% | Palco Kabuki | 23.7% | 29.0% |
| 16 | **Kenshin** | **38.4%** | Floresta de Bambu | 55.3% | Arrozais Terraciados | 23.7% | 31.6% |
| 17 | **Ren** | **38.4%** | Cemitério Gótico | 50.0% | Pátio dos Sinos Shaolin | 26.3% | 23.7% |
| 18 | **Saitou** | **38.0%** | Gruta das Sombras | 50.0% | Pátio dos Sinos Shaolin | 23.7% | 26.3% |
| 19 | **Chiyo** | **37.8%** | Palco Kabuki | 50.0% | Ponte Gojo | 26.3% | 23.7% |
| 20 | **Teppo** | **37.0%** | Gruta das Sombras | 55.3% | Ilha de Ganryū | 26.3% | 28.9% |

## 3. Matriz de Confrontos Diretos Head-to-Head (20x20)
Percentual de vitórias da linha contra a coluna através de todas as 20 arenas:

| Lutador | Kensh | Musas | Hanzo | Joe | Saito | Teppo | Muras | Kasum | Okuni | Tomoe | Anne | Julie | Ren | Chiyo | Benke | O-Rin | Goro | Ichi | Valer | Seime |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 22% | 40% | 32% | 40% | 60% | 15% | 55% | 35% | 50% | 38% | 32% | 52% | 42% | 38% | 45% | 52% | 32% | 18% | 30% |
| **Musashi** | 78% | — | 22% | 30% | 90% | 80% | 12% | 72% | 50% | 50% | 52% | 40% | 95% | 62% | 80% | 32% | 65% | 48% | 15% | 42% |
| **Hanzo** | 60% | 78% | — | 35% | 50% | 57% | 52% | 28% | 57% | 50% | 68% | 38% | 42% | 45% | 38% | 50% | 42% | 60% | 15% | 35% |
| **Joe** | 68% | 70% | 65% | — | 60% | 82% | 72% | 38% | 60% | 45% | 65% | 55% | 55% | 85% | 60% | 60% | 60% | 55% | 20% | 25% |
| **Saitou** | 60% | 10% | 50% | 40% | — | 65% | 22% | 45% | 30% | 48% | 28% | 22% | 60% | 40% | 60% | 18% | 45% | 30% | 35% | 15% |
| **Teppo** | 40% | 20% | 42% | 18% | 35% | — | 50% | 32% | 52% | 32% | 50% | 35% | 42% | 45% | 32% | 52% | 38% | 32% | 15% | 38% |
| **Murasaki** | 85% | 88% | 48% | 28% | 78% | 50% | — | 42% | 62% | 40% | 5% | 52% | 80% | 82% | 45% | 62% | 90% | 72% | 30% | 28% |
| **Kasumi** | 45% | 28% | 72% | 62% | 55% | 68% | 57% | — | 78% | 48% | 62% | 28% | 70% | 72% | 32% | 68% | 80% | 52% | 72% | 25% |
| **Okuni** | 65% | 50% | 42% | 40% | 68% | 48% | 38% | 22% | — | 38% | 62% | 38% | 50% | 60% | 52% | 40% | 60% | 57% | 15% | 10% |
| **Tomoe** | 50% | 50% | 50% | 55% | 52% | 68% | 60% | 52% | 62% | — | 62% | 55% | 65% | 68% | 40% | 57% | 65% | 68% | 28% | 38% |
| **Anne** | 60% | 48% | 32% | 35% | 72% | 50% | 95% | 38% | 38% | 38% | — | 38% | 98% | 60% | 52% | 42% | 78% | 48% | 38% | 15% |
| **Julie** | 68% | 60% | 62% | 45% | 78% | 65% | 48% | 72% | 62% | 45% | 62% | — | 40% | 60% | 62% | 65% | 52% | 48% | 20% | 28% |
| **Ren** | 45% | 5% | 57% | 45% | 40% | 57% | 20% | 30% | 50% | 35% | 2% | 60% | — | 57% | 50% | 28% | 68% | 35% | 28% | 18% |
| **Chiyo** | 55% | 38% | 55% | 15% | 60% | 55% | 18% | 28% | 40% | 32% | 40% | 40% | 40% | — | 55% | 25% | 50% | 50% | 8% | 15% |
| **Benkei** | 57% | 20% | 62% | 40% | 40% | 65% | 55% | 68% | 48% | 60% | 48% | 35% | 48% | 38% | — | 52% | 42% | 42% | 20% | 18% |
| **O-Rin** | 52% | 65% | 50% | 40% | 82% | 48% | 38% | 32% | 60% | 42% | 57% | 35% | 72% | 75% | 42% | — | 45% | 57% | 35% | 5% |
| **Goro** | 48% | 35% | 57% | 40% | 55% | 62% | 10% | 20% | 40% | 35% | 22% | 48% | 32% | 50% | 57% | 55% | — | 22% | 38% | 28% |
| **Ichi** | 68% | 52% | 40% | 45% | 70% | 68% | 28% | 40% | 42% | 32% | 52% | 52% | 65% | 50% | 55% | 42% | 78% | — | 35% | 40% |
| **Valerius** | 82% | 82% | 85% | 80% | 65% | 85% | 70% | 28% | 85% | 72% | 62% | 80% | 72% | 92% | 80% | 65% | 62% | 65% | — | 40% |
| **Seimei** | 68% | 57% | 65% | 72% | 85% | 62% | 70% | 75% | 90% | 62% | 85% | 72% | 82% | 85% | 80% | 35% | 72% | 60% | 60% | — |

## 4. Classificação Oficial via Algoritmo Merge Sort
A ordenação por divisão e conquista arbitrou cada emparelhamento utilizando estritamente o retrospecto direto (Head-to-Head):

1. **Seimei** — Winrate Geral: 70.5% (536V / 196D / 28E)
2. **Valerius** — Winrate Geral: 71.3% (542V / 217D / 1E)
3. **Tomoe** — Winrate Geral: 55.0% (418V / 342D / 0E)
4. **Kasumi** — Winrate Geral: 56.6% (430V / 327D / 3E)
5. **Joe** — Winrate Geral: 57.9% (440V / 319D / 1E)
6. **Hanzo** — Winrate Geral: 47.4% (360V / 400D / 0E)
7. **Murasaki** — Winrate Geral: 56.2% (427V / 332D / 1E)
8. **Ichi** — Winrate Geral: 50.3% (382V / 374D / 4E)
9. **Musashi** — Winrate Geral: 53.5% (407V / 351D / 2E)
10. **Saitou** — Winrate Geral: 38.0% (289V / 470D / 1E)
11. **Kenshin** — Winrate Geral: 38.4% (292V / 461D / 7E)
12. **Ren** — Winrate Geral: 38.4% (292V / 465D / 3E)
13. **Julie** — Winrate Geral: 54.9% (417V / 342D / 1E)
14. **Anne** — Winrate Geral: 51.2% (389V / 370D / 1E)
15. **Goro** — Winrate Geral: 39.7% (302V / 458D / 0E)
16. **Teppo** — Winrate Geral: 37.0% (281V / 478D / 1E)
17. **O-Rin** — Winrate Geral: 49.2% (374V / 358D / 28E)
18. **Okuni** — Winrate Geral: 45.0% (342V / 417D / 1E)
19. **Chiyo** — Winrate Geral: 37.8% (287V / 468D / 5E)
20. **Benkei** — Winrate Geral: 45.1% (343V / 405D / 12E)

## 5. Análise Técnica dos Resultados

### 5.1 Domínio dos Top Tiers: **Valerius (71.3%)** e **Seimei (70.5%)**
- Combatentes com excelente alcance, precedência de ataque imediata ou cobertura por projéteis mantêm controle consistente do espaço mesmo em arenas com perigos complexos.

### 5.2 Desafios dos Bottom Tiers: **Teppo (37.0%)** e **Chiyo (37.8%)**
- Personagens que dependem de recarga estacionária, tiros com windup ou que possuem desvantagens contra assédio a longa distância sofrem mais em arenas abertas e com perigos móveis.

### 5.3 Confrontos com Polarização Extrema (>= 85% de dominância)
- **Murasaki vs Kenshin**: 34 a 6 (85.0% de dominância)
- **Musashi vs Saitou**: 36 a 4 (90.0% de dominância)
- **Murasaki vs Musashi**: 35 a 5 (87.5% de dominância)
- **Musashi vs Ren**: 38 a 2 (95.0% de dominância)
- **Valerius vs Hanzo**: 34 a 6 (85.0% de dominância)
- **Joe vs Chiyo**: 34 a 6 (85.0% de dominância)
- **Seimei vs Saitou**: 34 a 6 (85.0% de dominância)
- **Valerius vs Teppo**: 34 a 6 (85.0% de dominância)

## 6. Diretrizes e Recomendações de Balanceamento
1. **Normalização de Recovery**: Ajustar janelas de whiff para punição balanceada de ataques rápidos.
2. **Mobilidade Tática**: Preservar movimentação tática durante recargas para reduzir vulnerabilidade em arenas estreitas.
3. **Interação com Perigos**: Manter zonas neutras acessíveis em arenas com hazards telegrafados ativos.
