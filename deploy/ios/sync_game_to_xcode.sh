#!/usr/bin/env bash
# ==============================================================================
# Samurai Edge Demake - Sincronizar Código e Assets com o Projeto iOS
# ==============================================================================
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TARGET_APP="$PROJECT_ROOT/build/samuraiedge-pygame-ios/pygame-ios/app/samuraiedge"

echo "-> Sincronizando código e assets para o projeto Xcode iOS..."
mkdir -p "$TARGET_APP"

cp "$PROJECT_ROOT/main.py" "$TARGET_APP/__main__.py"
rsync -av --delete "$PROJECT_ROOT/src/" "$TARGET_APP/src/"
rsync -av --delete "$PROJECT_ROOT/assets/" "$TARGET_APP/assets/"

for config in settings.json controls_config.json arcade_save.json; do
    if [ -f "$PROJECT_ROOT/$config" ]; then
        cp "$PROJECT_ROOT/$config" "$TARGET_APP/"
    fi
done

echo "✅ Sincronização concluída com sucesso!"
