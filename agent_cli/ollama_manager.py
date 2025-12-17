"""Ollama connection and model management."""

import time
import threading
import os
from typing import Optional
import requests


class OllamaManager:
    """Manages Ollama connections and model lifecycle."""

    def __init__(self):
        self.base_url: Optional[str] = None
        self.current_model: Optional[str] = None
        self.keep_alive_minutes: int = 5
        self.model_loaded_at: Optional[float] = None
        self._cleanup_timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()

    def initialize(self) -> bool:
        """Initialize from environment variables."""
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.current_model = os.environ.get("DEFAULT_OLLAMA_MODEL")

        try:
            keep_alive = os.environ.get("OLLAMA_KEEP_ALIVE", "5")
            self.keep_alive_minutes = int(keep_alive)
        except ValueError:
            self.keep_alive_minutes = 5

        return self.base_url is not None

    def load_model(self, model: Optional[str] = None) -> bool:
        """Load a model into GPU memory."""
        if not self.base_url:
            return False

        model_name = model or self.current_model
        if not model_name:
            return False

        try:
            # Generate request to load model
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": "",
                    "keep_alive": f"{self.keep_alive_minutes}m"
                    if self.keep_alive_minutes >= 0
                    else "-1",
                },
                timeout=10,
            )

            if response.status_code == 200:
                with self._lock:
                    self.current_model = model_name
                    self.model_loaded_at = time.time()
                    self._schedule_cleanup()
                return True
        except Exception:
            pass

        return False

    def _schedule_cleanup(self):
        """Schedule automatic cleanup based on keep_alive setting."""
        # Cancel existing timer
        if self._cleanup_timer:
            self._cleanup_timer.cancel()

        # Schedule new cleanup if keep_alive is not indefinite
        if self.keep_alive_minutes > 0:
            cleanup_seconds = self.keep_alive_minutes * 60
            self._cleanup_timer = threading.Timer(cleanup_seconds, self.unload_model)
            self._cleanup_timer.daemon = True
            self._cleanup_timer.start()

    def unload_model(self) -> bool:
        """Unload the current model from GPU memory."""
        if not self.base_url or not self.current_model:
            return False

        try:
            # Send request with keep_alive=0 to unload
            requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.current_model, "prompt": "", "keep_alive": "0"},
                timeout=5,
            )

            with self._lock:
                self.current_model = None
                self.model_loaded_at = None

            return True
        except Exception:
            pass

        return False

    def get_time_remaining(self) -> Optional[int]:
        """Get seconds remaining before model unload. None if indefinite."""
        if self.keep_alive_minutes < 0:
            return None  # Indefinite

        if not self.model_loaded_at:
            return 0

        with self._lock:
            elapsed = time.time() - self.model_loaded_at
            total_seconds = self.keep_alive_minutes * 60
            remaining = int(total_seconds - elapsed)
            return max(0, remaining)

    def get_status_display(self) -> str:
        """Get formatted status display for UI."""
        if not self.current_model:
            return ""

        remaining = self.get_time_remaining()

        if remaining is None:
            # Indefinite keep-alive
            return f"🦙 {self.current_model} (loaded)"
        elif remaining > 0:
            mins, secs = divmod(remaining, 60)
            return f"🦙 {self.current_model} ({mins}:{secs:02d})"
        else:
            return ""

    def cleanup(self):
        """Cleanup on exit - cancel timers and unload model."""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()

        self.unload_model()


# Global instance
_ollama_manager: Optional[OllamaManager] = None


def get_ollama_manager() -> OllamaManager:
    """Get or create the global Ollama manager instance."""
    global _ollama_manager
    if _ollama_manager is None:
        _ollama_manager = OllamaManager()
        _ollama_manager.initialize()
    return _ollama_manager
