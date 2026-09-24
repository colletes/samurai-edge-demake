#!/bin/bash
cd "$(dirname "$0")"

echo "=========================================="
echo "    Iniciando Samurai Edge HD-2D...      "
echo "=========================================="

if [ -f "./venv/bin/python" ]; then
    ./venv/bin/python main.py
else
    python3 main.py
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "Ocorreu um erro ao executar o jogo. Pressione Enter para sair..."
    read -r
fi
