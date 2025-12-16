# Code Puppy Feature Analysis & Adoption Plan

Based on analysis of [code_puppy](https://github.com/mpfaffenberger/code_puppy), here are features we could borrow and adapt for agent-cli.

## 🎯 High Priority Features (Easy Wins)

### 1. **Command Registry System** ⭐⭐⭐
**What it is**: Decorator-based command registration system that auto-discovers commands and generates help.

**Why it's valuable**:
- Eliminates manual command lists
- Auto-generates help text
- Supports aliases and categories
- Makes adding new commands trivial

**Implementation**:
```python
@register_command(
    name="model",
    description="Switch to a different model",
    usage="/model <name>",
    aliases=["m"],
    category="config"
)
def handle_model(command: str) -> bool:
    # Command logic
    return True
```

**Adaptation for agent-cli**: Replace our manual command handling with a registry system. This would make our `/model`, `/provider`, etc. commands more maintainable.

### 2. **Better Configuration Management** ⭐⭐⭐
**What it is**: XDG-based config with proper directory structure and config file management.

**Why it's valuable**:
- Follows XDG Base Directory spec
- Better organization (config, data, cache, state)
- Config file validation and defaults
- Runtime config updates

**Current state**: We have basic `.env` support, but could be more robust.

**Adaptation**: 
- Add `~/.agent-cli/config.ini` for persistent settings
- Separate directories for config, data, cache
- Runtime config updates via `/set` command

### 3. **Session Management** ⭐⭐
**What it is**: Per-terminal-session agent/provider selection persistence.

**Why it's valuable**:
- Remembers your last used provider/model per terminal
- Better UX for multi-terminal workflows
- Session isolation

**Adaptation**: Store last used provider/model per terminal session ID (PPID-based).

## 🔧 Medium Priority Features (Valuable Additions)

### 4. **Model Factory Pattern** ⭐⭐
**What it is**: Centralized model creation with settings management, validation, and metadata.

**Why it's valuable**:
- Model-specific settings (max_tokens, temperature, etc.)
- Model metadata (context length, capabilities)
- Better error handling
- Support for model-specific features

**Current state**: We create models directly in agents. A factory would centralize this.

**Adaptation**: Create `ModelFactory` class that handles:
- Model validation
- Settings management
- Provider abstraction
- Model metadata (from JSON file)

### 5. **Enhanced MCP Integration** ⭐⭐
**What it is**: More sophisticated MCP server management with runtime integration.

**Why it's valuable**:
- Better MCP server lifecycle management
- Runtime tool discovery
- MCP tool integration into agent responses

**Current state**: We have basic MCP config storage, but no runtime integration.

**Adaptation**: 
- Add MCP server startup/shutdown
- Tool discovery from MCP servers
- Integrate MCP tools into agent responses

### 6. **Message History Management** ⭐⭐
**What it is**: Better conversation history handling with compaction, summarization, and limits.

**Why it's valuable**:
- Prevents context window overflow
- Smart history management
- Optional summarization for long conversations

**Current state**: We store history as simple list. Could be smarter.

**Adaptation**:
- Add history compaction strategies
- Configurable message limits
- Optional summarization agent for long histories

## 🚀 Lower Priority (Nice to Have)

### 7. **JSON Agent System** ⭐
**What it is**: Allow users to create custom agents via JSON files without Python knowledge.

**Why it's valuable**:
- User extensibility
- Easy agent sharing
- No Python required

**Consideration**: This might be overkill for agent-cli's simpler scope. Our agents are provider-based, not task-based like code_puppy.

### 8. **Tool System** ⭐
**What it is**: Agent-specific tool access control and tool registration.

**Why it's valuable**:
- Fine-grained control over agent capabilities
- Extensible tool system

**Consideration**: Our agents are simpler (just chat interfaces), so this might not be needed unless we add tool-calling capabilities.

## 📋 Implementation Recommendations

### Phase 1: Quick Wins (1-2 days)
1. **Command Registry System** - Replace manual command handling
2. **Better Config Management** - Add config file support alongside .env

### Phase 2: Enhancements (3-5 days)
3. **Session Management** - Remember last provider/model per terminal
4. **Model Factory** - Centralize model creation and settings

### Phase 3: Advanced (1-2 weeks)
5. **Enhanced MCP Integration** - Runtime MCP server management
6. **Message History Management** - Smart history handling

## 🎨 Architecture Patterns to Adopt

### 1. **Separation of Concerns**
- **Config**: Separate config management from business logic
- **Factory Pattern**: Use factories for model/agent creation
- **Registry Pattern**: Use registries for commands, agents, tools

### 2. **Extensibility**
- **Plugin System**: Make it easy to add new providers/agents
- **Discovery**: Auto-discover agents/commands/tools
- **Configuration**: Externalize configuration

### 3. **User Experience**
- **Session Persistence**: Remember user preferences
- **Smart Defaults**: Good defaults with easy customization
- **Help System**: Auto-generated, comprehensive help

## 🔍 Key Differences to Consider

**code_puppy** is:
- Task-oriented (code generation, review, QA, etc.)
- Tool-heavy (file operations, shell commands, etc.)
- Agent-centric (multiple specialized agents)

**agent-cli** is:
- Provider-oriented (Ollama, OpenAI, Anthropic, Google)
- Chat-focused (simple LLM interactions)
- Simpler scope (CLI tool, not full IDE)

**What to borrow**: Architecture patterns, config management, command system
**What to skip**: Tool system, JSON agents (unless we expand scope)

## 📚 References

- [code_puppy GitHub](https://github.com/mpfaffenberger/code_puppy)
- [code_puppy Agents Documentation](https://github.com/mpfaffenberger/code_puppy/blob/main/AGENTS.md)

