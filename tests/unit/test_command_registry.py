"""Unit tests for command_registry module."""
import pytest
from unittest.mock import MagicMock

from agent_cli.command_registry import (
    CommandInfo,
    register_command,
    get_command,
    get_all_commands,
    get_commands_by_category,
    handle_command,
    generate_help_text,
    _COMMAND_REGISTRY
)


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear command registry before each test."""
    _COMMAND_REGISTRY.clear()
    yield
    _COMMAND_REGISTRY.clear()


class TestCommandRegistration:
    """Test command registration functionality."""

    def test_register_simple_command(self):
        """Test registering a basic command."""
        @register_command("test", "Test command")
        def test_handler(cmd, ctx):
            return True
        
        cmd = get_command("test")
        assert cmd is not None
        assert cmd.name == "test"
        assert cmd.description == "Test command"

    def test_register_command_with_aliases(self):
        """Test registering a command with aliases."""
        @register_command("test", "Test command", aliases=["t", "tst"])
        def test_handler(cmd, ctx):
            return True
        
        # Primary name should work
        cmd = get_command("test")
        assert cmd is not None
        
        # Aliases should work
        assert get_command("t") == cmd
        assert get_command("tst") == cmd


class TestCommandRetrieval:
    """Test command retrieval functionality."""

    def test_get_nonexistent_command(self):
        """Test getting a command that doesn't exist."""
        assert get_command("nonexistent") is None

    def test_get_all_commands_returns_dict(self):
        """Test getting all registered commands returns dict."""
        @register_command("test1", "Test 1")
        def handler1(cmd, ctx):
            return True
        
        @register_command("test2", "Test 2")
        def handler2(cmd, ctx):
            return True
        
        commands = get_all_commands()
        assert isinstance(commands, dict)
        assert "test1" in commands
        assert "test2" in commands


class TestCommandHandling:
    """Test command execution functionality."""

    def test_handle_command_success(self):
        """Test handling a command that succeeds."""
        @register_command("test", "Test command")
        def handler(cmd, ctx):
            return True
        
        result = handle_command("/test", {})
        assert result is True

    def test_handle_command_case_insensitive(self):
        """Test that command names are case-insensitive."""
        @register_command("test", "Test command")
        def handler(cmd, ctx):
            return True
        
        result = handle_command("/TEST", {})
        assert result is True

    def test_handle_nonexistent_command(self):
        """Test handling a command that doesn't exist."""
        result = handle_command("/nonexistent", {})
        assert result is False


class TestHelpGeneration:
    """Test help text generation."""

    def test_generate_help_returns_string(self):
        """Test that help generation returns a string."""
        @register_command("test1", "Test 1", category="cat1")
        def handler1(cmd, ctx):
            return True
        
        help_text = generate_help_text()
        assert isinstance(help_text, str)
        assert len(help_text) > 0
