#!/usr/bin/env python3
"""Verify that all UI fixes are applied correctly."""

import sys


def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    try:
        from prompt_toolkit.layout.containers import Float, FloatContainer
        from prompt_toolkit.layout.menus import CompletionsMenu

        from agent_cli.ui import UI, InteractiveSession
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_ui_initialization():
    """Test that UI components initialize properly."""
    print("\nTesting UI initialization...")
    try:
        from agent_cli.ui import UI, InteractiveSession

        ui = UI()
        session = InteractiveSession(ui)

        # Check that session has required attributes
        assert hasattr(session, "slash_completer"), "Missing slash_completer"
        assert hasattr(session, "completer_dict"), "Missing completer_dict"
        assert hasattr(session, "_get_provider_icon"), "Missing _get_provider_icon"
        assert hasattr(session, "_shorten_model_name"), "Missing _shorten_model_name"
        assert hasattr(session, "_get_toolbar_tokens"), "Missing _get_toolbar_tokens"

        print("✓ UI components initialized successfully")
        return True
    except Exception as e:
        print(f"✗ UI initialization failed: {e}")
        return False


def test_completer_structure():
    """Test that completer has proper structure."""
    print("\nTesting completer structure...")
    try:
        from agent_cli.ui import UI, InteractiveSession

        ui = UI()
        session = InteractiveSession(ui)

        # Check completer dict structure
        assert "/provider" in session.completer_dict
        assert isinstance(session.completer_dict["/provider"], dict)
        assert "ollama" in session.completer_dict["/provider"]

        assert "/theme" in session.completer_dict
        assert isinstance(session.completer_dict["/theme"], dict)

        print("✓ Completer structure is correct")
        return True
    except Exception as e:
        print(f"✗ Completer structure test failed: {e}")
        return False


def test_ollama_timer():
    """Test that timer display code exists."""
    print("\nTesting Ollama timer code...")
    try:
        import inspect

        from agent_cli.ui import InteractiveSession

        # Check that _get_toolbar_tokens has timer code
        source = inspect.getsource(InteractiveSession._get_toolbar_tokens)
        assert "ollama" in source.lower(), "Timer code missing 'ollama' check"
        assert "⏱" in source, "Timer emoji missing"
        assert "remaining_mins" in source, "Timer calculation missing"

        # Check that prompt method has timer display
        source = inspect.getsource(InteractiveSession.prompt)
        assert "get_ollama_manager" in source, "Ollama manager import missing"
        assert "justify=\"right\"" in source or 'justify="right"' in source, "Right-aligned status missing"

        print("✓ Timer code is present")
        return True
    except Exception as e:
        print(f"✗ Timer code test failed: {e}")
        return False


def test_completion_menu_support():
    """Test that completion menu components are imported."""
    print("\nTesting completion menu support...")
    try:
        import inspect

        from agent_cli.ui import InteractiveSession

        source = inspect.getsource(InteractiveSession.prompt)
        assert "FloatContainer" in source, "FloatContainer import missing"
        assert "CompletionsMenu" in source, "CompletionsMenu import missing"
        assert "Float(" in source, "Float import/usage missing"

        print("✓ Completion menu support is present")
        return True
    except Exception as e:
        print(f"✗ Completion menu test failed: {e}")
        return False


def test_model_name_display():
    """Test that model name appears in prompt."""
    print("\nTesting model name display...")
    try:
        import inspect

        from agent_cli.ui import InteractiveSession

        source = inspect.getsource(InteractiveSession.prompt)
        assert "_shorten_model_name" in source, "Model name shortening missing"
        assert "_get_provider_icon" in source, "Provider icon missing"
        assert "| You ➜" in source or '| You ➜' in source, "Prompt format missing"

        print("✓ Model name display code is present")
        return True
    except Exception as e:
        print(f"✗ Model name display test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("UI Fixes Verification")
    print("=" * 60)
    print()

    tests = [
        test_imports,
        test_ui_initialization,
        test_completer_structure,
        test_ollama_timer,
        test_completion_menu_support,
        test_model_name_display,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("=" * 60)
        print("\n✨ All fixes verified! You can now test the app:")
        print("   ./agent chat")
        print("\nExpected behavior:")
        print("  1. Type '/' → completion menu appears")
        print("  2. With Ollama → timer shows in top-right")
        print("  3. Prompt shows: 🦙 model-name | You ➜")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
