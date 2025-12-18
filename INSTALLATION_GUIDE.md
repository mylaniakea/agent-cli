# Agent CLI - Installation & Usage Guide

## Installation

The package is installed in **editable/development mode**, which means code changes take effect immediately without reinstalling.

```bash
# Install/reinstall the package
uv pip install -e .
```

## Available Commands

### 1. Using `agent-cli` Command

After installation, the `agent-cli` command is available in your virtual environment:

```bash
# Activate virtual environment first
source .venv/bin/activate

# Now use the command
agent-cli --version
agent-cli --help
agent-cli chat
agent-cli list-models
agent-cli config
agent-cli mcp list
agent-cli setup ollama

# Deactivate when done
deactivate
```

### 2. Using Direct Path (No activation)

```bash
# Use full path to command
.venv/bin/agent-cli --help
.venv/bin/agent-cli chat
```

### 3. Using Convenience Wrapper (Simplest!)

We've created an `./agent` wrapper script for you:

```bash
# Just use ./agent directly
./agent --version
./agent chat
./agent list-models
./agent --help
```

This is the **easiest option** - no activation needed, always uses latest code!

### 4. Using Development Script

The original `./dev.sh` script still works:

```bash
./dev.sh              # Starts interactive chat
./dev.sh --help       # Show help
./dev.sh --version    # Show version
```

## Usage Examples

### Interactive Chat (Default)
```bash
# Any of these work:
./agent chat
agent-cli chat                    # (after activating venv)
.venv/bin/agent-cli chat          # (no activation)
```

### Non-Interactive (Single Prompt)
```bash
./agent chat --provider ollama --model llama2 --non-interactive "What is Python?"
```

### List Available Models
```bash
./agent list-models
./agent list-models --provider ollama
./agent list-models --detailed
```

### Show Configuration
```bash
./agent config
```

### Setup a Provider
```bash
./agent setup openai
./agent setup anthropic
./agent setup google
```

### MCP Server Management
```bash
./agent mcp list
./agent mcp add my-server "/path/to/command" arg1 arg2
./agent mcp show my-server
./agent mcp remove my-server
```

## Interactive Mode Commands

When in interactive chat mode, you can use slash commands:

```bash
/help              # Show all commands
/model llama2      # Switch model
/provider openai   # Switch provider
/stream            # Toggle streaming
/clear             # Clear history
/history           # Show conversation history
/compress          # Compress history into summary
/beads status      # Check Beads CLI status
/keepalive 10m     # Set Ollama keep-alive
/theme dracula     # Change theme
/config            # Show settings
/export json       # Export conversation
exit               # Exit interactive mode
```

## File References

You can include file contents in your prompts using the `@` syntax:

```bash
# In interactive mode
You: @main.py can you explain this code?
You: @"file with spaces.txt" summarize this

# In non-interactive mode
./agent chat "Review this code: @main.py"
```

## Development Workflow

### Making Code Changes

1. Edit code in `agent_cli/`
2. Changes take effect immediately (editable install)
3. Just run `./agent` or `agent-cli` to test

### No Reinstall Needed!

Because the package is installed in editable mode (`pip install -e .`), your code changes are reflected immediately. You only need to reinstall if you:
- Change dependencies in `pyproject.toml`
- Change entry points or package structure
- Add/remove Python files

### Adding New Dependencies

```bash
# 1. Add to pyproject.toml [project.dependencies]
# 2. Reinstall
uv pip install -e .
```

## System-Wide Installation (Optional)

If you want `agent-cli` available system-wide (not recommended for development):

```bash
# Install with pipx (isolated, system-wide)
pipx install .

# Or install globally (not recommended)
pip install .
```

## Uninstallation

```bash
# From virtual environment
uv pip uninstall agent-cli

# If installed with pipx
pipx uninstall agent-cli
```

## Troubleshooting

### Command Not Found

**Problem**: `agent-cli: command not found`

**Solutions**:
1. Activate virtual environment first: `source .venv/bin/activate`
2. Use full path: `.venv/bin/agent-cli`
3. Use convenience wrapper: `./agent`

### Old Version Showing

**Problem**: `agent-cli --version` shows old version

**Solution**: Reinstall in editable mode
```bash
uv pip install -e .
```

### Import Errors

**Problem**: Module not found errors

**Solution**: Make sure you're in the project directory and venv is activated
```bash
cd /path/to/agent-cli
source .venv/bin/activate
```

## Quick Reference

| Method | Command | Pros | Cons |
|--------|---------|------|------|
| **Wrapper** | `./agent` | Simplest, no activation | Only works in project dir |
| **Direct Path** | `.venv/bin/agent-cli` | No activation needed | Longer to type |
| **Activated** | `agent-cli` | Short command | Requires activation |
| **Dev Script** | `./dev.sh` | Clears cache | Limited to chat command |

## Recommended Setup

For daily development, we recommend:

1. **Use the `./agent` wrapper** for quick commands
2. **Activate venv** for longer sessions:
   ```bash
   source .venv/bin/activate
   agent-cli chat  # Now you can use the short command
   ```
3. **Add to PATH** (optional) for system-wide access:
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export PATH="$PATH:/path/to/agent-cli/.venv/bin"
   ```

## Next Steps

1. Try the interactive mode: `./agent chat`
2. Explore slash commands: Type `/help` in interactive mode
3. Set up your preferred provider: `./agent setup ollama`
4. Read the full documentation: See `CLAUDE.md` and `README.md`

Happy coding! 🚀
