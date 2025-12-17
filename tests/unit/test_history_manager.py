"""Unit tests for history_manager module."""


from agent_cli import history_manager


class TestMessageLimit:
    """Test message limit configuration."""

    def test_get_message_limit_returns_int(self):
        """Test that get_message_limit returns an integer."""
        limit = history_manager.get_message_limit()
        assert isinstance(limit, int)
        assert limit > 0


class TestCompactionCheck:
    """Test history compaction checks."""

    def test_should_compact_history_with_small_history(self):
        """Test that small history doesn't need compaction."""
        history = [{"role": "user", "content": f"msg{i}"} for i in range(5)]
        # Should return a boolean
        result = history_manager.should_compact_history(history)
        assert isinstance(result, bool)

    def test_should_compact_history_with_large_history(self):
        """Test compaction check with large history."""
        history = [{"role": "user", "content": f"msg{i}"} for i in range(100)]
        # Should return a boolean
        result = history_manager.should_compact_history(history)
        assert isinstance(result, bool)


class TestHistoryCompaction:
    """Test history compaction strategies."""

    def test_compact_history_returns_list(self):
        """Test that compact_history returns a list."""
        history = [{"role": "user", "content": f"msg{i}"} for i in range(20)]
        result = history_manager.compact_history(history)

        assert isinstance(result, list)
        # Should return history that is same or smaller
        assert len(result) <= len(history)

    def test_compact_history_preserves_structure(self):
        """Test that compacted history maintains message structure."""
        history = [
            {"role": "user", "content": "msg1"},
            {"role": "assistant", "content": "resp1"},
        ]
        result = history_manager.compact_history(history)

        # Each message should still have role and content
        for msg in result:
            assert "role" in msg
            assert "content" in msg
