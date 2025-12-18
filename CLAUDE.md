# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent CLI is a custom LLM CLI tool with support for local agents (via Ollama) and external API providers (OpenAI, Anthropic, Google). It provides an interactive chat interface with streaming responses, session management, and extensible command system.

**Key inspirations**: Command registry system, session management, and architectural patterns inspired by [code-puppy](https://github.com/mpfaffenberger/code_puppy).

## Development Commands

### Setup & Installation
```bash
# One-time setup (creates venv, installs dependencies)
./install-dev.sh

# Development mode - run latest code without reinstalling
./dev.sh              # Interactive chat (default)
./dev.sh --help       # Show all commands
./dev.sh --version    # Check version

# Install with uv (recommended)
make install          # Install with dev dependencies
```

### Testing & Quality Checks
```bash
# Run tests
pytest                                    # Run all tests
pytest tests/unit/test_config.py          # Run specific test file
make test                                 # Run with coverage report

# Linting and formatting
make lint             # Check code with ruff
make format           # Auto-format code with ruff
make typecheck        # Run mypy type checker
make all              # Run format, lint, typecheck, test in sequence

# Manual cleanup
make clean            # Remove build artifacts and cache
```

### Running Single Tests
```bash
# Run a specific test function
pytest tests/unit/test_config.py::TestConfig::test_config_priority

# Run tests matching a pattern
pytest -k "test_session"

# Run with verbose output
pytest -v
```

### Git Workflow
```bash
# Commits must pass pre-commit hooks (ruff check + ruff format)
git commit -m "message"  # Auto-runs pre-commit hooks

# Skip hooks (avoid unless necessary)
git commit --no-verify -m "message"
```

## Architecture

### High-Level Structure

```
CLI Layer (cli.py)
    ↓
Command Registry (command_registry.py) - Decorator-based command registration
    ↓
Configuration & Session Layer
    ├── Config (config.py) - Multi-source config (env, ini, .env)
    └── SessionManager (session_manager.py) - PPID-based per-terminal sessions
    ↓
Model & Agent Layer
    ├── ModelFactory (model_factory.py) - Model metadata & validation
    └── AgentFactory (agents/factory.py) - Provider abstraction
    ↓
Provider Layer (agents/)
    ├── OllamaAgent
    ├── OpenAIAgent
    ├── AnthropicAgent
    └── GoogleAgent
```

### Key Design Patterns

**Factory Pattern**: `AgentFactory` creates provider-specific agents; `ModelFactory` manages model metadata.

**Registry Pattern**: `CommandRegistry` enables decorator-based command discovery. Commands auto-register with `@register_command` decorator.

**Manager Pattern**: `ConfigManager` handles multi-source configuration priority; `SessionManager` provides per-terminal session isolation using PPID; `HistoryManager` handles conversation history with automatic compaction.

### Request Flow

```
User Input → CLI → SessionManager (load state) → ModelFactory (validate)
→ AgentFactory (create agent) → Provider Agent (API call)
→ HistoryManager (add to history) → SessionManager (save state) → Output
```

### Configuration Priority

1. Environment variables (highest)
2. `~/.agent-cli/config.ini` (or XDG_CONFIG_HOME)
3. `.env` file in project root
4. Default values (lowest)

## Key Components

### Session Management (`session_manager.py`)
- Uses **PPID (Parent Process ID)** for unique session identification
- Each terminal gets isolated session state
- Sessions persist across invocations in same terminal
- Auto-cleanup of dead sessions using process liveness checks
- Cross-platform (Unix signal 0, Windows OpenProcess API)

### Command Registry (`command_registry.py`)
Commands register with decorator pattern:
```python
@register_command(
    name="model",
    description="Switch model",
    usage="/model [name]",
    aliases=["m"],
    category="config",
    detailed_help="Detailed help text..."
)
def handle_model(command: str, context: dict) -> bool:
    # Handler implementation
    return True
```

All registered commands auto-appear in `/help`. Commands are discovered at import time.

### History Manager (`history_manager.py`)
- Automatic message compaction when limit exceeded
- Strategies: "recent" (default), "first", "middle"
- Configurable via `MESSAGE_LIMIT` and `HISTORY_COMPACTION_STRATEGY`

### Interactive Mode (`ui.py`)
- Built with `prompt_toolkit` and `rich`
- Slash command autocomplete (currently broken as of commit c18afc8)
- Status bar shows provider/model/theme
- Multiline input with syntax highlighting

## File Structure

```
agent_cli/
├── cli.py                    # Main CLI entry (Click commands)
├── config.py                 # Configuration management
├── command_registry.py       # Command registration system
├── session_manager.py        # Session state tracking (PPID-based)
├── history_manager.py        # Conversation history with compaction
├── model_factory.py          # Model metadata & validation
├── ui.py                     # Terminal UI with prompt_toolkit
├── interactive_commands.py   # Command handlers (@register_command)
├── constants.py              # Shared constants (e.g., Ollama defaults)
├── onboarding.py            # First-run setup wizard
├── ollama_manager.py        # Ollama-specific operations
├── export_manager.py        # Export conversations
├── token_counter.py         # Token counting utilities
├── beads.py                 # Theme system
├── agents/
│   ├── base.py              # BaseAgent interface
│   ├── factory.py           # AgentFactory
│   ├── ollama_agent.py      # Local Ollama models
│   ├── openai_agent.py      # OpenAI API
│   ├── anthropic_agent.py   # Anthropic Claude API
│   └── google_agent.py      # Google Gemini API
└── models.json              # Model metadata database
```

## Extension Points

### Adding a New Provider

1. Create `agent_cli/agents/newprovider_agent.py`
2. Inherit from `BaseAgent` and implement:
   - `chat(prompt: str, history: list) -> str`
   - `stream(prompt: str, history: list) -> Iterator[str]`
   - `list_models() -> list[str]`
3. Register in `AgentFactory.create()` in `agents/factory.py`
4. Add model metadata to `models.json`
5. Add configuration keys to `Config.__init__()` in `config.py`

### Adding a New Command

1. Add handler function to `interactive_commands.py`
2. Decorate with `@register_command(name, description, usage, aliases, category)`
3. Command auto-appears in `/help` and autocomplete
4. Handler receives `(command: str, context: dict) -> bool`
5. Context keys: `CONTEXT_KEY_AGENT`, `CONTEXT_KEY_PROVIDER`, `CONTEXT_KEY_MODEL`, `CONTEXT_KEY_HISTORY`, `CONTEXT_KEY_CONFIG`

### Adding Configuration

1. Add property to `Config.__init__()` in `config.py`
2. Use `self._get_value(key, default)` for priority resolution
3. Optionally add to config.ini template in CONFIG_DIR
4. Document in CONFIG_GUIDE.md

## Recent Fixes

### CLI Refactoring (Dec 17, 2025)
**Major refactoring** of `cli.py` for better encapsulation and bug fixes:

**Critical Bugs Fixed**:
1. **Stream duplication bug**: Non-interactive stream mode consumed generator twice, causing it to never output
2. **Global UI dependency**: Removed global `ui` import, now passes instances as parameters

**Improvements**:
- Extracted `run_interactive_mode()` and `run_non_interactive_mode()` functions
- Added 11 helper functions for better separation of concerns
- Reduced main `chat()` function from 430+ lines to ~100 lines
- Added constants: `DUMMY_MODEL_NAME`, `EXIT_COMMANDS`
- Fixed repeated `interactive` variable computation (was computed 3 times)

**New Commands** (moved from hardcoded to registry):
- `/compress` - Compress conversation history
- `/beads` - Beads CLI integration with auto-install
- `/keepalive` - Ollama keep-alive management
- `/reasoning` - Reasoning display toggle

**See `CLI_REFACTORING_SUMMARY.md` for complete details.**

### Autocomplete Fix (Dec 17, 2025)
**Issue**: Slash command autocomplete was not working for boxed themes (any theme except "simple")
- The custom `Application` created for boxed UI didn't have completer attached to Buffer
- No Tab key bindings for triggering completions

**Fix**: Added completer to Buffer initialization and Tab key bindings in `ui.py`:
- Buffer now includes `completer=self.slash_completer` and `complete_while_typing=True`
- Added Tab binding to start/navigate completions
- Added Shift+Tab binding for backwards navigation

See `agent_cli/ui.py` lines 557-560 (Buffer) and 625-639 (key bindings)

## Testing Notes

- Test structure: `tests/unit/` and `tests/integration/`
- Uses pytest with pytest-cov, pytest-mock
- Coverage reports in `htmlcov/`
- Interactive features (autocomplete, menus) MUST be tested manually
- Always test after changes to `ui.py`, `interactive_commands.py`, or command registry

## Important Patterns

### Exception Chaining
Always use `from` for exception chaining:
```python
try:
    something()
except SomeError as e:
    raise NewError("Context") from e  # Note: 'from e'
```

### Type Hints
- Use modern syntax: `list[str]` not `List[str]`, `dict[str, str]` not `Dict[str, str]`
- Use `Optional[Type]` for nullable values
- Type hints required for all function signatures

### File References
Users can include file contents with `@filename` or `@"file with spaces.txt"` syntax. The CLI automatically reads and prepends file contents to prompts.

## Dependencies

**Core**: click, requests, python-dotenv, pyyaml, rich, prompt_toolkit
**Dev**: pytest, pytest-cov, pytest-mock, ruff, mypy, pre-commit
**APIs**: anthropic, openai, google-generativeai

## Storage Locations

- **Config**: `~/.agent-cli/config.ini` (or XDG_CONFIG_HOME/agent-cli)
- **Sessions**: `~/.agent-cli/sessions.json` (or XDG_STATE_HOME/agent-cli)
- **MCP Servers**: `~/.agent-cli/mcp_servers.json` (or XDG_CONFIG_HOME/agent-cli)
- **Project .env**: `<project-root>/.env` (for development)

XDG paths only used when environment variables are explicitly set; otherwise defaults to `~/.agent-cli/` for all file types.
