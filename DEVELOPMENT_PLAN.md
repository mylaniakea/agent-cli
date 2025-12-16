# Development Plan: Code-Puppy Inspired Enhancements

This document outlines our plan to adapt, borrow, and improve features from the [code-puppy](https://github.com/mpfaffenberger/code_puppy) project to enhance agent-cli.

## 🎯 Project Goals

**Adapt**: Take proven patterns and adapt them to our simpler, provider-focused architecture  
**Borrow**: Use battle-tested solutions for common problems  
**Improve**: Simplify where code-puppy is complex, enhance where we can add value

## 📋 Implementation Phases

### Phase 5: Command Registry System ⚡ ✅ COMPLETE

**Inspired by**: code-puppy's `command_registry.py`

**What we're adapting**:
- Decorator-based command registration
- Auto-generated help system
- Command aliases and categories
- Dynamic command discovery

**What we're improving**:
- Simpler implementation (no need for complex categories)
- Better integration with Click framework
- Cleaner command handler signatures

**Implementation**:
- [x] Create command registry module (`agent_cli/command_registry.py`)
- [x] Refactor existing interactive commands to use registry (`agent_cli/interactive_commands.py`)
- [x] Add auto-generated help system
- [x] Support command aliases (e.g., `/h` for `/help`, `/m` for `/model`)
- [x] Update CLI to use registry
- [x] Test all commands work with new registry system

**Results**:
- All 8 interactive commands now use the registry system
- Help is auto-generated from command metadata
- Commands are organized by category (core, config, session)
- Aliases work correctly (e.g., `/h`, `/m`, `/p`, `/s`, `/c`, `/hist`, `/cfg`)
- Adding new commands is now trivial (just add a decorated function)

---

### Phase 6: Enhanced Configuration Management 🔧 ✅ COMPLETE

**Inspired by**: code-puppy's `config.py` with XDG support

**What we're adapting**:
- Config file support (INI format)
- XDG Base Directory compliance
- Runtime config updates
- Config validation

**What we're improving**:
- Keep .env support (code-puppy doesn't use .env)
- Simpler config structure (we don't need as many directories)
- Better defaults
- Priority system: env > ini > .env > defaults

**Implementation**:
- [x] Add config.ini support alongside .env
- [x] Implement XDG directory structure (with fallback to ~/.agent-cli)
- [x] Add `/set` command for runtime config updates
- [x] Config validation and defaults
- [x] Backward compatibility with .env files maintained

**Results**:
- Configuration priority: Environment variables > config.ini > .env > defaults
- XDG Base Directory support (uses XDG vars if set, otherwise ~/.agent-cli)
- `/set` command allows runtime config updates
- Config values persist to `~/.agent-cli/config.ini`
- Full backward compatibility with existing .env files
- API key security warning when setting via /set

---

### Phase 7: Session Management 💾 ✅ COMPLETE

**Inspired by**: code-puppy's session-based agent selection

**What we're adapting**:
- Per-terminal session tracking
- Last provider/model persistence
- Session isolation

**What we're improving**:
- Simpler session ID generation
- Better session file format
- Clearer session management commands
- Auto-load session state in interactive mode

**Implementation**:
- [x] Session ID generation (PPID-based) (`session_manager.py`)
- [x] Session state persistence to `~/.agent-cli/sessions.json`
- [x] Remember last provider/model per session
- [x] Session management commands (`/session`, `/session new`, `/session clear`, `/session list`)
- [x] Auto-load session state when starting interactive mode
- [x] Auto-save session state when provider/model changes
- [x] Dead session cleanup (removes sessions for closed terminals)

**Results**:
- Each terminal session remembers its last provider/model
- Interactive mode auto-loads last session state
- Provider/model are optional in interactive mode (uses session state)
- Session state persists across CLI invocations
- Dead sessions are automatically cleaned up
- Session management commands for viewing/clearing sessions

---

### Phase 8: Model Factory Pattern 🏭 ✅ COMPLETE

**Inspired by**: code-puppy's `model_factory.py`

**What we're adapting**:
- Centralized model creation
- Model metadata management
- Model-specific settings
- Provider abstraction

**What we're improving**:
- Simpler factory (we have fewer providers)
- Better error messages
- Model validation
- Enhanced list-models command with metadata

**Implementation**:
- [x] Create ModelFactory class (`agent_cli/model_factory.py`)
- [x] Model metadata JSON file (`agent_cli/models.json`)
- [x] Model settings management (temperature, max_tokens per model)
- [x] Provider abstraction layer
- [x] Model validation before use
- [x] Enhanced `list-models` command with `--detailed` and `--provider` options
- [x] Model metadata integration (context length, capabilities)

**Results**:
- Centralized model metadata management
- Model validation with helpful warnings
- Enhanced `list-models` command shows metadata
- Model-specific settings (temperature, max_tokens) available
- Better error messages when models not found
- Foundation for future model-specific optimizations

---

### Phase 9: Enhanced MCP Integration 🔌 ✅ COMPLETE

**Inspired by**: code-puppy's MCP integration

**What we're adapting**:
- Enhanced MCP server management
- Better error handling
- Server validation

**What we're improving**:
- Better error handling and validation
- Enhanced CLI commands with more options
- Detailed server information display

**Implementation**:
- [x] Enhanced `mcp list` command with `--detailed` option
- [x] Enhanced `mcp add` command with `--validate` option
- [x] Enhanced `mcp remove` command with `--force` option
- [x] New `mcp show` command for detailed server info
- [x] Better error handling and user feedback
- [x] Security improvements (masking sensitive values)

**Results**:
- Better MCP server management UX
- Validation of server configurations
- More informative command output
- Improved error messages

---

### Phase 10: Smart Message History 📚 ✅ COMPLETE

**Inspired by**: code-puppy's message history management

**What we're adapting**:
- History compaction strategies
- Message limits
- Better history display

**What we're improving**:
- Simpler compaction (we don't need as complex)
- Better history display with truncation
- Configurable limits via config
- Automatic compaction

**Implementation**:
- [x] History compaction strategies (`recent`, `first`, `middle`)
- [x] Configurable message limits (via MESSAGE_LIMIT config)
- [x] Enhanced history display with formatting
- [x] Automatic compaction when limit exceeded
- [x] Manual compaction via `/history compact`
- [x] HistoryManager module (`agent_cli/history_manager.py`)

**Results**:
- Prevents context window overflow
- Better history display with truncation
- Configurable limits (default: 50 messages)
- Multiple compaction strategies
- Automatic and manual compaction support

---

## 🏗️ Architecture Improvements

### Current Architecture
```
CLI → Agent Factory → Agents → Providers
```

### Improved Architecture (After Phases 5-10)
```
CLI → Command Registry → Handlers
     ↓
Config Manager (XDG + .env)
     ↓
Model Factory → Agents → Providers
     ↓
Session Manager (persistence)
     ↓
MCP Manager (runtime integration)
```

## 📊 Progress Tracking

### Completed Phases
- [x] Phase 1: Foundation & CLI structure
- [x] Phase 2: Ollama integration
- [x] Phase 3: External API providers (OpenAI, Anthropic, Google)
- [x] Phase 4: Advanced features (streaming, context, file references, interactive commands, MCP config)

### Current Phase
- [x] Phase 5: Command Registry System ✅
- [x] Phase 6: Enhanced Configuration Management ✅
- [x] Phase 7: Session Management ✅
- [x] Phase 8: Model Factory Pattern ✅
- [x] Phase 9: Enhanced MCP Integration ✅
- [x] Phase 10: Smart Message History ✅

**🎉 All Planned Phases Complete! 🎉**

**Total Phases**: 10  
**Completed**: 10 (100%)  
**Status**: ✅ **PROJECT COMPLETE**

## 🎨 Design Principles

### What We're Keeping Simple
- **No tool system**: We're chat-focused, not tool-heavy
- **No JSON agents**: Our agents are provider-based, not task-based
- **Simpler config**: We don't need as many directories as code-puppy

### What We're Enhancing
- **Better UX**: Cleaner commands, better help
- **Better defaults**: Smarter defaults with easy customization
- **Better error messages**: More helpful error handling

### What We're Borrowing
- **Proven patterns**: Command registry, factory pattern, session management
- **Best practices**: XDG compliance, proper config management
- **Architecture**: Separation of concerns, extensibility

## 📝 Notes

### Differences from code-puppy
- **Scope**: code-puppy is a full IDE replacement; we're a focused CLI tool
- **Agents**: code-puppy has task-oriented agents; we have provider-oriented agents
- **Tools**: code-puppy is tool-heavy; we're chat-focused
- **Complexity**: code-puppy is more complex; we aim to stay simpler

### What Makes Our Approach Better
- **Simplicity**: Easier to understand and maintain
- **Focus**: Single purpose (LLM CLI) vs multi-purpose (code generation)
- **Lightweight**: Fewer dependencies, faster startup
- **Flexibility**: Easy to add new providers

## 🔗 References

- [code-puppy GitHub](https://github.com/mpfaffenberger/code_puppy)
- [code-puppy Agents Documentation](https://github.com/mpfaffenberger/code_puppy/blob/main/AGENTS.md)
- [CODE_PUPPY_INSPIRATION.md](./CODE_PUPPY_INSPIRATION.md) - Detailed feature analysis

