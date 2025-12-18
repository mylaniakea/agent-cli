#!/bin/bash
# Test autocomplete in interactive mode

echo "=========================================="
echo "Testing Autocomplete"
echo "=========================================="
echo ""
echo "This will start interactive chat."
echo "To test autocomplete:"
echo "  1. Type: /"
echo "  2. Press: Tab key"
echo "  3. You should see commands with descriptions"
echo ""
echo "Press Ctrl+C to exit when done testing."
echo ""
read -p "Press Enter to start..."

./agent chat
