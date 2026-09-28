# 🗺️ ROADMAP — Samurai Edge Demake

> **Versão atual:** `v1.3.3` (HEAD) | **Branch:** `main`  
> Última atualização: Setembro 2026

---

## ✅ Concluído

### v1.0 — Fundação do Jogo
- [x] Motor de combate isométrico voxel 3D com câmera y-sorted
- [x] 12 guerreiros jogáveis com mecânicas únicas
- [x] Arena Floresta de Bambu (interativa: bambus cortáveis)
- [x] Arena Kyoto Bakumatsu (carruagens, escombros, lanternas)
- [x] Sistema de colisão e hitbox com i-frames
- [x] IA adversária por personagem
- [x] Build automatizado com GitHub Actions (macOS / Linux / Windows)

### v1.1 — Controles & Qualidade de Vida
- [x] Suporte nativo a gamepads (Xbox, DualShock 4, DualSense PS5)
- [x] Controles touchscreen adaptativos (Android / iOS)
- [x] Analógico virtual flutuante
- [x] Manual estratégico in-game (`F1`) com fichas dos 12 guerreiros
- [x] i18n bilíngue (PT-BR / EN) com alternância instantânea
- [x] Haptic rumble no spawn do round

### v1.2 — Polimento Visual & Efeitos
- [x] Overhaul visual Sumi-e na tela de título e seleção
- [x] Retratos HD-2D dos guerreiros
- [x] Pós-imagens *zanzou* no Shukuchi do Kenshi
- [x] Rastro de sangue e fatalities cinematográficos (Kurosawa Flash)
- [x] Corpo voxel fatiado pós-fatalidade
- [x] Tela de carregamento com barra de progresso

### v1.3 — 20 Patches Críticos de Mecânica e Balanceamento
- [x] **Kasumi — Mina Remota:** auto-dano garantido mesmo em i-frames de dodge
- [x] **Kasumi — Dash:** emite fumaça densa + invisibilidade (`alpha=15`) em vez de faíscas; janela de stealth de 1.6s; sombra do personagem escala com opacidade
- [x] **Kasumi — Bomba de fumaça:** 48+ partículas volumétricas ao usar a esquiva; rastro contínuo de fumaça durante o deslocamento
- [x] **Kenshi — Ryuu Tsui Sen:** corte descendente vertical (de `wz=2.6m`), invulnerável durante a subida
- [x] **Kenshi — Travamento Iai:** bloco `STATE_ATTACK` restaurado em `red_samurai.py`; cooldown de recovery corrigido
- [x] **Murasaki — Escudo frontal:** deflexão da Kusarigama restrita a cone de 120° (projéteis pelas costas passam)
- [x] **Murasaki — Foice Kama:** modelo voxel com lâmina curvada em formato de foice + aura de energia; alcance 1.30m; rastro de ataque orientado
- [x] **Murasaki — Dash:** sem faíscas; efeito sombrio de teletransporte ninja
- [x] **Julie — Cape Flourish:** movido para a tecla de esquiva; duração 0.16s; deflexão de projéteis **apenas frontais** (cone 180° de frente); projéteis nas costas passam; invulnerabilidade total durante a esquiva
- [x] **Julie — Animação Coup de Pied:** capa 3D giratória + extensão de perna (`CAPE_FLOURISH` state)
- [x] **Julie — Banner de morte:** exibe `POCKET FLINTLOCK SNIPE!` em vez de `TANEGASHIMA HEADSHOT`
- [x] **Flintlock — Alcance:** limitado a 5.8 tiles (era 18.0 do rifle Tanegashima)
- [x] **Joe — Cão Yamato:** só atordoa quando em `STATE_DOG_BARK` / `STATE_DOG_CHARGE`; imune a golpes em modo `FOLLOW`
- [x] **Tomoe — Flecha de Corda:** cooldown de 2.0s implementado
- [x] **Hanzo — Kunai:** clamped dentro dos limites do mapa; ângulo descendente corrigido no salto
- [x] **Anne — Indicador de Lentidão:** fuligem preta nos pés do personagem afetado por `slow_timer`
- [x] **Okuni — Dokukiri:** veneno em cone frontal com pushback; frenzy +25% de velocidade e -20% cooldown ao envenenar
- [x] **HUD Cooldowns:** nomes de atributos corrigidos para Kasumi, Okuni, Murasaki e Tomoe
- [x] **Controles P2:** tecla `I` remapeada para "Voltar/Cancelar"; `ESC` não interfere no gameplay
- [x] **Obstáculos sólidos:** faíscas e hitstop generalizados (rochas, poço, lanternas, carruagens, Torii)
- [x] **Rumble tátil:** vibração em golpes fatais, clashes, explosões, atordoamentos

### v1.3 — Buffs de Balanceamento Anne & Julie
- [x] **Anne — Alfanje:** avanço de 0.65m; hitbox varredor de 1.55m; cooldown canhão 4.5s
- [x] **Anne — Canhão:** ciclo completo tap (disparo imediato) e hold (mira livre); IA dispara corretamente
- [x] **Anne — Black Powder Dash:** fumaça cegante na colisão; mini-stun de 0.40s
- [x] **Julie — Fleche Thrust:** hitbox 0.70m; recovery 0.18s (era 0.28s)
- [x] **Julie — Flintlock:** secondary exclusivo com cooldown 4.5s
- [x] **Deflexão de projéteis com i-frames completos:** musket bullet passa através de qualquer guerreiro em dodge ativo

---

## 🔴 Alta Prioridade — v1.4

### Perf-1 — Eliminar alocação de Surface por frame no renderer de partículas
> **Causa do slowdown no Ryuu Tsui Sen e explosões**

- [ ] `SmokeParticle.render()` cria um novo `pygame.Surface(SRCALPHA)` a cada frame por partícula. Com picos de 48–80 partículas simultâneas, são dezenas de alocações por frame causando GC stutter.
- [ ] **Solução:** Surface pool pré-alocada por tamanho (buckets 4px a 44px) reutilizável. Ou redesenhar usando `pygame.draw.circle` diretamente com `pygame.BLEND_RGBA_SUB`.
- [ ] **Arquivo:** `src/effects/particles.py` — `SmokeParticle.render()`

### Perf-2 — Hitstop em cascata ao atingir obstáculos sólidos com hitbox grande
> **Causa do slowdown forte ao atingir pedras com o Ryuu Tsui Sen**

- [ ] Quando `hitbox_radius = 1.45m` (Ryuu Tsui Sen) se sobrepõe a uma rocha, `_check_obstacle_sparks` seta `hitstop_timer = 0.06s` e o loop principal executa `continue` — congela tudo. Se a hitbox ainda sobrepõe no frame seguinte, repete → stutter em cascata.
- [ ] **Soluções:**
  - Ignorar obstáculos durante descida aérea (`wz > 0.5`); hitstop de obstáculo só ao pousar.
  - Cooldown por obstáculo: não re-triggar se o mesmo sólido causou hitstop nos últimos 0.25s.
  - Reduzir `hitstop_timer` de obstáculos de `0.06s` para `0.04s`.
- [ ] **Arquivo:** `src/combat/collision.py` — `_check_obstacle_sparks()`

### Perf-3 — Y-sort global a cada frame
- [ ] `render_queue.sort()` em `main.py` linha 1065 ordena ~80 itens (inclui todas as partículas) a cada frame. Separar fila estática (pré-ordenada) da fila dinâmica (fighters + partículas) e só re-ordenar a dinâmica.
- [ ] **Arquivo:** `main.py` — bloco de render (linha ~1000–1065)

### Perf-4 — Cap global de partículas
- [ ] Sem limite, rajadas de combate acumulam 200+ partículas simultâneas. Implementar `MAX_PARTICLES = 150`: partículas cosméticas novas são descartadas quando o pool está cheio.
- [ ] **Arquivo:** `main.py` — linha 988 (`particles = [p for p in particles if p.update(dt)]`)

---

## 🟠 Alta Prioridade — v1.4

### Sound-1 — Arquitetura do SoundManager
- [ ] Criar `src/audio/sound_manager.py` — singleton com cache, volume global, canais SFX.
- [ ] Criar `src/audio/sound_events.py` — enum/constantes de todos os eventos sonoros.
- [ ] Criar `assets/sounds/sfx/` e `assets/sounds/music/` com placeholders procedurais (gerados via `numpy` + `pygame.sndarray`) para funcionar sem assets externos.
- [ ] Inicializar `pygame.mixer` em `main.py` com frequência 44100 Hz, 16-bit, estéreo.

### Sound-2 — SFX de Combate
- [ ] Golpe fatal → `sword_hit.ogg`
- [ ] Clash de espadas / parry → `sword_clash.ogg`
- [ ] Explosão (bomba, canhão) → `bomb_explode.ogg`
- [ ] Canhão naval → `cannon_fire.ogg`
- [ ] Pistola Flintlock → `gunshot_flintlock.ogg`
- [ ] Flecha Yumi (lançamento / impacto) → `arrow_release.ogg` / `arrow_hit.ogg`
- [ ] Shuriken → `shuriken_throw.ogg`
- [ ] Ryuu Tsui Sen → `ryuu_tsui_sen_whoosh.ogg`
- [ ] Fumaça / bomba de fumaça → `smoke_puff.ogg`
- [ ] Passos no campo / pedra → `footstep_grass.ogg` / `footstep_stone.ogg` (a cada 0.35s)
- [ ] Round start / round win → `round_start.ogg` / `round_win.ogg`

### Sound-3 — Música de fundo por arena
- [ ] Tela de título: `bgm_menu.ogg` em loop
- [ ] Floresta de Bambu: `bgm_bamboo.ogg` com fade in de 2s
- [ ] Kyoto Bakumatsu: `bgm_kyoto.ogg` com fade in de 2s
- [ ] Fade out de 0.5s entre rounds
- [ ] Controles independentes de volume (música vs SFX) no menu de configurações

---

## 🟡 Média Prioridade — v1.4 / v1.5

### Balance-1 — Kenshin / Musashi (Winrate: 29.6% / 33.7%)
- [ ] Iai: reduzir recovery de `0.35s` para `0.25s` quando acerta
- [ ] Shukuchi: 0.12s de i-frame mesmo sem `is_invulnerable_dodge` (pós-imagens visuais já existem)
- [ ] IA: usar Shukuchi para evasão quando encurralado (`dist < 1.5m`), não apenas para aproximação

### Balance-2 — Murasaki (Winrate: 29.2%)
- [ ] Velocidade da corrente Kusarigama: 8.5 → 11.0 unidades/s
- [ ] Dano de hook: 1 HP ao puxar e oponente bater no solo
- [ ] Duração da hitbox da Kama: 0.18s → 0.22s

### Balance-3 — Kasumi (Winrate: 28.4%)
- [ ] Auto-dano da bomba: `damage=0` quando Kasumi tem ≤ 2 HP (evitar suicídio)
- [ ] Raio de auto-dano reduzido para `explosion_radius * 0.6`
- [ ] Mina Remota: delay de armamento 0.40s → 0.28s

### Balance-4 — Hanzo (Winrate: 26.9%)
- [ ] Kunai recolhível após 1.5s no chão (em vez de desaparecer)
- [ ] IA: usar salto + kunai a 2.5–4.5m com 45% de probabilidade
- [ ] Segundo arremesso no ar: Kunai extra com cooldown total de 4s

### Balance-5 — Joe / Yamato (Winrate: 23.9%)
- [ ] Cão: reduzir hesitação antes do `STATE_DOG_CHARGE` de 0.4s → 0.15s
- [ ] Cão: velocidade em `STATE_DOG_CHARGE` de 5.5 → 7.0
- [ ] Shuriken: +1 HP de dano quando oponente não está stunned
- [ ] IA: shuriken como abridor a 3–5m antes de aproximar com o cão

---

## 🟢 Baixa Prioridade — v1.5

### UX-1 — Tela de Resultados pós-round
- [ ] Criar `src/ui/round_result.py` com exibição de: vencedor, golpe fatal, HP restante, tempo
- [ ] Animação: flash branco → tela preta com texto → fade in
- [ ] Input de rematch: `Espaço` / `Enter` / botão A reinicia com os mesmos personagens

### UX-2 — Contador de Rounds (Best of 3)
- [ ] Variáveis `p1_rounds_won` / `p2_rounds_won` no estado do jogo
- [ ] HUD: ícones de round (katana cruzada) acima das barras de HP
- [ ] Match encerra ao atingir 2 vitórias de round (BO3)
- [ ] Tela "MATCH WINNER" ao final

### UX-3 — Efeito cinematográfico no Ryuu Tsui Sen
- [ ] Zoom suave da câmera (+10%) quando `wz > 2.0`
- [ ] Overlay de desaturação gradual até o impacto

### UX-4 — Poses de vitória e introdução
- [ ] `STATE_VICTORY`: animação de espada levantada para o vencedor
- [ ] Frase de vitória por personagem (2–3 frases de texto)
- [ ] "Round N — FIGHT!": texto animado com fade in + som

### UX-5 — Sombras de projéteis no chão
- [ ] Projéteis em trajetória balística (bomba, flecha, canhão) projetam sombra no `wx, wy` para indicar altura

---

## 🔵 Futuro — v2.0

### Feat-1 — Modo Training
- [ ] Personagens imortais, input exibido frame a frame
- [ ] Útil para aprender timings de Iai, Ryuu Tsui Sen, etc.

### Feat-2 — IA Adaptativa (níveis de dificuldade)
- [ ] Iniciante (30% ações aleatórias), Normal (atual), Mestre (prevê posição do oponente 0.3s à frente)
- [ ] Selecionável no menu de configurações

### Feat-3 — Torneio Local (4 / 8 jogadores)
- [ ] Chaveamento automático de eliminatória simples
- [ ] Árvore de torneio exibida na tela

### Feat-4 — Leaderboard & Estatísticas Locais
- [ ] Histórico das últimas 50 partidas em JSON
- [ ] Tela de estatísticas: winrate por personagem, golpe mais usado

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
| `tests/test_modifications_review.py` | — | ⚠️ 1 falha (`TSUKA_ATE` state check desatualizado) |
| `tests/test_settings_and_hanzo_jump.py` | — | ⚠️ 1 falha (label do menu de configurações desatualizado) |
| `tests/test_controller_commands_and_selection.py` | — | ⚠️ 1 falha (glyph PS5 DualSense desatualizado) |
| `tests/test_phase2_hud_and_round_start.py` | — | ❌ `ModuleNotFoundError: src` (rodar da pasta raiz) |
| `tests/test_idle_walk_animations.py` | — | ❌ `ModuleNotFoundError: src` (rodar da pasta raiz) |
| `tests/test_p2_character_confirmation.py` | — | ❌ `ModuleNotFoundError: src` (rodar da pasta raiz) |

> **Total validado:** 71 testes passando com 100% de sucesso nas suítes principais.  
> As suítes com ⚠️ contêm testes legados com assertions desatualizadas após refactors — não refletem bugs reais.  
> As suítes com ❌ precisam ser executadas com `./venv/bin/python3 tests/<nome>.py` a partir da raiz do projeto.

---

## 📦 Próxima Release Planejada: v1.4

**Escopo mínimo para v1.4:**
1. Correções de performance (Perf-1 e Perf-2 obrigatórias)
2. Sistema de som básico (Sound-1 + Sound-2 com placeholders)
3. Balanceamento Tier D (Balance-3 a Balance-5)
4. Unificação das suítes de testes legadas (⚠️ e ❌ acima)
