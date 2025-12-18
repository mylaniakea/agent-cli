# Command Reference

Complete reference for all agent-cli commands.

## Main Commands

### `agent-cli chat`

Chat with an LLM agent.

**Usage:**
```bash
agent-cli chat [OPTIONS] [PROMPT]
```

**Options:**
- `-p, --provider [ollama|openai|anthropic|google]` - Provider to use (optional in interactive mode)
- `-m, --model TEXT` - Model name (optional in interactive mode)
- `-i, --interactive` - Run in interactive mode
- `-s, --stream` - Stream responses token by token

**Examples:**
```bash
# Simple query
agent-cli chat --provider ollama --model llama2 "What is Python?"

# Interactive mode
agent-cli chat --provider ollama --model llama2 --interactive

# Interactive mode (uses last session)
agent-cli chat --interactive

# Streaming
agent-cli chat --provider openai --model gpt-4 --stream "Write a story"
```

### `agent-cli list-models`

List available models for each provider.

**Usage:**
```bash
agent-cli list-models [OPTIONS]
```

**Options:**
- `-p, --provider [ollama|openai|anthropic|google]` - Filter by provider
- `-d, --detailed` - Show detailed model information

**Examples:**
```bash
# List all models
agent-cli list-models

# List with details
agent-cli list-models --detailed

# Filter by provider
agent-cli list-models --provider openai --detailed
```

### `agent-cli config`

Show current configuration.

**Usage:**
```bash
agent-cli config
```

### `agent-cli mcp`

Manage MCP (Model Context Protocol) servers.

**Subcommands:**
- `list` - List configured servers
- `add` - Add a server
- `remove` - Remove a server
- `show` - Show server details

**Examples:**
```bash
# List servers
agent-cli mcp list
agent-cli mcp list --detailed

# Add server
agent-cli mcp add filesystem npx -y @modelcontextprotocol/server-filesystem /path

# Show server details
agent-cli mcp show filesystem

# Remove server
agent-cli mcp remove filesystem
agent-cli mcp remove filesystem --force
```

## Interactive Commands

Available in interactive mode (when using `--interactive`):

### `/help` or `/h` or `/?`

Show available commands or detailed help for a command.

**Usage:**
```
/help
/help model
```

### `/model` or `/m`

Switch to a different model or show current model.

**Usage:**
```
/model
/model mistral
```

### `/provider` or `/p`

Switch to a different provider or show current provider.

**Usage:**
```
/provider
/provider openai
```

### `/stream` or `/s`

Toggle streaming mode on/off.

**Usage:**
```
/stream
```

### `/clear` or `/c`

Clear conversation history.

**Usage:**
```
/clear
```

### `/history` or `/hist`

Show recent conversation history.

**Usage:**
```
/history
/history compact
```

### `/config` or `/cfg`

Show current configuration.

**Usage:**
```
/config
```

### `/set`

Set a configuration value.

**Usage:**
```
/set OLLAMA_BASE_URL=http://192.168.1.100:11434
/set DEFAULT_OLLAMA_MODEL=mistral
```

### `/session` or `/sess`

Show or manage session state.

**Usage:**
```
/session
/session new
/session clear
/session list
```

### `/mcp`

Show MCP server management information.

**Usage:**
```
/mcp
```

### `/bead` - Manage Personality Beads

Manage personality beads for the current session.

**Usage:**
```bash
/bead list              # List available beads
/bead add <name>        # Add a bead to the active chain
/bead remove <name>     # Remove a bead from the chain
/bead clear             # Clear all active beads
/bead show              # Show current active beads and composed prompt
```

**Examples:**
```bash
/bead add helpful
/bead add python-expert
/bead add concise
```

### `/context` - Manage Project Context

Manage project context files and usage.

**Usage:**
```bash
/context [status]       # Show context summary (default)
/context usage          # Show context window usage and token count
/context update         # Update context from git history
/context view           # View all context content
/context add <note>     # Add a note to context
```

## File References

Include file contents in prompts using `@filename` syntax:

```bash
# In interactive mode
You: @config.py explain this file

# In command line
agent-cli --provider ollama --model llama2 "@README.md summarize this"

# Files with spaces
You: @"my file.txt" analyze this
```

## Exit Commands

In interactive mode:
- `exit` - Exit interactive mode
- `quit` - Exit interactive mode
- `Ctrl+C` - Exit interactive mode

