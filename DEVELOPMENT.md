# Development Guide

## Quick Start

### First Time Setup
```bash
./install-dev.sh
```

This will:
- Create a virtual environment in `.venv/`
- Install all dependencies using `uv`
- Set up the project in editable mode

### Running During Development
```bash
./dev.sh              # Start interactive chat (default)
./dev.sh --help       # See all commands
./dev.sh --version    # Check version
```

**Benefits of `./dev.sh`:**
- ✅ Always runs the **latest code** (no reinstall needed)
- ✅ Clears Python cache automatically
- ✅ No need to activate venv manually
- ✅ Works from any directory

## Development Workflow

### Making Changes
1. Edit code in `agent_cli/`
2. Run with `./dev.sh` to test immediately
3. Changes are reflected instantly - no reinstall needed!

### Testing
```bash
# Run all tests
pytest

# Run specific test
pytest tests/unit/test_config.py

# Run with coverage
pytest --cov=agent_cli
```

### Linting & Formatting
```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

## Common Issues

### "Module not found" errors
Run `./install-dev.sh` to ensure dependencies are installed.

### Seeing old behavior after code changes
The `./dev.sh` script clears cache automatically, but if you're still seeing old behavior:
```bash
# Manual cache clear
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Need to reinstall dependencies
```bash
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Project Structure
```
agent-cli/
├── agent_cli/           # Main source code
│   ├── agents/          # AI provider agents
│   ├── cli.py           # CLI entry point
│   ├── ui.py            # User interface
│   └── ...
├── tests/               # Test suite
├── dev.sh               # Development runner (use this!)
├── install-dev.sh       # One-time setup
└── setup.py             # Package configuration
```

## Production Installation

To install system-wide (not for development):
```bash
pip install .
# or
pipx install .
```

Then use:
```bash
agent-cli
```
