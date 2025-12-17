"""Project-specific configuration management."""

from pathlib import Path
from typing import Optional

import yaml


class ProjectConfig:
    """Manage project-specific agent configurations."""

    CONFIG_FILES = [
        ".agent.yml",
        ".agent.yaml",
        "claude.md",
        "gemini.md",
        "gpt.md",
        "ollama.md",
    ]

    @staticmethod
    def find_project_config(start_dir: Optional[Path] = None) -> Optional[Path]:
        """Find project config file by walking up directory tree.

        Args:
            start_dir: Starting directory (default: current directory)

        Returns:
            Path to config file, or None if not found
        """
        if start_dir is None:
            start_dir = Path.cwd()

        current = Path(start_dir).resolve()

        # Walk up to root
        while current != current.parent:
            for config_file in ProjectConfig.CONFIG_FILES:
                config_path = current / config_file
                if config_path.exists():
                    return config_path
            current = current.parent

        return None

    @staticmethod
    def parse_markdown_config(filepath: Path) -> dict:
        """Parse markdown config file (claude.md, gemini.md, etc.).

        Looks for YAML frontmatter or special comment blocks.

        Args:
            filepath: Path to markdown file

        Returns:
            Dict with config (provider, model, system_prompt, etc.)
        """
        config = {}

        # Infer provider from filename
        filename = filepath.name.lower()
        if "claude" in filename or "anthropic" in filename:
            config["provider"] = "anthropic"
        elif "gemini" in filename or "google" in filename:
            config["provider"] = "google"
        elif "gpt" in filename or "openai" in filename:
            config["provider"] = "openai"
        elif "ollama" in filename:
            config["provider"] = "ollama"

        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Try to parse YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    if isinstance(frontmatter, dict):
                        config.update(frontmatter)
                except Exception:
                    pass

        # Rest of content is system prompt/instructions
        if "---" in content:
            # Skip frontmatter
            parts = content.split("---", 2)
            system_content = parts[2].strip() if len(parts) >= 3 else ""
        else:
            system_content = content.strip()

        if system_content:
            config["system_prompt"] = system_content

        return config

    @staticmethod
    def parse_yaml_config(filepath: Path) -> dict:
        """Parse YAML config file (.agent.yml).

        Args:
            filepath: Path to YAML file

        Returns:
            Dict with config
        """
        with open(filepath, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config if isinstance(config, dict) else {}

    @staticmethod
    def load_project_config(start_dir: Optional[Path] = None) -> Optional[dict]:
        """Load project configuration if available.

        Args:
            start_dir: Starting directory

        Returns:
            Config dict or None
        """
        config_path = ProjectConfig.find_project_config(start_dir)
        if not config_path:
            return None

        try:
            if config_path.suffix in [".yml", ".yaml"]:
                return ProjectConfig.parse_yaml_config(config_path)
            elif config_path.suffix == ".md":
                return ProjectConfig.parse_markdown_config(config_path)
        except Exception as e:
            print(f"Warning: Failed to load project config: {e}")
            return None

        return None

    @staticmethod
    def create_project_config(
        provider: str, model: Optional[str] = None, format: str = "yaml"
    ) -> Path:
        """Create a project config file in current directory.

        Args:
            provider: Provider name (openai, anthropic, google, ollama)
            model: Optional model name
            format: Config format ('yaml' or 'markdown')

        Returns:
            Path to created config file
        """
        cwd = Path.cwd()

        if format == "markdown":
            # Create provider-specific markdown file
            filename_map = {
                "anthropic": "claude.md",
                "openai": "gpt.md",
                "google": "gemini.md",
                "ollama": "ollama.md",
            }
            filename = filename_map.get(provider, f"{provider}.md")
            config_path = cwd / filename

            # Create markdown with frontmatter
            content = f"""---
provider: {provider}
model: {model or "default"}
temperature: 0.7
---

# Project Instructions for {provider.title()}

Add your project-specific instructions, context, and guidelines here.
This content will be used as the system prompt for conversations.

## Example Instructions

- Code style preferences
- Project conventions
- Domain-specific knowledge
- Constraints and requirements
"""

        else:  # YAML format
            config_path = cwd / ".agent.yml"
            content = f"""# Agent CLI Project Configuration
provider: {provider}
model: {model or "default"}
temperature: 0.7

# Optional: System prompt/instructions
system_prompt: |
  You are a helpful AI assistant working on this project.
  Follow the project conventions and code style.

# Optional: Enable beads (conversation summarization)
beads:
  enabled: true
  max_messages: 20
  summary_threshold: 15
"""

        with open(config_path, "w", encoding="utf-8") as f:
            f.write(content)

        return config_path
