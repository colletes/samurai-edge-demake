#!/usr/bin/env bash
# ==============================================================================
# Samurai Edge Demake - Script de Preparação do Projeto iOS (Xcode)
# ==============================================================================
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IOS_BUILD_DIR="$PROJECT_ROOT/build/samuraiedge-ios"

echo "======================================================="
echo "  SAMURAI EDGE DEMAKE - SETUP PROJETO iOS (XCODE)"
echo "======================================================="

# 1. Verificar macOS e Xcode
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "ERRO: A compilação para iOS deve ser executada em um ambiente macOS com Xcode instalado."
    exit 1
fi

if ! xcode-select -p &> /dev/null; then
    echo "ERRO: Xcode Command Line Tools não encontrado. Execute 'xcode-select --install' antes de prosseguir."
    exit 1
fi

# 2. Instalar toolchain kivy-ios se necessário
if ! command -v toolchain &> /dev/null; then
    echo "-> Instalando toolchain do kivy-ios..."
    python3 -m pip install --upgrade "kivy-ios>=1.4.0" cython
fi

# 3. Compilar as receitas base (Python3 + SDL2 + Bibliotecas C)
echo "-> Verificando e compilando receitas essenciais do iOS (python3, sdl2, sdl2_image, sdl2_ttf, sdl2_mixer)..."
toolchain build python3 sdl2 sdl2_image sdl2_ttf sdl2_mixer

# 4. Criar o Projeto Xcode
mkdir -p "$PROJECT_ROOT/build"
echo "-> Gerando o projeto nativo do Xcode em: $IOS_BUILD_DIR..."
if [ -d "$IOS_BUILD_DIR" ]; then
    echo "-> Atualizando código-fonte no projeto existente..."
    toolchain update samuraiedge-ios "$PROJECT_ROOT"
else
    toolchain create samuraiedge-ios "$PROJECT_ROOT"
fi

# 5. Injetar Info.plist com configurações horizontais e Game Controller
if [ -f "$PROJECT_ROOT/deploy/ios/Info.plist" ]; then
    echo "-> Injetando Info.plist otimizado para Samurai Edge..."
    TARGET_PLIST="$IOS_BUILD_DIR/samuraiedge-ios-Info.plist"
    if [ -f "$TARGET_PLIST" ]; then
        cp "$PROJECT_ROOT/deploy/ios/Info.plist" "$TARGET_PLIST"
    fi
fi

echo ""
echo "======================================================="
echo "  PROJETO XCODE CRIADO COM SUCESSO!"
echo "======================================================="
echo "  Para abrir o projeto no Xcode e assinar com sua conta:"
echo "  open \"$IOS_BUILD_DIR/samuraiedge-ios.xcodeproj\""
echo "======================================================="
