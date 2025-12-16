# Configuration System Guide

## How It Works

The agent-cli configuration system supports multiple configuration sources with a clear priority order. This gives you flexibility in how you manage your settings.

## Configuration Priority (Highest to Lowest)

1. **Environment Variables** (highest priority)
2. **config.ini file** (`~/.agent-cli/config.ini`)
3. **.env file** (project root)
4. **Default values** (lowest priority)

### Example Priority Flow

Let's say you want to set `OLLAMA_BASE_URL`:

```bash
# 1. Environment variable (wins)
export OLLAMA_BASE_URL=http://remote:11434
agent-cli --provider ollama --model llama2 "test"
# Uses: http://remote:11434

# 2. If no env var, checks config.ini
# ~/.agent-cli/config.ini:
# [agent-cli]
# OLLAMA_BASE_URL=http://local:11434
agent-cli --provider ollama --model llama2 "test"
# Uses: http://local:11434

# 3. If no config.ini, checks .env
# .env file in project root:
# OLLAMA_BASE_URL=http://project:11434
agent-cli --provider ollama --model llama2 "test"
# Uses: http://project:11434

# 4. If nothing found, uses default
agent-cli --provider ollama --model llama2 "test"
# Uses: http://localhost:11434 (default)
```

## Configuration Sources

### 1. Environment Variables

Set in your shell session:

```bash
export OLLAMA_BASE_URL=http://192.168.1.100:11434
export OPENAI_API_KEY=sk-...
export DEFAULT_OLLAMA_MODEL=mistral
```

**Pros:**
- Highest priority (overrides everything)
- Good for temporary changes
- Secure for API keys (not stored in files)

**Cons:**
- Not persistent (lost when shell closes)
- Need to set each time

### 2. config.ini File

Located at `~/.agent-cli/config.ini` (or XDG_CONFIG_HOME/agent-cli/config.ini if XDG vars are set).

```ini
[agent-cli]
OLLAMA_BASE_URL=http://192.168.1.100:11434
DEFAULT_OLLAMA_MODEL=mistral
DEFAULT_OPENAI_MODEL=gpt-4
```

**How to create/edit:**
- Automatically created when you use `/set` command
- Or manually edit the file

**Pros:**
- Persistent across sessions
- Easy to edit
- Can be version controlled (if you exclude API keys)

**Cons:**
- Overridden by environment variables
- Less secure for API keys (stored in plain text)

### 3. .env File

Located in your project root (where you run agent-cli).

```bash
# .env
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_OLLAMA_MODEL=llama2
```

**Pros:**
- Project-specific settings
- Can be shared with team (via git, excluding API keys)
- Good for development

**Cons:**
- Only works when in project directory
- Overridden by environment variables and config.ini

### 4. Default Values

Built-in defaults if nothing else is set:

```python
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama2"
DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"
# etc.
```

## Using the `/set` Command

In interactive mode, you can set configuration values that persist:

```bash
agent-cli --provider ollama --model llama2 --interactive

You: /set OLLAMA_BASE_URL=http://192.168.1.100:11434
Set OLLAMA_BASE_URL = http://192.168.1.100:11434
Note: This value is saved to config.ini and will persist.

You: /set DEFAULT_OLLAMA_MODEL=mistral
Set DEFAULT_OLLAMA_MODEL = mistral
```

**What happens:**
1. Value is saved to `~/.agent-cli/config.ini`
2. Current session uses the new value immediately
3. Future sessions will use the saved value (unless overridden by env vars)

**Security Note:**
If you try to set an API key via `/set`, you'll get a warning:

```bash
You: /set OPENAI_API_KEY=sk-...
Warning: API keys should be set via environment variables for security.
Continue anyway? (y/N): N
Cancelled.
```

## Configuration Directories

### Default Location: `~/.agent-cli/`

```
~/.agent-cli/
├── config.ini          # Main configuration file
└── mcp_servers.json   # MCP server configurations
```

### XDG Base Directory Support

If you set XDG environment variables, agent-cli will use them:

```bash
export XDG_CONFIG_HOME=$HOME/.config
export XDG_DATA_HOME=$HOME/.local/share
export XDG_CACHE_HOME=$HOME/.cache
export XDG_STATE_HOME=$HOME/.local/state
```

Then files are stored in:
- Config: `$XDG_CONFIG_HOME/agent-cli/config.ini`
- Data: `$XDG_DATA_HOME/agent-cli/`
- Cache: `$XDG_CACHE_HOME/agent-cli/`
- State: `$XDG_STATE_HOME/agent-cli/`

If XDG vars are not set, everything goes to `~/.agent-cli/`.

## Real-World Examples

### Example 1: Remote Ollama Server

**Option A: Environment Variable (temporary)**
```bash
export OLLAMA_BASE_URL=http://192.168.1.100:11434
agent-cli --provider ollama --model llama2 "test"
```

**Option B: config.ini (persistent)**
```bash
# In interactive mode
You: /set OLLAMA_BASE_URL=http://192.168.1.100:11434

# Or edit ~/.agent-cli/config.ini directly
```

**Option C: .env file (project-specific)**
```bash
# Create .env in project root
echo "OLLAMA_BASE_URL=http://192.168.1.100:11434" > .env
```

### Example 2: API Keys

**Best Practice: Environment Variables**
```bash
# In ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GOOGLE_API_KEY=...

# Then reload shell
source ~/.bashrc
```

**Why?**
- More secure (not stored in files)
- Works across all projects
- Can be managed by secret managers

### Example 3: Default Models

**Set in config.ini (persistent)**
```bash
You: /set DEFAULT_OLLAMA_MODEL=mistral
You: /set DEFAULT_OPENAI_MODEL=gpt-4
```

These will be used when you don't specify `--model`.

## How the Code Works

### Configuration Loading Order

1. **Initialize Config class**
   ```python
   config = Config()
   ```

2. **Load .env file** (if exists in project root)
   ```python
   load_dotenv(env_path)  # Loads into os.environ
   ```

3. **Load config.ini** (if exists)
   ```python
   configparser.read(CONFIG_FILE)
   ```

4. **Get values with priority**
   ```python
   def _get_value(key, default):
       # 1. Check environment variable
       if os.getenv(key):
           return os.getenv(key)
       
       # 2. Check config.ini
       if key in config_ini:
           return config_ini[key]
       
       # 3. .env was loaded into os.environ, so already checked
       # 4. Return default
       return default
   ```

### Setting Values

When you use `/set`:

```python
config.set_value("OLLAMA_BASE_URL", "http://remote:11434")
```

This:
1. Updates the internal config object
2. Saves to `~/.agent-cli/config.ini`
3. Updates the instance attribute (`config.ollama_base_url`)
4. Value persists for future sessions

## Troubleshooting

### "My config isn't being used"

Check priority order:
1. Is there an environment variable set? (`echo $OLLAMA_BASE_URL`)
2. Does config.ini exist? (`cat ~/.agent-cli/config.ini`)
3. Is there a .env file? (`cat .env`)
4. What's the default? (check code or docs)

### "Changes aren't persisting"

- `/set` saves to config.ini, but env vars override it
- Check if you have an environment variable set
- Verify config.ini was written (`cat ~/.agent-cli/config.ini`)

### "Where is my config file?"

```bash
# Default location
ls ~/.agent-cli/config.ini

# Or if XDG_CONFIG_HOME is set
ls $XDG_CONFIG_HOME/agent-cli/config.ini
```

## Summary

- **Multiple sources**: env vars, config.ini, .env, defaults
- **Clear priority**: env > ini > .env > defaults
- **Persistent settings**: Use `/set` or edit config.ini
- **Temporary settings**: Use environment variables
- **Secure**: API keys should use environment variables
- **Flexible**: Choose the method that works best for your workflow

