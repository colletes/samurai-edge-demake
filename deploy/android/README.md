# Samurai Edge Demake - Deploy Android

Este guia detalha o processo de empacotamento do **Samurai Edge Demake** para smartphones e tablets Android.

---

## 🎮 Funcionalidades Mobile Nativas Inclusas

- **Controles Touchscreen**: Joystick analógico virtual responsivo no polegar esquerdo e botões dedicados de Ataque e Dash/Especial com suporte a Multi-Touch nativo (`FINGERDOWN`, `FINGERMOTION`, `FINGERUP`).
- **Suporte a Gamepads Bluetooth/USB**: Conecte um controle de **Xbox**, **PlayStation (DualShock 4 / DualSense)** ou **Genérico** via Bluetooth ou adaptador OTG; o jogo reconhece o modelo automaticamente e adapta os botões da tela.
- **Vibração Háptica**: Feedback de vibração ao acertar cortes letais e finalizações cinematográficas.
- **Ajuste de Tela Automático**: Viewport responsivo com Letterbox/Pillarbox para telas 16:9, 19.5:9, 20:9 e tablets.

---

## 🚀 Método 1: Compilação Rápida com Script Local

### Pré-requisitos:
- Python 3.10+
- Java JDK 17 (`brew install openjdk@17` no Mac)
- `pip install buildozer cython`

### Executando o Build:
```bash
# Gerar APK em modo Debug
./deploy/android/build_apk.sh

# Gerar APK em modo Release
./deploy/android/build_apk.sh --release
```

O arquivo `.apk` final será gerado dentro da pasta `./bin/`.

---

## 🐳 Método 2: Compilação Isolada via Docker (Recomendado)

Não requer a instalação local do Android SDK, NDK nem Java:

```bash
./deploy/android/build_apk.sh --docker
```

---

## 📲 Como Instalar o APK no Celular

1. **Via Cabo USB e ADB**:
   - Ative a **Depuração USB** nas Opções de Desenvolvedor do seu celular Android.
   - Conecte o aparelho e execute:
     ```bash
     adb install -r bin/samuraiedge-1.0.0-arm64-v8a-debug.apk
     ```

2. **Direto pelo Celular**:
   - Envie o arquivo `.apk` da pasta `bin/` para o Google Drive, Telegram ou copie via cabo USB.
   - No celular, toque no APK e selecione **Instalar** (permita a instalação de fontes desconhecidas se solicitado).
