#!/bin/bash
# ==============================================================================
# Samurai Edge - Bakumatsu: Game Launcher
# Double-click this file in Finder to launch the game.
# ==============================================================================

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

export SDL_JOYSTICK_IOKIT=0
export SDL_JOYSTICK_MFI=1

echo "========================================================"
echo "  SAMURAI EDGE - BAKUMATSU (Game Launcher)"
echo "========================================================"
echo "Iniciando o jogo..."

if [ -f "./venv/bin/python" ]; then
    PYTHON_EXEC="./venv/bin/python"
else
    PYTHON_EXEC="python3"
fi

"$PYTHON_EXEC" main.py

exit 0
