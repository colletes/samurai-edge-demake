# 04 — Diagnóstico de FPS (alvo: 60 FPS, referência Steam Deck)

## Veredito

**NÃO.** O jogo **não roda a 60 FPS em nenhuma das 24 arenas no Steam Deck** — e, nas minhas medições, nem no Mac M3 usado como referência ele sustenta 60 FPS de forma consistente: em 18 das 24 arenas mais de 1/3 dos quadros estoura 16,7 ms mesmo no melhor caso medido (14 arenas passam de 50%; a melhor, kabuki_stage, ainda tem ~9% de quadros acima do orçamento). Projetando para o Deck (CPU ~2,5–3,5× mais lenta por thread), a estimativa é de **~20 FPS na mediana (faixa ~12–33 FPS por arena)** na qualidade Alta, e o modo Baixa quase não muda isso (~8% mais rápido na mediana).

> ⚠️ **Isto é uma PROJEÇÃO, não uma medição no Steam Deck.** Não tenho um Deck aqui. O que foi medido de verdade: o loop real do jogo (`main.run_game`) numa Apple M3, em modo headless (SDL dummy). Os números do Deck são M3 × fator. Para fechar a dúvida, rode `tools/fps_benchmark.py` no aparelho (instruções no fim).

## Como foi medido

- **Ferramenta**: `tools/fps_benchmark.py` (novo). Dirige o **loop real do jogo** (`main.run_game`): atravessa título → Versus → seleção → arena, e roda uma partida **IA vs IA** (modo `watch`, rounds ilimitados) com tudo ligado (HUD, iluminação, névoa, partículas, hazards, cinemáticas de fatality, letterbox). Mede o tempo de cada iteração do loop (update + draw + escala para a janela), sem o limitador de 60 FPS. dt do jogo fixo em 1/60 (carga idêntica entre execuções).
- 900–1200 quadros por arena (descartando 30 iniciais), janela 1280×800 (resolução do Deck; o jogo usa canvas lógico 1280×720 com letterbox, escala 1,0), lutadores Kenshin vs Musashi.
- Qualidade **Alta** (padrão) e **Baixa** (`effects_quality: low`), governador automático desligado para isolar cada nível.
- **Ruído**: o Mac estava em uso (Chrome, VS Code, BambuStudio, e agentes de teste meus rodando em paralelo) com *load average* de 5 a 240. Isso inflou muito os tempos (a mesma arena variou até 2× entre execuções: bamboo 17→29 ms, kyoto 29→58 ms). Por isso a tabela usa o **melhor valor (mínimo) de 3 passadas independentes por arena/qualidade**, o estimador menos contaminado por carga externa. Os números reais num aparelho dedicado devem ser iguais ou *melhores* que os do M3 "melhor caso" aqui apenas se o fator de projeção estiver certo — veja as incertezas abaixo.
- Dados brutos por execução (inclui loadavg): `docs/deploy_prep/04_fps_raw_summaries.json`.

## Resultados por arena (melhor de 3 passadas, M3; projeção Deck = ×3,0)

Orçamento para 60 FPS = 16,7 ms/quadro. No Deck, isso exige ≤ ~5,6 ms/quadro medidos no M3 (fator 3,0).

| Arena | Alta p50 (ms) | Alta p95 (ms) | Baixa p50 | Baixa p95 | Deck proj. Alta (FPS, ×2,5 / ×3,0 / ×3,5) | 60 FPS no Deck? |
|:--|:-:|:-:|:-:|:-:|:-:|:-:|
| yoshiwara_alley | 29.4 | 44.3 | 37.2 | 48.8 | 14 / **11** / 10 | ❌ |
| gojo_bridge | 23.7 | 51.8 | 26.1 | 38.6 | 17 / **14** / 12 | ❌ |
| sacred_dohyo | 22.9 | 45.4 | 15.7 | 20.1 | 17 / **15** / 12 | ❌ |
| mist_temple | 21.9 | 31.8 | 10.7 | 24.7 | 18 / **15** / 13 | ❌ |
| dejima_warehouse | 21.7 | 34.0 | 17.7 | 28.9 | 18 / **15** / 13 | ❌ |
| higanbana_garden | 20.5 | 37.0 | 25.5 | 37.8 | 20 / **16** / 14 | ❌ |
| forest_camp | 20.3 | 35.0 | 16.7 | 27.4 | 20 / **16** / 14 | ❌ |
| baroque_court | 19.3 | 29.9 | 14.8 | 20.3 | 21 / **17** / 15 | ❌ |
| sacred_pines | 18.6 | 39.0 | 11.3 | 22.8 | 21 / **18** / 15 | ❌ |
| kyoto | 18.1 | 34.5 | 21.4 | 46.6 | 22 / **18** / 16 | ❌ |
| bamboo | 17.3 | 25.9 | 18.2 | 27.8 | 23 / **19** / 17 | ❌ |
| pirate_deck | 17.2 | 23.0 | 23.5 | 34.7 | 23 / **19** / 17 | ❌ |
| shadow_cave | 16.9 | 27.5 | 13.4 | 20.0 | 24 / **20** / 17 | ❌ |
| iga_rooftops | 16.8 | 28.4 | 21.2 | 36.5 | 24 / **20** / 17 | ❌ |
| mountain_shrine | 16.2 | 26.7 | 13.4 | 20.1 | 25 / **21** / 18 | ❌ |
| rice_paddies | 16.0 | 22.6 | 17.1 | 28.3 | 25 / **21** / 18 | ❌ |
| nagashino_field | 15.0 | 30.1 | 11.1 | 24.9 | 27 / **22** / 19 | ❌ |
| heian_shrine | 15.0 | 27.6 | 14.2 | 19.4 | 27 / **22** / 19 | ❌ |
| rain_mill | 14.4 | 22.7 | 15.3 | 19.4 | 28 / **23** / 20 | ❌ |
| ganryu_island | 14.3 | 28.5 | 14.5 | 21.5 | 28 / **23** / 20 | ❌ |
| ezo_tundra | 13.7 | 18.6 | 10.0 | 18.6 | 29 / **24** / 21 | ❌ |
| gothic_cemetery | 13.6 | 27.1 | 15.7 | 21.2 | 29 / **25** / 21 | ❌ |
| shaolin_temple | 11.9 | 28.1 | 13.0 | 16.2 | 34 / **28** / 24 | ❌ |
| kabuki_stage | 10.1 | 20.4 | 15.6 | 24.0 | 40 / **33** / 28 | ❌ |

Mediana entre arenas (M3, melhor caso): Alta p50 **17.0 ms**, Baixa p50 **15.6 ms** (ganho ~8%). Melhor arena (kabuki_stage, shaolin_temple) ~10–12 ms → ~28–33 FPS projetados; pior (yoshiwara_alley) ~29 ms → ~11 FPS. O p95 (microtravadas) é 1,5–2× o p50 em quase toda arena.

**Observações**
- A diferença Alta × Baixa é pequena e inconsistente (em algumas arenas Baixa foi *mais lenta*, dentro do ruído). O modo Baixa corta partículas/névoa/texturas de material, mas o custo dominante está na rasterização dos voxels, que ele não toca. O **governador automático** (`quality.update_fps_governor`, cai para Baixa abaixo de 48 FPS) portanto **não salva** o Deck.
- Os valores de p50 incluem partidas com cinemática de fatality (letterbox + câmera) — picos reais de jogo, não só idle.
- `mist_temple`: a arena **crasha** no loop real (ver 03); as medições dela usam um contorno só no benchmark (`--hotfix-mist`, sem alterar o código do jogo).

## Onde o tempo vai (cProfile, yoshiwara_alley / gojo_bridge / bamboo)

O renderer é **imediato, 100% CPU, single-thread, em Python puro** (pygame, sem GPU): cada quadro redesenha o mundo isométrico voxel por voxel.

- `draw_world_queue` (`main.py:1318`) = **~64–70% do tempo do quadro**.
- `voxel_renderer.draw_voxel_box` (`src/isometric/voxel_renderer.py:44`): ~270 caixas/quadro → ~2.000–2.600 `pygame.draw.polygon` e ~4.000–6.000 chamadas a `Camera.apply`/`world_to_iso` por quadro (Python puro, ~2 M chamadas por 400 quadros).
- `render_voxel_humanoid` (`src/entities/voxel_models.py:256`): **os 2 lutadores são re-rasterizados voxel a voxel a cada quadro** (~5–17 ms cada sob profiler) — 24–60% do desenho. Sem cache de sprite por pose.
- `arena_generator.render_terrain` (`:913`) 13–55% conforme a arena (gojo_bridge pior: `_draw_pit` + `_draw_water`).
- `bamboo.py` render: ~25% do quadro na arena bamboo (55 mil chamadas / 320 quadros).
- `lighting.render` + `fog.render` + ambience: ~10–12%.
- `Surface.blit` ~10–20% e `transform.scale` ~4–8% (SSAA 2× dos lutadores).

## Caminho para 60 FPS no Deck (necessário: ~3× mais rápido)

Em ordem de custo/benefício (estimativas qualitativas; não implementei nem validei):
1. **Cache de sprites dos lutadores** por (modelo, pose, ângulo de câmera, escala) — elimina a re-rasterização de ~2.000 voxels/quadro; é o maior item isolado (maior alvo: `render_voxel_humanoid`).
2. **Pré-renderizar (bake) o terreno e props estáticos** numa superfície única por arena e só redesenhar sprites dinâmicos + ordenação por profundidade (já existe `arena_cache.py` / `build_static_render_queue`; hoje `render_terrain` + `bamboo.render` ainda rodam por quadro).
3. **Vetorizar a projeção** (`Camera.apply`/`world_to_iso`: 2–2,6 M chamadas por 400 quadros) — numpy em lote ou projeção pré-computada por tile.
4. Perfil de qualidade **Deck** (resolução interna menor, p.ex. 960×540 com upscale, SSAA 2× desligado nos lutadores, menos `FogVolume`/partículas), usado por padrão quando detectar Linux/SteamOS.
5. Alternativa de maior escopo: mover a rasterização para GPU (`pygame._sdl2`/moderngl) ou multiprocessar (Deck tem 4C/8T; o jogo usa 1 thread).

Meta intermediária realista antes do deploy, se não houver tempo para 1–3: **travar em 30 FPS no Deck** (dt fixo 1/30 + perfil de qualidade Deck) — as projeções de pior arena ainda ficariam em ~11–14 FPS, então ainda exigiria o item 1.

## Incertezas da projeção (seja crítico com os números do Deck)

- **Fator M3→Deck (2,5–3,5×)** é estimativa por desempenho single-thread (Geekbench 6 SC: M3 ≈ 3.000; Deck/Zen 2 a 15 W ≈ 1.000–1.200) e por Python 3.11 ser limitado por IPC/frequência. Pode ser menor (ex.: cache/memória mais favoráveis) ou maior (throttle térmico/15 W compartilhado com a iGPU sob carga).
- Não medi: SteamOS/Linux, SDL2 com Wayland/X11 e *present* real da janela (o benchmark usa SDL dummy; o custo de apresentação — upload de 1280×800 — não está incluído, tipicamente 1–3 ms no Deck), áudio ativo (o mixer fica em `dummy`), controle/entrada real, vsync.
- Carga externa no Mac: ver ruído acima. Mínimo de 3 passadas mitiga mas não elimina.
- Uma única dupla de lutadores (Kenshin vs Musashi) em todas as arenas; lutadores com mais efeitos (Hendrika, Seimei, O-Rin, Valerius com invocações, Joe com cão) podem ser mais pesados. Não rodei a varredura por lutador.
- Só IA vs IA (modo `watch`); humano vs IA tem a mesma renderização.

## Como medir no Steam Deck (recomendado antes do deploy)

```bash
# no Deck (modo Desktop), com o venv do jogo:
python tools/fps_benchmark.py --arena kyoto --frames 1800 --quality high --window 1280x800 --out /tmp/kyoto_high.json            # SDL dummy: mede só o custo de CPU
python tools/fps_benchmark.py --arena kyoto --frames 1800 --quality auto --real-display --out /tmp/kyoto_real.json            # janela real (NÃO testado por mim); o jogo deve rodar em tela cheia/Game Mode
```
O JSON tem `summary` (p50/p95/p99/máx, % de quadros > 16,7 ms, nível de qualidade final do governador) e `frames_ms`. Critério de aprovação sugerido: p95 ≤ 16,7 ms em todas as 24 arenas (e p99 ≤ 25 ms).

