from agent_cli.command_registry import register_command
from agent_cli.commands.constants import (
    CONTEXT_KEY_SYSTEM_PROMPT,
)
from agent_cli.ui import ui


@register_command(
    name="bead",
    description="Manage personality beads",
    usage="/bead [list|add <name>|remove <name>|clear|show]",
    aliases=[],
    category="tools",
    detailed_help="Manage personality beads for the current session.\n" \
    "- /bead list - List available beads\n" \
    "- /bead add <name> - Add a bead to the active chain\n" \
    "- /bead remove <name> - Remove a bead from the chain\n" \
    "- /bead clear - Clear all active beads\n" \
    "- /bead show - Show current active beads and composed prompt",
)
def handle_bead(command: str, context: dict) -> bool:
    """Handle /bead command."""
    from agent_cli.beads import BeadsManager
    from agent_cli.personality_beads import BeadType

    # Initialize manager
    manager = BeadsManager()

    # Get current active beads from UI session (source of truth)
    current_beads = ui.interactive_session.active_beads
    active_ids = [b.id for b in current_beads]

    # Parse command
    parts = command.split()
    subcmd = parts[1].lower() if len(parts) > 1 else "list"

    if subcmd == "list":
        # List available beads
        beads = manager.list_personality_beads()

        if not beads:
            ui.print_info("No beads found in library.")
            return True

        ui.console.print("\n[bold cyan]Available Personality Beads[/bold cyan]\n")

        # Group by type
        by_type = {}
        for bead in beads:
            if bead.type not in by_type:
                by_type[bead.type] = []
            by_type[bead.type].append(bead)

        for bead_type in BeadType:
            if bead_type in by_type:
                ui.console.print(f"[bold]{bead_type.value.title()}[/bold]")
                for bead in by_type[bead_type]:
                    ui.console.print(f"  • [cyan]{bead.id}[/cyan]: {bead.description}")
                ui.console.print()

    elif subcmd == "add":
        if len(parts) < 3:
            ui.print_error("Usage: /bead add <name>")
            return True

        bead_id = parts[2]
        bead = manager.get_personality_bead(bead_id)

        if not bead:
            ui.print_error(f"Bead '{bead_id}' not found.")
            return True

        if bead_id not in active_ids:
            active_ids.append(bead_id)
            # Update UI
            _update_session_beads(ui, manager, active_ids)
            # Compose and update system prompt
            _update_system_prompt(context, manager, active_ids)
            ui.print_success(f"Added bead: {bead.name}")
        else:
            ui.print_info(f"Bead '{bead.name}' is already active.")

    elif subcmd == "remove":
        if len(parts) < 3:
            ui.print_error("Usage: /bead remove <name>")
            return True

        bead_id = parts[2]
        if bead_id in active_ids:
            active_ids.remove(bead_id)
            _update_session_beads(ui, manager, active_ids)
            _update_system_prompt(context, manager, active_ids)
            ui.print_success(f"Removed bead: {bead_id}")
        else:
            ui.print_warning(f"Bead '{bead_id}' is not active.")

    elif subcmd == "clear":
        active_ids.clear()
        _update_session_beads(ui, manager, active_ids)
        _update_system_prompt(context, manager, active_ids)
        ui.print_success("Cleared all beads.")

    elif subcmd == "show":
        if not active_ids:
            ui.print_info("No active beads.")
        else:
            ui.console.print("\n[bold]Active Beads:[/bold]")
            for bid in active_ids:
                bead = manager.get_personality_bead(bid)
                if bead:
                    ui.console.print(f"  • {bead.name} ({bead.type.value})")

            # Show composed prompt preview
            prompt = manager.compose_personality(active_ids)
            ui.console.print("\n[bold]Composed System Prompt:[/bold]")
            ui.console.print(f"[dim]{prompt}[/dim]\n")

    else:
        ui.print_error(f"Unknown subcommand: {subcmd}")

    return True

def _update_session_beads(ui, manager, active_ids):
    """Update UI session with active bead objects for pill rendering."""
    beads = []
    for bid in active_ids:
        bead = manager.get_personality_bead(bid)
        if bead:
            beads.append(bead)
    ui.interactive_session.set_active_beads(beads)

def _update_system_prompt(context, manager, active_ids):
    """Compose beads and update the system prompt in context."""
    if not active_ids:
        context[CONTEXT_KEY_SYSTEM_PROMPT] = None
        return

    prompt = manager.compose_personality(active_ids)
    context[CONTEXT_KEY_SYSTEM_PROMPT] = prompt
