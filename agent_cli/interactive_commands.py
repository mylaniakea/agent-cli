"""Interactive command handlers for agent-cli.

Commands are registered using the @register_command decorator from command_registry.
"""

import json
from datetime import datetime

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
def handle_help(command: str, context: dict) -> bool:
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
def handle_model(command: str, context: dict) -> bool:
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
            # Load Ollama model if using ollama provider
            if current_provider == "ollama":
                from agent_cli.ollama_manager import get_ollama_manager

                get_ollama_manager().load_model(new_model)
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
def handle_provider(command: str, context: dict) -> bool:
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
                # Load Ollama model if switched to ollama
                if new_provider == "ollama":
                    from agent_cli.ollama_manager import get_ollama_manager

                    get_ollama_manager().load_model(current_model)
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
def handle_stream(command: str, context: dict) -> bool:
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
def handle_clear(command: str, context: dict) -> bool:
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
def handle_history(command: str, context: dict) -> bool:
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
    name="context",
    description="Manage project context files",
    usage="/context [status|update|view|add <note>]",
    aliases=["ctx"],
    category="session",
    detailed_help="Manage project context files:\n"
    "- /context or /context status - Show context summary\n"
    "- /context update - Update context from git history\n"
    "- /context view - View all context content\n"
    "- /context add <note> - Add a note to context",
)
def handle_context(command: str, **kwargs) -> bool:
    """Handle /context command."""
    ui = kwargs.get("ui")
    if not ui:
        return True

    from pathlib import Path

    from agent_cli.context_manager import ContextManager

    # Parse subcommand
    parts = command.split(None, 1)
    subcommand = parts[1].lower() if len(parts) > 1 else "status"

    manager = ContextManager(Path.cwd())

    try:
        if subcommand == "status" or command.strip() == "/context":
            # Show context summary
            summary = manager.get_context_summary()
            ui.console.print(f"\n[bold]Project Context[/bold]\n")
            ui.console.print(summary)
            ui.console.print()

        elif subcommand == "update":
            # Update context from git
            ui.console.print("[cyan]Updating context from git history...[/cyan]")
            manager.update_context()
            ui.print_success("Context updated")

        elif subcommand == "view":
            # View all context
            content = manager.read_all_context()
            if content:
                ui.console.print("\n[bold]Project Context Content[/bold]\n")
                ui.console.print(content)
            else:
                ui.print_info("No context files found")

        elif subcommand.startswith("add "):
            # Add a note
            note = subcommand[4:].strip()
            if note:
                manager.add_note(note)
                ui.print_success("Note added to context")
            else:
                ui.print_error("Please provide a note to add")

        else:
            ui.print_error(f"Unknown subcommand: {subcommand}")
            ui.console.print("\nUsage:")
            ui.console.print("  /context [status] - Show context summary")
            ui.console.print("  /context update - Update from git history")
            ui.console.print("  /context view - View all context")
            ui.console.print("  /context add <note> - Add a note")

    except Exception as e:
        ui.print_error(f"Context error: {e}")

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
def handle_config(command: str, context: dict) -> bool:
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
def handle_mcp(command: str, context: dict) -> bool:
    """Handle /mcp command."""
    ui.print_info("MCP Server Management:")
    ui.print_info("  Use 'agent-cli mcp' command to manage MCP servers")
    rows = [
        ["agent-cli mcp list", "List configured servers"],
        ["agent-cli mcp add <name>", "Add a server"],
        ["agent-cli mcp remove <name>", "Remove a server"],
    ]

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
    "  create <name> <model> [--beads bead1,bead2,...] - Create a new agent\n"
    "  use <name>           - Switch to a specific agent persona\n"
    "  delete <name>        - Delete an agent\n"
    "  show <name>          - Show agent details\n"
    "  add-bead <name> <bead_id>    - Add a bead to an agent\n"
    "  remove-bead <name> <bead_id> - Remove a bead from an agent\n"
    "\n"
    "Examples:\n"
    "  /agent create coder llama3 --beads helpful,python-expert,concise\n"
    "  /agent create reviewer gpt-4 (then enter system prompt manually)\n"
    "  /agent add-bead coder patient\n"
    "  /agent use coder",
)
def handle_agent(command: str, context: dict) -> bool:
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
            ui.print_info("Usage: /agent create <name> <model> [--beads bead1,bead2,...]")
            return True

        # Parse command for --beads flag
        full_args = parts[2] if len(parts) > 2 else ""
        beads_flag_idx = full_args.find("--beads")

        if beads_flag_idx != -1:
            # Extract beads
            before_beads = full_args[:beads_flag_idx].strip()
            after_beads = full_args[beads_flag_idx + 7:].strip()  # 7 = len("--beads")

            # Parse name and model from before_beads
            args = before_beads.split(None, 1)
            name = args[0] if args else ""
            model = args[1] if len(args) > 1 else context.get(CONTEXT_KEY_MODEL)

            # Parse bead IDs (comma-separated)
            bead_ids = [b.strip() for b in after_beads.split(",") if b.strip()]

            if not name or not bead_ids:
                ui.print_error("Usage: /agent create <name> <model> --beads bead1,bead2,...")
                return True

            # Compose personality from beads
            from agent_cli.beads import BeadsManager

            manager = BeadsManager()
            system_prompt = manager.compose_personality(bead_ids)

            if not system_prompt:
                ui.print_error("Failed to compose personality from beads")
                return True

            # Create agent with beads
            config.add_agent(name, system_prompt, model, beads=bead_ids)
            ui.print_success(f"Agent '{name}' created with beads: {', '.join(bead_ids)}")

            # Show preview
            ui.print_info("\nComposed personality (first 200 chars):")
            ui.print_info(system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt)

        else:
            # Traditional manual prompt entry
            args = full_args.split(None, 1)
            name = args[0] if args else ""
            model = args[1] if len(args) > 1 else context.get(CONTEXT_KEY_MODEL)

            if not name:
                ui.print_error("Usage: /agent create <name> <model>")
                return True

            ui.print_info(f"Creating agent '{name}' using model '{model}'.")
            ui.print_info("Enter the System Prompt for this agent (press Enter twice to finish):")

            # Simple multi-line input simulation
            lines = []
            while True:
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
def handle_session(command: str, context: dict) -> bool:
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
def handle_theme(command: str, context: dict) -> bool:
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
def handle_set(command: str, context: dict) -> bool:
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


@register_command(
    name="context",
    description="Show current context window usage",
    usage="/context",
    aliases=["ctx"],
    category="info",
)
def handle_context(command: str, **kwargs) -> bool:
    """Show context window usage information."""
    ui = kwargs.get("ui")
    kwargs.get("agent")
    messages = kwargs.get("messages", [])

    if not ui:
        return True

    # Get model info
    model_name = kwargs.get("model", "unknown")
    provider = kwargs.get("provider", "unknown")

    # Get max context from model metadata
    from agent_cli.model_factory import ModelFactory

    try:
        factory = ModelFactory()
        metadata = factory.get_model_metadata(provider, model_name)
        max_context = metadata.context_length
    except Exception:
        max_context = 4096  # Default fallback

    # Get context info
    from agent_cli.history_manager import get_context_info
    from agent_cli.token_counter import TokenCounter

    info = get_context_info(messages, max_context)

    # Format output
    ui.console.print("\n[bold cyan]Context Window Usage[/bold cyan]")
    ui.console.print(f"Model: [bold]{model_name}[/bold] ({provider})")
    ui.console.print(f"Messages: [bold]{info['message_count']}[/bold]")

    # Token usage
    token_str = TokenCounter.format_token_count(info["token_count"])
    max_str = TokenCounter.format_token_count(info["max_tokens"])

    # Color based on status
    if info["status"] == "critical":
        color = "red"
        symbol = "⚠️"
    elif info["status"] == "warning":
        color = "yellow"
        symbol = "⚠"
    else:
        color = "green"
        symbol = "✓"

    ui.console.print(
        f"Tokens: [{color}]{symbol} {token_str} / {max_str}[/{color}] ({info['percentage']:.1f}%)"
    )

    # Progress bar
    from rich.progress import BarColumn, Progress, TextColumn

    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=ui.console,
    )

    with progress:
        progress.add_task("Usage", total=100, completed=info["percentage"])

    # Warnings
    if info["status"] == "critical":
        ui.console.print("\n[bold red]⚠️  Warning: Context window is almost full![/bold red]")
        ui.console.print("Consider using [cyan]/clear[/cyan] to reset the conversation history.")
    elif info["status"] == "warning":
        ui.console.print(
            "\n[yellow]⚠  Approaching context limit. Consider clearing history soon.[/yellow]"
        )

    ui.console.print()
    return True


@register_command(
    name="export",
    description="Export conversation to file",
    usage="/export [markdown|json] [filename]",
    aliases=[],
    category="utility",
)
def handle_export(command: str, **kwargs) -> bool:
    """Export current conversation to markdown or JSON."""
    ui = kwargs.get("ui")
    messages = kwargs.get("messages", [])

    if not ui or not messages:
        if ui:
            ui.print_error("No messages to export")
        return True

    # Parse command
    parts = command.split(maxsplit=2)
    format_type = "markdown"  # default
    filename = None

    if len(parts) >= 2:
        format_type = parts[1].lower()
    if len(parts) >= 3:
        filename = parts[2]

    # Validate format
    if format_type not in ["markdown", "json", "md"]:
        ui.print_error(f"Unknown format: {format_type}. Use 'markdown' or 'json'")
        return True

    # Normalize format
    if format_type == "md":
        format_type = "markdown"

    # Get default filename if not provided
    from agent_cli.export_manager import ExportManager

    if not filename:
        file_ext = "md" if format_type == "markdown" else "json"
        filename = ExportManager.get_default_export_path(file_ext)

    # Prepare metadata
    metadata = {
        "provider": kwargs.get("provider", "Unknown"),
        "model": kwargs.get("model", "Unknown"),
        "message_count": len(messages),
        "timestamp": datetime.now().isoformat(),
    }

    # Export
    try:
        if format_type == "markdown":
            path = ExportManager.export_to_markdown(messages, filename, metadata)
        else:
            path = ExportManager.export_to_json(messages, filename, metadata)

        ui.print_success(f"Exported {len(messages)} messages to: {path}")
    except Exception as e:
        ui.print_error(f"Export failed: {e}")

    return True


@register_command(
    name="log",
    description="View conversation logs",
    usage="/log [list|view <path>]",
    aliases=[],
    category="utility",
)
def handle_log(command: str, **kwargs) -> bool:
    """View and manage conversation logs."""
    ui = kwargs.get("ui")

    if not ui:
        return True

    from agent_cli.export_manager import ConversationLogger

    logger = ConversationLogger()

    # Parse command
    parts = command.split(maxsplit=2)
    subcommand = "list"  # default
    if len(parts) >= 2:
        subcommand = parts[1].lower()

    if subcommand == "list":
        # List recent logs
        logs = logger.list_recent_logs(limit=20)

        if not logs:
            ui.console.print("[yellow]No conversation logs found[/yellow]")
            return True

        ui.console.print("\n[bold cyan]Recent Conversation Logs[/bold cyan]\n")

        from rich.table import Table

        table = Table(show_header=True)
        table.add_column("ID", style="cyan", width=3)
        table.add_column("Date", style="green")
        table.add_column("Provider", style="blue")
        table.add_column("Model", style="magenta")
        table.add_column("Messages", justify="right")

        for i, log in enumerate(logs, 1):
            metadata = log.get("metadata", {})
            timestamp = log.get("timestamp", "")
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                date_str = timestamp[:16] if len(timestamp) > 16 else timestamp

            table.add_row(
                str(i),
                date_str,
                metadata.get("provider", "Unknown"),
                metadata.get("model", "Unknown"),
                str(log.get("message_count", 0)),
            )

        ui.console.print(table)
        ui.console.print("\n[dim]Use '/log view <id>' to view a specific log[/dim]\n")

    elif subcommand == "view":
        if len(parts) < 3:
            ui.print_error("Usage: /log view <id>")
            return True

        # Get log by ID
        try:
            log_id = int(parts[2])
            logs = logger.list_recent_logs(limit=20)

            if log_id < 1 or log_id > len(logs):
                ui.print_error(f"Invalid log ID: {log_id}")
                return True

            log_path = logs[log_id - 1]["path"]

            # Read and display log
            with open(log_path, encoding="utf-8") as f:
                data = json.load(f)

            metadata = data.get("metadata", {})
            messages = data.get("messages", [])

            ui.console.print(f"\n[bold cyan]Log: {log_path}[/bold cyan]")
            ui.console.print(f"Provider: {metadata.get('provider', 'Unknown')}")
            ui.console.print(f"Model: {metadata.get('model', 'Unknown')}")
            ui.console.print(f"Messages: {len(messages)}\n")

            # Display first few messages
            for _, msg in enumerate(messages[:5]):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:200]  # Truncate
                ui.console.print(f"[bold]{role}:[/bold] {content}...")

            if len(messages) > 5:
                ui.console.print(f"\n[dim]... and {len(messages) - 5} more messages[/dim]")

        except ValueError:
            ui.print_error("Log ID must be a number")
        except Exception as e:
            ui.print_error(f"Failed to view log: {e}")

    else:
        ui.print_error(f"Unknown subcommand: {subcommand}. Use 'list' or 'view'")

    return True


@register_command(
    name="init",
    description="Initialize project configuration with intelligent wizard",
    usage="/init [provider] [--quick] [--format yaml|markdown] [--analyze]",
    aliases=[],
    category="config",
)
def handle_init(command: str, **kwargs) -> bool:
    """Initialize project configuration file with intelligent wizard."""
    ui = kwargs.get("ui")

    if not ui:
        return True

    from pathlib import Path

    from agent_cli.interactive_select import SingleSelect
    from agent_cli.project_config import ProjectConfig
    from agent_cli.project_detector import detect_project
    from agent_cli.templates import get_template_library

    # Parse command
    parts = command.split()
    provider = None
    format_type = "markdown"  # default
    quick_mode = "--quick" in parts
    analyze = "--analyze" in parts or not any(p in parts[1:] for p in ["openai", "anthropic", "google", "ollama"])

    for i, part in enumerate(parts[1:], 1):
        if part.startswith("--format="):
            format_type = part.split("=")[1]
        elif part in ["--format", "-f"]:
            if i + 1 < len(parts):
                format_type = parts[i + 1]
        elif part not in ["--quick", "--analyze", "--format", "-f"] and not provider:
            provider = part

    # Check if config already exists
    existing = ProjectConfig.find_project_config()
    if existing:
        ui.console.print(f"\n[yellow]Warning: Project config already exists:[/yellow] {existing}")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != "y":
            ui.console.print("[dim]Cancelled[/dim]")
            return True

    # Show wizard header
    ui.console.print("\n╭────────────────────────────────────────────╮")
    ui.console.print("│ 🚀 Project Initialization Wizard          │")
    ui.console.print("╰────────────────────────────────────────────╯\n")

    # Analyze project if requested or no provider specified
    analysis = None
    if analyze:
        ui.console.print("[cyan]🔍 Analyzing your project...[/cyan]\n")
        try:
            analysis = detect_project(Path.cwd())
            ui.console.print(analysis.get_summary())
            ui.console.print()
        except Exception as e:
            ui.console.print(f"[yellow]Warning: Could not analyze project: {e}[/yellow]\n")

    # Get template library
    template_lib = get_template_library()

    # Provider selection
    if not provider:
        provider_options = [
            {"label": "🧠 Anthropic (Claude 3.5)", "value": "anthropic",
             "description": "Best for coding, reasoning, and complex tasks"},
            {"label": "🤖 OpenAI (GPT-4o, o1)", "value": "openai",
             "description": "Excellent all-rounder with strong performance"},
            {"label": "✨ Google (Gemini 1.5)", "value": "google",
             "description": "Fast and cost-effective with large context"},
            {"label": "🦙 Ollama (Local)", "value": "ollama",
             "description": "Privacy-focused local models"},
        ]

        # Highlight recommended provider if we have analysis
        if analysis and analysis.recommended_provider:
            for opt in provider_options:
                if opt["value"] == analysis.recommended_provider:
                    opt["label"] = opt["label"] + " [bold cyan](Recommended)[/bold cyan]"
                    # Move to front
                    provider_options.remove(opt)
                    provider_options.insert(0, opt)
                    break

        ui.console.print("[bold]Select your PRIMARY provider:[/bold]")
        selector = SingleSelect(provider_options)
        selected_provider = selector.show()

        if not selected_provider:
            ui.console.print("[dim]Cancelled[/dim]")
            return True

        provider = selected_provider

    # Template selection
    template = None
    if not quick_mode:
        # Get recommended template from analysis or provider
        recommended_template_id = None
        if analysis and analysis.recommended_template:
            recommended_template_id = analysis.recommended_template

        # Get templates for selection
        categories = template_lib.get_categories()
        template_options = []

        for template_obj in template_lib.list_templates():
            label = f"{template_obj.name}"
            if template_obj.id == recommended_template_id:
                label = f"{label} [bold cyan](Recommended)[/bold cyan]"

            template_options.append({
                "label": label,
                "value": template_obj.id,
                "description": template_obj.description
            })

        ui.console.print("\n[bold]Select a project template:[/bold]")
        selector = SingleSelect(template_options)
        selected_template_id = selector.show()

        if not selected_template_id:
            ui.console.print("[dim]Using default template[/dim]\n")
        else:
            template = template_lib.get_template(selected_template_id)

    # Format selection
    if not quick_mode:
        ui.console.print("\n[bold]Select configuration format:[/bold]")
        format_options = [
            {"label": "📄 Markdown (claude.md, gpt.md, etc.)", "value": "markdown",
             "description": "Human-friendly, easy to read and edit"},
            {"label": "📋 YAML (.agent.yml)", "value": "yaml",
             "description": "Structured, machine-readable format"},
        ]
        selector = SingleSelect(format_options)
        selected_format = selector.show()

        if selected_format:
            format_type = selected_format

    # Create config
    ui.console.print("\n[cyan]✨ Creating project configuration...[/cyan]\n")

    try:
        # Use template if selected
        if template:
            # Create config with template settings
            config_content = _create_config_from_template(
                provider=provider,
                template=template,
                format_type=format_type,
                analysis=analysis
            )

            # Determine filename
            if format_type == "yaml":
                config_path = Path.cwd() / ".agent.yml"
            else:
                config_path = Path.cwd() / f"{provider}.md"

            config_path.write_text(config_content)
        else:
            # Use default config creation
            config_path = ProjectConfig.create_project_config(
                provider.lower(),
                format=format_type
            )

        ui.print_success(f"Created project config: {config_path}")

        # Generate initial project context
        if not quick_mode and analysis:
            try:
                from agent_cli.context_manager import initialize_project_context

                ui.console.print("\n[cyan]📝 Generating project context...[/cyan]")

                context_info = {
                    "name": Path.cwd().name,
                    "primary_language": analysis.primary_language,
                    "frameworks": analysis.frameworks,
                    "complexity": analysis.complexity,
                    "total_loc": analysis.total_loc,
                    "dependency_files": analysis.dependency_files,
                    "has_tests": analysis.has_tests,
                    "has_docs": analysis.has_docs,
                    "has_ci": analysis.has_ci,
                }

                context_file = initialize_project_context(Path.cwd(), context_info)
                ui.console.print(f"  ✓ Created context file: {context_file.relative_to(Path.cwd())}")
            except Exception as e:
                ui.console.print(f"  [yellow]Warning: Could not generate context: {e}[/yellow]")

        # Offer to install git hooks
        if not quick_mode and analysis and analysis.has_git:
            try:
                ui.console.print("\n[cyan]🔗 Git hooks setup[/cyan]")
                response = input("  Install git hooks for automatic context updates? (Y/n): ").strip().lower()

                if response in ["", "y", "yes"]:
                    from agent_cli.git_hooks import install_git_hooks

                    result = install_git_hooks(Path.cwd())

                    if result["success"]:
                        if result["installed"]:
                            ui.console.print(f"  ✓ Installed hooks: {', '.join(result['installed'])}")
                        if result["skipped"]:
                            ui.console.print(f"  ⊘ Already installed: {', '.join(result['skipped'])}")
                    else:
                        ui.console.print(f"  [yellow]Warning: {result.get('error', 'Unknown error')}[/yellow]")
            except Exception as e:
                ui.console.print(f"  [yellow]Warning: Could not install git hooks: {e}[/yellow]")

        # Show next steps
        ui.console.print("\n[bold cyan]🎉 Project initialized successfully![/bold cyan]\n")
        ui.console.print("[bold]Next steps:[/bold]")
        ui.console.print(f"  • Edit [cyan]{config_path.name}[/cyan] to customize settings")
        ui.console.print("  • Use [cyan]/chat[/cyan] to start coding with project context")
        ui.console.print("  • Use [cyan]/fallback[/cyan] to add a backup provider")

        if template:
            ui.console.print(f"\n[dim]Template: {template.name}[/dim]")
            ui.console.print(f"[dim]Use cases: {', '.join(template.example_use_cases)}[/dim]")

    except Exception as e:
        ui.print_error(f"Failed to create config: {e}")

    return True


def _create_config_from_template(provider: str, template, format_type: str, analysis=None) -> str:
    """Create configuration content from a template.

    Args:
        provider: Provider name
        template: ProjectTemplate object
        format_type: 'yaml' or 'markdown'
        analysis: Optional ProjectAnalysis

    Returns:
        Configuration file content as string
    """
    if format_type == "yaml":
        # YAML format
        content = f"""# Agent CLI Project Configuration
# Auto-generated from template: {template.name}

provider: {provider}
model: {template.model}
temperature: {template.temperature}

# System prompt for this project
system_prompt: |
{chr(10).join('  ' + line for line in template.system_prompt.split(chr(10)))}

# Context files to include automatically
context_files:
"""
        for pattern in template.context_files:
            content += f'  - "{pattern}"\n'

        content += "\n# Files to exclude from context\nexclude_patterns:\n"
        for pattern in template.exclude_patterns:
            content += f'  - "{pattern}"\n'

        content += "\n# Enabled tools\ntools:\n"
        for tool in template.tools:
            content += f"  - {tool}\n"

        # Add Beads configuration if we have analysis
        if analysis:
            content += "\n# Beads context management\nbeads:\n"
            content += "  enabled: true\n"
            content += "  max_messages: 20\n"
            content += "  summary_threshold: 15\n"

    else:
        # Markdown format
        content = f"""---
provider: {provider}
model: {template.model}
temperature: {template.temperature}
context_files:
"""
        for pattern in template.context_files:
            content += f'  - "{pattern}"\n'

        content += "exclude_patterns:\n"
        for pattern in template.exclude_patterns:
            content += f'  - "{pattern}"\n'

        content += "tools:\n"
        for tool in template.tools:
            content += f"  - {tool}\n"

        content += "---\n\n"
        content += template.system_prompt

        # Add project info if we have analysis
        if analysis and analysis.primary_language:
            content += "\n\n## Project Information\n\n"
            content += f"- **Language**: {analysis.primary_language.title()}\n"
            if analysis.frameworks:
                content += f"- **Frameworks**: {', '.join(analysis.frameworks)}\n"
            content += f"- **Complexity**: {analysis.complexity.title()}\n"

    return content


@register_command(
    name="hooks",
    description="Manage git hooks for automatic context updates",
    usage="/hooks [install|uninstall|list]",
    aliases=[],
    category="config",
    detailed_help="Manage git hooks:\n"
    "- /hooks or /hooks list - Show installed hooks\n"
    "- /hooks install - Install git hooks\n"
    "- /hooks uninstall - Remove git hooks",
)
def handle_hooks(command: str, **kwargs) -> bool:
    """Handle /hooks command."""
    ui = kwargs.get("ui")
    if not ui:
        return True

    from pathlib import Path

    from agent_cli.git_hooks import GitHooksManager

    # Parse subcommand
    parts = command.split()
    subcommand = parts[1].lower() if len(parts) > 1 else "list"

    manager = GitHooksManager(Path.cwd())

    try:
        if not manager.is_git_repo():
            ui.print_error("Not a git repository")
            return True

        if subcommand in ["list", "status"]:
            # List hooks
            result = manager.list_hooks()

            ui.console.print("\n[bold]Git Hooks Status[/bold]\n")

            if result["agent_hooks"]:
                ui.console.print("[green]✓ Agent CLI Hooks:[/green]")
                for hook in result["agent_hooks"]:
                    ui.console.print(f"  • {hook}")
            else:
                ui.console.print("[dim]No Agent CLI hooks installed[/dim]")

            if result["other_hooks"]:
                ui.console.print("\n[dim]Other Hooks:[/dim]")
                for hook in result["other_hooks"]:
                    ui.console.print(f"  • {hook}")

            ui.console.print()

        elif subcommand == "install":
            # Install hooks
            ui.console.print("[cyan]Installing git hooks...[/cyan]\n")

            result = manager.install_hooks()

            if result["success"]:
                if result["installed"]:
                    ui.console.print("[green]✓ Installed:[/green]")
                    for hook in result["installed"]:
                        ui.console.print(f"  • {hook}")

                if result["skipped"]:
                    ui.console.print("\n[dim]Already installed:[/dim]")
                    for hook in result["skipped"]:
                        ui.console.print(f"  • {hook}")

                ui.print_success("\nGit hooks installed successfully")
            else:
                ui.print_error("Failed to install git hooks")
                for error in result.get("errors", []):
                    ui.console.print(f"  [red]✗[/red] {error}")

        elif subcommand == "uninstall":
            # Uninstall hooks
            ui.console.print("[cyan]Uninstalling git hooks...[/cyan]\n")

            result = manager.uninstall_hooks()

            if result["success"]:
                if result["removed"]:
                    ui.console.print("[green]✓ Removed:[/green]")
                    for hook in result["removed"]:
                        ui.console.print(f"  • {hook}")
                else:
                    ui.console.print("[dim]No Agent CLI hooks to remove[/dim]")

                ui.print_success("\nGit hooks uninstalled successfully")
            else:
                ui.print_error("Failed to uninstall git hooks")
                for error in result.get("errors", []):
                    ui.console.print(f"  [red]✗[/red] {error}")

        else:
            ui.print_error(f"Unknown subcommand: {subcommand}")
            ui.console.print("\nUsage:")
            ui.console.print("  /hooks [list] - Show installed hooks")
            ui.console.print("  /hooks install - Install git hooks")
            ui.console.print("  /hooks uninstall - Remove git hooks")

    except Exception as e:
        ui.print_error(f"Hooks error: {e}")

    return True


@register_command(
    name="setup",
    description="Interactive setup for a provider",
    usage="/setup <provider>",
    aliases=[],
    category="config",
)
def _handle_setup(context: dict, args: str) -> bool:
    """Handle the setup command - interactive provider onboarding."""
    from rich.console import Console

    from agent_cli.onboarding import ProviderOnboarding

    args = args.strip()
    if not args:
        console = Console()
        console.print("[yellow]Usage: /setup <provider>[/yellow]")
        console.print("Available providers: openai, anthropic, google, ollama")
        return True

    provider = args.lower()
    console = Console()

    result = ProviderOnboarding(console).run_onboarding(provider)

    if result:
        console.print("\n[green bold]🎉 Setup complete![/green bold]")
        console.print(f"[dim]Use /provider {provider} to switch to this provider[/dim]\n")

    return True


@register_command(
    name="compress",
    description="Compress conversation history into a summary",
    usage="/compress",
    aliases=[],
    category="session",
    detailed_help="Compress the conversation history into a concise summary.\n"
    "This reduces token usage while preserving key context.",
)
def handle_compress(command: str, context: dict) -> bool:
    """Handle /compress command."""
    history = context.get(CONTEXT_KEY_HISTORY, [])
    agent = context.get(CONTEXT_KEY_AGENT)

    if not history:
        ui.print_warning("No history to compress.")
        return True

    if not agent:
        ui.print_error("No agent available.")
        return True

    ui.print_info("Compressing conversation history...")
    try:
        with ui.create_spinner("Summarizing context..."):
            summary_prompt = (
                "Summarize our conversation so far into a concise context string "
                "that captures all key information, decisions, and current state. "
                "Do not lose important details."
            )
            summary = agent.chat(summary_prompt, history=history)

        # Replace history with summary
        history.clear()
        history.append({"role": "user", "content": "Previous Context Summary: " + summary})
        history.append({"role": "assistant", "content": "Understood. I have the context."})
        ui.print_success("Context compressed!")
    except Exception as e:
        ui.print_error(f"Error compressing history: {e}")

    return True


@register_command(
    name="beads",
    description="Check Beads CLI status or context",
    usage="/beads [status|context]",
    aliases=["bd"],
    category="tools",
    detailed_help="Integration with Beads CLI for project context management.\n"
    "Commands:\n"
    "  /beads status  - Show Beads status (default)\n"
    "  /beads context - Show Beads context\n\n"
    "If Beads is not installed, offers to install via Homebrew.",
)
def handle_beads(command: str, context: dict) -> bool:
    """Handle /beads command."""
    import shutil
    import subprocess

    parts = command.split()
    subcmd = parts[1] if len(parts) > 1 else "status"

    bd_path = shutil.which("bd")

    # Handle installation if missing
    if not bd_path:
        ui.print_warning("Beads CLI ('bd') not found.")

        # Check for Homebrew
        brew_path = shutil.which("brew")
        if brew_path:
            try:
                from rich.prompt import Confirm

                if Confirm.ask("Install 'bd' via Homebrew?"):
                    ui.print_info("Running: brew tap steveyegge/beads")
                    subprocess.run([brew_path, "tap", "steveyegge/beads"], check=True)

                    ui.print_info("Running: brew install bd")
                    subprocess.run([brew_path, "install", "bd"], check=True)

                    bd_path = shutil.which("bd")
                    if bd_path:
                        ui.print_success(f"Beads installed successfully at {bd_path}!")
                    else:
                        ui.print_error(
                            "Installation appeared to succeed but 'bd' is still not found."
                        )
            except subprocess.CalledProcessError as e:
                ui.print_error(f"Installation failed: {e}")
            except Exception as e:
                ui.print_error(f"Error during installation: {e}")

        if not bd_path:
            ui.print_info("Please install manually:")
            ui.print_info("  brew tap steveyegge/beads && brew install bd")
            ui.print_info("  -or-")
            ui.print_info(
                "  curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash"
            )
            return True

    # Execute beads command
    try:
        if subcmd == "context":
            result = subprocess.run([bd_path, "status"], capture_output=True, text=True, check=True)
            ui.console.print(f"\n[blue]Beads Context:[/blue]\n{result.stdout}")
        else:  # Default to status
            result = subprocess.run([bd_path, "status"], capture_output=True, text=True, check=True)
            ui.console.print(f"\n[blue]Beads Status:[/blue]\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        ui.print_warning(
            f"Beads returned error (is it initialized?): {e.stderr.strip() if e.stderr else e.stdout.strip()}"
        )
        ui.print_info("Try running 'bd init' in the project folder matching this session.")
    except FileNotFoundError:
        ui.print_error(f"Beads CLI ('bd') not found at '{bd_path}'.")
    except Exception as e:
        ui.print_error(f"An unexpected error occurred while running beads: {e}")

    return True


@register_command(
    name="keepalive",
    description="Set or show Ollama keep-alive duration",
    usage="/keepalive [duration]",
    aliases=["ka"],
    category="config",
    detailed_help="Set or show the keep-alive duration for Ollama models.\n"
    "Examples:\n"
    "  /keepalive       - Show current setting\n"
    "  /keepalive 10m   - Keep model loaded for 10 minutes\n"
    "  /keepalive 0     - Unload immediately after response\n\n"
    "Only works with Ollama provider.",
)
def handle_keepalive(command: str, context: dict) -> bool:
    """Handle /keepalive command."""
    agent = context.get(CONTEXT_KEY_AGENT)
    parts = command.split()

    if len(parts) > 1:
        # Set keep-alive
        duration = parts[1]
        if hasattr(agent, "set_keep_alive"):
            agent.set_keep_alive(duration)
            ui.print_success(f"Keep-alive set to {duration}")
        else:
            ui.print_warning("Keep-alive is only supported for Ollama agents.")
    else:
        # Show current keep-alive
        if hasattr(agent, "keep_alive"):
            ui.print_info(f"Current keep-alive: {agent.keep_alive}")
        else:
            ui.print_info("Keep-alive: N/A (not supported for this provider)")
        ui.print_info("Usage: /keepalive <duration> (e.g., 10m, 1h, 0)")

    return True


@register_command(
    name="reasoning",
    description="Toggle reasoning display mode",
    usage="/reasoning",
    aliases=["think"],
    category="config",
    detailed_help="Toggle reasoning display mode.\n"
    "When enabled, shows model reasoning process (if supported by model).",
)
def handle_reasoning(command: str, context: dict) -> bool:
    """Handle /reasoning command."""
    # For now, this is a placeholder for future reasoning display toggle
    ui.print_info("Reasoning display toggle: currently always enabled for raw stream.")
    ui.print_info("This feature will be enhanced in future updates.")
    return True
