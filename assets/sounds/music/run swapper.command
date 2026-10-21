#!/bin/zsh

# 1. Move to the folder containing this .command file
cd "$(dirname "$0")" || exit 1

# 2. Ensure Homebrew & user Python paths are available to Finder's shell
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"

# 3. Activate local virtual environment if present
if [ -d ".venv" ]; then
    source ".venv/bin/activate"
elif [ -d "venv" ]; then
    source "venv/bin/activate"
fi

echo "Using Python: $(which python3)"
echo "Launching GUI..."

# 4. Run the script and immediately store the exit status
python3 apply_cover.py
EXIT_CODE=$?

# 5. If it failed, keep the window open and display the reason
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Script exited with error code $EXIT_CODE."
    echo "If you see 'ModuleNotFoundError' above, run:"
    echo "$(which python3) -m pip install PySide6 mutagen Pillow"
    echo ""
    read -s -k "?Press any key to close..."
fi