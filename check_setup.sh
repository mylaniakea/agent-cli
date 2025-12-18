#!/bin/bash
echo "=== Agent-CLI Setup Check ==="
echo ""
echo "Version:"
.venv/bin/agent-cli --version 2>&1
echo ""
echo "Config file:"
cat ~/.agent-cli/config.json 2>/dev/null || echo "No config file found"
echo ""
echo "Python version:"
.venv/bin/python3 --version
echo ""
echo "To test the menu, run:"
echo "  .venv/bin/agent-cli chat"
echo "Then type '/' and see if the spreadsheet menu appears"
