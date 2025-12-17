"""Command registry for dynamic command discovery and help generation.

Inspired by code-puppy's command registry system, adapted for agent-cli's simpler needs.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class CommandInfo:
    """Metadata for a registered command."""

    name: str
    description: str
    handler: Callable[[str], bool]
    usage: str = ""
    aliases: list[str] = field(default_factory=list)
    category: str = "core"
    detailed_help: Optional[str] = None

    def __post_init__(self):
        """Set default usage if not provided."""
        if not self.usage:
            self.usage = f"/{self.name}"


# Global registry: maps command name/alias -> CommandInfo
_COMMAND_REGISTRY: dict[str, CommandInfo] = {}


def register_command(
    name: str,
    description: str,
    usage: str = "",
    aliases: Optional[list[str]] = None,
    category: str = "core",
    detailed_help: Optional[str] = None,
):
    """Decorator to register a command handler.

    This decorator registers a command function so it can be:
    - Auto-discovered by the help system
    - Invoked by handle_command() dynamically
    - Grouped by category
    - Documented with aliases and detailed help

    Args:
        name: Primary command name (without leading /)
        description: Short one-line description for help text
        usage: Full usage string (e.g., "/model <name>"). Defaults to "/{name}"
        aliases: List of alternative names (without leading /)
        category: Grouping category ("core", "config", "session", etc.)
        detailed_help: Optional detailed help text for /help <command>

    Example:
        >>> @register_command(
        ...     name="model",
        ...     description="Switch to a different model",
        ...     usage="/model <name>",
        ...     aliases=["m"],
        ...     category="config",
        ... )
        ... def handle_model(command: str) -> bool:
        ...     return True

    Returns:
        The decorated function, unchanged
    """

    def decorator(func: Callable[[str], bool]) -> Callable[[str], bool]:
        # Create CommandInfo instance
        cmd_info = CommandInfo(
            name=name,
            description=description,
            handler=func,
            usage=usage,
            aliases=aliases or [],
            category=category,
            detailed_help=detailed_help,
        )

        # Register primary name
        _COMMAND_REGISTRY[name] = cmd_info

        # Register all aliases pointing to the same CommandInfo
        for alias in aliases or []:
            _COMMAND_REGISTRY[alias] = cmd_info

        return func

    return decorator


def get_all_commands() -> dict[str, CommandInfo]:
    """Get all registered commands.

    Returns:
        Dictionary mapping command names/aliases to CommandInfo objects.
    """
    return _COMMAND_REGISTRY.copy()


def get_command(name: str) -> Optional[CommandInfo]:
    """Get command info by name or alias.

    Args:
        name: Command name or alias (without leading /)

    Returns:
        CommandInfo if found, None otherwise
    """
    return _COMMAND_REGISTRY.get(name)


def get_commands_by_category() -> dict[str, list[CommandInfo]]:
    """Get all commands grouped by category.

    Returns:
        Dictionary mapping category names to lists of CommandInfo objects.
    """
    categories: dict[str, list[CommandInfo]] = {}

    # Use a set to track primary names we've already added
    seen_primary_names = set()

    for cmd_info in _COMMAND_REGISTRY.values():
        # Only add each command once (by primary name)
        if cmd_info.name not in seen_primary_names:
            seen_primary_names.add(cmd_info.name)
            if cmd_info.category not in categories:
                categories[cmd_info.category] = []
            categories[cmd_info.category].append(cmd_info)

    return categories


def handle_command(command: str, context: Optional[dict] = None) -> bool:
    """Handle a command by name.

    Args:
        command: Full command string (e.g., "/model llama2" or "/help")
        context: Optional context dictionary to pass to handler

    Returns:
        True if command was handled, False if not found
    """
    # Remove leading / if present
    if command.startswith("/"):
        command = command[1:]

    # Split command and args
    parts = command.split(None, 1)
    cmd_name = parts[0].lower() if parts else ""
    parts[1] if len(parts) > 1 else ""

    # Look up command
    cmd_info = get_command(cmd_name)
    if not cmd_info:
        return False

    # Call handler with full command string
    try:
        return cmd_info.handler(command, context or {})
    except Exception:
        # Handler should handle its own errors, but catch here as fallback
        return False


def generate_help_text(category: Optional[str] = None, command: Optional[str] = None) -> str:
    """Generate help text for commands.

    Args:
        category: Optional category to filter by
        command: Optional specific command to show detailed help for

    Returns:
        Formatted help text
    """
    if command:
        # Show detailed help for specific command
        cmd_info = get_command(command)
        if not cmd_info:
            return f"Command '{command}' not found."

        help_text = f"Command: /{cmd_info.name}\n"
        help_text += f"Usage: {cmd_info.usage}\n"
        help_text += f"Description: {cmd_info.description}\n"
        if cmd_info.aliases:
            help_text += f"Aliases: {', '.join(f'/{alias}' for alias in cmd_info.aliases)}\n"
        if cmd_info.detailed_help:
            help_text += f"\n{cmd_info.detailed_help}\n"
        return help_text

    # Show all commands
    categories = get_commands_by_category()

    if category:
        # Show only specific category
        if category not in categories:
            return f"Category '{category}' not found."
        commands = categories[category]
        help_text = f"\n{category.upper()} Commands:\n"
        for cmd_info in sorted(commands, key=lambda x: x.name):
            help_text += f"  {cmd_info.usage:<20} - {cmd_info.description}\n"
        return help_text

    # Show all commands grouped by category
    help_text = "\nAvailable Commands:\n\n"
    for cat in sorted(categories.keys()):
        commands = categories[cat]
        help_text += f"{cat.upper()}:\n"
        for cmd_info in sorted(commands, key=lambda x: x.name):
            help_text += f"  {cmd_info.usage:<20} - {cmd_info.description}\n"
        help_text += "\n"

    return help_text
