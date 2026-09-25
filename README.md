# Samurai Edge Demake

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Pygame-CE](https://img.shields.io/badge/pygame--ce-2.5+-green.svg)](https://pyga.me/)
[![Releases](https://img.shields.io/badge/releases-v1.2.0-gold.svg)](https://github.com/colletes/samurai-edge-demake/releases)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux%20%7C%20Android%20%7C%20iOS-lightgrey.svg)](https://github.com/colletes/samurai-edge-demake/releases)
[![License: Proprietary](https://img.shields.io/badge/license-Personal%20Use-red.svg)](LICENSE)

Um jogo de duelo mortal isométrico tático em **3D Voxel Art** e **HD-2D**, inspirado no realismo impiedoso de clássicos como *Bushido Blade*, filmes de samurai de Akira Kurosawa e estética de demakes retrô com física de desmembramento volumétrico, iluminação dinâmica e um elenco perfeitamente equilibrado de 12 guerreiros.

![Samurai Edge Demake - Seleção de 12 Guerreiros](char_select_12p_preview.png)

---

## 📦 1. Downloads & Links para as Releases Prontas

Você pode baixar os pacotes executáveis pré-compilados diretamente na aba de **[Releases Oficiais no GitHub](https://github.com/colletes/samurai-edge-demake/releases)**:

| Plataforma | Pacote de Download | Como Executar |
| :--- | :--- | :--- |
| 🍏 **macOS** | [`Samurai-Edge-Demake-macOS.zip`](https://github.com/colletes/samurai-edge-demake/releases/latest) | Descompacte e abra o arquivo executável ou utilize o atalho `iniciar.command`. Caso o macOS exiba aviso de desenvolvedor não verificado: clique com o botão direito $\to$ *Abrir*, ou execute no terminal: `xattr -cr SamuraiEdge.app` |
| 🪟 **Windows** | [`Samurai-Edge-Demake-Windows.zip`](https://github.com/colletes/samurai-edge-demake/releases/latest) | Extraia a pasta zipada e dê dois cliques em `SamuraiEdge.exe`. |
| 🐧 **Linux** | [`Samurai-Edge-Demake-Linux.tar.gz`](https://github.com/colletes/samurai-edge-demake/releases/latest) | Extraia com `tar -xzvf Samurai-Edge-Demake-Linux.tar.gz` e execute `./SamuraiEdge/SamuraiEdge`. |
| 🤖 **Android** | `SamuraiEdge.apk` | Guia completo de compilação rápida em [`deploy/android/README.md`](deploy/android/README.md). |
| 📱 **iOS** | Projeto Xcode nativo | Projeto configurado para compilação via Xcode em [`deploy/ios/README.md`](deploy/ios/README.md). |

---

## ⚔️ 2. Mecânica do Jogo e Cenário Histórico

### Cenário Histórico: O Crepúsculo do Período Edo (Bakumatsu)
O jogo é ambientado em meados do século XIX, durante o turbulento período do **Bakumatsu** no Japão feudal — o fim da era dos samurais e a abertura para o comércio com o Ocidente. 
Em uma arena sagrada cercada por um bambuzal denso, lagos alimentados por fontes termais, pontes de madeira e lanternas de pedra, guerreiros de diferentes origens colidem:
- **Espadachins Tradicionais e Retalhadores**: Mestres das escolas *Iaijutsu*, *Niten Ichi-ryū* e os temidos capitães do *Shinsengumi*.
- **Clãs Shinobi e Kunoichis**: Assassinas furtivas de Iga e Koga empunhando foices *Kusarigama* e explosivos de cerâmica.
- **Arqueiras Miko e Mestras Kabuki**: Defensoras dos santuários xintoístas e acrobatas teatrais letais com leques de aço.
- **Armas de Fogo Feudais**: Atiradores veteranos armados com os pesados arcabuzes *Tanegashima*.
- **Guerreiros Estrangeiros**: Espadachins bucaneiros e mosqueteiras da guarda real europeia que aportaram nos portos de Nagasaki e Yokohama.

### Mecânicas de Combate: Bushido Letal (1-Hit Kill)
- **Morte em 1 Golpe**: Não há barras de vida longas ou combos infinitos. Um único corte limpo de espada, flecha certeira ou tiro à queima-roupa é fatal. Cada aproximação exige frieza, posicionamento e cálculo milimétrico.
- **Arena Volumétrica 3D Interativa**:
  - **Bambuzal Cortável**: Golpes de lâmina cortam colunas de bambu, abrindo linhas de visão e novas rotas de ataque.
  - **Água Desaceleradora**: Atravessar a lagoa reduz a velocidade do lutador em 45%, tornando-o um alvo fácil para estocadas e projéteis.
  - **Ponte Estreita**: Zona de afunilamento que favorece golpes com trajetória reta de longo alcance e ataques de varredura ampla.
  - **Obstáculos de Cobertura**: Pedras talhadas e o poço de cantaria bloqueiam investidas retilíneas, disparos de arcabuz, flechas e kunais.
- **Violência Cinematográfica (Kurosawa Noir)**:
  - **Hitstop Freeze**: Congelamento dramático instantâneo no exato momento do impacto letal.
  - **Flash Monocromático de Alto Contraste**: Efeito inspirado na cinematografia de Akira Kurosawa (*Sanjuro*, *Yojimbo*), dessaturando a cena e destacando com intensidade o sangue carmesim.
  - **Morte Atrasada (Delayed Death)**: O oponente atingido permanece estático por ~0.4s em suspense antes de colapsar com gêiseres de sangue e desmembramento volumétrico em peças 3D de voxels.
  - **Manchas de Sangue Persistentes**: O sangue jorrado permanece no assoalho de madeira e na terra durante todo o round.
- **Spawns Aleatórios & Indicadores de Partida**:
  - A cada novo round, os lutadores surgem em coordenadas aleatórias da arena com distância garantida $\ge 7.0$ tiles.
  - Indicadores piscantes `[ P1 ]` e `[ P2 ]` sobre as cabeças mostram instantaneamente quem é quem.

![Violência Cinematográfica Samurai Kurosawa](cinematic_violence_preview.png)

---

## 🎯 3. Objetivo do Jogo

O objetivo é simples, direto e impiedoso: **eliminar o oponente antes de ser atingido**. 
- As partidas são decididas no formato clássico de **Melhor de 3 Rounds** (First to 2 Kills).
- **Modos Disponíveis**:
  - 👤 **1 Jogador (1P vs IA Adaptativa)**: Enfrente a inteligência artificial com comportamentos táticos exclusivos para cada um dos 12 personagens (controle de distância, emboscadas em bambus, iscas e esquivas).
  - 👥 **2 Jogadores Local (Versus 1v1)**: Luta direta entre dois jogadores no mesmo computador (divisão de teclado ou com dois controles de videogame independentes).

---

## 🥋 4. Guia Completo dos 12 Guerreiros

O elenco conta com **12 combatentes (6 mulheres e 6 homens)**, cada um com mecânicas, armas, alcances e tempos de recuperação próprios.

```
       [ GUERREIROS SAMURAI EDGE ]
Homens/Guerreiros: Kenshi | Musashi | Hanzo | Joe & Doberman | Saitou | Teppo
Mulheres:           Murasaki | Kasumi | Okuni | Tomoe | Anne | Julie
```

---

### 1. Kenshi — A Espadachim Lendária [F]
*Mestre do Iaijutsu e do Saque Relâmpago.*
- **Estilo**: Hiten Mitsurugi-ryū | **Velocidade**: [5/5] Máxima
- **Ataque Primário [E / U]**: *Iai Flash* — Saque fulminante com avanço frontal em alta velocidade (1-Hit Kill) que decepa bambus pelo caminho.
- **Ação Secundária [R / I]**: *Shukuchi* — Passo de deslocamento divino (28.0 tiles/s) deixando pós-imagens translúcidas (*zanzou*).
- **Estratégia a Favor**: Use o *Shukuchi* para fechar a distância no exato instante em que o rival errar um ataque. O *Iai Flash* tem prioridade frontal devastadora em linha reta.
- **Estratégia Contra**: Após desferir o *Iai Flash*, ela entra na animação de *Noto* (embainhar a katana), ficando indefesa por uma fração de segundo. Se ela errar o golpe (*whiff*), puna imediatamente! Mantenha rochas entre você e ela.

---

### 2. Musashi — O Mestre das Duas Lâminas [M]
*O estrategista lendário do estilo Niten Ichi-ryū.*
- **Estilo**: Niten Ichi-ryū (Katana & Wakizashi) | **Velocidade**: [2/5] Cadenciada
- **Ataque Primário [E / U]**: *Combo de Lâminas Duplas* — Sequência de 3 cortes cruzados em rápida sucessão, cobrindo múltiplas áreas de esquiva.
- **Ação Secundária [R / I]**: *Parry Perfeito* — Postura defensiva de aparo que desvia espadas, kunais, flechas e cães de ataque, atordoando o agressor.
- **Estratégia a Favor**: Faça pressão com a ameaça do *Parry*. Quando o adversário hesitar com medo de atacar, avance com o combo de cortes para encurralá-lo.
- **Estratégia Contra**: Não ataque Musashi de frente de forma óbvia! Use ataques de longa distância (Projéteis, Arcabuz, Bombas) ou finte o ataque para fazer com que ele gaste o tempo do *Parry*.

---

### 3. Hanzo — O Mestre Shinobi de Iga [M]
*Agilidade extrema e projéteis letais à distância.*
- **Estilo**: Ninjutsu & Kunai | **Velocidade**: [5/5] Máxima
- **Ataque Primário [E / U]**: *Estocada Rápida* — Golpe curto e veloz com adaga shinobi (requer 2 acertos para eliminar).
- **Ação Secundária [R / I]**: *Arremesso de Kunai* — Disparo fatal de kunai (1-Hit Kill à distância). Se errar ou atingir uma rocha, ela se crava no solo e deve ser recuperada a pé.
- **Estratégia a Favor**: Mantenha-se móvel, espere o rival se alinhar e arremesse a Kunai para uma vitória limpa. Caso erre, use sua velocidade máxima para recolher a lâmina ou fustigar com a adaga.
- **Estratégia Contra**: A Kunai viaja em linha reta. Movimente-se perpendicularmente (em zigue-zague) ou use troncos de bambu e rochas como escudo balístico.

---

### 4. Joe — O American Ninja & Cão Doberman [M]
*Combate tático em dupla com cão de caça treinado.*
- **Estilo**: Ninjutsu Ocidental & Adestramento de Combate | **Velocidade**: [4/5] Rápido
- **Ataque Primário [E / U]**: *Shuriken Stun* — Estrela de metal arremessada velozmente. Não mata, mas aplica paralisia e atordoamento no impacto.
- **Ação Secundária [R / I]**: *Comando do Doberman* — O cão de guerra dispara em investida voraz, desferindo uma mordida fatal (1-Hit Kill).
- **Estratégia a Favor**: A estratégia clássica de pinça: arremesse a Shuriken para atordoar o rival e, no mesmo segundo, aperte a ação secundária para o Doberman finalizar o alvo indefeso.
- **Estratégia Contra**: O cão corre em linha reta previsível. Golpes cortantes de ampla abertura podem golpear e nocauteá-lo temporariamente durante o salto. Foque a pressão diretamente em Joe.

---

### 5. Hajime Saitou — O Lobo de Mibu [M]
*O lendário capitão da terceira divisão do Shinsengumi.*
- **Estilo**: Shinsengumi (Mizoguchi-ha Ittō-ryū) | **Velocidade**: [5/5] Carga Explosiva
- **Ataque Primário [E / U]**: *Gatotsu Shinsen* — Arrancada com aceleração progressiva contínua até velocidade supersônica (19.0 tiles/s), cortando bambus e atravessando a arena. Pode ser levemente curvada durante a corrida.
- **Ação Secundária [R / I]**: *Gatotsu Zeroshiki* — Estocada à queima-roupa desferida instantaneamente do corpo a corpo, sem corrida prévia.
- **Estratégia a Favor**: O *Gatotsu* possui prioridade frontal absurda. Quando o rival iniciar um movimento, engrene a marcha do Gatotsu. Se ele tentar colar pelas costas, vire e solte o *Zeroshiki*.
- **Estratégia Contra**: O *Gatotsu* perde controle lateral na alta velocidade e ricocheteia com atordoamento ao bater em pedras ou no poço. Lute perto dos obstáculos e esquive lateralmente no último segundo.

---

### 6. Teppo — O Marksman do Arcabuz Feudal [M]
*A revolução da pólvora nos campos de batalha japoneses.*
- **Estilo**: Tanegashima (Tiro de Mecha Feudal) | **Velocidade**: [3/5] Cadenciada
- **Ataque Primário [E / U]**: *Disparo de Arcabuz / Coronhada* — Se municiado, dispara um projétil devastador (1-Hit Kill). Se descarregado, desfere uma coronhada de carvalho que atordoa e repele o inimigo.
- **Ação Secundária [R / I]**: *Carregar Pólvora (Hold) / Salto Evasivo (Tap)* — Segurar recarrega a arma; um toque rápido executa um salto acrobático para trás com fumaça protetora.
- **Estratégia a Favor**: Teppo inicia a rodada desmuniciado! Siga a seta dourada flutuante e a bússola superior até o barril de pólvora, carregue o tiro e mantenha o oponente à distância para liquidar o duelo.
- **Estratégia Contra**: Não deixe Teppo chegar aos barris de pólvora! Pressione-o desde o primeiro segundo de luta. Se ele conseguir carregar a arma, fique atrás de rochas densas.

---

### 7. Murasaki — A Kunoichi da Foice [F]
*Agilidade felina com Kusarigama e prioridade absoluta de golpe.*
- **Estilo**: Kusarigamajutsu (Foice & Corrente) | **Velocidade**: [4/5] Ágil
- **Ataque Primário [E / U]**: *Corte de Foice (Kama Strike)* — Golpe dotado de **Precedência Absoluta**: anula e vence qualquer ataque adversário simultâneo sem gerar choque de espadas (*Clash*).
- **Ação Secundária [R / I]**: *Puxão de Corrente* — Lança a corrente com peso de ferro; se atingir, fisga o oponente e o arrasta velozmente até seus pés.
- **Estratégia a Favor**: Controle a distância com o gancho da corrente. Puxe o oponente e finalize imediatamente com a foice. Em trocas de golpes frontais simultâneos, seu ataque sempre tem preferência mecânica.
- **Estratégia Contra**: A corrente tem tempo de arremesso e recolhimento. Se ela errar o puxão, avance em diagonal e puna a abertura. Nunca dispute um ataque corpo a corpo no mesmo instante contra ela.

---

### 8. Kasumi — A Kunoichi da Névoa [F]
*Mestra do engano, bombas de cerâmica e cortinas de fumaça.*
- **Estilo**: Pólvora & Arte da Fumaça | **Velocidade**: [4/5] Evasiva
- **Ataque Primário [E / U]**: *Bomba em Arco 3D* — Arremessa bomba em trajetória parabólica sobre obstáculos (até 2 ativas). Detona no contato ou após queima do pavio (1.5s), com dano em área (inclui fogo amigo!).
- **Ação Secundária [R / I]**: *Cortina de Fumaça* — Detona bomba de fumaça densa aos pés, camuflando a ninja e aplicando 65% de lentidão (*Slow*) a quem entrar na névoa.
- **Estratégia a Favor**: Arremesse bombas por cima de rochas e bambuzais para atingir inimigos escondidos. Solte a cortina de fumaça em passagens estreitas (como a ponte) para paralisar o avanço inimigo.
- **Estratégia Contra**: Cole nela em combate corpo a corpo! Se Kasumi lançar uma bomba muito perto de si mesma, ela sofrerá auto-dano e morrerá pela própria explosão.

---

### 9. Okuni — A Mestra do Teatro Kabuki [F]
*Dança acrobática mortal e veneno de contagem regressiva.*
- **Estilo**: Tessen-jutsu & Dança do Veneno | **Velocidade**: [4/5] Acrobata
- **Ataque Primário [E / U]**: *Sopro de Veneno* — Sopra uma névoa carmesim tóxica. Ao atingir o rival, inicia uma **contagem regressiva fatal de 10 SEGUNDOS para a morte**!
- **Ação Secundária [R / I]**: *Kawarimi Decoy / Pirueta* — Salto acrobático que deixa um tronco de madeira (*kawarimi*) absorvendo golpes.
- **Estratégia a Favor**: Sua condição de vitória é única: infecte o adversário com o veneno no início do round. Depois disso, não lute! Fuja, salte obstáculos com o *Kawarimi* e espere os 10 segundos esgotarem.
- **Estratégia Contra**: Se for envenenado, seu tempo está correndo! Você recebe um bônus de fúria e velocidade: abandone a cautela e vá com tudo para cima de Okuni para matá-la antes que o contador chegue a zero.

---

### 10. Tomoe — A Arqueira Miko [F]
*Precisão sagrada do longo arco tradicional japonês.*
- **Estilo**: Kyudo Sagrado | **Velocidade**: [4/5] Ágil
- **Ataque Primário [E / U]**: *Retesamento do Arco Yumi* — Entra em postura de mira com barra de precisão sobre a cabeça; ao soltar, dispara uma flecha fatal com alcance superior a qualquer arma da arena.
- **Ação Secundária [R / I]**: *Flecha de Corda* — Cancela o preparo do arco e dispara uma flecha atrelada a uma corda que se fixa no cenário e puxa a arqueira rapidamente.
- **Estratégia a Favor**: Mantenha a maior distância possível do adversário. Use a *Flecha de Corda* para escapar quando encurralada e solte a flecha no corredor onde o inimigo estiver correndo.
- **Estratégia Contra**: Tomoe fica imóvel e vulnerável durante os instantes de retesamento do arco (*windup*). Aproxime-se em zigue-zague e use coberturas do mapa até poder desferir o golpe letal.

---

### 11. Anne — A Loba dos Mares [F]
*A espadachim bucaneira que domina varreduras em área.*
- **Estilo**: Alfanje Bucaneiro (Cutlass) | **Velocidade**: [4/5] Firme
- **Ataque Primário [E / U]**: *Corte de Alfanje 180°* — Golpe horizontal varrendo um semi-círculo completo de 180 graus com 1.35 tiles de raio, punindo rolagens laterais.
- **Ação Secundária [R / I]**: *Pólvora nos Olhos* — Arremessa pólvora abrasiva no rosto do rival à queima-roupa, aplicando atordoamento e cegueira enquanto salta em recuo evasivo.
- **Estratégia a Favor**: Aproxime-se, jogue a pólvora no rosto do adversário para cegá-lo e, com ele desorientado, execute o giro de 180° com o alfanje. O golpe cobre toda a frente, impedindo desvios curtos.
- **Estratégia Contra**: A pólvora tem alcance curto. Lute a média distância e utilize armas de estocada reta mais longas (como o Florete ou o Gatotsu) para puni-la de fora do seu alcance.

---

### 12. Julie — A Flor da Guarda Real [F]
*Nobreza europeia com esgrima clássica de precisão cirúrgica.*
- **Estilo**: Esgrima Francesa (Florete & Capa) | **Velocidade**: [5/5] Velocidade de Elite
- **Ataque Primário [E / U]**: *Estocada Fleche* — Lunge linear instantâneo de longo alcance (1.30 tiles) com o florete de aço, com recuperação quase instantânea (0.14s).
- **Ação Secundária [R / I]**: *Capa Riposte & Pistola* — Postura defensiva com a capa de seda reforçada (apara golpes) seguida de um contragolpe surpresa fatal com pistola de pederneira.
- **Estratégia a Favor**: O *Fleche* tem alcance superior ao das katanas convencionais. Mantenha o inimigo na ponta do florete. Se ele tentar contra-atacar, ative o *Riposte* da capa para aparar e disparar.
- **Estratégia Contra**: O *Fleche* avança em uma linha muito reta e estreita; esquivas laterais limpas abrem as costas de Julie para punição. Fique atento à postura da capa para não cair no contra-ataque.

---

## 🎮 5. Controles e Opções

### Mapeamento no Teclado

| Ação | Jogador 1 (P1) | Jogador 2 (P2) |
| :--- | :--- | :--- |
| **Movimento** | `W, A, S, D` | `Setas Direcionais (↑, ←, ↓, →)` |
| **Ataque Primário** | `E` | `U` |
| **Ação Secundária / Especial** | `R` | `I` |
| **Confirmar Seleção** | `E` ou `Espaço` | `U` ou `Enter` |
| **Troca de Modo (1P vs IA / 2 Jogadores)** | `TAB` | `TAB` |
| **Menu de Configurações** | `C` | `C` |
| **Ajuda & Guia Estratégico in-game** | `F1` | `F1` |
| **Reiniciar Partida (Reset)** | `Espaço` | `Espaço` |
| **Voltar ao Menu / Sair** | `ESC` | `ESC` |

---

### Suporte Nativo a Gamepads / Controles de Videogame
O jogo reconhece e calibra automaticamente controles conectados via USB ou Bluetooth:
- **Xbox (360, One, Series X/S)**: Direcional Analógico/D-Pad, Ataque no `A`, Especial no `B`.
- **PlayStation (DualShock 4, DualSense PS5)**: Direcional Analógico/D-Pad, Ataque no `✕`, Especial no `○`.
- **Controles Arcade / USB Genéricos**: Suporte completo via mapeamento SDL.
- **2 Controles Simultâneos**: Conecte dois controles para jogar em modo Versus local com seus amigos no sofá.
- **Vibração Háptica (Rumble)**: Resposta tátil com vibração em impactos críticos e finalizações.

---

### Controles Touchscreen & Dispositivos Móveis
Ao ser executado em smartphones ou tablets, o jogo ativa automaticamente uma interface tátil calibrada:
- **Analógico Virtual Flutuante**: Posicionado no polegar esquerdo, ajusta-se dinamicamente onde você tocar.
- **Botões Táteis de Ataque e Especial**: Posicionados no polegar direito, com suporte a multitoque simultâneo.
- **Suporte a Toque Contínuo (Hold)**: Permite segurar o botão de recarga da pólvora para o arcabuzeiro Teppo sem soltar a movimentação.
- **Display Scaler Responsivo**: Adaptação para telas 16:9, 19.5:9, 20:9 e tablets sem distorção.

---

### Menu de Configurações & Opções (`C` ou `Start`)
- **Idioma (i18n)**: Alternância dinâmica e instantânea entre **Português do Brasil (PT-BR)** e **Inglês (EN)**.
- **Modo Touchscreen**: Opções `Auto` (detecta toque), `Ligado` (sempre visível) ou `Desligado`.
- **Áudio & Efeitos**: Calibração de efeitos sonoros e intensidade de vibração háptica.
- **Manual F1**: Menu interativo de consulta de atributos com modelo tridimensional giratório do personagem selecionado.

---

## 🛠️ 6. Instalação e Execução a partir do Código-Fonte

### Pré-requisitos
- Python 3.10 ou superior
- `pip` e gerenciador de ambientes virtuais (`venv`)

```bash
# 1. Clonar o repositório
git clone https://github.com/colletes/samurai-edge-demake.git
cd samurai-edge-demake

# 2. Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar o jogo
python3 main.py

# Dica para macOS: você também pode abrir com um duplo clique no script:
# ./iniciar.command
```

### Execução da Suíte de Testes Automatizados
```bash
# Executa todos os 18 testes automatizados de sistema
./venv/bin/python test_game.py

# Executa testes específicos de controles e responsividade tátil
./venv/bin/python tests/test_controllers_and_touch.py
```

---

## 📄 7. Licença de Uso

Este projeto é disponibilizado sob uma **Licença Proprietária de Uso Pessoal Não Comercial** (*Source-Available / Personal Non-Commercial License*).
- Você tem permissão para baixar, executar, modificar localmente e estudar o código para fins pessoais e não comerciais.
- Todos os direitos autorais, de publicação, exploração comercial e distribuição de builds são reservados com exclusividade a **Thiago Carvalho**.
- É expressamente proibida a cópia, republicação ou incorporação deste código em produtos comerciais sem autorização prévia por escrito.
Consulte o arquivo [`LICENSE`](LICENSE) para os termos jurídicos completos.
