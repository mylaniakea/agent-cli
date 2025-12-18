# Onboarding Improvements & Fallback Provider

## Overview

The onboarding experience has been completely redesigned with:
1. **Keyboard + Spacebar Selection** - Beautiful multi-select UI for provider configuration
2. **Fallback Provider Support** - Automatic fallback when primary provider fails
3. **Consistent UI Components** - Reusable selection components throughout the app

---

## 1. Keyboard + Spacebar Multi-Select

### What Changed

**Before:** Multiple yes/no prompts (one per provider)
```
Do you want to configure OpenAI? (y/n)
Do you want to configure Anthropic? (y/n)
Do you want to configure Google? (y/n)
Do you want to configure Ollama? (y/n)
```

**After:** Interactive checkbox selection
```
Select providers to configure:

[*] 🤖 OpenAI (GPT-4, o1)
[ ] 🧠 Anthropic (Claude)
[*] ✨ Google (Gemini)
[ ] 🦙 Ollama (Local)

Use ↑/↓ to navigate, SPACE to select, ENTER when done
```

### How It Works

1. **Arrow Keys (↑/↓)** - Navigate between options
2. **Spacebar** - Toggle selection (check/uncheck)
3. **Enter** - Confirm selection and continue
4. **Esc / Ctrl+C** - Cancel

### Features

- Visual checkbox `[*]` / `[ ]` indicators
- Current selection highlighted
- Icons for each provider
- Intuitive keyboard navigation
- Multiple selections allowed

---

## 2. Fallback Provider Configuration

### What Is It?

A **fallback provider** is a backup AI provider that automatically activates when your primary provider fails. This ensures:
- **Zero downtime** - Seamless switching to backup
- **Reliability** - Always have a working provider
- **Flexibility** - Mix local and cloud providers

### When Does It Activate?

The fallback provider activates automatically when:
- Primary provider API is down
- API key is invalid or expired
- Network connectivity issues
- Rate limits exceeded
- Model unavailable

### Onboarding Flow

After configuring multiple providers, you'll see:

#### Step 1: Select Primary Provider
```
Select your PRIMARY provider:

(*) 🤖 OpenAI
( ) 🧠 Anthropic
( ) 🦙 Ollama

This will be your default provider. Use ↑/↓, then ENTER
```

#### Step 2: Select Fallback Provider (Optional)
```
Select a FALLBACK provider (optional):

(*) ⊘ No fallback (skip)
( ) 🧠 Anthropic
( ) 🦙 Ollama

Used when primary provider fails. Use ↑/↓, then ENTER
```

#### Step 3: Configuration Summary
```
✓ Primary: 🤖 OpenAI
✓ Fallback: 🦙 Ollama
```

### Configuration Storage

Settings are saved to `~/.agent-cli/config.ini`:
```ini
[agent-cli]
PRIMARY_PROVIDER = openai
FALLBACK_PROVIDER = ollama
```

---

## 3. Automatic Failover

### How It Works

When you send a message:

1. **Try Primary Provider**
   ```
   Sending to OpenAI (gpt-4)...
   ```

2. **If Primary Fails**
   ```
   ⚠️  Primary provider 'openai' failed: Connection timeout
   ℹ️  Attempting fallback to 'ollama'...
   ✓ Using fallback provider: ollama with model llama3.3
   ```

3. **Response from Fallback**
   ```
   🦙 llama3.3 | You ➜ [your message continues seamlessly]
   ```

### Fallback Logic

```python
def create_agent_with_fallback(provider, model, config):
    try:
        # Try primary provider
        agent = AgentFactory.create(provider, model, config)
        return agent
    except Exception as primary_error:
        # Check for fallback
        if config.fallback_provider:
            # Attempt fallback
            fallback_model = get_default_model(config.fallback_provider)
            agent = AgentFactory.create(config.fallback_provider, fallback_model, config)
            return agent
        else:
            # No fallback, raise original error
            raise primary_error
```

---

## 4. Reusable UI Components

### MultiSelect Component

Used for selecting multiple items with checkboxes.

**Usage:**
```python
from agent_cli.interactive_select import MultiSelect

options = [
    {"key": "option1", "label": "First Option", "icon": "🎯"},
    {"key": "option2", "label": "Second Option", "icon": "🔥"},
    {"key": "option3", "label": "Third Option", "icon": "⭐"},
]

multi_select = MultiSelect(
    options=options,
    title="Select multiple options:",
    console=console,
)

selected_keys = multi_select.show()
# Returns: ["option1", "option3"] if user selected first and third
```

### SingleSelect Component

Used for selecting a single item (radio buttons).

**Usage:**
```python
from agent_cli.interactive_select import SingleSelect

options = [
    {"key": "option1", "label": "First Option", "icon": "🎯"},
    {"key": "option2", "label": "Second Option", "icon": "🔥"},
    {"key": "option3", "label": "Third Option", "icon": "⭐"},
]

single_select = SingleSelect(
    options=options,
    title="Select one option:",
    default_index=0,  # Pre-select first option
    console=console,
)

selected_key = single_select.show()
# Returns: "option2" if user selected second option
```

---

## 5. Configuration Management

### View Current Configuration

```bash
./agent chat
# Inside chat:
/config
```

Shows:
```
Configuration:
  PRIMARY_PROVIDER: openai
  FALLBACK_PROVIDER: ollama
  DEFAULT_OPENAI_MODEL: gpt-4
  DEFAULT_OLLAMA_MODEL: llama3.3
  ...
```

### Change Providers

```bash
# Inside chat:
/provider ollama              # Switch to Ollama
/provider openai              # Switch to OpenAI
```

### Set Fallback Provider

```bash
# Inside chat:
/set FALLBACK_PROVIDER anthropic
```

Or edit `~/.agent-cli/config.ini` directly:
```ini
[agent-cli]
FALLBACK_PROVIDER = anthropic
```

### Disable Fallback

```bash
# Inside chat:
/set FALLBACK_PROVIDER ""
```

---

## 6. Recommended Configurations

### Configuration 1: Cloud Primary + Local Fallback

**Best for:** Development work with cost concerns

```
PRIMARY: OpenAI (gpt-4o-mini)
FALLBACK: Ollama (llama3.3)
```

**Benefits:**
- Fast, high-quality responses from OpenAI
- Free local fallback if API goes down
- No interruption to workflow

### Configuration 2: Local Primary + Cloud Fallback

**Best for:** Privacy-focused or offline work

```
PRIMARY: Ollama (llama3.3)
FALLBACK: Anthropic (claude-3-5-haiku)
```

**Benefits:**
- Private, local-first processing
- Cloud backup for complex queries
- No data leaves your machine (normally)

### Configuration 3: Multi-Cloud

**Best for:** Production applications

```
PRIMARY: Anthropic (claude-3-5-sonnet)
FALLBACK: OpenAI (gpt-4)
```

**Benefits:**
- Maximum reliability
- Diverse model capabilities
- Geographic redundancy

### Configuration 4: No Fallback

**Best for:** Single provider setups

```
PRIMARY: OpenAI (gpt-4)
FALLBACK: (none)
```

**Benefits:**
- Simpler configuration
- Predictable behavior
- Clear error messages when provider fails

---

## 7. Testing the Features

### Test Multi-Select Onboarding

```bash
# Remove existing config to trigger onboarding
rm ~/.agent-cli/config.ini
rm .env

# Start the app
./agent chat

# You'll see the new multi-select interface
# Try:
# - Arrow keys to navigate
# - Spacebar to toggle selections
# - Select multiple providers
# - Press Enter to confirm
```

### Test Fallback Provider

```bash
# Configure with fallback
./agent chat

# Simulate primary provider failure by using invalid API key
export OPENAI_API_KEY="invalid-key-test"

# Try sending a message
# You should see:
# 1. "Primary provider failed" warning
# 2. "Attempting fallback" message
# 3. Successful response from fallback provider
```

### Test Selection Components

```python
# Test MultiSelect
from agent_cli.interactive_select import MultiSelect
from rich.console import Console

console = Console()
options = [
    {"key": "opt1", "label": "Option 1", "icon": "🎯"},
    {"key": "opt2", "label": "Option 2", "icon": "🔥"},
]

multi = MultiSelect(options, title="Test Multi-Select", console=console)
result = multi.show()
print(f"Selected: {result}")
```

---

## 8. Files Modified

### New Files
- **agent_cli/interactive_select.py** - MultiSelect and SingleSelect components

### Modified Files
- **agent_cli/interactive_onboarding.py** - New multi-select UI and fallback selection
- **agent_cli/config.py** - Added PRIMARY_PROVIDER and FALLBACK_PROVIDER
- **agent_cli/cli.py** - Added create_agent_with_fallback() function

---

## 9. Benefits Summary

### User Experience
- ✅ Faster onboarding (single multi-select vs multiple y/n prompts)
- ✅ Visual feedback with checkboxes and icons
- ✅ Intuitive keyboard navigation
- ✅ Consistent UI throughout the app

### Reliability
- ✅ Zero-downtime provider switching
- ✅ Automatic failover
- ✅ Graceful error handling
- ✅ Always have a working provider

### Flexibility
- ✅ Mix local and cloud providers
- ✅ Configure per-environment
- ✅ Easy to enable/disable fallback
- ✅ Reusable components for future features

---

## 10. Future Enhancements

Potential improvements:
- **Multiple Fallback Levels** - Chain of fallbacks (primary → fallback1 → fallback2)
- **Smart Fallback Selection** - Auto-select based on query complexity
- **Provider Health Monitoring** - Pre-emptive switching before failure
- **Cost-Based Routing** - Route to cheapest available provider
- **Load Balancing** - Distribute requests across multiple providers
- **Provider-Specific Retries** - Retry with backoff before failing over

---

## 11. Troubleshooting

### Multi-Select Not Appearing

**Problem:** Onboarding shows old yes/no prompts

**Solution:** Update the code:
```bash
git pull  # Get latest changes
.venv/bin/pip install -e .  # Reinstall package
```

### Fallback Not Working

**Problem:** Primary fails but no fallback attempt

**Check:**
1. Is fallback configured?
   ```bash
   cat ~/.agent-cli/config.ini | grep FALLBACK
   ```

2. Is fallback provider properly configured?
   ```bash
   # Check if API keys exist for fallback provider
   env | grep -E "OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_API_KEY"
   ```

3. Try setting fallback explicitly:
   ```bash
   ./agent chat
   /set FALLBACK_PROVIDER ollama
   ```

### Selection UI Not Working

**Problem:** Arrow keys don't work, or display is garbled

**Solution:**
- Ensure you're in a proper TTY (not SSH without TTY)
- Try a different terminal emulator
- Check terminal size: `echo $COLUMNS $LINES`

---

## 12. Migration Guide

### From Old Onboarding

If you've already configured providers using the old system:

1. **Your existing config is preserved** - API keys and models unchanged
2. **Set primary provider** (optional):
   ```bash
   ./agent chat
   /set PRIMARY_PROVIDER openai
   ```

3. **Set fallback provider** (optional):
   ```bash
   /set FALLBACK_PROVIDER ollama
   ```

4. **Test fallback** by simulating failure:
   ```bash
   export OPENAI_API_KEY="invalid"
   ./agent chat
   # Send a message and watch fallback activate
   ```

---

**Enjoy the improved onboarding experience! 🎉**
