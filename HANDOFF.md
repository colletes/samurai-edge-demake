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

# 5. Execução em cadeia de todos os testes principais
./venv/bin/python3 test_game.py && ./venv/bin/python3 tests/test_patches_and_improvements.py && ./venv/bin/python3 tests/test_anne_and_julie_buffs.py
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
│   ├── audio/                       # [A SER CRIADO NA FASE 2] SoundManager e sintetizador procedural
│   ├── combat/
│   │   ├── collision.py             # CombatSystem: detecção de hit, parry, deflexão e faíscas em obstáculos
│   │   └── clash_system.py          # [A SER CRIADO NA FASE 5] Disputa de espadas QTE STRIKE
│   ├── effects/
│   │   ├── cinematic_director.py    # Fatal strike em câmera lenta, P&B e desmembramento
│   │   ├── particles.py             # SparkParticle, SmokeParticle, BloodParticle, FloatingBanner
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

O projeto acabou de consolidar a **Versão 1.3.3** com todos os 20 patches críticos aprovados e testados (commit `42ae791`). O plano de trabalho unificado está registrado no [`ROADMAP.md`](file:///Users/thiagocarvalho/Documents/Sample%20Game/ROADMAP.md).

### 👉 PRÓXIMA TAREFA A EXECUTAR: FASE 1 (Performance & Estabilidade)

A IA sucessora deve focar **exclusivamente** na **Fase 1**:

1. **Entregável 1.1 (`src/effects/particles.py`):**
   * Implementar pooling de superfícies para `SmokeParticle.render()`.
   * Criar dicionário de cache pré-alocado `_SMOKE_SURF_POOL` indexado pelo raio `r`.
2. **Entregável 1.2 (`src/combat/collision.py` e `src/entities/red_samurai.py`):**
   * Eliminar o slowdown do Ryuu Tsui Sen ao atingir rochas/sólidos.
   * Adicionar condição `if fighter.wz > 0.4: return` em `_check_obstacle_sparks`.
   * Adicionar cooldown de hitstop por obstáculo no combatente (`obstacle_spark_timer`).
   * Reduzir o tempo de hitstop em obstáculos para `0.035s`.
3. **Entregável 1.3 & 1.4 (`main.py`):**
   * Separar fila estática e dinâmica de Y-Sorting.
   * Aplicar cap global de 150 partículas (`MAX_PARTICLES = 150`).
4. **Validação:**
   * Criar o arquivo de teste `tests/test_performance_and_particles.py`.
   * Executar `./venv/bin/python3 tests/test_performance_and_particles.py` e garantir 100% de sucesso.
   * Executar os 21 testes de regressão em `./venv/bin/python3 test_game.py`.

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
