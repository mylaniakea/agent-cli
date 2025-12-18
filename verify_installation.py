#!/usr/bin/env python3
"""Verify the installation has the latest changes."""

print("Checking installation...")
print()

# Test 1: Model validation fix
print("1. Testing Ollama model validation fix...")
try:
    from agent_cli.model_factory import ModelFactory
    result = ModelFactory.validate_model("ollama", "devstral-small-2:24b")
    if result:
        print("   ✓ Ollama model validation fixed (no warning)")
    else:
        print("   ✗ Ollama model validation NOT working")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Completion menu has new commands
print("\n2. Testing completion menu has new commands...")
try:
    # Import commands to register them
    import agent_cli.interactive_commands  # noqa: F401
    from agent_cli.ui import InteractiveSession, UI

    ui = UI()
    session = InteractiveSession(ui)

    new_commands = ["/init", "/context", "/hooks"]
    missing = []
    for cmd in new_commands:
        if cmd not in session.completer_dict:
            missing.append(cmd)

    if not missing:
        print(f"   ✓ All new commands present ({len(session.completer_dict)} total)")
        print(f"   ✓ Commands include: /init, /context, /hooks")
    else:
        print(f"   ✗ Missing commands: {missing}")
        print(f"   Available: {list(session.completer_dict.keys())}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check agent-cli command location
print("\n3. Checking agent-cli installation...")
try:
    import subprocess
    result = subprocess.run(
        ["which", "agent-cli"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        location = result.stdout.strip()
        print(f"   ✓ agent-cli found at: {location}")

        # Check if it's the venv version
        if ".venv" in location:
            print("   ✓ Using virtual environment version")
        else:
            print(f"   ⚠ Using system version (not venv)")
    else:
        print("   ✗ agent-cli not found in PATH")
except Exception as e:
    print(f"   ✗ Error: {e}")

print()
print("=" * 60)
print("Run the agent with: ./agent chat")
print("Or: .venv/bin/agent-cli chat")
print("=" * 60)
