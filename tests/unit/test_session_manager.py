"""Unit tests for session_manager module."""

import os

from agent_cli import session_manager


class TestSessionID:
    """Test session ID generation."""

    def test_get_terminal_session_id(self):
        """Test that session ID is generated correctly."""
        session_id = session_manager.get_terminal_session_id()
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        # Should contain a number
        assert any(char.isdigit() for char in session_id)


class TestProcessAlive:
    """Test process existence checking."""

    def test_is_process_alive_current_process(self):
        """Test checking if current process is alive."""
        current_pid = os.getpid()
        result = session_manager._is_process_alive(current_pid)
        assert result is True

    def test_is_process_alive_returns_bool(self):
        """Test that _is_process_alive returns a boolean."""
        result = session_manager._is_process_alive(12345)
        assert isinstance(result, bool)
