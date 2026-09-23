#!/usr/bin/env bash
# ==============================================================================
# Samurai Edge Demake - Script de Build Android (APK / AAB)
# ==============================================================================
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "======================================================="
echo "  SAMURAI EDGE DEMAKE - BUILD ANDROID (BUILDOZER)"
echo "======================================================="

MODE="debug"
USE_DOCKER=false

for arg in "$@"; do
    case $arg in
        --release)
            MODE="release"
            shift
            ;;
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --clean)
            echo "-> Limpando cache do Buildozer (.buildozer)..."
            rm -rf .buildozer
            shift
            ;;
    esac
done

if [ "$USE_DOCKER" = true ]; then
    echo "-> Compilando APK via Docker Container isolado..."
    docker build -t samuraiedge-android-builder -f deploy/android/Dockerfile .
    docker run --rm -v "$PROJECT_ROOT/bin":/home/user/app/bin samuraiedge-android-builder buildozer android $MODE
    echo "-> Build concluído! APK salvo em: $PROJECT_ROOT/bin/"
    exit 0
fi

# Verificar Python e Buildozer
if ! command -v buildozer &> /dev/null; then
    echo "-> Buildozer não encontrado no PATH. Instalando via pip..."
    python3 -m pip install --upgrade buildozer cython
fi

echo "-> Iniciando compilação do APK Android (Modo: $MODE)..."
buildozer android "$MODE"

echo ""
echo "======================================================="
echo "  BUILD CONCLUÍDO COM SUCESSO!"
echo "  Seu arquivo APK está disponível em:"
echo "  $PROJECT_ROOT/bin/"
echo "======================================================="
