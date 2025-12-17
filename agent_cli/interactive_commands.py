"""Interactive command handlers for agent-cli.

Commands are registered using the @register_command decorator from command_registry.
"""

from typing import Dict

from agent_cli.command_registry import register_command
from agent_cli.ui import ui

# Context keys for command handlers
CONTEXT_KEY_AGENT = "agent"
CONTEXT_KEY_PROVIDER = "provider"
CONTEXT_KEY_MODEL = "model"
CONTEXT_KEY_STREAM = "stream"
CONTEXT_KEY_HISTORY = "history"
CONTEXT_KEY_CONFIG = "config"
CONTEXT_KEY_SYSTEM_PROMPT = "system_prompt"


@register_command(
    name="help",
    description="Show available commands or detailed help for a command",
    usage="/help [command]",
    aliases=["h", "?"],
    category="core",
    detailed_help="Show all available commands or detailed help for a specific command.\n"
    "Examples:\n"
    "  /help          - Show all commands\n"
    "  /help model    - Show detailed help for /model command",
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

    # Check if generate_help_text returns plain text and we want to render it nicely?
    # Actually, generate_help_text likely returns a string. We can try to format it better or just print it.
    # For now, print nicely.
    ui.print_info(help_text)

    ui.print_info("File References:")
    ui.print_info("  Use @filename to include file contents in your prompt")
    ui.print_info('  Example: @config.py or @"file with spaces.txt"')
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
    "  /model mistral  - Switch to mistral model",
)
def handle_model(command: str, context: Dict) -> bool:
    """Handle /model command."""
    from agent_cli.agents import AgentFactory

    parts = command.split(None, 1)
    config = context.get(CONTEXT_KEY_CONFIG)
    current_provider = context.get(CONTEXT_KEY_PROVIDER, "")
    current_model = context.get(CONTEXT_KEY_MODEL, "")

    if not config:
        ui.print_error("Configuration not available.")
        return True

    if len(parts) > 1:
        # Switch model
        new_model = parts[1]
        try:
            # Try to create agent with new model to validate
            test_agent = AgentFactory.create(current_provider, new_model, config)
            context[CONTEXT_KEY_MODEL] = new_model
            context[CONTEXT_KEY_AGENT] = test_agent
            ui.print_success(f"Switched to model: {new_model}")
        except Exception as e:
            ui.print_error(f"Error switching model: {e}")
    else:
        # Show current model
        ui.print_info(f"Current model: {current_model}")

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
    "  /provider openai  - Switch to OpenAI provider",
)
def handle_provider(command: str, context: Dict) -> bool:
    """Handle /provider command."""
    from agent_cli.agents import AgentFactory

    parts = command.split(None, 1)
    config = context.get(CONTEXT_KEY_CONFIG)
    current_provider = context.get(CONTEXT_KEY_PROVIDER, "")
    current_model = context.get(CONTEXT_KEY_MODEL, "")

    if not config:
        ui.print_error("Configuration not available.")
        return True

    if len(parts) > 1:
        new_provider = parts[1].lower()
        if new_provider in ["ollama", "openai", "anthropic", "google"]:
            try:
                # Try to create agent with new provider to validate
                test_agent = AgentFactory.create(new_provider, current_model, config)
                context[CONTEXT_KEY_PROVIDER] = new_provider
                context[CONTEXT_KEY_AGENT] = test_agent
                ui.print_success(f"Switched to provider: {new_provider}")
            except Exception as e:
                ui.print_error(f"Error switching provider: {e}")
        else:
            ui.print_error("Invalid provider. Choose from: ollama, openai, anthropic, google")
    else:
        # Show current provider
        ui.print_info(f"Current provider: {current_provider}")

    return True


@register_command(
    name="stream",
    description="Toggle streaming mode on/off",
    usage="/stream",
    aliases=["s"],
    category="config",
    detailed_help="Toggle streaming mode on or off.\n"
    "When enabled, responses are streamed token by token.\n"
    "When disabled, responses are returned all at once.",
)
def handle_stream(command: str, context: Dict) -> bool:
    """Handle /stream command."""
    current_stream = context.get(CONTEXT_KEY_STREAM, False)
    context[CONTEXT_KEY_STREAM] = not current_stream
    ui.print_info(f"Streaming mode: {'enabled' if context[CONTEXT_KEY_STREAM] else 'disabled'}")
    return True


@register_command(
    name="clear",
    description="Clear conversation history",
    usage="/clear",
    aliases=["c"],
    category="session",
    detailed_help="Clear the conversation history for the current session.\n"
    "This removes all previous messages from context.",
)
def handle_clear(command: str, context: Dict) -> bool:
    """Handle /clear command."""
    history = context.get(CONTEXT_KEY_HISTORY, [])
    if history:
        history.clear()
        ui.print_success("Conversation history cleared.")
    else:
        ui.print_info("No conversation history to clear.")
    return True


@register_command(
    name="history",
    description="Show recent conversation history",
    usage="/history [compact]",
    aliases=["hist"],
    category="session",
    detailed_help="Show the recent conversation history.\n"
    "Displays the last 10 messages in the conversation.\n"
    "Use '/history compact' to manually compact the history.",
)
def handle_history(command: str, context: Dict) -> bool:
    """Handle /history command."""
    from agent_cli.history_manager import compact_history, format_history_summary

    history = context.get(CONTEXT_KEY_HISTORY, [])

    # Check for compact subcommand
    parts = command.split(None, 1)
    if len(parts) > 1 and parts[1].lower() == "compact":
        if history:
            config = context.get(CONTEXT_KEY_CONFIG)
            strategy = (
                config.get_value("HISTORY_COMPACTION_STRATEGY", "recent") if config else "recent"
            )
            compacted = compact_history(history, strategy)
            context[CONTEXT_KEY_HISTORY] = compacted
            ui.print_success(f"History compacted: {len(history)} → {len(compacted)} messages")
        else:
            ui.print_info("No history to compact.")
        return True

    if history:
        summary = format_history_summary(history, max_lines=10)
        ui.print_markdown(f"**Recent Conversation History:**\n\n```\n{summary}\n```")
    else:
        ui.print_info("No conversation history.")
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
    "- Ollama URL",
)
def handle_config(command: str, context: Dict) -> bool:
    """Handle /config command."""
    config = context.get(CONTEXT_KEY_CONFIG)
    current_provider = context.get(CONTEXT_KEY_PROVIDER, "")
    current_model = context.get(CONTEXT_KEY_MODEL, "")
    current_stream = context.get(CONTEXT_KEY_STREAM, False)

    if not config:
        ui.print_error("Configuration not available.")
        return True

    rows = [
        ["Provider", current_provider],
        ["Model", current_model],
        ["Streaming", str(current_stream)],
        ["Ollama URL", config.ollama_base_url],
        ["OpenAI API Key", "Set" if config.openai_api_key else "Not set"],
        ["Anthropic API Key", "Set" if config.anthropic_api_key else "Not set"],
        ["Google API Key", "Set" if config.google_api_key else "Not set"],
    ]
    ui.print_table("Current Configuration", ["Setting", "Value"], rows)
    return True


@register_command(
    name="mcp",
    description="Show MCP server management information",
    usage="/mcp",
    category="config",
    detailed_help="Show information about MCP server management.\n"
    "Use 'agent-cli mcp' commands to manage MCP servers.",
)
def handle_mcp(command: str, context: Dict) -> bool:
    """Handle /mcp command."""
    ui.print_info("MCP Server Management:")
    ui.print_info("  Use 'agent-cli mcp' command to manage MCP servers")
    rows = [
        ["agent-cli mcp list", "List configured servers"],
        ["agent-cli mcp add <name>", "Add a server"],
        ["agent-cli mcp remove <name>", "Remove a server"],
    ]
    from agent_cli.ui import ui

    parts = command.split(None, 2)
    if len(parts) < 2:
        ui.print_info("Usage: /mcp <list|add|remove|show> [args]")
        return True

    action = parts[1].lower()

    config = context.get(CONTEXT_KEY_CONFIG)
    if not config:
        ui.print_error("Configuration not available.")
        return True

    mcp_config = config.get_mcp_config()

    if action == "list":
        rows = []
        for name, details in mcp_config.items():
            command_str = details.get("command", "")
            args_str = " ".join(details.get("args", []))
            rows.append([name, f"{command_str} {args_str}"])

        if not rows:
            ui.print_info("No MCP servers configured.")
        else:
            ui.print_table("MCP Servers", ["Name", "Command"], rows)

    elif action == "add":
        if len(parts) < 3:
            ui.print_info("Usage: /mcp add <name> <command_string>")
            return True

        # Simple parsing logic (could be improved for complex quotes)
        args_part = parts[2]
        name_config = args_part.split(None, 1)
        name = name_config[0]
        cmd_string = name_config[1] if len(name_config) > 1 else ""

        # Need to split command string into cmd + args list for config
        import shlex

        try:
            split_cmd = shlex.split(cmd_string)
            if not split_cmd:
                ui.print_error("Invalid command string.")
                return True

            cmd_exe = split_cmd[0]
            cmd_args = split_cmd[1:]

            config.add_mcp_server(name, cmd_exe, cmd_args)
            ui.print_success(f"Added MCP server '{name}'")

        except Exception as e:
            ui.print_error(f"Error parsing command: {e}")

    elif action == "remove":
        if len(parts) < 3:
            ui.print_info("Usage: /mcp remove <name>")
            return True
        name = parts[2]
        if config.remove_mcp_server(name):
            ui.print_success(f"Removed MCP server '{name}'")
        else:
            ui.print_error(f"MCP server '{name}' not found.")

    elif action == "show":
        if len(parts) < 3:
            ui.print_info("Usage: /mcp show <name>")
            return True
        name = parts[2]
        servers = config.get_mcp_config()
        if name in servers:
            import json

            ui.print_markdown(
                f"**{name}** Configuration:\n```json\n{json.dumps(servers[name], indent=2)}\n```"
            )
        else:
            ui.print_error(f"MCP server '{name}' not found.")

    else:
        ui.print_error(f"Unknown action: {action}")

    return True


@register_command(
    name="agent",
    description="Manage specialized agents (personas)",
    usage="/agent <action> [args]",
    aliases=[],
    category="config",
    detailed_help="Manage specialized agent personas with custom system prompts.\n"
    "Actions:\n"
    "  list                 - List saved agents\n"
    "  create <name> <model> - Create a new agent (interactive prompt follows)\n"
    "  use <name>           - Switch to a specific agent persona\n"
    "  delete <name>        - Delete an agent\n"
    "  show <name>          - Show agent details\n"
    "\n"
    "Examples:\n"
    "  /agent create coder llama3\n"
    "  /agent use coder",
)
def handle_agent(command: str, context: Dict) -> bool:
    """Handle /agent command."""
    from agent_cli.ui import ui

    parts = command.split(None, 2)
    if len(parts) < 2:
        ui.print_info("Usage: /agent <list|create|use|delete|show> [args]")
        return True

    action = parts[1].lower()
    config = context.get(CONTEXT_KEY_CONFIG)

    if action == "list":
        agents = config.get_agents()
        if not agents:
            ui.print_info("No specialized agents found. Use /agent create to make one.")
        else:
            rows = [
                [name, details.get("model", ""), details.get("system_prompt", "")[:50] + "..."]
                for name, details in agents.items()
            ]
            ui.print_table("Specialized Agents", ["Name", "Model", "System Prompt (Snippet)"], rows)

    elif action == "create":
        if len(parts) < 3:
            ui.print_info("Usage: /agent create <name> <model>")
            return True

        args = parts[2].split(None, 1)
        name = args[0]
        model = args[1] if len(args) > 1 else context.get(CONTEXT_KEY_MODEL)

        ui.print_info(f"Creating agent '{name}' using model '{model}'.")
        ui.print_info("Enter the System Prompt for this agent (press Enter twice to finish):")

        # Simple multi-line input simulation via existing session if possible, else standard loop
        lines = []
        while True:
            # We can't easily access the prompt session here without passing it or accessing global UI
            # but we have 'ui' imported.
            line = ui.interactive_session.session.prompt([("class:prompt", "> ")])
            if not line:
                break
            lines.append(line)

        system_prompt = "\n".join(lines)
        config.add_agent(name, system_prompt, model)
        ui.print_success(f"Agent '{name}' created!")

    elif action == "use":
        if len(parts) < 3:
            ui.print_info("Usage: /agent use <name>")
            # Also support resetting to default
            if ui.interactive_session and not parts[2:]:
                ui.print_info("To reset to default (no agent), type: /agent use default")
            return True

        name = parts[2]

        if name == "default":
            # clear system prompt logic
            context[CONTEXT_KEY_SYSTEM_PROMPT] = None
            ui.print_success("Switched to default agent (no system prompt).")
            return True

        agent_data = config.get_agent(name)
        if agent_data:
            model = agent_data.get("model")
            system_prompt = agent_data.get("system_prompt")

            # Update context
            context[CONTEXT_KEY_MODEL] = model
            context[CONTEXT_KEY_SYSTEM_PROMPT] = system_prompt

            ui.print_success(f"Switched to agent '{name}' ({model})")
        else:
            ui.print_error(f"Agent '{name}' not found.")

    elif action == "delete":
        if len(parts) < 3:
            ui.print_info("Usage: /agent delete <name>")
            return True
        name = parts[2]
        if config.remove_agent(name):
            ui.print_success(f"Agent '{name}' deleted.")
        else:
            ui.print_error(f"Agent '{name}' not found.")

    elif action == "show":
        if len(parts) < 3:
            ui.print_info("Usage: /agent show <name>")
            return True
        name = parts[2]
        agent_data = config.get_agent(name)
        if agent_data:
            import json

            ui.print_markdown(
                f"**Agent: {name}**\n```json\n{json.dumps(agent_data, indent=2)}\n```"
            )
        else:
            ui.print_error(f"Agent '{name}' not found.")

    else:
        ui.print_error(f"Unknown action: {action}")

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
    "  /session list  - List all active sessions",
)
def handle_session(command: str, context: Dict) -> bool:
    """Handle /session command."""
    from agent_cli.session_manager import (
        clear_session_state,
        create_new_session,
        get_session_state,
        get_terminal_session_id,
        list_all_sessions,
    )

    parts = command.split(None, 1)
    subcommand = parts[1].lower() if len(parts) > 1 else None

    if subcommand == "new":
        session_id = create_new_session()
        ui.print_success(f"Created new session: {session_id}")
    elif subcommand == "clear":
        clear_session_state()
        ui.print_success("Session state cleared.")
    elif subcommand == "list":
        sessions = list_all_sessions()
        if sessions:
            rows = []
            for sid, state in sessions.items():
                if state:
                    details = f"{state.get('provider', 'N/A')} / {state.get('model', 'N/A')}"
                else:
                    details = "(empty)"
                rows.append([sid, details])
            ui.print_table(f"Active Sessions ({len(sessions)})", ["Session ID", "State"], rows)
        else:
            ui.print_info("No active sessions.")
    else:
        # Show current session info
        session_id = get_terminal_session_id()
        state = get_session_state()

        info = [["Session ID", session_id]]
        if state:
            info.append(["Provider", state.get("provider", "N/A")])
            info.append(["Model", state.get("model", "N/A")])
            info.append(["Streaming", str(state.get("stream", False))])
        else:
            info.append(["State", "(no saved state)"])

        ui.print_table("Current Session", ["Key", "Value"], info)

    return True


@register_command(
    name="theme",
    description="List or switch UI themes",
    usage="/theme [name]",
    category="config",
    detailed_help="List available themes or switch to a specific theme.\n"
    "Examples:\n"
    "  /theme             - List all available themes\n"
    "  /theme catppuccin  - Switch to Catppuccin theme",
)
def handle_theme(command: str, context: Dict) -> bool:
    """Handle /theme command."""
    from agent_cli.ui import ui

    parts = command.split(None, 1)
    if len(parts) > 1:
        new_theme = parts[1].lower()
        if new_theme in ui.theme_manager.get_available_themes():
            ui.theme_manager.set_theme(new_theme)
            # Save preference to config
            config = context.get(CONTEXT_KEY_CONFIG)
            if config:
                config.set_value("THEME", new_theme)
            ui.print_success(f"Switched to theme: {new_theme}")
        else:
            ui.print_error(f"Theme '{new_theme}' not found.")
            ui.print_info(f"Available themes: {', '.join(ui.theme_manager.get_available_themes())}")
    else:
        current = ui.theme_manager.current_theme_name
        rows = []
        for theme in ui.theme_manager.get_available_themes():
            marker = "*" if theme == current else ""
            rows.append([marker, theme])
        ui.print_table("Available Themes", ["Current", "Theme"], rows)
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
    "Config file values are overridden by environment variables.",
)
def handle_set(command: str, context: Dict) -> bool:
    """Handle /set command."""
    from rich.prompt import Confirm

    config = context.get(CONTEXT_KEY_CONFIG)
    if not config:
        ui.print_error("Configuration not available.")
        return True

    # Parse command: /set KEY=value
    parts = command.split(None, 1)
    if len(parts) < 2:
        ui.print_info("Usage: /set <key>=<value>")
        ui.print_info("Example: /set OLLAMA_BASE_URL=http://192.168.1.100:11434")
        return True

    # Parse key=value
    assignment = parts[1]
    if "=" not in assignment:
        ui.print_error("Invalid format. Use KEY=value")
        # Check for user confusion
        if "MODEL" in assignment.upper() or "PROVIDER" in assignment.upper():
            ui.print_info("Did you mean to use /model or /provider?")
        return True

    key, value = assignment.split("=", 1)
    key = key.strip()
    value = value.strip()

    # Validation helpers
    if key.upper() == "MODEL":
        ui.print_warning(
            "Setting 'MODEL' in config only changes the default. Use /model to switch immediately."
        )

    # Warn about API keys
    if "API_KEY" in key.upper():
        ui.print_warning("API keys should be set via environment variables for security.")
        if not Confirm.ask("Continue anyway?", default=False, console=ui.console):
            ui.print_info("Cancelled.")
            return True

    try:
        config.set_value(key, value)
        ui.print_success(f"Set {key} = {value}")
        ui.print_info("Note: This value is saved to config.ini and will persist.")
        ui.print_info("Environment variables take precedence over config file values.")
    except Exception as e:
        ui.print_error(f"Error setting configuration: {e}")

    return True
