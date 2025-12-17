# Agent CLI

[![Tests](https://github.com/mpfaffenberger/agent-cli/actions/workflows/test.yml/badge.svg)](https://github.com/mpfaffenberger/agent-cli/actions/workflows/test.yml)
[![Lint](https://github.com/mpfaffenberger/agent-cli/actions/workflows/lint.yml/badge.svg)](https://github.com/mpfaffenberger/agent-cli/actions/workflows/lint.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

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

## Development Status

### Core Development ✅ Complete (Phases 1-11)
- Foundation & CLI structure
- Multi-provider support (Ollama, OpenAI, Anthropic, Google)
- Interactive mode with streaming
- Command registry system (inspired by [code-puppy](https://github.com/mpfaffenberger/code_puppy))
- Enhanced configuration management
- Session management & state persistence
- Model factory pattern with metadata
- MCP integration
- Smart message history management
- Specialized agents (personas) & themes

### Next: Open Source Release Preparation (Phases 12-22)

We're preparing for v1.0 release with:
- 🧪 **Testing Infrastructure** - Comprehensive test suite with CI/CD
- 📦 **Modern Packaging** - PyPI publication with pyproject.toml
- 🔍 **Code Quality** - Type hints, linting, pre-commit hooks
- 📚 **Documentation** - Complete wiki, contributor guides
- 🚀 **New Features** - Export, context management, security enhancements

**See [OPEN_SOURCE_PLAN.md](OPEN_SOURCE_PLAN.md) for detailed roadmap.**

🤝 **Want to contribute?** We'd love your help! Check out the open source plan and pick a phase to work on.

## 📖 Documentation & Wiki

We have moved our detailed documentation to a dedicated Wiki.
👉 **[Read the Full Wiki](WIKI.md)**

The Wiki includes:
- **Getting Started**: Installation and basic usage.
- **Themes**: customized your CLI look.
- **Specialized Agents**: Creating and managing custom personas.
- **Configuration**: Advanced settings and MCP setup.

## Acknowledgments

This project was inspired by and borrows patterns from [code-puppy](https://github.com/mpfaffenberger/code_puppy), adapted for a simpler, provider-focused architecture.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/mpfaffenberger/agent-cli.git
cd agent-cli

# Install with development dependencies
make install
```

### Running Tests

```bash
make test          # Run tests with coverage
make lint          # Check code style
make format        # Format code
make typecheck     # Run type checker
make all           # Run all checks
```

### Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [code_puppy](https://github.com/mpfaffenberger/code_puppy)
- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Uses [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for interactive mode
