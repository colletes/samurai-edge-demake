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

# 1. Verificar caminho sem espaços (obrigatório para compiladores C e make)
if [[ "$PROJECT_ROOT" =~ [[:space:]] ]]; then
    echo "ERRO CRÍTICO: O caminho da pasta do projeto contém espaços:"
    echo "  \"$PROJECT_ROOT\""
    echo ""
    echo "Compiladores C e ferramentas como 'make' (usados na compilação do OpenSSL/Python para iOS)"
    echo "não aceitam espaços em branco no caminho e falharão com erro de 'No rule to make target'."
    echo ""
    echo "Por favor, renomeie a pasta removendo os espaços. Exemplo:"
    echo "  mv \"$PROJECT_ROOT\" \"$(dirname "$PROJECT_ROOT")/SamuraiEdge\""
    echo "Em seguida, acesse a nova pasta e execute este script novamente."
    exit 1
fi

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
cd "$PROJECT_ROOT"
mkdir -p "$PROJECT_ROOT/build"
echo "-> Gerando o projeto nativo do Xcode em: $IOS_BUILD_DIR..."
if [ -d "$IOS_BUILD_DIR" ]; then
    echo "-> Atualizando código-fonte no projeto existente..."
    toolchain update "$IOS_BUILD_DIR"
else
    toolchain create samuraiedge "$PROJECT_ROOT"
    rm -rf "$IOS_BUILD_DIR"
    mv "$PROJECT_ROOT/samuraiedge-ios" "$IOS_BUILD_DIR"
fi

# 5. Garantir link simbólico de dist/ e ajustes de build para Xcode 15/16
ln -sfn "$PROJECT_ROOT/dist" "$PROJECT_ROOT/build/dist"
PBXPROJ="$IOS_BUILD_DIR/samuraiedge.xcodeproj/project.pbxproj"
if [ -f "$PBXPROJ" ]; then
    sed -i '' 's/ENABLE_USER_SCRIPT_SANDBOXING = YES;/ENABLE_USER_SCRIPT_SANDBOXING = NO;/g' "$PBXPROJ"
    sed -i '' "s|rsync -av --delete \"$PROJECT_ROOT\"/|rsync -av --delete --exclude='build' --exclude='dist' --exclude='.git' --exclude='venv' --exclude='__pycache__' --exclude='.cache' --exclude='deploy' --exclude='tests' \"$PROJECT_ROOT\"/|g" "$PBXPROJ"
fi

# 6. Injetar Info.plist com configurações horizontais e Game Controller
if [ -f "$PROJECT_ROOT/deploy/ios/Info.plist" ]; then
    echo "-> Injetando Info.plist otimizado para Samurai Edge..."
    TARGET_PLIST="$IOS_BUILD_DIR/samuraiedge-Info.plist"
    if [ -f "$TARGET_PLIST" ]; then
        cp "$PROJECT_ROOT/deploy/ios/Info.plist" "$TARGET_PLIST"
    fi
fi

# 7. Gerar ícones oficiais com a Kenshi para iPhone e iPad
if [ -f "$PROJECT_ROOT/deploy/ios/generate_icons.py" ]; then
    python3 "$PROJECT_ROOT/deploy/ios/generate_icons.py"
fi

echo ""
echo "======================================================="
echo "  PROJETO XCODE CRIADO COM SUCESSO!"
echo "======================================================="
echo "  Para abrir o projeto no Xcode e assinar com sua conta:"
echo "  open \"$IOS_BUILD_DIR/samuraiedge.xcodeproj\""
echo "======================================================="
