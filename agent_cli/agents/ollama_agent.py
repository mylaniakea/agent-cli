"""Ollama agent implementation."""
import requests
from typing import Iterator, List, Dict, Optional
from agent_cli.agents.base import BaseAgent


class OllamaAgent(BaseAgent):
    """Agent for interacting with local Ollama models."""
    
    def __init__(self, model: str, config):
        """Initialize Ollama agent."""
        super().__init__(model, config)
        self.base_url = config.ollama_base_url.rstrip("/")
    
    def _build_messages(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
        """Build messages list from prompt and history."""
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        return messages
    
    def chat(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Send a chat message to Ollama."""
        url = f"{self.base_url}/api/chat"
        
        messages = self._build_messages(prompt, history)
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "No response received")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Could not connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running."
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error communicating with Ollama: {e}")
    
    def stream(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> Iterator[str]:
        """Stream a chat response from Ollama."""
        url = f"{self.base_url}/api/chat"
        
        messages = self._build_messages(prompt, history)
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        import json
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            content = data["message"]["content"]
                            if content:
                                yield content
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Could not connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running."
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error communicating with Ollama: {e}")
    
    def list_models(self) -> list:
        """List available Ollama models."""
        url = f"{self.base_url}/api/tags"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return models
        except requests.exceptions.ConnectionError:
            return []
        except requests.exceptions.RequestException:
            return []
