# 🤝 HANDOFF — Samurai Edge Demake

> **Data de Atualização:** 30 de Setembro de 2026  
> **Branch:** `main` | **Último Commit:** `42ae791` (ou posterior)  
> **Finalidade:** Documento de transição e guia operacional completo para qualquer desenvolvedor ou modelo de IA assumir o projeto imediatamente, sem perda de contexto ou retrabalho.

---

## 📌 1. Visão Geral do Projeto

* **Gênero:** Jogo de luta e duelo samurai de morte súbita (*1-Hit Kill / Lethal Strike*), inspirado em clássicos como *Bushido Blade* e *Kengo*.
* **Estilo Visual:** Isométrico tridimensional em estilo Voxel 3D, com arte inspirada em xilogravura japonesa (*Sumi-E*), iluminação estilizada e direção cinematográfica de Akira Kurosawa (cortes P&B com nanquim).
* **Tecnologias:**
  * **Linguagem:** Python 3.11.x
  * **Engine Gráfica/Input:** `pygame-ce` (Pygame Community Edition >= 2.5.0)
  * **Matemática Isométrica:** Módulos matemáticos puros customizados (`src/isometric/iso_math.py`)
  * **Plataformas Alvo:** macOS, Linux, Windows (desktop via PyInstaller) + iOS/Android (mobile touch nativo).

---

## 🚀 2. Ambiente de Desenvolvimento e Comandos Rápidos

> [!IMPORTANT]
> **SEMPRE utilize o interpretador do ambiente virtual local:** `./venv/bin/python3`.  
> Nunca use `python` ou `python3` global do sistema operacional para evitar divergência de bibliotecas compiladas (`pygame-ce`, `SDL2`).

### 🎮 Como Executar o Jogo
```bash
# Execução normal no macOS / Linux
./venv/bin/python3 main.py
```

### 🧪 Como Rodar as Suítes de Testes
Todos os testes são desenvolvidos para rodar tanto em modo gráfico quanto em modo **Headless** (definindo `SDL_VIDEODRIVER=dummy` e `SDL_AUDIODRIVER=dummy`).

```bash
# 1. Suíte Principal de Sistema (21 testes de integração)
./venv/bin/python3 test_game.py

# 2. Suíte dos 20 Patches e Mecânicas Críticas (19 testes)
./venv/bin/python3 tests/test_patches_and_improvements.py

# 3. Suíte de Balanceamento Anne & Julie e Deflexão Cônica (9 testes)
./venv/bin/python3 tests/test_anne_and_julie_buffs.py

# 4. Suíte de Controles e Touchscreen (7 testes)
./venv/bin/python3 tests/test_controllers_and_touch.py

# 5. Suíte de Performance e Partículas da Fase 1 (4 testes)
./venv/bin/python3 tests/test_performance_and_particles.py

# 6. Suíte de Arquitetura de Áudio e SFX Feudal da Fase 2 (6 testes)
./venv/bin/python3 tests/test_audio_system.py

# 7. Execução em cadeia de todos os testes principais
./venv/bin/python3 test_game.py && ./venv/bin/python3 tests/test_performance_and_particles.py && ./venv/bin/python3 tests/test_audio_system.py
```

---

## 📂 3. Arquitetura de Pastas e Módulos-Chave

```
Sample Game/
├── main.py                          # Loop principal do jogo, Y-Sorting, câmera e estados de duelo
├── ROADMAP.md                       # O plano mestre das 7 fases iterativas
├── HANDOFF.md                       # Este documento de transição técnica
├── test_game.py                     # Suíte de integração geral (21 testes)
├── assets/                          # Fontes orientais, ícones SVG PlayStation, portraits HD-2D
│   ├── fonts/                       # Shojumaru, Zen Antique Soft, Noto Sans JP
│   ├── icons/playstation/           # Vetores SVG dos botões PS5/PS4
│   └── portraits/                   # Retratos 2D dos 12 lutadores
├── src/
│   ├── audio/                       # SoundManager Singleton, sintetizador procedural PCM e enums
│   │   ├── sound_events.py          # Identificadores de 24 SFX e 3 trilhas BGM
│   │   ├── procedural_sfx.py        # Sintetizador procedural puro 16-bit 44.1kHz em memória
│   │   └── sound_manager.py         # Cache, canais, controle de volume Master/SFX/BGM e crossfade
│   ├── combat/
│   │   ├── collision.py             # CombatSystem: detecção de hit, parry, deflexão e faíscas em obstáculos
│   │   └── clash_system.py          # [A SER CRIADO NA FASE 5] Disputa de espadas QTE STRIKE
│   ├── effects/
│   │   ├── cinematic_director.py    # Fatal strike em câmera lenta, P&B e desmembramento
│   │   ├── particles.py             # SparkParticle, SmokeParticle (com Surface Pooling), BloodParticle
│   │   └── lighting.py              # [A SER CRIADO NA FASE 6] Iluminação 2.5D dinâmica
│   ├── entities/
│   │   ├── samurai.py               # Classe-base com estados: IDLE, ATTACK, PARRY, RECOVERY, ROLL, DEAD
│   │   ├── red_samurai.py           # Kenshin (Iaijutsu, Ryuu Tsui Sen aéreo, Shukuchi com zanzou)
│   │   ├── gray_ninja.py            # Kasumi (Mina remota, bomba de fumaça stealth, adagas)
│   │   ├── musketeer.py             # Julie (Florete, Cape Flourish com Coup de Pied, Flintlock 5.8m)
│   │   ├── pirate.py                # Anne Bonny (Alfanje varredor 180°, canhão orbital tap/hold)
│   │   ├── purple_ninja.py          # Murasaki (Kusarigama, foice Kama curva, escudo frontal 120°)
│   │   ├── kyudo_archer.py          # Tomoe (Arco Yumi com retesamento, flecha-corda evasiva)
│   │   ├── american_ninja.py        # Joe (Ninjutsu militar, shurikens de choque, cão Doberman Yamato)
│   │   ├── doberman.py              # Cão Yamato (estados: FOLLOW, BARK, CHARGE, KNOCKED_OUT)
│   │   ├── projectile.py            # Flechas, balas de rifle/pederneira, minas, bombas em arco 3D
│   │   └── voxel_models.py          # Renderizador 3D voxel de humanos, armas, capas e sombras dinâmicas
│   ├── input/
│   │   └── controller_manager.py    # Gamepads SDL, mapeamentos DualSense/Xbox, rumble háptico
│   ├── isometric/
│   │   ├── camera.py                # Câmera com interpolação suave (lerp) e screenshake
│   │   └── iso_math.py              # Conversão cartesiano 3D (wx, wy, wz) <-> tela isométrica
│   ├── ui/
│   │   ├── character_select.py      # Tela de seleção com navegação 2D, retratos e modos 1P/2P
│   │   ├── settings_menu.py         # Configurações de teclado, gamepads com ícones SVG e idioma
│   │   ├── loading_screen.py        # Tela de transição com barra de carregamento
│   │   └── strategy_manual.py       # Manual tático in-game (F1) com visualizador de atributos
│   └── world/
│       ├── map_data.py              # Arena 1: Floresta de Bambu (bambus cortáveis, poço Tsukubai)
│       └── kyoto_map.py             # Arena 2: Kyoto Bakumatsu (machiyas, carruagens, escombros)
└── tests/                           # Suítes de testes automatizados específicos
```

---

## 🧠 4. Regras de Design e Convenções Inegociáveis

1. **Invulnerabilidade de Esquiva (`is_invulnerable_dodge`):**
   * Durante esquivas ativas (`STATE_ROLL`, `CAPE_FLOURISH`, `SHUKUCHI`, `KAWARIMI_ROLL`), o lutador possui `is_invulnerable_dodge = True`.
   * Projéteis físicos (balas, flechas, kunais) que cruzarem com o personagem nesse intervalo **NÃO devem ser destruídos nem detonados**; eles devem passar através do lutador sem causar dano.
2. **Deflexão Direcional de Projéteis:**
   * Deflexões de escudo (Kusarigama de Murasaki e Capa de Julie) exigem verificação cônica frontal (`dot > 0.0`). Projéteis que atingem as costas do defensor **sempre** acertam.
3. **Cão Yamato de Joe:**
   * O cão só pode sofrer atordoamento/dano se estiver atacando (`STATE_DOG_CHARGE` ou `STATE_DOG_BARK`). No modo `STATE_DOG_FOLLOW`, ele é imune a cortes para evitar que vire um escudo passivo indesejado.
4. **Alocação de Memória em Render Loop:**
   * **NUNCA** instancie `pygame.Surface(..., pygame.SRCALPHA)` repetidamente dentro de loops de renderização de partículas ou modelos voxel a cada frame. Sempre utilize superfícies pré-alocadas (pooling) ou desenhos diretos na superfície principal.
5. **Hitstop de Impacto:**
   * O hitstop pausa o loop do jogo por breves frações de segundo para dar sensação de peso ao golpe. Deve possuir cooldown rígido para não disparar em múltiplos frames consecutivos contra o mesmo obstáculo estático.

---

## 🎯 5. Onde Estamos e Qual a Próxima Ação Imediata

* **Fase 1 (Performance & Estabilidade):** ✅ **100% CONCLUÍDA E TESTADA**.
  - Entregável 1.1 (Surface pooling de `SmokeParticle`): ativo e eliminando alocações contínuas de memória.
  - Entregável 1.2 (Hitstop anti-cascata e altitude check no Ryuu Tsui Sen): corrigido com `wz <= 0.40`, cooldown de 0.25s e 0.035s de hitstop.
  - Entregável 1.3 (Y-Sorting estático vs dinâmico): fila estática `build_static_render_queue` implementada no início do round.
  - Entregável 1.4 (Particle Cap Global): limite rígido de 150 partículas preservando sangue e banners.
  - Testes: `tests/test_performance_and_particles.py` passando com 100% (4/4 testes).

* **Fase 2 (Arquitetura de Áudio & SFX Feudal):** ✅ **100% CONCLUÍDA E TESTADA**.
  - Entregável 2.1 (`SoundManager` & Síntese Procedural Fallback): síntese pura PCM 16-bit 44.1kHz em memória gerando 24 sons feudais sem assets externos obrigatórios.
  - Entregável 2.2 (Integração de SFX em Combate): choques de lâmina, deflexões, parry, fatal strikes, tiros de arcabuz/pederneira, canhão, veneno Dokukiri, passos e abertura/vitória de round conectados.
  - Entregável 2.3 (BGM Player com Crossfade): transições musicais suaves entre título/seleção (`TITLE_THEME`), Floresta de Bambu (`BAMBOO_THEME`) e Kyoto Bakumatsu (`KYOTO_THEME`).
  - Entregável 2.4 (Controles de Volume na UI & Persistência): sliders interativos de SFX e BGM em `SettingsMenu` com botões `[-]`/`[+]`, barras clicáveis e atalhos de teclado, salvos em `controls_config.json`.
  - Testes: `tests/test_audio_system.py` passando com 100% (6/6 testes).

### 👉 PRÓXIMA TAREFA A EXECUTAR: FASE 3 (Saneamento de Testes Legados & Ação Secundária de Tomoe)

A IA sucessora ou desenvolvedor deve focar na **Fase 3**:

1. **Entregável 3.1: Tomoe — Ação Secundária Sagrada (*Hamaya*):**
   * Flecha ritual perfurante de luz sagrada (*Hamaya* / 破魔矢) com rastro dourado, capaz de atravessar obstáculos sólidos e anular projéteis inimigos em voo.
   * Arquivos: `src/entities/kyudo_archer.py`, `src/entities/projectile.py`, `main.py`.
2. **Entregável 3.2: Kanjis Kurosawa no Flash Cinematográfico:**
   * Renderizar caligrafia Sumi-E kanji sobre o golpe final fatal (*一刀両断*, *決闘終焉*) com a fonte estilizada.
   * Arquivo: `src/effects/cinematic_director.py`.
3. **Entregável 3.3: Saneamento das 5 Suítes Legadas de Testes:**
   * Atualizar asserts legados que ainda procuravam atributos antigos em `tests/test_phase1_fighters.py`, `test_kawarimi_and_poison.py`, `test_modifications_review.py`, `test_settings_and_hanzo_jump.py` e `test_controller_commands_and_selection.py`.
4. **Validação:**
   * Garantir que todas as suítes em `tests/` rodem com 100% de sucesso.


---

## 💡 6. Dicas de Ouro para a Nova IA

* Se você precisar testar comportamentos sem abrir janela visual, lembre-se de configurar:
  ```python
  import os
  os.environ["SDL_VIDEODRIVER"] = "dummy"
  os.environ["SDL_AUDIODRIVER"] = "dummy"
  import pygame
  pygame.init()
  ```
* Se deparar com erros de importação nos testes (`ModuleNotFoundError: No module named 'src'`), garanta que o caminho raiz esteja no `sys.path`:
  ```python
  import sys, os
  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
  ```
* Se for commitar ou fazer push para o GitHub, sempre confirme se a suíte de testes passou sem erros antes de enviar.

---
*Pronto para continuar. Siga a ordem numérica das Fases no `ROADMAP.md` e mantenha a excelência técnica de 100% de testes verdes!*
