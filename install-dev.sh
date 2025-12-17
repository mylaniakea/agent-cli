#!/bin/bash
# One-time setup script for development environment

echo "🔧 Setting up agent-cli development environment..."

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate and install dependencies
echo "📥 Installing dependencies with uv..."
source .venv/bin/activate
pip install uv
uv pip install -e ".[dev]"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use during development:"
echo "  ./dev.sh              # Run the app with latest code (no venv activation needed)"
echo "  ./dev.sh --help       # See all commands"
echo ""
echo "To install system-wide (for production use):"
echo "  pip install ."
echo ""
