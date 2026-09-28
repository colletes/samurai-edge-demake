# 🗺️ ROADMAP — Samurai Edge Demake

> **Versão atual:** `v1.3.3` → commit `2a53dbb` | **Branch:** `main`  
> Última atualização: Setembro 2026  
> Este documento consolida o **Plano Mestre das 9 Frentes** (sessão anterior) com os **20 Patches Críticos** e as melhorias recentes de balanceamento.

---

## ✅ Concluído

### Fundação — v1.0 a v1.2
- [x] Motor de combate isométrico voxel 3D com câmera y-sorted
- [x] 12 guerreiros jogáveis com mecânicas únicas
- [x] Arena **Floresta de Bambu** (bambus cortáveis, lago Zen)
- [x] Arena **Kyoto Bakumatsu** (carruagens, escombros, chamas nos telhados, lanternas)
- [x] Sistema de colisão e hitbox com i-frames e parry
- [x] Build automatizado com GitHub Actions (macOS / Linux / Windows)
- [x] Suporte nativo a gamepads (Xbox, DualShock 4, DualSense PS5)
- [x] Controles touchscreen adaptativos (Android / iOS) com analógico virtual flutuante
- [x] Manual estratégico in-game (`F1`) com fichas dos 12 guerreiros
- [x] i18n bilíngue (PT-BR / EN) com alternância instantânea
- [x] Retratos HD-2D dos guerreiros; tela de carregamento com barra de progresso

### Plano Mestre — Prioridades Imediatas (concluídas)
- [x] **Ícones PlayStation em SVG** — `assets/icons/playstation/` + `src/ui/svg_icon_renderer.py` + integração em `settings_menu.py` e `controller_manager.py`
- [x] **3ª Ação Universal (Roll / Dash dedicado)** — `○ Círculo` / `T` (P1) / `O` (P2): esquiva específica por personagem (Kenshi: Iai Slide; Kasumi: Mist Roll; Tomoe: Kagitsuru Rope Hook; etc.)
- [x] **Novas Ações Secundárias** — Okuni: *Dokukiri* (Veneno em Cone); Anne: *Naval Artillery Strike* (Hold & Release com mobilidade); Teppo: *Black Powder Ground Trap*; Kenshi: *Tsuka-ate*

### Plano Mestre — Frente 1: Animações Idle & Caminhada
- [x] Respiração senoidal (*idle bob*) em `voxel_models.py`
- [x] Marcha orgânica (*step bob* com pernas articuladas) para todos os 12 guerreiros

### Plano Mestre — Frente 2: Mortes Renovadas (parcial)
- [x] Fragmentação voxel do corpo em `src/entities/voxel_corpse.py`
- [x] Flash de lâmina cinematográfico e hitstop Kurosawa P&B (`CinematicDirector`)
- [x] Corpo voxel fatiado pós-fatalidade no Y-sorting

### 20 Patches Críticos — v1.3 (todos verificados com testes automatizados)
- [x] **Kasumi — Mina Remota:** auto-dano garantido (1 HP) mesmo em i-frames de dodge
- [x] **Kasumi — Bomba de Fumaça (Dash):** 48+ partículas volumétricas, `alpha=15`, `stealth_timer=1.6s`; sombra escala com opacidade; rastro contínuo durante o deslocamento
- [x] **Kenshi — Ryuu Tsui Sen:** corte descendente vertical (de `wz=2.6m`), invulnerável na subida, pós-imagens *zanzou*
- [x] **Kenshi — Travamento Iai:** bloco `STATE_ATTACK` restaurado; Shukuchi com pós-imagens translúcidas
- [x] **Murasaki — Escudo Frontal:** deflexão da Kusarigama em cone de 120° (projéteis pelas costas passam)
- [x] **Murasaki — Foice Kama:** modelo voxel de lâmina curvada, alcance 1.30m
- [x] **Murasaki — Dash:** sem faíscas; efeito sombrio de teletransporte ninja
- [x] **Julie — Cape Flourish:** movido para a esquiva; duração 0.16s; deflexão frontal (180°) com i-frames completos; musket bullet passa através durante dodge
- [x] **Julie — Animação Coup de Pied:** capa 3D giratória + extensão de perna
- [x] **Julie — Banner de morte:** `POCKET FLINTLOCK SNIPE!`
- [x] **Flintlock — Alcance:** limitado a 5.8 tiles
- [x] **Joe — Cão Yamato:** atordoa apenas em `STATE_DOG_CHARGE` / `STATE_DOG_BARK`
- [x] **Tomoe — Flecha de Corda:** `rope_cooldown = 2.0s`
- [x] **Hanzo — Kunai:** clamped nos limites do mapa; ângulo descendente correto no salto
- [x] **Anne — Indicador de Lentidão:** fuligem preta nos pés
- [x] **Okuni — Dokukiri:** cone frontal, pushback, frenzy +25% velocidade, -20% cooldown
- [x] **HUD Cooldowns:** atributos corrigidos para todos os 12 guerreiros
- [x] **Controles P2:** tecla `I` → "Cancelar"; `ESC` bloqueado durante gameplay
- [x] **Obstáculos sólidos:** faíscas e hitstop generalizados (rochas, poço, lanternas, Torii, carruagens)
- [x] **Rumble tátil:** vibração em golpes fatais, clashes, explosões, atordoamentos

### Balanceamento Anne & Julie — v1.3 (buffs pós-simulação de 1.584 lutas)
- [x] Anne: avanço 0.65m, hitbox alfanje 1.55m, ciclo tap/hold/release do canhão
- [x] Julie: Fleche hitbox 0.70m, recovery 0.18s; Flintlock secondary exclusivo
- [x] Deflexão de projéteis com verificação completa de i-frames (dodge, CAPE_FLOURISH, SHUKUCHI)

---

## 🔴 Alta Prioridade — v1.4 (Performance)

> [!CAUTION]
> O slowdown ao atingir obstáculos com o Ryuu Tsui Sen é causado por dois problemas combinados abaixo. Corrigir antes de qualquer feature nova.

### Perf-1 — Surface pool de partículas (principal gargalo de FPS)
- [ ] `SmokeParticle.render()` cria um `pygame.Surface(SRCALPHA)` novo por partícula a cada frame. Com picos de 48–80 partículas (fumaça Kasumi + impacto Ryuu), são dezenas de alocações por frame → GC stutter.
- [ ] **Solução:** pool pré-alocada por bucket de tamanho (4px a 44px), reutilizando superfícies. Ou redesenhar com `pygame.draw.circle` diretamente + `BLEND_RGBA_SUB`.
- [ ] **Arquivo:** `src/effects/particles.py` — `SmokeParticle.render()`

### Perf-2 — Hitstop em cascata ao atingir obstáculos (stutter Ryuu Tsui Sen)
- [ ] Hitbox do Ryuu (raio 1.45m) se sobrepõe à rocha → `_check_obstacle_sparks` seta `hitstop_timer=0.06s` → loop principal faz `continue` e congela tudo. Se a hitbox ainda sobrepõe no próximo frame, repete → stutter de 2–5 frames.
- [ ] **Soluções:**
  - Ignorar obstáculos durante descida aérea (`wz > 0.5`); hitstop de obstáculo só ao pousar
  - Cooldown por obstáculo: não re-triggar se o mesmo sólido causou hitstop nos últimos 0.25s
  - Reduzir `hitstop_timer` de obstáculo de `0.06s` para `0.04s`
- [ ] **Arquivo:** `src/combat/collision.py` — `_check_obstacle_sparks()`

### Perf-3 — Y-sort global a cada frame
- [ ] `render_queue.sort()` ordena ~80 itens (estáticos + dinâmicos + partículas) a cada frame.
- [ ] **Solução:** separar fila estática (pré-ordenada, atualizada apenas ao cortar bambu) da fila dinâmica (fighters + partículas). Mesclar com `heapq.merge()`.
- [ ] **Arquivo:** `main.py` — bloco de render (linhas ~1000–1065)

### Perf-4 — Cap global de partículas
- [ ] Sem limite, rajadas de combate acumulam 200+ partículas. Cap de `MAX_PARTICLES = 150`: novas partículas cosméticas são descartadas; `FloatingBanner` e `BloodParticle` nunca são descartados.
- [ ] **Arquivo:** `main.py` — linha 988

---

## 🟠 Alta Prioridade — v1.4 (Plano Mestre — Frente 3: Áudio)

> [!NOTE]
> Nenhum código de áudio existe hoje. `pygame.mixer` não é inicializado em nenhum lugar do projeto.

### Sound-1 — SoundManager (arquitetura)
- [ ] Criar `src/audio/sound_manager.py` — singleton com cache, volume global, canais SFX dedicados
- [ ] Criar `src/audio/sound_events.py` — enum de todos os eventos sonoros
- [ ] Criar `assets/sounds/sfx/` e `assets/sounds/music/` com placeholders procedurais (gerados via `numpy` + `pygame.sndarray`) para funcionar sem assets externos desde o primeiro dia
- [ ] Inicializar `pygame.mixer` em `main.py` (44100 Hz, 16-bit, estéreo)

### Sound-2 — SFX de combate e movimentação
- [ ] Golpe fatal → `sword_hit.ogg` (grave, lento)
- [ ] Clash de espadas / parry → `sword_clash.ogg`
- [ ] Explosão (bomba, canhão) → `bomb_explode.ogg`
- [ ] Canhão naval Anne → `cannon_fire.ogg`
- [ ] Pistola Flintlock Julie → `gunshot_flintlock.ogg`
- [ ] Tanegashima (Teppo) → `tanegashima_shot.ogg`
- [ ] Flecha Yumi: lançamento + impacto → `arrow_release.ogg` / `arrow_hit.ogg`
- [ ] Shuriken → `shuriken_throw.ogg`
- [ ] Ryuu Tsui Sen → `ryuu_tsui_sen_whoosh.ogg`
- [ ] Bomba de fumaça Kasumi → `smoke_puff.ogg`
- [ ] Passos (grama / pedra) → `footstep_grass.ogg` / `footstep_stone.ogg` (a cada 0.35s)
- [ ] Round start / round win → `round_start.ogg` / `round_win.ogg`

### Sound-3 — BGM por arena + menu
- [ ] Tela de título: `bgm_menu.ogg` — Taiko e Shamisen relaxante
- [ ] Floresta de Bambu: `bgm_bamboo.ogg` (fade in de 2s)
- [ ] Kyoto Bakumatsu: `bgm_kyoto.ogg` (fade in de 2s)
- [ ] Fade out de 0.5s entre rounds; fanfare de vitória
- [ ] Controles de volume independentes (música vs SFX) no menu de configurações

---

## 🟡 Média Prioridade — v1.4 / v1.5

### Plano Mestre — Frente 2 (complemento): Kanjis Kurosawa
- [ ] Kanjis de impacto em nanquim no flash cinematográfico: *一刀両断* (Ittō Ryōdan), *決闘終焉* (Kettō Shūen), etc.
- [ ] Renderizados com fonte `Zen Antique` sobre o flash P&B do `CinematicDirector`
- [ ] **Arquivo:** `src/effects/cinematic_director.py`

### Plano Mestre — Frente 4: 3ª Arena — Telhados de Kyoto & Templo em Chamas
- [ ] Criar `src/world/rooftop_map.py`
- [ ] Cumeeiras de telhados com pontes suspensas destrutíveis
- [ ] Flechas flamejantes horizontais periódicas
- [ ] Rajadas de vento que empurram combatentes para abismos (knockback contextual)
- [ ] Chamas vivas no templo com iluminação dinâmica

### Plano Mestre — Frente 5: IA Tática e Reativa
- [ ] Controle de distância (*footsies*): manter distância ótima por arquétipo (curta/média/longa)
- [ ] Fintas e punição de *whiff*: IA identifica recovery do adversário e pune
- [ ] Esquiva proativa de perigos do cenário (carruagens, escombros, flechas flamejantes)
- [ ] Três níveis de dificuldade: Iniciante (30% aleatório) / Normal (atual) / Mestre (prevê posição 0.3s à frente)
- [ ] **Arquivo:** `src/entities/ai_controller.py`

### Plano Mestre — Frente 6: Clash de Espadas (Tsubazeriai / QTE Arcade)
- [ ] Criar `src/combat/clash_system.py`
- [ ] Ao cruzarem lâminas: choque de faíscas contínuas + zoom dramático
- [ ] Janela curta de QTE no centro superior da tela:
  - Botão vermelho de arcade: animação física de compressão 3D e pulso iluminado
  - Texto **"STRIKE!"** em fonte `Shojumaru` do título
- [ ] Integrar ao sistema de `CLASH!` já existente em `collision.py`

### Plano Mestre — Frente 7: Apresentação Cinematográfica de Round (Sumi-E)
- [ ] Criar `src/ui/round_intro.py`
- [ ] Órbita de 45° da câmera em torno dos combatentes antes do round
- [ ] Pergaminho vertical com nome e título do guerreiro em `Shojumaru` + `Zen Antique`
- [ ] Estrondo de Taiko sincronizado com o pergaminho

### Balanceamento Tier D (simulação de 1.584 lutas — winrates abaixo de 35%)
- [ ] **Kenshin (29.6%):** recovery Iai 0.35s → 0.25s ao acertar; Shukuchi com 0.12s i-frame real; IA usa evasão quando encurralado
- [ ] **Murasaki (29.2%):** velocidade da corrente 8.5 → 11.0 u/s; dano de hook (+1 HP no puxão); hitbox Kama 0.18s → 0.22s
- [ ] **Kasumi (28.4%):** sem auto-dano com ≤ 2 HP; raio de auto-dano × 0.6; Mina delay 0.40s → 0.28s
- [ ] **Hanzo (26.9%):** kunai recolhível após 1.5s; IA: salto+kunai a 2.5–4.5m (45%); segundo arremesso no ar
- [ ] **Joe/Yamato (23.9%):** hesitação do cão 0.4s → 0.15s; velocidade de charge 5.5 → 7.0; shuriken +1 HP; IA: shuriken como abridor a 3–5m

### Tomoe — Ação Secundária (pendente decisão do jogador)
- [ ] **Opção 1 (Recomendada): Hamaya Sagrada** — flecha ritual que perfura obstáculos e anula projéteis; rastro dourado
- [ ] Opção 2: Chuva Sagrada de Flechas (Yabusame) — 5 flechas em parábola, chovem após 0.6s
- [ ] Opção 3: Barreira dos Ventos Kami — 3 talismãs orbitais repelindo ataques por 0.8s
- [ ] Opção 4: Kyu-jutsu Bo Strike — pancada melee com a haste do arco, stun 0.4s

---

## 🟢 Baixa Prioridade — v1.5

### Plano Mestre — Frente 8: Iluminação Dinâmica & FX Atmosféricos
- [ ] Criar `src/effects/lighting.py`
- [ ] Luz de chamas refletida nas pedras de Kyoto (overlay aditivo laranja pulsante)
- [ ] Vaga-lumes bioluminescentes sobre o lago da Floresta de Bambu
- [ ] Relâmpagos noturnos na Arena de Telhados

### UX — Tela de Resultados pós-round
- [ ] Criar `src/ui/round_result.py`: vencedor, golpe fatal, HP restante, tempo
- [ ] Animação: flash branco → tela preta → fade in; rematch com `Espaço`

### UX — Contador de Rounds (Best of 3)
- [ ] `p1_rounds_won` / `p2_rounds_won` no estado do jogo
- [ ] HUD: ícones de round (katana cruzada) acima das barras de HP
- [ ] Tela "MATCH WINNER" ao encerrar BO3

### UX — Efeitos cinematográficos do Ryuu Tsui Sen
- [ ] Zoom suave da câmera (+10%) quando `wz > 2.0`
- [ ] Overlay de desaturação gradual até o impacto

### UX — Sombras de projéteis no chão
- [ ] Bomba, flecha do Yumi e canhão projetam sombra diretamente abaixo durante a trajetória balística

---

## 🔵 Futuro — v2.0

### Plano Mestre — Frente 9: Modo Arcade & Boss Oni Esqueleto (Gashadokuro)
- [ ] Criar `src/arcade/arcade_mode.py` — campanha completa com torneio de 8 adversários
- [ ] Criar `src/entities/boss_oni.py` — **Gashadokuro** com 5 fases de transformação voxel:
  1. Colosso com Facões Gigantes
  2. Serpente de Ossos
  3. Rebatedor Breakout
  4. Clava de Ossos
  5. Caveira Flamejante (fase final)

### Feat — Modo Training
- [ ] Personagens imortais; input exibido frame a frame; dummies com HP infinito

### Feat — Torneio Local (4 / 8 jogadores)
- [ ] Chaveamento automático de eliminatória simples com árvore na tela

### Feat — Leaderboard & Estatísticas Locais
- [ ] Histórico das últimas 50 partidas em JSON; tela de winrate por personagem

---

## 🧪 Estado das Suítes de Testes

| Suíte | Testes | Status |
|---|:---:|:---:|
| `test_game.py` (sistema geral) | 21 | ✅ 100% |
| `tests/test_patches_and_improvements.py` | 19 | ✅ 100% |
| `tests/test_anne_and_julie_buffs.py` | 9 | ✅ 100% |
| `tests/test_controllers_and_touch.py` | 7 | ✅ 100% |
| `tests/test_tomoe_hold_release.py` | 5 | ✅ 100% |
| `tests/test_step2_actions.py` | 6 | ✅ 100% |
| `tests/test_phase3_controls_and_persistence.py` | 4 | ✅ 100% |
| `tests/test_phase1_fighters.py` | — | ⚠️ 1 falha (`cape_timer` desatualizado após refactor do Repel) |
| `tests/test_kawarimi_and_poison.py` | — | ⚠️ 1 falha (banner Okuni com wording desatualizado) |
| `tests/test_modifications_review.py` | — | ⚠️ 1 falha (`TSUKA_ATE` check desatualizado) |
| `tests/test_settings_and_hanzo_jump.py` | — | ⚠️ 1 falha (label menu configurações desatualizado) |
| `tests/test_controller_commands_and_selection.py` | — | ⚠️ 1 falha (glyph PS5 DualSense desatualizado) |
| `tests/test_phase2_hud_and_round_start.py` | — | ❌ `ModuleNotFoundError: src` (executar da raiz com `./venv/bin/python3`) |
| `tests/test_idle_walk_animations.py` | — | ❌ `ModuleNotFoundError: src` |
| `tests/test_p2_character_confirmation.py` | — | ❌ `ModuleNotFoundError: src` |

> **71 testes passando com 100%** nas suítes principais.  
> Suítes ⚠️: assertions legadas desatualizadas após refactors — não refletem bugs reais no jogo.  
> Suítes ❌: problema de `sys.path` — funcionam corretamente ao executar com `./venv/bin/python3 tests/<nome>.py` da raiz.

---

## 📦 Próxima Release: v1.4

**Escopo mínimo:**
1. `Perf-1` + `Perf-2` — eliminar slowdown do Ryuu Tsui Sen (obrigatório)
2. `Sound-1` + `Sound-2` — SoundManager com placeholders procedurais
3. Balanceamento Tier D (Kasumi, Hanzo, Joe prioritários)
4. Unificação das suítes de testes legadas (⚠️ e ❌)
5. Decisão e implementação da ação secundária de Tomoe
