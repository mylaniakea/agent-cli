"""Integration tests for agent interactions."""

from unittest.mock import patch

from agent_cli.agents.ollama_agent import OllamaAgent
from agent_cli.config import Config


class TestOllamaAgent:
    """Test Ollama agent functionality."""

    @patch("agent_cli.agents.ollama_agent.requests")
    def test_ollama_agent_init(self, mock_requests):
        """Test OllamaAgent initialization."""
        config = Config()
        agent = OllamaAgent(model="llama2", config=config)

        assert agent is not None
        assert agent.model == "llama2"
        assert agent.config is not None

    @patch("agent_cli.agents.ollama_agent.requests")
    def test_ollama_agent_has_chat_method(self, mock_requests):
        """Test that OllamaAgent has chat method."""
        config = Config()
        agent = OllamaAgent(model="llama2", config=config)

        assert hasattr(agent, "chat")
        assert callable(agent.chat)

    @patch("agent_cli.agents.ollama_agent.requests")
    def test_ollama_agent_has_stream_method(self, mock_requests):
        """Test that OllamaAgent has stream method."""
        config = Config()
        agent = OllamaAgent(model="llama2", config=config)

        assert hasattr(agent, "stream")
        assert callable(agent.stream)


class TestAgentModule:
    """Test agent module structure."""

    def test_can_import_agents(self):
        """Test that agent modules can be imported."""
        from agent_cli.agents import base, ollama_agent

        assert base is not None
        assert ollama_agent is not None

    def test_base_agent_is_abstract(self):
        """Test that BaseAgent is an abstract class."""
        from abc import ABC

        from agent_cli.agents.base import BaseAgent

        assert issubclass(BaseAgent, ABC)
