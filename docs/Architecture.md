# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      CLI Layer                           │
│  (Click commands: chat, list-models, config, mcp)       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Command Registry System                    │
│  (Decorator-based command registration & help)          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            Configuration & Session Layer               │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │   Config     │  │   Session    │                    │
│  │  Manager     │  │   Manager    │                    │
│  └──────────────┘  └──────────────┘                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Model & Agent Layer                        │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │   Model      │  │    Agent     │                    │
│  │   Factory    │  │   Factory    │                    │
│  └──────────────┘  └──────────────┘                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Provider Layer                         │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐               │
│  │Ollama│  │OpenAI│  │Anthropic│ │Google│               │
│  └──────┘  └──────┘  └──────┘  └──────┘               │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### CLI Layer (`agent_cli/cli.py`)
- Click-based command interface
- Command routing and argument parsing
- User interaction handling

### Command Registry (`agent_cli/command_registry.py`)
- Decorator-based command registration
- Auto-generated help system
- Command discovery and routing

### Configuration Manager (`agent_cli/config.py`)
- Multi-source configuration (env, ini, .env)
- XDG Base Directory support
- Runtime config updates

### Session Manager (`agent_cli/session_manager.py`)
- Per-terminal session tracking
- State persistence
- Session isolation

### Model Factory (`agent_cli/model_factory.py`)
- Model metadata management
- Model validation
- Model-specific settings

### Agent Factory (`agent_cli/agents/factory.py`)
- Provider abstraction
- Agent creation
- Provider routing

### History Manager (`agent_cli/history_manager.py`)
- Conversation history management
- Automatic compaction
- Message limits

## Data Flow

### Chat Request Flow

```
User Input
    ↓
CLI Command Handler
    ↓
Session Manager (load state)
    ↓
Model Factory (validate model)
    ↓
Agent Factory (create agent)
    ↓
Provider Agent (make API call)
    ↓
Response Processing
    ↓
History Manager (add to history)
    ↓
Session Manager (save state)
    ↓
User Output
```

### Configuration Resolution

```
Request for config value
    ↓
1. Environment Variable? → Yes → Use it
    ↓ No
2. config.ini file? → Yes → Use it
    ↓ No
3. .env file? → Yes → Use it
    ↓ No
4. Default value → Use it
```

## Key Design Patterns

### Factory Pattern
- **AgentFactory**: Creates provider-specific agents
- **ModelFactory**: Manages model metadata and settings

### Registry Pattern
- **CommandRegistry**: Dynamic command discovery
- **Agent Registry**: Provider-to-agent mapping

### Manager Pattern
- **ConfigManager**: Configuration lifecycle
- **SessionManager**: Session state management
- **HistoryManager**: Conversation history management

## Extension Points

### Adding a New Provider

1. Create agent class in `agent_cli/agents/`
2. Inherit from `BaseAgent`
3. Implement `chat()`, `stream()`, `list_models()`
4. Register in `AgentFactory`
5. Add model metadata to `models.json`

### Adding a New Command

1. Create handler function
2. Decorate with `@register_command`
3. Import in `cli.py` (auto-registered)
4. Command appears in help automatically

### Adding Configuration

1. Add to `Config` class `__init__`
2. Use `_get_value()` for priority resolution
3. Add to config.ini template
4. Document in Configuration guide

## File Structure

```
agent-cli/
├── agent_cli/
│   ├── __init__.py
│   ├── cli.py                 # Main CLI entry point
│   ├── config.py               # Configuration management
│   ├── command_registry.py     # Command registration system
│   ├── session_manager.py      # Session state management
│   ├── model_factory.py        # Model metadata & validation
│   ├── history_manager.py      # Conversation history management
│   ├── models.json             # Model metadata
│   ├── agents/
│   │   ├── base.py            # Base agent interface
│   │   ├── factory.py         # Agent factory
│   │   ├── ollama_agent.py
│   │   ├── openai_agent.py
│   │   ├── anthropic_agent.py
│   │   └── google_agent.py
│   └── interactive_commands.py # Interactive command handlers
├── docs/                       # Documentation
├── tests/                      # Test suite
└── README.md
```

## Dependencies

- **click**: CLI framework
- **requests**: HTTP client for API calls
- **python-dotenv**: .env file support
- **configparser**: INI file support (built-in)

## Configuration Storage

- **Config**: `~/.agent-cli/config.ini` (or XDG_CONFIG_HOME)
- **Sessions**: `~/.agent-cli/sessions.json` (or XDG_STATE_HOME)
- **MCP Servers**: `~/.agent-cli/mcp_servers.json` (or XDG_CONFIG_HOME)

See [Configuration Guide](Configuration) for details.

