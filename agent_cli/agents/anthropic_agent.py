"""Anthropic agent implementation."""
import requests
import json
from typing import Iterator, List, Dict, Optional
from agent_cli.agents.base import BaseAgent


class AnthropicAgent(BaseAgent):
    """Agent for interacting with Anthropic API."""
    
    def __init__(self, model: str, config):
        """Initialize Anthropic agent."""
        super().__init__(model, config)
        self.api_key = config.anthropic_api_key
        self.base_url = "https://api.anthropic.com/v1"
        
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable."
            )
    
    def _build_messages(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
        """Build messages list from prompt and history."""
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        return messages
    
    def chat(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Send a chat message to Anthropic."""
        url = f"{self.base_url}/messages"
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        messages = self._build_messages(prompt, history)
        
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error communicating with Anthropic: {e}")
    
    def stream(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> Iterator[str]:
        """Stream a chat response from Anthropic."""
        url = f"{self.base_url}/messages"
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        messages = self._build_messages(prompt, history)
        
        payload = {
            "model": self.model,
            "max_tokens": 4096,
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
                        try:
                            data = json.loads(line_text)
                            if data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})
                                text = delta.get("text", "")
                                if text:
                                    yield text
                            elif data.get("type") == "message_stop":
                                break
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error communicating with Anthropic: {e}")
    
    def list_models(self) -> list:
        """List available Anthropic models."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
