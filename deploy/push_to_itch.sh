#!/usr/bin/env bash
# ==============================================================================
# Samurai Edge Demake - Deploy to itch.io via Butler
# ==============================================================================
set -euo pipefail

ITCH_TARGET="${ITCH_TARGET:-colletes/samurai-edge-bakumatsu}"
VERSION="${1:-}"

# Check butler availability
if ! command -v butler &>/dev/null; then
  if [ -x "$HOME/.local/bin/butler" ]; then
    export PATH="$HOME/.local/bin:$PATH"
  else
    echo "❌ Butler não foi encontrado no PATH. Execute 'xattr -cr' e adicione-o ao PATH."
    exit 1
  fi
fi

echo "===================================================="
echo "  Samurai Edge Demake ➔ itch.io Deployment"
echo "  Target: $ITCH_TARGET"
if [ -n "$VERSION" ]; then
  echo "  Version: $VERSION"
fi
echo "===================================================="

# Check login
if ! butler which &>/dev/null; then
  echo "⚠️ Você precisa estar logado no butler. Executando 'butler login'..."
  butler login
fi

USERVERSION_FLAG=()
if [ -n "$VERSION" ]; then
  USERVERSION_FLAG=("--userversion" "$VERSION")
fi

PUSHED_COUNT=0

# macOS package
if [ -f "Samurai-Edge-Demake-macOS.zip" ]; then
  echo "📦 Enviando build macOS para canal :osx..."
  butler push Samurai-Edge-Demake-macOS.zip "$ITCH_TARGET:osx" "${USERVERSION_FLAG[@]}"
  PUSHED_COUNT=$((PUSHED_COUNT + 1))
elif [ -d "dist/SamuraiEdge.app" ]; then
  echo "📦 Enviando dist/SamuraiEdge.app para canal :osx..."
  butler push dist/SamuraiEdge.app "$ITCH_TARGET:osx" "${USERVERSION_FLAG[@]}"
  PUSHED_COUNT=$((PUSHED_COUNT + 1))
fi

# Windows package
if [ -f "Samurai-Edge-Demake-Windows.zip" ]; then
  echo "📦 Enviando build Windows para canal :windows..."
  butler push Samurai-Edge-Demake-Windows.zip "$ITCH_TARGET:windows" "${USERVERSION_FLAG[@]}"
  PUSHED_COUNT=$((PUSHED_COUNT + 1))
elif [ -d "dist/SamuraiEdge" ] && [ -f "dist/SamuraiEdge/SamuraiEdge.exe" ]; then
  echo "📦 Enviando dist/SamuraiEdge para canal :windows..."
  butler push dist/SamuraiEdge "$ITCH_TARGET:windows" "${USERVERSION_FLAG[@]}"
  PUSHED_COUNT=$((PUSHED_COUNT + 1))
fi

# Linux package
if [ -f "Samurai-Edge-Demake-Linux.tar.gz" ]; then
  echo "📦 Enviando build Linux para canal :linux..."
  butler push Samurai-Edge-Demake-Linux.tar.gz "$ITCH_TARGET:linux" "${USERVERSION_FLAG[@]}"
  PUSHED_COUNT=$((PUSHED_COUNT + 1))
fi

# Android APK
APK_FILE=$(find . -maxdepth 2 -name "*.apk" 2>/dev/null | head -n 1 || true)
if [ -n "$APK_FILE" ]; then
  echo "📦 Enviando build Android ($APK_FILE) para canal :android..."
  butler push "$APK_FILE" "$ITCH_TARGET:android" "${USERVERSION_FLAG[@]}"
  PUSHED_COUNT=$((PUSHED_COUNT + 1))
fi

if [ "$PUSHED_COUNT" -eq 0 ]; then
  echo "⚠️ Nenhum arquivo de build pré-empacotado foi encontrado no diretório raiz."
  echo "   Esperado: Samurai-Edge-Demake-macOS.zip, Samurai-Edge-Demake-Windows.zip, Samurai-Edge-Demake-Linux.tar.gz ou APK."
  echo "   Para enviar um arquivo manualmente:"
  echo "   butler push <arquivo> $ITCH_TARGET:<canal>"
  exit 1
fi

echo "✅ Deploy concluído com sucesso ($PUSHED_COUNT canais atualizados)!"
