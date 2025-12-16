"""Agent factory for creating agent instances."""
from agent_cli.agents.ollama_agent import OllamaAgent
from agent_cli.agents.openai_agent import OpenAIAgent
from agent_cli.agents.anthropic_agent import AnthropicAgent
from agent_cli.agents.google_agent import GoogleAgent
from agent_cli.agents.base import BaseAgent


class AgentFactory:
    """Factory for creating agent instances."""
    
    @staticmethod
    def create(provider: str, model: str, config) -> BaseAgent:
        """Create an agent instance based on provider.
        
        Args:
            provider: Provider name (ollama, openai, anthropic, google)
            model: Model name
            config: Configuration object
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If provider is not supported
        """
        provider = provider.lower()
        
        if provider == "ollama":
            return OllamaAgent(model, config)
        elif provider == "openai":
            return OpenAIAgent(model, config)
        elif provider == "anthropic":
            return AnthropicAgent(model, config)
        elif provider == "google":
            return GoogleAgent(model, config)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
