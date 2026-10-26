#!/bin/bash
# ==============================================================================
# Samurai Edge - Bakumatsu: Launcher Unificado
# Double-click this file in Finder to launch an interactive menu.
# ==============================================================================

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ -f "./venv/bin/python" ]; then
    PYTHON_EXEC="./venv/bin/python"
else
    PYTHON_EXEC="python3"
fi

clear
echo "========================================================"
echo "          ⚔️  SAMURAI EDGE: BAKUMATSU  ⚔️"
echo "                 Central de Lançamento"
echo "========================================================"
echo ""
echo "  [1] Jogar Samurai Edge (main.py)"
echo "  [2] Abrir 3D Model Inspector (Modelos dos Lutadores)"
echo "  [3] Abrir Studio Inspector 3D (Modelos F1 / Arenas F2)"
echo "  [4] Executar Suíte de Testes Automatizados"
echo "  [5] Sair"
echo ""
read -p "Selecione uma opção [1-5]: " OPTION

case "$OPTION" in
    1)
        echo ""
        echo "Iniciando o jogo..."
        "$PYTHON_EXEC" main.py
        ;;
    2)
        echo ""
        echo "Abrindo 3D Model Inspector..."
        "$PYTHON_EXEC" tools/model_inspector.py
        ;;
    3)
        echo ""
        echo "Abrindo Studio Inspector 3D..."
        "$PYTHON_EXEC" tools/studio_inspector.py
        ;;
    4)
        echo ""
        echo "Executando testes..."
        SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$PYTHON_EXEC" tests/test_game.py
        echo ""
        read -p "Pressione [Enter] para finalizar..."
        ;;
    *)
        echo "Encerrando."
        ;;
esac

exit 0
