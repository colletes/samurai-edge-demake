# Relatório Comparativo Global de Balanceamento (Easy vs Normal vs Hard)

> **Resumo da Auditoria Completa**:
> - Total de Batalhas Simuladas: **22800 batalhas**
> - Roster: **20 Guerreiros**
> - Arenas: **20 Arenas Temáticas**
> - Níveis de Dificuldade da IA: **Fácil (Easy)**, **Normal (Normal)**, **Difícil (Hard)**

## 1. Tabela Comparativa de Winrates por Dificuldade

| Rank Médio | Lutador | Winrate Easy | Winrate Normal | Winrate Hard | Variação (Hard - Easy) | Comportamento com IA Avançada |
|:---:|:---|:---:|:---:|:---:|:---:|:---|
| 1 | **Valerius** | 74.2% | 71.3% | 68.7% | -5.5% | 📉 Mais eficaz contra novatos / IA previsível |
| 2 | **Seimei** | 60.0% | 70.5% | 60.3% | +0.3% | ⚖️ Desempenho altamente consistente e estável |
| 3 | **Julie** | 55.7% | 54.9% | 57.9% | +2.2% | ⚖️ Desempenho altamente consistente e estável |
| 4 | **Joe** | 49.7% | 57.9% | 60.5% | +10.8% | 📈 Ganha muito valor com reações rápidas da IA |
| 5 | **Murasaki** | 48.8% | 56.2% | 61.8% | +13.0% | 📈 Ganha muito valor com reações rápidas da IA |
| 6 | **Musashi** | 53.2% | 53.5% | 56.3% | +3.2% | 📈 Ganha muito valor com reações rápidas da IA |
| 7 | **Kasumi** | 56.2% | 56.6% | 46.6% | -9.6% | 📉 Mais eficaz contra novatos / IA previsível |
| 8 | **Anne** | 53.0% | 51.2% | 54.1% | +1.0% | ⚖️ Desempenho altamente consistente e estável |
| 9 | **Ichi** | 49.2% | 50.3% | 55.9% | +6.7% | 📈 Ganha muito valor com reações rápidas da IA |
| 10 | **Tomoe** | 42.5% | 55.0% | 54.5% | +12.0% | 📈 Ganha muito valor com reações rápidas da IA |
| 11 | **O-Rin** | 47.1% | 49.2% | 46.5% | -0.7% | ⚖️ Desempenho altamente consistente e estável |
| 12 | **Okuni** | 46.7% | 45.0% | 46.0% | -0.7% | ⚖️ Desempenho altamente consistente e estável |
| 13 | **Benkei** | 50.8% | 45.1% | 40.0% | -10.8% | 📉 Mais eficaz contra novatos / IA previsível |
| 14 | **Hanzo** | 36.3% | 47.4% | 48.3% | +12.0% | 📈 Ganha muito valor com reações rápidas da IA |
| 15 | **Goro** | 42.6% | 39.7% | 48.2% | +5.5% | 📈 Ganha muito valor com reações rápidas da IA |
| 16 | **Ren** | 49.7% | 38.4% | 36.8% | -12.9% | 📉 Mais eficaz contra novatos / IA previsível |
| 17 | **Saitou** | 48.0% | 38.0% | 37.5% | -10.5% | 📉 Mais eficaz contra novatos / IA previsível |
| 18 | **Kenshin** | 46.8% | 38.4% | 37.9% | -9.0% | 📉 Mais eficaz contra novatos / IA previsível |
| 19 | **Chiyo** | 44.0% | 37.8% | 36.5% | -7.5% | 📉 Mais eficaz contra novatos / IA previsível |
| 20 | **Teppo** | 38.8% | 37.0% | 38.7% | -0.1% | ⚖️ Desempenho altamente consistente e estável |

## 2. Comparativo de Posições no Merge Sort

| Lutador | Posição Easy | Posição Normal | Posição Hard | Tendência Global |
|:---|:---:|:---:|:---:|:---|
| **Kenshin** | 11º | 11º | 16º | 🔻 Cai no Hard |
| **Musashi** | 5º | 9º | 4º | Estável |
| **Hanzo** | 20º | 6º | 12º | 🔺 Sobe no Hard |
| **Joe** | 13º | 5º | 2º | 🔺 Sobe no Hard |
| **Saitou** | 9º | 10º | 11º | Estável |
| **Teppo** | 19º | 16º | 17º | Estável |
| **Murasaki** | 14º | 7º | 14º | Estável |
| **Kasumi** | 12º | 4º | 13º | Estável |
| **Okuni** | 18º | 18º | 18º | Estável |
| **Tomoe** | 17º | 3º | 5º | 🔺 Sobe no Hard |
| **Anne** | 6º | 14º | 3º | 🔺 Sobe no Hard |
| **Julie** | 1º | 13º | 1º | Estável |
| **Ren** | 8º | 12º | 15º | 🔻 Cai no Hard |
| **Chiyo** | 10º | 19º | 19º | 🔻 Cai no Hard |
| **Benkei** | 7º | 20º | 20º | 🔻 Cai no Hard |
| **O-Rin** | 16º | 17º | 10º | 🔺 Sobe no Hard |
| **Goro** | 15º | 15º | 9º | 🔺 Sobe no Hard |
| **Ichi** | 2º | 8º | 6º | 🔻 Cai no Hard |
| **Valerius** | 4º | 2º | 8º | 🔻 Cai no Hard |
| **Seimei** | 3º | 1º | 7º | 🔻 Cai no Hard |

## 3. Principais Descobertas do Balanceamento
- **IA Easy (Reações lentas ~380ms)**: Personagens com projéteis rápidos ou ataques de área ampla (Tomoe, Murasaki, Anne) têm vantagem pronunciada, pois a IA não esquiva a tempo.
- **IA Normal (Reações realistas ~230ms)**: Distribuição equilibrada, onde combos e parries pontuais começam a punir ataques telegrafados.
- **IA Hard (Reações cirúrgicas ~145ms & 85% Parry)**: Personagens defensivos e de contra-ataque rápido (Musashi, Julie, Kenshin) sobem de rendimento devido ao timing refinado de defesas.
