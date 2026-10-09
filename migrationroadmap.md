# Roadmap de Migração — Samurai Edge (Edição HD-2D & Micro-voxels)

Este documento estabelece o planejamento técnico detalhado para a migração completa do jogo **Samurai Edge** para a arquitetura visual **HD-2D** (Pixel Art de alta definição ancorado no plano isométrico) integrada ao motor volumétrico de **Micro-voxels 3D** (Showroom e Galeria), assegurando **suporte obrigatório e otimizado a macOS** (Apple Silicon M1/M2/M3/M4 e Intel x86_64) a **60 FPS** constantes.

---

## 1. Visão Geral e Princípios Arquiteturais

### 1.1. Diretriz Visual Unificada
- **Gameplay de Duelo:** Renderização via **Sprites HD-2D** (72x80 px por frame, ancoragem de pés `FEET_Y = 72`), com animações fluídas por estado (`idle`, `walk_0`, `walk_1`, `attack`, `recovery`, `stunned`, `dead`), iluminação dinâmica, sombras elípticas de contato no solo e efeitos visuais dramáticos (cortes de lâmina, vento cortante, chamas e pétalas).
- **Showroom e Cinemáticas de Exposição:** Renderização 3D em tempo real via **Micro-voxels Procedurais** de alta densidade (`src/entities/microvoxel_roster.py`), com rotação 360° livre, permitindo inspecionar cada detalhe das vestimentas e armas das artes conceituais.
- **Transição Limpa e Descarte das Abordagens Inadequadas:** As opções de Mapeamento UV afim (T2), Voxel com Overlays 2.5D (T3) e Low-Poly Cel-Shaded tradicional (T4) foram testadas, avaliadas e **descartadas**. O visual definitivo do jogo combina a agilidade e charme nostálgico dos **Sprites HD-2D** em combate com a fidelidade volumétrica dos **Micro-voxels** no visualizador.

### 1.2. Requisito Obrigatório: Suporte Nativo a macOS
O ecossistema macOS possui particularidades severas de renderização gráfica que tornam este requisito central:
1. **Depreciação do OpenGL pela Apple:** Não depender de PyOpenGL ou extensões antigas de OpenGL que causam crashes ou emulação lenta por software no macOS.
2. **Backend Nativo Metal via SDL2 / Pygame-CE:** Utilização estrita de `pygame-ce` (Community Edition >= 2.5.0), que utiliza o backend SDL2 compilado com suporte nativo a **Metal** e aceleração de hardware nas GPUs da Apple (M1 a M4) e AMD/Intel integradas.
3. **Escalonamento HiDPI / Retina Display:** Prevenção de borrão (blur) bilinear em telas Retina de MacBooks, garantindo integer scaling (escalonamento inteiro por vizinho mais próximo) com nitidez cristalina em pixels.
4. **Sem Dependências Binárias C/C++ Incompatíveis:** Manter a base em Python puro + Pygame-CE/SDL2 para evitar problemas de compilação ou falhas de assinatura de código (codesign) no Gatekeeper do macOS.

---

## 2. Diagnóstico dos Ativos e Estado Atual

| Componente | Estado Atual | Localização no Projeto |
| :--- | :--- | :--- |
| **Model Inspector (Micro-voxels)** | ✅ Concluído com 12 personagens e menus clicáveis | `tools/model_inspector.py` |
| **Motor de Micro-voxels Roster** | ✅ Concluído (Okuni, Kasumi, Saitou + 9 lutadores) | `src/entities/microvoxel_roster.py` |
| **Sprites HD-2D: Combatentes Piloto** | ✅ Concluído (Okuni, Kasumi, Saitou) | `assets/sprites/{okuni,kasumi,saitou}/` |
| **Sprites HD-2D: Combatentes Legados** | ✅ Concluído (Kenshi, Murasaki) | `hd2d_edition/assets/sprites/{kenshi,murasaki}/` |
| **Sprites HD-2D: Restantes do Elenco** | ⏳ Pendente (Musashi, Hanzo, Tomoe, Teppo, Joe, Anne, Julie) | A gerar na Fase 1 |
| **Motor Isométrico HD-2D Base** | ✅ Validado na branch `hd2d_edition` | `hd2d_edition/src/isometric/hd2d_renderer.py` |
| **Suporte e Validação macOS** | ✅ Testado em macOS Darwin (Apple Silicon / Python 3.11) | Suporte nativo confirmado |

---

## 3. Cronograma de Migração por Fases

### Fase 1: Padronização dos Spritesheets HD-2D para o Elenco Completo
**Objetivo:** Completar os 7 lutadores restantes e empacotar todas as spritesheets no padrão unificado `72x80`.

- [x] **1.1. Geração dos Combatentes Piloto da Demo Técnica:**
  - Okuni (Dançarina Kabuki com leques Tessen duplos).
  - Kasumi (Kunoichi da Névoa com armadura cromada e cachecol).
  - Saitou (Capitão Shinsengumi com haori azul-celeste e estocada Gatotsu).
- [ ] **1.2. Geração dos 7 Combatentes Restantes:**
  - `musashi`: Mestre Niten Ichi-ryu com kimono azul cobalto e duas lâminas.
  - `hanzo`: Ninja de Iga com máscara oni dourada e adagas shinobi.
  - `tomoe`: Arqueira Miko sagrada com hakama vermelho e arco yumi longo.
  - `teppo`: Atirador Tanegashima com jingasa de ferro e arcabuz de mecha.
  - `joe`: American Ninja tático com camuflagem e bandana militar.
  - `anne`: Capitã Pirata com sobretudo bordô, tricórnio e alfanje cortante.
  - `julie`: Mosqueteira Real com casaca azul, chapéu de pluma e florete.
- [ ] **1.3. Exportação e Validação de Assets:**
  - Gerar `spritesheet_<char>.png` (fita horizontal de 504x80 px) para cada um dos 12 personagens.
  - Gerar a folha mestra comparativa do elenco (864x240 px).
  - Validar canal alfa RGBA sem halos pretos ou cinzas em torno dos contornos.

---

### Fase 2: Arquitetura de Renderização e Otimização para macOS
**Objetivo:** Integrar o motor HD-2D ao pipeline principal, garantindo 60 FPS contínuos e compatibilidade no Mac.

- [ ] **2.1. Configuração do Backend SDL2 Metal no macOS:**
  ```python
  import os, sys
  if sys.platform == "darwin":
      os.environ["SDL_RENDER_DRIVER"] = "metal"
      os.environ["SDL_HINT_RENDER_SCALE_QUALITY"] = "nearest"  # Pixel art sem blur em telas Retina
  ```
- [ ] **2.2. Sistema de Cache e Blit Eficiente:**
  - Manter dicionário global `_HD2D_CACHE` com chaves `(char_key, frame_name, flip, alpha)`.
  - Pré-carregar na inicialização do jogo todos os frames do jogador e adversário para evitar `image.load` em tempo real durante duelos.
  - Usar superfícies nativas convertidas com `.convert_alpha()` imediatamente após o carregamento.
- [ ] **2.3. Fallback Automático para Micro-voxels:**
  - Se um frame de sprite estiver ausente ou corrompido, a entidade recorre automaticamente a `render_microvoxel_fighter(c, char_type)`, impedindo crashes e garantindo que o jogo nunca falhe visualmente.

---

### Fase 3: Migração das Entidades e Lógica de Combate
**Objetivo:** Atualizar os combatentes para usar o novo motor gráfico mantendo a precisão das hitboxes e timings.

- [ ] **3.1. Conexão das Entidades dos Combatentes:**
  - Atualizar a classe base `Samurai` e as 12 subclasses (`Kabuki`, `GrayNinja`, `SaitouSamurai`, etc.) para chamar `HD2DSpriteRenderer.render_fighter(...)` no método `render()`.
- [ ] **3.2. Sincronização de Timings e Animações:**
  - **Windup:** Frame `idle` ou postura pré-ataque.
  - **Active / Strike:** Frame `attack.png` alinhado ao momento exato em que `hitbox_active = True`.
  - **Recovery:** Frame `recovery.png` com recolhimento de lâmina/arma.
  - **Stunned:** Frame `stunned.png` com recuo e faíscas.
  - **Dead:** Frame `dead.png` com silhueta no solo e sombra correta.
- [ ] **3.3. Sombra de Solo Elíptica e Efeitos de Partícula:**
  - Sombra com opacidade suave (`alpha = 130`) fixada na coordenada `(wx, wy, 0.0)`.
  - Partículas de folhas, faíscas e sangue cinemático desenhadas na camada correta (depth-sorting).

---

### Fase 4: Interface, Menus e Modo Museu (Showroom 3D)
**Objetivo:** Entregar experiência de usuário polida com menus clicáveis e galeria interativa de micro-voxels.

- [ ] **4.1. Integração do Model Inspector como "Galeria de Combatentes":**
  - Adicionar opção "Galeria de Guerreiros 3D" no menu principal do jogo.
  - Incorporar a tela de inspeção com órbita 360°, exibição dos concepts originais e botões de seleção de personagens totalmente clicáveis com mouse ou gamepad.
- [ ] **4.2. Tela de Seleção de Personagens com Sprites HD-2D:**
  - Cards de personagens exibindo o sprite animado em idle com paleta de cores correspondente.
- [ ] **4.3. Suporte a Controles no macOS:**
  - Suporte out-of-the-box para Apple Magic Mouse, Trackpad (gestos de pinça e arrasto suave), teclados Mac (Cmd, Option, teclado ABNT2/US) e controles Bluetooth (DualSense / Xbox / Nintendo Switch).

---

### Fase 5: Empacotamento, Testes de Regressão e Distribuição macOS
**Objetivo:** Gerar executável nativo do macOS sem dependências externas.

- [ ] **5.1. Construção do Pacote macOS (.app Bundle):**
  - Configurar script de build com `pyinstaller` visando macOS universal (`arm64` + `x86_64`):
  ```bash
  pyinstaller --noconfirm --onedir --windowed \
    --name "Samurai-Edge-HD2D" \
    --icon "assets/icon.icns" \
    --add-data "assets:assets" \
    main.py
  ```
- [ ] **5.2. Verificação de Integridade e Sandbox TCC:**
  - Validar caminhos relativos de leitura/gravação usando `os.path.abspath(os.path.dirname(__file__))`.
  - Garantir que arquivos de save e configurações sejam gravados em diretório de aplicação apropriado (`~/Library/Application Support/SamuraiEdge/` no macOS).
- [ ] **5.3. Benchmark Contínuo de Performance:**
  - Executar simulação de 100 duelos consecutivos via `simulate_tournament.py` validando taxa estável de **60.0 FPS** e consumo de memória inferior a 250 MB.

---

## 4. Matriz de Riscos e Estratégias de Mitigação no macOS

| Risco Identificado | Impacto | Estratégia de Mitigação |
| :--- | :--- | :--- |
| **Blur em telas Retina (HiDPI)** | Médio (Degradação visual) | Forçar `SDL_HINT_RENDER_SCALE_QUALITY = "nearest"` e trabalhar com resolução nativa escalonada por inteiros. |
| **Permissões de Disco (macOS TCC Sandbox)** | Alto (Falha de carregamento) | Manter caminhos estritamente contidos dentro do bundle `.app` para assets somente-leitura e usar `Application Support` para dados de escrita. |
| **Garbage Collector Spikes** | Médio (Queda momentânea de FPS) | Cache estático de superfícies transformadas (`_HD2D_CACHE`) para evitar recriação contínua de superfícies RGBA a cada frame. |
| **Diferença de Layout de Teclado no Mac** | Baixo (Ergonomia) | Mapeamento automático de teclas com suporte a setas direcionais, teclas WASD, e detecção de joystick SDL2 plug-and-play. |

---

## 5. Critérios de Aceitação da Migração

1. **Paridade Funcional Total:** Todos os 12 personagens selecionáveis e jogáveis com movimentação, ataques normais, técnicas especiais e estados de morte/vitória.
2. **Taxa de Quadros:** Execução contínua a **60 FPS estáveis** em qualquer Mac moderno (Apple Silicon M1 ou superior).
3. **Fidelidade às Artes Conceituais:** Trajes, armas e identidades dos lutadores respeitando os conceitos oficiais em ambas as vertentes (Sprites HD-2D e Micro-voxels).
4. **Zero Erros de Console:** Execução limpa sem exceções, avisos de depreciação ou dependências externas faltantes.
