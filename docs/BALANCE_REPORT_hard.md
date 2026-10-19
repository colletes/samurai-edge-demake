# Relatório Detalhado de Balanceamento & Merge Sort de Duelos (HARD)

> **Métricas Globais da Simulação**:
> - Dificuldade da IA (ambos os lutadores): **HARD**
> - Total de Guerreiros Avaliados: **20**
> - Total de Arenas Avaliadas: **20** (Cobertura Integral do Jogo)
> - Combinações Únicas de Duelos: **190 confrontos** $\binom{20}{2}$
> - Lutas por Combinação: **40 batalhas** (2 por arena, paridade simétrica P1/P2)
> - **Volume Total de Batalhas Simuladas**: **7600 batalhas**
> - Tempo Total de Simulação Física: **67.03 segundos** (113.4 lutas/s)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Valerius** | Necromante Prussiano (Foice/Invocações) | 522 | 237 | 1 | **68.7%** | S (Dominante / Alta Vantagem) |
| 2 | **Murasaki** | Kunoichi Foice (Kusarigama) | 470 | 290 | 0 | **61.8%** | S (Dominante / Alta Vantagem) |
| 3 | **Joe** | American Ninja (Shuriken/Cão) | 460 | 300 | 0 | **60.5%** | S (Dominante / Alta Vantagem) |
| 4 | **Seimei** | Onmyoji dos Talismãs (Ofuda/Selo Sagrado) | 458 | 271 | 31 | **60.3%** | S (Dominante / Alta Vantagem) |
| 5 | **Julie** | Mosqueteira (Florete/Riposte) | 440 | 318 | 2 | **57.9%** | A (Forte / Vantajoso) |
| 6 | **Musashi** | Duas Lâminas (Combo/Parry) | 428 | 326 | 6 | **56.3%** | A (Forte / Vantajoso) |
| 7 | **Ichi** | Lâmina Cega (Shikomizue/Gyaku-Iai) | 425 | 329 | 6 | **55.9%** | A (Forte / Vantajoso) |
| 8 | **Tomoe** | Arqueira Miko (Arco Yumi) | 414 | 345 | 1 | **54.5%** | A (Forte / Vantajoso) |
| 9 | **Anne** | Espadachim (Alfanje 180°) | 411 | 348 | 1 | **54.1%** | A (Forte / Vantajoso) |
| 10 | **Hanzo** | Ninja Mestre (Kunai) | 367 | 392 | 1 | **48.3%** | B (Balanceado / Saudável) |
| 11 | **Goro** | Fazendeiro da Kuwa (Kuwa Cleave/Pisotão) | 366 | 392 | 2 | **48.2%** | B (Balanceado / Saudável) |
| 12 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 354 | 401 | 5 | **46.6%** | C (Desfavorecido / Técnico) |
| 13 | **O-Rin** | Menestrel Acústica (Shamisen/Kamaitachi) | 353 | 380 | 27 | **46.5%** | C (Desfavorecido / Técnico) |
| 14 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 350 | 407 | 3 | **46.0%** | C (Desfavorecido / Técnico) |
| 15 | **Benkei** | Sōhei Monge Guerreiro (Naginata Colossal) | 304 | 448 | 8 | **40.0%** | D (Crítico / Sob Investigação) |
| 16 | **Teppo** | Marksman (Tanegashima/Pólvora) | 294 | 466 | 0 | **38.7%** | D (Crítico / Sob Investigação) |
| 17 | **Kenshin** | Retalhador (Iai/Shukuchi) | 288 | 465 | 7 | **37.9%** | D (Crítico / Sob Investigação) |
| 18 | **Saitou** | Lobo de Mibu (Gatotsu) | 285 | 471 | 4 | **37.5%** | D (Crítico / Sob Investigação) |
| 19 | **Ren** | Monge Shaolin (Kiai/Flurry) | 280 | 480 | 0 | **36.8%** | D (Crítico / Sob Investigação) |
| 20 | **Chiyo** | Lâminas Gêmeas (Dual Nodachi) | 277 | 480 | 3 | **36.5%** | D (Crítico / Sob Investigação) |

## 2. Desempenho por Arena & Variância Geográfica
Identificação das arenas de maior e menor eficácia para cada combatente (impacto de fossos, obstáculos, projéteis e perigos de fase):

| Rank | Lutador | Winrate Geral | Melhor Arena | WR Max | Pior Arena | WR Min | Dispersão |
|:---:|:---|:---:|:---|:---:|:---|:---:|:---:|
| 1 | **Valerius** | **68.7%** | Campo de Nagashino | 79.0% | Moinho na Chuva | 47.4% | 31.6% |
| 2 | **Murasaki** | **61.8%** | Floresta de Bambu | 73.7% | Acampamento na Floresta | 50.0% | 23.7% |
| 3 | **Joe** | **60.5%** | Convés na Tempestade | 73.7% | Campo de Nagashino | 50.0% | 23.7% |
| 4 | **Seimei** | **60.3%** | Jardim dos Lírios Carmim | 73.7% | Kyoto: Bakumatsu em Chamas | 39.5% | 34.2% |
| 5 | **Julie** | **57.9%** | Pátio dos Sinos Shaolin | 68.4% | Beco Yoshiwara | 47.4% | 21.1% |
| 6 | **Musashi** | **56.3%** | Telhados de Iga | 63.2% | Moinho na Chuva | 44.7% | 18.4% |
| 7 | **Ichi** | **55.9%** | Pátio Barroco | 65.8% | Ponte Gojo | 34.2% | 31.6% |
| 8 | **Tomoe** | **54.5%** | Acampamento na Floresta | 68.4% | Pátio Barroco | 44.7% | 23.7% |
| 9 | **Anne** | **54.1%** | Kyoto: Bakumatsu em Chamas | 68.4% | Acampamento na Floresta | 42.1% | 26.3% |
| 10 | **Hanzo** | **48.3%** | Acampamento na Floresta | 71.0% | Palco Kabuki | 34.2% | 36.8% |
| 11 | **Goro** | **48.2%** | Beco Yoshiwara | 60.5% | Floresta de Bambu | 34.2% | 26.3% |
| 12 | **Kasumi** | **46.6%** | Gruta das Sombras | 60.5% | Floresta de Bambu | 26.3% | 34.2% |
| 13 | **O-Rin** | **46.5%** | Kyoto: Bakumatsu em Chamas | 63.2% | Gruta das Sombras | 31.6% | 31.6% |
| 14 | **Okuni** | **46.0%** | Arrozais Terraciados | 60.5% | Moinho na Chuva | 28.9% | 31.6% |
| 15 | **Benkei** | **40.0%** | Convés na Tempestade | 47.4% | Floresta de Bambu | 31.6% | 15.8% |
| 16 | **Teppo** | **38.7%** | Acampamento na Floresta | 60.5% | Arrozais Terraciados | 18.4% | 42.1% |
| 17 | **Kenshin** | **37.9%** | Floresta de Bambu | 50.0% | Beco Yoshiwara | 26.3% | 23.7% |
| 18 | **Saitou** | **37.5%** | Templo na Névoa | 47.4% | Acampamento na Floresta | 23.7% | 23.7% |
| 19 | **Ren** | **36.8%** | Santuário na Montanha | 47.4% | Acampamento na Floresta | 18.4% | 28.9% |
| 20 | **Chiyo** | **36.5%** | Moinho na Chuva | 50.0% | Beco Yoshiwara | 23.7% | 26.3% |

## 3. Matriz de Confrontos Diretos Head-to-Head (20x20)
Percentual de vitórias da linha contra a coluna através de todas as 20 arenas:

| Lutador | Kensh | Musas | Hanzo | Joe | Saito | Teppo | Muras | Kasum | Okuni | Tomoe | Anne | Julie | Ren | Chiyo | Benke | O-Rin | Goro | Ichi | Valer | Seime |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 8% | 40% | 28% | 40% | 62% | 12% | 38% | 38% | 62% | 40% | 28% | 45% | 50% | 30% | 65% | 38% | 25% | 25% | 48% |
| **Musashi** | 92% | — | 45% | 42% | 95% | 70% | 18% | 68% | 35% | 62% | 38% | 52% | 90% | 45% | 95% | 38% | 50% | 52% | 22% | 60% |
| **Hanzo** | 60% | 55% | — | 28% | 48% | 68% | 48% | 60% | 55% | 38% | 70% | 38% | 52% | 75% | 48% | 65% | 38% | 32% | 15% | 28% |
| **Joe** | 72% | 57% | 72% | — | 60% | 80% | 50% | 50% | 70% | 62% | 55% | 48% | 62% | 82% | 85% | 57% | 57% | 72% | 30% | 25% |
| **Saitou** | 60% | 2% | 52% | 40% | — | 68% | 40% | 57% | 28% | 48% | 10% | 20% | 68% | 62% | 57% | 15% | 42% | 20% | 12% | 10% |
| **Teppo** | 38% | 30% | 32% | 20% | 32% | — | 48% | 52% | 68% | 22% | 60% | 48% | 48% | 50% | 22% | 55% | 30% | 50% | 15% | 15% |
| **Murasaki** | 88% | 82% | 52% | 50% | 60% | 52% | — | 48% | 88% | 40% | 0% | 75% | 60% | 82% | 75% | 65% | 78% | 82% | 38% | 60% |
| **Kasumi** | 62% | 32% | 40% | 50% | 42% | 48% | 52% | — | 50% | 32% | 70% | 22% | 65% | 70% | 25% | 48% | 62% | 32% | 68% | 12% |
| **Okuni** | 62% | 62% | 45% | 30% | 70% | 32% | 12% | 50% | — | 25% | 52% | 32% | 55% | 62% | 82% | 32% | 50% | 50% | 25% | 42% |
| **Tomoe** | 35% | 38% | 62% | 38% | 52% | 78% | 60% | 68% | 75% | — | 68% | 60% | 68% | 55% | 22% | 72% | 60% | 55% | 20% | 50% |
| **Anne** | 60% | 62% | 30% | 45% | 90% | 40% | 100% | 30% | 48% | 32% | — | 40% | 100% | 52% | 62% | 42% | 88% | 52% | 48% | 5% |
| **Julie** | 72% | 48% | 62% | 52% | 80% | 52% | 25% | 78% | 68% | 40% | 60% | — | 57% | 65% | 70% | 85% | 42% | 50% | 35% | 57% |
| **Ren** | 55% | 10% | 48% | 38% | 32% | 52% | 40% | 35% | 45% | 32% | 0% | 42% | — | 57% | 70% | 22% | 42% | 38% | 25% | 15% |
| **Chiyo** | 50% | 55% | 22% | 18% | 38% | 50% | 18% | 30% | 38% | 45% | 48% | 35% | 42% | — | 62% | 28% | 38% | 32% | 10% | 35% |
| **Benkei** | 62% | 5% | 52% | 15% | 42% | 78% | 25% | 75% | 18% | 78% | 38% | 25% | 30% | 35% | — | 72% | 25% | 22% | 20% | 42% |
| **O-Rin** | 35% | 57% | 35% | 42% | 82% | 45% | 35% | 52% | 68% | 28% | 57% | 15% | 78% | 72% | 28% | — | 42% | 57% | 45% | 8% |
| **Goro** | 62% | 48% | 62% | 42% | 57% | 70% | 22% | 38% | 50% | 40% | 10% | 57% | 57% | 62% | 75% | 57% | — | 28% | 38% | 38% |
| **Ichi** | 75% | 48% | 68% | 28% | 80% | 50% | 18% | 55% | 50% | 45% | 48% | 50% | 62% | 68% | 75% | 42% | 72% | — | 35% | 95% |
| **Valerius** | 75% | 75% | 85% | 70% | 88% | 85% | 62% | 32% | 75% | 80% | 52% | 65% | 75% | 90% | 80% | 55% | 62% | 65% | — | 32% |
| **Seimei** | 45% | 40% | 72% | 75% | 88% | 85% | 40% | 88% | 55% | 50% | 95% | 42% | 85% | 62% | 55% | 32% | 62% | 5% | 68% | — |

## 4. Classificação Oficial via Algoritmo Merge Sort
A ordenação por divisão e conquista arbitrou cada emparelhamento utilizando estritamente o retrospecto direto (Head-to-Head):

1. **Julie** — Winrate Geral: 57.9% (440V / 318D / 2E)
2. **Joe** — Winrate Geral: 60.5% (460V / 300D / 0E)
3. **Anne** — Winrate Geral: 54.1% (411V / 348D / 1E)
4. **Musashi** — Winrate Geral: 56.3% (428V / 326D / 6E)
5. **Tomoe** — Winrate Geral: 54.5% (414V / 345D / 1E)
6. **Ichi** — Winrate Geral: 55.9% (425V / 329D / 6E)
7. **Seimei** — Winrate Geral: 60.3% (458V / 271D / 31E)
8. **Valerius** — Winrate Geral: 68.7% (522V / 237D / 1E)
9. **Goro** — Winrate Geral: 48.2% (366V / 392D / 2E)
10. **O-Rin** — Winrate Geral: 46.5% (353V / 380D / 27E)
11. **Saitou** — Winrate Geral: 37.5% (285V / 471D / 4E)
12. **Hanzo** — Winrate Geral: 48.3% (367V / 392D / 1E)
13. **Kasumi** — Winrate Geral: 46.6% (354V / 401D / 5E)
14. **Murasaki** — Winrate Geral: 61.8% (470V / 290D / 0E)
15. **Ren** — Winrate Geral: 36.8% (280V / 480D / 0E)
16. **Kenshin** — Winrate Geral: 37.9% (288V / 465D / 7E)
17. **Teppo** — Winrate Geral: 38.7% (294V / 466D / 0E)
18. **Okuni** — Winrate Geral: 46.0% (350V / 407D / 3E)
19. **Chiyo** — Winrate Geral: 36.5% (277V / 480D / 3E)
20. **Benkei** — Winrate Geral: 40.0% (304V / 448D / 8E)

## 5. Análise Técnica dos Resultados

### 5.1 Domínio dos Top Tiers: **Valerius (68.7%)** e **Murasaki (61.8%)**
- Combatentes com excelente alcance, precedência de ataque imediata ou cobertura por projéteis mantêm controle consistente do espaço mesmo em arenas com perigos complexos.

### 5.2 Desafios dos Bottom Tiers: **Chiyo (36.5%)** e **Ren (36.8%)**
- Personagens que dependem de recarga estacionária, tiros com windup ou que possuem desvantagens contra assédio a longa distância sofrem mais em arenas abertas e com perigos móveis.

### 5.3 Confrontos com Polarização Extrema (>= 85% de dominância)
- **Musashi vs Kenshin**: 37 a 3 (92.5% de dominância)
- **Murasaki vs Kenshin**: 35 a 5 (87.5% de dominância)
- **Musashi vs Saitou**: 38 a 1 (95.0% de dominância)
- **Musashi vs Ren**: 36 a 4 (90.0% de dominância)
- **Musashi vs Benkei**: 38 a 2 (95.0% de dominância)
- **Valerius vs Hanzo**: 34 a 6 (85.0% de dominância)
- **Joe vs Benkei**: 34 a 6 (85.0% de dominância)
- **Anne vs Saitou**: 36 a 4 (90.0% de dominância)

## 6. Diretrizes e Recomendações de Balanceamento
1. **Normalização de Recovery**: Ajustar janelas de whiff para punição balanceada de ataques rápidos.
2. **Mobilidade Tática**: Preservar movimentação tática durante recargas para reduzir vulnerabilidade em arenas estreitas.
3. **Interação com Perigos**: Manter zonas neutras acessíveis em arenas com hazards telegrafados ativos.
