"""Interactive command handlers for agent-cli.

Commands are registered using the @register_command decorator from command_registry.
"""
import click
from typing import Dict, Optional
from agent_cli.command_registry import register_command


# Context keys for command handlers
CONTEXT_KEY_AGENT = "agent"
CONTEXT_KEY_PROVIDER = "provider"
CONTEXT_KEY_MODEL = "model"
CONTEXT_KEY_STREAM = "stream"
CONTEXT_KEY_HISTORY = "history"
CONTEXT_KEY_CONFIG = "config"


@register_command(
    name="help",
    description="Show available commands or detailed help for a command",
    usage="/help [command]",
    aliases=["h", "?"],
    category="core",
    detailed_help="Show all available commands or detailed help for a specific command.\n"
                  "Examples:\n"
                  "  /help          - Show all commands\n"
                  "  /help model    - Show detailed help for /model command"
)
def handle_help(command: str, context: Dict) -> bool:
    """Handle /help command."""
    from agent_cli.command_registry import generate_help_text
    
    # Remove leading /help and split
    parts = command.split(None, 1)
    if len(parts) > 1:
        # Show detailed help for specific command
        cmd_name = parts[1].lower()
        help_text = generate_help_text(command=cmd_name)
    else:
        # Show all commands
        help_text = generate_help_text()
    
    click.echo(help_text)
    click.echo("File References:")
    click.echo("  Use @filename to include file contents in your prompt")
    click.echo("  Example: @config.py or @\"file with spaces.txt\"")
    click.echo()
    return True


@register_command(
    name="model",
    description="Switch to a different model or show current model",
    usage="/model [name]",
    aliases=["m"],
    category="config",
    detailed_help="Switch to a different model or show the current model.\n"
                  "Examples:\n"
                  "  /model          - Show current model\n"
                  "  /model mistral  - Switch to mistral model"
)
def handle_model(command: str, context: Dict) -> bool:
    """Handle /model command."""
    from agent_cli.agents import AgentFactory
    
    parts = command.split(None, 1)
    config = context.get(CONTEXT_KEY_CONFIG)
    current_provider = context.get(CONTEXT_KEY_PROVIDER, "")
    current_model = context.get(CONTEXT_KEY_MODEL, "")
    
    if not config:
        click.echo("Error: Configuration not available.", err=True)
        return True
    
    if len(parts) > 1:
        # Switch model
        new_model = parts[1]
        try:
            # Try to create agent with new model to validate
            test_agent = AgentFactory.create(current_provider, new_model, config)
            context[CONTEXT_KEY_MODEL] = new_model
            context[CONTEXT_KEY_AGENT] = test_agent
            click.echo(f"Switched to model: {new_model}\n")
        except Exception as e:
            click.echo(f"Error switching model: {e}\n", err=True)
    else:
        # Show current model
        click.echo(f"Current model: {current_model}\n")
    
    return True


@register_command(
    name="provider",
    description="Switch to a different provider or show current provider",
    usage="/provider [name]",
    aliases=["p"],
    category="config",
    detailed_help="Switch to a different provider or show the current provider.\n"
                  "Available providers: ollama, openai, anthropic, google\n"
                  "Examples:\n"
                  "  /provider         - Show current provider\n"
                  "  /provider openai  - Switch to OpenAI provider"
)
def handle_provider(command: str, context: Dict) -> bool:
    """Handle /provider command."""
    from agent_cli.agents import AgentFactory
    
    parts = command.split(None, 1)
    config = context.get(CONTEXT_KEY_CONFIG)
    current_provider = context.get(CONTEXT_KEY_PROVIDER, "")
    current_model = context.get(CONTEXT_KEY_MODEL, "")
    
    if not config:
        click.echo("Error: Configuration not available.", err=True)
        return True
    
    if len(parts) > 1:
        new_provider = parts[1].lower()
        if new_provider in ["ollama", "openai", "anthropic", "google"]:
            try:
                # Try to create agent with new provider to validate
                test_agent = AgentFactory.create(new_provider, current_model, config)
                context[CONTEXT_KEY_PROVIDER] = new_provider
                context[CONTEXT_KEY_AGENT] = test_agent
                click.echo(f"Switched to provider: {new_provider}\n")
            except Exception as e:
                click.echo(f"Error switching provider: {e}\n", err=True)
        else:
            click.echo(f"Invalid provider. Choose from: ollama, openai, anthropic, google\n", err=True)
    else:
        # Show current provider
        click.echo(f"Current provider: {current_provider}\n")
    
    return True


@register_command(
    name="stream",
    description="Toggle streaming mode on/off",
    usage="/stream",
    aliases=["s"],
    category="config",
    detailed_help="Toggle streaming mode on or off.\n"
                  "When enabled, responses are streamed token by token.\n"
                  "When disabled, responses are returned all at once."
)
def handle_stream(command: str, context: Dict) -> bool:
    """Handle /stream command."""
    current_stream = context.get(CONTEXT_KEY_STREAM, False)
    context[CONTEXT_KEY_STREAM] = not current_stream
    click.echo(f"Streaming mode: {'enabled' if context[CONTEXT_KEY_STREAM] else 'disabled'}\n")
    return True


@register_command(
    name="clear",
    description="Clear conversation history",
    usage="/clear",
    aliases=["c"],
    category="session",
    detailed_help="Clear the conversation history for the current session.\n"
                  "This removes all previous messages from context."
)
def handle_clear(command: str, context: Dict) -> bool:
    """Handle /clear command."""
    history = context.get(CONTEXT_KEY_HISTORY, [])
    if history:
        history.clear()
        click.echo("Conversation history cleared.\n")
    else:
        click.echo("No conversation history to clear.\n")
    return True


@register_command(
    name="history",
    description="Show recent conversation history",
    usage="/history [compact]",
    aliases=["hist"],
    category="session",
    detailed_help="Show the recent conversation history.\n"
                  "Displays the last 10 messages in the conversation.\n"
                  "Use '/history compact' to manually compact the history."
)
def handle_history(command: str, context: Dict) -> bool:
    """Handle /history command."""
    from agent_cli.history_manager import format_history_summary, compact_history
    
    history = context.get(CONTEXT_KEY_HISTORY, [])
    
    # Check for compact subcommand
    parts = command.split(None, 1)
    if len(parts) > 1 and parts[1].lower() == "compact":
        if history:
            config = context.get(CONTEXT_KEY_CONFIG)
            strategy = config.get_value("HISTORY_COMPACTION_STRATEGY", "recent") if config else "recent"
            compacted = compact_history(history, strategy)
            context[CONTEXT_KEY_HISTORY] = compacted
            click.echo(f"History compacted: {len(history)} → {len(compacted)} messages\n")
        else:
            click.echo("No history to compact.\n")
        return True
    
    if history:
        summary = format_history_summary(history, max_lines=10)
        click.echo(f"\n{summary}\n")
    else:
        click.echo("No conversation history.\n")
    return True


@register_command(
    name="config",
    description="Show current configuration",
    usage="/config",
    aliases=["cfg"],
    category="config",
    detailed_help="Show the current configuration including:\n"
                  "- Current provider and model\n"
                  "- Streaming mode status\n"
                  "- API key status\n"
                  "- Ollama URL"
)
def handle_config(command: str, context: Dict) -> bool:
    """Handle /config command."""
    config = context.get(CONTEXT_KEY_CONFIG)
    current_provider = context.get(CONTEXT_KEY_PROVIDER, "")
    current_model = context.get(CONTEXT_KEY_MODEL, "")
    current_stream = context.get(CONTEXT_KEY_STREAM, False)
    
    if not config:
        click.echo("Error: Configuration not available.", err=True)
        return True
    
    click.echo("\nCurrent Configuration:")
    click.echo(f"  Provider: {current_provider}")
    click.echo(f"  Model: {current_model}")
    click.echo(f"  Streaming: {current_stream}")
    click.echo(f"  Ollama URL: {config.ollama_base_url}")
    click.echo(f"  OpenAI API Key: {'Set' if config.openai_api_key else 'Not set'}")
    click.echo(f"  Anthropic API Key: {'Set' if config.anthropic_api_key else 'Not set'}")
    click.echo(f"  Google API Key: {'Set' if config.google_api_key else 'Not set'}\n")
    return True


@register_command(
    name="mcp",
    description="Show MCP server management information",
    usage="/mcp",
    category="config",
    detailed_help="Show information about MCP server management.\n"
                  "Use 'agent-cli mcp' commands to manage MCP servers."
)
def handle_mcp(command: str, context: Dict) -> bool:
    """Handle /mcp command."""
    click.echo("\nMCP Server Management:")
    click.echo("  Use 'agent-cli mcp' command to manage MCP servers")
    click.echo("  Commands:")
    click.echo("    agent-cli mcp list          - List configured servers")
    click.echo("    agent-cli mcp add <name>    - Add a server")
    click.echo("    agent-cli mcp remove <name> - Remove a server\n")
    return True


@register_command(
    name="session",
    description="Show or manage session state",
    usage="/session [new|clear|list]",
    aliases=["sess"],
    category="session",
    detailed_help="Manage terminal session state.\n"
                  "Each terminal remembers its last provider and model.\n"
                  "Commands:\n"
                  "  /session        - Show current session info\n"
                  "  /session new   - Create a new session (clear state)\n"
                  "  /session clear - Clear current session state\n"
                  "  /session list  - List all active sessions"
)
def handle_session(command: str, context: Dict) -> bool:
    """Handle /session command."""
    from agent_cli.session_manager import (
        get_session_state,
        create_new_session,
        clear_session_state,
        list_all_sessions,
        get_terminal_session_id,
    )
    
    parts = command.split(None, 1)
    subcommand = parts[1].lower() if len(parts) > 1 else None
    
    if subcommand == "new":
        session_id = create_new_session()
        click.echo(f"Created new session: {session_id}\n")
    elif subcommand == "clear":
        clear_session_state()
        click.echo("Session state cleared.\n")
    elif subcommand == "list":
        sessions = list_all_sessions()
        if sessions:
            click.echo(f"\nActive Sessions ({len(sessions)}):\n")
            for sid, state in sessions.items():
                click.echo(f"  {sid}:")
                if state:
                    click.echo(f"    Provider: {state.get('provider', 'N/A')}")
                    click.echo(f"    Model: {state.get('model', 'N/A')}")
                else:
                    click.echo("    (empty)")
                click.echo()
        else:
            click.echo("No active sessions.\n")
    else:
        # Show current session info
        session_id = get_terminal_session_id()
        state = get_session_state()
        click.echo(f"\nCurrent Session: {session_id}")
        if state:
            click.echo(f"  Provider: {state.get('provider', 'N/A')}")
            click.echo(f"  Model: {state.get('model', 'N/A')}")
            click.echo(f"  Streaming: {state.get('stream', False)}")
        else:
            click.echo("  (no saved state)")
        click.echo()
    
    return True


@register_command(
    name="set",
    description="Set a configuration value",
    usage="/set <key>=<value>",
    aliases=[],
    category="config",
    detailed_help="Set a configuration value in the config file.\n"
                  "The value will be saved to ~/.agent-cli/config.ini\n"
                  "Examples:\n"
                  "  /set OLLAMA_BASE_URL=http://192.168.1.100:11434\n"
                  "  /set DEFAULT_OLLAMA_MODEL=mistral\n"
                  "\n"
                  "Note: API keys should be set via environment variables for security.\n"
                  "Config file values are overridden by environment variables."
)
def handle_set(command: str, context: Dict) -> bool:
    """Handle /set command."""
    config = context.get(CONTEXT_KEY_CONFIG)
    if not config:
        click.echo("Error: Configuration not available.", err=True)
        return True
    
    # Parse command: /set KEY=value
    parts = command.split(None, 1)
    if len(parts) < 2:
        click.echo("Usage: /set <key>=<value>", err=True)
        click.echo("Example: /set OLLAMA_BASE_URL=http://192.168.1.100:11434", err=True)
        return True
    
    # Parse key=value
    assignment = parts[1]
    if "=" not in assignment:
        click.echo("Error: Invalid format. Use KEY=value", err=True)
        click.echo("Example: /set OLLAMA_BASE_URL=http://192.168.1.100:11434", err=True)
        return True
    
    key, value = assignment.split("=", 1)
    key = key.strip()
    value = value.strip()
    
    # Warn about API keys
    if "API_KEY" in key.upper():
        click.echo("Warning: API keys should be set via environment variables for security.", err=True)
        response = click.prompt("Continue anyway? (y/N)", default="N", show_default=False)
        if response.lower() != "y":
            click.echo("Cancelled.")
            return True
    
    try:
        config.set_value(key, value)
        click.echo(f"Set {key} = {value}")
        click.echo("Note: This value is saved to config.ini and will persist.")
        click.echo("Environment variables take precedence over config file values.\n")
    except Exception as e:
        click.echo(f"Error setting configuration: {e}\n", err=True)
    
    return True

