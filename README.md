# Agent CLI 🤖

[![Tests](https://github.com/mpfaffenberger/agent/actions/workflows/test.yml/badge.svg)](https://github.com/mpfaffenberger/agent/actions/workflows/test.yml)
[![Lint](https://github.com/mpfaffenberger/agent/actions/workflows/lint.yml/badge.svg)](https://github.com/mpfaffenberger/agent/actions/workflows/lint.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A beautiful, feature-rich CLI for interacting with AI models. Supports local models (Ollama), cloud providers (OpenAI, Anthropic, Google), with advanced features like fallback providers, project-specific configurations, and intelligent context management.

---

## ✨ Highlights

- 🎨 **Beautiful UI** - Keyboard-driven selection, themed completion menus, clean prompt design
- 🔄 **Fallback Providers** - Automatic failover when primary provider is unavailable
- 📋 **Project Configs** - Per-project settings with templates for Python, React, and more
- 🧠 **Smart Context** - Beads integration for persistent project memory
- ⌨️ **Interactive** - Multi-select UI, auto-popup menus, visual feedback
- 🎨 **11 Themes** - Choose from catppuccin, dracula, nord, tokyo-night, and more
- 🦙 **Ollama Timer** - See how long your local model stays loaded
- 🚀 **Fast Setup** - Guided onboarding wizard with smart defaults

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/mpfaffenberger/agent-cli
cd agent-cli

# Install with uv (recommended) or pip
uv pip install -e .
# or
pip install -e .

# Start the interactive wizard
./agent chat

# Or use the installed command
agent-cli chat
```

---

## 🎯 Features

### Core Features

#### 🤖 **Multi-Provider Support**
- **Ollama** - Local models (llama3.3, deepseek, qwen, etc.)
- **OpenAI** - GPT-4, GPT-4o, o1, o1-mini
- **Anthropic** - Claude 3.5 Sonnet, Claude 3.5 Haiku
- **Google** - Gemini 1.5 Pro, Gemini 1.5 Flash

#### 🔄 **Automatic Fallback**
Configure a backup provider that activates automatically when your primary fails:
```yaml
# .agent.yml
PRIMARY_PROVIDER: anthropic
FALLBACK_PROVIDER: ollama
```

Never lose your workflow due to API downtime!

#### 📋 **Project-Specific Configuration**
```bash
# Initialize project config
/init anthropic

# Creates claude.md or .agent.yml with:
# - Provider and model settings
# - System prompts for your project
# - Context file inclusion
# - Git integration
```

#### 🎨 **Beautiful Interactive UI**
- **Keyboard Navigation** - Arrow keys, spacebar to select, Enter to confirm
- **Auto-Popup Menus** - Type `/` to see all commands instantly
- **Multi-Select** - Choose multiple providers during onboarding
- **11 Themes** - catppuccin, dracula, nord, tokyo-night, gruvbox, and more

#### 🧠 **Beads Integration**
Persistent project context that never forgets:
- Automatic conversation summarization
- Git-aware context updates
- Team-shared knowledge base
- Semantic search through history

---

## 📖 Installation

### Prerequisites
- Python 3.9 or higher
- (Optional) [Ollama](https://ollama.ai) for local models
- (Optional) [Nerd Fonts](https://www.nerdfonts.com/) for better icons

### Install Agent CLI

```bash
# Clone repository
git clone https://github.com/mpfaffenberger/agent-cli
cd agent-cli

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install CLI
pip install -e .
```

### Optional: Install Nerd Fonts

For better provider icons (󰝰 instead of 🦙):
```bash
./install_nerd_fonts.sh
# Then set your terminal font to "JetBrainsMono Nerd Font"
```

---

## 🎮 Usage

### Interactive Mode (Default)

```bash
# Start interactive chat
./agent chat

# Or use the installed command
agent-cli chat

# Specify provider and model
./agent chat --provider anthropic --model claude-3-5-sonnet-20241022
```

**Interactive Commands:**
```
/help        - Show all commands
/provider    - Switch provider
/model       - Switch model
/theme       - Change UI theme
/init        - Initialize project config
/fallback    - Configure fallback provider
/beads       - Beads context management
/history     - View conversation history
/clear       - Clear conversation
/exit        - Exit chat
```

### Non-Interactive Mode

```bash
# Single prompt
./agent chat --non-interactive "Explain quantum computing"

# Pipe input
echo "Write a Python function" | ./agent chat --non-interactive

# Streaming output
./agent chat --stream --non-interactive "Tell me a story"
```

### List Available Models

```bash
./agent models
./agent models --provider ollama
```

---

## ⚙️ Configuration

### Configuration Priority

1. **Environment variables** (highest)
2. **Project config** (`.agent.yml` or `claude.md`)
3. **User config** (`~/.agent-cli/config.ini`)
4. **.env file** (project root)
5. **Defaults** (lowest)

### Environment Variables

```bash
# API Keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."

# Ollama Configuration
export OLLAMA_BASE_URL="http://localhost:11434"
export DEFAULT_OLLAMA_MODEL="llama3.3"
export OLLAMA_KEEP_ALIVE="5"  # minutes

# Default Provider
export PRIMARY_PROVIDER="anthropic"
export FALLBACK_PROVIDER="ollama"
```

### Project Configuration

Create a project-specific config:

```bash
./agent chat
/init anthropic

# Creates claude.md:
---
provider: anthropic
model: claude-3-5-sonnet-20241022
temperature: 0.3
---

# Project Instructions

You are an expert FastAPI developer...
```

**Or use YAML:**
```yaml
# .agent.yml
provider: anthropic
model: claude-3-5-sonnet-20241022
temperature: 0.3

system_prompt: |
  You are an expert Python developer.
  Follow PEP 8 conventions.

# Fallback provider
fallback_provider: ollama
fallback_model: deepseek-coder-v2

# Context files to include
context_files:
  - "README.md"
  - "src/**/*.py"
  - "!**/test_*.py"

# Beads configuration
beads:
  enabled: true
  max_messages: 20
  summary_threshold: 15
```

### User Configuration

Edit `~/.agent-cli/config.ini`:
```ini
[agent-cli]
PRIMARY_PROVIDER = anthropic
FALLBACK_PROVIDER = ollama
DEFAULT_ANTHROPIC_MODEL = claude-3-5-sonnet-20241022
DEFAULT_OLLAMA_MODEL = llama3.3
THEME = catppuccin
```

---

## 🎨 Themes

11 beautiful themes to choose from:

```bash
# Switch themes in interactive mode
/theme catppuccin
/theme dracula
/theme nord
/theme tokyo-night
```

**Available themes:**
- `default` - Clean and minimal
- `catppuccin` - Soothing pastel theme
- `dracula` - Dark with vibrant colors
- `monokai` - Classic editor theme
- `simple` - No-frills minimal
- `solarized` - Easy on the eyes
- `nord` - Arctic, north-bluish
- `gruvbox` - Retro groove colors
- `tokyo-night` - Deep night theme
- `one-dark` - Atom's iconic theme
- `synthwave` - Neon cyberpunk

---

## 🧙 First-Run Wizard

On first run, you'll see a beautiful guided setup:

```
╭────────────────────────────────────────────╮
│ 🚀 Welcome to Agent CLI!                  │
╰────────────────────────────────────────────╯

Select providers to configure:

[*] 🤖 OpenAI (GPT-4, o1)
[ ] 🧠 Anthropic (Claude)
[*] 🦙 Ollama (Local)

Use ↑/↓ to navigate, SPACE to select, ENTER when done
```

The wizard will:
1. ✅ Guide you through provider setup
2. ✅ Configure API keys securely
3. ✅ Test connections
4. ✅ Set up primary and fallback providers
5. ✅ Save configuration

---

## 🔄 Fallback Providers

Configure automatic failover:

```bash
# During onboarding, you'll be asked:
Select your PRIMARY provider: anthropic
Select your FALLBACK provider: ollama

# Or configure manually:
/set PRIMARY_PROVIDER anthropic
/set FALLBACK_PROVIDER ollama
```

**How it works:**
1. Primary provider fails (network, API key, rate limit)
2. Automatic switch to fallback
3. Clear notification in UI
4. Seamless continuation of conversation

**Example:**
```
⚠️  Primary provider 'anthropic' failed: Connection timeout
ℹ️  Attempting fallback to 'ollama'...
✓ Using fallback provider: ollama with model llama3.3

🦙 llama3.3 | You ➜ [conversation continues]
```

---

## 📋 Project Initialization

Initialize project-specific settings with `/init`:

```bash
./agent chat
/init

# Launches interactive wizard:
╭────────────────────────────────────────────╮
│ 🚀 Project Initialization Wizard          │
╰────────────────────────────────────────────╯

Select provider: [anthropic]
Select project type: [Python / FastAPI]
Select template: [FastAPI Development]

🔍 Analyzing project...
  ✓ Detected: Python 3.11 + FastAPI
  ✓ Framework: FastAPI
  ✓ Files: 234

✨ Created claude.md with project template!
```

**Features:**
- Smart project detection (language, framework)
- Pre-built templates (Python, React, Node, etc.)
- Automatic context file inclusion
- Git integration
- Beads setup

---

## 🧠 Beads Context Management

Persistent project memory that grows with your project:

```bash
# Enable Beads during /init
# Or manually:
/beads status

# Beads provides:
# - Automatic conversation summarization
# - Multi-layer context (current, daily, weekly)
# - Git-aware updates
# - Semantic search
# - Team synchronization
```

**Configuration:**
```yaml
# .agent.yml
beads:
  enabled: true
  max_messages: 20
  summary_threshold: 15

  # Git integration
  git_integration: true
  include_commits: 20

  # Team features
  team_sync: true
  shared_context: .beads/team-context.md
```

---

## 🎯 Slash Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/provider [name]` | Switch or show current provider |
| `/model [name]` | Switch or show current model |
| `/theme [name]` | Change UI theme |
| `/init [provider]` | Initialize project config |
| `/config` | Show current configuration |
| `/set KEY VALUE` | Set configuration value |
| `/history` | Show conversation history |
| `/clear` | Clear conversation history |
| `/session` | Show session information |
| `/export [format]` | Export conversation |
| `/system [prompt]` | Set system prompt |
| `/compress` | Compress conversation history |
| `/beads [cmd]` | Beads context management |
| `/reasoning` | Toggle reasoning display |
| `/stream` | Toggle streaming mode |
| `/keepalive [min]` | Set Ollama keep-alive time |
| `/mcp` | Manage MCP servers |
| `/agent` | Manage agents (personas) |
| `/setup [provider]` | Interactive provider setup |
| `/exit` | Exit chat |

---

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/mpfaffenberger/agent-cli
cd agent-cli

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Install dev tools
pip install ruff pytest

# Run tests
pytest

# Lint code
ruff check agent_cli/
```

### Project Structure

```
agent-cli/
├── agent_cli/
│   ├── agents/              # Provider implementations
│   ├── interactive_commands.py  # Slash commands
│   ├── ui.py                # UI components
│   ├── config.py            # Configuration management
│   ├── beads.py             # Context management
│   ├── interactive_select.py    # Keyboard UI
│   └── ...
├── docs/                    # Documentation
├── tests/                   # Test suite
├── .agent.yml               # Project config example
└── README.md
```

---

## 📚 Documentation

Comprehensive guides available:

- **[INIT_SUPERPOWER_DESIGN.md](INIT_SUPERPOWER_DESIGN.md)** - Project initialization design
- **[BEADS_SUPER_INIT_DESIGN.md](BEADS_SUPER_INIT_DESIGN.md)** - Beads integration design
- **[MENU_CONSISTENCY.md](MENU_CONSISTENCY.md)** - UI menu system
- **[ONBOARDING_IMPROVEMENTS.md](ONBOARDING_IMPROVEMENTS.md)** - Onboarding flow
- **[BEAUTIFICATION_SUMMARY.md](BEAUTIFICATION_SUMMARY.md)** - UI improvements
- **[ROADMAP.md](ROADMAP.md)** - Development roadmap

---

## 🗺️ Roadmap

### Phase 1: Super Init - Basic (Current)
- ✅ Interactive wizard with keyboard UI
- ✅ Project type detection
- ✅ Template selection
- ✅ Beads auto-detection and install
- ⏳ Initial project context generation

### Phase 2: Deep Integration
- ⏳ Multi-layer context system
- ⏳ Git hooks for auto-updates
- ⏳ Smart configuration by project type
- ⏳ Session management

### Phase 3: Team Features
- ⏳ Shared context files
- ⏳ Auto-merge capabilities
- ⏳ Semantic search
- ⏳ Team dashboard

See [ROADMAP.md](ROADMAP.md) for full details.

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Ollama** - For making local LLMs accessible
- **Anthropic** - For Claude's excellent coding abilities
- **OpenAI** - For pioneering accessible AI
- **Google** - For Gemini's capabilities
- **Beads** - For conversation summarization concept
- **prompt_toolkit** - For the beautiful terminal UI
- **rich** - For styled terminal output

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/mpfaffenberger/agent-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mpfaffenberger/agent-cli/discussions)

---

**Built with ❤️ by developers, for developers.**
