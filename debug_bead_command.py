#!/usr/bin/env python3
"""Debug script to trace what happens with /bead list command."""

import sys

def debug_bead_list():
    """Simulate the /bead list command with debug output."""
    print("=" * 70)
    print("DEBUGGING /bead list COMMAND")
    print("=" * 70)

    # Step 1: Test imports
    print("\n1. Testing imports...")
    try:
        from agent_cli.beads import BeadsManager
        print("   ✓ BeadsManager imported")
    except Exception as e:
        print(f"   ✗ BeadsManager import failed: {e}")
        return

    try:
        from agent_cli.interactive_select import SingleSelect
        print("   ✓ SingleSelect imported")
    except Exception as e:
        print(f"   ✗ SingleSelect import failed: {e}")
        return

    try:
        from agent_cli.personality_beads import BeadType
        print("   ✓ BeadType imported")
    except Exception as e:
        print(f"   ✗ BeadType import failed: {e}")
        return

    # Step 2: Test bead loading
    print("\n2. Testing bead library...")
    manager = BeadsManager()
    count = manager.bead_library.count()
    print(f"   ✓ {count} beads loaded")

    # Step 3: Simulate command parsing
    print("\n3. Simulating command parsing...")
    command = "/bead list"
    parts = command.split(None, 2)
    print(f"   Command: '{command}'")
    print(f"   Parts: {parts}")
    print(f"   len(parts): {len(parts)}")

    # Step 4: Check condition
    print("\n4. Checking menu condition...")
    if len(parts) >= 3:
        print("   → Would parse type argument (NO MENU)")
        print(f"   Type argument: {parts[2]}")
    else:
        print("   → Should show interactive menu (YES MENU)")

    # Step 5: Try to show menu
    print("\n5. Attempting to show menu...")
    print("   (This should show interactive menu if terminal supports it)")
    print()

    type_options = [
        {"key": "all", "label": "📦 All Beads", "icon": ""},
        {"key": "base", "label": "Core Personality", "icon": "🎯"},
        {"key": "professional", "label": "Communication Style", "icon": "💼"},
        {"key": "domain", "label": "Expertise Areas", "icon": "🔧"},
        {"key": "modifier", "label": "Response Adjustments", "icon": "⚙️"},
        {"key": "behavior", "label": "Behavioral Patterns", "icon": "🎭"},
    ]

    try:
        selector = SingleSelect(
            type_options,
            title="Select bead category:",
            instruction="Use ↑/↓ to navigate, ENTER to select, ESC to cancel"
        )
        selected = selector.show()
        print(f"\n   ✓ Menu worked! Selected: {selected}")
    except Exception as e:
        print(f"\n   ✗ Menu failed: {e}")
        print("\n   This means your terminal doesn't support interactive menus.")
        print("   You need to use command arguments instead:")
        print("   Example: /bead list domain")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        debug_bead_list()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
