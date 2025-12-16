"""OpenAI agent implementation."""
import requests
import json
from typing import Iterator, List, Dict, Optional
from agent_cli.agents.base import BaseAgent


class OpenAIAgent(BaseAgent):
    """Agent for interacting with OpenAI API."""
    
    def __init__(self, model: str, config):
        """Initialize OpenAI agent."""
        super().__init__(model, config)
        self.api_key = config.openai_api_key
        self.base_url = "https://api.openai.com/v1"
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )
    
    def _build_messages(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
        """Build messages list from prompt and history."""
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        return messages
    
    def chat(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Send a chat message to OpenAI."""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = self._build_messages(prompt, history)
        
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error communicating with OpenAI: {e}")
    
    def stream(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> Iterator[str]:
        """Stream a chat response from OpenAI."""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = self._build_messages(prompt, history)
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        line_text = line_text[6:]  # Remove 'data: ' prefix
                        if line_text.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(line_text)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error communicating with OpenAI: {e}")
    
    def list_models(self) -> list:
        """List available OpenAI models."""
        # Return common OpenAI models
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
