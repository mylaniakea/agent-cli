"""Configuration management with XDG Base Directory support and INI config files.

Inspired by code-puppy's config system, adapted for agent-cli's simpler needs.
"""

import configparser
import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from agent_cli.constants import DEFAULT_OLLAMA_BASE_URL


def _get_xdg_dir(env_var: str, fallback: str) -> Path:
    """
    Get directory for agent-cli files, defaulting to ~/.agent-cli.

    XDG paths are only used when the corresponding environment variable
    is explicitly set by the user. Otherwise, we use the legacy ~/.agent-cli
    directory for all file types (config, data, cache, state).

    Args:
        env_var: XDG environment variable name (e.g., "XDG_CONFIG_HOME")
        fallback: Fallback path relative to home (e.g., ".config") - unused unless XDG var is set

    Returns:
        Path to the directory for agent-cli files
    """
    # Use XDG directory ONLY if environment variable is explicitly set
    xdg_base = os.getenv(env_var)
    if xdg_base:
        return Path(xdg_base) / "agent-cli"

    # Default to legacy ~/.agent-cli for all file types
    return Path.home() / ".agent-cli"


# XDG Base Directory paths
CONFIG_DIR = _get_xdg_dir("XDG_CONFIG_HOME", ".config")
DATA_DIR = _get_xdg_dir("XDG_DATA_HOME", ".local/share")
CACHE_DIR = _get_xdg_dir("XDG_CACHE_HOME", ".cache")
STATE_DIR = _get_xdg_dir("XDG_STATE_HOME", ".local/state")

# Configuration files
CONFIG_FILE = CONFIG_DIR / "config.ini"
MCP_SERVERS_FILE = CONFIG_DIR / "mcp_servers.json"

# Default section name
DEFAULT_SECTION = "agent-cli"


class Config:
    """Manages configuration from environment variables, .env file, and INI config file.

    Priority order (highest to lowest):
    1. Environment variables
    2. config.ini file
    3. .env file (project root)
    4. Default values
    """

    def __init__(self):
        # Ensure all directories exist
        for directory in [CONFIG_DIR, DATA_DIR, CACHE_DIR, STATE_DIR]:
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)

        # Load .env file if it exists (project root)
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # Load INI config file
        self._config = configparser.ConfigParser()
        if CONFIG_FILE.exists():
            self._config.read(CONFIG_FILE)

        # Ensure default section exists
        if DEFAULT_SECTION not in self._config:
            self._config[DEFAULT_SECTION] = {}

        # Load configuration values (priority: env > ini > .env > defaults)
        self.ollama_base_url = self._get_value("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)

        # API keys
        self.openai_api_key = self._get_value("OPENAI_API_KEY", "")
        self.anthropic_api_key = self._get_value("ANTHROPIC_API_KEY", "")
        self.google_api_key = self._get_value("GOOGLE_API_KEY", "")

        # Default model preferences
        self.default_ollama_model = self._get_value("DEFAULT_OLLAMA_MODEL", "llama2")
        self.default_openai_model = self._get_value("DEFAULT_OPENAI_MODEL", "gpt-3.5-turbo")
        self.default_anthropic_model = self._get_value("DEFAULT_ANTHROPIC_MODEL", "claude-3-haiku")
        self.default_google_model = self._get_value("DEFAULT_GOOGLE_MODEL", "gemini-pro")

        # Provider preferences
        self.primary_provider = self._get_value("PRIMARY_PROVIDER", "")
        self.fallback_provider = self._get_value("FALLBACK_PROVIDER", "")

        # UI preferences
        self.prompt_name = self._get_value("PROMPT_NAME", "You")

    def _get_value(self, key: str, default: str = "") -> str:
        """Get configuration value with priority: env > ini > .env > default.

        Args:
            key: Configuration key name
            default: Default value if not found

        Returns:
            Configuration value as string
        """
        # 1. Check environment variable (highest priority)
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value

        # 2. Check INI config file
        if DEFAULT_SECTION in self._config:
            ini_value = self._config[DEFAULT_SECTION].get(key)
            if ini_value is not None:
                return ini_value

        # 3. .env was already loaded by load_dotenv, so os.getenv would have caught it
        # 4. Return default
        return default

    def set_value(self, key: str, value: str) -> None:
        """Set a configuration value in the INI file.

        Args:
            key: Configuration key name
            value: Value to set
        """
        if DEFAULT_SECTION not in self._config:
            self._config[DEFAULT_SECTION] = {}

        self._config[DEFAULT_SECTION][key] = value
        self._save_config()

        # Update instance attributes if they exist
        key_lower = key.lower()
        if key_lower == "ollama_base_url":
            self.ollama_base_url = value
        elif key_lower == "openai_api_key":
            self.openai_api_key = value
        elif key_lower == "anthropic_api_key":
            self.anthropic_api_key = value
        elif key_lower == "google_api_key":
            self.google_api_key = value
        elif key_lower == "default_ollama_model":
            self.default_ollama_model = value
        elif key_lower == "default_openai_model":
            self.default_openai_model = value
        elif key_lower == "default_anthropic_model":
            self.default_anthropic_model = value
        elif key_lower == "default_google_model":
            self.default_google_model = value
        elif key_lower == "primary_provider":
            self.primary_provider = value
        elif key_lower == "fallback_provider":
            self.fallback_provider = value
        elif key_lower == "prompt_name":
            self.prompt_name = value

    def get_value(self, key: str, default: str = "") -> str:
        """Get a configuration value.

        Args:
            key: Configuration key name
            default: Default value if not found

        Returns:
            Configuration value as string
        """
        return self._get_value(key, default)

    def _save_config(self) -> None:
        """Save configuration to INI file."""
        with open(CONFIG_FILE, "w") as f:
            self._config.write(f)

    @property
    def config_dir(self) -> Path:
        """Get the configuration directory path."""
        return CONFIG_DIR

    @property
    def agents_file(self) -> Path:
        """Get the agents configuration file path."""
        return CONFIG_DIR / "agents.json"

    def get_agents(self) -> dict[str, dict]:
        """Get configured specialized agents (personas)."""
        if self.agents_file.exists():
            try:
                with open(self.agents_file) as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def add_agent(self, name: str, system_prompt: str, model: str, beads: Optional[list[str]] = None):
        """Add or update a specialized agent (persona).

        Args:
            name: Agent name
            system_prompt: System prompt text
            model: Model to use
            beads: Optional list of bead IDs used to compose this agent
        """
        agents = self.get_agents()
        agent_data = {"system_prompt": system_prompt, "model": model}

        # Add beads if provided (for v2.0.0 personality beads)
        if beads:
            agent_data["beads"] = beads

        agents[name] = agent_data
        with open(self.agents_file, "w") as f:
            json.dump(agents, f, indent=2)

    def remove_agent(self, name: str) -> bool:
        """Remove a specialized agent."""
        agents = self.get_agents()
        if name in agents:
            del agents[name]
            with open(self.agents_file, "w") as f:
                json.dump(agents, f, indent=2)
            return True
        return False

    def get_agent(self, name: str) -> Optional[dict]:
        """Get details for a specific agent."""
        return self.get_agents().get(name)

    @property
    def mcp_config_file(self) -> Path:
        """Get the MCP servers configuration file path."""
        return MCP_SERVERS_FILE

    def get_mcp_config(self) -> dict[str, dict]:
        """Get configured MCP servers. Alias for get_mcp_servers for consistency."""
        return self.get_mcp_servers()

    def get_mcp_servers(self) -> dict[str, dict]:
        """Get configured MCP servers."""
        if self.mcp_config_file.exists():
            try:
                with open(self.mcp_config_file) as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def add_mcp_server(
        self,
        name: str,
        command: str,
        args: Optional[list[str]] = None,
        env: Optional[dict[str, str]] = None,
    ):
        """Add or update an MCP server configuration."""
        servers = self.get_mcp_servers()
        servers[name] = {"command": command, "args": args or [], "env": env or {}}
        with open(self.mcp_config_file, "w") as f:
            json.dump(servers, f, indent=2)

    def remove_mcp_server(self, name: str) -> bool:
        """Remove an MCP server configuration."""
        servers = self.get_mcp_servers()
        if name in servers:
            del servers[name]
            with open(self.mcp_config_file, "w") as f:
                json.dump(servers, f, indent=2)
            return True
        return False
