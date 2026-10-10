# Relatório Detalhado de Balanceamento & Merge Sort de Duelos Simulados

> **Métricas Globais da Simulação**:
> - Dificuldade da IA (ambos os lutadores): **NORMAL**
> - Total de Guerreiros Avaliados: 12
> - Combinações Únicas de Duelos: 66 confrontos $\binom{12}{2}$
> - Volume de Lutas por Combinação: 24 batalhas simétricas (12 com P1/P2 alternados)
> - **Volume Total de Batalhas Simuladas**: **910 batalhas**
> - Tempo Total de Simulação Física: 5.03 segundos (180.9 lutas/segundo)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Teppo** | Marksman (Tanegashima/Pólvora) | 90 | 30 | 10 | **69.2%** | A (Forte / Vantajoso) |
| 2 | **Joe** | American Ninja (Shuriken/Cão) | 82 | 38 | 10 | **63.1%** | A (Forte / Vantajoso) |
| 3 | **Tomoe** | Arqueira Miko (Arco Yumi) | 76 | 46 | 8 | **58.5%** | A (Forte / Vantajoso) |
| 4 | **Musashi** | Duas Lâminas (Combo/Parry) | 72 | 49 | 9 | **55.4%** | A (Forte / Vantajoso) |
| 5 | **Julie** | Mosqueteira (Florete/Riposte) | 69 | 53 | 8 | **53.1%** | B (Balanceado / Saudável) |
| 6 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 65 | 62 | 3 | **50.0%** | B (Balanceado / Saudável) |
| 7 | **Anne** | Espadachim (Alfanje 180°) | 65 | 58 | 7 | **50.0%** | B (Balanceado / Saudável) |
| 8 | **Hanzo** | Ninja Mestre (Kunai) | 59 | 63 | 8 | **45.4%** | B (Balanceado / Saudável) |
| 9 | **Murasaki** | Kunoichi Foice (Kusarigama) | 58 | 69 | 3 | **44.6%** | C (Desfavorecido / Técnico) |
| 10 | **Saitou** | Lobo de Mibu (Gatotsu) | 57 | 67 | 6 | **43.9%** | C (Desfavorecido / Técnico) |
| 11 | **Kenshin** | Retalhador (Iai/Shukuchi) | 53 | 65 | 12 | **40.8%** | C (Desfavorecido / Técnico) |
| 12 | **Chiyo** | Lâminas Gêmeas (Dual Nodachi) | 45 | 80 | 5 | **34.6%** | C (Desfavorecido / Técnico) |
| 13 | **Ren** | Monge Shaolin (Kiai/Flurry) | 36 | 86 | 8 | **27.7%** | D (Underpowered / Crítico) |
| 14 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 29 | 90 | 11 | **22.3%** | D (Underpowered / Crítico) |

## 2. Comparativo de Desempenho por Cenário (Bambu vs Kyoto)
Impacto do layout (área aberta e reflexiva do lago vs via estreita de Kyoto com perigo ativo de carruagens e escombros):

| Rank | Lutador | Winrate Geral | Winrate Bambu | Winrate Kyoto | Impacto Kyoto vs Bambu |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | **Teppo** | **69.2%** | 80.0% | 58.5% | -21.5% |
| 2 | **Joe** | **63.1%** | 66.2% | 60.0% | -6.2% |
| 3 | **Tomoe** | **58.5%** | 60.0% | 56.9% | -3.1% |
| 4 | **Musashi** | **55.4%** | 61.5% | 49.2% | -12.3% |
| 5 | **Julie** | **53.1%** | 56.9% | 49.2% | -7.7% |
| 6 | **Kasumi** | **50.0%** | 55.4% | 44.6% | -10.8% |
| 7 | **Anne** | **50.0%** | 53.9% | 46.1% | -7.7% |
| 8 | **Hanzo** | **45.4%** | 49.2% | 41.5% | -7.7% |
| 9 | **Murasaki** | **44.6%** | 46.1% | 43.1% | -3.1% |
| 10 | **Saitou** | **43.9%** | 47.7% | 40.0% | -7.7% |
| 11 | **Kenshin** | **40.8%** | 38.5% | 43.1% | +4.6% |
| 12 | **Chiyo** | **34.6%** | 35.4% | 33.9% | -1.5% |
| 13 | **Ren** | **27.7%** | 29.2% | 26.1% | -3.1% |
| 14 | **Okuni** | **22.3%** | 20.0% | 24.6% | +4.6% |

## 3. Matriz de Confrontos Head-to-Head (H2H 12x12)
A tabela exibe a taxa percentual de vitórias da linha contra a coluna nas 24 lutas disputadas (12 em cada arena):

| Lutador | Kenshi | Musash | Hanzo | Joe | Saitou | Teppo | Murasa | Kasumi | Okuni | Tomoe | Anne | Julie | Ren | Chiyo |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 30% | 50% | 20% | 30% | 30% | 30% | 60% | 70% | 20% | 20% | 30% | 70% | 70% |
| **Musashi** | 70% | — | 40% | 40% | 60% | 30% | 70% | 70% | 70% | 40% | 50% | 60% | 50% | 70% |
| **Hanzo** | 30% | 60% | — | 50% | 50% | 40% | 30% | 30% | 50% | 60% | 40% | 20% | 70% | 60% |
| **Joe** | 80% | 60% | 50% | — | 90% | 10% | 70% | 60% | 90% | 60% | 40% | 50% | 80% | 80% |
| **Saitou** | 50% | 20% | 50% | 10% | — | 20% | 40% | 60% | 60% | 70% | 20% | 50% | 70% | 50% |
| **Teppo** | 60% | 50% | 50% | 60% | 80% | — | 90% | 80% | 80% | 50% | 80% | 50% | 80% | 90% |
| **Murasaki** | 60% | 20% | 70% | 30% | 60% | 10% | — | 20% | 70% | 30% | 10% | 50% | 90% | 60% |
| **Kasumi** | 40% | 30% | 70% | 30% | 40% | 20% | 80% | — | 60% | 40% | 80% | 30% | 70% | 60% |
| **Okuni** | 20% | 20% | 40% | 0% | 40% | 20% | 30% | 30% | — | 10% | 30% | 0% | 10% | 40% |
| **Tomoe** | 70% | 50% | 40% | 30% | 20% | 40% | 60% | 60% | 80% | — | 90% | 70% | 60% | 90% |
| **Anne** | 50% | 50% | 40% | 50% | 80% | 20% | 90% | 20% | 70% | 10% | — | 30% | 90% | 50% |
| **Julie** | 60% | 40% | 70% | 40% | 50% | 40% | 50% | 70% | 80% | 30% | 60% | — | 60% | 40% |
| **Ren** | 30% | 30% | 30% | 20% | 30% | 10% | 10% | 20% | 70% | 30% | 10% | 30% | — | 40% |
| **Chiyo** | 30% | 30% | 30% | 0% | 40% | 10% | 40% | 40% | 50% | 10% | 50% | 60% | 60% | — |

## 4. Resultado do Algoritmo Merge Sort de Duelos
O Merge Sort executou uma ordenação por divisão e conquista onde cada decisão de precedência foi arbitrada pelo retrospecto direto de combates:

1. **Teppo** — Winrate Geral: 69.2% (90V / 30D / 10E)
2. **Joe** — Winrate Geral: 63.1% (82V / 38D / 10E)
3. **Tomoe** — Winrate Geral: 58.5% (76V / 46D / 8E)
4. **Kasumi** — Winrate Geral: 50.0% (65V / 62D / 3E)
5. **Murasaki** — Winrate Geral: 44.6% (58V / 69D / 3E)
6. **Saitou** — Winrate Geral: 43.9% (57V / 67D / 6E)
7. **Kenshin** — Winrate Geral: 40.8% (53V / 65D / 12E)
8. **Hanzo** — Winrate Geral: 45.4% (59V / 63D / 8E)
9. **Musashi** — Winrate Geral: 55.4% (72V / 49D / 9E)
10. **Chiyo** — Winrate Geral: 34.6% (45V / 80D / 5E)
11. **Julie** — Winrate Geral: 53.1% (69V / 53D / 8E)
12. **Anne** — Winrate Geral: 50.0% (65V / 58D / 7E)
13. **Ren** — Winrate Geral: 27.7% (36V / 86D / 8E)
14. **Okuni** — Winrate Geral: 22.3% (29V / 90D / 11E)

## 5. Avaliação Técnica Aprofundada do Balanceamento

### 5.1 Opressão e Dominância (Top Tiers)
- **Teppo (69.2%) & Joe (63.1%)**:
  - As mecânicas de ataque com prioridade/precedência absoluta, alcance de projéteis instantâneos (snipers) ou frames defensivos de Parry/Riposte garantem uma taxa de vitória esmagadora contra lutadores de aproximação pura.

### 5.2 Vulnerabilidades Críticas (Bottom Tiers)
- **Okuni (22.3%) & Ren (27.7%)**:
  - Lutadores que dependem de tempos longos de recarga parada (ex: recarga do arcabuz sem cobertura móvel), auto-dano/suicídio por fogo amigo de explosivos, ou windup de retesamento de arco sofrem punições instantâneas contra oponentes rápidos.

### 5.3 Dinâmica de Pedra-Papel-Tesoura e Polarização Extrema
Não foram detectados confrontos com polarização extrema superior a 87%.

## 6. Propostas Concretas de Balance Patch (Recomendações de Design)
Para equalizar o elenco e aproximar todos os combatentes da faixa saudável de 45% a 55% de winrate:
1. **Ajuste de Precedência e Cooldowns de Projéteis**: Aumentar ligeiramente o recovery de golpes com prioridade e projéteis rápidos.
2. **Mobilidade durante a Recarga**: Permitir que classes que recarregam mantenham movimentação a 50% da velocidade, evitando vulnerabilidade estática total.
3. **Redução de Fogo Amigo**: Diminuir o raio de explosão auto-infligido para armas de área (como bombas).
4. **Janela de Defesa (Parry/Riposte)**: Ajustar a janela de parry para exigir timing mais preciso contra sequências rápidas.
