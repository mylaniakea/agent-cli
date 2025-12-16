"""Base agent interface."""
from abc import ABC, abstractmethod
from typing import Iterator, List, Dict, Optional


class BaseAgent(ABC):
    """Base class for all agent implementations."""
    
    def __init__(self, model: str, config):
        """Initialize the agent.
        
        Args:
            model: Model name to use
            config: Configuration object
        """
        self.model = model
        self.config = config
    
    @abstractmethod
    def chat(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Send a chat message and get a response.
        
        Args:
            prompt: User's message/prompt
            history: Optional conversation history as list of dicts with 'role' and 'content'
            
        Returns:
            Agent's response
        """
        pass
    
    def stream(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> Iterator[str]:
        """Stream a chat response token by token.
        
        Args:
            prompt: User's message/prompt
            history: Optional conversation history as list of dicts with 'role' and 'content'
            
        Yields:
            Response tokens as strings
        """
        # Default implementation: fall back to non-streaming and yield full response
        # Subclasses should override for true streaming
        response = self.chat(prompt, history)
        yield response
    
    @abstractmethod
    def list_models(self) -> list:
        """List available models for this provider.
        
        Returns:
            List of available model names
        """
        pass
