# Relatório Detalhado de Balanceamento & Merge Sort de Duelos Simulados

> **Métricas Globais da Simulação**:
> - Dificuldade da IA (ambos os lutadores): **NORMAL**
> - Total de Guerreiros Avaliados: 18
> - Combinações Únicas de Duelos: 153 confrontos $\binom{18}{2}$
> - Volume de Lutas por Combinação: 24 batalhas simétricas (12 com P1/P2 alternados)
> - **Volume Total de Batalhas Simuladas**: **3672 batalhas**
> - Tempo Total de Simulação Física: 16.67 segundos (220.3 lutas/segundo)

## 1. Tabela Geral de Desempenho & Tier List

| Rank | Lutador | Arquétipo / Estilo | Vitórias | Derrotas | Empates | Winrate | Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Murasaki** | Kunoichi Foice (Kusarigama) | 232 | 159 | 17 | **56.9%** | A (Forte / Vantajoso) |
| 2 | **Tomoe** | Arqueira Miko (Arco Yumi) | 232 | 152 | 24 | **56.9%** | A (Forte / Vantajoso) |
| 3 | **Joe** | American Ninja (Shuriken/Cão) | 220 | 171 | 17 | **53.9%** | B (Balanceado / Saudável) |
| 4 | **Julie** | Mosqueteira (Florete/Riposte) | 219 | 166 | 23 | **53.7%** | B (Balanceado / Saudável) |
| 5 | **Anne** | Espadachim (Alfanje 180°) | 217 | 169 | 22 | **53.2%** | B (Balanceado / Saudável) |
| 6 | **Musashi** | Duas Lâminas (Combo/Parry) | 216 | 172 | 20 | **52.9%** | B (Balanceado / Saudável) |
| 7 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | 208 | 175 | 25 | **51.0%** | B (Balanceado / Saudável) |
| 8 | **Hanzo** | Ninja Mestre (Kunai) | 203 | 184 | 21 | **49.8%** | B (Balanceado / Saudável) |
| 9 | **Saitou** | Lobo de Mibu (Gatotsu) | 184 | 196 | 28 | **45.1%** | B (Balanceado / Saudável) |
| 10 | **O-Rin** | Menestrel Acústica (Shamisen/Kamaitachi) | 183 | 200 | 25 | **44.9%** | C (Desfavorecido / Técnico) |
| 11 | **Benkei** | Sōhei Monge Guerreiro (Naginata Colossal) | 182 | 195 | 31 | **44.6%** | C (Desfavorecido / Técnico) |
| 12 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | 179 | 201 | 28 | **43.9%** | C (Desfavorecido / Técnico) |
| 13 | **Ichi** | Lâmina Cega (Shikomizue/Gyaku-Iai) | 178 | 202 | 28 | **43.6%** | C (Desfavorecido / Técnico) |
| 14 | **Ren** | Monge Shaolin (Kiai/Flurry) | 171 | 211 | 26 | **41.9%** | C (Desfavorecido / Técnico) |
| 15 | **Teppo** | Marksman (Tanegashima/Pólvora) | 165 | 221 | 22 | **40.4%** | C (Desfavorecido / Técnico) |
| 16 | **Kenshin** | Retalhador (Iai/Shukuchi) | 161 | 201 | 46 | **39.5%** | C (Desfavorecido / Técnico) |
| 17 | **Goro** | Fazendeiro da Kuwa (Kuwa Cleave/Pisotão) | 156 | 239 | 13 | **38.2%** | C (Desfavorecido / Técnico) |
| 18 | **Chiyo** | Lâminas Gêmeas (Dual Nodachi) | 145 | 237 | 26 | **35.5%** | C (Desfavorecido / Técnico) |

## 2. Comparativo de Desempenho por Cenário (Bambu vs Kyoto)
Impacto do layout (área aberta e reflexiva do lago vs via estreita de Kyoto com perigo ativo de carruagens e escombros):

| Rank | Lutador | Winrate Geral | Winrate Bambu | Winrate Kyoto | Impacto Kyoto vs Bambu |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | **Murasaki** | **56.9%** | 57.4% | 56.4% | -1.0% |
| 2 | **Tomoe** | **56.9%** | 57.8% | 55.9% | -2.0% |
| 3 | **Joe** | **53.9%** | 58.8% | 49.0% | -9.8% |
| 4 | **Julie** | **53.7%** | 58.8% | 48.5% | -10.3% |
| 5 | **Anne** | **53.2%** | 57.8% | 48.5% | -9.3% |
| 6 | **Musashi** | **52.9%** | 52.0% | 53.9% | +2.0% |
| 7 | **Kasumi** | **51.0%** | 52.9% | 49.0% | -3.9% |
| 8 | **Hanzo** | **49.8%** | 49.0% | 50.5% | +1.5% |
| 9 | **Saitou** | **45.1%** | 45.6% | 44.6% | -1.0% |
| 10 | **O-Rin** | **44.9%** | 48.0% | 41.7% | -6.4% |
| 11 | **Benkei** | **44.6%** | 46.6% | 42.6% | -3.9% |
| 12 | **Okuni** | **43.9%** | 49.5% | 38.2% | -11.3% |
| 13 | **Ichi** | **43.6%** | 46.1% | 41.2% | -4.9% |
| 14 | **Ren** | **41.9%** | 44.1% | 39.7% | -4.4% |
| 15 | **Teppo** | **40.4%** | 46.6% | 34.3% | -12.3% |
| 16 | **Kenshin** | **39.5%** | 43.6% | 35.3% | -8.3% |
| 17 | **Goro** | **38.2%** | 42.6% | 33.8% | -8.8% |
| 18 | **Chiyo** | **35.5%** | 40.7% | 30.4% | -10.3% |

## 3. Matriz de Confrontos Head-to-Head (H2H 18x18)
A tabela exibe a taxa percentual de vitórias da linha contra a coluna nas 24 lutas disputadas (12 em cada arena):

| Lutador | Kenshi | Musash | Hanzo | Joe | Saitou | Teppo | Murasa | Kasumi | Okuni | Tomoe | Anne | Julie | Ren | Chiyo | Benkei | O-Rin | Goro | Ichi |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Kenshin** | — | 21% | 33% | 29% | 42% | 67% | 17% | 46% | 46% | 25% | 62% | 29% | 29% | 46% | 17% | 50% | 79% | 33% |
| **Musashi** | 71% | — | 38% | 42% | 79% | 67% | 12% | 67% | 38% | 46% | 46% | 46% | 92% | 58% | 71% | 17% | 67% | 46% |
| **Hanzo** | 50% | 58% | — | 33% | 38% | 54% | 42% | 29% | 62% | 38% | 62% | 33% | 50% | 62% | 54% | 71% | 38% | 71% |
| **Joe** | 67% | 58% | 67% | — | 33% | 62% | 46% | 54% | 67% | 21% | 42% | 38% | 50% | 62% | 42% | 71% | 79% | 58% |
| **Saitou** | 46% | 8% | 62% | 62% | — | 62% | 21% | 58% | 38% | 62% | 42% | 21% | 58% | 67% | 50% | 38% | 50% | 21% |
| **Teppo** | 25% | 33% | 33% | 25% | 38% | — | 46% | 38% | 62% | 38% | 42% | 33% | 29% | 62% | 50% | 62% | 29% | 42% |
| **Murasaki** | 79% | 88% | 50% | 50% | 75% | 50% | — | 33% | 62% | 46% | 0% | 67% | 50% | 50% | 54% | 54% | 83% | 75% |
| **Kasumi** | 54% | 29% | 71% | 42% | 42% | 54% | 58% | — | 58% | 54% | 54% | 38% | 58% | 71% | 33% | 58% | 50% | 42% |
| **Okuni** | 33% | 54% | 33% | 33% | 50% | 33% | 38% | 38% | — | 46% | 50% | 33% | 50% | 54% | 54% | 54% | 54% | 38% |
| **Tomoe** | 62% | 50% | 50% | 75% | 25% | 62% | 54% | 33% | 46% | — | 54% | 58% | 46% | 79% | 62% | 67% | 58% | 83% |
| **Anne** | 25% | 50% | 38% | 50% | 54% | 58% | 96% | 38% | 38% | 38% | — | 50% | 83% | 42% | 54% | 54% | 88% | 50% |
| **Julie** | 54% | 46% | 62% | 54% | 67% | 58% | 33% | 54% | 62% | 42% | 50% | — | 42% | 62% | 50% | 54% | 62% | 58% |
| **Ren** | 58% | 4% | 50% | 42% | 29% | 58% | 38% | 33% | 46% | 54% | 8% | 54% | — | 71% | 42% | 29% | 50% | 46% |
| **Chiyo** | 42% | 42% | 25% | 33% | 29% | 33% | 50% | 25% | 42% | 12% | 54% | 29% | 25% | — | 42% | 33% | 42% | 46% |
| **Benkei** | 62% | 21% | 38% | 50% | 46% | 50% | 38% | 62% | 38% | 33% | 42% | 42% | 50% | 50% | — | 54% | 38% | 46% |
| **O-Rin** | 38% | 71% | 25% | 29% | 58% | 29% | 46% | 38% | 38% | 21% | 42% | 42% | 71% | 58% | 33% | — | 54% | 71% |
| **Goro** | 17% | 29% | 62% | 21% | 50% | 71% | 8% | 46% | 42% | 42% | 12% | 38% | 50% | 46% | 58% | 42% | — | 17% |
| **Ichi** | 54% | 54% | 29% | 42% | 62% | 50% | 21% | 38% | 54% | 17% | 42% | 42% | 46% | 46% | 46% | 25% | 75% | — |

## 4. Resultado do Algoritmo Merge Sort de Duelos
O Merge Sort executou uma ordenação por divisão e conquista onde cada decisão de precedência foi arbitrada pelo retrospecto direto de combates:

1. **Saitou** — Winrate Geral: 45.1% (184V / 196D / 28E)
2. **Benkei** — Winrate Geral: 44.6% (182V / 195D / 31E)
3. **Joe** — Winrate Geral: 53.9% (220V / 171D / 17E)
4. **Kasumi** — Winrate Geral: 51.0% (208V / 175D / 25E)
5. **Murasaki** — Winrate Geral: 56.9% (232V / 159D / 17E)
6. **Hanzo** — Winrate Geral: 49.8% (203V / 184D / 21E)
7. **O-Rin** — Winrate Geral: 44.9% (183V / 200D / 25E)
8. **Ichi** — Winrate Geral: 43.6% (178V / 202D / 28E)
9. **Musashi** — Winrate Geral: 52.9% (216V / 172D / 20E)
10. **Ren** — Winrate Geral: 41.9% (171V / 211D / 26E)
11. **Tomoe** — Winrate Geral: 56.9% (232V / 152D / 24E)
12. **Julie** — Winrate Geral: 53.7% (219V / 166D / 23E)
13. **Kenshin** — Winrate Geral: 39.5% (161V / 201D / 46E)
14. **Anne** — Winrate Geral: 53.2% (217V / 169D / 22E)
15. **Goro** — Winrate Geral: 38.2% (156V / 239D / 13E)
16. **Teppo** — Winrate Geral: 40.4% (165V / 221D / 22E)
17. **Okuni** — Winrate Geral: 43.9% (179V / 201D / 28E)
18. **Chiyo** — Winrate Geral: 35.5% (145V / 237D / 26E)

## 5. Avaliação Técnica Aprofundada do Balanceamento

### 5.1 Opressão e Dominância (Top Tiers)
- **Murasaki (56.9%) & Tomoe (56.9%)**:
  - As mecânicas de ataque com prioridade/precedência absoluta, alcance de projéteis instantâneos (snipers) ou frames defensivos de Parry/Riposte garantem uma taxa de vitória esmagadora contra lutadores de aproximação pura.

### 5.2 Vulnerabilidades Críticas (Bottom Tiers)
- **Chiyo (35.5%) & Goro (38.2%)**:
  - Lutadores que dependem de tempos longos de recarga parada (ex: recarga do arcabuz sem cobertura móvel), auto-dano/suicídio por fogo amigo de explosivos, ou windup de retesamento de arco sofrem punições instantâneas contra oponentes rápidos.

### 5.3 Dinâmica de Pedra-Papel-Tesoura e Polarização Extrema
Foram detectados confrontos com polarização extrema (>= 87% de vitória para um lado):
- **Murasaki vs Musashi**: Placar esmagador de 21 a 3 (87.5% de dominância)
- **Musashi vs Ren**: Placar esmagador de 22 a 1 (91.7% de dominância)
- **Anne vs Murasaki**: Placar esmagador de 23 a 0 (95.8% de dominância)
- **Anne vs Goro**: Placar esmagador de 21 a 3 (87.5% de dominância)

## 6. Propostas Concretas de Balance Patch (Recomendações de Design)
Para equalizar o elenco e aproximar todos os combatentes da faixa saudável de 45% a 55% de winrate:
1. **Ajuste de Precedência e Cooldowns de Projéteis**: Aumentar ligeiramente o recovery de golpes com prioridade e projéteis rápidos.
2. **Mobilidade durante a Recarga**: Permitir que classes que recarregam mantenham movimentação a 50% da velocidade, evitando vulnerabilidade estática total.
3. **Redução de Fogo Amigo**: Diminuir o raio de explosão auto-infligido para armas de área (como bombas).
4. **Janela de Defesa (Parry/Riposte)**: Ajustar a janela de parry para exigir timing mais preciso contra sequências rápidas.
