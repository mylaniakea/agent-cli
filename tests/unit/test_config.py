"""Unit tests for config module."""

from pathlib import Path

from agent_cli.config import CACHE_DIR, CONFIG_DIR, DATA_DIR, STATE_DIR, Config


class TestConfigDirectories:
    """Test configuration directory creation."""

    def test_config_directories_exist(self):
        """Test that config directories are created."""
        assert CONFIG_DIR.exists()
        assert DATA_DIR.exists()
        assert CACHE_DIR.exists()
        assert STATE_DIR.exists()

    def test_config_directories_are_paths(self):
        """Test that config directories are Path objects."""
        assert isinstance(CONFIG_DIR, Path)
        assert isinstance(DATA_DIR, Path)
        assert isinstance(CACHE_DIR, Path)
        assert isinstance(STATE_DIR, Path)


class TestConfig:
    """Test Config class."""

    def test_config_init(self):
        """Test Config initialization."""
        config = Config()
        assert config is not None

    def test_config_get_value_default(self):
        """Test getting default config value."""
        config = Config()
        # Test with a default value
        result = config.get_value("NONEXISTENT_KEY", "default")
        assert result == "default"

    def test_config_is_singleton_like(self):
        """Test that Config instances can be created."""
        config1 = Config()
        config2 = Config()
        # Both should be valid Config instances
        assert isinstance(config1, Config)
        assert isinstance(config2, Config)
