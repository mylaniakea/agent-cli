# Changelog

All notable changes to agent-cli will be documented in this file.

## [Unreleased]

### Phase 10: Smart Message History (Inspired by code-puppy)

#### Added
- **HistoryManager**: Smart conversation history management (`agent_cli/history_manager.py`)
- **History Compaction**: Automatic and manual history compaction
  - `recent` strategy: Keep most recent messages (default)
  - `first` strategy: Keep first and last messages
  - `middle` strategy: Keep evenly distributed messages
- **Configurable Limits**: Message limits via `MESSAGE_LIMIT` config (default: 50)
- **Enhanced History Display**: Better formatting with truncation and message counts
- **Manual Compaction**: `/history compact` command for manual compaction

#### Changed
- **History Management**: Automatic compaction when limit exceeded
- **History Display**: Improved formatting with message counts and truncation
- **History Command**: Enhanced `/history` command with compaction support

#### Configuration
- `MESSAGE_LIMIT`: Maximum messages to keep (default: 50)
- `HISTORY_COMPACTION_STRATEGY`: Compaction strategy (default: "recent")

---

### Phase 9: Enhanced MCP Integration (Inspired by code-puppy)

#### Added
- **Enhanced MCP Commands**: Improved MCP server management
  - `mcp list --detailed`: Show detailed server information
  - `mcp add --validate`: Validate server configuration after adding
  - `mcp remove --force`: Remove without confirmation
  - `mcp show <name>`: Show detailed information about a server
- **Server Validation**: Basic validation of MCP server commands
- **Security**: Masking of sensitive environment variable values

#### Changed
- **Better Error Handling**: More informative error messages
- **Improved UX**: Better command output and feedback

---

### Phase 8: Model Factory Pattern (Inspired by code-puppy)

#### Added
- **ModelFactory**: Centralized model creation and management (`agent_cli/model_factory.py`)
- **Model Metadata**: JSON file with model information (context length, capabilities, settings)
- **Model Validation**: Validates models before use with helpful warnings
- **Enhanced list-models**: New `--detailed` and `--provider` options
  - `agent-cli list-models --detailed` - Show detailed model information
  - `agent-cli list-models --provider openai` - Filter by provider
- **Model Settings**: Model-specific settings (temperature, max_tokens) available via factory
- **ModelMetadata Class**: Dataclass for structured model information

#### Changed
- **list-models command**: Now uses ModelFactory and shows metadata
- **Model validation**: Warns when models not found in metadata (but doesn't fail)
- **Better error messages**: More helpful messages when models are invalid

#### Files Added
- `agent_cli/model_factory.py` - Model factory implementation
- `agent_cli/models.json` - Model metadata configuration

---

### Phase 7: Session Management (Inspired by code-puppy)

#### Added
- **Session Management**: Per-terminal session tracking with PPID-based session IDs
- **Session Persistence**: Session state saved to `~/.agent-cli/sessions.json`
- **Auto-Load Session State**: Interactive mode automatically loads last provider/model
- **Session Commands**: `/session` command for managing session state
  - `/session` - Show current session info
  - `/session new` - Create new session (clear state)
  - `/session clear` - Clear current session state
  - `/session list` - List all active sessions
- **Dead Session Cleanup**: Automatically removes sessions for closed terminals

#### Changed
- **Interactive Mode**: Provider and model are now optional in interactive mode (uses session state)
- **Auto-Save**: Session state automatically saved when provider/model changes
- **CLI Options**: `--provider` and `--model` are optional in interactive mode

#### Files Added
- `agent_cli/session_manager.py` - Session management implementation

---

### Phase 6: Enhanced Configuration Management (Inspired by code-puppy)

#### Added
- **XDG Base Directory Support**: Follows XDG Base Directory spec (uses XDG vars if set, otherwise ~/.agent-cli)
- **INI Config File Support**: Configuration can be stored in `~/.agent-cli/config.ini`
- **Configuration Priority System**: Environment variables > config.ini > .env > defaults
- **Runtime Config Updates**: `/set` command allows setting config values during interactive sessions
- **Config Persistence**: Values set via `/set` are saved to config.ini and persist across sessions

#### Changed
- **Config Class**: Enhanced to support multiple configuration sources with priority ordering
- **Backward Compatibility**: Full support for existing .env files maintained

#### Security
- **API Key Warnings**: `/set` command warns when setting API keys (recommends environment variables)

---

### Phase 5: Command Registry System (Inspired by code-puppy)

#### Added
- **Command Registry System**: Decorator-based command registration inspired by [code-puppy](https://github.com/mpfaffenberger/code_puppy)
  - `@register_command` decorator for easy command registration
  - Auto-generated help system
  - Command aliases support
  - Command categorization (core, config, session)
  - Dynamic command discovery

#### Changed
- **Interactive Commands**: Refactored all interactive commands to use the registry system
  - Commands are now registered via decorators instead of manual if/elif chains
  - Help text is auto-generated from command metadata
  - Easier to add new commands (just decorate a function)

#### Files Added
- `agent_cli/command_registry.py` - Command registry implementation
- `agent_cli/interactive_commands.py` - All interactive command handlers
- `DEVELOPMENT_PLAN.md` - Development roadmap
- `CODE_PUPPY_INSPIRATION.md` - Feature analysis from code-puppy
- `CHANGELOG.md` - This file

#### Files Modified
- `agent_cli/cli.py` - Updated to use command registry
- `README.md` - Updated development phases

## Phase 4: Advanced Features

### Added
- **Streaming Support**: Real-time token-by-token response streaming for all providers
- **Conversation Context**: Automatic conversation history management in interactive mode
- **File References**: Include file contents in prompts using `@filename` syntax
- **Interactive Commands**: Special commands for interactive mode
  - `/help` - Show available commands
  - `/model` - Switch models
  - `/provider` - Switch providers
  - `/stream` - Toggle streaming
  - `/clear` - Clear history
  - `/history` - Show history
  - `/config` - Show configuration
  - `/mcp` - MCP server info
- **MCP Server Management**: CLI commands for managing MCP servers
  - `agent-cli mcp list` - List servers
  - `agent-cli mcp add` - Add server
  - `agent-cli mcp remove` - Remove server

## Phase 3: External API Providers

### Added
- OpenAI integration
- Anthropic (Claude) integration
- Google (Gemini) integration

## Phase 2: Ollama Integration

### Added
- Local Ollama support
- Remote Ollama support (via OLLAMA_BASE_URL)

## Phase 1: Foundation

### Added
- Basic CLI structure
- Configuration management
- Agent factory pattern

