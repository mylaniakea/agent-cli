"""Unit tests for model_factory module."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from agent_cli.model_factory import ModelFactory, ModelMetadata


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear model factory cache before each test."""
    ModelFactory._config_cache = None
    yield
    ModelFactory._config_cache = None


class TestModelMetadata:
    """Test ModelMetadata dataclass."""

    def test_create_metadata(self):
        """Test creating ModelMetadata instance."""
        metadata = ModelMetadata(
            provider="ollama",
            model_name="llama2",
            context_length=4096,
            max_tokens=2048,
            supports_streaming=True,
            supports_history=True,
            default_temperature=0.7,
        )

        assert metadata.provider == "ollama"
        assert metadata.model_name == "llama2"
        assert metadata.context_length == 4096


class TestModelFactory:
    """Test ModelFactory class."""

    def test_load_config_empty_file(self):
        """Test loading config when file doesn't exist."""
        with patch.object(Path, "exists", return_value=False):
            config = ModelFactory.load_config()
            assert config == {}

    def test_load_config_valid_json(self):
        """Test loading valid JSON configuration."""
        test_config = {"ollama": {"llama2": {"context_length": 4096, "max_tokens": 2048}}}

        mock_file = mock_open(read_data=json.dumps(test_config))
        with patch("builtins.open", mock_file):
            with patch.object(Path, "exists", return_value=True):
                config = ModelFactory.load_config()
                assert config == test_config

    def test_get_model_metadata_existing_model(self):
        """Test getting metadata for an existing model."""
        test_config = {
            "ollama": {
                "llama2": {
                    "context_length": 4096,
                    "max_tokens": 2048,
                    "supports_streaming": True,
                    "supports_history": True,
                }
            }
        }

        ModelFactory._config_cache = test_config
        metadata = ModelFactory.get_model_metadata("ollama", "llama2")

        assert metadata is not None
        assert metadata.provider == "ollama"
        assert metadata.model_name == "llama2"
        assert metadata.context_length == 4096

    def test_get_model_metadata_nonexistent_model(self):
        """Test getting metadata for a model that doesn't exist."""
        ModelFactory._config_cache = {}
        metadata = ModelFactory.get_model_metadata("ollama", "nonexistent")
        assert metadata is None

    def test_validate_model_exists(self):
        """Test validating an existing model."""
        test_config = {"ollama": {"llama2": {"context_length": 4096}}}

        ModelFactory._config_cache = test_config
        assert ModelFactory.validate_model("ollama", "llama2") is True

    def test_validate_model_not_exists(self):
        """Test validating a model that doesn't exist."""
        ModelFactory._config_cache = {}
        assert ModelFactory.validate_model("ollama", "nonexistent") is False
