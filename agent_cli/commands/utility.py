import json
from datetime import datetime

from agent_cli.command_registry import register_command


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
            ui.print_error("Invalid log ID. Please provide a number.")
        except Exception as e:
            ui.print_error(f"Failed to view log: {e}")

    else:
        ui.print_error(f"Unknown subcommand: {subcommand}. Use 'list' or 'view'")

    return True
