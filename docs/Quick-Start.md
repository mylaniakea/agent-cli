# Quick Start Guide

Get up and running with agent-cli in minutes!

## Basic Usage

### Simple Query

```bash
agent-cli --provider ollama --model llama2 "What is Python?"
```

### Interactive Mode

```bash
agent-cli --provider ollama --model llama2 --interactive
```

In interactive mode:
- Type your questions and press Enter
- Use `/help` to see available commands
- Type `exit` or `quit` to end

### Streaming Mode

See responses in real-time:

```bash
agent-cli --provider openai --model gpt-4 --stream "Write a story"
```

## Common Commands

### List Available Models

```bash
agent-cli list-models
```

### Show Configuration

```bash
agent-cli config
```

### Include Files in Prompts

```bash
# In interactive mode
You: @config.py explain this file

# Or in command line
agent-cli --provider ollama --model llama2 "@README.md summarize this"
```

## Interactive Commands

While in interactive mode, use these commands:

- `/help` - Show all commands
- `/model <name>` - Switch model
- `/provider <name>` - Switch provider
- `/stream` - Toggle streaming
- `/clear` - Clear history
- `/history` - Show conversation history
- `/config` - Show configuration
- `/session` - Show session info
- `/set KEY=value` - Set config value

## Examples

### Example 1: Code Explanation

```bash
agent-cli --provider openai --model gpt-4 "@app.py explain this code"
```

### Example 2: Long Conversation

```bash
agent-cli --provider anthropic --model claude-3-sonnet --interactive
You: What is machine learning?
You: Can you give me an example?
You: How does it relate to deep learning?
```

### Example 3: Remote Ollama

```bash
# Set remote Ollama URL
export OLLAMA_BASE_URL=http://192.168.1.100:11434

# Use it
agent-cli --provider ollama --model mistral "Hello"
```

## Next Steps

- Read [Basic Usage](Basic-Usage) for detailed examples
- Learn about [Configuration](Configuration)
- Explore [Advanced Features](Advanced-Features)

