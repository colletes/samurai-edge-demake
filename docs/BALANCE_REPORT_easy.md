# Relatório Detalhado de Balanceamento & Merge Sort de Duelos (EASY)

> **Métricas Globais da Simulação**:
> - Dificuldade da IA (ambos os lutadores): **EASY**
> - Total de Guerreiros Avaliados: **20**
> - Total de Arenas Avaliadas: **20** (Cobertura Integral do Jogo)
> - Combinações Únicas de Duelos: **190 confrontos** $\binom{20}{2}$
> - Lutas por Combinação: **40 batalhas** (2 por arena, paridade simétrica P1/P2)
> - **Volume Total de Batalhas Simuladas**: **7600 batalhas**
> - Tempo Total de Simulação Física: **64.25 segundos** (118.3 lutas/s)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Valerius** | Necromante Prussiano (Foice/Invocações) | 564 | 194 | 2 | **74.2%** | S (Dominante / Alta Vantagem) |
| 2 | **Seimei** | Onmyoji dos Talismãs (Ofuda/Selo Sagrado) | 456 | 271 | 33 | **60.0%** | S (Dominante / Alta Vantagem) |
| 3 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 427 | 331 | 2 | **56.2%** | A (Forte / Vantajoso) |
| 4 | **Julie** | Mosqueteira (Florete/Riposte) | 423 | 337 | 0 | **55.7%** | A (Forte / Vantajoso) |
| 5 | **Musashi** | Duas Lâminas (Combo/Parry) | 404 | 354 | 2 | **53.2%** | A (Forte / Vantajoso) |
| 6 | **Anne** | Espadachim (Alfanje 180°) | 403 | 357 | 0 | **53.0%** | A (Forte / Vantajoso) |
| 7 | **Benkei** | Sōhei Monge Guerreiro (Naginata Colossal) | 386 | 369 | 5 | **50.8%** | B (Balanceado / Saudável) |
| 8 | **Joe** | American Ninja (Shuriken/Cão) | 378 | 380 | 2 | **49.7%** | B (Balanceado / Saudável) |
| 9 | **Ren** | Monge Shaolin (Kiai/Flurry) | 378 | 382 | 0 | **49.7%** | B (Balanceado / Saudável) |
| 10 | **Ichi** | Lâmina Cega (Shikomizue/Gyaku-Iai) | 374 | 382 | 4 | **49.2%** | B (Balanceado / Saudável) |
| 11 | **Murasaki** | Kunoichi Foice (Kusarigama) | 371 | 388 | 1 | **48.8%** | B (Balanceado / Saudável) |
| 12 | **Saitou** | Lobo de Mibu (Gatotsu) | 365 | 392 | 3 | **48.0%** | B (Balanceado / Saudável) |
| 13 | **O-Rin** | Menestrel Acústica (Shamisen/Kamaitachi) | 358 | 366 | 36 | **47.1%** | B (Balanceado / Saudável) |
| 14 | **Kenshin** | Retalhador (Iai/Shukuchi) | 356 | 399 | 5 | **46.8%** | C (Desfavorecido / Técnico) |
| 15 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 355 | 403 | 2 | **46.7%** | C (Desfavorecido / Técnico) |
| 16 | **Chiyo** | Lâminas Gêmeas (Dual Nodachi) | 334 | 425 | 1 | **44.0%** | C (Desfavorecido / Técnico) |
| 17 | **Goro** | Fazendeiro da Kuwa (Kuwa Cleave/Pisotão) | 324 | 436 | 0 | **42.6%** | C (Desfavorecido / Técnico) |
| 18 | **Tomoe** | Arqueira Miko (Arco Yumi) | 323 | 437 | 0 | **42.5%** | C (Desfavorecido / Técnico) |
| 19 | **Teppo** | Marksman (Tanegashima/Pólvora) | 295 | 465 | 0 | **38.8%** | D (Crítico / Sob Investigação) |
| 20 | **Hanzo** | Ninja Mestre (Kunai) | 276 | 482 | 2 | **36.3%** | D (Crítico / Sob Investigação) |

## 2. Desempenho por Arena & Variância Geográfica
Identificação das arenas de maior e menor eficácia para cada combatente (impacto de fossos, obstáculos, projéteis e perigos de fase):

| Rank | Lutador | Winrate Geral | Melhor Arena | WR Max | Pior Arena | WR Min | Dispersão |
|:---:|:---|:---:|:---|:---:|:---|:---:|:---:|
| 1 | **Valerius** | **74.2%** | Acampamento na Floresta | 89.5% | Kyoto: Bakumatsu em Chamas | 60.5% | 28.9% |
| 2 | **Seimei** | **60.0%** | Beco Yoshiwara | 76.3% | Convés na Tempestade | 44.7% | 31.6% |
| 3 | **Kasumi** | **56.2%** | Pátio Barroco | 65.8% | Jardim dos Lírios Carmim | 44.7% | 21.1% |
| 4 | **Julie** | **55.7%** | Moinho na Chuva | 68.4% | Telhados de Iga | 47.4% | 21.1% |
| 5 | **Musashi** | **53.2%** | Convés na Tempestade | 63.2% | Floresta de Bambu | 39.5% | 23.7% |
| 6 | **Anne** | **53.0%** | Templo na Névoa | 68.4% | Acampamento na Floresta | 36.8% | 31.6% |
| 7 | **Benkei** | **50.8%** | Moinho na Chuva | 63.2% | Acampamento na Floresta | 34.2% | 28.9% |
| 8 | **Joe** | **49.7%** | Pavilhão Astral Heian | 68.4% | Floresta de Bambu | 36.8% | 31.6% |
| 9 | **Ren** | **49.7%** | Ilha de Ganryū | 57.9% | Moinho na Chuva | 34.2% | 23.7% |
| 10 | **Ichi** | **49.2%** | Arrozais Terraciados | 60.5% | Jardim dos Lírios Carmim | 28.9% | 31.6% |
| 11 | **Murasaki** | **48.8%** | Gruta das Sombras | 63.2% | Kyoto: Bakumatsu em Chamas | 36.8% | 26.3% |
| 12 | **Saitou** | **48.0%** | Jardim dos Lírios Carmim | 65.8% | Telhados de Iga | 34.2% | 31.6% |
| 13 | **O-Rin** | **47.1%** | Telhados de Iga | 55.3% | Pátio dos Sinos Shaolin | 31.6% | 23.7% |
| 14 | **Kenshin** | **46.8%** | Kyoto: Bakumatsu em Chamas | 57.9% | Beco Yoshiwara | 31.6% | 26.3% |
| 15 | **Okuni** | **46.7%** | Convés na Tempestade | 60.5% | Pavilhão Astral Heian | 28.9% | 31.6% |
| 16 | **Chiyo** | **44.0%** | Convés na Tempestade | 63.2% | Pátio Barroco | 28.9% | 34.2% |
| 17 | **Goro** | **42.6%** | Acampamento na Floresta | 52.6% | Kyoto: Bakumatsu em Chamas | 31.6% | 21.1% |
| 18 | **Tomoe** | **42.5%** | Campo de Nagashino | 57.9% | Moinho na Chuva | 28.9% | 28.9% |
| 19 | **Teppo** | **38.8%** | Palco Kabuki | 52.6% | Templo na Névoa | 18.4% | 34.2% |
| 20 | **Hanzo** | **36.3%** | Telhados de Iga | 60.5% | Arrozais Terraciados | 26.3% | 34.2% |

## 3. Matriz de Confrontos Diretos Head-to-Head (20x20)
Percentual de vitórias da linha contra a coluna através de todas as 20 arenas:

| Lutador | Kensh | Musas | Hanzo | Joe | Saito | Teppo | Muras | Kasum | Okuni | Tomoe | Anne | Julie | Ren | Chiyo | Benke | O-Rin | Goro | Ichi | Valer | Seime |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 15% | 62% | 55% | 42% | 60% | 50% | 52% | 50% | 78% | 35% | 32% | 48% | 48% | 32% | 62% | 72% | 32% | 25% | 38% |
| **Musashi** | 82% | — | 55% | 68% | 82% | 78% | 38% | 72% | 22% | 65% | 50% | 40% | 90% | 48% | 57% | 5% | 68% | 45% | 8% | 38% |
| **Hanzo** | 38% | 45% | — | 35% | 35% | 28% | 22% | 30% | 38% | 40% | 48% | 32% | 28% | 57% | 32% | 50% | 30% | 55% | 8% | 40% |
| **Joe** | 45% | 30% | 65% | — | 48% | 68% | 62% | 45% | 60% | 45% | 62% | 48% | 40% | 42% | 35% | 55% | 78% | 57% | 20% | 40% |
| **Saitou** | 57% | 18% | 62% | 52% | — | 65% | 55% | 57% | 45% | 60% | 40% | 40% | 35% | 52% | 48% | 48% | 62% | 38% | 38% | 40% |
| **Teppo** | 40% | 22% | 72% | 32% | 35% | — | 42% | 28% | 38% | 42% | 45% | 40% | 42% | 42% | 32% | 60% | 22% | 48% | 15% | 38% |
| **Murasaki** | 50% | 62% | 78% | 38% | 42% | 57% | — | 45% | 55% | 57% | 35% | 52% | 45% | 62% | 35% | 40% | 52% | 55% | 20% | 45% |
| **Kasumi** | 48% | 28% | 70% | 55% | 42% | 72% | 55% | — | 65% | 60% | 62% | 50% | 57% | 78% | 52% | 68% | 55% | 52% | 60% | 38% |
| **Okuni** | 50% | 78% | 62% | 40% | 52% | 62% | 45% | 35% | — | 45% | 65% | 35% | 32% | 55% | 40% | 42% | 60% | 50% | 15% | 22% |
| **Tomoe** | 22% | 35% | 60% | 55% | 40% | 57% | 42% | 40% | 55% | — | 42% | 35% | 38% | 55% | 52% | 50% | 32% | 60% | 12% | 22% |
| **Anne** | 65% | 50% | 52% | 38% | 60% | 55% | 65% | 38% | 35% | 57% | — | 50% | 95% | 52% | 68% | 57% | 65% | 38% | 25% | 42% |
| **Julie** | 68% | 60% | 68% | 52% | 60% | 60% | 48% | 50% | 65% | 65% | 50% | — | 40% | 42% | 80% | 68% | 55% | 57% | 22% | 48% |
| **Ren** | 52% | 10% | 72% | 60% | 65% | 57% | 55% | 42% | 68% | 62% | 5% | 60% | — | 65% | 50% | 52% | 68% | 45% | 28% | 28% |
| **Chiyo** | 52% | 52% | 42% | 57% | 48% | 57% | 38% | 22% | 45% | 45% | 48% | 57% | 35% | — | 40% | 35% | 57% | 50% | 20% | 32% |
| **Benkei** | 68% | 42% | 68% | 65% | 52% | 68% | 65% | 48% | 60% | 48% | 32% | 20% | 50% | 57% | — | 48% | 70% | 60% | 20% | 25% |
| **O-Rin** | 35% | 95% | 48% | 45% | 52% | 40% | 60% | 32% | 55% | 50% | 42% | 32% | 48% | 65% | 48% | — | 45% | 55% | 38% | 10% |
| **Goro** | 28% | 32% | 70% | 22% | 38% | 78% | 48% | 45% | 40% | 68% | 35% | 45% | 32% | 42% | 30% | 55% | — | 38% | 30% | 35% |
| **Ichi** | 62% | 55% | 45% | 42% | 62% | 52% | 45% | 42% | 50% | 40% | 62% | 42% | 55% | 50% | 40% | 45% | 62% | — | 28% | 52% |
| **Valerius** | 75% | 92% | 92% | 78% | 62% | 85% | 80% | 40% | 85% | 88% | 75% | 78% | 72% | 80% | 80% | 60% | 70% | 72% | — | 45% |
| **Seimei** | 60% | 62% | 60% | 60% | 60% | 62% | 55% | 62% | 78% | 78% | 57% | 52% | 72% | 68% | 70% | 15% | 65% | 48% | 55% | — |

## 4. Classificação Oficial via Algoritmo Merge Sort
A ordenação por divisão e conquista arbitrou cada emparelhamento utilizando estritamente o retrospecto direto (Head-to-Head):

1. **Julie** — Winrate Geral: 55.7% (423V / 337D / 0E)
2. **Ichi** — Winrate Geral: 49.2% (374V / 382D / 4E)
3. **Seimei** — Winrate Geral: 60.0% (456V / 271D / 33E)
4. **Valerius** — Winrate Geral: 74.2% (564V / 194D / 2E)
5. **Musashi** — Winrate Geral: 53.2% (404V / 354D / 2E)
6. **Anne** — Winrate Geral: 53.0% (403V / 357D / 0E)
7. **Benkei** — Winrate Geral: 50.8% (386V / 369D / 5E)
8. **Ren** — Winrate Geral: 49.7% (378V / 382D / 0E)
9. **Saitou** — Winrate Geral: 48.0% (365V / 392D / 3E)
10. **Chiyo** — Winrate Geral: 44.0% (334V / 425D / 1E)
11. **Kenshin** — Winrate Geral: 46.8% (356V / 399D / 5E)
12. **Kasumi** — Winrate Geral: 56.2% (427V / 331D / 2E)
13. **Joe** — Winrate Geral: 49.7% (378V / 380D / 2E)
14. **Murasaki** — Winrate Geral: 48.8% (371V / 388D / 1E)
15. **Goro** — Winrate Geral: 42.6% (324V / 436D / 0E)
16. **O-Rin** — Winrate Geral: 47.1% (358V / 366D / 36E)
17. **Tomoe** — Winrate Geral: 42.5% (323V / 437D / 0E)
18. **Okuni** — Winrate Geral: 46.7% (355V / 403D / 2E)
19. **Teppo** — Winrate Geral: 38.8% (295V / 465D / 0E)
20. **Hanzo** — Winrate Geral: 36.3% (276V / 482D / 2E)

## 5. Análise Técnica dos Resultados

### 5.1 Domínio dos Top Tiers: **Valerius (74.2%)** e **Seimei (60.0%)**
- Combatentes com excelente alcance, precedência de ataque imediata ou cobertura por projéteis mantêm controle consistente do espaço mesmo em arenas com perigos complexos.

### 5.2 Desafios dos Bottom Tiers: **Hanzo (36.3%)** e **Teppo (38.8%)**
- Personagens que dependem de recarga estacionária, tiros com windup ou que possuem desvantagens contra assédio a longa distância sofrem mais em arenas abertas e com perigos móveis.

### 5.3 Confrontos com Polarização Extrema (>= 85% de dominância)
- **Musashi vs Ren**: 36 a 4 (90.0% de dominância)
- **O-Rin vs Musashi**: 38 a 2 (95.0% de dominância)
- **Valerius vs Musashi**: 37 a 3 (92.5% de dominância)
- **Valerius vs Hanzo**: 37 a 3 (92.5% de dominância)
- **Valerius vs Teppo**: 34 a 6 (85.0% de dominância)
- **Valerius vs Okuni**: 34 a 6 (85.0% de dominância)
- **Valerius vs Tomoe**: 35 a 5 (87.5% de dominância)
- **Anne vs Ren**: 38 a 2 (95.0% de dominância)

## 6. Diretrizes e Recomendações de Balanceamento
1. **Normalização de Recovery**: Ajustar janelas de whiff para punição balanceada de ataques rápidos.
2. **Mobilidade Tática**: Preservar movimentação tática durante recargas para reduzir vulnerabilidade em arenas estreitas.
3. **Interação com Perigos**: Manter zonas neutras acessíveis em arenas com hazards telegrafados ativos.
