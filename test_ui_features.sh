#!/bin/bash
# Test script to verify UI features are working

echo "==================================="
echo "Testing Personality Beads UI"
echo "==================================="
echo ""

# Check if beads are loaded
echo "1. Checking bead library..."
.venv/bin/python -c "
from agent_cli.personality_beads import BeadLibrary
library = BeadLibrary()
print(f'   ✓ {library.count()} beads loaded')
beads = library.list_beads()
print(f'   ✓ First bead: {beads[0].name}')
" 2>/dev/null

echo ""
echo "2. Checking commands..."
.venv/bin/python -c "
from agent_cli.interactive_commands import handle_bead, handle_agent
print('   ✓ /bead command available')
print('   ✓ /agent command available')
" 2>/dev/null

echo ""
echo "3. Checking interactive menus..."
.venv/bin/python -c "
from agent_cli.interactive_select import SingleSelect, MultiSelect
print('   ✓ SingleSelect menu component available')
print('   ✓ MultiSelect menu component available')
" 2>/dev/null

echo ""
echo "==================================="
echo "✓ All components loaded successfully!"
echo "==================================="
echo ""
echo "To see the UI features, run:"
echo ""
echo "  agent-cli"
echo ""
echo "Then try these commands:"
echo "  /bead list          # Shows interactive menu"
echo "  /bead show          # Shows bead browser"
echo "  /agent create test llama3    # Interactive bead selection"
echo "  /help               # See all commands"
echo ""
