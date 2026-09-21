# Samurai Edge Demake

Um jogo de duelo isométrico em estilo **3D Voxel Art** tático, inspirado nos clássicos jogos de luta de espadas e demakes retrô com iluminação volumétrica direcional.

![Samurai Edge Demake - Seleção Voxel](char_select_7p_preview.png)

---

## 🗡️ Visão Geral

Ambientado em uma arena construída inteiramente em voxels 3D (estilo *3D Dot Game Heroes*, *Voxatron* e *Crossy Road*), com floresta de bambus em colunas de voxels cortáveis, lago rebaixado com margens em desnível, ponte de madeira com guarda-corpo elevado onde os oponentes iniciam o combate frente a frente em suas extremidades, poço de cantaria tradicional com telhado de telhas e cerejeiras de sakura com copa volumétrica. Dois guerreiros se enfrentam em duelos mortais onde precisão, alcance e timing definem a vitória.

O jogo suporta **Duelo 1P contra IA inteligente adaptativa** e **Modo 2 Jogadores Local** no mesmo teclado.

![Gameplay Preview - Duelo na Ponte de Madeira](saitou_bridge_gameplay.png)

---

## 🥋 Guerreiros Selecionáveis

### 1. Kenshin (Retalhador Carmim)
- **Estilo**: Iai-jutsu (Saque Rápido)
- **Velocidade**: Máxima (5/5)
- **Ataque Primário [E / U]**: Avanço fulminante com corte Iai instantâneo (1-Hit Kill).
- **Secundário [R / I]**: Dash evasivo multidirecional.

### 2. Musashi (Duas Lâminas)
- **Estilo**: Niten Ichi-ryū
- **Velocidade**: Cadenciada (2/5)
- **Ataque Primário [E / U]**: Combo consecutivo de 3 golpes em rápida sucessão.
- **Secundário [R / I]**: Parry defensivo que apara ataques de espada, projéteis e cães de caça, atordoando o agressor.

### 3. Hanzo (Ninja Amarelo)
- **Estilo**: Ninjutsu & Kunai
- **Velocidade**: Máxima (5/5)
- **Ataque Primário [E / U]**: Estocada rápida de curta distância (requer 2 acertos para vencer).
- **Secundário [R / I]**: Arremesso fatal de Kunai (1-Hit Kill à distância). Se errar ou colidir com obstáculos, a kunai crava no solo e deve ser recuperada a pé.

### 4. Joe & Doberman (American Ninja)
- **Estilo**: Tático & Cão de Ataque
- **Velocidade**: Ágil (4/5)
- **Ataque Primário [E / U]**: Arremesso de Shurikens em leque rotativo que não matam, mas aplicam atordoamento tático (Stun).
- **Secundário [R / I]**: Comanda o Doberman companheiro em uma investida mortal (1-Hit Kill). Se o oponente acertar o cão durante o salto, o animal é nocauteado e fica fora de combate por 4.5 segundos.

### 5. Kemuri (Ninja Cinza)
- **Estilo**: Pólvora & Cortina de Fumaça
- **Velocidade**: Ágil (4/5)
- **Ataque Primário [E / U]**: Bomba explosiva com delay de pavio (1.5s) que causa detonação mortal em área (AOE) e corta todos os bambus circundantes.
- **Secundário [R / I]**: Bomba de fumaça instantânea que camufla o ninja com recuo evasivo e reduz a velocidade do oponente em 65% (Slow), permitindo escapar de combos.

### 6. Murasaki (Ninja Roxo)
- **Estilo**: Kusarigama & Foice de Precedência
- **Velocidade**: Ágil (4/5)
- **Ataque Primário [E / U]**: Corte curto de foice (*Kama Strike*) com **Precedência Absoluta** sobre qualquer outro ataque (cancela e vence contra qualquer golpe adversário simultâneo sem entrar em Clash).
- **Secundário [R / I]**: Puxão de corrente (*Kusarigama Hook*) que agarra o oponente a média distância e o puxa rapidamente para perto, enquanto o alvo permanece livre para agir ou contra-atacar.

### 7. Hajime Saitou (Líder Shinsengumi)
- **Estilo**: Gatotsu (Estocada de Aceleração Crescente)
- **Velocidade**: Impulso Progressivo (5/5)
- **Ataque Primário [E / U]**: **Gatotsu (Estocada Crescente)**: Começa na velocidade normal e ganha aceleração contínua até velocidade supersônica (19.0 tiles/s), cortando bambus pelo caminho. Perde manobrabilidade (esterçamento rígido) e sofre inércia/frenagem demorada (Braking State) com vulnerabilidade a punição se errar (whiff), além de recuo/stun ao bater em pedras ou ser aparado pelo Parry do Musashi.
- **Secundário [R / I]**: **Gatotsu Zeroshiki**: Estocada rápida à queima-roupa desferida do corpo a corpo, sem corrida de impulso.

---

## 🎮 Controles

| Ação | Jogador 1 (P1) | Jogador 2 (P2) |
| :--- | :--- | :--- |
| **Movimento** | `W, A, S, D` | `Setas Direcionais` |
| **Ataque Primário** | `E` | `U` |
| **Ação Secundária** | `R` | `I` |

- **Troca de Modo (1P vs IA / 2 Jogadores)**: `TAB` na tela de seleção.
- **Configurações de Controles**: Pressione `C` a qualquer momento para remapear teclas livremente.
- **Reiniciar Partida**: `Espaço`
- **Mudar Personagens / Voltar ao Menu**: `ESC`

---

## ⚙️ Instalação e Execução

### Pré-requisitos
- Python 3.10+
- `pygame-ce`

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install pygame-ce

# Executar o jogo
python3 main.py
```

### Executar Testes Automatizados
```bash
python3 test_game.py
```
