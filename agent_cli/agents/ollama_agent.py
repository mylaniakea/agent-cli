"""Ollama agent implementation."""

import re
from collections.abc import Iterator
from datetime import datetime, timedelta
from typing import Optional

import requests

from agent_cli.agents.base import BaseAgent


class OllamaAgent(BaseAgent):
    """Agent for interacting with local Ollama models."""

    def __init__(self, model: str, config, system_prompt: Optional[str] = None):
        """Initialize Ollama agent."""
        super().__init__(model, config, system_prompt)
        self.base_url = config.ollama_base_url.rstrip("/")
        self.keep_alive = "5m"
        self.last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.last_request_time = None

    def set_keep_alive(self, keep_alive: str):
        """Set the keep-alive duration (e.g. '5m', '1h')."""
        self.keep_alive = keep_alive

    def get_time_remaining(self) -> Optional[str]:
        """Calculate remaining keep-alive time."""
        if not self.last_request_time:
            return None

        # Parse keep_alive string (simple regex for m/h/s)
        match = re.match(r"(\d+)([mhs])", self.keep_alive)
        if not match:
            return None  # Or "Unknown format"

        val, unit = match.groups()
        val = int(val)
        if unit == "m":
            delta = timedelta(minutes=val)
        elif unit == "h":
            delta = timedelta(hours=val)
        else:  # Assuming 's' for seconds, though not explicitly in prompt example
            delta = timedelta(seconds=val)

        expires_at = self.last_request_time + delta
        remaining = expires_at - datetime.now()

        if remaining.total_seconds() <= 0:
            return "Expired"

        # Format
        mm, ss = divmod(int(remaining.total_seconds()), 60)
        return f"{mm}m {ss}s"

    def get_last_usage(self) -> dict[str, int]:
        """Return token usage stats from the last request."""
        return self.last_usage

    def _build_messages(
        self, prompt: str, history: Optional[list[dict[str, str]]] = None
    ) -> list[dict[str, str]]:
        """Build messages list from prompt and history."""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        return messages

    def chat(self, prompt: str, history: Optional[list[dict[str, str]]] = None) -> str:
        """Send a chat message to Ollama."""
        self.last_request_time = datetime.now()
        url = f"{self.base_url}/api/chat"

        messages = self._build_messages(prompt, history)

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "keep_alive": self.keep_alive,
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 404:
                raise ValueError(
                    f"Model '{self.model}' not found. Run 'ollama pull {self.model}' on the server."
                )
            response.raise_for_status()
            data = response.json()

            # Capture usage
            self.last_usage = {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            }

            return data.get("message", {}).get("content", "No response received")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Could not connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running and accessible."
            ) from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error communicating with Ollama: {e}") from e

    def stream(self, prompt: str, history: Optional[list[dict[str, str]]] = None) -> Iterator[str]:
        """Stream a chat response from Ollama."""
        self.last_request_time = datetime.now()
        url = f"{self.base_url}/api/chat"

        messages = self._build_messages(prompt, history)

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "keep_alive": self.keep_alive,
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
                            # Capture usage from final chunk
                            self.last_usage = {
                                "prompt_tokens": data.get("prompt_eval_count", 0),
                                "completion_tokens": data.get("eval_count", 0),
                                "total_tokens": data.get("prompt_eval_count", 0)
                                + data.get("eval_count", 0),
                            }
                            break
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Could not connect to Ollama at {self.base_url}. Make sure Ollama is running."
            ) from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error communicating with Ollama: {e}") from e

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
