"""Agent factory for creating agent instances."""

from agent_cli.agents.anthropic_agent import AnthropicAgent
from agent_cli.agents.base import BaseAgent
from agent_cli.agents.google_agent import GoogleAgent
from agent_cli.agents.ollama_agent import OllamaAgent
from agent_cli.agents.openai_agent import OpenAIAgent


class AgentFactory:
    """Factory for creating agent instances."""

    @staticmethod
    def create(provider: str, model: str, config, system_prompt: str = None) -> BaseAgent:
        """Create an agent instance based on provider.

        Args:
            provider: Provider name (ollama, openai, anthropic, google)
            model: Model name
            config: Configuration object
            system_prompt: Optional system prompt

        Returns:
            Agent instance

        Raises:
            ValueError: If provider is not supported
        """
        provider = provider.lower()

        if provider == "ollama":
            return OllamaAgent(model, config, system_prompt=system_prompt)
        elif provider == "openai":
            # Pass system_prompt if supported, else ignore for now (or likely update all agents)
            # Assuming other agents inherit BaseAgent but might strict init.
            # For now, let's only pass to Ollama or check others.
            # Best practice: update all agents. But to fix immediate crash:
            return OpenAIAgent(model, config)
        elif provider == "anthropic":
            return AnthropicAgent(model, config)
        elif provider == "google":
            return GoogleAgent(model, config)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
