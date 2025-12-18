## [1.1.0] - 2025-12-17

### Added
- **Custom Container UI**: Complete box borders visible WHILE typing (top, left, right, bottom)
- **Interactive Onboarding**: First-run setup flow with multi-provider selection
- **Ollama Enhancements**:
  - Connection testing during setup
  - Model selection from available models
  - Keep-alive timer configuration
  - Real-time status display with countdown timer
  - Automatic model cleanup on exit
- **Interactive by Default**: `agent chat` now runs in interactive mode without flags
- **Environment Variable Fixes**: Corrected naming (`DEFAULT_OLLAMA_MODEL` vs `OLLAMA_DEFAULT_MODEL`)

### Changed
- **UI Theme**: Changed from blue to clean gray (#888888) for better aesthetics
- **CLI Behavior**: Interactive mode is now default; use `--non-interactive` for single prompts
- **Prompt Implementation**: Complete rewrite using prompt_toolkit custom containers

### Fixed
- Bottom border now displays inline during typing (not just after)
- Autocomplete menu styling (removed harsh blue)
- Model configuration loading from environment

---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-12-17

### Added
- **Fallback Provider Support**: Automatic failover when primary provider is unavailable
  - Configure via `PRIMARY_PROVIDER` and `FALLBACK_PROVIDER` settings
  - Seamless switching with user notification
  - Works across all providers (Ollama, OpenAI, Anthropic, Google)
- **Keyboard-Driven UI Components**:
  - Multi-select menu with arrow keys and spacebar selection
  - Single-select menu for provider/model/theme selection
  - Visual feedback with checkboxes and highlighting
  - Used in onboarding wizard and throughout the app
- **11 Beautiful Themes**:
  - catppuccin, dracula, nord, tokyo-night, gruvbox
  - monokai, solarized, one-dark, synthwave, simple, default
  - Switch themes with `/theme` command
  - Themed completion menus with consistent styling
- **Auto-Popup Completion Menus**:
  - Type `/` to instantly see all available commands
  - Completion menu appears automatically while typing
  - FloatContainer-based implementation for proper z-ordering
  - Themed styling matching selected theme
- **Nerd Font Icon Support**:
  - Provider icons using Nerd Fonts (󰝰 for Ollama, etc.)
  - Automatic fallback to emoji when Nerd Fonts unavailable
  - Detection based on fc-list command availability
  - Configurable in settings
- **Ollama Keep-Alive Timer Display**:
  - Real-time countdown timer in status bar (⏱️ 4m 23s)
  - Shows time remaining before model unloads
  - Right-aligned in status display
  - Updates automatically during conversation
- **Model Name in Prompt**:
  - Shows current model in every prompt (e.g., "🦙 llama3.3 | You ➜")
  - Provider icon + shortened model name
  - Consistent formatting across all providers
- **Project Initialization Enhancements**:
  - `/init` command creates project-specific configs
  - Support for `.agent.yml` and provider-specific markdown files
  - Template system for common project types
- **Status Bar Improvements**:
  - Provider icon in status bar
  - Model name display
  - Keep-alive timer (for Ollama)
  - Right-aligned status information
- **Design Documentation**:
  - `INIT_SUPERPOWER_DESIGN.md` - Comprehensive design for super-powered `/init`
  - `BEADS_SUPER_INIT_DESIGN.md` - Deep Beads integration design
  - `MENU_CONSISTENCY.md` - UI menu system documentation
  - `BEAUTIFICATION_SUMMARY.md` - UI improvements summary
  - `ONBOARDING_IMPROVEMENTS.md` - Onboarding flow documentation

### Changed
- **Improved Onboarding Wizard**:
  - Multi-select UI for provider selection
  - Keyboard navigation with arrow keys and spacebar
  - Visual confirmation of selections
  - Provider-specific setup flows
- **Enhanced Interactive Mode**:
  - Better prompt formatting with model name
  - Consistent menu styling across all themes
  - Improved completion menu visibility
- **Status Line Display**:
  - Moved to top-right of screen
  - Shows provider, model, and timer
  - Right-justified for better visual balance
- **README and Documentation**:
  - Complete rewrite with comprehensive feature documentation
  - Added installation instructions with Nerd Font setup
  - Detailed configuration examples
  - Usage examples for all major features
  - Slash command reference table
  - Development setup guide
- **Roadmap Planning**:
  - Created `ROADMAP.md` with 5-phase development plan
  - Phase 1: Super Init - Basic (70% complete)
  - Phase 2: Deep Integration (planned)
  - Phase 3: Team Features (planned)
  - Success metrics for each phase
  - Long-term vision through 2026+

### Fixed
- Completion menu visibility issue (FloatContainer implementation)
- Ollama timer display in status bar
- Status line formatting and alignment
- Menu styling inconsistencies across themes
- Provider icon display with Nerd Font fallback

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
