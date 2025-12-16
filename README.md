# Agent CLI

A custom LLM CLI tool that supports local agents (via Ollama) and external API providers with your own API keys.

## Features

- 🏠 **Local Agents**: Use Ollama-hosted models locally
- 🔑 **BYO API Key**: Bring your own API keys for external providers
- 🎯 **Flexible**: Easy to extend with new providers
- ⚡ **Fast**: Optimized for quick interactions
- 🌊 **Streaming**: Real-time token-by-token response streaming
- 💬 **Context**: Maintains conversation history in interactive mode

## Supported Providers

- **Ollama**: Local models (llama2, mistral, etc.)
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude 3 (Opus, Sonnet, Haiku)
- **Google**: Gemini Pro, Gemini 1.5 Pro/Flash

## Installation

```bash
# Clone or navigate to the project
cd agent-cli

# Install dependencies
pip install -r requirements.txt

# Install the CLI
pip install -e .
```

## Configuration

Configuration can be set via multiple methods (priority order):

1. **Environment variables** (highest priority)
2. **config.ini file** (`~/.agent-cli/config.ini`)
3. **.env file** (project root)
4. **Default values**

### Using .env file (project root)

```bash
# Ollama configuration (default: http://localhost:11434)
# Can be set to remote server: http://192.168.1.100:11434
OLLAMA_BASE_URL=http://localhost:11434

# External API keys (optional)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

### Using config.ini file

Configuration is automatically saved to `~/.agent-cli/config.ini` when using the `/set` command in interactive mode, or you can edit it directly:

```ini
[agent-cli]
OLLAMA_BASE_URL=http://192.168.1.100:11434
DEFAULT_OLLAMA_MODEL=mistral
```

### Runtime Configuration Updates

Use the `/set` command in interactive mode:

```bash
agent-cli --provider ollama --model llama2 --interactive
You: /set OLLAMA_BASE_URL=http://192.168.1.100:11434
Set OLLAMA_BASE_URL = http://192.168.1.100:11434
```

**Note**: 
- Ollama supports remote servers! Set `OLLAMA_BASE_URL` to any network-accessible Ollama instance.
- API keys should be set via environment variables for security.
- Config file values are overridden by environment variables.

## Usage

```bash
# Use a local Ollama model
agent-cli --provider ollama --model llama2 "What is Python?"

# Use OpenAI (requires API key)
agent-cli --provider openai --model gpt-4 "Explain quantum computing"

# Use Anthropic (requires API key)
agent-cli --provider anthropic --model claude-3-sonnet "Write a poem"

# Use Google Gemini (requires API key)
agent-cli --provider google --model gemini-pro "What is machine learning?"

# Interactive mode (provider/model optional - uses last session)
agent-cli --provider ollama --model llama2 --interactive

# Interactive mode without provider/model (uses last session state)
agent-cli --interactive

# Streaming mode (real-time token output)
agent-cli --provider openai --model gpt-4 --stream "Explain quantum computing"

# Interactive mode with streaming
agent-cli --provider ollama --model llama2 --interactive --stream
```

## Development Phases

- [x] Phase 1: Foundation & CLI structure
- [x] Phase 2: Ollama integration
- [x] Phase 3: External API providers (OpenAI, Anthropic, Google)
- [x] Phase 4: Advanced features (streaming, context, file references, interactive commands, MCP config)
- [x] Phase 5: Command Registry System (inspired by [code-puppy](https://github.com/mpfaffenberger/code_puppy))
- [x] Phase 6: Enhanced Configuration Management (XDG support, INI config, `/set` command)
- [x] Phase 7: Session Management (per-terminal state persistence, auto-load last provider/model)
- [x] Phase 8: Model Factory Pattern (centralized model metadata, validation, settings)
- [x] Phase 9: Enhanced MCP Integration (improved server management, validation)
- [x] Phase 10: Smart Message History (compaction, limits, better display)

**🎉 All Phases Complete! 🎉**

See [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) for detailed implementation plan.
See [docs/](docs/) for comprehensive documentation ready for GitHub wiki.

## Advanced Features

### Streaming Responses

Enable real-time streaming of responses with the `--stream` flag:

```bash
# Stream a single response
agent-cli --provider openai --model gpt-4 --stream "Write a story"

# Stream in interactive mode
agent-cli --provider ollama --model llama2 --interactive --stream
```

### Conversation Context

In interactive mode, the CLI automatically maintains conversation history, allowing the agent to remember previous messages in the session:

```bash
agent-cli --provider anthropic --model claude-3-sonnet --interactive
```

The conversation history is maintained throughout the interactive session, providing context-aware responses.

### Interactive Commands

In interactive mode, you can use special commands:

- `/help` or `/h` - Show available commands
- `/model <name>` or `/m` - Switch to a different model
- `/provider <name>` or `/p` - Switch to a different provider (ollama, openai, anthropic, google)
- `/stream` or `/s` - Toggle streaming mode on/off
- `/clear` or `/c` - Clear conversation history
- `/history` or `/hist` - Show recent conversation history
- `/config` or `/cfg` - Show current configuration
- `/set <key>=<value>` - Set a configuration value (saved to config.ini)
- `/session` or `/sess` - Show or manage session state
- `/mcp` - Manage MCP servers (use `agent-cli mcp` command)

Example:
```bash
agent-cli --provider ollama --model llama2 --interactive
You: /model mistral
Switched to model: mistral

You: /provider openai
Switched to provider: openai
```

### File References

Include file contents in your prompts using the `@filename` syntax:

```bash
# In interactive mode
You: @config.py explain this file

# In non-interactive mode
agent-cli --provider ollama --model llama2 "@README.md summarize this file"

# Files with spaces
You: @"my file.txt" analyze this
```

The file contents will be automatically included in the prompt sent to the agent.

### MCP Server Management

Manage Model Context Protocol (MCP) servers:

```bash
# List configured MCP servers
agent-cli mcp list

# Add an MCP server
agent-cli mcp add my-server /path/to/server --arg1 value1 -e KEY=value

# Remove an MCP server
agent-cli mcp remove my-server
```

MCP servers are stored in `~/.agent-cli/mcp_servers.json`.

## Documentation

Comprehensive documentation is available in the `docs/` directory, ready for GitHub wiki:

- [Installation Guide](docs/Installation.md)
- [Quick Start](docs/Quick-Start.md)
- [Architecture Overview](docs/Architecture.md)
- [Command Reference](docs/Command-Reference.md)
- [Development Phases](docs/Development-Phases.md)
- [Project Summary](docs/PROJECT_SUMMARY.md)

See [docs/WIKI_SETUP.md](docs/WIKI_SETUP.md) for GitHub wiki setup instructions.

## Acknowledgments

This project was inspired by and borrows patterns from [code-puppy](https://github.com/mpfaffenberger/code_puppy), adapted for a simpler, provider-focused architecture.
