#!/bin/bash
# ==============================================================================
# Samurai Edge - Bakumatsu: 3D Model Inspector Launcher
# Double-click this file in Finder to open the 3D Model Inspector.
# ==============================================================================

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "========================================================"
echo "  SAMURAI EDGE - BAKUMATSU (3D Model Inspector)"
echo "========================================================"
echo "Controles do Inspector:"
echo "  - Setas Esquerda/Direita: Trocar combatente"
echo "  - Botão Esquerdo + Arrastar: Rotacionar orbital (Azimute/Pitch)"
echo "  - Scroll do Mouse: Zoom in/out"
echo "  - Tecla [Espaço] ou [T]: Alternar Turntable automático 360°"
echo "  - Tecla [D]: Alternar Comparativo De / Para (Antigo vs Novo Overhaul)"
echo "  - Tecla [F]: Foco Facial Macro (Olhos & Detalhes)"
echo "  - Teclas [1] a [0] / [F1]-[F2]: Executar Animações & Golpes"
echo "  - Tecla [ESC]: Sair"
echo "========================================================"
echo "Abrindo o Model Inspector..."

export SDL_JOYSTICK_IOKIT=0
export SDL_JOYSTICK_MFI=1

if [ -f "./venv/bin/python" ]; then
    PYTHON_EXEC="./venv/bin/python"
else
    PYTHON_EXEC="python3"
fi

"$PYTHON_EXEC" tools/model_inspector.py --compare "$@"

exit 0
