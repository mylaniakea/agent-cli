"""Google (Gemini) agent implementation."""

import json
from collections.abc import Iterator
from typing import Optional

import requests

from agent_cli.agents.base import BaseAgent


class GoogleAgent(BaseAgent):
    """Agent for interacting with Google Gemini API."""

    def __init__(self, model: str, config):
        """Initialize Google agent."""
        super().__init__(model, config)
        self.api_key = config.google_api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

        if not self.api_key:
            raise ValueError("Google API key not found. Set GOOGLE_API_KEY environment variable.")

    def _build_contents(
        self, prompt: str, history: Optional[list[dict[str, str]]] = None
    ) -> list[dict]:
        """Build contents list from prompt and history."""
        contents = []
        if history:
            # Convert history to Google's format
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        return contents

    def chat(self, prompt: str, history: Optional[list[dict[str, str]]] = None) -> str:
        """Send a chat message to Google Gemini."""
        url = f"{self.base_url}/models/{self.model}:generateContent"

        params = {"key": self.api_key}

        contents = self._build_contents(prompt, history)

        payload = {"contents": contents}

        try:
            response = requests.post(url, json=payload, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            # Extract text from response
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]

            raise RuntimeError("Unexpected response format from Google API")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error communicating with Google: {e}") from e

    def stream(self, prompt: str, history: Optional[list[dict[str, str]]] = None) -> Iterator[str]:
        """Stream a chat response from Google Gemini."""
        url = f"{self.base_url}/models/{self.model}:streamGenerateContent"

        params = {"key": self.api_key}

        contents = self._build_contents(prompt, history)

        payload = {"contents": contents}

        try:
            response = requests.post(url, json=payload, params=params, timeout=60, stream=True)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "candidates" in data and len(data["candidates"]) > 0:
                            candidate = data["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                parts = candidate["content"]["parts"]
                                if len(parts) > 0 and "text" in parts[0]:
                                    text = parts[0]["text"]
                                    if text:
                                        yield text
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error communicating with Google: {e}") from e

    def list_models(self) -> list:
        """List available Google models."""
        return ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash"]
