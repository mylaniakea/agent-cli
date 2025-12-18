#!/usr/bin/env python3
"""Verify UI changes are loaded correctly."""

import sys

sys.path.insert(0, ".")

from agent_cli.ui import PRESET_THEMES, UI, InteractiveSession

print("=" * 60)
print("UI CHANGES VERIFICATION")
print("=" * 60)

# Check 1: Autocomplete descriptions
print("\n1. Checking autocomplete descriptions...")
ui = UI()
session = InteractiveSession(ui)
completer = session.slash_completer

if hasattr(completer, 'descriptions'):
    print(f"   ✅ Descriptions found: {len(completer.descriptions)} commands")
    print("   Sample descriptions:")
    for cmd in list(completer.descriptions.keys())[:5]:
        print(f"      {cmd}: {completer.descriptions[cmd]}")
else:
    print("   ❌ No descriptions attribute found")

# Check 2: Theme completion menu styles
print("\n2. Checking completion menu styles in themes...")
sample_themes = ["default", "catppuccin", "dracula"]
for theme_name in sample_themes:
    theme = PRESET_THEMES[theme_name]
    has_completion_style = "completion-menu.completion" in theme
    print(f"   {theme_name}: {'✅' if has_completion_style else '❌'} completion styles")

# Check 3: Timer code
print("\n3. Checking timer implementation...")
import inspect

source = inspect.getsource(session._get_toolbar_tokens)
has_timer = "Ollama keep-alive timer" in source and "⏱" in source
print(f"   {'✅' if has_timer else '❌'} Timer code with ⏱ emoji found")

# Check 4: Status display removal
print("\n4. Checking prompt method...")
prompt_source = inspect.getsource(session.prompt)
has_status_display = "status_tokens" in prompt_source and "status_text" in prompt_source
print(f"   {'✅' if not has_status_display else '❌'} Status display {'removed' if not has_status_display else 'still present'}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\nNOTE: To see the autocomplete menu:")
print("  1. Run: ./agent chat")
print("  2. Type: /")
print("  3. Press: Tab")
print("  4. You should see command descriptions")
print("\nNOTE: To see the timer:")
print("  1. Must be using Ollama provider")
print("  2. Must have a model loaded")
print("  3. Look at top-right corner for '⏱ X.Xm'")
