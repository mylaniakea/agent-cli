"""Model factory for centralized model creation and management.

Inspired by code-puppy's model_factory.py, adapted for agent-cli's simpler needs.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ModelMetadata:
    """Metadata for a model."""

    provider: str
    model_name: str
    context_length: int
    max_tokens: int
    supports_streaming: bool
    supports_history: bool
    default_temperature: Optional[float] = None
    custom_settings: Optional[dict[str, Any]] = None


class ModelFactory:
    """Factory for creating and managing AI models."""

    _config_cache: Optional[dict] = None
    _models_file: Path = Path(__file__).parent / "models.json"

    @classmethod
    def load_config(cls) -> dict:
        """Load model configuration from JSON file.

        Returns:
            Dictionary with model configurations
        """
        if cls._config_cache is not None:
            return cls._config_cache

        if not cls._models_file.exists():
            # Return empty config if file doesn't exist
            cls._config_cache = {}
            return cls._config_cache

        try:
            with open(cls._models_file) as f:
                cls._config_cache = json.load(f)
            return cls._config_cache
        except (OSError, json.JSONDecodeError):
            # Return empty config on error
            cls._config_cache = {}
            return cls._config_cache

    @classmethod
    def get_model_metadata(cls, provider: str, model_name: str) -> Optional[ModelMetadata]:
        """Get metadata for a specific model.

        Args:
            provider: Provider name (ollama, openai, anthropic, google)
            model_name: Model name

        Returns:
            ModelMetadata if found, None otherwise
        """
        config = cls.load_config()
        provider_config = config.get(provider.lower(), {})
        model_config = provider_config.get(model_name, {})

        if not model_config:
            return None

        return ModelMetadata(
            provider=provider.lower(),
            model_name=model_name,
            context_length=model_config.get("context_length", 4096),
            max_tokens=model_config.get("max_tokens", 2048),
            supports_streaming=model_config.get("supports_streaming", True),
            supports_history=model_config.get("supports_history", True),
            default_temperature=model_config.get("default_temperature"),
            custom_settings=model_config.get("custom_settings"),
        )

    @classmethod
    def validate_model(cls, provider: str, model_name: str) -> bool:
        """Validate that a model exists in the configuration.

        Args:
            provider: Provider name
            model_name: Model name

        Returns:
            True if model is valid, False otherwise
        """
        # Ollama models are user-installed and dynamic, so skip validation
        if provider.lower() == "ollama":
            return True

        metadata = cls.get_model_metadata(provider, model_name)
        return metadata is not None

    @classmethod
    def get_available_models(cls, provider: Optional[str] = None) -> dict[str, dict]:
        """Get available models, optionally filtered by provider.

        Args:
            provider: Optional provider name to filter by

        Returns:
            Dictionary mapping provider -> model_name -> model_config
        """
        config = cls.load_config()

        if provider:
            provider_lower = provider.lower()
            if provider_lower in config:
                return {provider_lower: config[provider_lower]}
            return {}

        return config

    @classmethod
    def get_model_settings(cls, provider: str, model_name: str) -> dict[str, Any]:
        """Get recommended settings for a model.

        Args:
            provider: Provider name
            model_name: Model name

        Returns:
            Dictionary with model settings
        """
        metadata = cls.get_model_metadata(provider, model_name)

        if not metadata:
            # Return defaults if model not found
            return {
                "max_tokens": 2048,
                "temperature": 0.7,
            }

        settings = {
            "max_tokens": metadata.max_tokens,
        }

        if metadata.default_temperature is not None:
            settings["temperature"] = metadata.default_temperature

        if metadata.custom_settings:
            settings.update(metadata.custom_settings)

        return settings

    @classmethod
    def calculate_max_tokens(cls, provider: str, model_name: str, history_length: int = 0) -> int:
        """Calculate appropriate max_tokens based on model and history.

        Args:
            provider: Provider name
            model_name: Model name
            history_length: Estimated tokens in conversation history

        Returns:
            Recommended max_tokens value
        """
        metadata = cls.get_model_metadata(provider, model_name)

        if not metadata:
            return 2048

        # Reserve some tokens for history and response
        available = metadata.context_length - history_length - 512  # Safety margin

        # Don't exceed model's max_tokens
        return min(available, metadata.max_tokens)

    @classmethod
    def list_models_by_provider(cls, provider: str) -> list:
        """List all models for a provider.

        Args:
            provider: Provider name

        Returns:
            List of model names
        """
        config = cls.load_config()
        provider_config = config.get(provider.lower(), {})
        return list(provider_config.keys())
