#!/bin/bash
# Development runner for agent-cli
# This ensures you always run the latest code without needing to reinstall

# Ensure we're using the venv
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found. Run ./install-dev.sh first"
    exit 1
fi

# Clear Python cache
find agent_cli -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find agent_cli -type f -name "*.pyc" -delete 2>/dev/null

# Use venv Python and run directly with module
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Suppress prompt_toolkit CPR warning
export PROMPT_TOOLKIT_NO_CPR=1

# If no arguments provided, default to interactive chat
if [ $# -eq 0 ]; then
    "$VENV_DIR/bin/python" -m agent_cli.cli chat
else
    "$VENV_DIR/bin/python" -m agent_cli.cli "$@"
fi
