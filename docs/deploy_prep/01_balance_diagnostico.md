# 01 — Diagnóstico de Balanceamento (pré-deploy)

> **Método**: IA vs IA (dificuldade `normal`, ambos os lados), motor headless de `tools/simulate_tournament.py`. **Todos os 276 pares × 24 arenas × 2 lados (P1/P2) = 13.248 duelos por réplica**; 2 réplicas com seeds independentes (26,454 duelos válidos no total, ~2.200 por lutador). Cada duelo tem seed determinística (reprodutível). Script: `tools/balance_full_matrix.py`. Dados brutos: `docs/deploy_prep/01_balance_raw.json`.

> **Winrate** = (vitórias + 0,5·empates) / duelos. **Meta do deploy: todo lutador entre 40% e 65%.** Ruído estatístico: ±~1,5 pp por lutador por réplica (medido: Benkei 37,8 → 39,5 e Saitou 64,9 → 65,2 entre réplicas).

## 1. Tier list (média das 2 réplicas, todas as 24 arenas)

| # | Lutador | Arquétipo | WR | Tier | Zen | Urbano | Rural | Extremo | Pior arena | Melhor arena | Pior matchup | Melhor matchup |
|:-:|:--|:--|:-:|:--|:-:|:-:|:-:|:-:|:--|:--|:--|:--|
| 1 | **Teppo** | Marksman (Tanegashima/Pólvora) | **72.8%** ⚠️ | S+ (fora da meta, alto) | 75 | 71 | 74 | 71 | yoshiwara_alley 61% | nagashino_field 90% | Joe 44% | Aoi 90% |
| 2 | **Saitou** | Lobo de Mibu (Gatotsu) | **65.0%** ⚠️ | S+ (fora da meta, alto) | 67 | 68 | 62 | 64 | forest_camp 47% | sacred_pines 75% | Teppo 39% | Goro 86% |
| 3 | **Valerius** | Necromante Prussiano (Foice/Invocações) | **57.5%** | A | 59 | 58 | 57 | 56 | kabuki_stage 48% | sacred_dohyo 68% | Saitou 24% | Anne 88% |
| 4 | **Okuni** | Mestra dos Leques (Tessen/Kawarimi) | **56.8%** | A | 56 | 56 | 57 | 58 | baroque_court 49% | pirate_deck 71% | Teppo 23% | Kenshin 75% |
| 5 | **Joe** | American Ninja (Shuriken/Cão) | **55.6%** | A | 55 | 56 | 55 | 57 | rice_paddies 46% | pirate_deck 63% | Hendrika 35% | Hanzo 82% |
| 6 | **Ichi** | Lâmina Cega (Shikomizue/Gyaku-Iai) | **55.4%** | A | 56 | 57 | 55 | 54 | forest_camp 47% | rice_paddies 64% | Teppo 24% | Goro 90% |
| 7 | **Raiden** | Yokozuna Invicto (Tsuppari/Tachiai) | **54.5%** | A | 55 | 56 | 52 | 55 | forest_camp 43% | ganryu_island 66% | Teppo 22% | Hanzo 74% |
| 8 | **Hendrika** | Alquimista de Dejima (Estilete/5 Reagentes) | **53.1%** | A | 51 | 55 | 54 | 53 | nagashino_field 46% | rain_mill 63% | Teppo 22% | Musashi 88% |
| 9 | **Kenshin** | Retalhador (Iai/Shukuchi) | **52.4%** | A | 53 | 51 | 53 | 53 | kabuki_stage 41% | yoshiwara_alley 61% | Okuni 25% | Hanzo 82% |
| 10 | **Musashi** | Duas Lâminas (Combo/Parry) | **50.9%** | B | 50 | 50 | 51 | 52 | higanbana_garden 42% | forest_camp 61% | Hendrika 12% | Ren 75% |
| 11 | **Murasaki** | Kunoichi Foice (Kusarigama) | **50.8%** | B | 50 | 48 | 54 | 52 | yoshiwara_alley 36% | rain_mill 67% | Anne 10% | Goro 86% |
| 12 | **Anne** | Espadachim (Alfanje 180°) | **50.3%** | B | 53 | 49 | 47 | 51 | rain_mill 41% | shaolin_temple 61% | Valerius 12% | Murasaki 90% |
| 13 | **Ren** | Monge Shaolin (Kiai/Flurry) | **49.4%** | B | 49 | 51 | 48 | 49 | rain_mill 41% | forest_camp 54% | Musashi 25% | Hanzo 79% |
| 14 | **Tomoe** | Arqueira Miko (Arco Yumi) | **49.1%** | B | 49 | 45 | 50 | 52 | dejima_warehouse 37% | shaolin_temple 61% | Valerius 23% | Ren 64% |
| 15 | **Daiki** | Peregrino do Bastão Bō (Pole Vault/Varredura) | **47.8%** | B | 50 | 50 | 47 | 43 | iga_rooftops 38% | shaolin_temple 55% | Teppo 18% | Hanzo 76% |
| 16 | **O-Rin** | Menestrel Acústica (Shamisen/Kamaitachi) | **47.7%** | B | 47 | 47 | 49 | 48 | shadow_cave 39% | gothic_cemetery 57% | Teppo 13% | Chiyo 74% |
| 17 | **Aoi** | Caçadora Ainu (Lança Op/Armadilha de Urso) | **46.4%** | C | 49 | 45 | 46 | 46 | kabuki_stage 37% | forest_camp 56% | Teppo 10% | Benkei 69% |
| 18 | **Seimei** | Onmyoji dos Talismãs (Ofuda/Selo Sagrado) | **46.2%** | C | 46 | 46 | 46 | 47 | gothic_cemetery 32% | mountain_shrine 59% | Teppo 13% | Raiden 67% |
| 19 | **Julie** | Mosqueteira (Florete/Riposte) | **44.0%** | C | 42 | 42 | 45 | 47 | rice_paddies 24% | rain_mill 58% | Teppo 20% | Benkei 84% |
| 20 | **Kasumi** | Kunoichi Névoa (Bombas/Fumaça) | **43.8%** | C | 43 | 46 | 43 | 43 | nagashino_field 35% | forest_camp 55% | Ichi 14% | Anne 70% |
| 21 | **Chiyo** | Lâminas Gêmeas (Dual Nodachi) | **42.7%** | C | 41 | 44 | 43 | 43 | shaolin_temple 33% | shadow_cave 52% | Teppo 23% | Benkei 67% |
| 22 | **Goro** | Fazendeiro da Kuwa (Kuwa Cleave/Pisotão) | **39.1%** ⚠️ | D (fora da meta, baixo) | 40 | 38 | 41 | 38 | dejima_warehouse 29% | nagashino_field 48% | Ichi 10% | Benkei 68% |
| 23 | **Benkei** | Sōhei Monge Guerreiro (Naginata Colossal) | **38.7%** ⚠️ | D (fora da meta, baixo) | 38 | 39 | 39 | 39 | forest_camp 28% | dejima_warehouse 55% | Julie 16% | O-Rin 82% |
| 24 | **Hanzo** | Ninja Mestre (Kunai) | **29.9%** ⚠️ | D (fora da meta, baixo) | 28 | 31 | 34 | 28 | gothic_cemetery 22% | ezo_tundra 43% | Ichi 12% | Benkei 57% |

⚠️ = fora da meta 40–65% (Saitou, em 65,0%, está literalmente no teto).

**Fora da meta hoje:** Teppo (72.8%), Saitou (65.0%), Goro (39.1%), Benkei (38.7%), Hanzo (29.9%).

Tiers: S+ >65 · S 58–65 · A 52–58 · B 47–52 · C 40–47 · D <40.

## 2. Resultados por arena

Lado: P1 venceu 48.7% / P2 51.0% / empate 0.37% (sem viés de lado relevante). Duelos por timeout: 1.4%.

| Arena | Cat. | Duração média | Timeout | Lutadores fora de 40–65% nesta arena |
|:--|:--|:-:|:-:|:--|
| nagashino_field | Rural | 3.3s | 2.9% | 8 |
| forest_camp | Rural | 2.9s | 2.5% | 3 |
| kyoto | Urban | 2.2s | 2.3% | 7 |
| ezo_tundra | Rural | 2.3s | 2.1% | 3 |
| rain_mill | Rural | 2.8s | 1.9% | 8 |
| sacred_pines | Rural | 2.2s | 1.6% | 3 |
| sacred_dohyo | Urban | 2.0s | 1.6% | 7 |
| iga_rooftops | Extreme | 2.9s | 1.4% | 3 |
| pirate_deck | Extreme | 2.2s | 1.4% | 6 |
| higanbana_garden | Zen | 2.6s | 1.4% | 5 |
| shaolin_temple | Zen | 2.1s | 1.3% | 5 |
| gojo_bridge | Extreme | 1.9s | 1.3% | 5 |
| bamboo | Zen | 2.6s | 1.2% | 5 |
| heian_shrine | Zen | 2.0s | 1.1% | 3 |
| gothic_cemetery | Extreme | 1.9s | 1.1% | 6 |
| ganryu_island | Extreme | 2.3s | 1.0% | 5 |
| kabuki_stage | Urban | 2.3s | 1.0% | 3 |
| rice_paddies | Rural | 1.9s | 1.0% | 6 |
| yoshiwara_alley | Urban | 2.3s | 1.0% | 5 |
| dejima_warehouse | Urban | 2.3s | 1.0% | 6 |
| mountain_shrine | Zen | 2.0s | 0.9% | 5 |
| baroque_court | Urban | 2.5s | 0.9% | 3 |
| shadow_cave | Extreme | 2.0s | 0.8% | 6 |
| mist_temple | Zen | 1.7s | 0.0% | 5 |

Nenhuma arena é anômala em duração/timeout (todas ≤ 3,3 s em média e ≤ 2,7% de timeouts). `mist_temple` teve 40 duelos (20 por réplica) abortados pelo **crash `UnboundLocalError: SmokeParticle`** em `src/world/hazards.py` (ver diagnóstico 03); esses duelos estão excluídos.

Contagem de pares (lutador, arena) fora de 40–65% (ruído de ~n=46 por célula é alto, ±7 pp; leia como tendência): Teppo 21/24, Saitou 13/24, Chiyo 8/24, Goro 13/24, Benkei 13/24, Hanzo 23/24.

## 3. Matchups extremos (≥ 85% / ≤ 15%, ~92 duelos cada)

- **Teppo** vence Aoi em 90%
- **Anne** vence Murasaki em 90%
- **Ichi** vence Goro em 90%
- **Valerius** vence Anne em 88%
- **Ichi** vence Hanzo em 88%
- **Hendrika** vence Musashi em 88%
- **Anne** vence Hanzo em 87%
- **Teppo** vence Seimei em 87%
- **Teppo** vence O-Rin em 87%
- **Saitou** vence Goro em 86%
- **Murasaki** vence Goro em 86%
- **Anne** vence Goro em 86%
- **Ichi** vence Kasumi em 86%

Teppo vence 22 dos 23 oponentes (só perde, por pouco, para Joe, ~44%); o único matchup realmente perdido do Saitou é Teppo (~39%). Goro e Hanzo têm matchups perdidos de forma quase absoluta (Goro × Ichi/Murasaki 6%, Hanzo × Joe 8%).

## 4. Propostas de ajuste (NÃO implementadas)

Todas as propostas abaixo foram **simuladas em memória** (sobrescrevendo atributos em instâncias, sem editar o código) com a mesma matriz completa. Resultado do pacote conjunto, médias das 2 réplicas:

| Lutador | WR atual | WR com pacote | Mudança proposta |
|:--|:-:|:-:|:--|
| Teppo | 72.8% | 57.1% | **Nerf** — `Rifleman.aim_duration` 0,22 → **0,38 s** (rifleman.py:247). Telegraph maior da queima da mecha dá janela de esquiva/aproximação. Sensibilidade isolada (só Teppo alterado): 0,32 → 65,9%; 0,38 → 60,9%; 0,45 → 53,1%. Alterar `reload_cooldown` (1,3 → 2,0) ou velocidade quase não move nada (71–74%). |
| Hanzo | 29.9% | 52.8% | **Buff** — `YellowNinja.max_hp/hp` 2 → **3** (yellow_ninja.py; precedente: `BlueSamurai` já tem 3). Único lever que funcionou: kunai_cooldown 1,5→0,9, speed 5,4→6,2, jump/roll cooldown e recuperações juntos chegam a no máx. 36,6%. Obs.: o working tree já traz o buff `hitbox_damage` 1→2 no Reverse Slash (yellow_ninja.py:145) — já incluído na linha de base. |
| Benkei | 38.7% | 52.8% | **Buff** — `BenkeiSamurai.max_hp/hp` 2 → **3** (benkei.py:~50; temático: sōhei tanque). Ajustes de velocidade/duração/alcance da estocada/investida/cooldowns: todos ≤ 39,3% (dentro do ruído). |
| Goro | 39.1% | 43.5% | **Buff** — hyper-armor durante `STATE_EARTH_STOMP` (0,20 s + recuperação): o primeiro golpe fatal recebido nesse estado deixa Goro com 1 HP (e stun 0,35 s, como o dano parcial já faz). Isolado: 45,7%. Hyper-armor também no ataque `ATTACK` ou no `POCKET_DIRT` não ajudou (39,2–39,7%); HP 3 total overshoota (65,1% — vira o novo S+); encurtar o stomp **piora** (35,5%). |
| Saitou | 65.0% | 63.2% | **Sem mudança validada — observar.** Está colado no teto (64,9 / 65,2% isolado; 62–64% após o pacote). O único contra-jogo real dele é Teppo (35–39%), então nerfar Teppo *sobe* o Saitou. Levers testados isoladamente (`max_charge_speed` 14,5→13 + `charge_accel` 12→10; `gatotsu_max_duration`, `turn_rate`, `brake_duration`, `zeroshiki_recovery`, `roll_cooldown`) deram só −0,5 pp. Se passar de 65% na próxima rodada, a opção é o nerf de Gatotsu (13/10) combinado com `brake_duration` 0,05→0,20 (−0,5 pp) e investigar um contra-jogo na IA. |

### Resultado projetado do pacote (Teppo + Hanzo + Benkei + Goro)

| Lutador | Atual | Projetado | Tier projetado |
|:--|:-:|:-:|:--|
| Saitou | 65.0% | 63.2% | S |
| Teppo | 72.8% | 57.1% | A |
| Okuni | 56.8% | 56.3% | A |
| Joe | 55.6% | 55.8% | A |
| Valerius | 57.5% | 55.1% | A |
| Ichi | 55.4% | 53.0% | A |
| Benkei | 38.7% | 52.8% | A |
| Hanzo | 29.9% | 52.8% | A |
| Raiden | 54.5% | 52.5% | A |
| Hendrika | 53.1% | 52.4% | A |
| Murasaki | 50.8% | 51.4% | B |
| Kenshin | 52.4% | 50.3% | B |
| Ren | 49.4% | 50.0% | B |
| Anne | 50.3% | 49.4% | B |
| Musashi | 50.9% | 49.1% | B |
| O-Rin | 47.7% | 47.6% | B |
| Seimei | 46.2% | 45.9% | C |
| Tomoe | 49.1% | 45.6% | C |
| Daiki | 47.8% | 45.0% | C |
| Aoi | 46.4% | 44.9% | C |
| Goro | 39.1% | 43.5% | C |
| Julie | 44.0% | 42.6% | C |
| Kasumi | 43.8% | 42.0% | C |
| Chiyo | 42.7% | 41.8% | C |

Projetado: mín 41.8% / máx 63.2% — **todos dentro de 40–65%** nas duas réplicas (réplica 1: Saitou 62,1 … Chiyo 42,2; réplica 2: Saitou 64,2 … Kasumi 40,8). Margem apertada em **Saitou (teto)** e **Kasumi / Chiyo / Julie (piso, ~41–44%)**: ficam na lista de observação; não há lever validado para elas e a margem de ruído (±1,5 pp) é comparável à folga.

## 5. Ressalvas importantes

- **Isto mede a IA, não jogadores humanos.** Duelos duram ~2 s (HP 2, quase todo golpe é fatal), então o resultado é dominado pelo primeiro contato e pela forma como `ai_controller.py` usa o kit de cada lutador. Para Goro, Benkei e Hanzo, mudanças numéricas de tempo/alcance/cooldown quase não mexeram o winrate (ver tabela) — o que sugere que parte do problema está no **uso do kit pela IA** (distâncias/gatilhos fixos em `ai_controller.py`, `decision_timer` 0,28–0,55 s), não nos números do personagem. Recomendo uma rodada de playtest humano nos 4 lutadores alterados antes de fechar os valores.
- HP 3 para Hanzo/Benkei quebra a convenção "morte em 2 golpes" (comentário em `raiden.py:36`: *padronizado com os outros 23 combatentes*). É a única alavanca que mostrou efeito; é decisão de design. A alternativa (hyper-armor condicional, como proposto para o Goro) preserva o HP padrão mas foi menos eficaz para Benkei (39,3%) — não testei para Hanzo.
- `BALANCE_REPORT*.md` na raiz são de 12/out/2026 (4 arenas, antes das overhauls da Fase 2/3); estão **obsoletos** (ex.: Hanzo 54% lá vs. ~30% hoje; Teppo 69% → 73%).
- Dificuldades `easy`/`hard` e IA com humano não foram simuladas; modo Arcade/boss fora de escopo.
- Efeitos de arena (hazards) rodam na simulação; `mist_temple` perdeu 40 duelos por crash (excluídos).
