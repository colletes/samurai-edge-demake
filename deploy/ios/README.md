# Samurai Edge Demake - Deploy iOS (iPhone / iPad)

Este guia orienta como gerar o projeto nativo do **Xcode**, assinar com sua **Conta de Desenvolvedor Apple** e instalar o **Samurai Edge Demake** no seu iPhone ou iPad físico, ou publicar via **TestFlight**.

---

## 🎮 Compatibilidade com iOS

- **Multi-Touch Nativo**: Joystick analógico virtual e botões de toque com resposta instantânea na tela Retina.
- **Suporte Nativo a Controles (MFi / Bluetooth)**:
  - Suporte completo aos controles **PlayStation 5 (DualSense)**, **PlayStation 4 (DualShock 4)** e **Xbox Wireless Controller** pareados via Bluetooth no iOS.
  - Reconhecimento automático dos modelos e exibição de botões correspondentes no jogo.
- **Orientação Fixa**: Execução exclusiva em modo Paisagem (*Landscape*), sem interrupções da barra de status do iOS.

---

## 🛠️ Passo 1: Gerar o Projeto Xcode

No Terminal do Mac, na pasta do jogo, execute:

```bash
./deploy/ios/setup_ios_project.sh
```

O script irá:
1. Instalar a ferramenta de compilação C/Python (`kivy-ios`).
2. Compilar as receitas do Python 3 e bibliotecas SDL2 para a arquitetura do iOS (arm64).
3. Gerar a pasta do projeto nativo em:
   `build/samuraiedge-ios/samuraiedge-ios.xcodeproj`
4. Injetar o arquivo `Info.plist` com as permissões e orientação correta.

---

## 🍏 Passo 2: Abrir e Assinar no Xcode

1. Abra o projeto no Xcode executando:
   ```bash
   open build/samuraiedge-ios/samuraiedge-ios.xcodeproj
   ```

2. No painel lateral esquerdo do Xcode, clique no nó raiz do projeto (**samuraiedge-ios**).

3. Vá até a aba **Signing & Capabilities**:
   - Marque a opção: `Automatically manage signing`.
   - No campo **Team**, selecione a sua conta de desenvolvedor Apple (**Apple Developer Account**).
   - Se necessário, ajuste o **Bundle Identifier** para o seu identificador registrado (ex: `com.thiagocarvalho.samuraiedge`).

---

## 📱 Passo 3: Rodar no iPhone / iPad Físico

1. Conecte seu iPhone ou iPad ao Mac via cabo USB (ou ative *Connect via Network*).
2. Na barra superior do Xcode, selecione o seu dispositivo conectado como alvo de execução.
3. Pressione o botão **Play / Run** (`⌘ + R`).
4. O Xcode compilará o app, fará o upload e iniciará o jogo diretamente na tela do seu aparelho!

> **Dica de Primeira Execução**: Se aparecer o aviso *"Desenvolvedor Não Confiável"* no iOS, vá em **Ajustes > Geral > Gerenciamento de VPN e Dispositivo**, localize seu e-mail de desenvolvedor e toque em **Confiar**.

---

## 🚀 Passo 4: Publicar no TestFlight ou App Store

1. No Xcode, selecione o alvo **Any iOS Device (arm64)**.
2. Vá no menu **Product > Archive**.
3. Quando a janela do *Organizer* abrir, clique em **Distribute App** e selecione **TestFlight & App Store**.
4. Siga os passos de validação automática para enviar a compilação diretamente para o App Store Connect.
