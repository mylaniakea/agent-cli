from agent_cli.command_registry import register_command
from agent_cli.ui import ui


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
