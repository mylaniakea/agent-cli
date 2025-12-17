"""Validation utilities for API keys, models, and configurations."""

import re
from typing import Optional


class APIKeyValidator:
    """Validate API keys for different providers."""

    @staticmethod
    def validate_openai_key(key: str) -> tuple[bool, Optional[str]]:
        """Validate OpenAI API key format.

        Args:
            key: API key to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not key:
            return False, "OpenAI API key is missing"

        if not key.startswith("sk-"):
            return False, "OpenAI API key should start with 'sk-'"

        if len(key) < 20:
            return False, "OpenAI API key appears too short"

        return True, None

    @staticmethod
    def validate_anthropic_key(key: str) -> tuple[bool, Optional[str]]:
        """Validate Anthropic API key format.

        Args:
            key: API key to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not key:
            return False, "Anthropic API key is missing"

        if not key.startswith("sk-ant-"):
            return False, "Anthropic API key should start with 'sk-ant-'"

        if len(key) < 30:
            return False, "Anthropic API key appears too short"

        return True, None

    @staticmethod
    def validate_google_key(key: str) -> tuple[bool, Optional[str]]:
        """Validate Google API key format.

        Args:
            key: API key to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not key:
            return False, "Google API key is missing"

        # Google API keys are typically 39 characters
        if len(key) < 20:
            return False, "Google API key appears too short"

        # Basic alphanumeric check
        if not re.match(r"^[A-Za-z0-9_-]+$", key):
            return False, "Google API key contains invalid characters"

        return True, None

    @staticmethod
    def validate_provider_key(provider: str, key: str) -> tuple[bool, Optional[str]]:
        """Validate API key for given provider.

        Args:
            provider: Provider name (openai, anthropic, google)
            key: API key to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        validators = {
            "openai": APIKeyValidator.validate_openai_key,
            "anthropic": APIKeyValidator.validate_anthropic_key,
            "google": APIKeyValidator.validate_google_key,
        }

        validator = validators.get(provider.lower())
        if not validator:
            # For providers without validation (ollama, etc.)
            return True, None

        return validator(key)

    @staticmethod
    def get_key_help_url(provider: str) -> str:
        """Get URL for obtaining API keys.

        Args:
            provider: Provider name

        Returns:
            URL string
        """
        urls = {
            "openai": "https://platform.openai.com/api-keys",
            "anthropic": "https://console.anthropic.com/settings/keys",
            "google": "https://makersuite.google.com/app/apikey",
            "ollama": "https://ollama.ai (local install, no key needed)",
        }
        return urls.get(provider.lower(), "")


class ModelValidator:
    """Validate model names and availability."""

    @staticmethod
    def validate_model(
        provider: str, model: str, models_metadata: dict
    ) -> tuple[bool, Optional[str]]:
        """Validate that model exists for provider.

        Args:
            provider: Provider name
            model: Model name
            models_metadata: Model metadata dict

        Returns:
            Tuple of (is_valid, error_message or suggestion)
        """
        provider_models = models_metadata.get(provider, {})

        if not provider_models:
            return False, f"Unknown provider: {provider}"

        if model in provider_models:
            return True, None

        # Model not found - suggest similar ones
        available = list(provider_models.keys())

        # Try to find close matches
        suggestions = []
        model_lower = model.lower()
        for available_model in available:
            if model_lower in available_model.lower() or available_model.lower() in model_lower:
                suggestions.append(available_model)

        if suggestions:
            return False, f"Model '{model}' not found. Did you mean: {', '.join(suggestions[:3])}?"
        else:
            return False, f"Model '{model}' not found. Available models: {', '.join(available[:5])}"


def format_validation_error(provider: str, error: str) -> str:
    """Format a validation error with helpful context.

    Args:
        provider: Provider name
        error: Error message

    Returns:
        Formatted error message with help
    """
    help_url = APIKeyValidator.get_key_help_url(provider)

    message = f"❌ {error}"
    if help_url:
        message += f"\n\n💡 Get your API key at: {help_url}"

    return message
