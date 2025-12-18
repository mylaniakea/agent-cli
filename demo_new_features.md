# Personality Beads v2.0 - New Features Demo

## What You Should See

### 1. Bead Pills in Prompt (Phase 3.1)
When you use an agent with personality beads, the prompt shows colored pills:

```
🦙 Matthew [helpful][python][concise] ➜
```

### 2. Interactive Menus (Phase 3.4 - Just Added!)

These beautiful menus appear when you use commands WITHOUT arguments:

#### Example 1: Browse Beads
```bash
/bead list
```
Shows an interactive menu:
```
Select bead category:

( ) 📦 All Beads
(*) 🎯 Core Personality
( ) 💼 Communication Style
( ) 🔧 Expertise Areas
( ) ⚙️ Response Adjustments
( ) 🎭 Behavioral Patterns

Use ↑/↓ to navigate, ENTER to select, ESC to cancel
```

#### Example 2: Create Agent with Beads
```bash
/agent create mycoder llama3
```
Shows choice menu:
```
Creating agent 'mycoder':

(*) 🎨 Compose from Personality Beads
( ) ✍️  Enter System Prompt Manually

Use ↑/↓ to navigate, ENTER to select
```

Then shows multi-select:
```
Select personality beads:

[*] 🎯 Helpful Assistant (base)
[ ] 🎯 Analytical Thinker (base)
[*] 🔧 Python Expert (domain)
[*] ⚙️ Concise Responses (modifier)

Use ↑/↓ to navigate, SPACE to select, ENTER when done
```

#### Example 3: Switch Agents
```bash
/agent use
```
Shows agent menu:
```
Select agent:

( ) 🔄 Default (No Agent)
(*) 🤖 mycoder (3 beads)

Use ↑/↓ to navigate, ENTER to select, ESC to cancel
```

## How to Test

1. **Start agent-cli in interactive mode:**
   ```bash
   agent-cli
   ```

2. **Try these commands (WITHOUT arguments to see menus):**
   ```bash
   /bead list           # Interactive category selector
   /bead show           # Interactive bead browser
   /agent create test llama3   # Interactive bead composer
   /agent use           # Interactive agent switcher
   ```

3. **Try with arguments (traditional CLI mode):**
   ```bash
   /bead list domain
   /bead show python-expert
   /agent create coder llama3 --beads helpful,python-expert,concise
   /agent use coder
   ```

4. **See the bead pills:**
   After creating and using an agent with beads, your prompt should show:
   ```
   🦙 Matthew [helpful][python][concise] ➜
   ```

## What "Simple Design Look" Might Mean

If you're seeing a basic terminal without:
- ❌ No colored bead pills in the prompt
- ❌ No interactive pop-up menus
- ❌ No checkbox selections
- ❌ No arrow key navigation

You might be:
1. Running in non-interactive mode (direct command execution)
2. Using a terminal that doesn't support the UI features
3. Not using the slash commands that trigger the menus

## Quick Test

Run this to verify everything is installed:
```bash
agent-cli --help
```

Then start interactive mode and try:
```bash
agent-cli
> /bead list
> /help
```

The `/bead list` command should show the interactive menu if everything is working!
