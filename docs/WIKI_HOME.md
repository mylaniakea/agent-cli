# Agent CLI - GitHub Wiki Home

Welcome to the Agent CLI documentation! This wiki provides comprehensive information about using, configuring, and extending agent-cli.

## 📚 Documentation Index

### Getting Started
- [Installation Guide](Installation)
- [Quick Start Guide](Quick-Start)
- [Configuration Guide](Configuration)

### User Guides
- [Basic Usage](Basic-Usage)
- [Interactive Mode](Interactive-Mode)
- [Streaming Responses](Streaming)
- [File References](File-References)
- [Session Management](Session-Management)

### Advanced Features
- [Model Factory](Model-Factory)
- [MCP Integration](MCP-Integration)
- [Message History Management](Message-History)
- [Command Registry](Command-Registry)

### Development
- [Architecture Overview](Architecture)
- [Adding New Providers](Adding-Providers)
- [Development Phases](Development-Phases)
- [Contributing](Contributing)

### Reference
- [Command Reference](Command-Reference)
- [Configuration Reference](Configuration-Reference)
- [API Reference](API-Reference)

---

## 🚀 Quick Links

- **Installation**: `pip install -e .` or see [Installation Guide](Installation)
- **Quick Start**: `agent-cli --provider ollama --model llama2 --interactive`
- **Documentation**: See sidebar for detailed guides
- **Issues**: Report bugs or request features on GitHub

---

## 📖 What is Agent CLI?

Agent CLI is a command-line interface for interacting with Large Language Models (LLMs) from multiple providers. It supports:

- **Local Models**: Ollama (local or remote)
- **Cloud Providers**: OpenAI, Anthropic (Claude), Google (Gemini)
- **Advanced Features**: Streaming, conversation context, file references, session management

## Key Features

- 🏠 **Local & Remote**: Use Ollama locally or connect to remote instances
- 🔑 **BYO API Keys**: Bring your own API keys for cloud providers
- 🌊 **Streaming**: Real-time token-by-token responses
- 💬 **Context**: Maintains conversation history automatically
- 📁 **File Support**: Include file contents with `@filename` syntax
- 💾 **Sessions**: Each terminal remembers its settings
- ⚙️ **Configurable**: Multiple configuration sources with priority

## Example Usage

```bash
# Simple query
agent-cli --provider ollama --model llama2 "What is Python?"

# Interactive mode with streaming
agent-cli --provider openai --model gpt-4 --interactive --stream

# Include file in prompt
agent-cli --provider anthropic --model claude-3-sonnet "@README.md summarize this"
```

---

## 🎯 Project Status

**Current Version**: 0.1.0 (Pre-release)

**Core Development**: ✅ Complete (Phases 1-11)

**Open Source Release Preparation**: 🚀 In Progress (Phases 12-22)
- Phase 12: Testing Infrastructure
- Phase 13: Modern Packaging (PyPI)
- Phase 14: Code Quality & Type Safety
- Phase 15: Update Model Metadata
- Phase 16-21: Feature Enhancements
- Phase 22: Final Release (v1.0)

**Target**: v1.0 release with comprehensive testing, modern packaging, and community guidelines.

See [OPEN_SOURCE_PLAN.md](../OPEN_SOURCE_PLAN.md) for detailed roadmap.

---

## 🤝 Contributing

We welcome contributions! See [Contributing Guide](Contributing) for:
- Code style guidelines
- How to submit pull requests
- Development setup
- Testing requirements

---

## 📝 License

MIT License - see [LICENSE](../LICENSE) file for details.

---

## 🙏 Acknowledgments

This project was inspired by and borrows patterns from [code-puppy](https://github.com/mpfaffenberger/code_puppy), adapted for a simpler, provider-focused architecture.

