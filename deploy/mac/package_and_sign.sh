#!/usr/bin/env bash
# ==============================================================================
# Samurai Edge Demake - Automated macOS Build, Code Signing & Packaging
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

IDENTITY="${CODESIGN_IDENTITY:-Apple Development: colletes@gmail.com (D7YJU7724A)}"
ENTITLEMENTS="$SCRIPT_DIR/entitlements.plist"
APP_PATH="dist/SamuraiEdge.app"
RELEASES_DIR="dist/releases"
IS_DEMO_BUILD="${IS_DEMO_BUILD:-0}"
if [ "${1:-}" = "--demo" ] || [ "$IS_DEMO_BUILD" -eq 1 ]; then
    IS_DEMO_BUILD=1
    ZIP_NAME="Samurai-Edge-Demake-Demo-macOS.zip"
    echo "🌟 Modo DEMO ativado!"
else
    ZIP_NAME="Samurai-Edge-Demake-macOS.zip"
fi
TARGET_ZIP="$RELEASES_DIR/$ZIP_NAME"

PYTHON_BIN="venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

if [ "$IS_DEMO_BUILD" -eq 1 ]; then
    # Garantir restauração de IS_DEMO ao sair
    trap 'sed -i "" "s/IS_DEMO = True/IS_DEMO = False/g" src/edition.py || true' EXIT
    sed -i "" "s/IS_DEMO = False/IS_DEMO = True/g" src/edition.py
fi

echo "===================================================="
echo "  Samurai Edge Demake ➔ macOS Package & Sign"
echo "  Identity:     $IDENTITY"
echo "  Entitlements: $ENTITLEMENTS"
echo "===================================================="

# Check signing identity in Keychain
if ! security find-identity -p codesigning -v | grep -q "$IDENTITY"; then
    echo "⚠️ AVISO: Identidade '$IDENTITY' não encontrada no chaveiro."
    echo "Identidades disponíveis:"
    security find-identity -p codesigning -v
    echo "Prosseguindo com ad-hoc sign (-) caso a assinatura formal falhe..."
fi

# Step 1: Build with PyInstaller if requested or if dist/SamuraiEdge.app is missing
SKIP_BUILD="${SKIP_BUILD:-0}"
if [ "$SKIP_BUILD" -eq 1 ] && [ -d "$APP_PATH" ]; then
    echo "⏩ Pulando build PyInstaller (SKIP_BUILD=1)..."
else
    echo "🔨 Executando PyInstaller com samurai_edge.spec..."
    "$PYTHON_BIN" -m PyInstaller --clean -y samurai_edge.spec
fi

if [ ! -d "$APP_PATH" ]; then
    echo "❌ Erro: $APP_PATH não foi gerado!"
    exit 1
fi

echo "🧹 Limpando atributos estendidos e quarentena (xattr)..."
xattr -cr "$APP_PATH" || true

echo "✍️  Assinando binários, frameworks e bibliotecas dinâmicas (.dylib, .so, ffmpeg)..."
find "$APP_PATH/Contents" -type f \( -name "*.dylib" -o -name "*.so" -o -name "*ffmpeg*" \) | while read -r lib; do
    if [ "$lib" != "$APP_PATH/Contents/MacOS/SamuraiEdge" ]; then
        chmod +x "$lib" 2>/dev/null || true
        codesign --force --options runtime --timestamp --sign "$IDENTITY" "$lib" 2>/dev/null || \
        codesign --force --sign - "$lib"
    fi
done

echo "✍️  Assinando executável principal com entitlements de Hardened Runtime..."
codesign --force --options runtime --entitlements "$ENTITLEMENTS" --timestamp --sign "$IDENTITY" "$APP_PATH/Contents/MacOS/SamuraiEdge" 2>/dev/null || \
codesign --force --entitlements "$ENTITLEMENTS" --sign - "$APP_PATH/Contents/MacOS/SamuraiEdge"

echo "✍️  Assinando o bundle SamuraiEdge.app completo..."
codesign --force --deep --options runtime --entitlements "$ENTITLEMENTS" --timestamp --sign "$IDENTITY" "$APP_PATH" 2>/dev/null || \
codesign --force --deep --entitlements "$ENTITLEMENTS" --sign - "$APP_PATH"

echo "🔍 Verificando integridade da assinatura..."
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

echo "📦 Compactando pacote macOS via ditto (preservando permissões e symlinks)..."
mkdir -p "$RELEASES_DIR"
rm -f "$TARGET_ZIP" "$ZIP_NAME"
ditto -c -k --keepParent "$APP_PATH" "$TARGET_ZIP"
cp "$TARGET_ZIP" "$ZIP_NAME"

SIZE=$(du -h "$TARGET_ZIP" | awk '{print $1}')
echo "===================================================="
echo "✅ Pacote macOS assinado e pronto!"
echo "   Arquivo: $TARGET_ZIP ($SIZE)"
echo "   Cópia na raiz: $ZIP_NAME"
echo "===================================================="
