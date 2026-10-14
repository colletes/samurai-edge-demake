# 🥋 Plano de Evolução Visual dos Personagens — Do Voxel aos Concept Arts

Documento de rastreamento do progresso da prova de conceito (PoC) para comparar as abordagens visuais nos guerreiros **Okuni**, **Kasumi** e **Saitou**, avaliando-as em um **Model Inspector 3D interativo** dedicado.

---

## 🎯 Visão Geral do Projeto

- **Objetivo:** Reduzir o distanciamento visual entre os modelos in-game e as ricas artes conceituais (`assets/concepts/`), testando soluções técnicas antes de aplicar a vencedora em todo o elenco de 12 combatentes.
- **Combatentes Piloto:**
  - **Okuni (Kabuki Dancer):** Quimono em camadas carmim/dourado, kanzashi, maquiagem teatral branca/vermelha e leques tessen.
  - **Kasumi (Mist Kunoichi):** Traje tático cinza/cromo, colete com fivelas, cachecol esvoaçante, coldres e adaga.
  - **Saitou (Shinsengumi Captain):** Haori azul-celeste com barra dente de serra *dandara*, hakama escura e postura Gatotsu.
- **Técnicas no Roadmap de Avaliação:**
  1. `T1`: **Micro-voxels & Texturas Procedurais Ricas** (alta densidade volumétrica + novos padrões têxteis).
  2. `T3`: **Voxel Base + Overlays 2.5D / Decalques** (base volumétrica sólida de micro-voxels enriquecida com camadas e decalques de alta definição ancorados na anatomia).
  3. `T4`: **Modelo 3D Tradicional Low-Poly com Cel Shading** (renderizador poligonal de software com toon shading + ink outline).

> **Nota de Avaliação (Técnica 2 — Descartada):**  
> A Técnica 2 (Mapeamento UV afim 2D sobre faces de cubos) foi testada e descartada após a prova de conceito com Okuni: a interpolação afim sofreu distorção visual severa sob rotação orbital 360°, resultando em estética inferior à base pura de micro-voxels 3D. A técnica foi removida do escopo ativo.

---

## 🚦 Roadmap de Implementação e Checklist de Progresso

### [x] Fase 0 — Alinhamento e Arquitetura (/grill-me)
- [x] Definição de escopo e técnica híbrida
- [x] Seleção de Okuni, Kasumi e Saitou para a prova de conceito
- [x] Definição do formato: `tools/model_inspector.py` em Pygame puro (compatibilidade total macOS/Windows)

---

### [x] Fase 1 — Fundação do Model Inspector 3D (`tools/model_inspector.py`)
- [x] Criar estrutura base de `tools/model_inspector.py` sem dependências externas de GPU
- [x] Implementar Câmera Orbital 3D (360° azimute, pitch de elevação, zoom suave, arrasto com mouse e teclas)
- [x] Implementar sistema de iluminação direcional ajustável e sombras
- [x] Adicionar HUD informativo (FPS, ângulos da câmera, personagem atual, técnica ativa, pose)
- [x] Integrar carregamento e exibição base dos modelos existentes de Okuni, Kasumi e Saitou
- [x] Suporte a snapshot e modo headless validado com geração de previews dos 3 guerreiros

---

### [x] Fase 2 — Técnica 1: Micro-voxels e Texturas Procedurais Ricas
- [x] **Okuni T1:** Modelagem refinada de kanzashi, maquiagem teatral nos olhos/lábios com reflexo, quimono furisode brocado e leques Tessen de aço com borlas (implementado em `src/entities/okuni_t1_model.py` e integrado no inspector)
- [x] **Kasumi T1:** Máscara ninja, olhos azuis-gelo afiados, colete-espartilho com 4 fivelas cromadas e ilhoses, cachecol longo em cascata ao vento, coldres e adaga com sulco fuller (implementado em `src/entities/kasumi_t1_model.py` e integrado no inspector)
- [x] **Saitou T1:** Rosto severo e topknot chonmage samurai com fita branca, haori azul-celeste com estampa Dandara dente de serra esculpida nas mangas e abas, obi branco cerimonial e katana longa do Gatotsu (implementado em `src/entities/saitou_t1_model.py` e integrado no inspector)
- [x] Padrões procedurais têxteis e metálicos (seda, brocado, laca, couro e metal escovado) validados em todos os 3 lutadores
- [x] Correções estruturais de depth sorting 360°, tronco contínuo e ancoragem anatômica validadas

---

### [x] Fase 3 — Técnica 3: Voxel Base com Overlays 2.5D / Decalques (Concluída)
- [x] Criar subsistema de decalques 2.5D (`src/isometric/decal_renderer.py`) ancorados em coordenadas locais dos membros/tronco
- [x] **Okuni T3:** Base de micro-voxels T1 preservada com overlays nítidos: maquiagem kabuki de alta resolução nos olhos e lábios laqueados, broche de jade esmeralda no obi e kamon floral de cerejeira dourado
- [x] **Kasumi T3:** Base de micro-voxels T1 com overlays nítidos: 4 fivelas cromadas metálicas de alta definição com pinos e reflexos sobre o espartilho, protetor de testa com rebites e olhos azuis-gelo penetrantes
- [x] **Saitou T3:** Base de micro-voxels T1 com overlays nítidos: brasão Shinsengumi "Makoto" (誠) circular nítido no dorso do haori azul-celeste (visível exclusivamente na vista traseira) e rosto severo do Lobo de Mibu com bandô branco na frente

---

### [x] Fase 4 — Técnica 4: Modelo 3D Low-Poly com Cel Shading (Concluída)
- [x] Implementar pipeline de renderização poligonal via software (`src/isometric/cel_mesh_renderer.py` com projeção 3D, z-sorting, iluminação toon de 2 bandas e contorno preto *ink outline*)
- [x] **Okuni T4:** Malha poligonal de quimono em pirâmide chanfrada, mangas furisode em leque e leques tessen abertos (`src/entities/okuni_t4_model.py`)
- [x] **Kasumi T4:** Malha poligonal aerodinâmica com ombreiras cromadas, colete facetado e adagas biseladas (`src/entities/kasumi_t4_model.py`)
- [x] **Saitou T4:** Malha poligonal com haori asagi-iro em trapézio, hakama facetada e katana estocada do Gatotsu (`src/entities/saitou_t4_model.py`)

---

### [ ] Fase 5 — Poses e Comportamentos (Idle, Concept Iconic Pose, Ataque Especial)
- [ ] Pose 1: **Idle** (postura relaxada/respiração de guarda)
- [ ] Pose 2: **Concept Iconic Pose** (reprodução exata da silhueta da ilustração de conceito)
- [ ] Pose 3: **Ataque Especial** (Okuni leque duplo aberto, Kasumi salto com adaga, Saitou Gatotsu estocado)

---

### [ ] Fase 6 — Exportador de Turntable 360° e Spritesheets
- [ ] Exportação de GIF animado turntable 360° com rotação suave e fundo transparente/customizável
- [ ] Exportação de Spritesheet PNG 8-direções em grade com metadados de alinhamento

---

### [ ] Fase 7 — Revisão Comparativa e Decisão Final
- [ ] Gerar renders comparativos lado a lado das técnicas para os 3 personagens
- [ ] Apresentar análise estética e de performance ao usuário para escolha da técnica definitiva
