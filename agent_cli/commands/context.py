import shutil
import subprocess
from pathlib import Path

from rich.prompt import Confirm

from agent_cli.command_registry import register_command
from agent_cli.ui import ui


@register_command(
    name="context",
    description="Manage project context and usage",
    usage="/context [status|update|view|add <note>|usage]",
    aliases=["ctx"],
    category="session",
    detailed_help="Manage project context files and usage:\n"
    "- /context or /context status - Show context summary (default)\n"
    "- /context usage - Show context window usage and token count\n"
    "- /context update - Update context from git history\n"
    "- /context view - View all context content\n"
    "- /context add <note> - Add a note to context",
)
def handle_context(command: str, **kwargs) -> bool:
    """Handle /context command."""
    ui = kwargs.get("ui")
    if not ui:
        return True

    from agent_cli.context_manager import ContextManager

    # Parse subcommand
    parts = command.split(None, 1)
    subcommand = parts[1].lower() if len(parts) > 1 else "status"

    # Handle usage subcommand separately
    if subcommand == "usage":
        return _handle_context_usage(**kwargs)

    # Handle usage alias if user meant /context usage but typed /context info
    if subcommand == "info": # Just in case
         return _handle_context_usage(**kwargs)

    manager = ContextManager(Path.cwd())

    try:
        if subcommand == "status":
            # Show context summary
            summary = manager.get_context_summary()
            ui.console.print("\n[bold]Project Context[/bold]\n")
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
            ui.console.print("  /context usage - Show context window usage")
            ui.console.print("  /context update - Update from git history")
            ui.console.print("  /context view - View all context")
            ui.console.print("  /context add <note> - Add a note")

    except Exception as e:
        ui.print_error(f"Error managing context: {e}")

    return True

def _handle_context_usage(**kwargs) -> bool:
    """Show context window usage information."""
    ui = kwargs.get("ui")
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
