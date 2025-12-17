# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project configuration system with `/init` command
  - Support for `.agent.yml`, `claude.md`, `gemini.md`, `gpt.md`, `ollama.md`
  - Automatic config detection by walking up directory tree
  - YAML frontmatter support for markdown configs
- Beads conversation summarization
  - Automatic summarization of old messages to extend context
  - Configurable thresholds and message limits
  - Preserves recent messages while summarizing older ones
- Context management with `/context` command
  - Token counting and usage visualization
  - Color-coded warnings at 75% and 90% thresholds
  - Progress bar display
- Export functionality with `/export` command
  - Export to markdown or JSON formats
  - Includes metadata (provider, model, timestamp)
- Conversation logging with `/log` command
  - Auto-log to `~/.agent-cli/logs/`
  - `/log list` to view recent conversations
  - `/log view <id>` to display specific logs
- Provider-specific emoji icons in prompts
  - 🤖 OpenAI, 🧠 Anthropic, ✨ Google, 🦙 Ollama
- API key and model validation
  - Format validation for OpenAI, Anthropic, Google keys
  - Helpful error messages with API key acquisition URLs
  - Model name suggestions for typos
- GitHub Actions CI/CD
  - Test workflow for Python 3.9-3.12
  - Lint workflow with ruff and mypy
  - Codecov integration
- Development tooling
  - Makefile with common commands
  - Pre-commit hooks configuration
  - ruff for linting and formatting
  - mypy for type checking
- Documentation
  - CONTRIBUTING.md with development guidelines
  - CODE_OF_CONDUCT.md (Contributor Covenant)
  - SECURITY.md with security best practices
  - Updated README with badges and development section

### Changed
- Updated model metadata to December 2024
  - OpenAI: Added gpt-4o, gpt-4o-mini, o1, o1-mini
  - Anthropic: Updated to Claude 3.5 Sonnet/Haiku (Oct 2024)
  - Google: Added Gemini 1.5 Pro/Flash with extended context
  - Ollama: Added llama3.3, llama3.2, qwen2.5, deepseek-coder-v2
- Python version requirement changed from >=3.8 to >=3.9
- Improved code quality with automated formatting and linting

### Fixed
- Syntax warning in ui.py (invalid escape sequences in ASCII art)
- Missing dependencies in pyproject.toml (click, prompt_toolkit, pyyaml, requests)

### Removed
- Deprecated models: gpt-3.5-turbo variants, old llama2/llama3 models

## [1.0.0] - TBD

Initial release with:
- Multi-provider support (Ollama, OpenAI, Anthropic, Google)
- Interactive chat mode with streaming
- Command system with slash commands
- Session management
- MCP (Model Context Protocol) support
- Rich terminal UI with themes
- Message history management

---

[Unreleased]: https://github.com/mpfaffenberger/agent-cli/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/mpfaffenberger/agent-cli/releases/tag/v1.0.0
